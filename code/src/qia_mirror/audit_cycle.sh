#!/bin/bash
# 29 Oct, his word: a six-hourly check of IBM's published calibration. pull, audit (inside the mirror), independent recount, compare, log.
cd ~/bones-forge/qia_mirror || exit 1
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
export HEUREMEN_PUBLISH=1   # 10 Nov 2026 (publish guard): this launchd job puts qia_ibm, qia_audit, qia_stability and the Check a Run index to the site KV, as the tick bus riders do
~/bones-forge/qvenv/bin/python ibm_mirror.py >> audit_cycle.out 2>&1
python3 -I audit.py > audit_cycle.a 2>/dev/null
python3 -I recount.py > audit_cycle.r 2>/dev/null
norm() { sed -e "s/Counter({\(.*\)})/{\1}/" -e "s/Counter()/{}/" -e "s/'//g" "$1" | python3 -c "import sys,re;[print(' '.join(sorted(re.findall(r'[A-Za-z_]+|\d+',l))) ) for l in sys.stdin if l.startswith('ibm_')]" | sort; }
if [ "$(norm audit_cycle.a | grep -v qia_audit)" == "$(norm audit_cycle.r)" ]; then R=MATCH; else R=MISMATCH; fi
echo "$(date -u +%FT%TZ) recount $R" >> audit_cycle.log
# 2 Nov 2026: refresh the Check a Run index on /qia from the records just pulled (KV push, no deploy)
python3 -I ~/bones-forge/qia_runcheck/build_index.py >> ~/bones-forge/qia_runcheck/refresh.log 2>&1 && python3 -I ~/bones-forge/qia_runcheck/push_index.py >> ~/bones-forge/qia_runcheck/refresh.log 2>&1
