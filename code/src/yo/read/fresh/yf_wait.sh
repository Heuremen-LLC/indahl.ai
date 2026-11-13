#!/bin/bash
# FRESH TEST launcher (not stamped; Sage A6 VERDICT 23:38Z conditions). Polls the GATE ONLY (yf_gate.py loads no model). When the gate passes it commits
# the upgraded proofs, then executes yf_drive.sh exactly once by its absolute path. Every driver exit is appended to RUN_STARTED.log and committed.
G="$HOME/bones-forge/yo"; cd "$G/read/fresh" || exit 1; echo "launcher $(shasum -a 256 "$G/read/fresh/yf_wait.sh" | cut -d" " -f1) started $(date -u +%FT%TZ)" >> RUN_STARTED.log; P="$HOME/bones-forge/archive/venv/bin/python"; O="$HOME/bones-forge/archive/venv/bin/ots"
F="PLAN_YO_FRESH.md PLAN_YO_FRESH_ADDENDUM1.md PLAN_YO_FRESH_ADDENDUM2.md PLAN_YO_FRESH_ADDENDUM3.md PLAN_YO_FRESH_ADDENDUM4.md PLAN_YO_FRESH_ADDENDUM5.md PLAN_YO_FRESH_ADDENDUM6.md"
while true; do for f in $F; do $O upgrade $f.ots >/dev/null 2>&1; done; $P yf_gate.py "$(date -u +%s)" $F > yf_gate_poll.log 2>&1; rc=$?; [ $rc -eq 0 ] && break; [ $rc -eq 1 ] && { echo "gate REFUSED, not running"; cat yf_gate_poll.log; exit 1; }; sleep 300; done
# upgraded proofs (with their Bitcoin attestations) and the gate's PASS lines go into git before the run; -f because yo/.gitignore ignores *.log
git -C "$G" add -f -- "$G"/read/fresh/PLAN_YO_FRESH*.md.ots "$G/read/fresh/yf_gate_poll.log" || { echo "FAILED: proof add; not running"; exit 1; }
git -C "$G" diff --cached --quiet || git -C "$G" commit -q -m "fresh: upgraded plan proofs and gate PASS lines committed before the run" || { echo "FAILED: proof commit; not running"; exit 1; }
git -C "$G" diff --quiet HEAD -- "$G"/read/fresh/PLAN_YO_FRESH*.md.ots || { echo "FAILED: proofs not committed; not running"; exit 1; }
echo "== gate passed $(date -u +%FT%TZ); executing $G/read/fresh/yf_drive.sh once (this is the run)" >> RUN_STARTED.log
"$G/read/fresh/yf_drive.sh" > yf_drive_run.log 2>&1; d=$?
echo "driver exit $d at $(date -u +%FT%TZ)" >> RUN_STARTED.log
git -C "$G" add -f -- "$G/read/fresh/RUN_STARTED.log" "$G/read/fresh/yf_drive_run.log" && git -C "$G" commit -q -m "fresh: run record (driver exit $d)" || echo "WARN: run-record commit failed; commit RUN_STARTED.log by hand"
tail -3 yf_drive_run.log
