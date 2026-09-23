"""打一个「传到服务器上双击就能上线」的部署包。

和 tools/make_release.py 的区别
------------------------------
make_release.py 打的是**发给学生自己电脑用**的包：里面不含 data/、不含讲解音频，
每个人在自己机器上重新生成。这个脚本打的是**放到你那台 ECS 上对外服务**的包，
所以：

  · 带上 data/ 里全部课程数据 + 讲解音频缓存（841MB 音频实测太占地方，
    默认不带，服务器上第一次点「生成讲解」时会自己攒，也可以加 --with-audio 带上）；
  · 带上随包 Python 与全部 wheel（服务器上不需要装任何东西）；
  · 额外塞进 一键上线.bat（设环境变量 + 开防火墙 + 起服务）和 上线前自检.bat；
  · **绝不带** .env（里面是你的 opencode go 密钥）、users.json、日志。

用法
----
    python tools/make_server_package.py              # 标准（不含讲解音频缓存）
    python tools/make_server_package.py --with-audio # 连讲解音频一起带（包很大）
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'dist'
WHEELS = ROOT / 'vendor' / 'wheels'
RUNTIME_ZIP = ROOT / 'runtime' / 'python-embed.zip'

# 平台自身 + 教学库（服务器上判题/讲解都要用）
PACKAGES = ['flask', 'edge_tts', 'waitress', 'requests', 'pytest',
            'fastapi', 'uvicorn', 'httpx', 'pandas', 'matplotlib', 'openai']

EXCLUDE_DIRS = {
    '.git', '__pycache__', 'logs', 'docs', 'runtime', 'vendor', 'dist', 'tests',
    'tools/render/node_modules', 'tools/render/preview', '.video-build', '.workbuddy',
    'data/music_cache', 'data/training', 'data/coach', 'data/user_notes',
    'static/audio',
}
# 讲解音频缓存默认排除（几百 MB，服务器上自己攒）
AUDIO_CACHE_DIRS = {'data/audio_cache'}
EXCLUDE_FILES = {
    '视频制作说明.md', 'data/users.json', 'data/whitelist.json', 'data/daily_usage.json',
    'data/.secret_key', 'data/comic_memory.json', 'data/.build_narrations.lock',
    'data/access.db', 'data/access.db-wal', 'data/access.db-shm',
    '更新说明-客户版.md', 'HANDOFF.md', 'PROGRESS.md', 'trend.png',
    'deploy/Caddyfile', 'deploy/Caddyfile.review', 'deploy/Dockerfile',
    'deploy/Dockerfile.dockerignore', 'deploy/docker-compose.yml',
    'deploy/review-compose.yml', 'deploy/entrypoint.py', 'deploy/.env.example',
    'runtime/python-path.txt',
}
KEEP_SUFFIX = {'.py', '.json', '.txt', '.md', '.js', '.mjs', '.css', '.html', '.png',
               '.jpg', '.jpeg', '.svg', '.mp3', '.ico', '.woff', '.woff2', '.ttf',
               '.bat', '.sh', '.toml', '.cfg', '.example', '.yml', '.yaml'}

# 服务器包根目录里只留这两个 bat，其余启动脚本一律清掉
SERVER_BATS = ('一键上线.bat', '上线前自检.bat')
ALLOWED_ROOT_BATS = {'0-启动PyMaster.bat'} | set(SERVER_BATS)

# 上线前必须看的文档，放压缩包根目录（不塞进子目录里）
SERVER_DOCS = ('服务器版上线手册.md', '大模型添加说明书和教程.md')

DEV_SCRIPTS = ('build_comics.py', 'build_narrations.py', 'build_static_docs.py',
               'fix_json.py', 'setup_api.py', 'test_tts_api.py')
DEV_DOCS = ('上线部署方案.md', '评审在线试用指引.md', '更新说明-客户版.md')

SERVER_README = """PyMaster 教学平台 · 服务器版
================================

【怎么上线】
  1. 把整个文件夹解压到服务器的某个盘（例如 D:\\PyMaster）
     —— 路径尽量短、不要带中文空格，后面排查日志方便。
  2. 双击「一键上线.bat」
  3. 它做完三件事：开防火墙端口、准备运行环境、启动服务。
  4. 看到「服务已启动」后，在浏览器打开：  http://服务器公网IP:5000

【上线后第一件事（务必做）】
  打开 http://服务器公网IP:5000/admin
  默认管理员：admin / admin888
  登录后立刻在「系统设置」里改成你自己的口令。
  这个后台能看到谁注册了、谁什么时候登录、各自绑了哪个模型。

【阿里云安全组也要放行】
  光开 Windows 防火墙不够，阿里云控制台的「安全组」还要加入方向规则：
    协议 TCP，端口 5000，授权对象 0.0.0.0/0
  否则外面连不上（表现是浏览器一直转圈直到超时）。

【学生怎么用】
  把 http://服务器公网IP:5000 发给他们即可。
  学生自己注册账号 → 在「模型配置」里填自己的 API Key → 开始学习。
  每个人的 Key 只存在他自己的账号记录里，互相看不到。

【数据在哪】
  data\\users.json      账号、进度、每人绑定的模型
  data\\access.db       访问日志（后台页面读的就是它）
  data\\avatars\\       头像
  备份：整个 data 目录拷走即可。

【怎么停止】
  关闭那个命令行窗口。或在「一键上线.bat」窗口按 Ctrl+C。
"""


def say(text):
    print(text, flush=True)


def should_keep(path: Path, with_audio: bool) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDE_FILES:
        return False
    blocked = set(EXCLUDE_DIRS)
    if not with_audio:
        blocked |= AUDIO_CACHE_DIRS
    for b in blocked:
        if rel == b or rel.startswith(b + '/'):
            return False
    if any(part == '__pycache__' for part in path.parts):
        return False
    if path.name.startswith('.env.') and path.name != '.env.example':
        return False
    if path.name == '.env':
        return False                          # 你的密钥绝不能进包
    if path.suffix.lower() not in KEEP_SUFFIX and path.name not in ALLOWED_ROOT_BATS:
        return False
    return True


def stage(stage_dir: Path, with_audio: bool) -> int:
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)
    count = 0
    for path in sorted(ROOT.rglob('*')):
        if path.is_dir() or not should_keep(path, with_audio):
            continue
        target = stage_dir / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    say(f'  · 复制了 {count} 个文件')

    # 开发脚本/内部资料收进子目录，根目录只留上线要用的东西
    for group, name in ((DEV_SCRIPTS, '开发脚本'), (DEV_DOCS, '内部资料')):
        for item in group:
            src = stage_dir / item
            if src.exists():
                dest = stage_dir / name
                dest.mkdir(exist_ok=True)
                shutil.move(str(src), str(dest / item))
    # tools 里只留上线与运行时真正会用到的：其余都是开发脚本，收进「开发脚本」
    tools_dir = stage_dir / 'tools'
    if tools_dir.exists():
        keep = {'bootstrap_runtime.py', 'preflight_check.py'}
        for item in tools_dir.iterdir():
            if item.is_file() and item.name not in keep:
                dev = stage_dir / '开发脚本'
                dev.mkdir(exist_ok=True)
                shutil.move(str(item), str(dev / item.name))
            elif item.is_dir() and item.name not in {'render'}:
                shutil.rmtree(item, ignore_errors=True)
        render = tools_dir / 'render'
        if render.exists():
            for item in render.iterdir():
                if item.name in {'node_modules', 'preview'}:
                    shutil.rmtree(item, ignore_errors=True)

    # 讲解插画是服务器版的核心内容之一，必须带；缺了会看到大片占位图
    narr = stage_dir / 'static' / 'narrations'
    say(f'  · 讲解插画：{len(list(narr.rglob("*"))) if narr.exists() else 0} 个文件')

    (stage_dir / 'runtime').mkdir(exist_ok=True)
    if RUNTIME_ZIP.exists():
        shutil.copy2(RUNTIME_ZIP, stage_dir / 'runtime' / 'python-embed.zip')
    shutil.copytree(WHEELS, stage_dir / 'vendor' / 'wheels', dirs_exist_ok=True)
    (stage_dir / 'data').mkdir(exist_ok=True)
    (stage_dir / '使用说明.txt').write_text(SERVER_README, encoding='utf-8')
    return count


def make_zip(stage_dir: Path, archive: Path):
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(stage_dir.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(stage_dir.parent))
    return archive


def write_requirements_bundle(stage_dir: Path):
    """按**本包实际带的 wheel** 重新生成安装清单。

    不能沿用仓库里那份 requirements-bundle.txt：它是 make_release.py
    给学生分发包生成的，不含 waitress（服务器版的多线程服务器），
    照它装的话服务器上会用回单线程，多人同时访问就互相卡 —— 而且
    这个失败很安静，bootstrap 只报"环境就绪"，要等有人抱怨慢才发现。
    """
    lines = ['# 由 tools/make_server_package.py 生成：服务器版离线安装清单']
    seen = {}
    for whl in sorted((stage_dir / 'vendor' / 'wheels').glob('*.whl')):
        parts = whl.name.split('-')
        if len(parts) < 2 or parts[0].lower() == 'pip':
            continue
        seen[parts[0].replace('_', '-')] = parts[1]
    for name, version in sorted(seen.items()):
        lines.append(f'{name}=={version}')
    (stage_dir / 'requirements-bundle.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return set(seen)


def main():
    parser = argparse.ArgumentParser(description='打 PyMaster 服务器部署包')
    parser.add_argument('--with-audio', action='store_true',
                        help='连讲解音频缓存一起打（包大很多，服务器上可省首次生成时间）')
    parser.add_argument('--skip-wheels', action='store_true', help='不重新下载 wheel')
    args = parser.parse_args()

    say('[1/4] 准备依赖 wheel')
    missing = [p for p in PACKAGES
               if not any(WHEELS.glob(f'{p.replace("-", "_")}-*.whl'))]
    if missing and not args.skip_wheels:
        say(f'  · 补齐缺失的包：{" ".join(missing)}')
        cmd = [sys.executable, '-m', 'pip', 'download', *missing, '-d', str(WHEELS),
               '--only-binary', ':all:', '-q', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            say('  ✗ 依赖下载失败：' + (result.stderr or '')[-400:])
            raise SystemExit(1)
    say(f'  · wheel 共 {len(list(WHEELS.glob("*.whl")))} 个')

    say('[2/4] 收集文件')
    stamp = datetime.now().strftime('%Y%m%d')
    name = f'PyMaster-服务器版-{stamp}'
    stage_dir = OUT_DIR / name
    stage(stage_dir, with_audio=args.with_audio)
    included = write_requirements_bundle(stage_dir)
    for must in ('flask', 'waitress', 'edge-tts'):
        if must not in included:
            say(f'  ✗ 安装清单里缺少 {must}（打包不完整）')
            raise SystemExit(1)
    say(f'  · 安装清单 {len(included)} 个包（含 waitress）')

    say('[3/4] 校验')
    problems = []
    for required in ('app.py', 'access_db.py', '一键上线.bat', '上线前自检.bat',
                     '0-启动PyMaster.bat', *SERVER_DOCS):
        if not (stage_dir / required).exists():
            problems.append(f'缺少 {required}')
    if not (stage_dir / 'runtime' / 'python-embed.zip').exists():
        problems.append('缺少随包 Python')
    if (stage_dir / '.env').exists():
        problems.append('包内出现了 .env（会泄露你的模型密钥）')
    for leak in ('data/users.json', 'data/.secret_key', 'data/access.db'):
        if (stage_dir / leak).exists():
            problems.append(f'包内出现了 {leak}（会泄露用户数据）')
    if not (stage_dir / 'static' / 'narrations').exists():
        problems.append('缺少讲解插画 static/narrations')
    bats = list(stage_dir.glob('*.bat'))
    if any(b.name not in ALLOWED_ROOT_BATS for b in bats):
        problems.append('根目录出现了不在白名单里的 bat：' +
                        ', '.join(b.name for b in bats if b.name not in ALLOWED_ROOT_BATS))
    if problems:
        for p in problems:
            say(f'  ✗ {p}')
        raise SystemExit(1)
    say('  · 校验通过')

    say('[4/4] 打包')
    archive = OUT_DIR / f'{name}.zip'
    make_zip(stage_dir, archive)
    size_mb = archive.stat().st_size / 1024 / 1024
    say(f'  ✓ {archive}')
    say(f'  · 体积 {size_mb:.1f} MB')
    say('')
    say('下一步：把 zip 上传到服务器，解压后双击「一键上线.bat」。')


if __name__ == '__main__':
    main()
