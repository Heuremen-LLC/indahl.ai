#!/bin/bash
# yo6_drive.sh -- YO v6 per PLAN_YO_V6.md (9a19c00). Known-good, nulls and YO v4 on TEST6, committed before the first v6 step; seed 49 trained
# from the v4 adapter and scored on TEST4 and TEST6; one live-reader pass; seed 50 the same; FUTURE built and scored for v4, v6 and v6b; all
# replies committed unread. No rate is read here: the replies are read in full before yo6_compare.py runs.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_V6.md)" ] || { echo "FAILED: PLAN_YO_V6.md is not clean in git"; exit 1; }
shasum -a 256 -c DATA_YO_V6.sha256 >/dev/null || { echo "FAILED: data6 does not match DATA_YO_V6.sha256"; exit 1; }
echo "== nulls on TEST6 $(date)"; : > yo6_nulls.out; for m in oracle nothing all daterule; do $PY yo6_eval.py test6 $m >> yo6_nulls.out 2>&1; done
grep -q 'test6 oracle job A n .* mean 1.000' yo6_nulls.out || { echo "FAILED: known-good (oracle on TEST6) is not 1.000"; exit 1; }
echo "== v4 on TEST6 $(date)"; $PY yo6_eval.py test6 yo adapters/v4 > yo6_v4_on_test6.out 2>&1 || { echo "FAILED: v4 on TEST6"; exit 1; }
"${GIT[@]}" add DATA_YO_V6.sha256 yo6_data.py yo6_eval.py yo6_future.py yo6_compare.py yo6.yaml yo6b.yaml yo6_drive.sh yo6_nulls.out yo6_v4_on_test6.out eval6_test6_oracle.jsonl eval6_test6_nothing.jsonl eval6_test6_all.jsonl eval6_test6_daterule.jsonl eval6_test6_yo_v4.jsonl
"${GIT[@]}" commit -q -m "YO v6: data hashes, known-good, nulls and YO v4 on TEST6, before the first v6 training step${TRAILER}"
for tag in 6 6b; do
  ad="v${tag}"
  echo "== train $ad $(date)"; $PY -m mlx_lm lora -c "yo${tag}.yaml" > "yo${tag}_train.log" 2>&1 || { echo "FAILED: training $ad"; exit 1; }
  echo "== $ad on TEST4 $(date)"; $PY yo4_eval.py yo "adapters/$ad" > "yo${tag}_test4.out" 2>&1 || { echo "FAILED: $ad on TEST4"; exit 1; }
  echo "== $ad on TEST6 $(date)"; $PY yo6_eval.py test6 yo "adapters/$ad" > "yo${tag}_test6.out" 2>&1 || { echo "FAILED: $ad on TEST6"; exit 1; }
  shasum -a 256 "adapters/$ad/adapters.safetensors" >> ADAPTERS_YO_V6.sha256
  "${GIT[@]}" add ADAPTERS_YO_V6.sha256 "yo${tag}_test4.out" "yo${tag}_test6.out" "eval4_yo_${ad}.jsonl" "eval6_test6_yo_${ad}.jsonl"
  "${GIT[@]}" commit -q -m "YO $ad: adapter hash and replies on TEST4 and TEST6, unread${TRAILER}"
  if [ "$tag" = "6" ]; then echo "== live reader pass between seeds $(date)"; $PY yo_reader.py > yo6_reader_pass.log 2>&1 || true; fi
done
echo "== FUTURE $(date)"; $PY yo6_future.py > yo6_future.out 2>&1 || { echo "FAILED: FUTURE build"; exit 1; }
for ad in v4 v6 v6b; do $PY yo6_eval.py future6 yo "adapters/$ad" >> yo6_future.out 2>&1 || { echo "FAILED: $ad on FUTURE"; exit 1; }; done
"${GIT[@]}" add DATA_YO_V6_FUTURE.sha256 yo6_future.out eval6_future6_yo_v4.jsonl eval6_future6_yo_v6.jsonl eval6_future6_yo_v6b.jsonl
"${GIT[@]}" commit -q -m "YO v6: FUTURE items built and scored for v4, v6 and v6b, unread${TRAILER}"
echo "== done $(date): read the replies in full before the comparison"
