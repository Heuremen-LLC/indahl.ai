#!/bin/bash
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python
P2R_STRENGTH=0.03 P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_s03b $PY rigetti_look_lengths.py collect >> fire_p2r.log 2>&1
$PY ladder_widths.py lookLengths_s03.npz:0.03 lookLengths_s03b.npz:0.03 2>&1 | grep -vi warn > ladder_s03_repeat.txt
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') 0.03 repeat read" >> fire_p2r.log
