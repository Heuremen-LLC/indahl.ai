#!/bin/zsh
# Thunderdome arena (THUNDERDOME_PLAN.md): rounds 12 and 13, the two finalists chosen by select_finalists.py (smollm2:1.7b and qwen3:4b), same items for both. Event-driven, no timer.
cd "${0:A:h}"; export OLLAMA_HOST=127.0.0.1:11500
for n in 12 13; do
  (cd faultsbench_r$n
   for m in smollm2:1.7b qwen3:4b; do echo "== $m $(date +%H:%M:%S)"; python3 run.py $m || echo "RUN FAILED $m"; /opt/homebrew/bin/ollama stop $m >/dev/null 2>&1; done) > faultsbench_r$n/drive_td.log 2>&1
  echo "ROUND $n DONE $(date +%H:%M)"
done
echo "THUNDERDOME ARENA DONE $(date +%H:%M)"
