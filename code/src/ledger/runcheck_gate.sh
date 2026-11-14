#!/bin/bash
# runcheck_gate.sh (13 Nov 2026): the Check a Run page must give the same answers as the qia-check package it mirrors.
# On 13 Nov the package's rules changed at 14:43 and the page and its index builder drifted for hours unnoticed.
# Runs qia_runcheck/tests/run_compare.py (about 5 minutes) only when the package, the page script, the index builder or the
# test itself changed since the last pass; the hashes of the last passing set are kept in ledger/.runcheck_gate_pass.
# Exit 0 = identical or unchanged since a pass. Exit 1 = MISMATCH (the ship is refused).
B=~/bones-forge
FILES="$B/qia_package/src/qia_check.py $B/cloudflare-workers/heuremen-door/public/qia/runcheck.js $B/qia_runcheck/public/qia/runcheck.js $B/qia_runcheck/build_index.py $B/qia_runcheck/tests/run_compare.py $B/qia_runcheck/tests/js_driver.js"
NOW=$(shasum -a 256 $FILES | shasum -a 256 | cut -c1-64)
PASS="$B/ledger/.runcheck_gate_pass"
if [ -f "$PASS" ] && [ "$(cat "$PASS")" == "$NOW" ]; then echo "runcheck gate: page and package unchanged since the last identical run"; exit 0; fi
if ! cmp -s "$B/cloudflare-workers/heuremen-door/public/qia/runcheck.js" "$B/qia_runcheck/public/qia/runcheck.js"; then echo "runcheck gate: the two copies of runcheck.js differ"; exit 1; fi
OUT=$(python3 -I "$B/qia_runcheck/tests/run_compare.py" 2>&1); LAST=$(echo "$OUT" | tail -1)
if [ "$LAST" == "ALL IDENTICAL" ]; then echo "$NOW" > "$PASS"; echo "runcheck gate: page and package ALL IDENTICAL (fixed cases and whole-history sweeps)"; exit 0; fi
echo "$OUT" | grep -v '^{' | head -20; echo "runcheck gate: MISMATCH between the Check a Run page and the qia-check package"; exit 1
