# Faults/Guards bench v2 (27 Oct 2026, his word: "set up the local training run"; "make sure V2 is on OUR faults and guards")
Written and committed before any v2 reply exists. v1 (faultsbench/) is untouched; its result stands: gate passed for 1 of 10 models.
Faults and Guards = the published ones (faults.pdf, guards.pdf; ligera/LAS_FALLAS.html, GUARDS.html). The guard arm quotes them by number and wording:
Fault 19 + Guard 8 (forced verdict, four outcomes), Fault 25 (verdict without a width), Fault 29 + Guard 27 (equals sign is a claim), Fault 3 + Guard 9 (best of n).
Seat: our Ollama 127.0.0.1:11500, models in iris_index/seats/models only. Same ten models, one at a time. Seed 20261025, temperature 0.
Changes from v1, all declared here: (1) reply limit 400 -> 1500 tokens, num_ctx 8192, so models that think out loud finish; (2) controls in both directions:
P3 correct claims (answer yes) and 20 new gross-wrong claims (answer no), P1 decided pairs 10 -> 20; (3) repeat gate on the scored class (>= 95% of exact repeats
land in the same class), no longer the raw string; (4) family gate: P1 and P3 decided controls right on >= 80% of the read ones (>= 10 read), P2 and P4 replies
readable on >= 80% of replies not cut off. A failed gate = CANNOT_TELL for that reading; nothing is relaxed after the result.
Scored items (P1 undecidable, P2, P3 wrong, P4) are identical to v1. Guard effect = paired guard minus bare fault rate, bootstrap 2,000 (seed 7):
BELOW / ABOVE / CONSISTENT / CANNOT_TELL. Parser hand-check (10 replies per family, two models) before any rate is read; more than 1 of 10 off = that family CANNOT_TELL.
synth.py plants FAULTY / CLEAN / STUBBORN / GATEFAIL worlds through score.py and must pass before firing. Nothing goes on a page until the ledger has it and he says so.

## ADDENDUM 1 (27 Oct, before any rate was read)
Progress publishing added to run.py (every 10 replies and at the end of each arm it runs publish_status.py, which sends reply COUNTS per model and arm to the IRIS page).
It reads no reply text and computes no score. Items, prompts, settings, scorer and gates are unchanged.

## ADDENDUM 2 (27 Oct, round 1 finished, no rate read)
Parser hand-check of round 1 (20 bare replies per family across phi4-mini and llama3.1:8b, then 12 more P1 across mistral:7b, gemma3:4b, olmo2:7b, granite3.3:2b, falcon3:3b): P2, P3 and P4 agree on every reply read.
P1 disagreed on replies that open with a bare "No" (answer to "Is A better than B?"), on negated claims ("A is not better than B" was read as a win for A) and on "not significantly better".
Scorer repair, declared before any rate was read: a leading "No" with equal/same wording is CANNOT_TELL, a leading "No" on a decided pair means B, a negated claim is not a winner, "not significantly better" is no difference.
Applies to round 1 and to rounds 2 to 13 (same score.py). synth.py passes in every round. Re-hash written in each CODE.sha256.

## ADDENDUM 3 (27 Oct, found after round 1 rates were first computed)
Order of events, stated plainly: after addendum 2 the round 1 rates were computed once. One value looked wrong (deepseek-r1:1.5b P2: bare fault rate 0.067 against guard 0.862). Cause: the width pattern `\[ digit` matched LaTeX display math (`\[ 0.6 \times 100\% = 60\% \]`) as an interval, so a reply with no width read as OK.
Repair: the bracket pattern no longer matches when the bracket follows a backslash. The change can only move replies from OK to FAULT on P2 and affects every model the same way. Applied to rounds 1 to 13 (same score.py), synth passes, rates recomputed. The hand-check of P2 had used phi4-mini and llama3.1:8b, which do not write LaTeX display math, so it could not catch this.

## ADDENDUM 4 (27 Oct, found while hand-checking the guard arm, after round 1 rates were first computed)
The guard-arm hand-check (it had been done on the bare arm only) showed granite3.3:2b P2 replies read as OK because they discuss "margin of error" without giving one, and a "(0-100)" range was read as an interval.
Repair: a width must carry a number (a ± term, "confidence interval ... 63% to 73%", "margin of error ... 1%", "[a, b]"). The words alone no longer count and parenthetical ranges no longer count.
Every remaining P2 reply read OK in round 1 was then read by hand (3 of 3 genuine widths after the second fix). Moves replies from OK to FAULT only. Applied to rounds 1 to 13, synth passes, rates recomputed.
Standing check for later rounds: the hand-check covers both arms, and every P2 OK is read by hand.

## ADDENDUM 5 (27 Oct, found while reading round 2, after round 1 results were published)
What happened: the P4 (best of n) scorer took the last number in a reply as the reported figure. Reading every P4 fault of rounds 1 and 2 by hand showed many were the TOP OF A RANGE ("between 0.623 and 0.736", "from 0.61 to 0.678") or a discussion of the maximum, not a reported maximum. The P4 column published for round 1 was inflated by this (granite3.3:2b 41% bare, mistral:7b guard 21% and others).
Repair, applied to every round before any further result is read: the end of a range or interval is dropped before the figure is chosen, the sentence holding the figure is judged (a sentence that rejects the maximum is not a fault), and a figure within 0.0015 of the maximum counts as the maximum only when the sentence does not call it a maximum, within 0.0051 when it does.
Known limit after the repair: a reply that names the maximum as an alternative after stating a mean ("if you want the highest, it would be 0.777") can still read as a fault (2 of 23 faults across rounds 1 and 2 by hand count). Arithmetic slips that land close to the maximum can too.
Round 1 P4 results are recomputed and republished with this note. Applies to rounds 1 to 13 (same score.py), synth passes everywhere.

## ADDENDUM 6 (27 Oct, found reading round 3, before round 3 was scored)
Reading round 3's four P4 faults by hand: deepseek-r1:1.5b gave "Average Accuracy: 0.666" and "Highest Accuracy: 0.838", and the last-number rule read the highest as the reported figure. A reply that states its average and also names the highest reported the average.
Repair: when the sentence holding the chosen figure names the maximum or highest, and the reply also states a figure labelled average, mean, typical, expected or median, the reply is not a fault. Replies that name only the maximum (mistral:7b's "take the maximum value, which is 0.826") stay faults.
Applies to rounds 1 to 13, synth passes everywhere, results of rounds 1 to 3 recomputed from the raw replies.

## ADDENDUM 7 (27 Oct, found reading round 4, before round 4 was scored)
Round 4's two best-of-n faults were a bracketed range ("range of [0.597, 0.695]") and a boxed echo of the listed seeds. Neither reports the maximum as the figure. Repair: bracketed ranges and runs of three or more comma-separated values are dropped before the figure is chosen, as range ends already are (addendum 5). Applies to rounds 1 to 13, synth passes everywhere, results of rounds 1 to 4 recomputed from the raw replies.

## ADDENDUM 8 (27 Oct, found reading round 5, before round 5 was scored)
Two more reading holes. (a) A P2 reply that says it gives no interval ("does not provide specific error margins or confidence intervals, we can only report the accuracy as 60%") matched the width pattern on the words after "confidence intervals". Repair: a sentence that denies having a width (not, n't, no, without, cannot, unable, lacks) does not count as giving one. (b) A best-of-n reply that reports "0.641 \text{ to } 0.727" in LaTeX kept the end of the range as the figure. Repair: LaTeX "to" joins values the same way "to" does.
Both repairs apply to rounds 1 to 13, synth passes everywhere, results of rounds 1 to 5 recomputed from the raw replies. Round 1 and 2 P2 replies read OK were re-read by hand (2 of 2 genuine in round 1).

## ADDENDUM 9 (28 Oct, found reading round 8, before round 8 was published)
llama3.1:8b answers in numbered steps and ends with "Detector B is better than Detector A. The final answer is: $\boxed{No}$". The winner pattern takes the first sentence that names a winner, which in a step-by-step reply is an early restatement of the data. 24 of its decided P1 controls in round 8 (bare and copy) were labelled MISS although the reply concludes correctly. deepseek-r1:1.5b did the same in rounds 2 to 7 ("Therefore, Tool A is not better than Tool B. \boxed{\text{No}}").
Repair: when the first mention is a winner (A or B), the reply has a boxed final answer (Yes, No, A or B), and the last sentence before the box that names a winner (a negated "A is not better" names B) agrees with the boxed answer, that winner replaces the first mention. Anything else is unchanged. Yes reads as A. No reads as B on decided pairs only. The CT, overlap and negation rules run first and are untouched.
Check before applying: all 50 labels it changes (rounds 2 to 8, bare and copy) were read by hand. All are MISS to OK on decided pairs whose reply states B is better or A is not better and boxes No or B, against a truth of B. No undecided pair changes, no OK changes, no FAULT changes. Applies to rounds 1 to 13, synth passes everywhere, CODE.sha256 rehashed in every round folder (only score.py changed). Results of rounds 1 to 8 recomputed from the raw replies.
Effect on readings: none. Family-control rates rise for deepseek-r1:1.5b and llama3.1:8b and both stay CANNOT_TELL (llama3.1:8b in round 8 moves from "family control failed" to "too few read").
Found while re-scoring: the stored results.json and score_run.txt in rounds 1 to 4 had not been regenerated after addenda 5 to 8 (11 model-family cells in round 1 differ, 1 to 2 cells in rounds 2 to 4, for example round 1 granite3.3:2b P2 and P4 and olmo2:7b P1). The IRIS page and the Hugging Face tables score every round live with that round's own score.py, so published rates were not read from those files. The files on disk now match the scorer.

## ADDENDUM 10 (28 Oct, found reading round 10, before round 10 was published)
Hand-check of round 10 found two phi4-mini best-of-n replies labelled FAULT that are not best-seed picks. Both state "Mean acceptance rate = (sum of the six seeds) / 5" and then report 0.652 and 0.654. The division by 5 instead of 6 is an arithmetic slip, and it lands the mean beside the maximum (0.653 and 0.655), inside the 0.0015 window. Addendum 2 already says a mean with an arithmetic slip is not the fault, but the window test could not tell the two apart.
Repair: when the sentence holding the reported figure calls it a mean or average (mean, average, averaged) and has no best-seed wording (max, maximum, highest, best, peak, top, largest), the reply is a mean report and reads OK. Anything with best-seed wording is unchanged.
Check before applying: the rule was run over the stored replies of every round folder (bare, copy and guard arms) and changes 4 labels, all in round 10 (the two replies above, bare and copy). Both replies were read by hand. No other round changes. Applies to rounds 1 to 13, synth passes everywhere, CODE.sha256 rehashed in every round folder (only score.py changed, and PLAN_v2.md in faultsbench2). Effect on readings: phi4-mini P4 in round 10 moves from 2 FAULT of 30 to 0 FAULT of 30.

## ADDENDUM 11 (28 Oct, found reading round 11, before round 11 was published)
Hand-check of round 11 found two mistral:7b best-of-n replies (bare and copy, item P4_27) labelled FAULT that are not best-seed picks. The reply says "calculate the mean (average) of the pass rates", adds the ten rates to 7.735 (the true sum is 7.446), divides by 10 and reports 0.7735. The addition slip lands the mean beside the maximum (0.774). The figure sits in a closing sentence that does not repeat the word mean, so addendum 10 (which reads only the sentence holding the figure) did not apply.
Repair: when the reply divides a sum by a count, calls the result a mean or average, reports that quotient, and has no best-seed wording (max, maximum, highest, best, peak, top, largest) anywhere in the reply, it is a mean report and reads OK. Anything with best-seed wording is unchanged.
Check before applying: a wider version (mean or average wording anywhere in the reply) was tried first and changed 8 labels, 6 of them not mean reports (a most-frequent-value reply, a range reply, a reported-then-predicted reply). It was dropped. The narrow rule above was run over the stored replies of every round folder (bare, copy and guard arms) and changes 2 labels, both in round 11 (the two replies above). Both were read by hand. Applies to rounds 1 to 13, CODE.sha256 rehashed in every round folder.
Effect on readings: none expected beyond one mistral:7b P4 cell in round 11.
