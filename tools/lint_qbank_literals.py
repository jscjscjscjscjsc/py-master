"""题库源码体检：找出「单引号字符串被内层单引号提前截断」的行。

写中文题目时最常犯的错误长这样：

    '例如 `impacted(tasks, ['用户表'])` 应该包含……'

外层用单引号，正文里又出现单引号 → 字符串在 `['` 处就结束了，
后面的中文变成裸标识符，解释器报「invalid syntax」。

这类错误 Python 只会报第一处、而且行号常常指向别的地方，
逐个试错很费时间。这个脚本按「字符串字面量的闭合位置」判断：
单引号开头的行，找到第一个未转义的收尾单引号后，
如果后面还有不是 , ) ] } : + % . \\ 的内容，就说明被截断了。

用法：
    python tools/lint_qbank_literals.py            # 检查 tools/qbank_*.py
    python tools/lint_qbank_literals.py 文件1 文件2
"""

import glob
import os
import sys

BACKSLASH = chr(92)
QUOTE = chr(39)
OK_AFTER = set(',)]}:+%.' + BACKSLASH)


def scan(path):
    hits = []
    with open(path, encoding='utf-8') as handle:
        for lineno, line in enumerate(handle.read().split('\n'), 1):
            stripped = line.lstrip()
            if not stripped.startswith(QUOTE):
                continue
            indent = len(line) - len(stripped)
            index = indent + 1
            while index < len(line):
                char = line[index]
                if char == BACKSLASH:
                    index += 2
                    continue
                if char == QUOTE:
                    break
                index += 1
            if index >= len(line):
                continue
            rest = line[index + 1:].strip()
            if not rest or rest[0] in OK_AFTER:
                continue
            hits.append((lineno, line.strip()[:130]))
    return hits


def main():
    targets = sys.argv[1:]
    if not targets:
        here = os.path.dirname(os.path.abspath(__file__))
        targets = sorted(glob.glob(os.path.join(here, 'qbank_*.py')))
    total = 0
    for path in targets:
        found = scan(path)
        total += len(found)
        print(f'== {os.path.basename(path)}：{len(found)} 处可疑')
        for lineno, text in found:
            print(f'   {lineno}: {text}')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
