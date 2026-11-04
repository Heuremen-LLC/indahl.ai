#!/bin/bash
# FRESH TEST driver (PLAN_YO_FRESH.md): refuses to run before the plan's Bitcoin block; checks every hash; runs the nine adapters on the fresh items, one GPU job at a time.
set -euo pipefail
cd "$HOME/bones-forge/yo/read/fresh"; PY="$HOME/bones-forge/venv/bin/python"; OTS="$HOME/bones-forge/archive/venv/bin/ots"
shasum -a 256 -c PLAN_YO_FRESH.sha256 >/dev/null || { echo "FAILED: plan hash"; exit 1; }
shasum -a 256 -c DATA_YO_FRESH.sha256 >/dev/null || { echo "FAILED: items or List hash"; exit 1; }
$OTS upgrade PLAN_YO_FRESH.md.ots >/dev/null 2>&1 || true
$OTS info PLAN_YO_FRESH.md.ots | grep -q BitcoinBlockHeaderAttestation || { echo "WAIT: plan not yet in a Bitcoin block"; exit 2; }
(cd .. && shasum -a 256 -c ADAPTERS_YO_READ.sha256 >/dev/null && cd shuffled && shasum -a 256 -c ADAPTERS_YO_SHUFFLED.sha256 >/dev/null && cd selflabel && shasum -a 256 -c ADAPTERS_SELFLABEL.sha256 >/dev/null) || { echo "FAILED: adapter hash"; exit 1; }
echo "== start $(date -u +%FT%TZ) block: $($OTS info PLAN_YO_FRESH.md.ots | grep -oE 'BitcoinBlockHeaderAttestation\([0-9]+\)' | head -1)"
for a in adapters/read1 adapters/read2 adapters/read3 shuffled/selflabel/adapters/self1 shuffled/selflabel/adapters/self2 shuffled/selflabel/adapters/self3 shuffled/adapters/shuf1 shuffled/adapters/shuf2 shuffled/adapters/shuf3; do
  echo "== $a $(date -u +%FT%TZ)"; $PY yf_eval.py yo "../$a" > "out_$(basename $a).log" 2>&1 || { echo "FAILED: $a"; exit 1; }
done
echo "== done $(date -u +%FT%TZ): replies unread; score with yf_score.py after the parser read"
