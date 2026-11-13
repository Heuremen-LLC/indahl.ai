#!/bin/bash
# yo7s_drive.sh -- YO v7 seed retest per PLAN_YO_V7S.md: seeds 53, 54, 55 of the v7 recipe (data7, start from YO v4). Known-good re-checked
# on TEST6; each seed trained and scored on TEST4 and TEST6; a live-reader pass between seeds; FUTURE7 scored for the three; all replies
# committed unread. No rate is read here: the replies are read in full before the comparison runs.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_V7S.md)" ] || { echo "FAILED: PLAN_YO_V7S.md is not clean in git"; exit 1; }
shasum -a 256 -c DATA_YO_V7.sha256 >/dev/null || { echo "FAILED: data7 does not match DATA_YO_V7.sha256"; exit 1; }
echo "== known-good on TEST6 $(date)"; $PY yo6_eval.py test6 oracle > yo7s_knowngood.out 2>&1
grep -q 'test6 oracle job A n .* mean 1.000' yo7s_knowngood.out || { echo "FAILED: known-good (oracle on TEST6) is not 1.000"; exit 1; }
"${GIT[@]}" add yo7s_knowngood.out
"${GIT[@]}" commit -q -m "YO v7 seed retest: known-good on TEST6 re-checked before the first new seed${TRAILER}"
for tag in 7c 7d 7e; do
  ad="v${tag}"
  echo "== train $ad $(date)"; $PY -m mlx_lm lora -c "yo${tag}.yaml" > "yo${tag}_train.log" 2>&1 || { echo "FAILED: training $ad"; exit 1; }
  echo "== $ad on TEST4 $(date)"; $PY yo4_eval.py yo "adapters/$ad" > "yo${tag}_test4.out" 2>&1 || { echo "FAILED: $ad on TEST4"; exit 1; }
  echo "== $ad on TEST6 $(date)"; $PY yo6_eval.py test6 yo "adapters/$ad" > "yo${tag}_test6.out" 2>&1 || { echo "FAILED: $ad on TEST6"; exit 1; }
  shasum -a 256 "adapters/$ad/adapters.safetensors" >> ADAPTERS_YO_V7S.sha256
  "${GIT[@]}" add ADAPTERS_YO_V7S.sha256 "yo${tag}_test4.out" "yo${tag}_test6.out" "eval4_yo_${ad}.jsonl" "eval6_test6_yo_${ad}.jsonl"
  "${GIT[@]}" commit -q -m "YO $ad: adapter hash and replies on TEST4 and TEST6, unread${TRAILER}"
  if [ "$tag" != "7e" ]; then echo "== live reader pass between seeds $(date)"; $PY yo_reader.py > yo${tag}_reader_pass.log 2>&1 || true; fi
done
for ad in v7c v7d v7e; do $PY yo6_eval.py future7 yo "adapters/$ad" >> yo7s_future.out 2>&1 || { echo "FAILED: $ad on FUTURE7"; exit 1; }; done
"${GIT[@]}" add yo7s_future.out eval6_future7_yo_v7c.jsonl eval6_future7_yo_v7d.jsonl eval6_future7_yo_v7e.jsonl
"${GIT[@]}" commit -q -m "YO v7 seed retest: FUTURE7 scored for v7c, v7d and v7e, unread${TRAILER}"
echo "== done $(date): read the replies in full before the comparison"
