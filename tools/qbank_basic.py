"""题库 · 基础篇（第 1–14 章）配套代码练习。

每题都带 checks（断言），学生代码跑通断言才算通关；
参考答案本身也要能通过同一套断言，由 tools/test_question_bank.py 全量验证。

写法约定：
- statement 面向学生，必须写清「要定义什么名字的函数 / 变量」，否则断言等于猜谜。
- checks 只断言题面要求的东西，不夹带额外约束。
"""

QUESTIONS = [
    # ── 第 1 章 认识 Python 与开发环境 ──────────────────────
    {
        'id': 'ch01-01',
        'chapter_id': 1,
        'title': '用 print 排出你的名片',
        'difficulty': 1,
        'tags': ['print', '字符串'],
        'statement': (
            '用 3 行 `print()` 输出你的名片，三行分别是：\n\n'
            '1. 姓名（例如 `张三`）\n'
            '2. 专业与年级，用 `|` 分隔（例如 `大数据技术 | 大一`）\n'
            '3. 一句你想对 Python 说的话\n\n'
            '要求：第 2 行必须用字符串拼接（`+`）把两个字符串接起来，不能直接写成一整串。'
        ),
        'starter_code': '# 第 1 行：打印姓名\n\n# 第 2 行：用 + 拼接专业和年级，中间用 " | " 连接\n\n# 第 3 行：打印一句话\n',
        'solution': (
            "print('张三')\n"
            "major = '大数据技术'\n"
            "grade = '大一'\n"
            "print(major + ' | ' + grade)\n"
            "print('Python，我想用你做出真正有用的东西。')\n"
        ),
        'checks': [
            "assert '|' in _out, '第 2 行里没有出现 | 分隔符'",
            "assert len([l for l in _out.strip().splitlines() if l.strip()]) >= 3, 'print 的行数不足 3 行'",
        ],
        'explanation': (
            '`print()` 是 Python 最直白的输出工具，它会自动在末尾换行，所以三行 print 就是三行文字。\n\n'
            '字符串拼接用 `+`，注意 `+` 两边必须都是字符串——写成 `major + " | " + grade` 是三个字符串相加。\n\n'
            '常见坑：把数字和字符串直接相加会报 `TypeError`，比如 `"今年" + 18` 是错的，'
            '得写成 `"今年" + str(18)`。'
        ),
        'expected_output': '',
        'hints': ['字符串拼接：两个字符串之间放一个 + 号', '想在同一行输出多个东西，也可以 print(a, b)，但本题要求用 +'],
    },
    {
        'id': 'ch01-02',
        'chapter_id': 1,
        'title': '读懂报错：把三处错误改对',
        'difficulty': 2,
        'tags': ['报错', '调试', '语法'],
        'statement': (
            '下面这段代码运行到最后一行时会报错，请找出原因并改正，让程序完整跑通：\n\n'
            '```python\n'
            "print('开始检验')\n"
            "message = 'PyMaster 训练场'\n"
            "print('欢迎来到 ' + message)\n"
            "total = 3 + 4\n"
            "print('结果是 ' + total)\n"
            "print('结束')\n"
            '```\n\n'
            '要求：不改动前四行，只把最后的输出改成 '
            '`结果是 7`（提示：想想 `+` 两边需要什么类型）。'
        ),
        'starter_code': "print('开始检验')\nmessage = 'PyMaster 训练场'\nprint('欢迎来到 ' + message)\ntotal = 3 + 4\nprint('结果是 ' + total)\nprint('结束')\n",
        'solution': (
            "print('开始检验')\n"
            "message = 'PyMaster 训练场'\n"
            "print('欢迎来到 ' + message)\n"
            "total = 3 + 4\n"
            "print('结果是 ' + str(total))\n"
            "print('结束')\n"
        ),
        'checks': [
            "assert '结果是 7' in _out, '输出里没有出现「结果是 7」'",
            "assert '开始检验' in _out and '结束' in _out, '首尾两行输出丢了'",
        ],
        'explanation': (
            '这段代码真正的坑只有一个：`\'结果是 \' + total`。\n\n'
            '`+` 在 Python 里不是万能的：`3 + 4` 是数学加法，`"a" + "b"` 是字符串拼接，'
            '但 `"字" + 7` 无解——到底是把 7 当字符接上去，还是把字符串当数字求和？'
            'Python 的官方选择是直接报错，让你写清楚意图。\n\n'
            '所以显式转换：`str(7)` 得到 `"7"`。反向的操作是 `int("7")`。'
        ),
        'expected_output': '开始检验\n欢迎来到 PyMaster 训练场\n结果是 7\n结束',
        'hints': ['TypeError 通常意味着「类型不对」，把数字变成字符串试试 str()'],
    },

    # ── 第 2 章 变量、数据类型与输入输出 ─────────────────────
    {
        'id': 'ch02-01',
        'chapter_id': 2,
        'title': '四种类型各来一个',
        'difficulty': 1,
        'tags': ['变量', '类型'],
        'statement': (
            '定义四个变量并打印它们的类型：\n\n'
            '- `age`：整数，值为你的年龄\n'
            '- `height`：浮点数，值 1.75\n'
            '- `name`：字符串，值为 `PyMaster`\n'
            '- `is_student`：布尔值，值为 `True`\n\n'
            '然后用一行 `print` 输出每个变量的 `type()`，形式不限。\n\n'
            '**注意**：变量名必须完全一致，最后一行还要打印 `age + 1` 的结果。'
        ),
        'starter_code': 'age = \nheight = \nname = \nis_student = \n',
        'solution': (
            "age = 18\n"
            "height = 1.75\n"
            "name = 'PyMaster'\n"
            "is_student = True\n"
            "print(type(age), type(height), type(name), type(is_student))\n"
            "print(age + 1)\n"
        ),
        'checks': [
            "assert isinstance(age, int) and not isinstance(age, bool), 'age 必须是整数'",
            "assert isinstance(height, float), 'height 必须是浮点数'",
            "assert isinstance(name, str), 'name 必须是字符串'",
            "assert is_student is True, 'is_student 必须是 True'",
            "assert str(age + 1) in _out, '没有打印 age + 1 的结果'",
        ],
        'explanation': (
            'Python 的变量不用声明类型，赋值那一刻类型就定下来了——这叫动态类型。\n\n'
            '`type()` 可以随时查看一个值的类型。注意 Python 里布尔值 `True` 是 `bool`，'
            '它是 `int` 的子类，所以 `True + 1` 等于 2，这是面试常问的小知识。\n\n'
            '写代码时想让别人看懂，变量名要起得像人话：`age` 比 `a` 好一百倍。'
        ),
        'expected_output': '',
        'hints': ['type(值) 返回类型', '整数直接写 18，浮点数要带小数点'],
    },
    {
        'id': 'ch02-02',
        'chapter_id': 2,
        'title': '温度换算器（含类型转换）',
        'difficulty': 2,
        'tags': ['类型转换', '运算', 'round'],
        'statement': (
            '把摄氏度转成华氏度，公式：`F = C × 9 / 5 + 32`。\n\n'
            '要求：\n'
            '1. 定义变量 `celsius = 37.5`\n'
            '2. 计算得到 `fahrenheit`\n'
            '3. 打印一行：`37.5℃ = 99.5℉`（华氏度保留 1 位小数，用 `round(值, 1)`）\n\n'
            '再加做一步：把 `fahrenheit` 取整存进 `fahrenheit_int`（用 `int()` 截断）。'
        ),
        'starter_code': 'celsius = 37.5\nfahrenheit = \n',
        'solution': (
            "celsius = 37.5\n"
            "fahrenheit = celsius * 9 / 5 + 32\n"
            "fahrenheit_int = int(fahrenheit)\n"
            "print(str(celsius) + '℃ = ' + str(round(fahrenheit, 1)) + '℉')\n"
        ),
        'checks': [
            "assert abs(fahrenheit - 99.5) < 1e-6, '换算结果不对，检查公式是否写成了 C * 9 / 5 + 32'",
            "assert fahrenheit_int == 99, 'fahrenheit_int 应该是截断后的整数 99'",
            "assert '99.5' in _out, '输出里没有保留 1 位小数的 99.5'",
            "assert '℉' in _out, '输出里缺少 ℉ 符号'",
        ],
        'explanation': (
            '算术运算符优先级和数学一致：`*` `/` 先于 `+`。`celsius * 9 / 5 + 32` 从左到右算，'
            '得到 99.5，正好是体温的华氏度。\n\n'
            '`round(x, 1)` 四舍五入到 1 位小数，但注意它是「银行家舍入」：`round(2.5)` 得到 2 而不是 3。'
            '真正需要精确的金融计算要用 `decimal` 模块。\n\n'
            '`int()` 是**截断**不是四舍五入：`int(99.9)` 是 99，想要四舍五入得用 `round()`。'
        ),
        'expected_output': '37.5℃ = 99.5℉',
        'hints': ['公式就是 celsius * 9 / 5 + 32，照着写', '拼接字符串前记得 str() 转换'],
    },
    {
        'id': 'ch02-03',
        'chapter_id': 2,
        'title': 'f-string 格式化一张成绩单',
        'difficulty': 1,
        'tags': ['f-string', '格式化'],
        'statement': (
            '已知 `name = "李雷"`、`score = 92.567`，请用 **f-string** 打印两行：\n\n'
            '```\n'
            '姓名：李雷\n'
            '成绩：92.57 分\n'
            '```\n\n'
            '要求成绩保留 2 位小数，并且**必须用 f-string 实现**（形如 `f"..."`），'
            '不能用 `round()` 或 `str.format()`。'
        ),
        'starter_code': 'name = "李雷"\nscore = 92.567\n# 用 f-string 打印两行\n',
        'solution': (
            'name = "李雷"\n'
            'score = 92.567\n'
            'print(f"姓名：{name}")\n'
            'print(f"成绩：{score:.2f} 分")\n'
        ),
        'checks': [
            "assert 'f\"' in _src or chr(102) + chr(39) in _src, '本题要求使用 f-string（形如 f + 引号 的字符串前缀）'",
            "assert '姓名：李雷' in _out, '第一行输出不对'",
            "assert '成绩：92.57 分' in _out, '第二行输出不对，注意保留 2 位小数且空格正确'",
        ],
        'explanation': (
            'f-string 是 Python 3.6 之后推荐的格式化方式：在字符串前加 `f`，'
            '里面用 `{}` 直接嵌入变量，比 `%` 和 `.format()` 都更好读。\n\n'
            '`{score:.2f}` 里的 `.2f` 是格式说明符：`f` 表示定点小数，`.2` 表示两位小数，'
            '而且它是**四舍五入**的，92.567 变成 92.57。\n\n'
            '常用格式符：`:.0f` 不要小数、`:,` 千分位、`:.2%` 百分比、`:<10` 左对齐补空格。'
        ),
        'expected_output': '姓名：李雷\n成绩：92.57 分',
        'hints': ['f"成绩：{score:.2f} 分" —— 冒号后面是格式说明符'],
    },
    {
        'id': 'ch02-04',
        'chapter_id': 2,
        'title': '交换两个变量（三种写法）',
        'difficulty': 2,
        'tags': ['赋值', '元组解包'],
        'statement': (
            '已知 `a = 1`、`b = 2`，把它们交换后打印 `a=2 b=1`。\n\n'
            '要求：**不允许**引入第三个变量（不许写 `temp = a`），'
            '请用 Python 特有的多重赋值一行搞定。\n\n'
            '打印格式必须是 `a=2 b=1`。'
        ),
        'starter_code': 'a = 1\nb = 2\n# 交换 a 和 b\n\nprint(f"a={a} b={b}")\n',
        'solution': 'a = 1\nb = 2\na, b = b, a\nprint(f"a={a} b={b}")\n',
        'checks': [
            "assert 'temp' not in _src, '本题不允许用第三个变量'",
            "assert a == 2 and b == 1, '交换没有生效：现在 a=%r b=%r' % (a, b)",
            "assert 'a=2 b=1' in _out, '打印格式应为 a=2 b=1'",
        ],
        'explanation': (
            '`a, b = b, a` 看起来像魔法，其实是**元组解包**：\n\n'
            '右边 `b, a` 先被打包成一个元组 `(2, 1)`，然后按位置依次赋给左边的 `a, b`。'
            '因为右边先算完，所以不存在「a 被覆盖后 b 拿不到旧值」的问题。\n\n'
            '其他语言的经典写法要用临时变量或异或技巧，Python 这一行是官方推荐写法，'
            '同样适用于 `x, y, z = 1, 2, 3` 这样的批量赋值。'
        ),
        'expected_output': 'a=2 b=1',
        'hints': ['Python 支持 a, b = b, a'],
    },

    # ── 第 3 章 流程控制：条件与循环 ────────────────────────
    {
        'id': 'ch03-01',
        'chapter_id': 3,
        'title': '成绩等级判定器',
        'difficulty': 1,
        'tags': ['if', 'elif', 'else'],
        'statement': (
            '定义函数 `grade(score)`，根据分数返回等级字符串：\n\n'
            '- 90 分及以上：`优秀`\n'
            '- 80 ~ 89：`良好`\n'
            '- 60 ~ 79：`及格`\n'
            '- 60 以下：`不及格`\n'
            '- 分数不在 0~100 范围内：返回 `分数无效`\n\n'
            '然后用 `grade(95)`、`grade(83)`、`grade(60)`、`grade(59)`、`grade(120)` 各调一次并打印。'
        ),
        'starter_code': 'def grade(score):\n    # 在这里写判断\n    pass\n',
        'solution': (
            "def grade(score):\n"
            "    if not isinstance(score, (int, float)):\n"
            "        return '分数无效'\n"
            "    if score < 0 or score > 100:\n"
            "        return '分数无效'\n"
            "    if score >= 90:\n"
            "        return '优秀'\n"
            "    elif score >= 80:\n"
            "        return '良好'\n"
            "    elif score >= 60:\n"
            "        return '及格'\n"
            "    else:\n"
            "        return '不及格'\n"
            "\n"
            "for s in (95, 83, 60, 59, 120):\n"
            "    print(s, grade(s))\n"
        ),
        'checks': [
            "assert grade(95) == '优秀', 'grade(95) 应为 优秀'",
            "assert grade(90) == '优秀', '边界值 90 应算优秀'",
            "assert grade(89) == '良好', 'grade(89) 应为 良好'",
            "assert grade(80) == '良好', '边界值 80 应算良好'",
            "assert grade(60) == '及格', '边界值 60 应算及格'",
            "assert grade(59) == '不及格', 'grade(59) 应为 不及格'",
            "assert grade(120) == '分数无效', '越界分数应返回 分数无效'",
            "assert grade(-5) == '分数无效', '负数分数应返回 分数无效'",
        ],
        'explanation': (
            '`if / elif / else` 自上而下依次判断，**只要有一个条件成立，剩下的全部跳过**。\n\n'
            '这就是为什么 `elif score >= 80` 不用再写 `score < 90`：能走到这一步，'
            '说明上面 `score >= 90` 已经不成立了，分数必然小于 90。把条件写「干净」'
            '可以减少出错，也让代码更好读。\n\n'
            '边界值最容易错。写区间判断时养成习惯：把 `>=` 和 `>` 想清楚，'
            '然后专门测一遍边界（90、80、60 这些点）。'
        ),
        'expected_output': '',
        'hints': ['先用 if 判断 >= 90，再依次用 elif 往下判断', '越界检查放在最前面最省事'],
    },
    {
        'id': 'ch03-02',
        'chapter_id': 3,
        'title': '九九乘法表（嵌套循环）',
        'difficulty': 2,
        'tags': ['for', 'range', '嵌套循环'],
        'statement': (
            '用**嵌套 for 循环**打印九九乘法表，共 9 行，第 i 行有 i 个算式。\n\n'
            '每个算式格式为 `1×1=1`（乘号用中文 `×`），算式之间用**两个空格**分隔，'
            '行尾不要多余空格。\n\n'
            '第一行必须是 `1×1=1`，最后一行必须以 `9×9=81` 结尾。'
        ),
        'starter_code': 'for i in range(1, 10):\n    # 内层循环从 1 到 i\n    pass\n',
        'solution': (
            "for i in range(1, 10):\n"
            "    row = []\n"
            "    for j in range(1, i + 1):\n"
            "        row.append(f'{j}×{i}={j * i}')\n"
            "    print('  '.join(row))\n"
        ),
        'checks': [
            "lines = [l for l in _out.strip().splitlines() if l.strip()]",
            "assert len(lines) == 9, '应输出 9 行，实际 %d 行' % len(lines)",
            "assert lines[0] == '1×1=1', '第一行应为 1×1=1，实际 %r' % lines[0]",
            "assert lines[-1].endswith('9×9=81'), '最后一行应以 9×9=81 结尾'",
            "assert lines[2].startswith('1×3=3') and lines[2].endswith('3×3=9'), '第三行内容不对'",
            "assert '  ' in lines[1], '算式之间应该用两个空格分隔'",
        ],
        'explanation': (
            '外层循环控制「行」，内层循环控制「这一行有几个算式」。第 i 行有 i 个算式，'
            '所以内层是 `range(1, i + 1)`。\n\n'
            '为什么是 `i + 1`？因为 `range(1, i)` 只到 `i - 1`。这是初学者最常见的 off-by-one 错误，'
            '记住一句话：**range 的右端点是取不到的**。\n\n'
            '行尾不要多余空格，是因为 `\'  \'.join(row)` 只在元素之间插分隔符，'
            '比循环里拼字符串再判断「是不是最后一个」优雅得多。'
        ),
        'expected_output': '1×1=1\n1×2=2  2×2=4\n1×3=3  2×3=6  3×3=9',
        'hints': ['外层 for i in range(1, 10)，内层 for j in range(1, i+1)', "用 '  '.join(列表) 拼一行，天然不会多出尾部空格"],
    },
    {
        'id': 'ch03-03',
        'chapter_id': 3,
        'title': '猜数字：while 循环与 break',
        'difficulty': 2,
        'tags': ['while', 'break', 'continue'],
        'statement': (
            '模拟猜数字游戏：答案是 42，猜测序列固定为 `[50, 30, 42]`。\n\n'
            '要求用 `while` 循环依次取出猜测值（用索引，不要用 for）：\n\n'
            '- 猜大了打印 `50 太大了`\n'
            '- 猜小了打印 `30 太小了`\n'
            '- 猜中打印 `42 猜对了，共猜了 3 次`，然后立刻 `break`\n\n'
            '最后把猜测次数存进变量 `attempts`。'
        ),
        'starter_code': 'answer = 42\nguesses = [50, 30, 42]\nindex = 0\nattempts = 0\n# 用 while 循环写\n',
        'solution': (
            "answer = 42\n"
            "guesses = [50, 30, 42]\n"
            "index = 0\n"
            "attempts = 0\n"
            "while index < len(guesses):\n"
            "    guess = guesses[index]\n"
            "    attempts += 1\n"
            "    if guess > answer:\n"
            "        print(f'{guess} 太大了')\n"
            "    elif guess < answer:\n"
            "        print(f'{guess} 太小了')\n"
            "    else:\n"
            "        print(f'{guess} 猜对了，共猜了 {attempts} 次')\n"
            "        break\n"
            "    index += 1\n"
        ),
        'checks': [
            "assert '50 太大了' in _out, '缺少「50 太大了」这行'",
            "assert '30 太小了' in _out, '缺少「30 太小了」这行'",
            "assert '42 猜对了，共猜了 3 次' in _out, '猜中提示不对，注意次数应为 3'",
            "assert attempts == 3, 'attempts 应为 3，实际 %r' % (attempts,)",
            "assert _out.count('猜对了') == 1, '猜中后应立刻 break，只能出现一次猜对提示'",
        ],
        'explanation': (
            '`while` 和 `for` 的区别在于**谁负责推进**：`for` 自动从序列里取下一个，'
            '`while` 要你自己让条件趋向结束（这里是 `index += 1`）。忘了这一步就是死循环。\n\n'
            '`break` 是「立刻跳出整个循环」，所以猜中后不会再有第四次循环。\n'
            '如果只想跳过本次、继续下一次，用 `continue`。\n\n'
            '注意本解法把 `index += 1` 放在 `break` 之后——因为 `break` 了就不需要再自增。'
            '这是可以接受的写法，但要注意别把自增写在 `continue` 后面，那样会死循环。'
        ),
        'expected_output': '50 太大了\n30 太小了\n42 猜对了，共猜了 3 次',
        'hints': ['while index < len(guesses): 每次循环末尾 index += 1', '猜中以后 break 跳出循环'],
    },
    {
        'id': 'ch03-04',
        'chapter_id': 3,
        'title': '找出 1~100 里的所有质数',
        'difficulty': 2,
        'tags': ['循环', 'break', '数学'],
        'statement': (
            '把 1 到 100 之间的所有质数收集到一个列表 `primes` 里并打印。\n\n'
            '要求：\n'
            '- 用 `for` 循环遍历候选数，用内层循环判断因子\n'
            '- 一旦发现能整除就 `break`，不要白跑完整个内层循环\n'
            '- 打印格式：`质数共 25 个：[2, 3, 5, 7, ...]`\n\n'
            '（100 以内的质数一共 25 个，可以用这个数字自检。）'
        ),
        'starter_code': 'primes = []\nfor n in range(1, 101):\n    # 判断 n 是不是质数\n    pass\n',
        'solution': (
            "primes = []\n"
            "for n in range(1, 101):\n"
            "    if n < 2:\n"
            "        continue\n"
            "    is_prime = True\n"
            "    for d in range(2, int(n ** 0.5) + 1):\n"
            "        if n % d == 0:\n"
            "            is_prime = False\n"
            "            break\n"
            "    if is_prime:\n"
            "        primes.append(n)\n"
            "print(f'质数共 {len(primes)} 个：{primes}')\n"
        ),
        'checks': [
            "assert len(primes) == 25, '100 以内的质数应有 25 个，实际 %d 个' % len(primes)",
            "assert primes[:5] == [2, 3, 5, 7, 11], '前几个质数不对'",
            "assert primes[-1] == 97, '最大的质数应该是 97'",
            "assert '质数共 25 个' in _out, '打印格式应为「质数共 25 个：[...]」'",
        ],
        'explanation': (
            '判断质数的关键是「能不能被 2 到 √n 之间的某数整除」。\n\n'
            '为什么只需要试到 √n？因为如果 n 有一个大于 √n 的因子，'
            '那必定还有一个小于 √n 的因子与它配对（`n = a × b` 里总有一个 ≤ √n）。'
            '所以 `range(2, int(n ** 0.5) + 1)` 就够，100 以内的数最多试到 10。\n\n'
            '这里 `break` 的价值很大：一旦发现 8 能被 2 整除，就没必要再试 3、4、5……'
            '这是「提前退出」思维在算法里的第一次登场，后面还会反复用到。\n\n'
            '另外 `n < 2` 时 `continue` 直接跳过，比在内层再判断一次简洁。'
        ),
        'expected_output': '质数共 25 个：[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]',
        'hints': ['1 不是质数，n < 2 的要跳过', '内层从 2 试到 int(n ** 0.5) + 1 就够'],
    },

    # ── 第 4 章 字符串深入 ─────────────────────────────────
    {
        'id': 'ch04-01',
        'chapter_id': 4,
        'title': '切片三连：反转、取偶数位、取尾部',
        'difficulty': 2,
        'tags': ['字符串', '切片'],
        'statement': (
            '已知 `s = "PyMaster2026"`，用**切片**（不要用循环、不要用 reversed）得到三个结果：\n\n'
            '1. `reversed_s`：整个字符串反转\n'
            '2. `even_chars`：所有偶数下标（0,2,4,...）的字符拼成的串\n'
            '3. `last_three`：最后三个字符\n\n'
            '最后把三个结果打印出来，一行一个。'
        ),
        'starter_code': 's = "PyMaster2026"\nreversed_s = \neven_chars = \nlast_three = \n',
        'solution': (
            's = "PyMaster2026"\n'
            'reversed_s = s[::-1]\n'
            'even_chars = s[::2]\n'
            'last_three = s[-3:]\n'
            'print(reversed_s)\n'
            'print(even_chars)\n'
            'print(last_three)\n'
        ),
        'checks': [
            "assert reversed_s == '6202retsaMyP', '反转结果不对：%r' % (reversed_s,)",
            "assert even_chars == 'PMse22', '偶数位字符不对：%r' % (even_chars,)",
            "assert last_three == '026', '最后三个字符不对：%r' % (last_three,)",
        ],
        'explanation': (
            '切片语法是 `s[开始:结束:步长]`，三者都可以省略：\n\n'
            '- `s[::-1]`：步长 -1 表示从右往左，天然实现反转；\n'
            '- `s[::2]`：从 0 开始每 2 个取一个，也就是所有偶数下标；\n'
            '- `s[-3:]`：负数下标从尾部数，`-1` 是最后一个字符。\n\n'
            '切片的好处是**不会越界报错**：`"abc"[10:]` 只是空字符串。'
            '这在处理不定长输入时非常好用。'
        ),
        'expected_output': '6202retsaMyP\nyatro02\n026',
        'hints': ['切片格式 s[开始:结束:步长]', '反转是 s[::-1]，取最后三个是 s[-3:]'],
    },
    {
        'id': 'ch04-02',
        'chapter_id': 4,
        'title': '判断回文（忽略大小写和空格）',
        'difficulty': 2,
        'tags': ['字符串', '方法', '算法'],
        'statement': (
            '定义函数 `is_palindrome(text)`，判断字符串是否是回文。\n\n'
            '规则：\n'
            '- 忽略大小写（`A` 和 `a` 视为相同）\n'
            '- 忽略空格\n'
            '- 空字符串和单字符都算回文\n\n'
            '要求先清洗字符串再比较，不能用循环逐字符比对（用切片反转即可）。\n\n'
            '然后对 `"A man a plan a canal Panama"`、`"hello"`、`""` 各调一次并打印结果。'
        ),
        'starter_code': 'def is_palindrome(text):\n    # 先清洗，再比较\n    pass\n',
        'solution': (
            "def is_palindrome(text):\n"
            "    cleaned = text.replace(' ', '').lower()\n"
            "    return cleaned == cleaned[::-1]\n"
            "\n"
            "for t in ('A man a plan a canal Panama', 'hello', ''):\n"
            "    print(repr(t), is_palindrome(t))\n"
        ),
        'checks': [
            "assert is_palindrome('A man a plan a canal Panama') is True, '经典回文句应判为 True'",
            "assert is_palindrome('hello') is False, 'hello 不是回文'",
            "assert is_palindrome('') is True, '空字符串应算回文'",
            "assert is_palindrome('上海自来水来自海上') is True, '中文回文也应支持'",
            "assert is_palindrome('AbBa') is True, '大小写不同的 AbBa 应算回文'",
            "assert is_palindrome('ab ba') is True, '中间有空格应被忽略'",
        ],
        'explanation': (
            '「清洗 + 比较」是字符串题的标准两步：先把干扰因素（空格、大小写）去掉，'
            '再判断核心性质。\n\n'
            '`cleaned == cleaned[::-1]` 用切片反转来比较，比双指针循环短得多，'
            '而且没有边界错误的风险。\n\n'
            '`lower()` 只处理英文字母，中文没有大小写，所以中文回文天然可用。'
            '如果要去掉所有标点，可以用 `str.isalnum()` 过滤：\n'
            '`cleaned = \'\'.join(c for c in text if c.isalnum()).lower()`。'
        ),
        'expected_output': "'A man a plan a canal Panama' True\n'hello' False\n'' True",
        'hints': ["用 replace(' ', '') 去空格，lower() 统一小写", '比较时用 cleaned == cleaned[::-1]'],
    },
    {
        'id': 'ch04-03',
        'chapter_id': 4,
        'title': '统计一句话里的单词',
        'difficulty': 2,
        'tags': ['split', '字典', '字符串方法'],
        'statement': (
            '已知 `sentence = "the quick brown fox jumps over the lazy dog the fox"`。\n\n'
            '要求：\n'
            '1. 用 `split()` 切词，存进 `words` 列表\n'
            '2. 统计每个单词出现次数，存进字典 `counter`\n'
            '3. 找出出现最多的单词和次数，存进 `top_word` 和 `top_count`\n'
            '4. 打印：`共 11 个单词，最多的是 the（3 次）`'
        ),
        'starter_code': 'sentence = "the quick brown fox jumps over the lazy dog the fox"\nwords = \ncounter = {}\n',
        'solution': (
            'sentence = "the quick brown fox jumps over the lazy dog the fox"\n'
            "words = sentence.split()\n"
            "counter = {}\n"
            "for w in words:\n"
            "    counter[w] = counter.get(w, 0) + 1\n"
            "top_word = max(counter, key=counter.get)\n"
            "top_count = counter[top_word]\n"
            "print(f'共 {len(words)} 个单词，最多的是 {top_word}（{top_count} 次）')\n"
        ),
        'checks': [
            "assert len(words) == 11, '单词数应为 11，实际 %d' % len(words)",
            "assert counter.get('the') == 3, 'the 应出现 3 次'",
            "assert counter.get('fox') == 2, 'fox 应出现 2 次'",
            "assert top_word == 'the' and top_count == 3, '出现最多的应为 the 3 次'",
            "assert '共 11 个单词，最多的是 the（3 次）' in _out, '打印格式不对'",
        ],
        'explanation': (
            '`split()` 不带参数时按任意空白切分，还会自动处理连续空格，'
            '比自己写循环靠谱。\n\n'
            '计数的核心是 `counter[w] = counter.get(w, 0) + 1`：`dict.get(key, 默认值)` '
            '在键不存在时返回默认值，避免 `KeyError`。这是最常用的计数字典写法。\n\n'
            '找最大值用 `max(counter, key=counter.get)`——注意这里比较的是**键**，'
            '但排序依据是**值**（`key=` 参数指定排序函数）。如果直接写 `max(counter)` '
            '会得到按字母序最大的键，那是另一个意思。'
        ),
        'expected_output': '共 11 个单词，最多的是 the（3 次）',
        'hints': ['split() 不传参数按空白切', 'counter.get(w, 0) + 1 是标准计数写法'],
    },
    {
        'id': 'ch04-04',
        'chapter_id': 4,
        'title': '把驼峰命名转成下划线命名',
        'difficulty': 3,
        'tags': ['字符串', '循环', '实际应用'],
        'statement': (
            '定义函数 `snake_case(name)`，把驼峰命名转成下划线命名：\n\n'
            '- `"getUserName"` → `"get_user_name"`\n'
            '- `"HTTPServer"` → `"http_server"`\n'
            '- `"parseHTML"` → `"parse_html"`\n'
            '- `"already_snake"` → `"already_snake"`\n\n'
            '规则：遇到大写字母就在前面加 `_` 并转小写；连续大写视为一个词；'
            '结果开头不能有下划线，也不能出现连续两个下划线。\n\n'
            '这是真实工程里会遇到的活——把 Java 风格的接口字段转成 Python 风格。'
        ),
        'starter_code': 'def snake_case(name):\n    # 遍历字符，遇到大写就加下划线\n    pass\n',
        'solution': (
            "def snake_case(name):\n"
            "    out = []\n"
            "    for i, ch in enumerate(name):\n"
            "        if ch.isupper():\n"
            "            # 前一个字符是小写/数字，或者后面还有小写字母，才断词\n"
            "            prev = name[i - 1] if i > 0 else ''\n"
            "            nxt = name[i + 1] if i + 1 < len(name) else ''\n"
            "            need_break = i > 0 and (prev.islower() or prev.isdigit() or (nxt.islower() and prev.isupper()))\n"
            "            if need_break:\n"
            "                out.append('_')\n"
            "            out.append(ch.lower())\n"
            "        else:\n"
            "            out.append(ch)\n"
            "    result = ''.join(out)\n"
            "    while '__' in result:\n"
            "        result = result.replace('__', '_')\n"
            "    return result.strip('_')\n"
            "\n"
            "for n in ('getUserName', 'HTTPServer', 'parseHTML', 'already_snake'):\n"
            "    print(n, '->', snake_case(n))\n"
        ),
        'checks': [
            "assert snake_case('getUserName') == 'get_user_name', 'getUserName 转换不对：%r' % snake_case('getUserName')",
            "assert snake_case('HTTPServer') == 'http_server', 'HTTPServer 转换不对：%r' % snake_case('HTTPServer')",
            "assert snake_case('parseHTML') == 'parse_html', 'parseHTML 转换不对：%r' % snake_case('parseHTML')",
            "assert snake_case('already_snake') == 'already_snake', 'already_snake 应保持不变'",
            "assert snake_case('a') == 'a' and snake_case('A') == 'a', '单字符处理不对'",
            "assert snake_case('userID') == 'user_id', 'userID 转换不对：%r' % snake_case('userID')",
        ],
        'explanation': (
            '这道题的难点在「连续大写」：`HTTPServer` 要拆成 `http` + `server`，'
            '断点不是第一个大写字母 H，而是 **S**（因为 S 后面跟着小写 erver）。\n\n'
            '所以判断规则是：当前字符是大写，且满足以下任一条件就断词——\n'
            '1. 前一个字符是小写或数字（如 `getU` 的 U）；\n'
            '2. 前一个是大写、后面是小写（如 `HTTPS` 的 S）。\n\n'
            '第二种情况容易漏，漏了就会得到 `h_t_t_p_server`。\n\n'
            '最后用 `while` 循环清理连续下划线、再 `strip("_")` 去掉首尾，'
            '是因为前两步的规则叠加后可能产生 `_` 或 `__`。'
        ),
        'expected_output': 'getUserName -> get_user_name\nHTTPServer -> http_server\nparseHTML -> parse_html\nalready_snake -> already_snake',
        'hints': ['用 enumerate 拿到下标，需要看前一个和后面一个字符', 'HTTPServer 的断点在 S，不在 H'],
    },

    # ── 第 5 章 数据结构（上）：列表与元组 ──────────────────
    {
        'id': 'ch05-01',
        'chapter_id': 5,
        'title': '列表增删改查一条龙',
        'difficulty': 1,
        'tags': ['列表', 'append', 'remove', 'insert'],
        'statement': (
            '从 `fruits = ["apple", "banana"]` 出发，依次完成：\n\n'
            '1. 末尾追加 `"cherry"`（用 `append`）\n'
            '2. 在开头插入 `"mango"`（用 `insert`）\n'
            '3. 删除 `"banana"`（用 `remove`）\n'
            '4. 把 `"apple"` 改成 `"APPLE"`（用下标赋值）\n'
            '5. 打印最终列表和它的长度\n\n'
            '最终结果应该是 `[\'mango\', \'APPLE\', \'cherry\']`，长度 3。'
        ),
        'starter_code': 'fruits = ["apple", "banana"]\n# 依次完成 1~5 步\nprint(fruits)\n',
        'solution': (
            'fruits = ["apple", "banana"]\n'
            'fruits.append("cherry")\n'
            'fruits.insert(0, "mango")\n'
            'fruits.remove("banana")\n'
            'fruits[fruits.index("apple")] = "APPLE"\n'
            'print(fruits)\n'
            'print(len(fruits))\n'
        ),
        'checks': [
            "assert fruits == ['mango', 'APPLE', 'cherry'], '最终列表不对：%r' % (fruits,)",
            "assert '3' in _out, '最后应打印长度 3'",
        ],
        'explanation': (
            '四个操作各有分工：\n\n'
            '- `append(x)`：末尾追加，**效率最高**；\n'
            '- `insert(i, x)`：插入到指定位置，后面的元素要整体后移（列表越长越慢）；\n'
            '- `remove(x)`：按**值**删除第一个匹配项，值不存在会抛 `ValueError`；\n'
            '- `lst[i] = x`：按下标改，这是唯一能直接改值的方式。\n\n'
            '注意 `remove("banana")` 和 `del fruits[1]` 的区别：前者按值找，后者按下标删。'
            '如果你说「删掉第二个」，那就该用 `del` 或 `pop(1)`。'
        ),
        'expected_output': "['mango', 'APPLE', 'cherry']\n3",
        'hints': ['列表的 index() 可以拿到值的下标', 'insert(0, x) 是插到最前面'],
    },
    {
        'id': 'ch05-02',
        'chapter_id': 5,
        'title': '成绩排序与统计',
        'difficulty': 2,
        'tags': ['列表', '排序', 'statistics'],
        'statement': (
            '已知 `scores = [88, 72, 95, 61, 88, 79, 100, 54]`。\n\n'
            '要求（不许手写循环求和/求平均，尽量用内置函数）：\n'
            '1. 排序后的新列表 `sorted_scores`（从低到高），原列表不要被改\n'
            '2. 最高分 `top`、最低分 `low`\n'
            '3. 平均分 `avg`（保留 1 位小数）\n'
            '4. 高于平均分的人数 `above_avg_count`\n'
            '5. 打印：`最高 100 最低 54 平均 79.6 高于平均 4 人`\n\n'
            '（平均分是 79.6，凡是严格大于它的都算「高于平均」——先把数算对再写代码。）'
        ),
        'starter_code': 'scores = [88, 72, 95, 61, 88, 79, 100, 54]\nsorted_scores = \n',
        'solution': (
            "scores = [88, 72, 95, 61, 88, 79, 100, 54]\n"
            "sorted_scores = sorted(scores)\n"
            "top = max(scores)\n"
            "low = min(scores)\n"
            "avg = round(sum(scores) / len(scores), 1)\n"
            "above_avg_count = sum(1 for s in scores if s > avg)\n"
            "print(f'最高 {top} 最低 {low} 平均 {avg} 高于平均 {above_avg_count} 人')\n"
        ),
        'checks': [
            "assert sorted_scores == [54, 61, 72, 79, 88, 88, 95, 100], '排序结果不对'",
            "assert scores[0] == 88, '原列表被改动了：sorted() 不会改原列表，sort() 才会'",
            "assert top == 100 and low == 54, '最高/最低分不对'",
            "assert abs(avg - 79.6) < 0.05, '平均分应为 79.6，实际 %r' % (avg,)",
            "assert above_avg_count == 4, '高于平均分的应有 4 人（88/95/88/100），实际 %r' % (above_avg_count,)",
            "assert '平均 79.6' in _out, '打印格式不对'",
        ],
        'explanation': (
            '`sorted(lst)` 返回**新列表**，`lst.sort()` 改**原列表**——这是最容易踩的坑之一，'
            '面试也爱问。需要原顺序时用 `sorted()`。\n\n'
            '求和、最大值、最小值、长度都是内置函数 `sum` / `max` / `min` / `len`，'
            '比手写循环快得多（它们是 C 实现的）也更短。\n\n'
            '`sum(1 for s in scores if s > avg)` 这个写法值得记住：'
            '生成器表达式 + sum，可以统计「满足条件的元素个数」，'
            '不用先建一个临时列表。'
        ),
        'expected_output': '最高 100 最低 54 平均 79.6 高于平均 5 人',
        'hints': ['sorted() 返回新列表，sort() 改自己', 'sum(1 for x in ... if 条件) 可以数个数'],
    },
    {
        'id': 'ch05-03',
        'chapter_id': 5,
        'title': '去掉列表里的重复项（保持顺序）',
        'difficulty': 2,
        'tags': ['列表', '集合', '去重'],
        'statement': (
            '已知 `data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]`。\n\n'
            '定义函数 `dedupe(items)`，返回去重后的列表，并**保持元素第一次出现的顺序**。\n\n'
            '要求：内层查重必须用**集合**（O(1) 查找），不能写 `if x not in result` '
            '这种列表查找（那是 O(n)，大数据量下会慢到没法用）。\n\n'
            '然后打印 `dedupe(data)` 的结果和长度。'
        ),
        'starter_code': 'data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]\ndef dedupe(items):\n    pass\n',
        'solution': (
            "data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]\n"
            "def dedupe(items):\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for item in items:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
            "\n"
            "print(dedupe(data))\n"
            "print(len(dedupe(data)))\n"
        ),
        'checks': [
            "assert dedupe(data) == [3, 1, 4, 5, 9, 2, 6], '去重结果或顺序不对：%r' % (dedupe(data),)",
            "assert dedupe([]) == [], '空列表应返回空列表'",
            "assert dedupe(['a', 'a', 'a']) == ['a'], '重复元素只应保留一个'",
            "assert 'set()' in _src, '本题要求用集合做查重'",
        ],
        'explanation': (
            '为什么不能直接写 `list(set(data))`？因为集合是**无序**的，'
            '`list(set(...))` 得到的顺序每次都可能不一样，输出不稳定。\n\n'
            '正确做法是「双结构」：列表负责**保序**，集合负责**快速判重**。\n'
            '`item not in seen` 在集合里是 O(1)，在列表里是 O(n)，\n'
            '一万条数据下这是「瞬间」和「卡一下」的区别。\n\n'
            '如果确定不需要保序（比如只是想去重后做统计），`set()` 一行就够了。'
        ),
        'expected_output': '[3, 1, 4, 5, 9, 2, 6]\n7',
        'hints': ['准备一个 set 记录见过的元素，一个 list 保存结果', '用集合判重才能保住性能'],
    },
    {
        'id': 'ch05-04',
        'chapter_id': 5,
        'title': '元组解包：把坐标列表拆开',
        'difficulty': 2,
        'tags': ['元组', '解包', 'zip'],
        'statement': (
            '已知若干二维坐标：`points = [(1, 2), (3, 4), (5, 6), (7, 8)]`。\n\n'
            '要求：\n'
            '1. 把它们拆成两个列表 `xs` 和 `ys`（提示：`zip(*points)`）\n'
            '2. 用 `*` 解包取出第一个点和剩余的点\n'
            '3. 计算 `xs` 的最大值和 `ys` 的最小值\n'
            '4. 打印：`xs=[1, 3, 5, 7] ys=[2, 4, 6, 8] 最大x=7 最小y=2`'
        ),
        'starter_code': 'points = [(1, 2), (3, 4), (5, 6), (7, 8)]\nxs, ys = \n',
        'solution': (
            "points = [(1, 2), (3, 4), (5, 6), (7, 8)]\n"
            "xs, ys = zip(*points)\n"
            "xs = list(xs)\n"
            "ys = list(ys)\n"
            "first, *rest = points\n"
            "print(f'xs={xs} ys={ys} 最大x={max(xs)} 最小y={min(ys)}')\n"
        ),
        'checks': [
            "assert xs == [1, 3, 5, 7], 'xs 不对：%r' % (xs,)",
            "assert ys == [2, 4, 6, 8], 'ys 不对：%r' % (ys,)",
            "assert first == (1, 2), 'first 应为第一个点 (1, 2)'",
            "assert rest == [(3, 4), (5, 6), (7, 8)], 'rest 应为剩余三个点'",
            "assert '最大x=7 最小y=2' in _out, '打印格式不对'",
        ],
        'explanation': (
            '`zip(*points)` 里的 `*` 是**解包**：把 `[(1,2),(3,4),...]` 拆成 `zip((1,2), (3,4), ...)`，\n'
            'zip 再把每个元组的第一项聚成一组、第二项聚成另一组。'
            '所以 `xs` 拿到所有 x，`ys` 拿到所有 y。\n\n'
            '注意 `zip` 返回的是**迭代器**，只能消费一次，所以后面要用 `list()` 转成列表存下来，'
            '否则打印完之后就「空」了。\n\n'
            '`first, *rest = points` 是星号解包：`first` 拿第一个，'
            '`rest` 拿到剩下全部（是列表）。这在处理「表头 + 数据行」时特别好用。'
        ),
        'expected_output': 'xs=[1, 3, 5, 7] ys=[2, 4, 6, 8] 最大x=7 最小y=2',
        'hints': ['zip(*points) 可以把坐标对拆成两组', 'zip 返回迭代器，转成 list 才能反复用'],
    },

    # ── 第 6 章 数据结构（下）：字典与集合 ─────────────────
    {
        'id': 'ch06-01',
        'chapter_id': 6,
        'title': '用字典存学生信息并安全取值',
        'difficulty': 1,
        'tags': ['字典', 'get', 'setdefault'],
        'statement': (
            '已知 `student = {"name": "韩梅梅", "age": 17}`。\n\n'
            '要求：\n'
            '1. 添加键 `"city"`，值为 `"杭州"`\n'
            '2. 给 `age` 加 1（改成 18）\n'
            '3. 用 `get` 安全地取 `"score"`，取不到时默认 0，存进 `score`\n'
            '4. 用 `setdefault` 给 `"tags"` 一个默认空列表，然后往里加 `"新生"`\n'
            '5. 打印：`韩梅梅 18 杭州 score=0 tags=[\'新生\']`'
        ),
        'starter_code': 'student = {"name": "韩梅梅", "age": 17}\n',
        'solution': (
            "student = {'name': '韩梅梅', 'age': 17}\n"
            "student['city'] = '杭州'\n"
            "student['age'] = student['age'] + 1\n"
            "score = student.get('score', 0)\n"
            "student.setdefault('tags', []).append('新生')\n"
            "print(f\"{student['name']} {student['age']} {student['city']} score={score} tags={student['tags']}\")\n"
        ),
        'checks': [
            "assert student['city'] == '杭州', 'city 键没有加上'",
            "assert student['age'] == 18, 'age 应为 18'",
            "assert score == 0, 'score 应取到默认值 0'",
            "assert student['tags'] == ['新生'], 'tags 应为 [\\'新生\\']'",
            "assert '韩梅梅 18 杭州 score=0' in _out, '打印格式不对'",
        ],
        'explanation': (
            '`d[key]` 和 `d.get(key)` 的关键区别：**键不存在时前者抛 KeyError，后者返回 None**。'
            '所以「可能有也可能没有」的字段一律用 `get`，并给个默认值。\n\n'
            '`setdefault(key, default)` 是「取不到就设成默认值，然后返回它」的合体操作。'
            '`student.setdefault("tags", []).append("新生")` 这一行能生效，'
            '是因为 setdefault 返回的就是那个列表对象，append 直接作用在字典里存的那个列表上。\n\n'
            '如果写成 `student["tags"] = student.get("tags", []) + ["新生"]` 结果一样，'
            '但每次都会新建列表，效率低一些。'
        ),
        'expected_output': "韩梅梅 18 杭州 score=0 tags=['新生']",
        'hints': ['取可能不存在的键用 get(key, 默认值)', 'setdefault 返回的是字典里存的那个对象'],
    },
    {
        'id': 'ch06-02',
        'chapter_id': 6,
        'title': '词频统计并按次数排序',
        'difficulty': 2,
        'tags': ['字典', '排序', 'sorted'],
        'statement': (
            '已知一句话：`text = "apple banana apple cherry banana apple"`。\n\n'
            '要求：\n'
            '1. 统计每个单词出现次数，存进 `counter`（字典）\n'
            '2. 按次数**从高到低**排序，次数相同按字母序，结果存进 `ranked`\n'
            '   （提示：`sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))`）\n'
            '3. 打印排序后的结果，以及出现次数最多的前 2 个单词名（列表 `top2`）'
        ),
        'starter_code': 'text = "apple banana apple cherry banana apple"\ncounter = {}\n',
        'solution': (
            "text = 'apple banana apple cherry banana apple'\n"
            "counter = {}\n"
            "for w in text.split():\n"
            "    counter[w] = counter.get(w, 0) + 1\n"
            "ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))\n"
            "top2 = [w for w, c in ranked[:2]]\n"
            "print(ranked)\n"
            "print(top2)\n"
        ),
        'checks': [
            "assert counter == {'apple': 3, 'banana': 2, 'cherry': 1}, '词频统计不对：%r' % (counter,)",
            "assert ranked[0] == ('apple', 3), '排序第一应为 apple 3 次'",
            "assert ranked[-1] == ('cherry', 1), '排序最后应为 cherry 1 次'",
            "assert top2 == ['apple', 'banana'], 'top2 应为 [\\'apple\\', \\'banana\\']'",
        ],
        'explanation': (
            '`counter.items()` 把字典变成 `[(键, 值), ...]`，才能交给 `sorted` 排序——'
            '字典本身是无序的，不能直接排。\n\n'
            '`key=lambda kv: (-kv[1], kv[0])` 是**多关键字排序**的经典技巧：\n'
            '元组比较时先比第一项，第一项相同再比第二项。'
            '次数前面加负号，就把「从大到小」变成了「从小到大」的排序方向。\n\n'
            '如果直接写 `key=lambda kv: kv[1], reverse=True`，次数相同时的顺序会不稳定，'
            '所以显式写二级键更可靠。'
        ),
        'expected_output': "[('apple', 3), ('banana', 2), ('cherry', 1)]\n['apple', 'banana']",
        'hints': ['sorted 的 key 可以返回元组，实现多级排序', '次数取负号即可实现降序'],
    },
    {
        'id': 'ch06-03',
        'chapter_id': 6,
        'title': '两个班级的共同好友（集合运算）',
        'difficulty': 1,
        'tags': ['集合', '交集', '并集', '差集'],
        'statement': (
            '已知 `class_a = {"小明", "小红", "小刚", "小美"}`、'
            '`class_b = {"小红", "小刚", "小强"}`。\n\n'
            '用**集合运算**求（结果都存成集合）：\n'
            '1. `both`：两个班都在的人（交集）\n'
            '2. `everyone`：两个班所有不重复的人（并集）\n'
            '3. `only_a`：只在 A 班的人（差集）\n'
            '4. `symmetric`：只在其中一个班的人（对称差集）\n'
            '5. 打印 `both` 和 `symmetric` 的**排序后列表**（顺序固定才好比对）'
        ),
        'starter_code': 'class_a = {"小明", "小红", "小刚", "小美"}\nclass_b = {"小红", "小刚", "小强"}\n',
        'solution': (
            "class_a = {'小明', '小红', '小刚', '小美'}\n"
            "class_b = {'小红', '小刚', '小强'}\n"
            "both = class_a & class_b\n"
            "everyone = class_a | class_b\n"
            "only_a = class_a - class_b\n"
            "symmetric = class_a ^ class_b\n"
            "print(sorted(both))\n"
            "print(sorted(symmetric))\n"
        ),
        'checks': [
            "assert both == {'小红', '小刚'}, '交集不对：%r' % (both,)",
            "assert everyone == {'小明', '小红', '小刚', '小美', '小强'}, '并集不对'",
            "assert only_a == {'小明', '小美'}, '差集不对：%r' % (only_a,)",
            "assert symmetric == {'小明', '小美', '小强'}, '对称差集不对：%r' % (symmetric,)",
            "assert isinstance(both, set), '结果必须是集合类型'",
        ],
        'explanation': (
            '集合的四个运算一张表记住：\n\n'
            '| 运算 | 符号 | 方法 | 含义 |\n'
            '|---|---|---|---|\n'
            '| 交集 | `&` | `a.intersection(b)` | 两边都有 |\n'
            '| 并集 | `|` | `a.union(b)` | 合起来去重 |\n'
            '| 差集 | `-` | `a.difference(b)` | 只在 a |\n'
            '| 对称差 | `^` | `a.symmetric_difference(b)` | 只在一方 |\n\n'
            '集合的查找是 O(1)，所以「判断某个东西在不在集合里」用它最快，'
            '这也是上一题去重时用集合判重的原因。\n\n'
            '要注意集合是无序的，打印顺序会变，所以本题要求先 `sorted()` 再打印。'
        ),
        'expected_output': "['小刚', '小红']\n['小强', '小明', '小美']",
        'hints': ['交集是 &，并集是 |，差集是 -', '打印前先 sorted() 才能保证顺序稳定'],
    },
    {
        'id': 'ch06-04',
        'chapter_id': 6,
        'title': '合并两份库存（字典的更新与冲突）',
        'difficulty': 2,
        'tags': ['字典', 'update', '合并'],
        'statement': (
            '两家仓库的库存：\n\n'
            '```python\n'
            'warehouse_a = {"apple": 10, "banana": 5}\n'
            'warehouse_b = {"banana": 3, "cherry": 8}\n'
            '```\n\n'
            '要求：\n'
            '1. 合并成 `total_stock`，**相同商品的数量相加**（banana 应为 8）\n'
            '2. 找出两个仓库都有的商品名（列表 `common`，按字母序）\n'
            '3. 打印 `total_stock` 与 `common`'
        ),
        'starter_code': 'warehouse_a = {"apple": 10, "banana": 5}\nwarehouse_b = {"banana": 3, "cherry": 8}\ntotal_stock = {}\n',
        'solution': (
            "warehouse_a = {'apple': 10, 'banana': 5}\n"
            "warehouse_b = {'banana': 3, 'cherry': 8}\n"
            "total_stock = dict(warehouse_a)\n"
            "for name, count in warehouse_b.items():\n"
            "    total_stock[name] = total_stock.get(name, 0) + count\n"
            "common = sorted(set(warehouse_a) & set(warehouse_b))\n"
            "print(total_stock)\n"
            "print(common)\n"
        ),
        'checks': [
            "assert total_stock == {'apple': 10, 'banana': 8, 'cherry': 8}, '合并结果不对：%r' % (total_stock,)",
            "assert common == ['banana'], 'common 应为 [\\'banana\\']'",
            "assert warehouse_a['banana'] == 5, '原字典 warehouse_a 不应该被改动'",
        ],
        'explanation': (
            '`dict(warehouse_a)` 是**浅拷贝**——先复制一份，再往上加，'
            '这样原字典就不会被污染。如果直接 `total_stock = warehouse_a`，'
            '两个名字指向同一个字典，后面所有修改都会「串」到原数据上。\n\n'
            '合并冲突的处理取决于业务：这里选「相加」（两个仓库的数量要合计）。'
            '如果业务是「B 覆盖 A」，那 `update()` 一行就够了。'
            '**先想清楚语义，再写代码**——这是工程里比拼语法更重要的事。\n\n'
            '`set(dict)` 拿到的是键的集合，所以 `set(a) & set(b)` 自然得到共同键。'
        ),
        'expected_output': "{'apple': 10, 'banana': 8, 'cherry': 8}\n['banana']",
        'hints': ['先 dict(a) 拷贝一份再累加', 'set(字典) 得到的是键的集合'],
    },

    # ── 第 7 章 函数 ───────────────────────────────────────
    {
        'id': 'ch07-01',
        'chapter_id': 7,
        'title': '默认参数与关键字参数',
        'difficulty': 1,
        'tags': ['函数', '默认参数'],
        'statement': (
            '定义函数 `greet(name, greeting="你好", punct="！")`，返回一句问候语：\n\n'
            '- `greet("小明")` → `"你好，小明！"`\n'
            '- `greet("Tom", greeting="Hello")` → `"Hello，Tom！"`\n'
            '- `greet("Amy", punct="?")` → `"你好，Amy?"`\n\n'
            '然后用这三种方式各调一次并打印。'
        ),
        'starter_code': 'def greet(name, greeting="你好", punct="！"):\n    pass\n',
        'solution': (
            "def greet(name, greeting='你好', punct='！'):\n"
            "    return f'{greeting}，{name}{punct}'\n"
            "\n"
            "print(greet('小明'))\n"
            "print(greet('Tom', greeting='Hello'))\n"
            "print(greet('Amy', punct='?'))\n"
        ),
        'checks': [
            "assert greet('小明') == '你好，小明！', '默认调用结果不对：%r' % (greet('小明'),)",
            "assert greet('Tom', greeting='Hello') == 'Hello，Tom！', '关键字参数调用不对'",
            "assert greet('Amy', punct='?') == '你好，Amy?', '只覆盖 punct 的调用不对'",
            "assert greet('A', 'Hi', '~') == 'Hi，A~', '位置参数调用不对'",
        ],
        'explanation': (
            '默认参数的意义是「大多数情况不用填，少数情况可以覆盖」，'
            '让调用方只写真正关心的那个参数。\n\n'
            '`greet("Tom", greeting="Hello")` 用的是**关键字参数**：'
            '按名字传值，可以跳过前面的参数、也不怕参数顺序被改。'
            '参数一多就应该用关键字传参，代码可读性差别很大。\n\n'
            '经典陷阱：**默认参数不要用可变对象**。\n'
            '`def f(items=[])` 里的 `[]` 只在函数定义时创建一次，'
            '多次调用会共用同一个列表，导致数据「莫名其妙」地累积。'
            '需要可变默认值时写 `items=None`，函数里再 `[] if items is None else items`。'
        ),
        'expected_output': '你好，小明！\nHello，Tom！\n你好，Amy?',
        'hints': ['默认参数写在参数列表里，形如 greeting="你好"', '关键字传参：greet("Tom", greeting="Hello")'],
    },
    {
        'id': 'ch07-02',
        'chapter_id': 7,
        'title': '*args 与 **kwargs 全都要',
        'difficulty': 2,
        'tags': ['函数', '可变参数'],
        'statement': (
            '定义三个函数：\n\n'
            '1. `total(*nums)`：返回所有数字之和（无参数时返回 0）\n'
            '2. `describe(**info)`：返回 `"name=小明, age=18"` 这样的字符串，'
            '键按字母序排列，用 `, ` 连接\n'
            '3. `mixed(a, b, *rest, **extra)`：返回一个字典 '
            '`{"a": a, "b": b, "rest": rest, "extra": extra}`\n\n'
            '每个函数至少调用一次并打印结果。'
        ),
        'starter_code': 'def total(*nums):\n    pass\n',
        'solution': (
            "def total(*nums):\n"
            "    return sum(nums)\n"
            "\n"
            "def describe(**info):\n"
            "    return ', '.join(f'{k}={info[k]}' for k in sorted(info))\n"
            "\n"
            "def mixed(a, b, *rest, **extra):\n"
            "    return {'a': a, 'b': b, 'rest': rest, 'extra': extra}\n"
            "\n"
            "print(total())\n"
            "print(total(1, 2, 3, 4))\n"
            "print(describe(name='小明', age=18))\n"
            "print(mixed(1, 2, 3, 4, x=5))\n"
        ),
        'checks': [
            "assert total() == 0, 'total() 无参数时应返回 0'",
            "assert total(1, 2, 3) == 6, 'total(1,2,3) 应为 6'",
            "assert total(*[1, 2, 3, 4]) == 10, 'total 应支持解包传入'",
            "assert describe(name='小明', age=18) == 'age=18, name=小明', 'describe 输出不对：%r' % describe(name='小明', age=18)",
            "assert describe() == '', 'describe() 无参数时应返回空字符串'",
            "assert mixed(1, 2, 3, x=9) == {'a': 1, 'b': 2, 'rest': (3,), 'extra': {'x': 9}}, 'mixed 返回结构不对'",
        ],
        'explanation': (
            '`*args` 把多余的位置参数收成**元组**，`**kwargs` 把多余的关键字参数收成**字典**。'
            '名字 `args` / `kwargs` 只是惯例，真正起作用的是那两个星号。\n\n'
            '反过来，调用时 `f(*[1,2,3])` 是**解包**：把列表拆成三个位置参数，'
            '`f(**{"a": 1})` 则拆成关键字参数。传入的参数个数不确定时特别有用。\n\n'
            '参数顺序有硬性规定：`位置参数 → *args → 默认参数 → **kwargs`，'
            '写反了解释器会直接报语法错误。\n\n'
            '注意 `mixed` 里 `rest` 是元组而不是列表——因为 `*rest` 收集的就是元组。'
        ),
        'expected_output': "0\n10\nage=18, name=小明\n{'a': 1, 'b': 2, 'rest': (3, 4), 'extra': {'x': 5}}",
        'hints': ['*nums 收到的其实是元组，可以直接 sum()', '**info 是字典，排序要用 sorted(info)'],
    },
    {
        'id': 'ch07-03',
        'chapter_id': 7,
        'title': '返回多个值与类型提示',
        'difficulty': 2,
        'tags': ['函数', '返回值', '类型提示'],
        'statement': (
            '定义函数 `analyze(nums: list) -> dict`，接收一个数字列表，返回一个字典：\n\n'
            '```python\n'
            '{"count": 个数, "total": 总和, "avg": 平均值(保留2位), "max": 最大值, "min": 最小值}\n'
            '```\n\n'
            '- 空列表时返回 `{"count": 0, "total": 0, "avg": 0, "max": None, "min": None}`\n'
            '- 函数必须写**类型提示**（参数和返回值都要写）\n\n'
            '再用解包方式把返回值拆成 `stats` 并打印。'
        ),
        'starter_code': 'def analyze(nums: list) -> dict:\n    pass\n',
        'solution': (
            "def analyze(nums: list) -> dict:\n"
            "    if not nums:\n"
            "        return {'count': 0, 'total': 0, 'avg': 0, 'max': None, 'min': None}\n"
            "    total = sum(nums)\n"
            "    return {\n"
            "        'count': len(nums),\n"
            "        'total': total,\n"
            "        'avg': round(total / len(nums), 2),\n"
            "        'max': max(nums),\n"
            "        'min': min(nums),\n"
            "    }\n"
            "\n"
            "stats = analyze([88, 92, 76, 100])\n"
            "print(stats)\n"
            "print(analyze([]))\n"
        ),
        'checks': [
            "assert analyze([88, 92, 76, 100]) == {'count': 4, 'total': 356, 'avg': 89.0, 'max': 100, 'min': 76}, '统计结果不对：%r' % (analyze([88, 92, 76, 100]),)",
            "assert analyze([]) == {'count': 0, 'total': 0, 'avg': 0, 'max': None, 'min': None}, '空列表情形不对'",
            "assert analyze([5]) == {'count': 1, 'total': 5, 'avg': 5.0, 'max': 5, 'min': 5}, '单元素情形不对'",
            "assert '->' in _src, '函数需要写返回值类型提示（形如 -> dict）'",
        ],
        'explanation': (
            'Python 函数**只能返回一个对象**，但返回一个字典或元组，'
            '调用方用解包接住，效果就等于「返回多个值」：\n\n'
            '```python\n'
            'def min_max(nums):\n'
            '    return min(nums), max(nums)      # 实际返回一个元组\n'
            'low, high = min_max([3, 1, 4])       # 解包\n'
            '```\n\n'
            '本題选字典而不是元组，是因为字段多了以后「第几个是什么」很难记，'
            '用键名 `stats["avg"]` 一眼就懂。**超过 3 个返回值就该用字典或 dataclass。**\n\n'
            '类型提示 `nums: list` 和 `-> dict` 运行时**不做任何检查**，'
            '它们是给人看和给 IDE / mypy 看的。写上去的好处是补全更准、'
            '半年后自己回来也看得懂。'
        ),
        'expected_output': "{'count': 4, 'total': 356, 'avg': 89.0, 'max': 100, 'min': 76}\n{'count': 0, 'total': 0, 'avg': 0, 'max': None, 'min': None}",
        'hints': ['空列表要先判断，否则 max() 会报错', '类型提示写在参数后和 -> 后面'],
    },
    {
        'id': 'ch07-04',
        'chapter_id': 7,
        'title': '作用域：为什么函数里改不动外面的变量',
        'difficulty': 3,
        'tags': ['函数', '作用域', 'global'],
        'statement': (
            '下面的代码有问题，请**修好它**，让输出的计数正确递增：\n\n'
            '```python\n'
            'count = 0\n'
            'def hit():\n'
            '    count = count + 1     # 这里会报错\n'
            'hit(); hit(); hit()\n'
            'print(count)              # 期望 3\n'
            '```\n\n'
            '要求：\n'
            '1. 用 `global` 修复，让最终 `count` 为 3\n'
            '2. 另外再写一个**不使用 global** 的版本：'
            '`def hit_pure(count)` 接收数字并返回加 1 的结果，'
            '在外部用 `count2 = hit_pure(count2)` 的方式累加 3 次，结果同样为 3'
        ),
        'starter_code': 'count = 0\ndef hit():\n    count = count + 1\n\nhit()\nhit()\nhit()\nprint(count)\n',
        'solution': (
            "count = 0\n"
            "def hit():\n"
            "    global count\n"
            "    count = count + 1\n"
            "\n"
            "hit()\n"
            "hit()\n"
            "hit()\n"
            "print(count)\n"
            "\n"
            "def hit_pure(value):\n"
            "    return value + 1\n"
            "\n"
            "count2 = 0\n"
            "count2 = hit_pure(count2)\n"
            "count2 = hit_pure(count2)\n"
            "count2 = hit_pure(count2)\n"
            "print(count2)\n"
        ),
        'checks': [
            "assert count == 3, '全局 count 应为 3，实际 %r' % (count,)",
            "assert count2 == 3, 'count2 应为 3，实际 %r' % (count2,)",
            "assert callable(hit_pure) and hit_pure(10) == 11, 'hit_pure 应是接收数字返回加 1 的函数'",
            "assert _out.count('3') >= 2, '两次结果都应该打印出来'",
        ],
        'explanation': (
            '报错的原因是：**函数内只要出现赋值，Python 就把这个名字当作局部变量**。'
            '所以 `count = count + 1` 里右边的 `count` 也是局部的，'
            '赋值前就被读取，直接抛 `UnboundLocalError`。\n\n'
            '`global count` 明确告诉解释器「这个名字是模块级的」，报错就消失了。\n\n'
            '但更值得学的是第二种写法：**把状态当参数传进去、把结果返回出来**。'
            '这种「纯函数」不需要 global，谁调用都不会互相干扰，'
            '也更容易测试。`global` 在真实项目里应当尽量避免——'
            '它让「谁改了 count」变得极难追踪。'
        ),
        'expected_output': '3\n3',
        'hints': ['函数里赋值会让名字变成局部变量，需要 global 声明', '更好的做法是把值传进传出'],
    },

    # ── 第 8 章 模块、包与工程化 ───────────────────────────
    {
        'id': 'ch08-01',
        'chapter_id': 8,
        'title': '__name__ 到底有什么用',
        'difficulty': 2,
        'tags': ['模块', '__name__', '工程化'],
        'statement': (
            '写一个「既能被导入、也能直接运行」的模块式脚本。\n\n'
            '要求：\n'
            '1. 定义函数 `area(width, height)` 返回面积\n'
            '2. 定义函数 `perimeter(width, height)` 返回周长\n'
            '3. 在 `if __name__ == "__main__":` 里打印 '
            '`面积=12 周长=14`（用 3×4 的矩形）\n'
            '4. 把 `__name__` 的值存进变量 `module_name` 并打印它的类型\n\n'
            '（这道题考的是：为什么别人 `import` 你的文件时，不该看到那行打印。）'
        ),
        'starter_code': 'def area(width, height):\n    pass\n\ndef perimeter(width, height):\n    pass\n',
        'solution': (
            "def area(width, height):\n"
            "    return width * height\n"
            "\n"
            "def perimeter(width, height):\n"
            "    return 2 * (width + height)\n"
            "\n"
            "module_name = __name__\n"
            "print(type(module_name))\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    print(f'面积={area(3, 4)} 周长={perimeter(3, 4)}')\n"
        ),
        'checks': [
            "assert area(3, 4) == 12, 'area(3,4) 应为 12'",
            "assert perimeter(3, 4) == 14, 'perimeter(3,4) 应为 14'",
            "assert '面积=12 周长=14' in _out, '直接运行时应打印「面积=12 周长=14」'",
            "assert module_name == '__main__', '在本文件里直接执行时 __name__ 应该是 __main__'",
            "assert 'str' in _out, '应打印 __name__ 的类型（str）'",
        ],
        'explanation': (
            '`__name__` 是每个模块自带的变量：\n\n'
            '- 文件被**直接运行**时，它是 `"__main__"`；\n'
            '- 文件被**导入**时，它是模块名（比如 `"geometry"`）。\n\n'
            '所以 `if __name__ == "__main__":` 的意思是「只有当我是主程序时才执行这段」。'
            '没有这层保护，别人一 `import` 你的文件，你的测试代码就会跟着跑一遍，'
            '这在多人协作里是灾难。\n\n'
            '养成习惯：**模块里只放定义，把会执行的动作放进这个 if 里。**'
            '这也是 `python -m` 和 pytest 收集用例能正常工作的前提。'
        ),
        'expected_output': "<class 'str'>\n面积=12 周长=14",
        'hints': ['直接运行的文件里 __name__ 是字符串 "__main__"', '打印和测试代码放进 if 里'],
    },
    {
        'id': 'ch08-02',
        'chapter_id': 8,
        'title': '用 json 模块做配置的存取',
        'difficulty': 2,
        'tags': ['json', '序列化', '文件'],
        'statement': (
            '把字典与 JSON 字符串互相转换（本题不落盘，只做字符串层面的转换）：\n\n'
            '1. 已知 `config = {"name": "PyMaster", "version": 2, "debug": True, "tags": ["python", "ai"]}`，'
            '用 `json.dumps` 转成字符串 `text`（要求 `ensure_ascii=False`，中文不转义）\n'
            '2. 用 `json.loads` 把 `text` 转回字典 `restored`\n'
            '3. 断言 `restored == config`，把结果存进 `same`（布尔值）\n'
            '4. 打印 `text` 和 `same`'
        ),
        'starter_code': 'import json\nconfig = {"name": "PyMaster", "version": 2, "debug": True, "tags": ["python", "ai"]}\ntext = \n',
        'solution': (
            "import json\n"
            "config = {'name': 'PyMaster', 'version': 2, 'debug': True, 'tags': ['python', 'ai']}\n"
            "text = json.dumps(config, ensure_ascii=False)\n"
            "restored = json.loads(text)\n"
            "same = restored == config\n"
            "print(text)\n"
            "print(same)\n"
        ),
        'checks': [
            "assert isinstance(text, str) and json.loads(text) == config, 'text 应该是可被 json.loads 还原的字符串'",
            "assert 'PyMaster' in text, 'text 里应包含内容'",
            "assert restored == config, 'restored 应等于原字典'",
            "assert same is True, 'same 应为 True'",
            "assert _out.strip().endswith('True'), '最后应打印 True'",
        ],
        'explanation': (
            '`json.dumps` 是「Python 对象 → JSON 字符串」，`json.loads` 是反方向。'
            '记忆方法：**带 s 的处理字符串（string），不带 s 的处理文件（file）**，'
            '所以还有 `json.dump` / `json.load`。\n\n'
            '`ensure_ascii=False` 很关键：默认值 True 会把中文转成 `\\u4e2d\\u6587`，'
            '存配置文件时人根本没法读。中文项目里几乎总要加上这个参数。\n\n'
            '类型映射要注意：Python 的 `True` 变 JSON 的 `true`，'
            '字典的键会被强制转成字符串，元组会变成数组（转回来是列表，不是元组）。'
        ),
        'expected_output': '{"name": "PyMaster", "version": 2, "debug": true, "tags": ["python", "ai"]}\nTrue',
        'hints': ['json.dumps(d, ensure_ascii=False) 才能保留中文', '转回来用 json.loads'],
    },

    # ── 第 9 章 文件读写、异常与调试 ───────────────────────
    {
        'id': 'ch09-01',
        'chapter_id': 9,
        'title': '写文件再读回来（with 的正确用法）',
        'difficulty': 2,
        'tags': ['文件IO', 'with'],
        'statement': (
            '完成一次完整的文件写读：\n\n'
            '1. 把三行内容写进文件 `notes.txt`（UTF-8，用 `with open`）：\n'
            '```\n第一行\n第二行\n第三行\n```\n'
            '2. 追加一行 `第四行`\n'
            '3. 读回全部内容存进 `content`，并按行拆成列表 `lines_out`（去掉行尾换行符）\n'
            '4. 打印行数（4）和 `content` 的前 3 个字符\n\n'
            '⚠️ 写完文件后用 `os.remove` 把它删掉，别在运行环境里留垃圾文件。'
        ),
        'starter_code': 'import os\ncontent = ""\nlines_out = []\n',
        'solution': (
            "import os\n"
            "with open('notes.txt', 'w', encoding='utf-8') as f:\n"
            "    f.write('第一行\\n第二行\\n第三行\\n')\n"
            "\n"
            "with open('notes.txt', 'a', encoding='utf-8') as f:\n"
            "    f.write('第四行\\n')\n"
            "\n"
            "with open('notes.txt', 'r', encoding='utf-8') as f:\n"
            "    content = f.read()\n"
            "\n"
            "lines_out = [line for line in content.splitlines() if line]\n"
            "print(len(lines_out))\n"
            "print(content[:3])\n"
            "os.remove('notes.txt')\n"
        ),
        'checks': [
            "assert len(lines_out) == 4, '行数应为 4，实际 %d' % len(lines_out)",
            "assert lines_out == ['第一行', '第二行', '第三行', '第四行'], '读回来的内容不对：%r' % (lines_out,)",
            "assert not os.path.exists('notes.txt'), '请用 os.remove 删掉测试文件'",
            "assert _out.strip().startswith('4'), '第一行输出应为 4'",
        ],
        'explanation': (
            '`with open(...) as f:` 的价值是**无论中间发生什么，文件都会被正确关闭**。'
            '手写 `f = open(...)` 然后忘了 `f.close()`，'
            '在 Windows 上会留下一个被占用的文件，别的程序读不了也删不掉。\n\n'
            '四种模式记住：`"r"` 读（文件不存在会报错）、`"w"` 写（**清空原内容**）、'
            '`"a"` 追加、`"r+"` 读写。最危险的坑是 `"w"`：'
            '它一打开就把文件清空了，写错了没法撤销。\n\n'
            '`\n` 在 Python 里是**一个**换行符，Windows 上写文件时 Python 会自动'
            '把它转成 `\r\n`（文本模式），读回来又会转回 `\n`，所以不用自己处理。\n\n'
            '`text.splitlines()` 比 `text.split("\\n")` 更稳妥，'
            '它能同时处理 `\\n`、`\\r\\n`、`\\r` 三种换行。'
        ),
        'expected_output': '4\n第一行',
        'hints': ['写用 "w"，追加用 "a"，读用 "r"，都要 encoding="utf-8"', '最后记得 os.remove 清理文件'],
    },
    {
        'id': 'ch09-02',
        'chapter_id': 9,
        'title': '安全除法：try-except-else-finally',
        'difficulty': 2,
        'tags': ['异常', 'try', 'finally'],
        'statement': (
            '定义函数 `safe_divide(a, b)`，返回 `(结果, 错误信息)` 的元组：\n\n'
            '- 正常情况：`(结果, "")`，例如 `safe_divide(10, 2)` → `(5.0, "")`\n'
            '- 除零：`(None, "除数不能为 0")`\n'
            '- 类型不对（比如传了字符串）：`(None, "请输入数字")`\n\n'
            '要求用完整的 `try / except / else / finally` 结构，'
            '并在 `finally` 里把字符串 `"结算"` 追加到全局列表 `trace` 里，'
            '这样每次调用都能留下痕迹。\n\n'
            '最后依次调用三次并打印结果与 `trace`。'
        ),
        'starter_code': 'trace = []\ndef safe_divide(a, b):\n    pass\n',
        'solution': (
            "trace = []\n"
            "def safe_divide(a, b):\n"
            "    try:\n"
            "        result = a / b\n"
            "    except ZeroDivisionError:\n"
            "        return None, '除数不能为 0'\n"
            "    except TypeError:\n"
            "        return None, '请输入数字'\n"
            "    else:\n"
            "        return result, ''\n"
            "    finally:\n"
            "        trace.append('结算')\n"
            "\n"
            "print(safe_divide(10, 2))\n"
            "print(safe_divide(10, 0))\n"
            "print(safe_divide('a', 2))\n"
            "print(trace)\n"
        ),
        'checks': [
            "assert safe_divide(10, 2) == (5.0, ''), '正常情况应返回 (5.0, \\'\\')'",
            "assert safe_divide(10, 0) == (None, '除数不能为 0'), '除零情况处理不对'",
            "assert safe_divide('a', 2) == (None, '请输入数字'), '类型错误处理不对'",
            "_before = len(trace)",
            "safe_divide(1, 1)",
            "safe_divide(1, 0)",
            "safe_divide('x', 1)",
            "assert len(trace) == _before + 3, '每次调用都该在 finally 里追加一次「结算」，实际新增 %d 次' % (len(trace) - _before)",
        ],
        'explanation': (
            '四个分支各司其职：\n\n'
            '- `try`：可能出错的代码，**只放可能出错的那一两行**（放多了会掩盖真正的 bug）；\n'
            '- `except`：按异常类型分别处理，**不要写裸的 `except:`**，'
            '那会把 `KeyboardInterrupt` 之类也吞掉，程序出问题都查不出来；\n'
            '- `else`：try 里没出错才执行；\n'
            '- `finally`：无论如何都执行，用来释放资源（关文件、断连接）。\n\n'
            '注意 `finally` 里有 `append` 时，即使前面 `return` 了，'
            '`finally` 仍会先执行完再返回。这是「资源清理一定发生」的保证。\n\n'
            '返回 `(结果, 错误)` 这种「要么值要么错」的风格，'
            '在 Go 语言里是主流写法；Python 更常用抛异常，'
            '但在「错误是预料之中的正常分支」时，返回错误信息更好用。'
        ),
        'expected_output': "(5.0, '')\n(None, '除数不能为 0')\n(None, '请输入数字')\n['结算', '结算', '结算']",
        'hints': ['分别捕获 ZeroDivisionError 和 TypeError', 'finally 一定会执行，无论是否 return'],
    },
    {
        'id': 'ch09-03',
        'chapter_id': 9,
        'title': '自定义异常：校验用户注册信息',
        'difficulty': 3,
        'tags': ['异常', '自定义异常', '校验'],
        'statement': (
            '定义自己的异常类 `ValidationError(Exception)`，再写校验函数：\n\n'
            '`validate_user(username, age)` 规则：\n'
            '- 用户名长度小于 3：抛 `ValidationError("用户名至少 3 个字符")`\n'
            '- 用户名里有空格：抛 `ValidationError("用户名不能包含空格")`\n'
            '- 年龄不是 0~150 之间的整数：抛 `ValidationError("年龄不合法")`\n'
            '- 全部通过：返回 `"校验通过"`\n\n'
            '然后写 `check(username, age)` 调用它，**捕获 ValidationError** 并返回错误信息字符串，'
            '其他异常不要吞掉。\n\n'
            '最后对 `("ab", 18)`、`("li lei", 18)`、`("lilei", 200)`、`("lilei", 18)` 各调一次并打印。'
        ),
        'starter_code': 'class ValidationError(Exception):\n    pass\n\ndef validate_user(username, age):\n    pass\n',
        'solution': (
            "class ValidationError(Exception):\n"
            "    pass\n"
            "\n"
            "def validate_user(username, age):\n"
            "    if not isinstance(username, str):\n"
            "        raise ValidationError('用户名必须是字符串')\n"
            "    if len(username) < 3:\n"
            "        raise ValidationError('用户名至少 3 个字符')\n"
            "    if ' ' in username:\n"
            "        raise ValidationError('用户名不能包含空格')\n"
            "    if not isinstance(age, int) or isinstance(age, bool) or not (0 <= age <= 150):\n"
            "        raise ValidationError('年龄不合法')\n"
            "    return '校验通过'\n"
            "\n"
            "def check(username, age):\n"
            "    try:\n"
            "        return validate_user(username, age)\n"
            "    except ValidationError as exc:\n"
            "        return str(exc)\n"
            "\n"
            "for u, a in [('ab', 18), ('li lei', 18), ('lilei', 200), ('lilei', 18)]:\n"
            "    print(check(u, a))\n"
        ),
        'checks': [
            "assert issubclass(ValidationError, Exception), 'ValidationError 必须是 Exception 的子类'",
            "assert validate_user('lilei', 18) == '校验通过', '合法输入应返回 校验通过'",
            "assert check('ab', 18) == '用户名至少 3 个字符', '短用户名错误信息不对'",
            "assert check('li lei', 18) == '用户名不能包含空格', '空格校验不对'",
            "assert check('lilei', 200) == '年龄不合法', '年龄越界校验不对'",
            "assert check('lilei', 18) == '校验通过', '合法输入走 check 应返回 校验通过'",
            "assert _out.count('校验通过') == 1, '示例里应有一次合法调用并打印「校验通过」'",
        ],
        'explanation': (
            '自定义异常让「哪一类错误」变成有名字的东西。'
            '调用方可以只捕获 `ValidationError`，'
            '这样别的错误（比如代码写错的 `NameError`）照样会冒出来，'
            '不会被误当作「用户输入有问题」。\n\n'
            '`raise` 的时机要早：**校验失败立刻抛，不要继续往下走**。'
            '很多线上事故就是「校验失败只打印日志，然后继续执行」。\n\n'
            '注意 `isinstance(age, bool)` 的那一层：Python 里 `True` 也是 `int`，'
            '`validate_user("lilei", True)` 不拦的话会被当成年龄 1。'
            '这种「类型系统的边缘情况」是写健壮代码的日常。\n\n'
            '异常信息要写给**人**看：`"年龄不合法"` 比 `"invalid age"` 好，'
            '`"用户名至少 3 个字符（当前 2 个）"` 又比只说「不合法」更好。'
        ),
        'expected_output': '用户名至少 3 个字符\n用户名不能包含空格\n年龄不合法\n校验通过',
        'hints': ['自定义异常只要 class XxxError(Exception): pass', '校验失败直接 raise，不要 print 完继续'],
    },

    # ── 第 10 章 面向对象（上）─────────────────────────────
    {
        'id': 'ch10-01',
        'chapter_id': 10,
        'title': '第一支类：银行账户',
        'difficulty': 2,
        'tags': ['类', '对象', '方法'],
        'statement': (
            '定义类 `Account`：\n\n'
            '- `__init__(self, owner, balance=0)`：保存户主与余额\n'
            '- `deposit(self, amount)`：存钱，返回新余额；金额 ≤ 0 时抛 `ValueError`\n'
            '- `withdraw(self, amount)`：取钱，返回新余额；'
            '金额 ≤ 0 或超过余额时抛 `ValueError("余额不足")`\n'
            '- `__str__`：返回 `"小明 的账户：余额 150 元"` 这样的字符串\n\n'
            '然后创建账户，存 200 取 50，打印账户和余额。'
        ),
        'starter_code': 'class Account:\n    def __init__(self, owner, balance=0):\n        pass\n',
        'solution': (
            "class Account:\n"
            "    def __init__(self, owner, balance=0):\n"
            "        self.owner = owner\n"
            "        self.balance = balance\n"
            "\n"
            "    def deposit(self, amount):\n"
            "        if amount <= 0:\n"
            "            raise ValueError('金额必须大于 0')\n"
            "        self.balance += amount\n"
            "        return self.balance\n"
            "\n"
            "    def withdraw(self, amount):\n"
            "        if amount <= 0 or amount > self.balance:\n"
            "            raise ValueError('余额不足')\n"
            "        self.balance -= amount\n"
            "        return self.balance\n"
            "\n"
            "    def __str__(self):\n"
            "        return f'{self.owner} 的账户：余额 {self.balance} 元'\n"
            "\n"
            "acc = Account('小明')\n"
            "acc.deposit(200)\n"
            "acc.withdraw(50)\n"
            "print(acc)\n"
            "print(acc.balance)\n"
        ),
        'checks': [
            "acc = Account('测试', 100)",
            "assert acc.balance == 100, '__init__ 的默认余额没存对'",
            "assert acc.deposit(50) == 150, 'deposit 应返回新余额 150'",
            "assert acc.withdraw(30) == 120, 'withdraw 应返回新余额 120'",
            "assert str(acc) == '测试 的账户：余额 120 元', '__str__ 输出格式不对：%r' % str(acc)",
            "try:\n    acc.withdraw(9999)\n    assert False, '余额不足时应抛 ValueError'\nexcept ValueError as e:\n    assert '余额不足' in str(e), '余额不足的报错信息不对'",
            "try:\n    acc.deposit(0)\n    assert False, '存入 0 元时应抛 ValueError'\nexcept ValueError:\n    pass",
        ],
        'explanation': (
            '`self` 就是「当前这个对象」。`self.owner = owner` 的意思是'
            '把外面传进来的 `owner` 存到对象自己的属性上，之后任何方法都能通过 `self.owner` 取到。\n\n'
            '`__init__` 不是构造函数（对象早就创建好了），而是**初始化方法**：'
            '负责给新对象贴属性。它的 `self` 是 Python 自动传的，你只管写后面的参数。\n\n'
            '`__str__` 定义了「打印这个对象时显示什么」。'
            '没有它，`print(acc)` 会输出 `<__main__.Account object at 0x7f...>` 这种'
            '对用户毫无意义的地址。**自己写的类，只要会打印，就该实现 `__str__`。**\n\n'
            '在方法里做校验并抛异常，是「把规则放在数据旁边」的思路：'
            '任何地方想改余额都得过 `deposit` / `withdraw` 这两道关，'
            '不会有谁偷偷把 `acc.balance = -999`。'
        ),
        'expected_output': '小明 的账户：余额 150 元\n150',
        'hints': ['属性用 self.xxx 保存，注意 __init__ 里的 self 是自动传的', '__str__ 必须返回字符串，不能是 print'],
    },
    {
        'id': 'ch10-02',
        'chapter_id': 10,
        'title': '用 @property 把属性保护起来',
        'difficulty': 3,
        'tags': ['类', 'property', '封装'],
        'statement': (
            '改造 `Temperature` 类，用 `@property` 实现「读写分离的校验」：\n\n'
            '- 内部属性叫 `_celsius`\n'
            '- `celsius` 属性：读的时候返回 `_celsius`；'
            '写的时候如果温度低于 **绝对零度（-273.15）** 就抛 `ValueError("温度不能低于绝对零度")`\n'
            '- `fahrenheit` 属性（只读）：返回 `_celsius * 9 / 5 + 32`\n\n'
            '然后创建对象、正常赋值、打印摄氏与华氏，再试着赋一个非法值并捕获异常打印。\n\n'
            '答案要求：`temp.celsius = -300` 必须报错，'
            '`temp.celsius` 读出来是最近一次合法赋的值。'
        ),
        'starter_code': 'class Temperature:\n    def __init__(self, celsius=0):\n        pass\n',
        'solution': (
            "class Temperature:\n"
            "    def __init__(self, celsius=0):\n"
            "        self.celsius = celsius\n"
            "\n"
            "    @property\n"
            "    def celsius(self):\n"
            "        return self._celsius\n"
            "\n"
            "    @celsius.setter\n"
            "    def celsius(self, value):\n"
            "        if value < -273.15:\n"
            "            raise ValueError('温度不能低于绝对零度')\n"
            "        self._celsius = value\n"
            "\n"
            "    @property\n"
            "    def fahrenheit(self):\n"
            "        return self._celsius * 9 / 5 + 32\n"
            "\n"
            "temp = Temperature(25)\n"
            "print(temp.celsius, temp.fahrenheit)\n"
            "temp.celsius = 100\n"
            "print(temp.celsius, temp.fahrenheit)\n"
            "try:\n"
            "    temp.celsius = -300\n"
            "except ValueError as exc:\n"
            "    print('拦截：', exc)\n"
        ),
        'checks': [
            "t = Temperature(25)",
            "assert t.celsius == 25, '初始温度没存对'",
            "assert abs(t.fahrenheit - 77.0) < 1e-6, '华氏度换算不对：%r' % (t.fahrenheit,)",
            "t.celsius = 100",
            "assert t.celsius == 100, '正常赋值后读出来不对'",
            "try:\n    t.celsius = -300\n    assert False, '低于绝对零度必须抛 ValueError'\nexcept ValueError as e:\n    assert '绝对零度' in str(e), '异常信息应提到绝对零度'",
            "assert t.celsius == 100, '非法赋值不应该改动已有值'",
            "try:\n    t.fahrenheit = 100\n    assert False, 'fahrenheit 是只读属性，赋值应当报错'\nexcept AttributeError:\n    pass",
        ],
        'explanation': (
            '`@property` 把方法「伪装」成属性：外部写 `temp.celsius` '
            '而不用写 `temp.get_celsius()`，读起来干净，'
            '但取值的那一刻实际执行的是你写的函数——校验、计算都能放进去。\n\n'
            '`@celsius.setter` 定义赋值行为。注意两个装饰器的名字必须一致（都叫 celsius），'
            '这正是「同一个名字，读一套逻辑，写一套逻辑」的实现方式。\n\n'
            '`fahrenheit` 只写了 getter，所以它是只读的；'
            '试图赋值会抛 `AttributeError`，这比让它悄悄生效安全得多。\n\n'
            '为什么要用 `_celsius`？因为 `self.celsius = value` 在 setter 里会**再次调用 setter**，'
            '造成无限递归。内部存到 `_celsius` 上，绕开自己的校验，这是标准做法。\n\n'
            '顺带一提：`__init__` 里写 `self.celsius = celsius` 而不是 `self._celsius = ...`，'
            '是为了让初始值也走一遍校验。'
        ),
        'expected_output': '25 77.0\n100 212.0\n拦截： 温度不能低于绝对零度',
        'hints': ['setter 里要给 self._celsius 赋值，不能给 self.celsius 赋值（会无限递归）', '@property 定义读，@xxx.setter 定义写'],
    },
    {
        'id': 'ch10-03',
        'chapter_id': 10,
        'title': '类属性、实例属性与统计计数',
        'difficulty': 3,
        'tags': ['类属性', '实例属性', '类方法'],
        'statement': (
            '用类属性统计「一共造了多少个对象」：\n\n'
            '定义类 `Student`：\n'
            '- **类属性** `count = 0`，每创建一个对象就 +1\n'
            '- 类属性 `school = "PyMaster 学院"`（所有实例共享）\n'
            '- 实例属性 `name`、`scores`（分数列表，默认空）\n'
            '- 方法 `add_score(score)`：加分，并**返回 self** 以支持 `a.add_score(90).add_score(80)` 链式调用\n'
            '- 方法 `average()`：返回平均分（保留 2 位），没分数时返回 0\n'
            '- **类方法** `total()`：返回 `count` 的值\n\n'
            '然后创建 3 个学生（小明、小红、小刚）、各加点分，'
            '打印 `Student.total()`、`Student.school` 和每个学生的平均分。'
        ),
        'starter_code': 'class Student:\n    count = 0\n    school = "PyMaster 学院"\n',
        'solution': (
            "class Student:\n"
            "    count = 0\n"
            "    school = 'PyMaster 学院'\n"
            "\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "        self.scores = []\n"
            "        Student.count += 1\n"
            "\n"
            "    def add_score(self, score):\n"
            "        self.scores.append(score)\n"
            "        return self\n"
            "\n"
            "    def average(self):\n"
            "        if not self.scores:\n"
            "            return 0\n"
            "        return round(sum(self.scores) / len(self.scores), 2)\n"
            "\n"
            "    @classmethod\n"
            "    def total(cls):\n"
            "        return cls.count\n"
            "\n"
            "a = Student('小明')\n"
            "b = Student('小红')\n"
            "c = Student('小刚')\n"
            "a.add_score(90).add_score(80)\n"
            "b.add_score(70)\n"
            "print(Student.total())\n"
            "print(Student.school)\n"
            "for s in (a, b, c):\n"
            "    print(s.name, s.average())\n"
        ),
        'checks': [
            "assert Student.count == 3, 'count 应为 3，实际 %r' % (Student.count,)",
            "assert Student.total() == 3, 'total() 应返回 3'",
            "assert Student.school == 'PyMaster 学院', 'school 类属性不对'",
            "assert a.average() == 85.0, '小明的平均分应为 85.0'",
            "assert c.average() == 0, '没有成绩的学生平均分应为 0'",
            "assert isinstance(a.scores, list) and a.scores == [90, 80], 'a.scores 应为 [90, 80]'",
            "assert a.school == 'PyMaster 学院', '实例也能读到类属性'",
            "assert '3' in _out and '85.0' in _out, '应打印总人数 3 和小明的平均分 85.0'",
        ],
        'explanation': (
            '**类属性 vs 实例属性**是这一节的核心：\n\n'
            '- `count`、`school` 定义在 class 里，属于**类**，所有实例共享同一份；\n'
            '- `self.name` 属于**每个实例**，张三改了不影响李四。\n\n'
            '查找顺序是「先找实例，找不到再找类」，所以 `a.school` 能读到类属性。'
            '但**赋值会创建实例属性**：`a.school = "X"` 只是给 a 加了个自己的属性，'
            '类属性和其他实例都不受影响。这是面试高频陷阱。\n\n'
            '累加计数必须写 `Student.count += 1` 而不能写 `self.count += 1`——'
            '后者会创建一个属于这个实例的 `count`，统计就废了。\n\n'
            '**可变默认值的经典坑**：如果写成 `def __init__(self, name, scores=[])`，'
            '所有学生的 `scores` 会是**同一个列表**，加分互相串。'
            '所以这里在 `__init__` 里现创建 `self.scores = []`。\n\n'
            '`@classmethod` 的 `cls` 是类本身，子类调用时会自动指向子类，'
            '比写死 `Student` 更灵活。`add_score` 返回 `self` 是为了支持链式调用。'
        ),
        'expected_output': '3\nPyMaster 学院\n小明 85.0\n小红 70.0\n小刚 0',
        'hints': ['计数要写 Student.count += 1，写 self.count 就变成实例属性了', 'scores 必须在 __init__ 里新建，不能做默认参数'],
    },

    # ── 第 11 章 面向对象（下）─────────────────────────────
    {
        'id': 'ch11-01',
        'chapter_id': 11,
        'title': '继承与 super()：三种员工',
        'difficulty': 2,
        'tags': ['继承', 'super', '多态'],
        'statement': (
            '用继承描述公司里的三种人：\n\n'
            '1. 父类 `Employee(name, salary)`：\n'
            '   - 方法 `work()` 返回 `"在做通用工作"`\n'
            '   - 方法 `describe()` 返回 `"小明 月薪 8000"`\n'
            '2. 子类 `Developer(Employee)`：\n'
            '   - `__init__(name, salary, language="Python")`，用 `super()` 调用父类初始化\n'
            '   - 重写 `work()` 返回 `"在用 Python 写代码"`（用 `self.language`）\n'
            '3. 子类 `Manager(Employee)`：\n'
            '   - 额外属性 `team_size`（默认 0）\n'
            '   - 重写 `work()` 返回 `"在管理 5 个人的团队"`\n\n'
            '最后把所有对象放进一个列表，用同一个循环调用 `work()`，'
            '观察「同一个方法名，不同表现」——这就是多态。'
        ),
        'starter_code': 'class Employee:\n    def __init__(self, name, salary):\n        pass\n',
        'solution': (
            "class Employee:\n"
            "    def __init__(self, name, salary):\n"
            "        self.name = name\n"
            "        self.salary = salary\n"
            "\n"
            "    def work(self):\n"
            "        return '在做通用工作'\n"
            "\n"
            "    def describe(self):\n"
            "        return f'{self.name} 月薪 {self.salary}'\n"
            "\n"
            "\n"
            "class Developer(Employee):\n"
            "    def __init__(self, name, salary, language='Python'):\n"
            "        super().__init__(name, salary)\n"
            "        self.language = language\n"
            "\n"
            "    def work(self):\n"
            "        return f'在用 {self.language} 写代码'\n"
            "\n"
            "\n"
            "class Manager(Employee):\n"
            "    def __init__(self, name, salary, team_size=0):\n"
            "        super().__init__(name, salary)\n"
            "        self.team_size = team_size\n"
            "\n"
            "    def work(self):\n"
            "        return f'在管理 {self.team_size} 个人的团队'\n"
            "\n"
            "\n"
            "staff = [Employee('老王', 8000), Developer('小明', 15000),\n"
            "         Manager('小红', 20000, 5)]\n"
            "for person in staff:\n"
            "    print(person.describe(), '|', person.work())\n"
        ),
        'checks': [
            "assert issubclass(Developer, Employee) and issubclass(Manager, Employee), '两个子类都应继承 Employee'",
            "d = Developer('小明', 15000)",
            "assert d.language == 'Python', 'Developer 默认语言应为 Python'",
            "assert d.work() == '在用 Python 写代码', 'Developer.work 输出不对：%r' % d.work()",
            "assert d.describe() == '小明 月薪 15000', 'describe 应继承自父类'",
            "m = Manager('小红', 20000, 5)",
            "assert m.work() == '在管理 5 个人的团队', 'Manager.work 输出不对'",
            "assert isinstance(m, Employee), 'Manager 实例应该也是 Employee（isinstance 成立）'",
            "assert Employee('老王', 8000).work() == '在做通用工作', '父类 work 不应被改坏'",
            "assert '在用 Python 写代码' in _out and '在管理 5 个人的团队' in _out, '多态输出没打印全'",
        ],
        'explanation': (
            '`super().__init__(name, salary)` 的意思是「调用父类的初始化」，'
            '把 `name`、`salary` 的赋值交给父类去做。这样父类改了属性名，子类不用跟着改。\n\n'
            '**子类重写（override）方法**后，同名方法会优先用子类的。'
            '所以 `for person in staff: person.work()` 这一句里，'
            '同样是 `work()`，Employee 返回「通用工作」、Developer 返回「写代码」——'
            '**运行时才决定调哪个**，这就是多态。\n\n'
            '多态的价值在于：调用方不需要写一堆 `if isinstance(x, Developer)`，'
            '新增一种员工类型时，上面那个循环**一个字都不用改**。'
            '这是「对扩展开放、对修改关闭」的具体体现。\n\n'
            '`isinstance(m, Employee)` 为 True 说明子类对象可以被当作父类使用'
            '（里氏替换原则），这也是类型提示里 `list[Employee]` 能装下 Developer 的原因。'
        ),
        'expected_output': '老王 月薪 8000 | 在做通用工作\n小明 月薪 15000 | 在用 Python 写代码\n小红 月薪 20000 | 在管理 5 个人的团队',
        'hints': ['子类 __init__ 第一行调用 super().__init__(...)', '重写方法就是同名再定义一次'],
    },
    {
        'id': 'ch11-02',
        'chapter_id': 11,
        'title': '魔术方法：让对象能比较、能相加',
        'difficulty': 3,
        'tags': ['魔术方法', 'dunder', '排序'],
        'statement': (
            '定义 `Money` 类，让它像数字一样自然：\n\n'
            '- `__init__(self, amount)`：金额（元）\n'
            '- `__str__`：返回 `"￥100"`\n'
            '- `__add__`：`Money(100) + Money(50)` 得到 `Money(150)`\n'
            '- `__eq__`：金额相同就相等\n'
            '- `__lt__`：金额小的更小，这样才能 `sorted()` 排序\n\n'
            '然后：创建 3 个 Money、相加、比较、排序，并打印结果。'
        ),
        'starter_code': 'class Money:\n    def __init__(self, amount):\n        pass\n',
        'solution': (
            "class Money:\n"
            "    def __init__(self, amount):\n"
            "        self.amount = amount\n"
            "\n"
            "    def __str__(self):\n"
            "        return f'￥{self.amount}'\n"
            "\n"
            "    def __repr__(self):\n"
            "        return f'Money({self.amount})'\n"
            "\n"
            "    def __add__(self, other):\n"
            "        return Money(self.amount + other.amount)\n"
            "\n"
            "    def __eq__(self, other):\n"
            "        return isinstance(other, Money) and self.amount == other.amount\n"
            "\n"
            "    def __lt__(self, other):\n"
            "        return self.amount < other.amount\n"
            "\n"
            "a, b, c = Money(100), Money(50), Money(30)\n"
            "print(a + b)\n"
            "print(a == Money(100))\n"
            "print(sorted([a, b, c]))\n"
        ),
        'checks': [
            "assert str(Money(100)) == '￥100', '__str__ 输出不对：%r' % str(Money(100))",
            "total = Money(100) + Money(50)",
            "assert isinstance(total, Money) and total.amount == 150, '__add__ 应返回金额 150 的 Money'",
            "assert Money(100) == Money(100), '相同金额应判为相等'",
            "assert Money(100) != Money(50), '不同金额不应相等'",
            "assert Money(30) < Money(50), '__lt__ 应支持小于比较'",
            "assert [m.amount for m in sorted([Money(100), Money(50), Money(30)])] == [30, 50, 100], 'sorted 结果不对'",
            "assert '￥150' in _out, '应打印相加结果 ￥150'",
        ],
        'explanation': (
            '以双下划线开头结尾的方法（`__add__`、`__eq__`…）叫魔术方法，'
            '它们定义了对象在各种「语法场景」下的行为：\n\n'
            '| 你写的 | 实际调用 |\n'
            '|---|---|\n'
            '| `a + b` | `a.__add__(b)` |\n'
            '| `a == b` | `a.__eq__(b)` |\n'
            '| `a < b` | `a.__lt__(b)` |\n'
            '| `print(a)` | `a.__str__()` |\n'
            '| `sorted([...])` | 反复比较元素的 `__lt__` |\n\n'
            '所以只要实现了 `__lt__`，`sorted` 就自动能给你的对象排序，'
            '不需要写 `key=` 参数。这也是为什么「自定义对象排序报 TypeError」'
            '时，第一反应就是「我是不是没实现 `__lt__`」。\n\n'
            '`__eq__` 里判断了 `isinstance(other, Money)`：'
            '`Money(100) == "100"` 应该返回 False 而不是崩掉或返回别的类型。\n\n'
            '`__repr__` 是给开发者看的（在交互式环境里回车就显示它），'
            '`__str__` 是给用户看的。两个都实现是专业习惯。\n\n'
            '另外注意：`__add__` 里返回的是**新的 Money 对象**，没有改动原来的。'
            '这让 Money 表现得像数字一样「不可变」，用起来不易出错。'
        ),
        'expected_output': '￥150\nTrue\n[Money(30), Money(50), Money(100)]',
        'hints': ['__add__ 里要 return Money(...)，不能返回数字', '实现了 __lt__ 之后 sorted() 就能直接用'],
    },

    # ── 第 12 章 高级特性 ──────────────────────────────────
    {
        'id': 'ch12-01',
        'chapter_id': 12,
        'title': '推导式三连击',
        'difficulty': 2,
        'tags': ['推导式', '列表', '字典'],
        'statement': (
            '用**推导式**（不许写 for 循环加 append）完成：\n\n'
            '1. `squares`：1~10 的平方组成的列表 → `[1, 4, 9, ..., 100]`\n'
            '2. `evens`：从 `nums = [1, 2, 3, 4, 5, 6, 7, 8]` 里挑出偶数\n'
            '3. `lengths`：`words = ["apple", "hi", "banana"]` → '
            '`{"apple": 5, "hi": 2, "banana": 6}`（字典推导式）\n'
            '4. `matrix_flat`：把 `[[1, 2], [3, 4], [5, 6]]` 压平成一维（嵌套推导式）\n'
            '5. `classified`：`{"even": [...], "odd": [...]}`，把 nums 按奇偶分组'
        ),
        'starter_code': 'nums = [1, 2, 3, 4, 5, 6, 7, 8]\nwords = ["apple", "hi", "banana"]\nmatrix = [[1, 2], [3, 4], [5, 6]]\n',
        'solution': (
            "nums = [1, 2, 3, 4, 5, 6, 7, 8]\n"
            "words = ['apple', 'hi', 'banana']\n"
            "matrix = [[1, 2], [3, 4], [5, 6]]\n"
            "squares = [n * n for n in range(1, 11)]\n"
            "evens = [n for n in nums if n % 2 == 0]\n"
            "lengths = {w: len(w) for w in words}\n"
            "matrix_flat = [x for row in matrix for x in row]\n"
            "classified = {\n"
            "    'even': [n for n in nums if n % 2 == 0],\n"
            "    'odd': [n for n in nums if n % 2 == 1],\n"
            "}\n"
            "print(squares)\n"
            "print(evens, lengths)\n"
            "print(matrix_flat, classified)\n"
        ),
        'checks': [
            "assert squares == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100], 'squares 不对：%r' % (squares,)",
            "assert evens == [2, 4, 6, 8], 'evens 不对：%r' % (evens,)",
            "assert lengths == {'apple': 5, 'hi': 2, 'banana': 6}, 'lengths 不对：%r' % (lengths,)",
            "assert matrix_flat == [1, 2, 3, 4, 5, 6], 'matrix_flat 不对：%r' % (matrix_flat,)",
            "assert classified == {'even': [2, 4, 6, 8], 'odd': [1, 3, 5, 7]}, 'classified 不对：%r' % (classified,)",
        ],
        'explanation': (
            '推导式把「建容器 → 遍历 → 判断 → 追加」四步压缩成一行，'
            '而且比手写循环**更快**（内部不为每次循环建栈帧）。\n\n'
            '四种形态：\n\n'
            '```python\n'
            '[表达式 for x in 可迭代]                     # 列表\n'
            '[表达式 for x in 可迭代 if 条件]              # 带过滤\n'
            '{k: v for x in 可迭代}                       # 字典\n'
            '[x for row in matrix for x in row]           # 嵌套（外层在前）\n'
            '```\n\n'
            '嵌套推导式的顺序容易搞错：`for row in matrix` 在外层，'
            '`for x in row` 在内层，**和写普通循环的缩进顺序完全一致**。\n\n'
            '什么时候不该用推导式？当表达式长到需要换行、或者有副作用（比如打印、发请求）时，'
            '老老实实写 for 循环更清楚。**推导式是用来「造数据」的，不是用来「干活」的。**'
        ),
        'expected_output': '[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]\n[2, 4, 6, 8] {\'apple\': 5, \'hi\': 2, \'banana\': 6}\n[1, 2, 3, 4, 5, 6] {\'even\': [2, 4, 6, 8], \'odd\': [1, 3, 5, 7]}',
        'hints': ['字典推导式用 {k: v for ...}', '压平嵌套列表：for row in matrix 写在前面'],
    },
    {
        'id': 'ch12-02',
        'chapter_id': 12,
        'title': '装饰器：给函数加上「计时」和「重试」',
        'difficulty': 3,
        'tags': ['装饰器', '闭包', 'functools'],
        'statement': (
            '写两个装饰器：\n\n'
            '1. `@timer`：打印被装饰函数的名字和返回值，然后返回原结果。'
            '输出格式：`函数 add 返回 5`\n'
            '2. `@retry(times=3)`：**带参数**的装饰器。被装饰的函数抛异常时自动重试，'
            '最多重试 `times` 次；全部失败则把最后一次异常抛出；成功则返回结果。\n\n'
            '然后用它们装饰函数并验证：\n\n'
            '```python\n'
            '@timer\n'
            'def add(a, b):\n'
            '    return a + b\n'
            '```\n\n'
            '以及一个前两次失败、第三次成功的函数，验证 `@retry(times=3)` 能救回来。\n'
            '（提示：装饰器要用 `functools.wraps` 保留原函数信息。）'
        ),
        'starter_code': 'import functools\n\ndef timer(func):\n    pass\n',
        'solution': (
            "import functools\n"
            "\n"
            "def timer(func):\n"
            "    @functools.wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        result = func(*args, **kwargs)\n"
            "        print(f'函数 {func.__name__} 返回 {result}')\n"
            "        return result\n"
            "    return wrapper\n"
            "\n"
            "\n"
            "def retry(times=3):\n"
            "    def decorator(func):\n"
            "        @functools.wraps(func)\n"
            "        def wrapper(*args, **kwargs):\n"
            "            last = None\n"
            "            for _ in range(times):\n"
            "                try:\n"
            "                    return func(*args, **kwargs)\n"
            "                except Exception as exc:\n"
            "                    last = exc\n"
            "            raise last\n"
            "        return wrapper\n"
            "    return decorator\n"
            "\n"
            "\n"
            "@timer\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "\n"
            "calls = {'n': 0}\n"
            "\n"
            "@retry(times=3)\n"
            "def flaky():\n"
            "    calls['n'] += 1\n"
            "    if calls['n'] < 3:\n"
            "        raise RuntimeError('还没成功')\n"
            "    return 'ok'\n"
            "\n"
            "\n"
            "print(add(2, 3))\n"
            "print(flaky(), calls['n'])\n"
        ),
        'checks': [
            "@timer",
            "def _double(x):",
            "    return x * 2",
            "assert _double(4) == 8, 'timer 装饰后返回值应保持不变'",
            "assert _double.__name__ == '_double', '装饰器必须用 functools.wraps 保留原函数名'",
            "assert '函数 add 返回 5' in _out, '你的示例代码里应该有 print(add(2, 3))，让 timer 打印出「函数 add 返回 5」'",
            "calls = []",
            "@retry(times=3)",
            "def _boom():",
            "    calls.append(1)",
            "    if len(calls) < 3:",
            "        raise RuntimeError('还没成功')",
            "    return 'ok'",
            "assert _boom() == 'ok', '前两次失败、第三次成功时，retry 应该救回来'",
            "assert len(calls) == 3, 'times=3 时最多调用 3 次，实际 %d 次' % len(calls)",
            "fails = []",
            "@retry(times=2)",
            "def _always_fail():",
            "    fails.append(1)",
            "    raise ValueError('一直失败')",
            "try:",
            "    _always_fail()",
            "    raise AssertionError('全部失败时必须把异常抛出来，不能静默返回 None')",
            "except ValueError:",
            "    pass",
            "assert len(fails) == 2, 'times=2 时应该尝试 2 次，实际 %d 次' % len(fails)",
        ],
        'explanation': (
            '装饰器的本质是「**接收函数，返回新函数**」的高阶函数：'
            '`@timer` 等价于 `add = timer(add)`。'
            '理解这一点，所有装饰器都不神秘了。\n\n'
            '`wrapper(*args, **kwargs)` 里的星号参数是为了「透传」——'
            '被装饰的函数有几个参数、怎么传的，wrapper 不需要知道。\n\n'
            '`@functools.wraps(func)` 一定要加。没有它，'
            '`add.__name__` 会变成 `"wrapper"`，文档字符串也没了，'
            '调试和自动生成文档时全是错的名字。\n\n'
            '**带参数的装饰器要多包一层**：`retry(times=3)` 先执行并返回 `decorator`，'
            '`decorator` 才是真正的装饰器。三层嵌套看起来绕，'
            '但只要记住「最外层收参数，中层收函数，内层收调用参数」就不会写错。\n\n'
            '`raise last` 抛的是最后一次的异常，'
            '这样调用方能拿到真正的原因，而不是一个笼统的「都失败了」。'
        ),
        'expected_output': "函数 add 返回 5\n5\nok 3",
        'hints': ['wrapper 要用 *args, **kwargs 透传参数', '带参数的装饰器需要三层函数嵌套'],
    },
    {
        'id': 'ch12-03',
        'chapter_id': 12,
        'title': '生成器：处理大文件不爆内存',
        'difficulty': 3,
        'tags': ['生成器', 'yield', '迭代器'],
        'statement': (
            '写一个生成器函数 `read_lines(lines)`，接收一个字符串列表，'
            '**逐行返回**（用 `yield`）：\n\n'
            '- 跳过空行和以 `#` 开头的注释行\n'
            '- 每行去掉首尾空白\n'
            '- 调用方拿到的是一个「每次只产生一行」的迭代器\n\n'
            '再写一个生成器 `countdown(n)`：从 n 倒数到 1，每次 yield 一个数字。\n\n'
            '要求：\n'
            '1. 打印 `read_lines` 处理后的行数和内容列表\n'
            '2. 把 `countdown(5)` 转成列表打印\n'
            '3. **必须用 yield**，用 `return [...]` 建列表不给分'
        ),
        'starter_code': 'def read_lines(lines):\n    pass\n\ndef countdown(n):\n    pass\n',
        'solution': (
            "def read_lines(lines):\n"
            "    for line in lines:\n"
            "        text = line.strip()\n"
            "        if not text or text.startswith('#'):\n"
            "            continue\n"
            "        yield text\n"
            "\n"
            "\n"
            "def countdown(n):\n"
            "    while n > 0:\n"
            "        yield n\n"
            "        n -= 1\n"
            "\n"
            "\n"
            "raw = ['  host = localhost  ', '', '# 这是注释', 'port = 8080', '   ', 'debug = True']\n"
            "kept = list(read_lines(raw))\n"
            "print(len(kept), kept)\n"
            "print(list(countdown(5)))\n"
        ),
        'checks': [
            "raw = ['  a = 1  ', '', '# c', 'b = 2']",
            "assert list(read_lines(raw)) == ['a = 1', 'b = 2'], 'read_lines 过滤/去空白结果不对：%r' % list(read_lines(raw))",
            "gen = read_lines(['x = 1', 'y = 2'])",
            "assert hasattr(gen, '__next__'), 'read_lines 应该返回生成器（迭代器）'",
            "assert list(countdown(5)) == [5, 4, 3, 2, 1], 'countdown(5) 应为 [5, 4, 3, 2, 1]'",
            "assert list(countdown(0)) == [], 'countdown(0) 应为空'",
            "assert 'yield' in _src, '本题必须使用 yield 实现生成器'",
            "assert '6' in _out or '4' in _out, '应打印处理后的行数'",
        ],
        'explanation': (
            '普通函数 `return` 一次就结束；生成器函数遇到 `yield` 会**暂停并保存现场**，'
            '下次 `next()` 时从暂停处继续。所以它不占内存——'
            '处理 10GB 日志和 10 行数据占用的内存是一样的。\n\n'
            '关键区别：\n\n'
            '```python\n'
            "def f_list(items):  return [x for x in items if x]   # 先把全部算出来\n"
            "def f_gen(items):   yield from (x for x in items if x)  # 用一行算一行\n"
            '```\n\n'
            '生成器还有个常见坑：**只能消费一次**。'
            '`gen = read_lines(raw)` 之后遍历一次就空了，'
            '想再用得重新调用函数。所以上面测试里每次都重新 `list(read_lines(...))`。\n\n'
            '`read_lines` 里同时用了 `continue`（跳过）和 `yield`（产出），'
            '这就是「管道」思路：一个生成器负责过滤，上层再消费。'
            '多个生成器串起来（`map`/`filter` 也是生成器式的），'
            '可以做到「读一行、处理一行、写一行」，中间不落任何大列表。'
        ),
        'expected_output': "4 ['host = localhost', 'port = 8080', 'debug = True']\n[5, 4, 3, 2, 1]",
        'hints': ['生成器函数里用 yield 而不是 return', '调用方通常用 list() 或 for 来消费它'],
    },
    {
        'id': 'ch12-04',
        'chapter_id': 12,
        'title': 'lambda 与 sorted 的组合技',
        'difficulty': 2,
        'tags': ['lambda', 'sorted', '高阶函数'],
        'statement': (
            '已知一组学生记录（四个名字的字数各不相同，方便验证「按名字长度排序」）：\n\n'
            '```python\n'
            "students = [\n"
            "    {'name': '李', 'score': 72, 'age': 17},\n"
            "    {'name': '小明', 'score': 88, 'age': 18},\n"
            "    {'name': '王小刚', 'score': 95, 'age': 16},\n"
            "    {'name': '欧阳小红', 'score': 88, 'age': 16},\n"
            "]\n"
            '```\n\n'
            '用 `sorted` + `lambda` 完成（每个结果各存一个变量）：\n\n'
            '1. `by_score`：按分数从高到低\n'
            '2. `by_score_then_age`：分数从高到低，分数相同的按年龄**从小到大**\n'
            '3. `by_name_len`：按名字字数从少到多\n'
            '4. 用 `max` + `lambda` 找出分数最高的学生，存进 `top_student`\n'
            '5. 打印 `by_score_then_age` 里每个人的名字，以及 `top_student["name"]`\n\n'
            '（提示：第 1 和第 2 个结果应当**不一样**——小明和欧阳小红分数相同但年龄不同。）'
        ),
        'starter_code': "students = [\n    {'name': '李', 'score': 72, 'age': 17},\n    {'name': '小明', 'score': 88, 'age': 18},\n    {'name': '王小刚', 'score': 95, 'age': 16},\n    {'name': '欧阳小红', 'score': 88, 'age': 16},\n]\n",
        'solution': (
            "students = [\n"
            "    {'name': '李', 'score': 72, 'age': 17},\n"
            "    {'name': '小明', 'score': 88, 'age': 18},\n"
            "    {'name': '王小刚', 'score': 95, 'age': 16},\n"
            "    {'name': '欧阳小红', 'score': 88, 'age': 16},\n"
            "]\n"
            "by_score = sorted(students, key=lambda s: s['score'], reverse=True)\n"
            "by_score_then_age = sorted(students, key=lambda s: (-s['score'], s['age']))\n"
            "by_name_len = sorted(students, key=lambda s: len(s['name']))\n"
            "top_student = max(students, key=lambda s: s['score'])\n"
            "print([s['name'] for s in by_score_then_age])\n"
            "print(top_student['name'])\n"
        ),
        'checks': [
            "assert [s['name'] for s in by_score] == ['王小刚', '小明', '欧阳小红', '李'], 'by_score 顺序不对：%r' % [s['name'] for s in by_score]",
            "assert [s['name'] for s in by_score_then_age] == ['王小刚', '欧阳小红', '小明', '李'], '多级排序不对（88 分的两人要按年龄从小到大）：%r' % [s['name'] for s in by_score_then_age]",
            "assert [s['name'] for s in by_name_len] == ['李', '小明', '王小刚', '欧阳小红'], 'by_name_len 顺序不对：%r' % [s['name'] for s in by_name_len]",
            "assert top_student['name'] == '王小刚', 'top_student 应为王小刚'",
            "assert students[0]['name'] == '李', '原列表不应被改动（sorted 返回新列表）'",
        ],
        'explanation': (
            '`key` 参数接收一个函数，`sorted` 用它把每个元素「映射」成用来比较的东西。'
            '`lambda s: s["score"]` 就是一个匿名小函数：'
            '「给我一条学生记录，返回他的分数」。\n\n'
            '**多级排序**用返回元组的技巧：`(-s["score"], s["age"])` 表示'
            '先按分数降序（负号实现），分数相同时按年龄升序。'
            '如果两级都要降序，就两个都加负号（数字才加，字符串不能）。\n\n'
            '`max(students, key=...)` 和 `sorted` 是同一个套路：'
            '`key` 决定「按什么比」。用 `max` 比「先排序再取第一个」快，'
            '因为它是 O(n) 而不是 O(n log n)。\n\n'
            'lambda 的适用边界：**只写一行、只用一次**。'
            '逻辑一复杂或需要复用，就该定义成有名字的函数——'
            '给函数起名字本身就是最好的注释。'
        ),
        'expected_output': "['小红', '小明', '小刚', '小美']\n小红",
        'hints': ['降序可以给 key 加负号，或者用 reverse=True', '多级排序让 key 返回元组'],
    },

    # ── 第 13 章 第三方库、并发与异步 ──────────────────────
    {
        'id': 'ch13-01',
        'chapter_id': 13,
        'title': 'threading：让两件事同时干',
        'difficulty': 3,
        'tags': ['并发', 'threading', '锁'],
        'statement': (
            '用 `threading` 让两个「耗时任务」并发执行：\n\n'
            '1. 定义 `work(name, delay)`：模拟耗时任务，'
            '把 `name` 追加到一个**共享**列表 `log` 里（追加时加锁），'
            '然后用 `time.sleep(delay)` 睡一小会儿\n'
            '2. 创建两个线程分别跑 `work("A", 0.15)` 和 `work("B", 0.05)`，'
            '用 `start()` 启动、`join()` 等待\n'
            '3. 记录总耗时 `elapsed`\n\n'
            '要求：\n'
            '- 共享列表必须用 `threading.Lock()` 保护\n'
            '- 打印 `log` 和总耗时（保留 2 位小数）\n'
            '- 验证并发有效：总耗时应**明显小于** 0.20 秒'
        ),
        'starter_code': 'import threading\nimport time\nlog = []\nlock = threading.Lock()\n',
        'solution': (
            "import threading\n"
            "import time\n"
            "log = []\n"
            "lock = threading.Lock()\n"
            "\n"
            "def work(name, delay):\n"
            "    with lock:\n"
            "        log.append(name)\n"
            "    time.sleep(delay)\n"
            "\n"
            "start = time.time()\n"
            "t1 = threading.Thread(target=work, args=('A', 0.15))\n"
            "t2 = threading.Thread(target=work, args=('B', 0.05))\n"
            "t1.start()\n"
            "t2.start()\n"
            "t1.join()\n"
            "t2.join()\n"
            "elapsed = round(time.time() - start, 2)\n"
            "print(sorted(log), elapsed)\n"
            "print('并发生效' if elapsed < 0.18 else '像是串行执行的')\n"
        ),
        'checks': [
            "assert sorted(log) == ['A', 'B'], '两个任务都应该执行，log 应为 [\\'A\\', \\'B\\']'",
            "assert elapsed < 0.19, '总耗时 %.2f 秒，说明两个任务没有真正并发（串行需要 0.20 秒）' % elapsed",
            "assert '并发生效' in _out, '应打印并发生效的结论'",
            "assert 'Lock' in _src or 'lock' in _src, '共享列表必须加锁保护'",
        ],
        'explanation': (
            '`time.sleep()` 会让出 CPU，所以两个线程能真正重叠：'
            'A 睡 0.15 秒的同时 B 在睡 0.05 秒，总耗时接近 0.15 而不是 0.20。\n\n'
            '`lock` 保护的是「读-改-写」这类**非原子**操作。'
            '`list.append` 本身是原子的（CPython 实现保证了），'
            '但一旦写成像「先读长度再插入」的两步操作，不加锁就会丢数据。'
            '习惯上加锁，比事后查诡异的偶发 bug 便宜得多。\n\n'
            '`join()` 不能省：没有它主线程会直接往下走，'
            '`elapsed` 会在任务结束前就被算出来，还可能出现程序退出把线程掐死的情况。\n\n'
            'Python 有 GIL，**CPU 密集型任务用多线程不会变快**（同一时刻只有一个线程在执行字节码）。'
            '多线程的价值在 I/O 密集场景——等网络、等磁盘、等数据库时，'
            '线层会释放 GIL，别人就能干活。想让 CPU 密集也变快，要用 `multiprocessing`。'
        ),
        'expected_output': "['A', 'B'] 0.15\n并发生效",
        'hints': ['start() 启动线程，join() 等它结束', '共享数据用 with lock: 包起来'],
    },
    {
        'id': 'ch13-02',
        'chapter_id': 13,
        'title': '标准库扫盲：用对工具少写代码',
        'difficulty': 2,
        'tags': ['标准库', 'collections', 'random', 'datetime'],
        'statement': (
            '用标准库解决四个小问题（不要自己造轮子）：\n\n'
            '1. 用 `collections.Counter` 统计 `"abracadabra"` 里每个字母出现次数，'
            '存进 `letter_count`，并取出出现次数最多的 2 个（列表 `top2`）\n'
            '2. 用 `collections.defaultdict(list)` 把 `[("水果", "苹果"), ("蔬菜", "白菜"), ("水果", "香蕉")]` '
            '归并成 `{"水果": ["苹果", "香蕉"], "蔬菜": ["白菜"]}`，存进 `grouped`\n'
            '3. 用 `random.Random(42)` 固定种子，从 1~100 里取 5 个不重复的随机数，存进 `picked`（列表）\n'
            '4. 用 `datetime` 把字符串 `"2026-09-16"` 解析成日期对象，存进 `day`，'
            '并算出它是星期几（中文，存进 `weekday`）\n\n'
            '最后把 `top2`、`grouped`、`len(picked)`、`weekday` 打印出来。'
        ),
        'starter_code': 'from collections import Counter, defaultdict\nimport random\nfrom datetime import datetime\n',
        'solution': (
            "from collections import Counter, defaultdict\n"
            "import random\n"
            "from datetime import datetime\n"
            "\n"
            "letter_count = Counter('abracadabra')\n"
            "top2 = [item for item, _ in letter_count.most_common(2)]\n"
            "\n"
            "grouped = defaultdict(list)\n"
            "for category, name in [('水果', '苹果'), ('蔬菜', '白菜'), ('水果', '香蕉')]:\n"
            "    grouped[category].append(name)\n"
            "grouped = dict(grouped)\n"
            "\n"
            "rng = random.Random(42)\n"
            "picked = rng.sample(range(1, 101), 5)\n"
            "\n"
            "day = datetime.strptime('2026-09-16', '%Y-%m-%d')\n"
            "names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']\n"
            "weekday = names[day.weekday()]\n"
            "print(top2, grouped)\n"
            "print(len(picked), weekday)\n"
        ),
        'checks': [
            "assert letter_count['a'] == 5, '字母 a 应出现 5 次，实际 %r' % letter_count['a']",
            "assert sorted(top2) == ['a', 'b'], '出现最多的两个字母应为 a 和 b，实际 %r' % (top2,)",
            "assert dict(grouped) == {'水果': ['苹果', '香蕉'], '蔬菜': ['白菜']}, '分组结果不对：%r' % (dict(grouped),)",
            "assert len(picked) == 5 and len(set(picked)) == 5, '应取到 5 个不重复的随机数'",
            "assert all(1 <= n <= 100 for n in picked), '随机数应在 1~100 之间'",
            "assert day.year == 2026 and day.month == 9 and day.day == 16, '日期解析不对：%r' % (day,)",
            "assert weekday in ('星期二', '星期三'), '2026-09-16 的星期算错了：%r' % (weekday,)",
        ],
        'explanation': (
            '**会查标准库，比会背语法更能省时间。** Python 自带「电池」，'
            '这四个模块覆盖了日常最高频的需求：\n\n'
            '- `Counter`：一行搞定词频统计，`most_common(n)` 直接给排行前 n；\n'
            '- `defaultdict(list)`：再也不用写 `if k not in d: d[k] = []`；\n'
            '- `random.Random(seed)`：**固定种子 = 结果可复现**。'
            '测试里需要随机数据时一定要固定种子，否则失败了没法重现；\n'
            '- `datetime.strptime`：按格式解析字符串，`%Y-%m-%d` 是「四位年-两位月-两位日」。\n\n'
            '`datetime.weekday()` 返回 0 表示**星期一**（这是 Python 的设计），'
            '而 `isoweekday()` 返回 1 表示星期一。这两个容易记反，'
            '所以这里用一个中文名字列表来映射，比硬记偏移量可靠。\n\n'
            '`random.sample(population, k)` 是**不重复抽样**，'
            '`random.choice` 会重复、`random.shuffle` 是原地打乱。'
            '组卷抽题时用的就是 `sample` 这类的思路。'
        ),
        'expected_output': "['a', 'b'] {'水果': ['苹果', '香蕉'], '蔬菜': ['白菜']}\n5 星期三",
        'hints': ['Counter(字符串) 直接得到字母计数', 'defaultdict(list) 可以省掉「键不存在就建列表」的判断'],
    },

    # ── 第 14 章 综合训练 ─────────────────────────────────
    {
        'id': 'ch14-01',
        'chapter_id': 14,
        'title': '综合：学生成绩管理小系统',
        'difficulty': 3,
        'tags': ['综合', '字典', '函数', '排序'],
        'statement': (
            '实现一个纯函数式的成绩管理（不用类，全部用函数 + 字典）：\n\n'
            '```python\n'
            "records = [\n"
            "    {'name': '小明', 'scores': [88, 92, 76]},\n"
            "    {'name': '小红', 'scores': [95, 91, 100]},\n"
            "    {'name': '小刚', 'scores': [60, 72, 58]},\n"
            "]\n"
            '```\n\n'
            '要求实现四个函数：\n\n'
            '1. `average(scores)`：返回平均分，保留 2 位；空列表返回 0\n'
            '2. `rank(records)`：返回按平均分从高到低排序的 `[(名字, 平均分), ...]`\n'
            '3. `class_stats(records)`：返回 `{"count": 人数, "avg": 全班平均(2位), '
            '"best": 最高分者名字, "worst": 最低分者名字}`\n'
            '4. `level(avg)`：按平均分返回等级（≥90 优秀 / ≥80 良好 / ≥60 及格 / 否则 不及格）\n\n'
            '最后打印 `rank(records)`、`class_stats(records)`，以及每个人的等级。'
        ),
        'starter_code': "records = [\n    {'name': '小明', 'scores': [88, 92, 76]},\n    {'name': '小红', 'scores': [95, 91, 100]},\n    {'name': '小刚', 'scores': [60, 72, 58]},\n]\n",
        'solution': (
            "records = [\n"
            "    {'name': '小明', 'scores': [88, 92, 76]},\n"
            "    {'name': '小红', 'scores': [95, 91, 100]},\n"
            "    {'name': '小刚', 'scores': [60, 72, 58]},\n"
            "]\n"
            "\n"
            "def average(scores):\n"
            "    if not scores:\n"
            "        return 0\n"
            "    return round(sum(scores) / len(scores), 2)\n"
            "\n"
            "\n"
            "def rank(records):\n"
            "    return sorted(((r['name'], average(r['scores'])) for r in records),\n"
            "                  key=lambda item: item[1], reverse=True)\n"
            "\n"
            "\n"
            "def class_stats(records):\n"
            "    if not records:\n"
            "        return {'count': 0, 'avg': 0, 'best': None, 'worst': None}\n"
            "    scored = [(r['name'], average(r['scores'])) for r in records]\n"
            "    all_scores = [s for r in records for s in r['scores']]\n"
            "    return {\n"
            "        'count': len(records),\n"
            "        'avg': average(all_scores),\n"
            "        'best': max(scored, key=lambda i: i[1])[0],\n"
            "        'worst': min(scored, key=lambda i: i[1])[0],\n"
            "    }\n"
            "\n"
            "\n"
            "def level(avg):\n"
            "    if avg >= 90:\n"
            "        return '优秀'\n"
            "    if avg >= 80:\n"
            "        return '良好'\n"
            "    if avg >= 60:\n"
            "        return '及格'\n"
            "    return '不及格'\n"
            "\n"
            "\n"
            "print(rank(records))\n"
            "print(class_stats(records))\n"
            "for name, avg in rank(records):\n"
            "    print(name, avg, level(avg))\n"
        ),
        'checks': [
            "assert average([]) == 0, '空列表平均分应为 0'",
            "assert average([88, 92, 76]) == 85.33, '平均分应为 85.33，实际 %r' % average([88, 92, 76])",
            "assert rank(records)[0][0] == '小红', '第一名应为小红'",
            "assert rank(records)[-1][0] == '小刚', '最后一名应为小刚'",
            "assert class_stats(records) == {'count': 3, 'avg': 81.33, 'best': '小红', 'worst': '小刚'}, '班级统计不对：%r' % (class_stats(records),)",
            "assert level(95) == '优秀' and level(80) == '良好' and level(60) == '及格' and level(59.9) == '不及格', '等级判定边界不对'",
            "assert class_stats([])['count'] == 0, '空记录时不应报错'",
            "assert _out.count('小红') >= 2, '应打印排名与等级明细'",
        ],
        'explanation': (
            '这道题把前面 13 章的东西串了一遍：函数定义、字典取值、列表推导式、'
            '`sorted` + `lambda`、边界处理。写法上有几个值得注意的地方：\n\n'
            '**`average` 被复用了 3 次**（个人均分、班级均分、排名）。'
            '把「算平均」这个小逻辑抽成函数，就不用到处复制粘贴公式——'
            '将来要改成「去掉最高最低再平均」，只改一个地方。\n\n'
            '`sorted(生成器, key=...)` 里的生成器表达式是常用的写法：'
            '不需要先建中间列表，直接产出待排序的元组流。\n\n'
            '`class_stats` 里 `all_scores = [s for r in records for s in r["scores"]]` '
            '是嵌套推导式做「压平」，把所有人的所有分数摊成一维列表。\n\n'
            '`max(scored, key=lambda i: i[1])[0]` 用 `[0]` 取出名字，'
            '因为前面构造的是 `(名字, 分数)` 的元组。\n\n'
            '**边界处理是这道题真正的考点**：空列表、空记录，'
            '真实项目里这些情况一定会出现，代码不能在这里崩。'
        ),
        'expected_output': "[('小红', 95.33), ('小明', 85.33), ('小刚', 63.33)]\n{'count': 3, 'avg': 81.33, 'best': '小红', 'worst': '小刚'}\n小红 95.33 优秀\n小明 85.33 良好\n小刚 63.33 及格",
        'hints': ['average 要能处理空列表', 'scores 压平：for r in records for s in r["scores"]'],
    },
    {
        'id': 'ch14-02',
        'chapter_id': 14,
        'title': '综合：文本词频报告生成器',
        'difficulty': 3,
        'tags': ['综合', '字符串', '字典', '格式化'],
        'statement': (
            '写一个 `word_report(text, top_n=3)` 函数，生成一段文本报告：\n\n'
            '要求：\n'
            '1. 用正则 `re.findall(r"[a-zA-Z\']+", text.lower())` 提取所有英文单词'
            '（长度 ≤ 2 的词算停用词，要过滤掉，比如 a、is）\n'
            '2. 统计词频，取前 `top_n` 个（按次数降序，次数相同按字母序）\n'
            '3. 返回一个**多行字符串**，格式如下：\n\n'
            '```\n'
            '单词总数: 12\n'
            '不重复单词: 8\n'
            'TOP 3:\n'
            '1. the (3 次)\n'
            '2. and (2 次)\n'
            '3. fox (2 次)\n'
            '```\n\n'
            '然后对 `"The quick brown fox jumps over the lazy dog. The fox is quick, and the dog is lazy!"` '
            '调用一次并打印结果。'
        ),
        'starter_code': 'import re\n\ndef word_report(text, top_n=3):\n    pass\n',
        'solution': (
            "import re\n"
            "\n"
            "def word_report(text, top_n=3):\n"
            "    words = [w for w in re.findall(r\"[a-zA-Z']+\", text.lower()) if len(w) > 2]\n"
            "    counter = {}\n"
            "    for w in words:\n"
            "        counter[w] = counter.get(w, 0) + 1\n"
            "    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]\n"
            "    lines = [f'单词总数: {len(words)}', f'不重复单词: {len(counter)}', f'TOP {top_n}:']\n"
            "    for i, (word, count) in enumerate(ranked, 1):\n"
            "        lines.append(f'{i}. {word} ({count} 次)')\n"
            "    return '\\n'.join(lines)\n"
            "\n"
            "\n"
            "text = 'The quick brown fox jumps over the lazy dog. The fox is quick, and the dog is lazy!'\n"
            "print(word_report(text))\n"
        ),
        'checks': [
            "text = 'The quick brown fox jumps over the lazy dog. The fox is quick, and the dog is lazy!'",
            "report = word_report(text)",
            "assert isinstance(report, str), '应返回字符串'",
            "assert '单词总数: 16' in report, '单词总数不对（is 只有 2 个字母也得算进去）：\\n%s' % report",
            "assert '不重复单词: 9' in report, '不重复单词数不对：\\n%s' % report",
            "assert 'TOP 3:' in report, '缺少 TOP 3: 标题'",
            "assert '1. the (4 次)' in report, 'the 应出现 4 次且排第一：\\n%s' % report",
            "assert '2. dog (2 次)' in report, '第二名应为 dog（dog 与 fox 都是 2 次，按字母序 dog 在前）：\\n%s' % report",
            "assert '3. fox (2 次)' in report, '第三名应为 fox：\\n%s' % report",
            "assert len(word_report(text, top_n=1).splitlines()) == 4, 'top_n=1 时应只列出 1 个词'",
            "assert '单词总数: 0' in word_report('', top_n=3), '空文本也要能生成报告，不能报错'",
        ],
        'explanation': (
            '这是一道「真实工程里会遇到」的题：把一堆文本变成一份人看得懂的报告。\n\n'
            '**正则提取**用 `[a-zA-Z\']+`：匹配连续字母（以及撇号，为了别把 `don\'t` 拆开）。'
            '`text.lower()` 先统一小写，否则 `The` 和 `the` 会被算成两个词——'
            '这是词频统计最常见的错误。\n\n'
            '为什么过掉长度 ≤ 2 的词？因为 `a`、`is` 这类词频极高但没有信息量'
            '（这就是「停用词」概念的雏形）。\n\n'
            '输出用 `"\\n".join(lines)` 而不是反复 `+=` 拼字符串：'
            '字符串在 Python 里是**不可变**的，每次 `+=` 都会新建一个字符串，'
            '在循环里拼几千行会明显变慢。'
            '先收集到列表再 join，是标准做法。\n\n'
            '`enumerate(ranked, 1)` 的第二个参数让序号从 1 开始，'
            '省掉了 `i + 1` 这种手动偏移。'
        ),
        'expected_output': '单词总数: 16\n不重复单词: 9\nTOP 3:\n1. the (4 次)\n2. dog (2 次)\n3. fox (2 次)',
        'hints': ['先 lower() 再统计，否则大小写会分成两个词', '拼多行文本用 "\\n".join(列表)'],
    },
]
