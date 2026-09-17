"""题库 · 西安科技大学 823《数据结构与算法》真题风格（进阶篇）· 专题 131–134。

写法约定与 qbank_408.py / qbank_basic.py 保持一致：

- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式；图的存储方式
  （邻接矩阵 / 邻接表字典 / 邻接表列表）、不连通怎么表示、空图怎么返回，都在题面里逐字交代，
  不让学生猜。
- checks 是**字符串列表**，判题时在**同一个全局命名空间**里执行：可以直接调用学生定义好的
  函数 / 类，也可以用平台注入的 `_out`（学生的全部标准输出）与 `_src`（学生的全部源码）。
  每条断言都带中文提示，并覆盖空输入、单元素、重复元素、已有序、不连通等边界。
- 参考答案必须能通过自己这一整套断言。

本文件对应老师整理的第 5~8 章题库（题 13 ~ 题 29，共 17 道）：

    第 5 章 树与二叉树   题 13 递归遍历 / 题 14 层序遍历 / 题 15 先序中序还原 / 题 16 哈夫曼 WPL
    第 6 章 图           题 17 邻接矩阵 DFS / 题 18 邻接表 BFS / 题 19 Prim / 题 20 拓扑排序 /
                        题 21 Dijkstra
    第 7 章 查找         题 22 折半查找 / 题 23 二叉排序树 / 题 24 散列表（线性探测）
    第 8 章 内部排序     题 25 冒泡 / 题 26 直接插入 / 题 27 快速 / 题 28 归并 / 题 29 堆排序

专题划分（chapter_id / chapter_title / topic 三个字段同值）：

    131 823·树与二叉树    132 823·图    133 823·查找    134 823·内部排序

全局约定：

- 图的权值统一为**正整数**；「无边」统一用 `float('inf')` 表示（`0` 只出现在对角线，表示
  自己到自己）；全篇不出现负权边。
- 需要在学生代码里固定名字的东西（结点类属性、函数名、类方法名、返回值形状）都写在题面里。
- 编号从 x823-101 起（001–099 归同事的基础篇，不要占用）。
"""

QUESTIONS = [
    # ── 专题 131 · 823·树与二叉树（题 13–16）───────────────
    {
        'id': 'x823-101',
        'track': 'algorithm',
        'chapter_id': 131,
        'chapter_title': '823·树与二叉树',
        'topic': '823·树与二叉树',
        'title': '题13 二叉树的递归遍历（先序 / 中序 / 后序）',
        'difficulty': 1,
        'tags': ['二叉树', '先序遍历', '中序遍历', '后序遍历', '递归'],
        'statement': (
            '**考点：先序、中序、后序遍历序列。**\n\n'
            '按下面的定义写好二叉树结点类（属性名必须一致）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义三个**递归**遍历函数，参数都是根结点 `root`，返回值都是「访问到的结点值」'
            '组成的**列表**：\n\n'
            '- `preorder(root)`：先序遍历，顺序是 **根 → 左 → 右**；\n'
            '- `inorder(root)`：中序遍历，顺序是 **左 → 根 → 右**；\n'
            '- `postorder(root)`：后序遍历，顺序是 **左 → 右 → 根**。\n\n'
            '规定：\n\n'
            '- **空树返回 `[]`**（`root is None` 时直接返回空表，不要报错）；\n'
            '- 三个函数都必须**用递归**实现（在自己的函数体里调用自己），不要改写成栈 / 循环版本；\n'
            '- 只读遍历，不要修改树的结点（`left`、`right`、`val` 都不许动）。\n\n'
            '最后打印下面这棵树的三个序列：\n\n'
            '```\n'
            '        1\n'
            '      /   \\\n'
            '     2     3\n'
            '    / \\   / \\\n'
            '   4   5 6   7\n'
            '```\n\n'
            '构造方式就是 `TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), '
            'TreeNode(3, TreeNode(6), TreeNode(7)))`。\n\n'
            '再打印空树 `None`、以及左斜树 `3(2(1))`（写成 `TreeNode(3, TreeNode(2, TreeNode(1)))`）'
            '的三个序列。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef preorder(root):\n    # 根 → 左 → 右\n    pass\n\ndef inorder(root):\n    # 左 → 根 → 右\n    pass\n\ndef postorder(root):\n    # 左 → 右 → 根\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def preorder(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return [root.val] + preorder(root.left) + preorder(root.right)\n"
            "\n"
            "def inorder(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return inorder(root.left) + [root.val] + inorder(root.right)\n"
            "\n"
            "def postorder(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return postorder(root.left) + postorder(root.right) + [root.val]\n"
            "\n"
            "tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))\n"
            "print(preorder(tree))\n"
            "print(inorder(tree))\n"
            "print(postorder(tree))\n"
            "print(preorder(None), inorder(None), postorder(None))\n"
            "skew = TreeNode(3, TreeNode(2, TreeNode(1)))\n"
            "print(preorder(skew), inorder(skew), postorder(skew))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert preorder(None) == [] and inorder(None) == [] and postorder(None) == [], '空树三个遍历都应返回 []，实际 %r / %r / %r' % (preorder(None), inorder(None), postorder(None))",
            "_n = TreeNode(1)\nassert preorder(_n) == [1] and inorder(_n) == [1] and postorder(_n) == [1], '只有一个根结点时三个序列都是 [1]，实际 %r / %r / %r' % (preorder(_n), inorder(_n), postorder(_n))",
            "_n = TreeNode(1, TreeNode(2), TreeNode(3))\nassert preorder(_n) == [1, 2, 3], '先序应是 [1, 2, 3]（根 1 先访问），实际 %r' % (preorder(_n),)",
            "_n = TreeNode(1, TreeNode(2), TreeNode(3))\nassert inorder(_n) == [2, 1, 3], '中序应是 [2, 1, 3]，实际 %r' % (inorder(_n),)",
            "_n = TreeNode(1, TreeNode(2), TreeNode(3))\nassert postorder(_n) == [2, 3, 1], '后序应是 [2, 3, 1]（根最后访问），实际 %r' % (postorder(_n),)",
            "_t = _tree([1, 2, 3, 4, 5, 6, 7])\nassert preorder(_t) == [1, 2, 4, 5, 3, 6, 7], '满二叉树的先序应是 [1, 2, 4, 5, 3, 6, 7]，实际 %r' % (preorder(_t),)",
            "_t = _tree([1, 2, 3, 4, 5, 6, 7])\nassert inorder(_t) == [4, 2, 5, 1, 6, 3, 7], '满二叉树的中序应是 [4, 2, 5, 1, 6, 3, 7]，实际 %r' % (inorder(_t),)",
            "_t = _tree([1, 2, 3, 4, 5, 6, 7])\nassert postorder(_t) == [4, 5, 2, 6, 7, 3, 1], '满二叉树的后序应是 [4, 5, 2, 6, 7, 3, 1]，实际 %r' % (postorder(_t),)",
            "_t = _tree([3, 2, None, 1])\nassert preorder(_t) == [3, 2, 1] and inorder(_t) == [1, 2, 3] and postorder(_t) == [1, 2, 3], '一直往左的斜树：先序 [3, 2, 1]、中序与后序都是 [1, 2, 3]，实际 %r / %r / %r' % (preorder(_t), inorder(_t), postorder(_t))",
            "_t = _tree([1, None, 2, None, 3])\nassert preorder(_t) == [1, 2, 3] and inorder(_t) == [1, 2, 3] and postorder(_t) == [3, 2, 1], '一直往右的斜树：先序与中序都是 [1, 2, 3]、后序是 [3, 2, 1]，实际 %r / %r / %r' % (preorder(_t), inorder(_t), postorder(_t))",
            "_t = _tree([2, 2, 2])\nassert preorder(_t) == [2, 2, 2] and inorder(_t) == [2, 2, 2] and postorder(_t) == [2, 2, 2], '值全相同时每个结点都要访问一次（不是只访问一个），实际 %r / %r / %r' % (preorder(_t), inorder(_t), postorder(_t))",
            "_t = _tree([-1, -2, -3])\nassert preorder(_t) == [-1, -2, -3] and inorder(_t) == [-2, -1, -3] and postorder(_t) == [-2, -3, -1], '负数同样要按顺序访问，实际 %r / %r / %r' % (preorder(_t), inorder(_t), postorder(_t))",
            "_t = _tree(list(range(1, 16)))\nassert preorder(_t) == [1, 2, 4, 8, 9, 5, 10, 11, 3, 6, 12, 13, 7, 14, 15], '15 个结点的满二叉树先序不对：%r' % (preorder(_t),)",
            "_t = _tree(list(range(1, 16)))\nassert inorder(_t) == [8, 4, 9, 2, 10, 5, 11, 1, 12, 6, 13, 3, 14, 7, 15], '15 个结点的满二叉树中序不对：%r' % (inorder(_t),)",
            "_t = _tree(list(range(1, 16)))\nassert postorder(_t) == [8, 9, 4, 10, 11, 5, 2, 12, 13, 6, 14, 15, 7, 3, 1], '15 个结点的满二叉树后序不对：%r' % (postorder(_t),)",
            "_body = _src.partition('def preorder')[2].partition('\\ndef ')[0]\nassert 'preorder(' in _body, '题面要求 preorder 用递归实现（在自己的函数体里调用自己），函数体里没有检测到递归调用'",
            "_body = _src.partition('def inorder')[2].partition('\\ndef ')[0]\nassert 'inorder(' in _body, '题面要求 inorder 用递归实现（在自己的函数体里调用自己），函数体里没有检测到递归调用'",
            "_body = _src.partition('def postorder')[2].partition('\\ndef ')[0]\nassert 'postorder(' in _body, '题面要求 postorder 用递归实现（在自己的函数体里调用自己），函数体里没有检测到递归调用'",
            "_t = _tree([1, 2, 3, 4, 5, 6, 7])\npreorder(_t)\ninorder(_t)\npostorder(_t)\nassert _t.left.left.val == 4 and _t.right.right.val == 7, '遍历是只读操作，不许改动树的结构，实际左左孩子 %r' % (_t.left.left.val,)",
        ],
        'explanation': (
            '三种遍历的差别只在「访问根」的时机，代码骨架完全一样：\n\n'
            '```python\n'
            'def preorder(root):\n'
            '    if root is None:\n'
            '        return []\n'
            '    return [root.val] + preorder(root.left) + preorder(root.right)\n'
            '```\n\n'
            '中序把 `[root.val]` 挪到两次递归中间，后序把它挪到两次递归后面。'
            '递归的语义是「整棵子树交给同名的函数处理」，所以写的时候只要保证'
            '「根、左、右」三块拼装顺序正确即可。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记写空树出口（`if root is None: return []`），叶子结点上 '
            '`root.left` 会直接 `AttributeError`；\n'
            '2. 用全局列表收集结果却不带参数（多次调用会互相污染），'
            '本题要求**返回**列表，最稳妥的写法就是上面这种拼接；\n'
            '3. 中序写成「先根后左」，或后序把根放在中间；\n'
            '4. 三个函数写成同一段代码改个名字，结果三个序列一模一样。\n\n'
            '**自检办法**：先序的第一个一定是根，后序的最后一个一定是根，'
            '中序里根把左右子树的值分成两段——用这棵 `1(2(4, 5), 3(6, 7))` 手工对一遍即可。\n\n'
            '复杂度：每个结点访问一次，时间 O(n)；递归深度等于树高，'
            '空间 O(h)（最坏 O(n)，平均 O(log n)）。'
        ),
        'expected_output': '[1, 2, 4, 5, 3, 6, 7]\n[4, 2, 5, 1, 6, 3, 7]\n[4, 5, 2, 6, 7, 3, 1]\n[] [] []\n[3, 2, 1] [1, 2, 3] [1, 2, 3]',
        'hints': ['先序：根 → 左 → 右；中序：左 → 根 → 右；后序：左 → 右 → 根', '空树先返回 []，再按顺序拼接三段结果'],
    },
    {
        'id': 'x823-102',
        'track': 'algorithm',
        'chapter_id': 131,
        'chapter_title': '823·树与二叉树',
        'topic': '823·树与二叉树',
        'title': '题14 二叉树的层序遍历（按层返回）',
        'difficulty': 2,
        'tags': ['二叉树', '层序遍历', '队列', 'BFS'],
        'statement': (
            '**考点：层序遍历、队列实现。**\n\n'
            '沿用结点类（属性名必须一致）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `level_order(root)`：用**队列**实现二叉树的层序遍历，'
            '**按层**返回结点值——返回值是「列表的列表」：\n\n'
            '- 外层一个元素代表一层，从第 1 层（根所在层）往下；\n'
            '- 每层内部按**从左到右**排；\n'
            '- 空树返回 `[]`（不是 `[[]]`）。\n\n'
            '例如树 `1(2(_, 4), 3(_, 5))`（按层序记作 `[1, 2, 3, None, 4, None, 5]`）'
            '应返回 `[[1], [2, 3], [4, 5]]`。\n\n'
            '要求：\n\n'
            '- 用列表当队列（队尾 `append`、队头 `pop(0)`）或者用 `collections.deque`，'
            '**不要用递归**；\n'
            '- 关键是「分批出队」：每轮循环开始时先记下 `len(queue)`，'
            '它就是这一层的结点个数，用 `for _ in range(size)` 整好处理这么多结点，'
            '一边出队一边把左右孩子入队；\n'
            '- 这一轮结束后队列里恰好全是下一层的结点。\n\n'
            '最后打印 `[1, 2, 3, None, 4, None, 5]` 这棵树的结果，'
            '再打印空树、单结点树 `[1]`、以及三层满二叉树 `[1, 2, 3, 4, 5, 6, 7]` 的结果。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef level_order(root):\n    if root is None:\n        return []\n    result = []\n    queue = [root]\n    # 每轮先量一次 len(queue)，再整好处理这一层\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def level_order(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    result = []\n"
            "    queue = [root]\n"
            "    while queue:\n"
            "        size = len(queue)\n"
            "        level = []\n"
            "        for _ in range(size):\n"
            "            node = queue.pop(0)\n"
            "            level.append(node.val)\n"
            "            if node.left is not None:\n"
            "                queue.append(node.left)\n"
            "            if node.right is not None:\n"
            "                queue.append(node.right)\n"
            "        result.append(level)\n"
            "    return result\n"
            "\n"
            "def build(values):\n"
            "    if not values:\n"
            "        return None\n"
            "    root = TreeNode(values[0])\n"
            "    queue = [root]\n"
            "    index = 1\n"
            "    while queue and index < len(values):\n"
            "        node = queue.pop(0)\n"
            "        if index < len(values) and values[index] is not None:\n"
            "            node.left = TreeNode(values[index])\n"
            "            queue.append(node.left)\n"
            "        index += 1\n"
            "        if index < len(values) and values[index] is not None:\n"
            "            node.right = TreeNode(values[index])\n"
            "            queue.append(node.right)\n"
            "        index += 1\n"
            "    return root\n"
            "\n"
            "print(level_order(build([1, 2, 3, None, 4, None, 5])))\n"
            "print(level_order(None))\n"
            "print(level_order(build([1])))\n"
            "print(level_order(build([1, 2, 3, 4, 5, 6, 7])))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert level_order(None) == [], '空树应返回 []（不是 [[]]），实际 %r' % (level_order(None),)",
            "assert level_order(TreeNode(1)) == [[1]], '只有一个根结点时应返回 [[1]]，实际 %r' % (level_order(TreeNode(1)),)",
            "assert level_order(TreeNode(1, TreeNode(2), TreeNode(3))) == [[1], [2, 3]], '两个孩子应在同一层：[[1], [2, 3]]，实际 %r' % (level_order(TreeNode(1, TreeNode(2), TreeNode(3))),)",
            "_t = _tree([1, 2, 3, 4, 5, 6, 7])\nassert level_order(_t) == [[1], [2, 3], [4, 5, 6, 7]], '三层满二叉树应是 [[1], [2, 3], [4, 5, 6, 7]]，实际 %r' % (level_order(_t),)",
            "_t = _tree([1, 2, 3, None, 4, None, 5])\nassert level_order(_t) == [[1], [2, 3], [4, 5]], '缺左孩子的两层树应是 [[1], [2, 3], [4, 5]]（按层号分，不按父亲分），实际 %r' % (level_order(_t),)",
            "_t = _tree([3, 2, None, 1])\nassert level_order(_t) == [[3], [2], [1]], '一直往左的斜树每层只有一个结点，实际 %r' % (level_order(_t),)",
            "_t = _tree([1, None, 2, None, 3])\nassert level_order(_t) == [[1], [2], [3]], '一直往右的斜树每层只有一个结点，实际 %r' % (level_order(_t),)",
            "_t = _tree([2, 2, 2])\nassert level_order(_t) == [[2], [2, 2]], '值全部相同时每个结点都要按层输出一次，实际 %r' % (level_order(_t),)",
            "_t = _tree([-1, -2, 3, -4])\nassert level_order(_t) == [[-1], [-2, 3], [-4]], '负数和缺孩子的情况也要对，实际 %r' % (level_order(_t),)",
            "_nodes = [TreeNode(_i) for _i in range(63)]\nfor _i in range(31):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\n_r = level_order(_nodes[0])\nassert [len(_lv) for _lv in _r] == [1, 2, 4, 8, 16, 32], '6 层满二叉树每层结点数应是 1/2/4/8/16/32，实际 %r' % ([len(_lv) for _lv in _r],)",
            "_nodes = [TreeNode(_i) for _i in range(63)]\nfor _i in range(31):\n    _nodes[_i].left = _nodes[2 * _i + 1]\n    _nodes[_i].right = _nodes[2 * _i + 2]\n_r = level_order(_nodes[0])\nassert _r[0] == [0] and _r[-1] == list(range(31, 63)), '满二叉树的最后一层应是从 31 到 62，实际 %r' % (_r[-1][:5],)",
            "_t = _tree([1, 2, 3, None, 4, None, 5])\n_r = level_order(_t)\nassert isinstance(_r, list) and all(isinstance(_lv, list) for _lv in _r), '返回值必须是「列表的列表」，每层一个列表，实际 %r' % (_r,)",
            "_deep = TreeNode(0)\nfor _i in range(1, 300):\n    _deep = TreeNode(_i, _deep)\n_r = level_order(_deep)\nassert len(_r) == 300 and all(_lv == [_i] for _lv, _i in zip(_r, range(299, -1, -1))), '300 层深的左斜树要能走完且每层 1 个结点，实际层数 %r' % (len(_r),)",
            "assert 'pop(0)' in _src or 'popleft' in _src or 'deque' in _src, '题面要求用队列实现（列表的 pop(0) 或 collections.deque 的 popleft），没有检测到出队操作'",
        ],
        'explanation': (
            '层序遍历 = BFS，靠**队列**保证「先遇到的先访问」。'
            '要把结果按层切开，诀窍是**每轮先量一次队长**：\n\n'
            '```python\n'
            'while queue:\n'
            '    size = len(queue)        # 这一层还剩多少个结点没出队\n'
            '    level = []\n'
            '    for _ in range(size):    # 只处理这一层的 size 个\n'
            '        node = queue.pop(0)\n'
            '        level.append(node.val)\n'
            '        if node.left:  queue.append(node.left)\n'
            '        if node.right: queue.append(node.right)\n'
            '    result.append(level)\n'
            '```\n\n'
            '循环里新入队的孩子都排在队尾，不会被这一轮的 `for` 处理到，'
            '所以 `size` 天然把「当前层」和「下一层」分开了。\n\n'
            '**常见错误**：\n\n'
            '1. 直接 `while queue: node = queue.pop(0); ...` 不记 `size`，'
            '结果是一个扁平的 BFS 序列，没法按层切开；\n'
            '2. 把 `size = len(queue)` 写在 `for` 循环体内（每轮重新量），层号会串；\n'
            '3. 空树没拦，`queue = [None]` 后访问 `None.val` 报错；\n'
            '4. 用递归做层序（可以，但要传层号并按层号填结果），本题要求队列。\n\n'
            '顺带记住：**「按层切开」的写法在求宽度、求层数、之字形遍历里都要用**，'
            '是树这一章最值钱的模板之一。\n\n'
            '复杂度：每个结点入队出队各一次，时间 O(n)；'
            '队列最长时存一整层，空间 O(宽度)。'
        ),
        'expected_output': '[[1], [2, 3], [4, 5]]\n[]\n[[1]]\n[[1], [2, 3], [4, 5, 6, 7]]',
        'hints': ['每轮先记 size = len(queue)，用 for _ in range(size) 处理这一层', '孩子一律 append 到队尾，它们自然属于下一层'],
    },
    {
        'id': 'x823-103',
        'track': 'algorithm',
        'chapter_id': 131,
        'chapter_title': '823·树与二叉树',
        'topic': '823·树与二叉树',
        'title': '题15 由先序 + 中序序列还原二叉树',
        'difficulty': 2,
        'tags': ['二叉树', '遍历序列还原', '递归', '分治'],
        'statement': (
            '**考点：由遍历序列还原二叉树（823 大题高频）。**\n\n'
            '已知二叉树的**先序遍历序列** `preorder` 和**中序遍历序列** `inorder`，'
            '两个都是整数列表。\n\n'
            '定义函数 `build_tree(preorder, inorder)`：重建这棵二叉树，'
            '**返回根结点**（结点类定义如下，属性名必须一致）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '约定：\n\n'
            '- 两个列表都为空 → 返回 `None`（空树）；\n'
            '- 两个列表长度不等、或元素集合不同（非法输入）→ 返回 `None`；\n'
            '- 结点值可能有重复（有的考卷会这么出），因此**必须按位置切分**、'
            '不能用「值 → 下标」的字典去重；\n'
            '- **不要修改**传入的两个列表；\n'
            '- 必须真的把树建出来（返回的根结点上 `left` / `right` 要挂好），'
            '不能只把序列塞进某个对象里糊弄过去。\n\n'
            '算法提示（分治）：\n\n'
            '1. `preorder[0]` 就是根；\n'
            '2. 在中序段里找到这个根的位置 `k`，则 `inorder[:k]` 是左子树的中序、'
            '`inorder[k+1:]` 是右子树的中序；\n'
            '3. 左子树有 `k` 个结点，所以 `preorder[1 : 1 + k]` 是左子树的先序，'
            '剩下的 `preorder[1 + k:]` 是右子树的先序；\n'
            '4. 对左右两段递归。\n\n'
            '例如 `preorder = [3, 9, 20, 15, 7]`、`inorder = [9, 3, 15, 20, 7]`，'
            '还原出来的树是 `3(9, 20(15, 7))`。\n\n'
            '最后打印上面这棵树的先序与中序（自己写遍历函数验证），'
            '再打印空序列、单结点 `[1] / [1]`、以及左斜树 `[3, 2, 1] / [1, 2, 3]` 的还原结果。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef build_tree(preorder, inorder):\n    # 根 = preorder[0]；在中序里定位根，切出左右子树的两段序列，递归\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def build_tree(preorder, inorder):\n"
            "    if not preorder and not inorder:\n"
            "        return None\n"
            "    if len(preorder) != len(inorder):\n"
            "        return None\n"
            "    if sorted(preorder) != sorted(inorder):\n"
            "        return None\n"
            "\n"
            "    def build(pl, pr, il, ir):\n"
            "        if pl > pr:\n"
            "            return None\n"
            "        node = TreeNode(preorder[pl])\n"
            "        k = inorder.index(preorder[pl], il, ir + 1)\n"
            "        left_size = k - il\n"
            "        node.left = build(pl + 1, pl + left_size, il, k - 1)\n"
            "        node.right = build(pl + left_size + 1, pr, k + 1, ir)\n"
            "        return node\n"
            "\n"
            "    return build(0, len(preorder) - 1, 0, len(inorder) - 1)\n"
            "\n"
            "def pre_of(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return [root.val] + pre_of(root.left) + pre_of(root.right)\n"
            "\n"
            "def in_of(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return in_of(root.left) + [root.val] + in_of(root.right)\n"
            "\n"
            "root = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])\n"
            "print(pre_of(root), in_of(root))\n"
            "print(build_tree([], []))\n"
            "one = build_tree([1], [1])\n"
            "print(pre_of(one), in_of(one))\n"
            "skew = build_tree([3, 2, 1], [1, 2, 3])\n"
            "print(pre_of(skew), in_of(skew))\n"
        ),
        'checks': [
            "def _pre(root):\n    if root is None:\n        return []\n    return [root.val] + _pre(root.left) + _pre(root.right)",
            "def _in(root):\n    if root is None:\n        return []\n    return _in(root.left) + [root.val] + _in(root.right)",
            "assert build_tree([], []) is None, '两个空列表应返回 None（空树）'",
            "_r = build_tree([1], [1])\nassert _r is not None and _r.val == 1 and _r.left is None and _r.right is None, '单结点应还原出一个值为 1 的叶子，实际 %r' % (_r,)",
            "_r = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])\nassert _r is not None and _pre(_r) == [3, 9, 20, 15, 7] and _in(_r) == [9, 3, 15, 20, 7], '还原出的树先序/中序应与输入一致，实际 %r / %r' % (_pre(_r) if _r else None, _in(_r) if _r else None)",
            "_r = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])\nassert _r.left is not None and _r.left.val == 9 and _r.right is not None and _r.right.val == 20, '根 3 的左孩子应是 9、右孩子应是 20，实际 %r / %r' % (_r.left.val if _r.left else None, _r.right.val if _r.right else None)",
            "_r = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])\nassert _r.right.left is not None and _r.right.left.val == 15 and _r.right.right.val == 7, '20 的左孩子是 15、右孩子是 7，实际 %r' % (_r.right.left.val if _r.right.left else None,)",
            "_r = build_tree([1, 2, 3], [1, 2, 3])\nassert _pre(_r) == [1, 2, 3] and _r.left is None and _r.right is not None and _r.right.val == 2, '先序与中序相同说明是「只有右孩子」的右斜树，实际 %r' % (_pre(_r),)",
            "_r = build_tree([3, 2, 1], [1, 2, 3])\nassert _pre(_r) == [3, 2, 1] and _r.right is None and _r.left is not None and _r.left.val == 2, '先序逆序、中序顺序说明是左斜树，实际 %r' % (_pre(_r),)",
            "_full_pre = [1, 2, 4, 8, 9, 5, 10, 11, 3, 6, 12, 13, 7, 14, 15]\n_full_in = [8, 4, 9, 2, 10, 5, 11, 1, 12, 6, 13, 3, 14, 7, 15]\n_r = build_tree(_full_pre, _full_in)\nassert _pre(_r) == _full_pre, '15 个结点的满二叉树先序不对：%r' % (_pre(_r),)",
            "_full_pre = [1, 2, 4, 8, 9, 5, 10, 11, 3, 6, 12, 13, 7, 14, 15]\n_full_in = [8, 4, 9, 2, 10, 5, 11, 1, 12, 6, 13, 3, 14, 7, 15]\n_r = build_tree(_full_pre, _full_in)\nassert _in(_r) == _full_in, '15 个结点的满二叉树中序不对：%r' % (_in(_r),)",
            "_r = build_tree([0, -1, -2, -3], [-3, -2, -1, 0])\nassert _pre(_r) == [0, -1, -2, -3] and _in(_r) == [-3, -2, -1, 0], '有负数时也要还原正确，实际 %r / %r' % (_pre(_r), _in(_r))",
            "_r = build_tree([7, 7, 3], [7, 3, 7])\nassert _r is not None and _pre(_r) == [7, 7, 3] and _in(_r) == [7, 3, 7], '序列里有重复值时必须按位置切分（根 7 要取中序段里第一个 7，右子树才是 7(3)），实际 %r / %r' % (_pre(_r) if _r else None, _in(_r) if _r else None)",
            "assert build_tree([1, 2], [1]) is None, '两个序列长度不等属于非法输入，应返回 None，实际 %r' % (build_tree([1, 2], [1]),)",
            "assert build_tree([1, 2], [2, 3]) is None, '两个序列元素集合不同属于非法输入，应返回 None，实际 %r' % (build_tree([1, 2], [2, 3]),)",
            "_p = [3, 9, 20, 15, 7]\n_i = [9, 3, 15, 20, 7]\nbuild_tree(_p, _i)\nassert _p == [3, 9, 20, 15, 7] and _i == [9, 3, 15, 20, 7], '题面要求不要修改传入的序列，实际 %r / %r' % (_p, _i)",
            "_r = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])\nassert isinstance(_r, TreeNode), '返回值必须是 TreeNode 结点（不是列表、不是字典），实际 %r' % (type(_r),)",
            "_n = 150\n_p = list(range(_n))\n_i = list(range(_n - 1, -1, -1))\n_r = build_tree(_p, _i)\nassert _pre(_r) == _p and _in(_r) == _i, '150 个结点、先序逆序的左斜树要能还原，实际先序前 3 位 %r' % (_pre(_r)[:3],)",
            "_n = 200\n_p = list(range(_n))\n_i = list(range(_n))\n_r = build_tree(_p, _i)\nassert _pre(_r) == _p and _r.left is None and _in(_r) == _i, '200 个结点的右斜树（先序与中序相同）也要还原对，实际先序前 3 位 %r' % (_pre(_r)[:3],)",
        ],
        'explanation': (
            '还原的思路是「先序定根、中序分左右」：\n\n'
            '- **先序的第一个元素一定是根**（先访问根）；\n'
            '- 在中序段里找到根的位置 `k`：它左边有 `k - il` 个元素，全是左子树的结点；'
            '右边是右子树的结点；\n'
            '- 于是先序里紧跟根的那 `k - il` 个元素属于左子树，剩下的属于右子树；\n'
            '- 左右两段各自又满足同样的规律——递归。\n\n'
            '```python\n'
            'def build(pl, pr, il, ir):\n'
            '    if pl > pr:\n'
            '        return None\n'
            '    node = TreeNode(preorder[pl])\n'
            '    k = inorder.index(preorder[pl], il, ir + 1)   # 根在中序段里的位置\n'
            '    left_size = k - il\n'
            '    node.left  = build(pl + 1, pl + left_size, il, k - 1)\n'
            '    node.right = build(pl + left_size + 1, pr, k + 1, ir)\n'
            '    return node\n'
            '```\n\n'
            '用**下标**（`pl / pr / il / ir`）而不是每次切片，是为了避免 O(n²) 的列表复制；'
            '`inorder.index(value, il, ir + 1)` 只在当前中序段里找，'
            '即使序列里有重复值也能按位置正确切分（本题特意保留了这个情况）。\n\n'
            '**常见错误**：\n\n'
            '1. 左子树长度算错：写成 `pl + k`（应该是 `pl + 1 + (k - il)`）；\n'
            '2. 只返回值不挂指针：`return TreeNode(preorder[0])` 就不管左右子树了；\n'
            '3. 用「值 → 下标」字典缓存位置，一遇到重复值就切错；\n'
            '4. 空序列直接 `preorder[0]`，忘了先判空 / 判非法输入。\n\n'
            '**要背下来的结论**：中序 + 先序（或中序 + 后序）能唯一确定一棵二叉树；'
            '先序 + 后序**不行**（分不清只有一个孩子的结点是左孩子还是右孩子）。\n\n'
            '复杂度：时间 O(n log n)~O(n²)（取决于 `index` 查找；值互不相同时可加哈希做到 O(n)），'
            '空间 O(n)（递归栈 O(h) + 结点本身）。'
        ),
        'expected_output': '[3, 9, 20, 15, 7] [9, 3, 15, 20, 7]\nNone\n[1] [1]\n[3, 2, 1] [1, 2, 3]',
        'hints': ['先序的第一个是根；在中序里找它的位置，左边是左子树、右边是右子树', '左子树的结点个数 = 根在中序里的下标 - 该段中序的左边界'],
    },
    {
        'id': 'x823-104',
        'track': 'algorithm',
        'chapter_id': 131,
        'chapter_title': '823·树与二叉树',
        'topic': '823·树与二叉树',
        'title': '题16 哈夫曼树构建与 WPL 计算',
        'difficulty': 2,
        'tags': ['哈夫曼树', 'WPL', '优先队列', '贪心'],
        'statement': (
            '**考点：哈夫曼树的构造、带权路径长度 WPL（823 大题必考）。**\n\n'
            '给定一组权值 `weights`（**非负整数**的列表，允许取 0、允许重复），'
            '按哈夫曼算法构造哈夫曼树，返回它的**带权路径长度 WPL**'
            '（WPL = 每个叶子权值 × 该叶子到根的路径长度，再求和）。\n\n'
            '定义函数 `huffman_wpl(weights)`：\n\n'
            '- 返回 WPL（**整数**）；\n'
            '- 空列表返回 `0`；只剩一个权值时返回 `0`（只有一个叶子，路径长度为 0）；\n'
            '- **不要修改**传入的 `weights` 列表（也不许就地排序）。\n\n'
            '哈夫曼算法（每一步都取当前最小的两个）：\n\n'
            '1. 把所有权值放进一个「小根堆」（优先队列）；\n'
            '2. 每次弹出两个最小的权值 `a`、`b`，合并成新结点 `a + b`；\n'
            '3. 把 `a + b` 放回优先队列（它同时是这棵新子树的根权）；\n'
            '4. 重复到只剩一个结点。\n\n'
            '**WPL 有个不用画树就能算的口径：把每次合并出来的新结点权值全部加起来。**'
            '所以上面第 2~3 步每合并一次就把 `a + b` 累加进答案即可。\n\n'
            '例如 `weights = [8, 3, 5, 7]`：先合并 3 + 5 = 8，再合并 7 + 8 = 15，'
            '最后合并 8 + 15 = 23，WPL = 8 + 15 + 23 = **46**。\n\n'
            '最后打印 `[8, 3, 5, 7]`、`[1, 2, 3, 4, 5]`、空列表、单元素 `[5]` 的结果。'
        ),
        'starter_code': 'import heapq\n\ndef huffman_wpl(weights):\n    heap = list(weights)\n    heapq.heapify(heap)\n    total = 0\n    # 每次弹出两个最小权值，合并后放回，并把合并值累加进 total\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def huffman_wpl(weights):\n"
            "    if len(weights) <= 1:\n"
            "        return 0\n"
            "    heap = list(weights)\n"
            "    heapq.heapify(heap)\n"
            "    total = 0\n"
            "    while len(heap) > 1:\n"
            "        a = heapq.heappop(heap)\n"
            "        b = heapq.heappop(heap)\n"
            "        merged = a + b\n"
            "        total += merged\n"
            "        heapq.heappush(heap, merged)\n"
            "    return total\n"
            "\n"
            "print(huffman_wpl([8, 3, 5, 7]))\n"
            "print(huffman_wpl([1, 2, 3, 4, 5]))\n"
            "print(huffman_wpl([]))\n"
            "print(huffman_wpl([5]))\n"
        ),
        'checks': [
            "assert huffman_wpl([]) == 0, '空列表返回 0，实际 %r' % (huffman_wpl([]),)",
            "assert huffman_wpl([5]) == 0, '只剩一个权值时它自己就是根，WPL = 0，实际 %r' % (huffman_wpl([5]),)",
            "assert huffman_wpl([0]) == 0, '单个 0 权值也是 0，实际 %r' % (huffman_wpl([0]),)",
            "assert huffman_wpl([2, 2]) == 4, '两个权值 2、2：合并一次得 4，WPL = 4，实际 %r' % (huffman_wpl([2, 2]),)",
            "assert huffman_wpl([8, 3, 5, 7]) == 46, '老师给的例子 [8, 3, 5, 7]：合并 3+5=8、7+8=15、8+15=23，WPL = 8+15+23 = 46，实际 %r' % (huffman_wpl([8, 3, 5, 7]),)",
            "assert huffman_wpl([1, 2, 3, 4, 5]) == 33, '五个权值 1~5 的 WPL 是 33（合并 1+2=3、3+3=6、4+5=9、6+9=15，累加 3+6+9+15=33），实际 %r' % (huffman_wpl([1, 2, 3, 4, 5]),)",
            "assert huffman_wpl([1, 2, 3]) == 9, '三个权值 1、2、3：合并 1+2=3、3+3=6，WPL = 3+6 = 9，实际 %r' % (huffman_wpl([1, 2, 3]),)",
            "assert huffman_wpl([5, 5, 5, 5]) == 40, '四个相等的权值 5：每个深度都是 2，WPL = 2 × (5+5+5+5) = 40，实际 %r' % (huffman_wpl([5, 5, 5, 5]),)",
            "assert huffman_wpl([1, 1, 1, 1]) == 8, '四个 1 的 WPL 是 8，实际 %r' % (huffman_wpl([1, 1, 1, 1]),)",
            "assert huffman_wpl([4, 4, 4]) == 20, '三个 4：合并 4+4=8、8+4=12，WPL = 8+12 = 20，实际 %r' % (huffman_wpl([4, 4, 4]),)",
            "assert huffman_wpl([0, 3, 5, 7]) == 26, '有权值 0 时照样参与合并：0+3=3、3+5=8、7+8=15，WPL = 3+8+15 = 26，实际 %r' % (huffman_wpl([0, 3, 5, 7]),)",
            "assert huffman_wpl([1, 1, 2, 3, 5, 8]) == 45, '含重复值的例子 WPL 是 45，实际 %r' % (huffman_wpl([1, 1, 2, 3, 5, 8]),)",
            "assert huffman_wpl([10, 15, 12, 3, 4, 13, 1, 9]) == 185, '八个权值的例子 WPL 是 185，实际 %r' % (huffman_wpl([10, 15, 12, 3, 4, 13, 1, 9]),)",
            "_w = [8, 3, 5, 7]\nhuffman_wpl(_w)\nassert _w == [8, 3, 5, 7], '题面要求不要修改传入的权重列表，实际 %r' % (_w,)",
            "_w = [3, 1, 2]\nhuffman_wpl(_w)\nassert _w == [3, 1, 2], '权重列表必须保持原样（不能就地排序），实际 %r' % (_w,)",
            "assert huffman_wpl(list(range(1, 101))) == 32298, '1~100 共 100 个权值的 WPL 是 32298，实际 %r' % (huffman_wpl(list(range(1, 101))),)",
            "assert huffman_wpl([3] * 100) == 2016, '100 个相同权值 3 的 WPL 是 2016，实际 %r' % (huffman_wpl([3] * 100),)",
            "assert isinstance(huffman_wpl([8, 3, 5, 7]), int), '返回值必须是整数，实际 %r' % (type(huffman_wpl([8, 3, 5, 7])),)",
            "_many = [(i * 7919) % 1009 + 1 for i in range(400)]\nassert huffman_wpl(_many) == huffman_wpl(sorted(_many)), 'WPL 只与权值集合有关、与输入顺序无关，实际 %r / %r' % (huffman_wpl(_many), huffman_wpl(sorted(_many)))",
        ],
        'explanation': (
            '哈夫曼算法的贪心规则只有一句：**每次取当前最小的两个权值合并**，'
            '合并出来的新结点再放回池子里。权值大的结点因此离根更近，WPL 就最小。\n\n'
            '**WPL 为什么等于「每次合并值之和」？** 合并出的结点权值等于它下面所有叶子权值之和，'
            '而每经过一次合并，这些叶子到根的距离就多 1，'
            '所以「所有合并值相加」恰好等于「每个叶子权值 × 它的深度」之和，也就是 WPL。'
            '这也是考场上最快的算法：**不用画树，只累加合并值**。\n\n'
            '老师给的例子 `[8, 3, 5, 7]` 走一遍：\n\n'
            '1. 取最小的 3、5，合并成 8（池子变成 `{7, 8, 8}`），累加 8；\n'
            '2. 取最小的 7、8，合并成 15（池子 `{8, 15}`），累加 15；\n'
            '3. 取 8、15，合并成 23（池子 `{23}`），累加 23；\n'
            '4. WPL = 8 + 15 + 23 = **46**。\n\n'
            '换个角度核对：最终的哈夫曼树是 `23 = 8 ⊕ 15`、`15 = 7 ⊕ (3 ⊕ 5)`，'
            '所以原来的 8 在深度 1、7 在深度 2、3 和 5 都在深度 3，'
            '于是 8×1 + 7×2 + 3×3 + 5×3 = 8 + 14 + 9 + 15 = **46**，两个口径完全一致。\n\n'
            '**注意**：讲义上这道题若写出 48，是笔误。用上面两种口径核对都得到 46，'
            '而且 46 已经是这组权值的理论最小值（不可能更低），批改与自测都以 46 为准。\n\n'
            '**常见错误**：\n\n'
            '1. 把合并值只当作新结点、忘了累加进 WPL；\n'
            '2. 想找一个「求和乘层数」的公式——没有，WPL 只能按合并过程算；\n'
            '3. 每轮都 `sorted()` 重排（O(n² log n)），数据大时很慢；'
            '正确做法是小根堆 `heapq`，合并 n-1 次，O(n log n)；\n'
            '4. 只弹出最小两个却忘了把合并值放回堆，导致后面少合并、结果偏小。\n\n'
            '复杂度：时间 O(n log n)，额外空间 O(n)。'
        ),
        'expected_output': '46\n33\n0\n0',
        'hints': ['每次从堆里弹出两个最小值，合并后放回堆', 'WPL = 所有合并出来的新权值之和，直接一边合并一边累加'],
    },
    # ── 专题 132 · 823·图（题 17–21）──────────────────────
    {
        'id': 'x823-105',
        'track': 'algorithm',
        'chapter_id': 132,
        'chapter_title': '823·图',
        'topic': '823·图',
        'title': '题17 邻接矩阵存储的 DFS 深度优先遍历',
        'difficulty': 1,
        'tags': ['图', '邻接矩阵', 'DFS', '递归'],
        'statement': (
            '**考点：图的遍历、DFS 序列。**\n\n'
            '无向图用 **n × n 的邻接矩阵** `graph` 表示：\n\n'
            '- `graph[i][j] == 1` 表示顶点 i 与顶点 j 之间有边，`0` 表示没有边；\n'
            '- 无向图的矩阵是**对称**的（`graph[i][j] == graph[j][i]`），题目保证；\n'
            '- 对角线全是 0（没有自环），题目保证；\n'
            '- 顶点编号为 `0 ~ n - 1`，`n = len(graph)`。\n\n'
            '定义函数 `dfs(graph, start)`：返回从顶点 `start` 出发的**深度优先遍历序列**'
            '（访问到的顶点编号组成的列表）。\n\n'
            '访问顺序按统考教材的定义：\n\n'
            '1. 先访问 `start`；\n'
            '2. 然后**按顶点编号从小到大**检查 `start` 的邻居'
            '（也就是从左往右扫矩阵第 `start` 行）；\n'
            '3. 遇到第一个还没访问过的邻居就**立刻深入**下去，把这条路走到底，再回头处理下一个邻居。\n\n'
            '约定：\n\n'
            '- 空图 `[]` 返回 `[]`；`start` 越界（小于 0 或不小于 n）也返回 `[]`；\n'
            '- 从 `start` 出发到不了的顶点**不会**出现在结果里（这是遍历，不是连通分量统计）；\n'
            '- **不要修改**传入的 `graph`；\n'
            '- 用**递归**实现最直观（也可以用显式栈，但要注意「先深入小编号邻居」的顺序）。\n\n'
            '例：6 个顶点、边为 `(0,1) (0,2) (1,3) (2,4) (3,4) (4,5)` 的图，'
            '从 0 出发的 DFS 序列是 `[0, 1, 3, 4, 2, 5]`。\n\n'
            '最后打印这个例子从 0 出发的结果，再打印单顶点图 `[[0]]`、越界 `start = 9`、'
            '空图 `[]` 的结果。'
        ),
        'starter_code': 'def dfs(graph, start):\n    n = len(graph)\n    if n == 0 or start < 0 or start >= n:\n        return []\n    visited = [False] * n\n    order = []\n    # 递归：访问 u，然后按编号从小到大深入没访问过的邻居\n    pass\n',
        'solution': (
            "def dfs(graph, start):\n"
            "    n = len(graph)\n"
            "    if n == 0 or start < 0 or start >= n:\n"
            "        return []\n"
            "    visited = [False] * n\n"
            "    order = []\n"
            "\n"
            "    def walk(u):\n"
            "        visited[u] = True\n"
            "        order.append(u)\n"
            "        for v in range(n):\n"
            "            if graph[u][v] == 1 and not visited[v]:\n"
            "                walk(v)\n"
            "\n"
            "    walk(start)\n"
            "    return order\n"
            "\n"
            "def make(n, edges):\n"
            "    matrix = [[0] * n for _ in range(n)]\n"
            "    for u, v in edges:\n"
            "        matrix[u][v] = 1\n"
            "        matrix[v][u] = 1\n"
            "    return matrix\n"
            "\n"
            "graph = make(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5)])\n"
            "print(dfs(graph, 0))\n"
            "print(dfs([[0]], 0))\n"
            "print(dfs(graph, 9))\n"
            "print(dfs([], 0))\n"
        ),
        'checks': [
            "def _mat(n, edges):\n    matrix = [[0] * n for _ in range(n)]\n    for u, v in edges:\n        matrix[u][v] = 1\n        matrix[v][u] = 1\n    return matrix",
            "assert dfs([], 0) == [], '空图应返回 []'",
            "assert dfs([[0]], 5) == [], 'start 越界应返回 []，实际 %r' % (dfs([[0]], 5),)",
            "assert dfs([[0]], -1) == [], 'start 为负数应返回 []'",
            "assert dfs([[0]], 0) == [0], '只有一个孤立顶点时应返回 [0]，实际 %r' % (dfs([[0]], 0),)",
            "_g = _mat(2, [(0, 1)])\nassert dfs(_g, 0) == [0, 1] and dfs(_g, 1) == [1, 0], '两个顶点一条边：从 0 出发 [0, 1]、从 1 出发 [1, 0]，实际 %r / %r' % (dfs(_g, 0), dfs(_g, 1))",
            "_g = _mat(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5)])\nassert dfs(_g, 0) == [0, 1, 3, 4, 2, 5], '题面例子从 0 出发应是 [0, 1, 3, 4, 2, 5]，实际 %r' % (dfs(_g, 0),)",
            "_g = _mat(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5)])\nassert dfs(_g, 1) == [1, 0, 2, 4, 3, 5], '从 1 出发应是 [1, 0, 2, 4, 3, 5]（每次都要走编号最小的未访问邻居），实际 %r' % (dfs(_g, 1),)",
            "_g = _mat(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5)])\nassert dfs(_g, 2) == [2, 0, 1, 3, 4, 5], '从 2 出发应是 [2, 0, 1, 3, 4, 5]，实际 %r' % (dfs(_g, 2),)",
            "_g = _mat(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5)])\nassert dfs(_g, 5) == [5, 4, 2, 0, 1, 3], '从 5 出发应是 [5, 4, 2, 0, 1, 3]，实际 %r' % (dfs(_g, 5),)",
            "_g = _mat(6, [(0, 1), (1, 2), (3, 4)])\nassert dfs(_g, 0) == [0, 1, 2], '不连通时只输出起点所在的分量，实际 %r' % (dfs(_g, 0),)",
            "_g = _mat(6, [(0, 1), (1, 2), (3, 4)])\nassert dfs(_g, 5) == [5], '孤立顶点自己一个人就是一条序列，实际 %r' % (dfs(_g, 5),)",
            "_g = _mat(4, [(0, 1), (0, 2), (0, 3)])\nassert dfs(_g, 0) == [0, 1, 2, 3], '星形图从中心出发应按编号顺序走到每个叶子，实际 %r' % (dfs(_g, 0),)",
            "_n = 5\n_g = [[1] * _n for _ in range(_n)]\nfor _i in range(_n):\n    _g[_i][_i] = 0\nassert dfs(_g, 0) == [0, 1, 2, 3, 4], '完全图（对角线是 0）从 0 出发应是 [0, 1, 2, 3, 4]，实际 %r' % (dfs(_g, 0),)",
            "_n = 200\n_g = [[0] * _n for _ in range(_n)]\nfor _i in range(_n - 1):\n    _g[_i][_i + 1] = 1\n    _g[_i + 1][_i] = 1\nassert dfs(_g, 0) == list(range(_n)), '200 个顶点的链应从 0 一直走到 199，实际长度 %r' % (len(dfs(_g, 0)),)",
            "_g = _mat(4, [(0, 1), (0, 2), (1, 3)])\n_snapshot = [row[:] for row in _g]\ndfs(_g, 0)\nassert _g == _snapshot, '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_g = _mat(7, [(0, 3), (3, 5), (5, 6), (1, 2), (2, 4)])\n_r = dfs(_g, 0)\nassert _r[0] == 0 and sorted(_r) == sorted([0, 3, 5, 6]), '不连通图从 0 出发只应访问 {0, 3, 5, 6} 这一片，实际 %r' % (_r,)",
        ],
        'explanation': (
            'DFS 的定义就是递归：**访问 u，然后按顺序对每个未访问的邻居深入**。\n\n'
            '```python\n'
            'def walk(u):\n'
            '    visited[u] = True\n'
            '    order.append(u)\n'
            '    for v in range(n):            # 邻接矩阵：按编号从小到大扫一行\n'
            '        if graph[u][v] == 1 and not visited[v]:\n'
            '            walk(v)\n'
            '```\n\n'
            '`visited` 必须有：无向图里 u 的邻居一定包含「我刚从哪来」，'
            '没有访问标记就会来回震荡、递归爆栈。\n\n'
            '**矩阵与邻接表的差别**：矩阵存图时「找邻居」要扫一整行 O(n)，'
            '所以邻接矩阵版 DFS 的总时间是 O(n²)；邻接表是 O(n + e)。'
            '这也是「稠密图用矩阵、稀疏图用邻接表」的原因。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记标记起点，或标记写在 `for` 之后；\n'
            '2. 空图和越界 `start` 没拦截（`graph[start]` 直接 IndexError / 负下标取到倒数第一行）；\n'
            '3. 一次性把所有邻居入栈的迭代写法：弹出顺序会和「编号从小到大深入」相反；\n'
            '4. 把「不连通时只输出一个分量」办成了「输出所有顶点」——要跑完一个分量就停。\n\n'
            '复杂度：时间 O(n²)（每个顶点扫一行）、额外空间 O(n)。'
        ),
        'expected_output': '[0, 1, 3, 4, 2, 5]\n[0]\n[]\n[]',
        'hints': ['矩阵的一行就是邻居集合，按列号从小到大扫', 'visited 在进入结点时就置 True，再递归深入未访问的邻居'],
    },
    {
        'id': 'x823-106',
        'track': 'algorithm',
        'chapter_id': 132,
        'chapter_title': '823·图',
        'topic': '823·图',
        'title': '题18 邻接表存储的 BFS 广度优先遍历',
        'difficulty': 1,
        'tags': ['图', '邻接表', 'BFS', '队列'],
        'statement': (
            '**考点：BFS 遍历、队列实现。**\n\n'
            '无向图用**邻接表**表示：`graph` 是一个**字典**，'
            '键是顶点编号（整数，可以**不连续**），值是它的邻居编号列表。\n\n'
            '- 无向图的两端互相登记：`v` 在 `graph[u]` 里，就有 `u` 在 `graph[v]` 里'
            '（题目保证，同一个邻居不会重复列出）；\n'
            '- 顶点只出现在键里：某个顶点如果没有邻居，它的值是空列表 `[]`。\n\n'
            '定义函数 `bfs(graph, start)`：返回从顶点 `start` 出发的**广度优先遍历序列**'
            '（访问到的顶点编号组成的列表）。\n\n'
            '访问规则：\n\n'
            '1. 先访问 `start`；\n'
            '2. 用**队列**：出队一个顶点时，把它**按邻居列表给出的顺序**、'
            '还没访问过的邻居依次入队；\n'
            '3. 队列空时结束。\n\n'
            '约定：\n\n'
            '- 空字典 `{}` 返回 `[]`；`start` 不是字典的键（顶点不存在）也返回 `[]`；\n'
            '- 到不了的顶点不出现在结果里；\n'
            '- **不要修改**传入的 `graph`；\n'
            '- 用列表当队列（队头 `pop(0)`）或 `collections.deque` 都行，不要用递归。\n\n'
            '例：`{0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}` '
            '从 0 出发是 `[0, 1, 2, 3, 4]`，从 5 出发是 `[5]`。\n\n'
            '最后打印这个例子从 0 与从 3 出发的结果，再打印空字典、'
            '以及 `start = 9`（图中没有的顶点）的结果。'
        ),
        'starter_code': 'def bfs(graph, start):\n    if start not in graph:\n        return []\n    visited = {start}\n    queue = [start]\n    order = []\n    # 出队一个就把它的邻居按顺序检查并入队\n    pass\n',
        'solution': (
            "def bfs(graph, start):\n"
            "    if start not in graph:\n"
            "        return []\n"
            "    visited = {start}\n"
            "    queue = [start]\n"
            "    order = []\n"
            "    while queue:\n"
            "        u = queue.pop(0)\n"
            "        order.append(u)\n"
            "        for v in graph[u]:\n"
            "            if v not in visited:\n"
            "                visited.add(v)\n"
            "                queue.append(v)\n"
            "    return order\n"
            "\n"
            "graph = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}\n"
            "print(bfs(graph, 0))\n"
            "print(bfs(graph, 3))\n"
            "print(bfs({}, 0))\n"
            "print(bfs(graph, 9))\n"
        ),
        'checks': [
            "assert bfs({}, 0) == [], '空字典应返回 []'",
            "assert bfs({0: []}, 9) == [], 'start 不是字典里的顶点应返回 []，实际 %r' % (bfs({0: []}, 9),)",
            "assert bfs({0: []}, 0) == [0], '只有一个孤立顶点时应返回 [0]，实际 %r' % (bfs({0: []}, 0),)",
            "_g = {0: [1], 1: [0]}\nassert bfs(_g, 0) == [0, 1] and bfs(_g, 1) == [1, 0], '一条边：从两端出发分别是 [0, 1] 与 [1, 0]，实际 %r / %r' % (bfs(_g, 0), bfs(_g, 1))",
            "_g = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}\nassert bfs(_g, 0) == [0, 1, 2, 3, 4], '题面例子从 0 出发应是 [0, 1, 2, 3, 4]，实际 %r' % (bfs(_g, 0),)",
            "_g = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}\nassert bfs(_g, 3) == [3, 1, 0, 2, 4], '从 3 出发应是 [3, 1, 0, 2, 4]，实际 %r' % (bfs(_g, 3),)",
            "_g = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}\nassert bfs(_g, 5) == [5], '孤立顶点 5 只有自己，实际 %r' % (bfs(_g, 5),)",
            "_g = {0: [1, 2], 1: [0], 2: [0], 10: [11], 11: [10]}\nassert bfs(_g, 0) == [0, 1, 2], '编号不连续 + 不连通：只输出 0 所在的分量，实际 %r' % (bfs(_g, 0),)",
            "_g = {0: [1, 2], 1: [0], 2: [0], 10: [11], 11: [10]}\nassert bfs(_g, 10) == [10, 11], '从 10 出发应是 [10, 11]，实际 %r' % (bfs(_g, 10),)",
            "_g = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3]}\nassert bfs(_g, 0) == [0, 1, 2, 3, 4], '一条链要从头走到尾，实际 %r' % (bfs(_g, 0),)",
            "_g = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}\nassert bfs(_g, 0) == [0, 1, 2, 3], '星形图按邻居列表顺序访问叶子，实际 %r' % (bfs(_g, 0),)",
            "_g = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}\nassert bfs(_g, 0) == [0] + _g[0], '第一层叶子必须按 graph[0] 里给出的顺序访问（不是排序后的顺序），实际 %r' % (bfs(_g, 0),)",
            "_g = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}\n_r = bfs(_g, 0)\nassert len(_r) == len(set(_r)), '同一个顶点不能重复访问，实际 %r' % (_r,)",
            "_n = 400\n_g = {}\nfor _i in range(_n):\n    _nbrs = []\n    if _i > 0:\n        _nbrs.append(_i - 1)\n    if _i < _n - 1:\n        _nbrs.append(_i + 1)\n    _g[_i] = _nbrs\nassert bfs(_g, 0) == list(range(_n)), '400 个顶点的链应从 0 一直到 399，实际长度 %r' % (len(bfs(_g, 0)),)",
            "_g = {0: [1, 2], 1: [0, 3], 2: [0, 4], 3: [1], 4: [2], 5: []}\n_snapshot = {k: list(v) for k, v in _g.items()}\nbfs(_g, 0)\nassert _g == _snapshot, '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_g = {0: [1, 2, 3, 4], 1: [0, 2], 2: [0, 1, 3], 3: [0, 2, 4], 4: [0, 3]}\n_r = bfs(_g, 0)\nassert _r[0] == 0 and _r[1:3] == [1, 2] and sorted(_r) == [0, 1, 2, 3, 4], '有环的图也要按层访问：第 1 层是邻居列表前两个，实际 %r' % (_r,)",
        ],
        'explanation': (
            'BFS 只有两个零件：**队列**和 **visited**。\n\n'
            '```python\n'
            'queue = [start]\n'
            'visited = {start}\n'
            'while queue:\n'
            '    u = queue.pop(0)          # 出队即访问\n'
            '    order.append(u)\n'
            '    for v in graph[u]:        # 按邻居列表给出的顺序\n'
            '        if v not in visited:\n'
            '            visited.add(v)    # 入队时就标记，避免同一个顶点被排两次\n'
            '            queue.append(v)\n'
            '```\n\n'
            '**为什么入队时就要标记？** 若等到出队才标记，同一个顶点可能被它的多个邻居'
            '重复入队，序列里会出现重复顶点。\n\n'
            '**BFS 的性质**（考试常考）：在无权图里，BFS 首次访问一个顶点时走过的边数，'
            '就是它到起点的**最少边数**——这也是「BFS 求单源最短路径（边数）」的原理。'
            '另外 BFS 序列天然按「层」排列：起点一层、它的邻居一层、再外一层……\n\n'
            '**常见错误**：\n\n'
            '1. 用 `visited` 记错对象（把顶点编号和下标混用，字典版要按**键**判断）；\n'
            '2. `start` 不在字典里却直接 `graph[start]`，KeyError；\n'
            '3. 出队时忘了标记已访问，或标记了却不入队；\n'
            '4. 用 `list.pop()`（默认弹队尾）当出队——那就变成栈了，'
            '序列会退化成 DFS 的样子。\n\n'
            '复杂度：时间 O(n + e)（每个顶点入队一次、每条边检查两次），额外空间 O(n)。'
        ),
        'expected_output': '[0, 1, 2, 3, 4]\n[3, 1, 0, 2, 4]\n[]\n[]',
        'hints': ['出队一个顶点，把它还没访问过的邻居按顺序入队', '入队时就打标记，防止同一个顶点被重复入队'],
    },
    {
        'id': 'x823-107',
        'track': 'algorithm',
        'chapter_id': 132,
        'chapter_title': '823·图',
        'topic': '823·图',
        'title': '题19 Prim 算法求最小生成树的总权值',
        'difficulty': 2,
        'tags': ['图', '最小生成树', 'Prim', '贪心'],
        'statement': (
            '**考点：最小生成树、Prim 算法（823 计算大题）。**\n\n'
            '无向带权图用 **n × n 的邻接矩阵** `graph` 表示：\n\n'
            '- `graph[i][j]` 是正整数，表示顶点 i 到顶点 j 的边的**权值**；\n'
            '- `float("inf")` 表示 i、j 之间**没有边**；\n'
            '- 对角线 `graph[i][i] == 0`，矩阵**对称**（题目保证）；\n'
            '- 顶点编号 `0 ~ n - 1`。\n\n'
            '定义函数 `prim(graph)`：返回**最小生成树的总权值**（整数）。\n\n'
            '约定：\n\n'
            '- 空矩阵 `[]` 返回 `0`；只有一个顶点（`[[0]]`）返回 `0`（没有边要选）；\n'
            '- **图不连通时不存在生成树，返回 `None`**；\n'
            '- **不要修改**传入的 `graph`。\n\n'
            'Prim 算法（朴素版，O(n²)，不用堆）：\n\n'
            '1. 从顶点 0 开始，维护「已经在生成树里的集合」；\n'
            '2. 用数组 `dist[v]` 记录顶点 v 到**已选集合**的最小边权'
            '（一开始 `dist[0] = 0`，其余是 inf）；\n'
            '3. 每轮在**未选**的顶点里挑 `dist` 最小的那个 u（若它的 dist 还是 inf，'
            '说明图不连通，返回 `None`），把它加入集合，总权值加上 `dist[u]`；\n'
            '4. 用 u 的邻接行更新其他未选顶点的 `dist`（`dist[v] = min(dist[v], graph[u][v])`）；\n'
            '5. 重复 n 轮。\n\n'
            '例：6 个顶点、边为 `(0,1,6) (0,2,1) (0,3,5) (1,2,5) (1,4,3) (2,3,5) '
            '(2,4,6) (2,5,4) (3,5,2) (4,5,6)` 的图，最小生成树总权值是 **15**\n\n'
            '（选出来的边可以是 `(0,2,1) (2,5,4) (5,3,2) (2,1,5) (1,4,3)`，1+4+2+5+3 = 15）。\n\n'
            '最后打印这个例子的结果，再打印空矩阵、单顶点矩阵、'
            '以及一个不连通图（返回 `None`）的结果。'
        ),
        'starter_code': 'def prim(graph):\n    n = len(graph)\n    if n == 0:\n        return 0\n    used = [False] * n\n    dist = [float(\'inf\')] * n\n    dist[0] = 0\n    total = 0\n    # 每轮选一个 dist 最小的未选顶点，加入集合，并用它更新别人的 dist\n    pass\n',
        'solution': (
            "def prim(graph):\n"
            "    n = len(graph)\n"
            "    if n == 0:\n"
            "        return 0\n"
            "    inf = float('inf')\n"
            "    used = [False] * n\n"
            "    dist = [inf] * n\n"
            "    dist[0] = 0\n"
            "    total = 0\n"
            "    for _ in range(n):\n"
            "        u = -1\n"
            "        for v in range(n):\n"
            "            if not used[v] and (u == -1 or dist[v] < dist[u]):\n"
            "                u = v\n"
            "        if dist[u] == inf:\n"
            "            return None\n"
            "        used[u] = True\n"
            "        total += dist[u]\n"
            "        for v in range(n):\n"
            "            if not used[v] and graph[u][v] < dist[v]:\n"
            "                dist[v] = graph[u][v]\n"
            "    return total\n"
            "\n"
            "def make(n, edges):\n"
            "    inf = float('inf')\n"
            "    matrix = [[inf] * n for _ in range(n)]\n"
            "    for i in range(n):\n"
            "        matrix[i][i] = 0\n"
            "    for u, v, w in edges:\n"
            "        matrix[u][v] = w\n"
            "        matrix[v][u] = w\n"
            "    return matrix\n"
            "\n"
            "example = make(6, [(0, 1, 6), (0, 2, 1), (0, 3, 5), (1, 2, 5), (1, 4, 3),\n"
            "                   (2, 3, 5), (2, 4, 6), (2, 5, 4), (3, 5, 2), (4, 5, 6)])\n"
            "print(prim(example))\n"
            "print(prim([]))\n"
            "print(prim([[0]]))\n"
            "print(prim(make(4, [(0, 1, 1), (2, 3, 2)])))\n"
        ),
        'checks': [
            "def _mat(n, edges):\n    inf = float('inf')\n    matrix = [[inf] * n for _ in range(n)]\n    for i in range(n):\n        matrix[i][i] = 0\n    for u, v, w in edges:\n        matrix[u][v] = w\n        matrix[v][u] = w\n    return matrix",
            "assert prim([]) == 0, '空矩阵返回 0，实际 %r' % (prim([]),)",
            "assert prim([[0]]) == 0, '只有一个顶点时没有边要选，返回 0，实际 %r' % (prim([[0]]),)",
            "_g = _mat(2, [(0, 1, 7)])\nassert prim(_g) == 7, '两个顶点一条边：总权值就是这条边的权 7，实际 %r' % (prim(_g),)",
            "_g = _mat(6, [(0, 1, 6), (0, 2, 1), (0, 3, 5), (1, 2, 5), (1, 4, 3), (2, 3, 5), (2, 4, 6), (2, 5, 4), (3, 5, 2), (4, 5, 6)])\nassert prim(_g) == 15, '题面那个 6 顶点图的最小生成树总权值是 15，实际 %r' % (prim(_g),)",
            "_g = _mat(5, [(0, 1, 3), (0, 2, 8), (1, 2, 4), (1, 3, 7), (2, 3, 2), (3, 4, 9), (2, 4, 5)])\nassert prim(_g) == 14, '另一组 5 顶点图的 MST 总权值是 14（2 + 4 + 3 + 5），实际 %r' % (prim(_g),)",
            "_g = _mat(4, [(0, 1, 5), (1, 2, 5), (2, 3, 5)])\nassert prim(_g) == 15, '四个顶点连成一条权 5 的链，MST 就是 15，实际 %r' % (prim(_g),)",
            "_g = _mat(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 1), (0, 2, 1), (1, 3, 1)])\nassert prim(_g) == 3, '四个顶点的完全图（每条边权都是 1）：选 3 条边，总权值 3，实际 %r' % (prim(_g),)",
            "_g = _mat(5, [(0, 4, 1), (0, 1, 9), (1, 2, 9), (2, 3, 9), (3, 4, 9), (1, 3, 2)])\nassert prim(_g) == 21, '要选到便宜的边（1 + 2 + 9 + 9 = 21），不能只挑最前面几条，实际 %r' % (prim(_g),)",
            "_g = _mat(4, [(0, 1, 1), (2, 3, 2)])\nassert prim(_g) is None, '不连通图不存在生成树，应返回 None，实际 %r' % (prim(_g),)",
            "_g = _mat(5, [(0, 1, 4)])\nassert prim(_g) is None, '只有一条边、其余顶点是孤立的，同样应返回 None，实际 %r' % (prim(_g),)",
            "_g = _mat(3, [(0, 1, 2), (1, 2, 3)])\nassert prim(_g) == 5, '三个顶点一条链：2 + 3 = 5，实际 %r' % (prim(_g),)",
            "_g = _mat(6, [(0, 1, 6), (0, 2, 1), (0, 3, 5), (1, 2, 5), (1, 4, 3), (2, 3, 5), (2, 4, 6), (2, 5, 4), (3, 5, 2), (4, 5, 6)])\n_snapshot = [row[:] for row in _g]\nprim(_g)\nassert _g == _snapshot, '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_n = 60\n_edges = [(i, i + 1, (i * 11) % 9 + 1) for i in range(_n - 1)]\n_edges += [((i * 17) % _n, (i * 13 + 7) % _n, (i * 5) % 12 + 1) for i in range(_n)]\n_edges = [(u, v, w) for u, v, w in _edges if u != v]\n_g = _mat(_n, _edges)\n_pairs = {}\nfor _u in range(_n):\n    for _v in range(_u + 1, _n):\n        if _g[_u][_v] != float('inf'):\n            _pairs[(_u, _v)] = _g[_u][_v]\ndef _kruskal(n, edges):\n    parent = list(range(n))\n    def find(x):\n        while parent[x] != x:\n            parent[x] = parent[parent[x]]\n            x = parent[x]\n        return x\n    total = 0\n    count = 0\n    for u, v, w in sorted(edges, key=lambda e: e[2]):\n        if find(u) != find(v):\n            parent[find(u)] = find(v)\n            total += w\n            count += 1\n    return total if count == n - 1 else None\n_expected = _kruskal(_n, [(u, v, w) for (u, v), w in _pairs.items()])\nassert prim(_g) == _expected, '60 个顶点的随机图与 Kruskal 的结果应一致（期望 %r，实际 %r）' % (_expected, prim(_g))",
            "_n = 7\n_g = _mat(_n, [(0, 1, 2), (1, 2, 3), (2, 3, 1), (3, 4, 4), (4, 5, 2), (5, 6, 3), (0, 6, 9), (1, 4, 8)])\nassert prim(_g) == 15, '7 个顶点的例子 MST 总权值是 15（2+3+1+4+2+3），实际 %r' % (prim(_g),)",
        ],
        'explanation': (
            'Prim 的思路是「**从一个根开始，不断把最近的点拉进来**」：\n\n'
            '- 用 `used[v]` 表示 v 是否已经进树；\n'
            '- `dist[v]` 表示 v 到「已进树的点集」的最短一条边的权值；\n'
            '- 每轮挑 `dist` 最小的未选点加入（贪心），并把它新贡献的边拿去更新别人的 `dist`。\n\n'
            '```python\n'
            'for _ in range(n):\n'
            '    u = 未选中 dist 最小的顶点\n'
            '    if dist[u] == inf: return None      # 剩下的点都够不到，图不连通\n'
            '    used[u] = True; total += dist[u]\n'
            '    for v in range(n):\n'
            '        if not used[v] and graph[u][v] < dist[v]:\n'
            '            dist[v] = graph[u][v]\n'
            '```\n\n'
            '**为什么贪心是对的？** 已选集合要连到集合外，任何生成树都必须用至少一条跨越'
            '「集合 / 集合外」的边；选其中最便宜的那条，一定存在一棵最优树包含它'
            '（这就是 MST 的割性质）。\n\n'
            '**注意 `dist[0] = 0`**：第一个顶点不需要边就能进树，所以总权值加上的是 0；'
            '如果把它写成 inf 或写成「随便挑一条边」，结果就多算了。\n\n'
            '**常见错误**：\n\n'
            '1. 挑最小点时忘记跳过 `used` 的点，把同一个顶点选两次；\n'
            '2. 不连通图没判（`dist[u] == inf` 时直接加 inf，结果变成 inf 或崩溃），'
            '本题要求返回 `None`；\n'
            '3. 更新 `dist` 时写成 `dist[v] = graph[u][v]`（丢掉了 min），'
            '会把之前更短的边覆盖掉；\n'
            '4. 把「无边」的 `inf` 当权值参与加法。\n\n'
            '复杂度：朴素版两重循环 O(n²)，跟边数无关，适合稠密图；'
            '稀疏图用「堆 + 邻接表」的 Kruskal / 堆优化 Prim 更好。'
        ),
        'expected_output': '15\n0\n0\nNone',
        'hints': ['dist[v] 记录 v 到「已选集合」的最短边，起点 dist 设 0', '每轮挑未选中 dist 最小的点；若它是 inf 说明图不连通，返回 None'],
    },
    {
        'id': 'x823-108',
        'track': 'algorithm',
        'chapter_id': 132,
        'chapter_title': '823·图',
        'topic': '823·图',
        'title': '题20 拓扑排序（AOV 网，判断有没有环）',
        'difficulty': 2,
        'tags': ['图', '拓扑排序', '有向无环图', '入度'],
        'statement': (
            '**考点：有向无环图（AOV 网）的拓扑排序、判断有环（823 大题高频）。**\n\n'
            '有向图用**邻接表 + 入度数组**给出：\n\n'
            '- `graph` 是**列表**：`graph[u]` 是顶点 u 的**出边**邻居列表，'
            '顶点编号 `0 ~ n - 1`，`n = len(graph)`；允许平行边（同一个邻居出现多次）；\n'
            '- `indegree` 是长度 n 的列表：`indegree[v]` 就是顶点 v 的入度，'
            '与 `graph` 完全一致（题目保证，不需要自己重算）。\n\n'
            '定义函数 `topo_sort(graph, indegree)`：\n\n'
            '- 图**没有环**时，返回一个**拓扑序列**（长度 n 的列表）；\n'
            '- 图**有环**时（存在环、包括自环），返回**空列表 `[]`**；\n'
            '- 空图 `[]` 返回 `[]`；\n'
            '- **不要修改**传入的 `graph` 和 `indegree`（入度数组要自己拷一份再减）。\n\n'
            '为了让答案唯一，约定：**每次从当前入度为 0 的顶点里取编号最小的那个**'
            '（可以用 `heapq` 实现最小堆，也可以每轮扫一遍找最小值）。\n\n'
            'Kahn 算法：\n\n'
            '1. 把所有入度为 0 的顶点放进「候选集合」；\n'
            '2. 每次取出编号最小的一个，接到序列末尾；\n'
            '3. 把它所有出边的终点入度减 1，减到 0 的顶点进候选集合；\n'
            '4. 候选集合空了以后，若序列长度**小于 n**，说明剩下的顶点互相纠缠成了环，'
            '返回 `[]`。\n\n'
            '例：`graph = [[1, 2], [3], [3], [4], [5], []]`、'
            '`indegree = [0, 1, 1, 2, 1, 1]`，拓扑序列是 `[0, 1, 2, 3, 4, 5]`。\n\n'
            '最后打印这个例子的结果，再打印单顶点图 `[[]]`、'
            '一个有环的图（返回 `[]`）、以及空图 `[]` 的结果。'
        ),
        'starter_code': 'import heapq\n\ndef topo_sort(graph, indegree):\n    n = len(graph)\n    if n == 0:\n        return []\n    remaining = list(indegree)\n    heap = [u for u in range(n) if remaining[u] == 0]\n    heapq.heapify(heap)\n    order = []\n    # 取最小编号、出队、给邻居减入度\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def topo_sort(graph, indegree):\n"
            "    n = len(graph)\n"
            "    if n == 0:\n"
            "        return []\n"
            "    remaining = list(indegree)\n"
            "    heap = [u for u in range(n) if remaining[u] == 0]\n"
            "    heapq.heapify(heap)\n"
            "    order = []\n"
            "    while heap:\n"
            "        u = heapq.heappop(heap)\n"
            "        order.append(u)\n"
            "        for v in graph[u]:\n"
            "            remaining[v] -= 1\n"
            "            if remaining[v] == 0:\n"
            "                heapq.heappush(heap, v)\n"
            "    if len(order) != n:\n"
            "        return []\n"
            "    return order\n"
            "\n"
            "print(topo_sort([[1, 2], [3], [3], [4], [5], []], [0, 1, 1, 2, 1, 1]))\n"
            "print(topo_sort([[]], [0]))\n"
            "print(topo_sort([[1], [2], [0]], [1, 1, 1]))\n"
            "print(topo_sort([], []))\n"
        ),
        'checks': [
            "def _build(n, edges):\n    graph = [[] for _ in range(n)]\n    indegree = [0] * n\n    for u, v in edges:\n        graph[u].append(v)\n        indegree[v] += 1\n    return graph, indegree",
            "assert topo_sort([], []) == [], '空图应返回 []'",
            "assert topo_sort([[]], [0]) == [0], '只有一个孤立顶点时序列就是 [0]，实际 %r' % (topo_sort([[]], [0]),)",
            "_g, _d = _build(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)])\nassert topo_sort(_g, _d) == [0, 1, 2, 3, 4, 5], '题面例子的拓扑序列应是 [0, 1, 2, 3, 4, 5]，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(4, [(0, 1), (0, 2), (1, 3), (2, 3)])\nassert topo_sort(_g, _d) == [0, 1, 2, 3], '菱形图（0 指 1、2，二者都指 3）应按编号取小：应是 [0, 1, 2, 3]，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(3, [(2, 0), (2, 1)])\nassert topo_sort(_g, _d) == [2, 0, 1], '起点不是 0 时也要按编号取小：应是 [2, 0, 1]，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(4, [(0, 1), (2, 3)])\nassert topo_sort(_g, _d) == [0, 1, 2, 3], '两个不连通的分量按编号顺序穿插：应是 [0, 1, 2, 3]，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(3, [(0, 1), (1, 2), (2, 0)])\nassert topo_sort(_g, _d) == [], '三元环有环，应返回 []，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(2, [(0, 1), (1, 0)])\nassert topo_sort(_g, _d) == [], '两个顶点互相指也是有环，应返回 []，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(2, [(0, 0)])\nassert topo_sort(_g, _d) == [], '自环会让自己永远进不了候选集合，应返回 []，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(4, [(0, 1), (1, 2), (2, 3), (3, 1)])\nassert topo_sort(_g, _d) == [], '0 能出去、后面的 1-2-3 成环：应返回 []（不能只输出 [0]），实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(4, [(0, 1), (0, 2), (1, 2)])\n_r = topo_sort(_g, _d)\nassert len(_r) == 4 and all(_r.index(u) < _r.index(v) for u, v in [(0, 1), (0, 2), (1, 2)]), '每条边必须由前指向后，实际 %r' % (_r,)",
            "_g = [[1, 1], [], []]\nassert topo_sort(_g, [0, 2, 0]) == [0, 1, 2], '平行边（0 连出两条到 1）要在循环里各减一次入度，实际 %r' % (topo_sort(_g, [0, 2, 0]),)",
            "_g, _d = _build(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])\nassert topo_sort(_g, _d) == [], '五元环也要判出来，实际 %r' % (topo_sort(_g, _d),)",
            "_g, _d = _build(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)])\n_g_snap = [list(x) for x in _g]\n_d_snap = list(_d)\ntopo_sort(_g, _d)\nassert _g == _g_snap and _d == _d_snap, '题面要求不要修改 graph 与 indegree（入度要自己拷贝），实际 %r / %r' % (_g, _d)",
            "_n = 300\n_edges = [(i, i + 1) for i in range(_n - 1)]\n_edges += [(i, i + 3) for i in range(_n - 3)]\n_g, _d = _build(_n, _edges)\n_r = topo_sort(_g, _d)\nassert _r == list(range(_n)), '300 个顶点的链式 DAG（还有 +3 的跳边）序列应是 0 到 299，实际前 5 位 %r' % (_r[:5],)",
            "_n = 200\n_edges = [(i, i + 1) for i in range(_n - 1)] + [(_n - 1, 0)]\n_g, _d = _build(_n, _edges)\nassert topo_sort(_g, _d) == [], '200 个顶点的环也要判出来'",
        ],
        'explanation': (
            'Kahn 算法把「拓扑排序」翻译成了「不断摘掉入度为 0 的点」：\n\n'
            '```python\n'
            'remaining = list(indegree)                  # 拷一份，别改题面给的数组\n'
            'heap = [u for u in range(n) if remaining[u] == 0]   # 用最小堆保证取编号最小的\n'
            'while heap:\n'
            '    u = heapq.heappop(heap)\n'
            '    order.append(u)\n'
            '    for v in graph[u]:                      # 摘掉 u 会「放松」它的所有出边\n'
            '        remaining[v] -= 1\n'
            '        if remaining[v] == 0:\n'
            '            heapq.heappush(heap, v)\n'
            'if len(order) != n:\n'
            '    return []                               # 还有剩，说明剩下的点互相成环\n'
            '```\n\n'
            '**为什么「序列长度小于 n」等价于「有环」？** 有向图里只要还有环，环上的点入度都至少是 1'
            '（环给每个点留了一条入边），永远进不了候选集合。反过来，无环图的每个点最终都会被摘掉。\n\n'
            '**拓扑序列一般不唯一**：本题用「取编号最小的入度 0 顶点」这条约定把它钉死成唯一答案；'
            '换成栈（后进先出）会得到另一个合法序列（比如菱形图会输出 `[0, 2, 1, 3]`），'
            '它同样是正确的拓扑序——所以判题时才特意规定了取最小的规则。\n\n'
            '**常见错误**：\n\n'
            '1. 直接改题面给的 `indegree`（本题断言会查这个）；\n'
            '2. 忘了判环出口：候选集合空了就返回序列，长度不足时也照返回；\n'
            '3. 平行边只减一次入度（应该按 `graph[u]` 里出现几次减几次）；\n'
            '4. 让「已经进过队」的点再次入队（入度减到 0 只会发生一次，注意减到 0 才 push）。\n\n'
            '复杂度：时间 O(n + e + n log n)（堆操作），空间 O(n)。'
        ),
        'expected_output': '[0, 1, 2, 3, 4, 5]\n[0]\n[]\n[]',
        'hints': ['先把入度为 0 的点放进候选集合，每轮取编号最小的那个', '摘掉一个点就给它所有出边的终点减入度；最后序列长度不足 n 就是有环'],
    },
    {
        'id': 'x823-109',
        'track': 'algorithm',
        'chapter_id': 132,
        'chapter_title': '823·图',
        'topic': '823·图',
        'title': '题21 Dijkstra 单源最短路径（邻接矩阵）',
        'difficulty': 2,
        'tags': ['图', '最短路径', 'Dijkstra', '贪心'],
        'statement': (
            '**考点：最短路径、Dijkstra 算法（823 计算大题）。**\n\n'
            '带权**有向**图用 **n × n 的邻接矩阵** `graph` 表示：\n\n'
            '- `graph[i][j]` 是正整数，表示**从 i 指向 j** 的边的权值（单向！）；\n'
            '- `float("inf")` 表示 i 到 j 没有边；\n'
            '- 对角线 `graph[i][i] == 0`；矩阵**不一定对称**；\n'
            '- 题目保证**没有负权边**；顶点编号 `0 ~ n - 1`。\n\n'
            '定义函数 `dijkstra(graph, start)`：返回一个长度 n 的**距离数组**，'
            '`dist[v]` 是 `start` 到顶点 v 的**最短距离**；到不了的顶点写 `float("inf")`。\n\n'
            '约定：\n\n'
            '- 空矩阵 `[]` 返回 `[]`；`start` 越界（小于 0 或不小于 n）返回 `[]`；\n'
            '- 单顶点图 `[[0]]`、`start = 0` 返回 `[0]`；\n'
            '- **不要修改**传入的 `graph`；\n'
            '- 要求写**朴素版 O(n²)**（每轮线性扫描找未确定点里 dist 最小的，不用堆）。\n\n'
            '算法步骤：\n\n'
            '1. `dist = list(graph[start])`（起点那一行就是「只走一条边」的初始距离），'
            '`done` 数组全为 False；\n'
            '2. 重复 n 次：在**还没确定**的顶点里挑 `dist` 最小的 u；\n'
            '   若这个最小值是 `inf`，说明剩下的都到不了，可以提前结束；\n'
            '3. 把 u 标记为已确定，然后用 u 做「松弛」：'
            '若 `dist[u] + graph[u][v] < dist[v]`，就更新 `dist[v]`。\n\n'
            '例：6 个顶点的有向图（边为 `0→1(10) 0→4(5) 1→2(1) 1→4(2) 2→3(4) '
            '3→0(7) 3→2(6) 4→1(3) 4→2(9) 4→3(2)`），从 0 出发的最短距离数组是\n\n'
            '`[0, 8, 9, 7, 5, inf]`——到顶点 1 最省的路是 `0→4→1`（5 + 3 = 8），'
            '比直达的 10 更短；顶点 5 没有入边，到不了。\n\n'
            '最后打印这个例子从 0 出发的结果，再打印空矩阵、越界 `start = 9`、'
            '单顶点矩阵的结果。'
        ),
        'starter_code': 'def dijkstra(graph, start):\n    n = len(graph)\n    if n == 0 or start < 0 or start >= n:\n        return []\n    inf = float(\'inf\')\n    dist = list(graph[start])\n    done = [False] * n\n    # 每轮挑未确定的 dist 最小点，标记后松弛它的出边\n    pass\n',
        'solution': (
            "def dijkstra(graph, start):\n"
            "    n = len(graph)\n"
            "    if n == 0 or start < 0 or start >= n:\n"
            "        return []\n"
            "    inf = float('inf')\n"
            "    dist = list(graph[start])\n"
            "    done = [False] * n\n"
            "    for _ in range(n):\n"
            "        u = -1\n"
            "        for v in range(n):\n"
            "            if not done[v] and (u == -1 or dist[v] < dist[u]):\n"
            "                u = v\n"
            "        if dist[u] == inf:\n"
            "            break\n"
            "        done[u] = True\n"
            "        for v in range(n):\n"
            "            if not done[v] and graph[u][v] != inf and dist[u] + graph[u][v] < dist[v]:\n"
            "                dist[v] = dist[u] + graph[u][v]\n"
            "    return dist\n"
            "\n"
            "def make(n, edges):\n"
            "    inf = float('inf')\n"
            "    matrix = [[inf] * n for _ in range(n)]\n"
            "    for i in range(n):\n"
            "        matrix[i][i] = 0\n"
            "    for u, v, w in edges:\n"
            "        matrix[u][v] = w\n"
            "    return matrix\n"
            "\n"
            "example = make(6, [(0, 1, 10), (0, 4, 5), (1, 2, 1), (1, 4, 2), (2, 3, 4),\n"
            "                   (3, 0, 7), (3, 2, 6), (4, 1, 3), (4, 2, 9), (4, 3, 2)])\n"
            "print(dijkstra(example, 0))\n"
            "print(dijkstra([], 0))\n"
            "print(dijkstra([[0]], 9))\n"
            "print(dijkstra([[0]], 0))\n"
        ),
        'checks': [
            "def _mat(n, edges):\n    inf = float('inf')\n    matrix = [[inf] * n for _ in range(n)]\n    for i in range(n):\n        matrix[i][i] = 0\n    for u, v, w in edges:\n        matrix[u][v] = w\n    return matrix",
            "assert dijkstra([], 0) == [], '空矩阵应返回 []'",
            "assert dijkstra([[0]], 5) == [] and dijkstra([[0]], -1) == [], 'start 越界应返回 []，实际 %r / %r' % (dijkstra([[0]], 5), dijkstra([[0]], -1))",
            "assert dijkstra([[0]], 0) == [0], '单顶点图从 0 出发应返回 [0]，实际 %r' % (dijkstra([[0]], 0),)",
            "assert dijkstra([[0, 3], [4, 0]], 0) == [0, 3], '有向图 0→1(3)、1→0(4)：从 0 出发是 [0, 3]，实际 %r' % (dijkstra([[0, 3], [4, 0]], 0),)",
            "assert dijkstra([[0, 3], [4, 0]], 1) == [4, 0], '同一个图从 1 出发是 [4, 0]（有向图不能反着走），实际 %r' % (dijkstra([[0, 3], [4, 0]], 1),)",
            "_g = _mat(6, [(0, 1, 10), (0, 4, 5), (1, 2, 1), (1, 4, 2), (2, 3, 4), (3, 0, 7), (3, 2, 6), (4, 1, 3), (4, 2, 9), (4, 3, 2)])\nassert dijkstra(_g, 0) == [0, 8, 9, 7, 5, float('inf')], '题面例子从 0 出发应是 [0, 8, 9, 7, 5, inf]（注意 1 最省是 0→4→1 = 8），实际 %r' % (dijkstra(_g, 0),)",
            "_g = _mat(6, [(0, 1, 10), (0, 4, 5), (1, 2, 1), (1, 4, 2), (2, 3, 4), (3, 0, 7), (3, 2, 6), (4, 1, 3), (4, 2, 9), (4, 3, 2)])\nassert dijkstra(_g, 4) == [9, 3, 4, 2, 0, float('inf')], '从 4 出发应是 [9, 3, 4, 2, 0, inf]，实际 %r' % (dijkstra(_g, 4),)",
            "_g = _mat(6, [(0, 1, 10), (0, 4, 5), (1, 2, 1), (1, 4, 2), (2, 3, 4), (3, 0, 7), (3, 2, 6), (4, 1, 3), (4, 2, 9), (4, 3, 2)])\nassert dijkstra(_g, 5) == [float('inf')] * 5 + [0], '顶点 5 没有出边也没有入边，从它出发只有自己可达，实际 %r' % (dijkstra(_g, 5),)",
            "_g = _mat(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)])\nassert dijkstra(_g, 0) == [0, 1, 2, 3], '一条链要能一路松弛下去：应是 [0, 1, 2, 3]，实际 %r' % (dijkstra(_g, 0),)",
            "_g = _mat(3, [(0, 1, 4)])\nassert dijkstra(_g, 0) == [0, 4, float('inf')], '到不了的顶点写 inf（不是 -1、不是 0），实际 %r' % (dijkstra(_g, 0),)",
            "_g = _mat(4, [(0, 1, 1), (0, 2, 5), (1, 2, 1), (2, 3, 1)])\nassert dijkstra(_g, 0) == [0, 1, 2, 3], '绕路更短时要选绕路：0→1→2→3 是 3，实际 %r' % (dijkstra(_g, 0),)",
            "_g = _mat(4, [(0, 1, 1), (0, 2, 5), (1, 2, 1), (2, 3, 1)])\n_r = dijkstra(_g, 0)\nassert _r[2] == 2 and _r[1] == 1, '顶点 2 的最短路是 0→1→2 = 2（不是直达的 5），实际 %r' % (_r,)",
            "_g = _mat(6, [(0, 1, 10), (0, 4, 5), (1, 2, 1), (1, 4, 2), (2, 3, 4), (3, 0, 7), (3, 2, 6), (4, 1, 3), (4, 2, 9), (4, 3, 2)])\n_snapshot = [row[:] for row in _g]\ndijkstra(_g, 0)\nassert _g == _snapshot, '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_undirected = [(0, 1, 7), (0, 2, 9), (1, 2, 10), (1, 3, 15), (2, 3, 11), (2, 5, 2), (3, 4, 6), (4, 5, 9)]\ndef _sym_mat(n, edges):\n    inf = float('inf')\n    matrix = [[inf] * n for _ in range(n)]\n    for i in range(n):\n        matrix[i][i] = 0\n    for u, v, w in edges:\n        matrix[u][v] = w\n        matrix[v][u] = w\n    return matrix\n_g = _sym_mat(6, _undirected)\n_ok = True\nfor _s in range(6):\n    for _t in range(6):\n        if dijkstra(_g, _s)[_t] != dijkstra(_g, _t)[_s]:\n            _ok = False\nassert _ok, '无向图（对称矩阵）里 a 到 b 的最短路应等于 b 到 a 的最短路，两个方向跑一遍必须相等'",
            "_n = 40\n_edges = [(i, (i + 1) % _n, (i * 3) % 9 + 1) for i in range(_n)]\n_edges += [(i, (i * 7 + 3) % _n, (i * 5) % 7 + 1) for i in range(_n)]\n_g = _mat(_n, _edges)\n_mat_edges = [(_u, _v, _g[_u][_v]) for _u in range(_n) for _v in range(_n) if _g[_u][_v] != float('inf') and _u != _v]\ndef _bellman(n, edges, start):\n    inf = float('inf')\n    dist = [inf] * n\n    dist[start] = 0\n    for _ in range(n - 1):\n        for u, v, w in edges:\n            if dist[u] != inf and dist[u] + w < dist[v]:\n                dist[v] = dist[u] + w\n    return dist\n_expected = _bellman(_n, _mat_edges, 0)\nassert dijkstra(_g, 0) == _expected, '40 个顶点的随机有向图应与 Bellman-Ford 的结果一致（期望前 5 位 %r，实际前 5 位 %r）' % (_expected[:5], dijkstra(_g, 0)[:5])",
            "_g = _mat(5, [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2), (0, 4, 100)])\n_r = dijkstra(_g, 0)\nassert _r == [0, 2, 4, 6, 8], '长链比一条直达的巨边更省：应是 [0, 2, 4, 6, 8]，实际 %r' % (_r,)",
        ],
        'explanation': (
            'Dijkstra 是「**不断确定最近的点**」的贪心：\n\n'
            '```python\n'
            'dist = list(graph[start])        # 起点那一行：只走一条边的距离\n'
            'for _ in range(n):\n'
            '    u = 未确定点里 dist 最小的\n'
            '    if dist[u] == inf: break     # 剩下的都到不了\n'
            '    done[u] = True\n'
            '    for v in range(n):\n'
            '        if graph[u][v] != inf and dist[u] + graph[u][v] < dist[v]:\n'
            '            dist[v] = dist[u] + graph[u][v]      # 松弛\n'
            '```\n\n'
            '**为什么「dist 最小的未确定点」可以直接确定？** 所有边权都是正的，'
            '想从别的路绕到 u，得先经过某个还没确定的点 x，而 `dist[x] >= dist[u]`，'
            '再加上正权边只会更大——所以 `dist[u]` 已经不可能被改小了，可以放心确定。\n\n'
            '**这题一共有三个坑**：\n\n'
            '1. **无边的 `inf` 不能参与加法**（`inf + w` 还是 inf，结果看起来「没错」，'
            '但如果把 `inf` 写成了某个大整数就会算错）；\n'
            '2. **有向图**：`graph[i][j]` 只表示 i→j，别顺手把矩阵当对称的；\n'
            '3. **不要修改传入的矩阵**（`dist = list(graph[start])` 是拷贝，'
            '写完别再去改 `graph`）。\n\n'
            '**常见错误**：\n\n'
            '- 用 Dijkstra 处理**负权边**（本算法会失效，负权要用 Bellman-Ford / SPFA）；\n'
            '- 松弛时忘记先判断 `graph[u][v] != inf`；\n'
            '- 忘了「起点越界 / 空图」的保护，直接 `graph[start]` 报错；\n'
            '- 输出用 `-1` 或 `0` 表示不可达（本题规定是 `float("inf")`）。\n\n'
            '复杂度：朴素版 O(n²)（每轮线性找最小 + 松弛整行），额外空间 O(n)；'
            '堆优化后是 O(e log n)，适合稀疏图。'
        ),
        'expected_output': '[0, 8, 9, 7, 5, inf]\n[]\n[]\n[0]',
        'hints': ['起始距离用起点那一行；每轮挑未确定点里 dist 最小的标记为已确定', '用 dist[u] + graph[u][v] 去松弛未确定的邻居，不可达保持 inf'],
    },
    # ── 专题 133 · 823·查找（题 22–24）────────────────────
    {
        'id': 'x823-110',
        'track': 'algorithm',
        'chapter_id': 133,
        'chapter_title': '823·查找',
        'topic': '823·查找',
        'title': '题22 折半查找（返回下标与比较次数，验算 ASL）',
        'difficulty': 2,
        'tags': ['查找', '折半查找', '二分', 'ASL'],
        'statement': (
            '**考点：折半查找、平均查找长度 ASL。**\n\n'
            '已知一个**升序**顺序表 `arr`（元素可能重复）和值 `target`。\n\n'
            '定义函数 `binary_search(arr, target)`：返回一个**二元组**'
            '`(index, comparisons)`：\n\n'
            '- `index`：找到时返回 `target` 在表里的**下标**'
            '（有重复元素时返回**任意一个**值等于 `target` 的下标都算对，'
            '但要保证 `arr[index] == target`）；找不到返回 `-1`；空表返回 `-1`；\n'
            '- `comparisons`：**比较次数**，口径是「每执行一轮循环记 1 次」'
            '（循环体里只做一次「`arr[mid]` 与 `target` 比大小」）。'
            '空表是 0 次；单元素表无论命中与否都是 1 次。\n\n'
            '要求**迭代**写法，时间 O(log n)、空间 O(1)，并且**按下面的骨架写**'
            '（本判题系统的比较次数就是按这个骨架数的）：\n\n'
            '```python\n'
            'low = 0\n'
            'high = len(arr) - 1\n'
            'count = 0\n'
            'while low <= high:\n'
            '    mid = (low + high) // 2\n'
            '    count += 1                     # 每轮一次比较\n'
            '    if arr[mid] == target:\n'
            '        return mid, count\n'
            '    if arr[mid] < target:\n'
            '        low = mid + 1              # 扔掉左半边\n'
            '    else:\n'
            '        high = mid - 1             # 扔掉右半边\n'
            'return -1, count\n'
            '```\n\n'
            '- `low <= high` 里的 `=` 不能少，否则「表里只剩一个元素而且正好是它」会被漏判；\n'
            '- 收缩边界必须是 `mid ± 1`，写成 `mid` 会死循环；\n'
            '- 不要用 `bisect` 模块，也不要递归。\n\n'
            '最后打印在 `[1, 3, 5, 7, 9, 11]` 里找 7、找 4 的结果，'
            '再打印空表里找 1、以及全相同的 `[2, 2, 2, 2]` 里找 2 的结果。'
        ),
        'starter_code': 'def binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    count = 0\n    # while low <= high:\n    #     mid = (low + high) // 2\n    #     count += 1                    # 每轮一次比较\n    #     arr[mid] == target 就 return (mid, count)\n    #     arr[mid] < target 就 low = mid + 1；否则 high = mid - 1\n    return -1, count\n',
        'solution': (
            "def binary_search(arr, target):\n"
            "    low = 0\n"
            "    high = len(arr) - 1\n"
            "    count = 0\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        count += 1\n"
            "        if arr[mid] == target:\n"
            "            return mid, count\n"
            "        if arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1, count\n"
            "\n"
            "print(binary_search([1, 3, 5, 7, 9, 11], 7))\n"
            "print(binary_search([1, 3, 5, 7, 9, 11], 4))\n"
            "print(binary_search([], 1))\n"
            "print(binary_search([2, 2, 2, 2], 2))\n"
        ),
        'checks': [
            "_i, _c = binary_search([], 5)\nassert _i == -1 and _c == 0, '空表应返回 (-1, 0)（一次都没比），实际 %r' % ((_i, _c),)",
            "_i, _c = binary_search([5], 5)\nassert _i == 0 and _c == 1, '单元素命中应是 (0, 1)，实际 %r' % ((_i, _c),)",
            "_i, _c = binary_search([5], 4)\nassert _i == -1 and _c == 1, '单元素没命中应是 (-1, 1)，实际 %r' % ((_i, _c),)",
            "_a = [1, 3, 5, 7, 9, 11]\n_i, _c = binary_search(_a, 7)\nassert (_i, _c) == (3, 3), '在 [1, 3, 5, 7, 9, 11] 里找 7：命中下标 3，比较 3 次（mid = 2、4、3），实际 %r' % ((_i, _c),)",
            "_a = [1, 3, 5, 7, 9, 11]\n_i, _c = binary_search(_a, 4)\nassert (_i, _c) == (-1, 3), '找不存在的 4 要比较 3 次后返回 (-1, 3)，实际 %r' % ((_i, _c),)",
            "_a = [1, 3, 5, 7, 9, 11]\nassert binary_search(_a, 1)[0] == 0 and binary_search(_a, 11)[0] == 5, '首尾元素也要能找到，实际 %r / %r' % (binary_search(_a, 1), binary_search(_a, 11))",
            "_a = [1, 3, 5, 7, 9, 11]\nassert binary_search(_a, 0)[0] == -1 and binary_search(_a, 100)[0] == -1 and binary_search(_a, 6)[0] == -1, '比首元素小、比尾元素大、夹在中间但不存在，都要返回 -1'",
            "_b = [2, 2, 2, 2]\n_i, _c = binary_search(_b, 2)\nassert _b[_i] == 2 and _c == 1, '全相同的表里找 2：第一轮 mid = 1 就命中（返回的下标必须真的等于 2），实际 %r' % ((_i, _c),)",
            "_d = [1, 3, 3, 3, 5]\n_i, _c = binary_search(_d, 3)\nassert 0 <= _i < 5 and _d[_i] == 3 and 1 <= _c <= 3, '有重复元素时返回任意一个值等于 3 的下标即可（比较次数 1~3），实际 %r' % ((_i, _c),)",
            "_a = list(range(1, 8))\n_total = sum(binary_search(_a, _v)[1] for _v in _a)\nassert _total == 17, '把 1~7 每个元素都查一遍，比较次数之和应是 17（ASL = 17/7 ≈ 2.43），实际 %r' % (_total,)",
            "_a = list(range(1, 8))\nassert binary_search(_a, 0)[1] == 3 and binary_search(_a, 8)[1] == 3, '在 1~7 里查 0 和 8 都要比较 3 次才确定失败，实际 %r / %r' % (binary_search(_a, 0)[1], binary_search(_a, 8)[1])",
            "_b = list(range(1, 12))\n_total = sum(binary_search(_b, _v)[1] for _v in _b)\nassert _total == 33, '把 1~11 每个元素都查一遍，比较次数之和应是 33（ASL = 33/11 = 3），实际 %r' % (_total,)",
            "_b = list(range(1, 12))\nassert binary_search(_b, 6) == (5, 1), '11 个元素时 mid 正好落在中间的 6 上，应一次命中 (5, 1)，实际 %r' % (binary_search(_b, 6),)",
            "_c = list(range(1000))\nassert binary_search(_c, 500) == (500, 9) and binary_search(_c, 0) == (0, 9), '1000 个元素里查中间和查第一个都应比 9 次，实际 %r / %r' % (binary_search(_c, 500), binary_search(_c, 0))",
            "_c = list(range(1000))\nassert binary_search(_c, 999) == (999, 10), '1000 个元素里查最后一个要比较 10 次（log2(1000) ≈ 10），实际 %r' % (binary_search(_c, 999),)",
            "_big = list(range(0, 200000, 2))\nassert binary_search(_big, 199998) == (99999, 17), '10 万元素里查最后一个（下标 99999）应比较 17 次，实际 %r' % (binary_search(_big, 199998),)",
            "_big = list(range(0, 200000, 2))\n_i, _c = binary_search(_big, 199999)\nassert _i == -1 and _c == 17, '10 万元素里查一个不存在的奇数应返回 (-1, 17)，实际 %r' % ((_i, _c),)",
            "_e = [-10, -5, 0, 3]\nassert binary_search(_e, -5)[0] == 1 and binary_search(_e, -6)[0] == -1, '负数同样要能查找，实际 %r / %r' % (binary_search(_e, -5), binary_search(_e, -6))",
            "_f = [_i for _i in range(100)]\nassert 1 <= binary_search(_f, 50)[1] <= 7 and 1 <= binary_search(_f, 99)[1] <= 7, '100 个元素的比较次数不该超过 7 次（log2(100) ≈ 6.6），实际 %r' % (binary_search(_f, 99),)",
            "_i, _c = binary_search([1, 2, 3], 2)\nassert _i == 1 and _c == 1, '三个元素时 mid 正好是下标 1，应一次命中 (1, 1)，实际 %r' % ((_i, _c),)",
        ],
        'explanation': (
            '折半查找每一轮都在做同一件事：**看中点，然后扔掉不可能的半边**。\n\n'
            '```python\n'
            'low, high, count = 0, len(arr) - 1, 0\n'
            'while low <= high:\n'
            '    mid = (low + high) // 2\n'
            '    count += 1\n'
            '    if arr[mid] == target: return mid, count\n'
            '    if arr[mid] < target: low = mid + 1\n'
            '    else:                 high = mid - 1\n'
            'return -1, count\n'
            '```\n\n'
            '**几个必须抠准的细节**：\n\n'
            '1. `while low <= high`：`low == high` 时区间里还有**一个**元素，必须再比一次；'
            '写成 `low < high` 会在「只剩一个元素而且正好是答案」时误返回 -1；\n'
            '2. 收缩边界必须是 `mid ± 1`（`mid` 已经比过了），写成 `mid` 会死循环；\n'
            '3. 循环外的 `return -1` 是「区间空了都没找到」的出口。\n\n'
            '**ASL（平均查找长度）**：把每个元素的比较次数加起来除以元素个数。'
            '以 1~7 为例，各元素的比较次数是 `3, 2, 3, 1, 3, 2, 3`，'
            '和是 17，所以 ASL = 17/7 ≈ 2.43。'
            '折半查找的判定树是一棵平衡的二叉排序树：'
            '**深度为 h 的判定树最多有 2^h − 1 个结点**，所以 n 个元素的查找最多比较'
            '⌈log2(n + 1)⌉ ≈ log2(n) + 1 次——这就是「100 个元素不超过 7 次」的来历。\n\n'
            '折半查找要求**顺序存储 + 有序**，这也是它不能用在链表上的原因'
            '（链表无法 O(1) 取中点）。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '(3, 3)\n(-1, 3)\n(-1, 0)\n(1, 1)',
        'hints': ['while low <= high 的等号不能丢', '每轮循环先 count += 1，再决定命中还是砍半'],
    },
    {
        'id': 'x823-111',
        'track': 'algorithm',
        'chapter_id': 133,
        'chapter_title': '823·查找',
        'topic': '823·查找',
        'title': '题23 二叉排序树的插入与查找',
        'difficulty': 1,
        'tags': ['查找', '二叉排序树', 'BST', '动态查找'],
        'statement': (
            '**考点：二叉排序树（二叉查找树）的性质与插入、查找操作。**\n\n'
            '先按下面的定义写好结点类与二叉排序树类（名字、属性名必须一致）：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '\n'
            'class BST:\n'
            '    def __init__(self):\n'
            '        self.root = None          # 空树\n'
            '```\n\n'
            '要求实现下面两个方法：\n\n'
            '- `insert(self, val)`：把 `val` 插入二叉排序树。'
            '**插入成功返回 `True`**；若 `val` 已经在树里（**不允许重复**），'
            '**不做任何改动并返回 `False`**。\n'
            '  插入规则：比当前结点小就往左走，大就往右走，走到空位置挂上去'
            '（空树时新结点就是根）；\n'
            '- `search(self, val)`：找到返回 `True`，否则返回 `False`（空树返回 `False`）。\n\n'
            '二叉排序树的性质（必须满足，判题会检查）：**对任意结点，'
            '左子树上所有结点的值都小于它，右子树上所有结点的值都大于它**；'
            '所以**中序遍历**一定能得到递增序列。\n\n'
            '提示：`insert` 要先用「查找」的思路走到该插入的位置，'
            '**在走的过程中要记住父结点**（或者用「当前结点为空就挂上」的写法），'
            '别把结点接丢了；`search` 就是一个循环：小往左、大往右，走到空就是没找到。\n\n'
            '最后依次插入 `50, 30, 70, 20, 40, 60, 80`，打印：\n\n'
            '1. 中序遍历结果（自己写一个遍历函数或列表收集）；\n'
            '2. `search(40)`、`search(99)` 的结果；\n'
            '3. 再插一次 `50`（重复）的结果。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\nclass BST:\n    def __init__(self):\n        self.root = None\n\n    def insert(self, val):\n        # 小往左、大往右；重复值返回 False\n        pass\n\n    def search(self, val):\n        pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "class BST:\n"
            "    def __init__(self):\n"
            "        self.root = None\n"
            "\n"
            "    def insert(self, val):\n"
            "        if self.root is None:\n"
            "            self.root = TreeNode(val)\n"
            "            return True\n"
            "        node = self.root\n"
            "        while True:\n"
            "            if val == node.val:\n"
            "                return False\n"
            "            if val < node.val:\n"
            "                if node.left is None:\n"
            "                    node.left = TreeNode(val)\n"
            "                    return True\n"
            "                node = node.left\n"
            "            else:\n"
            "                if node.right is None:\n"
            "                    node.right = TreeNode(val)\n"
            "                    return True\n"
            "                node = node.right\n"
            "\n"
            "    def search(self, val):\n"
            "        node = self.root\n"
            "        while node is not None:\n"
            "            if val == node.val:\n"
            "                return True\n"
            "            if val < node.val:\n"
            "                node = node.left\n"
            "            else:\n"
            "                node = node.right\n"
            "        return False\n"
            "\n"
            "tree = BST()\n"
            "for value in [50, 30, 70, 20, 40, 60, 80]:\n"
            "    tree.insert(value)\n"
            "\n"
            "def inorder(node, out):\n"
            "    if node is None:\n"
            "        return out\n"
            "    inorder(node.left, out)\n"
            "    out.append(node.val)\n"
            "    inorder(node.right, out)\n"
            "    return out\n"
            "\n"
            "print(inorder(tree.root, []))\n"
            "print(tree.search(40), tree.search(99))\n"
            "print(tree.insert(50))\n"
        ),
        'checks': [
            "def _inorder(node):\n    if node is None:\n        return []\n    return _inorder(node.left) + [node.val] + _inorder(node.right)",
            "def _count(node):\n    if node is None:\n        return 0\n    return 1 + _count(node.left) + _count(node.right)",
            "def _is_bst(node, low=None, high=None):\n    if node is None:\n        return True\n    if low is not None and node.val <= low:\n        return False\n    if high is not None and node.val >= high:\n        return False\n    return _is_bst(node.left, low, node.val) and _is_bst(node.right, node.val, high)",
            "_t = BST()\nassert _t.root is None, '新建的二叉排序树根结点应是 None，实际 %r' % (_t.root,)",
            "_t = BST()\nassert _t.search(1) is False, '空树上查找应返回 False（不能报错），实际 %r' % (_t.search(1),)",
            "_t = BST()\nassert _t.insert(5) is True and _t.root is not None and _t.root.val == 5, '往空树里插入 5：应返回 True 且根结点是 5，实际 %r' % (_t.insert(5),)",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\nassert _inorder(_t.root) == [20, 30, 40, 50, 60, 70, 80], '中序遍历必须递增（这是二叉排序树的判定标准），实际 %r' % (_inorder(_t.root),)",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\nassert _t.root.val == 50 and _t.root.left.val == 30 and _t.root.right.val == 70, '第一个插入的 50 是根，30 在左、70 在右，实际 %r' % (_t.root.val,)",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\nassert _is_bst(_t.root), '必须满足「左子树全都小、右子树全都大」，实际中序 %r' % (_inorder(_t.root),)",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\nassert all(_t.search(_v) for _v in [50, 30, 70, 20, 40, 60, 80]), '插进去的每个值都要能查到'",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\nassert _t.search(45) is False and _t.search(99) is False and _t.search(0) is False and _t.search(-1) is False, '树里没有的值要返回 False（包括小于最小、大于最大）'",
            "_t = BST()\nfor _v in [50, 30, 70]:\n    _t.insert(_v)\nassert _t.insert(50) is False and _t.insert(30) is False and _t.insert(70) is False, '重复值不许插入，应返回 False'",
            "_t = BST()\nfor _v in [50, 30, 70]:\n    _t.insert(_v)\n_t.insert(30)\n_t.insert(30)\nassert _count(_t.root) == 3 and _inorder(_t.root) == [30, 50, 70], '重复插入不能真的加结点：3 个值反复插之后仍应只有 3 个结点，实际 %r 个 / %r' % (_count(_t.root), _inorder(_t.root))",
            "_t = BST()\nfor _v in [1, 2, 3, 4, 5]:\n    _t.insert(_v)\nassert _inorder(_t.root) == [1, 2, 3, 4, 5] and _t.root.left is None and _t.root.right.val == 2, '按升序插入会退化成一条右斜链（这是 BST 的缺点），实际 %r' % (_inorder(_t.root),)",
            "_t = BST()\nfor _v in [5, 4, 3, 2, 1]:\n    _t.insert(_v)\nassert _inorder(_t.root) == [1, 2, 3, 4, 5] and _t.root.right is None and _t.root.left.val == 4, '按降序插入是左斜链，实际 %r' % (_inorder(_t.root),)",
            "_t = BST()\nfor _v in [0, -5, 5, -10, 10]:\n    _t.insert(_v)\nassert _inorder(_t.root) == [-10, -5, 0, 5, 10] and _t.search(-10) and _t.search(10), '0 和负数也要能插、能查，实际 %r' % (_inorder(_t.root),)",
            "_t = BST()\nfor _v in [7, 3, 9, 7, 3, 11, 1]:\n    _t.insert(_v)\nassert _inorder(_t.root) == [1, 3, 7, 9, 11], '重复值出现在中间也不要紧，中序仍应无重复且递增，实际 %r' % (_inorder(_t.root),)",
            "_t = BST()\n_ok = True\nfor _v in range(500, 0, -1):\n    if _t.insert(_v) is not True:\n        _ok = False\nassert _ok and _inorder(_t.root) == list(range(1, 501)), '把 500 个值倒序插进去，中序应正好是 1~500，实际前 3 位 %r' % (_inorder(_t.root)[:3],)",
            "_t = BST()\nfor _v in range(200):\n    _t.insert(_v * 3)\nassert all(_t.search(_v * 3) for _v in range(200)) and not _t.search(1) and not _t.search(598), '200 个值（0, 3, 6, ...）都要能查到，中间缺失的 1 与 598 应查不到'",
            "_t = BST()\nfor _v in [50, 30, 70, 20, 40, 60, 80]:\n    _t.insert(_v)\n_r = _t.search(60)\nassert _r is True, '查找必须返回 True（不是结点、不是 1），实际 %r' % (_r,)",
            "_t = BST()\nfor _v in [5, 2, 8]:\n    _t.insert(_v)\nassert _t.insert(5) is False and _count(_t.root) == 3, '重复插入后树的结点数不能变，实际 %r' % (_count(_t.root),)",
        ],
        'explanation': (
            '二叉排序树把「有序」编进了树形结构里：**小往左、大往右**。'
            '于是查找就像走一条从根到叶的路：\n\n'
            '```python\n'
            'def search(self, val):\n'
            '    node = self.root\n'
            '    while node is not None:\n'
            '        if val == node.val: return True\n'
            '        node = node.left if val < node.val else node.right\n'
            '    return False\n'
            '```\n\n'
            '插入 = **先查找（找该挂的位置），再把新结点接上**。'
            '这里的坑是要「记住父结点」，否则走到 `None` 就回不去了。'
            '本题用的写法是「父结点指向空就挂上」，等价且更短：\n\n'
            '```python\n'
            'if val < node.val:\n'
            '    if node.left is None:\n'
            '        node.left = TreeNode(val); return True\n'
            '    node = node.left\n'
            '```\n\n'
            '**为什么要禁止重复值？** 二叉排序树的查找路径依赖「小于走左、大于走右」，'
            '相等时无路可走；不同教材处理方式不同（有的约定重复放右子树），'
            '本题统一规定：**重复插入返回 False、不改动树**。\n\n'
            '**常见错误**：\n\n'
            '1. 插入时新建了结点却没有挂到父结点上（最常见的错，树永远只有根）；\n'
            '2. 相等的判断写成 `>=` / `<=`，导致重复值插进去后中序不再严格递增；\n'
            '3. `search` 走到 `None` 之后还访问 `node.val`（AttributeError）；\n'
            '4. 用递归插入时忘了把返回值接回 `node.left = insert(...)`，指针链断掉。\n\n'
            '**复杂度**：查找/插入的时间是 O(h)（h 是树高）。'
            '随机数据下 h ≈ O(log n)，但**输入已有序时树退化成链，h = n**，'
            '查找也就退化成 O(n)——这正是需要平衡二叉树（AVL / 红黑树）的原因。'
        ),
        'expected_output': '[20, 30, 40, 50, 60, 70, 80]\nTrue False\nFalse',
        'hints': ['小于往左、大于往右；相等就是重复，直接返回 False', '插入时走到「孩子是 None」的位置挂上新结点；空树时新结点当根'],
    },
    {
        'id': 'x823-112',
        'track': 'algorithm',
        'chapter_id': 133,
        'chapter_title': '823·查找',
        'topic': '823·查找',
        'title': '题24 哈希表（除留余数法 + 线性探测）与 ASL',
        'difficulty': 2,
        'tags': ['查找', '散列表', '线性探测', 'ASL', '装填因子'],
        'statement': (
            '**考点：哈希函数、冲突处理、装填因子、ASL（填空计算必考）。**\n\n'
            '定义类 `HashTable`，用**除留余数法 + 线性探测**实现一个闭散列表'
            '（只用一维数组，不挂链）：\n\n'
            '```python\n'
            'class HashTable:\n'
            '    def __init__(self, size):\n'
            '        self.size = size                  # 表长 m\n'
            '        self.table = [None] * size        # 空槽用 None 标记\n'
            '```\n\n'
            '哈希函数固定为 **`h(key) = key % size`**（除留余数法）；'
            '发生冲突时按 **`(h(key) + 1) % size`、`(h(key) + 2) % size`、……**'
            '依次线性探测（注意绕回表头）。\n\n'
            '实现下面四个方法（名字必须一致）：\n\n'
            '- `insert(key)`：插入整数 `key`。成功返回 `True`；'
            '  若 `key` **已经在表里**（重复插入）或**表已满**，返回 `False` 且不做改动；\n'
            '- `search(key)`：找到返回 `True`，否则返回 `False`。'
            '  **探测到空槽就可以停下**——线性探测的插入不会跳过空槽，空槽后面不可能还有 `key`；\n'
            '- `probes(key)`：返回这次查找**比较过的槽位个数**（算 ASL 的口径）：\n'
            '  - 找到 `key` 时：从 `h(key)` 数到 `key` 所在的槽位（含两端）；\n'
            '  - 找不到时：从 `h(key)` 一直探测到**第一个空槽**为止（含那个空槽）；\n'
            '  - 表已满且 `key` 不在表里时：返回 `size`。\n'
            '- `asl()`：**成功查找的平均查找长度** —— 把表里**已有元素**的 `probes` '
            '求平均；空表返回 `0.0`。\n\n'
            '（顺带记住：**装填因子 α = 表中元素个数 ÷ 表长**，'
            '本题可以自己用 `len([c for c in self.table if c is not None]) / self.size` 算。）\n\n'
            '最后用表长 7 依次插入 `3`、`10`、`17`、`24`，打印它们的 `probes` 与 `asl()`，'
            '再打印 `search(24)`、`search(4)`、重复插入 `3` 的结果。'
        ),
        'starter_code': 'class HashTable:\n    def __init__(self, size):\n        self.size = size\n        self.table = [None] * size\n\n    def insert(self, key):\n        pass\n\n    def search(self, key):\n        pass\n\n    def probes(self, key):\n        pass\n\n    def asl(self):\n        pass\n',
        'solution': (
            "class HashTable:\n"
            "    def __init__(self, size):\n"
            "        self.size = size\n"
            "        self.table = [None] * size\n"
            "\n"
            "    def _probe(self, key):\n"
            "        start = key % self.size\n"
            "        for step in range(self.size):\n"
            "            cell = self.table[(start + step) % self.size]\n"
            "            if cell is None or cell == key:\n"
            "                return step + 1\n"
            "        return self.size\n"
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
            "        return self._probe(key)\n"
            "\n"
            "    def asl(self):\n"
            "        keys = [cell for cell in self.table if cell is not None]\n"
            "        if not keys:\n"
            "            return 0.0\n"
            "        return sum(self._probe(k) for k in keys) / len(keys)\n"
            "\n"
            "table = HashTable(7)\n"
            "for key in [3, 10, 17, 24]:\n"
            "    table.insert(key)\n"
            "print([table.probes(key) for key in [3, 10, 17, 24]], table.asl())\n"
            "print(table.search(24), table.search(4))\n"
            "print(table.insert(3))\n"
        ),
        'checks': [
            "_h = HashTable(7)\nassert _h.size == 7 and len(_h.table) == 7 and all(_c is None for _c in _h.table), '建表后应有 size 个空槽（空槽用 None 标记，不能用 0），实际 %r' % (_h.table,)",
            "_h = HashTable(7)\nassert _h.asl() == 0.0, '空表的 ASL 是 0.0，实际 %r' % (_h.asl(),)",
            "_h = HashTable(7)\nassert _h.search(3) is False and _h.probes(3) == 1, '空表里找 3：3 %% 7 = 3 是空槽，1 次比较就该返回 False，实际 %r / %r' % (_h.search(3), _h.probes(3))",
            "_h = HashTable(7)\nassert _h.insert(3) is True, '往空槽插入 3 应返回 True'",
            "_h = HashTable(7)\n_h.insert(3)\nassert _h.search(3) is True and _h.probes(3) == 1, '插入后找 3：一次就命中（不算后面的空槽），实际 %r / %r' % (_h.search(3), _h.probes(3))",
            "_h = HashTable(7)\n_h.insert(3)\nassert _h.insert(10) is True and _h.probes(10) == 2, '10 %% 7 = 3 冲突，落到槽 4，查找要比较 2 次，实际 %r' % (_h.probes(10),)",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert [_h.probes(_k) for _k in [3, 10, 17, 24]] == [1, 2, 3, 4], '3、10、17、24 都散列到槽 3，依次落在 3、4、5、6 号槽：探测次数应是 1、2、3、4，实际 %r' % ([_h.probes(_k) for _k in [3, 10, 17, 24]],)",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert abs(_h.asl() - 2.5) < 1e-9, '4 个元素的探测次数 1+2+3+4 = 10，ASL = 10/4 = 2.5，实际 %r' % (_h.asl(),)",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert _h.search(24) is True and _h.search(4) is False, '找 24 应 True；找 4（4 %% 7 = 4 被占，往后探测到槽 0 空）应 False，实际 %r / %r' % (_h.search(24), _h.search(4))",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert _h.probes(4) == 4, '找 4 要比较槽 4（10）、槽 5（17）、槽 6（24）、槽 0（空）共 4 次，实际 %r' % (_h.probes(4),)",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert _h.probes(99) == 1, '99 %% 7 = 1 是空槽，1 次比较就停（不能算到别处去），实际 %r' % (_h.probes(99),)",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\nassert _h.insert(3) is False and _h.insert(24) is False, '重复插入已有的 key 应返回 False'",
            "_h = HashTable(7)\nfor _k in [3, 10, 17, 24]:\n    _h.insert(_k)\n_h.insert(17)\nassert _h.probes(17) == 3 and _h.asl() == 2.5, '重复插入不能真的写第二个 17，ASL 与探测次数都要保持不变，实际 %r / %r' % (_h.probes(17), _h.asl())",
            "_h = HashTable(11)\nfor _k in [1, 12, 23, 34, 45]:\n    _h.insert(_k)\nassert [_h.probes(_k) for _k in [1, 12, 23, 34, 45]] == [1, 2, 3, 4, 5], '表长 11 时 1、12、23、34、45 都散列到槽 1，探测次数是 1~5，实际 %r' % ([_h.probes(_k) for _k in [1, 12, 23, 34, 45]],)",
            "_h = HashTable(11)\nfor _k in [1, 12, 23, 34, 45]:\n    _h.insert(_k)\nassert abs(_h.asl() - 3.0) < 1e-9, '1+2+3+4+5 = 15，ASL = 15/5 = 3.0，实际 %r' % (_h.asl(),)",
            "_h = HashTable(11)\nfor _k in [1, 12, 23, 34, 45]:\n    _h.insert(_k)\nassert sum(1 for _c in _h.table if _c is not None) == 5 and abs(sum(1 for _c in _h.table if _c is not None) / _h.size - 5 / 11) < 1e-9, '表长 11 装 5 个元素：装填因子 α = 5/11，实际 %r' % (sum(1 for _c in _h.table if _c is not None) / _h.size,)",
            "_h = HashTable(11)\nfor _k in [1, 12, 23, 34, 45]:\n    _h.insert(_k)\nassert _h.search(45) is True and _h.search(0) is False and _h.probes(0) == 1 and _h.probes(11) == 1, '槽 0 是空的：找 0 与 11 都应 1 次比较后返回 False，实际 %r / %r' % (_h.probes(0), _h.probes(11))",
            "_h = HashTable(5)\nfor _k in [0, 5, 10, 15, 20]:\n    _h.insert(_k)\nassert all(_c is not None for _c in _h.table), '0、5、10、15、20 都散列到槽 0，应把表填满（注意 key 可能是 0，空槽标记不能用 0）'",
            "_h = HashTable(5)\nfor _k in [0, 5, 10, 15, 20]:\n    _h.insert(_k)\nassert _h.search(0) is True and _h.probes(0) == 1, '必须能查到 0（用 0 当空槽标记的实现会在这里出错），实际 %r / %r' % (_h.search(0), _h.probes(0))",
            "_h = HashTable(5)\nfor _k in [0, 5, 10, 15, 20]:\n    _h.insert(_k)\nassert _h.insert(25) is False and _h.insert(1) is False, '表满之后插入应返回 False（不许覆盖已有元素）'",
            "_h = HashTable(5)\nfor _k in [0, 5, 10, 15, 20]:\n    _h.insert(_k)\nassert _h.search(7) is False and _h.probes(7) == 5, '表满且找不到时应把 size 个槽全查一遍（5 次），实际 %r' % (_h.probes(7),)",
            "_h = HashTable(5)\nfor _k in [0, 5, 10, 15, 20]:\n    _h.insert(_k)\nassert abs(_h.asl() - 3.0) < 1e-9, '满表（探测次数 1+2+3+4+5）的 ASL = 15/5 = 3.0，实际 %r' % (_h.asl(),)",
            "_h = HashTable(1)\nassert _h.asl() == 0.0 and _h.probes(9) == 1, '表长 1 的空表：ASL 0.0，查找比较 1 次，实际 %r / %r' % (_h.asl(), _h.probes(9))",
            "_h = HashTable(1)\nassert _h.insert(0) is True and _h.insert(5) is False, '表长 1 插入 0 就满了，再插任何 key 都返回 False'",
            "_h = HashTable(3)\n_h.insert(4)\nassert _h.search(4) is True and _h.probes(4) == 1 and _h.search(1) is False and _h.probes(1) == 2, '4 %% 3 = 1 落在槽 1：找 4 比较 1 次；找 1 要从 h(1) = 1 号槽（被 4 占着）探到 2 号槽（空）才停，共 2 次（实际 %r / %r）' % (_h.probes(4), _h.probes(1))",
            "_h = HashTable(97)\nfor _k in range(50):\n    _h.insert(_k * 3)\nassert _h.search(0) is True and _h.probes(0) == 1 and _h.search(147) is True, '装了 50 个元素后，槽 0 上的 0 仍应 1 次命中；147 应查得到，实际 %r' % (_h.probes(0),)",
            "_h = HashTable(97)\nfor _k in range(50):\n    _h.insert(_k * 3)\nassert 1.0 <= _h.asl() <= 3.0, '50 个元素、表长 97（α ≈ 0.52）时成功 ASL 应在 1.0~3.0 之间，实际 %r' % (_h.asl(),)",
            "_h = HashTable(13)\nfor _k in [19, 14, 23, 1, 68, 20, 84, 27]:\n    _h.insert(_k)\n_h2 = HashTable(13)\nfor _k in [27, 84, 20, 68, 1, 23, 14, 19]:\n    _h2.insert(_k)\nassert _h.asl() >= 1.0 and _h2.asl() >= 1.0, '换一个插入顺序 ASL 会变（这正是「聚集」现象），但都要能算出数（实际 %r / %r）' % (_h.asl(), _h2.asl())",
            "_h = HashTable(13)\nfor _k in [19, 14, 23, 1, 68, 20, 84, 27]:\n    _h.insert(_k)\nassert all(_h.search(_k) for _k in [19, 14, 23, 1, 68, 20, 84, 27]) and not _h.search(30) and not _h.search(6), '插进去的每个 key 都要能查到；30、6 不该在表里'",
        ],
        'explanation': (
            '线性探测散列表的三件事都要「绕圈」做，取模 `% size` 是核心：\n\n'
            '```python\n'
            'start = key % size\n'
            'for step in range(size):\n'
            '    slot = (start + step) % size\n'
            '```\n\n'
            '**为什么查找可以「遇到空槽就停」？** 因为插入时一遇到空槽就放进去了，'
            '绝不会跳过空槽继续往后找位置；所以沿着同一条探测链走，'
            '空槽之前没有 key，空槽之后更不可能有。'
            '这条性质把「查找失败」的代价限制在一个很小的范围内（ASL 不成功约为 1/(1−α)）。\n\n'
            '**ASL 的口径**：成功查找的 ASL = 每个元素的探测次数之和 ÷ 元素个数。'
            '本题的例子（表长 7，插入 3、10、17、24）探测次数是 1、2、3、4，'
            'ASL = 10/4 = 2.5；而**查找失败**的 ASL 是按「探测到第一个空槽」的次数算的，'
            '两者口径不要混。\n\n'
            '**为什么说「冲突会传染」（聚集现象）？** 表长 7 那个例子最明显：'
            '4 个同余的 key 挤在一段连续槽里，后来者（哪怕散列地址本该是空的）'
            '也要沿着这一串往后挪，ASL 迅速上升。'
            '装填因子 α 越大，聚集越严重——这就是散列表要**留出余量**、'
            '并在 α 过高时扩容的原因。\n\n'
            '**常见错误**：\n\n'
            '1. 探测不取模，`start + step` 越界 IndexError（或漏掉绕回表头的部分）；\n'
            '2. 用 `0` 当空槽标记——key 本身可能是 0，应该用 `None`；\n'
            '3. 重复插入直接返回 True，或者更糟：把原来的 key 覆盖掉；\n'
            '4. `probes` 找不到时只数到最后一个非空槽，忘了算那个「确认失败的空槽」。\n\n'
            '复杂度：一趟插入 / 查找最多 O(size)，散列均匀时平均 O(1)。'
        ),
        'expected_output': '[1, 2, 3, 4] 2.5\nTrue False\nFalse',
        'hints': ['探测一律写成 (start + step) % size，注意绕回表头', '空槽用 None；查找失败时 probes 要算上那个空槽'],
    },
    # ── 专题 134 · 823·内部排序（题 25–29）────────────────
    {
        'id': 'x823-113',
        'track': 'algorithm',
        'chapter_id': 134,
        'chapter_title': '823·内部排序',
        'topic': '823·内部排序',
        'title': '题25 冒泡排序（提前结束 + 比较/交换次数）',
        'difficulty': 1,
        'tags': ['排序', '冒泡排序', '交换排序', '稳定性'],
        'statement': (
            '**考点：交换排序、稳定性、时间复杂度。**\n\n'
            '已知顺序表 `items`（元素只要能互相比较大小即可，比如整数或元组）。\n\n'
            '定义函数 `bubble_sort(items)`：\n\n'
            '- **就地**把 `items` 排成升序（函数不改返回值，列表对象本身要变）；\n'
            '- 返回一个二元组 `(comparisons, swaps)`：\n'
            '  - `comparisons`：**元素之间的比较次数**，每执行一次'
            '「`items[j] > items[j + 1]` 这类的相邻比较」记 1 次；\n'
            '  - `swaps`：**交换次数**，每真正交换一对相邻元素记 1 次。\n\n'
            '要求（含优化）：\n\n'
            '1. 外层循环控制「趟数」，第 `i` 趟只需要比较到第 `n - 1 - i` 对'
            '（后面 `i` 个已经是最大的了）；\n'
            '2. **优化：某一趟如果一次交换都没发生，说明表已经有序，'
            '立刻 `break` 提前结束**；\n'
            '3. 只能两两相邻交换，不许用 `sorted` / `items.sort()`。\n\n'
            '参考骨架：\n\n'
            '```python\n'
            'def bubble_sort(items):\n'
            '    comparisons = swaps = 0\n'
            '    n = len(items)\n'
            '    for i in range(n - 1):\n'
            '        changed = False\n'
            '        for j in range(n - 1 - i):\n'
            '            comparisons += 1\n'
            '            if items[j] > items[j + 1]:\n'
            '                items[j], items[j + 1] = items[j + 1], items[j]\n'
            '                swaps += 1\n'
            '                changed = True\n'
            '        if not changed:\n'
            '            break\n'
            '    return (comparisons, swaps)\n'
            '```\n\n'
            '最后打印 `[5, 1, 4, 2, 8]` 的结果与排序后的表，'
            '再打印已经有序的 `[1, 2, 3]`（优化的效果：只比 2 次就结束）'
            '与空表 `[]` 的结果。'
        ),
        'starter_code': 'def bubble_sort(items):\n    comparisons = 0\n    swaps = 0\n    n = len(items)\n    for i in range(n - 1):\n        changed = False\n        # 内层只比到 n - 1 - i；一趟没换过就提前结束\n        pass\n    return (comparisons, swaps)\n',
        'solution': (
            "def bubble_sort(items):\n"
            "    comparisons = 0\n"
            "    swaps = 0\n"
            "    n = len(items)\n"
            "    for i in range(n - 1):\n"
            "        changed = False\n"
            "        for j in range(n - 1 - i):\n"
            "            comparisons += 1\n"
            "            if items[j] > items[j + 1]:\n"
            "                items[j], items[j + 1] = items[j + 1], items[j]\n"
            "                swaps += 1\n"
            "                changed = True\n"
            "        if not changed:\n"
            "            break\n"
            "    return (comparisons, swaps)\n"
            "\n"
            "data = [5, 1, 4, 2, 8]\n"
            "print(bubble_sort(data), data)\n"
            "sorted_data = [1, 2, 3]\n"
            "print(bubble_sort(sorted_data), sorted_data)\n"
            "empty = []\n"
            "print(bubble_sort(empty), empty)\n"
        ),
        'checks': [
            "_a = [5, 1, 4, 2, 8]\n_r = bubble_sort(_a)\nassert _a == [1, 2, 4, 5, 8], '排序结果是 [1, 2, 4, 5, 8]，实际 %r' % (_a,)",
            "_a = [5, 1, 4, 2, 8]\n_r = bubble_sort(_a)\nassert _r == (9, 4), '[5, 1, 4, 2, 8] 的比较/交换次数应是 (9, 4)（第 1 趟 4 比 3 换、第 2 趟 3 比 1 换、第 3 趟 2 比 0 换后提前结束），实际 %r' % (_r,)",
            "_a = []\nassert bubble_sort(_a) == (0, 0) and _a == [], '空表应返回 (0, 0)（不能报错）'",
            "_a = [7]\nassert bubble_sort(_a) == (0, 0) and _a == [7], '只有一个元素时不用比较，返回 (0, 0)'",
            "_a = [1, 2, 3]\nassert bubble_sort(_a) == (2, 0), '已经有序的 [1, 2, 3] 只比 2 次就提前结束（这就是优化的意义），实际 %r' % (bubble_sort([1, 2, 3]),)",
            "_a = [3, 2, 1]\nassert bubble_sort(_a) == (3, 3) and _a == [1, 2, 3], '完全逆序的三个元素：3 次比较、3 次交换，实际 %r' % (bubble_sort([3, 2, 1]),)",
            "_a = [5, 5, 5, 5]\nassert bubble_sort(_a) == (3, 0), '元素全相同：第一趟比 3 次、0 次交换，然后提前结束，实际 %r' % (bubble_sort([5, 5, 5, 5]),)",
            "_a = [4, 4, 4]\nassert bubble_sort(_a) == (2, 0), '三个相同元素只比 2 次，实际 %r' % (bubble_sort([4, 4, 4]),)",
            "_a = [2, 1]\nassert bubble_sort(_a) == (1, 1) and _a == [1, 2], '两个逆序元素：1 次比较、1 次交换，实际 %r' % (bubble_sort([2, 1]),)",
            "_a = [1, 2]\nassert bubble_sort(_a) == (1, 0) and _a == [1, 2], '两个已有序元素：1 次比较、0 次交换，实际 %r' % (bubble_sort([1, 2]),)",
            "_a = [3, 1, 2, 1, 5]\nassert bubble_sort(_a)[0] >= 4 and _a == [1, 1, 2, 3, 5], '有重复元素时每个元素都要保留，实际 %r' % (_a,)",
            "_a = [-3, 5, 0, -1]\nassert bubble_sort(_a)[0] >= 3 and _a == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_a,)",
            "_pairs = [(2, 'a'), (1, 'b'), (2, 'c')]\nbubble_sort(_pairs)\nassert _pairs == [(1, 'b'), (2, 'a'), (2, 'c')], '冒泡排序是稳定的（相等的元素保持原来的先后）：应是 [(1, b), (2, a), (2, c)]，实际 %r' % (_pairs,)",
            "_a = [3, 2, 1]\n_ref = _a\nbubble_sort(_a)\nassert _a is _ref and _ref == [1, 2, 3], '要求原地排序：函数内部要改同一个列表对象，实际 %r' % (_ref,)",
            "_n = 20\n_a = list(range(_n, 0, -1))\n_r = bubble_sort(_a)\nassert _a == list(range(1, _n + 1)) and _r == (190, 190), '20 个元素完全逆序：比较与交换都是 n(n-1)/2 = 190 次（没有提前结束的机会），实际 %r' % (_r,)",
            "_n = 500\n_a = list(range(_n))\n_r = bubble_sort(_a)\nassert _r == (_n - 1, 0), '500 个已升序元素只比 499 次、交换 0 次就结束（优化版是 O(n) 而不是 O(n²)），实际 %r' % (_r,)",
            "_a = [(_i * 7919) % 10007 for _i in range(300)]\n_expect = sorted(_a)\n_r = bubble_sort(_a)\nassert _a == _expect, '300 个元素的表也要排对（前 3 位 %r，期望 %r）' % (_a[:3], _expect[:3])",
            "_a = [(_i * 7919) % 10007 for _i in range(300)]\n_r = bubble_sort(_a)\nassert _r[0] <= 300 * 299 // 2, '比较次数最多是 n(n-1)/2 = 44850，实际 %r' % (_r[0],)",
            "_a = [9, 8, 7, 6, 5, 4]\n_r = bubble_sort(_a)\nassert _a == [4, 5, 6, 7, 8, 9] and _r[1] == _r[0] or _r[1] <= _r[0], '交换次数不会超过比较次数，实际 %r' % (_r,)",
        ],
        'explanation': (
            '冒泡排序的每一趟都在做「相邻两两比较，逆序就换」：'
            '一趟走完，**最大的元素一定被推到了末尾**，所以下一趟可以少比一个。\n\n'
            '```python\n'
            'for i in range(n - 1):\n'
            '    changed = False\n'
            '    for j in range(n - 1 - i):        # 后面 i 个已经就位\n'
            '        comparisons += 1\n'
            '        if items[j] > items[j + 1]:\n'
            '            items[j], items[j + 1] = items[j + 1], items[j]\n'
            '            swaps += 1\n'
            '            changed = True\n'
            '    if not changed:                   # 一趟没换过 = 已经有序\n'
            '        break\n'
            '```\n\n'
            '**提前结束这个优化有多值钱？** 已经有序的表只用 1 趟、n−1 次比较，'
            '时间 O(n)；不写这个判断则永远跑满 n(n−1)/2 次。'
            '考试里「基本有序的数据用什么排序」这类题，答案常常就是冒泡 / 插入。\n\n'
            '**稳定性**：冒泡只交换相邻的一对，而且条件是**严格大于**才换，'
            '所以值相等的一对永远不会被换到前后颠倒——**冒泡排序是稳定的**。'
            '如果把条件写成 `>=`，它立刻变成不稳定排序（本题用元素带标记的检查项验证这一点）。\n\n'
            '**常见错误**：\n\n'
            '1. 内层写成 `range(n)`，既多比又可能越界（`items[j + 1]`）；\n'
            '2. 忘记 `changed` 标记只声明不更新，优化失效；\n'
            '3. 只写一层循环（把「冒泡」写成了「一趟」）；\n'
            '4. 返回值写成 `comparisons` 或 `[comparisons, swaps]`——本题要求**二元组**。\n\n'
            '复杂度：时间平均/最坏 O(n²)（最坏比较与交换都是 n(n−1)/2），'
            '最好 O(n)（有序 + 提前结束）；额外空间 O(1)。'
        ),
        'expected_output': '(9, 4) [1, 2, 4, 5, 8]\n(2, 0) [1, 2, 3]\n(0, 0) []',
        'hints': ['内层 j 只到 n - 1 - i；一趟没发生交换就 break', '比较次数每轮 +1；交换成功才把 swaps +1'],
    },
    {
        'id': 'x823-114',
        'track': 'algorithm',
        'chapter_id': 134,
        'chapter_title': '823·内部排序',
        'topic': '823·内部排序',
        'title': '题26 直接插入排序（比较/移动次数与「基本有序」的威力）',
        'difficulty': 1,
        'tags': ['排序', '插入排序', '基本有序', '稳定性'],
        'statement': (
            '**考点：插入排序、基本有序时效率趋近 O(n)。**\n\n'
            '已知顺序表 `items`（元素可比较）。\n\n'
            '定义函数 `insertion_sort(items)`：\n\n'
            '- **就地**把 `items` 排成升序；\n'
            '- 返回二元组 `(comparisons, moves)`：\n'
            '  - `comparisons`：**元素之间比大小**的次数'
            '（`items[j] > value` 这种比较；只判 `j >= 0` 的下标判断不算）；\n'
            '  - `moves`：**元素移动次数**——每执行一次 `items[j + 1] = items[j]` 记 1 次，'
            '  最后把 `value` 写回空位（`items[j + 1] = value`）也记 1 次'
            '  （即使位置没变也记）。\n\n'
            '做法（把 `items[i]` 插到前面已经有序的 `items[0..i-1]` 里）：\n\n'
            '1. 先把它存进临时变量 `value = items[i]`（因为往后挪元素会覆盖掉它）；\n'
            '2. 从 `j = i - 1` 开始往前找：只要 `items[j] > value` 就把 `items[j]` '
            '往后挪一格（`items[j + 1] = items[j]`，同时 `j -= 1`）；\n'
            '3. 一旦遇到 `items[j] <= value`（或者 `j` 走出表头）就停，'
            '把 `value` 写进 `items[j + 1]`。\n\n'
            '参考骨架：\n\n'
            '```python\n'
            'def insertion_sort(items):\n'
            '    comparisons = moves = 0\n'
            '    for i in range(1, len(items)):\n'
            '        value = items[i]\n'
            '        j = i - 1\n'
            '        while j >= 0:\n'
            '            comparisons += 1\n'
            '            if items[j] > value:\n'
            '                items[j + 1] = items[j]\n'
            '                moves += 1\n'
            '                j -= 1\n'
            '            else:\n'
            '                break\n'
            '        items[j + 1] = value\n'
            '        moves += 1\n'
            '    return (comparisons, moves)\n'
            '```\n\n'
            '注意最后那行 `items[j + 1] = value` 要在循环**外面**：'
            '无论是「找到位置停下」还是「一路挪到表头」，都靠它把值放回去。\n\n'
            '最后打印 `[5, 4, 3, 2, 1]` 的结果与排序后的表，'
            '再打印已经有序的 `[1, 2, 3, 4, 5]`（比较次数应正好是 4 = n−1）'
            '与空表的结果。'
        ),
        'starter_code': 'def insertion_sort(items):\n    comparisons = 0\n    moves = 0\n    for i in range(1, len(items)):\n        value = items[i]\n        j = i - 1\n        # 往前找位置：items[j] > value 就往后挪一格\n        pass\n    return (comparisons, moves)\n',
        'solution': (
            "def insertion_sort(items):\n"
            "    comparisons = 0\n"
            "    moves = 0\n"
            "    for i in range(1, len(items)):\n"
            "        value = items[i]\n"
            "        j = i - 1\n"
            "        while j >= 0:\n"
            "            comparisons += 1\n"
            "            if items[j] > value:\n"
            "                items[j + 1] = items[j]\n"
            "                moves += 1\n"
            "                j -= 1\n"
            "            else:\n"
            "                break\n"
            "        items[j + 1] = value\n"
            "        moves += 1\n"
            "    return (comparisons, moves)\n"
            "\n"
            "data = [5, 4, 3, 2, 1]\n"
            "print(insertion_sort(data), data)\n"
            "sorted_data = [1, 2, 3, 4, 5]\n"
            "print(insertion_sort(sorted_data), sorted_data)\n"
            "empty = []\n"
            "print(insertion_sort(empty), empty)\n"
        ),
        'checks': [
            "_a = [5, 4, 3, 2, 1]\n_r = insertion_sort(_a)\nassert _a == [1, 2, 3, 4, 5], '排序结果是 [1, 2, 3, 4, 5]，实际 %r' % (_a,)",
            "_a = [5, 4, 3, 2, 1]\n_r = insertion_sort(_a)\nassert _r == (10, 14), '完全逆序的 5 个元素：比较 1+2+3+4 = 10 次、移动 2+3+4+5 = 14 次，实际 %r' % (_r,)",
            "_a = [1, 2, 3, 4, 5]\nassert insertion_sort(_a) == (4, 4), '已经有序时每个元素只跟前一个比一次：比较 4 次、写回 4 次（O(n) 的证据），实际 %r' % (insertion_sort([1, 2, 3, 4, 5]),)",
            "_a = []\nassert insertion_sort(_a) == (0, 0) and _a == [], '空表应返回 (0, 0)'",
            "_a = [7]\nassert insertion_sort(_a) == (0, 0) and _a == [7], '单元素表不用比较也不用移动，返回 (0, 0)'",
            "_a = [2, 1]\nassert insertion_sort(_a) == (1, 2) and _a == [1, 2], '两个逆序元素：比较 1 次、移动 2 次（挪一次 + 写回一次），实际 %r' % (insertion_sort([2, 1]),)",
            "_a = [1, 2]\nassert insertion_sort(_a) == (1, 1) and _a == [1, 2], '两个已有序元素：比较 1 次，写回 1 次（写回也算移动，原地不动照样记 1 次），实际 %r' % (insertion_sort([1, 2]),)",
            "_a = [2, 2, 2]\nassert insertion_sort(_a) == (2, 2) and _a == [2, 2, 2], '三个相同的元素：相等就 break，每个只比一次（2 次比较），写回 2 次，实际 %r' % (insertion_sort([2, 2, 2]),)",
            "_a = [3, 1, 2, 1, 5]\nassert insertion_sort(_a) == (7, 8) and _a == [1, 1, 2, 3, 5], '带重复元素的表：比较 7 次、移动 8 次，实际 %r' % (insertion_sort([3, 1, 2, 1, 5]),)",
            "_a = [-3, 5, 0, -1]\ninsertion_sort(_a)\nassert _a == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_a,)",
            "_pairs = [(2, 'a'), (1, 'b'), (2, 'c')]\ninsertion_sort(_pairs)\nassert _pairs == [(1, 'b'), (2, 'a'), (2, 'c')], '直接插入排序是稳定的（相等时不往前挪）：应是 [(1, b), (2, a), (2, c)]，实际 %r' % (_pairs,)",
            "_a = [3, 2, 1]\n_ref = _a\ninsertion_sort(_a)\nassert _a is _ref and _ref == [1, 2, 3], '要求原地排序（同一个列表对象），实际 %r' % (_ref,)",
            "_n = 2000\n_a = list(range(_n))\n_r = insertion_sort(_a)\nassert _r == (_n - 1, _n - 1), '2000 个已升序元素：比较与移动都正好是 1999 次 —— 这就是「基本有序时趋近 O(n)」的实测证据，实际 %r' % (_r,)",
            "_n = 200\n_a = list(range(_n, 0, -1))\n_r = insertion_sort(_a)\nassert _r == (_n * (_n - 1) // 2, _n * (_n - 1) // 2 + _n - 1), '200 个完全逆序元素：比较 n(n-1)/2 = 19900 次、移动 19900 + 199 = 20099 次，实际 %r' % (_r,)",
            "_a = [(_i * 7919) % 10007 for _i in range(400)]\n_expect = sorted(_a)\n_r = insertion_sort(_a)\nassert _a == _expect, '400 个元素的表也要排对（前 3 位 %r，期望 %r）' % (_a[:3], _expect[:3])",
            "_a = [1, 3, 5, 7, 9, 2, 4, 6, 8]\n_r = insertion_sort(_a)\nassert _a == [1, 2, 3, 4, 5, 6, 7, 8, 9] and _r[0] < 9 * 8 // 2, '「前一半有序、后一半是小数」的表比较次数应远小于 n(n-1)/2（因为插入得近），实际 %r' % (_r[0],)",
            "_a = [4, 4, 4, 4]\nassert insertion_sort(_a) == (3, 3), '四个相同元素：每个元素只和前一个比一次（3 次比较），每个元素各写回一次（3 次移动），实际 %r' % (insertion_sort([4, 4, 4, 4]),)",
            "_a = [2, 3, 1]\n_r = insertion_sort(_a)\nassert _a == [1, 2, 3] and _r[0] == 3, '把最小的 1 插到表头：比较 2 次 + 写回 3 次，比较共 3 次，实际 %r' % (_r,)",
        ],
        'explanation': (
            '直接插入排序像**打扑克摸牌**：左手是已经排好的牌，右手摸到一张就往里插。\n\n'
            '```python\n'
            'for i in range(1, len(items)):\n'
            '    value = items[i]                 # 先把摸到的牌拿在手上\n'
            '    j = i - 1\n'
            '    while j >= 0 and items[j] > value:   # 比它大的都往后挪\n'
            '        items[j + 1] = items[j]\n'
            '        j -= 1\n'
            '    items[j + 1] = value             # 空出来的位置放下它\n'
            '```\n\n'
            '**两个必须写对的地方**：\n\n'
            '1. `value = items[i]` 必须先存起来——挪动的过程会把 `items[i]` 覆盖掉；\n'
            '2. 写回是 `items[j + 1] = value`（停下时 `j` 指的是第一个**不大于** value 的位置，'
            '所以要放在 `j + 1`），而且必须在循环外，'
            '这样「一路挪到表头（`j` 变成 -1）」时写回的是 `items[0]`。\n\n'
            '**为什么「基本有序时趋近 O(n)」？** 每张牌只跟左邻居比一次就停下，'
            '一次都不挪，总代价是 n−1 次比较 + n−1 次写回，线性。'
            '本题 2000 个已升序元素的检查项就是把这个结论钉死：'
            '比较 1999 次、移动 1999 次，而不是 O(n²) 的 200 万次。'
            '反过来，完全逆序时每张牌都要挪到最前面，比较与移动都是 O(n²)（200 个元素正好 19900 次比较）。\n\n'
            '**稳定性**：只有 `items[j] > value` 才继续往前挪，'
            '遇到相等的就停手，所以相等元素的前后次序不变——**插入排序是稳定的**'
            '（带标记元组的检查项验证了这一点）。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了备份 `value`，挪动时把待插元素冲掉（结果里出现重复值、丢值）；\n'
            '2. 写回写成 `items[j] = value`（差一格）；\n'
            '3. 把写回写在循环体内，导致中途乱写；\n'
            '4. 用两两交换来「往前挪」（结果对，但移动次数变成 3 倍，考试里会算错移动次数）。\n\n'
            '复杂度：时间最好 O(n)（基本有序）、平均与最坏 O(n²)；空间 O(1)。'
        ),
        'expected_output': '(10, 14) [1, 2, 3, 4, 5]\n(4, 4) [1, 2, 3, 4, 5]\n(0, 0) []',
        'hints': ['先把 items[i] 存进 value，再往前挪元素', '停下后把 value 写进 items[j + 1]（循环外面那一步）'],
    },
    {
        'id': 'x823-115',
        'track': 'algorithm',
        'chapter_id': 134,
        'chapter_title': '823·内部排序',
        'topic': '823·内部排序',
        'title': '题27 快速排序（首元素为基准的划分 + 递归）',
        'difficulty': 2,
        'tags': ['排序', '快速排序', '划分', '分治'],
        'statement': (
            '**考点：分治、基准划分、最好最坏复杂度（823 算法大题高频）。**\n\n'
            '已知顺序表 `items`（元素可比较）。\n\n'
            '定义函数 `quick_sort(items)`：\n\n'
            '- **就地**把 `items` 排成升序；\n'
            '- 返回一个整数：**元素与基准比较的总次数**（口径见下）。\n\n'
            '规定划分方式（必须按这个口径写，判题按它数比较次数）：\n\n'
            '1. **基准取区间第一个元素**：`pivot = items[low]`；\n'
            '2. 用 `i` 记住「小于基准的那些元素已经放好的最后一个位置」，'
            '初始 `i = low`；\n'
            '3. `j` 从 `low + 1` 扫到 `high`：每比较一次 `items[j] < pivot` 记 1 次比较；'
            '   若成立就 `i += 1` 并交换 `items[i]` 与 `items[j]`；\n'
            '4. 扫描结束后交换 `items[low]` 与 `items[i]`——基准落到它的**最终位置** `i`；\n'
            '5. 对左右两段 `[low, i - 1]` 与 `[i + 1, high]` 分别递归，'
            '   区间长度 ≤ 1 时不用做（那是递归出口）。\n\n'
            '参考骨架：\n\n'
            '```python\n'
            'def quick_sort(items):\n'
            '    comparisons = 0\n'
            '    def partition(low, high):\n'
            '        nonlocal comparisons\n'
            '        pivot = items[low]\n'
            '        i = low\n'
            '        for j in range(low + 1, high + 1):\n'
            '            comparisons += 1\n'
            '            if items[j] < pivot:\n'
            '                i += 1\n'
            '                items[i], items[j] = items[j], items[i]\n'
            '        items[low], items[i] = items[i], items[low]\n'
            '        return i\n'
            '    # 递归处理 [low, high]\n'
            '    return comparisons\n'
            '```\n\n'
            '想一想（这题的重点）：**每一趟划分的比较次数就是「区间长度 − 1」**，'
            '所以总比较次数完全由「基准把区间切得多均匀」决定——'
            '均匀时递归深度 O(log n)、总次数 O(n log n)；'
            '而**已经有序时基准每次只切掉一个元素**，总次数正好是 n(n−1)/2，退化 O(n²)。\n\n'
            '最后打印 `[4, 6, 8, 5, 9]` 的排序结果与比较次数，'
            '再打印已经有序的 `[1, 2, 3, 4, 5, 6, 7, 8]`（比较次数应是 28 = 8×7/2）'
            '与空表的结果。'
        ),
        'starter_code': 'def quick_sort(items):\n    comparisons = 0\n\n    def partition(low, high):\n        nonlocal comparisons\n        pivot = items[low]\n        i = low\n        # j 从 low + 1 扫到 high，比 pivot 小的往左边换\n        pass\n\n    def qs(low, high):\n        # low >= high 就返回；否则划分后递归两边\n        pass\n\n    qs(0, len(items) - 1)\n    return comparisons\n',
        'solution': (
            "def quick_sort(items):\n"
            "    comparisons = 0\n"
            "\n"
            "    def partition(low, high):\n"
            "        nonlocal comparisons\n"
            "        pivot = items[low]\n"
            "        i = low\n"
            "        for j in range(low + 1, high + 1):\n"
            "            comparisons += 1\n"
            "            if items[j] < pivot:\n"
            "                i += 1\n"
            "                items[i], items[j] = items[j], items[i]\n"
            "        items[low], items[i] = items[i], items[low]\n"
            "        return i\n"
            "\n"
            "    def qs(low, high):\n"
            "        if low >= high:\n"
            "            return\n"
            "        mid = partition(low, high)\n"
            "        qs(low, mid - 1)\n"
            "        qs(mid + 1, high)\n"
            "\n"
            "    qs(0, len(items) - 1)\n"
            "    return comparisons\n"
            "\n"
            "data = [4, 6, 8, 5, 9]\n"
            "print(quick_sort(data), data)\n"
            "sorted_data = [1, 2, 3, 4, 5, 6, 7, 8]\n"
            "print(quick_sort(sorted_data), sorted_data)\n"
            "empty = []\n"
            "print(quick_sort(empty), empty)\n"
        ),
        'checks': [
            "_a = [4, 6, 8, 5, 9]\n_r = quick_sort(_a)\nassert _a == [4, 5, 6, 8, 9], '排序结果是 [4, 5, 6, 8, 9]，实际 %r' % (_a,)",
            "_a = [4, 6, 8, 5, 9]\n_r = quick_sort(_a)\nassert _r == 8, '[4, 6, 8, 5, 9] 的比较次数是 8（每趟划分比「区间长度 − 1」次：4 + 2 + 1 + 1 = 8），实际 %r' % (_r,)",
            "_a = []\nassert quick_sort(_a) == 0 and _a == [], '空表返回 0 次比较（不能报错）'",
            "_a = [7]\nassert quick_sort(_a) == 0 and _a == [7], '单元素表不用划分，返回 0'",
            "_a = [2, 1]\nassert quick_sort(_a) == 1 and _a == [1, 2], '两个逆序元素：划分 1 次比较，实际 %r' % (quick_sort([2, 1]),)",
            "_a = [1, 2]\nassert quick_sort(_a) == 1 and _a == [1, 2], '两个已有序元素：同样 1 次比较，实际 %r' % (quick_sort([1, 2]),)",
            "_a = [2, 1, 4, 3]\nassert quick_sort(_a) == 4 and _a == [1, 2, 3, 4], '[2, 1, 4, 3] 的比较次数是 4（3 + 1），实际 %r' % (quick_sort([2, 1, 4, 3]),)",
            "_a = [3, 3, 3]\nassert quick_sort(_a) == 3 and _a == [3, 3, 3], '三个相同元素：比较 2 + 1 = 3 次，实际 %r' % (quick_sort([3, 3, 3]),)",
            "_a = [9, 8, 7, 6, 5]\nassert quick_sort(_a) == 10 and _a == [5, 6, 7, 8, 9], '完全逆序的 5 个元素：比较 4 + 3 + 2 + 1 = 10 次（基准每次只切掉一个），实际 %r' % (quick_sort([9, 8, 7, 6, 5]),)",
            "_a = [1, 2, 3, 4, 5, 6, 7, 8]\n_r = quick_sort(_a)\nassert _r == 28 and _a == list(range(1, 9)), '已经升序时是最坏情况：比较次数 = 8×7/2 = 28，实际 %r' % (_r,)",
            "_a = list(range(50))\n_r = quick_sort(_a)\nassert _r == 50 * 49 // 2, '已经升序的 50 个元素：比较 1225 次（= n(n-1)/2，这就是 O(n²) 的最坏情况），实际 %r' % (_r,)",
            "_a = [5, 1, 4, 2, 8]\n_r = quick_sort(_a)\nassert _a == [1, 2, 4, 5, 8] and _r == 6, '[5, 1, 4, 2, 8] 的比较次数是 6（4 + 2），实际 %r' % (_r,)",
            "_a = [-3, 5, 0, -1]\nquick_sort(_a)\nassert _a == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_a,)",
            "_a = [3, 1, 2, 1, 5]\n_r = quick_sort(_a)\nassert _a == [1, 1, 2, 3, 5] and _r == 7, '有重复元素 [3, 1, 2, 1, 5]：排序正确，比较 7 次，实际 %r' % (_r,)",
            "_a = [4, 4, 4, 4, 4, 4]\nassert quick_sort(_a) == 15 and _a == [4, 4, 4, 4, 4, 4], '六个相同元素：比较 5 + 4 + 3 + 2 + 1 = 15 次，实际 %r' % (quick_sort([4, 4, 4, 4, 4, 4]),)",
            "_a = [3, 2, 1]\n_ref = _a\nquick_sort(_a)\nassert _a is _ref and _ref == [1, 2, 3], '要求原地排序（同一个列表对象），实际 %r' % (_ref,)",
            "_a = [(_i * 7919) % 10007 for _i in range(3000)]\n_expect = sorted(_a)\n_r = quick_sort(_a)\nassert _a == _expect, '3000 个元素也要排对（前 3 位 %r，期望 %r）' % (_a[:3], _expect[:3])",
            "_a = [(_i * 7919) % 10007 for _i in range(3000)]\n_n = len(_a)\n_r = quick_sort(_a)\nassert _n - 1 <= _r <= _n * (_n - 1) // 2, '比较次数一定落在 n−1 和 n(n-1)/2 之间（下界是每趟至少比较到一次，上界是最坏情况），实际 %r' % (_r,)",
            "_a = [2, 3, 1]\n_r = quick_sort(_a)\nassert _a == [1, 2, 3] and _r == 2, '[2, 3, 1] 的比较次数是 2（基准 2 划分时和 3、1 各比一次，2 直接归位），实际 %r' % (_r,)",
            "_a = [1, 3, 2]\n_r = quick_sort(_a)\nassert _a == [1, 2, 3] and _r == 3, '[1, 3, 2]：基准 1 只切掉自己，右段 [3, 2] 再比 1 次，共 3 次，实际 %r' % (_r,)",
            "_a = [6, 1, 2, 7, 9, 3, 4, 5, 10, 8]\n_expect = sorted(_a)\n_r = quick_sort(_a)\nassert _a == _expect, '经典 10 元素例子排序不对：%r' % (_a,)",
            "_a = [6, 1, 2, 7, 9, 3, 4, 5, 10, 8]\n_r = quick_sort(_a)\nassert _r < 10 * 9 // 2, '基准能均匀切分时比较次数应明显小于最坏情况的 45 次，实际 %r' % (_r,)",
        ],
        'explanation': (
            '快速排序 = **划分（partition）+ 分治递归**：\n\n'
            '```python\n'
            'def partition(low, high):\n'
            '    pivot = items[low]        # 基准取区间第一个元素\n'
            '    i = low                   # i 是「小于基准区」的最后一个位置\n'
            '    for j in range(low + 1, high + 1):\n'
            '        if items[j] < pivot:\n'
            '            i += 1\n'
            '            items[i], items[j] = items[j], items[i]\n'
            '    items[low], items[i] = items[i], items[low]   # 基准归位\n'
            '    return i                  # 基准的最终下标\n'
            '```\n\n'
            '划分完，基准左边的都比它小、右边的都比它大，**基准的位置以后再也不会变**，'
            '于是问题被切成两个独立的小问题——递归下去即可。\n\n'
            '**比较次数的账**：一趟划分无论数据怎么排，都是「区间长度 − 1」次比较。'
            '所以总次数只取决于**基准把区间切得多均匀**：\n\n'
            '- **最好/平均**：每次大致对半分，递归深度 O(log n)，每层合计约 n 次比较，'
            '总 O(n log n)（10 个元素的例子只有 15 次比较，远小于最坏的 45 次）；\n'
            '- **最坏**：表已经升序或降序，而基准偏偏取第一个元素——'
            '每次划分只把「基准自己」切出去，剩下 n−1 个再递归，'
            '比较次数 = (n−1) + (n−2) + … + 1 = **n(n−1)/2**，退化成 O(n²)。'
            '这就是「快排最坏 O(n²)」的来源（改进办法：随机选基准 / 三数取中）。\n\n'
            '**为什么快排平均比冒泡、插入快这么多？** 因为它是「分治」：'
            '每一层的元素只被比较常数次，但**被处理的问题规模指数级缩小**（log n 层）；'
            '而插入 / 冒泡是每次只把问题缩小 1 个元素（n 层）。\n\n'
            '**常见错误**：\n\n'
            '1. 递归出口漏写或写错（`low >= high` 才返回，`low == high` 也必须返回）；\n'
            '2. 基准 `pivot` 取的是「值」但比较时又去读 `items[low]`——'
            '归位交换那一步会把 `items[low]` 改掉，所以基准值要先存起来；\n'
            '3. 分区后递归区间写成 `[low, mid]`（把基准又算进去，死循环）；\n'
            '4. 用 `sorted` 偷懒，或把小数组改用其他排序——本题要求手写划分。\n\n'
            '复杂度：时间平均 O(n log n)、最坏 O(n²)；'
            '原地划分的空间 O(1)，递归栈平均 O(log n)、最坏 O(n)；快排**不稳定**。'
        ),
        'expected_output': '8 [4, 5, 6, 8, 9]\n28 [1, 2, 3, 4, 5, 6, 7, 8]\n0 []',
        'hints': ['基准取 items[low]，j 从左往右扫，比基准小就换到 i 的位置', '扫描完把基准与 items[i] 交换，递归左右两段（low >= high 是出口）'],
    },
    {
        'id': 'x823-116',
        'track': 'algorithm',
        'chapter_id': 134,
        'chapter_title': '823·内部排序',
        'topic': '823·内部排序',
        'title': '题28 归并排序（拆分 + merge 合并）',
        'difficulty': 2,
        'tags': ['排序', '归并排序', '分治', '稳定性'],
        'statement': (
            '**考点：分治、合并过程、时间与空间复杂度。**\n\n'
            '要求写出**两个**函数（名字必须一致）：\n\n'
            '1. `merge(left, right)`：把两个**各自有序**的列表合并成一个新的有序列表。\n'
            '   - 两个指针分别从头走，谁小就把谁先放进去（**相等时优先取左边**，'
            '这样整体才稳定）；\n'
            '   - 一个列表走完后，把另一个剩下的整段接上；\n'
            '   - `merge([], [])` 返回 `[]`，`merge([], [1, 2])` 返回 `[1, 2]`；\n'
            '   - **不要修改**传入的两个列表。\n'
            '2. `merge_sort(items)`：**返回一个排好序的新列表**'
            '（升序），**不要修改**传入的 `items`；\n'
            '   - 递归拆分：长度 ≤ 1 时直接返回它的副本（递归出口）；\n'
            '   - 否则从中间切开，两边分别 `merge_sort`，再用 `merge` 合并。\n\n'
            '参考骨架：\n\n'
            '```python\n'
            'def merge(left, right):\n'
            '    result = []\n'
            '    i = j = 0\n'
            '    while i < len(left) and j < len(right):\n'
            '        if left[i] <= right[j]:\n'
            '            result.append(left[i]); i += 1\n'
            '        else:\n'
            '            result.append(right[j]); j += 1\n'
            '    result.extend(left[i:])\n'
            '    result.extend(right[j:])\n'
            '    return result\n'
            '\n'
            'def merge_sort(items):\n'
            '    if len(items) <= 1:\n'
            '        return list(items)\n'
            '    mid = len(items) // 2\n'
            '    return merge(merge_sort(items[:mid]), merge_sort(items[mid:]))\n'
            '```\n\n'
            '想一想：每层合并的总代价是 O(n)，一共有 log n 层，所以时间 O(n log n)；'
            '合并需要额外的 result 数组，所以空间 O(n)（这也是归并排序不如快排省内存的原因）。\n\n'
            '最后打印 `[5, 2, 9, 1, 5, 6]` 排序前后的两个列表（证明原表没被改动），'
            '再打印 `merge([1, 3, 5], [2, 4, 6])` 与空表的结果。'
        ),
        'starter_code': 'def merge(left, right):\n    result = []\n    i = 0\n    j = 0\n    # 谁小先放谁；剩下的整段接上\n    pass\n\ndef merge_sort(items):\n    if len(items) <= 1:\n        return list(items)\n    # 从中间切开，两边递归，再 merge\n    pass\n',
        'solution': (
            "def merge(left, right):\n"
            "    result = []\n"
            "    i = 0\n"
            "    j = 0\n"
            "    while i < len(left) and j < len(right):\n"
            "        if left[i] <= right[j]:\n"
            "            result.append(left[i])\n"
            "            i += 1\n"
            "        else:\n"
            "            result.append(right[j])\n"
            "            j += 1\n"
            "    result.extend(left[i:])\n"
            "    result.extend(right[j:])\n"
            "    return result\n"
            "\n"
            "def merge_sort(items):\n"
            "    if len(items) <= 1:\n"
            "        return list(items)\n"
            "    mid = len(items) // 2\n"
            "    left = merge_sort(items[:mid])\n"
            "    right = merge_sort(items[mid:])\n"
            "    return merge(left, right)\n"
            "\n"
            "data = [5, 2, 9, 1, 5, 6]\n"
            "print(merge_sort(data), data)\n"
            "print(merge([1, 3, 5], [2, 4, 6]))\n"
            "print(merge_sort([]))\n"
        ),
        'checks': [
            "assert merge([], []) == [], '两个空列表合并应返回 []'",
            "assert merge([], [1, 2]) == [1, 2] and merge([1, 2], []) == [1, 2], '有一边为空时结果就是另一边（不能报错）'",
            "assert merge([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6], '交错合并应是 [1, 2, 3, 4, 5, 6]，实际 %r' % (merge([1, 3, 5], [2, 4, 6]),)",
            "assert merge([1, 2, 3], [4, 5, 6]) == [1, 2, 3, 4, 5, 6], '一边全小的情况也要对，实际 %r' % (merge([1, 2, 3], [4, 5, 6]),)",
            "assert merge([2, 2], [2]) == [2, 2, 2], '重复值要全部保留（不能去重），实际 %r' % (merge([2, 2], [2]),)",
            "assert merge([5], [1]) == [1, 5] and merge([1], [5]) == [1, 5], '单元素合并两种顺序都要排好，实际 %r / %r' % (merge([5], [1]), merge([1], [5]))",
            "assert merge([-3, 0], [-1, 5]) == [-3, -1, 0, 5], '负数也要合并对，实际 %r' % (merge([-3, 0], [-1, 5]),)",
            "_l = [1, 3]\n_r = [2, 4]\nmerge(_l, _r)\nassert _l == [1, 3] and _r == [2, 4], 'merge 不许修改传入的两个列表，实际 %r / %r' % (_l, _r)",
            "assert merge_sort([]) == [] and merge_sort([7]) == [7], '空表和单元素表要原样返回（单元素要返回列表而不是元素本身），实际 %r / %r' % (merge_sort([]), merge_sort([7]))",
            "assert merge_sort([2, 1]) == [1, 2], '两个逆序元素应返回 [1, 2]，实际 %r' % (merge_sort([2, 1]),)",
            "assert merge_sort([1, 2]) == [1, 2], '两个已有序元素应返回 [1, 2]，实际 %r' % (merge_sort([1, 2]),)",
            "assert merge_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9], '六个元素的例子应是 [1, 2, 5, 5, 6, 9]，实际 %r' % (merge_sort([5, 2, 9, 1, 5, 6]),)",
            "_a = [5, 2, 9, 1, 5, 6]\nmerge_sort(_a)\nassert _a == [5, 2, 9, 1, 5, 6], 'merge_sort 不许修改传入的列表（要返回新列表），实际 %r' % (_a,)",
            "_a = [3, 2, 1]\n_r = merge_sort(_a)\nassert _r is not _a and _a == [3, 2, 1] and _r == [1, 2, 3], '结果必须是新列表（不能原地改），且原表保持 [3, 2, 1]，实际 %r / %r' % (_a, _r)",
            "_a = [5, 5, 5, 5]\nassert merge_sort(_a) == [5, 5, 5, 5], '元素全相同时全部保留，实际 %r' % (merge_sort(_a),)",
            "_a = [3, 1, 3, 1, 2]\nassert merge_sort(_a) == [1, 1, 2, 3, 3], '有重复元素时每个都要保留，实际 %r' % (merge_sort(_a),)",
            "_a = [-3, 5, 0, -1]\nassert merge_sort(_a) == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (merge_sort(_a),)",
            "_pairs = [(2, 'a'), (1, 'b'), (2, 'c'), (1, 'd')]\nassert merge_sort(_pairs) == [(1, 'b'), (1, 'd'), (2, 'a'), (2, 'c')], '归并排序是稳定的：相等元素保持原先后（比较时必须 left[i] <= right[j] 才取左边），实际 %r' % (merge_sort(_pairs),)",
            "_a = list(range(500, 0, -1))\nassert merge_sort(_a) == list(range(1, 501)), '500 个降序元素要排成 1~500（递归深度 log2(500) ≈ 9，不会爆栈），实际前 3 位 %r' % (merge_sort(_a)[:3],)",
            "_a = [(_i * 7919) % 10007 for _i in range(4000)]\n_expect = sorted(_a)\nassert merge_sort(_a) == _expect, '4000 个元素的表也要排对（这题允许用新列表，所以空间是 O(n)）'",
            "_a = []\nassert isinstance(merge_sort(_a), list), 'merge_sort 的返回值必须是列表'",
            "_head, _, _tail = _src.partition('def merge')\nassert _head != _src and 'def merge_sort' in _src, '题面要求分别写 merge 与 merge_sort 两个函数（merge 负责合并、merge_sort 负责拆分递归）'",
            "assert merge_sort(list(range(1000))) == list(range(1000)), '1000 个已升序元素也要排对'",
        ],
        'explanation': (
            '归并排序是「**分治**」最标准的模板：\n\n'
            '```python\n'
            'def merge_sort(items):\n'
            '    if len(items) <= 1:\n'
            '        return list(items)                     # 出口：0/1 个元素天然有序\n'
            '    mid = len(items) // 2\n'
            '    return merge(merge_sort(items[:mid]), merge_sort(items[mid:]))\n'
            '```\n\n'
            '**合并（merge）为什么是 O(n)？** 两个指针各走一遍，每个元素被取走一次，'
            '所以合并 k 个元素只要 k 次操作。\n\n'
            '**总时间怎么算？** 每层合并的总量都是 n，一共拆 log₂n 层'
            '（每次对半分，规模从 n 降到 1），所以 **O(n log n)**，'
            '而且这个界是**稳定**的：最好、平均、最坏都是 O(n log n)——'
            '这是归并相对快排的优势（快排最坏会退化到 O(n²)）。\n\n'
            '**空间 O(n)**：合并时必须借助一个新的 `result` 数组，'
            '递归的每一层都要申请空间；虽然可以用全局临时数组优化到 O(n)，'
            '但相比快排的原地划分，归并的额外空间始终是 O(n)。\n\n'
            '**稳定性**：合并时判断写成 `left[i] <= right[j]` 就取左边，'
            '于是**相等元素左边永远先出**，原来的相对次序保持不变——'
            '归并排序是稳定排序（这也是它被用在「按多个关键字排序」「外部排序」里的原因）。\n\n'
            '**常见错误**：\n\n'
            '1. 递归出口写成 `len(items) == 0`：单元素时 `items[0]` 又要往下拆，死循环；\n'
            '2. 比较写成 `left[i] < right[j]`（相等时取右边）——排序结果还对，但**不再稳定**；\n'
            '3. 合并时忘了把剩下的那一段整段接上（结果少元素）；\n'
            '4. 在 `merge_sort` 里原地改 `items`（切片的副本改了没用，原表却脏了）。\n\n'
            '复杂度：时间 O(n log n)（任何情况），空间 O(n)；需要额外数组，'
            '所以考场上常说「归并适合外排序、快排适合内存里排」。'
        ),
        'expected_output': '[1, 2, 5, 5, 6, 9] [5, 2, 9, 1, 5, 6]\n[1, 2, 3, 4, 5, 6]\n[]',
        'hints': ['merge 用两个指针，谁小先放谁；一个走完就把另一个整段 extend 上去', '相等时取左边（<=）才能保持稳定；merge_sort 返回新列表，不动原表'],
    },
    {
        'id': 'x823-117',
        'track': 'algorithm',
        'chapter_id': 134,
        'chapter_title': '823·内部排序',
        'topic': '823·内部排序',
        'title': '题29 堆排序（建大根堆 + 反复调整堆）',
        'difficulty': 2,
        'tags': ['排序', '堆排序', '大根堆', '筛选'],
        'statement': (
            '**考点：大根堆、调整堆（筛选）、时间复杂度（823 大题）。**\n\n'
            '已知顺序表 `items`。要求写出**两个**函数（名字必须一致）：\n\n'
            '1. `sift_down(items, root, size)`：把下标 `root` 的结点在「有效长度是 `size`」'
            '的堆里**向下调整**（筛选）：\n'
            '   - 它的左孩子是 `2 * root + 1`、右孩子是 `2 * root + 2`；\n'
            '   - 若有孩子比它大，就和**较大的那个孩子**交换，然后继续往下调整；\n'
            '   - 直到它比两个孩子都大（或者孩子不存在，即下标 ≥ `size`）为止；\n'
            '   - 函数不需要返回值。\n'
            '2. `build_heap(items)`：把整个列表**就地**建成**大根堆**'
            '（从最后一个非叶结点 `len(items) // 2 - 1` 开始，**倒着**对每个结点做一次 '
            '`sift_down`）。函数不需要返回值；对已经是堆的表再调用一次，结果不能变。\n'
            '3. `heap_sort(items)`：**就地**把表排成**升序**：先 `build_heap`，'
            '然后反复「把堆顶 `items[0]` 与当前末尾 `items[end]` 交换（最大值归位）→ '
            '有效长度减一 → 对下标 0 做一次 `sift_down`」。函数不需要返回值。\n\n'
            '**升序要用大根堆**：每一轮把最大的放到末尾，最后就是升序。\n'
            '（反过来用「小根堆 + 从后往前填」也可以，但本题统一要求大根堆。）\n\n'
            '不要用 `heapq`，也不要用 `items.sort()` / `sorted`。\n\n'
            '最后打印 `[4, 6, 8, 5, 9]` 排序后的结果，'
            '再打印 `build_heap([1, 2, 3, 4, 5])` 之后堆顶的值，'
            '以及空表、单元素表 `[3]` 的结果。'
        ),
        'starter_code': 'def sift_down(items, root, size):\n    # 和孩子比大小，孩子更大就往下换\n    pass\n\ndef build_heap(items):\n    # 从 len(items) // 2 - 1 倒着 sift_down\n    pass\n\ndef heap_sort(items):\n    # 先建大根堆，再反复把堆顶换到末尾并重新下滤\n    pass\n',
        'solution': (
            "def sift_down(items, root, size):\n"
            "    while True:\n"
            "        child = 2 * root + 1\n"
            "        if child >= size:\n"
            "            return\n"
            "        if child + 1 < size and items[child + 1] > items[child]:\n"
            "            child += 1\n"
            "        if items[child] > items[root]:\n"
            "            items[root], items[child] = items[child], items[root]\n"
            "            root = child\n"
            "        else:\n"
            "            return\n"
            "\n"
            "def build_heap(items):\n"
            "    for i in range(len(items) // 2 - 1, -1, -1):\n"
            "        sift_down(items, i, len(items))\n"
            "\n"
            "def heap_sort(items):\n"
            "    build_heap(items)\n"
            "    for end in range(len(items) - 1, 0, -1):\n"
            "        items[0], items[end] = items[end], items[0]\n"
            "        sift_down(items, 0, end)\n"
            "\n"
            "data = [4, 6, 8, 5, 9]\n"
            "heap_sort(data)\n"
            "print(data)\n"
            "heap = [1, 2, 3, 4, 5]\n"
            "build_heap(heap)\n"
            "print(heap[0])\n"
            "empty = []\n"
            "heap_sort(empty)\n"
            "print(empty)\n"
            "one = [3]\n"
            "heap_sort(one)\n"
            "print(one)\n"
        ),
        'checks': [
            "def _is_heap(items):\n    n = len(items)\n    for _i in range(n):\n        for _c in (2 * _i + 1, 2 * _i + 2):\n            if _c < n and items[_c] > items[_i]:\n                return False\n    return True",
            "_a = [4, 6, 8, 5, 9]\nheap_sort(_a)\nassert _a == [4, 5, 6, 8, 9], '堆排序结果是 [4, 5, 6, 8, 9]，实际 %r' % (_a,)",
            "_a = []\nheap_sort(_a)\nassert _a == [], '空表调用后仍是空表（不能报错）'",
            "_a = [7]\nheap_sort(_a)\nassert _a == [7], '单元素表不用动，实际 %r' % (_a,)",
            "_a = [2, 1]\nheap_sort(_a)\nassert _a == [1, 2], '两个逆序元素要换过来，实际 %r' % (_a,)",
            "_a = [1, 2]\nheap_sort(_a)\nassert _a == [1, 2], '两个已有序元素保持原样，实际 %r' % (_a,)",
            "_a = [5, 4, 3, 2, 1]\nheap_sort(_a)\nassert _a == [1, 2, 3, 4, 5], '完全逆序要排成升序，实际 %r' % (_a,)",
            "_a = [1, 2, 3, 4, 5]\nheap_sort(_a)\nassert _a == [1, 2, 3, 4, 5], '已经升序也要排对（升序表不是大根堆，必须先把堆建对），实际 %r' % (_a,)",
            "_a = [5, 5, 5, 5]\nheap_sort(_a)\nassert _a == [5, 5, 5, 5], '元素全相同时保持原样，实际 %r' % (_a,)",
            "_a = [3, 1, 3, 1, 2]\nheap_sort(_a)\nassert _a == [1, 1, 2, 3, 3], '有重复元素时每个都要保留，实际 %r' % (_a,)",
            "_a = [-3, 5, 0, -1]\nheap_sort(_a)\nassert _a == [-3, -1, 0, 5], '负数和 0 也要排对，实际 %r' % (_a,)",
            "_a = [9, 8, 7, 6, 5, 4, 3]\nheap_sort(_a)\nassert _a == [3, 4, 5, 6, 7, 8, 9], '七个降序元素要排成升序，实际 %r' % (_a,)",
            "_a = [3, 2, 1]\n_ref = _a\nheap_sort(_a)\nassert _a is _ref and _ref == [1, 2, 3], '要求原地排序（同一个列表对象），实际 %r' % (_ref,)",
            "_h = [4, 6, 8, 5, 9]\nbuild_heap(_h)\nassert _is_heap(_h), 'build_heap 之后必须是合法的大根堆（每个父亲都不小于孩子），实际 %r' % (_h,)",
            "_h = [4, 6, 8, 5, 9]\nbuild_heap(_h)\nassert sorted(_h) == [4, 5, 6, 8, 9], '建堆不能丢元素也不能改元素（只是重排），实际 %r' % (_h,)",
            "_h = [1, 2, 3, 4, 5]\nbuild_heap(_h)\nassert _h[0] == 5 and _is_heap(_h), '五个升序元素建堆后堆顶必须是最大值 5，实际 %r' % (_h,)",
            "_h = [5, 4, 3, 2, 1]\nbuild_heap(_h)\nassert _h[0] == 5 and _is_heap(_h), '五个降序元素建堆后堆顶也是 5，实际 %r' % (_h,)",
            "_h = [4, 6, 8, 5, 9]\nbuild_heap(_h)\n_first = list(_h)\nbuild_heap(_h)\nassert _h == _first and _is_heap(_h), '对已经是堆的表再建一次，结果不能变（幂等），实际 %r' % (_h,)",
            "_h = []\nbuild_heap(_h)\nassert _h == [], '空表建堆后仍是空表'",
            "_h = [7]\nbuild_heap(_h)\nassert _h == [7], '单元素表本身就是堆'",
            "_h = [5, 5, 5]\nbuild_heap(_h)\nassert _is_heap(_h) and _h == [5, 5, 5], '全相同的表建堆后不变，实际 %r' % (_h,)",
            "_a = [3, 1, 4, 1, 5, 9, 2, 6]\n_ref = list(_a)\nsift_down(_a, 0, len(_a))\nassert sorted(_a) == sorted(_ref), 'sift_down 只调整顺序、不能增删元素，实际 %r' % (_a,)",
            "_a = [1, 3, 2]\nsift_down(_a, 0, 3)\nassert _a[0] == 3 and _is_heap(_a), '根 1 的两个孩子是 3、2：下滤后堆顶应是 3，实际 %r' % (_a,)",
            "_a = [2, 1, 5]\nsift_down(_a, 0, 3)\nassert _a == [5, 1, 2], '要和较大的孩子换：根 2 的右孩子 5 更大，换完应是 [5, 1, 2]，实际 %r' % (_a,)",
            "_a = [1, 5, 3, 4, 2]\nsift_down(_a, 0, 5)\nassert _a[0] == 5 and _is_heap(_a), '根 1 一路下滤，最终堆顶是 5，实际 %r' % (_a,)",
            "_a = [5, 4, 3, 2, 1]\nsift_down(_a, 1, 5)\nassert _is_heap(_a), '对内部结点（下标 1）下滤也要保持堆性质，实际 %r' % (_a,)",
            "_a = [1, 2, 3]\nsift_down(_a, 0, 1)\nassert _a == [1, 2, 3], 'size = 1 时下标 0 是叶子，什么都不用做，实际 %r' % (_a,)",
            "_a = [9, 1, 2, 5]\nsift_down(_a, 1, 4)\nassert _a == [9, 5, 2, 1] and _is_heap(_a), '下标 1 的值 1 比它的孩子（下标 3 的 5）小，下滤后应变成 [9, 5, 2, 1]，实际 %r' % (_a,)",
            "_a = [(_i * 7919) % 10007 for _i in range(3000)]\n_expect = sorted(_a)\nheap_sort(_a)\nassert _a == _expect, '3000 个元素也要排对（前 3 位 %r，期望 %r）' % (_a[:3], _expect[:3])",
            "_a = list(range(1000))\nheap_sort(_a)\nassert _a == list(range(1000)), '1000 个已升序元素也要排对（堆排序最坏也是 O(n log n)，不会像快排那样退化）'",
            "_a = [(_i * 7919) % 10007 for _i in range(3000)]\n_ref = _a\nheap_sort(_a)\nassert _a is _ref, '要求原地排序：排序后还是同一个列表对象，实际 %r' % (type(_a),)",
        ],
        'explanation': (
            '堆排序把「选择排序」的选择过程加速了：用**大根堆**让「找最大值」只要 O(1)。\n\n'
            '**第一步：建堆（build_heap）**。从**最后一个非叶结点** `n // 2 - 1` 开始，'
            '倒着对每个结点做一次下滤：\n\n'
            '```python\n'
            'for i in range(len(items) // 2 - 1, -1, -1):\n'
            '    sift_down(items, i, len(items))\n'
            '```\n\n'
            '为什么倒着？因为**要先保证孩子已经是堆**，父亲的下滤才有意义；'
            '叶子天然是堆，所以从最后一个非叶结点开始。建堆的总时间是 O(n)'
            '（虽然有下滤，但大部分结点都在底层，均摊下来是线性的）。\n\n'
            '**第二步：反复取堆顶**：\n\n'
            '```python\n'
            'for end in range(len(items) - 1, 0, -1):\n'
            '    items[0], items[end] = items[end], items[0]   # 最大值换到末尾\n'
            '    sift_down(items, 0, end)                      # 有效长度减一后重新下滤\n'
            '```\n\n'
            '**下滤（sift_down）的关键**：和**较大的那个孩子**交换。'
            '如果跟较小的孩子换，换完父结点仍然小于另一个孩子，堆性质就破了。\n'
            '所以顺序是：先选出较大的孩子（`child + 1 < size and items[child + 1] > items[child]`），'
            '再和它比。\n\n'
            '**为什么升序要用大根堆？** 因为「把堆顶（最大值）换到末尾」'
            '正好把当前最大的元素放到它该待的位置，反复 n−1 次就是升序。'
            '若用「小根堆 + 从前往后放」，得到的是降序。\n\n'
            '**常见错误**：\n\n'
            '1. 建堆从 `len(items) // 2` 开始（越界）或从 0 开始（顺序错了，可能建不成堆）；\n'
            '2. `sift_down` 里跟**较小**的孩子交换；\n'
            '3. 忘记「有效长度」这个参数：排序阶段必须只在下标 `< end` 的范围内调整，'
            '否则会把已经归位的最大值又搅回来；\n'
            '4. 用 `heapq`（它是小根堆，且本题要求手写筛选过程）。\n\n'
            '复杂度：时间 O(n log n)（建堆 O(n) + n−1 次下滤，每次 O(log n)），'
            '最好/最坏/平均都是 O(n log n)（不会像快排那样退化）；'
            '额外空间 O(1)（原地）；**堆排序不稳定**。'
        ),
        'expected_output': '[4, 5, 6, 8, 9]\n5\n[]\n[3]',
        'hints': ['建堆要从最后一个非叶结点 n // 2 - 1 倒着做下滤', '下滤只和较大的那个孩子交换；排序阶段用有效长度把已归位的末尾排除在外'],
    },
]
