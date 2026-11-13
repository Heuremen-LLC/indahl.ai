# PROV lane P3, 30 Oct 2026 (28 rows, read only, evidence only)

Conventions
- Paths are under /Users/heuremen/bones-forge/ unless they start with /.
- "paper text" = qia_leads/recheck_published/src/<id>.txt (cached copy of their paper or Zenodo record). Line numbers are of that file.
- SCR = /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p3/ (my fetched data and scripts, one subfolder per row, e.g. SCR/r25/).
- Their public data was fetched from their GitHub or Zenodo and read as data (python3 -I). Nothing of theirs was run. Where I reran OUR code (twin_cauca.py, ufsm.py, under venv_quantum) it ran on copies in SCR against their data files.
- THE_BOOK.md, the ledger and book_calibrated.json were used only to find the rows, never as proof.
- Verdict words follow the brief. "PULL (clause)" = one number or sentence cannot be traced, the rest of the row stands if that clause is deleted.

## Summary: 21 KEEP, 5 FIX, 2 PULL

| # | row id | verdict | what to do |
|---|---|---|---|
| 1 | recount_10.5281/zenodo.22849729 | KEEP | none |
| 2 | recount_10.5281/zenodo.19840870 | KEEP | none |
| 3 | free_2508.01893 | KEEP | optional: "about 10-20% apart" is 5-22% (see row) |
| 4 | free_2511.08096 | KEEP | none |
| 5 | free_2208.01050 | PULL (clause) | delete "4 of 6 checks reproduce" (the six checks lived only in the deleted inventory). "16 of 274" is recounted and stands |
| 6 | recount_2604.02569 | KEEP | none |
| 7 | recount_10.5281/zenodo.20025452 | KEEP | none |
| 8 | kaist_fez | FIX | the 42-74% belongs to the factor intervals 1.19-1.34, not to 1.24-1.27 (54-59%) |
| 9 | recount_10.5281/zenodo.21587385 | KEEP | none |
| 10 | recount_10.5281/zenodo.21586385 | FIX | drop "truncated, not rounded": false for this paper's table. 81.86% stands |
| 11 | fresh_lums_2609.13669 | KEEP | none |
| 12 | recount_10.5281/zenodo.21981913 | KEEP | none |
| 13 | recount_2410.09121 | FIX | "14 of 17" is 15 of 18 |
| 14 | kingston_phase_diagram | PULL | "2.6-4.4" and "damped by ~3x" cannot be traced, recomputed or recounted. "1.30-1.37" is traced |
| 15 | recount_10.5281/zenodo.21041855 | KEEP | optional: 8,192 is a quotient, not printed |
| 16 | recount_10.5281/zenodo.19855345 | KEEP | none |
| 17 | free_2407.16107 | FIX | printed -15.5943 is not the notebook's -15.594427 to the printed digits (0.00013 Ha apart) |
| 18 | fill_2605.30676 | KEEP | optional: say "paper's twin" for the 0.11-0.34 |
| 19 | k2025_ufsm_2502.01824 | KEEP | none |
| 20 | recount_2604.27836 | KEEP | none |
| 21 | free_2511.22324 | KEEP | none |
| 22 | free_2502.13910 | KEEP | none |
| 23 | free_2505.09371 | KEEP | none |
| 24 | und_fez | KEEP | optional: their 1x-2x is a training-data arm, not "results across a sweep" |
| 25 | free_2209.05716 | KEEP | none |
| 26 | free_2212.14170 | KEEP | none |
| 27 | free_2505.17731 | KEEP | none |
| 28 | recount_10.5281/zenodo.20688687 | FIX | "132-sigma ... cannot be rebuilt" is wrong: it rebuilds to 132.7 from their raw shots. 3.672 and 267.2% stand |

Replacement text for the FIX and PULL rows is at the end of each row's block (lines starting "Suggested").

---

## 1. recount_10.5281/zenodo.22849729 : KEEP
| number | how | source |
|---|---|---|
| 97.15% | RECOMPUTED: 1 - 0.0285 = 0.9715, their stability formula S = (1 - mean abs deviation) x 100 | paper text lines 21, 86, 88 |
| 0.4536 | printed | paper text lines 23, 92 |
| n = 10 and "noiseless simulator values" | RECOUNTED from released code (read, not run): the comparison loop is over dataset[:10], and corr = np.corrcoef(ideal_vals, y[:10]) where ideal_vals come from local_engine = QubeEngine() on the default AerSimulator (no noise model) | github.com/gulfamh1999-afk/qube-cancer-atlas qube_cancer_atlas.py, copy SCR/r0/qube_cancer_atlas.py. Zenodo record 22849729 lists that repo as isSupplementTo |
| p = 0.19 | RECOMPUTED: t = 0.4536 x sqrt(8) / sqrt(1 - 0.4536^2) = 1.4396 on 8 df, two-sided p = 0.1879 (own t-integral, SCR/tdist.py) | arithmetic |
Note: the correlation itself depends on a random start and live hardware, so it is taken as printed.

## 2. recount_10.5281/zenodo.19840870 : KEEP
| number | how | source |
|---|---|---|
| 96.9%, 96.0%, 0.9 points, 1,024 shots, 3.1% | printed (3.1% = 1/sqrt(1024) = 3.125%) | paper text lines 1732-1739 |
| p ~ 0.965 | RECOMPUTED (0.969 + 0.960)/2 = 0.9645 | arithmetic |
| 0.8% | RECOMPUTED: one-run sd sqrt(0.9645 x 0.0355 / 1024) = 0.00578, difference of two independent runs x sqrt2 = 0.00818 (using each run's own p: 0.00818 too) | arithmetic |
| 1.1 widths | RECOMPUTED 0.009 / 0.00818 = 1.10 | arithmetic |
| "overstated 4x" (source line) | RECOMPUTED 3.125 / 0.818 = 3.8 | arithmetic |

## 3. free_2508.01893 : KEEP
| number | how | source |
|---|---|---|
| Table II rows and GEO-M 0.107, 0.036, 0.182, 0.063 | printed | paper text lines 281-291 |
| geometric means 0.096, 0.030, 0.165, 0.059 | RECOMPUTED over the six rows: 0.0960, 0.0299, 0.1652, 0.0594 | arithmetic |
| arithmetic means 0.107, 0.036, 0.182, 0.063 | RECOMPUTED: 0.1067, 0.0365 (exactly), 0.1822, 0.0627. These equal the printed GEO-M row | arithmetic |
| "Table I uses a true geometric mean" | RECOMPUTED: Kolkata [12] column geo mean 1.477e-6 vs printed 1.48E-06 (the arithmetic mean would be 2.84e-5) | paper text lines 230-238 |
| "about 10-20 % apart" | RECOMPUTED arithmetic/geometric = 1.111, 1.222, 1.102, 1.054, i.e. 5-22% (or 6-18% of the arithmetic) | arithmetic |
Suggested (optional): "about 5-20 % apart".

## 4. free_2511.08096 : KEEP
| number | how | source |
|---|---|---|
| 0.693 +/- 0.053, 0.56 +/- 0.12, 0.594 +/- 0.019 | printed (Table 1, "Interval" not defined in the caption) | paper text lines 670-679 |
| +0.133 | RECOMPUTED 0.693 - 0.56 = 0.133. Half-widths 0.053 + 0.12 = 0.173 > 0.133, the intervals overlap, so "consistent as printed" holds | arithmetic |

## 5. free_2208.01050 : PULL (clause)
| number | how | source |
|---|---|---|
| tf rule (4 for 0.05<=ta<=0.17, 10 for 0.17<ta<=2) | printed | paper text line 306 |
| 274 files | RECOUNTED: 93 + 5 (bogota anticrossing, full_crossing) + 137 + 39 (lima) = 274 .dat files | github.com/sanhq17/Testing_KZM_IBMQ data/ (paper Data Availability, paper text line 474); copy in SCR/r4/data |
| 16 files with tf = 4 where the rule gives 10 | RECOUNTED with SCR/r4/count_tf.py (tf = last t_sim value in each file, ta from the header): ta = 0.25 gives 13 files and ta = 0.5 gives 3 files stored with tf = 4 (bogota anticrossing 4, bogota full_crossing 1, lima anticrossing 4, lima full_crossing 7 = 16). No file has tf = 10 where the rule says 4. Matches the cell | their data |
| (extra, not in cell) | 39 lima anticrossing files have ta between 0.025 and 0.0455, below the stated 0.05 lower bound, all tf = 4 | their data |
| "4 of 6 checks reproduce" | NOT FOUND. The only source was the deleted qia_leads/inventory_2022jul_2024jun/FREE_2022H2_RESULTS.jsonl (named on the Book's row line). The six checks are listed nowhere in a kept file or in the cell. find / for that file name: no copy | none |
Suggested: delete the sentence "4 of 6 checks reproduce". Keep "16 of 274 released files use tf = 4 where the stated rule gives tf = 10".

## 6. recount_2604.02569 : KEEP
| number | how | source |
|---|---|---|
| Eq. 38, n = 12, 0.74, 0.66 (sim), 58%, 49%, 33% (hardware) | printed. Their text also says the fidelity measures "the fraction of mismatched bits" | paper text lines 626-642 (grep fails on this file's bytes, read with python) |
| F can only be k/12: 0.75 and 0.50 | RECOMPUTED 1 - d/12 = 1, .9167, .8333, .75, .6667, .5833, .5, .4167, .3333 ... Nearest to 0.74 is 0.75, nearest to 49% is 0.50 | arithmetic |
| 58% = 7/12, 33% = 4/12, 0.66 = 8/12 truncated | RECOMPUTED 0.5833, 0.3333, 0.6667 (rounds to 0.67) | arithmetic |

## 7. recount_10.5281/zenodo.20025452 : KEEP
| number | how | source |
|---|---|---|
| <H_YY> = 16.00 +/- 0.21, 16.4715 +/- 0.0448, 15.2815 +/- 0.0493; predicted 21 | printed ("consistent with the predicted noiseless value 21") | paper text lines 72-73, 319-320, 1475-1479 |
| 24, 101, 116 widths below 21 | RECOMPUTED (21 - 16.00)/0.21 = 23.8; (21 - 16.4715)/0.0448 = 101.1; (21 - 15.2815)/0.0493 = 116.0 | arithmetic |
| 1.19 and 18 widths | RECOMPUTED 16.4715 - 15.2815 = 1.1900; sqrt(0.0448^2 + 0.0493^2) = 0.0666; 1.19/0.0666 = 17.9 | arithmetic |
| 73-78% of ideal | RECOMPUTED 15.2815/21 = 72.8%, 16.00/21 = 76.2%, 16.4715/21 = 78.4% | arithmetic |

## 8. kaist_fez : FIX (wording of the range)
| number | how | source |
|---|---|---|
| ibm_fez CZ 1.244 [1.191, 1.303] and 1.269 [1.206, 1.338] (1.24, 1.27) | TRACED, RB 23 Oct 2026 | qia_runs/2026-10-29-gift-makesomenoise/noise_model_fez_calibration/fez_23oct_job1.text line 9 and fez_23oct_job2.text line 9; README.md line 15 of that folder; qia_leads/audits/kaist_fez_2607.13374/AUDIT.md section 5 |
| twofold gap | TRACED in their paper: model 38.5% feasible, hardware 16.9 +/- 0.6%, "about 2x lower" | qia_leads/audits/kaist_fez_2607.13374/src/paper.txt lines 751-755, 784. 0.169/0.385 = 0.439 |
| 42-74% | TRACED to AUDIT.md section 6 (0.42 / 0.56 / 0.74 after the uniform subtraction, at factors 1.191 / 1.255 / 1.338) and the final line of the file. RECOMPUTED: N = 711 gates, stated surviving fraction 0.146 so N r = 1.924; log gap after removing the 1.5% uniform feasible fraction ln((0.169-0.015)/(0.385-0.015)) = -0.877; share = 1.924 (f-1)/0.877 = 0.42 at 1.191, 0.56 at 1.255, 0.74 at 1.338 | AUDIT.md section 6; arithmetic |
The problem: 42% and 74% are the ends of the two 95% intervals (1.191 and 1.338). At the medians 1.244 and 1.269 the share is 54% and 59% (57% and 63% on the raw basis).
Suggested (QIA Calibration cell): "Scale the simulation's CZ error by our ibm_fez factor (1.24-1.27, intervals 1.19-1.34, 23 Oct 2026): it accounts for about 42-74% of the twofold gap (54-59% at the medians; projection)."

## 9. recount_10.5281/zenodo.21587385 : KEEP
| number | how | source |
|---|---|---|
| 3,353 counts, 4,096 shots, printed 81.84% | printed | paper text lines 19, 90-91 |
| 81.86% | RECOMPUTED 3,353/4,096 = 0.818604 (rounding and truncation both give 81.86, so 81.84 is neither) | arithmetic |
| "others are truncated, not rounded" | RECOMPUTED counts/4096 for 146, 128, 127, 124, 61, 57, 38, 11 : 3.5645, 3.125, 3.1006, 3.0273, 1.4893, 1.3916, 0.9277, 0.2686. Printed 3.56, 3.12, 3.10, 3.02, 1.48, 1.39, 0.92, 0.26 equal truncation in every row (rounding would give 3.03, 1.49, 0.93, 0.27 for four of them) | paper text lines 90-125 |

## 10. recount_10.5281/zenodo.21586385 : FIX (second sentence)
| number | how | source |
|---|---|---|
| 81.84% printed, 3,353/4,096 | printed | paper text lines 16, 74-75 |
| 81.86% | RECOMPUTED 3,353/4,096 = 81.86% | arithmetic |
| "the other frequencies are truncated, not rounded" | NOT TRUE for this paper. Printed 3.56, 3.12, 3.10, 3.02, 1.49, 1.39, 0.93, 0.27, others 1.25. 3.02 is truncated (rounds to 3.03) but 1.49, 0.93, 0.27 and 1.25 (51/4096 = 1.2451) are rounded (truncation gives 1.48, 0.92, 0.26, 1.24). The "consistent truncation" holds for the other Zenodo paper (row 9), not this one. The two cells were copied from each other | paper text lines 74-110 |
Suggested: Measured "3,353/4,096 = 81.86%." (drop the sentence on truncation). Calibration "Use 81.86% and round every frequency the same way." can stay.

## 11. fresh_lums_2609.13669 : KEEP
Raw counts and code are kept: qia_runs/2026-10-24-fill-lums (24 Oct) and qia_runs/2026-10-29-repeat-lums (29 Oct). I recomputed the job-mean spreads independently from the raw counts and their released JSON with a short numpy script (SCR/r10/lums_recompute.py).
| number | how | source |
|---|---|---|
| n=8 24 Oct: untwirled 0.326, twirled 0.048, interval [0.030, 0.117] | TRACED 0.3260, 0.0476, [0.0297, 0.1167]; RECOUNTED 0.3260 and 0.0476 from raw counts | qia_runs/2026-10-24-fill-lums/results_lums.text lines 2, 3, 7 |
| shot noise 0.0155 | TRACED (O-arm null median job SD) | qia_runs/2026-10-24-fill-lums/posthoc_lums.text line 1; RESULT_LUMS.md.text line 11 |
| n=10 24 Oct: 0.012, 0.017, excess at most 0.0117 and 0.0163, interval [0.011, 0.042] | TRACED 0.0123, 0.0170, 0.0117, 0.0163, [0.0106, 0.0418]; RECOUNTED 0.0123 and 0.0170 | same file lines 10, 11, 15 |
| n=8 29 Oct: 0.017, 0.027, excess at most 0.0167 and 0.0262 | TRACED 0.0172 (upper 0.0167) and 0.0269 (upper 0.0262); RECOUNTED 0.0172 and 0.0269 | qia_runs/2026-10-29-repeat-lums/results_lums_r2.text lines 2, 3 |
| intervals [0.030, 0.117], [0.011, 0.042] | RECOMPUTED sD x sqrt(5/chi2_0.975(5)) and sD x sqrt(5/chi2_0.025(5)), chi2 quantiles 12.8325 and 0.8312 | arithmetic |
| one step: J02O -2.835, five later jobs -1.97 to -2.10 | TRACED in RESULT_LUMS.md.text (POST HOC, line 24); RECOUNTED from raw counts: J02O -2.8352, then -2.0578, -1.9669, -2.0296, -2.0699, -2.0952 | qia_runs/2026-10-24-fill-lums/raw_lums_J*.json |
| their shifts +0.0426 (n=8), -0.0499 (n=10); "all tables reproduce" | TRACED; also recounted from their released JSON (+0.042646, -0.049858) | qia_leads/audits/fresh_lums_2609.13669/KNOWN_GOOD.md section 1 |
| 12 jobs interleaved | TRACED order TOOTTOOTTOOT | results_lums.text lines 1, 9 |

## 12. recount_10.5281/zenodo.21981913 : KEEP
| number | how | source |
|---|---|---|
| bare row ZZ -0.9756, XX -0.0124, YY +0.0082; printed purity 0.9641, printed F 0.00598 | printed in their released raw_hardware_tomography_data.csv (EXP-01), also a file of the Zenodo record | paper text line 69 |
| their formulas | printed: Tr(rho^2) = (1/4)[1 + ZZ^2 + XX^2 + YY^2], F(Psi-) = [1 - ZZ + abs(XX) + abs(YY)]/4 | paper text lines ~8670-8700 |
| F = 0.499 | RECOMPUTED (1 + 0.9756 + 0.0124 + 0.0082)/4 = 0.49905 | arithmetic |
| purity 0.488 | RECOMPUTED (1 + 0.95180 + 0.00015 + 0.00007)/4 = 0.48800 | arithmetic |
Check: the same formulas reproduce the printed F and purity of rows EXP-02 to EXP-06, 08, 09 and 12 to within 0.0004. The bare row is off, as are EXP-07, EXP-10 and EXP-11 (not in the cell).

## 13. recount_2410.09121 : FIX ("14 of 17" is 15 of 18)
| number | how | source |
|---|---|---|
| Table 2 | printed: 6 rows x 3 columns = 18 accuracies (v1 and v2 identical, own diff of arxiv.org/pdf/2410.09121v1 and v2, SCR/r12) | paper text lines 170-177 |
| test-set size not printed | searched the text for dataset, test, images, sample, trials: nothing | paper text |
| 187 | RECOUNTED: smallest N for which most cells equal k/N at two decimals. N = 187 (and 374, 561, 748) | arithmetic on Table 2 |
| 14 of 17 | DOES NOT REPRODUCE. At N = 187 eleven cells equal round(k/187 x 100, 2) and four more equal truncation (57.21 = 57.2193, 94.11 = 94.1176 twice, 83.95 = 83.9572): 15 of 18 fit. Three fit neither: 52.68 (nearest 99/187 = 52.94), 86.84 (nearest 162/187 = 86.63), 59.5 (111/187 = 59.36, 112/187 = 59.89). Strict rounding alone: 11 of 18 | arithmetic |
Suggested: Measured "15 of 18 Table 2 accuracies are k/187 (rounded or truncated to the printed digits). 52.68%, 86.84% and 59.5% are not. Test-set size not printed, 187 inferred after the data." Calibration "State the test-set size: 15 of 18 accuracies are k/187. 52.68%, 86.84% and 59.5% are not."

## 14. kingston_phase_diagram (arXiv 2609.16108) : PULL
| number | how | source |
|---|---|---|
| 1.30-1.37 (delivered / stated) | TRACED: ibm_kingston, three sessions 23-24 Oct 2026. CZ 1.302 [1.209, 1.379], 1.311 [1.226, 1.386], 1.345; sx 1.306 [1.234, 1.381], 1.366 [1.252, 1.443], 1.344. 1.30-1.37 is the union of the CZ and sx medians | arxiv_one_readout/sweep_run/SWEEP_SUMMARY_internal.text lines 7-8, 29-30; results_sweep_3.text lines 20-21; results_sweep_r2_part.text lines 20-21; results_sweep_ibm_kingston_r3.text lines 8-9; qia_leads/audits/kingston_constant/AUDIT.md line 31 |
| 2.6-4.4 times below what stated errors predict | NOT FOUND. Its audit folder qia_leads/audits/kingston_phase_diagram was deleted on 25 Oct (in the manifest's delete list). I read the paper text and the arXiv TeX source (main.tex, appendices.tex, SCR/r13/x): there is no damping factor, no stated gate-error figure for kingston, no table of amplitudes. Hardware data exist only as figure PDFs, the only release is their simulator code (github.com/kemperlab/yaqs). Appendix A gives only a model, C = gamma dt/(gamma dt + eps), with no values. I could not define a measured-over-predicted ratio from these that returns 2.6-4.4 | none |
| "damped by ~3x" (calibration) | NOT FOUND, same reason (derived from 2.6-4.4) | none |
Suggested: Measured "Our ibm_kingston delivered gate error is 1.30-1.37 times stated (RB, 23-24 Oct 2026)." and drop the 2.6-4.4 and "damped by ~3x" until the damping is re-measured from their figure data.

## 15. recount_10.5281/zenodo.21041855 : KEEP
| number | how | source |
|---|---|---|
| 57,344 shots, 7 jobs, 95.2% "average GHZ fidelity", qubit 13 sole measurement | printed | paper text lines 13-14, 29-31, 47-56 |
| 8,192 | RECOMPUTED 57,344 / 7 = 8,192 exactly. 8,192 itself is not printed | arithmetic |
Suggested (optional): "57,344 shots over 7 jobs = 8,192 per job" instead of "as printed".

## 16. recount_10.5281/zenodo.19855345 : KEEP
| number | how | source |
|---|---|---|
| f = 0.384 +/- 0.279, three patterns (M1, M5, M6), 51 memories, 5.67 bits | printed (Table 6: mean 0.384, std 0.279; Table 7: 51, 5.67) | paper text lines 37-39, 254-265, 285 |
| 73% | RECOMPUTED 0.279/0.384 = 0.7266 | arithmetic |
| 5.67 bits | RECOMPUTED log2(51) = 5.672 | arithmetic |

## 17. free_2407.16107 : FIX (wording)
| number | how | source |
|---|---|---|
| printed -15.5943 | printed, as the "expected value" | paper text lines 383, 416 |
| notebook reference energy -15.594427 | RECOUNTED from their released notebooks (read as JSON, not run): final_submission_latest.ipynb cell 13 prints "Reference_energy: -15.594427466321315" from NumPyMinimumEigensolver (classical exact solver); BeH2_gs_fermi_level_with_em_latest.ipynb cell 10 prints -15.594427466321344 | github.com/jsaroni/QHack2023_Feynmanprodigies (paper line 454), copies in SCR/r16 |
| "the printed -15.5943 is that classical value" | holds to 0.00013 Ha, not to the printed digits: -15.594427 rounds to -15.5944. Other classical references in the same repo: -15.59435832 (VQE_over_bond_length.ipynb, one bond length), -15.59443 and -15.59471 ("Exact Energy" in two notebooks). -15.5943 equals -15.594358 only by truncation | their notebooks |
Suggested: "The notebook reference energy is -15.594427 (classical solver). The printed -15.5943 is a classical value, 0.00013 Ha above it, not a hardware result."

## 18. fill_2605.30676 : KEEP
| number | how | source |
|---|---|---|
| 9.7% | TRACED: R5 share abs(dA)/S_gap, max 0.097 (job 4 minus job 1, same circuits, about 7 minutes apart, abs(dA) <= 0.0125) | qia_runs/2026-10-24-fill-cauca/results_cauca.text line 26; RESULT_CAUCA.md.text; qia_runs/2026-10-30-gift-cauca/volunteer_kingston/results_cauca.text |
| 0.11-0.34 | TRACED: R4 twin minus hardware 0.113, 0.301, 0.344, 0.310, 0.267, 0.237, 0.217, 0.198, ABOVE at every N | same results_cauca.text line 20 |
| kingston CZ 1.302 to 1.345, single-qubit 1.306 to 1.366 (three sessions 23 and 24 Oct) | TRACED: CZ 1.302, 1.311, 1.345; sx 1.306, 1.366, 1.344 | arxiv_one_readout/sweep_run/results_sweep_3.text lines 20-21, results_sweep_r2_part.text lines 20-21, results_sweep_ibm_kingston_r3.text lines 8-9 |
| 17 to 20% of the N=9 gap, N=2 gap wider by about 2% | RECOUNTED with our twin code (qia_runs/2026-10-24-fill-cauca/twin_cauca.py) on their released properties_L2.json and their published hardware means (SCR/r17/rescale17.py): (CZ, sx) = (1.302, 1.306) closes 0.169, (1.311, 1.366) 0.182, (1.345, 1.344) 0.192, corner (1.345, 1.366) 0.195; N=2 gap -0.0961 becomes -0.0977 to -0.0980 (wider by 1.7-2.0%) | their data; also qia_runs/2026-10-24-fill-cauca/rescale_check.text |
Note: the 0.11-0.34 is for the paper's twin. The released-notebook twin sits higher (job-1 table: 0.116 at N=2, 0.374 at N=4). The cell does not say which twin.

## 19. k2025_ufsm_2502.01824 : KEEP
| number | how | source |
|---|---|---|
| deficit 52 pp (DD off) | TRACED 51.984 pp (b) | qia_runs/2026-10-24-fill-ufsm/results_ufsm.text line 2 |
| their 4.67 pp, their +3.428 | TRACED (their Fig 8 counts through our code: (a) 1.245, (b) 4.673 pp; extra 3.428) | qia_runs/2026-10-24-fill-ufsm/RESULT_UFSM.md.text; results_ufsm.text line 3 |
| +49.698 +/- 0.289 | TRACED, and reproduced by rerunning ufsm.py on the raw counts (SCR/r18/dd_halfwidth.py) | results_ufsm.text line 3 |
| DD on: +3.97 (0.23), +3.06 (0.24) | TRACED +3.967 +/- 0.234 and +3.062 +/- 0.244 | qia_runs/2026-10-24-fill-ufsm/results_ufsm_dd.text line 1 |
| +0.54 | RECOMPUTED 3.967 - 3.428 = 0.539; rerun gives 0.5395 | arithmetic |
| 0.67 | RECOUNTED: 99% half-width = 2.5758 x hypot(0.2336, 0.1178) = 0.674 pp, where 0.1178 is their pooled binomial sd (ufsm.py: sT from def_a 0.012451, def_b 0.046729, 40960 shots; PLAN_UFSM.md.text line 13 "their pooled binomial sd 0.12 pp") | qia_runs/2026-10-24-fill-ufsm/ufsm.py |
| "their DD setting is not on record" | TRACED (sampler options cell is commented out in their notebook) | RESULT_UFSM.md.text |

## 20. recount_2604.27836 : KEEP
| number | how | source |
|---|---|---|
| "up to 3-4x with four QPUs"; four backends kingston, pittsburgh, fez, marrakesh | printed | paper text lines 36-37, 342-343 |
| Table 2: 2344.76 s (Kingston sequential), 956.48 s (Kingston parallel), 889.04 s (multi-QPU), SA 2.3 s and 213 optimal, Kingston rows 0 optimal | printed | paper text lines 487-504, 562 |
| 2.64x and 2.45x | RECOMPUTED 2344.76/889.04 = 2.637; 2344.76/956.48 = 2.451 | arithmetic |

## 21. free_2511.22324 : KEEP
| number | how | source |
|---|---|---|
| 200 shots, circuit duplicated 50 times, stated 10^5 | printed (Methods and Fig. 7 caption) | paper text lines 855-857, 475 |
| 10000 | RECOMPUTED 200 x 50 = 10,000 = 10^4 | arithmetic |

## 22. free_2502.13910 : KEEP
| number | how | source |
|---|---|---|
| f(r) = 2 - 2 Re of the overlap of psi_ideal and psi_out; "maximum possible value ... of two" | printed | paper text lines 214, 259-261 |
| range [0, 4], 4 when psi_out = -psi_ideal, 2 at zero real overlap | RECOMPUTED. The squared distance between two normalised states is 2 - 2 Re(overlap), so it runs from 0 to 4. Numeric check on 10^5 random normalised 2-level pairs: identity holds to 2e-15, min 2e-5, max 3.9994, mean 1.9989. a=(1,0), b=-a gives 4.0; b=ia gives 2.0 | own check |

## 23. free_2505.09371 : KEEP
| number | how | source |
|---|---|---|
| main text says "execute them on IBMQ-Brisbane device"; Appendix G says noise "in Qiskit" | printed | paper text lines 484-485, 1110 |
| Table 4 IBMQ-Brisbane error 2.8e-3 (best episode), 1.5e-3, 3.3e-3; chemical accuracy 1.6e-3 Ha | printed | paper text lines 1117-1120, 985, 1527 |
| 1.75 | RECOMPUTED 2.8e-3 / 1.6e-3 = 1.75 (3.3/1.6 = 2.06; 1.5e-3 is at or below: 1 of 3) | arithmetic |

## 24. und_fez : KEEP
| number | how | source |
|---|---|---|
| ibm_fez CZ 1.244 / 1.269 (1.24-1.27), sx 1.450 / 1.417 (1.42-1.45), 23 Oct 2026 | TRACED | qia_leads/audits/und_fez_2602.21253/AUDIT.md section 5 (line 43); raw: qia_runs/2026-10-29-gift-makesomenoise/noise_model_fez_calibration/fez_23oct_job1.text lines 8-9 and fez_23oct_job2.text lines 8-9 |
| their 1x-2x | TRACED: 40% of training samples drawn from synthetic models at 1x, 1.5x, 2x the backend's median gate and readout errors. 1.24-1.27 and 1.42-1.45 lie inside | qia_leads/audits/und_fez_2602.21253/src/paper.txt lines 911-914 |
| "no data released" | TRACED to the 24 Oct audit (paper prints no link for the "replication package", GitHub, Zenodo, Hugging Face searched). Not re-searched today | AUDIT.md section 0; paper.txt lines 805, 941 |
Note: the 1x-2x is a training-data arm, so "results across a 1x-2x noise sweep" in the Published cell is loose wording.

## 25. free_2209.05716 : KEEP
| number | how | source |
|---|---|---|
| Table I: Quito 5 qubits, Nairobi 7 qubits; T1, T2, first CNOT, readout, single-gate error | printed. CNOT is given for 4 + 6 qubits, so 24 + 34 = 58 numeric entries | paper text lines 374-389 |
| 58 entries, 56 match | RECOUNTED against their ibmq_quito_calibrations.csv and ibm_nairobi_calibrations.csv (paper ref [55], github.com/mx73/Testing-QM-on-NISQ, folder "Stronger Hardys quantum nonlocality theory and simulation/data"), readout x100, ID error x1e4, first CNOT x100, rounded half up. Script SCR/r24/cmp.py | their data |
| the two that differ | Quito Q4 T1 paper 69.45 vs CSV 56.12, Quito Q4 T2 paper 62.78 vs CSV 69.45 | their data |

## 26. free_2212.14170 : KEEP
| number | how | source |
|---|---|---|
| Table III (3 rows x 11 columns = 33 R2 cells); Eq. (35); "averaged from 4 runs" | printed | paper text lines 700-717, 619 |
| 27 of 33 | RECOUNTED from their released data (github.com/hanoipho997/Simulating-neutrino-oscillations-on-a-superconducting-qutrit, Data/Figure 3, 4, 5; repo was renamed) with my own numpy port of the theory in their notebooks (read as JSON, not run; parameters 33.45, 42.1, 8.62 deg, D21 7.42e-5, D31 2.510e-3; SCR/r25/r2count.py, table3.py). R2 of the 4-run average (Fig 3 and 5) or the single file (Fig 4), with Eq. 35 and the mean of the data. 27 cells equal my value rounded or truncated to the printed digits; 6 do not | their data |
| the 6 that do not | vacuum nu_mu(0) column x3 (printed 0.9975 / 0.9955 / 0.9955), matter Vm=1e-5 final nu_e (printed 0.999, mine 0.99848) and final nu_mu (printed 0.996, mine 0.99547), delta=pi final nu_e (printed 0.998, mine 0.98827) | their data |
| 3 vacuum cells match run 4 alone | RECOUNTED: run 4 alone gives 0.9975, 0.9955, 0.9955 exactly; the 4-run average gives 0.9951, 0.9851, 0.9839. (Their notebook averages runs 2-4 for nu_mu and says run 1 was run with other parameters, which gives 0.9976, 0.9953, 0.9945, also not the printed.) | their data |
| 19.1 | RECOMPUTED 12224/640 = 19.1 (paper prints 19.6) | paper text lines 737-738 |

## 27. free_2505.17731 : KEEP
| number | how | source |
|---|---|---|
| "nearly a 20% absolute increase" over 48.5%; Table 2 XOR: 48.5% (CNOT + Transpiler), 71.5% and 71.8% (topology-aware, fixed map) | printed | paper text lines 476-477, 480-484 |
| 23.0 and 23.3 points | RECOMPUTED 71.5 - 48.5 = 23.0; 71.8 - 48.5 = 23.3 | arithmetic |

## 28. recount_10.5281/zenodo.20688687 : FIX (the "132-sigma" sentence)
The Zenodo record is a code and data archive (35 files, no formal paper). Two different campaigns are in it.
| number | how | source |
|---|---|---|
| 0.4590, 24,000 shots, 267.2% | printed in vacuum_lock_evidence.json (final_p0 0.459, total_shots 24000, enhancement_percentage 267.2; counts 000 = 11016 from jobs 5493 + 5523) and in the vacuum_geometric_lock.pdf text ("267.20% above Chaos") | paper text lines 580-590, 797 |
| 3.672 | RECOMPUTED 11016/24000 = 0.4590; 0.4590/0.125 = 3.672; (3.672 - 1) x 100 = 267.2 | arithmetic |
| 132 | printed: title "132-Sigma"; read me.md says the 48k raw data "Verifies the 132.76 Sigma deviation"; Experimental_Data_Master_Final.csv has Sigma_Level 132.76 on four Exp_6_Resurrection rows (4 jobs x 12,000 shots, top state 000, top prob 0.3240, 0.3117, 0.3225, 0.3432). This belongs to the 48,000-shot campaign, not to 0.4590 | paper text lines 1399, 1720-1727 |
| "no shot count or width anywhere in the text, so it cannot be rebuilt" | FALSE. RECOUNTED from Raw_Data_48k_Shots.zip (their record; its central directory lists only 2 of 4 jobs, I carved all 4 with zlib and decoded the qiskit BitArray with numpy, no pickle; SCR/r27): four jobs x 12,000 = 48,000 shots; 000 counts 4119, 3870, 3888, 3740 = 15,617; P(000) = 0.32535 (jobs 0.34325, 0.32250, 0.32400, 0.31167, equal to the CSV). With the null width sqrt(1/8 x 7/8 / 48000) = 0.0015095: (0.32535 - 0.125)/0.0015095 = 132.73; with P(000) rounded to 0.3254 it is 132.76, the printed figure. With the width their own script final_48k_verdict.py uses, sqrt(p(1-p)/N) = 0.00214, it is 93.7 | their data |
Suggested: "132-sigma rebuilds from their 48,000 raw shots (P(000) = 0.3254) with the width sqrt(1/8 x 7/8 / N) = 0.0015. Their own script's width, sqrt(p(1-p)/N), gives 93.7. The 3.672x / 267.2% is a different 24,000-shot run (0.4590)." The F4 ask would then be "state which width the 132.76 uses".
