#!/bin/bash
# ONE's control leg on another day (Cepheus): the bottom rung (0.03) again after 00:05Z 7 Oct -- a new UTC day and a new calibration (Cepheus recalibrates :02/:32).
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; L=fire_p2r.log
until [ "$(date -u +%Y%m%d%H%M)" -ge 202610070005 ]; do sleep 30; done
P2R_STRENGTH=0.03 P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_s03_day2 $PY rigetti_look_lengths.py submit 2>&1 | grep -vi warn | tail -1 | cut -c1-160 >> $L
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') 0.03 day-2 sent" >> $L
P2R_STRENGTH=0.03 P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_s03_day2 $PY rigetti_look_lengths.py collect >> $L 2>&1
$PY ladder_widths.py lookLengths_s03.npz:0.03 lookLengths_s03b.npz:0.03 lookLengths_s03_day2.npz:0.03 2>&1 | grep -vi warn > ladder_s03_day2.txt
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') 0.03 day-2 read" >> $L
