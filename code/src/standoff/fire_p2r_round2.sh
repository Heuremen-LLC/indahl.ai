#!/bin/bash
# P2-R round 2 (replaces fire_p2r.sh's loop, which compared stamps as strings: an error string sorted after every date and released round 1 at
# 14:32:32 under the OLD 18:02Z calibration). Now: the stamp is parsed as a time; a failed read counts as "not yet"; send only once the
# stamp is at or after 19:02Z AND it is at least 2 minutes old (the recalibration settled).
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; L=fire_p2r.log
ready(){ $PY - <<'PY' 2>/dev/null
import datetime as D, rigetti_drift_probe as P
try:
    s = D.datetime.fromisoformat(P.cal_stamp()); now = D.datetime.now(D.timezone.utc)
    print('yes' if s >= D.datetime(2026, 10, 6, 19, 2, tzinfo=D.timezone.utc) and (now - s).total_seconds() >= 120 else 'no')
except Exception: print('no')
PY
}
until [ "$(ready | tail -1)" == "yes" ]; do sleep 30; done
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') round 2: Cepheus calibration $($PY -c 'import rigetti_drift_probe as P; print(P.cal_stamp())' 2>/dev/null | tail -1); sending" >> $L
P2R_SAVE=lookLengths_r2 $PY rigetti_look_lengths.py submit 2>&1 | grep -vi warn | tail -4 | cut -c1-260 >> $L
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') round 2: sent" >> $L
