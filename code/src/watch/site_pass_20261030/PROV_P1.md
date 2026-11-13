# PROV lane P1, 30 Oct 2026 (read only, evidence only)

34 rows from /Users/heuremen/bones-forge/watch/site_pass_20261030/prov_lane1.json. Cells read from /Users/heuremen/bones-forge/qia_leads/matrix_page/book_calibrated.json.
Result: 29 KEEP, 4 FIX, 1 PULL.

Path legend (all under /Users/heuremen/bones-forge):
- SW = arxiv_one_readout/sweep_run (gate/readout sweep, raw .npz per chip)
- IND = arxiv_one_readout/industry_run
- QR = qia_runs
- AU = qia_leads/audits
- RP = qia_leads/recheck_published/src (cached paper text, named in the brief; for Zenodo rows it is the record text)
- Scratch = /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p1 (my scripts at top level, authors' downloads under data/, read with python3 -I, none of their code run)

Verdict key: TRACED = number in a kept file. RECOMPUTED = arithmetic on printed numbers. RECOUNTED = my own script on the authors' released data.

## Summary

| row id | verdict | one line |
|---|---|---|
| fresh_arclight_2609.11637 | KEEP | q109 readout ranges recounted from our raw sweep counts (3 records) |
| eviden_siemens_fez | KEEP | factors and 173-177 traced in kept README and sweep results |
| ibm_qaoa_tutorial | KEEP | 0.286 and interval recounted from raw counts, factors traced |
| free_2510.15316 | KEEP | all four means and the 10/13, 5/13 counts recomputed from Table I |
| qusmos_karlsruhe | KEEP | factors traced, 16-25 and 25-35 percent recomputed as 1 - 1/f |
| recount_10.5281/zenodo.20736911 | KEEP | 202 vs 206.3, p 0.40 and all baselines recomputed from Table 1 (precision note) |
| recount_10.5281/zenodo.22804814 | KEEP | +17.0 and +22.0 rebuilt from the printed Q matrix by enumeration |
| so_2610.28705 | KEEP | all five figures in the kept result file (wording note on "about a third") |
| so_2609.15411 | FIX | "1.3 times stated" is 1.36 times, so 1.4. Everything else traced |
| recount_10.5281/zenodo.22103070 | KEEP | all six closed-loop results and headline figures are in the released JSON |
| recount_2511.21932 | FIX | "6-30" upper bound is not derivable. Only minimum sizes 6 and 32 follow |
| recount_2603.28821 | KEEP | 4.8 + 69.8 + 28.6 = 103.2, counts 6 + 88 + 36 = 130 vs 126 |
| recount_2512.12645 | KEEP | 0.219, 6.8, 0.015, 2.4 recomputed from Table 2 and 156 from kept props |
| recount_2607.26756 | PULL | 279.55 / 404.66 / 0.281 need IBM's 21 Jul 2026 record, not in any kept file |
| recount_2508.05331 | KEEP | 0.003115, 0.01312, 93.27 recomputed |
| recount_2507.09532 | KEEP | mean 79.64, median 79.62, sd 3.096 from the ten printed fidelities |
| fill_2607.20377 | KEEP | ABBA 0.0234 [0.0218, 0.0250], drift 0.0029, 6.5 percent in kept result |
| recount_10.5281/zenodo.22172952 | KEEP | every figure recounted from released qpu_results.json and ibm_sim_reference.json |
| recount_10.5281/zenodo.23407123 | FIX | counts and chi2 20.3 recounted. "Consistent at 5%" for cos(8 phi) rests on the wrong df |
| free_2604.17486 | KEEP | 172 entries, means, medians, minima recounted from Tables 1-4 |
| recount_10.5281/zenodo.22790702 | KEEP | -46.9, 1.9, 16.6 recomputed, Tables II and III rebuild |
| recount_10.5281/zenodo.20840196 | KEEP | slope, bound and 1.1-2.2 percent recomputed (assumption note) |
| fire_pavani | KEEP | 0.1565 [0.146, 0.168] and 0.17-0.38 in kept result and raw counts |
| recount_10.5281/zenodo.22898763 | FIX | 0.499 depends on an unstated formula, "8 of 12" depends on an unstated tolerance |
| free_2604.24283 | KEEP | 287, 311, 247 and the gaps recounted from their released summary.json |
| free_2504.04021 | KEEP | means 5.77 and 4.50, max 14.81 and 9.30 recomputed from Table II |
| recount_10.5281/zenodo.22073993 | KEEP | closed form matched to 99 digits with decimal arithmetic |
| free_2505.21243 | KEEP | fractions and truncations recomputed against Table 2 |
| free_2511.15802 | KEEP | all percentages recomputed from Table 3 (inputs are rounded integers) |
| free_2603.18749 | KEEP | ratios recomputed from Table 3 |
| fire_tehran | KEEP | every figure in the kept result file and results_tele.text |
| free_2606.14933 | KEEP | every figure recounted from their released energy files |
| run_qfim | KEEP | 0.00433, interval, null band, 0.85 in kept result and qfim.py |
| recount_10.5281/zenodo.22242711 | KEEP | 167/205 and 85/93 reproduce printed values and Wilson intervals uniquely |

## Rows

### fresh_arclight_2609.11637 : KEEP
- P(0|1) 0.0050 to 0.0098, P(1|0) 0.0004 to 0.0036, q109, 23-24 Oct: RECOUNTED from our raw counts. Column 109 of $SW/raw_sweep_ibm_kingston.npz (23 Oct 16:02 record), _r2.npz (17:16), _r3.npz (24 Oct 07:48). Using sweep.py's circuit order (I1, I0, IQ, two copies): P(1|0) = mean of a in I0 and a in I1, P(0|1) = 1 - mean of b in IQ and in I1. Smallest and largest of the 3 records x 2 previous-state conditions: P(0|1) 0.0050 (r1, after |1>) to 0.00975 (r3, after |1>); P(1|0) 0.00038 (r3, after |0>) to 0.00362 (r1 and r2, after |0>). Rounds to the cell's figures. Script: Scratch/q109.py. The kept sweep_run/ADDENDUM and results text do not print q109, so the recount from raw is the trace.
- "below 1 percent" in both directions: holds on the point values (0.0098 is the top). Each point has binomial 95 percent half-width about 0.001 at 8000 shots, so the top of P(0|1) is not strictly under 1 percent at 95 percent. Wording note, not a number error.
- 5 percent symmetric model: TRACED, $AU/fresh_arclight_2609.11637/KNOWN_GOOD.md lines 14 and 24 (declared A = [[.95,.05],[.05,.95]]).
- IBM states 0.49 percent on q109: TRACED, KNOWN_GOOD.md line 26 and $AU/fresh_arclight_2609.11637/src/l7_repro_out.txt line 14 (stated readout_error 0.0049).
- 19/20 and 20/20: TRACED, KNOWN_GOOD.md section 1 table.

### eviden_siemens_fez : KEEP
- 220 and about 180: TRACED in the paper, $RP/eviden_siemens_fez.txt lines 900-902.
- 220 / 180 = 1.22: RECOMPUTED, 1.2222.
- 1.24 to 1.27 (CZ, ibm_fez): TRACED, $SW/results_sweep_3.text line 9 (1.244) and $SW/results_sweep_r2_part.text line 9 (1.269). Also $QR/2026-10-29-gift-makesomenoise/README.md line 15.
- 173 to 177: RECOMPUTED, 220 / 1.269 = 173.4 and 220 / 1.244 = 176.8. Printed the same way in README.md line 22.

### ibm_qaoa_tutorial : KEEP
- 0.286 and 95 percent binomial interval [0.277, 0.295]: RECOUNTED from $IND/run_tqaoa_ibm_kingston.json counts (10,000 shots, cut value 5 is optimal on the tutorial's 5-node graph): 0.2860, normal interval [0.2771, 0.2949]. Printed in $IND/results_tqaoa_ibm_kingston.text lines 24 and 29 as [0.2772, 0.2950]. Script: Scratch/qaoa.py.
- 0.330 (forecast, in the published cell): TRACED, same file line 25 and 29 (0.3301).
- 1.31 to 1.37 (sx) and 1.30 to 1.31 (CZ), kingston: TRACED, $SW/results_sweep_3.text lines 20-21 (sx 1.306, CZ 1.302) and $SW/results_sweep_r2_part.text lines 20-21 (sx 1.366, CZ 1.311), both 23 Oct, before the 22:06Z tutorial run. Note: the third kingston record (24 Oct 07:48) reads sx 1.344, CZ 1.345 ($SW/results_sweep_ibm_kingston_r3.text lines 8-9), outside the CZ range, but it is the next morning.

### free_2510.15316 : KEEP
All from Table I in $RP/free_2510.15316.txt lines 528-545 (the extracted columns are run together, parsed by the 3-decimal rule, MD column cross-checked against the text values 0.79, 1.616, 1.826, 5.11, 5.32). Script: Scratch/prot.py.
- 13 peptides: counted, 13 rows.
- IBM mean 3.62: RECOMPUTED, mean of the Mean column = 3.616.
- SA 2.59: RECOMPUTED, 2.585.
- MD 2.94: RECOMPUTED, 2.945 (2.9448).
- SA beats IBM mean in 10 of 13, MD in 10 of 13, SA beats IBM minimum in 5 of 13: RECOMPUTED, 10, 10, 5.
- Prion peptide 4TUT SA 0.731 vs IBM minimum 3.115: read straight from Table I.
- "best structure picked against the experimental coordinates": TRACED to the Figure 6 and 7 captions (minimum RMSD structure within the minimum free energy bin).

### qusmos_karlsruhe : KEEP
- CZ 1.24 to 1.27 and sx 1.42 to 1.45, ibm_fez: TRACED, $SW/results_sweep_3.text lines 8-9 (sx 1.450, CZ 1.244) and $SW/results_sweep_r2_part.text lines 8-9 (sx 1.417, CZ 1.269).
- 16 to 25 percent (CZ) and 25 to 35 percent (sx): RECOMPUTED as 1 - 1/f over both jobs' intervals: CZ 1 - 1/1.191 = 16.0 to 1 - 1/1.338 = 25.3; sx 1 - 1/1.336 = 25.1 to 1 - 1/1.534 = 34.8. Also printed in $AU/qusmos_2605.04099/out/qusmos_model_check.txt (projection block) and AUDIT.md line 47.
- "order 10^-2": TRACED, $RP/qusmos_karlsruhe.txt line 19.

### recount_10.5281/zenodo.20736911 : KEEP
Table 1 at $RP/recount_10.5281_zenodo.20736911.txt lines 107-260. Script: Scratch/ecdlp.py.
- 1 of 500,000 = 0.0002 percent: 1/500000 = 0.0002 percent, printed in the table.
- Hit rates rebuild: all 14 printed rates equal hits/shots.
- 202 hits on 9-18 bit runs: RECOMPUTED, 51 + 75 + 38 + 16 + 12 + 4 + 1 + 2 + 1 + 1 + 1 = 202.
- 206.3 expected: RECOMPUTED, sum of shots/n over the same rows = 206.29.
- Poisson p 0.40: RECOMPUTED, P(X <= 202 | 206.29) = 0.4001. This is the one-sided lower tail. Two-sided is 0.81.
- 18-bit 1 vs 3.8, 17-bit 1 vs 1.5: RECOMPUTED, 500000/130579 = 3.83, 100000/65173 = 1.53.
- 4-7 bit: 96 vs 714, 583 vs 645, 565 vs 633: RECOMPUTED, 5000/7 = 714.3, 20000/31 = 645.2, 50000/79 = 632.9. Hits 96, 583, 565 are the printed values.
- Precision note: shots/n is the first-order chance level. With a and b uniform and n prime the exact level is shots (n - 1)/n^2: 612, 624, 625 for the three small runs and 205.8 for 9-18 (p 0.41). Conclusion unchanged. If a one-word hedge is wanted, "about shots/n".

### recount_10.5281/zenodo.22804814 : KEEP
Printed Q matrix at $RP/recount_10.5281_zenodo.22804814.txt section 5.2 (diagonal 2.0, -4.0, 0.5, 9.0, -3.0; off-diagonal 3.0, -1.5, 2.0, 0.5, 0.5, 10.0, -2.5, -1.0, 0.5, 1.0). Enumerated all 32 bitstrings. Script run inline (Scratch not saved as file, five lines).
- "Everything" [1,1,1,1,1]: +17.0 (printed +26.5 at lines 509 and 629).
- Worst case [1,1,0,1,0] = 11010: +22.0 (next worst +20.5, +18.0).
- 10 hardware rows' costs and the optimum -9.5: all rebuild. Counts 365 ... 47 of 2000 give the printed percentages within 0.05.

### so_2610.28705 : KEEP
- +0.0066 (99 percent half-width 0.0149), twirl-set -0.0092 (0.0167), +0.0230 (0.0084): TRACED, $QR/2026-10-24-fill-kumar-kingston/RESULT_KUMAR_KINGSTON.md.text lines 3-6. Band is two-sided t(19) at 99 percent, $QR/2026-10-24-fill-kumar-kingston/analyze_kumar.py line 11.
- +0.0561 (0.9058 to 0.9619): RECOMPUTED, 0.9619 - 0.9058 = 0.0561.
- "about a third": same file line 8 says "roughly a third". The half-widths are 27 and 30 percent of 0.0561. If the guard is added to the twirl-set bound (0.0167 + 0.0107) it is 49 percent. Wording note. The qia_calibration "bounded at +/-0.0149" is the half-width of an interval centred on +0.0066, so drift lies in [-0.0083, +0.0215]. Consider "with 99 percent half-width 0.0149".

### so_2609.15411 : FIX
- "1.3 times stated" is wrong. Delivered 0.012604 (packed, prep 0, 4 jobs, 65,536 shots) over stated 0.009277 (props 0.00927734375) = 1.3586. Printed 0.0126 / 0.0093 = 1.355. Both round to 1.4. The "x1.3" in $QR/2026-10-24-fill-zhukov/RESULT_ZHUKOV.md.text line 5 was truncated. Recount: Scratch/zh1.py using $QR/2026-10-24-fill-zhukov/zhukov.py and the raw_zhukov_*.npz. Right wording: "1.4 times stated" (or "1.36 times"). Two places: the measured cell and the qia_calibration cell.
- 0.766: TRACED, zhukov.py line 327 (solo prep 0, 0.7657).
- 0.0126 [0.0115, 0.0138] (99 percent) vs 0.0093: TRACED, $QR/2026-10-24-fill-zhukov/results_zhukov.text line 1.
- median chi2/dof 0.79, band [0.72, 0.89]: TRACED, results_zhukov.text B_WITHIN 0.7919 [0.7154, 0.8922]; the band is the 0.5 and 99.5 percentiles of the shot-permutation null (zhukov.py line 194).
- -46.8 +/- 4.1, his +46.3 (se 2.5), -9.3 +/- 3.8, +37.4 +/- 5.6: TRACED, $QR/2026-10-29-repeat-zhukov/results_date.text line 1. Half-widths are 99 percent (z 2.576, zhukov.py line 28 and combine at line 78); 5.6 = hypot(3.8, 4.1) = 5.59 (date_reading.py line 19).
- 29 Oct 0.0089 [0.0080, 0.0099], stated 0.0132 to 0.0159: TRACED, $QR/2026-10-29-repeat-zhukov/results_zhukov_r2.text line 1.

### recount_10.5281/zenodo.22103070 : KEEP
The cached record text holds the released JSON: $RP/recount_10.5281_zenodo.22103070.txt lines 921-1010 (closed loop), 1155-1176, 1195-1217, 1355-1361.
- +148/+163/+783 percent: improvement_pct 148.37 (marrakesh), 163.12 (fez), 783.17 (kingston); each equals F_mitigated / F_raw - 1.
- -49/-50/-58 percent: -48.79 (kingston), -50.46 (fez), -57.94 (marrakesh); pass_15pct false on all.
- F_raw 0.81/0.95/0.78 to F_mitigated 0.40/0.40/0.40: 0.808972/0.948497/0.784158 to 0.400792/0.398894/0.401531.
- 13.73: eff_rank 13.7266. SCI 0.9996: 0.999638. 5.93x: comp 5.93 at k = 8. r 0.6302 and n 209: r 0.630195, n 209. z 10.98: 10.9788.
- "verdict closed_loop PASS": printed at line 1008.
- Note: the release is summary JSON only (no source). "Rebuild" here means the printed headline values match the JSON and the percentages match F_mitigated / F_raw. The rank, SCI, r and z cannot be recomputed from raw data.

### recount_2511.21932 : FIX
Paper prints Table III at $RP/recount_2511.21932.txt lines 337-340: Bot IoT 0.8333 / 0.8809 / 0.8333 / 0.8333, IoT23 0.8437 / 0.7500 / 0.7500 / 0.7447. No test-set size is printed. Scripts: Scratch/qae2.py.
- 0.8333 = k/n: n must be a multiple of 6 (6, 12, 18 ...). With the printed precision 0.8809 as a weighted average (printed figures are truncated: 0.88095 prints as 0.8809), n must be a multiple of 12. No upper limit.
- 0.8437 = 27/32: n must be a multiple of 32. No upper limit. No single-averaging binary confusion matrix reproduces the IoT23 row for any n up to 160.
- "6-30": NOT FOUND. No printed number gives an upper bound of 30. The original recount file (qia_leads/recounts/2511.21932_recount.md) was deleted 25 Oct. 6 and 32 are minimum sizes.
- "steps of 3 to 17 points": RECOMPUTED, 1/32 = 3.1 points and 1/6 = 16.7 points, at the smallest sizes.
- Suggested replacement for the measured cell: "Counts are not released. The printed accuracies fit test sets of 6, 12, 18 ... samples (Bot IoT, 0.8333 = 5/6) and 32, 64 ... samples (IoT23, 0.8437 = 27/32)." And for the calibration: "At the smallest test sets the accuracies allow (6 and 32 samples) one sample moves accuracy by 17 and 3 points."
- Averaging rule claim (Bot IoT recall = accuracy, IoT23 recall 0.75 not equal to accuracy 0.8437) is in the printed table and needs no number.

### recount_2603.28821 : KEEP
Table I at $RP/recount_2603.28821.txt lines 376-402. Five-ones block, Run 1, HAMMR-L: 4.8 + 69.8 + 28.6 = 103.2.
- 126: C(9,5) = 126 permutations (text lines 291-298: "all of the permutations"). Every other five-ones column (QBEEP run 1, HAMMR-L run 2, QBEEP run 2) sums to 100.0 and equals k/126 within rounding.
- 6 + 88 + 36 = 130: RECOMPUTED, 4.8, 69.8, 28.6 percent of 126 = 6.05, 87.95, 36.04.
- Every column in the whole table sums to 100.0 (checked all 20 columns) except this one.

### recount_2512.12645 : KEEP
Table 2 at $RP/recount_2512.12645.txt lines 449-460.
- 0.963 + 0.000 = 0.963 and 0.001 + 0.743 = 0.744: RECOMPUTED.
- 0.963 to 0.744 moves 0.219: RECOMPUTED, 0.963 - 0.744 = 0.219.
- 6.8 widths: RECOMPUTED, 0.219 / hypot(0.005, 0.032) = 6.76.
- Aer 0.015 and 2.4 widths: RECOMPUTED, 0.988 - 0.973 = 0.015, 0.015 / hypot(0.002, 0.006) = 2.37.
- 27-qubit in text (line 472) and 156 qubits: 156 TRACED, $SW/props_sweep_ibm_fez.json has 156 qubits.

### recount_2607.26756 : PULL
- "127-qubit Eagle r3" in the paper: $RP/recount_2607.26756.txt line 388 (ibm_marrakesh, 2026-07-21, qubit 2, T1 = 280 us, T2 = 405 us, readout 0.28 percent). 156 qubits: TRACED, $SW/props_sweep_ibm_marrakesh.json (156 qubits).
- T1 279.55, T2 404.66, readout 0.281 percent "match IBM's 21 Jul 17:16 record exactly": NOT FOUND. The paper prints only the rounded 280 / 405 / 0.28. The unrounded figures and the 17:16 timestamp come from an IBM historical-properties record for ibm_marrakesh that no kept file holds (checked: qia_runs, qia_leads/audits, arxiv_one_readout, public_mirror code/qia-runs, our Zenodo record 23662284 which starts 24 Sep; a whole-tree grep for 279.55 hits only ledger copies, THE_BOOK.md and unrelated files). The paper cites no data or code. I did not call IBM's API with the stored key, since the brief names authors' public data only.
- What would settle it: one zero-QPU historical-properties call for ibm_marrakesh qubit 2 at 2026-07-21 17:16 EDT. If it returns 279.55 / 404.66 / 0.281 the row is KEEP.
- If pulled to what is traceable: "The paper calls ibm_marrakesh a 127-qubit Eagle r3. It has 156 qubits," and the F6 line stays.

### recount_2508.05331 : KEEP
Paper lines 625-674 ($RP/recount_2508.05331.txt).
- 12 x 2.596e-4 = 0.003115 (printed 0.002755): RECOMPUTED, 0.0031152.
- 2 x 6.560e-3 = 0.01312 (printed 0.01389): RECOMPUTED.
- 93.27 percent: RECOMPUTED, exp(-(0.0031152 + 0.01312 + 0.0534)) = 0.93273, with their measurement term 0.0534. With their own wrong products it would be 93.24.
- 94.79 percent headline: printed, equals exp(-0.0534) = 0.9480 (truncated), i.e. measurement term only.

### recount_2507.09532 : KEEP
Ten fidelities at $RP/recount_2507.09532.txt lines 1868-1872: 79.31, 77.51, 78.98, 84.64, 76.17, 83.64, 81.33, 80.21, 79.92, 74.65.
- mean 79.64: RECOMPUTED, 79.636. median 79.62: RECOMPUTED, 79.615. sd 3.096: RECOMPUTED, sample sd 3.0963. max 84.64 = the headline. 79.31 and 74.65: first and last values printed.
- Table 2.1 (line 1928): CNOT errors direction-symmetric, T2 <= 2 T1 for all 7 qubits: checked by hand, holds.

### fill_2607.20377 : KEEP
- Twirl gap 0.0234 [0.0218, 0.0250] (95 percent): TRACED, $QR/2026-10-24-fill-kyiv/RESULT_KYIV.md.text line 9 (+0.02337 [+0.02180, +0.02501]); 95 percent per kyiv.py lines 4 and 34-35.
- |drift| <= 0.0029, 6.5 percent of their gap, 3.6 minutes: TRACED, same file lines 5-6. 0.00293 / 0.0451 = 6.50 percent.
- Their 0.0451 and RMSE 0.0878 vs 0.0427: RECOMPUTED, 0.0878 - 0.0427 = 0.0451 on printed values ($RP/fill_2607.20377.txt line 14). Unrounded they are 0.08777 - 0.04273 = 0.0450 (kyiv.py line 12), still under 6.5 percent.
- Our twirl gap 0.023 against 0.045: same.

### recount_10.5281/zenodo.22172952 : KEEP
RECOUNTED from Zenodo 22172952 file recoverability-criticality-v1.6.1.zip (prelab/qpu_results.json, prelab/ibm_sim_reference.json). Scratch/data/z22172952.
- 0.8347 - 0.8116 = 0.023 at r = 0.95: QPU F_petz 0.834656 minus reference 0.811643 = 0.02301. Every other r differs by 0.0005 to 0.0153 (r = 0.2, 0.5, 0.8, 1.0, 1.05, 1.2, 2.0, 4.0), so the 0.02 bound fails at r = 0.95 only.
- EP band: r = 0.95, 1.0, 1.05. sigma 0.00776 (mean 0.007756), anchor r = 0.2 0.00195 (0.0019466), ratio 3.98 (3.9845). Printed 4.0x in prelab/REPORT_QPU.md line 8.
- Petz band 0.8285 (0.828454) vs flanks r = 0.5/0.8/1.2/2.0 mean 0.8355 (0.835473), difference -0.007 (-0.00702). Printed in REPORT_QPU.md line 10.
- 0.02 claim: REPORT_QPU.md line 12 ("dif <= 0.02 em todos os r").

### recount_10.5281/zenodo.23407123 : FIX
RECOUNTED from Zenodo 23407123 (quantum-anchor-v1.2.2.zip, measurement_raw/iqm_tesseract_v3_*.json). Scratch/data/z23407123.
- 13, 3, 2, 14, 3 of 1,024: counts of 00000000 plus 11111111 per phase (6+7, 3+0, 2+0, 7+7, 1+2). Their Wilson intervals rebuild exactly.
- 35 of 5,120 = 0.684 percent, interval [0.49, 0.95]: 0.6836, Wilson [0.492, 0.949].
- chi2 vs flat on percentages 1.98: 1.9810 reproduces the printed line. On counts: 142/7 = 20.29, p = 0.00044 at df 4 (flat model, mean fitted, df 4 is right). Cell figures 20.3 and p = 0.0004 match.
- chi2 vs cos(8 phi) on counts 8.53: 8.5306, using their least-squares fit (analyze_5phase_final.py: offset 0.6836, amplitude 0.5114 percent), p = 0.074 at their df 4.
- Problem: the cos model has two fitted parameters on five points, so df is 3 (or 2), not 4. p = 0.036 at df 3 and 0.014 at df 2. Even the best-case fit (minimum Pearson chi2 over both parameters, 8.06) gives p = 0.045 at df 3. Expected counts are also small (2.8 to 12). So "CONSISTENT at 5 percent" is not supported. The qia_calibration line (flat, 20.3, df 4, p = 0.0004) is fine.
- Suggested replacement for the last two measured sentences: "On counts, chi2 vs cos(8 phi) = 8.53 (p = 0.074 at their df of 4, 0.036 at df 3 for the two fitted parameters), with expected counts as low as 2.8." Drop "CONSISTENT at 5%".

### free_2604.17486 : KEEP
Tables 1-4 at $RP/free_2604.17486.txt lines 499-745, parsed by regex, three IDs with a space inside the PDF text (1A VU, 1CW A, 1R W5) added by hand. Script: Scratch/ctqw.py.
- 172 distinct PDB entries: 172 rows, 172 distinct IDs.
- Means 0.941 / 0.861 / 0.956 / 0.922: 0.94107, 0.86106, 0.95581, 0.92151.
- Medians 0.964 / 0.867 / 1.000 / 1.000. Minima 0.582 / 0.491 / 0.700 / 0.538. All match.
- "150" in the abstract and "around 150" in the body: lines 13 and 399.

### recount_10.5281/zenodo.22790702 : KEEP
Printed at $RP/recount_10.5281_zenodo.22790702.txt lines 486-487 and Tables II and III (lines 387-450).
- 0.9746 +/- 0.0242 to 0.5175 +/- 0.0130: printed values. -46.9 percent: RECOMPUTED, 0.5175 / 0.9746 - 1 = -0.4690. +/- 1.9 percent: ratio error 0.0188. 16.6 sigma: (0.9746 - 0.5175) / hypot(0.0242, 0.0130) = 16.64.
- Their -49.1 percent / 2.9 percent / 17.1 sigma are the printed values the cell replaces.
- Tables II and III deviations rebuild: all 14 deviations (+40.2 ... +36.4 and +8.8 ... +2.3) and both weighted means (1.3171 +/- 0.0239, 0.9746 +/- 0.0242) recomputed.

### recount_10.5281/zenodo.20840196 : KEEP
Table 1 at $RP/recount_10.5281_zenodo.20840196.txt lines 47-52: counts 756, 738, 752, 749, 767, 744 of 1,000 at delays 0, 0.5, 1.0, 1.5, 2.0, 3.0 us.
- Weighted slope +0.0005 +/- 0.0057 per us: RECOMPUTED with binomial weights, +0.000475 +/- 0.005676.
- [-0.033, +0.035] over 3 us at two standard errors: 3 x (0.000475 -/+ 0.011351) = [-0.0326, +0.0355].
- 1.1 to 2.2 percent for T1 100 to 200 us: RECOMPUTED as the 0.756 baseline x (1 - exp(-3/T1)): 2.23 percent and 1.13 percent. Assumption: decay of the survival amplitude, not of a bare |1> population (the bare value is 3.0 to 1.5 percent). T1 100 to 200 us is an assumed range: ibm_fez median T1 in our 23 Oct record is 131 us, 10th to 90th percentile 74 to 191 us ($SW/props_sweep_ibm_fez.json). Suggest naming the model: "a plain qubit with T1 100 to 200 us keeps 98 to 99 percent of its amplitude".

### fire_pavani : KEEP
- 0.1565 [0.146, 0.168] (95 percent Wilson), ibm_fez best path: TRACED, $QR/2026-10-25-fire-pavani/RESULT_PAV.md.text line 5 (and line 3, 641/4096 = 0.1565); Wilson recomputed [0.1457, 0.1679].
- 0.17 to 0.38 on other paths: TRACED, same file lines 6-8 (0.1667, 0.3838, 0.2166); confirmed in $QR/2026-10-25-fire-pavani/results_pav.text (p1 values 0.16675, 0.38379, 0.21655).
- 0.125: ideal, line 4.

### recount_10.5281/zenodo.22898763 : FIX
RECOUNTED from Zenodo 22898763 (synthetic-hamiltonian-engineering-v.1.0.0.zip, raw_hardware_tomography_data.csv). Scratch/data/z22898763.
- The release states no formula for Fidelity_Mode. I tested F = (1 + |ZZ| + |XX| + |YY|)/4 and the signed singlet form (1 - ZZ - XX - YY)/4. They agree on 10 of 12 rows and differ on EXP-01 and EXP-11.
- EXP-01: 0.499 (abs form, 0.49905) or 0.495 (signed form) against 0.00598 printed. The cell's 0.499 needs the abs form named.
- "8 of 12 rebuild": true at a tolerance of 0.0005 (EXP-02 to 06, 08, 09, 12 rebuild; EXP-01, 07, 10, 11 do not). At 0.00015 only 6 rebuild, at 0.0006 EXP-10 (0.4733 vs 0.4739, miss 0.00058) joins and it is 9 of 12. So the count depends on the tolerance.
- EXP-07: 0.8548 vs 0.8047 printed. EXP-11: 0.4135 (abs) or 0.092 (signed) vs -0.0112 printed.
- Suggested replacement: "Taking the fidelity as (1 + |ZZ| + |XX| + |YY|)/4, 8 of 12 rows rebuild to within 0.0005. EXP-01 gives 0.499 (0.495 with the signed form) against 0.006 printed." The calibration line "four tomography rows" stands (EXP-01, 07, 10, 11) with EXP-10 marginal.

### free_2604.24283 : KEEP
RECOUNTED from GitHub SMU-Quantum/autoqresearch (main at fetch), hardware_runs/results_hardware/cvrp/e13_autoq_20260413T054007Z/summary.json. Scratch/data/gh_smu.
- 287.0: best_result.routed_cost. 247: optimal_reference_cost 246.99999843. 311.0: classical_greedy_route_cost (summary.json line 27052).
- gap 0.139373: best_result.optimality_gap 0.1393728, also cvrp_results/suite_results.tsv. (287 - 247)/287 = 0.13937 and 40/287 = 0.1394. 64/311 = 0.2058, published 0.205788.
- Conventional gaps: 287/247 - 1 = 0.1619 (0.16194); 311/247 - 1 = 0.2591 (0.25911).

### free_2504.04021 : KEEP
Table II at $RP/free_2504.04021.txt lines 470-483.
- Torino 0.91 ... 14.81: mean 5.77, max 14.81 at p = 10 only. Marrakesh 2.51 ... 7.40: mean 4.50 (4.502), max 9.30, one negative row (-3.09). All RECOMPUTED. "over 14%" sentence at line 487.

### recount_10.5281/zenodo.22073993 : KEEP
The cached record text holds the released files ($RP/recount_10.5281_zenodo.22073993.txt lines 1-100). Decimal arithmetic at 120 digits, Scratch inline.
- phi_esk_max 2.8287340381868885...: ln(33) x (1 - (1 - 1/phi)/2) agrees with the printed 100-digit value for 99 digits after the point (cell says 50, which is conservative).
- 3.07e-4 above 2 sqrt 2: printed value minus 2 sqrt 2 = 3.0691e-4.
- shannon_entropy = ln(8192): agrees to about 96 digits. 8,192 shots and 8,192 unique states printed.

### free_2505.21243 : KEEP
Bounds printed at $RP/free_2505.21243.txt lines 268-290; Table 2 lines 307-313.
- 17/18 = 0.9444, 14/15 = 0.9333, 8/9 = 0.8889, 13/15 = 0.8667 (doily and EYYY), 11/15 = 0.7333: RECOMPUTED.
- sigma_NISQ 0.94, 0.93, 0.88, 0.86, 0.86, 0.73: each is the bound truncated to two decimals. 0.88 < 0.8889 and 0.86 < 0.8667 cannot be rounding of the bound (rounds to 0.89 and 0.87). Pl square, pl doily, llll EYYY sit inside rounding.

### free_2511.15802 : KEEP
Table 3 at $RP/free_2511.15802.txt lines 380-386 (all entries are rounded integers).
- Marrakesh 14/7/16 over 18/11/20 = 77.8, 63.6, 80.0 percent. Kyiv 15/9/16 = 83.3, 81.8, 80.0. Fez C6 5/11 = 45.5 (range 4.5/11 to 5.5/11 = 40.9 to 50.0), C7 15/20 = 75. Brisbane C5 14/18 = 77.8. IonQ Aria1 12/18 = 66.7. All RECOMPUTED. 45 to 83 percent range checks out.
- Note: because the printed advantages are rounded integers, each ratio carries about plus or minus 3 points (Marrakesh C5 spans 73 to 83 percent). The cell only gives that range for Fez C6.

### free_2603.18749 : KEEP
Table 3 at $RP/free_2603.18749.txt lines 273-278 and text line 290.
- AHO L=8: RL0 76 s, RL1 96 s (x1.263), RL2 86 s (x1.132). HO 8: 30 s vs 31 s (x1.033). DW 4 3 14: 107 s vs 69 s (x0.645). RECOMPUTED.
- Totals 1632/532 = 3.07 and 2408/532 = 4.53: RECOMPUTED. Job counts 7, 17, 28 = totals / per-job usage (532/76, 1632/96, 2408/86), also the Iters column.

### fire_tehran : KEEP
- f = 1.045 +/- 0.060, 1.043 +/- 0.025; f - 1 = +0.045 [-0.073, +0.164] and +0.043 [-0.006, +0.092]: TRACED, $QR/2026-10-25-fire-tehran/RESULT_TELE.md.text lines 6-7 (THEIRS and f - 1).
- Native fidelity +0.024 and +0.026, 95 percent [+0.007, +0.042] and [+0.012, +0.040]: TRACED, same file line 9 and $QR/2026-10-25-fire-tehran/results_tele.text ci95 0.006922 to 0.041533 and 0.012226 to 0.040329. 3.5 minutes: line 8.
- Three chains 1.045 / 0.883 / 0.856 (p 0.037) and 1.043 / 0.941 / 0.890 (p 0.00025): TRACED, line 13 of the same file (both circuits).

### free_2606.14933 : KEEP
RECOUNTED from GitHub MSRG/LUCJSQDInitializationAnalysis (main at fetch): machine_learning/injection/DDLUCJ-experiment-pipeline/energies/*.txt (1,080 energy files = 12 molecules x 3 bases x 5 depths x 6 initializations) and classical/energies.csv (the SCI rows are their HCI reference). Scratch/data/msrg_subset, scripts Scratch/lucj.py, lucj2b.py.
- Share within 1.6 mEh of the CCSD-initialised energy: STO-3G 55.00 (zeroes) to 63.33 (ML_exact); cc-pVDZ 65.00 (zeroes) to 81.67 (MP2); aug-cc-pVDZ 88.33 (zeroes) to 98.33. Cell: 55 to 63, 65 to 82, 88 to 98. Match, and the STO-3G and aug figures are also printed in the paper (lines 408-410).
- Mean |E - E_CCSD|, zeroes: 57.55, 16.66, 0.82 mEh. Exact.
- MAE against HCI: zeroes 21.87, 6.13, 0.27; CCSD 79.01, 22.68. Exact, and printed in the paper (lines 441-445).
- 49x and 14x chemical accuracy: 79.01 / 1.6 = 49.4, 22.68 / 1.6 = 14.2.

### run_qfim : KEEP
- Job-to-job sd 0.00433 [0.00268, 0.00613]: TRACED, $QR/2026-10-24-fill-qfim/results_qfim_kingston.text line 2 (95 percent per qfim.py line 11).
- Shot-noise null [0.00248, 0.00596], 99 percent, 2000 redraws: TRACED, same line; qfim.py line 80 (0.5 and 99.5 percentiles for the R1 null) and B = 2000 at line 68.
- 0.85: $QR/2026-10-24-fill-qfim/results_qfim_kingston.text line 14 (0.850), also RESULT_QFIM_KINGSTON.md.text line 6. Shot floor 0.794.
- "all 8 published means and standard deviations": R0 line 1 (8/8).

### recount_10.5281/zenodo.22242711 : KEEP
Table XII at $RP/recount_10.5281_zenodo.22242711.txt lines 1530-1544. Script inline.
- 0.815 [0.756, 0.862]: 167/205 gives 0.8146 and Wilson [0.756, 0.862]; it is the only (k, n) with n up to 450 that reproduces both the printed value and the printed interval.
- 0.914 [0.839, 0.956]: 85/93 = 0.9140, Wilson [0.839, 0.956], also unique.
- 0.815 and 0.914 are not k/450 (366.75 and 411.3).
- Availability cells 0.960, 0.864, 0.969, 0.896: 432/450, 389/450, 436/450, 403/450 reproduce the printed values and intervals (other n would also fit three of them, but n = 450 does for all four, consistent with the caption).

## Methods notes
- Authors' data fetched (public, 30 Oct 2026): Zenodo 22172952, 23407123, 22898763; GitHub SMU-Quantum/autoqresearch and MSRG/LUCJSQDInitializationAnalysis (main branch zips). Held in the scratch folder only. Their code was read as text, never run. The 4.5 GB MSRG tree was reduced to the energy files and classical/energies.csv after use.
- Our own raw data used: sweep_run raw .npz (kingston r1, r2, r3), industry_run counts, the zhukov raw .npz via the kept zhukov.py module (imported read-only, no bytecode written).
- No file outside the scratch folder and this report was edited.
- Not done: IBM API call for row recount_2607.26756 (see that row).
