# Round 2 report v2 (Sage 20:14Z edits; v1 is hashed in SHA256SUMS_X2 and kept) (seed replication of round 1). Sage's ruling 7 Nov ~19:59Z: T1 verdict stands as computed; wording moved per her five edits.
Read is SELF-WITNESSED until SHA256SUMS_R2READ is in a Bitcoin block (read_round2.py was written after the rows existed, before its numbers were seen).

**Result.** The rule reads seed-dependent because one of four runs failed to train (NaN, twice), and the three that trained all cleared.
s64's failure is a training fault, not a seed effect: s63 hit the same fault, was retrained once under A19 W2 and trained clean; s64 failed both times.

**Headline, P1 OK flips (sample 0, base vs trained, 100 P1 questions each):** s61 up 44 / down 4 (p 1.5e-9); s62 up 41 / down 5 (p 4.4e-8);
s63 up 38 / down 7 (p 3.1e-6); s64 FAILED, no rows.

**T1 (A16 as pinned by A17-A19).** Scored-only ruler: gaps +0.150, +0.095, +0.078 against base rerun floors 0.008, 0.008, 0.004; all three clear (a);
(b) min gap 0.0782 vs largest seed-pair difference 0.0734 (s61 vs s63), holds by +0.0048. That margin is thin and nothing leans on it.
Sensitivity, labelled: with MISS dropped instead of counted as a fault, the margin is +0.0433. The pinned ruler stays the headline.
Independently recomputed from the raw rows by Sage's DIG: every T1 number matches.
All-items ruler: gaps +0.201, +0.153, +0.147, floors 0.012, 0.012, 0.015; (b) 0.147 vs 0.053, holds by +0.094, the sturdier margin.
The three gaps differ, from 0.150 to 0.078. The claim stays round 1's narrowed claim; no seed result widens it.

**P4M.** Base answers is_max right on 90 of 90 rows, so by U4 the is_max arm cannot read the always-max habit. The trained arms do lose is_max:
OK drops from 90 (base) to 27 (s61), 30 (s62), 38 (s63) of 90. Most of the rest are confident numeric replies the scorer can't bin (UNREAD
52, 52, 47): unclassified. The habit check reads CAN'T TELL for s61, s62 and s63 (UNREAD over 50% on a kind). Original r15 P4: base 88, s61 89,
s62 88, s63 90 OK of 90. Counts per kind are in round2_READ.txt.

**Defined after the data.** P3 fault rate rises on all three seeds (sample 0: base 0.385/0.385/0.412, trained 0.458/0.551/0.626).

**Checks.** P2 UNREAD (trained): 88, 78, 59 of 180. s62's base rerun is byte-identical to round 1's (eval_round1.py re-runs base with seeded sampling; it is a rerun, not a copy: eval_s62.log holds the base progress lines, and the log and rows file carry mtime 18:25:22Z against round 1's 06:23:23Z); s63's base sample 0 differs (129/139/72 vs
126/138/76; samples 1-2 match). s63's eval ran beside the flock's Mac seats on the same GPU (disclosed in POST_READ_CHANGES.md); no cause named.
A secondary read of the unclassified replies is stamped separately (SECONDARY_R2.txt) and is reported beside T4, never inside it.
