"""题库 · 西安科技大学 823《数据结构与算法》· 教材前四章（专题 127–130）。

写法约定与 qbank_408.py / qbank_basic.py / qbank_pro.py / qbank_algo.py 保持一致：

- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式：
  下标从 0 还是从 1 开始、返回 True 还是 None、越界怎么办，全部写死，不留模糊地带；
- checks 是**字符串列表**，判题时与学生的代码在**同一个全局命名空间**里执行：
  可以直接调用学生定义好的函数 / 类，也可以用平台注入的 `_out`（学生的全部标准输出）
  与 `_src`（学生的全部源码）做检查。每条断言都带中文失败提示。
- 边界一律覆盖：空表 / 空串、单元素、重复元素、越界下标、头结点 / 尾结点等；
- 参考答案必须能通过自己这一整套断言（tools/verify_qbank.py 会全量复验）。

出题口径（823 真题风格）：

- 题目保留老师的原始表述，规格按 Python 补全成「学生能照着写出代码」的样子；
- 绪论与复杂度：对数阶循环计数（O(log n)）、嵌套循环与单层循环的执行次数对比（O(n²) / O(n)）；
- 线性表：顺序表指定位置删除（手写前移）、带头结点单链表指定位置插入、带头结点单链表
  就地逆置、双向链表删除指定结点（只改相邻指针，不遍历）；
- 栈和队列：括号匹配、后缀表达式求值（注意除法向零截断）、牺牲一个存储位置的循环队列；
- 串、数组与广义表：KMP 的 next 数组（下标从 0 起，next[0] = -1）、对称矩阵压缩存储
  与下标换算、广义表的 head / tail 运算。

凡是链表、双链表一律要求先定义题面给定的结点类（属性名必须一致），
算法直接在结点上改指针，不许把值拷进列表「绕开」指针操作。

专题划分：

    127 823·绪论与复杂度     128 823·线性表
    129 823·栈和队列         130 823·串数组与广义表

编号 x823-001 … x823-012，落在 x823-001 … x823-099 区间内。

（说明：本文件按教材第 1–4 章重新编排；此前同名文件是「专题 127–129 基础篇」的 21 道题，
已原样备份为 tools/qbank_xust823a_basic21.py.bak，需要时拷回即可。）
"""

QUESTIONS = [
    # ── 专题 127 823·绪论与复杂度 ─────────────────────────
    {
        'id': 'x823-001',
        'track': 'algorithm',
        'chapter_id': 127,
        'chapter_title': '823·绪论与复杂度',
        'topic': '823·绪论与复杂度',
        'title': '对数阶时间复杂度验证（i = i * 2 循环计数）',
        'difficulty': 1,
        'tags': ['时间复杂度', '对数阶', '大 O 表示法'],
        'statement': (
            '考点：时间复杂度计算、大 O 表示法。\n\n'
            '定义函数 `log_time(n)`，模拟下面这段「i 每轮翻倍」的循环，'
            '统计循环体的**执行次数**和**累加和**：\n\n'
            '```python\n'
            'i = 1\n'
            'while i <= n:\n'
            '    # 循环体：次数加一，并把当前的 i 累加进总和\n'
            '    i *= 2\n'
            '```\n\n'
            '要求：\n\n'
            '- 返回一个二元组 `(count, total)`：`count` 是循环体执行了几次，'
            '`total` 是把每轮循环时的 `i` 累加起来的结果；\n'
            '- `n <= 0` 时循环体一次也不执行，返回 `(0, 0)`；\n'
            '- **必须真的用循环一边走一边计数**（这正是题目要「数出来」的东西），'
            '不许直接拿 `math.log` 之类口算一个结果返回。\n\n'
            '最后依次打印 `log_time(8)`、`log_time(1000)`、`log_time(0)` 的结果。'
        ),
        'starter_code': (
            'def log_time(n):\n'
            '    count = 0\n'
            '    total = 0\n'
            '    i = 1\n'
            '    # while i <= n: 次数加一、把 i 累加进 total、i *= 2\n'
            '    pass\n'
        ),
        'solution': (
            "def log_time(n):\n"
            "    count = 0\n"
            "    total = 0\n"
            "    i = 1\n"
            "    while i <= n:\n"
            "        count += 1\n"
            "        total += i\n"
            "        i *= 2\n"
            "    return count, total\n"
            "\n"
            "print(log_time(8))\n"
            "print(log_time(1000))\n"
            "print(log_time(0))\n"
        ),
        'checks': [
            "assert log_time(8) == (4, 15), 'n = 8 时 i 依次取 1、2、4、8，应返回 (4, 15)，实际 %r' % (log_time(8),)",
            "assert log_time(1) == (1, 1), 'n = 1 时循环体只跑一轮（i = 1），应返回 (1, 1)，实际 %r' % (log_time(1),)",
            "assert log_time(2) == (2, 3) and log_time(7) == (3, 7), 'n = 2 应返回 (2, 3)；n = 7 时 i 取 1、2、4，应返回 (3, 7)，实际 %r / %r' % (log_time(2), log_time(7))",
            "assert log_time(0) == (0, 0), 'n = 0 时循环一次也不执行，应返回 (0, 0)，实际 %r' % (log_time(0),)",
            "assert log_time(-5) == (0, 0), 'n 是负数时也应当返回 (0, 0)，不要报错，实际 %r' % (log_time(-5),)",
            "assert log_time(1024) == (11, 2047), 'n = 1024 = 2 ** 10 时 i 取 1、2、…、1024 共 11 个，应返回 (11, 2047)，实际 %r' % (log_time(1024),)",
            "assert log_time(1000) == (10, 1023), 'n = 1000 时 i 最大只到 512，共 10 轮，总和 1023，实际 %r' % (log_time(1000),)",
            "assert log_time(2 ** 20)[0] == 21, 'n = 2 ** 20 时循环 21 次——规模涨了一百万倍，次数只多了 11 次，这就是 O(log n)，实际 %r' % (log_time(2 ** 20),)",
            "assert log_time(10 ** 6) == (20, 2 ** 20 - 1), 'n = 1000000 时 i 取 1、2、…、524288 共 20 个，总和是 2 ** 20 - 1，实际 %r' % (log_time(10 ** 6),)",
            "_r = log_time(6)\nassert isinstance(_r, tuple) and len(_r) == 2, '要求返回二元组 (次数, 累加和)，实际返回 %r' % (_r,)",
            "assert 'while' in _src or 'for' in _src, '题目要求真的用循环一边走一边计数，不能直接套 log 公式返回'",
        ],
        'explanation': (
            '这题考的是「**循环次数和 n 是什么关系**」，是复杂度分析的入门动作。\n\n'
            '```python\n'
            'i = 1\n'
            'while i <= n:\n'
            '    count += 1\n'
            '    total += i\n'
            '    i *= 2\n'
            '```\n\n'
            '**为什么要看 i 而不是看 n？** 循环次数就是「1、2、4、8、… 一直翻倍，'
            '翻到超过 n 用了几步」。设次数为 k，则 2^(k−1) ≤ n < 2^k，两边取对数得 k ≈ log₂n + 1。'
            '大 O 只保留增长的量级，常数和底数都不写，所以是 **O(log n)**。\n\n'
            '几条值得记住的对照：\n\n'
            '- n = 8 → 4 次；n = 1024 → 11 次；n = 2^20 → 21 次，规模暴涨时次数只是「多几」；\n'
            '- 如果循环体里写的是 `i += 1`，那就是 O(n)；写成 `i *= 2` 才是 O(log n)，'
            '差别只在一个乘号上，却是天壤之别；\n'
            '- 循环条件写成 `i < n` 而不是 `i <= n`，次数会少 1 次，'
            '但这只是常数级差异，不影响 O(log n) 的结论。\n\n'
            '**常见错误**：\n\n'
            '1. 把 `i *= 2` 写成 `i += 2`，算出来就成了 O(n)；\n'
            '2. 忘记处理 `n <= 0`，或者把 i 的初值写错；\n'
            '3. 累加和写成了 1 + 2 + … + n（那是 O(n) 循环的结果，不是本题的 2^k − 1）。\n\n'
            '复杂度：循环次数 ⌊log₂n⌋ + 1，时间 O(log n)、额外空间 O(1)。'
        ),
        'expected_output': '(4, 15)\n(10, 1023)\n(0, 0)',
        'hints': [
            '循环开始前 i = 1，每轮结束时 i *= 2，循环条件是 i <= n',
            '数一数 n = 8 时 i 会取到哪些值（1、2、4、8），就有 4 次',
        ],
    },
    {
        'id': 'x823-002',
        'track': 'algorithm',
        'chapter_id': 127,
        'chapter_title': '823·绪论与复杂度',
        'topic': '823·绪论与复杂度',
        'title': '嵌套循环与单层循环的执行次数对比（O(n²) 与 O(n)）',
        'difficulty': 1,
        'tags': ['时间复杂度', '嵌套循环', 'O(n²)'],
        'statement': (
            '考点：嵌套循环时间复杂度、O(n²) 与 O(n) 的阶区分。\n\n'
            '定义两个函数，用「数循环次数」的办法亲手验证两者的差距：\n\n'
            '1. `count_nested(n)`：两层嵌套的 `for` 循环，**每层都从 0 到 n − 1**，'
            '统计最内层循环体一共执行了多少次，返回这个次数；\n'
            '2. `count_single(n)`：一层 `for` 循环，从 0 到 n − 1，统计循环体执行次数并返回；\n'
            '3. `n <= 0` 时两个函数都返回 `0`（循环不执行）。\n\n'
            '然后对 `n = 10` 和 `n = 100` 各打印一行：`print(n, count_nested(n), count_single(n))`，'
            '对比两个数字的增长速度。\n\n'
            '要求：就是老老实实的嵌套循环和单层循环，'
            '不要用 `n * n`、`n ** 2` 之类的公式代替循环——本题要的是「数出来」的过程。'
        ),
        'starter_code': (
            'def count_nested(n):\n'
            '    total = 0\n'
            '    # 两层 for 循环，每层 0…n-1，每进一次最内层就 total += 1\n'
            '    pass\n'
            '\n'
            'def count_single(n):\n'
            '    total = 0\n'
            '    # 一层 for 循环，每轮 total += 1\n'
            '    pass\n'
        ),
        'solution': (
            "def count_nested(n):\n"
            "    total = 0\n"
            "    for i in range(n):\n"
            "        for j in range(n):\n"
            "            total += 1\n"
            "    return total\n"
            "\n"
            "def count_single(n):\n"
            "    total = 0\n"
            "    for i in range(n):\n"
            "        total += 1\n"
            "    return total\n"
            "\n"
            "for n in (10, 100):\n"
            "    print(n, count_nested(n), count_single(n))\n"
        ),
        'checks': [
            "assert count_nested(10) == 100, '两层各 0…9 的循环，最内层一共跑 10 * 10 = 100 次，实际 %r' % (count_nested(10),)",
            "assert count_nested(1) == 1 and count_nested(0) == 0, 'n = 1 时内层跑 1 次、n = 0 时 0 次，实际 %r / %r' % (count_nested(1), count_nested(0))",
            "assert count_nested(-3) == 0, 'n 是负数时循环不执行，应返回 0，实际 %r' % (count_nested(-3),)",
            "assert count_nested(100) == 10000, 'n = 100 时最内层跑 100 * 100 = 10000 次，实际 %r' % (count_nested(100),)",
            "assert count_nested(1000) == 10 ** 6, 'n = 1000 时是 10 ** 6 次——n 翻 10 倍、次数翻 100 倍，这就是 O(n²)，实际 %r' % (count_nested(1000),)",
            "assert count_single(100) == 100 and count_single(1) == 1, '单层循环 n = 100 应返回 100、n = 1 应返回 1，实际 %r / %r' % (count_single(100), count_single(1))",
            "assert count_single(0) == 0 and count_single(-1) == 0, '单层循环在 n = 0 / 负数时应返回 0，实际 %r / %r' % (count_single(0), count_single(-1))",
            "_n = 50\nassert count_nested(_n) == count_single(_n) ** 2, '同样的 n，嵌套循环的次数应当正好等于单层循环次数的平方（%d ** 2 = %d），实际 %r' % (_n, _n * _n, count_nested(_n))",
            "assert '10 100 10' in _out, 'n = 10 那一行应当包含 10 100 10（请按 print(n, count_nested(n), count_single(n)) 的格式打印）'",
            "assert '100 10000 100' in _out, 'n = 100 那一行应当包含 100 10000 100，用来和第 10 行对比增长速度'",
        ],
        'explanation': (
            '「循环嵌套一层，复杂度就乘一个 n」是本章最常用的结论，这题让你亲手把它数出来。\n\n'
            '```python\n'
            'for i in range(n):        # 外层跑 n 轮\n'
            '    for j in range(n):    # 每轮外层里，内层又跑 n 轮\n'
            '        total += 1        # 一共 n × n 次\n'
            '```\n\n'
            '两行打印的对比很有说服力：n 从 10 涨到 100（10 倍）时，\n\n'
            '- 单层循环：10 → 100，涨了 10 倍（线性）；\n'
            '- 嵌套循环：100 → 10000，涨了 100 倍（平方）。\n\n'
            '**为什么大 O 里不写常数？** 因为要比较的是「n 很大时谁涨得快」。'
            '循环体里执行 1 次还是 3 次运算都是常数倍，写成 O(n²) 就够了；'
            '而 n² 与 n 差的是**量级**：n = 1000 时相差 1000 倍，n = 10^6 时相差 10^6 倍。\n\n'
            '**常见错误**：\n\n'
            '1. 内层写成 `for j in range(i, n)` 或 `range(i + 1, n)`——'
            '那也是 O(n²)（次数为 n(n+1)/2），但本题明确要求「每层都从 0 到 n − 1」，'
            '次数必须是恰好 n²；\n'
            '2. 直接 `return n * n`——题面要的是统计循环次数，而不是套公式；\n'
            '3. 忘了 `n <= 0` 时返回 0（`range(负数)` 本来就不循环，显式说明更稳妥）。\n\n'
            '复杂度：`count_nested` 是 O(n²)、`count_single` 是 O(n)。'
        ),
        'expected_output': '10 100 10\n100 10000 100',
        'hints': [
            '内层循环每被执行到一次就让 total 加一，这就是「数」循环次数的办法',
            '外层 n 轮、内层每轮 n 次，所以总数是 n * n；打印时把三个值放在一行方便对比',
        ],
    },
    # ── 专题 128 823·线性表 ───────────────────────────────
    {
        'id': 'x823-003',
        'track': 'algorithm',
        'chapter_id': 128,
        'chapter_title': '823·线性表',
        'topic': '823·线性表',
        'title': '顺序表指定位置删除（手写元素前移）',
        'difficulty': 1,
        'tags': ['顺序表', '删除', '元素移动次数'],
        'statement': (
            '考点：顺序表删除的元素移动次数、平均时间复杂度。\n\n'
            '已知顺序表（用 Python 列表表示）`arr` 和下标 `pos`（**从 0 开始计数**）。\n\n'
            '定义函数 `delete_seq_list(arr, pos)`：删除 `arr` 中下标为 `pos` 的元素，'
            '把 `pos` 后面的元素**逐个前移一位**，最后让表长减一。\n\n'
            '要求（请逐条对照）：\n\n'
            '- 删除成功返回 `True`；位置非法返回 `False`，而且这时 `arr` **不能有任何变化**；\n'
            '- `pos < 0` 或 `pos >= len(arr)` 都算非法，**空表上删除也是非法**；\n'
            '- **必须手写前移的循环**，例如 `for i in range(pos, len(arr) - 1): arr[i] = arr[i + 1]`；'
            '不许出现 `del`、`arr.remove(...)`、`arr.pop(pos)` 这种「按下标一步删掉目标位置」的写法'
            '（表尾的收尾可以用不带参数的 `arr.pop()`）；\n'
            '- 前移完成后表尾会多出一个空位，用它收尾即可。'
            '注意别写成 `arr = arr[:-1]`——那只是让函数里的局部名字指向一个新列表，'
            '调用方手里的列表一点没变；\n'
            '- 时间是 O(n)：移动元素的平均次数是 (n − 1) / 2，所以顺序表删除的平均时间复杂度是 O(n)；'
            '额外空间 O(1)，只用几个下标变量。\n\n'
            '最后对 `[10, 20, 30, 40, 50]` 删除下标 1 的元素，'
            '打印返回值和删除后的表；再打印一次越界删除（下标 10）的结果。'
        ),
        'starter_code': (
            'def delete_seq_list(arr, pos):\n'
            '    # 1) pos 合法吗？  2) 把 pos 后面的元素前移一位  3) 表长减一\n'
            '    pass\n'
        ),
        'solution': (
            "def delete_seq_list(arr, pos):\n"
            "    if pos < 0 or pos >= len(arr):\n"
            "        return False\n"
            "    for i in range(pos, len(arr) - 1):\n"
            "        arr[i] = arr[i + 1]\n"
            "    arr.pop()\n"
            "    return True\n"
            "\n"
            "data = [10, 20, 30, 40, 50]\n"
            "print(delete_seq_list(data, 1), data)\n"
            "print(delete_seq_list(data, 10), data)\n"
        ),
        'checks': [
            "_a = [10, 20, 30, 40, 50]\n_r = delete_seq_list(_a, 1)\nassert _r is True, '删除合法位置应返回 True，实际 %r' % (_r,)\nassert _a == [10, 30, 40, 50], '删除下标 1 之后表应当变成 [10, 30, 40, 50]，实际 %r' % (_a,)",
            "_b = [1, 2, 3]\n_r = delete_seq_list(_b, 0)\nassert _r is True and _b == [2, 3], '删除下标 0（表头）时后面的元素都要前移，结果应当是 [2, 3]，实际 %r' % (_b,)",
            "_c = [1, 2, 3]\n_r = delete_seq_list(_c, 2)\nassert _r is True and _c == [1, 2], '删除最后一个元素时不需要移动元素，结果应当是 [1, 2]，实际 %r' % (_c,)",
            "_d = [7]\n_r = delete_seq_list(_d, 0)\nassert _r is True and _d == [], '单元素表删掉它应当变成长度为 0 的空表，实际 %r' % (_d,)",
            "_e = [1, 2]\n_r = delete_seq_list(_e, 2)\nassert _r is False and _e == [1, 2], 'pos = len(arr) 越界，应返回 False 且表不变，实际 %r' % (_e,)",
            "_f = [1, 2]\n_r = delete_seq_list(_f, -1)\nassert _r is False and _f == [1, 2], 'pos 是负数算非法（Python 里 -1 会取到最后一个元素，但本题不允许），实际 %r' % (_f,)",
            "_g = []\n_r = delete_seq_list(_g, 0)\nassert _r is False and _g == [], '空表上删除应返回 False（不要抛出异常），实际 %r' % (_r,)",
            "_h = [1, 2, 3]\n_ref = _h\n_r = delete_seq_list(_h, 1)\nassert _ref == [1, 3] and _h is _ref, '要求原地修改：列表对象本身要变短，实际 %r' % (_ref,)",
            "_i = [5, 5, 5, 5]\n_r = delete_seq_list(_i, 2)\nassert _r is True and _i == [5, 5, 5], '有重复元素时按下标删，实际 %r' % (_i,)",
            "_j = list(range(1000))\n_r = delete_seq_list(_j, 500)\nassert _r is True and len(_j) == 999, '1000 个元素删掉 1 个后长度应当是 999，实际 %d' % (len(_j),)\nassert _j[499] == 499 and _j[500] == 501, '前移后下标 500 处应当是原来的 501，实际 %r' % (_j[500],)",
            "assert 'del ' not in _src, '题面要求手写前移的循环，不能用 del 一步删掉元素'",
            "assert '.remove(' not in _src, '题面要求手写前移的循环，不能用 remove() 按值删除'",
            "assert '.pop(' not in _src or '.pop()' in _src, '只允许用不带参数的 arr.pop() 收尾（去掉表尾空位），不能用 arr.pop(下标) 一步删掉目标位置'",
        ],
        'explanation': (
            '顺序表删除要问自己一个问题：**删完之后，后面那些元素到哪儿去了？**\n\n'
            '它们的下标必须**整体减一**，否则表里就会出现一个「洞」——'
            '这正是顺序表删除必须搬移元素的原因，也是它与链表删除最大的区别。\n\n'
            '```python\n'
            'if pos < 0 or pos >= len(arr):\n'
            '    return False\n'
            'for i in range(pos, len(arr) - 1):\n'
            '    arr[i] = arr[i + 1]      # 后一个盖到前一个上\n'
            'arr.pop()                     # 表长减一（去掉尾巴上那份重复的旧值）\n'
            'return True\n'
            '```\n\n'
            '循环到 `len(arr) - 1` 为止，因为最后一次搬移是把 `arr[len - 1]` 盖到 `arr[len - 2]` 上，'
            '再往后就越界了。搬完以后最后一个位置里还留着一份旧值，所以必须把表长减一。\n\n'
            '**元素移动次数**（考试常考的计算）：\n\n'
            '- 删除最后一个元素：移动 0 次；\n'
            '- 删除第一个元素：移动 n − 1 次；\n'
            '- 在等概率假设下（每个位置被删的概率都是 1/n），平均移动次数是 '
            '(0 + 1 + … + (n − 1)) / n = (n − 1) / 2，所以平均时间复杂度是 **O(n)**。\n\n'
            '**常见错误**：\n\n'
            '1. 写成 `arr = arr[:-1]`——局部名字换了个新列表，调用方的列表毫无变化；\n'
            '2. 用 `arr.pop(pos)` 或 `del arr[pos]` 一步删掉——本题的评分点就是手写前移那段循环；\n'
            '3. 忘了判断 `pos < 0`：Python 允许负下标，`arr[-1]` 会删掉最后一个元素，'
            '但按本题约定负数属于非法位置；\n'
            '4. 非法时已经把 `arr` 改坏了才返回 False——判断必须放在动手之前。'
        ),
        'expected_output': 'True [10, 30, 40, 50]\nFalse [10, 30, 40, 50]',
        'hints': [
            '先判 pos 合法性再动手，非法时原表必须原封不动',
            '前移用 for i in range(pos, len(arr) - 1): arr[i] = arr[i + 1]，收尾别忘了让表长减一',
        ],
    },
    {
        'id': 'x823-004',
        'track': 'algorithm',
        'chapter_id': 128,
        'chapter_title': '823·线性表',
        'topic': '823·线性表',
        'title': '带头结点单链表指定位置插入（pos 从 1 开始）',
        'difficulty': 2,
        'tags': ['单链表', '插入', '带头结点', '指针'],
        'statement': (
            '考点：单链表指针操作、插入逻辑。\n\n'
            '请**按下面的定义**写好结点类（属性名必须一致，后面的函数都要用它）：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `insert_pos(head, pos, val)`：在**带头结点**的单链表中，'
            '把值为 `val` 的新结点插到**第 pos 个数据结点**的位置上。\n\n'
            '约定（务必逐条看清）：\n\n'
            '- `head` 是**头结点**（也叫哨兵），它**不存数据**，'
            '真正的第 1 个数据结点是 `head.next`；\n'
            '- `pos` **从 1 开始计数**：`pos = 1` 表示插成第一个数据结点，'
            '`pos = 2` 表示插到原来第 1 个结点之后；\n'
            '- 设原有数据结点个数为 n，则 **1 ≤ pos ≤ n + 1** 都是合法位置，'
            '其中 `pos = n + 1` 表示插到表尾；越界（`pos < 1` 或 `pos > n + 1`）返回 `False`，'
            '此时链表不能有任何变化；\n'
            '- 插入成功返回 `True`（要布尔值本身，不要返回结点或 None）；\n'
            '- 因为带头结点，**头结点对象永远不变**，函数不需要返回新的头指针；\n'
            '- 只允许改指针：先找到第 `pos − 1` 个结点 `prev`，让新结点的 `next` 指向 `prev.next`，'
            '再让 `prev.next` 指向新结点；**不许**把值拷进列表重建链表。\n\n'
            '最后构造带头结点的链表（数据结点依次是 `1 → 2 → 3`），在第 2 个位置插入 9，'
            '打印链表的所有数据值；再打印一次 `pos = 0` 的越界结果和链表的值。'
        ),
        'starter_code': (
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '\n'
            'def insert_pos(head, pos, val):\n'
            '    # 从头结点出发走 pos - 1 步找到前驱 prev，走不到就说明越界\n'
            '    pass\n'
        ),
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def insert_pos(head, pos, val):\n"
            "    if pos < 1:\n"
            "        return False\n"
            "    prev = head\n"
            "    step = 0\n"
            "    while step < pos - 1 and prev is not None:\n"
            "        prev = prev.next\n"
            "        step += 1\n"
            "    if prev is None:\n"
            "        return False\n"
            "    node = Node(val)\n"
            "    node.next = prev.next\n"
            "    prev.next = node\n"
            "    return True\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    node = head.next\n"
            "    while node is not None:\n"
            "        out.append(node.val)\n"
            "        node = node.next\n"
            "    return out\n"
            "\n"
            "head = Node(0)\n"
            "head.next = Node(1, Node(2, Node(3)))\n"
            "print(insert_pos(head, 2, 9))\n"
            "print(values_of(head))\n"
            "print(insert_pos(head, 0, 7))\n"
            "print(values_of(head))\n"
        ),
        'checks': [
            "def _dummy(values):\n    head = Node(0)\n    tail = head\n    for v in values:\n        tail.next = Node(v)\n        tail = tail.next\n    return head",
            "def _vals(head):\n    out = []\n    node = head.next\n    while node is not None:\n        out.append(node.val)\n        node = node.next\n    return out",
            "_h = _dummy([1, 2, 3])\n_r = insert_pos(_h, 2, 9)\nassert _r is True, 'pos = 2 是合法位置，应返回 True，实际 %r' % (_r,)\nassert _vals(_h) == [1, 9, 2, 3], '插入后应当是 [1, 9, 2, 3]，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\ninsert_pos(_h, 1, 9)\nassert _vals(_h) == [9, 1, 2, 3], 'pos = 1 表示插到最前面（插在头结点之后），实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\ninsert_pos(_h, 4, 9)\nassert _vals(_h) == [1, 2, 3, 9], 'pos = n + 1 = 4 表示插到表尾，是合法位置，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\n_r = insert_pos(_h, 5, 9)\nassert _r is False and _vals(_h) == [1, 2, 3], 'pos = 5 超过 n + 1，应返回 False 且链表不变，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\n_r = insert_pos(_h, 0, 9)\nassert _r is False and _vals(_h) == [1, 2, 3], 'pos = 0 小于 1，越界应返回 False 且链表不变，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\n_r = insert_pos(_h, -1, 9)\nassert _r is False and _vals(_h) == [1, 2, 3], 'pos 是负数应返回 False，实际 %r' % (_r,)",
            "_h = _dummy([])\n_r = insert_pos(_h, 1, 7)\nassert _r is True and _vals(_h) == [7], '空表（只有头结点）上 pos = 1 是合法的，应插入成功，实际 %r' % (_vals(_h),)",
            "_h = _dummy([])\n_r = insert_pos(_h, 2, 7)\nassert _r is False and _vals(_h) == [], '空表上只有 pos = 1 合法，pos = 2 应返回 False，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2])\n_first = _h.next\ninsert_pos(_h, 1, 9)\nassert _h.next.val == 9 and _h.next.next is _first, '要求只改指针、复用原来的结点，不能把值拷出来重建链表'",
            "_h = _dummy([1, 2, 3])\ninsert_pos(_h, 3, 8)\nassert _h.val == 0 and _vals(_h) == [1, 2, 8, 3], '头结点（哨兵）本身不变，插入的位置也要对，实际 %r' % (_vals(_h),)",
            "_h = _dummy([2, 2, 2])\ninsert_pos(_h, 2, 2)\nassert _vals(_h) == [2, 2, 2, 2], '值都相同时按位置插入，实际 %r' % (_vals(_h),)",
            "_h = _dummy([])\nfor _i in range(1, 51):\n    assert insert_pos(_h, _i, _i) is True, '每次插到表尾（pos = %d = n + 1）都应当合法' % _i\nassert _vals(_h) == list(range(1, 51)), '连续插到表尾 50 次后应当是从 1 到 50，实际前 5 个是 %r' % (_vals(_h)[:5],)",
            "_h = _dummy([1, 2, 3])\ninsert_pos(_h, 3, 9)\nassert insert_pos(_h, 3, 8) is True and _vals(_h) == [1, 2, 8, 9, 3], '在同一个位置连插两次也要对，实际 %r' % (_vals(_h),)",
        ],
        'explanation': (
            '单链表插入的难点全在「**找前驱**」：要改动的是第 pos − 1 个结点的 `next`，'
            '所以指针必须停在它身上，而不是停在「要插入的位置」上。\n\n'
            '```python\n'
            'prev = head\n'
            'step = 0\n'
            'while step < pos - 1 and prev is not None:\n'
            '    prev = prev.next\n'
            '    step += 1\n'
            'if prev is None:          # 还没走够步数就到底了 → pos 太大\n'
            '    return False\n'
            'node = Node(val)\n'
            'node.next = prev.next     # 先把后面的链接上\n'
            'prev.next = node          # 再让前驱指向新结点\n'
            'return True\n'
            '```\n\n'
            '**为什么先接 `node.next`、后改 `prev.next`？** 顺序反了不报错，但一旦先执行'
            '`prev.next = node`，原来 `prev.next` 的值就丢了，新结点会指错地方甚至断链。'
            '养成「先接尾巴、再挂前面」的习惯。\n\n'
            '**带头结点的好处**：`pos = 1`（插到最前面）和 `pos = n + 1`（插到最后面）'
            '都能用同一段代码完成——因为头结点永远存在，前驱一定找得到，'
            '不需要像不带头结点那样单独处理「插到空表」「插到第一个位置」这些特例。'
            '这就是哨兵结点的价值所在。\n\n'
            '**常见错误**：\n\n'
            '1. 走 `pos` 步而不是 `pos − 1` 步，结果整体错一位；\n'
            '2. 边界写成 `pos > n` 就返回 False，把「插到表尾」这个合法位置误判为越界；\n'
            '3. 忘了 `pos < 1` 的判断，负下标一路走到底；\n'
            '4. 走不到就对 `prev.next` 取属性报 AttributeError，'
            '应该用 `prev is None` 提前拦下。\n\n'
            '复杂度：时间 O(n)（最坏要走 n 步找前驱）、额外空间 O(1)。'
        ),
        'expected_output': 'True\n[1, 9, 2, 3]\nFalse\n[1, 9, 2, 3]',
        'hints': [
            '从头结点出发走 pos - 1 步，prev 停在「新结点的前驱」上',
            'pos = n + 1 是插到表尾（合法），再大就说明中途走到底了，返回 False',
        ],
    },
    {
        'id': 'x823-005',
        'track': 'algorithm',
        'chapter_id': 128,
        'chapter_title': '823·线性表',
        'topic': '823·线性表',
        'title': '带头结点单链表就地逆置（三指针 O(1) 空间）',
        'difficulty': 2,
        'tags': ['单链表', '逆置', '三指针', 'O(1) 空间'],
        'statement': (
            '考点：链表指针操作、经典算法题。\n\n'
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `reverse_list(head)`：把**带头结点**的单链表**就地**逆置，'
            '返回**头结点**（即传入的那个哨兵对象，逆置后它仍然是链表的头结点）。\n\n'
            '约定与要求：\n\n'
            '- `head` 是头结点（哨兵，不存数据），要逆置的是 `head.next` 开始的整条**数据链**；\n'
            '- **就地**逆置：只改每个结点的 `next` 指针，'
            '**不许新建结点**、也不许把值读进列表再重新串一条链表出来；\n'
            '- 额外空间严格 O(1)：用 `prev`、`current`、`nxt` 三个指针轮换即可；\n'
            '- **头结点对象保持不动**，函数返回它即可'
            '（返回值的约定是为了让「逆置后的链表」有个统一出口）；\n'
            '- 空表（只有头结点）、只有一个数据结点、两个数据结点都要能正确处理。\n\n'
            '最后构造一条带头结点、数据结点依次是 `1 → 2 → 3 → 4 → 5` 的链表，逆置后打印所有数据值；'
            '再打印逆置空链表和单结点链表的结果。'
        ),
        'starter_code': (
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '\n'
            'def reverse_list(head):\n'
            '    prev = None\n'
            '    current = head.next\n'
            '    # 每步：先存 nxt = current.next，再让 current.next 指向 prev，最后两个指针一起后移\n'
            '    pass\n'
        ),
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def reverse_list(head):\n"
            "    prev = None\n"
            "    current = head.next\n"
            "    while current is not None:\n"
            "        nxt = current.next\n"
            "        current.next = prev\n"
            "        prev = current\n"
            "        current = nxt\n"
            "    head.next = prev\n"
            "    return head\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    node = head.next\n"
            "    while node is not None:\n"
            "        out.append(node.val)\n"
            "        node = node.next\n"
            "    return out\n"
            "\n"
            "head = Node(0, Node(1, Node(2, Node(3, Node(4, Node(5))))))\n"
            "print(values_of(reverse_list(head)))\n"
            "print(values_of(reverse_list(Node(0))))\n"
            "print(values_of(reverse_list(Node(0, Node(8)))))\n"
        ),
        'checks': [
            "def _dummy(values):\n    head = Node(0)\n    tail = head\n    for v in values:\n        tail.next = Node(v)\n        tail = tail.next\n    return head",
            "def _vals(head):\n    out = []\n    node = head.next\n    while node is not None:\n        out.append(node.val)\n        node = node.next\n    return out",
            "assert _vals(reverse_list(_dummy([]))) == [], '空表（只有头结点）逆置后数据链仍然是空的'",
            "assert _vals(reverse_list(_dummy([7]))) == [7], '只有一个数据结点时逆置后还是它自己'",
            "_h = _dummy([1, 2])\nassert _vals(reverse_list(_h)) == [2, 1], '两个结点要交换过来，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3, 4, 5])\nassert _vals(reverse_list(_h)) == [5, 4, 3, 2, 1], '五个结点逆置结果不对，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\n_last = _h.next.next.next\n_ret = reverse_list(_h)\nassert _ret is _h, '带头结点逆置后要返回头结点本身（哨兵对象不变）'\nassert _h.next is _last, '要求就地逆置、复用原结点：新的第一个数据结点应当正好是原来的尾结点'",
            "_h = _dummy([1, 2, 3])\n_first = _h.next\nreverse_list(_h)\nassert _first.next is None, '就地逆置后原来的头结点应当变成尾结点（next 为 None）'",
            "_h = _dummy([1, 2, 3])\nreverse_list(_h)\nassert _h.val == 0, '头结点（哨兵）的 val 不该被改动，逆置的只是 head.next 之后的数据链'",
            "_h = _dummy([1, 1, 2, 2, 1])\nassert _vals(reverse_list(_h)) == [1, 2, 2, 1, 1], '有重复值也要正确逆置，实际 %r' % (_vals(_h),)",
            "_h = _dummy([-1, 0, 0, 5])\nassert _vals(reverse_list(_h)) == [5, 0, 0, -1], '负数和 0 也要正确处理，实际 %r' % (_vals(_h),)",
            "_h = _dummy([1, 2, 3])\nreverse_list(_h)\nreverse_list(_h)\nassert _vals(_h) == [1, 2, 3], '逆置两次应当回到原样，实际 %r' % (_vals(_h),)",
            "_h = _dummy(list(range(1000)))\nassert _vals(reverse_list(_h)) == list(range(999, -1, -1)), '1000 个结点的链表也要能逆置（注意别写递归，会栈溢出）'",
        ],
        'explanation': (
            '逆置链表靠的是**三根指针的轮换**，每一步只做四件事：\n\n'
            '```python\n'
            'while current is not None:\n'
            '    nxt = current.next      # 1. 先记住后面还有谁\n'
            '    current.next = prev     # 2. 当前结点掉头，指向前一个\n'
            '    prev = current          # 3. prev 前进到当前结点\n'
            '    current = nxt           # 4. current 前进到下一个\n'
            'head.next = prev            # 哨兵的 next 指向新的第一个数据结点\n'
            '```\n\n'
            '第 1 步**必须先做**：一旦执行了第 2 步，`current.next` 就被改写了，'
            '再想往后走就找不到路——链表会在中间断成两截，后面的结点全丢。'
            '这是本题最经典的错误，和「先接尾巴再挂前面」是同一种思维。\n\n'
            '循环结束时 `current` 是 None，`prev` 停在原来的最后一个结点上，'
            '所以最后要让 `head.next = prev`，然后返回 `head`。'
            '**注意哨兵自己不在逆置范围内**：如果把 `head` 也当成数据结点一起翻转，'
            '结果会多出一个 val 为 0 的结点，链表就错了。\n\n'
            '**为什么强调「就地」？** 新建一条链表需要 O(n) 额外空间，'
            '而就地逆置只用三个变量，空间 O(1)；考试评分点恰恰在这个 O(1) 上，'
            '把值读出来放进列表再重建虽然结果对，但会丢分。'
            '另外一定要用循环（迭代）写：递归版会额外吃掉 O(n) 的栈空间，'
            '1000 个结点还可能触发递归深度上限。\n\n'
            '复杂度：时间 O(n)（每个结点只处理一次）、额外空间 O(1)。'
        ),
        'expected_output': '[5, 4, 3, 2, 1]\n[]\n[8]',
        'hints': [
            '每步先把 current.next 存进 nxt，再让 current.next 指向 prev',
            '循环结束后 prev 是新链的第一个结点，把它接到 head.next 上并返回 head',
        ],
    },
    {
        'id': 'x823-006',
        'track': 'algorithm',
        'chapter_id': 128,
        'chapter_title': '823·线性表',
        'topic': '823·线性表',
        'title': '双向链表删除指定结点（只改相邻指针）',
        'difficulty': 1,
        'tags': ['双链表', '删除', '指针修改'],
        'statement': (
            '考点：双链表指针修改顺序（易错点）。\n\n'
            '请**按下面的定义**写好双向链表结点类（属性名必须一致）：\n\n'
            '```python\n'
            'class DNode:\n'
            '    def __init__(self, val=0, prev=None, next=None):\n'
            '        self.val = val\n'
            '        self.prev = prev\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `delete_node(node)`：把结点 `node` 从它所在的双向链表里**摘下来**，'
            '返回被删除结点的值；`node` 为 `None` 时返回 `None`。\n\n'
            '要求：\n\n'
            '- **只修改相邻结点的指针，不许遍历**：`node.prev` 存在就把它接到 `node.next`；'
            '`node.next` 存在就把它接到 `node.prev`。正因为双向链表有 `prev` 指针，'
            '「给了结点就能直接删」是它的拿手好戏——单链表做不到这一点，必须先找前驱；\n'
            '- 四种情况都不能报错：`node` 是中间结点 / 是头结点（`prev` 为 `None`）/ '
            '是尾结点（`next` 为 `None`）/ 链上只有它一个（既是头又是尾）；\n'
            '- 函数只负责「把这个结点摘下来」，**不负责更新外面保存的 `head` 变量**：'
            '如果删掉的正好是头结点，调用方手里的头指针要自己改成 `node.next`；\n'
            '- 时间是 O(1)、额外空间 O(1)。\n\n'
            '最后构造双向链表 `1 ↔ 2 ↔ 3`，删除中间的结点 2，'
            '打印返回值和剩下的数据值；再打印一次用 `None` 调用函数的结果。'
        ),
        'starter_code': (
            'class DNode:\n'
            '    def __init__(self, val=0, prev=None, next=None):\n'
            '        self.val = val\n'
            '        self.prev = prev\n'
            '        self.next = next\n'
            '\n'
            'def delete_node(node):\n'
            '    # node.prev 存在就让它指向 node.next；node.next 存在就让它指向 node.prev\n'
            '    pass\n'
        ),
        'solution': (
            "class DNode:\n"
            "    def __init__(self, val=0, prev=None, next=None):\n"
            "        self.val = val\n"
            "        self.prev = prev\n"
            "        self.next = next\n"
            "\n"
            "def delete_node(node):\n"
            "    if node is None:\n"
            "        return None\n"
            "    if node.prev is not None:\n"
            "        node.prev.next = node.next\n"
            "    if node.next is not None:\n"
            "        node.next.prev = node.prev\n"
            "    value = node.val\n"
            "    node.prev = None\n"
            "    node.next = None\n"
            "    return value\n"
            "\n"
            "def link(values):\n"
            "    head = None\n"
            "    tail = None\n"
            "    for v in values:\n"
            "        node = DNode(v, tail, None)\n"
            "        if tail is None:\n"
            "            head = node\n"
            "        else:\n"
            "            tail.next = node\n"
            "        tail = node\n"
            "    return head\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    while head is not None:\n"
            "        out.append(head.val)\n"
            "        head = head.next\n"
            "    return out\n"
            "\n"
            "data = link([1, 2, 3])\n"
            "print(delete_node(data.next), values_of(data))\n"
            "print(delete_node(None))\n"
        ),
        'checks': [
            "def _link(values):\n    head = None\n    tail = None\n    for v in values:\n        node = DNode(v, tail, None)\n        if tail is None:\n            head = node\n        else:\n            tail.next = node\n        tail = node\n    return head",
            "def _vals(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "def _back(head):\n    node = head\n    while node.next is not None:\n        node = node.next\n    out = []\n    while node is not None:\n        out.append(node.val)\n        node = node.prev\n    return out",
            "_h = _link([1, 2, 3])\n_r = delete_node(_h.next)\nassert _r == 2, '删除中间结点应返回它的值 2，实际 %r' % (_r,)\nassert _vals(_h) == [1, 3], '删掉中间的 2 之后应当是 [1, 3]，实际 %r' % (_vals(_h),)\nassert _back(_h) == [3, 1], '沿 prev 从尾部倒着走应当是 [3, 1]，说明两个方向的指针都改对了，实际 %r' % (_back(_h),)",
            "_h = _link([1, 2, 3])\n_new = _h.next\n_r = delete_node(_h)\nassert _r == 1 and _vals(_new) == [2, 3], '删除头结点（prev 为 None）后，新头应当是原来的第二个结点，实际 %r' % (_vals(_new),)\nassert _new.prev is None, '新的头结点的 prev 必须是 None'",
            "_h = _link([1, 2, 3])\n_r = delete_node(_h.next.next)\nassert _r == 3 and _vals(_h) == [1, 2], '删除尾结点（next 为 None）后应当剩 [1, 2]，实际 %r' % (_vals(_h),)\nassert _back(_h) == [2, 1], '删尾之后倒着走应当是 [2, 1]，实际 %r' % (_back(_h),)",
            "_h = _link([9])\n_r = delete_node(_h)\nassert _r == 9, '链上只有一个结点（既是头又是尾）时要能正常删除并返回值，实际 %r' % (_r,)",
            "assert delete_node(None) is None, 'node 是 None 时应返回 None，不要报错'",
            "_h = _link([1, 2, 3])\n_a = _h\n_c = _h.next.next\n_r = delete_node(_h.next)\nassert _a.next is _c and _c.prev is _a, '删除中间结点后，前后两个结点应当直接相连（这一对指针最容易改漏）'",
            "_h = _link([5, 5, 5])\n_r = delete_node(_h.next)\nassert _r == 5 and _vals(_h) == [5, 5], '值重复时按结点对象删除，实际 %r' % (_vals(_h),)",
            "_h = _link(list(range(200)))\n_node = _h\nfor _ in range(50):\n    _node = _node.next\n_r = delete_node(_node)\nassert _r == 50, '应当删掉值为 50 的那个结点，实际 %r' % (_r,)\nassert _vals(_h) == list(range(50)) + list(range(51, 200)), '剩下的应当是 0…49 与 51…199，实际长度 %d' % (len(_vals(_h)),)\nassert _back(_h) == _vals(_h)[::-1], '删除之后沿 prev 反向走一遍，顺序应当和正向完全相反'",
            "_h = _link([1, 2, 3, 4])\n_n2 = _h.next\n_n3 = _h.next.next\ndelete_node(_n3)\ndelete_node(_n2)\nassert _vals(_h) == [1, 4], '连续删掉两个中间结点之后应当是 [1, 4]，实际 %r' % (_vals(_h),)\nassert _back(_h) == [4, 1], '连续删除之后反向指针也要保持正确，实际 %r' % (_back(_h),)",
        ],
        'explanation': (
            '双向链表删除一个**已知结点**，只需改两根指针——这就是 `prev` 的价值：\n\n'
            '```python\n'
            'if node.prev is not None:\n'
            '    node.prev.next = node.next     # 前驱跨过它\n'
            'if node.next is not None:\n'
            '    node.next.prev = node.prev     # 后继跨过它\n'
            '```\n\n'
            '**为什么两个 `if` 都必须有？**\n\n'
            '- 删的是**头结点**时 `node.prev` 是 `None`，第一个 `if` 挡住的正是「对 None 取属性」的崩溃；\n'
            '- 删的是**尾结点**时 `node.next` 是 `None`，第二个 `if` 同理；\n'
            '- 链上**只有一个结点**时两个都是 `None`，两句都被跳过——它就这样干脆地脱链了，'
            '不需要任何特殊分支。\n\n'
            '**和单链表的对比**（考试爱考）：单链表删一个已知结点得先找前驱，'
            '要么从头 O(n) 扫一遍，要么用「把后继的值抄过来再删后继」的绕弯办法'
            '（那还删不掉尾结点）；双向链表给了结点就能 O(1) 删除，'
            '代价是每个结点多一个 `prev` 指针，插入和删除时都要维护两根指针。\n\n'
            '**指针修改顺序**是双链表的核心易错点，但分场合：\n\n'
            '- **删除**时先改 `prev.next` 还是先改 `next.prev` 都不影响结果——'
            '因为要用的旧值（`node.prev`、`node.next`）来自 `node` 自己，不会互相覆盖；\n'
            '- **插入**时顺序就致命了：必须先把新结点的两根指针接好，再动相邻结点，'
            '否则邻居的地址就丢了。\n\n'
            '**另一个常见错误**：把「摘下来」和「删掉头指针」混为一谈。'
            '函数只把结点脱链，外部的 `head` 变量该不该改是调用方的事；'
            '如果被删的是头结点，调用方必须自己执行 `head = node.next`，'
            '否则那个变量还指着已经脱链的结点。\n\n'
            '复杂度：时间 O(1)、额外空间 O(1)。'
        ),
        'expected_output': '2 [1, 3]\nNone',
        'hints': [
            '两个 if 分别挡住「删头结点」和「删尾结点」两种越界情况',
            '删除只需要 node.prev.next = node.next 和 node.next.prev = node.prev 两句',
        ],
    },
    # ── 专题 129 823·栈和队列 ─────────────────────────────
    {
        'id': 'x823-007',
        'track': 'algorithm',
        'chapter_id': 129,
        'chapter_title': '823·栈和队列',
        'topic': '823·栈和队列',
        'title': '括号匹配检验（列表模拟栈）',
        'difficulty': 2,
        'tags': ['栈', '括号匹配', '列表模拟栈'],
        'statement': (
            '考点：栈的应用。\n\n'
            '已知一个只由 `(` `)` `[` `]` `{` `}` 六种括号组成的字符串 `s`。\n\n'
            '定义函数 `is_valid(s)`：检验 `s` 中的括号是否**合法匹配**，'
            '返回 `True` / `False`（要布尔值本身）。\n\n'
            '「合法」的意思是：\n\n'
            '- 每个右括号都能找到**同类型**、且**最近还没闭合**的那个左括号；\n'
            '- 不允许交叉嵌套：`([)]` 不合法（`[` 还没闭合，`)` 就想闭合）；\n'
            '- 空字符串算合法；\n'
            '- `(((`、`)`、`([{}]` 这类「有括号没闭合」的都不合法。\n\n'
            '要求：\n\n'
            '- **用列表模拟栈**（`stack = []`，用 `append` 压栈、`pop` 弹栈），一次遍历 O(n)；\n'
            '- 遇左括号就压栈；遇右括号时先看栈空不空（**栈空就直接返回 False**），'
            '再弹出栈顶看类型对不对；\n'
            '- 遍历结束后**栈必须为空**，否则说明还有左括号没有闭合；\n'
            '- 不许用「反复把 `()`、`[]`、`{}` 成对替换掉再看剩不剩东西」的取巧写法'
            '（如 `replace`），本题的考点就是栈。\n\n'
            '最后打印 `is_valid("({[]})")`、`is_valid("([)]")`、`is_valid("")` 的结果。'
        ),
        'starter_code': (
            "def is_valid(s):\n"
            "    pairs = {')': '(', ']': '[', '}': '{'}\n"
            "    stack = []\n"
            "    # 左括号压栈；右括号弹出栈顶比对；最后检查栈是否为空\n"
            "    pass\n"
        ),
        'solution': (
            "def is_valid(s):\n"
            "    pairs = {')': '(', ']': '[', '}': '{'}\n"
            "    stack = []\n"
            "    for ch in s:\n"
            "        if ch in '([{':\n"
            "            stack.append(ch)\n"
            "        elif ch in pairs:\n"
            "            if not stack or stack.pop() != pairs[ch]:\n"
            "                return False\n"
            "        else:\n"
            "            return False\n"
            "    return not stack\n"
            "\n"
            "print(is_valid('({[]})'))\n"
            "print(is_valid('([)]'))\n"
            "print(is_valid(''))\n"
        ),
        'checks': [
            "assert is_valid('()[]{}') is True, '三种括号并列且都闭合，应返回 True，实际 %r' % (is_valid('()[]{}'),)",
            "assert is_valid('({[]})') is True, '多层混合嵌套是合法的，实际 %r' % (is_valid('({[]})'),)",
            "assert is_valid('') is True, '空字符串算合法，应返回 True，实际 %r' % (is_valid(''),)",
            "assert is_valid('([)]') is False, '([)] 是交叉嵌套，不合法（最容易漏的一种）'",
            "assert is_valid('[(])') is False, '[(]) 也是交叉嵌套，应返回 False'",
            "assert is_valid('(') is False and is_valid(')') is False, '只有左括号、或只有右括号都不合法'",
            "assert is_valid('(((') is False and is_valid(')))') is False, '一串不闭合的括号应返回 False，实际 %r / %r' % (is_valid('((('), is_valid(')))'))",
            "assert is_valid('([{}]') is False, '少一个右括号（遍历结束后栈不为空）应返回 False'",
            "assert is_valid('{[]}') is True and is_valid('()()') is True, '并列的多组括号都合法，实际 %r / %r' % (is_valid('{[]}'), is_valid('()()'))",
            "assert is_valid('(]') is False and is_valid('{)') is False, '类型不匹配要返回 False'",
            "_s = '(' * 500 + ')' * 500\nassert is_valid(_s) is True, '500 层嵌套再逐层闭合应当是合法的'",
            "_s = '(' * 500 + ')' * 499\nassert is_valid(_s) is False, '左括号比右括号多一个应返回 False'",
            "assert is_valid('()') is True and is_valid('(') is False, '返回值要正好是 True / False 这两个布尔值'",
            "assert 'replace(' not in _src and 're.sub' not in _src, '这题要求用栈判断，不许用「反复 replace 掉成对括号」的取巧写法'",
        ],
        'explanation': (
            '括号匹配之所以用栈，是因为括号的嵌套规则恰好是**后进先出**：'
            '最后打开的那个括号，必须最先被关闭。\n\n'
            "```python\n"
            "for ch in s:\n"
            "    if ch in '([{':\n"
            "        stack.append(ch)\n"
            "    elif ch in pairs:\n"
            "        if not stack or stack.pop() != pairs[ch]:\n"
            "            return False\n"
            "return not stack\n"
            "```\n\n"
            '栈里存的是「**已经打开、还没关闭**的左括号」，栈顶就是最近打开的那个。'
            '遇到右括号时，它要配对的正是栈顶——对不上就说明交叉了或者类型错了。\n\n'
            '两个最容易丢分的点：\n\n'
            '1. **栈空时遇到右括号**要立刻返回 False。少了这一句，`pop()` 会抛 `IndexError`；\n'
            '2. 循环结束后**栈必须为空**，否则 `(((`、`([{}]` 这种「左括号没闭合」的串会被误判为合法。'
            '所以最后写 `return not stack`（空列表在布尔判断里是假，于是返回 True）。\n\n'
            '`([)]` 为什么非法？读到 `)` 时栈顶是 `[`，类型不对——栈顶不是「任意一个左括号」，'
            '而是**最近打开的那个**，这正是「后进先出」在判题上的体现。\n\n'
            '**常见错误**：\n\n'
            '1. 用两个计数器分别数左右括号——只能判断数量，判断不了嵌套顺序，`([)]` 就会漏掉；\n'
            '2. 遇到右括号直接 `stack.pop()` 而不先判空，遇到 `)` 开头的串就崩；\n'
            '3. 用「反复 `replace(\'()\', \'\')` 直到串不再变化」的取巧法：'
            '结果常常正确，但复杂度是 O(n²)，而且完全绕开了栈这个考点。\n\n'
            '复杂度：时间 O(n)（每个字符进出栈一次）、空间 O(n)（最坏全压栈）。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': [
            '左括号压栈；遇到右括号先判栈空，再弹出栈顶比对类型',
            '循环结束别急着 return True，要先确认栈是空的（否则 ( 会被放过）',
        ],
    },
    {
        'id': 'x823-008',
        'track': 'algorithm',
        'chapter_id': 129,
        'chapter_title': '823·栈和队列',
        'topic': '823·栈和队列',
        'title': '后缀表达式求值（除法要向零截断）',
        'difficulty': 2,
        'tags': ['栈', '后缀表达式', '逆波兰式'],
        'statement': (
            '考点：栈的应用、逆波兰表达式。\n\n'
            '已知一个**后缀表达式**（逆波兰式），用字符串列表 `tokens` 表示：'
            '每个元素要么是表示整数的字符串（可能带负号，如 `"-3"`），'
            '要么是运算符 `"+"` `"-"` `"*"` `"/"` 之一。\n\n'
            '定义函数 `eval_rpn(tokens)`：计算它的值并返回（整数）。\n\n'
            '例如 `["2", "1", "+", "3", "*"]` 表示 `(2 + 1) * 3`，结果是 `9`。\n\n'
            '要求：\n\n'
            '- **用列表模拟栈**：从左到右扫一遍 tokens，遇到数字就压栈；遇到运算符就弹出'
            '**两个**操作数——**先弹出的是右操作数 `b`，后弹出的是左操作数 `a`**，'
            '把 `a 运算符 b` 的结果压回栈；全部扫完后栈里剩下的那个数就是答案；\n'
            '- **除法按「向零截断」的整数除法**（和 C 语言一样）：'
            '`7 / 2 = 3`、`-7 / 2 = -3`。注意 Python 的 `//` 是**向下取整**（`-7 // 2 == -4`），'
            '直接用会错；`int(a / b)` 也可以，但大整数走浮点会失真，'
            '更稳的是自己用绝对值算再补符号；\n'
            '- 空列表返回 `0`（本题约定）；\n'
            '- **不要修改传入的 `tokens`**（用下标从左到右读，别用 `tokens.pop()` 把它吃空）；\n'
            '- 题目保证表达式合法：运算符一定有足够的操作数，且除数不为 0。\n\n'
            '最后打印 `eval_rpn(["2","1","+","3","*"])`、`eval_rpn(["4","13","5","/","+"])`、'
            '`eval_rpn(["-7","2","/"])` 的结果。'
        ),
        'starter_code': (
            'def eval_rpn(tokens):\n'
            '    stack = []\n'
            '    # 数字压栈；运算符弹出两个操作数（先弹出的是右操作数），算完把结果压回\n'
            '    pass\n'
        ),
        'solution': (
            "def eval_rpn(tokens):\n"
            "    stack = []\n"
            "    for token in tokens:\n"
            "        if token in ('+', '-', '*', '/'):\n"
            "            b = stack.pop()\n"
            "            a = stack.pop()\n"
            "            if token == '+':\n"
            "                stack.append(a + b)\n"
            "            elif token == '-':\n"
            "                stack.append(a - b)\n"
            "            elif token == '*':\n"
            "                stack.append(a * b)\n"
            "            else:\n"
            "                q = abs(a) // abs(b)\n"
            "                stack.append(-q if (a < 0) != (b < 0) else q)\n"
            "        else:\n"
            "            stack.append(int(token))\n"
            "    if not stack:\n"
            "        return 0\n"
            "    return stack[-1]\n"
            "\n"
            "print(eval_rpn(['2', '1', '+', '3', '*']))\n"
            "print(eval_rpn(['4', '13', '5', '/', '+']))\n"
            "print(eval_rpn(['-7', '2', '/']))\n"
        ),
        'checks': [
            "assert eval_rpn(['2', '1', '+', '3', '*']) == 9, '题目给的例子 (2 + 1) * 3 应当是 9，实际 %r' % (eval_rpn(['2', '1', '+', '3', '*']),)",
            "assert eval_rpn(['4', '13', '5', '/', '+']) == 6, '4 + 13 / 5 = 4 + 2 = 6，实际 %r' % (eval_rpn(['4', '13', '5', '/', '+']),)",
            "assert eval_rpn(['-7', '2', '/']) == -3, '除法要「向零截断」：-7 / 2 应当是 -3（Python 的 -7 // 2 是 -4，用 // 就会错），实际 %r' % (eval_rpn(['-7', '2', '/']),)",
            "assert eval_rpn(['7', '-2', '/']) == -3, '7 / -2 也要向零截断成 -3，实际 %r' % (eval_rpn(['7', '-2', '/']),)",
            "assert eval_rpn(['-7', '-2', '/']) == 3, '两个负数相除得正：-7 / -2 应当是 3，实际 %r' % (eval_rpn(['-7', '-2', '/']),)",
            "assert eval_rpn(['3']) == 3 and eval_rpn(['-3']) == -3, '只有一个操作数时直接返回它，实际 %r / %r' % (eval_rpn(['3']), eval_rpn(['-3']))",
            "assert eval_rpn([]) == 0, '空列表按约定返回 0，实际 %r' % (eval_rpn([]),)",
            "assert eval_rpn(['2', '3', '*', '4', '+']) == 10 and eval_rpn(['10', '2', '-']) == 8, '减法和乘法的操作数顺序不能反（先弹出的是右操作数），实际 %r / %r' % (eval_rpn(['2', '3', '*', '4', '+']), eval_rpn(['10', '2', '-']))",
            "assert eval_rpn(['10', '6', '9', '3', '+', '-11', '*', '/', '*', '17', '+', '5', '+']) == 22, '这条长表达式（含一次向零截断的除法）应当是 22，实际 %r' % (eval_rpn(['10', '6', '9', '3', '+', '-11', '*', '/', '*', '17', '+', '5', '+']),)",
            "_t = ['2', '1', '+', '3', '*']\neval_rpn(_t)\nassert _t == ['2', '1', '+', '3', '*'], '题目要求不修改传入的 tokens（用下标从左到右读），实际 %r' % (_t,)",
            "_tk = ['1', '2', '+'] + ['3', '+'] * 100\nassert eval_rpn(_tk) == 303, '1 + 2 再连加 100 次 3，结果应当是 303，实际 %r' % (eval_rpn(_tk),)",
            "assert eval_rpn(['0', '5', '*']) == 0, '含 0 的表达式也要正确，实际 %r' % (eval_rpn(['0', '5', '*']),)",
            "assert eval_rpn(['2', '-3', '*']) == -6 and eval_rpn(['-2', '-3', '*']) == 6, '负数的乘法也要正确，实际 %r / %r' % (eval_rpn(['2', '-3', '*']), eval_rpn(['-2', '-3', '*']))",
        ],
        'explanation': (
            '后缀表达式不需要括号、也不需要优先级：**从左到右扫一遍就能算完**，'
            '这正是它作为「计算机内部表达式」的原因。\n\n'
            '```python\n'
            'b = stack.pop()\n'
            'a = stack.pop()\n'
            'stack.append(a + b)      # 或 a - b、a * b、a / b\n'
            '```\n\n'
            '**为什么要强调「先弹出的是右操作数」？** 栈是后进先出，'
            '后压进去的是右操作数，所以第一次 `pop()` 得到 `b`，第二次才得到 `a`。'
            '减法和除法不满足交换律，搞反了 `10 2 -` 会算成 `2 − 10 = −8`。\n\n'
            '**除法的坑（本题最值钱的地方）**：题目要求像 C 语言那样**向零截断**，'
            '而 Python 的 `//` 是**向下取整**：\n\n'
            '```python\n'
            '-7 // 2       # -4（向下取整，不对）\n'
            '-7 / 2        # -3.5\n'
            'int(-7 / 2)   # -3（向零截断，对）\n'
            '```\n\n'
            '`int(a / b)` 会先转成浮点再截断，数字很大时（超过 2^53）会丢精度，'
            '所以更稳妥的写法是 `q = abs(a) // abs(b)`，两个数异号再取负——'
            '这正是参考答案的做法。\n\n'
            '**常见错误**：\n\n'
            '1. 两个操作数弹出来就写 `a - b` / `a / b`，却忘了它们是「先右后左」；\n'
            '2. 直接用 `//` 处理除法，负数样例全错；\n'
            '3. 用 `tokens.pop()` 一边弹一边算——表达式算完了，调用方手里的列表也空了；\n'
            '4. 忘了处理空列表，或者算完后取 `stack[0]`（应当取栈里剩下的那个元素）。\n\n'
            '复杂度：时间 O(n)（每个 token 处理一次）、空间 O(n)（栈最多存下所有操作数）。'
        ),
        'expected_output': '9\n6\n-3',
        'hints': [
            '遇到运算符时，先弹出的是右操作数 b、后弹出的是左操作数 a',
            '除法向零截断：abs(a) // abs(b) 再补符号（或 int(a / b)），别直接用 //',
        ],
    },
    {
        'id': 'x823-009',
        'track': 'algorithm',
        'chapter_id': 129,
        'chapter_title': '823·栈和队列',
        'topic': '823·栈和队列',
        'title': '数组模拟循环队列（牺牲一个存储位置）',
        'difficulty': 2,
        'tags': ['循环队列', '队列', '判空判满', '必考'],
        'statement': (
            '考点：循环队列的判空、判满、入队、出队（必考）。\n\n'
            '用列表实现循环队列类 `CircularQueue`，容量参数是 `max_size`：\n\n'
            '```python\n'
            'class CircularQueue:\n'
            '    def __init__(self, max_size):   # max_size 是数组的容量\n'
            '    def enqueue(self, val):         # 入队：成功返回 True，队满返回 False\n'
            '    def dequeue(self):              # 出队：返回队头元素，队空返回 None\n'
            '    def is_empty(self):             # 队空返回 True\n'
            '    def is_full(self):              # 队满返回 True\n'
            '```\n\n'
            '要求（**必须采用「牺牲一个存储位置」的方案**；属性名随意，行为对就行）：\n\n'
            '- 开一个长度正好是 `max_size` 的列表当数组，'
            '再加两个下标 `front`（指向队头元素）和 `rear`（指向队尾元素的**下一个空位**）；\n'
            '- **队空**的条件是 `front == rear`；\n'
            '- **队满**的条件是 `(rear + 1) % max_size == front`——'
            '队满时数组里始终**留着一个空位**，用它把「队空」和「队满」区分开；\n'
            '- 因此容量为 `max_size` 的队列**最多只能存 `max_size − 1` 个元素**，'
            '第 `max_size` 个元素进不来；\n'
            '- 下标移动一律用 `(x + 1) % max_size` 绕回数组开头，四个操作都必须是 O(1)；\n'
            '- 队满时 `enqueue` 返回 `False`，而且**不能覆盖已有数据**；'
            '队空时 `dequeue` 返回 `None`（不要抛出异常）；\n'
            '- 队列必须严格 **FIFO**：先进先出。\n\n'
            '然后造一个 `max_size = 5` 的队列，按下面的顺序打印（每行一句 `print`）：\n\n'
            '1. 依次入队 1、2、3、4 的四个返回值；\n'
            '2. `is_full()` 和再入队 5 的返回值；\n'
            '3. 出队两次的结果；\n'
            '4. 再入队 5、入队 6 的返回值（体会下标绕回数组开头）；\n'
            '5. 连续出队四次的结果；\n'
            '6. `is_empty()` 和队空时再出队的结果。'
        ),
        'starter_code': (
            'class CircularQueue:\n'
            '    def __init__(self, max_size):\n'
            '        self.max_size = max_size\n'
            '        self.data = [None] * max_size\n'
            '        self.front = 0\n'
            '        self.rear = 0\n'
            '\n'
            '    def is_empty(self):\n'
            '        # front == rear\n'
            '        pass\n'
            '\n'
            '    def is_full(self):\n'
            '        # (rear + 1) % max_size == front\n'
            '        pass\n'
            '\n'
            '    def enqueue(self, val):\n'
            '        pass\n'
            '\n'
            '    def dequeue(self):\n'
            '        pass\n'
        ),
        'solution': (
            "class CircularQueue:\n"
            "    def __init__(self, max_size):\n"
            "        self.max_size = max_size\n"
            "        self.data = [None] * max_size\n"
            "        self.front = 0\n"
            "        self.rear = 0\n"
            "\n"
            "    def is_empty(self):\n"
            "        return self.front == self.rear\n"
            "\n"
            "    def is_full(self):\n"
            "        return (self.rear + 1) % self.max_size == self.front\n"
            "\n"
            "    def enqueue(self, val):\n"
            "        if self.is_full():\n"
            "            return False\n"
            "        self.data[self.rear] = val\n"
            "        self.rear = (self.rear + 1) % self.max_size\n"
            "        return True\n"
            "\n"
            "    def dequeue(self):\n"
            "        if self.is_empty():\n"
            "            return None\n"
            "        val = self.data[self.front]\n"
            "        self.front = (self.front + 1) % self.max_size\n"
            "        return val\n"
            "\n"
            "q = CircularQueue(5)\n"
            "print(q.enqueue(1), q.enqueue(2), q.enqueue(3), q.enqueue(4))\n"
            "print(q.is_full(), q.enqueue(5))\n"
            "print(q.dequeue(), q.dequeue())\n"
            "print(q.enqueue(5), q.enqueue(6))\n"
            "print(q.dequeue(), q.dequeue(), q.dequeue(), q.dequeue())\n"
            "print(q.is_empty(), q.dequeue())\n"
        ),
        'checks': [
            "_q = CircularQueue(5)\nassert _q.is_empty() is True, '刚建好的队列应当是空的'\nassert _q.is_full() is False, '空队列不应当是满的'",
            "_q = CircularQueue(5)\nfor _v in (1, 2, 3, 4):\n    assert _q.enqueue(_v) is True, '容量 5 的循环队列（牺牲一个位置）最多存 4 个，第 %d 个应当入队成功' % _v\nassert _q.is_full() is True, '存满 4 个之后应当队满（(rear + 1) % max_size == front）'",
            "_q = CircularQueue(5)\nfor _v in (1, 2, 3, 4):\n    _q.enqueue(_v)\nassert _q.enqueue(5) is False, '队满时入队应返回 False（被牺牲的那个位置不能被占用）'",
            "_q = CircularQueue(5)\nfor _v in (1, 2, 3, 4):\n    _q.enqueue(_v)\n_out = [_q.dequeue() for _ in range(4)]\nassert _out == [1, 2, 3, 4], '出队顺序必须是先进先出，实际 %r' % (_out,)\nassert _q.is_empty() is True, '4 个元素都出队之后应当队空'",
            "_q = CircularQueue(5)\n_r = _q.dequeue()\nassert _r is None, '空队列出队应返回 None，不要抛出异常，实际 %r' % (_r,)",
            "_q = CircularQueue(2)\nassert _q.is_empty() is True and _q.is_full() is False\nassert _q.enqueue(9) is True\nassert _q.is_full() is True, '容量 2 的循环队列只能存 1 个元素，存进去之后立刻就是满的'\nassert _q.enqueue(8) is False, '已经满了，第 2 个元素不能再入队'\nassert _q.dequeue() == 9, '出队的应当是最先入队的 9'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\nassert _q.is_full() is True, '容量 3 最多存 2 个，这时应当队满'\nassert _q.dequeue() == 1, '先出队的应当是 1'\nassert _q.enqueue(3) is True, '出队一个之后空位在数组开头，入队要能绕回去（(rear + 1) % max_size）'\nassert _q.dequeue() == 2 and _q.dequeue() == 3, '绕回之后顺序仍然是 2、3（先进先出）'",
            "_q = CircularQueue(4)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.enqueue(3)\nassert _q.enqueue(4) is False, '容量 4 只能存 3 个，第 4 个应当被拒绝'\nassert _q.dequeue() == 1 and _q.dequeue() == 2, '入队失败不能破坏已有数据，出队还应当是 1、2'",
            "_q = CircularQueue(4)\nfor _round in range(100):\n    assert _q.enqueue(_round) is True, '第 %d 轮：队列空着，应当能入队' % _round\n    assert _q.dequeue() == _round, '第 %d 轮：刚进去的元素应当原样出来（FIFO 被破坏）' % _round\nassert _q.is_empty() is True and _q.is_full() is False, '反复进出之后应当回到「空且不满」的状态'",
            "_q = CircularQueue(6)\nfor _v in range(5):\n    assert _q.enqueue(_v) is True, '容量 6 能存 5 个，第 %d 个应当入队成功' % (_v + 1)\nassert _q.is_full() is True, '存满 5 个之后应当队满'\nassert _q.enqueue(99) is False, '队满时入队应返回 False'",
            "_q = CircularQueue(5)\nassert _q.is_empty() is True and _q.is_full() is False, '两个判断的返回值要正好是 True / False 这两个布尔值'",
        ],
        'explanation': (
            '循环队列要解决的是一个矛盾：**队空和队满时，`front` 和 `rear` 都可能相等**。'
            '如果只按下标判断，这两种情况就分不开。三种常见解法里，'
            '本题要求的是考纲最常考的「**牺牲一个存储位置**」。\n\n'
            '```python\n'
            'def is_empty(self):\n'
            '    return self.front == self.rear\n'
            '\n'
            'def is_full(self):\n'
            '    return (self.rear + 1) % self.max_size == self.front\n'
            '```\n\n'
            '**为什么 `% max_size` 不能少？** 下标到数组末尾就要绕回 0。'
            '没有取模，`rear` 会一路涨到数组外面去，`self.data[rear]` 直接下标越界。\n\n'
            '**为什么要牺牲一个位置？** 让数组里永远留一个空位：'
            '「`rear` 再走一格就撞上 `front`」说明快满了，此时判满、拒绝入队。'
            '代价是容量为 `max_size` 的数组只能存 `max_size − 1` 个元素；'
            '好处是判空判满都只是一次比较，O(1) 且不需要额外的计数变量。\n\n'
            '**另外两种解法**（了解即可）：\n\n'
            '- 加一个 `size` 计数器：`size == 0` 为空、`size == max_size` 为满；\n'
            '- 加一个 `tag` 标志位：记录「最后一次操作是入队还是出队」来区分两种情况。\n\n'
            '**常见错误**：\n\n'
            '1. 判满写成 `rear == front`，那样空队列会被误判成满队列，一个元素都进不来；\n'
            '2. 忘了取模，队列用着用着就下标越界；\n'
            '3. 入队时先移动 `rear` 再存数据（差一格），出队时忘了移动 `front`；\n'
            '4. 队满时还往 `data[rear]` 里写，把队头的数据覆盖掉，FIFO 全乱。\n\n'
            '复杂度：四个操作都是 O(1)；空间 O(max_size)。'
        ),
        'expected_output': (
            'True True True True\n'
            'True False\n'
            '1 2\n'
            'True True\n'
            '3 4 5 6\n'
            'True None'
        ),
        'hints': [
            '队空看 front == rear，队满看 (rear + 1) % max_size == front，差别就在那个空位',
            '入队先把值写进 data[rear]，再把 rear 取模后移；出队先取值，再把 front 取模后移',
        ],
    },
    # ── 专题 130 823·串数组与广义表 ───────────────────────
    {
        'id': 'x823-010',
        'track': 'algorithm',
        'chapter_id': 130,
        'chapter_title': '823·串数组与广义表',
        'topic': '823·串数组与广义表',
        'title': 'KMP 算法 next 数组计算（下标从 0 起，next[0] = -1）',
        'difficulty': 2,
        'tags': ['KMP', 'next 数组', '串匹配'],
        'statement': (
            '考点：KMP 的 next 数组（填空必考）。\n\n'
            '已知模式串 `pattern`（普通字符串）。\n\n'
            '定义函数 `get_next(pattern)`：计算模式串的 next 数组，'
            '返回一个**与模式串等长**的列表。\n\n'
            '本题采用**下标从 0 开始**的写法：\n\n'
            '- `next[0] = -1`（约定值）；\n'
            '- 对 `j >= 1`，`next[j]` 是满足 `pattern[0:k] == pattern[j - k:j]` 的**最大** `k`'
            '（`0 ≤ k < j`）——也就是「`pattern` 前 j 个字符」的**最长相等真前缀 / 真后缀**的长度；\n'
            '- 空串返回空列表 `[]`。\n\n'
            '例如 `pattern = "ababc"`：\n\n'
            '- `next[0] = -1`；\n'
            '- `j = 1`（子串 `a`）：真前后缀只能是空串，`next[1] = 0`；\n'
            '- `j = 2`（`ab`）：`a ≠ b`，`next[2] = 0`；\n'
            '- `j = 3`（`aba`）：`a == a`（长度 1），`next[3] = 1`；\n'
            '- `j = 4`（`abab`）：`ab == ab`（长度 2），`next[4] = 2`；\n'
            '- 所以 `get_next("ababc")` 返回 `[-1, 0, 0, 1, 2]`。\n\n'
            '要求：用**递推**（KMP 求 next 的标准做法）来算——`i` 从前往后扫描，'
            '`j` 表示当前已经匹配上的前缀长度；`pattern[i] == pattern[j]` 就同时前进，'
            '否则让 `j` 回退到 `next[j]`（`j == -1` 时退无可退，`i` 前进、`j` 归 0）。'
            '这样做是 O(n)；不要对每个位置都从头暴力枚举前后缀（那是 O(n²)）。\n\n'
            '最后打印 `get_next("ababc")`、`get_next("aaa")`、`get_next("")`，'
            '以及把 `get_next("ababc")` 每个值加 1 得到的结果'
            '（那就是教材上下标从 1 开始的 next 数组，可以对照一下）。'
        ),
        'starter_code': (
            'def get_next(pattern):\n'
            '    n = len(pattern)\n'
            '    if n == 0:\n'
            '        return []\n'
            '    nxt = [-1] * n\n'
            '    # i 扫描、j 回溯：相等就同时前进并把 j 写进 nxt[i]，否则 j = nxt[j]\n'
            '    pass\n'
        ),
        'solution': (
            "def get_next(pattern):\n"
            "    n = len(pattern)\n"
            "    if n == 0:\n"
            "        return []\n"
            "    nxt = [-1] * n\n"
            "    i = 0\n"
            "    j = -1\n"
            "    while i < n - 1:\n"
            "        if j == -1 or pattern[i] == pattern[j]:\n"
            "            i += 1\n"
            "            j += 1\n"
            "            nxt[i] = j\n"
            "        else:\n"
            "            j = nxt[j]\n"
            "    return nxt\n"
            "\n"
            "print(get_next('ababc'))\n"
            "print(get_next('aaa'))\n"
            "print(get_next(''))\n"
            "print([v + 1 for v in get_next('ababc')])\n"
        ),
        'checks': [
            "assert get_next('ababc') == [-1, 0, 0, 1, 2], '题目给的例子 ababc 应当是 [-1, 0, 0, 1, 2]，实际 %r' % (get_next('ababc'),)",
            "assert get_next('') == [], '空串应返回空列表，实际 %r' % (get_next(''),)",
            "assert get_next('a') == [-1], '只有一个字符时只有 next[0] = -1，实际 %r' % (get_next('a'),)",
            "assert get_next('aa') == [-1, 0], 'aa 应当是 [-1, 0]，实际 %r' % (get_next('aa'),)",
            "assert get_next('aaa') == [-1, 0, 1], 'aaa 应当是 [-1, 0, 1]，实际 %r' % (get_next('aaa'),)",
            "assert get_next('aaaa') == [-1, 0, 1, 2], 'aaaa 应当是 [-1, 0, 1, 2]，实际 %r' % (get_next('aaaa'),)",
            "assert get_next('abab') == [-1, 0, 0, 1], 'abab 应当是 [-1, 0, 0, 1]，实际 %r' % (get_next('abab'),)",
            "assert get_next('abcabc') == [-1, 0, 0, 0, 1, 2], 'abcabc 应当是 [-1, 0, 0, 0, 1, 2]，实际 %r' % (get_next('abcabc'),)",
            "assert get_next('abcac') == [-1, 0, 0, 0, 1], 'abcac 应当是 [-1, 0, 0, 0, 1]，实际 %r' % (get_next('abcac'),)",
            "assert get_next('aabaaab') == [-1, 0, 1, 0, 1, 2, 2], 'aabaaab 应当是 [-1, 0, 1, 0, 1, 2, 2]（注意 next[2]：子串 aa 的最长真前后缀长度是 1），实际 %r' % (get_next('aabaaab'),)",
            "_p = 'abracadabra'\n_nxt = get_next(_p)\nassert len(_nxt) == len(_p), '返回的 next 数组长度必须和模式串一样长（%d），实际 %d' % (len(_p), len(_nxt))\nassert all(-1 <= _v < _i for _i, _v in enumerate(_nxt)), '第 j 个值必须满足 -1 <= next[j] < j，实际 %r' % (_nxt,)",
            "def _naive(pattern):\n    out = [-1] * len(pattern)\n    for _j in range(1, len(pattern)):\n        _best = 0\n        for _k in range(_j - 1, 0, -1):\n            if pattern[:_k] == pattern[_j - _k:_j]:\n                _best = _k\n                break\n        out[_j] = _best\n    return out",
            "for _p in ('abcabcabd', 'aabaaabaa', 'abacabadabacaba', 'mississippi', 'aaaaab'):\n    assert get_next(_p) == _naive(_p), '模式串 %r 算出来是 %r，按「最长相等真前后缀」的定义应当是 %r' % (_p, get_next(_p), _naive(_p))",
            "_p = 'ab' * 100\nassert get_next(_p) == _naive(_p), '200 个字符的长模式串也要算对（它的 next 有「next[j] = j - 2」的规律）'",
            "assert get_next('ababc')[0] == -1, '注意 next[0] 是 -1 而不是 0，整张表不要整体错位'",
        ],
        'explanation': (
            'next 数组回答的是一个问题：**当第 j 个字符失配时，模式串应该退到哪个位置继续比？**'
            '退回去的位置，就是「已经匹配上的那一段里最长相等真前后缀」的长度。\n\n'
            '递推写法（本题要求）只扫一遍：\n\n'
            '```python\n'
            'i = 0\n'
            'j = -1                 # j 表示「已经匹配上的前缀长度」，-1 是退无可退的标志\n'
            'while i < n - 1:\n'
            '    if j == -1 or pattern[i] == pattern[j]:\n'
            '        i += 1\n'
            '        j += 1\n'
            '        nxt[i] = j     # 先加再写：这里用的是新的 i\n'
            '    else:\n'
            '        j = nxt[j]     # 失配就退到 nxt[j]，i 不动\n'
            '```\n\n'
            '**为什么是 `nxt[i] = j` 而不是 `nxt[i - 1] = j`？** 因为 i 和 j 是「同时前进」的：'
            '现在 `pattern[i] == pattern[j]` 说明前 j + 1 个字符构成了一对相等的前后缀，'
            '所以是**加完之后**的第 i 个位置记下 j。这是手写 KMP 最常见的差一格错误。\n\n'
            '**`j = -1` 是干什么的？** 它是「退到最前面、连一个字符都没匹配上」的标志。'
            '有了它，就不需要为第一个字符单独写分支：`j == -1` 时直接把 i、j 各推进一步，'
            '于是 `next[i] = 0`（前缀长度为 0），逻辑统一。\n\n'
            '**和教材（下标从 1 起）的换算**：严蔚敏教材里 `next[1] = 0`，'
            '而我们这里 `next[0] = -1`，两张表**整体相差 1**——把本题结果每个值加 1，'
            '就得到教材上那张表（`ababc` → `[0, 1, 1, 2, 3]`）。'
            '考试填空时先看清题目用的是哪一套下标，这一步错整题皆错。\n\n'
            '**常见错误**：\n\n'
            '1. `nxt[i] = j` 写成先写后加，整张表错位一格；\n'
            '2. 循环条件写成 `while i < n`，最后多算一格（数组越界）；\n'
            '3. 把 `j = nxt[j]` 写成 `j -= 1`——那不是 KMP，退化成朴素匹配；\n'
            '4. 忘记处理空串，`nxt[0]` 直接报错。\n\n'
            '复杂度：时间 O(n)（i 只前进不后退，j 的回退是均摊的）、空间 O(n)（next 数组本身）。'
        ),
        'expected_output': '[-1, 0, 0, 1, 2]\n[-1, 0, 1]\n[]\n[0, 1, 1, 2, 3]',
        'hints': [
            'j 表示「已经匹配上的前缀长度」，初值 -1 是退无可退的标志',
            '相等就 i += 1、j += 1，然后把 j 写进 next[i]；不相等就 j = next[j]（i 不动）',
        ],
    },
    {
        'id': 'x823-011',
        'track': 'algorithm',
        'chapter_id': 130,
        'chapter_title': '823·串数组与广义表',
        'topic': '823·串数组与广义表',
        'title': '对称矩阵压缩存储与下标换算',
        'difficulty': 1,
        'tags': ['对称矩阵', '压缩存储', '下标换算'],
        'statement': (
            '考点：对称矩阵的一维数组压缩、下标换算。\n\n'
            '已知一个 n 阶**对称矩阵** `matrix`（用二维列表表示，满足 `matrix[i][j] == matrix[j][i]`）。\n\n'
            '定义两个函数：\n\n'
            '1. `matrix_to_arr(matrix)`：把矩阵**压缩存储**到一维列表里，'
            '按「**行优先、只存下三角（含对角线）**」的顺序排列：'
            '`(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), …`，返回这个一维列表；\n'
            '2. `get_val(arr, i, j)`：给出一维数组 `arr` 和原矩阵的**行号 i、列号 j（都从 0 开始）**，'
            '返回对应的矩阵元素值；当 `i < j`（要查上三角）时，利用对称性'
            '`matrix[i][j] == matrix[j][i]` 换算成查下三角。\n\n'
            '下标换算公式（本题的核心，请自己推一遍）：\n\n'
            '```\n'
            '行优先存下三角时，第 i 行之前一共有 1 + 2 + … + i = i (i + 1) / 2 个元素，\n'
            '所以 (i, j)（i >= j）在一维数组里的下标是  k = i * (i + 1) / 2 + j\n'
            '```\n\n'
            '其他要求：\n\n'
            '- 空矩阵 `[]` 压缩后是空列表 `[]`；\n'
            '- 题目保证 `i`、`j` 都是合法下标（`0 ≤ i, j < n`），不用做越界检查；\n'
            '- 不要把上三角的元素也存进去——n 阶对称矩阵只需要 `n (n + 1) / 2` 个存储位置，'
            '3 阶只要 6 个，存成 9 个就失去了压缩存储的意义；\n'
            '- 不要修改传入的 `matrix`。\n\n'
            '最后对 `[[1, 2, 3], [2, 4, 5], [3, 5, 6]]` 打印压缩后的一维数组，'
            '并打印 `get_val(arr, 2, 1)`、`get_val(arr, 1, 2)`、`get_val(arr, 0, 0)` 的结果。'
        ),
        'starter_code': (
            'def matrix_to_arr(matrix):\n'
            '    arr = []\n'
            '    # 行优先存下三角：第 i 行存 matrix[i][0] … matrix[i][i]\n'
            '    pass\n'
            '\n'
            'def get_val(arr, i, j):\n'
            '    # i < j 时先换成 (j, i)，再用 k = i * (i + 1) // 2 + j 取下标\n'
            '    pass\n'
        ),
        'solution': (
            "def matrix_to_arr(matrix):\n"
            "    n = len(matrix)\n"
            "    arr = []\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1):\n"
            "            arr.append(matrix[i][j])\n"
            "    return arr\n"
            "\n"
            "def get_val(arr, i, j):\n"
            "    if i < j:\n"
            "        i, j = j, i\n"
            "    return arr[i * (i + 1) // 2 + j]\n"
            "\n"
            "m = [[1, 2, 3], [2, 4, 5], [3, 5, 6]]\n"
            "a = matrix_to_arr(m)\n"
            "print(a)\n"
            "print(get_val(a, 2, 1))\n"
            "print(get_val(a, 1, 2))\n"
            "print(get_val(a, 0, 0))\n"
        ),
        'checks': [
            "assert matrix_to_arr([]) == [], '空矩阵压缩后应当是空列表，实际 %r' % (matrix_to_arr([]),)",
            "assert matrix_to_arr([[5]]) == [5], '1 阶矩阵只有对角线一个元素，实际 %r' % (matrix_to_arr([[5]]),)",
            "assert matrix_to_arr([[1, 2], [2, 3]]) == [1, 2, 3], '2 阶对称矩阵应当压缩成 [1, 2, 3]（只存下三角），实际 %r' % (matrix_to_arr([[1, 2], [2, 3]]),)",
            "_m = [[1, 2, 3], [2, 4, 5], [3, 5, 6]]\n_a = matrix_to_arr(_m)\nassert _a == [1, 2, 4, 3, 5, 6], '3 阶按行优先存下三角应当是 [1, 2, 4, 3, 5, 6]，实际 %r' % (_a,)\nassert len(_a) == 6, '3 阶对称矩阵只要 n(n+1)/2 = 6 个位置，不是 9 个，实际 %d 个' % (len(_a),)",
            "_m = [[1, 2, 3], [2, 4, 5], [3, 5, 6]]\n_a = matrix_to_arr(_m)\nfor _i in range(3):\n    for _j in range(3):\n        assert get_val(_a, _i, _j) == _m[_i][_j], '(%d, %d) 处的值应当是 %r，实际 %r' % (_i, _j, _m[_i][_j], get_val(_a, _i, _j))",
            "_m = [[1, 2, 3], [2, 4, 5], [3, 5, 6]]\n_a = matrix_to_arr(_m)\nassert get_val(_a, 2, 1) == 5 and get_val(_a, 1, 2) == 5, '下三角 (2, 1) 与上三角 (1, 2) 是对称位置，都应当是 5，实际 %r / %r' % (get_val(_a, 2, 1), get_val(_a, 1, 2))",
            "_m = [[1, 2, 3], [2, 4, 5], [3, 5, 6]]\n_a = matrix_to_arr(_m)\nassert get_val(_a, 0, 0) == 1 and get_val(_a, 1, 1) == 4 and get_val(_a, 2, 2) == 6, '对角线元素 (i, i) 也要取对（k = i(i+1)/2 + i），实际 %r' % ([get_val(_a, _i, _i) for _i in range(3)],)",
            "_m = [[_i * 10 + _j for _j in range(5)] for _i in range(5)]\n_m = [[_m[min(_i, _j)][max(_i, _j)] for _j in range(5)] for _i in range(5)]\n_a = matrix_to_arr(_m)\nassert len(_a) == 15, '5 阶对称矩阵只要 15 个存储位置，实际 %d 个' % (len(_a),)\nfor _i in range(5):\n    for _j in range(5):\n        assert get_val(_a, _i, _j) == _m[_i][_j], '5 阶矩阵 (%d, %d) 处的值应当是 %r，实际 %r' % (_i, _j, _m[_i][_j], get_val(_a, _i, _j))",
            "_m = [[7, 1], [1, 8]]\n_a = matrix_to_arr(_m)\nassert get_val(_a, 0, 1) == get_val(_a, 1, 0) == 1, '上三角元素必须用对称性换成下三角去查，实际 %r' % (get_val(_a, 0, 1),)",
            "_m = [[1, 2], [2, 3]]\nmatrix_to_arr(_m)\nassert _m == [[1, 2], [2, 3]], '压缩存储只是读出下三角，不要修改原矩阵'",
            "_m = [[9]]\n_a = matrix_to_arr(_m)\nassert get_val(_a, 0, 0) == 9, '1 阶矩阵取 (0, 0) 应当是 9，实际 %r' % (get_val(_a, 0, 0),)",
            "_m = [[1, 2, 3, 4], [2, 5, 6, 7], [3, 6, 8, 9], [4, 7, 9, 10]]\n_a = matrix_to_arr(_m)\nassert _a == [1, 2, 5, 3, 6, 8, 4, 7, 9, 10], '4 阶对称矩阵按行优先存下三角应当是 [1, 2, 5, 3, 6, 8, 4, 7, 9, 10]，实际 %r' % (_a,)",
        ],
        'explanation': (
            '对称矩阵里 `a[i][j]` 和 `a[j][i]` 是同一个值，只存一半就够了：'
            'n 阶矩阵从 n² 个位置压到 **n(n+1)/2** 个，几乎省掉一半空间。\n\n'
            '**下标换算要自己推**，别死记：行优先存下三角时，'
            '第 i 行之前有第 0、1、…、i − 1 行，'
            '它们分别有 1、2、…、i 个元素，加起来正是 `1 + 2 + … + i = i(i+1)/2`；'
            '再数上第 i 行里 `(i, j)` 前面还有 j 个元素（下标 0…j − 1），于是\n\n'
            '```\n'
            'k = i (i + 1) / 2 + j          （前提是 i >= j）\n'
            '```\n\n'
            '```python\n'
            'def get_val(arr, i, j):\n'
            '    if i < j:\n'
            '        i, j = j, i        # 上三角：靠对称性换成下三角\n'
            '    return arr[i * (i + 1) // 2 + j]\n'
            '```\n\n'
            '**为什么先交换再套公式？** 公式的前提是 `i >= j`（只存了左下角）。'
            '查上三角时直接套公式会取到错误的位置，甚至越界。\n\n'
            '**考试里常见的变体**：\n\n'
            '- 只存上三角（行优先）：偏移量换成「第 j 列之前」的累加，'
            '即 `k = j(j+1)/2 + i`；\n'
            '- 下标从 1 开始的教材写法：`k = (i − 1) i / 2 + (j − 1)`，本质是同一公式平移一格；\n'
            '- 三对角矩阵、稀疏矩阵的三元组表示，套路一致：'
            '先算「前面整块有多少个」，再加上块内偏移。\n\n'
            '**常见错误**：\n\n'
            '1. 把 `i(i+1)/2` 写成 `i²/2` 或 `i(i−1)/2`——差一行，全盘错位；\n'
            '2. 上三角忘了交换，取到的是另一个位置的值；\n'
            '3. 压缩时把上三角也存进去（长度变成 n²），本题明确要求只存下三角；\n'
            '4. Python 里 `i * (i + 1) / 2` 是浮点数，必须写 `//`，'
            '否则拿浮点下标去索引直接报 TypeError。\n\n'
            '复杂度：压缩要扫 n(n+1)/2 个元素，时间 O(n²)；`get_val` 是 O(1)。'
        ),
        'expected_output': '[1, 2, 4, 3, 5, 6]\n5\n5\n1',
        'hints': [
            '第 i 行之前一共有 1 + 2 + … + i = i(i+1)/2 个元素，这就是偏移量',
            'i < j 时先交换成 i >= j 再套公式；除法记得用 // 得到整数下标',
        ],
    },
    {
        'id': 'x823-012',
        'track': 'algorithm',
        'chapter_id': 130,
        'chapter_title': '823·串数组与广义表',
        'topic': '823·串数组与广义表',
        'title': '广义表的表头表尾操作（取出嵌套原子 f）',
        'difficulty': 2,
        'tags': ['广义表', 'head', 'tail', '嵌套结构'],
        'statement': (
            '考点：广义表的 head / tail 运算。\n\n'
            '用 Python 列表模拟广义表：**原子元素用字符串表示**（如 `b`、`f`），'
            '子表仍然是列表（如 `[f, c, d]` 写成 `["f", "c", "d"]`）。\n\n'
            '定义两个函数（约定与教材一致）：\n\n'
            '- `head(ls)`：返回广义表的**表头**——就是第一个元素本身；'
            '如果第一个元素是子表，返回的就是那个子表；空表 `[]` 返回 `None`；\n'
            '- `tail(ls)`：返回广义表的**表尾**——**除表头外其余元素组成的广义表**。'
            '注意表尾**一定是一个表**（列表）：长度为 1 的广义表，其表尾是**空表** `[]`，'
            '不是 `None`；空表 `[]` 的 tail 返回 `None`；\n'
            '- 两个函数都**不许修改**传入的广义表（`tail` 要返回一个新列表）。\n\n'
            '然后完成教材上的经典练习：**从广义表 `[b, [f, c, d], a]` 中取出原子 `f`**'
            '（Python 里这个广义表写作 `["b", ["f", "c", "d"], "a"]`）。\n\n'
            '提示：先 `tail` 掉表头 `b`，再 `head` 得到子表 `["f", "c", "d"]`，'
            '对子表再取一次表头就是 `f`——把这个嵌套表达式写出来并打印。\n\n'
            '最后依次打印：该广义表的表头、表尾、取出的 `f`、用 head / tail 取出的 `a`，'
            '以及空表的 `head([])`。'
        ),
        'starter_code': (
            'def head(ls):\n'
            '    # 空表返回 None，否则返回第一个元素本身\n'
            '    pass\n'
            '\n'
            'def tail(ls):\n'
            '    # 空表返回 None，否则返回「除表头外其余元素组成的表」\n'
            '    pass\n'
        ),
        'solution': (
            "def head(ls):\n"
            "    if not ls:\n"
            "        return None\n"
            "    return ls[0]\n"
            "\n"
            "def tail(ls):\n"
            "    if not ls:\n"
            "        return None\n"
            "    return ls[1:]\n"
            "\n"
            "ls = ['b', ['f', 'c', 'd'], 'a']\n"
            "print(head(ls))\n"
            "print(tail(ls))\n"
            "print(head(head(tail(ls))))\n"
            "print(head(tail(tail(ls))))\n"
            "print(head([]))\n"
        ),
        'checks': [
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert head(_ls) == 'b', '表头应当是第一个元素 b（原子），实际 %r' % (head(_ls),)",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert tail(_ls) == [['f', 'c', 'd'], 'a'], '表尾应当是「除表头外其余元素组成的表」，即 [[f, c, d], a]，实际 %r' % (tail(_ls),)",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert head(head(tail(_ls))) == 'f', '经典练习：head(head(tail(ls))) 应当取出原子 f，实际 %r' % (head(head(tail(_ls))),)",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert head(tail(tail(_ls))) == 'a', '连续两次 tail 去掉前面两个元素，再 head 就能取出 a，实际 %r' % (head(tail(tail(_ls))),)",
            "assert head(['x']) == 'x', '只有一个元素时，表头就是它自己'",
            "assert tail(['x']) == [], '只有一个元素时表尾是空表 []，不是 None——表尾一定是个表'",
            "assert head([]) is None and tail([]) is None, '空表既没有表头也没有表尾，按约定都返回 None（不要抛出异常）'",
            "assert head([['f', 'c', 'd'], 'a']) == ['f', 'c', 'd'], '表头本身是子表时，返回的是那个子表本身（不是它的表头）'",
            "_ls = ['b', 'a']\ntail(_ls)\nassert _ls == ['b', 'a'], '题面要求不修改原广义表：tail 返回的必须是新列表'",
            "_l2 = ['a', ['b', ['c']]]\nassert head(head(tail(head(tail(_l2))))) == 'c', '两层嵌套：一路 head / tail 拆下去应当能取出最里层的原子 c，实际 %r' % (head(head(tail(head(tail(_l2))))),)",
            "_l3 = [[], 'a']\nassert head(_l3) == [] and tail(_l3) == ['a'], '表头可以是一个空的子表，此时 head 返回 []（是空表，不是 None）'",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert len(tail(_ls)) == 2 and len(tail(tail(_ls))) == 1, '每 tail 一次表长少 1（3 个元素 → 2 个 → 1 个）'",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\nassert tail(_ls)[0] == ['f', 'c', 'd'], '子表是作为一个整体参与 head / tail 运算的，tail 之后它还在表里'",
            "_ls = ['b', ['f', 'c', 'd'], 'a']\ntail(_ls)\nassert head(_ls) == 'b' and tail(_ls) is not _ls, 'tail 不能原地改原表，也不能把表头吃掉（调用之后 ls 的表头还是 b）'",
        ],
        'explanation': (
            '广义表（列表）是**嵌套结构**：一个广义表要么是空表，'
            '要么是「一个表头 + 一个表尾」，而表尾本身又是广义表。'
            'head / tail 就是把这条定义翻译成代码的两个操作。\n\n'
            '```python\n'
            'def head(ls):        # 表头：第一个元素本身（可能是原子，也可能是子表）\n'
            '    if not ls:\n'
            '        return None\n'
            '    return ls[0]\n'
            '\n'
            'def tail(ls):        # 表尾：剩下的元素构成的「表」（一定是列表）\n'
            '    if not ls:\n'
            '        return None\n'
            '    return ls[1:]\n'
            '```\n\n'
            '**head 和 tail 的地位并不对称**，这是最容易考、也最容易错的一点：\n\n'
            '- `head` 的结果**可能是原子，也可能是表**：`head([\'b\', ...])` 得到原子 `b`，'
            '而 `head([[\'f\', \'c\', \'d\'], \'a\'])` 得到子表 `[\'f\', \'c\', \'d\']`；\n'
            '- `tail` 的结果**永远是表**：哪怕只剩一个元素，表尾也是空表 `[]`，'
            '绝不是 `None`——`tail([\'x\']) == []`。\n\n'
            '**取出 f 的过程**（本题的经典练习）：\n\n'
            '```\n'
            'ls = [b, [f, c, d], a]\n'
            'tail(ls)          → [[f, c, d], a]      去掉表头 b\n'
            'head(tail(ls))    → [f, c, d]           取到子表\n'
            'head(...)         → f                   再取子表的表头，就是原子 f\n'
            '```\n\n'
            '写成一行就是 `head(head(tail(ls)))`。'
            '同理 `head(tail(tail(ls)))` 取出的是 `a`——每一层 head / tail 只剥掉一层。\n\n'
            '**常见错误**：\n\n'
            '1. `tail` 返回 `ls[1]`（第二个元素）而不是 `ls[1:]`（剩下的元素组成的表）；\n'
            '2. 用 `del ls[0]` 或 `ls.pop(0)` 实现 tail，把调用方的表改坏了；\n'
            '3. 空表时直接 `ls[0]` 报 IndexError，按题面约定应当返回 None；\n'
            '4. 认为「表尾是空表」等于「没有表尾」——空表 `[]` 和 `None` 是两回事。\n\n'
            '复杂度：head 是 O(1)；Python 的 `ls[1:]` 会复制一份，所以 tail 是 O(n)；'
            '沿嵌套结构逐层拆解的总代价是 O(元素个数)。'
        ),
        'expected_output': "b\n[['f', 'c', 'd'], 'a']\nf\na\nNone",
        'hints': [
            'head 取 ls[0]（可能是原子也可能是子表），tail 取 ls[1:]（结果一定是个表）',
            '取 f 的表达式是 head(head(tail(ls)))：先剥掉 b，拿到子表，再取子表的表头',
        ],
    },
]
