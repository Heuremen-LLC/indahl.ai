#!/bin/bash
# ys_drive.sh -- YO Read shuffled-label arm per PLAN_YO_SHUFFLED.md (+ Addenda 1-5), blocks 974519/974530 confirmed (974519 at 10:52:51Z).
# Trains shuf1-3 (seeds 71-73) one at a time, then scores each on the frozen rescore items. Replies written unread.
set -euo pipefail
cd "$HOME/bones-forge/yo/read/shuffled"; PY="$HOME/bones-forge/venv/bin/python"
for f in PLAN_YO_SHUFFLED*.sha256; do shasum -a 256 -c "$f" >/dev/null || { echo "FAILED: $f"; exit 1; }; done
cd ..; shasum -a 256 -c DATA_YO_RESCORE.sha256 >/dev/null || { echo "FAILED: rescore items"; exit 1; }; cd shuffled
for s in 1 2 3; do
  echo "== train shuf$s $(date -u +%FT%TZ)"; $PY -m mlx_lm lora -c "ys$s.yaml" > "ys${s}_train.log" 2>&1 || { echo "FAILED: training shuf$s"; exit 1; }
  shasum -a 256 "adapters/shuf$s/adapters.safetensors" >> ADAPTERS_YO_SHUFFLED.sha256
  echo "== shuf$s on rescore TEST $(date -u +%FT%TZ)"; (cd .. && $PY yr_rescore_eval.py yo "shuffled/adapters/shuf$s" > "shuffled/ys${s}_test.out" 2>&1) || { echo "FAILED: shuf$s on TEST"; exit 1; }
done
echo "== done $(date -u +%FT%TZ): replies unread; score per Addendum 1 next"
