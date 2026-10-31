#!/bin/zsh
# Faults/Guards bench v2, second seat (PLAN.md here). Waits for the v1 second-seat drive to end (event wait), then one model at a time. Resumable.
cd "${0:A:h}"; export FB_URL=http://192.168.8.158:11434/api/chat
[ -n "$1" ] && caffeinate -w $1
for m in phi4-mini:latest gemma3:4b llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b qwen3:8b hermes3:latest deepseek-r1:8b mistral:7b-instruct-v0.3-q8_0 gpt-oss:20b; do
  echo "== $m $(date +%H:%M:%S)"; python3 run_armature.py $m || echo "RUN FAILED $m"
done
echo "== ALL REPLIES IN $(date +%H:%M:%S) (scoring waits for the parser hand-check, PLAN.md)"
