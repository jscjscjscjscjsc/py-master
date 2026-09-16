"""题库 · 算法篇（算法与数据结构专题，专题 101–116）。

写法约定与 qbank_basic.py 保持一致：
- statement 面向学生，必须写清「要定义什么名字的函数 / 类」以及输入输出格式。
- checks 只断言题面要求的东西，每条断言都带中文提示，覆盖空输入、单元素、重复元素等边界。
- 参考答案本身必须能通过同一套断言：`python tools/verify_qbank.py --module algo` 会全量验证。
"""

QUESTIONS = [
    # ── 专题 101 复杂度与基础 ──────────────────────────────
    {
        'id': 'alg-001',
        'track': 'algorithm',
        'chapter_id': 101,
        'chapter_title': '复杂度与基础',
        'topic': '复杂度与基础',
        'title': '一趟遍历找出最大值的下标',
        'difficulty': 1,
        'tags': ['遍历', 'O(n)', '边界处理'],
        'statement': (
            '定义函数 `argmax(nums)`，返回列表中**最大值所在的下标**。规则：\n\n'
            '- 如果有多个相同的最大值，返回**最靠前**的那个下标\n'
            '- 如果列表为空，返回 `-1`\n\n'
            '要求只走**一趟循环**（一边遍历一边更新「目前最大值」和「它的下标」），'
            '不要写 `nums.index(max(nums))` 这种走两趟的写法。\n\n'
            '然后调用 `argmax([3, 7, 2, 7, 5])`、`argmax([])`、`argmax([-5, -1, -9])` 并各打印一行结果。'
        ),
        'starter_code': 'def argmax(nums):\n    # 一趟循环：同时维护最大值和它的下标\n    pass\n',
        'solution': (
            "def argmax(nums):\n"
            "    if not nums:\n"
            "        return -1\n"
            "    best = 0\n"
            "    for i in range(1, len(nums)):\n"
            "        if nums[i] > nums[best]:\n"
            "            best = i\n"
            "    return best\n"
            "\n"
            "print(argmax([3, 7, 2, 7, 5]))\n"
            "print(argmax([]))\n"
            "print(argmax([-5, -1, -9]))\n"
        ),
        'checks': [
            "assert argmax([3, 7, 2, 7, 5]) == 1, '有重复最大值时应返回最靠前的下标 1，实际 %r' % (argmax([3, 7, 2, 7, 5]),)",
            "assert argmax([]) == -1, '空列表应返回 -1，实际 %r' % (argmax([]),)",
            "assert argmax([42]) == 0, '只有一个元素应返回 0，实际 %r' % (argmax([42]),)",
            "assert argmax([-5, -1, -9]) == 1, '全是负数时最大值 -1 在下标 1，实际 %r' % (argmax([-5, -1, -9]),)",
            "assert argmax([0, 0, 0]) == 0, '元素全部相等时应返回第一个下标 0，实际 %r' % (argmax([0, 0, 0]),)",
            "assert argmax(list(range(1000))) == 999, '递增序列的最大值下标应是 999，实际 %r' % (argmax(list(range(1000))),)",
        ],
        'explanation': (
            '「一趟循环」的价值：`max(nums)` 走一趟找最大值，`nums.index(...)` 再走一趟找位置，'
            '虽然都是 O(n)，但走了两倍的路。更好的做法是**边走边记下标**：\n\n'
            '```python\n'
            'best = 0\n'
            'for i in range(1, len(nums)):\n'
            '    if nums[i] > nums[best]:\n'
            '        best = i\n'
            '```\n\n'
            '关键细节是**严格大于**：写成 `>=` 就会返回最后一个最大值的位置，和题面要求相反。'
            '另外从下标 1 开始比较，可以省掉「第一个元素」的特判。\n\n'
            '空列表要单独拦截，否则 `best = 0` 会在空列表上直接 `IndexError`。'
            '「先处理边界，再写主逻辑」是写算法题的第一课。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': '1\n-1\n1',
        'hints': ['用 best 记住目前最大值的下标，遇到更大的就更新', '注意是 > 不是 >=，否则重复的最大值会返回最后一个'],
    },
    {
        'id': 'alg-002',
        'track': 'algorithm',
        'chapter_id': 101,
        'chapter_title': '复杂度与基础',
        'topic': '复杂度与基础',
        'title': '质数判断：只试到 √n',
        'difficulty': 1,
        'tags': ['数学', 'O(√n)', '提前返回'],
        'statement': (
            '定义函数 `is_prime(n)`：n 是质数返回 `True`，否则返回 `False`。\n\n'
            '规则：小于 2 的数（0、1、负数）都不是质数。\n\n'
            '要求把判断做到 **O(√n)**：试除只需要试到 √n，循环边界写成 `d * d <= n` '
            '或者 `int(n ** 0.5) + 1`；一旦遇到能整除的因子就**立刻返回 False**，'
            '不要傻傻跑完整个循环。\n\n'
            '然后打印 1~30 之间的所有质数（用循环或推导式收集都行）。'
        ),
        'starter_code': 'def is_prime(n):\n    # 先处理 n < 2，再试除到 √n\n    pass\n',
        'solution': (
            "def is_prime(n):\n"
            "    if n < 2:\n"
            "        return False\n"
            "    for d in range(2, int(n ** 0.5) + 1):\n"
            "        if n % d == 0:\n"
            "            return False\n"
            "    return True\n"
            "\n"
            "print([n for n in range(1, 31) if is_prime(n)])\n"
            "print(is_prime(9973), is_prime(9999))\n"
            "print(is_prime(1), is_prime(2))\n"
        ),
        'checks': [
            "assert is_prime(2) and is_prime(3) and is_prime(7) and is_prime(97), '2、3、7、97 都是质数'",
            "assert not is_prime(1) and not is_prime(0) and not is_prime(-7), '1、0 和负数都不是质数'",
            "assert not is_prime(4) and not is_prime(49) and not is_prime(1000), '4、49、1000 都不是质数'",
            "assert is_prime(9973) is True, '9973 是质数（4 位里最大的质数）'",
            "assert not is_prime(9999), '9999 = 3 × 3333，不是质数'",
            "assert is_prime(1000003) is True, '1000003 是质数，用 √n 边界才能跑得快'",
            "assert is_prime(2) is True and is_prime(2) == True, '请返回布尔值 True / False'",
            "import re\nassert 'sqrt' in _src or '0.5' in _src or re.search(r'\\w+\\s*\\*\\s*\\w+\\s*<=', _src) is not None, '请用「试到 √n」的循环边界（比如 d * d <= n 或 int(n ** 0.5) + 1），不要一直试到 n'",
        ],
        'explanation': (
            '为什么试到 √n 就够了？因为如果 n 有一个大于 √n 的因子 a，'
            '那必定有一个小于 √n 的因子 b 与它配对（`n = a × b`），'
            '小的那个早就被我们试到了。所以 `for d in range(2, int(n ** 0.5) + 1)` 不会漏判。\n\n'
            '`+ 1` 不能省：`range` 右端取不到，n = 49 时 √n = 7，'
            '少了 +1 就会漏掉因子 7，把 49 误判成质数。\n\n'
            '「发现因子就立刻 return False」是**提前退出**思维：'
            '判断 1000 时试到 2 就能结束，根本不用往后跑 30 次。\n\n'
            '复杂度：时间 O(√n)、空间 O(1)。判断 10 万以内的数时它快到几乎无感，'
            '而试到 n-1 的写法要慢 300 倍以上。'
        ),
        'expected_output': '[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]\nTrue False\nFalse True',
        'hints': ['n < 2 直接返回 False', '循环边界用 int(n ** 0.5) + 1，注意那个 +1 不能漏'],
    },

    # ── 专题 102 数组与双指针 ──────────────────────────────
    {
        'id': 'alg-003',
        'track': 'algorithm',
        'chapter_id': 102,
        'chapter_title': '数组与双指针',
        'topic': '数组与双指针',
        'title': '两数之和（哈希表版）',
        'difficulty': 1,
        'tags': ['哈希表', '数组', '下标'],
        'statement': (
            '定义函数 `two_sum(nums, target)`：在 `nums` 里找出**两个下标不同**的元素，'
            '使它们的和等于 `target`，返回这两个元素的下标组成的列表。\n\n'
            '规则：\n\n'
            '- 返回的两个下标顺序**不限**（`[0, 1]` 和 `[1, 0]` 都算对）\n'
            '- 题目保证最多只有一组答案（也可能一组都没有），任何一种正确答案都算对\n'
            '- 如果找不到，返回空列表 `[]`\n'
            '- 同一个元素不能用两次，但**值相同的两个不同位置**可以（比如 `nums = [0, 0]`、`target = 0`）\n\n'
            '要求用**字典（哈希表）**做到 O(n)：边遍历边把「值 → 下标」记下来，'
            '对每个数先查「还差多少」在不在字典里，不要写双重循环（那是 O(n²)）。\n\n'
            '然后打印 `two_sum([2, 7, 11, 15], 9)`、`two_sum([3, 2, 4], 6)`、`two_sum([1, 2, 3], 7)` 的结果。'
        ),
        'starter_code': 'def two_sum(nums, target):\n    # 用字典记下「值 -> 下标」，边遍历边查\n    pass\n',
        'solution': (
            "def two_sum(nums, target):\n"
            "    seen = {}\n"
            "    for index, value in enumerate(nums):\n"
            "        need = target - value\n"
            "        if need in seen:\n"
            "            return [seen[need], index]\n"
            "        seen[value] = index\n"
            "    return []\n"
            "\n"
            "print(two_sum([2, 7, 11, 15], 9))\n"
            "print(two_sum([3, 2, 4], 6))\n"
            "print(two_sum([1, 2, 3], 7))\n"
        ),
        'checks': [
            "assert sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1], 'two_sum([2, 7, 11, 15], 9) 应返回下标 0 和 1，实际 %r' % (two_sum([2, 7, 11, 15], 9),)",
            "assert sorted(two_sum([3, 2, 4], 6)) == [1, 2], 'two_sum([3, 2, 4], 6) 应返回下标 1 和 2，实际 %r' % (two_sum([3, 2, 4], 6),)",
            "assert two_sum([1, 2, 3], 7) == [], '无解时应返回空列表，实际 %r' % (two_sum([1, 2, 3], 7),)",
            "assert two_sum([], 0) == [], '空列表应返回 []'",
            "assert two_sum([5], 10) == [], '只有一个元素时凑不出两个下标，应返回 []'",
            "assert sorted(two_sum([0, 0], 0)) == [0, 1], '值相同但下标不同也算一组答案，实际 %r' % (two_sum([0, 0], 0),)",
            "assert sorted(two_sum([-3, 4, 3, 90], 0)) == [0, 2], '有负数时也要能找对，实际 %r' % (two_sum([-3, 4, 3, 90], 0),)",
            "_r = two_sum([1, 3, 1, 2], 4)\nassert len(_r) == 2 and _r[0] != _r[1] and [1, 3, 1, 2][_r[0]] + [1, 3, 1, 2][_r[1]] == 4, '多个答案时任一组都对，但必须是两个不同下标且元素之和为 target，实际 %r' % (_r,)",
        ],
        'explanation': (
            '暴力法是「每个数都拿去和后面的数配对」，要比较 n²/2 次。'
            '哈希表法的思路是**把查找变成 O(1)**：遍历到 `value` 时，'
            '「我需要谁」是确定的——`need = target - value`，'
            '只要之前见过 need，答案就找到了。\n\n'
            '```python\n'
            'for index, value in enumerate(nums):\n'
            '    need = target - value\n'
            '    if need in seen:\n'
            '        return [seen[need], index]\n'
            '    seen[value] = index\n'
            '```\n\n'
            '**先查再存**很重要：如果先把当前元素存进去，`[0, 0]` 这种输入会返回两个相同的下标。\n\n'
            '常见错误：返回了值（`[2, 7]`）而不是下标（`[0, 1]`）；'
            '以及忘了「无解返回空列表」这个分支。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': '[0, 1]\n[1, 2]\n[]',
        'hints': ['对每个数先算 need = target - value，再去字典里查', '先查后存，顺序反了会用到同一个元素两次'],
    },
    {
        'id': 'alg-004',
        'track': 'algorithm',
        'chapter_id': 102,
        'chapter_title': '数组与双指针',
        'topic': '数组与双指针',
        'title': '双指针合并两个有序数组',
        'difficulty': 2,
        'tags': ['双指针', '归并', '有序数组'],
        'statement': (
            '定义函数 `merge_two(a, b)`：把两个**升序**列表合并成一个升序列表并返回。\n\n'
            '要求用**双指针**：两个指针分别指向 a、b 的开头，'
            '每次把较小的那个放进结果并让对应指针后移；'
            '某一个列表走完后，把另一个剩下的部分整体接上。时间复杂度 O(n + m)。\n\n'
            '**不允许**使用 `sorted()`、`.sort()`、也不要 `a + b` 之后再排序。\n\n'
            '重复元素必须**全部保留**（不能去重）。空列表也要能处理。\n\n'
            '然后打印 `merge_two([1, 3, 5], [2, 4, 6])`、`merge_two([], [])`、'
            '`merge_two([1, 2, 2], [2, 3])` 的结果。'
        ),
        'starter_code': 'def merge_two(a, b):\n    # i 指向 a，j 指向 b，比大小往 result 里放\n    pass\n',
        'solution': (
            "def merge_two(a, b):\n"
            "    i = 0\n"
            "    j = 0\n"
            "    result = []\n"
            "    while i < len(a) and j < len(b):\n"
            "        if a[i] <= b[j]:\n"
            "            result.append(a[i])\n"
            "            i += 1\n"
            "        else:\n"
            "            result.append(b[j])\n"
            "            j += 1\n"
            "    result.extend(a[i:])\n"
            "    result.extend(b[j:])\n"
            "    return result\n"
            "\n"
            "print(merge_two([1, 3, 5], [2, 4, 6]))\n"
            "print(merge_two([], []))\n"
            "print(merge_two([1, 2, 2], [2, 3]))\n"
        ),
        'checks': [
            "assert merge_two([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6], '合并结果不对：%r' % (merge_two([1, 3, 5], [2, 4, 6]),)",
            "assert merge_two([], []) == [], '两个空列表应得到空列表'",
            "assert merge_two([], [1, 2]) == [1, 2], '空列表和非空列表合并应原样返回另一个'",
            "assert merge_two([1, 2], []) == [1, 2], '非空列表和空列表合并应原样返回另一个'",
            "assert merge_two([1, 2, 2, 5], [2, 2, 3]) == [1, 2, 2, 2, 2, 3, 5], '重复元素必须全部保留，实际 %r' % (merge_two([1, 2, 2, 5], [2, 2, 3]),)",
            "assert merge_two([-5, -1], [-3, 0]) == [-5, -3, -1, 0], '负数也要正确合并'",
            "assert merge_two([9], [1]) == [1, 9], '每个列表各一个元素时也要比大小'",
            "assert 'sorted(' not in _src and '.sort(' not in _src, '本题要求用双指针合并，不能调用内置排序'",
        ],
        'explanation': (
            '双指针的套路：两个指针分别代表「两个列表还没处理的部分的开头」，'
            '每次比较 `a[i]` 和 `b[j]`，把小的放进结果。\n\n'
            '```python\n'
            'while i < len(a) and j < len(b):\n'
            '    if a[i] <= b[j]:\n'
            '        result.append(a[i]); i += 1\n'
            '    else:\n'
            '        result.append(b[j]); j += 1\n'
            'result.extend(a[i:])   # 谁剩下就整体接上\n'
            'result.extend(b[j:])\n'
            '```\n\n'
            '「剩下的整体接上」这一步最关键，很多人忘了写，'
            '结果 `[1, 2]` 和 `[3, 4]` 合并后只剩 `[1, 2]`。\n\n'
            '用 `<=` 而不是 `<`，是为了让 a 里的元素在同值时先出，'
            '这样合并结果**稳定**、可预测。\n\n'
            '为什么不用 `sorted(a + b)`？因为它要 O((n+m)log(n+m))，'
            '而双指针只要 O(n+m)——「已经有序」这个已知条件不该浪费。'
        ),
        'expected_output': '[1, 2, 3, 4, 5, 6]\n[]\n[1, 2, 2, 2, 3]',
        'hints': ['while 条件是 i < len(a) and j < len(b)，两个都没走完', '循环结束后用 extend 把剩下的切片接上'],
    },
    {
        'id': 'alg-005',
        'track': 'algorithm',
        'chapter_id': 102,
        'chapter_title': '数组与双指针',
        'topic': '数组与双指针',
        'title': '移动零（原地双指针）',
        'difficulty': 2,
        'tags': ['双指针', '原地修改', '数组'],
        'statement': (
            '定义函数 `move_zeroes(nums)`：把列表里所有的 0 都移到**末尾**，'
            '其他元素的**相对顺序保持不变**。\n\n'
            '要求：\n\n'
            '1. **原地修改**传入的那个列表（不新建列表、不返回拷贝）\n'
            '2. 返回**传入的那个列表本身**（也就是 `return nums`）\n'
            '3. 一趟遍历完成：用快慢两个指针，快指针找非零元素，慢指针指向「下一个非零元素该放的位置」，'
            '遇到非零就交换\n\n'
            '然后对 `[0, 1, 0, 3, 12]` 调用并打印结果。'
        ),
        'starter_code': 'def move_zeroes(nums):\n    # slow 指向下一个该放非零数的位置\n    slow = 0\n    pass\n',
        'solution': (
            "def move_zeroes(nums):\n"
            "    slow = 0\n"
            "    for fast in range(len(nums)):\n"
            "        if nums[fast] != 0:\n"
            "            nums[slow], nums[fast] = nums[fast], nums[slow]\n"
            "            slow += 1\n"
            "    return nums\n"
            "\n"
            "data = [0, 1, 0, 3, 12]\n"
            "print(move_zeroes(data))\n"
            "print(data)\n"
        ),
        'checks': [
            "_data = [0, 1, 0, 3, 12]\n_r = move_zeroes(_data)\nassert _r == [1, 3, 12, 0, 0], '移动结果不对：%r' % (_r,)",
            "_data2 = [0, 1, 0, 3, 12]\n_r2 = move_zeroes(_data2)\nassert _data2 == [1, 3, 12, 0, 0], '要求原地修改：传入的列表本身也要变成 [1, 3, 12, 0, 0]，实际 %r' % (_data2,)",
            "_data3 = [0, 1]\nassert move_zeroes(_data3) is _data3, '应返回传入的那个列表对象（return nums）'",
            "assert move_zeroes([]) == [], '空列表应返回空列表'",
            "assert move_zeroes([0]) == [0], '只有一个 0 时应保持 [0]'",
            "assert move_zeroes([0, 0, 0]) == [0, 0, 0], '全是 0 时列表不变'",
            "assert move_zeroes([1, 2, 3]) == [1, 2, 3], '没有 0 时列表不变'",
            "assert move_zeroes([0, 0, 5, 0, 7]) == [5, 7, 0, 0, 0], '非零元素的相对顺序必须保持，实际 %r' % (move_zeroes([0, 0, 5, 0, 7]),)",
        ],
        'explanation': (
            '「快慢指针」是数组原地操作的标准手法：\n\n'
            '- `slow`：下一个非零元素应该放的位置；\n'
            '- `fast`：负责扫描，找非零元素。\n\n'
            '```python\n'
            'for fast in range(len(nums)):\n'
            '    if nums[fast] != 0:\n'
            '        nums[slow], nums[fast] = nums[fast], nums[slow]\n'
            '        slow += 1\n'
            '```\n\n'
            '每次交换后，`slow` 左边全是非零元素，而 0 被换到了后面——一趟走完自然就分好了，'
            '而且非零元素之间的相对顺序不会变。\n\n'
            '另一种等价写法是「先用 slow 覆盖写非零数，最后把 slow 之后的格子填 0」，'
            '效果一样，但需要第二步补零。\n\n'
            '为什么强调原地？因为它只用了 O(1) 额外空间。'
            '在嵌入式或大数据场景里，「不开新数组」常常是硬性要求。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': '[1, 3, 12, 0, 0]\n[1, 3, 12, 0, 0]',
        'hints': ['fast 负责找非零元素，slow 指向下一个要放的位置', '交换写法 nums[slow], nums[fast] = nums[fast], nums[slow] 不用临时变量'],
    },
    {
        'id': 'alg-006',
        'track': 'algorithm',
        'chapter_id': 102,
        'chapter_title': '数组与双指针',
        'topic': '数组与双指针',
        'title': '三数之和（排序 + 双指针）',
        'difficulty': 3,
        'tags': ['双指针', '排序', '去重'],
        'statement': (
            '定义函数 `three_sum(nums)`：找出所有**和为 0** 的三元组（三个元素的下标必须互不相同）。\n\n'
            '返回格式要求：\n\n'
            '- 每个三元组是**内部升序**排列的列表，例如 `[-1, 0, 1]`\n'
            '- **不出现重复的三元组**：`[-1, 0, 1]` 和 `[1, -1, 0]` 视为同一个，只能出现一次\n'
            '- 三元组之间的先后顺序不限\n'
            '- 没有答案时返回 `[]`\n\n'
            '要求用「**先排序，再固定一个数 + 双指针扫另外两个**」的做法，时间复杂度 O(n²)，'
            '不要写三重循环（O(n³)）。nums 里可能有重复元素。\n\n'
            '然后打印 `three_sum([-1, 0, 1, 2, -1, -4])`、`three_sum([0, 0, 0])`、`three_sum([1, 2, 3])` 的结果。'
        ),
        'starter_code': 'def three_sum(nums):\n    # 排序后固定 i，left/right 双指针向中间收缩\n    pass\n',
        'solution': (
            "def three_sum(nums):\n"
            "    nums = sorted(nums)\n"
            "    result = []\n"
            "    n = len(nums)\n"
            "    for i in range(n - 2):\n"
            "        if nums[i] > 0:\n"
            "            break\n"
            "        if i > 0 and nums[i] == nums[i - 1]:\n"
            "            continue\n"
            "        left = i + 1\n"
            "        right = n - 1\n"
            "        while left < right:\n"
            "            total = nums[i] + nums[left] + nums[right]\n"
            "            if total == 0:\n"
            "                result.append([nums[i], nums[left], nums[right]])\n"
            "                while left < right and nums[left] == nums[left + 1]:\n"
            "                    left += 1\n"
            "                while left < right and nums[right] == nums[right - 1]:\n"
            "                    right -= 1\n"
            "                left += 1\n"
            "                right -= 1\n"
            "            elif total < 0:\n"
            "                left += 1\n"
            "            else:\n"
            "                right -= 1\n"
            "    return result\n"
            "\n"
            "print(three_sum([-1, 0, 1, 2, -1, -4]))\n"
            "print(three_sum([0, 0, 0]))\n"
            "print(three_sum([1, 2, 3]))\n"
        ),
        'checks': [
            "_got = three_sum([-1, 0, 1, 2, -1, -4])\nassert len(_got) == 2, '[-1, 0, 1, 2, -1, -4] 应有两组答案，实际 %r' % (_got,)",
            "assert sorted(tuple(sorted(t)) for t in three_sum([-1, 0, 1, 2, -1, -4])) == [(-1, -1, 2), (-1, 0, 1)], '答案内容不对：%r' % (three_sum([-1, 0, 1, 2, -1, -4]),)",
            "assert all(sum(t) == 0 for t in three_sum([-1, 0, 1, 2, -1, -4])), '每个三元组的和都必须为 0'",
            "assert all(list(t) == sorted(t) for t in three_sum([-1, 0, 1, 2, -1, -4])), '每个三元组内部要按升序排列'",
            "assert three_sum([]) == [], '空数组应返回 []'",
            "assert three_sum([1, 2, 3]) == [], '没有答案时应返回 []'",
            "assert sorted(tuple(sorted(t)) for t in three_sum([0, 0, 0])) == [(0, 0, 0)], 'three_sum([0, 0, 0]) 应返回 [[0, 0, 0]]'",
            "assert len(three_sum([0, 0, 0, 0])) == 1, '四个 0 也只能算出一组 [0, 0, 0]，不能重复'",
            "assert sorted(tuple(sorted(t)) for t in three_sum([-2, 0, 1, 1, 2])) == [(-2, 0, 2), (-2, 1, 1)], '[-2, 0, 1, 1, 2] 应得到 (-2, 0, 2) 和 (-2, 1, 1)，实际 %r' % (three_sum([-2, 0, 1, 1, 2]),)",
        ],
        'explanation': (
            '核心思路是**先排序，把「找三个数」变成「固定一个 + 找两个」**：\n\n'
            '1. 排序后，固定下标 i 的数；\n'
            '2. 在 i 右边用 left、right 双指针：和太小就 left 右移，和太大就 right 左移；\n'
            '3. 找到一组后 left、right 同时往中间收。\n\n'
            '去重是本题的灵魂，有两个地方要处理：\n\n'
            '- `if i > 0 and nums[i] == nums[i - 1]: continue`：跳过重复的固定数；\n'
            '- 找到一组后，跳过所有和当前 left / right 相同的元素。\n\n'
            '常见错误：只去重了 i，结果 `[0, 0, 0, 0]` 会输出两组 `[0, 0, 0]`；'
            '或者去重逻辑写成 `while nums[left] == nums[left+1]` 而忘了 `left < right` 保护，导致越界。\n\n'
            '另外 `if nums[i] > 0: break` 是个便宜的剪枝：排序后最小的数都大于 0，后面不可能凑成 0。\n\n'
            '复杂度：排序 O(n log n)，双指针部分 O(n²)，整体时间 O(n²)、空间 O(1)（不计结果）。'
        ),
        'expected_output': '[[-1, -1, 2], [-1, 0, 1]]\n[[0, 0, 0]]\n[]',
        'hints': ['排序之后固定 i，left = i + 1、right = n - 1 向中间夹', '跳过重复：i 和前一个相同时 continue；找到一组后跳过左右重复值'],
    },

    # ── 专题 103 字符串算法 ────────────────────────────────
    {
        'id': 'alg-007',
        'track': 'algorithm',
        'chapter_id': 103,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '第一个只出现一次的字符',
        'difficulty': 1,
        'tags': ['字符串', '哈希表', '计数'],
        'statement': (
            '定义函数 `first_unique_char(s)`：返回 s 中**第一个只出现一次**的字符的**下标**；'
            '如果不存在这样的字符，返回 `-1`。\n\n'
            '要求用**字典（哈希表）统计每个字符出现的次数**，一共两趟：'
            '第一趟数次数，第二趟从左到右找第一个次数为 1 的字符。整体 O(n)。\n\n'
            '`s` 只包含小写字母，也可能是空字符串。\n\n'
            '然后打印 `first_unique_char("leetcode")`、`first_unique_char("aabb")`、`first_unique_char("")` 的结果。'
        ),
        'starter_code': 'def first_unique_char(s):\n    # 第一趟统计次数，第二趟找第一个次数为 1 的\n    pass\n',
        'solution': (
            "def first_unique_char(s):\n"
            "    counts = {}\n"
            "    for ch in s:\n"
            "        counts[ch] = counts.get(ch, 0) + 1\n"
            "    for index, ch in enumerate(s):\n"
            "        if counts[ch] == 1:\n"
            "            return index\n"
            "    return -1\n"
            "\n"
            "print(first_unique_char('leetcode'))\n"
            "print(first_unique_char('aabb'))\n"
            "print(first_unique_char(''))\n"
        ),
        'checks': [
            "assert first_unique_char('leetcode') == 0, 'leetcode 里第一个不重复的字符是下标 0 的 l，实际 %r' % (first_unique_char('leetcode'),)",
            "assert first_unique_char('loveleetcode') == 2, 'loveleetcode 里第一个不重复的字符是下标 2 的 v，实际 %r' % (first_unique_char('loveleetcode'),)",
            "assert first_unique_char('aabb') == -1, '所有字符都重复时应返回 -1，实际 %r' % (first_unique_char('aabb'),)",
            "assert first_unique_char('') == -1, '空字符串应返回 -1'",
            "assert first_unique_char('a') == 0, '单字符字符串应返回 0'",
            "assert first_unique_char('aab') == 2, 'aab 里 b 只出现一次，下标是 2，实际 %r' % (first_unique_char('aab'),)",
            "assert first_unique_char('aaabbbccc') == -1, '三组重复字符应返回 -1'",
            "assert '{' in _src or 'Counter' in _src, '本题要求用字典统计每个字符出现的次数'",
        ],
        'explanation': (
            '两趟扫描是计数类问题的标准套路：\n\n'
            '```python\n'
            'counts = {}\n'
            'for ch in s:\n'
            '    counts[ch] = counts.get(ch, 0) + 1\n'
            'for index, ch in enumerate(s):\n'
            '    if counts[ch] == 1:\n'
            '        return index\n'
            'return -1\n'
            '```\n\n'
            '`counts.get(ch, 0) + 1` 是最常用的计数字典写法，'
            '键不存在时 get 返回默认值 0，避免 `KeyError`。\n\n'
            '为什么第二趟要**从左往右**扫？因为题目要的是「第一个」；'
            '如果直接遍历字典取第一个次数为 1 的键，'
            '得到的是**插入顺序里最早统计到**的字符，'
            '对 `"aab"` 没问题，对 `"baab"` 会答错（应该是 b）。\n\n'
            '也可以用 `collections.Counter(s)`，一行完成统计。\n\n'
            '复杂度：时间 O(n)、空间 O(1)（字符种类数最多 26）。'
        ),
        'expected_output': '0\n-1\n-1',
        'hints': ['先统计次数，再从左到右找第一个次数为 1 的字符', 'counts.get(ch, 0) + 1 是标准计数写法'],
    },
    {
        'id': 'alg-008',
        'track': 'algorithm',
        'chapter_id': 103,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '字符串压缩（游程编码）',
        'difficulty': 2,
        'tags': ['字符串', '一次遍历', '计数'],
        'statement': (
            '定义函数 `compress(s)`：把连续重复的字符压缩成「**字符 + 次数**」的形式。\n\n'
            '例如：\n\n'
            '- `"aaabbc"` → `"a3b2c1"`\n'
            '- `"abc"` → `"a1b1c1"`（只出现一次的字符也要写出 1，这样才方便解压）\n'
            '- `"aaaa"` → `"a4"`\n'
            '- `""` → `""`（空串返回空串）\n\n'
            '要求一次遍历完成（O(n)）：记住「当前字符」和「已经连了几个」，'
            '遇到不同的字符就把上一段写进结果，最后别忘了把**最后一段**补上。\n\n'
            '然后打印 `compress("aaabbc")`、`compress("")`、`compress("abc")` 的结果。'
        ),
        'starter_code': 'def compress(s):\n    # 记住当前字符和连续个数，遍历时遇到变化就写一段\n    pass\n',
        'solution': (
            "def compress(s):\n"
            "    if not s:\n"
            "        return ''\n"
            "    parts = []\n"
            "    current = s[0]\n"
            "    count = 1\n"
            "    for ch in s[1:]:\n"
            "        if ch == current:\n"
            "            count += 1\n"
            "        else:\n"
            "            parts.append(current + str(count))\n"
            "            current = ch\n"
            "            count = 1\n"
            "    parts.append(current + str(count))\n"
            "    return ''.join(parts)\n"
            "\n"
            "print(compress('aaabbc'))\n"
            "print(compress(''))\n"
            "print(compress('abc'))\n"
        ),
        'checks': [
            "assert compress('aaabbc') == 'a3b2c1', 'compress(\\'aaabbc\\') 应为 a3b2c1，实际 %r' % (compress('aaabbc'),)",
            "assert compress('') == '', '空字符串应返回空字符串'",
            "assert compress('abc') == 'a1b1c1', '只出现一次的字符也要写出 1，实际 %r' % (compress('abc'),)",
            "assert compress('a') == 'a1', '单字符应返回 a1，实际 %r' % (compress('a'),)",
            "assert compress('aaaa') == 'a4', 'compress(\\'aaaa\\') 应为 a4，实际 %r' % (compress('aaaa'),)",
            "assert compress('aabbaa') == 'a2b2a2', '相同的字符中间被打断要重新计数，实际 %r' % (compress('aabbaa'),)",
            "assert compress('abbbbc') == 'a1b4c1', '最后一段也要写进结果，实际 %r' % (compress('abbbbc'),)",
            "assert compress('zz') == 'z2', '两个相同字符应得到 z2，实际 %r' % (compress('zz'),)",
        ],
        'explanation': (
            '「游程编码」（Run-Length Encoding）是最简单的无损压缩：'
            '把 `aaaaa` 写成 `a5`，连续重复越长压缩率越高。图片格式里的 PCX、BMP 就用了它。\n\n'
            '写法的关键在于**两个状态的维护**：`current`（当前这一段是什么字符）和 `count`（连着几个）。'
            '遍历时如果字符没变就 `count += 1`；变了就把 `current + str(count)` 存起来，'
            '然后把 current/count 重置成新字符。\n\n'
            '最常见的错误是**忘了处理最后一段**：循环结束时最后那一组还没写进结果，'
            '所以 `compress("abbbbc")` 会丢掉结尾的 `c1`。修复办法就是循环外再 append 一次。\n\n'
            '用列表收集再用 `"".join()` 拼接，而不是在循环里 `result += ...`：'
            '字符串不可变，反复拼接会不断新建对象、越拼越慢。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': 'a3b2c1\n\na1b1c1',
        'hints': ['用 current 和 count 记住当前这一段', '循环结束后必须把最后一段补写进结果'],
    },
    {
        'id': 'alg-009',
        'track': 'algorithm',
        'chapter_id': 103,
        'chapter_title': '字符串算法',
        'topic': '字符串算法',
        'title': '最长无重复字符子串（滑动窗口）',
        'difficulty': 3,
        'tags': ['字符串', '滑动窗口', '哈希表'],
        'statement': (
            '定义函数 `length_of_longest_substring(s)`：返回不含重复字符的**最长连续子串的长度**。\n\n'
            '例如 `"abcabcbb"` 的最长无重复子串是 `"abc"`，长度 3；`"bbbbb"` 的长度是 1。\n\n'
            '要求用**滑动窗口**做到 O(n)：\n\n'
            '- 用 `left` 表示窗口左边界，`right` 从左到右扫；\n'
            '- 用一个字典记录每个字符**最后出现的位置**；\n'
            '- 遇到重复字符时，把 `left` 直接跳到「上一个相同字符的位置 + 1」'
            '（注意要判断这个位置是不是在 left 右边，否则 left 会往回退）；\n'
            '- 每一步用 `right - left + 1` 更新答案。\n\n'
            '不要枚举所有子串（那是 O(n²) 以上）。空串返回 0。\n\n'
            '然后打印 `length_of_longest_substring("abcabcbb")`、`length_of_longest_substring("bbbbb")`、'
            '`length_of_longest_substring("pwwkew")` 的结果。'
        ),
        'starter_code': 'def length_of_longest_substring(s):\n    # last 记录字符最后出现的位置，left 是窗口左边界\n    last = {}\n    left = 0\n    best = 0\n    pass\n',
        'solution': (
            "def length_of_longest_substring(s):\n"
            "    last = {}\n"
            "    left = 0\n"
            "    best = 0\n"
            "    for right, ch in enumerate(s):\n"
            "        if ch in last and last[ch] >= left:\n"
            "            left = last[ch] + 1\n"
            "        last[ch] = right\n"
            "        if right - left + 1 > best:\n"
            "            best = right - left + 1\n"
            "    return best\n"
            "\n"
            "print(length_of_longest_substring('abcabcbb'))\n"
            "print(length_of_longest_substring('bbbbb'))\n"
            "print(length_of_longest_substring('pwwkew'))\n"
        ),
        'checks': [
            "assert length_of_longest_substring('abcabcbb') == 3, 'abcabcbb 的答案是 3（abc），实际 %r' % (length_of_longest_substring('abcabcbb'),)",
            "assert length_of_longest_substring('bbbbb') == 1, 'bbbbb 的答案是 1，实际 %r' % (length_of_longest_substring('bbbbb'),)",
            "assert length_of_longest_substring('pwwkew') == 3, 'pwwkew 的答案是 3（wke），实际 %r' % (length_of_longest_substring('pwwkew'),)",
            "assert length_of_longest_substring('') == 0, '空串应返回 0'",
            "assert length_of_longest_substring('a') == 1, '单字符应返回 1'",
            "assert length_of_longest_substring('abba') == 2, 'abba 的答案是 2（ab 或 ba），实际 %r' % (length_of_longest_substring('abba'),)",
            "assert length_of_longest_substring('dvdf') == 3, 'dvdf 的答案是 3（vdf），实际 %r' % (length_of_longest_substring('dvdf'),)",
            "assert length_of_longest_substring('abcdefg') == 7, '全不重复时应等于长度本身'",
            "assert length_of_longest_substring('tmmzuxt') == 5, 'tmmzuxt 的答案是 5（mzuxt），实际 %r' % (length_of_longest_substring('tmmzuxt'),)",
            "assert length_of_longest_substring(' ' * 10) == 1, '十个空格的最长无重复长度是 1'",
        ],
        'explanation': (
            '滑动窗口的核心是：**窗口 `[left, right]` 内永远没有重复字符**。'
            '右边界每次只走一步，左边界只往右走，两个指针都只走 n 步，所以是 O(n)。\n\n'
            '```python\n'
            'if ch in last and last[ch] >= left:\n'
            '    left = last[ch] + 1\n'
            'last[ch] = right\n'
            'best = max(best, right - left + 1)\n'
            '```\n\n'
            '`last[ch] >= left` 这个判断极易漏掉。看 `"abba"`：\n'
            '扫到最后一个 a 时，`last["a"] = 0`，但那时 `left` 已经是 2 了，'
            '如果直接把 left 跳到 0 + 1 = 1，窗口就**倒退**了，答案会算错。\n\n'
            '另一个常见错误是「遇到重复就 left += 1」，那是暴力收缩，'
            '虽然结果对，但最坏退化到 O(n²)——本题的考点正是**直接跳到重复字符的下一位**。\n\n'
            '复杂度：时间 O(n)、空间 O(字符集大小)。'
        ),
        'expected_output': '3\n1\n3',
        'hints': ['last 记录的是「字符最后出现的位置」，left 是窗口左边界', 'left 只能往右跳：先判断 last[ch] >= left 再更新'],
    },

    # ── 专题 104 哈希表 ────────────────────────────────────
    {
        'id': 'alg-010',
        'track': 'algorithm',
        'chapter_id': 104,
        'chapter_title': '哈希表',
        'topic': '哈希表',
        'title': '有效的字母异位词',
        'difficulty': 1,
        'tags': ['哈希表', '字符串', '计数'],
        'statement': (
            '定义函数 `is_anagram(s, t)`：判断 s 和 t 是否互为**字母异位词**'
            '（由完全相同的字符组成、每种字符的个数也一样，只是顺序不同），'
            '返回 `True` / `False`。\n\n'
            '- `is_anagram("anagram", "nagaram")` → `True`\n'
            '- `is_anagram("rat", "car")` → `False`\n'
            '- 空串和空串互为异位词\n'
            '- 大小写敏感：`"A"` 和 `"a"` 不算同一个字符\n\n'
            '要求用**字典统计每个字符出现的次数**（O(n)）：'
            '先统计 s 的次数，再遍历 t 逐个减掉，出现负数或找不到就返回 False。\n\n'
            '**不允许**用 `sorted(s) == sorted(t)` 直接比较，也不要用 `set`——'
            '因为集合会忽略「个数」，`"aab"` 和 `"ab"` 用 set 比会误判成相等。\n\n'
            '然后打印 `is_anagram("anagram", "nagaram")`、`is_anagram("rat", "car")`、'
            '`is_anagram("", "")` 的结果。'
        ),
        'starter_code': 'def is_anagram(s, t):\n    # 先统计 s 的字符次数，再用 t 去抵消\n    pass\n',
        'solution': (
            "def is_anagram(s, t):\n"
            "    if len(s) != len(t):\n"
            "        return False\n"
            "    counts = {}\n"
            "    for ch in s:\n"
            "        counts[ch] = counts.get(ch, 0) + 1\n"
            "    for ch in t:\n"
            "        if ch not in counts:\n"
            "            return False\n"
            "        counts[ch] -= 1\n"
            "        if counts[ch] < 0:\n"
            "            return False\n"
            "    return True\n"
            "\n"
            "print(is_anagram('anagram', 'nagaram'))\n"
            "print(is_anagram('rat', 'car'))\n"
            "print(is_anagram('', ''))\n"
        ),
        'checks': [
            "assert is_anagram('anagram', 'nagaram') is True, 'anagram 与 nagaram 互为异位词'",
            "assert is_anagram('rat', 'car') is False, 'rat 与 car 不是异位词'",
            "assert is_anagram('', '') is True, '两个空串互为异位词'",
            "assert is_anagram('a', 'a') is True, '单个相同字符应返回 True'",
            "assert is_anagram('ab', 'a') is False, '长度不同一定不是异位词'",
            "assert is_anagram('aacc', 'ccac') is False, '字符个数不同就不是异位词（set 会误判这里）'",
            "assert is_anagram('listen', 'silent') is True, 'listen 与 silent 互为异位词'",
            "assert is_anagram('A', 'a') is False, '大小写敏感，A 和 a 不是同一个字符'",
            "assert is_anagram('aab', 'abb') is False, 'a 与 b 的个数不同，应返回 False'",
            "assert 'sorted(' not in _src, '本题要求用哈希表统计次数，不要用 sorted(s) == sorted(t)'",
        ],
        'explanation': (
            '字母异位词的判定标准是「**每种字符的个数完全一致**」，'
            '所以天然适合用计数字典。\n\n'
            '最短的写法是 `collections.Counter(s) == Counter(t)`，思路一样。'
            '手写的版本用「先加后减」：统计 s 时每个字符 +1，遍历 t 时 -1，'
            '一旦减到负数说明 t 里这个字符比 s 多，直接返回 False。\n\n'
            '为什么不能只比 `set`？`set("aab") == set("abb")` 都是 `{"a","b"}`，'
            '但两个串明显不互为异位词——**集合丢掉了「数量」这个关键信息**。\n\n'
            '为什么开头就 `if len(s) != len(t): return False`？'
            '这是一个免费的剪枝：长度不同根本不用进循环算。\n\n'
            '复杂度：时间 O(n)、空间 O(字符种类数)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['长度不同直接 False，省一次循环', '先用 s 建立计数字典，再用 t 逐个减，减到负数就返回 False'],
    },
    {
        'id': 'alg-011',
        'track': 'algorithm',
        'chapter_id': 104,
        'chapter_title': '哈希表',
        'topic': '哈希表',
        'title': '字母异位词分组',
        'difficulty': 2,
        'tags': ['哈希表', '分组', '排序'],
        'statement': (
            '定义函数 `group_anagrams(words)`：把互为异位词的单词分到**同一组**，返回分组的列表。\n\n'
            '- 组内单词的顺序不限，组与组之间的顺序也不限\n'
            '- `group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])` 应得到 3 组：'
            '`{eat, tea, ate}`、`{tan, nat}`、`{bat}`\n'
            '- 空列表返回 `[]`；空字符串是合法单词（`["", ""]` 只有 1 组）\n\n'
            '要求用**字典**：把「异位词的共同特征」当作键（例如把单词的字母排序后得到的字符串，'
            '或者 26 个字母的计数元组），一次遍历把单词塞进对应的组里，'
            '复杂度约 O(n · k log k)（k 是单词长度）。\n\n'
            '不要两两比较单词（那是 O(n² · k)）。\n\n'
            '然后打印这个经典例子的分组结果。'
        ),
        'starter_code': 'def group_anagrams(words):\n    # key 用「排序后的字母」，同 key 的单词放一组\n    groups = {}\n    pass\n',
        'solution': (
            "def group_anagrams(words):\n"
            "    groups = {}\n"
            "    for word in words:\n"
            "        key = ''.join(sorted(word))\n"
            "        groups.setdefault(key, []).append(word)\n"
            "    return list(groups.values())\n"
            "\n"
            "print(group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']))\n"
            "print(group_anagrams([]))\n"
            "print(group_anagrams(['abc', 'cba', 'ab', 'ba']))\n"
        ),
        'checks': [
            "_r = group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])\nassert len(_r) == 3, '应分成 3 组，实际 %d 组：%r' % (len(_r), _r)",
            "assert sorted(sorted(g) for g in group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])) == [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']], '分组内容不对：%r' % (group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']),)",
            "assert group_anagrams([]) == [], '空列表应返回 []'",
            "_single = group_anagrams(['a'])\nassert len(_single) == 1 and list(_single[0]) == ['a'], '只有一个单词时应返回 1 组'",
            "_empty = group_anagrams(['', ''])\nassert len(_empty) == 1 and len(_empty[0]) == 2, '两个空字符串应分到同一组'",
            "_mix = group_anagrams(['abc', 'cba', 'ab', 'ba'])\nassert sorted(sorted(g) for g in _mix) == [['ab', 'ba'], ['abc', 'cba']], '分组内容不对：%r' % (_mix,)",
            "_dup = group_anagrams(['ab', 'ab'])\nassert len(_dup) == 1 and len(_dup[0]) == 2, '两个相同的单词属于同一组，且不能去重'",
            "_all = ['eat', 'tea', 'tan', 'ate', 'nat', 'bat']\n_flat = [w for g in group_anagrams(_all) for w in g]\nassert sorted(_flat) == sorted(_all), '每个单词都要出现一次，不能丢也不能多'",
        ],
        'explanation': (
            '分组的通用套路是：**给每个元素算一个「特征键」，同键的就是一组**。'
            '异位词的特征键就是把字母排序后的字符串——`eat`、`tea`、`ate` 排序后都是 `aet`。\n\n'
            '```python\n'
            'groups.setdefault(key, []).append(word)\n'
            '```\n\n'
            '`setdefault(key, [])` 的语义是「取不到就设成 `[]` 再返回」，'
            '所以能直接 `.append`，不用写「先判断键在不在」的三行代码。\n\n'
            '另一个常用键是「26 个字母的出现次数组成的元组」'
            '（`tuple(Counter(word)[c] for c in string.ascii_lowercase)`），'
            '它把每个单词的建键成本从 O(k log k) 降到 O(k)，适合超长单词。\n\n'
            '常见错误：用 `word` 本身或 `len(word)` 当键，那样只能分出长度相同的组，语义完全错。\n\n'
            '复杂度：时间 O(n · k log k)、空间 O(n · k)。'
        ),
        'expected_output': "[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]\n[]\n[['abc', 'cba'], ['ab', 'ba']]",
        'hints': ['键用 "".join(sorted(word))，用 setdefault 直接 append', '返回值是「组的列表」，用 list(groups.values()) 一次转好'],
    },
    {
        'id': 'alg-012',
        'track': 'algorithm',
        'chapter_id': 104,
        'chapter_title': '哈希表',
        'topic': '哈希表',
        'title': '最长连续序列（集合 O(n)）',
        'difficulty': 2,
        'tags': ['哈希表', '集合', '连续序列'],
        'statement': (
            '定义函数 `longest_consecutive(nums)`：返回数组里**最长的连续整数序列的长度**。\n\n'
            '- `[100, 4, 200, 1, 3, 2]` → 4（因为有 `1, 2, 3, 4`）\n'
            '- 序列里的数字在数组里的位置任意，连续指的是**数值连续**（相差 1）\n'
            '- 重复的数字只算一次：`[1, 1, 2]` → 2\n'
            '- 空数组 → 0；只有一个数 → 1\n'
            '- 不要求序列在数组里连续排列\n\n'
            '要求用**集合**做到 O(n)：先把所有数放进集合，'
            '只从「没有前驱」的数开始数——也就是 `x - 1` 不在集合里时，'
            '才从 x 开始 `x+1`、`x+2`… 一路数下去。\n\n'
            '不要排序后扫描（那是 O(n log n)）。\n\n'
            '然后打印 `longest_consecutive([100, 4, 200, 1, 3, 2])`、`longest_consecutive([])`、'
            '`longest_consecutive([1, 1, 2, 2, 3])` 的结果。'
        ),
        'starter_code': 'def longest_consecutive(nums):\n    # 先转成集合；只从「x - 1 不在集合里」的数开始往后数\n    pass\n',
        'solution': (
            "def longest_consecutive(nums):\n"
            "    numbers = set(nums)\n"
            "    best = 0\n"
            "    for value in numbers:\n"
            "        if value - 1 in numbers:\n"
            "            continue\n"
            "        length = 1\n"
            "        while value + length in numbers:\n"
            "            length += 1\n"
            "        if length > best:\n"
            "            best = length\n"
            "    return best\n"
            "\n"
            "print(longest_consecutive([100, 4, 200, 1, 3, 2]))\n"
            "print(longest_consecutive([]))\n"
            "print(longest_consecutive([1, 1, 2, 2, 3]))\n"
        ),
        'checks': [
            "assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4, '最长连续序列是 1,2,3,4，长度 4，实际 %r' % (longest_consecutive([100, 4, 200, 1, 3, 2]),)",
            "assert longest_consecutive([]) == 0, '空数组应返回 0'",
            "assert longest_consecutive([1, 1, 2, 2, 3]) == 3, '重复数字只算一次，答案是 3，实际 %r' % (longest_consecutive([1, 1, 2, 2, 3]),)",
            "assert longest_consecutive([0]) == 1, '单个元素应返回 1'",
            "assert longest_consecutive([5, 5, 5]) == 1, '全是同一个数时答案是 1'",
            "assert longest_consecutive([1, 2, 0, 1]) == 3, '0,1,2 是连续的，答案是 3，实际 %r' % (longest_consecutive([1, 2, 0, 1]),)",
            "assert longest_consecutive([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]) == 7, '3~9 是连续的，答案是 7，实际 %r' % (longest_consecutive([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]),)",
            "assert longest_consecutive([-2, -1, 0, 1]) == 4, '负数序列也要能数，实际 %r' % (longest_consecutive([-2, -1, 0, 1]),)",
            "assert longest_consecutive(list(range(300))) == 300, '0~299 的连续长度应为 300'",
        ],
        'explanation': (
            '如果排序，就是 O(n log n)，而且还要处理重复；'
            '用集合可以做到 O(n)，关键是**避免重复劳动**：\n\n'
            '```python\n'
            'for value in numbers:\n'
            '    if value - 1 in numbers:\n'
            '        continue          # 不是序列起点，跳过\n'
            '    length = 1\n'
            '    while value + length in numbers:\n'
            '        length += 1\n'
            '```\n\n'
            '为什么这也是 O(n)？因为 `while` 只会在「序列的起点」上跑，'
            '每个数字**最多被数一次**，总工作量是 O(n)，而不是 O(n²)。\n\n'
            '如果省掉 `value - 1 in numbers` 这个判断，'
            '每个数字都要往后数一遍，最坏变成 O(n²)。\n\n'
            '常见错误：用 `sorted(set(nums))` 再扫描（能过但不满足复杂度要求）；'
            '以及忘记重复元素——集合天然去重，重复数只算一次正好符合题意。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': '4\n0\n3',
        'hints': ['先 set(nums)，重复元素自动只算一次', '只从「没有前驱」的数开始数，才能保证整体 O(n)'],
    },

    # ── 专题 105 栈与队列 ──────────────────────────────────
    {
        'id': 'alg-013',
        'track': 'algorithm',
        'chapter_id': 105,
        'chapter_title': '栈与队列',
        'topic': '栈与队列',
        'title': '有效的括号（栈的经典用法）',
        'difficulty': 1,
        'tags': ['栈', '括号匹配', '哈希表'],
        'statement': (
            '定义函数 `is_valid(s)`：判断只由 `(` `)` `[` `]` `{` `}` 组成的字符串是否**括号匹配**，'
            '返回 `True` / `False`。\n\n'
            '有效意味着：\n\n'
            '- 每个左括号都能被**同类型**的右括号按**正确顺序**闭合\n'
            '- `"()[]{}"` 有效；`"(]"`、`"([)]"`、`"((("`、`")"` 都无效\n'
            '- 空字符串视为有效\n\n'
            '要求用**栈**实现，一次遍历 O(n)：遇到左括号就压栈；'
            '遇到右括号时，栈不能为空、且栈顶必须是它对应的左括号，否则直接返回 False；'
            '最后栈必须为空。\n\n'
            '然后打印 `is_valid("()[]{}")`、`is_valid("([)]")`、`is_valid("")` 的结果。'
        ),
        'starter_code': "def is_valid(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    pass\n",
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
            "print(is_valid('()[]{}'))\n"
            "print(is_valid('([)]'))\n"
            "print(is_valid(''))\n"
        ),
        'checks': [
            "assert is_valid('()[]{}') is True, '()[]{} 是有效的，实际 %r' % (is_valid('()[]{}'),)",
            "assert is_valid('([)]') is False, '([)] 交叉嵌套是无效的，实际 %r' % (is_valid('([)]'),)",
            "assert is_valid('') is True, '空字符串视为有效'",
            "assert is_valid('(') is False, '只有左括号没有闭合，应返回 False'",
            "assert is_valid(')') is False, '只有右括号，应返回 False'",
            "assert is_valid('(]') is False, '括号类型不匹配，应返回 False'",
            "assert is_valid('((()))') is True, '多层同类嵌套是有效的'",
            "assert is_valid('{[]}') is True, '多层混合嵌套是有效的'",
            "assert is_valid('(){}[]') is True, '并列的括号组都有效'",
            "assert is_valid('[(])') is False, '交叉嵌套都必须判为无效'",
        ],
        'explanation': (
            '栈的「后进先出」正好对应括号的嵌套规则：**最后打开的括号必须最先关闭**。\n\n'
            '```python\n'
            'for ch in s:\n'
            '    if ch in "([{":\n'
            '        stack.append(ch)\n'
            '    elif not stack or stack.pop() != pairs[ch]:\n'
            '        return False\n'
            'return not stack\n'
            '```\n\n'
            '两个最容易漏的点：\n\n'
            '1. **栈为空时遇到右括号**要立刻返回 False，否则 `pop()` 会抛 `IndexError`；\n'
            '2. 循环结束后**栈必须为空**，否则 `"((("` 这种「只有左括号」的串会被误判为有效。\n\n'
            '`stack.pop() != pairs[ch]` 这个写法很紧凑：pop 既取了栈顶又把它删掉，'
            '因为不管匹配成功还是失败，这个栈顶都不再需要。\n\n'
            '另一种做法是遇到左括号时直接压入「对应的右括号」，'
            '遇到右括号时只比较是否相等，代码稍短一点。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['左括号压栈，右括号弹出栈顶比对', '别忘了最后要检查「栈是空的」'],
    },
    {
        'id': 'alg-014',
        'track': 'algorithm',
        'chapter_id': 105,
        'chapter_title': '栈与队列',
        'topic': '栈与队列',
        'title': '最小栈（O(1) 取最小值）',
        'difficulty': 2,
        'tags': ['栈', '设计', 'O(1)'],
        'statement': (
            '实现 `MinStack` 类：\n\n'
            '- `__init__(self)`：初始化空栈\n'
            '- `push(self, val)`：把 val 压入栈\n'
            '- `pop(self)`：弹出栈顶元素并**返回它的值**\n'
            '- `top(self)`：返回栈顶元素，但不弹出\n'
            '- `get_min(self)`：返回当前栈中的**最小元素**\n\n'
            '要求 `get_min` 是 **O(1)**（不能每次遍历整个栈）：'
            '办法是**再开一个辅助栈**同步记录「到目前为止的最小值」——'
            '压入 val 时，如果辅助栈为空或 `val <= 辅助栈栈顶`，就往辅助栈也压一个 val；'
            '弹出时，如果弹出的值正好等于辅助栈栈顶，辅助栈也跟着弹。\n\n'
            '然后依次 push -2、0、-3，打印 get_min()、pop()、top()、get_min() 的结果。'
        ),
        'starter_code': 'class MinStack:\n    def __init__(self):\n        # 需要两个列表：一个存数据，一个同步存最小值\n        pass\n',
        'solution': (
            "class MinStack:\n"
            "    def __init__(self):\n"
            "        self.data = []\n"
            "        self.mins = []\n"
            "\n"
            "    def push(self, val):\n"
            "        self.data.append(val)\n"
            "        if not self.mins or val <= self.mins[-1]:\n"
            "            self.mins.append(val)\n"
            "\n"
            "    def pop(self):\n"
            "        val = self.data.pop()\n"
            "        if self.mins and self.mins[-1] == val:\n"
            "            self.mins.pop()\n"
            "        return val\n"
            "\n"
            "    def top(self):\n"
            "        return self.data[-1]\n"
            "\n"
            "    def get_min(self):\n"
            "        return self.mins[-1]\n"
            "\n"
            "stack = MinStack()\n"
            "stack.push(-2)\n"
            "stack.push(0)\n"
            "stack.push(-3)\n"
            "print(stack.get_min())\n"
            "print(stack.pop())\n"
            "print(stack.top())\n"
            "print(stack.get_min())\n"
        ),
        'checks': [
            "st = MinStack()\nst.push(-2)\nst.push(0)\nst.push(-3)\nassert st.get_min() == -3, '压入 -2、0、-3 之后最小值应是 -3，实际 %r' % (st.get_min(),)",
            "st = MinStack()\nst.push(-2)\nst.push(0)\nst.push(-3)\nassert st.pop() == -3, 'pop() 应返回被弹出的栈顶元素 -3，实际 %r' % (st.pop(),)",
            "st = MinStack()\nst.push(-2)\nst.push(0)\nassert st.top() == 0 and st.get_min() == -2, 'top() 应返回 0 但不弹出，此时最小值是 -2'",
            "st2 = MinStack()\nst2.push(5)\nst2.push(5)\nassert st2.get_min() == 5\nst2.pop()\nassert st2.get_min() == 5, '弹出重复的最小值 5 之后，最小值仍然是 5（另一个还在）'",
            "st3 = MinStack()\nst3.push(1)\nst3.push(2)\nst3.push(0)\nassert st3.get_min() == 0\nassert st3.pop() == 0\nassert st3.get_min() == 1, '把最小值 0 弹出后，最小值应恢复成 1，实际 %r' % (st3.get_min(),)",
            "st4 = MinStack()\nfor _i in range(300, 0, -1):\n    st4.push(_i)\nfor _i in range(1, 301):\n    assert st4.get_min() == _i, '弹出第 %d 个数之前最小值应为 %d，实际 %r' % (_i, _i, st4.get_min())\n    assert st4.pop() == _i, 'pop() 应返回 %d' % _i",
            "st5 = MinStack()\nst5.push(3)\nassert st5.top() == 3 and st5.get_min() == 3, '栈里只有一个元素时 top 和 get_min 都是它'",
        ],
        'explanation': (
            '如果 `get_min` 每次都 `min(self.data)`，那是 O(n)；'
            '数据量大、调用频繁时会成为瓶颈。用**辅助栈**可以做到 O(1)：\n\n'
            '```python\n'
            'def push(self, val):\n'
            '    self.data.append(val)\n'
            '    if not self.mins or val <= self.mins[-1]:\n'
            '        self.mins.append(val)\n'
            '```\n\n'
            '辅助栈的栈顶永远是「当前整个栈的最小值」，因为只有更小的值才会被压进去。\n\n'
            '两个易错点：\n\n'
            '1. `push` 时用 `<=` 而不是 `<`：否则 `[5, 5]` 里弹出第一个 5 时'
            '辅助栈会把自己的 5 弹掉，最小值就丢了；\n'
            '2. `pop` 时必须判断「弹出的值是否等于辅助栈栈顶」再决定要不要同步弹出，'
            '否则辅助栈和数据栈长度会对不上。\n\n'
            '复杂度：push / pop / top / get_min 全是 O(1)，空间 O(n)。'
        ),
        'expected_output': '-3\n-3\n0\n-2',
        'hints': ['辅助栈的栈顶 = 当前最小值', 'push 时用 val <= mins[-1] 判断，重复最小值也要存'],
    },
    {
        'id': 'alg-015',
        'track': 'algorithm',
        'chapter_id': 105,
        'chapter_title': '栈与队列',
        'topic': '栈与队列',
        'title': '每日温度（单调栈）',
        'difficulty': 3,
        'tags': ['单调栈', '数组', 'O(n)'],
        'statement': (
            '定义函数 `daily_temperatures(temperatures)`：给定每天的气温列表，'
            '返回一个**等长**的列表 `answer`，其中 `answer[i]` 表示'
            '「第 i 天之后，还要等几天才会遇到**更高**的温度」；'
            '如果之后都不会更高，就填 `0`。\n\n'
            '例如 `[73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`。\n\n'
            '要求用**单调栈**做到 O(n)：栈里存的是**下标**，'
            '并保持「从栈底到栈顶的温度严格递减」；'
            '每遇到一个新温度，就把栈顶所有比它冷的下标弹出，'
            '这些位置等的天数就是「当前下标 - 它的下标」。\n\n'
            '不要对每天都往后扫一遍（那是 O(n²)）。空列表返回 `[]`。\n\n'
            '然后打印这个例子、`[30, 40, 50, 60]` 和 `[30, 60, 90]` 的结果。'
        ),
        'starter_code': 'def daily_temperatures(temperatures):\n    # stack 里存下标，栈内温度递减\n    answer = [0] * len(temperatures)\n    stack = []\n    pass\n',
        'solution': (
            "def daily_temperatures(temperatures):\n"
            "    answer = [0] * len(temperatures)\n"
            "    stack = []\n"
            "    for i, t in enumerate(temperatures):\n"
            "        while stack and temperatures[stack[-1]] < t:\n"
            "            j = stack.pop()\n"
            "            answer[j] = i - j\n"
            "        stack.append(i)\n"
            "    return answer\n"
            "\n"
            "print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))\n"
            "print(daily_temperatures([30, 40, 50, 60]))\n"
            "print(daily_temperatures([30, 60, 90]))\n"
        ),
        'checks': [
            "assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0], '经典例子应得到 [1, 1, 4, 2, 1, 1, 0, 0]，实际 %r' % (daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]),)",
            "assert daily_temperatures([]) == [], '空列表应返回 []'",
            "assert daily_temperatures([50]) == [0], '只有一天时后面没有更高的温度，返回 [0]'",
            "assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0], '递增序列应得到 [1, 1, 1, 0]，实际 %r' % (daily_temperatures([30, 40, 50, 60]),)",
            "assert daily_temperatures([90, 80, 70]) == [0, 0, 0], '递减序列都等不到更高的温度'",
            "assert daily_temperatures([40, 40, 40]) == [0, 0, 0], '温度相同不算「更高」，应全部为 0'",
            "assert daily_temperatures([30, 60, 90]) == [1, 1, 0], '实际 %r' % (daily_temperatures([30, 60, 90]),)",
            "assert daily_temperatures([55, 38, 53, 81, 61, 93, 97, 32, 43, 78]) == [3, 1, 1, 2, 1, 1, 0, 1, 1, 0], '长一点的例子算错了：%r' % (daily_temperatures([55, 38, 53, 81, 61, 93, 97, 32, 43, 78]),)",
            "assert daily_temperatures(list(range(100))) == [1] * 99 + [0], '0~99 递增序列的答案是 99 个 1 加一个 0'",
        ],
        'explanation': (
            '这题是**单调栈**的入门题。栈里存的是「还没等到更高温度」的那些天的**下标**，'
            '而且它们的温度从栈底到栈顶**递减**（栈顶最冷）。\n\n'
            '```python\n'
            'for i, t in enumerate(temperatures):\n'
            '    while stack and temperatures[stack[-1]] < t:\n'
            '        j = stack.pop()\n'
            '        answer[j] = i - j\n'
            '    stack.append(i)\n'
            '```\n\n'
            '新温度 t 一来，就把栈顶那些「比 t 冷」的日子一次性结算掉——'
            '它们等的天数就是 `i - j`。结算完把自己压进栈，继续往后看。\n\n'
            '**为什么是 O(n) 而不是 O(n²)**？因为每个下标最多进栈一次、出栈一次，'
            'while 循环的总执行次数不超过 n。\n\n'
            '常见错误：栈里存温度值而不是下标（那样算不出天数）；'
            '以及用 `<=` 比较（温度相同时会被误结算成「更高」）。\n\n'
            '复杂度：时间 O(n)、空间 O(n)。'
        ),
        'expected_output': '[1, 1, 4, 2, 1, 1, 0, 0]\n[1, 1, 1, 0]\n[1, 1, 0]',
        'hints': ['栈里存下标，不要存温度值', 'while temperatures[stack[-1]] < t 弹出并写下 i - j'],
    },

    # ── 专题 106 链表 ──────────────────────────────────────
    {
        'id': 'alg-016',
        'track': 'algorithm',
        'chapter_id': 106,
        'chapter_title': '链表',
        'topic': '链表',
        'title': '链表入门：节点、长度与求和',
        'difficulty': 1,
        'tags': ['链表', '遍历', 'Node'],
        'statement': (
            '请**按下面的定义**写好节点类（属性名必须一致，后面的函数要用它）：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '然后实现两个函数：\n\n'
            '- `list_length(head)`：返回链表的节点个数（空链表返回 0）\n'
            '- `sum_list(head)`：返回链表中所有节点 `val` 的和（空链表返回 0）\n\n'
            '两个函数都要用 `while head is not None` 一个节点一个节点地走，'
            '不许先把链表转成列表。\n\n'
            '最后构造链表 `1 → 2 → 3` 打印两个函数的结果，再打印空链表 `None` 的结果。'
        ),
        'starter_code': 'class Node:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef list_length(head):\n    pass\n',
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
            "def sum_list(head):\n"
            "    total = 0\n"
            "    while head is not None:\n"
            "        total += head.val\n"
            "        head = head.next\n"
            "    return total\n"
            "\n"
            "chain = Node(1, Node(2, Node(3)))\n"
            "print(list_length(chain), sum_list(chain))\n"
            "print(list_length(None), sum_list(None))\n"
        ),
        'checks': [
            "assert Node(5).val == 5 and Node(5).next is None, 'Node 的 next 默认值应该是 None'",
            "assert Node(1, Node(2)).next.val == 2, 'Node(val, next) 要按这个顺序接收参数'",
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "assert list_length(None) == 0 and sum_list(None) == 0, '空链表（None）应返回 0'",
            "assert list_length(_build([7])) == 1 and sum_list(_build([7])) == 7, '单节点链表的长度是 1，和是 7'",
            "assert list_length(_build([1, 2, 3])) == 3 and sum_list(_build([1, 2, 3])) == 6, '1->2->3 的长度是 3、和是 6，实际 %r / %r' % (list_length(_build([1, 2, 3])), sum_list(_build([1, 2, 3])))",
            "assert sum_list(_build([-1, -2, 3])) == 0, '有负数也要正确求和（-1 + -2 + 3 = 0）'",
            "assert list_length(_build([5, 5, 5])) == 3 and sum_list(_build([5, 5, 5])) == 15, '重复的节点值不能漏算'",
            "assert list_length(_build(list(range(1000)))) == 1000 and sum_list(_build(list(range(1000)))) == 499500, '1000 个节点的链表要用循环遍历（0~999 的和是 499500）'",
        ],
        'explanation': (
            '链表和列表最大的差别是：**不能按下标访问**，只能顺着 `next` 一个一个走。'
            '所以链表题的标准姿势就是：\n\n'
            '```python\n'
            'while head is not None:\n'
            '    处理 head.val\n'
            '    head = head.next      # 指向下一个节点\n'
            '```\n\n'
            '注意 `head = head.next` 只是把**局部变量**指向下一个节点，'
            '并没有破坏链表本身——原链表的头还好好存在别的地方。'
            '如果后面还需要从头遍历，就要先把头保存到另一个变量里。\n\n'
            '`Node(1, Node(2, Node(3)))` 这种嵌套构造很常用：'
            '内层先建好，外层把内层当作 next，于是链条自然成形。\n\n'
            '常见错误：写 `while head.next is not None`，'
            '这样会漏掉最后一个节点（长度少 1、和少了尾巴上的值）。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': '3 6\n0 0',
        'hints': ['循环条件用 while head is not None，别写成 while head.next', '节点属性就是 val 和 next'],
    },
    {
        'id': 'alg-017',
        'track': 'algorithm',
        'chapter_id': 106,
        'chapter_title': '链表',
        'topic': '链表',
        'title': '反转链表（就地改指针）',
        'difficulty': 2,
        'tags': ['链表', '指针', '迭代'],
        'statement': (
            '沿用上一题的节点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `reverse_list(head)`：把链表**就地反转**（只改节点的 `next` 指针，'
            '不要新建节点、也不要把值拷到新链表里），返回**反转后的新头节点**；'
            '空链表返回 `None`。\n\n'
            '经典写法是三个指针：`prev`（已经反转好的部分）、`current`（正在处理的节点）、'
            '`nxt`（先保存下一个节点，免得链断掉之后找不到）。\n\n'
            '最后把 `1 → 2 → 3 → 4 → 5` 反转并打印每个节点的值，再打印反转空链表的结果。'
        ),
        'starter_code': 'def reverse_list(head):\n    prev = None\n    current = head\n    # 每一步：先存 next，再改 current.next 指向 prev，最后一起后移\n    pass\n',
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
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "def _to_list(head):\n    out = []\n    while head is not None:\n        out.append(head.val)\n        head = head.next\n    return out",
            "assert _to_list(reverse_list(_build([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1], '反转结果不对：%r' % (_to_list(reverse_list(_build([1, 2, 3, 4, 5]))),)",
            "assert _to_list(reverse_list(None)) == [], '空链表应返回 None（转成列表就是 []）'",
            "assert _to_list(reverse_list(_build([1]))) == [1], '单节点链表反转后还是它自己'",
            "assert _to_list(reverse_list(_build([1, 2]))) == [2, 1], '两个节点要交换过来'",
            "assert _to_list(reverse_list(_build([-1, 0, 0, 3]))) == [3, 0, 0, -1], '重复值与负数也要处理正确'",
            "_head = _build([1, 2, 3])\n_new = reverse_list(_head)\nassert _new.val == 3 and _new.next.next is _head and _head.next is None, '要求就地反转：新头应是原来的尾节点，原来的头变成新的尾节点（复用原来的节点对象）'",
            "assert _to_list(reverse_list(_build(list(range(50))))) == list(range(49, -1, -1)), '50 个节点的链表也要能反转'",
        ],
        'explanation': (
            '反转链表只要记住**三根指针的舞蹈**：\n\n'
            '```python\n'
            'while current is not None:\n'
            '    nxt = current.next      # 1. 先记住后面还有谁\n'
            '    current.next = prev     # 2. 把当前节点掉头指向前面\n'
            '    prev = current          # 3. prev 前进到当前\n'
            '    current = nxt           # 4. current 前进到下一个\n'
            'return prev\n'
            '```\n\n'
            '第 1 步**必须先做**：一旦执行了第 2 步，`current.next` 就被改掉了，'
            '再想往后走就找不到路了。这是本题最经典的错误——'
            '忘记保存 next，链表从中断成两截。\n\n'
            '循环结束时 `current` 是 None，`prev` 停在原来的最后一个节点上，'
            '所以返回的是 `prev` 而不是 `current` / `head`。\n\n'
            '为什么强调「就地」？因为新建一条链表要 O(n) 额外空间，'
            '而就地反转只用三个变量，空间 O(1)。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': '[5, 4, 3, 2, 1]\nNone',
        'hints': ['先把 current.next 存进 nxt，再改指针', '循环结束后返回 prev，它才是新头'],
    },
    {
        'id': 'alg-018',
        'track': 'algorithm',
        'chapter_id': 106,
        'chapter_title': '链表',
        'topic': '链表',
        'title': '判断链表是否有环（快慢指针）',
        'difficulty': 3,
        'tags': ['链表', '快慢指针', 'Floyd'],
        'statement': (
            '沿用节点类：\n\n'
            '```python\n'
            'class Node:\n'
            '    def __init__(self, val=0, next=None):\n'
            '        self.val = val\n'
            '        self.next = next\n'
            '```\n\n'
            '定义函数 `has_cycle(head)`：如果链表里存在**环**'
            '（某个节点的 `next` 指回了前面出现过的节点）就返回 `True`，否则返回 `False`；'
            '空链表返回 `False`。\n\n'
            '要求用**快慢指针（Floyd 判圈）**：慢指针每次走 1 步、快指针每次走 2 步，'
            '如果两者相遇就说明有环；快指针走到尽头（`None`）则无环。'
            '这样只用 O(1) 额外空间（不要用「走过就记进集合」的做法）。\n\n'
            '最后构造一个带环的链表和一个无环链表各验证一次并打印结果。'
        ),
        'starter_code': 'def has_cycle(head):\n    slow = head\n    fast = head\n    # fast 每次两步，slow 每次一步，相遇即有环\n    pass\n',
        'solution': (
            "class Node:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def has_cycle(head):\n"
            "    slow = head\n"
            "    fast = head\n"
            "    while fast is not None and fast.next is not None:\n"
            "        slow = slow.next\n"
            "        fast = fast.next.next\n"
            "        if slow is fast:\n"
            "            return True\n"
            "    return False\n"
            "\n"
            "a, b, c, d = Node(3), Node(2), Node(0), Node(-4)\n"
            "a.next, b.next, c.next, d.next = b, c, d, b\n"
            "print(has_cycle(a))\n"
            "\n"
            "e, f = Node(1), Node(2)\n"
            "e.next = f\n"
            "print(has_cycle(e))\n"
            "print(has_cycle(None))\n"
        ),
        'checks': [
            "def _build(values):\n    head = None\n    for v in reversed(values):\n        head = Node(v, head)\n    return head",
            "assert not has_cycle(None), '空链表没有环，应返回 False'",
            "assert not has_cycle(_build([1])), '只有 1 个节点且 next 为 None，应返回 False'",
            "assert not has_cycle(_build([1, 2, 3, 4])), '普通无环链表应返回 False'",
            "_a = _build([1, 2, 3, 4])\n_tail = _a.next.next.next\n_tail.next = _a.next\nassert has_cycle(_a) is True, '尾巴接回第二个节点构成环，应返回 True'",
            "_self = Node(9)\n_self.next = _self\nassert has_cycle(_self) is True, '节点指向自己也是环'",
            "_p = Node(1)\n_q = Node(2)\n_p.next = _q\n_q.next = _p\nassert has_cycle(_p) is True, '两个节点互指构成环'",
            "_head = _build(list(range(9)))\n_last = _head.next.next.next.next.next.next.next.next\nassert _last.next is None\n_last.next = _head\nassert has_cycle(_head) is True, '整条链首尾相接构成环，应返回 True'",
            "assert not has_cycle(_build(list(range(1000)))), '1000 个节点的无环链表应返回 False'",
        ],
        'explanation': (
            '快慢指针为什么一定能相遇？把链表看成一条跑道：'
            '快指针速度是慢指针的两倍，一旦进入环里，'
            '快指针每轮都会把和慢指针的距离**缩短 1**，所以早晚追平（不会跳过）。\n\n'
            '```python\n'
            'while fast is not None and fast.next is not None:\n'
            '    slow = slow.next\n'
            '    fast = fast.next.next\n'
            '    if slow is fast:\n'
            '        return True\n'
            'return False\n'
            '```\n\n'
            '循环条件必须**同时**判断 `fast` 和 `fast.next`：'
            '因为 `fast.next.next` 会让快指针一次跳两格，'
            '只判断 `fast is not None` 时，遇到长度为偶数的链表走到结尾会报 `AttributeError`。\n\n'
            '另一个常见错误是用 `slow.val == fast.val` 判断相遇：'
            '节点值可能重复（比如 `1→1→1`），那样会误判；'
            '判断「是不是同一个节点对象」要用 `is`。\n\n'
            '「走过就塞进集合」的写法也能判环，但要多花 O(n) 空间——'
            '快慢指针的卖点正是 O(1)。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': 'True\nFalse\nFalse',
        'hints': ['快指针每次走两步，慢指针每次走一步，相遇即有环', '循环条件要同时写 fast is not None and fast.next is not None'],
    },

    # ── 专题 107 递归与分治 ────────────────────────────────
    {
        'id': 'alg-019',
        'track': 'algorithm',
        'chapter_id': 107,
        'chapter_title': '递归与分治',
        'topic': '递归与分治',
        'title': '汉诺塔：递归把大事化小',
        'difficulty': 2,
        'tags': ['递归', '分治', '经典题'],
        'statement': (
            '定义函数 `hanoi(n, start="A", target="C", helper="B")`，'
            '返回把所有盘子从 start 柱搬到 target 柱的**步骤列表**。\n\n'
            '规则：\n\n'
            '- 盘子用数字 `1..n` 表示，1 号最小\n'
            '- 每一步是一个元组 `(盘子编号, 从哪根柱, 到哪根柱)`，例如 `(1, "A", "C")`\n'
            '- 每次只能搬一个盘，且**大盘不能压在小盘上**\n'
            '- `n = 0` 时返回空列表 `[]`\n\n'
            '要求用**递归**实现，思路是：\n\n'
            '1. 先把上面 `n-1` 个盘从 start 搬到 helper（借助 target）\n'
            '2. 把最大的第 n 号盘从 start 搬到 target\n'
            '3. 再把那 `n-1` 个盘从 helper 搬到 target（借助 start）\n\n'
            '最后打印 `hanoi(3)` 的每一步和 `hanoi(4)` 的步数。'
        ),
        'starter_code': "def hanoi(n, start='A', target='C', helper='B'):\n    # 递归三步：n-1 到 helper、最大盘到 target、n-1 到 target\n    pass\n",
        'solution': (
            "def hanoi(n, start='A', target='C', helper='B'):\n"
            "    if n == 0:\n"
            "        return []\n"
            "    moves = hanoi(n - 1, start, helper, target)\n"
            "    moves.append((n, start, target))\n"
            "    moves.extend(hanoi(n - 1, helper, target, start))\n"
            "    return moves\n"
            "\n"
            "for step in hanoi(3):\n"
            "    print(step)\n"
            "print(len(hanoi(4)))\n"
            "print(hanoi(0))\n"
        ),
        'checks': [
            "assert hanoi(0) == [], 'n 为 0 时应返回空列表，实际 %r' % (hanoi(0),)",
            "assert hanoi(1) == [(1, 'A', 'C')], '1 个盘只需一步 (1, A, C)，实际 %r' % (hanoi(1),)",
            "assert len(hanoi(2)) == 3, '2 个盘需要 3 步，实际 %d 步' % len(hanoi(2))",
            "assert len(hanoi(3)) == 7, '3 个盘需要 2^3 - 1 = 7 步，实际 %d 步' % len(hanoi(3))",
            "assert len(hanoi(10)) == 1023, '10 个盘需要 2^10 - 1 = 1023 步，实际 %d 步' % len(hanoi(10))",
            "_moves = hanoi(3, 'X', 'Z', 'Y')\nassert len(_moves) == 7 and _moves[0] == (1, 'X', 'Z') and _moves[-1] == (1, 'X', 'Z'), '柱子名字要按参数走（start=X、target=Z），实际第一步 %r、最后一步 %r' % (_moves[0], _moves[-1])",
            "_pegs = {'A': list(range(4, 0, -1)), 'B': [], 'C': []}\nfor _disk, _from, _to in hanoi(4):\n    assert _pegs[_from] and _pegs[_from][-1] == _disk, '非法移动：%d 号盘并不在 %s 柱顶部，实际顶部是 %r' % (_disk, _from, _pegs[_from][-1:])\n    assert not _pegs[_to] or _pegs[_to][-1] > _disk, '非法移动：%d 号盘压到了更小的盘上（%s 柱顶部是 %r）' % (_disk, _to, _pegs[_to][-1:])\n    _pegs[_to].append(_pegs[_from].pop())\nassert _pegs['C'] == [4, 3, 2, 1] and _pegs['A'] == [] and _pegs['B'] == [], '4 个盘最终应全部按顺序落到 C 柱，实际 %r' % (_pegs,)",
        ],
        'explanation': (
            '汉诺塔是理解递归的最佳入口。别看盘子多，思路只有三句话：\n\n'
            '```python\n'
            'moves = hanoi(n - 1, start, helper, target)   # 上面 n-1 个先挪到 helper\n'
            'moves.append((n, start, target))              # 最大的直接搬过去\n'
            'moves.extend(hanoi(n - 1, helper, target, start))\n'
            '```\n\n'
            '写递归的关键是**相信递归**：不要试图在脑子里模拟 n=4 的每一步，'
            '只要保证「n-1 个盘能正确搬到另一根柱子上」这件事由递归自己去解决就行。\n\n'
            '**基准情况**是 `n == 0` 返回 `[]`——有了它，n=1 时才能正常工作'
            '（n-1 = 0 那次调用返回空列表，然后顺利 append 那一步）。\n\n'
            '用 `extend` 而不是 `append` 拼接第二个列表，'
            '否则会把整个列表当成一个元素塞进去，结果里出现嵌套列表。\n\n'
            '步数是 2ⁿ - 1：n=64 时约 1.8×10¹⁹ 步，'
            '按每秒一步算要 5800 亿年——所以递归只是「描述得简洁」，并不是「算得快」。'
        ),
        'expected_output': "(1, 'A', 'C')\n(2, 'A', 'B')\n(1, 'C', 'B')\n(3, 'A', 'C')\n(1, 'B', 'A')\n(2, 'B', 'C')\n(1, 'A', 'C')\n15\n[]",
        'hints': ['三步：n-1 到 helper、最大盘到 target、n-1 从 helper 到 target', '递归调用里参数顺序会「换位」，别把 start / target 搞混'],
    },
    {
        'id': 'alg-020',
        'track': 'algorithm',
        'chapter_id': 107,
        'chapter_title': '递归与分治',
        'topic': '递归与分治',
        'title': '快速幂（指数折半的分治）',
        'difficulty': 2,
        'tags': ['分治', '递归', '快速幂'],
        'statement': (
            '定义函数 `power(x, n)`：计算 x 的 n 次方，其中 n 是**非负整数**，x 可以是整数或浮点数。\n\n'
            '要求用**分治（指数折半）**实现：\n\n'
            '- `n == 0` 时返回 1（`power(0, 0)` 也返回 1）\n'
            '- 先递归算出 `half = power(x, n // 2)`\n'
            '- n 是偶数就返回 `half * half`，是奇数就返回 `half * half * x`\n\n'
            '这样递归深度只有 log₂n 层，时间复杂度 **O(log n)**。\n\n'
            '**不允许**使用 `**` 运算符，也不允许用 `pow()`。\n\n'
            '然后打印 `power(2, 10)`、`power(3, 0)`、`power(2.0, 3)` 的结果，'
            '以及 `len(str(power(2, 1000)))`（2 的 1000 次方有多少位）。'
        ),
        'starter_code': 'def power(x, n):\n    # n 为 0 返回 1；否则递归算一半，再按奇偶拼回来\n    pass\n',
        'solution': (
            "def power(x, n):\n"
            "    if n == 0:\n"
            "        return 1\n"
            "    half = power(x, n // 2)\n"
            "    if n % 2 == 0:\n"
            "        return half * half\n"
            "    return half * half * x\n"
            "\n"
            "print(power(2, 10))\n"
            "print(power(3, 0))\n"
            "print(power(2.0, 3))\n"
            "print(len(str(power(2, 1000))))\n"
        ),
        'checks': [
            "assert power(2, 10) == 1024, 'power(2, 10) 应为 1024，实际 %r' % (power(2, 10),)",
            "assert power(3, 0) == 1 and power(0, 0) == 1, '任何数的 0 次方都应该是 1'",
            "assert power(5, 1) == 5, 'power(5, 1) 应为 5'",
            "assert power(7, 2) == 49, 'power(7, 2) 应为 49'",
            "assert abs(power(2.0, 3) - 8.0) < 1e-9, '浮点数也要支持：2.0 的 3 次方是 8.0，实际 %r' % (power(2.0, 3),)",
            "assert abs(power(1.5, 4) - 5.0625) < 1e-9, '1.5 的 4 次方是 5.0625，实际 %r' % (power(1.5, 4),)",
            "assert power(2, 100) == 1267650600228229401496703205376, '2 的 100 次方算错了，实际 %r' % (power(2, 100),)",
            "assert power(7, 1000) % 10 == 1, '7 的 1000 次方末位应为 1（说明大指数也能算出来）'",
            "assert '**' not in _src and 'pow(' not in _src, '本题要求用分治递归实现快速幂，不能使用 ** 运算符或 pow()'",
        ],
        'explanation': (
            '朴素做法是把 x 连乘 n 次，O(n)。快速幂利用了一个简单事实：\n\n'
            '```\n'
            'x^n = (x^(n/2))^2          n 是偶数\n'
            'x^n = (x^((n-1)/2))^2 * x  n 是奇数\n'
            '```\n\n'
            '于是只需要算一次「一半」，就能拼出整个结果：\n\n'
            '```python\n'
            'half = power(x, n // 2)\n'
            'return half * half if n % 2 == 0 else half * half * x\n'
            '```\n\n'
            '**half 只算一次**很重要：写成 `power(x, n // 2) * power(x, n // 2)` '
            '就变成两倍的工作量，整个算法退化成 O(n)，而且还不容易看出错。\n\n'
            '为什么要 `n // 2` 而不是 `n / 2`？因为指数必须是整数，'
            'Python 里 `/` 会得到浮点数，接着就会变成浮点幂甚至溢出。\n\n'
            '常见错误：忘了处理 n == 0 的基准情况，递归永不停止；'
            '或者奇数分支忘了再乘一个 x。\n\n'
            '复杂度：时间 O(log n)、空间 O(log n)（递归栈深度）。'
        ),
        'expected_output': '1024\n1\n8.0\n302',
        'hints': ['先算 half = power(x, n // 2)，再根据奇偶拼回来', '基准情况 n == 0 返回 1，否则递归停不下来'],
    },
    {
        'id': 'alg-021',
        'track': 'algorithm',
        'chapter_id': 107,
        'chapter_title': '递归与分治',
        'topic': '递归与分治',
        'title': '统计逆序对（归并分治）',
        'difficulty': 3,
        'tags': ['分治', '归并', '逆序对'],
        'statement': (
            '定义函数 `count_inversions(nums)`：返回数组里**逆序对**的个数。\n\n'
            '逆序对指的是满足 `i < j` 且 `nums[i] > nums[j]` 的一对下标'
            '（必须是**严格大于**，相等的数不算）。\n\n'
            '- `[4, 3, 2, 1]` 有 6 对；`[2, 4, 1, 3, 5]` 有 3 对\n'
            '- 空数组和单元素数组都返回 0\n\n'
            '要求用**归并排序的分治思想**在 O(n log n) 内统计：'
            '递归排好左右两半（顺便统计各自的逆序对），'
            '再在**合并**时统计跨越两半的逆序对——'
            '只要右边某个元素先被取走，说明左边**剩下还没取的元素都比它大**，'
            '一次就能加上 `len(left) - i` 个。\n\n'
            '不要写双重循环（那是 O(n²)）。\n\n'
            '然后打印 `count_inversions([2, 4, 1, 3, 5])`、`count_inversions([5, 4, 3, 2, 1])`、'
            '`count_inversions([])` 的结果。'
        ),
        'starter_code': 'def count_inversions(nums):\n    # 归并时统计：右边元素先取走 => 左边剩下的都比它大\n    pass\n',
        'solution': (
            "def count_inversions(nums):\n"
            "    def merge_count(items):\n"
            "        if len(items) <= 1:\n"
            "            return items, 0\n"
            "        mid = len(items) // 2\n"
            "        left, left_count = merge_count(items[:mid])\n"
            "        right, right_count = merge_count(items[mid:])\n"
            "        merged = []\n"
            "        count = left_count + right_count\n"
            "        i = 0\n"
            "        j = 0\n"
            "        while i < len(left) and j < len(right):\n"
            "            if left[i] <= right[j]:\n"
            "                merged.append(left[i])\n"
            "                i += 1\n"
            "            else:\n"
            "                merged.append(right[j])\n"
            "                count += len(left) - i\n"
            "                j += 1\n"
            "        merged.extend(left[i:])\n"
            "        merged.extend(right[j:])\n"
            "        return merged, count\n"
            "\n"
            "    return merge_count(list(nums))[1]\n"
            "\n"
            "print(count_inversions([2, 4, 1, 3, 5]))\n"
            "print(count_inversions([5, 4, 3, 2, 1]))\n"
            "print(count_inversions([]))\n"
        ),
        'checks': [
            "assert count_inversions([]) == 0, '空数组应返回 0'",
            "assert count_inversions([1]) == 0, '单元素数组应返回 0'",
            "assert count_inversions([1, 2, 3, 4]) == 0, '升序数组没有逆序对'",
            "assert count_inversions([4, 3, 2, 1]) == 6, '严格降序的 4 个元素有 4*3/2 = 6 个逆序对，实际 %r' % (count_inversions([4, 3, 2, 1]),)",
            "assert count_inversions([2, 4, 1, 3, 5]) == 3, '[2, 4, 1, 3, 5] 的逆序对是 (2,1)、(4,1)、(4,3)，共 3 个，实际 %r' % (count_inversions([2, 4, 1, 3, 5]),)",
            "assert count_inversions([1, 1, 1]) == 0, '相等不算逆序对（必须是严格大于）'",
            "assert count_inversions([2, 1, 2, 1]) == 3, '[2, 1, 2, 1] 有 3 个逆序对，实际 %r' % (count_inversions([2, 1, 2, 1]),)",
            "assert count_inversions([2, 2, 1]) == 2, '[2, 2, 1] 里两个 2 都大于 1，共 2 个，实际 %r' % (count_inversions([2, 2, 1]),)",
            "_data = [3, 1, 2]\nassert count_inversions(_data) == 2, '[3, 1, 2] 的逆序对是 (3,1) 和 (3,2)，共 2 个，实际 %r' % (count_inversions(_data),)",
            "assert count_inversions(list(range(1000, 0, -1))) == 499500, '1000 个逆序元素的逆序对数是 1000*999/2 = 499500，实际 %r' % (count_inversions(list(range(1000, 0, -1))),)",
        ],
        'explanation': (
            '「数逆序对」和「归并排序」是天生一对，因为归并的**合并**步骤里藏着答案。\n\n'
            '合并两个**各自有序**的子数组时，一旦发现 `right[j] < left[i]`，'
            '就说明 `left[i]` 以及它后面的所有元素都比 `right[j]` 大——'
            '而它们在原数组里的下标都比 `right[j]` 小，所以这一次就能一次性加上'
            '`len(left) - i` 个逆序对，不用一个一个数。\n\n'
            '```python\n'
            'else:\n'
            '    merged.append(right[j])\n'
            '    count += len(left) - i     # 关键的一行\n'
            '    j += 1\n'
            '```\n\n'
            '注意用 `left[i] <= right[j]` 先取左边的等值元素，'
            '保证「相等不算逆序对」这条规则（写成 `<` 会把相等的也数进去）。\n\n'
            '递归的返回值是「（排好序的列表, 逆序对数）」这样一个二元组，'
            '排序和计数一次搞定——分成两趟做就浪费了一倍时间。\n\n'
            '复杂度：时间 O(n log n)、空间 O(n)。'
        ),
        'expected_output': '3\n10\n0',
        'hints': ['返回 (排好序的列表, 逆序对数) 这样的二元组，排序和计数一起做', '右边元素先被取走时，一次加 len(left) - i 个'],
    },

    # ── 专题 108 排序算法 ──────────────────────────────────
    {
        'id': 'alg-022',
        'track': 'algorithm',
        'chapter_id': 108,
        'chapter_title': '排序算法',
        'topic': '排序算法',
        'title': '冒泡排序（带提前退出）',
        'difficulty': 1,
        'tags': ['排序', '冒泡', '拷贝与原地'],
        'statement': (
            '定义函数 `bubble_sort(nums)`：用**冒泡排序**返回一个**升序的新列表**。\n\n'
            '规则：\n\n'
            '- **不要修改传入的原列表**（先 `result = list(nums)` 复制一份）\n'
            '- 双重循环：外层控制「已经排好几个」，内层两两比较，把大的往后换\n'
            '- 加一个优化：如果某一轮**一次交换都没发生**，说明已经有序，直接 `break`\n'
            '- 重复元素要保留，空列表返回 `[]`\n\n'
            '**不允许**使用 `sorted()` 或 `.sort()`。\n\n'
            '然后打印 `bubble_sort([5, 2, 9, 1, 5, 6])`、原列表（应该是原样）、`bubble_sort([])` 的结果。'
        ),
        'starter_code': 'def bubble_sort(nums):\n    result = list(nums)\n    n = len(result)\n    # 双重循环 + swapped 标记\n    pass\n',
        'solution': (
            "def bubble_sort(nums):\n"
            "    result = list(nums)\n"
            "    n = len(result)\n"
            "    for i in range(n - 1):\n"
            "        swapped = False\n"
            "        for j in range(n - 1 - i):\n"
            "            if result[j] > result[j + 1]:\n"
            "                result[j], result[j + 1] = result[j + 1], result[j]\n"
            "                swapped = True\n"
            "        if not swapped:\n"
            "            break\n"
            "    return result\n"
            "\n"
            "data = [5, 2, 9, 1, 5, 6]\n"
            "print(bubble_sort(data))\n"
            "print(data)\n"
            "print(bubble_sort([]))\n"
        ),
        'checks': [
            "assert bubble_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9], '排序结果不对：%r' % (bubble_sort([5, 2, 9, 1, 5, 6]),)",
            "assert bubble_sort([]) == [], '空列表应返回 []'",
            "assert bubble_sort([1]) == [1], '单元素列表应原样返回'",
            "assert bubble_sort([2, 1]) == [1, 2], '两个元素要交换过来'",
            "assert bubble_sort([3, 2, 2, 1]) == [1, 2, 2, 3], '重复元素也要排对，实际 %r' % (bubble_sort([3, 2, 2, 1]),)",
            "_data = [4, 3, 2]\nbubble_sort(_data)\nassert _data == [4, 3, 2], '不能修改传入的原列表（先 list(nums) 复制一份），实际 %r' % (_data,)",
            "assert bubble_sort([-5, 0, -1]) == [-5, -1, 0], '负数也要能排'",
            "assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], '已经有序的列表应原样返回'",
            "assert bubble_sort(list(range(50, 0, -1))) == list(range(1, 51)), '50 个逆序元素要排成 1~50'",
            "assert 'sorted(' not in _src and '.sort(' not in _src, '本题要求自己实现冒泡排序，不能调用内置排序'",
        ],
        'explanation': (
            '冒泡排序的画面感很强：每一轮让「最大的那个」像气泡一样浮到右端。\n\n'
            '```python\n'
            'for i in range(n - 1):\n'
            '    swapped = False\n'
            '    for j in range(n - 1 - i):\n'
            '        if result[j] > result[j + 1]:\n'
            '            result[j], result[j + 1] = result[j + 1], result[j]\n'
            '            swapped = True\n'
            '    if not swapped:\n'
            '        break\n'
            '```\n\n'
            '内层边界是 `n - 1 - i`：每走完一轮，末尾就有 i 个元素已经就位，不用再比了。'
            '写成 `n - 1` 结果也对，但白跑了很多次。\n\n'
            '`swapped` 这个标记是很有价值的优化：'
            '如果某一轮一次都没换，说明整个列表已经有序，直接收工。'
            '对「本来就基本有序」的数据，这让冒泡从 O(n²) 变成 O(n)。\n\n'
            '为什么要求返回**新列表**？因为调用方常常还想留着原顺序做对比。'
            '把「复制」和「排序」分成两步，是函数式风格的常见约定。\n\n'
            '复杂度：时间 O(n²)（最好 O(n)）、空间 O(n)（因为复制了一份）。'
        ),
        'expected_output': '[1, 2, 5, 5, 6, 9]\n[5, 2, 9, 1, 5, 6]\n[]',
        'hints': ['先 result = list(nums) 复制，别在原列表上排', '内层范围是 range(n - 1 - i)，末尾 i 个已经就位'],
    },
    {
        'id': 'alg-023',
        'track': 'algorithm',
        'chapter_id': 108,
        'chapter_title': '排序算法',
        'topic': '排序算法',
        'title': '插入排序（原地移位）',
        'difficulty': 2,
        'tags': ['排序', '插入', '原地'],
        'statement': (
            '定义函数 `insertion_sort(nums)`：用**插入排序**把传入的列表**原地**排成升序，'
            '并返回**这个列表本身**（`return nums`，不要新建列表）。\n\n'
            '做法：从左到右把每个元素当作 `key`，'
            '在它左边（已经有序的部分）从右往左找位置——'
            '比 key 大的元素统统**右移一格**，找到位置后把 key 放进去：\n\n'
            '```python\n'
            'key = nums[i]\n'
            'while j >= 0 and nums[j] > key:\n'
            '    nums[j + 1] = nums[j]\n'
            '    j -= 1\n'
            'nums[j + 1] = key\n'
            '```\n\n'
            '**不允许**使用 `sorted()` 或 `.sort()`。\n\n'
            '然后对 `[5, 1, 4, 2, 8]` 调用并打印结果，再打印原列表（应该也已经有序）。'
        ),
        'starter_code': 'def insertion_sort(nums):\n    for i in range(1, len(nums)):\n        key = nums[i]\n        # 把左边比 key 大的依次右移，再把 key 放到空位\n        pass\n',
        'solution': (
            "def insertion_sort(nums):\n"
            "    for i in range(1, len(nums)):\n"
            "        key = nums[i]\n"
            "        j = i - 1\n"
            "        while j >= 0 and nums[j] > key:\n"
            "            nums[j + 1] = nums[j]\n"
            "            j -= 1\n"
            "        nums[j + 1] = key\n"
            "    return nums\n"
            "\n"
            "data = [5, 1, 4, 2, 8]\n"
            "print(insertion_sort(data))\n"
            "print(data)\n"
            "print(insertion_sort([]))\n"
        ),
        'checks': [
            "_d = [5, 1, 4, 2, 8]\n_r = insertion_sort(_d)\nassert _r == [1, 2, 4, 5, 8], '排序结果不对：%r' % (_r,)",
            "_d2 = [5, 1, 4, 2, 8]\ninsertion_sort(_d2)\nassert _d2 == [1, 2, 4, 5, 8], '要求原地排序：传入的列表本身也要变成有序的，实际 %r' % (_d2,)",
            "_d3 = [2, 1]\nassert insertion_sort(_d3) is _d3, '应返回传入的那个列表对象（return nums）'",
            "assert insertion_sort([]) == [], '空列表应返回 []'",
            "assert insertion_sort([1]) == [1], '单元素列表应原样返回'",
            "assert insertion_sort([7, 7, 7]) == [7, 7, 7], '全是相同元素也要能正常结束，实际 %r' % (insertion_sort([7, 7, 7]),)",
            "assert insertion_sort([-1, -5, 3, 0]) == [-5, -1, 0, 3], '负数也要能排，实际 %r' % (insertion_sort([-1, -5, 3, 0]),)",
            "assert insertion_sort([1, 2, 3, 4]) == [1, 2, 3, 4], '已经有序的列表应保持原样'",
            "assert insertion_sort(list(range(20, 0, -1))) == list(range(1, 21)), '20 个逆序元素要排成 1~20'",
            "assert 'sorted(' not in _src and '.sort(' not in _src, '本题要求自己实现插入排序，不能调用内置排序'",
        ],
        'explanation': (
            '插入排序模仿的是**整理扑克牌**的动作：左手已经是一把有序的牌，'
            '右手每摸一张，就往左找到合适的位置插进去。\n\n'
            '实现上有两种等价写法：一种是**交换**（发现左边更大就交换，一路挪过去），'
            '另一种是**移位**（先把 key 存起来，比它大的元素整体右移，最后把 key 放到空位）。'
            '本题要求的是后者，它比交换版少做一半赋值操作。\n\n'
            '```python\n'
            'while j >= 0 and nums[j] > key:\n'
            '    nums[j + 1] = nums[j]\n'
            '    j -= 1\n'
            'nums[j + 1] = key\n'
            '```\n\n'
            '注意循环结束后放 key 的位置是 `j + 1`：while 退出时 j 已经指向'
            '「第一个不大于 key 的元素」，所以空位在它右边一格。'
            '写成 `nums[j] = key` 会覆盖掉正确的元素。\n\n'
            '插入排序对**基本有序**的数据非常快（接近 O(n)），'
            '所以在真实工程里常被当作小数组的收尾排序（Python 的 Timsort 就是这么干的）。\n\n'
            '复杂度：时间 O(n²)（最好 O(n)）、空间 O(1)。'
        ),
        'expected_output': '[1, 2, 4, 5, 8]\n[1, 2, 4, 5, 8]\n[]',
        'hints': ['key = nums[i]，把左边比 key 大的都右移一格', '最后放 key 的位置是 j + 1'],
    },
    {
        'id': 'alg-024',
        'track': 'algorithm',
        'chapter_id': 108,
        'chapter_title': '排序算法',
        'topic': '排序算法',
        'title': '快速排序（Lomuto 分区 + 分治）',
        'difficulty': 3,
        'tags': ['排序', '快排', '分治'],
        'statement': (
            '实现两个函数：\n\n'
            '1. `partition(nums, low, high)`：**原地**分区。以 `nums[high]`（最后一个元素）为**枢轴**，'
            '把 ≤ 枢轴的元素都换到左边、> 枢轴的换到右边，'
            '返回**枢轴最终所在的下标**（Lomuto 分区：用 i 记录「≤ 枢轴区」的末尾）。\n\n'
            '2. `quick_sort(nums)`：返回**升序的新列表**（不要修改传入的列表），'
            '内部用递归分治：对 `[low, high]` 区间做 `partition`，'
            '再分别递归排左右两半，区间长度 ≤ 1 时就返回。\n\n'
            '**不允许**使用 `sorted()` 或 `.sort()`。\n\n'
            '然后打印对 `[3, 1, 4, 1, 5, 9, 2, 6]` 调用 `partition(..., 0, 7)` 的返回值、'
            '`quick_sort` 的结果、原列表（应保持原样）和 `quick_sort([])` 的结果。'
        ),
        'starter_code': 'def partition(nums, low, high):\n    pivot = nums[high]\n    i = low - 1\n    # 遍历 low..high-1，把 <= pivot 的换到左半\n    pass\n\ndef quick_sort(nums):\n    pass\n',
        'solution': (
            "def partition(nums, low, high):\n"
            "    pivot = nums[high]\n"
            "    i = low - 1\n"
            "    for j in range(low, high):\n"
            "        if nums[j] <= pivot:\n"
            "            i += 1\n"
            "            nums[i], nums[j] = nums[j], nums[i]\n"
            "    nums[i + 1], nums[high] = nums[high], nums[i + 1]\n"
            "    return i + 1\n"
            "\n"
            "def quick_sort(nums):\n"
            "    def sort_range(items, low, high):\n"
            "        if low >= high:\n"
            "            return\n"
            "        p = partition(items, low, high)\n"
            "        sort_range(items, low, p - 1)\n"
            "        sort_range(items, p + 1, high)\n"
            "\n"
            "    items = list(nums)\n"
            "    sort_range(items, 0, len(items) - 1)\n"
            "    return items\n"
            "\n"
            "data = [3, 1, 4, 1, 5, 9, 2, 6]\n"
            "print(partition([3, 1, 4, 1, 5, 9, 2, 6], 0, 7))\n"
            "print(quick_sort(data))\n"
            "print(data)\n"
            "print(quick_sort([]))\n"
        ),
        'checks': [
            "_arr = [3, 1, 4, 1, 5, 9, 2, 6]\n_p = partition(_arr, 0, len(_arr) - 1)\nassert _arr[_p] == 6, '以最后一个元素 6 为枢轴分区后，枢轴应该落在下标 %r 上，实际数组 %r' % (_p, _arr)",
            "_arr2 = [3, 1, 4, 1, 5, 9, 2, 6]\n_p2 = partition(_arr2, 0, len(_arr2) - 1)\nassert all(x <= 6 for x in _arr2[:_p2]) and all(x >= 6 for x in _arr2[_p2 + 1:]), '分区后左半必须都 <= 6、右半必须都 >= 6，实际 %r' % (_arr2,)",
            "_arr3 = [2, 8, 7, 1, 3, 5, 6, 4]\n_p3 = partition(_arr3, 0, len(_arr3) - 1)\nassert _arr3[_p3] == 4 and all(x <= 4 for x in _arr3[:_p3]) and all(x >= 4 for x in _arr3[_p3 + 1:]), '以 4 为枢轴的分区结果不对，实际 %r' % (_arr3,)",
            "assert partition([3], 0, 0) == 0, '只有一个元素时分区后枢轴下标就是 0'",
            "_arr4 = [5, 1]\n_p4 = partition(_arr4, 0, 1)\nassert _arr4 == [1, 5] and _arr4[_p4] == 1, '[5, 1] 以末尾的 1 为枢轴，分区后应变成 [1, 5] 且枢轴下标是 0，实际 %r / %r' % (_arr4, _p4)",
            "assert quick_sort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9], '快速排序结果不对：%r' % (quick_sort([3, 1, 4, 1, 5, 9, 2, 6]),)",
            "assert quick_sort([]) == [] and quick_sort([1]) == [1], '空列表和单元素列表要处理好'",
            "_data = [5, 3, 1]\nquick_sort(_data)\nassert _data == [5, 3, 1], 'quick_sort 不应该修改传入的列表（先 list(nums) 复制一份），实际 %r' % (_data,)",
            "assert quick_sort([2, 2, 1]) == [1, 2, 2], '重复元素也要排对，实际 %r' % (quick_sort([2, 2, 1]),)",
            "assert quick_sort([5, 5, 5, 5]) == [5, 5, 5, 5], '全是相同元素时不能死循环或递归过深'",
            "assert quick_sort(list(range(100, 0, -1))) == list(range(1, 101)), '100 个逆序元素（最坏情况）也要排对'",
            "assert 'sorted(' not in _src and '.sort(' not in _src, '本题要求自己实现快速排序，不能调用内置排序'",
        ],
        'explanation': (
            '快速排序 = **分区（partition）+ 递归**。分区一次就干成一件大事：'
            '把枢轴放到它最终的位置上，并且让左边都不大于它、右边都不小于它。'
            '之后左右两半各自递归，不用再互相比较。\n\n'
            'Lomuto 分区的写法：\n\n'
            '```python\n'
            'pivot = nums[high]\n'
            'i = low - 1                       # i 指向「<= 枢轴区」的最后一个位置\n'
            'for j in range(low, high):\n'
            '    if nums[j] <= pivot:\n'
            '        i += 1\n'
            '        nums[i], nums[j] = nums[j], nums[i]\n'
            'nums[i + 1], nums[high] = nums[high], nums[i + 1]   # 枢轴归位\n'
            'return i + 1\n'
            '```\n\n'
            '最后那次交换是把枢轴从末尾换到「分界点」上，别忘了。\n\n'
            '递归的**基准情况**是 `low >= high`（区间里 0 个或 1 个元素），'
            '漏了它会无限递归。全是相同元素时也不会死循环：'
            'Lomuto 每次都把枢轴放到末尾，区间一定会缩小。\n\n'
            '如果每次都拿最后一个元素当枢轴，遇到**已经有序**的数组会退化成 O(n²)；'
            '工程实现里通常随机选枢轴或三数取中。\n\n'
            '复杂度：平均 O(n log n)、最坏 O(n²)、空间 O(log n)（递归栈）。'
        ),
        'expected_output': '6\n[1, 1, 2, 3, 4, 5, 6, 9]\n[3, 1, 4, 1, 5, 9, 2, 6]\n[]',
        'hints': ['i 从 low - 1 开始，遇到 <= pivot 就 i += 1 并交换', '最后别忘了把 nums[high] 换到 i + 1 的位置'],
    },

    # ── 专题 109 二分查找 ──────────────────────────────────
    {
        'id': 'alg-025',
        'track': 'algorithm',
        'chapter_id': 109,
        'chapter_title': '二分查找',
        'topic': '二分查找',
        'title': '二分查找（基础版）',
        'difficulty': 1,
        'tags': ['二分查找', 'O(log n)', '边界'],
        'statement': (
            '定义函数 `binary_search(nums, target)`：在**升序**列表 `nums` 中查找 `target`。\n\n'
            '- 找到就返回它的下标；找不到返回 `-1`\n'
            '- 题目保证元素**互不相同**\n'
            '- 空列表返回 `-1`\n\n'
            '要求用**二分查找**做到 O(log n)：维护 `low`、`high` 两个边界，'
            '每次取中点 `mid = (low + high) // 2`，'
            '比目标小就让 `low = mid + 1`，比目标大就让 `high = mid - 1`，'
            '循环条件是 `while low <= high`。\n\n'
            '**不要**用 `nums.index(target)`（可能抛异常），也不要写 `for` 从头扫到尾。\n\n'
            '然后打印 `binary_search([-1, 0, 3, 5, 9, 12], 9)`、'
            '`binary_search([-1, 0, 3, 5, 9, 12], 2)`、`binary_search([], 5)` 的结果。'
        ),
        'starter_code': 'def binary_search(nums, target):\n    low = 0\n    high = len(nums) - 1\n    # while low <= high: 取中点比较，缩小区间\n    pass\n',
        'solution': (
            "def binary_search(nums, target):\n"
            "    low = 0\n"
            "    high = len(nums) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        if nums[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
            "\n"
            "print(binary_search([-1, 0, 3, 5, 9, 12], 9))\n"
            "print(binary_search([-1, 0, 3, 5, 9, 12], 2))\n"
            "print(binary_search([], 5))\n"
        ),
        'checks': [
            "assert binary_search([-1, 0, 3, 5, 9, 12], 9) == 4, '9 在下标 4，实际 %r' % (binary_search([-1, 0, 3, 5, 9, 12], 9),)",
            "assert binary_search([-1, 0, 3, 5, 9, 12], -1) == 0, '第一个元素要能查到，实际 %r' % (binary_search([-1, 0, 3, 5, 9, 12], -1),)",
            "assert binary_search([-1, 0, 3, 5, 9, 12], 12) == 5, '最后一个元素要能查到，实际 %r' % (binary_search([-1, 0, 3, 5, 9, 12], 12),)",
            "assert binary_search([-1, 0, 3, 5, 9, 12], 2) == -1, '不存在的 2 应返回 -1，实际 %r' % (binary_search([-1, 0, 3, 5, 9, 12], 2),)",
            "assert binary_search([-1, 0, 3, 5, 9, 12], -100) == -1, '比所有元素都小时应返回 -1'",
            "assert binary_search([-1, 0, 3, 5, 9, 12], 100) == -1, '比所有元素都大时应返回 -1'",
            "assert binary_search([], 5) == -1, '空列表应返回 -1'",
            "assert binary_search([7], 7) == 0 and binary_search([7], 8) == -1, '单元素列表：查到返回 0，查不到返回 -1'",
            "_big = list(range(0, 200000, 2))\nassert binary_search(_big, 199998) == 99999 and binary_search(_big, 199999) == -1, '10 万个元素的列表也要能查对（199998 在下标 99999）'",
        ],
        'explanation': (
            '二分查找的直觉来自查字典：不会从第一页翻起，而是翻到中间，'
            '看要查的字在前面还是后面，然后**丢掉一半**。\n\n'
            '```python\n'
            'while low <= high:\n'
            '    mid = (low + high) // 2\n'
            '    if nums[mid] == target:\n'
            '        return mid\n'
            '    if nums[mid] < target:\n'
            '        low = mid + 1      # 答案在右半边\n'
            '    else:\n'
            '        high = mid - 1     # 答案在左半边\n'
            'return -1\n'
            '```\n\n'
            '三个必须写对的细节：\n\n'
            '1. 循环条件 `low <= high` 而不是 `<`，否则「只剩一个元素」时会漏查；\n'
            '2. 更新边界用 `mid + 1` / `mid - 1` 而不是 `mid`，否则区间不缩小、变成死循环；\n'
            '3. `mid` 用 `//` 整除，Python 里 `/` 得到浮点数，不能当下标用。\n\n'
            '为什么必须有序？因为「丢掉一半」的依据就是「中间值比目标小 ⇒ 左半边全比目标小」。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '4\n-1\n-1',
        'hints': ['while low <= high，边界更新要 +1 / -1，区间才会缩小', '先判断 nums[mid] == target，再决定往哪边走'],
    },
    {
        'id': 'alg-026',
        'track': 'algorithm',
        'chapter_id': 109,
        'chapter_title': '二分查找',
        'topic': '二分查找',
        'title': '二分变体：找第一个大于等于 target 的位置',
        'difficulty': 2,
        'tags': ['二分查找', '左边界', '边界处理'],
        'statement': (
            '定义函数 `lower_bound(nums, target)`：在**非递减**（允许有重复元素）的列表里，'
            '返回**第一个大于等于 target 的元素的下标**。\n\n'
            '- `lower_bound([1, 2, 2, 2, 3], 2)` → `1`（第一个 2 在下标 1）\n'
            '- `lower_bound([1, 2, 2, 2, 3], 4)` → `5`（所有元素都小于 4，返回 `len(nums)`）\n'
            '- 空列表返回 `0`\n\n'
            '要求 O(log n)，写法上有一点和普通二分不同：\n\n'
            '- `high` 取 `len(nums)`（不是 `len(nums) - 1`），循环条件用 `while low < high`\n'
            '- `nums[mid] < target` 时 `low = mid + 1`；**否则 `high = mid`**（不排除 mid，因为 mid 可能就是答案）\n'
            '- 最后返回 `low`\n\n'
            '不要用 `for` 循环扫（那是 O(n)）。\n\n'
            '然后打印 `lower_bound([1, 2, 2, 2, 3], 2)`、`lower_bound([1, 2, 2, 2, 3], 4)`、'
            '`lower_bound([], 5)` 的结果。'
        ),
        'starter_code': 'def lower_bound(nums, target):\n    low = 0\n    high = len(nums)\n    # while low < high: mid 偏左，收缩时 high = mid\n    pass\n',
        'solution': (
            "def lower_bound(nums, target):\n"
            "    low = 0\n"
            "    high = len(nums)\n"
            "    while low < high:\n"
            "        mid = (low + high) // 2\n"
            "        if nums[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid\n"
            "    return low\n"
            "\n"
            "print(lower_bound([1, 2, 2, 2, 3], 2))\n"
            "print(lower_bound([1, 2, 2, 2, 3], 4))\n"
            "print(lower_bound([], 5))\n"
        ),
        'checks': [
            "assert lower_bound([1, 2, 2, 2, 3], 2) == 1, '重复元素要找第一个，答案是 1，实际 %r' % (lower_bound([1, 2, 2, 2, 3], 2),)",
            "assert lower_bound([1, 2, 2, 2, 3], 4) == 5, '所有元素都小于 4 时应返回 len(nums) = 5，实际 %r' % (lower_bound([1, 2, 2, 2, 3], 4),)",
            "assert lower_bound([], 5) == 0, '空列表应返回 0，实际 %r' % (lower_bound([], 5),)",
            "assert lower_bound([1, 2, 2, 2, 3], 0) == 0, 'target 比所有元素都小时返回 0'",
            "assert lower_bound([1, 2, 2, 2, 3], 3) == 4, '找 3 应返回它自己的下标 4，实际 %r' % (lower_bound([1, 2, 2, 2, 3], 3),)",
            "assert lower_bound([5], 5) == 0 and lower_bound([5], 6) == 1, '单元素列表的两种情况'",
            "assert lower_bound([1, 1, 1], 1) == 0 and lower_bound([1, 1, 1], 2) == 3, '全是相同元素时也要正确，实际 %r / %r' % (lower_bound([1, 1, 1], 1), lower_bound([1, 1, 1], 2))",
            "_even = list(range(0, 1000, 2))\nassert lower_bound(_even, 500) == 250 and lower_bound(_even, 501) == 251, '偶数序列里 500 在下标 250、501 的下一个位置是 251，实际 %r / %r' % (lower_bound(_even, 500), lower_bound(_even, 501))",
        ],
        'explanation': (
            '普通二分是「找到就返回」，而**找边界**的二分要改成「记录候选、继续收缩」。\n\n'
            '```python\n'
            'low = 0\n'
            'high = len(nums)          # 注意：high 是「越界」的合法答案\n'
            'while low < high:         # 注意：< 而不是 <=\n'
            '    mid = (low + high) // 2\n'
            '    if nums[mid] < target:\n'
            '        low = mid + 1\n'
            '    else:\n'
            '        high = mid        # mid 可能就是答案，不能跳过\n'
            'return low\n'
            '```\n\n'
            '为什么 `high` 初始取 `len(nums)`？因为「所有元素都小于 target」时答案就是'
            '`len(nums)`，把它当成一个合法的「哨兵位置」会让代码少很多特判。\n\n'
            '为什么 `nums[mid] >= target` 时是 `high = mid` 而不是 `mid - 1`？'
            '因为 mid 本身可能就是第一个满足条件的位置，丢掉它就错了。\n\n'
            '常见错误：把 `nums[mid] <= target` 写成 `<`，'
            '结果找的是「第一个大于 target 的位置」；循环条件写成 `low <= high` 会死循环。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '1\n5\n0',
        'hints': ['high 从 len(nums) 开始，循环 while low < high', 'nums[mid] >= target 时 high = mid（不要减 1）'],
    },
    {
        'id': 'alg-027',
        'track': 'algorithm',
        'chapter_id': 109,
        'chapter_title': '二分查找',
        'topic': '二分查找',
        'title': '搜索旋转排序数组',
        'difficulty': 3,
        'tags': ['二分查找', '旋转数组', 'O(log n)'],
        'statement': (
            '定义函数 `search_rotated(nums, target)`：`nums` 是一个**升序列表在某个位置旋转**'
            '之后的结果（例如 `[0, 1, 2, 4, 5, 6, 7]` 旋转后可能是 `[4, 5, 6, 7, 0, 1, 2]`），'
            '数组里的元素**互不相同**。找到 `target` 返回下标，找不到返回 `-1`，空列表返回 `-1`。\n\n'
            '要求保持 O(log n)：每次取 `mid` 之后，'
            '**先判断 `nums[low] <= nums[mid]` 是否成立——成立说明左半段是有序的**，'
            '再看 target 是否落在 `[nums[low], nums[mid])` 这个左半区间里，'
            '是就往左走、否就往右走；如果左半段无序，说明右半段一定有序，对称处理。\n\n'
            '不要先找旋转点再二分（那要写两遍二分），也不要线性扫描。\n\n'
            '然后打印 `search_rotated([4, 5, 6, 7, 0, 1, 2], 0)`、'
            '`search_rotated([4, 5, 6, 7, 0, 1, 2], 3)`、`search_rotated([1], 0)` 的结果。'
        ),
        'starter_code': 'def search_rotated(nums, target):\n    low = 0\n    high = len(nums) - 1\n    # 每次判断哪一半是有序的，再决定往哪边走\n    pass\n',
        'solution': (
            "def search_rotated(nums, target):\n"
            "    low = 0\n"
            "    high = len(nums) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        if nums[low] <= nums[mid]:\n"
            "            if nums[low] <= target < nums[mid]:\n"
            "                high = mid - 1\n"
            "            else:\n"
            "                low = mid + 1\n"
            "        else:\n"
            "            if nums[mid] < target <= nums[high]:\n"
            "                low = mid + 1\n"
            "            else:\n"
            "                high = mid - 1\n"
            "    return -1\n"
            "\n"
            "print(search_rotated([4, 5, 6, 7, 0, 1, 2], 0))\n"
            "print(search_rotated([4, 5, 6, 7, 0, 1, 2], 3))\n"
            "print(search_rotated([1], 0))\n"
        ),
        'checks': [
            "assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4, '旋转数组里 0 在下标 4，实际 %r' % (search_rotated([4, 5, 6, 7, 0, 1, 2], 0),)",
            "assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1, '不存在的 3 应返回 -1，实际 %r' % (search_rotated([4, 5, 6, 7, 0, 1, 2], 3),)",
            "assert search_rotated([4, 5, 6, 7, 0, 1, 2], 4) == 0, '第一个元素要能查到'",
            "assert search_rotated([4, 5, 6, 7, 0, 1, 2], 2) == 6, '最后一个元素要能查到'",
            "assert search_rotated([4, 5, 6, 7, 0, 1, 2], 7) == 3, '旋转点左边的元素也要能查到'",
            "assert search_rotated([], 5) == -1, '空列表应返回 -1'",
            "assert search_rotated([1], 1) == 0 and search_rotated([1], 0) == -1, '单元素列表的两种情况'",
            "assert search_rotated([1, 2, 3, 4, 5], 3) == 2, '没有旋转的有序数组也要能查'",
            "assert search_rotated([3, 1], 1) == 1 and search_rotated([3, 1], 3) == 0, '两个元素的旋转数组，实际 %r / %r' % (search_rotated([3, 1], 1), search_rotated([3, 1], 3))",
            "assert search_rotated([5, 1, 3], 3) == 2, '[5, 1, 3] 里 3 在下标 2，实际 %r' % (search_rotated([5, 1, 3], 3),)",
            "assert search_rotated([6, 7, 8, 1, 2, 3, 4, 5], 5) == 7 and search_rotated([6, 7, 8, 1, 2, 3, 4, 5], 6) == 0, '元素多一点的旋转数组'",
        ],
        'explanation': (
            '旋转之后数组整体不再有序，但有一个关键性质：'
            '**任意时刻，`[low, mid]` 和 `[mid, high]` 里至少有一半是有序的**。\n\n'
            '```python\n'
            'if nums[low] <= nums[mid]:          # 左半有序\n'
            '    if nums[low] <= target < nums[mid]:\n'
            '        high = mid - 1              # 目标在左半的有序区间里\n'
            '    else:\n'
            '        low = mid + 1\n'
            'else:                               # 右半一定有序\n'
            '    if nums[mid] < target <= nums[high]:\n'
            '        low = mid + 1\n'
            '    else:\n'
            '        high = mid - 1\n'
            '```\n\n'
            '判据 `nums[low] <= nums[mid]` 之所以成立，是因为'
            '「旋转」只会在数组里制造一个「断崖」：'
            '如果 `low` 到 `mid` 没跨过断崖，那这一段就是升序的。\n\n'
            '常见错误：把区间判断写成闭区间 `nums[low] <= target <= nums[mid]`，'
            '这会在 `target == nums[mid]` 时重复判断（虽然结果不错，但逻辑不干净）；'
            '以及忘了 `mid` 已经排除，边界要用 `mid ± 1`。\n\n'
            '复杂度：时间 O(log n)、空间 O(1)。'
        ),
        'expected_output': '4\n-1\n-1',
        'hints': ['先判断 nums[low] <= nums[mid] 确定哪一半有序', '目标落在有序的那一半里就往那边走，否则走另一半'],
    },

    # ── 专题 110 树与二叉树 ────────────────────────────────
    {
        'id': 'alg-028',
        'track': 'algorithm',
        'chapter_id': 110,
        'chapter_title': '树与二叉树',
        'topic': '树与二叉树',
        'title': '二叉树的中序与层序遍历',
        'difficulty': 2,
        'tags': ['二叉树', '遍历', '队列'],
        'statement': (
            '请**按下面的定义**写好节点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '（测试时会用「层序数组」来构造树，数组里的 `None` 表示空位。）\n\n'
            '然后实现两个遍历函数，都返回**值组成的列表**：\n\n'
            '- `inorder(root)`：**中序**遍历，顺序是「左 → 根 → 右」，可以用递归\n'
            '- `level_order(root)`：**层序**遍历，从上到下、每层从左到右，返回**一维**列表，'
            '用一个列表当队列（`pop(0)` 取出队头，`append` 加入队尾）\n\n'
            '空树都返回 `[]`。\n\n'
            '最后构造 `4(2(1,3), 6(5,7))` 这棵树，打印两种遍历的结果和空树的结果。'
        ),
        'starter_code': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder(root):\n    pass\n\ndef level_order(root):\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def inorder(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    return inorder(root.left) + [root.val] + inorder(root.right)\n"
            "\n"
            "def level_order(root):\n"
            "    if root is None:\n"
            "        return []\n"
            "    result = []\n"
            "    queue = [root]\n"
            "    while queue:\n"
            "        node = queue.pop(0)\n"
            "        result.append(node.val)\n"
            "        if node.left is not None:\n"
            "            queue.append(node.left)\n"
            "        if node.right is not None:\n"
            "            queue.append(node.right)\n"
            "    return result\n"
            "\n"
            "root = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))\n"
            "print(inorder(root))\n"
            "print(level_order(root))\n"
            "print(inorder(None), level_order(None))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert inorder(None) == [] and level_order(None) == [], '空树应返回空列表'",
            "assert inorder(_tree([1])) == [1] and level_order(_tree([1])) == [1], '只有一个根节点时应返回 [1]'",
            "_root = _tree([4, 2, 6, 1, 3, 5, 7])\nassert inorder(_root) == [1, 2, 3, 4, 5, 6, 7], '中序遍历应是 [1, 2, 3, 4, 5, 6, 7]，实际 %r' % (inorder(_root),)",
            "assert level_order(_tree([4, 2, 6, 1, 3, 5, 7])) == [4, 2, 6, 1, 3, 5, 7], '层序遍历应是 [4, 2, 6, 1, 3, 5, 7]，实际 %r' % (level_order(_tree([4, 2, 6, 1, 3, 5, 7])),)",
            "assert inorder(_tree([1, None, 2, None, 3])) == [1, 2, 3], '只有右子树的「斜树」也要对，实际 %r' % (inorder(_tree([1, None, 2, None, 3])),)",
            "assert level_order(_tree([1, None, 2, None, 3])) == [1, 2, 3], '斜树的层序遍历同样是 [1, 2, 3]'",
            "assert inorder(_tree([3, 2, None, 1])) == [1, 2, 3], '一直往左的斜树中序是 [1, 2, 3]，实际 %r' % (inorder(_tree([3, 2, None, 1])),)",
            "assert level_order(_tree([3, 2, None, 1])) == [3, 2, 1], '一直往左的斜树层序是 [3, 2, 1]，实际 %r' % (level_order(_tree([3, 2, None, 1])),)",
            "_full = _tree(list(range(1, 16)))\nassert level_order(_full) == list(range(1, 16)), '满二叉树的层序就是数组顺序，实际 %r' % (level_order(_full),)",
            "assert inorder(_full) == [8, 4, 9, 2, 10, 5, 11, 1, 12, 6, 13, 3, 14, 7, 15], '满二叉树的中序不对：%r' % (inorder(_full),)",
            "assert inorder(_tree([2, 1, 3])) == [1, 2, 3], 'BST 的中序一定是从小到大'",
        ],
        'explanation': (
            '**中序**（左 → 根 → 右）用递归最自然：\n\n'
            '```python\n'
            'def inorder(root):\n'
            '    if root is None:\n'
            '        return []\n'
            '    return inorder(root.left) + [root.val] + inorder(root.right)\n'
            '```\n\n'
            '拼接的顺序就是访问顺序，读起来和定义一模一样。'
            '对二叉搜索树来说，中序遍历的结果一定是升序——这是最常用的性质。\n\n'
            '**层序**（一层一层、从左到右）要用**队列**：\n\n'
            '```python\n'
            'queue = [root]\n'
            'while queue:\n'
            '    node = queue.pop(0)      # 队头出队\n'
            '    result.append(node.val)\n'
            '    if node.left:  queue.append(node.left)\n'
            '    if node.right: queue.append(node.right)\n'
            '```\n\n'
            '队列的「先进先出」保证了上一层全部处理完，才会轮到下一层。'
            '用栈就会变成深度优先，输出顺序完全不同。\n\n'
            '复杂度：时间 O(n)（每次 `pop(0)` 是 O(n)，用 `collections.deque` 更标准）、空间 O(n)。'
        ),
        'expected_output': '[1, 2, 3, 4, 5, 6, 7]\n[4, 2, 6, 1, 3, 5, 7]\n[] []',
        'hints': ['中序用递归：左 + [根] + 右', '层序用队列：pop(0) 出队，左右孩子依次 append'],
    },
    {
        'id': 'alg-029',
        'track': 'algorithm',
        'chapter_id': 110,
        'chapter_title': '树与二叉树',
        'topic': '树与二叉树',
        'title': '二叉树的深度、节点数与叶子数',
        'difficulty': 2,
        'tags': ['二叉树', '递归', '深度'],
        'statement': (
            '沿用节点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '实现三个函数（都用**递归**，返回值是整数）：\n\n'
            '- `max_depth(root)`：最大深度，即「根到最远叶子的节点数」；空树为 0，只有根为 1\n'
            '- `count_nodes(root)`：节点总数；空树为 0\n'
            '- `count_leaves(root)`：**叶子节点**个数（既没有左孩子也没有右孩子的节点）；空树为 0\n\n'
            '提示：深度 = `1 + max(左边深度, 右边深度)`；'
            '节点数 = `1 + 左子树节点数 + 右子树节点数`。\n\n'
            '最后构造 `1(2(4), 3)` 这棵树，打印三个函数的结果，再打印空树的结果。'
        ),
        'starter_code': 'def max_depth(root):\n    pass\n\ndef count_nodes(root):\n    pass\n\ndef count_leaves(root):\n    pass\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def max_depth(root):\n"
            "    if root is None:\n"
            "        return 0\n"
            "    return 1 + max(max_depth(root.left), max_depth(root.right))\n"
            "\n"
            "def count_nodes(root):\n"
            "    if root is None:\n"
            "        return 0\n"
            "    return 1 + count_nodes(root.left) + count_nodes(root.right)\n"
            "\n"
            "def count_leaves(root):\n"
            "    if root is None:\n"
            "        return 0\n"
            "    if root.left is None and root.right is None:\n"
            "        return 1\n"
            "    return count_leaves(root.left) + count_leaves(root.right)\n"
            "\n"
            "root = TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))\n"
            "print(max_depth(root), count_nodes(root), count_leaves(root))\n"
            "print(max_depth(None), count_nodes(None), count_leaves(None))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert max_depth(None) == 0 and count_nodes(None) == 0 and count_leaves(None) == 0, '空树的深度、节点数、叶子数都是 0'",
            "_single = _tree([1])\nassert max_depth(_single) == 1 and count_nodes(_single) == 1 and count_leaves(_single) == 1, '只有一个根节点时三个答案都是 1'",
            "_t = _tree([3, 9, 20, None, None, 15, 7])\nassert max_depth(_t) == 3, '经典例子的深度是 3，实际 %r' % (max_depth(_t),)",
            "_t2 = _tree([3, 9, 20, None, None, 15, 7])\nassert count_nodes(_t2) == 5, '经典例子的节点数是 5，实际 %r' % (count_nodes(_t2),)",
            "_t3 = _tree([3, 9, 20, None, None, 15, 7])\nassert count_leaves(_t3) == 3, '叶子是 9、15、7 共 3 个，实际 %r' % (count_leaves(_t3),)",
            "_skew = _tree([1, 2, None, 3, None, 4])\nassert max_depth(_skew) == 4 and count_nodes(_skew) == 4 and count_leaves(_skew) == 1, '一直往左的斜树：深度 4、节点 4、叶子只有 1 个，实际 %r / %r / %r' % (max_depth(_skew), count_nodes(_skew), count_leaves(_skew))",
            "_right = _tree([1, None, 2, None, 3])\nassert max_depth(_right) == 3 and count_leaves(_right) == 1 and count_nodes(_right) == 3, '一直往右的斜树也要算对'",
            "_perfect = _tree(list(range(1, 16)))\nassert max_depth(_perfect) == 4 and count_nodes(_perfect) == 15 and count_leaves(_perfect) == 8, '4 层满二叉树：深度 4、节点 15、叶子 8，实际 %r / %r / %r' % (max_depth(_perfect), count_nodes(_perfect), count_leaves(_perfect))",
            "_node = None\nfor _v in range(300, 0, -1):\n    _node = TreeNode(_v, None, _node)\nassert max_depth(_node) == 300 and count_nodes(_node) == 300 and count_leaves(_node) == 1, '300 个节点的链状树：深度 300、叶子 1 个，实际 %r / %r / %r' % (max_depth(_node), count_nodes(_node), count_leaves(_node))",
        ],
        'explanation': (
            '树形结构的递归有一个统一的模板：\n\n'
            '```\n'
            '处理空树（基准情况） → 递归处理左右子树 → 把两个结果合并\n'
            '```\n\n'
            '三个问题只是「合并方式」不同：\n\n'
            '| 问题 | 空树返回 | 合并 |\n'
            '|---|---|---|\n'
            '| 深度 | 0 | `1 + max(左, 右)` |\n'
            '| 节点数 | 0 | `1 + 左 + 右` |\n'
            '| 叶子数 | 0 | 无孩子返回 1，否则 `左 + 右` |\n\n'
            '深度为什么用 `max`？因为一棵树的高度取决于**更深**的那一边。'
            '注意叶子数的定义：左右孩子都为 `None` 才算叶子——'
            '只有左孩子的节点**不算**叶子。\n\n'
            '常见错误：把 `count_leaves` 写成「左为空或右为空」，'
            '那样斜树里的每个节点都会被当成叶子，答案会偏大。\n\n'
            '复杂度：时间 O(n)、空间 O(h)（h 是树高，递归栈的深度）。'
        ),
        'expected_output': '3 4 2\n0 0 0',
        'hints': ['深度 = 1 + max(左深度, 右深度)', '叶子 = 左右孩子都为 None 的节点，只有一边为空不算叶子'],
    },
    {
        'id': 'alg-030',
        'track': 'algorithm',
        'chapter_id': 110,
        'chapter_title': '树与二叉树',
        'topic': '树与二叉树',
        'title': '验证二叉搜索树',
        'difficulty': 3,
        'tags': ['二叉树', 'BST', '上下界'],
        'statement': (
            '沿用节点类：\n\n'
            '```python\n'
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '```\n\n'
            '定义函数 `is_valid_bst(root)`：判断一棵二叉树是否是**二叉搜索树**，返回 `True` / `False`。\n\n'
            '规则：对任意节点，**整棵左子树**的所有值都必须**严格小于**它，'
            '**整棵右子树**的所有值都必须**严格大于**它（相等的值不算 BST）。空树算有效。\n\n'
            '要求用「**从上往下传值域**」的做法：\n\n'
            '```python\n'
            'def check(node, low, high):\n'
            '    # node 的值必须满足 low < node.val < high\n'
            '    # 往左递归时上界变成 node.val，往右递归时下界变成 node.val\n'
            '```\n\n'
            '只比较「根和它的左右孩子」是**不够的**，那样会漏掉「孙子辈越界」的情况。\n\n'
            '最后打印一个合法 BST、一个经典的反例和空树的判断结果。'
        ),
        'starter_code': 'def is_valid_bst(root):\n    def check(node, low, high):\n        pass\n    return check(root, None, None)\n',
        'solution': (
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def is_valid_bst(root):\n"
            "    def check(node, low, high):\n"
            "        if node is None:\n"
            "            return True\n"
            "        if low is not None and node.val <= low:\n"
            "            return False\n"
            "        if high is not None and node.val >= high:\n"
            "            return False\n"
            "        return check(node.left, low, node.val) and check(node.right, node.val, high)\n"
            "\n"
            "    return check(root, None, None)\n"
            "\n"
            "root = TreeNode(5, TreeNode(1), TreeNode(8, TreeNode(7), TreeNode(9)))\n"
            "print(is_valid_bst(root))\n"
            "print(is_valid_bst(TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))))\n"
            "print(is_valid_bst(None))\n"
        ),
        'checks': [
            "def _tree(values):\n    if not values or values[0] is None:\n        return None\n    root = TreeNode(values[0])\n    queue = [root]\n    index = 1\n    while queue and index < len(values):\n        node = queue.pop(0)\n        if index < len(values) and values[index] is not None:\n            node.left = TreeNode(values[index])\n            queue.append(node.left)\n        index += 1\n        if index < len(values) and values[index] is not None:\n            node.right = TreeNode(values[index])\n            queue.append(node.right)\n        index += 1\n    return root",
            "assert is_valid_bst(None) is True, '空树算有效的 BST'",
            "assert is_valid_bst(_tree([1])) is True, '只有一个节点是 BST'",
            "assert is_valid_bst(_tree([5, 1, 8, None, None, 7, 9])) is True, '标准 BST 应返回 True，实际 %r' % (is_valid_bst(_tree([5, 1, 8, None, None, 7, 9])),)",
            "assert is_valid_bst(_tree([2, 1, 3])) is True, '小 BST 应返回 True'",
            "assert is_valid_bst(_tree([3, 2, None, 1])) is True, '一直往左降的斜树也是 BST'",
            "assert is_valid_bst(_tree([2, 1, 3, None, None, None, 4])) is True, '2,1,3,4 也是合法 BST'",
            "assert is_valid_bst(_tree([5, 1, 4, None, None, 3, 6])) is False, '经典反例：3 在 5 的右子树里却比 5 小，应返回 False'",
            "assert is_valid_bst(_tree([5, 4, 6, None, None, 3, 7])) is False, '3 在 5 的右子树里，应返回 False'",
            "assert is_valid_bst(_tree([1, 1])) is False, '有相等的值不算严格 BST'",
            "assert is_valid_bst(_tree([10, 5, 15, None, None, 6, 20])) is False, '6 落在 10 的右子树里，应返回 False'",
            "assert is_valid_bst(_tree([5, 3, 7, 2, 4, 6, 8])) is True, '完整的 BST 应返回 True'",
        ],
        'explanation': (
            '最容易写错的版本是「只比较父子」：\n\n'
            '```python\n'
            'def wrong(node):            # 错的！\n'
            '    if node.left and node.left.val >= node.val: return False\n'
            '    if node.right and node.right.val <= node.val: return False\n'
            '```\n\n'
            '看这棵树：`5(1, 4(3, 6))`——每个父子关系看起来都合法（3 < 4 < 6），'
            '但 3 和 6 都在 5 的右子树里，却比 5 小，所以它**不是** BST。\n\n'
            '正确做法是**把允许的区间一路传下去**：\n\n'
            '```python\n'
            'def check(node, low, high):\n'
            '    if node is None:\n'
            '        return True\n'
            '    if (low is not None and node.val <= low) or (high is not None and node.val >= high):\n'
            '        return False\n'
            '    return check(node.left, low, node.val) and check(node.right, node.val, high)\n'
            '```\n\n'
            '一开始区间是「负无穷到正无穷」，用 `None` 表示无界，'
            '比写 `float("-inf")` 更省事（而且对超大整数也安全）。\n\n'
            '另一个等价思路是**中序遍历**：结果必须是严格递增的。\n\n'
            '复杂度：时间 O(n)、空间 O(h)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['往左递归时把上界收紧成当前值，往右递归时把下界收紧成当前值', '用 None 表示「没有边界」，判断前先检查 low/high 是否为 None'],
    },

    # ── 专题 111 堆与优先队列 ──────────────────────────────
    {
        'id': 'alg-031',
        'track': 'algorithm',
        'chapter_id': 111,
        'chapter_title': '堆与优先队列',
        'topic': '堆与优先队列',
        'title': 'Top-K：用堆求最大的 k 个数',
        'difficulty': 2,
        'tags': ['堆', 'heapq', 'Top-K'],
        'statement': (
            '定义函数 `top_k(nums, k)`：返回 `nums` 中**最大的 k 个元素**，'
            '按**从大到小**排列。\n\n'
            '- `k <= 0` 或 `nums` 为空时返回 `[]`\n'
            '- `k >= len(nums)` 时返回全部元素（降序）\n'
            '- 重复元素要保留：`[3, 2, 3, 1]` 取 2 个得到 `[3, 3]`\n\n'
            '要求使用 `heapq` 模块维护一个**大小为 k 的小顶堆**（整体 O(n log k)）：\n\n'
            '```python\n'
            'import heapq\n'
            'heap = []\n'
            '# 堆没满就 heappush；堆满了就比较 value 和 heap[0]（当前 k 个里最小的），\n'
            '# 比它大就 heapreplace 换掉它\n'
            '```\n\n'
            '最后返回时把堆排成降序（可以用 `sorted(heap, reverse=True)`）。\n\n'
            '然后打印 `top_k([3, 2, 1, 5, 6, 4], 2)`、`top_k([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)`、'
            '`top_k([], 3)`、`top_k([1, 2], 0)`、`top_k([1, 2], 5)` 的结果。'
        ),
        'starter_code': 'import heapq\n\ndef top_k(nums, k):\n    if k <= 0 or not nums:\n        return []\n    heap = []\n    pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "def top_k(nums, k):\n"
            "    if k <= 0 or not nums:\n"
            "        return []\n"
            "    heap = []\n"
            "    for value in nums:\n"
            "        if len(heap) < k:\n"
            "            heapq.heappush(heap, value)\n"
            "        elif value > heap[0]:\n"
            "            heapq.heapreplace(heap, value)\n"
            "    return sorted(heap, reverse=True)\n"
            "\n"
            "print(top_k([3, 2, 1, 5, 6, 4], 2))\n"
            "print(top_k([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))\n"
            "print(top_k([], 3), top_k([1, 2], 0), top_k([1, 2], 5))\n"
        ),
        'checks': [
            "assert top_k([3, 2, 1, 5, 6, 4], 2) == [6, 5], 'top_k([3, 2, 1, 5, 6, 4], 2) 应返回 [6, 5]，实际 %r' % (top_k([3, 2, 1, 5, 6, 4], 2),)",
            "assert top_k([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == [6, 5, 5, 4], '重复元素要保留，实际 %r' % (top_k([3, 2, 3, 1, 2, 4, 5, 5, 6], 4),)",
            "assert top_k([], 3) == [], '空列表应返回 []'",
            "assert top_k([1, 2], 0) == [] and top_k([1, 2], -1) == [], 'k <= 0 时应返回 []'",
            "assert top_k([1, 2], 5) == [2, 1], 'k 超过长度时返回全部元素（降序），实际 %r' % (top_k([1, 2], 5),)",
            "assert top_k([7], 1) == [7], '单元素列表取 1 个就是它自己'",
            "assert top_k([-3, -1, -2], 2) == [-1, -2], '全是负数时也要取「最大的」，实际 %r' % (top_k([-3, -1, -2], 2),)",
            "assert top_k([5, 5, 5], 2) == [5, 5], '全是相同的值也要取够 k 个'",
            "assert top_k([1, 2, 3, 4], 4) == [4, 3, 2, 1], 'k 等于长度时就是整体降序'",
            "assert top_k(list(range(1000)), 3) == [999, 998, 997], '1000 个元素的 Top-3 应是 [999, 998, 997]'",
            "assert 'heapq' in _src, '本题要求使用 heapq 模块维护大小为 k 的小顶堆'",
        ],
        'explanation': (
            '求 Top-K 的两种思路：\n\n'
            '1. 整体排序再取前 k 个：O(n log n)，还得把所有数据读进内存；\n'
            '2. **大小为 k 的小顶堆**：O(n log k)，额外空间只有 O(k)。\n\n'
            '```python\n'
            'for value in nums:\n'
            '    if len(heap) < k:\n'
            '        heapq.heappush(heap, value)\n'
            '    elif value > heap[0]:           # 比「k 个里最小的」还大\n'
            '        heapq.heapreplace(heap, value)   # 弹出堆顶，换进新值\n'
            '```\n\n'
            '为什么用**小顶堆**求**最大**的 k 个？因为小顶堆的堆顶正是'
            '「目前这 k 个里最小的那个」——它就是**淘汰线**，'
            '新元素比它大才有资格留下。这个反直觉的点是本题的核心。\n\n'
            '常见错误：用大顶堆（那样堆顶是最大的，根本不知道谁该被淘汰）；'
            '以及把 `heapreplace` 写成「先 pop 再 push」（两步容易出错，heapreplace 一步到位）。\n\n'
            '当 k 很小、n 很大（比如从 1 亿条日志里找最慢的 10 个请求）时，'
            '堆的优势非常明显。')
        ,
        'expected_output': '[6, 5]\n[6, 5, 5, 4]\n[] [] [2, 1]',
        'hints': ['堆没满就 heappush，满了只跟 heap[0] 比较', 'heap[0] 是堆里最小的，它就是淘汰线'],
    },
    {
        'id': 'alg-032',
        'track': 'algorithm',
        'chapter_id': 111,
        'chapter_title': '堆与优先队列',
        'topic': '堆与优先队列',
        'title': '数据流中的中位数（双堆）',
        'difficulty': 3,
        'tags': ['堆', 'heapq', '设计'],
        'statement': (
            '实现 `MedianFinder` 类，数据是**一个接一个到来**的，不能每次都重新排序：\n\n'
            '- `__init__(self)`：初始化\n'
            '- `add_num(self, num)`：加入一个数字\n'
            '- `find_median(self)`：返回当前所有数字的**中位数**并返回浮点数；\n'
            '  奇数个返回中间那个，偶数个返回中间两个的**平均值**；没有任何数字时返回 `0.0`\n\n'
            '要求用**两个堆**，让 `add_num` 是 O(log n)、`find_median` 是 O(1)：\n\n'
            '- `small`：保存较小的一半。Python 只有小顶堆，'
            '所以**把数字取负**存进去，这样堆顶就是这一半里最大的\n'
            '- `large`：保存较大的一半，小顶堆，堆顶是这一半里最小的\n'
            '- 加入后做两步维护：① 如果 `small` 的堆顶（取负还原）比 `large` 堆顶大，就换一下；'
            '② 保证两个堆的大小差不超过 1\n\n'
            '中位数就是：两堆相等时取两个堆顶的平均值，否则取 `small` 的堆顶。\n\n'
            '然后依次 add 1、2、3、4，每次打印 `find_median()`。'
        ),
        'starter_code': 'import heapq\n\nclass MedianFinder:\n    def __init__(self):\n        self.small = []   # 存负数，堆顶是这一半里最大的\n        self.large = []\n\n    def add_num(self, num):\n        pass\n\n    def find_median(self):\n        pass\n',
        'solution': (
            "import heapq\n"
            "\n"
            "class MedianFinder:\n"
            "    def __init__(self):\n"
            "        self.small = []\n"
            "        self.large = []\n"
            "\n"
            "    def add_num(self, num):\n"
            "        heapq.heappush(self.small, -num)\n"
            "        if self.large and -self.small[0] > self.large[0]:\n"
            "            heapq.heappush(self.large, -heapq.heappop(self.small))\n"
            "        if len(self.small) > len(self.large) + 1:\n"
            "            heapq.heappush(self.large, -heapq.heappop(self.small))\n"
            "        elif len(self.large) > len(self.small):\n"
            "            heapq.heappush(self.small, -heapq.heappop(self.large))\n"
            "\n"
            "    def find_median(self):\n"
            "        if not self.small and not self.large:\n"
            "            return 0.0\n"
            "        if len(self.small) > len(self.large):\n"
            "            return float(-self.small[0])\n"
            "        return (-self.small[0] + self.large[0]) / 2\n"
            "\n"
            "finder = MedianFinder()\n"
            "for value in (1, 2, 3, 4):\n"
            "    finder.add_num(value)\n"
            "    print(finder.find_median())\n"
            "print(MedianFinder().find_median())\n"
        ),
        'checks': [
            "_f = MedianFinder()\nassert _f.find_median() == 0.0, '还没有任何数字时应返回 0.0，实际 %r' % (_f.find_median(),)",
            "_f = MedianFinder()\n_f.add_num(1)\nassert _f.find_median() == 1.0, '只有一个数 1 时中位数是 1.0，实际 %r' % (_f.find_median(),)",
            "_f = MedianFinder()\n_f.add_num(1)\n_f.add_num(2)\nassert _f.find_median() == 1.5, '偶数个时取中间两个的平均：(1 + 2) / 2 = 1.5，实际 %r' % (_f.find_median(),)",
            "_f = MedianFinder()\nfor _v in (1, 2, 3):\n    _f.add_num(_v)\nassert _f.find_median() == 2.0, '1、2、3 的中位数是 2.0，实际 %r' % (_f.find_median(),)",
            "_f = MedianFinder()\nfor _v in (5, 3, 8):\n    _f.add_num(_v)\nassert _f.find_median() == 5.0, '5、3、8 的中位数是 5.0，实际 %r' % (_f.find_median(),)",
            "_g = MedianFinder()\n_g.add_num(-1)\n_g.add_num(-2)\nassert _g.find_median() == -1.5, '负数：( -1 + -2 ) / 2 = -1.5，实际 %r' % (_g.find_median(),)",
            "_h = MedianFinder()\nfor _v in (6, 10, 2, 6, 5):\n    _h.add_num(_v)\nassert _h.find_median() == 6.0, '2、5、6、6、10 的中位数是 6.0，实际 %r' % (_h.find_median(),)",
            "_big = MedianFinder()\nfor _v in range(1, 101):\n    _big.add_num(_v)\nassert _big.find_median() == 50.5, '1~100 的中位数是 (50 + 51) / 2 = 50.5，实际 %r' % (_big.find_median(),)",
            "_odd = MedianFinder()\nfor _v in range(1, 102):\n    _odd.add_num(_v)\nassert _odd.find_median() == 51.0, '1~101 的中位数是 51.0，实际 %r' % (_odd.find_median(),)",
            "assert 'heapq' in _src, '本题要求用 heapq 实现两个堆'",
        ],
        'explanation': (
            '中位数的本质是「把数据分成大小接近的两半」，这正好对应两个堆：\n\n'
            '- `small` 装较小的一半，堆顶是**这一半里最大的**（所以用小顶堆 + 取负数模拟大顶堆）；\n'
            '- `large` 装较大的一半，堆顶是**这一半里最小的**。\n\n'
            '只要维护好两个不变量：\n\n'
            '1. `small` 里的所有数都不大于 `large` 里的数；\n'
            '2. 两个堆的大小差不超过 1。\n\n'
            '那么中位数就在两个堆顶——奇数时是 `small` 堆顶，偶数时是两个堆顶的平均。\n\n'
            '`-num` 这个技巧值得记住：Python 的 `heapq` 只有小顶堆，'
            '要当大顶堆用就得**把值取负**，取出时再取回负号。\n\n'
            '常见错误：只做了大小平衡、忘了比较两个堆顶的大小（数据顺序乱了）；'
            '以及返回 `(-self.small[0] + self.large[0]) / 2` 时忘了先给 `small[0]` 取负。\n\n'
            '复杂度：`add_num` O(log n)、`find_median` O(1)、空间 O(n)。'
        ),
        'expected_output': '1.0\n1.5\n2.0\n2.5\n0.0',
        'hints': ['small 存负数当大顶堆用，堆顶是这一半里最大的', '每次 add 后都要维护：两堆顶的顺序 + 两堆大小差不超过 1'],
    },

    # ── 专题 112 图与搜索 ──────────────────────────────────
    {
        'id': 'alg-033',
        'track': 'algorithm',
        'chapter_id': 112,
        'chapter_title': '图与搜索',
        'topic': '图与搜索',
        'title': '岛屿数量（网格 DFS/BFS）',
        'difficulty': 2,
        'tags': ['网格', 'DFS', 'BFS'],
        'statement': (
            '定义函数 `num_islands(grid)`：`grid` 是二维列表，'
            '元素是字符串 `"1"`（陆地）或 `"0"`（水）。\n\n'
            '- **上下左右**相邻的陆地连成一座岛（斜着相邻**不算**同一座岛）\n'
            '- 返回岛屿的总数；空网格（`[]` 或 `[[]]`）返回 0\n\n'
            '要求一次遍历网格：遇到 `"1"` 就把答案 +1，然后从这个格子出发'
            '用 **DFS 或 BFS 把整座岛都「淹掉」**（把访问过的 `"1"` 改成 `"0"`），'
            '这样每个格子最多被访问一次，整体 O(行 × 列)。\n\n'
            '允许**直接修改**传入的 grid。\n\n'
            '然后打印 3 座岛的经典例子、`[["0"]]` 和 `[]` 的结果。'
        ),
        'starter_code': 'def num_islands(grid):\n    if not grid or not grid[0]:\n        return 0\n    count = 0\n    # 遇到 "1"：count += 1，然后用栈/队列把整座岛淹掉\n    pass\n',
        'solution': (
            "def num_islands(grid):\n"
            "    if not grid or not grid[0]:\n"
            "        return 0\n"
            "    rows = len(grid)\n"
            "    cols = len(grid[0])\n"
            "    count = 0\n"
            "    for r in range(rows):\n"
            "        for c in range(cols):\n"
            "            if grid[r][c] != '1':\n"
            "                continue\n"
            "            count += 1\n"
            "            stack = [(r, c)]\n"
            "            grid[r][c] = '0'\n"
            "            while stack:\n"
            "                row, col = stack.pop()\n"
            "                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n"
            "                    nr = row + dr\n"
            "                    nc = col + dc\n"
            "                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':\n"
            "                        grid[nr][nc] = '0'\n"
            "                        stack.append((nr, nc))\n"
            "    return count\n"
            "\n"
            "board = [\n"
            "    ['1', '1', '0', '0', '0'],\n"
            "    ['1', '1', '0', '0', '0'],\n"
            "    ['0', '0', '1', '0', '0'],\n"
            "    ['0', '0', '0', '1', '1'],\n"
            "]\n"
            "print(num_islands(board))\n"
            "print(num_islands([['0']]))\n"
            "print(num_islands([]))\n"
        ),
        'checks': [
            "assert num_islands([['1', '1', '1', '1', '0'], ['1', '1', '0', '1', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '0', '0', '0']]) == 1, '这一整块陆地连成 1 座岛，实际 %r' % (num_islands([['1', '1', '1', '1', '0'], ['1', '1', '0', '1', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '0', '0', '0']]),)",
            "assert num_islands([['1', '1', '0', '0', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '0', '1', '1']]) == 3, '经典例子有 3 座岛，实际 %r' % (num_islands([['1', '1', '0', '0', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '0', '1', '1']]),)",
            "assert num_islands([]) == 0, '空网格应返回 0'",
            "assert num_islands([[]]) == 0, '只有一行空列表也应返回 0'",
            "assert num_islands([['0']]) == 0 and num_islands([['1']]) == 1, '1×1 网格的两种情况'",
            "assert num_islands([['1', '0'], ['0', '1']]) == 2, '斜着相邻不算连在一起，应是 2 座岛'",
            "assert num_islands([['1', '1', '1'], ['1', '1', '1'], ['1', '1', '1']]) == 1, '整片陆地是 1 座岛'",
            "assert num_islands([['0', '0'], ['0', '0']]) == 0, '全是水应返回 0'",
            "assert num_islands([['1', '0', '1', '0', '1']]) == 3, '一行里被水隔开的是 3 座岛'",
            "assert num_islands([['1'], ['0'], ['1']]) == 2, '一列里被水隔开的是 2 座岛'",
            "assert num_islands([['1', '0', '1'], ['1', '1', '1'], ['0', '0', '1']]) == 1, '拐弯相连的陆地算同一座岛'",
        ],
        'explanation': (
            '网格问题可以看成一幅图：每个格子是一个点，上下左右的格子之间有边。'
            '于是「数岛屿」= 「数连通分量」。\n\n'
            '标准做法是**一遍扫描 + 淹没**：\n\n'
            '```python\n'
            'if grid[r][c] != "1":\n'
            '    continue\n'
            'count += 1\n'
            'stack = [(r, c)]        # 用栈 = DFS，用 deque 当队列 = BFS\n'
            'grid[r][c] = "0"        # 入栈时就标记，避免重复入栈\n'
            '```\n\n'
            '「标记」这一步很关键：把访问过的陆地改成 `"0"`，'
            '后面就不会重复数同一座岛，每个格子只处理一次，整体 O(行 × 列)。\n\n'
            '常见错误：\n\n'
            '1. **越界检查**写成 `0 <= nr <= rows`，多算了边界外面一格；\n'
            '2. 忘记把 `grid[nr][nc]` 标记掉就入栈，'
            '同一格被邻居反复入栈，数据大时会爆内存；\n'
            '3. 用递归 DFS 处理 1000×1000 的网格——Python 递归深度默认只有 1000，'
            '会抛 `RecursionError`，这种情况用**显式栈**更稳。\n\n'
            '复杂度：时间 O(行 × 列)、空间 O(行 × 列)。'
        ),
        'expected_output': '3\n0\n0',
        'hints': ['遇到 "1" 就 count += 1，然后用栈把整座岛淹成 "0"', '四个方向写成 (1,0) (-1,0) (0,1) (0,-1)，越界要判断'],
    },
    {
        'id': 'alg-034',
        'track': 'algorithm',
        'chapter_id': 112,
        'chapter_title': '图与搜索',
        'topic': '图与搜索',
        'title': '无向图最短路径（BFS 层数）',
        'difficulty': 2,
        'tags': ['图', 'BFS', '最短路'],
        'statement': (
            '定义函数 `shortest_distance(edges, n, start, target)`：\n\n'
            '- 图里有 `n` 个节点，编号 `0 ~ n-1`；\n'
            '- `edges` 是**无向边**列表，每条边形如 `[u, v]`（可能有重复边，也可能有自环 `[u, u]`）；\n'
            '- 返回从 `start` 到 `target` 的**最少边数**；\n'
            '- 不可达返回 `-1`；`start == target` 返回 `0`。\n\n'
            '要求先建**邻接表**（每个点连了哪些点），再用 **BFS** 一层一层往外扩：'
            '用队列，起点距离 0，每遇到一个没访问过的邻居，'
            '它的距离就是「当前点距离 + 1」。\n\n'
            '为什么不能用 DFS？因为 DFS 先走到的那条路不一定最短。\n\n'
            '然后打印 `shortest_distance([[0, 1], [1, 2], [2, 3]], 4, 0, 3)`、'
            '`shortest_distance([[0, 1], [1, 2], [2, 3]], 4, 3, 3)`、'
            '`shortest_distance([[0, 1]], 3, 0, 2)` 的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef shortest_distance(edges, n, start, target):\n    graph = [[] for _ in range(n)]\n    # 建邻接表，然后 BFS\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "def shortest_distance(edges, n, start, target):\n"
            "    graph = [[] for _ in range(n)]\n"
            "    for u, v in edges:\n"
            "        graph[u].append(v)\n"
            "        graph[v].append(u)\n"
            "    if start == target:\n"
            "        return 0\n"
            "    distance = [-1] * n\n"
            "    distance[start] = 0\n"
            "    queue = deque([start])\n"
            "    while queue:\n"
            "        node = queue.popleft()\n"
            "        for nxt in graph[node]:\n"
            "            if distance[nxt] == -1:\n"
            "                distance[nxt] = distance[node] + 1\n"
            "                if nxt == target:\n"
            "                    return distance[nxt]\n"
            "                queue.append(nxt)\n"
            "    return -1\n"
            "\n"
            "print(shortest_distance([[0, 1], [1, 2], [2, 3]], 4, 0, 3))\n"
            "print(shortest_distance([[0, 1], [1, 2], [2, 3]], 4, 3, 3))\n"
            "print(shortest_distance([[0, 1]], 3, 0, 2))\n"
        ),
        'checks': [
            "assert shortest_distance([[0, 1], [1, 2], [2, 3], [3, 4]], 5, 0, 4) == 4, '一条链要走 4 条边，实际 %r' % (shortest_distance([[0, 1], [1, 2], [2, 3], [3, 4]], 5, 0, 4),)",
            "assert shortest_distance([[0, 1], [1, 2], [2, 3], [3, 4]], 5, 4, 0) == 4, '无向图两个方向的距离一样，实际 %r' % (shortest_distance([[0, 1], [1, 2], [2, 3], [3, 4]], 5, 4, 0),)",
            "assert shortest_distance([[0, 1], [1, 2], [0, 2], [2, 3]], 4, 0, 3) == 2, '有捷径时最短距离是 2（0->2->3），实际 %r' % (shortest_distance([[0, 1], [1, 2], [0, 2], [2, 3]], 4, 0, 3),)",
            "assert shortest_distance([], 3, 2, 2) == 0, '起点就是终点应返回 0'",
            "assert shortest_distance([[0, 1], [2, 3]], 4, 0, 3) == -1, '不连通的两个点应返回 -1，实际 %r' % (shortest_distance([[0, 1], [2, 3]], 4, 0, 3),)",
            "assert shortest_distance([], 1, 0, 0) == 0, '只有一个节点、起点终点都是它，返回 0'",
            "assert shortest_distance([[0, 0], [0, 1]], 2, 0, 1) == 1, '自环不会缩短距离，实际 %r' % (shortest_distance([[0, 0], [0, 1]], 2, 0, 1),)",
            "assert shortest_distance([[0, 1], [0, 2], [0, 3], [0, 4]], 5, 2, 4) == 2, '星形图上两个叶子之间要走 2 步，实际 %r' % (shortest_distance([[0, 1], [0, 2], [0, 3], [0, 4]], 5, 2, 4),)",
            "assert shortest_distance([[0, 1], [1, 2], [2, 3], [3, 0]], 4, 0, 2) == 2, '环上要走最短的那一边（2 步），实际 %r' % (shortest_distance([[0, 1], [1, 2], [2, 3], [3, 0]], 4, 0, 2),)",
            "assert shortest_distance([[0, 1], [1, 2], [2, 0]], 3, 0, 2) == 1, '三角形里 0 和 2 直接相连，距离 1，实际 %r' % (shortest_distance([[0, 1], [1, 2], [2, 0]], 3, 0, 2),)",
            "assert shortest_distance([[0, 0], [0, 0]], 3, 0, 2) == -1, '只有自环时节点 2 不可达'",
            "_line = [[i, i + 1] for i in range(9)]\nassert shortest_distance(_line, 10, 0, 9) == 9, '10 个点的链，0 到 9 要走 9 步，实际 %r' % (shortest_distance(_line, 10, 0, 9),)",
        ],
        'explanation': (
            'BFS 求无权图最短路的原理是：**它按距离从小到大逐层扩展**。'
            '第一层是距离 1 的点，第二层是距离 2 的点……'
            '所以某个点**第一次**被访问到时的距离，一定是最短的。\n\n'
            '```python\n'
            'distance = [-1] * n        # -1 既表示「没访问过」，也是不可达的返回值\n'
            'distance[start] = 0\n'
            'queue = deque([start])\n'
            'while queue:\n'
            '    node = queue.popleft()\n'
            '    for nxt in graph[node]:\n'
            '        if distance[nxt] == -1:      # 只处理第一次到达\n'
            '            distance[nxt] = distance[node] + 1\n'
            '            queue.append(nxt)\n'
            '```\n\n'
            '「入队时就标记」很重要：如果等出队再标记，同一个点可能被多个邻居重复入队。\n\n'
            '为什么用 `deque` 而不是 `list`？`list.pop(0)` 要把后面所有元素前移，是 O(n)，'
            '`deque.popleft()` 是 O(1)。数据大时差别很明显。\n\n'
            '为什么 DFS 不行？DFS 会「一条路走到黑」，'
            '它第一次到达目标点的路径可能绕了很远，得到的是错误答案。\n\n'
            '复杂度：时间 O(n + 边数)、空间 O(n + 边数)。'
        ),
        'expected_output': '3\n0\n-1',
        'hints': ['先建邻接表 graph[u].append(v) 和 graph[v].append(u)', 'BFS：distance[nxt] = distance[node] + 1，第一次访问就是最短'],
    },
    {
        'id': 'alg-035',
        'track': 'algorithm',
        'chapter_id': 112,
        'chapter_title': '图与搜索',
        'topic': '图与搜索',
        'title': '课程表：拓扑排序判断能否修完',
        'difficulty': 3,
        'tags': ['图', '拓扑排序', '入度'],
        'statement': (
            '定义函数 `can_finish(num_courses, prerequisites)`：\n\n'
            '- 一共有 `num_courses` 门课，编号 `0 ~ num_courses-1`；\n'
            '- `prerequisites` 里每个 `[a, b]` 表示「要修课程 a，必须先修完课程 b」；\n'
            '- 如果能修完全部课程返回 `True`，如果先修关系里存在**环**（互相依赖、'
            '或自己依赖自己）就返回 `False`。\n\n'
            '要求用 **Kahn 算法（BFS 拓扑排序）**：\n\n'
            '1. 建邻接表 `graph[b].append(a)`（b 修完才能修 a），同时统计每门课的**入度**'
            '（有多少门前置课）；\n'
            '2. 把所有**入度为 0** 的课放进队列；\n'
            '3. 不断取出队首课程，把它的后继课入度减 1，减到 0 就入队；\n'
            '4. 统计一共修了几门课，**等于总课程数说明无环**。\n\n'
            '不要用递归 DFS 判断环（本题要求拓扑排序），整体 O(V + E)。\n\n'
            '然后打印 `can_finish(2, [[1, 0]])`、`can_finish(2, [[1, 0], [0, 1]])`、'
            '`can_finish(1, [])` 的结果。'
        ),
        'starter_code': 'from collections import deque\n\ndef can_finish(num_courses, prerequisites):\n    graph = [[] for _ in range(num_courses)]\n    indegree = [0] * num_courses\n    pass\n',
        'solution': (
            "from collections import deque\n"
            "\n"
            "def can_finish(num_courses, prerequisites):\n"
            "    graph = [[] for _ in range(num_courses)]\n"
            "    indegree = [0] * num_courses\n"
            "    for course, pre in prerequisites:\n"
            "        graph[pre].append(course)\n"
            "        indegree[course] += 1\n"
            "    queue = deque([i for i in range(num_courses) if indegree[i] == 0])\n"
            "    finished = 0\n"
            "    while queue:\n"
            "        node = queue.popleft()\n"
            "        finished += 1\n"
            "        for nxt in graph[node]:\n"
            "            indegree[nxt] -= 1\n"
            "            if indegree[nxt] == 0:\n"
            "                queue.append(nxt)\n"
            "    return finished == num_courses\n"
            "\n"
            "print(can_finish(2, [[1, 0]]))\n"
            "print(can_finish(2, [[1, 0], [0, 1]]))\n"
            "print(can_finish(1, []))\n"
        ),
        'checks': [
            "assert can_finish(2, [[1, 0]]) is True, '1 依赖 0，可以修完，实际 %r' % (can_finish(2, [[1, 0]]),)",
            "assert can_finish(2, [[1, 0], [0, 1]]) is False, '两门课互相依赖，修不完，实际 %r' % (can_finish(2, [[1, 0], [0, 1]]),)",
            "assert can_finish(1, []) is True, '没有依赖关系时一定可以修完'",
            "assert can_finish(3, []) is True, '三门课互不依赖，可以修完'",
            "assert can_finish(4, [[1, 0], [2, 1], [3, 2]]) is True, '一条依赖链可以修完'",
            "assert can_finish(3, [[1, 0], [2, 1], [0, 2]]) is False, '三门课构成环，应返回 False'",
            "assert can_finish(4, [[1, 0], [2, 1], [3, 0]]) is True, '有公共前置课也没关系，实际 %r' % (can_finish(4, [[1, 0], [2, 1], [3, 0]]),)",
            "assert can_finish(5, [[1, 0], [2, 0], [3, 1], [4, 1]]) is True, '树形的依赖关系可以修完'",
            "assert can_finish(5, [[1, 0], [2, 1], [3, 2], [4, 3], [0, 4]]) is False, '五门课绕成一圈，应返回 False'",
            "assert can_finish(2, [[0, 0]]) is False, '自己依赖自己也是矛盾，应返回 False'",
            "assert can_finish(1, [[0, 0]]) is False, '唯一一门课自己依赖自己，应返回 False'",
            "assert can_finish(6, [[1, 0], [3, 2], [5, 4]]) is True, '三组彼此独立的依赖对可以修完'",
            "assert can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) is True, '菱形依赖（3 需要 1 和 2）可以修完，实际 %r' % (can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]]),)",
        ],
        'explanation': (
            '拓扑排序回答的是「这些有先后要求的任务，能否排出一个合法顺序」。'
            'Kahn 算法的直觉非常朴素：**总得先有「没有前置要求」的课能修**。\n\n'
            '```python\n'
            'for course, pre in prerequisites:\n'
            '    graph[pre].append(course)     # pre 修完 -> course 解锁\n'
            '    indegree[course] += 1         # course 还有几门前置课\n'
            'queue = deque([i for i in range(num_courses) if indegree[i] == 0])\n'
            '```\n\n'
            '然后不断「修一门课 → 让后继课的入度减 1」，减到 0 就解锁入队。'
            '如果最后**修完的课程数小于总数**，说明剩下那些课的入度永远降不到 0——'
            '它们被别人（们）互相卡住了，也就是**存在环**。\n\n'
            '注意有向边的方向：`[a, b]` 表示 b 是 a 的前置，所以边是 `b → a`。'
            '写反了的话，简单链的例子照样过，但环的例子会判错。\n\n'
            '自环 `[0, 0]` 会让 0 号课的入度至少为 1，永远进不了队列，所以也是 False——'
            '这个边界很容易漏。\n\n'
            '复杂度：时间 O(V + E)、空间 O(V + E)。'
        ),
        'expected_output': 'True\nFalse\nTrue',
        'hints': ['邻接表方向是 graph[前置] -> 课程，同时统计入度', '最后比较「修完的课程数」和 num_courses 是否相等'],
    },

    # ── 专题 113 动态规划 ──────────────────────────────────
    {
        'id': 'alg-036',
        'track': 'algorithm',
        'chapter_id': 113,
        'chapter_title': '动态规划',
        'topic': '动态规划',
        'title': '爬楼梯（入门 DP）',
        'difficulty': 1,
        'tags': ['动态规划', '递推', '滚动变量'],
        'statement': (
            '定义函数 `climb_stairs(n)`：一次可以爬 1 级或 2 级台阶，返回爬到第 n 级的**方法数**。\n\n'
            '- `n >= 1`，`climb_stairs(1)` 是 1（只能一次一级）\n'
            '- `climb_stairs(2)` 是 2（一级一级走，或一次两级）\n'
            '- `climb_stairs(3)` 是 3\n\n'
            '思路（DP）：到达第 n 级，要么是从第 `n-1` 级迈一级上来，'
            '要么是从第 `n-2` 级迈两级上来，所以 `f(n) = f(n-1) + f(n-2)`。\n\n'
            '要求用**迭代**实现，并且只滚动保存两个变量（`prev, curr = curr, prev + curr`），'
            '空间 O(1)、时间 O(n)。\n\n'
            '**不要写朴素递归**——那是重复计算，n=45 时慢到跑不完。\n\n'
            '然后打印 `climb_stairs(1)`、`climb_stairs(2)`、`climb_stairs(3)` 和 `climb_stairs(45)`。'
        ),
        'starter_code': 'def climb_stairs(n):\n    if n <= 2:\n        return n\n    prev, curr = 1, 2\n    # 滚动递推\n    pass\n',
        'solution': (
            "def climb_stairs(n):\n"
            "    if n <= 2:\n"
            "        return n\n"
            "    prev, curr = 1, 2\n"
            "    for _ in range(3, n + 1):\n"
            "        prev, curr = curr, prev + curr\n"
            "    return curr\n"
            "\n"
            "print(climb_stairs(1), climb_stairs(2), climb_stairs(3))\n"
            "print(climb_stairs(10))\n"
            "print(climb_stairs(45))\n"
        ),
        'checks': [
            "assert climb_stairs(1) == 1, '只有 1 级台阶时方法数是 1'",
            "assert climb_stairs(2) == 2, '2 级台阶有 2 种走法（1+1 或 2）'",
            "assert climb_stairs(3) == 3, '3 级台阶有 3 种走法，实际 %r' % (climb_stairs(3),)",
            "assert climb_stairs(4) == 5 and climb_stairs(5) == 8, '4 级是 5 种、5 级是 8 种，实际 %r / %r' % (climb_stairs(4), climb_stairs(5))",
            "assert climb_stairs(10) == 89, '10 级台阶是 89 种，实际 %r' % (climb_stairs(10),)",
            "assert climb_stairs(20) == 10946, '20 级台阶是 10946 种，实际 %r' % (climb_stairs(20),)",
            "assert climb_stairs(35) == 14930352, '35 级台阶是 14930352 种，实际 %r' % (climb_stairs(35),)",
            "assert climb_stairs(45) == 1836311903, '45 级台阶是 1836311903 种（朴素递归在这里会超时），实际 %r' % (climb_stairs(45),)",
        ],
        'explanation': (
            '动态规划的第一步是**定义状态**：`f(n)` 表示「爬到第 n 级的方法数」。\n\n'
            '第二步是**找转移方程**：最后一步只有两种可能——'
            '从第 n-1 级迈 1 级上来，或从第 n-2 级迈 2 级上来。'
            '所以 `f(n) = f(n-1) + f(n-2)`。\n\n'
            '```python\n'
            'if n <= 2:\n'
            '    return n\n'
            'prev, curr = 1, 2\n'
            'for _ in range(3, n + 1):\n'
            '    prev, curr = curr, prev + curr\n'
            'return curr\n'
            '```\n\n'
            '这就是斐波那契数列，只是起点挪了一位。\n\n'
            '为什么不能写朴素递归？因为它会**重复计算**同一个子问题：'
            '`f(45)` 会算出两颗巨大的子树，调用次数是天文数字（约 10 亿次），'
            '而迭代只需要 43 次加法。\n\n'
            '「只保存前两个值」的技巧叫**滚动变量**：'
            '算 `f(n)` 只依赖 `f(n-1)` 和 `f(n-2)`，更早的值用完就可以丢，'
            '于是空间从 O(n) 的数组降到 O(1)。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': '1 2 3\n89\n1836311903',
        'hints': ['f(n) = f(n-1) + f(n-2)，起点 f(1) = 1、f(2) = 2', '只留两个变量：prev, curr = curr, prev + curr'],
    },
    {
        'id': 'alg-037',
        'track': 'algorithm',
        'chapter_id': 113,
        'chapter_title': '动态规划',
        'topic': '动态规划',
        'title': '最长递增子序列',
        'difficulty': 2,
        'tags': ['动态规划', '子序列', 'LIS'],
        'statement': (
            '定义函数 `length_of_lis(nums)`：返回最长**严格递增**子序列的长度。\n\n'
            '子序列是指从原数组里按顺序挑出若干元素（**可以不连续**），'
            '但**不能改变相对顺序**。\n\n'
            '- `[10, 9, 2, 5, 3, 7, 101, 18]` → 4（`2, 3, 7, 101`）\n'
            '- 相等的元素不算递增：`[7, 7, 7, 7]` → 1\n'
            '- 空数组返回 0\n\n'
            '要求用 DP，`dp[i]` 表示「**以 `nums[i]` 结尾**的最长递增子序列长度」，'
            '转移是「往前找一个比 `nums[i]` 小的 `j`，取 `dp[j] + 1` 的最大值」；'
            '答案是 `dp` 里的最大值（不是 `dp[-1]`）。O(n²) 即可。\n\n'
            '然后打印 `length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])`、'
            '`length_of_lis([7, 7, 7, 7])`、`length_of_lis([])` 的结果。'
        ),
        'starter_code': 'def length_of_lis(nums):\n    # dp[i] 表示以 nums[i] 结尾的最长递增子序列长度\n    pass\n',
        'solution': (
            "def length_of_lis(nums):\n"
            "    if not nums:\n"
            "        return 0\n"
            "    dp = [1] * len(nums)\n"
            "    for i in range(1, len(nums)):\n"
            "        for j in range(i):\n"
            "            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:\n"
            "                dp[i] = dp[j] + 1\n"
            "    return max(dp)\n"
            "\n"
            "print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))\n"
            "print(length_of_lis([7, 7, 7, 7]))\n"
            "print(length_of_lis([]))\n"
        ),
        'checks': [
            "assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4, '经典例子答案是 4（2, 3, 7, 101），实际 %r' % (length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]),)",
            "assert length_of_lis([7, 7, 7, 7]) == 1, '相等不算严格递增，答案是 1，实际 %r' % (length_of_lis([7, 7, 7, 7]),)",
            "assert length_of_lis([]) == 0, '空数组应返回 0'",
            "assert length_of_lis([1]) == 1, '单元素数组应返回 1'",
            "assert length_of_lis([1, 2, 3, 4, 5]) == 5, '整体递增时答案就是长度'",
            "assert length_of_lis([5, 4, 3, 2, 1]) == 1, '整体递减时答案是 1'",
            "assert length_of_lis([3, 1, 2]) == 2, '[3, 1, 2] 的答案是 2（1, 2），实际 %r' % (length_of_lis([3, 1, 2]),)",
            "assert length_of_lis([0, 1, 0, 3, 2, 3]) == 4, '答案是 4（0, 1, 2, 3），实际 %r' % (length_of_lis([0, 1, 0, 3, 2, 3]),)",
            "assert length_of_lis([-5, -3, -1]) == 3, '负数序列也要能算'",
            "assert length_of_lis([2, 2, 2, 3]) == 2, '前面重复的 2 不算递增，答案是 2，实际 %r' % (length_of_lis([2, 2, 2, 3]),)",
            "assert length_of_lis(list(range(500))) == 500, '500 个递增元素答案是 500'",
        ],
        'explanation': (
            'DP 题目的标准三步：**定义状态 → 转移方程 → 初始值和答案**。\n\n'
            '- 状态：`dp[i]` = 以 `nums[i]` **结尾**的最长递增子序列长度；\n'
            '- 转移：`dp[i] = max(dp[j] + 1)`，其中 `j < i` 且 `nums[j] < nums[i]`；\n'
            '- 初始化：每个元素自己就是一个长度 1 的序列，所以 `dp = [1] * n`。\n\n'
            '为什么是「以 nums[i] 结尾」？因为只有固定了结尾，'
            '才能判断「能不能把新的数接上去」。\n\n'
            '**答案不是 `dp[-1]`，而是 `max(dp)`**：'
            '最长的那条子序列可能在数组中间就结束了。'
            '这是本题最常见的错误，比如 `[1, 2, 3, 0]` 的答案应该是 3，'
            '但 `dp[-1]` 只有 1。\n\n'
            '另一个坑是 `nums[j] < nums[i]` 写成了 `<=`，那样重复元素会被算进递增序列，'
            '`[7, 7, 7, 7]` 就会得到 4 而不是 1。\n\n'
            '进阶：用「贪心 + 二分（patience sorting）」可以做到 O(n log n)。\n\n'
            '复杂度：时间 O(n²)、空间 O(n)。'
        ),
        'expected_output': '4\n1\n0',
        'hints': ['dp[i] 表示以 nums[i] 结尾的最长递增子序列长度，初值全为 1', '答案是 max(dp)，不是 dp[-1]'],
    },
    {
        'id': 'alg-038',
        'track': 'algorithm',
        'chapter_id': 113,
        'chapter_title': '动态规划',
        'topic': '动态规划',
        'title': '零钱兑换（完全背包）',
        'difficulty': 2,
        'tags': ['动态规划', '完全背包', '最值'],
        'statement': (
            '定义函数 `coin_change(coins, amount)`：用面额列表 `coins` 凑出金额 `amount`，'
            '每种面额的硬币可以**无限次使用**，返回**最少需要的硬币个数**。\n\n'
            '- 凑不出来返回 `-1`；`amount == 0` 返回 `0`；`coins` 为空且 `amount > 0` 返回 `-1`\n'
            '- `coin_change([1, 2, 5], 11)` → 3（5 + 5 + 1）\n'
            '- `coin_change([2], 3)` → -1\n\n'
            '要求用 DP：`dp[i]` 表示「凑出金额 i 的最少硬币数」，'
            '`dp[0] = 0`，其余初始化为「无穷大」（可以用 `float("inf")`），'
            '转移是 `dp[i] = min(dp[i - coin] + 1)`，对所有 `coin <= i` 试一遍。\n\n'
            '复杂度 O(amount × len(coins))。\n\n'
            '然后打印 `coin_change([1, 2, 5], 11)`、`coin_change([2], 3)`、'
            '`coin_change([1], 0)`、`coin_change([2, 5], 11)` 的结果。'
        ),
        'starter_code': 'def coin_change(coins, amount):\n    dp = [0] + [float("inf")] * amount\n    # 从 1 到 amount 逐个求最少硬币数\n    pass\n',
        'solution': (
            "def coin_change(coins, amount):\n"
            "    INF = float('inf')\n"
            "    dp = [0] + [INF] * amount\n"
            "    for i in range(1, amount + 1):\n"
            "        for coin in coins:\n"
            "            if coin <= i and dp[i - coin] + 1 < dp[i]:\n"
            "                dp[i] = dp[i - coin] + 1\n"
            "    if dp[amount] == INF:\n"
            "        return -1\n"
            "    return dp[amount]\n"
            "\n"
            "print(coin_change([1, 2, 5], 11))\n"
            "print(coin_change([2], 3))\n"
            "print(coin_change([1], 0))\n"
            "print(coin_change([2, 5], 11))\n"
        ),
        'checks': [
            "assert coin_change([1, 2, 5], 11) == 3, '[1, 2, 5] 凑 11 只要 3 枚（5 + 5 + 1），实际 %r' % (coin_change([1, 2, 5], 11),)",
            "assert coin_change([2], 3) == -1, '面额只有 2 时凑不出 3，应返回 -1，实际 %r' % (coin_change([2], 3),)",
            "assert coin_change([1], 0) == 0, 'amount 为 0 时应返回 0（不需要任何硬币）'",
            "assert coin_change([5], 5) == 1, '正好有一枚硬币时应返回 1'",
            "assert coin_change([2, 5], 11) == 4, '只能用 2 和 5 凑 11 需要 4 枚（5 + 2 + 2 + 2），实际 %r' % (coin_change([2, 5], 11),)",
            "assert coin_change([], 5) == -1, '没有可用面额时应返回 -1'",
            "assert coin_change([], 0) == 0, '没有面额但金额为 0，仍然返回 0'",
            "assert coin_change([1], 5) == 5, '只能用 1 元硬币时要 5 枚'",
            "assert coin_change([1, 2, 5], 1) == 1 and coin_change([1, 2, 5], 2) == 1, '金额 1 和 2 都只要 1 枚'",
            "assert coin_change([3, 7], 5) == -1, '3 和 7 都超过 5，凑不出应返回 -1'",
            "assert coin_change([1, 5, 10], 100) == 10, '100 元用 10 张 10 元，实际 %r' % (coin_change([1, 5, 10], 100),)",
            "assert coin_change([7, 11], 100) == 12, '100 用 11 和 7 凑：11*8 + 7*... 最优是 12 枚，实际 %r' % (coin_change([7, 11], 100),)",
        ],
        'explanation': (
            '这是**完全背包**的入门题：每种硬币可以拿无限次，求最小值。\n\n'
            '- 状态：`dp[i]` = 凑出金额 i 的最少硬币数；\n'
            '- 转移：`dp[i] = min(dp[i - coin] + 1)`，意思是「最后放一枚面值 coin 的硬币」；\n'
            '- 边界：`dp[0] = 0`，其他先设成 `inf`（表示暂时凑不出来）。\n\n'
            '为什么用 `float("inf")` 当初始值？因为它比任何真实答案都大，'
            '`min` 之后不会影响结果；而写成 0 或 -1 会让「凑不出来」和「0 枚硬币」混淆。\n\n'
            '```python\n'
            'for i in range(1, amount + 1):\n'
            '    for coin in coins:\n'
            '        if coin <= i and dp[i - coin] + 1 < dp[i]:\n'
            '            dp[i] = dp[i - coin] + 1\n'
            '```\n\n'
            '**循环顺序**：外层是金额（从小到大），内层是硬币。'
            '金额从 1 往上算，保证 `dp[i - coin]` 已经算好了。\n\n'
            '最后判断 `dp[amount]` 是否还是无穷大，是就返回 -1。'
            '常见错误：忘了这个判断，直接返回 `dp[amount]`，'
            '结果凑不出来时返回一个天文数字。\n\n'
            '注意贪心在这里是**错的**：`coins = [1, 3, 4]`、`amount = 6`，'
            '贪心会拿 4 + 1 + 1 = 3 枚，而最优是 3 + 3 = 2 枚——'
            '这正是要用 DP 的原因。\n\n'
            '复杂度：时间 O(amount × len(coins))、空间 O(amount)。'
        ),
        'expected_output': '3\n-1\n0\n4',
        'hints': ['dp[0] = 0，其余用 float("inf") 初始化', '最后要判断 dp[amount] 是否还是无穷大，是就返回 -1'],
    },
    {
        'id': 'alg-039',
        'track': 'algorithm',
        'chapter_id': 113,
        'chapter_title': '动态规划',
        'topic': '动态规划',
        'title': '0-1 背包（一维滚动数组）',
        'difficulty': 3,
        'tags': ['动态规划', '背包', '滚动数组'],
        'statement': (
            '定义函数 `knapsack(weights, values, capacity)`：\n\n'
            '- 有若干物品，第 i 件的重量是 `weights[i]`、价值是 `values[i]`；\n'
            '- 每件物品**最多拿一次**（0-1 背包）；\n'
            '- 背包承重 `capacity`，返回能装下的**最大总价值**；\n'
            '- 物品列表为空或 `capacity == 0` 时返回 0。\n\n'
            '要求用 DP 的一维滚动数组：`dp[j]` 表示「容量为 j 时的最大价值」，'
            '外层遍历物品、内层遍历容量，并且**容量必须从大到小遍历**：\n\n'
            '```python\n'
            'for i in range(len(weights)):\n'
            '    for j in range(capacity, weights[i] - 1, -1):\n'
            '        dp[j] = max(dp[j], dp[j - weights[i]] + values[i])\n'
            '```\n\n'
            '为什么倒着走？如果正着走，`dp[j - weights[i]]` 可能已经包含了当前物品，'
            '那就变成「一件物品拿多次」了。\n\n'
            '然后打印 `knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5)`、'
            '`knapsack([1, 2, 3], [6, 10, 12], 5)`、`knapsack([], [], 10)`、'
            '`knapsack([5], [10], 3)` 的结果。'
        ),
        'starter_code': 'def knapsack(weights, values, capacity):\n    dp = [0] * (capacity + 1)\n    # 外层物品、内层容量从大到小\n    pass\n',
        'solution': (
            "def knapsack(weights, values, capacity):\n"
            "    dp = [0] * (capacity + 1)\n"
            "    for i in range(len(weights)):\n"
            "        for j in range(capacity, weights[i] - 1, -1):\n"
            "            take = dp[j - weights[i]] + values[i]\n"
            "            if take > dp[j]:\n"
            "                dp[j] = take\n"
            "    return dp[capacity]\n"
            "\n"
            "print(knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5))\n"
            "print(knapsack([1, 2, 3], [6, 10, 12], 5))\n"
            "print(knapsack([], [], 10))\n"
            "print(knapsack([5], [10], 3))\n"
        ),
        'checks': [
            "assert knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5) == 7, '容量 5 时应拿重量 2+3 的两件（价值 3+4=7），实际 %r' % (knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5),)",
            "assert knapsack([1, 2, 3], [6, 10, 12], 5) == 22, '容量 5 时拿重量 2+3 的两件（价值 10+12=22），实际 %r' % (knapsack([1, 2, 3], [6, 10, 12], 5),)",
            "assert knapsack([], [], 10) == 0, '没有物品时最大价值是 0'",
            "assert knapsack([5], [10], 3) == 0, '物品比背包还重，装不下，价值 0'",
            "assert knapsack([1, 2, 3], [6, 10, 12], 6) == 28, '容量 6 能装下全部三件，价值 28，实际 %r' % (knapsack([1, 2, 3], [6, 10, 12], 6),)",
            "assert knapsack([3], [5], 3) == 5, '刚好装下时价值是 5'",
            "assert knapsack([1, 1, 1], [1, 2, 3], 2) == 5, '容量 2 时应挑价值最大的两件（3 + 2 = 5），实际 %r' % (knapsack([1, 1, 1], [1, 2, 3], 2),)",
            "assert knapsack([2, 2], [3, 3], 4) == 6, '两件都要拿，实际 %r' % (knapsack([2, 2], [3, 3], 4),)",
            "assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9, '容量 7 时 3 + 4 的两件价值 4 + 5 = 9，实际 %r' % (knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7),)",
            "assert knapsack([2, 3, 5], [10, 15, 25], 10) == 50, '三件刚好装满（2 + 3 + 5），价值 50，实际 %r' % (knapsack([2, 3, 5], [10, 15, 25], 10),)",
            "assert knapsack([1] * 50, [1] * 50, 30) == 30, '50 件重量 1 价值 1 的物品、容量 30，最多拿 30 件，实际 %r' % (knapsack([1] * 50, [1] * 50, 30),)",
            "assert knapsack([3, 4], [7, 8], 0) == 0, '容量为 0 时应返回 0'",
        ],
        'explanation': (
            '背包问题的状态设计很像「逐件物品做决策」：\n\n'
            '- `dp[j]`：容量为 j 时能拿到的最大价值；\n'
            '- 面对第 i 件物品，只有两个选择：**不拿**（保持 `dp[j]`）或'
            '**拿**（`dp[j - w] + v`，前提是 j >= w）。\n\n'
            '二维写法是 `dp[i][j]`，而一维滚动数组把「物品」那一维压掉了。'
            '压缩能成立，是因为第 i 行只依赖第 i-1 行——'
            '但代价是**内层容量必须倒序遍历**：\n\n'
            '```python\n'
            'for j in range(capacity, weights[i] - 1, -1):\n'
            '    dp[j] = max(dp[j], dp[j - weights[i]] + values[i])\n'
            '```\n\n'
            '倒着走时，`dp[j - w]` 还是「上一轮（没考虑当前物品）」的旧值；'
            '正着走的话它已经被本轮更新过，等于允许同一件物品被拿多次——'
            '那就变成**完全背包**了。这个「正序 / 倒序」的区别是背包问题的分水岭。\n\n'
            '另外要注意 `dp` 初始化全是 0：它表示「什么都不拿」的合法状态，'
            '所以最后的答案直接就是 `dp[capacity]`。\n\n'
            '复杂度：时间 O(n × capacity)、空间 O(capacity)。'
        ),
        'expected_output': '7\n22\n0\n0',
        'hints': ['内层容量必须从 capacity 倒着走到 weights[i]', '取或不取：max(dp[j], dp[j - w] + v)'],
    },

    # ── 专题 114 贪心算法 ──────────────────────────────────
    {
        'id': 'alg-040',
        'track': 'algorithm',
        'chapter_id': 114,
        'chapter_title': '贪心算法',
        'topic': '贪心算法',
        'title': '活动选择（按结束时间贪心）',
        'difficulty': 2,
        'tags': ['贪心', '区间', '排序'],
        'statement': (
            '定义函数 `max_activities(intervals)`：`intervals` 是活动列表，'
            '每个活动是 `[start, end]`。\n\n'
            '- 同一时间只能参加一个活动；下一个活动的 `start` 必须 **>= 上一个活动的 `end`**'
            '（首尾相接允许）\n'
            '- 返回最多能参加的**活动个数**；空列表返回 0\n\n'
            '要求用**贪心**：\n\n'
            '1. 把所有活动按**结束时间从小到大**排序；\n'
            '2. 选第一个（结束最早的）；\n'
            '3. 往后扫，凡是 `start >= 上一个选中活动的 end` 就选它，并更新「上次结束时间」；\n'
            '4. 统计一共选了几个。\n\n'
            '为什么按结束时间排序是对的？结束得越早，留给后面的时间就越多。\n\n'
            '然后打印 `max_activities([[1, 3], [2, 5], [4, 6], [6, 8], [5, 7]])`、'
            '`max_activities([])`、`max_activities([[1, 10], [2, 3], [4, 5]])` 的结果。'
        ),
        'starter_code': 'def max_activities(intervals):\n    if not intervals:\n        return 0\n    # 按结束时间排序，然后贪心地往后挑\n    pass\n',
        'solution': (
            "def max_activities(intervals):\n"
            "    if not intervals:\n"
            "        return 0\n"
            "    ordered = sorted(intervals, key=lambda item: item[1])\n"
            "    count = 1\n"
            "    last_end = ordered[0][1]\n"
            "    for start, end in ordered[1:]:\n"
            "        if start >= last_end:\n"
            "            count += 1\n"
            "            last_end = end\n"
            "    return count\n"
            "\n"
            "print(max_activities([[1, 3], [2, 5], [4, 6], [6, 8], [5, 7]]))\n"
            "print(max_activities([]))\n"
            "print(max_activities([[1, 10], [2, 3], [4, 5]]))\n"
        ),
        'checks': [
            "assert max_activities([[1, 3], [2, 5], [4, 6], [6, 8], [5, 7]]) == 3, '经典例子最多参加 3 个（[1,3]、[4,6]、[6,8]），实际 %r' % (max_activities([[1, 3], [2, 5], [4, 6], [6, 8], [5, 7]]),)",
            "assert max_activities([]) == 0, '空列表应返回 0'",
            "assert max_activities([[1, 10], [2, 3], [4, 5]]) == 2, '放弃长活动能参加更多：[2,3] 和 [4,5]，实际 %r' % (max_activities([[1, 10], [2, 3], [4, 5]]),)",
            "assert max_activities([[1, 2]]) == 1, '只有一个活动时返回 1'",
            "assert max_activities([[1, 2], [2, 3]]) == 2, '首尾相接（start == 上一个 end）可以参加，实际 %r' % (max_activities([[1, 2], [2, 3]]),)",
            "assert max_activities([[1, 2], [2, 3], [3, 4]]) == 3, '连续相接的三个活动都能参加'",
            "assert max_activities([[1, 5], [1, 5], [1, 5]]) == 1, '时间完全冲突时只能参加 1 个'",
            "assert max_activities([[1, 4], [4, 8]]) == 2, '首尾相接的两个'",
            "assert max_activities([[5, 7], [1, 3], [3, 5]]) == 3, '输入顺序打乱也要先排序再挑，实际 %r' % (max_activities([[5, 7], [1, 3], [3, 5]]),)",
            "assert max_activities([[1, 10], [2, 3], [3, 4], [4, 5]]) == 3, '贪心应放弃最长的 [1,10]，实际 %r' % (max_activities([[1, 10], [2, 3], [3, 4], [4, 5]]),)",
            "assert max_activities([[2, 3], [1, 2], [3, 4], [4, 5]]) == 4, '四个首尾相接的活动都能参加，实际 %r' % (max_activities([[2, 3], [1, 2], [3, 4], [4, 5]]),)",
        ],
        'explanation': (
            '这是贪心算法最经典的例子，也是「贪心选择性质」最好的说明。\n\n'
            '**为什么按结束时间排序**？想象你只有一天时间安排会议：'
            '越早结束的活动，留给后面活动的余量就越大。'
            '所以「结束最早」这个局部最优选择，不会堵死后面的路。\n\n'
            '```python\n'
            'ordered = sorted(intervals, key=lambda item: item[1])\n'
            'count = 1\n'
            'last_end = ordered[0][1]\n'
            'for start, end in ordered[1:]:\n'
            '    if start >= last_end:      # 不冲突\n'
            '        count += 1\n'
            '        last_end = end\n'
            '```\n\n'
            '注意排序键是 `item[1]`（结束时间），不是 `item[0]`（开始时间）。'
            '按开始时间排序会得到错误答案，比如 `[[1,10],[2,3],[4,5]]`，'
            '先选 [1,10] 就只剩 1 个，而最优是 2 个。\n\n'
            '选中的活动个数可以用第一种活动的结束时间做初值，'
            '也可以在循环里用 `-inf` 初始化 `last_end`，两种写法都对。\n\n'
            '复杂度：时间 O(n log n)（排序占主要开销）、空间 O(n)。'
        ),
        'expected_output': '3\n0\n2',
        'hints': ['按结束时间 item[1] 排序，不是开始时间', 'start >= last_end 就选它，并更新 last_end'],
    },
    {
        'id': 'alg-041',
        'track': 'algorithm',
        'chapter_id': 114,
        'chapter_title': '贪心算法',
        'topic': '贪心算法',
        'title': '跳跃游戏（维护最远可达位置）',
        'difficulty': 2,
        'tags': ['贪心', '数组', 'O(n)'],
        'statement': (
            '定义函数 `can_jump(nums)`：`nums[i]` 表示站在下标 i 时'
            '**最多**可以向右跳的步数（1 到 `nums[i]` 步都可以）。\n\n'
            '- 从下标 0 出发，判断能否到达**最后一个下标**；能返回 `True`，不能返回 `False`\n'
            '- 空列表和只有一个元素的列表都返回 `True`（起点就是终点）\n'
            '- `nums` 里的数都是非负整数\n\n'
            '要求用**贪心**做到 O(n)：维护一个变量 `reach` 表示「目前能到达的最远下标」，'
            '从左到右扫描；如果当前下标 `index > reach`，说明这里根本走不到，直接返回 False；'
            '否则用 `index + nums[index]` 更新 `reach`。\n\n'
            '不要用「枚举每个位置能跳到哪些位置」的 BFS/DP（那是 O(n²)）。\n\n'
            '然后打印 `can_jump([2, 3, 1, 1, 4])`、`can_jump([3, 2, 1, 0, 4])`、'
            '`can_jump([])`、`can_jump([0])` 的结果。'
        ),
        'starter_code': 'def can_jump(nums):\n    reach = 0\n    # for index, step in enumerate(nums): 判断 index > reach\n    pass\n',
        'solution': (
            "def can_jump(nums):\n"
            "    reach = 0\n"
            "    for index, step in enumerate(nums):\n"
            "        if index > reach:\n"
            "            return False\n"
            "        if index + step > reach:\n"
            "            reach = index + step\n"
            "    return True\n"
            "\n"
            "print(can_jump([2, 3, 1, 1, 4]))\n"
            "print(can_jump([3, 2, 1, 0, 4]))\n"
            "print(can_jump([]))\n"
            "print(can_jump([0]))\n"
        ),
        'checks': [
            "assert can_jump([2, 3, 1, 1, 4]) is True, '经典可以跳到的例子应返回 True，实际 %r' % (can_jump([2, 3, 1, 1, 4]),)",
            "assert can_jump([3, 2, 1, 0, 4]) is False, '被下标 3 的 0 卡住，应返回 False，实际 %r' % (can_jump([3, 2, 1, 0, 4]),)",
            "assert can_jump([]) is True, '空列表返回 True（起点就是终点）'",
            "assert can_jump([0]) is True, '只有一个元素时已经站在终点，返回 True'",
            "assert can_jump([0, 1]) is False, '第 0 个元素是 0，一步也跳不了，实际 %r' % (can_jump([0, 1]),)",
            "assert can_jump([1, 0, 0]) is False, '只能跳到下标 1，之后走不动，实际 %r' % (can_jump([1, 0, 0]),)",
            "assert can_jump([2, 0, 0]) is True, '一步跳两级就能到终点，实际 %r' % (can_jump([2, 0, 0]),)",
            "assert can_jump([1, 1, 1, 1]) is True, '每次跳一步也能到终点'",
            "assert can_jump([5, 0, 0, 0, 0]) is True, '第一格就能直接跳到终点'",
            "assert can_jump([0, 0, 0]) is False, '全是 0 且长度大于 1，无法前进'",
            "assert can_jump([2, 5, 0, 0]) is True, '中途可以借力跳更远'",
            "assert can_jump([1] * 100) is True, '100 个 1 每次跳一步能到终点'",
            "assert can_jump([1, 0, 1]) is False, '下标 1 的值是 0，跳到那里就走不动了，实际 %r' % (can_jump([1, 0, 1]),)",
            "assert can_jump([1] * 98 + [2, 0]) is True, '只要中途能借力跳远就行'",
        ],
        'explanation': (
            '这题的贪心思想是：**不关心「怎么跳」，只关心「最远能到哪」**。\n\n'
            '```python\n'
            'reach = 0\n'
            'for index, step in enumerate(nums):\n'
            '    if index > reach:\n'
            '        return False            # 这个位置根本到不了\n'
            '    reach = max(reach, index + step)\n'
            'return True\n'
            '```\n\n'
            '`index > reach` 这个判断为什么成立？因为 `reach` 是「所有能到达的位置里'
            '能延伸得最远的那个」。如果连当前下标都超过了 `reach`，'
            '说明中间存在一段「跳不过去的真空」，后面的位置也就都到不了。\n\n'
            '为什么不用 BFS/DP？`dp[i]` 表示能否到达 i，每次要回头找「谁能跳过来」，'
            '是 O(n²)；而上面的贪心只需一趟扫描，因为'
            '「能否到达 i」只取决于「前面所有位置能延伸到的最远处」。\n\n'
            '常见错误：把 `index > reach` 写成 `index >= reach`，'
            '那样 `[0, 1]` 这种「起点就是终点」的情形会被误判；'
            '以及忘了在循环里更新 `reach`，导致死循环或必然返回 True。\n\n'
            '复杂度：时间 O(n)、空间 O(1)。'
        ),
        'expected_output': 'True\nFalse\nTrue\nTrue',
        'hints': ['reach 表示目前能到达的最远下标，初始为 0', 'index > reach 说明这个位置到不了，直接返回 False'],
    },

    # ── 专题 115 回溯算法 ──────────────────────────────────
    {
        'id': 'alg-042',
        'track': 'algorithm',
        'chapter_id': 115,
        'chapter_title': '回溯算法',
        'topic': '回溯算法',
        'title': '全排列（回溯模板）',
        'difficulty': 2,
        'tags': ['回溯', '递归', '排列'],
        'statement': (
            '定义函数 `permute(nums)`：返回 `nums` 的**所有排列**（`nums` 里的元素互不相同）。\n\n'
            '- 返回值是「排列的列表」，每个排列是一个列表；排列之间的先后顺序**不限**\n'
            '- 空列表返回 `[[]]`（只有一个「空排列」）\n'
            '- 长度为 n 的列表应该有 n! 个排列，且不能有重复\n\n'
            '要求用**回溯（递归 + 选择 / 撤销）**实现：\n\n'
            '1. 用一个 `used` 布尔列表记录哪些下标已经被选走；\n'
            '2. 把当前路径 `current` 往下传：`current` 长度等于 n 时就收进结果；\n'
            '3. 否则遍历所有下标，没被用过就「标记 used → append → 递归 → pop → 取消标记」。\n\n'
            '**不要**用 `itertools.permutations`。\n\n'
            '然后打印 `permute([1, 2, 3])`、`permute([])`、`permute([1])` 的结果。'
        ),
        'starter_code': 'def permute(nums):\n    result = []\n    used = [False] * len(nums)\n    def backtrack(current):\n        pass\n    backtrack([])\n    return result\n',
        'solution': (
            "def permute(nums):\n"
            "    result = []\n"
            "    used = [False] * len(nums)\n"
            "    current = []\n"
            "\n"
            "    def backtrack():\n"
            "        if len(current) == len(nums):\n"
            "            result.append(list(current))\n"
            "            return\n"
            "        for i in range(len(nums)):\n"
            "            if used[i]:\n"
            "                continue\n"
            "            used[i] = True\n"
            "            current.append(nums[i])\n"
            "            backtrack()\n"
            "            current.pop()\n"
            "            used[i] = False\n"
            "\n"
            "    backtrack()\n"
            "    return result\n"
            "\n"
            "print(permute([1, 2, 3]))\n"
            "print(permute([]))\n"
            "print(permute([1]))\n"
        ),
        'checks': [
            "_r = permute([1, 2, 3])\nassert len(_r) == 6, '3 个元素应有 3! = 6 个排列，实际 %d 个：%r' % (len(_r), _r)",
            "assert sorted(tuple(p) for p in permute([1, 2, 3])) == [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)], '排列内容不对：%r' % (permute([1, 2, 3]),)",
            "assert all(sorted(list(p)) == [1, 2, 3] for p in permute([1, 2, 3])), '每个结果都必须是原数组的一个排列（元素不能重复或多出来）'",
            "assert permute([]) == [[]], '空列表应返回 [[]]（一个空排列），实际 %r' % (permute([]),)",
            "_single = permute([1])\nassert len(_single) == 1 and list(_single[0]) == [1], '单元素列表只有 1 个排列，实际 %r' % (_single,)",
            "_four = [tuple(p) for p in permute([1, 2, 3, 4])]\nassert len(_four) == 24 and len(set(_four)) == 24, '4 个元素应有 24 个不重复的排列，实际 %r 个' % (len(_four),)",
            "assert sorted(tuple(p) for p in permute([0, -1])) == [(-1, 0), (0, -1)], '包含 0 和负数时也要正确，实际 %r' % (permute([0, -1]),)",
            "_dup = [tuple(p) for p in permute(['a', 'b', 'c'])]\nassert len(set(_dup)) == 6, '字符串元素同样要能全排列'",
            "assert 'permutations' not in _src, '本题要求手写回溯，不能调用 itertools.permutations（提示：答案里也没有这个写法）'",
        ],
        'explanation': (
            '回溯是「带撤销的穷举」，模板长得非常固定：\n\n'
            '```python\n'
            'def backtrack():\n'
            '    if 走到底了:\n'
            '        收集结果\n'
            '        return\n'
            '    for 每个候选:\n'
            '        if 候选不可用: continue\n'
            '        做出选择          # used[i] = True; current.append(...)\n'
            '        backtrack()       # 递归\n'
            '        撤销选择          # current.pop(); used[i] = False\n'
            '```\n\n'
            '**「做出选择」和「撤销选择」必须成对出现**，'
            '顺序也严格相反——这就是「回溯」这个名字的由来。'
            '忘了撤销，后面的分支会看到被污染的状态，结果少一大半。\n\n'
            '`result.append(list(current))` 里的 `list(...)` 不能省：'
            '`current` 是整个递归过程共用的一个列表，'
            '直接 append 进去，最后所有结果都指向同一个（空的）列表。'
            '这是一个非常隐蔽的 bug。\n\n'
            '排列的复杂度是 O(n! × n)：共 n! 个结果，每个复制需要 O(n)。'
        ),
        'expected_output': "[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]\n[[]]\n[[1]]",
        'hints': ['模板：标记 -> 递归 -> 撤销标记', '收集结果时要 list(current) 复制一份，否则所有结果会指向同一个列表'],
    },
    {
        'id': 'alg-043',
        'track': 'algorithm',
        'chapter_id': 115,
        'chapter_title': '回溯算法',
        'topic': '回溯算法',
        'title': 'N 皇后（回溯 + 冲突集合）',
        'difficulty': 3,
        'tags': ['回溯', '剪枝', '经典题'],
        'statement': (
            '定义函数 `count_n_queens(n)`：在 n×n 的棋盘上放 n 个皇后，'
            '要求任意两个皇后不在**同一行、同一列、同一斜线**上，返回**解的个数**。\n\n'
            '- `n = 0` 时返回 1（空棋盘算一个解）\n'
            '- `n = 1` 返回 1；`n = 2`、`n = 3` 都返回 0；`n = 4` 返回 2；`n = 8` 返回 92\n\n'
            '要求用**回溯**，一行一行地放（每行放一个，天然避免了同行冲突）：\n\n'
            '- 用三个集合记录已占用的**列** `col`、**主对角线** `row - col`、'
            '  **副对角线** `row + col`\n'
            '   （同一条主对角线上的格子 `row - col` 相同，副对角线上 `row + col` 相同）\n'
            '- 当前格子三种冲突都不占，就「加入集合 → 递归下一行 → 从集合移除」；\n'
            '- `row == n` 时说明这一组放好了，解的数量 +1。\n\n'
            '然后打印 n = 1、2、4、5、8 时的解的个数。'
        ),
        'starter_code': 'def count_n_queens(n):\n    cols = set()\n    diag1 = set()\n    diag2 = set()\n    count = 0\n    # 一行一行地放，冲突就跳过（剪枝）\n    pass\n',
        'solution': (
            "def count_n_queens(n):\n"
            "    cols = set()\n"
            "    diag1 = set()\n"
            "    diag2 = set()\n"
            "    count = 0\n"
            "\n"
            "    def backtrack(row):\n"
            "        nonlocal count\n"
            "        if row == n:\n"
            "            count += 1\n"
            "            return\n"
            "        for col in range(n):\n"
            "            if col in cols or (row - col) in diag1 or (row + col) in diag2:\n"
            "                continue\n"
            "            cols.add(col)\n"
            "            diag1.add(row - col)\n"
            "            diag2.add(row + col)\n"
            "            backtrack(row + 1)\n"
            "            cols.discard(col)\n"
            "            diag1.discard(row - col)\n"
            "            diag2.discard(row + col)\n"
            "\n"
            "    backtrack(0)\n"
            "    return count\n"
            "\n"
            "for size in (1, 2, 4, 5, 8):\n"
            "    print(size, count_n_queens(size))\n"
        ),
        'checks': [
            "assert count_n_queens(0) == 1, 'n = 0 时规定返回 1（空棋盘算一个解）'",
            "assert count_n_queens(1) == 1, '1×1 棋盘放 1 个皇后有 1 个解'",
            "assert count_n_queens(2) == 0 and count_n_queens(3) == 0, '2 和 3 无解，应返回 0，实际 %r / %r' % (count_n_queens(2), count_n_queens(3))",
            "assert count_n_queens(4) == 2, '4 皇后有 2 个解，实际 %r' % (count_n_queens(4),)",
            "assert count_n_queens(5) == 10, '5 皇后有 10 个解，实际 %r' % (count_n_queens(5),)",
            "assert count_n_queens(6) == 4, '6 皇后有 4 个解，实际 %r' % (count_n_queens(6),)",
            "assert count_n_queens(7) == 40, '7 皇后有 40 个解，实际 %r' % (count_n_queens(7),)",
            "assert count_n_queens(8) == 92, '8 皇后有 92 个解（经典答案），实际 %r' % (count_n_queens(8),)",
            "assert count_n_queens(9) == 352, '9 皇后有 352 个解，实际 %r' % (count_n_queens(9),)",
        ],
        'explanation': (
            'N 皇后是回溯 + 剪枝的典范。核心是**把冲突判断变成集合查询**：\n\n'
            '- 每行只放一个 → 天然没有「同行」冲突；\n'
            '- 用 `cols` 记录占用的列；\n'
            '- 用 `diag1` 记录 `row - col`（主对角线）；\n'
            '- 用 `diag2` 记录 `row + col`（副对角线）。\n\n'
            '为什么对角线可以这样表示？因为在同一条「↘」斜线上，'
            '行号减列号的差是固定的；在同一条「↙」斜线上，行号加列号是固定的。'
            '一个 O(1) 的集合查找就替代了「遍历前面所有皇后逐个算斜率」。\n\n'
            '```python\n'
            'if col in cols or (row - col) in diag1 or (row + col) in diag2:\n'
            '    continue                     # 冲突，剪枝\n'
            '```\n\n'
            '**剪枝**是这道题能跑得动的关键：不合法就 `continue`，'
            '根本不给它进入下一层递归的机会。n=8 时暴力枚举是 8⁸ ≈ 1600 万种，'
            '回溯只要几万次调用。\n\n'
            '常见错误：递归返回后忘了把三个集合里的元素删掉（`discard`），'
            '状态被污染，后续分支全部失配；'
            '以及 `count` 是嵌套函数里的变量，累加需要 `nonlocal count` 声明。\n\n'
            '复杂度：时间 O(n!)（剪枝后远小于这个上界）、空间 O(n)。'
        ),
        'expected_output': '1 1\n2 0\n4 2\n5 10\n8 92',
        'hints': ['三个集合分别管列、row - col、row + col，查冲突是 O(1)', '递归回去后一定把三个集合里的元素删掉，否则状态被污染'],
    },

    # ── 专题 116 综合挑战 ──────────────────────────────────
    {
        'id': 'alg-044',
        'track': 'algorithm',
        'chapter_id': 116,
        'chapter_title': '综合挑战',
        'topic': '综合挑战',
        'title': '编辑距离（二维 DP 综合）',
        'difficulty': 3,
        'tags': ['动态规划', '字符串', '二维DP'],
        'statement': (
            '定义函数 `edit_distance(word1, word2)`：返回把 `word1` 变成 `word2` 的'
            '**最少操作次数**，允许的操作有三种（每次算 1 步）：\n\n'
            '- 插入一个字符\n'
            '- 删除一个字符\n'
            '- 替换一个字符\n\n'
            '- `edit_distance("horse", "ros")` → 3\n'
            '- `edit_distance("intention", "execution")` → 5\n'
            '- 空串也要支持：`edit_distance("", "abc")` → 3\n\n'
            '要求用二维 DP：`dp[i][j]` 表示「`word1` 的前 i 个字符变成 `word2` 的前 j 个字符」'
            '的最少操作数。\n\n'
            '- 边界：`dp[i][0] = i`（删掉 i 个字符）、`dp[0][j] = j`（插入 j 个字符）\n'
            '- 转移：`word1[i-1] == word2[j-1]` 时 `dp[i][j] = dp[i-1][j-1]`；\n'
            '  否则 `dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1`\n\n'
            '然后打印三组示例的结果。'
        ),
        'starter_code': 'def edit_distance(word1, word2):\n    rows, cols = len(word1), len(word2)\n    dp = [[0] * (cols + 1) for _ in range(rows + 1)]\n    # 先填边界，再按转移方程填表\n    pass\n',
        'solution': (
            "def edit_distance(word1, word2):\n"
            "    rows = len(word1)\n"
            "    cols = len(word2)\n"
            "    dp = [[0] * (cols + 1) for _ in range(rows + 1)]\n"
            "    for i in range(rows + 1):\n"
            "        dp[i][0] = i\n"
            "    for j in range(cols + 1):\n"
            "        dp[0][j] = j\n"
            "    for i in range(1, rows + 1):\n"
            "        for j in range(1, cols + 1):\n"
            "            if word1[i - 1] == word2[j - 1]:\n"
            "                dp[i][j] = dp[i - 1][j - 1]\n"
            "            else:\n"
            "                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1\n"
            "    return dp[rows][cols]\n"
            "\n"
            "print(edit_distance('horse', 'ros'))\n"
            "print(edit_distance('intention', 'execution'))\n"
            "print(edit_distance('', 'abc'))\n"
        ),
        'checks': [
            "assert edit_distance('horse', 'ros') == 3, 'horse -> ros 最少 3 步，实际 %r' % (edit_distance('horse', 'ros'),)",
            "assert edit_distance('intention', 'execution') == 5, 'intention -> execution 最少 5 步，实际 %r' % (edit_distance('intention', 'execution'),)",
            "assert edit_distance('', '') == 0, '两个空串不需要任何操作'",
            "assert edit_distance('', 'abc') == 3, '空串变 abc 需要插入 3 次，实际 %r' % (edit_distance('', 'abc'),)",
            "assert edit_distance('abc', '') == 3, 'abc 变空串需要删除 3 次，实际 %r' % (edit_distance('abc', ''),)",
            "assert edit_distance('abc', 'abc') == 0, '完全相同的字符串不需要操作'",
            "assert edit_distance('a', 'b') == 1, '一个字符替换一次就够了'",
            "assert edit_distance('ab', 'ba') == 2, 'ab -> ba 需要 2 步（删 a 加 a，或两次替换），实际 %r' % (edit_distance('ab', 'ba'),)",
            "assert edit_distance('kitten', 'sitting') == 3, 'kitten -> sitting 是 3 步（经典例子），实际 %r' % (edit_distance('kitten', 'sitting'),)",
            "assert edit_distance('sunday', 'saturday') == 3, 'sunday -> saturday 是 3 步，实际 %r' % (edit_distance('sunday', 'saturday'),)",
            "assert edit_distance('aaa', 'a') == 2, 'aaa -> a 要删掉两个字符，实际 %r' % (edit_distance('aaa', 'a'),)",
            "assert edit_distance('abc', 'xyz') == edit_distance('xyz', 'abc') == 3, '编辑距离是对称的，实际 %r / %r' % (edit_distance('abc', 'xyz'), edit_distance('xyz', 'abc'))",
        ],
        'explanation': (
            '编辑距离是二维 DP 的「毕业题」，它的状态定义很关键：\n\n'
            '**`dp[i][j]` = 把 word1 的前 i 个字符变成 word2 的前 j 个字符所需的最少操作数。**\n\n'
            '边界为什么是 `dp[i][0] = i`、`dp[0][j] = j`？'
            '因为把任意前缀变成空串，只能全部删掉（i 次）；'
            '把空串变成任意前缀，只能全部插入（j 次）。\n\n'
            '转移方程的三个来源正好对应三种操作：\n\n'
            '| 操作 | 来源 |\n'
            '|---|---|\n'
            '| 删除 word1 的字符 | `dp[i-1][j] + 1` |\n'
            '| 插入一个字符到 word1 | `dp[i][j-1] + 1` |\n'
            '| 替换 | `dp[i-1][j-1] + 1` |\n\n'
            '当 `word1[i-1] == word2[j-1]` 时，两个字符可以「配上对」，'
            '不需要任何操作，直接抄左上角。\n\n'
            '常见错误：忘记填边界（整个表全 0，答案永远是 0）；'
            '以及下标写成 `word1[i]` / `word2[j]`——'
            '因为 `dp` 多了一行一列的边界，所以取字符时要减 1。\n\n'
            '复杂度：时间 O(m × n)、空间 O(m × n)（可优化到 O(n)）。'
        ),
        'expected_output': '3\n5\n3',
        'hints': ['先填 dp[i][0] = i 和 dp[0][j] = j 这两条边界', '字符相等抄左上角，不等取「上、左、左上」的最小值再加 1'],
    },
    {
        'id': 'alg-045',
        'track': 'algorithm',
        'chapter_id': 116,
        'chapter_title': '综合挑战',
        'topic': '综合挑战',
        'title': 'LRU 缓存（字典 + 使用顺序）',
        'difficulty': 3,
        'tags': ['设计', '哈希表', '缓存'],
        'statement': (
            '实现 `LRUCache` 类（Least Recently Used，最近最少使用缓存）：\n\n'
            '- `__init__(self, capacity)`：容量 `capacity`（`>= 1`）\n'
            '- `get(self, key)`：key 存在就返回对应的值，'
            '并把它的使用时间变成**最新**；不存在返回 `-1`\n'
            '- `put(self, key, value)`：写入或更新键值。'
            '**更新已有键也算一次使用**（要变成最新）；'
            '如果写入后**超过容量**，淘汰**最久未使用**的那个键\n\n'
            '要求 `get` 和 `put` 接近 O(1)：用「字典 + 维护使用顺序」实现。'
            '最省事的做法是用 `collections.OrderedDict` 的 `move_to_end(key)` 和 '
            '`popitem(last=False)`；用普通 dict（Python 3.7 起保持插入顺序）'
            '「先 pop 再重新赋值」也能达到同样效果。\n\n'
            '然后跑一遍这个经典序列并打印结果：\n\n'
            '```python\n'
            'cache = LRUCache(2)\n'
            'cache.put(1, 1)\n'
            'cache.put(2, 2)\n'
            'print(cache.get(1))     # 1\n'
            'cache.put(3, 3)         # 淘汰 2\n'
            'print(cache.get(2))     # -1\n'
            'print(cache.get(3))     # 3\n'
            '```'
        ),
        'starter_code': 'from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity):\n        self.capacity = capacity\n        self.data = OrderedDict()\n\n    def get(self, key):\n        pass\n\n    def put(self, key, value):\n        pass\n',
        'solution': (
            "from collections import OrderedDict\n"
            "\n"
            "class LRUCache:\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.data = OrderedDict()\n"
            "\n"
            "    def get(self, key):\n"
            "        if key not in self.data:\n"
            "            return -1\n"
            "        self.data.move_to_end(key)\n"
            "        return self.data[key]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        if key in self.data:\n"
            "            self.data.move_to_end(key)\n"
            "        self.data[key] = value\n"
            "        if len(self.data) > self.capacity:\n"
            "            self.data.popitem(last=False)\n"
            "\n"
            "cache = LRUCache(2)\n"
            "cache.put(1, 1)\n"
            "cache.put(2, 2)\n"
            "print(cache.get(1))\n"
            "cache.put(3, 3)\n"
            "print(cache.get(2))\n"
            "print(cache.get(3))\n"
            "print(cache.get(1))\n"
        ),
        'checks': [
            "_c = LRUCache(2)\n_c.put(1, 1)\n_c.put(2, 2)\nassert _c.get(1) == 1, 'put(1, 1)、put(2, 2) 之后 get(1) 应是 1，实际 %r' % (_c.get(1),)\n_c.put(3, 3)\nassert _c.get(2) == -1, '键 2 是最久未使用的，被 put(3, 3) 淘汰后 get(2) 应返回 -1，实际 %r' % (_c.get(2),)\nassert _c.get(3) == 3, '刚写入的键 3 应该还在，实际 %r' % (_c.get(3),)\nassert _c.get(1) == 1, 'get(1) 让它变成最新使用，应该还在，实际 %r' % (_c.get(1),)",
            "_c2 = LRUCache(1)\n_c2.put(1, 1)\n_c2.put(2, 2)\nassert _c2.get(1) == -1 and _c2.get(2) == 2, '容量 1 时写入新键必须淘汰旧键，实际 %r / %r' % (_c2.get(1), _c2.get(2))",
            "_c3 = LRUCache(2)\n_c3.put(1, 1)\n_c3.put(2, 2)\n_c3.get(1)\n_c3.put(1, 100)\n_c3.put(3, 3)\nassert _c3.get(1) == 100, '更新已有键后它应变成最新，不该被淘汰，实际 %r' % (_c3.get(1),)\nassert _c3.get(2) == -1, '键 2 才是被淘汰的那个，实际 %r' % (_c3.get(2),)",
            "_c4 = LRUCache(3)\nfor _i in range(10):\n    _c4.put(_i, _i * _i)\nassert _c4.get(9) == 81 and _c4.get(7) == 49 and _c4.get(8) == 64, '容量 3 时最后只应留下 7、8、9，实际 %r / %r / %r' % (_c4.get(9), _c4.get(7), _c4.get(8))\nassert _c4.get(0) == -1 and _c4.get(6) == -1, '写入 10 个键之后 0 和 6 都应该被淘汰，实际 %r / %r' % (_c4.get(0), _c4.get(6))",
            "_c5 = LRUCache(2)\n_c5.put('x', [1, 2])\nassert _c5.get('x') == [1, 2], '值可以是任意对象（比如列表）'",
            "assert LRUCache(2).get('nope') == -1, '不存在的键应返回 -1'",
            "_c6 = LRUCache(2)\n_c6.put(1, 1)\n_c6.put(2, 2)\nassert _c6.get(1) == 1\n_c6.put(3, 3)\nassert _c6.get(2) == -1 and _c6.get(1) == 1, 'get(1) 之后 1 变成了最新使用，put(3, 3) 应该淘汰 2 而不是 1，实际 %r / %r' % (_c6.get(2), _c6.get(1))",
            "_c7 = LRUCache(2)\n_c7.put(1, 1)\n_c7.put(2, 2)\n_c7.put(2, 22)\n_c7.put(3, 3)\nassert _c7.get(2) == 22, '重复写入同一个键只更新值，不该占用额外容量，实际 %r' % (_c7.get(2),)\nassert _c7.get(1) == -1, '键 1 才是被淘汰的，实际 %r' % (_c7.get(1),)",
        ],
        'explanation': (
            'LRU 的两件事要分开想：**查得快**和**知道谁最旧**。\n\n'
            '- 查得快 → 哈希表（Python 的 `dict`）：O(1)；\n'
            '- 知道谁最旧 → 维护一个「使用顺序」。\n\n'
            '`OrderedDict` 把两件事合在一起：字典的键就是使用顺序，'
            '`move_to_end(key)` 把某个键提到「最新」，'
            '`popitem(last=False)` 弹出「最旧」的那个。\n\n'
            '```python\n'
            'def get(self, key):\n'
            '    if key not in self.data:\n'
            '        return -1\n'
            '    self.data.move_to_end(key)     # 用过就变最新\n'
            '    return self.data[key]\n'
            '\n'
            'def put(self, key, value):\n'
            '    if key in self.data:\n'
            '        self.data.move_to_end(key) # 更新也算使用\n'
            '    self.data[key] = value\n'
            '    if len(self.data) > self.capacity:\n'
            '        self.data.popitem(last=False)   # 淘汰最旧的\n'
            '```\n\n'
            '三个容易写错的点：\n\n'
            '1. `put` 更新已有键时也要 `move_to_end`，否则「刚更新过的键」会被当成旧的淘汰掉；\n'
            '2. `get` 命中时也要 `move_to_end`——否则它就不算「最近使用」，'
            '这正是 LRU 与 FIFO（先进先出）的区别；\n'
            '3. 淘汰的判断用 `>`（严格超过容量），而不是 `>=`，否则容量 1 时刚存进去就被删。\n\n'
            '真实场景里 LRU 常用「哈希表 + 自己写的双向链表」实现，'
            '因为链表能在 O(1) 内把一个节点从中间挪到头部。\n\n'
            '复杂度：时间 get / put 均摊 O(1)，空间 O(capacity)。'
        ),
        'expected_output': '1\n-1\n3\n1',
        'hints': ['get 命中时要 move_to_end，否则缓存退化成先进先出', 'put 更新已有键也要 move_to_end，再判断是否超容量'],
    },
]

# __APPEND_MARKER__
