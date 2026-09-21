"""题库 · 操作系统篇（专题 134–136）。

写法约定与 qbank_408.py / qbank_algo.py 保持一致：
- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式。
- checks 只断言题面要求的东西，每条断言都带中文提示，覆盖空输入、单元素、
  空闲时间、全部阻塞等边界；断言里可以用 _out（学生全部标准输出）与 _src（全部源码）。
- 参考答案必须能通过自己那套断言（tools/verify_qbank.py 会逐题重跑一遍）。

操作系统是概念课，但题库必须是**可执行**的 Python。本文件的出题口径是把考点
「翻译成算法题」：

    进程与线程    进程状态机推演、PCB 结构、FCFS/SJF/RR/HRRN/SRTF 调度模拟、
                  上下文切换开销与 CPU 利用率、线程共享/私有资源、fork 进程计数
    同步与互斥    临界区四条准则、信号量 P/V 语义（负值 = 等待进程数）、
                  互斥锁、Peterson 算法、前趋图与同步信号量、读者-写者、
                  生产者-消费者、计数信号量（资源池）、哲学家进餐
    死锁与银行家  死锁四个必要条件与预防、资源分配图（等待图）找环、
                  死锁检测算法、死锁解除（最少撤销）、保证不死锁的最少资源数、
                  银行家算法的 Need 矩阵 / 安全性算法 / 资源请求三步 / 完整实现 /
                  枚举所有安全序列

关于线程：直接起真实线程会让判题结果不稳定（调度顺序不可控），所以本文件的
并发题目一律采用「模拟 / 状态推演」的写法：自己实现信号量类，用**手工给定的
操作序列**验证 P/V 的阻塞与唤醒语义，结果完全确定。

专题划分：
    134 操作系统·进程与线程        135 操作系统·同步与互斥
    136 操作系统·死锁与银行家算法
"""

# %s

QUESTIONS = [
    # ── 专题 134 操作系统·进程与线程 ────────────────────────
    {
        'id': 'os-201',
        'track': 'algorithm',
        'chapter_id': 139,
        'chapter_title': '操作系统·进程与线程进阶',
        'topic': '操作系统·进程与线程进阶',
        'title': '进程五状态模型的转换推演',
        'difficulty': 1,
        'tags': ['进程状态', '状态转换', '状态机'],
        'statement': (
            '进程的五状态模型：`新建 → 就绪 → 运行 → 终止`，运行中的进程还可能因等待'
            '事件而进入 `阻塞`。本题把状态图实现成一台「状态机」，按事件序列推演。\n\n'
            '**合法的事件与转换**（其余事件在当前状态下非法：直接忽略，状态不变）：\n\n'
            '```\n'
            '新建 --admit-----> 就绪      # 创建完成，进入就绪队列\n'
            '就绪 --dispatch--> 运行      # 被调度程序选中，分配 CPU\n'
            '运行 --timeout---> 就绪      # 时间片用完，回到就绪\n'
            '运行 --wait------> 阻塞      # 等待 I/O 或某个事件\n'
            '阻塞 --io_done---> 就绪      # 等待的事件出现，重新排队\n'
            '运行 --exit------> 终止\n'
            '```\n\n'
            '定义函数 `process_state(initial, events)`，返回一个**元组**：'
            '`(最终状态, 被忽略的非法事件个数)`。\n\n'
            '- `initial` 是初始状态，取值只能是 `新建`、`就绪`、`运行`、`阻塞`、`终止`；\n'
            '- `events` 是事件名组成的列表，可以是空列表；\n'
            '- 空事件列表返回 `(initial, 0)`。\n\n'
            '最后依次打印下面四种调用的结果：\n\n'
            '1. 从 `运行` 出发：`timeout`、`wait`、`io_done`、`dispatch`、`exit`；\n'
            '2. 从 `新建` 出发：`dispatch`、`admit`、`dispatch`、`exit`；\n'
            '3. 从 `阻塞` 出发：`wait`、`io_done`、`dispatch`、`timeout`；\n'
            '4. 从 `终止` 出发：`dispatch`、`exit`。'
        ),
        'starter_code': (
            "# 合法转换表：状态 -> {事件: 新状态}\n"
            "LEGAL = {\n"
            "    '新建': {'admit': '就绪'},\n"
            "    '就绪': {'dispatch': '运行'},\n"
            "    '运行': {'timeout': '就绪', 'wait': '阻塞', 'exit': '终止'},\n"
            "    '阻塞': {'io_done': '就绪'},\n"
            "    '终止': {},\n"
            "}\n\n"
            "def process_state(initial, events):\n"
            "    state = initial\n"
            "    ignored = 0\n"
            "    # 逐个事件查表：查不到就是非法事件，ignored 加一\n"
            "    pass\n"
        ),
        'solution': (
            "LEGAL = {\n"
            "    '新建': {'admit': '就绪'},\n"
            "    '就绪': {'dispatch': '运行'},\n"
            "    '运行': {'timeout': '就绪', 'wait': '阻塞', 'exit': '终止'},\n"
            "    '阻塞': {'io_done': '就绪'},\n"
            "    '终止': {},\n"
            "}\n"
            "\n"
            "def process_state(initial, events):\n"
            "    state = initial\n"
            "    ignored = 0\n"
            "    for event in events:\n"
            "        nxt = LEGAL.get(state, {}).get(event)\n"
            "        if nxt is None:\n"
            "            ignored += 1\n"
            "        else:\n"
            "            state = nxt\n"
            "    return state, ignored\n"
            "\n"
            "print(process_state('运行', ['timeout', 'wait', 'io_done', 'dispatch', 'exit']))\n"
            "print(process_state('新建', ['dispatch', 'admit', 'dispatch', 'exit']))\n"
            "print(process_state('阻塞', ['wait', 'io_done', 'dispatch', 'timeout']))\n"
            "print(process_state('终止', ['dispatch', 'exit']))\n"
        ),
        'checks': [
            "assert process_state('就绪', []) == ('就绪', 0), '空事件列表应原样返回 (就绪, 0)，实际 %r' % (process_state('就绪', []),)",
            "assert process_state('运行', []) == ('运行', 0), '空事件列表在任何状态下都返回 (initial, 0)'",
            "assert process_state('就绪', ['dispatch', 'wait', 'io_done']) == ('就绪', 0), '就绪-运行-阻塞-就绪 一路都是合法事件，被忽略数应为 0，实际 %r' % (process_state('就绪', ['dispatch', 'wait', 'io_done']),)",
            "assert process_state('就绪', ['dispatch', 'wait', 'io_done', 'dispatch', 'timeout', 'dispatch', 'exit']) == ('终止', 0), '走完全程应到 终止，全部事件合法，实际 %r' % (process_state('就绪', ['dispatch', 'wait', 'io_done', 'dispatch', 'timeout', 'dispatch', 'exit']),)",
            "assert process_state('运行', ['admit', 'timeout', 'exit']) == ('就绪', 2), '运行态不能 admit、就绪态不能 exit：两个事件都该被忽略，实际 %r' % (process_state('运行', ['admit', 'timeout', 'exit']),)",
            "assert process_state('新建', ['dispatch', 'admit', 'dispatch', 'exit']) == ('终止', 1), '新建态要先 admit，开头的 dispatch 应被忽略，实际 %r' % (process_state('新建', ['dispatch', 'admit', 'dispatch', 'exit']),)",
            "assert process_state('终止', ['dispatch', 'exit']) == ('终止', 2), '终止态不再接受任何事件（终止是吸收态），实际 %r' % (process_state('终止', ['dispatch', 'exit']),)",
            "assert process_state('阻塞', ['dispatch', 'wait']) == ('阻塞', 2), '阻塞态只能被 io_done 唤醒：dispatch 和 wait 都非法，实际 %r' % (process_state('阻塞', ['dispatch', 'wait']),)",
            "assert process_state('新建', ['exit', 'timeout', 'io_done', 'wait']) == ('新建', 4), '四个事件在新建态都不合法，状态应原地不动，实际 %r' % (process_state('新建', ['exit', 'timeout', 'io_done', 'wait']),)",
            "assert process_state('运行', ['exit', 'admit', 'wait']) == ('终止', 2), 'exit 到终止后 admit、wait 都非法，实际 %r' % (process_state('运行', ['exit', 'admit', 'wait']),)",
            "assert process_state('就绪', ['dispatch', 'timeout'] * 50) == ('就绪', 0), '来回切换 100 次后仍应回到就绪且没有非法事件，实际 %r' % (process_state('就绪', ['dispatch', 'timeout'] * 50),)",
            "_r = process_state('阻塞', ['io_done', 'io_done'])\nassert _r == ('就绪', 1), 'io_done 只有在阻塞态合法，第二次应被忽略，实际 %r' % (_r,)",
        ],
        'explanation': (
            '五状态模型是进程管理的总纲，要记住的是「哪些事件合法」而不是死背箭头：\n\n'
            '| 状态 | 能接受的事件 | 去向 |\n'
            '| --- | --- | --- |\n'
            '| 新建 | admit | 就绪 |\n'
            '| 就绪 | dispatch | 运行 |\n'
            '| 运行 | timeout / wait / exit | 就绪 / 阻塞 / 终止 |\n'
            '| 阻塞 | io_done | 就绪 |\n'
            '| 终止 | 无（吸收态） | — |\n\n'
            '几条容易考的规律：\n\n'
            '1. **阻塞态不能直接变运行**：事件出现后只能回到就绪队列重新竞争 CPU，'
            '「io_done 直接变成运行」是最常见的错误选项；\n'
            '2. **就绪态不能主动 wait**：还没拿到 CPU，谈不上等待 I/O；\n'
            '3. **终止是吸收态**：进程结束后不能再被调度；\n'
            '4. 运行 → 就绪（时间片到）与运行 → 阻塞（等待事件）是两条完全不同的边，'
            '前者是被剥夺 CPU，后者是主动让出。\n\n'
            '实现上就是一张 `状态 × 事件 → 状态` 的查表，查不到就忽略。'
            '复杂度：时间 O(len(events))、空间 O(1)（表是常量）。'
        ),
        'expected_output': "('终止', 2)\n('终止', 1)\n('就绪', 1)\n('终止', 2)",
        'hints': ['用一张 状态 -> {事件: 新状态} 的表来查，比写一长串 if 更不容易漏', '查不到的事件就 ignored 加一，状态不变'],
    },
    {
        'id': 'os-202',
        'track': 'algorithm',
        'chapter_id': 139,
        'chapter_title': '操作系统·进程与线程进阶',
        'topic': '操作系统·进程与线程进阶',
        'title': 'PCB 结构与就绪进程的选择',
        'difficulty': 1,
        'tags': ['PCB', '就绪队列', '优先级'],
        'statement': (
            '进程控制块（PCB）是进程存在的唯一标志，调度器靠它记录进程的运行情况。'
            '本题实现一个简化的 PCB 和「从就绪队列里挑一个进程」。\n\n'
            '按下面的定义写类（属性名、方法名必须一致）：\n\n'
            '```python\n'
            'class PCB:\n'
            '    def __init__(self, pid, arrival, need_time, priority=0):\n'
            '        # pid: 进程标识；arrival: 到达时间；need_time: 需要 CPU 的总时间\n'
            '        # priority: 优先级，数值越小优先级越高\n'
            '        # 新进程的 used_time（已运行时间）为 0，state（状态）为 就绪\n'
            '        ...\n'
            '```\n\n'
            '要求实现：\n\n'
            '- `remaining()`：返回还需要多少 CPU 时间（`need_time - used_time`）；\n'
            '- `is_finished()`：`used_time >= need_time` 时为 `True`；\n'
            '- `tick(n=1)`：让进程运行 `n` 个时间单位。运行时 `state` 变为 `运行`，'
            '`used_time` 累加（**最多加到 need_time，不能超过**）；'
            '累加后如果已经完成，`state` 变为 `终止`。'
            '进程已经是 `终止` 时再 `tick` 不应改变任何东西。返回本次实际运行的时间。\n\n'
            '再定义函数 `pick_next(processes)`：从 `processes` 里挑出**状态为 就绪**的进程中'
            '优先级最高的一个，返回它的 `pid`；优先级相同时返回 `pid` 较小（按字符串比较）的那个；'
            '没有就绪进程时返回 `None`。注意 `运行`、`阻塞`、`终止` 的进程都不参与挑选。\n\n'
            '最后构造 `a = PCB(\'P1\', 0, 5, priority=2)`、`b = PCB(\'P2\', 0, 3, priority=1)`、'
            '`c = PCB(\'P3\', 1, 4, priority=1)`，依次打印：'
            'a 的剩余时间 / 是否完成 / 状态；a 运行 3 个时间单位后的剩余时间与是否完成；'
            'a 再运行 10 个时间单位后的剩余时间与状态；`pick_next([a, b, c])`；`pick_next([])`。'
        ),
        'starter_code': (
            "class PCB:\n"
            "    def __init__(self, pid, arrival, need_time, priority=0):\n"
            "        pass\n\n"
            "    def remaining(self):\n"
            "        pass\n\n"
            "    def is_finished(self):\n"
            "        pass\n\n"
            "    def tick(self, n=1):\n"
            "        pass\n\n"
            "def pick_next(processes):\n"
            "    pass\n"
        ),
        'solution': (
            "class PCB:\n"
            "    def __init__(self, pid, arrival, need_time, priority=0):\n"
            "        self.pid = pid\n"
            "        self.arrival = arrival\n"
            "        self.need_time = need_time\n"
            "        self.priority = priority\n"
            "        self.used_time = 0\n"
            "        self.state = '就绪'\n"
            "\n"
            "    def remaining(self):\n"
            "        return self.need_time - self.used_time\n"
            "\n"
            "    def is_finished(self):\n"
            "        return self.used_time >= self.need_time\n"
            "\n"
            "    def tick(self, n=1):\n"
            "        if self.state == '终止':\n"
            "            return 0\n"
            "        self.state = '运行'\n"
            "        run = min(n, self.remaining())\n"
            "        self.used_time += run\n"
            "        if self.is_finished():\n"
            "            self.state = '终止'\n"
            "        return run\n"
            "\n"
            "def pick_next(processes):\n"
            "    ready = [p for p in processes if p.state == '就绪']\n"
            "    if not ready:\n"
            "        return None\n"
            "    ready.sort(key=lambda p: (p.priority, str(p.pid)))\n"
            "    return ready[0].pid\n"
            "\n"
            "a = PCB('P1', 0, 5, priority=2)\n"
            "b = PCB('P2', 0, 3, priority=1)\n"
            "c = PCB('P3', 1, 4, priority=1)\n"
            "print(a.remaining(), a.is_finished(), a.state)\n"
            "a.tick(3)\n"
            "print(a.remaining(), a.is_finished())\n"
            "a.tick(10)\n"
            "print(a.remaining(), a.state)\n"
            "print(pick_next([a, b, c]))\n"
            "print(pick_next([]))\n"
        ),
        'checks': [
            "_p = PCB('A', 0, 5, priority=1)\nassert _p.remaining() == 5 and _p.used_time == 0, '新进程的剩余时间应等于 need_time、used_time 为 0，实际 %r / %r' % (_p.remaining(), _p.used_time)",
            "_p = PCB('A', 0, 5)\nassert _p.state == '就绪' and _p.is_finished() is False, '新进程状态应是 就绪、is_finished() 应为 False，实际 %r' % (_p.state,)",
            "_p = PCB('A', 0, 5)\nassert _p.tick(2) == 2 and _p.used_time == 2 and _p.state == '运行', '运行 2 个时间单位后 used_time 应为 2、状态为 运行，实际 %r' % (_p.used_time,)",
            "_p = PCB('A', 0, 5)\n_p.tick(5)\nassert _p.used_time == 5 and _p.is_finished() is True and _p.state == '终止', '运行满 need_time 后应完成并变成 终止，实际 %r' % (_p.state,)",
            "_p = PCB('A', 0, 5)\n_p.tick(99)\nassert _p.used_time == 5, 'used_time 不能超过 need_time（多给的时间要被截断），实际 %r' % (_p.used_time,)",
            "_p = PCB('A', 0, 5)\n_p.tick(5)\n_p.tick(3)\nassert _p.used_time == 5 and _p.state == '终止', '终止后再 tick 不应改变任何东西，实际 %r' % (_p.used_time,)",
            "_a = PCB('P1', 0, 3, priority=2)\n_b = PCB('P2', 0, 3, priority=1)\nassert pick_next([_a, _b]) == 'P2', '优先级数值小的先被选中，实际 %r' % (pick_next([_a, _b]),)",
            "_a = PCB('P9', 0, 3, priority=1)\n_b = PCB('P1', 0, 3, priority=1)\nassert pick_next([_a, _b]) == 'P1', '优先级相同时 pid 小的先（按字符串比较），实际 %r' % (pick_next([_a, _b]),)",
            "_a = PCB('P1', 0, 3)\n_a.state = '阻塞'\n_b = PCB('P2', 0, 3)\n_b.state = '终止'\n_c = PCB('P3', 0, 3)\n_c.state = '运行'\nassert pick_next([_a, _b, _c]) is None, '阻塞 / 终止 / 运行 的进程都不在就绪队列里，应返回 None，实际 %r' % (pick_next([_a, _b, _c]),)",
            "assert pick_next([]) is None, '空列表应返回 None'",
            "_a = PCB('P1', 0, 10, priority=5)\n_a.state = '阻塞'\n_b = PCB('P2', 0, 10, priority=3)\n_c = PCB('P3', 0, 10, priority=3)\nassert pick_next([_a, _b, _c]) == 'P2', '跳过阻塞进程后，剩下两个同优先级取 pid 小的，实际 %r' % (pick_next([_a, _b, _c]),)",
            "_p = PCB('A', 0, 5)\n_p.tick(0)\nassert _p.used_time == 0 and _p.remaining() == 5, 'tick(0) 不应推进时间，实际 %r' % (_p.used_time,)",
        ],
        'explanation': (
            'PCB 里最要紧的三个字段就是本题用到的：`need_time`（总共要多少 CPU）、'
            '`used_time`（已经用了多少）、`state`（现在处于哪个状态）。'
            '调度算法算周转时间、响应时间时，都是从这几个字段推出来的。\n\n'
            '**`tick` 里的截断为什么要写？** 如果直接 `used_time += n`，'
            '给一个「还差 2 秒却运行 10 秒」的进程就会让 `used_time` 超过 `need_time`，'
            '于是 `remaining()` 变成负数，后面所有周转时间的计算全错。'
            '所以实际运行时间只能是 `min(n, remaining())`。\n\n'
            '**优先级方向**：教材里「优先级越高数值越小」（0 是最高优先级），'
            '本题沿用这个约定；写成 `max` 的话整题方向就反了。'
            '这也是考研选择题常设的坑：题目说「优先级为 1 的进程先执行」就不用你猜方向。\n\n'
            '**就绪队列的挑选顺序**用元组做 key 最省事：`(priority, pid)`——'
            '先比优先级，相同再比 pid，一次排序同时满足两条规则。\n\n'
            '复杂度：`tick` O(1)；`pick_next` 时间 O(n log n)（排序，也可以只扫一遍取最小 O(n)）、空间 O(1)。'
        ),
        'expected_output': '5 False 就绪\n2 False\n0 终止\nP2\nNone',
        'hints': ['used_time 累加时要截断到 need_time，否则 remaining() 会出现负数', 'pick_next 用 (priority, pid) 当排序键，一次就满足两条规则'],
    },
    {
        'id': 'os-203',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': 'FCFS 先来先服务调度与周转时间',
        'difficulty': 2,
        'tags': ['调度', 'FCFS', '周转时间', '带权周转时间'],
        'statement': (
            '**先来先服务（FCFS）**：按进程到达的先后顺序排队，谁先到谁先用 CPU；'
            '一个进程一旦上 CPU 就一直运行到结束（非抢占）。\n\n'
            '定义函数 `fcfs(procs)`：\n\n'
            '- 参数 `procs` 是 `(pid, arrival, burst)` 三元组组成的列表：'
            '进程标识、到达时间、需要运行的时间；\n'
            '- 返回一个字典，含六个键：\n'
            '  - `order`：进程的执行顺序（pid 列表）；\n'
            '  - `finish`：`{pid: 完成时间}`；\n'
            '  - `turnaround`：`{pid: 周转时间}`，**周转时间 = 完成时间 − 到达时间**；\n'
            '  - `weighted`：`{pid: 带权周转时间}`，**带权周转时间 = 周转时间 ÷ 服务时间**；\n'
            '  - `avg_turnaround`：平均周转时间（float）；\n'
            '  - `avg_weighted`：平均带权周转时间（float）。\n\n'
            '细节要求：\n\n'
            '- **CPU 可能空闲**：如果下一个进程还没到达，CPU 要等到它到达才开始运行'
            '（用 `now = max(now, arrival)`）；\n'
            '- 到达时间相同时按 pid 从小到大（按字符串比较）决定先后；\n'
            '- 字典的键顺序按 `procs` 里出现的顺序即可。\n\n'
            '最后打印两组数据的结果：\n\n'
            '1. `(\'P1\', 0, 3)`、`(\'P2\', 2, 6)`、`(\'P3\', 4, 4)`、`(\'P4\', 6, 5)`：'
            '打印 `order`、`finish`、`turnaround`，再打印保留 4 位小数的 `avg_weighted`；\n'
            '2. `(\'A\', 0, 2)`、`(\'B\', 5, 3)`（中间 CPU 要空闲 3 个时间单位）：'
            '打印 `finish` 与保留 2 位小数的 `avg_turnaround`。'
        ),
        'starter_code': (
            "def fcfs(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    for pid, arrival, burst in order:\n"
            "        # 先让 now 追上到达时间，再跑 burst 个时间单位\n"
            "        pass\n"
            "    pass\n"
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
            "r1 = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_weighted'], 4))\n"
            "r2 = fcfs([('A', 0, 2), ('B', 5, 3)])\n"
            "print(r2['finish'])\n"
            "print(round(r2['avg_turnaround'], 2))\n"
        ),
        'checks': [
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert _r['order'] == ['P1', 'P2', 'P3', 'P4'], 'FCFS 的执行顺序就是到达顺序，实际 %r' % (_r['order'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert _r['finish'] == {'P1': 3, 'P2': 9, 'P3': 13, 'P4': 18}, '完成时间应是 P1=3、P2=9、P3=13、P4=18，实际 %r' % (_r['finish'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert _r['turnaround'] == {'P1': 3, 'P2': 7, 'P3': 9, 'P4': 12}, '周转时间 = 完成 − 到达，实际 %r' % (_r['turnaround'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert round(_r['avg_turnaround'], 4) == 7.75, '平均周转时间应是 7.75，实际 %r' % (_r['avg_turnaround'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert round(_r['avg_weighted'], 4) == 1.7042, '平均带权周转时间应是 1.7042，实际 %r' % (_r['avg_weighted'],)",
            "_r = fcfs([('A', 0, 2), ('B', 5, 3)])\nassert _r['finish'] == {'A': 2, 'B': 8}, 'CPU 空闲时 B 要到 5 才开始、8 结束，实际 %r' % (_r['finish'],)",
            "_r = fcfs([('A', 0, 2), ('B', 5, 3)])\nassert round(_r['avg_turnaround'], 4) == 2.5, 'A 周转 2、B 周转 3，平均 2.5，实际 %r' % (_r['avg_turnaround'],)",
            "_r = fcfs([])\nassert _r['order'] == [] and _r['avg_turnaround'] == 0.0, '空列表不应除零，应返回空的统计结果，实际 %r' % (_r, )",
            "_r = fcfs([('X', 3, 4)])\nassert _r['finish'] == {'X': 7} and _r['turnaround'] == {'X': 4}, '只有一个进程时它就是 3 到达、7 结束，实际 %r' % (_r['finish'],)",
            "_r = fcfs([('B', 0, 4), ('A', 0, 2)])\nassert _r['order'] == ['A', 'B'], '同时到达时按 pid 从小到大排（A 先），实际 %r' % (_r['order'],)",
            "_r = fcfs([('P1', 0, 4), ('P2', 100, 1)])\nassert _r['finish'] == {'P1': 4, 'P2': 101}, '长空闲期也要正确推进时间，实际 %r' % (_r['finish'],)",
            "_r = fcfs([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert round(sum(_r['weighted'].values()) / 4, 6) == round(_r['avg_weighted'], 6), 'avg_weighted 应该是各进程带权周转时间的平均值，实际 %r' % (_r['avg_weighted'],)",
        ],
        'explanation': (
            'FCFS 的模拟只有一个循环，但两个细节决定成败：\n\n'
            '```python\n'
            'for pid, arrival, burst in order:\n'
            '    now = max(now, arrival)     # CPU 空闲到进程到达\n'
            '    now += burst\n'
            '    finish[pid] = now\n'
            '```\n\n'
            '`now = max(now, arrival)` 就是「CPU 空闲」的处理：如果 `now` 已经超过 '
            '`arrival`（前一个进程还没跑完），就接着跑；否则要等到 `arrival`。'
            '漏掉这一句，后面所有完成时间都会偏小。\n\n'
            '**四个时间指标一定要分清**（考研最爱在这里设选项）：\n\n'
            '- 周转时间 = 完成时间 − 到达时间（整个在系统里待了多久）；\n'
            '- 带权周转时间 = 周转时间 ÷ 服务时间（长作业跑得久是正常的，'
            '带权之后才公平）；\n'
            '- 等待时间 = 周转时间 − 服务时间（排队 + 等待 I/O，本题没有 I/O）；\n'
            '- 响应时间 = 首次获得 CPU − 提交时刻（分时系统更关心它）。\n\n'
            '**FCFS 的缺点**：对短作业不利。前面一个大作业在跑时，后面一堆短作业都得等，'
            '「带权周转时间」会非常大——这正是 SJF 要解决的问题。\n\n'
            '复杂度：时间 O(n log n)（排序）、空间 O(n)。'
        ),
        'expected_output': "['P1', 'P2', 'P3', 'P4']\n{'P1': 3, 'P2': 9, 'P3': 13, 'P4': 18}\n{'P1': 3, 'P2': 7, 'P3': 9, 'P4': 12}\n1.7042\n{'A': 2, 'B': 8}\n2.5",
        'hints': ['now = max(now, arrival) 处理 CPU 空闲；然后 now += burst 就是完成时间', '周转时间 = 完成 − 到达；带权周转 = 周转 ÷ 服务时间'],
    },
    {
        'id': 'os-204',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': 'SJF 短作业优先（非抢占）调度',
        'difficulty': 2,
        'tags': ['调度', 'SJF', '周转时间'],
        'statement': (
            '**短作业优先（SJF）**：每次要调度时，从「已经到达而且还没结束」的进程里'
            '挑**服务时间最短**的那个运行到结束（本题是非抢占版本，不能把正在跑的进程踢下去）。\n\n'
            '定义函数 `sjf(procs)`，参数与返回值和上一题的 FCFS **完全一样**'
            '（`order` / `finish` / `turnaround` / `weighted` / `avg_turnaround` / `avg_weighted`）。\n\n'
            '细节要求：\n\n'
            '- 调度发生在「CPU 空闲」和「进程结束」这两个时刻：此时把所有已到达的进程都放进就绪队列，'
            '再从中选服务时间最短的；\n'
            '- **不要抢占**：进程一旦开始就运行到结束，中途到达的短作业只能等；\n'
            '- 服务时间相同时，先到达的优先；到达时间也相同则 pid 小的优先（按字符串比较）；\n'
            '- 同样要处理 CPU 空闲（`now = max(now, 下一个未完成进程的到达时间)`）。\n\n'
            '最后打印两组结果：\n\n'
            '1. `(\'P1\', 0, 7)`、`(\'P2\', 2, 4)`、`(\'P3\', 4, 1)`、`(\'P4\', 5, 4)`：'
            '打印 `order`、`finish`、`turnaround`、保留 4 位小数的 `avg_weighted`；\n'
            '2. `(\'P1\', 0, 7)`、`(\'P2\', 1, 1)`：用来验证「后来到达的短作业不会抢占」。'
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
            "        # ready 为空就先推进 now；否则挑 burst 最小的跑完\n"
            "        pass\n"
            "    pass\n"
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
            "r1 = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_weighted'], 4))\n"
            "r2 = sjf([('P1', 0, 7), ('P2', 1, 1)])\n"
            "print(r2['order'], r2['finish'])\n"
        ),
        'checks': [
            "_r = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert _r['order'] == ['P1', 'P3', 'P2', 'P4'], 'P1 跑完(时刻 7)后先做最短的 P3(1)，再做 P2(4)、P4(4)，实际 %r' % (_r['order'],)",
            "_r = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert _r['finish'] == {'P1': 7, 'P2': 12, 'P3': 8, 'P4': 16}, '完成时间应是 P1=7、P3=8、P2=12、P4=16，实际 %r' % (_r['finish'],)",
            "_r = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert _r['turnaround'] == {'P1': 7, 'P2': 10, 'P3': 4, 'P4': 11}, '周转时间应是 7 / 10 / 4 / 11，实际 %r' % (_r['turnaround'],)",
            "_r = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert round(_r['avg_turnaround'], 4) == 8.0, '平均周转时间应是 8.0，实际 %r' % (_r['avg_turnaround'],)",
            "_r = sjf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert round(_r['avg_weighted'], 4) == 2.5625, '平均带权周转时间应是 2.5625，实际 %r' % (_r['avg_weighted'],)",
            "_r = sjf([('P1', 0, 7), ('P2', 1, 1)])\nassert _r['order'] == ['P1', 'P2'], 'P2 虽然很短，但 P1 已经开跑，非抢占式不能把它踢下去，实际 %r' % (_r['order'],)",
            "_r = sjf([('A', 5, 3), ('B', 1, 2)])\nassert _r['order'] == ['B', 'A'] and _r['finish'] == {'B': 3, 'A': 8}, '要先推进到最早的到达时刻再调度，实际 %r' % (_r['finish'],)",
            "_r = sjf([('A', 0, 4), ('B', 0, 4), ('C', 0, 2)])\nassert _r['order'] == ['C', 'A', 'B'], '同时到达时先做短的，长度相同再按 pid，实际 %r' % (_r['order'],)",
            "_r = sjf([('A', 0, 5), ('B', 0, 5)])\nassert _r['order'] == ['A', 'B'] and _r['finish'] == {'A': 5, 'B': 10}, '服务时间相同时先到达者优先（同时到达则 pid 小的），实际 %r' % (_r['order'],)",
            "_r = sjf([])\nassert _r['order'] == [] and _r['avg_weighted'] == 0.0, '空列表应返回空结果且不能除零，实际 %r' % (_r,)",
            "_r = sjf([('X', 2, 3)])\nassert _r['finish'] == {'X': 5} and _r['turnaround'] == {'X': 3}, '单进程：5 结束、周转 3，实际 %r' % (_r['finish'],)",
            "_r = sjf([('P1', 0, 3), ('P2', 2, 6), ('P3', 4, 4), ('P4', 6, 5)])\nassert round(_r['avg_turnaround'], 4) == 7.75 and round(_r['avg_weighted'], 4) == 1.7042, 'P2 先到就得先跑完（非抢占），完成时刻依次 3 / 9 / 13 / 18，平均周转 7.75、平均带权 1.7042，实际 %r / %r' % (round(_r['avg_turnaround'], 4), round(_r['avg_weighted'], 4))",
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
            '**为什么 ready 为空时要 `continue` 而不是直接算？** 因为此时 CPU 空闲，'
            '必须先把 `now` 推到「下一个要到达的进程」的时刻，否则可能漏掉调度点。\n\n'
            '**SJF 的性质**（选择题常考）：\n\n'
            '1. 在所有进程同时到达的特殊情况下，SJF 的**平均等待时间 / 平均周转时间最小**，'
            '这是可以证明的最优性；\n'
            '2. 它需要预知服务时间（现实里只能估计），所以更像一种理论基准；\n'
            '3. 对长作业不利，长作业可能一直排在短作业后面（**饥饿**）；\n'
            '4. 抢占版本的 SJF 叫 **SRTF**（最短剩余时间优先），本题是非抢占版本，'
            '所以后来到达的短作业不能把正在跑的进程踢下去。\n\n'
            '复杂度：时间 O(n² log n)（最坏每轮排序一次）、空间 O(n)；n 很小时完全够用。'
        ),
        'expected_output': "['P1', 'P3', 'P2', 'P4']\n{'P1': 7, 'P3': 8, 'P2': 12, 'P4': 16}\n{'P1': 7, 'P2': 10, 'P3': 4, 'P4': 11}\n2.5625\n['P1', 'P2'] {'P1': 7, 'P2': 8}",
        'hints': ['每一轮从「已到达且未完成」里挑 burst 最小的，跑完再进入下一轮', 'ready 为空说明 CPU 空闲，要把 now 推到下一个到达时刻'],
    },
    {
        'id': 'os-205',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': '时间片轮转 RR 调度的时间线',
        'difficulty': 2,
        'tags': ['调度', '时间片轮转', 'RR', '时间线'],
        'statement': (
            '**时间片轮转（RR）**：就绪进程排成一个队列，每次让队首进程运行一个时间片；'
            '时间片用完还没结束就回到队尾重新排队。\n\n'
            '定义函数 `rr(procs, quantum)`：\n\n'
            '- `procs` 是 `(pid, arrival, burst)` 列表，`quantum` 是时间片长度（正整数）；\n'
            '- 返回一个字典：\n'
            '  - `timeline`：按时间顺序排列的 `(pid, 开始时刻, 结束时刻)` 列表，'
            '**每个时间片一段**；\n'
            '  - `finish`：`{pid: 完成时间}`；\n'
            '  - `turnaround`：`{pid: 周转时间}`；\n'
            '  - `avg_turnaround`：平均周转时间（float）。\n\n'
            '**调度规则（必须严格照做，否则时间线会差一格）**：\n\n'
            '1. 每一个时间片，队首进程运行 `min(quantum, 剩余时间)`；\n'
            '2. 进程运行**期间**到达的进程，按到达时刻先后加入队尾，'
            '**排在被本时间片挤下来的那个进程之前**；\n'
            '3. 到达时刻正好等于本时间片结束时刻的进程也算「运行期间到达」，同样先入队；\n'
            '4. 就绪队列为空而还有进程没到达时，CPU 空闲，时间推进到下一个到达时刻；\n'
            '5. 新到达的进程如果在 CPU 空闲时到达，直接开始运行（不必等一个完整时间片）。\n\n'
            '最后打印三组结果：\n\n'
            '1. `[(\'P1\', 0, 4), (\'P2\', 1, 3), (\'P3\', 2, 2)]`，`quantum=2`：'
            '打印 `timeline`、`finish`、`turnaround`；\n'
            '2. `[(\'P1\', 0, 3), (\'P2\', 1, 2), (\'P3\', 2, 1)]`，`quantum=1`：打印 `timeline`；\n'
            '3. `[(\'A\', 0, 1), (\'B\', 3, 1)]`，`quantum=2`：打印 `timeline`。'
        ),
        'starter_code': (
            "def rr(procs, quantum):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    remaining = {p[0]: p[2] for p in order}\n"
            "    now = 0\n"
            "    idx = 0\n"
            "    queue = []\n"
            "    timeline = []\n"
            "    finish = {}\n"
            "    # 队首出队 -> 跑 min(quantum, 剩余) -> 运行期间到达的先入队 -> 没跑完的再入队\n"
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
            "    timeline = []\n"
            "    finish = {}\n"
            "    while idx < n or queue:\n"
            "        if not queue:\n"
            "            now = max(now, order[idx][1])\n"
            "            while idx < n and order[idx][1] <= now:\n"
            "                queue.append(order[idx])\n"
            "                idx += 1\n"
            "        pid, arrival, burst = queue.pop(0)\n"
            "        run = min(quantum, remaining[pid])\n"
            "        start = now\n"
            "        now += run\n"
            "        remaining[pid] -= run\n"
            "        while idx < n and order[idx][1] <= now:\n"
            "            queue.append(order[idx])\n"
            "            idx += 1\n"
            "        if remaining[pid] > 0:\n"
            "            queue.append((pid, arrival, burst))\n"
            "        else:\n"
            "            finish[pid] = now\n"
            "        timeline.append((pid, start, now))\n"
            "    turnaround = {}\n"
            "    for pid, arrival, burst in order:\n"
            "        turnaround[pid] = finish[pid] - arrival\n"
            "    return {\n"
            "        'timeline': timeline,\n"
            "        'finish': finish,\n"
            "        'turnaround': turnaround,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\n"
            "print(r1['timeline'])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "r2 = rr([('P1', 0, 3), ('P2', 1, 2), ('P3', 2, 1)], 1)\n"
            "print(r2['timeline'])\n"
            "r3 = rr([('A', 0, 1), ('B', 3, 1)], 2)\n"
            "print(r3['timeline'])\n"
        ),
        'checks': [
            "_r = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\nassert _r['timeline'] == [('P1', 0, 2), ('P2', 2, 4), ('P3', 4, 6), ('P1', 6, 8), ('P2', 8, 9)], '时间线应是 P1(0-2) P2(2-4) P3(4-6) P1(6-8) P2(8-9)，实际 %r' % (_r['timeline'],)",
            "_r = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\nassert _r['finish'] == {'P3': 6, 'P1': 8, 'P2': 9}, '完成时间应是 P3=6、P1=8、P2=9，实际 %r' % (_r['finish'],)",
            "_r = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\nassert _r['turnaround'] == {'P1': 8, 'P2': 8, 'P3': 4}, '周转时间应是 P1=8、P2=8、P3=4，实际 %r' % (_r['turnaround'],)",
            "_r = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\nassert round(_r['avg_turnaround'], 4) == round(20 / 3, 4), '平均周转时间应是 20/3，实际 %r' % (_r['avg_turnaround'],)",
            "_r = rr([('P1', 0, 3), ('P2', 1, 2), ('P3', 2, 1)], 1)\nassert _r['timeline'] == [('P1', 0, 1), ('P2', 1, 2), ('P1', 2, 3), ('P3', 3, 4), ('P2', 4, 5), ('P1', 5, 6)], '时间片为 1 时每个进程轮流跑一格，实际 %r' % (_r['timeline'],)",
            "_r = rr([('P1', 0, 3), ('P2', 1, 2), ('P3', 2, 1)], 1)\nassert _r['finish'] == {'P3': 4, 'P2': 5, 'P1': 6}, '时间片为 1 时的完成时间应是 P3=4、P2=5、P1=6，实际 %r' % (_r['finish'],)",
            "_r = rr([('A', 0, 1), ('B', 3, 1)], 2)\nassert _r['timeline'] == [('A', 0, 1), ('B', 3, 4)], 'CPU 空闲时要等 B 到达再跑（不是从 0 连续算），实际 %r' % (_r['timeline'],)",
            "_r = rr([('A', 0, 10)], 3)\nassert _r['timeline'] == [('A', 0, 3), ('A', 3, 6), ('A', 6, 9), ('A', 9, 10)], '只有一个进程时它会连续跑完，最后一个时间片不足 quantum，实际 %r' % (_r['timeline'],)",
            "_r = rr([('A', 0, 4), ('B', 0, 4)], 4)\nassert _r['timeline'] == [('A', 0, 4), ('B', 4, 8)], '时间片不小于服务时间时 RR 退化成 FCFS，实际 %r' % (_r['timeline'],)",
            "_r = rr([('A', 0, 2), ('B', 0, 2), ('C', 0, 2)], 1)\nassert _r['finish'] == {'A': 4, 'B': 5, 'C': 6}, '三人各跑一格：A 在 3-4 结束、B 在 4-5、C 在 5-6，实际 %r' % (_r['finish'],)",
            "_r = rr([], 2)\nassert _r['timeline'] == [] and _r['avg_turnaround'] == 0.0, '空列表应返回空时间线且不除零，实际 %r' % (_r,)",
            "_r = rr([('P1', 0, 4), ('P2', 1, 3), ('P3', 2, 2)], 2)\nassert all(_r['timeline'][i][2] == _r['timeline'][i + 1][1] for i in range(len(_r['timeline']) - 1)), '时间线必须首尾相接（前一段的结束就是后一段的开始），实际 %r' % (_r['timeline'],)",
        ],
        'explanation': (
            'RR 的模拟难点只有一个：**入队的时机与顺序**。\n\n'
            '```python\n'
            'run = min(quantum, remaining[pid])\n'
            'start = now\n'
            'now += run\n'
            'while idx < n and order[idx][1] <= now:   # 运行期间到达的先入队\n'
            '    queue.append(order[idx]); idx += 1\n'
            'if remaining[pid] > 0:\n'
            '    queue.append(cur)                     # 时间片用完的自己排到最后\n'
            '```\n\n'
            '「运行期间到达的先入队、被挤下来的再排到它们后面」是教材的标准约定。'
            '写成「先把自己放回队列、再放新到达的」会让新进程永远排在旧进程后面，'
            '时间线整体错位——这是本题最容易丢分的地方。\n\n'
            '**时间片大小的权衡**（选择题常考）：\n\n'
            '- 时间片太大 → 退化成 FCFS，短作业的响应时间变差；\n'
            '- 时间片太小 → 进程切换次数剧增，切换开销吃掉 CPU（要按'
            '「切换时间 / (时间片 + 切换时间)」估算浪费比例）；\n'
            '- RR 对**短作业有利**（它很快就能拿到一个时间片），'
            '但**平均周转时间通常比 SJF 差**：长作业被切得七零八落，'
            '而且所有进程都要跟着等好几轮。\n\n'
            '注意 `now = max(now, order[idx][1])`：CPU 空闲时不能直接跑，'
            '要等到进程真的到达。\n\n'
            '复杂度：时间 O(n × 总时间片数)、空间 O(n)。'
        ),
        'expected_output': "[('P1', 0, 2), ('P2', 2, 4), ('P3', 4, 6), ('P1', 6, 8), ('P2', 8, 9)]\n{'P3': 6, 'P1': 8, 'P2': 9}\n{'P1': 8, 'P2': 8, 'P3': 4}\n[('P1', 0, 1), ('P2', 1, 2), ('P1', 2, 3), ('P3', 3, 4), ('P2', 4, 5), ('P1', 5, 6)]\n[('A', 0, 1), ('B', 3, 4)]",
        'hints': ['一个时间片结束时，先让「运行期间到达」的进程入队，再把没跑完的当前进程放到队尾', '就绪队列空了就 now = max(now, 下一个到达时刻)，别忘了 CPU 会空闲'],
    },
    {
        'id': 'os-206',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': 'HRRN 高响应比优先调度',
        'difficulty': 2,
        'tags': ['调度', 'HRRN', '响应比'],
        'statement': (
            '**高响应比优先（HRRN）**：每次调度时计算每个就绪进程的**响应比**，选最大的那个运行。\n\n'
            '```\n'
            '响应比 R = (等待时间 + 服务时间) / 服务时间 = 1 + 等待时间 / 服务时间\n'
            '等待时间 = 当前时刻 − 到达时刻\n'
            '```\n\n'
            '这个公式同时照顾了短作业（服务时间小 → R 大）和等待久的作业'
            '（等待时间长 → R 大），所以不会像 SJF 那样让长作业饿死。\n\n'
            '定义函数 `hrrn(procs)`，参数与返回值与 FCFS/SJF 一致'
            '（`order` / `finish` / `turnaround` / `weighted` / `avg_turnaround` / `avg_weighted`），'
            '另外多返回一个键 `ratios`：`{pid: 被选中时的响应比}`。\n\n'
            '细节要求：\n\n'
            '- 调度发生在 CPU 空闲或进程结束的时刻，从「已到达且未完成」的进程里选 R 最大的；\n'
            '- **R 相同时服务时间短的优先**，再相同则 pid 小的优先（按字符串比较）；\n'
            '- 比较 R 时建议 `round(R, 9)`，避免浮点误差导致同分不同判；\n'
            '- 非抢占：进程开始后运行到结束。\n\n'
            '最后打印两组结果：\n\n'
            '1. `(\'A\', 0, 2)`、`(\'B\', 2, 10)`、`(\'C\', 2, 1)`、`(\'D\', 3, 1)`：'
            '打印 `order`、`finish`、`ratios`、保留 4 位小数的 `avg_weighted`；\n'
            '2. `(\'A\', 0, 3)`、`(\'B\', 0, 1)`：验证同时到达时短作业先跑（R 都是 1）。'
        ),
        'starter_code': (
            "def hrrn(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    ratios = {}\n"
            "    seq = []\n"
            "    done = set()\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        # 响应比 = (now - arrival + burst) / burst，选最大的\n"
            "        pass\n"
            "    pass\n"
        ),
        'solution': (
            "def hrrn(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    now = 0\n"
            "    finish = {}\n"
            "    ratios = {}\n"
            "    seq = []\n"
            "    done = set()\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        if not ready:\n"
            "            now = min(p[1] for p in order if p[0] not in done)\n"
            "            continue\n"
            "        def rank(p):\n"
            "            r = (now - p[1] + p[2]) / p[2]\n"
            "            return (-round(r, 9), p[2], str(p[0]))\n"
            "        cur = sorted(ready, key=rank)[0]\n"
            "        ratios[cur[0]] = round((now - cur[1] + cur[2]) / cur[2], 4)\n"
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
            "        'ratios': ratios,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "        'avg_weighted': sum(weighted.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\n"
            "print(r1['order'])\n"
            "print(r1['finish'])\n"
            "print(r1['ratios'])\n"
            "print(round(r1['avg_weighted'], 4))\n"
            "r2 = hrrn([('A', 0, 3), ('B', 0, 1)])\n"
            "print(r2['order'])\n"
        ),
        'checks': [
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert _r['order'] == ['A', 'C', 'B', 'D'], 't=2 时 B、C 响应比都是 1，取短的 C；t=3 时 B 的响应比涨到 1.1 > D 的 1.0，所以轮到 B，实际 %r' % (_r['order'],)",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert _r['finish'] == {'A': 2, 'C': 3, 'B': 13, 'D': 14}, '完成时间应是 A=2、C=3、B=13、D=14，实际 %r' % (_r['finish'],)",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert _r['turnaround'] == {'A': 2, 'B': 11, 'C': 1, 'D': 11}, '周转时间应是 A=2、B=11、C=1、D=11，实际 %r' % (_r['turnaround'],)",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert round(_r['avg_weighted'], 4) == 3.525, '平均带权周转时间应是 3.525，实际 %r' % (_r['avg_weighted'],)",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert _r['ratios']['A'] == 1.0 and _r['ratios']['C'] == 1.0, '刚到达就被调度的进程响应比是 1.0，实际 %r' % (_r['ratios'],)",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert abs(_r['ratios']['B'] - 1.1) < 1e-9, 'B 在 t=3 被选中，等待 1、服务 10，响应比 = 11/10 = 1.1，实际 %r' % (_r['ratios'].get('B'),)",
            "_r = hrrn([('A', 0, 3), ('B', 0, 1)])\nassert _r['order'] == ['B', 'A'], '同时到达时响应比都是 1，服务时间短的先跑，实际 %r' % (_r['order'],)",
            "_r = hrrn([('A', 0, 4), ('B', 0, 4)])\nassert _r['order'] == ['A', 'B'], '响应比、服务时间都相同时按 pid 小的先，实际 %r' % (_r['order'],)",
            "_r = hrrn([('X', 5, 2)])\nassert _r['finish'] == {'X': 7} and _r['turnaround'] == {'X': 2}, '单进程：7 结束、周转 2，实际 %r' % (_r['finish'],)",
            "_r = hrrn([('A', 0, 1), ('B', 3, 1)])\nassert _r['finish'] == {'A': 1, 'B': 4}, 'CPU 空闲期要推进时间，实际 %r' % (_r['finish'],)",
            "assert hrrn([])['order'] == [], '空列表应返回空结果'",
            "_r = hrrn([('A', 0, 2), ('B', 2, 10), ('C', 2, 1), ('D', 3, 1)])\nassert round(_r['avg_turnaround'], 4) == 6.25, '平均周转时间应是 6.25，实际 %r' % (_r['avg_turnaround'],)",
        ],
        'explanation': (
            'HRRN 是「折中派」：SJF 只看服务时间，会让长作业饿死；FCFS 只看到达顺序，'
            '对短作业不公平。响应比把两者揉在一起：\n\n'
            '```\n'
            'R = 1 + 等待时间 / 服务时间\n'
            '```\n\n'
            '- 服务时间越短，R 的「基数」越大 → 偏向短作业；\n'
            '- 等待时间越长，R 涨得越快 → 长作业等久了也终会被选中（**不会饥饿**）。\n\n'
            '本题的关键时刻在 t=3：此时队列里有 B（等待 1、服务 10，R = 11/10 = 1.1）'
            '和新到达的 D（等待 0、服务 1，R = 1/1 = 1.0）。'
            '按 SJF 会选 D，按 HRRN 会选 B——这就是 HRRN 与 SJF 的分水岭，'
            '也是「长作业终于熬出头」的直观体现。\n\n'
            '**常见错误**：\n\n'
            '1. 公式写反（用服务时间 ÷ 等待时间）——那变成「服务时间越长越优先」，'
            '完全违背初衷；\n'
            '2. 忘了 `round(R, 9)`：`11/10` 这类小数在浮点里可能有 1e-16 的误差，'
            '严判「相同时取短的」时分不出高下；\n'
            '3. 忘记 CPU 空闲时推进时间。\n\n'
            'HRRN 需要每次调度都算一遍 R，开销比 FCFS/SJF 大；'
            '它同样是非抢占式的（抢占版本较少讨论）。\n\n'
            '复杂度：时间 O(n² log n)、空间 O(n)。'
        ),
        'expected_output': "['A', 'C', 'B', 'D']\n{'A': 2, 'C': 3, 'B': 13, 'D': 14}\n{'A': 1.0, 'C': 1.0, 'B': 1.1, 'D': 11.0}\n3.525\n['B', 'A']",
        'hints': ['响应比 = (等待时间 + 服务时间) / 服务时间，用 (等待 + burst) / burst 直接算', '比较时先 round(R, 9)，再按 (R 降序, burst 升序, pid 升序) 挑人'],
    },
    {
        'id': 'os-207',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': '进程切换开销与 CPU 利用率',
        'difficulty': 2,
        'tags': ['上下文切换', 'CPU 利用率', '开销'],
        'statement': (
            '进程切换本身要花时间：保存现场、切换页表、刷新快表，这些时间 CPU 什么正事都没干。'
            '本题计算**时间片轮转**下的切换开销与 CPU 利用率。\n\n'
            '模型（严格按这个来）：\n\n'
            '- `bursts` 是各进程需要运行的**总时间**，所有进程都在 0 时刻同时到达，'
            '就绪队列初始顺序就是 `bursts` 的顺序；\n'
            '- 时间片为 `quantum`，每个时间片运行 `min(quantum, 剩余时间)`；\n'
            '- **每执行一个时间片之前都要付一次 `switch_cost` 的切换开销，但第一个时间片不用付**'
            '（一开始没有「上一个进程」）；\n'
            '- 最后一个进程跑完就结束，不再有额外开销。\n\n'
            '定义函数 `rr_overhead(bursts, quantum, switch_cost)`，返回字典：\n\n'
            '- `switches`：切换次数（= 时间片数 − 1）；\n'
            '- `service`：所有进程真正使用 CPU 的总时间（就是 `sum(bursts)`）；\n'
            '- `total`：从 0 时刻到全部结束的总时间（含开销）；\n'
            '- `utilization`：CPU 利用率 = `service / total`，**保留 4 位小数**（用 `round`）。\n\n'
            '最后打印：\n\n'
            '1. `rr_overhead([6, 4, 2], 2, 1)`（三进程、时间片 2、每次切换 1）；\n'
            '2. `rr_overhead([6, 4, 2], 2, 0)`（切换不花时间）的 `utilization`；\n'
            '3. `rr_overhead([5], 2, 1)`（只有一个进程，不需要切换）。'
        ),
        'starter_code': (
            "def rr_overhead(bursts, quantum, switch_cost):\n"
            "    remaining = list(bursts)\n"
            "    queue = list(range(len(bursts)))\n"
            "    now = 0\n"
            "    slices = 0\n"
            "    # 出队 -> 若不是第一个时间片就先加 switch_cost -> 跑一个时间片 -> 没跑完回到队尾\n"
            "    pass\n"
        ),
        'solution': (
            "def rr_overhead(bursts, quantum, switch_cost):\n"
            "    remaining = list(bursts)\n"
            "    queue = list(range(len(bursts)))\n"
            "    now = 0\n"
            "    slices = 0\n"
            "    while queue:\n"
            "        i = queue.pop(0)\n"
            "        if slices > 0:\n"
            "            now += switch_cost\n"
            "        run = min(quantum, remaining[i])\n"
            "        now += run\n"
            "        remaining[i] -= run\n"
            "        slices += 1\n"
            "        if remaining[i] > 0:\n"
            "            queue.append(i)\n"
            "    service = sum(bursts)\n"
            "    return {\n"
            "        'switches': slices - 1 if slices else 0,\n"
            "        'service': service,\n"
            "        'total': now,\n"
            "        'utilization': round(service / now, 4) if now else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = rr_overhead([6, 4, 2], 2, 1)\n"
            "print(r1['switches'], r1['total'], r1['utilization'])\n"
            "r2 = rr_overhead([6, 4, 2], 2, 0)\n"
            "print(r2['utilization'])\n"
            "r3 = rr_overhead([5], 2, 1)\n"
            "print(r3['switches'], r3['total'], r3['utilization'])\n"
        ),
        'checks': [
            "_r = rr_overhead([6, 4, 2], 2, 1)\nassert _r['service'] == 12, 'service 就是总的服务时间 12，实际 %r' % (_r['service'],)",
            "_r = rr_overhead([6, 4, 2], 2, 1)\nassert _r['switches'] == 5, '6 个时间片应有 5 次切换，实际 %r' % (_r['switches'],)",
            "_r = rr_overhead([6, 4, 2], 2, 1)\nassert _r['total'] == 17, '总时间 = 12 服务 + 5 切换 = 17，实际 %r' % (_r['total'],)",
            "_r = rr_overhead([6, 4, 2], 2, 1)\nassert _r['utilization'] == 0.7059, 'CPU 利用率 = 12/17 = 0.7059（保留 4 位），实际 %r' % (_r['utilization'],)",
            "_r = rr_overhead([6, 4, 2], 2, 0)\nassert _r['utilization'] == 1.0 and _r['total'] == 12, '切换不花时间时利用率是 1.0、总时间等于服务时间，实际 %r / %r' % (_r['utilization'], _r['total'])",
            "_r = rr_overhead([5], 2, 1)\nassert _r['switches'] == 2, '按本题口径切换次数 = 时间片数 − 1：5 个单位时间、片长 2 要跑 3 个时间片，故切换 2 次，实际 %r' % (_r['switches'],)",
            "_r = rr_overhead([5], 2, 1)\nassert _r['total'] == 7 and round(_r['utilization'], 4) == round(5 / 7, 4), '3 个时间片要付 2 次开销：总时间 5 + 2 = 7，利用率 5/7 ≈ 0.7143，实际 %r / %r' % (_r['total'], _r['utilization'])",
            "_r = rr_overhead([1, 1], 1, 2)\nassert _r['switches'] == 1 and _r['total'] == 4, '两个各跑一格（2）+ 一次切换（2）= 4，实际 %r' % (_r['total'],)",
            "_r = rr_overhead([1, 1], 1, 2)\nassert _r['utilization'] == 0.5, '切换开销太大时利用率只有 0.5，实际 %r' % (_r['utilization'],)",
            "_r = rr_overhead([10], 3, 1)\nassert _r['switches'] == 3 and _r['total'] == 13, '10 秒分成 3+3+3+1 共 4 个时间片，3 次切换，实际 %r / %r' % (_r['switches'], _r['total'])",
            "_r = rr_overhead([2, 2], 2, 5)\nassert _r['switches'] == 1 and _r['total'] == 9, '时间片够大时每人只跑一次，只切换一次，实际 %r / %r' % (_r['switches'], _r['total'])",
            "_r = rr_overhead([], 2, 1)\nassert _r['switches'] == 0 and _r['total'] == 0 and _r['utilization'] == 0.0, '空列表不应除零，实际 %r' % (_r,)",
        ],
        'explanation': (
            '上下文切换的开销看着不起眼，算出来却很吓人：本题里 12 个时间单位的服务时间'
            '配了 5 次切换、每次 1 个时间单位，CPU 有 5/17 ≈ 29%% 的时间在做无用功。\n\n'
            '```\n'
            '利用率 = 服务时间 / (服务时间 + 切换次数 × 单次开销)\n'
            '```\n\n'
            '由此可以直接看出时间片的两难：\n\n'
            '- 时间片太小 → 切换次数暴涨。若每次切换要 0.1 ms、时间片 1 ms，'
            '利用率只有约 91%%；\n'
            '- 时间片太大 → 退化成 FCFS，交互式进程的响应时间变得不可接受。\n\n'
            '教材的结论是：时间片要**远大于**切换开销（典型取值是几十毫秒对几微秒），'
            '并且切换开销里最重的往往是**页表与 TLB 的更新**（换页表会刷新快表，'
            '之后所有访存都要重新填 TLB）。\n\n'
            '**常见错误**：\n\n'
            '1. 把第一次调度也算一次切换——第一个时间片前面没有「上一个进程」，不该收费；\n'
            '2. 最后一个进程结束后又加一次切换；\n'
            '3. 用 `总时间` 当分母算利用率时忘了把切换时间加进去（分母必须含开销）。\n\n'
            '复杂度：时间 O(时间片总数)、空间 O(n)。'
        ),
        'expected_output': '5 17 0.7059\n1.0\n2 7 0.7143',
        'hints': ['用 slices 计数：slices > 0 时，每个时间片前先加一次 switch_cost', 'switches = slices − 1（第一个时间片不算切换）；utilization = sum(bursts) / total'],
    },
    {
        'id': 'os-208',
        'track': 'algorithm',
        'chapter_id': 140,
        'chapter_title': '操作系统·进程调度进阶',
        'topic': '操作系统·进程调度进阶',
        'title': 'SRTF 最短剩余时间优先（抢占式 SJF）',
        'difficulty': 3,
        'tags': ['调度', 'SRTF', '抢占', '周转时间'],
        'statement': (
            '**最短剩余时间优先（SRTF）** = 抢占式的 SJF：每个时刻都挑「剩余时间最短」的进程运行；'
            '新到达的进程如果剩余时间更短，就**立刻抢占**正在运行的进程。\n\n'
            '定义函数 `srtf(procs)`，参数是 `(pid, arrival, burst)` 列表，返回字典：\n\n'
            '- `finish`：`{pid: 完成时间}`；\n'
            '- `turnaround`：`{pid: 周转时间}`；\n'
            '- `weighted`：`{pid: 带权周转时间}`；\n'
            '- `avg_turnaround`、`avg_weighted`：平均值（float）。\n\n'
            '**规则（按这个顺序判断，保证结果唯一）**：\n\n'
            '1. 每个时间单位重新挑一次：候选是「已经到达且还没完成」的进程；\n'
            '2. 选剩余时间最短的；**剩余时间相同时选 pid 小的**（按字符串比较）；\n'
            '3. 如果候选为空（CPU 空闲），时间直接推进到下一个进程的到达时刻；\n'
            '4. 字典的键按 pid 从小到大（字符串）排列，方便打印与比较。\n\n'
            '最后打印两组数据的结果（`finish`、`turnaround`、保留 4 位小数的 '
            '`avg_turnaround` 与 `avg_weighted`）：\n\n'
            '1. `(\'P1\', 0, 7)`、`(\'P2\', 2, 4)`、`(\'P3\', 4, 1)`、`(\'P4\', 5, 4)`；\n'
            '2. `(\'A\', 0, 4)`、`(\'B\', 1, 1)`（B 到达后应立刻抢占 A）。'
        ),
        'starter_code': (
            "def srtf(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    remaining = {p[0]: p[2] for p in order}\n"
            "    now = 0\n"
            "    done = set()\n"
            "    finish = {}\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        # ready 为空就跳到下一个到达时刻；否则挑剩余时间最短的跑 1 个时间单位\n"
            "        pass\n"
            "    pass\n"
        ),
        'solution': (
            "def srtf(procs):\n"
            "    order = sorted(procs, key=lambda p: (p[1], str(p[0])))\n"
            "    remaining = {p[0]: p[2] for p in order}\n"
            "    now = 0\n"
            "    done = set()\n"
            "    finish = {}\n"
            "    while len(done) < len(order):\n"
            "        ready = [p for p in order if p[1] <= now and p[0] not in done]\n"
            "        if not ready:\n"
            "            now = min(p[1] for p in order if p[0] not in done)\n"
            "            continue\n"
            "        cur = sorted(ready, key=lambda p: (remaining[p[0]], str(p[0])))[0]\n"
            "        remaining[cur[0]] -= 1\n"
            "        now += 1\n"
            "        if remaining[cur[0]] == 0:\n"
            "            finish[cur[0]] = now\n"
            "            done.add(cur[0])\n"
            "    turnaround = {}\n"
            "    weighted = {}\n"
            "    for pid, arrival, burst in sorted(order, key=lambda p: str(p[0])):\n"
            "        turnaround[pid] = finish[pid] - arrival\n"
            "        weighted[pid] = turnaround[pid] / burst\n"
            "    n = len(order)\n"
            "    return {\n"
            "        'finish': finish,\n"
            "        'turnaround': turnaround,\n"
            "        'weighted': weighted,\n"
            "        'avg_turnaround': sum(turnaround.values()) / n if n else 0.0,\n"
            "        'avg_weighted': sum(weighted.values()) / n if n else 0.0,\n"
            "    }\n"
            "\n"
            "r1 = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\n"
            "print(r1['finish'])\n"
            "print(r1['turnaround'])\n"
            "print(round(r1['avg_turnaround'], 4), round(r1['avg_weighted'], 4))\n"
            "r2 = srtf([('A', 0, 4), ('B', 1, 1)])\n"
            "print(r2['finish'], r2['turnaround'])\n"
        ),
        'checks': [
            "_r = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert _r['finish'] == {'P1': 16, 'P2': 7, 'P3': 5, 'P4': 11}, '完成时间应是 P1=16、P2=7、P3=5、P4=11，实际 %r' % (_r['finish'],)",
            "_r = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert _r['turnaround'] == {'P1': 16, 'P2': 5, 'P3': 1, 'P4': 6}, '周转时间应是 16 / 5 / 1 / 6，实际 %r' % (_r['turnaround'],)",
            "_r = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert round(_r['avg_turnaround'], 4) == 7.0, '平均周转时间应是 7.0，实际 %r' % (_r['avg_turnaround'],)",
            "_r = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert round(_r['avg_weighted'], 4) == 1.5089, '平均带权周转时间应是 1.5089，实际 %r' % (_r['avg_weighted'],)",
            "_r = srtf([('A', 0, 4), ('B', 1, 1)])\nassert _r['finish'] == {'A': 5, 'B': 2}, 'B 在 t=1 到达后立刻抢占（剩余 1 < A 的 3），A 要到 5 才完成，实际 %r' % (_r['finish'],)",
            "_r = srtf([('A', 0, 4), ('B', 1, 1)])\nassert round(_r['avg_turnaround'], 4) == 3.0, 'A 周转 5、B 周转 1，平均 3.0，实际 %r' % (_r['avg_turnaround'],)",
            "_r = srtf([('A', 0, 3), ('B', 0, 3)])\nassert _r['finish'] == {'A': 3, 'B': 6}, '剩余时间相同时按 pid 小的先跑（不会来回抢占），实际 %r' % (_r['finish'],)",
            "_r = srtf([('A', 5, 2)])\nassert _r['finish'] == {'A': 7} and _r['turnaround'] == {'A': 2}, '单进程且晚到达：7 完成、周转 2，实际 %r' % (_r['finish'],)",
            "assert srtf([])['finish'] == {}, '空列表应返回空字典'",
            "_r = srtf([('A', 0, 5), ('B', 0, 5), ('C', 0, 1)])\nassert _r['finish'] == {'C': 1, 'A': 6, 'B': 11}, 'C 最短(1) 先跑完；A 与 B 剩余相同，按 pid 小的先，A 一路跑到 6、B 再到 11，实际 %r' % (_r['finish'],)",
            "_r = srtf([('A', 0, 6), ('B', 2, 2), ('C', 3, 1)])\nassert _r['finish'] == {'B': 4, 'C': 5, 'A': 9}, 't=2 时 B(剩 2) 比 A(剩 4) 短，抢占；t=3 时 B、C 剩余都是 1，按 pid 小的先，B 先跑完(4)、C 接着(5)，最长的 A 最后(9)，实际 %r' % (_r['finish'],)",
            "_r = srtf([('P1', 0, 7), ('P2', 2, 4), ('P3', 4, 1), ('P4', 5, 4)])\nassert round(sum(_r['weighted'].values()) / 4, 6) == round(_r['avg_weighted'], 6), 'avg_weighted 应是各带权周转时间的平均值，实际 %r' % (_r['avg_weighted'],)",
        ],
        'explanation': (
            'SRTF 的模拟最朴素的写法是「一个时间单位一步」：\n\n'
            '```python\n'
            'while len(done) < len(order):\n'
            '    ready = [p for p in order if p[1] <= now and p[0] not in done]\n'
            '    if not ready:\n'
            '        now = min(p[1] for p in order if p[0] not in done)   # CPU 空闲\n'
            '        continue\n'
            '    cur = sorted(ready, key=lambda p: (remaining[p[0]], str(p[0])))[0]\n'
            '    remaining[cur[0]] -= 1\n'
            '    now += 1\n'
            '    if remaining[cur[0]] == 0:\n'
            '        finish[cur[0]] = now\n'
            '        done.add(cur[0])\n'
            '```\n\n'
            '每一步都重新挑人，抢占就自然发生了：**新进程一到达就进入候选集合**，'
            '如果它的剩余时间比当前进程短，下一时刻它就会胜出。\n\n'
            '注意「剩余时间相同选 pid 小的」这条仲裁规则：没有它，A、B 两个都剩 3 的进程'
            '会每个时间单位互相抢占，虽然完成时间数字可能一样，'
            '但过程（以及某些教辅给出的甘特图）就对不上了。\n\n'
            '**SRTF 的考点**：\n\n'
            '1. 它是抢占式的 SJF，**平均周转时间比 SJF 更短**（本题 7.0 与 SJF 的 8.0 对比），'
            '因为短作业一到就能抢到 CPU；\n'
            '2. 但**切换次数变多**，调度开销更大，而且长作业更惨（本题 P1 从 7 拖到 16）；\n'
            '3. 它同样要求预知服务时间，现实中只能用「历史运行时间」估计。\n\n'
            '复杂度：时间 O(总服务时间 × n)、空间 O(n)。'
        ),
        'expected_output': "{'P3': 5, 'P2': 7, 'P4': 11, 'P1': 16}\n{'P1': 16, 'P2': 5, 'P3': 1, 'P4': 6}\n7.0 1.5089\n{'B': 2, 'A': 5} {'A': 5, 'B': 1}",
        'hints': ['每个时间单位都重新从「已到达且未完成」里挑剩余时间最短的，抢占就自然发生', '剩�余时间相同时按 pid 小的优先，否则会来回抢占'],
    },
    {
        'id': 'os-209',
        'track': 'algorithm',
        'chapter_id': 139,
        'chapter_title': '操作系统·进程与线程进阶',
        'topic': '操作系统·进程与线程进阶',
        'title': '线程共享与私有的资源分类',
        'difficulty': 1,
        'tags': ['线程', '共享资源', '私有资源'],
        'statement': (
            '同一进程内的多个线程**共享**进程的绝大部分资源，但每个线程也有自己**私有**的'
            '运行现场。本题按下面的清单做分类。\n\n'
            '**线程之间共享**（属于进程）：`代码段`、`数据段`、`堆`、`打开的文件`、'
            '`当前工作目录`、`进程PID`、`信号处理函数`。\n\n'
            '**每个线程私有**：`程序计数器`、`寄存器组`、`线程栈`、`线程ID`、'
            '`线程局部存储`、`errno`。\n\n'
            '定义函数 `classify_thread_items(items)`：\n\n'
            '- 参数 `items` 是资源名字符串组成的列表（可能有重复、可能有清单以外的名字）；\n'
            '- 返回三元组 `(共享列表, 私有列表, 未知列表)`；\n'
            '- 三个列表都要**保持 items 里的相对顺序**，重复的名字保留（出现两次就放两次）；\n'
            '- 清单以外的名字放进「未知列表」。\n\n'
            '最后打印三次调用的结果：\n\n'
            '1. `[\'代码段\', \'线程栈\', \'堆\', \'线程ID\']`；\n'
            '2. `[\'数据段\', \'数据段\', \'寄存器组\', \'神奇资源\']`；\n'
            '3. `[]`（空列表）。'
        ),
        'starter_code': (
            "SHARED = {'代码段', '数据段', '堆', '打开的文件', '当前工作目录', '进程PID', '信号处理函数'}\n"
            "PRIVATE = {'程序计数器', '寄存器组', '线程栈', '线程ID', '线程局部存储', 'errno'}\n\n"
            "def classify_thread_items(items):\n"
            "    shared = []\n"
            "    private = []\n"
            "    unknown = []\n"
            "    # 依次判断每个名字属于哪一边，顺序要保持\n"
            "    pass\n"
        ),
        'solution': (
            "SHARED = {'代码段', '数据段', '堆', '打开的文件', '当前工作目录', '进程PID', '信号处理函数'}\n"
            "PRIVATE = {'程序计数器', '寄存器组', '线程栈', '线程ID', '线程局部存储', 'errno'}\n"
            "\n"
            "def classify_thread_items(items):\n"
            "    shared = []\n"
            "    private = []\n"
            "    unknown = []\n"
            "    for name in items:\n"
            "        if name in SHARED:\n"
            "            shared.append(name)\n"
            "        elif name in PRIVATE:\n"
            "            private.append(name)\n"
            "        else:\n"
            "            unknown.append(name)\n"
            "    return shared, private, unknown\n"
            "\n"
            "print(classify_thread_items(['代码段', '线程栈', '堆', '线程ID']))\n"
            "print(classify_thread_items(['数据段', '数据段', '寄存器组', '神奇资源']))\n"
            "print(classify_thread_items([]))\n"
        ),
        'checks': [
            "_s, _p, _u = classify_thread_items(['代码段', '线程栈', '堆', '线程ID'])\nassert _s == ['代码段', '堆'], '共享的应是代码段与堆（保持输入顺序），实际 %r' % (_s,)",
            "_s, _p, _u = classify_thread_items(['代码段', '线程栈', '堆', '线程ID'])\nassert _p == ['线程栈', '线程ID'], '私有的应是线程栈与线程ID，实际 %r' % (_p,)",
            "_s, _p, _u = classify_thread_items(['数据段', '数据段', '寄存器组', '神奇资源'])\nassert _s == ['数据段', '数据段'] and _p == ['寄存器组'] and _u == ['神奇资源'], '重复名字要保留两次、未知名字单独归一类，实际 %r / %r / %r' % (_s, _p, _u)",
            "_s, _p, _u = classify_thread_items([])\nassert (_s, _p, _u) == ([], [], []), '空列表应返回三个空列表，实际 %r' % ((_s, _p, _u),)",
            "_s, _p, _u = classify_thread_items(['程序计数器', '寄存器组', '线程栈', '线程局部存储', 'errno'])\nassert _s == [] and len(_p) == 5, '五个私有资源都不该出现在共享列表里，实际 %r / %r' % (_s, _p)",
            "_s, _p, _u = classify_thread_items(['打开的文件', '当前工作目录', '进程PID', '信号处理函数'])\nassert len(_s) == 4 and _p == [], '打开的文件、工作目录、PID、信号处理函数都是线程共享的，实际 %r' % (_s,)",
            "_s, _p, _u = classify_thread_items(['堆', '堆', '堆'])\nassert _s == ['堆', '堆', '堆'], '同一个名字出现三次就要放三次，实际 %r' % (_s,)",
            "_s, _p, _u = classify_thread_items(['不存在的资源'])\nassert _s == [] and _p == [] and _u == ['不存在的资源'], '清单外的名字只进未知列表，实际 %r / %r / %r' % (_s, _p, _u)",
            "_s, _p, _u = classify_thread_items(['线程栈', '代码段', '线程ID', '堆'])\nassert _s == ['代码段', '堆'] and _p == ['线程栈', '线程ID'], '结果顺序应与输入顺序一致（不是字典顺序），实际 %r / %r' % (_s, _p)",
            "_s, _p, _u = classify_thread_items(['errno', 'errno'])\nassert _p == ['errno', 'errno'], 'errno 是线程私有的（每个线程一套错误码），实际 %r' % (_p,)",
            "_s, _p, _u = classify_thread_items(['代码段', '程序计数器', '堆', '线程栈', '进程PID', '寄存器组'])\nassert len(_s) + len(_p) + len(_u) == 6, '分类不能丢元素也不能重复计入，实际 %r' % (len(_s) + len(_p) + len(_u),)",
        ],
        'explanation': (
            '线程被称为「轻量级进程」，轻就轻在**不拥有资源**：\n\n'
            '| 归谁 | 内容 |\n'
            '| --- | --- |\n'
            '| 进程（线程共享） | 代码段、数据段、堆、打开的文件、当前工作目录、进程 PID、信号处理函数 |\n'
            '| 线程（私有） | 程序计数器、寄存器组、栈、线程 ID、线程局部存储 TLS、errno |\n\n'
            '记忆线索：**「执行流要用的现场」是私有的，「资源和环境」是共享的**。'
            '每个线程都要能独立地被切换，所以必须有自己的 PC 和寄存器；'
            '函数调用要压栈，所以栈必须私有（否则两个线程的局部变量会互相踩）；'
            '而代码段、全局变量、堆、文件描述符表属于整个进程，所有线程看到的是同一份。\n\n'
            '**这也解释了为什么线程切换比进程切换便宜**：\n\n'
            '- 线程切换只要保存/恢复 PC、寄存器、栈指针，**不用换页表和地址空间**，'
            '因此不会刷新快表（TLB）；\n'
            '- 进程切换要换地址空间，TLB 与 Cache 大量失效，开销大得多。\n\n'
            '**常见错误**：把「堆」当成线程私有（堆是进程级的、所有线程共享的内存区域，'
            '`malloc` 出来的内存在同进程的其它线程里可以直接访问）；'
            '把 `errno` 当成全局共享（现代系统里 errno 是线程私有的，'
            '否则多线程下错误码会互相覆盖）。\n\n'
            '复杂度：时间 O(len(items))、空间 O(len(items))。'
        ),
        'expected_output': "(['代码段', '堆'], ['线程栈', '线程ID'], [])\n(['数据段', '数据段'], ['寄存器组'], ['神奇资源'])\n([], [], [])",
        'hints': ['用两个集合装清单，逐个判断名字属于哪一边', '三个结果列表都要按输入顺序 append，不能先排序'],
    },
    {
        'id': 'os-210',
        'track': 'algorithm',
        'chapter_id': 139,
        'chapter_title': '操作系统·进程与线程进阶',
        'topic': '操作系统·进程与线程进阶',
        'title': 'fork 调用后的进程数与打印次数',
        'difficulty': 2,
        'tags': ['fork', '创建进程', '进程数'],
        'statement': (
            '`fork()` 会创建一个子进程：**父进程和子进程都从 fork 之后继续往下执行**，'
            '区别只在返回值（子进程里返回 0，父进程里返回子进程的 pid）。'
            '因此循环里每 fork 一次，后续代码的执行者数量就翻倍。\n\n'
            '考察这段程序（`n` 是循环次数）：\n\n'
            '```python\n'
            'for i in range(n):\n'
            '    fork()        # 或 os.fork()\n'
            '    print(i)\n'
            '```\n\n'
            '定义函数 `fork_analysis(n)`，返回字典：\n\n'
            '- `processes`：程序结束时（所有 fork 完成后）的进程总数；\n'
            '- `counts`：列表，`counts[i]` 表示**数字 i 被打印了多少次**'
            '（也就是打印 `i` 的那条语句被多少个进程执行）；\n'
            '- `total_lines`：总打印行数（= `sum(counts)`）。\n\n'
            '注意 `n = 0` 时循环体一次都不执行：只有 1 个进程，什么都不打印。\n\n'
            '最后打印 `n = 0`、`n = 1`、`n = 3`、`n = 5` 四次调用的结果。'
        ),
        'starter_code': (
            "def fork_analysis(n):\n"
            "    processes = 2 ** n\n"
            "    counts = []\n"
            "    # 打印 i 的进程数：i 之前已经 fork 了 i+1 次\n"
            "    pass\n"
        ),
        'solution': (
            "def fork_analysis(n):\n"
            "    processes = 2 ** n\n"
            "    counts = []\n"
            "    for i in range(n):\n"
            "        counts.append(2 ** (i + 1))\n"
            "    return {\n"
            "        'processes': processes,\n"
            "        'counts': counts,\n"
            "        'total_lines': sum(counts),\n"
            "    }\n"
            "\n"
            "print(fork_analysis(0))\n"
            "print(fork_analysis(1))\n"
            "print(fork_analysis(3))\n"
            "print(fork_analysis(5)['processes'], fork_analysis(5)['total_lines'])\n"
        ),
        'checks': [
            "_r = fork_analysis(0)\nassert _r['processes'] == 1 and _r['counts'] == [] and _r['total_lines'] == 0, 'n=0 时只有 1 个进程、一次都不打印，实际 %r' % (_r,)",
            "_r = fork_analysis(1)\nassert _r['processes'] == 2 and _r['counts'] == [2] and _r['total_lines'] == 2, 'n=1：fork 出 2 个进程，两个都打印 0，实际 %r' % (_r,)",
            "_r = fork_analysis(2)\nassert _r['processes'] == 4, 'n=2 时进程数是 2 的 2 次方 = 4，实际 %r' % (_r['processes'],)",
            "_r = fork_analysis(2)\nassert _r['counts'] == [2, 4], 'n=2：数字 0 被 2 个进程打印、数字 1 被 4 个进程打印，实际 %r' % (_r['counts'],)",
            "_r = fork_analysis(3)\nassert _r['processes'] == 8 and _r['counts'] == [2, 4, 8], 'n=3：8 个进程，counts 是 [2, 4, 8]，实际 %r' % (_r,)",
            "_r = fork_analysis(3)\nassert _r['total_lines'] == 14, 'n=3 的总行数 = 2+4+8 = 14，实际 %r' % (_r['total_lines'],)",
            "_r = fork_analysis(5)\nassert _r['processes'] == 32 and _r['total_lines'] == 62, 'n=5：32 个进程、总行数 2 的 6 次方减 2 = 62，实际 %r' % (_r,)",
            "_r = fork_analysis(10)\nassert _r['processes'] == 1024 and _r['total_lines'] == 2046, 'n=10：1024 个进程、2046 行，实际 %r' % (_r,)",
            "_r = fork_analysis(4)\nassert _r['counts'] == [2, 4, 8, 16], 'n=4 的 counts 应是 [2, 4, 8, 16]，实际 %r' % (_r['counts'],)",
            "assert fork_analysis(6)['total_lines'] == sum(fork_analysis(6)['counts']), 'total_lines 必须等于 counts 各元素之和'",
            "_r = fork_analysis(7)\nassert _r['processes'] == 128 and len(_r['counts']) == 7, 'n=7：进程数 128、counts 有 7 项，实际 %r' % (_r,)",
        ],
        'explanation': (
            '关键是数清楚「打印第 i 个数字时，系统里已经有几个进程」。\n\n'
            '执行轨迹：\n\n'
            '```\n'
            '开始:        1 个进程\n'
            '第 1 次 fork: 2 个进程  → 两个都执行 print(0)   → 2 行\n'
            '第 2 次 fork: 4 个进程  → 四个都执行 print(1)   → 4 行\n'
            '第 3 次 fork: 8 个进程  → 八个都执行 print(2)   → 8 行\n'
            '```\n\n'
            '所以数字 i 被打印 `2^(i+1)` 次，总行数 `2 + 4 + ... + 2^n = 2^(n+1) − 2`，'
            '而进程总数是 `2^n`（注意最后那次 fork 之后没有打印语句了，'
            '所以进程数比「最后一行打印者数量」少一半）。\n\n'
            '**为什么 fork 之后父子都往后执行？** 因为 fork 复制了父进程的地址空间与执行现场，'
            '两个进程的 PC 都停在下一条语句上，谁先被调度是不确定的（可能交错执行）。'
            '判断这类题目只要记住一条：**fork 是「复制当前执行流」，从此一分为二**。\n\n'
            '**常见错误**：\n\n'
            '1. 认为「父进程 fork 完继续跑、子进程只执行一次」——那 prints 就会少一半；\n'
            '2. 把进程总数写成 `2^(n+1) − 1`（把最初那个也数重了）：只有 n 次 fork，'
            '进程数是 `2^n`；\n'
            '3. 忘记 `n = 0` 的平凡情况（1 个进程、0 行）。\n\n'
            '如果把 `fork()` 换成 `pthread_create()` 创建线程，程序里的进程数始终是 1，'
            '但**线程数**同样会翻倍——这正是「进程是资源分配单位、线程是调度单位」的体现。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': "{'processes': 1, 'counts': [], 'total_lines': 0}\n{'processes': 2, 'counts': [2], 'total_lines': 2}\n{'processes': 8, 'counts': [2, 4, 8], 'total_lines': 14}\n32 62",
        'hints': ['第 i 次 fork 之后进程数翻倍，所以 print(i) 的执行者数量是 2 的 (i+1) 次方', '总行数是等比数列求和：2 + 4 + ... + 2 的 n 次方 = 2 的 (n+1) 次方 减 2'],
    },
    # __APPEND_POINT__
]
