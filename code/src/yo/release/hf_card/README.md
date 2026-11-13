---
license: apache-2.0
base_model: Qwen/Qwen3-1.7B
library_name: transformers
pipeline_tag: text-generation
language:
- en
tags:
- quantum-computing
- ibm-quantum
- calibration
- audit
- lora
- mlx
---

# YO

YO is a small open model that audits IBM Quantum calibration records. It is Qwen3-1.7B with a LoRA adapter, trained by Heuremen LLC on IBM's own published calibration history. This repository holds the merged model (root), the adapter alone (`adapter/`), and a tool that runs it on a whole record (`yo_audit.py`).

## What it does

Shown a record's last-calibration stamp and eight of its qubits, YO flags:

- **stale**: qubits whose T1 or T2 was measured more than 24 hours before the stamp
- **zero**: error values of exactly 0

It also gives a four-outcome verdict (ABOVE, BELOW, CONSISTENT, CANNOT_TELL) on a measured value against a stated reference.

These rules can be computed exactly by code, and `yo_audit.py` prints the code's answer beside YO's on every run. Where they differ, the code is right.

## Run it

Save a backend's calibration record from Qiskit (`backend.properties().to_dict()`, written with `json.dump(..., default=str)`), then:

```
pip install mlx-lm                       # Apple silicon
python yo_audit.py record.json --model indahl/YO

pip install transformers torch           # anywhere
python yo_audit.py record.json --fused indahl/YO
```

Every qubit with a T1 and a T2 value and date is audited, eight per prompt, in the same format YO was trained on.

## How it scored

On IBM records held out from training (426 records from 2 to 31 October 2026 that no earlier test used), against YO v2, the earlier model. Planned readings, with 95 % intervals over records:

- Records whose 8 qubits all sit 20 to 50 hours from their stamp: qubits stale by 24 to 48 hours found, 905 of 928 (YO v2: 403). Above, +0.54 [+0.45, +0.63].
- Record audit on the everyday mix of records: 0.990 (YO v2: 0.961). Above, +0.030 [+0.013, +0.048].
- Of the qubits YO flags as stale, 1,127 of 1,128 are stale (YO v2: 550 of 567). The interval clears zero resampled by record and reaches zero resampled by day, so this reads cannot tell.
- Four-outcome verdicts: 390 of 400 (YO v2: 377). Above, +0.032 [+0.010, +0.055], not credited to the training design, which did not target this job.

Defined after the data:

- Records with all 8 qubits stale: the stale list exactly right on 130 of 136 (YO v2: 53). YO still flags nothing on 3 of them and one qubit on 3.
- The everyday mix of records: 193 of 215 stale qubits found (YO v2: 119).
- Zero values: 115 of 119 found, with 4 false flags.
- By processor, in records whose 8 qubits all sit 20 to 50 hours from their stamp: 120 of 135 stale qubits found on ibm_boston and 72 of 80 on ibm_kingston, all of them on the other four.

## Seeds

This model is seed 44 of three training runs on the same plan, data and settings. Seed 44 was fixed in the plan before any data was built, seed 45 was planned before it was trained, and seed 46 was added to the plan after the seed 45 readings were seen. All three were scored once on the same 426 records. Stale qubits found in the whole-window records were 905, 928 and 920 of 928 (YO v2: 403), and the record audit was 0.990, 0.990 and 0.992 (YO v2: 0.961). Qubits flagged that were not stale were 1, 25 and 8, in 1, 4 and 2 of 390 audit items. CANNOT_TELL items given another verdict were 5, 24 and 11 of 100, and verdict scores were 390, 375 and 385 of 400 (YO v2: 377). This model has the fewest false flags and forced verdicts of the three, and also finds the fewest stale qubits over all audit items (1,127 of 1,172, against 1,165 and 1,164). The figures above are this adapter's. Another seed gave the different counts listed here, and three seeds are a small sample.

The plan was committed before any data was built. Plan, code and every reading: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo . The results table: https://indahl.ai/iris/lab

## YO v5, tried

YO v5 continued training YO v4 on 8,400 items, 2,400 of them same-date items (8 qubits from one record that share one calibration date) and the rest replay of earlier kinds, with two seeds fixed in the plan before any data was built (PLAN_YO_V5.md). On a new test set of same-date items it found 2,312 (seed 47) and 2,297 (seed 48) of 2,320 stale qubits, where YO v4 found 2,240. Seed 47's gain is above zero and seed 48's cannot be told from zero. None of the three flagged any of the 2,400 qubits in same-date items younger than a day. On YO v4's own test set seed 47 flagged 25 qubits that were not stale (YO v4 flagged 1, and, defined after the data, YO v4's own three seeds flagged 1, 25 and 8, all in items where 7 or 8 of the 8 qubits share one date younger than a day). Seed 48 gave a verdict to 45 of 100 items that had none (YO v4 gave 5). By the rule written before training YO v4 stays the model at work. Every reading: https://indahl.ai/iris/lab and https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo

## YO v6, tried

YO v6 continued training YO v4 on young groups whose date falls on the previous day and young groups with a stale qubit beside them, with two seeds (49 and 50) fixed in the plan before any data was built (PLAN_YO_V6.md). On a new test set of 890 items, seeds 49 and 50 flagged 2 and 1 of the 1,974 young qubits beside a stale one, where YO v4 flagged 94, and flagged 0 and 16 of 2,400 young previous-day qubits (YO v4 0). They found 2,297 and 2,305 of 2,320 older same-date stale qubits, where YO v4 found 2,249, and neither gain can be told from zero. Seed 49 found 864 of 928 qubits stale by 24 to 48 hours on YO v4's whole-window test, where YO v4 found 905, and seed 50 found 416 of 426 stale qubits beside young groups, where YO v4 found 424. By the rule written before training YO v4 stays the model at work. Every reading: https://indahl.ai/iris/lab and https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo

## YO v7, at work

YO v7 continued training YO v4 with YO v4's whole-window and band items restored beside the YO v6 kinds (PLAN_YO_V7). Of its first two seeds, 51 passed the plan rule and 52 did not (it found fewer stale qubits than YO v4), so a retest plan (PLAN_YO_V7S) retrained the same recipe with seeds 53, 54 and 55 and required all three to pass. All three did: on the older same-date items they found 1.000, 0.997 and 0.993 of 2,320 stale qubits, where YO v4 found 0.969, and none was shown to flag more young qubits or to find fewer stale ones. On the share of flags that are right they read 0.992 against YO v4's 0.999, and on the four-outcome verdict 0.960, 0.965 and 0.975 against 0.975, neither shown worse within the plan's bands. By the rule YO v7 seed 51 replaces YO v4 for the live reads from 1 November 2026. Every reading: https://indahl.ai/iris/lab and https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo

## YO v8, tried

YO v8 continued training YO v7 seed 51 with 2,400 verdict items near the edges of the four-outcome rule (PLAN_YO_V8), with seeds 56, 57 and 58. On 800 new border items from held-out records it scored 0.769, 0.754 and 0.765 exact against YO v7's 0.729 (seed 57's band reaches zero). On borders inside the margin all three seeds scored lower than YO v7 (0.835, 0.880 and 0.890 against 0.940). The plan needed all three seeds to pass. Seed 56 found 0.852 of 2,320 older same-date stale qubits against YO v7's 1.000, and seeds 57 and 58 flagged more young qubits beside stale ones (0.027 and 0.048 against 0.001). No seed passed, so YO v7 stays at work. The largest miss is the same for every version: an interval that ends just outside the margin is answered CONSISTENT where the rule says CANNOT_TELL. Every reading: https://indahl.ai/iris/lab and https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo

## Live

YO reads each new IBM calibration record as it is published, beside the code's answer, at https://indahl.ai/qia

## License

Apache-2.0, as the base model Qwen/Qwen3-1.7B. Trained on IBM Quantum calibration records as IBM publishes them.
