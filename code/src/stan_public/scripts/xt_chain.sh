#!/bin/sh
N=$1; cd /Users/heuremen/bones-forge/stan/scripts
while true; do
  python3 -u crosstalk.py $N >> ../teachers/run_${N}_xt.log 2>&1
  [ $(grep -l chain-ended ../teachers/run_llama.log ../teachers/run_mistral.log ../teachers/run_gemma.log 2>/dev/null | wc -l) -eq 3 ] && { python3 -u crosstalk.py $N >> ../teachers/run_${N}_xt.log 2>&1; break; }
  sleep 120
done
echo xt-ended >> ../teachers/run_${N}_xt.log
