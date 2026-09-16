"""把 tools/qbank_*.py 里的题库编译成 data/question_bank.json。

为什么要多这一步，而不是让程序直接 import 那三个模块：

- 题目文件是**源码**（带注释、带 Python 字面量），运行时要的是**数据**。
  编译成 JSON 后，改题库与跑程序解耦，出问题也容易 diff。
- 编译期可以做体检：id 重复、章节号对不上课程、缺字段、难度越界——
  这些错误如果不拦住，上线后表现是「某道题点开是空白」，很难排查。

用法：
    python tools/build_question_bank.py            # 编译并写入
    python tools/build_question_bank.py --check    # 只体检，不写文件
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODULES = ['qbank_basic', 'qbank_pro', 'qbank_algo', 'qbank_408', 'qbank_leetcode']

# 算法专题的章节号从 101 起，避免与课程章节（1–40）冲突
ALGO_TOPICS = {
    101: '复杂度与基础',
    102: '数组与双指针',
    103: '字符串算法',
    104: '哈希表',
    105: '栈与队列',
    106: '链表',
    107: '递归与分治',
    108: '排序算法',
    109: '二分查找',
    110: '树与二叉树',
    111: '堆与优先队列',
    112: '图与搜索',
    113: '动态规划',
    114: '贪心算法',
    115: '回溯算法',
    116: '综合挑战',
    117: '顺序表与数组算法',
    118: '链表算法',
    119: '树与二叉树算法',
    120: '图算法与搜索',
    121: '查找与散列',
    122: '排序算法进阶',
    123: '字符串算法',
    124: '动态规划进阶',
    125: '数据结构高频题',
    126: '位运算与数学',
}

REQUIRED = ['id', 'chapter_id', 'title', 'difficulty', 'statement', 'solution']
ALLOWED_KEYS = {
    'id', 'track', 'chapter_id', 'chapter_title', 'topic', 'title', 'difficulty',
    'tags', 'statement', 'starter_code', 'solution', 'checks', 'explanation',
    'expected_output', 'hints', 'stdin',
}


def load_courses():
    path = os.path.join(ROOT, 'data', 'courses.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as handle:
        courses = json.load(handle)
    return {course['id']: course for course in courses}


def collect():
    items, problems = [], []
    seen = {}
    for module_name in MODULES:
        try:
            module = __import__(module_name)
        except ImportError:
            # 题库是分批写的，缺一个文件不该让整个编译失败
            problems.append(f'{module_name}: 模块不存在，已跳过')
            continue
        for index, raw in enumerate(module.QUESTIONS):
            question = dict(raw)
            qid = question.get('id', f'{module_name}#{index}')
            for field in REQUIRED:
                if not question.get(field):
                    problems.append(f'{qid}: 缺少字段 {field}')
            if question.get('difficulty') not in (1, 2, 3):
                problems.append(f'{qid}: difficulty 必须是 1/2/3，实际 {question.get("difficulty")!r}')
            extra = set(question) - ALLOWED_KEYS
            if extra:
                problems.append(f'{qid}: 出现未知字段 {sorted(extra)}')
            if qid in seen:
                problems.append(f'{qid}: id 重复（{seen[qid]} 与 {module_name}）')
            seen[qid] = module_name

            track = question.get('track') or ('algorithm' if question['chapter_id'] >= 100 else 'course')
            question['track'] = track
            if track == 'algorithm':
                topic = question.get('topic') or ALGO_TOPICS.get(question['chapter_id'], '')
                question['topic'] = topic
                question['chapter_title'] = topic or f'算法专题 {question["chapter_id"]}'
            items.append(question)
    return items, problems


def enrich_with_courses(items, courses, problems):
    for question in items:
        if question['track'] == 'algorithm':
            continue
        chapter = courses.get(question['chapter_id'])
        if chapter:
            question['chapter_title'] = chapter['title']
        else:
            problems.append(f'{question["id"]}: 章节 {question["chapter_id"]} 在 courses.json 里不存在')
            question.setdefault('chapter_title', f'第 {question["chapter_id"]} 章')
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='只体检，不写文件')
    parser.add_argument('--out', default=os.path.join(ROOT, 'data', 'question_bank.json'))
    args = parser.parse_args()

    courses = load_courses()
    items, problems = collect()
    items = enrich_with_courses(items, courses, problems)

    # 顺序：先按章节，再按难度，最后按 id，保证前端列表稳定
    items.sort(key=lambda q: (q['chapter_id'], q['difficulty'], q['id']))

    course_count = sum(1 for q in items if q['track'] == 'course')
    algo_count = len(items) - course_count
    chapters = sorted({q['chapter_id'] for q in items})
    levels = {1: 0, 2: 0, 3: 0}
    for question in items:
        levels[question['difficulty']] += 1
    checks_total = sum(len(q.get('checks') or []) for q in items)
    no_check = [q['id'] for q in items if not (q.get('checks') or [])]

    print(f'题目总数：{len(items)}（课程配套 {course_count} / 算法 {algo_count}）')
    print(f'覆盖章节：{len(chapters)} 个 -> {chapters[:12]}{" ..." if len(chapters) > 12 else ""}')
    print(f'难度分布：简单 {levels[1]} / 中等 {levels[2]} / 较难 {levels[3]}')
    print(f'断言总数：{checks_total} 条（平均每题 {checks_total / max(1, len(items)):.1f} 条）')
    if no_check:
        print(f'⚠ 没有断言的题目：{no_check}')
    if problems:
        print(f'\n⚠ 发现 {len(problems)} 个问题：')
        for problem in problems:
            print('  - ' + problem)
        return 1

    if args.check:
        print('\n体检通过（未写入文件）。')
        return 0

    with open(args.out, 'w', encoding='utf-8') as handle:
        json.dump(items, handle, ensure_ascii=False, indent=1)
    size = os.path.getsize(args.out) / 1024
    print(f'\n已写入 {args.out}（{size:.0f} KB）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
