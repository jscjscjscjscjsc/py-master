"""判题复核：自动判题说"没过"，但可能只是格式细节不同 —— 交给 AI 再看一眼。

要解决的问题
------------
题库的断言是**精确匹配**：`assert str(acc) == '测试 的账户：余额 120 元'`。
学生逻辑完全写对了，只是少打一个空格、或者把两个字段的顺序调了个头，
就会被判"未通过"。全库统计有 44 处断言是这种"输出字符串必须一字不差"。

这类误判比"判错"更伤人：学生明明做对了，平台却说他错，
他会开始怀疑自己，然后去猜平台的格式偏好 —— 这不是学编程该练的能力。

判题流程（分层）
----------------
    代码跑起来了吗？
      ├─ 没有 → 不通过（真的有问题，AI 也救不了，直接给报错）
      └─ 可以跑
           ├─ 断言全过 → 通过（3 星，最快路径，不花 AI 额度）
           └─ 断言没过 → **交给 AI 复核**
                ├─ AI 说逻辑等价 → 通过（最多 2 星，标注"经复核"）
                └─ AI 说真错   → 不通过，并给出比断言更人话的解释

为什么要有 AI 这一层
--------------------
断言只能表达"结果必须完全等于什么"，表达不了"逻辑对不对"。
比如题目要求"把两个数交换"，学生用临时变量、用元组解包、用加减法，
三种写法断言都能过；但如果题目要求打印 `a=1 b=2`，
学生打印 `a = 1, b = 2`（多了空格和逗号），断言就挂了 —— 而这是对的。

安全边界（重要）
----------------
AI 复核**只放宽"能运行的代码"**，永远不会把跑不起来的代码判成通过。
而且它必须给出理由，理由会被记录下来，教师可以查。
"""
import json
import re

REVIEW_SYSTEM = """你是一位严格的 Python 教学助教，负责复核一次自动判题的结果。

自动判题用的是精确字符串/数值匹配，可能因为**格式细节**而误判。
你要判断的是：学生的代码在**逻辑上**是否已经正确解决了题目要求的问题。

【判 equivalent（逻辑正确）的情况】
- 结果正确，只是输出格式略有差异：空格、标点、大小写、中英文符号
- 打印的措辞与题目示例不完全一致，但含义相同
- 变量名、函数名与参考不同（只要行为正确）
- 用了不同的写法达成同一结果（循环 vs 内置函数、列表推导 vs for）
- 多打印了无关的调试信息，但题目要求的内容都在

【判 wrong（确实有错）的情况】
- 结果算错、逻辑错误
- 只对示例输入有效，换个输入就错
- 题目的关键要求没实现（漏了整整一步，比如要求排序却没排序）
- 代码虽然能运行，但没有真正解决题目要求的问题
- 明显是为了骗过检查而写死答案（比如直接 return 期望值）

判断原则：**看逻辑和结果，不看形式**。但"能跑"不等于"正确"，
不要因为代码能运行就放行 —— 必须确认它真的做对了题目要求的事。

补充：学生可能只提交了题目要求的**一部分**（比如题目要三个函数，
他先写了两个来验证）。这种情况下，只要他写的部分是对的，就算 equivalent ——
不要因为"题目要求的其它部分没出现"就判 wrong。那属于没写完，
不在这次复核范围内（没写完的自然过不了断言）。

只输出 JSON，不要任何其它文字：
{"verdict": "equivalent" 或 "wrong", "reason": "一句话说明你的判断依据"}"""


def build_prompt(question, cells, result, stdout='', expected=''):
    """把复核需要的材料拼成一段话。"""
    statement = (question.get('statement') or '').strip()
    # 题面可能很长，截断到合理长度（够判断即可，也省 token）
    if len(statement) > 1200:
        statement = statement[:1200] + '…'

    code = '\n'.join(str(c) for c in (cells or []))
    if len(code) > 2400:
        code = code[:2400] + '\n…# （代码过长，已截断）'

    out = (stdout or '').strip()
    if len(out) > 800:
        out = out[:800] + '…'

    err = (result.get('error') or '').strip()
    if len(err) > 600:
        err = err[:600] + '…'

    parts = [
        '【题目要求】', statement, '',
        '【学生代码】', '```python', code, '```', '',
    ]
    if out:
        parts += ['【程序实际输出】', '```', out, '```', '']
    if err:
        parts += ['【自动判题的失败原因】', err, '']
    if expected:
        exp = expected.strip()
        if len(exp) > 500:
            exp = exp[:500] + '…'
        parts += ['【题目里的参考输出】', '```', exp, '```', '']
    parts.append(
        '注意：自动判题用的是精确匹配，**断言失败不等于代码错**。\n'
        '请判断：学生的代码在逻辑上是否正确解决了题目要求？')
    return '\n'.join(parts)


def parse_reply(text):
    """从模型回复里取出结论。解析不出来时返回 None（保持原判，不冒险放行）。"""
    if not text:
        return None
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except (ValueError, TypeError):
        return None
    verdict = str(data.get('verdict', '')).strip().lower()
    if verdict not in ('equivalent', 'wrong'):
        return None
    return {
        'verdict': verdict,
        'reason': str(data.get('reason', '')).strip()[:200],
    }


def review(question, cells, result, complete, stdout='', attempts=2):
    """复核一次判题结果。

    `complete` 是一个「给我 prompt，返回模型回复文本」的回调（由 app.py 注入），
    这样本模块不依赖具体的模型客户端，也就好测试。

    返回 {'reviewed': bool, 'pass': bool, 'reason': str}
      reviewed=False 表示没能得出结论（模型不可用/回复不可解析/连接失败），
      此时调用方**保持原判** —— 拿不到结论时宁可维持严格，也不能默认放行。

    会重试：实测模型偶发卡死（同一请求 6 次里有 1 次挂 40 秒以上）。
    复核是"兜底放宽"，晚一点得出结论远好过直接放弃。
    """
    if not complete:
        return {'reviewed': False, 'pass': False, 'reason': '未启用 AI 复核'}

    prompt = build_prompt(question, cells, result, stdout=stdout,
                          expected=question.get('expected_output', ''))

    last_error = ''
    for _attempt in range(max(1, attempts)):
        try:
            reply = complete(prompt)
        except Exception as exc:
            last_error = f'{type(exc).__name__}: {str(exc)[:80]}'
            continue
        parsed = parse_reply(reply)
        if parsed:
            return {
                'reviewed': True,
                'pass': parsed['verdict'] == 'equivalent',
                'reason': parsed['reason'],
                'verdict': parsed['verdict'],
            }
        last_error = '模型回复里没有可解析的结论'
    return {'reviewed': False, 'pass': False, 'reason': f'复核未得出结论（{last_error}）'}
