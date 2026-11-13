#!/bin/bash
# yo4_run.sh -- YO v4 per PLAN_YO_V4.md (8c5a448): nulls, v2 and v3 scored on TEST4 and committed; train v4 from the v2 adapter; score v4 once.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
echo "== nulls $(date)"; for m in oracle nothing daterule all; do $PY yo4_eval.py $m >> yo4_nulls.out 2>&1; done
grep -q 'oracle job A n .* mean 1.000' yo4_nulls.out && grep -q 'oracle job C n .* mean 1.000' yo4_nulls.out || { echo "FAILED: known-good (oracle) is not 1.000"; exit 1; }
echo "== v2 on TEST4 $(date)"; $PY yo4_eval.py yo adapters/v2 > yo4_v2_on_test4.out 2>&1
echo "== v3 on TEST4 $(date)"; $PY yo4_eval.py yo adapters/v3 > yo4_v3_on_test4.out 2>&1
"${GIT[@]}" add DATA_YO_V4.sha256 yo4_data.py yo4_eval.py yo4_compare.py yo4.yaml yo4_run.sh yo4_nulls.out eval4_oracle.jsonl eval4_nothing.jsonl eval4_daterule.jsonl eval4_all.jsonl eval4_yo_v2.jsonl eval4_yo_v3.jsonl yo4_v2_on_test4.out yo4_v3_on_test4.out
"${GIT[@]}" commit -q -m "YO v4: data hashes, known-good, nulls, YO v2 and YO v3 scored on TEST4, before the first v4 training step${TRAILER}"
echo "== train $(date)"; $PY -m mlx_lm lora -c yo4.yaml > yo4_train.log 2>&1 || { echo "FAILED: training"; exit 1; }
echo "== test $(date)"; $PY yo4_eval.py yo adapters/v4 > yo4_test.out 2>&1 || { echo "FAILED: test"; exit 1; }
echo "== done $(date): read the replies in full before the comparison"
