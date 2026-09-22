"""安全闸门自测：确认公网部署时系统级操作被拦、正常教学代码放行。

单独一个脚本，不进 test_platform.py —— 后面那个是平台功能自测，
这个是部署安全边界，两者关注点不同，混在一起容易在改功能时误删。

用法：
    python tools/test_sandbox.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 直接进程内测闸门本身（比走 HTTP 快，也不依赖服务器起没起）
os.environ['PYMASTER_SAFE_MODE'] = '1'
import sandbox_guard as sg  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, detail=''):
    (PASS if ok else FAIL).append(name)
    print(('  ✓ ' if ok else '  ✗ ') + name + (f'   {detail}' if detail and not ok else ''))


# （代码, 是否应当放行, 说明）
CASES = [
    # 必须拦
    ('import subprocess', False, '起子进程'),
    ('import os\nos.system("dir")', False, 'os.system'),
    ('import socket', False, '网络 socket'),
    ('import requests', False, '网络库'),
    ('import urllib.request', False, 'urllib'),
    ('import ctypes', False, '底层句柄'),
    ('import shutil\nshutil.rmtree("/tmp")', False, '删目录'),
    ('import pickle', False, '反序列化'),
    ('open("x.txt","w").write("h")', False, '写文件'),
    ('open("x.txt","a")', False, '追加写'),
    ('eval("1+1")', False, 'eval'),
    ('exec("a=1")', False, 'exec'),
    ('__import__("os")', False, '动态导入'),
    ('import os\nos.remove("a")', False, 'os.remove'),
    ('import os\nos.listdir("/")', False, '列目录'),
    # 必须放行（课程内容，误伤会直接影响学生做题）
    ('print(1+1)', True, '最基本输出'),
    ('s = "PyMaster2026"\nprint(s[::-1])', True, '字符串切片'),
    ('import math\nprint(math.sqrt(16))', True, 'math'),
    ('import random\nprint(random.randint(1,6))', True, 'random'),
    ('import json\nprint(json.dumps({"a":1}))', True, 'json'),
    ('n = int(input())\nprint(n*2)', True, 'input（有测试输入框）'),
    ('open("data.txt").read()', True, '只读打开'),
    ('lst = [3,1,2]\nlst.sort()\nprint(lst)', True, 'list.sort'),
    ('lst = [1]\nlst.remove(1)', True, 'list.remove（方法名撞黑名单）'),
    ('d = {"a":1}\nprint(d.get("a"))', True, 'dict.get'),
    ('import os\nprint(os.name)', True, 'os.name 只读判断'),
    ('import os\nprint(os.getcwd())', True, 'os.getcwd 只读判断'),
]


def main():
    print('安全闸门自测（PYMASTER_SAFE_MODE=1）\n' + '─' * 56)
    for code, should_pass, label in CASES:
        try:
            sg.check_source(code)
            blocked = False
        except sg.UnsafeCode:
            blocked = True
        allowed = not blocked
        check(f'{label:<28} {"放行" if should_pass else "拦截"}', allowed == should_pass,
              f'实际 {"放行" if allowed else "拦截"}')

    print('\n' + '─' * 56)
    print(f'通过 {len(PASS)}/{len(CASES)}')
    if FAIL:
        print('失败项：')
        for name in FAIL:
            print('  ✗', name)
        return 1
    print('全部通过 ✅')
    return 0


if __name__ == '__main__':
    sys.exit(main())
