"""课件迁移工具：把 Markdown 教材正文转换为 PyMaster 的 data/courses.json。

数据来源
--------
1. `桌面/数据文件/教材正文/Day*/第N章_*.md`            —— Python 基础 → AI 应用（第 1–35 章）
2. `桌面/数据文件/教材正文/Day*/第N章_练习题答案.md`    —— 合并为练习题的参考答案
3. `桌面/数据文件/AI全栈开发40天课程体系/教材正文/第0N章_*.md` —— AI 进阶（RAG / Agent）

章节切分规则
------------
`## N.X 标题` 视为一个知识点；「本章练习题」不进知识点而是转成练习题库；
Debug 四件套 / 任务卡 / 小结 / 速查 会打上类型标记，供前端做差异化样式。

用法
----
    python tools/migrate_courseware.py --check      # 只体检，不写文件
    python tools/migrate_courseware.py --write      # 生成 data/courses.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md2html import html_to_text, md_to_html  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = Path.home() / 'Desktop'
BASIC_DIR = DESKTOP / '数据文件' / '教材正文'
ADVANCED_DIR = DESKTOP / '数据文件' / 'AI全栈开发40天课程体系' / '教材正文'
COURSES_FILE = ROOT / 'data' / 'courses.json'
BACKUP_FILE = ROOT / 'data' / 'courses_legacy_9ch.json'

# 章节图标（按章号手工指定，比关键词猜测稳定）
ICONS = {
    1: '🐍', 2: '📦', 3: '🔀', 4: '🔤', 5: '📋', 6: '🗂️', 7: '🧩', 8: '📚',
    9: '📁', 10: '🏛️', 11: '🔗', 12: '✨', 13: '⚡', 14: '🏁', 15: '📐',
    16: '💎', 17: '🧪', 18: '🌿', 19: '☁️', 20: '👥', 21: '🏗️', 22: '🌐',
    23: '🛠️', 24: '🚄', 25: '💚', 26: '📊', 27: '🧠', 28: '🤖', 29: '🧭',
    30: '🎯', 31: '🗺️', 32: '🧱', 33: '🎨', 34: '🔧', 35: '🎤',
    37: '🔌', 38: '📚', 39: '🕹️', 40: '🧰', 41: '🎛️', 42: '🪄',
}

STAGES = [
    ('基础篇 · Python 核心语法', 1, 14,
     '从零开始的 Python 语法地基：环境、变量、流程、容器、函数、面向对象与文件 IO。'),
    ('工程篇 · 软件工程与协作', 15, 20,
     '把"能跑"变成"能维护"：需求、设计、测试、Git 分支与团队协作工作流。'),
    ('全栈篇 · 后端 / 前端 / 数据', 21, 26,
     '架构认知到落地：HTTP、REST、SQLite、FastAPI、Vue 与数据分析。'),
    ('AI 篇 · 大模型应用开发', 27, 35,
     '从调用大模型到做出产品：API 调用、工具调用、智能体框架与综合实战。'),
    ('AI 进阶篇 · RAG 与 Agent 工程', 36, 99,
     '企业级 AI 应用的工程化：LLM 后端、RAG 检索增强、Agent 机制与框架实战。'),
]

SECTION_KINDS = [
    (('学习目标',), 'goals'),
    (('debug',), 'debug'),
    (('任务卡', '解锁仪式', '微任务'), 'task'),
    (('小结', '知识树'), 'summary'),
    (('速查',), 'cheatsheet'),
    (('交付物检查表',), 'checklist'),
    (('测验',), 'exam'),
    (('练习题',), 'exercises'),
]


def section_kind(title):
    low = title.lower()
    for keys, kind in SECTION_KINDS:
        if any(k.lower() in low for k in keys):
            return kind
    return 'normal'


def stage_of(chapter_id):
    for name, lo, hi, desc in STAGES:
        if lo <= chapter_id <= hi:
            return name, desc
    return STAGES[-1][0], STAGES[-1][3]


# ---------------------------------------------------------------- 解析

def split_sections(md):
    """按 `## ` 二级标题切块，返回 [(标题, 正文)]，代码栅栏内的内容不参与切分。"""
    lines = md.replace('\r\n', '\n').split('\n')
    sections, current_title, buf = [], None, []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence
            buf.append(line)
            continue
        if not in_fence and re.match(r'^##\s+', line) and not line.startswith('###'):
            if current_title is not None:
                sections.append((current_title, '\n'.join(buf)))
            current_title = re.sub(r'^##\s+', '', line).strip()
            buf = []
            continue
        buf.append(line)

    if current_title is not None:
        sections.append((current_title, '\n'.join(buf)))
    elif buf:
        sections.append(('', '\n'.join(buf)))
    return sections


def clean_section_title(title):
    """剥掉 "5.1.1 " 这类编号前缀，编号单独返回。"""
    match = re.match(r'^(\d+(?:\.\d+)*)\s*[、.．]?\s*(.*)$', title)
    if match and match.group(2):
        return match.group(1), match.group(2).strip()
    return '', title


DIFFICULTY_RE = re.compile(r'^(基础题|进阶题|挑战题|提高题)')
QUESTION_RE = re.compile(
    r'^\*\*第\s*(\d+)\s*题\*\*(?:\s*[（(]([^）)]*)[）)])?\s*[:：]?\s*(.*)$')


def parse_exercises(section_md):
    """把「本章练习题」段落解析成题目列表。"""
    exercises = []
    buffers, current = [], None

    def flush():
        if current is None:
            return
        text = '\n'.join(current.pop('_lines')).strip()
        current['body'] = md_to_html(text, 3) if text else ''
        exercises.append(current)

    for raw in section_md.split('\n'):
        line = raw.rstrip()
        head = re.match(r'^###\s+(.*)$', line.strip())
        if head and DIFFICULTY_RE.match(head.group(1).strip()):
            difficulty = head.group(1).strip()
            continue
        if line.strip().startswith('###'):
            continue
        match = QUESTION_RE.match(line.strip())
        if match:
            flush()
            current = {
                'no': int(match.group(1)),
                'difficulty': difficulty,
                'tag': (match.group(2) or '').strip(),
                'title': match.group(3).strip(),
                '_lines': [],
            }
            continue
        if current is not None:
            current['_lines'].append(line)
        elif line.strip():
            buffers.append(line)

    flush()

    # 题目之前的引子（"纪律：全部手写…"）单独留出，交给页面做提示条
    intro = md_to_html('\n'.join(buffers).strip(), 3) if any(b.strip() for b in buffers) else ''
    return exercises, intro


def parse_answers(path):
    """解析《第N章_练习题答案.md》，返回 {题号: {'answer': md, 'explain': md}}。"""
    if not path.exists():
        return {}
    md = path.read_text(encoding='utf-8')
    result = {}
    blocks = re.split(r'\n(?=###\s+第\s*\d+\s*题)', md)
    for block in blocks:
        head = re.match(r'###\s+第\s*(\d+)\s*题[^\n]*\n(.*)', block, flags=re.S)
        if not head:
            continue
        no = int(head.group(1))
        body = head.group(2)
        explain_at = re.search(r'\n\*\*解析\*\*[:：]?\s*\n?', body)
        if explain_at:
            answer_md = body[:explain_at.start()]
            explain_md = body[explain_at.end():]
        else:
            answer_md, explain_md = body, ''
        explain_md = re.split(r'\n\*\*涉及知识点\*\*', explain_md)[0]
        result[no] = {
            'answer': md_to_html(answer_md.strip(), 3),
            'explain': md_to_html(explain_md.strip(), 3) if explain_md.strip() else '',
        }
    return result


_CODE_BLOCK_RE = re.compile(r'```(?:python|py)?\s*\n.+?```', re.S)
_CONCEPTUAL_RE = re.compile(
    r'解释|说明|什么(是|区别)|为什么|列举|描述|对比|分析|谈谈|总结|口述|用自己的话说')


def _has_code_block(text):
    """参考答案里有没有可直接运行的 Python 代码块。"""
    return bool(_CODE_BLOCK_RE.search(text or ''))


def _looks_conceptual(question_md):
    """题干是否在问概念而不是在要求写代码。"""
    plain = re.sub(r'`[^`]*`', '', question_md or '')
    return bool(_CONCEPTUAL_RE.search(plain))


def _plain_text(md_text):
    """把题干压成纯文本，给代码编辑器当题目说明用。

    编辑器里是 textContent，Markdown 符号（** 反引号）会原样显示出来，
    所以这里先剥掉标记，只留可读文字。
    """
    text = re.sub(r'```.*?```', ' ', md_text or '', flags=re.S)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.M)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.M)
    text = re.sub(r'[ \t]+', ' ', text)
    return re.sub(r'\n{2,}', '\n', text).strip()


def build_code_starter(question_md, reference):
    """给学生一个"题目已在编辑器里"的开场，而不是一片空白。

    只放题目要点做注释，不泄露参考答案的写法。
    """
    plain = re.sub(r'\s+', ' ', _plain_text(question_md)).strip()
    if len(plain) > 160:
        plain = plain[:160] + '…'
    lines = [f'# 题目：{plain}' if plain else '# 请在下面编写你的代码']
    skeleton = re.search(r'```(?:python|py)?\s*\n(.*?)```', question_md or '', re.S)
    if skeleton:
        lines.append('# 题目给出的代码骨架：')
        lines.extend('#   ' + line for line in skeleton.group(1).rstrip().split('\n'))
    lines.append('')
    lines.append('')
    return '\n'.join(lines)


def parse_mindmap(chapter_title, sections):
    """用小节标题树生成默认思维导图（mind-elixir 的 Markdown 语法）。"""
    lines = [f'# {chapter_title}']
    for title, body in sections:
        if not title:
            continue
        kind = section_kind(title)
        if kind in ('exercises', 'goals', 'cheatsheet'):
            continue
        num, name = clean_section_title(title)
        lines.append(f'## {num + " " if num else ""}{name}')
        for sub in re.findall(r'^###\s+(.*)$', body, flags=re.M):
            lines.append(f'### {clean_section_title(sub)[1]}')
    return '\n'.join(lines) if len(lines) > 1 else None


def parse_chapter(path, chapter_id):
    md = path.read_text(encoding='utf-8')
    title_match = re.match(r'^#\s+(.*)$', md, flags=re.M)
    raw_title = title_match.group(1).strip() if title_match else path.stem
    raw_title = re.sub(r'^第\s*\d+\s*章\s*[｜|:：、-]?\s*', '', raw_title).strip()

    sections = split_sections(md)
    knowledge_points, exercises, exercise_note, meta_lines = [], [], '', []

    head = sections[0][1] if sections and sections[0][0] == '' else ''
    for line in head.split('\n'):
        if line.strip().startswith('>'):
            meta_lines.append(re.sub(r'^\s*>\s?', '', line).strip())

    for title, body in sections:
        if not title:
            continue
        kind = section_kind(title)
        if kind == 'exercises':
            exercises, exercise_note = parse_exercises(body)
            continue
        num, name = clean_section_title(title)
        full_title = f'{num} {name}'.strip() if num else name
        knowledge_points.append({
            'title': full_title,
            'kind': kind,
            'content': md_to_html(body),
        })

    answers = parse_answers(path.with_name(f'第{chapter_id}章_练习题答案.md'))
    payload = []
    for ex in exercises:
        ref = answers.get(ex['no'], {})
        question_md = (f'**第 {ex["no"]} 题**' + (f'（{ex["tag"]}）' if ex['tag'] else '')
                       + '：' + ex['title'])
        if ex.get('body'):
            question_md += '\n\n' + ex['body']
        question_html = md_to_html(question_md, 3)
        reference = ref.get('answer', '')
        payload.append({
            'type': 'open',
            'difficulty': ex['difficulty'],
            'no': ex['no'],
            'question': question_md,
            'question_html': question_html,
            'question_plain': _plain_text(question_md),
            'body': ex.get('body', ''),
            # 学生打开编辑器时先看到的是任务说明，而不是一片空白
            'code_starter': build_code_starter(question_md, reference),
            'expects': 'text' if (not _has_code_block(reference) and _looks_conceptual(question_md)) else 'code',
            'reference': reference,
            'explanation': ref.get('explain', ''),
        })

    stage_name, stage_desc = stage_of(chapter_id)
    description = ''
    for line in meta_lines:
        if '主题' in line:
            description = line.split('：', 1)[-1].strip()
            break
    if not description:
        description = ' '.join(meta_lines[:2])[:160]
    if not description and knowledge_points:
        description = html_to_text(knowledge_points[0]['content'])[:120]

    return {
        'id': chapter_id,
        'title': raw_title,
        'icon': ICONS.get(chapter_id, '📘'),
        'description': description,
        'stage': stage_name,
        'stage_description': stage_desc,
        'source': str(path.relative_to(DESKTOP)).replace('\\', '/'),
        'knowledge_points': knowledge_points,
        'exercises': payload,
        'exercise_note': exercise_note,
        'ppt_url': None,
        'mindmap': parse_mindmap(raw_title, sections),
    }


# ---------------------------------------------------------------- 收集

def discover_chapters():
    """返回 [(章号, 路径, 来源)]，跳过答案册、试卷与教学总案。"""
    found = {}

    if BASIC_DIR.exists():
        for path in sorted(BASIC_DIR.glob('*_Day*/*.md')):
            name = path.name
            # 答案册与单独成卷的测验卷不进主章节链（正文里已有对应的知识点小节）
            if '练习题答案' in name or '测验卷' in name or '测验答案' in name:
                continue
            match = re.match(r'^第\s*(\d+)\s*章', name)
            if not match:
                continue
            found[int(match.group(1))] = (path, 'basic')

    offset = 35
    if ADVANCED_DIR.exists():
        for path in sorted(ADVANCED_DIR.glob('第0*章*.md')):
            name = path.name
            if '学习路线' in name or '教学总案' in name or '练习题答案' in name:
                continue
            match = re.match(r'^第\s*(\d+)\s*章', name)
            if not match:
                continue
            found[offset + int(match.group(1))] = (path, 'advanced')

    # 复习试卷作为附录挂到第 14 章之后（不进主链，避免打断解锁顺序）
    return [(cid, found[cid][0], found[cid][1]) for cid in sorted(found)]


def build():
    chapters = []
    for chapter_id, path, source in discover_chapters():
        try:
            chapters.append(parse_chapter(path, chapter_id))
        except Exception as exc:  # 单章失败不应阻断整批迁移
            print(f'  ✗ 第 {chapter_id} 章解析失败：{type(exc).__name__}: {exc}')
    return chapters


def main():
    parser = argparse.ArgumentParser(description='把教材正文迁移为 PyMaster 课程数据')
    parser.add_argument('--write', action='store_true', help='写入 data/courses.json')
    parser.add_argument('--check', action='store_true', help='只输出统计体检')
    args = parser.parse_args()

    chapters = build()
    kp_total = sum(len(c['knowledge_points']) for c in chapters)
    ex_total = sum(len(c['exercises']) for c in chapters)
    answered = sum(1 for c in chapters for e in c['exercises'] if e['reference'])

    print(f'章节：{len(chapters)}  知识点：{kp_total}  练习题：{ex_total}（含参考答案 {answered}）')
    for chapter in chapters:
        kinds = {}
        for kp in chapter['knowledge_points']:
            kinds[kp['kind']] = kinds.get(kp['kind'], 0) + 1
        summary = ' '.join(f'{k}={v}' for k, v in sorted(kinds.items()) if k != 'normal')
        print(f"  [{chapter['id']:>2}] {chapter['icon']} {chapter['title'][:26]:<28} "
              f"kp={len(chapter['knowledge_points']):>2} ex={len(chapter['exercises']):>2}"
              f"{'  ' + summary if summary else ''}")
        if not chapter['knowledge_points']:
            print('       ⚠ 无知识点，检查切分规则')

    if args.write:
        if not args.check and COURSES_FILE.exists() and not BACKUP_FILE.exists():
            BACKUP_FILE.write_text(COURSES_FILE.read_text(encoding='utf-8'), encoding='utf-8')
            print(f'\n已备份旧课程数据 → {BACKUP_FILE.name}')
        COURSES_FILE.write_text(
            json.dumps(chapters, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'已写入 {COURSES_FILE}  （{COURSES_FILE.stat().st_size / 1024:.0f} KB）')


if __name__ == '__main__':
    main()
