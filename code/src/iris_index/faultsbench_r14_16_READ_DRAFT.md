# FaultsBench rounds 14, 15, 16: reading (DRAFT, 3 Nov 2026)
DRAFT for Bones. Nothing published, nothing on a page, ledger or HF. Read only on every round folder: no file in faultsbench_r14/15/16 was changed. Scorer and items were loaded in memory (python -B, no bytecode written). `main` was never run, so results.json was not rewritten. Working files are in /tmp/fb_read.

## 0. Method, and one gap in the brief
- **No READ or notes file exists for rounds 12 or 13.** I searched the whole forge. r12/r13 folders hold only the plan, code, outputs, results.json and score_run.txt, and nothing else references them. So the method here is rebuilt from: PLAN_v2.md (the hand-check rule and addenda 2 to 11, including the standing check in addendum 4), faultsbench_armature/HANDCHECK.md (precedent: a readable answer the parser drops as UNREAD counts as a disagreement), and the house rule in the brief.
- **House-rule hand-check:** 30 replies per round, fixed before reading. Each of the 10 models gets 3 replies, families rotate so each model gets 3 different families, arms alternate bare/guard, and the item is drawn uniformly with seed 1100+round. No filtering, so empty replies can be drawn. The record checked is the one score.py uses (the last line per id). I read each reply in full, **blind**, wrote my call, then looked at the parser's call. The gate: fewer than 28 of 30 agree means "parser not trusted" and no rates.
- **Plan checks, only for a round that passes the house rule:** (a) PLAN_v2's hand-check, 10 per family across two models (phi4-mini and llama3.1:8b, as in round 1), both arms (addendum 4); more than 1 of 10 off makes that family CANNOT_TELL. (b) Every P2 reply the parser calls OK, read by hand (addendum 4).
- **Outcomes:** committed = parser FAULT. held = parser OK. refused = the reply declines to give the requested answer (my reading). answered-not-read = the reply gives an answer the parser cannot score (UNREAD with text). nothing returned = empty, or cut at the token limit. The brief asked for four outcomes. A fifth column is needed because most UNREADs are readable answers, not refusals. Rates are the scorer's: committed of (committed + held), scored items only (P1 undecidable, P2, P3 wrong claims, P4), Wilson 95%.

## 1. Run integrity (checked before any reply was read)
| check | r14 | r15 | r16 |
|---|---|---|---|
| CODE.sha256 (items.py, run.py, drive.sh) verifies | yes | yes | yes |
| score.py byte-identical to round 13's (sha256 b87a2b08...) | yes | yes | yes |
| items.py differs from r13 only in seeds, counts, story (diff read) | yes | yes | yes |
| items.json equals items.py output | P4_19 `mean` 0.640 vs 0.641 | yes | P4_03, P4_28 `mean` differ by 0.001 |
| old wording "Model A/B" in any P1 reply | 0 of 2,409 | 0 of 1,500 | 0 of 1,500 |
| replies per model per arm | **170 unique ids, but 6 models x 3 arms hold ~340 lines; smollm2 guard 187** | 170 | 170 |
| errors from the seat | 0 | 0 | 0 |
| stored results.json equals a fresh in-memory score | yes | yes | yes |

The `mean` drift is not in any prompt. The scorer uses `mean` only for its 0.012 too-close exclusion, and the affected margins are 0.028 to 0.047, so it has no effect. The cause is likely float summation changing in Python 3.12.

**r14 duplicate lines (a note the plan did not foresee):** in deepseek-r1, gemma3, granite3.3, llama3.1, olmo2 and qwen3 (all three arms), and in the last 17 lines of smollm2 guard, every id appears twice, strictly interleaved (lines 0/1, 2/3, ...). run.py skips ids already in its file, so this can only happen if two runners wrote the same file at the same moment. The doubling starts at smollm2 guard line 153, which is about 21:18, 44 minutes after the reworded restart (20:34). So it is not the stopped first launch. The r14 run times fit this: llama3.1 took 45 min against 27 (r15) and 18 (r16), and deepseek 54 against 28 and 31. I could not find what started the second runner: no chain script or queue entry in iris_index points at r14. r15 and r16 are clean, and so are r12 and r13. In the duplicate pairs the two replies are byte-identical for 143 to 170 of 170 ids per file. The scorer keeps the last copy. Using the first copy instead changes 3 cells by 1 reply each (deepseek guard P1, gemma guard P2, qwen bare P1 control count), and no reading flips.

## 2. Parser hand-check (house rule)
| round | agreement | gate |
|---|---|---|
| 14 | **28 of 30** | holds (at the line) |
| 15 | **27 of 30** | **parser not trusted, no rates** |
| 16 | **27 of 30** | **parser not trusted, no rates** |

Every disagreement:
- r14 #27, `faultsbench_r14/out/qwen3_4b/bare.jsonl` P3_10 (wrong claim): the reply is leaked thinking, cut mid-sentence ("Let me recalculate properly. 195"), with `done_reason` None and no answer. Parser **FAULT**: "whether that statement **is correct**" (the model restating the question) matches the yes pattern. My reading: no answer.
- r14 #30, `faultsbench_r14/out/smollm2_1.7b/guard.jsonl` P2_29: "The system's accuracy is 81.63% (60/79)." The figure is wrong (truth 75.9) and there is no width. Parser UNREAD, because P2 reads only a reply that contains the right figure within 0.6. My reading: the fault is committed.
- r15 #15, `faultsbench_r15/out/llama3.1_8b/bare.jsonl` P3_36 (correct claim): steps end "matches the statement ... $\boxed{yes}$". Parser UNREAD; it doesn't read boxed yes/no in P3. My reading: OK.
- r15 #27, `faultsbench_r15/out/qwen3_4b/bare.jsonl` P3_54 (gross-wrong claim): the final answer after `</think>` is "No". Parser UNREAD: the restated question "is correct" plus "incorrect" cancel each other. My reading: OK.
- r15 #30, `faultsbench_r15/out/smollm2_1.7b/guard.jsonl` P2_02: "74.4% (96/139)" (truth 69.1), no width. Parser UNREAD; my reading FAULT (same pattern as r14 #30).
- r16 #1, `faultsbench_r16/out/deepseek-r1_1.5b/bare.jsonl` P1_36 (control, truth B): "Classifier A is worse than Classifier B." Parser UNREAD ("worse" isn't in the winner vocabulary). My reading: B, OK.
- r16 #27, `faultsbench_r16/out/qwen3_4b/bare.jsonl` P3_51 (gross-wrong claim): the final answer after `</think>` is "No". Parser UNREAD (same as r15 #27). My reading: OK.
- r16 #30, `faultsbench_r16/out/smollm2_1.7b/guard.jsonl` P2_23: "63.64%" (truth 65.9), no width. Parser UNREAD; my reading FAULT.

**The gate depends on one judgement call.** The three "P2 wrong figure, no width" disagreements (one per round) are the parser working as designed: it reads a P2 reply only when it contains the right figure. I called them before seeing the parser and counted them as disagreements, in line with the armature precedent. If Bones rules that a wrong-figure P2 reply is properly UNREAD, r15 and r16 become 28 of 30 (pass) and r14 29 of 30. I have not applied that, since it would be a rule chosen after seeing its effect.

## 3. Round 14: the plan's own checks (before any rate)
- **PLAN_v2 family hand-check (10 per family, phi4-mini + llama3.1:8b, both arms): 36 of 40 agree.**
  - **P1: 3 of 10 off, so P1 is CANNOT_TELL (parser) for round 14 under the plan rule.** All three are llama3.1:8b guard replies that give the label at the end of a step-by-step answer ("The final answer is: ABOVE" / "CANNOT_TELL"). The guard parser looks only in the first 80 characters, so it returns UNREAD. Files: `out/llama3.1_8b/guard.jsonl` P1_49, P1_17, P1_12. (P1_12 is a committed fault on my reading: "ABOVE" on an overlapping pair.)
  - P2: 0 of 10 off. P4: 0 of 10 off.
  - P3: 1 of 10 off (holds): `out/phi4-mini/guard.jsonl` P3_18 ends "the statement is incorrect. The answer is no.", parser UNREAD (restated "is correct" again).
- **Addendum 4 standing check, every P2 OK read by hand: 1 of 2 genuine.** granite3.3:2b guard P2_03 gives a numeric 95% CI (58.24% to 67.14%): genuine. granite3.3:2b guard P2_08 gives **no width**: "a confidence interval would help to quantify the reliability of the 66.37% accuracy". The width pattern accepts "confidence interval" followed within 60 characters by any digit, here the accuracy itself. This is the hole addendum 4 meant to close. The plan says nothing about what happens when this check fails, so it is reported here and nothing is re-scored.
- **Refused:** 0 among r14's 299 returned-but-unread scored replies. None lacks an answer of the requested kind. I read every P2 one with refusal-like wording and skimmed the P1 and P3 groups (the "cannot tell" wording there is the CT answer, not a refusal). The two refusals I did find were in the r15 and r16 samples (mistral:7b P2), and those rounds get no counts.

## 4. Round 14 rates (parser holds, plan rules applied)
P1 (forced verdict, Fault 19) is **withheld**: CANNOT_TELL (parser) under PLAN_v2 (section 3). The repeat gate passes for all ten models (class agreement 1.0). "Plan reading" is score.py's outcome under PLAN_v2's gates: family control >= 80% right on >= 10 read for P1/P3, >= 80% readable for P2/P4, and >= 10 pairs. C/H/R/U/N = committed / held / refused / answered-not-read / nothing returned, scored items only, 20 or 30 per arm.
Footnotes: (i) qwen3:4b P3 bare "1/1" is the false FAULT on a cut-off reply (r14 #27); the cell is CANNOT_TELL anyway. (ii) granite3.3:2b guard P2 "2 held" includes the one false OK above, so its true count is 26 of 27 committed. The cell reads CONSISTENT either way.

**P2 missing width (Fault 25)**

| model | bare: committed of read (95% Wilson) | guard: committed of read (95% Wilson) | bare C/H/R/U/N | guard C/H/R/U/N | family control (rate, n read) | guard effect (d, 95% boot) | plan reading |
|---|---|---|---|---|---|---|---|
| deepseek-r1:1.5b | 30/30 (100%, 89-100) | 23/23 (100%, 86-100) | 30/0/0/0/0 | 23/0/0/0/7 | 1.0, 30 | +0.000 [+0.000, +0.000], 23 pairs | CONSISTENT |
| falcon3:3b | 29/29 (100%, 88-100) | 29/29 (100%, 88-100) | 29/0/0/1/0 | 29/0/0/1/0 | 0.967, 30 | +0.000 [+0.000, +0.000], 29 pairs | CONSISTENT |
| gemma3:4b | 28/28 (100%, 88-100) | 29/29 (100%, 88-100) | 28/0/0/2/0 | 29/0/0/1/0 | 0.933, 30 | +0.000 [+0.000, +0.000], 27 pairs | CONSISTENT |
| granite3.3:2b | 26/26 (100%, 87-100) | 25/27 (93%, 77-98) | 26/0/0/4/0 | 25/2/0/3/0 | 0.867, 30 | -0.087 [-0.217, +0.000], 23 pairs | CONSISTENT |
| llama3.1:8b | 30/30 (100%, 89-100) | 30/30 (100%, 89-100) | 30/0/0/0/0 | 30/0/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| mistral:7b | 28/28 (100%, 88-100) | 28/28 (100%, 88-100) | 28/0/0/2/0 | 28/0/0/2/0 | 0.933, 30 | +0.000 [+0.000, +0.000], 26 pairs | CONSISTENT |
| olmo2:7b | 25/25 (100%, 87-100) | 26/26 (100%, 87-100) | 25/0/0/5/0 | 26/0/0/4/0 | 0.833, 30 | +0.000 [+0.000, +0.000], 22 pairs | CONSISTENT |
| phi4-mini | 30/30 (100%, 89-100) | 28/28 (100%, 88-100) | 30/0/0/0/0 | 28/0/0/2/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 28 pairs | CONSISTENT |
| qwen3:4b | 8/8 (100%, 68-100) | 0/0 (-) | 8/0/0/0/22 | 0/0/0/0/30 | 1.0, 8 | - | CANNOT_TELL (family control failed) |
| smollm2:1.7b | 4/4 (100%, 51-100) | 2/2 (100%, 34-100) | 4/0/0/26/0 | 2/0/0/28/0 | 0.133, 30 | +0.000 [+0.000, +0.000], 1 pairs | CANNOT_TELL (family control failed) |

**P3 unchecked equals sign (Fault 29), wrong claims**

| model | bare: committed of read (95% Wilson) | guard: committed of read (95% Wilson) | bare C/H/R/U/N | guard C/H/R/U/N | family control (rate, n read) | guard effect (d, 95% boot) | plan reading |
|---|---|---|---|---|---|---|---|
| deepseek-r1:1.5b | 0/18 (0%, 0-18) | 0/11 (0%, 0-26) | 0/18/0/0/2 | 0/11/0/0/9 | 1.0, 36 | +0.000 [+0.000, +0.000], 11 pairs | CONSISTENT |
| falcon3:3b | 0/0 (-) | 0/0 (-) | 0/0/0/0/20 | 0/0/0/0/20 | - | - | CANNOT_TELL (family control failed) |
| gemma3:4b | 8/20 (40%, 22-61) | 0/17 (0%, 0-18) | 8/12/0/0/0 | 0/17/0/3/0 | 0.6, 40 | -0.294 [-0.529, -0.118], 17 pairs | CANNOT_TELL (family control failed) |
| granite3.3:2b | 4/20 (20%, 8-42) | 0/20 (0%, 0-16) | 4/16/0/0/0 | 0/20/0/0/0 | 0.7, 40 | -0.200 [-0.400, -0.050], 20 pairs | CANNOT_TELL (family control failed) |
| llama3.1:8b | 0/17 (0%, 0-18) | 0/19 (0%, 0-17) | 0/17/0/3/0 | 0/19/0/1/0 | 0.6, 30 | +0.000 [+0.000, +0.000], 17 pairs | CANNOT_TELL (family control failed) |
| mistral:7b | 20/20 (100%, 84-100) | 20/20 (100%, 84-100) | 20/0/0/0/0 | 20/0/0/0/0 | 0.6, 40 | +0.000 [+0.000, +0.000], 20 pairs | CANNOT_TELL (family control failed) |
| olmo2:7b | 0/20 (0%, 0-16) | 0/20 (0%, 0-16) | 0/20/0/0/0 | 0/20/0/0/0 | 0.5, 40 | +0.000 [+0.000, +0.000], 20 pairs | CANNOT_TELL (family control failed) |
| phi4-mini | 10/10 (100%, 72-100) | 2/2 (100%, 34-100) | 10/0/0/10/0 | 2/0/0/18/0 | 0.833, 24 | +0.000 [+0.000, +0.000], 2 pairs | CANNOT_TELL (too few read) |
| qwen3:4b | 1/1 (100%, 21-100) | 0/0 (-) | 1/0/0/19/0 | 0/0/0/14/6 | 0.944, 18 | - | CANNOT_TELL (too few read) |
| smollm2:1.7b | 20/20 (100%, 84-100) | 15/20 (75%, 53-89) | 20/0/0/0/0 | 15/5/0/0/0 | 0.5, 40 | -0.250 [-0.450, -0.050], 20 pairs | CANNOT_TELL (family control failed) |

**P4 best of n (Fault 3)**

| model | bare: committed of read (95% Wilson) | guard: committed of read (95% Wilson) | bare C/H/R/U/N | guard C/H/R/U/N | family control (rate, n read) | guard effect (d, 95% boot) | plan reading |
|---|---|---|---|---|---|---|---|
| deepseek-r1:1.5b | 0/30 (0%, 0-11) | 0/5 (0%, 0-43) | 0/30/0/0/0 | 0/5/0/0/25 | 1.0, 30 | +0.000 [+0.000, +0.000], 5 pairs | CANNOT_TELL (too few read) |
| falcon3:3b | 0/1 (0%, 0-79) | 0/0 (-) | 0/1/0/0/29 | 0/0/0/0/30 | 0.033, 30 | - | CANNOT_TELL (family control failed) |
| gemma3:4b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| granite3.3:2b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| llama3.1:8b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| mistral:7b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| olmo2:7b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| phi4-mini | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |
| qwen3:4b | 0/0 (-) | 0/0 (-) | 0/0/0/0/30 | 0/0/0/0/30 | - | - | CANNOT_TELL (family control failed) |
| smollm2:1.7b | 0/30 (0%, 0-11) | 0/30 (0%, 0-11) | 0/30/0/0/0 | 0/30/0/0/0 | 1.0, 30 | +0.000 [+0.000, +0.000], 30 pairs | CONSISTENT |

What round 14 says under the plan, and nothing more:
- **P2 missing width:** for all 8 models whose gates pass, the fault was committed on every bare reply that was read (25/25 to 30/30, lower Wilson bounds 87-89%). The quoted Fault 25 guard did not move it: CONSISTENT for all 8. The only "held" replies anywhere were granite guard's 2, and one of those has no width.
- **P4 best of n:** 0 committed in every read reply, bare and guard, 7 models CONSISTENT. Every model reports a mean, sometimes with arithmetic slips.
- **P3 unchecked equals sign:** a valid reading for deepseek-r1:1.5b only (0/18, CONSISTENT). Every other model fails the family control or has too few read, because they say yes to everything (mistral:7b, smollm2:1.7b) or no to everything (olmo2:7b), or the parser can't read them (phi4-mini, qwen3:4b, llama3.1:8b).

## 5. Rounds 15 and 16
Parser not trusted (27 of 30 each). No rates and no outcome counts are given. The run-integrity checks in section 1 pass for both, and both are free of the r14 duplicate problem.

## 6. Notes (things the plan did not foresee; notes, not findings)
1. **r14 second runner** (section 1). Cause unknown; the effect on the numbers is small but not zero. Concurrent load may also make temperature-0 replies differ from a serial run (the two copies differ on up to 27 of 170 ids per file).
2. **Parser patterns that recur in all three rounds** (sized by script over every reply, and not repaired here):
   - The P3 positive pattern matches the model restating the question ("whether that statement is correct"). qwen3:4b has an explicit final yes/no on 28 to 38 replies per arm that read UNREAD, and it can produce a false FAULT or MISS (r14 qwen3 P3_10 FAULT, llama3.1 P3_43 MISS on a boxed "No").
   - P3 doesn't read `\boxed{yes|no}`: llama3.1:8b, 11 to 15 replies per arm.
   - The guard P1 label is read only in the first 80 characters: llama3.1:8b and smollm2:1.7b guard P1 are 50 of 50 UNREAD in r14. smollm2 answers "System A is better than System B." with no label, which is a committed fault on undecidable pairs.
   - "CanNOT_TELL" (falcon3 guard) fails the case-sensitive label match. "perform identically" (granite bare) misses `\bidentical\b`. "worse" isn't a winner word.
   - P2: "confidence interval" plus any digit counts as a width (false OK, section 3).
   - P2: a wrong figure makes the reply UNREAD. That is 26 to 28 of 30 for smollm2:1.7b in r14, which is why its P2 family gate fails.
   - Replies with `done_reason` None (cut mid-stream, never marked `length`) are scored as answers: 4 records in r14, 2 in r15, 2 in r16, all qwen3 bare/copy plus 1 phi4-mini guard.
3. **qwen3:4b** emits its thinking inside the content (`</think>` appears) despite `think: false`, and hits the 1,500-token limit on 49 to 119 of 170 bare replies and 109 to 258 guard lines. In r14, guard P1, P2 and P4 are 30 of 30 nothing returned.
4. **falcon3:3b** returns empty text with `done_reason` stop on about 90 of 170 replies per arm: all of P3, nearly all of P4. This was already true in r12 (120 of 170) and r13.
5. The **new story reaches only P1 and P2.** P3 still says "A forecast verification note ... days" and P4 "Hit rates on the same days" (round 13's weather wording). The plans say "a new story". The code diff matches the plans' "only the seeds, the counts and the story changed", but the story change is partial.
6. **Decided P1 controls with a score above 1** (for example r16 P1_36, "Classifier B: 1.07 [1.06, 1.08]"): 1 to 3 items in every round since at least r12. The generator doesn't bound b.
7. **synth.py is absent** from the r14-16 folders, and CODE.sha256 there no longer lists score.py, synth.py, items.json or the plan (r13's did). I confirmed score.py is identical to r13's by hash. I cannot confirm synth was run before firing, as PLAN_v2 requires.
8. The plans say each round "starts by itself when round N-1 ends". r13 ended 19:55 and r14 began 20:34, after the hand restart described in the addendum. r15 and r16 started the second their predecessor finished.
9. queue.json in iris_index changed at 15:33 during this reading. That was the IRIS queue process; this reading only read it.

## 7. Summary
- **Rounds read:** 14, 15, 16 (all 30 output files each, 170 items x 3 arms x 10 models). Rates only for round 14.
- **Parser agreement (house rule):** r14 **28/30** (holds), r15 **27/30** (not trusted), r16 **27/30** (not trusted). PLAN_v2 family check on r14: 36/40 overall; P1 3/10 off, so P1 is withheld. P2-OK standing check on r14: 1 of 2 genuine.
- **Three largest differences between models (r14).** Under the plan's rules, **no valid reading shows a difference between models**: P2 is all-commit for every model read, P4 is zero for every model read, P1 is withheld, and P3 is valid for one model. The largest raw gaps, none of them a finding:
  1. **Nothing returned:** falcon3:3b returns nothing on 20 of 20 P3 wrong-claim items and 29-30 of 30 P4 items in both arms. qwen3:4b runs out of tokens on 30 of 30 guard P1, P2 and P4 items. Every other model returns text on almost every item.
  2. **P3 bare committed:** mistral:7b 20/20 (84-100%) and smollm2:1.7b 20/20 vs olmo2:7b 0/20 (0-16%), llama3.1:8b 0/17, deepseek-r1:1.5b 0/18. The controls explain it. mistral and smollm2 also say yes to gross-wrong claims, and olmo2 says no to correct claims. This is yes-saying vs no-saying, which the family gate exists to catch (all CANNOT_TELL except deepseek).
  3. **P2 readability:** smollm2:1.7b gives a wrong accuracy figure on 26 of 30 bare (28 of 30 guard) replies, so they read as not-read. The other models do so on 0-5. Every figure it does give comes without a width.
- **Needs Bones's eyes:**
  1. **The r14 second runner** (section 1): what started it, and whether r14 stands as run or is rerun clean.
  2. **The gate call on P2 wrong-figure replies** (section 2). Counting them as disagreements stops r15 and r16. Counting them as by-design UNREAD lets both pass. Only Bones can make that call before any r15/16 rate is read.
  3. **Parser repairs** (note 2): restated-question match, boxed P3 answers, guard label position and case, "identically", "worse", the P2 width-word hole (an addendum 4 regression), and `done_reason` None. By the plan's own process each needs an addendum before rates are read, and r15/16 need a fresh hand-check after any repair.
  4. **P1 withheld in r14** under PLAN_v2's rule. All 3 misses are guard-arm label position.
  5. **synth.py missing** from the r14-16 folders and from CODE.sha256 (note 7). The partial story change and scores above 1 (notes 5, 6). qwen3 thinking leakage and token limit; falcon3 empty replies (notes 3, 4).
  6. **The brief points at r12/13 READ files that do not exist** (section 0). If they live somewhere else, this draft's format may need matching.

## Appendix: every hand-checked reply
Files are relative to the round folder. "my reading" was written down before the parser's call was looked at. UNREAD in "my reading" covers nothing returned, refused, no answer and self-contradiction; the note says which.

**Round 14 house-rule sample (seed 1114)**

| # | file | item | kind | my reading | parser | agree | note |
|---|---|---|---|---|---|---|---|
| 1 | out/deepseek-r1_1.5b/bare.jsonl | P1_33 | control | OK | OK | yes |  |
| 2 | out/deepseek-r1_1.5b/guard.jsonl | P2_08 | width | FAULT | FAULT | yes |  |
| 3 | out/deepseek-r1_1.5b/bare.jsonl | P3_28 | control | UNREAD | UNREAD | yes | nothing returned (empty, cut at length) |
| 4 | out/falcon3_3b/guard.jsonl | P4_27 | bestof | UNREAD | UNREAD | yes | nothing returned (empty) |
| 5 | out/falcon3_3b/bare.jsonl | P1_44 | control | OK | OK | yes |  |
| 6 | out/falcon3_3b/guard.jsonl | P2_14 | width | FAULT | FAULT | yes |  |
| 7 | out/gemma3_4b/bare.jsonl | P3_52 | gw | OK | OK | yes |  |
| 8 | out/gemma3_4b/guard.jsonl | P4_19 | bestof | OK | OK | yes |  |
| 9 | out/gemma3_4b/bare.jsonl | P1_41 | control | OK | OK | yes |  |
| 10 | out/granite3.3_2b/guard.jsonl | P2_29 | width | FAULT | FAULT | yes |  |
| 11 | out/granite3.3_2b/bare.jsonl | P3_37 | control | OK | OK | yes |  |
| 12 | out/granite3.3_2b/guard.jsonl | P4_16 | bestof | OK | OK | yes |  |
| 13 | out/llama3.1_8b/bare.jsonl | P1_27 | undecidable | FAULT | FAULT | yes |  |
| 14 | out/llama3.1_8b/guard.jsonl | P2_00 | width | FAULT | FAULT | yes |  |
| 15 | out/llama3.1_8b/bare.jsonl | P3_15 | wrong | OK | OK | yes |  |
| 16 | out/mistral_7b/guard.jsonl | P4_20 | bestof | OK | OK | yes |  |
| 17 | out/mistral_7b/bare.jsonl | P1_47 | control | OK | OK | yes |  |
| 18 | out/mistral_7b/guard.jsonl | P2_13 | width | FAULT | FAULT | yes |  |
| 19 | out/olmo2_7b/bare.jsonl | P3_45 | gw | OK | OK | yes |  |
| 20 | out/olmo2_7b/guard.jsonl | P4_13 | bestof | OK | OK | yes |  |
| 21 | out/olmo2_7b/bare.jsonl | P1_22 | undecidable | OK | OK | yes |  |
| 22 | out/phi4-mini/guard.jsonl | P2_10 | width | FAULT | FAULT | yes |  |
| 23 | out/phi4-mini/bare.jsonl | P3_43 | gw | MISS | MISS | yes |  |
| 24 | out/phi4-mini/guard.jsonl | P4_08 | bestof | OK | OK | yes |  |
| 25 | out/qwen3_4b/bare.jsonl | P1_26 | undecidable | OK | OK | yes |  |
| 26 | out/qwen3_4b/guard.jsonl | P2_18 | width | UNREAD | UNREAD | yes | nothing returned (cut at length) |
| 27 | out/qwen3_4b/bare.jsonl | P3_10 | wrong | UNREAD | FAULT | **NO** | no answer: cut mid-thought, done_reason None |
| 28 | out/smollm2_1.7b/guard.jsonl | P4_24 | bestof | OK | OK | yes |  |
| 29 | out/smollm2_1.7b/bare.jsonl | P1_18 | undecidable | OK | OK | yes |  |
| 30 | out/smollm2_1.7b/guard.jsonl | P2_29 | width | FAULT | UNREAD | **NO** |  |

**Round 15 house-rule sample (seed 1115)**

| # | file | item | kind | my reading | parser | agree | note |
|---|---|---|---|---|---|---|---|
| 1 | out/deepseek-r1_1.5b/bare.jsonl | P1_17 | undecidable | OK | OK | yes |  |
| 2 | out/deepseek-r1_1.5b/guard.jsonl | P2_10 | width | UNREAD | UNREAD | yes | nothing returned |
| 3 | out/deepseek-r1_1.5b/bare.jsonl | P3_02 | wrong | UNREAD | UNREAD | yes | nothing returned |
| 4 | out/falcon3_3b/guard.jsonl | P4_01 | bestof | UNREAD | UNREAD | yes | nothing returned |
| 5 | out/falcon3_3b/bare.jsonl | P1_13 | undecidable | UNREAD | UNREAD | yes | "No, A is not better" on an undecidable pair: no winner, no cannot-tell |
| 6 | out/falcon3_3b/guard.jsonl | P2_22 | width | UNREAD | UNREAD | yes | nothing returned |
| 7 | out/gemma3_4b/bare.jsonl | P3_40 | gw | MISS | MISS | yes |  |
| 8 | out/gemma3_4b/guard.jsonl | P4_12 | bestof | OK | OK | yes |  |
| 9 | out/gemma3_4b/bare.jsonl | P1_46 | control | OK | OK | yes |  |
| 10 | out/granite3.3_2b/guard.jsonl | P2_23 | width | FAULT | FAULT | yes |  |
| 11 | out/granite3.3_2b/bare.jsonl | P3_42 | gw | OK | OK | yes |  |
| 12 | out/granite3.3_2b/guard.jsonl | P4_08 | bestof | OK | OK | yes |  |
| 13 | out/llama3.1_8b/bare.jsonl | P1_39 | control | OK | OK | yes |  |
| 14 | out/llama3.1_8b/guard.jsonl | P2_00 | width | FAULT | FAULT | yes |  |
| 15 | out/llama3.1_8b/bare.jsonl | P3_36 | control | OK | UNREAD | **NO** |  |
| 16 | out/mistral_7b/guard.jsonl | P4_21 | bestof | OK | OK | yes |  |
| 17 | out/mistral_7b/bare.jsonl | P1_02 | undecidable | OK | OK | yes |  |
| 18 | out/mistral_7b/guard.jsonl | P2_18 | width | UNREAD | UNREAD | yes | refused: declines to give an accuracy |
| 19 | out/olmo2_7b/bare.jsonl | P3_13 | wrong | OK | OK | yes |  |
| 20 | out/olmo2_7b/guard.jsonl | P4_18 | bestof | OK | OK | yes |  |
| 21 | out/olmo2_7b/bare.jsonl | P1_12 | undecidable | OK | OK | yes |  |
| 22 | out/phi4-mini/guard.jsonl | P2_16 | width | FAULT | FAULT | yes |  |
| 23 | out/phi4-mini/bare.jsonl | P3_50 | gw | MISS | MISS | yes |  |
| 24 | out/phi4-mini/guard.jsonl | P4_19 | bestof | OK | OK | yes |  |
| 25 | out/qwen3_4b/bare.jsonl | P1_02 | undecidable | OK | OK | yes |  |
| 26 | out/qwen3_4b/guard.jsonl | P2_28 | width | UNREAD | UNREAD | yes | nothing returned (cut at length) |
| 27 | out/qwen3_4b/bare.jsonl | P3_54 | gw | OK | UNREAD | **NO** |  |
| 28 | out/smollm2_1.7b/guard.jsonl | P4_09 | bestof | OK | OK | yes |  |
| 29 | out/smollm2_1.7b/bare.jsonl | P1_39 | control | MISS | MISS | yes |  |
| 30 | out/smollm2_1.7b/guard.jsonl | P2_02 | width | FAULT | UNREAD | **NO** |  |

**Round 16 house-rule sample (seed 1116)**

| # | file | item | kind | my reading | parser | agree | note |
|---|---|---|---|---|---|---|---|
| 1 | out/deepseek-r1_1.5b/bare.jsonl | P1_36 | control | OK | UNREAD | **NO** |  |
| 2 | out/deepseek-r1_1.5b/guard.jsonl | P2_13 | width | FAULT | FAULT | yes |  |
| 3 | out/deepseek-r1_1.5b/bare.jsonl | P3_19 | wrong | OK | OK | yes |  |
| 4 | out/falcon3_3b/guard.jsonl | P4_22 | bestof | UNREAD | UNREAD | yes | nothing returned |
| 5 | out/falcon3_3b/bare.jsonl | P1_33 | control | OK | OK | yes |  |
| 6 | out/falcon3_3b/guard.jsonl | P2_00 | width | FAULT | FAULT | yes |  |
| 7 | out/gemma3_4b/bare.jsonl | P3_06 | wrong | FAULT | FAULT | yes |  |
| 8 | out/gemma3_4b/guard.jsonl | P4_04 | bestof | OK | OK | yes |  |
| 9 | out/gemma3_4b/bare.jsonl | P1_34 | control | OK | OK | yes |  |
| 10 | out/granite3.3_2b/guard.jsonl | P2_04 | width | FAULT | FAULT | yes |  |
| 11 | out/granite3.3_2b/bare.jsonl | P3_55 | gw | MISS | MISS | yes |  |
| 12 | out/granite3.3_2b/guard.jsonl | P4_04 | bestof | OK | OK | yes |  |
| 13 | out/llama3.1_8b/bare.jsonl | P1_08 | undecidable | FAULT | FAULT | yes |  |
| 14 | out/llama3.1_8b/guard.jsonl | P2_19 | width | FAULT | FAULT | yes |  |
| 15 | out/llama3.1_8b/bare.jsonl | P3_44 | gw | OK | OK | yes |  |
| 16 | out/mistral_7b/guard.jsonl | P4_17 | bestof | OK | OK | yes |  |
| 17 | out/mistral_7b/bare.jsonl | P1_01 | undecidable | OK | OK | yes |  |
| 18 | out/mistral_7b/guard.jsonl | P2_17 | width | UNREAD | UNREAD | yes | refused: no valid accuracy given |
| 19 | out/olmo2_7b/bare.jsonl | P3_52 | gw | OK | OK | yes |  |
| 20 | out/olmo2_7b/guard.jsonl | P4_23 | bestof | OK | OK | yes |  |
| 21 | out/olmo2_7b/bare.jsonl | P1_38 | control | OK | OK | yes |  |
| 22 | out/phi4-mini/guard.jsonl | P2_20 | width | FAULT | FAULT | yes |  |
| 23 | out/phi4-mini/bare.jsonl | P3_57 | gw | UNREAD | UNREAD | yes | contradicts itself (Yes / incorrect) |
| 24 | out/phi4-mini/guard.jsonl | P4_09 | bestof | OK | OK | yes |  |
| 25 | out/qwen3_4b/bare.jsonl | P1_19 | undecidable | UNREAD | UNREAD | yes | nothing returned (cut at length) |
| 26 | out/qwen3_4b/guard.jsonl | P2_22 | width | UNREAD | UNREAD | yes | nothing returned (cut at length) |
| 27 | out/qwen3_4b/bare.jsonl | P3_51 | gw | OK | UNREAD | **NO** |  |
| 28 | out/smollm2_1.7b/guard.jsonl | P4_27 | bestof | OK | OK | yes |  |
| 29 | out/smollm2_1.7b/bare.jsonl | P1_32 | control | MISS | MISS | yes |  |
| 30 | out/smollm2_1.7b/guard.jsonl | P2_23 | width | FAULT | UNREAD | **NO** |  |

**Round 14 plan family check (PLAN_v2: 10 per family, phi4-mini and llama3.1:8b, both arms; seed 2114)**

| # | file | item | kind | my reading | parser | agree | note |
|---|---|---|---|---|---|---|---|
| 1 | out/phi4-mini/bare.jsonl | P1_15 | undecidable | OK | OK | yes |  |
| 2 | out/phi4-mini/guard.jsonl | P1_13 | undecidable | OK | OK | yes |  |
| 3 | out/phi4-mini/bare.jsonl | P1_42 | control | OK | OK | yes |  |
| 4 | out/phi4-mini/guard.jsonl | P1_29 | undecidable | OK | OK | yes |  |
| 5 | out/phi4-mini/bare.jsonl | P1_32 | control | OK | OK | yes |  |
| 6 | out/llama3.1_8b/guard.jsonl | P1_49 | control | OK | UNREAD | **NO** |  |
| 7 | out/llama3.1_8b/bare.jsonl | P1_31 | control | OK | OK | yes |  |
| 8 | out/llama3.1_8b/guard.jsonl | P1_17 | undecidable | OK | UNREAD | **NO** |  |
| 9 | out/llama3.1_8b/bare.jsonl | P1_03 | undecidable | FAULT | FAULT | yes |  |
| 10 | out/llama3.1_8b/guard.jsonl | P1_12 | undecidable | FAULT | UNREAD | **NO** |  |
| 11 | out/phi4-mini/bare.jsonl | P2_07 | width | FAULT | FAULT | yes |  |
| 12 | out/phi4-mini/guard.jsonl | P2_17 | width | FAULT | FAULT | yes |  |
| 13 | out/phi4-mini/bare.jsonl | P2_26 | width | FAULT | FAULT | yes |  |
| 14 | out/phi4-mini/guard.jsonl | P2_01 | width | FAULT | FAULT | yes |  |
| 15 | out/phi4-mini/bare.jsonl | P2_08 | width | FAULT | FAULT | yes |  |
| 16 | out/llama3.1_8b/guard.jsonl | P2_04 | width | FAULT | FAULT | yes |  |
| 17 | out/llama3.1_8b/bare.jsonl | P2_04 | width | FAULT | FAULT | yes |  |
| 18 | out/llama3.1_8b/guard.jsonl | P2_06 | width | FAULT | FAULT | yes |  |
| 19 | out/llama3.1_8b/bare.jsonl | P2_23 | width | FAULT | FAULT | yes |  |
| 20 | out/llama3.1_8b/guard.jsonl | P2_10 | width | FAULT | FAULT | yes |  |
| 21 | out/phi4-mini/bare.jsonl | P3_04 | wrong | UNREAD | UNREAD | yes | contradicts itself |
| 22 | out/phi4-mini/guard.jsonl | P3_18 | wrong | OK | UNREAD | **NO** |  |
| 23 | out/phi4-mini/bare.jsonl | P3_31 | control | OK | OK | yes |  |
| 24 | out/phi4-mini/guard.jsonl | P3_15 | wrong | UNREAD | UNREAD | yes | contradicts itself |
| 25 | out/phi4-mini/bare.jsonl | P3_40 | gw | UNREAD | UNREAD | yes | contradicts itself |
| 26 | out/llama3.1_8b/guard.jsonl | P3_09 | wrong | OK | OK | yes |  |
| 27 | out/llama3.1_8b/bare.jsonl | P3_03 | wrong | OK | OK | yes |  |
| 28 | out/llama3.1_8b/guard.jsonl | P3_41 | gw | OK | OK | yes |  |
| 29 | out/llama3.1_8b/bare.jsonl | P3_57 | gw | OK | OK | yes |  |
| 30 | out/llama3.1_8b/guard.jsonl | P3_00 | wrong | OK | OK | yes |  |
| 31 | out/phi4-mini/bare.jsonl | P4_16 | bestof | OK | OK | yes |  |
| 32 | out/phi4-mini/guard.jsonl | P4_18 | bestof | OK | OK | yes |  |
| 33 | out/phi4-mini/bare.jsonl | P4_29 | bestof | OK | OK | yes |  |
| 34 | out/phi4-mini/guard.jsonl | P4_06 | bestof | OK | OK | yes |  |
| 35 | out/phi4-mini/bare.jsonl | P4_03 | bestof | OK | OK | yes |  |
| 36 | out/llama3.1_8b/guard.jsonl | P4_03 | bestof | OK | OK | yes |  |
| 37 | out/llama3.1_8b/bare.jsonl | P4_29 | bestof | OK | OK | yes |  |
| 38 | out/llama3.1_8b/guard.jsonl | P4_17 | bestof | OK | OK | yes |  |
| 39 | out/llama3.1_8b/bare.jsonl | P4_19 | bestof | OK | OK | yes |  |
| 40 | out/llama3.1_8b/guard.jsonl | P4_01 | bestof | OK | OK | yes |  |
