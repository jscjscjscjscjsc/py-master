"""在线运行代码的安全闸门（只在公网部署时启用）。

背景
----
判题与"运行代码"是把学生提交的 Python **在服务器上直接跑**（见
`上线操作手册.md` 第三节）。本地版这样最省事，但一挂公网，任何人都能
拿它当跳板：读文件、发请求、扫内网、起进程、写走数据。

完全解决要靠一次性容器（Docker + 只读根 + 禁网），那是另一件工程。
这里做的是**可接受的折中**，目标是把"扫到就能用"降到"要绕过这些检查
才有机会"，同时不影响学生正常做题：

  第 1 层：静态检查 —— 拦掉明确的系统级危险操作（起进程、开网络、
           删文件、拿底层句柄）。正常教学代码碰不到这些。
  第 2 层：进程资源限制 —— 子进程里限 CPU 时间与地址空间，
           防止死循环/吃内存把服务器拖垮（仅在 Linux 生效）。

设置 `PYMASTER_SAFE_MODE=1` 启用（部署脚本默认开），本地版不设就完全不管。

注意：这是"降低风险"不是"保证安全"。真要公开大规模开放，
请按上线操作手册第三节的第三条路走（一次性容器）。
"""
import ast
import os
import re

# ── 第 1 层：静态检查 ────────────────────────────────────

# 直接禁止的模块：拿到它们就能操作系统或网络
BLOCKED_MODULES = {
    'subprocess', 'socket', 'ctypes', 'multiprocessing', 'pty', 'signal',
    'telnetlib', 'ftplib', 'smtplib', 'poplib', 'imaplib', 'http',
    'urllib', 'requests', 'httpx', 'aiohttp', 'paramiko', 'fabric',
    'pickle', 'marshal', 'shelve',           # 反序列化可执行任意代码
    'importlib', 'runpy', 'code', 'codeop',  # 动态导入/执行
    'shutil', 'tempfile',                    # 文件系统操作
    'pathlib', 'glob', 'fileinput',          # 遍历/读写文件
    'webbrowser', 'platform', 'getpass',     # 探测环境
}

# 单独放行的调用名（在其它模块下也要拦）
BLOCKED_ATTRS = {
    'system', 'popen', 'execv', 'execve', 'execvp', 'spawn', 'fork',
    'remove', 'unlink', 'rmdir', 'removedirs', 'rmtree', 'rename',
    'chmod', 'chown', 'kill', 'killpg', 'setuid', 'setgid',
    'urlopen', 'urlretrieve', 'socket', 'connect', 'sendall',
    'eval', 'exec', 'compile', '__import__', 'globals', 'locals',
    'getattr', 'setattr', 'delattr', 'vars', 'dir', 'open',
    'walk', 'listdir', 'scandir', 'makedirs', 'mkdir',
}

# 允许 os 用到的少数属性（学生偶尔会写 os.name 之类的无害判断）
OS_SAFE_ATTRS = {'name', 'sep', 'pathsep', 'linesep', 'getcwd', 'environ'}

BLOCK_MESSAGE = (
    '这段代码用到了在线环境不允许的操作（起进程 / 网络 / 文件系统 / 动态执行）。\n'
    '在线版只运行课程范围内的 Python 代码；本地完整版没有这个限制。\n'
    '如果是课程里要求写文件的练习，请在本地版完成。'
)


class UnsafeCode(Exception):
    """代码里出现了在线环境不允许的操作。"""


def is_enabled():
    return os.environ.get('PYMASTER_SAFE_MODE', '').strip().lower() in ('1', 'true', 'yes', 'on')


def _module_root(name):
    """`os.path.join` → `os`；`a.b.c` → `a`"""
    return (name or '').split('.')[0]


def check_source(code):
    """静态检查。不安全就抛 UnsafeCode，带上人话说明。"""
    if not is_enabled():
        return

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # 语法错的代码交给原来的流程去报（那边有更好的提示）
        return

    for node in ast.walk(tree):
        # import xxx / from xxx import yyy
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _module_root(alias.name) in BLOCKED_MODULES:
                    raise UnsafeCode(f'{BLOCK_MESSAGE}\n（不允许导入 {alias.name}）')
        elif isinstance(node, ast.ImportFrom):
            if _module_root(node.module) in BLOCKED_MODULES:
                raise UnsafeCode(f'{BLOCK_MESSAGE}\n（不允许导入 {node.module}）')
            for alias in node.names:
                if alias.name in BLOCKED_ATTRS:
                    raise UnsafeCode(f'{BLOCK_MESSAGE}\n（不允许使用 {node.module}.{alias.name}）')

        # 属性访问：os.system(...) / shutil.rmtree(...) 这类
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr not in BLOCKED_ATTRS:
                continue
            base = node.value
            base_name = ''
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            # os 白名单：允许 os.name / os.pathsep 这类只读判断
            if base_name == 'os' and attr in OS_SAFE_ATTRS:
                continue
            # list.remove / dict.get 之类的普通方法名撞上了黑名单，放行
            if base_name and base_name[0].islower() and base_name not in (
                    'os', 'sys', 'shutil', 'pathlib', 'ctypes', 'socket',
                    'subprocess', 'glob', 'tempfile', 'urllib', 'requests'):
                # 只在"看着像模块"的名字上加拦截，避免误伤 lst.remove(x)
                if base_name not in ('os', 'sys'):
                    continue
            raise UnsafeCode(f'{BLOCK_MESSAGE}\n（不允许调用 {base_name}.{attr}）')

        # 直接调用 eval / exec / __import__
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in (
                    'eval', 'exec', 'compile', '__import__', 'open', 'input'):
                # input 是课程内容（有专门的测试输入框），放行
                if func.id == 'input':
                    continue
                if func.id == 'open':
                    # 课程里确实要教文件读写。只允许读，不允许写的模式
                    mode = ''
                    if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                        mode = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                    if any(ch in mode for ch in ('w', 'a', 'x', '+')):
                        raise UnsafeCode(
                            '在线环境不允许写文件（只能用只读模式打开）。\n'
                            '课程里需要写文件的练习请在本地版完成。')
                    continue
                raise UnsafeCode(f'{BLOCK_MESSAGE}\n（不允许使用 {func.id}）')


# ── 第 2 层：子进程资源限制 ──────────────────────────────

# 打进子进程的一段启动代码：限 CPU 时间与地址空间，防止拖垮服务器。
# 用 resource 模块（Linux 有效；Windows 上该模块不存在，会被 try 跳过）。
RESOURCE_PREAMBLE = '''
try:
    import resource as _r
    _r.setrlimit(_r.RLIMIT_CPU, (15, 15))            # CPU 时间 15 秒
    _mb = 512 * 1024 * 1024
    _r.setrlimit(_r.RLIMIT_AS, (_mb, _mb))           # 地址空间 512MB
    _r.setrlimit(_r.RLIMIT_NPROC, (64, 64))          # 限制能起的线程/进程数
except Exception:
    pass
'''


def limit_resources():
    """在子进程里调用：给当前进程加资源上限。"""
    if not is_enabled():
        return
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
        cap = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    except Exception:
        # 非 Linux 或权限不足时静默跳过：宁可少一层防护，也不要让判题崩掉
        pass
