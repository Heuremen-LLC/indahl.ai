#!/bin/sh
# chain.sh NAME : after the slice-1 run for NAME ends, run slices 2,3,... as they appear. One writer per teacher file.
N=$1; cd /Users/heuremen/bones-forge/stan/scripts
while pgrep -f "run_teachers.py $N( 1)?\$" >/dev/null; do sleep 15; done
k=2
while true; do
  f=../data/slices/slice_$(printf %02d $k).json
  if [ -f $f ]; then python3 -u run_teachers.py $N $k >> ../teachers/run_$N.log 2>&1; k=$((k+1))
  elif grep -q '^done' ../data/build_slices.log 2>/dev/null; then break
  else sleep 30; fi
done
echo chain-ended >> ../teachers/run_$N.log
