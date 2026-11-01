# YO v7 -- plan (committed before any v7 item was built or any v7 output read; times from git). Wayfinder and Bones.
Why (defined after the data, from the YO v6 reading, yo6_results.text): both v6 seeds cut the false flags on young groups with a stale
neighbour (YO v4 0.048 of young qubits flagged, both seeds 0.001, below), but seed 49 lost whole-window recall on YO v4's test records
(0.931 against 0.975, below) and seed 50 missed more stale qubits beside young ones (0.977 against 0.995, below), so neither passed.
v6 trained on 1,200 whole-window items where YO v4 trained on 2,400, and on no band items where YO v4 had 1,200. v7 restores both and
changes nothing else. Wayfinder, 1 Nov: "Can we get some training going for the Mac lab please?"
## Training
Continue from the YO v4 adapter (adapters/v4/adapters.safetensors, sha256 starting 4737100d6e008afa), same base, prompt format, chat
template and settings as v4 to v6 (mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5, 1,200 iterations,
validation every 200 steps). Two seeds, one after the other: 51 (adapters/v7) and 52 (adapters/v7b). One GPU job at a time, one
live-reader pass between the seeds.
Data from TRAIN-period records only (before 2026-10-02), answers computed by code, new draw seeds for every kind:
 - the v6 kinds, same counts: 1,200 young previous-day items, 1,200 young-with-stale items (600 with one stale, 600 with two),
   1,200 same-date items older than 24 hours, 600 same-date items younger than 24 hours;
 - 2,400 whole-window items (v4's count, v6 had 1,200) and 1,200 band items (v4's builder and count, v6 had none);
 - replay: 1,200 Job A items drawn as v2 draws them and 2,400 Job C items.
## Test sets (unchanged, no new test set)
TEST6 (data6/test_items.jsonl, 890 items) and TEST4, exactly as scored for YO v4 and v6. The scores of YO v4, the nulls and v6 on them are
already committed (d66b5f7 and the v6 commits). v7's design used v6's TEST4 recall and TEST6 neighbour readings, so both sets have been read
before v7 is scored; every v7 reading on them says so. FUTURE7: every record the QIA mirror saves after this plan's commit, one live-format
item each, scored for YO v4, v7 and v7b.
## Readings, comparison and rule
 As PLAN_YO_V6.md, unchanged: R6a, R6b (false flags and stale found), R6c on TEST6; R1 to R4 on TEST4; R7 on FUTURE7; each seed minus
 YO v4, paired bootstrap over records, 2,000 resamples, seed 41, 95 %, margin 0.02. A seed passes if R6c is ABOVE, R6a is not ABOVE, R6b
 false flags are not ABOVE, R6b stale found is not BELOW, and R1 to R4 are not BELOW. YO v7 (seed 51) replaces YO v4 only if both seeds
 pass. Otherwise YO v4 stays the model at work and both seeds are reported as tried. Every reading is published.
## KNOWN-GOOD
 The scorer on the code's own TEST6 answers gives 1.000 (committed for v6). The driver re-runs the oracle and refuses to train if it fails.
 Replies are read in full before any comparison is run.
