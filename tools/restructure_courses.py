"""课程体系重排：按《14 天新版课程编排方案》给 39 章重新定位与排序。

做了什么
--------
1. **重编章号**（id）与显示顺序 —— 这是"分体系"的实质：
   14 天主线排在最前，其余章节作为"进阶选修"排在后面
2. **更新 stage / stage_description**：从原来的 5 篇改为
   主线一（Python 基础）/ 主线二（衔接大模型）/ 4 个进阶选修篇
3. **给每章补 order 字段**，前端按它排序，避免依赖 id 的连续性

排序依据（来自 `新版14天课程编排方案.md`）
------------------------------------------
    主线一 · Python 基础（Day01–12）
      Day01 第1章  认识 Python 与开发环境
      Day02 第2章  变量、数据类型与输入输出
      Day03 第3章  流程控制
      Day04 第4章  字符串深入
      Day05 第5章  数据结构（上）
      Day06 第6章  数据结构（下）
      Day07 第7章  函数
      Day08 第8+9章 模块包、文件读写与异常
      Day09 第10+11章 面向对象
      Day10 第12章 高级特性
      Day11 第13章 第三方库与异步
      Day12 第24章 FastAPI（去数据库改造）
    主线二 · 衔接大模型（Day13–14）
      Day13 第27+28章 大模型 API 实战
      Day14 第29章 LangFlow 与智能体入门
    进阶选修
      工程与协作：15-20
      全栈与数据：21-23、25、26
      AI 应用开发：30-35
      AI 工程化：36-40

用法：
    python tools/restructure_courses.py --check     # 只看计划
    python tools/restructure_courses.py             # 执行（会备份）
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / 'data' / 'courses.json'

# 新的章节顺序：直接写"原来的 id"，脚本负责重编成连续的 1..N。
# 这段顺序就是给学生看到的顺序，也是学习路径。
NEW_ORDER = [
    # ── 主线一 · Python 基础（Day01–12）──
    1,    # Day01 认识 Python 与开发环境
    2,    # Day02 变量、数据类型与输入输出
    3,    # Day03 流程控制
    4,    # Day04 字符串深入
    5,    # Day05 数据结构（上）
    6,    # Day06 数据结构（下）
    7,    # Day07 函数
    8,    # Day08 模块、包与工程化
    9,    # Day08 文件读写、异常与调试
    10,   # Day09 面向对象（上）
    11,   # Day09 面向对象（下）
    12,   # Day10 高级特性
    13,   # Day11 第三方库、并发与异步
    24,   # Day12 FastAPI
    14,   # Day10 之后的课外自测卷（不占课时，但属于主线一）
    # ── 主线二 · 衔接大模型（Day13–14）──
    27,   # Day13 大模型、API 与智能体概念
    28,   # Day13 DeepSeek API 实战
    29,   # Day14 主流智能体框架全景（压缩为开场速览）
    41,   # Day14 LangFlow（新章，由迁移脚本从新版教材导入）
    # ── 进阶选修 · 工程与协作 ──
    15, 16, 17, 18, 19, 20,
    # ── 进阶选修 · 全栈与数据 ──
    21, 22, 23, 25, 26,
    # ── 进阶选修 · AI 应用开发 ──
    31, 32, 33, 34, 35,
    # ── 进阶选修 · AI 工程化 ──
    # 新版 40 天体系的完整版（51–59）；旧的 37–40 与 52–55 是同一份教材，
    # 已去重删除，这里不再引用。
    51, 52, 53, 54, 55, 56, 57, 58, 59,
]

# 每章归属的篇（按"原 id"给），脚本会据此写 stage
STAGE_OF = {}
for cid in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24):
    STAGE_OF[cid] = 'main1'
for cid in (27, 28, 29, 41):   # 41 = 新版 LangFlow（Day14）
    STAGE_OF[cid] = 'main2'
for cid in (15, 16, 17, 18, 19, 20):
    STAGE_OF[cid] = 'adv_eng'
for cid in (21, 22, 23, 25, 26):   # 原 24 FastAPI 已进主线，不在此列
    STAGE_OF[cid] = 'adv_full'
for cid in (31, 32, 33, 34, 35):
    STAGE_OF[cid] = 'adv_ai'
for cid in (51, 52, 53, 54, 55, 56, 57, 58, 59):   # 41 LangFlow 归主线二
    STAGE_OF[cid] = 'adv_aieng'
STAGE_OF[14] = 'main1'      # 阶段测验卷跟主线一

STAGES = {
    'main1': ('主线一 · Python 基础',
              '零基础到能写脚本：环境、变量、流程控制、字符串、四大容器、函数、'
              '面向对象、文件与 JSON、高级特性、requests 与异步。'
              '对应 14 天课程的 Day01–Day12。'),
    'main2': ('主线二 · 衔接大模型',
              '从 Python 跨到 AI：调用大模型 API、多轮对话与流式输出、'
              '工具调用、LangFlow 可视化编排。'
              '对应 14 天课程的 Day13–Day14，也是后续 AI 应用开发课的前置。'),
    'adv_eng': ('进阶选修 · 工程与协作',
                '把"能跑"变成"能维护"：需求、设计、测试、Git 分支与团队协作工作流。'
                '属软件工程专业课，不影响主线学习。'),
    'adv_full': ('进阶选修 · 全栈与数据',
                 '架构认知到落地：HTTP、REST、SQLite、FastAPI 完整版、Vue 与数据分析。'),
    'adv_ai': ('进阶选修 · AI 应用开发',
               '从调用大模型到做出产品：智能体框架与 M1–M5 综合实战项目。'
               '建议在主线二打底之后再回来做完整项目。'),
    'adv_aieng': ('进阶选修 · AI 工程化（RAG 与 Agent）',
                  '企业级 AI 应用的工程化：LLM 后端、RAG 检索增强、'
                  'Agent 机制与框架实战。给已入门、想继续往深走的人。'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    data = json.loads(COURSES.read_text(encoding='utf-8'))
    by_id = {c['id']: c for c in data}

    # 现有 id 里没有的（比如 ch36 还没导入）就跳过，不报错
    plan = [(old, by_id[old]) for old in NEW_ORDER if old in by_id]
    missing = [old for old in NEW_ORDER if old not in by_id]
    unused = [cid for cid in by_id if cid not in NEW_ORDER]

    print('课程体系重排计划')
    print('=' * 68)
    stage_now = None
    for new_id, (old_id, course) in enumerate(plan, 1):
        key = STAGE_OF.get(old_id, 'adv_aieng')
        if key != stage_now:
            stage_now = key
            print(f"\n【{STAGES[key][0]}】")
        print(f"  {new_id:>2}. (原 {old_id:>2}) {course['title'][:38]}"
              f"  知识点 {len(course.get('knowledge_points', [])):>3}")
    if missing:
        print(f'\n尚未导入（稍后由迁移脚本补上前会跳过）：{missing}')
    if unused:
        print(f'\n未列入新顺序的章节：{unused}')

    if args.check:
        print('\n--check：未写入')
        return 0

    # 备份
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = COURSES.with_suffix(f'.before-restructure-{stamp}.json')
    shutil.copy2(COURSES, backup)
    print(f'\n已备份到 {backup.name}')

    # **不改 id**，只加 order 字段控制显示顺序。
    # 原因：章号被三处引用 —— 题库的 chapter_id、讲解索引的键、
    # 以及解锁逻辑里的 sorted(id)。重编号要同时改三处，风险远大于收益，
    # 而"排序"这件事本来就该由独立字段表达。
    new_data = []
    for idx, (old_id, course) in enumerate(plan, 1):
        key = STAGE_OF.get(old_id, 'adv_aieng')
        course['stage'], course['stage_description'] = STAGES[key]
        course['order'] = idx
        new_data.append(course)
    for cid in unused:                       # 未列入的也保留，排到最后
        c = by_id[cid]
        c['order'] = len(new_data) + 1
        new_data.append(c)

    # 每个 stage 内再给一个篇内序号，前端分篇展示时用
    seen = {}
    for c in new_data:
        st = c.get('stage', '')
        seen[st] = seen.get(st, 0) + 1
        c['stage_order'] = seen[st]

    COURSES.write_text(json.dumps(new_data, ensure_ascii=False, indent=2),
                       encoding='utf-8')
    print(f'已重排 {len(plan)} 章的显示顺序与分篇（另有 {len(unused)} 章保留在末尾）')
    print('章号（id）保持不变：题库、讲解索引、解锁逻辑都不受影响。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
