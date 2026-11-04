#!/bin/bash
# FRESH TEST driver (PLAN_YO_FRESH.md): refuses to run before the plan's Bitcoin block; checks every hash; runs the nine adapters on the fresh items, one GPU job at a time.
set -euo pipefail
cd "$HOME/bones-forge/yo/read/fresh"; PY="$HOME/bones-forge/venv/bin/python"; OTS="$HOME/bones-forge/archive/venv/bin/ots"
shasum -a 256 -c PLAN_YO_FRESH.sha256 >/dev/null || { echo "FAILED: plan hash"; exit 1; }
shasum -a 256 -c PLAN_YO_FRESH_ADDENDUM1.sha256 >/dev/null || { echo "FAILED: addendum 1 hash"; exit 1; }
shasum -a 256 -c PLAN_YO_FRESH_ADDENDUM2.sha256 >/dev/null || { echo "FAILED: addendum 2 hash"; exit 1; }
shasum -a 256 -c DATA_YO_FRESH.sha256 >/dev/null || { echo "FAILED: items or List hash"; exit 1; }
for o in PLAN_YO_FRESH.md.ots PLAN_YO_FRESH_ADDENDUM1.md.ots PLAN_YO_FRESH_ADDENDUM2.md.ots; do $OTS upgrade $o >/dev/null 2>&1 || true; done
# block gate (Sage, 4 Nov): verifies each proof against the current bytes and the block's merkle root, and the block time against this start.
NOW=$(date -u +%s); GATE_RC=0
"$HOME/bones-forge/archive/venv/bin/python" yf_gate.py "$NOW" PLAN_YO_FRESH.md PLAN_YO_FRESH_ADDENDUM1.md PLAN_YO_FRESH_ADDENDUM2.md || GATE_RC=$?
if [ "$GATE_RC" -eq 2 ]; then echo "WAIT: gate says wait"; exit 2; fi
if [ "$GATE_RC" -ne 0 ]; then echo "FAILED: gate refused (rc $GATE_RC)"; exit 1; fi
(cd .. && shasum -a 256 -c ADAPTERS_YO_READ.sha256 >/dev/null && cd shuffled && shasum -a 256 -c ADAPTERS_YO_SHUFFLED.sha256 >/dev/null && cd selflabel && shasum -a 256 -c ADAPTERS_SELFLABEL.sha256 >/dev/null) || { echo "FAILED: adapter hash"; exit 1; }
echo "== start $(date -u -r $NOW +%FT%TZ) (gate passed, see lines above)"
for a in adapters/read1 adapters/read2 adapters/read3 shuffled/selflabel/adapters/self1 shuffled/selflabel/adapters/self2 shuffled/selflabel/adapters/self3 shuffled/adapters/shuf1 shuffled/adapters/shuf2 shuffled/adapters/shuf3; do
  echo "== $a $(date -u +%FT%TZ)"; $PY yf_eval.py yo "../$a" > "out_$(basename $a).log" 2>&1 || { echo "FAILED: $a"; exit 1; }
done
shasum -a 256 eval_fresh_yo_*.jsonl out_*.log > OUTPUTS_YO_FRESH.sha256
$OTS stamp OUTPUTS_YO_FRESH.sha256 >/dev/null 2>&1 || echo "WARN: output stamp failed; stamp OUTPUTS_YO_FRESH.sha256 by hand now"
echo "== done $(date -u +%FT%TZ): outputs hashed and stamped (OUTPUTS_YO_FRESH.sha256.ots); replies unread; score with yf_score.py after the parser read"
