#!/bin/bash
# 29 Oct: wait for the census to end, then run checker rounds until nothing is due. Event-driven (caffeinate -w), no timers.
cd ~/bones-forge/linkrot_index
P=$(pgrep -f "linkrot_collec[t]" | head -1); [ -n "$P" ] && caffeinate -w $P
for i in $(seq 1 12); do
  python3 -I linkrot_tick.py >> passes.log 2>&1
  python3 -c "import json;import sys;sys.exit(0 if json.load(open('summary_linkrot.json'))['due']==0 else 1)" && break
done
echo done >> passes.log
