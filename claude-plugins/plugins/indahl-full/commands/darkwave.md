---
disable-model-invocation: true
description: Self-test, measure or apply the Darkwave readout-turn correction for IBM Quantum circuits
argument-hint: selftest | measure --backend B --readout 5,6 --targets 4,8 [--check] | apply --table T in.qpy out.qpy
---

Use the darkwave skill for: $ARGUMENTS

Never submit a hardware job (`--yes`) without showing the `--check` output first and getting the user's explicit go in this conversation.
If nothing was given, explain the three steps and offer the self-test.
