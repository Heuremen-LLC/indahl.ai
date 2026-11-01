#!/bin/bash
# yo5_drive.sh -- YO v5 per PLAN_YO_V5.md (c3b5b8c). Known-good, nulls and YO v4 on TEST5, committed before the first v5 step; seed 47 trained
# from the v4 adapter and scored on TEST4 and TEST5; one live-reader pass; seed 48 the same; FUTURE built and scored for v4, v5 and v5b; all
# replies committed unread. No rate is read here: the replies are read in full before yo5_compare.py runs.
set -euo pipefail
cd "$HOME/bones-forge/yo"; PY="$HOME/bones-forge/venv/bin/python"
GIT=(git -c user.name=Bones -c user.email=268764679+claude-wayfinder@users.noreply.github.com)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW'
[ -z "$(git status --porcelain -- PLAN_YO_V5.md)" ] || { echo "FAILED: PLAN_YO_V5.md is not clean in git"; exit 1; }
shasum -a 256 -c DATA_YO_V5.sha256 >/dev/null || { echo "FAILED: data5 does not match DATA_YO_V5.sha256"; exit 1; }
echo "== nulls on TEST5 $(date)"; : > yo5_nulls.out; for m in oracle nothing all daterule; do $PY yo5_eval.py test5 $m >> yo5_nulls.out 2>&1; done
grep -q 'test5 oracle job A n .* mean 1.000' yo5_nulls.out || { echo "FAILED: known-good (oracle on TEST5) is not 1.000"; exit 1; }
echo "== v4 on TEST5 $(date)"; $PY yo5_eval.py test5 yo adapters/v4 > yo5_v4_on_test5.out 2>&1 || { echo "FAILED: v4 on TEST5"; exit 1; }
"${GIT[@]}" add DATA_YO_V5.sha256 yo5_data.py yo5_eval.py yo5_future.py yo5_compare.py yo5.yaml yo5b.yaml yo5_drive.sh yo5_nulls.out yo5_v4_on_test5.out eval5_test5_oracle.jsonl eval5_test5_nothing.jsonl eval5_test5_all.jsonl eval5_test5_daterule.jsonl eval5_test5_yo_v4.jsonl
"${GIT[@]}" commit -q -m "YO v5: data hashes, known-good, nulls and YO v4 on TEST5, before the first v5 training step${TRAILER}"
for tag in 5 5b; do
  ad="v${tag}"
  echo "== train $ad $(date)"; $PY -m mlx_lm lora -c "yo${tag}.yaml" > "yo${tag}_train.log" 2>&1 || { echo "FAILED: training $ad"; exit 1; }
  echo "== $ad on TEST4 $(date)"; $PY yo4_eval.py yo "adapters/$ad" > "yo${tag}_test4.out" 2>&1 || { echo "FAILED: $ad on TEST4"; exit 1; }
  echo "== $ad on TEST5 $(date)"; $PY yo5_eval.py test5 yo "adapters/$ad" > "yo${tag}_test5.out" 2>&1 || { echo "FAILED: $ad on TEST5"; exit 1; }
  shasum -a 256 "adapters/$ad/adapters.safetensors" >> ADAPTERS_YO_V5.sha256
  "${GIT[@]}" add ADAPTERS_YO_V5.sha256 "yo${tag}_test4.out" "yo${tag}_test5.out" "eval4_yo_${ad}.jsonl" "eval5_test5_yo_${ad}.jsonl"
  "${GIT[@]}" commit -q -m "YO $ad: adapter hash and replies on TEST4 and TEST5, unread${TRAILER}"
  if [ "$tag" = "5" ]; then echo "== live reader pass between seeds $(date)"; $PY yo_reader.py > yo5_reader_pass.log 2>&1 || true; fi
done
echo "== FUTURE $(date)"; $PY yo5_future.py > yo5_future.out 2>&1 || { echo "FAILED: FUTURE build"; exit 1; }
for ad in v4 v5 v5b; do $PY yo5_eval.py future yo "adapters/$ad" >> yo5_future.out 2>&1 || { echo "FAILED: $ad on FUTURE"; exit 1; }; done
"${GIT[@]}" add DATA_YO_V5_FUTURE.sha256 yo5_future.out eval5_future_yo_v4.jsonl eval5_future_yo_v5.jsonl eval5_future_yo_v5b.jsonl
"${GIT[@]}" commit -q -m "YO v5: FUTURE items built and scored for v4, v5 and v5b, unread${TRAILER}"
echo "== done $(date): read the replies in full before the comparison"
