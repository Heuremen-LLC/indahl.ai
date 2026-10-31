#!/bin/zsh
# Live bridge driver (PLAN.md): six sessions in the planned order, one at a time. Named *drive.sh so the lab queue sees the Mac GPU as busy.
cd "$(dirname "$0")"
[ "$(grep -c 'sha256 OK' fetch.log)" = 3 ] || { echo "FAILED: the three GGUF hashes are not all checked (fetch.log)"; exit 1; }
for s in "Q4_K_M 1" "Q4_K_M 2" "Q8_0 1" "Q8_0 2" "Q3_K_M 1" "Q3_K_M 2"; do
  f=${s% *}; k=${s#* }
  echo "== $f s$k $(date -u +%H:%M:%SZ)"
  /usr/bin/python3 -I bridge.py $f $k || echo "FAILED $f s$k"
done
echo "ALL SESSIONS ENDED $(date -u +%H:%M:%SZ)"
