"""题库 · 408 真题风格算法篇（专题 117–122）。

写法约定与 qbank_basic.py / qbank_pro.py / qbank_algo.py 保持一致：
- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式。
- checks 只断言题面要求的东西，每条断言都带中文提示，覆盖空输入、单元素、重复元素等边界。
- 参考答案本身必须能通过同一套断言。

主题是「历年 408 统考真题的算法与数据结构风格」：题干按真题的写法给出数据结构定义
与函数签名，要求写出算法并说明复杂度。真题里的 C 伪代码在这里统一用 Python 的
顺序表（列表）/ 自定义结点类重述。

专题划分：
    117 顺序表与数组算法   118 链表算法      119 树与二叉树算法
    120 图算法与搜索       121 查找与散列     122 排序算法进阶
"""

QUESTIONS = [
    # ── 专题 117 顺序表与数组算法 ─────────────────────────
    {
        'id': 'n408-001',
        'track': 'algorithm',
        'chapter_id': 117,
        'chapter_title': '顺序表与数组算法',
        'topic': '顺序表与数组算法',
        'title': '顺序表删除所有值为 x 的元素（原地 O(n)）',
        'difficulty': 1,
        'tags': ['顺序表', '原地', 'O(n)'],
        'statement': (
            '已知一个顺序表（用 Python 列表 `items` 表示）和一个值 `x`。\n\n'
            '定义函数 `del_x(items, x)`：**删除表中所有值为 x 的元素**，'
            '并返回删除后剩下的元素个数。\n\n'
            '要求：\n\n'
            '- **原地**修改 `items`（表长要真的变短，不是返回一个新列表）；\n'
            '- 时间 O(n)、额外空间 O(1)：用一个「写入位置」下标 `k`，从左到右扫描，'
            '凡是值不等于 x 的元素就写进 `items[k]` 并让 `k` 加一，'
            '扫描结束后把下标 `k` 之后的部分删掉；\n'
            '- 不要写 `while x in items: items.remove(x)`，每次 remove 都要搬移后面的元素，'
            '最坏是 O(n²)。\n\n'
            '最后对 `[3, 1, 2, 1, 5, 1]` 调用 `del_x(data, 1)`，打印返回值和删除后的 `data`；'
            '再对空表、以及「全是 x」的表各打印一次结果。'
        ),
        'starter_code': 'def del_x(items, x):\n    k = 0\n    # 不等于 x 的元素写到 items[k]，k 加一；最后删掉 k 之后的尾巴\n    pass\n',
        'solution': (
            "def del_x(items, x):\n"
            "    k = 0\n"
            "    for value in items:\n"
            "        if value != x:\n"
            "            items[k] = value\n"
            "            k += 1\n"
            "    del items[k:]\n"
            "    return k\n"
            "\n"
            "data = [3, 1, 2, 1, 5, 1]\n"
            "print(del_x(data, 1), data)\n"
            "empty = []\n"
            "print(del_x(empty, 7), empty)\n"
            "all_x = [2, 2, 2]\n"
            "print(del_x(all_x, 2), all_x)\n"
        ),
        'checks': [
            "_a = [3, 1, 2, 1, 5, 1]\nassert del_x(_a, 1) == 3, 'del_x([3, 1, 2, 1, 5, 1], 1) 应返回 3（剩下的元素个数），实际 %r' % (del_x(_a, 1),)",
            "_b = [3, 1, 2, 1, 5, 1]\ndel_x(_b, 1)\nassert _b == [3, 2, 5], '删除后原列表本身应变成 [3, 2, 5]（原地修改），实际 %r' % (_b,)",
            "_c = []\nassert del_x(_c, 5) == 0 and _c == [], '空表应返回 0 且仍是空表，实际 %r' % (_c,)",
            "_d = [7]\nassert del_x(_d, 7) == 0 and _d == [], '只有一个元素且正好等于 x 时应删成空表，实际 %r' % (_d,)",
            "_e = [7]\nassert del_x(_e, 8) == 1 and _e == [7], '只有一个元素且不等于 x 时应原样保留，实际 %r' % (_e,)",
            "_f = [4, 4, 4, 4]\nassert del_x(_f, 4) == 0 and _f == [], '全是要删的值时应返回 0 且清空，实际 %r' % (_f,)",
            "_g = [1, 2, 3]\nassert del_x(_g, 9) == 3 and _g == [1, 2, 3], '没有要删的值时个数和内容都不变，实际 %r' % (_g,)",
            "_h = [2, 5, 2]\n_ref = _h\ndel_x(_h, 2)\nassert _ref == [5] and _h is _ref, '要求原地修改：列表对象本身要变成 [5]，实际 %r' % (_ref,)",
            "_i = [-1, -1, 0, -1, 2]\nassert del_x(_i, -1) == 2 and _i == [0, 2], '负数元素同样要正确处理，实际 %r' % (_i,)",
            "_j = [1, 2] * 1000\nassert del_x(_j, 1) == 1000 and _j == [2] * 1000, '2000 个元素（一半要删）应返回 1000，实际 %r' % (len(_j),)",
        ],
        'explanation': (
            '这是顺序表最经典的「原地删除」题，也是 408 顺序表大题的入门考法。\n\n'
            '**关键思路**：不要「遇到一个 x 就把后面所有元素整体前移一位」，那样最坏是 O(n²)。'
            '换个角度：把「不等于 x」的元素当成要保留的货物，用下标 k 记录下一个该放货物的位置：\n\n'
            '```python\n'
            'k = 0\n'
            'for value in items:\n'
            '    if value != x:\n'
            '        items[k] = value\n'
            '        k += 1\n'
            'del items[k:]\n'
            '```\n\n'
            '因为 k 永远追不上正在读的位置（k ≤ 当前下标），被覆盖的都是已经读过的元素，不会丢数据。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了最后的 `del items[k:]`，表长没变、尾巴上残留旧值；\n'
            '2. 用 `items.remove(x)` 循环删除——每次删除都要搬移后面所有元素，最坏 O(n²)；\n'
            '3. 写成 `items = [v for v in items if v != x]`，它看起来对，但那是**新建列表**，'
            '调用方手里的列表一点没变。题面要求「原地」时必须改对象本身，'
            '这种写法在 408 里是要扣分的。\n\n'
            '复杂度：时间 O(n)（每个元素只读一次）、额外空间 O(1)。'
        ),
        'expected_output': '3 [3, 2, 5]\n0 []\n0 []',
        'hints': ['用一个写入下标 k，把不等于 x 的元素往前搬', '扫描结束后记得 del items[k:]，否则表长不变'],
    },
    {
        'id': 'n408-002',
        'track': 'algorithm',
        'chapter_id': 117,
        'chapter_title': '顺序表与数组算法',
        'topic': '顺序表与数组算法',
        'title': '顺序表就地逆置（双指针交换）',
        'difficulty': 1,
        'tags': ['顺序表', '双指针', '原地'],
        'statement': (
            '已知顺序表 `items`（Python 列表）。\n\n'
            '定义函数 `reverse_inplace(items)`：把表**就地逆置**——'
            '第一个元素与最后一个交换、第二个与倒数第二个交换……'
            '直接修改传入的列表，函数不需要返回值。\n\n'
            '要求：\n\n'
            '- 时间 O(n)、额外空间 O(1)：用两个下标 `left = 0`、`right = len(items) - 1`，'
            '相向而行，交换 `items[left]` 与 `items[right]`，直到两者相遇；\n'
            '- 不许调用 `items.reverse()`、`reversed()` 或切片 `items[::-1]` 这类现成反转，'
            '要手写这个交换过程。\n\n'
            '最后把 `[1, 2, 3, 4, 5]` 逆置并打印，再打印空表和单元素表的逆置结果。'
        ),
        'starter_code': 'def reverse_inplace(items):\n    left = 0\n    right = len(items) - 1\n    # 交换 items[left] 与 items[right]，然后 left += 1、right -= 1\n    pass\n',
        'solution': (
            "def reverse_inplace(items):\n"
            "    left = 0\n"
            "    right = len(items) - 1\n"
            "    while left < right:\n"
            "        items[left], items[right] = items[right], items[left]\n"
            "        left += 1\n"
            "        right -= 1\n"
            "\n"
            "data = [1, 2, 3, 4, 5]\n"
            "reverse_inplace(data)\n"
            "print(data)\n"
            "empty = []\n"
            "reverse_inplace(empty)\n"
            "print(empty)\n"
            "one = [9]\n"
            "reverse_inplace(one)\n"
            "print(one)\n"
        ),
        'checks': [
            "_a = [1, 2, 3, 4, 5]\nreverse_inplace(_a)\nassert _a == [5, 4, 3, 2, 1], '五个元素逆置后应是 [5, 4, 3, 2, 1]，实际 %r' % (_a,)",
            "_b = [1, 2, 3, 4]\nreverse_inplace(_b)\nassert _b == [4, 3, 2, 1], '偶数个元素也要正确交换（4 个 → [4, 3, 2, 1]），实际 %r' % (_b,)",
            "_c = []\nreverse_inplace(_c)\nassert _c == [], '空表调用后仍应是空表'",
            "_d = [7]\nreverse_inplace(_d)\nassert _d == [7], '只有一个元素时逆置后还是它自己'",
            "_e = [2, 2, 3]\nreverse_inplace(_e)\nassert _e == [3, 2, 2], '有重复元素时也要正确，实际 %r' % (_e,)",
            "_f = [5, 5, 5, 5]\nreverse_inplace(_f)\nassert _f == [5, 5, 5, 5], '元素全相同时逆置后不变，实际 %r' % (_f,)",
            "_g = [1, 2]\n_ref = _g\nreverse_inplace(_g)\nassert _ref == [2, 1] and _g is _ref, '要求原地修改：列表对象本身要变成 [2, 1]，实际 %r' % (_ref,)",
            "_h = list(range(1000))\nreverse_inplace(_h)\nassert _h == list(range(999, -1, -1)), '1000 个元素逆置后第一个应是 999，实际 %r' % (_h[0],)",
            "assert '.reverse(' not in _src and '[::-1]' not in _src and 'reversed(' not in _src, '题面要求手写双指针交换来逆置，不要调用 reverse()/reversed()/切片反转'",
        ],
        'explanation': (
            '逆置的本质是**对称位置的元素互换**，所以只要两个下标就够了。\n\n'
            '```python\n'
            'while left < right:\n'
            '    items[left], items[right] = items[right], items[left]\n'
            '    left += 1\n'
            '    right -= 1\n'
            '```\n\n'
            '循环条件为什么是 `left < right` 而不是 `left <= right`？'
            '当 `left == right` 时，交换的是同一个位置，纯属白做；'
            '如果写成 `left != right` 之类的条件，偶数长度还会越过中点造成二次交换（换了等于没换）。\n\n'
            'Python 的 `a, b = b, a` 一步完成交换，靠的是「先算右边再同时赋值」；'
            '写成 `items[left] = items[right]` 再 `items[right] = items[left]` 就会把两个位置变成同一个值（经典丢失数据的错误）。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `items = items[::-1]`——切片产生新列表，原列表没变，而且额外空间是 O(n)；\n'
            '2. 循环里忘记同时推进两个下标，造成死循环；\n'
            '3. 交换写成连续两条赋值语句，丢掉了被覆盖的值。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[5, 4, 3, 2, 1]\n[]\n[9]',
        'hints': ['两个下标相向而行，left < right 时交换并各自前进一步', 'Python 里 a, b = b, a 一步交换，别拆成两步赋值'],
    },
    {
        'id': 'n408-003',
        'track': 'algorithm',
        'chapter_id': 117,
        'chapter_title': '顺序表与数组算法',
        'topic': '顺序表与数组算法',
        'title': '两个有序表合并去重（双指针归并）',
        'difficulty': 2,
        'tags': ['顺序表', '归并', '去重'],
        'statement': (
            '已知两个**升序**顺序表 `a` 和 `b`（可能有重复元素）。\n\n'
            '定义函数 `merge_sorted(a, b)`：返回一个**新的升序列表**，'
            '其中包含 a 和 b 的所有元素，且**相同的值只保留一个**。\n\n'
            '要求：\n\n'
            '- 用「双指针归并」：`i` 指向 a、`j` 指向 b，每次取较小的那个放进结果，'
            '  两个元素相等时两个指针一起后移（这样重复值只写一次），'
            '  时间 O(len(a) + len(b))；\n'
            '- **不要修改** a 和 b；\n'
            '- 不要写 `sorted(set(a + b))`：`set` 会丢掉顺序，`sorted` 又要 O(n log n)，'
            '  不符合题目要求；\n'
            '- 收尾时把某一边剩下的元素接着放进结果（注意同样要去重）。\n\n'
            '最后打印 `merge_sorted([1, 3, 5, 7], [2, 3, 4, 8])`、'
            '`merge_sorted([], [1, 2])` 和 `merge_sorted([1, 1, 2], [1, 2, 2])` 的结果。'
        ),
        'starter_code': 'def merge_sorted(a, b):\n    result = []\n    i = 0\n    j = 0\n    # 比大小、取小的、跳过重复值；最后把剩下的接上\n    pass\n',
        'solution': (
            "def merge_sorted(a, b):\n"
            "    result = []\n"
            "    i = 0\n"
            "    j = 0\n"
            "    while i < len(a) and j < len(b):\n"
            "        if a[i] < b[j]:\n"
            "            pick = a[i]\n"
            "            i += 1\n"
            "        elif a[i] > b[j]:\n"
            "            pick = b[j]\n"
            "            j += 1\n"
            "        else:\n"
            "            pick = a[i]\n"
            "            i += 1\n"
            "            j += 1\n"
            "        if not result or result[-1] != pick:\n"
            "            result.append(pick)\n"
            "    while i < len(a):\n"
            "        if not result or result[-1] != a[i]:\n"
            "            result.append(a[i])\n"
            "        i += 1\n"
            "    while j < len(b):\n"
            "        if not result or result[-1] != b[j]:\n"
            "            result.append(b[j])\n"
            "        j += 1\n"
            "    return result\n"
            "\n"
            "print(merge_sorted([1, 3, 5, 7], [2, 3, 4, 8]))\n"
            "print(merge_sorted([], [1, 2]))\n"
            "print(merge_sorted([1, 1, 2], [1, 2, 2]))\n"
        ),
        'checks': [
            "assert merge_sorted([1, 3, 5, 7], [2, 3, 4, 8]) == [1, 2, 3, 4, 5, 7, 8], '经典例子应是 [1, 2, 3, 4, 5, 7, 8]，实际 %r' % (merge_sorted([1, 3, 5, 7], [2, 3, 4, 8]),)",
            "assert merge_sorted([], []) == [], '两个空表应返回空列表，实际 %r' % (merge_sorted([], []),)",
            "assert merge_sorted([], [1, 2]) == [1, 2], 'a 为空时结果就是 b 的元素，实际 %r' % (merge_sorted([], [1, 2]),)",
            "assert merge_sorted([1, 2], []) == [1, 2], 'b 为空时结果就是 a 的元素，实际 %r' % (merge_sorted([1, 2], []),)",
            "assert merge_sorted([1, 2], [3, 4]) == [1, 2, 3, 4], '一边整体更小时要正确接上，实际 %r' % (merge_sorted([1, 2], [3, 4]),)",
            "assert merge_sorted([3, 4], [1, 2]) == [1, 2, 3, 4], 'b 整体更小时也要正确，实际 %r' % (merge_sorted([3, 4], [1, 2]),)",
            "assert merge_sorted([1, 1, 2], [1, 2, 2]) == [1, 2], '两边都有重复值时结果只保留一个，实际 %r' % (merge_sorted([1, 1, 2], [1, 2, 2]),)",
            "assert merge_sorted([5], [5]) == [5], '两个单元素且相等时应只剩一个 5，实际 %r' % (merge_sorted([5], [5]),)",
            "assert merge_sorted([1, 1, 1], [2, 2]) == [1, 2], 'a 内部有大量重复也要去重，实际 %r' % (merge_sorted([1, 1, 1], [2, 2]),)",
            "_p = [1, 3]\n_q = [2]\nmerge_sorted(_p, _q)\nassert _p == [1, 3] and _q == [2], '题面要求返回新列表、不修改 a 和 b，实际 a=%r b=%r' % (_p, _q)",
            "assert merge_sorted([-5, -1], [-3, 0]) == [-5, -3, -1, 0], '负数同样要正确归并，实际 %r' % (merge_sorted([-5, -1], [-3, 0]),)",
            "assert merge_sorted(list(range(0, 2000, 2)), list(range(1, 2000, 2))) == list(range(2000)), '两个各 1000 个元素的表应归并成 0~1999'",
        ],
        'explanation': (
            '归并两个有序表是顺序表里最常考的算法，双指针一趟扫描就够：\n\n'
            '```python\n'
            'while i < len(a) and j < len(b):\n'
            '    if a[i] < b[j]:\n'
            '        pick = a[i]; i += 1\n'
            '    elif a[i] > b[j]:\n'
            '        pick = b[j]; j += 1\n'
            '    else:\n'
            '        pick = a[i]; i += 1; j += 1      # 相等：两个指针一起后移\n'
            '    if not result or result[-1] != pick:\n'
            '        result.append(pick)\n'
            '```\n\n'
            '**为什么不会漏掉重复值？** 因为两个表各自升序，「值相等」只可能出现在两个指针当前位置。'
            '相等时让两个指针一起走，等于把这个值在两边同时消费掉；'
            '再配合 `result[-1] != pick` 这道保险，表内部的重复（如 a = [1, 1, 2]）也能滤掉。\n\n'
            '**常见错误**：\n\n'
            '1. 只写主循环、忘了两个收尾 `while`，一边的剩余元素全丢；\n'
            '2. 收尾时直接用 `result += a[i:]`，把重复值又放回来了；\n'
            '3. 写成 `sorted(set(a + b))`，能得到正确答案但复杂度变成 O(n log n)，'
            '   而且 `set` 里的元素顺序是散列决定的，题目要的是「归并」这个 O(n) 做法。\n\n'
            '复杂度：时间 O(m + n)、额外空间 O(m + n)（结果列表本身）。'
        ),
        'expected_output': '[1, 2, 3, 4, 5, 7, 8]\n[1, 2]\n[1, 2]',
        'hints': ['两个指针分别往前走，取较小的那个', '相等时两个指针一起后移，再把 result[-1] 和它比对一下去重'],
    },
    {
        'id': 'n408-004',
        'track': 'algorithm',
        'chapter_id': 117,
        'chapter_title': '顺序表与数组算法',
        'topic': '顺序表与数组算法',
        'title': '顺序表循环左移 k 位（三次翻转）',
        'difficulty': 2,
        'tags': ['顺序表', '三次翻转', 'O(1) 空间'],
        'statement': (
            '已知顺序表 `items` 和非负整数 `k`。\n\n'
            '定义函数 `rotate_left(items, k)`：把表中元素**整体循环左移 k 位**，'
            '直接修改 `items`，函数不需要返回值。\n\n'
            '例如 `[1, 2, 3, 4, 5]` 左移 2 位得到 `[3, 4, 5, 1, 2]`。\n\n'
            '要求：\n\n'
            '- `k` 可能大于等于表长，先做 `k = k % len(items)`（注意空表要直接返回，别让取模除零）；\n'
            '- 时间 O(n)、额外空间 O(1)，用**三次翻转**的做法：'
            '先把前 k 个元素翻转，再把剩下的 n − k 个元素翻转，最后把整个表翻转；\n'
            '- 不要用 `items[:] = items[k:] + items[:k]`（那是 O(n) 额外空间），'
            '也不要一位一位地搬移（那是 O(n × k)）。\n\n'
            '最后打印 `[1, 2, 3, 4, 5]` 左移 2 位的结果，以及左移 0 位、'
            '左移 5 位、`[1, 2, 3]` 左移 7 位的结果。'
        ),
        'starter_code': 'def reverse_range(items, left, right):\n    # 把 items[left..right] 这一段就地翻转\n    pass\n\ndef rotate_left(items, k):\n    n = len(items)\n    # k %= n；三次翻转：前 k 个、后 n-k 个、整体\n    pass\n',
        'solution': (
            "def reverse_range(items, left, right):\n"
            "    while left < right:\n"
            "        items[left], items[right] = items[right], items[left]\n"
            "        left += 1\n"
            "        right -= 1\n"
            "\n"
            "def rotate_left(items, k):\n"
            "    n = len(items)\n"
            "    if n == 0:\n"
            "        return\n"
            "    k = k % n\n"
            "    reverse_range(items, 0, k - 1)\n"
            "    reverse_range(items, k, n - 1)\n"
            "    reverse_range(items, 0, n - 1)\n"
            "\n"
            "a = [1, 2, 3, 4, 5]\n"
            "rotate_left(a, 2)\n"
            "print(a)\n"
            "b = [1, 2, 3, 4, 5]\n"
            "rotate_left(b, 0)\n"
            "print(b)\n"
            "c = [1, 2, 3, 4, 5]\n"
            "rotate_left(c, 5)\n"
            "print(c)\n"
            "d = [1, 2, 3]\n"
            "rotate_left(d, 7)\n"
            "print(d)\n"
        ),
        'checks': [
            "_a = [1, 2, 3, 4, 5]\nrotate_left(_a, 2)\nassert _a == [3, 4, 5, 1, 2], '左移 2 位应是 [3, 4, 5, 1, 2]，实际 %r' % (_a,)",
            "_b = [1, 2, 3]\nrotate_left(_b, 0)\nassert _b == [1, 2, 3], 'k = 0 时表不该有任何变化，实际 %r' % (_b,)",
            "_c = [1, 2, 3]\nrotate_left(_c, 3)\nassert _c == [1, 2, 3], 'k 等于表长时表不该有变化，实际 %r' % (_c,)",
            "_d = [1, 2, 3]\nrotate_left(_d, 7)\nassert _d == [2, 3, 1], 'k = 7 表示 7 %% 3 = 1，应是 [2, 3, 1]，实际 %r' % (_d,)",
            "_e = []\nrotate_left(_e, 3)\nassert _e == [], '空表调用不该报错（注意别对 0 取模），实际 %r' % (_e,)",
            "_f = [9]\nrotate_left(_f, 4)\nassert _f == [9], '只有一个元素时左移任意位都不变，实际 %r' % (_f,)",
            "_g = [1, 2, 3]\n_ref = _g\nrotate_left(_g, 1)\nassert _ref == [2, 3, 1] and _g is _ref, '要求原地修改：列表对象本身要变成 [2, 3, 1]，实际 %r' % (_ref,)",
            "_h = [1, 1, 2, 2]\nrotate_left(_h, 3)\nassert _h == [2, 1, 1, 2], '有重复元素也要正确，实际 %r' % (_h,)",
            "_i = list(range(10))\nrotate_left(_i, 1000003)\nassert _i == list(range(3, 10)) + list(range(0, 3)), 'k 远大于表长时先取模（1000003 %% 10 = 3），实际 %r' % (_i,)",
            "_j = list(range(8))\nrotate_left(_j, 5)\nassert _j == list(range(5, 8)) + list(range(0, 5)), '8 个元素左移 5 位应是 [5, 6, 7, 0, 1, 2, 3, 4]，实际 %r' % (_j,)",
        ],
        'explanation': (
            '循环左移 k 位 = 把前 k 个元素「搬到」后面去。\n\n'
            '**三次翻转为什么对？** 记字符串 A = 前 k 个、B = 剩下的 n − k 个，原表是 AB，'
            '目标是把 AB 变成 BA。翻转有个漂亮的性质：`reverse(reverse(A) + reverse(B)) = B + A`。'
            '于是「各自翻转、再整体翻转」就完成了搬家，而且每一步都只在原表上交换，不需要额外数组。\n\n'
            '```python\n'
            'k = k % n\n'
            'reverse_range(items, 0, k - 1)      # A 变 reverse(A)\n'
            'reverse_range(items, k, n - 1)      # B 变 reverse(B)\n'
            'reverse_range(items, 0, n - 1)      # 整体翻转 → BA\n'
            '```\n\n'
            '**常见错误**：\n\n'
            '1. 忘记 `k %= n`，k 比 n 大时就翻错位置；\n'
            '2. 空表上做 `k %= n` 直接 ZeroDivisionError，要先 `if n == 0: return`；\n'
            '3. 三次翻转的顺序写反（必须是「前段 → 后段 → 整体」）；\n'
            '4. 用 `items[:] = items[k:] + items[:k]`，答案虽然对，但额外空间是 O(n)，'
            '   408 的评分点恰恰在 O(1) 空间上。\n\n'
            '复杂度：时间 O(n)（每段各扫一遍）、额外空间 O(1)。'
        ),
        'expected_output': '[3, 4, 5, 1, 2]\n[1, 2, 3, 4, 5]\n[1, 2, 3, 4, 5]\n[2, 3, 1]',
        'hints': ['k 先对表长取模，空表要提前返回', '三次翻转的顺序：前 k 个 → 其余 → 整体'],
    },
    {
        'id': 'n408-005',
        'track': 'algorithm',
        'chapter_id': 117,
        'chapter_title': '顺序表与数组算法',
        'topic': '顺序表与数组算法',
        'title': '两个等长升序序列的中位数（分治 O(log n)）',
        'difficulty': 3,
        'tags': ['顺序表', '分治', '中位数', 'O(log n)'],
        'statement': (
            '已知两个**长度相同**的升序序列 `a` 和 `b`（长度 n ≥ 1，元素可能重复）。\n\n'
            '定义函数 `median_equal_length(a, b)`，返回它们合并后序列的中位数。\n\n'
            '按统考教材的定义：对 m 个元素的升序序列，中位数是**第 ⌈m / 2⌉ 个**元素。'
            '这里两个序列一共 2n 个元素，所以中位数就是合并序列里**第 n 小**的那个元素'
            '（2n 是偶数，取靠前的那个中位数）。\n\n'
            '例如 `a = [11, 13, 15, 17, 19]`、`b = [2, 4, 6, 8, 20]`，'
            '合并后是 `[2, 4, 6, 8, 11, 13, 15, 17, 19, 20]`，n = 5，第 5 小是 11。\n\n'
            '要求：**时间 O(log n)、空间 O(1)**，用分治每次砍掉一半，'
            '不允许先把两个序列合并起来再取中间（O(n) 太慢）。做法：\n\n'
            '- 分别取 a 的中位数 `ma = a[(lo1 + hi1) // 2]`、`mb = b[(lo2 + hi2) // 2]`；\n'
            '- 若 `ma == mb`，它就是答案；\n'
            '- 若 `ma < mb`，答案不可能在 a 的前半段、也不可能在 b 的后半段，各舍一半；\n'
            '- 若 `ma > mb`，对称地舍掉 a 的后半段与 b 的前半段；\n'
            '- 注意**段长是奇数还是偶数**会让边界差一格：段长为奇数时保留 `ma` 自己，'
            '偶数时要连同它一起舍掉（可以对照下面「参考答案」里的写法）；\n'
            '- 直到两段各剩一个元素，返回较小的那个。\n\n'
            '最后打印上面例子、`[1, 3]` 与 `[2, 4]`、`[5]` 与 `[7]` 的结果。'
        ),
        'starter_code': 'def median_equal_length(a, b):\n    lo1, hi1 = 0, len(a) - 1\n    lo2, hi2 = 0, len(b) - 1\n    # 每轮比较两段的中位数，砍掉一半；剩一个元素时返回较小的那个\n    pass\n',
        'solution': (
            "def median_equal_length(a, b):\n"
            "    lo1, hi1 = 0, len(a) - 1\n"
            "    lo2, hi2 = 0, len(b) - 1\n"
            "    while lo1 < hi1:\n"
            "        mid1 = (lo1 + hi1) // 2\n"
            "        mid2 = (lo2 + hi2) // 2\n"
            "        if a[mid1] == b[mid2]:\n"
            "            return a[mid1]\n"
            "        if a[mid1] < b[mid2]:\n"
            "            if (lo1 + hi1) % 2 == 0:\n"
            "                lo1 = mid1\n"
            "                hi2 = mid2\n"
            "            else:\n"
            "                lo1 = mid1 + 1\n"
            "                hi2 = mid2\n"
            "        else:\n"
            "            if (lo1 + hi1) % 2 == 0:\n"
            "                hi1 = mid1\n"
            "                lo2 = mid2\n"
            "            else:\n"
            "                hi1 = mid1\n"
            "                lo2 = mid2 + 1\n"
            "    if a[lo1] < b[lo2]:\n"
            "        return a[lo1]\n"
            "    return b[lo2]\n"
            "\n"
            "print(median_equal_length([11, 13, 15, 17, 19], [2, 4, 6, 8, 20]))\n"
            "print(median_equal_length([1, 3], [2, 4]))\n"
            "print(median_equal_length([5], [7]))\n"
        ),
        'checks': [
            "assert median_equal_length([11, 13, 15, 17, 19], [2, 4, 6, 8, 20]) == 11, '经典例子合并后第 5 小是 11，实际 %r' % (median_equal_length([11, 13, 15, 17, 19], [2, 4, 6, 8, 20]),)",
            "assert median_equal_length([5], [7]) == 5, '各 1 个元素时应返回较小的 5，实际 %r' % (median_equal_length([5], [7]),)",
            "assert median_equal_length([7], [5]) == 5, '参数顺序反过来结果一样（都是 5），实际 %r' % (median_equal_length([7], [5]),)",
            "assert median_equal_length([1, 3], [2, 4]) == 2, '合并后 [1, 2, 3, 4] 的第 2 小是 2，实际 %r' % (median_equal_length([1, 3], [2, 4]),)",
            "assert median_equal_length([1, 2], [3, 4]) == 2, '两段完全不重叠时第 2 小是 2，实际 %r' % (median_equal_length([1, 2], [3, 4]),)",
            "assert median_equal_length([3, 4], [1, 2]) == 2, '两段顺序对调结果不变，实际 %r' % (median_equal_length([3, 4], [1, 2]),)",
            "assert median_equal_length([1, 2, 3], [4, 5, 6]) == 3, '各 3 个元素时第 3 小是 3，实际 %r' % (median_equal_length([1, 2, 3], [4, 5, 6]),)",
            "assert median_equal_length([2, 2, 2], [2, 2, 2]) == 2, '元素全相同时中位数就是 2，实际 %r' % (median_equal_length([2, 2, 2], [2, 2, 2]),)",
            "assert median_equal_length([1, 1, 1], [1, 1, 2]) == 1, '只有最后一个元素更大时第 3 小仍是 1，实际 %r' % (median_equal_length([1, 1, 1], [1, 1, 2]),)",
            "assert median_equal_length([1, 2, 3, 4], [3, 4, 5, 6]) == 3, '合并后 [1, 2, 3, 3, 4, 4, 5, 6] 的第 4 小是 3，实际 %r' % (median_equal_length([1, 2, 3, 4], [3, 4, 5, 6]),)",
            "assert median_equal_length(list(range(0, 200, 2)), list(range(1, 200, 2))) == 99, '两个各 100 个元素的序列（0~199）第 100 小是 99，实际 %r' % (median_equal_length(list(range(0, 200, 2)), list(range(1, 200, 2))),)",
            "assert median_equal_length(list(range(1, 200, 2)), list(range(0, 200, 2))) == 99, '两个序列对调后结果仍是 99，实际 %r' % (median_equal_length(list(range(1, 200, 2)), list(range(0, 200, 2))),)",
        ],
        'explanation': (
            '这题是「分治 + 二分」的典型：**两个等长升序序列的中位数一定夹在两段中位数之间**。\n\n'
            '设 a 的中位数是 ma、b 的是 mb，且 ma < mb。'
            'a 里比 ma 小的那一半（连同 ma）和 b 里比 mb 大的那一半（连同 mb）'
            '都可以直接砍掉——因为合起来看，它们的位置一定不在第 n 小上。'
            '每轮砍掉一半，所以是 O(log n)。\n\n'
            '**奇数长度和偶数长度的边界不一样**，这是本题最容易丢分的地方：\n\n'
            '```python\n'
            'if a[mid1] < b[mid2]:\n'
            '    if (lo1 + hi1) % 2 == 0:      # 段长是奇数\n'
            '        lo1 = mid1                # 保留 ma\n'
            '        hi2 = mid2\n'
            '    else:                         # 段长是偶数\n'
            '        lo1 = mid1 + 1            # 舍掉 ma\n'
            '        hi2 = mid2\n'
            '```\n\n'
            '直观理解：段长为奇数时，mid1 前面的元素个数和后面的元素个数相同，'
            'ma 需要留在候选里；段长为偶数时多出来的那一个必须被舍掉，否则剩下的两段长度不再相等，'
            '后面的下标就全错了。\n\n'
            '**常见错误**：忘记处理段长奇偶；循环退出条件是「两段各剩 1 个元素」，'
            '最后返回 `min(a[lo1], b[lo2])` 而不是某一侧的值。\n\n'
            '复杂度：时间 O(log n)、额外空间 O(1)。'
        ),
        'expected_output': '11\n2\n5',
        'hints': ['每轮比较两段的中位数，然后各砍一半', '段长为奇数时保留 mid 本身，偶数时要把它一起舍掉'],
    },
    # ── 专题 118 链表算法 ─────────────────────────────────
    {
        'id': 'n408-006',
        'track': 'algorithm',
        'chapter_id': 118,
        'chapter_title': '链表算法',
        'topic': '链表算法',
        'title': '删除单链表中所有值为 x 的结点',
        'difficulty': 1,
        'tags': ['单链表', '指针', '原地'],
        'statement': (
            '请**按下面的定义**写好结点类（属性名必须一致，后面的函数都要用它）：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `remove_all(head, x)`：删除单链表中**所有** `val == x` 的结点，'
            '返回删除后的头结点；空链表返回 `None`。\n\n'
            '要求：\n\n'
            '- 一趟扫描、额外空间 O(1)，**不要新建结点**、也不要把值拷进列表再重建；\n'
            '- 注意**头结点也可能被删掉**：先用 `while head is not None and head.val == x` '
            '把开头连续的 x 全部跳过；\n'
            '- 再用 `current` 指针往后走，检查的是 `current.next` 的值：'
            '命中就 `current.next = current.next.next`（跳过它），没命中才把 `current` 后移。\n\n'
            '最后构造 `1 → 2 → 1 → 3 → 1`，删除 1 后打印剩下的值，'
            '再打印对空链表调用后的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef remove_all(head, x):\n    # 先处理开头连续的 x，再用 current 检查 current.next\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def remove_all(head, x):\n"
            "    while head is not None and head.val == x:\n"
            "        head = head.next\n"
            "    current = head\n"
            "    while current is not None and current.next is not None:\n"
            "        if current.next.val == x:\n"
            "            current.next = current.next.next\n"
            "        else:\n"
            "            current = current.next\n"
            "    return head\n"
            "\n"
            "chain = Node(1, Node(2, Node(1, Node(3, Node(1)))))\n"
            "result = remove_all(chain, 1)\n"
            "values = []\n"
            "while result is not None:\n"
            "    values.append(result.val)\n"
            "    result = result.next\n"
            "print(values)\n"
            "print(remove_all(None, 1))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "assert _to_list(remove_all(None, 1)) == [], '空链表（None）删除后还应是 None（转成列表是 []）'",
            "assert _to_list(remove_all(_build([5]), 5)) == [], '只有一个结点且等于 x 时应全部删掉'",
            "assert _to_list(remove_all(_build([5]), 3)) == [5], '只有一个结点但不等于 x 时应原样保留'",
            "assert _to_list(remove_all(_build([1, 2, 3]), 1)) == [2, 3], '头结点等于 x 时新头要后移，实际 %r' % (_to_list(remove_all(_build([1, 2, 3]), 1)),)",
            "assert _to_list(remove_all(_build([1, 2, 3]), 3)) == [1, 2], '尾结点等于 x 时要把尾删掉，实际 %r' % (_to_list(remove_all(_build([1, 2, 3]), 3)),)",
            "assert _to_list(remove_all(_build([1, 9, 9, 9, 2]), 9)) == [1, 2], '中间连续多个 x 要全部删掉，实际 %r' % (_to_list(remove_all(_build([1, 9, 9, 9, 2]), 9)),)",
            "assert _to_list(remove_all(_build([4, 4, 4]), 4)) == [], '全是要删的值时应返回 None（空链表）'",
            "assert _to_list(remove_all(_build([1, 2, 3]), 7)) == [1, 2, 3], '没有命中的值时应原样返回，实际 %r' % (_to_list(remove_all(_build([1, 2, 3]), 7)),)",
            "assert _to_list(remove_all(_build([2, 2, 3, 2]), 3)) == [2, 2, 2], '值有重复但都不是 x 时一个也不能少，实际 %r' % (_to_list(remove_all(_build([2, 2, 3, 2]), 3)),)",
            "assert _to_list(remove_all(_build([1, 2] * 300), 2)) == [1] * 300, '600 个结点的链表要一趟扫完（剩下 300 个 1）'",
        ],
        'explanation': (
            '单链表删除要处理两个位置：**头结点**和**其它结点**，这两处的写法不一样。\n\n'
            '```python\n'
            'while head is not None and head.val == x:\n'
            '    head = head.next              # 头结点被删，头指针后移\n'
            'current = head\n'
            'while current is not None and current.next is not None:\n'
            '    if current.next.val == x:\n'
            '        current.next = current.next.next     # 跳过下一个结点\n'
            '    else:\n'
            '        current = current.next               # 没命中才后移\n'
            '```\n\n'
            '**为什么检查 `current.next` 而不是 `current`？** 因为要删掉一个结点，'
            '必须改**它前面那个结点**的 `next`；只拿着「要删的结点」是没法把它摘下来的。'
            '所以让 `current` 始终停在「待检查结点的前一个」位置。\n\n'
            '**常见错误**：\n\n'
            '1. 命中后也把 `current` 后移了，于是连续两个 x 时只删掉第一个；\n'
            '2. 忘了处理头结点，`1 → 1 → 2` 删除 1 后会留下一个 1；\n'
            '3. 直接 `while current.val == x: current = current.next`，'
            '   没有改前驱的指针，链表里残渣还在；\n'
            '4. 为了省事把值拷进列表再重建链表——408 明确要求就地改指针。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[2, 3]\nNone',
        'hints': ['先跳过开头连续的 x（头结点可能被删）', '检查 current.next，命中就跳过它，没命中才后移'],
    },
    {
        'id': 'n408-007',
        'track': 'algorithm',
        'chapter_id': 118,
        'chapter_title': '链表算法',
        'topic': '链表算法',
        'title': '单链表就地逆置（三指针）',
        'difficulty': 1,
        'tags': ['单链表', '指针', '就地逆置'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `reverse_list(head)`：把单链表**就地逆置**'
            '（只改结点的 `next` 指针，复用原来的结点），返回**逆置后的新头结点**；'
            '空链表返回 `None`。\n\n'
            '要求：时间 O(n)、额外空间 O(1)，用**三指针**：`prev`（已经逆置好的部分的头）、'
            '`current`（当前结点）、`nxt`（先保存下一个结点）。每一步：\n\n'
            '1. `nxt = current.next`（先把后面的路记下来）；\n'
            '2. `current.next = prev`（当前结点掉头指向前一个）；\n'
            '3. `prev = current`、`current = nxt`（两个指针一起后移）；\n'
            '4. 循环结束后返回 `prev`。\n\n'
            '最后把 `1 → 2 → 3 → 4 → 5` 逆置并打印各结点的值，'
            '再打印逆置空链表和单结点链表的结果。'
        ),
        'starter_code': 'def reverse_list(head):\n    prev = None\n    current = head\n    # 先存 next，再改 current.next 指向 prev，最后一起后移\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def reverse_list(head):\n"
            "    prev = None\n"
            "    current = head\n"
            "    while current is not None:\n"
            "        nxt = current.next\n"
            "        current.next = prev\n"
            "        prev = current\n"
            "        current = nxt\n"
            "    return prev\n"
            "\n"
            "node = Node(1, Node(2, Node(3, Node(4, Node(5)))))\n"
            "reversed_head = reverse_list(node)\n"
            "values = []\n"
            "while reversed_head is not None:\n"
            "    values.append(reversed_head.val)\n"
            "    reversed_head = reversed_head.next\n"
            "print(values)\n"
            "print(reverse_list(None))\n"
            "print(reverse_list(Node(8)).val)\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "assert _to_list(reverse_list(None)) == [], '空链表逆置后还应是 None（转成列表是 []）'",
            "assert _to_list(reverse_list(_build([1]))) == [1], '单结点链表逆置后还是它自己'",
            "assert _to_list(reverse_list(_build([1, 2]))) == [2, 1], '两个结点要交换过来，实际 %r' % (_to_list(reverse_list(_build([1, 2]))),)",
            "assert _to_list(reverse_list(_build([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1], '五个结点逆置结果不对：%r' % (_to_list(reverse_list(_build([1, 2, 3, 4, 5]))),)",
            "assert _to_list(reverse_list(_build([1, 1, 2, 2, 1]))) == [1, 2, 2, 1, 1], '有重复值也要正确逆置，实际 %r' % (_to_list(reverse_list(_build([1, 1, 2, 2, 1]))),)",
            "assert _to_list(reverse_list(_build([-1, 0, 0, 5]))) == [5, 0, 0, -1], '负数和 0 也要正确处理，实际 %r' % (_to_list(reverse_list(_build([-1, 0, 0, 5]))),)",
            "_head = _build([1, 2, 3])\n_tail = _head.next.next\n_new = reverse_list(_head)\nassert _new is _tail, '要求就地逆置：新头应当是原来的尾结点（复用原来的结点对象）'",
            "_head = _build([1, 2, 3])\nreverse_list(_head)\nassert _head.next is None, '就地逆置后原来的头结点应变成尾结点（next 为 None）'",
            "assert _to_list(reverse_list(_build(list(range(1000))))) == list(range(999, -1, -1)), '1000 个结点的链表也要能逆置'",
        ],
        'explanation': (
            '逆置链表只要记住**三根指针的舞蹈**：\n\n'
            '```python\n'
            'while current is not None:\n'
            '    nxt = current.next      # 1. 先记住后面还有谁\n'
            '    current.next = prev     # 2. 当前结点掉头指向前一个\n'
            '    prev = current          # 3. prev 前进\n'
            '    current = nxt           # 4. current 前进\n'
            'return prev\n'
            '```\n\n'
            '第 1 步**必须先做**：一旦执行了第 2 步，`current.next` 就被改掉了，'
            '再想往后走就找不到路了。这是本题最经典的错误——忘记保存 next，'
            '链表在中间断成两截，后面的结点全部丢失。\n\n'
            '循环结束时 `current` 是 None，`prev` 停在原来的最后一个结点上，'
            '所以返回的是 `prev`，不是 `current`、也不是原来的 `head`。\n\n'
            '为什么强调「就地」？新建一条链表需要 O(n) 额外空间，'
            '而就地逆置只用三个变量，空间 O(1)。408 的参考答案就是这种改指针的写法，'
            '把值读出来放进列表再重建虽然结果对，但会丢分。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[5, 4, 3, 2, 1]\nNone\n8',
        'hints': ['先把 current.next 存进 nxt，再改指针方向', '循环结束后返回 prev，它才是新头'],
    },
    {
        'id': 'n408-008',
        'track': 'algorithm',
        'chapter_id': 118,
        'chapter_title': '链表算法',
        'topic': '链表算法',
        'title': '求两个链表的第一个公共结点（长度对齐）',
        'difficulty': 2,
        'tags': ['单链表', '公共结点', '双指针'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `first_common(head_a, head_b)`：返回两条单链表的**第一个公共结点**'
            '（要求是**同一个结点对象**，返回的就是那个结点本身），没有公共结点就返回 `None`。\n\n'
            '注意「公共结点」的含义：两条链表从某个结点开始**共用同一段尾巴**'
            '（后面的每个结点都是同一个对象）；'
            '**不是**「两个位置上的值恰好相等」——值相同但结点不同不算公共结点。\n\n'
            '要求时间 O(m + n)、额外空间 O(1)，用「长度对齐」的两步做法：\n\n'
            '1. 先分别求出两条链表的长度；\n'
            '2. 让较长的那条先走 |len_a − len_b| 步，使两个指针到**链表尾部**的距离相同；\n'
            '3. 两个指针同步前进，第一次满足 `p is q` 的地方就是第一个公共结点；'
            '若走到末尾（两个都是 `None`）仍未相遇，则没有公共结点。\n\n'
            '不要用集合 / 字典记录走过的结点（那是 O(n) 额外空间），'
            '也不要比较结点的值。\n\n'
            '最后造两条共尾的链表（`1 → 2 → 6 → 7` 与 `3 → 6 → 7`，公共部分是 `6 → 7`），'
            '打印公共结点的值；再打印两条「值相同但结点完全不同」的链表的结果。'
        ),
        'starter_code': 'def list_length(head):\n    # 走一遍数结点个数\n    pass\n\ndef first_common(head_a, head_b):\n    # 先算长度差，让长的先走若干步，再同步前进找 p is q\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def list_length(head):\n"
            "    count = 0\n"
            "    while head is not None:\n"
            "        count += 1\n"
            "        head = head.next\n"
            "    return count\n"
            "\n"
            "def first_common(head_a, head_b):\n"
            "    len_a = list_length(head_a)\n"
            "    len_b = list_length(head_b)\n"
            "    p = head_a\n"
            "    q = head_b\n"
            "    while len_a > len_b:\n"
            "        p = p.next\n"
            "        len_a -= 1\n"
            "    while len_b > len_a:\n"
            "        q = q.next\n"
            "        len_b -= 1\n"
            "    while p is not None and q is not None:\n"
            "        if p is q:\n"
            "            return p\n"
            "        p = p.next\n"
            "        q = q.next\n"
            "    return None\n"
            "\n"
            "common = Node(6, Node(7))\n"
            "head_a = Node(1, Node(2, common))\n"
            "head_b = Node(3, common)\n"
            "print(first_common(head_a, head_b).val)\n"
            "print(first_common(Node(1, Node(2)), Node(1, Node(2))))\n"
            "print(first_common(None, head_a))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "_tail = Node(6, Node(7))\n_a = Node(1, Node(2, _tail))\n_b = Node(3, _tail)\nassert first_common(_a, _b) is _tail, '公共部分从 6 开始，应返回那个结点对象，实际 %r' % (_to_list(first_common(_a, _b)),)",
            "assert first_common(_build([1, 2, 3]), _build([1, 2, 3])) is None, '值相同但结点不同不算公共结点，应返回 None'",
            "_c = _build([1, 2, 3])\nassert first_common(_c, _c) is _c, '两条链表就是同一条时应返回它的头结点'",
            "assert first_common(None, _build([1])) is None and first_common(None, None) is None, '有链表为空时应返回 None'",
            "_t = Node(9)\n_x = _t\n_y = Node(4, _t)\nassert first_common(_x, _y) is _t, '公共结点是第一条链表的头结点时也要能找出来'",
            "_t = Node(5)\n_p = Node(1, Node(2, _t))\n_q = Node(3, Node(4, _t))\nassert first_common(_p, _q) is _t, '公共部分只有一个结点时也要找对，实际 %r' % (_to_list(first_common(_p, _q)),)",
            "_t = Node(999)\n_u = Node(1, _t)\n_v = Node(2, _t)\nassert first_common(_u, _v) is _t, '两个结点共用一个尾结点也算公共结点'",
            "_t = Node(7, Node(8))\n_long = _t\nfor _i in range(50):\n    _long = Node(_i, _long)\n_short = Node(100, _t)\nassert first_common(_long, _short) is _t, '长度差 49 的两条链表要先把长的走齐再找（公共结点是 7）'",
            "_t = Node(3, Node(4, Node(5)))\n_a1 = Node(1, _t)\n_b1 = Node(2, Node(9, _t))\nassert first_common(_a1, _b1) is _t, '第一条更短时（对齐的另一个分支）也要找对'",
            "assert first_common(_build([1, 2]), _build([3, 4, 5])) is None, '完全没有公共结点应返回 None'",
        ],
        'explanation': (
            '两条链表如果有公共结点，那么从第一个公共结点开始，后面的部分**完全重合**——'
            '因为每个结点只有一个 `next`，分叉后再也合不回去（合得上就是同一个结点了）。'
            '也就是说「公共」意味着**同一条尾巴**，而不是「某个值恰好相等」。\n\n'
            '既然尾巴一样，那么让两个指针**站在离尾部同样远的位置**同步前进，'
            '相遇点就是第一个公共结点。步骤：\n\n'
            '```python\n'
            'while len_a > len_b:\n'
            '    p = p.next; len_a -= 1\n'
            'while len_b > len_a:\n'
            '    q = q.next; len_b -= 1\n'
            'while p is not None and q is not None:\n'
            '    if p is q:\n'
            '        return p\n'
            '    p = p.next; q = q.next\n'
            'return None\n'
            '```\n\n'
            '**常见错误**：\n\n'
            '1. 比较 `p.val == q.val`：`[1, 2, 3]` 和另一条 `[1, 2, 3]` 会被误判成有公共结点；\n'
            '2. 对齐后忘记同步前进，或者只移动了一个指针；\n'
            '3. 用集合记录第一条链表的结点再扫第二条——答案对，但空间 O(n)，'
            '   本题的考点正是 O(1) 空间。\n\n'
            '复杂度：时间 O(m + n)（数长度两趟 + 同步走一趟）、额外空间 O(1)。'
        ),
        'expected_output': '6\nNone\nNone',
        'hints': ['先求出两条链表的长度，让较长的先走差值的步数', '相遇的判据是 p is q（同一个结点对象），不是值相等'],
    },
    {
        'id': 'n408-009',
        'track': 'algorithm',
        'chapter_id': 118,
        'chapter_title': '链表算法',
        'topic': '链表算法',
        'title': '按序号奇偶拆分单链表',
        'difficulty': 2,
        'tags': ['单链表', '拆分', '复用结点'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `split_odd_even(head)`：把单链表按结点的**序号**'
            '（第 1 个结点序号为 1，依此类推，与值的大小无关）拆成两条链表：\n\n'
            '- 奇数序号的结点按**原相对顺序**连成 A；\n'
            '- 偶数序号的结点按**原相对顺序**连成 B；\n'
            '- 返回 `(head_a, head_b)`，其中某条链一个结点都没有时返回 `None`。\n\n'
            '要求：\n\n'
            '- **复用原来的结点**（只改 `next` 指针，不要新建结点、不要把值拷进新链表）；\n'
            '- 时间 O(n)、额外空间 O(1)；建议用两个「尾巴」指针 `tail_a`、`tail_b`：'
            '一边走一边把当前结点挂到对应链表的尾部，第一次挂的时候顺便记住链表头；\n'
            '- 别忘了先把 `current.next` 存下来再摘结点，否则走不下去。\n\n'
            '最后把 `1 → 2 → 3 → 4 → 5` 拆开、分别打印两条链表的值，'
            '再打印空链表和单结点链表的结果。'
        ),
        'starter_code': 'def split_odd_even(head):\n    head_a = tail_a = None\n    head_b = tail_b = None\n    # index 从 1 开始，按奇偶挂到两条链表的尾部\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def split_odd_even(head):\n"
            "    head_a = None\n"
            "    head_b = None\n"
            "    tail_a = None\n"
            "    tail_b = None\n"
            "    current = head\n"
            "    index = 1\n"
            "    while current is not None:\n"
            "        nxt = current.next\n"
            "        current.next = None\n"
            "        if index % 2 == 1:\n"
            "            if head_a is None:\n"
            "                head_a = current\n"
            "            else:\n"
            "                tail_a.next = current\n"
            "            tail_a = current\n"
            "        else:\n"
            "            if head_b is None:\n"
            "                head_b = current\n"
            "            else:\n"
            "                tail_b.next = current\n"
            "            tail_b = current\n"
            "        current = nxt\n"
            "        index += 1\n"
            "    return head_a, head_b\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    while head is not None:\n"
            "        out.append(head.val)\n"
            "        head = head.next\n"
            "    return out\n"
            "\n"
            "odd, even = split_odd_even(Node(1, Node(2, Node(3, Node(4, Node(5))))))\n"
            "print(values_of(odd), values_of(even))\n"
            "empty_odd, empty_even = split_odd_even(None)\n"
            "print(empty_odd, empty_even)\n"
            "one_odd, one_even = split_odd_even(Node(9))\n"
            "print(values_of(one_odd), values_of(one_even))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "_a, _b = split_odd_even(None)\nassert _a is None and _b is None, '空链表应返回 (None, None)'",
            "_a, _b = split_odd_even(_build([9]))\nassert _to_list(_a) == [9] and _b is None, '只有一个结点时 A 是 [9]、B 是 None'",
            "_a, _b = split_odd_even(_build([1, 2]))\nassert _to_list(_a) == [1] and _to_list(_b) == [2], '两个结点应拆成 [1] 和 [2]，实际 %r / %r' % (_to_list(_a), _to_list(_b))",
            "_a, _b = split_odd_even(_build([1, 2, 3, 4, 5]))\nassert _to_list(_a) == [1, 3, 5] and _to_list(_b) == [2, 4], '五个结点应拆成 [1, 3, 5] 和 [2, 4]，实际 %r / %r' % (_to_list(_a), _to_list(_b))",
            "_a, _b = split_odd_even(_build([1, 2, 3, 4, 5, 6]))\nassert _to_list(_a) == [1, 3, 5] and _to_list(_b) == [2, 4, 6], '偶数个结点时两条链表一样长，实际 %r / %r' % (_to_list(_a), _to_list(_b))",
            "_a, _b = split_odd_even(_build([7, 7, 7, 7]))\nassert _to_list(_a) == [7, 7] and _to_list(_b) == [7, 7], '值全都相同时按序号（不是按值）拆，实际 %r / %r' % (_to_list(_a), _to_list(_b))",
            "_head = _build([1, 2, 3, 4])\n_a, _b = split_odd_even(_head)\nassert _a is _head, '要求复用原来的结点：奇数链的头应当还是原来的头结点对象'",
            "_head = _build(list(range(1, 8)))\n_a, _b = split_odd_even(_head)\nassert len(_to_list(_a)) + len(_to_list(_b)) == 7, '拆分后两条链表的结点总数应等于原来的 7 个（不能丢结点）'",
            "_a, _b = split_odd_even(_build(list(range(101))))\nassert _to_list(_a) == list(range(0, 101, 2)) and _to_list(_b) == list(range(1, 101, 2)), '101 个结点（0~100）应拆成 51 个偶数序号和 50 个奇数序号'",
        ],
        'explanation': (
            '拆分的核心是「**尾插法**」：维护两条链表的尾巴指针，把摘下来的结点接到对应尾巴后面。\n\n'
            '```python\n'
            'nxt = current.next        # 先记路\n'
            'current.next = None       # 摘下来（也可以不写，最后会被覆盖）\n'
            'if index % 2 == 1:\n'
            '    if head_a is None:\n'
            '        head_a = current  # 第一个结点，顺便记头\n'
            '    else:\n'
            '        tail_a.next = current\n'
            '    tail_a = current\n'
            '```\n\n'
            '为什么要先 `nxt = current.next`？因为接下来要改 `current.next`，'
            '一旦改了，就找不到下一个结点了——和逆置链表是同一个坑。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记保存 `nxt`，链表走两步就断；\n'
            '2. 用「按值判断奇偶」代替「按序号判断」（如 `if current.val % 2`），'
            '   题目要的是序号；\n'
            '3. 新建结点把值拷过去——虽然结果看着一样，但失去了链表算法的意义，408 会扣分；\n'
            '4. 忘了把某个链表为空时返回 `None`（不要返回一个 val 为 0 的哨兵结点）。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[1, 3, 5] [2, 4]\nNone None\n[9] []',
        'hints': ['用两个尾巴指针把结点分别挂到两条链表后面', '先存 current.next 再改指针，否则会断链'],
    },
    {
        'id': 'n408-010',
        'track': 'algorithm',
        'chapter_id': 118,
        'chapter_title': '链表算法',
        'topic': '链表算法',
        'title': '判断链表有环并求环的入口结点',
        'difficulty': 3,
        'tags': ['单链表', '快慢指针', 'Floyd'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `detect_cycle_entrance(head)`：如果链表中存在**环**'
            '（某个结点的 `next` 指回了前面出现过的结点），返回**环的入口结点**（那个结点对象）；'
            '没有环、或空链表返回 `None`。\n\n'
            '要求时间 O(n)、额外空间 O(1)，用**快慢指针**：\n\n'
            '1. `slow` 每次走 1 步、`fast` 每次走 2 步。若 `fast` 走到 `None`'
            '（或 `fast.next` 是 `None`），说明没有环，返回 `None`；\n'
            '2. 若两者相遇（`slow is fast`），说明有环：这时把 `slow` 放回**头结点**，\n'
            '3. 两个指针改成**同速**（每次各走 1 步）前进，它们再次相遇的结点就是环的入口。\n\n'
            '不要用集合记录走过的结点（那是 O(n) 额外空间）。\n\n'
            '最后造一个 `1 → 2 → 3 → 4 → 5` 且 `5` 指回 `3` 的带环链表，'
            '打印入口结点的值；再打印一个无环链表和空链表的结果。'
        ),
        'starter_code': 'def detect_cycle_entrance(head):\n    slow = head\n    fast = head\n    # 快慢指针相遇后，把 slow 放回头，两者同速前进再相遇即入口\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def detect_cycle_entrance(head):\n"
            "    slow = head\n"
            "    fast = head\n"
            "    while fast is not None and fast.next is not None:\n"
            "        slow = slow.next\n"
            "        fast = fast.next.next\n"
            "        if slow is fast:\n"
            "            slow = head\n"
            "            while slow is not fast:\n"
            "                slow = slow.next\n"
            "                fast = fast.next\n"
            "            return slow\n"
            "    return None\n"
            "\n"
            "nodes = [Node(1), Node(2), Node(3), Node(4), Node(5)]\n"
            "for i in range(4):\n"
            "    nodes[i].next = nodes[i + 1]\n"
            "nodes[4].next = nodes[2]\n"
            "print(detect_cycle_entrance(nodes[0]).val)\n"
            "print(detect_cycle_entrance(nodes[0]) is nodes[2])\n"
            "print(detect_cycle_entrance(Node(1, Node(2, Node(3)))))\n"
            "print(detect_cycle_entrance(None))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "assert detect_cycle_entrance(None) is None, '空链表应返回 None'",
            "assert detect_cycle_entrance(_build([1])) is None, '单结点且没有自环应返回 None'",
            "assert detect_cycle_entrance(_build([1, 2, 3, 4])) is None, '普通无环链表应返回 None'",
            "_a = _build([1, 2, 3, 4, 5])\nassert detect_cycle_entrance(_a) is None, '长一点的无环链表也要返回 None'",
            "_x = Node(1)\n_x.next = _x\nassert detect_cycle_entrance(_x) is _x, '自环（结点指回自己）的入口就是它自己'",
            "_p, _q, _r = Node(1), Node(2), Node(3)\n_p.next = _q\n_q.next = _r\n_r.next = _p\nassert detect_cycle_entrance(_p) is _p, '整条链是环时入口就是头结点，实际 %r' % (getattr(detect_cycle_entrance(_p), 'val', None),)",
            "_nodes = [Node(1), Node(2), Node(3), Node(4), Node(5)]\nfor _i in range(4):\n    _nodes[_i].next = _nodes[_i + 1]\n_nodes[4].next = _nodes[2]\nassert detect_cycle_entrance(_nodes[0]) is _nodes[2], '5 指回 3 时入口应是结点 3，实际 %r' % (getattr(detect_cycle_entrance(_nodes[0]), 'val', None),)",
            "_x, _y = Node(1), Node(2)\n_x.next = _y\n_y.next = _x\nassert detect_cycle_entrance(_x) is _x, '两个结点互指时入口是头结点'",
            "_tail = Node(99)\n_head = _tail\nfor _i in range(200):\n    _head = Node(_i, _head)\n_tail.next = _head.next\nassert detect_cycle_entrance(_head) is _head.next, '200 个结点的长链、从第二个结点开始成环，入口应是第二个结点'",
            "_nodes = [Node(7), Node(7), Node(7), Node(7)]\nfor _i in range(3):\n    _nodes[_i].next = _nodes[_i + 1]\n_nodes[3].next = _nodes[3]\nassert detect_cycle_entrance(_nodes[0]) is _nodes[3], '值全都相同时要按结点对象判断，入口应是第 4 个结点'",
        ],
        'explanation': (
            '先解决「有没有环」：让慢指针每次走 1 步、快指针每次走 2 步。'
            '如果有环，快指针会先进入环里绕圈，迟早从后面追上慢指针（相对速度 1 步/轮）；'
            '如果没环，快指针会先到达 `None`。\n\n'
            '**为什么相遇后能这样找入口？** 设头到入口的距离为 a，入口到相遇点的距离为 b，'
            '环长为 L。相遇时慢指针走了 `a + b`，快指针走了 `a + b + kL`，'
            '而快指针走的路程是慢指针的两倍，于是 `a + b = kL`，即 `a = kL − b`。\n\n'
            '这式子的意思是：**从相遇点绕环往前走 kL − b 步（效果等于从相遇点继续走到入口）'
            '和从头结点走 a 步到入口，路程一样**。'
            '所以把一个指针放回头结点、两者同速前进，相遇处正是入口。\n\n'
            '```python\n'
            'while fast is not None and fast.next is not None:\n'
            '    slow = slow.next\n'
            '    fast = fast.next.next\n'
            '    if slow is fast:\n'
            '        slow = head\n'
            '        while slow is not fast:\n'
            '            slow = slow.next\n'
            '            fast = fast.next\n'
            '        return slow\n'
            'return None\n'
            '```\n\n'
            '**常见错误**：循环条件只写 `fast is not None`，'
            '`fast.next.next` 会对 `None` 取属性而报错，必须同时检查 `fast.next`；'
            '另外第二阶段千万不要再让快指针走两步。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '3\nTrue\nNone\nNone',
        'hints': ['快指针每次 2 步、慢指针 1 步，相遇说明有环', '相遇后把慢指针放回头结点，两者同速再走，相遇点就是入口'],
    },
    # ── 专题 119 树与二叉树算法 ───────────────────────────
    {
        'id': 'n408-011',
        'track': 'algorithm',
        'chapter_id': 119,
        'chapter_title': '树与二叉树算法',
        'topic': '树与二叉树算法',
        'title': '二叉树非递归中序遍历（手写栈）',
        'difficulty': 1,
        'tags': ['二叉树', '中序遍历', '栈'],
        'statement': (
            '请**按下面的定义**写好二叉树结点类（属性名必须一致）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `inorder_iter(root)`：用**自己的栈**实现中序遍历'
            '（访问顺序：左 → 根 → 右），返回访问到的值组成的列表；空树返回 `[]`。\n\n'
            '要求：\n\n'
            '- **不许用递归**（也不要用 `sys.setrecursionlimit` 去绕），只能用列表当栈；\n'
            '- 经典写法：从根出发，一路向左把沿途结点压栈，直到 `None`；'
            '然后弹出栈顶（它就是当前最深、最左、还没访问的结点），把它的值写进结果，'
            '再转向它的右子树，继续重复上面的过程；\n'
            '- 循环条件是 `while node is not None or stack:`——栈非空时也不能停。\n\n'
            '最后构造 `4(2(1, 3), 6(5, 7))`（就写成 '
            '`TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))`），'
            '打印它的中序结果；再打印空树和一个「一直往左」的斜树 `3(2(1))` 的结果。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder_iter(root):\n    result = []\n    stack = []\n    # 一路向左压栈；弹出即访问，然后转向右子树\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def inorder_iter(root):\n"
            "    result = []\n"
            "    stack = []\n"
            "    node = root\n"
            "    while node is not None or stack:\n"
            "        while node is not None:\n"
            "            stack.append(node)\n"
            "            node = node.left\n"
            "        node = stack.pop()\n"
            "        result.append(node.val)\n"
            "        node = node.right\n"
            "    return result\n"
            "\n"
            "tree = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))\n"
            "print(inorder_iter(tree))\n"
            "print(inorder_iter(None))\n"
            "print(inorder_iter(TreeNode(3, TreeNode(2, TreeNode(1)))))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert inorder_iter(None) == [], '空树应返回 []'",
            "assert inorder_iter(TreeNode(1)) == [1], '只有一个根结点时应返回 [1]'",
            "assert inorder_iter(TreeNode(1, TreeNode(2), TreeNode(3))) == [2, 1, 3], '左 2 右 3 的树中序应是 [2, 1, 3]，实际 %r' % (inorder_iter(TreeNode(1, TreeNode(2), TreeNode(3))),)",
            "_root = _tree([4, 2, 6, 1, 3, 5, 7])\nassert inorder_iter(_root) == [1, 2, 3, 4, 5, 6, 7], '中序应是 [1, 2, 3, 4, 5, 6, 7]，实际 %r' % (inorder_iter(_root),)",
            "assert inorder_iter(_tree([3, 2, None, 1])) == [1, 2, 3], '一直往左的斜树中序是 [1, 2, 3]，实际 %r' % (inorder_iter(_tree([3, 2, None, 1])),)",
            "assert inorder_iter(_tree([1, None, 2, None, 3])) == [1, 2, 3], '一直往右的斜树中序是 [1, 2, 3]，实际 %r' % (inorder_iter(_tree([1, None, 2, None, 3])),)",
            "assert inorder_iter(_tree([2, 2, 2])) == [2, 2, 2], '值全部相同时每个结点都要访问一次，实际 %r' % (inorder_iter(_tree([2, 2, 2])),)",
            "_full = _tree(list(range(1, 16)))\nassert inorder_iter(_full) == [8, 4, 9, 2, 10, 5, 11, 1, 12, 6, 13, 3, 14, 7, 15], '满二叉树的中序不对：%r' % (inorder_iter(_full),)",
            "_node = TreeNode(0)\nfor _i in range(1, 1500):\n    _node = TreeNode(_i, _node)\nassert inorder_iter(_node) == list(range(1500)), '1500 层深的左斜树也必须能走完（这题不许用递归）'",
        ],
        'explanation': (
            '递归版中序只有三行，但它把「回来的位置」交给系统递归栈保管。'
            '改成非递归，就得用**自己的栈**显式模拟这件事：\n\n'
            '```python\n'
            'while node is not None or stack:\n'
            '    while node is not None:      # 一路向左，沿途压栈\n'
            '        stack.append(node)\n'
            '        node = node.left\n'
            '    node = stack.pop()           # 弹出来就是该访问的结点\n'
            '    result.append(node.val)\n'
            '    node = node.right            # 右子树重复同样过程\n'
            '```\n\n'
            '**为什么弹出栈顶就能访问？** 因为这一路压栈的都是「自己还没被访问、'
            '但左子树已经走到底」的结点，栈顶就是最深最左的那个，'
            '它的左子树要么为空、要么已经访问完，按「左 → 根 → 右」正是轮到它。\n\n'
            '**常见错误**：\n\n'
            '1. 循环条件只写 `while node is not None`，弹出一次就结束了；\n'
            '2. 弹出后忘记转向右子树（`node = node.right`），结果只访问了最左边一条链；\n'
            '3. 访问完右子树后忘了重新「一路向左」——必须回到内层 while，'
            '   不能直接把右孩子当新根往下走。\n\n'
            '复杂度：时间 O(n)（每个结点进栈出栈各一次）、空间 O(h)（h 是树高，最坏 O(n)）。'
        ),
        'expected_output': '[1, 2, 3, 4, 5, 6, 7]\n[]\n[1, 2, 3]',
        'hints': ['一路向左压栈，直到 None', '弹出栈顶就是要访问的结点，访问后转向它的右子树'],
    },
    {
        'id': 'n408-012',
        'track': 'algorithm',
        'chapter_id': 119,
        'chapter_title': '树与二叉树算法',
        'topic': '树与二叉树算法',
        'title': '求二叉树的宽度（层序统计每层结点数）',
        'difficulty': 2,
        'tags': ['二叉树', '层序遍历', '队列'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `tree_width(root)`：返回二叉树的**宽度**，'
            '也就是**结点数最多的那一层**的结点个数；空树返回 0。\n\n'
            '要求用**层序遍历**（队列），时间 O(n)、空间 O(宽度)：\n\n'
            '- 每轮开始时先记下当前队列长度 `level_size`，它就是这一层的结点个数，'
            '用它更新最大值；\n'
            '- 然后**整好处理这么多结点**（`for _ in range(level_size)`），'
            '一边处理一边把它们的左右孩子入队；\n'
            '- 这一轮处理完，队列里恰好全是下一层的结点。\n\n'
            '不要用「给每个结点记一个层号、再统计每层多少个」的写法'
            '（结果也对，但多存了很多信息）。\n\n'
            '最后打印 `1(2(4, 5), 3(6, 7))`（宽度 4）、空树（0）、单结点树（1）的结果，'
            '再打印一个「越往下一层越宽」的树 `1(2(4), 3)`（宽度 2）的结果。'
        ),
        'starter_code': 'def tree_width(root):\n    if root is None:\n        return 0\n    queue = [root]\n    best = 0\n    # 每轮先取 len(queue) 作为这一层的结点数，再整好处理这么多结点\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def tree_width(root):\n"
            "    if root is None:\n"
            "        return 0\n"
            "    queue = [root]\n"
            "    best = 0\n"
            "    while queue:\n"
            "        level_size = len(queue)\n"
            "        if level_size > best:\n"
            "            best = level_size\n"
            "        for _ in range(level_size):\n"
            "            node = queue.pop(0)\n"
            "            if node.left is not None:\n"
            "                queue.append(node.left)\n"
            "            if node.right is not None:\n"
            "                queue.append(node.right)\n"
            "    return best\n"
            "\n"
            "tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\n"
            "print(tree_width(tree))\n"
            "print(tree_width(None))\n"
            "print(tree_width(TreeNode(1)))\n"
            "print(tree_width(TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert tree_width(None) == 0, '空树宽度是 0'",
            "assert tree_width(TreeNode(1)) == 1, '只有一个根结点时宽度是 1'",
            "assert tree_width(TreeNode(1, TreeNode(2), None)) == 1, '一条只有左孩子的链，每层都只有 1 个结点'",
            "assert tree_width(_tree([1, 2, 3])) == 2, '根加两个孩子宽度是 2，实际 %r' % (tree_width(_tree([1, 2, 3])),)",
            "assert tree_width(_tree([1, 2, 3, 4, 5, 6, 7])) == 4, '三层满二叉树第三层有 4 个结点，实际 %r' % (tree_width(_tree([1, 2, 3, 4, 5, 6, 7])),)",
            "assert tree_width(_tree([1, 2, 3, 4])) == 2, '第 2 层 2 个、第 3 层 1 个，宽度应是 2，实际 %r' % (tree_width(_tree([1, 2, 3, 4])),)",
            "assert tree_width(_tree([1, None, 2, None, 3])) == 1, '右斜树每层只有 1 个结点，实际 %r' % (tree_width(_tree([1, None, 2, None, 3])),)",
            "_left = TreeNode(1, TreeNode(2, TreeNode(3, TreeNode(4, TreeNode(5)))))\nassert tree_width(_left) == 1, '一直往左的深链宽度是 1，实际 %r' % (tree_width(_left),)",
            "_mixed = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\nassert tree_width(_mixed) == 4, '满三层的树宽度是 4，实际 %r' % (tree_width(_mixed),)",
            "_nodes = [TreeNode(_i) for _i in range(200)]\nfor _i in range(99):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\n_nodes[99].left = _nodes[199]\nassert tree_width(_nodes[0]) == 73, '200 个结点的完全二叉树最后一层有 73 个结点，实际 %r' % (tree_width(_nodes[0]),)",
            "_deep = TreeNode(0)\nfor _i in range(1, 400):\n    _deep = TreeNode(_i, _deep)\nassert tree_width(_deep) == 1, '400 层深的斜树宽度仍是 1'",
        ],
        'explanation': (
            '「宽度」按层统计，层序遍历是天然的工具。关键技巧是：\n\n'
            '**进循环时先量一次队列长度**，它正好是这一层还没出队的结点个数：\n\n'
            '```python\n'
            'while queue:\n'
            '    level_size = len(queue)      # 这一层有多少个结点\n'
            '    best = max(best, level_size)\n'
            '    for _ in range(level_size):  # 只处理这一层的结点\n'
            '        node = queue.pop(0)\n'
            '        if node.left:  queue.append(node.left)\n'
            '        if node.right: queue.append(node.right)\n'
            '```\n\n'
            '`for _ in range(level_size)` 把「这一层」和「下一层」分开：'
            '循环里新入队的孩子都排在队尾，不会被这一轮处理到。\n\n'
            '**常见错误**：\n\n'
            '1. 写成 `while queue:` + 逐个出队、不区分层，结果算出来的是结点总数；\n'
            '2. 用 `len(queue)` 直接当层大小但把新孩子也算进去'
            '（把 `level_size` 写成在循环里实时 `len(queue)`），层就串了；\n'
            '3. 忘记 `queue.pop(0)` 的 O(n) 代价——数据量大时用 `collections.deque` 的 '
            '`popleft()` 更标准（本题数据规模下两种都行）。\n\n'
            '复杂度：时间 O(n)（每个结点入队出队各一次）、额外空间 O(宽度)。'
        ),
        'expected_output': '4\n0\n1\n2',
        'hints': ['每轮先记住 len(queue) 作为这一层的结点数', '用 for _ in range(level_size) 整好处理这一层'],
    },
    {
        'id': 'n408-013',
        'track': 'algorithm',
        'chapter_id': 119,
        'chapter_title': '树与二叉树算法',
        'topic': '树与二叉树算法',
        'title': '判断二叉树是否是完全二叉树',
        'difficulty': 2,
        'tags': ['二叉树', '完全二叉树', '层序遍历'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `is_complete(root)`：判断二叉树是不是**完全二叉树**，'
            '是返回 `True`，不是返回 `False`；**空树算完全二叉树**（返回 `True`）。\n\n'
            '完全二叉树的判定口径（按层序看）：把所有结点按层序排好，'
            '只要出现了**空位**，后面就再也不能有结点。\n\n'
            '要求用队列做层序遍历，队列里**允许放 `None`**：\n\n'
            '- 出队一个结点，如果它是 `None`，把标志 `seen_none` 记为 True；\n'
            '- 如果它是非空结点，而 `seen_none` 已经是 True，说明「空位后面又冒出了结点」，'
            '  直接返回 `False`；\n'
            '- 非空结点的左、右孩子**都要入队（哪怕是 None）**，这样空位才不会被跳过。\n\n'
            '最后打印满二叉树 `1(2(4, 5), 3(6, 7))`、'
            '`1(2(4), 3(None, 7))`（3 只有右孩子）、'
            '`1(None, 3)`（根没有左孩子）和空树的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef is_complete(root):\n    queue = deque([root])\n    seen_none = False\n    # 遇到 None 就置 seen_none；再遇到非空结点就说明有空位，返回 False\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def is_complete(root):\n"
            "    queue = deque([root])\n"
            "    seen_none = False\n"
            "    while queue:\n"
            "        node = queue.popleft()\n"
            "        if node is None:\n"
            "            seen_none = True\n"
            "            continue\n"
            "        if seen_none:\n"
            "            return False\n"
            "        queue.append(node.left)\n"
            "        queue.append(node.right)\n"
            "    return True\n"
            "\n"
            "full = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\n"
            "print(is_complete(full))\n"
            "print(is_complete(TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3, None, TreeNode(7)))))\n"
            "print(is_complete(TreeNode(1, None, TreeNode(3))))\n"
            "print(is_complete(None))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert is_complete(None) is True, '空树算完全二叉树'",
            "assert is_complete(TreeNode(1)) is True, '只有一个根结点是完全二叉树'",
            "assert is_complete(_tree([1, 2, 3, 4, 5, 6, 7])) is True, '三层满二叉树是完全二叉树'",
            "assert is_complete(_tree([1, 2, 3, 4, 5])) is True, '1(2(4, 5), 3) 编号连续，是完全二叉树'",
            "assert is_complete(_tree([1, 2, 3, 4])) is True, '1(2(4), 3) 也是完全二叉树，实际 %r' % (is_complete(_tree([1, 2, 3, 4])),)",
            "assert is_complete(_tree([1, None, 3])) is False, '根没有左孩子却有右孩子，不是完全二叉树'",
            "assert is_complete(_tree([1, 2, None, 3])) is False, '左孩子连在 2 上、却跳过了 3 的位置，不是完全二叉树'",
            "assert is_complete(_tree([1, 2, 3, None, 5])) is False, '2 只有右孩子时编号出现空位，不是完全二叉树'",
            "assert is_complete(TreeNode(1, TreeNode(2, TreeNode(4, TreeNode(8), TreeNode(9)), TreeNode(5)), TreeNode(3, TreeNode(6)))) is False, '第 4 层左边连了两个、右边只连一个，编号不连续'",
            "assert is_complete(TreeNode(1, None, TreeNode(2, None, TreeNode(3)))) is False, '一直往右的斜树不是完全二叉树'",
            "assert is_complete(TreeNode(1, TreeNode(2, TreeNode(3)))) is False, '一直往左的斜树（1→2→3）也不是完全二叉树，因为 1 的右孩子位置空了'",
            "_nodes = [TreeNode(_i) for _i in range(200)]\nfor _i in range(99):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\n_nodes[99].left = _nodes[199]\nassert is_complete(_nodes[0]) is True, '200 个结点的完全二叉树（堆的形状）应判定为完全二叉树'",
            "_nodes = [TreeNode(_i) for _i in range(200)]\nfor _i in range(99):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\n_nodes[99].left = _nodes[199]\n_nodes[74].right = None\nassert is_complete(_nodes[0]) is False, '挖掉中间一个结点后编号出现空位，应判定为不是完全二叉树'",
        ],
        'explanation': (
            '完全二叉树的定义是「按层序编号后，结点占满了前面的编号，中间不空」。'
            '换成一个可以直接写代码的判据：**层序遍历时，一旦遇到空位，后面不能再出现结点**。\n\n'
            '所以层序队列要**把 None 也入队**，否则空位被跳过、判据就失效了：\n\n'
            '```python\n'
            'queue = deque([root])\n'
            'seen_none = False\n'
            'while queue:\n'
            '    node = queue.popleft()\n'
            '    if node is None:\n'
            '        seen_none = True\n'
            '        continue\n'
            '    if seen_none:\n'
            '        return False          # 空位之后又出现了结点\n'
            '    queue.append(node.left)\n'
            '    queue.append(node.right)\n'
            'return True\n'
            '```\n\n'
            '注意这里**不做「叶子结点就不入队」的优化**：只有把两个孩子无条件入队，'
            '空位才会真的出现在队列里。\n\n'
            '**常见错误**：\n\n'
            '1. 只检查「有没有孩子」：`1(None, 3)` 这种「缺左孩子、有右孩子」的情况最容易漏判；\n'
            '2. 只判断了「只有左孩子」的结点后面还有没有结点，忘记处理「左右都没有」之后的情况；\n'
            '3. 空树返回 False（题面明确要求 True）。\n\n'
            '复杂度：时间 O(n)、额外空间 O(n)（队列最坏装一层结点，约 n/2 个）。'
        ),
        'expected_output': 'True\nFalse\nFalse\nTrue',
        'hints': ['队列里连 None 一起放，空位才会被看见', '遇到第一个 None 后打标志，再遇到非空结点就返回 False'],
    },
    {
        'id': 'n408-014',
        'track': 'algorithm',
        'chapter_id': 119,
        'chapter_title': '树与二叉树算法',
        'topic': '树与二叉树算法',
        'title': '二叉树的镜像（就地交换左右子树）',
        'difficulty': 2,
        'tags': ['二叉树', '递归', '原地'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `mirror(root)`：把二叉树**就地**变成它的镜像——'
            '每个结点的左右孩子互换（并且对左右子树也做同样的事），'
            '返回**根结点**；空树返回 `None`。\n\n'
            '要求：\n\n'
            '- **原地修改**传入的这棵树（不要新建一棵镜像树把原树丢在一边）；\n'
            '- 时间 O(n)、额外空间 O(树高)（递归栈），写法是「先交换当前结点的左右孩子，'
            '  再递归处理左右子树」（先递归再交换也等价）；\n'
            '- 不要用「按层把每一层的值倒过来重写」的写法（值一样但拓扑会错，'
            '  比如斜树的层序倒过来根本不是镜像）。\n\n'
            '最后构造 `1(2(4, 5), 3(6, 7))`，镜像后打印它的层序结果'
            '（应为 `[1, 3, 2, 7, 6, 5, 4]`）；再打印空树和单结点树的结果。'
        ),
        'starter_code': 'def mirror(root):\n    if root is None:\n        return None\n    # 交换左右孩子，再递归处理左右子树，最后返回 root\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def mirror(root):\n"
            "    if root is None:\n"
            "        return None\n"
            "    root.left, root.right = root.right, root.left\n"
            "    mirror(root.left)\n"
            "    mirror(root.right)\n"
            "    return root\n"
            "\n"
            "def level_values(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    out = []\n"
            "    queue = [root]\n"
            "    while queue:\n"
            "        node = queue.pop(0)\n"
            "        out.append(node.val)\n"
            "        if node.left is not None:\n"
            "            queue.append(node.left)\n"
            "        if node.right is not None:\n"
            "            queue.append(node.right)\n"
            "    return out\n"
            "\n"
            "tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\n"
            "print(level_values(mirror(tree)))\n"
            "print(mirror(None))\n"
            "single = TreeNode(9)\n"
            "print(level_values(mirror(single)))\n"
        ),
        'checks': [
            "def _levels(root):\n    if root is None:\n        return []\n    out = []\n    queue = [root]\n    while queue:\n        node = queue.pop(0)\n        out.append(node.val)\n        if node.left is not None:\n            queue.append(node.left)\n        if node.right is not None:\n            queue.append(node.right)\n    return out",
            "def _inorder(root):\n    if root is None:\n        return []\n    return _inorder(root.left) + [root.val] + _inorder(root.right)",
            "assert mirror(None) is None, '空树的镜像还是 None'",
            "_single = TreeNode(9)\nassert mirror(_single) is _single and _single.left is None and _single.right is None, '单结点树的镜像还是它自己'",
            "_root = TreeNode(1, TreeNode(2), TreeNode(3))\nassert mirror(_root) is _root, '题面要求原地返回根结点（应返回同一个根对象）'",
            "_root = TreeNode(1, TreeNode(2), TreeNode(3))\nmirror(_root)\nassert _root.left.val == 3 and _root.right.val == 2, '两层的树镜像后左孩子应是 3、右孩子应是 2，实际 %r / %r' % (_root.left.val, _root.right.val)",
            "_t = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\nmirror(_t)\nassert _levels(_t) == [1, 3, 2, 7, 6, 5, 4], '三层满二叉树镜像后的层序应是 [1, 3, 2, 7, 6, 5, 4]，实际 %r' % (_levels(_t),)",
            "_t = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))\nmirror(_t)\nassert _inorder(_t) == [7, 6, 5, 4, 3, 2, 1], '二叉搜索树镜像后中序会变成降序，实际 %r' % (_inorder(_t),)",
            "_chain = TreeNode(1, TreeNode(2, TreeNode(3)))\nmirror(_chain)\nassert _chain.left is None and _chain.right.val == 2 and _chain.right.right.val == 3 and _chain.right.left is None, '一直往左的斜树镜像后应变成一直往右的斜树'",
            "_chain = TreeNode(1, None, TreeNode(2, None, TreeNode(3)))\nmirror(_chain)\nassert _chain.right is None and _chain.left.val == 2 and _chain.left.left.val == 3, '一直往右的斜树镜像后应变成一直往左的斜树'",
            "_t = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))\nmirror(mirror(_t))\nassert _levels(_t) == [4, 2, 6, 1, 3, 5, 7], '镜像两次应当变回原样，实际 %r' % (_levels(_t),)",
            "_chain = TreeNode(0)\nfor _i in range(1, 100):\n    _chain = TreeNode(_i, None, _chain)\nmirror(_chain)\n_depth = 0\n_node = _chain\nwhile _node is not None and _node.left is not None:\n    _node = _node.left\n    _depth += 1\nassert _depth == 99, '100 个结点的右斜链镜像后左链的深度应是 99，实际 %r' % (_depth,)",
        ],
        'explanation': (
            '镜像是递归结构最漂亮的应用之一：**一棵树的镜像 = 交换左右孩子后的子树再各自镜像**。\n\n'
            '```python\n'
            'def mirror(root):\n'
            '    if root is None:\n'
            '        return None\n'
            '    root.left, root.right = root.right, root.left\n'
            '    mirror(root.left)\n'
            '    mirror(root.right)\n'
            '    return root\n'
            '```\n\n'
            '有人会担心：「交换完再递归，`root.left` 已经是原来的右子树了，会不会处理错？」'
            '不会——交换后 `root.left` 正好就是「需要被镜像的那棵子树」，'
            '递归处理的先后顺序不影响结果（交换本身是对称的）。\n\n'
            '**为什么不能只把每层的值倒过来？** 因为镜像交换的是**子树的位置**，'
            '不是值的排列顺序。比如 `1(2(3), None)` 的层序是 `[1, 2, 3]`，'
            '倒过来得到 `[3, 2, 1]`，而真正的镜像应该是 `1(None, 2(None, 3))`，'
            '层序是 `[1, 2, 3]`——值一样但形状完全不同。\n\n'
            '**常见错误**：\n\n'
            '1. 只交换了根结点，忘了递归到子树；\n'
            '2. 忘了 `root is None` 的递归出口，直接崩在空树上；\n'
            '3. 新建结点构造镜像树——题面要求就地。\n\n'
            '复杂度：时间 O(n)、额外空间 O(树高)（最坏是斜树，O(n)）。'
        ),
        'expected_output': '[1, 3, 2, 7, 6, 5, 4]\nNone\n[9]',
        'hints': ['交换左右孩子后再递归处理左右子树', '递归出口是 root is None，直接返回 None'],
    },
    {
        'id': 'n408-015',
        'track': 'algorithm',
        'chapter_id': 119,
        'chapter_title': '树与二叉树算法',
        'topic': '树与二叉树算法',
        'title': '求二叉树的带权路径长度 WPL',
        'difficulty': 3,
        'tags': ['二叉树', 'WPL', '递归', '叶子'],
        'statement': (
            '沿用结点类，结点值就是**权值**（非负整数）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `wpl(root)`：求二叉树的**带权路径长度 WPL**；空树返回 0。\n\n'
            '定义（按统考教材）：WPL = 所有**叶子结点**的「权值 × 该叶子的路径长度」之和。'
            '**路径长度**是从根走到该叶子**经过的边数**：'
            '根的孩子路径长度为 1，根自己若是叶子则路径长度为 0。\n\n'
            '“叶子结点”指的是**没有左孩子、也没有右孩子**的结点，'
            '不要用「值是 0」或「值最小」来判断叶子。\n\n'
            '要求时间 O(n)，两种写法都行：\n\n'
            '- 递归：写辅助函数 `walk(node, depth)`，空结点返回 0；'
            '  是叶子就返回 `node.val * depth`；否则返回左右子树之和；\n'
            '- 非递归：层序遍历时把「结点」和「它的路径长度」一起入队。\n\n'
            '最后打印 `1(2(4, 5), 3)` 的 WPL（应为 4×2 + 5×2 + 3×1 = 21）、'
            '单结点树（叶子的路径长度是 0，所以是 0）和空树（0）的结果。'
        ),
        'starter_code': 'def wpl(root):\n    def walk(node, depth):\n        # 空结点返回 0；叶子返回 val * depth；否则左右相加\n        pass\n    return walk(root, 0)\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def wpl(root):\n"
            "    def walk(node, depth):\n"
            "        if node is None:\n"
            "            return 0\n"
            "        if node.left is None and node.right is None:\n"
            "            return node.val * depth\n"
            "        return walk(node.left, depth + 1) + walk(node.right, depth + 1)\n"
            "    return walk(root, 0)\n"
            "\n"
            "tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))\n"
            "print(wpl(tree))\n"
            "print(wpl(TreeNode(7)))\n"
            "print(wpl(None))\n"
        ),
        'checks': [
            "assert wpl(None) == 0, '空树的 WPL 是 0'",
            "assert wpl(TreeNode(5)) == 0, '只有一个根结点时它也是叶子，但路径长度是 0，所以 WPL = 0'",
            "assert wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))) == 21, '4×2 + 5×2 + 3×1 = 21，实际 %r' % (wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))),)",
            "assert wpl(TreeNode(1, TreeNode(2), TreeNode(3))) == 5, '2×1 + 3×1 = 5，实际 %r' % (wpl(TreeNode(1, TreeNode(2), TreeNode(3))),)",
            "assert wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))) == 44, '三层满二叉树（叶子是 4、5、6、7，路径长度都是 2）应为 44，实际 %r' % (wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))),)",
            "assert wpl(TreeNode(1, TreeNode(2, TreeNode(3)))) == 6, '只有 3 是叶子、路径长度 2，应为 6，实际 %r' % (wpl(TreeNode(1, TreeNode(2, TreeNode(3)))),)",
            "assert wpl(TreeNode(1, None, TreeNode(2, None, TreeNode(3)))) == 6, '一直往右的斜树结果同样是 6，实际 %r' % (wpl(TreeNode(1, None, TreeNode(2, None, TreeNode(3)))),)",
            "assert wpl(TreeNode(1, TreeNode(0), TreeNode(3))) == 3, '权值为 0 的叶子也要算进去（0×1 + 3×1 = 3），实际 %r' % (wpl(TreeNode(1, TreeNode(0), TreeNode(3))),)",
            "assert wpl(TreeNode(0, TreeNode(4), TreeNode(5))) == 9, '内部结点权值是 0 不影响结果（4 + 5 = 9），实际 %r' % (wpl(TreeNode(0, TreeNode(4), TreeNode(5))),)",
            "assert wpl(TreeNode(10, TreeNode(20, TreeNode(30)), TreeNode(40))) == 100, '叶子在不同层：30 的路径长度是 2、40 是 1，30×2 + 40×1 = 100，实际 %r' % (wpl(TreeNode(10, TreeNode(20, TreeNode(30)), TreeNode(40))),)",
            "assert wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, None, TreeNode(6)))) == 30, '三个叶子都在第 3 层，路径长度都是 2：(4 + 5 + 6) × 2 = 30，实际 %r' % (wpl(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, None, TreeNode(6)))),)",
            "_nodes = [TreeNode(_i + 1) for _i in range(63)]\nfor _i in range(31):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\nassert wpl(_nodes[0]) == 7600, '63 个结点的满二叉树（值 1~63）WPL 应是 (32+...+63)×5 = 7600，实际 %r' % (wpl(_nodes[0]),)",
        ],
        'explanation': (
            'WPL 的定义抓两个点即可：**谁是叶子**、**它的路径长度是多少**。'
            '先序遍历时把「当前深度」当参数往下传，天然解决第二个问题：\n\n'
            '```python\n'
            'def walk(node, depth):\n'
            '    if node is None:\n'
            '        return 0\n'
            '    if node.left is None and node.right is None:\n'
            '        return node.val * depth      # 叶子：权值 × 路径长度\n'
            '    return walk(node.left, depth + 1) + walk(node.right, depth + 1)\n'
            '```\n\n'
            '**为什么根的 depth 传 0？** 因为路径长度按「边的条数」算，根到自己是 0 条边。'
            '所以「只有一个根结点」的树 WPL = 0（尽管它也是叶子）。'
            '如果按「层数」算（根为第 1 层）会得到 5 而不是 0，两种口径要看清题目用哪种。\n\n'
            '**叶子要按结构判断**（`left is None and right is None`），'
            '不能按值判断。写 `if node.val == 0` 或 `if node.val < 某值` 都是错的——'
            '值只是权值，和它在树里的位置没关系。\n\n'
            '**常见错误**：\n\n'
            '1. 把非叶子的权值也算进去（408 的 WPL 只统计叶子）；\n'
            '2. depth 忘了加一，或者从 1 开始算，导致整棵树多算一层的量；\n'
            '3. 用「层序遍历 + 累加每层结点值」的写法，把内部结点也累加了。\n\n'
            '复杂度：时间 O(n)（每个结点访问一次）、额外空间 O(树高)。'
        ),
        'expected_output': '21\n0\n0',
        'hints': ['把「当前路径长度」作为递归参数往下传，根传 0', '叶子用 left is None and right is None 判断，不要用值判断'],
    },
    # ── 专题 120 图算法与搜索 ─────────────────────────────
    {
        'id': 'n408-016',
        'track': 'algorithm',
        'chapter_id': 120,
        'chapter_title': '图算法与搜索',
        'topic': '图算法与搜索',
        'title': '邻接表上的深度优先遍历（DFS）',
        'difficulty': 2,
        'tags': ['图', '邻接表', 'DFS'],
        'statement': (
            '图用**邻接表**表示：`graph` 是一个列表，`graph[u]` 是顶点 u 的邻居列表，'
            '顶点编号为 `0 ~ len(graph) - 1`。图是**无向图**（邻接表对称）。\n\n'
            '定义函数 `dfs_order(graph, start)`：返回从顶点 `start` 出发的'
            '**深度优先遍历序列**（访问顺序组成的列表）。\n\n'
            '遍历顺序按统考教材的定义：先访问 `start`；'
            '然后**按 `graph[u]` 里邻居出现的顺序**，遇到第一个还没访问过的邻居就'
            '**立刻深入**下去，把这条路走到底，再回头处理第二个邻居。\n\n'
            '- 空图返回 `[]`；`start` 不在 `0 ~ len(graph) - 1` 范围内（含越界）也返回 `[]`；\n'
            '- 从 `start` 出发到不了的顶点不会出现在结果里（这是遍历，不是连通分量统计）；\n'
            '- **不要修改**传入的 `graph`。\n\n'
            '注意：这个顺序**不能用「把所有邻居一次性压栈」的迭代写法**'
            '（那会把最后一个邻居先访问，顺序和定义不符），'
            '要么写递归，要么压栈时把邻居**倒序**压入。\n\n'
            '最后对 `graph = [[1, 2], [0, 3], [0], [1]]` 打印从 0 出发的结果，'
            '再打印单顶点图 `[[]]`、越界 `start=9`、空图 `[]` 的结果。'
        ),
        'starter_code': 'def dfs_order(graph, start):\n    if not graph or start < 0 or start >= len(graph):\n        return []\n    visited = [False] * len(graph)\n    order = []\n    # 递归：访问 u，然后按 graph[u] 的顺序深入没访问过的邻居\n    pass\n',
        'solution': (
            "def dfs_order(graph, start):\n"
            "    if not graph or start < 0 or start >= len(graph):\n"
            "        return []\n"
            "    visited = [False] * len(graph)\n"
            "    order = []\n"
            "\n"
            "    def walk(u):\n"
            "        visited[u] = True\n"
            "        order.append(u)\n"
            "        for v in graph[u]:\n"
            "            if not visited[v]:\n"
            "                walk(v)\n"
            "\n"
            "    walk(start)\n"
            "    return order\n"
            "\n"
            "graph = [[1, 2], [0, 3], [0], [1]]\n"
            "print(dfs_order(graph, 0))\n"
            "print(dfs_order([[]], 0))\n"
            "print(dfs_order(graph, 9))\n"
            "print(dfs_order([], 0))\n"
        ),
        'checks': [
            "assert dfs_order([], 0) == [], '空图应返回 []'",
            "assert dfs_order([[1], [0]], 5) == [], 'start 越界应返回 []，实际 %r' % (dfs_order([[1], [0]], 5),)",
            "assert dfs_order([[1], [0]], -1) == [], 'start 为负数应返回 []'",
            "assert dfs_order([[]], 0) == [0], '只有一个孤立顶点时应返回 [0]，实际 %r' % (dfs_order([[]], 0),)",
            "assert dfs_order([[1], [0]], 0) == [0, 1], '两个顶点一条边应是 [0, 1]，实际 %r' % (dfs_order([[1], [0]], 0),)",
            "assert dfs_order([[1, 2], [0, 3], [0], [1]], 0) == [0, 1, 3, 2], '经典 4 顶点图从 0 出发应是 [0, 1, 3, 2]，实际 %r' % (dfs_order([[1, 2], [0, 3], [0], [1]], 0),)",
            "assert dfs_order([[1, 2], [0, 3], [0], [1]], 2) == [2, 0, 1, 3], '从 2 出发应是 [2, 0, 1, 3]，实际 %r' % (dfs_order([[1, 2], [0, 3], [0], [1]], 2),)",
            "assert dfs_order([[1, 2, 3], [0], [0], [0]], 0) == [0, 1, 2, 3], '必须按邻接表顺序先深入 1：应是 [0, 1, 2, 3]，实际 %r' % (dfs_order([[1, 2, 3], [0], [0], [0]], 0),)",
            "assert dfs_order([[1, 2], [0, 3, 4], [0], [1], [1]], 0) == [0, 1, 3, 4, 2], '有分支的树形图应是 [0, 1, 3, 4, 2]，实际 %r' % (dfs_order([[1, 2], [0, 3, 4], [0], [1], [1]], 0),)",
            "assert dfs_order([[1], [0], [3], [2]], 0) == [0, 1], '不连通时只输出起点所在的分量，实际 %r' % (dfs_order([[1], [0], [3], [2]], 0),)",
            "assert dfs_order([[0, 1], [0]], 0) == [0, 1], '顶点有自环时也要正常走完，实际 %r' % (dfs_order([[0, 1], [0]], 0),)",
            "_g = [[1], [0]]\ndfs_order(_g, 0)\nassert _g == [[1], [0]], '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_n = 300\n_path = []\nfor _i in range(_n):\n    _nbrs = []\n    if _i > 0:\n        _nbrs.append(_i - 1)\n    if _i < _n - 1:\n        _nbrs.append(_i + 1)\n    _path.append(_nbrs)\nassert dfs_order(_path, 0) == list(range(_n)), '300 个顶点的链应从 0 一直走到 299，实际长度 %r' % (len(dfs_order(_path, 0)),)",
        ],
        'explanation': (
            'DFS 的定义就是递归：**访问 u，然后按邻接表顺序对每个未访问的邻居深入**。\n\n'
            '```python\n'
            'def walk(u):\n'
            '    visited[u] = True\n'
            '    order.append(u)\n'
            '    for v in graph[u]:\n'
            '        if not visited[v]:\n'
            '            walk(v)\n'
            '```\n\n'
            '`visited` 是必须的：无向图里 `u` 的邻居列表一定包含「我刚才从哪来」，'
            '没有访问标记就会来回震荡、栈溢出。\n\n'
            '**为什么不能用「一次性把所有邻居压栈」的写法？** 那样栈里先压进去的邻居会被'
            '压在底下，最后一个邻居先被弹出访问，得到的顺序是「反着来的」，'
            '和教材定义的 DFS 序不一致。要用迭代模拟递归，压栈时要把邻居**倒序**压入。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记标记起点，或标记写在 `for` 之后；\n'
            '2. 空图和越界 `start` 没拦截（`graph[start]` 直接 IndexError）；\n'
            '3. 在遍历里修改了 `graph`（比如删掉走过的边），把输入弄脏。\n\n'
            '复杂度：时间 O(V + E)（每个顶点访问一次、每条边检查两次）、'
            '额外空间 O(V)（visited + 递归栈）。'
        ),
        'expected_output': '[0, 1, 3, 2]\n[0]\n[]\n[]',
        'hints': ['递归走到第一个未访问的邻居，整条路走到底再回头', 'visited 标记要在进入结点时就置上，否则会绕圈'],
    },
    {
        'id': 'n408-017',
        'track': 'algorithm',
        'chapter_id': 120,
        'chapter_title': '图算法与搜索',
        'topic': '图算法与搜索',
        'title': '统计无向图的连通分量个数',
        'difficulty': 2,
        'tags': ['图', '连通分量', 'DFS'],
        'statement': (
            '图用邻接表表示（无向图，`graph[u]` 是顶点 u 的邻居列表，'
            '顶点编号 `0 ~ len(graph) - 1`）。\n\n'
            '定义函数 `count_components(graph)`：返回无向图的**连通分量个数**；空图返回 0。\n\n'
            '要求：\n\n'
            '- 用一个 `visited` 数组，**从编号最小的未访问顶点出发**做一次 DFS/BFS，'
            '把这一片能到达的顶点全部标记；\n'
            '- 每发起一次新的搜索，分量个数就加一；\n'
            '- **孤立的顶点（邻居列表为空）自己算一个连通分量**，别忘了数它；\n'
            '- 时间 O(V + E)、空间 O(V)。\n\n'
            '最后对 `[[1], [0, 2], [1], [], [5], [4]]` 打印结果'
            '（3 个分量：{0, 1, 2}、{3}、{4, 5}），'
            '再打印空表和只有孤立顶点的图 `[[], [], [], []]` 的结果。'
        ),
        'starter_code': 'def count_components(graph):\n    n = len(graph)\n    visited = [False] * n\n    count = 0\n    # 对每个没访问过的顶点发起一次搜索，count 加一\n    pass\n',
        'solution': (
            "def count_components(graph):\n"
            "    n = len(graph)\n"
            "    visited = [False] * n\n"
            "    count = 0\n"
            "    for start in range(n):\n"
            "        if visited[start]:\n"
            "            continue\n"
            "        count += 1\n"
            "        stack = [start]\n"
            "        visited[start] = True\n"
            "        while stack:\n"
            "            u = stack.pop()\n"
            "            for v in graph[u]:\n"
            "                if not visited[v]:\n"
            "                    visited[v] = True\n"
            "                    stack.append(v)\n"
            "    return count\n"
            "\n"
            "print(count_components([[1], [0, 2], [1], [], [5], [4]]))\n"
            "print(count_components([]))\n"
            "print(count_components([[], [], [], []]))\n"
        ),
        'checks': [
            "assert count_components([]) == 0, '空图应返回 0'",
            "assert count_components([[]]) == 1, '只有一个孤立顶点时是 1 个连通分量'",
            "assert count_components([[], []]) == 2, '两个孤立顶点是 2 个连通分量，实际 %r' % (count_components([[], []]),)",
            "assert count_components([[1], [0]]) == 1, '一条边把两个顶点连成 1 个分量，实际 %r' % (count_components([[1], [0]]),)",
            "assert count_components([[1], [0, 2], [1], [], [5], [4]]) == 3, '经典例子应是 3 个分量（{0,1,2}、{3}、{4,5}），实际 %r' % (count_components([[1], [0, 2], [1], [], [5], [4]]),)",
            "assert count_components([[1, 2], [0, 2], [0, 1]]) == 1, '三角形是 1 个分量，实际 %r' % (count_components([[1, 2], [0, 2], [0, 1]]),)",
            "assert count_components([[0]]) == 1, '只有自环的顶点仍是 1 个分量，实际 %r' % (count_components([[0]]),)",
            "assert count_components([[1], [0], [], [], []]) == 4, '一条边加三个孤立顶点应是 4 个分量，实际 %r' % (count_components([[1], [0], [], [], []]),)",
            "assert count_components([[], [], [], []]) == 4, '全是孤立顶点的图分量数等于顶点数，实际 %r' % (count_components([[], [], [], []]),)",
            "assert count_components([[1, 2], [0], [0], [4, 5], [3], [3], []]) == 3, '两个分量加一个孤立顶点应是 3，实际 %r' % (count_components([[1, 2], [0], [0], [4, 5], [3], [3], []]),)",
            "_n = 500\n_path = []\nfor _i in range(_n):\n    _nbrs = []\n    if _i > 0:\n        _nbrs.append(_i - 1)\n    if _i < _n - 1:\n        _nbrs.append(_i + 1)\n    _path.append(_nbrs)\nassert count_components(_path) == 1, '500 个顶点连成一条链时应是 1 个分量，实际 %r' % (count_components(_path),)",
            "assert count_components([[] for _ in range(500)]) == 500, '500 个孤立顶点应是 500 个分量，实际 %r' % (count_components([[] for _ in range(500)]),)",
        ],
        'explanation': (
            '连通分量的统计就一句话：**能一次遍历到达的顶点属于同一个分量**。\n\n'
            '```python\n'
            'for start in range(n):\n'
            '    if visited[start]:\n'
            '        continue\n'
            '    count += 1                 # 找到一个新分量\n'
            '    ... 从 start 出发把这一片全部标记 ...\n'
            '```\n\n'
            '为什么这个循环是对的？因为外层按编号从小到大扫描，'
            '遇到一个没被标记的顶点，说明它和之前所有起点都不连通，'
            '它开的这一次搜索正好覆盖「包含它的整个连通分量」。\n\n'
            '**孤立顶点不能漏**：它的邻居列表是空的，搜索立即结束，'
            '但它照样占一个分量。如果只遍历「有边的顶点」就会少算。\n\n'
            '**常见错误**：\n\n'
            '1. 只从顶点 0 出发遍历一次，统计出来的其实是「0 所在分量的大小」而不是分量个数；\n'
            '2. 忘记标记起点（`visited[start]` 没置 True），搜索又在起点上转圈；\n'
            '3. 用递归 DFS 处理上万个顶点的链——Python 递归深度有限，'
            '   容易 `RecursionError`，大图建议用显式栈。\n\n'
            '复杂度：时间 O(V + E)、额外空间 O(V)。'
        ),
        'expected_output': '3\n0\n4',
        'hints': ['外层扫所有顶点，遇到没访问过的就 count += 1 并搜索一遍', '孤立顶点邻居为空，搜索一次就结束，但它自己算一个分量'],
    },
    {
        'id': 'n408-018',
        'track': 'algorithm',
        'chapter_id': 120,
        'chapter_title': '图算法与搜索',
        'topic': '图算法与搜索',
        'title': '拓扑排序判环（Kahn 算法）',
        'difficulty': 2,
        'tags': ['图', '拓扑排序', '入度', '判环'],
        'statement': (
            '有向图用邻接表表示：`graph[u]` 是顶点 u 的**出边**邻居列表'
            '（顶点编号 `0 ~ len(graph) - 1`，每条边 u → v 表示 v 在 u 的邻居表里）。\n\n'
            '定义函数 `topo_sort(graph)`：返回**任意一个**合法的拓扑排序序列；'
            '如果图里有环（无法拓扑排序）就返回 `[]`；空图也返回 `[]`。\n\n'
            '拓扑排序：把所有顶点排成一列，使得每条有向边 u → v 都满足'
            '「u 排在 v 前面」。\n\n'
            '要求用 **Kahn 算法**（基于入度），时间 O(V + E)、空间 O(V)：\n\n'
            '1. 先统计每个顶点的入度（遍历所有邻接表，被指向一次就加一）；\n'
            '2. 把所有入度为 0 的顶点放进队列；\n'
            '3. 反复取出一个顶点 u 放进答案，把 u 的每个邻居 v 的入度减一，'
            '若 v 的入度变成 0 就让它入队；\n'
            '4. 结束后如果答案里的顶点数少于总顶点数，说明剩下的顶点'
            '互相牵制（有环），返回 `[]`。\n\n'
            '最后打印 `[[1, 2], [3], [3], []]` 的结果'
            '（`[0, 1, 2, 3]` 等几种答案都对）、有环的 `[[1], [2], [0]]` 的结果、'
            '以及空表的结果。'
        ),
        'starter_code': 'def topo_sort(graph):\n    n = len(graph)\n    indegree = [0] * n\n    # 统计入度 → 入度为 0 的入队 → 逐个出队并给邻居减入度\n    pass\n',
        'solution': (
            "def topo_sort(graph):\n"
            "    n = len(graph)\n"
            "    indegree = [0] * n\n"
            "    for u in range(n):\n"
            "        for v in graph[u]:\n"
            "            indegree[v] += 1\n"
            "    queue = [u for u in range(n) if indegree[u] == 0]\n"
            "    order = []\n"
            "    head = 0\n"
            "    while head < len(queue):\n"
            "        u = queue[head]\n"
            "        head += 1\n"
            "        order.append(u)\n"
            "        for v in graph[u]:\n"
            "            indegree[v] -= 1\n"
            "            if indegree[v] == 0:\n"
            "                queue.append(v)\n"
            "    if len(order) < n:\n"
            "        return []\n"
            "    return order\n"
            "\n"
            "print(topo_sort([[1, 2], [3], [3], []]))\n"
            "print(topo_sort([[1], [2], [0]]))\n"
            "print(topo_sort([]))\n"
        ),
        'checks': [
            "def _valid_topo(graph, order):\n    n = len(graph)\n    if len(order) != n or sorted(order) != list(range(n)):\n        return False\n    pos = {v: i for i, v in enumerate(order)}\n    for u in range(n):\n        for v in graph[u]:\n            if not pos[u] < pos[v]:\n                return False\n    return True",
            "assert topo_sort([]) == [], '空图应返回 []'",
            "assert topo_sort([[]]) == [0], '只有一个孤立顶点时应返回 [0]，实际 %r' % (topo_sort([[]]),)",
            "_g = [[1, 2], [3], [3], []]\n_r = topo_sort(_g)\nassert _valid_topo(_g, _r), '拆线图应给出合法拓扑序（每条边都是前面的点指向后面的点），实际 %r' % (_r,)",
            "_g = [[], [], []]\n_r = topo_sort(_g)\nassert _valid_topo(_g, _r), '三个孤立顶点的图随便怎么排都合法，实际 %r' % (_r,)",
            "_g = [[1], [2, 3], [4], [4], []]\n_r = topo_sort(_g)\nassert _valid_topo(_g, _r), '一般 DAG 应给出合法拓扑序，实际 %r' % (_r,)",
            "_g = [[1], [0]]\nassert topo_sort(_g) == [], '0 与 1 互相指向（二元环）应返回 []，实际 %r' % (topo_sort(_g),)",
            "assert topo_sort([[1], [2], [0]]) == [], '三元环应返回 []，实际 %r' % (topo_sort([[1], [2], [0]]),)",
            "assert topo_sort([[0]]) == [], '自环的图无法拓扑排序，应返回 []，实际 %r' % (topo_sort([[0]]),)",
            "assert topo_sort([[1], [0], [3], []]) == [], '有环的顶点加上一条无关的链 2→3，仍应返回 []（不能只输出 2、3）'",
            "_g = [[], [], [0]]\n_r = topo_sort(_g)\nassert _valid_topo(_g, _r), '只有一条边 2→0 的图无环，应给出合法拓扑序（2 必须排在 0 前面），实际 %r' % (_r,)",
            "_g = [[1, 2], [3], [3], []]\n_r = topo_sort(_g)\nassert len(_r) == 4 and _r.index(3) > _r.index(1) and _r.index(3) > _r.index(2), '顶点 3 必须在 1 和 2 之后，实际 %r' % (_r,)",
            "_n = 200\n_g = [[_i + 1] for _i in range(_n - 1)] + [[]]\nassert topo_sort(_g) == list(range(_n)), '200 个顶点的链只能按 0, 1, 2, ... 排列，实际 %r' % (topo_sort(_g)[:5],)",
            "_g = [[1], [2], [3], [4], [0]]\nassert topo_sort(_g) == [], '五元环应返回 []，实际 %r' % (topo_sort(_g),)",
        ],
        'explanation': (
            'Kahn 算法的直觉很朴素：**没有前提的活儿先干**。'
            '入度为 0 的顶点表示「没有任何点要求它排在后面」，可以立刻输出；'
            '输出它之后，它指向的那些顶点的「前提」就少了一个，于是入度减一。\n\n'
            '```python\n'
            'queue = [u for u in range(n) if indegree[u] == 0]\n'
            'while head < len(queue):\n'
            '    u = queue[head]; head += 1\n'
            '    order.append(u)\n'
            '    for v in graph[u]:\n'
            '        indegree[v] -= 1\n'
            '        if indegree[v] == 0:\n'
            '            queue.append(v)\n'
            'if len(order) < n:      # 剩下的顶点入度都不为 0\n'
            '    return []\n'
            '```\n\n'
            '**判环原理**：如果图里有环，环上的顶点入度永远不会降到 0（'
            '每个点都在等环上的前一个点），所以队列迟早空掉，'
            '而答案里的顶点数小于总顶点数——这就是有环的判据。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `queue.pop(0)` 当队列（虽然结果对，但每轮 O(n)，'
            '   教程里的写法常用一个 `head` 下标模拟出队，整体仍是 O(V + E)）；\n'
            '2. 忘记统计入度时把**所有**邻接表都扫一遍，只统计了前半部分；\n'
            '3. 判环写成「边数 >= 顶点数」之类的经验条件——必须用「输出顶点数 < 总顶点数」；\n'
            '4. 有环时返回部分结果（如只输出 2、3），题目要求返回 `[]`。\n\n'
            '复杂度：时间 O(V + E)、额外空间 O(V)。'
        ),
        'expected_output': '[0, 1, 2, 3]\n[]\n[]',
        'hints': ['先算入度，入度为 0 的先入队', '输出一个顶点就给它所有邻居入度减一，最后看输出个数是否等于顶点数'],
    },
    {
        'id': 'n408-019',
        'track': 'algorithm',
        'chapter_id': 120,
        'chapter_title': '图算法与搜索',
        'topic': '图算法与搜索',
        'title': '二分图判定（染色法）',
        'difficulty': 2,
        'tags': ['图', '二分图', '染色', 'BFS'],
        'statement': (
            '无向图用邻接表表示（`graph[u]` 是顶点 u 的邻居列表，邻接表对称，'
            '顶点编号 `0 ~ len(graph) - 1`）。\n\n'
            '定义函数 `is_bipartite(graph)`：判断这个图是不是**二分图**——'
            '能否把所有顶点分成两个集合，使得**每条边的两个端点都在不同集合**里；'
            '是返回 `True`，不是返回 `False`；空图返回 `True`。\n\n'
            '要求用**染色法**（BFS、DFS 都行），时间 O(V + E)、空间 O(V)：\n\n'
            '- 用 `color[v]` 记录颜色（0 / 1），`color[v] == -1` 表示还没染色；\n'
            '- **图可能不连通**，所以要对每个还没染色的顶点都发起一次染色'
            '（每个连通分量分别处理）；\n'
            '- 任选一个没染色的顶点染成 0，然后遍历：每个邻居都要染成'
            '「和自己相反」的颜色；如果某个邻居**已经染过色、而且颜色和自己相同**，'
            '说明出现冲突（一定是奇环），直接返回 `False`；\n'
            '- 自环（`u` 是自己的邻居）必然冲突。\n\n'
            '最后打印四边形 `[[1, 3], [0, 2], [1, 3], [0, 2]]` 的结果、'
            '三角形 `[[1, 2], [0, 2], [0, 1]]` 的结果、空表的结果。'
        ),
        'starter_code': 'def is_bipartite(graph):\n    n = len(graph)\n    color = [-1] * n\n    # 对每个没染色的顶点：染成 0，然后 BFS/DFS 把邻居染成相反色，冲突就返回 False\n    pass\n',
        'solution': (
            "def is_bipartite(graph):\n"
            "    n = len(graph)\n"
            "    color = [-1] * n\n"
            "    for start in range(n):\n"
            "        if color[start] != -1:\n"
            "            continue\n"
            "        color[start] = 0\n"
            "        stack = [start]\n"
            "        while stack:\n"
            "            u = stack.pop()\n"
            "            for v in graph[u]:\n"
            "                if color[v] == -1:\n"
            "                    color[v] = 1 - color[u]\n"
            "                    stack.append(v)\n"
            "                elif color[v] == color[u]:\n"
            "                    return False\n"
            "    return True\n"
            "\n"
            "print(is_bipartite([[1, 3], [0, 2], [1, 3], [0, 2]]))\n"
            "print(is_bipartite([[1, 2], [0, 2], [0, 1]]))\n"
            "print(is_bipartite([]))\n"
        ),
        'checks': [
            "assert is_bipartite([]) is True, '空图是二分图'",
            "assert is_bipartite([[]]) is True, '只有一个顶点的图是二分图'",
            "assert is_bipartite([[], [], []]) is True, '全是孤立顶点的图是二分图'",
            "assert is_bipartite([[1], [0]]) is True, '一条边是二分图'",
            "assert is_bipartite([[1, 3], [0, 2], [1, 3], [0, 2]]) is True, '四边形是二分图（按奇偶层染色即可），实际 %r' % (is_bipartite([[1, 3], [0, 2], [1, 3], [0, 2]]),)",
            "assert is_bipartite([[1, 2], [0, 2], [0, 1]]) is False, '三角形（奇环）不是二分图，实际 %r' % (is_bipartite([[1, 2], [0, 2], [0, 1]]),)",
            "assert is_bipartite([[1], [2], [3], [4], [0]]) is False, '五元环不是二分图，实际 %r' % (is_bipartite([[1], [2], [3], [4], [0]]),)",
            "assert is_bipartite([[1], [2], [3], [4], [5], [0]]) is True, '六元环是二分图，实际 %r' % (is_bipartite([[1], [2], [3], [4], [5], [0]]),)",
            "assert is_bipartite([[0]]) is False, '自环不是二分图，实际 %r' % (is_bipartite([[0]]),)",
            "assert is_bipartite([[0, 1], [0]]) is False, '带自环的图（0 指向自己）不是二分图'",
            "assert is_bipartite([[1], [0], [3], [2]]) is True, '两个独立的二点图合起来仍是二分图'",
            "assert is_bipartite([[1], [0], [3, 4, 5], [2, 4, 5], [2, 3, 5], [2, 3, 4]]) is False, '一个二分分量 + 一个三角形分量：只要有一个分量不行就返回 False'",
            "assert is_bipartite([[1, 2], [0], [0], [4], [3]]) is True, '星形（1-0-2）加一条边（3-4）都是二分图'",
            "_g = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]\nassert is_bipartite(_g) is False, 'K4 的变体（每两个之间都有边）不是二分图，实际 %r' % (is_bipartite(_g),)",
            "_n = 1000\n_g = [[(_i + 1) % _n, (_i - 1) % _n] for _i in range(_n)]\nassert is_bipartite(_g) is True, '1000 元偶环是二分图'",
            "_n = 1001\n_g = [[(_i + 1) % _n, (_i - 1) % _n] for _i in range(_n)]\nassert is_bipartite(_g) is False, '1001 元奇环不是二分图，实际 %r' % (is_bipartite(_g),)",
        ],
        'explanation': (
            '二分图判定的核心是**染色 + 冲突检测**：\n\n'
            '- 每条边的两个端点必须不同色，所以从任意顶点染 0 出发，'
            '它的邻居必须全是 1，邻居的邻居又必须是 0……一层一层交替下去；\n'
            '- 如果在某个时刻发现「一个邻居和当前顶点同色」，就产生了矛盾，'
            '说明存在**奇环**（走一圈回来层数差是奇数），图不是二分图。\n\n'
            '```python\n'
            'for v in graph[u]:\n'
            '    if color[v] == -1:\n'
            '        color[v] = 1 - color[u]   # 染成相反色\n'
            '        stack.append(v)\n'
            '    elif color[v] == color[u]:\n'
            '        return False              # 冲突：奇环\n'
            '```\n\n'
            '**注意不连通的情况**：外层的 `for start in range(n)` 必须扫所有顶点，'
            '每个连通分量单独染。否则「三角形 + 一个孤立顶点」这种图会被误判成二分图。\n\n'
            '**常见错误**：\n\n'
            '1. 只从顶点 0 开始染色，漏掉其它连通分量；\n'
            '2. 冲突判断写成 `color[v] == -1`（那是「还没染色」的分支），'
            '   两个分支写反；\n'
            '3. 用「把邻居和自己染成同色」的写法——那就永远检测不出冲突；\n'
            '4. 自环没有特判也能被这套逻辑自动发现（自己和自己同色），'
            '   但如果实现里「已染色就跳过」，自环就会被漏掉。\n\n'
            '复杂度：时间 O(V + E)、额外空间 O(V)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['邻居必须染成和自己相反的颜色', '每个连通分量都要处理：外层扫所有没染色的顶点'],
    },
    {
        'id': 'n408-020',
        'track': 'algorithm',
        'chapter_id': 120,
        'chapter_title': '图算法与搜索',
        'topic': '图算法与搜索',
        'title': 'Dijkstra 单源最短路径',
        'difficulty': 3,
        'tags': ['图', '最短路', 'Dijkstra', '堆'],
        'statement': (
            '带权有向图用邻接表表示：`graph[u]` 是一串 `(邻居, 边权)` 二元组，'
            '边权都是**非负整数**，顶点编号 `0 ~ len(graph) - 1`。\n\n'
            '定义函数 `dijkstra(graph, start)`：返回一个长度等于顶点个数的列表，'
            '第 `i` 个元素是**从 start 到顶点 i 的最短路径长度**；'
            '到不了的顶点记为 `-1`；空图返回 `[]`；`start` 越界也返回 `[]`。\n\n'
            '要求用「贪心 + 松弛」的经典做法（`heapq` 优先队列或 O(V²) 朴素扫描都行）：\n\n'
            '1. `dist[start] = 0`，其余顶点先记为「无穷大」；\n'
            '2. 反复在还没确定的顶点里挑出 `dist` 最小的 u（**贪心选择**：'
            '   因为边权非负，这个值不可能再被改小）；\n'
            '3. 对 u 的每条出边 `(v, w)` 做**松弛**：'
            '   若 `dist[u] + w < dist[v]` 就更新 `dist[v]`；\n'
            '4. 全部处理完后把还是「无穷大」的位置换成 `-1` 返回。\n\n'
            '注意是**有向图**：`graph[u]` 里没有的边就不能走。\n\n'
            '最后打印 `[[(1, 4), (2, 1)], [(3, 1)], [(1, 1), (3, 5)], []]` '
            '从 0 出发的最短距离，再打印单顶点图和空图的结果。'
        ),
        'starter_code': 'import heapq\n\ndef dijkstra(graph, start):\n    n = len(graph)\n    # dist 全为无穷大，dist[start] = 0；用小顶堆反复取最小、松弛\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def dijkstra(graph, start):\n"
            "    n = len(graph)\n"
            "    if n == 0 or start < 0 or start >= n:\n"
            "        return []\n"
            "    dist = [float('inf')] * n\n"
            "    dist[start] = 0\n"
            "    visited = [False] * n\n"
            "    heap = [(0, start)]\n"
            "    while heap:\n"
            "        d, u = heapq.heappop(heap)\n"
            "        if visited[u]:\n"
            "            continue\n"
            "        visited[u] = True\n"
            "        for v, w in graph[u]:\n"
            "            if not visited[v] and d + w < dist[v]:\n"
            "                dist[v] = d + w\n"
            "                heapq.heappush(heap, (dist[v], v))\n"
            "    return [(-1 if value == float('inf') else value) for value in dist]\n"
            "\n"
            "graph = [[(1, 4), (2, 1)], [(3, 1)], [(1, 1), (3, 5)], []]\n"
            "print(dijkstra(graph, 0))\n"
            "print(dijkstra([[]], 0))\n"
            "print(dijkstra([], 0))\n"
        ),
        'checks': [
            "_g = [[(1, 4), (2, 1)], [(3, 1)], [(1, 1), (3, 5)], []]\nassert dijkstra(_g, 0) == [0, 2, 1, 3], '0→2→1→3 是最短的：0→2 花 1、2→1 花 1、1→3 花 1，实际 %r' % (dijkstra(_g, 0),)",
            "assert dijkstra([], 0) == [], '空图应返回 []'",
            "assert dijkstra([[]], 5) == [], 'start 越界应返回 []'",
            "assert dijkstra([[]], 0) == [0], '只有一个孤立顶点时到自己的距离是 0，实际 %r' % (dijkstra([[]], 0),)",
            "assert dijkstra([[(1, 2)], []], 0) == [0, 2], '一条边 0→1 权 2，实际 %r' % (dijkstra([[(1, 2)], []], 0),)",
            "assert dijkstra([[(1, 2)], []], 1) == [-1, 0], '有向图的边不能反向走：从 1 出发到不了 0，实际 %r' % (dijkstra([[(1, 2)], []], 1),)",
            "assert dijkstra([[], []], 0) == [0, -1], '两个无边的顶点，到不了的要记 -1，实际 %r' % (dijkstra([[], []], 0),)",
            "assert dijkstra([[(1, 0)], [(2, 0)], []], 0) == [0, 0, 0], '边权可以是 0，实际 %r' % (dijkstra([[(1, 0)], [(2, 0)], []], 0),)",
            "_g = [[(1, 10), (2, 1)], [(3, 100)], [(3, 5)], []]\nassert dijkstra(_g, 0) == [0, 10, 1, 6], '绕道 0→2→3 只要 6，比 0→1→3 的 110 短，实际 %r' % (dijkstra(_g, 0),)",
            "_g = [[(1, 5), (1, 2)], []]\nassert dijkstra(_g, 0) == [0, 2], '两个顶点之间有两条平行边时要取更短的那条，实际 %r' % (dijkstra(_g, 0),)",
            "_g = [[(1, 7), (2, 9), (5, 14)], [(2, 10), (3, 15)], [(3, 11), (5, 2)], [(4, 6)], [(5, 9)], []]\nassert dijkstra(_g, 0) == [0, 7, 9, 20, 26, 11], '教材里的六顶点例子应是 [0, 7, 9, 20, 26, 11]，实际 %r' % (dijkstra(_g, 0),)",
            "_n = 300\n_g = [[(_i + 1, 1)] for _i in range(_n - 1)] + [[]]\nassert dijkstra(_g, 0) == list(range(_n)), '300 个顶点的链，到第 i 个顶点的距离就是 i，实际末位 %r' % (dijkstra(_g, 0)[-1],)",
            "assert dijkstra([[(1, 2)], []], -1) == [], 'start 为负数应返回 []'",
        ],
        'explanation': (
            'Dijkstra 的骨架是「**反复取最小的未确定顶点 + 松弛它的出边**」。\n\n'
            '```python\n'
            'while heap:\n'
            '    d, u = heapq.heappop(heap)\n'
            '    if visited[u]:\n'
            '        continue            # 同一个顶点可能被压进去多次，取一次就够\n'
            '    visited[u] = True\n'
            '    for v, w in graph[u]:\n'
            '        if not visited[v] and d + w < dist[v]:\n'
            '            dist[v] = d + w\n'
            '            heapq.heappush(heap, (dist[v], v))\n'
            '```\n\n'
            '**为什么贪心是对的？** 因为边权非负，已经确定的最小距离不可能被'
            '「绕远路」改小——任何绕行只会让距离更大。这也是它不能处理负权边的原因'
            '（负权要用 Bellman-Ford / SPFA）。\n\n'
            '`visited` 不做也行（用 `d > dist[u]` 的过期堆顶判断），'
            '但显式标记更直观，也能避免重复松弛。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了「不可达」的位置要转成 `-1`（直接返回 `inf` 会判错）；\n'
            '2. 松弛时写成 `if d + w < w` 之类的笔误，或者漏掉 `dist[v]` 的比较；\n'
            '3. 把有向图当成无向图，反着也走了一遍；\n'
            '4. 用 `heapq` 时把 `(dist[v], v)` 顺序写反——堆是按元组第一个元素比的，'
            '   距离必须放在前面。\n\n'
            '复杂度：优先队列实现 O((V + E) log V)、朴素扫描实现 O(V²)，空间 O(V + E)。'
        ),
        'expected_output': '[0, 2, 1, 3]\n[0]\n[]',
        'hints': ['小顶堆里存 (距离, 顶点)，先取距离最小的', '松弛：dist[u] + w < dist[v] 就更新并入堆；最后把 inf 换成 -1'],
    },
    # ── 专题 121 查找与散列 ───────────────────────────────
    {
        'id': 'n408-021',
        'track': 'algorithm',
        'chapter_id': 121,
        'chapter_title': '查找与散列',
        'topic': '查找与散列',
        'title': '折半查找（迭代版）',
        'difficulty': 1,
        'tags': ['查找', '折半查找', '二分'],
        'statement': (
            '已知一个**升序**顺序表 `items`（元素可能重复）和值 `target`。\n\n'
            '定义函数 `binary_search(items, target)`：\n\n'
            '- 找到就返回 `target` 在表中的**下标**（有重复元素时**任意一个**正确下标都算对，'
            '但要保证 `items[返回的下标] == target`）；\n'
            '- 找不到返回 `-1`；空表返回 `-1`。\n\n'
            '要求**迭代**写法（不要递归），时间 O(log n)、空间 O(1)：\n\n'
            '```python\n'
            'low = 0\n'
            'high = len(items) - 1\n'
            'while low <= high:\n'
            '    mid = (low + high) // 2\n'
            '```\n\n'
            '- `low <= high` 里的 `=` 不能少，否则只剩一个元素时会被漏判；\n'
            '- `items[mid] < target` 时把区间收成右半边（`low = mid + 1`），'
            '否则收成左半边（`high = mid - 1`）；\n'
            '- 中点写成 `(low + high) // 2`，别写 `mid + 1` 之类的自创边界。\n\n'
            '最后打印在 `[1, 3, 5, 7, 9, 11]` 里找 7、找 4，以及空表里找 1 的结果。'
        ),
        'starter_code': 'def binary_search(items, target):\n    low = 0\n    high = len(items) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        # 命中返回 mid，否则砍掉一半\n        pass\n    return -1\n',
        'solution': (
            "def binary_search(items, target):\n"
            "    low = 0\n"
            "    high = len(items) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if items[mid] == target:\n"
            "            return mid\n"
            "        if items[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
            "\n"
            "print(binary_search([1, 3, 5, 7, 9, 11], 7))\n"
            "print(binary_search([1, 3, 5, 7, 9, 11], 4))\n"
            "print(binary_search([], 1))\n"
        ),
        'checks': [
            "assert binary_search([], 5) == -1, '空表应返回 -1'",
            "assert binary_search([5], 5) == 0, '只有一个元素且命中时应返回下标 0'",
            "assert binary_search([5], 4) == -1, '只有一个元素但没命中应返回 -1'",
            "_a = [1, 3, 5, 7, 9, 11]\nassert binary_search(_a, 7) == 3, '7 在下标 3，实际 %r' % (binary_search(_a, 7),)",
            "_a = [1, 3, 5, 7, 9, 11]\nassert binary_search(_a, 1) == 0 and binary_search(_a, 11) == 5, '首尾元素也要能找到，实际 %r / %r' % (binary_search(_a, 1), binary_search(_a, 11))",
            "_a = [1, 3, 5, 7, 9, 11]\nassert binary_search(_a, 4) == -1 and binary_search(_a, 0) == -1 and binary_search(_a, 100) == -1, '不存在的值要返回 -1（比首元素小、比尾元素大都算）'",
            "_b = [1, 2, 3, 4]\nassert binary_search(_b, 1) == 0 and binary_search(_b, 4) == 3 and binary_search(_b, 3) == 2, '偶数长度时每个位置都要能命中，实际 %r' % (binary_search(_b, 3),)",
            "_c = [2, 2, 2, 2]\n_i = binary_search(_c, 2)\nassert _i is not None and 0 <= _i < 4 and _c[_i] == 2, '全表都是重复元素时返回的下标必须落在表内且值等于 target，实际 %r' % (_i,)",
            "_d = [1, 3, 3, 3, 5]\n_i = binary_search(_d, 3)\nassert 0 <= _i < 5 and _d[_i] == 3, '有重复元素时任意一个正确的下标都可以，实际 %r' % (_i,)",
            "_e = [-10, -5, 0, 3]\nassert binary_search(_e, -5) == 1 and binary_search(_e, -6) == -1, '负数同样要能查找，实际 %r' % (binary_search(_e, -5),)",
            "_f = list(range(0, 2000, 2))\nassert binary_search(_f, 1998) == 999, '1000 个元素里查最后一个应是下标 999（循环边界不能差一格），实际 %r' % (binary_search(_f, 1998),)",
            "_f = list(range(0, 2000, 2))\nassert binary_search(_f, 1999) == -1, '查一个不存在的奇数应返回 -1'",
            "_g = list(range(1000))\nassert binary_search(_g, 0) == 0 and binary_search(_g, 999) == 999 and binary_search(_g, 500) == 500, '1000 个元素的首、中、尾都要命中'",
        ],
        'explanation': (
            '折半查找的每一轮都在做同一件事：**看中点，然后扔掉不可能的半边**。\n\n'
            '```python\n'
            'low = 0\n'
            'high = len(items) - 1\n'
            'while low <= high:\n'
            '    mid = (low + high) // 2\n'
            '    if items[mid] == target:\n'
            '        return mid\n'
            '    if items[mid] < target:\n'
            '        low = mid + 1        # 答案只可能在右半边\n'
            '    else:\n'
            '        high = mid - 1       # 答案只可能在左半边\n'
            'return -1\n'
            '```\n\n'
            '**几个必须抠准的细节**：\n\n'
            '1. `while low <= high`：当 `low == high` 时区间里还有**一个**元素，'
            '   必须再比一次，写成 `low < high` 会在「表只剩一个元素且正好是答案」时误返回 -1；\n'
            '2. 收缩边界必须是 `mid ± 1`：`mid` 已经比较过了，留着它会死循环；\n'
            '3. 循环外的 `return -1` 是「区间空了都没找到」的出口。\n\n'
            '折半查找要求**顺序存储 + 有序**，这也是它不能用在链表上的原因'
            '（链表无法 O(1) 取中点）。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '3\n-1\n-1',
        'hints': ['while low <= high 的等号不能丢', '不命中时区间收成 mid + 1 或 mid - 1'],
    },
    {
        'id': 'n408-022',
        'track': 'algorithm',
        'chapter_id': 121,
        'chapter_title': '查找与散列',
        'topic': '查找与散列',
        'title': '找到第一个不小于 target 的位置（下界二分）',
        'difficulty': 2,
        'tags': ['查找', '二分', '下界'],
        'statement': (
            '已知一个**升序**顺序表 `items`（可能有重复元素）和值 `target`。\n\n'
            '定义函数 `lower_bound(items, target)`：返回**第一个值 ≥ target 的元素下标**。\n\n'
            '- 如果所有元素都小于 `target`，返回 `len(items)`；\n'
            '- 空表返回 0；\n'
            '- 例如 `[1, 3, 3, 5]` 中找 3 返回 1（第一个 3 的位置），找 4 返回 3（5 的位置），找 6 返回 4。\n\n'
            '要求手写二分做到 O(log n)（**不要调用 `bisect` 模块**），'
            '关键是**命中时也不能提前返回**，要把区间继续往左压：\n\n'
            '```python\n'
            'left = 0\n'
            'right = len(items)        # 注意右边界是 len(items)，不是 len(items) - 1\n'
            'while left < right:       # 区间是 [left, right) 左闭右开\n'
            '    mid = (left + right) // 2\n'
            '    if items[mid] < target:\n'
            '        left = mid + 1\n'
            '    else:\n'
            '        right = mid\n'
            'return left\n'
            '```\n\n'
            '最后打印 `[1, 3, 3, 5, 8]` 中找 3、找 0、找 9 的结果。'
        ),
        'starter_code': 'def lower_bound(items, target):\n    left = 0\n    right = len(items)\n    # 命中不返回，继续把右边界压到 mid；最后 left 就是答案\n    pass\n',
        'solution': (
            "def lower_bound(items, target):\n"
            "    left = 0\n"
            "    right = len(items)\n"
            "    while left < right:\n"
            "        mid = (left + right) // 2\n"
            "        if items[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid\n"
            "    return left\n"
            "\n"
            "print(lower_bound([1, 3, 3, 5, 8], 3))\n"
            "print(lower_bound([1, 3, 3, 5, 8], 0))\n"
            "print(lower_bound([1, 3, 3, 5, 8], 9))\n"
        ),
        'checks': [
            "assert lower_bound([], 5) == 0, '空表应返回 0'",
            "assert lower_bound([1, 3, 3, 5, 8], 3) == 1, '第一个 3 在下标 1（要返回最左边那个），实际 %r' % (lower_bound([1, 3, 3, 5, 8], 3),)",
            "assert lower_bound([1, 3, 3, 5, 8], 0) == 0, '0 比所有元素都小时返回 0，实际 %r' % (lower_bound([1, 3, 3, 5, 8], 0),)",
            "assert lower_bound([1, 3, 3, 5, 8], 9) == 5, '9 比所有元素都大时返回 len(items) = 5，实际 %r' % (lower_bound([1, 3, 3, 5, 8], 9),)",
            "assert lower_bound([1, 3, 3, 5, 8], 4) == 3, '4 不在表里，第一个 ≥ 4 的是 5（下标 3），实际 %r' % (lower_bound([1, 3, 3, 5, 8], 4),)",
            "assert lower_bound([1, 3, 3, 5, 8], 5) == 3, '找 5 时返回它自己的位置 3，实际 %r' % (lower_bound([1, 3, 3, 5, 8], 5),)",
            "assert lower_bound([1, 3, 3, 5, 8], 1) == 0 and lower_bound([1, 3, 3, 5, 8], 2) == 1, '首元素命中返回 0、比首元素大一点返回 1'",
            "assert lower_bound([7], 7) == 0 and lower_bound([7], 8) == 1 and lower_bound([7], 6) == 0, '单元素表的三种情况'",
            "assert lower_bound([2, 2, 2], 2) == 0 and lower_bound([2, 2, 2], 1) == 0 and lower_bound([2, 2, 2], 3) == 3, '全表重复值的三种情况'",
            "assert lower_bound([1, 2, 2, 2, 3], 2) == 1 and lower_bound([1, 2, 2, 2, 3], 3) == 4, '重复区间的左边界要准，实际 %r / %r' % (lower_bound([1, 2, 2, 2, 3], 2), lower_bound([1, 2, 2, 2, 3], 3))",
            "_a = [_i // 3 for _i in range(30)]\nfor _t in range(-1, 12):\n    assert lower_bound(_a, _t) == sum(1 for _v in _a if _v < _t), 'target = %r 时返回的下标应等于「小于 target 的元素个数」，实际 %r' % (_t, lower_bound(_a, _t))",
            "_big = list(range(0, 200000, 2))\nassert lower_bound(_big, 100000) == 50000, '10 万个元素里找 100000 应返回 50000，实际 %r' % (lower_bound(_big, 100000),)",
            "_big = list(range(0, 200000, 2))\nassert lower_bound(_big, 199999) == 100000, '找不到时返回 len(items) = 100000，实际 %r' % (lower_bound(_big, 199999),)",
            "_c = [7] * 50\nassert lower_bound(_c, 6) == 0 and lower_bound(_c, 7) == 0 and lower_bound(_c, 8) == 50, '50 个相同的值：找 6 是 0、找 7 是 0、找 8 是 50'",
        ],
        'explanation': (
            '「第一个 ≥ target 的位置」是二分查找最重要的变体，'
            '很多题（插入位置、区间计数、去重计数）都靠它。\n\n'
            '它和普通折半查找最大的不同是：**命中时不能直接返回**。'
            '因为要找的是「第一个」≥ target 的位置，命中点左边可能还有同样的值，'
            '必须把区间继续往左压：\n\n'
            '```python\n'
            'if items[mid] < target:\n'
            '    left = mid + 1        # mid 和它左边都太小\n'
            'else:\n'
            '    right = mid           # mid 可能就是答案，保留它\n'
            '```\n\n'
            '**边界设计**：右边界取 `len(items)`（不是 `len(items) - 1`），'
            '区间是左闭右开的 `[left, right)`。这样「所有元素都小于 target」时，'
            '答案 `len(items)` 天然就在区间里，不需要额外特判。\n\n'
            '**常见错误**：\n\n'
            '1. 右边界写成 `len(items) - 1` + `while left <= right`：'
            '   找不到时返回的位置会差一格；\n'
            '2. 命中就 `return mid`：有重复元素时返回的可能不是第一个；\n'
            '3. 循环条件写成 `left <= right` 配左闭右开区间，会死循环；\n'
            '4. `right = mid - 1`：会把可能是答案的 mid 丢掉。\n\n'
            '一个自检办法：`lower_bound` 的返回值一定等于「小于 target 的元素个数」。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '1\n0\n5',
        'hints': ['右边界是 len(items)，区间左闭右开', '命中时也把 right 压到 mid，最后返回 left'],
    },
    {
        'id': 'n408-023',
        'track': 'algorithm',
        'chapter_id': 121,
        'chapter_title': '查找与散列',
        'topic': '查找与散列',
        'title': '线性探测散列表的插入、查找与探测次数',
        'difficulty': 2,
        'tags': ['散列表', '线性探测', 'ASL'],
        'statement': (
            '定义类 `LinearProbeHash`，用**除留余数法 + 线性探测**实现一个散列表'
            '（只用数组，不挂链）：\n\n'
            '```python\n'
            'class LinearProbeHash:\n'
            '    def __init__(self, size):\n'
            '        # 表长 size，所有槽一开始都是空的\n'
            '        ...\n'
            '```\n\n'
            '要求实现下面四个方法（名字必须一致）：\n\n'
            '- `insert(key)`：插入整数 `key`。散列函数 `h(key) = key % size`；'
            '  若该槽已占用，依次探测 `(h + 1) % size`、`(h + 2) % size`……'
            '  插入成功返回 `True`；若 `key` **已经在表里**（重复插入）或**表已满**，'
            '  返回 `False` 且不插入；\n'
            '- `search(key)`：找到返回 `True`，否则返回 `False`。'
            '  **探测到空槽就可以停下**——线性探测的插入位置不会跳过空槽，'
            '  空槽后面不可能还有 key；\n'
            '- `probes(key)`：返回这次查找**比较过的槽位个数**'
            '（这是统考里算平均查找长度 ASL 的口径）：\n'
            '  - 找到 key 时：从 `h(key)` 数到 key 所在槽位（含两端）；\n'
            '  - 找不到时：从 `h(key)` 一直探测到**第一个空槽**为止（含那个空槽）；\n'
            '  - 表已满且 `key` 不在表里时：返回 `size`。\n\n'
            '最后用表长 5 依次插入 `3`、`8`、`13`，打印 `search` 与 `probes` 的结果，'
            '再打印「重复插入」「表满后再插入」「表满时查找一个不存在的值」的结果。'
        ),
        'starter_code': 'class LinearProbeHash:\n    def __init__(self, size):\n        self.size = size\n        self.table = [None] * size\n\n    def insert(self, key):\n        pass\n\n    def search(self, key):\n        pass\n\n    def probes(self, key):\n        pass\n',
        'solution': (
            "class LinearProbeHash:\n"
            "    def __init__(self, size):\n"
            "        self.size = size\n"
            "        self.table = [None] * size\n"
            "\n"
            "    def insert(self, key):\n"
            "        start = key % self.size\n"
            "        for step in range(self.size):\n"
            "            slot = (start + step) % self.size\n"
            "            if self.table[slot] is None:\n"
            "                self.table[slot] = key\n"
            "                return True\n"
            "            if self.table[slot] == key:\n"
            "                return False\n"
            "        return False\n"
            "\n"
            "    def search(self, key):\n"
            "        start = key % self.size\n"
            "        for step in range(self.size):\n"
            "            cell = self.table[(start + step) % self.size]\n"
            "            if cell is None:\n"
            "                return False\n"
            "            if cell == key:\n"
            "                return True\n"
            "        return False\n"
            "\n"
            "    def probes(self, key):\n"
            "        start = key % self.size\n"
            "        for step in range(self.size):\n"
            "            cell = self.table[(start + step) % self.size]\n"
            "            if cell is None or cell == key:\n"
            "                return step + 1\n"
            "        return self.size\n"
            "\n"
            "table = LinearProbeHash(5)\n"
            "print(table.search(3), table.probes(3))\n"
            "print(table.insert(3), table.insert(8), table.insert(13))\n"
            "print(table.search(13), table.probes(13))\n"
            "print(table.insert(3))\n"
            "print(table.insert(9), table.insert(4))\n"
            "print(table.insert(6))\n"
            "print(table.search(7), table.probes(7))\n"
        ),
        'checks': [
            "_h = LinearProbeHash(5)\nassert _h.search(3) is False and _h.probes(3) == 1, '空表找 3：3 %% 5 = 3 是空槽，1 次比较就该返回 False，实际 %r / %r' % (_h.search(3), _h.probes(3))",
            "assert _h.insert(3) is True, '往空槽插入 3 应返回 True'",
            "assert _h.search(3) is True and _h.probes(3) == 1, '插入后找 3 一次就比较到，实际 %r / %r' % (_h.search(3), _h.probes(3))",
            "assert _h.insert(8) is True, '8 %% 5 = 3 冲突，应探测到槽 4（插入成功返回 True）'",
            "assert _h.search(8) is True and _h.probes(8) == 2, '8 在槽 4，从槽 3 数起是 2 次比较，实际 %r' % (_h.probes(8),)",
            "assert _h.search(9) is False and _h.probes(9) == 2, '9 %% 5 = 4 被 8 占用，下一个槽 0 是空的，2 次比较后停下，实际 %r' % (_h.probes(9),)",
            "assert _h.insert(3) is False, '重复插入已有的 3 应返回 False'",
            "assert _h.insert(13) is True and _h.probes(13) == 3, '13 %% 5 = 3：槽 3、4 都被占，落到槽 0，共 3 次比较，实际 %r' % (_h.probes(13),)",
            "assert _h.probes(12) == 1, '12 %% 5 = 2 那是空槽，1 次比较就该停下（probes 要从 h(key) 起算），实际 %r' % (_h.probes(12),)",
            "assert _h.insert(9) is True and _h.insert(4) is True, '再插入 9 和 4 应能填满剩下的槽'",
            "assert _h.insert(6) is False, '表满后插入应返回 False（不能覆盖已有元素）'",
            "assert _h.search(4) is True and _h.probes(4) == 4, '表满时找 4：4 %% 5 = 4，要绕过 8、13、9 才到槽 2，共 4 次比较，实际 %r' % (_h.probes(4),)",
            "assert _h.search(7) is False and _h.probes(7) == 5, '表满且找不到时应把 size 个槽全查一遍（5 次），实际 %r' % (_h.probes(7),)",
            "_one = LinearProbeHash(1)\nassert _one.search(0) is False and _one.probes(0) == 1, '表长 1 时找 0 应比较 1 次，实际 %r' % (_one.probes(0),)",
            "assert _one.insert(0) is True and _one.insert(5) is False, '表长 1 插入 0 后即满，再插任何 key 都失败'",
            "assert _one.search(7) is False and _one.probes(7) == 1, '表长 1 且表满时查找失败返回 size = 1，实际 %r' % (_one.probes(7),)",
            "_two = LinearProbeHash(3)\nassert _two.insert(4) is True and _two.search(4) is True and _two.search(1) is False, '4 %% 3 = 1 存好后，找 1 应从槽 1 探测到空槽 2 后返回 False'",
            "assert _two.probes(1) == 2, '找 1 要比较槽 1（不是 1）和槽 2（空）共 2 次，实际 %r' % (_two.probes(1),)",
            "_big = LinearProbeHash(97)\nfor _k in range(50):\n    _big.insert(_k * 3)\nassert _big.search(0) is True and _big.search(147) is True and _big.probes(0) == 1, '装了 50 个元素后，槽 0 上的 0 仍应 1 次命中，实际 %r' % (_big.probes(0),)",
        ],
        'explanation': (
            '线性探测的三件事都要"绕圈"做，所以取模 `% size` 是核心：\n\n'
            '```python\n'
            'start = key % size\n'
            'for step in range(size):\n'
            '    slot = (start + step) % size\n'
            '```\n\n'
            '**为什么查找可以「遇到空槽就停」？** 因为插入时一旦遇到空槽就放进去了，'
            '绝不会跳过空槽继续往后找位置；所以沿着同一条探测链走，'
            '空槽之前的位置若没有 key，空槽之后更不可能有。'
            '这个性质把查找失败的平均代价限制在常数级。\n\n'
            '**ASL（平均查找长度）**就是各 key 的探测次数之和除以 key 的个数，'
            '所以 `probes` 必须精确：找到 key 时算到它所在槽；'
            '找不到时算到第一个空槽（408 教材里失败 ASL 就是这样统计的）。\n\n'
            '**常见错误**：\n\n'
            '1. 探测不取模，`start + step` 越界 IndexError（或漏掉绕过表尾的部分）；\n'
            '2. 循环只写 `for step in range(size)` 却忘了「探测 size 次都没位置就是表满」；\n'
            '3. 重复插入时直接返回 True，或者更糟：把原来的 key 覆盖掉；\n'
            '4. 用 `0` 作为空槽标记——key 可能是 0。应该用 `None` 或另外的标记数组。\n\n'
            '复杂度：插入 / 查找一趟最多 O(size)；散列分布均匀时平均 O(1)。'
        ),
        'expected_output': 'False 1\nTrue True True\nTrue 3\nFalse\nTrue True\nFalse\nFalse 5',
        'hints': ['探测一律写成 (start + step) % size，注意绕回表头', '空槽标记用 None 而不是 0（key 可能是 0）'],
    },
    {
        'id': 'n408-024',
        'track': 'algorithm',
        'chapter_id': 121,
        'chapter_title': '查找与散列',
        'topic': '查找与散列',
        'title': 'QuickSelect 求第 k 小的元素（平均 O(n)）',
        'difficulty': 3,
        'tags': ['查找', '快速选择', '分区', '期望 O(n)'],
        'statement': (
            '定义函数 `kth_smallest(nums, k)`：返回无序列表 `nums` 中**第 k 小**的元素'
            '（`k` 从 1 开始；有重复元素时按位置算，例如 `[3, 3, 1]` 的第 2 小是 3）。\n\n'
            '- `k` 不在 `1 ~ len(nums)` 范围内时返回 `None`（空列表、`k = 0`、`k` 大于长度都返回 None）；\n'
            '- 允许**原地修改** `nums`（QuickSelect 的分区本来就会打乱它）；\n'
            '- 要求**平均 O(n)**：用快速排序的「分区（partition）」思路，'
            '每趟只往答案所在的那一侧继续，**不要两边都做**；\n'
            '- **不要整个排序**（不要用 `sorted`、`.sort()`、`heapq`），那样是 O(n log n)。\n\n'
            '做法：分区后枢轴停在最终位置 `p`，然后三选一：\n\n'
            '- `p == k - 1`：枢轴就是答案，直接返回 `nums[p]`；\n'
            '- `p > k - 1`：答案在左半段，把右边界缩到 `p - 1`；\n'
            '- `p < k - 1`：答案在右半段，把左边界缩到 `p + 1`。\n\n'
            '为了避开「已经有序的输入」这种最坏情况，'
            '取枢轴时**随机挑一个下标**再换到区间头部即可。\n\n'
            '最后打印 `[7, 2, 9, 4, 1, 5]` 的第 1、3、6 小的值，'
            '再打印 `k = 0` 和空表的结果。'
        ),
        'starter_code': 'import random\n\ndef kth_smallest(nums, k):\n    if not nums or k < 1 or k > len(nums):\n        return None\n    # 随机选取枢轴 → 分区 → 只看答案所在的一侧\n    pass\n',
        'solution': (
            "import random\n"
            "\n"
            "def kth_smallest(nums, k):\n"
            "    if not nums or k < 1 or k > len(nums):\n"
            "        return None\n"
            "    left = 0\n"
            "    right = len(nums) - 1\n"
            "    target = k - 1\n"
            "    while left <= right:\n"
            "        pick = random.randint(left, right)\n"
            "        nums[left], nums[pick] = nums[pick], nums[left]\n"
            "        store = left\n"
            "        for i in range(left + 1, right + 1):\n"
            "            if nums[i] < nums[left]:\n"
            "                store += 1\n"
            "                nums[store], nums[i] = nums[i], nums[store]\n"
            "        nums[left], nums[store] = nums[store], nums[left]\n"
            "        if store == target:\n"
            "            return nums[store]\n"
            "        if store > target:\n"
            "            right = store - 1\n"
            "        else:\n"
            "            left = store + 1\n"
            "    return None\n"
            "\n"
            "data = [7, 2, 9, 4, 1, 5]\n"
            "print(kth_smallest(data, 1))\n"
            "print(kth_smallest(data, 3))\n"
            "print(kth_smallest(data, 6))\n"
            "print(kth_smallest(data, 0))\n"
            "print(kth_smallest([], 1))\n"
        ),
        'checks': [
            "assert kth_smallest([], 1) is None, '空列表应返回 None'",
            "assert kth_smallest([1], 0) is None and kth_smallest([1], 2) is None, 'k 越界（0 或超过长度）应返回 None'",
            "assert kth_smallest([5], 1) == 5, '只有一个元素时第 1 小就是它'",
            "assert kth_smallest([7, 2, 9, 4, 1, 5], 1) == 1, '第 1 小是最小值 1，实际 %r' % (kth_smallest([7, 2, 9, 4, 1, 5], 1),)",
            "assert kth_smallest([7, 2, 9, 4, 1, 5], 3) == 4, '排序后是 [1, 2, 4, 5, 7, 9]，第 3 小是 4，实际 %r' % (kth_smallest([7, 2, 9, 4, 1, 5], 3),)",
            "assert kth_smallest([7, 2, 9, 4, 1, 5], 6) == 9, '第 6 小（最大值）是 9，实际 %r' % (kth_smallest([7, 2, 9, 4, 1, 5], 6),)",
            "assert kth_smallest([3, 3, 1], 2) == 3, '有重复元素时按位置算：[1, 3, 3] 的第 2 小是 3，实际 %r' % (kth_smallest([3, 3, 1], 2),)",
            "assert kth_smallest([2, 2, 2], 2) == 2, '全部相同元素时第 2 小还是 2，实际 %r' % (kth_smallest([2, 2, 2], 2),)",
            "assert kth_smallest([-1, -5, 3, 0], 2) == -1, '有负数时排序是 [-5, -1, 0, 3]，第 2 小是 -1，实际 %r' % (kth_smallest([-1, -5, 3, 0], 2),)",
            "assert kth_smallest(list(range(10)), 4) == 3, '已经升序的输入第 4 小是 3，实际 %r' % (kth_smallest(list(range(10)), 4),)",
            "assert kth_smallest(list(range(9, -1, -1)), 5) == 4, '已经降序的输入第 5 小是 4，实际 %r' % (kth_smallest(list(range(9, -1, -1)), 5),)",
            "assert kth_smallest([1, 2, 3, 4], 4) == 4 and kth_smallest([1, 2, 3, 4], 1) == 1, '第 k 小不是第 k 大：最大值在下标 k = 4 时取到'",
            "assert kth_smallest([6] * 100, 50) == 6, '100 个相同的 6，第 50 小仍是 6'",
            "_data = [(i * 7919) % 10007 for i in range(5000)]\n_expect = sorted(_data)\nassert kth_smallest(list(_data), 2500) == _expect[2499], '5000 个元素求第 2500 小：期望 %r，实际 %r' % (_expect[2499], kth_smallest(list(_data), 2500))",
            "_data = [(i * 7919) % 10007 for i in range(5000)]\n_expect = sorted(_data)\nassert kth_smallest(list(_data), 1) == _expect[0] and kth_smallest(list(_data), 5000) == _expect[4999], '5000 个元素求最小值和最大值也要对'",
        ],
        'explanation': (
            '快速选择（QuickSelect）就是「只做一半的快速排序」。\n\n'
            '分区（partition）之后，枢轴会落在它的**最终位置** `p` 上：'
            '左边全都比它小、右边全都比它大。于是：\n\n'
            '- 要找的下标正好是 `p` → 答案就是它；\n'
            '- 要找的下标小于 `p` → 答案一定在左半段，右半段整个扔掉；\n'
            '- 要找的下标大于 `p` → 只保留右半段。\n\n'
            '每轮只处理一侧，平均下来总工作量是 `n + n/2 + n/4 + ... = 2n`，'
            '所以平均 O(n)；而快速排序对两边都要排，是 O(n log n)。\n\n'
            '**为什么枢轴要随机取？** 如果每次都取区间第一个元素，'
            '遇到「已经有序」的输入，每轮只能把问题规模减 1，退化成 O(n²)。'
            '随机化之后，最坏情况仍然存在但概率极低，平均 O(n) 就保住了。\n\n'
            '**常见错误**：\n\n'
            '1. 两边都递归下去——那就变成快排了；\n'
            '2. 分区后忘了判断 `p == k - 1`（注意 k 从 1 开始，下标要减 1）；\n'
            '3. 用「排序后取下标」的做法，复杂度直接变 O(n log n)，'
            '   本题的考点就没练到；\n'
            '4. 递归写随机枢轴 + 深递归，在极端数据上碰到 `RecursionError`'
            '（改成 `while` 迭代就没有这个问题）。\n\n'
            '复杂度：平均时间 O(n)、最坏 O(n²)；额外空间 O(1)（迭代写法，不递归）。'
        ),
        'expected_output': '1\n4\n9\nNone\nNone',
        'hints': ['分区后枢轴的位置 p 就是它的最终下标，只处理 target 所在的那一侧', '随机挑枢轴再换到区间头部，避免有序输入退化成 O(n²)'],
    },
    {
        'id': 'n408-025',
        'track': 'algorithm',
        'chapter_id': 121,
        'chapter_title': '查找与散列',
        'topic': '查找与散列',
        'title': '两个有序数组的中位数（二分 O(log(min(m, n)))）',
        'difficulty': 3,
        'tags': ['查找', '二分', '中位数', '划分'],
        'statement': (
            '已知两个**升序**数组 `a` 和 `b`（长度可以不同、可以为空，元素可能重复）。\n\n'
            '定义函数 `find_median_sorted_arrays(a, b)`：返回两个数组合并后的**中位数**：\n\n'
            '- 总长度为**奇数**时就是中间那个数；\n'
            '- 总长度为**偶数**时是中间两个数的**平均值**（例如 2.5）；\n'
            '- 两个数组都为空时返回 `None`。\n\n'
            '要求用手写二分做到 **O(log(min(m, n)))**（m、n 是两个数组的长度），'
            '**不要**先把两个数组合并起来再取中间（那是 O(m + n)）。\n\n'
            '做法（**划分法**）：设总长度 `total = m + n`，左半部分应有 '
            '`half = (total + 1) // 2` 个元素。我们在**较短的数组**（记作 a）上二分'
            '「a 贡献左半部分几个元素」：\n\n'
            '- 设 a 贡献 `i` 个（`0 ≤ i ≤ m`），则 b 贡献 `j = half - i` 个；\n'
            '- 记 `a_left = a[i - 1]`（i 为 0 时当作 −∞）、`a_right = a[i]`'
            '（i 为 m 时当作 +∞），`b_left`、`b_right` 同理；\n'
            '- 若 `a_left ≤ b_right` 且 `b_left ≤ a_right`，划分正确：\n'
            '  - 总长度是奇数：答案是 `max(a_left, b_left)`；\n'
            '  - 总长度是偶数：答案是 `(max(a_left, b_left) + min(a_right, b_right)) / 2`；\n'
            '- 若 `a_left > b_right`，说明 a 给多了，把 `i` 调小（`high = i - 1`）；\n'
            '  否则 a 给少了（`low = i + 1`）。\n\n'
            '最后打印 `[1, 3]` 与 `[2]`、`[1, 2]` 与 `[3, 4]`、`[]` 与 `[5, 6, 7]`、'
            '以及两个空数组的结果。'
        ),
        'starter_code': 'def find_median_sorted_arrays(a, b):\n    if len(a) > len(b):\n        a, b = b, a\n    m = len(a)\n    n = len(b)\n    # 在 a 上二分贡献给左半部分的元素个数，检查划分条件\n    pass\n',
        'solution': (
            "def find_median_sorted_arrays(a, b):\n"
            "    if len(a) > len(b):\n"
            "        a, b = b, a\n"
            "    m = len(a)\n"
            "    n = len(b)\n"
            "    if n == 0:\n"
            "        return None\n"
            "    total = m + n\n"
            "    half = (total + 1) // 2\n"
            "    low = 0\n"
            "    high = m\n"
            "    while low <= high:\n"
            "        i = (low + high) // 2\n"
            "        j = half - i\n"
            "        a_left = a[i - 1] if i > 0 else float('-inf')\n"
            "        a_right = a[i] if i < m else float('inf')\n"
            "        b_left = b[j - 1] if j > 0 else float('-inf')\n"
            "        b_right = b[j] if j < n else float('inf')\n"
            "        if a_left <= b_right and b_left <= a_right:\n"
            "            if total % 2 == 1:\n"
            "                return float(max(a_left, b_left))\n"
            "            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0\n"
            "        if a_left > b_right:\n"
            "            high = i - 1\n"
            "        else:\n"
            "            low = i + 1\n"
            "    return None\n"
            "\n"
            "print(find_median_sorted_arrays([1, 3], [2]))\n"
            "print(find_median_sorted_arrays([1, 2], [3, 4]))\n"
            "print(find_median_sorted_arrays([], [5, 6, 7]))\n"
            "print(find_median_sorted_arrays([], []))\n"
        ),
        'checks': [
            "assert find_median_sorted_arrays([], []) is None, '两个空数组应返回 None'",
            "assert find_median_sorted_arrays([], [5, 6, 7]) == 6, '一个为空时就是另一个的中位数 6，实际 %r' % (find_median_sorted_arrays([], [5, 6, 7]),)",
            "assert find_median_sorted_arrays([5, 6, 7], []) == 6, '参数顺序反过来结果一样，实际 %r' % (find_median_sorted_arrays([5, 6, 7], []),)",
            "assert find_median_sorted_arrays([1], []) == 1 and find_median_sorted_arrays([], [2]) == 2, '单元素数组的中位数就是它自己'",
            "assert find_median_sorted_arrays([1, 3], [2]) == 2, '合并后 [1, 2, 3]，中位数是 2，实际 %r' % (find_median_sorted_arrays([1, 3], [2]),)",
            "assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5, '合并后 [1, 2, 3, 4]，中位数是 (2 + 3) / 2 = 2.5，实际 %r' % (find_median_sorted_arrays([1, 2], [3, 4]),)",
            "assert find_median_sorted_arrays([1, 3], [2, 4]) == 2.5, '交错的两个数组结果也是 2.5，实际 %r' % (find_median_sorted_arrays([1, 3], [2, 4]),)",
            "assert find_median_sorted_arrays([1], [2]) == 1.5, '两个单元素数组的中位数是平均值 1.5，实际 %r' % (find_median_sorted_arrays([1], [2]),)",
            "assert find_median_sorted_arrays([1, 1], [1, 1]) == 1, '全相同时中位数是 1，实际 %r' % (find_median_sorted_arrays([1, 1], [1, 1]),)",
            "assert find_median_sorted_arrays([1, 2, 2], [3]) == 2, '合并后 [1, 2, 2, 3]，中位数是 (2 + 2) / 2 = 2，实际 %r' % (find_median_sorted_arrays([1, 2, 2], [3]),)",
            "assert find_median_sorted_arrays([1, 2, 3, 4, 5], [100]) == 3.5, '长数组 + 一个很大的数：合并后中间两个是 3 和 4，实际 %r' % (find_median_sorted_arrays([1, 2, 3, 4, 5], [100]),)",
            "assert find_median_sorted_arrays([100], [1, 2, 3, 4, 5]) == 3.5, '把它写在第一个参数（会触发交换）结果也应一样，实际 %r' % (find_median_sorted_arrays([100], [1, 2, 3, 4, 5]),)",
            "assert find_median_sorted_arrays([1, 5, 9], [2, 3, 4]) == 3.5, '合并后 [1, 2, 3, 4, 5, 9]，中位数是 3.5，实际 %r' % (find_median_sorted_arrays([1, 5, 9], [2, 3, 4]),)",
            "assert find_median_sorted_arrays([-5, -3, -1], [-4, -2]) == -3, '负数数组：合并后 [-5, -4, -3, -2, -1]，中位数是 -3，实际 %r' % (find_median_sorted_arrays([-5, -3, -1], [-4, -2]),)",
            "assert find_median_sorted_arrays([1, 2], [1, 2]) == 1.5, '两个完全一样的数组结果还是 1.5，实际 %r' % (find_median_sorted_arrays([1, 2], [1, 2]),)",
            "_a = list(range(0, 4000, 2))\n_b = list(range(1, 4000, 2))\nassert find_median_sorted_arrays(_a, _b) == 1999.5, '两个各 2000 个元素的数组（0~3999）中位数是 1999.5，实际 %r' % (find_median_sorted_arrays(_a, _b),)",
            "_a = list(range(0, 100000, 2))\n_b = list(range(1, 100000, 2))\nassert find_median_sorted_arrays(_a, _b) == 49999.5, '各 5 万个元素时中位数是 49999.5（必须用二分，别合并）'",
        ],
        'explanation': (
            '把两个有序数组「切成左右两半」是这题最优雅的做法。'
            '设总长度 `total`，我们要找一个划分，使得：\n\n'
            '- 左半部分恰好有 `half = (total + 1) // 2` 个元素；\n'
            '- 左半部分的最大值 ≤ 右半部分的最小值。\n\n'
            '只要在**较短的数组**上二分「它贡献几个元素」（记为 `i`），'
            '`j = half - i` 就被确定了，检查两个不等式即可：\n\n'
            '```python\n'
            'if a_left <= b_right and b_left <= a_right:\n'
            '    if total % 2 == 1:\n'
            '        return float(max(a_left, b_left))\n'
            '    return (max(a_left, b_left) + min(a_right, b_right)) / 2.0\n'
            'if a_left > b_right:\n'
            '    high = i - 1      # a 给多了\n'
            'else:\n'
            '    low = i + 1       # a 给少了\n'
            '```\n\n'
            '**为什么两处都要用哨兵？** `i = 0` 时 a 没有左边元素，'
            '用 −∞ 保证「左边的最大值」不会因为空而算错；`i = m` 时用 +∞ 同理。\n\n'
            '**为什么要在短数组上二分？** 因为要保证 `j = half - i` 落在 `[0, n]` 内，'
            '否则会越界。先交换成 `m ≤ n`，二分范围就只有 O(log(min(m, n)))。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记交换两个数组，导致 `b[j]` 越界；\n'
            '2. 奇偶长度的公式用混（奇数取 `max`，偶数取 `max` 和 `min` 的平均）；\n'
            '3. 直接合并两个数组求中位数——答案对，但复杂度是 O(m + n)，不是本题要求；\n'
            '4. 返回整数：偶数长度时中位数可能是 `x.5`，要保证除法是浮点除法（`/ 2.0`）。\n\n'
            '复杂度：时间 O(log(min(m, n)))、额外空间 O(1)。'
        ),
        'expected_output': '2.0\n2.5\n6.0\nNone',
        'hints': ['在较短的数组上二分「它给左半部分几个元素」', '两处越界用 -inf / inf 当哨兵，划分正确的判据是两个不等式'],
    },
    # ── 专题 122 排序算法进阶 ─────────────────────────────
    {
        'id': 'n408-026',
        'track': 'algorithm',
        'chapter_id': 122,
        'chapter_title': '排序算法进阶',
        'topic': '排序算法进阶',
        'title': '希尔排序（缩小增量 + 组内插入排序）',
        'difficulty': 1,
        'tags': ['排序', '希尔排序', '插入排序'],
        'statement': (
            '已知顺序表 `items`。\n\n'
            '定义函数 `shell_sort(items)`：用**希尔排序**（缩小增量排序）'
            '把表**就地**排成升序，函数不需要返回值。\n\n'
            '要求：\n\n'
            '- 增量序列用 `gap = len(items) // 2`，每轮结束 `gap //= 2`，`gap == 0` 时停止；\n'
            '- 每个 `gap` 内对 `items[i]`、`items[i + gap]`、`items[i + 2 * gap]`……'
            '这组「隔着 gap 取一个」的子序列做**直接插入排序**：'
            '把普通插入排序里「往前挪 1 位」改成「往前挪 gap 位」；\n'
            '- 直接插入排序本身是稳定的，但希尔排序会跨 gap 搬移元素，整体**不稳定**'
            '（本题不要求稳定）；\n'
            '- 空间 O(1)：不要新建列表来排，也不要调用 `sorted` / `items.sort()`。\n\n'
            '参考骨架（把内层写成插入排序）：\n\n'
            '```python\n'
            'gap = len(items) // 2\n'
            'while gap > 0:\n'
            '    for i in range(gap, len(items)):\n'
            '        value = items[i]\n'
            '        j = i - gap\n'
            '        while j >= 0 and items[j] > value:\n'
            '            items[j + gap] = items[j]\n'
            '            j -= gap\n'
            '        items[j + gap] = value\n'
            '    gap //= 2\n'
            '```\n\n'
            '最后打印 `[9, 1, 5, 3, 7, 2, 8]` 排序后的结果，'
            '再打印空表和已经有序的表 `[1, 2, 3]` 的结果。'
        ),
        'starter_code': 'def shell_sort(items):\n    gap = len(items) // 2\n    while gap > 0:\n        # 对每个「隔 gap 取一个」的子序列做插入排序\n        gap //= 2\n',
        'solution': (
            "def shell_sort(items):\n"
            "    n = len(items)\n"
            "    gap = n // 2\n"
            "    while gap > 0:\n"
            "        for i in range(gap, n):\n"
            "            value = items[i]\n"
            "            j = i - gap\n"
            "            while j >= 0 and items[j] > value:\n"
            "                items[j + gap] = items[j]\n"
            "                j -= gap\n"
            "            items[j + gap] = value\n"
            "        gap //= 2\n"
            "    return None\n"
            "\n"
            "data = [9, 1, 5, 3, 7, 2, 8]\n"
            "shell_sort(data)\n"
            "print(data)\n"
            "empty = []\n"
            "shell_sort(empty)\n"
            "print(empty)\n"
            "sorted_data = [1, 2, 3]\n"
            "shell_sort(sorted_data)\n"
            "print(sorted_data)\n"
        ),
        'checks': [
            "_a = [9, 1, 5, 3, 7, 2, 8]\nshell_sort(_a)\nassert _a == [1, 2, 3, 5, 7, 8, 9], '七个元素排序后应是 [1, 2, 3, 5, 7, 8, 9]，实际 %r' % (_a,)",
            "_b = []\nshell_sort(_b)\nassert _b == [], '空表调用后仍是空表（不能报错）'",
            "_c = [7]\nshell_sort(_c)\nassert _c == [7], '只有一个元素时不用动'",
            "_d = [1, 2, 3]\nshell_sort(_d)\nassert _d == [1, 2, 3], '已经有序的表应保持不变，实际 %r' % (_d,)",
            "_e = [5, 4, 3, 2, 1]\nshell_sort(_e)\nassert _e == [1, 2, 3, 4, 5], '完全逆序应排成升序，实际 %r' % (_e,)",
            "_f = [2, 1]\nshell_sort(_f)\nassert _f == [1, 2], '两个元素逆序也要换过来，实际 %r' % (_f,)",
            "_g = [5, 5, 5, 5]\nshell_sort(_g)\nassert _g == [5, 5, 5, 5], '元素全相同时保持原样，实际 %r' % (_g,)",
            "_h = [3, 1, 3, 1, 2]\nshell_sort(_h)\nassert _h == [1, 1, 2, 3, 3], '有重复元素时每个元素都要保留，实际 %r' % (_h,)",
            "_i = [3, 2, 1]\n_ref = _i\nshell_sort(_i)\nassert _ref == [1, 2, 3] and _i is _ref, '要求原地排序：列表对象本身要变成 [1, 2, 3]，实际 %r' % (_ref,)",
            "_j = [-3, 5, 0, -1]\nshell_sort(_j)\nassert _j == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_j,)",
            "_k = [(_i * 7919) % 10007 for _i in range(1000)]\n_expect = sorted(_k)\nshell_sort(_k)\nassert _k == _expect, '1000 个元素的逆序/随机表也要排对（前 5 个 %r，期望 %r）' % (_k[:5], _expect[:5])",
            "_m = list(range(500, 0, -1))\nshell_sort(_m)\nassert _m == list(range(1, 501)), '500 个元素的降序表要排成 1~500，实际前三位 %r' % (_m[:3],)",
        ],
        'explanation': (
            '希尔排序 = **分组插入排序 + 增量逐步缩小**。\n\n'
            '直接插入排序在「数据基本有序」时几乎只花 O(n)，'
            '但一开始数据很乱，每次插入都要挪很远。'
            '希尔的想法是：先用大 gap 把远处的小元素快速搬到前面，'
            '让序列「大致有序」，再用小 gap 精修，最后 gap = 1 时几乎不用挪动。\n\n'
            '```python\n'
            'gap = n // 2\n'
            'while gap > 0:\n'
            '    for i in range(gap, n):          # 组内插入排序\n'
            '        value = items[i]\n'
            '        j = i - gap\n'
            '        while j >= 0 and items[j] > value:\n'
            '            items[j + gap] = items[j]    # 往前挪 gap 位\n'
            '            j -= gap\n'
            '        items[j + gap] = value\n'
            '    gap //= 2\n'
            '```\n\n'
            '**注意 `j >= 0` 和 `j -= gap`**：插入排序里是 `j -= 1`，'
            '这里全部换成 `gap`，包括回填时的 `items[j + gap]`。'
            '`gap = 1` 那一轮其实就是普通的直接插入排序。\n\n'
            '**常见错误**：\n\n'
            '1. 内层 `j -= 1` 写漏了 `gap`，退化成普通插入排序'
            '（结果还对，但没体现希尔的思想）；\n'
            '2. `while gap > 0` 写成 `while gap >= 1` 后忘记 `gap //= 2`，死循环；\n'
            '3. 空表 / 单元素没处理（`range(gap, n)` 天然安全，但要有 `gap = n // 2` 为 0 时直接跳过）；\n'
            '4. 用 `sorted(items)` 偷懒——本轮考的是原地排序的写法。\n\n'
            '复杂度：时间与增量序列有关（最坏 O(n²)，比直接插入排序好得多），空间 O(1)。'
        ),
        'expected_output': '[1, 2, 3, 5, 7, 8, 9]\n[]\n[1, 2, 3]',
        'hints': ['外层的 gap 从 n // 2 开始，每轮减半', '组内插入排序把「挪 1 位」改成「挪 gap 位」'],
    },
    {
        'id': 'n408-027',
        'track': 'algorithm',
        'chapter_id': 122,
        'chapter_title': '排序算法进阶',
        'topic': '排序算法进阶',
        'title': '堆排序（建大顶堆 + 下滤）',
        'difficulty': 2,
        'tags': ['排序', '堆排序', '大顶堆', '下滤'],
        'statement': (
            '已知顺序表 `items`。\n\n'
            '定义函数 `heap_sort(items)`：用**堆排序**把表**就地**排成升序，'
            '函数不需要返回值。\n\n'
            '要求手写「建大顶堆 → 反复取堆顶 → 下滤」这三步'
            '（**不要用 `heapq`**，也不要用 `items.sort()` / `sorted`）：\n\n'
            '1. 写一个辅助函数 `sift_down(items, root, size)`：把下标 `root` 的结点**向下调整**——'
            '   拿它和 `2 * root + 1`、`2 * root + 2`（左右孩子）比，'
            '   若某个孩子更大就和它交换，然后继续往下调整，直到它比两个孩子都大或到了叶子；\n'
            '2. **建堆**：从最后一个非叶结点 `size // 2 - 1` 开始，'
            '   倒着对每个下标做一次 `sift_down`；\n'
            '3. **排序**：反复把堆顶 `items[0]` 与当前末尾 `items[end]` 交换'
            '   （最大值归位），把堆的有效长度减一，再对下标 0 做一次 `sift_down`。\n\n'
            '升序排序要用**大顶堆**（每次把最大的换到末尾），时间 O(n log n)、空间 O(1)。\n\n'
            '最后打印 `[4, 6, 8, 5, 9]` 堆排序后的结果，'
            '再打印空表和单元素表 `[3]` 的结果。'
        ),
        'starter_code': 'def sift_down(items, root, size):\n    # 和孩子比大小，孩子更大就往下换\n    pass\n\ndef heap_sort(items):\n    # 先建大顶堆，再反复把堆顶换到末尾并重新下滤\n    pass\n',
        'solution': (
            "def sift_down(items, root, size):\n"
            "    while True:\n"
            "        left = 2 * root + 1\n"
            "        right = left + 1\n"
            "        largest = root\n"
            "        if left < size and items[left] > items[largest]:\n"
            "            largest = left\n"
            "        if right < size and items[right] > items[largest]:\n"
            "            largest = right\n"
            "        if largest == root:\n"
            "            return\n"
            "        items[root], items[largest] = items[largest], items[root]\n"
            "        root = largest\n"
            "\n"
            "def heap_sort(items):\n"
            "    n = len(items)\n"
            "    for i in range(n // 2 - 1, -1, -1):\n"
            "        sift_down(items, i, n)\n"
            "    for end in range(n - 1, 0, -1):\n"
            "        items[0], items[end] = items[end], items[0]\n"
            "        sift_down(items, 0, end)\n"
            "    return None\n"
            "\n"
            "data = [4, 6, 8, 5, 9]\n"
            "heap_sort(data)\n"
            "print(data)\n"
            "empty = []\n"
            "heap_sort(empty)\n"
            "print(empty)\n"
            "one = [3]\n"
            "heap_sort(one)\n"
            "print(one)\n"
        ),
        'checks': [
            "_a = [4, 6, 8, 5, 9]\nheap_sort(_a)\nassert _a == [4, 5, 6, 8, 9], '经典例子排序后应是 [4, 5, 6, 8, 9]，实际 %r' % (_a,)",
            "_b = []\nheap_sort(_b)\nassert _b == [], '空表调用后仍是空表（不能报错）'",
            "_c = [3]\nheap_sort(_c)\nassert _c == [3], '只有一个元素时不用动'",
            "_d = [1, 2]\nheap_sort(_d)\nassert _d == [1, 2], '两个元素且已有序时保持不变，实际 %r' % (_d,)",
            "_e = [2, 1]\nheap_sort(_e)\nassert _e == [1, 2], '两个元素逆序时要换过来，实际 %r' % (_e,)",
            "_f = list(range(10))\nheap_sort(_f)\nassert _f == list(range(10)), '已经升序的输入应保持不变，实际 %r' % (_f,)",
            "_g = list(range(10, 0, -1))\nheap_sort(_g)\nassert _g == list(range(1, 11)), '完全逆序应排成 1~10，实际 %r' % (_g,)",
            "_h = [5] * 20\nheap_sort(_h)\nassert _h == [5] * 20, '元素全相同时保持原样，实际 %r' % (_h[:5],)",
            "_i = [3, 1, 3, 1]\nheap_sort(_i)\nassert _i == [1, 1, 3, 3], '有重复元素时一个都不能少，实际 %r' % (_i,)",
            "_j = [3, 2, 1]\n_ref = _j\nheap_sort(_j)\nassert _ref == [1, 2, 3] and _j is _ref, '要求原地排序：列表对象本身要变成 [1, 2, 3]，实际 %r' % (_ref,)",
            "_k = [-3, 5, 0, -1]\nheap_sort(_k)\nassert _k == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_k,)",
            "_m = [(_i * 7919) % 10007 for _i in range(1000)]\n_expect = sorted(_m)\nheap_sort(_m)\nassert _m == _expect, '1000 个元素也要排对（前 5 个 %r，期望 %r）' % (_m[:5], _expect[:5])",
            "_n = [7, 2, 9, 4, 1, 5, 8, 3, 6]\nheap_sort(_n)\nassert _n == list(range(1, 10)), '1~9 打乱后应排成 [1, 2, 3, 4, 5, 6, 7, 8, 9]，实际 %r' % (_n,)",
        ],
        'explanation': (
            '堆排序的骨架只有两块：**下滤**和**两轮循环**。\n\n'
            '下滤（sift_down）解决「堆顶被换掉、堆性质被破坏」的问题：'
            '把当前结点和两个孩子里较大的那个交换，然后继续往下看，'
            '一路把「小的」沉到底：\n\n'
            '```python\n'
            'left = 2 * root + 1\n'
            'right = left + 1          # 顺序存储的二叉树：孩子下标是 2i+1、2i+2\n'
            '```\n\n'
            '**建堆为什么从 `n // 2 - 1` 倒着做？** 下标大于 `n // 2 - 1` 的结点都是叶子，'
            '叶子本身已经是合法的堆，不需要调整。倒序做保证「轮到某个结点时，'
            '它的左右子树都已经是堆」。\n\n'
            '**排序为什么升序要用大顶堆？** 大顶堆的堆顶是最大值，'
            '把它和当前末尾交换，最大值就「归位」到最终位置了；'
            '换完后堆的有效长度减一，再对堆顶做一次下滤即可。\n\n'
            '**常见错误**：\n\n'
            '1. `sift_down` 里忘记比较 `right < size`，最后一行越界；\n'
            '2. 交换后没有把 `root = largest` 继续往下沉（只调整了一层）；\n'
            '3. 建堆写成从 0 往下做，或者只对根做一次下滤；\n'
            '4. 排序阶段用「取堆顶放到新数组」，多花了 O(n) 空间；'
            '   标准做法是把堆顶换到末尾、原地收缩堆。\n\n'
            '复杂度：时间 O(n log n)（建堆 O(n) + n 次下滤各 O(log n)）、'
            '额外空间 O(1)（递归/迭代都只用常数个变量）。'
        ),
        'expected_output': '[4, 5, 6, 8, 9]\n[]\n[3]',
        'hints': ['孩子下标是 2i+1 和 2i+2，注意别越界', '建堆从 n // 2 - 1 倒着做；排序时把堆顶换到末尾再下滤'],
    },
    {
        'id': 'n408-028',
        'track': 'algorithm',
        'chapter_id': 122,
        'chapter_title': '排序算法进阶',
        'topic': '排序算法进阶',
        'title': '荷兰国旗问题（三路分区）',
        'difficulty': 2,
        'tags': ['排序', '三指针', '分区', '原地'],
        'statement': (
            '已知顺序表 `items`，里面的元素**只可能是 0、1、2**，'
            '要把它排成「所有 0 → 所有 1 → 所有 2」。\n\n'
            '定义函数 `sort_colors(items)`：**就地**排好序，函数不需要返回值。\n\n'
            '要求**一趟遍历**（时间 O(n)）、额外空间 O(1)，用荷兰国旗的**三指针**做法：\n\n'
            '- `low` 之前（不含 `low`）全是 0，`high` 之后（不含 `high`）全是 2，'
            '`mid` 是当前正在看的元素；\n'
            '- `items[mid] == 0`：与 `items[low]` 交换，`low`、`mid` 都加一；\n'
            '- `items[mid] == 1`：`mid` 加一；\n'
            '- `items[mid] == 2`：与 `items[high]` 交换，`high` 减一，'
            '**`mid` 不动**——因为从 `high` 换过来的元素还没看过。\n\n'
            '不要用「先数一遍 0 的个数、再数 1 的个数、然后重写数组」的两趟计数做法，'
            '也不要调用 `sorted`。\n\n'
            '最后打印 `[2, 0, 2, 1, 1, 0]` 排序后的结果，'
            '再打印空表和全是 1 的表 `[1, 1, 1]` 的结果。'
        ),
        'starter_code': 'def sort_colors(items):\n    low = 0\n    mid = 0\n    high = len(items) - 1\n    # 0 换到前面、2 换到后面、1 直接跳过；注意 mid <= high\n    pass\n',
        'solution': (
            "def sort_colors(items):\n"
            "    low = 0\n"
            "    mid = 0\n"
            "    high = len(items) - 1\n"
            "    while mid <= high:\n"
            "        if items[mid] == 0:\n"
            "            items[low], items[mid] = items[mid], items[low]\n"
            "            low += 1\n"
            "            mid += 1\n"
            "        elif items[mid] == 1:\n"
            "            mid += 1\n"
            "        else:\n"
            "            items[mid], items[high] = items[high], items[mid]\n"
            "            high -= 1\n"
            "    return None\n"
            "\n"
            "data = [2, 0, 2, 1, 1, 0]\n"
            "sort_colors(data)\n"
            "print(data)\n"
            "empty = []\n"
            "sort_colors(empty)\n"
            "print(empty)\n"
            "ones = [1, 1, 1]\n"
            "sort_colors(ones)\n"
            "print(ones)\n"
        ),
        'checks': [
            "_a = [2, 0, 2, 1, 1, 0]\nsort_colors(_a)\nassert _a == [0, 0, 1, 1, 2, 2], '经典例子应排成 [0, 0, 1, 1, 2, 2]，实际 %r' % (_a,)",
            "_b = []\nsort_colors(_b)\nassert _b == [], '空表调用后仍是空表'",
            "_c = [0]\nsort_colors(_c)\nassert _c == [0], '单个 0 不用动，实际 %r' % (_c,)",
            "_d = [2]\nsort_colors(_d)\nassert _d == [2], '单个 2 不用动，实际 %r' % (_d,)",
            "_e = [0, 0, 1, 1, 2, 2]\nsort_colors(_e)\nassert _e == [0, 0, 1, 1, 2, 2], '已经排好的表应保持不变，实际 %r' % (_e,)",
            "_f = [2, 2, 1, 1, 0, 0]\nsort_colors(_f)\nassert _f == [0, 0, 1, 1, 2, 2], '完全逆序也要排对，实际 %r' % (_f,)",
            "_g = [2, 0, 2, 0]\nsort_colors(_g)\nassert _g == [0, 0, 2, 2], '只有 0 和 2 时应把 0 全换到前面，实际 %r' % (_g,)",
            "_h = [1, 1, 1]\nsort_colors(_h)\nassert _h == [1, 1, 1], '全是 1 时保持不变，实际 %r' % (_h,)",
            "_i = [2, 2, 2]\nsort_colors(_i)\nassert _i == [2, 2, 2], '全是 2 时保持不变，实际 %r' % (_i,)",
            "_j = [0, 0, 0]\nsort_colors(_j)\nassert _j == [0, 0, 0], '全是 0 时保持不变，实际 %r' % (_j,)",
            "_k = [1, 0, 2]\n_ref = _k\nsort_colors(_k)\nassert _ref == [0, 1, 2] and _k is _ref, '要求原地排序：列表对象本身要变成 [0, 1, 2]，实际 %r' % (_ref,)",
            "_m = [(i * 7) % 3 for i in range(3000)]\n_expect = sorted(_m)\nsort_colors(_m)\nassert _m == _expect, '3000 个元素也要排对（前 5 个 %r）' % (_m[:5],)",
            "_n = [2, 1, 0]\nsort_colors(_n)\nassert _n == [0, 1, 2], '三个元素各一个时应排成 [0, 1, 2]，实际 %r' % (_n,)",
        ],
        'explanation': (
            '荷兰国旗问题把数组分成三段，关键是**三个指针各管一件事**：\n\n'
            '```python\n'
            'while mid <= high:\n'
            '    if items[mid] == 0:\n'
            '        items[low], items[mid] = items[mid], items[low]\n'
            '        low += 1; mid += 1        # 换过来的是 0，已看过，mid 前进\n'
            '    elif items[mid] == 1:\n'
            '        mid += 1                  # 1 就该待在中间，跳过\n'
            '    else:\n'
            '        items[mid], items[high] = items[high], items[mid]\n'
            '        high -= 1                 # 换过来的还没看，mid 不能动\n'
            '```\n\n'
            '**为什么 2 的分支里 `mid` 不动？** 因为从 `high` 位置换过来的元素'
            '可能还是 2、也可能是 0，必须先重新检查它。'
            '这是本题最容易写错的地方：多写一句 `mid += 1` 就会漏掉元素。\n\n'
            '**循环条件为什么是 `mid <= high`？** `high` 之后已经是排好的 2，'
            '`mid` 一旦越过 `high`，所有元素都归位了，再继续就会把刚换过去的 2 又换回来。\n\n'
            '**常见错误**：\n\n'
            '1. `items[mid] == 2` 分支里也 `mid += 1`；\n'
            '2. 循环条件写成 `mid < high`，最后一个元素没检查；\n'
            '3. 用「数出 0/1/2 各多少个再重写」——两趟遍历，'
            '   虽然结果对，但不符合「一趟 + 三指针」的要求。\n\n'
            '这个分区思路是快速排序三路划分的基础。\n\n'
            '复杂度：时间 O(n)（每个元素最多被交换一次）、额外空间 O(1)。'
        ),
        'expected_output': '[0, 0, 1, 1, 2, 2]\n[]\n[1, 1, 1]',
        'hints': ['三个指针：low 管 0、high 管 2、mid 当前扫描', '遇到 2 时 mid 不要动，因为换过来的元素还没看过'],
    },
    {
        'id': 'n408-029',
        'track': 'algorithm',
        'chapter_id': 122,
        'chapter_title': '排序算法进阶',
        'topic': '排序算法进阶',
        'title': '计数排序（O(n + k) 非比较排序）',
        'difficulty': 2,
        'tags': ['排序', '计数排序', '非比较排序'],
        'statement': (
            '已知顺序表 `items`，元素都是**非负整数**（可能有重复，也可能值很大）。\n\n'
            '定义函数 `counting_sort(items)`：返回一个**新的升序列表**，'
            '并且**不修改**传入的 `items`；空表返回 `[]`。\n\n'
            '要求用**计数排序**，时间 O(n + k)、空间 O(n + k)（k 是最大值 + 1）：\n\n'
            '1. 先找出最大值 `max_value`；\n'
            '2. 开一个长度 `max_value + 1` 的计数数组 `counts`，'
            '   `counts[v]` 记录值 v 出现了几次；\n'
            '3. 从小到大扫一遍 `counts`：某个值出现几次，就往结果里写几次；\n'
            '4. **不要**用 `sorted(items)` 或 `items.sort()`。\n\n'
            '（计数排序只适合值域不太大的非负整数，这是它的适用条件；'
            '它是**稳定**的——按值从小到大输出，相同值的相对顺序天然保持。）\n\n'
            '最后打印 `[4, 2, 2, 8, 3, 3, 1]` 排序后的结果和原列表（证明没被改动），'
            '再打印空表和 `[0, 0, 0]` 的结果。'
        ),
        'starter_code': 'def counting_sort(items):\n    if not items:\n        return []\n    # 找最大值 → 统计次数 → 从小到大写回结果\n    pass\n',
        'solution': (
            "def counting_sort(items):\n"
            "    if not items:\n"
            "        return []\n"
            "    max_value = max(items)\n"
            "    counts = [0] * (max_value + 1)\n"
            "    for value in items:\n"
            "        counts[value] += 1\n"
            "    result = []\n"
            "    for value in range(max_value + 1):\n"
            "        for _ in range(counts[value]):\n"
            "            result.append(value)\n"
            "    return result\n"
            "\n"
            "data = [4, 2, 2, 8, 3, 3, 1]\n"
            "print(counting_sort(data))\n"
            "print(data)\n"
            "print(counting_sort([]))\n"
            "print(counting_sort([0, 0, 0]))\n"
        ),
        'checks': [
            "assert counting_sort([4, 2, 2, 8, 3, 3, 1]) == [1, 2, 2, 3, 3, 4, 8], '经典例子应是 [1, 2, 2, 3, 3, 4, 8]，实际 %r' % (counting_sort([4, 2, 2, 8, 3, 3, 1]),)",
            "assert counting_sort([]) == [], '空表应返回空列表'",
            "assert counting_sort([5]) == [5], '只有一个元素时返回它本身'",
            "assert counting_sort([0]) == [0] and counting_sort([0, 0, 0]) == [0, 0, 0], '0 也要能处理（不能被当成空值跳过），实际 %r' % (counting_sort([0, 0, 0]),)",
            "_a = [3, 1, 2]\n_r = counting_sort(_a)\nassert _a == [3, 1, 2], '题面要求不修改原列表，实际 %r' % (_a,)",
            "_a = [3, 1, 2]\n_r = counting_sort(_a)\nassert _r == [1, 2, 3] and _r is not _a, '应返回一个新的排好序的列表，实际 %r' % (_r,)",
            "assert counting_sort([0, 3, 0]) == [0, 0, 3], '0 在中间出现时要正确统计，实际 %r' % (counting_sort([0, 3, 0]),)",
            "assert counting_sort([7, 7, 7, 7]) == [7, 7, 7, 7], '全是同一个值时一个都不能少，实际 %r' % (counting_sort([7, 7, 7, 7]),)",
            "assert counting_sort([1, 2, 3]) == [1, 2, 3], '已经有序时结果不变，实际 %r' % (counting_sort([1, 2, 3]),)",
            "assert counting_sort([2, 1, 2, 1]) == [1, 1, 2, 2], '重复的多个值都要保留，实际 %r' % (counting_sort([2, 1, 2, 1]),)",
            "assert counting_sort([1000000]) == [1000000], '值很大但只有一个元素时应能处理，实际 %r' % (counting_sort([1000000]),)",
            "assert counting_sort([0, 1000000]) == [0, 1000000], '值域跨度大时也会开 1000001 个计数槽（计数排序的适用条件），实际 %r' % (counting_sort([0, 1000000]),)",
            "_b = [(i * 37) % 101 for i in range(2000)]\n_r = counting_sort(_b)\nassert _b == [(i * 37) % 101 for i in range(2000)], '原列表在排序后必须保持不变'",
            "_b = [(i * 37) % 101 for i in range(2000)]\nassert counting_sort(_b) == sorted(_b), '2000 个元素的随机值域数据要排对（前 5 个 %r）' % (counting_sort(_b)[:5],)",
        ],
        'explanation': (
            '计数排序跳出「比较两个元素」的框架：'
            '**一个值应该排在哪里，取决于比它小的值一共有多少个**。\n\n'
            '```python\n'
            'max_value = max(items)\n'
            'counts = [0] * (max_value + 1)\n'
            'for value in items:\n'
            '    counts[value] += 1            # 统计每个值出现的次数\n'
            'result = []\n'
            'for value in range(max_value + 1):\n'
            '    for _ in range(counts[value]):\n'
            '        result.append(value)      # 出现几次就写几次\n'
            '```\n\n'
            '**为什么它是 O(n + k)？** 统计要一趟 O(n)，'
            '输出要扫一遍计数数组 O(k)，总共 O(n + k)——当 k 和 n 差不多大时就是线性的，'
            '比任何比较排序都快。\n\n'
            '**为什么不做比较就能排序？** 因为比较排序的信息论下界 O(n log n) 只约束'
            '「只靠比较元素大小来排序」的算法；计数排序利用了「元素是 0 ~ k 的整数」'
            '这个额外信息，用值当下标直接定位。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `items.index(value)` 或 `items.remove` 之类的操作去「取出」元素——'
            '   那样复杂度变成 O(n²) 还把原表改坏了；\n'
            '2. 计数数组只开到 `max(items)`（少 1 个槽）导致越界；\n'
            '3. 忘记空表返回 `[]`，`max([])` 会直接抛异常；\n'
            '4. 用 `counts[v] > 0` 而不是按次数写回，重复元素会丢。\n\n'
            '复杂度：时间 O(n + k)、空间 O(n + k)（返回的结果列表 + 计数数组）。'
        ),
        'expected_output': '[1, 2, 2, 3, 3, 4, 8]\n[4, 2, 2, 8, 3, 3, 1]\n[]\n[0, 0, 0]',
        'hints': ['计数数组长度是 max(items) + 1', '输出时按 counts[value] 的次数写 value，重复元素才不丢'],
    },
    {
        'id': 'n408-030',
        'track': 'algorithm',
        'chapter_id': 122,
        'chapter_title': '排序算法进阶',
        'topic': '排序算法进阶',
        'title': '多关键字排序（利用稳定排序逐趟处理）',
        'difficulty': 3,
        'tags': ['排序', '稳定性', '多关键字'],
        'statement': (
            '已知一批学生记录，每条记录是三元组 `(学号, 总分, 年龄)`，学号互不相同。\n\n'
            '定义函数 `sort_records(records)`：返回一个**新的列表**'
            '（不修改传入的列表），排序规则为：\n\n'
            '1. **总分从高到低**（降序）；\n'
            '2. 总分相同时，**年龄从小到大**（升序）；\n'
            '3. 总分与年龄都相同时，**学号从小到大**（升序）。\n\n'
            '要求利用**稳定排序**的性质，用「从最次要的关键字开始，逐趟稳定排序」的做法'
            '（这里依次是：学号 → 年龄 → 总分降序）：\n\n'
            '- 第 1 趟：按**学号**升序排；\n'
            '- 第 2 趟：按**年龄**升序**稳定**排序（年龄相同的记录保持第 1 趟的学号顺序）；\n'
            '- 第 3 趟：按**总分降序**稳定排序（总分相同的记录保持第 2 趟的顺序）。\n\n'
            'Python 的 `sorted` 和 `list.sort` 都是**稳定**的（相等元素的相对次序不变），'
            '所以三趟 `sorted` 就能得到正确结果。'
            '（写成「一次排序 + 多关键字 key」也能得到同样结果，'
            '但本题希望你练「稳定排序逐趟处理」这个思路。）\n\n'
            '最后打印 `[(1003, 90, 20), (1002, 90, 20), (1001, 95, 21), (1004, 80, 19)]` '
            '排序后的结果（每行打印一条），再打印原列表和空表的结果。'
        ),
        'starter_code': 'def sort_records(records):\n    # 从最次要的关键字开始逐趟稳定排序：学号 → 年龄 → 总分（降序）\n    result = sorted(records, key=lambda record: record[0])\n    pass\n',
        'solution': (
            "def sort_records(records):\n"
            "    result = sorted(records, key=lambda record: record[0])\n"
            "    result = sorted(result, key=lambda record: record[2])\n"
            "    result = sorted(result, key=lambda record: -record[1])\n"
            "    return result\n"
            "\n"
            "records = [(1003, 90, 20), (1002, 90, 20), (1001, 95, 21), (1004, 80, 19)]\n"
            "for record in sort_records(records):\n"
            "    print(record)\n"
            "print(records)\n"
            "print(sort_records([]))\n"
        ),
        'checks': [
            "assert sort_records([(1003, 90, 20), (1002, 90, 20), (1001, 95, 21), (1004, 80, 19)]) == [(1001, 95, 21), (1002, 90, 20), (1003, 90, 20), (1004, 80, 19)], '经典例子应是 [(1001, 95, 21), (1002, 90, 20), (1003, 90, 20), (1004, 80, 19)]，实际 %r' % (sort_records([(1003, 90, 20), (1002, 90, 20), (1001, 95, 21), (1004, 80, 19)]),)",
            "assert sort_records([]) == [], '空表应返回空列表'",
            "assert sort_records([(1, 60, 18)]) == [(1, 60, 18)], '只有一条记录时原样返回'",
            "assert sort_records([(1, 80, 22), (2, 80, 20)]) == [(2, 80, 20), (1, 80, 22)], '总分相同时按年龄升序，实际 %r' % (sort_records([(1, 80, 22), (2, 80, 20)]),)",
            "assert sort_records([(3, 70, 18), (1, 70, 18), (2, 70, 18)]) == [(1, 70, 18), (2, 70, 18), (3, 70, 18)], '总分和年龄都相同时按学号升序（与输入顺序无关），实际 %r' % (sort_records([(3, 70, 18), (1, 70, 18), (2, 70, 18)]),)",
            "assert sort_records([(5, 90, 20), (4, 90, 20), (6, 90, 19)]) == [(6, 90, 19), (4, 90, 20), (5, 90, 20)], '先比总分、再比年龄、最后比学号，实际 %r' % (sort_records([(5, 90, 20), (4, 90, 20), (6, 90, 19)]),)",
            "assert sort_records([(1, 100, 30), (2, 0, 1)]) == [(1, 100, 30), (2, 0, 1)], '总分降序：高的排前面（哪怕年龄更大），实际 %r' % (sort_records([(1, 100, 30), (2, 0, 1)]),)",
            "assert sort_records([(2, 60, 20), (1, 90, 20)]) == [(1, 90, 20), (2, 60, 20)], '两条记录的排序，实际 %r' % (sort_records([(2, 60, 20), (1, 90, 20)]),)",
            "_a = [(2, 60, 20), (1, 90, 20)]\n_r = sort_records(_a)\nassert _a == [(2, 60, 20), (1, 90, 20)], '题面要求不修改传入的列表，实际 %r' % (_a,)",
            "_a = [(2, 60, 20), (1, 90, 20)]\n_r = sort_records(_a)\nassert _r is not _a, '应返回一个新的列表，实际返回了原列表对象'",
            "assert sort_records([(3, 90, 22), (1, 90, 22), (2, 90, 20)]) == [(2, 90, 20), (1, 90, 22), (3, 90, 22)], '顺序打乱的输入也要排对，实际 %r' % (sort_records([(3, 90, 22), (1, 90, 22), (2, 90, 20)]),)",
            "_big = [((_i * 37) % 1000, (_i * 17) % 5, (_i * 7) % 3) for _i in range(500)]\n_expect = sorted(_big, key=lambda _r: (-_r[1], _r[2], _r[0]))\n_r = sort_records(_big)\nassert _r == _expect, '500 条记录（三关键字都有重复）应与多关键字排序结果一致，实际前三条 %r' % (_r[:3],)",
            "_big = [((_i * 37) % 1000, (_i * 17) % 5, (_i * 7) % 3) for _i in range(500)]\n_r = sort_records(_big)\nassert sorted(_r) == sorted(_big) and len(_r) == 500, '排序不能丢记录也不能改记录，实际 %r 条' % (len(_r),)",
        ],
        'explanation': (
            '多关键字排序有两种正确写法，**稳定排序的妙处**在于：'
            '只要「从最次要的关键字开始，逐趟稳定排序」，最后一趟自然得到'
            '「主要关键字优先」的正确顺序。\n\n'
            '```python\n'
            'result = sorted(records, key=lambda r: r[0])      # 1. 学号升序\n'
            'result = sorted(result, key=lambda r: r[2])       # 2. 年龄升序（稳定）\n'
            'result = sorted(result, key=lambda r: -r[1])      # 3. 总分降序（稳定）\n'
            '```\n\n'
            '**为什么倒着排就行？** 第 2 趟排序只在「年龄相同」的记录之间保持原有次序，'
            '而原有次序已经被第 1 趟整理成了学号升序；'
            '同理第 3 趟保留了第 2 趟整理好的「年龄 → 学号」次序。'
            '倒着来一遍，最后的关键字就成了第一优先级。\n\n'
            '**总分降序怎么写？** 稳定性只保证「相等元素不乱序」，'
            '所以降序不能写成 `reverse=True`（那会把相等元素也翻过来），'
            '而是用 `key=lambda r: -r[1]` 把降序转成升序比较。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `reverse=True` 排总分，同分记录的顺序被翻转，第二、第三关键字就乱了；\n'
            '2. 顺序写反（先按总分排、再按年龄排），最后变成「年龄优先」；\n'
            '3. 用 `list.sort()` 原地排序：那会修改传入的列表，题面要求返回新列表；\n'
            '4. 以为 `sorted(key=...)` 传元组 key 才叫多关键字——'
            '   两种写法都对，但本题要练的是「稳定排序逐趟处理」。\n\n'
            '复杂度：三趟排序各 O(n log n)，总共 O(n log n)、额外空间 O(n)。'
        ),
        'expected_output': '(1001, 95, 21)\n(1002, 90, 20)\n(1003, 90, 20)\n(1004, 80, 19)\n[(1003, 90, 20), (1002, 90, 20), (1001, 95, 21), (1004, 80, 19)]\n[]',
        'hints': ['从最次要的关键字开始排：学号 → 年龄 → 总分', '降序要用 key=lambda r: -r[1]，不能用 reverse=True（会翻转同分记录）'],
    },
]
