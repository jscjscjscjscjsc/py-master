"""题库 · 操作系统考试题库（专题 135–138，老师整理的 11 道操作系统大题）。

写法约定与 qbank_408.py / qbank_osa.py / qbank_osb.py 保持一致：

- statement 面向学生，先给老师的原题表述，再补全「要定义什么名字的函数」以及
  输入输出的类型与格式；所有数据（进程表、空闲分区表、页面引用串、磁柱序列、
  资源矩阵）都在题面里给死，不让学生猜。
- checks 只断言题面要求的东西，每条断言带中文提示，并覆盖空列表、单元素、
  CPU 空闲、全部同时到达、越界、表满等边界；断言里可以用 `_out` 与 `_src`。
- 参考答案必须能通过自己那套断言（改完题库要重跑 tools/verify_qbank.py）。

操作系统是概念课，判题却只能判「跑出来的代码」，所以这份题库的编排口径是
**把每个概念翻译成一段可执行的模拟 / 算法**：题面给出算法规则与数据，学生写函数，
断言按定义核对结果。凡是教材上有多种口径的地方都在题面里写死（SCAN 只走到该方向
最远的请求而不是磁盘端点、RR 运行期间到达的进程先入队、位示图 0 空闲 1 占用、
安全序列按「每轮从下标 0 起找第一个可满足进程」扫描），避免「学生写对了却被判错」。

专题划分（与老师题库的四章一一对应）：

    135 操作系统·进程调度          题 30 先来先服务 FCFS、题 31 短作业优先 SJF（非抢占）、
                                   题 32 时间片轮转 RR
    136 操作系统·内存管理          题 33 首次适应 FF、题 34 最佳适应 BF、
                                   题 35 FIFO 页面置换、题 36 LRU 最近最久未使用置换
    137 操作系统·文件与磁盘        题 37 位示图分配 / 回收、题 38 FCFS 磁盘调度、
                                   题 39 SCAN 电梯调度
    138 操作系统·死锁与银行家算法  题 40 银行家算法安全性检测

难度按老师标注的星级取（⭐ = 1、⭐⭐ = 2）；银行家算法（题 40）虽然标 ⭐⭐，
但要自己算 Need 矩阵、再按定义搜索安全序列，是标准的大题做法，定为 3。
"""

QUESTIONS = [
    # ── 专题 135 操作系统·进程调度 ─────────────────────────
    {
        'id': 'os-001',
        'track': 'algorithm',
        'chapter_id': 135,
        'chapter_title': '操作系统·进程调度',
        'topic': '操作系统·进程调度',
        'title': 'FCFS 先来先服务调度（周转时间与带权周转时间）',
        'difficulty': 1,
        'tags': ['调度', 'FCFS', '周转时间', '带权周转时间'],
        'statement': (
            '**题 30 · 先来先服务 FCFS 调度**\n\n'
            '考点：FCFS 调度算法、周转时间计算。\n\n'
            '老师的原题：输入进程列表（进程名、到达时间、服务时间），实现 FCFS 调度，'
            '计算每个进程的周转时间、带权周转时间，输出平均周转时间。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '先来先服务：按进程到达的先后顺序排队，谁先到谁先用 CPU；'
            '一个进程一旦上 CPU 就一直运行到结束（非抢占）。\n\n'
            '定义函数 `fcfs(procs)`：\n\n'
            '- 参数 `procs` 是 `(进程名, 到达时间, 服务时间)` 三元组组成的列表，'
            '**不保证按到达时间排好序**，进程名是字符串；\n'
            '- 返回一个字典，含 6 个键：\n'
            '  - `order`：进程的执行顺序（进程名列表）；\n'
            '  - `finish`：`{进程名: 完成时间}`；\n'
            '  - `turnaround`：`{进程名: 周转时间}`，周转时间 = 完成时间 − 到达时间；\n'
            '  - `weighted`：`{进程名: 带权周转时间}`，带权周转时间 = 周转时间 ÷ 服务时间；\n'
            '  - `avg_turnaround`：平均周转时间（float）；\n'
            '  - `avg_weighted`：平均带权周转时间（float）。\n\n'
            '规则（写死，避免歧义）：\n\n'
            '1. 按到达时间升序调度；**到达时间相同**时按进程名字典序（`sorted` 默认的字符串比较）；\n'
            '2. CPU 可能空闲：下一个进程还没到达时，先让 `now = max(now, 到达时间)`；\n'
            '3. 空列表不许除零：返回 `order == []`、`avg_turnaround == 0.0`、`avg_weighted == 0.0`。\n\n'
            '参考数据（本题主数据）：`[(\'P1\', 0, 3), (\'P2\', 1, 5), (\'P3\', 2, 2), (\'P4\', 4, 4)]`：\n\n'
            '- 执行顺序 P1 → P2 → P3 → P4；P1 从 0 跑到 3，P2 虽然 1 就到了但只能等，'
            '3 开始 8 结束，接着 P3 跑到 10、P4 跑到 14；\n'
            '- 完成时间 3、8、10、14，平均周转时间 = (3 + 7 + 8 + 10) / 4 = 7.0；\n'
            '- 带权周转时间 3/3、7/5、8/2、10/4 = 1.0、1.4、4.0、2.5。\n\n'
            '最后打印：主数据的 `order`、`finish`、`turnaround`、'
            '`round(avg_turnaround, 4)`、`round(avg_weighted, 4)`；'
            '再对 `[(\'B\', 6, 3), (\'A\', 2, 2)]`（输入乱序、中间 CPU 空闲）'
            '打印 `order` 与 `finish`。'
        ),
        'starter_code': (
            "def fcfs(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    seq = []\n"
            "    for pid, arrival, burst in order:\n"
            "        # now = max(now, arrival) 处理 CPU 空闲，再 now += burst\n"
            "        pass\n"
            "    return {\n"
            "        'order': seq,\n"
            "        'finish': finish,\n"
            "        'turnaround': {},      # {进程名: 完成时间 - 到达时间}\n"
            "        'weighted': {},        # {进程名: 周转时间 / 服务时间}\n"
            "        'avg_turnaround': 0.0,\n"
            "        'avg_weighted': 0.0,\n"
            "    }\n"
        ),
        'solution': (
            "def fcfs(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    seq = []\n"
            "    for pid, arrival, burst in order:\n"
            "        now = max(now, arrival)\n"
            "        now += burst\n"
            "        finish[pid] = now\n"
            "        seq.append(pid)\n"
            "    turnaround = {}\n"
            "    weighted = {}\n"
            "    for pid, arrival, burst in order:\n"
            "        turnaround[pid] = finish[pid] - arrival\n"
            "        weighted[pid] = turnaround[pid] / burst\n"
            "    n = len(order)\n"
            "    return {\n"
            "        'order': seq,\n"
            "        'finish': finish,\n"
            "        'turnaround': turnaround,\n"
            "        'weighted': weighted,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "        'avg_weighted': sum(weighted.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_turnaround'], 4))\n"
            "print(round(r1['avg_weighted'], 4))\n"
            "r2 = fcfs([('B', 6, 3), ('A', 2, 2)])\n"
            "print(r2['order'])\n"
            "print(r2['finish'])\n"
        ),
        'checks': [
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert _r['order'] == ['P1', 'P2', 'P3', 'P4'], 'FCFS 的执行顺序就是到达顺序，实际 %r' % (_r['order'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert _r['finish'] == {'P1': 3, 'P2': 8, 'P3': 10, 'P4': 14}, '完成时间应是 P1=3、P2=8、P3=10、P4=14，实际 %r' % (_r['finish'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert _r['turnaround'] == {'P1': 3, 'P2': 7, 'P3': 8, 'P4': 10}, '周转时间 = 完成时间 - 到达时间，实际 %r' % (_r['turnaround'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert round(_r['avg_turnaround'], 4) == 7.0, '平均周转时间 = (3+7+8+10)/4 = 7.0，实际 %r' % (_r['avg_turnaround'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert {k: round(v, 4) for k, v in _r['weighted'].items()} == {'P1': 1.0, 'P2': 1.4, 'P3': 4.0, 'P4': 2.5}, '带权周转时间应是 1.0 / 1.4 / 4.0 / 2.5，实际 %r' % (_r['weighted'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert round(_r['avg_weighted'], 4) == 2.225, '平均带权周转时间 = (1.0+1.4+4.0+2.5)/4 = 2.225，实际 %r' % (_r['avg_weighted'],)",
            "_r = fcfs([('B', 6, 3), ('A', 2, 2)])\nassert _r['order'] == ['A', 'B'], '输入乱序时要先按到达时间排好再调度（A 先），实际 %r' % (_r['order'],)",
            "_r = fcfs([('B', 6, 3), ('A', 2, 2)])\nassert _r['finish'] == {'A': 4, 'B': 9}, 'A 在 2 到达、跑到 4；B 要到 6 才到达，所以 6 开始 9 结束（CPU 空闲 2 个时间单位），实际 %r' % (_r['finish'],)",
            "_r = fcfs([('B', 0, 2), ('A', 0, 3)])\nassert _r['order'] == ['A', 'B'], '同时到达时按进程名字典序，A 先 B 后，实际 %r' % (_r['order'],)",
            "_r = fcfs([])\nassert _r['order'] == [] and _r['avg_turnaround'] == 0.0 and _r['avg_weighted'] == 0.0, '空列表不能除零：order 为空、两个平均值都是 0.0，实际 %r' % (_r,)",
            "_r = fcfs([('X', 3, 4)])\nassert _r['finish'] == {'X': 7} and _r['turnaround'] == {'X': 4} and _r['weighted'] == {'X': 1.0}, '单进程：3 到达、7 结束、周转 4、带权 1.0，实际 %r / %r / %r' % (_r['finish'], _r['turnaround'], _r['weighted'])",
            "_r = fcfs([('P1', 0, 4), ('P2', 100, 1)])\nassert _r['finish'] == {'P1': 4, 'P2': 101}, '长空闲期也要正确推进时间（P2 到 100 才开始运行），实际 %r' % (_r['finish'],)",
            "_ps = [('P1', 0, 3), ('P2', 1, 5)]\n_copy = list(_ps)\nfcfs(_ps)\nassert _ps == _copy, 'fcfs 只能读进程表，不能改动传入的列表，实际 %r' % (_ps,)",
            "_r = fcfs([('P1', 0, 3), ('P2', 1, 5), ('P3', 2, 2), ('P4', 4, 4)])\nassert abs(sum(_r['weighted'].values()) / 4 - _r['avg_weighted']) < 1e-9 and abs(sum(_r['turnaround'].values()) / 4 - _r['avg_turnaround']) < 1e-9, '两个平均值必须分别是各自字典里各项的平均，实际 %r / %r' % (_r['avg_turnaround'], _r['avg_weighted'])",
        ],
        'explanation': (
            'FCFS 的模拟只有一个循环，但两个细节决定成败：\n\n'
            '```python\n'
            'for pid, arrival, burst in order:\n'
            '    now = max(now, arrival)     # CPU 空闲就等到进程到达\n'
            '    now += burst\n'
            '    finish[pid] = now\n'
            '```\n\n'
            '`now = max(now, arrival)` 就是「CPU 空闲」的处理：如果 `now` 已经超过 '
            '`arrival`（前一个进程还没跑完），就接着跑；否则要等到 `arrival`。'
            '漏掉这一句，后面所有完成时间都会偏小。\n\n'
            '**四个时间指标一定要分清**（考研最爱在这里做文章）：\n\n'
            '- 周转时间 = 完成时间 − 到达时间（在系统里一共待了多久）；\n'
            '- 带权周转时间 = 周转时间 ÷ 服务时间（长作业跑得久是正常的，带权之后才公平）；\n'
            '- 等待时间 = 周转时间 − 服务时间；\n'
            '- 响应时间 = 首次获得 CPU 的时刻 − 提交时刻（分时系统更关心它）。\n\n'
            '**手算一遍主数据**：P1 先到先跑，0→3 结束，周转 3、带权 1.0；'
            'P2 在 3 开始跑 5 个时间单位，8 结束，周转 8−1=7、带权 7/5=1.4；'
            'P3 在 8→10 结束，周转 10−2=8、带权 8/2=4.0；P4 在 10→14 结束，'
            '周转 14−4=10、带权 10/4=2.5。平均周转时间 (3+7+8+10)/4 = 7.0。\n\n'
            '**FCFS 的缺点**：对短作业不利——前面一个大作业在跑，后面的短作业都得干等，'
            '带权周转时间会大得离谱（本题 P3 的 4.0 就是被 P1、P2 拖出来的）。'
            '这正是 SJF 要解决的问题，也是「护航效应」的由来。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记 `now = max(now, arrival)`，把「CPU 空闲」当成「提前开始跑」；\n'
            '2. 忘记先按到达时间排序（题面明确说输入可能是乱序的）；\n'
            '3. 平均周转时间写成整除或忘记处理空列表导致 `ZeroDivisionError`。\n\n'
            '复杂度：时间 O(n log n)（排序）、空间 O(n)。'
        ),
        'expected_output': "['P1', 'P2', 'P3', 'P4']\n{'P1': 3, 'P2': 8, 'P3': 10, 'P4': 14}\n{'P1': 3, 'P2': 7, 'P3': 8, 'P4': 10}\n7.0\n2.225\n['A', 'B']\n{'A': 4, 'B': 9}",
        'hints': [
            'now = max(now, arrival) 处理 CPU 空闲，然后 now += burst 就是完成时间',
            '周转时间 = 完成 − 到达；带权周转 = 周转 ÷ 服务时间；平均值是各进程的平均',
        ],
    },
    {
        'id': 'os-002',
        'track': 'algorithm',
        'chapter_id': 135,
        'chapter_title': '操作系统·进程调度',
        'topic': '操作系统·进程调度',
        'title': 'SJF 短作业优先（非抢占）调度',
        'difficulty': 1,
        'tags': ['调度', 'SJF', '非抢占', '周转时间'],
        'statement': (
            '**题 31 · 短作业优先 SJF 调度**\n\n'
            '考点：SJF 调度、平均周转时间最小。\n\n'
            '老师的原题：实现**非抢占式**短作业优先调度算法，输出调度顺序和平均周转时间。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '短作业优先：每次要调度时，从「已经到达而且还没结束」的进程里挑**服务时间最短**的'
            '运行到结束。本题是**非抢占式**：进程一旦开跑就不能被后来到达的短作业踢下去。\n\n'
            '定义函数 `sjf(procs)`，参数与返回值与第 30 题（FCFS）**完全一样**：\n\n'
            '- 参数 `procs` 是 `(进程名, 到达时间, 服务时间)` 三元组列表；\n'
            '- 返回字典，含 `order`、`finish`、`turnaround`、`weighted`、'
            '`avg_turnaround`、`avg_weighted` 六个键（含义同 FCFS）。\n\n'
            '规则（写死）：\n\n'
            '1. 调度只发生在「CPU 空闲」和「进程结束」这两个时刻：'
            '把此刻所有已到达且未完成的进程作为候选，挑服务时间最短的那个跑完；\n'
            '2. 服务时间相同时，先到达者优先；到达时间也相同则进程名字典序小的优先；\n'
            '3. 候选为空说明 CPU 空闲，把 `now` 推进到「下一个尚未完成进程的最早到达时刻」；\n'
            '4. 空列表不许除零：`order == []`、两个平均值都为 0.0。\n\n'
            '参考数据（本题主数据）：'
            '`[(\'P1\', 0, 6), (\'P2\', 1, 3), (\'P3\', 2, 8), (\'P4\', 3, 2), (\'P5\', 9, 1)]`：\n\n'
            '- 0 时刻只有 P1 到达，只能先跑 P1（0→6）；\n'
            '- 6 时刻 P2、P3、P4 都已到达，P4 最短（2），跑 6→8；\n'
            '- 8 时刻 P2（3）比 P3（8）短，跑 8→11；\n'
            '- 11 时刻要重新挑一次：P5 在 9 已经到达、只要 1 个时间单位，比 P3 短，'
            '所以 P5 跑 11→12（这不是抢占，P2 已经跑完了）；\n'
            '- 最后 P3 跑 12→20；\n'
            '- 顺序 P1 → P4 → P2 → P5 → P3，平均周转时间 8.4。\n\n'
            '最后打印：主数据的 `order`、`finish`、`turnaround`、'
            '`round(avg_turnaround, 4)`、`round(avg_weighted, 4)`；'
            '再对 `[(\'P1\', 0, 6), (\'P2\', 1, 1)]` 与 `[(\'A\', 5, 2), (\'B\', 1, 3)]` '
            '各打印一行 `order` 和 `finish`。'
        ),
        'starter_code': (
            "def sjf(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    seq = []\n"
            "    done = set()\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        # ready 为空就推进 now；否则挑 burst 最小的跑完这一轮\n"
            "        pass\n"
            "    return {\n"
            "        'order': seq,\n"
            "        'finish': finish,\n"
            "        'turnaround': {},\n"
            "        'weighted': {},\n"
            "        'avg_turnaround': 0.0,\n"
            "        'avg_weighted': 0.0,\n"
            "    }\n"
        ),
        'solution': (
            "def sjf(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    seq = []\n"
            "    done = set()\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        if not ready:\n"
            "            now = min(p[1] for p in order if p[0] not in done)\n"
            "            continue\n"
            "        cur = sorted(ready, key=lambda p: (p[2], p[1], str(p[0])))[0]\n"
            "        now += cur[2]\n"
            "        finish[cur[0]] = now\n"
            "        seq.append(cur[0])\n"
            "        done.add(cur[0])\n"
            "    turnaround = {}\n"
            "    weighted = {}\n"
            "    for pid, arrival, burst in order:\n"
            "        turnaround[pid] = finish[pid] - arrival\n"
            "        weighted[pid] = turnaround[pid] / burst\n"
            "    n = len(order)\n"
            "    return {\n"
            "        'order': seq,\n"
            "        'finish': finish,\n"
            "        'turnaround': turnaround,\n"
            "        'weighted': weighted,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "        'avg_weighted': sum(weighted.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_turnaround'], 4))\n"
            "print(round(r1['avg_weighted'], 4))\n"
            "r2 = sjf([('P1', 0, 6), ('P2', 1, 1)])\n"
            "print(r2['order'], r2['finish'])\n"
            "r3 = sjf([('A', 5, 2), ('B', 1, 3)])\n"
            "print(r3['order'], r3['finish'])\n"
        ),
        'checks': [
            "_r = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\nassert _r['order'] == ['P1', 'P4', 'P2', 'P5', 'P3'], 'P1 跑完（6）后先做最短的 P4(2)，再 P2(3)；11 时刻 P5(1) 已在 9 到达且更短，所以先做 P5，最后才是 P3(8)，实际 %r' % (_r['order'],)",
            "_r = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\nassert _r['finish'] == {'P1': 6, 'P4': 8, 'P2': 11, 'P5': 12, 'P3': 20}, '完成时间应是 P1=6、P4=8、P2=11、P5=12、P3=20，实际 %r' % (_r['finish'],)",
            "_r = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\nassert _r['turnaround'] == {'P1': 6, 'P2': 10, 'P3': 18, 'P4': 5, 'P5': 3}, '周转时间应是 6 / 10 / 18 / 5 / 3，实际 %r' % (_r['turnaround'],)",
            "_r = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\nassert round(_r['avg_turnaround'], 4) == 8.4, '平均周转时间 = (6+10+18+5+3)/5 = 8.4，实际 %r' % (_r['avg_turnaround'],)",
            "_r = sjf([('P1', 0, 6), ('P2', 1, 3), ('P3', 2, 8), ('P4', 3, 2), ('P5', 9, 1)])\nassert round(_r['avg_weighted'], 4) == 2.4167, '平均带权周转时间 = (1 + 10/3 + 18/8 + 2.5 + 3)/5 = 2.4167，实际 %r' % (_r['avg_weighted'],)",
            "_r = sjf([('P1', 0, 6), ('P2', 1, 1)])\nassert _r['order'] == ['P1', 'P2'] and _r['finish'] == {'P1': 6, 'P2': 7}, 'P2 虽然很短，但 P1 已经开跑，非抢占式不能把它踢下去（P2 只能等 P1 跑完），实际 %r / %r' % (_r['order'], _r['finish'])",
            "_r = sjf([('A', 5, 2), ('B', 1, 3)])\nassert _r['order'] == ['B', 'A'] and _r['finish'] == {'B': 4, 'A': 7}, '开始时要先把 now 推进到最早到达时刻 1：B 跑 1→4，A 等到 5 跑 5→7，实际 %r / %r' % (_r['order'], _r['finish'])",
            "_r = sjf([('A', 0, 5), ('B', 0, 2), ('C', 0, 4)])\nassert _r['order'] == ['B', 'C', 'A'], '全部同时到达时就是「短的先跑」：B(2) → C(4) → A(5)，实际 %r' % (_r['order'],)",
            "_r = sjf([('A', 0, 3), ('B', 2, 3), ('C', 1, 3)])\nassert _r['order'] == ['A', 'C', 'B'], '服务时间相同看到达时间（C 比 B 早到），实际 %r' % (_r['order'],)",
            "_r = sjf([('B', 0, 2), ('A', 0, 2)])\nassert _r['order'] == ['A', 'B'], '到达时间与服务时间都相同时按进程名字典序，实际 %r' % (_r['order'],)",
            "_r = sjf([])\nassert _r['order'] == [] and _r['avg_turnaround'] == 0.0 and _r['avg_weighted'] == 0.0, '空列表应返回空的统计结果且不能除零，实际 %r' % (_r,)",
            "_r = sjf([('X', 2, 3)])\nassert _r['finish'] == {'X': 5} and _r['turnaround'] == {'X': 3}, '单进程：2 到达、5 结束、周转 3，实际 %r / %r' % (_r['finish'], _r['turnaround'])",
            "_r = sjf([('A', 0, 4), ('B', 0, 4), ('C', 0, 4)])\nassert _r['finish'] == {'A': 4, 'B': 8, 'C': 12}, '三个一样长的作业按到达时间（都相同则按名字）依次跑，实际 %r' % (_r['finish'],)",
            "_ps = [('P1', 0, 6), ('P2', 1, 3)]\n_copy = list(_ps)\nsjf(_ps)\nassert _ps == _copy, 'sjf 不能改动传入的进程表，实际 %r' % (_ps,)",
        ],
        'explanation': (
            'SJF 的模拟要用「循环挑人」的写法，因为调度点在时间轴上出现多次：\n\n'
            '```python\n'
            'while len(done) < len(order):\n'
            '    ready = [p for p in order if p[1] <= now and p[0] not in done]\n'
            '    if not ready:\n'
            '        now = min(p[1] for p in order if p[0] not in done)   # CPU 空闲\n'
            '        continue\n'
            '    cur = sorted(ready, key=lambda p: (p[2], p[1], str(p[0])))[0]\n'
            '    now += cur[2]\n'
            '    finish[cur[0]] = now\n'
            '    done.add(cur[0])\n'
            '```\n\n'
            '**为什么 ready 为空时要 `continue`？** 因为这时 CPU 空闲，必须先把 `now` 推到'
            '「下一个要到达的进程」的时刻，否则会漏掉后面的调度点（甚至死循环）。\n\n'
            '**手算一遍主数据**：0 时刻只有 P1 到达（P2 要 1 才能到），所以第一段只能跑 P1；'
            '到 6 时刻 P2、P3、P4 都到了，挑最短的 P4(2) 跑 6→8；8 时刻在剩下的 P2(3)、P3(8) 里'
            '挑 P2 跑 8→11；**11 时刻要重新挑一次**——P5 已经在 9 到达且只要 1 个时间单位，'
            '比 P3 短，所以 P5 跑 11→12（这不是抢占：P2 已经运行结束，属于正常的下一次调度）；'
            '最后 P3(8) 跑 12→20。周转时间 6、10、18、5、3，平均 8.4；'
            '带权 1、3.3333、2.25、2.5、3，平均 2.4167。\n\n'
            '**SJF 的性质**（选择题常考）：\n\n'
            '1. 所有进程**同时到达**时，SJF 的平均等待时间 / 平均周转时间最小（可证明是最优的）；\n'
            '2. 它需要预知服务时间，现实里只能估计，所以更像理论基准；\n'
            '3. 对长作业不利，长作业可能一直排在短作业后面（**饥饿**）；\n'
            '4. 抢占版的 SJF 叫 **SRTF**（最短剩余时间优先），本题是非抢占版，'
            '所以后面到达的短作业不能把正在跑的进程踢下去。\n\n'
            '**常见错误**：\n\n'
            '1. 一开始就全局排序（把还没到达的 P4 排到 P1 前面），那就变成了「知道未来的 FCFS」；\n'
            '2. 忘了非抢占——在 P1 运行时被 P2 抢占；\n'
            '3. ready 为空时直接 `now += 1` 硬推时间，遇到大空隙会算错。\n\n'
            '复杂度：时间 O(n² log n)（最坏每轮排一次序）、空间 O(n)；n 很小时完全够用。'
        ),
        'expected_output': "['P1', 'P4', 'P2', 'P5', 'P3']\n{'P1': 6, 'P4': 8, 'P2': 11, 'P5': 12, 'P3': 20}\n{'P1': 6, 'P2': 10, 'P3': 18, 'P4': 5, 'P5': 3}\n8.4\n2.4167\n['P1', 'P2'] {'P1': 6, 'P2': 7}\n['B', 'A'] {'B': 4, 'A': 7}",
        'hints': [
            '每一轮从「已到达且未完成」里挑服务时间最短的跑完，再去下一轮',
            'ready 为空说明 CPU 空闲：now = min(未完成进程的到达时间)，不要硬加 1',
        ],
    },
    {
        'id': 'os-003',
        'track': 'algorithm',
        'chapter_id': 135,
        'chapter_title': '操作系统·进程调度',
        'topic': '操作系统·进程调度',
        'title': '时间片轮转 RR 调度（执行顺序与周转时间）',
        'difficulty': 2,
        'tags': ['调度', '时间片轮转', 'RR', '周转时间', '响应时间'],
        'statement': (
            '**题 32 · 时间片轮转 RR 调度**\n\n'
            '考点：时间片轮转、响应时间（操作系统大题）。\n\n'
            '老师的原题：给定时间片大小，实现时间片轮转调度算法，'
            '输出进程执行顺序、各进程周转时间。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '时间片轮转：就绪进程排成队列，每次让队首进程运行一个时间片；'
            '时间片用完还没结束就回到队尾重新排队。\n\n'
            '定义函数 `rr(procs, quantum)`：\n\n'
            '- `procs` 是 `(进程名, 到达时间, 服务时间)` 列表；`quantum` 是时间片长度（正整数）；\n'
            '- 返回一个字典，含 4 个键：\n'
            '  - `order`：**每个时间片执行了哪个进程**（进程名列表，同一进程会出现多次），'
            '调度顺序；\n'
            '  - `finish`：`{进程名: 完成时间}`；\n'
            '  - `turnaround`：`{进程名: 周转时间}`（= 完成时间 − 到达时间）；\n'
            '  - `avg_turnaround`：平均周转时间（float），空列表返回 0.0。\n\n'
            '调度规则（写死，否则时间轴会差一格）：\n\n'
            '1. 每个时间片，队首进程运行 `min(quantum, 剩余时间)`；\n'
            '2. 进程运行**期间**到达的进程，按到达时间（相同则按名字典序）加入队尾，'
            '**排在被这个时间片挤下来的进程之前**；\n'
            '3. 到达时刻正好等于本时间片结束时刻的进程也算「运行期间到达」，同样先入队；\n'
            '4. 就绪队列为空而还有进程没到达时，CPU 空闲，时间推进到下一个到达时刻'
            '（`now = max(now, 下一个到达时刻)`），到达的进程立刻开始跑（不必等满一个时间片）；\n'
            '5. 同一时刻同时到达的多个进程按进程名字典序入队。\n\n'
            '参考数据（本题主数据）：`[(\'P1\', 0, 5), (\'P2\', 0, 4), (\'P3\', 1, 2)]`，`quantum = 2`：\n\n'
            '- 0 时刻 P1、P2 入队：P1 跑 0→2（剩 3），期间 P3 到达先入队，P1 排到 P3 后面；\n'
            '- P2 跑 2→4（剩 2）；P3 跑 4→6（跑完，完成时间 6）；\n'
            '- P1 跑 6→8（剩 1）；P2 跑 8→10（跑完）；P1 最后跑 10→11；\n'
            '- 执行顺序 P1 P2 P3 P1 P2 P1，平均周转时间 26/3。\n\n'
            '最后打印：主数据的 `order`、`finish`、`turnaround`、`round(avg_turnaround, 4)`；'
            '再对 `[(\'A\', 0, 3), (\'B\', 3, 1)]`（quantum=2，验证 CPU 空闲与「正好在时间片结束时刻到达」）'
            '打印 `order` 与 `finish`；最后打印空列表的结果。'
        ),
        'starter_code': (
            "def rr(procs, quantum):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    n = len(order)\n"
            "    remaining = {p[0]: p[2] for p in order}\n"
            "    now = 0\n"
            "    idx = 0\n"
            "    queue = []\n"
            "    seq = []\n"
            "    finish = {}\n"
            "    # 出队 -> 跑 min(quantum, 剩余) -> 运行期间到达的先入队 -> 没跑完的自己排到最后\n"
            "    pass\n"
        ),
        'solution': (
            "def rr(procs, quantum):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    n = len(order)\n"
            "    remaining = {p[0]: p[2] for p in order}\n"
            "    now = 0\n"
            "    idx = 0\n"
            "    queue = []\n"
            "    seq = []\n"
            "    finish = {}\n"
            "    while idx < n or queue:\n"
            "        if not queue:\n"
            "            now = max(now, order[idx][1])\n"
            "            while idx < n and order[idx][1] <= now:\n"
            "                queue.append(order[idx])\n"
            "                idx += 1\n"
            "        pid, arrival, burst = queue.pop(0)\n"
            "        run = min(quantum, remaining[pid])\n"
            "        now += run\n"
            "        remaining[pid] -= run\n"
            "        while idx < n and order[idx][1] <= now:\n"
            "            queue.append(order[idx])\n"
            "            idx += 1\n"
            "        if remaining[pid] > 0:\n"
            "            queue.append((pid, arrival, burst))\n"
            "        else:\n"
            "            finish[pid] = now\n"
            "        seq.append(pid)\n"
            "    turnaround = {}\n"
            "    for pid, arrival, burst in order:\n"
            "        turnaround[pid] = finish[pid] - arrival\n"
            "    return {\n"
            "        'order': seq,\n"
            "        'finish': finish,\n"
            "        'turnaround': turnaround,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_turnaround'], 4))\n"
            "r2 = rr([('A', 0, 3), ('B', 3, 1)], 2)\n"
            "print(r2['order'])\n"
            "print(r2['finish'])\n"
            "r3 = rr([], 2)\n"
            "print(r3['order'], r3['avg_turnaround'])\n"
        ),
        'checks': [
            "_r = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\nassert _r['order'] == ['P1', 'P2', 'P3', 'P1', 'P2', 'P1'], '执行顺序应是 P1 P2 P3 P1 P2 P1（每个时间片一格），实际 %r' % (_r['order'],)",
            "_r = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\nassert _r['finish'] == {'P3': 6, 'P2': 10, 'P1': 11}, '完成时间应是 P3=6、P2=10、P1=11，实际 %r' % (_r['finish'],)",
            "_r = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\nassert _r['turnaround'] == {'P1': 11, 'P2': 10, 'P3': 5}, '周转时间应是 P1=11、P2=10、P3=5，实际 %r' % (_r['turnaround'],)",
            "_r = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\nassert round(_r['avg_turnaround'], 4) == round(26 / 3, 4), '平均周转时间应是 (11+10+5)/3 = 8.6667，实际 %r' % (_r['avg_turnaround'],)",
            "_r = rr([('P1', 0, 5), ('P2', 0, 4), ('P3', 1, 2)], 2)\nassert len(_r['order']) == 6 and _r['order'].count('P1') == 3 and _r['order'].count('P2') == 2 and _r['order'].count('P3') == 1, '每个进程占 ceil(服务时间/时间片) 个时间片：P1 三段、P2 两段、P3 一段，实际 %r' % (_r['order'],)",
            "_r = rr([('A', 0, 3), ('B', 3, 1)], 2)\nassert _r['order'] == ['A', 'A', 'B'], 'A 先跑满 2 格（剩 1），再跑 1 格到时刻 3 结束；B 正好在 3 到达并立刻开始，实际 %r' % (_r['order'],)",
            "_r = rr([('A', 0, 3), ('B', 3, 1)], 2)\nassert _r['finish'] == {'A': 3, 'B': 4}, 'A 在 3 完成、B 在 4 完成（到达时刻正好等于时间片结束时刻也要立刻入队），实际 %r' % (_r['finish'],)",
            "_r = rr([('P1', 0, 4), ('P2', 1, 4), ('P3', 2, 4)], 10)\nassert _r['order'] == ['P1', 'P2', 'P3'] and _r['finish'] == {'P1': 4, 'P2': 8, 'P3': 12}, '时间片比服务时间还大时 RR 退化成 FCFS：各跑一段、依次结束，实际 %r / %r' % (_r['order'], _r['finish'])",
            "_r = rr([('X', 0, 5)], 2)\nassert _r['order'] == ['X', 'X', 'X'] and _r['finish'] == {'X': 5}, '单进程连续跑三段，最后一段不足一个时间片（2 + 2 + 1），实际 %r / %r' % (_r['order'], _r['finish'])",
            "_r = rr([('A', 0, 2), ('B', 0, 2), ('C', 0, 2)], 1)\nassert _r['finish'] == {'A': 4, 'B': 5, 'C': 6}, '三人同时到达、时间片为 1：A 在 0-1 与 3-4 各跑一格（4 结束）、B 在 1-2 与 4-5、C 在 2-3 与 5-6，实际 %r' % (_r['finish'],)",
            "_r = rr([('A', 0, 1), ('B', 4, 1)], 2)\nassert _r['order'] == ['A', 'B'] and _r['finish'] == {'A': 1, 'B': 5}, '中途 CPU 空闲：A 跑完（时刻 1）后等到 4 才跑 B，实际 %r / %r' % (_r['order'], _r['finish'])",
            "_r = rr([], 2)\nassert _r['order'] == [] and _r['avg_turnaround'] == 0.0 and _r['turnaround'] == {}, '空进程表应返回空结果且不能除零，实际 %r' % (_r,)",
            "_r = rr([('B', 0, 2), ('A', 0, 2)], 2)\nassert _r['order'] == ['A', 'B'], '同时到达的进程按名字典序入队（A 先），实际 %r' % (_r['order'],)",
            "_ps = [('P1', 0, 5), ('P2', 0, 4)]\n_copy = list(_ps)\nrr(_ps, 2)\nassert _ps == _copy, 'rr 不能改动传入的进程表，实际 %r' % (_ps,)",
        ],
        'explanation': (
            'RR 的模拟难点只有一个：**入队的时机与顺序**。\n\n'
            '```python\n'
            'run = min(quantum, remaining[pid])\n'
            'now += run\n'
            'while idx < n and order[idx][1] <= now:   # 运行期间到达的先入队\n'
            '    queue.append(order[idx]); idx += 1\n'
            'if remaining[pid] > 0:\n'
            '    queue.append(cur)                     # 被挤下来的自己排到它们后面\n'
            '```\n\n'
            '「运行期间到达的先入队、被挤下来的再排到它们后面」是教材的标准约定；'
            '写成「先把自己放回队列、再放新到达的」会让新进程永远排在旧进程后面，'
            '时间轴整体错位——这是本题最容易丢分的地方。\n\n'
            '**手算一遍主数据**（时间片 2）：\n\n'
            '| 时间片 | 进程 | 时间 | 说明 |\n'
            '| --- | --- | --- | --- |\n'
            '| 1 | P1 | 0→2 | 剩 3；期间 P3(到达 1) 入队，P1 排到 P3 后面 |\n'
            '| 2 | P2 | 2→4 | 剩 2，排到队尾 |\n'
            '| 3 | P3 | 4→6 | 跑完，完成时间 6 |\n'
            '| 4 | P1 | 6→8 | 剩 1 |\n'
            '| 5 | P2 | 8→10 | 跑完，完成时间 10 |\n'
            '| 6 | P1 | 10→11 | 只剩 1 个时间单位，跑完 |\n\n'
            '周转时间 = 完成时间 − 到达时间：P1 11、P2 10、P3 5，平均 26/3 ≈ 8.6667。\n'
            '注意 P3 服务时间最短，周转时间反而最小——RR 对短作业有利，'
            '因为它很快就能拿到一个时间片（响应时间短）。\n\n'
            '**时间片大小的权衡**（选择题常考）：\n\n'
            '- 时间片太大 → 退化成 FCFS，短作业的响应时间变差；\n'
            '- 时间片太小 → 进程切换次数剧增，切换开销吃掉 CPU；\n'
            '- RR 的平均周转时间通常比 SJF 差（长作业被切得七零八落、所有进程一起等好几轮），'
            '但它**响应时间好**、不会饥饿，是分时系统的首选。\n\n'
            '**常见错误**：\n\n'
            '1. 入队顺序写反（见上）；\n'
            '2. 到达时刻正好等于时间片结束时刻的进程被漏掉，要多等一轮；\n'
            '3. 队列空时直接在当前时刻继续跑，忘了 `now = max(now, 下一个到达时刻)`；\n'
            '4. 最后一个时间片忘了用 `min(quantum, 剩余时间)`，时间轴凭空多出一截。\n\n'
            '复杂度：时间 O(总时间片数 × 进程数)、空间 O(进程数)。'
        ),
        'expected_output': "['P1', 'P2', 'P3', 'P1', 'P2', 'P1']\n{'P3': 6, 'P2': 10, 'P1': 11}\n{'P1': 11, 'P2': 10, 'P3': 5}\n8.6667\n['A', 'A', 'B']\n{'A': 3, 'B': 4}\n[] 0.0",
        'hints': [
            '一个时间片结束时，先让「运行期间到达」的进程入队，再把没跑完的当前进程放到队尾',
            '就绪队列空了就 now = max(now, 下一个到达时刻)；最后一个时间片不足 quantum 要按剩余时间算',
        ],
    },
    {
        'id': 'os-004',
        'track': 'algorithm',
        'chapter_id': 136,
        'chapter_title': '操作系统·内存管理',
        'topic': '操作系统·内存管理',
        'title': '首次适应 FF 内存分配（返回分配的起始地址）',
        'difficulty': 2,
        'tags': ['内存管理', '可变分区', '首次适应', '空闲分区表'],
        'statement': (
            '**题 33 · 首次适应 FF 内存分配**\n\n'
            '考点：可变分区分配、最先适应算法。\n\n'
            '老师的原题：初始空闲分区列表（按地址递增排列），实现首次适应分配算法。'
            '输入进程申请大小，分配后更新空闲分区，返回分配的起始地址；分配失败返回 -1。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '可变分区分配中，空闲分区用列表表示：每个元素是**两元素列表** '
            '`[起始地址, 大小]`，整个表按起始地址递增排列，相邻分区不重叠。\n\n'
            '定义函数 `first_fit_alloc(free_list, size)`：\n\n'
            '- `free_list`：空闲分区表（元素是可变列表，函数要**直接在上面更新**）；\n'
            '- `size`：本次申请的大小（正整数）；\n'
            '- 分配成功：从**第一个**「大小 ≥ size」的分区的**低地址端**切出 size，'
            '即 `起始地址 += size`、`大小 -= size`；若剩余大小为 0 就把这个分区从表里删掉；'
            '返回**分配的起始地址**；\n'
            '- 分配失败（没有任何分区放得下）：返回 `-1`，且 `free_list` 必须保持不变；\n'
            '- 因为总是从低地址端切、且不改变分区之间的先后关系，分配后表仍按地址递增。\n\n'
            '参考计算（小例子）：空闲表 `[[100, 200], [400, 50], [600, 30]]`：\n\n'
            '- 申请 40 → 用 100 号分区，返回 100，表变 `[[140, 160], [400, 50], [600, 30]]`；\n'
            '- 再申请 100 → 还是 100 号分区（它是第一个够用的），返回 140，'
            '表变 `[[240, 60], [400, 50], [600, 30]]`。\n\n'
            '**本题判题用主数据**：`[[100, 60], [200, 150], [400, 80], [600, 200]]`，'
            '依次申请 40、90、70、100、50、500，打印每次的返回值，最后打印空闲表。'
        ),
        'starter_code': (
            "def first_fit_alloc(free_list, size):\n"
            "    for i in range(len(free_list)):\n"
            "        # 找到第一个装得下的分区：起始地址 += size、大小 -= size\n"
            "        pass\n"
            "    return -1\n"
        ),
        'solution': (
            "def first_fit_alloc(free_list, size):\n"
            "    for i in range(len(free_list)):\n"
            "        if free_list[i][1] >= size:\n"
            "            start = free_list[i][0]\n"
            "            free_list[i][0] += size\n"
            "            free_list[i][1] -= size\n"
            "            if free_list[i][1] == 0:\n"
            "                del free_list[i]\n"
            "            return start\n"
            "    return -1\n"
            "\n"
            "blocks = [[100, 60], [200, 150], [400, 80], [600, 200]]\n"
            "for need in [40, 90, 70, 100, 50, 500]:\n"
            "    print(need, first_fit_alloc(blocks, need))\n"
            "print(blocks)\n"
            "print(first_fit_alloc([], 10))\n"
        ),
        'checks': [
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\n_r = first_fit_alloc(_b, 40)\nassert _r == 100, '首次适应要用第一个够用的分区（100 号，60 >= 40），返回起始地址 100，实际 %r' % (_r,)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\nfirst_fit_alloc(_b, 40)\nassert _b == [[140, 20], [200, 150], [400, 80], [600, 200]], '分配 40 后 100 号分区应变成 [140, 20]，实际 %r' % (_b,)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\n_r = first_fit_alloc(_b, 90)\nassert _r == 200 and _b == [[100, 60], [290, 60], [400, 80], [600, 200]], '申请 90 时 100 号分区只有 60（装不下）要跳过，改用 200 号分区并返回 200，实际 %r / %r' % (_r, _b)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\n_res = []\nfor _need in [40, 90, 70, 100, 50, 500]:\n    _res.append(first_fit_alloc(_b, _need))\nassert _res == [100, 200, 400, 600, 290, -1], '主数据的返回值应是 [100, 200, 400, 600, 290, -1]（注意第 5 个 50 装进了 290 号那个 60 大小的分区，500 谁都装不下），实际 %r' % (_res,)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\nfor _need in [40, 90, 70, 100, 50, 500]:\n    first_fit_alloc(_b, _need)\nassert _b == [[140, 20], [340, 10], [470, 10], [700, 100]], '主数据跑完后的空闲表应是 [[140, 20], [340, 10], [470, 10], [700, 100]]，实际 %r' % (_b,)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\nfirst_fit_alloc(_b, 500)\nassert _b == [[100, 60], [200, 150], [400, 80], [600, 200]], '装不下时必须返回 -1 且不能改动空闲表，实际 %r' % (_b,)",
            "assert first_fit_alloc([], 10) == -1, '空闲表为空时任何申请都装不下，应返回 -1'",
            "_b = [[100, 50]]\nassert first_fit_alloc(_b, 50) == 100 and _b == [], '申请大小正好等于分区大小时，要把这个分区整块切走（剩余为 0 的分区必须删掉），实际 %r' % (_b,)",
            "_b = [[100, 100], [200, 100]]\nassert first_fit_alloc(_b, 30) == 100 and _b == [[130, 70], [200, 100]], '两个分区都够用时首次适应取低地址的那个，实际 %r' % (_b,)",
            "_b = [[100, 200], [400, 50]]\n_r = first_fit_alloc(_b, 40)\nassert _r == 100 and _b == [[140, 160], [400, 50]], '后面虽然有一个更小却够用的分区（50），首次适应也**不回头**去用它：必须返回第一个够用的 100 号分区（那是最佳适应该做的事），实际 %r / %r' % (_r, _b)",
            "_b = [[100, 300], [500, 100]]\n_r = first_fit_alloc(_b, 80)\nassert _r == 100 and _b == [[180, 220], [500, 100]], '首次适应只看「谁在前面」，不看分区大小：应返回 100 而不是 500，实际 %r / %r' % (_r, _b)",
            "_b = [[100, 50], [200, 300]]\nassert first_fit_alloc(_b, 60) == 200 and _b == [[100, 50], [260, 240]], '第一个分区装不下（50 < 60）就继续往后找，实际 %r' % (_b,)",
            "_b = [[140, 20], [340, 10], [470, 10], [700, 100]]\nassert first_fit_alloc(_b, 101) == -1, '没有任何分区装得下 101（最大的空洞才 100）时应返回 -1，实际 %r' % (_b,)",
            "_b = [[100, 60], [200, 150], [400, 80], [600, 200]]\nfor _need in [40, 90, 70, 100, 50]:\n    first_fit_alloc(_b, _need)\nassert all(_b[i][0] < _b[i + 1][0] for i in range(len(_b) - 1)) and all(_h[1] > 0 for _h in _b), '分配后空闲表必须仍按地址递增，且不能留下大小为 0 的幽灵分区，实际 %r' % (_b,)",
            "_b = [[100, 60]]\nfirst_fit_alloc(_b, 20)\nassert _b[0][0] == 120 and _b[0][1] == 40, '切分区必须同时改起始地址和大小（只在原地址上缩水是错的），实际 %r' % (_b,)",
        ],
        'explanation': (
            '首次适应只做一件事：**从头扫描空闲表，遇到第一个装得下的分区就用它**，'
            '不用继续往后看。\n\n'
            '```python\n'
            'for i in range(len(free_list)):\n'
            '    if free_list[i][1] >= size:\n'
            '        start = free_list[i][0]\n'
            '        free_list[i][0] += size      # 低地址端被切走\n'
            '        free_list[i][1] -= size\n'
            '        if free_list[i][1] == 0:\n'
            '            del free_list[i]          # 正好用完，删掉这个分区\n'
            '        return start\n'
            'return -1\n'
            '```\n\n'
            '**手算一遍主数据** `[[100, 60], [200, 150], [400, 80], [600, 200]]`：\n\n'
            '| 申请 | 用的分区 | 返回 | 之后的空闲表 |\n'
            '| --- | --- | --- | --- |\n'
            '| 40 | 100 号 | 100 | [140, 20] |\n'
            '| 90 | 200 号（140 号只剩 20） | 200 | [290, 60] |\n'
            '| 70 | 400 号 | 400 | [470, 10] |\n'
            '| 100 | 600 号 | 600 | [700, 100] |\n'
            '| 50 | 290 号（60 是第一个够用的） | 290 | [340, 10] |\n'
            '| 500 | 谁都装不下 | -1 | 不变 |\n\n'
            '**首次适应的特点**：低地址部分被优先使用，高地址容易留下大块连续空间；'
            '缺点是低地址一端会积累很多小到再也用不上的碎片（外部碎片）。'
            '它也是速度最快的近似算法——通常不必扫描整张表。\n\n'
            '对照记忆：**最佳适应**每次选「能装下的最小分区」，看起来最省，'
            '实际会切出一堆比请求大一点点的小空洞（有「最佳适应是最坏策略」的说法）；'
            '**最坏适应**每次选最大的分区，留下的空洞较大、还能再用，但大分区很快被耗尽。\n'
            '本题的检查里专门放了两个「首次适应与最佳适应结果不同」的小例子：'
            '空闲表 `[[100, 200], [400, 50]]` 申请 40 时，首次适应返回 100，'
            '最佳适应才会返回 400——只要写成「挑最小的」就过不了检查。\n\n'
            '**常见错误**：\n\n'
            '1. 切分区时只减大小、不改起始地址（分区「原地缩水」，地址就错了）；\n'
            '2. 忘记删除剩余大小为 0 的分区，表里出现 `[300, 0]` 这种幽灵分区；\n'
            '3. 装不下时抛异常或返回 0——题面要求返回 -1 且不动表；\n'
            '4. 直接改传入的表却返回了新表（或者反过来），题面要求**原地更新并返回起始地址**。\n\n'
            '复杂度：时间 O(请求数 × 分区数)（每次最多扫一遍表）、空间 O(1)。'
        ),
        'expected_output': "40 100\n90 200\n70 400\n100 600\n50 290\n500 -1\n[[140, 20], [340, 10], [470, 10], [700, 100]]\n-1",
        'hints': [
            '从头扫到第一个「大小 >= size」的分区就用它，切的时候起始地址 += size、大小 -= size',
            '剩余大小变成 0 要把分区删掉；装不下返回 -1 且不许改动表',
        ],
    },
    {
        'id': 'os-005',
        'track': 'algorithm',
        'chapter_id': 136,
        'chapter_title': '操作系统·内存管理',
        'topic': '操作系统·内存管理',
        'title': '最佳适应 BF 内存分配（空闲分区按容量递增）',
        'difficulty': 1,
        'tags': ['内存管理', '可变分区', '最佳适应', '空闲分区表'],
        'statement': (
            '**题 34 · 最佳适应 BF 内存分配**\n\n'
            '考点：最佳适应算法、空闲分区排序。\n\n'
            '老师的原题：实现最佳适应分配算法，空闲分区按容量递增排序，分配后更新空闲表。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '最佳适应：每次分配都选**能装下的、容量最小的**那个空闲分区'
            '（容量相同就选地址小的），从它的低地址端切出申请大小。\n\n'
            '定义函数 `best_fit_alloc(free_list, size)`：\n\n'
            '- `free_list`：空闲分区表，元素是**两元素列表** `[起始地址, 大小]`；'
            '初始按地址递增给出，函数要**直接在上面更新**；\n'
            '- `size`：本次申请的大小（正整数）；\n'
            '- 分配成功：切出 size（`起始地址 += size`、`大小 -= size`，剩余为 0 就删掉这个分区），'
            '然后**把整个表按「容量递增、容量相同按地址递增」重排**，返回分配的起始地址；\n'
            '- 分配失败：返回 `-1`，且 `free_list` 保持原样（连顺序都不能动）；\n'
            '- 因为要按容量递增维护，所以分配后的表**不再**保证按地址递增——这是本题与'
            '首次适应的最大区别，也是「空闲链按容量递增挂」的教材写法。\n\n'
            '参考计算（小例子）：空闲表 `[[100, 200], [400, 50], [600, 30]]`：\n\n'
            '- 申请 40 → 够用的有 200 和 50，选最小的 50（400 号分区），返回 400，'
            '变 `[[440, 10], [100, 200], [600, 30]]`，再按容量递增重排成 '
            '`[[440, 10], [600, 30], [100, 200]]`。\n\n'
            '**本题判题用主数据**：`[[100, 60], [300, 120], [500, 80], [700, 200]]`，'
            '依次申请 70、100、150、60、45、100，打印每次的返回值，最后打印空闲表。'
        ),
        'starter_code': (
            "def best_fit_alloc(free_list, size):\n"
            "    pick = -1\n"
            "    for i in range(len(free_list)):\n"
            "        # 在所有够用的分区里挑容量最小的（容量相同挑地址小的）\n"
            "        pass\n"
            "    if pick == -1:\n"
            "        return -1\n"
            "    free_list.sort(key=lambda hole: (hole[1], hole[0]))\n"
            "    return 0\n"
        ),
        'solution': (
            "def best_fit_alloc(free_list, size):\n"
            "    pick = -1\n"
            "    for i in range(len(free_list)):\n"
            "        if free_list[i][1] >= size:\n"
            "            if pick == -1 or free_list[i][1] < free_list[pick][1] or (\n"
            "                    free_list[i][1] == free_list[pick][1]\n"
            "                    and free_list[i][0] < free_list[pick][0]):\n"
            "                pick = i\n"
            "    if pick == -1:\n"
            "        return -1\n"
            "    start = free_list[pick][0]\n"
            "    free_list[pick][0] += size\n"
            "    free_list[pick][1] -= size\n"
            "    if free_list[pick][1] == 0:\n"
            "        del free_list[pick]\n"
            "    free_list.sort(key=lambda hole: (hole[1], hole[0]))\n"
            "    return start\n"
            "\n"
            "blocks = [[100, 60], [300, 120], [500, 80], [700, 200]]\n"
            "for need in [70, 100, 150, 60, 45, 100]:\n"
            "    print(need, best_fit_alloc(blocks, need))\n"
            "print(blocks)\n"
            "print(best_fit_alloc([], 10))\n"
        ),
        'checks': [
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\n_r = best_fit_alloc(_b, 70)\nassert _r == 500, '申请 70 时够用的分区有 120、80、200，最小的那个是 500 号分区的 80，应返回 500，实际 %r' % (_r,)",
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\nbest_fit_alloc(_b, 70)\nassert _b == [[570, 10], [100, 60], [300, 120], [700, 200]], '分配后要把 500 号分区切成 [570, 10]，并按容量递增重排（10 排最前），实际 %r' % (_b,)",
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\n_res = []\nfor _need in [70, 100, 150, 60, 45, 100]:\n    _res.append(best_fit_alloc(_b, _need))\nassert _res == [500, 300, 700, 100, 850, -1], '主数据的返回值应是 [500, 300, 700, 100, 850, -1]（最后一次申请 100 时只剩 5、10、20 的小空洞），实际 %r' % (_res,)",
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\nfor _need in [70, 100, 150, 60, 45, 100]:\n    best_fit_alloc(_b, _need)\nassert _b == [[895, 5], [570, 10], [400, 20]], '主数据跑完后的空闲表应是 [[895, 5], [570, 10], [400, 20]]，实际 %r' % (_b,)",
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\nfor _need in [70, 100, 150]:\n    best_fit_alloc(_b, _need)\nassert _b == [[570, 10], [400, 20], [850, 50], [100, 60]], '每次分配成功后都要重排：容量 10、20、50、60 依次排列，实际 %r' % (_b,)",
            "_b = [[100, 80], [500, 80], [900, 200]]\n_r = best_fit_alloc(_b, 50)\nassert _r == 100 and _b == [[150, 30], [500, 80], [900, 200]], '两个够用的分区容量相同时要选地址小的那个（100 号），实际 %r / %r' % (_r, _b)",
            "_b = [[100, 50]]\nassert best_fit_alloc(_b, 50) == 100 and _b == [], '正好装满时要返回 100 且把分区删掉（表空），实际 %r' % (_b,)",
            "_b = [[100, 50]]\nassert best_fit_alloc(_b, 70) == -1 and _b == [[100, 50]], '装不下时要返回 -1 且表保持原样，实际 %r' % (_b,)",
            "assert best_fit_alloc([], 10) == -1, '空闲表为空时任何申请都装不下，应返回 -1'",
            "_b = [[100, 60], [200, 150], [300, 80]]\nassert best_fit_alloc(_b, 160) == -1 and _b == [[100, 60], [200, 150], [300, 80]], '最大的分区只有 150，申请 160 必须失败且不许重排表，实际 %r' % (_b,)",
            "_b = [[100, 300], [200, 80], [400, 40]]\n_r1 = best_fit_alloc(_b, 30)\n_r2 = best_fit_alloc(_b, 100)\nassert _r1 == 400 and _r2 == 100, '申请 30 时最小的够用分区是 400 号的 40（不是低地址的 300）；再申请 100 时只剩 100 号的 300 够用，实际 %r / %r' % (_r1, _r2)",
            "_b = [[100, 300], [200, 80], [400, 40]]\nbest_fit_alloc(_b, 30)\nbest_fit_alloc(_b, 100)\nassert _b == [[430, 10], [200, 80], [200, 200]], '两次分配后的空闲表应是 [[430, 10], [200, 80], [200, 200]]（按容量递增），实际 %r' % (_b,)",
            "_b = [[400, 90], [100, 200], [600, 90]]\n_r = best_fit_alloc(_b, 20)\nassert _r == 400, '表按容量递增时地址与大小无关，选最小的够用分区（90 里地址更小的 400 号），实际 %r' % (_r,)",
            "_b = [[100, 60], [300, 120], [500, 80], [700, 200]]\nfor _need in [70, 100, 150, 60, 45]:\n    best_fit_alloc(_b, _need)\nassert all(_b[i][1] <= _b[i + 1][1] for i in range(len(_b) - 1)), '分配后的空闲表必须按容量递增排列（这是最佳适应维护空闲链的方式），实际 %r' % (_b,)",
            "_b = [[100, 60]]\nbest_fit_alloc(_b, 20)\nassert _b[0][0] == 120 and _b[0][1] == 40, '切分区必须同时改起始地址和大小，实际 %r' % (_b,)",
        ],
        'explanation': (
            '最佳适应与首次适应只差「挑哪个分区」这一句：\n\n'
            '```python\n'
            '# 首次适应：遇到第一个装得下的就用（可以立刻 break）\n'
            '# 最佳适应：把所有装得下的都比一遍，选容量最小的那个\n'
            '```\n\n'
            '教材里最佳适应常写成「空闲分区链按容量递增排序」，因为这样第一个够用的就是最优解；'
            '本题用列表实现，所以每次分配后显式 `sort(key=lambda h: (h[1], h[0]))` 重排——'
            '排序键里的第二项就是「容量相同按地址递增」的平局规则。\n\n'
            '**手算一遍主数据** `[[100, 60], [300, 120], [500, 80], [700, 200]]`：\n\n'
            '| 申请 | 够用的分区 | 选中的 | 返回 | 重排后的表 |\n'
            '| --- | --- | --- | --- | --- |\n'
            '| 70 | 120、80、200 | 80（500 号） | 500 | [570,10]、[100,60]、[300,120]、[700,200] |\n'
            '| 100 | 120、200 | 120（300 号） | 300 | [570,10]、[400,20]、[100,60]、[700,200] |\n'
            '| 150 | 200 | 200（700 号） | 700 | [570,10]、[400,20]、[850,50]、[100,60] |\n'
            '| 60 | 60（正好）、50 不够 | 60（100 号） | 100 | [570,10]、[400,20]、[850,50] |\n'
            '| 45 | 50 | 50（850 号） | 850 | [895,5]、[570,10]、[400,20] |\n'
            '| 100 | 无（5、10、20 都不够） | —— | -1 | 不变 |\n\n'
            '**为什么说「最佳适应是最坏策略」**：它总把分区切得只剩下一点点'
            '（本题留下了 5、10、20 三个小空洞），这些碎片几乎永远满足不了任何请求，'
            '而且每次分配都要扫描整张空闲表。\n\n'
            '三种适应算法的口诀：\n\n'
            '- 首次适应：低地址优先、快、低端碎片多；\n'
            '- 最佳适应：留下最小碎片、慢、碎片最多最碎；\n'
            '- 最坏适应：总用最大的分区、留下的空洞最大、大分区很快用完。\n\n'
            '**常见错误**：\n\n'
            '1. 只比较「够用」就 break（那写成了首次适应）；\n'
            '2. 忘记分配后重排空闲表；\n'
            '3. 失败时也去重排（题面要求失败时表原样不动）；\n'
            '4. 切分区只减大小不改起始地址。\n\n'
            '复杂度：时间 O(请求数 × 分区数 log 分区数)、空间 O(1)。'
        ),
        'expected_output': "70 500\n100 300\n150 700\n60 100\n45 850\n100 -1\n[[895, 5], [570, 10], [400, 20]]\n-1",
        'hints': [
            '先把所有「容量 >= size」的分区比一遍，挑最小的（容量相同挑地址小的）',
            '成功分配后要 free_list.sort(key=lambda hole: (hole[1], hole[0])) 重排；失败时表不许动',
        ],
    },
    {
        'id': 'os-006',
        'track': 'algorithm',
        'chapter_id': 136,
        'chapter_title': '操作系统·内存管理',
        'topic': '操作系统·内存管理',
        'title': 'FIFO 页面置换（缺页次数与缺页率）',
        'difficulty': 1,
        'tags': ['页面置换', 'FIFO', '缺页次数', '缺页率', 'Belady 异常'],
        'statement': (
            '**题 35 · FIFO 页面置换算法**\n\n'
            '考点：页面置换、缺页次数。\n\n'
            '老师的原题：给定页面访问序列和内存块数，实现 FIFO 置换算法，'
            '统计缺页次数和缺页率。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            'FIFO（先进先出）：内存里的页框排成一个队列，发生缺页且没有空闲页框时，'
            '淘汰**最先进入内存**的那一页。\n\n'
            '定义函数 `fifo_replace(pages, frame_count)`：\n\n'
            '- `pages`：页面访问序列（页号组成的列表，可能为空）；'
            '`frame_count`：可用页框数（≥ 1）；\n'
            '- 返回二元组 `(缺页次数, 缺页率)`，缺页率 = 缺页次数 ÷ 访问总次数'
            '（**float**；空序列返回 `(0, 0.0)`）；\n'
            '- 页框一开始全是空的：第一次访问某个页一定缺页（装入空框）；\n'
            '- 同一个页再次被访问属于**命中**，不计缺页，而且**不改变任何页的进入次序**'
            '（FIFO 只看谁来得早，不看谁最近用过——命中时什么都不做）；\n'
            '- 替换时淘汰最早进入的页，新页排到队尾。\n\n'
            '**本题判题用主数据**：`[1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]`。\n\n'
            '参考计算（前几步）：3 个页框时，1、2、3 依次装入（缺页 3 次）；'
            '访问 4 时页框满，淘汰最早进入的 1；访问 2 时命中……最终 3 个页框缺页 12 次'
            '（共 15 次访问，缺页率 0.8）。\n\n'
            '最后打印：主数据在 3 个页框、4 个页框下的「缺页次数 缺页率（保留 4 位小数）」，'
            '再打印空序列在 3 个页框下的结果。'
        ),
        'starter_code': (
            "def fifo_replace(pages, frame_count):\n"
            "    frames = []\n"
            "    faults = 0\n"
            "    # 命中什么都不做；缺页时满了就 frames.pop(0) 淘汰最早进入的页\n"
            "    pass\n"
        ),
        'solution': (
            "def fifo_replace(pages, frame_count):\n"
            "    frames = []\n"
            "    faults = 0\n"
            "    for page in pages:\n"
            "        if page in frames:\n"
            "            continue\n"
            "        faults += 1\n"
            "        if len(frames) >= frame_count:\n"
            "            frames.pop(0)\n"
            "        frames.append(page)\n"
            "    total = len(pages)\n"
            "    return faults, (faults / total if total else 0.0)\n"
            "\n"
            "data = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n"
            "f3, r3 = fifo_replace(data, 3)\n"
            "print(f3, round(r3, 4))\n"
            "f4, r4 = fifo_replace(data, 4)\n"
            "print(f4, round(r4, 4))\n"
            "print(fifo_replace([], 3))\n"
        ),
        'checks': [
            "_d = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n_f, _r = fifo_replace(_d, 3)\nassert _f == 12, '主数据在 3 个页框下应缺页 12 次，实际 %r' % (_f,)",
            "_d = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n_f, _r = fifo_replace(_d, 3)\nassert abs(_r - 0.8) < 1e-9, '缺页率 = 12 / 15 = 0.8，实际 %r' % (_r,)",
            "_d = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n_f, _r = fifo_replace(_d, 4)\nassert _f == 11 and abs(_r - 11 / 15) < 1e-9, '同一序列在 4 个页框下应缺页 11 次（缺页率 0.7333），实际 %r / %r' % (_f, _r)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\n_f = fifo_replace(_d, 3)[0]\nassert _f == 9, '经典 Belady 序列在 3 个页框下应缺页 9 次，实际 %r' % (_f,)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\n_f = fifo_replace(_d, 4)[0]\nassert _f == 10, '同一序列在 4 个页框下反而缺页 10 次（Belady 异常：页框多了缺页更多），实际 %r' % (_f,)",
            "assert fifo_replace([1, 2, 1, 3, 2], 2)[0] == 3, '命中不能改变队列次序：1、2 装入后访问 1 是命中，访问 3 时淘汰的必须是 1（不是 2），所以共缺页 3 次；用 LRU 写会得到 4'",
            "assert fifo_replace([], 3) == (0, 0.0), '空引用串应返回 (0, 0.0) 且不能除零，实际 %r' % (fifo_replace([], 3),)",
            "assert fifo_replace([5], 1) == (1, 1.0), '只访问一页且只有一个页框：缺页 1 次、缺页率 1.0，实际 %r' % (fifo_replace([5], 1),)",
            "assert fifo_replace([7, 7, 7], 2)[0] == 1, '反复访问同一个页只会在第一次缺页，实际 %r' % (fifo_replace([7, 7, 7], 2)[0],)",
            "assert fifo_replace([1, 2, 3], 5)[0] == 3, '页框比用到的页还多时每个不同的页只缺页一次，实际 %r' % (fifo_replace([1, 2, 3], 5)[0],)",
            "assert fifo_replace([1, 2, 1, 2], 1)[0] == 4, '只有 1 个页框时每次访问都与上一页不同，4 次全部缺页，实际 %r' % (fifo_replace([1, 2, 1, 2], 1)[0],)",
            "assert fifo_replace([1, 2, 3, 1, 2, 3], 2)[0] == 6, '2 个页框装 3 个循环访问的页，每次都缺页，共 6 次，实际 %r' % (fifo_replace([1, 2, 3, 1, 2, 3], 2)[0],)",
            "_d = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n_f, _r = fifo_replace(_d, 3)\nassert abs(_r - _f / len(_d)) < 1e-9, '缺页率必须等于 缺页次数 ÷ 访问次数，实际 %r 与 %r' % (_r, _f / len(_d))",
            "_d = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3]\n_copy = list(_d)\nfifo_replace(_d, 3)\nassert _d == _copy, 'fifo_replace 只能读引用串，不能修改它，实际 %r' % (_d,)",
        ],
        'explanation': (
            'FIFO 的规则最朴素：**谁先进内存，谁先被淘汰**。实现上用一个列表当队列，'
            '命中时什么都不做，缺页且满时就 `pop(0)` 再 `append`。\n\n'
            '```python\n'
            'for page in pages:\n'
            '    if page in frames:\n'
            '        continue                    # 命中：FIFO 不改变次序\n'
            '    faults += 1\n'
            '    if len(frames) >= frame_count:\n'
            '        frames.pop(0)               # 淘汰最早进入的页\n'
            '    frames.append(page)\n'
            '```\n\n'
            '**手算一遍主数据**（3 个页框，共 15 次访问）：\n\n'
            '```\n'
            '1   缺页   [1]\n'
            '2   缺页   [1,2]\n'
            '3   缺页   [1,2,3]\n'
            '4   缺页   [2,3,4]     淘汰 1\n'
            '2   命中\n'
            '1   缺页   [3,4,1]     淘汰 2\n'
            '5   缺页   [4,1,5]     淘汰 3\n'
            '6   缺页   [1,5,6]     淘汰 4\n'
            '2   缺页   [5,6,2]     淘汰 1\n'
            '1   缺页   [6,2,1]     淘汰 5\n'
            '2   命中\n'
            '3   缺页   [2,1,3]     淘汰 6\n'
            '7   缺页   [1,3,7]     淘汰 2\n'
            '6   缺页   [3,7,6]     淘汰 1\n'
            '3   命中\n'
            '```\n\n'
            '共缺页 12 次，缺页率 12/15 = 0.8；换 4 个页框后是 11 次（0.7333）——'
            '这一组数据里页框多了缺页变少，符合直觉。\n\n'
            '**Belady 异常**是 FIFO 最有名的反常识现象：经典序列 '
            '`[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]` 在 3 个页框下缺页 9 次，'
            '4 个页框下反而缺页 10 次。原因是增加页框会**改变淘汰次序**，'
            '把某些马上要用的页更早地踢了出去。\n\n'
            '对照记忆：\n\n'
            '- FIFO：实现最简单，可能淘汰马上要用的页，**有** Belady 异常；\n'
            '- LRU：淘汰「最近最久未使用」的页，**没有** Belady 异常（属于栈算法），'
            '但需要硬件记录访问历史；\n'
            '- OPT：淘汰「将来最久不用」的页，缺页最少，但需要预知未来，只能当理论下界。\n\n'
            '**常见错误**：\n\n'
            '1. 命中时也调整队列次序（那就写成了 LRU，本题的 [1, 2, 1, 3, 2] 会多缺一次）；\n'
            '2. 缺页时只 `pop(0)` 忘记 `append`，页框一直是空的；\n'
            '3. 忘记「页框一开始是空的」，把第一次访问也当成置换；\n'
            '4. 空序列除零。\n\n'
            '复杂度：时间 O(访问次数 × 页框数)、额外空间 O(页框数)。'
        ),
        'expected_output': "12 0.8\n11 0.7333\n(0, 0.0)",
        'hints': [
            '命中时什么都不做；缺页且页框满时 pop(0) 淘汰最早进入的页，再把新页 append 到队尾',
            '缺页率 = 缺页次数 ÷ 访问总次数，空序列要返回 0.0 而不是报除零错误',
        ],
    },
    {
        'id': 'os-007',
        'track': 'algorithm',
        'chapter_id': 136,
        'chapter_title': '操作系统·内存管理',
        'topic': '操作系统·内存管理',
        'title': 'LRU 最近最久未使用置换（栈类算法）',
        'difficulty': 2,
        'tags': ['页面置换', 'LRU', '栈算法', '缺页次数'],
        'statement': (
            '**题 36 · LRU 最近最久未使用置换**\n\n'
            '考点：LRU 算法、堆栈类算法（高频考点）。\n\n'
            '老师的原题：给定页面访问序列和内存块数，实现 LRU 页面置换算法，统计缺页次数。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            'LRU（Least Recently Used）：发生缺页且页框满时，淘汰**上一次被访问时刻最早**'
            '（最久没被用过）的那一页；每访问一页（无论命中还是缺页装入），'
            '这一页都变成「最近刚用过」的。\n\n'
            '定义函数 `lru_replace(pages, frame_count)`：\n\n'
            '- `pages`：页面访问序列（可能为空）；`frame_count`：可用页框数（≥ 1）；\n'
            '- 返回**缺页次数**（int）；空序列返回 0；\n'
            '- 初始页框为空，第一次访问某页一定缺页；\n'
            '- 命中时要把这页标记为「刚刚用过」（这是 LRU 与 FIFO 的唯一区别）；\n'
            '- 缺页且页框满时淘汰最近最久未使用的页。\n\n'
            '**本题判题用主数据**：'
            '`[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]`，'
            '用 3 个页框（教材经典例题，LRU 缺页 12 次、FIFO 要 15 次）。\n\n'
            '另一个要会推的序列：`[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]`'
            '（就是 FIFO 的 Belady 序列）在 3 个页框下 LRU 缺页 10 次，4 个页框下 8 次——'
            '页框变多缺页单调不增，这正是「栈算法」的性质。\n\n'
            '最后打印：主数据在 3 个页框和 4 个页框下的缺页次数，'
            '再打印空序列在 3 个页框下的次数。'
        ),
        'starter_code': (
            "def lru_replace(pages, frame_count):\n"
            "    frames = []          # 按「最近使用时间」排序：最久没用的放最前面\n"
            "    faults = 0\n"
            "    # 命中：把该页移到队尾；缺页：满了就淘汰队首\n"
            "    pass\n"
        ),
        'solution': (
            "def lru_replace(pages, frame_count):\n"
            "    frames = []\n"
            "    faults = 0\n"
            "    for page in pages:\n"
            "        if page in frames:\n"
            "            frames.remove(page)\n"
            "            frames.append(page)\n"
            "            continue\n"
            "        faults += 1\n"
            "        if len(frames) >= frame_count:\n"
            "            frames.pop(0)\n"
            "        frames.append(page)\n"
            "    return faults\n"
            "\n"
            "data = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\n"
            "print(lru_replace(data, 3))\n"
            "print(lru_replace(data, 4))\n"
            "print(lru_replace([], 3))\n"
        ),
        'checks': [
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert lru_replace(_d, 3) == 12, '教材经典序列在 3 个页框下 LRU 应缺页 12 次（同一序列 FIFO 要 15 次），实际 %r' % (lru_replace(_d, 3),)",
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert lru_replace(_d, 4) == 8, '同一序列在 4 个页框下 LRU 应缺页 8 次（页框多了缺页更少），实际 %r' % (lru_replace(_d, 4),)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert lru_replace(_d, 3) == 10, 'Belady 序列在 3 个页框下 LRU 应缺页 10 次（FIFO 是 9 次，两者不对称正是考点），实际 %r' % (lru_replace(_d, 3),)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert lru_replace(_d, 4) == 8 and lru_replace(_d, 4) <= lru_replace(_d, 3), 'LRU 是栈算法：页框 4 个时缺页 8 次，且必须不多于 3 个页框时的 10 次（没有 Belady 异常），实际 %r' % (lru_replace(_d, 4),)",
            "assert lru_replace([1, 2, 1, 3, 2], 2) == 4, '命中要把该页标记为刚用过：1、2 装入后访问 1（命中，1 变成最近用过），访问 3 时淘汰的是 2；随后访问 2 又缺页，共 4 次（FIFO 只有 3 次），实际 %r' % (lru_replace([1, 2, 1, 3, 2], 2),)",
            "assert lru_replace([], 3) == 0, '空引用串一次缺页都没有，应返回 0，实际 %r' % (lru_replace([], 3),)",
            "assert lru_replace([5], 1) == 1, '只访问一页时缺页 1 次，实际 %r' % (lru_replace([5], 1),)",
            "assert lru_replace([1, 1, 1, 1], 1) == 1, '反复访问同一页只缺页一次，实际 %r' % (lru_replace([1, 1, 1, 1], 1),)",
            "assert lru_replace([1, 2, 2, 3], 1) == 3, '只有 1 个页框时每次换页都缺页（1、2、3 各一次），实际 %r' % (lru_replace([1, 2, 2, 3], 1),)",
            "assert lru_replace([1, 2, 3], 5) == 3, '页框足够时每个不同的页只缺页一次，实际 %r' % (lru_replace([1, 2, 3], 5),)",
            "assert lru_replace([1, 2, 1, 2, 1], 2) == 2, '两个页轮流访问且都在内存里时只在前两次缺页，实际 %r' % (lru_replace([1, 2, 1, 2, 1], 2),)",
            "assert lru_replace([1, 2, 3, 1, 2, 3], 2) == 6, '2 个页框装 3 个循环访问的页，每次都要置换，共缺页 6 次，实际 %r' % (lru_replace([1, 2, 3, 1, 2, 3], 2),)",
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\n_copy = list(_d)\nlru_replace(_d, 3)\nassert _d == _copy, 'lru_replace 只能读引用串，不能修改它，实际 %r' % (_d,)",
        ],
        'explanation': (
            '实现 LRU 有一个著名的小技巧：**用一个列表按「最近使用时间」排序，'
            '最久没用的放最前面**。命中时把该页从中间摘出来、追加到末尾；'
            '缺页且满时淘汰队首。\n\n'
            '```python\n'
            'if page in frames:\n'
            '    frames.remove(page)     # 先摘出来\n'
            '    frames.append(page)     # 再放到「最近用过」的一端\n'
            '    continue\n'
            'faults += 1\n'
            'if len(frames) >= frame_count:\n'
            '    frames.pop(0)           # 淘汰最久没用过的\n'
            'frames.append(page)\n'
            '```\n\n'
            '**与 FIFO 的唯一区别就是命中时那一对 remove / append**：'
            'FIFO 命中时什么都不做，LRU 命中时要把这页「刷新」。'
            '本题 `[1, 2, 1, 3, 2]`（2 个页框）就是专门用来区分两者的：'
            'LRU 缺页 4 次、FIFO 缺页 3 次。\n\n'
            '**手算主数据前几步**（3 个页框，LRU 顺序「最久没用 → 最近用过」）：\n\n'
            '```\n'
            '7   缺页   [7]\n'
            '0   缺页   [7,0]\n'
            '1   缺页   [7,0,1]\n'
            '2   缺页   [0,1,2]     淘汰 7\n'
            '0   命中   [1,2,0]\n'
            '3   缺页   [2,0,3]     淘汰 1\n'
            '0   命中   [2,3,0]\n'
            '4   缺页   [3,0,4]     淘汰 2\n'
            '2   缺页   [0,4,2]     淘汰 3\n'
            '3   缺页   [4,2,3]     淘汰 0\n'
            '0   缺页   [2,3,0]     淘汰 4（至此已 9 次）\n'
            '```\n\n'
            '后面 3、2 命中，1、0、7 缺页，最后 0、1 命中，总计 **12 次**；'
            'FIFO 同一序列要 15 次——LRU 用「最近用过」的历史近似了「将来会用」，'
            '所以更准。\n\n'
            '**什么是栈算法**：把页框数 k 的驻留集记作 L(k)，如果恒有 L(k) ⊆ L(k+1)，'
            '这类算法就叫栈算法；LRU 和 OPT 都是。'
            '栈算法**不会出现 Belady 异常**（页框多了缺页数单调不增），'
            'FIFO 不是栈算法，所以会有 9 → 10 这种反常。'
            '考试里判断「谁有 Belady 异常」就记住：**FIFO 有，LRU / OPT 没有**。\n\n'
            '**常见错误**：\n\n'
            '1. 命中时不刷新访问时间（那就退化成 FIFO，本题会多缺页）；\n'
            '2. 缺页时先 append 再 pop(0)（把自己的新页淘汰掉）；\n'
            '3. 用「访问次数」而不是「上一次访问的时刻」比较新旧。\n\n'
            '复杂度：时间 O(访问次数 × 页框数)、额外空间 O(页框数)。'
        ),
        'expected_output': '12\n8\n0',
        'hints': [
            '用列表维护 LRU 顺序：最久没用的放最前面，命中时 remove + append 刷新到队尾',
            '缺页且页框满时淘汰队首；LRU 是栈算法，页框变多缺页不会反增',
        ],
    },
    {
        'id': 'os-008',
        'track': 'algorithm',
        'chapter_id': 137,
        'chapter_title': '操作系统·文件与磁盘',
        'topic': '操作系统·文件与磁盘',
        'title': '位示图管理磁盘块（分配与回收）',
        'difficulty': 2,
        'tags': ['位示图', '磁盘块', '分配与回收'],
        'statement': (
            '**题 37 · 位示图管理磁盘块**\n\n'
            '考点：位示图、磁盘块分配。\n\n'
            '老师的原题：磁盘总块数为 n，用列表模拟位示图（0 空闲，1 占用）。实现两个函数：\n'
            '(1) `allocate_block()`：分配一个空闲块，返回块号；\n'
            '(2) `free_block(block_no)`：释放指定块号。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '位示图用一个列表 `bitmap` 表示，**下标就是块号**（从 0 开始），'
            '长度就是磁盘总块数；`0` 表示空闲、`1` 表示已占用。'
            '为了判题时能显式传参，两个函数都接收位示图：\n\n'
            '1. `allocate_block(bitmap)`：\n'
            '   - 从头扫描位示图，找到**第一个为 0 的位**，把它置成 1，返回它的块号；\n'
            '   - 位示图全满（没有 0）时返回 `-1`，且**不修改**位示图；\n'
            '   - 位示图为空列表时同样返回 `-1`。\n'
            '2. `free_block(bitmap, block_no)`：\n'
            '   - 块号合法（`0 <= block_no < len(bitmap)`）且该块**当前是已占用（1）**时，'
            '把它清成 0，返回 `True`；\n'
            '   - 否则返回 `False` 且不修改位示图：'
            '块号越界（含负数），或者该块本来就是空闲的，都算「回收失败」。\n\n'
            '两个函数都直接修改传入的 `bitmap`，位示图的长度始终不变。\n\n'
            '参考计算：位示图 `[1, 1, 0, 0, 0]`：\n'
            '`allocate_block` 返回 2（第一个 0 在下标 2），位示图变成 `[1, 1, 1, 0, 0]`；'
            '再调一次返回 3。`free_block(bitmap, 2)` 返回 True，'
            '位示图变成 `[1, 1, 0, 1, 0]`（注意 2 号块空出来了，下次分配又会先分到 2）。\n\n'
            '最后打印四次调用的结果（返回值与位示图），'
            '再打印「位示图全满时分配」与「释放一个本来就空闲的块」的结果。'
        ),
        'starter_code': (
            "def allocate_block(bitmap):\n"
            "    for i in range(len(bitmap)):\n"
            "        # 找到第一个 0：置 1 并返回块号\n"
            "        pass\n"
            "    return -1\n\n"
            "def free_block(bitmap, block_no):\n"
            "    # 合法且当前为 1 才清 0 并返回 True，否则返回 False 且不改动\n"
            "    pass\n"
        ),
        'solution': (
            "def allocate_block(bitmap):\n"
            "    for i in range(len(bitmap)):\n"
            "        if bitmap[i] == 0:\n"
            "            bitmap[i] = 1\n"
            "            return i\n"
            "    return -1\n"
            "\n"
            "def free_block(bitmap, block_no):\n"
            "    if 0 <= block_no < len(bitmap) and bitmap[block_no] == 1:\n"
            "        bitmap[block_no] = 0\n"
            "        return True\n"
            "    return False\n"
            "\n"
            "bm = [1, 1, 0, 0, 0]\n"
            "print(allocate_block(bm), bm)\n"
            "print(allocate_block(bm), bm)\n"
            "print(free_block(bm, 0), bm)\n"
            "print(allocate_block(bm), bm)\n"
            "print(allocate_block([1, 1]), free_block([1, 0, 0], 1))\n"
        ),
        'checks': [
            "_bm = [1, 1, 0, 0, 0]\n_r = allocate_block(_bm)\nassert _r == 2 and _bm == [1, 1, 1, 0, 0], '第一个空闲块是 2 号（下标 2），分配后该位置 1，实际 %r / %r' % (_r, _bm)",
            "_bm = [1, 1, 0, 0, 0]\nallocate_block(_bm)\n_r = allocate_block(_bm)\nassert _r == 3 and _bm == [1, 1, 1, 1, 0], '再分配一个应返回 3（下一个 0），实际 %r / %r' % (_r, _bm)",
            "_bm = [1, 1, 0, 0, 0]\n_r = allocate_block(_bm)\nassert _r == 2, '位示图 [1, 1, 0, 0, 0] 的第一个空闲块号是 2，实际 %r' % (_r,)",
            "_bm = [1, 1, 0]\nassert free_block(_bm, 0) is True and _bm == [0, 1, 0], '释放已占用的 0 号块应返回 True 并把它清成 0，实际 %r / %r' % (free_block([1, 1, 0], 0), _bm)",
            "_bm = [0, 1, 1]\nassert free_block(_bm, 0) is False and _bm == [0, 1, 1], '释放一个本来就空闲的块应返回 False，且位示图不能变，实际 %r' % (_bm,)",
            "_bm = [1, 0, 1]\nassert free_block(_bm, 3) is False and _bm == [1, 0, 1], '块号越界（3 不小于长度 3）应返回 False 且不改动位示图，实际 %r' % (_bm,)",
            "_bm = [1, 1]\nassert free_block(_bm, -1) is False and _bm == [1, 1], '负数块号非法，应返回 False（不能拿它当倒数下标用），实际 %r' % (_bm,)",
            "_bm = [1, 1, 1]\nassert allocate_block(_bm) == -1 and _bm == [1, 1, 1], '位示图全满时应返回 -1 且不修改它，实际 %r' % (_bm,)",
            "assert allocate_block([]) == -1, '位示图为空（磁盘没有块）时分配应返回 -1'",
            "_bm = [0, 0, 0, 0, 0, 0, 0, 0]\nfor _ in range(3):\n    allocate_block(_bm)\nassert _bm.count(1) == 3, '连续分配 3 个块后应恰好有 3 个位置是 1，实际 %r' % (_bm,)",
            "_bm = [1, 1, 1, 0, 0]\nassert allocate_block(_bm) == 3 and allocate_block(_bm) == 4 and allocate_block(_bm) == -1, '填满最后两个块之后再分配就没有空闲块了，应返回 -1，实际 %r' % (_bm,)",
            "_bm = [0, 0, 0]\nallocate_block(_bm)\nfree_block(_bm, 0)\n_r = allocate_block(_bm)\nassert _r == 0 and _bm == [1, 0, 0], '释放 0 号块后再分配，低块号优先，应重新分到 0，实际 %r / %r' % (_r, _bm)",
            "_bm = [1, 0, 1]\nassert free_block(_bm, 0) is True and free_block(_bm, 2) is True and _bm == [0, 0, 0], '逐个释放后位示图应回到全 0，实际 %r' % (_bm,)",
            "_bm = [1, 1, 0]\nallocate_block(_bm)\nfree_block(_bm, 1)\nassert _bm == [1, 0, 1], '回收只动指定的那一位，其它位不能受影响，实际 %r' % (_bm,)",
            "_bm = [0, 1, 0]\n_len = len(_bm)\nfor _ in range(5):\n    allocate_block(_bm)\n    free_block(_bm, 0)\nassert len(_bm) == _len and _bm == [0, 1, 0], '反复分配与回收不能改变位示图的长度，且每次都先分到 0 号再被释放，状态回到 [0, 1, 0]，实际 %r' % (_bm,)",
        ],
        'explanation': (
            '位示图（bitmap）是磁盘块管理最常用的数据结构：**一位对应一块**，'
            '0 空闲、1 占用。分配就是「找第一个 0 并置 1」，回收就是「把对应位清 0」。\n\n'
            '```python\n'
            'def allocate_block(bitmap):\n'
            '    for i in range(len(bitmap)):\n'
            '        if bitmap[i] == 0:\n'
            '            bitmap[i] = 1\n'
            '            return i\n'
            '    return -1          # 一个 0 都没有 → 磁盘满了\n'
            '```\n\n'
            '分配是**顺序查找**：总是优先使用低块号，速度取决于位示图前面有多少个 1。\n\n'
            '**408 常考的「字号 / 位号」换算**：位示图在实际系统里按「字」存储，'
            '每个字 m 位（比如 32 位）。块号 `b` 与「字号 `i`、位号 `j`」的关系是：\n\n'
            '```\n'
            'i = b // m        j = b % m        （本题的列表表示里 j 就是下标）\n'
            'b = i * m + j\n'
            '```\n\n'
            '回收时还要注意：**同一块不能被释放两次**，也不能释放不属于自己文件的块，'
            '所以 `free_block` 必须先检查「这一块当前是 1」，非法操作返回 False。'
            '本题把「越界」和「本来就空闲」都当成回收失败处理。\n\n'
            '**手算一遍参考数据**：`[1, 1, 0, 0, 0]` → 分配得到 2（位示图 `[1, 1, 1, 0, 0]`）'
            '→ 再分配得到 3（`[1, 1, 1, 1, 0]`）→ 回收 0 号 → `[0, 1, 1, 1, 0]`'
            '→ 再分配又回到 0 号（低块号优先）。\n\n'
            '**常见错误**：\n\n'
            '1. 分配时只返回块号忘记置 1（下次会重复分配同一块）；\n'
            '2. 回收越界块号时直接 `bitmap[block_no] = 0`，'
            'Python 里负下标会**悄悄改到最后一块**（本题专门用 -1 检测这个坑）；\n'
            '3. 没检查「本来就是 0」，把二次释放也当成功（磁盘空间会凭空增加）；\n'
            '4. 位示图全满时返回 0（0 是合法块号），必须用 -1 表示失败。\n\n'
            '复杂度：分配 / 回收一趟 O(n)（n 为块数），位示图本身只占 n 个二进制位。'
        ),
        'expected_output': "2 [1, 1, 1, 0, 0]\n3 [1, 1, 1, 1, 0]\nTrue [0, 1, 1, 1, 0]\n0 [1, 1, 1, 1, 0]\n-1 False",
        'hints': [
            '分配 = 找第一个 0 并置 1 返回下标；全满返回 -1，空表也返回 -1',
            '回收要先判断 0 <= block_no < len(bitmap) 且该位是 1，否则返回 False 且什么都不改',
        ],
    },
    {
        'id': 'os-009',
        'track': 'algorithm',
        'chapter_id': 137,
        'chapter_title': '操作系统·文件与磁盘',
        'topic': '操作系统·文件与磁盘',
        'title': 'FCFS 磁盘调度（总寻道长度）',
        'difficulty': 1,
        'tags': ['磁盘调度', 'FCFS', '寻道长度'],
        'statement': (
            '**题 38 · FCFS 磁盘调度**\n\n'
            '考点：磁盘调度、寻道长度。\n\n'
            '老师的原题：给定磁头初始位置和访问柱面序列，实现先来先服务磁盘调度，'
            '计算总寻道长度。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            'FCFS 磁盘调度：磁头**按请求到达的先后顺序**依次移动到各个柱面，'
            '先后顺序就是输入序列的顺序，不重新排序。\n\n'
            '定义函数 `fcfs_disk(head, requests)`：\n\n'
            '- `head`：磁头初始位置（柱面号，非负整数）；\n'
            '- `requests`：访问柱面序列（列表，可能为空、可能有重复的柱面）；\n'
            '- 返回二元组 `(访问顺序, 总寻道长度)`：\n'
            '  - `访问顺序`：柱面号列表，FCFS 下与 `requests` 完全相同；\n'
            '  - `总寻道长度`：磁头依次移动的距离之和，'
            '**从 head 移动到第一个请求的距离也要算**，'
            '即 `|r1 - head| + |r2 - r1| + ...`（相邻两个柱面差的绝对值累加）；\n'
            '  - 空序列返回 `([], 0)`；\n'
            '  - `requests` 不能被修改。\n\n'
            '参考数据（教材经典例题）：`head = 53`，'
            '`requests = [98, 183, 37, 122, 14, 124, 65, 67]`：\n\n'
            '- 访问顺序就是原序列；\n'
            '- 寻道距离依次是 45、85、146、85、108、110、59、2，总寻道长度 640。\n\n'
            '最后打印：经典数据的访问顺序与总寻道长度；'
            '再打印 `fcfs_disk(100, [200, 50, 150, 25, 75])` 与 `fcfs_disk(50, [])` 的结果。'
        ),
        'starter_code': (
            "def fcfs_disk(head, requests):\n"
            "    order = list(requests)\n"
            "    total = 0\n"
            "    cur = head\n"
            "    # 依次累加 |目标柱面 - 当前柱面|，然后磁头走到目标柱面\n"
            "    pass\n"
            "    return order, total\n"
        ),
        'solution': (
            "def fcfs_disk(head, requests):\n"
            "    order = list(requests)\n"
            "    total = 0\n"
            "    cur = head\n"
            "    for cyl in requests:\n"
            "        total += abs(cyl - cur)\n"
            "        cur = cyl\n"
            "    return order, total\n"
            "\n"
            "order, total = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\n"
            "print(order)\n"
            "print(total)\n"
            "print(fcfs_disk(100, [200, 50, 150, 25, 75]))\n"
            "print(fcfs_disk(50, []))\n"
        ),
        'checks': [
            "_o, _t = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\nassert _o == [98, 183, 37, 122, 14, 124, 65, 67], 'FCFS 的访问顺序就是请求顺序（不排序），实际 %r' % (_o,)",
            "_o, _t = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\nassert _t == 640, '经典例题的总寻道长度应是 45+85+146+85+108+110+59+2 = 640，实际 %r' % (_t,)",
            "_o, _t = fcfs_disk(100, [200, 50, 150, 25, 75])\nassert _o == [200, 50, 150, 25, 75] and _t == 525, '100 出发依次到 200、50、150、25、75：距离 100+150+100+125+50 = 525，实际 %r / %r' % (_o, _t)",
            "_o, _t = fcfs_disk(50, [])\nassert _o == [] and _t == 0, '空请求序列应返回 ([], 0)，实际 %r' % ((_o, _t),)",
            "_o, _t = fcfs_disk(53, [50])\nassert _o == [50] and _t == 3, '只有一个请求时寻道长度就是磁头到它的距离 3，实际 %r' % ((_o, _t),)",
            "_o, _t = fcfs_disk(0, [10, 20])\nassert _o == [10, 20] and _t == 20, '从 0 号柱面出发依次到 10、20：10 + 10 = 20，实际 %r' % ((_o, _t),)",
            "_o, _t = fcfs_disk(100, [50])\nassert _t == 50, '磁头从 100 移到 50 的寻道长度是 50（取绝对值，不能写成 -50），实际 %r' % (_t,)",
            "_o, _t = fcfs_disk(5, [5, 5])\nassert _o == [5, 5] and _t == 0, '请求柱面等于当前柱面时磁头不动（距离 0），重复请求也要保留，实际 %r' % ((_o, _t),)",
            "_o, _t = fcfs_disk(200, [100, 300, 150])\nassert _t == 100 + 200 + 150, '来回折返也要逐段累加：|100-200| + |300-100| + |150-300| = 450，实际 %r' % (_t,)",
            "_req = [98, 183, 37]\n_copy = list(_req)\nfcfs_disk(53, _req)\nassert _req == _copy, 'fcfs_disk 不能改动传入的请求序列，实际 %r' % (_req,)",
            "_o, _t = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\nassert isinstance(_t, int) and _o is not None, '返回的寻道长度应是整数，实际 %r' % (_t,)",
            "_o1, _t1 = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\n_o2, _t2 = fcfs_disk(53, [98, 183, 37, 122, 14, 124, 65, 67])\nassert _t1 == _t2 == 640 and _o1 == _o2, '同一组输入必须得到同样的结果（纯函数，不能依赖外部状态）'",
        ],
        'explanation': (
            'FCFS 磁盘调度是「最公平但最笨」的策略：**谁先来就先服务谁**，'
            '磁头像摆渡一样在盘面上来回跑。\n\n'
            '```python\n'
            'total = 0\n'
            'cur = head\n'
            'for cyl in requests:\n'
            '    total += abs(cyl - cur)   # 这一段要走的距离\n'
            '    cur = cyl                 # 磁头移到请求柱面\n'
            '```\n\n'
            '**手算一遍经典例题**（head = 53）：\n\n'
            '| 请求 | 98 | 183 | 37 | 122 | 14 | 124 | 65 | 67 |\n'
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
            '| 移动距离 | 45 | 85 | 146 | 85 | 108 | 110 | 59 | 2 |\n\n'
            '总寻道长度 640。同一组请求若按 **SSTF**（最短寻道时间优先）只需 236，'
            '按 **SCAN**（下一题的电梯算法）只需 208~299（看初始方向）——'
            'FCFS 的性能差，但胜在**不会饥饿**：每个请求迟早都会被服务，请求之间也不会被插队。\n\n'
            '**四个指标别搞混**：\n\n'
            '- 寻道时间：磁头移动到目标柱面的时间 ≈ 寻道长度 × 每道时间；\n'
            '- 旋转延迟：等待目标扇区转到磁头下（平均为半圈时间）；\n'
            '- 传输时间：读写数据本身的时间；\n'
            '- 磁盘访问时间 = 寻道时间 + 旋转延迟 + 传输时间（前两项占大头）。\n\n'
            '**常见错误**：\n\n'
            '1. 忘记把「从初始位置 head 到第一个请求」的距离算进去（少算一段）；\n'
            '2. 对差值忘了取绝对值（来回折返时累计值会互相抵消）；\n'
            '3. 自作聪明地给请求排序——FCFS 就是按到达顺序，排序后就变成别的算法了；\n'
            '4. 空序列时返回 0 却忘了 access 顺序也要是空列表。\n\n'
            '复杂度：时间 O(n)、空间 O(n)（存访问顺序）。'
        ),
        'expected_output': "[98, 183, 37, 122, 14, 124, 65, 67]\n640\n([200, 50, 150, 25, 75], 525)\n([], 0)",
        'hints': [
            '用一个 cur 记录磁头当前位置，每步 total += abs(cyl - cur) 再 cur = cyl',
            '第一段是从 head 到第一个请求的距离，别忘了算；空序列返回 ([], 0)',
        ],
    },
    {
        'id': 'os-010',
        'track': 'algorithm',
        'chapter_id': 137,
        'chapter_title': '操作系统·文件与磁盘',
        'topic': '操作系统·文件与磁盘',
        'title': 'SCAN 电梯调度（访问顺序与总寻道长度）',
        'difficulty': 2,
        'tags': ['磁盘调度', 'SCAN', '电梯算法', '寻道长度'],
        'statement': (
            '**题 39 · SCAN 电梯调度算法**\n\n'
            '考点：电梯调度、移动方向。\n\n'
            '老师的原题：给定磁头初始位置、初始移动方向、访问柱面序列，'
            '实现 SCAN 电梯调度算法。输出访问顺序和总寻道长度。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            'SCAN 像电梯一样：磁头沿一个方向移动，**途中遇到的请求依次服务**；'
            '这一方向的请求服务完后掉头，再服务另一方向的请求。\n\n'
            '定义函数 `scan_disk(head, direction, requests)`：\n\n'
            '- `head`：磁头初始柱面号；`direction`：初始移动方向，'
            '取值 `\'up\'`（柱面号增大方向）或 `\'down\'`（减小方向）；\n'
            '- `requests`：访问柱面序列（可能为空、可能有重复）；\n'
            '- 返回二元组 `(访问顺序, 总寻道长度)`；\n'
            '- `访问顺序` 里每个请求都出现且只出现一次（重复的请求柱面也重复列出）；\n'
            '- `总寻道长度` = 磁头实际移动的总距离（从 head 到第一个被服务的请求开始算）。\n\n'
            '**本题采用 LOOK 口径（必须照做）**：\n\n'
            '1. 磁头只走到该方向上**最远的那个请求**柱面，**不空跑到磁盘端点**；'
            '服务完该方向所有请求后立即掉头；\n'
            '2. 若初始方向上**一个请求都没有**，磁头直接掉头（不产生额外寻道距离）；\n'
            '3. 请求柱面与 `head` 相同时，按当前方向**最先服务**它；\n'
            '4. 重复的柱面按多个请求处理，访问顺序里重复出现（磁头不动，距离记 0）。\n\n'
            '（经典教材口径是「走到磁盘端点再掉头」，多出的那段空跑也算进总长度；'
            '本题没有给磁盘边界，所以统一按只走到最远请求的 LOOK 口径判题。）\n\n'
            '**本题判题用主数据**：`head = 53`，`direction = \'up\'`，'
            '`requests = [98, 183, 37, 122, 14, 124, 65, 67]`：\n\n'
            '- 向大方向先依次服务 65、67、98、122、124、183（到 183 为止），然后掉头；\n'
            '- 再服务 37、14；\n'
            '- 总寻道长度 = (183−53) + (183−14) = 130 + 169 = 299。\n\n'
            '最后打印：主数据的访问顺序与总寻道长度；再打印同一组数据在 '
            '`direction = \'down\'` 时的结果；最后打印 `scan_disk(100, \'up\', [10, 20, 30])`。'
        ),
        'starter_code': (
            "def scan_disk(head, direction, requests):\n"
            "    # 按方向把请求分成「去程」和「回程」两段：\n"
            "    # up   -> 去程 = head 及以上、升序；回程 = head 以下、降序\n"
            "    # down -> 去程 = head 及以下、降序；回程 = head 以上、升序\n"
            "    order = []\n"
            "    total = 0\n"
            "    cur = head\n"
            "    pass\n"
        ),
        'solution': (
            "def scan_disk(head, direction, requests):\n"
            "    if direction == 'up':\n"
            "        first = sorted(c for c in requests if c >= head)\n"
            "        second = sorted((c for c in requests if c < head), reverse=True)\n"
            "    else:\n"
            "        first = sorted((c for c in requests if c <= head), reverse=True)\n"
            "        second = sorted(c for c in requests if c > head)\n"
            "    order = first + second\n"
            "    total = 0\n"
            "    cur = head\n"
            "    for cyl in order:\n"
            "        total += abs(cyl - cur)\n"
            "        cur = cyl\n"
            "    return order, total\n"
            "\n"
            "reqs = [98, 183, 37, 122, 14, 124, 65, 67]\n"
            "order, total = scan_disk(53, 'up', reqs)\n"
            "print(order)\n"
            "print(total)\n"
            "order2, total2 = scan_disk(53, 'down', reqs)\n"
            "print(order2)\n"
            "print(total2)\n"
            "print(scan_disk(100, 'up', [10, 20, 30]))\n"
        ),
        'checks': [
            "_o, _t = scan_disk(53, 'up', [98, 183, 37, 122, 14, 124, 65, 67])\nassert _o == [65, 67, 98, 122, 124, 183, 37, 14], '向大方向依次服务 65、67、98、122、124、183，到最远的 183 后掉头服务 37、14，实际 %r' % (_o,)",
            "_o, _t = scan_disk(53, 'up', [98, 183, 37, 122, 14, 124, 65, 67])\nassert _t == 299, '总寻道长度 = (183-53) + (183-14) = 299（只走到最远请求 183，不空跑到磁盘端点），实际 %r' % (_t,)",
            "_o, _t = scan_disk(53, 'down', [98, 183, 37, 122, 14, 124, 65, 67])\nassert _o == [37, 14, 65, 67, 98, 122, 124, 183], '向小方向先服务 37、14，掉头后再升序服务 65、67、98、122、124、183，实际 %r' % (_o,)",
            "_o, _t = scan_disk(53, 'down', [98, 183, 37, 122, 14, 124, 65, 67])\nassert _t == 208, '总寻道长度 = (53-14) + (183-14) = 39 + 169 = 208，实际 %r' % (_t,)",
            "_o, _t = scan_disk(100, 'up', [10, 20, 30])\nassert _o == [30, 20, 10] and _t == 90, '初始方向上没有请求（都比 100 小）就直接掉头：30、20、10，距离 70+10+10 = 90，实际 %r / %r' % (_o, _t)",
            "_o, _t = scan_disk(10, 'down', [50, 60])\nassert _o == [50, 60] and _t == 50, '向小方向没有请求就掉头向上服务：50、60，距离 40 + 10 = 50，实际 %r / %r' % (_o, _t)",
            "_o, _t = scan_disk(50, 'up', [50, 60, 40])\nassert _o == [50, 60, 40] and _t == 30, '与 head 重合的请求 50 按当前方向最先服务（距离 0），再 60，最后掉头到 40，实际 %r / %r' % (_o, _t)",
            "_o, _t = scan_disk(50, 'down', [50, 60, 40])\nassert _o == [50, 40, 60] and _t == 30, '同为 50 的请求在 down 方向也是最先服务（距离 0），然后 40（10）、掉头到 60（20），共 30，实际 %r / %r' % (_o, _t)",
            "_o, _t = scan_disk(50, 'up', [60, 60, 40])\nassert _o == [60, 60, 40] and _t == 30, '重复柱面按多个请求处理（访问顺序里出现两次，第二次距离 0），实际 %r / %r' % (_o, _t)",
            "_o, _t = scan_disk(100, 'up', [])\nassert _o == [] and _t == 0, '空请求序列应返回 ([], 0)，实际 %r' % ((_o, _t),)",
            "_o, _t = scan_disk(100, 'down', [30])\nassert _o == [30] and _t == 70, '只有一个请求时就是直接走过去，距离 70，实际 %r' % ((_o, _t),)",
            "_o, _t = scan_disk(53, 'up', [98, 183, 37, 122, 14, 124, 65, 67])\nassert sorted(_o) == sorted([98, 183, 37, 122, 14, 124, 65, 67]), '每个请求都要被服务且只服务一次（访问顺序是请求序列的一个排列），实际 %r' % (_o,)",
            "_o, _t = scan_disk(53, 'up', [98, 183, 37, 122, 14, 124, 65, 67])\nassert _o[:6] == sorted(_o[:6]) and _o[6:] == sorted(_o[6:], reverse=True), 'SCAN 的访问顺序必须分成两段：去程升序、回程降序（u 形折返），实际 %r' % (_o,)",
            "_o, _t = scan_disk(53, 'down', [98, 183, 37, 122, 14, 124, 65, 67])\nassert abs(_t - sum(abs(b - a) for a, b in zip([53] + _o[:-1], _o))) < 1e-9, '总寻道长度必须等于按访问顺序逐段累加的绝对值之和，实际 %r' % (_t,)",
            "_req = [98, 183, 37]\n_copy = list(_req)\nscan_disk(53, 'up', _req)\nassert _req == _copy, 'scan_disk 不能改动传入的请求序列，实际 %r' % (_req,)",
        ],
        'explanation': (
            'SCAN 又叫**电梯算法**：电梯不会为了某层的乘客来回乱跑，'
            '而是朝一个方向走到底（本题是走到该方向最远的请求）、沿途服务，再掉头回来。\n\n'
            '```python\n'
            'if direction == \'up\':\n'
            '    first = sorted(c for c in requests if c >= head)          # 去程：升序\n'
            '    second = sorted((c for c in requests if c < head), reverse=True)  # 回程：降序\n'
            'else:\n'
            '    first = sorted((c for c in requests if c <= head), reverse=True)\n'
            '    second = sorted(c for c in requests if c > head)\n'
            '```\n\n'
            '**手算一遍主数据**（head = 53，向上）：去程要服务 65、67、98、122、124、183，'
            '走到 183；回程服务 37、14。总距离 = 130（去） + 169（回） = 299。'
            '同一组数据若初始方向向下，则先服务 37、14，再掉头服务 65、67、98、122、124、183，'
            '总距离 = 39 + 169 = 208——**同一批请求，初始方向不同，结果差很多**，'
            '这是 SCAN 计算题的常考陷阱。\n\n'
            '**SCAN 为什么比 SSTF 公平？** SSTF（最短寻道时间优先）每次都挑最近的请求，'
            '平均寻道长度很小，但会「赖着」磁头当前位置附近不走，'
            '远处的请求可能永远排不上队（**饥饿**）。SCAN 保证磁头朝一个方向推进会'
            '扫过沿途所有请求，任何请求最多等「一趟往返」，所以**不会饥饿**，'
            '代价是平均寻道长度通常比 SSTF 差一些。\n\n'
            '**两种口径都要会**：\n\n'
            '- 走到**磁盘端点**再掉头的经典 SCAN：要加上「最远请求到端点」的空跑距离；\n'
            '- 走到**最远请求**就掉头的 LOOK（本题口径）：不空跑，总长度更小。\n\n'
            '**常见错误**：\n\n'
            '1. 回程时又按升序服务（忘了掉头后方向相反，应该降序）；\n'
            '2. 忽略 `direction`，一律先升序（本题 down 的检查就是抓这个）；\n'
            '3. 与 head 重合的请求被漏掉或放到回程里；\n'
            '4. 初始方向没有请求时还硬走到端点（多出一段不存在的寻道距离）。\n\n'
            '复杂度：时间 O(n log n)（排序）、空间 O(n)。'
        ),
        'expected_output': "[65, 67, 98, 122, 124, 183, 37, 14]\n299\n[37, 14, 65, 67, 98, 122, 124, 183]\n208\n([30, 20, 10], 90)",
        'hints': [
            '把请求按方向切成「去程」「回程」两段：up 是「大于等于 head 升序」+「小于 head 降序」',
            '掉头后方向相反，回程必须降序；初始方向没请求就直接掉头，不空跑到端点',
        ],
    },
    {
        'id': 'os-011',
        'track': 'algorithm',
        'chapter_id': 138,
        'chapter_title': '操作系统·死锁与银行家算法',
        'topic': '操作系统·死锁与银行家算法',
        'title': '银行家算法安全性检测（返回安全序列）',
        'difficulty': 3,
        'tags': ['死锁', '死锁避免', '银行家算法', '安全序列', 'Need 矩阵'],
        'statement': (
            '**题 40 · 银行家算法安全性检测**\n\n'
            '考点：银行家算法、死锁避免（操作系统大题）。\n\n'
            '老师的原题：输入可用资源向量、各进程最大需求矩阵、已分配矩阵，'
            '实现安全性检测算法。判断系统是否处于安全状态，是则返回安全序列，否则返回 False。\n\n'
            '——下面是判题需要写死的规格——\n\n'
            '**输入格式**（三个参数）：\n\n'
            '- `available`：一维列表，`available[j]` 是当前可用的第 j 类资源数量；\n'
            '- `max_need`：二维列表，`max_need[i][j]` 是进程 i 对第 j 类资源的最大需求；\n'
            '- `allocated`：二维列表，`allocated[i][j]` 是进程 i 已经拿到的第 j 类资源；\n'
            '- 进程用**下标** 0、1、2……标识；资源类数 = `len(available)`；\n'
            '- **Need（还需要多少）矩阵要你自己在函数里算**：'
            '`need[i][j] = max_need[i][j] - allocated[i][j]`。\n\n'
            '定义函数 `is_safe(available, max_need, allocated)`：\n\n'
            '- 返回**安全序列**（列表，元素是进程下标）：\n'
            '  按照这个顺序让每个进程拿到它还需要（Need）的全部资源并运行完、归还资源，'
            '每一步都能满足；\n'
            '- 若不存在这样的序列（系统不安全），返回布尔值 `False`'
            '（不是 `None`、不是空列表、不是 -1）；\n'
            '- **没有进程**（`max_need == []`）时返回空列表 `[]`（视为安全）；\n'
            '- 不能修改三个入参。\n\n'
            '**扫描规则（写死，避免安全序列不唯一带来的歧义）**：\n\n'
            '1. `work = available` 的**副本**；\n'
            '2. 每一轮都**从下标 0 开始**找第一个「尚未完成且 Need 的每一项都 ≤ work」的进程；\n'
            '3. 找到就让它完成：`work[j] += allocated[i][j]`，把它的下标加入序列；\n'
            '4. 一轮下来一个都找不到时，若还有进程没完成，系统**不安全**，返回 False；\n'
            '5. 所有进程都完成时返回安全序列。\n\n'
            '**判题用主数据（安全）**：\n\n'
            '```\n'
            'available = [3, 3, 2]\n'
            'max_need  = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n'
            'allocated = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n'
            '```\n\n'
            '手算提示：Need 是 `[[7,4,3], [1,2,2], [6,0,0], [0,1,1], [4,3,1]]`，'
            '一开始 work = [3,3,2]，只有 1 号进程（Need [1,2,2]）能先完成……'
            '参考的安全序列是 `[1, 3, 0, 2, 4]`（按上面的扫描规则）。\n\n'
            '**注意**：判题时校验的是「你返回的序列本身是不是一个合法的安全序列」'
            '（按定义一步步走一遍），而不是和某个标准答案逐位比较——'
            '安全序列可能不唯一，只要合法就算对。\n\n'
            '最后打印：主数据的结果；再打印一组不安全数据的结果'
            '`available = [0, 0]`、`max_need = [[3, 1], [1, 2], [2, 2]]`、'
            '`allocated = [[2, 1], [1, 1], [1, 1]]`；再打印单进程的例子'
            '`available = [1, 1]`、`max_need = [[2, 1]]`、`allocated = [[1, 0]]`。'
        ),
        'starter_code': (
            "def is_safe(available, max_need, allocated):\n"
            "    n = len(max_need)\n"
            "    m = len(available)\n"
            "    need = [[max_need[i][j] - allocated[i][j] for j in range(m)] for i in range(n)]\n"
            "    work = list(available)      # 副本！不能直接改 available\n"
            "    finish = [False] * n\n"
            "    seq = []\n"
            "    for _ in range(n):\n"
            "        # 从下标 0 起找第一个 Need 全部 <= work 的未完成进程；找不到就 return False\n"
            "        pass\n"
            "    return seq\n"
        ),
        'solution': (
            "def is_safe(available, max_need, allocated):\n"
            "    n = len(max_need)\n"
            "    m = len(available)\n"
            "    need = [[max_need[i][j] - allocated[i][j] for j in range(m)] for i in range(n)]\n"
            "    work = list(available)\n"
            "    finish = [False] * n\n"
            "    seq = []\n"
            "    for _ in range(n):\n"
            "        found = -1\n"
            "        for i in range(n):\n"
            "            if finish[i]:\n"
            "                continue\n"
            "            ok = True\n"
            "            for j in range(m):\n"
            "                if need[i][j] > work[j]:\n"
            "                    ok = False\n"
            "                    break\n"
            "            if ok:\n"
            "                found = i\n"
            "                break\n"
            "        if found == -1:\n"
            "            return False\n"
            "        for j in range(m):\n"
            "            work[j] += allocated[found][j]\n"
            "        finish[found] = True\n"
            "        seq.append(found)\n"
            "    return seq\n"
            "\n"
            "available = [3, 3, 2]\n"
            "max_need = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n"
            "allocated = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n"
            "print(is_safe(available, max_need, allocated))\n"
            "print(is_safe([0, 0], [[3, 1], [1, 2], [2, 2]], [[2, 1], [1, 1], [1, 1]]))\n"
            "print(is_safe([1, 1], [[2, 1]], [[1, 0]]))\n"
        ),
        'checks': [
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n_res = is_safe(_av, _mx, _al)\nassert isinstance(_res, list) and sorted(_res) == [0, 1, 2, 3, 4], '安全状态要返回列表形式的安全序列（每个进程下标恰好出现一次），实际 %r' % (_res,)",
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n_res = is_safe(_av, _mx, _al)\n_work = list(_av)\nfor _p in _res:\n    for _j in range(3):\n        assert _mx[_p][_j] - _al[_p][_j] <= _work[_j], '返回的序列不是安全序列：轮到进程 %d 时它还需要 %d 个第 %d 类资源，而当前可用只有 %d（完整序列 %r）' % (_p, _mx[_p][_j] - _al[_p][_j], _j, _work[_j], _res)\n    for _j in range(3):\n        _work[_j] += _al[_p][_j]\nassert all(_m >= 0 for _m in _work), '按返回的序列走完后 work 不应出现负数，实际 %r' % (_work,)",
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n_res = is_safe(_av, _mx, _al)\n_first = _res[0]\nassert all(_mx[_first][_j] - _al[_first][_j] <= _av[_j] for _j in range(3)), '安全序列的第一个进程必须一开始就能拿到它需要的全部资源（否则它不可能最先完成），实际首元素 %r' % (_first,)",
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n_r1 = is_safe(_av, _mx, _al)\nassert _av == [3, 3, 2] and _mx == [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]] and _al == [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]], '安全性检测不能改写入参（work 必须是 available 的副本），实际 %r / %r / %r' % (_av, _mx, _al)",
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\nassert is_safe(_av, _mx, _al) == is_safe(_av, _mx, _al) and is_safe(_av, _mx, _al) is not False, '同一组输入连续调用必须得到相同结果（不能受上一次调用的残留状态影响）'",
            "_av = [1, 2]\n_mx = [[3, 3], [2, 2], [4, 2]]\n_al = [[1, 1], [2, 0], [3, 1]]\n_res = is_safe(_av, _mx, _al)\nassert isinstance(_res, list) and sorted(_res) == [0, 1, 2], '这组数据是安全的，应返回 0/1/2 的一个排列，实际 %r' % (_res,)\n_work = list(_av)\nfor _p in _res:\n    for _j in range(2):\n        assert _mx[_p][_j] - _al[_p][_j] <= _work[_j], '这组数据返回的序列不可行：进程 %d 需要 %d 个第 %d 类资源，当前只有 %d（序列 %r）' % (_p, _mx[_p][_j] - _al[_p][_j], _j, _work[_j], _res)\n    for _j in range(2):\n        _work[_j] += _al[_p][_j]",
            "_av = [1, 2, 1]\n_mx = [[3, 2, 1], [1, 2, 1], [2, 2, 1], [1, 0, 0]]\n_al = [[2, 0, 0], [0, 1, 1], [2, 1, 0], [1, 0, 0]]\n_res = is_safe(_av, _mx, _al)\nassert isinstance(_res, list) and sorted(_res) == [0, 1, 2, 3], '四个进程的安全序列应包含 0~3 各一次，实际 %r' % (_res,)\n_work = list(_av)\nfor _p in _res:\n    for _j in range(3):\n        assert _mx[_p][_j] - _al[_p][_j] <= _work[_j], '四进程数据返回的序列不可行：进程 %d 的 Need 超过当前可用（序列 %r）' % (_p, _res)\n    for _j in range(3):\n        _work[_j] += _al[_p][_j]",
            "_av = [1, 2]\n_mx = [[3, 3], [2, 2], [4, 2]]\n_al = [[1, 1], [2, 0], [3, 1]]\n_copy = (list(_av), [list(r) for r in _mx], [list(r) for r in _al])\nis_safe(_av, _mx, _al)\nassert (_av, _mx, _al) == _copy, 'is_safe 只能读三个矩阵，不能改动它们（常见错误是 work 直接引用了 available），实际 %r / %r / %r' % (_av, _mx, _al)",
            "_av = [0, 0]\n_mx = [[3, 1], [1, 2], [2, 2]]\n_al = [[2, 1], [1, 1], [1, 1]]\n_res = is_safe(_av, _mx, _al)\nassert _res is False, '这组数据 Need 分别是 [1,0]、[0,1]、[1,1]，而可用资源是 [0,0]，谁都无法先完成，必须返回布尔值 False，实际 %r' % (_res,)",
            "_av = [0, 1]\n_mx = [[3, 2], [3, 2], [2, 0]]\n_al = [[1, 1], [1, 1], [1, 0]]\n_res = is_safe(_av, _mx, _al)\nassert _res is False, '三人都只差一个第 1 类资源（Need 是 [2,1]、[2,1]、[1,0]），但可用只有 [0,1]，构成死锁，必须返回 False，实际 %r' % (_res,)",
            "_res = is_safe([1, 1], [[2, 1]], [[1, 0]])\nassert _res is not False and list(_res) == [0], '单进程边界：Need = [1,1] 正好可以被满足，应返回 [0]，实际 %r' % (_res,)",
            "_res = is_safe([0, 0], [[1, 1]], [[1, 1]])\nassert _res is not False and list(_res) == [0], '单进程边界：Need 已经全是 0（它不需要更多资源），应立即返回 [0]，实际 %r' % (_res,)",
            "_res = is_safe([2, 0], [], [])\nassert list(_res) == [] and _res is not False, '没有进程时应返回空列表（视为安全），实际 %r' % (_res,)",
            "_res = is_safe([0, 0], [[0, 0], [0, 0]], [[0, 0], [0, 0]])\nassert isinstance(_res, list) and sorted(_res) == [0, 1], '所有 Need 都是 0 时每个进程都能立刻完成，应返回包含 0、1 的序列，实际 %r' % (_res,)",
            "_av = [3, 3, 2]\n_mx = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]\n_al = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]\n_res = is_safe(_av, _mx, _al)\n_seq2 = is_safe([3, 3, 2], [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]], [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]])\nassert _res == _seq2 and _res == [1, 3, 0, 2, 4], '按题面的扫描规则（每轮从下标 0 起找第一个可满足的进程），主数据的安全序列是 [1, 3, 0, 2, 4]，实际 %r' % (_res,)",
        ],
        'explanation': (
            '银行家算法把「死锁避免」变成一道可以照章执行的模拟题，判题只看两个问题：'
            '**有没有安全序列、序列本身合不合法**。\n\n'
            '**第一步：算 Need**\n\n'
            '```python\n'
            'need[i][j] = max_need[i][j] - allocated[i][j]\n'
            '```\n\n'
            '主数据算出来是 `[[7,4,3], [1,2,2], [6,0,0], [0,1,1], [4,3,1]]`。\n\n'
            '**第二步：一轮一轮找能完成的进程**（work 从 available 的副本出发）\n\n'
            '```\n'
            'work = [3,3,2]\n'
            '第 1 轮：0 号 Need[7,4,3] 不行（7>3）；1 号 [1,2,2] 行 → work += [2,0,0] = [5,3,2]\n'
            '第 2 轮：0 号 [7,4,3] 不行（7>5）；2 号 [6,0,0] 不行（6>5）；3 号 [0,1,1] 行 → work += [2,1,1] = [7,4,3]\n'
            '第 3 轮：0 号 [7,4,3] 行 → work += [0,1,0] = [7,5,3]\n'
            '第 4 轮：2 号 [6,0,0] 行 → work += [3,0,2] = [10,5,5]\n'
            '第 5 轮：4 号 [4,3,1] 行 → work += [0,0,2] = [10,5,7]\n'
            '```\n\n'
            '得到安全序列 `[1, 3, 0, 2, 4]`。注意每轮都要**从下标 0 重新扫**，'
            '所以 0 号在第 3 轮才被选中——「扫描顺序」决定了拿到的是哪一个安全序列。\n\n'
            '**为什么这样贪心一定对？** 如果存在某个安全序列，那么它的第一个进程'
            '一定是「当前 work 能满足」的；我们随便挑一个满足的进程让它先完成，'
            '只会让 work 变大（更宽裕），不会破坏后面序列的可行性。'
            '所以「找到就选、找不到才判定不安全」不会漏掉任何安全序列。\n\n'
            '**关键概念**：\n\n'
            '- **安全状态**：存在一个让所有进程都能顺利完成的顺序；'
            '**不安全状态**：这种顺序不存在（可能死锁，也可能只是运气好没死锁，'
            '但银行家算法一律拒绝再分配）；\n'
            '- 安全序列**不唯一**（主数据共有 16 个），所以判题只校验序列的合法性；\n'
            '- 银行家算法要求每个进程**预先声明最大需求**，并且「已分配 + 还需 = 最大需求」'
            '这个账要一直保持——这是它比死锁检测更保守的原因。\n\n'
            '**常见错误**：\n\n'
            '1. `work = available`（少了 `list(...)`）——直接改写了入参，'
            '第二次调用结果就错了（本题有专门的检查）；\n'
            '2. 判断条件写成 `need < work`（要求所有分量严格小于，'
            '其实**等于也可以**，进程拿到正好够用的资源就能跑完）；\n'
            '3. 进程完成后忘了把 `allocated[i]` 加回 work（只回收了 Need，账就错了）；\n'
            '4. 找不到可完成的进程时返回空列表或 None，而不是布尔 `False`；\n'
            '5. 把**已经完成**的进程又算一遍（要用 finish 标记）。\n\n'
            '复杂度：时间 O(n² × m)（最多 n 轮、每轮扫 n 个进程比 m 类资源）、空间 O(n × m)。'
        ),
        'expected_output': "[1, 3, 0, 2, 4]\nFalse\n[0]",
        'hints': [
            '先算 need[i][j] = max_need[i][j] - allocated[i][j]，work 一定要写 list(available) 做副本',
            '每轮从下标 0 起找第一个「未完成且 Need 各分量都 <= work」的进程，找到就把它的 allocated 加回 work；一轮找不到就 return False',
        ],
    },
]


