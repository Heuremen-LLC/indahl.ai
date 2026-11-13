# YO v1 -- plan (written 23 Oct 2026 before any YO v1 data was built or any model output was read). Wayfinder and Bones.
Base: Qwen/Qwen3-1.7B (Apache-2.0), LoRA with mlx-lm 0.31.3 on the Mac. Name: YO (his word, 23 Oct: "go for Yo!").

## Job A -- RECORD AUDIT (the pre-flight check)
Input: one IBM backend properties record, shown as its "last calibration" stamp plus 8 qubits drawn at random (seeded),
each with T1, T2, readout_error, prob_meas1_prep0, prob_meas0_prep1 as value + measurement date.
Answer (JSON, computed by code from the record, never written by hand):
  stale = qubits with a T1 or T2 date more than 24 h before the stamp; zero = qubit:field pairs whose error value is exactly 0.
Records: every distinct (backend, stamp) on disk (records.json), fake_* snapshots excluded.
Split by stamp: TEST = stamps on/after 2026-10-21 00:00 UTC; TRAIN/VALID = earlier (valid = last 10 % of train by stamp).
Score: per example, F1 of the stale set and of the zero set (both empty and predicted empty = 1). Mean over examples.

## Job B -- FAULT FAMILY
Input: one catch's "what" text from watch/tp_score.jsonl. Answer: its logged lesson (I, II, III, IV, V, VI, none).
Split by time: TEST = catches at/after 2026-10-21 00:00 EDT; TRAIN/VALID = earlier. Score: accuracy and per-class counts.

## Nulls (built and scored BEFORE training, on the same TEST items)
A: (1) flag nothing; (2) base Qwen3-1.7B with the same prompt and the rule stated in the prompt.
B: (1) majority class of TRAIN; (2) base Qwen3-1.7B with the seven family names + one-line definitions in the prompt.
## Rule
YO v1 counts on a job only if its TEST score beats BOTH nulls for that job by more than the bootstrap 95 % width
(2000 resamples of TEST items). Otherwise the job reads CONSISTENT with the null or CANNOT_TELL and is reported as such.
Both jobs reported side by side, all numbers, whatever they say.
