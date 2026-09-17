"""题库全量自测：每道题的参考答案都必须能通过它自己的断言。

这一步不能省。手写 120 道题的断言，必然会有几道因为「我算错了期望值」
或「断言写得比题面更严」而误判——上线后表现就是学生写对了却判错，
那是最伤人的 bug。所以题库改了就必须重跑这个脚本。

用法：
```bash
python tools/verify_qbank.py               # 全部
python tools/verify_qbank.py --module algo # 只验算法篇
python tools/verify_qbank.py --id ch05-02  # 只验一题（调试用，会打印输出）
python tools/verify_qbank.py --show 5      # 只打印前 5 题的详情
```
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import training_engine as te  # noqa: E402

MODULES = ['qbank_basic', 'qbank_pro', 'qbank_algo', 'qbank_408', 'qbank_leetcode',
           'qbank_xust823a', 'qbank_xust823b', 'qbank_xust823c', 'qbank_xust823d',
           'qbank_os_exam', 'qbank_osa', 'qbank_osb']


def load_questions(only_module=None, only_id=None):
    items = []
    for name in MODULES:
        if only_module and name != f'qbank_{only_module}':
            continue
        try:
            module = __import__(name)
        except ImportError:
            continue
        for q in module.QUESTIONS:
            if only_id and q['id'] != only_id:
                continue
            items.append((name, q))
    return items


def check_schema(q, problems):
    """结构体检：缺字段的题目会让前端直接渲染不出来。"""
    required = ['id', 'chapter_id', 'title', 'difficulty', 'statement', 'solution']
    for field in required:
        if not q.get(field):
            problems.append(f'{q.get("id", "?")}: 缺少字段 {field}')
    if q.get('difficulty') not in (1, 2, 3):
        problems.append(f'{q["id"]}: difficulty 必须是 1/2/3，实际 {q.get("difficulty")}')
    if not q.get('checks') and not (q.get('expected_output') or '').strip():
        problems.append(f'{q["id"]}: 既没有 checks 也没有 expected_output，无法判题')
    if q.get('track') == 'algorithm' and not q.get('topic'):
        problems.append(f'{q["id"]}: 算法题必须带 topic')
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', help='只验某一篇：basic / pro / algo')
    parser.add_argument('--id', help='只验一道题')
    parser.add_argument('--show', type=int, default=0, help='打印前 N 题的输出详情')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    items = load_questions(args.module, args.id)
    if not items:
        print('没有找到题目。')
        return 1

    print(f'题库自测：共 {len(items)} 道题\n' + '─' * 60)
    started = time.time()
    failed, schema_problems = [], []
    chapters = set()
    difficulty_count = {1: 0, 2: 0, 3: 0}

    for index, (module_name, q) in enumerate(items, 1):
        check_schema(q, schema_problems)
        chapters.add(q['chapter_id'])
        difficulty_count[q['difficulty']] = difficulty_count.get(q['difficulty'], 0) + 1

        cells = [q['solution']]
        result = te.judge(q, cells, stdin_text=q.get('stdin', ''))
        ok = result.get('passed')
        if not ok:
            failed.append((q, result))
        mark = '✓' if ok else '✗'
        if not args.quiet:
            print(f'{mark} [{q["id"]:>9}] {q["title"]}')
        if not ok or (args.show and index <= args.show):
            print('    ' + (result.get('error') or '').replace('\n', '\n    ')[:1200])
            if args.show and index <= args.show:
                print('    ── 输出 ──')
                print('    ' + (result.get('detail') or '').replace('\n', '\n    ')[:600])
                print('    ── 期望 ──')
                print('    ' + (q.get('expected_output') or '(无)').replace('\n', '\n    ')[:400])

    elapsed = round(time.time() - started, 1)
    print('─' * 60)
    print(f'通过 {len(items) - len(failed)}/{len(items)}，耗时 {elapsed}s')
    print(f'难度分布：简单 {difficulty_count.get(1, 0)} / 中等 {difficulty_count.get(2, 0)} / 较难 {difficulty_count.get(3, 0)}')
    print(f'覆盖章节 {len(chapters)} 个：{sorted(chapters)}')
    if schema_problems:
        print(f'\n结构问题 {len(schema_problems)} 处：')
        for p in schema_problems:
            print('  ⚠ ' + p)
    if failed:
        print(f'\n失败 {len(failed)} 道：')
        for q, result in failed:
            print(f'  ✗ {q["id"]} {q["title"]}')
            print('    ' + (result.get('error') or '').replace('\n', '\n    ')[:400])
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
