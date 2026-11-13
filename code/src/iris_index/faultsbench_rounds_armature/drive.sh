#!/bin/zsh
# Faults/Guards rounds r2..r11, second seat (PLAN.md here, Addendum 1). Waits for the v2 second-seat drive to end (event wait). Round by round,
# model by model, deepseek-r1:8b last (all its rounds after everyone else's). Resumable.
cd "${0:A:h}"; export FB_URL=http://192.168.8.158:11434/api/chat
[ -n "$1" ] && caffeinate -w $1
R=(r2 r3 r4 r5 r6 r7 r8 r9 r10 r11)
for r in $R; do
  for m in phi4-mini:latest gemma3:4b llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b qwen3:8b hermes3:latest mistral:7b-instruct-v0.3-q8_0 gpt-oss:20b; do
    echo "== $r $m $(date +%H:%M:%S)"; (cd $r && python3 run_armature.py $m) || echo "RUN FAILED $r $m"
  done
done
for r in $R; do echo "== $r deepseek-r1:8b $(date +%H:%M:%S)"; (cd $r && python3 run_armature.py deepseek-r1:8b) || echo "RUN FAILED $r deepseek-r1:8b"; done
echo "== ALL ROUNDS IN $(date +%H:%M:%S) (scoring waits for the parser hand-check, PLAN.md)"
