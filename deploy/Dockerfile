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

# 不用 root 跑服务：判题会执行用户提交的代码，能少一分权限就少一分
RUN useradd -m -u 10001 pymaster \
 && mkdir -p data logs static/narrations \
 && chown -R pymaster:pymaster /srv/pymaster
USER pymaster

EXPOSE 5000
# 用 gunicorn 而不是 flask 自带的开发服务器；
# AI 答疑是 SSE 流式返回，所以要给足线程，否则会互相阻塞
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--timeout", "180", \
     "--graceful-timeout", "30", "-b", "0.0.0.0:5000", "app:app"]
