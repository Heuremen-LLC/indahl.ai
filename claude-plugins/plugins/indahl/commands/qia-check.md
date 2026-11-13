---
description: Check an IBM Quantum calibration record before a run, or the records in force during a run
argument-hint: before <record.json> [--qubits 0,1,5] | after <records_dir> --start <UTC> --end <UTC> [--qubits ...]
---

Use the qia-check skill to run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/qia_check.py" $ARGUMENTS` and report the result.

If nothing was given, ask whether this is before a run (one saved record) or after one (a folder of records plus the run's start and end
times from the job record).
