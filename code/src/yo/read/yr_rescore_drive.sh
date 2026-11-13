#!/bin/bash
# yr_rescore_drive.sh -- PREREG_YO_RESCORE (fe751109). Known-good on the corrected items, then seeds 61, 62, 63 (existing adapters, no retraining), replies committed unread, then the frozen score.
set -euo pipefail
cd "$HOME/bones-forge/yo/read"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01MPZfWcyMxj86D4md9XjW4w'
shasum -a 256 -c DATA_YO_RESCORE.sha256 >/dev/null || { echo "FAILED: items do not match DATA_YO_RESCORE.sha256"; exit 1; }
shasum -a 256 -c ADAPTERS_YO_READ.sha256 >/dev/null || { echo "FAILED: adapters do not match ADAPTERS_YO_READ.sha256"; exit 1; }
echo "== known-good $(date)"; $PY yr_rescore_eval.py truth > yr_rescore_knowngood.out 2>&1
grep -q 'truth n 444 unread 0 mean 1.000' yr_rescore_knowngood.out || { echo "FAILED: known-good"; exit 1; }
for s in 1 2 3; do echo "== read$s $(date)"; $PY yr_rescore_eval.py yo "adapters/read$s" > "yr_rescore_${s}.out" 2>&1 || { echo "FAILED: read$s"; exit 1; }; done
"${GIT[@]}" add yr_rescore_knowngood.out yr_rescore_[123].out eval_rescore_*.jsonl
"${GIT[@]}" commit -q -m "YO rescore: known-good and seeds 61-63 replies on the corrected TEST items, unread${TRAILER}"
echo "== score $(date)"; $PY yr_rescore_score.py > yr_rescore_score.out 2>&1 || { echo "FAILED: score"; exit 1; }
echo "== done $(date)"
