# Lane D (IRIS) site pass, 30 Oct 2026. Packs L, P, O. Read only.

Scratch work (fetched pages, feeds, scripts): /Users/heuremen/bones-forge/watch/site_pass_20261030/scratch_D/

## 1. COVERAGE

- Pages in lane: 13 (the 13 URLs in lane_D_urls.txt: /iris, /iris/lab, /iris/key, /iris/list, 9 /iris/study/2610.* pages).
- Checked by script: 13 of 13. Live fetch with ?w=1 (all 200), 161 distinct links and scripts on them (all 200, internal and outbound), tag balance (no unclosed or stray tags), scan for semicolons, "undefined", "NaN", "null", email addresses, "Indahl", personal and internal names, AI statements, canonical and meta description.
- Read by eye: 13 of 13 (full text of each).
- Rendered in a real browser (so the JS sections were checked, not only the feed): /iris and /iris/lab. No "Loading." left, no console errors or warnings, train.js, bench.js and bench-results fill.
- Feeds checked against the page and the source: /iris/train.json, /iris/bench.json, /iris/bench2..11.json (all 11 complete), /iris/bench-results.json (11 rounds, index table recomputed and equal to the render), /iris/live.json (against queue.json), /headlines.json, /hosts/live.json, /stack/live.json (desk readings), /iris/list.json (equal to iris_list.json on disk).
- Sources recounted: matrix_v2_results_v2.json (all 10 models), MATRIX.md, MATRIX_v2.md, judge_counts/summary.json and the log it reads, training_counts/summary.json and the log it reads (independent recount), IRIS_BOOK_register.json, SCAN_register.json, the 11 recounts/*/RESULT.md, matrix/frontier/RESULT.md, falcon_train/falcon_results.txt, thunder_results.txt, ledger rows with surfaces iris_lab (32 of 32 text-equal to the lab page), iris_matrix (46, equal modulo cell separators), iris_paper.
- Papers fetched to test quotes: arXiv 2610.31256v1, 2610.18610v1, 2610.25964v2 (text extracted in scratch_D).
- NOT checked, with reason:
  - ~/bones-forge/iris_index/claims_lighteval/ not read (run in progress, as instructed). The lane pages say nothing about S1L or the claims rounds (grep of all 13 pages for lighteval, S1L, "model claims": 0). Only /iris/live.json names it (see D-27).
  - Whether S1L is making progress: the queue log queue_s1l-lighteval.log is 168 bytes since 08:41 local and I did not open it; process 17680 is alive 55 minutes. Liveness by completed work could not be confirmed without reading the run's files.
  - Parser hand-check (L1) of the Faults/Guards rounds was not redone. It is recorded in the plan addenda; I read only the counts.
  - The other 8 papers behind the study pages were checked against our recount files (RESULT.md and recount_out), not against the papers' own text. No quotation marks appear on those pages.
  - Desk pages HFSIZE, HFLICENSE, PKGLICENSE, PKGINSTALL, WEIGHTS, AILUMINATE, HOSTS belong to other lanes. I checked only their one-line readings on /iris against /stack/live.json.

Result in one line: no page number disagrees with its own source row. The findings are about what the numbers are called, what is left out beside them, and one selection claim the page's own grid contradicts.

## 2. FINDINGS

id: D-1 | check: I, V, P6, L5 | severity: wrong-claim
- where: https://indahl.ai/iris (section "Models as judges in our own pipeline", rows "Items the judge saw more than once" and "Of those, verdicts that differ between looks") and https://indahl.ai/iris/key row L7
- page says: "Items the judge saw more than once: 24 of 374". "Of those, verdicts that differ between looks: 22 of 24 (91.7% [74.2, 97.7])". Key L7: "a judge model gave different verdicts on 22 of 24 items it saw more than once".
- source says: the numbers equal /Users/heuremen/bones-forge/iris_index/judge_counts/summary.json (24, 374, 22). But the "item" key is not an item. judge_counts.py groups on the parenthetical tag of each log line (regex group 3 of autonomous_judge.log). Counted from that log: 1,779 verdicts over 374 tags. Tag "freed-sage-v3" has 1,013 verdicts (580 hold, 358 discard, 75 keep), "freed-sage-v3-armature" has 227. That name is the live adapter's name in the training evals (training_counts evals: live "freed-sage-v3"). The 16 tags "triangulated-ask_transformer-<one hex character>" hold 177 verdicts, so they are 16 buckets, not items. 175 tags "triangulated-ask_diffusion-<three hex characters>" hold 181 verdicts, and 6 of them repeat, about what chance collisions give (181 draws into 4,096 values expect about 4). The 181 "ask_rwkv" tags are all unique. So the 24 "seen more than once" are 2 adapter names, 16 one-character buckets and 6 collisions. "22 of 24 differ" says nothing about the judge's agreement with itself on the same item. It also puts a 95% interval on 24 buckets.
- fix at source: /Users/heuremen/bones-forge/iris_index/judge_counts/judge_counts.py (key on a real unique item id, or drop `items_judged_more_than_once`, `of_those_with_differing_verdicts`, `differing_share_pct`). Then drop the two rows in IRIS_JUDGE in /Users/heuremen/bones-forge/indahl-ai/build_site.py (about line 1648), the last sentence of KEY L7 in /Users/heuremen/bones-forge/iris_index/matrix_page/build_iris_page.py, and ledger rows iris.judge.multi and iris.judge.differ (as withdrawals with this evidence). The verdict counts and hold share can stay, but note that 1,240 of the 1,779 verdicts are on the two adapter names.

id: D-2 | check: I, VI, L6, P6 | severity: wrong-claim
- where: https://indahl.ai/iris/lab (section "The Two Finalists, Head to Head", first sentence), against the same page's "How Different Models Handle Faults and Guards" index table
- page says: "After eleven rounds, the two models with the lowest Fault rate under the Guard wording were smollm2:1.7b and qwen3:4b."
- source says: in the rendered index table qwen3:4b reads "Cannot tell in all 11 rounds" in all four families. In the feed /iris/bench-results.json qwen3:4b has 0 readable cells of 44 (23 "family control failed", 21 "too few read"). Yet /Users/heuremen/bones-forge/iris_index/select_finalists.py line 19 skips only outcomes starting "CANNOT_TELL (family" or "CANNOT_TELL (repeat". A family with "CANNOT_TELL (too few read)" (under 10 readable pairs, score.py line 111; 30 items per family, 20 for P3) stays in. Run as written it gives qwen3:4b a guard-arm mean of 0.167 from those 21 cells (output: smollm2:1.7b 0.058, qwen3:4b 0.167, olmo2:7b 0.210). Re-run with every CANNOT_TELL cell excluded (the page's own grid rule, copy at scratch_D/sel_strict.py), qwen3:4b has no score and the finalists are smollm2:1.7b and olmo2:7b (0.224). THUNDERDOME_PLAN.md says "families whose gate failed excluded". The Fault rate for the second finalist is therefore the rate among the few replies that were not cut off at the token budget, which the grid itself calls cannot tell.
- fix at source: select_finalists.py line 19 (exclude any outcome starting "CANNOT_TELL"), a dated plan addendum in THUNDERDOME_PLAN.md saying the selection rule did not match its text, and either re-run the arena with the corrected pair or change the lead sentence in IRIS_THUNDER in /Users/heuremen/bones-forge/indahl-ai/build_site.py (about line 303) to say what was computed ("lowest mean Fault rate among readable replies, counting families with fewer than 10 readable pairs"). Bones decides which.

id: D-3 | check: VI, V | severity: wrong-claim
- where: https://indahl.ai/iris, first H2 (id headline), and the table under it
- page says: "Reverse the order of the options and the score holds within a few points, but 27% to 50% of the answers change."
- source says: /Users/heuremen/bones-forge/iris_index/matrix/matrix_v2_results_v2.json key mcq4_rev_acc_change for the four models read: phi4-mini +3.5 [-3.5, +10.1], mistral:7b +1.5 [-4.5, +8.1], falcon3:3b -3.1 [-10.9, +4.1], smollm2:1.7b +2.6 [-5.2, +9.9]. Every interval holds zero and reaches 8 to 11 points on one side. "Holds within a few points" is the point estimate. On the size that would matter the reading is cannot tell.
- fix at source: H2 string in build_iris_page.py (also repeated in the .replace in build_site.py line 1617). For example: "Reverse the order of the options and 27% to 50% of the answers change. The score change is within about 10 points of zero either way and the data cannot narrow it."

id: D-4 | check: P3, P10, P2, L3, I | severity: wrong-claim
- where: https://indahl.ai/iris, second H2 and its table ("Given a none option, gemma3:4b misses three in four real personas...")
- page says: column "Flip under option reversal": gemma3:4b 0.145 [0.100, 0.200], phi4-mini 0.075, mistral:7b 0.217, llama3.1:8b 0.150. H2: "gemma3:4b misses three in four real personas, and qwen3:4b tags two in five comments that have none."
- source says (numbers equal /Users/heuremen/bones-forge/iris_index/matrix/MATRIX.md and ledger pub2.tab_*). Four things the paper says and the page does not:
  1. The flip column is the v1 two-option cell (M3, Jev-ToM 2-option). MATRIX.md: "M3 at 2 options cannot separate order sensitivity from letter fallback (flips land on the preferred letter: gemma 27/29 A, mistral 39/43 B, phi4 13/15 B)". The paper caption: "Flips are at two options (see text)". The same page's top table gives other numbers under nearly the same label for the same models: gemma3:4b "cannot tell (failed the first-option check)" and 32.5% in the source, phi4-mini 27.8%, mistral:7b 27.3%, llama3.1:8b "cannot tell". Two different tasks, no label.
  2. "none" is counted only when the no-persona flag is set, "rule defined after the replies were seen" (paper table caption; MATRIX.md: "M1 rule (stated after the referee, 25 Oct)"). The page has no post-hoc label anywhere (grep "post hoc", "after the data": 0 on /iris and /iris/key). Its footer says "Every plan was committed before the data it describes."
  3. The paper adds: "gemma3's 76% false 'none' may be driven by our prompt or format; we report it as measured." The H2 states 75.5% flatly and Key L9 repeats it.
  4. The table is "first five models" (paper caption). The page shows 5 of the 10 models of the table above and does not say so. The omitted rows in MATRIX.md are larger than the two named in the H2: falcon3:3b false "none" 0.880, smollm2:1.7b over-attribution 0.991, olmo2:7b over-attribution 1.000 (false "none" 0.000), granite3.3:2b 0.138 / 0.473.
- fix at source: build_iris_page.py MODELS and the second H2: relabel the third column as two-option flips that include letter fallback (or drop it), add the post-hoc rule label and the gemma3 caveat as a line under the table, say "five of ten models, the other five are in the data zip", and name the benchmark and task (NepPlural for the personas, Jev-ToM for the flips). Check the H2 against the omitted rows.

id: D-5 | check: L6, I, P3 | severity: wrong-claim
- where: https://indahl.ai/iris, top table, column "Answers that changed, prompt reworded"; https://indahl.ai/iris/key row L2
- page says: falcon3:3b "22.2% [7.4, 40.7]", smollm2:1.7b "30.0% [10.0, 50.0]", granite3.3:2b "29.4% [17.6, 43.1]", phi4-mini "10.6% [5.6, 15.5]". Key L2: "falcon3:3b 22.2% ... smollm2:1.7b 30.0% ... of answers change". No n and no count of replies dropped.
- source says: matrix_v2_results_v2.json, key `terminations.mcq4_B` and the n in `mcq4_B_flip_minus_floor`. Template B rates rest on: falcon3:3b 27 of 200 (173 EMPTY), smollm2:1.7b 20 of 200 (180 NO_JSON), granite3.3:2b 51 of 200 (145 NO_JSON), phi4-mini 142 (58 NO_JSON), olmo2:7b 183 (13), mistral:7b 191 (9), gemma3:4b 195 (5), llama3.1:8b 200. The rate is taken on items answerable in both formats, so the denominator is built from the format that one arm fails more often (core I). The column header "prompt reworded" understates it: PLAN.md M5 calls it the format carrier, "Reply with the letter only" against story, question, options and a JSON answer.
- fix at source: build_iris_page.py HEAD2 (`_cell` and the `pc_(v['mcq4_B_flip_minus_floor'])` call): print "k of 200 read" in the cell or as a second line, and mark a model with more than 10% dropped as cannot tell (the plan's own NO_ANSWER_FIELD rule is 10%). Relabel the header "answer format changed". Update KEY L2 the same way.

id: D-6 | check: V, VI, L4 | severity: wrong-claim
- where: https://indahl.ai/iris, top table, column "Answers that changed, exact repeat"; Key L3
- page says: "0.0% [0.0, 0.0]" for seven of the eight read models (falcon3:3b "0.5% [0.0, 1.5]"). Key L3: "exact repeats agree on all but 0% to 0.5% of answers".
- source says: a bootstrap interval of an all-zero sample has zero width. 0 of 199 has a Wilson 95% upper bound near 1.9%. MATRIX.md: "the exact-repeat check is identical by construction (greedy, fixed seed), so it is a determinism check, not a noise floor". The paper: "which shows the setup is deterministic, not that it has no floor". The same paper reports that on the CUDA machine repeats matched byte for byte on only 127 to 158 of 170 items.
- fix at source: HEAD2 in build_iris_page.py (use Wilson for the repeat column, or print "0 of 199 changed"). Rename the header "exact repeat (determinism check)". In Key L3 name the seat (the Mac server) and say which machine the 0 to 0.5% is for.

id: D-7 | check: R, P7 | severity: wrong-claim
- where: https://indahl.ai/iris/list, row "Jev-ToM: Evaluating Theory of Mind in Typed Decision Models", receipt line "Measured on our setup"
- page says: 'the "excluding controls reverses the lead" figure (69.1 vs 70.9) does not rebuild from the released control marks: CANNOT_TELL'
- source says: /Users/heuremen/bones-forge/iris_index/IRIS_BOOK_register.json row arXiv:2610.18610v1, field `referee`: "reversal CONFIRMED (69.08 vs 70.87 ...). Our CANNOT_TELL withdrawn." recounts/2610.18610/RESULT.md ends the same way ("Our earlier CANNOT_TELL is WITHDRAWN"). The List is built from the `priced` field, which was never updated. The register also has two intervals for the same contrast: `referee` "-1.79 [-3.54, -0.09]" against RESULT.md "-1.79 [-3.54, -0.19]", and the lead as [+0.23, +2.92] (register) against [+0.22, +2.94] (RESULT.md) against [+0.25, +2.89] (priced, the one printed).
- fix at source: IRIS_BOOK_register.json field `priced` of 2610.18610 (state the reversal as rebuilt from `category`, 920 controls, 69.08 vs 70.87, and fix the interval typo), rerun /Users/heuremen/bones-forge/iris_index/matrix_page/iris_list.py, ship. The older BOOK line in build_iris_page.py ("Rebuilds, including the no-controls figures they report") already says the opposite of the List row.

id: D-8 | check: P4, P10, P6 | severity: wrong-claim
- where: https://indahl.ai/iris/key row L5 and https://indahl.ai/iris/study/2610.30512
- page says: Key L5 "What happens": "Results change when the provider's serving backend changes behind the same model name." Study page: "changed outcomes on 27.3% of prompts where the reported serving backend changed and 17.5% where it did not (+9.8 points [+2.1, +17.6])."
- source says: /Users/heuremen/bones-forge/iris_index/recounts/2610.30512/RESULT.md: "What it rules out: that a pinned model name at temperature 0 makes the serving backend irrelevant to a verdict. It does not name a cause." and the rebuttal "the changed-backend prompts were just closer to the boundary" is "Partly true: mean |margin| 0.89 differ vs 0.99 match", margin-stratified gap +8.0 pp [+0.7, +15.3], "defined after the data". The List row has the margin line and the label. The Key row names a cause (backend change makes results change) from a split of prompts by whether a fingerprint changed, and the study page and Key drop the +8.0 reading and its post-hoc label.
- fix at source: KEY L5 in build_iris_page.py (describe the split, not a cause, and add the margin reading with "defined after the data"); SHOW['2610.30512'] in build_iris_page.py (same).

id: D-9 | check: III, V, P2 | severity: wrong-claim
- where: https://indahl.ai/iris/key row L1; https://indahl.ai/iris/study/2610.30512 last sentence
- page says: Key L1: "falcon3:3b 42.5% ... smollm2:1.7b 50.0% of answers change with the options reversed (our setup). GPT-4.1, Claude Sonnet 4.5 and Gemini 2.5 Flash flip the verdict on 31.0%, 31.3% and 30.9%". Study page: "flip about 3 verdicts in 10 when the two answers swap position."
- source says: the first set is flip minus the exact-repeat floor, on 4-option items (our seat). The second set is a gross verdict-sign flip with no floor, from an earlier experiment "run once per judge under each provider's own code" (pub2 main.tex lines 75 to 80) and matrix/frontier/RESULT.md: "Not comparable to the seat's MCQ numbers; compare within a row." GPT-4.1 31.0% is the May run; the pinned October run is 28.1%, and 12.5 points [8.0, 16.7] above its own copy floor of 15.5% (the only judge with a floor). Unlike rulers sit in one cell and one sentence, and the location of the 31.0, 31.3 and 30.9 (frontier/RESULT.md F-M3, not the 30512 recount) is not given.
- fix at source: KEY L1 and SHOW['2610.30512'] in build_iris_page.py: split into two sentences, say "net of the exact repeat" for ours and "no repeat floor, one run per judge, earlier experiment" for the judges, and add the +12.5 above-floor figure for pinned GPT-4.1.

id: D-10 | check: R, I | severity: wrong-claim
- where: https://indahl.ai/iris, "Models as judges in our own pipeline", rows "Orchestrating model: rounds, each asking three models" and "Asks made"
- page says: "Orchestrating model: rounds, each asking three models: 11,057". "Asks made: 19,141".
- source says: /Users/heuremen/bones-forge/triangulate.log (the file judge_counts.py reads). 11,057 round lines. Asks per round: 0 asks in 4,634 rounds, 1 in 52, 2 in 24, 3 in 6,347. 11,057 x 3 = 33,171, not 19,141. Only 6,347 rounds (57%) asked three models. The 75.9% forced share is over asks, which come in triples within rounds.
- fix at source: IRIS_JUDGE in build_site.py: label the row "rounds logged" and add "rounds in which three models were asked: 6,347" (add `rounds_with_asks` to judge_counts.py).

id: D-11 | check: R, P2 | severity: wrong-claim
- where: https://indahl.ai/iris/study/2610.31135 ("What it shows about the model"), https://indahl.ai/iris/list receipt for Mixing Matters, Key L3
- page says: "Same model and seed: 800 of 800 items identical on the same host. On a different GPU and host, 0.95% of 8,000 items change."
- source says: recounts/2610.31135/recount.py line 37: item agreement is `np.nanmean(A==B)` over a questions x 10 positions matrix, so 8,000 cells for 800 questions. Printed: same host "item agreement 1.0000", cross-GPU "0.9905". "800 of 800" is the question count (n 800) and 0.95% is of 8,000 cells. One sentence uses two units for "items". The pub2 paper says "agree on all 9,600 records" for the same-host runs (a third denominator). The cross-GPU run is phase 5 (a different experiment, A10G against A40), and the primacy copy gap is +0.0019 [-0.0050, +0.0088], consistent with zero; the page does not say the 0.95% did not move the score.
- fix at source: SHOW['2610.31135'] and KEY L3 in build_iris_page.py; IRIS_BOOK_register.json 2610.31135 `priced`. Use "8,000 of 8,000 question-position cells identical" and "76 of 8,000 cells (0.95%) change, A40 against A10G; primacy gap +0.0019 [-0.0050, +0.0088], consistent with zero".

id: D-12 | check: P6, L7 | severity: wrong-claim
- where: https://indahl.ai/iris/study/2610.25159 and https://indahl.ai/iris/key row L7
- page says: "The GPT labeller the gold labels were reviewed from scores 0.960 accuracy on that gold, ahead of every trained classifier by 0.115 to 0.145."
- source says: RESULT.md B1: "The gold was made by reviewing that labeller's output (their own anchoring caveat), so how much of the lead is anchoring is CANNOT_TELL without a from-scratch gold set." The List row says it ("on a gold anchored to it; anchoring share CANNOT_TELL; corrected-item test n=8 CANNOT_TELL"). Pub2: "a reason to read the labeller's score on this gold as uninformative." The study page and Key give the lead with no caveat (pack L7).
- fix at source: SHOW['2610.25159'] and KEY L7 in build_iris_page.py: add "The gold was built by reviewing this labeller's output, so the lead cannot be separated from anchoring."

id: D-13 | check: P6, VI | severity: wrong-claim
- where: https://indahl.ai/iris/study/2610.25626
- page says: "With seeds as the unit, MapSteal leads on 2 of 18 settings, not the 12 of 18 the means give."
- source says: RESULT.md: ABOVE on 2 of 18 (lower bounds +0.03 and +0.06 points, Welch, 3 seeds v 3), CONSISTENT on 15, BELOW on 1 (2B CTI-Bench). Pub2 adds "uncorrected for 18 tests" and "bounds on a coarse ruler". At 5% over 18 tests about 0.9 false calls are expected, so 2 ABOVE is not separated from chance. The 12 of 18 is "a correct count of means" (pub2). "Leads" for the two and "not the 12 of 18" read as a correction of the authors.
- fix at source: SHOW['2610.25626'] in build_iris_page.py: "resolves in 2 of 18 settings (lower bounds +0.03 and +0.06, uncorrected for 18 tests), is consistent with zero in 15 and behind in 1. The authors' 12 of 18 is a correct count of means."

id: D-14 | check: P6, L7, P5 | severity: wrong-claim
- where: https://indahl.ai/iris/study/2610.21468 and Key L7; also its meta description
- page says: "On G1 against G2 the Gemini 3.1 Pro judge agrees with the reader majority 0.657 [0.486, 0.800] of the time, consistent with chance."
- source says: RESULT.md B1 has two contrasts, G1 vs G2 0.657 [0.486, 0.800] n 35 and G1 vs G0 0.839 [0.710, 0.968] n 31 ("ABOVE chance; CONSISTENT with reader-vs-reader"), and "One judge, two contrasts, two different answers." The List row prints both. The study page prints only the weak one, no n (35 items decisive for both, not "of the time" over all items), and no interval level.
- fix at source: SHOW['2610.21468'] in build_iris_page.py (add the second contrast and n for both).

id: D-15 | check: L8, II, R | severity: wrong-claim
- where: https://indahl.ai/iris/lab, "A Falcon Trained on the Faults and Guards"
- page says: table cells "A ahead, B ahead: gain" (column "Trained against mixed labels") and the status line "Training finished, 600 steps each, and every reply was received on both evaluation sets (30 Oct 01:57 UTC)."
- source says: (a) The table is one training run per arm (seed 20280007, train_config.yaml). FALCON_TRAIN_PLAN_3.md exists because "A different random seed could change which items the adapter gets right"; the second seed was trained and evaluated on four sets (seed2.sh, eval3_*.log, queue falcon-seed2 done 30 Oct 02:05 UTC) and is not read. Round 2 (sets C and D, FALCON_TRAIN_PLAN_2.md, queue falcon-r2-evals done 28 Oct 23:51 UTC) is also run and is not on the page. The page says "two fresh evaluation sets" and "Results follow" and never says it is one seed or that later rounds exist. The "gain" is against a control trained on mixed (partly wrong) labels; against the untouched model the same rows read "cannot tell" or "no gain" in all four families. (b) The time stamp in parentheses is `updated` from /iris/train.json, written by publish_train_status.py when it last ran (29 Oct 21:57 EDT), not when training or replies finished (train logs 28 Oct 15:25 and 15:31 EDT; evals ended 28 Oct about 17:20 EDT). Placed after "every reply was received" it reads as a completion time, about 28 hours after the last seed-1 reply. publish_train_status.py counts seed-1 files only.
- fix at source: IRIS_FALCON text in build_site.py (add "one training run per arm" and "a second seed and two further evaluation rounds are run and not yet read"); the finished-state text in /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/public/iris/train.js line 14 (say "last checked" or drop the stamp). falcon_results_page.py note.

id: D-16 | check: L6, P3 | severity: wrong-claim
- where: https://indahl.ai/iris/lab, "How Different Models Handle Faults and Guards" (index table and round grids) and the Falcon table note
- page says: "Cannot tell means the round's repeat or control checks failed." (bench.js note). Falcon note: "Replies with no readable answer are left out of the rates and counted in the replies file."
- source says: /iris/bench-results.json `why` field: of 440 model-family-round cells, 63 are cannot tell for "too few read" (fewer than 10 readable pairs), not for a failed repeat or control: qwen3:4b 21, deepseek-r1:1.5b 20, llama3.1:8b 9, falcon3:3b 7, phi4-mini 3, olmo2:7b 2, gemma3:4b 1. The `why` is in the feed and not shown. Rates in the index and grids come with no count of replies read or left out (the feed carries n read as the fourth number of each `bare` and `guard` triple). The Falcon note points to "the replies file" with no link and gives no counts. The Finalists table does print "k of 30 unread", so the page is inconsistent about it.
- fix at source: bench.js note text and drawRound (print n read; show `why`); falcon_results_page.py note and table (counts, link to the dataset).

id: D-17 | check: I, R, P10 | severity: wrong-claim
- where: https://indahl.ai/iris/lab, "The Two Finalists, Head to Head"
- page says: "The selection rule and the reading rule were committed before any round was read." Table and note: "Share of readable replies that commit the Fault with the plain prompt"; no guard-arm column.
- source says: THUNDERDOME_PLAN.md (commit ac4fd66, 27 Oct 09:33): finalists chosen on the guard-arm rate, and "Reading: ... paired fault difference ... on the guard arm and on the bare arm". The page shows the bare arm only and does not say the guard arm is not shown. The bench scorer got addenda 3 to 11 after rates were read (faultsbench2/PLAN_v2.md: addendum 3 "found after round 1 rates were first computed", addenda 9 to 11 on 28 Oct "rounds 1 to 8 rescored"), and select_finalists ran on the rescored rounds; the page does not label that. qwen3:4b P2 is 28 of 30 unread in round 12 and 0 of 30 unread in round 13 (same model, arm, budget) with no reason given; the plan's addendum 1 states "28 of 30 P2 items and 29 of 30 P4 items" as if one set.
- fix at source: IRIS_THUNDER text and thunder_results.html in build_site.py / iris_index (add the guard-arm column or the sentence that it is not shown; "scoring rules were amended 11 times, each dated, in the plan addenda" with a link). Related backlog from the 29 Oct audit: "page copy that says plans were committed first".

id: D-18 | check: P1 | severity: wrong-claim
- where: https://indahl.ai/iris/list, three receipt lines
- page says: (IndoNutriQA) '"GPT-4o matched by Llama-3.1-8B (overlapping CIs)"'; (Jev-ToM) '"excluding controls reverses the lead"'; (POPE) '"exceeds five of six"'.
- source says: IndoNutriQA 2610.31256v1 text: "frontier GPT-4o (F1 = 50.33) is matched by the smaller Llama-3.1-8B-Instruct (55.55) under five-shot prompting (overlapping CIs; Section 6.4)". Jev-ToM 2610.18610v1: "Removing native controls reverses Jev's lead over GPT-3.5, leaving 69.1% against 70.9%" (table caption: "Excluding controls, Jev scores 69.1% and GPT-3.5 70.9%"). POPE 2610.25964v2 abstract: "exceeds the adversarial gain reported by five of the six papers we surveyed". None of the three is verbatim; all are paraphrases inside quotation marks.
- fix at source: IRIS_BOOK_register.json fields `priced` of 2610.31256, 2610.18610 and 2610.25964 (quote the full clause or take the quotation marks off), regenerate with iris_list.py.

id: D-19 | check: P8, P1 | severity: broken
- where: <meta name="description"> and og/twitter description of 5 study pages: /iris/study/2610.30512, 2610.15732, 2610.21468, 2610.25159, 2610.25964
- page says: 30512: "...17.5% where it did not (+9.8 points." ; 15732: "Gemini is ahead of GPT by +0.052." (interval cut off) ; 21468: "...consistent with chance. Readers agree." ; 25159: "...by 0.115 to 0.145. It is." ; 25964: "...on the adversarial split, 5.37."
- source says: build_site.py line about 1711: `_desc = (_what[:150].rsplit(' ', 1)[0] + '.')` cuts at 150 characters and adds a full stop. The snippets are cut mid-bracket, drop the width, or say "Readers agree." (the study says readers agree with themselves 0.930) and "It is." (original: "It is not in the paper's results table.").
- fix at source: /Users/heuremen/bones-forge/indahl-ai/build_site.py (the `_desc` line in the IRIS study loop): cut at the last sentence end before 150 characters, never inside a bracket.

id: D-20 | check: P2, P3, L3 | severity: style
- where: https://indahl.ai/iris, top table (Findings), and https://indahl.ai/iris/key
- page says: "Score as reported", "Score change, options reversed", "cannot tell (failed the first-option check)", "cannot tell (replies cut off)". Nothing on the page names the benchmark, the item count, the settings, or the seat.
- source says: build_iris_page.py has HEAD_INTRO and HEAD_NOTE ("four-option questions from a public theory-of-mind benchmark", "counted against the same model's exact repeat", what cannot tell means) but the `body` f-string never includes them, so the live page lacks them (grep "theory-of-mind" on /iris: 0). Source facts missing from the page: 200 four-option Jev-ToM items, Ollama on our own Mac server, temperature 0, seed 20261025, num_ctx 4096, 500-token reply limit (num_predict, "length limit" in L4), JSON mode, "Score as reported" is accuracy on the original order over parsed items only (granite3.3:2b 173 of 200, olmo2:7b 195), "score change" is reversed minus original, "first-option check" is the positive control (pick the option listed first, 80% in both orders), "answers that changed" is net of the exact-repeat rate. No Ollama version is named (pack L4). The label "Score as reported" reads as the vendor's number.
- fix at source: add HEAD_INTRO and HEAD_NOTE (reworded, with the facts above) to `body` in build_iris_page.py; rename the column "Score on the original order".

id: D-21 | check: P5 | severity: style
- where: /iris (top tables, persona table), /iris/key (L1 to L9), the 9 study pages, /iris/list (all receipts), /iris/lab "Models" index and round grids
- page says: intervals such as "[21.7, 34.3]", "[+2.1, +17.6]", "[4.43, 7.83]", "[0.486, 0.800]" with no level or method.
- source says: the level appears only in the judge table header ("Share, 95% interval") and in the Falcon and Finalists notes. Sources: 2,000-draw bootstrap, percentile 2.5 and 97.5 (score_matrix_v2.py `ci`), 20,000 for the POPE recount, Welch for MapSteal, Wilson in publish_results.py.
- fix at source: one sentence under the top table and in the Key header ("Intervals are 95%, percentile bootstrap unless the row says otherwise"); `bench.js` note for the Models section; SHOW strings.

id: D-22 | check: P9 (plain sentences) | severity: style
- where: /iris/list (33 semicolons in receipts), /iris/lab Finalists table (8, "round 12: ...; round 13: ..."), /iris (5, the "Software this page uses or compares against" line)
- page says: e.g. "Read: full text, version v1; their released files (34 output files)".
- source says: house rule, no semicolons in page prose. Text lives in IRIS_BOOK_register.json (`recount`, `priced`), iris_list.py (receipt template), /Users/heuremen/bones-forge/iris_index/thunder_results.html, and the software line built in build_site.py (about line 2032).
- fix at source: those four places (use full stops or "and").

id: D-23 | check: P8, typos | severity: style
- where: https://indahl.ai/iris/list
- page says: "Data: /iris/runs/recounts.zip" (11 times, plain text, not a link); "their released files (1 output files)"; "(5037 output files)" with no thousands separator, while the same page writes "17,000/17,000".
- source says: iris_list.py receipt list item 'Data: /iris/runs/recounts.zip' is escaped text. The zip exists (200, 47,758 bytes).
- fix at source: iris_list.py (emit an anchor, singular "1 output file", thousands separator).

id: D-24 | check: P9 (AI statements) | severity: style
- where: https://indahl.ai/iris, section after "Inventory of Published Studies" (IRIS_FG)
- page says: "Our organization has had to employ a number of workarounds to keep the data accurate, including loading what is in these two PDFs into the model's context window first and checking the output again after every turn for known faults."
- source says: house rule: no statements about AI assistance on the site, footer rule only. The paragraph says we run a model in our own work. It may be deliberate copy (it sits with the Faults and Guards PDFs); flagged for Bones to rule on.
- fix at source: IRIS_FG in build_site.py (about line 1620), if it is to go.

id: D-25 | check: L3, P2 | severity: style
- where: https://indahl.ai/iris/study/2610.25964 and Key L6
- page says: "The model's answers score differently depending on which yes or no tokens are read: F1 moves 6.13 points [4.43, 7.83]..."
- source says: the abstract of 2610.25964v2: the model is LLaVA-1.5-7B "under 4-bit NF4 quantization, so we cannot say how much of any reported gain a matched evaluation would keep. That comparison stays unresolved until readout and precision are matched." Our own pub2 text says "from the same single 4-bit model". The page names neither the model nor the precision, and the List row's "exceeds five of six ... CANNOT_TELL" is the committed reading. Same on the 17203 page: "the planned scoring rule" and the rule under which 74.5 rebuilds (the favorite rule) are not defined anywhere on the study page.
- fix at source: SHOW['2610.25964'] and SHOW['2610.17203'] in build_iris_page.py.

id: D-26 | check: R, II, V | severity: style (open since the 29 Oct audit backlog "IRIS page pools")
- where: https://indahl.ai/iris, "Our own fine-tuning runs"
- page says: "Sessions whose last validation loss was below their first ... 36 of 99"; "Sessions whose lowest validation loss came before their last check: 92 of 99". Then: "Until 26 August the validation step scored a random 100 of the 489 validation examples ... The chart pools both periods."
- source says: the two table rows pool sessions from both periods too, and the page does not say how many of the 99 sessions are before the fix. With a random 100 of 489 each time, "lowest before the last check" is expected for most sessions and 92 of 99 is not evidence about training. All table values recount correctly (see HOLDS).
- fix at source: training_counts.py (split by the fix date, from the checkpoint or log date) and the IRIS_TRAIN rows in build_site.py.

id: D-27 | check: O2, O4, O5 | severity: broken (low)
- where: https://indahl.ai/iris/live.json and https://indahl.ai/iris/live.js, and https://indahl.ai/iris/lab (no status line)
- page says: nothing. The lab page no longer has a queue status (the "Running Now" table was dropped 30 Oct, build_site.py about line 1727). /iris/live.js and /iris/live.json are still published and updated (13:22 UTC while I read).
- source says: queue.json and live.json agree (running: s1l-lighteval; done: the last four of seven done jobs). The feed publicly names unpublished work: "Model claims round S1L: SmolLM2-1.7B-Instruct rerun with the card's own tool (lighteval)", S2 "Phi-4-mini-instruct", S3 "Granite 4.1 3B", and the plan path iris_index/claims_lighteval/ROUND_S1L.md. The Mac cross-seat plan says "Nothing goes on a page until the ledger has it and he says so." iris_queue.py line 32 marks a job `running` by `alive(pid)`, not by completed work (pack O4), and 'failed' only if the log contains the string FAILED. queue_s1-bbh-chat.log (marked done) holds 5 tracebacks "FileNotFoundError: 'npx'" (status publishing from a queue-spawned job has no npx on PATH, pack O5) before "S1B DONE". queue_s1l-lighteval.log is 168 bytes after 55 minutes.
- fix at source: decide whether /iris/live.json should keep publishing (remove the KV key iris_live or filter titles in iris_queue.py `publish`); set PATH in the `Popen` env in iris_queue.py; add a completed-work check for liveness.

id: D-28 | check: P2 | severity: style
- where: https://indahl.ai/iris, footer line "Software this page uses or compares against"
- page says: "MLX LM, MLX, Ollama, lm-evaluation-harness, huggingface_hub, faultsguards (ours)" with git and PyPI links.
- source says: the line is built from _SWMAP['iris'] in build_site.py. No result on /iris uses lm-evaluation-harness, MLX LM or MLX (the page's results come from Ollama; the Falcon training with MLX is on /iris/lab, which has no software line).
- fix at source: _SWMAP in build_site.py (move to /iris/lab, drop lm-eval until a claims round is public).

## 3. HOLDS (checks that found nothing)

- Numbers on /iris vs source: top table, all 10 models, every cell equal to matrix_v2_results_v2.json (score, change, flip, template B, repeat, cannot-tell reasons). Persona table equal to MATRIX.md and ledger pub2.tab_*. Judge table: all 11 numbers equal judge_counts/summary.json, the three shares re-derived (1,028/1,779, 623/1,779, 128/1,779), Wilson intervals recomputed. Fine-tuning table: all values equal training_counts/summary.json and independently recounted from train_continuous.log (99 sessions, 257,680 iterations, 25,768 training lines, 777 and 39 not-a-number lines, 1,378 validation lines) and from disk (134 adapter folders, 3,124 checkpoints). "1.478 to 2.116", "100 of 489", "488 of 489" equal train_continuous.sh lines 209 to 221. The two eval rows (0 of 11, 1 of 12, 0 of 2) equal the eval JSON.
- Key page L1 to L9 numbers vs sources: all equal (42.5, 27.3, 27.8, 50.0; L2 eight values; 108 of 200 and 191 of 200 length limit from done_reason; 0.95%; +9.8 [+2.1, +17.6]; 6.13 [4.43, 7.83], 5.37, 3.15; 72.9 vs 74.5; 0.960, 0.115 to 0.145; 0.657 [0.486, 0.800]; +0.21, +0.27, +0.20; 0.755 [0.696, 0.815]).
- Study pages vs RESULT.md: every number on all 9 pages equals its recount file. Post-hoc label present on 2610.17203 ("Judge scores rebuild only under a rule found after the data").
- /iris/list vs IRIS_BOOK_register.json and SCAN_register.json: 17 rows, file counts and versions equal, list.json on the site equals iris_list.json on disk.
- Lab page: Falcon table equals falcon_results.txt and the 20 ledger rows; Finalists table equals thunder_results.txt and 12 ledger rows; Faults and Guards names equal faults.pdf and guards.pdf text (FAULTS_GUARDS_TEXT.txt lines 12, 66, 91, 105, 176, 178, 214). Models index recomputed from /iris/bench-results.json and equal to the render (40 cells).
- Live sections fill (P8): /iris and /iris/lab rendered in a browser; train.js shows "Training finished, 600 steps each ..."; bench-live hidden when done; bench-more children hidden; bench-results fills with the index and 11 grids; no console messages. train.json equals falcon_train/status_train.json byte for byte. All 11 bench feeds complete (170 of 170 in every arm). headline.js: /iris headline is from /headlines.json (871 endpoints, 176 models, 45 below 100 percent at 13:22 UTC) and equals /hosts/live.json (871, 70 hosts, 176 models; 44 at 13:31); refresh every 2 minutes. The static HTML fallback (46, 11:50 UTC) is replaced by JS. Desk readings on /iris equal /stack/live.json (HFSIZE 11 of 142, HFLICENSE 0 of 86, PKGLICENSE 7 of 699, PKGINSTALL 0 of 525, WEIGHTS 0 of 912, AILUMINATE 0 of 27). LAB has no reading row and HOSTS has share null (NOTHING_RETURNED), so those two desk lines are blank by design.
- Links: 161 distinct links and scripts across the 13 pages, all HTTP 200 (internal and outbound, arXiv, GitHub, PyPI, Hugging Face, data zips).
- HTML: tags balanced on all 13 pages; no "undefined", "NaN" or "null" text; no email addresses; no "Indahl" in visible text; no personal names; "Heuremen LLC" throughout; section anchors on /iris and /iris/lab resolve.
- Titles and headings: no count of our own things in any title, H1, H2, lead or nav label (the headline "871 host endpoints" counts third-party endpoints we read).
- O2 (a failure is called a failure): the queue logs of the other done jobs hold no FAILED string (queue_s1-bbh-chat.log is the exception noted in D-27: errors but no FAILED, and it ended with "S1B DONE").
- L2 (no rate before the hand-check): the pages show no S1L figure, and I did not read the S1L files or log.
- L12 (same-family referees): no referee or labeller output of ours is presented on the 13 pages; the byline "by Bones, by hand" in the register is not printed.
- Core II (nets hiding flips): Falcon, Finalists and Models tables show per-cell outcomes with cannot tell kept as its own bin; no net rate stands in for a difference.
