#!/bin/bash
# Waits for the blocks by calling the GATE ONLY (yf_gate.py, loads no model), then executes yf_drive.sh exactly once: that execution is the run (Addendum 6 item 4).
cd "$HOME/bones-forge/yo/read/fresh"; P="$HOME/bones-forge/archive/venv/bin/python"; O="$HOME/bones-forge/archive/venv/bin/ots"
F="PLAN_YO_FRESH.md PLAN_YO_FRESH_ADDENDUM1.md PLAN_YO_FRESH_ADDENDUM2.md PLAN_YO_FRESH_ADDENDUM3.md PLAN_YO_FRESH_ADDENDUM4.md PLAN_YO_FRESH_ADDENDUM5.md PLAN_YO_FRESH_ADDENDUM6.md"
while true; do for f in $F; do $O upgrade $f.ots >/dev/null 2>&1; done; $P yf_gate.py "$(date -u +%s)" $F > yf_gate_poll.log 2>&1; rc=$?; [ $rc -eq 0 ] && break; [ $rc -eq 1 ] && { echo "gate REFUSED, not running"; cat yf_gate_poll.log; exit 1; }; sleep 300; done
echo "== gate passed $(date -u +%FT%TZ); executing yf_drive.sh once (this is the run)" | tee -a RUN_STARTED.log
./yf_drive.sh > yf_drive.log 2>&1; echo "driver exit $?"; tail -3 yf_drive.log
