#!/usr/bin/env bash
# 分批生产图文讲解，失败自动重试。
#
# 外部服务（大模型 / edge-tts）偶发抖动会让个别小节失败，
# build_narrations.py 会把成功的落盘、失败的跳过，
# 所以这里循环几轮，用"重复跑 + 跳过已完成"把缺口补齐。
#
# 用法：
#   bash tools/batch_stage.sh                     # 全部篇章，直到做完
#   bash tools/batch_stage.sh "基础篇"            # 只做某一篇
#   bash tools/batch_stage.sh "全部" 50 3 6       # 全部，每轮最多 50 节，最多 3 轮，并发 6
set -u

STAGE="${1:-全部}"
LIMIT="${2:-0}"
ROUNDS="${3:-40}"
KP_WORKERS="${4:-4}"

cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
LOG="logs/batch_$(date +%Y%m%d_%H%M%S).log"

ARGS=(--kp-workers "$KP_WORKERS" --voice-workers 2)
if [ "$STAGE" != "全部" ] && [ -n "$STAGE" ]; then
  ARGS+=(--stage "$STAGE")
fi
[ "$LIMIT" -gt 0 ] && ARGS+=(--limit "$LIMIT")


# 预检：额度欠费 / 密钥失效时直接退出，不要空转几十轮
preflight() {
  python - <<'PYEOF'
import json, os, sys, urllib.request, urllib.error
from pathlib import Path
env = {}
f = Path('.env')
if f.exists():
    for line in f.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1); env[k.strip()] = v.strip()
key = os.environ.get('ARK_API_KEY') or env.get('ARK_API_KEY', '')
base = (os.environ.get('PYMASTER_AI_BASE_URL') or env.get('PYMASTER_AI_BASE_URL', '')).rstrip('/')
model = os.environ.get('PYMASTER_AI_MODEL') or env.get('PYMASTER_AI_MODEL', '')
if not (key and base and model):
    print('NO_CONFIG'); raise SystemExit(0)
body = json.dumps({'model': model, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 3}).encode()
req = urllib.request.Request(base + '/chat/completions', data=body,
    headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=25) as r:
        print('OK')
except urllib.error.HTTPError as e:
    detail = e.read().decode('utf-8', 'ignore')
    if 'Overdue' in detail or 'overdue' in detail:
        print('OVERDUE')
    elif e.code in (401, 403):
        print('AUTH')
    else:
        print('HTTP_' + str(e.code))
except Exception:
    print('NETWORK')
PYEOF
}

case "$(preflight)" in
  OK) : ;;
  OVERDUE)
    echo "✗ 模型账号欠费（AccountOverdueError），无法生成讲解。"
    echo "  请到火山方舟控制台充值后重新运行本脚本。"
    exit 2 ;;
  AUTH)
    echo "✗ API Key 无效或没有该模型权限，请重新运行启动脚本并检查配置。"
    exit 2 ;;
  NO_CONFIG)
    echo "✗ 还没有配置大模型，请先打开平台完成首次配置。"
    exit 2 ;;
  *)
    echo "⚠ 预检未能连上模型接口，仍尝试开始生产（可能是临时网络问题）。" ;;
esac

echo "=== 批量生产「${STAGE}」 并发 ${KP_WORKERS} ===" | tee -a "$LOG"
echo "日志：$LOG" | tee -a "$LOG"

remaining_total() {
  python - <<'PY'
import json
from pathlib import Path
try:
    narr = json.loads(Path('data/narrations.json').read_text(encoding='utf-8'))
    courses = json.loads(Path('data/courses.json').read_text(encoding='utf-8'))
    total = sum(len(c['knowledge_points']) for c in courses)
    have = sum(1 for c in courses for i in range(len(c['knowledge_points']))
               if f"{c['id']}_{i}" in narr)
    print(total - have)
except Exception:
    print(-1)
PY
}

for ((round = 1; round <= ROUNDS; round++)); do
  echo "" | tee -a "$LOG"
  echo "──────── 第 $round/$ROUNDS 轮 $(date +%H:%M:%S) ────────" | tee -a "$LOG"

  python -u build_narrations.py "${ARGS[@]}" >>"$LOG" 2>&1
  status=$?

  left=$(remaining_total)
  python -u build_narrations.py --list 2>/dev/null | head -3 | tee -a "$LOG"

  if [ "$left" -le 0 ]; then
    echo "" | tee -a "$LOG"
    echo "✅ 全部讲解已完成" | tee -a "$LOG"
    exit 0
  fi
  echo "  还有 $left 节未完成（本轮 exit=$status），30 秒后继续" | tee -a "$LOG"
  sleep 30
done

echo "⚠ 已达最大轮数，仍有缺口；可再次运行本脚本续做" | tee -a "$LOG"
