#!/bin/sh
# One Armature worker so the three teachers never fight over the loaded-model slot. Slice 1 first (gemma remainder), then per slice: llama, mistral, gemma, crosstalk for all three.
cd /Users/heuremen/bones-forge/stan/scripts
for n in llama mistral gemma; do python3 -u run_teachers.py $n 1 >> ../teachers/run_$n.log 2>&1; done
for n in llama mistral gemma; do python3 -u crosstalk.py $n >> ../teachers/run_${n}_xt.log 2>&1; done
k=2
while true; do
  f=../data/slices/slice_$(printf %02d $k).json
  if [ -f $f ]; then
    for n in llama mistral gemma; do python3 -u run_teachers.py $n $k >> ../teachers/run_$n.log 2>&1; done
    for n in llama mistral gemma; do python3 -u crosstalk.py $n >> ../teachers/run_${n}_xt.log 2>&1; done
    k=$((k+1))
  elif grep -q '^done' ../data/build_slices.log 2>/dev/null; then break
  else sleep 30; fi
done
for n in llama mistral gemma; do python3 -u crosstalk.py $n >> ../teachers/run_${n}_xt.log 2>&1; echo chain-ended >> ../teachers/run_$n.log; echo xt-ended >> ../teachers/run_${n}_xt.log; done
