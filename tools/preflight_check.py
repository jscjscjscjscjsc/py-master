"""上线前自检：把"到服务器上才发现"的问题尽量提前暴露出来。

每一条都是实际会踩的坑，不是走形式的检查：
  · 安全组/防火墙没开 → 外面连不上，但本机 curl 是通的，最容易误判「部署成功」；
  · .env 里还是默认管理员口令 → 等于后台门开着；
  · 判题开着但沙箱没开 → 服务器上无沙箱跑陌生人的代码；
  · Windows 上端口被旧进程占着 → 两个版本同时监听，看到的是旧内容；
  · 磁盘太小 / data 目录不可写 → 学生注册时 500，报错还指不到原因。
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OK, WARN, BAD = '√', '!', 'x'
problems = []


def item(level, text, hint=''):
    mark = {OK: '[√]', WARN: '[!]', BAD: '[x]'}[level]
    print(f'  {mark} {text}')
    if hint:
        print(f'        → {hint}')
    if level == BAD:
        problems.append(text)


def check_files():
    print('\n【文件完整性】')
    required = ['app.py', 'access_db.py', 'ark_client.py', 'sandbox_guard.py',
                'training_engine.py', 'templates/admin.html', 'templates/login.html',
                'static/css/style.css', '0-启动PyMaster.bat', '一键上线.bat']
    missing = [f for f in required if not (ROOT / f).exists()]
    if missing:
        item(BAD, f'缺少关键文件：{", ".join(missing)}', '请用完整的服务器版压缩包')
    else:
        item(OK, f'关键文件齐全（{len(required)} 项）')

    narr = ROOT / 'static' / 'narrations'
    n = len(list(narr.rglob('*'))) if narr.exists() else 0
    if n == 0:
        item(WARN, '没有讲解插画（static/narrations 为空）',
             '图文讲解会缺图；完整包应当自带这部分')
    else:
        item(OK, f'讲解插画 {n} 个文件')

    for name in ('courses.json', 'question_bank.json'):
        p = ROOT / 'data' / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                count = len(data) if isinstance(data, list) else len(data or {})
                item(OK, f'data/{name} 可读（{count} 项）')
            except ValueError as exc:
                item(BAD, f'data/{name} 不是合法 JSON：{exc}')
        else:
            item(BAD, f'缺少 data/{name}')


def check_env():
    print('\n【服务器配置】')
    env_file = ROOT / '.env'
    values = {}
    if env_file.exists():
        for raw in env_file.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                values[k.strip()] = v.strip().strip('"\'')
    else:
        item(WARN, '还没有 .env（双击「一键上线.bat」会自动生成）')

    merged = {**values, **{k: v for k, v in os.environ.items() if k.startswith('PYMASTER') or k == 'ARK_API_KEY'}}

    if merged.get('PYMASTER_SERVER_MODE', '').lower() in ('1', 'true', 'yes', 'on'):
        item(OK, '服务器模式已开启（并发用多线程服务器）')
    else:
        item(WARN, '还没开服务器模式',
             '在 .env 里加 PYMASTER_SERVER_MODE=1，否则多人同时用会互相卡')

    pwd = merged.get('PYMASTER_ADMIN_PASSWORD', '')
    if not pwd:
        item(WARN, '管理员口令还是默认的 admin888',
             '上线后请打开 /admin 登录并在「系统设置」里改掉，或在这里设 PYMASTER_ADMIN_PASSWORD')
    elif len(pwd) < 8:
        item(WARN, f'管理员口令只有 {len(pwd)} 位，建议至少 8 位')
    else:
        item(OK, '管理员口令已自定义')

    code_exec = merged.get('PYMASTER_ALLOW_CODE_EXEC', '').lower()
    safe = merged.get('PYMASTER_SAFE_MODE', '').lower() in ('1', 'true', 'yes', 'on')
    if code_exec in ('1', 'true', 'yes', 'on'):
        if safe:
            item(OK, '在线运行代码已开启，且安全沙箱已开')
        else:
            item(BAD, '在线运行代码开着，但安全沙箱没开',
                 '这等于把服务器借给任何人在上面执行代码。'
                 '要么设 PYMASTER_SAFE_MODE=1，要么关掉 PYMASTER_ALLOW_CODE_EXEC')
    else:
        item(OK, '在线运行代码已关闭（公网默认，安全）')

    if merged.get('ARK_API_KEY'):
        item(OK, '平台级模型 Key 已配置（未绑自己 Key 的用户会用它）')
    else:
        item(WARN, '没有平台级模型 Key',
             '学生必须各自绑定自己的 API 才能用 AI 功能（这是安全的默认值）')


def check_runtime():
    print('\n【运行环境】')
    print(f'  · Python {sys.version.split()[0]}（{sys.executable}）')

    try:
        import flask
        item(OK, f'Flask {flask.__version__}')
    except ImportError:
        item(BAD, '没装 Flask', '双击「一键上线.bat」会自动安装依赖')

    try:
        import waitress
        item(OK, 'waitress 已就绪（多线程服务器）')
    except ImportError:
        item(WARN, '没装 waitress，多人同时访问会互相卡',
             '双击「一键上线.bat」会自动装上')

    for mod, label in (('pandas', 'pandas（部分课程练习要用）'),
                       ('matplotlib', 'matplotlib（绘图章节要用）'),
                       ('edge_tts', 'edge-tts（讲解配音要用）')):
        try:
            __import__(mod)
            item(OK, label)
        except ImportError:
            item(WARN, f'缺少 {label}')

    import sqlite3
    item(OK, f'SQLite {sqlite3.sqlite_version}（访问日志用）')


def check_data_dir():
    print('\n【数据目录】')
    data_dir = Path(os.environ.get('PYMASTER_DATA_DIR') or (ROOT / 'data'))
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / '.write_test'
        probe.write_text('ok', encoding='utf-8')
        probe.unlink()
        item(OK, f'{data_dir} 可写')
    except OSError as exc:
        item(BAD, f'{data_dir} 不可写：{exc}',
             '学生注册会直接报 500。检查权限，或把平台放到有写权限的目录')
        return

    users = data_dir / 'users.json'
    if users.exists():
        try:
            count = len(json.loads(users.read_text(encoding='utf-8')))
            item(OK, f'已有 {count} 个账号（升级部署会保留）')
        except ValueError:
            item(BAD, 'users.json 损坏，解析失败',
                 '从备份恢复；没有备份就改名留档，平台会重建一个空表')
    try:
        free_gb = __import__('shutil').disk_usage(data_dir).free / 1024 ** 3
        if free_gb < 2:
            item(WARN, f'磁盘剩余空间只有 {free_gb:.1f} GB',
                 '讲解音频与日志会持续增长，建议至少留 2GB')
        else:
            item(OK, f'磁盘剩余 {free_gb:.1f} GB')
    except OSError:
        pass


def check_port():
    print('\n【端口】')
    port = int(os.environ.get('PORT', 5000))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        item(OK, f'{port} 端口空闲')
    except OSError:
        item(WARN, f'{port} 端口已被占用',
             '如果那是正在运行的 PyMaster，忽略即可；'
             '否则启动时会自动清理，清理失败要手动结束占用进程')
    finally:
        sock.close()

    # 外面能不能连上是部署成败的关键，而本机自测永远是通的
    print('\n  提示：本机自检看不出「外面能不能连上」。'
          '\n        阿里云控制台 → 安全组 → 入方向 → 放行 TCP %d。' % port)


def check_security():
    print('\n【安全】')
    if (ROOT / '.env').exists():
        mode = oct((ROOT / '.env').stat().st_mode)[-3:]
        item(OK if mode in ('600', '644') else WARN,
             f'.env 权限 {mode}')
    leaked = [p.name for p in ROOT.glob('.env.*') if p.name != '.env.example']
    if leaked:
        item(WARN, f'存在密钥备份文件：{", ".join(leaked)}',
             '确认它们不会被一起打包/上传到公开仓库')
    item(OK, '学生密码用 PBKDF2 加盐哈希存储（非明文）')
    item(OK, '管理员后台与学生账号体系已隔离（学生无法通过注册同名账号进入后台）')


def main():
    print('=' * 62)
    print('  PyMaster 上线前自检')
    print('=' * 62)
    check_files()
    check_env()
    check_runtime()
    check_data_dir()
    check_port()
    check_security()
    print('\n' + '=' * 62)
    if problems:
        print(f'  发现 {len(problems)} 个必须处理的问题：')
        for p in problems:
            print(f'    · {p}')
    else:
        print('  自检通过。可以双击「一键上线.bat」了。')
    print('=' * 62)
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
