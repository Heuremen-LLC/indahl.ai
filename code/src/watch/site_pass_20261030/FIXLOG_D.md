# FIXLOG lane D (IRIS), site pass 30 Oct 2026

Nothing is built, shipped or deployed. Source files are changed, the lane generators were run (judge_counts.py, training_counts.py, iris_list.py, build_iris_page.py), and the changed pages were checked on a preview render made by importing build_site.py into the scratchpad (no site files written, ledger snippets checked against it with check_ledger.norm). Backups: <file>.pre-sitepass-20261030 beside every file I edited (build_site.py's backup was made earlier by another agent).

Files for Bones: LEDGER_TODO_D.md (run before ship), BOOK_TODO_D.md (register edits for D-7, D-11, D-18), iris_index/judge_counts/tag_audit_20261030.txt (evidence file for the D-1 withdrawals).

## Needs Bones first
1. D-7 is a wrong claim on the live List: BOOK_TODO_D.md, field `priced` of 2610.18610.
2. LEDGER_TODO_D.md: two withdrawals (iris.judge.multi, iris.judge.differ), five adds, 36 off/on snippet swaps (8 top-table rows, 7 study rows, 8 Finalists rows, 12 Falcon rows optional, 1 training row).
3. Outside my area, stale copies that still carry old content: hf_indahl/build.py line 58 and hf_indahl/stage/iris-judge-counts (README says "how often a judge model repeats itself on the same item", old judge_counts.py and summary.json), hf_indahl stage for iris-training-runs (summary.json has new by_period keys), ~/bones-forge/public_mirror/indahl.ai/code/iris/select_finalists.py (still the old exclusion rule), and pub2 main.tex lines 60 to 61 (same "9,600 records" and "8,000 position items" units as D-11).
4. Static files changed that need a deploy: public/iris/bench.js, train.js, list.json (iris_list.py copied it).

## Per finding

D-1 fixed. judge_counts.py: the log has no item id (verdict lines carry only a tag in parentheses, the one other line type with a uuid is "FAILED, leaving in queue"), so `items_judged_more_than_once`, `of_those_with_differing_verdicts`, `differing_share_pct` and `distinct_items` are dropped, and `verdicts_under_adapter_names` (1,240 of 1,779) added. Re-ran it: verdicts 1,779, hold 1,028, discard 623, keep 128 unchanged. Verified by recount into tag_audit_20261030.txt: 374 tags = 2 adapter names (1,240 verdicts), 16 one-character buckets (177), 175 three-character labels (181 verdicts, 6 repeated, about 4 expected), 181 unique. build_site.py IRIS_JUDGE: two rows dropped, row "Verdicts logged under the two names of our own adapter" 1,240 added, one sentence says the log tags verdicts by adapter name or short label, not item id. KEY L7: the last sentence removed whole (read literally, so the held-on-57.8% clause went with it, the hold share is still in the IRIS_JUDGE table). Ledger withdrawals in LEDGER_TODO_D.md. No other live ledger row carries those numbers.

D-2 fixed. Verified: select_finalists.py as run gives smollm2:1.7b 0.058, qwen3:4b 0.167, olmo2:7b 0.210. Strict rule gives smollm2:1.7b 0.058, olmo2:7b 0.224, qwen3:4b no score (feed: 0 readable of 44 family-rounds, 23 control failed, 21 too few read). Line 19 now excludes every CANNOT_TELL (it sits at line 21 with a dated comment), re-ran it read-only: finalists now smollm2:1.7b and olmo2:7b. THUNDERDOME_PLAN.md: dated "ADDENDUM 3 (30 Oct 2026, site pass, correction)" appended, arena not re-run. IRIS_THUNDER lead sentence now says what was computed and what the written rule gives.

D-3 fixed. Verified mcq4_rev_acc_change for the four models (each interval holds zero, bounds 8.1 to 10.9). Headline now: "Reverse the order of the options and 27% to 50% of the answers change. The score change is consistent with zero for the four models read, with intervals that reach 8 to 11 points on one side." build_site.py's headline data-line insertion is now pattern based (the old exact-string replace would have silently dropped the data line).

D-4 fixed (verified against MATRIX.md and the omitted rows). Third column relabelled "Two-option flips under option reversal, including letter fallback". Added a note under the table: five of ten models shown, NepPlural and Jev-ToM named, the none rule stated after the replies were seen, gemma3 prompt-or-format caveat, falcon3:3b higher false none and smollm2:1.7b and olmo2:7b higher over-attribution among the models not shown. Second headline now starts "Among the five models shown" (the omitted rows are further out, so the old headline read as if gemma3 and qwen3 were the extremes).

D-5 fixed. Verified from terminations and the n in mcq4_B_flip_minus_floor: 27, 20, 51, 142, 183, 191, 195, 200 of 200. Cell prints "k of 200 items". More than 10 percent unread is cannot tell, so falcon3:3b, smollm2:1.7b, granite3.3:2b and phi4-mini no longer show a rate. This is a page-level rule (the plan's 10 percent convention), the data JSON outcomes are unchanged. Header "Answers that changed, answer format changed". KEY L2 now lists the four kept values and says why the others are cannot tell.

D-6 fixed. The repeat column is now k of n with a Wilson interval (0 of 199 gives 0.0% [0.0, 1.9], falcon3:3b 1 of 195 gives [0.1, 2.8]). Header "(determinism check)". KEY L3 names the Mac server and says determinism check, not noise floor.

D-7 needs Bones (register field, BOOK_TODO_D.md). Evidence verified: RESULT.md and reversal_out.text confirm the reversal (69.08 vs 70.87, -1.79 [-3.54, -0.19]), the register's own referee field says CONFIRMED.

D-8 fixed. KEY L5 and SHOW['2610.30512'] describe the split, say it does not name a cause, and add the margin reading (+8.0 [+0.7, +15.3], defined after the data).

D-9 fixed. KEY L1 now has two sentences: ours is "net of the exact repeat", the judges' figures are "a different measure, from an earlier experiment, run once per judge with no repeat floor" with a link to the frontier data zip, and the pinned October GPT-4.1 figure +12.5 [8.0, 16.7] above its floor. SHOW['2610.30512'] says "no repeat floor, run once per judge".

D-10 fixed. judge_counts.py adds rounds_with_three_asks 6,347 and rounds_by_asks_made (0: 4,634, 1: 52, 2: 24, 3: 6,347, sums to 11,057 rounds and 19,141 asks). IRIS_JUDGE row relabelled "rounds logged" plus a row "Rounds in which three models were asked".

D-11 fixed on the page (SHOW and KEY L3: "8,000 of 8,000 question-position cells identical", "76 of 8,000 cells (0.95%) change, A40 against A10G", primacy gap +0.0019 [-0.0050, +0.0088] consistent with zero). Verified against recount.py line 37 and recount_out.text (n 800 questions x 10 positions, agreement 1.0000 and 0.9905, 76 derived). Register `priced` is in BOOK_TODO_D.md.

D-12 fixed. SHOW['2610.25159'] and KEY L7 say the gold was built by reviewing that labeller's output, so the lead cannot be separated from anchoring.

D-13 fixed. SHOW['2610.25626']: resolves in 2 of 18 settings, uncorrected for 18 tests, consistent with zero in 15, behind in 1, Welch interval three seeds against three, lower bounds +0.03 and +0.06, "The authors' 12 of 18 is a correct count of means." Sentence order chosen so the meta description keeps the caveat.

D-14 fixed. SHOW['2610.21468'] and KEY L7 print both contrasts (G1 vs G2 0.657 [0.486, 0.800] n 35 consistent with chance, G1 vs G0 0.839 [0.710, 0.968] n 31 above chance).

D-15 fixed. IRIS_FALCON paragraph says one training run per model, one seed, and that a second seed and two further evaluation sets have been run and are not on the page yet. The note says the mixed-label model is a control trained on partly wrong labels and that against the untouched model no family shows a gain (verified from the ledger rows: cannot tell, cannot tell, cannot tell, no gain). train.js finished text now reads "(status last checked 30 Oct 01:57 UTC)". Verified: 600-step training seed 20280007 vs seed 20290007 in train_config_s2.yaml, queue shows falcon-r2-evals and falcon-seed2 done.

D-16 fixed. bench.js: the round grids print "n read" after each rate and the reason under a cannot-tell cell, the Models index names the reasons per cell ("family control failed in 8, too few read in 3"), the note says cannot tell also means fewer than 10 replies could be read. Verified in a browser against the live feeds (no errors from bench.js or train.js, counts match the feed: qwen3:4b 23 control failed and 21 too few read, 63 too-few-read cells overall). falcon_results_page.py now prints "Replies read: A k of n, B k of n" under each Falcon cell (the ledger snippet is still the start of the cell text) and writes "read ..." source lines into falcon_results.txt. Because that script adds ledger rows when run, I did not run it. I ran its first half in the scratchpad (output first checked byte equal to the current html and txt), then copied the new html and txt in. The note no longer points to an unlinked "replies file".

D-17 fixed with the sentence option. thunder_results.html note now says only the plain-prompt arm is shown and the Guard arm reading is not, says the scorer plan was amended 11 times (addenda 3 to 11, nine of them after rates had been computed, finalists chosen on the rescored rounds) with a link to the dataset that holds PLAN_v2.md, and gives the qwen3:4b P2 cut-off (28 of 30 in round 12, none in round 13, cause not found). IRIS_THUNDER says the plan was committed on 27 October before any round was read (verified: commit ac4fd66 27 Oct 09:33, round 1 rates first computed 11:53). A guard-arm column was not built, that would need a new scoring pass and new ledger rows. THUNDERDOME_PLAN.md addendum 3 point 3 corrects addendum 1's "28 of 30 P2 and 29 of 30 P4" (they are two rounds). Verified from the reply files.

D-18 needs Bones (BOOK_TODO_D.md). All three quotes checked against the papers. The IndoNutriQA clause contains a semicolon, so the proposal drops the quotation marks, the other two use the paper's own words.

D-19 fixed. build_site.py `_snip()`: last sentence end within 150 characters, else the first sentence end within 200, else a word cut that is never inside a bracket. All nine study descriptions read as complete sentences on the preview. Deviation from the finding: the 200 cap for a first sentence longer than 150.

D-20 fixed. HEAD_INTRO and HEAD_NOTE are now in the body with the facts verified in run_matrix_v2.py, PLAN_v2.md and score_matrix_v2.py: 200 four-option items from the Jev-ToM release, Ollama on our Mac server, temperature 0, seed 20261025, num_ctx 4096, num_predict 500, and "the server's JSON mode was not used" (the finding listed JSON mode, PLAN_v2 addendum v2-1 says the opposite). Defines each column, the first-option check (80 percent of 40 items, both orders), cannot tell, interval level. Column renamed "Score on the original order".

D-21 fixed. Interval level stated: under the top table, under the Key header, on every study page (Welch on the 25626 page), on the List, in the bench.js note, in the Falcon note and the Finalists note.

D-22 fixed on the pages. List: iris_list.py turns "; " into a full stop in `recount` and `priced`, so I did not need to edit the register for this (the register still holds the semicolons). Finalists: one line per round. Software line: now joined with commas. That join is in the shared `_codeline` function, so it also applies to every other page that has a software line (qia, model, hfsize, pkginstall, coin). Preview: 0 semicolons in the visible text of /iris, /iris/lab, /iris/key, /iris/list and the 9 study pages.

D-23 fixed. Data line is a link, "1 output file", thousands separators ("5,037 output files"). list.json regenerated and copied.

D-24 fixed. The first paragraph of IRIS_FG removed. The Faults and Guards PDF links stay.

D-25 fixed. SHOW['2610.25964'] and KEY L6 name LLaVA-1.5-7B at 4-bit precision, the authors' five-of-six claim against our four-below, one-inside, one-above count and "unresolved until readout and precision are matched". SHOW['2610.17203'] and KEY L6 define the planned rule (share of 16 picks per item) and the rule under which 74.5 rebuilds (more-picked answer, found after the data).

D-26 fixed. training_counts.py splits the 99 sessions at the 26 August fix (adapter folder last written after that date, cross-checked by median "Val took" of 40 s or more, 0 of 99 disagree): before 90 sessions (36 improved, 85 with the lowest loss before the last check), after 9 (0 and 7). Pooled totals are unchanged. IRIS_TRAIN has four rows in place of the two pooled rows and a sentence saying the before-fix rows do not show how training went.

D-27 partly fixed. iris_queue.py: PATH set in the Popen environment (/opt/homebrew/bin first), and the public feed names jobs by kind ("A model-claims round", "A Faults and Guards round", "A training round") with an empty plan path unless the job id is in the new ON_A_PAGE set (empty now, none of the S rounds is on a page). Checked with a dry run of the new status() on queue.json (no job started, stopped or requeued, queue.json not touched, py_compile clean). Not changed: liveness by completed work. A job's "running" state decides when the next job may start, and there is no generic per-job completion marker, so that is a scheduling change, not a small one. Logged here for a decision.

D-28 partly fixed. lm-evaluation-harness dropped from the /iris software line, and a software line (Ollama, MLX LM, MLX, faultsguards) added to /iris/lab. The finding did not fully hold: /iris has the "Our own fine-tuning runs" section, whose numbers come from MLX LM training logs, so MLX LM and MLX stay on /iris.

## Other
- build_site.py edits are only in IRIS_JUDGE, IRIS_THUNDER, IRIS_FALCON, IRIS_FG, IRIS_TRAIN, the headline data-line insertion, the IRIS study loop (`_snip`, `_desc`, one interval sentence in the study-page footer), `_SWMAP['iris']`, and the software-line code (`_swline`, `_codeline`, one lab line after the replies loop). Each file compiles.
- The Falcon "replies read" swaps (12, optional) and the r2 swaps keep source.grep targets valid. check_ledger.py shows only the two expected SOURCE drifts for iris.judge.multi and iris.judge.differ (cleared by the withdrawals).
- Scripts run: judge_counts.py and training_counts.py (rewrote their summary.json), iris_list.py (rewrote iris_list.json, iris_list_body.html and the public list.json), build_iris_page.py (rewrote iris_body.html, iris_key_body.html, staged/), select_finalists.py (read-only, before and after). Not run: falcon_results_page.py, ledger.py, build_site.py main, any ship step.
