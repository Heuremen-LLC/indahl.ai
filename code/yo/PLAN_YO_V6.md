# YO v6 -- plan (committed before any v6 item was built, any v6 null scored or any v6 output read; times from git). Wayfinder and Bones.
Why (defined after the data, from the YO v5 reading, yo5_counts2.text): YO v5 found more of the stale qubits in same-date items but was not
adopted, because seed 47 flagged 25 qubits that were not stale and seed 48 lost verdicts. On YO v4's test items every qubit flagged in error,
by every YO model so far (YO v4's three seeds and both v5 seeds), sat in an item where 7 or 8 of the 8 qubits share one date younger than a day.
Read item by item they are of two kinds: (a) a young group whose date falls on the previous calendar day (6.6 to 23.7 hours old), flagged
whole, and (b) a young group with one stale qubit beside it, flagged whole. TEST5's younger items never held a stale neighbour.
Wayfinder, 1 Nov: "Can we get some training going for the Mac lab please?"
## Training
Continue from the YO v4 adapter (the model at work; adapters/v4/adapters.safetensors, sha256 starting 4737100d6e008afa), same base, prompt
format, chat template and settings as v4 and v5 (mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5, 1,200
iterations, validation every 200 steps). Two seeds, one after the other: 49 (adapters/v6) and 50 (adapters/v6b). One GPU job at a time, one
live-reader pass between the seeds.
Data from TRAIN-period records only (before 2026-10-02), answers computed by code. A group is the set of qubits in one record whose older T1/T2
date is identical. Only groups of 8 or more are used.
 - 1,200 young previous-day items: 8 qubits from one group whose older date is under 24 hours before the stamp and on an earlier UTC
   calendar day than the stamp (no qubit stale);
 - 1,200 young-with-stale items: 7 qubits (600 items) or 6 qubits (600 items) from one group under 24 hours old, plus 1 or 2 qubits from the
   same record whose older date is more than 24 hours old (only those stale);
 - 1,200 same-date items older than 24 hours (yo5_data.py's builder, new draws), the kind YO v5 learned;
 - replay: 600 same-date items younger than 24 hours, 1,200 whole-window items, 1,200 Job A items drawn as v2 draws them, 2,400 Job C items.
 If a kind has fewer items than asked, all are used and the builder prints the count.
## TEST6 (new, never read)
From TEST-period records (2026-10-02 on), new draws with seeds no earlier set used; no v6 training item comes from this period:
 - up to 300 young previous-day items, one per record;
 - up to 300 young-with-stale items, one per record;
 - up to 300 same-date items older than 24 hours, at most one per group, at most 2 per record.
TEST4 is kept as it is. FUTURE6: every record the QIA mirror saves with a stamp after this plan's commit time, one live-format item each.
## Readings (all reported)
 R6a on TEST6: the share of qubits flagged in the young previous-day items (none is stale).
 R6b on TEST6, young-with-stale items: the share of the young qubits flagged (false flags) and the share of the stale qubits found.
 R6c on TEST6: the share of stale qubits found in the same-date items older than 24 hours.
 R1 to R4 on TEST4, defined as in PLAN_YO_V4.md (yo4_compare.py R, unchanged).
 R7 on FUTURE6: exact items for YO v4, v6 and v6b, with the count, reported, not part of the rule.
 Each seed minus YO v4, paired bootstrap over records (TEST6 records for R6, TEST4 records for R1 to R4), 2,000 resamples, seed 41, 95 %.
 Nulls on TEST6: flag nothing, flag every qubit, and the date rule of PLAN_YO_V3 (it flags a whole previous-day group by construction).
## Rule (four outcomes, margin 0.02 for "no worse")
 A seed passes if, against YO v4: R6c is ABOVE, R6a is not ABOVE, the false-flag share of R6b is not ABOVE, the stale share of R6b is not
 BELOW, and R1, R2, R3 and R4 accuracy are not BELOW. YO v6 (seed 49) replaces YO v4 as the model at work only if both seeds pass. Then the
 live reader switches to adapters/v6. Otherwise YO v4 stays the model at work and both seeds are reported as tried. Every reading is published.
## KNOWN-GOOD
 The scorer on the code's own TEST6 answers gives 1.000. The nulls and YO v4 are scored on TEST6 with the same code and committed before the
 first v6 training step. The driver refuses to train if the known-good fails. Replies are read in full before any comparison is run.
