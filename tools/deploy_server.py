#!/usr/bin/env python3
"""把 PyMaster 推到一台服务器上跑起来（一条命令）。

它做的事
--------
1. 本地打包：代码 + 模板 + 静态资源 + 讲解产物（配图/口播）+ 课程数据
2. scp 上传到服务器（默认 /opt/pymaster）
3. ssh 过去：装 Docker（没装的话）→ 建卷目录 → docker compose up -d --build
4. 告诉你还差哪几步（DNS、访问口令、模型密钥）

用法
----
    # 先看看会打包什么、多大，不动服务器
    python tools/deploy_server.py --host root@1.2.3.4 --dry-run

    # 完整部署（约 1.4GB，含讲解配图与口播）
    python tools/deploy_server.py --host root@1.2.3.4 --domain learn.example.com

    # 只想先确认服务器能跑通，不传讲解产物（约 30MB）
    python tools/deploy_server.py --host root@1.2.3.4 --skip-media

    # 讲解产物单独补传（上次 --skip-media 之后）
    python tools/deploy_server.py --host root@1.2.3.4 --media-only

前提：本机能用 ssh/scp 免密登录那台服务器（配好公钥）。
Windows 用 Git Bash 或 PowerShell 都自带 OpenSSH，不需要额外装东西。
"""
import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE_NAME = 'pymaster-deploy'

# 不进包：运行环境、产物、缓存、版本库、以及本地才用得上的东西
EXCLUDE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', 'runtime', 'dist',
    'docs', 'logs', '.video-build', '.workbuddy', 'tests', 'preview',
    'static/audio', 'static/narration-audio',
    # 这两个是本地才用的：随包 Python 的离线 wheel 由镜像里的 pip 自己装；
    # 音乐缓存是 fetch_music.py 的下载中转，服务器只要 static/audio 里的成品
    'vendor/wheels', 'data/music_cache',
}
EXCLUDE_SUFFIX = {'.pyc', '.pyo', '.zip', '.log', '.bak'}

# 讲解产物：量大，但少了学生就听不到看不到。可以用 --skip-media 先不传
MEDIA_PATHS = ('static/narrations', 'data/audio_cache')

# 体积上限（超过就提醒一句，别让人以为卡死了）
SIZE_WARN = 3 * 1024 ** 3


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.1f} {unit}'
        n /= 1024


def is_excluded(rel: Path):
    parts = rel.parts
    # 逐级比对目录名，这样 tools/__pycache__/x.pyc 这类嵌套的也能拦下
    for i in range(len(parts) - 1):
        for depth in (1, 2):
            if i + depth <= len(parts) - 1:
                if '/'.join(parts[i:i + depth]) in EXCLUDE_DIRS:
                    return True
        if parts[i] in EXCLUDE_DIRS:
            return True
    return rel.suffix.lower() in EXCLUDE_SUFFIX


def collect(with_media=True):
    """列出要打包的文件，顺便算出体积。"""
    files = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if is_excluded(rel):
            continue
        if not with_media and any(rel.as_posix().startswith(m) for m in MEDIA_PATHS):
            continue
        files.append(rel)
    return files


def build_tarball(files, out_path: Path):
    """打一个不带压缩的 tar —— 讲解产物是 jpg/mp3，本来就压不动，
    gzip 只会白烧几分钟 CPU。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out_path, 'w') as tar:
        for rel in files:
            tar.add(ROOT / rel, arcname=f'{STAGE_NAME}/{rel.as_posix()}')
    return out_path


def run(cmd, **kw):
    print('  $', ' '.join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    return subprocess.run(cmd, **kw)


def check_ssh_tools():
    for tool in ('ssh', 'scp'):
        if not shutil.which(tool):
            sys.exit(f'找不到 {tool}。Windows 请确认已启用 OpenSSH 客户端'
                     '（设置 → 系统 → 可选功能），或用 Git Bash 打开本脚本。')


def remote(host, script, check=True):
    return run(['ssh', '-o', 'StrictHostKeyChecking=accept-new', host, script],
               check=check)


def main():
    ap = argparse.ArgumentParser(description='把 PyMaster 部署到一台服务器')
    ap.add_argument('--host', required=True, help='SSH 目标，例如 root@1.2.3.4')
    ap.add_argument('--dir', default='/opt/pymaster', help='服务器上的安装目录')
    ap.add_argument('--domain', default='', help='访问域名（用于提示，可选）')
    ap.add_argument('--skip-media', action='store_true',
                    help='不传讲解配图与口播（部署快很多，讲解页会是空的）')
    ap.add_argument('--media-only', action='store_true',
                    help='只补传讲解产物到已部署的服务器')
    ap.add_argument('--no-docker-install', action='store_true',
                    help='不在服务器上自动装 Docker')
    ap.add_argument('--dry-run', action='store_true', help='只打包并报告，不连服务器')
    args = ap.parse_args()

    with_media = not args.skip_media
    files = collect(with_media=with_media)
    if args.media_only:
        files = [f for f in files
                 if any(f.as_posix().startswith(m) for m in MEDIA_PATHS)]
    total = sum((ROOT / f).stat().st_size for f in files)

    print('=' * 58)
    print(f'  打包清单：{len(files)} 个文件，合计 {human(total)}')
    print(f'  含讲解产物：{"是" if with_media or args.media_only else "否"}')
    print(f'  目标：{args.host}:{args.dir}')
    print('=' * 58)
    if total > SIZE_WARN and not args.dry_run:
        print(f'  ⚠ 体积 {human(total)} 偏大，上传会慢，先确认服务器磁盘够用。')
    if not args.dry_run:
        print('  （大文件多，预计几分钟到十几分钟，取决于上行带宽）\n')

    tarball = ROOT / 'dist' / 'pymaster-deploy.tar'
    if args.media_only:
        tarball = ROOT / 'dist' / 'pymaster-media.tar'
    print('[1/4] 打包…')
    t0 = time.time()
    build_tarball(files, tarball)
    print(f'      -> {tarball}  {human(tarball.stat().st_size)}  '
          f'用时 {time.time() - t0:.0f}s')

    if args.dry_run:
        print('\n--dry-run：已生成 tar，未连接服务器。')
        return

    check_ssh_tools()

    if not args.media_only:
        print('\n[2/4] 准备服务器环境…')
        remote(args.host, f'mkdir -p {args.dir}')
        if not args.no_docker_install:
            remote(args.host,
                   'command -v docker >/dev/null 2>&1 || '
                   '(curl -fsSL https://get.docker.com | sh)', check=False)
        remote(args.host,
               f'cd {args.dir} && mkdir -p deploy/runtime-data '
               f'deploy/static-narrations deploy/logs && touch deploy/env')

    print('\n[3/4] 上传…')
    remote(args.host, f'cd {args.dir} && rm -rf {STAGE_NAME}.old && '
                      f'(mv {STAGE_NAME} {STAGE_NAME}.old 2>/dev/null || true)')
    run(['scp', '-C', str(tarball), f'{args.host}:{args.dir}/'])
    remote(args.host, f'cd {args.dir} && tar -xf {tarball.name} && rm -f {tarball.name}')

    if args.media_only:
        # 只把讲解产物搬到卷目录里
        remote(args.host, f'cd {args.dir}/{STAGE_NAME} && '
                          f'rm -rf ../deploy/runtime-data/audio_cache && '
                          f'mkdir -p ../deploy/runtime-data && '
                          f'cp -r data/audio_cache ../deploy/runtime-data/ && '
                          f'rm -rf ../deploy/static-narrations/* && '
                          f'cp -r static/narrations/. ../deploy/static-narrations/')
        remote(args.host, f'cd {args.dir} && docker compose '
                          f'-f deploy/docker-compose.yml restart pymaster')
        print('\n讲解产物已补传并重启服务。')
        print(f'   → http://{args.host.split("@")[-1]}')
        return

    print('\n[4/4] 构建并启动（首次约 5–10 分钟）…')
    remote(args.host, f'cd {args.dir}/{STAGE_NAME} && '
                      f'docker compose -f deploy/docker-compose.yml up -d --build')

    print('\n' + '=' * 58)
    print('  服务已起。还差三步：')
    print('=' * 58)
    print(f'''
  1) 把域名 A 记录指向服务器公网 IP
     {'（域名：' + args.domain + '）' if args.domain else ''}

  2) 设置访问口令（只有 30 人用，务必设，否则链接一传开谁都能进）
     ssh {args.host}
     cd {args.dir}/deploy
     cp .env.example .env
     docker run --rm caddy:2 caddy hash-password --plaintext '你想设的口令'
     vi .env          # 填 DOMAIN / BASIC_USER / BASIC_HASH
     cd .. && docker compose -f deploy/docker-compose.yml up -d caddy

  3) 填模型密钥（不填也能用，只是没有 AI 答疑和批改）
     ssh {args.host} "vi {args.dir}/deploy/env"
     内容三行：
       PYMASTER_AI_BASE_URL=https://opencode.ai/zen/go/v1
       PYMASTER_AI_MODEL=deepseek-v4.1-flash
       ARK_API_KEY=你的密钥
     存盘后：docker compose -f deploy/docker-compose.yml restart pymaster

  之后学生访问 https://{"你的域名" if not args.domain else args.domain} → 输入口令 → 注册账号 → 开始学。
  健康检查：docker compose -f deploy/docker-compose.yml logs -f pymaster
''')


if __name__ == '__main__':
    main()
