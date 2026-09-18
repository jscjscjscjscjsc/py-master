#!/usr/bin/env python3
"""容器入口：理顺挂载卷的属主，然后降权起 gunicorn。

为什么需要它
------------
服务是以非 root 用户（pymaster, uid 10001）跑的，而 bind mount 和云盘挂上来
的目录属主通常还是 root —— 于是应用写不进去，表现是「注册账号报 500」
「学习进度存不下来」，而且日志里往往只有一句 Permission denied。

这里在启动前把可写目录的属主改成服务用户，再用 setuid 降权。
容器以 root 启动只是为了让这一步能做，真正的 Flask 进程仍是普通用户。

顺带把端口也接过来：平台（云托管 / PaaS）一般用 PORT 环境变量指定端口，
写死 5000 会连不上健康检查。
"""
import os
import pwd
import sys

APP_DIR = '/srv/pymaster'
DATA_DIR = (os.environ.get('PYMASTER_DATA_DIR') or '').strip() or os.path.join(APP_DIR, 'data')
SERVICE_USER = 'pymaster'

# 需要写的三处：用户数据、日志、讲解配图（本地生成讲解时会往里写）
WRITABLE = [
    DATA_DIR,
    os.path.join(APP_DIR, 'logs'),
    os.path.join(APP_DIR, 'static', 'narrations'),
]


def prepare_as_root():
    """root 身份下把可写目录交给服务用户，然后降权。"""
    try:
        account = pwd.getpwnam(SERVICE_USER)
    except KeyError:
        print(f'[entrypoint] 镜像里没有 {SERVICE_USER} 用户，保持当前身份运行', flush=True)
        return

    for path in WRITABLE:
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc:
            print(f'[entrypoint] 跳过 {path}：{exc}', flush=True)
            continue
        for current, dirs, files in os.walk(path):
            for name in [current] + [os.path.join(current, n) for n in dirs + files]:
                try:
                    os.chown(name, account.pw_uid, account.pw_gid)
                except OSError:
                    pass

    os.setgid(account.pw_gid)
    os.setuid(account.pw_uid)


def main():
    if os.geteuid() == 0:
        prepare_as_root()

    port = (os.environ.get('PORT') or '5000').strip()
    workers = (os.environ.get('PYMASTER_WORKERS') or '1').strip()
    # 线程给足：AI 答疑是 SSE 长连接，每路占一个线程；30 人的班同时问问题，
    # 8 个线程会互相排队。线程比 worker 省内存，所以加线程而不是加进程。
    threads = (os.environ.get('PYMASTER_THREADS') or '16').strip()

    print(f'[entrypoint] 以 {pwd.getpwuid(os.geteuid()).pw_name} 身份启动，'
          f'监听 0.0.0.0:{port}（workers={workers} threads={threads}）', flush=True)

    cmd = [
        'gunicorn',
        '--workers', workers,
        '--threads', threads,
        # 现场生成讲解要跑图片渲染，可能好几分钟；超时给短了会被 gunicorn 杀掉
        '--timeout', '600',
        '--graceful-timeout', '30',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '-b', f'0.0.0.0:{port}',
        'app:app',
    ]
    os.execvp(cmd[0], cmd)


if __name__ == '__main__':
    main()
