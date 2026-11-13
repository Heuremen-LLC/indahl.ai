#!/bin/bash
# 29 Oct (ROUND_S1.md addendum 3): when the BBH plain run ends, read its result as the round script would, then end the paused round script so the lab queue can start Falcon round 3. The BBH chat run runs later as the queue job s1-bbh-chat.
PY=/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/trainenv/bin/python
cd ~/bones-forge/iris_index/claims_stack || exit 1
caffeinate -w "$1"
ls -d s1/bbh_plain/eval_* >/dev/null 2>&1 && touch s1/bbh_plain/done
$PY score_s1.py read > score_s1.log 2>&1
python3 - <<'PYEOF'
import json
p='state_s1.json'; d=json.load(open(p)); d['status']='Running. bbh_plain finished. The BBH chat run is deferred behind Falcon round 3.'; json.dump(d,open(p,'w'))
PYEOF
$PY publish_sad_live.py
echo "hand-off done $(date +%H:%M): bbh_plain read, round script ended, bbh_chat queued"
kill -TERM "$2"; kill -CONT "$2"
