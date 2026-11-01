# YO v3 -- plan (written 31 Oct 2026 ~19:45 EDT, before any v3 item was built, any v3 null scored or any v3 output read). Wayfinder and Bones.
Why (POSTHOC_YO_V2.md, after the referee): YO v2 finds half the stale qubits (recall 0.496, precision 0.927). It flags a stale qubit mostly
when its T1/T2 date is two or more calendar days before the record stamp, and misses most qubits stale by 24 to 48 h (24-25 h: 1 of 70).
A code rule written after the data (zeros, plus two or more calendar days) scores 0.929 against YO v2's 0.957. Wayfinder, 31 Oct: "refine
yo a bit in the weights".
## Training
Continue from the YO v2 adapter (adapters/v2/adapters.safetensors, sha256 starting f73c847be9f51dd5), same base (Qwen3-1.7B), same prompt
format and chat template as v2, completions with mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5, 1,200
iterations, seed 33, validation every 200 steps. One GPU job on the Mac.
Data, from TRAIN-period records only (stamps before 2026-09-18 22:41 UTC, the v2 TRAIN/VALID boundary; VALID as v2):
 - 2,400 Job A items whose 8 qubits are drawn so that at least 3 have a T1/T2 gap between 20 and 50 h where the record holds such qubits
   (the band both sides of the 24 h line: stale qubits one calendar day apart, and qubits under 24 h that are not stale);
 - 1,200 Job A items drawn as v2 draws them (replay);
 - 2,400 Job C items drawn as v2 draws them, 600 per truth (replay).
 Seeds differ from v2's. Answers computed by code, as v2.
## TEST3 (fresh, never read)
From TEST-period records (stamps on/after 2026-10-02 00:00 UTC) that no v2 TEST item came from: 400 Job A items drawn as v2 draws them,
400 Job C items (100 per truth). No TEST3 item is read before the readings below are computed.
## Readings (on TEST3, all of them reported)
 R1 Job A score (v2 scorer). R2 qubit-level stale recall and precision, and recall in the 24-48 h gap band. R3 Job C accuracy and
 forced-verdict rate.
 Compared, paired over TEST3 records (2,000 resamples, seed 31, 95 %): YO v3 minus YO v2 on R1, on R3, and on the 24-48 h band recall
 (resampling records); YO v3 minus the code rule (zeros + two calendar days) on R1. Nulls also scored: flag nothing.
## Rule (four outcomes, margin 0.02 for "no worse")
 v3 REFINES YO if its 24-48 h band recall is ABOVE v2's AND its Job A score is not BELOW v2's AND its Job C accuracy is not BELOW v2's.
 Otherwise YO v2 stays the working model and v3 is reported as tried. Whatever the outcome, every reading is published.
## KNOWN-GOOD
 The scorer on the code's own TEST3 answers gives 1.000 on both jobs; YO v2 is scored on TEST3 with the same code (its own repeat).

## Note added after the readings (changes no rule; times from git)
The header time above is wrong: git records this plan's commit d70fcbe at 19:00:54 EDT, before any v3 item was built (854dd2e 19:03:45, e5ba486 19:07:15).
Built as follows, where the text above differs (from the referee, read in full): the band items carry 3 to 5 qubits with a 20 to 50 h gap each; the last TRAIN record is 22:14:57 UTC and the first VALID record 22:36:10 UTC on 18 Sep; TEST3 Job C was drawn with up to 40 draws per record (v2 used 12), 400 items from 329 records; the 24-48 h band is 24 h < gap < 48 h with gap the older of the T1 and T2 ages, as in yo3_compare.py.
