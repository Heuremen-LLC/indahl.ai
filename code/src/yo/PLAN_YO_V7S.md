# YO v7, seed retest -- plan (committed before any new seed was trained; times from git). Wayfinder and Bones.
Why (defined after the data, from the YO v7 reading, yo7_results.text, commit bb65335): the two v7 seeds split. Seed 51 passed every reading
of the PLAN_YO_V7 rule (R6c +0.031 [+0.007, +0.059], above), seed 52 failed (R6c -0.118 [-0.186, -0.054] and R6b stale found -0.016, below).
Two seeds of one recipe cannot say which is the recipe. This plan retrains the same recipe with three new seeds before anything changes.
## Training (unchanged from PLAN_YO_V7)
Same data (data7, hashes in DATA_YO_V7.sha256), same base, adapter start (YO v4), settings and 1,200 iterations as yo7.yaml. Seeds 53, 54 and
55 (adapters/v7c, v7d, v7e), one after the other, one GPU job at a time, one live-reader pass between seeds.
## Test sets
TEST6 and TEST4 exactly as scored for YO v4, v6 and v7 (both have been read several times; every reading says so). FUTURE7 as built for v7.
## Readings and rule
As PLAN_YO_V7 (R6a, R6b, R6c on TEST6; R1 to R4 on TEST4; paired bootstrap over records, 2,000 resamples, seed 41, 95 %, margin 0.02), for
each new seed minus YO v4. RULE (strict, written before any new seed is trained): the v7 recipe replaces YO v4 only if ALL THREE new seeds
pass the PLAN_YO_V7 rule. Then YO v7 seed 51 (adapters/v7, named in PLAN_YO_V7 as the model that would go to work) goes to work; no seed is
chosen by its scores. Otherwise YO v4 stays. Also reported, not part of the rule: each reading's spread over all five v7 seeds (51 to 55).
## KNOWN-GOOD
KNOWN-GOOD: the scorer on the code's own TEST6 answers gives 1.000 (oracle), re-checked by the driver before training; the driver refuses to
train if it fails. Replies are read in full (structural check plus 10 per kind) before any comparison is run.
