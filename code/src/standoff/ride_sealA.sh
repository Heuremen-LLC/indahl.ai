#!/bin/bash
# Rides seal step A on Cepheus set after set (3 rounds, 130 tasks, ~$103 each) while the 00:00-06:59Z window is open; cap 4 sets (~$411). Each set saved beside the others.
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python
for n in 1 2 3 4; do
  h=$(date -u +%H); m=$(date -u +%M); [ $((10#$h*60+10#$m)) -ge 390 ] && { echo "$(date -u) window closing, stop at set $n" >> ride_sealA.log; break; }
  cal=$($PY -c "import boto3,json; d=boto3.client('braket',region_name='us-west-1').get_device(deviceArn='arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q'); print(json.loads(d['deviceCapabilities'])['service']['updatedAt'])" 2>/dev/null)
  echo "$(date -u) set $n submit (calibration $cal)" >> ride_sealA.log
  $PY rigetti_seal.py A-submit >> ride_sealA.log 2>&1 || { echo "$(date -u) submit failed, stop" >> ride_sealA.log; break; }
  $PY rigetti_seal.py A-collect >> ride_sealA.log 2>&1
  cp time20261004/sealA.npz time20261004/sealA_day2_set$n.npz; cp time20261004/sealA_tasks.json time20261004/sealA_tasks_day2_set$n.json
  echo "$(date -u) set $n collected" >> ride_sealA.log
done
echo "$(date -u) ride done" >> ride_sealA.log
