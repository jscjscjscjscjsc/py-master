#!/usr/bin/env bash
# 分批生产某一篇的图文讲解，失败自动重试。
#
# edge-tts 与大模型都是外部服务，偶发抖动会让个别小节失败；
# build_narrations.py 会把成功的落盘、失败的跳过，
# 所以这里循环几轮，用"重复跑 + 跳过已完成"的方式把缺口补齐。
#
# 用法：bash tools/batch_stage.sh "基础篇" [每轮上限] [最多轮数]
set -u

STAGE="${1:-基础篇}"
LIMIT="${2:-0}"
ROUNDS="${3:-6}"

cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
LOG="logs/batch_$(date +%Y%m%d_%H%M%S).log"

echo "=== 批量生产「${STAGE}」 ===" | tee -a "$LOG"
echo "日志：$LOG" | tee -a "$LOG"

for ((round = 1; round <= ROUNDS; round++)); do
  echo "" | tee -a "$LOG"
  echo "──────── 第 $round/$ROUNDS 轮 $(date +%H:%M:%S) ────────" | tee -a "$LOG"

  pending=$(python -u build_narrations.py --stage "$STAGE" --list 2>/dev/null \
            | grep -c '█' || true)
  args=(--stage "$STAGE")
  [ "$LIMIT" -gt 0 ] && args+=(--limit "$LIMIT")

  python -u build_narrations.py "${args[@]}" >>"$LOG" 2>&1
  status=$?

  # 每轮结束打印一次进度摘要
  python build_narrations.py --list 2>/dev/null | tee -a "$LOG"

  if [ $status -eq 0 ]; then
    remaining=$(python - <<'PY'
import json
from pathlib import Path
d = json.loads(Path('data/narrations.json').read_text(encoding='utf-8'))
c = json.loads(Path('data/courses.json').read_text(encoding='utf-8'))
want = [ch for ch in c if '基础篇' in ch.get('stage', '')]
total = sum(len(ch['knowledge_points']) for ch in want)
have = sum(1 for ch in want for i in range(len(ch['knowledge_points']))
           if f"{ch['id']}_{i}" in d)
print(total - have)
PY
)
    if [ "$remaining" -le 0 ]; then
      echo "" | tee -a "$LOG"
      echo "✅ 「${STAGE}」全部完成，用时见日志" | tee -a "$LOG"
      exit 0
    fi
    echo "  还有 $remaining 节未完成，30 秒后继续" | tee -a "$LOG"
  else
    echo "  本轮异常退出（exit=$status），60 秒后重试" | tee -a "$LOG"
    sleep 60
    continue
  fi
  sleep 30
done

echo "⚠ 已达最大轮数，仍有缺口；可再次运行本脚本续做" | tee -a "$LOG"
