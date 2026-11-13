#!/bin/bash
# Waits for the Google sign-in on this Mac, then creates the project and the public dataset once and runs the first load.
G=/opt/homebrew/share/google-cloud-sdk/bin/gcloud
for i in $(seq 1 360); do
  A=$($G auth list --format='value(account)' 2>/dev/null | head -1)
  [ -n "$A" ] && break; sleep 5
done
[ -z "$A" ] && { echo "no sign-in after 30 minutes"; exit 1; }
echo "signed in"
cd ~/bones-forge/bq_index
BQ_SETUP=1 python3 bq_publish.py
python3 bq_publish.py
