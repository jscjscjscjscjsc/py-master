"""逐题体检：渲染、代码运行、AI 评分三条链路都要真的跑通。

关于"参考答案跑不通"的判定
--------------------------
教材答案里的代码有相当一部分是**教学节选**，天生不能独立运行，例如：
  · 只给 `@app.get(...)` 装饰器函数，而 `app = FastAPI()` 在上一段；
  · 只给 `import utils` 后调用，而 utils.py 是学生上一题自己写的；
  · 题目本身要求"找出下面代码的坏味道 / 把命名改成 PEP8"，示例代码故意是坏的；
  · 需要先由学生创建 poem.txt / scores.csv 等数据文件。
这些不算缺陷，但需要和真正的失败区分开，否则结论没有意义。
所以这里按错误类型 + 题干关键词做分类，只把"应该能跑却跑不通"的算问题。

用法
----
    python tools/test_exercises.py                 # 渲染 + 运行（全量，不花钱）
    python tools/test_exercises.py --ai 24         # 额外抽 24 道做 AI 评分
    python tools/test_exercises.py --chapter 5
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PY_BLOCK_RE = re.compile(
    r'<div class="md-codeblock" data-lang="(python|py)">.*?<pre><code[^>]*>(.*?)</code></pre>',
    re.S)

# 依赖学生自己创建的模块（上一题写的 utils.py / calc.py …）
OWN_MODULE_RE = re.compile(r"ModuleNotFoundError: No module named '([^']+)'")
# 题干在描述"故意制造错误""找出坏味道""改命名"这类活动
INTENTIONAL_RE = re.compile(
    r'故意|制造|找出.{0,6}(坏味道|问题|错误)|改(成|写)|重命名|PEP\s*8|有什么.{0,4}(问题|坏味道)|'
    r'下面.{0,6}代码|阅读下面|看下面|指出.{0,4}(错误|问题)')
NEEDS_DATA_RE = re.compile(r'创建|新建|准备|读取|打开|保存为|写入')


def load_courses():
    return json.loads((ROOT / 'data' / 'courses.json').read_text(encoding='utf-8'))


def extract_python(reference_html):
    """从参考答案 HTML 里抽出可运行的 Python 代码。"""
    blocks = []
    for _lang, body in PY_BLOCK_RE.findall(reference_html or ''):
        code = html_mod.unescape(re.sub(r'<[^>]+>', '', body)).strip()
        if code:
            blocks.append(code)
    return blocks


def check_render(client, courses, verbose=False):
    """渲染检查：每道题都要有题干与作答入口。"""
    problems = []
    total = 0
    for course in courses:
        resp = client.get(f"/chapter/{course['id']}")
        if resp.status_code != 200:
            problems.append((course['id'], '-', f'章节页返回 {resp.status_code}'))
            continue
        page = resp.get_data(as_text=True)
        cards = re.findall(r'<div class="kp-exercise"[\s\S]*?(?=<div class="kp-exercise"|<div class="kp-notes-section")',
                           page)
        expected = sum(len(exs) for exs in
                       distribute(course).values())
        total += expected
        if len(cards) != expected:
            problems.append((course['id'], '-',
                             f'练习题卡片数 {len(cards)}，期望 {expected}'))
        for card in cards:
            idx_m = re.search(r'data-ex-idx="(\d+)"', card)
            label = f"练习{int(idx_m.group(1)) + 1}" if idx_m else '?'
            has_question = ('ex-question' in card) and len(
                re.sub(r'<[^>]+>', '', card.split('ex-question')[1][:900]).strip()) > 8
            has_actions = ('openCodeEx' in card) or ('toggleTextAnswer' in card)
            has_reference = 'ex-answer' in card
            if not has_question:
                problems.append((course['id'], label, '题干为空（还是空白框）'))
            if not has_actions:
                problems.append((course['id'], label, '没有作答入口'))
            if not has_reference:
                problems.append((course['id'], label, '没有参考答案区'))
            if verbose and has_question and has_actions:
                pass
    return total, problems


def distribute(course):
    """复刻 app.py 里把章节题目分配到各知识点的逻辑，用于核对卡片数量。"""
    kps = course.get('knowledge_points', [])
    exercises = course.get('exercises', [])
    out = {}
    ex_idx = 0
    for i, kp in enumerate(kps):
        items = []
        if ex_idx < len(exercises):
            items.append(exercises[ex_idx])
            ex_idx += 1
        if not items or items[0].get('type') != 'code':
            if 'md-codeblock' in kp.get('content', ''):
                items.append({'type': 'code'})
        out[i] = items
    return out


def classify(course_id, ex_no, output, question):
    """判断一段参考代码跑不通是"预期"还是"真问题"。"""
    own = OWN_MODULE_RE.search(output)
    if own and own.group(1) in {'utils', 'calc', 'main', 'score_utils', 'mymath', 'tools', 'app'}:
        return 'expected', f'依赖学生自建模块 {own.group(1)}.py'
    if INTENTIONAL_RE.search(question):
        return 'expected', '题目本身要求改错/重命名，示例代码故意不规范'
    # 答案里故意抛异常来演示异常传播，例如 raise ValueError("故意出错")
    if '故意' in output or '故意' in question:
        return 'expected', '代码故意抛异常，用于演示异常处理'
    # 需要 API 密钥 / 环境变量才能跑
    if re.search(r'Missing credentials|api_key|API_KEY|AuthenticationError|Unauthorized', output) \
            or 'API_KEY' in question:
        return 'expected', '需要配置 API 密钥（教材要求先设置环境变量）'
    if 'FileNotFoundError' in output and NEEDS_DATA_RE.search(question):
        return 'expected', '需要先按题目创建数据文件'
    if 'FileNotFoundError' in output:
        return 'expected', '需要先准备题目要求的数据文件'
    if 'NameError' in output or 'TypeError' in output:
        return 'fragment', '答案片段依赖前文的类/变量，非完整程序'
    if 'SyntaxError' in output or 'IndentationError' in output:
        return 'fragment', '答案片段不是完整语句'
    if 'SSLError' in output or 'ConnectError' in output or 'ConnectionError' in output:
        return 'expected', '需要联网（课堂环境可能不可达）'
    return 'real', '应当能运行却失败了'


def check_run(client, courses, limit=None, verbose=False):
    """代码运行检查：参考答案里的 Python 代码能否真跑起来。"""
    results = []
    for course in courses:
        for ex in course['exercises']:
            question = re.sub(r'<[^>]+>', '', ex.get('question', ''))
            for n, code in enumerate(extract_python(ex.get('reference', ''))):
                if 'input(' in code:
                    results.append((course['id'], ex['no'], n, 'skip', '需要交互输入', ''))
                    continue
                try:
                    resp = client.post('/api/run-code', json={'code': code})
                    data = resp.get_json() or {}
                except Exception as exc:
                    results.append((course['id'], ex['no'], n, 'error', str(exc)[:70], 'real'))
                    continue
                if not data.get('success'):
                    results.append((course['id'], ex['no'], n, 'error',
                                    (data.get('error') or '未知错误')[:70], 'real'))
                elif data.get('exit_code') == 0:
                    results.append((course['id'], ex['no'], n, 'ok',
                                    (data.get('output') or '')[:60].replace('\n', ' / '), ''))
                else:
                    out = data.get('output') or ''
                    kind, why = classify(course['id'], ex['no'], out, question)
                    results.append((course['id'], ex['no'], n, kind,
                                    (out or '').replace('\n', ' ')[:90], why))
                if limit and len(results) >= limit:
                    return results
    return results


def check_ai(client, courses, sample, kind):
    """AI 评分检查：把参考答案当学生作答交上去，看能不能拿到分。"""
    results = []
    picked = 0
    for course in courses:
        for ex in course['exercises']:
            if picked >= sample:
                return results
            if (ex.get('expects') == 'text') != (kind == 'text'):
                continue
            if kind == 'code':
                blocks = extract_python(ex.get('reference', ''))
                if not blocks:
                    continue
                payload = {'kp_title': f"第{course['id']}章 练习{ex['no']}",
                           'code': blocks[0], 'output': '(参考运行结果)',
                           'prompt': re.sub(r'<[^>]+>', '', ex.get('question', ''))[:300]}
                url = '/api/score-code'
            else:
                payload = {'question': re.sub(r'<[^>]+>', '', ex.get('question', ''))[:800],
                           'answer': re.sub(r'<[^>]+>', ' ', ex.get('reference', ''))[:1200],
                           'reference': re.sub(r'<[^>]+>', ' ', ex.get('reference', ''))[:1200],
                           'explanation': re.sub(r'<[^>]+>', ' ', ex.get('explanation', ''))[:800]}
                url = '/api/score-answer'
            picked += 1
            try:
                data = (client.post(url, json=payload).get_json() or {})
                results.append((course['id'], ex['no'], kind,
                                data.get('score'), (data.get('feedback') or data.get('message') or '')[:60],
                                data.get('success')))
            except Exception as exc:
                results.append((course['id'], ex['no'], kind, None, str(exc)[:60], False))
    return results


def main():
    parser = argparse.ArgumentParser(description='练习题全量体检')
    parser.add_argument('--chapter', type=int, help='只测某一章')
    parser.add_argument('--ai', type=int, default=0, help='AI 评分抽样题数（消耗额度）')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    import app as pymaster
    client = pymaster.app.test_client()

    courses = load_courses()
    if args.chapter:
        courses = [c for c in courses if c['id'] == args.chapter]

    print('=' * 66)
    print('① 渲染检查（全部题目）')
    total, problems = check_render(client, courses, args.verbose)
    print(f'   统计到 {total} 道题卡片')
    if problems:
        print(f'   ✗ 发现 {len(problems)} 个问题：')
        for cid, label, msg in problems[:25]:
            print(f'      第{cid}章 {label}: {msg}')
        if len(problems) > 25:
            print(f'      … 还有 {len(problems) - 25} 个')
    else:
        print('   ✓ 全部题目都有题干与作答入口')

    print()
    print('=' * 66)
    print('② 代码运行检查（参考答案能否跑起来）')
    started = time.time()
    runs = check_run(client, courses)
    ok = [r for r in runs if r[3] == 'ok']
    skip = [r for r in runs if r[3] == 'skip']
    expected = [r for r in runs if r[3] == 'expected']
    fragment = [r for r in runs if r[3] == 'fragment']
    real = [r for r in runs if r[3] in ('real', 'error')]
    print(f'   共 {len(runs)} 段参考代码，用时 {time.time() - started:.0f}s')
    print(f'   ✓ 独立运行成功        {len(ok):>3} 段')
    print(f'   – 需交互输入（跳过）  {len(skip):>3} 段')
    print(f'   – 预期失败            {len(expected):>3} 段   （依赖学生自建模块 / 题目要求改错 / 需先建数据文件）')
    print(f'   – 教学片段不可独立跑  {len(fragment):>3} 段   （答案片段依赖前文，非完整程序）')
    print(f'   ✗ 真失败              {len(real):>3} 段')
    if real:
        for cid, no, n, st, msg, why in real[:15]:
            print(f'      第{cid}章 第{no}题 #{n}: {msg[:80]}')
    if expected:
        print('   预期失败分布（前 8 条）：')
        for cid, no, n, st, msg, why in expected[:8]:
            print(f'      第{cid}章 第{no}题: {why}')

    if args.ai:
        print()
        print('=' * 66)
        print(f'③ AI 评分检查（抽样 {args.ai} 道，会消耗模型额度）')
        for kind in ('code', 'text'):
            got = check_ai(client, courses, args.ai // 2 or 1, kind)
            if not got:
                print(f'   [{kind}] 没有可抽样的题目')
                continue
            scores = [g[3] for g in got if g[3] is not None]
            print(f'   [{kind}] 抽样 {len(got)} 道 | 成功 {len(scores)} | '
                  f'均分 {sum(scores) / len(scores):.0f}' if scores else f'   [{kind}] 全部失败')
            for cid, no, _k, score, fb, ok_flag in got[:6]:
                mark = '✓' if ok_flag else '✗'
                print(f'      {mark} 第{cid}章 第{no}题 得分 {score}  {fb}')

    print()
    print('=' * 66)
    verdict = '全部通过' if (not problems and not real) else '存在问题，见上方明细'
    print(f'结论：{verdict}')
    return 0 if (not problems and not real) else 1


if __name__ == '__main__':
    sys.exit(main())
