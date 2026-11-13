# YO v8 -- plan (committed before any v8 item was built, any v8 seed trained or any v8 output read; times from git). Wayfinder and Bones.
Wayfinder, 1 Nov: "can we get some training going? V8?"
Why (defined after the data, from YO v7's replies on TEST4, eval4_yo_v7.jsonl): of 400 four-outcome verdict items, YO v7 seed 51 missed 11
(YO v4 missed 10). Every miss is at a border of the rule: 6 CONSISTENT answered CANNOT_TELL, 4 CANNOT_TELL answered CONSISTENT, 1
CANNOT_TELL answered BELOW. The verdict items are drawn with random centres and widths, so few of them sit near a border. v8 trains on
the borders and is scored on a new border set that no one has read.
## Training
Continue from YO v7 seed 51 (adapters/v7/adapters.safetensors, sha256 starting 36fb23d31d6a754a), same base (Qwen/Qwen3-1.7B), prompt
format, chat template and settings as v7 (mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5, 1,200
iterations, validation every 200 steps). Three seeds, one after the other: 56 (adapters/v8), 57 (adapters/v8b), 58 (adapters/v8c). One GPU
job at a time, one live-reader pass between seeds.
Data (data8), from TRAIN-period records only (before 2026-10-02), answers computed by code (yo2_data.truth on the rounded printed values):
 - every data7 training item, unchanged (hash in DATA_YO_V7.sha256);
 - 2,400 border verdict items (yo8_data.item_border), 600 of each kind: an interval end within a quarter of the margin of reference plus
   the margin or reference minus the margin, inside ("margin-in") or outside ("margin-out"); an interval end within a quarter of the margin
   of the reference itself, past it ("ref-past", ABOVE or BELOW) or short of it ("ref-short"). The truth is whatever the rule gives on the
   printed numbers; the kind only sets where the draw lands. Items with a reference under 5 microseconds are not drawn.
VALID8: data7 VALID plus 100 border items from VALID records.
## Test sets
TEST8C (new, data8/test8c_items.jsonl): 800 border items from TEST-period records (on or after 2026-10-02), 200 of each kind, built once by
yo8_data.py with draw seed 881, not read before the comparison. TEST6 and TEST4 exactly as scored for YO v4 to v7 (both read before; every
reading on them says so).
## Readings, comparison and rule
R8 on TEST8C: share of verdicts exact. R6a, R6b, R6c on TEST6 and R1 to R4 on TEST4, as PLAN_YO_V7. Each seed minus YO v7 seed 51 (the
model at work), paired bootstrap over records, 2,000 resamples, seed 41, 95 %, margin 0.02, four outcomes.
A seed passes if R8 is ABOVE, R6a is not ABOVE, R6b false flags are not ABOVE, R6b stale found is not BELOW, R6c is not BELOW, and R1 to R4
are not BELOW. RULE (written before any seed is trained): YO v8 seed 56 replaces YO v7 only if ALL THREE seeds pass. Otherwise YO v7 stays
the model at work and every seed is reported as tried. No seed is chosen by its scores. Every reading is published.
Also reported, not part of the rule: R8 for YO v4 and the nulls (always CONSISTENT; the binary rule that never says CANNOT_TELL), R8 by kind.
## KNOWN-GOOD
KNOWN-GOOD: the scorer on the code's own answers gives 1.000 on TEST6 (oracle, as for v6 and v7) and must give 1.000 on TEST8C; the driver
re-runs both and refuses to train if either fails. A synthetic check in yo8_data.py asserts, before writing, that every border item's truth
equals the rule recomputed from the printed prompt text. Replies are read in full (structural check plus 10 per kind) before any comparison.
