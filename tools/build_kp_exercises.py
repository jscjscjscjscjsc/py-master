"""从知识点正文里生成"具体的"随堂练习。

要解决的问题
------------
平台原本对"没有配套练习"的知识点统一塞一句模板话：

    编写代码验证「4.3 格式化进阶：对齐、千分位、百分比」
    提示：用代码把「4.3 格式化进阶：对齐、千分位、百分比」的核心用法演示一遍，并打印出结果。
    判定：代码成功运行即表示你已掌握本知识点！

问题有三层：
  1. 学生不知道该写什么 —— "核心用法"是个空洞的指代；
  2. 判定形同虚设 —— "能运行就算掌握"，`print(1)` 也能过；
  3. 439 个知识点里约 227 个走的是这条兜底路径，占比过半。

改成什么
--------
用**知识点自己的代码案例**生成题目：
  · 题目要求：把该知识点的关键代码改成有明确的输入与预期
  · 给一段挖空的起始代码（骨架），而不是空白编辑器
  · 判据用"实际输出与预期一致"，而不是"跑起来就行"

对确实没有代码的知识点（概念、协作、流程类），不再硬塞编程题 ——
改为不给练习，正文末尾保留自测提示。硬塞只会让学生无从下手。

用法：
    python tools/build_kp_exercises.py --check    # 看看会生成什么
    python tools/build_kp_exercises.py            # 写入 data/kp_exercises.json
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / 'data' / 'courses.json'
OUT = ROOT / 'data' / 'kp_exercises.json'

# 代码案例：代码块 + 紧随其后的运行结果（如果有）
# 宽松匹配：只要「代码案例 N：标题（标记）」后面**跟着一个代码块**就算，
# 运行结果可有可无（有则用作判据，无则只给要求）。
# 关键在最后那段：要**跨过中间的讲解文字**去找「运行结果」，
# 但被下一个代码块挡住（否则会一路吃到后面案例的结果）。
# 用 `.{0,400}?` 非贪婪会立刻收尾，group(5) 永远为空 —— 这个坑踩过两次。
CASE_RE = re.compile(
    r'<p><strong>代码案例\s*([\d.]+)\s*</strong>[：:]\s*([^<（(]*)[（(]([^）)]*)[）)]\s*</p>\s*'
    r'<div class="md-codeblock"[^>]*>.*?<pre><code[^>]*>(.*?)</code></pre></div>',
    re.S)

# 运行结果单独匹配：接在代码块后面的一段里找。
# 不跟 CASE_RE 合成一个正则 —— 中间可能隔着讲解段落、冒号可能在
# strong 标签内外、末尾可能有句号，合成后极其脆弱（这个坑踩过三次）。
RUN_RE = re.compile(
    r'<p><strong>运行结果</strong>\s*[：:]?\s*</p>\s*'
    r'<div class="md-figure"><pre class="md-diagram">(.*?)</pre></div>',
    re.S)

# 一段正文里最多往后找这么多字符，避免把后面案例的结果算进来
RUN_LOOKAHEAD = 700


def find_run_output(content, end_pos):
    """从代码块结束处往后找最近的「运行结果」。找不到返回 ''。"""
    seg = content[end_pos:end_pos + RUN_LOOKAHEAD]
    # 遇到下一个代码块就停，那说明这个案例没有结果
    nxt = seg.find('<div class="md-codeblock"')
    if nxt >= 0:
        seg = seg[:nxt]
    m = RUN_RE.search(seg)
    return m.group(1) if m else ''


# 不生成练习的情况：跑不起来的示例、需要外部资源、故意错误
SKIP_MARK = ('❌', '错误', '反例', 'PowerShell', '终端', 'cmd')
SKIP_CODE = (r'\binput\s*\(', r'\bopen\s*\(', r'\brequests\.', r'\bimport\s+sqlite3',
             r'\bsocket\b', r'time\.sleep', r'\bwhile\s+True\b', r'\bimport\s+subprocess')


# 通用兜底：不只认"代码案例"，任何「标记 + 代码块 + 运行结果」都可用。
# 教材里还有大量 "问题代码 / 预期输出 / 实际输出"、"示例"、"对比" 等写法，
# 只认一个标记会漏掉三分之二的知识点。
GENERIC_RE = re.compile(
    r'<p><strong>([^<]{2,26}?)</strong>[^<]{0,20}</p>\s*'
    r'<div class="md-codeblock" data-lang="python"[^>]*>.*?<pre><code[^>]*>(.*?)</code></pre></div>',
    re.S)

# 明显是"给出来让人看"的标记，不当练习素材
NOT_EXERCISE = ('学完本章', '前置知识', '知识树', '必须记住', '讲授', '练习 ', '休息',
                '任务名称', '任务内容', 'Review 清单', '参考提问', '提示', '讲解',
                '结论', '就业提示', '实战目标', '本节小结', '本章小结', '问题描述')


def unescape(t):
    return html.unescape(t or '').strip().replace('\u00a0', ' ')


def strip_comments(code):
    """删掉整行注释，留下的才是"要写的代码"。"""
    keep = []
    for line in code.splitlines():
        if line.strip().startswith('#'):
            continue
        keep.append(line)
    return '\n'.join(keep).strip()


def blank_out(code):
    """把代码挖空成"可读的骨架"。

    关键取舍：**不能挖太狠**。第一版把每个赋值都换成 `____`，
    结果样例长这样（学生看到直接懵，等于没给骨架）：

        ____
        ____
        ____

    现在的策略：前 60% 给完整代码作示范（让他看懂这段在干什么），
    只把**后面要动手的部分**挖空。骨架必须一眼能读懂。
    """
    lines = code.splitlines()
    if len(lines) <= 2:
        return '\n'.join(lines[:-1] + ['____']).strip()

    keep = max(1, int(len(lines) * 0.6))
    out = list(lines[:keep])
    for line in lines[keep:]:
        stripped = line.strip()
        indent = line[:len(line) - len(line.lstrip())]
        if not stripped:
            out.append('')
            continue
        # 控制流骨架保留，让学生看到结构
        if re.match(r'^(def |class |for |while |if |elif |else|try|except|finally|'
                    r'with |import |from |return|pass|@)', stripped):
            out.append(line)
            continue
        m = re.match(r'^([A-Za-z_][\w\.\[\]]*)\s*=(.*)$', stripped)
        if m:
            out.append(f'{indent}{m.group(1)} = ____   # 这里要你来写')
            continue
        if stripped.startswith('print('):
            out.append(f'{indent}print(____)   # 补上要打印的内容')
            continue
        out.append(f'{indent}____')
    return '\n'.join(out).strip()


def make_exercise(kp_title, case_id, case_title, code, stated_out):
    """按一个代码案例生成练习。"""
    code = strip_comments(code)
    if not code:
        return None

    skeleton = blank_out(code)
    expect = (stated_out or '').strip()

    prompt_parts = [f'照着「{case_title}」的做法，把下面的代码补完整，让它能跑出正确结果。']
    if expect:
        prompt_parts.append('跑出来的结果应该是：')
        prompt_parts.append(expect)
    else:
        prompt_parts.append('补完后运行，确认结果符合这个知识点的用法。')

    return {
        'type': 'code',
        'title': f'补全代码：{case_title}',
        'prompt': '\n'.join(prompt_parts),
        'starter': skeleton,
        'expect': expect,
        'source': f'代码案例 {case_id}',
    }


def build(chapter_filter=None):
    data = json.loads(COURSES.read_text(encoding='utf-8'))
    result = {}
    stats = {'kp_total': 0, 'generated': 0, 'no_code': 0, 'skipped': 0}

    for course in data:
        if chapter_filter and course['id'] != chapter_filter:
            continue
        kps = course.get('knowledge_points', [])
        per_chapter = {}
        for idx, kp in enumerate(kps):
            stats['kp_total'] += 1
            content = kp.get('content', '')
            # 先找标准的"代码案例 N：标题"，找不到就用通用匹配
            cands = [(m, True) for m in CASE_RE.finditer(content)]
            if not cands:
                cands = [(m, False) for m in GENERIC_RE.finditer(content)]
            if not cands:
                stats['no_code'] += 1
                continue

            made = None
            for m, is_standard in cands:
                if is_standard:
                    case_id, case_title, mark = m.group(1), m.group(2).strip(), m.group(3)
                    code_html = m.group(4)
                    out_html = find_run_output(content, m.end())
                else:
                    # 通用匹配：group1=标记名 group2=代码 group3=输出
                    case_title = m.group(1).strip()
                    case_id = ''
                    code_html = m.group(2)
                    out_html = find_run_output(content, m.end())
                    if any(w in case_title for w in NOT_EXERCISE):
                        continue
                if any(w in mark for w in SKIP_MARK):
                    continue
                # 只有"有代码"才值得做练习；没有预期输出的也可以
                # （要求写成"跑出符合该知识点的结果"）
                m2 = re.match(r'.*', code_html)
                # 复用下面的解析
                _ = m2
                code = unescape(code_html)
                if any(re.search(pat, code) for pat in SKIP_CODE):
                    continue
                if len(code.splitlines()) < 2:
                    continue
                made = make_exercise(kp['title'], case_id, case_title, code,
                                     unescape(out_html))
                if made:
                    break
            if made:
                per_chapter[str(idx)] = made
                stats['generated'] += 1
            else:
                stats['skipped'] += 1
        if per_chapter:
            result[str(course['id'])] = per_chapter
    return result, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--chapter', type=int)
    args = ap.parse_args()

    data, stats = build(args.chapter)
    n = sum(len(v) for v in data.values())
    print('随堂练习生成')
    print('=' * 62)
    print(f"  知识点总数 {stats['kp_total']}")
    print(f"  生成具体练习 {stats['generated']}（覆盖 {len(data)} 章）")
    print(f"  无可生成的代码案例 {stats['no_code']}")
    print(f"  有代码但都被跳过 {stats['skipped']}")
    print(f'  合计产出 {n} 道')

    # 抽几个样例看看样子
    print('\n样例：')
    shown = 0
    for cid, kps in data.items():
        for idx, ex in kps.items():
            print(f"\n  【ch{cid} · 知识点{idx}】{ex['title']}")
            print('  ' + ex['prompt'].replace('\n', '\n  ')[:300])
            print('  --- 起始代码 ---')
            print('  ' + ex['starter'].replace('\n', '\n  ')[:260])
            shown += 1
            break
        if shown >= 2:
            break

    if args.check:
        print('\n--check：未写入')
        return 0
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n已写入 {OUT.name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
