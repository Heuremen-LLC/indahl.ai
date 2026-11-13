#!/bin/bash
# collect the two weaker-strength sweeps (0.03, 0.06) when Cepheus finishes them, read each, circle into Wen (gather)
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; L=fire_p2r.log
for A in 0.03 0.06; do
  P2R_STRENGTH=$A P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_s${A#0.} $PY rigetti_look_lengths.py collect >> $L 2>&1
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') strength $A collected" >> $L
  P2R_NPZ=lookLengths_s${A#0.}.npz P2R_STRENGTH=$A P2R_KS=1,2,3,4 $PY readrigetti_look_lengths.py 2>&1 | grep -vi warn > read_strength_${A#0.}.txt
done
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') both strengths read" >> $L
