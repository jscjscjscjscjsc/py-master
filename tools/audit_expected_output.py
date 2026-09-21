"""题库审计：参考答案的实际输出 vs 题目里写的 expected_output。

为什么需要这个脚本
------------------
`expected_output` 有两个用途：
  1. 发给前端，学生在「看解析」里看到的就是它；
  2. 对**没有 checks 的题**，它就是判题依据（实际输出必须包含其中每一行）。

`verify_qbank.py` 只验证「参考答案能否通过自己的断言」，它压根不看
expected_output —— 于是这个字段可以一直错着没人发现。已经踩到的实例：
ch04-01 写的是 `yatro02`（连字符串里都没有的字母），正确值是 `PMse22`。
学生看到的「期望输出」是错的，等于在教错东西。

用法：
```bash
python tools/audit_expected_output.py            # 审计全部
python tools/audit_expected_output.py --id ch04-01
python tools/audit_expected_output.py --show-ok   # 连一致的也列出来
```
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import training_engine as te  # noqa: E402
from verify_qbank import load_questions  # noqa: E402


def lines_of(text):
    return [ln.strip() for ln in (text or '').strip().splitlines() if ln.strip()]


def audit_one(q):
    """返回 (状态, 说明)。状态取 ok / mismatch / missing_expect / no_output。"""
    expect = (q.get('expected_output') or '').strip()
    result = te.judge(q, [q['solution']], stdin_text=q.get('stdin', ''))
    actual_raw = result.get('stdout') or result.get('detail') or ''
    actual = lines_of(actual_raw)

    if not expect:
        return 'missing_expect', actual

    wanted = lines_of(expect)
    missing = [w for w in wanted if w not in actual]
    extra = [a for a in actual if a not in wanted]

    if not actual and wanted:
        return 'no_output', {'expect': wanted, 'actual': actual, 'result': result.get('error', '')[:200]}

    if missing:
        return 'mismatch', {'expect': wanted, 'actual': actual,
                            'missing': missing, 'extra': extra}
    if extra:
        # 期望的每一行都在，但实际还多打了内容：判题不会误判，
        # 但学生对照解析时会困惑，值得看一眼
        return 'extra', {'expect': wanted, 'actual': actual, 'extra': extra}
    return 'ok', {'expect': wanted, 'actual': actual}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', help='只审一道题')
    ap.add_argument('--show-ok', action='store_true', help='连一致的也打印')
    ap.add_argument('--limit', type=int, default=0, help='只审前 N 道（调试用）')
    args = ap.parse_args()

    items = load_questions(None, args.id)
    if args.limit:
        items = items[:args.limit]
    print(f'expected_output 审计：共 {len(items)} 道题\n' + '─' * 64)

    buckets = {}
    for module_name, q in items:
        status, info = audit_one(q)
        buckets.setdefault(status, []).append((q, info))

    for status in ('mismatch', 'no_output', 'missing_expect', 'extra'):
        rows = buckets.get(status, [])
        if not rows:
            continue
        label = {
            'mismatch': '❌ 期望与实际不符（会误判 / 会教错）',
            'no_output': '⚠ 参考答案没有输出，但题里写了期望',
            'missing_expect': '⚠ 没有 expected_output 也没有 checks',
            'extra': 'ℹ 期望是子集，实际多打了内容（不会误判，但对照解析时困惑）',
        }[status]
        print(f'\n{label}：{len(rows)} 道')
        for q, info in rows:
            print(f'  [{q["id"]}] {q["title"]}')
            if status == 'missing_expect':
                continue
            if isinstance(info, dict) and info.get('missing'):
                print(f'      期望有、实际没有：{info["missing"]}')
            if isinstance(info, dict) and info.get('expect') is not None:
                print(f'      题目写的期望：{info["expect"]}')
                print(f'      实际输出　　：{info["actual"]}')

    ok_rows = buckets.get('ok', [])
    print(f'\n{"─" * 64}\n一致 {len(ok_rows)} 道'
          f'，不一致 {len(buckets.get("mismatch", []))} 道'
          f'，多余 {len(buckets.get("extra", []))} 道')
    if args.show_ok:
        for q, _ in ok_rows:
            print(f'  ✓ [{q["id"]}] {q["title"]}')
    return 1 if buckets.get('mismatch') else 0


if __name__ == '__main__':
    sys.exit(main())
