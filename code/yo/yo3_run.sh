#!/bin/bash
# yo3_run.sh -- YO v3 per PLAN_YO_V3.md (d70fcbe): v2 scored on TEST3 (null), committed; train v3 from the v2 adapter; score v3 on TEST3 once.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
echo "== v2 on TEST3 $(date)"; $PY yo3_eval.py yo adapters/v2 > yo3_v2_on_test3.out 2>&1; mv eval3_yo_v2.jsonl eval3_yo_v2.jsonl 2>/dev/null || true
"${GIT[@]}" add DATA_YO_V3.sha256 yo3_data.py yo3_eval.py yo3_compare.py yo3.yaml yo3_run.sh eval3_oracle.jsonl eval3_nothing.jsonl eval3_daterule.jsonl eval3_yo_v2.jsonl yo3_v2_on_test3.out
"${GIT[@]}" commit -q -m "YO v3: data hashes, known-good, flag-nothing, date rule and YO v2 scored on TEST3, before the first v3 training step${TRAILER}"
echo "== train $(date)"; $PY -m mlx_lm lora -c yo3.yaml > yo3_train.log 2>&1 || { echo "FAILED: training"; exit 1; }
echo "== test $(date)"; $PY yo3_eval.py yo adapters/v3 > yo3_test.out 2>&1 || { echo "FAILED: test"; exit 1; }
echo "== done $(date): read the replies in full before the comparison"
