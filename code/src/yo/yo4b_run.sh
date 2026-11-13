#!/bin/bash
# yo4b_run.sh -- YO v4 second seed per PLAN_YO_V4B.md (f80660b): train seed 45 on data4 from the v2 adapter, score on TEST4 once.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
sha256sum -c DATA_YO_V4.sha256 2>/dev/null || shasum -a 256 -c DATA_YO_V4.sha256
echo "== train $(date)"; $PY -m mlx_lm lora -c yo4b.yaml > yo4b_train.log 2>&1 || { echo "FAILED: training"; exit 1; }
echo "== test $(date)"; $PY yo4_eval.py yo adapters/v4b > yo4b_test.out 2>&1 || { echo "FAILED: test"; exit 1; }
echo "== done $(date): read the replies in full before the comparison"
