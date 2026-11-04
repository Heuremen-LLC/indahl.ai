#!/bin/bash
# SELF-LABEL arm driver (Addenda 2-5, GO_ORDER): base-rate report first, then train self1-3 (seeds 74-76), then run each on the rescore TEST. One GPU job at a time.
set -euo pipefail
cd "$HOME/bones-forge/yo/read/shuffled"; PY="$HOME/bones-forge/venv/bin/python"
for f in PLAN_YO_SHUFFLED*.sha256; do shasum -a 256 -c "$f" >/dev/null || { echo "FAILED: $f"; exit 1; }; done
(cd .. && shasum -a 256 -c DATA_YO_RESCORE.sha256 >/dev/null) || { echo "FAILED: rescore items"; exit 1; }
cd selflabel
echo "== base-rate report start $(date -u +%FT%TZ)"; $PY sl_base.py > sl_base.out 2>&1 || { echo "FAILED: base-rate report"; exit 1; }
test -s BASE_RATES.text || { echo "FAILED: no BASE_RATES.text"; exit 1; }
shasum -a 256 BASE_RATES.text data/train.jsonl data/valid.jsonl > DATA_SELFLABEL.sha256
echo "== base-rate report written $(date -u +%FT%TZ)"
for s in 1 2 3; do
  echo "== train self$s $(date -u +%FT%TZ)"; $PY -m mlx_lm lora -c "sl$s.yaml" > "sl${s}_train.log" 2>&1 || { echo "FAILED: training self$s"; exit 1; }
  shasum -a 256 "adapters/self$s/adapters.safetensors" >> ADAPTERS_SELFLABEL.sha256
  echo "== self$s on rescore TEST $(date -u +%FT%TZ)"; (cd ../.. && $PY yr_rescore_eval.py yo "shuffled/selflabel/adapters/self$s" > "shuffled/selflabel/sl${s}_test.out" 2>&1) || { echo "FAILED: self$s on TEST"; exit 1; }
done
echo "== done $(date -u +%FT%TZ): replies unread; score per Addendum 2 next"
