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
- Weaker on some processors: in records whose 8 qubits all sit 20 to 50 hours from their stamp, 120 of 135 stale qubits found on ibm_boston and 72 of 80 on ibm_kingston, all of them on the other four.

One training run, one seed, scored once. The plan was committed before any data was built. Plan, code and every reading: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/yo . The results table: https://indahl.ai/iris/lab

## Live

YO reads each new IBM calibration record as it is published, beside the code's answer, at https://indahl.ai/qia

## License

Apache-2.0, as the base model Qwen/Qwen3-1.7B. Trained on IBM Quantum calibration records as IBM publishes them.
