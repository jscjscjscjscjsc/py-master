"""题库 · 操作系统考研风格题库（第二批：专题 137–139）。

写法约定与 qbank_408.py / qbank_basic.py 等保持一致：

- statement 面向学生，必须写清「要定义什么名字的函数」以及输入输出的类型与格式；
  所有参数（页大小、内存大小、引用串、磁头位置、请求序列……）都在题面里给死，不让学生猜。
- checks 只断言题面要求的东西，每条断言都带中文提示，并覆盖空输入、单元素、
  全命中、越界、成环等边界情况。
- 参考答案本身必须能通过同一套断言（题库改了就要重跑 tools/verify_qbank.py）。

本文件覆盖的三个专题（chapter_id 从 137 起，避免与课程章节 1–40 和
算法专题 101–126 冲突）：

    137 操作系统·内存与分页   地址转换、页表与多级页表、EAT 与 TLB、
                              缺页中断与 FIFO / LRU / OPT / Clock 页面置换、
                              分段与段页式、页面分配策略、内存碎片与紧凑
    138 操作系统·文件与磁盘   文件的物理结构（连续 / 链接 / 索引与多级索引）、
                              目录与 inode、FAT、位示图与成组链接、
                              FCFS / SSTF / SCAN / C-SCAN / LOOK 磁盘调度、
                              磁盘访问时间
    139 操作系统·调度与综合   作业 / 进程调度（FCFS、SJF、RR、HRRN、SRTF）、
                              PV 操作与信号量、银行家算法、CPU 利用率与吞吐量、
                              分页与调度的组合题、多道批处理系统综合推演

出题口径：把统考里「手算表格 + 写结论」的操作系统大题翻译成可执行的 Python 题——
题面给出算法规则与数据，学生写函数返回计算结果，判题用断言核对。
凡是教材上有多种口径的地方（SCAN 是否走到端点、位示图 0/1 的含义、
OPT 并列时淘汰谁、RR 队列的入队顺序……）都在题面里写死，避免「学生写对了却被判错」。
"""

# %s

QUESTIONS = [
    # ── 专题 137 操作系统·内存与分页 ─────────────────────
    {
        'id': 'os-301',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': '逻辑地址拆分与页式地址转换',
        'difficulty': 1,
        'tags': ['分页', '地址转换', '页号', '页内偏移'],
        'statement': (
            '在页式存储管理中，逻辑地址被分成「页号」和「页内偏移」两部分，'
            '页表给出每个页对应的**物理块号**（页框号）。\n\n'
            '定义两个函数：\n\n'
            '1. `split_address(logical_addr, page_size)`：返回二元组 `(页号, 页内偏移)`。\n'
            '   计算口径：`页号 = logical_addr // page_size`、`页内偏移 = logical_addr % page_size`'
            '（等价于把地址右移 log2(页大小) 位取高位、低位留给偏移）。\n'
            '2. `translate(logical_addr, page_size, page_table)`：返回**物理地址**；'
            '   出现下面两种情况时返回 `None`：\n\n'
            '   - 页号 ≥ `len(page_table)`：**越界**（地址超出该进程的页表范围）；\n'
            '   - 页表项是 `None`：该页不在内存，发生**缺页中断**。\n\n'
            '   物理地址 = 物理块号 × 页大小 + 页内偏移。\n\n'
            '参数说明：`logical_addr` 是非负整数（十进制），`page_size` 是 2 的整数次幂'
            '（本题用到 4096 和 1024），`page_table` 是列表，第 i 项就是页号 i 对应的物理块号，'
            '`None` 表示缺页。函数不要修改 `page_table`。\n\n'
            '参考计算：页大小 4096 B 时，逻辑地址 8315 = 2 × 4096 + 123，'
            '所以页号 2、偏移 123；若页表是 `[5, 1, 3, None]`，页 2 在物理块 3，'
            '物理地址 = 3 × 4096 + 123 = 12411。\n\n'
            '最后打印 `split_address(8315, 4096)`、`translate(8315, 4096, [5, 1, 3, None])`、'
            '一个越界地址的转换结果和一个缺页地址的转换结果。'
        ),
        'starter_code': (
            'def split_address(logical_addr, page_size):\n'
            '    # 页号 = 地址 // 页大小，偏移 = 地址 % 页大小\n'
            '    pass\n\n'
            'def translate(logical_addr, page_size, page_table):\n'
            '    # 先拆地址，再查页表；越界或缺页都返回 None\n'
            '    pass\n'
        ),
        'solution': (
            "def split_address(logical_addr, page_size):\n"
            "    return logical_addr // page_size, logical_addr % page_size\n"
            "\n"
            "def translate(logical_addr, page_size, page_table):\n"
            "    page_no, offset = split_address(logical_addr, page_size)\n"
            "    if page_no >= len(page_table):\n"
            "        return None\n"
            "    frame = page_table[page_no]\n"
            "    if frame is None:\n"
            "        return None\n"
            "    return frame * page_size + offset\n"
            "\n"
            "print(split_address(8315, 4096))\n"
            "print(translate(8315, 4096, [5, 1, 3, None]))\n"
            "print(translate(4096 * 4, 4096, [5, 1, 3, None]))\n"
            "print(translate(4096, 4096, [5, None, 3, 7]))\n"
        ),
        'checks': [
            "assert split_address(0, 4096) == (0, 0), '地址 0 应拆成页号 0、偏移 0，实际 %r' % (split_address(0, 4096),)",
            "assert split_address(8315, 4096) == (2, 123), '8315 = 2 × 4096 + 123，应拆成 (2, 123)，实际 %r' % (split_address(8315, 4096),)",
            "assert split_address(4095, 4096) == (0, 4095), '一页的最后一个字节（4095）页号仍是 0、偏移 4095，实际 %r' % (split_address(4095, 4096),)",
            "assert split_address(4096, 4096) == (1, 0), '4096 正好是第 1 页的第 0 个字节，实际 %r' % (split_address(4096, 4096),)",
            "assert split_address(12345, 1024) == (12, 57), '页大小换成 1024 时 12345 = 12 × 1024 + 57，实际 %r' % (split_address(12345, 1024),)",
            "_pt = [5, 1, 3, None]\nassert translate(8315, 4096, _pt) == 12411, '页 2 在物理块 3，物理地址 = 3 × 4096 + 123 = 12411，实际 %r' % (translate(8315, 4096, _pt),)",
            "_pt = [5, 1, 3, None]\nassert translate(0, 4096, _pt) == 20480, '页 0 在物理块 5，物理地址 = 5 × 4096 = 20480，实际 %r' % (translate(0, 4096, _pt),)",
            "_pt = [5, 1, 3, 7]\nassert translate(4096 * 3, 4096, _pt) == 28672, '最后一页（页 3）在物理块 7，物理地址 = 7 × 4096 = 28672，实际 %r' % (translate(4096 * 3, 4096, _pt),)",
            "_pt = [5, 1, 3, None]\nassert translate(4096 * 4, 4096, _pt) is None, '页号 4 超出页表长度（越界），应返回 None，实际 %r' % (translate(4096 * 4, 4096, _pt),)",
            "_pt = [5, None, 3, 7]\nassert translate(4096, 4096, _pt) is None, '页表项为 None 表示缺页中断，应返回 None，实际 %r' % (translate(4096, 4096, _pt),)",
            "_pt = [2, 4, 6, 8, 10, 12]\nassert translate(5000, 1024, _pt) == 11144, '页大小 1024 时 5000 属于页 4、偏移 904，物理地址 = 10 × 1024 + 904 = 11144，实际 %r' % (translate(5000, 1024, _pt),)",
            "_pt = [5, 1, 3, None]\n_copy = list(_pt)\ntranslate(12345, 4096, _pt)\nassert _pt == _copy, 'translate 只做查询，不应该修改传入的页表，实际 %r' % (_pt,)",
        ],
        'explanation': (
            '分页地址转换就一条公式，先拆后拼：\n\n'
            '```python\n'
            '页号 = logical_addr // page_size      # 等价于右移 log2(page_size) 位\n'
            '偏移 = logical_addr % page_size       # 等价于取低 log2(page_size) 位\n'
            '物理地址 = 物理块号 * page_size + 偏移\n'
            '```\n\n'
            '页大小取 2 的幂正是为了让「除法 / 取余」和「移位 / 掩码」等价，'
            '硬件里用后者，一行门电路就能算出来。\n\n'
            '**两个必须查的边界**：\n\n'
            '1. **越界**：页号 ≥ 页表长度时地址非法，必须拦截，否则 `page_table[page_no]` 直接 IndexError；\n'
            '2. **缺页**：页表项为空说明该页不在内存，硬件会触发缺页中断把它调进来，'
            '在这里的表现就是「得不到物理地址」，返回 None。注意缺页不是错误，'
            '只是这条转换路径暂时走不通。\n\n'
            '**常见错误**：\n\n'
            '1. 把偏移算成 `logical_addr - page_size`（应该是取余，不是做减法）；\n'
            '2. 忘记乘页大小，直接把「物理块号 + 偏移」当物理地址（块号是页号单位的，必须先放大）；\n'
            '3. 没有越界检查，页号刚好等于 `len(page_table)` 时越界访问抛异常；\n'
            '4. 忘记 `None`（缺页）这一支，`None * page_size` 会抛 TypeError。\n\n'
            '复杂度：时间 O(1)、额外空间 O(1)。'
        ),
        'expected_output': '(2, 123)\n12411\nNone\nNone',
        'hints': [
            '页号用整除、偏移用取余，最后别忘了「物理块号 × 页大小」',
            '越界（页号 ≥ 页表长度）和缺页（表项是 None）都要返回 None',
        ],
    },
    {
        'id': 'os-302',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': '页表规模计算（单级页表与两级页表的内存开销）',
        'difficulty': 1,
        'tags': ['页表', '多级页表', '页表项', '内存开销'],
        'statement': (
            '本题计算页表本身要占多少内存。约定：**每个页表恰好占一页**'
            '（一页能放下 `page_size // pte_size` 个页表项，这个位数记作「每级页号位数」）。\n\n'
            '定义函数 `page_table_sizes(addr_bits, page_size, pte_size, levels)`，'
            '返回四元组 `(offset_bits, page_bits, top_entries, total_bytes)`：\n\n'
            '- `offset_bits`：页内偏移的位数 = log2(page_size)；\n'
            '- `page_bits`：页号的位数 = addr_bits − offset_bits；\n'
            '- `top_entries`：**顶级页表**的页表项个数；\n'
            '  · `levels == 1` 时只有一级页表，`top_entries = 2 ** page_bits`；\n'
            '  · `levels == 2` 时每级页号位数 `bits_per_level = log2(page_size // pte_size)`，'
            '    顶级页表项数 `top_entries = 2 ** (page_bits - bits_per_level)`；\n'
            '- `total_bytes`：**整个页表体系**占用的字节数（按全映射、每个页表占满一页计算）：\n'
            '  · 单级：`top_entries × pte_size`（页表连续存放，占多少算多少）；\n'
            '  · 两级：`(1 + top_entries) × page_size`（1 个顶级页表 + top_entries 个二级页表，'
            '    每个页表都占一页）。\n\n'
            '本题只考「页号位数 > 每级页号位数」的正常配置，不需要处理退化情况。\n\n'
            '参考计算：32 位地址、页大小 4 KB(4096 B)、页表项 4 B：\n\n'
            '- 偏移 12 位、页号 20 位，页表项个数 2²⁰ = 1048576，单级页表占 1048576 × 4 = 4194304 B = 4 MB；\n'
            '- 两级时每级 10 位（4096 / 4 = 1024 = 2¹⁰），顶级 2¹⁰ = 1024 项，'
            '  总占用 = (1 + 1024) × 4096 = 4198400 B（4 MB + 4 KB）。\n\n'
            '最后打印 32 位 / 4 KB / 4 B 在单级和两级下的结果，以及 32 位 / 4 KB / 8 B 两级的结果。'
        ),
        'starter_code': (
            'def page_table_sizes(addr_bits, page_size, pte_size, levels):\n'
            '    offset_bits = 0\n'
            '    page_bits = 0\n'
            '    # 先算偏移位数与页号位数，再按单级 / 两级分别算项数与总字节\n'
            '    pass\n'
        ),
        'solution': (
            "def page_table_sizes(addr_bits, page_size, pte_size, levels):\n"
            "    offset_bits = 0\n"
            "    size = page_size\n"
            "    while size > 1:\n"
            "        size //= 2\n"
            "        offset_bits += 1\n"
            "    page_bits = addr_bits - offset_bits\n"
            "    if levels == 1:\n"
            "        top_entries = 2 ** page_bits\n"
            "        total_bytes = top_entries * pte_size\n"
            "        return offset_bits, page_bits, top_entries, total_bytes\n"
            "    bits_per_level = 0\n"
            "    entries_per_page = page_size // pte_size\n"
            "    while entries_per_page > 1:\n"
            "        entries_per_page //= 2\n"
            "        bits_per_level += 1\n"
            "    top_entries = 2 ** (page_bits - bits_per_level)\n"
            "    total_bytes = (1 + top_entries) * page_size\n"
            "    return offset_bits, page_bits, top_entries, total_bytes\n"
            "\n"
            "print(page_table_sizes(32, 4096, 4, 1))\n"
            "print(page_table_sizes(32, 4096, 4, 2))\n"
            "print(page_table_sizes(32, 4096, 8, 2))\n"
        ),
        'checks': [
            "assert page_table_sizes(32, 4096, 4, 1) == (12, 20, 1048576, 4194304), '32 位 / 4 KB / 4 B 单级页表：偏移 12 位、页号 20 位、1048576 项、4 MB，实际 %r' % (page_table_sizes(32, 4096, 4, 1),)",
            "assert page_table_sizes(32, 4096, 4, 2) == (12, 20, 1024, 4198400), '32 位 / 4 KB / 4 B 两级页表：顶级 1024 项、总占用 (1 + 1024) × 4096 = 4198400 B，实际 %r' % (page_table_sizes(32, 4096, 4, 2),)",
            "assert page_table_sizes(32, 4096, 8, 2) == (12, 20, 2048, 8392704), '页表项 8 B 时每页只能放 512 项（9 位），顶级页表 2^11 = 2048 项、总占用 2049 × 4096 = 8392704 B，实际 %r' % (page_table_sizes(32, 4096, 8, 2),)",
            "assert page_table_sizes(32, 8192, 4, 1) == (13, 19, 524288, 2097152), '页大小 8 KB 时偏移 13 位、页号 19 位，单级页表 524288 项共 2097152 B，实际 %r' % (page_table_sizes(32, 8192, 4, 1),)",
            "assert page_table_sizes(64, 4096, 8, 1) == (12, 52, 4503599627370496, 36028797018963968), '64 位地址、4 KB 页、8 B 表项：页号 52 位，单级页表的项数与字节数都极大（2^52 项、2^55 B），实际 %r' % (page_table_sizes(64, 4096, 8, 1),)",
            "assert page_table_sizes(32, 1024, 4, 1) == (10, 22, 4194304, 16777216), '页大小 1 KB 时偏移 10 位、页号 22 位，单级页表 4194304 项共 16 MB，实际 %r' % (page_table_sizes(32, 1024, 4, 1),)",
            "assert page_table_sizes(32, 1024, 4, 2) == (10, 22, 16384, 16778240), '1 KB 页两级页表：每级 8 位（1024 / 4 = 256），顶级 2^14 = 16384 项，总占用 (1 + 16384) × 1024 = 16778240 B，实际 %r' % (page_table_sizes(32, 1024, 4, 2),)",
            "_r1 = page_table_sizes(32, 4096, 4, 1)\n_r2 = page_table_sizes(32, 4096, 4, 2)\nassert _r1[0] == _r2[0] and _r1[1] == _r2[1], '单级和两级只影响页表项数与占用，偏移位数和页号位数是一样的（都应 12 / 20），实际 %r / %r' % (_r1, _r2)",
            "_r = page_table_sizes(32, 4096, 4, 2)\nassert _r[2] * 4 == 4096, '两级页表的顶级页表要恰好占一页（1024 项 × 4 B = 4096 B），实际 %r B' % (_r[2] * 4,)",
        ],
        'explanation': (
            '页表为什么要分级？因为**页表必须连续存放在内存里**，'
            '单级页表的项数等于「页数」，页数越多，页表越大，还得找一大块连续内存放它。\n\n'
            '以 32 位 / 4 KB / 4 B 为例：\n\n'
            '```\n'
            '页内偏移 12 位 → 页号 20 位 → 页数 2^20 = 1048576\n'
            '单级页表：1048576 × 4 B = 4 MB（必须连续！）\n'
            '两级页表：页号拆成 10 + 10，顶级页表 1024 项 = 4 KB（正好一页）\n'
            '          每个二级页表也是一页，全映射时共 1024 个 → (1 + 1024) × 4 KB\n'
            '```\n\n'
            '**关键点**：拆分页号的位数由「一个页表能放多少个表项」决定：'
            '`page_size // pte_size` 个表项，位数就是 log2 它。'
            '4 KB 页、4 B 表项 → 1024 项 → 每级 10 位。'
            '这样每个页表刚好占一页，既好分配又不需要连续内存。\n\n'
            '**为什么两级反而更省？** 因为进程用到的地址空间是稀疏的：'
            '只有真正用到的二级页表才需要建立，题面里的 total_bytes 是「全映射」的上界，'
            '实际占用远小于这个数。相反，单级页表的 4 MB 是**必须实打实分配**的。\n\n'
            '**常见错误**：\n\n'
            '1. 把「页表项个数」算成 `2 ** addr_bits`（忘记减掉偏移位数）；\n'
            '2. 把 `page_size // pte_size` 当成长度而不是「项数」，位数算成「除法」而不是「取以 2 为底的对数」；\n'
            '3. 两级页表的总占用忘记加上顶级页表本身那一页；\n'
            '4. 单位混乱：1 KB = 1024 B，4 MB 是 4194304 B 而不是 4000000 B。\n\n'
            '复杂度：时间 O(log page_size)、额外空间 O(1)。'
        ),
        'expected_output': '(12, 20, 1048576, 4194304)\n(12, 20, 1024, 4198400)\n(12, 20, 2048, 8392704)',
        'hints': [
            '偏移位数 = log2(页大小)，页号位数 = 地址位数 − 偏移位数',
            '两级时每级页号位数 = log2(页大小 // 页表项大小)，顶级项数 = 2 **（页号位数 − 每级位数）',
        ],
    },
    {
        'id': 'os-303',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': '动态分区分配：首次适应与最佳适应',
        'difficulty': 2,
        'tags': ['内存管理', '动态分区', '首次适应', '最佳适应', '外部碎片'],
        'statement': (
            '动态分区分配中，空闲分区用列表表示：每个元素是二元组 `(起始地址, 大小)`，'
            '列表**按起始地址递增**排列，相邻分区之间不会重叠。\n\n'
            '定义三个函数：\n\n'
            '1. `first_fit(free_blocks, requests)`：按**首次适应**处理每个请求，'
            '返回处理完全部请求后的空闲分区表（元组列表、按地址递增、**去掉大小为 0 的分区**）。\n'
            '   规则：对每个请求依次扫描空闲分区表，找到**第一个**「大小 ≥ 请求大小」的分区，'
            '从它的**低地址端**切出请求大小：'
            '分区的起始地址加上请求大小、大小减去请求大小（相减后为 0 就删除这个分区）；'
            '   若没有任何分区放得下，**该请求无法分配，直接跳过**，继续处理下一个请求。\n'
            '2. `best_fit(free_blocks, requests)`：同样返回处理完全部请求后的空闲分区表，'
            '但每次选的是**能放下的最小分区**（容量相同就选地址小的那个）；同样从低地址端切出。\n'
            '3. `free_total(free_blocks)`：返回空闲分区表里所有分区的**大小之和**（即剩余空闲空间总量）。\n\n'
            '两个函数都**不能修改**传入的 `free_blocks`（返回新列表）。\n\n'
            '参考计算：空闲分区 `[(100, 200), (400, 50), (600, 30)]`，请求 `[40, 100]`：\n\n'
            '- 首次适应先给 40 用 100 号分区（剩 (140, 160)），再给 100 继续用这个分区（剩 (240, 60)），'
            '结果 `[(240, 60), (400, 50), (600, 30)]`；\n'
            '- 最佳适应先给 40 用 400 号分区（50 是最小的够用分区，剩 (440, 10)），'
            '再给 100 用 100 号分区（剩 (200, 100)），结果 `[(200, 100), (440, 10), (600, 30)]`。\n\n'
            '最后打印上面例子的两个结果，以及一个「请求太大、谁都装不下」的例子。'
        ),
        'starter_code': (
            'def first_fit(free_blocks, requests):\n'
            '    holes = [(start, size) for start, size in free_blocks]\n'
            '    # 每个请求找第一个放得下的分区，从低地址端切一刀\n'
            '    pass\n\n'
            'def best_fit(free_blocks, requests):\n'
            '    # 每个请求找「最小的、放得下的」分区\n'
            '    pass\n\n'
            'def free_total(free_blocks):\n'
            '    pass\n'
        ),
        'solution': (
            "def first_fit(free_blocks, requests):\n"
            "    holes = [(start, size) for start, size in free_blocks]\n"
            "    for need in requests:\n"
            "        for i in range(len(holes)):\n"
            "            start, size = holes[i]\n"
            "            if size >= need:\n"
            "                holes[i] = (start + need, size - need)\n"
            "                break\n"
            "    return [(start, size) for start, size in holes if size > 0]\n"
            "\n"
            "def best_fit(free_blocks, requests):\n"
            "    holes = [(start, size) for start, size in free_blocks]\n"
            "    for need in requests:\n"
            "        pick = -1\n"
            "        for i in range(len(holes)):\n"
            "            start, size = holes[i]\n"
            "            if size >= need:\n"
            "                if pick == -1 or size < holes[pick][1]:\n"
            "                    pick = i\n"
            "        if pick >= 0:\n"
            "            start, size = holes[pick]\n"
            "            holes[pick] = (start + need, size - need)\n"
            "    return [(start, size) for start, size in holes if size > 0]\n"
            "\n"
            "def free_total(free_blocks):\n"
            "    total = 0\n"
            "    for start, size in free_blocks:\n"
            "        total += size\n"
            "    return total\n"
            "\n"
            "blocks = [(100, 200), (400, 50), (600, 30)]\n"
            "print(first_fit(blocks, [40, 100]))\n"
            "print(best_fit(blocks, [40, 100]))\n"
            "print(blocks)\n"
            "print(first_fit([(100, 60), (200, 100)], [70, 150, 80]))\n"
        ),
        'checks': [
            "_ff = first_fit([(100, 200), (400, 50), (600, 30)], [40, 100])\nassert _ff == [(240, 60), (400, 50), (600, 30)], '首次适应应先切 100 号分区：40 与 100 连续从同一分区切出，结果 [(240, 60), (400, 50), (600, 30)]，实际 %r' % (_ff,)",
            "_bf = best_fit([(100, 200), (400, 50), (600, 30)], [40, 100])\nassert _bf == [(200, 100), (440, 10), (600, 30)], '最佳适应应先用最小的够用分区 50：40 切在 400、100 切在 100，结果 [(200, 100), (440, 10), (600, 30)]，实际 %r' % (_bf,)",
            "assert first_fit([], [10]) == [], '没有空闲分区时任何请求都装不下，应返回空表'",
            "assert first_fit([(100, 50)], []) == [(100, 50)], '请求序列为空时应原样返回空闲分区表，实际 %r' % (first_fit([(100, 50)], []),)",
            "assert first_fit([(100, 50)], [50]) == [], '请求大小正好等于分区大小时应把这个分区整块切走（相减为 0 的分区要删掉）'",
            "assert best_fit([(100, 50)], [50]) == [], '最佳适应遇到「正好装满」时同样应删掉这个分区'",
            "_ff = first_fit([(100, 60), (200, 100)], [70, 150, 80])\nassert _ff == [(100, 60), (270, 30)], '第一个请求 70 用 200 号分区（剩 (270, 30)），后两个请求（150、80）都装不下应跳过，实际 %r' % (_ff,)",
            "_bf = best_fit([(100, 60), (200, 100)], [70, 150, 80])\nassert _bf == [(100, 60), (270, 30)], '最佳适应在这组数据下与首次适应结果相同，实际 %r' % (_bf,)",
            "_ff = first_fit([(100, 50), (200, 150), (400, 80), (600, 200)], [90, 60, 40, 100])\nassert _ff == [(140, 10), (400, 80), (700, 100)], '首次适应：90 用 200 号、60 用 290 号（正好装满）、40 用 100 号（剩 (140, 10)）、100 用 600 号（剩 (700, 100)），实际 %r' % (_ff,)",
            "_bf = best_fit([(100, 50), (200, 150), (400, 80), (600, 200)], [90, 60, 40, 100])\nassert _bf == [(140, 10), (400, 80), (700, 100)], '最佳适应在这组数据下与首次适应结果相同，实际 %r' % (_bf,)",
            "_blocks = [(100, 200), (400, 50), (600, 30)]\n_copy = list(_blocks)\nfirst_fit(_blocks, [40])\nbest_fit(_blocks, [40])\nassert _blocks == _copy, '两个函数都不能修改传入的空闲分区表，实际 %r' % (_blocks,)",
            "_ff = first_fit([(100, 200), (400, 50), (600, 30)], [40, 100])\nassert free_total(_ff) == 140, '结果表里空闲空间总量 = 60 + 50 + 30 = 140，实际 %r' % (free_total(_ff),)",
            "assert free_total([]) == 0, '空空闲表的总量是 0，实际 %r' % (free_total([]),)",
        ],
        'explanation': (
            '两种分配算法只差在「挑哪个分区」：\n\n'
            '```python\n'
            '# 首次适应：遇到第一个装得下的就用（不用继续往后看）\n'
            '# 最佳适应：把所有装得下的都比一遍，选最小的那个\n'
            '```\n\n'
            '**首次适应**的优点是快（平均不需要扫描全部空闲区）'
            '而且低地址部分被优先使用，容易留下高地址的大块连续空间；'
            '缺点是低地址一端会积累很多小的、再也用不上的碎片。\n\n'
            '**最佳适应**看起来「最省」，实际上会切出大量比请求大一点点的碎片'
            '（比如剩 (440, 10) 这种 10 个字节的空洞，几乎永远用不上），'
            '所以有「最佳适应是最坏策略」的说法。\n'
            '上一条「两者结果相同」的检查正说明：数据不同时，两种算法的差距可能显现不出来。\n\n'
            '**外部碎片**就是这些小到谁都塞不进、又不相邻的空闲区；'
            '本题的 `free_total` 统计的是「还剩下多少空闲空间」，'
            '它大于「能装下的最大请求」。要真正利用这些碎片，得靠**紧凑**（挪动进程把空闲区拼起来）。\n\n'
            '**常见错误**：\n\n'
            '1. 切分区时只减大小、不改起始地址（那样分区会「原地缩水」，地址错了）；\n'
            '2. 忘记删除大小为 0 的分区，结果表里出现 (300, 0) 这种幽灵分区；\n'
            '3. 装不下时出错退出——题面要求跳过并继续；\n'
            '4. 直接在传入列表上改（题面要求返回新表、不修改入参）。\n\n'
            '复杂度：首次适应 O(请求数 × 分区数)，最佳适应同样是 O(请求数 × 分区数)'
            '（只是内层必须扫完整个表）。'
        ),
        'expected_output': '[(240, 60), (400, 50), (600, 30)]\n[(200, 100), (440, 10), (600, 30)]\n[(100, 200), (400, 50), (600, 30)]\n[(100, 60), (270, 30)]',
        'hints': [
            '从分区的低地址端切：起始地址 + 请求大小、大小 − 请求大小',
            '最佳适应要扫完整个空闲表，选「够用的里面最小的」；装不下就跳过这个请求',
        ],
    },
    {
        'id': 'os-304',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': '有效访问时间 EAT（含缺页率）',
        'difficulty': 1,
        'tags': ['EAT', '缺页率', '有效访问时间'],
        'statement': (
            '在带有虚拟内存的页式系统中，一次访存可能是「正常访问」，'
            '也可能是「缺页 → 先把缺页处理掉 → 再重新访存」。\n\n'
            '定义两个函数：\n\n'
            '1. `eat(page_fault_rate, mem_access_time, fault_time)`：返回**有效访问时间** EAT，'
            '公式为 `EAT = (1 − p) × t_mem + p × t_fault`，'
            '其中 `page_fault_rate` 是缺页率 p（0 ~ 1 的小数）、'
            '`mem_access_time` 是一次正常访存的时间（纳秒）、'
            '`fault_time` 是**一次缺页处理的总时间**（含缺页中断开销、磁盘读入、更新页表、重新执行指令，纳秒）。\n'
            '2. `max_fault_rate(target_eat, mem_access_time, fault_time)`：'
            '反解出「想让 EAT 不超过 `target_eat`，缺页率最大是多少」，'
            '即 `p = (target_eat − t_mem) / (t_fault − t_mem)`；\n'
            '   - 若 `target_eat ≤ t_mem`，返回 `0.0`（不可能比不访存还快，只能要求「绝不缺页」）；\n'
            '   - 若 `target_eat ≥ t_fault`，返回 `1.0`（允许一直缺页）。\n\n'
            '返回的都是**浮点数**（不用刻意取整，本题按数值比较，允许浮点误差）。\n\n'
            '参考计算：`mem_access_time = 100`、`fault_time = 10100`、`p = 0.001` 时，'
            '`EAT = 0.999 × 100 + 0.001 × 10100 = 99.9 + 10.1 = 110` 纳秒；'
            '若要求 EAT ≤ 300 纳秒，则最大缺页率 = (300 − 100) / (10100 − 100) = 0.02。\n\n'
            '最后打印上面两个参考计算的结果，以及 p = 0 和 p = 1 两个极端情况。'
        ),
        'starter_code': (
            'def eat(page_fault_rate, mem_access_time, fault_time):\n'
            '    # (1 - p) * 正常访存 + p * 缺页处理\n'
            '    pass\n\n'
            'def max_fault_rate(target_eat, mem_access_time, fault_time):\n'
            '    # 反解缺页率，并把结果限制在 [0, 1]\n'
            '    pass\n'
        ),
        'solution': (
            "def eat(page_fault_rate, mem_access_time, fault_time):\n"
            "    return (1 - page_fault_rate) * mem_access_time + page_fault_rate * fault_time\n"
            "\n"
            "def max_fault_rate(target_eat, mem_access_time, fault_time):\n"
            "    if target_eat <= mem_access_time:\n"
            "        return 0.0\n"
            "    if target_eat >= fault_time:\n"
            "        return 1.0\n"
            "    return (target_eat - mem_access_time) / (fault_time - mem_access_time)\n"
            "\n"
            "print(eat(0.001, 100, 10100))\n"
            "print(max_fault_rate(300, 100, 10100))\n"
            "print(eat(0, 100, 10100))\n"
            "print(eat(1, 100, 10100))\n"
        ),
        'checks': [
            "assert abs(eat(0.001, 100, 10100) - 110) < 1e-6, 'p = 0.001、访存 100 ns、缺页处理 10100 ns 时 EAT = 0.999 × 100 + 0.001 × 10100 = 110 ns，实际 %r' % (eat(0.001, 100, 10100),)",
            "assert abs(eat(0, 100, 10100) - 100) < 1e-6, 'p = 0（从不缺页）时 EAT 就是一次正常访存时间 100 ns，实际 %r' % (eat(0, 100, 10100),)",
            "assert abs(eat(1, 100, 10100) - 10100) < 1e-6, 'p = 1（每次都缺页）时 EAT 就是缺页处理时间 10100 ns，实际 %r' % (eat(1, 100, 10100),)",
            "assert abs(eat(0.02, 100, 10100) - 300) < 1e-6, 'p = 0.02 时 EAT = 0.98 × 100 + 0.02 × 10100 = 300 ns，实际 %r' % (eat(0.02, 100, 10100),)",
            "assert abs(eat(0.5, 200, 200) - 200) < 1e-6, '缺页处理时间与正常访存相同时（都 200 ns）EAT 恒为 200 ns，实际 %r' % (eat(0.5, 200, 200),)",
            "assert abs(max_fault_rate(300, 100, 10100) - 0.02) < 1e-9, '要求 EAT ≤ 300 ns 时缺页率不得超过 (300 − 100) / (10100 − 100) = 0.02，实际 %r' % (max_fault_rate(300, 100, 10100),)",
            "assert abs(max_fault_rate(110, 100, 10100) - 0.001) < 1e-9, '要求 EAT ≤ 110 ns 时最大缺页率是 0.001，实际 %r' % (max_fault_rate(110, 100, 10100),)",
            "assert max_fault_rate(100, 100, 10100) == 0.0, '目标 EAT 等于正常访存时间（100 ns）时只能是「绝不缺页」，返回 0.0，实际 %r' % (max_fault_rate(100, 100, 10100),)",
            "assert max_fault_rate(50, 100, 10100) == 0.0, '目标 EAT 小于正常访存时间时无法达到，按题面约定返回 0.0，实际 %r' % (max_fault_rate(50, 100, 10100),)",
            "assert max_fault_rate(10100, 100, 10100) == 1.0, '目标 EAT 等于缺页处理时间时允许一直缺页，返回 1.0，实际 %r' % (max_fault_rate(10100, 100, 10100),)",
            "assert max_fault_rate(999999, 100, 10100) == 1.0, '目标 EAT 远大于缺页处理时间时缺页率上限仍是 1.0（不能超过 1），实际 %r' % (max_fault_rate(999999, 100, 10100),)",
            "assert abs(max_fault_rate(5000, 100, 10100) - 0.49) < 1e-9, '目标 EAT = 5000 ns 时最大缺页率 = 4900 / 10000 = 0.49，实际 %r' % (max_fault_rate(5000, 100, 10100),)",
            "_small = eat(1e-9, 100, 10100)\nassert 100 <= _small < 100.001, '缺页率极小时 EAT 应非常接近正常访存时间 100 ns，实际 %r' % (_small,)",
        ],
        'explanation': (
            '有效访问时间（Effective Access Time, EAT）是虚拟内存的核心指标：'
            '**把「小概率、超高代价」的缺页事件摊到每次访问上**。\n\n'
            '```\n'
            'EAT = (1 − p) × t_mem + p × t_fault\n'
            '```\n\n'
            '缺页处理时间 `t_fault` 通常是访存时间的几万倍（毫秒 vs 纳秒），'
            '所以即使 p 只有 0.001，它贡献的项也远大于正常访存那一项：'
            '110 ns 里有 10.1 ns 是缺页开销，占了近 10%。'
            '这就是为什么操作系统要拼命提高命中率——**缺页率必须压到万分之一量级才不拖慢系统**。\n\n'
            '反解公式来自一次方程：`target = (1 − p) t_mem + p t_fault = t_mem + p (t_fault − t_mem)`，'
            '于是 `p = (target − t_mem) / (t_fault − t_mem)`。'
            '分母 `t_fault − t_mem` 恒为正（缺页一定更慢），直接除就行。\n\n'
            '**常见错误**：\n\n'
            '1. 反解时分子分母颠倒（分母必须是「缺页处理时间 − 正常访存时间」）；\n'
            '2. 忘记 `(1 − p)`，写成 `p × t_mem + p × t_fault`；\n'
            '3. 忘记把结果限制在 [0, 1]，算出负的缺页率（物理上没意义）；\n'
            '4. 单位不统一：缺页处理常给毫秒，访存给纳秒，要先统一到同一单位再代入。\n\n'
            '复杂度：时间 O(1)、额外空间 O(1)。'
        ),
        'expected_output': '110.0\n0.02\n100\n10100',
        'hints': [
            'EAT = (1 − p) × 正常访存 + p × 缺页处理时间',
            '反解 p = (目标 EAT − 正常访存) / (缺页处理 − 正常访存)，再夹在 0 和 1 之间',
        ],
    },
    {
        'id': 'os-305',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': 'TLB 命中率与有效访问时间',
        'difficulty': 2,
        'tags': ['TLB', '快表', '命中率', 'EAT'],
        'statement': (
            '引入**快表 TLB** 后，一次访存的流程是：先查 TLB（耗时 `tlb_time`），'
            '命中则直接得到物理块号，再访存取数据（一次 `mem_time`）；'
            '未命中则还要再访问一次内存去查页表，然后才取数据。\n\n'
            '定义两个函数：\n\n'
            '1. `tlb_eat(hit_rate, tlb_time, mem_time)`：返回平均有效访问时间，\n'
            '   公式 `EAT = tlb_time + mem_time + (1 − hit_rate) × mem_time`\n'
            '   （前两项是「查 TLB + 取数据」，未命中时额外多一次访存去读页表）。\n'
            '2. `tlb_needed_rate(target_eat, tlb_time, mem_time)`：反解「要把 EAT 压到 '
            '`target_eat` 以内，TLB 命中率至少要多少」，'
            '   即 `h = 1 − (target_eat − tlb_time − mem_time) / mem_time`；\n'
            '   - 若 `target_eat ≤ tlb_time + mem_time`，返回 `1.0`（只能要求「次次命中」）；\n'
            '   - 若 `target_eat ≥ tlb_time + 2 × mem_time`，返回 `0.0`（命中率取 0 也够）。\n\n'
            '返回的都是浮点数（按数值比较，允许浮点误差）。\n\n'
            '参考计算：`tlb_time = 20`、`mem_time = 100`、命中率 0.9 时，'
            '`EAT = 20 + 100 + 0.1 × 100 = 130` 纳秒；'
            '若要求 EAT ≤ 125 ns，则命中率至少 `1 − (125 − 120) / 100 = 0.95`。\n\n'
            '最后打印命中率 0.9 的 EAT、要求 125 ns 时的最低命中率、'
            '以及命中率 1.0 和 0.0 两个极端情况下的 EAT。'
        ),
        'starter_code': (
            'def tlb_eat(hit_rate, tlb_time, mem_time):\n'
            '    # 查 TLB + 取数据 + 未命中时多查一次页表\n'
            '    pass\n\n'
            'def tlb_needed_rate(target_eat, tlb_time, mem_time):\n'
            '    # 反解命中率，并限制在 [0, 1]\n'
            '    pass\n'
        ),
        'solution': (
            "def tlb_eat(hit_rate, tlb_time, mem_time):\n"
            "    return tlb_time + mem_time + (1 - hit_rate) * mem_time\n"
            "\n"
            "def tlb_needed_rate(target_eat, tlb_time, mem_time):\n"
            "    if target_eat <= tlb_time + mem_time:\n"
            "        return 1.0\n"
            "    if target_eat >= tlb_time + 2 * mem_time:\n"
            "        return 0.0\n"
            "    return 1 - (target_eat - tlb_time - mem_time) / mem_time\n"
            "\n"
            "print(tlb_eat(0.9, 20, 100))\n"
            "print(tlb_needed_rate(125, 20, 100))\n"
            "print(tlb_eat(1.0, 20, 100))\n"
            "print(tlb_eat(0.0, 20, 100))\n"
        ),
        'checks': [
            "assert abs(tlb_eat(0.9, 20, 100) - 130) < 1e-6, '命中率 0.9、查 TLB 20 ns、访存 100 ns 时 EAT = 20 + 100 + 0.1 × 100 = 130 ns，实际 %r' % (tlb_eat(0.9, 20, 100),)",
            "assert abs(tlb_eat(1.0, 20, 100) - 120) < 1e-6, '命中率 100% 时 EAT = 20 + 100 = 120 ns（不再多查页表），实际 %r' % (tlb_eat(1.0, 20, 100),)",
            "assert abs(tlb_eat(0.0, 20, 100) - 220) < 1e-6, '命中率 0 时每次都要多查一次页表，EAT = 20 + 100 + 100 = 220 ns，实际 %r' % (tlb_eat(0.0, 20, 100),)",
            "assert abs(tlb_eat(0.8, 10, 50) - 70) < 1e-6, '换成查 TLB 10 ns、访存 50 ns、命中率 0.8：EAT = 10 + 50 + 0.2 × 50 = 70 ns，实际 %r' % (tlb_eat(0.8, 10, 50),)",
            "assert abs(tlb_eat(0.5, 0, 100) - 150) < 1e-6, 'TLB 查找时间为 0（理想快表）时 EAT = 100 + 0.5 × 100 = 150 ns，实际 %r' % (tlb_eat(0.5, 0, 100),)",
            "assert abs(tlb_needed_rate(130, 20, 100) - 0.9) < 1e-9, '要求 EAT ≤ 130 ns 时命中率至少 1 − (130 − 120) / 100 = 0.9，实际 %r' % (tlb_needed_rate(130, 20, 100),)",
            "assert abs(tlb_needed_rate(125, 20, 100) - 0.95) < 1e-9, '要求 EAT ≤ 125 ns 时命中率至少 0.95，实际 %r' % (tlb_needed_rate(125, 20, 100),)",
            "assert abs(tlb_needed_rate(170, 20, 100) - 0.5) < 1e-9, '要求 EAT ≤ 170 ns 时命中率至少 0.5，实际 %r' % (tlb_needed_rate(170, 20, 100),)",
            "assert tlb_needed_rate(120, 20, 100) == 1.0, '目标 EAT 等于「查 TLB + 访存」（120 ns）时只能要求命中率 100%，返回 1.0，实际 %r' % (tlb_needed_rate(120, 20, 100),)",
            "assert tlb_needed_rate(100, 20, 100) == 1.0, '目标 EAT 小于 120 ns 时不可能达到，按题面约定返回 1.0，实际 %r' % (tlb_needed_rate(100, 20, 100),)",
            "assert tlb_needed_rate(220, 20, 100) == 0.0, '目标 EAT 等于「命中率为 0」时的 220 ns，命中率下限是 0.0，实际 %r' % (tlb_needed_rate(220, 20, 100),)",
            "assert tlb_needed_rate(9999, 20, 100) == 0.0, '目标 EAT 很大时命中率下限仍是 0.0（不能小于 0），实际 %r' % (tlb_needed_rate(9999, 20, 100),)",
            "_h = tlb_needed_rate(130, 20, 100)\nassert abs(tlb_eat(_h, 20, 100) - 130) < 1e-6, '反解出来的命中率代回 EAT 公式应当正好得到 130 ns，实际 %r' % (tlb_eat(_h, 20, 100),)",
        ],
        'explanation': (
            'TLB（快表）是一小块硬件缓存，存的是最近用过的「页号 → 物理块号」。'
            '它的存在把「访存前必须查页表」这件事变成了「大多数时候不用查」。\n\n'
            '```\n'
            '命中：查 TLB（t_tlb） + 访存取数据（t_mem）\n'
            '未命中：查 TLB + 访存查页表 + 访存取数据 = t_tlb + 2 × t_mem\n'
            'EAT = h (t_tlb + t_mem) + (1 − h) (t_tlb + 2 t_mem)\n'
            '    = t_tlb + t_mem + (1 − h) t_mem        ← 化简后的常用形式\n'
            '```\n\n'
            '注意这里默认**先查 TLB、再访存**是串行的；'
            '有的教材把 TLB 与访存写成并行（先按逻辑地址查页表、同时查 TLB），'
            '公式会变成 `EAT = h t_tlb + (1 − h)(t_tlb + t_mem) + t_mem` 的不同形式，'
            '做真题时一定要看清题面给的口径（本题按上面第一组公式）。\n\n'
            '反解就是解一次方程：`EAT = t_tlb + t_mem + (1 − h) t_mem`，'
            '把 `(1 − h)` 当未知数即可；两个夹逼边界对应「命中率为 1」和「命中率为 0」的极端。\n\n'
            '**常见错误**：\n\n'
            '1. 未命中时把「查页表」和「取数据」都算上，却忘了再乘一次 `t_tlb`（查 TLB 无论命中与否都要做）；\n'
            '2. 把命中率写反：`h` 是命中率，漏掉的是 `(1 − h)`；\n'
            '3. 反解时忘记除以 `mem_time`，直接写成 `1 − (target − tlb − mem)`；\n'
            '4. 反解结果不夹逼，算出 1.2 或 −0.3 这种「物理上不可能」的命中率。\n\n'
            '复杂度：时间 O(1)、额外空间 O(1)。'
        ),
        'expected_output': '130.0\n0.95\n120.0\n220.0',
        'hints': [
            'EAT = 查 TLB 时间 + 访存时间 + (1 − 命中率) × 再一次访存',
            '反解命中率 = 1 − (目标 EAT − TLB − 访存) / 访存，结果夹在 0 和 1 之间',
        ],
    },
    {
        'id': 'os-306',
        'track': 'algorithm',
        'chapter_id': 141,
        'chapter_title': '操作系统·内存管理与地址转换',
        'topic': '操作系统·内存管理与地址转换',
        'title': 'TLB 与缺页中断的联合有效访问时间',
        'difficulty': 2,
        'tags': ['TLB', '缺页率', 'EAT', '综合计算'],
        'statement': (
            '把快表和缺页放在一起：先查 TLB（`tlb_time`），未命中再访存查页表；'
            '**只有在查页表时发现该页不在内存，才会发生缺页**（概率为 `fault_rate`），'
            '此时整条指令要重来，代价是 `fault_time`。\n\n'
            '定义两个函数：\n\n'
            '1. `eat_full(hit_rate, tlb_time, mem_time, fault_rate, fault_time)`，返回\n\n'
            '   ```\n'
            '   normal = tlb_time + mem_time + (1 − hit_rate) × mem_time\n'
            '   EAT = (1 − fault_rate) × normal + fault_rate × fault_time\n'
            '   ```\n\n'
            '2. `fault_rate_needed(target_eat, hit_rate, tlb_time, mem_time, fault_time)`：'
            '反解 `p = (target_eat − normal) / (fault_time − normal)`，并按惯例夹在 [0, 1]：'
            '目标 ≤ normal 返回 `0.0`，目标 ≥ `fault_time` 返回 `1.0`。\n\n'
            '返回浮点数（按数值比较，允许浮点误差）。\n\n'
            '参考计算：`hit_rate = 0.9`、`tlb_time = 20`、`mem_time = 100`，'
            '则 `normal = 130`；再取 `fault_rate = 0.001`、`fault_time = 10000000`（10 ms，单位纳秒），'
            '`EAT = 0.999 × 130 + 0.001 × 10000000 = 129.87 + 10000 = 10129.87` ns。\n\n'
            '最后打印上面参考计算的 EAT，以及「要求 EAT ≤ 150 ns、缺页处理 10130 ns」时'
            '允许的最大缺页率。'
        ),
        'starter_code': (
            'def eat_full(hit_rate, tlb_time, mem_time, fault_rate, fault_time):\n'
            '    normal = 0\n'
            '    # 先算不缺页时的 EAT，再按缺页率加权\n'
            '    pass\n\n'
            'def fault_rate_needed(target_eat, hit_rate, tlb_time, mem_time, fault_time):\n'
            '    # 反解缺页率，夹在 [0, 1]\n'
            '    pass\n'
        ),
        'solution': (
            "def eat_full(hit_rate, tlb_time, mem_time, fault_rate, fault_time):\n"
            "    normal = tlb_time + mem_time + (1 - hit_rate) * mem_time\n"
            "    return (1 - fault_rate) * normal + fault_rate * fault_time\n"
            "\n"
            "def fault_rate_needed(target_eat, hit_rate, tlb_time, mem_time, fault_time):\n"
            "    normal = tlb_time + mem_time + (1 - hit_rate) * mem_time\n"
            "    if target_eat <= normal:\n"
            "        return 0.0\n"
            "    if target_eat >= fault_time:\n"
            "        return 1.0\n"
            "    return (target_eat - normal) / (fault_time - normal)\n"
            "\n"
            "print(eat_full(0.9, 20, 100, 0.001, 10000000))\n"
            "print(fault_rate_needed(150, 0.9, 20, 100, 10130))\n"
        ),
        'checks': [
            "assert abs(eat_full(0.9, 20, 100, 0.001, 10000000) - 10129.87) < 1e-6, 'normal = 130，EAT = 0.999 × 130 + 0.001 × 10000000 = 10129.87 ns，实际 %r' % (eat_full(0.9, 20, 100, 0.001, 10000000),)",
            "assert abs(eat_full(0.9, 20, 100, 0, 10000000) - 130) < 1e-6, '缺页率为 0 时 EAT 就是 TLB 口径下的 130 ns，实际 %r' % (eat_full(0.9, 20, 100, 0, 10000000),)",
            "assert abs(eat_full(0.9, 20, 100, 1, 10000000) - 10000000) < 1e-6, '缺页率为 1 时 EAT 就是缺页处理时间 10000000 ns，实际 %r' % (eat_full(0.9, 20, 100, 1, 10000000),)",
            "assert abs(eat_full(1.0, 20, 100, 0.001, 10000000) - (0.999 * 120 + 0.001 * 10000000)) < 1e-6, 'TLB 全命中时 normal = 120，EAT = 0.999 × 120 + 0.001 × 10000000 = 10119.88 ns，实际 %r' % (eat_full(1.0, 20, 100, 0.001, 10000000),)",
            "assert abs(eat_full(0.0, 20, 100, 0, 10000000) - 220) < 1e-6, '命中率 0、缺页率 0 时 EAT = 20 + 100 + 100 = 220 ns，实际 %r' % (eat_full(0.0, 20, 100, 0, 10000000),)",
            "assert abs(fault_rate_needed(150, 0.9, 20, 100, 10130) - 0.002) < 1e-9, 'normal = 130、缺页处理 10130 ns 时，EAT ≤ 150 对应 p = (150 − 130) / (10130 − 130) = 0.002，实际 %r' % (fault_rate_needed(150, 0.9, 20, 100, 10130),)",
            "assert fault_rate_needed(130, 0.9, 20, 100, 10130) == 0.0, '目标正好等于 normal（130 ns）时只能是「绝不缺页」，返回 0.0，实际 %r' % (fault_rate_needed(130, 0.9, 20, 100, 10130),)",
            "assert fault_rate_needed(100, 0.9, 20, 100, 10130) == 0.0, '目标小于 normal 时无法达到，按题面约定返回 0.0，实际 %r' % (fault_rate_needed(100, 0.9, 20, 100, 10130),)",
            "assert fault_rate_needed(10130, 0.9, 20, 100, 10130) == 1.0, '目标等于缺页处理时间时允许一直缺页，返回 1.0，实际 %r' % (fault_rate_needed(10130, 0.9, 20, 100, 10130),)",
            "assert fault_rate_needed(99999, 0.9, 20, 100, 10130) == 1.0, '目标远大于缺页处理时间时上限仍是 1.0，实际 %r' % (fault_rate_needed(99999, 0.9, 20, 100, 10130),)",
            "_p = fault_rate_needed(150, 0.9, 20, 100, 10130)\nassert abs(eat_full(0.9, 20, 100, _p, 10130) - 150) < 1e-6, '反解出的缺页率代回 EAT 公式应正好得到 150 ns，实际 %r' % (eat_full(0.9, 20, 100, _p, 10130),)",
            "_big = eat_full(0.9, 20, 100, 0.01, 10000000)\nassert _big > 100000, '缺页率升到 0.01 时 EAT 应该是十万纳秒量级（0.99 × 130 + 0.01 × 10000000 ≈ 100128.7），实际 %r' % (_big,)",
        ],
        'explanation': (
            '这题是「两件坏事叠在一起」的加权：先算**不缺页时的 EAT**（TLB 口径），'
            '再按缺页率把它和缺页处理时间加权平均。\n\n'
            '```\n'
            'normal = t_tlb + t_mem + (1 − h) t_mem      # 不缺页时的每次访存时间\n'
            'EAT    = (1 − p) × normal + p × t_fault\n'
            '```\n\n'
            '代入数字能直观感受到「缺页的破坏力」：'
            'normal 是 130 ns，但只要缺页率 0.001、缺页处理 10 ms，'
            'EAT 就涨到 10129.87 ns——**放大了将近 78 倍**。'
            '也就是说，虚拟内存的性能瓶颈几乎完全由缺页率决定，'
            'TLB 优化只能影响那 130 ns 里的零头（真正被摊薄的是它）。\n\n'
            '反解时先把 `normal` 算出来再解一次方程即可：'
            '`target = normal + p (t_fault − normal)`。'
            '两个边界对应「连 normal 都达不到」（只能 0 缺页）和「目标比缺页处理还宽松」（随便缺页）。\n\n'
            '**常见错误**：\n\n'
            '1. 把缺页率和 TLB 命中率混在一起相乘（两者作用在不同环节，不能直接相乘）；\n'
            '2. 忘记 `normal` 里还有 `(1 − h) × t_mem` 这一项；\n'
            '3. 单位不统一：`fault_time` 给的是纳秒还是毫秒要看清（本题统一用纳秒）；\n'
            '4. 反解时用错分母（分母是 `fault_time − normal`，不是 `fault_time − t_mem`）。\n\n'
            '复杂度：时间 O(1)、额外空间 O(1)。'
        ),
        'expected_output': '10129.87\n0.002',
        'hints': [
            '先算「不缺页时」的 EAT（TLB 口径），再按缺页率加权',
            '反解分母是「缺页处理时间 − 不缺页时的 EAT」',
        ],
    },
    {
        'id': 'os-307',
        'track': 'algorithm',
        'chapter_id': 142,
        'chapter_title': '操作系统·页面置换与缺页',
        'topic': '操作系统·页面置换与缺页',
        'title': 'FIFO 页面置换与 Belady 异常',
        'difficulty': 2,
        'tags': ['页面置换', 'FIFO', 'Belady 异常', '缺页次数'],
        'statement': (
            '**FIFO 页面置换算法**：内存里的页框排成一个队列，'
            '发生缺页且没有空闲页框时，淘汰**最先进入内存**的那一页（先进先出）；'
            '命中时**不改变**任何页的进入次序（FIFO 只看「谁来得早」，不看谁最近用过）。\n\n'
            '定义两个函数：\n\n'
            '1. `fifo_faults(pages, frame_count)`：返回把页面引用串 `pages` 走一遍'
            '所产生的**缺页次数**。\n'
            '   - `pages` 是页号组成的列表，可能为空；`frame_count` 是可用的页框数（≥ 1）；\n'
            '   - 页框一开始全是空的，第一次访问某个页一定缺页（装入空框）；\n'
            '   - 同一个页在内存里再次被访问算**命中**，不计缺页。\n'
            '2. `belady_demo(pages)`：返回二元组 `(帧数 3 时的缺页次数, 帧数 4 时的缺页次数)`，'
            '用来演示 **Belady 异常**——对某些引用串，FIFO 在页框更多时缺页反而更多。\n\n'
            '参考数据（本题主要用它）：引用串 `[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]`，'
            '3 个页框时缺页 9 次，4 个页框时缺页 10 次——帧多了反而多缺一次页。\n\n'
            '最后打印该引用串在 3 帧、4 帧下的缺页次数，以及上面那对数字（演示 Belady 异常）。'
        ),
        'starter_code': (
            'def fifo_faults(pages, frame_count):\n'
            '    frames = []\n'
            '    faults = 0\n'
            '    # 命中：什么都不做；缺页：满了就 pop(0) 淘汰最早进入的页\n'
            '    pass\n\n'
            'def belady_demo(pages):\n'
            '    # 返回 (fifo_faults(pages, 3), fifo_faults(pages, 4))\n'
            '    pass\n'
        ),
        'solution': (
            "def fifo_faults(pages, frame_count):\n"
            "    frames = []\n"
            "    faults = 0\n"
            "    for page in pages:\n"
            "        if page in frames:\n"
            "            continue\n"
            "        faults += 1\n"
            "        if len(frames) >= frame_count:\n"
            "            frames.pop(0)\n"
            "        frames.append(page)\n"
            "    return faults\n"
            "\n"
            "def belady_demo(pages):\n"
            "    return fifo_faults(pages, 3), fifo_faults(pages, 4)\n"
            "\n"
            "data = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\n"
            "print(fifo_faults(data, 3))\n"
            "print(fifo_faults(data, 4))\n"
            "print(belady_demo(data))\n"
        ),
        'checks': [
            "_data = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert fifo_faults(_data, 3) == 9, '经典 Belady 引用串在 3 个页框下应缺页 9 次，实际 %r' % (fifo_faults(_data, 3),)",
            "_data = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert fifo_faults(_data, 4) == 10, '同一引用串在 4 个页框下应缺页 10 次（Belady 异常：帧多反而缺页多），实际 %r' % (fifo_faults(_data, 4),)",
            "_data = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert belady_demo(_data) == (9, 10), 'belady_demo 应返回 (3 帧缺页数, 4 帧缺页数) = (9, 10)，实际 %r' % (belady_demo(_data),)",
            "_data = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert fifo_faults(_data, 3) == 15, '教材经典引用串在 3 个页框下应缺页 15 次，实际 %r' % (fifo_faults(_data, 3),)",
            "_data = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert fifo_faults(_data, 4) == 10, '同一引用串在 4 个页框下应缺页 10 次，实际 %r' % (fifo_faults(_data, 4),)",
            "_data = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert belady_demo(_data) == (15, 10), 'belady_demo 对这组数据应返回 (15, 10)，实际 %r' % (belady_demo(_data),)",
            "assert fifo_faults([], 3) == 0, '空引用串一次缺页都没有，应返回 0，实际 %r' % (fifo_faults([], 3),)",
            "assert fifo_faults([5], 1) == 1, '只访问一页时缺页 1 次，实际 %r' % (fifo_faults([5], 1),)",
            "assert fifo_faults([1, 1, 1, 1], 1) == 1, '反复访问同一页只缺页 1 次，实际 %r' % (fifo_faults([1, 1, 1, 1], 1),)",
            "assert fifo_faults([1, 2, 3], 3) == 3, '页框足够时每个不同的页只缺页一次，实际 %r' % (fifo_faults([1, 2, 3], 3),)",
            "assert fifo_faults([1, 2, 3], 5) == 3, '页框比用到的页还多时同样是 3 次，实际 %r' % (fifo_faults([1, 2, 3], 5),)",
            "assert fifo_faults([1, 2, 1, 2, 1], 2) == 2, '两个页轮流访问且都在内存里时只在前两次缺页，实际 %r' % (fifo_faults([1, 2, 1, 2, 1], 2),)",
            "assert fifo_faults([1, 2, 3, 1, 2, 3], 2) == 6, '2 个页框装 3 个循环访问的页时每次都要置换，共缺页 6 次，实际 %r' % (fifo_faults([1, 2, 3, 1, 2, 3], 2),)",
            "assert fifo_faults([1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], 1) == 12, '只有 1 个页框时每次访问（与上一页不同）都缺页，共 12 次，实际 %r' % (fifo_faults([1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], 1),)",
            "_pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\n_copy = list(_pages)\nfifo_faults(_pages, 3)\nassert _pages == _copy, 'fifo_faults 只能读引用串，不能修改它，实际 %r' % (_pages,)",
        ],
        'explanation': (
            'FIFO 的规则最朴素：**谁先进内存，谁先被淘汰**。实现上用一个列表当队列，'
            '命中时什么都不做，缺页满了就 `pop(0)` 再 `append`。\n\n'
            '```python\n'
            'for page in pages:\n'
            '    if page in frames:\n'
            '        continue                    # 命中：FIFO 不改变次序\n'
            '    faults += 1\n'
            '    if len(frames) >= frame_count:\n'
            '        frames.pop(0)               # 淘汰最早进入的页\n'
            '    frames.append(page)\n'
            '```\n\n'
            '**Belady 异常**是 FIFO 最有名的「反常识」：直觉上页框越多、缺页越少，'
            '但 FIFO 不满足这个直觉。原因在于增加页框会**改变淘汰次序**，'
            '使得某些页被更早地踢出去，形成新的缺页——比如本题的 9 → 10。\n'
            '理论上只有「栈算法」（LRU、OPT 属于这一类）才能保证帧数增加时缺页单调不增。\n\n'
            '对照记忆：\n\n'
            '- FIFO：实现最简单，但可能淘汰马上要用的页，**有** Belady 异常；\n'
            '- LRU：按「最近最久未使用」淘汰，**没有** Belady 异常，但需要硬件支持（访问位 / 时间戳）；\n'
            '- OPT：淘汰「将来最久不用」的页，缺页最少，但需要预知未来，现实中做不了，只当理论下界。\n\n'
            '**常见错误**：\n\n'
            '1. 命中时也调整队列次序（那就变成 LRU 了）；\n'
            '2. 缺页时才 `pop(0)` 而忘记 `append`，页框一直空着；\n'
            '3. 忘记「页框一开始是空的」，导致第一次访问也算成「置换」；\n'
            '4. 帧数大于引用串里不同页的个数时还要硬凑 min 逻辑（直接全装下即可）。\n\n'
            '复杂度：时间 O(引用串长度 × 帧数)、额外空间 O(帧数)。'
        ),
        'expected_output': '9\n10\n(9, 10)',
        'hints': [
            '命中时什么都不做；缺页且页框满时 pop(0) 淘汰最早进入的页',
            'Belady 异常 = 帧数多反而缺页多，本题的数据是 9（3 帧）与 10（4 帧）',
        ],
    },
    {
        'id': 'os-308',
        'track': 'algorithm',
        'chapter_id': 142,
        'chapter_title': '操作系统·页面置换与缺页',
        'topic': '操作系统·页面置换与缺页',
        'title': 'LRU 页面置换与缺页序列',
        'difficulty': 2,
        'tags': ['页面置换', 'LRU', '缺页序列', '局部性'],
        'statement': (
            '**LRU（最近最久未使用）页面置换算法**：发生缺页且没有空闲页框时，'
            '淘汰**上一次被访问时间距现在最久**（最久没被用过）的那一页；'
            '每次**命中也要把该页标记为「最近刚用过」**——这是 LRU 与 FIFO 的唯一区别。\n\n'
            '定义两个函数：\n\n'
            '1. `lru_faults(pages, frame_count)`：返回走完引用串 `pages` 的**缺页次数**。\n'
            '2. `lru_fault_list(pages, frame_count)`：返回**每次访问是否缺页**的布尔列表'
            '（长度与 `pages` 相同，`True` 表示这次访问缺页，`False` 表示命中）。\n\n'
            '实现提示：用一个列表 `frames` 保存当前内存中的页，'
            '**约定列表末尾的元素是「最近刚用过」的页**。'
            '命中时把该页移动到列表末尾（先 `remove` 再 `append`）；'
            '缺页时若已满就 `pop(0)` 淘汰表头（最久未使用），再把新页 `append` 到末尾。\n\n'
            '参考数据：引用串 `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]`'
            '在 3 个页框下缺页 12 次；'
            '`[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]` 在 3 帧下缺页 10 次、4 帧下缺页 8 次'
            '（帧多反而**少**缺页，说明 LRU 没有 Belady 异常）。\n\n'
            '最后打印 20 次引用的经典串在 3 帧下的缺页次数，以及 12 次引用的串在 3 帧、4 帧下的缺页次数。'
        ),
        'starter_code': (
            'def lru_faults(pages, frame_count):\n'
            '    # 提示：可以调用下面这个函数，返回缺页列表里 True 的个数\n'
            '    pass\n\n'
            'def lru_fault_list(pages, frame_count):\n'
            '    frames = []\n'
            '    result = []\n'
            '    # 命中：把该页移到表尾；缺页：满了先 pop(0) 淘汰表头\n'
            '    pass\n'
        ),
        'solution': (
            "def lru_fault_list(pages, frame_count):\n"
            "    frames = []\n"
            "    result = []\n"
            "    for page in pages:\n"
            "        if page in frames:\n"
            "            frames.remove(page)\n"
            "            frames.append(page)\n"
            "            result.append(False)\n"
            "            continue\n"
            "        result.append(True)\n"
            "        if len(frames) >= frame_count:\n"
            "            frames.pop(0)\n"
            "        frames.append(page)\n"
            "    return result\n"
            "\n"
            "def lru_faults(pages, frame_count):\n"
            "    return sum(1 for fault in lru_fault_list(pages, frame_count) if fault)\n"
            "\n"
            "data20 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\n"
            "print(lru_faults(data20, 3))\n"
            "data12 = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\n"
            "print(lru_faults(data12, 3))\n"
            "print(lru_faults(data12, 4))\n"
        ),
        'checks': [
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert lru_faults(_d, 3) == 12, '教材经典引用串在 3 个页框下 LRU 应缺页 12 次，实际 %r' % (lru_faults(_d, 3),)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert lru_faults(_d, 3) == 10, 'Belady 引用串在 3 个页框下 LRU 应缺页 10 次，实际 %r' % (lru_faults(_d, 3),)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert lru_faults(_d, 4) == 8, '同一引用串在 4 个页框下 LRU 应缺页 8 次（帧多则缺页少，LRU 无 Belady 异常），实际 %r' % (lru_faults(_d, 4),)",
            "_d = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]\nassert lru_fault_list(_d, 3) == [True, True, True, True, True, True, True, False, False, True, True, True], '该串前 7 次都缺页，第 8、9 次（1、2）命中，最后 3 次又缺页，实际 %r' % (lru_fault_list(_d, 3),)",
            "assert lru_fault_list([1, 2, 1, 2, 1], 2) == [True, True, False, False, False], '两页轮流访问：只有最开始两次缺页，后面全命中，实际 %r' % (lru_fault_list([1, 2, 1, 2, 1], 2),)",
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\nassert not lru_fault_list(_d, 3)[4], '第 5 次访问页 0（此时内存里应该有 0）应命中（缺页标志为假），实际 %r' % (lru_fault_list(_d, 3)[4],)",
            "assert lru_fault_list([], 3) == [], '空引用串的缺页序列也应该是空的，实际 %r' % (lru_fault_list([], 3),)",
            "assert lru_faults([], 3) == 0, '空引用串缺页 0 次，实际 %r' % (lru_faults([], 3),)",
            "assert lru_faults([4, 4, 4, 4], 2) == 1, '反复访问同一页只缺页 1 次，实际 %r' % (lru_faults([4, 4, 4, 4], 2),)",
            "assert lru_faults([1, 2, 3], 3) == 3, '页框够装时每个不同的页只缺页一次，实际 %r' % (lru_faults([1, 2, 3], 3),)",
            "assert lru_faults([1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], 1) == 12, '只有 1 个页框时 12 次访问全部缺页（相邻页都不同），实际 %r' % (lru_faults([1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], 1),)",
            "assert lru_faults([1, 2, 3, 1, 2, 3], 2) == 6, '2 个页框装 3 页循环访问时每次都缺页，共 6 次，实际 %r' % (lru_faults([1, 2, 3, 1, 2, 3], 2),)",
            "assert lru_faults([3, 1, 3, 1, 3, 1], 2) == 2, '交替访问两个页时 LRU 只在前两次缺页，实际 %r' % (lru_faults([3, 1, 3, 1, 3, 1], 2),)",
            "_d = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]\n_faults = lru_faults(_d, 3)\nassert _faults == sum(1 for _f in lru_fault_list(_d, 3) if _f), 'lru_faults 的结果应等于 lru_fault_list 里 True 的个数，实际 %r' % (_faults,)",
            "_pages = [1, 2, 3, 1]\n_copy = list(_pages)\nlru_faults(_pages, 2)\nlru_fault_list(_pages, 2)\nassert _pages == _copy, '两个函数都只能读引用串，不能修改它，实际 %r' % (_pages,)",
        ],
        'explanation': (
            'LRU 的出发点是**程序的局部性原理**：刚用过的页很可能马上还要用，'
            '而很久没用的页接下来大概也不会用。所以「淘汰最久未使用的页」是合理的猜测。\n\n'
            '```python\n'
            'if page in frames:\n'
            '    frames.remove(page)      # 命中也要更新「最近使用」位置\n'
            '    frames.append(page)\n'
            'else:\n'
            '    if len(frames) >= frame_count:\n'
            '        frames.pop(0)        # 表头 = 最久未使用\n'
            '    frames.append(page)\n'
            '```\n\n'
            '把「列表末尾 = 最近使用」这个约定固定下来，代码就只剩两步：'
            '命中移到末尾、缺页淘汰表头。\n\n'
            '**LRU 与 FIFO 的唯一区别**就在命中那一支：'
            'FIFO 命中时什么都不做，LRU 命中时要把该页「摸热」。'
            '本题两处的参考数据正好形成对照：同一个 Belady 引用串，'
            'FIFO 是 9（3 帧）→ 10（4 帧）（帧多反而更差），'
            'LRU 是 10（3 帧）→ 8（4 帧）（帧多一定不差）。\n\n'
            '**LRU 为什么没有 Belady 异常？** 因为 LRU 属于「栈算法」：'
            '任何时刻，n 个页框里的页集合一定是 n+1 个页框里页集合的子集，'
            '所以增加页框不可能把「本来命中的访问」变成缺页。FIFO 不具备这个性质。\n\n'
            '**常见错误**：\n\n'
            '1. 命中时不更新次序（那 LRU 就退化成 FIFO 了）；\n'
            '2. 把「最久未使用」记反了——被淘汰的是最久**没**用的，不是最近才用的；\n'
            '3. `lru_fault_list` 与 `lru_faults` 两套逻辑各写一遍、结果对不上；\n'
            '4. 忘记「页框一开始是空的」，第一次访问当成命中。\n\n'
            '复杂度：时间 O(引用串长度 × 帧数)、额外空间 O(帧数)。'
        ),
        'expected_output': '12\n10\n8',
        'hints': [
            '约定列表末尾是「最近使用」：命中先 remove 再 append',
            '缺页且页框满时淘汰表头（最久未使用），新页放到末尾',
        ],
    },
    # ==== 追加位置 ====
]
