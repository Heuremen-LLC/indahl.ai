#!/bin/bash
# yo2_run.sh -- YO v2 end to end per PLAN_YO_V2.md (b634941): build data, known-good, nulls (committed), train live, score TEST once.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
echo "== build $(date)"; $PY yo2_data.py | tee yo2_data.out
echo "== known-good $(date)"; $PY yo2_eval.py oracle | tee known_good.out
grep -q "job A n 400 mean 1.000" known_good.out && grep -q "job C n 400 mean 1.000" known_good.out || { echo "FAILED: known-good scorer"; exit 1; }
$PY yo2_eval.py nothing | tee nulls.out
python3 - <<'PY' || { echo "FAILED: flag-nothing known-good"; exit 1; }
import json
it = [json.loads(l) for l in open('data2/test_items.jsonl') if '"job": "A"' in l]
both = sum(json.loads(i['answer']) == {'stale': [], 'zero': []} for i in it) / len(it)   # Addendum 1: half credit when one set is empty
one = sum((json.loads(i['answer'])['stale'] == []) != (json.loads(i['answer'])['zero'] == []) for i in it) / len(it); share = both + 0.5 * one
got = [l for l in open('nulls.out') if 'job A' in l][0]
assert abs(float(got.split('mean ')[1].split()[0]) - share) < 0.0005, (got, share); print('flag-nothing equals both-empty + half of one-empty', round(share, 4))
PY
echo "== nulls $(date)"; $PY yo2_eval.py consistent | tee -a nulls.out; $PY yo2_eval.py binary | tee -a nulls.out
$PY yo2_eval.py base | tee -a nulls.out
"${GIT[@]}" add DATA_YO_V2.sha256 yo2_data.out known_good.out nulls.out eval2_oracle.jsonl eval2_nothing.jsonl eval2_consistent.jsonl eval2_binary.jsonl eval2_base.jsonl yo2.yaml yo2_run.sh yo2_data.py yo2_eval.py yo2_compare.py yo2_publish.py
"${GIT[@]}" commit -q -m "YO v2: data hashes, known-good and every null scored, before the first training step${TRAILER}"
python3 yo2_publish.py || true
echo "== train $(date)"; $PY -m mlx_lm lora -c yo2.yaml > yo2_train.log 2>&1 || { echo "FAILED: training (see yo2_train.log)"; exit 1; }
python3 yo2_publish.py || true
echo "== test $(date)"; $PY yo2_eval.py yo adapters/v2 > yo2_test.out 2>&1 || { echo "FAILED: test scoring"; exit 1; }
echo "== done $(date): TEST scored to eval2_yo_v2.jsonl; read the replies in full before any rate"
