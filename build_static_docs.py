"""把平台导出成可放到 GitHub Pages 的纯静态站。

导出内容
--------
- 全部页面：首页、章节页、星海图、练习场、画布
- 全部文字内容：知识点正文、练习题与解析、思维导图（跟着 courses.json 走）
- 讲解样例：挑选若干节，导出分镜 JSON + 配图 + 口播音频，
  让在线预览能真的点开听；其余小节提示"请在本地运行"

为什么只放样例
--------------
全量讲解的配图与音频约 280MB，塞进 git 仓库会让克隆和推送都变得很痛苦。
讲解脚本本身（data/narrations.json）已经在仓库里，别人克隆后本地跑一次
`node tools/render/build-plan.mjs && python tools/render/render_plan.py`
就能把几千张配图重新生成出来，不需要任何外部接口。

用法
----
    python build_static_docs.py                  # 默认导出 8 节讲解样例
    python build_static_docs.py --samples 20     # 多放几节
    python build_static_docs.py --samples 0      # 不放讲解，只导出页面
"""
import argparse
import json
import re
import shutil
from pathlib import Path

import app as pymaster

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

# 样例优先挑"基础篇开头 + AI 篇"这类最能说明问题的知识点
SAMPLE_PRIORITY = [
    (1, 0), (1, 1), (1, 5), (2, 0), (3, 0), (4, 0), (5, 1), (5, 2),
    (7, 0), (10, 1), (12, 3), (27, 0), (28, 1), (37, 0), (38, 1),
]

STATIC_HTML_REPLACEMENTS = {
    'href="/static/': 'href="static/',
    'src="/static/': 'src="static/',
    "url('/static/": "url('static/",
    'href="/dashboard"': 'href="index.html"',
    'href="/playground"': 'href="playground.html"',
    'href="/canvas"': 'href="canvas.html"',
    'href="/stars"': 'href="stars.html"',
    "window.location.href='/canvas'": "window.location.href='canvas.html'",
    # 开场 CG 在静态站上也要能播完：把它的出口从后端路由换成导出的首页
    'data-static="0"': 'data-static="1"',
}

# 章节互链要带 .html 后缀（/chapter/12 → chapter-12.html），
# 字符串替换做不到补后缀，所以单独走正则
CHAPTER_HREF_RE = re.compile(r'href="/chapter/(\d+)"')

# 静态站适配层必须最先执行：它要在 main.js 之前接管 fetch 与站内跳转
STATIC_MODE_SCRIPT = '<script src="static/js/static_mode.js"></script>\n'

# 绑定自定义域名后填这里（例如 'pymaster.example.com'）：
# GitHub Pages 认的是发布目录里的 CNAME 文件，放在这里才不会被下次导出冲掉
CNAME_DOMAIN = ''


def static_html(text):
    for old, new in STATIC_HTML_REPLACEMENTS.items():
        text = text.replace(old, new)
    return CHAPTER_HREF_RE.sub(lambda m: f'href="chapter-{m.group(1)}.html"', text)


def write_page(client, route, destination):
    response = client.get(route)
    if response.status_code != 200:
        raise RuntimeError(f'{route} 返回 {response.status_code}')
    body = static_html(response.get_data(as_text=True))
    # 打开静态模式：播放器改为读 data/narrations/*.json，不再打后端接口；
    # 适配层负责接住其余后端请求，避免在线演示站上满屏 404
    body = body.replace('</head>', STATIC_MODE_SCRIPT +
                        '<script>window.PYMASTER_STATIC = true;</script>\n</head>', 1)
    (DOCS / destination).write_text(body, encoding='utf-8')


def export_qbank():
    """导出在线刷题需要的数据。

    刷题中心原来是"后端专属"，在线站点进去只弹一句提示。但它的输入其实
    全是静态的：题库、题目详情、判题脚本。判题需要跑 Python —— 那一环
    交给浏览器里的 Pyodide（见 static/js/pyodide_runner.js），
    于是整条链路（选题 → 写代码 → 运行 → 判题 → 看解析）在静态站上都能走通。

    导出三份：
      data/qbank/catalog.json    章节与专题目录（带赛道归类）
      data/qbank/briefs.json     题目列表（不含答案，用于侧栏与筛选）
      data/qbank/details/<id>.json  单题详情（含答案与断言，点开才拉）
    详情拆成单文件是刻意的：256 道题合起来约 1MB，全部预加载会拖慢首屏，
    而学生一次只看一道。
    """
    import json as _json
    out = DOCS / 'data' / 'qbank'
    detail_dir = out / 'details'
    out.mkdir(parents=True, exist_ok=True)
    detail_dir.mkdir(parents=True, exist_ok=True)

    courses = _json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))
    bank = pymaster.training.load_bank()
    chapters = pymaster.training.bank_chapters(courses)

    # 补上进度字段。本地版这些来自用户的作答档案；在线站没有成绩库，
    # 一律给 0 —— 但字段必须齐，否则前端渲染成 "undefined/2"、"NAN/75"。
    for info in chapters:
        items = pymaster.training.filter_questions(chapters=[info['id']])
        info.setdefault('solved', 0)
        info.setdefault('attempted', 0)
        info.setdefault('wrong', 0)
        info.setdefault('progress', 0)

    (out / 'catalog.json').write_text(_json.dumps({
        'success': True,
        'chapters': chapters,
        'total': len(bank),
        # 浏览器里跑不了第三方库（Pyodide 核心只带标准库），
        # 把受影响的题目标出来，前端会给出明确提示而不是让学生对着报错发呆
        'limits': {
            'no_third_party': True,
            'note': '在线演示站用浏览器内置的 Python 运行，'
                    '只支持标准库；用到 pandas / requests 等第三方库的题目请下载本地版。',
        },
    }, ensure_ascii=False), encoding='utf-8')

    briefs = [pymaster.training.question_brief(q, {}) for q in bank]
    (out / 'briefs.json').write_text(_json.dumps(
        {'success': True, 'questions': briefs, 'count': len(briefs)},
        ensure_ascii=False), encoding='utf-8')

    # 判题脚本：与后端用的是同一份（training_engine.HARNESS），
    # 保证"本地能过 / 在线过不了"这种差异不会出现
    (out / 'harness.py').write_text(pymaster.training.HARNESS, encoding='utf-8')

    n = 0
    for q in bank:
        detail = pymaster.training.public_question(q, {}, reveal=True)
        if not detail:
            continue
        (detail_dir / f"{q['id']}.json").write_text(
            _json.dumps({'success': True, 'question': detail}, ensure_ascii=False),
            encoding='utf-8')
        n += 1
    print(f'题库导出完成：{len(bank)} 道题（catalog + briefs + {n} 份详情 + 判题脚本）')


def export_narrations(samples):
    """导出讲解样例：分镜 JSON、配图、口播音频。"""
    narrations = pymaster.narration_engine.load_narrations()
    out_dir = DOCS / 'data' / 'narrations'
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = DOCS / 'static' / 'narration-audio'
    exported = []

    ordered = [k for k in (f'{c}_{i}' for c, i in SAMPLE_PRIORITY) if k in narrations]
    # 剩余名额按章轮询补齐：样例要跨章分布，只堆在第 1 章说服力不够
    remaining = [k for k in sorted(
        (k for k in narrations if k not in ordered),
        key=lambda k: (int(k.split('_')[0]), int(k.split('_')[1])))]
    by_chapter = {}
    for key in remaining:
        by_chapter.setdefault(key.split('_')[0], []).append(key)
    while len(ordered) < samples and any(by_chapter.values()):
        for chapter in list(by_chapter):
            if by_chapter[chapter] and len(ordered) < samples:
                ordered.append(by_chapter[chapter].pop(0))
            if not by_chapter[chapter]:
                del by_chapter[chapter]
    picked = ordered[:samples]

    for key in picked:
        data = narrations[key]
        chapter_id, kp_index = data['chapter_id'], data['kp_index']
        scenes = []
        copied = 0
        for scene in data['scenes']:
            item = dict(scene)
            image = ROOT / 'static' / (scene.get('image') or '')
            if image.exists():
                target = DOCS / 'static' / scene['image']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(image, target)
                copied += 1
            audio_name = Path(scene.get('audio') or '').name
            source_audio = pymaster.narration_engine.AUDIO_CACHE / audio_name
            if audio_name and source_audio.exists():
                audio_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_audio, audio_dir / audio_name)
                item['audio_url'] = f'static/narration-audio/{audio_name}'
            else:
                item['audio_url'] = ''
            item.pop('audio', None)
            item.pop('image_prompt', None)
            scenes.append(item)

        payload = {
            'success': True,
            'available': True,
            'narration': {
                'chapter_id': chapter_id,
                'kp_index': kp_index,
                'chapter_title': data.get('chapter_title', ''),
                'kp_title': data.get('kp_title', ''),
                'title': data.get('title', ''),
                'hook_line': data.get('hook_line', ''),
                'scene_count': data.get('scene_count', len(scenes)),
                'total_seconds': data.get('total_seconds', 0),
                'narration_chars': data.get('narration_chars', 0),
                'created_at': data.get('created_at', ''),
                'scenes': scenes,
            },
        }
        (out_dir / f'{key}.json').write_text(
            json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        exported.append({'key': key, 'title': data.get('kp_title', ''), 'images': copied})

    # 索引：让前端知道哪些小节有在线样例
    index = {
        'total': len(narrations),
        'online': [item['key'] for item in exported],
    }
    (out_dir / 'index.json').write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')
    return exported


DOC_PAGE_CSS = """
:root{--bg:#0d1117;--card:#161b22;--line:#21262d;--tx:#e6edf3;--tx2:#8b949e;
--cyan:#00d4ff;--jade:#2e6f68;--gold:#b8883b;--paper:#f3ead8;--ink:#29251f}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1200px 700px at 50% -10%,#141a26,#0a0a0f 60%);
color:var(--tx);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
line-height:1.85;padding:0 20px 90px}
.wrap{max-width:960px;margin:0 auto}
.top{padding:56px 0 28px;border-bottom:1px solid var(--line);margin-bottom:34px}
.top .kicker{font-size:12px;letter-spacing:.28em;color:var(--cyan);font-weight:700}
.top h1{font-size:40px;margin:14px 0 10px;letter-spacing:-.01em}
.top p{color:var(--tx2);margin:0;font-size:15px}
h2{font-size:26px;margin:52px 0 16px;padding-left:16px;border-left:5px solid var(--jade)}
h3{font-size:20px;margin:34px 0 10px;color:#cfe3ff}
p{margin:14px 0}
a{color:var(--cyan);text-decoration:none;border-bottom:1px solid rgba(0,212,255,.3)}
strong{color:#fff}
blockquote{margin:22px 0;padding:16px 22px;background:rgba(0,212,255,.06);
border-left:4px solid var(--cyan);border-radius:10px;color:#c9d6e4}
code{background:#1d2432;padding:2px 7px;border-radius:5px;font-size:.92em;
font-family:Consolas,monospace;color:#9fd9ff}
pre{background:#171c26;border:1px solid #2a3242;border-radius:12px;padding:16px 18px;
overflow-x:auto}
pre code{background:none;padding:0;color:#cfe3ff}
.md-table-wrap{overflow-x:auto;margin:22px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{border:1px solid var(--line);padding:11px 14px;text-align:left;vertical-align:top}
th{background:#1b2230;color:#cfe3ff;font-weight:700;white-space:nowrap}
tr:nth-child(even) td{background:rgba(255,255,255,.017)}
ul,ol{padding-left:26px}
li{margin:7px 0}
hr{border:none;border-top:1px solid var(--line);margin:48px 0}
.foot{margin-top:60px;padding-top:22px;border-top:1px solid var(--line);
color:var(--tx2);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
.back{display:inline-block;margin-top:20px;color:var(--cyan);font-size:14px}
"""


def render_doc_page():
    """把《更新说明-客户版》渲染成在线演示站里可直接阅读的页面。"""
    import sys
    src = ROOT / '更新说明-客户版.md'
    if not src.exists():
        return None
    sys.path.insert(0, str(ROOT / 'tools'))
    from md2html import md_to_html
    body = md_to_html(src.read_text(encoding='utf-8'), min_heading=2)
    title_match = re.search(r'^#\s+(.*)$', src.read_text(encoding='utf-8'), flags=re.M)
    title = title_match.group(1).strip() if title_match else '更新说明'
    page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — PyMaster</title>
<style>{DOC_PAGE_CSS}</style></head>
<body><div class="wrap">
  <div class="top">
    <div class="kicker">PYMASTER · RELEASE NOTES</div>
    <h1>{title}</h1>
    <p>PyMaster 教学平台 · 本次功能升级说明</p>
  </div>
  {body}
  <a class="back" href="index.html">← 打开在线演示</a>
  <div class="foot"><span>PyMaster 教学平台</span><span>{title}</span></div>
</div></body></html>"""
    (DOCS / 'update.html').write_text(page, encoding='utf-8')
    return 'update.html'


def build(samples=8):
    DOCS.mkdir(exist_ok=True)
    legacy = DOCS / 'chapter.html'
    if legacy.exists():
        legacy.unlink()

    # static/ 整目录复制，但排除体积巨大的讲解产物（样例在 export_narrations 里单独拷）
    shutil.copytree(ROOT / 'static', DOCS / 'static', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('narrations'))
    (DOCS / '.nojekyll').touch()
    if CNAME_DOMAIN:
        (DOCS / 'CNAME').write_text(CNAME_DOMAIN.strip() + '\n', encoding='utf-8')
        print(f'已写入 docs/CNAME -> {CNAME_DOMAIN.strip()}')

    client = pymaster.app.test_client()
    write_page(client, '/dashboard', 'index.html')
    write_page(client, '/intro', 'intro.html')
    write_page(client, '/stars', 'stars.html')
    write_page(client, '/canvas', 'canvas.html')
    write_page(client, '/playground', 'playground.html')
    write_page(client, '/training', 'training.html')
    # 刷题页额外挂两个静态专用脚本：
    #   pyodide_runner.js —— 浏览器里真跑 Python（判题的执行环境）
    #   static_qbank.js   —— 把 /api/training/* 接到导出的 JSON 上
    # 必须放在 static_mode.js 之后（它在 head 注入），因为这一层是"包一层"：
    # 未接管的接口继续落到 static_mode.js 的降级提示上。
    training_file = DOCS / 'training.html'
    html = training_file.read_text(encoding='utf-8')
    inject = ('<script src="static/js/pyodide_runner.js"></script>'
              + chr(10)
              + '<script src="static/js/static_qbank.js"></script>'
              + chr(10))
    if 'pyodide_runner.js' not in html:
        html = html.replace('</body>', inject + '</body>', 1)
        training_file.write_text(html, encoding='utf-8')

    courses = json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))
    for course in courses:
        write_page(client, f"/chapter/{course['id']}", f"chapter-{course['id']}.html")
    print(f'页面导出完成：{len(courses)} 章')

    export_qbank()

    # 星海图的数据也走静态文件
    stars_file = DOCS / 'stars.html'
    stars = stars_file.read_text(encoding='utf-8')
    stars = stars.replace('data-universe-url="/api/knowledge-universe"',
                          'data-universe-url="data/knowledge-universe.json"')
    stars = stars.replace('data-dashboard-url="/dashboard"', 'data-dashboard-url="index.html"')
    stars_file.write_text(stars, encoding='utf-8')

    universe = client.get('/api/knowledge-universe').get_json()
    for galaxy in universe['galaxies']:
        for star in galaxy['stars']:
            star['url'] = re.sub(r'^/chapter/(\d+)', r'chapter-\1.html', star['url'])
    (DOCS / 'data').mkdir(exist_ok=True)
    (DOCS / 'data' / 'knowledge-universe.json').write_text(
        json.dumps(universe, ensure_ascii=False, indent=2), encoding='utf-8')

    # 术语表是纯静态数据，导出后在线站也能查（static_mode.js 会转到这个文件）
    (DOCS / 'data' / 'glossary.json').write_text(
        json.dumps(client.get('/api/glossary').get_json(), ensure_ascii=False),
        encoding='utf-8')

    star_script = DOCS / 'static' / 'js' / 'knowledge_stars.js'
    source = star_script.read_text(encoding='utf-8')
    source = source.replace("location.assign('/dashboard')",
                            "location.assign(document.body.dataset.dashboardUrl||'index.html')")
    source = source.replace("else location.assign('/dashboard')",
                            "else location.assign(document.body.dataset.dashboardUrl||'index.html')")
    star_script.write_text(source, encoding='utf-8')

    if samples:
        exported = export_narrations(samples)
        total_images = sum(item['images'] for item in exported)
        print(f'讲解样例导出：{len(exported)} 节 / {total_images} 张配图')
        for item in exported:
            print(f"   · {item['key']:<6} {item['title'][:28]}")
    else:
        (DOCS / 'data' / 'narrations').mkdir(parents=True, exist_ok=True)
        (DOCS / 'data' / 'narrations' / 'index.json').write_text(
            json.dumps({'total': 0, 'online': []}, ensure_ascii=False), encoding='utf-8')

    doc = render_doc_page()
    if doc:
        print(f'客户更新说明已渲染为在线页面：docs/{doc}')

    size = sum(f.stat().st_size for f in DOCS.rglob('*') if f.is_file())
    print(f'\nGitHub Pages 构建完成 -> {DOCS}')
    print(f'总体积：{size / 1024 / 1024:.1f} MB')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导出 GitHub Pages 静态站')
    parser.add_argument('--samples', type=int, default=8, help='导出几节讲解样例')
    args = parser.parse_args()
    build(args.samples)
