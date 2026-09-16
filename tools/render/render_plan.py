"""讲解配图的截图器：把 build-plan.mjs 生成的 HTML 计划渲染成 1080×1080 课件图。

复用 Python Playwright 已安装的 Chromium，一个浏览器会话连续截图，
单张约 0.1–0.3 秒，几千张也能在几分钟内出完。

用法
    python tools/render/render_plan.py                    # 渲染 tools/render/build-plan.json
    python tools/render/render_plan.py --sheet            # 渲染样张计划（等价于先跑 build-plan.mjs --sheet）
    python tools/render/render_plan.py --limit 8          # 只渲染前 N 张（抽样检查用）
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent          # 发布版/
PLAN_FILE = Path(__file__).resolve().parent / 'build-plan.json'

SIZE = 1080
QUALITY = 86


def render(limit: int | None = None) -> int:
    if not PLAN_FILE.exists():
        print('找不到 build-plan.json，请先运行：node tools/render/build-plan.mjs')
        return 1
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8'))
    if limit:
        plan = plan[:limit]
    if not plan:
        print('计划为空，没有需要渲染的图')
        return 0

    from playwright.sync_api import sync_playwright

    print(f'待渲染 {len(plan)} 张')
    started = time.time()
    done = failed = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': SIZE, 'height': SIZE}, device_scale_factor=1)
        try:
            for item in plan:
                target = ROOT / item['out'].replace('/', '\\')
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    page.set_content(item['html'], wait_until='load')
                    page.evaluate('document.fonts.ready')
                    page.screenshot(path=str(target), type='jpeg', quality=QUALITY)
                    done += 1
                except Exception as exc:
                    failed += 1
                    print(f"  ✗ {item['out']}: {type(exc).__name__}: {exc}")
                if done % 100 == 0 and done:
                    rate = done / max(time.time() - started, 0.01)
                    print(f'  进度 {done}/{len(plan)}  {time.time() - started:.0f}s  {rate:.1f} 张/秒')
        finally:
            browser.close()

    elapsed = time.time() - started
    print(f'完成：成功 {done} 张，失败 {failed} 张，用时 {elapsed:.1f}s'
          f'（{done / max(elapsed, 0.01):.1f} 张/秒）')
    return 0 if failed == 0 else 2


def main():
    parser = argparse.ArgumentParser(description='渲染讲解配图')
    parser.add_argument('--limit', type=int, help='只渲染前 N 张')
    args = parser.parse_args()
    return render(args.limit)


if __name__ == '__main__':
    sys.exit(main())
