#!/bin/zsh
# Bench v2 on the Mac seat for models first run on Armature (PLAN.md here). One model at a time on OUR seat (11500). Resumable.
cd "${0:A:h}"; export OLLAMA_HOST=127.0.0.1:11500
for m in llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b; do
  echo "== $m $(date +%H:%M:%S)"; python3 run.py $m || echo "RUN FAILED $m"
  /opt/homebrew/bin/ollama stop $m >/dev/null 2>&1
done
echo "== ALL REPLIES IN $(date +%H:%M:%S)"
