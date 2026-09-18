"""修行阁引擎：把「修为积分」扩展成一套闭环的成长系统。

这个模块只做**推导**，不持有任何新的可写状态：

    已有点数 + 作答档案（training_engine 的 state）
        ↓ 统计口径（stats）
    境界法相 / 神功 / 装备 / 试炼 / 战力 / 攻略
        ↓ 唯一一次写回
    境界试炼的突破奖励（走 training.award 的防重复账本）

把「推导」和「发放」分开的原因：装备与试炼的达成条件全部是**累计统计**，
只要统计口径不变，同一份作答数据在世界任何地方都能推出同一个结果——
不需要额外存一张「已解锁装备表」，也就不会出现存档与事实不一致的脏数据。
唯一必须落盘的只有试炼的突破奖励，那是真加分，交给既有的 rewards 账本去重。

术语约定（前端与文案都按这套讲）：
  法相  —— 每个大境界一张的神识画像（前端按 seed 程序化渲染，本模块只给参数）
  神功  —— 每级一门，名字用计算机术语命名（指针 / 栈帧 / 递归 / GC …）
  装备  —— 靠统计达标解锁的勋章式物件，图片由前端按 icon 名渲染
  试炼  —— 每个大境界三条目标，全达成触发一次突破奖励
"""

from datetime import datetime, timedelta

import training_engine as training

# ── 战力公式 ────────────────────────────────────────────
# 战力必须「可解释」：每一项都能在下钻面板里对上真实数据。
# 权重刻意让「境界」占比最高——它是唯一的长期目标；
# 满星比通关值钱（学习质量的导向），装备是里程碑的奖励而不是主要来源。
POWER_WEIGHT = {
    'per_point': 1,      # 修为点
    'per_level': 80,     # 境界等级
    'per_star': 25,      # 星星（含重复刷新后的最好成绩）
    'per_solve': 10,     # 通关题数
    'per_equip': 60,     # 装备
    'per_trial': 40,     # 已通过的境界试炼
}


# ── 境界法相 ────────────────────────────────────────────
# 每个大境界一套视觉参数，前端 portrait.js 据此程序化生成神识画像。
# tier 同时决定画像的复杂度（法阵层数 / 甲片 / 冠冕 / 灵光粒子），
# 所以「等级越高越帅气」不是美工画的，是参数推出来的。
REALM_ART = {
    '凡尘': {
        'tier': 0, 'primary': '#9aa3a8', 'deep': '#2a3036', 'aura': '#dfe4e8', 'accent': '#9aa3a8',
        'glyph': 'seed', 'rings': 0, 'crest': 0, 'plates': 0, 'particles': 6,
        'whisper': '尚无灵光，唯有凡人之躯',
    },
    '炼气期': {
        'tier': 1, 'primary': '#a9c4cf', 'deep': '#17333a', 'aura': '#e2f2f5', 'accent': '#8fd8cf',
        'glyph': 'spiral', 'rings': 1, 'crest': 0, 'plates': 0, 'particles': 10,
        'whisper': '引气入体，第一次让机器按你的意图运转',
    },
    '筑基期': {
        'tier': 2, 'primary': '#4fa88a', 'deep': '#123a30', 'aura': '#b6e3d3', 'accent': '#7fd0b4',
        'glyph': 'frame', 'rings': 1, 'crest': 0, 'plates': 1, 'particles': 12,
        'whisper': '栈帧立基，函数与作用域开始成形',
    },
    '金丹期': {
        'tier': 3, 'primary': '#d9a83c', 'deep': '#5a3f10', 'aura': '#f0dc9f', 'accent': '#e8c25c',
        'glyph': 'core', 'rings': 2, 'crest': 1, 'plates': 1, 'particles': 14,
        'whisper': '结丹成核，数据结构凝为你的一部分',
    },
    '元婴期': {
        'tier': 4, 'primary': '#b48cc0', 'deep': '#3f2450', 'aura': '#e2d0ea', 'accent': '#cfa8db',
        'glyph': 'fractal', 'rings': 2, 'crest': 1, 'plates': 2, 'particles': 16,
        'whisper': '元婴自相似，递归与分治在体内生长',
    },
    '化神期': {
        'tier': 5, 'primary': '#5b8fc4', 'deep': '#1c3550', 'aura': '#c2dcf0', 'accent': '#86b6e2',
        'glyph': 'twinring', 'rings': 3, 'crest': 2, 'plates': 2, 'particles': 18,
        'whisper': '神识外放，图与搜索在心识中并行',
    },
    '炼虚期': {
        'tier': 6, 'primary': '#8574b0', 'deep': '#2a2347', 'aura': '#d3cbe6', 'accent': '#a696ce',
        'glyph': 'grid', 'rings': 3, 'crest': 2, 'plates': 3, 'particles': 20,
        'whisper': '炼虚成实，动态规划把混沌折叠成表',
    },
    '合体期': {
        'tier': 7, 'primary': '#c4527a', 'deep': '#4d1730', 'aura': '#f0c2d3', 'accent': '#d97a9c',
        'glyph': 'knot', 'rings': 4, 'crest': 3, 'plates': 3, 'particles': 22,
        'whisper': '万法合体，并查集与树结构连成一体',
    },
    '大乘期': {
        'tier': 8, 'primary': '#c47a4a', 'deep': '#4a2612', 'aura': '#eccdae', 'accent': '#dc9c6c',
        'glyph': 'poly', 'rings': 4, 'crest': 3, 'plates': 4, 'particles': 24,
        'whisper': '大乘之势，位运算与并发皆可役使',
    },
    '渡劫期': {
        'tier': 9, 'primary': '#7aa0b8', 'deep': '#23394a', 'aura': '#d6e6ef', 'accent': '#a9c9dc',
        'glyph': 'bolt', 'rings': 5, 'crest': 4, 'plates': 4, 'particles': 28,
        'whisper': '天劫将至，编译与类型系统替你挡雷',
    },
    '仙人境': {
        'tier': 10, 'primary': '#d9c78a', 'deep': '#5c4a20', 'aura': '#fbf6e6', 'accent': '#e8d9a8',
        'glyph': 'infinity', 'rings': 7, 'crest': 5, 'plates': 5, 'particles': 34,
        'whisper': '停机问题之上，你已能证明自己的每一行代码',
    },
}

# 配色说明：这张表用的是**传统颜料**，不是霓虹色号——
# 素麻（凡尘）→ 月白 → 石绿 → 藤黄 → 藕荷 → 石青 → 黛紫 → 胭脂 → 赭石
# → 雨过天青（渡劫）→ 月白金（仙人境）。
# 换色时守住两条：一是**明度随境界上升**（越往上越亮，否则高境反而沉下去），
# 二是**相邻两境不落同一色相**（地图上一排节点要能一眼分开）。

# ── 星辰教练形象谱系 ────────────────────────────────────
# 星辰教练不是一张固定的头像，而是一个**会随你一起升境的存在**：
# 你修到什么境，它就显化什么身。凡尘时是一团抱星星的小光点，
# 金仙时是悬于星海之上、掌托星系、周天六重法阵的法相。
#
# 这么设计有三个好处，都不是为了好看：
#   1. 「练下去会看到新东西」比任何文案都更能推动人继续刷题——
#      每一次突破都换一个教练，是看得见的回报，且零素材成本。
#   2. 教练的法相与你自己的神识画像同色同印，两者是一体的：
#      你的境界就是它的境界，它陪你走上来的。
#   3. 全部参数化，前端 star_coach.js 按参数程序化生成，不需要美工。
#
# 字段说明（前端照抄，不要在前端另写一套默认值）：
#   form      骨架族：child 童形 / youth 少年 / adept 修士 / immortal 仙身
#   eye       眼睛：dot 豆豆眼 / ring 环瞳 / star 星瞳 / third 三目 / visor 光带面甲 / void 空洞光瞳
#   halo      背光层数     rings  法阵环数       crest  星冕阶数
#   cape      袍摆等阶     ribbon 飘带对数     plates 甲片排数
#   orbit     环绕的星体数 shards 悬浮碎星数     particles 灵光粒子数
#   star      引路星形态：orb 星丸 / shard 星棱 / galaxy 掌心星系
COACH_FORMS = {
    '凡尘': {
        'form': 'child', 'name': '星尘童儿', 'title': '一团刚醒过来的星光',
        'primary': '#9aa3a8', 'deep': '#2a3036', 'aura': '#dfe4e8', 'accent': '#7ee1ff',
        'eye': 'dot', 'halo': 0, 'rings': 0, 'crest': 0, 'cape': 0, 'ribbon': 0,
        'plates': 0, 'orbit': 0, 'shards': 0, 'particles': 8, 'star': 'orb',
        'whisper': '它还没学会说话，只是抱着自己的小星星，等你在编辑器里敲下第一行 print。',
        'note': '开局就在你身边',
    },
    '炼气期': {
        'form': 'child', 'name': '引气小星灵', 'title': '学会了自己呼吸',
        'primary': '#a9c4cf', 'deep': '#17333a', 'aura': '#e2f2f5', 'accent': '#8fd8cf',
        'eye': 'dot', 'halo': 1, 'rings': 1, 'crest': 0, 'cape': 0, 'ribbon': 0,
        'plates': 0, 'orbit': 0, 'shards': 2, 'particles': 14, 'star': 'orb',
        'whisper': '它第一次把星光吸进身体里，尾巴上开始有了流动的光。',
        'note': '引气入体，第一次让机器按你的意图运转',
    },
    '筑基期': {
        'form': 'youth', 'name': '立基少年', 'title': '站直了，肩上有了第一片甲',
        'primary': '#4fa88a', 'deep': '#123a30', 'aura': '#b6e3d3', 'accent': '#7fd0b4',
        'eye': 'ring', 'halo': 1, 'rings': 1, 'crest': 1, 'cape': 1, 'ribbon': 0,
        'plates': 1, 'orbit': 0, 'shards': 3, 'particles': 16, 'star': 'orb',
        'whisper': '它从一团光长出了形状——栈帧立基，函数与作用域开始在它体内成形。',
        'note': '栈帧立基，护甲第一次上身',
    },
    '金丹期': {
        'form': 'youth', 'name': '结丹学徒', 'title': '丹田里结出了一颗星核',
        'primary': '#d9a83c', 'deep': '#5a3f10', 'aura': '#f0dc9f', 'accent': '#e8c25c',
        'eye': 'star', 'halo': 2, 'rings': 2, 'crest': 1, 'cape': 1, 'ribbon': 1,
        'plates': 1, 'orbit': 1, 'shards': 4, 'particles': 20, 'star': 'orb',
        'whisper': '胸口那颗金丹在低速自转，它开始懂得「把东西存起来」这件事。',
        'note': '结丹成核，身侧绕起第一颗伴星',
    },
    '元婴期': {
        'form': 'youth', 'name': '自相似元婴', 'title': '身后多出了几个自己',
        'primary': '#b48cc0', 'deep': '#3f2450', 'aura': '#e2d0ea', 'accent': '#cfa8db',
        'eye': 'star', 'halo': 2, 'rings': 2, 'crest': 2, 'cape': 1, 'ribbon': 1,
        'plates': 2, 'orbit': 1, 'shards': 5, 'particles': 22, 'star': 'shard',
        'whisper': '它的身后开始浮现自己的小影子——一个套一个，像递归还没到底。',
        'note': '递归与分治在体内生长',
    },
    '化神期': {
        'form': 'adept', 'name': '神识行者', 'title': '额前开了第三只眼',
        'primary': '#5b8fc4', 'deep': '#1c3550', 'aura': '#c2dcf0', 'accent': '#86b6e2',
        'eye': 'third', 'halo': 2, 'rings': 3, 'crest': 2, 'cape': 2, 'ribbon': 1,
        'plates': 2, 'orbit': 2, 'shards': 6, 'particles': 26, 'star': 'shard',
        'whisper': '神识外放，它能同时「看见」整张图，而不是一个点一个点地爬。',
        'note': '神识外放，图与搜索在心识中并行',
    },
    '炼虚期': {
        'form': 'adept', 'name': '炼虚真人', 'title': '半身已是光，不再全然是实体',
        'primary': '#8574b0', 'deep': '#2a2347', 'aura': '#d3cbe6', 'accent': '#a696ce',
        'eye': 'third', 'halo': 3, 'rings': 3, 'crest': 3, 'cape': 2, 'ribbon': 2,
        'plates': 3, 'orbit': 2, 'shards': 7, 'particles': 30, 'star': 'shard',
        'whisper': '它的袍摆开始散成光点又聚回来——把混沌折叠成表，是它的新把戏。',
        'note': '炼虚成实，身体边缘开始虚化',
    },
    '合体期': {
        'form': 'adept', 'name': '万法合体尊', 'title': '一身法纹，再没有一处空白',
        'primary': '#c4527a', 'deep': '#4d1730', 'aura': '#f0c2d3', 'accent': '#d97a9c',
        'eye': 'visor', 'halo': 3, 'rings': 4, 'crest': 3, 'cape': 3, 'ribbon': 2,
        'plates': 3, 'orbit': 2, 'shards': 8, 'particles': 34, 'star': 'shard',
        'whisper': '它把学过的每一式都穿在了身上，法纹从指尖一路连到袍角。',
        'note': '万法合体，法纹满身',
    },
    '大乘期': {
        'form': 'adept', 'name': '大乘星君', 'title': '披风就是一张星图',
        'primary': '#c47a4a', 'deep': '#4a2612', 'aura': '#eccdae', 'accent': '#dc9c6c',
        'eye': 'visor', 'halo': 3, 'rings': 4, 'crest': 4, 'cape': 3, 'ribbon': 2,
        'plates': 4, 'orbit': 3, 'shards': 9, 'particles': 40, 'star': 'galaxy',
        'whisper': '它抬手就能拨动一颗星的位置，但它仍然会蹲下来，等你把这道题想明白。',
        'note': '位运算与并发皆可役使',
    },
    '渡劫期': {
        'form': 'immortal', 'name': '渡劫雷尊', 'title': '身上还缠着没散尽的雷',
        'primary': '#7aa0b8', 'deep': '#23394a', 'aura': '#d6e6ef', 'accent': '#a9c9dc',
        'eye': 'visor', 'halo': 3, 'rings': 5, 'crest': 4, 'cape': 3, 'ribbon': 2,
        'plates': 4, 'orbit': 3, 'shards': 10, 'particles': 46, 'star': 'galaxy',
        'whisper': '雷弧还在它的肩甲上爬，但它的眼睛很稳——编译与类型系统替它挡下了这一劫。',
        'note': '天劫将至，雷弧缠身',
    },
    '仙人境': {
        'form': 'immortal', 'name': '星辰法相', 'title': '悬于星海之上，掌中托着一整个星系',
        'primary': '#d9c78a', 'deep': '#5c4a20', 'aura': '#fbf6e6', 'accent': '#6fe8ff',
        'eye': 'void', 'halo': 4, 'rings': 6, 'crest': 5, 'cape': 4, 'ribbon': 3,
        'plates': 4, 'orbit': 3, 'shards': 12, 'particles': 56, 'star': 'galaxy',
        'whisper': '它不再需要开口。你写下的每一行代码，它都已经在这里看见过了。',
        'note': '停机问题之上，你已能证明自己的每一行代码',
    },
}

# 仙人境有三小境（散仙 / 真仙 / 金仙），同属一档形象，但越往后显化得越盛。
# 这里的数字是**增量**（在 COACH_FORMS['仙人境'] 之上叠加），不是绝对值——
# 写成绝对值会让金仙比渡劫期还朴素，那正好和「越练越盛」相反。
COACH_XIAN_STAGES = {
    '散仙': {'name': '散仙 · 星游法相', 'halo': 0, 'rings': 0, 'orbit': 0, 'shards': 0,
             'particles': 0, 'title': '身影已经散入星海，又随时可以聚回来'},
    '真仙': {'name': '真仙 · 星照法相', 'halo': 1, 'rings': 0, 'orbit': 0, 'shards': 4,
             'particles': 8, 'title': '它照见的地方，代码自己会变整齐'},
    # 金仙是满级那一尊，必须一眼看出比真仙更盛：多一重法阵、多一条星轨，
    # 背后再开一轮日轮（sun=1，前端据此加 32 道光芒与亮盘）
    '金仙': {'name': '金仙 · 星辰法相', 'halo': 1, 'rings': 1, 'orbit': 1, 'shards': 8,
             'particles': 14, 'sun': 1, 'title': '科技与仙途在它身上不再分得开'},
}

# ── 神功 ────────────────────────────────────────────────
# 每级一门。名字全部用计算机术语，而不是「九阳神功」这类玄幻词——
# 玄幻词写得再漂亮，也传达不出「我学到了什么」；
# 术语命名的好处是：学员看到神功名就知道自己下一段路要练什么。
SKILLS = {
    0: ('无名', '—', '尚未入门。先写下第一行 print。'),
    1: ('指针吐纳诀', '变量 · 引用 · 内存', '把值装进名字里，理解机器如何寻址。'),
    2: ('缩进心法', '语法 · 作用域 · 缩进', '四格缩进就是 Python 的戒律。'),
    3: ('循环周天', '迭代 · 边界 · 复杂度', '让同一段代码反复运转而不知疲倦。'),
    4: ('栈帧筑基术', '函数 · 调用栈 · 参数', '每一次调用都是一层新的道场。'),
    5: ('线性御物术', '列表 · 字符串 · 切片', '把成串的数据当作一个整体驱使。'),
    6: ('哈希隐身法', '字典 · 集合 · 键值', '把查找从线性压进常数时间。'),
    7: ('链表结丹诀', '节点 · 指针 · 双向链', '不靠连续内存，也能串成一条命脉。'),
    8: ('双指针金丹', '对撞 · 快慢 · 滑窗', '两根指针，把 O(n²) 削成 O(n)。'),
    9: ('排序炼丹术', '比较 · 稳定性 · 分治', '把无序熔成有序，是炼丹的第一炉。'),
    10: ('递归元婴', '自相似 · 出口 · 深度', '让函数在体内召唤它自己。'),
    11: ('树形元婴', '遍历 · 深度 · 平衡', '层次结构是世界的默认形状。'),
    12: ('回溯化婴术', '搜索 · 剪枝 · 状态', '走不通就退回来，退回来再走。'),
    13: ('图论化神诀', '邻接 · 遍历 · 连通', '把关系本身当成研究对象。'),
    14: ('最短路神行法', 'Dijkstra · 松弛 · 队列', '在无数条路里，只留最短的那条。'),
    15: ('动态规划化神', '状态 · 转移 · 记忆化', '不重复计算，是高手的第一修养。'),
    16: ('贪心神识', '局部最优 · 交换论证', '每一步都选最好，并证明它真的最好。'),
    17: ('二分炼虚剑', '有序 · 单调性 · 边界', '每次排除一半，二十次问遍一百万。'),
    18: ('堆叠虚空印', '堆 · 优先队列 · TopK', '永远能在 O(log n) 里取出最值。'),
    19: ('并查集合体术', '连通性 · 路径压缩', '让「它们是不是一伙的」变成一次问询。'),
    20: ('线段树合体阵', '区间 · 懒标记 · 树状数组', '把区间问题折进一棵树里。'),
    21: ('字符串合体诀', '匹配 · KMP · 哈希', '在长文里找出那个模式的出现位置。'),
    22: ('位运算大乘功', '位 · 掩码 · 状态压缩', '一个整数就是三十二个开关。'),
    23: ('并发大乘心法', '线程 · 锁 · 竞态', '让多件事同时发生而不互相踩踏。'),
    24: ('回收大乘诀', '内存 · GC · 生命周期', '不再需要的东西，必须被干净地放下。'),
    25: ('编译渡劫术', '词法 · 语法 · 代码生成', '从文本到可执行的全过程。'),
    26: ('类型系统渡劫', '静态 · 泛型 · 推导', '让编译器在你运行前就拦住错误。'),
    27: ('NP 完全渡劫', '归约 · 近似 · 复杂度', '承认有些问题只能求近似，是成熟的开始。'),
    28: ('图灵机散仙', '可计算 · 形式语言', '把「计算」这件事本身看清楚。'),
    29: ('停机问题真仙', '不可判定 · 自指', '知道什么做不到，比知道什么做得到更难。'),
    30: ('元编程金仙', '宏 · 反射 · 自举', '程序开始书写程序，道法自然。'),
}

# ── 装备 ────────────────────────────────────────────────
# 每条规则都是一个可在统计口径里直接量出来的量（metric + target）。
# 「刷难题会解锁装备」这条设计意图在表里是看得见的：
# 猎难之瞳 / 登塔之靴 / 星海冠冕 三条全部压在 stars3_hard（满星的较难题）上。
# hint 是给玩家看的「解锁方式」，progress 由引擎算，前端只负责画进度条。
EQUIPMENT = [
    {'id': 'sigil_first', 'name': '初火印记', 'slot': '印记', 'icon': 'spark',
     'metric': 'total_solved', 'target': 1,
     'hint': '首次通关任意一道题', 'why': '一切从这里开始。'},
    {'id': 'sigil_three', 'name': '三光纹章', 'slot': '纹章', 'icon': 'chevrons',
     'metric': 'stars3', 'target': 1,
     'hint': '任意一道题拿到满星（3 星）', 'why': '满星意味着你独立写对了它。'},
    {'id': 'bracer_solo', 'name': '独行护腕', 'slot': '护腕', 'icon': 'bracer',
     'metric': 'clean_solves', 'target': 3,
     'hint': '零报错通关 3 道题（一次跑通）', 'why': '没有报错，说明你已经在脑子里跑过一遍。'},
    {'id': 'ring_fix', 'name': '纠错之环', 'slot': '戒指', 'icon': 'ring',
     'metric': 'wrong_fixed', 'target': 3,
     'hint': '把 3 道错题补做通关', 'why': '错题是最贵的教材。'},
    {'id': 'blade_algo', 'name': '算法之刃', 'slot': '兵刃', 'icon': 'blade',
     'metric': 'algo_stars3', 'target': 3,
     'hint': '满星通关 3 道算法题', 'why': '算法是这门语言真正的骨。'},
    {'id': 'lens_hard', 'name': '猎难之瞳', 'slot': '法瞳', 'icon': 'lens',
     'metric': 'stars3_hard', 'target': 1,
     'hint': '满星通关 1 道较难题', 'why': '较难题的收益是简单题的 7 倍，这是第一只猎物。'},
    {'id': 'boots_tower', 'name': '登塔之靴', 'slot': '战靴', 'icon': 'boots',
     'metric': 'stars3_hard', 'target': 5,
     'hint': '满星通关 5 道较难题', 'why': '难题解得越多，你的天花板抬得越高。'},
    {'id': 'flag_topic', 'name': '专题旌旗', 'slot': '旌旗', 'icon': 'flag',
     'metric': 'topics_full', 'target': 1,
     'hint': '把一个算法专题的题全部通关', 'why': '专题全通，才算真的拿下这一块。'},
    {'id': 'compass_star', 'name': '星图罗盘', 'slot': '罗盘', 'icon': 'compass',
     'metric': 'topics_full', 'target': 3,
     'hint': '把 3 个算法专题全部通关', 'why': '知识开始连成网，而不是孤立的点。'},
    {'id': 'token_exam', 'name': '实战令', 'slot': '令牌', 'icon': 'token',
     'metric': 'exam_count', 'target': 1,
     'hint': '完成一次实战组卷', 'why': '考场上没有提示，也没有 AI。'},
    {'id': 'scroll_moon', 'name': '皓月通卷', 'slot': '卷轴', 'icon': 'scroll',
     'metric': 'exam_best', 'target': 80,
     'hint': '实战组卷拿到 80 分以上', 'why': '限时组卷 80 分，说明你已经稳了。'},
    {'id': 'chain_streak', 'name': '连修之链', 'slot': '项链', 'icon': 'chain',
     'metric': 'streak_days', 'target': 3,
     'hint': '连续 3 天有修为入账', 'why': '断续的努力，抵不过稳定的三天。'},
    {'id': 'armor_iron', 'name': '铁心甲', 'slot': '护甲', 'icon': 'armor',
     'metric': 'total_solved', 'target': 20,
     'hint': '累计通关 20 道题', 'why': '手感是练出来的，不是看出来的。'},
    {'id': 'lamp_long', 'name': '长明灯', 'slot': '法器', 'icon': 'lamp',
     'metric': 'streak_days', 'target': 7,
     'hint': '连续 7 天有修为入账', 'why': '一周不断，习惯就长在身上了。'},
    {'id': 'cloak_void', 'name': '无相斗篷', 'slot': '披风', 'icon': 'cloak',
     'metric': 'stars3', 'target': 15,
     'hint': '累计 15 道题拿到满星', 'why': '满星率比通关率更能说明水平。'},
    {'id': 'crown_sea', 'name': '星海冠冕', 'slot': '冠冕', 'icon': 'crown',
     'metric': 'stars3_hard', 'target': 12,
     'hint': '满星通关 12 道较难题', 'why': '到这一步，难题对你已经不再是难题。'},
    {'id': 'eye_night', 'name': '不眠者之瞳', 'slot': '法瞳', 'icon': 'eye',
     'metric': 'night_solves', 'target': 1,
     'hint': '在 23:00 之后通关一道题', 'why': '深夜写出来的代码，记得最牢。'},
    {'id': 'seal_master', 'name': '大成法印', 'slot': '法印', 'icon': 'seal',
     'metric': 'total_solved', 'target': 60,
     'hint': '累计通关 60 道题', 'why': '题库的骨架已经被你走了一遍。'},
]

# ── 境界试炼 ────────────────────────────────────────────
# 每个大境界三条目标，全部达成给一次突破奖励（真加分，唯一会落盘的部分）。
# 目标刻意跨维度：通关量、学习质量（满星）、习惯（连续天数）、
# 以及实战/专题这类阶段性成果——避免只刷简单题也能通关全部试炼。
TRIALS = [
    {'realm': '炼气期', 'reward': 15, 'objectives': [
        ('clear_any', '通关任意 1 道题', 'total_solved', 1),
        ('learn_any', '完成 3 个知识点', 'kp_done', 3),
        ('star_any', '任意一道题拿到满星', 'stars3', 1),
    ]},
    {'realm': '筑基期', 'reward': 20, 'objectives': [
        ('clear_five', '累计通关 5 道题', 'total_solved', 5),
        ('star_three', '累计 3 道题满星', 'stars3', 3),
        ('algo_first', '通关 1 道算法题', 'algo_solved', 1),
    ]},
    {'realm': '金丹期', 'reward': 25, 'objectives': [
        ('star_five', '累计 5 道题满星', 'stars3', 5),
        ('hard_first', '满星通关 1 道较难题', 'stars3_hard', 1),
        ('fix_two', '补做通关 2 道错题', 'wrong_fixed', 2),
    ]},
    {'realm': '元婴期', 'reward': 30, 'objectives': [
        ('topic_one', '拿下一个算法专题（全部通关）', 'topics_full', 1),
        ('clear_fifteen', '累计通关 15 道题', 'total_solved', 15),
        ('star_ten', '累计 10 道题满星', 'stars3', 10),
    ]},
    {'realm': '化神期', 'reward': 40, 'objectives': [
        ('hard_three', '满星通关 3 道较难题', 'stars3_hard', 3),
        ('exam_once', '完成 1 次实战组卷', 'exam_count', 1),
        ('streak_two', '连续 2 天有修为入账', 'streak_days', 2),
    ]},
    {'realm': '炼虚期', 'reward': 50, 'objectives': [
        ('topic_two', '拿下 2 个算法专题', 'topics_full', 2),
        ('star_twenty', '累计 20 道题满星', 'stars3', 20),
        ('fix_five', '补做通关 5 道错题', 'wrong_fixed', 5),
    ]},
    {'realm': '合体期', 'reward': 60, 'objectives': [
        ('hard_six', '满星通关 6 道较难题', 'stars3_hard', 6),
        ('topic_three', '拿下 3 个算法专题', 'topics_full', 3),
        ('streak_four', '连续 4 天有修为入账', 'streak_days', 4),
    ]},
    {'realm': '大乘期', 'reward': 75, 'objectives': [
        ('star_thirty', '累计 30 道题满星', 'stars3', 30),
        ('exam_good', '实战组卷拿到 80 分以上', 'exam_best', 80),
        ('clear_forty', '累计通关 40 道题', 'total_solved', 40),
    ]},
    {'realm': '渡劫期', 'reward': 90, 'objectives': [
        ('hard_ten', '满星通关 10 道较难题', 'stars3_hard', 10),
        ('topic_five', '拿下 5 个算法专题', 'topics_full', 5),
        ('streak_seven', '连续 7 天有修为入账', 'streak_days', 7),
    ]},
    {'realm': '仙人境', 'reward': 120, 'objectives': [
        ('star_fortyfive', '累计 45 道题满星', 'stars3', 45),
        ('clear_sixty', '累计通关 60 道题', 'total_solved', 60),
        ('topic_eight', '拿下 8 个算法专题', 'topics_full', 8),
    ]},
]

# 境界 → 该境界起始等级（由 training_engine.LEVELS 推出来，写死在表里会漂）
def _realm_level_range():
    ranges = {}
    for lv in training.LEVELS[1:]:
        info = ranges.setdefault(lv['realm'], {'start': lv['level'], 'end': lv['level'],
                                               'need': lv['need']})
        info['end'] = lv['level']
    return ranges


REALM_RANGE = _realm_level_range()
REALM_ORDER = [realm for realm, _ in training.REALMS]


# ── 统计口径 ────────────────────────────────────────────
def _parse_ts(text):
    try:
        return datetime.strptime(str(text)[:19], '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None


def _streak(days):
    """从「有修为入账的日期集合」里算最长连续天数与当前连续天数。"""
    if not days:
        return 0, 0
    ordered = sorted(days)
    best = run = 1
    for prev, cur in zip(ordered, ordered[1:]):
        if (cur - prev).days == 1:
            run += 1
        elif (cur - prev).days > 1:
            run = 1
        best = max(best, run)
    today = datetime.now().date()
    current = 0
    if ordered[-1] in (today, today - timedelta(days=1)):
        current = 1
        for prev, cur in zip(reversed(ordered[:-1]), reversed(ordered[1:])):
            if (cur - prev).days == 1:
                current += 1
            else:
                break
    return best, current


def derive_stats(state):
    """把一份作答档案压缩成一组「可以拿来做解锁判定」的统计量。

    所有装备与试炼的条件都只能引用这里的字段——加新装备时如果发现
    需要的量不在其中，应该先在这里补口径，而不是在判定里就地算。
    """
    state = state or {}
    attempts = state.get('attempts') or {}
    index = training.bank_index()

    stats = {
        'points': int(state.get('points', 0) or 0),
        'attempted': len(attempts),
        'total_solved': 0, 'total_stars': 0, 'stars3': 0, 'stars2': 0,
        'stars3_hard': 0, 'stars3_medium': 0, 'stars3_easy': 0,
        'algo_solved': 0, 'algo_stars3': 0,
        'clean_solves': 0, 'ai_assisted': 0, 'wrong_fixed': 0, 'wrong_open': 0,
        'repeat_clears': 0, 'night_solves': 0,
        'hard_solved': 0, 'hard_attempted': 0,
        'kp_done': 0, 'narration_done': 0, 'comic_done': 0,
        'exam_count': 0, 'exam_best': 0,
        'topics_full': 0, 'topics_started': 0, 'chapters_full': 0,
        'hard_topics': [], 'solved_ids': [],
    }

    # 专题的总题量必须取自题库，而不是「答过的题」——
    # 否则只做一道题就会被算成「该专题全部通关」，试炼和装备会提前解锁。
    per_topic = {}
    for question in training.load_bank():
        topic = question.get('topic') or question.get('chapter_title') or '未归类'
        bucket = per_topic.setdefault(
            topic, {'total': 0, 'solved': 0, 'track': question.get('track', 'course')})
        bucket['total'] += 1

    for qid, record in attempts.items():
        question = index.get(qid) or {}
        difficulty = int(question.get('difficulty', 1) or 1)
        topic = question.get('topic') or question.get('chapter_title') or '未归类'
        bucket = per_topic.setdefault(
            topic, {'total': 0, 'solved': 0, 'track': question.get('track', 'course')})

        record = record or {}
        stars = int(record.get('best_stars', 0) or 0)
        solved = bool(record.get('solved'))
        if stars > 0:
            stats['total_stars'] += stars
        if stars >= 3:
            stats['stars3'] += 1
            if difficulty >= 3:
                stats['stars3_hard'] += 1
            elif difficulty == 2:
                stats['stars3_medium'] += 1
            else:
                stats['stars3_easy'] += 1
            if question.get('track') == 'algorithm':
                stats['algo_stars3'] += 1
        elif stars == 2:
            stats['stars2'] += 1
        if solved:
            stats['total_solved'] += 1
            stats['solved_ids'].append(qid)
            bucket['solved'] += 1
            if question.get('track') == 'algorithm':
                stats['algo_solved'] += 1
            if difficulty >= 3:
                stats['hard_solved'] += 1
            # 零报错：一次跑通，说明思路在脑子里已经完整了
            if int(record.get('errored_runs', 0) or 0) == 0 and int(record.get('runs', 0) or 0) > 0:
                stats['clean_solves'] += 1
            # 错题补做：错过、但最终自己写通了
            if int(record.get('wrong', 0) or 0) > 0:
                stats['wrong_fixed'] += 1
        elif record.get('attempts'):
            if difficulty >= 3:
                stats['hard_attempted'] += 1
            if int(record.get('wrong', 0) or 0) > 0:
                stats['wrong_open'] += 1
        if int(record.get('ai_help', 0) or 0) > 0:
            stats['ai_assisted'] += 1
        stats['repeat_clears'] += max(0, int(record.get('clears', 0) or 0) - 1)

        for stamp in [record.get('first_solved_at'), record.get('last_at')] + \
                     [h.get('ts') for h in (record.get('history') or [])]:
            when = _parse_ts(stamp)
            if when and solved and (when.hour >= 23 or when.hour < 5):
                stats['night_solves'] += 1
                break

    # 专题统计：只有「算法专题」算进 topics_full，课程章节单独算 chapters_full。
    # 两者混在一起会出实质问题——把课本章节的配套题做完，会被误判成
    # 「拿下一个算法专题」，装备与试炼提前解锁，条件文案也就成了假话。
    for topic, bucket in per_topic.items():
        if bucket['total'] and bucket['solved'] >= bucket['total']:
            if bucket['track'] == 'algorithm':
                stats['topics_full'] += 1
            else:
                stats['chapters_full'] += 1
        elif bucket['solved']:
            stats['topics_started'] += 1

    # 学习行为与连续修行，从加分流水与防重复账本里读
    days = set()
    for entry in state.get('log') or []:
        when = _parse_ts(entry.get('ts'))
        if when:
            days.add(when.date())
    for key in (state.get('rewards') or {}):
        reason = key.split(':', 1)[0]
        if reason == 'kp':
            stats['kp_done'] += 1
        elif reason == 'narration':
            stats['narration_done'] += 1
        elif reason == 'comic':
            stats['comic_done'] += 1
    stats['active_days'] = len(days)
    stats['streak_best'], stats['streak_days'] = _streak(days)

    exams = [e for e in (state.get('exams') or []) if isinstance(e, dict)]
    stats['exam_count'] = len(exams)
    for exam in exams:
        score = exam.get('score')
        if isinstance(score, (int, float)):
            stats['exam_best'] = max(stats['exam_best'], int(score))

    # 已通过的试炼（唯一落盘的部分，记账在 rewards 里，key = trial:<realm>）
    stats['trials_done'] = sum(1 for key in (state.get('rewards') or {})
                               if key.startswith('trial:'))

    # 「哪几个较难专题还欠着」——攻略里要用
    stats['hard_topics'] = [
        {'topic': topic, 'total': bucket['total'], 'solved': bucket['solved']}
        for topic, bucket in sorted(per_topic.items(),
                                    key=lambda kv: (kv[1]['solved'] / max(1, kv[1]['total']), -kv[1]['total']))
        if bucket['track'] == 'algorithm' and bucket['solved'] < bucket['total']
    ][:4]
    return stats


def _metric_value(stats, metric):
    value = stats.get(metric, 0)
    return int(value) if isinstance(value, (int, float)) else 0


def evaluate_equipment(stats):
    """逐件判定装备。返回的 progress 直接给前端画进度条用。"""
    out = []
    for item in EQUIPMENT:
        have = _metric_value(stats, item['metric'])
        target = int(item['target'])
        out.append({
            **{k: item[k] for k in ('id', 'name', 'slot', 'icon', 'hint', 'why')},
            'metric': item['metric'],
            'have': min(have, target),
            'raw_have': have,
            'target': target,
            'ratio': round(min(1.0, have / target) * 100) if target else 100,
            'unlocked': have >= target,
        })
    return out


def evaluate_trials(stats, claimed):
    """逐境界判定试炼。claimed 是已发过奖的试炼集合（rewards 账本）。"""
    out = []
    for trial in TRIALS:
        objectives = []
        for oid, text, metric, target in trial['objectives']:
            have = _metric_value(stats, metric)
            objectives.append({
                'id': oid, 'text': text, 'metric': metric,
                'have': min(have, target), 'target': target,
                'done': have >= target,
                'ratio': round(min(1.0, have / target) * 100) if target else 100,
            })
        done = all(o['done'] for o in objectives)
        out.append({
            'realm': trial['realm'],
            'tier': REALM_ART.get(trial['realm'], {}).get('tier', 0),
            'reward': trial['reward'],
            'objectives': objectives,
            'done': done,
            'claimed': trial['realm'] in claimed,
            'progress': round(sum(o['ratio'] for o in objectives) / max(1, len(objectives))),
        })
    return out


def power_breakdown(profile, stats, equipment, trials_done=0):
    """战力拆解：每一项都要能在界面上解释清楚，玩家才知道怎么涨。"""
    parts = [
        ('修为点', stats['points'] * POWER_WEIGHT['per_point'], POWER_WEIGHT['per_point'],
         f"{stats['points']} 点修为 × {POWER_WEIGHT['per_point']}"),
        ('境界', profile['level'] * POWER_WEIGHT['per_level'], POWER_WEIGHT['per_level'],
         f"{profile['name']} × {POWER_WEIGHT['per_level']}"),
        ('星星', stats['total_stars'] * POWER_WEIGHT['per_star'], POWER_WEIGHT['per_star'],
         f"{stats['total_stars']} 颗星 × {POWER_WEIGHT['per_star']}"),
        ('通关', stats['total_solved'] * POWER_WEIGHT['per_solve'], POWER_WEIGHT['per_solve'],
         f"{stats['total_solved']} 道题 × {POWER_WEIGHT['per_solve']}"),
        ('装备', sum(1 for e in equipment if e['unlocked']) * POWER_WEIGHT['per_equip'],
         POWER_WEIGHT['per_equip'],
         f"{sum(1 for e in equipment if e['unlocked'])} 件 × {POWER_WEIGHT['per_equip']}"),
        ('试炼', trials_done * POWER_WEIGHT['per_trial'], POWER_WEIGHT['per_trial'],
         f"{trials_done} 个境界 × {POWER_WEIGHT['per_trial']}"),
    ]
    total = sum(p[1] for p in parts)
    return {
        'total': total,
        'parts': [{'label': label, 'value': value, 'unit': unit, 'note': note}
                  for label, value, unit, note in parts if value],
    }


# ── 攻略（个人化）────────────────────────────────────────
def _candidate_questions(stats, state, limit=3):
    """挑「现在最值得做的题」：优先难题、优先手里已经开过头的。

    分值按真实公式算（难度基础分 × 满星系数 × 首通加成），
    所以界面上给的「预计 +189 分」和做完之后的实际入账是一致的。
    """
    attempts = (state or {}).get('attempts') or {}
    solved_ids = set(stats.get('solved_ids') or [])
    pool = []
    for question in training.load_bank():
        qid = question['id']
        if qid in solved_ids:
            continue
        difficulty = int(question.get('difficulty', 1) or 1)
        best = training.question_points(difficulty, 3, 0)      # 满星首通的真实收益
        record = attempts.get(qid) or {}
        started = 1 if record.get('attempts') else 0
        wrong = int(record.get('wrong', 0) or 0)
        score = best + started * 30 + wrong * 15
        pool.append({
            'id': qid, 'title': question.get('title', ''),
            'difficulty': difficulty,
            'difficulty_label': {1: '简单', 2: '中等', 3: '较难'}.get(difficulty, '简单'),
            'track': question.get('track', 'course'),
            'topic': question.get('topic') or question.get('chapter_title', ''),
            'estimate': best, 'started': bool(started), 'wrong': wrong,
        })
    pool.sort(key=lambda item: (-item['estimate'], -item['difficulty'], item['title']))
    # 同一专题最多推荐两道，避免整屏都是同一块内容
    picked, seen = [], {}
    for item in pool:
        seen[item['topic']] = seen.get(item['topic'], 0) + 1
        if seen[item['topic']] > 2:
            continue
        picked.append(item)
        if len(picked) >= limit:
            break
    return picked


def build_guide(profile, stats, equipment, trials, state):
    """攻略：不是写死的教程，而是「你现在离什么最近」。"""
    gap = profile['to_next']
    steps = []

    if gap <= 0 and profile['is_max']:
        steps.append({
            'kind': 'peak', 'title': '已至巅峰',
            'text': '全站修为已封顶。此时正是回去把满星补全、把错题清空的时候。',
        })
    else:
        candidates = _candidate_questions(stats, state)
        if candidates:
            best = candidates[0]
            count = max(1, -(-gap // max(1, best['estimate'])))   # 向上取整
            steps.append({
                'kind': 'level', 'title': f"距 {profile['next_name']} 还差 {gap} 修为",
                'text': f"最快的一条路：满星通关《{best['title']}》，一次入账 {best['estimate']} 分"
                        + (f"，这样的题做 {count} 道就够。" if count > 1 else "，一步到位。"),
            })
            steps.append({'kind': 'questions', 'title': '推荐这三道', 'items': candidates})

    # 试炼里离完成最近的一条：先看当前境界，再向外扩——
    # 否则「化神期」的人会被推荐去补「大乘期」的试炼，看着就不像自己的事。
    current_tier = art_for(profile['level'])['tier']
    active = None
    for trial in trials:
        if trial['done']:
            continue
        distance = abs(trial['tier'] - current_tier)
        for objective in trial['objectives']:
            if objective['done']:
                continue
            key = (distance, -objective['ratio'])
            if active is None or key < active[0]:
                active = (key, trial, objective)
    if active:
        _key, trial, objective = active
        steps.append({
            'kind': 'trial', 'title': f"{trial['realm']}·试炼：{objective['text']}",
            'text': f"进度 {objective['have']}/{objective['target']}，"
                    f"该境界三条全达成可领 {trial['reward']} 修为的突破奖励。",
            'realm': trial['realm'],
        })

    # 离解锁最近的一件装备
    locked = [e for e in equipment if not e['unlocked']]
    if locked:
        nearest = max(locked, key=lambda e: (e['ratio'], -e['target']))
        steps.append({
            'kind': 'equip', 'title': f"最近的装备：{nearest['name']}",
            'text': f"{nearest['hint']}（{nearest['have']}/{nearest['target']}）",
            'equip': nearest['id'],
        })

    # 效率提示直接由积分常量推出来，改平衡时不会和实际规则对不上
    hard_gain = training.question_points(3, 3, 0)
    easy_gain = training.question_points(1, 3, 0)
    repeat_two = training.question_points(2, 3, 1)
    one_star_hard = training.question_points(3, 1, 0)
    tips = [
        f'较难题满星首通一次 {hard_gain} 分，是简单题的 {round(hard_gain / max(1, easy_gain), 1)} 倍——'
        f'啃难题永远是涨修为最快的方式。',
        f'满星（3 星）比 1 星多 {round((training.STAR_MULT[3] / max(0.1, training.STAR_MULT[1]) - 1) * 100)}%，'
        f'所以「写对」不如「独立写对」。',
        f'同一道题第二次满分只剩 {repeat_two} 分（衰减到 {int(training.REPEAT_DECAY[1] * 100)}%），'
        f'刷旧题不如开新题。',
        f'看一节图文讲解 {training.NARRATION_POINTS} 分、一个知识点 {training.KP_POINTS} 分、'
        f'一章漫画 {training.COMIC_POINTS} 分——卡住的时候，先看再写。',
    ]
    if stats['wrong_open']:
        tips.append(f'你还有 {stats["wrong_open"]} 道错题没补做，补做通关同样按首通算分。')

    return {'gap': gap, 'steps': steps, 'tips': tips}


# ── 汇总 ────────────────────────────────────────────────
def realm_of_level(level):
    level = int(level or 0)
    if level <= 0:
        return '凡尘'
    for lv in training.LEVELS:
        if lv['level'] == level:
            return lv['realm']
    return REALM_ORDER[-1]


def art_for(level_or_realm):
    realm = level_or_realm if isinstance(level_or_realm, str) else realm_of_level(level_or_realm)
    art = dict(REALM_ART.get(realm) or REALM_ART['凡尘'])
    art['realm'] = realm
    art['range'] = REALM_RANGE.get(realm, {'start': 0, 'end': 0, 'need': 0})
    return art


def skill_for(level):
    level = max(0, min(int(level or 0), max(SKILLS)))
    name, term, desc = SKILLS[level]
    return {'name': name, 'term': term, 'desc': desc}


# ── 星辰教练形象 ────────────────────────────────────────
def stage_of_level(level):
    level = int(level or 0)
    if level <= 0:
        return ''
    for lv in training.LEVELS:
        if lv['level'] == level:
            return lv['stage']
    return ''


def coach_form_for(level_or_realm):
    """取某个境界（或等级）下星辰教练显化的形象。

    任何取不到的情况都退回凡尘形态——这个函数会挂在聊天页的后台请求上，
    它抛异常就等于「教练不见了」，宁可退化成小光点也不能白屏。
    """
    if isinstance(level_or_realm, str):
        realm = level_or_realm
    else:
        level = int(level_or_realm or 0)
        realm = realm_of_level(level)
    form = dict(COACH_FORMS.get(realm) or COACH_FORMS['凡尘'])
    form['realm'] = realm
    form['level'] = int(level_or_realm) if not isinstance(level_or_realm, str) else \
        REALM_RANGE.get(realm, {'start': 0})['start']
    form['range'] = REALM_RANGE.get(realm, {'start': 0, 'end': 0, 'need': 0})

    # 仙人境的三小境：散仙 → 真仙 → 金仙，形象逐级加盛
    stage = stage_of_level(form['level'])
    bonus = COACH_XIAN_STAGES.get(stage)
    if bonus and realm == '仙人境':
        for key in ('halo', 'rings', 'orbit', 'shards', 'particles'):
            form[key] = int(form.get(key, 0)) + int(bonus.get(key, 0))
        # 非数值的开关型字段（金仙的日轮）直接透传
        for key, value in bonus.items():
            if key not in ('halo', 'rings', 'orbit', 'shards', 'particles', 'name', 'title'):
                form[key] = value
        form['name'] = bonus['name']
        form['title'] = bonus['title']
        form['stage'] = stage
    else:
        form['stage'] = stage
    return form


def coach_form_table(profile_level):
    """11 境形象全表 + 解锁状态。图鉴与「还差几境解锁」都靠它。

    注意：REALM_ORDER 只有十个**大境界**（炼气期起），凡尘不在其中
    ——因为凡尘不是「修出来的」，是出生自带的那一档。但星辰教练的第一尊
    （抱星星的星尘童儿）恰恰就是凡尘这一档，所以这里要把它补回表首，
    否则图鉴只有十格，而用户开局看到的那一尊反而在图鉴里找不到。
    """
    current_realm = realm_of_level(profile_level)
    rows = []
    for realm in ['凡尘'] + REALM_ORDER:
        rng = REALM_RANGE.get(realm, {'start': 0, 'end': 0, 'need': 0})
        # 当前所在的那个大境界要按**你的实际小境**取像：仙人境有三小境，
        # 全都取起始的「散仙」会让已经到金仙的人在图鉴里看到一尊不是自己的法相
        art = coach_form_for(profile_level if realm == current_realm else rng['start'])
        rows.append({
            'realm': realm,
            'art': art,
            'unlock_level': rng['start'],
            'unlock_need': rng['need'],
            'reached': profile_level >= rng['start'],
            'current': realm == current_realm,
        })
    return rows


def levels_table(profile_level):
    """全部 30 级 + 每级的神功，前端画地图与等级详情都用这一张表。"""
    rows = []
    for lv in training.LEVELS:
        realm = lv['realm']
        art = REALM_ART.get(realm, REALM_ART['凡尘'])
        rows.append({
            'level': lv['level'], 'name': lv['name'], 'realm': realm,
            'stage': lv['stage'], 'need': lv['need'],
            'tier': art['tier'], 'primary': art['primary'],
            'skill': skill_for(lv['level']),
            'reached': lv['level'] <= profile_level,
            'current': lv['level'] == profile_level,
        })
    return rows


def snapshot(username, state):
    """一次算完前端要的所有东西（除攻略部分按需裁剪）。"""
    state = state or {}
    profile = training.level_from_points(state.get('points', 0))
    stats = derive_stats(state)
    equipment = evaluate_equipment(stats)
    claimed = {key.split(':', 1)[1] for key in (state.get('rewards') or {})
               if key.startswith('trial:')}
    trials = evaluate_trials(stats, claimed)
    power = power_breakdown(profile, stats, equipment, stats.get('trials_done', 0))

    realms = []
    for realm in REALM_ORDER:
        rng = REALM_RANGE.get(realm, {'start': 0, 'end': 0, 'need': 0})
        trial = next((t for t in trials if t['realm'] == realm), None)
        realms.append({
            'realm': realm,
            'art': art_for(realm),
            'range': rng,
            'skill_start': skill_for(rng['start']),
            'skill_end': skill_for(rng['end']),
            'trial': trial,
            'reached': profile['level'] >= rng['start'],
            'current': profile['realm'] == realm,
            'equipment_done': sum(1 for e in equipment if e['unlocked']),
        })

    return {
        'user': username,
        'profile': profile,
        'art': art_for(profile['level']),
        'stats': stats,
        'power': power,
        'equipment': equipment,
        'trials': trials,
        'realms': realms,
        'levels': levels_table(profile['level']),
        'guide': build_guide(profile, stats, equipment, trials, state),
        'rules': {
            'question_base': training.QUESTION_BASE,
            'star_mult': training.STAR_MULT,
            'first_clear_bonus': training.FIRST_CLEAR_BONUS,
            'repeat_decay': training.REPEAT_DECAY,
            'kp_points': training.KP_POINTS,
            'narration_points': training.NARRATION_POINTS,
            'comic_points': training.COMIC_POINTS,
            'power_weight': POWER_WEIGHT,
        },
    }


def light_profile(state):
    """给全局悬浮等级条用的轻量补充：战力 + 试炼进度。

    悬浮条在每个页面都会挂，不能让它把整份 snapshot（含攻略选题）都算一遍。
    """
    state = state or {}
    profile = training.level_from_points(state.get('points', 0))
    stats = derive_stats(state)
    equipment = evaluate_equipment(stats)
    claimed = {key.split(':', 1)[1] for key in (state.get('rewards') or {})
               if key.startswith('trial:')}
    trials = evaluate_trials(stats, claimed)
    power = power_breakdown(profile, stats, equipment, stats.get('trials_done', 0))
    current_trial = next((t for t in trials if t['realm'] == profile['realm']), None)
    # 凡人期还没有自己的试炼，就把最近一个未通过的顶上来——
    # 新手第一眼看到的是「炼气期试炼 0/3」，而不是一片空白。
    if current_trial is None:
        current_trial = next((t for t in trials if not t['done']), trials[0] if trials else None)
    return {
        'power': power['total'],
        'equipment_unlocked': sum(1 for e in equipment if e['unlocked']),
        'equipment_total': len(equipment),
        'stars3': stats['stars3'],
        'hard_stars3': stats['stars3_hard'],
        'trial': current_trial,
        'skill': skill_for(profile['level']),
        'art': art_for(profile['level']),
        # 十境的法印表：仪表盘的境界阶梯要按境界给不同的印记与颜色，
        # 这份表很小（10 条），比为此再发一次 /api/game/state 划算得多。
        'realm_art': {realm: {'glyph': REALM_ART[realm]['glyph'],
                              'primary': REALM_ART[realm]['primary'],
                              'tier': REALM_ART[realm]['tier']} for realm in REALM_ORDER},
    }


def claim_trials(username):
    """把已达成的试炼奖励发下去。

    返回 (本次新发的 [(境界, 分数)], 最新等级信息)。

    要点是**级联**：一次突破奖励本身会进流水，可能让「连续 2 天有修为入账」
    这类目标同时达成，所以发完要重算一遍（最多三轮，避免任何意外死循环）。
    """
    if not username or username == 'guest':
        return [], training.level_from_points(0)

    granted = []

    def _pending(state):
        claimed = {key.split(':', 1)[1] for key in (state.get('rewards') or {})
                   if key.startswith('trial:')}
        return [t for t in evaluate_trials(derive_stats(state), claimed)
                if t['done'] and not t['claimed']]

    for _round in range(3):
        state = training.load_state(username)
        pending = _pending(state)
        if not pending:
            break

        def mutate(current, queue=pending):
            for trial in queue:
                awarded, _before, _after = training.award(
                    current, 'trial', trial['realm'], trial['reward'],
                    note=f"{trial['realm']}·境界试炼全通")
                if awarded:
                    granted.append((trial['realm'], awarded))
            return True

        training.mutate_state(username, mutate)

    state = training.load_state(username)
    return granted, training.level_from_points(state.get('points', 0))


if __name__ == '__main__':   # 手动跑一下：python game_engine.py <用户名>
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else 'guest'
    snap = snapshot(name, training.load_state(name) if name != 'guest' else {})
    print(f"{snap['profile']['name']} · 战力 {snap['power']['total']}")
    for part in snap['power']['parts']:
        print(f"  {part['label']}: {part['value']}（{part['note']}）")
    print(f"装备 {sum(1 for e in snap['equipment'] if e['unlocked'])}/{len(snap['equipment'])}")
    print('攻略：')
    for step in snap['guide']['steps']:
        print('  -', step['title'], '|', step.get('text', ''))
    print('当前神功：', snap['levels'][snap['profile']['level']]['skill']['name'])
