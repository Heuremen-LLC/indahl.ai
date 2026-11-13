# REFEREE_YO_V7S -- outside referee, raw files only (read-only; independent code in /tmp/ref, python3 -I)

Decision under test: all three new seeds (v7c=53, v7d=54, v7e=55) pass the PLAN_YO_V7 rule, so seed 51 replaces YO v4.
VERDICT: the decision stands under the plan's rule as written. One flag (item 4: R3 interval touches zero for v7d and v7e). 

## 1. Copied comparison changed only model lists and the rule line -- HOLDS
diff yo7_compare.py yo7s_compare.py: (a) docstring line; (b) S4/S6 model lists and the TEST4/TEST6 print loops extended with yo_v7c/d/e;
(c) FUTURE7 loop extended; (d) the bootstrap loop now runs ('yo_v7c','yo_v7d','yo_v7e','yo_v7','yo_v7b') instead of ('yo_v7','yo_v7b');
(e) the final rule line is now all(passes[x] for x in v7c, v7d, v7e), v7/v7b only as spread. The per-seed pass expression, R definitions, boot()
(2,000 resamples, bs[49], bs[1949]), margin 0.02 and C4.outcome are untouched; rng = Random(41) is reset per model, so the order change does not
alter any interval. yo4_compare.py is unchanged since 31 Oct 20:06 (before the plan). v7 and v7b rows in yo7s_results.text equal the earlier yo7_results
(R6c +0.031 [+0.007,+0.059] for v7; -0.118 [-0.186,-0.054] for v7b). Training configs: yo7c/d/e.yaml differ from yo7.yaml only in adapter_path and
seed (53/54/55); same data7, resume adapter, 1,200 iters, lr 5e-5.

## 2. Recompute -- HOLDS (R6 all four readings, R1-R4 all, from reply files + test items)
Own code, own parsing (same item sets: TEST6 yprev 300 / ystale 300 / sdold 290 items; denominators 2400, 1974, 426, 2320). Point values:
| model | R6c | R6b_false | R6b_found | R6a |
| yo_v4 | 0.9694 | 0.0476 | 0.9953 | 0.0000 |
| v7c | 1.0000 | 0.0157 | 1.0000 | 0.0000 |
| v7d | 0.9966 | 0.0441 | 0.9977 | 0.0000 |
| v7e | 0.9931 | 0.0056 | 0.9953 | 0.0033 |
All equal yo7s_results.text. TEST4 (own R1-R4): v4 0.9752/0.9903/0.9991/0.9750; v7c 0.9914/0.9985/0.9923/0.9600; v7d 0.9925/0.9843/0.9922/0.9650;
v7e 1.0000/0.9944/0.9924/0.9750, equal to the file. My bootstraps (seeds 41, 1, 2, and 3 for TEST4) give the same outcome words as the file for every
reading of every seed; R6c intervals: v7c [+0.0068,+0.0581], v7d [+0.0058,+0.0544], v7e [+0.0030,+0.0491] (seed 41), stable across seeds.

## 3. Rule as applied vs plan text -- HOLDS
PLAN_YO_V7: pass = R6c ABOVE, R6a not ABOVE, R6b false not ABOVE, R6b found not BELOW, R1-R4 not BELOW; seed 95%, 2,000 resamples, seed 41, margin 0.02,
four outcomes (ABOVE/BELOW/CONSISTENT/CANNOT_TELL via lo>0, hi<0, inside +-0.02). The code's passes[] expression is exactly that, nothing added or dropped.
PLAN_YO_V7S: all three new seeds pass, then seed 51 (adapters/v7) goes to work, no seed chosen by score: the final rule line does that. Hand check of each
seed against the rule: v7c R6c ABOVE, R6a CONSISTENT, R6b_false BELOW, found CONSISTENT, R1-R4 ABOVE/CANNOT_TELL (R2 ABOVE) none BELOW: pass.
v7d: R6c ABOVE, R6b_false CANNOT_TELL (not ABOVE), found CONSISTENT, R1-R4 none BELOW: pass. v7e: R6c ABOVE, R6a CONSISTENT, R6b_false BELOW, none BELOW: pass.
(Note: a TEST6 and TEST4 that the plan says were read before; the plan states it. Note v7d R6b_false: -0.004 [-0.034,+0.025] gives no false-flag gain over v4.)

## 4. Closest bound to failing -- HOLDS, but THREE PASSES REST ON R3 UPPER BOUNDS AT ZERO (flag)
"Not BELOW" fails if the upper bound is under 0. R3 (stale precision) point estimate is below v4 for all three (v4 1127/1128 flagged correct; v7c 1164/1173,
v7d 1143/1152, v7e 1172/1181):
- v7c: R3 -0.0068 [-0.0227, +0.0019] -> closest bound +0.0019 (own 20 other seeds: +0.0017 to +0.0019). Also R6c lower +0.0068.
- v7d: R3 -0.0069 [-0.0224, +0.00005] -> upper bound +0.00005 (20 other seeds: +0.00005 to +0.00006). Printed "+0.000". R6c lower +0.0058.
- v7e: R3 -0.0067 [-0.0234, +0.00011] -> upper bound +0.00011 (20 other seeds: +0.00009 to +0.00011). Printed "+0.000". R6c lower +0.0030 (closest to losing ABOVE).
No alternative seed gave an upper bound below 0, so the result is not an artefact of seed 41, but v7d and v7e pass R3 only because ~2.5% of resamples omit
every record with a wrong flag; the bound is the discrete floor, not a margin. Under a stricter reading ("a point estimate below v4 on all of R3 in three
of three seeds") they would not be clean, but the plan's rule is the four-outcome one and it passes. R1 v7e lower bound +0.0000 is irrelevant (only BELOW matters).
Other near misses: v7c R4 -0.0150 [-0.036,+0.005], v7d R2 -0.006; both far from hi<0.

## 5. Plan items done? -- HOLDS, with two notes
- Plan committed before training: dd19fa5 13:35:39 (with yo7s_drive.sh and yaml); first replies b5b4aa5 14:22. OK.
- KNOWN-GOOD: yo7s_knowngood.out "test6 oracle job A n 890 mean 1.000 | unparsed 0", committed 1fd302f 13:35:40, driver greps it and refuses to train otherwise. Done once before the first seed (plan says "before training"; not repeated between seeds). It is yo6_eval.py's scorer, not the yo7s_compare scorer; the compare's own 'all'/'nothing' rows (1.0/0.0) give a weak sanity check. 
- Replies read before the comparison: yo7s_replies.py d44e066 (16:16:43), fix 6b77a62 (16:17:02, "fixed before any score was read"), yo7s_replies.text mtime 16:17:03, yo7s_compare.py committed d2c7afc 16:17:31, yo7s_results.text file time 16:56:03 (not yet in git; untracked). Order OK. But the reply tool is structural, prints 10 per kind (A5, A6, TEST4 job) and was committed and run within 1 minute of the fix; reading depth is what the plan asked ("structural check plus 10 per kind"), not more.
- Replies, scores and adapters committed unread (b5b4aa5, e866f69, 9bda9f3, 29655c1); hashes in ADAPTERS_YO_V7S.sha256 (3 lines). I did not recompute adapter hashes (adapters not touched).
- Reply read found: v7d 1 TEST4 job-A reply is a runaway repetition (id A|ibm_pittsburgh|2026-10-13T19:46:15+00:00|60, 300 chars, unterminated zero list). The stale list inside it equals the truth and v4's answer, but the scorer gave it 0 and the comparison counts it as no flags. Effect: lowers v7d R2 slightly (CANNOT_TELL anyway); counting its flags would raise R3 by about 0.00005. No effect on any outcome. 
- Off-record flagged numbers: v7d 2 (TEST6 sdold), v7e 2; the TEST6 reader intersects with shown qubits so none affects R6. Reported in yo7s_replies.text. 
- FUTURE7 (8 items): v7c 8/8, v7d 8/8, v7e 7/8 exact, v4 8/8; reported only.

## Summary
Items 1,2,3,5 hold. Item 4: all three pass, but v7d and v7e R3 upper bounds are +0.00005 and +0.0001 (the line), and R3 point estimates are below YO v4 in all three seeds
(about -0.007). Switch decision stands under the plan's rule; the claim to make is "not worse on R3 beyond what 790 records can show", not "equal".
