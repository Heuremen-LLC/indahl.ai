# FIXLOG HEU1: heuremen.org HTML pages, 30 Oct 2026

Review: watch/site_pass_20261030/heu/HEU1.md. Bones had already done HEU1-2 (superseded copies, `_config.yml` excludes), and HEU1-23 (footer names) was left as decided. The PDFs, `ligera/` and `arxiv_one_readout/` were not touched. Nothing was shipped, committed, pushed or submitted to IBM, and no IBM API was called.

## What changed on disk

- **45 pages edited** under `/Users/heuremen/bones-forge/heuremen.org/` (`git status` in that repo lists them). `media.html` and `media/2026-10-26-heuremen-publishes.html` were left alone.
- **Run-folder files:**
  - `experiments/2026-10-22-hahn-t2/hahn_table.py` and `results_hahn_table.text` now cover 13 runs.
  - `experiments/readout-mitigation-check/README.text` was changed (HEU1-14).
- **New files:**
  - `experiments/2026-10-04-three-positions/verify_output.text`, the output of `python3 -I verify.py` in that folder, run locally with no network.
  - `fonts/*.woff2` (4 files), byte-identical (sha256) to `cloudflare-workers/heuremen-door/public/fonts/`, for the self-hosted correlations fonts.
- **Backups:** one per changed file at `/Users/heuremen/bones-forge/archive/heuremen_heu1_backups/<same path>.pre-heu1-20261030` (48 files: 45 pages and 3 run-folder files). Backups of files that ended unchanged were removed.
- **Helper agents:** four helper agents (Sonnet) did the style pass on the experiment pages that had no claim edits, following `heu1_fix/scratch/STYLE_BRIEF.md`.
  - I read every diff they made. I also corrected four wordings: control-run "With 10", pairs-run "is not removed", the deciding-runs claim duplicate, and the reach orphan sentence.
- **Checks after all edits:**
  - Visible-prose semicolons: 0 on every page.
  - `numdiff`: no reading lost. Every removed number is a cut clause, a renamed "Claim N", a Hahn range being replaced, or a token that only changed punctuation.
  - HTML is balanced on all pages.
  - `count_scan` over all heuremen.org pages, experiments included: 0 hits.
  - Every page that prints [lo, hi] or ± now states what they mean.

## Claims (step 1)

**HEU1-1, Hahn 13th run**
- *Page said:*
  - Hahn page: "Twelve runs on six processors." and "Marrakesh's fresh-record run waits for IBM to remeasure its T2 (as of 23 October)."
  - Front page: "twelve runs ... marrakesh 0.907 to 0.948 and 0.892 to 0.897 (two runs) ... 0.6 to 34.3 hours old".
- *Says now:*
  - The table has a marrakesh fresh-record row: 10-23 19:44, 0.5 h, 1.015 [0.937, 1.130] CONSISTENT (73 of 153 below) and 0.958 [0.902, 1.016] CONSISTENT (83 of 150 below), with job/props/raw links.
  - The section lead lists the six processors with no count.
  - The pooled bullet adds "Marrakesh's three runs ... 0.972 [0.929, 1.022] CONSISTENT (fixed fit), 0.889 [0.845, 0.936] BELOW (free fit)".
  - The rule bullet says marrakesh's fresh run "reads CONSISTENT under both fits ... so marrakesh does not meet the rule". "No chip meets it" still holds, so it stays.
  - Front page: "thirteen runs ... marrakesh 0.907 to 1.015 and 0.892 to 0.958 (three runs) ... 0.5 to 34.3 hours old".
- *Source:*
  - `experiments/2026-10-22-hahn-t2/results_hahn_table.text` lines 25-26 and 32 ("over the thirteen runs 0.120 (boston)").
  - `results_hahn_fresh_ibm_marrakesh.text` lines 2-7.
- *How the table was regenerated, without calling IBM:*
  - The 13-run `hahn_table.py` and its output already existed from 23 Oct 16:15-16:17: `arxiv_one_readout/hahn_t2/hahn_table.py` and `results_hahn_table.text.new`.
  - The script differs from the site's only by the added marrakesh_fresh run and "twelve" becoming "thirteen".
  - Its first 24 lines are byte-identical to the site's 12-run output.
  - Both files were copied into the site run folder.

**HEU1-3, correlations.html**
- *Page said:*
  - "+0.0012 ± 0.0024 at zero wait: nothing"
  - "bell last −0.0013 ± 0.0154. Fake #1: it was the order."
  - "χ² 19.4 on 20: no dependence at all"
  - "Fake #2: an unbalanced partner."
  - "Balanced reruns killed both"
  - "entanglement itself costs nothing extra ... loses the same coherence"
- *Says now:*
  - Row 1: "... (8 pairs): consistent with zero".
  - Row 3: "Cannot tell: the reversed arm reaches both 0 and +0.0124 within one standard error, so the effect was neither confirmed nor removed."
  - Row 4: "χ² 19.4 on 20 degrees of freedom: consistent with no phase dependence, within each pair's own fit error".
  - Row 5: "Balanced rerun −0.0014 ± 0.0026: consistent with zero. Not confirmed: the two runs differ by less than two standard errors, so the imbalance is not shown to be the cause."
  - The prediction record and "How this squares" are rewritten in the same terms: "no extra cost from entanglement itself that these runs resolve ... consistent with ... (+0.0012 ± 0.0024 ..., one standard error over 8 pairs)".
  - The note under the table defines ± as one standard error across pairs.
- *Source:* `experiments/2026-09-24-temporal-spatial-correlations/verify_september_output.text` lines 109-123, and `verify_september.py` lines 10 and 45-46 (SE = sd/sqrt(n) across pairs).
- *Derived checks:*
  - −0.0013 ± 0.0154 spans [−0.0167, +0.0141].
  - Row 5's two runs differ by 0.0062 against a combined SE of 0.0044.

**HEU1-4, correlations description**
- *Said:* "Superposition across time and entanglement across space are the same link. ..."
- *Says now* (description and og:description): "Correlation across time and correlation across space follow the same cosine on the same chip, measured on IBM quantum processors on 24 September 2026. The readings that did not hold are kept on the page."

**HEU1-5, sign convention**
- *Front page item 5 and technical summary section 1:*
  - Each now states that the 22 October runs print the kick as negative, so the difference (kick in 1 minus kick in 0) is positive when the kick in 1 is smaller.
  - Each also states that the 21 October excitation test prints the kick as positive, so there a positive difference means a larger kick in 1.
- *Echo paragraph* (front item 19 and section 1b): "This run prints the kick as negative ..."
- *Item 18:* "These runs print the kick as negative, as the 22 October runs do."
- *Further differences given their convention:*
  - Restart: "(kick size after 72 readouts minus after 72 idles, positive when the kick is larger)".
  - 8 minus 2: "printed with the kick negative so that a positive value means a smaller kick at 8", now attributed to "the control and raw-readout runs, pooled".
  - Next-minus-two-steps is now "kick size ... minus the size".
- *Source, checked each time:*
  - `2026-10-22-deciding-runs/results_excitation.text` (RJ.1 −1.522 / −2.967, RJ.3 +0.178 / +0.9226 ABOVE).
  - `2026-10-21-excitation-test/results_check_j.text` ("kick in 0 +3.023").
  - `2026-10-21-readout-vs-idle/results_kick.text` (+1.73).
  - `2026-10-22-dd-run/results_dd.text` (R1 −1.504).
  - `results_freshclock.text` lines 7-14 ("size = kick x sign").
  - `2026-10-21-control-run/results_check_i.text` (H1 size, H2 kick(8) − kick(2) signed).
  - `2026-10-07-equal-idle/summary_table.text` line 1 ("kick negative = same direction as 21-22 Oct").

**HEU1-6, front page item 9**
- *Said:* "... is excluded on all three in the first run and on kingston and marrakesh in the repeat."
- *Says now:* "... is excluded on kingston and marrakesh by the committed rule in both runs, and on fez only in the first run, by a copy-gap reading defined after the data."
- *Source:*
  - `2026-10-21-pairs-run/results_pairs.text` lines 24, 49 and 74.
  - `results_check_g.text` line 8.
  - `2026-10-22-pairs-repeat/results_pairs_repeat.text` lines 24, 49 and 74.

**HEU1-7, kingston readout-instruction repeats**
- *Length-run page:*
  - Added the section "Repeats on ibm_kingston and ibm_fez, 22 October, night", covering both kingston repeats and the fez repeat.
  - For each it gives the job, shots, ratio at 4 and 8 readouts with the outcome word as printed, the copy gap [+0.038, +0.441] that made repeat 1 CANNOT_TELL at 4, and the known-good value with its comparison to the control run's interval.
  - It links every file in `experiments/2026-10-22-length-repeat/`: plan, addendum, hashes, job records, raw, outputs, code and calibration.
  - The bare folder is not linked because it has no index, so the URL would 404.
  - The heading now reads "ibm_kingston, not decided in this run".
- *Front page item 2 and technical summary:*
  - *Said:* "on ibm_kingston, in repeats, the ratio is 0.95 ... and 0.98 ... (2000 shots)".
  - *Says now:* "the first run is not decided ... The first (1000 shots) reads 1.01 [0.81, 1.20] at 4 readouts, cannot tell because its copies disagree, and 1.01 [0.80, 1.37] at 8, per readout. The second (2000 shots) reads 0.95 [0.75, 1.17] and 0.98 [0.77, 1.28] ..."
- *Aligned pages:*
  - `what-we-measured.html` no longer says "kingston not decided". It now describes the not-decided first run, repeat 1 and repeat 2.
  - `experiments/2026-10-21-measurements/index.html` and `measured_qubit/` say "(fez and marrakesh, and kingston in a repeat)", the same as the front page.
- *Source:*
  - `2026-10-22-length-repeat/results_kingston_repeat.text` lines 3, 5, 7 and 9.
  - `results_kingston_r2.text` lines 5, 7 and 9.
  - `results_fez_r2.text` lines 5, 7 and 9.
  - `ADDENDUM_LENGTH_REPEAT2.md.text` (known-good rule, each run decides its processor, no pooling).
  - `2026-10-22-length-run/results_kingston.text` (first run, N=8 copies disagree).

**HEU1-8, what-we-measured**
- *Said:* "11.5 between copies in one run, shot noise alone (simulated scatter 2.9 to 4.2) is not claimed to account for it".
- *Says now:* "11.5 millionths of a second between copies in one run. Compared like with like, the range of three copies in a run is inside the simulated 95th percentile of shot noise alone in 8 of 9 runs. The simulation takes its noise scale from the copies themselves, so it cannot separate shot noise from drift between copies."
- *Source:* `2026-10-21-measurements/processors_apparatus/referee_controls.text` (marra 301: range 10.4 against p95 8.9, the other 8 inside).

**HEU1-9, cause named**
- *Front item 6:*
  - *Said:* "It comes from the readouts themselves:"
  - *Says now:* "A cause that does not depend on the number of qubits read out is excluded:"
- *what-we-measured:*
  - *Said:* "so it comes from the measurements themselves and not from something that happens whatever number is read"
  - *Says now:* "so a cause that does not depend on the number of qubits read out is excluded".
- *flip-check:*
  - *Said:* "Cause, found in the committed plan for run 2: ..."
  - *Says now:* "One cause, found ... Run 2 builds the floor like for like, and kingston's known-good check still fails there (+0.1541 and +0.1835 percentage points above the floor at N = 0 and 4), so this asymmetry accounts for part of run 1's failure at most."
- *flip-check-run2:*
  - *Said:* "failed ... because the floor and the idle arm were built from different shot sets"
  - *Says now:* "failed its known-good check on all three processors. One cause was found ... so that cause accounts for part of run 1's failure at most."
- *Source:* `2026-10-22-flip-check-run2/results_flip.text` lines 102-103.

**HEU1-14, readout-mitigation-check/README.text**
- *Said:* `Vendor rebuttal tested: "the effects ... go away."`
- *Says now:* "Rebuttal tested (our own statement of the strongest vendor rebuttal, not a quotation): the effects on untouched qubits are readout (assignment) error, and applying TREX, M3 or calibration-matrix inversion makes them go away."

**HEU1-15, "IBM charged" clauses: cut**
- *Cut on:*
  - control-run: "IBM charged 69, 71 and 68 seconds."
  - iq-run: "charging 20, 19 and 19 seconds"
  - pairs-run: "charging 35–37 seconds each"
- *Why:* No usage figure is saved in any run folder or job record (job_*.json and job-index hold no usage).
- *Only trace on disk:* the remaining-budget lines in `arxiv_one_readout/control_run/fire.log`, `fire_iq.log` and `fire_pairs.log`. These are not in the site folders.
  - control: 233→164→93→25 gives 69, 71, 68.
  - iq: 565→545→526→504 gives 20, 19, **22**. The page said 19 for fez.
  - pairs: 35, 35, 37, 37, 35, then the last reads 328→2293, which is unusable.
- If Bones wants the clauses back, publish those logs and give fez 22 on the iq page.

**HEU1-16, calibration-records/index.html**
- *Renumbered to the live bill* (`indahl-ai/qia_template/QIA-2026-001.json` record_notes):
  - Rows 3 and 4 became record notes 4 and 5.
  - Row 5 became note 6.
  - Row 6 became note 7.
  - "Record notes 2 to 4, 7 and 8" became "3 to 5, 8 and 9". The page notes that `record_notes.py`'s own header still uses an older numbering.
- *Note 6 now gives both outputs:* 2,655 entries over 9 pairs (`results_restamp.text`), plus 1,549 entries over 5 pairs of 22 and 23 October (`results_restamp_oct23.text`, TOTAL line). That makes "4,204 of 4,204 entries ... across 14 record pairs, 16 September to 23 October, the figure the audit prints".
- *Also:*
  - The lead links https://indahl.ai/quantum-idle-audit.pdf (HTTP 200 checked).
  - The cut description is completed.

**HEU1-17, fitted-rate cut**
- *October Campaign verify.py row and technical summary section 4 now state:*
  - The cut keeps untouched qubits with fitted rate above 4 deg/µs, 284 of the 524 readings.
  - Without it, all 524 give 1.0405 and one constant does not fit (χ²/dof 2.22, p = 0.038).
- The page also says that verify.py prints a reading defined after the data (dropping the 30 negative readings), which is not reported. Its number is not printed.
- *Source:* `experiments/2026-10-04-three-positions/verify_output.text` (new file, sections 5 and 6). The numbers are identical to `verify.py` run in the reviewer's scratch.

**HEU1-18, correlations caption**
- *Said:* "Replicated on ibm_kingston (pair 144-145, −0.813 vs −0.840 at π) and ibm_fez (−0.891 at π)."
- *Says now:*
  - Kingston space −0.813 on pair 144-145.
  - Pair 16-23 is excluded as a dead readout (length alone 1.355). Its space at π is −0.159, and the both-pair mean would be −0.486.
  - Kingston time −0.840 is the mean of qubits 1, 2 and 133 in the arrow run, not pair 144-145.
  - Fez −0.891 is the mean of pairs 22-23 (−0.950) and 81-82 (−0.832).
  - The caption links the verify output.
- *Arrow note:* clarified to "(fez at π: −0.925 forward, −0.919 backward)".
- *Source:* `verify_september_output.text` lines 39-41, 47-48 and 58.

**HEU1-19, readout audit and job index**
- *Readout audit page:*
  - Has a results list, one line per output file, with outcomes as printed: results_ro × 4 (fez, kingston, marrakesh, marrakesh repeat), results_iso × 3, and results_iso_vs_repeat.
  - Has links to the repeat plan, the addendum and the record files.
  - Its description is completed.
- *Inbound links:*
  - Front page Method links the job index ("Every IBM job and Rigetti task on our credentials, 24 September to 22 October: job index").
  - Front page Method also links calibration records. That page had no inbound link either.
  - The calibration-records page and the job-index page each link the readout audit.

**HEU1-22, direct-zz**
- *Said:* "The method reads IBM's zz directly where IBM's figure is right."
- *Says now:* "On fez the method reads back IBM's stated zz, which is what the known-good check asks of it."
- The 24 Sep data page title "data" is now "Data Files, 24 September 2026".

## Style (step 2)

**HEU1-10, what brackets and ± mean**
- One sentence was added to every page that prints [lo, hi] or ±, read from that page's own analysis code and plan. All 32 sentences are listed by the command at the end of this section.
- *Ones Bones may want to read:*
  - **index.html:** 95 % bootstrap over the units each reading is taken over, qubits, Bell pairs, coupled pairs or qubit triples (2000 draws, 4000 in the Hahn runs). Combined readings join processors by value and width. ± is the spread of three jobs (decay exponent, `cost/results.text:75`) and one shot-noise SE for Rigetti (`rigetti_extra/results.text:151`).
  - **technical-summary.html:** the same brackets. ± is a one-standard-error width per figure (X-train bootstrap width, `gate_trains/verify_xtrain.py:261`; fitted-rate SE, `verify.py`), with the named exceptions.
  - **hahn-t2:** 95 %, 4000-draw bootstrap over qubits (`hahn_pool.py:38`).
  - **direct-zz:** 95 %, 2000-draw bootstrap over triples, edge as unit (`PLAN_DIRECT.md.text:20`, `analyze_direct.py:9,61`).
  - **three-positions:** ± is the SE of the pooled value, from a 400-draw bootstrap width per processor combined by inverse variance (`verify.py`).
  - **correlations:** ± is one SE, from post-selected shots for the weak values and across pairs for the differences (`verify_september.py:46,119`).
  - **readout audit:** 95 %, 4000-draw bootstrap over qubits (`readout_audit.py:18-19`).
  - **what-we-measured:** "Square brackets give the 95 % range of a reading, found by resampling 2000 times the qubits it is a median over, and ± is one standard error from shot noise alone."
- **Open, for Bones's call:** flat-beat's "bracket by triple" is the outside referee's block bootstrap over triples (4000 draws, `REFEREE.md.text` section 5). Its level is not on disk, so the page states the method and draws only.
- To list every sentence: `grep -rho 'On this page[^<]*\|Square brackets[^<]*' /Users/heuremen/bones-forge/heuremen.org --include='*.html'`

**HEU1-11, semicolons removed per page** (visible prose; a second count in parentheses is for semicolons in meta descriptions):

| page | removed |
|---|---|
| technical-summary.html | 69 |
| index.html | 51 |
| experiments/2026-10-21-control-run | 44 (+2) |
| experiments/2026-10-22-deciding-runs | 33 |
| correlations.html | 16 |
| experiments/2026-10-07-equal-idle | 15 |
| what-we-measured.html | 15 |
| experiments/2026-10-22-direct-zz | 14 |
| experiments/2026-10-22-hahn-t2 | 13 |
| measurements/processors_apparatus | 12 |
| experiments/2026-10-21-readout-vs-idle | 12 |
| measurements/index | 11 |
| experiments/2026-10-21-superposition-entanglement | 11 |
| experiments/2026-10-22-one-neighbour-revival | 11 |
| experiments/2026-10-21-pairs-run | 10 |
| experiments/2026-10-21-iq-run | 9 |
| experiments/2026-10-22-flip-check-run2 | 9 |
| experiments/2026-10-22-three-box-run | 9 |
| measurements/cost | 8 (+2) |
| measurements/gate_cost | 8 |
| experiments/2026-10-22-length-run | 8 |
| experiments/job-index | 8 (+2) |
| measurements/measured_qubit | 7 (+2) |
| experiments/2026-10-21-excitation-test | 7 |
| experiments/2026-10-22-pairs-repeat | 7 |
| experiments/2026-10-22-reach-run | 7 |
| measurements/reach | 6 |
| measurements/rigetti_extra | 6 |
| experiments/2026-10-22-flip-check | 6 |
| experiments/2026-10-22-flat-beat | 5 |
| measurements/gate_nonexp | 4 |
| experiments/2026-10-21-entanglement-marrakesh | 4 |
| experiments/2026-10-04-three-positions | 3 (+2) |
| measurements/gate_trains | 3 |
| experiments/2026-10-22-kingston-claim4-repeat | 3 |
| measurements/processors_apparatus/recheck_20261022 | 2 |
| 24-sep index | 1 (+2) |
| experiments/2026-10-22-dd-run | 1 |
| calibration-records | 1 |

- **Total:** 469 in prose and 12 in meta descriptions. **Left:** 0.
- No number, interval or outcome word changed. Every case `numdiff.py` flags is accounted for at the top of this log.

**HEU1-12, counts moved out of titles, headings, leads and descriptions** (each count kept, unchanged, in a later body sentence):
- correlations h2 "The five that came back textbook" is now "What came back textbook".
- deciding-runs lead and description "Six readings" is now "Readings".
- job-index: lead and description (546/3035 moved to a second paragraph).
- October Campaign: lead and description (305/63/... moved to a second paragraph).
- equal-idle: "32 jobs".
- 24 Sep: "48 jobs that day".
- gate_trains: "13 jobs".
- cost: "three jobs / 14 jobs".
- flip-check h2 is now "failed on fez, kingston and marrakesh".
- measured_qubit: "Seven IBM processors".
- Also: control-run h2s "Two/Three ... checks"; readout-vs-idle and superposition "156-qubit"; dd-run, pairs-run, entanglement-marrakesh, reach-run and three-box leads; two control-run label bullets that count_scan flagged.
- **count_scan.py** still excludes /experiments/ from its gate list. Changing the gate is outside this agent's files. Run with experiments included, it now reads 0 hits.

**HEU1-13, Claim N:**
- kingston-claim4-repeat:
  - Title is now "Kingston Repeat: Kick in 1 Against Kick in 0".
  - h1 is now "Repeat on ibm_kingston: is the kick bigger with the measured qubits in 1? 22 October 2026".
  - The slug is kept.
- flip-check: "Claim 6" is now "The claim that readouts cost untouched qubits coherence".
- pairs-repeat: "Claim 7" is now "The claim that readouts cost untouched Bell pairs entanglement".
- deciding-runs: "(claim 4; ..." is now "(plan ...", because the bold label already states the claim.

**HEU1-20, descriptions:**
- Every cut description and og:description is now one or two complete sentences, with the two copies identical.
- what-we-measured.html and technical-summary.html each have their own description.
- The restamp_check and calibration subpages replaced link-list or bare-name descriptions.

**HEU1-21, layout and fonts:**
- *Tables wrapped in `overflow-x:auto`:*
  - equal-idle, excitation-test, superposition-entanglement (the three named).
  - readout-vs-idle (3 tables).
  - measurements index.
- *Viewport meta added:* technical-summary, three-positions, 24 Sep data, calibration-records ibm_fez, ibm_kingston, ibm_marrakesh and restamp_check.
- *correlations.html fonts:*
  - The Google Fonts link is replaced by inline `@font-face` rules pointing at `/fonts/*.woff2`. These are the 27 Oct indahl.ai files (Lora, Abril Fatface, Cinzel), copied into `heuremen.org/fonts/`.
  - They had to be copied because indahl.ai sends no CORS header, so heuremen.org cannot load them from there.
  - No page loads Google Fonts now.

## Not fixed, or needs Bones

- **HEU1-15:** cut, not sourced (see above). The iq-run fez charge on disk reads 22, not the page's 19.
- **HEU1-10 flat-beat:** the triple-bootstrap level is not on disk.
- **HEU1-12:** `heuremen-specbook/count_scan.py` still skips /experiments/. That is a gate change for Bones.
- **arxiv_one_readout/hahn_t2/results_hahn_table.text:** the paper source copy still holds 12 runs. The 13-run output sits beside it as `.text.new`. Not touched, per the brief.
- **Shipping:** `public_mirror/heuremen.org` and the live site follow only through `ledger/ship.sh`. The new files (`fonts/`, `verify_output.text`) must ship with the pages.
- **Ledger:** 18 drift lines are open (16 MISSING + 2 SOURCE). `LEDGER_TODO_HEU1.md` closes all of them (rehearsed to drift 0 on a copy) and adds rows for every new number this pass printed.

## Last lines of the gates (live tree, before the ledger TODO is run)

- `python3 ledger/check_ledger.py`: `ledger: 2397 rows (2358 live); drift: 18` (all 18 are this pass's changed snippets and the two source greps, listed in LEDGER_TODO_HEU1.md)
- On the rehearsal copy after the TODO: `ledger: 2436 rows (2397 live); drift: 0`
- `python3 heuremen-specbook/site_gate.py`: `site gate: 103 pages, 794 served files read for wording; breaches: 0`
