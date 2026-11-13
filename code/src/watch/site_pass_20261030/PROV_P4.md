# PROV lane P4, 30 Oct 2026 (34 rows, read only, evidence only)

Rows: /Users/heuremen/bones-forge/watch/site_pass_20261030/prov_lane4.json. Cells read from /Users/heuremen/bones-forge/qia_leads/matrix_page/book_calibrated.json.
Result: 23 KEEP, 11 FIX, 0 PULL.

Conventions
- Paths are relative to /Users/heuremen/bones-forge/ unless they start with /.
- AU = qia_leads/audits, RP = qia_leads/recheck_published/src (cached paper or record text), SW = arxiv_one_readout/sweep_run, CR = arxiv_one_readout/control_run.
- Scratch = /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p4 (authors' downloads under data/, my scripts at top level and in tcg/). Their data was read with python3 -I. None of their code was run.
- A number counts as traced only when it sits in the row's own material. THE_BOOK.md, the ledger and book_calibrated.json were used only to find rows.
- Every "grep:" string below was checked with `grep -a -F` against its file (34 of 34 hit). Six cached texts contain non-UTF-8 bytes, so plain grep calls them binary. Those rows are marked "(grep -a)".
- No IBM or other paid call was made or needed. Every IBM record used here is already on disk.

## Summary

| # | row id | verdict | what to do |
|---|---|---|---|
| 1 | fresh_fandaqah_2609.06448 | KEEP | none. The q53 gap sets were recounted from the authors' repo |
| 2 | recount_2511.20741 | KEEP | none |
| 3 | ibm_ncpp | KEEP | none |
| 4 | ibm_spacetime_detect | FIX | "resolved rows" covers bare fidelities only 1.3 and 1.7 SE from zero. Reword |
| 5 | ibm_spacetime_logical | FIX | "PEC at d = 6 not run" is wrong (it ran and did not converge). The paper prints 3.7x, not 3.6x |
| 6 | marrakesh_mis | KEEP | none |
| 7 | ibm_fugaku_closedloop | FIX | "last row time-capped" is not stated. The 0.090 vs 0.08 item was struck in the audit's own final |
| 8 | readout_dominated | KEEP | none |
| 9 | free_2503.17833 | FIX | the calibration asks for "one device family", but the paper says two versions were used. Ask for dates |
| 10 | mitsubishi_keio_2609.39693 | KEEP | none. first_mae_below_0p1 was recounted from their repo |
| 11 | recount_2511.09322 | FIX | "Print the widths": the widths are printed. The paper never says what the ± is |
| 12 | recount_2509.26229 | KEEP | none |
| 13 | riken_2610.09532 | KEEP | optional: the equal-CZ evidence is one setting (H2O, M = 2) |
| 14 | recount_10.5281/zenodo.23108790 | KEEP | none |
| 15 | recount_2607.27777 | KEEP | none. Note for Bones: their text says "within ~0.01 mHa" but Table IV goes up to 0.465 mHa |
| 16 | uchicago_ibm_backaction | KEEP | optional: the How cell reads as if the authors released kick data |
| 17 | vanguard_portfolio | KEEP | none |
| 18 | workday_2609.38713 | FIX | the match pairs each depth with a different shot convention. Reword as a range |
| 19 | recount_10.5281/zenodo.22644883 | FIX | 10 rows, not 9. The remainders are the 23 misses that the totals line states |
| 20 | recount_10.5281/zenodo.21199323 | KEEP | none |
| 21 | bas_sofia_grover | FIX | the calibration asks them to state dates and versions they already print. Ask them to correct the date |
| 22 | cern_bern_lmu_marrakesh | FIX | 5.0 mixes the 21 Oct stated median with a factor taken against the 23 Oct record. On one record it is 4.3 |
| 23 | recount_10.5281/zenodo.20026696 | KEEP | none |
| 24 | cuhk_mcm | KEEP | optional: same How-cell wording as row 16 |
| 25 | free_2509.19448 | FIX | "Sec 2.4" should be Sec. 2.3 (both arXiv versions) |
| 26 | fez_carbon_credit | FIX | "check the index alignment" has no support on disk. Drop it |
| 27 | free_2512.03341 | KEEP | none |
| 28 | hanyang_2610.14778 | KEEP | optional: 6.7% is their print. Their own values give 6.79% |
| 29 | lane_hebrew_2506.11270 | KEEP | none |
| 30 | iisc_depth_model | KEEP | none |
| 31 | iu_lbnl_2610.18482 | KEEP | none |
| 32 | tcg_oist_marrakesh | KEEP | none. Both counts recounted here (Bones's final had accepted them unrecounted) |
| 33 | bl_2605.13109 | KEEP | none |
| 34 | lviv_2610.06127 | KEEP | none |

Replacement text for FIX rows is in each block, on lines starting "Suggested".

---

## 1. fresh_fandaqah_2609.06448 : KEEP
- 8 arms reproduce: TRACED in AU/fresh_fandaqah_2609.06448/src/l3_repro_out.txt lines 2-5 and 10-13 (4 arms x 2 acquisitions, ours = printed to 4 decimals).
- 0.2540 / 0.2114: TRACED in the same file, lines 7 and 15.
- q53 exponents come from different gap sets on different days: RECOUNTED from the authors' released files (github Mirza-Samad-Ahmed-Baig/quantum-phase-cycled-rb, data/survey_ibm_fez_20260729T170154Z_offset_results.json and data/survey_ibm_fez_20260730T095356Z_confirm_results.json, copies in Scratch/data/fandaqah). Offset run: deltas_ns [8, 20, 40, 80, 200, 640], nu_offset 1.8647 ± 0.2168. Confirm run: [8, 40, 200, 640], 1.2591 ± 0.1409. The stamps are 29 Jul 17:01Z and 30 Jul 09:53Z. Also in AU/fresh_fandaqah_2609.06448/KNOWN_GOOD.md line 36.
- Cannot tell selection from drift: KNOWN_GOOD.md section 3 (CANNOT_TELL).
- source: qia_leads/audits/fresh_fandaqah_2609.06448/src/l3_repro_out.txt; qia_leads/audits/fresh_fandaqah_2609.06448/KNOWN_GOOD.md
- grep: `est ours 0.2540 printed 0.2540`

## 2. recount_2511.20741 : KEEP
- n = 3: TRACED in RP/recount_2511.20741.txt lines 20, 125, 420, 473 and 529.
- The authors call the numbers non-inferential: lines 24, 420, 473 and 529.
- Point estimates: lines 21, 498 and 527.
- source: qia_leads/recheck_published/src/recount_2511.20741.txt
- grep: `non-inferential (n= 3)` (grep -a)

## 3. ibm_ncpp : KEEP
- Published quote: AU/ibm_ncpp_2606_20441/src/paper.txt lines 554-556 (also RP/ibm_ncpp.txt line 470).
- Quartic, not quadratic: RECOMPUTED. PNA^2 ∝ PEC^(1/2) gives PEC ∝ PNA^4, while the same sentence calls it the expected quadratic speedup (PEC ∝ PNA^2). Also in AUDIT.md lines 60 and 98.
- The noise model is their own learned model: TRACED in paper.txt lines 494-497 (the noise-learning workload, 12.7 min, provides the noise model PNA uses).
- The learned model, counts and run dates are not public: AUDIT.md lines 47 and 68.
- source: qia_leads/audits/ibm_ncpp_2606_20441/src/paper.txt; qia_leads/audits/ibm_ncpp_2606_20441/AUDIT.md
- grep: `pling cost roughly tracks the square root of the PEC` (grep -a)

## 4. ibm_spacetime_detect : FIX (wording)
- Largest of 7 rows, 236x: TRACED in Table 1 of AU/ibm_spacetime_236x/src/paper_arxiv_html.txt (gains 2, 4, 13, 109, 83, 104, 236, all on ibm_kingston). RECOUNTED from the authors' repo pickles in AU/ibm_spacetime_236x/recompute_gains_output.txt (gain=236.0 for the 250405 custom50c file). The run date 5 Apr 2025 comes from the 250405 file stamp.
- 0.060 ± 0.049 and 2.5e-4 ± 7.1e-4: TRACED in AU/ibm_spacetime_236x/recompute_uncertainty_output.txt line 7 and AUDIT.md line 48. These SEMs are our own computation, using the repo's own error formula (src/an4.py line 8, the formula behind the Fig. 4 shading). The paper prints no value for them.
- Not bounded: TRACED, P(F0 ≤ 0) = 0.36 on the same line.
- 83-109x: TRACED in recompute_gains_output.txt lines 4-6 (109.5 at n=32, 83.1 at n=38, 104.3 at n=44).
- Problem: "The resolved rows give 83–109x". In those three rows the bare fidelity sits 1.3 (n=32), 2.8 (n=38) and 1.7 (n=44) standard errors from zero, with P(F0 ≤ 0) of 0.10 and 0.05 at n=32 and n=44 (recompute_uncertainty_output.txt lines 4-6). Only n=38 clears two standard errors. The well-resolved rows are n=14 to 26 (16 to 86 SE), and they give 2x to 13x.
- Suggested measured: "The largest of 7 rows. At n = 50 the bare fidelity 2.5e-4 is 0.4 standard errors from zero. The next rows (n = 32 to 44, bare fidelity 1.3 to 2.8 standard errors above zero) give 83–109x."
- Suggested calibration: change "With the authors' own standard errors" to "With standard errors from the authors' own formula (the one behind Fig. 4)". The rest stands.
- source: qia_leads/audits/ibm_spacetime_236x/AUDIT.md; qia_leads/audits/ibm_spacetime_236x/recompute_uncertainty_output.txt; qia_leads/audits/ibm_spacetime_236x/recompute_gains_output.txt
- grep: `2.54e-4 +/- 7.1e-4 (0.4)`

## 5. ibm_spacetime_logical : FIX
- 3.6 / 15.9 / 63: RECOMPUTED from Table 1 in AU/ibm_stlog_2609_13108/recompute_printed_output.txt lines 2-4: 44.1/12.1 = 3.645, 1941/122 = 15.91, 85545/1359 = 62.95. The paper prints 3.7x (src/paper.txt lines 129 and 144). 3.7 is inside the rounding of its own inputs (3.626 to 3.664). The cell writes 3.6 as if it were their ratio, and then asks them to state 3.6.
- Model-inferred: TRACED (the abstract says "inferred sampling overhead"; AUDIT.md lines 11 and 44).
- No interval: TRACED. Table 1 has none (AUDIT.md line 21).
- "PEC at d = 6 not run": WRONG. paper.txt line 127 says standalone PEC at d = 6 deviates strongly from the ideal value, with much larger uncertainty. Table 4 (line 591) lists PEC and ED+PEC at d = 6 with 40,000 randomizations x 160 shots. PEC also ran at d = 4 and did not converge (line 128). What was never realised is the 85,545 overhead, which is inferred. The audit's wording was "PEC baseline not realised" (AUDIT.md lines 44 and 95); the cell shortened it to "not run". The cell's own calibration then budgets a repeat of "each d = 6 arm".
- 3.5 kHz: TRACED in paper.txt line 590. Table 4 gives 3571 / 3560 / 3544 Hz.
- 3.2e3 s: RECOMPUTED, 3 x 3.7e6 / 3500 = 3171 s. Note that 3.7e6 is the whole Clifford-test budget per layout (Table 3, paper.txt lines 535-570). It includes 150,000 target-stabilizer shots, and there are two layouts (reference and checked). Learning-only shots per layout come to 3.55e6, or 3.0e3 s for three repeats. That is inside the cell's "about".
- 3.6e3 s: RECOMPUTED, 2 x 6.4e6 / 3544 = 3612 s. Total 6,783 s, which rounds to 6.8e3. The ibm_aachen device and the unstated Ising learning budget are TRACED (paper D.1; AUDIT.md lines 70 and 77).
- Suggested measured: "The deepest of three model-inferred ratios (3.7 / 15.9 / 63 as printed). Standalone PEC ran at d = 6 but did not converge, so its 85,545 overhead is inferred, not reached. No interval."
- Suggested calibration (first sentence): State "inferred overhead reduction 3.7x / 15.9x / 63x at d = 2 / 4 / 6 (model-inferred; standalone PEC at d = 6 did not converge)". The rest stands.
- source: qia_leads/audits/ibm_stlog_2609_13108/recompute_printed_output.txt; qia_leads/audits/ibm_stlog_2609_13108/src/paper.txt
- grep: `d=6: 85545/1359 = 62.947`

## 6. marrakesh_mis : KEEP
- Certified size 15, exact solve 0.6 s: TRACED in AU/ibm_mis_2606.28866/out/mis_180.txt line 2 (size=15, proven_optimal=True, time=0.6s).
- About 60% of 20,000-sample blocks: TRACED in out/dumb_180_hits.txt (24 of 40 blocks = 60%). Bones's fresh seeds gave 3 of 5 (AUDIT.md line 84).
- Seconds on one core: 25.7 s for 40 blocks (0.64 s per block), in single-thread Python (src/dumb_180_hits.py).
- "stall at size 14": TRACED in src/paper.txt line 31.
- source: qia_leads/audits/ibm_mis_2606.28866/out/dumb_180_hits.txt; qia_leads/audits/ibm_mis_2606.28866/out/mis_180.txt
- grep: `blocks with >=1 size-15 set: 24`

## 7. ibm_fugaku_closedloop : FIX (wording)
- 20-25x: TRACED in AU/ibm_riken_fugaku_2511_00224/src/paper.txt lines 1120-1123.
- 33.8x and 25.3x: RECOMPUTED as node-minutes from Table I (paper.txt lines 1052-1083). 384 x 2 = 768, 5,184 x 5 = 25,920 and 65,536 x 10 = 655,360 give ratios of 33.75 and 25.28. Also in src/arith.out.
- "the last row time-capped": NOT FOUND as stated. The paper says runs stop either at the target accuracy or at the predefined maximum wall-clock time (lines 1088-1090), and that some stopped at the limit (line 1097). It does not say which runs. Bones's final reads "10^10 may be time-capped" (AUDIT.md line 114).
- 0.090 Eh: RECOMPUTED, −5049.127 − (−5049.217) = 0.090 (arith.out line 4). But the audit's BONES FINAL struck this item (AUDIT.md line 113), because "about 0.08" sits inside the paper's own ±0.02. The calibration cell still carries it.
- Node and walker accounting: TRACED, and re-checked here because Bones's final said "not re-checked". p.7 line 999 has 2 walkers and 76,032 nodes per walker. p.8 line 1117 has 76,032 nodes with two walkers in total. For 10^9, the text gives B = 256 and 16,384 nodes (lines 1103-1111), while Table I gives B = 64 and 65,536 nodes. For 10^10, the text gives M = 11 and Table I gives M = 22.
- Layer-fidelity, SPAM values and run dates are not published: AUDIT.md lines 38, 45 and 57.
- Suggested measured: "Table I node-minutes give 33.8x and 25.3x per decade. The last step (3.5x to 4.6x) is not a test, since runs stop at a wall-clock limit and the paper does not say which did."
- Suggested calibration: drop the sentence "Print the [2Fe-2S] gap from the quoted energies (0.090 Eh, not about 0.08)." The audit's own final struck it as inside ±0.02; keep it only if Bones overrules that. The rest stands.
- source: qia_leads/audits/ibm_riken_fugaku_2511_00224/src/arith.out; qia_leads/audits/ibm_riken_fugaku_2511_00224/src/paper.txt
- grep: `1e8/1e7 = 33.8 ; 1e9/1e8 = 25.3`

## 8. readout_dominated : KEEP
- 16: TRACED in AU/sigdel_porthamnn_2607.12269/src/paper.txt lines 1021-1022. From the pair's own values it is 16.17 (out/proj_readout_gate.txt line 4).
- 10: RECOMPUTED in out/proj_readout_gate.txt line 7. With CZ x1.616 the error-probability ratio is 10.0 (15.0 on the observable basis).
- CZ factor 1.616 (RB, 23 Oct 2026): TRACED in SW/results_sweep_3.text line 33. The chip is ibm_marrakesh (paper line 877).
- Note: this is a chip-level factor applied to one pair (135-139), 74 days after their calibration read. The How cell already labels it a projection.
- source: qia_leads/audits/sigdel_porthamnn_2607.12269/out/proj_readout_gate.txt; arxiv_one_readout/sweep_run/results_sweep_3.text
- grep: `CZ x1.616: ratio(error-prob basis) 10.0`

## 9. free_2503.17833 : FIX (calibration wording)
- Both quotes are TRACED in RP/free_2503.17833.txt. The main text names the Eagle devices ibm kawasaki and ibm kyiv (lines 410-411). The Fig. 6 caption names the Heron version (lines 645-646), and App. C does too (line 587).
- Problem: the paper says outright that the Fig. 6 timing ran on the Heron version, "not the Eagle version in the main text". It names two hardware generations for two different experiments and does not mix them up. "Name one device family for ibm_kawasaki" asks for something that would be false if both versions were used. What is missing is run dates: there are none anywhere in the text (searched).
- Suggested calibration: "F6 Date each run, so the Eagle-era and Heron-era ibm_kawasaki records can be told apart." The measured cell stands.
- source: qia_leads/recheck_published/src/free_2503.17833.txt
- grep: `the latest Heron version of theibm kawasakidevice` (grep -a)

## 10. mitsubishi_keio_2609.39693 : KEEP
- 0.09945: TRACED in AU/mitsubishi_keio_2609.39693/out/analysis7.json line 2. Also RECOUNTED from the authors' repo file data/annulene/hybrid/summary.json (sk888ks/macrocycle_dynamics_open, copy in Scratch/data/mitsu). It gives first_mae_below_0p1.mae = 0.09945429162061421, with 37 bits, 3,774 observables and 448.9 s ideal 100-way.
- first_mae_below_0p1: that key name is in the same file.
- 0.4 sigma: RECOMPUTED, (0.1 − 0.099454) / 0.0014536 = 0.38. The width is shot noise only, from analysis7.json.
- 52%: RECOMPUTED, 3774/7260 = 51.98% (n_files 7260 in out/analysis.json line 14).
- 0.2031: TRACED in out/analysis.json line 16 (0.20306).
- source: qia_leads/audits/mitsubishi_keio_2609.39693/out/analysis7.json; qia_leads/audits/mitsubishi_keio_2609.39693/out/analysis.json
- grep: `"mae": 0.09945429162061421`

## 11. recount_2511.09322 : FIX (calibration wording)
- Table 3 is in RP/recount_2511.09322.txt lines 518-520: JW 0.0040±0.0012 and GSE 0.0020±0.0002, three repetitions each (line 503).
- Rebuilds: RECOMPUTED, 0.0040/0.0020 = 2.0. "About twice as many shots" also rebuilds from the raw shots: 9877/0.380 = 25,992 against 9478/0.748 = 12,671, a ratio of 2.05.
- Not resolved by the widths: RECOMPUTED. This holds if each ± is a one-sigma width. Then the ratio is 2.0 ± 0.63 (1.27 to 2.89 at the edges), 1.6 widths from no gain. The paper never says what the ± is. If it is the spread of the 3 repetitions, the standard errors are √3 smaller, giving 2.0 ± 0.37 and 2.85 SE.
- Problem: "Print the widths" asks for widths the table already prints.
- Suggested measured: "Rebuilds (0.0040 / 0.0020 = 2.0). Read as one-sigma, the printed widths give 2.0 ± 0.6 (1.3 to 2.9), so "twofold" is a point estimate. The paper does not say what the ± is."
- Suggested calibration: "F3 State what the ± widths are (spread over the three repetitions or a standard error) and give the ratio with its interval."
- source: qia_leads/recheck_published/src/recount_2511.09322.txt
- grep: `1.5% 0.0040` (the string 0.0040±0.0012 matches only under LC_ALL=C)

## 12. recount_2509.26229 : KEEP
- Ratios rebuild: RECOMPUTED. All nine Table 1 gaps equal (ω − 1) x 100 to the printed digit (RP lines 672-690). 47.5% = (1.9614 − 1.0287)/1.9614 = 47.55%.
- Run counts do not reconcile: TRACED. The paper gives:
  - 500 runs per size per backend, 38,500 samples over 77 sizes (lines 546 and 568)
  - 9 sizes x 50 runs = 450 per backend (lines 636-638)
  - 500 runs per size and 4,500 per backend (line 660)
  - 900 jobs, which is 2 x 450 (line 696)
- source: qia_leads/recheck_published/src/recount_2509.26229.txt
- grep: `based on 500 runs per size and backend (4500`

## 13. riken_2610.09532 : KEEP
- Tracks CZ count: TRACED in AU/riken_vlucj_2610.09532/AUDIT.md line 38 (median CZ for VLUCJ 101.5 / 49 against 320-4,068 / 229-2,998 for the others). The paper itself says VLUCJ is cheapest by CZ count (AUDIT line 13).
- At equal CZ, equal retention: TRACED in out/recompute_retention.json lines 1880-1920. For H2O, M = 2, 10 CZ:

  | chip | basis | VLUCJ | CHC |
  |---|---|---|---|
  | kingston | HO | 90.481 | 90.528 |
  | kingston | modal | 90.558 | 89.965 |
  | phoenix | HO | 93.306 | 93.272 |
  | phoenix | modal | 93.109 | 92.944 |
- Optional: the equal-CZ evidence is that one setting on two chips. "at the one equal-CZ setting (H2O, M = 2)" would be exact.
- source: qia_leads/audits/riken_vlucj_2610.09532/out/recompute_retention.json; qia_leads/audits/riken_vlucj_2610.09532/AUDIT.md
- grep: `"VLUCJ_ret": 90.481`

## 14. recount_10.5281/zenodo.23108790 : KEEP
- 30.88 and 21.22 on 15 dof, p 0.0091 and 0.130: printed at RP lines 709-712. RECOMPUTED with my own chi-square tail function as 0.0091 and 0.1299. Runs 2 and 3 also rebuild (18.05 gives 0.260, 14.85 gives 0.462).
- w divided by sqrt(15): their definition is w = sqrt(χ²/[Ns(K − 1)]) (line 424), with Ns = 1024 (line 351) and K − 1 = 15. RECOMPUTED: theirs comes to 0.0448 and 0.0372, while sqrt(χ²/N) gives 0.174 and 0.144. The ratio is 3.873 = sqrt(15).
- Note: 0.17 and 0.14 are still "small" on Cohen's scale (0.1 small, 0.3 medium). Their conclusion stands and only the value changes. The cell does not claim otherwise.
- source: qia_leads/recheck_published/src/recount_10.5281_zenodo.23108790.txt
- grep: `p = 0.0091, Cohen`

## 15. recount_2607.27777 : KEEP
- Rebuilds as printed: RECOMPUTED every Table IV entry (RP lines 568-582) from the appendix CASCI and DHF energies (lines 1048-1074) and the Table III PDMs (lines 450-466):
  - all 8 ΔE match to 0.001 mHa
  - all 8 ΔPDM match
  - %E_corr matches within input rounding (99.626 printed 99.62, 99.761 printed 99.75, 92.599 printed 92.60)
- Calibration printed without a date: TRACED at line 556. The device figures (CZ 2.71e-3, SX 3.53e-4, readout 1.48e-2, T1 196.04, T2 98.82) are given "at the time of the experiments", and there is no date anywhere.
- No data released: TRACED at line 645 (available on reasonable request).
- Note, not in the cell: the text says the hardware energies agree with CASCI within ~0.01 mHa (line 600). Table IV ΔE is above 0.01 mHa in 5 of 8 rows (0.034 to 0.465). Bones's call whether to add it.
- source: qia_leads/recheck_published/src/recount_2607.27777.txt
- grep: `At the time of the experiments`

## 16. uchicago_ibm_backaction : KEEP
- Spectators assumed negligible: TRACED in AU/uchicago_backaction_2606.00433/src/paper.txt line 1069 (assumption S10(iv)).
- Z-twirled protocol: lines 46, 92 and 98.
- "~100x" against a baseline they built: the abstract (src/abs.html, src/paper_v2.txt) has ~100x. Line 194 says the baseline collapses the learned errors into a confusion matrix.
- Our per-readout kick on untouched neighbours: TRACED in CR/results_prereg.txt. Fez is −1.618 deg at full pack and −0.133 at 10 of 39. Kingston is −2.864 and −0.276. Marrakesh is −0.233 at 10 of 39.
- Optional wording: the How cell says "their Z-twirled protocol readout-kick data (DOI)". The authors released no data (AUDIT.md line 65), and the DOI is ours. Clearer: "Our readout-kick measurements (DOI) set against their Z-twirled protocol".
- source: qia_leads/audits/uchicago_backaction_2606.00433/src/paper.txt; arxiv_one_readout/control_run/results_prereg.txt
- grep: `The solid baseline collapses the learned errors into a confusion matrix`

## 17. vanguard_portfolio : KEEP
- BFCD 0.91% against TwoLocal 0.49%: TRACED in AU/vanguard_portfolio/src/paper.txt line 185.
- The comparator is local search on the untrained circuit's samples: TRACED at lines 179-180 (the "Initial" distribution is iteration 1 of the TwoLocal bilinear on the simulator) and line 171 (all parameters start at π/3).
- No data statement: TRACED. The only github hits are arXiv page chrome (lines 4, 9 and 10).
- source: qia_leads/audits/vanguard_portfolio/src/paper.txt
- grep: `BFCD color ( 0.91`

## 18. workday_2609.38713 : FIX
- 15 of 18 worse: TRACED in AU/workday_2609.38713/out/analysis.json (8 of 10 and 7 of 8), digitized from the vector Fig. 4 (out/fig4_digitized.json).
- Median ratios: RECOMPUTED from the 18 digitized pairs (AUDIT.md lines 23-24). At 2 layers the raw median is 0.00735 and ZNE 0.0303, a ratio of 4.12. At 5 layers they are 0.0071 and 0.0531, a ratio of 7.48.
- 4.36 and 7.55: RECOMPUTED. sqrt(19) = 4.359 applies with 8,192 shots at each of the three fold points. sqrt(57) = 7.550 applies with 8,192 shots split over the three.
- Problem: the cell pairs each depth with a different shot convention, but both depths ran under one protocol.
  - The paper ran both under its equal-online-budget protocol (src/paper.txt line 409). Table 1 gives ZNE B/3 shots per execution.
  - Under that protocol the amplification is 7.55 at both depths. 7.48 (5 layers) matches; 4.12 (2 layers) does not.
  - With 8,192 shots per execution it is 4.36 at both depths. 4.12 matches; 7.48 does not.
  - The raw medians are the same at both depths (0.0074 and 0.0071), so shot noise alone does not explain why the two ratios differ.
  - The audit itself calls the shot-noise reading consistent, not proven (AUDIT.md line 49).
- Suggested measured: "ZNE worse on 15 of 18. Median ratios 4.12 (2 layers) and 7.48 (5 layers) sit between the shot-noise amplification of their own three-point Richardson with 8,192 shots per execution (4.36) and with 8,192 split three ways (7.55)."
- Suggested calibration: "F6 Compare hardware ZNE with the shot-noise amplification of the same Richardson extrapolation: 4.36 at 8,192 shots per execution, 7.55 under the paper's equal-budget split. The observed 4.12 and 7.48 fall in that range, so shot noise is not ruled out as the cause."
- source: qia_leads/audits/workday_2609.38713/out/analysis.json; qia_leads/audits/workday_2609.38713/src/paper.txt
- grep: `"median_ratio": 4.122448979591836`

## 19. recount_10.5281/zenodo.22644883 : FIX
- "13 (11 OK)" and "25 (13 OK, 3 expl)": TRACED at RP lines 2095 and 2100.
- "9 rows": RECOUNTED from the Appendix C ledger table (RP lines 2085-2222, script inline). There are 25 rows with verdicts. In 10 of them, not 9, the verdicts exceed OK plus exploratory:

  | session | verdicts not accounted |
  |---|---|
  | Learning | 2 |
  | Life | 9 |
  | Memory to mind | 3 |
  | Replication | 1 |
  | Rift | 2 |
  | Rift II | 1 |
  | Ubi II | 1 |
  | Ubi III | 2 |
  | Finis | 1 |
  | Copia | 1 |
- The remainders sum to 23. That is the totals line's "23 missed" (line 2224: 395 run = 361 passed + 23 missed + 11 exploratory; the table columns sum to 395, 361 and 11). So the misses are stated in total; what the table lacks is a miss count per row.
- The printed binding checks hold: RECOMPUTED, 361 + 23 = 384 and 384 + 11 = 395.
- Not in the cell: 402 registered minus 395 run minus 6 not run leaves 1 application unaccounted (lines 13, 145 and 2223-2224).
- "later Bands I–II": not in this record. Band II (Zenodo 22715893, band2_paper_v3.pdf, copy in Scratch/data/band2) does print misses per row, as "7 (6 OK, 1 miss)" and "8 (6 OK, 2 miss)". A Zenodo creator search found no record titled Band I.
- Suggested measured: "In 10 rows the verdict count exceeds OK plus exploratory. The remainders sum to 23, the totals line's 23 misses, but no row names its misses. The printed binding checks hold."
- Suggested calibration: "F4 List the misses per row in the summary table, as the later Band II does."
- source: qia_leads/recheck_published/src/recount_10.5281_zenodo.22644883.txt
- grep: `361 passed, 23 missed, 11 exploratory`

## 20. recount_10.5281/zenodo.21199323 : KEEP
- The null ran on ibm_fez (4-5 July 2026): RP lines 1, 6 and 53.
- The QITE-feedback treatment ran on ibm_kingston (1 June 2026): lines 10, 14, 51 and 557.
- Coherence exp(−8 Var p1) of 0.99 against 0.4127 for random angles: lines 65-68 (definition also at line 510). Random angles give broad p1 distributions and so high variance (lines 69-71).
- Note: the authors argue that calibration differences cannot account for the result (line 57). "Does not isolate" is our reading.
- source: qia_leads/recheck_published/src/recount_10.5281_zenodo.21199323.txt
- grep: `Random angles (v2, null) 0.4127`

## 21. bas_sofia_grover : FIX (calibration wording)
- No data: TRACED in AU/bas_sofia_grover_2604_23228/AUDIT.md line 8 (no availability statement).
- The run date precedes the stated software versions: TRACED. src/paper.txt line 146 gives the Marrakesh runs as 2025-03-12, and line 93 names qiskit 2.1.0 and qiskit-ibm-runtime 0.40.1. The PyPI upload dates are in out/qiskit.json (2025-06-19) and out/qiskit-ibm-runtime.json (2025-06-05). It is likely a typo for 2026-03-12 (the other runs are in March 2026), but that cannot be settled without job ids.
- Problem: "State the run dates and software versions" asks for things the paper already prints.
- Suggested calibration: "F4 Correct or explain the ibm_marrakesh run date (2025-03-12 predates qiskit 2.1.0 and qiskit-ibm-runtime 0.40.1), and release the counts."
- source: qia_leads/audits/bas_sofia_grover_2604_23228/src/paper.txt; qia_leads/audits/bas_sofia_grover_2604_23228/out/qiskit.json; qia_leads/audits/bas_sofia_grover_2604_23228/out/qiskit-ibm-runtime.json
- grep: `the ones on Marrakesh (Heron r2) on 2025-03-12`

## 22. cern_bern_lmu_marrakesh : FIX
- 1,021 CZ: TRACED in the App. F text at src/paper.txt line 516 (Table 1 prints 1,023), AU/cern_2602.21311/src/count_check_out.txt and AUDIT.md line 15.
- 1.616 (23 Oct 2026): TRACED in SW/results_sweep_3.text line 33.
- 5.0: RECOMPUTED, 1,021 x 3.044e-3 x 1.616 = 5.02 (AU/cern_2602.21311/src/projection_budget_out.txt line 5). The 3.044e-3 is the median stated CZ error in IBM's 21 Oct 2026 18:44 record (src/ext/backend_properties_ibm_marrakesh.json, the same record as CR/backend_properties_ibm_marrakesh.json).
- Problem: the 5.0 multiplies one record's stated figure by a factor taken against another.
  - The 1.616 factor was measured against the 23 Oct 16:33 record. That record's median stated CZ error is 2.450e-3 (SW/props_sweep_ibm_marrakesh.json, my recount, 8 entries of 1 excluded), 20% lower than on 21 Oct.
  - On the 23 Oct record alone, our delivered chip-median CZ error that day was 4.22e-3 (results_sweep_3.text line 33), and 1,021 x 4.22e-3 = 4.31.
  - The factor route on the same record gives 1,021 x 2.450e-3 x 1.616 = 4.04.
  - So "at our delivered CZ error" is about 4.3, not 5.0. The reading (several expected errors per run) is unchanged.
- Sample source not named: TRACED. No device or simulator is named for the shot-based likelihoods (src/paper.txt lines 287-296). App. F (lines 515-546) covers transpilation only, and its Table 1 lists an Aer row. AUDIT.md line 32.
- Suggested measured: "At our delivered ibm_marrakesh CZ error (chip median 4.22e-3, 23 Oct 2026), their 1,021 CZ gates amount to 4.3 infidelity units. Sample source not named."
- Suggested calibration: "Q17 Budget the circuit at delivered CZ error: 1,021 CZ at our ibm_marrakesh delivered median (4.22e-3, 23 Oct 2026; 1.616 times stated, edge by edge) is 4.3 infidelity units. Name the sample source."
- source: arxiv_one_readout/sweep_run/results_sweep_3.text; arxiv_one_readout/sweep_run/props_sweep_ibm_marrakesh.json; qia_leads/audits/cern_2602.21311/src/projection_budget_out.txt
- grep: `delivered chip median 4.22e-03`

## 23. recount_10.5281/zenodo.20026696 : KEEP
- Fidelity 1.0, 16 distinct bitstrings, 8,192 shots, 4-qubit GHZ: TRACED at RP lines 39-40, 57, 162-165 and 737-738.
- 17,361x and 94.54%: printed at lines 20, 74 and 702.
- Fidelity below 1: RECOMPUTED by logic. An ideal 4-qubit GHZ gives only 0000 and 1111. Weight on any of the other 14 strings lowers the measured GHZ population below 1, whether it comes from state error or readout error. The record does not separate the two.
- source: qia_leads/recheck_published/src/recount_10.5281_zenodo.20026696.txt
- grep: `across 16 distinct bitstrings, achieving fidelity = 1.0`

## 24. cuhk_mcm : KEEP
- The headline comes from a simulator fed by the same calibration the compiler uses: TRACED in AU/cuhk_2511.10921/src/paper.txt line 210.
- The kick is small at their dose: TRACED in our dose rows, CR/results_prereg.txt. Fez at K = 1 has interval [−0.152, +0.024] deg per readout and −0.133 at K = 10. Kingston is −0.276 at K = 10, marrakesh −0.233. The projection in src/check_cuhk_out.txt gives at most 1.4 deg after 9 MCMs, P(Z) ≤ 1.5e-4.
- Note: the paper does not print the number of MCMs per circuit. "Their dose" assumes one readout at a time (AUDIT.md line 48).
- Hardware not decidable from the release: AUDIT.md lines 51-53.
- Optional: the How cell has the same "their ... readout-kick data (DOI)" wording as row 16.
- source: arxiv_one_readout/control_run/results_prereg.txt; qia_leads/audits/cuhk_2511.10921/src/check_cuhk_out.txt; qia_leads/audits/cuhk_2511.10921/src/paper.txt
- grep: `R2 K=1: interval [-0.152, +0.024]`

## 25. free_2509.19448 : FIX (section number)
- The statement: TRACED at RP/free_2509.19448.txt lines 400-402. It says the variances scale as ~ν^(-1/2), and so do the covariance elements.
- Textbook: a binomial variance goes as 1/ν and its standard deviation as ν^(-1/2). The paper's own line 1000 gets the precision scaling right.
- "Sec 2.4": WRONG. The sentence is in Sec. 2.3, whose heading is at line 322, and the paper has no Sec. 2.4. Both arXiv versions agree (v1 of 23 Sep 2025 and v2 of 29 May 2026, copies in Scratch/data/a2509).
- Suggested published: replace "Sec 2.4:" with "Sec. 2.3:". The measured and calibration cells stand.
- source: qia_leads/recheck_published/src/free_2509.19448.txt
- grep: `since the variances of the estimated readout probabilities scale as` (grep -a)

## 26. fez_carbon_credit : FIX (calibration clause)
- 69.64: TRACED in AU/fez_carbon/src/paper.txt lines 870, 925 and 973. It is also in the authors' repo results file (kept copy AU/fez_carbon/ext_repo/repo/results/resultados_consolidados_v7.json, executions[3].qaoa_zne.score).
- 63.34: TRACED in AU/fez_carbon/check_carbon_output.txt (an upper bound on any k = 28 portfolio). The construction is in AUDIT.md line 24.
- 47.46 in 0.18 s: TRACED in the same file (swap local search from greedy: 47.4623 in 0.18 s).
- Single author, Federal University of Goias: AUDIT.md line 6.
- Report expectation values, not the best valid shot: TRACED. The extrapolated quantity is the maximum valid-shot score (AUDIT.md line 31).
- "Recompute run 4 with the published evaluate() and check the index alignment": NOT FOUND in the audit.
  - The audit explains Run 4 differently. A quadratic extrapolation of best-valid-shot scores is not the score of any portfolio, so it can exceed the bound (AUDIT.md items 4 and 7 and outcome (c)).
  - "Index alignment" appears only in a referee line (qia_leads/matrix_page/abc_reports.json.pre-sitepass-20261030) and in the Book and page built from it.
  - Nothing on disk tests for an index error.
- Suggested calibration: "F5 F7 Report expectation values, not the extrapolated best valid shot (Run 4's 69.64 lies above the 63.34 any 28-municipality portfolio can reach). Compare with the swap local search (47.46)."
- source: qia_leads/audits/fez_carbon/check_carbon_output.txt; qia_leads/audits/fez_carbon/src/paper.txt
- grep: `loose upper bound on any k=28 portfolio (n_biomes at its max): 63.34`

## 27. free_2512.03341 : KEEP
- The abstract says "without error mitigation": RP line 17.
- The text calls the renormalization an error mitigation strategy: lines 1203-1210 (Eq. 68).
- The Fig. 12 caption puts N = 4 on ibm fez and N = 6 on the noisy IBM simulator: lines 1184-1187.
- source: qia_leads/recheck_published/src/free_2512.03341.txt
- grep: `This normalization procedure serves as an error mitigation` (grep -a)

## 28. hanyang_2610.14778 : KEEP
- "approximately 10%": AU/hanyang_defect_2610.14778/src/paper.txt lines 34 and 814.
- The d = 5 values, 12.1% (Z) and 10.0% (X): RECOMPUTED in out/recompute.json (12.10 and 10.04).
- The d = 7 values, 8.1% and 6.7%: printed at lines 779-780 and 794-796. RECOMPUTED from their LEPC values (0.062331 to 0.057272, and 0.137551 to 0.128216) as 8.12 and 6.79. 6.79 rounds to 6.8; the cell quotes their printed 6.7. Optional: "6.8% (printed 6.7%)".
- No error bars: TRACED. There is no ±, error bar, CI or standard error anywhere in the text (AUDIT.md line 41).
- source: qia_leads/audits/hanyang_defect_2610.14778/src/paper.txt; qia_leads/audits/hanyang_defect_2610.14778/out/recompute.json
- grep: `0.128216 (a 6.7% reduction)`

## 29. lane_hebrew_2506.11270 : KEEP
- Spectators get an equal delay, "automatically mitigated", unique to their approach: TRACED in the Fig. 1 text, paper_v1.txt lines 354-355 and paper_v2.txt lines 362-363.
- All checks are computational-basis: DESK.md line 21. Neither version has a phase-basis test.
- The Fig. 6 caption gives 0.977 ± 0.027 and the text gives 0.975 ± 0.027 (all-zeros input, m = 5): TRACED in v1 lines 1053 and 1105 and in v2 lines 1188 and 1192.
- Extrapolated to order 5 from data to order 3: v2 line 1188, and the Fig. 6 axis ticks 0, 1, 2, 3 in the v2 text layer (around line 1170).
- source: qia_leads/audits/lane_hebrew_2506.11270/src/paper_v2.txt; qia_leads/audits/lane_hebrew_2506.11270/src/paper_v1.txt; qia_leads/audits/lane_hebrew_2506.11270/DESK.md
- grep: `the extrapolated fidelity is 0.975`

## 30. iisc_depth_model : KEEP
- 98.2%: AU/iisc_2607.24704/src/paper.txt lines 537 and 615. The extremes 1.87% and 2.11% are at lines 611-612.
- 97.89-98.13: RECOMPUTED as 100 − 2.11 and 100 − 1.87 (out/iisc_eq_check.txt item g). All three numbers carry "about", and Bones's final calls it borderline (AUDIT.md line 89).
- Eq. 8/9 off by orders of magnitude: RECOMPUTED in out/iisc_eq_check.txt items a-c. Eq. 8 returns at most 24 shots for F_max ≥ 0.9 and n_q ≤ 32. Eq. 9 gives about 6e7 at their own example, against the 285 quoted at paper line 95.
- source: qia_leads/audits/iisc_2607.24704/out/iisc_eq_check.txt; qia_leads/audits/iisc_2607.24704/src/paper.txt
- grep: `mean accuracy in [97.89, 98.13] % (paper: 98.2 %)`

## 31. iu_lbnl_2610.18482 : KEEP
- 80.4 / 82.5 / 79.8: printed at AU/iu_lbnl_2610.18482/src/paper.txt line 1061.
- The figure values are TRACED as printed labels in the PDF text layer (lines 1184-1248): hard repetition 86.2 / 70.8 / 90.1, unencoded baseline 92.1 / 80.3 / 94.6, and Lifting at d = 2 97.3 / 94.9 / 98.0.
- 65.8 / 74.1 / 63.0: RECOMPUTED as 1 − 2.7/7.9, 1 − 5.1/19.7 and 1 − 2.0/5.4. The headline also rebuilds: 1 − 2.7/13.8 = 80.4, 1 − 5.1/29.2 = 82.5 and 1 − 2.0/9.9 = 79.8. All are in out/analysis.json.
- source: qia_leads/audits/iu_lbnl_2610.18482/out/analysis.json; qia_leads/audits/iu_lbnl_2610.18482/src/paper.txt
- grep: `"lif2_vs_single_qubit_baseline_reduction": 65.8`

## 32. tcg_oist_marrakesh : KEEP
- 88% / 87%: the abstract (AUDIT.md line 16).
- Max of 30 entries, median 71.5%: RECOUNTED from Table 1 (src/paper.txt lines 626-660) with my own parser, Scratch/tcg/recount.py.
  - The 30 two-qubit reductions run from 22.13 to 87.87, median 71.485.
  - The depth maximum is 86.64.
  - All 60 printed reductions reproduce. In 7 of them the print is truncated rather than rounded (28.638 is printed 28.63).
- 8 of 48 wrong-sign entries: RECOUNTED from Table 2 (lines 1651-1676). There are 48 entries with nonzero ED, and PFD = (HW − ED)/ED x 100. Eight have the wrong sign: at Δ0 = 3, t 0.25 SPE and t 1.25 imbalance, QFI and SPE; at Δ0 = 15, SPE at t 0.50, 0.75, 1.00 and 1.25. This matches out/tcg_check.json. Bones's final had accepted the count without a recount; this is the recount.
- P_succ never evaluated: TRACED. The formula appears once (lines 1041-1042), and no number is computed from it.
- Note: the 71.5% median is for the two-qubit set. The depth median is 67.3%.
- source: qia_leads/audits/tcg_oist_marrakesh_2608.02245/out/tcg_check.json; qia_leads/audits/tcg_oist_marrakesh_2608.02245/src/paper.txt
- grep: `"of_which_sign_flipped": 8`

## 33. bl_2605.13109 : KEEP
- The Heron tolerance eps = 0.04, set from FakeFez: TRACED in AU/l7_2605.13109/src/paper_text_2605.13109.txt (the Heron-class deployment value, and the Table 9 per-input eps from the FakeFez and FakeBrisbane noise models).
- 0.074: TRACED in the same file (worst over X, Y, Z = 0.074). RECOUNTED from their released counts in src/cells_out.txt: the worst deviation of 18 cells is 0.0736.
- source: qia_leads/audits/l7_2605.13109/src/cells_out.txt; qia_leads/audits/l7_2605.13109/src/paper_text_2605.13109.txt
- grep: `worst dev 0.0736`

## 34. lviv_2610.06127 : KEEP
- "within estimated error bounds": AU/lviv_2610.06127/src/paper.txt lines 23 and 758.
- 13 of 13 negative and 5 of 13 outside their own bars: RECOUNTED from the kept digitization, out/digitized.json (panel 6b). All 13 points are negative (−0.091 to −0.177). Five fall outside their own bars, at θ/π = 0, 0.333, 0.416, 0.667 and 0.75.
- I did not re-digitize the PDF here (PyMuPDF is not installed). The digitization is ours (src/digitize_fig.py), made from the figure's vector paths.
- source: qia_leads/audits/lviv_2610.06127/out/digitized.json; qia_leads/audits/lviv_2610.06127/AUDIT.md
- grep: `5 of 13 (theta/pi = 0, 0.333, 0.417, 0.667, 0.75`

---

## Methods notes
- Fetched on 30 Oct 2026 into Scratch/data, all public:
  - two survey result files from github Mirza-Samad-Ahmed-Baig/quantum-phase-cycled-rb
  - data/annulene/hybrid/summary.json from github sk888ks/macrocycle_dynamics_open
  - Zenodo API records for Westrick (22644883, 22715893, 22809021, plus a creator search) and band2_paper_v3.pdf
  - arXiv 2509.19448 v1 and v2 PDFs
- PDFs were turned into text with pypdf (Scratch/pdf2txt.py). Their code was never run.
- My scripts: Scratch/tcg/recount.py for the TCG tables. The chi-square tail, the Westrick ledger count, the 2607.27777 Table IV rebuild and the marrakesh record medians were run inline with python3 -I.
- IBM records used (already on disk, no calls):
  - CR/backend_properties_ibm_marrakesh.json (21 Oct 18:44)
  - SW/props_sweep_ibm_marrakesh.json (23 Oct 16:33)
- No file outside Scratch and this report was edited.
