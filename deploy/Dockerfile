# PyMaster 完整版（Flask + Python 执行 + AI）的服务器镜像。
#
# 构建上下文是仓库根目录：
#   docker compose -f deploy/docker-compose.yml up -d --build
#
# 注意：镜像里带了 pandas / matplotlib，学生做第 26 章的数据分析题才跑得通；
# 代价是镜像约 1GB、空闲内存占用约 200MB，小内存机器（1核1G）会很吃力。
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=1 \
    PYMASTER_OPEN_BROWSER=0 \
    MPLBACKEND=Agg

WORKDIR /srv/pymaster

# 依赖单独一层，改代码时不用重装
COPY requirements.txt requirements-teaching.txt ./
RUN pip install -r requirements.txt edge_tts \
 && pip install -r requirements-teaching.txt

COPY . .

# 建服务用户，但容器本身仍以 root 启动 —— deploy/entrypoint.py 要 root 才能
# 把挂载卷的属主交给它，然后再 setuid 降权。真正的 Flask 进程不是 root。
RUN useradd -m -u 10001 pymaster \
 && mkdir -p data logs static/narrations user_notes \
 && chown -R pymaster:pymaster /srv/pymaster

# 平台（云托管 / PaaS）一般用 PORT 环境变量指定端口，入口会读它；本机 compose 走 5000
EXPOSE 5000

# 入口负责三件事：理顺挂载卷属主 → 降权到 pymaster → 用 gunicorn 起服务。
# 不用 flask 自带的开发服务器：AI 答疑是 SSE 流式返回，要给足线程才不会互相阻塞。
CMD ["python", "deploy/entrypoint.py"]
