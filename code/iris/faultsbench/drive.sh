#!/bin/zsh
# One model at a time on OUR seat (11500). Resumable: rerun to continue. One-shot overnight job (no timer, no loop over time).
cd "${0:A:h}"; export OLLAMA_HOST=127.0.0.1:11500
for m in phi4-mini mistral:7b falcon3:3b smollm2:1.7b llama3.1:8b gemma3:4b olmo2:7b granite3.3:2b qwen3:4b deepseek-r1:1.5b; do
  echo "== $m $(date +%H:%M:%S)"; python3 run.py $m || echo "RUN FAILED $m"
  /opt/homebrew/bin/ollama stop $m >/dev/null 2>&1
done
python3 score.py > score_run.txt 2>&1; echo "== ALL DONE $(date +%H:%M:%S)"
