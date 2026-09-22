"""修复课件里"照录运行结果"与代码实际输出不符的地方。

背景：教材的代码案例是人工/大模型写下"运行结果"的，从未验证过。
`tools/audit_courseware.py` 真跑一遍后抓出若干处不符 —— 学生照着敲、
看到结果对不上，会先怀疑自己，这比"没写结果"更糟。

本脚本做两件事：
  1. 修正 courses.json 里的照录结果（运行时数据）
  2. 同步修正教材正文 md（源头），否则下次跑迁移又会被覆盖回去

用法：
    python tools/fix_courseware.py --check    # 只看要改什么
    python tools/fix_courseware.py            # 执行
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / 'data' / 'courses.json'
DESKTOP = Path.home() / 'Desktop'
BASIC_DIR = DESKTOP / '数据文件' / '教材正文'

# 逐条写清"错在哪、改成什么"。
# 每条 = (定位用的唯一片段, 原文, 修正后)
# 定位片段用来同时命中 json 与 md 两处（它们内容一致）。
FIXES = [
    {
        'name': '4.7 split 与 join：照录多了一行',
        'anchor': "joined = \"、\".join(name_list)",
        'old': "['张三', '李四', '王五']\n['张三', '李四', '王五']\n张三、李四、王五",
        'new': "['张三', '李四', '王五']\n张三、李四、王五",
        'why': '代码只 print 了 name_list 和 joined 两行，照录却写了三行',
    },
    {
        'name': '4.11 千分位与百分比：第三行照录错了',
        'anchor': "print(f\"人口：{1234567:,}\")",
        'old': "总销售额：1,234,567.89 元\n达成率：85.6%\n达成率：85.6%",
        'new': "总销售额：1,234,567.89 元\n达成率：85.6%\n人口：1,234,567",
        'why': '第三行代码打印的是人口，照录却复制了上一行的达成率',
    },
    {
        'name': '6.2 添加、修改、删除：照录漏了字段',
        'anchor': 'city = student.pop("city")',
        'old': "{'name': '张三', 'age': 19, 'city': '北京'}\n"
               "{'name': '张三', 'age': 20}\n北京\n{'name': '张三'}\n{}",
        'new': "{'name': '张三', 'age': 19, 'city': '北京'}\n"
               "{'name': '张三', 'age': 20, 'city': '北京'}\n北京\n"
               "{'name': '张三', 'age': 20}\n{}",
        'why': '改 age 时 city 还在；pop 掉 city 之后剩下的是 age，照录两处都对不上',
    },
    {
        'name': '6.3 keys/values/items：末段照录写错了格式',
        'anchor': "for key, value in student.items():",
        'old': "键：name\n键：age\n键：score\n"
               "值：张三\n值：19\n值：88.5\n"
               "键：name\n键：age\n键：score",
        'new': "键：name\n键：age\n键：score\n"
               "值：张三\n值：19\n值：88.5\n"
               "name = 张三\nage = 19\nscore = 88.5",
        'why': 'items() 那段的格式串是 f"{key} = {value}"，照录却写成「键：x」',
    },
]


def apply_to_text(text, old, new):
    """替换。返回 (新文本, 是否改动)。"""
    if old in text:
        return text.replace(old, new, 1), True
    return text, False


def json_escape(text):
    """把 md 里的片段转成它在 courses.json 里的样子。

    courses.json 里的正文是 HTML（内容经 html.escape 处理过），
    且换行存成了字面量反斜杠+n，不是真换行。
    """
    import html as _html
    literal_newline = chr(92) + 'n'      # 字面量 \n（两字符）
    return _html.escape(text, quote=True).replace(chr(10), literal_newline)


def fix_courses_json(dry=True):
    data = COURSES.read_text(encoding='utf-8')
    changed = []
    for fix in FIXES:
        # 锚点与原文都要用 json 里的转义形态去找
        for anchor in (json_escape(fix['anchor']), fix['anchor']):
            idx = data.find(anchor)
            if idx >= 0:
                break
        if idx < 0:
            print(f"  ？ {fix['name']} —— 在 courses.json 里找不到锚点")
            continue
        window = data[idx:idx + 2000]
        replaced, ok = apply_to_text(window, json_escape(fix['old']), json_escape(fix['new']))
        if not ok:
            # 试一下未转义的形态（万一原文没被转义）
            replaced, ok = apply_to_text(window, fix['old'], fix['new'])
        if not ok:
            print(f"  ？ {fix['name']} —— 锚点附近没找到原文")
            continue
        data = data[:idx] + replaced + data[idx + 2000:]
        changed.append(fix['name'])
    if changed and not dry:
        COURSES.write_text(data, encoding='utf-8')
    return changed


def fix_markdown(dry=True):
    """同步修教材正文 md（源头）。"""
    changed = []
    for md in sorted(BASIC_DIR.rglob('第*章_*.md')):
        if '_旧版备份' in str(md):
            continue
        text = md.read_text(encoding='utf-8')
        orig = text
        for fix in FIXES:
            idx = text.find(fix['anchor'])
            if idx < 0:
                continue
            window = text[idx:idx + 1500]
            replaced, ok = apply_to_text(window, fix['old'], fix['new'])
            if ok:
                text = text[:idx] + replaced + text[idx + 1500:]
                changed.append(f"{md.name} / {fix['name']}")
        if text != orig and not dry:
            md.write_text(text, encoding='utf-8')
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='只报告，不写入')
    args = ap.parse_args()
    dry = args.check

    print('修复课件代码与运行结果不符\n' + '─' * 60)
    for fix in FIXES:
        print(f"  · {fix['name']}")
        print(f"      原因：{fix['why']}")

    print('\n[courses.json]')
    a = fix_courses_json(dry)
    for n in a:
        print(f'  ✓ {n}')
    print('\n[教材正文 md]')
    b = fix_markdown(dry)
    for n in b:
        print(f'  ✓ {n}')

    if dry:
        print(f'\n--check：将修改 {len(a)} 处 json、{len(b)} 处 md（未写入）')
    else:
        print(f'\n已修改 {len(a)} 处 json、{len(b)} 处 md')
        print('提示：重新跑 python tools/audit_courseware.py 确认已一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
