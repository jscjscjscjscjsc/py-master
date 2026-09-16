"""手工撰稿入口：把人工写好的讲解稿接进生产流水线。

这条通路不含任何外部语言模型：讲解稿由人（或编码助手）直接撰写，
配图由程序化渲染生成，口播用免费的 edge-tts 合成。整条链路零 API 费用。

撰稿格式（尽量紧凑，作图规格由程序推导，不必手写）
--------------------------------------------------
tools/authored/<章号>_<知识点序号>.json

{
  "chapter_id": 9, "kp_index": 2,
  "title": "本讲标题",
  "hook_line": "一句话点题",
  "scenes": [
    {"t": "hook",    "nar": "口播稿…", "cap": "字幕要点",
     "vt": "画面标题", "vq": "画面里的提问"},
    {"t": "concept", "nar": "…", "cap": "…", "vt": "…", "vb": "要点一|要点二|要点三",
     "vh": "底部结论条"},
    {"t": "code",    "nar": "…", "cap": "…", "vt": "…",
     "code": "可运行的代码", "out": "运行结果"},
    {"t": "compare", "nar": "…", "cap": "…", "vt": "…",
     "left": "左栏标题:行1|行2", "right": "右栏标题:行1|行2", "vh": "结论"},
    {"t": "pitfall", "nar": "…", "cap": "…", "vt": "…",
     "wrong": "错误说明", "wcode": "错误代码",
     "right_answer": "正确说明", "rcode": "正确代码", "vh": "提醒"},
    {"t": "flow",    "nar": "…", "cap": "…", "vt": "…", "vs": "第一步|第二步|第三步"},
    {"t": "summary", "nar": "…", "cap": "…", "vt": "…", "vb": "结论一|结论二|结论三"}
  ]
}

字段说明：t=镜头类型，nar=口播稿，cap=字幕，v 开头的是作图规格
（vt 标题 / vb 竖排要点 / vs 编号步骤 / vh 结论条 / vq 提问）。
未提供的作图字段会从口播稿里自动推导。

用法
----
    python tools/author_scripts.py                 # 处理全部待办稿件
    python tools/author_scripts.py --key 9_2       # 只处理一节
    python tools/author_scripts.py --no-render     # 只合成口播，不渲染配图
    python tools/author_scripts.py --check         # 只校验稿件，不进流水线
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from narration_engine import (  # noqa: E402
    NarrationBuilder, VoiceOver, narration_key, save_narration, stats,
)
from tools.md2html import html_to_text  # noqa: E402

AUTHORED_DIR = Path(__file__).resolve().parent / 'authored'
COURSES_FILE = ROOT / 'data' / 'courses.json'

DEFAULT_SCENES = 16


def split_pipe(text, limit=None):
    if not text:
        return []
    parts = [p.strip() for p in str(text).split('|') if p.strip()]
    return parts[:limit] if limit else parts


def split_sentences(text):
    """按中文标点切句，用于从口播稿推导作图要点。"""
    out, buf = [], ''
    for ch in str(text or ''):
        buf += ch
        if ch in '。！？；':
            if buf.strip():
                out.append(buf.strip())
            buf = ''
    if buf.strip():
        out.append(buf.strip())
    return out


def derive_visual(scene, index):
    """从口播稿推导作图规格；作者给了 v 开头的字段就用作者的。"""
    kind = scene.get('t', 'concept')
    if kind not in ('hook', 'concept', 'code', 'compare', 'pitfall', 'summary', 'flow'):
        kind = 'concept'
    narration = scene.get('nar', '')
    sentences = split_sentences(narration)
    cap = scene.get('cap', '')
    # 标题优先用作者给的，其次用字幕要点，最后用首句的前半段
    title = scene.get('vt') or cap or (sentences[0][:16] if sentences else f'第 {index} 点')

    visual = {'layout': kind, 'title': title[:16], 'subtitle': ''}

    if kind == 'hook':
        visual['question'] = (scene.get('vq') or cap or (sentences[0] if sentences else ''))[:26]
        visual['mood'] = 'alert' if scene.get('mood') == 'alert' else 'happy'
        visual['bullets'] = [{'icon': '', 'text': t} for t in split_pipe(scene.get('vb'), 2)]
    elif kind == 'concept':
        bullets = split_pipe(scene.get('vb'), 4) or [s[:16] for s in sentences[:4]]
        visual['bullets'] = [{'icon': '', 'text': t} for t in bullets]
        visual['highlight'] = (scene.get('vh') or (sentences[-1] if sentences else ''))[:20]
    elif kind == 'code':
        visual['code'] = scene.get('code', '')
        visual['output'] = scene.get('out', '')
        bullets = split_pipe(scene.get('vb'), 1)
        visual['bullets'] = [{'icon': '', 'text': t} for t in bullets]
    elif kind == 'compare':
        for side in ('left', 'right'):
            raw = scene.get(side, '')
            label, _, rest = raw.partition(':')
            visual[side] = {
                'label': (label or '').strip()[:10],
                'lines': split_pipe(rest, 4) or split_pipe(label, 4),
            }
        visual['highlight'] = (scene.get('vh') or '')[:20]
    elif kind == 'pitfall':
        visual['wrong'] = (scene.get('wrong') or '')[:26]
        visual['wrong_code'] = scene.get('wcode', '')
        visual['right_answer'] = (scene.get('right_answer') or '')[:26]
        visual['right_code'] = scene.get('rcode', '')
        visual['highlight'] = (scene.get('vh') or '')[:20]
    elif kind == 'flow':
        steps = split_pipe(scene.get('vs'), 5) or [s[:14] for s in sentences[:4]]
        visual['steps'] = steps
        visual['highlight'] = (scene.get('vh') or '')[:20]
    elif kind == 'summary':
        bullets = split_pipe(scene.get('vb'), 3) or [s[:20] for s in sentences[:3]]
        visual['bullets'] = bullets

    # 交给引擎统一裁剪，避免手写超出排版上限
    from narration_engine import sanitize_visual
    return sanitize_visual(visual, kind)


def load_authored():
    if not AUTHORED_DIR.exists():
        return {}
    out = {}
    for path in sorted(AUTHORED_DIR.glob('*.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as exc:
            print(f'  ✗ {path.name} JSON 解析失败：{exc}')
            continue
        out[path.stem] = (path, data)
    return out


def validate(key, data, courses_by_id):
    """校验稿件：章节是否存在、知识点序号是否越界、口播字数是否够。"""
    problems = []
    chapter = courses_by_id.get(data.get('chapter_id'))
    if not chapter:
        return [f'第 {data.get("chapter_id")} 章不存在']
    kps = chapter['knowledge_points']
    idx = data.get('kp_index', -1)
    if not (0 <= idx < len(kps)):
        return [f'知识点序号 {idx} 越界（该章共 {len(kps)} 个）']
    scenes = data.get('scenes') or []
    if len(scenes) < 8:
        problems.append(f'镜头只有 {len(scenes)} 个，建议 12–16 个')
    chars = sum(len(s.get('nar', '')) for s in scenes)
    if chars < 1200:
        problems.append(f'口播稿共 {chars} 字，不足 5 分钟（建议 1500±150 字）')
    elif chars > 1900:
        problems.append(f'口播稿共 {chars} 字，超过 5 分钟较多')
    for i, s in enumerate(scenes, 1):
        if not s.get('nar'):
            problems.append(f'镜头 {i} 缺口播稿')
        if s.get('t') == 'code' and not s.get('code'):
            problems.append(f'镜头 {i} 是代码镜头但没有代码')
    return problems


def build_payload(key, data, chapter):
    scenes = []
    for i, raw in enumerate(data.get('scenes', []), start=1):
        kind = raw.get('t', 'concept')
        scenes.append({
            'id': i,
            'type': kind,
            'title': (raw.get('vt') or raw.get('cap') or '')[:20],
            'narration': raw.get('nar', '').strip(),
            'caption': (raw.get('cap') or '')[:60],
            'code': (raw.get('code') or '').rstrip(),
            'visual': derive_visual(raw, i),
        })
    chars = sum(len(s['narration']) for s in scenes)
    return {
        'chapter_id': data['chapter_id'],
        'kp_index': data['kp_index'],
        'chapter_title': chapter['title'],
        'kp_title': chapter['knowledge_points'][data['kp_index']]['title'],
        'title': data.get('title', '')[:40],
        'hook_line': data.get('hook_line', '')[:40],
        'style': 'programmatic-slide',
        'image_engine': 'tools/render (程序化作图)',
        'text_model': '人工撰稿（无外部模型）',
        'narration_chars': chars,
        'scene_count': len(scenes),
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'scenes': scenes,
    }


def synthesize_and_render(payload, with_render=True, log=print):
    """跑完剩下的免费环节：口播合成 + 配图渲染。"""
    builder = NarrationBuilder(voice_workers=3, on_log=log)
    key_base = f"{payload['chapter_id']}_{payload['kp_index']}"

    def speak(scene):
        from narration_engine import VOICE_BY_TYPE
        voice = VOICE_BY_TYPE.get(scene['type'], 'zh-CN-YunxiNeural')
        rate = '+2%' if scene['type'] == 'summary' else '+6%'
        scene['image'] = f'narrations/{key_base}/s{scene["id"]:02d}.jpg'
        scene['voice'] = voice
        try:
            path, duration = builder.voice.synth(scene['narration'], voice=voice, rate=rate)
        except Exception as exc:
            log(f'    ⚠ 镜头 {scene["id"]} 口播失败：{str(exc)[:80]}')
            scene['audio'] = ''
            scene['audio_seconds'] = 0
            return 0.0
        scene['audio'] = f'data/audio_cache/{path.name}'
        scene['audio_seconds'] = round(duration, 2)
        return duration

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as pool:
        durations = list(pool.map(speak, payload['scenes']))
    total = round(sum(durations), 1)
    payload['total_seconds'] = total
    missing = sum(1 for s in payload['scenes'] if not s.get('audio'))
    log(f'    ✓ 口播 {total:.0f}s' + (f'（{missing} 个镜头缺失）' if missing else ''))

    if with_render:
        save_narration(narration_key(payload['chapter_id'], payload['kp_index']), payload)
        import build_narrations as bn
        bn.render_images(payload['chapter_id'], payload['kp_index'], log=log)
    else:
        save_narration(narration_key(payload['chapter_id'], payload['kp_index']), payload)
    return payload


def main():
    parser = argparse.ArgumentParser(description='把人工撰稿接进生产流水线')
    parser.add_argument('--key', help='只处理某一节，例如 9_2')
    parser.add_argument('--no-render', action='store_true', help='只合成口播')
    parser.add_argument('--check', action='store_true', help='只校验稿件')
    parser.add_argument('--force', action='store_true', help='已存在的也重做')
    args = parser.parse_args()

    courses = json.loads(COURSES_FILE.read_text(encoding='utf-8'))
    by_id = {c['id']: c for c in courses}
    authored = load_authored()
    if not authored:
        print(f'还没有撰稿。把稿件放到 {AUTHORED_DIR} 下，格式见本文件顶部说明。')
        return 0

    done = set(stats()['ready'])
    todo = []
    for key, (path, data) in authored.items():
        if args.key and key != args.key:
            continue
        problems = validate(key, data, by_id)
        if problems:
            print(f'✗ {key}（{path.name}）:')
            for p in problems:
                print(f'    · {p}')
            continue
        if key in done and not args.force:
            continue
        todo.append((key, path, data))

    print(f'稿件 {len(authored)} 份，待处理 {len(todo)} 节\n')
    if args.check:
        print('校验完成')
        return 0
    if not todo:
        print('没有需要处理的稿件')
        return 0

    started = time.time()
    ok = 0
    for key, path, data in todo:
        chapter = by_id[data['chapter_id']]
        kp_title = chapter['knowledge_points'][data['kp_index']]['title']
        print(f'[{ok + 1}/{len(todo)}] {key} · {kp_title}')
        payload = build_payload(key, data, chapter)
        try:
            synthesize_and_render(payload, with_render=not args.no_render)
            ok += 1
        except Exception as exc:
            print(f'    ✗ 失败：{type(exc).__name__}: {exc}')
    total = stats()
    print(f'\n完成 {ok} 节，用时 {(time.time() - started) / 60:.1f} 分钟')
    print(f'库存：{total["count"]} 节 / {total["scenes"]} 镜头 / '
          f'{total["seconds"] / 60:.1f} 分钟口播')
    return 0


if __name__ == '__main__':
    sys.exit(main())
