#!/bin/bash
# yo7_drive.sh -- YO v7 per PLAN_YO_V7.md (e313664). Known-good re-checked on TEST6; seed 51 trained from the v4 adapter and scored on TEST4
# and TEST6; one live-reader pass; seed 52 the same; FUTURE7 built and scored for v4, v7 and v7b; all replies committed unread. YO v4's and the
# nulls' scores on TEST4 and TEST6 are already committed. No rate is read here: the replies are read in full before yo7_compare.py runs.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_V7.md)" ] || { echo "FAILED: PLAN_YO_V7.md is not clean in git"; exit 1; }
shasum -a 256 -c DATA_YO_V7.sha256 >/dev/null || { echo "FAILED: data7 does not match DATA_YO_V7.sha256"; exit 1; }
echo "== known-good on TEST6 $(date)"; $PY yo6_eval.py test6 oracle > yo7_knowngood.out 2>&1
grep -q 'test6 oracle job A n .* mean 1.000' yo7_knowngood.out || { echo "FAILED: known-good (oracle on TEST6) is not 1.000"; exit 1; }
"${GIT[@]}" add DATA_YO_V7.sha256 yo7_data.py yo7_future.py yo7_compare.py yo6_eval.py yo7.yaml yo7b.yaml yo7_drive.sh yo7_knowngood.out
"${GIT[@]}" commit -q -m "YO v7: data hashes, known-good on TEST6, code, before the first v7 training step${TRAILER}"
for tag in 7 7b; do
  ad="v${tag}"
  echo "== train $ad $(date)"; $PY -m mlx_lm lora -c "yo${tag}.yaml" > "yo${tag}_train.log" 2>&1 || { echo "FAILED: training $ad"; exit 1; }
  echo "== $ad on TEST4 $(date)"; $PY yo4_eval.py yo "adapters/$ad" > "yo${tag}_test4.out" 2>&1 || { echo "FAILED: $ad on TEST4"; exit 1; }
  echo "== $ad on TEST6 $(date)"; $PY yo6_eval.py test6 yo "adapters/$ad" > "yo${tag}_test6.out" 2>&1 || { echo "FAILED: $ad on TEST6"; exit 1; }
  shasum -a 256 "adapters/$ad/adapters.safetensors" >> ADAPTERS_YO_V7.sha256
  "${GIT[@]}" add ADAPTERS_YO_V7.sha256 "yo${tag}_test4.out" "yo${tag}_test6.out" "eval4_yo_${ad}.jsonl" "eval6_test6_yo_${ad}.jsonl"
  "${GIT[@]}" commit -q -m "YO $ad: adapter hash and replies on TEST4 and TEST6, unread${TRAILER}"
  if [ "$tag" = "7" ]; then echo "== live reader pass between seeds $(date)"; $PY yo_reader.py > yo7_reader_pass.log 2>&1 || true; fi
done
echo "== FUTURE7 $(date)"; $PY yo7_future.py > yo7_future.out 2>&1 || { echo "FAILED: FUTURE7 build"; exit 1; }
for ad in v4 v7 v7b; do $PY yo6_eval.py future7 yo "adapters/$ad" >> yo7_future.out 2>&1 || { echo "FAILED: $ad on FUTURE7"; exit 1; }; done
"${GIT[@]}" add DATA_YO_V7_FUTURE.sha256 yo7_future.out eval6_future7_yo_v4.jsonl eval6_future7_yo_v7.jsonl eval6_future7_yo_v7b.jsonl
"${GIT[@]}" commit -q -m "YO v7: FUTURE7 items built and scored for v4, v7 and v7b, unread${TRAILER}"
echo "== done $(date): read the replies in full before the comparison"
