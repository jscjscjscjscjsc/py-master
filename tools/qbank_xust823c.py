"""题库 · 西安科技大学 823《数据结构与算法》风格（基础篇）· 专题 127–129。

写法约定与 qbank_basic.py / qbank_pro.py / qbank_algo.py / qbank_408.py 保持一致：
- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式；
- checks 只断言题面要求的东西，每条断言都带中文提示，覆盖空输入、单元素、重复元素、
  逆序、全相同等边界；
- 参考答案本身必须能通过同一套断言。

出题口径：按 823 考试大纲的三大块组织——线性表（顺序表 / 单链表 / 双链表）与串
（朴素匹配、KMP）、栈与队列（栈的应用、循环队列、双端队列）、树与二叉树
（遍历与重建、BST、AVL 旋转、哈夫曼树与编码、线索二叉树、堆）。
题干按 823 真题的写法给出数据结构定义与函数签名，要求写出算法并说明复杂度；
真题里的 C 伪代码统一用 Python 的顺序表（列表）/ 结点类重述。
凡是链表、双链表、二叉树，都要求先定义题面给定的结点类（属性名一致），
算法直接在这些结点上改指针，不许把值拷进列表「绕开」指针操作。

专题划分：
    127 823·线性表与串     128 823·栈与队列      129 823·树与二叉树
"""

QUESTIONS = [
    # ── 专题 127 823·线性表与串 ───────────────────────────
    {
        'id': 'x823-201',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '顺序表删除最小值（表尾元素填补空位）',
        'difficulty': 1,
        'tags': ['顺序表', '原地', 'O(n)'],
        'statement': (
            '已知一个顺序表（用 Python 列表 `items` 表示）。\n\n'
            '定义函数 `del_min(items)`：**删除表中值最小的元素**，并返回被删元素的值。\n\n'
            '细节要求：\n\n'
            '- 如果最小的元素有多个，只删掉**第一个**（下标最小的那个）；\n'
            '- 空表返回 `None`（不要报错）；\n'
            '- 先扫一遍找到最小元素的下标 `min_i`，然后**用表尾元素填补 `items[min_i]`**，'
            '再把表尾删掉：\n\n'
            '```python\n'
            'removed = items[min_i]\n'
            'items[min_i] = items[-1]\n'
            'items.pop()\n'
            '```\n\n'
            '- 时间 O(n)、额外空间 O(1)；不许用 `items.remove(x)`（它还要再扫一遍表找位置），'
            '也不许用 `items.sort()`。\n\n'
            '最后打印 `del_min([3, 1, 2, 1, 5])` 的结果和删除后的列表，'
            '再打印空表、单元素表 `[7]`、全相同元素表 `[4, 4, 4]` 的结果。'
        ),
        'starter_code': 'def del_min(items):\n    # 先找最小元素的下标 min_i，再用 items[-1] 填补、pop 掉表尾\n    pass\n',
        'solution': (
            "def del_min(items):\n"
            "    if not items:\n"
            "        return None\n"
            "    min_i = 0\n"
            "    for i in range(1, len(items)):\n"
            "        if items[i] < items[min_i]:\n"
            "            min_i = i\n"
            "    removed = items[min_i]\n"
            "    items[min_i] = items[-1]\n"
            "    items.pop()\n"
            "    return removed\n"
            "\n"
            "data = [3, 1, 2, 1, 5]\n"
            "print(del_min(data), data)\n"
            "empty = []\n"
            "print(del_min(empty), empty)\n"
            "one = [7]\n"
            "print(del_min(one), one)\n"
            "same = [4, 4, 4]\n"
            "print(del_min(same), same)\n"
        ),
        'checks': [
            "_a = []\nassert del_min(_a) is None, '空表应返回 None，实际 %r' % (del_min([]),)",
            "_a = []\ndel_min(_a)\nassert _a == [], '空表调用后仍应是空表，实际 %r' % (_a,)",
            "_a = [7]\nassert del_min(_a) == 7, '只有一个元素时应返回 7，实际 %r' % (del_min([7]),)",
            "_a = [7]\ndel_min(_a)\nassert _a == [], '单元素表删除后应是空表，实际 %r' % (_a,)",
            "_a = [3, 1, 2, 1, 5]\n_r = del_min(_a)\nassert _r == 1, '最小值 1 出现了两次，应删第一个并返回 1，实际 %r' % (_r,)",
            "_a = [3, 1, 2, 1, 5]\ndel_min(_a)\nassert _a == [3, 5, 2, 1], '表尾的 5 要填到最小值原来的位置（下标 1）：应是 [3, 5, 2, 1]，实际 %r' % (_a,)",
            "_a = [1, 2, 3]\nassert del_min(_a) == 1 and _a == [3, 2], '最小值在表头时用表尾 3 填补：应是 [3, 2]，实际 %r' % (_a,)",
            "_a = [3, 2, 1]\nassert del_min(_a) == 1 and _a == [3, 2], '最小值正好在表尾时直接删尾：应是 [3, 2]，实际 %r' % (_a,)",
            "_a = [4, 4, 4]\nassert del_min(_a) == 4 and _a == [4, 4], '元素全相同时删掉一个：返回 4、剩下 [4, 4]，实际 %r' % (_a,)",
            "_a = [-1, 5, -1, 2]\nassert del_min(_a) == -1 and sorted(_a) == [-1, 2, 5], '负数最小值同样要处理，实际 %r' % (_a,)",
            "_a = [5, 3, 8, 3, 9]\ndel_min(_a)\nassert sorted(_a) == [3, 5, 8, 9], '删掉一个最小值后剩下的元素应与原表一致（不能多删也不能少删），实际 %r' % (_a,)",
            "_a = [2, 9]\n_ref = _a\ndel_min(_a)\nassert _a is _ref and _ref == [9], '要求原地修改原列表（对象本身要变成 [9]），实际 %r' % (_ref,)",
            "_a = list(range(1000, 0, -1))\nassert del_min(_a) == 1 and _a == list(range(1000, 1, -1)), '1000 个元素（最小值 1 在表尾）应删成 1000~2，实际长度 %r' % (len(_a),)",
        ],
        'explanation': (
            '顺序表删除有两个动作：**找到要删的位置**、**把空位补上**。\n\n'
            '很多同学的写法是「找到最小值后，把后面所有元素整体前移一位」，'
            '搬移是 O(n) 本身没问题，但题面给的提示是更省事的做法：**用表尾元素填补空位**，'
            '一步就填好，再 `pop()` 掉重复的表尾元素。\n\n'
            '注意三个细节：\n\n'
            '1. 求最小值时比较用 `<` 而不是 `<=`，这样多个相同最小值时留下的是**第一个**；\n'
            '2. 填补要在 `pop()` 之前做——如果先 `pop()` 再取 `items[-1]`，'
            '当最小值就在表尾时会把别的元素填进去，结果就错了；\n'
            '3. 空表必须提前返回，否则 `items[-1]` 直接 IndexError。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `items.remove(min(items))`，虽然结果对，但 `remove` 又要扫一遍表，'
            '而且 `min(items)` 已经扫过一遍了，等于扫两遍；\n'
            '2. 用 `sorted(items)[0]` 求最小值，那是 O(n log n)；\n'
            '3. 忘记 `pop()`，表长不变、表尾多出一个元素。\n\n'
            '复杂度：时间 O(n)（找最小值一趟）、额外空间 O(1)。'
        ),
        'expected_output': '1 [3, 5, 2, 1]\nNone []\n7 []\n4 [4, 4]',
        'hints': ['先用一趟循环找最小元素的下标 min_i（用 < 比较，保证删第一个）', 'items[min_i] = items[-1] 之后别忘了 items.pop()'],
    },
    {
        'id': 'x823-202',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '单链表求表长与最大值（一趟扫描）',
        'difficulty': 1,
        'tags': ['单链表', '遍历', 'O(n)'],
        'statement': (
            '请**按下面的定义**写好结点类（属性名必须一致，后面的函数都要用它）：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `list_stats(head)`：返回一个二元组 `(结点个数, 最大值)`。\n\n'
            '- 空链表返回 `(0, None)`（最大值记 `None`，不要用 0 之类的假值）；\n'
            '- 只允许**一趟扫描**（不许先数长度、再扫一遍求最大值），时间 O(n)、额外空间 O(1)；\n'
            '- 不许修改链表（不许改 `val`、也不许改 `next`）；\n'
            '- 表中的值可能是**负数**，所以「最大值」不能拿 0 当初始值，'
            '要用「还没有最大值」的标志判断（例如 `best is None`）。\n\n'
            '最后用 `print` 依次打印对 `1 → 5 → 3`、空链表、`-3 → -1 → -7`、'
            '`2 → 2 → 2` 调用 `list_stats` 的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef list_stats(head):\n    # count 数结点个数，best 记最大值（还没有时是 None）\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def list_stats(head):\n"
            "    count = 0\n"
            "    best = None\n"
            "    while head is not None:\n"
            "        count += 1\n"
            "        if best is None or head.val > best:\n"
            "            best = head.val\n"
            "        head = head.next\n"
            "    return count, best\n"
            "\n"
            "def build(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        head = Node(v, head)\n"
            "    return head\n"
            "\n"
            "print(list_stats(build([1, 5, 3])))\n"
            "print(list_stats(None))\n"
            "print(list_stats(build([-3, -1, -7])))\n"
            "print(list_stats(build([2, 2, 2])))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "assert list_stats(None) == (0, None), '空链表应返回 (0, None)，实际 %r' % (list_stats(None),)",
            "assert list_stats(_build([7])) == (1, 7), '只有一个结点时应返回 (1, 7)，实际 %r' % (list_stats(_build([7])),)",
            "assert list_stats(_build([1, 5, 3])) == (3, 5), '1 → 5 → 3 应是 (3, 5)，实际 %r' % (list_stats(_build([1, 5, 3])),)",
            "assert list_stats(_build([9, 1, 2])) == (3, 9), '最大值在表头也要能找出来，实际 %r' % (list_stats(_build([9, 1, 2])),)",
            "assert list_stats(_build([1, 2, 8])) == (3, 8), '最大值在表尾也要能找出来，实际 %r' % (list_stats(_build([1, 2, 8])),)",
            "assert list_stats(_build([2, 2, 2])) == (3, 2), '元素全相同时最大值就是 2，实际 %r' % (list_stats(_build([2, 2, 2])),)",
            "assert list_stats(_build([-3, -1, -7])) == (3, -1), '全是负数时最大值是 -1（不能拿 0 当初始最大值），实际 %r' % (list_stats(_build([-3, -1, -7])),)",
            "assert list_stats(_build([0, -5, 4])) == (3, 4), '有 0 和负数时最大值应是 4，实际 %r' % (list_stats(_build([0, -5, 4])),)",
            "_head = _build([1, 5, 3])\nlist_stats(_head)\nassert _to_list(_head) == [1, 5, 3], '题面要求不修改链表，实际 %r' % (_to_list(_head),)",
            "_head = _build(list(range(1000)))\nassert list_stats(_head) == (1000, 999), '1000 个结点（0~999）应是 (1000, 999)，实际 %r' % (list_stats(_head),)",
            "_n, _m = list_stats(_build([4, 6]))\nassert _n == 2 and _m == 6, '返回值要能解包成 (结点个数, 最大值)，实际 %r / %r' % (_n, _m)",
        ],
        'explanation': (
            '链表没有「长度」这个字段，求任何统计量都只能**走一遍**。'
            '这题把「数个数」和「求最大值」放在同一趟里完成——这也是链表题最常见的形态：'
            '**用一根指针走到底，边走边更新若干个变量**。\n\n'
            '```python\n'
            'while head is not None:\n'
            '    count += 1\n'
            '    if best is None or head.val > best:\n'
            '        best = head.val\n'
            '    head = head.next\n'
            '```\n\n'
            '**为什么 `best` 从 `None` 开始？** 如果写成 `best = 0`，'
            '遇到「全是负数」的表（如 `-3 → -1 → -7`）就会返回 0，'
            '而 0 根本不在表里。用 `None` 表示「还没装进任何值」，第一次就直接赋值。\n\n'
            '**常见错误**：\n\n'
            '1. `best = 0` 导致全负数的表答案错误；\n'
            '2. 先写一个循环数长度、再写一个循环求最大值——扫了两趟，'
            '题面明确要求一趟；\n'
            '3. 循环里写了 `head = head.next` 之后又用 `head.val`（`head` 已经是下一个结点了）；\n'
            '4. 为了省事把值拷进 Python 列表再用 `max()`，那就不是链表算法了，823 会扣分。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '(3, 5)\n(0, None)\n(3, -1)\n(3, 2)',
        'hints': ['一趟循环里同时数个数、更新最大值', '最大值初始用 None，避免「全是负数」时返回 0'],
    },
    {
        'id': 'x823-203',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '有序顺序表插入（从后往前搬移）',
        'difficulty': 1,
        'tags': ['顺序表', '插入', '原地'],
        'statement': (
            '已知顺序表 `items`**已经按升序排好**（可能为空），以及一个值 `x`。\n\n'
            '定义函数 `insert_sorted(items, x)`：把 `x` 插到正确的位置上，'
            '使表插入后仍然升序，并**返回插入后表的长度**。\n\n'
            '要求：\n\n'
            '- 用**从后往前**的扫描方式，边比较边把元素后移一位，最后把 `x` 放进空出的位置：\n\n'
            '```python\n'
            'i = len(items) - 1\n'
            'items.append(x)                 # 先扩出一个位置\n'
            'while i >= 0 and items[i] > x:\n'
            '    items[i + 1] = items[i]     # 比 x 大的元素依次后移\n'
            '    i -= 1\n'
            'items[i + 1] = x\n'
            '```\n\n'
            '- 原地修改 `items`，不许 `items.sort()` / `sorted()` / `bisect`，'
            '也不许「新建一个列表再拼回去」；\n'
            '- 有相同元素时插在哪一侧都行（结果列表是一样的），不用纠结。\n\n'
            '最后打印把 4 插进 `[1, 3, 5, 7]` 后返回的长度和列表，'
            '再打印往空表插 9、往 `[2, 2, 2]` 插 2 的结果。'
        ),
        'starter_code': 'def insert_sorted(items, x):\n    i = len(items) - 1\n    items.append(x)\n    # 从后往前，比 x 大的元素后移一位；最后把 x 写到 items[i + 1]\n    pass\n',
        'solution': (
            "def insert_sorted(items, x):\n"
            "    i = len(items) - 1\n"
            "    items.append(x)\n"
            "    while i >= 0 and items[i] > x:\n"
            "        items[i + 1] = items[i]\n"
            "        i -= 1\n"
            "    items[i + 1] = x\n"
            "    return len(items)\n"
            "\n"
            "data = [1, 3, 5, 7]\n"
            "print(insert_sorted(data, 4), data)\n"
            "empty = []\n"
            "print(insert_sorted(empty, 9), empty)\n"
            "same = [2, 2, 2]\n"
            "print(insert_sorted(same, 2), same)\n"
        ),
        'checks': [
            "_a = []\nassert insert_sorted(_a, 5) == 1 and _a == [5], '往空表插 5 应返回 1、表变成 [5]，实际 %r' % (_a,)",
            "_a = [1, 3, 5, 7]\nassert insert_sorted(_a, 4) == 5 and _a == [1, 3, 4, 5, 7], '4 应插到 3 和 5 之间，实际 %r' % (_a,)",
            "_a = [2, 3]\nassert insert_sorted(_a, 1) == 3 and _a == [1, 2, 3], '插到表头时所有元素都要后移，实际 %r' % (_a,)",
            "_a = [1, 2]\nassert insert_sorted(_a, 9) == 3 and _a == [1, 2, 9], '插到表尾时不用搬移，实际 %r' % (_a,)",
            "_a = [1, 2, 3]\ninsert_sorted(_a, 2)\nassert _a == [1, 2, 2, 3], '相同元素插在任意一侧都行，结果应是 [1, 2, 2, 3]，实际 %r' % (_a,)",
            "_a = [5, 5]\nassert insert_sorted(_a, 5) == 3 and _a == [5, 5, 5], '全是相同元素时应插成 [5, 5, 5]，实际 %r' % (_a,)",
            "_a = [-5, -3]\ninsert_sorted(_a, -4)\nassert _a == [-5, -4, -3], '负数同样要按升序插入，实际 %r' % (_a,)",
            "_a = [7]\n_ref = _a\ninsert_sorted(_a, 1)\nassert _a is _ref and _ref == [1, 7], '要求原地修改：列表对象本身要变成 [1, 7]，实际 %r' % (_ref,)",
            "_a = list(range(0, 1000, 2))\ninsert_sorted(_a, 999)\nassert len(_a) == 501 and _a[-1] == 999 and _a[:2] == [0, 2], '500 个元素里插 999 应追加到表尾（长度 501），实际长度 %r' % (len(_a),)",
            "_a = list(range(0, 2000, 2))\ninsert_sorted(_a, -1)\nassert len(_a) == 1001 and _a[0] == -1 and _a[1] == 0, '插到最前面时 1000 个元素都要后移，实际前两项 %r' % (_a[:2],)",
            "_a = [3, 3, 3, 3]\ninsert_sorted(_a, 0)\nassert _a == [0, 3, 3, 3, 3], '全相同元素中间差值更大时也要插对，实际 %r' % (_a,)",
            "assert '.sort(' not in _src and 'bisect' not in _src, '题面要求手写「从后往前搬移」的插入，不要调用 sort() 或 bisect 模块'",
        ],
        'explanation': (
            '顺序表插入的代价全在**搬移**：新元素要放在下标 `k`，'
            '那么 `k` 之后的所有元素都得整体后移一位。'
            '既然表是有序的，插入位置由「第一个比 x 大的元素」决定，'
            '所以一边找位置一边搬移就能一趟完成——**从后往前**走：\n\n'
            '```python\n'
            'i = len(items) - 1\n'
            'items.append(x)                 # 先扩出一个位置\n'
            'while i >= 0 and items[i] > x:\n'
            '    items[i + 1] = items[i]\n'
            '    i -= 1\n'
            'items[i + 1] = x\n'
            '```\n\n'
            '**为什么必须先 `append` 再搬？** `append` 把表长加一，'
            '这样每个元素都有一个合法的「后一个位置」可写；'
            '如果先搬移再 append，最后一步写入会越界。\n\n'
            '**为什么从后往前？** 后移的本质是「把 `items[i]` 写到 `items[i + 1]`」，'
            '从后往前写，`items[i + 1]` 一定是已经搬走的旧值，不会覆盖还没搬的数据；'
            '反过来从前往后写就会把右边的元素冲掉。\n\n'
            '循环条件用 `>` 而不是 `>=`：遇到与 x 相等的元素就停下来，'
            'x 插在相同元素的前面（插在后面也一样，结果相同）。\n\n'
            '**常见错误**：\n\n'
            '1. 从前往后搬，把后面没搬的元素覆盖掉；\n'
            '2. 忘记 `append`，`items[i + 1]` 下标越界；\n'
            '3. 用 `items.append(x); items.sort()`——结果对，但复杂度从 O(n) 变成 O(n log n)，'
            '而且题面明确不许用现成排序。\n\n'
            '复杂度：时间 O(n)（最坏是所有元素都后移）、额外空间 O(1)。'
        ),
        'expected_output': '5 [1, 3, 4, 5, 7]\n1 [9]\n4 [2, 2, 2, 2]',
        'hints': ['先 append 扩位，再从后往前把比 x 大的元素依次后移', '循环结束时的 i + 1 就是 x 该放的位置'],
    },
    {
        'id': 'x823-204',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '删除单链表中值最小的结点（记录前驱）',
        'difficulty': 2,
        'tags': ['单链表', '前驱指针', '最小值'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `delete_min(head)`：删除单链表中**值最小的结点**，'
            '返回删除后的头结点；空链表返回 `None`。\n\n'
            '要求：\n\n'
            '- 如果最小结点有多个，删除**最靠前**的那一个（用 `<` 比较即可）；\n'
            '- **最小结点可能就是头结点**，要单独处理；\n'
            '- 删除一个结点必须改它**前驱**的 `next`，所以扫描时要同时记住'
            '「当前最小值结点」和「它的前驱」；\n'
            '- 一趟扫描、额外空间 O(1)，**不许新建结点**、也不许把值拷进列表重建链表。\n\n'
            '最后构造 `3 → 1 → 2`，删除最小值后打印剩下的值，'
            '再打印对空链表、单结点链表 `7`、以及 `1 → 2 → 3`（最小值在头上）的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef delete_min(head):\n    # min_node 记最小结点，min_prev 记它的前驱；扫描结束后把 min_prev.next 改掉\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def delete_min(head):\n"
            "    if head is None:\n"
            "        return None\n"
            "    min_node = head\n"
            "    min_prev = None\n"
            "    prev = None\n"
            "    node = head\n"
            "    while node is not None:\n"
            "        if node.val < min_node.val:\n"
            "            min_node = node\n"
            "            min_prev = prev\n"
            "        prev = node\n"
            "        node = node.next\n"
            "    if min_prev is None:\n"
            "        return head.next\n"
            "    min_prev.next = min_node.next\n"
            "    return head\n"
            "\n"
            "def build(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        head = Node(v, head)\n"
            "    return head\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    while head is not None:\n"
            "        out.append(head.val)\n"
            "        head = head.next\n"
            "    return out\n"
            "\n"
            "print(values_of(delete_min(build([3, 1, 2]))))\n"
            "print(delete_min(None))\n"
            "print(values_of(delete_min(build([7]))))\n"
            "print(values_of(delete_min(build([1, 2, 3]))))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "def _nodes(head):\n    out = []\n    while head is not None:\n        out.append(head)\n        head = head.next\n    return out",
            "assert delete_min(None) is None, '空链表应返回 None'",
            "assert _to_list(delete_min(_build([7]))) == [], '只有一个结点时删除后应是空链表（返回 None）'",
            "assert _to_list(delete_min(_build([3, 1, 2]))) == [3, 2], '删除最小值 1 后应是 [3, 2]，实际 %r' % (_to_list(delete_min(_build([3, 1, 2]))),)",
            "assert _to_list(delete_min(_build([1, 2, 3]))) == [2, 3], '最小值在头结点时新头要后移，实际 %r' % (_to_list(delete_min(_build([1, 2, 3]))),)",
            "assert _to_list(delete_min(_build([3, 2, 1]))) == [3, 2], '最小值在尾结点时要把尾删掉，实际 %r' % (_to_list(delete_min(_build([3, 2, 1]))),)",
            "assert _to_list(delete_min(_build([2, 1, 3, 1]))) == [2, 3, 1], '最小值重复时只删最靠前的那个 1，实际 %r' % (_to_list(delete_min(_build([2, 1, 3, 1]))),)",
            "assert _to_list(delete_min(_build([5, 5, 5]))) == [5, 5], '元素全相同时删掉一个，实际 %r' % (_to_list(delete_min(_build([5, 5, 5]))),)",
            "assert _to_list(delete_min(_build([-1, -5, -3]))) == [-1, -3], '负数最小值也要正确处理，实际 %r' % (_to_list(delete_min(_build([-1, -5, -3]))),)",
            "_head = _build([1, 2, 3])\nassert delete_min(_head) is _head.next, '要求就地删除、复用结点：删除头结点后返回的就是原来的第二个结点'",
            "_head = _build([2, 3, 1, 4])\n_orig = _nodes(_head)\n_r = delete_min(_head)\nassert all(any(x is y for y in _orig) for x in _nodes(_r)), '要求复用原来的结点对象（不许新建结点）'",
            "_head = _build(list(range(300, 0, -1)))\nassert _to_list(delete_min(_head)) == list(range(300, 1, -1)), '300 个结点（最小值 1 在表尾）应删成 300~2，实际长度 %r' % (len(_to_list(delete_min(_build(list(range(300, 0, -1)))))),)",
        ],
        'explanation': (
            '删除链表结点的铁律：**要删掉一个结点，必须改它前驱的 `next`**。'
            '所以「找最小结点」这件事要连带记下**它的前驱**，否则知道最小值是谁也删不掉。\n\n'
            '```python\n'
            'while node is not None:\n'
            '    if node.val < min_node.val:\n'
            '        min_node = node\n'
            '        min_prev = prev        # 最小值换人，前驱也要一起换\n'
            '    prev = node\n'
            '    node = node.next\n'
            '```\n\n'
            '**为什么前驱要跟着最小值一起更新？** 因为 `prev` 每轮都在变'
            '（它总是「当前结点的前一个」），如果只记录 `min_node`，'
            '循环结束后 `prev` 停在尾结点上，用它去删最小值就删错人了。\n\n'
            '**头结点要单独处理**：最小结点就是头结点时，它的前驱是 `None`，'
            '此时返回 `head.next` 就完成了删除（头指针后移）。'
            '为了统一处理，教材里常给链表加一个**头结点（哨兵）**，'
            '有了哨兵，所有结点都有前驱，代码就只剩一种情况了。\n\n'
            '**常见错误**：\n\n'
            '1. 只记 `min_node` 不记前驱，最后无法删除；\n'
            '2. 找到最小值后回头再扫一遍找它的前驱——那是两趟，题面要求一趟；\n'
            '3. 忘了头结点分支，`min_prev.next` 对 `None` 取属性直接崩；\n'
            '4. 比较写成 `<=`，删除的变成最靠**后**的相同最小值。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[3, 2]\nNone\n[]\n[2, 3]',
        'hints': ['扫描时同时记录最小结点和它的前驱', '最小结点是头结点时要单独返回 head.next'],
    },
    {
        'id': 'x823-205',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '双向链表删除所有值为 x 的结点',
        'difficulty': 2,
        'tags': ['双链表', '指针', '原地'],
        'statement': (
            '请**按下面的定义**写好双向链表结点类（属性名必须一致）：\n\n'
            '```python\n'
            'class DNode:\n'
            '    def __init__(self, val=0, prev=None, next=None):\n'
            '        self.val = val\n'
            '        self.prev = prev\n'
            '        self.next = next\n'
            '```\n\n'
            '`head` 是双向链表的头结点（`head.prev is None`）。\n\n'
            '定义函数 `dremove_all(head, x)`：删除所有 `val == x` 的结点，'
            '返回删除后的头结点；空链表返回 `None`。\n\n'
            '要求：\n\n'
            '- **两个方向的指针都要接好**：删掉结点 `p` 时要做\n'
            '`p.prev.next = p.next` 与 `p.next.prev = p.prev`，'
            '缺少任何一半，从尾部往前遍历就会断链；\n'
            '- 删掉的是**头结点**时，新头的 `prev` 必须是 `None`；删掉尾结点时同理；\n'
            '- 一趟扫描、额外空间 O(1)，不许新建结点；\n'
            '- 建议先把 `p.next` 存下来再动指针（改完 `p.next` 就找不到下一个结点了）。\n\n'
            '最后构造 `1 ↔ 2 ↔ 3`，删除 1 后先打印正向的值、再打印反向的值，'
            '再打印对空链表、全部结点都是 9 的链表 `9 ↔ 9` 的结果。'
        ),
        'starter_code': 'class DNode:\n    def __init__(self, val=0, prev=None, next=None):\n        self.val = val\n        self.prev = prev\n        self.next = next\n\ndef dremove_all(head, x):\n    # 命中就接好 p.prev.next 与 p.next.prev 两处指针\n    pass\n',
        'solution': (
            "class DNode:\n"
            "    def __init__(self, val=0, prev=None, next=None):\n"
            "        self.val = val\n"
            "        self.prev = prev\n"
            "        self.next = next\n"
            "\n"
            "def dremove_all(head, x):\n"
            "    node = head\n"
            "    while node is not None:\n"
            "        nxt = node.next\n"
            "        if node.val == x:\n"
            "            if node.prev is not None:\n"
            "                node.prev.next = node.next\n"
            "            else:\n"
            "                head = node.next\n"
            "            if node.next is not None:\n"
            "                node.next.prev = node.prev\n"
            "        node = nxt\n"
            "    return head\n"
            "\n"
            "def dbuild(values):\n"
            "    head = None\n"
            "    tail = None\n"
            "    for v in values:\n"
            "        node = DNode(v)\n"
            "        node.prev = tail\n"
            "        if tail is None:\n"
            "            head = node\n"
            "        else:\n"
            "            tail.next = node\n"
            "        tail = node\n"
            "    return head\n"
            "\n"
            "def forward(head):\n"
            "    out = []\n"
            "    while head is not None:\n"
            "        out.append(head.val)\n"
            "        head = head.next\n"
            "    return out\n"
            "\n"
            "def backward_values(head):\n"
            "    node = head\n"
            "    if node is None:\n"
            "        return []\n"
            "    while node.next is not None:\n"
            "        node = node.next\n"
            "    out = []\n"
            "    while node is not None:\n"
            "        out.append(node.val)\n"
            "        node = node.prev\n"
            "    return out\n"
            "\n"
            "print(forward(dremove_all(dbuild([1, 2, 3]), 1)))\n"
            "print(backward_values(dremove_all(dbuild([1, 2, 3]), 1)))\n"
            "print(dremove_all(dbuild([]), 1))\n"
            "print(dremove_all(dbuild([9, 9]), 9))\n"
        ),
        'checks': [
            "def _dbuild(values):\n    head = None\n    tail = None\n    for v in values:\n        node = DNode(v)\n        node.prev = tail\n        if tail is None:\n            head = node\n        else:\n            tail.next = node\n        tail = node\n    return head",
            "def _dto_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "def _dcheck(head, expected):\n    forward = []\n    node = head\n    prev = None\n    while node is not None:\n        if node.prev is not prev:\n            return False, '结点的 prev 指针没接对（在第 %d 个结点处断了）' % (len(forward) + 1,)\n        forward.append(node.val)\n        prev = node\n        node = node.next\n    if forward != expected:\n        return False, '正向应为 %r，实际 %r' % (expected, forward)\n    back = []\n    while prev is not None:\n        back.append(prev.val)\n        prev = prev.prev\n    if back != expected[::-1]:\n        return False, '从尾部往前的方向接错了：%r' % (back,)\n    return True, ''",
            "_r = dremove_all(None, 1)\nassert _r is None, '空链表应返回 None，实际 %r' % (_r,)",
            "_r = dremove_all(_dbuild([5]), 5)\nassert _r is None, '只有一个结点且命中时应删成空链表（返回 None）'",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([5]), 3), [5])\nassert _ok, '没有命中的值时应原样保留，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([1, 2, 3]), 1), [2, 3])\nassert _ok, '删除头结点后应剩下 [2, 3]，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([1, 2, 3]), 3), [1, 2])\nassert _ok, '删除尾结点后应剩下 [1, 2]，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([1, 2, 3]), 2), [1, 3])\nassert _ok, '删除中间结点后应剩下 [1, 3]，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([1, 9, 9, 2]), 9), [1, 2])\nassert _ok, '连续多个 9 要全部删掉，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([9, 9, 9]), 9), [])\nassert _ok, '全是要删的值时应删成空链表，但 ' + _msg",
            "_ok, _msg = _dcheck(dremove_all(_dbuild([4, 4, 5, 4]), 3), [4, 4, 5, 4])\nassert _ok, '值有重复但都不命中时一个也不能少，但 ' + _msg",
            "_head = _dbuild([1, 2, 3])\n_second = _head.next\n_new = dremove_all(_head, 1)\nassert _new is _second, '要求复用结点并就地删除：新头应是原来的第二个结点'",
            "_new = dremove_all(_dbuild([1, 2, 3]), 1)\nassert _new.prev is None, '删除头结点后新头的 prev 必须是 None，实际 %r' % (_new.prev,)",
            "_head = _dbuild(list(range(500)))\n_orig = []\n_n = _head\nwhile _n is not None:\n    _orig.append(_n)\n    _n = _n.next\n_r = dremove_all(_head, 250)\n_kept = []\n_n = _r\nwhile _n is not None:\n    _kept.append(_n)\n    _n = _n.next\nassert len(_kept) == 499, '500 个结点删掉 1 个后应剩 499 个，实际 %r' % (len(_kept),)",
            "assert all(any(x is y for y in _orig) for x in _kept), '要求复用原来的结点对象（不许新建结点）'",
        ],
        'explanation': (
            '双向链表删除比单链表多一件事：**每个结点有两个指针，都得改**。\n\n'
            '```python\n'
            'if node.prev is not None:\n'
            '    node.prev.next = node.next        # 前驱绕过当前结点\n'
            'else:\n'
            '    head = node.next                  # 删的是头结点，头指针后移\n'
            'if node.next is not None:\n'
            '    node.next.prev = node.prev        # 后继绕过当前结点\n'
            '```\n\n'
            '**为什么头尾要特判？** 头结点的 `prev` 是 `None`，'
            '删它的时候没有「前驱」可改，只能改头指针；'
            '尾结点的 `next` 是 `None`，没有「后继」的 `prev` 可改，'
            '否则会对 `None` 取属性报错。\n\n'
            '**先存 `nxt` 再动指针**：命中时我们改了 `node.prev.next`，'
            '虽然 `node.next` 本身没被改，但习惯上先 `nxt = node.next` 更稳妥，'
            '也避免了「删完当前结点就找不到下一个」这类断链 bug。\n\n'
            '**双向链表的意义**：它能 O(1) 找到前驱，所以「按值删除」「按结点删除」'
            '都不需要额外记录前驱，代价是每个结点多一个指针域、'
            '插入删除时要多维护一条链。\n\n'
            '**常见错误**：\n\n'
            '1. 只改了 `prev.next` 没改 `next.prev`，正向看着正常、反向一遍历就断；\n'
            '2. 删头结点时忘了把新头的 `prev` 置 `None`（本题检查了这一点）；\n'
            '3. 命中后直接 `node = node.next`，看上去没问题，'
            '但若实现里先把 `node.next` 改了就会跳过结点；\n'
            '4. 新建结点重建链表——823 明确要求就地改指针。\n\n'
            '复杂度：时间 O(n)、额外空间 O(1)。'
        ),
        'expected_output': '[2, 3]\n[3, 2]\nNone\nNone',
        'hints': ['删结点时 p.prev.next 与 p.next.prev 两处都要改', '删头结点要更新 head，还要保证新头的 prev 是 None'],
    },
    {
        'id': 'x823-206',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '两个有序单链表归并（复用结点）',
        'difficulty': 2,
        'tags': ['单链表', '归并', '尾插法'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '已知两条按值**非递减**排列的单链表 `a`、`b`。\n\n'
            '定义函数 `merge_two(a, b)`：把它们归并成一条仍然非递减的链表，'
            '返回新链表的头结点；两条都空时返回 `None`。\n\n'
            '要求：\n\n'
            '- **复用原来的结点**：只改 `next` 指针，不许新建结点、不许改 `val`；\n'
            '- **保留重复值**（这里不去重，和「合并去重」那类题不同）；\n'
            '- 时间 O(m + n)、额外空间 O(1)（最多允许用**一个**临时哨兵结点）；\n'
            '- 推荐用「哨兵 + 尾指针」的写法：`tail` 始终指向结果链表的最后一个结点，'
            '每次把较小的那个结点接到 `tail.next` 上；一条走完后把另一条的剩余部分整段接上；\n'
            '- 不要用「把值读进列表排序再重建链表」。\n\n'
            '最后打印把 `1 → 3 → 5` 和 `2 → 4` 归并后的结果值，'
            '再打印空链表与 `2 → 4` 归并、以及 `1 → 1 → 2` 与 `1 → 2 → 2` 归并的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef merge_two(a, b):\n    tail = dummy = Node(0)\n    # 两边都有结点时接较小的那个；一条走完就把另一条整段接上\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def merge_two(a, b):\n"
            "    tail = dummy = Node(0)\n"
            "    while a is not None and b is not None:\n"
            "        if a.val <= b.val:\n"
            "            tail.next = a\n"
            "            a = a.next\n"
            "        else:\n"
            "            tail.next = b\n"
            "            b = b.next\n"
            "        tail = tail.next\n"
            "    tail.next = a if a is not None else b\n"
            "    return dummy.next\n"
            "\n"
            "def build(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        head = Node(v, head)\n"
            "    return head\n"
            "\n"
            "def values_of(head):\n"
            "    out = []\n"
            "    while head is not None:\n"
            "        out.append(head.val)\n"
            "        head = head.next\n"
            "    return out\n"
            "\n"
            "print(values_of(merge_two(build([1, 3, 5]), build([2, 4]))))\n"
            "print(values_of(merge_two(None, build([2, 4]))))\n"
            "print(values_of(merge_two(build([1, 1, 2]), build([1, 2, 2]))))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "def _nodes(head):\n    out = []\n    while head is not None:\n        out.append(head)\n        head = head.next\n    return out",
            "assert merge_two(None, None) is None, '两条空链表归并后应返回 None'",
            "assert _to_list(merge_two(None, _build([2, 4]))) == [2, 4], 'a 为空时结果就是 b，实际 %r' % (_to_list(merge_two(None, _build([2, 4]))),)",
            "assert _to_list(merge_two(_build([1, 3]), None)) == [1, 3], 'b 为空时结果就是 a，实际 %r' % (_to_list(merge_two(_build([1, 3]), None)),)",
            "assert _to_list(merge_two(_build([1, 3, 5]), _build([2, 4]))) == [1, 2, 3, 4, 5], '经典例子应是 [1, 2, 3, 4, 5]，实际 %r' % (_to_list(merge_two(_build([1, 3, 5]), _build([2, 4]))),)",
            "assert _to_list(merge_two(_build([2, 4]), _build([1, 3, 5]))) == [1, 2, 3, 4, 5], '两条链表对调后结果一样，实际 %r' % (_to_list(merge_two(_build([2, 4]), _build([1, 3, 5]))),)",
            "assert _to_list(merge_two(_build([1, 2]), _build([3, 4]))) == [1, 2, 3, 4], '一条整体更小时要整段接上，实际 %r' % (_to_list(merge_two(_build([1, 2]), _build([3, 4]))),)",
            "assert _to_list(merge_two(_build([3, 4]), _build([1, 2]))) == [1, 2, 3, 4], 'b 整体更小时也要整段接上，实际 %r' % (_to_list(merge_two(_build([3, 4]), _build([1, 2]))),)",
            "assert _to_list(merge_two(_build([1, 1, 2]), _build([1, 2, 2]))) == [1, 1, 1, 2, 2, 2], '重复值要全部保留（不去重），实际 %r' % (_to_list(merge_two(_build([1, 1, 2]), _build([1, 2, 2]))),)",
            "assert _to_list(merge_two(_build([5]), _build([5]))) == [5, 5], '两个相等的单结点都要保留，实际 %r' % (_to_list(merge_two(_build([5]), _build([5]))),)",
            "assert _to_list(merge_two(_build([-5, -1]), _build([-3, 0]))) == [-5, -3, -1, 0], '负数同样要正确归并，实际 %r' % (_to_list(merge_two(_build([-5, -1]), _build([-3, 0]))),)",
            "assert _to_list(merge_two(_build([7, 7, 7]), _build([7, 7]))) == [7, 7, 7, 7, 7], '全是相同值时一个都不能丢，实际 %r' % (_to_list(merge_two(_build([7, 7, 7]), _build([7, 7]))),)",
            "_a = _build([1, 3, 5])\n_b = _build([2, 4])\n_an = _nodes(_a)\n_bn = _nodes(_b)\n_r = merge_two(_a, _b)\n_rn = _nodes(_r)\nassert len(_rn) == 5, '归并后结点总数应是 5（不能丢结点），实际 %r' % (len(_rn),)",
            "assert all(any(x is y for y in _an + _bn) for x in _rn), '题面要求复用原来的结点（不许新建结点）'",
            "_a = _build([1, 3])\n_r = merge_two(_a, _build([2, 4]))\nassert _r is _a, '要求复用结点：结果的头结点应当是原来 a 的头结点（a 的首元素最小）'",
            "_a = _build(list(range(0, 600, 2)))\n_b = _build(list(range(1, 600, 2)))\nassert _to_list(merge_two(_a, _b)) == list(range(600)), '两个各 300 个元素的链表应归并成 0~599'",
        ],
        'explanation': (
            '归并两条有序链表是链表里最经典的「**尾插法**」练习：'
            '拿一个尾指针指着结果链表的末尾，每次比较两条链表的头，'
            '把小的那个结点「摘」下来接到尾巴上。\n\n'
            '```python\n'
            'tail = dummy = Node(0)\n'
            'while a is not None and b is not None:\n'
            '    if a.val <= b.val:\n'
            '        tail.next = a\n'
            '        a = a.next\n'
            '    else:\n'
            '        tail.next = b\n'
            '        b = b.next\n'
            '    tail = tail.next\n'
            'tail.next = a if a is not None else b\n'
            'return dummy.next\n'
            '```\n\n'
            '**哨兵结点（dummy）的好处**：结果链表的第一个结点也要「接」，'
            '如果不用哨兵，就得写一堆「如果这是第一个结点，那么 head = ...」的判断；'
            '用了哨兵，所有结点都接在某个结点的后面，代码只剩一种情况，'
            '最后返回 `dummy.next` 即可。哨兵是**新结点**，但只用了一个，空间仍是 O(1)。\n\n'
            '**收尾那一步不能漏**：主循环结束时有一条链表已经走完，'
            '另一条剩下的结点都是有序的、而且都比结果里的最后一个值大（或相等），'
            '所以整段接上就行，不需要再逐个比较——这正是「归并」能做到 O(m + n) 的原因。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了收尾，剩下的结点全丢；\n'
            '2. 比较写成 `a.val < b.val` 也没问题（重复值顺序不影响结果），'
            '但若在循环里「相等时两边都后移」，就会丢掉一个重复值；\n'
            '3. 忘记 `tail = tail.next`，所有结点都接在同一个位置，结果只剩两个结点；\n'
            '4. 把值读出来排序再新建链表——复杂度变成 O((m+n) log(m+n))，'
            '而且违反了「复用结点」的要求。\n\n'
            '复杂度：时间 O(m + n)、额外空间 O(1)（一个哨兵结点）。'
        ),
        'expected_output': '[1, 2, 3, 4, 5]\n[2, 4]\n[1, 1, 1, 2, 2, 2]',
        'hints': ['用哨兵结点 + 尾指针，谁的当前结点小就接谁', '一条走完后，把另一条整段接到 tail.next 上'],
    },
    {
        'id': 'x823-207',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '单链表求倒数第 k 个结点（快慢指针）',
        'difficulty': 2,
        'tags': ['单链表', '快慢指针', '一趟扫描'],
        'statement': (
            '沿用结点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `kth_from_end(head, k)`：返回单链表中**倒数第 k 个结点**的值。\n\n'
            '- `k` 从 1 开始数，`k = 1` 表示最后一个结点；\n'
            '- 若链表长度小于 `k`，或 `k <= 0`，或空链表，返回 `None`；\n'
            '- 只允许**一趟扫描**（不许先数长度再走第二趟），额外空间 O(1)。\n\n'
            '做法（快慢指针）：\n\n'
            '1. 先让 `fast` 从表头往前走 `k` 步（途中若 `fast` 变成 `None`，说明表不够长，直接返回 `None`）；\n'
            '2. 让 `slow` 从表头出发，两个指针同步前进；`fast` 走到 `None` 时，'
            '`slow` 正好停在「离表尾 k 个结点」的位置上。\n\n'
            '最后打印 `1 → 2 → 3 → 4 → 5` 的倒数第 1、第 5、第 6 个结点的结果，'
            '再打印空链表查倒数第 1 个、`k = 0` 的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef kth_from_end(head, k):\n    if k <= 0:\n        return None\n    fast = head\n    # fast 先走 k 步，再让 slow 从头出发同步前进\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def kth_from_end(head, k):\n"
            "    if k <= 0:\n"
            "        return None\n"
            "    fast = head\n"
            "    for _ in range(k):\n"
            "        if fast is None:\n"
            "            return None\n"
            "        fast = fast.next\n"
            "    slow = head\n"
            "    while fast is not None:\n"
            "        fast = fast.next\n"
            "        slow = slow.next\n"
            "    return slow.val\n"
            "\n"
            "def build(values):\n"
            "    head = None\n"
            "    for v in reversed(values):\n"
            "        head = Node(v, head)\n"
            "    return head\n"
            "\n"
            "chain = build([1, 2, 3, 4, 5])\n"
            "print(kth_from_end(chain, 1))\n"
            "print(kth_from_end(chain, 5))\n"
            "print(kth_from_end(chain, 6))\n"
            "print(kth_from_end(None, 1))\n"
            "print(kth_from_end(chain, 0))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "assert kth_from_end(None, 1) is None, '空链表应返回 None'",
            "assert kth_from_end(_build([7]), 1) == 7, '只有一个结点时倒数第 1 个就是它自己，实际 %r' % (kth_from_end(_build([7]), 1),)",
            "assert kth_from_end(_build([7]), 2) is None, 'k 超过表长应返回 None'",
            "assert kth_from_end(_build([1, 2, 3, 4, 5]), 1) == 5, '倒数第 1 个是尾结点 5，实际 %r' % (kth_from_end(_build([1, 2, 3, 4, 5]), 1),)",
            "assert kth_from_end(_build([1, 2, 3, 4, 5]), 5) == 1, '倒数第 5 个是头结点 1，实际 %r' % (kth_from_end(_build([1, 2, 3, 4, 5]), 5),)",
            "assert kth_from_end(_build([1, 2, 3, 4, 5]), 6) is None, 'k 比表长大应返回 None'",
            "assert kth_from_end(_build([1, 2, 3, 4, 5]), 0) is None, 'k = 0 无意义，应返回 None'",
            "assert kth_from_end(_build([1, 2, 3]), -2) is None, 'k 为负数应返回 None'",
            "assert kth_from_end(_build([2, 2, 2, 2]), 3) == 2, '值全相同时也要按位置取，实际 %r' % (kth_from_end(_build([2, 2, 2, 2]), 3),)",
            "assert kth_from_end(_build([9, 8, 7, 6]), 2) == 7, '倒数第 2 个应是 7，实际 %r' % (kth_from_end(_build([9, 8, 7, 6]), 2),)",
            "assert kth_from_end(_build([-1, -2, -3]), 1) == -3, '负数也要正确返回，实际 %r' % (kth_from_end(_build([-1, -2, -3]), 1),)",
            "assert kth_from_end(_build(list(range(1000))), 1000) == 0, '1000 个结点取倒数第 1000 个应是 0，实际 %r' % (kth_from_end(_build(list(range(1000))), 1000),)",
            "assert kth_from_end(_build(list(range(1000))), 1001) is None, '1000 个结点取倒数第 1001 个应返回 None'",
            "_head = _build([1, 2, 3])\nkth_from_end(_head, 2)\nassert _to_list(_head) == [1, 2, 3], '题面要求不修改链表，实际 %r' % (_to_list(_head),)",
        ],
        'explanation': (
            '「倒数第 k 个」如果先数长度再走第二趟，需要扫描两遍。'
            '快慢指针的妙处在于**用一个固定的「间距」把倒数变成顺数**：\n\n'
            '```python\n'
            'for _ in range(k):            # fast 先走 k 步\n'
            '    if fast is None:\n'
            '        return None\n'
            '    fast = fast.next\n'
            'while fast is not None:       # 同步前进，直到 fast 走出表尾\n'
            '    fast = fast.next\n'
            '    slow = slow.next\n'
            'return slow.val\n'
            '```\n\n'
            '**为什么对？** 两个指针之间的间隔始终是 k 个结点。'
            '当 `fast` 到达 `None`（尾结点之后的那个空位置）时，'
            '`slow` 与表尾的距离正好是 k，也就是倒数第 k 个。\n\n'
            '**边界**：`k <= 0` 直接返回 `None`；'
            '`fast` 在前进途中就变成 `None`，说明表长不足 k，也要返回 `None`。'
            '注意循环里写的是 `for _ in range(k)`，如果写成 `while k > 0` 就要自己记得 `k -= 1`，'
            '否则死循环。\n\n'
            '**常见错误**：\n\n'
            '1. `fast` 先走 k − 1 步（那是「第 k 个」不是「倒数第 k 个」的做法），差一格；\n'
            '2. 忘记判断 `fast is None`，表太短时对 `None` 取 `.next` 报错；\n'
            '3. 用「把结点值压进列表再取 `values[-k]`」——空间 O(n)，题面要求 O(1)。\n\n'
            '复杂度：时间 O(n)（只扫一趟）、额外空间 O(1)。'
        ),
        'expected_output': '5\n1\nNone\nNone\nNone',
        'hints': ['fast 先走 k 步（走的过程中就要判断是否为 None）', '然后 fast、slow 同步走，fast 到 None 时 slow 就是答案'],
    },
    {
        'id': 'x823-208',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '串的朴素模式匹配（BF 算法）',
        'difficulty': 2,
        'tags': ['串', '模式匹配', 'BF'],
        'statement': (
            '定义函数 `naive_index(text, pattern)`：返回 `pattern` 在 `text` 中'
            '**第一次出现的起始下标**，找不到返回 `-1`。\n\n'
            '约定：\n\n'
            '- **空模式串**（`pattern == ""`）返回 `0`（空串是任何串的子串，位置为 0）；\n'
            '- 模式串比主串长返回 `-1`；\n'
            '- 下标从 0 开始，可以匹配任意字符（含中文）。\n\n'
            '要求手写**朴素匹配（BF）**的两层循环，最坏 O(n × m)：\n\n'
            '```python\n'
            'i = 0\n'
            'while i <= n - m:          # 主串里还能放下 m 个字符\n'
            '    j = 0\n'
            '    while j < m and text[i + j] == pattern[j]:\n'
            '        j += 1\n'
            '    if j == m:\n'
            '        return i           # 全部匹配上了\n'
            '    i += 1\n'
            'return -1\n'
            '```\n\n'
            '不许用 `in` / `find` / `index` / `count` / `re` 等现成查找，'
            '也不许用切片比较（`text[i:i+m] == pattern`）代替逐字符比较。\n\n'
            '最后打印在 `"ababcabcacbab"` 中找 `"abc"`、在 `"aaabaaaab"` 中找 `"aaaab"`、'
            '以及空模式串、找不到时（`"abc"` 中找 `"d"`）的结果。'
        ),
        'starter_code': 'def naive_index(text, pattern):\n    n = len(text)\n    m = len(pattern)\n    if m == 0:\n        return 0\n    # 两层循环：外层 i 是主串里可能的起点，内层 j 逐字符比较\n    pass\n',
        'solution': (
            "def naive_index(text, pattern):\n"
            "    n = len(text)\n"
            "    m = len(pattern)\n"
            "    if m == 0:\n"
            "        return 0\n"
            "    i = 0\n"
            "    while i <= n - m:\n"
            "        j = 0\n"
            "        while j < m and text[i + j] == pattern[j]:\n"
            "            j += 1\n"
            "        if j == m:\n"
            "            return i\n"
            "        i += 1\n"
            "    return -1\n"
            "\n"
            "print(naive_index('ababcabcacbab', 'abc'))\n"
            "print(naive_index('aaabaaaab', 'aaaab'))\n"
            "print(naive_index('abc', ''))\n"
            "print(naive_index('abc', 'd'))\n"
        ),
        'checks': [
            "assert naive_index('ababcabcacbab', 'abc') == 2, '第一次出现在下标 2（不是后面的 5），实际 %r' % (naive_index('ababcabcacbab', 'abc'),)",
            "assert naive_index('aaabaaaab', 'aaaab') == 4, '经典例子应返回 4（这道题就是 KMP 的动机），实际 %r' % (naive_index('aaabaaaab', 'aaaab'),)",
            "assert naive_index('', '') == 0, '空主串配空模式串应返回 0'",
            "assert naive_index('abc', '') == 0, '空模式串应返回 0'",
            "assert naive_index('', 'a') == -1, '空主串里找不到非空模式串，应返回 -1'",
            "assert naive_index('abc', 'abcd') == -1, '模式串比主串长应返回 -1'",
            "assert naive_index('abc', 'abc') == 0, '完全相同应返回 0，实际 %r' % (naive_index('abc', 'abc'),)",
            "assert naive_index('aaa', 'aa') == 0, '有重叠时要返回最左边的起点 0，实际 %r' % (naive_index('aaa', 'aa'),)",
            "assert naive_index('abab', 'bab') == 1, '从下标 1 开始才匹配，实际 %r' % (naive_index('abab', 'bab'),)",
            "assert naive_index('aabaabaaa', 'aabaaa') == 3, '要逐个起点试到下标 3，实际 %r' % (naive_index('aabaabaaa', 'aabaaa'),)",
            "assert naive_index('abcde', 'e') == 4, '单字符模式串在表尾时应返回下标 4，实际 %r' % (naive_index('abcde', 'e'),)",
            "assert naive_index('数据结构与算法', '结构') == 2, '中文串按字符下标计数，应返回 2，实际 %r' % (naive_index('数据结构与算法', '结构'),)",
            "assert naive_index('数据结构', '构算') == -1, '中文串不匹配时应返回 -1'",
            "assert naive_index('abc', 'xbc') == -1 and naive_index('abc', 'abx') == -1, '第一位不匹配、最后一位不匹配都要返回 -1'",
            "assert naive_index('a' * 500 + 'b', 'a' * 200 + 'b') == 300, '500 个 a 加 b 里找 200 个 a 加 b，起点应是 300，实际 %r' % (naive_index('a' * 500 + 'b', 'a' * 200 + 'b'),)",
            "assert '.find(' not in _src and '.index(' not in _src and '.count(' not in _src and 'import re' not in _src, '题面要求手写 BF 的两层循环，不要用 find()/index()/count()/re 等现成查找'",
        ],
        'explanation': (
            '朴素匹配（BF，Brute Force）的思路就是「**每个可能的起点都试一遍**」：'
            '外层枚举主串中的起点 `i`，内层从 `i` 起逐字符与模式串比较，'
            '一旦整段都比完（`j == m`）就找到了。\n\n'
            '**为什么外层条件是 `i <= n - m`？** 起点 `i` 必须保证主串里还剩得下 `m` 个字符，'
            '否则后面必然比较越界。写成 `i < n` 就得在内层加一堆越界判断。\n\n'
            '**最坏情况有多坏？** 主串 `aaaa...a`（n 个 a）、模式串 `aaa...ab`（m − 1 个 a 加 b）时，'
            '每个起点都要比较 m 次才发现最后一位不匹配，总共 O(n × m)。'
            '这就是 KMP 要解决的问题：**利用已经比较过的信息，让 i 不回退**。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `text.find(pattern)` 或 `pattern in text` 直接给答案——'
            'Python 内部是优化过的算法，题目考的是你自己把 BF 写出来；\n'
            '2. 用 `text[i:i + m] == pattern` 切片比较：写法短，但每次切片都要复制 m 个字符，'
            '而且掩盖了「逐字符比较、遇到失配就换起点」这个核心过程；\n'
            '3. 循环条件写成 `i < n`，当 `i + j` 越界时 IndexError；\n'
            '4. 空模式串没特判，`m = 0` 时 `i <= n - 0` 能进循环但语义混乱。\n\n'
            '复杂度：最好 O(m)（第一个起点就命中），最坏 O(n × m)；'
            '额外空间 O(1)。'
        ),
        'expected_output': '2\n4\n0\n-1',
        'hints': ['外层枚举起点 i（i <= n - m），内层逐字符比较', 'j 走到 m 说明整段匹配成功，返回 i'],
    },
    {
        'id': 'x823-209',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': 'KMP 模式匹配（含 next 数组）',
        'difficulty': 3,
        'tags': ['串', 'KMP', 'next 数组', 'O(n+m)'],
        'statement': (
            '本题分两个函数，**必须都写**。\n\n'
            '**（1）`build_next(pattern)`**：返回 `pattern` 的 `next` 数组。\n\n'
            '本题采用「前缀函数」口径：`next` 的长度等于 `len(pattern)`，'
            '`next[i]` 表示子串 `pattern[0..i]` 的**最长相等真前后缀的长度**'
            '（真前后缀：不含整段自己）。例如：\n\n'
            '```text\n'
            'pattern = "abab"  ->  next = [0, 0, 1, 2]\n'
            'pattern = "aaaa"  ->  next = [0, 1, 2, 3]\n'
            'pattern = "abc"   ->  next = [0, 0, 0]\n'
            '```\n\n'
            '空模式串返回 `[]`。\n\n'
            '**（2）`kmp_index(text, pattern)`**：返回 `pattern` 在 `text` 中第一次出现的起始下标，'
            '找不到返回 `-1`；空模式串返回 `0`（与朴素匹配一致）。\n\n'
            '要求：\n\n'
            '- 用 `next` 数组做失配回退，**主串下标 `i` 只能前进、不许回退**，时间 O(n + m)；\n'
            '- 不许调用 `find` / `index` / `in` / `re` 等现成查找；\n'
            '- `kmp_index` 内部要调用你自己写的 `build_next`。\n\n'
            '最后打印 `"ababcabcacbab"` 中找 `"abc"`、`"aaabaaaab"` 中找 `"aaaab"` 的结果，'
            '再打印 `build_next("abab")` 和 `build_next("aaaab")`，以及空模式串的结果。'
        ),
        'starter_code': 'def build_next(pattern):\n    n = len(pattern)\n    nxt = [0] * n\n    k = 0\n    # for i in range(1, n)：失配时 k 回退到 nxt[k - 1]，匹配则 k += 1\n    pass\n\ndef kmp_index(text, pattern):\n    if len(pattern) == 0:\n        return 0\n    nxt = build_next(pattern)\n    # j 是模式串上已匹配的长度：失配时 j = nxt[j - 1]，匹配则 j += 1\n    pass\n',
        'solution': (
            "def build_next(pattern):\n"
            "    n = len(pattern)\n"
            "    nxt = [0] * n\n"
            "    k = 0\n"
            "    for i in range(1, n):\n"
            "        while k > 0 and pattern[i] != pattern[k]:\n"
            "            k = nxt[k - 1]\n"
            "        if pattern[i] == pattern[k]:\n"
            "            k += 1\n"
            "        nxt[i] = k\n"
            "    return nxt\n"
            "\n"
            "def kmp_index(text, pattern):\n"
            "    if len(pattern) == 0:\n"
            "        return 0\n"
            "    nxt = build_next(pattern)\n"
            "    j = 0\n"
            "    for i in range(len(text)):\n"
            "        while j > 0 and text[i] != pattern[j]:\n"
            "            j = nxt[j - 1]\n"
            "        if text[i] == pattern[j]:\n"
            "            j += 1\n"
            "        if j == len(pattern):\n"
            "            return i - len(pattern) + 1\n"
            "    return -1\n"
            "\n"
            "print(kmp_index('ababcabcacbab', 'abc'))\n"
            "print(kmp_index('aaabaaaab', 'aaaab'))\n"
            "print(build_next('abab'))\n"
            "print(build_next('aaaab'))\n"
            "print(kmp_index('abc', ''))\n"
        ),
        'checks': [
            "assert build_next('') == [], '空模式串的 next 应是空列表，实际 %r' % (build_next(''),)",
            "assert build_next('a') == [0], '单字符的 next 应是 [0]，实际 %r' % (build_next('a'),)",
            "assert build_next('ab') == [0, 0], '\"ab\" 没有相等真前后缀，应是 [0, 0]，实际 %r' % (build_next('ab'),)",
            "assert build_next('aa') == [0, 1], '\"aa\" 的前缀 a 与后缀 a 相等，应是 [0, 1]，实际 %r' % (build_next('aa'),)",
            "assert build_next('abc') == [0, 0, 0], '\"abc\" 应是 [0, 0, 0]，实际 %r' % (build_next('abc'),)",
            "assert build_next('abab') == [0, 0, 1, 2], '\"abab\" 应是 [0, 0, 1, 2]，实际 %r' % (build_next('abab'),)",
            "assert build_next('aaaa') == [0, 1, 2, 3], '\"aaaa\" 应是 [0, 1, 2, 3]，实际 %r' % (build_next('aaaa'),)",
            "assert build_next('aaaab') == [0, 1, 2, 3, 0], '\"aaaab\" 应是 [0, 1, 2, 3, 0]，实际 %r' % (build_next('aaaab'),)",
            "assert build_next('abcac') == [0, 0, 0, 1, 0], '\"abcac\" 应是 [0, 0, 0, 1, 0]（末尾的 a 与开头的 a 相等），实际 %r' % (build_next('abcac'),)",
            "assert build_next('ababc') == [0, 0, 1, 2, 0], '\"ababc\" 应是 [0, 0, 1, 2, 0]，实际 %r' % (build_next('ababc'),)",
            "_p = 'aaabaaabaaaab'\nassert all(build_next(_p)[i] <= i for i in range(len(_p))), 'next[i] 不可能超过 i（真前后缀不含整段自己）'",
            "assert kmp_index('ababcabcacbab', 'abc') == 2, '第一次出现在下标 2，实际 %r' % (kmp_index('ababcabcacbab', 'abc'),)",
            "assert kmp_index('aaabaaaab', 'aaaab') == 4, '经典例子应返回 4（i 不回退就不会退化成 O(n×m)），实际 %r' % (kmp_index('aaabaaaab', 'aaaab'),)",
            "assert kmp_index('abc', '') == 0, '空模式串应返回 0'",
            "assert kmp_index('', '') == 0, '两个空串应返回 0'",
            "assert kmp_index('', 'a') == -1, '空主串里找不到非空模式串'",
            "assert kmp_index('abc', 'abcd') == -1, '模式串比主串长应返回 -1'",
            "assert kmp_index('aaa', 'aa') == 0, '有重叠时要返回最左边的起点 0，实际 %r' % (kmp_index('aaa', 'aa'),)",
            "assert kmp_index('abab', 'bab') == 1 and kmp_index('aaaab', 'aab') == 2, '多组边界例子结果不对：%r / %r' % (kmp_index('abab', 'bab'), kmp_index('aaaab', 'aab'))",
            "assert kmp_index('abcde', 'e') == 4 and kmp_index('abcde', 'a') == 0, '首尾位置也要能匹配，实际 %r / %r' % (kmp_index('abcde', 'e'), kmp_index('abcde', 'a'))",
            "assert kmp_index('数据结构与算法', '结构') == 2, '中文串也要能匹配，实际 %r' % (kmp_index('数据结构与算法', '结构'),)",
            "_t = 'ab' * 300 + 'c'\nassert kmp_index(_t, 'ab' * 100 + 'c') == 400, '长串（大量重复前缀）要匹配正确：唯一的 c 在下标 600，起点应是 400，实际 %r' % (kmp_index(_t, 'ab' * 100 + 'c'),)",
            "_t = 'a' * 400 + 'b'\nassert kmp_index(_t, 'a' * 200 + 'b') == 200, '400 个 a 加 b 里找 200 个 a 加 b，起点应是 200，实际 %r' % (kmp_index(_t, 'a' * 200 + 'b'),)",
            "_t = 'x' * 1000\nassert kmp_index(_t, 'y') == -1 and kmp_index(_t, 'x' * 1001) == -1, '完全找不到的情况应返回 -1'",
            "assert '.find(' not in _src and 'import re' not in _src, '题面要求手写 KMP，不要用 find() 或 re 模块'",
        ],
        'explanation': (
            'KMP 的全部思想可以压成一句话：**主串下标不回退，用模式串自己的信息决定退到哪。**\n\n'
            '`next[i]` 是「`pattern[0..i]` 的最长相等真前后缀长度」。'
            '它的意义是：当 `pattern[i + 1]` 失配时，'
            '前面那一段已经有 `next[i]` 个字符「既开头又结尾」，'
            '把它们直接当成已经比对过，从 `next[i]` 那个位置接着比就行——主串不动。\n\n'
            '求 `next` 的过程就是「模式串自己匹配自己」：\n\n'
            '```python\n'
            'k = 0\n'
            'for i in range(1, n):\n'
            '    while k > 0 and pattern[i] != pattern[k]:\n'
            '        k = nxt[k - 1]        # 失配：退到上一个可能的前缀长度\n'
            '    if pattern[i] == pattern[k]:\n'
            '        k += 1\n'
            '    nxt[i] = k\n'
            '```\n\n'
            '`k` 只增不减（每次回退都是往下掉，但整体摊还 O(n)），所以求 `next` 是 O(m)；'
            '匹配阶段 `i` 只前进，是 O(n)。总复杂度 O(n + m)。\n\n'
            '**常见错误**：\n\n'
            '1. 回退写成 `k = nxt[k]`（下标差一格，正确的是 `nxt[k - 1]`）；\n'
            '2. `while` 条件漏掉 `k > 0`，`nxt[-1]` 会悄悄取到最后一个元素，'
            '   表现为「有时候对、有时候错」；\n'
            '3. 匹配到 `j == len(pattern)` 后忘记返回起点 `i - len(pattern) + 1`；\n'
            '4. 把 `next` 的口径搞混（有的教材用 1 起下标、`next[1] = 0`），'
            '   题面已明确用前缀函数口径，按题面写就不会错。\n\n'
            '复杂度：时间 O(n + m)、额外空间 O(m)（next 数组）。'
        ),
        'expected_output': '2\n4\n[0, 0, 1, 2]\n[0, 1, 2, 3, 0]\n0',
        'hints': ['next[i] 是 pattern[0..i] 的最长相等真前后缀长度', '失配时 j = nxt[j - 1]，主串下标 i 永不回退'],
    },
    {
        'id': 'x823-210',
        'track': 'algorithm',
        'chapter_id': 143,
        'chapter_title': '823·线性表与串（提高）',
        'topic': '823·线性表与串（提高）',
        'title': '判断两个串是否互为循环移位（串匹配应用）',
        'difficulty': 3,
        'tags': ['串', 'KMP', '循环移位'],
        'statement': (
            '定义函数 `is_rotation(s, t)`：判断 `t` 是不是 `s` 的**循环移位**'
            '（把 `s` 左移若干位得到的串，移位 0 次也算），是返回 `True`，否返回 `False`。\n\n'
            '例如 `s = "abc"` 时，`"cab"` 是它的循环移位（`"abc"` 左移 2 位），'
            '`"acb"` 不是；`"abcabc"` 与 `"bcabca"` 互为循环移位。\n\n'
            '约定：\n\n'
            '- 两个串长度不等返回 `False`；两个空串返回 `True`；\n'
            '- `t` 是 `s` 的循环移位 **等价于** 「`t` 是 `s + s` 的子串」，'
            '所以核心就是一次子串查找；\n'
            '- **必须自己写查找（KMP 或朴素匹配都行，要 O(n + m) 的 KMP 更好）**，'
            '不许用 `in` 运算符、`find`、`index`、`re` 等现成查找；\n'
            '- 特别提醒：`s = ""` 时 `s + s` 仍是空串，'
            '而 `t` 也是空串，所以空串要单独处理（直接返回 `True`），'
            '否则「空串是空串的子串」这个约定会让你返回错误结果。\n\n'
            '最后打印 `is_rotation("abc", "cab")`、`is_rotation("abc", "acb")`、'
            '`is_rotation("", "")`、`is_rotation("abcabc", "bcabca")` 的结果。'
        ),
        'starter_code': 'def build_next(pattern):\n    # 可以直接复用上一题写的 KMP\n    pass\n\ndef is_rotation(s, t):\n    if len(s) != len(t):\n        return False\n    if len(s) == 0:\n        return True\n    text = s + s\n    # 在 text 中用 KMP 查找 t\n    pass\n',
        'solution': (
            "def build_next(pattern):\n"
            "    n = len(pattern)\n"
            "    nxt = [0] * n\n"
            "    k = 0\n"
            "    for i in range(1, n):\n"
            "        while k > 0 and pattern[i] != pattern[k]:\n"
            "            k = nxt[k - 1]\n"
            "        if pattern[i] == pattern[k]:\n"
            "            k += 1\n"
            "        nxt[i] = k\n"
            "    return nxt\n"
            "\n"
            "def kmp_find(text, pattern):\n"
            "    if len(pattern) == 0:\n"
            "        return 0\n"
            "    nxt = build_next(pattern)\n"
            "    j = 0\n"
            "    for i in range(len(text)):\n"
            "        while j > 0 and text[i] != pattern[j]:\n"
            "            j = nxt[j - 1]\n"
            "        if text[i] == pattern[j]:\n"
            "            j += 1\n"
            "        if j == len(pattern):\n"
            "            return i - len(pattern) + 1\n"
            "    return -1\n"
            "\n"
            "def is_rotation(s, t):\n"
            "    if len(s) != len(t):\n"
            "        return False\n"
            "    if len(s) == 0:\n"
            "        return True\n"
            "    return kmp_find(s + s, t) != -1\n"
            "\n"
            "print(is_rotation('abc', 'cab'))\n"
            "print(is_rotation('abc', 'acb'))\n"
            "print(is_rotation('', ''))\n"
            "print(is_rotation('abcabc', 'bcabca'))\n"
        ),
        'checks': [
            "assert is_rotation('', '') is True, '两个空串互为循环移位，应返回 True'",
            "assert is_rotation('', 'a') is False, '长度不等应返回 False'",
            "assert is_rotation('a', 'a') is True, '单字符相同即互为循环移位，实际 %r' % (is_rotation('a', 'a'),)",
            "assert is_rotation('a', 'b') is False, '单字符不同应返回 False'",
            "assert is_rotation('ab', 'ba') is True, 'ba 是 ab 左移 1 位的结果，实际 %r' % (is_rotation('ab', 'ba'),)",
            "assert is_rotation('ab', 'ab') is True, '移位 0 次也算循环移位，实际 %r' % (is_rotation('ab', 'ab'),)",
            "assert is_rotation('abc', 'abc') is True, '自己当然是自己移位 0 次的结果'",
            "assert is_rotation('abc', 'cab') is True, 'cab 是 abc 左移 2 位的结果，实际 %r' % (is_rotation('abc', 'cab'),)",
            "assert is_rotation('abc', 'bca') is True, 'bca 是 abc 左移 1 位的结果，实际 %r' % (is_rotation('abc', 'bca'),)",
            "assert is_rotation('abc', 'acb') is False, 'acb 不是 abc 的循环移位，实际 %r' % (is_rotation('abc', 'acb'),)",
            "assert is_rotation('abcd', 'abdc') is False, '只交换了末尾两位不算循环移位，实际 %r' % (is_rotation('abcd', 'abdc'),)",
            "assert is_rotation('abcabc', 'bcabca') is True, 'abcabc 左移 1 位就是 bcabca，实际 %r' % (is_rotation('abcabc', 'bcabca'),)",
            "assert is_rotation('aab', 'aba') is True, '有重复字符时 aba 也是循环移位，实际 %r' % (is_rotation('aab', 'aba'),)",
            "assert is_rotation('aab', 'baa') is True, '有重复字符时 baa 也是循环移位，实际 %r' % (is_rotation('aab', 'baa'),)",
            "assert is_rotation('aab', 'abb') is False, '字符个数不同应返回 False，实际 %r' % (is_rotation('aab', 'abb'),)",
            "assert is_rotation('aaaa', 'aaaa') is True, '全是相同字符当然互为循环移位'",
            "assert is_rotation('aaab', 'aaba') is True, 'aaab 左移 3 位得到 aaba，实际 %r' % (is_rotation('aaab', 'aaba'),)",
            "assert is_rotation('abcde', 'cdeab') is True, 'abcde 左移 2 位得到 cdeab，实际 %r' % (is_rotation('abcde', 'cdeab'),)",
            "assert is_rotation('abcde', 'cdeac') is False, '差一个字符也要判 False，实际 %r' % (is_rotation('abcde', 'cdeac'),)",
            "assert is_rotation('abab', 'baba') is True and is_rotation('abab', 'abba') is False, '两种容易混淆的情况要分清，实际 %r / %r' % (is_rotation('abab', 'baba'), is_rotation('abab', 'abba'))",
            "assert is_rotation('数据结构', '结构数据') is True, '中文串也能判断循环移位，实际 %r' % (is_rotation('数据结构', '结构数据'),)",
            "_s = 'ab' * 200\nassert is_rotation(_s, 'ba' * 200) is True, '400 个字符的长串也要在 O(n) 内判完，实际 %r' % (is_rotation(_s, 'ba' * 200),)",
            "_s = 'a' * 500\nassert is_rotation(_s, 'a' * 500) is True and is_rotation(_s, 'a' * 499 + 'b') is False, '大量重复字符的串也是 O(n)，实际 %r' % (is_rotation(_s, 'a' * 499 + 'b'),)",
            "assert '.find(' not in _src and 'import re' not in _src, '题面要求自己写查找（KMP），不要用 find() 或 re 模块'",
        ],
        'explanation': (
            '这题的关键在**一个等价转换**：\n\n'
            '> `t` 是 `s` 的循环移位  ⟺  `t` 是 `s + s` 的子串。\n\n'
            '为什么？把 `s + s` 展开看，每个长度为 `len(s)` 的窗口都正好是'
            '「从某个位置开始、绕一圈回来」的串，也就是 `s` 的某次循环移位；'
            '反过来任何一次循环移位都对应其中一个窗口。\n\n'
            '```python\n'
            'if len(s) != len(t):\n'
            '    return False\n'
            'if len(s) == 0:\n'
            '    return True\n'
            'return kmp_find(s + s, t) != -1\n'
            '```\n\n'
            '**为什么长度必须先判？** 不判的话 `s = "ab"`、`t = "a"` 时'
            '`"a"` 是 `"abab"` 的子串，会被误判成循环移位。'
            '题目里的「循环移位」必须长度相等。\n\n'
            '**空串为什么要单独处理？** 空串长度相等时 `s + s = ""`，'
            '按「空模式串返回 0」的约定会返回 `-1`；'
            '而按定义「空串左移 0 位还是空串」，两个空串应当互为循环移位。'
            '这类边界是 823 阅卷时的常见扣分点。\n\n'
            '**常见错误**：\n\n'
            '1. 用 `t in s + s` 一行搞定——在 Python 里是做对了，'
            '但考试要求你写出查找过程（真题会明确要求 KMP）；\n'
            '2. 忘记判长度，被长度更短的子串误判；\n'
            '3. 用朴素的 `s + s` 逐字符比较（每滑动一格都比较 len(s) 个字符），'
            '最坏退化到 O(n²)，而 KMP 是 O(n + m)。\n\n'
            '复杂度：时间 O(n + m)（KMP 查找，本处 n = m = len(s)，即 O(len(s))）、'
            '额外空间 O(len(s))（`s + s` 与 next 数组）。'
        ),
        'expected_output': 'True\nFalse\nTrue\nTrue',
        'hints': ['t 是 s 的循环移位等价于 t 在 s + s 里出现', '先判长度相等，再特判空串，最后用自己写的 KMP 查找'],
    },
    # ── 专题 128 823·栈与队列 ─────────────────────────────
    {
        'id': 'x823-211',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '用栈做进制转换（十进制的 2~16 进制）',
        'difficulty': 1,
        'tags': ['栈', '进制转换', '取余'],
        'statement': (
            '定义函数 `dec_to_base(n, base)`：把十进制**非负整数** `n` 转成 `base` 进制'
            '（`2 <= base <= 16`）的字符串，并返回它。\n\n'
            '约定：\n\n'
            '- `n = 0` 返回 `"0"`（这是最容易漏的边界）；\n'
            '- 大于 9 的数位用**大写字母** `A`~`F` 表示，比如 16 进制里 255 是 `"FF"`；\n'
            '- 必须用**栈**（就用 Python 列表 `append` / `pop`）：\n\n'
            '```text\n'
            'n = 10, base = 2：\n'
            '  10 % 2 = 0  -> 压栈 [0]\n'
            '   5 % 2 = 1  -> 压栈 [0, 1]\n'
            '   2 % 2 = 0  -> 压栈 [0, 1, 0]\n'
            '   1 % 2 = 1  -> 压栈 [0, 1, 0, 1]\n'
            '   反复整除到 0，再依次弹栈：1 0 1 0\n'
            '```\n\n'
            '- 不许用 `bin()` / `oct()` / `hex()` / `format()` 之类现成的进制转换函数；\n'
            '- 数位表可以用字符串 `digits = "0123456789ABCDEF"`，'
            '弹出来的余数就是它的下标。\n\n'
            '最后打印 `dec_to_base(10, 2)`、`dec_to_base(255, 16)`、'
            '`dec_to_base(0, 2)`、`dec_to_base(1000000, 16)` 的结果。'
        ),
        'starter_code': 'def dec_to_base(n, base):\n    digits = "0123456789ABCDEF"\n    if n == 0:\n        return "0"\n    # 反复取余压栈，最后弹栈拼字符串\n    pass\n',
        'solution': (
            "def dec_to_base(n, base):\n"
            "    digits = '0123456789ABCDEF'\n"
            "    if n == 0:\n"
            "        return '0'\n"
            "    stack = []\n"
            "    while n > 0:\n"
            "        stack.append(n % base)\n"
            "        n //= base\n"
            "    out = []\n"
            "    while stack:\n"
            "        out.append(digits[stack.pop()])\n"
            "    return ''.join(out)\n"
            "\n"
            "print(dec_to_base(10, 2))\n"
            "print(dec_to_base(255, 16))\n"
            "print(dec_to_base(0, 2))\n"
            "print(dec_to_base(1000000, 16))\n"
        ),
        'checks': [
            "assert dec_to_base(0, 2) == '0', 'n = 0 应返回 \"0\"，实际 %r' % (dec_to_base(0, 2),)",
            "assert dec_to_base(0, 16) == '0', 'n = 0、base = 16 也应返回 \"0\"，实际 %r' % (dec_to_base(0, 16),)",
            "assert dec_to_base(1, 2) == '1', '1 的二进制是 \"1\"，实际 %r' % (dec_to_base(1, 2),)",
            "assert dec_to_base(10, 2) == '1010', '10 的二进制应是 \"1010\"（弹栈顺序不能反），实际 %r' % (dec_to_base(10, 2),)",
            "assert dec_to_base(255, 2) == '11111111', '255 的二进制应是 8 个 1，实际 %r' % (dec_to_base(255, 2),)",
            "assert dec_to_base(1023, 2) == '1111111111', '1023 的二进制应是 10 个 1，实际 %r' % (dec_to_base(1023, 2),)",
            "assert dec_to_base(7, 8) == '7', '7 的八进制是 \"7\"，实际 %r' % (dec_to_base(7, 8),)",
            "assert dec_to_base(8, 8) == '10', '8 的八进制应是 \"10\"，实际 %r' % (dec_to_base(8, 8),)",
            "assert dec_to_base(100, 7) == '202', '100 的七进制应是 \"202\"，实际 %r' % (dec_to_base(100, 7),)",
            "assert dec_to_base(16, 16) == '10', '16 的十六进制应是 \"10\"，实际 %r' % (dec_to_base(16, 16),)",
            "assert dec_to_base(35, 16) == '23', '35 = 2 × 16 + 3，应返回 \"23\"，实际 %r' % (dec_to_base(35, 16),)",
            "assert dec_to_base(255, 16) == 'FF', '255 的十六进制应是 \"FF\"（大于 9 的数位用大写字母），实际 %r' % (dec_to_base(255, 16),)",
            "assert dec_to_base(1000000, 16) == 'F4240', '1000000 的十六进制应是 \"F4240\"，实际 %r' % (dec_to_base(1000000, 16),)",
            "assert dec_to_base(1000000, 2).count('1') == 7, '1000000 的二进制应含 7 个 1（1000000 = 0b11110100001001000000），实际 %r 个' % (dec_to_base(1000000, 2).count('1'),)",
            "assert dec_to_base(1000000, 2)[0] == '1', '转换结果的第一位（栈底）必须是最高位、且是 1，实际 %r' % (dec_to_base(1000000, 2)[:4],)",
            "assert 'bin(' not in _src and 'oct(' not in _src and 'hex(' not in _src and 'format(' not in _src, '题面要求用栈自己做进制转换，不要用 bin()/oct()/hex()/format()'",
        ],
        'explanation': (
            '进制转换的原理是**除基取余**：`n % base` 得到**最低位**，'
            '`n // base` 把它去掉，继续求下一位，直到 `n` 变成 0。\n\n'
            '注意余数的产生顺序是**从低位到高位**，而我们写数是从高位到低位，'
            '所以需要一个「后进先出」的容器把顺序倒过来——这正是栈的用武之地：\n\n'
            '```python\n'
            'while n > 0:\n'
            '    stack.append(n % base)      # 低位先进栈\n'
            '    n //= base\n'
            'while stack:\n'
            '    out.append(digits[stack.pop()])   # 高位先出栈\n'
            '```\n\n'
            '**为什么 `n = 0` 要单独返回 "0"？** 循环条件是 `n > 0`，'
            'n = 0 时一次都不进循环，栈是空的，拼出来是空字符串——'
            '而 0 的正确表示是 `"0"`。这是本题最常见的失分点。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记 `n = 0` 的边界；\n'
            '2. 把余数直接拼在字符串右边（`result += digits[rem]`），得到的数位是反的；\n'
            '3. 用 `hex(n)[2:]` 之类偷懒，题目考的就是栈；\n'
            '4. 数位表写成小写 `abcdef`，虽然能解释，但题面约定大写。\n\n'
            '复杂度：时间 O(log_base n)（数位个数）、额外空间 O(log_base n)（栈）。'
        ),
        'expected_output': '1010\nFF\n0\nF4240',
        'hints': ['取余得到低位，压栈；整除去掉低位，继续', '最后弹栈拼串，顺序自然从高位到低位'],
    },
    {
        'id': 'x823-212',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '括号匹配（栈的经典应用）',
        'difficulty': 1,
        'tags': ['栈', '括号匹配', '字符串'],
        'statement': (
            '定义函数 `is_balanced(s)`：判断字符串 `s` 里的括号是否**配对正确**。\n\n'
            '`s` 中只会出现这六种字符：`(` `)` `[` `]` `{` `}`（也可能为空串）。\n\n'
            '配对正确指：\n\n'
            '- 每个左括号都有对应的右括号，类型一致、顺序正确（`"([)]"` 是错的）；\n'
            '- 任何前缀里左括号都不少于右括号（`")("` 是错的）；\n'
            '- 空串算配对正确，返回 `True`。\n\n'
            '要求**用栈**（列表 `append` / `pop`），时间 O(n)、额外空间 O(n)：\n\n'
            '```python\n'
            'pairs = {")": "(", "]": "[", "}": "{"}\n'
            'for ch in s:\n'
            '    if ch in "([{":\n'
            '        stack.append(ch)             # 左括号进栈\n'
            '    else:\n'
            '        if not stack or stack.pop() != pairs[ch]:\n'
            '            return False             # 右括号多了，或类型不对\n'
            'return not stack                         # 栈空才算全部配对\n'
            '```\n\n'
            '最后打印 `"{[()]}"`、`"([)]"`、空串、`"((("` 四个例子的结果。'
        ),
        'starter_code': 'def is_balanced(s):\n    pairs = {")": "(", "]": "[", "}": "{"}\n    stack = []\n    # 左括号压栈；右括号要和栈顶配对，最后栈必须是空的\n    pass\n',
        'solution': (
            "def is_balanced(s):\n"
            "    pairs = {')': '(', ']': '[', '}': '{'}\n"
            "    stack = []\n"
            "    for ch in s:\n"
            "        if ch in '([{':\n"
            "            stack.append(ch)\n"
            "        else:\n"
            "            if not stack or stack.pop() != pairs[ch]:\n"
            "                return False\n"
            "    return not stack\n"
            "\n"
            "print(is_balanced('{[()]}'))\n"
            "print(is_balanced('([)]'))\n"
            "print(is_balanced(''))\n"
            "print(is_balanced('((('))\n"
        ),
        'checks': [
            "assert is_balanced('') is True, '空串算配对正确，应返回 True'",
            "assert is_balanced('()') is True, '一对圆括号是配对的'",
            "assert is_balanced('()[]{}') is True, '三种括号并排都是配对的'",
            "assert is_balanced('{[()]}') is True, '嵌套的括号应返回 True，实际 %r' % (is_balanced('{[()]}'),)",
            "assert is_balanced('((()))') is True, '三层嵌套圆括号应返回 True，实际 %r' % (is_balanced('((()))'),)",
            "assert is_balanced('([{}])') is True, '交替嵌套应返回 True，实际 %r' % (is_balanced('([{}])'),)",
            "assert is_balanced('(') is False, '只有左括号不配对，应返回 False'",
            "assert is_balanced(')') is False, '只有右括号不配对，应返回 False'",
            "assert is_balanced('(((') is False, '全是左括号应返回 False'",
            "assert is_balanced(')))') is False, '全是右括号应返回 False'",
            "assert is_balanced(')(') is False, '右括号在前不合法，应返回 False'",
            "assert is_balanced('([)]') is False, '交叉嵌套（类型顺序不对）应返回 False，实际 %r' % (is_balanced('([)]'),)",
            "assert is_balanced('{[]') is False, '少了右花括号应返回 False'",
            "assert is_balanced('[]}') is False, '多了一个右花括号应返回 False'",
            "assert is_balanced('()()') is True, '并列的多组括号应返回 True'",
            "assert is_balanced('({[)]}') is False, '括号类型错配应返回 False，实际 %r' % (is_balanced('({[)]}'),)",
            "assert is_balanced('(' * 500 + ')' * 500) is True, '500 层嵌套必须能判对（不要用递归，也不要靠数个数）'",
            "assert is_balanced('(' * 500 + ')' * 499) is False, '少一个右括号应返回 False'",
            "assert is_balanced('(' * 300 + ')' * 300 + '[') is False, '末尾多一个左方括号应返回 False'",
            "assert is_balanced('()[{}]()') is True, '多段并列嵌套应返回 True，实际 %r' % (is_balanced('()[{}]()'),)",
            "assert 'append(' in _src and 'pop()' in _src, '题面要求用栈（列表的 append / pop）来实现括号匹配'",
        ],
        'explanation': (
            '括号匹配是栈最经典的应用：**扫描一遍，左括号等着右括号来配**，'
            '而「最近出现的左括号最先被配对」正是后进先出。\n\n'
            '```python\n'
            'for ch in s:\n'
            '    if ch in "([{":\n'
            '        stack.append(ch)\n'
            '    else:\n'
            '        if not stack or stack.pop() != pairs[ch]:\n'
            '            return False\n'
            'return not stack\n'
            '```\n\n'
            '**两个失败分支**：\n\n'
            '1. 来了一个右括号，但栈是空的 → 「右括号比左括号多」，直接 False；\n'
            '2. 栈顶的左括号类型不对 → 「交叉嵌套」（如 `"([)]"`），也 False。\n\n'
            '**为什么最后要检查 `not stack`？** 扫描结束时如果栈里还有左括号'
            '（如 `"((("`），说明有左括号没被配对，也要返回 False。'
            '这一步最容易忘，忘了就会把 `"((("` 判成 True。\n\n'
            '**为什么不能只数个数？** 只统计左右括号数量相等会把 `")("` 判成正确，'
            '而它任何时刻前缀都不合法——这正是「用栈」而不是「用计数器」的原因。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记最后的 `not stack`；\n'
            '2. 用 `stack.pop()` 之前没判空，`")"` 会 IndexError；\n'
            '3. 递归写法在 500 层嵌套时 RecursionError（本题数据就有 500 层）。\n\n'
            '复杂度：时间 O(n)、额外空间 O(n)（最坏全是左括号）。'
        ),
        'expected_output': 'True\nFalse\nTrue\nFalse',
        'hints': ['左括号进栈；遇到右括号先判空，再和栈顶比对类型', '扫完之后栈必须是空的，否则说明还有左括号没配对'],
    },
    {
        'id': 'x823-213',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '用栈判断回文串（只压前半部分）',
        'difficulty': 1,
        'tags': ['栈', '回文', '串'],
        'statement': (
            '定义函数 `is_palindrome_stack(s)`：用**栈**判断字符串 `s` 是不是**回文串**'
            '（正着读和倒着读一样），是返回 `True`，否返回 `False`。\n\n'
            '要求：\n\n'
            '- 只把**前一半**字符依次压栈：`half = len(s) // 2`，把 `s[0] ~ s[half - 1]` 压栈；\n'
            '- 然后从 `len(s) - half` 这个位置开始，用后一半的字符与弹栈得到的字符逐一比较'
            '（弹栈的顺序正好是「前一半的倒序」）；\n'
            '- 一旦不相等立刻返回 `False`，全部比完返回 `True`；\n'
            '- 奇数长度时**中间那个字符不参与比较**（它和谁比都是自己）；\n'
            '- 空串和一个字符都算回文；\n'
            '- 时间 O(n)、额外空间 O(n / 2)（不要整个串压栈，也不要写 `s == s[::-1]` 偷懒）。\n\n'
            '最后打印 `"abba"`、`"abcba"`、`"ab"`、空串四个例子的结果。'
        ),
        'starter_code': 'def is_palindrome_stack(s):\n    n = len(s)\n    half = n // 2\n    stack = []\n    # 把前一半压栈，再用后一半与弹栈结果逐一比较\n    pass\n',
        'solution': (
            "def is_palindrome_stack(s):\n"
            "    n = len(s)\n"
            "    half = n // 2\n"
            "    stack = []\n"
            "    for i in range(half):\n"
            "        stack.append(s[i])\n"
            "    for i in range(n - half, n):\n"
            "        if stack.pop() != s[i]:\n"
            "            return False\n"
            "    return True\n"
            "\n"
            "print(is_palindrome_stack('abba'))\n"
            "print(is_palindrome_stack('abcba'))\n"
            "print(is_palindrome_stack('ab'))\n"
            "print(is_palindrome_stack(''))\n"
        ),
        'checks': [
            "assert is_palindrome_stack('') is True, '空串算回文'",
            "assert is_palindrome_stack('a') is True, '单个字符算回文'",
            "assert is_palindrome_stack('aa') is True, '两个相同字符是回文'",
            "assert is_palindrome_stack('ab') is False, '两个不同字符不是回文，实际 %r' % (is_palindrome_stack('ab'),)",
            "assert is_palindrome_stack('aba') is True, '奇数长度的回文（中间字符不参与比较），实际 %r' % (is_palindrome_stack('aba'),)",
            "assert is_palindrome_stack('abc') is False, '三个字符不同不是回文，实际 %r' % (is_palindrome_stack('abc'),)",
            "assert is_palindrome_stack('abba') is True, 'abba 是回文，实际 %r' % (is_palindrome_stack('abba'),)",
            "assert is_palindrome_stack('abca') is False, 'abca 不是回文，实际 %r' % (is_palindrome_stack('abca'),)",
            "assert is_palindrome_stack('abcba') is True, 'abcba 是回文，实际 %r' % (is_palindrome_stack('abcba'),)",
            "assert is_palindrome_stack('abcddcba') is True, 'abcddcba 是回文，实际 %r' % (is_palindrome_stack('abcddcba'),)",
            "assert is_palindrome_stack('abcdecba') is False, 'abcdecba 中间不一样，应返回 False'",
            "assert is_palindrome_stack('12321') is True, '数字组成的回文也要判对，实际 %r' % (is_palindrome_stack('12321'),)",
            "assert is_palindrome_stack('上海自来水来自海上') is True, '中文回文也要判对，实际 %r' % (is_palindrome_stack('上海自来水来自海上'),)",
            "assert is_palindrome_stack('数据结构') is False, '中文非回文应返回 False'",
            "assert is_palindrome_stack('a' * 4001) is True, '4001 个相同字符是回文'",
            "assert is_palindrome_stack('a' * 2000 + 'b' + 'a' * 2000) is True, '4001 个字符、中间夹一个 b 仍是回文'",
            "assert is_palindrome_stack('a' * 2000 + 'b' + 'a' * 1999 + 'c') is False, '最后一位不同应返回 False'",
            "assert is_palindrome_stack('ab' * 1500) is False and is_palindrome_stack('ab' * 750 + 'ba' * 750) is True, '3000 个字符的两例要判对（(ab)^1500 不是回文，(ab)^750(ba)^750 是回文）：%r / %r' % (is_palindrome_stack('ab' * 1500), is_palindrome_stack('ab' * 750 + 'ba' * 750))",
            "assert 'append(' in _src and 'pop()' in _src, '题面要求用栈（列表的 append / pop）实现回文判断'",
            "assert '[::-1]' not in _src, '题面要求用栈比较，不要用切片反转（s[::-1]）走捷径'",
        ],
        'explanation': (
            '回文的本质是「**第 i 个字符与倒数第 i 个字符相同**」。'
            '栈能把「前一半」变成「倒序」，于是比较就变成了「弹一个、比一个」。\n\n'
            '```python\n'
            'half = n // 2\n'
            'for i in range(half):\n'
            '    stack.append(s[i])          # 前一半：s[0] ~ s[half-1]\n'
            'for i in range(n - half, n):     # 后一半：s[n-half] ~ s[n-1]\n'
            '    if stack.pop() != s[i]:\n'
            '        return False\n'
            '```\n\n'
            '**后一半从哪里开始？** 是 `n - half`，不是 `half`。'
            '奇数长度时 `half = n // 2` 向下取整，中间那个字符的下标正好是 `half`，'
            '它既不压栈、也不参与比较：比如 `"abcba"`，`half = 2`，'
            '压栈 a、b，后一半从下标 3 开始是 b、a，中间的下标 2（c）被跳过。\n\n'
            '**为什么只要 O(n/2) 空间？** 压栈的只有前一半，'
            '后一半直接和弹出来的字符比，不需要额外存。'
            '如果整个串都压栈，虽然答案也对，但空间是本解的两倍，'
            '题面（以及真题）强调的正是「一半就够」。\n\n'
            '**常见错误**：\n\n'
            '1. 后一半的起点写成 `half`，奇数长度时中间的字符被比了两次，结果错乱；\n'
            '2. 用 `s == s[::-1]` 一行给答案——题面明确要求用栈；\n'
            '3. 忘记判空栈（`stack.pop()` 对空栈会 IndexError）——'
            '按上面的边界，后一半长度不超过前一半，正常写法不会弹空；\n'
            '4. 用 `for ch in s[half:]` 但忘了奇数长度要先跳过中间字符。\n\n'
            '复杂度：时间 O(n)、额外空间 O(n / 2)。'
        ),
        'expected_output': 'True\nTrue\nFalse\nTrue',
        'hints': ['half = n // 2，把前一半压栈', '后一半从下标 n - half 开始，与弹栈结果逐一比较'],
    },
    {
        'id': 'x823-214',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '循环队列的实现（牺牲一个单元判满）',
        'difficulty': 2,
        'tags': ['队列', '循环队列', '判空判满'],
        'statement': (
            '请定义一个类 `CircularQueue`，用**循环队列**（顺序存储、下标取模回绕）'
            '实现先进先出的队列。\n\n'
            '构造要求：`CircularQueue(capacity)`，内部用一个长度正好是 `capacity` 的列表'
            '（属性名随便取），下标 `front` 指向队头元素、`rear` 指向**队尾元素的下一个空位**。\n\n'
            '**用「牺牲一个存储单元」区分队空和队满**（这是教材写法）：\n\n'
            '- 队空：`front == rear`\n'
            '- 队满：`(rear + 1) % capacity == front`\n'
            '- 因此队列里最多只能放 `capacity - 1` 个元素！'
            '比如 `capacity = 3` 时最多存 2 个，第 3 个要入队必须先出队。\n\n'
            '必须实现的方法：\n\n'
            '- `is_empty()`：队空返回 True；\n'
            '- `is_full()`：队满返回 True；\n'
            '- `enqueue(x)`：入队成功返回 True；**队满时返回 False 且不覆盖已有元素**；\n'
            '- `dequeue()`：出队并返回队头元素；**队空时返回 `None`**；\n'
            '- `size()`：返回当前元素个数。\n\n'
            '入队时 `rear` 要写成 `self.rear = (self.rear + 1) % capacity` 这样**绕回来**，'
            '出队同理，不许用「整体搬移元素」或 `pop(0)` 的方式。\n\n'
            '最后构造容量 3 的队列，依次打印「是否为空/是否满」「入队 1、入队 2 的结果」'
            '「是否满、入队 3 的结果」「连续出队三次的结果」。'
        ),
        'starter_code': 'class CircularQueue:\n    def __init__(self, capacity):\n        self.capacity = capacity\n        self.data = [None] * capacity\n        self.front = 0\n        self.rear = 0\n\n    def is_empty(self):\n        pass\n\n    def is_full(self):\n        pass\n\n    def enqueue(self, x):\n        pass\n\n    def dequeue(self):\n        pass\n\n    def size(self):\n        pass\n',
        'solution': (
            "class CircularQueue:\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.data = [None] * capacity\n"
            "        self.front = 0\n"
            "        self.rear = 0\n"
            "\n"
            "    def is_empty(self):\n"
            "        return self.front == self.rear\n"
            "\n"
            "    def is_full(self):\n"
            "        return (self.rear + 1) % self.capacity == self.front\n"
            "\n"
            "    def enqueue(self, x):\n"
            "        if self.is_full():\n"
            "            return False\n"
            "        self.data[self.rear] = x\n"
            "        self.rear = (self.rear + 1) % self.capacity\n"
            "        return True\n"
            "\n"
            "    def dequeue(self):\n"
            "        if self.is_empty():\n"
            "            return None\n"
            "        value = self.data[self.front]\n"
            "        self.data[self.front] = None\n"
            "        self.front = (self.front + 1) % self.capacity\n"
            "        return value\n"
            "\n"
            "    def size(self):\n"
            "        return (self.rear - self.front) % self.capacity\n"
            "\n"
            "q = CircularQueue(3)\n"
            "print(q.is_empty(), q.is_full())\n"
            "print(q.enqueue(1), q.enqueue(2))\n"
            "print(q.is_full(), q.enqueue(3))\n"
            "print(q.dequeue(), q.dequeue(), q.dequeue())\n"
        ),
        'checks': [
            "_q = CircularQueue(3)\nassert _q.is_empty(), '新建的队列应为空，实际 is_empty() = %r' % (_q.is_empty(),)",
            "_q = CircularQueue(3)\nassert not _q.is_full(), '新建的空队列不该是满的'",
            "_q = CircularQueue(3)\nassert _q.size() == 0, '新建队列的元素个数应是 0，实际 %r' % (_q.size(),)",
            "_q = CircularQueue(3)\nassert _q.dequeue() is None, '队空时 dequeue 应返回 None，实际 %r' % (_q.dequeue(),)",
            "_q = CircularQueue(3)\nassert _q.enqueue(1) and _q.enqueue(2), '空队列入队 1、2 都应成功'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\nassert _q.is_full(), '容量 3 的循环队列牺牲一个单元，存满 2 个时 is_full() 应为 True'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\nassert not _q.enqueue(3), '队满时 enqueue 应返回假值（不能覆盖已有元素）'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.enqueue(3)\nassert _q.size() == 2 and _q.dequeue() == 1, '队满入队失败后元素个数应仍是 2，队头仍是 1，实际 %r' % (_q.size(),)",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\nassert [_q.dequeue(), _q.dequeue()] == [1, 2], '先进先出：出队顺序应是 1、2'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.dequeue()\nassert _q.enqueue(3), '出队腾出的位置要能被环形复用（rear 绕回来），否则 enqueue 会误判成队满'",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.dequeue()\n_q.enqueue(3)\nassert [_q.dequeue(), _q.dequeue()] == [2, 3], '环形复用后出队顺序应是 2、3，实际 %r' % ([_q.dequeue(), _q.dequeue()],)",
            "_q = CircularQueue(3)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.enqueue(3)\nassert _q.is_empty() is False and _q.size() == 2, '队满入队失败后队列仍有 2 个元素'",
            "_q = CircularQueue(3)\n_q.enqueue(7)\n_q.dequeue()\nassert _q.is_empty() and _q.size() == 0 and not _q.is_full(), '出一个元素后队列应空（front 追上了 rear）'",
            "_q = CircularQueue(2)\nassert _q.enqueue(9), '容量 2 的队列空的时候应能入队'",
            "_q = CircularQueue(2)\n_q.enqueue(9)\nassert _q.is_full() and not _q.enqueue(8), '容量 2 的循环队列最多存 1 个元素，此时应判满'",
            "_q = CircularQueue(2)\n_q.enqueue(9)\nassert _q.dequeue() == 9 and _q.dequeue() is None, '容量 2 的队列出队 1 个后就空了，再出队应返回 None'",
            "_q = CircularQueue(3)\n_ok = True\nfor _i in range(60):\n    if not _q.enqueue(_i):\n        _ok = False\n        break\n    if _q.dequeue() != _i:\n        _ok = False\n        break\nassert _ok, '反复「入队一个、出队一个」60 轮，顺序应始终先进先出（front/rear 必须能回绕）'",
            "_q = CircularQueue(4)\nassert _q.enqueue(1) and _q.enqueue(2) and _q.enqueue(3), '容量 4 的队列应能连续存 3 个元素'",
            "_q = CircularQueue(4)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.enqueue(3)\nassert not _q.enqueue(4), '容量 4 的队列存满 3 个后不能再入队'",
            "_q = CircularQueue(4)\n_q.enqueue(1)\n_q.enqueue(2)\n_q.enqueue(3)\n_q.dequeue()\n_q.enqueue(4)\nassert _q.dequeue() == 2 and _q.size() == 2, '绕了一圈后出队应是 2，元素个数应是 2，实际 %r' % (_q.size(),)",
            "_q = CircularQueue(5)\n_ok = True\nfor _i in range(4):\n    if not _q.enqueue(_i):\n        _ok = False\nassert not _q.enqueue(99), '容量 5 的队列存满 4 个后应判满'\nassert _ok, '前 4 次入队都应成功'",
            "assert 'collections' not in _src, '题面要求用列表 + 取模下标手写循环队列，不要用 collections 里的现成队列'",
        ],
        'explanation': (
            '循环队列要解决的是顺序队列的**假溢出**：普通顺序队列出队后前面的空间浪费了，'
            '用取模让下标「绕回去」就能重复利用。\n\n'
            '麻烦在于：只用 `front`、`rear` 两个下标，`front == rear` 这时'
            '既可能是「队空」也可能是「队满」，怎么办？教材给了三种方案'
            '（少存一个 / 加 size 计数 / 加标志位），本题采用最经典的**牺牲一个单元**：\n\n'
            '```python\n'
            '队空：front == rear\n'
            '队满：(rear + 1) % capacity == front\n'
            '```\n\n'
            '代价是「最多存 capacity − 1 个元素」，好处是判空判满都只用一个表达式。\n\n'
            '`size()` 的写法值得记一下：`(rear - front) % capacity`。'
            '因为 rear 可能绕到 front 前面（数值更小），直接相减是负数，取模就回来了。\n\n'
            '**常见错误**：\n\n'
            '1. 判满写成 `(rear + 1) == capacity`，队列绕一圈后（front 也移动过）就判错；\n'
            '2. 入队/出队后忘记对下标取模，下标一直涨、越界；\n'
            '3. 认为「capacity 个位置能存 capacity 个元素」——牺牲单元后只能存 capacity − 1 个；\n'
            '4. 用 `data.pop(0)` 出队（那是 O(n) 的搬移，不是循环队列）。\n\n'
            '复杂度：入队、出队、判空、判满、size 全是 O(1)、额外空间 O(capacity)。'
        ),
        'expected_output': 'True False\nTrue True\nTrue False\n1 2 None',
        'hints': ['队空 front == rear；队满 (rear + 1) % capacity == front', '入队出队后下标都要对 capacity 取模回绕'],
    },
    {
        'id': 'x823-215',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '后缀表达式求值（逆波兰计算器）',
        'difficulty': 2,
        'tags': ['栈', '后缀表达式', '求值'],
        'statement': (
            '定义函数 `eval_postfix(tokens)`：计算**后缀（逆波兰）表达式**的值，返回整数。\n\n'
            '`tokens` 是**字符串列表**，例如 `["3", "4", "+"]` 表示 `3 + 4`：\n\n'
            '- 操作数是十进制整数字符串，可能有负号，如 `"-7"`；\n'
            '- 运算符是 `"+"`、`"-"`、`"*"`、`"/"` 四种，都是二元运算符；\n'
            '- 除法按 `int(a / b)` **向零取整**（例如 `"-7" "2" "/"` 得 `-3`），除数不会是 0。\n\n'
            '算法（栈）：从左到右扫 token——遇到数就压栈；遇到运算符就弹出**两个**数，'
            '**先弹出的是右操作数、后弹出的是左操作数**，算完把结果压回去。'
            '扫完后栈里正好剩一个数，就是答案。\n\n'
            '边界要求：\n\n'
            '- 空列表、操作数不足（如 `["+"]`）、扫完后栈里不止一个数、'
            '含有既不是数也不是运算符的 token，都抛 `ValueError`；\n'
            '- 时间 O(n)、额外空间 O(n)。\n\n'
            '最后打印 `["3","4","+"]`、`["3","4","+","5","*"]`、'
            '`["5","1","2","+","4","*","+","3","-"]`、`["-7","2","/"]` 的结果。'
        ),
        'starter_code': 'def eval_postfix(tokens):\n    stack = []\n    # 数字压栈；运算符弹出两个数（先弹右、后弹左），结果压回去\n    pass\n',
        'solution': (
            "def eval_postfix(tokens):\n"
            "    stack = []\n"
            "    for token in tokens:\n"
            "        if token in ('+', '-', '*', '/'):\n"
            "            if len(stack) < 2:\n"
            "                raise ValueError('操作数不足：%r' % (tokens,))\n"
            "            right = stack.pop()\n"
            "            left = stack.pop()\n"
            "            if token == '+':\n"
            "                stack.append(left + right)\n"
            "            elif token == '-':\n"
            "                stack.append(left - right)\n"
            "            elif token == '*':\n"
            "                stack.append(left * right)\n"
            "            else:\n"
            "                stack.append(int(left / right))\n"
            "        else:\n"
            "            try:\n"
            "                stack.append(int(token))\n"
            "            except ValueError:\n"
            "                raise ValueError('非法 token：%r' % (token,))\n"
            "    if len(stack) != 1:\n"
            "        raise ValueError('表达式非法：%r' % (tokens,))\n"
            "    return stack[0]\n"
            "\n"
            "print(eval_postfix(['3', '4', '+']))\n"
            "print(eval_postfix(['3', '4', '+', '5', '*']))\n"
            "print(eval_postfix(['5', '1', '2', '+', '4', '*', '+', '3', '-']))\n"
            "print(eval_postfix(['-7', '2', '/']))\n"
        ),
        'checks': [
            "assert eval_postfix(['42']) == 42, '只有一个操作数时应直接返回它，实际 %r' % (eval_postfix(['42']),)",
            "assert eval_postfix(['-3']) == -3, '负数操作数也要能解析，实际 %r' % (eval_postfix(['-3']),)",
            "assert eval_postfix(['3', '4', '+']) == 7, '3 4 + 应是 7，实际 %r' % (eval_postfix(['3', '4', '+']),)",
            "assert eval_postfix(['1', '2', '-']) == -1, '减法要注意左右：1 - 2 = -1，实际 %r' % (eval_postfix(['1', '2', '-']),)",
            "assert eval_postfix(['2', '1', '-']) == 1, '左右反过来是 2 - 1 = 1，实际 %r' % (eval_postfix(['2', '1', '-']),)",
            "assert eval_postfix(['3', '4', '+', '5', '*']) == 35, '(3 + 4) * 5 = 35，实际 %r' % (eval_postfix(['3', '4', '+', '5', '*']),)",
            "assert eval_postfix(['2', '3', '4', '*', '+']) == 14, '2 + (3 * 4) = 14，实际 %r' % (eval_postfix(['2', '3', '4', '*', '+']),)",
            "assert eval_postfix(['7', '2', '/']) == 3, '7 / 2 向零取整是 3，实际 %r' % (eval_postfix(['7', '2', '/']),)",
            "assert eval_postfix(['-7', '2', '/']) == -3, '-7 / 2 向零取整是 -3（不是 -4），实际 %r' % (eval_postfix(['-7', '2', '/']),)",
            "assert eval_postfix(['7', '2', '/', '2', '/']) == 1, '连续整除 (7 / 2) / 2 = 1，实际 %r' % (eval_postfix(['7', '2', '/', '2', '/']),)",
            "assert eval_postfix(['10', '20', '30', '/', '-']) == 10, '10 - (20 / 30) = 10（整除）实际 %r' % (eval_postfix(['10', '20', '30', '/', '-']),)",
            "assert eval_postfix(['5', '1', '2', '+', '4', '*', '+', '3', '-']) == 14, '教材例子 5 + ((1 + 2) * 4) - 3 = 14，实际 %r' % (eval_postfix(['5', '1', '2', '+', '4', '*', '+', '3', '-']),)",
            "assert eval_postfix(['2', '2', '2', '*', '*']) == 8, '2 * 2 * 2 = 8，实际 %r' % (eval_postfix(['2', '2', '2', '*', '*']),)",
            "assert eval_postfix(['0', '5', '+']) == 5, '操作数里有 0 也要正常，实际 %r' % (eval_postfix(['0', '5', '+']),)",
            "assert eval_postfix(['100', '20', '-']) == 80, '多位数操作数要按整数解析，实际 %r' % (eval_postfix(['100', '20', '-']),)",
            "_bad = False\ntry:\n    eval_postfix(['+'])\nexcept ValueError:\n    _bad = True\nassert _bad, '操作数不足的表达式（只有一个加号）应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_postfix(['1', '2'])\nexcept ValueError:\n    _bad = True\nassert _bad, '扫完后剩两个操作数（1 和 2）不合法，应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_postfix(['1', '+', '2'])\nexcept ValueError:\n    _bad = True\nassert _bad, '后缀表达式里运算符位置不对应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_postfix([])\nexcept ValueError:\n    _bad = True\nassert _bad, '空表达式应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_postfix(['1', '2', '+', '+'])\nexcept ValueError:\n    _bad = True\nassert _bad, '多出一个运算符导致操作数不足，应抛出 ValueError'",
        ],
        'explanation': (
            '后缀表达式为什么好算？因为**运算符出现时，它要的两个操作数刚好就在前面**，'
            '不需要括号、也不需要优先级表。\n\n'
            '```python\n'
            'right = stack.pop()      # 先弹出的是右操作数\n'
            'left = stack.pop()       # 后弹出的是左操作数\n'
            'stack.append(left - right)\n'
            '```\n\n'
            '**弹出顺序是这题最容易错的地方**：栈顶是「最近压进来的数」，'
            '在 `1 2 -` 里先压 1 再压 2，栈顶是 2，所以先弹出来的是**右**操作数。'
            '如果写成 `left = stack.pop()` 再 `right = stack.pop()`，'
            '减法和除法就会算出相反的结果（`1 2 -` 变成 1 而不是 -1）。\n\n'
            '**边界为什么用 ValueError？** 表达式非法（操作数不足、剩余多个、'
            'token 不认识）时没有正确的返回值可以给，抛异常是 Python 的惯例。'
            '很多同学只处理「能算对」的情况，遇到 `["+"]` 直接 IndexError——'
            '在 823 阅卷里，这类异常处理也是得分点。\n\n'
            '**常见错误**：\n\n'
            '1. 左右操作数弹反（只影响减法和除法）；\n'
            '2. 除法用 `left // right`（向下取整），负数时 `-7 // 2 == -4`，'
            '   与题面要求的向零取整 `int(-7 / 2) == -3` 不一致；\n'
            '3. 直接 `int(token)` 解析运算符，抛出的异常类型不对；\n'
            '4. 忘记「扫完栈里应恰好剩一个数」的检查，`["1", "2"]` 会静默返回 2。\n\n'
            '复杂度：时间 O(n)、额外空间 O(n)（栈最坏存一半的操作数）。'
        ),
        'expected_output': '7\n35\n14\n-3',
        'hints': ['遇到数就压栈；遇到运算符先弹右操作数、再弹左操作数', '除法用 int(left / right) 向零取整，别用 //'],
    },
    {
        'id': 'x823-216',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '中缀表达式转后缀表达式（算符优先栈）',
        'difficulty': 2,
        'tags': ['栈', '中缀转后缀', '运算符优先级'],
        'statement': (
            '定义函数 `to_postfix(expr)`：把**中缀表达式**转成**后缀表达式**，返回字符串。\n\n'
            '输入约定：\n\n'
            '- `expr` 是**不含空格**的字符串，例如 `"3+4*5"`、`"(a+b)*c"`；\n'
            '- 操作数是**单个字符**（数字或字母，如 `3`、`a`）；\n'
            '- 运算符只有 `+`、`-`、`*`、`/` 和圆括号；\n'
            '- 空串返回空字符串。\n\n'
            '输出格式：后缀表达式的 token（操作数与运算符）之间**用一个空格分隔**，'
            '例如 `"3+4*5"` 的结果是 `"3 4 5 * +"`。\n\n'
            '规则（一个运算符栈 `ops`）：\n\n'
            '1. 遇到操作数：直接输出；\n'
            '2. 遇到 `(`：压栈（左括号要一直等到配对的右括号才弹出）；\n'
            '3. 遇到 `)`：把栈顶运算符逐个弹出输出，直到遇到 `(`，'
            '**把 `(` 弹掉但不输出**；\n'
            '4. 遇到运算符 op：**只要栈顶是优先级不低于 op 的运算符就把它弹出输出**'
            '（同级也要弹，保证左结合，例如 `a/b/c` → `a b / c /`），'
            '然后把 op 压栈；\n'
            '5. 扫描结束后把栈里剩下的运算符依次弹出输出。\n\n'
            '最后打印 `to_postfix("3+4*5")`、`to_postfix("(3+4)*5")`、'
            '`to_postfix("a+b*c-d")` 的结果，再打印空串的结果（用 `print(repr(...))`）。'
        ),
        'starter_code': 'def to_postfix(expr):\n    prec = {"+": 1, "-": 1, "*": 2, "/": 2}\n    out = []\n    ops = []\n    # 操作数直接进 out；运算符按优先级弹栈；括号单独处理\n    pass\n',
        'solution': (
            "def to_postfix(expr):\n"
            "    prec = {'+': 1, '-': 1, '*': 2, '/': 2}\n"
            "    out = []\n"
            "    ops = []\n"
            "    for ch in expr:\n"
            "        if ch.isalnum():\n"
            "            out.append(ch)\n"
            "        elif ch == '(':\n"
            "            ops.append(ch)\n"
            "        elif ch == ')':\n"
            "            while ops and ops[-1] != '(':\n"
            "                out.append(ops.pop())\n"
            "            if ops:\n"
            "                ops.pop()\n"
            "        elif ch in prec:\n"
            "            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[ch]:\n"
            "                out.append(ops.pop())\n"
            "            ops.append(ch)\n"
            "    while ops:\n"
            "        out.append(ops.pop())\n"
            "    return ' '.join(out)\n"
            "\n"
            "print(to_postfix('3+4*5'))\n"
            "print(to_postfix('(3+4)*5'))\n"
            "print(to_postfix('a+b*c-d'))\n"
            "print(repr(to_postfix('')))\n"
        ),
        'checks': [
            "assert to_postfix('') == '', '空表达式应返回空字符串，实际 %r' % (to_postfix(''),)",
            "assert to_postfix('a') == 'a', '只有一个操作数时应原样输出，实际 %r' % (to_postfix('a'),)",
            "assert to_postfix('3+4') == '3 4 +', '3+4 应是 \"3 4 +\"，实际 %r' % (to_postfix('3+4'),)",
            "assert to_postfix('3+4*5') == '3 4 5 * +', '乘法优先级高，应是 \"3 4 5 * +\"，实际 %r' % (to_postfix('3+4*5'),)",
            "assert to_postfix('3*4+5') == '3 4 * 5 +', '先算乘法再算加法，实际 %r' % (to_postfix('3*4+5'),)",
            "assert to_postfix('(3+4)*5') == '3 4 + 5 *', '括号里的要先输出，实际 %r' % (to_postfix('(3+4)*5'),)",
            "assert to_postfix('a+b-c') == 'a b + c -', '同级左结合：先弹加号，实际 %r' % (to_postfix('a+b-c'),)",
            "assert to_postfix('a-b+c') == 'a b - c +', '减号也要按左结合弹出，实际 %r' % (to_postfix('a-b+c'),)",
            "assert to_postfix('a/b/c') == 'a b / c /', '同级左结合：(a/b)/c，实际 %r' % (to_postfix('a/b/c'),)",
            "assert to_postfix('a+b*c-d') == 'a b c * + d -', '综合例子应是 \"a b c * + d -\"，实际 %r' % (to_postfix('a+b*c-d'),)",
            "assert to_postfix('a*(b+c)/d') == 'a b c + * d /', '先括号、再乘法、最后除法，实际 %r' % (to_postfix('a*(b+c)/d'),)",
            "assert to_postfix('((a+b)*c)') == 'a b + c *', '多余的外层括号不影响结果，实际 %r' % (to_postfix('((a+b)*c)'),)",
            "assert to_postfix('((a))') == 'a', '只有一层操作数时应输出 \"a\"，实际 %r' % (to_postfix('((a))'),)",
            "assert to_postfix('1+2*3-4/2') == '1 2 3 * + 4 2 / -', '教材例子应是 \"1 2 3 * + 4 2 / -\"，实际 %r' % (to_postfix('1+2*3-4/2'),)",
            "assert to_postfix('(a+b)*(c-d)') == 'a b + c d - *', '两组括号相乘，实际 %r' % (to_postfix('(a+b)*(c-d)'),)",
            "assert to_postfix('a+b*(c-d)-e/f') == 'a b c d - * + e f / -', '综合长例子应是 \"a b c d - * + e f / -\"，实际 %r' % (to_postfix('a+b*(c-d)-e/f'),)",
            "assert to_postfix('((a+b)*(c+d))') == 'a b + c d + *', '括号套括号要一并处理，实际 %r' % (to_postfix('((a+b)*(c+d))'),)",
            "assert to_postfix('a+b*c*d') == 'a b c * d * +', '连续两个同级乘法都要弹出，实际 %r' % (to_postfix('a+b*c*d'),)",
            "assert '  ' not in to_postfix('1+2*3-4/2') and to_postfix('3+4*5')[0] == '3', 'token 之间只能有一个空格，且第一个 token 是操作数：%r' % (to_postfix('3+4*5'),)",
            "assert len(to_postfix('1+2*3-4/2').split(' ')) == 9, '1+2*3-4/2 的后缀式应有 9 个 token（5 个操作数 + 4 个运算符），实际 %r' % (len(to_postfix('1+2*3-4/2').split(' ')),)",
            "assert 'append(' in _src and 'pop()' in _src, '题面要求用栈（运算符栈）来实现中缀转后缀'",
        ],
        'explanation': (
            '中缀转后缀的算法本质上就是**把「谁先算」编码进输出顺序**，'
            '栈里存的是「暂时还不知道什么时候用」的运算符。\n\n'
            '为什么「栈顶优先级不低于当前运算符就弹出」？'
            '因为中缀是**左结合**的：`a - b + c` 里 `+` 来了以后，'
            '前面那个 `-` 的两个操作数已经齐了，可以先把 `-` 输出；'
            '如果当前是 `*` 而栈顶是 `+`，就必须等 `*` 的两个操作数凑齐（栈顶优先级低，不弹）。\n\n'
            '```python\n'
            'elif ch in prec:\n'
            '    while ops and ops[-1] != "(" and prec[ops[-1]] >= prec[ch]:\n'
            '        out.append(ops.pop())\n'
            '    ops.append(ch)\n'
            '```\n\n'
            '括号的处理要点：左括号入栈后，**在它被弹掉之前，'
            '外面的运算符不能弹到它之外**，所以所有弹栈循环都要加 `ops[-1] != "("` 的条件；'
            '遇到右括号时一直弹到左括号，左括号本身丢弃（后缀式里没有括号）。\n\n'
            '**注意最后一步**：扫描结束后栈里剩下的运算符要全部弹出，'
            '很多同学忘了这一步，`"3+4"` 会输出成 `"3 4"`。\n\n'
            '**常见错误**：\n\n'
            '1. 同级用 `>` 而不是 `>=`，`a/b/c` 会转成 `a b c / /`（右结合），错了；\n'
            '2. 右括号处理时把 `(` 也输出到了结果里；\n'
            '3. 忘记弹完栈里剩下的运算符；\n'
            '4. 输出时用逗号或没有空格拼接，`"3,4,+"` 或 `"34+"` 都不符合题面格式。\n\n'
            '复杂度：时间 O(n)（每个字符进出栈各一次）、额外空间 O(n)。'
        ),
        'expected_output': '3 4 5 * +\n3 4 + 5 *\na b c * + d -\n\'\'',
        'hints': ['操作数直接输出；运算符要先把栈顶「优先级不低于自己」的都弹出', '左括号压栈后不能被普通弹栈弹走，遇到右括号才把整段弹出'],
    },
    {
        'id': 'x823-217',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '用两个栈实现队列',
        'difficulty': 2,
        'tags': ['栈', '队列', '均摊 O(1)'],
        'statement': (
            '请定义一个类 `MyQueue`，**只用两个栈（Python 列表）**实现先进先出的队列。\n\n'
            '必须实现的方法：\n\n'
            '- `push(x)`：把元素 `x` 放到队尾；\n'
            '- `pop()`：弹出并返回队头元素；**队列为空时返回 `None`**；\n'
            '- `peek()`：返回队头元素但**不出队**；队列为空时返回 `None`；\n'
            '- `empty()`：队列为空返回 True。\n\n'
            '经典做法：\n\n'
            '- 一个栈专门负责**入队**（记为 `stack_in`），元素直接压进去；\n'
            '- 另一个栈专门负责**出队**（记为 `stack_out`）；\n'
            '- 需要出队时，如果 `stack_out` 是空的，就把 `stack_in` 里的元素'
            '**全部倒进** `stack_out`（倒一次顺序就正过来了），然后再弹 `stack_out` 的栈顶；\n'
            '- `stack_out` 非空时**不要**再倒，否则顺序会乱。\n\n'
            '每个元素最多被倒一次，所以 `push`、`pop` 均摊下来都是 O(1)。\n\n'
            '最后构造一个 `MyQueue`：先入队 1、2，打印 `peek()`、`pop()`、`empty()`；'
            '再入队 3，打印两次 `pop()` 和 `empty()`。'
        ),
        'starter_code': 'class MyQueue:\n    def __init__(self):\n        self.stack_in = []\n        self.stack_out = []\n\n    def push(self, x):\n        pass\n\n    def pop(self):\n        pass\n\n    def peek(self):\n        pass\n\n    def empty(self):\n        pass\n',
        'solution': (
            "class MyQueue:\n"
            "    def __init__(self):\n"
            "        self.stack_in = []\n"
            "        self.stack_out = []\n"
            "\n"
            "    def push(self, x):\n"
            "        self.stack_in.append(x)\n"
            "\n"
            "    def _shift(self):\n"
            "        if not self.stack_out:\n"
            "            while self.stack_in:\n"
            "                self.stack_out.append(self.stack_in.pop())\n"
            "\n"
            "    def pop(self):\n"
            "        self._shift()\n"
            "        if not self.stack_out:\n"
            "            return None\n"
            "        return self.stack_out.pop()\n"
            "\n"
            "    def peek(self):\n"
            "        self._shift()\n"
            "        if not self.stack_out:\n"
            "            return None\n"
            "        return self.stack_out[-1]\n"
            "\n"
            "    def empty(self):\n"
            "        return not self.stack_in and not self.stack_out\n"
            "\n"
            "q = MyQueue()\n"
            "q.push(1)\n"
            "q.push(2)\n"
            "print(q.peek(), q.pop(), q.empty())\n"
            "q.push(3)\n"
            "print(q.pop(), q.pop(), q.empty())\n"
        ),
        'checks': [
            "_q = MyQueue()\nassert _q.empty(), '新建的队列应为空'",
            "_q = MyQueue()\nassert _q.pop() is None, '空队列 pop 应返回 None，实际 %r' % (_q.pop(),)",
            "_q = MyQueue()\nassert _q.peek() is None, '空队列 peek 应返回 None，实际 %r' % (_q.peek(),)",
            "_q = MyQueue()\n_q.push(1)\nassert not _q.empty(), '入队一个元素后不该是空的'",
            "_q = MyQueue()\n_q.push(1)\nassert _q.peek() == 1, '队头应是 1，实际 %r' % (_q.peek(),)",
            "_q = MyQueue()\n_q.push(1)\n_q.peek()\nassert _q.pop() == 1, 'peek 不该把元素吃掉，pop 仍应返回 1'",
            "_q = MyQueue()\n_q.push(1)\n_q.push(2)\nassert _q.pop() == 1 and _q.pop() == 2, '先进先出：先入队的 1 先出'",
            "_q = MyQueue()\n_q.push(1)\n_q.push(2)\n_q.pop()\n_q.pop()\nassert _q.empty(), '两个元素都出队后队列应空'",
            "_q = MyQueue()\n_q.push(1)\n_q.push(2)\n_q.push(3)\nassert _q.peek() == 1 and _q.pop() == 1, '连续入队 3 个后应先出 1，实际 %r' % (_q.peek(),)",
            "_q = MyQueue()\nfor _i in range(5):\n    _q.push(_i)\nassert [_q.pop() for _ in range(5)] == [0, 1, 2, 3, 4], '一次倒栈后应按 0~4 的顺序出队'",
            "_q = MyQueue()\n_q.push(1)\n_q.push(2)\n_q.pop()\n_q.push(3)\nassert [_q.pop(), _q.pop()] == [2, 3], '出队后再入队，顺序仍是 2、3（stack_out 非空时不能再倒）'",
            "_q = MyQueue()\n_q.push(1)\n_q.pop()\n_q.push(2)\n_q.push(3)\n_q.pop()\nassert _q.peek() == 3 and _q.pop() == 3, '交错操作后队头应是 3，实际 %r' % (_q.peek(),)",
            "_q = MyQueue()\n_q.push(1)\n_q.pop()\nassert _q.empty() and _q.pop() is None, '出队后应回到空状态，pop 返回 None'",
            "_q = MyQueue()\n_ref = []\n_ok = True\nfor _i in range(200):\n    if _i % 3 == 2 and _ref:\n        if _q.pop() != _ref.pop(0):\n            _ok = False\n            break\n    else:\n        _q.push(_i)\n        _ref.append(_i)\nassert _ok, '入队/出队交错 200 次，出队顺序应与普通队列完全一致（两个栈要配合好）'",
            "_q = MyQueue()\n_ref = []\nfor _i in range(30):\n    _q.push(_i)\n    _ref.append(_i)\nwhile _ref:\n    assert _q.pop() == _ref.pop(0), '把剩下的元素依次弹出，顺序应仍是先进先出'\nassert _q.empty(), '全部弹出后队列应空'",
            "_q = MyQueue()\n_q.push('a')\n_q.push('b')\nassert _q.pop() == 'a' and _q.peek() == 'b', '字符串元素也要能存入并保持顺序，实际 %r' % (_q.peek(),)",
            "assert 'collections' not in _src, '题面要求只用两个列表（栈）手写队列，不要用 collections 里的现成容器'",
        ],
        'explanation': (
            '栈是后进先出，队列是先进先出，两者差一个「方向」。'
            '**倒一次栈就把方向翻过来了**——这就是两个栈实现队列的全部秘密。\n\n'
            '```python\n'
            'def pop(self):\n'
            '    if not self.stack_out:\n'
            '        while self.stack_in:\n'
            '            self.stack_out.append(self.stack_in.pop())   # 倒栈\n'
            '    return self.stack_out.pop() if self.stack_out else None\n'
            '```\n\n'
            '**为什么 `stack_out` 非空时不能再倒？** 假设 `stack_out` 里还压着'
            '`[3, 2]`（栈顶 2 是队头），现在新 push 了 4。如果这时候又倒一次栈，'
            '4 会被压到 2 上面变成队头，顺序立刻乱掉。'
            '正确的做法是「旧的先出完，再倒新的」。\n\n'
            '**为什么均摊 O(1)？** 每个元素一生中最多经历两次搬运：'
            '从 `stack_in` 出来一次、进 `stack_out` 一次，'
            '所以 n 次操作总共 O(n)，平均每次 O(1)。'
            '注意 `pop` 单次最坏是 O(n)（赶上大倒栈），这是「均摊」的含义。\n\n'
            '**常见错误**：\n\n'
            '1. 每次 `pop` 都无脑倒栈，顺序错乱；\n'
            '2. 只用 `stack_in` 加 `pop(0)`——那不是两个栈，也是 O(n)；\n'
            '3. `peek` 直接把元素 pop 出来再 push 回去，'
            '   这样虽然答案对，但把元素搬到了错误的栈里，后续顺序会乱；\n'
            '4. 忘记处理空队列，返回 `None` 的要求没满足。\n\n'
            '复杂度：push O(1)、pop / peek 均摊 O(1)（最坏 O(n)）、空间 O(n)。'
        ),
        'expected_output': '1 1 False\n2 3 True',
        'hints': ['入队只往 stack_in 压；出队只从 stack_out 弹', 'stack_out 空了才把 stack_in 全部倒过去（非空时不能倒）'],
    },
    {
        'id': 'x823-218',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '判断合法出栈序列（栈的模拟）',
        'difficulty': 2,
        'tags': ['栈', '出栈序列', '模拟'],
        'statement': (
            '已知入栈序列 `pushed`（各元素互不相同）和出栈序列 `popped`。\n\n'
            '定义函数 `is_valid_pop_sequence(pushed, popped)`：'
            '判断 `popped` 是否是**合法的出栈序列**——'
            '即按 `pushed` 的顺序依次入栈、期间可以随时出栈，'
            '能否恰好按 `popped` 的顺序把元素全部弹出；能返回 `True`，不能返回 `False`。\n\n'
            '约定：\n\n'
            '- 两个序列长度不等返回 `False`（例如 `[1, 2]` 与 `[1, 2, 3]`）；\n'
            '- 两个空序列返回 `True`；\n'
            '- `popped` 里出现 `pushed` 中没有的元素（如 `[1, 2, 3]` 与 `[1, 2, 4]`）返回 `False`。\n\n'
            '算法（栈模拟，O(n)）：\n\n'
            '```python\n'
            'j = 0\n'
            'stack = []\n'
            'for x in pushed:\n'
            '    stack.append(x)                      # 按入栈序列压栈\n'
            '    while stack and j < len(popped) and stack[-1] == popped[j]:\n'
            '        stack.pop()                      # 栈顶正好是下一个该弹出的元素\n'
            '        j += 1\n'
            'return j == len(popped) and not stack\n'
            '```\n\n'
            '最后打印 `([1,2,3], [3,2,1])`、`([1,2,3], [3,1,2])`、`([], [])` 的结果。'
        ),
        'starter_code': 'def is_valid_pop_sequence(pushed, popped):\n    if len(pushed) != len(popped):\n        return False\n    stack = []\n    j = 0\n    # 按 pushed 压栈，能弹就弹；最后看 j 是否走完、栈是否为空\n    pass\n',
        'solution': (
            "def is_valid_pop_sequence(pushed, popped):\n"
            "    if len(pushed) != len(popped):\n"
            "        return False\n"
            "    stack = []\n"
            "    j = 0\n"
            "    for x in pushed:\n"
            "        stack.append(x)\n"
            "        while stack and j < len(popped) and stack[-1] == popped[j]:\n"
            "            stack.pop()\n"
            "            j += 1\n"
            "    return j == len(popped) and not stack\n"
            "\n"
            "print(is_valid_pop_sequence([1, 2, 3], [3, 2, 1]))\n"
            "print(is_valid_pop_sequence([1, 2, 3], [3, 1, 2]))\n"
            "print(is_valid_pop_sequence([], []))\n"
        ),
        'checks': [
            "assert is_valid_pop_sequence([], []) is True, '两个空序列应返回 True'",
            "assert is_valid_pop_sequence([1], [1]) is True, '入栈 1 后立刻出栈是合法的'",
            "assert is_valid_pop_sequence([1], [2]) is False, '出栈序列里出现了没入过栈的元素，应返回 False'",
            "assert is_valid_pop_sequence([1, 2, 3], [1, 2, 3]) is True, '边入边出（1、2、3）是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [1, 2, 3]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [3, 2, 1]) is True, '全部入完再出是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [3, 2, 1]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [3, 1, 2]) is False, '经典反例：3 出栈后栈里是 1、2（2 在顶），1 不能先出来，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [3, 1, 2]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [2, 1, 3]) is True, '2、1、3 是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [2, 1, 3]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [2, 3, 1]) is True, '2、3、1 是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [2, 3, 1]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [1, 3, 2]) is True, '1、3、2 是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3], [1, 3, 2]),)",
            "assert is_valid_pop_sequence([1, 2, 3], [1, 2, 4]) is False, '出现了不在入栈序列里的元素，应返回 False'",
            "assert is_valid_pop_sequence([1, 2], [1, 2, 3]) is False, '两个序列长度不等应返回 False'",
            "assert is_valid_pop_sequence([1, 2, 3, 4], [4, 3, 2, 1]) is True, '四个元素全入完再出是合法的'",
            "assert is_valid_pop_sequence([1, 2, 3, 4], [3, 4, 2, 1]) is True, '3、4、2、1 是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3, 4], [3, 4, 2, 1]),)",
            "assert is_valid_pop_sequence([1, 2, 3, 4], [4, 3, 1, 2]) is False, '4、3 出栈后栈里是 1、2（2 在顶），1 不能先出来'",
            "assert is_valid_pop_sequence([1, 2, 3, 4], [2, 4, 3, 1]) is True, '2、4、3、1 是合法的，实际 %r' % (is_valid_pop_sequence([1, 2, 3, 4], [2, 4, 3, 1]),)",
            "assert is_valid_pop_sequence([5, 6, 7], [6, 7, 5]) is True, '元素不连续（5、6、7）同样按顺序模拟即可，实际 %r' % (is_valid_pop_sequence([5, 6, 7], [6, 7, 5]),)",
            "assert is_valid_pop_sequence([5, 6, 7], [7, 5, 6]) is False, '7 出栈后 5 不能越过 6 先出，实际 %r' % (is_valid_pop_sequence([5, 6, 7], [7, 5, 6]),)",
            "assert is_valid_pop_sequence([1, 1, 2], [1, 2, 1]) is True, '入栈序列本身有重复值时，模拟过程仍要按位置走，实际 %r' % (is_valid_pop_sequence([1, 1, 2], [1, 2, 1]),)",
            "_n = 1000\nassert is_valid_pop_sequence(list(range(_n)), list(range(_n - 1, -1, -1))) is True, '1000 个元素全部入完再出是合法的（不能写成 O(n²) 的暴力枚举）'",
            "_n = 1000\nassert is_valid_pop_sequence(list(range(_n)), list(range(_n))) is True, '1000 个元素边入边出（升序）也是合法的'",
            "_n = 1000\n_bad = [_n - 1, _n - 3, _n - 2] + list(range(_n - 4, -1, -1))\nassert is_valid_pop_sequence(list(range(_n)), _bad) is False, '1000 个元素里 999 出栈后应轮到 998，998 前出 997 不合法，实际 %r' % (is_valid_pop_sequence(list(range(_n)), _bad),)",
            "assert 'append(' in _src and 'pop()' in _src, '题面要求用一个栈模拟入栈出栈过程'",
        ],
        'explanation': (
            '判断出栈序列最稳的办法就是**照着实实在在地模拟一遍**：'
            '按 `pushed` 的顺序把元素压进栈，只要栈顶正好等于 `popped` 里下一个该出的元素，'
            '就立刻弹出来。全部压完后，如果 `popped` 也正好走完、栈也空了，就是合法序列。\n\n'
            '```python\n'
            'for x in pushed:\n'
            '    stack.append(x)\n'
            '    while stack and j < len(popped) and stack[-1] == popped[j]:\n'
            '        stack.pop()\n'
            '        j += 1\n'
            'return j == len(popped) and not stack\n'
            '```\n\n'
            '**为什么这个「能弹就弹」的贪心是对的？** 当栈顶等于 `popped[j]` 时，'
            '它是「下一个必须出栈的元素」；此时不弹，唯一能让它出来的办法'
            '就是把更多元素压到它上面，那只会让它更晚出来、'
            '更不可能满足 `popped` 的顺序。所以「必须先弹」是唯一的选择，不存在取舍。\n\n'
            '**经典结论**：n 个元素的合法出栈序列个数是**卡特兰数** C(2n, n) / (n + 1)。'
            '本题反过来给定一个序列让你判断，O(n) 模拟即可，'
            '千万不要去枚举所有可能序列。\n\n'
            '**常见错误**：\n\n'
            '1. 只比较两个序列的元素集合（`sorted` 相等就返回 True），'
            '   那会把 `[3, 1, 2]` 判成合法；\n'
            '2. 忘记长度检查，`([1, 2], [1, 2, 3])` 会越界或误判；\n'
            '3. 循环里少了 `j < len(popped)` 的判断，`popped` 走完后 IndexError；\n'
            '4. 用递归枚举所有出栈可能，n = 1000 时直接超时。\n\n'
            '复杂度：时间 O(n)（每个元素进出栈各一次）、额外空间 O(n)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['按 pushed 顺序压栈，栈顶等于 popped 的当前元素就弹', '最后要同时满足「popped 走完」和「栈为空」'],
    },
    {
        'id': 'x823-219',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '用队列生成杨辉三角的第 n 行',
        'difficulty': 2,
        'tags': ['队列', '杨辉三角', '递推'],
        'statement': (
            '定义函数 `pascal_row(n)`：返回杨辉三角**第 n 行**的元素列表'
            '（`n` 从 1 开始：第 1 行是 `[1]`，第 2 行是 `[1, 1]`，第 3 行是 `[1, 2, 1]`）。\n\n'
            '- `n <= 0` 返回 `[]`；\n'
            '- 杨辉三角的递推关系：每个数等于它**肩上两个数之和**，行首行尾都是 1。\n\n'
            '要求用**队列**逐行推进（这是教材里队列的经典应用）：\n\n'
            '- 队列里放「当前行」；\n'
            '- 每往下一行走一步：在队头前补一个 0、在队尾后补一个 0，'
            '然后依次出队**相邻两个数**相加，得到的就是下一行（边算边入队）；\n'
            '- 从第 1 行推到第 n 行，共做 `n - 1` 步；\n'
            '- 可以用 `collections.deque`（队头 `popleft` 是 O(1)）。\n\n'
            '例如从 `[1]` 推 `[1, 1]`：补 0 得 `[0, 1, 0]`，'
            '相邻两数相加得 `1`、`1`，即 `[1, 1]`；'
            '再从 `[1, 1]` 得 `[0, 1, 1, 0]` → `1`、`2`、`1`。\n\n'
            '最后打印 `pascal_row(1)`、`pascal_row(5)`、`pascal_row(6)`、`pascal_row(0)` 的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef pascal_row(n):\n    if n <= 0:\n        return []\n    row = deque([1])\n    # 每走一步：队头队尾各补一个 0，再出队相邻两数相加\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "def pascal_row(n):\n"
            "    if n <= 0:\n"
            "        return []\n"
            "    row = deque([1])\n"
            "    for _ in range(1, n):\n"
            "        row.appendleft(0)\n"
            "        row.append(0)\n"
            "        nxt = deque()\n"
            "        prev = row.popleft()\n"
            "        while row:\n"
            "            cur = row.popleft()\n"
            "            nxt.append(prev + cur)\n"
            "            prev = cur\n"
            "        row = nxt\n"
            "    return list(row)\n"
            "\n"
            "print(pascal_row(1))\n"
            "print(pascal_row(5))\n"
            "print(pascal_row(6))\n"
            "print(pascal_row(0))\n"
        ),
        'checks': [
            "assert pascal_row(0) == [], 'n = 0 应返回空列表，实际 %r' % (pascal_row(0),)",
            "assert pascal_row(-3) == [], 'n 为负数应返回空列表，实际 %r' % (pascal_row(-3),)",
            "assert pascal_row(1) == [1], '第 1 行是 [1]，实际 %r' % (pascal_row(1),)",
            "assert pascal_row(2) == [1, 1], '第 2 行是 [1, 1]，实际 %r' % (pascal_row(2),)",
            "assert pascal_row(3) == [1, 2, 1], '第 3 行是 [1, 2, 1]，实际 %r' % (pascal_row(3),)",
            "assert pascal_row(4) == [1, 3, 3, 1], '第 4 行是 [1, 3, 3, 1]，实际 %r' % (pascal_row(4),)",
            "assert pascal_row(5) == [1, 4, 6, 4, 1], '第 5 行是 [1, 4, 6, 4, 1]，实际 %r' % (pascal_row(5),)",
            "assert pascal_row(6) == [1, 5, 10, 10, 5, 1], '第 6 行是 [1, 5, 10, 10, 5, 1]，实际 %r' % (pascal_row(6),)",
            "assert pascal_row(7) == [1, 6, 15, 20, 15, 6, 1], '第 7 行是 [1, 6, 15, 20, 15, 6, 1]，实际 %r' % (pascal_row(7),)",
            "assert pascal_row(10) == [1, 9, 36, 84, 126, 126, 84, 36, 9, 1], '第 10 行应是 [1, 9, 36, 84, 126, 126, 84, 36, 9, 1]，实际 %r' % (pascal_row(10),)",
            "_r = pascal_row(20)\nassert len(_r) == 20, '第 20 行应有 20 个数，实际 %r 个' % (len(_r),)",
            "_r = pascal_row(30)\nassert _r[0] == 1 and _r[-1] == 1, '每行首尾都必须是 1，实际 %r / %r' % (_r[0], _r[-1])",
            "_r = pascal_row(30)\nassert _r == _r[::-1], '杨辉三角每一行都是回文（左右对称），实际首尾 %r / %r' % (_r[0], _r[-1])",
            "_r = pascal_row(30)\nassert sum(_r) == 2 ** 29, '第 30 行所有数之和应是 2 的 29 次方（536870912），实际 %r' % (sum(_r),)",
            "_r = pascal_row(30)\nassert _r[1] == 29 and _r[2] == 406, '第 30 行的第 2、3 个数应是 29 和 406（C(29,1)、C(29,2)），实际 %r / %r' % (_r[1], _r[2])",
            "_r = pascal_row(61)\nassert _r[1] == 60 and _r[-2] == 60, '第 61 行的次首、次末项都应是 60，实际 %r / %r' % (_r[1], _r[-2])",
            "_r = pascal_row(50)\nassert _r == pascal_row(50), '同一行重复计算的结果必须一致（不能有隐藏状态残留）'",
            "assert 'popleft' in _src or 'pop(0)' in _src, '题面要求用队列（从队头出队）来做逐行推进'",
        ],
        'explanation': (
            '杨辉三角的每一行都是上一行的「相邻两数之和」，'
            '而队列天然适合做这种**相邻滑动求和**：把上一行放进队列，'
            '再在两端各补一个 0，然后每次取出「相邻的两个数」相加。\n\n'
            '```text\n'
            '上一行    [1, 1]\n'
            '两端补 0  [0, 1, 1, 0]\n'
            '相邻相加   1  2  1        -> 下一行 [1, 2, 1]\n'
            '```\n\n'
            '补 0 的作用是把「行首、行尾的 1」也纳入同一套加法：'
            '`0 + 1 = 1`（行首）、`1 + 0 = 1`（行尾），'
            '不用再对边界写特判。\n\n'
            '实现上有两种写法，效果一样：\n\n'
            '1. **本解**：先把 `row` 两端补 0，再用一个 `prev` 记住上一次弹出的值，'
            '每弹一个新值就和 `prev` 相加入队；\n'
            '2. 原地滑窗：每次 `popleft` 一个数 `a`，读队首 `b`，'
            '把 `a + b` 追加到队尾，同时把 `a` 重新 `append` 回去——'
            '注意这种写法要小心别把刚刚追加的元素又当成输入。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了在两端补 0，行首行尾的 1 就丢了（或只补一端）；\n'
            '2. 用 `list.pop(0)` 出队——单次 O(n)，整体退化成 O(n²)（本题数据小，'
            '   但 `deque.popleft()` 才是标准写法）；\n'
            '3. `n` 与「走多少步」差一格：从第 1 行到第 n 行要做 `n - 1` 步；\n'
            '4. 忘记 `n <= 0` 的边界。\n\n'
            '复杂度：时间 O(n²)（第 n 行有 n 个元素，逐行递推）、'
            '额外空间 O(n)（队列里最多一行）。'
        ),
        'expected_output': '[1]\n[1, 4, 6, 4, 1]\n[1, 5, 10, 10, 5, 1]\n[]',
        'hints': ['队列里放当前行，两端各补一个 0，再让相邻两数相加', '从第 1 行推到第 n 行一共走 n - 1 步'],
    },
    {
        'id': 'x823-220',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '中缀表达式直接求值（双栈法）',
        'difficulty': 3,
        'tags': ['栈', '中缀表达式', '求值', '优先级'],
        'statement': (
            '定义函数 `eval_infix(expr)`：**直接**计算中缀表达式的值并返回整数'
            '（不用先转后缀）。\n\n'
            '输入约定：\n\n'
            '- `expr` 是不含空格的字符串，操作数是**非负整数**（可以多位，如 `"10+20*3"`）；\n'
            '- 运算符只有 `+`、`-`、`*`、`/` 与圆括号；\n'
            '- 除法按 `int(a / b)` **向零取整**，除数不会是 0。\n\n'
            '算法（双栈法，教材写法）：\n\n'
            '- 一个**操作数栈** `nums`，一个**运算符栈** `ops`；\n'
            '- 遇到数字：把整段数字解析成整数压入 `nums`（注意是多位数！）；\n'
            '- 遇到 `(`：直接压入 `ops`；\n'
            '- 遇到 `)`：不停地对 `ops` 栈顶的运算符求值，直到栈顶是 `(`，最后把 `(` 弹掉；\n'
            '- 遇到运算符 op：只要 `ops` 栈顶是优先级**不低于** op 的运算符'
            '（同级也要算，保证左结合），就先把它求值，然后把 op 压栈；\n'
            '- 一次「求值」= 弹出两个操作数（**先弹右、后弹左**）与一个运算符，算完压回 `nums`；\n'
            '- 扫描结束后把 `ops` 里剩下的运算符依次求值，`nums` 里唯一的数就是答案。\n\n'
            '边界要求：以下情况都抛 `ValueError`——空表达式、括号不匹配、'
            '运算符位置不对（如 `"3++4"`、`"*5"`）、出现非法字符。\n\n'
            '最后打印 `eval_infix("3+4*5")`、`eval_infix("(3+4)*5")`、'
            '`eval_infix("10+20*3")`、`eval_infix("((2+3)*4-5)/3")` 的结果。'
        ),
        'starter_code': 'def eval_infix(expr):\n    prec = {"+": 1, "-": 1, "*": 2, "/": 2}\n    nums = []\n    ops = []\n    # 数字解析后进 nums；运算符按优先级决定是否先算；括号单独处理\n    pass\n',
        'solution': (
            "def eval_infix(expr):\n"
            "    prec = {'+': 1, '-': 1, '*': 2, '/': 2}\n"
            "    nums = []\n"
            "    ops = []\n"
            "\n"
            "    def apply_top():\n"
            "        if len(nums) < 2 or not ops:\n"
            "            raise ValueError('表达式非法：%r' % (expr,))\n"
            "        right = nums.pop()\n"
            "        left = nums.pop()\n"
            "        op = ops.pop()\n"
            "        if op == '+':\n"
            "            nums.append(left + right)\n"
            "        elif op == '-':\n"
            "            nums.append(left - right)\n"
            "        elif op == '*':\n"
            "            nums.append(left * right)\n"
            "        else:\n"
            "            nums.append(int(left / right))\n"
            "\n"
            "    i = 0\n"
            "    n = len(expr)\n"
            "    while i < n:\n"
            "        ch = expr[i]\n"
            "        if ch.isdigit():\n"
            "            j = i\n"
            "            while j < n and expr[j].isdigit():\n"
            "                j += 1\n"
            "            nums.append(int(expr[i:j]))\n"
            "            i = j\n"
            "        elif ch == '(':\n"
            "            ops.append(ch)\n"
            "            i += 1\n"
            "        elif ch == ')':\n"
            "            while ops and ops[-1] != '(':\n"
            "                apply_top()\n"
            "            if not ops:\n"
            "                raise ValueError('括号不匹配：%r' % (expr,))\n"
            "            ops.pop()\n"
            "            i += 1\n"
            "        elif ch in prec:\n"
            "            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[ch]:\n"
            "                apply_top()\n"
            "            ops.append(ch)\n"
            "            i += 1\n"
            "        else:\n"
            "            raise ValueError('非法字符：%r' % (ch,))\n"
            "    while ops:\n"
            "        if ops[-1] == '(':\n"
            "            raise ValueError('括号不匹配：%r' % (expr,))\n"
            "        apply_top()\n"
            "    if len(nums) != 1:\n"
            "        raise ValueError('表达式非法：%r' % (expr,))\n"
            "    return nums[0]\n"
            "\n"
            "print(eval_infix('3+4*5'))\n"
            "print(eval_infix('(3+4)*5'))\n"
            "print(eval_infix('10+20*3'))\n"
            "print(eval_infix('((2+3)*4-5)/3'))\n"
        ),
        'checks': [
            "assert eval_infix('7') == 7, '只有一个数时应直接返回它，实际 %r' % (eval_infix('7'),)",
            "assert eval_infix('123') == 123, '多位操作数要整体解析，实际 %r' % (eval_infix('123'),)",
            "assert eval_infix('3+4') == 7, '3+4 = 7，实际 %r' % (eval_infix('3+4'),)",
            "assert eval_infix('3+4*5') == 23, '乘法优先：3 + 20 = 23，实际 %r' % (eval_infix('3+4*5'),)",
            "assert eval_infix('(3+4)*5') == 35, '括号优先：7 * 5 = 35，实际 %r' % (eval_infix('(3+4)*5'),)",
            "assert eval_infix('10+20*3') == 70, '多位数：10 + 60 = 70，实际 %r' % (eval_infix('10+20*3'),)",
            "assert eval_infix('100/7') == 14, '100 / 7 向零取整是 14，实际 %r' % (eval_infix('100/7'),)",
            "assert eval_infix('100-30-20') == 50, '减法左结合：(100 - 30) - 20 = 50，实际 %r' % (eval_infix('100-30-20'),)",
            "assert eval_infix('2+3*4-6/2') == 11, '2 + 12 - 3 = 11，实际 %r' % (eval_infix('2+3*4-6/2'),)",
            "assert eval_infix('1+2*3-4/2') == 5, '1 + 6 - 2 = 5，实际 %r' % (eval_infix('1+2*3-4/2'),)",
            "assert eval_infix('((2+3)*4-5)/3') == 5, '((2 + 3) * 4 - 5) / 3 = 5，实际 %r' % (eval_infix('((2+3)*4-5)/3'),)",
            "assert eval_infix('2*(3+(4-1))') == 12, '嵌套括号：2 * (3 + 3) = 12，实际 %r' % (eval_infix('2*(3+(4-1))'),)",
            "assert eval_infix('3*(4+5*(2-1))') == 27, '多层嵌套：3 * (4 + 5) = 27，实际 %r' % (eval_infix('3*(4+5*(2-1))'),)",
            "assert eval_infix('((((5))))') == 5, '多层多余括号不影响结果，实际 %r' % (eval_infix('((((5))))'),)",
            "assert eval_infix('20/(2*5)') == 2, '括号里先算乘法，实际 %r' % (eval_infix('20/(2*5)'),)",
            "assert eval_infix('100*2/5') == 40, '乘除同级左结合：(100 * 2) / 5 = 40，实际 %r' % (eval_infix('100*2/5'),)",
            "assert eval_infix('(1+2)*(3+4)') == 21, '两组括号相乘：3 * 7 = 21，实际 %r' % (eval_infix('(1+2)*(3+4)'),)",
            "assert eval_infix('8/3') == 2 and eval_infix('9/4') == 2, '整除不四舍五入：8/3 = 2、9/4 = 2，实际 %r / %r' % (eval_infix('8/3'), eval_infix('9/4'))",
            "_bad = False\ntry:\n    eval_infix('3+')\nexcept ValueError:\n    _bad = True\nassert _bad, '运算符后面没有操作数（\\'3+\\'）应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_infix('(3+4')\nexcept ValueError:\n    _bad = True\nassert _bad, '左括号没有闭合应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_infix('3+4)')\nexcept ValueError:\n    _bad = True\nassert _bad, '多余的右括号应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_infix('')\nexcept ValueError:\n    _bad = True\nassert _bad, '空表达式应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_infix('3++4')\nexcept ValueError:\n    _bad = True\nassert _bad, '连续两个运算符应抛出 ValueError'",
            "_bad = False\ntry:\n    eval_infix('3+4*')\nexcept ValueError:\n    _bad = True\nassert _bad, '表达式以运算符结尾应抛出 ValueError'",
            "assert 'append(' in _src and 'pop()' in _src, '题面要求用双栈（操作数栈 + 运算符栈）实现求值'",
        ],
        'explanation': (
            '双栈法其实就是「先转后缀再求值」的**合并版**：'
            '运算符栈负责决定「什么时候算」，操作数栈负责存数。\n\n'
            '```python\n'
            'def apply_top():\n'
            '    right = nums.pop()\n'
            '    left = nums.pop()\n'
            '    op = ops.pop()\n'
            '    ...\n'
            '```\n\n'
            '**为什么「栈顶优先级不低于当前运算符就立刻求值」？**'
            '因为中缀左结合：`100 * 2 / 5` 里 `/` 到来时 '
            '`*` 的两个操作数已经齐了，必须先算 `*`；'
            '而 `3 + 4 * 5` 里 `*` 到来时栈顶是 `+`，'
            '`+` 的右操作数（`4 * 5` 的结果）还没算出来，只能等——'
            '所以优先级低时不弹。\n\n'
            '**多位数是本题最容易翻车的地方**：读到一个数字字符后，'
            '必须继续往后吃数字直到不是数字为止，'
            '否则 `"10+20"` 会被拆成 1、0、+、2、0 五个 token。\n\n'
            '**左右操作数的顺序**：`right = nums.pop()` 先弹、`left = nums.pop()` 后弹，'
            '减法和除法全靠这个顺序；写反了 `10-3` 会算出 -7。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记「扫描结束后把 ops 里剩下的运算符算完」，`3+4*5` 会返回 4；\n'
            '2. 多位数只取第一个字符；\n'
            '3. 遇到 `)` 时把 `(` 也当运算符求值，导致操作数不足；\n'
            '4. 非法表达式直接 IndexError，没有按要求抛 `ValueError`；\n'
            '5. 除法用 `left // right`（负数时会向 -∞ 取整）。\n\n'
            '复杂度：时间 O(n)（每个 token 至多进出栈各一次）、'
            '额外空间 O(n)（两个栈）。'
        ),
        'expected_output': '23\n35\n70\n5',
        'hints': ['数字要整体解析（多位），压入操作数栈', '运算符入栈前先把栈顶「优先级不低于自己」的算掉；遇到右括号算到左括号为止'],
    },
    {
        'id': 'x823-221',
        'track': 'algorithm',
        'chapter_id': 144,
        'chapter_title': '823·栈与队列（提高）',
        'topic': '823·栈与队列（提高）',
        'title': '滑动窗口最大值（单调双端队列）',
        'difficulty': 3,
        'tags': ['双端队列', '单调队列', '滑动窗口'],
        'statement': (
            '定义函数 `max_sliding_window(nums, k)`：'
            '返回一个列表，其中第 `i` 个元素是 `nums[i .. i + k - 1]` 这个窗口的最大值。\n\n'
            '约定：\n\n'
            '- `nums` 是整数列表（可能有负数、重复值）；\n'
            '- 返回值的长度是 `len(nums) - k + 1`；\n'
            '- `nums` 为空、`k <= 0`、或 `k` 比 `len(nums)` 还大，都返回 `[]`。\n\n'
            '要求用**单调队列**（双端队列 `collections.deque`）做到 **O(n)**：\n\n'
            '- 队列里存**下标**（不是值），这些下标对应的值从队头到队尾**单调递减**；\n'
            '- 新元素 `x` 要进队时：先把队尾「值 ≤ x」的下标全部弹掉'
            '（它们已经不可能再成为任何窗口的最大值了），再压入当前下标；\n'
            '- 队头如果已经**滑出窗口**（下标 ≤ `i - k`），就把它从队头弹掉；\n'
            '- 队头始终是当前窗口最大值的下标。\n\n'
            '不许对每个窗口调用 `max()`（那是 O(n × k)），必须让每个元素**最多进出队各一次**。\n\n'
            '最后打印 `[1, 3, -1, -3, 5, 3, 6, 7]` 在 `k = 3` 时的结果，'
            '再打印 `[1]`（k = 1）和 `[]`（k = 3）的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef max_sliding_window(nums, k):\n    if not nums or k <= 0 or k > len(nums):\n        return []\n    dq = deque()\n    result = []\n    # dq 存下标且对应值单调递减；队头滑出窗口就 popleft\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "def max_sliding_window(nums, k):\n"
            "    if not nums or k <= 0 or k > len(nums):\n"
            "        return []\n"
            "    dq = deque()\n"
            "    result = []\n"
            "    for i, x in enumerate(nums):\n"
            "        while dq and nums[dq[-1]] <= x:\n"
            "            dq.pop()\n"
            "        dq.append(i)\n"
            "        if dq[0] <= i - k:\n"
            "            dq.popleft()\n"
            "        if i >= k - 1:\n"
            "            result.append(nums[dq[0]])\n"
            "    return result\n"
            "\n"
            "print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))\n"
            "print(max_sliding_window([1], 1))\n"
            "print(max_sliding_window([], 3))\n"
        ),
        'checks': [
            "assert max_sliding_window([], 1) == [], '空数组应返回 []'",
            "assert max_sliding_window([], 3) == [], '空数组配 k = 3 也应返回 []'",
            "assert max_sliding_window([1, 2, 3], 0) == [], 'k = 0 应返回 []'",
            "assert max_sliding_window([1, 2, 3], -1) == [], 'k 为负数应返回 []'",
            "assert max_sliding_window([1, 2, 3], 4) == [], 'k 比数组长度大应返回 []，实际 %r' % (max_sliding_window([1, 2, 3], 4),)",
            "assert max_sliding_window([5], 1) == [5], '只有一个元素时应返回 [5]，实际 %r' % (max_sliding_window([5], 1),)",
            "assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7], '经典例子应是 [3, 3, 5, 5, 6, 7]，实际 %r' % (max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3),)",
            "assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 1) == [1, 3, -1, -3, 5, 3, 6, 7], 'k = 1 时每个元素自己就是窗口最大值，实际 %r' % (max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 1),)",
            "assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 8) == [7], 'k 等于数组长度时只有一个窗口，实际 %r' % (max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 8),)",
            "assert max_sliding_window([2, 2, 2, 2], 2) == [2, 2, 2], '元素全相同时每个窗口的最大值都是 2，实际 %r' % (max_sliding_window([2, 2, 2, 2], 2),)",
            "assert max_sliding_window([5, 4, 3, 2, 1], 3) == [5, 4, 3], '递减序列每个窗口最大值是窗口第一个元素，实际 %r' % (max_sliding_window([5, 4, 3, 2, 1], 3),)",
            "assert max_sliding_window([1, 2, 3, 4, 5], 3) == [3, 4, 5], '递增序列每个窗口最大值是窗口最后一个元素，实际 %r' % (max_sliding_window([1, 2, 3, 4, 5], 3),)",
            "assert max_sliding_window([-7, -8, -3, -4], 2) == [-7, -3, -3], '全是负数时不能拿 0 当初始最大值，实际 %r' % (max_sliding_window([-7, -8, -3, -4], 2),)",
            "assert max_sliding_window([0, 0, -1, 5], 2) == [0, 0, 5], '有 0 和负数混在一起也要正确，实际 %r' % (max_sliding_window([0, 0, -1, 5], 2),)",
            "assert max_sliding_window([9, 8, 7, 6, 5, 4], 6) == [9], '整个数组是一个窗口时取全局最大值，实际 %r' % (max_sliding_window([9, 8, 7, 6, 5, 4], 6),)",
            "assert max_sliding_window([1, 2], 1) == [1, 2], '两个元素的 k = 1，实际 %r' % (max_sliding_window([1, 2], 1),)",
            "assert max_sliding_window([3, 1, 2], 3) == [3], '窗口覆盖全数组时最大值是 3，实际 %r' % (max_sliding_window([3, 1, 2], 3),)",
            "assert max_sliding_window([7, 2, 4, 6, 1, 9, 3], 4) == [7, 6, 9, 9], '混合数据多个窗口：%r' % (max_sliding_window([7, 2, 4, 6, 1, 9, 3], 4),)",
            "assert len(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)) == 6, '窗口个数应是 len(nums) - k + 1 = 6，实际 %r' % (len(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)),)",
            "_nums = list(range(1000))\nassert max_sliding_window(_nums, 100) == list(range(99, 1000)), '1000 个元素、窗口 100 时最大值是每个窗口的右端点，实际末位 %r' % (max_sliding_window(_nums, 100)[-1],)",
            "_nums = list(range(1000, 0, -1))\nassert max_sliding_window(_nums, 100) == list(range(1000, 99, -1)), '递减的 1000 个元素，最大值是每个窗口的左端点，实际首位 %r' % (max_sliding_window(_nums, 100)[0],)",
            "assert max_sliding_window(list(range(500)), 500) == [499], '500 个元素、窗口 500 时只有一个最大值 499'",
            "assert 'popleft' in _src, '题面要求用双端队列（deque 的 popleft）实现单调队列'",
            "assert 'max(' not in _src, '不许对每个窗口调用 max()（那是 O(n × k)），要用单调队列做到 O(n)'",
        ],
        'explanation': (
            '滑动窗口最大值的暴力做法是「每个窗口扫一遍」，O(n × k)。'
            '单调队列把它压到 O(n)，靠的是**及时丢掉没用的元素**。\n\n'
            '关键观察：如果新来的 `x` 比队列里某些旧元素还大，'
            '那么**在 x 过期之前，那些旧元素永远不可能成为最大值**（x 比它们大、还比它们晚过期），'
            '所以它们可以直接扔掉——这就是队尾的 `while dq and nums[dq[-1]] <= x: dq.pop()`。\n\n'
            '```python\n'
            'for i, x in enumerate(nums):\n'
            '    while dq and nums[dq[-1]] <= x:\n'
            '        dq.pop()                    # 比 x 小的旧元素没用了\n'
            '    dq.append(i)\n'
            '    if dq[0] <= i - k:\n'
            '        dq.popleft()                # 队头滑出窗口\n'
            '    if i >= k - 1:\n'
            '        result.append(nums[dq[0]])  # 队头就是窗口最大值\n'
            '```\n\n'
            '**为什么队列里存下标而不是值？** 因为要判断「是否滑出窗口」，'
            '必须知道每个元素的位置；只存值就没法判断过期。\n\n'
            '**为什么是 O(n)？** 每个下标最多被压入一次、弹出（队尾或队头）一次，'
            '均摊下来总操作数是 2n。\n\n'
            '**常见错误**：\n\n'
            '1. 队尾比较写成 `nums[dq[-1]] < x`（少了等号），'
            '   遇到相等元素时旧的下标留在队里，虽然结果常常还对，'
            '   但队列里会堆积过期的重复值；\n'
            '2. 忘记「队头滑出窗口」的检查，或者用 `i - k` 写成 `i - k + 1`（差一格）；\n'
            '3. 用 `max(nums[i:i + k])` 图省事——O(n × k)，本题的核心考点就没了；\n'
            '4. `k <= 0` 或 `k > len(nums)` 没拦住，返回空列表的要求没满足。\n\n'
            '复杂度：时间 O(n)（每个下标进出队各一次）、额外空间 O(k)（队列最多存 k 个下标）。'
        ),
        'expected_output': '[3, 3, 5, 5, 6, 7]\n[1]\n[]',
        'hints': ['队列存下标，对应值从队头到队尾单调递减', '新元素进队前先把队尾比它小的都弹掉；队头滑出窗口就 popleft'],
    },
]
