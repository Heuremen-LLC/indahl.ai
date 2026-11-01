# YO v4 -- plan (committed before any v4 item was built, any v4 null scored or any v4 output read; times from git). Wayfinder and Bones.
Why (readings_after_referee.text, defined after the data): on TEST3, in items where all 8 qubits were stale by 24 to 48 h (240 qubits in 30
records), YO v3 found 0.408, YO v2 0.367 and the date rule 0.367. The first live read on QIA (ibm_pittsburgh, record stamp 2026-10-31 23:17 UTC)
held 8 stale qubits by the code and YO v2 flagged none. v3's band items held 3 to 5 band qubits each, so a record whose qubits all went stale
together reached v3's training only through replay. Wayfinder, 31 Oct: "can we get some of Yo done on the mac?"
## Training
Continue from the YO v2 adapter (the model at work; adapters/v2/adapters.safetensors, sha256 starting f73c847be9f51dd5), same base (Qwen3-1.7B),
same prompt format and chat template, completions with mask_prompt, max_seq_length 2048, LoRA on 16 layers, batch 4, learning rate 5e-5,
1,200 iterations, seed 44, validation every 200 steps. One GPU job on the Mac. The live reader skips its run while a YO job holds the GPU.
Data, from TRAIN-period records only (as v3), answers computed by code, seeds differ from v2 and v3:
 - 2,400 Job A whole-window items: all 8 qubits drawn from qubits whose older T1/T2 date is 20 to 50 h before the stamp, from records that
   hold at least 8 such qubits (so some qubits are under 24 h and not stale, and most are stale);
 - 1,200 Job A band items built as v3 builds them (3 to 5 qubits in the 20 to 50 h window);
 - 1,200 Job A items drawn as v2 draws them (replay);
 - 2,400 Job C items drawn as v2 draws them, 600 per truth (replay).
## TEST4 (fresh, never read)
From TEST-period records that no v2 TEST item and no TEST3 item came from:
 - up to 200 Job A whole-window items, one per record, drawn as the training whole-window items (the count is printed by the builder);
 - 200 Job A items drawn as v2 draws them;
 - 400 Job C items, 100 per truth.
No TEST4 item is read before the readings below are computed.
## Readings (on TEST4, all of them reported)
 R1 whole-window recall: the share of qubits stale by 24 to 48 h (24 h < gap < 48 h, gap = the older of the T1 and T2 ages) inside the
    whole-window items that are flagged.
 R2 Job A score (v2 scorer) on the 200 items drawn as v2 draws them.
 R3 stale precision over all Job A items: the share of flagged qubits that are stale.
 R4 Job C accuracy and forced-verdict rate, and wrong CANNOT_TELL answers counted item by item.
 Compared, paired over TEST4 records (2,000 resamples, seed 41, 95 %): YO v4 minus YO v2 on R1, R2, R3 and R4 accuracy; YO v4 minus YO v3 on
 R1 and R2. Nulls also scored: flag nothing, the date rule, and flag every qubit (it finds every stale qubit by construction, and shows what
 R1 alone would reward).
## Rule (four outcomes, margin 0.02 for "no worse")
 YO v4 replaces YO v2 as the model at work if R1 is ABOVE v2's AND R2 is not BELOW AND R3 is not BELOW AND R4 accuracy is not BELOW. Then the
 live reader on QIA switches to the v4 adapter. Otherwise YO v2 stays the model at work and v4 is reported as tried. Every reading is published.
## KNOWN-GOOD
 The scorer on the code's own TEST4 answers gives 1.000 on both jobs. YO v2 and YO v3 are scored on TEST4 with the same code before the first
 v4 training step, and committed.
