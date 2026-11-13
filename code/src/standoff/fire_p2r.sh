#!/bin/bash
# P2-R chain (6 Oct, Wayfinder: "go for amazon" / "Fire!"): round 1 after the 18:32Z recalibration, round 2 after 19:02Z. Cepheus's stamp read before each send.
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; L=fire_p2r.log
stamp(){ $PY -c "import rigetti_drift_probe as P; print(P.cal_stamp())" 2>/dev/null | tail -1; }
for spec in "1 2026-10-06T18:32" "2 2026-10-06T19:02"; do
  set -- $spec; r=$1; want=$2
  until [ "$(stamp | cut -c1-16)" \> "$want" ] || [ "$(stamp | cut -c1-16)" == "$want" ]; do sleep 30; done
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') round $r: Cepheus calibration $(stamp); sending" >> $L
  P2R_SAVE=lookLengths_r$r $PY rigetti_look_lengths.py submit 2>&1 | grep -vi warn | tail -4 | cut -c1-260 >> $L
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') round $r: sent" >> $L
done
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') P2-R chain done (collect: P2R_SAVE=lookLengths_rN python rigetti_look_lengths.py collect)" >> $L
