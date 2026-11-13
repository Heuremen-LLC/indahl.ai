#!/bin/zsh
# Matrix v2 driver: one model at a time on OUR seat (11500). Resumable: rerun to continue where it stopped.
export OLLAMA_HOST=127.0.0.1:11500
for m in gemma3:4b qwen3:4b phi4-mini mistral:7b llama3.1:8b granite3.3:2b olmo2:7b falcon3:3b smollm2:1.7b deepseek-r1:1.5b; do
  echo "== $m pull $(date +%H:%M:%S)"; /opt/homebrew/bin/ollama pull $m >/dev/null 2>&1 || { echo "PULL FAILED $m"; continue; }
  echo "== $m run $(date +%H:%M:%S)"; python3 -I run_matrix_v2.py $m || echo "RUN FAILED $m"
  /opt/homebrew/bin/ollama stop $m >/dev/null 2>&1
done
echo "== ALL DONE $(date +%H:%M:%S)"
