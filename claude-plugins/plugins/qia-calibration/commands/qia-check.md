---
description: Check an IBM Quantum calibration record before a run, or the records in force during a run
argument-hint: before <record.json> [--qubits 0,1,5] | after <records_dir> --start <UTC> --end <UTC> [--qubits ...]
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/qia-calibration/qia_check-f7354879f19e.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/qia-calibration/scripts/qia_check.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != 'f7354879f19e47d2aac76a15951e125b2a3ce102e0af97aa9f1f75a6c81b7ede')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/qia-calibration/scripts/qia_check.py (sha256 f7354879f19e47d2aac76a15951e125b2a3ce102e0af97aa9f1f75a6c81b7ede).


Use the qia-check skill to run `python3 "$HOME/.cache/indahl-plugins/qia-calibration/qia_check-f7354879f19e.py" $ARGUMENTS` and report the result.

If nothing was given, ask whether this is before a run (one saved record) or after one (a folder of records plus the run's start and end
times from the job record).
