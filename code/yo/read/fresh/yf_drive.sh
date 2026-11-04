#!/bin/bash
# FRESH TEST driver (PLAN_YO_FRESH.md): refuses to run before the plan's Bitcoin block; checks every hash; runs the nine adapters on the fresh items, one GPU job at a time.
set -euo pipefail
cd "$HOME/bones-forge/yo/read/fresh"; PY="$HOME/bones-forge/venv/bin/python"; OTS="$HOME/bones-forge/archive/venv/bin/ots"
shasum -a 256 -c PLAN_YO_FRESH.sha256 >/dev/null || { echo "FAILED: plan hash"; exit 1; }
shasum -a 256 -c PLAN_YO_FRESH_ADDENDUM1.sha256 >/dev/null || { echo "FAILED: addendum 1 hash"; exit 1; }
shasum -a 256 -c DATA_YO_FRESH.sha256 >/dev/null || { echo "FAILED: items or List hash"; exit 1; }
for o in PLAN_YO_FRESH.md.ots PLAN_YO_FRESH_ADDENDUM1.md.ots; do $OTS upgrade $o >/dev/null 2>&1 || true
  $OTS info $o | grep -q BitcoinBlockHeaderAttestation || { echo "WAIT: $o not yet in a Bitcoin block"; exit 2; }; done
# block-time gate (Sage, 4 Nov): each file's attested block must be mined before this start time, read from mempool.space
NOW=$(date -u +%s)
for o in PLAN_YO_FRESH.md.ots PLAN_YO_FRESH_ADDENDUM1.md.ots; do
  H=$($OTS info $o | grep -oE 'BitcoinBlockHeaderAttestation\([0-9]+\)' | grep -oE '[0-9]+' | sort -n | head -1)
  BH=$(curl -fsS "https://mempool.space/api/block-height/$H") || { echo "WAIT: cannot read block $H"; exit 2; }
  BT=$(curl -fsS "https://mempool.space/api/block/$BH" | python3 -c 'import json,sys;print(json.load(sys.stdin)["timestamp"])') || { echo "WAIT: cannot read block time"; exit 2; }
  [ "$BT" -lt "$NOW" ] || { echo "FAILED: $o block $H time $BT not before start $NOW"; exit 1; }
  echo "gate: $o block $H mined $(date -u -r $BT +%FT%TZ), before start $(date -u -r $NOW +%FT%TZ)"
done
(cd .. && shasum -a 256 -c ADAPTERS_YO_READ.sha256 >/dev/null && cd shuffled && shasum -a 256 -c ADAPTERS_YO_SHUFFLED.sha256 >/dev/null && cd selflabel && shasum -a 256 -c ADAPTERS_SELFLABEL.sha256 >/dev/null) || { echo "FAILED: adapter hash"; exit 1; }
echo "== start $(date -u +%FT%TZ) blocks: plan $($OTS info PLAN_YO_FRESH.md.ots | grep -oE 'BitcoinBlockHeaderAttestation\([0-9]+\)' | head -1) addendum1 $($OTS info PLAN_YO_FRESH_ADDENDUM1.md.ots | grep -oE 'BitcoinBlockHeaderAttestation\([0-9]+\)' | head -1)"
for a in adapters/read1 adapters/read2 adapters/read3 shuffled/selflabel/adapters/self1 shuffled/selflabel/adapters/self2 shuffled/selflabel/adapters/self3 shuffled/adapters/shuf1 shuffled/adapters/shuf2 shuffled/adapters/shuf3; do
  echo "== $a $(date -u +%FT%TZ)"; $PY yf_eval.py yo "../$a" > "out_$(basename $a).log" 2>&1 || { echo "FAILED: $a"; exit 1; }
done
echo "== done $(date -u +%FT%TZ): replies unread; score with yf_score.py after the parser read"
