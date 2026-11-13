#!/bin/bash
# yr_drive.sh -- YO Read per PLAN_YO_READ.md: known-good (truth 1.000), REGEX, MAJORITY and BASE on TEST, then seeds 61, 62, 63 trained
# and scored on TEST. All replies committed unread.
set -euo pipefail
cd "$HOME/bones-forge/yo/read"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_READ.md)" ] || { echo "FAILED: plan not clean"; exit 1; }
shasum -a 256 -c DATA_YO_READ.sha256 >/dev/null || { echo "FAILED: data does not match DATA_YO_READ.sha256"; exit 1; }
echo "== known-good $(date)"; $PY yr_eval.py truth > yr_knowngood.out 2>&1
grep -q 'truth n 444 unread 0 mean 1.000' yr_knowngood.out || { echo "FAILED: known-good"; exit 1; }
for m in regex majority base; do echo "== $m $(date)"; $PY yr_eval.py $m > yr_$m.out 2>&1 || { echo "FAILED: $m"; exit 1; }; done
"${GIT[@]}" add yr_knowngood.out yr_regex.out yr_majority.out yr_base.out eval_*.jsonl
"${GIT[@]}" commit -q -m "YO Read: known-good, REGEX, MAJORITY and BASE replies on TEST, unread${TRAILER}"
for s in 1 2 3; do
  echo "== train read$s $(date)"; $PY -m mlx_lm lora -c "yr$s.yaml" > "yr${s}_train.log" 2>&1 || { echo "FAILED: training read$s"; exit 1; }
  echo "== read$s on TEST $(date)"; $PY yr_eval.py yo "adapters/read$s" > "yr${s}_test.out" 2>&1 || { echo "FAILED: read$s on TEST"; exit 1; }
  shasum -a 256 "adapters/read$s/adapters.safetensors" >> ADAPTERS_YO_READ.sha256
  "${GIT[@]}" add ADAPTERS_YO_READ.sha256 "yr${s}_test.out" "eval_yo_read$s.jsonl"
  "${GIT[@]}" commit -q -m "YO Read seed 6$s: adapter hash and TEST replies, unread${TRAILER}"
done
echo "== done $(date): read the replies in full before the comparison"
