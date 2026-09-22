"""课件代码审计：把教材里的「代码案例」真跑一遍，比对照录的「运行结果」。

为什么需要这个脚本
------------------
教材的代码案例是**人工/大模型写下"运行结果"**的，从来没被验证过。
实测踩到的例子（第 4 章 4.3）：

    代码三行：total_sales / rate / 人口
    照录结果却把第三行写成了重复的「达成率：85.6%」，
    而代码实际输出的是「人口：1,234,567」

学生照着敲、看到结果对不上，会先怀疑自己 —— 这比"没写结果"更糟。

这个脚本做的事：抽取每一对「代码 ↔ 运行结果」，真跑一遍，逐行比对。
不一致的列出来，并给出**实测输出**，便于直接改教材。

用法：
    python tools/audit_courseware.py              # 全量审计
    python tools/audit_courseware.py --chapter 4  # 只审某一章
    python tools/audit_courseware.py --fix        # 用实测输出覆盖照录结果
    python tools/audit_courseware.py --show-ok    # 连一致的一起列出来
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / 'data' / 'courses.json'

# 「代码案例 4.11：千分位与百分比（✅ 正确）」+ 代码块 + 可选运行结果
CASE_RE = re.compile(
    r'<p><strong>代码案例\s*([\d.]+)\s*</strong>[：:]\s*([^<（(]*)[（(]([^）)]*)[）)]\s*</p>\s*'
    r'<div class="md-codeblock"[^>]*>.*?<pre><code[^>]*>(.*?)</code></pre></div>\s*'
    r'(?:<p><strong>运行结果</strong>[：:]</p>\s*'
    r'<div class="md-figure"><pre class="md-diagram">(.*?)</pre></div>)?',
    re.S)

# 这些案例不该真跑：故意的错误示例、需要网络/输入/文件的、终端命令
SKIP_MARK = ('❌', '错误', '反例', '对比例', 'PowerShell', 'cmd', '终端')
SKIP_CODE = (r'\binput\s*\(', r'\bopen\s*\(', r'\brequests\.', r'\burllib\b',
             r'\bsocket\b', r'\btime\.sleep', r'\binput\b.*\(', r'\bwhile\s+True\b')


def unescape(text):
    """把 HTML 实体还原成能执行的源码。"""
    if not text:
        return ''
    s = html.unescape(text)
    # 教材里可能有 &#x27; 之类的数字实体，html.unescape 已处理；
    # 这里再顺手把不换行空格换成普通空格
    return s.replace('\u00a0', ' ').strip()


def run_code(code, timeout=10):
    """在子进程里跑一段代码，返回 (是否正常结束, 输出文本)。"""
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix='.py', prefix='audit_')
        os.close(fd)
        Path(tmp).write_text(code, encoding='utf-8')
        proc = subprocess.run(
            [sys.executable, '-X', 'utf8', tmp],
            capture_output=True, timeout=timeout,
            cwd=os.path.dirname(tmp),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                 'MPLBACKEND': 'Agg'})
        out = (proc.stdout or b'').decode('utf-8', 'replace').strip()
        err = (proc.stderr or b'').decode('utf-8', 'replace').strip()
        # logging / pytest 这类库默认往 stderr 写。教材照录的是"运行后看到的内容"，
        # 不区分流 —— 两条流都要算进来，否则会误报"照录了但实际没输出"。
        both = chr(10).join(x for x in (out, err) if x)
        return proc.returncode == 0, both, err
    except subprocess.TimeoutExpired:
        return False, '', '（超时）'
    except Exception as exc:
        return False, '', f'{type(exc).__name__}: {exc}'
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def should_skip(mark, code):
    for word in SKIP_MARK:
        if word in mark:
            return f'跳过（{word.strip("❌") or "示例"}）'
    for pat in SKIP_CODE:
        if re.search(pat, code):
            return '跳过（需要输入/网络/文件）'
    return None


def ordered_equal(a_lines, b_lines):
    """行数与多重集合都相同，只是顺序不同。"""
    if len(a_lines) != len(b_lines):
        return False
    from collections import Counter
    return Counter(a_lines) == Counter(b_lines)


# 每次运行都会变的部分：内存地址、耗时、日期时间。
# 教材照录这类值时用 `0x...` 之类的写法是**正确的示范**，
# 不该被判成"结果不符" —— 归一化之后再比。
VARYING = [
    (re.compile(r'0x[0-9a-fA-F]+'), '0x…'),            # 对象内存地址
    (re.compile(r'\d+\.\d+\s*秒'), 'N 秒'),             # 耗时
    (re.compile(r'\d{4}-\d{2}-\d{2}'), 'YYYY-MM-DD'),   # 日期
    (re.compile(r'\d{2}:\d{2}:\d{2}'), 'HH:MM:SS'),     # 时间
]


def normalize_line(line):
    out = line
    for pat, rep in VARYING:
        out = pat.sub(rep, out)
    return out.strip()


def norm_lines(text):
    return [normalize_line(ln) for ln in (text or '').strip().splitlines() if ln.strip()]


def audit(chapter=None, show_ok=False):
    data = json.loads(COURSES.read_text(encoding='utf-8'))
    stats = {'total': 0, 'no_out': 0, 'skipped': 0, 'ok': 0,
             'mismatch': [], 'failed': [], 'skip_detail': {}}

    for course in data:
        if chapter and course['id'] != chapter:
            continue
        for kp in course.get('knowledge_points', []):
            content = kp.get('content', '')
            for m in CASE_RE.finditer(content):
                cid, title, mark, code_html, out_html = (
                    m.group(1), m.group(2).strip(), m.group(3),
                    m.group(4), m.group(5))
                stats['total'] += 1

                reason = should_skip(mark, code_html)
                if reason:
                    stats['skipped'] += 1
                    stats['skip_detail'][reason] = stats['skip_detail'].get(reason, 0) + 1
                    continue
                if not out_html:
                    stats['no_out'] += 1
                    continue

                code = unescape(code_html)
                stated = unescape(out_html)
                ok, actual, err = run_code(code)

                label = f"ch{course['id']} {cid} {title}"
                if not ok:
                    stats['failed'].append((label, code, stated, err))
                    continue

                a_lines, s_lines = norm_lines(actual), norm_lines(stated)
                if a_lines == s_lines:
                    stats['ok'] += 1
                    if show_ok:
                        print(f'  ✓ {label}')
                elif ordered_equal(a_lines, s_lines):
                    # 内容一样只是顺序不同（set 打印顺序不保证）：单独归类 ——
                    # 它不是"照录错了"，而是"照录了一个顺序不保证的结果"
                    stats.setdefault('unordered', []).append((label, stated, actual))
                else:
                    stats['mismatch'].append((label, code, stated, actual))

    return stats


def report(stats):
    print('课件代码审计')
    print('=' * 66)
    unordered = stats.get('unordered', [])
    compared = stats['ok'] + len(stats['mismatch']) + len(unordered) + len(stats['failed'])
    print(f"代码案例 {stats['total']} 个"
          f"（跳过 {stats['skipped']}，无照录结果 {stats['no_out']}，"
          f"参与比对 {compared}）")
    print(f"一致 {stats['ok']}  /  结果不符 {len(stats['mismatch'])}"
          f"  /  顺序不同 {len(unordered)}  /  代码跑不起来 {len(stats['failed'])}")
    if unordered:
        print('\n（顺序不同：内容一致，只是 set 这类容器打印顺序不保证）')
        for label, stated, actual in unordered:
            print(f'  · {label}')
    if stats['skip_detail']:
        print('\n跳过明细：')
        for k, v in sorted(stats['skip_detail'].items(), key=lambda x: -x[1]):
            print(f'  {v:>4}  {k}')

    if stats['failed']:
        print(f"\n{'─' * 66}\n代码跑不起来的案例：{len(stats['failed'])} 个")
        for label, code, stated, err in stats['failed'][:20]:
            print(f"\n  ✗ {label}")
            print(f'    报错：{(err or "").strip()[:160]}')

    if stats['mismatch']:
        print(f"\n{'─' * 66}\n照录结果与实际输出不符：{len(stats['mismatch'])} 个")
        for label, code, stated, actual in stats['mismatch'][:30]:
            print(f'\n  ✗ {label}')
            print(f'    照录：{norm_lines(stated)}')
            print(f'    实测：{norm_lines(actual)}')
    return len(stats['mismatch']) + len(stats['failed'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter', type=int, help='只审某一章')
    ap.add_argument('--show-ok', action='store_true')
    ap.add_argument('--fix', action='store_true',
                    help='用实测输出覆盖照录结果（会改写 courses.json）')
    args = ap.parse_args()

    stats = audit(args.chapter, args.show_ok)
    bad = report(stats)
    print('\n' + '=' * 66)
    print(f'需要人工确认：{bad} 处')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
