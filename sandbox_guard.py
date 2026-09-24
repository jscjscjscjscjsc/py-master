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
import threading

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
#
# 这一层原来只有 Linux 的 resource 模块，在 Windows 服务器上等于没有 ——
# 而线上那台正是 Windows。表现是：学生写一句 `x = bytearray(3 * 10**9)`
# 就能瞬间把 2GB 内存的机器吃满，把所有人的连接一起拖死（不是"他一个人崩"）。
# 所以补上 Windows 的原生手段，两条链路共用下面这一份代码。

# 每个代码子进程的内存上限（MB）。默认 512；线上 2GB 的机器建议调小，
# 用 PYMASTER_CODE_MEM_MB 控制 —— 留足给主进程和并发的那几份。
def mem_limit_mb():
    try:
        return max(64, int(os.environ.get('PYMASTER_CODE_MEM_MB', '512')))
    except ValueError:
        return 512


def cpu_limit_sec():
    try:
        return max(2, int(os.environ.get('PYMASTER_CODE_CPU_SEC', '15')))
    except ValueError:
        return 15


def _limit_code_body():
    """返回"给当前进程套上限"的 Python 源码（自包含，可直接嵌进子进程）。"""
    mb = mem_limit_mb()
    cpu = cpu_limit_sec()
    return f'''
def _pymaster_apply_limits():
    """给当前进程套上资源上限：CPU {cpu} 秒、内存 {mb}MB。

    Linux：resource 模块（内核级）。
    Windows：Job Object（同样内核级）。设的是"进程内存上限"，超了就抛
      MemoryError 而不是杀掉整个进程 —— 学生能看到一条正常报错，
      同机的其他人不受影响。
    """
    try:
        import resource as _r
        _r.setrlimit(_r.RLIMIT_CPU, ({cpu}, {cpu}))
        _cap = {mb} * 1024 * 1024
        _r.setrlimit(_r.RLIMIT_AS, (_cap, _cap))
        _r.setrlimit(_r.RLIMIT_NPROC, (64, 64))
        return
    except Exception:
        pass
    try:
        import ctypes as _ct
        from ctypes import wintypes as _wt

        class _IoCounters(_ct.Structure):
            _fields_ = [('a', _ct.c_ulonglong), ('b', _ct.c_ulonglong),
                        ('c', _ct.c_ulonglong), ('d', _ct.c_ulonglong),
                        ('e', _ct.c_ulonglong), ('f', _ct.c_ulonglong)]

        class _BasicLimit(_ct.Structure):
            _fields_ = [('PerProcessUserTimeLimit', _ct.c_int64),
                        ('PerJobUserTimeLimit', _ct.c_int64),
                        ('LimitFlags', _wt.DWORD),
                        ('MinimumWorkingSetSize', _ct.c_size_t),
                        ('MaximumWorkingSetSize', _ct.c_size_t),
                        ('ActiveProcessLimit', _wt.DWORD),
                        ('Affinity', _ct.c_size_t),
                        ('PriorityClass', _wt.DWORD),
                        ('SchedulingClass', _wt.DWORD)]

        class _ExtLimit(_ct.Structure):
            _fields_ = [('BasicLimitInformation', _BasicLimit),
                        ('IoInfo', _IoCounters),
                        ('ProcessMemoryLimit', _ct.c_size_t),
                        ('JobMemoryLimit', _ct.c_size_t),
                        ('PeakProcessMemoryUsed', _ct.c_size_t),
                        ('PeakJobMemoryUsed', _ct.c_size_t)]

        _k = _ct.WinDLL('kernel32', use_last_error=True)
        # 这几个声明缺一不可：不写 restype，64 位下句柄会被按 32 位整数截断，
        # 所有调用都会连着失败（而且报的是"参数错误"，完全指不到真正原因）。
        _k.CreateJobObjectW.restype = _wt.HANDLE
        _k.CreateJobObjectW.argtypes = [_ct.c_void_p, _wt.LPCWSTR]
        _k.SetInformationJobObject.restype = _wt.BOOL
        _k.SetInformationJobObject.argtypes = [_wt.HANDLE, _ct.c_int, _ct.c_void_p, _wt.DWORD]
        _k.AssignProcessToJobObject.restype = _wt.BOOL
        _k.AssignProcessToJobObject.argtypes = [_wt.HANDLE, _wt.HANDLE]
        _k.GetCurrentProcess.restype = _wt.HANDLE

        _job = _k.CreateJobObjectW(None, None)
        if not _job:
            return
        _info = _ExtLimit()
        # 0x100 = PROCESS_MEMORY（单个进程上限，配 ProcessMemoryLimit）
        # 0x200 = JOB_MEMORY    （整个 job 上限，配 JobMemoryLimit）
        # 0x2   = PROCESS_TIME  （单个进程的 CPU 时间，配 PerProcessUserTimeLimit）
        # 三个都设。**必须成对**：标志与字段不匹配时 SetInformationJobObject
        # 直接返回 ERROR_INVALID_PARAMETER(87)，限制静默失效 —— 这个坑踩过，
        # 表象是"设了限制但吃内存的代码照样跑"。
        _info.BasicLimitInformation.LimitFlags = 0x100 | 0x200 | 0x2
        _info.ProcessMemoryLimit = {mb} * 1024 * 1024
        _info.JobMemoryLimit = {mb} * 1024 * 1024
        # PerProcessUserTimeLimit 单位是 100 纳秒；这是 Windows 上对应
        # Linux RLIMIT_CPU 的东西，超了系统直接结束该进程，死循环不会一直吃 CPU。
        _info.BasicLimitInformation.PerProcessUserTimeLimit = {cpu} * 10_000_000
        if not _k.SetInformationJobObject(_job, 9, _ct.byref(_info), _ct.sizeof(_info)):
            return
        _k.AssignProcessToJobObject(_job, _k.GetCurrentProcess())
    except Exception:
        # 套不上也不让代码跑不起来：这层是"降低影响"，不是"保证安全"
        pass


_pymaster_apply_limits()
'''


# BLAS / OpenMP 线程数上限。**这是让 pandas 能跑起来的关键**，不是可选优化：
# numpy 背后的 OpenBLAS 默认按 CPU 核数开线程，每个线程都预留一大块缓冲，
# 于是"import pandas"本身就会申请几百 MB —— 实测在 512MB 上限下直接
# MemoryError + 一串 "OpenBLAS error: Memory allocation still failed"；
# 把线程数压到 1 之后，同一段 pandas + matplotlib 画图的代码在 256MB 里
# 就能跑通（实测峰值仅约 116MB）。2 核的机器上这也顺带减少了线程争抢。
# 必须通过环境变量在**子进程启动前**设好：OpenBLAS 是在 import 时读的，
# 进 Python 之后再改来不及。所以要合进子进程的 env，而不是写在引导脚本里。
BLAS_ENV = {
    'OPENBLAS_NUM_THREADS': '1',
    'OMP_NUM_THREADS': '1',
    'MKL_NUM_THREADS': '1',
    'NUMEXPR_NUM_THREADS': '1',
}


# 子进程引导：先限额，再执行目标脚本，并把 sys.argv 修正成"直接运行该脚本"的样子。
#
# 为什么不把限额代码直接拼到学生文件前面？那会让报错行号整体偏移 ——
# 学生看到"第 12 行出错"，可他自己写的文件里根本没有 12 行。
#
# sys.argv 必须手工校正：`python -c "..." 脚本 参数...` 里 sys.argv 是
# ['-c', 脚本, 参数...]，而判题 harness 读的是 sys.argv[1]=payload、
# argv[2]=out、argv[3]=figures —— 不校正就会整体错位一位，题目全部判不出来。
GUARD_BOOTSTRAP = ('import sys\n' + _limit_code_body()
                   + '''
_script = sys.argv[1]
sys.argv = [ _script ] + sys.argv[2:]
import runpy
runpy.run_path(_script, run_name="__main__")
''')


def limit_resources():
    """在子进程里调用：给当前进程加资源上限。（保留给外部/测试直接调用）"""
    if not is_enabled():
        return
    ns = {'sys': __import__('sys')}
    exec(_limit_code_body(), ns)          # noqa: S102 —— 内容由本模块生成，非外部输入


def guarded_command(script_path, extra_args=()):
    """把"目标脚本"包装成"带资源上限的执行命令"。

    两条执行链路都该用它：不加的话 Windows 上内存完全不设防，
    学生一句 bytearray(3*10**9) 就能把整台机器吃满。
    """
    import sys as _sys
    if not is_enabled():
        return [_sys.executable, '-X', 'utf8', str(script_path), *[str(a) for a in extra_args]]
    return [_sys.executable, '-X', 'utf8', '-c', GUARD_BOOTSTRAP,
            str(script_path), *[str(a) for a in extra_args]]


# ── 第 3 层：限制"同时跑几个" ──────────────────────────────
# 光有单进程上限还不够：2 核机器上十几个请求同时各跑一份 pandas，
# 每个人都变慢、最后一起超时。这里做成"排队"：跑满了就让后来的人
# 稍等几秒，等不到就给一句人话，而不是大家一起卡死。
def _slot_count():
    try:
        return max(1, int(os.environ.get('PYMASTER_MAX_CONCURRENT_RUNS', '4') or 4))
    except ValueError:
        return 4


_EXEC_SLOTS = threading.BoundedSemaphore(_slot_count())


def acquire_exec_slot(timeout=20):
    try:
        return _EXEC_SLOTS.acquire(timeout=timeout)
    except Exception:
        return True


def release_exec_slot():
    try:
        _EXEC_SLOTS.release()
    except Exception:
        pass


BUSY_MESSAGE = ('现在同时在跑的程序有点多，服务器在排队。'
                '请等几秒再点一次「运行」；如果一直这样，说明同一时间用的人比较多。')

