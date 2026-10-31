# YO v2 -- plan (written 31 Oct 2026 ~17:40 EDT, before any v2 item was built, any null was scored or any v2 output was read). Wayfinder and Bones.
Question (PLAN_YO_PAPER.md, unchanged): can a small open-weight model (Qwen3-1.7B, Apache-2.0) be trained to read a vendor's stated device
calibration the way an auditor does: flag figures that are stale or zero under a fresh stamp (Job A), and give a FOUR-outcome verdict
(ABOVE / BELOW / CONSISTENT / CANNOT_TELL) instead of the two-outcome verdict models default to (Job C)?

## Why a v2 (the pilot, on record in project notes and eval_yo_v1.jsonl)
YO v1 answered "I" to every TEST item of both jobs. Causes found before this plan, none tested yet on v2 data: (1) training examples were cut at
max_seq_length 1024 and the record-audit prompts (8 qubits, full-precision floats) are near or over that, so many Job A answers were cut off
and the only answers left were the one-token fault labels of Job B, whose majority label is "I"; (2) loss was taken on prompt tokens too
("text" format); (3) TRAIN held 2020 ibmq records while TEST was 2026 Heron records. v2 changes all three and drops Job B (house labels).

## Data
- Records: yo/history/, pulled by pull_history2.py (every backend the service lists, properties(datetime=t) at 2-hour steps over the 180 days
  ending 31 Oct 2026 21:00 UTC, distinct stamps, zero QPU seconds). Every file used is hashed into DATA_YO_V2.sha256 before training starts.
  The v1 records.json (incl. 2020 ibmq records) is not used.
- Split by the record's last_update_date: TEST = on/after 2026-10-02 00:00 UTC; TRAIN = earlier; VALID = last 10 % of TRAIN records by stamp.
- Values are printed to 4 significant digits and dates to the minute (shorter prompts; the answer rules use the record's own values).
## Jobs (answers computed by code from the record, never written by hand)
- A. RECORD AUDIT, as v1: 8 qubits drawn per item (seeded), each with T1, T2, readout_error, prob_meas1_prep0, prob_meas0_prep1 and dates.
  stale = qubits whose T1 or T2 date is more than 24 h before the stamp; zero = qubit:field pairs whose error value is exactly 0.
  Answer: JSON {"stale": [...], "zero": [...]}, sorted. Score per item: mean of the F1 of the two sets (both empty and predicted empty = 1).
- C. FOUR-OUTCOME VERDICT: one qubit's stated T1 or T2 from the record is the reference r (microseconds). An estimate's 95 % interval is drawn
  (seeded): centre c = r (1 + delta), delta ~ U(-0.5, 0.5); relative half-width w ~ U(0.02, 0.40); [lo, hi] = [c (1 - w), c (1 + w)], 1 decimal.
  Equivalence margin d = 0.10 r. Truth, the rule stated in the prompt in this order: ABOVE if lo > r; BELOW if hi < r; CONSISTENT if
  r - d <= lo and hi <= r + d; otherwise CANNOT_TELL. Answer: the one word. Draws are kept so each split holds the four truths in equal numbers.
  Score: accuracy; also the FORCED-VERDICT RATE = share of CANNOT_TELL truths answered with anything else, and the full confusion table.
- Sizes (seeded): TRAIN 4,000 A + 4,000 C; VALID 200 A + 200 C; TEST 400 A + 400 C (C: 100 per truth). TEST items come from TEST records only.
## Training
mlx-lm 0.31.3, LoRA on 16 layers, Qwen/Qwen3-1.7B; completions format {prompt, completion} with mask_prompt true (loss on the answer only);
the tokenizer's own chat template; thinking off at evaluation (enable_thinking=False). max_seq_length 2048, and the builder REFUSES to write
the data if any TRAIN or VALID item (prompt + answer) exceeds it. 2,000 iterations, batch 4 (one pass over TRAIN), learning rate 1e-4,
grad checkpointing on, seed 31, validation loss every 250 steps, adapters saved every 250 steps. One GPU job on the Mac. No other model
server or model is used. TEST is read once, with the final adapter, after training ends.
## Nulls (scored on the same TEST items BEFORE training starts; their files committed before the first training step)
- A: flag nothing; base Qwen3-1.7B with the same prompt.  C: always CONSISTENT; the binary rule (ABOVE if lo > r, BELOW if hi < r, else
  CONSISTENT), which never says CANNOT_TELL; base Qwen3-1.7B with the same prompt. Greedy decoding everywhere, max 200 new tokens (A), 8 (C).
## KNOWN-GOOD
The scorer, given the code's own answers, must give 1.000 on both jobs, and flag-nothing must equal the share of TEST A items whose two
sets are both empty. If either fails, nothing is scored.
## Rule (four outcomes)
For YO minus each null, per job: paired bootstrap over TEST RECORDS (items from one record move together; 2,000 resamples, seed 31), 95 %.
ABOVE if the interval sits above 0; BELOW if below 0; CONSISTENT if it sits inside [-0.02, +0.02]; otherwise CANNOT_TELL.
Every job, every null, the forced-verdict rate and the confusion table are reported, whatever they say. No mechanism named.
## Live (indahl.ai)
While training runs the page shows only: the step, train and validation loss as mlx-lm prints them, and the null scores fixed before training.
The TEST reading appears after the run, once, with its intervals and four outcomes.
