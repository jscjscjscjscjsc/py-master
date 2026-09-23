"""打一个"解压即用"的分发包。

为什么这么打
------------
用户反馈最多的失败是"双击启动脚本没反应"——根因基本都是没装 Python，
或者 pip 装不上库（校园网/公司网最容易被拦）。所以分发包里自带：

  · runtime/python-embed.zip   嵌入式 Python 3.12（约 11MB，不需要用户装）
  · vendor/wheels/*.whl        全部依赖的 wheel，离线安装
  · 0-启动PyMaster.bat         唯一入口，首次运行自动铺好环境

用户拿到压缩包只需要：解压 → 双击「0-启动PyMaster.bat」。

用法
----
    python tools/make_release.py                # 完整包（含随包 Python 与全部 wheel）
    python tools/make_release.py --lite         # 精简包（不含 pandas/matplotlib 等教学库）
    python tools/make_release.py --refresh      # 重新下载 wheel 与 Python
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'dist'
WHEELS = ROOT / 'vendor' / 'wheels'
RUNTIME_ZIP = ROOT / 'runtime' / 'python-embed.zip'
PY_VERSION = '3.12.10'
PY_URL = f'https://www.python.org/ftp/python/{PY_VERSION}/python-{PY_VERSION}-embed-amd64.zip'
MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple'

# 平台自身启动就要用的（缺了直接报错）
# waitress 是服务器模式的多线程服务器：本地版用不到，但带上它，
# 同一个包直接放到服务器上也能用，不必再单独补依赖。
CORE_PACKAGES = ['flask', 'edge_tts', 'waitress']
# 教材里的章节练习要用（第 13/17/24/26/28 章），缺了学生做题会 ImportError
TEACHING_PACKAGES = ['requests', 'pytest', 'fastapi', 'uvicorn', 'httpx', 'pandas', 'matplotlib', 'openai']

# 不打进分发包：讲解产物与用户数据（体积大或涉及隐私）
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'logs', 'docs', 'runtime', 'vendor', 'dist', 'tests',
    'static/narrations', 'static/narration-audio', 'data/audio_cache',
    'data/music_cache', 'data/training', 'data/coach', 'tools/render/node_modules',
    'tools/render/preview', 'tools/render/build-plan.json', '.video-build', '.workbuddy',
}
EXCLUDE_FILES = {
    '视频制作说明.md',
    'data/users.json', 'data/whitelist.json', 'data/daily_usage.json', 'data/.secret_key',
    'data/comic_memory.json', 'data/.build_narrations.lock',
    '更新说明-客户版.md', 'HANDOFF.md', 'PROGRESS.md', 'trend.png',
}
# 这些后缀之外的文件不进包（避免把日志、临时文件、密钥备份带上）
KEEP_SUFFIX = {'.py', '.json', '.txt', '.md', '.js', '.mjs', '.css', '.html', '.png',
               '.jpg', '.jpeg', '.svg', '.mp3', '.ico', '.woff', '.woff2', '.ttf',
               '.bat', '.sh', '.toml', '.cfg', '.env', '.example'}

# 学生最需要的两份文档，直接放压缩包根目录（不是藏在 docs/ 里）
DOC_FILES = ('大模型添加说明书和教程.md', '本地与云服务器部署教程.md')

README = """PyMaster 教学平台 · 使用说明
=====================================

【怎么启动】
  1. 把整个文件夹解压到任意目录（路径带中文、空格都没问题）
  2. 双击「0-启动PyMaster.bat」
  3. 首次启动会自动准备运行环境（约 1 分钟，不需要你安装 Python）
  4. 浏览器会自动打开 http://127.0.0.1:5000
     —— 没自动打开就手动访问这个地址

【第一次使用】
  在网页里完成：创建本地账号 → 填写模型密钥 → 开始学习。
  · 账号是纯本地的：用户名 + 密码，只存在你电脑的 data/users.json 里，
    不联网、不要邮箱、不会上传。
  · 登录一次之后会记住（一年内打开就是你自己），不用每次输密码。
  · 一台电脑可以存多个账号（比如家里两个孩子各一个）：点头像就能切换。
  · 头像可以上传照片，也可以直接选一个表情。
  模型密钥在「首次运行配置」页填写，支持任何 OpenAI 兼容接口
  （火山方舟、DeepSeek、硅基流动、本地 Ollama 等）。
  不填也能用：课程正文、练习、刷题、判题都可以离线跑，
  只有 AI 答疑、AI 批改、图文讲解生成需要模型。

【怎么停止】
  关闭那个黑色命令行窗口即可。

【常见问题】
  · 提示"没有找到 Python"
      说明你下的是精简包，请下载完整包；或自己装 Python 3.12
      （安装时勾选 Add python.exe to PATH）。
  · 提示端口 5000 被占用
      关掉其它 PyMaster 窗口再启动；本脚本会自动清理残留进程。
  · 杀毒软件报毒 / 拦截
      Python 启动本地服务的行为常被误判，把本文件夹加入白名单即可。
  · 依赖装不上
      完整包里的依赖是离线安装的，不需要网络；如果仍失败，
      多半是杀毒软件拦截，加白名单后重新双击启动。

【数据在哪】
  · 账号与学习记录：data/users.json
  · 头像图片：data/avatars/
  · 刷题档案：data/training/    教练会话：data/coach/
  · 图文讲解产物：static/narrations/（可删，删了会重新生成）
  备份直接拷 data 目录即可；换电脑把 data 拷过去就能接着学，
  账号、进度、错题、笔记、头像全都在里面。

【忘记密码怎么办】
  密码只在你自己的电脑上，没有"找回"通道。确实忘了就编辑
  data/users.json，把对应账号的 password 和 password_salt 两行删掉，
  再用同一个用户名重新注册即可（学习记录不会丢）。

【讲解与语音】
  五分钟图文讲解由大模型写分镜、本地程序化作图、edge-tts 合成口播。
  配图与音频不入包（体积大），需要时在平台上点「现在为这一节生成讲解」。
"""


def say(text):
    print(text, flush=True)


def download(url, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return target
    say(f'  · 下载 {url.rsplit("/", 1)[-1]} …')
    with urllib.request.urlopen(url, timeout=300) as response, open(target, 'wb') as out:
        shutil.copyfileobj(response, out)
    return target


def fetch_wheels(lite=False, refresh=False):
    packages = list(CORE_PACKAGES) + ([] if lite else list(TEACHING_PACKAGES))
    if refresh and WHEELS.exists():
        shutil.rmtree(WHEELS)
    WHEELS.mkdir(parents=True, exist_ok=True)
    if not refresh and any(WHEELS.glob('flask-*.whl')):
        say('  · wheel 已存在（--refresh 可重新下载）')
        return packages
    say(f'  · 下载依赖 wheel：{" ".join(packages)}')
    cmd = [sys.executable, '-m', 'pip', 'download', *packages, 'pip',
           '-d', str(WHEELS), '--only-binary', ':all:', '-q', '-i', MIRROR]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        say('  ✗ 依赖下载失败：' + (result.stderr or '')[-400:])
        raise SystemExit(1)
    return packages


def write_requirements_bundle(lite=False):
    """把 wheel 里的版本号固化成安装清单，保证离线安装可复现。"""
    lines = ['# 由 tools/make_release.py 生成：离线分发包按这份清单安装依赖']
    wheels = sorted(WHEELS.glob('*.whl'))
    seen = {}
    for whl in wheels:
        name, version = whl.name.split('-')[0], whl.name.split('-')[1]
        if name.lower() == 'pip':
            continue
        seen[name.replace('_', '-')] = version
    for name, version in sorted(seen.items()):
        lines.append(f'{name}=={version}')
    (ROOT / 'requirements-bundle.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return seen


def should_keep(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDE_FILES:
        return False
    for blocked in EXCLUDE_DIRS:
        if rel == blocked or rel.startswith(blocked + '/'):
            return False
    if any(part == '__pycache__' for part in path.parts):
        return False
    if path.name.startswith('.env.') and path.name != '.env.example':
        return False                                   # 密钥备份一律不进包
    if path.suffix.lower() not in KEEP_SUFFIX and path.name not in {'0-启动PyMaster.bat'}:
        return False
    return True


# 开发脚本：只在制作阶段用，运行时零引用（已逐个核对 app.py/*_engine.py）。
# 分发包里收进「开发脚本/」子目录 —— 学生解压后根目录越干净，越不容易点错东西。
DEV_SCRIPTS = ('build_comics.py', 'build_narrations.py', 'build_static_docs.py',
               'fix_json.py', 'setup_api.py', 'test_tts_api.py')
DEV_DOCS = ('上线部署方案.md', '评审在线试用指引.md')


def stage(stage_dir: Path, lite=False, doc_files=()):
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)
    count = 0
    for path in sorted(ROOT.rglob('*')):
        if path.is_dir() or not should_keep(path):
            continue
        target = stage_dir / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    # 根目录清爽化：开发脚本与内部文档移到子目录，不跟启动脚本抢眼球
    for name in DEV_SCRIPTS:
        src = stage_dir / name
        if src.exists():
            dest = stage_dir / '开发脚本'
            dest.mkdir(exist_ok=True)
            shutil.move(str(src), str(dest / name))
    for name in DEV_DOCS:
        src = stage_dir / name
        if src.exists():
            dest = stage_dir / '内部资料'
            dest.mkdir(exist_ok=True)
            shutil.move(str(src), str(dest / name))
    # 只留一个入口
    for extra in ('启动PyMaster.bat', '启动新版PyMaster.bat'):
        leftover = stage_dir / extra
        if leftover.exists():
            leftover.unlink()
    # 启动脚本也只允许一个：多一个就多一批人来问"我该点哪个"
    bats = sorted(stage_dir.glob('*.bat'))
    for bat in bats:
        if bat.name != '0-启动PyMaster.bat':
            bat.unlink()
            say(f'  · 移除多余启动脚本：{bat.name}')
    (stage_dir / 'runtime').mkdir(exist_ok=True)
    if RUNTIME_ZIP.exists():
        shutil.copy2(RUNTIME_ZIP, stage_dir / 'runtime' / 'python-embed.zip')
    shutil.copytree(WHEELS, stage_dir / 'vendor' / 'wheels', dirs_exist_ok=True)
    (stage_dir / '使用说明.txt').write_text(README, encoding='utf-8')
    # 学生最需要的两份文档，放根目录最显眼的位置
    for doc in doc_files:
        src = ROOT / doc
        if src.exists():
            shutil.copy2(src, stage_dir / doc)
        else:
            say(f'  ! 缺少文档 {doc}（正式发包前请先补齐）')
    (stage_dir / 'data').mkdir(exist_ok=True)
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


def main():
    parser = argparse.ArgumentParser(description='打 PyMaster 分发包')
    parser.add_argument('--lite', action='store_true', help='不含 pandas/matplotlib 等教学库')
    parser.add_argument('--refresh', action='store_true', help='重新下载 wheel 与 Python')
    parser.add_argument('--no-python', action='store_true', help='不打进随包 Python（用系统 Python）')
    parser.add_argument('--tag', default='', help='版本后缀，例如 v1.2')
    args = parser.parse_args()

    say('[1/5] 准备依赖 wheel')
    fetch_wheels(lite=args.lite, refresh=args.refresh)
    versions = write_requirements_bundle(lite=args.lite)
    say(f'  · 共 {len(versions)} 个包')

    say('[2/5] 准备随包 Python')
    if args.no_python:
        say('  · 跳过（--no-python）')
    else:
        download(PY_URL, RUNTIME_ZIP)
        say(f'  · {RUNTIME_ZIP.name} {RUNTIME_ZIP.stat().st_size / 1024 / 1024:.1f} MB')

    say('[3/5] 收集文件')
    stage_dir = OUT_DIR / 'PyMaster'
    count = stage(stage_dir, lite=args.lite, doc_files=DOC_FILES)
    say(f'  · {count} 个文件')

    say('[4/5] 校验完整性')
    problems = []
    if not (stage_dir / 'app.py').exists():
        problems.append('缺少 app.py')
    if not (stage_dir / '0-启动PyMaster.bat').exists():
        problems.append('缺少启动脚本 0-启动PyMaster.bat')
    if not args.no_python and not (stage_dir / 'runtime' / 'python-embed.zip').exists():
        problems.append('缺少随包 Python')
    for doc in DOC_FILES:
        if not (stage_dir / doc).exists():
            problems.append(f'缺少文档 {doc}')
    # 密钥与用户数据绝不能进包 —— 这两条一次都别放过
    if (stage_dir / '.env').exists():
        problems.append('包内出现了 .env（会泄露密钥）')
    if (stage_dir / 'data' / 'users.json').exists():
        problems.append('包内出现了 data/users.json（会泄露用户数据）')
    bats = list(stage_dir.glob('*.bat'))
    if len(bats) != 1:
        problems.append(f'启动脚本不是唯一一个，找到 {len(bats)} 个')
    # 根目录不该再出现开发脚本：它们已经收进「开发脚本/」，
    # 万一哪天有人往根目录又丢一个，这里会拦下来
    stray = [n for n in DEV_SCRIPTS if (stage_dir / n).exists()]
    if stray:
        problems.append('开发脚本还在根目录：' + '、'.join(stray))
    if problems:
        for item in problems:
            say('  ✗ ' + item)
        raise SystemExit(1)
    say('  · 校验通过（唯一入口 / 无密钥 / 文档齐全 / 根目录清爽）')

    say('[5/5] 打包')
    name = 'PyMaster_教学平台'
    if args.tag:
        name += '_' + args.tag
    if args.lite:
        name += '_精简版'
    archive = make_zip(stage_dir, OUT_DIR / f'{name}.zip')

    say('[5/5] 完成')
    size = archive.stat().st_size / 1024 / 1024
    say(f'  → {archive}')
    say(f'  → 压缩包 {size:.1f} MB')
    say('  用户拿到后：解压 → 双击「0-启动PyMaster.bat」')


if __name__ == '__main__':
    main()
