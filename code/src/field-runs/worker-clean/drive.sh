#!/bin/bash
# ticks the chain until every stage is done, failed or blocked; the perl alarm around this is the deadline
R=/Users/heuremen/bones-forge/claude-plugins/src/relay/scripts/relay.py
while true; do
  python3 $R tick chain.json >/dev/null
  S=$(python3 $R status chain.json | tail -1)
  echo "$(date +%H:%M:%S) $S"
  echo "$S" | grep -qE "waiting|running" || break
  perl -e 'select(undef,undef,undef,15)'
done
python3 $R status chain.json
