"""首次启动时把运行环境准备好，让用户只面对一个「一键启动」。

为什么需要它
------------
下载压缩包的学生里，失败最多的两步是"没装 Python"和"pip 装不上"。
所以包里带了一份嵌入式 Python（runtime/python-embed.zip）和全部依赖的
wheel（vendor/wheels/），本脚本负责：

  1. 找 Python —— 优先用包里自带的，其次是系统的（顺手建个虚拟环境）；
  2. 解压嵌入式 Python 并修好 ._pth、装好 pip；
  3. 离线安装依赖（--no-index --find-links vendor/wheels），
     只有包内 wheel 不全时才回退到联网装（清华镜像）。

成功时退出码 0，并把选定的 python.exe 路径写到 runtime/python-path.txt，
启动脚本读它来起服务。任何一步失败都会打印人话说明并返回非 0。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'runtime'
BUNDLED_PY = RUNTIME / 'python'
BUNDLED_ZIP = RUNTIME / 'python-embed.zip'
WHEELS = ROOT / 'vendor' / 'wheels'
REQ_BUNDLE = ROOT / 'requirements-bundle.txt'
REQ_BASE = ROOT / 'requirements.txt'
VENV = RUNTIME / 'venv'
PY_PATH_FILE = RUNTIME / 'python-path.txt'
MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple'

# 平台自己启动就要用的库；装不上就直接告诉用户，不要让他对着报错猜
CORE_MODULES = ['flask', 'edge_tts']


def say(message):
    print(message, flush=True)


def run(cmd, **kwargs):
    kwargs.setdefault('cwd', str(ROOT))
    return subprocess.run([str(c) for c in cmd], **kwargs)


def find_system_python():
    """返回一个可用的系统 Python 解释器路径（自带 Python 不在考虑范围内）。"""
    candidates = []
    if os.name == 'nt':
        candidates.append(['py', '-3'])
    candidates.append([sys.executable])
    candidates.append(['python'])
    for item in candidates:
        exe, *rest = item
        if exe == sys.executable and not Path(exe).exists():
            continue
        try:
            probe = subprocess.run([exe, *rest, '-c', 'import sys; print("%d.%d" % sys.version_info[:2])'],
                                   capture_output=True, text=True, timeout=25)
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode != 0:
            continue
        try:
            major, minor = (int(part) for part in probe.stdout.strip().split('.')[:2])
        except ValueError:
            continue
        if major == 3 and 10 <= minor <= 13:
            return [exe, *rest]
    return None


def unpack_embedded():
    """解压随包 Python，并把它改造成能装第三方库的样子。"""
    if BUNDLED_PY.exists():
        return True
    if not BUNDLED_ZIP.exists():
        return False
    say('  · 正在解压随包 Python（只需一次）…')
    RUNTIME.mkdir(parents=True, exist_ok=True)
    BUNDLED_PY.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BUNDLED_ZIP) as archive:
        archive.extractall(BUNDLED_PY)

    (BUNDLED_PY / 'Lib' / 'site-packages').mkdir(parents=True, exist_ok=True)
    configure_embedded_pth()
    return True


def configure_embedded_pth():
    """把随包 Python 配成"能装库 + 能 import 平台自己的模块"。

    嵌入式发行版有两处默认行为会咬人：
      1. 禁用 site、不带 pip —— 装不了第三方库；
      2. 一旦存在 ._pth 就进入隔离模式，**不会**把脚本所在目录加进 sys.path，
         于是 `python app.py` 会报 ModuleNotFoundError: comic_engine。
    所以这里每次都按当前路径重写一遍：整个文件夹被搬到别处也能自愈。
    """
    stdlib_zip = next((p.name for p in BUNDLED_PY.glob('python*.zip')), '')
    for pth in BUNDLED_PY.glob('python*._pth'):
        lines = [stdlib_zip] if stdlib_zip else []
        lines += ['.', 'Lib\\site-packages', str(ROOT), 'import site']
        pth.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def bundled_python():
    exe = BUNDLED_PY / 'python.exe'
    return exe if exe.exists() else None


def ensure_pip(python):
    """嵌入式 Python 没有 pip，用包内 pip wheel 直接铺进去。"""
    probe = run([python, '-m', 'pip', '--version'], capture_output=True, text=True)
    if probe.returncode == 0:
        return True
    pip_wheels = sorted(WHEELS.glob('pip-*.whl')) if WHEELS.exists() else []
    if not pip_wheels:
        return False
    site = BUNDLED_PY / 'Lib' / 'site-packages'
    site.mkdir(parents=True, exist_ok=True)
    say('  · 正在准备 pip…')
    with zipfile.ZipFile(pip_wheels[-1]) as archive:
        archive.extractall(site)
    return run([python, '-m', 'pip', '--version'], capture_output=True, text=True).returncode == 0


def install_requirements(python):
    """先离线装；包内 wheel 不全时才联网。"""
    req = REQ_BUNDLE if REQ_BUNDLE.exists() else REQ_BASE
    if not req.exists():
        return True
    base = [python, '-m', 'pip', 'install', '--disable-pip-version-check', '-q', '-r', str(req)]
    if WHEELS.exists() and any(WHEELS.glob('*.whl')):
        offline = run(base + ['--no-index', '--find-links', str(WHEELS)],
                      capture_output=True, text=True)
        if offline.returncode == 0:
            say('  · 依赖已就绪（离线包）')
            return True
        say('  · 离线安装没成功，改用线上源重试…')
    online = run(base + ['-i', MIRROR], capture_output=True, text=True)
    if online.returncode == 0:
        say('  · 依赖已就绪（在线安装）')
        return True
    say('  ✗ 依赖安装失败。若是网络问题，请连上网后重新双击启动；')
    say('    错误摘要：' + (online.stderr or online.stdout or '')[-300:].strip())
    return False


def verify(python):
    code = 'import ' + ', '.join(CORE_MODULES)
    probe = run([python, '-c', code], capture_output=True, text=True)
    if probe.returncode == 0:
        return True
    say('  ✗ 运行环境不完整：' + (probe.stderr or '')[-300:].strip())
    return False


def main():
    parser = argparse.ArgumentParser(description='准备 PyMaster 运行环境')
    parser.add_argument('--check', action='store_true', help='只检查，不安装')
    args = parser.parse_args()

    RUNTIME.mkdir(exist_ok=True)
    say('[环境准备] 首次启动需要几十秒，之后就是秒开。')

    python = bundled_python()
    if not python and unpack_embedded():
        python = bundled_python()
        if python:
            say('  · 已启用随包 Python：' + str(python.relative_to(ROOT)))

    if python:
        # 每次启动都重写一次：用户把解压后的文件夹搬走/重命名后仍然能用
        configure_embedded_pth()
        if not ensure_pip(python):
            say('  ✗ 随包 Python 缺少 pip，压缩包可能不完整，请重新解压。')
            return 1
    else:
        system = find_system_python()
        if not system:
            say('  ✗ 没有找到可用的 Python（3.10–3.13）。')
            say('    请安装 Python 3.12：https://www.python.org/downloads/')
            say('    安装时记得勾选 “Add python.exe to PATH”，然后重新双击启动。')
            return 1
        venv_python = VENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if not venv_python.exists():
            say('  · 正在用系统 Python 建虚拟环境（不影响系统环境）…')
            created = run(system + ['-m', 'venv', str(VENV)], capture_output=True, text=True)
            if created.returncode != 0:
                say('  ✗ 虚拟环境创建失败：' + (created.stderr or '')[-300:].strip())
                return 1
        python = venv_python

    if args.check:
        ok = verify(python)
        say('  · 检查完成：' + ('可用' if ok else '需要安装依赖'))
        return 0 if ok else 1

    if not install_requirements(python):
        return 1
    if not verify(python):
        return 1

    PY_PATH_FILE.parent.mkdir(exist_ok=True)
    PY_PATH_FILE.write_text(str(python), encoding='utf-8')
    say('  ✓ 环境就绪')
    return 0


if __name__ == '__main__':
    sys.exit(main())
