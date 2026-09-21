"""题库 · 进阶篇（第 15–40 章）配套代码练习。

覆盖工程篇（需求 / 质量 / 测试 / Git / 协作）、全栈篇（架构 / 前端 / 后端 / FastAPI / Vue / 数据）
与 AI 篇（大模型 API / 智能体 / RAG / Agent）。

这些题的设计原则和基础篇不同：**不考语法，考「工作里真会遇到的那一段代码」**。
比如校验一个 API 请求体、按 token 估算裁剪会话历史、解析流式响应、
给检索结果算余弦相似度——都是学生做项目时立刻能用上的片段。

判题约定同基础篇：checks 在参考答案跑完后于同一进程执行，
可用 `_out`（全部输出）与 `_src`（全部源码）。
"""

QUESTIONS = [
    # ── 第 15 章 软件工程导论与需求分析 ────────────────────
    {
        'id': 'ch15-01',
        'chapter_id': 15,
        'title': '把用户故事拆成验收条件',
        'difficulty': 2,
        'tags': ['需求分析', '用户故事', '列表处理'],
        'statement': (
            '用户故事的标准格式是「**作为〈角色〉，我想要〈功能〉，以便〈价值〉**」。\n\n'
            '定义函数 `parse_story(text)`，把一条用户故事解析成字典：\n\n'
            '```python\n'
            "parse_story('作为学生，我想要导出错题，以便考前复习')\n"
            "# → {'role': '学生', 'feature': '导出错题', 'value': '考前复习', 'valid': True}\n"
            '```\n\n'
            '规则：\n'
            '- 按 `作为` / `我想要` / `以便` 三个关键词切分（注意逗号可有可无）\n'
            '- 缺少任一要素时，缺的字段为空字符串 `""`，且 `valid` 为 `False`\n'
            '- 传入空字符串或非字符串时返回 `{"role": "", "feature": "", "value": "", "valid": False}`\n\n'
            '另外定义函数 `check_acceptance(items)`：接收若干验收条件字符串，'
            '返回不符合「可验证」要求的那些条件——判断标准是**必须包含数字或明确的结果词**'
            '（`能` / `可以` / `显示` / `返回`）。\n\n'
            '用几个例子调一遍并打印结果。'
        ),
        'starter_code': "def parse_story(text):\n    pass\n\n\ndef check_acceptance(items):\n    pass\n",
        'solution': (
            "def parse_story(text):\n"
            "    empty = {'role': '', 'feature': '', 'value': '', 'valid': False}\n"
            "    if not isinstance(text, str) or not text.strip():\n"
            "        return dict(empty)\n"
            "    cleaned = text.strip().rstrip('。.')\n"
            "    result = dict(empty)\n"
            "    for key, marker in (('role', '作为'), ('feature', '我想要'), ('value', '以便')):\n"
            "        if marker not in cleaned:\n"
            "            continue\n"
            "        tail = cleaned.split(marker, 1)[1]\n"
            "        for other in ('作为', '我想要', '以便'):\n"
            "            if other != marker and other in tail:\n"
            "                tail = tail.split(other, 1)[0]\n"
            "        result[key] = tail.strip().strip('，,。 ')\n"
            "    result['valid'] = all(result[k] for k in ('role', 'feature', 'value'))\n"
            "    return result\n"
            "\n"
            "\n"
            "def check_acceptance(items):\n"
            "    weak = []\n"
            "    for item in items:\n"
            "        text = str(item)\n"
            "        has_number = any(ch.isdigit() for ch in text)\n"
            "        has_result = any(word in text for word in ('能', '可以', '显示', '返回'))\n"
            "        if not (has_number or has_result):\n"
            "            weak.append(item)\n"
            "    return weak\n"
            "\n"
            "\n"
            "print(parse_story('作为学生，我想要导出错题，以便考前复习'))\n"
            "print(parse_story('我想要一个按钮'))\n"
            "print(parse_story(''))\n"
            "print(check_acceptance(['点击后 3 秒内返回结果', '界面好看', '能显示错题列表']))\n"
        ),
        'checks': [
            "r = parse_story('作为学生，我想要导出错题，以便考前复习')",
            "assert r['role'] == '学生', 'role 解析不对：%r' % (r,)",
            "assert r['feature'] == '导出错题', 'feature 解析不对：%r' % (r,)",
            "assert r['value'] == '考前复习', 'value 解析不对：%r' % (r,)",
            "assert r['valid'] is True, '完整故事应判为 valid=True'",
            "r2 = parse_story('我想要一个按钮')",
            "assert r2['feature'] == '一个按钮' and r2['value'] == '' and r2['valid'] is False, '缺少要素时结果不对：%r' % (r2,)",
            "assert parse_story('') == {'role': '', 'feature': '', 'value': '', 'valid': False}, '空字符串应返回全空且 invalid'",
            "assert parse_story(None)['valid'] is False, '传入 None 不应报错，应返回 invalid'",
            "assert check_acceptance(['点击后 3 秒内返回结果', '界面好看', '能显示错题列表']) == ['界面好看'], 'check_acceptance 应只挑出「界面好看」这种没法验证的条件'",
            "assert check_acceptance([]) == [], '空列表应返回空列表'",
        ],
        'explanation': (
            '用户故事是需求的最小单位，而「验收条件」决定它是否可测。'
            '`界面好看` 这种描述执行时必然扯皮，所以要有一道**可验证性检查**——'
            '本題用「含数字或明确结果词」做粗筛，真实项目里由测试同学人工把关。\n\n'
            '解析实现里有三个细节值得注意：\n'
            '1. `dict(empty)` 每次返回**新字典**，如果返回同一个对象，'
            '调用方改了它就会污染后续所有返回值；\n'
            '2. 先 `rstrip("。.")` 去掉句末标点，否则最后一个字段会带上符号；\n'
            '3. 切分时要把**其它关键词**也当分隔符切掉，'
            '否则 ``我想要`` 后面的内容会把 ``以便`` 那段也吞进来。\n\n'
            '`any(ch.isdigit() for ch in text)` 比正则更轻，'
            '判断「有没有数字」用它足够。'
        ),
        'expected_output': "{'role': '学生', 'feature': '导出错题', 'value': '考前复习', 'valid': True}\n{'role': '', 'feature': '一个按钮', 'value': '', 'valid': False}\n{'role': '', 'feature': '', 'value': '', 'valid': False}\n['界面好看']",
        'hints': ['先用 split(关键词, 1) 把三段切开', '缺字段时返回空字符串而不是 None，方便前端直接渲染'],
    },
    {
        'id': 'ch15-02',
        'chapter_id': 15,
        'title': '需求变更影响面分析',
        'difficulty': 2,
        'tags': ['需求分析', '字典', '集合'],
        'statement': (
            '一个需求有若干实现任务，任务之间有依赖关系。需求一改，要找出**所有受影响的任务**。\n\n'
            '```python\n'
            "tasks = {\n"
            "    '登录接口': [],\n"
            "    '用户表': [],\n"
            "    '会话校验': ['登录接口', '用户表'],\n"
            "    '权限中间件': ['会话校验'],\n"
            "    '订单接口': ['权限中间件'],\n"
            "    '前端登录页': ['登录接口'],\n"
            "}\n"
            '```\n\n'
            '定义函数 `impacted(tasks, changed)`：`changed` 是变更的任务名列表，'
            '返回**所有直接或间接依赖该任务**的任务名集合（含它们自己）。\n\n'
            '例如 `impacted(tasks, ["用户表"])` 应该包含：用户表、会话校验、权限中间件、订单接口、'
            '（因为订单接口依赖权限中间件，权限中间件依赖会话校验，会话校验依赖用户表）。\n'
            '注意 `登录接口` **不**受影响——它不依赖用户表。\n\n'
            '要求处理循环依赖（不能死循环）。最后打印排序后的结果。'
        ),
        'starter_code': "tasks = {\n    '登录接口': [],\n    '用户表': [],\n    '会话校验': ['登录接口', '用户表'],\n    '权限中间件': ['会话校验'],\n    '订单接口': ['权限中间件'],\n    '前端登录页': ['登录接口'],\n}\n\n\ndef impacted(tasks, changed):\n    pass\n",
        'solution': (
            "tasks = {\n"
            "    '登录接口': [],\n"
            "    '用户表': [],\n"
            "    '会话校验': ['登录接口', '用户表'],\n"
            "    '权限中间件': ['会话校验'],\n"
            "    '订单接口': ['权限中间件'],\n"
            "    '前端登录页': ['登录接口'],\n"
            "}\n"
            "\n"
            "\n"
            "def impacted(tasks, changed):\n"
            "    affected = set(changed)\n"
            "    changed_work = True\n"
            "    while changed_work:\n"
            "        changed_work = False\n"
            "        for name, deps in tasks.items():\n"
            "            if name in affected:\n"
            "                continue\n"
            "            if any(dep in affected for dep in deps):\n"
            "                affected.add(name)\n"
            "                changed_work = True\n"
            "    return affected\n"
            "\n"
            "\n"
            "print(sorted(impacted(tasks, ['用户表'])))\n"
            "print(sorted(impacted(tasks, ['前端登录页'])))\n"
        ),
        'checks': [
            "r = impacted(tasks, ['用户表'])",
            "assert r == {'用户表', '会话校验', '权限中间件', '订单接口'}, '影响面算错了：%r' % sorted(r)",
            "assert '登录接口' not in r and '前端登录页' not in r, '登录接口不依赖用户表，不该被算作受影响'",
            "assert impacted(tasks, ['订单接口']) == {'订单接口'}, '终端任务不应牵连别人'",
            "assert impacted(tasks, []) == set(), '变更列表为空时不应有任何影响'",
            "assert impacted(tasks, ['不存在的任务']) == {'不存在的任务'}, '未知任务不应报错'",
            "cyclic = {'a': ['b'], 'b': ['a']}",
            "assert impacted(cyclic, ['a']) == {'a', 'b'}, '循环依赖时不能死循环，且两者都算受影响'",
            "assert _out.strip(), '最后应该把结果打印出来（用 sorted 保证顺序稳定）'",
        ],
        'explanation': (
            '这是「图的可达性问题」的最朴素解法——**反复扫直到不再变化**（不动点迭代）。'
            '对几十个任务的小图完全够用，而且比递归更好读、不会栈溢出。\n\n'
            '要点在 `changed_work` 这个标记：只要本轮有新增，就再扫一轮。'
            '循环依赖（a 依赖 b、b 依赖 a）在这个写法下不会死循环，'
            '因为 `if name in affected: continue` 保证了每个任务最多被加入一次。\n\n'
            '如果任务有几千个，就该换成**反向建图 + BFS**：'
            '先建 `dep -> [依赖它的任务]` 的反向索引，再从变更点出发广度优先遍历一次，'
            '复杂度从 O(n²) 降到 O(n + e)。'
            '工业界的依赖影响分析（比如 Maven / npm 的依赖树）用的就是这个思路。\n\n'
            '为什么返回 `set` 而不是 `list`？因为「受影响的任务」本身不关心顺序，'
            '集合天然去重；要展示时再 `sorted()` 一次，顺序就稳定了。'
        ),
        'expected_output': "['会话校验', '权限中间件', '用户表', '订单接口']\n['前端登录页']",
        'hints': ['反复扫描，只要还有新任务被加入就再扫一轮', '循环依赖时靠「已在集合里就跳过」来终止'],
    },

    # ── 第 16 章 设计思维与代码质量 ────────────────────────
    {
        'id': 'ch16-01',
        'chapter_id': 16,
        'title': '重构：把一坨代码拆成小函数',
        'difficulty': 3,
        'tags': ['重构', '函数拆分', '代码质量'],
        'statement': (
            '下面这个函数把「校验、计算、输出」堆在一起，' \
            '它有三个问题：职责不清、没法单测、没法复用。\n\n'
            '```python\n'
            'def process(records):\n'
            '    total = 0\n'
            '    count = 0\n'
            '    for r in records:\n'
            '        if r.get("price") is not None and r.get("qty") is not None:\n'
            '            total += r["price"] * r["qty"]\n'
            '            count += 1\n'
            '    if count == 0:\n'
            '        return "无有效订单"\n'
            '    return f"共 {count} 单，合计 {total:.2f} 元，均价 {total / count:.2f} 元"\n'
            '```\n\n'
            '请把它拆成**四个小函数**（每个都单独可测）：\n\n'
            '1. `parse_record(record)`：把一条原始订单转成 `{"price": 单价, "qty": 数量}`；'
            '缺字段或字段非数字时返回 `None`\n'
            '2. `total_and_count(records)`：返回 `(总金额, 有效单数)`\n'
            '3. `format_summary(total, count)`：返回汇总文案；`count` 为 0 时返回 `"无有效订单"`\n'
            '4. `process(records)`：串起前三步并返回同样的字符串\n\n'
            '要求行为与原函数完全一致（原函数的输出格式不能变）。'
        ),
        'starter_code': 'def parse_record(record):\n    pass\n\n\ndef total_and_count(records):\n    pass\n\n\ndef format_summary(total, count):\n    pass\n\n\ndef process(records):\n    pass\n',
        'solution': (
            "def parse_record(record):\n"
            "    if not isinstance(record, dict):\n"
            "        return None\n"
            "    price, qty = record.get('price'), record.get('qty')\n"
            "    if isinstance(price, bool) or isinstance(qty, bool):\n"
            "        return None\n"
            "    if not isinstance(price, (int, float)) or not isinstance(qty, (int, float)):\n"
            "        return None\n"
            "    return {'price': price, 'qty': qty}\n"
            "\n"
            "\n"
            "def total_and_count(records):\n"
            "    total, count = 0, 0\n"
            "    for record in records:\n"
            "        parsed = parse_record(record)\n"
            "        if parsed is None:\n"
            "            continue\n"
            "        total += parsed['price'] * parsed['qty']\n"
            "        count += 1\n"
            "    return total, count\n"
            "\n"
            "\n"
            "def format_summary(total, count):\n"
            "    if count == 0:\n"
            "        return '无有效订单'\n"
            "    return f'共 {count} 单，合计 {total:.2f} 元，均价 {total / count:.2f} 元'\n"
            "\n"
            "\n"
            "def process(records):\n"
            "    total, count = total_and_count(records)\n"
            "    return format_summary(total, count)\n"
            "\n"
            "\n"
            "data = [\n"
            "    {'price': 10, 'qty': 2},\n"
            "    {'price': 5.5, 'qty': 4},\n"
            "    {'price': None, 'qty': 3},\n"
            "    {'qty': 9},\n"
            "    {'price': 3, 'qty': 1},\n"
            "]\n"
            "print(process(data))\n"
            "print(process([]))\n"
        ),
        'checks': [
            "assert parse_record({'price': 10, 'qty': 2}) == {'price': 10, 'qty': 2}, 'parse_record 正常值应原样返回'",
            "assert parse_record({'price': None, 'qty': 3}) is None, 'price 为 None 应返回 None'",
            "assert parse_record({'qty': 3}) is None, '缺 price 应返回 None'",
            "assert parse_record({'price': '10', 'qty': 2}) is None, 'price 是字符串应返回 None'",
            "assert parse_record(None) is None, '传入非字典应返回 None，不能抛异常'",
            "assert total_and_count([{'price': 10, 'qty': 2}, {'price': 5.5, 'qty': 4}]) == (42.0, 2), 'total_and_count 结果不对'",
            "assert total_and_count([]) == (0, 0), '空输入应返回 (0, 0)'",
            "assert format_summary(0, 0) == '无有效订单', 'count 为 0 时的文案不对'",
            "assert format_summary(42.0, 2) == '共 2 单，合计 42.00 元，均价 21.00 元', '文案格式不对：%r' % format_summary(42.0, 2)",
            "data = [{'price': 10, 'qty': 2}, {'price': 5.5, 'qty': 4}, {'price': None, 'qty': 3}, {'qty': 9}, {'price': 3, 'qty': 1}]",
            "assert process(data) == '共 3 单，合计 45.00 元，均价 15.00 元', 'process 结果与原逻辑不一致：%r' % process(data)",
            "assert process([]) == '无有效订单', '空列表应返回「无有效订单」'",
        ],
        'explanation': (
            '原函数的问题不是「跑不对」，而是**三件事挤在一起**：'
            '数据清洗（判断字段有效）、业务计算（求和计数）、文案格式化。'
            '拆开之后每个函数只做一件事，于是：\n\n'
            '- `parse_record` 可以单独测试各种脏数据；\n'
            '- `format_summary` 改文案时不会碰到计算逻辑；\n'
            '- `total_and_count` 可以被「统计报表」复用，不必复制粘贴。\n\n'
            '这就是所谓「重构不改变行为」——注意 `process` 的输出字符串'
            '和原来**一模一样**，改造期间用同一个输入对比输出，就能确认没改坏。\n\n'
            '顺带修掉了原代码的一个隐患：`r.get("price") is not None` 挡不住字符串 `"10"`，'
            '`"10" * 2` 会得到 `"1010"`（字符串重复！），金额直接算错。'
            '拆出 `parse_record` 后，这里顺手做了 `isinstance` 校验。\n\n'
            '为什么单独判断 `isinstance(price, bool)`？因为 Python 里 `True` 也是数字，'
            '`True * 2` 会得到 2。这种「类型边缘情况」在数据清洗里必须处理。'
        ),
        'expected_output': '共 3 单，合计 45.00 元，均价 15.00 元\n无有效订单',
        'hints': ['每个函数只做一件事，process 只负责串起来', '注意 True 也是 int，数据清洗时要排除布尔值'],
    },
    {
        'id': 'ch16-02',
        'chapter_id': 16,
        'title': '坏味道扫描器：找出超长函数与重复命名',
        'difficulty': 2,
        'tags': ['代码质量', 'AST', '正则'],
        'statement': (
            '定义函数 `find_smells(source)`，分析一段 Python 源码，返回问题清单（字符串列表）。\n\n'
            '用标准库 `ast` 解析源码，检查两条规则：\n\n'
            '1. **超长函数**：函数体语句数超过 8 条 → 报 '
            '`"函数 xxx 有 N 条语句，建议拆分（阈值 8）"`\n'
            '2. **单字母变量**：函数里出现长度为 1 的变量名（`_` 除外）→ 报 '
            '`"函数 xxx 里出现单字母变量 a"`（每个变量名只报一次）\n\n'
            '另外用 `find_duplicates(names)` 找出名字相似度高的重复命名：'
            '输入名字列表，返回**首字母相同且长度差不超过 2** 的名字分组。\n\n'
            '最后对自己写的示例源码跑一遍并打印结果。'
        ),
        'starter_code': 'import ast\n\n\ndef find_smells(source):\n    pass\n\n\ndef find_duplicates(names):\n    pass\n',
        'solution': (
            "import ast\n"
            "\n"
            "\n"
            "def find_smells(source):\n"
            "    smells = []\n"
            "    tree = ast.parse(source)\n"
            "    for node in ast.walk(tree):\n"
            "        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):\n"
            "            continue\n"
            "        body = node.body\n"
            "        # 去掉开头的 docstring 再计数，否则文档写得长会被误判\n"
            "        statements = [s for s in body if not (isinstance(s, ast.Expr)\n"
            "                      and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]\n"
            "        if len(statements) > 8:\n"
            "            smells.append(f'函数 {node.name} 有 {len(statements)} 条语句，建议拆分（阈值 8）')\n"
            "        short = set()\n"
            "        for sub in ast.walk(node):\n"
            "            if isinstance(sub, ast.Name) and len(sub.id) == 1 and sub.id != '_':\n"
            "                short.add(sub.id)\n"
            "            if isinstance(sub, ast.arg) and len(sub.arg) == 1 and sub.arg != '_':\n"
            "                short.add(sub.arg)\n"
            "        for name in sorted(short):\n"
            "            smells.append(f'函数 {node.name} 里出现单字母变量 {name}')\n"
            "    return smells\n"
            "\n"
            "\n"
            "def find_duplicates(names):\n"
            "    groups = []\n"
            "    seen = set()\n"
            "    for i, a in enumerate(names):\n"
            "        group = [a]\n"
            "        for b in names[i + 1:]:\n"
            "            if b in seen:\n"
            "                continue\n"
            "            if a[:1].lower() == b[:1].lower() and abs(len(a) - len(b)) <= 2:\n"
            "                group.append(b)\n"
            "                seen.add(b)\n"
            "        if len(group) > 1:\n"
            "            groups.append(group)\n"
            "    return groups\n"
            "\n"
            "\n"
            "demo = '''\n"
            "def too_long(x):\n"
            "    a = 1\n"
            "    b = a + 1\n"
            "    c = b + 1\n"
            "    d = c + 1\n"
            "    e = d + 1\n"
            "    f = e + 1\n"
            "    g = f + 1\n"
            "    h = g + 1\n"
            "    i = h + 1\n"
            "    return i\n"
            "'''\n"
            "print(find_smells(demo))\n"
            "print(find_duplicates(['user_name', 'user_id', 'order_no', 'total']))\n"
        ),
        'checks': [
            "src_short = 'def ok():\\n    a = 1\\n    return a\\n'",
            "assert find_smells(src_short) == ['函数 ok 里出现单字母变量 a'], '短函数的检查结果不对：%r' % (find_smells(src_short),)",
            "long_src = 'def big(value):\\n' + ''.join('    v%d = %d\\n' % (i, i) for i in range(11)) + '    return value\\n'",
            "long_hits = find_smells(long_src)",
            "assert any(s.startswith('函数 big 有') and '12' in s for s in long_hits), '超过 8 条语句的函数应被报出来：%r' % (long_hits,)",
            "assert not any('v1' in s or 'v2' in s for s in long_hits), 'v1、v2 是多字符变量名，不该被当成单字母：%r' % (long_hits,)",
            "assert long_hits == ['函数 big 有 12 条语句，建议拆分（阈值 8）'], '这条函数里除了超长之外不该有别的问题：%r' % (long_hits,)",
            "clean = 'def tidy(value):\\n    total = value + 1\\n    return total\\n'",
            "assert find_smells(clean) == [], '干净的函数不应报任何问题：%r' % (find_smells(clean),)",
            "doc_src = 'def documented(value):\\n    \"\"\"这是很长的文档\"\"\"\\n    return value\\n'",
            "assert find_smells(doc_src) == [], '函数开头的中文档字符串不应该被算成语句、也不该触发单字母检查：%r' % (find_smells(doc_src),)",
            "assert find_duplicates(['user_name', 'user_id', 'order_no']) == [['user_name', 'user_id']], '重复命名分组不对：%r' % (find_duplicates(['user_name', 'user_id', 'order_no']),)",
            "assert find_duplicates(['a', 'b']) == [], '首字母不同不应分组'",
            "assert find_duplicates([]) == [], '空列表应返回空列表'",
        ],
        'explanation': (
            '用 `ast` 而不是正则来分析代码，是因为**正则会看错**：'
            '字符串里的 `def`、注释里的括号都会骗过正则，而 AST 是解释器自己解析出来的语法树，'
            '结构信息天然准确。这也是 flake8、pylint 这类工具的地基。\n\n'
            '`ast.walk(node)` 会遍历子树里的所有节点，所以内层函数的问题也会被发现。\n'
            '收集单字母变量时用 `set` 再 `sorted`，避免同一个 `a` 出现多次。\n\n'
            '有个容易被忽略的细节：**文档字符串也是 `Expr` 节点**，'
            '如果不排除它，「写了文档」反而会让函数显得更长。'
            '这里的做法是判断「字符串常量表达式」并跳过。\n\n'
            '`find_duplicates` 用的是简单的「首字母 + 长度」启发式。'
            '真实工具会算编辑距离（Levenshtein），但那个算法是 O(n·m)，'
            '对「扫描几百个变量名」这种场景，先用廉价规则筛一遍更实际。\n\n'
            '注意 `find_smells` 会抛 `SyntaxError`——这其实是对的：'
            '语法都不对的代码，先别提风格问题。'
        ),
        'expected_output': "['函数 too_long 有 10 条语句，建议拆分（阈值 8）', '函数 too_long 里出现单字母变量 a', '函数 too_long 里出现单字母变量 b', '函数 too_long 里出现单字母变量 c', '函数 too_long 里出现单字母变量 d', '函数 too_long 里出现单字母变量 e', '函数 too_long 里出现单字母变量 f', '函数 too_long 里出现单字母变量 g', '函数 too_long 里出现单字母变量 h', '函数 too_long 里出现单字母变量 i', '函数 too_long 里出现单字母变量 x']\n[['user_name', 'user_id']]",
        'hints': ['用 ast.parse 拿语法树，ast.walk 遍历所有节点', '函数体里的文档字符串也是语句，要排除掉'],
    },

    # ── 第 17 章 测试：让代码可验证 ────────────────────────
    {
        'id': 'ch17-01',
        'chapter_id': 17,
        'title': '给一个函数补齐边界测试',
        'difficulty': 2,
        'tags': ['测试', '边界值', '断言'],
        'statement': (
            '已有待测函数 `clamp(value, low, high)`：把 value 限制在 `[low, high]` 区间内。\n\n'
            '```python\n'
            'def clamp(value, low, high):\n'
            '    if value < low:\n'
            '        return low\n'
            '    if value > high:\n'
            '        return high\n'
            '    return value\n'
            '```\n\n'
            '要求写一个测试运行器 `run_tests(fn)`，接收被测函数，'
            '返回 `(通过数, 失败信息列表)`，其中每个失败信息形如 '
            '`"用例 3 失败：clamp(10, 20, 5) 期望 20 实际 5"`。\n\n'
            '测试用例必须覆盖（至少 8 条）：\n'
            '- 正常区间内\n- 小于下界\n- 大于上界\n- 正好等于下界 / 上界\n'
            '- 下界等于上界\n- 下界大于上界（**故意的异常输入**）\n- 浮点数\n- 负数\n\n'
            '注意 `clamp(10, 20, 5)` 这个「下界比上界大」的用例，'
            '当前实现返回的是 5，而正确行为应该是**先判断 low > high 就报错**——'
            '所以请先把 `clamp` 按「下界大于上界时抛 ValueError」修好，再让它通过测试。'
        ),
        'starter_code': 'def clamp(value, low, high):\n    if value < low:\n        return low\n    if value > high:\n        return high\n    return value\n\n\ndef run_tests(fn):\n    pass\n',
        'solution': (
            "def clamp(value, low, high):\n"
            "    if low > high:\n"
            "        raise ValueError('下界不能大于上界')\n"
            "    if value < low:\n"
            "        return low\n"
            "    if value > high:\n"
            "        return high\n"
            "    return value\n"
            "\n"
            "\n"
            "CASES = [\n"
            "    ((5, 0, 10), 5),\n"
            "    ((-3, 0, 10), 0),\n"
            "    ((99, 0, 10), 10),\n"
            "    ((0, 0, 10), 0),\n"
            "    ((10, 0, 10), 10),\n"
            "    ((7, 7, 7), 7),\n"
            "    ((2.5, 0.0, 2.0), 2.0),\n"
            "    ((-7, -5, -1), -5),\n"
            "]\n"
            "\n"
            "\n"
            "def run_tests(fn):\n"
            "    passed = 0\n"
            "    failures = []\n"
            "    for index, (args, expected) in enumerate(CASES, 1):\n"
            "        try:\n"
            "            actual = fn(*args)\n"
            "        except Exception as exc:\n"
            "            actual = f'抛异常 {type(exc).__name__}: {exc}'\n"
            "        if actual == expected:\n"
            "            passed += 1\n"
            "        else:\n"
            "            failures.append(f'用例 {index} 失败：clamp{args} 期望 {expected} 实际 {actual}')\n"
            "    return passed, failures\n"
            "\n"
            "\n"
            "ok, bad = run_tests(clamp)\n"
            "print(f'通过 {ok}/{len(CASES)}')\n"
            "for line in bad:\n"
            "    print(line)\n"
            "try:\n"
            "    clamp(10, 20, 5)\n"
            "except ValueError as exc:\n"
            "    print('异常用例：', exc)\n"
        ),
        'checks': [
            "assert clamp(5, 0, 10) == 5, '区间内应原样返回'",
            "assert clamp(-3, 0, 10) == 0, '小于下界应返回下界'",
            "assert clamp(99, 0, 10) == 10, '大于上界应返回上界'",
            "assert clamp(0, 0, 10) == 0 and clamp(10, 0, 10) == 10, '等于边界时应返回边界值'",
            "try:\n    clamp(10, 20, 5)\n    raise AssertionError('下界大于上界时必须抛 ValueError')\nexcept ValueError:\n    pass",
            "passed, failures = run_tests(clamp)",
            "assert isinstance(passed, int) and isinstance(failures, list), 'run_tests 应返回 (通过数, 失败列表)'",
            "assert passed == len(CASES), '修好 clamp 之后所有用例都应通过，实际通过 %d 个：%r' % (passed, failures)",
            "assert failures == [], '不应该有失败用例：%r' % (failures,)",
            "assert len(CASES) >= 8, '测试用例至少 8 条，实际 %d 条' % len(CASES)",
            "assert any(args[1] == args[2] for args, _ in CASES), '用例里要覆盖「下界等于上界」'",
            "assert any(isinstance(a[0], float) for a, _ in CASES), '用例里要覆盖浮点数'",
            "assert any(a[0] < 0 for a, _ in CASES), '用例里要覆盖负数'",
        ],
        'explanation': (
            '这道题真正考的是「**边界值思维**」：程序出错几乎从来不发生在中间值上，'
            '而是发生在等号两边、空值、极值、以及你没想到的非法组合上。\n\n'
            '`clamp(10, 20, 5)` 就是一个典型：下界比上界大。'
            '原实现「碰巧」返回了 5，看起来没崩，但语义是错的——'
            '调用方传反了参数，程序却静默给一个看似合理的结果，'
            '这种 bug 最难查。**主动抛异常比返回一个错误答案好一万倍。**\n\n'
            '`run_tests` 的结构是「用例表 + 循环执行 + 收集失败」，'
            '这是所有测试框架的最小内核：'
            'pytest 无非多做了「自动发现、参数化、夹具、漂亮报告」。\n\n'
            '把每个用例写成 `(参数元组, 期望值)`，好处是**失败信息能自动生成**——'
            '`f"用例 {index} 失败：clamp{args} 期望 {expected} 实际 {actual}"` '
            '里 `clamp{args}` 会把元组渲染成 `clamp(10, 20, 5)`，正好是可复制的调用形式。\n\n'
            '`try/except` 把异常也当成一种「实际结果」来比对，'
            '否则一个用例抛异常会让整个测试运行器崩掉，后面所有用例都跑不到。'
        ),
        'expected_output': '通过 8/8\n异常用例： 下界不能大于上界',
        'hints': ['先把 low > high 的情况用 raise ValueError 拦住', '异常也要被捕获成「实际结果」，否则运行器会中断'],
    },
    {
        'id': 'ch17-02',
        'chapter_id': 17,
        'title': '手写一个极简 pytest：发现并运行测试函数',
        'difficulty': 3,
        'tags': ['测试', '反射', '装饰器'],
        'statement': (
            'pytest 的核心其实很小：**找到 `test_` 开头的函数、跑它、统计结果**。\n\n'
            '要求实现：\n\n'
            '1. `test_case(fn)`：装饰器，给测试函数打标记（`fn._is_test = True`），'
            '并返回原函数\n'
            '2. `collect_tests(namespace)`：从传入的命名空间（字典）里找出所有「测试函数」——'
            '名字以 `test_` 开头、且可调用。返回按名字排序的 `(名字, 函数)` 列表\n'
            '3. `run_all(namespace)`：依次运行收集到的测试，返回 '
            '`{"passed": n, "failed": n, "errors": [ "test_xxx: 报错信息", ... ]}`。'
            '断言失败要记为 failed，其它异常也记为 failed 并记录信息；'
            '函数抛 `AssertionError` 时错误信息里要有「断言失败」字样\n\n'
            '最后写三个测试函数（两通过一失败）验证。'
        ),
        'starter_code': 'def test_case(fn):\n    pass\n\n\ndef collect_tests(namespace):\n    pass\n\n\ndef run_all(namespace):\n    pass\n',
        'solution': (
            "def test_case(fn):\n"
            "    fn._is_test = True\n"
            "    return fn\n"
            "\n"
            "\n"
            "def collect_tests(namespace):\n"
            "    found = []\n"
            "    for name, value in namespace.items():\n"
            "        if name.startswith('test_') and callable(value):\n"
            "            found.append((name, value))\n"
            "    found.sort(key=lambda item: item[0])\n"
            "    return found\n"
            "\n"
            "\n"
            "def run_all(namespace):\n"
            "    passed = failed = 0\n"
            "    errors = []\n"
            "    for name, fn in collect_tests(namespace):\n"
            "        try:\n"
            "            fn()\n"
            "        except AssertionError as exc:\n"
            "            failed += 1\n"
            "            errors.append(f'{name}: 断言失败 {exc}')\n"
            "        except Exception as exc:\n"
            "            failed += 1\n"
            "            errors.append(f'{name}: {type(exc).__name__} {exc}')\n"
            "        else:\n"
            "            passed += 1\n"
            "    return {'passed': passed, 'failed': failed, 'errors': errors}\n"
            "\n"
            "\n"
            "@test_case\n"
            "def test_add():\n"
            "    assert 1 + 1 == 2\n"
            "\n"
            "\n"
            "@test_case\n"
            "def test_upper():\n"
            "    assert 'abc'.upper() == 'ABC'\n"
            "\n"
            "\n"
            "@test_case\n"
            "def test_故意失败():\n"
            "    assert 2 + 2 == 5, '四则运算错了'\n"
            "\n"
            "\n"
            "def helper():\n"
            "    return 1\n"
            "\n"
            "\n"
            # 只看被 @test_case 标记过的函数：装饰器与 collect_tests / run_all
            # 的名字也以 test_ 开头，光看名字会把它们自己收进去。
            "namespace = {k: v for k, v in globals().items() if getattr(v, '_is_test', False)}\n"
            "result = run_all(namespace)\n"
            "print(result)\n"
        ),
        'checks': [
            "def _t_a():\n    assert True",
            "_t_a = test_case(_t_a)",
            "assert getattr(_t_a, '_is_test', False) is True, 'test_case 应该给函数打上 _is_test 标记'",
            "assert _t_a() is None and _t_a.__name__ == '_t_a', 'test_case 必须返回原函数本身，不能包一层 wrapper'",
            "def _t_z():\n    return 1",
            "_t_b = test_case(lambda: None)",
            "ns = {'test_ok': test_case(lambda: None), 'test_bad': test_case(lambda: (_ for _ in ()).throw(AssertionError('故意'))), 'helper': lambda: 1, 'not_test': 5}",
            "names = [n for n, _ in collect_tests(ns)]",
            "assert names == ['test_bad', 'test_ok'], '收集结果应按名字排序且只收 test_ 开头的可调用对象：%r' % (names,)",
            "assert 'helper' not in names and 'not_test' not in names, '不该收集 helper 或非函数的 not_test'",
            "res = run_all(ns)",
            "assert res['passed'] == 1 and res['failed'] == 1, '统计结果不对：%r' % (res,)",
            "assert len(res['errors']) == 1 and res['errors'][0].startswith('test_bad'), '错误信息应以测试名开头：%r' % (res['errors'],)",
            "assert '断言失败' in res['errors'][0], 'AssertionError 的信息里要有「断言失败」字样：%r' % (res['errors'][0],)",
            "ns2 = {'test_boom': test_case(lambda: 1 / 0)}",
            "res2 = run_all(ns2)",
            "assert res2['failed'] == 1 and 'ZeroDivisionError' in res2['errors'][0], '普通异常也要被记为失败并保留异常类型：%r' % (res2,)",
            "assert run_all({}) == {'passed': 0, 'failed': 0, 'errors': []}, '空命名空间应返回全零'",
        ],
        'explanation': (
            '这段代码就是 pytest 的骨架：**约定优于配置**。'
            '不需要注册表、不需要配置文件，只要函数名叫 `test_*` 就自动被发现——'
            '这也是 pytest 比 unittest 好用的地方（后者必须继承 `TestCase` 类）。\n\n'
            '`collect_tests` 遍历的是「命名空间字典」。'
            '在真实 pytest 里这个动作由「导入模块 → 取 `vars(module)`」完成；'
            '本題直接传 `dict(globals())`，效果一样。'
            '注意它**必须返回新列表并排序**：字典顺序虽然现在是有序的，'
            '但显式排序才能保证测试报告每次顺序一致，便于比对。\n\n'
            '`try / except AssertionError / except Exception / else` 的分支顺序很关键：\n'
            '- `AssertionError` 是「测试没过」，属于**预期内的信息**；\n'
            '- 其它异常是「测试代码自己写崩了」，需要保留异常类型；\n'
            '- `else` 分支只在没异常时执行，用它来计 passed 最干净。\n\n'
            '`@test_case` 装饰器只是打个标记，本題里其实不参与筛选'
            '（筛选靠名字前缀），但留着它有两个好处：'
            '一是将来想改成「只跑打了标记的函数」不用改调用方，'
            '二是 IDE 和类型检查器能认出这是测试。'
        ),
        'expected_output': "{'passed': 2, 'failed': 1, 'errors': ['test_故意失败: 断言失败 四则运算错了']}",
        'hints': ['收集时用 name.startswith("test_") 加 callable(value)', 'AssertionError 和普通异常分两个 except 分支处理'],
    },

    # ── 第 18 章 Git 进阶：分支、合并与冲突 ────────────────
    {
        'id': 'ch18-01',
        'chapter_id': 18,
        'title': '解析 git log 输出，找出谁改了什么',
        'difficulty': 2,
        'tags': ['Git', '字符串解析', '数据聚合'],
        'statement': (
            '`git log --pretty=format:"%h|%an|%s"` 的输出长这样：\n\n'
            '```\n'
            'a1b2c3d|小明|feat: 增加登录接口\n'
            'e4f5g6h|小红|fix: 修复订单金额计算\n'
            'i7j8k9l|小明|docs: 更新 README\n'
            'm0n1o2p|小红|feat: 增加导出功能\n'
            'q3r4s5t|小明|fix: 修复登录超时\n'
            '```\n\n'
            '定义函数 `summarize(log_text)`，返回一个统计字典：\n\n'
            '```python\n'
            '{\n'
            '    "total": 5,\n'
            '    "authors": {"小明": 3, "小红": 2},\n'
            '    "types": {"feat": 2, "fix": 2, "docs": 1},\n'
            '    "hotfix_by": ["小明"],   # 提交过 fix 的人，按提交数降序\n'
            '}\n'
            '```\n\n'
            '规则：\n'
            '- 空行要跳过；格式不对的行（少于 3 段）要跳过，不能报错\n'
            '- 提交信息里没有 `类型:` 前缀的，类型记为 `other`\n'
            '- `authors` 里同一个人名要累加\n\n'
            '最后用上面的示例跑一遍并打印。'
        ),
        'starter_code': "log_text = '''a1b2c3d|小明|feat: 增加登录接口\ne4f5g6h|小红|fix: 修复订单金额计算\ni7j8k9l|小明|docs: 更新 README\nm0n1o2p|小红|feat: 增加导出功能\nq3r4s5t|小明|fix: 修复登录超时'''\n\n\ndef summarize(log_text):\n    pass\n",
        'solution': (
            "log_text = '''a1b2c3d|小明|feat: 增加登录接口\n"
            "e4f5g6h|小红|fix: 修复订单金额计算\n"
            "i7j8k9l|小明|docs: 更新 README\n"
            "m0n1o2p|小红|feat: 增加导出功能\n"
            "q3r4s5t|小明|fix: 修复登录超时'''\n"
            "\n"
            "\n"
            "def summarize(log_text):\n"
            "    total = 0\n"
            "    authors = {}\n"
            "    types = {}\n"
            "    fixes = {}\n"
            "    for line in str(log_text).splitlines():\n"
            "        line = line.strip()\n"
            "        if not line:\n"
            "            continue\n"
            "        parts = line.split('|')\n"
            "        if len(parts) < 3:\n"
            "            continue\n"
            "        _, author, message = parts[0], parts[1], '|'.join(parts[2:])\n"
            "        total += 1\n"
            "        authors[author] = authors.get(author, 0) + 1\n"
            "        kind = 'other'\n"
            "        if ':' in message:\n"
            "            head = message.split(':', 1)[0].strip().lower()\n"
            "            if head and ' ' not in head and len(head) <= 10:\n"
            "                kind = head\n"
            "        types[kind] = types.get(kind, 0) + 1\n"
            "        if kind == 'fix':\n"
            "            fixes[author] = fixes.get(author, 0) + 1\n"
            "    hotfix_by = [name for name, _ in sorted(fixes.items(), key=lambda kv: (-kv[1], kv[0]))]\n"
            "    return {'total': total, 'authors': authors, 'types': types, 'hotfix_by': hotfix_by}\n"
            "\n"
            "\n"
            "print(summarize(log_text))\n"
        ),
        'checks': [
            "sample = 'a1b2c3d|小明|feat: 增加登录接口\\ne4f5g6h|小红|fix: 修复订单金额计算\\ni7j8k9l|小明|docs: 更新 README\\nm0n1o2p|小红|feat: 增加导出功能\\nq3r4s5t|小明|fix: 修复登录超时'",
            "r = summarize(sample)",
            "assert r['total'] == 5, 'total 应为 5，实际 %r' % (r['total'],)",
            "assert r['authors'] == {'小明': 3, '小红': 2}, 'authors 统计不对：%r' % (r['authors'],)",
            "assert r['types'] == {'feat': 2, 'fix': 2, 'docs': 1}, 'types 统计不对：%r' % (r['types'],)",
            "assert r['hotfix_by'] == ['小明', '小红'], 'hotfix_by 应包含提交过 fix 的人（小明 2 次在前）：%r' % (r['hotfix_by'],)",
            "messy = 'a1|小明|feat: x\\n\\n坏行\\n\\na2|小红|随手改了一下'",
            "r2 = summarize(messy)",
            "assert r2['total'] == 2, '空行与坏行都要跳过，total 应为 2，实际 %r' % (r2['total'],)",
            "assert r2['types'].get('other') == 1, '没有「类型:」前缀的提交应记为 other：%r' % (r2['types'],)",
            "assert summarize('')['total'] == 0, '空输入应返回 total 0'",
            "assert summarize('')['authors'] == {} and summarize('')['hotfix_by'] == [], '空输入时 authors 应为空字典、hotfix_by 应为空列表'",
        ],
        'explanation': (
            '这段代码的套路是「**逐行解析 → 累加统计 → 排序输出**」，'
            '处理日志、CSV、命令行输出时全是这个骨架。\n\n'
            '三个容易踩的坑：\n\n'
            '1. **分隔符可能出现在内容里**。提交信息里如果有 `|`，'
            '`line.split("|")` 会切出 4 段以上。所以取 `parts[2:]` 再 join 回去，'
            '而不是硬取 `parts[2]`——这样内容里的 `|` 不会丢。\n'
            '2. **脏数据要跳过而不是崩掉**。真实 `git log` 里混着空行、'
            '特殊字符、甚至 windows 的 `\\r`，`splitlines()` 会处理掉 `\\r\\n`，'
            '剩下的靠 `len(parts) < 3` 兜底。\n'
            '3. **类型前缀的识别要收窄**。`"修复了:一个问题"` 这种描述里的冒号'
            '不该被当成类型。这里用「冒号前没有空格且长度 ≤ 10」做了个便宜的收窄，'
            '真实工具（如 commitlint）会用正则 `^([a-z]+)(\\(.+\\))?:` 严格匹配。\n\n'
            '`sorted(fixes.items(), key=lambda kv: (-kv[1], kv[0]))` 又是多级排序：'
            '先按提交次数降序，次数相同时按人名升序，保证输出稳定。\n\n'
            '这套统计在团队里很实用——'
            '`types` 里 `fix` 占比过高通常说明测试覆盖不够，'
            '`authors` 分布过于集中说明知识没有共享。'
        ),
        'expected_output': "{'total': 5, 'authors': {'小明': 3, '小红': 2}, 'types': {'feat': 2, 'fix': 2, 'docs': 1}, 'hotfix_by': ['小明', '小红']}",
        'hints': ['用 line.split("|") 拿三段，注意提交信息本身可能含 |', '类型取冒号前的部分，转小写再判断'],
    },
    {
        'id': 'ch18-02',
        'chapter_id': 18,
        'title': '模拟合并冲突：三方合并算法',
        'difficulty': 3,
        'tags': ['Git', '算法', '三方合并'],
        'statement': (
            'Git 合并两个分支时，其实是在做**三方合并**：'
            '拿「共同祖先 base」当参照，比较两个分支各自的改动。\n\n'
            '规则（按行比较，假设三个版本行数相同）：\n'
            '- 某一行只有一边改了 → 采用改过的那一边\n'
            '- 两边都改了但改得一样 → 采用该值（不算冲突）\n'
            '- 两边都改了且不一样 → 冲突，该行输出 `<<<<<<<` 标记块\n\n'
            '定义函数 `merge_lines(base, ours, theirs)`：\n'
            '- 接收三个等长的字符串列表\n'
            '- 返回 `(merged_lines, conflicts)`：合并结果与冲突行号列表（从 1 开始）\n\n'
            '非冲突行的输出就是选中的那一行原样；'
            '冲突行在 `merged_lines` 里输出三行：\n'
            '`"<<<<<<< ours"`、我们这边的值、`">>>>>>> theirs"`。\n\n'
            '最后用示例数据跑一遍并打印结果。'
        ),
        'starter_code': 'def merge_lines(base, ours, theirs):\n    pass\n',
        'solution': (
            "def merge_lines(base, ours, theirs):\n"
            "    merged = []\n"
            "    conflicts = []\n"
            "    for index, (b, o, t) in enumerate(zip(base, ours, theirs), 1):\n"
            "        if o == t:\n"
            "            merged.append(o)\n"
            "        elif o == b:\n"
            "            merged.append(t)\n"
            "        elif t == b:\n"
            "            merged.append(o)\n"
            "        else:\n"
            "            conflicts.append(index)\n"
            "            merged.append('<<<<<<< ours')\n"
            "            merged.append(o)\n"
            "            merged.append('>>>>>>> theirs')\n"
            "    return merged, conflicts\n"
            "\n"
            "\n"
            "base = ['def add(a, b):', '    return a + b', '', 'print(add(1, 2))']\n"
            "ours = ['def add(a, b):', '    return a * b', '# 我加的注释', 'print(add(1, 2))']\n"
            "theirs = ['def add(a, b):', '    return a + b', '# 他加的注释', 'print(add(1, 2))']\n"
            "merged, conflicts = merge_lines(base, ours, theirs)\n"
            "print(merged)\n"
            "print('冲突行：', conflicts)\n"
        ),
        'checks': [
            "base = ['a', 'b', 'c']",
            "ours = ['a', 'B', 'c']",
            "theirs = ['a', 'b', 'C']",
            "merged, conflicts = merge_lines(base, ours, theirs)",
            "assert merged == ['a', 'B', 'C'], '两边各改一行时应分别采用：%r' % (merged,)",
            "assert conflicts == [], '没有冲突时不应报冲突：%r' % (conflicts,)",
            "m2, c2 = merge_lines(['x'], ['y'], ['z'])",
            "assert c2 == [1], '两边改成不同内容应判定冲突：%r' % (c2,)",
            "assert m2 == ['<<<<<<< ours', 'y', '>>>>>>> theirs'], '冲突行输出格式不对：%r' % (m2,)",
            "m3, c3 = merge_lines(['x'], ['y'], ['y'])",
            "assert m3 == ['y'] and c3 == [], '两边改成一样的内容不算冲突'",
            "m4, c4 = merge_lines(['x', 'y'], ['x', 'y'], ['x', 'z'])",
            "assert m4 == ['x', 'z'] and c4 == [], '只有一边改动的行应采用改动值'",
            "m5, c5 = merge_lines(['same'], ['same'], ['same'])",
            "assert m5 == ['same'] and c5 == [], '三方相同时应原样保留'",
            "assert merge_lines([], [], []) == ([], []), '空输入应返回空结果'",
            "assert '冲突行' in _out, '应该把冲突行号打印出来'",
        ],
        'explanation': (
            '三方合并的判断逻辑其实只有四条，但覆盖了所有情况——'
            '这也是 Git 内部 `merge` 的核心思路（真实实现还会做 diff 对齐，'
            '把「行数不同」的情况规整成 hunk 再按 hunk 合并）。\n\n'
            '判断顺序很重要：\n'
            '1. 先看 `o == t`——两边一致就不用管 base，直接采用；\n'
            '2. 再看 `o == b` 或 `t == b`——说明**只有一边改了**，采用改的那边；\n'
            '3. 剩下的就是两边都改且不同，冲突。\n\n'
            '注意第 3 条不需要再显式判断「两边都改了」：'
            '前两个条件都不成立时，既然 `o != t`，'
            '而 `o != b` 且 `t != b`，那就必然是「都改了且不同」。'
            '**把条件写全反而是冗余，容易写错。**\n\n'
            '冲突标记只输出 `<<<<<<<` 和 `>>>>>>>` 两行，没有 `=======`——'
            '因为本題规定「冲突行只输出我们这边的值」。'
            '真正的 Git 冲突块是 `<<<<<<<` / 我们的内容 / `=======` / 他们的内容 / `>>>>>>>`，'
            '两边内容都留着让人手动选。\n\n'
            '`zip(base, ours, theirs)` 会按最短的截断，'
            '所以本題前提是三个列表等长；'
            '真实场景要先把不同长度的文件对齐（这就是 diff 算法要解决的事）。'
        ),
        'expected_output': "['def add(a, b):', '    return a * b', '<<<<<<< ours', '# 我加的注释', '>>>>>>> theirs', 'print(add(1, 2))']\n冲突行： [3]",
        'hints': ['先判断 o == t，再判断 o == b 或 t == b，剩下的就是冲突', '冲突时要输出三行标记，并记录行号'],
    },

    # ── 第 19 章 Gitee 平台与远程协作 ──────────────────────
    {
        'id': 'ch19-01',
        'chapter_id': 19,
        'title': '远程仓库链接与分支名规范化',
        'difficulty': 2,
        'tags': ['Git', '正则', '规范'],
        'statement': (
            '团队协作要靠约定。请实现两个校验函数：\n\n'
            '1. `parse_remote(url)`：解析远程仓库地址，返回 '
            '`{"host": 域名, "owner": 组织, "repo": 仓库名}`；无法识别时返回 `None`。\n'
            '   要同时支持两种写法：\n'
            '   - `https://gitee.com/pymaster/team-project.git`\n'
            '   - `git@gitee.com:pymaster/team-project.git`（SSH 写法）\n\n'
            '2. `check_branch(name)`：检查分支名是否符合团队规范，返回问题列表（没有则空列表）：\n'
            '   - 只能包含小写字母、数字、`-`、`/` → 否则报 `"只能使用小写字母、数字、- 和 /"`\n'
            '   - 不能以 `-` 或 `/` 开头、不能以 `-` 或 `/` 结尾 → '
            '报 `"不能以 - 或 / 开头或结尾"`\n'
            '   - 不能有连续两个 `-` 或连续斜杠 → 报 `"出现了连续的符号"`\n'
            '   - 分支名总长度不超过 20 → 报 `"分支名过长（上限 20）"`\n\n'
            '最后分别用合法与不合法的例子验证并打印。'
        ),
        'starter_code': 'import re\n\n\ndef parse_remote(url):\n    pass\n\n\ndef check_branch(name):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "\n"
            "def parse_remote(url):\n"
            "    if not isinstance(url, str):\n"
            "        return None\n"
            "    text = url.strip()\n"
            "    if text.endswith('.git'):\n"
            "        text = text[:-4]\n"
            "    match = re.match(r'^https?://(?P<host>[^/]+)/(?P<owner>[^/]+)/(?P<repo>[^/]+)$', text)\n"
            "    if not match:\n"
            "        match = re.match(r'^[\\w.\\-]+@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>[^/]+)$', text)\n"
            "    if not match:\n"
            "        return None\n"
            "    return {'host': match.group('host'), 'owner': match.group('owner'), 'repo': match.group('repo')}\n"
            "\n"
            "\n"
            "def check_branch(name):\n"
            "    problems = []\n"
            "    if not isinstance(name, str) or not name:\n"
            "        return ['分支名不能为空']\n"
            "    if not re.fullmatch(r'[a-z0-9\\-/]+', name):\n"
            "        problems.append('只能使用小写字母、数字、- 和 /')\n"
            "    if name[0] in '-/' or name[-1] in '-/':\n"
            "        problems.append('不能以 - 或 / 开头或结尾')\n"
            "    if '--' in name or '//' in name:\n"
            "        problems.append('出现了连续的符号')\n"
            "    if len(name) > 20:\n"
            "        problems.append('分支名过长（上限 20）')\n"
            "    return problems\n"
            "\n"
            "\n"
            "print(parse_remote('https://gitee.com/pymaster/team-project.git'))\n"
            "print(parse_remote('git@gitee.com:pymaster/team-project.git'))\n"
            "print(parse_remote('随便一段文字'))\n"
            "print(check_branch('feature/login'))\n"
            "print(check_branch('Feature_Login'))\n"
            "print(check_branch('-feature--login-'))\n"
        ),
        'checks': [
            "assert parse_remote('https://gitee.com/pymaster/team-project.git') == {'host': 'gitee.com', 'owner': 'pymaster', 'repo': 'team-project'}, 'HTTPS 地址解析不对：%r' % (parse_remote('https://gitee.com/pymaster/team-project.git'),)",
            "assert parse_remote('git@gitee.com:pymaster/team-project.git') == {'host': 'gitee.com', 'owner': 'pymaster', 'repo': 'team-project'}, 'SSH 地址解析不对：%r' % (parse_remote('git@gitee.com:pymaster/team-project.git'),)",
            "assert parse_remote('https://github.com/org/repo')['repo'] == 'repo', '不带 .git 后缀也要能解析'",
            "assert parse_remote('随便一段文字') is None, '无法识别时应返回 None'",
            "assert parse_remote('') is None and parse_remote(None) is None, '空值应返回 None，不能抛异常'",
            "assert check_branch('feature/login') == [], '合法分支名不应报问题：%r' % (check_branch('feature/login'),)",
            "assert check_branch('dev-1') == [], 'dev-1 是合法分支名'",
            "bad1 = check_branch('Feature_Login')",
            "assert '只能使用小写字母、数字、- 和 /' in bad1, '大写和下划线要被报出来：%r' % (bad1,)",
            "bad2 = check_branch('-feature')",
            "assert '不能以 - 或 / 开头或结尾' in bad2, '以 - 开头要被报出来：%r' % (bad2,)",
            "bad3 = check_branch('feature--login')",
            "assert '出现了连续的符号' in bad3, '连续符号要被报出来：%r' % (bad3,)",
            "bad4 = check_branch('feature/very-long-name-x')",
            "assert '分支名过长（上限 20）' in bad4, '超长分支名要被报出来：%r' % (bad4,)",
            "assert check_branch('feature-') != [], '以 - 结尾要被报出来'",
        ],
        'explanation': (
            '解析远程地址的难点是**同一件事有两种写法**：'
            'HTTPS（`https://host/owner/repo.git`）和 SSH（`git@host:owner/repo.git`）。'
            '它们的区分点是一个 `://` 和一个 `@...:`，所以用两条正则分别匹配，'
            '先试 HTTPS 再试 SSH，都不中就返回 `None`。\n\n'
            '用**命名分组** `(?P<host>...)` 的好处是取值时写 `group("host")` 而不是 `group(1)`，'
            '正则改动后不会因为顺序变化取错值。\n\n'
            '`[^/]+` 这种「非斜杠的任意字符」比 `\\w+` 更宽松，'
            '能兼容带 `.` 或 `-` 的组织名与仓库名。\n\n'
            '校验分支名时，`re.fullmatch` 比 `re.match` 更合适：'
            '`match` 只要求**开头**匹配，所以 `fullmatch(r"[a-z]+", "abc!")` 才为 False，'
            '而 `match` 会因为前三个字符匹配就通过。'
            '**做「整串必须符合」的校验，一定要 `fullmatch` 或用 `^...$`。**\n\n'
            '注意多个问题要**一次性全部返回**，而不是发现一个就 return——'
            '前端要把所有问题一起显示给用户，'
            '一个一个报会让人改四遍。\n\n'
            '这类「规范校验函数」在实际项目里非常常见：'
            'CI 里跑一遍分支名校验，能挡掉一堆因为 `Feature/Login` 这种命名导致的混乱。'
        ),
        'expected_output': "{'host': 'gitee.com', 'owner': 'pymaster', 'repo': 'team-project'}\n{'host': 'gitee.com', 'owner': 'pymaster', 'repo': 'team-project'}\nNone\n[]\n['只能使用小写字母、数字、- 和 /']\n['不能以 - 或 / 开头或结尾', '出现了连续的符号']",
        'hints': ['HTTPS 和 SSH 两种格式各写一条正则，用命名分组取值', '逐项检查并把所有问题都收集起来返回'],
    },

    # ── 第 20 章 团队协作工作流与 Code Review ──────────────
    {
        'id': 'ch20-01',
        'chapter_id': 20,
        'title': 'Code Review 检查清单：自动扫描高危改动',
        'difficulty': 3,
        'tags': ['Code Review', '正则', '安全'],
        'statement': (
            'Review 时最该盯住的是「安全意识」而不是「缩进好不好看」。'
            '请实现 `scan_diff(diff_text)`，对一段 diff（只考虑以 `+` 开头的新增行）'
            '做高危模式扫描，返回问题列表，每条是 '
            '`{"line": 行号, "rule": 规则名, "snippet": 该行内容}`。\n\n'
            '四条规则（命中就报，一条行可以命中多条）：\n\n'
            '1. `hardcoded-secret`：出现 `password` / `secret` / `api_key` / `token` '
            '且后面跟着等号和字符串（例如 `password = "123456"`）\n'
            '2. `sql-concat`：用 `+` 或 f-string 直接拼 SQL，'
            '例如 `"SELECT * FROM t WHERE id = " + uid` 或 `f"DELETE FROM t WHERE id={uid}"`\n'
            '3. `bare-except`：裸的 `except:`（后面没有具体异常类型）\n'
            '4. `print-debug`：新增行里出现 `print(`（提醒别把调试打印提交上来）\n\n'
            '行号用 diff 里的**新文件行号**（即以 `+` 开头的行在最终文件里的位置，'
            '从 1 开始计数，只统计 `+` 行）。\n\n'
            '最后用一段示例 diff 验证并打印结果。'
        ),
        'starter_code': 'import re\n\n\ndef scan_diff(diff_text):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "SECRET_RE = re.compile(r'(password|secret|api_key|token)\\s*=\\s*[\\'\"][^\\'\"]+[\\'\"]', re.I)\n"
            "SQL_RE = re.compile(r'(SELECT|INSERT|UPDATE|DELETE|DROP)\\b', re.I)\n"
            "BARE_EXCEPT_RE = re.compile(r'^\\s*except\\s*:')\n"
            "PRINT_RE = re.compile(r'(^|[^\\w.])print\\s*\\(')\n"
            "\n"
            "\n"
            "def scan_diff(diff_text):\n"
            "    issues = []\n"
            "    new_line = 0\n"
            "    for raw in str(diff_text).splitlines():\n"
            "        if raw.startswith('+++') or raw.startswith('---'):\n"
            "            continue\n"
            "        if raw.startswith('+'):\n"
            "            new_line += 1\n"
            "            content = raw[1:]\n"
            "        elif raw.startswith('-'):\n"
            "            continue\n"
            "        else:\n"
            "            new_line += 1\n"
            "            continue\n"
            "        if SECRET_RE.search(content):\n"
            "            issues.append({'line': new_line, 'rule': 'hardcoded-secret', 'snippet': content.strip()})\n"
            "        if SQL_RE.search(content) and ('+' in content or content.strip().startswith(('f\"', \"f'\"))):\n"
            "            issues.append({'line': new_line, 'rule': 'sql-concat', 'snippet': content.strip()})\n"
            "        if BARE_EXCEPT_RE.search(content):\n"
            "            issues.append({'line': new_line, 'rule': 'bare-except', 'snippet': content.strip()})\n"
            "        if PRINT_RE.search(content):\n"
            "            issues.append({'line': new_line, 'rule': 'print-debug', 'snippet': content.strip()})\n"
            "    return issues\n"
            "\n"
            "\n"
            "diff = '''\n"
            "+def login(user, pwd):\n"
            "+    password = \"123456\"\n"
            "+    query = \"SELECT * FROM users WHERE name = \" + user\n"
            "+    try:\n"
            "+        do_login(query)\n"
            "+    except:\n"
            "+        print(\"登录失败\")\n"
            "+    return True\n"
            "'''\n"
            "for issue in scan_diff(diff):\n"
            "    print(issue)\n"
        ),
        'checks': [
            "diff = '\\n'.join([\n"
            "    '+def login(user):',\n"
            "    '+    password = \"123456\"',\n"
            "    '+    query = \"SELECT * FROM users WHERE name = \" + user',\n"
            "    '+    try:',\n"
            "    '+        do_login(query)',\n"
            "    '+    except:',\n"
            "    '+        print(\"登录失败\")',\n"
            "    '+    return True',\n"
            "])",
            "issues = scan_diff(diff)",
            "rules = [i['rule'] for i in issues]",
            "assert 'hardcoded-secret' in rules, '应检出硬编码密码：%r' % (issues,)",
            "assert 'sql-concat' in rules, '应检出 SQL 拼接：%r' % (issues,)",
            "assert 'bare-except' in rules, '应检出裸 except：%r' % (issues,)",
            "assert 'print-debug' in rules, '应检出调试 print：%r' % (issues,)",
            "secret = next(i for i in issues if i['rule'] == 'hardcoded-secret')",
            "assert secret['line'] == 2, '硬编码密码应报在新文件的第 2 行，实际 %r' % (secret['line'],)",
            "assert '123456' in secret['snippet'], 'snippet 应该是那一行的内容'",
            "clean = '+def add(a, b):\\n+    return a + b'",
            "assert scan_diff(clean) == [], '普通加法代码不该被误报：%r' % (scan_diff(clean),)",
            "sql_without_concat = '+    cursor.execute(\"SELECT * FROM users\")'",
            "assert [i['rule'] for i in scan_diff(sql_without_concat)] == [], '参数化的 SQL 不该被报成拼接'",
            "typed_except = '+    except ValueError:'",
            "assert [i['rule'] for i in scan_diff(typed_except)] == [], '有具体异常类型的 except 不该被报'",
            "named = '+    my_print(x)  # 名字里含 print 但不是调用'",
            "assert [i['rule'] for i in scan_diff(named)] == [], 'my_print 不该被误报成调试打印'",
            "assert scan_diff('') == [], '空 diff 应返回空列表'",
            "assert any(i['rule'] == 'print-debug' for i in scan_diff('+    print(1)')), 'print(1) 应被检出'",
        ],
        'explanation': (
            '这套规则的工程价值在于「**把 Review 里最容易漏的事交给机器**」。'
            '人盯着 300 行 diff 时，最容易被忽略的恰恰是硬编码密钥和裸 `except`——'
            '前者会泄露到线上，后者会把所有异常吞掉，出问题时什么线索都没有。\n\n'
            '四个正则各自的小心思：\n'
            '- **密钥**：要求「等号后面紧跟一个字符串字面量」，'
            '所以 `password = get_from_env()` 不会误报——这是常见的好写法。\n'
            '- **SQL 拼接**：先要求出现 `SELECT/INSERT/...` 关键字，'
            '再要求**同行有 `+` 或 f-string**。'
            '少了第二个条件，`cursor.execute("SELECT ...")` 这种参数化写法会被误伤。\n'
            '- **裸 except**：`^\\s*except\\s*:` 里的 `\\s*:` 要求冒号紧跟其后，'
            '所以 `except ValueError:` 不匹配。\n'
            '- **print**：`(^|[^\\w.])print\\s*\\(` 里的前缀判断，'
            '是为了放过 `my_print(`、`obj.print(` 这类。'
            '正则的 `\\b` 在这里不够用，因为它认为 `_` 是单词字符——'
            '`my_print` 里 `print` 前是 `_`，属于同一单词，`\\b` 不会在那里断开。'
            '换成显式的 `[^\\w.]` 才能正确排除。\n\n'
            '行号统计只数 `+` 行与上下文行，跳过 `-` 行和文件头，'
            '这样报出的行号能直接对上新文件——Review 时点一下就能跳过去。'
        ),
        'expected_output': '{\'line\': 3, \'rule\': \'hardcoded-secret\', \'snippet\': \'password = "123456"\'}\n{\'line\': 4, \'rule\': \'sql-concat\', \'snippet\': \'query = "SELECT * FROM users WHERE name = " + user\'}\n{\'line\': 7, \'rule\': \'bare-except\', \'snippet\': \'except:\'}\n{\'line\': 8, \'rule\': \'print-debug\', \'snippet\': \'print("登录失败")\'}',
        'hints': ['只扫描以 + 开头的行，行号按新文件计数', 'SQL 拼接要同时满足「有 SQL 关键字」和「有 + 或 f-string」两个条件'],
    },
    {
        'id': 'ch20-02',
        'chapter_id': 20,
        'title': '提交信息规范检查（Conventional Commits）',
        'difficulty': 2,
        'tags': ['Git', '正则', '规范'],
        'statement': (
            '团队约定提交信息必须符合 Conventional Commits 格式：\n\n'
            '```\n<类型>(<范围>): <描述>\n```\n\n'
            '- 类型必须是 `feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` 之一\n'
            '- 范围可选，写就放在括号里（如 `feat(login): 增加验证码`）\n'
            '- 冒号后面必须有一个空格\n'
            '- 描述长度 4~50 字\n'
            '- 描述结尾不能是句号\n\n'
            '定义函数 `check_commit(message)`，返回问题列表（合法则空列表），'
            '每条问题用中文描述清楚哪里不对。\n\n'
            '另外定义 `split_commit(message)`：合法时返回 '
            '`{"type":…, "scope":…, "desc":…}`（没有范围时 scope 为 `""`），'
            '不合法时返回 `None`。\n\n'
            '最后用若干例子（含反例）验证并打印。'
        ),
        'starter_code': 'import re\n\nTYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]\n\n\ndef check_commit(message):\n    pass\n\n\ndef split_commit(message):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']\n"
            "PATTERN = re.compile(r'^(?P<type>[a-z]+)(?:\\((?P<scope>[^)]+)\\))?: (?P<desc>.+)$')\n"
            "\n"
            "\n"
            "def check_commit(message):\n"
            "    problems = []\n"
            "    if not isinstance(message, str) or not message.strip():\n"
            "        return ['提交信息不能为空']\n"
            "    text = message.strip()\n"
            "    if len(text.splitlines()) > 1:\n"
            "        problems.append('第一行应该是简短描述，详细说明放到空行之后')\n"
            "        text = text.splitlines()[0]\n"
            "    match = PATTERN.match(text)\n"
            "    if not match:\n"
            "        if ':' not in text:\n"
            "            problems.append('缺少「类型: 描述」的结构')\n"
            "        elif ': ' not in text and ':' in text:\n"
            "            problems.append('冒号后面要有一个空格')\n"
            "        else:\n"
            "            problems.append('格式不符合「类型(范围): 描述」的约定')\n"
            "        return problems\n"
            "    if match.group('type') not in TYPES:\n"
            "        problems.append('类型 ' + match.group('type') + ' 不在允许列表里：' + '/'.join(TYPES))\n"
            "    desc = match.group('desc').strip()\n"
            "    if len(desc) < 4:\n"
            "        problems.append('描述太短（至少要 4 个字）')\n"
            "    if len(desc) > 50:\n"
            "        problems.append('描述太长（最多 50 个字）')\n"
            "    if desc.endswith(('。', '.')):\n"
            "        problems.append('描述结尾不要加句号')\n"
            "    return problems\n"
            "\n"
            "\n"
            "def split_commit(message):\n"
            "    if check_commit(message):\n"
            "        return None\n"
            "    match = PATTERN.match(str(message).strip().splitlines()[0])\n"
            "    return {\n"
            "        'type': match.group('type'),\n"
            "        'scope': match.group('scope') or '',\n"
            "        'desc': match.group('desc').strip(),\n"
            "    }\n"
            "\n"
            "\n"
            "for msg in ['feat(login): 增加验证码校验', 'fix: 修复金额计算错误',\n"
            "            'feat(login):增加验证码', 'update: 改了点东西。', 'fix: 改']:\n"
            "    print(msg, '->', check_commit(msg))\n"
            "print(split_commit('feat(login): 增加验证码校验'))\n"
        ),
        'checks': [
            "assert check_commit('feat(login): 增加验证码校验') == [], '合法信息不该报问题：%r' % (check_commit('feat(login): 增加验证码校验'),)",
            "assert check_commit('fix: 修复金额计算错误') == [], '不带范围的合法信息也不该报问题'",
            "assert check_commit('chore: 升级依赖版本') == [], 'chore 类型应被允许'",
            "assert '不在允许列表里' in ' '.join(check_commit('update: 更新了登录逻辑')), '非法类型要被报出来：%r' % (check_commit('update: 更新了登录逻辑'),)",
            "assert '空格' in ' '.join(check_commit('feat(login):增加验证码校验')), '缺空格要被报出来：%r' % (check_commit('feat(login):增加验证码校验'),)",
            "assert '句号' in ' '.join(check_commit('fix: 修复登录超时问题。')), '结尾句号要被报出来：%r' % (check_commit('fix: 修复登录超时问题。'),)",
            "assert '太短' in ' '.join(check_commit('fix: 改')), '描述过短要被报出来：%r' % (check_commit('fix: 改'),)",
            "assert '太长' in ' '.join(check_commit('fix: ' + '很长的描述' * 12)), '描述过长要被报出来'",
            "assert check_commit('') == ['提交信息不能为空'], '空提交信息应被拦下'",
            "assert '缺少' in ' '.join(check_commit('随便写点什么')), '没有结构的提交信息要报「缺少结构」：%r' % (check_commit('随便写点什么'),)",
            "r = split_commit('feat(login): 增加验证码校验')",
            "assert r == {'type': 'feat', 'scope': 'login', 'desc': '增加验证码校验'}, '解析结果不对：%r' % (r,)",
            "assert split_commit('fix: 修复金额计算错误') == {'type': 'fix', 'scope': '', 'desc': '修复金额计算错误'}, '没有范围时 scope 应为空字符串'",
            "assert split_commit('update: 更新了登录逻辑') is None, '不合法的信息应返回 None'",
        ],
        'explanation': (
            'Conventional Commits 的价值不是「好看」，而是**让机器能读**：'
            '`feat` 和 `fix` 能自动生成 CHANGELOG，'
            '`fix: xxx` 能自动关联 issue，CI 能据此决定要不要发版本。'
            '所以团队里通常会用 commitlint 在 pre-commit 阶段强制检查。\n\n'
            '正则 `^(?P<type>[a-z]+)(?:\\((?P<scope>[^)]+\\))?: (?P<desc>.+)$` 的三个部分：\n'
            '- `(?:\\(...\\))?` 用一个非捕获组 `(?:...)` 加 `?` 让范围**整体可选**；\n'
            '- `[^)]+` 表示范围里不能有右括号，避免 `feat(a)b): x` 这种怪异输入被接受；\n'
            '- `: ` 里那个**空格**就是用来强制「冒号后必须有空格」的——'
            '约束写进正则，比事后单独判断更可靠。\n\n'
            '`check_commit` 对「格式完全不匹配」的情况做了细分：'
            '有冒号但没空格、干脆没冒号、别的格式问题，'
            '给出的提示完全不同。**报错信息要能指出下一步怎么改**，'
            '统一说「格式错误」等于让用户自己猜。\n\n'
            '`split_commit` 直接复用 `check_commit` 做守门，'
            '避免「校验和解析两套逻辑不一致」这种经典 bug——'
            '校验通过了但解析不出来，是最让人困惑的失败方式。'
        ),
        'expected_output': "feat(login): 增加验证码校验 -> []\nfix: 修复金额计算错误 -> []\nfeat(login):增加验证码 -> ['冒号后面要有一个空格']\nupdate: 改了点东西。 -> ['类型 update 不在允许列表里：feat/fix/docs/style/refactor/test/chore', '描述结尾不要加句号']\nfix: 改 -> ['描述太短（至少要 4 个字）']\n{'type': 'feat', 'scope': 'login', 'desc': '增加验证码校验'}",
        'hints': ['范围括号可以用非捕获组加 ? 让其整体可选', '冒号后的空格直接写进正则，就自动强制了'],
    },

    # ── 第 21 章 软件架构基础 ──────────────────────────────
    {
        'id': 'ch21-01',
        'chapter_id': 21,
        'title': '分层架构的依赖方向检查',
        'difficulty': 3,
        'tags': ['架构', '分层', '依赖检查'],
        'statement': (
            '分层架构有条铁律：**依赖只能由外层指向内层**，反过来就是坏味道。\n\n'
            '约定层号（数字越小越靠内）：\n'
            '`1 = domain`（领域模型） / `2 = repository`（数据访问） / '
            '`3 = service`（业务逻辑） / `4 = api`（接口层）\n\n'
            '已知模块清单：\n\n'
            '```python\n'
            "modules = {\n"
            "    'models': 1,\n"
            "    'repositories': 2,\n"
            "    'services': 3,\n"
            "    'controllers': 4,\n"
            "}\n"
            "imports = [('repositories', 'models'), ('services', 'repositories'),\n"
            "           ('services', 'models'), ('controllers', 'services'),\n"
            "           ('models', 'services')]\n"
            '```\n\n'
            '定义函数 `check_layers(modules, imports)`，返回违规的依赖列表，'
            '每条是 `"model -> service（第 1 层依赖第 3 层，方向反了）"` 这样的字符串'
            '（模块名按原样输出，顺序与 imports 中出现的顺序一致）。\n\n'
            '再定义 `topological_order(modules, imports)`：返回一个合法的加载顺序列表，'
            '**被依赖的模块排在前面**（同层内按模块名字母序）；'
            '如果存在循环依赖，返回 `None`。\n\n'
            '⚠️ 注意 `imports` 里的方向是「左边的模块导入了右边的模块」，'
            '所以左边依赖右边，排序时右边应当**排在前面**。'
        ),
        'starter_code': 'modules = {\n    "models": 1,\n    "repositories": 2,\n    "services": 3,\n    "controllers": 4,\n}\nimports = [("repositories", "models"), ("services", "repositories"),\n           ("services", "models"), ("controllers", "services"),\n           ("models", "services")]\n\n\ndef check_layers(modules, imports):\n    pass\n\n\ndef topological_order(modules, imports):\n    pass\n',
        'solution': (
            "modules = {\n"
            "    'models': 1,\n"
            "    'repositories': 2,\n"
            "    'services': 3,\n"
            "    'controllers': 4,\n"
            "}\n"
            "imports = [('repositories', 'models'), ('services', 'repositories'),\n"
            "           ('services', 'models'), ('controllers', 'services'),\n"
            "           ('models', 'services')]\n"
            "\n"
            "\n"
            "def check_layers(modules, imports):\n"
            "    bad = []\n"
            "    for source, target in imports:\n"
            "        a = modules.get(source)\n"
            "        b = modules.get(target)\n"
            "        if a is None or b is None:\n"
            "            continue\n"
            "        if a < b:\n"
            "            bad.append(f'{source} -> {target}（第 {a} 层依赖第 {b} 层，方向反了）')\n"
            "    return bad\n"
            "\n"
            "\n"
            "def topological_order(modules, imports):\n"
            "    deps = {name: set() for name in modules}\n"
            "    for source, target in imports:\n"
            "        if source in deps and target in deps and source != target:\n"
            "            deps[source].add(target)\n"
            "    order = []\n"
            "    remaining = set(deps)\n"
            "    while remaining:\n"
            "        ready = sorted(n for n in remaining if not (deps[n] & remaining))\n"
            "        if not ready:\n"
            "            return None\n"
            "        order.extend(ready)\n"
            "        remaining -= set(ready)\n"
            "    return order\n"
            "\n"
            "\n"
            "print(check_layers(modules, imports))\n"
            "print(topological_order(modules, imports))\n"
        ),
        'checks': [
            "mods = {'models': 1, 'repositories': 2, 'services': 3, 'controllers': 4}",
            "imps = [('repositories', 'models'), ('services', 'repositories'), ('models', 'services')]",
            "bad = check_layers(mods, imps)",
            "assert len(bad) == 1, '只有 models -> services 是反向依赖，实际 %r' % (bad,)",
            "assert bad[0].startswith('models -> services'), '违规描述格式不对：%r' % (bad[0],)",
            "assert '第 1 层' in bad[0] and '第 3 层' in bad[0], '违规描述里要带层号：%r' % (bad[0],)",
            "assert check_layers(mods, [('controllers', 'services')]) == [], '正向依赖不该被报出来'",
            "assert check_layers(mods, [('services', 'services')]) == [], '自己依赖自己（同层）不算反向'",
            "assert check_layers(mods, []) == [], '空依赖应返回空列表'",
            "assert check_layers(mods, [('unknown', 'models')]) == [], '未知模块应跳过而不是报错'",
            "order = topological_order(mods, [('services', 'repositories'), ('repositories', 'models'), ('controllers', 'services')])",
            "assert order.index('models') < order.index('repositories') < order.index('services') < order.index('controllers'), '被依赖的模块必须排在前面：%r' % (order,)",
            "assert topological_order(mods, []) == ['controllers', 'models', 'repositories', 'services'], '没有依赖时按字母序输出：%r' % (topological_order(mods, []),)",
            "cyclic = {'a': 1, 'b': 1}",
            "assert topological_order(cyclic, [('a', 'b'), ('b', 'a')]) is None, '循环依赖必须返回 None（不能死循环）'",
            "assert sorted(order) == ['controllers', 'models', 'repositories', 'services'], '排序结果必须包含所有模块且不重复'",
        ],
        'explanation': (
            '**依赖方向是分层架构唯一不能破的规矩。** 内层（领域模型）不该知道外层的事，'
            '否则改一个 HTTP 参数就可能要动数据库映射层，架构就退化成了一坨。\n\n'
            '`check_layers` 用「层号比较」而不是模块名字符串比较，'
            '好处是加新模块时只需在 `modules` 里补一条。'
            '`a < b` 表示「导入方比被导入方更靠内」，也就是依赖方向反了。'
            '同层之间（`a == b`）允许互相引用，这很常见。\n\n'
            '`topological_order` 用的是 **Kahn 算法**：\n'
            '每轮挑出「所有依赖都已经就位」的模块（`not (deps[n] & remaining)`），'
            '把它们加进结果并从待处理集合里拿掉，'
            '直到没有可放的模块——此时若还有剩余，就说明**存在环**，返回 `None`。\n\n'
            '注意这里的依赖方向：`imports` 里 `("services", "repositories")` 表示 '
            'services 导入 repositories，所以 services **依赖** repositories，'
            '加载时 repositories 必须先就位。'
            '这正是 `deps[source].add(target)` 的含义，也是为什么判断条件是'
            '「自己的依赖不在 remaining 里」。\n\n'
            '`sorted(...)` 保证同层按字母序，输出稳定——'
            '这对「每次构建结果都一样」很重要。'
        ),
        'expected_output': "['models -> services（第 1 层依赖第 3 层，方向反了）']\nNone",
        'hints': ['层号小的模块被层号大的模块依赖是正常的，反过来才违规', '拓扑排序每轮挑「依赖已就绪」的模块，挑不出来说明有环'],
    },

    # ── 第 22 章 前端基础 ─────────────────────────────────
    {
        'id': 'ch22-01',
        'chapter_id': 22,
        'title': 'HTML 转义：防止 XSS 的第一步',
        'difficulty': 1,
        'tags': ['HTML', '安全', '字符串替换'],
        'statement': (
            '用户输入不能直接塞进 HTML——破坏页面结构是小事，'
            '注入脚本（XSS）是大事。\n\n'
            '定义函数 `escape_html(text)`，把五个特殊字符替换成实体：\n\n'
            '| 字符 | 实体 |\n'
            '|---|---|\n'
            '| `&` | `&amp;` |\n'
            '| `<` | `&lt;` |\n'
            '| `>` | `&gt;` |\n'
            '| `"` | `&quot;` |\n'
            '| `\'` | `&#39;` |\n\n'
            '再定义 `render_comment(user, text)`，返回一段 HTML：\n\n'
            '```html\n'
            '<div class="comment"><b>小明</b><p>说点 &lt;script&gt; 之类的</p></div>\n'
            '```\n\n'
            '用户名和内容都要转义。\n\n'
            '⚠️ **替换顺序至关重要**：`&` 必须最先替换，否则后续替换产生的 `&lt;` '
            '会被二次转义成 `&amp;lt;`。'
        ),
        'starter_code': 'def escape_html(text):\n    pass\n\n\ndef render_comment(user, text):\n    pass\n',
        'solution': (
            "def escape_html(text):\n"
            "    result = str(text)\n"
            "    for char, entity in (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'),\n"
            "                         ('\"', '&quot;'), (\"'\", '&#39;')):\n"
            "        result = result.replace(char, entity)\n"
            "    return result\n"
            "\n"
            "\n"
            "def render_comment(user, text):\n"
            "    return f'<div class=\"comment\"><b>{escape_html(user)}</b><p>{escape_html(text)}</p></div>'\n"
            "\n"
            "\n"
            "print(escape_html('<script>alert(1)</script>'))\n"
            "print(escape_html('Tom & Jerry'))\n"
            "print(render_comment('小明', '说点 <script> 之类的'))\n"
        ),
        'checks': [
            "assert escape_html('<b>') == '&lt;b&gt;', '尖括号转义不对：%r' % escape_html('<b>')",
            "assert escape_html('Tom & Jerry') == 'Tom &amp; Jerry', '& 转义不对：%r' % escape_html('Tom & Jerry')",
            "assert escape_html('He said \"hi\"') == 'He said &quot;hi&quot;', '双引号转义不对'",
            "assert escape_html(\"it's\") == 'it&#39;s', '单引号转义不对：%r' % escape_html(\"it's\")",
            "assert escape_html('a & b < c') == 'a &amp; b &lt; c', '混合输入转义不对：%r' % escape_html('a & b < c')",
            "assert escape_html('&lt;') == '&amp;lt;', '已经转义过的文本再转义一次应该变成 &amp;lt;（说明 & 是第一个被替换的）'",
            "assert escape_html('') == '', '空字符串应原样返回'",
            "assert escape_html('普通中文') == '普通中文', '不含特殊字符时不应改变内容'",
            "r = render_comment('小明', '说点 <script> 之类的')",
            "assert r.startswith('<div class=\"comment\"><b>小明</b><p>') and r.endswith('</p></div>'), 'HTML 结构不对：%r' % (r,)",
            "assert '<script>' not in r, '不能把原始 script 标签留在输出里'",
            "assert '&lt;script&gt;' in r, 'script 标签应该被转义成实体'",
            "r2 = render_comment('<img>', '\"><script>alert(1)</script>')",
            "assert r2.count('<script>') == 0 and r2.count('</script>') == 0, 'XSS 载荷必须被完全转义掉：%r' % (r2,)",
            "assert escape_html(None) == 'None', '传入非字符串应该先 str() 再处理，不能崩'",
        ],
        'explanation': (
            '转义的顺序是这道题唯一的知识点，也是唯一容易错的地方。\n\n'
            '如果先替换 `<` 得到 `&lt;`，再替换 `&`，那么 `&lt;` 里的 `&` 会被再次替换，'
            '结果变成 `&amp;lt;`，页面上就会显示成字面量 `&lt;` 而不是 `<`。'
            '所以**必须先把 `&` 处理掉**，后面的替换产物就不会再被影响。\n\n'
            '五个字符里，`&` 和 `<` 是破坏结构的，`>` 是配套的，'
            '`"` 和 `\'` 则是为了防止属性被截断（比如 `value="用户输入"` 里塞进一个引号，'
            '后面就能接上 `onclick=...`）。\n\n'
            '「先转义再拼接」这个原则要贯穿所有模板渲染。'
            '现代前端框架（Vue、React）默认就会转义插值内容，'
            '这也解释了为什么在 Vue 里用 `{{ value }}` 是安全的，'
            '而 `v-html` / `dangerouslySetInnerHTML` 才需要特别小心——'
            '**危险的不是插值，而是「不转义地直接写 HTML」。**\n\n'
            '标准库里其实有现成的：`html.escape(text, quote=True)`。'
            '真实项目优先用它；本題手写一遍是为了搞清楚它到底做了什么。'
        ),
        'expected_output': "&lt;script&gt;alert(1)&lt;/script&gt;\nTom &amp; Jerry\n<div class=\"comment\"><b>小明</b><p>说点 &lt;script&gt; 之类的</p></div>",
        'hints': ['先替换 & ，再替换其他四个', '注意单引号也要转义成 &#39;'],
    },
    {
        'id': 'ch22-02',
        'chapter_id': 22,
        'title': '把数据渲染成 HTML 表格',
        'difficulty': 2,
        'tags': ['HTML', '模板渲染', '列表处理'],
        'statement': (
            '实现一个极简模板函数 `render_table(rows, columns)`：\n\n'
            '- `rows`：字典列表，例如 `[{"name": "小明", "score": 88}, ...]`\n'
            '- `columns`：列定义，每项是 `(字段名, 表头中文名)` 的元组\n\n'
            '输出结构：\n\n'
            '```html\n'
            '<table>\n'
            '  <thead><tr><th>姓名</th><th>分数</th></tr></thead>\n'
            '  <tbody>\n'
            '    <tr><td>小明</td><td>88</td></tr>\n'
            '  </tbody>\n'
            '</table>\n'
            '```\n\n'
            '要求：\n'
            '1. 单元格内容必须**转义**（复用上一题的思路，写个内部 `esc` 函数即可）\n'
            '2. 某行缺少某字段时，该单元格输出空字符串\n'
            '3. 值为 `None` 时也输出空字符串\n'
            '4. `rows` 为空时，输出 `<tbody></tbody>`（不要生成空的白行）\n'
            '5. 缩进用两个空格，行与行之间用 `\\n` 连接\n\n'
            '最后用示例数据打印结果。'
        ),
        'starter_code': 'def render_table(rows, columns):\n    pass\n',
        'solution': (
            "def render_table(rows, columns):\n"
            "    def esc(value):\n"
            "        text = '' if value is None else str(value)\n"
            "        for char, entity in (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'),\n"
            "                             ('\"', '&quot;'), (\"'\", '&#39;')):\n"
            "            text = text.replace(char, entity)\n"
            "        return text\n"
            "\n"
            "    head = '    <tr>' + ''.join(f'<th>{esc(label)}</th>' for _, label in columns) + '</tr>'\n"
            "    body = []\n"
            "    for row in rows:\n"
            "        cells = ''.join(f'<td>{esc(row.get(key))}</td>' for key, _ in columns)\n"
            "        body.append('    <tr>' + cells + '</tr>')\n"
            "    lines = ['<table>', '  <thead>' + head + '</thead>', '  <tbody>']\n"
            "    lines.extend(body)\n"
            "    lines.append('  </tbody>')\n"
            "    lines.append('</table>')\n"
            "    return '\\n'.join(lines)\n"
            "\n"
            "\n"
            "rows = [\n"
            "    {'name': '小明', 'score': 88},\n"
            "    {'name': '小红', 'score': None},\n"
            "    {'name': '<img src=x>'},\n"
            "]\n"
            "print(render_table(rows, [('name', '姓名'), ('score', '分数')]))\n"
            "print(render_table([], [('name', '姓名')]))\n"
        ),
        'checks': [
            "cols = [('name', '姓名'), ('score', '分数')]",
            "html = render_table([{'name': '小明', 'score': 88}], cols)",
            "assert html.startswith('<table>'), '应以 <table> 开头：%r' % html[:40]",
            "assert '<th>姓名</th>' in html and '<th>分数</th>' in html and '</thead>' in html, '表头单元格不对：%r' % html",
            "assert '<tbody>' in html and '</tbody>' in html and '</table>' in html, '缺少 tbody 或闭合标签'",
            "assert '<tr><td>小明</td><td>88</td></tr>' in html, '数据行不对：%r' % html",
            "empty_cell = render_table([{'name': '小红'}], cols)",
            "assert '<td></td>' in empty_cell, '缺字段时应输出空单元格：%r' % empty_cell",
            "none_cell = render_table([{'name': '小红', 'score': None}], cols)",
            "assert '<td>小红</td><td></td>' in none_cell, 'None 也应输出空单元格：%r' % none_cell",
            "assert render_table([], cols).count('<tr>') == 1, '空数据时只应有表头那一行，实际 %d 行' % render_table([], cols).count('<tr>')",
            "assert '<tbody></tbody>' not in render_table([], cols) and '<tbody>' in render_table([], cols), '空数据时 tbody 仍要有配对标签'",
            "xss = render_table([{'name': '<script>x</script>', 'score': 1}], cols)",
            "assert '<script>' not in xss and '&lt;script&gt;' in xss, '单元格内容必须转义：%r' % xss",
            "no_cols = render_table([{'a': 1}], [])",
            "assert '<th></th>' not in no_cols, '没有列定义时不该凭空造表头单元格'",
            "assert render_table([{'name': 'a'}], [('name', '姓名')]).count('\\n') >= 5, '行之间应该用换行连接，便于阅读'",
        ],
        'explanation': (
            '这就是「模板引擎」的最小形态：**遍历数据 → 生成字符串 → 拼接**。'
            'Jinja2、Vue 的编译结果，本质都是把这段逻辑做得更通用、更快。\n\n'
            '`esc` 写在函数内部，是因为它**只服务于这个渲染函数**。'
            'Python 里嵌套函数很轻量（不像类那样要额外开销），'
            '把它藏在里面就不用污染模块命名空间，'
            '而且天然带着「只在这里用」的语义。\n\n'
            '两个细节值得注意：\n'
            '1. `row.get(key)` 而不是 `row[key]`——数据不齐是常态，'
            '缺字段就让单元格空着，比抛 `KeyError` 整个页面 500 要好；\n'
            '2. `"" if value is None else str(value)` 先把 `None` 变成空串，'
            '否则页面上会出现字面量 `None`，用户看了莫名其妙。\n\n'
            '用列表收集行再 `"\\n".join(...)`，比在循环里 `html += ...` 快得多'
            '（字符串不可变，每次 `+=` 都要复制整个字符串）。\n\n'
            '**真实项目里不要手写模板。** 容易漏转义、难维护，'
            '用 Jinja2 这类成熟引擎，它默认自动转义。'
            '本題的价值在于理解「为什么会漏转义」——'
            '比如这里的 `esc` 如果忘了调用，XSS 就进去了。'
        ),
        'expected_output': '<table>\n  <thead>    <tr><th>姓名</th><th>分数</th></tr></thead>\n  <tbody>\n    <tr><td>小明</td><td>88</td></tr>\n    <tr><td>小红</td><td></td></tr>\n    <tr><td>&lt;img src=x&gt;</td><td></td></tr>\n  </tbody>\n</table>\n<table>\n  <thead>    <tr><th>姓名</th></tr></thead>\n  <tbody>\n  </tbody>\n</table>',
        'hints': ['用 row.get(key) 取字段，缺了就得到 None', '先收集所有行到列表，最后用 "\\n".join 拼起来'],
    },

    # ── 第 23 章 后端基础：HTTP、REST 与数据库 ─────────────
    {
        'id': 'ch23-01',
        'chapter_id': 23,
        'title': 'RESTful 路由设计与参数校验',
        'difficulty': 2,
        'tags': ['REST', '路由', '校验'],
        'statement': (
            '后端要能从请求里提取路径参数并校验分页参数。\n\n'
            '1. `match_route(pattern, path)`：把 `/users/<id>/posts` 这类**路由模板**'
            '和真实路径 `/users/42/posts` 比对，匹配则返回参数字典 `{"id": "42"}`，'
            '不匹配返回 `None`。'
            '模板里的 `<名字>` 是占位符；普通段必须完全相等。\n\n'
            '2. `parse_pagination(query)`：`query` 是查询参数字典（值都是字符串），'
            '返回 `(page, size, errors)`：\n'
            '   - `page` 默认 1，`size` 默认 10，都必须是不小于 1 的整数\n'
            '   - `size` 上限 100（超过就报错，**不要静默截断**）\n'
            '   - 非法值放进 `errors` 列表（形如 `"size 必须是正整数"`），'
            '出错时对应字段回落到默认值\n\n'
            '最后用几组正反例验证并打印。'
        ),
        'starter_code': 'def match_route(pattern, path):\n    pass\n\n\ndef parse_pagination(query):\n    pass\n',
        'solution': (
            "def match_route(pattern, path):\n"
            "    pattern_parts = [p for p in str(pattern).strip('/').split('/') if p]\n"
            "    path_parts = [p for p in str(path).strip('/').split('/') if p]\n"
            "    if len(pattern_parts) != len(path_parts):\n"
            "        return None\n"
            "    params = {}\n"
            "    for template, actual in zip(pattern_parts, path_parts):\n"
            "        if template.startswith('<') and template.endswith('>'):\n"
            "            params[template[1:-1]] = actual\n"
            "        elif template != actual:\n"
            "            return None\n"
            "    return params\n"
            "\n"
            "\n"
            "def parse_pagination(query):\n"
            "    errors = []\n"
            "    page, size = 1, 10\n"
            "    raw_page = (query or {}).get('page')\n"
            "    raw_size = (query or {}).get('size')\n"
            "    if raw_page is not None:\n"
            "        try:\n"
            "            page = int(raw_page)\n"
            "            if page < 1:\n"
            "                raise ValueError\n"
            "        except (TypeError, ValueError):\n"
            "            errors.append('page 必须是正整数')\n"
            "            page = 1\n"
            "    if raw_size is not None:\n"
            "        try:\n"
            "            size = int(raw_size)\n"
            "            if size < 1:\n"
            "                raise ValueError\n"
            "            if size > 100:\n"
            "                errors.append('size 不能超过 100')\n"
            "                size = 10\n"
            "        except (TypeError, ValueError):\n"
            "            errors.append('size 必须是正整数')\n"
            "            size = 10\n"
            "    return page, size, errors\n"
            "\n"
            "\n"
            "print(match_route('/users/<id>/posts', '/users/42/posts'))\n"
            "print(match_route('/users/<id>/posts', '/users/42/comments'))\n"
            "print(parse_pagination({'page': '3', 'size': '20'}))\n"
            "print(parse_pagination({'page': '0', 'size': 'abc'}))\n"
            "print(parse_pagination({'size': '500'}))\n"
        ),
        'checks': [
            "assert match_route('/users/<id>/posts', '/users/42/posts') == {'id': '42'}, '基本匹配不对：%r' % (match_route('/users/<id>/posts', '/users/42/posts'),)",
            "assert match_route('/users/<id>/posts', '/users/42/comments') is None, '末段不同应返回 None'",
            "assert match_route('/users/<id>', '/users/42/') == {'id': '42'}, '尾部斜杠不应影响匹配'",
            "assert match_route('/users/<uid>/posts/<pid>', '/users/1/posts/2') == {'uid': '1', 'pid': '2'}, '多参数匹配不对：%r' % (match_route('/users/<uid>/posts/<pid>', '/users/1/posts/2'),)",
            "assert match_route('/users', '/users') == {}, '无参数的静态路由应返回空字典'",
            "assert match_route('/users/<id>', '/users') is None, '段数不同应返回 None'",
            "assert match_route('/users', '/orders') is None, '静态段不同应返回 None'",
            "assert parse_pagination({}) == (1, 10, []), '默认值应为 (1, 10, [])'",
            "assert parse_pagination({'page': '3', 'size': '20'}) == (3, 20, []), '正常参数解析不对'",
            "p, s, errs = parse_pagination({'page': '0'})",
            "assert p == 1 and errs == ['page 必须是正整数'], 'page=0 应报错并回落到 1：%r' % ((p, s, errs),)",
            "p, s, errs = parse_pagination({'size': 'abc'})",
            "assert s == 10 and errs == ['size 必须是正整数'], 'size 非数字应报错并回落到 10：%r' % ((p, s, errs),)",
            "p, s, errs = parse_pagination({'size': '500'})",
            "assert s == 10 and errs == ['size 不能超过 100'], 'size 超上限应报错并回落，不能静默截断：%r' % ((p, s, errs),)",
            "p, s, errs = parse_pagination({'page': 'abc', 'size': '-5'})",
            "assert len(errs) == 2, '两个参数都非法时应报两条错：%r' % (errs,)",
            "assert parse_pagination(None) == (1, 10, []), 'query 为 None 时应返回默认值，不能崩'",
        ],
        'explanation': (
            '`match_route` 就是所有 Web 框架路由匹配的核心思路：'
            '**按 `/` 切开、逐段比较、占位符段存进参数字典**。'
            'Django 的 `<int:pk>`、FastAPI 的 `{user_id}` 都是这个思路加上类型转换。\n\n'
            '两个工程细节：\n'
            '- 用 `strip("/")` 去掉首尾斜杠再做「非空段」过滤，'
            '这样 `/users/42/`、`users/42`、`/users/42` 会被当成同一个路径。'
            '否则用户多打一个斜杠就 404，是最常见的接口「玄学问题」。\n'
            '- 段数不同要**先返回 None**，不要进入循环——'
            '`zip` 会按短的那个截断，``/users/<id>`` 和 ``/users`` 就会「匹配成功」，'
            '这是很隐蔽的 bug。\n\n'
            '`parse_pagination` 的关键决策是「**报错而不是静默截断**」：'
            '`size=500` 时如果悄悄改成 100，调用方以为拿到 500 条数据，'
            '却发现只有 100 条，而且不知道被截断了——'
            '这种 silent truncation 是分页接口最经典的坑。'
            '返回 400 + 明确错误信息，让调用方知道要改请求。\n\n'
            '出错时把字段回落到默认值而不是设为 `None`，'
            '是为了让「有错但也想继续返回数据」的场景能正常工作。\n\n'
            '`int("3.5")` 会抛 `ValueError`，正好被捕获——'
            '所以不需要额外判断小数，' 
            '这也是「用异常做校验」比手写字符判断更省事的地方。'
        ),
        'expected_output': "{'id': '42'}\nNone\n(3, 20, [])\n(1, 10, ['page 必须是正整数', 'size 必须是正整数'])\n(1, 10, ['size 不能超过 100'])",
        'hints': ['路径按 / 切开后先比段数，再逐段比较', 'size 超上限要报错，不要静默改成 100'],
    },
    {
        'id': 'ch23-02',
        'chapter_id': 23,
        'title': '参数化 SQL：把占位符和参数分开',
        'difficulty': 3,
        'tags': ['SQL', '安全', '注入'],
        'statement': (
            'SQL 注入的根源是「把用户输入拼进 SQL 字符串」。'
            '正确做法是**把 SQL 语句和参数分开**交给数据库驱动处理。\n\n'
            '定义函数 `build_query(table, filters, order_by=None, limit=None)`：\n\n'
            '- `table`：表名（必须只含字母、数字、下划线，否则抛 `ValueError("表名不合法")`）\n'
            '- `filters`：字典，形如 `{"age": 18, "city": "杭州", "name": None}`\n'
            '  - 值为 `None` 的键**跳过**（表示「不按这个条件筛」）\n'
            '  - 值为列表/元组时用 `IN`：`{"id": [1, 2, 3]}` → `id IN (?, ?, ?)`\n'
            '  - 其他值用 `=`\n'
            '- `order_by`：形如 `"age"` 或 `"-created_at"`（前缀 `-` 表示降序），'
            '列名同样要校验（只允许字母数字下划线），非法抛 `ValueError("排序字段不合法")`\n'
            '- `limit`：正整数，非法则忽略（不写 LIMIT 子句）\n\n'
            '返回 `(sql, params)`：SQL 里一律用 `?` 占位，参数按顺序放进列表。\n\n'
            '最后用示例验证：**确认生成的 SQL 里绝不出现用户提供的值**。'
        ),
        'starter_code': 'import re\n\n\ndef build_query(table, filters, order_by=None, limit=None):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')\n"
            "\n"
            "\n"
            "def build_query(table, filters, order_by=None, limit=None):\n"
            "    if not IDENT_RE.match(str(table or '')):\n"
            "        raise ValueError('表名不合法')\n"
            "    clauses = []\n"
            "    params = []\n"
            "    for column, value in (filters or {}).items():\n"
            "        if value is None:\n"
            "            continue\n"
            "        if not IDENT_RE.match(str(column)):\n"
            "            raise ValueError('字段名不合法')\n"
            "        if isinstance(value, (list, tuple)):\n"
            "            if not value:\n"
            "                clauses.append(f'{column} IN (NULL)')\n"
            "                continue\n"
            "            placeholders = ', '.join('?' for _ in value)\n"
            "            clauses.append(f'{column} IN ({placeholders})')\n"
            "            params.extend(value)\n"
            "        else:\n"
            "            clauses.append(f'{column} = ?')\n"
            "            params.append(value)\n"
            "    sql = 'SELECT * FROM ' + str(table)\n"
            "    if clauses:\n"
            "        sql += ' WHERE ' + ' AND '.join(clauses)\n"
            "    if order_by:\n"
            "        desc = str(order_by).startswith('-')\n"
            "        column = str(order_by).lstrip('-')\n"
            "        if not IDENT_RE.match(column):\n"
            "            raise ValueError('排序字段不合法')\n"
            "        sql += f' ORDER BY {column} {\"DESC\" if desc else \"ASC\"}'\n"
            "    if isinstance(limit, int) and not isinstance(limit, bool) and limit > 0:\n"
            "        sql += ' LIMIT ?'\n"
            "        params.append(limit)\n"
            "    return sql, params\n"
            "\n"
            "\n"
            "print(build_query('users', {'age': 18, 'city': '杭州', 'name': None}))\n"
            "print(build_query('users', {'id': [1, 2, 3]}, order_by='-created_at', limit=5))\n"
            "try:\n"
            "    build_query('users; DROP TABLE', {'a': 1})\n"
            "except ValueError as exc:\n"
            "    print('拦截：', exc)\n"
        ),
        'checks': [
            "sql, params = build_query('users', {'age': 18, 'city': '杭州'})",
            "assert sql == 'SELECT * FROM users WHERE age = ? AND city = ?', 'SQL 结构不对：%r' % (sql,)",
            "assert params == [18, '杭州'], '参数顺序不对：%r' % (params,)",
            "sql2, params2 = build_query('users', {'age': 18, 'name': None})",
            "assert sql2 == 'SELECT * FROM users WHERE age = ?', 'None 的条件应被跳过：%r' % (sql2,)",
            "assert params2 == [18], '跳过的条件不该进参数列表：%r' % (params2,)",
            "sql3, params3 = build_query('users', {'id': [1, 2, 3]})",
            "assert sql3 == 'SELECT * FROM users WHERE id IN (?, ?, ?)', 'IN 子句占位符不对：%r' % (sql3,)",
            "assert params3 == [1, 2, 3], 'IN 的参数应展开：%r' % (params3,)",
            "sql4, params4 = build_query('users', {}, order_by='-age', limit=5)",
            "assert sql4 == 'SELECT * FROM users ORDER BY age DESC LIMIT ?', '排序与 limit 拼接不对：%r' % (sql4,)",
            "assert params4 == [5], 'limit 也要用占位符：%r' % (params4,)",
            "sql5, _ = build_query('users', {})",
            "assert sql5 == 'SELECT * FROM users', '没有任何条件时不该出现 WHERE：%r' % (sql5,)",
            "inject = \"admin' OR 1=1 --\"",
            "sql6, params6 = build_query('users', {'name': inject})",
            "assert inject not in sql6, '用户输入绝不能出现在 SQL 里：%r' % (sql6,)",
            "assert inject in params6, '用户输入应该作为参数传递：%r' % (params6,)",
            "try:\n    build_query('users; DROP TABLE users', {})\n    raise AssertionError('非法表名必须抛 ValueError')\nexcept ValueError as exc:\n    assert '表名' in str(exc), '异常信息应说明表名不合法'",
            "try:\n    build_query('users', {}, order_by='age; DROP TABLE users')\n    raise AssertionError('非法排序字段必须抛 ValueError')\nexcept ValueError as exc:\n    assert '排序' in str(exc), '异常信息应说明排序字段不合法'",
            "assert build_query('users', {}, limit=-1)[0] == 'SELECT * FROM users', '非法 limit 应被忽略'",
            "assert build_query('users', {}, limit='5')[0] == 'SELECT * FROM users', '字符串 limit 应被忽略而不是拼进 SQL'",
        ],
        'explanation': (
            '这道题的核心只有一句话：**SQL 语句和用户数据必须走两条路**。\n\n'
            'SQL 里写 `?`，把值放进 `params` 列表，'
            '由数据库驱动负责「安全地填入」。'
            '驱动会把值当作**纯数据**处理，'
            '所以 `admin\' OR 1=1 --` 只会被当成一个名字叫这个的用户去查，'
            '不会变成 SQL 语法的一部分。\n\n'
            '但占位符救不了**标识符**（表名、列名）——'
            '`?` 只能替代「值」，不能替代「字段名」。'
            '所以表名、列名必须用**白名单校验**（这里用 `^[A-Za-z_][A-Za-z0-9_]*$`），'
            '这也是本題要显式抛 `ValueError` 的原因。\n'
            '`users; DROP TABLE` 通不过这个正则，注入就被挡在门外。\n\n'
            '几个容易忽略的细节：\n'
            '- `value is None` 时**跳过**条件，而不是写成 `= NULL`——'
            'SQL 里 `= NULL` 永远不成立（要用 `IS NULL`），'
            '写成 `= ?` 传 None 会得到「查不到任何数据」的诡异结果；\n'
            '- 空列表时输出 `IN (NULL)`，表示「不等于任何值」，'
            '比生成 `IN ()`（语法错误）好；\n'
            '- `limit` 只接受真正的整数，字符串 `"5"` 直接忽略——'
            '否则就是给自己开了个拼接后门。\n\n'
            '`isinstance(limit, int) and not isinstance(limit, bool)` '
            '又一次处理了「`True` 是 `int`」这个 Python 特性：'
            '不排除布尔值的话，`limit=True` 会变成 `LIMIT 1`。'
        ),
        'expected_output': "('SELECT * FROM users WHERE age = ? AND city = ?', [18, '杭州'])\n('SELECT * FROM users WHERE id IN (?, ?, ?) ORDER BY created_at DESC LIMIT ?', [1, 2, 3, 5])\n拦截： 表名不合法",
        'hints': ['SQL 里只出现 ? ，值全部进 params 列表', '表名和列名不能用占位符，必须用正则做白名单校验'],
    },

    # ── 第 24 章 FastAPI ──────────────────────────────────
    {
        'id': 'ch24-01',
        'chapter_id': 24,
        'title': '手写一个请求体校验器（Pydantic 的雏形）',
        'difficulty': 3,
        'tags': ['FastAPI', 'Pydantic', '校验'],
        'statement': (
            'FastAPI 用 Pydantic 做请求体校验，出错时返回 422 和一份错误明细。'
            '本題手写这个校验器，理解它到底做了什么。\n\n'
            '给定字段规格：\n\n'
            '```python\n'
            "schema = {\n"
            "    'username': {'type': 'str', 'required': True, 'min_len': 3, 'max_len': 20},\n"
            "    'age': {'type': 'int', 'required': True, 'min': 0, 'max': 150},\n"
            "    'email': {'type': 'str', 'required': False, 'pattern': r'^[^@]+@[^@]+\\.[a-z]{2,}$'},\n"
            "    'tags': {'type': 'list', 'required': False, 'max_items': 5},\n"
            "}\n"
            '```\n\n'
            '定义 `validate_body(data, schema)`，返回 `(cleaned, errors)`：\n\n'
            '- `cleaned`：校验通过的数据（做必要的类型转换，比如整数字符串 `"18"` 转成 `18`）\n'
            '- `errors`：错误列表，每条形如 `{"field": "username", "message": "长度不能少于 3"}`\n'
            '- 缺必需字段 → `"缺少必填字段"`\n'
            '- 类型不对 → `"必须是 str 类型"` / `"必须是 int 类型"` / `"必须是 list 类型"`\n'
            '- 越界 → `"不能小于 0"` / `"不能大于 150"`\n'
            '- 长度不符 → `"长度不能少于 3"` / `"长度不能超过 20"`\n'
            '- 正则不符 → `"格式不正确"`\n'
            '- 列表超长 → `"最多 5 项"`\n'
            '- **校验失败的字段不放进 `cleaned`**，但其余字段照常放进去\n\n'
            '最后用正例和反例各跑一遍并打印。'
        ),
        'starter_code': 'import re\n\nSCHEMA = {\n    "username": {"type": "str", "required": True, "min_len": 3, "max_len": 20},\n    "age": {"type": "int", "required": True, "min": 0, "max": 150},\n    "email": {"type": "str", "required": False, "pattern": r"^[^@]+@[^@]+\\.[a-z]{2,}$"},\n    "tags": {"type": "list", "required": False, "max_items": 5},\n}\n\n\ndef validate_body(data, schema):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "SCHEMA = {\n"
            "    'username': {'type': 'str', 'required': True, 'min_len': 3, 'max_len': 20},\n"
            "    'age': {'type': 'int', 'required': True, 'min': 0, 'max': 150},\n"
            "    'email': {'type': 'str', 'required': False, 'pattern': r'^[^@]+@[^@]+\\.[a-z]{2,}$'},\n"
            "    'tags': {'type': 'list', 'required': False, 'max_items': 5},\n"
            "}\n"
            "\n"
            "\n"
            "def validate_body(data, schema):\n"
            "    cleaned = {}\n"
            "    errors = []\n"
            "    source = data if isinstance(data, dict) else {}\n"
            "    for field, rule in schema.items():\n"
            "        if field not in source or source[field] is None:\n"
            "            if rule.get('required'):\n"
            "                errors.append({'field': field, 'message': '缺少必填字段'})\n"
            "            continue\n"
            "        value = source[field]\n"
            "        kind = rule.get('type')\n"
            "        if kind == 'int' and isinstance(value, str) and value.strip().lstrip('-').isdigit():\n"
            "            value = int(value)\n"
            "        if kind == 'str' and isinstance(value, (int, float)) and not isinstance(value, bool):\n"
            "            value = str(value)\n"
            "        ok = True\n"
            "        if kind == 'int' and (not isinstance(value, int) or isinstance(value, bool)):\n"
            "            errors.append({'field': field, 'message': '必须是 int 类型'})\n"
            "            ok = False\n"
            "        elif kind == 'str' and not isinstance(value, str):\n"
            "            errors.append({'field': field, 'message': '必须是 str 类型'})\n"
            "            ok = False\n"
            "        elif kind == 'list' and not isinstance(value, list):\n"
            "            errors.append({'field': field, 'message': '必须是 list 类型'})\n"
            "            ok = False\n"
            "        if not ok:\n"
            "            continue\n"
            "        if 'min_len' in rule and isinstance(value, str) and len(value) < rule['min_len']:\n"
            "            errors.append({'field': field, 'message': f'长度不能少于 {rule[\"min_len\"]}'})\n"
            "            ok = False\n"
            "        elif 'max_len' in rule and isinstance(value, str) and len(value) > rule['max_len']:\n"
            "            errors.append({'field': field, 'message': f'长度不能超过 {rule[\"max_len\"]}'})\n"
            "            ok = False\n"
            "        if ok and 'min' in rule and isinstance(value, int) and value < rule['min']:\n"
            "            errors.append({'field': field, 'message': f'不能小于 {rule[\"min\"]}'})\n"
            "            ok = False\n"
            "        if ok and 'max' in rule and isinstance(value, int) and value > rule['max']:\n"
            "            errors.append({'field': field, 'message': f'不能大于 {rule[\"max\"]}'})\n"
            "            ok = False\n"
            "        if ok and 'pattern' in rule and isinstance(value, str) and not re.match(rule['pattern'], value):\n"
            "            errors.append({'field': field, 'message': '格式不正确'})\n"
            "            ok = False\n"
            "        if ok and 'max_items' in rule and isinstance(value, list) and len(value) > rule['max_items']:\n"
            "            errors.append({'field': field, 'message': f'最多 {rule[\"max_items\"]} 项'})\n"
            "            ok = False\n"
            "        if ok:\n"
            "            cleaned[field] = value\n"
            "    return cleaned, errors\n"
            "\n"
            "\n"
            "print(validate_body({'username': 'lilei', 'age': '18', 'email': 'a@b.com', 'tags': ['x']}, SCHEMA))\n"
            "print(validate_body({'username': 'ab', 'age': 200}, SCHEMA))\n"
            "print(validate_body({}, SCHEMA))\n"
        ),
        'checks': [
            "clean, errs = validate_body({'username': 'lilei', 'age': '18'}, SCHEMA)",
            "assert errs == [], '合法请求不应有错误：%r' % (errs,)",
            "assert clean == {'username': 'lilei', 'age': 18}, '字符串 \"18\" 应该被转成整数 18：%r' % (clean,)",
            "clean, errs = validate_body({'username': 'lilei'}, SCHEMA)",
            "assert any(e['field'] == 'age' and e['message'] == '缺少必填字段' for e in errs), '缺必填字段要报出来：%r' % (errs,)",
            "clean, errs = validate_body({'username': 'ab', 'age': 18}, SCHEMA)",
            "assert any(e['field'] == 'username' and '长度不能少于 3' == e['message'] for e in errs), '长度不足要报出来：%r' % (errs,)",
            "assert 'username' not in clean and clean.get('age') == 18, '校验失败的字段不放进 cleaned，其余照常：%r' % (clean,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 200}, SCHEMA)",
            "assert any(e['message'] == '不能大于 150' for e in errs), '超上限要报出来：%r' % (errs,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': -1}, SCHEMA)",
            "assert any(e['message'] == '不能小于 0' for e in errs), '小于下限要报出来：%r' % (errs,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 'abc'}, SCHEMA)",
            "assert any(e['field'] == 'age' and e['message'] == '必须是 int 类型' for e in errs), '类型不对要报出来：%r' % (errs,)",
            "clean, errs = validate_body({'username': 123, 'age': 18}, SCHEMA)",
            "assert clean.get('username') == '123', '数字应该被转成字符串：%r' % (clean,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 18, 'email': 'not-an-email'}, SCHEMA)",
            "assert any(e['field'] == 'email' and e['message'] == '格式不正确' for e in errs), '正则不匹配要报出来：%r' % (errs,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 18, 'email': 'a@b.com'}, SCHEMA)",
            "assert 'email' in clean, '合法的可选字段要保留：%r' % (clean,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 18, 'tags': [1, 2, 3, 4, 5, 6]}, SCHEMA)",
            "assert any(e['field'] == 'tags' and e['message'] == '最多 5 项' for e in errs), '列表超长要报出来：%r' % (errs,)",
            "clean, errs = validate_body({}, SCHEMA)",
            "assert len(errs) == 2, 'username 和 age 都必填，应有 2 条错误：%r' % (errs,)",
            "assert clean == {}, '全部失败时 cleaned 应为空字典'",
            "clean, errs = validate_body(None, SCHEMA)",
            "assert len(errs) == 2, 'data 为 None 时应等同于空请求体，不能崩：%r' % (errs,)",
            "clean, errs = validate_body({'username': 'lilei', 'age': 18, 'email': None}, SCHEMA)",
            "assert 'email' not in clean and errs == [], '可选字段传 None 视为未提供，不应报错'",
        ],
        'explanation': (
            'Pydantic 替你做的就这几件事：**看字段在不在 → 看类型对不对 → 看约束满不满足 → 转换**。'
            '看起来简单，但「一次返回所有错误」和「转换与校验的顺序」这两个细节，'
            '决定了它是好用的工具还是折磨人的工具。\n\n'
            '**一次返回全部错误**是关键设计。'
            '如果发现第一个错误就 return，用户就要改一次、提交一次、再改一次，'
            '表单长的时候体验极差。所以这里用 `errors` 列表收集完再一起返回，'
            '而且每条错误都带 `field`，前端能精确标红出错的输入框。\n\n'
            '**转换先于校验**：`"18"` 先转成 `18`，再去做 `min/max` 判断。'
            '反过来写（先判断类型）的话，表单提交上来的数字永远是字符串，'
            '全都会被判「类型不对」。'
            '真实场景里 HTTP 表单和 JSON 的数字类型很不确定，'
            'Pydantic 的「宽松模式」做的就是这种转换。\n\n'
            '**失败字段不进 `cleaned`**：这点容易被忽略。'
            '如果错误字段也放进结果，调用方拿到的就是「半真半假」的数据，'
            '很容易直接写进数据库。宁可让它缺失，逼调用方检查 `errors`。\n\n'
            '布尔值又一次捣乱：`isinstance(value, int)` 对 `True` 成立，'
            '所以 `age=True` 会被当成 1 通过校验。加一层 `isinstance(value, bool)` 排除。\n\n'
            '`ok` 这个标志位让后续检查能「短路」——'
            '类型都不对的时候，就不该再去比较长度。'
            '用 `if ok and ...` 串起来，比层层嵌套 `if` 干净。'
        ),
        'expected_output': "({'username': 'lilei', 'age': 18, 'email': 'a@b.com', 'tags': ['x']}, [])\n({}, [{'field': 'username', 'message': '长度不能少于 3'}, {'field': 'age', 'message': '不能大于 150'}])\n({}, [{'field': 'username', 'message': '缺少必填字段'}, {'field': 'age', 'message': '缺少必填字段'}])",
        'hints': ['先做类型转换再校验约束', '每个字段独立检查，错误全收集完再返回'],
    },
    {
        'id': 'ch24-02',
        'chapter_id': 24,
        'title': '统一响应格式与分页包装',
        'difficulty': 2,
        'tags': ['FastAPI', '响应格式', '分页'],
        'statement': (
            '团队约定所有接口返回统一结构：\n\n'
            '```python\n'
            '{"code": 0, "message": "ok", "data": {...}}\n'
            '```\n\n'
            '定义三个函数：\n\n'
            '1. `ok(data=None, message="ok")`：成功响应，`code` 固定 0\n'
            '2. `fail(message, code=1001, data=None)`：失败响应，`code` 为传入值\n'
            '3. `paginate(items, page=1, size=10)`：把列表切成一页并包成统一结构，'
            '`data` 里包含 `list` / `total` / `page` / `size` / `pages`（总页数，向上取整，'
            '空列表时 `pages` 为 0）。'
            '当 `page` 超过总页数时返回空 `list`，但 `total` 与 `pages` 仍要是真实值。\n\n'
            '另外写一个 `handle(fn)` 风格的辅助函数 `safe_call(fn, *args, **kwargs)`：'
            '捕获被调函数抛出的 `ValueError` 并转成 `fail(...)` 结构，'
            '其他异常转成 `fail("服务器内部错误", code=500)`。\n\n'
            '最后用例子验证并打印。'
        ),
        'starter_code': 'import math\n\n\ndef ok(data=None, message="ok"):\n    pass\n\n\ndef fail(message, code=1001, data=None):\n    pass\n\n\ndef paginate(items, page=1, size=10):\n    pass\n\n\ndef safe_call(fn, *args, **kwargs):\n    pass\n',
        'solution': (
            "import math\n"
            "\n"
            "\n"
            "def ok(data=None, message='ok'):\n"
            "    return {'code': 0, 'message': message, 'data': data}\n"
            "\n"
            "\n"
            "def fail(message, code=1001, data=None):\n"
            "    return {'code': code, 'message': message, 'data': data}\n"
            "\n"
            "\n"
            "def paginate(items, page=1, size=10):\n"
            "    items = list(items or [])\n"
            "    page = max(1, int(page))\n"
            "    size = max(1, int(size))\n"
            "    total = len(items)\n"
            "    pages = math.ceil(total / size) if total else 0\n"
            "    start = (page - 1) * size\n"
            "    return ok({\n"
            "        'list': items[start:start + size],\n"
            "        'total': total,\n"
            "        'page': page,\n"
            "        'size': size,\n"
            "        'pages': pages,\n"
            "    })\n"
            "\n"
            "\n"
            "def safe_call(fn, *args, **kwargs):\n"
            "    try:\n"
            "        return fn(*args, **kwargs)\n"
            "    except ValueError as exc:\n"
            "        return fail(str(exc) or '参数不合法')\n"
            "    except Exception as exc:\n"
            "        print(f'[error] {type(exc).__name__}: {exc}')\n"
            "        return fail('服务器内部错误', code=500)\n"
            "\n"
            "\n"
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        raise ValueError('除数不能为 0')\n"
            "    return ok(a / b)\n"
            "\n"
            "\n"
            "print(paginate(list(range(1, 26)), page=3, size=10))\n"
            "print(paginate([], page=1, size=10))\n"
            "print(safe_call(divide, 6, 2))\n"
            "print(safe_call(divide, 6, 0))\n"
            "print(safe_call(divide, 'x', 2))\n"
        ),
        'checks': [
            "assert ok() == {'code': 0, 'message': 'ok', 'data': None}, 'ok() 默认结构不对：%r' % (ok(),)",
            "assert ok({'a': 1}, '查到了') == {'code': 0, 'message': '查到了', 'data': {'a': 1}}, 'ok 自定义 message 不对'",
            "assert fail('出错了') == {'code': 1001, 'message': '出错了', 'data': None}, 'fail 默认 code 应为 1001：%r' % fail('出错了')",
            "assert fail('无权限', code=403)['code'] == 403, 'fail 的自定义 code 没生效'",
            "r = paginate(list(range(1, 26)), page=3, size=10)",
            "assert r['code'] == 0 and r['data']['total'] == 25, '分页的 total 不对：%r' % (r,)",
            "assert r['data']['list'] == [21, 22, 23, 24, 25], '第 3 页内容不对：%r' % (r['data']['list'],)",
            "assert r['data']['pages'] == 3, '25 条按每页 10 条应是 3 页：%r' % (r['data']['pages'],)",
            "e = paginate([], page=1, size=10)",
            "assert e['data']['total'] == 0 and e['data']['pages'] == 0 and e['data']['list'] == [], '空列表的 pages 应为 0：%r' % (e,)",
            "over = paginate([1, 2, 3], page=99, size=10)",
            "assert over['data']['list'] == [] and over['data']['total'] == 3 and over['data']['pages'] == 1, '翻过页时 list 为空但 total/pages 要真实：%r' % (over,)",
            "assert paginate([1, 2, 3], page=0, size=10)['data']['page'] == 1, 'page 小于 1 时应回落到 1'",
            "assert paginate([1, 2, 3], size=0)['data']['size'] == 1, 'size 小于 1 时应回落到 1'",
            "second = paginate(list(range(10)), page=2, size=4)",
            "assert second['data']['list'] == [4, 5, 6, 7] and second['data']['pages'] == 3, '滑动窗口算错了：%r' % (second['data'],)",
            "r_ok = safe_call(lambda a, b: a + b, 1, 2)",
            "assert r_ok == 3, '正常情况下 safe_call 应原样返回结果：%r' % (r_ok,)",
            "r_val = safe_call(lambda: (_ for _ in ()).throw(ValueError('参数不合法')))",
            "assert r_val == {'code': 1001, 'message': '参数不合法', 'data': None}, 'ValueError 应被转成 fail 结构：%r' % (r_val,)",
            "r_err = safe_call(lambda: 1 / 0)",
            "assert r_err['code'] == 500 and '内部错误' in r_err['message'], '其它异常应转成 500：%r' % (r_err,)",
        ],
        'explanation': (
            '统一响应格式是团队协作的「接口契约」：前端只需要写一次拦截器，'
            '判断 `code === 0` 就放行、否则统一弹错。'
            '如果没有这个约定，每个接口的返回结构都不一样，'
            '前端要为每个接口写一遍判断，后端一改就又得跟着改。\n\n'
            '**`code` 用数字而不是 HTTP 状态码**，'
            '是国内团队很常见的做法（HTTP 一律 200，业务错误放在 body 里）。'
            '好处是能任意扩展业务错误码，'
            '坏处是丢掉了 HTTP 语义（缓存、监控、网关都得靠 body 判断）。'
            '两种都能用，**关键是团队内统一**。\n\n'
            '分页里三个细节值得记：\n'
            '1. `pages` 用 `math.ceil(total / size)`，'
            '空列表时单独返回 0——因为 `ceil(0/10)` 算出来是 0 也对，'
            '但写成 `(total + size - 1) // size` 时 `0 + 9 // 10 = 0` 同样成立，'
            '两种写法都要记住「空数据 pages 是 0」这个语义；\n'
            '2. 「翻过页」时 `list` 为空但 `total`/`pages` 保持真实值——'
            '前端要靠这两个值渲染分页器，返回 0 会让页码消失；\n'
            '3. `items[start:start + size]` 里的切片天然处理越界：'
            '`start` 超过长度时得到空列表，不需要额外判断。\n\n'
            '`safe_call` 把异常翻译成响应，这是「异常边界」的雏形：'
            '真实的 FastAPI 用 `@app.exception_handler` 做同一件事。'
            '注意它把详细异常**打到日志**（`print`）而只给用户返回笼统的「内部错误」——'
            '把 `ZeroDivisionError: division by zero` 直接返回给前端，'
            '既是信息泄露，对用户也毫无用处。'
        ),
        'expected_output': "{'code': 0, 'message': 'ok', 'data': {'list': [21, 22, 23, 24, 25], 'total': 25, 'page': 3, 'size': 10, 'pages': 3}}\n{'code': 0, 'message': 'ok', 'data': {'list': [], 'total': 0, 'page': 1, 'size': 10, 'pages': 0}}\n{'code': 0, 'message': 'ok', 'data': 3.0}\n{'code': 1001, 'message': '除数不能为 0', 'data': None}\n[error] TypeError: unsupported operand type(s) for /: 'str' and 'int'\n{'code': 500, 'message': '服务器内部错误', 'data': None}",
        'hints': ['分页切片用 items[start:start+size]，越界会自动得到空列表', 'ValueError 和普通异常要分开处理，异常详情只打日志不外传'],
    },

    # ── 第 25 章 Vue 入门 ─────────────────────────────────
    {
        'id': 'ch25-01',
        'chapter_id': 25,
        'title': '模拟 Vue 的响应式：算出最小更新集合',
        'difficulty': 3,
        'tags': ['Vue', '响应式', 'diff'],
        'statement': (
            'Vue 的响应式系统靠「依赖收集」：数据变了，只重新渲染用到它的那部分。\n\n'
            '已知模板用到的变量：\n\n'
            '```python\n'
            "watchers = {\n"
            "    'header': ['username', 'avatar'],\n"
            "    'todo-list': ['todos', 'filter'],\n"
            "    'footer': ['count'],\n"
            "    'side-panel': ['todos', 'tags'],\n"
            "}\n"
            '```\n\n'
            '定义函数 `collect_updates(watchers, changed)`：\n'
            '- `changed` 是发生变化的变量名列表\n'
            '- 返回**需要重新渲染的组件名**列表（按字母序），'
            '只要组件依赖的变量里有一个变了，它就要重渲染\n\n'
            '再定义 `diff_state(old, new)`：比较两个状态字典，'
            '返回发生**变化或新增**的键的列表（按字母序）；'
            '值相同（用 `==` 判断）不算变化；被删除的键也算变化，'
            '但要用 `"key:removed"` 这种形式标记？——不，'
            '**删除的键直接以键名形式返回即可**，用第三条规则区分：\n'
            '返回值是 `(changed_keys, removed_keys)` 两个列表。\n\n'
            '最后写一个 `render_log(watchers, old, new)`：'
            '先 `diff_state` 得到变化与删除的键，'
            '再 `collect_updates` 得到要重渲染的组件，'
            '返回一段可读的字符串报告。'
        ),
        'starter_code': "watchers = {\n    'header': ['username', 'avatar'],\n    'todo-list': ['todos', 'filter'],\n    'footer': ['count'],\n    'side-panel': ['todos', 'tags'],\n}\n\n\ndef collect_updates(watchers, changed):\n    pass\n\n\ndef diff_state(old, new):\n    pass\n\n\ndef render_log(watchers, old, new):\n    pass\n",
        'solution': (
            "watchers = {\n"
            "    'header': ['username', 'avatar'],\n"
            "    'todo-list': ['todos', 'filter'],\n"
            "    'footer': ['count'],\n"
            "    'side-panel': ['todos', 'tags'],\n"
            "}\n"
            "\n"
            "\n"
            "def collect_updates(watchers, changed):\n"
            "    changed_set = set(changed or [])\n"
            "    dirty = []\n"
            "    for component, deps in watchers.items():\n"
            "        if changed_set & set(deps):\n"
            "            dirty.append(component)\n"
            "    return sorted(dirty)\n"
            "\n"
            "\n"
            "def diff_state(old, new):\n"
            "    old = old or {}\n"
            "    new = new or {}\n"
            "    changed = [k for k in new if k not in old or old[k] != new[k]]\n"
            "    removed = [k for k in old if k not in new]\n"
            "    return sorted(changed), sorted(removed)\n"
            "\n"
            "\n"
            "def render_log(watchers, old, new):\n"
            "    changed, removed = diff_state(old, new)\n"
            "    dirty = collect_updates(watchers, changed)\n"
            "    lines = [f'变化字段：{changed}', f'删除字段：{removed}',\n"
            "             f'需要重渲染：{dirty}']\n"
            "    return '\\n'.join(lines)\n"
            "\n"
            "\n"
            "old = {'username': '小明', 'todos': [1, 2], 'count': 2, 'tmp': 1}\n"
            "new = {'username': '小明', 'todos': [1, 2, 3], 'count': 2, 'filter': 'all'}\n"
            "print(render_log(watchers, old, new))\n"
        ),
        'checks': [
            "assert collect_updates(watchers, ['count']) == ['footer'], '只有 footer 依赖 count：%r' % (collect_updates(watchers, ['count']),)",
            "assert collect_updates(watchers, ['todos']) == ['side-panel', 'todo-list'], '两个组件依赖 todos，应按字母序返回：%r' % (collect_updates(watchers, ['todos']),)",
            "assert collect_updates(watchers, ['username', 'count']) == ['footer', 'header'], '多变量变化要合并去重并按字母序：%r' % (collect_updates(watchers, ['username', 'count']),)",
            "assert collect_updates(watchers, []) == [], '没有变化时不应有任何组件重渲染'",
            "assert collect_updates(watchers, ['不存在的变量']) == [], '未知变量不应触发渲染'",
            "assert collect_updates({}, ['x']) == [], '没有组件时返回空列表'",
            "assert collect_updates(watchers, ['username', 'username']) == ['header'], '重复的变量名不应导致组件重复出现'",
            "c, r = diff_state({'a': 1, 'b': 2}, {'a': 1, 'b': 3})",
            "assert c == ['b'] and r == [], '只有 b 变了：%r %r' % (c, r)",
            "c2, r2 = diff_state({'a': 1, 'tmp': 5}, {'a': 1, 'b': 2})",
            "assert c2 == ['b'] and r2 == ['tmp'], '新增与删除要分开返回：%r %r' % (c2, r2)",
            "c3, r3 = diff_state({}, {'x': 1})",
            "assert c3 == ['x'] and r3 == [], '空状态下新增的键应算变化：%r' % (c3,)",
            "c4, r4 = diff_state({'x': 1}, {})",
            "assert c4 == [] and r4 == ['x'], '新状态为空时旧的键都算删除：%r' % (r4,)",
            "c5, r5 = diff_state({'a': [1, 2]}, {'a': [1, 2]})",
            "assert c5 == [] and r5 == [], '值相等的列表不应算变化（== 比较内容）'",
            "c6, r6 = diff_state(None, None)",
            "assert c6 == [] and r6 == [], '传 None 应被当作空字典，不能崩'",
            "log = render_log(watchers, {'username': '小明', 'tmp': 1}, {'username': '小明', 'filter': 'all'})",
            "assert '变化字段' in log and '删除字段' in log and '需要重渲染' in log, '报告应包含三个部分：%r' % (log,)",
            "assert 'filter' in log and 'todo-list' in log, 'filter 变化应触发 todo-list 重渲染：%r' % (log,)",
        ],
        'explanation': (
            '这道题把 Vue 响应式系统里最核心的两步抽出来了：'
            '**找出哪些数据变了，再找出谁用到了变的数据**。\n\n'
            '`collect_updates` 用集合交集 `changed_set & set(deps)` 判断「用到没用到」，'
            '这是把 O(n·m) 的双重循环降成 O(n+m) 的常见手法。'
            'Vue 3 内部也是用 `Set` / `Map` 存依赖的——'
            '一个组件可能依赖多个变量，一个变量也可能被多个组件依赖，'
            '所以**依赖关系天然是双向的**，两个方向都要能 O(1) 查到。\n\n'
            '**为什么返回排序后的列表？**'
            '因为渲染顺序要稳定：如果组件顺序随机变化，'
            '页面可能出现「先画 A 再画 B」和「先画 B 再画 A」两种时序，'
            '偶发的视觉闪烁就是这么来的。排序让结果可复现，也方便测试。\n\n'
            '`diff_state` 比较用的是 `==` 而不是 `is`：'
            '`[1, 2] == [1, 2]` 为 True（内容相同），'
            '`[1, 2] is [1, 2]` 为 False（两个不同对象）。'
            '响应式系统要的是「值变了没变」，所以必须用 `==`。\n\n'
            '真正让 Vue 3 比 Vue 2 快的，是它会把「数据变化」**编译期**就关联到具体的 DOM 节点，'
            '本題的「组件级」粒度在 Vue 里已经是比较粗的了（Vue 的粒度是「依赖该变量的渲染函数」）。'
            '但原理一样：**能不动的地方就不动**。'
        ),
        'expected_output': '变化字段：[\'filter\', \'todos\']\n删除字段：[\'tmp\']\n需要重渲染：[\'side-panel\', \'todo-list\']',
        'hints': ['用集合交集判断组件是否依赖变化的变量', '新增和删除要分开返回，值比较用 == 而不是 is'],
    },

    # ── 第 26 章 数据分析与自动化 ──────────────────────────
    {
        'id': 'ch26-01',
        'chapter_id': 26,
        'title': '不用 pandas 做分组统计',
        'difficulty': 2,
        'tags': ['数据分析', '分组统计', '字典'],
        'statement': (
            '搞清楚 pandas 的 `groupby` 到底做了什么，最好的方式是手写一遍。\n\n'
            '给定销售流水：\n\n'
            '```python\n'
            "records = [\n"
            "    {'city': '杭州', 'product': 'A', 'amount': 120},\n"
            "    {'city': '杭州', 'product': 'B', 'amount': 80},\n"
            "    {'city': '上海', 'product': 'A', 'amount': 200},\n"
            "    {'city': '杭州', 'product': 'A', 'amount': 60},\n"
            "    {'city': '上海', 'product': 'B', 'amount': 40},\n"
            "]\n"
            '```\n\n'
            '实现 `group_sum(records, key, value)`：按 `key` 字段分组，'
            '对 `value` 字段求和，返回字典（缺字段的记录跳过，值非数字的也跳过）。\n\n'
            '实现 `group_agg(records, key, value)`：返回 `{分组: {"sum": 合计, '
            '"count": 笔数, "avg": 均值(2位小数), "max": 最大}}` 的嵌套字典。\n\n'
            '实现 `top_groups(records, key, value, n=2)`：按合计**降序**返回前 n 个 '
            '`(分组名, 合计)` 元组；合计相同按分组名字母序。\n\n'
            '最后用示例数据打印三个结果。'
        ),
        'starter_code': "records = [\n    {'city': '杭州', 'product': 'A', 'amount': 120},\n    {'city': '杭州', 'product': 'B', 'amount': 80},\n    {'city': '上海', 'product': 'A', 'amount': 200},\n    {'city': '杭州', 'product': 'A', 'amount': 60},\n    {'city': '上海', 'product': 'B', 'amount': 40},\n]\n\n\ndef group_sum(records, key, value):\n    pass\n",
        'solution': (
            "records = [\n"
            "    {'city': '杭州', 'product': 'A', 'amount': 120},\n"
            "    {'city': '杭州', 'product': 'B', 'amount': 80},\n"
            "    {'city': '上海', 'product': 'A', 'amount': 200},\n"
            "    {'city': '杭州', 'product': 'A', 'amount': 60},\n"
            "    {'city': '上海', 'product': 'B', 'amount': 40},\n"
            "]\n"
            "\n"
            "\n"
            "def group_sum(records, key, value):\n"
            "    totals = {}\n"
            "    for record in records or []:\n"
            "        if not isinstance(record, dict):\n"
            "            continue\n"
            "        name = record.get(key)\n"
            "        amount = record.get(value)\n"
            "        if name is None or isinstance(amount, bool) or not isinstance(amount, (int, float)):\n"
            "            continue\n"
            "        totals[name] = totals.get(name, 0) + amount\n"
            "    return totals\n"
            "\n"
            "\n"
            "def group_agg(records, key, value):\n"
            "    buckets = {}\n"
            "    for record in records or []:\n"
            "        if not isinstance(record, dict):\n"
            "            continue\n"
            "        name = record.get(key)\n"
            "        amount = record.get(value)\n"
            "        if name is None or isinstance(amount, bool) or not isinstance(amount, (int, float)):\n"
            "            continue\n"
            "        bucket = buckets.setdefault(name, {'sum': 0, 'count': 0, 'max': amount})\n"
            "        bucket['sum'] += amount\n"
            "        bucket['count'] += 1\n"
            "        bucket['max'] = max(bucket['max'], amount)\n"
            "    result = {}\n"
            "    for name, bucket in buckets.items():\n"
            "        result[name] = {\n"
            "            'sum': bucket['sum'],\n"
            "            'count': bucket['count'],\n"
            "            'avg': round(bucket['sum'] / bucket['count'], 2),\n"
            "            'max': bucket['max'],\n"
            "        }\n"
            "    return result\n"
            "\n"
            "\n"
            "def top_groups(records, key, value, n=2):\n"
            "    totals = group_sum(records, key, value)\n"
            "    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))\n"
            "    return ranked[:n]\n"
            "\n"
            "\n"
            "print(group_sum(records, 'city', 'amount'))\n"
            "print(group_agg(records, 'city', 'amount'))\n"
            "print(top_groups(records, 'city', 'amount', 2))\n"
        ),
        'checks': [
            "assert group_sum(records, 'city', 'amount') == {'杭州': 260, '上海': 240}, '按城市求和不对：%r' % (group_sum(records, 'city', 'amount'),)",
            "assert group_sum(records, 'product', 'amount') == {'A': 380, 'B': 120}, '按产品求和不对：%r' % (group_sum(records, 'product', 'amount'),)",
            "dirty = records + [{'city': '杭州'}, {'city': '北京', 'amount': 'abc'}, 'not-a-dict']",
            "assert group_sum(dirty, 'city', 'amount') == {'杭州': 260, '上海': 240}, '缺字段/非数字/非字典的记录都要跳过：%r' % (group_sum(dirty, 'city', 'amount'),)",
            "assert group_sum([], 'city', 'amount') == {}, '空列表应返回空字典'",
            "agg = group_agg(records, 'city', 'amount')",
            "assert agg['杭州'] == {'sum': 260, 'count': 3, 'avg': 86.67, 'max': 120}, '杭州的聚合结果不对：%r' % (agg['杭州'],)",
            "assert agg['上海'] == {'sum': 240, 'count': 2, 'avg': 120.0, 'max': 200}, '上海的聚合结果不对：%r' % (agg['上海'],)",
            "assert group_agg([], 'city', 'amount') == {}, '空列表的聚合应返回空字典'",
            "assert top_groups(records, 'city', 'amount', 2) == [('杭州', 260), ('上海', 240)], 'top 排序不对：%r' % (top_groups(records, 'city', 'amount', 2),)",
            "assert top_groups(records, 'city', 'amount', 1) == [('杭州', 260)], '取前 1 个不对'",
            "assert top_groups(records, 'city', 'amount', 99) == [('杭州', 260), ('上海', 240)], 'n 超过分组数时应返回全部，不能报错'",
            "tie = [{'g': 'b', 'v': 5}, {'g': 'a', 'v': 5}]",
            "assert top_groups(tie, 'g', 'v', 2) == [('a', 5), ('b', 5)], '合计相同时应按分组名字母序：%r' % (top_groups(tie, 'g', 'v', 2),)",
            "assert '杭州' in _out and '上海' in _out, '三个结果都应该打印出来'",
        ],
        'explanation': (
            '`groupby` 的本质是「**按某个键把数据分到不同的桶里**」，'
            '这个桶在 Python 里就是字典。手写一遍之后，'
            'pandas 那些 `agg({"amount": ["sum", "mean", "max"]})` 就不再神秘了。\n\n'
            '三个实现细节：\n'
            '1. **脏数据一律跳过而不是报错**。真实数据里什么都有：'
            '空字段、字符串数字、根本不是字典的行。'
            '`if not isinstance(record, dict): continue` 这类防线，'
            '决定了你的脚本是「遇到一行坏数据就崩」还是「跑完并报告」。\n'
            '2. **`isinstance(amount, bool)` 要单独排除**。'
            'Python 里 `True` 是 `int`，如果数据源里混了布尔值'
            '（Excel 里很常见），`sum` 会莫名其妙多出几个 1。\n'
            '3. **`setdefault(name, {...})` 一次到位**，'
            '比「先判断存在不存在，再初始化」少一层缩进。'
            '注意 `max` 的初值直接用第一个数，'
            '不要写 `0`——如果全是负数，`max` 会永远返回 0。\n\n'
            '`top_groups` 又用到了 `key=lambda kv: (-kv[1], kv[0])`：'
            '先按合计降序，合计相同时按名字升序。'
            '没有第二级键的话，输出顺序会依赖字典的插入顺序，'
            '换个数据源顺序就变了，测试根本没法写。\n\n'
            '**什么时候该用 pandas？** 当数据量到几十万行、'
            '或者需要多列聚合、透视、时间窗口时。'
            '几千行以内，纯 Python 字典又快又不用装依赖。'
        ),
        'expected_output': "{'杭州': 260, '上海': 240}\n{'杭州': {'sum': 260, 'count': 3, 'avg': 86.67, 'max': 120}, '上海': {'sum': 240, 'count': 2, 'avg': 120.0, 'max': 200}}\n[('杭州', 260), ('上海', 240)]",
        'hints': ['分组就是「用字典做桶」，setdefault 一次建好桶结构', '求最大值时初值要用第一个数，不要写死 0'],
    },
    {
        'id': 'ch26-02',
        'chapter_id': 26,
        'title': '用 matplotlib 画一张能看的成绩分布图',
        'difficulty': 3,
        'tags': ['matplotlib', '可视化', '统计'],
        'statement': (
            '给定一批成绩，要求画一张分布直方图并保存下来。\n\n'
            '实现 `score_histogram(scores, bins=(0, 60, 70, 80, 90, 101), title="成绩分布")`：\n\n'
            '1. 用 `matplotlib` 画直方图（`hist`），开启网格（`grid(True, alpha=0.3)`）\n'
            '2. 设置标题、X 轴标签 `"分数段"`、Y 轴标签 `"人数"`\n'
            '3. 返回 `(fig, ax, stats)`：\n'
            '   - `fig` / `ax` 是 matplotlib 对象\n'
            '   - `stats` 是各分数段的人数字典，形如 `{"0-60": 2, "60-70": 1, ...}`\n'
            '4. **不要调用 `plt.show()`**（服务端环境没有界面，会卡住）\n\n'
            '分数段的标签规则：最后一档用 `"90+"`，其余用 `"起-止"`（止不含，'
            '即 `[0, 60)` 记为 `"0-60"`）。\n\n'
            '最后用示例成绩跑一遍并打印 `stats`。'
        ),
        'starter_code': 'import matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt\n\n\ndef score_histogram(scores, bins=(0, 60, 70, 80, 90, 101), title="成绩分布"):\n    pass\n',
        'solution': (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "\n"
            "def score_histogram(scores, bins=(0, 60, 70, 80, 90, 101), title='成绩分布'):\n"
            "    data = [s for s in (scores or []) if isinstance(s, (int, float)) and not isinstance(s, bool)]\n"
            "    fig, ax = plt.subplots(figsize=(7, 4))\n"
            "    ax.hist(data, bins=list(bins), color='#4c9ef0', edgecolor='white')\n"
            "    ax.set_title(title)\n"
            "    ax.set_xlabel('分数段')\n"
            "    ax.set_ylabel('人数')\n"
            "    ax.grid(True, alpha=0.3)\n"
            "    stats = {}\n"
            "    for index in range(len(bins) - 1):\n"
            "        low, high = bins[index], bins[index + 1]\n"
            "        label = f'{low}+' if index == len(bins) - 2 else f'{low}-{high}'\n"
            "        count = sum(1 for s in data if low <= s < high)\n"
            "        stats[label] = count\n"
            "    return fig, ax, stats\n"
            "\n"
            "\n"
            "scores = [95, 88, 72, 59, 100, 63, 77, 81, 45, 92, 68, 74, 85, 55, 90]\n"
            "fig, ax, stats = score_histogram(scores)\n"
            "print(stats)\n"
            "print('图数量：', len(plt.get_fignums()))\n"
        ),
        'checks': [
            "scores = [95, 88, 72, 59, 100, 63, 77, 81, 45, 92, 68, 74, 85, 55, 90]",
            "fig, ax, stats = score_histogram(scores)",
            "assert stats == {'0-60': 3, '60-70': 2, '70-80': 3, '80-90': 3, '90+': 4}, '分段统计不对：%r' % (stats,)",
            "assert fig is not None and ax is not None, '要返回 (fig, ax, stats) 三件套'",
            "assert ax.get_title() == '成绩分布', '标题不对：%r' % ax.get_title()",
            "assert ax.get_xlabel() == '分数段' and ax.get_ylabel() == '人数', '坐标轴标签不对'",
            "assert len(plt.get_fignums()) >= 1, '应该真的创建了一张图'",
            "fig2, ax2, stats2 = score_histogram([100], title='单人')",
            "assert stats2 == {'0-60': 0, '60-70': 0, '70-80': 0, '80-90': 0, '90+': 1}, '边界值 100 应落在 90+ 段：%r' % (stats2,)",
            "fig3, ax3, stats3 = score_histogram([60, 70, 90])",
            "assert stats3 == {'0-60': 0, '60-70': 1, '70-80': 1, '80-90': 0, '90+': 1}, '段边界应左闭右开（60 归到 60-70）：%r' % (stats3,)",
            "fig4, ax4, stats4 = score_histogram([], title='空')",
            "assert sum(stats4.values()) == 0, '空数据时各段人数都应为 0，不能报错'",
            "fig5, ax5, stats5 = score_histogram([88, 'abc', None, True])",
            "assert sum(stats5.values()) == 1, '非数字与布尔值都要被过滤掉：%r' % (stats5,)",
            "assert 'plt.show' not in _src, '不要调用 plt.show()，服务端环境会卡住'",
        ],
        'explanation': (
            '服务端画图有两个必须记住的规矩：\n\n'
            '**一是 `matplotlib.use("Agg")`**。默认后端会尝试连接图形界面，'
            '在没有显示器的服务器上就会卡在那里直到超时。'
            'Agg 是纯 CPU 渲染后端，只出图片文件，不弹窗口。\n'
            '（本平台的代码运行沙箱已经统一设了 `MPLBACKEND=Agg` 环境变量，'
            '但自己写脚本时显式声明更保险。）\n\n'
            '**二是绝对不要 `plt.show()`**。它会启动事件循环等待人关窗口，'
            '在服务端就是「永久挂住」。要保存就用 `fig.savefig(path)`。\n\n'
            '`fig, ax = plt.subplots(figsize=(7, 4))` 是**面向对象写法**，'
            '比 `plt.hist(...)` 这种「隐式当前图」的写法好：'
            '所有操作都挂在明确的 `ax` 上，'
            '一个函数里要画多张图、或者要返回图形对象时不会互相串。\n\n'
            '分段统计用手写循环而不是 `ax.hist` 的返回值，'
            '是为了保证语义清晰：`low <= s < high` 是「左闭右开」，'
            '所以 60 分落在 `60-70` 段而不是 `0-60`。'
            '这种边界约定要**先定死再写代码**，'
            '否则统计口径不一致，两个人算出来的分数段人数会不一样。\n\n'
            '`isinstance(s, bool)` 又一次出现——'
            '数据集里混进布尔值时，`True` 会被算成 1 分进入 `0-60` 段，'
            '这种错误在图上完全看不出来。'
        ),
        'expected_output': "{'0-60': 3, '60-70': 2, '70-80': 3, '80-90': 3, '90+': 4}\n图数量： 1",
        'hints': ['用 plt.subplots() 拿到 fig 和 ax，面向对象地画图', '分段统计用 low <= s < high，注意左闭右开'],
    },

    # ── 第 27 章 大模型、API 与智能体概念 ──────────────────
    {
        'id': 'ch27-01',
        'chapter_id': 27,
        'title': '拼装对话消息数组',
        'difficulty': 1,
        'tags': ['大模型', '消息结构', 'API'],
        'statement': (
            '调用大模型接口时，`messages` 数组是有严格结构的：'
            '每条消息有 `role`（`system` / `user` / `assistant`）与 `content`。\n\n'
            '定义函数 `build_messages(system, history, question, max_turns=3)`：\n\n'
            '- 第一条固定是 `{"role": "system", "content": system}`\n'
            '- 接着放入历史对话，但**只保留最近 `max_turns` 轮**'
            '（一轮 = 一条 user + 一条 assistant，按数组顺序成对出现）\n'
            '- 最后追加当前提问 `{"role": "user", "content": question}`\n'
            '- `system` 为空字符串或 `None` 时**不放 system 消息**\n\n'
            '再定义 `count_tokens(messages)` 做粗略的 token 估算：\n'
            '中文字符每个算 1 个 token，英文/数字/标点每 4 个字符算 1 个 token（向上取整），'
            '每条消息额外加 4 个 token 的结构开销。返回总估算值。\n\n'
            '最后用示例验证并打印。'
        ),
        'starter_code': 'def build_messages(system, history, question, max_turns=3):\n    pass\n\n\ndef count_tokens(messages):\n    pass\n',
        'solution': (
            "def build_messages(system, history, question, max_turns=3):\n"
            "    messages = []\n"
            "    if system:\n"
            "        messages.append({'role': 'system', 'content': system})\n"
            "    turns = []\n"
            "    pending_user = None\n"
            "    for item in history or []:\n"
            "        if not isinstance(item, dict):\n"
            "            continue\n"
            "        role = item.get('role')\n"
            "        if role == 'user':\n"
            "            pending_user = item\n"
            "        elif role == 'assistant' and pending_user is not None:\n"
            "            turns.append((pending_user, item))\n"
            "            pending_user = None\n"
            "    for user_item, assistant_item in turns[-max_turns:]:\n"
            "        messages.append({'role': 'user', 'content': user_item.get('content', '')})\n"
            "        messages.append({'role': 'assistant', 'content': assistant_item.get('content', '')})\n"
            "    if question:\n"
            "        messages.append({'role': 'user', 'content': question})\n"
            "    return messages\n"
            "\n"
            "\n"
            "def count_tokens(messages):\n"
            "    total = 0\n"
            "    for message in messages or []:\n"
            "        text = str(message.get('content', ''))\n"
            "        chinese = sum(1 for ch in text if '\\u4e00' <= ch <= '\\u9fff')\n"
            "        other = len(text) - chinese\n"
            "        total += chinese + (other + 3) // 4\n"
            "        total += 4\n"
            "    return total\n"
            "\n"
            "\n"
            "history = [\n"
            "    {'role': 'user', 'content': '什么是列表'},\n"
            "    {'role': 'assistant', 'content': '一种有序容器'},\n"
            "    {'role': 'user', 'content': '那元组呢'},\n"
            "    {'role': 'assistant', 'content': '不可变序列'},\n"
            "    {'role': 'user', 'content': '哪个更快'},\n"
            "    {'role': 'assistant', 'content': '元组略快'},\n"
            "]\n"
            "msgs = build_messages('你是 Python 老师', history, '那字典呢', max_turns=2)\n"
            "for m in msgs:\n"
            "    print(m['role'], m['content'])\n"
            "print('估算 token：', count_tokens(msgs))\n"
        ),
        'checks': [
            "history = [\n    {'role': 'user', 'content': 'Q1'},\n    {'role': 'assistant', 'content': 'A1'},\n    {'role': 'user', 'content': 'Q2'},\n    {'role': 'assistant', 'content': 'A2'},\n    {'role': 'user', 'content': 'Q3'},\n    {'role': 'assistant', 'content': 'A3'},\n]",
            "msgs = build_messages('你是老师', history, 'Q4', max_turns=2)",
            "assert msgs[0] == {'role': 'system', 'content': '你是老师'}, '第一条必须是 system：%r' % (msgs[0],)",
            "assert len(msgs) == 1 + 4 + 1, 'system + 2 轮 + 当前问题 = 6 条，实际 %d 条' % len(msgs)",
            "assert [m['content'] for m in msgs[1:]] == ['Q2', 'A2', 'Q3', 'A3', 'Q4'], '只应保留最近两轮：%r' % ([m['content'] for m in msgs[1:]],)",
            "assert msgs[-1] == {'role': 'user', 'content': 'Q4'}, '最后一条应为当前提问'",
            "no_sys = build_messages('', history, 'Q4', max_turns=1)",
            "assert no_sys[0]['role'] == 'user', 'system 为空时不放 system 消息：%r' % (no_sys[0],)",
            "assert len(no_sys) == 3, '无 system + 1 轮 + 提问 = 3 条：%r' % len(no_sys)",
            "assert build_messages(None, [], 'Q1') == [{'role': 'user', 'content': 'Q1'}], '空历史时只应有当前提问'",
            "odd = [{'role': 'assistant', 'content': '没人问的回复'}, {'role': 'user', 'content': 'Q1'}]",
            "assert [m['content'] for m in build_messages(None, odd, 'Q2')] == ['Q2'], '不成对的历史不应被当成完整的一轮'",
            "assert build_messages('S', [], '') == [{'role': 'system', 'content': 'S'}], '问题为空且无历史时，只应留下 system 消息'",
            "assert count_tokens([]) == 0, '空消息列表的 token 应为 0'",
            "one = count_tokens([{'role': 'user', 'content': '你好'}])",
            "assert one == 2 + 4, '两个中文 + 4 结构开销 = 6，实际 %r' % (one,)",
            "eight = count_tokens([{'role': 'user', 'content': 'abcdefgh'}])",
            "assert eight == 2 + 4, '8 个英文字符 = 2 token，加 4 = 6，实际 %r' % (eight,)",
            "two = count_tokens([{'role': 'user', 'content': 'ab'}])",
            "assert two == 1 + 4, '2 个英文字符向上取整为 1 token：%r' % (two,)",
        ],
        'explanation': (
            '多轮对话的关键是「**历史要成对传**」。'
            '大模型是无状态的——它不记得上一轮说了什么，'
            '你每次都得把历史重新发过去。'
            '如果 user 和 assistant 不成对（比如只发了两个 user），'
            '很多服务商会直接报错，或者给出奇怪的回复。\n\n'
            '所以 `build_messages` 用一个 `pending_user` 暂存，'
            '**只有遇到 assistant 才配成一轮**。'
            '这样即使历史里出现「连续两条 user」「孤立的 assistant」，'
            '也不会拼出非法的消息序列。'
            '真实项目里这种脏数据太常见了（用户狂点发送、前面某次请求失败了）。\n\n'
            '`turns[-max_turns:]` 只截最近的几轮，是为了**控制上下文长度**。'
            '完整历史会越来越长，最终超出模型窗口——'
            '表现就是请求报错，或者模型开始「忘记」最近的对话。'
            '生产环境的做法更精细：按 token 数倒着删，'
            '或者把早期对话**摘要**成一段话再放进去。\n\n'
            '`count_tokens` 是**估算**：真实的分词器（BPE）不是这么算的，'
            '中文通常 1 个字 ≈ 1~2 个 token，英文平均 4 个字符 ≈ 1 个 token。'
            '但估算够用了——你要的是「大概还剩多少额度」，不是精确值。'
            '`(other + 3) // 4` 是向上取整的整数写法，'
            '比 `math.ceil(other / 4)` 更快也不会引入浮点误差。\n\n'
            '判断中文用 `"\\u4e00" <= ch <= "\\u9fff"` 是 Unicode 码点比较，'
            '覆盖了常用汉字区。要更全面可以用 `unicodedata.name()`，'
            '但那是几十倍的开销，不值得。'
        ),
        'expected_output': 'system 你是 Python 老师\nuser 那元组呢\nassistant 不可变序列\nuser 哪个更快\nassistant 元组略快\nuser 那字典呢\n估算 token： 51',
        'hints': ['历史要 user 和 assistant 成对才算一轮，用暂存变量配对', '取最近 max_turns 轮就是 turns[-max_turns:]'],
    },
    {
        'id': 'ch27-02',
        'chapter_id': 27,
        'title': '给智能体装工具：函数注册表',
        'difficulty': 2,
        'tags': ['智能体', '装饰器', '工具调用'],
        'statement': (
            '智能体能「动手」，靠的是**工具注册表**：'
            '把函数注册成工具，模型选中后按名字调用。\n\n'
            '实现一个极简工具系统：\n\n'
            '1. `tool(name, description)`：装饰器工厂，把函数注册进全局注册表，'
            '记录它的名字、描述、参数名列表（用 `inspect.signature` 取）\n'
            '2. `list_tools()`：返回工具清单，每项是 '
            '`{"name":…, "description":…, "params": [...]}`，按名字排序\n'
            '3. `call_tool(name, **kwargs)`：按名字调用工具，返回结果；'
            '工具不存在时返回 `{"error": "未知工具 xxx"}`；'
            '参数不对（缺参数或有未定义参数）时返回 '
            '`{"error": "参数不匹配：…"}`，**不要抛出异常**\n\n'
            '要求：`call_tool` 遇到工具内部自己抛的异常时，'
            '也要转成 `{"error": "执行失败：…"}` 返回（智能体不能因为一个工具报错就整体崩掉）。\n\n'
            '最后注册两个工具（如 `get_weather(city)`、`add(a, b)`）验证并打印。'
        ),
        'starter_code': 'import inspect\n\n_REGISTRY = {}\n\n\ndef tool(name, description):\n    pass\n\n\ndef list_tools():\n    pass\n\n\ndef call_tool(name, **kwargs):\n    pass\n',
        'solution': (
            "import inspect\n"
            "\n"
            "_REGISTRY = {}\n"
            "\n"
            "\n"
            "def tool(name, description):\n"
            "    def decorator(func):\n"
            "        params = list(inspect.signature(func).parameters.keys())\n"
            "        _REGISTRY[name] = {'name': name, 'description': description,\n"
            "                           'params': params, 'func': func}\n"
            "        func._tool_name = name\n"
            "        return func\n"
            "    return decorator\n"
            "\n"
            "\n"
            "def list_tools():\n"
            "    return [{'name': entry['name'], 'description': entry['description'],\n"
            "             'params': entry['params']} for _, entry in sorted(_REGISTRY.items())]\n"
            "\n"
            "\n"
            "def call_tool(name, **kwargs):\n"
            "    entry = _REGISTRY.get(name)\n"
            "    if entry is None:\n"
            "        return {'error': f'未知工具 {name}'}\n"
            "    expected = set(entry['params'])\n"
            "    given = set(kwargs)\n"
            "    missing = expected - given\n"
            "    unexpected = given - expected\n"
            "    if missing or unexpected:\n"
            "        parts = []\n"
            "        if missing:\n"
            "            parts.append('缺少参数 ' + ', '.join(sorted(missing)))\n"
            "        if unexpected:\n"
            "            parts.append('多余参数 ' + ', '.join(sorted(unexpected)))\n"
            "        return {'error': '参数不匹配：' + '；'.join(parts)}\n"
            "    try:\n"
            "        return entry['func'](**kwargs)\n"
            "    except Exception as exc:\n"
            "        return {'error': f'执行失败：{type(exc).__name__} {exc}'}\n"
            "\n"
            "\n"
            "@tool('get_weather', '查询某个城市的天气')\n"
            "def get_weather(city):\n"
            "    data = {'杭州': '晴 26℃', '上海': '多云 24℃'}\n"
            "    if city not in data:\n"
            "        raise KeyError(f'没有 {city} 的天气数据')\n"
            "    return {'city': city, 'weather': data[city]}\n"
            "\n"
            "\n"
            "@tool('add', '把两个数字相加')\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "\n"
            "for item in list_tools():\n"
            "    print(item)\n"
            "print(call_tool('get_weather', city='杭州'))\n"
            "print(call_tool('add', a=1, b=2))\n"
            "print(call_tool('get_weather'))\n"
            "print(call_tool('nope'))\n"
            "print(call_tool('get_weather', city='火星'))\n"
        ),
        'checks': [
            "@tool('t_echo', '原样返回输入')",
            "def t_echo(text):",
            "    return text",
            "assert t_echo('hi') == 'hi', '装饰器必须返回原函数，不能包一层'",
            "names = [t['name'] for t in list_tools()]",
            "assert 't_echo' in names, 'list_tools 应包含刚注册的工具：%r' % (names,)",
            "assert names == sorted(names), '工具清单应按名字排序：%r' % (names,)",
            "entry = next(t for t in list_tools() if t['name'] == 't_echo')",
            "assert entry['description'] == '原样返回输入', '描述没记录对：%r' % (entry,)",
            "assert entry['params'] == ['text'], '参数名列表不对：%r' % (entry['params'],)",
            "@tool('t_boom', '总是抛异常')",
            "def t_boom():",
            "    raise ValueError('炸了')",
            "assert call_tool('t_echo', text='ok') == 'ok', '正常调用应直接返回结果'",
            "unknown = call_tool('not_exists')",
            "assert isinstance(unknown, dict) and '未知工具' in unknown['error'], '未知工具应返回错误字典：%r' % (unknown,)",
            "missing = call_tool('t_echo')",
            "assert '参数不匹配' in missing['error'] and '缺少参数' in missing['error'], '缺参数要报出来：%r' % (missing,)",
            "extra = call_tool('t_echo', text='a', wrong=1)",
            "assert '参数不匹配' in extra['error'] and '多余参数' in extra['error'], '多余参数要报出来：%r' % (extra,)",
            "boom = call_tool('t_boom')",
            "assert '执行失败' in boom['error'] and 'ValueError' in boom['error'], '工具内部异常要被兜住并保留异常类型：%r' % (boom,)",
            "assert 't_boom' in [t['name'] for t in list_tools()], '注册表应持续累积工具'",
            "assert call_tool('t_echo', text='x') == 'x', '一次失败不应影响后续调用'",
        ],
        'explanation': (
            '智能体的「工具」和普通函数的区别，就在于**多了一层描述与调度**：'
            '模型看到的不是代码，而是这样一段 JSON：',
            '```json\n',
            '{"name": "get_weather", "description": "查询某个城市的天气", "params": ["city"]}\n',
            '```\n\n',
            '模型决定「要调这个工具、参数是 city=杭州」，'
            '再由你的代码去真正执行。'
            '所以**描述写得好不好，直接决定模型选不选得对**——'
            '`"查询某个城市的天气"` 比 `"天气"` 有用得多。\n\n'
            '用 `inspect.signature` 自动提取参数名，比手写参数列表可靠：'
            '函数改签名时注册信息自动跟着变，不会出现「文档说一个参数、代码要两个」。\n\n'
            '**`call_tool` 绝不能抛异常**，这是整个设计的关键。'
            '模型经常会给出各种奇怪的参数组合，'
            '如果每次都抛异常，你的 Agent 主循环每次都要写 try/except，'
            '漏一处整个对话就崩了。'
            '把「参数错误」「工具内部错误」都变成结构化的 `{"error": ...}` 返回，'
            '模型拿到这个错误信息后**还能自己纠正**（比如换成正确的参数重试）——'
            '这是 Agent 自我修复的基础。\n\n'
            '注意错误信息里保留了异常类型（`ValueError ...`）：'
            '对模型来说，`执行失败：KeyError 「没有 火星 的天气数据」` '
            '比笼统的「执行失败」更有指导性，它可能据此换个城市再试。\n\n'
            '装饰器工厂的三层结构（`tool(...)` → `decorator(func)` → 返回 func）'
            '和前面 `@retry(times=3)` 是同一个模式：'
            '最外层收配置，内层收函数。'
        ),
        'expected_output': '{\'name\': \'add\', \'description\': \'把两个数字相加\', \'params\': [\'a\', \'b\']}\n{\'name\': \'get_weather\', \'description\': \'查询某个城市的天气\', \'params\': [\'city\']}\n{\'city\': \'杭州\', \'weather\': \'晴 26℃\'}\n3\n{\'error\': \'参数不匹配：缺少参数 city\'}\n{\'error\': \'未知工具 nope\'}\n{\'error\': "执行失败：KeyError \'没有 火星 的天气数据\'"}',
        'hints': ['用 inspect.signature(func).parameters 取参数名', 'call_tool 里先检查参数，再 try/except 包住真正的调用'],
    },

    # ── 第 28 章 DeepSeek API 实战 ────────────────────────
    {
        'id': 'ch28-01',
        'chapter_id': 28,
        'title': '组装请求体与解析响应',
        'difficulty': 2,
        'tags': ['API', 'JSON', '错误处理'],
        'statement': (
            '调用大模型 HTTP 接口分三步：**组装请求体 → 发送 → 解析响应**。'
            '本題不真的发请求，只写前两步与第三步。\n\n'
            '1. `build_payload(model, messages, temperature=0.7, max_tokens=800, stream=False)`：\n'
            '   返回请求体字典，并做参数校验：\n'
            '   - `temperature` 必须在 `0 ~ 2` 之间，超出抛 `ValueError("temperature 必须在 0~2 之间")`\n'
            '   - `max_tokens` 必须是正整数，否则抛 `ValueError("max_tokens 必须是正整数")`\n'
            '   - `messages` 为空或不是列表时抛 `ValueError("messages 不能为空")`\n'
            '   - 最终返回的字典包含 `model` / `messages` / `temperature` / `max_tokens` / `stream`\n\n'
            '2. `parse_response(data)`：解析响应体：\n'
            '   - 正常：返回 `{"ok": True, "content": 正文, "model": 模型名, '
            '"tokens": 总 token 数（取不到就 0）}`\n'
            '   - 结构不对（没有 `choices` 或为空）：返回 `{"ok": False, "error": "响应结构异常"}`\n\n'
            '3. `describe_error(status, body)`：把 HTTP 错误翻译成人话：\n'
            '   - `401` → `"API Key 不正确或已失效"`\n'
            '   - `403` → `"没有权限或账号欠费"`\n'
            '   - `404` → `"模型名称或接口地址不对"`\n'
            '   - `429` → `"请求太频繁或额度用尽，请稍后重试"`\n'
            '   - `5xx` → `"服务端异常，请稍后重试"`\n'
            '   - 其他 → 附上状态码与 `body` 的前 80 个字符\n\n'
            '最后用几个例子验证并打印。'
        ),
        'starter_code': 'def build_payload(model, messages, temperature=0.7, max_tokens=800, stream=False):\n    pass\n\n\ndef parse_response(data):\n    pass\n\n\ndef describe_error(status, body=""):\n    pass\n',
        'solution': (
            "def build_payload(model, messages, temperature=0.7, max_tokens=800, stream=False):\n"
            "    if not isinstance(messages, list) or not messages:\n"
            "        raise ValueError('messages 不能为空')\n"
            "    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):\n"
            "        raise ValueError('temperature 必须在 0~2 之间')\n"
            "    if not 0 <= temperature <= 2:\n"
            "        raise ValueError('temperature 必须在 0~2 之间')\n"
            "    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens <= 0:\n"
            "        raise ValueError('max_tokens 必须是正整数')\n"
            "    return {\n"
            "        'model': model,\n"
            "        'messages': messages,\n"
            "        'temperature': temperature,\n"
            "        'max_tokens': max_tokens,\n"
            "        'stream': bool(stream),\n"
            "    }\n"
            "\n"
            "\n"
            "def parse_response(data):\n"
            "    if not isinstance(data, dict):\n"
            "        return {'ok': False, 'error': '响应结构异常'}\n"
            "    choices = data.get('choices')\n"
            "    if not isinstance(choices, list) or not choices:\n"
            "        return {'ok': False, 'error': '响应结构异常'}\n"
            "    message = choices[0].get('message') or {}\n"
            "    usage = data.get('usage') or {}\n"
            "    return {\n"
            "        'ok': True,\n"
            "        'content': message.get('content', ''),\n"
            "        'model': data.get('model', ''),\n"
            "        'tokens': usage.get('total_tokens', 0),\n"
            "    }\n"
            "\n"
            "\n"
            "def describe_error(status, body=''):\n"
            "    mapping = {\n"
            "        401: 'API Key 不正确或已失效',\n"
            "        403: '没有权限或账号欠费',\n"
            "        404: '模型名称或接口地址不对',\n"
            "        429: '请求太频繁或额度用尽，请稍后重试',\n"
            "    }\n"
            "    if status in mapping:\n"
            "        return mapping[status]\n"
            "    if isinstance(status, int) and 500 <= status < 600:\n"
            "        return '服务端异常，请稍后重试'\n"
            "    return f'请求失败（HTTP {status}）：{str(body)[:80]}'\n"
            "\n"
            "\n"
            "msgs = [{'role': 'user', 'content': '你好'}]\n"
            "print(build_payload('deepseek-chat', msgs))\n"
            "print(parse_response({'model': 'deepseek-chat', 'choices': [{'message': {'content': '你好！'}}], 'usage': {'total_tokens': 12}}))\n"
            "print(parse_response({'choices': []}))\n"
            "for code in (401, 403, 404, 429, 502, 418):\n"
            "    print(code, describe_error(code, 'some body text'))\n"
            "try:\n"
            "    build_payload('m', msgs, temperature=5)\n"
            "except ValueError as exc:\n"
            "    print('拦截：', exc)\n"
        ),
        'checks': [
            "msgs = [{'role': 'user', 'content': 'hi'}]",
            "p = build_payload('deepseek-chat', msgs)",
            "assert p == {'model': 'deepseek-chat', 'messages': msgs, 'temperature': 0.7, 'max_tokens': 800, 'stream': False}, '默认请求体不对：%r' % (p,)",
            "assert build_payload('m', msgs, stream=True)['stream'] is True, 'stream 参数没生效'",
            "for bad_temp in (2.1, -0.1, 'hot'):\n    try:\n        build_payload('m', msgs, temperature=bad_temp)\n        raise AssertionError('temperature=%r 应该抛 ValueError' % (bad_temp,))\n    except ValueError as exc:\n        assert 'temperature' in str(exc), '异常信息应提到 temperature'",
            "for bad_tokens in (0, -5, 1.5, 'many', True):\n    try:\n        build_payload('m', msgs, max_tokens=bad_tokens)\n        raise AssertionError('max_tokens=%r 应该抛 ValueError' % (bad_tokens,))\n    except ValueError as exc:\n        assert 'max_tokens' in str(exc), '异常信息应提到 max_tokens'",
            "for bad_msgs in ([], None, 'hi'):\n    try:\n        build_payload('m', bad_msgs)\n        raise AssertionError('messages=%r 应该抛 ValueError' % (bad_msgs,))\n    except ValueError as exc:\n        assert 'messages' in str(exc), '异常信息应提到 messages'",
            "good = {'model': 'deepseek-chat', 'choices': [{'message': {'content': '你好'}}], 'usage': {'total_tokens': 12}}",
            "r = parse_response(good)",
            "assert r == {'ok': True, 'content': '你好', 'model': 'deepseek-chat', 'tokens': 12}, '正常响应解析不对：%r' % (r,)",
            "assert parse_response({'model': 'm', 'choices': [{'message': {'content': 'x'}}]})['tokens'] == 0, '取不到 usage 时 tokens 应为 0'",
            "assert parse_response({'choices': []})['ok'] is False, 'choices 为空应判为结构异常'",
            "assert parse_response({})['error'] == '响应结构异常', '缺 choices 应返回结构异常'",
            "assert parse_response(None)['ok'] is False, 'None 应返回结构异常，不能崩'",
            "assert describe_error(401) == 'API Key 不正确或已失效', '401 的中文提示不对：%r' % describe_error(401)",
            "assert describe_error(403) == '没有权限或账号欠费', '403 的提示不对'",
            "assert describe_error(404) == '模型名称或接口地址不对', '404 的提示不对'",
            "assert describe_error(429) == '请求太频繁或额度用尽，请稍后重试', '429 的提示不对'",
            "assert describe_error(503) == '服务端异常，请稍后重试', '5xx 的提示不对'",
            "assert '418' in describe_error(418, 'i am a teapot'), '未知状态码要带上状态码：%r' % describe_error(418, 'i am a teapot')",
            "assert len(describe_error(418, 'x' * 500)) <= 120, '未知错误里的 body 要截断，不能把整段返回体糊给用户'",
        ],
        'explanation': (
            '这三段代码对应了调用任何 HTTP API 的完整流程，'
            '**把它们分开写**（组请求 / 解响应 / 翻译错误）'
            '是很有必要的——每一段都能单独测试，'
            '排查线上问题时也能立刻定位是哪一环出了岔子。\n\n'
            '校验 `temperature` 时要注意 `isinstance(temperature, bool)`：'
            '又是 `True` 是 `int` 这个坑，'
            '不排除的话 `temperature=True` 会被当成 1.0 通过。'
            '真实项目里这种「类型意外」往往来自 JSON 反序列化。\n\n'
            '`parse_response` 里连续三个 `.get()` 加 `or {}`：'
            '`data.get("choices")`、`choices[0].get("message") or {}`，'
            '一路防着「字段缺失」。'
            '因为**上游返回的结构不总是你以为的那样**：'
            '模型被内容审核拦截时，返回的可能压根没有 `choices`。'
            '不防的话就是 `KeyError` / `IndexError` 直接把接口打成 500。\n\n'
            '`describe_error` 的价值全在「说人话」：'
            '用户看到 `HTTP 401` 一头雾水，'
            '看到「API Key 不正确或已失效」就知道该去检查密钥了。'
            '把 4xx/5xx 归类成**用户能行动的建议**，'
            '是后端接口设计里回报很高的一件事。\n\n'
            '最后那条 `str(body)[:80]` 的截断也别省：'
            '上游报错时可能返回几 KB 的 HTML 错误页，'
            '整个塞进错误信息会污染日志、撑爆前端提示框。'
        ),
        'expected_output': "{'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': '你好'}], 'temperature': 0.7, 'max_tokens': 800, 'stream': False}\n{'ok': True, 'content': '你好！', 'model': 'deepseek-chat', 'tokens': 12}\n{'ok': False, 'error': '响应结构异常'}\n401 API Key 不正确或已失效\n403 没有权限或账号欠费\n404 模型名称或接口地址不对\n429 请求太频繁或额度用尽，请稍后重试\n502 服务端异常，请稍后重试\n418 请求失败（HTTP 418）：some body text\n拦截： temperature 必须在 0~2 之间",
        'hints': ['温度校验注意 True 也是 int，要单独排除布尔值', '解析响应一路用 .get() 加 or {} 防字段缺失'],
    },
    {
        'id': 'ch28-02',
        'chapter_id': 28,
        'title': '按 token 预算裁剪对话历史',
        'difficulty': 3,
        'tags': ['API', '上下文管理', '算法'],
        'statement': (
            '模型的上下文窗口有限。发请求前要**按 token 预算裁剪历史**，'
            '策略是「保留 system + 最近的若干轮，从最老的开始丢」。\n\n'
            '定义 `trim_messages(messages, budget, count_tokens)`：\n\n'
            '- `messages`：完整消息列表（可能以 system 开头）\n'
            '- `budget`：允许的最大 token 数\n'
            '- `count_tokens`：一个函数，接收消息列表返回 token 估算值（复用上一题的实现）\n\n'
            '返回裁剪后的消息列表，规则：\n'
            '1. **system 消息永远保留**（在开头）\n'
            '2. 从**最老的**非 system 消息开始删除，直到总量降到预算内\n'
            '3. 删除时要保证 user / assistant 成对：'
            '如果删完剩下以 assistant 开头的对话，继续删掉它\n'
            '4. 如果只留 system 还是超预算，就**只返回 system**\n\n'
            '5. 如果连 system 都没有且超预算，返回**最后一条消息**'
            '（总得让模型看到点什么）\n\n'
            '另外返回被丢弃的条数：函数返回 `(trimmed, dropped_count)`。\n\n'
            '最后用示例验证并打印。'
        ),
        'starter_code': 'def trim_messages(messages, budget, count_tokens):\n    pass\n',
        'solution': (
            "def trim_messages(messages, budget, count_tokens):\n"
            "    items = list(messages or [])\n"
            "    if not items:\n"
            "        return [], 0\n"
            "    system = items[0] if items[0].get('role') == 'system' else None\n"
            "    body = items[1:] if system else items[:]\n"
            "\n"
            "    def total(part):\n"
            "        return count_tokens(([system] if system else []) + part)\n"
            "\n"
            "    # 至少留一条，其余从最老的开始丢\n"
            "    while len(body) > 1 and total(body) > budget:\n"
            "        body.pop(0)\n"
            "    # 剪完如果开头是 assistant，说明它的提问被删了，一起删掉\n"
            "    while body and body[0].get('role') == 'assistant':\n"
            "        body.pop(0)\n"
            "    if total(body) > budget:\n"
            "        # 一条都放不下：有 system 就只留 system，否则留最后一条\n"
            "        body = [] if system else body[-1:]\n"
            "    result = ([system] if system else []) + body\n"
            "    if not result:\n"
            "        result = [items[-1]]\n"
            "    return result, len(items) - len(result)\n"
            "\n"
            "\n"
            "def rough_tokens(messages):\n"
            "    total = 0\n"
            "    for message in messages:\n"
            "        total += len(str(message.get('content', ''))) + 4\n"
            "    return total\n"
            "\n"
            "\n"
            "history = [{'role': 'system', 'content': '你是老师'}] + [\n"
            "    {'role': 'user', 'content': f'问题{i}'} for i in range(1, 6)\n"
            "]\n"
            "history = [{'role': 'system', 'content': '你是老师'}]\n"
            "for i in range(1, 6):\n"
            "    history.append({'role': 'user', 'content': f'问题{i}的详细描述' * 2})\n"
            "    history.append({'role': 'assistant', 'content': f'回答{i}的内容' * 2})\n"
            "trimmed, dropped = trim_messages(history, 100, rough_tokens)\n"
            "print('原有', len(history), '条，丢弃', dropped, '条')\n"
            "for m in trimmed:\n"
            "    print(' ', m['role'], m['content'][:12])\n"
        ),
        'checks': [
            "def tcount(msgs):\n    return sum(len(str(m.get('content', ''))) + 4 for m in msgs)",
            "full = [{'role': 'system', 'content': 'S'}, {'role': 'user', 'content': 'u1'}, {'role': 'assistant', 'content': 'a1'}, {'role': 'user', 'content': 'u2'}, {'role': 'assistant', 'content': 'a2'}]",
            "keep, dropped = trim_messages(full, 1000, tcount)",
            "assert keep == full and dropped == 0, '预算够时不应删任何消息：%r' % (keep,)",
            "small, d2 = trim_messages(full, 20, tcount)",
            "assert small[0]['role'] == 'system', 'system 必须保留在开头：%r' % (small,)",
            "assert tcount(small) <= 20, '裁剪后必须落在预算内，实际 %d' % tcount(small)",
            "assert small[-1]['content'] == 'a2', '应该保留最新的消息：%r' % (small,)",
            "assert d2 == 2, '应丢掉最开始的两条（u1、a1），实际丢 %d 条' % d2",
            "paired, d3 = trim_messages(full, 25, tcount)",
            "roles = [m['role'] for m in paired]",
            "assert roles == ['system', 'user', 'assistant'], '裁剪后不能以 assistant 开头：%r' % (roles,)",
            "assert d3 >= 2, '成对删除要一并计入丢弃条数：%d' % d3",
            "no_sys = [{'role': 'user', 'content': 'x' * 50}]",
            "single, d4 = trim_messages(no_sys, 5, tcount)",
            "assert single == no_sys, '没有 system 且只有一条消息时，至少保留这一条'",
            "empty, d5 = trim_messages([], 100, tcount)",
            "assert empty == [] and d5 == 0, '空输入应返回空列表和 0'",
            "tight = [{'role': 'system', 'content': 'S'}, {'role': 'user', 'content': 'u'}]",
            "only_sys, d6 = trim_messages(tight, 5, tcount)",
            "assert only_sys == [{'role': 'system', 'content': 'S'}], '只留 system 也超预算时，就只返回 system：%r' % (only_sys,)",
            "assert tcount(only_sys) <= 10, 'system 本身很短，结果应该很干净'",
            "same = trim_messages(full, 1000, tcount)[0]",
            "assert same[1]['content'] == 'u1', '不该改动原列表的顺序'",
        ],
        'explanation': (
            '上下文管理是 AI 应用工程里**最容易出事**的一环：'
            '不做裁剪，用户聊到第 30 轮就会收到「context length exceeded」，'
            '而且报错信息通常很难看。\n\n'
            '策略选择上有讲究。常見三种：\n'
            '1. **从头丢**（本題）：实现简单，代价是最早的信息丢了。'
            '适合「用户只关心最近在问什么」的场景；\n'
            '2. **摘要压缩**：用一次额外的大模型调用把旧对话浓缩成一段摘要。'
            '保住信息但多花钱、多一次延迟；\n'
            '3. **按重要性保留**：把系统提示、用户明确设定的偏好标记为「必须保留」。\n'
            '生产系统通常是 2 + 3 结合。\n\n'
            '**为什么必须成对删除？** 如果裁剪后剩下的第一条是 `assistant`，'
            '模型看到的对话就始于「自己说过的一句话」，'
            '很多服务商会直接返回 400（消息序列非法），'
            '或者让模型产生严重的幻觉——它会顺着这个残缺上下文继续编。\n\n'
            '**为什么 system 永远保留？** 它是整个对话的「人格与规则」。'
            '丢了它，模型会变回默认语气、忘掉所有约束，'
            '用户会立刻感觉「AI 变傻了」。'
            '这也是为什么 system 通常写得很精简——'
            '它要占着预算的每一轮都在场。\n\n'
            '最后两个兜底分支（只留 system / 只留最后一条）看起来是「不可能的路径」，'
            '但真实线上会遇到：用户粘贴了一篇 5 万字的文章，'
            '预算再怎么裁都不够。'
            '这时候**宁可丢掉大部分内容，也不能让请求直接失败**——'
            '让模型看到点什么，比让用户看到 500 好。'
        ),
        'expected_output': '原有 11 条，丢弃 6 条\n  system 你是老师\n  user 问题4的详细描述问题4的\n  assistant 回答4的内容回答4的内容\n  user 问题5的详细描述问题5的\n  assistant 回答5的内容回答5的内容',
        'hints': ['用 while 循环从最老的开始 pop(0)，直到总量进预算', '剪完后再检查开头是不是 assistant，是就继续删'],
    },

    # ── 第 29 章 主流智能体框架全景 ────────────────────────
    {
        'id': 'ch29-01',
        'chapter_id': 29,
        'title': '给工具调用结果做缓存与限流',
        'difficulty': 3,
        'tags': ['智能体', '缓存', '限流'],
        'statement': (
            '智能体反复调用工具时会浪费时间和额度，' \
            '所以要加**缓存**（同样的调用不重复执行）和**限流**（防止打爆下游）。\n\n'
            '实现一个极简的 `ToolBox` 类：\n\n'
            '```python\n'
            'class ToolBox:\n'
            '    def __init__(self, ttl=60, rate_limit=3): ...\n'
            '    def register(self, name, fn): ...\n'
            '    def call(self, name, *args, **kwargs): ...\n'
            '```\n\n'
            '规则：\n'
            '1. **缓存**：相同 `(name, args, kwargs)` 的调用在 `ttl` 秒内直接返回上次结果，'
            '不重复执行。缓存命中时结果里带 `"cached": True`？——'
            '不用，**`call` 直接返回结果本身**，但要有 `hits` 计数属性记录命中次数\n'
            '2. **限流**：同一工具的调用次数超过 `rate_limit` 次时，'
            '返回 `{"error": "调用过于频繁"}`（缓存命中的不算在限流内）\n'
            '3. `stats()` 返回 `{"calls": 总调用次数, "hits": 缓存命中次数, '
            '"blocked": 被限流次数, "tools": [已注册工具名]}`\n'
            '4. 未注册的工具返回 `{"error": "未知工具 xxx"}`\n\n'
            '为了可测试，时间用 `self.now` 属性表示（默认 0），'
            '调用方可以通过修改 `box.now` 来模拟时间流逝。\n\n'
            '最后用示例（含时间推进）验证并打印。'
        ),
        'starter_code': 'class ToolBox:\n    def __init__(self, ttl=60, rate_limit=3):\n        pass\n\n    def register(self, name, fn):\n        pass\n\n    def call(self, name, *args, **kwargs):\n        pass\n\n    def stats(self):\n        pass\n',
        'solution': (
            "class ToolBox:\n"
            "    def __init__(self, ttl=60, rate_limit=3):\n"
            "        self.ttl = ttl\n"
            "        self.rate_limit = rate_limit\n"
            "        self.now = 0\n"
            "        self._tools = {}\n"
            "        self._cache = {}\n"
            "        self._counts = {}\n"
            "        self._calls = 0\n"
            "        self._hits = 0\n"
            "        self._blocked = 0\n"
            "\n"
            "    def register(self, name, fn):\n"
            "        self._tools[name] = fn\n"
            "        return self\n"
            "\n"
            "    @staticmethod\n"
            "    def _key(name, args, kwargs):\n"
            "        return name + '|' + repr(args) + '|' + repr(sorted(kwargs.items()))\n"
            "\n"
            "    def call(self, name, *args, **kwargs):\n"
            "        if name not in self._tools:\n"
            "            return {'error': f'未知工具 {name}'}\n"
            "        key = self._key(name, args, kwargs)\n"
            "        cached = self._cache.get(key)\n"
            "        if cached is not None and self.now - cached[0] <= self.ttl:\n"
            "            self._hits += 1\n"
            "            return cached[1]\n"
            "        served = self._counts.get(name, 0)\n"
            "        if served >= self.rate_limit:\n"
            "            self._blocked += 1\n"
            "            return {'error': '调用过于频繁'}\n"
            "        self._counts[name] = served + 1\n"
            "        self._calls += 1\n"
            "        result = self._tools[name](*args, **kwargs)\n"
            "        self._cache[key] = (self.now, result)\n"
            "        return result\n"
            "\n"
            "    def stats(self):\n"
            "        return {\n"
            "            'calls': self._calls,\n"
            "            'hits': self._hits,\n"
            "            'blocked': self._blocked,\n"
            "            'tools': sorted(self._tools),\n"
            "        }\n"
            "\n"
            "\n"
            "counter = {'n': 0}\n"
            "\n"
            "\n"
            "def slow_add(a, b):\n"
            "    counter['n'] += 1\n"
            "    return a + b\n"
            "\n"
            "\n"
            "box = ToolBox(ttl=60, rate_limit=3)\n"
            "box.register('add', slow_add)\n"
            "print(box.call('add', 1, 2))\n"
            "print(box.call('add', 1, 2))\n"
            "print('真实执行次数：', counter['n'])\n"
            "print(box.stats())\n"
            "box.now = 100\n"
            "print(box.call('add', 1, 2))\n"
            "print('缓存过期后执行次数：', counter['n'])\n"
            "box.now = 1000\n"
            "print(box.call('add', 5, 5), box.call('add', 6, 6))\n"
            "print(box.call('add', 7, 7))\n"
            "print(box.stats())\n"
        ),
        'checks': [
            "calls = {'n': 0}",
            "def f(a, b=0):\n    calls['n'] += 1\n    return a + b",
            "box = ToolBox(ttl=60, rate_limit=3)",
            "box.register('f', f)",
            "assert box.call('f', 1, b=2) == 3, '正常调用应返回结果'",
            "assert calls['n'] == 1, '第一次调用应该真的执行'",
            "assert box.call('f', 1, b=2) == 3 and calls['n'] == 1, '相同参数第二次调用应命中缓存，不重复执行'",
            "assert box.stats()['hits'] == 1, 'hits 计数不对：%r' % (box.stats(),)",
            "assert box.call('f', 2, b=2) == 4 and calls['n'] == 2, '参数不同不应命中缓存'",
            "assert box.call('f', 1, b=3) == 4 and calls['n'] == 3, '关键字参数不同也要区分开'",
            "ts = ToolBox(ttl=60, rate_limit=99)",
            "ts.register('f', f)",
            "before_ttl = calls['n']",
            "ts.call('f', 9, b=9)",
            "assert calls['n'] == before_ttl + 1, '新盒子第一次调用应真的执行'",
            "ts.call('f', 9, b=9)",
            "assert calls['n'] == before_ttl + 1, 'ttl 内重复调用应命中缓存'",
            "ts.now = 61",
            "ts.call('f', 9, b=9)",
            "assert calls['n'] == before_ttl + 2, '超过 ttl 后缓存应失效并重新执行，实际执行 %d 次' % calls['n']",
            "b2 = ToolBox(ttl=10, rate_limit=2)",
            "b2.register('g', lambda: 'ok')",
            "b2.call('g')",
            "b2.call('g', )",
            "third = b2.call('g')",
            "assert third == 'ok', '缓存命中不应触发限流：%r' % (third,)",
            "b3 = ToolBox(ttl=0, rate_limit=1)",
            "b3.register('h', lambda: 'v')",
            "assert b3.call('h') == 'v', '第一次应成功'",
            "b3.now = 1",
            "blocked = b3.call('h')",
            "assert blocked == {'error': '调用过于频繁'}, '超过限流应返回错误字典：%r' % (blocked,)",
            "assert b3.stats()['blocked'] == 1, 'blocked 计数不对：%r' % (b3.stats(),)",
            "assert box.call('nope') == {'error': '未知工具 nope'}, '未知工具应返回错误字典'",
            "assert box.stats()['tools'] == ['f'], 'tools 列表不对：%r' % (box.stats(),)",
            "assert set(box.stats()) == {'calls', 'hits', 'blocked', 'tools'}, 'stats 字段不完整：%r' % (box.stats(),)",
            "b4 = ToolBox(rate_limit=5)",
            "b4.register('a', lambda: 1).register('b', lambda: 2)",
            "assert b4.stats()['tools'] == ['a', 'b'], 'register 应支持链式调用'",
        ],
        'explanation': (
            '缓存和限流是让 Agent「能跑得久」的两个基础设施，'
            '而且它们的**顺序不能颠倒**：必须先查缓存，再判断限流。\n\n'
            '为什么？因为缓存命中并不消耗下游资源。'
            '用户连点三次同一个按钮，第三次应该直接秒回缓存结果，'
            '而不是被限流挡住报错——那样体验很差，而且逻辑上也说不通'
            '（你并没有真的调用下游）。\n\n'
            '缓存键的构造 `name + repr(args) + repr(sorted(kwargs.items()))` 有几个讲究：\n'
            '- `sorted(kwargs.items())` 让 `f(a=1, b=2)` 和 `f(b=2, a=1)` 命中同一份缓存。'
            '用 `repr(dict)` 直接拼的话，字典顺序不同就会被当成两次不同的调用；\n'
            '- 用 `repr` 而不是 `str`：`repr` 能区分 `1` 和 `"1"`，'
            '而 `str(1)` 和 `str("1")` 都是 `"1"`——'
            '这种键冲突会让工具收到错误类型的参数，是最难查的一类 bug；\n'
            '- 真实系统还会加上「工具版本」和「用户 id」，'
            '前者避免代码更新后读到旧缓存，后者避免用户之间串数据。\n\n'
            '`self.now` 做成可写属性，是为了**让时间可控**。'
            '如果代码里直接调 `time.time()`，测试就得 `time.sleep(60)` 才能验证缓存过期，'
            '整个测试套件会慢到没人愿意跑。'
            '把「当前时间」变成依赖，是写可测代码的通用手法。\n\n'
            '限流用**固定窗口计数**（最简单的实现）。'
            '真实场景常用令牌桶或滑动窗口，'
            '因为固定窗口在边界处会「双倍突发」——'
            '第 59 秒打满额度、第 61 秒又打满，两秒内实际放行了 2 倍流量。'
        ),
        'expected_output': "3\n3\n真实执行次数： 1\n{'calls': 1, 'hits': 1, 'blocked': 0, 'tools': ['add']}\n3\n缓存过期后执行次数： 2\n10 {'error': '调用过于频繁'}\n{'error': '调用过于频繁'}\n{'calls': 3, 'hits': 1, 'blocked': 2, 'tools': ['add']}",
        'hints': ['先查缓存再判断限流，命中缓存的调用不该被限流挡住', '缓存键要处理关键字参数的顺序，用 sorted(kwargs.items())'],
    },

    # ── 第 30–35 章 综合实战 ───────────────────────────────
    {
        'id': 'ch30-01',
        'chapter_id': 30,
        'title': '把需求写成可执行的任务清单',
        'difficulty': 2,
        'tags': ['项目管理', '需求拆解', '排序'],
        'statement': (
            '项目启动时，把需求拆成任务卡片，并按依赖排出执行顺序。\n\n'
            '任务卡片格式：\n\n'
            '```python\n'
            "tasks = [\n"
            "    {'id': 'T1', 'title': '搭建 FastAPI 骨架', 'deps': [], 'days': 1, 'priority': 1},\n"
            "    {'id': 'T2', 'title': '设计数据库表', 'deps': [], 'days': 1, 'priority': 2},\n"
            "    {'id': 'T3', 'title': '实现用户接口', 'deps': ['T1', 'T2'], 'days': 2, 'priority': 1},\n"
            "    {'id': 'T4', 'title': '接入 DeepSeek', 'deps': ['T3'], 'days': 2, 'priority': 1},\n"
            "    {'id': 'T5', 'title': '前端页面', 'deps': ['T3'], 'days': 3, 'priority': 2},\n"
            "]\n"
            '```\n\n'
            '实现 `plan(tasks)`，返回 `(order, total_days, warnings)`：\n\n'
            '- `order`：拓扑排序后的任务 id 列表。'
            '同一批可执行的任务里，**优先做 priority 小的**（1 比 2 优先），'
            'priority 相同时按 id 排\n'
            '- `total_days`：**关键路径**长度（按天累加，'
            '从无依赖任务开始算「最早完成时间」，取最大值）\n'
            '- `warnings`：字符串列表，'
            '依赖不存在的任务要报 `"T9 依赖的任务 T99 不存在"`；'
            '存在循环依赖要报 `"存在循环依赖，无法排序"`\n\n'
            '最后用示例数据打印结果。'
        ),
        'starter_code': 'def plan(tasks):\n    pass\n',
        'solution': (
            "def plan(tasks):\n"
            "    warnings = []\n"
            "    items = {}\n"
            "    for task in tasks or []:\n"
            "        if not isinstance(task, dict) or 'id' not in task:\n"
            "            continue\n"
            "        items[task['id']] = {\n"
            "            'deps': [d for d in (task.get('deps') or [])],\n"
            "            'days': max(1, int(task.get('days', 1))),\n"
            "            'priority': int(task.get('priority', 99)),\n"
            "        }\n"
            "    for tid, info in items.items():\n"
            "        for dep in info['deps']:\n"
            "            if dep not in items:\n"
            "                warnings.append(f'{tid} 依赖的任务 {dep} 不存在')\n"
            "        info['deps'] = [d for d in info['deps'] if d in items]\n"
            "    # 拓扑排序：同批次按 (priority, id) 选一个出来\n"
            "    order = []\n"
            "    done = set()\n"
            "    while len(done) < len(items):\n"
            "        ready = [tid for tid, info in items.items()\n"
            "                 if tid not in done and all(d in done for d in info['deps'])]\n"
            "        if not ready:\n"
            "            if '存在循环依赖，无法排序' not in warnings:\n"
            "                warnings.append('存在循环依赖，无法排序')\n"
            "            break\n"
            "        ready.sort(key=lambda tid: (items[tid]['priority'], tid))\n"
            "        order.append(ready[0])\n"
            "        done.add(ready[0])\n"
            "    # 关键路径：每个任务的最早完成时间 = 自身天数 + 依赖里最大的完成时间\n"
            "    finish = {}\n"
            "    for tid in order:\n"
            "        base = max((finish[d] for d in items[tid]['deps'] if d in finish), default=0)\n"
            "        finish[tid] = base + items[tid]['days']\n"
            "    total_days = max(finish.values()) if finish else 0\n"
            "    return order, total_days, warnings\n"
            "\n"
            "\n"
            "tasks = [\n"
            "    {'id': 'T1', 'title': '搭建 FastAPI 骨架', 'deps': [], 'days': 1, 'priority': 1},\n"
            "    {'id': 'T2', 'title': '设计数据库表', 'deps': [], 'days': 1, 'priority': 2},\n"
            "    {'id': 'T3', 'title': '实现用户接口', 'deps': ['T1', 'T2'], 'days': 2, 'priority': 1},\n"
            "    {'id': 'T4', 'title': '接入 DeepSeek', 'deps': ['T3'], 'days': 2, 'priority': 1},\n"
            "    {'id': 'T5', 'title': '前端页面', 'deps': ['T3'], 'days': 3, 'priority': 2},\n"
            "]\n"
            "order, days, warns = plan(tasks)\n"
            "print(order, days, warns)\n"
        ),
        'checks': [
            "tasks = [\n    {'id': 'T1', 'deps': [], 'days': 1, 'priority': 1},\n    {'id': 'T2', 'deps': [], 'days': 1, 'priority': 2},\n    {'id': 'T3', 'deps': ['T1', 'T2'], 'days': 2, 'priority': 1},\n    {'id': 'T4', 'deps': ['T3'], 'days': 2, 'priority': 1},\n    {'id': 'T5', 'deps': ['T3'], 'days': 3, 'priority': 2},\n]",
            "order, days, warns = plan(tasks)",
            "assert order == ['T1', 'T2', 'T3', 'T4', 'T5'], '排序结果不对：%r' % (order,)",
            "assert warns == [], '没有坏数据时不应有警告：%r' % (warns,)",
            "assert days == 6, '关键路径应为 T1→T3→T5 = 1+2+3 = 6 天，实际 %r' % (days,)",
            "prio = [\n    {'id': 'A', 'deps': [], 'days': 1, 'priority': 3},\n    {'id': 'B', 'deps': [], 'days': 1, 'priority': 1},\n]",
            "o2, d2, _ = plan(prio)",
            "assert o2 == ['B', 'A'], '同批任务应先做 priority 小的：%r' % (o2,)",
            "broken = [{'id': 'X', 'deps': ['MISSING'], 'days': 1}]",
            "o3, d3, w3 = plan(broken)",
            "assert any('MISSING' in w for w in w3), '依赖不存在的任务要给出警告：%r' % (w3,)",
            "assert o3 == ['X'], '依赖缺失的任务本身仍应被排进去：%r' % (o3,)",
            "cyclic = [{'id': 'P', 'deps': ['Q'], 'days': 1}, {'id': 'Q', 'deps': ['P'], 'days': 1}]",
            "o4, d4, w4 = plan(cyclic)",
            "assert any('循环依赖' in w for w in w4), '循环依赖要给出警告：%r' % (w4,)",
            "assert o4 == [], '有环时排不出顺序：%r' % (o4,)",
            "assert plan([]) == ([], 0, []), '空任务列表应返回 ([], 0, [])'",
            "long = [{'id': 'S', 'deps': [], 'days': 5}, {'id': 'T', 'deps': ['S'], 'days': 1}]",
            "assert plan(long)[1] == 6, '依赖链的工期要累加：%r' % (plan(long)[1],)",
            "par = [{'id': 'P1', 'deps': [], 'days': 3}, {'id': 'P2', 'deps': [], 'days': 7}]",
            "assert plan(par)[1] == 7, '并行任务的关键路径取最大值，不是求和：%r' % (plan(par)[1],)",
        ],
        'explanation': (
            '这道题把「项目管理」变成了两个真实算法：**拓扑排序**和**关键路径**。\n\n'
            '拓扑排序这里用的是「反复挑就绪任务」的做法，'
            '和前面第 21 章那道架构题的区别在于：'
            '这里每轮**只挑一个**（按 priority 排序后取第一个），'
            '所以能表达「优先做哪个」这种业务意图。'
            '如果一次把整批就绪的都加入结果，就只能得到「层」的概念，'
            '没法在层内排序。\n\n'
            '**关键路径**是这道题最有价值的点。很多人算工期时会写'
            '`total += days`（把天数全加起来），'
            '那样 T1 和 T2 并行的话会算成 2 天，实际只要 1 天。\n'
            '正确做法是「**最早完成时间**」：\n\n'
            '```\n'
            'finish[任务] = 自身天数 + max(所有前置任务的 finish)\n'
            '```\n\n'
            '`max(..., default=0)` 里的 `default` 处理了「没有依赖」的情况——'
            '前置为空时取 0，所以 `finish = 0 + days`。'
            '用 `max(生成器, default=0)` 比先判断空列表再取 max 简洁，'
            '这是 Python 3.4 之后才有的便利。\n\n'
            '**为什么依赖不存在的任务仍然要排进 order？**'
            '因为「依赖写错了」是数据问题，「任务本身能不能做」是另一回事。'
            '警告已经告诉用户去修 `deps`，'
            '任务本身仍然应该出现在计划里——'
            '直接把它丢掉，用户会以为任务凭空消失了。\n\n'
            '**有环时 `order` 返回空列表**，而不是返回未完成的部分。'
            '因为一个拿不到完整顺序的计划是有害的（会误导排期），'
            '不如明确失败 + 给出可行动的警告。'
        ),
        'expected_output': "['T1', 'T2', 'T3', 'T4', 'T5'] 6 []",
        'hints': ['每轮挑「依赖已完成」的任务里 priority 最小的那个', '关键路径是「自身天数 + 前置任务里最大的完成时间」'],
    },

    # ── 第 32 章 综合实战 M2：后端开发 ─────────────────────
    {
        'id': 'ch32-01',
        'chapter_id': 32,
        'title': '把数据库查询结果映射成对象',
        'difficulty': 2,
        'tags': ['数据库', '后端', '数据映射'],
        'statement': (
            '数据库驱动返回的是「列名 + 一堆元组」，'
            '业务代码需要的是字典列表。这层转换写错了，后面全是 bug。\n\n'
            '实现三个函数：\n\n'
            '1. `to_dicts(columns, rows)`：把查询结果映射成字典列表。\n'
            '   - `columns` 是列名列表，`rows` 是元组/列表的列表\n'
            '   - 行比列长时，多出来的值丢掉；行比列短时，缺的列补 `None`\n'
            '   - `columns` 为空或 `rows` 为空时返回空列表\n\n'
            '2. `pick(records, fields)`：只保留指定字段，返回新的字典列表。\n'
            '   - 记录里缺的字段补 `None`\n'
            '   - `fields` 的顺序决定结果字典的键顺序\n\n'
            '3. `build_limit(limit, offset)`：返回 `("LIMIT ? OFFSET ?", [limit, offset])`。\n'
            '   - `limit` 必须是 1~100 的整数，不合法就取默认 20\n'
            '   - `offset` 必须是不小于 0 的整数，不合法就取默认 0\n'
            '   - **不要抛异常**，非法值一律回落默认值\n\n'
            '最后用几个例子（含脏数据）验证并打印。'
        ),
        'starter_code': 'def to_dicts(columns, rows):\n    pass\n\n\ndef pick(records, fields):\n    pass\n\n\ndef build_limit(limit, offset):\n    pass\n',
        'solution': (
            "def to_dicts(columns, rows):\n"
            "    columns = list(columns or [])\n"
            "    if not columns:\n"
            "        return []\n"
            "    result = []\n"
            "    for row in rows or []:\n"
            "        values = list(row or [])\n"
            "        record = {}\n"
            "        for index, name in enumerate(columns):\n"
            "            record[name] = values[index] if index < len(values) else None\n"
            "        result.append(record)\n"
            "    return result\n"
            "\n"
            "\n"
            "def pick(records, fields):\n"
            "    fields = list(fields or [])\n"
            "    result = []\n"
            "    for record in records or []:\n"
            "        item = {}\n"
            "        for field in fields:\n"
            "            item[field] = (record or {}).get(field)\n"
            "        result.append(item)\n"
            "    return result\n"
            "\n"
            "\n"
            "def build_limit(limit, offset):\n"
            "    ok_limit = isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 100\n"
            "    ok_offset = isinstance(offset, int) and not isinstance(offset, bool) and offset >= 0\n"
            "    return 'LIMIT ? OFFSET ?', [limit if ok_limit else 20, offset if ok_offset else 0]\n"
            "\n"
            "\n"
            "cols = ['id', 'name', 'score']\n"
            "print(to_dicts(cols, [(1, '小明', 88), (2, '小红')]))\n"
            "print(pick(to_dicts(cols, [(1, '小明', 88), (2, '小红')]), ['name', 'id']))\n"
            "print(build_limit(50, 0))\n"
            "print(build_limit(-1, 'abc'))\n"
        ),
        'checks': [
            "cols = ['id', 'name']",
            "assert to_dicts(cols, [(1, 'a'), (2, 'b')]) == [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}], '基本映射不对'",
            "assert to_dicts(cols, [(1, 'a', 999)]) == [{'id': 1, 'name': 'a'}], '多出来的值应被丢掉：%r' % (to_dicts(cols, [(1, 'a', 999)]),)",
            "assert to_dicts(cols, [(1,)]) == [{'id': 1, 'name': None}], '缺的列应补 None：%r' % (to_dicts(cols, [(1,)]),)",
            "assert to_dicts([], [(1, 2)]) == [], '列名为空时应返回空列表'",
            "assert to_dicts(cols, []) == [], '没有数据行时应返回空列表'",
            "assert to_dicts(cols, None) == [], 'rows 为 None 时应返回空列表，不能崩'",
            "recs = [{'id': 1, 'name': 'a', 'secret': 'x'}, {'name': 'b'}]",
            "picked = pick(recs, ['name', 'id'])",
            "assert picked == [{'name': 'a', 'id': 1}, {'name': 'b', 'id': None}], '字段裁剪/补 None 不对：%r' % (picked,)",
            "assert list(picked[0].keys()) == ['name', 'id'], '结果字典的键顺序应跟 fields 一致：%r' % (list(picked[0].keys()),)",
            "assert 'secret' not in picked[0], '未指定的字段不应出现在结果里'",
            "assert recs[0].get('secret') == 'x', 'pick 不应改动原记录'",
            "assert pick([], ['id']) == [] and pick(recs, []) == [{}, {}], '空输入应返回空列表/空字典'",
            "sql, params = build_limit(50, 10)",
            "assert sql == 'LIMIT ? OFFSET ?' and params == [50, 10], 'SQL 与参数不对：%r %r' % (sql, params)",
            "assert build_limit(-1, 0)[1] == [20, 0], '非法 limit 应回落 20'",
            "assert build_limit(200, 0)[1] == [20, 0], '超上限的 limit 应回落 20'",
            "assert build_limit(True, 0)[1] == [20, 0], '布尔值不算整数，应回落 20'",
            "assert build_limit('30', 0)[1] == [20, 0], '字符串形式的 limit 应回落 20（不能直接拼进 SQL）'",
            "assert build_limit(10, -5)[1] == [10, 0], '非法 offset 应回落 0'",
            "assert build_limit(10, 'x')[1] == [10, 0], '字符串 offset 应回落 0'",
            "assert build_limit(10, 0)[1][1] == 0, 'offset 为 0 是合法值'",
        ],
        'explanation': (
            '`to_dicts` 是「行 → 字典」的映射层。它看起来简单，但有两个必须处理的现实：\n\n'
            '1. **行比列短**。数据库加字段、迁移没跑完、或者手写的 mock 数据不齐，'
            '都会让某行的元素个数少几个。不补 `None` 就是 `IndexError`。\n'
            '2. **行比列长**。SQL 用了 `SELECT *` 但列名列表过期了，'
            '多出来的值必须丢掉——如果按 `zip` 来写就会静默错位。\n\n'
            '`pick` 里 `list(picked[0].keys()) == ["name", "id"]` 这个检查说明了一个容易被忽略的点：'
            '**Python 3.7+ 的字典是有序的**，键顺序就是插入顺序。'
            '所以按 `fields` 顺序构造字典，前端表格的列顺序就自然对了。'
            '这也解释了为什么 `pick` 要用 for 循环逐个插入，而不是 `{k: v for k in fields}` '
            '——后者其实也对，但用 `**` 合并或 `dict.fromkeys` 就会丢顺序。\n\n'
            '`build_limit` 的「不抛异常，回落默认值」是分页接口的常见策略：'
            '翻页参数是用户可控的，一个手滑的 `page=-1` 不该让整个列表页报 500。'
            '和 `build_query` 那题里「表名非法就抛异常」不同——'
            '**表名来自代码，limit 来自用户**，所以处理方式不同。\n\n'
            '`isinstance(limit, bool)` 又出现了。这个模式在本课程里出现了第五次，'
            '它值得你形成条件反射：**只要做整数校验，就顺手排除 bool**。'
        ),
        'expected_output': "[{'id': 1, 'name': '小明', 'score': 88}, {'id': 2, 'name': '小红', 'score': None}]\n[{'name': '小明', 'id': 1}, {'name': '小红', 'id': 2}]\n('LIMIT ? OFFSET ?', [50, 0])\n('LIMIT ? OFFSET ?', [20, 0])",
        'hints': ['按列名逐个取值，用下标是否越界来决定补 None', 'limit/offset 非法时回落默认值，不要抛异常'],
    },

    # ── 第 33 章 综合实战 M3：前端开发 ─────────────────────
    {
        'id': 'ch33-01',
        'chapter_id': 33,
        'title': '三栏工作区的面板状态归并',
        'difficulty': 2,
        'tags': ['前端', '状态管理', '不可变更新'],
        'statement': (
            '三栏工作区（左侧栏 / 中间编辑区 / 右侧栏）的面板状态用字典表示：\n\n'
            '```python\n'
            "state = {'left': True, 'center': True, 'right': False}\n"
            '```\n\n'
            '实现三个函数，**全部返回新字典，不许修改传入的 state**：\n\n'
            '1. `toggle(state, name)`：切换某个面板的展开状态；名字不存在时原样返回\n'
            '2. `only(state, name)`：手风琴模式——只展开 `name`，其他都收起；'
            '`name` 不存在时原样返回\n'
            '3. `apply_events(state, events)`：按顺序处理事件列表，返回最终状态。\n'
            '   事件形如 `("toggle", "right")` / `("only", "left")` / '
            '`("set", "left", False)`，遇到不认识的类型就**跳过**\n\n'
            '最后用一串事件验证并打印每一步的状态。'
        ),
        'starter_code': "state = {'left': True, 'center': True, 'right': False}\n\n\ndef toggle(state, name):\n    pass\n\n\ndef only(state, name):\n    pass\n\n\ndef apply_events(state, events):\n    pass\n",
        'solution': (
            "state = {'left': True, 'center': True, 'right': False}\n"
            "\n"
            "\n"
            "def toggle(state, name):\n"
            "    if name not in state:\n"
            "        return dict(state)\n"
            "    updated = dict(state)\n"
            "    updated[name] = not state[name]\n"
            "    return updated\n"
            "\n"
            "\n"
            "def only(state, name):\n"
            "    if name not in state:\n"
            "        return dict(state)\n"
            "    return {key: (key == name) for key in state}\n"
            "\n"
            "\n"
            "def apply_events(state, events):\n"
            "    current = dict(state or {})\n"
            "    for event in events or []:\n"
            "        if not event:\n"
            "            continue\n"
            "        kind = event[0]\n"
            "        if kind == 'toggle' and len(event) >= 2:\n"
            "            current = toggle(current, event[1])\n"
            "        elif kind == 'only' and len(event) >= 2:\n"
            "            current = only(current, event[1])\n"
            "        elif kind == 'set' and len(event) >= 3:\n"
            "            if event[1] in current:\n"
            "                current = dict(current)\n"
            "                current[event[1]] = bool(event[2])\n"
            "    return current\n"
            "\n"
            "\n"
            "print(apply_events(state, [('toggle', 'right')]))\n"
            "print(apply_events(state, [('only', 'left'), ('toggle', 'right')]))\n"
            "print(apply_events(state, [('set', 'center', 0), ('nope', 'x')]))\n"
            "print('原状态：', state)\n"
        ),
        'checks': [
            "base = {'left': True, 'center': True, 'right': False}",
            "toggled = toggle(base, 'right')",
            "assert toggled == {'left': True, 'center': True, 'right': True}, '切换结果不对：%r' % (toggled,)",
            "assert base == {'left': True, 'center': True, 'right': False}, '不能修改传入的 state'",
            "assert toggle(base, 'nope') == base, '未知面板应原样返回'",
            "assert toggle(base, 'nope') is not base, '即使原样返回，也应该是一个新字典（避免调用方改到内部状态）'",
            "single = only(base, 'right')",
            "assert single == {'left': False, 'center': False, 'right': True}, '手风琴模式结果不对：%r' % (single,)",
            "assert only(base, 'nope') == base, '未知面板时 only 应原样返回'",
            "assert only(base, 'left') == {'left': True, 'center': False, 'right': False}, '只展开 left 不对'",
            "step1 = apply_events(base, [('only', 'left'), ('toggle', 'right')])",
            "assert step1 == {'left': True, 'center': False, 'right': True}, '事件序列处理不对：%r' % (step1,)",
            "assert apply_events(base, []) == base, '空事件列表应返回等价状态'",
            "assert apply_events(base, [('set', 'center', 0)]) == {'left': True, 'center': False, 'right': False}, 'set 事件应把值转成布尔：%r' % (apply_events(base, [('set', 'center', 0)]),)",
            "assert apply_events(base, [('set', 'ghost', True)]) == base, '对不存在的面板 set 应被忽略'",
            "assert apply_events(base, [('unknown_event', 'x'), ('toggle', 'left')]) == {'left': False, 'center': True, 'right': False}, '未知事件应跳过，后续事件继续生效'",
            "assert apply_events(base, [('toggle',)]) == base, '事件参数不足时应跳过而不是崩掉'",
            "assert apply_events(None, [('toggle', 'left')]) == {}, 'state 为 None 时按空状态处理（面板不存在，toggle 无效果）'",
            "assert base == {'left': True, 'center': True, 'right': False}, '跑完所有事件后原状态仍不能变'",
        ],
        'explanation': (
            '三个函数都遵循同一个原则：**返回新字典，绝不修改入参**。'
            '这就是 Vue / React 里「不可变更新」的核心。\n\n'
            '为什么必须这么做？因为前端框架判断「要不要重新渲染」是靠**引用比较**：'
            '`oldState === newState` 就认为是同一份数据、不重新渲染。'
            '如果你原地改 `state.left = False`，引用没变，'
            '框架会以为什么都没发生，**页面不会更新**——'
            '这是新手用 Vue 3 的 `reactive` 和 React 的 `setState` 时最容易困惑的问题。\n\n'
            '`{key: (key == name) for key in state}` 这一行很精练：'
            '字典推导式直接根据「键是不是目标」决定 `True` / `False`，'
            '用布尔值当值构造新字典。比「先把所有键设为 False，再单独把一个设为 True」少一次遍历。\n\n'
            '`apply_events` 处理的是**事件流**：它必须容忍三类脏输入——'
            '未知事件类型（前端发了个新版本才有的事件）、'
            '参数个数不对（`("toggle",)`）、'
            '状态为 `None`（组件挂载前的初始值）。'
            '`if kind == "toggle" and len(event) >= 2` 这种写法把「类型对」和「参数够」'
            '放在同一个条件里，比层层嵌套的 try/except 清晰。\n\n'
            '最后一个断言「跑完所有事件后原状态仍不能变」是这道题真正的考点：'
            '**只要有一处漏了 `dict(state)` 拷贝，用户连着点两次按钮就可能出现诡异状态。**'
            '这类 bug 在单测里最容易漏，所以本題把所有修改路径都验了一遍。'
        ),
        'expected_output': "{'left': True, 'center': True, 'right': True}\n{'left': True, 'center': False, 'right': True}\n{'left': True, 'center': False, 'right': False}\n原状态： {'left': True, 'center': True, 'right': False}",
        'hints': ['每次都 dict(state) 拷一份再改，绝不原地改', '字典推导式可以一次构造出「只有某个键为 True」的字典'],
    },

    # ── 第 37 章 LLM API 工程化 ───────────────────────────
    {
        'id': 'ch37-01',
        'chapter_id': 37,
        'title': '指数退避重试：给模型调用加韧性',
        'difficulty': 3,
        'tags': ['工程化', '重试', '指数退避'],
        'statement': (
            '调用大模型接口时，限流（429）和网络抖动是常态。'
            '生产代码必须**退避重试**，而不是立刻失败或疯狂重试。\n\n'
            '已知两种异常：\n\n'
            '```python\n'
            'class RetryableError(Exception):   # 限流、超时——值得重试\n'
            'class FatalError(Exception):       # 参数错、密钥错——重试也没用\n'
            '```\n\n'
            '实现 `retry_call(fn, attempts=3, base_delay=0.5, max_delay=8.0, sleep=None)`：\n\n'
            '- 调用 `fn()`；成功就返回结果\n'
            '- 抛 `RetryableError` 时：如果还有剩余次数，'
            '**等一会儿再试**（延迟 = `min(max_delay, base_delay * 2 ** (第几次重试 - 1))`，'
            '即 0.5 → 1 → 2 → 4 → 8 封顶）\n'
            '- 抛 `FatalError` 或其它异常时：**立刻抛出**，不重试\n'
            '- 次数用尽仍失败：抛出最后一次的 `RetryableError`\n'
            '- `sleep` 是注入的「等待函数」（默认 `time.sleep`），'
            '测试时传一个记录延迟的假函数，**不要真的睡**\n'
            '- 返回 `(结果, delays)`：`delays` 是每次实际等待的秒数列表\n\n'
            '最后用一个「前两次限流、第三次成功」的函数验证并打印。'
        ),
        'starter_code': 'import time\n\nclass RetryableError(Exception):\n    pass\n\nclass FatalError(Exception):\n    pass\n\n\ndef retry_call(fn, attempts=3, base_delay=0.5, max_delay=8.0, sleep=None):\n    pass\n',
        'solution': (
            "import time\n"
            "\n"
            "class RetryableError(Exception):\n"
            "    pass\n"
            "\n"
            "class FatalError(Exception):\n"
            "    pass\n"
            "\n"
            "\n"
            "def retry_call(fn, attempts=3, base_delay=0.5, max_delay=8.0, sleep=None):\n"
            "    sleeper = sleep or time.sleep\n"
            "    delays = []\n"
            "    last_error = None\n"
            "    for round_index in range(max(1, attempts)):\n"
            "        try:\n"
            "            return fn(), delays\n"
            "        except RetryableError as exc:\n"
            "            last_error = exc\n"
            "            if round_index == attempts - 1:\n"
            "                break\n"
            "            delay = min(max_delay, base_delay * (2 ** round_index))\n"
            "            delays.append(delay)\n"
            "            sleeper(delay)\n"
            "    raise last_error\n"
            "\n"
            "\n"
            "record = []\n"
            "state = {'n': 0}\n"
            "\n"
            "\n"
            "def flaky():\n"
            "    state['n'] += 1\n"
            "    if state['n'] < 3:\n"
            "        raise RetryableError('限流了')\n"
            "    return '成功'\n"
            "\n"
            "\n"
            "result, delays = retry_call(flaky, attempts=3, sleep=record.append)\n"
            "print(result, delays, '调用次数', state['n'])\n"
        ),
        'checks': [
            "def make_sleep(log):\n    def _sleep(seconds):\n        log.append(seconds)\n    return _sleep",
            "log = []",
            "assert retry_call(lambda: 'ok', sleep=make_sleep(log)) == ('ok', []), '一次成功时不应有等待，且应返回 (结果, delays) 元组'",
            "state = {'n': 0}\n"
            "def fail_twice():\n"
            "    state['n'] += 1\n"
            "    if state['n'] < 3:\n"
            "        raise RetryableError('限流')\n"
            "    return 'done'",
            "log = []",
            "result, delays = retry_call(fail_twice, attempts=3, sleep=make_sleep(log))",
            "assert result == 'done', '第三次应该成功：%r' % (result,)",
            "assert state['n'] == 3, '应该调用 3 次，实际 %d 次' % state['n']",
            "assert log == [0.5, 1.0], '退避延迟应为 0.5、1.0，实际 %r' % (log,)",
            "log2 = []",
            "try:\n    retry_call(lambda: (_ for _ in ()).throw(RetryableError('一直失败')), attempts=3, sleep=make_sleep(log2))\n    raise AssertionError('次数用尽后应该抛出异常')\nexcept RetryableError:\n    pass",
            "assert log2 == [0.5, 1.0], '最后一次失败后不该再等待，实际 %r' % (log2,)",
            "calls = {'n': 0}\ndef fatal():\n    calls['n'] += 1\n    raise FatalError('密钥不对')",
            "log3 = []",
            "try:\n    retry_call(fatal, attempts=5, sleep=make_sleep(log3))\n    raise AssertionError('FatalError 应该直接抛出')\nexcept FatalError:\n    pass",
            "assert calls['n'] == 1, 'FatalError 不该重试，实际调用 %d 次' % calls['n']",
            "assert log3 == [], 'FatalError 不该有等待'",
            "log4 = []",
            "try:\n    retry_call(lambda: (_ for _ in ()).throw(ValueError('别的错')), attempts=4, sleep=make_sleep(log4))\n    raise AssertionError('其它异常也应该直接抛出')\nexcept ValueError:\n    pass",
            "assert log4 == [], '非 RetryableError 不该有等待'",
            "log5 = []",
            "retry_call(lambda: (_ for _ in ()).throw(RetryableError('x')), attempts=6, base_delay=1, max_delay=4, sleep=make_sleep(log5)) if False else None",
            "try:\n    retry_call(lambda: (_ for _ in ()).throw(RetryableError('x')), attempts=6, base_delay=1, max_delay=4, sleep=make_sleep(log5))\nexcept RetryableError:\n    pass",
            "assert log5 == [1, 2, 4, 4, 4], '指数退避应该封顶在 max_delay：%r' % (log5,)",
            "log6 = []",
            "assert retry_call(lambda: 42, attempts=1, sleep=make_sleep(log6))[0] == 42, 'attempts=1 时也应正常工作'",
        ],
        'explanation': (
            '指数退避（exponential backoff）是分布式系统的**基本功**。'
            '服务被限流时，成百上千个客户端如果立刻重试，'
            '会把服务彻底打垮（这就是「重试风暴」）；'
            '而按 0.5、1、2、4、8 秒错开，压力就被摊平了。\n\n'
            '三个设计点值得记：\n\n'
            '**一、区分可重试与不可重试。** '
            '`FatalError`（密钥错、参数错）重试一万次也没用，'
            '反而白白浪费额度、拖长用户等待。'
            '所以异常要分类，这是「把错误编码成类型」的价值。'
            '真实项目里还会区分 429（可重试）和 400（不可重试），'
            '本课程前面 `describe_error` 那题做的就是这件事。\n\n'
            '**二、退避必须封顶。** 不设 `max_delay` 的话，'
            '第 10 次重试要等 512 秒，用户体验堪比卡死。'
            '`min(max_delay, base * 2**n)` 一行搞定。\n\n'
            '**三、`sleep` 要可注入。** 这是本題最重要的工程技巧：'
            '如果函数内部写死 `time.sleep`，测试要么真的睡 3 秒（慢），'
            '要么只能测「有没有重试」而测不到「退避多久」（漏）。'
            '把副作用（等待、打印、网络）作为参数传进来，'
            '代码立刻变得可测——这个技巧叫「依赖注入」，'
            '你在 `ToolBox.now` 那题里已经用过一次了。\n\n'
            '`base_delay * (2 ** round_index)` 里用 `round_index`（从 0 开始）'
            '而不是「第几次重试」（从 1 开始），正好让第一次延迟等于 `base_delay`——'
            '**这里的 off-by-one 要特别小心**，'
            '写成 `2 ** (round_index + 1)` 就会变成 1、2、4，'
            '与文档不符。\n\n'
            '返回 `(结果, delays)` 而不是只返回结果，'
            '是为了让调用方能记录「这次调用退避了几次」——'
            '这个指标在生产监控里很有用：退避次数突然上升，'
            '往往意味上游出问题了。'
        ),
        'expected_output': "成功 [0.5, 1.0] 调用次数 3",
        'hints': ['延迟用 min(max_delay, base_delay * 2 ** n)，n 从 0 开始', '把等待函数作为参数传进来，测试时换成记录器就不会真的等'],
    },

    # ── 第 38 章 RAG 检索增强生成 ─────────────────────────
    {
        'id': 'ch38-01',
        'chapter_id': 38,
        'title': 'RAG 第一步：文本分块与相似度检索',
        'difficulty': 3,
        'tags': ['RAG', '分块', '余弦相似度'],
        'statement': (
            'RAG 的效果八成取决于「切块」和「检索」这两步。'
            '本題手写一遍，理解它们到底在做什么。\n\n'
            '1. `chunk_text(text, size=20, overlap=5)`：把长文本切成块。\n'
            '   - 先按换行切段，再把短段**拼到接近 `size` 个字符**为一块；\n'
            '   - 单段本身就超过 `size` 时，**硬切**成不超过 `size` 的块；\n'
            '   - 相邻块之间保留 `overlap` 个字符的重叠（简单实现：'
            '把上一块的末尾 `overlap` 个字符拼到下一块开头）；\n'
            '   - 返回块列表，**空文本返回空列表**，空行/空白段要被忽略\n\n'
            '2. `cosine(a, b)`：余弦相似度。\n'
            '   - 任一向量长度为 0 或模长为 0 时返回 `0.0`\n'
            '   - 计算公式：点积 / (模长之积)\n\n'
            '3. `search(query_vec, docs, top_k=2)`：\n'
            '   - `docs` 是 `[(id, vector), ...]`\n'
            '   - 返回按相似度**降序**排列的前 `top_k` 个 `(id, score)`；\n'
            '   - 相似度相同时按 id 的字符串序；\n'
            '   - `score` 保留 4 位小数\n\n'
            '最后用示例验证并打印。'
        ),
        'starter_code': 'import math\n\n\ndef chunk_text(text, size=20, overlap=5):\n    pass\n\n\ndef cosine(a, b):\n    pass\n\n\ndef search(query_vec, docs, top_k=2):\n    pass\n',
        'solution': (
            "import math\n"
            "\n"
            "\n"
            "def chunk_text(text, size=20, overlap=5):\n"
            "    paragraphs = [p.strip() for p in str(text or '').splitlines() if p.strip()]\n"
            "    chunks = []\n"
            "    current = ''\n"
            "    for paragraph in paragraphs:\n"
            "        while len(paragraph) > size:\n"
            "            piece, paragraph = paragraph[:size], paragraph[size:]\n"
            "            if current:\n"
            "                chunks.append(current)\n"
            "                current = ''\n"
            "            chunks.append(piece)\n"
            "        candidate = (current + ' ' + paragraph).strip() if current else paragraph\n"
            "        if len(candidate) <= size:\n"
            "            current = candidate\n"
            "        else:\n"
            "            chunks.append(current)\n"
            "            current = paragraph\n"
            "    if current:\n"
            "        chunks.append(current)\n"
            "    if overlap <= 0 or len(chunks) < 2:\n"
            "        return chunks\n"
            "    overlapped = [chunks[0]]\n"
            "    for index in range(1, len(chunks)):\n"
            "        tail = chunks[index - 1][-overlap:]\n"
            "        overlapped.append((tail + chunks[index])[:size])\n"
            "    return overlapped\n"
            "\n"
            "\n"
            "def cosine(a, b):\n"
            "    a = list(a or [])\n"
            "    b = list(b or [])\n"
            "    if not a or not b or len(a) != len(b):\n"
            "        return 0.0\n"
            "    dot = sum(x * y for x, y in zip(a, b))\n"
            "    norm_a = math.sqrt(sum(x * x for x in a))\n"
            "    norm_b = math.sqrt(sum(y * y for y in b))\n"
            "    if norm_a == 0 or norm_b == 0:\n"
            "        return 0.0\n"
            "    return dot / (norm_a * norm_b)\n"
            "\n"
            "\n"
            "def search(query_vec, docs, top_k=2):\n"
            "    scored = [(doc_id, round(cosine(query_vec, vector), 4)) for doc_id, vector in docs or []]\n"
            "    scored.sort(key=lambda item: (-item[1], str(item[0])))\n"
            "    return scored[:top_k]\n"
            "\n"
            "\n"
            "print(chunk_text('列表是有序容器\\n元组不可变\\n字典是键值对\\n集合去重', size=12, overlap=3))\n"
            "print(cosine([1, 0], [1, 0]), cosine([1, 0], [0, 1]), cosine([], [1]))\n"
            "docs = [('d1', [1, 0]), ('d2', [0.9, 0.1]), ('d3', [0, 1])]\n"
            "print(search([1, 0], docs, top_k=2))\n"
        ),
        'checks': [
            "assert chunk_text('', size=10) == [], '空文本应返回空列表'",
            "assert chunk_text('   \\n  \\n', size=10) == [], '全是空白应返回空列表'",
            "assert chunk_text('abc', size=10) == ['abc'], '短文本应整段成一块：%r' % (chunk_text('abc', size=10),)",
            "assert chunk_text('12345678901', size=5, overlap=0) == ['12345', '67890', '1'], '超长单段应被硬切成 size 长度：%r' % (chunk_text('12345678901', size=5, overlap=0),)",
            "chunks = chunk_text('aaa\\nbbb\\nccc', size=20, overlap=0)",
            "assert len(chunks) == 1, '总长不超上限时应合并成一块：%r' % (chunks,)",
            "joined = chunk_text('aaa\\nbbb\\nccc', size=20, overlap=0)[0]",
            "assert 'aaa' in joined and 'bbb' in joined and 'ccc' in joined, '合并时不能丢内容：%r' % (joined,)",
            "many = chunk_text('aaaaaaaaaa\\nbbbbbbbbbb\\ncccccccccc', size=12, overlap=0)",
            "assert len(many) > 1, '超过上限时应切多块：%r' % (many,)",
            "assert all(len(c) <= 12 for c in many), '每块长度都不能超过 size：%r' % (many,)",
            "ov = chunk_text('aaaaaaaaaa\\nbbbbbbbbbb\\ncccccccccc', size=12, overlap=3)",
            "assert all(len(c) <= 12 for c in ov), '带重叠时每块也不能超过 size：%r' % (ov,)",
            "assert ov[1].startswith(ov[0][-3:]), '第二块开头应带上重叠片段：%r' % (ov,)",
            "assert cosine([1, 0], [1, 0]) == 1.0, '相同向量的余弦相似度应为 1'",
            "assert abs(cosine([1, 0], [0, 1])) < 1e-9, '正交向量的余弦相似度应为 0'",
            "assert cosine([], [1, 0]) == 0.0, '空向量应返回 0.0'",
            "assert cosine([0, 0], [1, 0]) == 0.0, '零向量应返回 0.0（不能除零）'",
            "assert cosine([1, 0], [1, 0, 0]) == 0.0, '维度不同应返回 0.0 而不是报错'",
            "assert abs(cosine([1, 1], [2, 2]) - 1.0) < 1e-9, '同方向不同长度应得 1（余弦只看方向）'",
            "docs = [('d1', [1, 0]), ('d2', [0.9, 0.1]), ('d3', [0, 1])]",
            "hits = search([1, 0], docs, top_k=2)",
            "assert [h[0] for h in hits] == ['d1', 'd2'], '检索结果排序不对：%r' % (hits,)",
            "assert hits[0][1] == 1.0, '最相似的分数应为 1.0：%r' % (hits,)",
            "assert len(search([1, 0], docs, top_k=99)) == 3, 'top_k 超过文档数时应返回全部'",
            "assert search([1, 0], [], top_k=2) == [], '没有文档时应返回空列表'",
            "tie = [('b', [1, 0]), ('a', [1, 0])]",
            "assert [h[0] for h in search([1, 0], tie, top_k=2)] == ['a', 'b'], '分数相同时应按 id 排序：%r' % (search([1, 0], tie, top_k=2),)",
        ],
        'explanation': (
            '**分块（chunking）**是 RAG 里最被低估的一步。'
            '块切太大，检索出来的内容混杂，模型抓不到重点还浪费 token；'
            '切太小，一句话被劈成两半，语义就断了。'
            '所以真实系统里的分块通常是「按语义边界切 + 控制长度 + 保留重叠」，'
            '本題实现的就是这个骨架。\n\n'
            '**为什么要有 `overlap`？** 因为边界处的信息最容易被割裂。'
            '比如「Python 的列表是可变的」这句话如果正好被切在「列表是」和「可变的」之间，'
            '那么无论检索到哪一块，模型都看不全这个知识点。'
            '让相邻块共享 3~5 个字符（真实系统里是 50~100 个 token），'
            '就能保证跨边界的内容至少有一块是完整的。\n\n'
            '`overlapped.append((tail + chunks[index])[:size])` 里的 `[:size]` 不能省：'
            '加了重叠前缀之后长度会超，必须截回去——'
            '否则嵌入模型可能因为超长直接报错或被静默截断。\n\n'
            '**余弦相似度**只关心「方向」不关心「长度」：'
            '`cosine([1,1], [2,2])` 等于 1，'
            '所以文档长短不影响打分，这是它在文本检索里比欧氏距离更常用的原因。\n\n'
            '三个边界必须处理：**空向量**（`[]`）、**零向量**（`[0, 0]`）、'
            '**维度不一致**。前两个会让分母为 0 直接 `ZeroDivisionError`；'
            '维度不一致说明你把两个不同模型的向量拿来比了'
            '（换了嵌入模型却没重建索引，是 RAG 项目最常见的线上事故），'
            '这时返回 0 比抛异常更安全——至少服务不会挂。\n\n'
            '`sorted(..., key=lambda item: (-item[1], str(item[0])))` '
            '又用到了「负号降序 + 二级键」的组合：'
            '相似度降序、相同则按 id 升序。'
            '`str(item[0])` 是为了兼容 id 是数字的情况，'
            '避免 `int` 和 `str` 比较时报 `TypeError`。'
        ),
        'expected_output': "['列表是有序容器', '序容器元组不可变 字典是', '键值对集合去重']\n1.0 0.0 0.0\n[('d1', 1.0), ('d2', 0.9939)]",
        'hints': ['先按换行拆段，再把短段合并到不超过 size', '余弦相似度记住三种返回 0 的情况：空、零向量、维度不同'],
    },
]
