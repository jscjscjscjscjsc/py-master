"""题库 · 西安科技大学 823《数据结构与算法》考研风格 · 进阶篇（专题 130–133）。

写法约定与 qbank_408.py / qbank_basic.py 保持一致：

- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式，
  图的表示方式（邻接表字典 / 边列表 / 邻接矩阵）在每道题里都逐字交代清楚，不让学生猜。
- checks 是**字符串列表**，判题时在**同一个全局命名空间**里执行：
  可以直接调用学生定义好的函数 / 类，也可以用平台注入的 `_out`（学生的全部标准输出）
  与 `_src`（学生的全部源码）。每条断言都带中文失败提示。
- 参考答案必须能通过自己这一整套断言（tools/verify_qbank.py 会全量复验）。

出题口径（823 真题风格）：

- 图一律按「邻接表字典 `{u: [...]}`」「边列表 `[(u, v, w), ...]`」「邻接矩阵 `matrix[i][j]`」
  三种形式给出，权值统一为**正整数**，无边用 `float('inf')` 表示；
  全篇**不出现负权边**（负权会让 Dijkstra 失效，不在本专题的考查范围内）。
- 覆盖图上算法：邻接矩阵/邻接表、BFS、DFS、拓扑排序、Prim、Kruskal（并查集）、
  **Dijkstra 单源最短路径（朴素版 / 路径还原 / 堆优化版共 3 道）**、Floyd、关键路径。
- 查找与散列：顺序/折半/分块查找、二叉排序树的构造与删除、闭散列（线性探测）、
  开散列（链地址法）、AVL 旋转、折半查找判定树与 ASL。
- 排序与算法分析：冒泡、直接插入、快速排序、归并排序、堆、基数排序、
  快速选择（第 k 小）、归并求逆序对——都要求写出算法本身并分析比较/移动次数。
- 算法设计综合：快速幂（分治）、最大连续子序列和、0-1 背包、区间调度（贪心）、
  最少硬币（完全背包）、并查集、编辑距离、N 皇后（回溯）。

专题划分：

    130 823·图与最短路径      131 823·查找与散列
    132 823·排序与算法分析    133 823·算法设计综合

编号从 x823-101 起（001–099 归同事的基础篇，不要占用）。
"""

QUESTIONS = [
    # ── 专题 130 · 823·图与最短路径 ───────────────────────
    {
        'id': 'x823-301',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': '邻接矩阵转邻接表并统计边数',
        'difficulty': 1,
        'tags': ['图', '邻接矩阵', '邻接表'],
        'statement': (
            '无向图用 n × n 的**邻接矩阵** `matrix` 表示：`matrix[i][j] == 1` 表示顶点 i 与顶点 j '
            '之间有一条边，`0` 表示没有边；对角线全是 0（题面保证不出现自环）。顶点编号为 `0 ~ n - 1`。\n\n'
            '定义函数 `matrix_to_adjlist(matrix)`：返回这张图的**邻接表**，用**字典**表示——\n\n'
            '- 键是每个顶点编号（**每个顶点都要有键**，孤立顶点的值就是空列表）；\n'
            '- 值是该顶点的邻居编号组成的列表，要求**从小到大排好序**。\n\n'
            '再定义函数 `count_edges(adjlist)`：返回无向图的**边数**。\n\n'
            '提示：无向图的每条边在两个端点的邻居表里**各出现一次**，所以边数 = 所有顶点度数之和 ÷ 2；'
            '空图 `{}` 的边数是 0。\n\n'
            '最后打印 `[[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]` 的邻接表与边数，'
            '再打印空矩阵 `[]`、只有一个顶点的 `[[0]]`、全零矩阵 `[[0, 0], [0, 0]]` 的结果。'
        ),
        'starter_code': 'def matrix_to_adjlist(matrix):\n    adjlist = {}\n    # 对每一行，把 matrix[i][j] 不为 0 的列号 j 收进邻居表\n    pass\n\ndef count_edges(adjlist):\n    # 度数之和除以 2\n    pass\n',
        'solution': (
            "def matrix_to_adjlist(matrix):\n"
            "    adjlist = {}\n"
            "    for i in range(len(matrix)):\n"
            "        neighbors = []\n"
            "        for j in range(len(matrix[i])):\n"
            "            if matrix[i][j] != 0:\n"
            "                neighbors.append(j)\n"
            "        adjlist[i] = neighbors\n"
            "    return adjlist\n"
            "\n"
            "def count_edges(adjlist):\n"
            "    total = 0\n"
            "    for neighbors in adjlist.values():\n"
            "        total += len(neighbors)\n"
            "    return total // 2\n"
            "\n"
            "m = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]\n"
            "print(matrix_to_adjlist(m), count_edges(matrix_to_adjlist(m)))\n"
            "print(matrix_to_adjlist([]), count_edges(matrix_to_adjlist([])))\n"
            "print(matrix_to_adjlist([[0]]), count_edges(matrix_to_adjlist([[0]])))\n"
            "zero = [[0, 0], [0, 0]]\n"
            "print(matrix_to_adjlist(zero), count_edges(matrix_to_adjlist(zero)))\n"
        ),
        'checks': [
            "assert matrix_to_adjlist([]) == {}, '空矩阵应返回空字典 {}，实际 %r' % (matrix_to_adjlist([]),)",
            "assert matrix_to_adjlist([[0]]) == {0: []}, '只有一个顶点时字典里也要有这个键，值应是空列表，实际 %r' % (matrix_to_adjlist([[0]]),)",
            "assert matrix_to_adjlist([[0, 1], [1, 0]]) == {0: [1], 1: [0]}, '两个顶点一条边应是 {0: [1], 1: [0]}，实际 %r' % (matrix_to_adjlist([[0, 1], [1, 0]]),)",
            "_m = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]\nassert matrix_to_adjlist(_m) == {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}, '四个顶点的例子邻接表不对，实际 %r' % (matrix_to_adjlist(_m),)",
            "_m = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]\nassert count_edges(matrix_to_adjlist(_m)) == 3, '这个例子有 3 条边，实际 %r' % (count_edges(matrix_to_adjlist(_m)),)",
            "_k4 = [[0 if _i == _j else 1 for _j in range(4)] for _i in range(4)]\nassert matrix_to_adjlist(_k4) == {0: [1, 2, 3], 1: [0, 2, 3], 2: [0, 1, 3], 3: [0, 1, 2]}, '完全图 K4 每个顶点应连着其余 3 个，实际 %r' % (matrix_to_adjlist(_k4),)",
            "_k4 = [[0 if _i == _j else 1 for _j in range(4)] for _i in range(4)]\nassert count_edges(matrix_to_adjlist(_k4)) == 6, '完全图 K4 有 4 × 3 ÷ 2 = 6 条边，实际 %r' % (count_edges(matrix_to_adjlist(_k4)),)",
            "assert matrix_to_adjlist([[0, 0, 0], [0, 0, 0], [0, 0, 0]]) == {0: [], 1: [], 2: []}, '没有任何边的图每个顶点都要有键、值为空列表，实际 %r' % (matrix_to_adjlist([[0, 0, 0], [0, 0, 0], [0, 0, 0]]),)",
            "assert count_edges(matrix_to_adjlist([[0, 0, 0], [0, 0, 0], [0, 0, 0]])) == 0, '没有边时边数是 0，实际 %r' % (count_edges(matrix_to_adjlist([[0, 0, 0], [0, 0, 0], [0, 0, 0]])),)",
            "assert count_edges({}) == 0, '空邻接表的边数是 0'",
            "assert count_edges({0: [1, 2], 1: [0, 3], 2: [0], 3: [1], 4: []}) == 3, '五个顶点、其中一个是孤立顶点时边数是 3，实际 %r' % (count_edges({0: [1, 2], 1: [0, 3], 2: [0], 3: [1], 4: []}),)",
            "_m = [[0, 1], [1, 0]]\n_copy = [_row[:] for _row in _m]\nmatrix_to_adjlist(_m)\nassert _m == _copy, '函数不应修改传入的邻接矩阵，实际 %r' % (_m,)",
            "_n = 60\n_chain = [[0] * _n for _ in range(_n)]\nfor _i in range(_n - 1):\n    _chain[_i][_i + 1] = 1\n    _chain[_i + 1][_i] = 1\n_adj = matrix_to_adjlist(_chain)\nassert _adj[0] == [1] and _adj[59] == [58] and _adj[30] == [29, 31], '60 个顶点的链两端度数应为 1、中间为 2，实际 %r / %r / %r' % (_adj[0], _adj[59], _adj[30])\nassert count_edges(_adj) == 59, '60 个顶点的链应有 59 条边，实际 %r' % (count_edges(_adj),)",
        ],
        'explanation': (
            '邻接矩阵和邻接表是同一张图的两种存法，转换就是一次二维扫描。\n\n'
            '```python\n'
            'for i in range(n):\n'
            '    neighbors = []\n'
            '    for j in range(n):\n'
            '        if matrix[i][j] != 0:\n'
            '            neighbors.append(j)\n'
            '    adjlist[i] = neighbors\n'
            '```\n\n'
            '因为 j 是从 0 递增扫过去的，写进邻居表的编号天然升序，不用再排序。\n\n'
            '**为什么边数要除以 2？** 无向图里 (u, v) 这一条边既记在 u 的邻居表里、也记在 v 的邻居表里，'
            '把所有顶点的度数加起来等于 2 × 边数。有向图就不能这么算（出度和才等于边数）。\n\n'
            '**常见错误**：\n\n'
            '1. 孤立顶点没写进字典——遍历 `adjlist` 时会漏掉它们；\n'
            '2. 边数忘记除以 2，算出来是度数之和；\n'
            '3. 用 `[[0] * n] * n` 之类构造矩阵时的别名问题（本题只是读入，问题不大，但要知道这个坑）。\n\n'
            '复杂度：时间 O(n²)（矩阵本身就有 n² 个元素），额外空间 O(n + E)（邻接表）。'
            '当图很稀疏（E 远小于 n²）时，邻接表比邻接矩阵省得多。'
        ),
        'expected_output': '{0: [1, 2], 1: [0, 3], 2: [0], 3: [1]} 3\n{} 0\n{0: []} 0\n{0: [], 1: []} 0',
        'hints': ['逐行扫描，把 matrix[i][j] 不为 0 的列号 j 收进顶点 i 的邻居表', '无向图边数 = 所有顶点度数之和 // 2'],
    },
    {
        'id': 'x823-302',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': '无权图 BFS 单源最短路径（边数最少）',
        'difficulty': 2,
        'tags': ['图', 'BFS', '最短路径', '队列'],
        'statement': (
            '无向图用**邻接表字典** `graph` 表示：键是顶点编号（整数），值是邻居编号列表；'
            '邻接表是对称的（u 的邻居表里有 v，v 的邻居表里就有 u），'
            '邻居表里出现的编号一定也是 `graph` 的键。空图用 `{}` 表示。\n\n'
            '定义函数 `bfs_shortest(graph, start)`：返回一个字典，键是**从 start 出发能够到达的顶点**，'
            '值是从 start 到它的**最少边数**（start 到自己的距离是 0）。\n\n'
            '要求：\n\n'
            '- 从不了的顶点**不要**放进返回的字典；\n'
            '- 空图、或 start 不在 `graph` 里时返回 `{}`；\n'
            '- 用**队列**做广度优先搜索：先访问的顶点离 start 更近，所以一个顶点第一次被遇到时，'
            '  它的距离就已经是最小的，之后不用再改；\n'
            '- **不要修改**传入的 `graph`。\n\n'
            '时间 O(V + E)。\n\n'
            '最后打印链式图 `{0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}` 从 0 出发与从 3 出发的结果，'
            '再打印两个互不相连的分量 `{0: [1], 1: [0], 2: [3], 3: [2]}` 从 0 出发的结果、'
            '空图的结果、start = 9（图里没有这个顶点）的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef bfs_shortest(graph, start):\n    if not graph or start not in graph:\n        return {}\n    dist = {start: 0}\n    queue = deque([start])\n    # 出队一个顶点，把还没见过的邻居记成「它的距离 + 1」并入队\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "def bfs_shortest(graph, start):\n"
            "    if not graph or start not in graph:\n"
            "        return {}\n"
            "    dist = {start: 0}\n"
            "    queue = deque([start])\n"
            "    while queue:\n"
            "        u = queue.popleft()\n"
            "        for v in graph[u]:\n"
            "            if v not in dist:\n"
            "                dist[v] = dist[u] + 1\n"
            "                queue.append(v)\n"
            "    return dist\n"
            "\n"
            "chain = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}\n"
            "print(bfs_shortest(chain, 0))\n"
            "print(bfs_shortest(chain, 3))\n"
            "print(bfs_shortest({0: [1], 1: [0], 2: [3], 3: [2]}, 0))\n"
            "print(bfs_shortest({}, 0))\n"
            "print(bfs_shortest(chain, 9))\n"
        ),
        'checks': [
            "assert bfs_shortest({}, 0) == {}, '空图应返回 {}，实际 %r' % (bfs_shortest({}, 0),)",
            "assert bfs_shortest({0: []}, 0) == {0: 0}, '只有一个孤立顶点时结果是 {0: 0}，实际 %r' % (bfs_shortest({0: []}, 0),)",
            "assert bfs_shortest({0: [1], 1: [0]}, 9) == {}, 'start 不在图里时应返回 {}，实际 %r' % (bfs_shortest({0: [1], 1: [0]}, 9),)",
            "_g = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}\nassert bfs_shortest(_g, 0) == {0: 0, 1: 1, 2: 2, 3: 3}, '链式图从 0 出发距离应是 0/1/2/3，实际 %r' % (bfs_shortest(_g, 0),)",
            "_g = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}\nassert bfs_shortest(_g, 3) == {3: 0, 2: 1, 1: 2, 0: 3}, '从 3 出发距离应反过来，实际 %r' % (bfs_shortest(_g, 3),)",
            "_g = {0: [1, 2], 1: [0, 2], 2: [0, 1]}\nassert bfs_shortest(_g, 0) == {0: 0, 1: 1, 2: 1}, '三角形里两个邻居距离都是 1，实际 %r' % (bfs_shortest(_g, 0),)",
            "_g = {0: [1], 1: [0], 2: [3], 3: [2]}\nassert bfs_shortest(_g, 0) == {0: 0, 1: 1}, '不连通时只返回起点所在分量的顶点，实际 %r' % (bfs_shortest(_g, 0),)",
            "_g = {0: [0, 1], 1: [0]}\nassert bfs_shortest(_g, 0) == {0: 0, 1: 1}, '顶点有自环时不能把自己算成距离 1，实际 %r' % (bfs_shortest(_g, 0),)",
            "_g = {0: [1], 1: [0], 2: [3], 3: [2], 4: []}\n_r = bfs_shortest(_g, 0)\nassert 4 not in _r and 2 not in _r, '不可达的顶点不能出现在结果里，实际 %r' % (_r,)",
            "_g = {0: [1, 2], 1: [0], 2: [0, 3], 3: [2]}\nassert bfs_shortest(_g, 0)[3] == 2, '0-2-3 两跳比绕路更近，距离应是 2，实际 %r' % (bfs_shortest(_g, 0)[3],)",
            "_g = {0: [1, 2], 1: [0], 2: [0, 3], 3: [2]}\n_copy = {_k: list(_v) for _k, _v in _g.items()}\nbfs_shortest(_g, 0)\nassert _g == _copy, '题面要求不要修改 graph，实际 %r' % (_g,)",
            "_n = 500\n_path = {}\nfor _i in range(_n):\n    _nbrs = []\n    if _i > 0:\n        _nbrs.append(_i - 1)\n    if _i < _n - 1:\n        _nbrs.append(_i + 1)\n    _path[_i] = _nbrs\n_r = bfs_shortest(_path, 0)\nassert len(_r) == _n and _r[_n - 1] == _n - 1, '500 个顶点的链应从 0 一直量到 499（距离 499），实际 %r' % (_r.get(_n - 1),)",
        ],
        'explanation': (
            'BFD（广度优先）之所以能求**无权图**的最短路径，是因为它按「层」推进：'
            '队列里的顶点距离是 0、1、2……严格不下降，第一次遇到某个顶点时走的边数一定最少。\n\n'
            '```python\n'
            'dist = {start: 0}\n'
            'queue = deque([start])\n'
            'while queue:\n'
            '    u = queue.popleft()\n'
            '    for v in graph[u]:\n'
            '        if v not in dist:      # 第一次见到 v，就是最短的\n'
            '            dist[v] = dist[u] + 1\n'
            '            queue.append(v)\n'
            '```\n\n'
            '**为什么不用再更新？** 假设后面还有一条更短的路到 v，那条路的前驱必然更早出队，'
            '也就更早把 v 标记过了——与「第一次遇到」矛盾。\n\n'
            '**常见错误**：\n\n'
            '1. 用 DFS（栈）去求最短路径——DFS 找到的是「一条路」，不是最短路；\n'
            '2. 顶点「入队时」忘记标记，等到「出队时」才标记，同一个顶点会被重复入队很多次；\n'
            '3. 把不可达的顶点也塞进结果（距离记成 -1 或 inf）——题面要求这些顶点不出现；\n'
            '4. 用列表当队列却写 `queue.pop()`（那是栈），必须 `pop(0)` 或 `deque.popleft()`。\n\n'
            '复杂度：时间 O(V + E)（每个顶点入队一次、每条边检查两次），空间 O(V)。'
        ),
        'expected_output': '{0: 0, 1: 1, 2: 2, 3: 3}\n{3: 0, 2: 1, 1: 2, 0: 3}\n{0: 0, 1: 1}\n{}\n{}',
        'hints': ['用 deque 做队列，出队时把没见过的邻居标记为 dist[u] + 1', '顶点在入队时就记距离，保证每个顶点只入队一次'],
    },
    {
        'id': 'x823-303',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': '字典序最小的拓扑排序（Kahn + 最小堆）',
        'difficulty': 2,
        'tags': ['图', '拓扑排序', '入度', '优先队列'],
        'statement': (
            '有向图用**邻接表字典** `graph` 表示：键是顶点名（本题是**小写字母组成的字符串**），'
            '值是顶点 u 的出边指向的顶点列表（`graph[u]` 里是 u 的直接后继）。\n\n'
            '定义函数 `topo_smallest(graph)`：返回**字典序最小**的那个拓扑排序序列（字符串列表）。\n\n'
            '- 拓扑排序：把所有顶点排成一列，使得每条有向边 u → v 都满足「u 排在 v 前面」；\n'
            '- **字典序最小**：在每一步可以选的「入度为 0 的顶点」里，总是挑**字符串最小**的那个输出；\n'
            '- 若图中存在环（剩下的顶点互相牵制、排不出完整序列），返回 `[]`；\n'
            '- 空字典也返回 `[]`。\n\n'
            '要求用 **Kahn 算法**（按入度）+ **最小堆**：\n\n'
            '1. 先统计每个顶点的入度（遍历所有邻接表，被指向一次就加一）；\n'
            '2. 把所有入度为 0 的顶点放进 `heapq` 最小堆；\n'
            '3. 反复弹出堆顶 u 输出，把 u 的每个后继 v 的入度减一，'
            '某个 v 的入度降到 0 就把它压进堆；\n'
            '4. 结束时若输出的顶点数少于总顶点数，说明有环，返回 `[]`。\n\n'
            '时间 O(V + E) 再加堆的 O(V log V)。\n\n'
            '最后打印 `{\'a\': [\'b\', \'c\'], \'b\': [\'d\'], \'c\': [\'d\'], \'d\': []}` 的结果、'
            '有环的 `{\'a\': [\'b\'], \'b\': [\'a\']}` 的结果、空字典的结果、'
            '只有两个孤立顶点的 `{\'b\': [], \'a\': []}` 的结果。'
        ),
        'starter_code': 'import heapq\n\ndef topo_smallest(graph):\n    indegree = {u: 0 for u in graph}\n    # 1. 统计入度  2. 入度为 0 的进最小堆  3. 弹出并给后继减入度\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def topo_smallest(graph):\n"
            "    indegree = {u: 0 for u in graph}\n"
            "    for u in graph:\n"
            "        for v in graph[u]:\n"
            "            indegree[v] = indegree.get(v, 0) + 1\n"
            "    heap = [u for u in graph if indegree[u] == 0]\n"
            "    heapq.heapify(heap)\n"
            "    order = []\n"
            "    while heap:\n"
            "        u = heapq.heappop(heap)\n"
            "        order.append(u)\n"
            "        for v in graph[u]:\n"
            "            indegree[v] -= 1\n"
            "            if indegree[v] == 0:\n"
            "                heapq.heappush(heap, v)\n"
            "    if len(order) != len(graph):\n"
            "        return []\n"
            "    return order\n"
            "\n"
            "print(topo_smallest({'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}))\n"
            "print(topo_smallest({'a': ['b'], 'b': ['a']}))\n"
            "print(topo_smallest({}))\n"
            "print(topo_smallest({'b': [], 'a': []}))\n"
        ),
        'checks': [
            "assert topo_smallest({}) == [], '空图应返回 []，实际 %r' % (topo_smallest({}),)",
            "assert topo_smallest({'a': []}) == ['a'], '只有一个孤立顶点时应返回 [a]，实际 %r' % (topo_smallest({'a': []}),)",
            "_g = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}\nassert topo_smallest(_g) == ['a', 'b', 'c', 'd'], '这个 DAG 的字典序最小拓扑序应是 [a, b, c, d]，实际 %r' % (topo_smallest(_g),)",
            "assert topo_smallest({'a': ['b'], 'b': ['a']}) == [], '二元环应返回 []，实际 %r' % (topo_smallest({'a': ['b'], 'b': ['a']}),)",
            "assert topo_smallest({'a': ['a']}) == [], '自环无法拓扑排序，应返回 []，实际 %r' % (topo_smallest({'a': ['a']}),)",
            "assert topo_smallest({'a': ['b'], 'b': ['a'], 'c': []}) == [], '有环时即使还有别的孤立顶点也要返回 []（不能只输出那个孤立顶点）'",
            "assert topo_smallest({'b': [], 'a': []}) == ['a', 'b'], '两个孤立顶点要按字典序输出 [a, b]，实际 %r' % (topo_smallest({'b': [], 'a': []}),)",
            "_g = {'c': ['e'], 'a': ['b', 'd'], 'b': ['c'], 'd': ['c'], 'e': []}\nassert topo_smallest(_g) == ['a', 'b', 'd', 'c', 'e'], '必须先 a，再在 b 与 d 里取小的 b，然后 d、c、e，实际 %r' % (topo_smallest(_g),)",
            "_g = {'a': ['b'], 'b': ['c'], 'c': []}\nassert topo_smallest(_g) == ['a', 'b', 'c'], '链必须按 a, b, c 输出，实际 %r' % (topo_smallest(_g),)",
            "_g = {'a': [], 'b': ['a'], 'c': ['a']}\nassert topo_smallest(_g) == ['b', 'c', 'a'], '候选里 b 比 c 小，最后才是 a，实际 %r' % (topo_smallest(_g),)",
            "assert topo_smallest({'a': ['b'], 'b': ['c'], 'c': ['a']}) == [], '三元环应返回 []，实际 %r' % (topo_smallest({'a': ['b'], 'b': ['c'], 'c': ['a']}),)",
            "_n = 200\n_g = {}\nfor _i in range(_n):\n    _name = 'v%03d' % _i\n    _next = ['v%03d' % (_i + 1)] if _i < _n - 1 else []\n    _g[_name] = _next\n_r = topo_smallest(_g)\nassert len(_r) == _n and _r[0] == 'v000' and _r[-1] == 'v199', '200 个顶点的链应完整输出 v000 到 v199，实际长度 %r' % (len(_r),)",
            "_g = {'a': ['b', 'c', 'd'], 'b': [], 'c': [], 'd': []}\n_r = topo_smallest(_g)\nassert _r[0] == 'a' and sorted(_r[1:]) == ['b', 'c', 'd'], 'a 必须排在最前面，其余三个按字典序，实际 %r' % (_r,)",
        ],
        'explanation': (
            'Kahn 算法的思路是「先做没有前提的事」：入度为 0 的顶点没有任何前驱，可以立刻输出；'
            '输出它之后，它指向的后继就少了一个前提，入度减一。\n\n'
            '```python\n'
            'heap = [u for u in graph if indegree[u] == 0]\n'
            'heapq.heapify(heap)\n'
            'while heap:\n'
            '    u = heapq.heappop(heap)      # 每次都拿当前最小的\n'
            '    order.append(u)\n'
            '    for v in graph[u]:\n'
            '        indegree[v] -= 1\n'
            '        if indegree[v] == 0:\n'
            '            heapq.heappush(heap, v)\n'
            '```\n\n'
            '**为什么用最小堆就能得到字典序最小？** 拓扑排序在「候选集合」里的选择是自由的，'
            '贪心地每次取最小的一定能得到全局字典序最小的序列（这属于贪心可交换论证：'
            '若某个拓扑序第一位不是最小的候选，把它和那个最小的候选换位置，序列仍然合法且更小）。\n\n'
            '**判环原理**：环上的顶点入度永远降不到 0，队列迟早空掉，'
            '于是输出的顶点数小于总数——这就是有环的判据，此时题目要求返回 `[]` 而不是半截序列。\n\n'
            '**常见错误**：\n\n'
            '1. 用普通的列表 / 栈（`pop()`）当候选集合，得到的不是字典序最小；\n'
            '2. 只统计了部分邻接表的入度；\n'
            '3. 有环时返回已经输出的那一段（题面要求返回空列表）；\n'
            '4. 忘记处理「顶点只出现在别人的邻居表里」的情况——本题保证每个顶点都是字典的键，'
            '但 `indegree.get(v, 0)` 这种写法更保险。\n\n'
            '复杂度：时间 O(V + E + V log V)，空间 O(V)。'
        ),
        'expected_output': "['a', 'b', 'c', 'd']\n[]\n[]\n['a', 'b']",
        'hints': ['入度为 0 的顶点放进 heapq 最小堆，每次弹最小的那个', '输出顶点数少于总顶点数就说明有环，返回 []'],
    },
    {
        'id': 'x823-304',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': 'Dijkstra 单源最短路径（朴素版，邻接矩阵）',
        'difficulty': 2,
        'tags': ['图', '最短路径', 'Dijkstra', '贪心'],
        'statement': (
            '带权**有向图**用 n × n 的**邻接矩阵** `matrix` 表示：\n\n'
            '- `matrix[i][j]` 是边 i → j 的权值（**正整数**）；\n'
            '- 没有边时写 `float(\'inf\')`（可以在开头写 `INF = float(\'inf\')`）；\n'
            '- 对角线（自己到自己）是 0。\n\n'
            '题面保证**没有负权边**——Dijkstra 只适用于非负权图。\n\n'
            '定义函数 `dijkstra(matrix, start)`：返回长度为 n 的列表 `dist`，'
            '`dist[i]` 是从 `start` 到顶点 i 的**最短路径长度**；从 start 到不了的顶点记为 `float(\'inf\')`。'
            '空矩阵、或 `start` 越界（含负数）时返回 `[]`。\n\n'
            '要求手写**朴素版 Dijkstra**（**不要用 heapq**，时间 O(n²)）：\n\n'
            '1. `visited[i]` 表示顶点 i 的最短距离是否已经**确定**；一开始只有 `dist[start] = 0`，其余都是 inf；\n'
            '2. 一共做 n 轮：每一轮在**还没确定**的顶点里挑一个 `dist` 最小的顶点 u'
            '（若最小的也是 inf，说明剩下的顶点全都不可达，可以提前退出）；\n'
            '3. 把 u 标记为已确定，然后拿 u 去**松弛**所有还没确定的顶点 v：'
            '若 `matrix[u][v]` 不是 inf 且 `dist[u] + matrix[u][v] < dist[v]`，就更新 `dist[v]`。\n\n'
            '**为什么能这样挑？** 因为所有边权为正，当前 dist 最小的未确定顶点，'
            '不可能再经过别的顶点绕一圈变得更短——它已经可以「拍板」了。\n\n'
            '最后打印 4 顶点例子（0→1 权 1、0→2 权 4、1→2 权 2、1→3 权 6、2→3 权 3）从 0 出发的距离、'
            '「多跳更便宜」的例子（0→1 权 10、0→2 权 1、2→1 权 1）从 0 出发的距离、'
            '不可达的例子（0→1 权 5，其余无边）从 0 出发的距离、空矩阵的结果。'
        ),
        'starter_code': 'INF = float(\'inf\')\n\ndef dijkstra(matrix, start):\n    n = len(matrix)\n    if n == 0 or start < 0 or start >= n:\n        return []\n    dist = [INF] * n\n    visited = [False] * n\n    dist[start] = 0\n    # 每轮挑一个未确定且 dist 最小的顶点，标记后松弛它的邻居\n    pass\n',
        'solution': (
            "INF = float('inf')\n"
            "\n"
            "def dijkstra(matrix, start):\n"
            "    n = len(matrix)\n"
            "    if n == 0 or start < 0 or start >= n:\n"
            "        return []\n"
            "    dist = [INF] * n\n"
            "    visited = [False] * n\n"
            "    dist[start] = 0\n"
            "    for _ in range(n):\n"
            "        u = -1\n"
            "        best = INF\n"
            "        for i in range(n):\n"
            "            if not visited[i] and dist[i] < best:\n"
            "                best = dist[i]\n"
            "                u = i\n"
            "        if u == -1:\n"
            "            break\n"
            "        visited[u] = True\n"
            "        for v in range(n):\n"
            "            if not visited[v] and matrix[u][v] != INF and dist[u] + matrix[u][v] < dist[v]:\n"
            "                dist[v] = dist[u] + matrix[u][v]\n"
            "    return dist\n"
            "\n"
            "m = [[0, 1, 4, INF],\n"
            "     [INF, 0, 2, 6],\n"
            "     [INF, INF, 0, 3],\n"
            "     [INF, INF, INF, 0]]\n"
            "print(dijkstra(m, 0))\n"
            "cheap = [[0, 10, 1], [INF, 0, INF], [INF, 1, 0]]\n"
            "print(dijkstra(cheap, 0))\n"
            "far = [[0, 5, INF], [INF, 0, INF], [INF, INF, 0]]\n"
            "print(dijkstra(far, 0))\n"
            "print(dijkstra([], 0))\n"
        ),
        'checks': [
            "assert dijkstra([], 0) == [], '空矩阵应返回 []，实际 %r' % (dijkstra([], 0),)",
            "assert dijkstra([[0]], 0) == [0], '只有一个顶点时从它出发的距离是 [0]，实际 %r' % (dijkstra([[0]], 0),)",
            "assert dijkstra([[0]], 5) == [] and dijkstra([[0]], -1) == [], 'start 越界（含负数）时应返回 []，实际 %r / %r' % (dijkstra([[0]], 5), dijkstra([[0]], -1))",
            "assert dijkstra([[0, INF], [INF, 0]], 0) == [0, INF], '两个顶点之间没有边时第二个顶点距离是 inf，实际 %r' % (dijkstra([[0, INF], [INF, 0]], 0),)",
            "_m = [[0, 1, 4, INF], [INF, 0, 2, 6], [INF, INF, 0, 3], [INF, INF, INF, 0]]\nassert dijkstra(_m, 0) == [0, 1, 3, 6], '经典例子从 0 出发应是 [0, 1, 3, 6]（0→1→2→3 比 0→1→3 更近），实际 %r' % (dijkstra(_m, 0),)",
            "_m = [[0, 1, 4, INF], [INF, 0, 2, 6], [INF, INF, 0, 3], [INF, INF, INF, 0]]\nassert dijkstra(_m, 2) == [INF, INF, 0, 3], '从 2 出发到不了 0、1，距离应是 [inf, inf, 0, 3]，实际 %r' % (dijkstra(_m, 2),)",
            "_m = [[0, 5, INF], [INF, 0, INF], [INF, INF, 0]]\nassert dijkstra(_m, 0) == [0, 5, INF], '不可达的顶点要保持 inf，实际 %r' % (dijkstra(_m, 0),)",
            "_m = [[0, INF], [3, 0]]\n_d0 = dijkstra(_m, 0)\n_d1 = dijkstra(_m, 1)\nassert _d0 == [0, INF] and _d1 == [3, 0], '有向图要区分方向：0 到不了 1，1 能到 0（权 3），实际 %r / %r' % (_d0, _d1)",
            "_m = [[0, 10, 1], [INF, 0, INF], [INF, 1, 0]]\nassert dijkstra(_m, 0) == [0, 2, 1], '两条边的路（0→2→1 = 2）比直达（10）更短，实际 %r' % (dijkstra(_m, 0),)",
            "_n = 5\n_m = [[0 if _i == _j else (1 if _j == _i + 1 else INF) for _j in range(_n)] for _i in range(_n)]\nassert dijkstra(_m, 0) == [0, 1, 2, 3, 4], '5 个顶点的链从 0 出发距离应是 0 到 4，实际 %r' % (dijkstra(_m, 0),)",
            "_m = [[0, 1, INF], [INF, 0, 1], [1, INF, 0]]\nassert dijkstra(_m, 0) == [0, 1, 2], '图里有回路时起点到自己仍是 0（绕一圈回来只会更长），实际 %r' % (dijkstra(_m, 0),)",
            "_m = [[0, 1, 4, INF], [INF, 0, 2, 6], [INF, INF, 0, 3], [INF, INF, INF, 0]]\n_copy = [_row[:] for _row in _m]\ndijkstra(_m, 0)\nassert _m == _copy, '函数不应修改传入的邻接矩阵，实际 %r' % (_m,)",
            "_n = 120\n_big = [[0 if _i == _j else INF for _j in range(_n)] for _i in range(_n)]\nfor _i in range(_n - 1):\n    _big[_i][_i + 1] = 2\nassert dijkstra(_big, 0)[119] == 238, '120 个顶点、每段权 2 的链，最远距离应是 119 × 2 = 238，实际 %r' % (dijkstra(_big, 0)[119],)",
        ],
        'explanation': (
            'Dijkstra 就是「贪心 + 松弛」：每次都把**当前距离最小**的未确定顶点拍板，'
            '再用它去改善别人的距离。\n\n'
            '```python\n'
            'for _ in range(n):\n'
            '    u = -1; best = INF\n'
            '    for i in range(n):                 # 挑最小：O(n)\n'
            '        if not visited[i] and dist[i] < best:\n'
            '            best = dist[i]; u = i\n'
            '    if u == -1:                        # 剩下的都不可达\n'
            '        break\n'
            '    visited[u] = True                  # 拍板\n'
            '    for v in range(n):                 # 松弛：O(n)\n'
            '        if not visited[v] and matrix[u][v] != INF and dist[u] + matrix[u][v] < dist[v]:\n'
            '            dist[v] = dist[u] + matrix[u][v]\n'
            '```\n\n'
            '外层 n 轮、内层两个 O(n) 的循环，所以是 O(n²)。稠密图（E 接近 n²）用它最合适；'
            '稀疏图改用邻接表 + 优先队列可以优化到 O(E log V)。\n\n'
            '**为什么「当前最小的顶点可以拍板」？** 假设还存在一条更短的路，'
            '它必须先经过某个还没确定的顶点 x，而 x 的当前距离已经不小于 u 的距离、边权又是正的，'
            '绕过去只会更长——矛盾。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记跳过 `visited[u]`（重复松弛，结果可能还凑巧对，但复杂度更乱）；\n'
            '2. 用「遍历顺序」而不是「最小 dist」来选顶点（那就是 BFS 了，只能处理无权图）；\n'
            '3. 把 `INF` 当成一个很大的整数却忘记判 `matrix[u][v] != INF`，'
            '`inf + 权值` 会污染结果；\n'
            '4. 在负权图上用 Dijkstra——本题明确没有负权，但要知道这是它的适用前提。\n\n'
            '复杂度：时间 O(n²)，额外空间 O(n)。'
        ),
        'expected_output': '[0, 1, 3, 6]\n[0, 2, 1]\n[0, 5, inf]\n[]',
        'hints': ['每轮在「未确定」的顶点里挑 dist 最小的，标记后松弛它的邻居', '更新条件是 dist[u] + matrix[u][v] < dist[v]，并且 matrix[u][v] 不是 inf'],
    },
    {
        'id': 'x823-305',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': 'Dijkstra 记录前驱并还原完整最短路径',
        'difficulty': 3,
        'tags': ['图', '最短路径', 'Dijkstra', '路径还原'],
        'statement': (
            '邻接矩阵约定与上一题相同：带权**有向图**，`matrix[i][j]` 是边 i → j 的**正**权值，'
            '无边写 `float(\'inf\')`，对角线为 0，没有负权边。\n\n'
            '定义函数 `dijkstra_with_path(matrix, start, target)`：返回一个二元组 `(dist, path)`——\n\n'
            '- `dist` 是 start 到 target 的**最短距离**；\n'
            '- `path` 是从 start 到 target 的顶点编号列表，**包含起点和终点**；\n'
            '- 若 target 不可达，返回 `(float(\'inf\'), [])`；\n'
            '- 若 `start == target`，返回 `(0, [start])`（即使图中没有自环）；\n'
            '- 只要矩阵为空、或 start / target 越界（含负数），一律返回 `(float(\'inf\'), [])`。\n\n'
            '要求：在 Dijkstra 的基础上多开一个 `prev` 数组（初值 -1）记录**前驱**：'
            '每当松弛成功（`dist[u] + matrix[u][v] < dist[v]`）就同时写 `prev[v] = u`。'
            '算完以后从 `target` 出发沿着 `prev` 往回走（一直走到 -1 为止），'
            '把顶点依次收起来，最后**反转**就是 start → target 的路径。\n\n'
            '最后打印 5 顶点例子（0→1 权 2、0→2 权 5、1→2 权 1、1→3 权 4、2→3 权 1、3→4 权 3）'
            '中从 0 到 4、从 0 到 3、从 2 到 2、从 4 到 0 的结果，'
            '再打印空矩阵和 target 越界（9）的结果。'
        ),
        'starter_code': 'INF = float(\'inf\')\n\ndef dijkstra_with_path(matrix, start, target):\n    n = len(matrix)\n    # 与朴素 Dijkstra 相同，只是松弛成功时额外记 prev[v] = u\n    # 最后从 target 沿 prev 回溯、反转成路径\n    pass\n',
        'solution': (
            "INF = float('inf')\n"
            "\n"
            "def dijkstra_with_path(matrix, start, target):\n"
            "    n = len(matrix)\n"
            "    if n == 0 or start < 0 or start >= n or target < 0 or target >= n:\n"
            "        return INF, []\n"
            "    dist = [INF] * n\n"
            "    visited = [False] * n\n"
            "    prev = [-1] * n\n"
            "    dist[start] = 0\n"
            "    for _ in range(n):\n"
            "        u = -1\n"
            "        best = INF\n"
            "        for i in range(n):\n"
            "            if not visited[i] and dist[i] < best:\n"
            "                best = dist[i]\n"
            "                u = i\n"
            "        if u == -1:\n"
            "            break\n"
            "        visited[u] = True\n"
            "        for v in range(n):\n"
            "            if not visited[v] and matrix[u][v] != INF and dist[u] + matrix[u][v] < dist[v]:\n"
            "                dist[v] = dist[u] + matrix[u][v]\n"
            "                prev[v] = u\n"
            "    if dist[target] == INF:\n"
            "        return INF, []\n"
            "    path = []\n"
            "    node = target\n"
            "    while node != -1:\n"
            "        path.append(node)\n"
            "        node = prev[node]\n"
            "    path.reverse()\n"
            "    return dist[target], path\n"
            "\n"
            "m = [[0, 2, 5, INF, INF],\n"
            "     [INF, 0, 1, 4, INF],\n"
            "     [INF, INF, 0, 1, INF],\n"
            "     [INF, INF, INF, 0, 3],\n"
            "     [INF, INF, INF, INF, 0]]\n"
            "print(dijkstra_with_path(m, 0, 4))\n"
            "print(dijkstra_with_path(m, 0, 3))\n"
            "print(dijkstra_with_path(m, 2, 2))\n"
            "print(dijkstra_with_path(m, 4, 0))\n"
            "print(dijkstra_with_path([], 0, 0))\n"
            "print(dijkstra_with_path(m, 0, 9))\n"
        ),
        'checks': [
            "assert dijkstra_with_path([], 0, 0) == (float('inf'), []), '空矩阵应返回 (inf, [])，实际 %r' % (dijkstra_with_path([], 0, 0),)",
            "assert dijkstra_with_path([[0]], 0, 0) == (0, [0]), '只有一个顶点且起点就是终点时应返回 (0, [0])，实际 %r' % (dijkstra_with_path([[0]], 0, 0),)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 0, 4) == (7, [0, 1, 2, 3, 4]), '0 到 4 的最短路是 0→1→2→3→4，长度 7，实际 %r' % (dijkstra_with_path(_m, 0, 4),)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 0, 3) == (4, [0, 1, 2, 3]), '0 到 3 的最短路长度是 4、路径 [0, 1, 2, 3]，实际 %r' % (dijkstra_with_path(_m, 0, 3),)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 2, 2) == (0, [2]), '起点等于终点时距离是 0、路径只有它自己，实际 %r' % (dijkstra_with_path(_m, 2, 2),)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 4, 0) == (float('inf'), []), '4 到不了 0，应返回 (inf, [])，实际 %r' % (dijkstra_with_path(_m, 4, 0),)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 0, 9) == (float('inf'), []) and dijkstra_with_path(_m, -1, 2) == (float('inf'), []), 'start / target 越界应返回 (inf, [])，实际 %r / %r' % (dijkstra_with_path(_m, 0, 9), dijkstra_with_path(_m, -1, 2))",
            "assert dijkstra_with_path([[0, 1, 10], [INF, 0, 1], [INF, INF, 0]], 0, 2) == (2, [0, 1, 2]), '绕一跳（1 + 1 = 2）比直达（10）更短，路径应是 [0, 1, 2]，实际 %r' % (dijkstra_with_path([[0, 1, 10], [INF, 0, 1], [INF, INF, 0]], 0, 2),)",
            "_m = [[0, 3, INF, 7, INF], [INF, 0, 1, INF, INF], [INF, INF, 0, 2, 5], [INF, INF, INF, 0, 1], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 0, 3) == (6, [0, 1, 2, 3]), '0 到 3 应走 0→1→2→3（3 + 1 + 2 = 6），比直达 7 更短，实际 %r' % (dijkstra_with_path(_m, 0, 3),)",
            "_m = [[0, 3, INF, 7, INF], [INF, 0, 1, INF, INF], [INF, INF, 0, 2, 5], [INF, INF, INF, 0, 1], [INF, INF, INF, INF, 0]]\n_d, _p = dijkstra_with_path(_m, 0, 4)\nassert _p and _p[0] == 0 and _p[-1] == 4, '路径必须以起点开头、以终点结尾，实际 %r' % (_p,)\nassert _d == 7, '0 到 4 的最短距离应是 7（0→1→2→3→4），实际 %r' % (_d,)",
            "_m = [[0, 3, INF, 7, INF], [INF, 0, 1, INF, INF], [INF, INF, 0, 2, 5], [INF, INF, INF, 0, 1], [INF, INF, INF, INF, 0]]\n_d, _p = dijkstra_with_path(_m, 0, 4)\n_sum = 0\nfor _i in range(len(_p) - 1):\n    assert 0 <= _p[_i] < len(_m) and 0 <= _p[_i + 1] < len(_m), '路径里出现越界顶点：%r' % (_p,)\n    _w = _m[_p[_i]][_p[_i + 1]]\n    assert _w != float('inf') and _w > 0, '路径上 %r 到 %r 之间没有边，不是一条真实路径：%r' % (_p[_i], _p[_i + 1], _p)\n    _sum += _w\nassert _sum == _d, '路径上各边权值之和应等于返回的最短距离，实际和 %r、距离 %r、路径 %r' % (_sum, _d, _p)",
            "_m = [[0, 2, 5, INF, INF], [INF, 0, 1, 4, INF], [INF, INF, 0, 1, INF], [INF, INF, INF, 0, 3], [INF, INF, INF, INF, 0]]\nassert dijkstra_with_path(_m, 0, 1) == (2, [0, 1]) and dijkstra_with_path(_m, 0, 0) == (0, [0]), '直达一条边与「原地不动」两种最短路径都要正确，实际 %r / %r' % (dijkstra_with_path(_m, 0, 1), dijkstra_with_path(_m, 0, 0))",
        ],
        'explanation': (
            '求「一条完整的最短路径」比只求长度多一步：**记住每个顶点是从哪来的**。\n\n'
            '```python\n'
            'if dist[u] + matrix[u][v] < dist[v]:\n'
            '    dist[v] = dist[u] + matrix[u][v]\n'
            '    prev[v] = u                     # 松弛成功时顺便记前驱\n'
            '...\n'
            'path = []\n'
            'node = target\n'
            'while node != -1:                   # 沿前驱一路退回起点\n'
            '    path.append(node)\n'
            '    node = prev[node]\n'
            'path.reverse()                      # 回溯得到的是倒序，要反转\n'
            '```\n\n'
            '`prev[start]` 始终是 -1，所以循环到它自然停下（起点同时也是路径的第一站）。\n\n'
            '**为什么只在「松弛成功」时写 prev？** 因为只有真正把 v 的距离改小了，'
            '才说明「经由 u 到 v」是当前最优的一段，u 才是 v 的正牌前驱。'
            '如果每次扫描都写 prev，会把没用的边也记进去。\n\n'
            '**常见错误**：\n\n'
            '1. 回溯出来忘记 `reverse()`，路径变成 target → start；\n'
            '2. 不可达时还去回溯——`prev` 全是 -1，会得到一个只有 target 的错误路径，'
            '所以要先判 `dist[target] == INF`；\n'
            '3. `start == target` 的边界写错：这时最短路径是空走，返回 `(0, [start])`；\n'
            '4. 越界没拦截，`matrix[9]` 直接 IndexError。\n\n'
            '复杂度：与朴素 Dijkstra 相同，时间 O(n²)、空间 O(n)（多了一个 prev 数组）。'
        ),
        'expected_output': '(7, [0, 1, 2, 3, 4])\n(4, [0, 1, 2, 3])\n(0, [2])\n(inf, [])\n(inf, [])\n(inf, [])',
        'hints': ['松弛成功时同时写 prev[v] = u', '从 target 沿 prev 回溯到 -1，再把路径反转；不可达要先判 inf'],
    },
    {
        'id': 'x823-306',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': 'Dijkstra 堆优化版（边列表 + 优先队列）',
        'difficulty': 3,
        'tags': ['图', '最短路径', 'Dijkstra', '优先队列', '哈希表'],
        'statement': (
            '有向带权图用**边列表** `edges` 表示：每个元素是一个三元组 `(u, v, w)`，'
            '表示从顶点 u 到顶点 v 有一条权值为 `w`（**正整数**）的**有向边**。'
            '顶点名是**字符串**（例如 `\'A\'`、`\'B\'`、`\'City\'`），'
            '同一个顶点对之间可能出现**平行边**（取权值最小的那条），也允许出现自环。\n\n'
            '定义函数 `dijkstra_heap(edges, start)`：返回一个字典，键是 **start 能到达的顶点**，'
            '值是到它的最短距离。\n\n'
            '- start 自己一定在结果里，距离是 0（空边列表也返回 `{start: 0}`）；\n'
            '- **不能到达的顶点不要放进结果**（不是记成 inf，而是根本不出现）。\n\n'
            '要求用**邻接表 + heapq 最小堆**（**不要再用 O(V²) 的朴素写法**）：\n\n'
            '1. 先用一个字典把边列表整理成邻接表（注意：只在 `u` 出现的顶点也要有键，值为空列表）；\n'
            '2. 把 `(0, start)` 压进堆，用字典 `dist` 记录已知的最短距离；\n'
            '3. 每次弹出 `(d, u)`：**如果 d 大于当前已知的 `dist[u]`，说明这条记录已经过期（同一个顶点'
            '  以前进过堆、后来又被更短的距离取代），直接 `continue` 跳过**；\n'
            '4. 否则用 u 的每条出边尝试松弛：`d + w < dist.get(v, inf)` 就更新 `dist[v]` 并把 `(新距离, v)` 压堆。\n\n'
            '这种「允许堆里存在过期记录、弹出时再判断」的做法叫**惰性删除**，'
            '省去了「修改堆中元素」的麻烦。时间 O(E log V)。\n\n'
            '最后打印经典例子（A→B 1、A→C 4、B→C 2、B→D 6、C→D 3）从 A 出发的结果、'
            '只有反向边时从 B 出发的结果、三元环的结果、平行边取最小的结果、空边列表的结果。'
        ),
        'starter_code': 'import heapq\n\ndef dijkstra_heap(edges, start):\n    adj = {}\n    # 1. 建邻接表，注意 v 也要有键\n    dist = {start: 0}\n    heap = [(0, start)]\n    # 2. 弹出时跳过过期记录，否则松弛 u 的每条出边\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def dijkstra_heap(edges, start):\n"
            "    adj = {}\n"
            "    for u, v, w in edges:\n"
            "        adj.setdefault(u, []).append((v, w))\n"
            "        adj.setdefault(v, [])\n"
            "    INF = float('inf')\n"
            "    dist = {start: 0}\n"
            "    heap = [(0, start)]\n"
            "    while heap:\n"
            "        d, u = heapq.heappop(heap)\n"
            "        if d > dist.get(u, INF):\n"
            "            continue\n"
            "        for v, w in adj.get(u, []):\n"
            "            nd = d + w\n"
            "            if nd < dist.get(v, INF):\n"
            "                dist[v] = nd\n"
            "                heapq.heappush(heap, (nd, v))\n"
            "    return dist\n"
            "\n"
            "print(dijkstra_heap([('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 6), ('C', 'D', 3)], 'A'))\n"
            "print(dijkstra_heap([('A', 'B', 2)], 'B'))\n"
            "print(dijkstra_heap([('A', 'B', 1), ('B', 'C', 1), ('C', 'A', 1)], 'A'))\n"
            "print(dijkstra_heap([('A', 'B', 5), ('A', 'B', 2)], 'A'))\n"
            "print(dijkstra_heap([], 'A'))\n"
        ),
        'checks': [
            "assert dijkstra_heap([], 'A') == {'A': 0}, '空边列表应返回 {start: 0}，实际 %r' % (dijkstra_heap([], 'A'),)",
            "assert dijkstra_heap([('A', 'B', 5)], 'A') == {'A': 0, 'B': 5}, '一条边的结果应是 {A: 0, B: 5}，实际 %r' % (dijkstra_heap([('A', 'B', 5)], 'A'),)",
            "_e = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 6), ('C', 'D', 3)]\nassert dijkstra_heap(_e, 'A') == {'A': 0, 'B': 1, 'C': 3, 'D': 6}, '经典例子应是 {A: 0, B: 1, C: 3, D: 6}，实际 %r' % (dijkstra_heap(_e, 'A'),)",
            "assert dijkstra_heap([('A', 'B', 2)], 'B') == {'B': 0}, '有向图 B 到不了 A：结果里只能有 B 自己，实际 %r' % (dijkstra_heap([('A', 'B', 2)], 'B'),)",
            "assert dijkstra_heap([('A', 'B', 1), ('B', 'C', 1), ('C', 'A', 1)], 'A') == {'A': 0, 'B': 1, 'C': 2}, '三元环从 A 出发应是 A=0、B=1、C=2（回到 A 不会更短），实际 %r' % (dijkstra_heap([('A', 'B', 1), ('B', 'C', 1), ('C', 'A', 1)], 'A'),)",
            "assert dijkstra_heap([('A', 'B', 5), ('A', 'B', 2)], 'A') == {'A': 0, 'B': 2}, '平行边要取权值最小的那条（2），实际 %r' % (dijkstra_heap([('A', 'B', 5), ('A', 'B', 2)], 'A'),)",
            "assert dijkstra_heap([('A', 'B', 1), ('B', 'C', 1), ('A', 'C', 5)], 'A') == {'A': 0, 'B': 1, 'C': 2}, '两跳（1 + 1）比直达（5）更短，实际 %r' % (dijkstra_heap([('A', 'B', 1), ('B', 'C', 1), ('A', 'C', 5)], 'A'),)",
            "_e = [('A', 'B', 3), ('C', 'D', 4)]\n_r = dijkstra_heap(_e, 'A')\nassert _r == {'A': 0, 'B': 3}, '不可达的 C、D 不能出现在结果里，实际 %r' % (_r,)",
            "_e = [('A', 'A', 1), ('A', 'B', 2)]\nassert dijkstra_heap(_e, 'A') == {'A': 0, 'B': 2}, '自环不会让起点到自己的距离变成 1，实际 %r' % (dijkstra_heap(_e, 'A'),)",
            "_e = [('A', 'B', 10), ('A', 'C', 1), ('C', 'B', 1)]\nassert dijkstra_heap(_e, 'A') == {'A': 0, 'B': 2, 'C': 1}, '后发现的更短路径要能覆盖先前的 dist（B 最终是 2），实际 %r' % (dijkstra_heap(_e, 'A'),)",
            "_e = [('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3), ('A', 'D', 100)]\nassert dijkstra_heap(_e, 'A')['D'] == 6, 'A→B→C→D 总长 6 比直达 100 更短，实际 %r' % (dijkstra_heap(_e, 'A')['D'],)",
            "_e = [('A', 'B', 3), ('B', 'A', 3), ('B', 'C', 4)]\n_r = dijkstra_heap(_e, 'B')\nassert _r.get('A') == 3 and _r.get('C') == 4, '双向边情况下从 B 出发应是 A=3、C=4，实际 %r' % (_r,)",
            "_big = [('v%d' % _i, 'v%d' % (_i + 1), 1) for _i in range(1000)]\n_r = dijkstra_heap(_big, 'v0')\nassert len(_r) == 1001 and _r['v1000'] == 1000, '1000 条边的链应能一路量到 v1000（距离 1000），实际 %r / %r' % (len(_r), _r.get('v1000'))",
        ],
        'explanation': (
            '朴素 Dijkstra 的瓶颈在「每轮花 O(V) 找最小」，一共 n 轮就是 O(V²)。'
            '用**优先队列**代替这层扫描，就能做到 O(E log V)。\n\n'
            '```python\n'
            'heap = [(0, start)]\n'
            'while heap:\n'
            '    d, u = heapq.heappop(heap)\n'
            '    if d > dist.get(u, INF):\n'
            '        continue                    # 过期记录，跳过\n'
            '    for v, w in adj.get(u, []):\n'
            '        nd = d + w\n'
            '        if nd < dist.get(v, INF):\n'
            '            dist[v] = nd\n'
            '            heapq.heappush(heap, (nd, v))\n'
            '```\n\n'
            '**为什么可以「不过期删除」？** `heapq` 只能弹最小值，不能就地改某个元素，'
            '所以改进距离时干脆**再压一份新的**。旧记录留在堆里没关系：'
            '它弹出来时 `d` 一定大于现在的 `dist[u]`，被 `continue` 丢掉。'
            '每个顶点最多被压入「入度」次，堆里的记录数 O(E)。\n\n'
            '**和其它算法对比**：\n\n'
            '- 无权图（或每步代价相同）用 BFS 就够，O(V + E)；\n'
            '- 非负权单源最短路：稀疏图用堆优化 Dijkstra，稠密图用朴素 O(V²) 反而更快（常数小）；\n'
            '- 多源最短路用 Floyd，O(V³)。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记 `setdefault(v, [])`，`adj.get(u, [])` 查不到起点或只出现一次的顶点；\n'
            '2. 不判过期记录，同一个顶点被反复松弛，复杂度退化；\n'
            '3. 把不可达顶点也塞进结果（题面要求它们不出现）；\n'
            '4. 用 `dist.get(v, 0)` 当初始值——那会让所有距离都变成 0 或负数，必须用 inf。\n\n'
            '复杂度：时间 O(E log E)，空间 O(V + E)。'
        ),
        'expected_output': "{'A': 0, 'B': 1, 'C': 3, 'D': 6}\n{'B': 0}\n{'A': 0, 'B': 1, 'C': 2}\n{'A': 0, 'B': 2}\n{'A': 0}",
        'hints': ['先把边列表整理成邻接表，注意每个出现过的顶点都要有键', '弹出时用 if d > dist.get(u, inf): continue 跳过过期记录'],
    },
    {
        'id': 'x823-307',
        'track': 'algorithm',
        'chapter_id': 145,
        'chapter_title': '823·图算法强化',
        'topic': '823·图算法强化',
        'title': 'Prim 算法求最小生成树（邻接矩阵 O(n²)）',
        'difficulty': 2,
        'tags': ['图', '最小生成树', 'Prim', '贪心'],
        'statement': (
            '带权**无向**图用 n × n 的**邻接矩阵** `matrix` 表示：`matrix[i][j]` 是边 (i, j) 的权值'
            '（**正整数**），无边写 `float(\'inf\')`，对角线为 0；矩阵是**对称**的。\n\n'
            '定义函数 `prim_mst(matrix)`：返回**最小生成树各边权值之和**（一个整数）。\n\n'
            '- 图**不连通**（无法生成树）时返回 `float(\'inf\')`；\n'
            '- `len(matrix) <= 1`（空图或只有一个顶点）时返回 0（不需要任何边）。\n\n'
            '要求写 **O(n²) 朴素 Prim**（不要排序、不要用堆）：\n\n'
            '- 维护 `dist[v]` 表示「顶点 v 连到**已经选中的顶点集合**的最小边权」；'
            '一开始只有 `dist[0] = 0`，其余为 inf；\n'
            '- 一共做 n 轮：每轮在**还没选入**的顶点里挑 `dist` 最小的 u，'
            '若最小的是 inf 说明图不连通、直接返回 inf；\n'
            '- 把 `dist[u]` 累加进答案，把 u 标记为已选入，'
            '再用 u 与其它未选顶点之间的边去更新它们的 `dist`（取较小值）；\n'
            '- 从哪个顶点开始长树，得到的总权值都一样，本题统一从顶点 0 开始。\n\n'
            '时间 O(n²)、空间 O(n)。\n\n'
            '最后打印经典 4 顶点例子（0-1 权 1、0-2 权 4、0-3 权 3、1-2 权 2、2-3 权 5）的总权值、'
            '三角形（0-1 权 1、1-2 权 3、0-2 权 2）的总权值、'
            '不连通例子（两个顶点之间无边）的结果、空矩阵和单顶点矩阵的结果。'
        ),
        'starter_code': 'INF = float(\'inf\')\n\ndef prim_mst(matrix):\n    n = len(matrix)\n    if n <= 1:\n        return 0\n    used = [False] * n\n    dist = [INF] * n\n    dist[0] = 0\n    total = 0\n    # 每轮挑一个未选入且 dist 最小的顶点，累加 dist[u] 并更新其它顶点的 dist\n    pass\n',
        'solution': (
            "INF = float('inf')\n"
            "\n"
            "def prim_mst(matrix):\n"
            "    n = len(matrix)\n"
            "    if n <= 1:\n"
            "        return 0\n"
            "    used = [False] * n\n"
            "    dist = [INF] * n\n"
            "    dist[0] = 0\n"
            "    total = 0\n"
            "    for _ in range(n):\n"
            "        u = -1\n"
            "        best = INF\n"
            "        for i in range(n):\n"
            "            if not used[i] and dist[i] < best:\n"
            "                best = dist[i]\n"
            "                u = i\n"
            "        if u == -1:\n"
            "            return INF\n"
            "        used[u] = True\n"
            "        total += best\n"
            "        for v in range(n):\n"
            "            if not used[v] and matrix[u][v] != INF and matrix[u][v] < dist[v]:\n"
            "                dist[v] = matrix[u][v]\n"
            "    return total\n"
            "\n"
            "m = [[0, 1, 4, 3],\n"
            "     [1, 0, 2, INF],\n"
            "     [4, 2, 0, 5],\n"
            "     [3, INF, 5, 0]]\n"
            "print(prim_mst(m))\n"
            "print(prim_mst([[0, 1, 2], [1, 0, 3], [2, 3, 0]]))\n"
            "print(prim_mst([[0, INF], [INF, 0]]))\n"
            "print(prim_mst([]))\n"
            "print(prim_mst([[0]]))\n"
        ),
        'checks': [
            "assert prim_mst([]) == 0 and prim_mst([[0]]) == 0, '空矩阵和单顶点矩阵都不需要边，应返回 0，实际 %r / %r' % (prim_mst([]), prim_mst([[0]]))",
            "assert prim_mst([[0, INF], [INF, 0]]) == float('inf'), '两个顶点之间没有边时图不连通，应返回 inf，实际 %r' % (prim_mst([[0, INF], [INF, 0]]),)",
            "assert prim_mst([[0, 7], [7, 0]]) == 7, '两个顶点一条边时生成树就是这条边，实际 %r' % (prim_mst([[0, 7], [7, 0]]),)",
            "_m = [[0, 1, 4, 3], [1, 0, 2, INF], [4, 2, 0, 5], [3, INF, 5, 0]]\nassert prim_mst(_m) == 6, '经典例子应选 (0,1) 权 1、(1,2) 权 2、(0,3) 权 3，总权值 6，实际 %r' % (prim_mst(_m),)",
            "assert prim_mst([[0, 1, 2], [1, 0, 3], [2, 3, 0]]) == 3, '三角形里挑两条较小的边：1 + 2 = 3，实际 %r' % (prim_mst([[0, 1, 2], [1, 0, 3], [2, 3, 0]]),)",
            "assert prim_mst([[0, 10, 1], [10, 0, 1], [1, 1, 0]]) == 2, '直达边权 10 不该被选：用两条权 1 的边，实际 %r' % (prim_mst([[0, 10, 1], [10, 0, 1], [1, 1, 0]]),)",
            "_k4 = [[0 if _i == _j else 1 for _j in range(4)] for _i in range(4)]\nassert prim_mst(_k4) == 3, '4 个顶点两两权值为 1 的完全图，生成树要 3 条边，总权值 3，实际 %r' % (prim_mst(_k4),)",
            "_m = [[0, 6, 1, 5, INF, INF], [6, 0, 5, INF, 3, INF], [1, 5, 0, 5, 6, 4], [5, INF, 5, 0, INF, 2], [INF, 3, 6, INF, 0, 6], [INF, INF, 4, 2, 6, 0]]\nassert prim_mst(_m) == 15, '6 个顶点的大例子最小生成树总权值是 15，实际 %r' % (prim_mst(_m),)",
            "_m = [[0, 5, INF, 5], [5, 0, INF, INF], [INF, INF, 0, INF], [5, INF, INF, 0]]\nassert prim_mst(_m) == float('inf'), '顶点 2 与其它顶点都没有边，图不连通应返回 inf，实际 %r' % (prim_mst(_m),)",
            "_m = [[0, 1, 4, 3], [1, 0, 2, INF], [4, 2, 0, 5], [3, INF, 5, 0]]\n_copy = [_row[:] for _row in _m]\nprim_mst(_m)\nassert _m == _copy, '函数不应修改传入的邻接矩阵，实际 %r' % (_m,)",
            "_n = 50\n_m = [[0 if _i == _j else (2 if abs(_i - _j) == 1 else INF) for _j in range(_n)] for _i in range(_n)]\nassert prim_mst(_m) == 98, '50 个顶点的链每段权 2，生成树只能用这 49 条边，总权值 98，实际 %r' % (prim_mst(_m),)",
            "_n = 50\n_m = [[0 if _i == _j else (2 if abs(_i - _j) == 1 else (1 if abs(_i - _j) == 2 else INF)) for _j in range(_n)] for _i in range(_n)]\nassert prim_mst(_m) == 50, '这张图还有「跨一格、权 1」的边：48 条跨格边配 1 条相邻边才能连通，总权值 50，实际 %r' % (prim_mst(_m),)",
        ],
        'explanation': (
            'Prim 的思路是「**让一棵树慢慢长大**」：每次从「树内」连到「树外」的所有边里，'
            '挑一条权值最小的（这就是贪心选择），把那个顶点拉进树里，直到所有顶点都在树上。\n\n'
            '```python\n'
            'for _ in range(n):\n'
            '    u = -1; best = INF\n'
            '    for i in range(n):                 # 挑「离树最近」的树外顶点\n'
            '        if not used[i] and dist[i] < best:\n'
            '            best = dist[i]; u = i\n'
            '    if u == -1:\n'
            '        return INF                     # 树外顶点全都不可达：图不连通\n'
            '    used[u] = True\n'
            '    total += best\n'
            '    for v in range(n):                 # 用 u 更新树外顶点的最近距离\n'
            '        if not used[v] and matrix[u][v] != INF and matrix[u][v] < dist[v]:\n'
            '            dist[v] = matrix[u][v]\n'
            '```\n\n'
            '注意 Prim 的 `dist[v]` 和 Dijkstra 的 `dist[v]` **含义不同**：\n\n'
            '- Prim：v 到**已选集合**的一条边的权值（只加最后一段）；\n'
            '- Dijkstra：起点到 v 的**整条路径长度**（要累加 `dist[u] + w`）。\n\n'
            '把两者写混是本题最典型的错误——Prim 里写成 `dist[u] + matrix[u][v]` 就变成最短路了。\n\n'
            '**常见错误**：\n\n'
            '1. 忘了判断 `u == -1`（图不连通时 `best` 一直是 inf，`total` 会被 inf 污染）；\n'
            '2. 更新 `dist` 时没判 `used[v]`，把已经进树的顶点又改小了；\n'
            '3. `dist[v]` 写成了 `dist[u] + matrix[u][v]`；\n'
            '4. 用 Kruskal 的思路（按全局边权排序）来写 Prim——那是另一套算法。\n\n'
            '复杂度：时间 O(n²)（稠密图优于 Kruskal 的 O(E log E)），空间 O(n)。'
        ),
        'expected_output': '6\n3\ninf\n0\n0',
        'hints': ['每轮挑「未选入且 dist 最小」的顶点，把它的 dist 累加进答案', 'Prim 的更新是 dist[v] = matrix[u][v]（只取一条边），不是 dist[u] + matrix[u][v]'],
    },
    # __APPEND_MARKER__
]
