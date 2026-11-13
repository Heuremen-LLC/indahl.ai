#!/bin/sh
cd /Users/heuremen/bones-forge/stan/scripts
while true; do
  python3 silver.py > /dev/null 2>&1
  n=$(python3 -c "import json;print(json.load(open('../results/silver_summary.json'))['train_rows'])")
  echo "$(date +%H:%M) train_rows $n" >> ../results/silver_watch.log
  [ "$n" -ge 250 ] && { echo THRESHOLD $n; break; }
  [ $(grep -l xt-ended ../teachers/run_*_xt.log 2>/dev/null | wc -l) -eq 3 ] && { echo ALL_DONE $n; break; }
  sleep 300
done
