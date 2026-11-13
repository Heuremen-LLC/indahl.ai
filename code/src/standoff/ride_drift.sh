#!/bin/bash
# Rides the drift probe all day: rounds at :04 :10 :16 :22 :28 :34 :40 :46 :52 :58 (2-26 min after Cepheus's :02/:32 recalibrations), inside the
# 09:00-19:00Z and 21:00-23:59Z windows; each round collected in the background. Stops at CAP dollars (est $26.85 a round).
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; CAP=${CAP:-600}; PER=26.85
n=$(ls time20261004/drift_r*_tasks.json 2>/dev/null | wc -l | tr -d ' '); spent=0
while true; do
  over=$(python3 -c "print(1 if $spent + $PER > $CAP else 0)"); [ "$over" = 1 ] && { echo "$(date -u) cap \$$CAP reached after $n rounds, stop" >> ride_drift.log; break; }
  H=$((10#$(date -u +%H))); M=$((10#$(date -u +%M)))
  inwin=0; { [ $H -ge 9 ] && [ $H -lt 19 ]; } && inwin=1; [ $H -ge 21 ] && inwin=1
  if [ $inwin = 1 ] && [ $((M % 6)) = 4 ]; then
    n=$((n+1)); echo "$(date -u) round $n submit" >> ride_drift.log
    if $PY rigetti_drift_probe.py submit $n >> ride_drift.log 2>&1; then spent=$(python3 -c "print($spent + $PER)"); ( $PY rigetti_drift_probe.py collect $n >> ride_drift.log 2>&1 ) &
    else echo "$(date -u) submit failed (login?), waiting 10 min" >> ride_drift.log; sleep 600; fi
    sleep 70
  else sleep 20; fi
  [ $H -ge 23 ] && [ $M -ge 55 ] && { echo "$(date -u) day's windows done" >> ride_drift.log; break; }
done
