# YO v4, second seed -- plan (committed before this run's training, any of its output or any reading; times from git). Wayfinder and Bones.
Why: YO v4 is one training run with one seed (44), scored once. Both referees and the Check Block marked its seed width as unknown (L8).
This run measures it. It changes nothing about which model is at work: YO v4 (seed 44) stays the model at work whatever this run reads.
## Training
Identical to PLAN_YO_V4.md (8c5a448) in every setting and on the same data4 files (hashes in DATA_YO_V4.sha256), except seed 45 and the
adapter folder adapters/v4b. Continue from the YO v2 adapter, 1,200 iterations, learning rate 5e-5, batch 4, LoRA on 16 layers.
## Readings (on TEST4, the same items and scorer, all reported)
 S1 R1 to R4 for v4b, as PLAN_YO_V4 defines them.
 S2 The seed gap: v4b minus v4 on R1, R2, R4, paired bootstrap over TEST4 records (2,000 resamples, seed 51, 95 %), four outcomes with a
    0.02 margin, CONSISTENT printed as a bound.
 S3 Item flips between the two seeds, counted before any net: Job A items whose stale list differs, Job C items whose verdict differs,
    each direction.
 S4 v4b minus v2 on R1, as PLAN_YO_V4 compares v4 (does the second seed also clear v2).
## What it decides
 Nothing about the model at work. It prints the size of the seed gap, so every v4 reading can say how far a second seed moved it.
## KNOWN-GOOD
 The scorer gives 1.000 on the code's own TEST4 answers (eval4_oracle.jsonl, committed c4cd881). The v4 seed 44 outputs are already
 committed (ddd7a07), so S2 and S3 compare against a fixed file.

## ADDENDUM 1 (1 Nov 2026, after the seed 45 readings, before any seed 46 training or output; times from git)
Seed 45 put the four-outcome verdicts BELOW seed 44 and made 25 false flags against 1. Two seeds show a gap but not which seed is usual.
A third run, seed 46 (adapter adapters/v4c), on the same data4 files and settings, scored on TEST4 with the same code. Readings: S1 to S4
as above for v4c (v4c minus v4, and v4c minus v2 on R1), plus, across the three seeds, the range of R1, R3 (with its false-flag count), R4
and the forced-verdict count. It still decides nothing about the model at work.
