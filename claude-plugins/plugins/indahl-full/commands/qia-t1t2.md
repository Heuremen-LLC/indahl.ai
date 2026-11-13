---
disable-model-invocation: true
description: Measure T1 and T2 (Hahn echo) on chosen IBM qubits in one job and compare with IBM's published pair (self-test, estimate, or a paid run from your terminal)
argument-hint: --selftest | --backend B --qubits 85,12 --estimate | --flagged --backend B --estimate
---

Use the qia-check skill's "Measure T1 and T2 yourself" section for: $ARGUMENTS

Never add `--yes`. The paid submit runs only from the user's own terminal: show them the exact command and ask them to run it there.
If nothing was given, offer the self-test, which needs no device and no account.
