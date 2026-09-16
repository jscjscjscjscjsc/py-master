"""批量生产 5 分钟图文讲解。

配图由 tools/render 的程序化作图引擎产出（不需要任何第三方生图接口）：
    Node 把分镜里的 visual 规格编译成版面 HTML → Python Playwright 截图。
单张渲染约 0.1 秒，一节的 16 张图 2 秒内出完。

示例
----
    python build_narrations.py --list                        # 看进度
    python build_narrations.py --chapter 5 --kp 2            # 只做一章一节（验证用）
    python build_narrations.py --chapter 5                   # 做整章
    python build_narrations.py --stage 基础篇                 # 做一整篇
    python build_narrations.py --stage 基础篇 --limit 8       # 先做 8 节
    python build_narrations.py --chapter 5 --force           # 强制重做
    python build_narrations.py --chapter 5 --no-render        # 只出脚本和口播

产物：data/narrations.json + static/narrations/<ch>_<kp>/*.jpg + data/audio_cache/narr_*.mp3
脚本与音频按内容寻址缓存，重复执行不重复计费。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from narration_engine import (  # noqa: E402
    DEFAULT_SCENES, NarrationBuilder, load_narrations, narration_key,
    save_narration, stats,
)
from tools.md2html import html_to_text  # noqa: E402

ROOT = Path(__file__).resolve().parent
COURSES_FILE = ROOT / 'data' / 'courses.json'
LOCK_FILE = ROOT / 'data' / '.build_narrations.lock'


class AlreadyRunning(RuntimeError):
    pass


class BuildLock:
    """防止两个生产进程同时写同一批文件。

    并发跑批会让两处同时写同一段音频缓存（WinError 32 文件占用），
    也会让 narrations.json 互相覆盖，所以宁可拒绝启动。
    """

    def __init__(self, path=LOCK_FILE):
        self.path = path

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                pid = int(self.path.read_text(encoding='utf-8').strip() or 0)
            except ValueError:
                pid = 0
            if pid and _pid_alive(pid):
                raise AlreadyRunning(f'已有生产进程在运行（PID {pid}）。'
                                     f'如确认它已退出，删除 {self.path} 后重试。')
        self.path.write_text(str(os.getpid()), encoding='utf-8')
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)
        return False


def _pid_alive(pid):
    try:
        out = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                             capture_output=True, text=True, timeout=10).stdout
        return str(pid) in out
    except Exception:
        return False


def load_courses():
    return json.loads(COURSES_FILE.read_text(encoding='utf-8'))


def images_complete(key, scene_count):
    """配图是否齐。用于发现「narration 已保存但配图缺失」的缺口。"""
    folder = ROOT / 'static' / 'narrations' / key
    if not folder.exists():
        return False
    return len(list(folder.glob('s*.jpg'))) >= scene_count


# 渲染器读写的 build-plan.json 是全局共享文件，
# 多节并发时若同时渲染会互相覆盖计划，所以这里串行化。
# 渲染本身很快（16 张约 1–2 秒），串行不影响整体吞吐。
_render_lock = threading.Lock()


def render_images(chapter_id, kp_index, log=print):
    """调用程序化作图引擎渲染这一节的 16 张配图。

    总是带 --force：脚本刚生成或刚重建，配图必须跟着新脚本重画，
    否则画面里讲的还是上一版内容。渲染很快（16 张约 1–2 秒），不值得省。
    Node 出错不中断整批——脚本和口播才是花时间的大头，配图随时可以补。
    """
    node = shutil.which('node')
    if not node:
        log('    ⚠ 未找到 node，跳过配图渲染（可稍后单独跑 tools/render/build-plan.mjs）')
        return False
    key = f'{chapter_id}_{kp_index}'
    with _render_lock:
        plan = subprocess.run([node, str(ROOT / 'tools' / 'render' / 'build-plan.mjs'),
                               '--key', key, '--force'],
                              cwd=ROOT, capture_output=True, text=True, timeout=180)
        if plan.returncode != 0:
            log(f'    ⚠ 版式编译失败：{plan.stderr.strip()[:160]}')
            return False
        shot = subprocess.run([sys.executable, str(ROOT / 'tools' / 'render' / 'render_plan.py')],
                              cwd=ROOT, capture_output=True, text=True, timeout=900)
        if shot.returncode != 0:
            log(f'    ⚠ 配图渲染失败：{shot.stderr.strip()[:160]}')
            return False
    tail = [line for line in shot.stdout.strip().split('\n') if line.strip()]
    log(f'    ✓ {tail[-1] if tail else "配图渲染完成"}')
    return True


def pick_targets(courses, args):
    """返回 [(chapter, kp_index)]，按章号与知识点顺序排列。"""
    targets = []
    for chapter in courses:
        if args.chapter and chapter['id'] != args.chapter:
            continue
        if args.stage and args.stage not in chapter.get('stage', ''):
            continue
        for index, kp in enumerate(chapter['knowledge_points']):
            if args.kind and kp.get('kind', 'normal') not in args.kind.split(','):
                continue
            if args.kp is not None and index != args.kp:
                continue
            targets.append((chapter, index))
    return targets


def main():
    parser = argparse.ArgumentParser(description='批量生成 5 分钟图文讲解')
    parser.add_argument('--chapter', type=int, help='只做指定章号')
    parser.add_argument('--kp', type=int, help='只做指定知识点序号（从 0 开始）')
    parser.add_argument('--stage', help='按篇筛选，例如 基础篇 / AI 篇')
    parser.add_argument('--kind', help='按小节类型筛选，例如 normal,task,summary')
    parser.add_argument('--limit', type=int, help='最多做几节')
    parser.add_argument('--scenes', type=int, default=DEFAULT_SCENES, help='镜头数（默认 16）')
    parser.add_argument('--size', default='1024x1024', help='配图尺寸')
    parser.add_argument('--workers', type=int, default=4, help='配图并发数')
    parser.add_argument('--voice-workers', type=int, default=2,
                        help='单节内部的口播并发（压低可减少 edge-tts 限流）')
    parser.add_argument('--kp-workers', type=int, default=1,
                        help='同时处理多少节（提升总吞吐，默认 1）')
    parser.add_argument('--force', action='store_true', help='已完成也重做')
    parser.add_argument('--image-model', action='store_true',
                        help='改用第三方生图模型出图（默认用程序化作图引擎）')
    parser.add_argument('--no-render', action='store_true', help='只出脚本与口播，不渲染配图')
    parser.add_argument('--list', action='store_true', help='只打印进度，不生成')
    args = parser.parse_args()

    courses = load_courses()
    done = load_narrations()

    if args.list:
        summary = stats()
        total_kp = sum(len(c['knowledge_points']) for c in courses)
        print(f'已有讲解：{summary["count"]} 节 / 共 {total_kp} 个知识点'
              f'（{summary["count"] / total_kp * 100:.1f}%）')
        print(f'累计镜头 {summary["scenes"]} 个，口播总时长 '
              f'{summary["seconds"] / 60:.1f} 分钟，口播稿 {summary["chars"]} 字')
        for chapter in courses:
            keys = [f"{chapter['id']}_{i}" for i in range(len(chapter['knowledge_points']))]
            have = sum(1 for k in keys if k in done)
            if have:
                bar = '█' * int(have / max(len(keys), 1) * 20)
                print(f'  [{chapter["id"]:>2}] {chapter["icon"]} '
                      f'{chapter["title"][:24]:<26} {have:>2}/{len(keys):<2} {bar}')
        return

    targets = pick_targets(courses, args)

    def needs_work(chapter, index):
        key = narration_key(chapter['id'], index)
        if args.force or key not in done:
            return True
        # 已经生成过，但要检查配图与口播是否齐——生产中断过的节靠这条自愈
        if args.no_render:
            return False
        narration = done[key]
        if not images_complete(key, len(narration.get('scenes', []))):
            return True
        return any(not scene.get('audio') for scene in narration.get('scenes', []))

    pending = [(c, i) for c, i in targets if needs_work(c, i)]
    if args.limit:
        pending = pending[:args.limit]

    if not pending:
        print('没有需要生成的讲解（可用 --force 重做，或 --list 看进度）')
        return

    try:
        with BuildLock():
            run_batch(args, pending, courses)
    except AlreadyRunning as exc:
        print(f'✗ {exc}')
        raise SystemExit(3)

def run_batch(args, pending, courses):
    builder = NarrationBuilder(workers=args.workers,
                               voice_workers=args.voice_workers)
    if not builder.text.available:
        print('⚠ 未配置 ARK_API_KEY，无法生成分镜脚本。请在 .env 里补上密钥。')
        return
    if args.image_model and not builder.images.available:
        print('⚠ 选择了第三方生图但未配置 ARK_API_KEY，将跳过生图')

    source = '第三方生图模型' if args.image_model else '程序化作图引擎'
    print(f'待生成 {len(pending)} 节，每节 {args.scenes} 镜头，配图：{source}'
          f'{"（本次不渲染配图）" if args.no_render else ""}')
    print(f'并发：{args.kp_workers} 节同时做，每节口播并发 {args.voice_workers}\n')

    started = time.time()
    done = {'ok': 0, 'fail': 0}
    failed = []
    counter_lock = threading.Lock()
    log_lock = threading.Lock()

    def log(text):
        with log_lock:
            print(text, flush=True)

    def work(order_pair):
        order, (chapter, index) = order_pair
        kp = chapter['knowledge_points'][index]
        head = f'[{order}/{len(pending)}] 第 {chapter["id"]} 章 · {kp["title"]}'
        log(f'{head}  ▶ 开始')
        t0 = time.time()
        try:
            payload = builder.build(
                chapter_id=chapter['id'], kp_index=index,
                chapter_title=chapter['title'], kp_title=kp['title'],
                kp_text=html_to_text(kp['content']),
                scenes=args.scenes, image_size=args.size,
                use_image_model=args.image_model,
            )
            save_narration(narration_key(chapter['id'], index), payload)
            if not (args.no_render or args.image_model):
                render_images(chapter['id'], index, log=lambda m: log(f'{head}  {m.strip()}'))
            with counter_lock:
                done['ok'] += 1
            log(f'{head}  ✓ 完成 {time.time() - t0:.0f}s  '
                f'（累计成功 {done["ok"]}，耗时 {time.time() - started:.0f}s）')
        except Exception as exc:
            with counter_lock:
                done['fail'] += 1
                failed.append((chapter['id'], index, str(exc)[:120]))
            log(f'{head}  ✗ 失败：{type(exc).__name__}: {str(exc)[:100]}')

    with ThreadPoolExecutor(max_workers=max(1, args.kp_workers)) as pool:
        list(pool.map(work, enumerate(pending, start=1)))

    total = stats()
    print(f'\n完成 {done["ok"]} 节，失败 {done["fail"]} 节，'
          f'总耗时 {(time.time() - started) / 60:.1f} 分钟')
    print(f'库存：{total["count"]} 节 / {total["scenes"]} 镜头 / '
          f'{total["seconds"] / 60:.1f} 分钟口播')
    for chapter_id, index, message in failed:
        print(f'  ✗ 第 {chapter_id} 章 #{index}：{message}')


if __name__ == '__main__':
    main()
