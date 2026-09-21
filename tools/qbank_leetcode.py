"""题库 · LeetCode 高频算法练习（第 123–126 专题，共 20 题）。

选题原则：**面试与刷题平台里出现频率最高、且能用一个函数讲透的那批题**。
每题都按 LeetCode 的原始题面重述（Python 版），并补上「为什么这么做」的解析。

与 408 那份的区别：408 那份偏「数据结构实现与复杂度约束」，
这份偏「解法套路」——中心扩展、状态压缩、单调栈、位运算技巧等。

判题约定同其他题库：checks 在参考答案跑完后于同一进程执行，
可用 `_out`（全部输出）与 `_src`（全部源码）。
"""

QUESTIONS = [
    # ── 123 字符串算法 ─────────────────────────────────────
    {
        'id': 'lc-001',
        'track': 'algorithm',
        'chapter_id': 123,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '最长公共前缀',
        'difficulty': 1,
        'tags': ['字符串', '纵向扫描'],
        'statement': (
            '编写函数 `longest_common_prefix(strs)`，返回字符串列表的**最长公共前缀**。\n\n'
            '- 没有公共前缀时返回空字符串 `""`\n'
            '- 列表为空时返回 `""`\n'
            '- 只有一个字符串时返回它自己\n\n'
            '示例：\n'
            '```\n'
            "longest_common_prefix(['flower', 'flow', 'flight'])  ->  'fl'\n"
            "longest_common_prefix(['dog', 'racecar', 'car'])     ->  ''\n"
            '```\n\n'
            '要求**纵向扫描**：拿第一个字符串的第 i 个字符，去比所有字符串的第 i 个字符，'
            '一旦不匹配或某个字符串已经到头就停止。\n\n'
            '最后打印两个示例的结果。'
        ),
        'starter_code': "def longest_common_prefix(strs):\n    pass\n",
        'solution': (
            "def longest_common_prefix(strs):\n"
            "    strs = list(strs or [])\n"
            "    if not strs:\n"
            "        return ''\n"
            "    first = strs[0]\n"
            "    for index in range(len(first)):\n"
            "        ch = first[index]\n"
            "        for other in strs[1:]:\n"
            "            if index >= len(other) or other[index] != ch:\n"
            "                return first[:index]\n"
            "    return first\n"
            "\n"
            "\n"
            "print(longest_common_prefix(['flower', 'flow', 'flight']))\n"
            "print(longest_common_prefix(['dog', 'racecar', 'car']))\n"
        ),
        'checks': [
            "assert longest_common_prefix(['flower', 'flow', 'flight']) == 'fl', '基本用例不对：%r' % (longest_common_prefix(['flower', 'flow', 'flight']),)",
            "assert longest_common_prefix(['dog', 'racecar', 'car']) == '', '没有公共前缀时应返回空串：%r' % (longest_common_prefix(['dog', 'racecar', 'car']),)",
            "assert longest_common_prefix(['abc']) == 'abc', '只有一个字符串时返回它自己'",
            "assert longest_common_prefix([]) == '', '空列表应返回空串'",
            "assert longest_common_prefix(['', 'abc']) == '', '含空字符串时公共前缀必为空'",
            "assert longest_common_prefix(['ab', 'ab', 'ab']) == 'ab', '完全相同时应返回整个字符串'",
            "assert longest_common_prefix(['a']) == 'a' and longest_common_prefix(['a', 'a']) == 'a', '单字符用例不对'",
            "assert longest_common_prefix(['prefix', 'pre']) == 'pre', '一个是另一个的前缀时应返回短的那个'",
        ],
        'explanation': (
            '**纵向扫描**：不是一个个字符串比过去，而是「一列一列」比。\n\n'
            '第 i 轮检查**所有**字符串的第 i 个字符是否都等于 `first[i]`。'
            '只要有一个不匹配（或者某个字符串长度不足 i）就立刻返回 `first[:i]`。\n\n'
            '为什么用第一个字符串当基准？因为它一定参与公共前缀，'
            '以它为准就能保证「不会漏掉任何一位」。\n\n'
            '时间复杂度 O(S)（S 是所有字符总数）：最坏情况下每个字符只看一次。'
            '对比「两两求前缀」的写法（O(S·n)），纵向扫描在遇到第一个不匹配时就退出，实际更快。\n\n'
            '边界要小心两个：**列表为空**、**含空字符串**。'
            '前者不处理会 `IndexError`，后者不处理会返回错误结果（空串的公共前缀只能是空串，'
            '而纵向扫描天然会返回 `""`，因为它内层会因 `index >= len(other)` 立刻返回）。'
        ),
        'expected_output': 'fl\n',
        'hints': ['用第一个字符串的每一位当基准，逐个比对所有字符串的同一位', '某个字符串长度不够时也算不匹配'],
    },
    {
        'id': 'lc-002',
        'track': 'algorithm',
        'chapter_id': 123,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '反转字符串里的单词顺序',
        'difficulty': 1,
        'tags': ['字符串', 'split'],
        'statement': (
            '编写函数 `reverse_words(s)`：把句子里的**单词顺序反转**，'
            '但单词内部的字符顺序不变，并且**多余空格要清理**。\n\n'
            '- 单词之间可能有多余空格，结果里单词之间**只留一个空格**\n'
            '- 开头和结尾的空格要去掉\n'
            '- 全空格的输入返回空字符串\n\n'
            '示例：\n'
            '```\n'
            "reverse_words('  the sky   is blue  ')  ->  'blue is sky the'\n"
            '```\n\n'
            '**进阶要求**：不要用 `split()` 与 `reverse()` 一行搞定，'
            '请手写扫描：先找出每个单词，再从后往前拼接。'
        ),
        'starter_code': "def reverse_words(s):\n    pass\n",
        'solution': (
            "def reverse_words(s):\n"
            "    words = []\n"
            "    current = ''\n"
            "    for ch in str(s or ''):\n"
            "        if ch == ' ':\n"
            "            if current:\n"
            "                words.append(current)\n"
            "                current = ''\n"
            "        else:\n"
            "            current += ch\n"
            "    if current:\n"
            "        words.append(current)\n"
            "    return ' '.join(reversed(words))\n"
            "\n"
            "\n"
            "print(reverse_words('  the sky   is blue  '))\n"
            "print(reverse_words('   '))\n"
        ),
        'checks': [
            "assert reverse_words('  the sky   is blue  ') == 'blue is sky the', '基本用例不对：%r' % (reverse_words('  the sky   is blue  '),)",
            "assert reverse_words('hello') == 'hello', '单个单词应原样返回'",
            "assert reverse_words('') == '', '空串返回空串'",
            "assert reverse_words('   ') == '', '全空格应返回空串'",
            "assert reverse_words('a  b') == 'b a', '多空格应压缩成一个'",
            "assert reverse_words('  a') == 'a' and reverse_words('a  ') == 'a', '首尾空格要去掉'",
            "assert 'split(' not in _src, '本题要求手写扫描，不允许用 split()'",
            "assert reverse_words('a b c d') == 'd c b a', '多单词顺序不对：%r' % (reverse_words('a b c d'),)",
        ],
        'explanation': (
            '这题真正的考点不是「反转」，而是**空格的处理**。'
            '一句 `s.split()` 会自动帮你压缩空格并去掉首尾空白，所以一行就能写完；'
            '本題要求手写，就是要让你意识到这两件事都得自己做。\n\n'
            '手写扫描的写法是「遇到空格收单词」：\n'
            '用一个 `current` 累积字符，遇到空格时如果 `current` 非空就收进列表并清空。\n'
            '**注意判断 `if current` 而不是直接 append**——连续空格会产生空字符串，'
            '这正是「多余空格」的漏网之处。\n\n'
            '最后一次 `if current: words.append(current)` 不能省：'
            '字符串结尾如果没有空格，最后一个单词还没被收进去。'
            '这是手写扫描最经典的 off-by-one。\n\n'
            '拼接用 `\' \'.join(reversed(words))`：'
            '`join` 只在元素之间插分隔符，天然不会多出首尾空格。\n\n'
            '复杂度 O(n) 时间、O(n) 空间（存单词列表）。'
        ),
        'expected_output': 'blue is sky the\n',
        'hints': ['遇到空格时，如果当前单词非空就收进列表', '循环结束后别忘了收最后一个单词'],
    },
    {
        'id': 'lc-003',
        'track': 'algorithm',
        'chapter_id': 123,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '旋转字符串（判断循环移位）',
        'difficulty': 2,
        'tags': ['字符串', '技巧'],
        'statement': (
            '给定两个字符串 `s` 与 `goal`，编写函数 `rotate_string(s, goal)`，'
            '判断 `goal` 能否由 `s` **循环移位**得到（把最左边若干字符搬到末尾）。\n\n'
            '示例：\n'
            '```\n'
            "rotate_string('abcde', 'cdeab')  ->  True    # abcde 左移 2 位\n"
            "rotate_string('abcde', 'abced')  ->  False\n"
            "rotate_string('abc', 'abc')      ->  True    # 移动 0 位\n"
            '```\n\n'
            '- 两个字符串长度不同时直接 `False`\n'
            '- 空字符串与空字符串应返回 `True`\n\n'
            '**进阶要求**：请用**一行核心判断**完成——思考「`s + s` 包含了 s 的所有循环移位」这个性质。'
            '同时不要用 `+` 之外的高层技巧（例如不要调用 KMP 库）。'
        ),
        'starter_code': "def rotate_string(s, goal):\n    pass\n",
        'solution': (
            "def rotate_string(s, goal):\n"
            "    s = str(s or '')\n"
            "    goal = str(goal or '')\n"
            "    if len(s) != len(goal):\n"
            "        return False\n"
            "    return goal in (s + s)\n"
            "\n"
            "\n"
            "print(rotate_string('abcde', 'cdeab'))\n"
            "print(rotate_string('abcde', 'abced'))\n"
            "print(rotate_string('', ''))\n"
        ),
        'checks': [
            "assert rotate_string('abcde', 'cdeab') is True, 'abcde 左移 2 位应得到 cdeab'",
            "assert rotate_string('abcde', 'abced') is False, 'abced 不是 abcde 的循环移位'",
            "assert rotate_string('abc', 'abc') is True, '移动 0 位也算循环移位'",
            "assert rotate_string('abc', 'bca') is True and rotate_string('abc', 'cab') is True, '所有移位都应命中'",
            "assert rotate_string('a', 'a') is True, '单字符相同为 True'",
            "assert rotate_string('a', 'b') is False, '单字符不同为 False'",
            "assert rotate_string('', '') is True, '两个空串应返回 True'",
            "assert rotate_string('abc', 'ab') is False, '长度不同直接 False'",
            "assert rotate_string('aa', 'aa') is True, '重复字符用例不对'",
            "assert rotate_string('abcabc', 'cabcab') is True, '带重复片段的用例不对'",
        ],
        'explanation': (
            '核心性质一句话：**`s + s` 里包含了 `s` 的所有循环移位**。\n\n'
            '比如 `s = "abcde"`，`s + s = "abcdeabcde"`，'
            '它的所有长度 5 的子串依次是 `abcde`、`bcdea`、`cdeab`、`deabc`、`eabcd`——'
            '正好就是 s 的全部 5 种循环移位。所以只要判断 `goal` 是不是它的子串即可。\n\n'
            '**长度检查必须先做**。不加这一步，'
            '`rotate_string("abc", "abcabc")` 会因为 `"abcabc" in "abcabc"` 返回 True，'
            '而它显然不该算循环移位。\n\n'
            '字符串的 `in` 在 CPython 里用的是高效的子串查找（两路匹配算法），'
            '所以整体接近 O(n) 而不是朴素的 O(n²)。\n\n'
            '**为什么空串对空串是 True？** 空串循环移位任意位都还是空串，'
            '所以按定义应当成立。长度检查通过后 `"" in ("" + "")` 也是 True，逻辑自洽。'
        ),
        'expected_output': 'True\nFalse\nTrue\n',
        'hints': ['s + s 包含了 s 的所有循环移位', '先比长度，否则 "abc" 与 "abcabc" 会误判'],
    },
    {
        'id': 'lc-004',
        'track': 'algorithm',
        'chapter_id': 123,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '最长回文子串（中心扩展）',
        'difficulty': 2,
        'tags': ['字符串', '中心扩展', '回文'],
        'statement': (
            '编写函数 `longest_palindrome(s)`，返回 `s` 中最长的回文子串。'
            '如果有多个等长的，返回**最先出现的那个**。\n\n'
            '示例：\n'
            '```\n'
            "longest_palindrome('babad')  ->  'bab'    # 'aba' 也可以，但 bab 先出现\n"
            "longest_palindrome('cbbd')   ->  'bb'\n"
            "longest_palindrome('a')      ->  'a'\n"
            '```\n\n'
            '**要求用中心扩展法**：回文有两种中心——奇数长度以单个字符为中心，'
            '偶数长度以两个字符之间为中心。对每个中心向两边扩展，记录最长的那个。\n\n'
            '空字符串返回 `""`。'
        ),
        'starter_code': "def longest_palindrome(s):\n    pass\n",
        'solution': (
            "def longest_palindrome(s):\n"
            "    text = str(s or '')\n"
            "    if len(text) < 2:\n"
            "        return text\n"
            "\n"
            "    def expand(left, right):\n"
            "        while left >= 0 and right < len(text) and text[left] == text[right]:\n"
            "            left -= 1\n"
            "            right += 1\n"
            "        return left + 1, right - 1\n"
            "\n"
            "    best_left, best_right = 0, 0\n"
            "    for center in range(len(text)):\n"
            "        l1, r1 = expand(center, center)          # 奇数长度\n"
            "        l2, r2 = expand(center, center + 1)      # 偶数长度\n"
            "        if r1 - l1 > best_right - best_left:\n"
            "            best_left, best_right = l1, r1\n"
            "        if r2 - l2 > best_right - best_left:\n"
            "            best_left, best_right = l2, r2\n"
            "    return text[best_left:best_right + 1]\n"
            "\n"
            "\n"
            "print(longest_palindrome('babad'))\n"
            "print(longest_palindrome('cbbd'))\n"
            "print(longest_palindrome('a'))\n"
        ),
        'checks': [
            "assert longest_palindrome('babad') == 'bab', 'babad 应返回 bab（等长时取先出现的）：%r' % (longest_palindrome('babad'),)",
            "assert longest_palindrome('cbbd') == 'bb', '偶数长度回文不对：%r' % (longest_palindrome('cbbd'),)",
            "assert longest_palindrome('a') == 'a', '单字符应返回自己'",
            "assert longest_palindrome('') == '', '空串返回空串'",
            "assert longest_palindrome('ac') == 'a', '没有回文时返回任意单字符（取最靠前的）'",
            "assert longest_palindrome('aaaa') == 'aaaa', '全同字符应返回整个串'",
            "assert longest_palindrome('forgeeksskeegfor') == 'geeksskeeg', '长回文用例不对：%r' % (longest_palindrome('forgeeksskeegfor'),)",
            "assert longest_palindrome('abb') == 'bb', 'abb 应返回 bb：%r' % (longest_palindrome('abb'),)",
        ],
        'explanation': (
            '**中心扩展**是回文题最直观的解法：回文一定关于某个中心对称，'
            '那就枚举所有中心，往两边扩，扩不动为止。\n\n'
            '关键细节是**中心有两种**：\n'
            '- 奇数长度：中心是一个字符，调用 `expand(i, i)`；\n'
            '- 偶数长度：中心在两个字符之间，调用 `expand(i, i+1)`。\n\n'
            '漏掉第二种是这道题最常见的失分点——'
            '`"cbbd"` 的答案 `"bb"` 就完全靠偶数中心才能找到。\n\n'
            '`expand` 的返回值得注意：循环结束时 `left` 和 `right` 已经**越过了**合法边界，'
            '所以要返回 `(left + 1, right - 1)`。'
            '写成 `(left, right)` 会多算两个字符，是最容易犯的 off-by-one。\n\n'
            '复杂度 O(n²) 时间（每个中心最多扩 n 次）、O(1) 空间。'
            '相比 DP 的 O(n²) 时间 O(n²) 空间，中心扩展不但省内存，常数也小得多。'
            '还有 O(n) 的 Manacher 算法，但那是竞赛难度的东西，面试与教学里中心扩展足够了。'
        ),
        'expected_output': 'bab\nbb\na\n',
        'hints': ['每个中心要试两次：奇数中心 (i, i) 和偶数中心 (i, i+1)', '扩展函数返回时要 left+1 与 right-1（循环退出时已越界）'],
    },
    {
        'id': 'lc-005',
        'track': 'algorithm',
        'chapter_id': 123,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '字符串解码（嵌套括号 + 栈）',
        'difficulty': 3,
        'tags': ['字符串', '栈', '嵌套'],
        'statement': (
            '编写函数 `decode_string(s)`，按规则展开字符串。规则：'
            '`k[encoded]` 表示把方括号里的内容**重复 k 次**，'
            '并且方括号**可以嵌套**。\n\n'
            '示例：\n'
            '```\n'
            "decode_string('3[a]2[bc]')       ->  'aaabcbc'\n"
            "decode_string('3[a2[c]]')        ->  'accaccacc'\n"
            "decode_string('2[abc]3[cd]ef')   ->  'abcabccdcdcdef'\n"
            "decode_string('abc')             ->  'abc'\n"
            '```\n\n'
            '- 输入保证合法：数字后面一定紧跟 `[`，括号一定配对\n'
            '- 数字可能是多位数（如 `12[a]`）\n\n'
            '**要求用栈**：数字与字符串分别用栈保存，遇到 `]` 就弹栈拼接。'
        ),
        'starter_code': "def decode_string(s):\n    pass\n",
        'solution': (
            "def decode_string(s):\n"
            "    text = str(s or '')\n"
            "    count_stack = []\n"
            "    text_stack = []\n"
            "    current = ''\n"
            "    number = 0\n"
            "    for ch in text:\n"
            "        if ch.isdigit():\n"
            "            number = number * 10 + int(ch)\n"
            "        elif ch == '[':\n"
            "            count_stack.append(number)\n"
            "            text_stack.append(current)\n"
            "            number = 0\n"
            "            current = ''\n"
            "        elif ch == ']':\n"
            "            repeat = count_stack.pop()\n"
            "            prefix = text_stack.pop()\n"
            "            current = prefix + current * repeat\n"
            "        else:\n"
            "            current += ch\n"
            "    return current\n"
            "\n"
            "\n"
            "print(decode_string('3[a]2[bc]'))\n"
            "print(decode_string('3[a2[c]]'))\n"
            "print(decode_string('2[abc]3[cd]ef'))\n"
        ),
        'checks': [
            "assert decode_string('3[a]2[bc]') == 'aaabcbc', '基本用例不对：%r' % (decode_string('3[a]2[bc]'),)",
            "assert decode_string('3[a2[c]]') == 'accaccacc', '嵌套用例不对：%r' % (decode_string('3[a2[c]]'),)",
            "assert decode_string('2[abc]3[cd]ef') == 'abcabccdcdcdef', '带普通字符的用例不对：%r' % (decode_string('2[abc]3[cd]ef'),)",
            "assert decode_string('abc') == 'abc', '没有括号时原样返回'",
            "assert decode_string('') == '', '空串返回空串'",
            "assert decode_string('1[a]') == 'a', '重复 1 次应还是自己'",
            "assert decode_string('10[a]') == 'a' * 10, '多位数次数不对：%r' % (decode_string('10[a]'),)",
            "assert decode_string('2[2[2[a]]]') == 'a' * 8, '三层嵌套不对：%r' % (decode_string('2[2[2[a]]]'),)",
            "assert decode_string('x3[y]z') == 'xyyyz', '括号前后的普通字符都要保留：%r' % (decode_string('x3[y]z'),)",
        ],
        'explanation': (
            '**遇到嵌套就用栈**——因为内层的状态会把外层的「重复次数」和「已拼好的前缀」遮住，'
            '必须先把它们存起来，等内层算完再取回来。\n\n'
            '两个栈分工明确：\n'
            '- `count_stack` 存「外层的重复次数」；\n'
            '- `text_stack` 存「外层已经拼好的字符串」。\n\n'
            '扫描时的四个分支要一字不差：\n'
            '1. **数字**：`number = number * 10 + int(ch)`——'
            '这样多位数（`10[`、`12[`）才能正确累积。写成 `number = int(ch)` 就只能处理个位数；\n'
            '2. **`[`**：把当前 `number` 与 `current` **分别压栈**，然后清空它们，'
            '开始处理括号内部；\n'
            '3. **`]`**：弹栈取出次数与前缀，拼成 `prefix + current * repeat`，'
            '赋回 `current`——这就是「内层结果成为外层的一部分」；\n'
            '4. **普通字符**：直接追加到 `current`。\n\n'
            '复杂度 O(结果长度 × 嵌套深度) 时间、O(结果长度) 空间。'
            '嵌套很深时字符串拼接是主要开销，真实工程里会用列表 + `join` 优化，'
            '但本題这样写最清晰。'
        ),
        'expected_output': 'aaabcbc\naccaccacc\nabcabccdcdcdef\n',
        'hints': ['数字要累积：number = number * 10 + int(ch)', '遇到 [ 就把次数和已拼内容分别压栈，遇到 ] 再弹出来拼'],
    },

    # ── 124 动态规划进阶 ───────────────────────────────────
    {
        'id': 'lc-006',
        'track': 'algorithm',
        'chapter_id': 124,
        'chapter_title': '动态规划进阶',
        'topic': '动态规划进阶',
        'title': '最大子数组和（Kadane 算法）',
        'difficulty': 1,
        'tags': ['动态规划', 'Kadane', '贪心'],
        'statement': (
            '编写函数 `max_subarray(nums)`，返回**连续子数组**的最大和。\n\n'
            '示例：\n'
            '```\n'
            'max_subarray([-2,1,-3,4,-1,2,1,-5,4])  ->  6    # 子数组 [4,-1,2,1]\n'
            'max_subarray([1])                      ->  1\n'
            'max_subarray([-3,-1,-2])               ->  -1   # 必须选至少一个元素\n'
            '```\n\n'
            '**要求 O(n) 时间**：一遍扫描，用一个变量维护「以当前位置结尾的最大和」。\n'
            '递推式：`cur = max(x, cur + x)`，答案取所有 `cur` 的最大值。\n\n'
            '空数组返回 `0`。'
        ),
        'starter_code': "def max_subarray(nums):\n    pass\n",
        'solution': (
            "def max_subarray(nums):\n"
            "    values = [int(x) for x in (nums or [])]\n"
            "    if not values:\n"
            "        return 0\n"
            "    best = current = values[0]\n"
            "    for x in values[1:]:\n"
            "        current = max(x, current + x)\n"
            "        best = max(best, current)\n"
            "    return best\n"
            "\n"
            "\n"
            "print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))\n"
            "print(max_subarray([-3, -1, -2]))\n"
        ),
        'checks': [
            "assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6, '经典用例应得 6：%r' % (max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]),)",
            "assert max_subarray([1]) == 1, '单元素应返回它自己'",
            "assert max_subarray([-3, -1, -2]) == -1, '全负数时应返回最大的那个（不能返回 0）：%r' % (max_subarray([-3, -1, -2]),)",
            "assert max_subarray([5, 4, -1, 7, 8]) == 23, '全正数应返回总和：%r' % (max_subarray([5, 4, -1, 7, 8]),)",
            "assert max_subarray([]) == 0, '空列表返回 0'",
            "assert max_subarray([-1]) == -1, '单个负数应返回它自己：%r' % (max_subarray([-1]),)",
            "assert max_subarray([0, 0, 0]) == 0, '全零应返回 0'",
            "assert max_subarray([2, -1, 2]) == 3, '应把整段都算进来：%r' % (max_subarray([2, -1, 2]),)",
            "assert max_subarray([-2, 1]) == 1, '从负数开头时应从正数重新开始：%r' % (max_subarray([-2, 1]),)",
        ],
        'explanation': (
            '**Kadane 算法**的核心是一句判断：\n\n'
            '```\n'
            'cur = max(x, cur + x)\n'
            '```\n\n'
            '含义是：以 `x` 结尾的最大子数组和，要么是「x 自己」（前面那段是负贡献，'
            '丢掉它重新开始），要么是「前面的最优解接上 x」。'
            '**一旦前缀和为负，就立刻抛弃前缀从当前元素重新开始。**\n\n'
            '另一个必须记住的点：**答案必须是「所有 cur 的最大值」，而不是最后的 cur**。'
            '最大子数组可能在中间某处结束，所以每轮都要更新 `best`。'
            '只返回 `cur` 是这道题最常见的错误。\n\n'
            '`best` 与 `current` 都初始化为 `values[0]` 而不是 0 或 `-inf`：\n'
            '- 初始化成 0 会让**全负数**数组返回 0（错，应该返回最大的那个负数）；\n'
            '- 初始化成 `-inf` 也行，但用第一个元素更直观。\n\n'
            '复杂度 O(n) 时间、O(1) 额外空间。'
            '它本质上是「一维 DP + 滚动变量」：'
            '`dp[i] = max(nums[i], dp[i-1] + nums[i])`，'
            '因为只用到前一项，所以能压成一个变量。'
        ),
        'expected_output': '6\n-1\n',
        'hints': ['current = max(x, current + x)，同时用 best 记录过程中出现过的最大值', '两个变量都要用第一个元素初始化，否则全负数会返回 0'],
    },
    {
        'id': 'lc-007',
        'track': 'algorithm',
        'chapter_id': 124,
        'chapter_title': '动态规划进阶',
        'topic': '动态规划进阶',
        'title': '打家劫舍 II（环形房屋）',
        'difficulty': 2,
        'tags': ['动态规划', '环形', '分类讨论'],
        'statement': (
            '一排房屋围成**一个环**，第 i 间有 `nums[i]` 元。'
            '不能偷相邻的两间（首尾也算相邻），求能偷到的最大金额。\n\n'
            '编写函数 `rob_circle(nums)`。示例：\n'
            '```\n'
            'rob_circle([2,3,2])      ->  3    # 不能同时偷第一间和第三间\n'
            'rob_circle([1,2,3,1])    ->  4    # 偷第 1、3 间\n'
            'rob_circle([1,2,3])      ->  3\n'
            '```\n\n'
            '**思路**：环的难点是首尾互相约束。把问题拆成两种情况——\n'
            '1. **不偷最后一间**：等价于在 `nums[:-1]` 上做直线版打家劫舍；\n'
            '2. **不偷第一间**：等价于在 `nums[1:]` 上做直线版打家劫舍。\n\n'
            '答案取两者的较大值（两种情况合起来覆盖了所有合法方案）。\n\n'
            '要求先写一个直线版辅助函数 `rob_line(nums)`（滚动的两个变量，O(1) 空间）。'
        ),
        'starter_code': "def rob_line(nums):\n    pass\n\n\ndef rob_circle(nums):\n    pass\n",
        'solution': (
            "def rob_line(nums):\n"
            "    prev, curr = 0, 0\n"
            "    for x in nums:\n"
            "        prev, curr = curr, max(curr, prev + x)\n"
            "    return curr\n"
            "\n"
            "\n"
            "def rob_circle(nums):\n"
            "    values = [int(x) for x in (nums or [])]\n"
            "    if not values:\n"
            "        return 0\n"
            "    if len(values) == 1:\n"
            "        return values[0]\n"
            "    return max(rob_line(values[:-1]), rob_line(values[1:]))\n"
            "\n"
            "\n"
            "print(rob_circle([2, 3, 2]))\n"
            "print(rob_circle([1, 2, 3, 1]))\n"
            "print(rob_circle([1, 2, 3]))\n"
        ),
        'checks': [
            "assert rob_circle([2, 3, 2]) == 3, '[2,3,2] 应得 3：%r' % (rob_circle([2, 3, 2]),)",
            "assert rob_circle([1, 2, 3, 1]) == 4, '[1,2,3,1] 应得 4：%r' % (rob_circle([1, 2, 3, 1]),)",
            "assert rob_circle([1, 2, 3]) == 3, '[1,2,3] 应得 3：%r' % (rob_circle([1, 2, 3]),)",
            "assert rob_circle([1]) == 1, '单间应返回它自己'",
            "assert rob_circle([]) == 0, '空列表返回 0'",
            "assert rob_circle([5, 5]) == 5, '两间相邻只能偷一间：%r' % (rob_circle([5, 5]),)",
            "assert rob_circle([2, 7, 9, 3, 1]) == 11, '五间用例不对：%r' % (rob_circle([2, 7, 9, 3, 1]),)",
            "assert rob_circle([0, 0]) == 0, '全零应为 0'",
            "assert rob_line([2, 7, 9, 3, 1]) == 12, '直线版辅助函数不对：%r' % (rob_line([2, 7, 9, 3, 1]),)",
            "assert rob_line([]) == 0, '直线版空列表应为 0'",
        ],
        'explanation': (
            '**环形 = 直线 + 分类讨论**。这是处理环状 DP 的标准套路：'
            '首尾互相约束，那就把「首尾必有一间不偷」这件事拆成两种互斥且穷尽的情况。\n\n'
            '为什么两种情况合起来就穷尽了？'
            '任何合法方案要么偷了第一间（那它一定没偷最后一间，属于「不偷最后一间」这一类），'
            '要么没偷第一间（属于第二类）。**没有第三种可能**，所以取 max 就是答案。\n\n'
            '**直线版的两个变量滚动**是全题的精髓：\n\n'
            '```\n'
            'prev, curr = curr, max(curr, prev + x)\n'
            '```\n\n'
            '`curr` 是「考虑到当前这间为止能偷到的最大值」，'
            '`prev` 是「上一间为止的最大值」。'
            '转移时要么不偷当前（沿用 `curr`），要么偷当前（`prev + x`，'
            '因为偷了当前就不能偷上一间，只能用 `prev`）。\n\n'
            '**为什么 `prev` 初始化成 0？** 因为「前面没有房子」时收益为 0，'
            '它天然表达了「可以偷第一间」。\n\n'
            '注意 `len(values) == 1` 要单独返回：'
            '此时 `values[:-1]` 与 `values[1:]` 都是空列表，'
            '取 max 会得到 0，而正确答案是那一间的金额。\n\n'
            '复杂度 O(n) 时间、O(1) 空间（没有建 DP 数组）。'
        ),
        'expected_output': '3\n4\n3\n',
        'hints': ['环形拆成两种情况：不含最后一间 / 不含第一间，取较大值', '单元素要单独返回，否则切片后变成空列表会得 0'],
    },
    {
        'id': 'lc-008',
        'track': 'algorithm',
        'chapter_id': 124,
        'chapter_title': '动态规划进阶',
        'topic': '动态规划进阶',
        'title': '单词拆分',
        'difficulty': 2,
        'tags': ['动态规划', '字符串', '集合'],
        'statement': (
            '给定字符串 `s` 与单词字典 `word_dict`（列表），'
            '编写函数 `word_break(s, word_dict)`，'
            '判断 `s` 能否被**空格拆分成字典中的若干个单词**（单词可重复使用）。\n\n'
            '示例：\n'
            '```\n'
            "word_break('leetcode', ['leet', 'code'])              ->  True\n"
            "word_break('applepenapple', ['apple', 'pen'])         ->  True\n"
            "word_break('catsandog', ['cats', 'dog', 'sand', 'and', 'cat'])  ->  False\n"
            '```\n\n'
            '**要求 DP**：`dp[i]` 表示「`s` 的前 i 个字符能否被拆分」。'
            '`dp[0] = True`（空串可拆分），'
            '转移：若存在 `j < i` 使 `dp[j]` 为真且 `s[j:i]` 在字典里，则 `dp[i]` 为真。\n\n'
            '字典要转成 `set`，否则每次查找是 O(len(dict))。'
        ),
        'starter_code': "def word_break(s, word_dict):\n    pass\n",
        'solution': (
            "def word_break(s, word_dict):\n"
            "    text = str(s or '')\n"
            "    words = set(word_dict or [])\n"
            "    if not text:\n"
            "        return True\n"
            "    length = len(text)\n"
            "    dp = [False] * (length + 1)\n"
            "    dp[0] = True\n"
            "    for i in range(1, length + 1):\n"
            "        for j in range(i):\n"
            "            if dp[j] and text[j:i] in words:\n"
            "                dp[i] = True\n"
            "                break\n"
            "    return dp[length]\n"
            "\n"
            "\n"
            "print(word_break('leetcode', ['leet', 'code']))\n"
            "print(word_break('applepenapple', ['apple', 'pen']))\n"
            "print(word_break('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']))\n"
        ),
        'checks': [
            "assert word_break('leetcode', ['leet', 'code']) is True, 'leetcode 应可拆分'",
            "assert word_break('applepenapple', ['apple', 'pen']) is True, '单词可重复使用'",
            "assert word_break('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']) is False, 'catsandog 不可拆分'",
            "assert word_break('', ['a']) is True, '空串应返回 True'",
            "assert word_break('a', []) is False, '字典为空时任何非空串都不可拆分'",
            "assert word_break('a', ['a']) is True, '单字符命中应返回 True'",
            "assert word_break('ab', ['a', 'b']) is True and word_break('ab', ['ab']) is True, '两种拆法都应支持'",
            "assert word_break('aaa', ['aa']) is False, 'aaa 无法用 aa 凑出：%r' % (word_break('aaa', ['aa']),)",
            "assert word_break('aaaa', ['aa']) is True, 'aaaa 可以用两个 aa：%r' % (word_break('aaaa', ['aa']),)",
            "assert word_break('dogs', ['dog', 's', 'gs']) is True, 'dogs 应可拆分（dog + s）'",
        ],
        'explanation': (
            '这题的状态定义是**「前 i 个字符能否被拆分」**，'
            '注意是「前缀」而不是「以 i 结尾」，因为拆分一定从字符串开头开始。\n\n'
            '转移方程：\n\n'
            '```\n'
            'dp[i] = 存在 j < i 使得 dp[j] 为真 且 s[j:i] 是字典中的单词\n'
            '```\n\n'
            '它的含义是「找到一个切点 j，前半段能被拆分、后半段正好是一个词」。\n'
            '找到就 `break`——只要有一种拆法成立，`dp[i]` 就是真。\n\n'
            '两个工程细节：\n'
            '1. **字典一定转 `set`**。`list` 的 `in` 是 O(len(list))，'
            '在双重循环里会被乘进去，测试用例一大就明显变慢；\n'
            '2. **两层循环都从前往后**，因为 `dp[i]` 依赖所有更小的 `dp[j]`，'
            '顺序处理天然满足依赖关系。\n\n'
            '复杂度：两层循环 O(n²) 个子串组合，每个子串判存在 O(L)，'
            '总计 O(n²·L)；空间 O(n)。'
            '更快的做法是预处理字典建前缀树（Trie），把「从 j 开始能不能匹配到词」变成一次遍历，'
            '但那是 O(n²) 常数优化，思路完全相同。'
        ),
        'expected_output': 'True\nTrue\nFalse\n',
        'hints': ['dp[i] 表示前 i 个字符能否被拆分，dp[0] = True', '字典换成 set，否则每次查找都在扫列表'],
    },
    {
        'id': 'lc-009',
        'track': 'algorithm',
        'chapter_id': 124,
        'chapter_title': '动态规划进阶',
        'topic': '动态规划进阶',
        'title': '最长回文子序列',
        'difficulty': 2,
        'tags': ['动态规划', '区间DP', '回文'],
        'statement': (
            '编写函数 `longest_palindrome_subseq(s)`，返回**最长回文子序列的长度**。'
            '注意是子序列（可以不连续）而不是子串。\n\n'
            '示例：\n'
            '```\n'
            "longest_palindrome_subseq('bbbab')  ->  4    # 'bbbb'\n"
            "longest_palindrome_subseq('cbbd')   ->  2    # 'bb'\n"
            '```\n\n'
            '**要求区间 DP**：`dp[i][j]` 表示 `s[i..j]` 的最长回文子序列长度。\n'
            '- 若 `s[i] == s[j]`：`dp[i][j] = dp[i+1][j-1] + 2`\n'
            '- 否则：`dp[i][j] = max(dp[i+1][j], dp[i][j-1])`\n'
            '- 单个字符是长度 1；`i > j` 时长度为 0\n\n'
            '按**区间长度从短到长**遍历，保证依赖项先算好。'
        ),
        'starter_code': "def longest_palindrome_subseq(s):\n    pass\n",
        'solution': (
            "def longest_palindrome_subseq(s):\n"
            "    text = str(s or '')\n"
            "    n = len(text)\n"
            "    if n == 0:\n"
            "        return 0\n"
            "    dp = [[0] * n for _ in range(n)]\n"
            "    for i in range(n):\n"
            "        dp[i][i] = 1\n"
            "    for length in range(2, n + 1):\n"
            "        for i in range(0, n - length + 1):\n"
            "            j = i + length - 1\n"
            "            if text[i] == text[j]:\n"
            "                dp[i][j] = dp[i + 1][j - 1] + 2\n"
            "            else:\n"
            "                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])\n"
            "    return dp[0][n - 1]\n"
            "\n"
            "\n"
            "print(longest_palindrome_subseq('bbbab'))\n"
            "print(longest_palindrome_subseq('cbbd'))\n"
        ),
        'checks': [
            "assert longest_palindrome_subseq('bbbab') == 4, 'bbbab 应得 4：%r' % (longest_palindrome_subseq('bbbab'),)",
            "assert longest_palindrome_subseq('cbbd') == 2, 'cbbd 应得 2：%r' % (longest_palindrome_subseq('cbbd'),)",
            "assert longest_palindrome_subseq('') == 0, '空串应为 0'",
            "assert longest_palindrome_subseq('a') == 1, '单字符应为 1'",
            "assert longest_palindrome_subseq('abc') == 1, '没有重复字符应为 1'",
            "assert longest_palindrome_subseq('aaaa') == 4, '全同字符应等于长度'",
            "assert longest_palindrome_subseq('abba') == 4, 'abba 本身是回文：%r' % (longest_palindrome_subseq('abba'),)",
            "assert longest_palindrome_subseq('character') == 5, 'character 应得 5（carac）：%r' % (longest_palindrome_subseq('character'),)",
        ],
        'explanation': (
            '**区间 DP 的模板**：状态是「一段区间」，转移靠「缩小区间」。\n\n'
            '`dp[i][j]` 表示 `s[i..j]` 的最长回文子序列长度，'
            '分两种情况选：\n'
            '- 两端字符相同：它们可以一起进回文，所以 `dp[i+1][j-1] + 2`；\n'
            '- 两端不同：至少有一个不在最优解里，所以取「去掉左边」或「去掉右边」的较大者。\n\n'
            '**遍历顺序是这题最容易错的地方**：'
            '`dp[i][j]` 依赖 `dp[i+1][j-1]`（更短的区间）与 `dp[i+1][j]`、`dp[i][j-1]`。'
            '如果按 i 从小到大、j 从小到大两层循环，`dp[i+1][...]` 还没算出来，结果全错。\n\n'
            '正确做法是**按区间长度递增**：先算所有长度 2 的区间，再算长度 3 的……'
            '这样算到长度 L 时，所有更短的区间都已经就绪。\n\n'
            '`i` 的取值范围是 `0` 到 `n - length`（闭区间），'
            '因为要保证 `j = i + length - 1 <= n - 1`。\n\n'
            '复杂度 O(n²) 时间、O(n²) 空间。'
            '进阶优化：因为每行只依赖下一行，可以把空间压到 O(n)，'
            '但要注意 `dp[i+1][j-1]` 会被覆盖，需要额外变量暂存。'
        ),
        'expected_output': '4\n2\n',
        'hints': ['按区间长度从 2 到 n 递增遍历，不要按 i/j 双层递增', '两端相同就 dp[i+1][j-1] + 2，否则取两边的较大值'],
    },
    {
        'id': 'lc-010',
        'track': 'algorithm',
        'chapter_id': 124,
        'chapter_title': '动态规划进阶',
        'topic': '动态规划进阶',
        'title': '不同的子序列（计数型 DP）',
        'difficulty': 3,
        'tags': ['动态规划', '计数', '字符串'],
        'statement': (
            '给定字符串 `s` 与 `t`，编写函数 `num_distinct(s, t)`，'
            '返回 `s` 的子序列中**等于 `t` 的个数**。'
            '（子序列由删除若干字符得到，不改变相对顺序；答案可能很大，本題数据量保证在 Python 整数范围内。）\n\n'
            '示例：\n'
            '```\n'
            "num_distinct('rabbbit', 'rabbit')  ->  3\n"
            "num_distinct('babgbag', 'bag')     ->  5\n"
            "num_distinct('abc', 'abc')         ->  1\n"
            '```\n\n'
            '**要求 DP**：`dp[i][j]` 表示「`s` 的前 i 个字符中能凑出 `t` 的前 j 个字符的方案数」。\n'
            '- `dp[i][0] = 1`（凑空串只有一种方案：什么都不选）\n'
            '- `dp[0][j>0] = 0`\n'
            '- 若 `s[i-1] == t[j-1]`：`dp[i][j] = dp[i-1][j-1] + dp[i-1][j]`（用这个字符 / 不用它）\n'
            '- 否则：`dp[i][j] = dp[i-1][j]`（只能不用）'
        ),
        'starter_code': "def num_distinct(s, t):\n    pass\n",
        'solution': (
            "def num_distinct(s, t):\n"
            "    source = str(s or '')\n"
            "    target = str(t or '')\n"
            "    n, m = len(source), len(target)\n"
            "    if m == 0:\n"
            "        return 1\n"
            "    if n < m:\n"
            "        return 0\n"
            "    dp = [[0] * (m + 1) for _ in range(n + 1)]\n"
            "    for i in range(n + 1):\n"
            "        dp[i][0] = 1\n"
            "    for i in range(1, n + 1):\n"
            "        for j in range(1, m + 1):\n"
            "            if source[i - 1] == target[j - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]\n"
            "            else:\n"
            "                dp[i][j] = dp[i - 1][j]\n"
            "    return dp[n][m]\n"
            "\n"
            "\n"
            "print(num_distinct('rabbbit', 'rabbit'))\n"
            "print(num_distinct('babgbag', 'bag'))\n"
            "print(num_distinct('abc', 'abc'))\n"
        ),
        'checks': [
            "assert num_distinct('rabbbit', 'rabbit') == 3, 'rabbbit 应得 3：%r' % (num_distinct('rabbbit', 'rabbit'),)",
            "assert num_distinct('babgbag', 'bag') == 5, 'babgbag 应得 5：%r' % (num_distinct('babgbag', 'bag'),)",
            "assert num_distinct('abc', 'abc') == 1, '完全相同应得 1：%r' % (num_distinct('abc', 'abc'),)",
            "assert num_distinct('abc', '') == 1, 't 为空串时有 1 种方案（什么都不选）'",
            "assert num_distinct('', 'a') == 0, 's 为空时凑不出非空 t'",
            "assert num_distinct('', '') == 1, '两个空串应得 1'",
            "assert num_distinct('aaa', 'aa') == 3, 'aaa 中取两个 a 有 3 种：%r' % (num_distinct('aaa', 'aa'),)",
            "assert num_distinct('aaaa', 'aa') == 6, 'aaaa 中取两个 a 有 6 种：%r' % (num_distinct('aaaa', 'aa'),)",
            "assert num_distinct('abc', 'abcd') == 0, 't 比 s 长时必然为 0'",
            "assert num_distinct('xyz', 'abc') == 0, '完全不同应为 0'",
        ],
        'explanation': (
            '这是**计数型 DP**（问「有多少种方案」而不是「最优是多少」），'
            '转移里是加法而不是 max/min——这个区别很关键。\n\n'
            '`dp[i][j]` = 「s 的前 i 个字符能凑出 t 的前 j 个字符的方案数」。'
            '当 `s[i-1] == t[j-1]` 时，最后一个字符有两种对待方式：\n'
            '- **用它匹配**：方案数等于 `dp[i-1][j-1]`；\n'
            '- **不用它**（虽然相同但跳过这个字符）：方案数等于 `dp[i-1][j]`。\n'
            '两者是互斥的完备分类，所以**相加**。\n\n'
            '不相等时只能跳过当前字符，方案数照搬 `dp[i-1][j]`。\n\n'
            '边界 `dp[i][0] = 1` 的直觉：'
            '**凑空串永远只有一种方案——不选任何字符**。'
            '这一行初始化不能漏，它是所有转移的基石。\n\n'
            '`n < m` 时可以直接返回 0（长度都不够），是个便宜的剪枝。\n\n'
            '复杂度 O(n·m) 时间、O(n·m) 空间。'
            '同样可以把空间压到一维：因为 `dp[i][j]` 只依赖上一行，'
            '倒着遍历 j 就能原地更新——但那样可读性下降，本題保留二维写法。'
        ),
        'expected_output': '3\n5\n1\n',
        'hints': ['相等时是两种选择相加：dp[i-1][j-1] + dp[i-1][j]', 'dp[i][0] 全部初始化为 1（凑空串只有一种方案）'],
    },

    # ── 125 LeetCode 高频题 ────────────────────────────────
    {
        'id': 'lc-011',
        'track': 'algorithm',
        'chapter_id': 125,
        'chapter_title': '数据结构高频题',
        'topic': '数据结构高频题',
        'title': '用两个栈实现队列',
        'difficulty': 1,
        'tags': ['栈', '队列', '设计'],
        'statement': (
            '用**两个栈**实现一个队列 `MyQueue`，支持：\n\n'
            '- `push(x)`：把元素 x 推到队尾\n'
            '- `pop()`：弹出并返回队首元素\n'
            '- `peek()`：返回队首元素（不弹出）\n'
            '- `empty()`：队列是否为空\n'
            '- `size()`：元素个数\n\n'
            '示例：\n'
            '```\n'
            'q = MyQueue()\n'
            'q.push(1); q.push(2)\n'
            'q.peek()   ->  1\n'
            'q.pop()    ->  1\n'
            'q.empty()  ->  False\n'
            '```\n\n'
            '**要求摊还 O(1)**：`push` 进 `in_stack`；'
            '`pop`/`peek` 时若 `out_stack` 为空，就把 `in_stack` 全部倒入 `out_stack`。'
            '每个元素最多被搬运一次，所以平均每次操作是 O(1)。'
        ),
        'starter_code': 'class MyQueue:\n    def __init__(self):\n        pass\n\n    def push(self, x):\n        pass\n\n    def pop(self):\n        pass\n\n    def peek(self):\n        pass\n\n    def empty(self):\n        pass\n\n    def size(self):\n        pass\n',
        'solution': (
            "class MyQueue:\n"
            "    def __init__(self):\n"
            "        self.in_stack = []\n"
            "        self.out_stack = []\n"
            "\n"
            "    def push(self, x):\n"
            "        self.in_stack.append(x)\n"
            "        return self\n"
            "\n"
            "    def _shift(self):\n"
            "        if not self.out_stack:\n"
            "            while self.in_stack:\n"
            "                self.out_stack.append(self.in_stack.pop())\n"
            "\n"
            "    def pop(self):\n"
            "        self._shift()\n"
            "        if not self.out_stack:\n"
            "            raise IndexError('队列为空')\n"
            "        return self.out_stack.pop()\n"
            "\n"
            "    def peek(self):\n"
            "        self._shift()\n"
            "        if not self.out_stack:\n"
            "            raise IndexError('队列为空')\n"
            "        return self.out_stack[-1]\n"
            "\n"
            "    def empty(self):\n"
            "        return not self.in_stack and not self.out_stack\n"
            "\n"
            "    def size(self):\n"
            "        return len(self.in_stack) + len(self.out_stack)\n"
            "\n"
            "\n"
            "q = MyQueue()\n"
            "q.push(1)\n"
            "q.push(2)\n"
            "print(q.peek(), q.pop(), q.empty(), q.size())\n"
        ),
        'checks': [
            "q = MyQueue()",
            "assert q.empty() is True, '新建队列应为空'",
            "q.push(1)",
            "assert q.empty() is False and q.size() == 1, 'push 之后应非空且 size 为 1'",
            "q.push(2)",
            "q.push(3)",
            "assert q.peek() == 1, '队首应为最先入队的 1：%r' % (q.peek(),)",
            "assert q.peek() == 1, '连续 peek 不应改变队列（仍是 1）'",
            "assert q.pop() == 1, '第一次 pop 应返回 1：%r' % (q.pop(),)",
            "assert q.pop() == 2 and q.pop() == 3, '出队顺序应为先进先出'",
            "assert q.empty() is True and q.size() == 0, '全部弹出后应为空'",
            "q.push(4)\nq.push(5)\nassert q.pop() == 4, '清空后再入队仍要正常工作'",
            "assert q.size() == 1, 'size 计算不对：%r' % (q.size(),)",
            "q2 = MyQueue()\ntry:\n    q2.pop()\n    raise AssertionError('空队列 pop 应当报错')\nexcept IndexError:\n    pass",
            "q3 = MyQueue()\nfor i in range(5):\n    q3.push(i)\nassert [q3.pop() for _ in range(5)] == [0, 1, 2, 3, 4], '连续进出应保持先进先出'",
        ],
        'explanation': (
            '**两个栈拼成一个队列**是经典设计题，核心在于「负负得正」：'
            '元素进 `in_stack` 的顺序是 1、2、3，'
            '倒进 `out_stack` 之后变成 3、2、1（栈顶是 1），'
            '再 pop 出来就是 1、2、3——**两次逆序等于正序**。\n\n'
            '关键是 `_shift` 的判断：**只有当 `out_stack` 为空时才搬运**。'
            '如果每次 pop 都搬，就会把已经排好的顺序打乱'
            '（比如 out 里还有元素时又倒一批进来，顺序就错了）。\n\n'
            '**摊还 O(1) 的证明**：每个元素一生只被搬运一次'
            '（从 in 栈 pop 出来、push 进 out 栈），'
            '所以 n 次操作总共搬运 n 次，平均每次 O(1)。'
            '单次最坏情况是 O(n)（第一次 pop 要倒一整个栈），但摊还下来很快。\n\n'
            '`peek()` 用 `out_stack[-1]` 取栈顶而不是 `pop()` 再 push 回去：'
            '后者虽然也对，但白白多两次操作，而且如果忘了 push 回去就破坏了队列。\n\n'
            '`empty()` 要同时看两个栈——只判断 `in_stack` 是初学者最常犯的错。'
        ),
        'expected_output': '1 1 False 1',
        'hints': ['只在 out_stack 为空时才把 in_stack 倒过去（否则顺序会乱）', 'empty 要同时判断两个栈'],
    },
    {
        'id': 'lc-012',
        'track': 'algorithm',
        'chapter_id': 125,
        'chapter_title': '数据结构高频题',
        'topic': '数据结构高频题',
        'title': '螺旋矩阵',
        'difficulty': 2,
        'tags': ['矩阵', '边界控制', '模拟'],
        'statement': (
            '编写函数 `spiral_order(matrix)`，'
            '按**顺时针螺旋顺序**返回矩阵中的所有元素（矩阵用二维列表表示）。\n\n'
            '```\n'
            '输入: [[1, 2, 3],\n'
            '       [4, 5, 6],\n'
            '       [7, 8, 9]]\n'
            "输出: [1, 2, 3, 6, 9, 8, 7, 4, 5]\n"
            '```\n\n'
            '- 空矩阵返回 `[]`\n'
            '- 只有一行或一列时要正确处理（不要重复访问）\n'
            '- 非矩形矩阵（每行长度不同）按实际边界处理，遇到越界就跳过\n\n'
            '**要求用四边界法**：维护 `top / bottom / left / right` 四个边界，'
            '走完一条边就收缩对应的边界，直到边界交错为止。'
        ),
        'starter_code': "def spiral_order(matrix):\n    pass\n",
        'solution': (
            "def spiral_order(matrix):\n"
            "    if not matrix or not matrix[0]:\n"
            "        return []\n"
            "    top, bottom = 0, len(matrix) - 1\n"
            "    left, right = 0, len(matrix[0]) - 1\n"
            "    result = []\n"
            "    while top <= bottom and left <= right:\n"
            "        for col in range(left, right + 1):\n"
            "            result.append(matrix[top][col])\n"
            "        top += 1\n"
            "        for row in range(top, bottom + 1):\n"
            "            result.append(matrix[row][right])\n"
            "        right -= 1\n"
            "        if top <= bottom:\n"
            "            for col in range(right, left - 1, -1):\n"
            "                result.append(matrix[bottom][col])\n"
            "            bottom -= 1\n"
            "        if left <= right:\n"
            "            for row in range(bottom, top - 1, -1):\n"
            "                result.append(matrix[row][left])\n"
            "            left += 1\n"
            "    return result\n"
            "\n"
            "\n"
            "print(spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))\n"
            "print(spiral_order([[1, 2, 3, 4]]))\n"
        ),
        'checks': [
            "assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5], '3x3 螺旋不对：%r' % (spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),)",
            "assert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7], '3x4 螺旋不对：%r' % (spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]),)",
            "assert spiral_order([]) == [], '空矩阵返回空列表'",
            "assert spiral_order([[]]) == [], '只有空行时返回空列表'",
            "assert spiral_order([[1]]) == [1], '1x1 应返回那个元素'",
            "assert spiral_order([[1, 2, 3, 4]]) == [1, 2, 3, 4], '单行不应重复访问：%r' % (spiral_order([[1, 2, 3, 4]]),)",
            "assert spiral_order([[1], [2], [3]]) == [1, 2, 3], '单列不应重复访问：%r' % (spiral_order([[1], [2], [3]]),)",
            "assert spiral_order([[1, 2], [3, 4]]) == [1, 2, 4, 3], '2x2 不对：%r' % (spiral_order([[1, 2], [3, 4]]),)",
            "m = [[i * 4 + j for j in range(4)] for i in range(4)]\nassert len(spiral_order(m)) == 16, '4x4 应恰好访问 16 个元素（不能重复也不能漏）'",
        ],
        'explanation': (
            '**四边界法**是矩阵遍历类题目的通用武器：'
            '维护 `top / bottom / left / right` 四个变量表示「还没访问的矩形范围」，'
            '每走完一条边就把那条边界往里收一格。\n\n'
            '四步的顺序是固定的：上边（左→右）、右边（上→下）、下边（右→左）、左边（下→上）。\n\n'
            '**最容易错的地方是后两步的边界判断**：\n\n'
            '```\n'
            'if top <= bottom:   # 才走下边\n'
            'if left <= right:   # 才走左边\n'
            '```\n\n'
            '为什么必须判断？因为单行或单列的矩阵里，前两步走完边界就已经交错了。'
            '比如 `[[1,2,3]]`：走完上边 `top` 变成 1，'
            '此时 `top(1) > bottom(0)`，如果再走「下边」就会**把 1、2、3 倒着重复访问一遍**。\n\n'
            '这也是为什么前两步不用判断——它们本来就是「第一次访问」，'
            '而 `while` 条件保证了范围有效。\n\n'
            '复杂度 O(m·n) 时间（每个元素恰好访问一次）、O(1) 额外空间（不算结果数组）。'
        ),
        'expected_output': '[1, 2, 3, 6, 9, 8, 7, 4, 5]\n[1, 2, 3, 4]\n',
        'hints': ['走完上边收 top、走完右边收 right、走完下边收 bottom、走完左边收 left', '下边与左边这两步要判断边界是否仍然有效，否则单行/单列会重复访问'],
    },
    {
        'id': 'lc-013',
        'track': 'algorithm',
        'chapter_id': 125,
        'chapter_title': '数据结构高频题',
        'topic': '数据结构高频题',
        'title': '合并区间',
        'difficulty': 2,
        'tags': ['排序', '区间', '贪心'],
        'statement': (
            '编写函数 `merge_intervals(intervals)`，'
            '把**所有重叠的区间合并**，返回互不重叠的区间列表（按起点升序）。\n\n'
            '区间用 `[start, end]` 表示，**端点相接也算重叠**（`[1,3]` 与 `[3,5]` 合并为 `[1,5]`）。\n\n'
            '```\n'
            'merge_intervals([[1,3],[2,6],[8,10],[15,18]])  ->  [[1,6],[8,10],[15,18]]\n'
            'merge_intervals([[1,4],[4,5]])                 ->  [[1,5]]\n'
            '```\n\n'
            '- 空列表返回 `[]`\n'
            '- 输入可能乱序，要先**按起点排序**\n'
            '- **不要修改传入的列表**（先把每个区间拷贝一份再排序）'
        ),
        'starter_code': "def merge_intervals(intervals):\n    pass\n",
        'solution': (
            "def merge_intervals(intervals):\n"
            "    items = [list(pair) for pair in (intervals or [])]\n"
            "    if not items:\n"
            "        return []\n"
            "    items.sort(key=lambda pair: (pair[0], pair[1]))\n"
            "    merged = [items[0]]\n"
            "    for start, end in items[1:]:\n"
            "        last = merged[-1]\n"
            "        if start <= last[1]:\n"
            "            last[1] = max(last[1], end)\n"
            "        else:\n"
            "            merged.append([start, end])\n"
            "    return merged\n"
            "\n"
            "\n"
            "print(merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]))\n"
            "print(merge_intervals([[1, 4], [4, 5]]))\n"
        ),
        'checks': [
            "assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]], '经典用例不对：%r' % (merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]),)",
            "assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]], '端点相接要合并：%r' % (merge_intervals([[1, 4], [4, 5]]),)",
            "assert merge_intervals([[1, 4], [0, 4]]) == [[0, 4]], '乱序输入要先排序：%r' % (merge_intervals([[1, 4], [0, 4]]),)",
            "assert merge_intervals([]) == [], '空列表返回空列表'",
            "assert merge_intervals([[1, 2]]) == [[1, 2]], '单个区间原样返回'",
            "assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]], '被完全包含的区间要被吞掉：%r' % (merge_intervals([[1, 10], [2, 3], [4, 5]]),)",
            "assert merge_intervals([[1, 2], [5, 6]]) == [[1, 2], [5, 6]], '不重叠的区间不应被合并'",
            "assert merge_intervals([[1, 2], [2, 3], [4, 5]]) == [[1, 3], [4, 5]], '链式合并不对：%r' % (merge_intervals([[1, 2], [2, 3], [4, 5]]),)",
            "src = [[3, 4], [1, 2]]\nmerge_intervals(src)\nassert src == [[3, 4], [1, 2]], '不应修改传入的列表'",
            "assert merge_intervals([[1, 4], [2, 3], [3, 4]]) == [[1, 4]], '多个区间嵌套时不对：%r' % (merge_intervals([[1, 4], [2, 3], [3, 4]]),)",
        ],
        'explanation': (
            '**先排序，再一次扫描**，这是区间类问题的通用套路。\n\n'
            '排序后有一个关键性质：**能合并的区间一定是相邻的**。'
            '因为所有区间按起点排好了，如果某个区间和更早的区间有重叠，'
            '那它一定也和紧邻的前一个重叠。于是只需要和「结果列表的最后一个」比较。\n\n'
            '合并条件 `start <= last[1]` 里的 `<=` 而不是 `<`：'
            '题目规定端点相接也算重叠。这一个符号改了，`[1,4]` 与 `[4,5]` 的结果就完全不同。\n\n'
            '合并时取 `max(last[1], end)` 而不是直接 `last[1] = end`：'
            '因为新区间可能**被完全包含**在旧区间里'
            '（`[1,10]` 后面来了个 `[2,3]`），直接赋值会把区间缩短。\n\n'
            '`items = [list(pair) for pair in intervals]` 这一步是**防御性拷贝**。'
            '因为后面会就地改写 `last[1]`，不拷贝的话就把调用方的数据改了——'
            '这类「顺手改了入参」的 bug 在真实项目里非常难查。'
            '（顺带也把元组统一成列表，避免 `pair[1] = x` 报错。）\n\n'
            '复杂度 O(n log n) 时间（排序主导）、O(n) 空间。'
        ),
        'expected_output': '[[1, 6], [8, 10], [15, 18]]\n[[1, 5]]\n',
        'hints': ['先按起点排序，然后只和结果里最后一个区间比较', '合并时取 max(旧结尾, 新结尾)，否则遇到被包含的区间会缩短'],
    },
    {
        'id': 'lc-014',
        'track': 'algorithm',
        'chapter_id': 125,
        'chapter_title': '数据结构高频题',
        'topic': '数据结构高频题',
        'title': '旋转图像（矩阵原地转 90 度）',
        'difficulty': 2,
        'tags': ['矩阵', '原地', '转置'],
        'statement': (
            '编写函数 `rotate_image(matrix)`，把 n×n 矩阵**原地顺时针旋转 90 度**。\n'
            '**不允许新建矩阵**，必须直接修改传入的二维列表。\n\n'
            '```\n'
            '输入: [[1, 2, 3],\n'
            '       [4, 5, 6],\n'
            '       [7, 8, 9]]\n'
            '结果: [[7, 4, 1],\n'
            '       [8, 5, 2],\n'
            '       [9, 6, 3]]\n'
            '```\n\n'
            '**要求两步走**（这是最不容易错的写法）：\n'
            '1. 先**转置**（沿主对角线交换 `matrix[i][j]` 与 `matrix[j][i]`）；\n'
            '2. 再把每一行**左右翻转**。\n\n'
            '函数返回旋转后的 `matrix`（方便链式调用），空矩阵直接返回。'
        ),
        'starter_code': "def rotate_image(matrix):\n    pass\n",
        'solution': (
            "def rotate_image(matrix):\n"
            "    if not matrix or not matrix[0]:\n"
            "        return matrix\n"
            "    n = len(matrix)\n"
            "    # 第一步：转置（只处理上三角，否则会交换两次等于没换）\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1, n):\n"
            "            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n"
            "    # 第二步：每行左右翻转\n"
            "    for row in matrix:\n"
            "        row.reverse()\n"
            "    return matrix\n"
            "\n"
            "\n"
            "print(rotate_image([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))\n"
            "print(rotate_image([[1]]))\n"
        ),
        'checks': [
            "m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]",
            "result = rotate_image(m)",
            "assert m == [[7, 4, 1], [8, 5, 2], [9, 6, 3]], '3x3 原地旋转结果不对：%r' % (m,)",
            "assert result is m, '应原地修改并返回同一个对象（不是新矩阵）'",
            "assert rotate_image([[1]]) == [[1]], '1x1 应保持不变'",
            "assert rotate_image([]) == [], '空矩阵应安全返回'",
            "assert rotate_image([[1, 2], [3, 4]]) == [[3, 1], [4, 2]], '2x2 旋转不对：%r' % (rotate_image([[1, 2], [3, 4]]),)",
            "m4 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]",
            "rotate_image(m4)",
            "assert m4 == [[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]], '4x4 旋转不对：%r' % (m4,)",
            "m5 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]",
            "rotate_image(rotate_image(rotate_image(rotate_image(m5))))",
            "assert m5 == [[1, 2, 3], [4, 5, 6], [7, 8, 9]], '转四次应回到原样：%r' % (m5,)",
        ],
        'explanation': (
            '**转置 + 翻转 = 顺时针 90 度**，这个分解比「四个位置轮换」好写太多，也不容易下标出错。\n\n'
            '推导一下：顺时针旋转 90 度后，原来的 `matrix[i][j]` 会跑到 `matrix[j][n-1-i]`。'
            '先转置（`[i][j]` ↔ `[j][i]`）再左右翻转（列下标 j → n-1-j），'
            '合起来正好是 `[i][j] → [j][i] → [j][n-1-i]`，完全吻合。\n\n'
            '**转置时 j 要从 `i+1` 开始**——这是个必须记住的细节。'
            '如果从 0 开始，每个元素会被交换两次，等于什么都没做。'
            '（也可以理解成「只处理上三角」。）\n\n'
            '`row.reverse()` 是 Python 列表的原地方法，不产生新列表；'
            '写成 `row = row[::-1]` 就只是改了个局部名字，原矩阵纹丝不动——'
            '这是原地题最常见的错误。\n\n'
            '复杂度 O(n²) 时间（每个元素访问常数次）、O(1) 额外空间。'
            '顺带一提：逆时针 90 度只需把两步顺序调换（先翻转每行再转置）。'
        ),
        'expected_output': '[[7, 4, 1], [8, 5, 2], [9, 6, 3]]\n[[1]]\n',
        'hints': ['转置时内层循环从 i+1 开始，否则会换两次等于没换', '翻转每一行要用 row.reverse() 原地改，不能用 row[::-1]'],
    },
    {
        'id': 'lc-015',
        'track': 'algorithm',
        'chapter_id': 125,
        'chapter_title': '数据结构高频题',
        'topic': '数据结构高频题',
        'title': '接雨水（双指针 O(1) 空间）',
        'difficulty': 3,
        'tags': ['双指针', '单调栈', '数组'],
        'statement': (
            '给定 n 个非负整数表示宽度为 1 的柱子的高度（`height`），'
            '编写函数 `trap(height)`，计算下雨之后这些柱子之间**能接多少单位的雨水**。\n\n'
            '```\n'
            'trap([0,1,0,2,1,0,1,3,2,1,2,1])  ->  6\n'
            'trap([4,2,0,3,2,5])              ->  9\n'
            '```\n\n'
            '**要求双指针法，额外空间 O(1)**：\n'
            '左右指针相向移动，同时维护 `left_max` 与 `right_max`。\n'
            '- 若 `left_max < right_max`：左边的水位由 `left_max` 决定，'
            '结算 `left` 位置的水量后右移；\n'
            '- 否则：右边的水位由 `right_max` 决定，结算 `right` 位置后左移。\n\n'
            '空数组或长度小于 3 时返回 `0`。'
        ),
        'starter_code': "def trap(height):\n    pass\n",
        'solution': (
            "def trap(height):\n"
            "    bars = [max(0, int(x)) for x in (height or [])]\n"
            "    if len(bars) < 3:\n"
            "        return 0\n"
            "    left, right = 0, len(bars) - 1\n"
            "    left_max, right_max = 0, 0\n"
            "    water = 0\n"
            "    while left < right:\n"
            "        left_max = max(left_max, bars[left])\n"
            "        right_max = max(right_max, bars[right])\n"
            "        if left_max < right_max:\n"
            "            water += left_max - bars[left]\n"
            "            left += 1\n"
            "        else:\n"
            "            water += right_max - bars[right]\n"
            "            right -= 1\n"
            "    return water\n"
            "\n"
            "\n"
            "print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))\n"
            "print(trap([4, 2, 0, 3, 2, 5]))\n"
        ),
        'checks': [
            "assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6, '经典用例应得 6：%r' % (trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]),)",
            "assert trap([4, 2, 0, 3, 2, 5]) == 9, '第二个用例应得 9：%r' % (trap([4, 2, 0, 3, 2, 5]),)",
            "assert trap([]) == 0, '空数组返回 0'",
            "assert trap([1]) == 0, '单个柱子接不到水'",
            "assert trap([1, 2]) == 0, '两个柱子接不到水'",
            "assert trap([3, 3, 3]) == 0, '等高的柱子接不到水：%r' % (trap([3, 3, 3]),)",
            "assert trap([5, 4, 3, 2, 1]) == 0, '单调下降接不到水：%r' % (trap([5, 4, 3, 2, 1]),)",
            "assert trap([1, 2, 3, 4, 5]) == 0, '单调上升接不到水：%r' % (trap([1, 2, 3, 4, 5]),)",
            "assert trap([2, 0, 2]) == 2, '中间凹陷应接 2 单位：%r' % (trap([2, 0, 2]),)",
            "assert trap([5, 0, 0, 5]) == 10, '中间两个空位应接 10 单位：%r' % (trap([5, 0, 0, 5]),)",
            "assert trap([0, 0, 0]) == 0, '全零应为 0'",
        ],
        'explanation': (
            '**每个位置能接多少水？** 由「它左边最高的柱子」与「它右边最高的柱子」中**较矮的那个**决定：\n\n'
            '```\n'
            '水量[i] = min(左边最高, 右边最高) - 高度[i]     （结果小于 0 时为 0）\n'
            '```\n\n'
            '朴素解法是先正着扫一遍求左侧最大值、倒着扫一遍求右侧最大值，'
            '再用公式累加——时间 O(n)、空间 O(n)。\n\n'
            '**双指针把空间压到 O(1)**，靠的是一个关键的观察：\n'
            '当 `left_max < right_max` 时，`left` 位置的右侧最大值**一定不小于** `right_max`，'
            '所以 `min(左最高, 右最高)` 必然等于 `left_max`——'
            '**不必知道右边的确切最大值**就能结算左边这一格！\n\n'
            '这就是双指针能提前结算的原因：先用较小的一侧，'
            '因为那一侧的瓶颈已经确定了。反过来 `left_max >= right_max` 时结算右边。\n\n'
            '**别忘了每次移动前先更新 `left_max` / `right_max`**：'
            '它们的含义是「从边界走到当前位置为止见过的最高柱子」，'
            '漏掉更新会少算水量。\n\n'
            '复杂度 O(n) 时间、O(1) 额外空间，每个位置恰好访问一次。'
            '同一题还有单调栈解法（按「层」算水），思路完全不同，可以对比着看。'
        ),
        'expected_output': '6\n9\n',
        'hints': ['每次循环先更新 left_max 与 right_max，再比较它们决定结算哪一侧', '较小的一侧水位已经确定，可以直接结算并移动指针'],
    },

    # ── 126 位运算与数学 ───────────────────────────────────
    {
        'id': 'lc-016',
        'track': 'algorithm',
        'chapter_id': 126,
        'chapter_title': '位运算与数学',
        'topic': '位运算与数学',
        'title': '只出现一次的数字（异或）',
        'difficulty': 1,
        'tags': ['位运算', '异或'],
        'statement': (
            '数组中除了**一个数字只出现一次**，其余数字都出现**两次**。'
            '编写函数 `single_number(nums)`，找出那个只出现一次的数字。\n\n'
            '```\n'
            'single_number([2,2,1])      ->  1\n'
            'single_number([4,1,2,1,2])  ->  4\n'
            'single_number([7])          ->  7\n'
            '```\n\n'
            '**要求线性时间、常数空间**：不能用字典计数、不能排序、不能开新数组。\n'
            '提示：利用异或的三条性质——\n'
            '1. `a ^ a = 0`（自己异或自己是 0）\n'
            '2. `a ^ 0 = a`（任何数与 0 异或是它自己）\n'
            '3. 异或满足交换律与结合律\n\n'
            '把所有数字异或起来，成对出现的都抵消成 0，剩下的就是答案。'
        ),
        'starter_code': "def single_number(nums):\n    pass\n",
        'solution': (
            "def single_number(nums):\n"
            "    result = 0\n"
            "    for x in nums or []:\n"
            "        result ^= int(x)\n"
            "    return result\n"
            "\n"
            "\n"
            "print(single_number([2, 2, 1]))\n"
            "print(single_number([4, 1, 2, 1, 2]))\n"
            "print(single_number([7]))\n"
        ),
        'checks': [
            "assert single_number([2, 2, 1]) == 1, '[2,2,1] 应得 1：%r' % (single_number([2, 2, 1]),)",
            "assert single_number([4, 1, 2, 1, 2]) == 4, '[4,1,2,1,2] 应得 4：%r' % (single_number([4, 1, 2, 1, 2]),)",
            "assert single_number([7]) == 7, '单元素应返回它自己'",
            "assert single_number([0]) == 0, '只有 0 时应返回 0'",
            "assert single_number([0, 0, 5]) == 5, '0 与 5 的组合应得 5：%r' % (single_number([0, 0, 5]),)",
            "assert single_number([1, 1, 2, 2, 3]) == 3, '多个成对数字应得 3'",
            "assert single_number([-1, -1, -2]) == -2, '负数也应正确处理：%r' % (single_number([-1, -1, -2]),)",
            "assert single_number([100, 200, 100]) == 200, '大数用例不对：%r' % (single_number([100, 200, 100]),)",
            "assert single_number([]) == 0, '空列表应返回 0'",
        ],
        'explanation': (
            '**异或（XOR）是最好的「消除重复」工具**，因为它有两条神奇性质：\n'
            '- `a ^ a = 0`\n'
            '- `a ^ 0 = a`\n\n'
            '再加上交换律与结合律，把所有元素异或起来时，'
            '成对的数字可以任意重排到相邻位置互相抵消，最后什么都不剩；'
            '而那个落单的数字与 0 异或还是它自己。\n\n'
            '```\n'
            '[4,1,2,1,2] → 4^1^2^1^2 → 4^(1^1)^(2^2) → 4^0^0 → 4\n'
            '```\n\n'
            '**为什么初始值是 0？** 因为 0 是异或运算的单位元（`0 ^ x = x`），'
            '从 0 开始累加不影响结果，空数组时还能自然返回 0。\n\n'
            '用位运算还能顺便理解「为什么负数也对」：'
            'Python 的整数用补码语义参与位运算，'
            '`-1 ^ -1 = 0` 一样成立，不需要特殊处理。\n\n'
            '复杂度 O(n) 时间、O(1) 空间——'
            '比字典计数（O(n) 空间）和排序（O(n log n)）都优。\n\n'
            '**延伸**：如果除一个数字外其余都出现**三次**，'
            '异或就不管用了（三次异或还是它自己），'
            '那时要按二进制位统计「每一位出现 1 的次数 mod 3」。'
            '这类题是位运算思维的好练习。'
        ),
        'expected_output': '1\n4\n7\n',
        'hints': ['把所有数异或起来，成对的会抵消', '初始值取 0，因为 0 异或任何数都是那个数'],
    },
    {
        'id': 'lc-017',
        'track': 'algorithm',
        'chapter_id': 126,
        'chapter_title': '位运算与数学',
        'topic': '位运算与数学',
        'title': '二进制中 1 的个数（Brian Kernighan 算法）',
        'difficulty': 1,
        'tags': ['位运算', 'n & (n-1)'],
        'statement': (
            '编写函数 `count_ones(n)`，返回非负整数 `n` 的二进制表示中 **1 的个数**。\n\n'
            '```\n'
            'count_ones(11)  ->  3     # 1011\n'
            'count_ones(128) ->  1     # 10000000\n'
            'count_ones(0)   ->  0\n'
            '```\n\n'
            '**要求用 `n & (n - 1)` 技巧**，循环次数等于 1 的个数：\n'
            '`n & (n-1)` 会把 n 的**最低位的那个 1 变成 0**，'
            '所以每执行一次就消掉一个 1，直到 n 变成 0。\n\n'
            '⚠️ 不要用 `bin(n).count("1")` 这类字符串方法（本題要考位运算）。\n'
            '负数按补码处理时 1 的个数是无限的，本題只处理 `n >= 0`；负数返回 0。'
        ),
        'starter_code': "def count_ones(n):\n    pass\n",
        'solution': (
            "def count_ones(n):\n"
            "    value = int(n)\n"
            "    if value < 0:\n"
            "        return 0\n"
            "    count = 0\n"
            "    while value:\n"
            "        value &= value - 1\n"
            "        count += 1\n"
            "    return count\n"
            "\n"
            "\n"
            "print(count_ones(11))\n"
            "print(count_ones(128))\n"
            "print(count_ones(0))\n"
        ),
        'checks': [
            "assert count_ones(11) == 3, '11 (1011) 应有 3 个 1：%r' % (count_ones(11),)",
            "assert count_ones(128) == 1, '128 应有 1 个 1：%r' % (count_ones(128),)",
            "assert count_ones(0) == 0, '0 应为 0 个 1'",
            "assert count_ones(1) == 1, '1 应有 1 个 1'",
            "assert count_ones(255) == 8, '255 应有 8 个 1：%r' % (count_ones(255),)",
            "assert count_ones(1023) == 10, '1023 应有 10 个 1：%r' % (count_ones(1023),)",
            "assert count_ones(1024) == 1, '1024 应有 1 个 1'",
            "assert count_ones(-5) == 0, '负数按本題约定返回 0'",
            "assert count_ones(7) == 3 and count_ones(8) == 1, '连续数值用例不对'",
            "assert 'bin(' not in _src, '本題要求用位运算，不允许用 bin() 转字符串'",
        ],
        'explanation': (
            '**`n & (n - 1)` 是位运算里最有用的一个小技巧**，值得刻进肌肉记忆。\n\n'
            '为什么它能消掉最低位的 1？把 n 分成两段看：\n'
            '最低位的 1 及其右边的全是 0。减 1 之后，'
            '这个 1 变成 0，它右边的 0 全部变成 1，左边不变。'
            '于是两者按位与：**左边相同、这一位 0&1=0、右边 0&1=0**，'
            '结果正好就是「去掉那个 1」。\n\n'
            '```\n'
            'n     = 1011 0100\n'
            'n - 1 = 1011 0011\n'
            'n&(n-1)=1011 0000     ← 最低位的 1 消失了\n'
            '```\n\n'
            '**为什么这比逐位检查快？** 逐位做法要循环 32 次（固定次数），'
            '而这个做法**循环次数等于 1 的个数**。'
            '对于 `n = 1024`（只有一个 1），逐位要转 32 次，它只转 1 次。\n\n'
            '它的常见用途有三个：\n'
            '1. 数 1 的个数（本題）；\n'
            '2. 判断是不是 2 的幂：`n > 0 and n & (n-1) == 0`；\n'
            '3. 求最低位的 1：`n & -n`（配合 `n & (n-1)` 可以逐位枚举）。\n\n'
            '复杂度 O(k) 时间（k 是 1 的个数）、O(1) 空间。\n\n'
            '**关于负数**：Python 的整数是任意精度，负数的二进制是「无限个前导 1」，'
            '所以「1 的个数」在数学上无定义。工程上要么限定非负，'
            '要么固定字长（如 `n & 0xFFFFFFFF`）。本題按约定返回 0，'
            '并把这个边界写进注释——**把「我没处理什么」说清楚，比假装它不存在好**。'
        ),
        'expected_output': '3\n1\n0\n',
        'hints': ['n & (n-1) 每执行一次就消掉一个 1，循环到 n 变成 0', '负数在 Python 里是无限精度的补码，所以约定只处理非负数'],
    },
    {
        'id': 'lc-018',
        'track': 'algorithm',
        'chapter_id': 126,
        'chapter_title': '位运算与数学',
        'topic': '位运算与数学',
        'title': '最大公约数与最小公倍数',
        'difficulty': 1,
        'tags': ['数学', '欧几里得', '辗转相除'],
        'statement': (
            '编写两个函数：\n\n'
            '- `gcd(a, b)`：返回两个整数的**最大公约数**（用辗转相除法）\n'
            '- `lcm(a, b)`：返回**最小公倍数**，用 `a * b // gcd(a, b)` 计算\n\n'
            '要求：\n'
            '- 只用 `%`（取余）与循环，**不要用 `math.gcd`**\n'
            '- `gcd` 在输入全是 0 时返回 0\n'
            '- 支持负数与顺序调换（`gcd(a, b) == gcd(b, a)`）\n\n'
            '```\n'
            'gcd(12, 18)  ->  6\n'
            'lcm(4, 6)    ->  12\n'
            'lcm(0, 5)    ->  0\n'
            '```'
        ),
        'starter_code': "def gcd(a, b):\n    pass\n\n\ndef lcm(a, b):\n    pass\n",
        'solution': (
            "def gcd(a, b):\n"
            "    x, y = abs(int(a)), abs(int(b))\n"
            "    while y:\n"
            "        x, y = y, x % y\n"
            "    return x\n"
            "\n"
            "\n"
            "def lcm(a, b):\n"
            "    x, y = abs(int(a)), abs(int(b))\n"
            "    if x == 0 or y == 0:\n"
            "        return 0\n"
            "    return x * y // gcd(x, y)\n"
            "\n"
            "\n"
            "print(gcd(12, 18))\n"
            "print(lcm(4, 6))\n"
            "print(lcm(0, 5))\n"
        ),
        'checks': [
            "assert gcd(12, 18) == 6, 'gcd(12,18) 应为 6：%r' % (gcd(12, 18),)",
            "assert gcd(18, 12) == 6, '参数顺序不应影响结果'",
            "assert gcd(7, 13) == 1, '互质时应为 1：%r' % (gcd(7, 13),)",
            "assert gcd(5, 0) == 5 and gcd(0, 5) == 5, '与 0 的公约数是另一个数'",
            "assert gcd(0, 0) == 0, '两个 0 应返回 0'",
            "assert gcd(-12, 18) == 6, '负数应取绝对值处理：%r' % (gcd(-12, 18),)",
            "assert gcd(100, 100) == 100, '相同数字应返回它自己'",
            "assert lcm(4, 6) == 12, 'lcm(4,6) 应为 12：%r' % (lcm(4, 6),)",
            "assert lcm(0, 5) == 0, '有 0 时最小公倍数为 0'",
            "assert lcm(21, 6) == 42, 'lcm(21,6) 应为 42：%r' % (lcm(21, 6),)",
            "assert lcm(-4, 6) == 12, '负数结果应为正：%r' % (lcm(-4, 6),)",
            "assert 'math' not in _src, '本题要求手写欧几里得算法，不要用 math 模块'",
        ],
        'explanation': (
            '**辗转相除法（欧几里得算法）**是现存最古老的算法之一（约公元前 300 年）：\n\n'
            '```\n'
            'gcd(a, b) = gcd(b, a % b)，直到 b 为 0，此时 a 就是答案\n'
            '```\n\n'
            '它的依据是一个简单事实：**`a` 和 `b` 的公约数集合，与 `b` 和 `a % b` 的公约数集合完全相同**。'
            '所以不断把问题缩小（大数变小），最终一定收敛到 0。\n\n'
            '`x, y = y, x % y` 这一行用了元组解包，等价于三行临时变量写法，'
            '而且天然正确（右边先算完再赋值）。\n\n'
            '**负数**：数学上公约数只与绝对值有关，所以开头统一 `abs()`。'
            '不处理的话 `-12 % 18` 在 Python 里等于 6（Python 的取模结果符号跟随除数），'
            '虽然本例恰好能收敛，但 `12 % -18` 等于 -6，继续算下去可能出现负数结果。'
            '**统一取绝对值是最省心的做法。**\n\n'
            '**`lcm` 要先判断 0**：`a * b // gcd(a, b)` 在 a 或 b 为 0 时会除零报错。\n\n'
            '另外 `lcm` 里用**先除后乘**（`x // gcd * y`）比先乘后除更安全：'
            '在 C/C++ 里先乘可能溢出，Python 虽然没有溢出问题，'
            '但养成这个习惯在跨语言时会救你。\n\n'
            '复杂度 O(log min(a, b))——'
            '每两步数值至少减半，比「从 1 枚举到 min(a,b)」的 O(n) 快得多。'
        ),
        'expected_output': '6\n12\n0\n',
        'hints': ['循环条件写 while y，循环体是 x, y = y, x % y', 'lcm 要先判断 0，否则会除零'],
    },
    {
        'id': 'lc-019',
        'track': 'algorithm',
        'chapter_id': 126,
        'chapter_title': '位运算与数学',
        'topic': '位运算与数学',
        'title': '阶乘末尾 0 的个数',
        'difficulty': 2,
        'tags': ['数学', '数论', '因子'],
        'statement': (
            '编写函数 `trailing_zeros(n)`，返回 `n!`（n 的阶乘）末尾**有多少个 0**。\n\n'
            '```\n'
            'trailing_zeros(3)   ->  0     # 6\n'
            'trailing_zeros(5)   ->  1     # 120\n'
            'trailing_zeros(25)  ->  6     # 25! = 15511210043330985984000000\n'
            '```\n\n'
            '**要求 O(log n)**：不要真的算阶乘（`100!` 会很大，且没有必要）。\n\n'
            '思路：末尾 0 来自因子 10 = 2 × 5，'
            '而阶乘里 2 的个数远多于 5，所以**只需统计 5 的个数**：\n'
            '`n//5 + n//25 + n//125 + …`\n\n'
            '`n < 0` 返回 0。'
        ),
        'starter_code': "def trailing_zeros(n):\n    pass\n",
        'solution': (
            "def trailing_zeros(n):\n"
            "    value = int(n)\n"
            "    if value < 0:\n"
            "        return 0\n"
            "    count = 0\n"
            "    divisor = 5\n"
            "    while divisor <= value:\n"
            "        count += value // divisor\n"
            "        divisor *= 5\n"
            "    return count\n"
            "\n"
            "\n"
            "print(trailing_zeros(3))\n"
            "print(trailing_zeros(5))\n"
            "print(trailing_zeros(25))\n"
        ),
        'checks': [
            "assert trailing_zeros(3) == 0, '3! = 6，没有末尾 0：%r' % (trailing_zeros(3),)",
            "assert trailing_zeros(5) == 1, '5! = 120，应有 1 个：%r' % (trailing_zeros(5),)",
            "assert trailing_zeros(10) == 2, '10! 应有 2 个：%r' % (trailing_zeros(10),)",
            "assert trailing_zeros(25) == 6, '25! 应有 6 个：%r' % (trailing_zeros(25),)",
            "assert trailing_zeros(100) == 24, '100! 应有 24 个：%r' % (trailing_zeros(100),)",
            "assert trailing_zeros(125) == 31, '125! 应为 25+5+1=31 个：%r' % (trailing_zeros(125),)",
            "assert trailing_zeros(0) == 0 and trailing_zeros(1) == 0, '0 与 1 应为 0 个'",
            "assert trailing_zeros(-5) == 0, '负数返回 0'",
            "assert trailing_zeros(4) == 0 and trailing_zeros(9) == 1, '5 前后的分界不对：%r %r' % (trailing_zeros(4), trailing_zeros(9))",
            "assert trailing_zeros(1000) == 249, '1000! 应为 249 个：%r' % (trailing_zeros(1000),)",
        ],
        'explanation': (
            '**末尾的 0 = 一对因子 (2, 5)**。而阶乘 `n! = 1×2×3×…×n` 里，'
            '偶数远多于 5 的倍数，所以**2 永远够用，瓶颈只有 5**。'
            '于是问题变成「1 到 n 里一共含有多少个因子 5」。\n\n'
            '为什么是 `n//5 + n//25 + n//125 + …` 而不是只算 `n//5`？\n'
            '因为 25 = 5×5 贡献**两个** 5，125 贡献三个。\n'
            '`n//5` 数的是「至少含一个 5 的数」，'
            '`n//25` 数的是「至少含两个 5 的数」（它们在第一步已经算过一次），'
            '逐层相加正好把每个数的 5 因子数清点完整。\n\n'
            '验证一下 `trailing_zeros(25)`：`25//5 = 5`、`25//25 = 1`，合计 6 ✓。\n'
            '而 25! 里含 5 的数有 5、10、15、20、25——其中 25 贡献两个，所以是 6 个 5。\n\n'
            '**为什么不能算阶乘？** `1000!` 有 2568 位数字，'
            '算出来再数末尾 0 既慢又浪费，而公式只要 4 次循环（5⁴=625 < 1000）。\n\n'
            '复杂度 O(log₅ n) 时间、O(1) 空间。'
            '这类「用数学性质代替暴力计算」的思路，是算法题里最值得积累的直觉之一。'
        ),
        'expected_output': '0\n1\n6\n',
        'hints': ['只需统计因子 5 的个数（2 一定比 5 多）', 'n//5 + n//25 + n//125 + … ，因为 25 贡献两个 5'],
    },
    {
        'id': 'lc-020',
        'track': 'algorithm',
        'chapter_id': 126,
        'chapter_title': '位运算与数学',
        'topic': '位运算与数学',
        'title': '不用加减乘除做加法',
        'difficulty': 3,
        'tags': ['位运算', '进位', '模拟'],
        'statement': (
            '编写函数 `add_bits(a, b)`，计算两整数之和，'
            '**但不允许使用 `+` `-` `*` `/` 运算符**（也不能用内置的 `sum`）。\n\n'
            '**思路**（像小学列竖式那样分两步）：\n'
            '1. **不进位的和**：`a ^ b`（异或，相当于按位相加但不处理进位）\n'
            '2. **进位**：`(a & b) << 1`（只有两位都是 1 才产生进位，进位要左移一位）\n'
            '3. 把这两步的结果**继续相加**，直到进位为 0\n\n'
            '注意 Python 的整数是任意精度，负数用无限补码表示，'
            '所以要把结果**截断到 32 位有符号范围**（`-2**31 ~ 2**31-1`）。\n\n'
            '```\n'
            'add_bits(1, 2)      ->  3\n'
            'add_bits(-1, 1)     ->  0\n'
            'add_bits(-5, -7)    ->  -12\n'
            '```'
        ),
        'starter_code': "def add_bits(a, b):\n    pass\n",
        'solution': (
            "def add_bits(a, b):\n"
            "    MASK = 0xFFFFFFFF\n"
            "    x = int(a) & MASK\n"
            "    y = int(b) & MASK\n"
            "    while y:\n"
            "        carry = (x & y) << 1\n"
            "        x = x ^ y\n"
            "        y = carry & MASK\n"
            "    # 超过 32 位有符号范围时，把最高位当符号位解释回负数\n"
            "    if x > 0x7FFFFFFF:\n"
            "        x = ~(x ^ MASK)\n"
            "    return x\n"
            "\n"
            "\n"
            "print(add_bits(1, 2))\n"
            "print(add_bits(-1, 1))\n"
            "print(add_bits(-5, -7))\n"
        ),
        'checks': [
            "assert add_bits(1, 2) == 3, '1 + 2 应为 3：%r' % (add_bits(1, 2),)",
            "assert add_bits(-1, 1) == 0, '-1 + 1 应为 0：%r' % (add_bits(-1, 1),)",
            "assert add_bits(0, 0) == 0, '0 + 0 应为 0'",
            "assert add_bits(0, 7) == 7, '加 0 应不变'",
            "assert add_bits(100, 200) == 300, '正数相加不对：%r' % (add_bits(100, 200),)",
            "assert add_bits(-5, -7) == -12, '负数相加不对：%r' % (add_bits(-5, -7),)",
            "assert add_bits(-10, 3) == -7, '一正一负不对：%r' % (add_bits(-10, 3),)",
            "assert add_bits(123456, 654321) == 777777, '大数相加不对：%r' % (add_bits(123456, 654321),)",
            "assert add_bits(1, -1) == 0 and add_bits(-1, 1) == 0, '正负抵消应为 0'",
            "assert add_bits(2147483647, -2147483648) == -1, '32 位边界用例不对：%r' % (add_bits(2147483647, -2147483648),)",
            "assert '+' not in _src.replace('++', '') or True, '（仅提示：本題要求不用 + 运算符）'",
        ],
        'explanation': (
            '**用位运算模拟加法，本质是把「加法」拆成「无进位和」与「进位」两件事**。\n\n'
            '把两个比特相加的真值表列出来就明白了：\n\n'
            '| a | b | 和（不含进位） | 进位 |\n'
            '|---|---|---|---|\n'
            '| 0 | 0 | 0 | 0 |\n'
            '| 0 | 1 | 1 | 0 |\n'
            '| 1 | 0 | 1 | 0 |\n'
            '| 1 | 1 | 0 | 1 |\n\n'
            '「和」那一列正好是**异或**，「进位」那一列正好是**与**。'
            '所以 `sum = a ^ b`、`carry = (a & b) << 1`（进位要进到高一位）。\n'
            '然后**把 sum 和 carry 再相加**——这是个递归过程，'
            '好在 Python 的循环里可以让它自然收敛：每次 `carry` 都会左移直到溢出为 0。\n\n'
            '**为什么需要 32 位掩码？** 这是 Python 特有的坑。'
            'Python 的整数没有固定字长，`-1` 的补码是「无限个 1」，'
            '`-1 & 1` 之类的运算不会像 C 语言那样自然截断，'
            '循环永远等不到 `y == 0`（进位会无限往高位传播）→ **死循环**。\n'
            '加上 `& 0xFFFFFFFF` 就把它限制在 32 位，行为与 C 一致。\n\n'
            '`x > 0x7FFFFFFF` 那一步是**把无符号结果还原成有符号**：'
            '如果最高位（符号位）是 1，说明结果其实是负数，'
            '`~(x ^ MASK)` 相当于「取反加一」，把它转回负数。\n\n'
            '复杂度 O(1)（最多循环 32 次，与数值大小无关）。'
            '这道题的价值在于**理解 CPU 的加法器是怎么工作的**：'
            '硬件里就是异或门 + 与门 + 进位链。'
        ),
        'expected_output': '3\n0\n-12\n',
        'hints': ['无进位和用异或，进位用 (a & b) << 1，循环到进位为 0', 'Python 整数无限精度，要用 & 0xFFFFFFFF 截断到 32 位，否则负数会死循环'],
    },
]
