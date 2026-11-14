---
description: Check an IBM Quantum calibration record before a run, or the records in force during a run
argument-hint: before <record.json> [--qubits 0,1,5] | after <records_dir> --start <UTC> --end <UTC> [--qubits ...]
---

## Get the script first

The script is not stored in this plugin. Fetch it from the public Heuremen LLC repository at the pinned commit, check its
sha256, and only then run it. If the download or the check fails, stop and tell the user; never run a file that did not pass.
Show the user the commands before running them the first time.

```bash
F="$HOME/.cache/indahl-plugins/qia-calibration/qia_check-81e0444d70a4.py"
[ -f "$F" ] || { mkdir -p "$(dirname "$F")" && curl -fsSL "https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/8eb90a0f63bc694ccc6b53af485d1731b7a20956/claude-plugins/src/qia-calibration/scripts/qia_check.py" -o "$F.part" && python3 -c "import hashlib,sys; sys.exit(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest() != '81e0444d70a4325f9df4ac07737cfc0b3c6089ab66837fa3b07db158b8bec06f')" "$F.part" && mv "$F.part" "$F"; }
```
Source: https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/8eb90a0f63bc694ccc6b53af485d1731b7a20956/claude-plugins/src/qia-calibration/scripts/qia_check.py (sha256 81e0444d70a4325f9df4ac07737cfc0b3c6089ab66837fa3b07db158b8bec06f).


Use the qia-check skill to run `python3 "$HOME/.cache/indahl-plugins/qia-calibration/qia_check-81e0444d70a4.py" $ARGUMENTS` and report the result.

If nothing was given, ask whether this is before a run (one saved record) or after one (a folder of records plus the run's start and end
times from the job record).
