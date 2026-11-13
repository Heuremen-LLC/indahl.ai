#!/bin/bash
# yo8_drive.sh -- YO v8 per PLAN_YO_V8.md: known-good on TEST6 and TEST8C; YO v7, YO v4 and the nulls on TEST8C; seeds 56, 57, 58 trained
# from YO v7 on data8 and scored on TEST4, TEST6 and TEST8C; a live-reader pass between seeds. All replies committed unread.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_V8.md)" ] || { echo "FAILED: PLAN_YO_V8.md is not clean in git"; exit 1; }
shasum -a 256 -c DATA_YO_V8.sha256 >/dev/null || { echo "FAILED: data8 does not match DATA_YO_V8.sha256"; exit 1; }
echo "== known-good $(date)"; $PY yo6_eval.py test6 oracle > yo8_knowngood.out 2>&1; $PY yo6_eval.py test8c oracle >> yo8_knowngood.out 2>&1
grep -q 'test6 oracle job A n .* mean 1.000' yo8_knowngood.out && grep -q 'test8c oracle job C n 800 mean 1.000' yo8_knowngood.out || { echo "FAILED: known-good"; exit 1; }
for m in consistent binary; do $PY yo6_eval.py test8c $m >> yo8_nulls.out 2>&1; done
for ad in v7 v4; do echo "== $ad on TEST8C $(date)"; $PY yo6_eval.py test8c yo "adapters/$ad" >> yo8_ref_test8c.out 2>&1 || { echo "FAILED: $ad on TEST8C"; exit 1; }; done
"${GIT[@]}" add yo8_knowngood.out yo8_nulls.out yo8_ref_test8c.out eval6_test8c_*.jsonl
"${GIT[@]}" commit -q -m "YO v8: known-good on TEST6 and TEST8C; YO v7, YO v4 and nulls on TEST8C, unread${TRAILER}"
for tag in 8 8b 8c; do
  ad="v${tag}"
  echo "== train $ad $(date)"; $PY -m mlx_lm lora -c "yo${tag}.yaml" > "yo${tag}_train.log" 2>&1 || { echo "FAILED: training $ad"; exit 1; }
  echo "== $ad on TEST4 $(date)"; $PY yo4_eval.py yo "adapters/$ad" > "yo${tag}_test4.out" 2>&1 || { echo "FAILED: $ad on TEST4"; exit 1; }
  echo "== $ad on TEST6 $(date)"; $PY yo6_eval.py test6 yo "adapters/$ad" > "yo${tag}_test6.out" 2>&1 || { echo "FAILED: $ad on TEST6"; exit 1; }
  echo "== $ad on TEST8C $(date)"; $PY yo6_eval.py test8c yo "adapters/$ad" > "yo${tag}_test8c.out" 2>&1 || { echo "FAILED: $ad on TEST8C"; exit 1; }
  shasum -a 256 "adapters/$ad/adapters.safetensors" >> ADAPTERS_YO_V8.sha256
  "${GIT[@]}" add ADAPTERS_YO_V8.sha256 "yo${tag}_test4.out" "yo${tag}_test6.out" "yo${tag}_test8c.out" "eval4_yo_${ad}.jsonl" "eval6_test6_yo_${ad}.jsonl" "eval6_test8c_yo_${ad}.jsonl"
  "${GIT[@]}" commit -q -m "YO $ad: adapter hash and replies on TEST4, TEST6 and TEST8C, unread${TRAILER}"
  if [ "$tag" != "8c" ]; then echo "== live reader pass between seeds $(date)"; $PY yo_reader.py > yo${tag}_reader_pass.log 2>&1 || true; fi
done
echo "== done $(date): read the replies in full before the comparison"
