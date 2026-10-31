#!/bin/zsh
# Addendum 1: the restored four-slot server runs the five models today into out_4slot_today/.
cd "${0:A:h}"; export FB_URL=http://192.168.8.158:11434/api/chat
for m in phi4-mini:latest llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b; do
  echo "== $m $(date +%H:%M:%S)"; python3 run_armature_4today.py $m || echo "RUN FAILED $m"
done
echo "== ALL REPLIES IN $(date +%H:%M:%S)"
