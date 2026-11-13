#!/bin/zsh
# Runs rounds 3..11 back to back after round 2's driver exits. Event-driven: caffeinate -w waits on the process, no timer, no poll.
cd "${0:A:h}"; caffeinate -w 96377; echo "ROUND 2 DONE $(date +%H:%M)"
for n in 3 4 5 6 7 8 9 10 11; do
  (cd faultsbench_r$n && ./drive.sh > drive.log 2>&1); echo "ROUND $n DONE $(date +%H:%M)"
done
echo "ALL ELEVEN DONE $(date +%H:%M)"
