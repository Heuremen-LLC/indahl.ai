# YO v5 -- plan (committed before any v5 item was built, any v5 null scored or any v5 output read; times from git). Wayfinder and Bones.
Why (defined after the data, from the live reads of YO v4 on QIA): YO v4 read 69 new IBM records live and was exact on 66. In the ibm_pittsburgh
record stamped 2026-11-01 05:25 UTC all 8 qubits it was shown carried the same older T1/T2 date, 32.6 h before the stamp, so all 8 were stale,
and YO v4 flagged none. In the ibm_pittsburgh record of 2026-10-31 23:17 UTC every qubit was stale and the 7 that YO v4 missed sat in one prompt.
Training so far drew qubits with mixed dates. A record whose qubits were calibrated in one batch shows one date on every line, and on both sides
of 24 h the answer is all or nothing. Wayfinder, 1 Nov: "Can we get some training going for the Mac lab please?"
## Training
Continue from the YO v4 adapter (the model at work; adapters/v4/adapters.safetensors, sha256 starting 4737100d6e008afa), same base (Qwen3-1.7B),
same prompt format and chat template, completions with mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5,
1,200 iterations, validation every 200 steps. Two seeds, run one after the other on the Mac: seed 47 (adapters/v5) and seed 48 (adapters/v5b).
One GPU job at a time. The live reader skips while a YO job holds the GPU, and the driver runs one reader pass between the two seeds.
Data, from TRAIN-period records only (before 2026-10-02, as v2 to v4), answers computed by code. A same-date group is the set of qubits in one
record whose older T1/T2 date is identical. Only groups of 8 or more qubits are used.
 - 1,200 same-date items older than 24 h: 8 qubits from one group whose older date is more than 24 h before the stamp (every qubit stale).
   Up to two draws per group, duplicates dropped. If fewer than 1,200 exist, all are used and the builder prints the count.
 - 1,200 same-date items younger than 24 h (no qubit stale): 400 from groups 20 to 24 h old, 400 from 12 to 20 h, 400 under 12 h, one per group.
 - Replay, new draws with seeds that differ from v4: 1,200 Job A whole-window items (v4 builder), 1,200 Job A band items (v3 builder),
   1,200 Job A items drawn as v2 draws them, 2,400 Job C items drawn as v2 draws them, 600 per truth.
 VALID5 from the VALID records: 50 same-date older, 50 same-date younger, 100 Job A as v2 draws them, 200 Job C (50 per truth).
## TEST5 (new, never read)
From TEST-period records (2026-10-02 on). No v5 training item comes from this period. TEST4 is kept as it is.
 - same-date older than 24 h: one item per group, at most 2 per record, up to 300 drawn (the count is printed);
 - same-date younger than 24 h: one item per record, up to 150 from groups 18 to 24 h old and up to 150 from groups under 18 h (counts printed).
## FUTURE
Every IBM record the QIA mirror saves with a stamp later than this plan's commit time, up to the moment the driver scores FUTURE, one item each,
built as the live reader builds it (yo2_data.item_a, k = 0). YO v4, YO v5 and YO v5b are scored on the same items.
## Readings (all reported)
 R1 to R4 on TEST4, defined as in PLAN_YO_V4.md (yo4_compare.py R, unchanged): whole-window recall, Job A score on items drawn as v2 draws them,
    stale precision over all Job A items, Job C accuracy with forced-verdict rate and wrong CANNOT_TELL answers.
 R5a on TEST5: the share of stale qubits flagged inside the same-date items older than 24 h. Also shown by age band (24-28, 28-36, 36-48, 48 h
    and older), not part of the rule.
 R5b on TEST5: the share of not-stale qubits flagged inside the same-date items younger than 24 h (false flags).
 R5c on TEST5: the Job A score of all same-date items, reported, not part of the rule.
 R6 on FUTURE: exact items and mean Job A score for v4, v5 and v5b, with the count, reported, not part of the rule.
 Compared, paired over records (TEST4 records for R1 to R4, TEST5 records for R5), 2,000 resamples, seed 41, 95 %: each seed minus YO v4.
 Nulls on TEST5: flag nothing, flag every qubit, and the date rule of PLAN_YO_V3.
## Rule (four outcomes, margin 0.02 for "no worse")
 A seed passes if, against YO v4: R5a is ABOVE, R5b is not ABOVE, and R1, R2, R3 and R4 accuracy are not BELOW.
 YO v5 (seed 47) replaces YO v4 as the model at work only if both seeds pass. Then the live reader on QIA switches to adapters/v5.
 Otherwise YO v4 stays the model at work and both seeds are reported as tried. Every reading is published.
## KNOWN-GOOD
 The scorer on the code's own TEST5 answers gives 1.000. The nulls and YO v4 are scored on TEST5 with the same code and committed before the
 first v5 training step. The driver refuses to train if the known-good fails. Replies are read in full before any comparison is run.
