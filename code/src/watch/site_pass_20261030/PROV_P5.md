# PROV lane P5, 30 Oct 2026 (34 rows, read only, evidence only)

Rows from /Users/heuremen/bones-forge/watch/site_pass_20261030/prov_lane5.json. Cells read from /Users/heuremen/bones-forge/qia_leads/matrix_page/book_calibrated.json.

Conventions
- Paths are under /Users/heuremen/bones-forge/ unless they start with /. Line numbers are of the file named.
- "paper text" = qia_leads/recheck_published/src/<id with / replaced by _>.txt, or the audit's or run's own src/paper.txt.
- SCR = /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/ (my scripts, and authors' public files fetched for recounts, one subfolder per row, e.g. SCR/r06/). Their files were read as data with python3 -I. None of their code was run.
- TRACED counts only in the row's own material: its audit folder, its run folder, its cached paper text, our sweep_run / industry_run where the cell cites our gate factors, or the authors' released data. THE_BOOK.md, the ledger and book_calibrated.json were used only to find rows, never as proof.
- Every "source:" / "grep:" pair below was checked by script (SCR/check_greps.py, byte search on the file): all hit. Some paper texts carry NUL bytes from PDF extraction, so search them with grep -a.
- No IBM or other paid API call was made. No file outside SCR and this report was edited.

## Summary: 21 KEEP, 13 FIX, 0 PULL

No row needs pulling: every number in every cell traced, recomputed or recounted. The FIX rows are wording, one miscount (boussahi 21 of 21 is 22 of 22), a number given to the wrong chip (multipliers 1.91x), a mixed-up interval (nikhef 23-75%), and claims that rest on an inference or a missing scope (nus_zib shots, protein_qsad record date, so_2610.18124 patch). Suggested replacement text is in each FIX block (lines starting "Suggested").

| # | row id | verdict | one line |
|---|---|---|---|
| 1 | fire_2608.04486 | KEEP | 120 +/- 40, [41, 199], [12, 228], exact 240 traced in the run folder. Their 200 = 236 - 36 recomputed from the paper and their released JSON |
| 2 | recount_10.5281/zenodo.20162808 | KEEP | definition F = P(0...0) + P(1...1), Z-basis-only circuit and parity, 88%, 89.4% to 83.7% all in the record text |
| 3 | nus_zib_2609.17497 | FIX | one cell over 100,000% and 20 of 45 recounted from Table 1, but both rest on shots we inferred (not printed). At twice the shots it is 4 counts and 18 of 45 |
| 4 | free_2512.18493 | KEEP | Tables III and IV print C0-C9, C5-C9 equal C0-C4 in all four metrics, Table I defines eight (C1-C8) |
| 5 | recount_2511.17692 | FIX | the sentence and 8 x 4 = 32, 12 = 3 x 4 hold. The "how" cell says "released data" while the measured cell says none is released (none is) |
| 6 | kisti_2609.35163 | FIX | 1.04 [0.90, 1.17] recomputed from Table 2. 2 of 5 recounted from the PDF's vector Fig. 5. But the five are observable groups, not "pair classes" |
| 7 | k2026_kobe_2603.13536 | KEEP | -0.930 [-1.208, -0.653], -0.112 [-0.378, +0.154], 10 instances, 97.5% traced. D2 mean rebuilt from per-seed values. 2.4x and 1.4x recomputed |
| 8 | recount_10.5281/zenodo.19754086 | KEEP | Phase 4 receiver: ancilla reads 0 for both bits (97.99% vs 97.93%), Phase 4v2 the same. Optional note on the Phase 5 claim |
| 9 | k2025_marmara_2512.14280 | KEEP | 1.808 +/- 0.017 (bootstrap sd) on fez DD on traced in our run folder. 1.279 / 0.701, 2.30 / 1.56, 1.45E-2 vs 1.477E-2 traced in the audit |
| 10 | so_2610.21761 | KEEP | chi2/N 6.0-47.3 at lambda = 1 and lambda 1.34-1.95 printed in Table I and Sec. IV G |
| 11 | recount_2512.21914 | FIX | 0.907 vs 0.904 traced. But the paper does state the simulator: "ideal noiseless". Its own simulation counts put 9.5% of shots outside the two allowed states, so that statement is what fails |
| 12 | nus_lanzhou_2610.22482 | KEEP | +0.034 to +0.070 on 12 points and 0.833-0.871 traced in the audit's digitized outputs; quote in paper text |
| 13 | nikhef_lhcb_velo | FIX | 0.2577 / 0.2499 recounted from their released JSON, 23-75% traced. But "promising" is in the Discussion, not the abstract, and 23-75% mixes point values (low end) with the top of the CZ interval (high end) |
| 14 | kingston_constant | KEEP | 0.010 [0.002, 0.018] traced. Backends fez / marrakesh / kingston read straight from the IBM job records in the authors' repo (optional wording note) |
| 15 | fresh_pes_2609.30496 | KEEP | 15.70 / 11.20 / 0.76 / 0.57 traced. Both CZ medians recounted from their GitHub. 1.40-1.99x recomputed |
| 16 | pukyong_2609.13935 | KEEP | junk arm 12/12 at 48q, attributable False, 0/12 at 78q recounted from their repo CSV. Caption quote in paper text |
| 17 | qusoft_kingston | KEEP | 1.49 [1.37, 1.59] and +0.043 / -0.039 traced in the 24 Oct run folder |
| 18 | recount_2604.26175 | KEEP | Table 2 TSP m=5 1271 vs m=6 1368. FLP (144) and VRP (734) minima at m=6, all in the paper text |
| 19 | free_2509.11450 | KEEP | Table III qubits and Table IV kingston rows read from the paper text. Gaps recomputed. Optional: quote the sentence's own hedge |
| 20 | smu_astar | KEEP | 0.055 / 0.024 traced in the audit's projection and recomputed from our 23 Oct CZ factors. 88 of 131 traced |
| 21 | fire_2510.17692 | KEEP | +3.4 ± 2.1 and [-0.8, +7.6] traced in the T10 run. +32 recomputed 344.6 - 312.6 on torino qubit 10 (wording note: the paper says "CPMG", not "CPMG10") |
| 22 | so_2610.18124 | FIX | 9.4%, ~1%, 1.35-2.04 and 0.3° all traced. The qia_calibration cell drops "on the 2×1 patch", and the 3×3 dose is not bracketed |
| 23 | utah_rice_rl | KEEP | noisy mode and 16384 shots, 13 of 16 by sign, 145/17/154 of 316: all in the audit's out/ files |
| 24 | uiu_dhaka | FIX | +70.7%, +13% and -1.4% recounted from their HF calibration JSONs. "gain" should be "difference". The how cell's "couplers they used" is wrong: the figures cover all 352 entries per chip |
| 25 | k2025_constantine_2509.18029 | KEEP | 9 PASS rows and -12.2592 vs -12.4031 traced. 4.7 sigma recomputed (note: the REM+Positivity rows reproduce neither way) |
| 26 | run_geopump | FIX | +3.60 [+3.27, +3.94] traced. The cell leaves out "per cycle" and "on our prepared-bit version". Q13 and "spectator cost" do not describe what the run measured |
| 27 | fresh_usp_2609.33255 | KEEP | recounted from their GitHub manifests: batches 4-6 have identical calibration snapshots and qubits 82, 83, 96, 103 |
| 28 | run_boussahi | FIX | "21 of 21 runs reproduce" is 22 of 22 (our reproduce output has 22 circuit-runs, all matching). Drift figures traced |
| 29 | arizona_anomaly | KEEP | R 1.30 / 1.38 in the paper; sx 1.17-1.93 and CZ 1.18-1.62 are the min and max over all our 23-24 Oct sweep records |
| 30 | ucf_lbnl_mcm | FIX | "moved z by up to 47" mixes a shift with its significance: scores moved up to 0.43, up to 47 shot-noise widths. "Hardware change" names a cause the audit left open |
| 31 | so_2609.34411 | FIX | the claim is recounted from their CSV (tau 82.5 vs 101.1 us, probe T2 408.6 vs 101.1 us). The quote in the published cell has γ where the paper prints Γ |
| 32 | recount_2602.16233 | KEEP | text 5.5 ms vs Table 2 5.7 ms; 33.1 and 218.7 round to 33 and 219 |
| 33 | protein_qsad | FIX | 6.6-10.8 holds only for fez/kingston/marrakesh on IBM's 21 Oct 2026 records (not their chip or date; 8.2-11.5 on our 23 Oct records). 14.3x, time and RMSD figures recomputed |
| 34 | multichip_multipliers | FIX | "their marrakesh 1.91x" is not printed by them. It is our ratio 0.0063 / 0.0033, and 1.91x is their KINGSTON multiplier. 36x recomputed |

---

### 1. fire_2608.04486 : KEEP
| number | how | source |
|---|---|---|
| their 200 at resilience 2 (published) | RECOMPUTED: 236 - 36 = 200 from the paper's printed 236 +/- 78 and 36 +/- 136 (resilience level 2, TREX + ZNE). From their released JSON 236.388 - 36.054 = 200.33 | qia_runs/2026-10-24-fire-2608.04486/src/paper.txt lines 1271-1282 (same text as recheck_published/src/fire_2608.04486.txt). Released file src/kingston_device_N3.json ("resilience": 2, job db2u5su8v0ts73c3i75g). known_good.text lines 1-2 |
| ibm_kingston, resilience 0, 24 Oct 2026 | TRACED: job dbek4h0m94ac738rvg60, submitted 2026-10-24T23:41:56Z, EstimatorV2 resilience_level 0 | RESULT_RES0.md.text lines 1-2. PLAN_RES0.md.text line 9 |
| 120 +/- 40 (one standard error) | TRACED: 119.98, sigma 40.08 | RESULT_RES0.md.text line 10. results_res0.text lines 19-20 |
| 95% [41, 199], moments' errors independent | TRACED: [41.43, 198.53]. The plan fixes independent propagation before the run | results_res0.text lines 21-24. PLAN_RES0.md.text line 16 |
| [12, 228] worst case, run after the result | TRACED: "fully correlated the bad way, 95% [12.2, 227.8]" under "CHECKS RUN AFTER THE RESULT". RECOMPUTED: per-state sigma C2sq_err + 2 C2 C2_err = 47.76 (solvable), 27.30 (mixed). Quadrature 55.01. 120.0 +/- 1.96 x 55.01 = [12.2, 227.8] | RESULT_RES0.md.text lines 15-17. results_res0.text lines 2-17 |
| exact 240 | TRACED: our rebuild pds.py and their print agree | known_good.text line 6. Paper line 1308 |
source: qia_runs/2026-10-24-fire-2608.04486/RESULT_RES0.md.text; qia_runs/2026-10-24-fire-2608.04486/results_res0.text
grep: 120.0 +- 40.1, 95% [41.4, 198.5]

### 2. recount_10.5281/zenodo.20162808 : KEEP
| number | how | source |
|---|---|---|
| "GHZ fidelity" defined as P(0...0) + P(1...1) | TRACED. Metric 1 in Sec. 2.3. The two odd bytes around the sum in the extracted text are the PDF's large-parenthesis glyphs, not a root or a fraction | qia_leads/recheck_published/src/recount_10.5281_zenodo.20162808.txt lines 101-104 |
| Parity <Z...Z> is Z-basis only | TRACED: metric 2 is the parity expectation of Z on all qubits. The circuit listing measures every qubit in the computational basis with no basis change, so no coherence term is measured | same file line 106 and Listing 1, lines 276-295 |
| 88% plateau | TRACED, printed (4 qubits, Table 1: 0.879, 0.882, 0.884 at depths 10, 15, 20) | lines 14 and 258-264 |
| 89.4% to 83.7% | TRACED, printed (5 qubits, Table 2: 0.894 at depth 2, 0.837 at depth 20) | lines 15, 266-273 |
| GHZ fidelity = (P + C)/2 with C <= P, so the printed values are upper bounds | standard identity, no number of theirs needed: F = (P00..0 + P11..1)/2 + abs(rho_0..0,1..1) and abs(rho) <= (P00..0 + P11..1)/2 | none needed |
Note: the extracted text has NUL bytes from the PDF, so search it with grep -a.
source: qia_leads/recheck_published/src/recount_10.5281_zenodo.20162808.txt
grep: continued decay from 89.4% to 83.7%

### 3. nus_zib_2609.17497 : FIX
Table 1 at qia_leads/audits/nus_zib_a2c_2609.17497/src/paper.txt (page 8 block, after line 357). My own recount from the printed table: /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/r03/nz.py. Transcription in the audit's table1_counts.py checked line by line against the text: it matches.
| number | how | source |
|---|---|---|
| "over 100,000%" is one cell | RECOMPUTED: only (N, p) = (50, 18) at the 99% threshold exceeds 100,000% (printed 108,308%, 361 / 0.333 - 1 = 108,308%). Next largest 86,726% | Table 1 in src/paper.txt. AUDIT.md line 22 |
| 2 baseline counts | RECOUNTED from the printed probabilities, ONLY under the inferred shot number. LR = 0.333e-6. Shots are not printed (the SI defines S_eff as the sum of returned counts but never gives it). The audit takes S_eff = 6,000,000 for the N = 50 block, the smallest S that makes every printed probability an integer count. Then 0.333e-6 x 6e6 = 2. Any multiple also fits: at 12,000,000 shots it is 4 counts | AUDIT.md line 20 ("That inference is mine and is labelled post hoc"), line 22. out/table1_counts.json |
| 20 of 45 cells include 0 | RECOUNTED: 45 cells (N = 50, 100, 156, three depths, five thresholds), Clopper-Pearson 95% on AR given AR + LR. 20 include 0 at the smallest shot numbers (6e6, 2e6, 2e6). At twice those it is 18 of 45 | AUDIT.md line 25. My nz.py |
Support for the smallest shot numbers: the authors call the N = 100 and 156 strict-optimum cells (0.500e-6 in both arms) the "measurement-resolution floor" (paper line 323), which fits 1 count at 2,000,000 shots. For N = 50 there is no such sentence. The smallest printed value 0.167e-6 is 1 count at 6,000,000.
Suggested: measured: "“Over 100,000%” is one cell. Shots are not printed. At the fewest shots the printed probabilities allow, that cell's baseline is 2 counts and 20 of 45 cells have a 95% interval that includes 0." / qia_calibration: "F2 Print the shots: “over 100,000%” is one cell whose baseline is 2 counts at the fewest shots the table allows, and 20 of 45 cells include 0 at that count. Report the distribution."
source: qia_leads/audits/nus_zib_a2c_2609.17497/AUDIT.md; qia_leads/audits/nus_zib_a2c_2609.17497/out/table1_counts.json
grep: LR = 2 counts (0.333e-6)

### 4. free_2512.18493 : KEEP
| number | how | source |
|---|---|---|
| caption "comparing eight combinations of qubit counts, models, and frameworks" | TRACED, both captions | qia_leads/recheck_published/src/free_2512.18493.txt lines 1675 and 1722 |
| 10 rows, IDs C0-C9 | TRACED: Table III lines 1678-1687, Table IV lines 1725-1734 | same file |
| C5 = C0 = 0.6613, 0.6911, 0.7411, 0.7032 (Table III) | TRACED | lines 1678 and 1683 |
| C9 = C4 = 0.8073, 0.7907, 0.9365, 0.9402 (Table III) | TRACED | lines 1682 and 1687 |
| C5-C9 copy C0-C4 in all four metrics, same in Table IV | TRACED: every pair (C0/C5 ... C4/C9) is identical in both tables | lines 1678-1687, 1725-1734 |
Note (optional): Table I (lines 1655-1665) defines eight combinations as C1-C8. Neither C0 nor C9 is defined there.
source: qia_leads/recheck_published/src/free_2512.18493.txt
grep: C5 0.6613 0.6911 0.7411 0.7032

### 5. recount_2511.17692 : FIX
| number | how | source |
|---|---|---|
| quote "8 quantum devices, with 4 different circuits per device, for a total of 12 circuits per session" | TRACED | qia_leads/recheck_published/src/recount_2511.17692.txt lines 476-478 |
| 8 x 4 = 32, 12 = 3 x 4 | RECOMPUTED | arithmetic |
| No data released | TRACED as absence: no repository, link, data or code statement in the text (searched http, www, github, zenodo, repositor, available, supplement) | same file |
| "how: Recounted from their released data" | WRONG. It contradicts the measured cell and the paper. The figures are arithmetic on one printed sentence | - |
Note (optional): the paper names two backends, ibm_torino and ibm_brisbane (line 406), so "8 devices" matches neither the run nor 12 / 4.
Suggested: how: "Recounted from their printed values". Optional measured: "No data released. The paper prints “8 quantum devices, with 4 different circuits per device, for a total of 12 circuits per session”. 8 x 4 = 32, 12 = 3 x 4, and the runs named are on two devices (ibm_torino, ibm_brisbane)."
source: qia_leads/recheck_published/src/recount_2511.17692.txt
grep: 8 quantum devices, with 4 different circuits per device, for a total of 12 circuits per

### 6. kisti_2609.35163 : FIX
| number | how | source |
|---|---|---|
| "more accurately than a classical baseline" | TRACED, abstract | qia_leads/audits/kisti_iqp_2609.35163/src/paper.txt lines 26-27 |
| holds on 2 of 5 (digitized) | RECOUNTED: I fetched arXiv 2609.35163v1 (sha256 90408c64...c8f026) and read the Fig. 5 vector drawing myself (PyMuPDF coordinates, page 14). Zero at x 439.5, +0.02 at 484.1. Group labels by y: All w = 1, Random w = 2, Edge pairs, Distance 2 pairs, Nonlocal pairs. ProdEM 95% bars: +0.0093 to +0.0167, +0.0018 to +0.0068, -0.0190 to -0.0109, -0.0194 to -0.0128, +0.0003 to +0.0052. LocalCondEM the same pattern. So better on 2 (edge, distance-2), worse on 3. Matches the kept out/fig5_digitized.json | /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/r06/fig5.py and labels.py. AUDIT.md lines 19-26 |
| MMD2 ratio 1.04, 95% [0.90, 1.17], independence assumed | RECOMPUTED from Table 2: 3.51 / 3.38 = 1.0385. Standard errors from the printed percentile intervals (width / 3.92): 0.1582 and 0.1633. Relative: 0.0451, 0.0483, combined 0.0661. 1.0385 x (1 -/+ 1.96 x 0.0661) = [0.904, 1.173] | src/paper.txt lines 665-682 (Table 2). out/recompute.json "MMD2_ProdEM_minus_Product" |
Problem: the five are observable groups, not pair classes. Two of them are not pairs (all weight-1 words, random weight-2 words). The 2 wins are both pair groups.
Suggested: measured: "“More accurately than a classical baseline” holds on 2 of 5 observable groups (edge and distance-2 pairs; digitized). MMD² ratio 1.04 (95% interval [0.90, 1.17] from their Table 2 intervals, independence assumed)" / qia_calibration: "F2 Restrict “more accurately than a classical baseline” to the 2 of 5 observable groups where it holds (edge and distance-2 pairs). MMD² ratio 1.04 (95% interval [0.90, 1.17])."
source: qia_leads/audits/kisti_iqp_2609.35163/out/recompute.json; qia_leads/audits/kisti_iqp_2609.35163/AUDIT.md; qia_leads/audits/kisti_iqp_2609.35163/out/fig5_digitized.json
grep: ratio 1.04 [0.90, 1.17]

### 7. k2026_kobe_2603.13536 : KEEP
| number | how | source |
|---|---|---|
| ibm_pittsburgh, 24 Oct 2026 | TRACED: job dbeecdvgdj9s73flkcn0, created 2026-10-24T17:09:12Z, finished 17:50:58Z | qia_runs/2026-10-24-fire-2603.13536/RESULT_2603.13536.md.text line 3. job1_dbeecdvgdj9s73flkcn0/results_2603.13536.text line 1 |
| averaged over 10 instances | TRACED: seeds 100-109, instances are the units | PLAN_2603.13536.md.text lines 7, 12 |
| 97.5% interval | TRACED: two-sided t(9) at 97.5% over the 10 instances, fixed in the plan | PLAN_2603.13536.md.text line 16 |
| -0.930 [-1.208, -0.653], below | TRACED | results_2603.13536.text (D1 line). RESULT line 11 |
| -0.112 [-0.378, +0.154], consistent | TRACED. RECOMPUTED mean from the per-seed log10 errors (AS trot minus AS ctrl): -0.02, -0.25, +0.36, -0.03, -0.06, +0.35, -0.60, -0.09, -0.29, -0.49, mean -0.112 | results_2603.13536.text (D2 line and seed lines). RESULT line 12 |
| factor 2.4 better to 1.4 worse | RECOMPUTED: 10^0.378 = 2.39, 10^0.154 = 1.43 | RESULT line 12 |
| margin appears with the circuit removed | TRACED: AS ctrl minus RND ctrl (no-gate samples) -0.792 [-1.008, -0.576], below | results_2603.13536.text (descriptive). RESULT line 15 |
Note: these are job 1 (the planned job). Job 2 was an unplanned duplicate, printed as a copy and not pooled.
source: qia_runs/2026-10-24-fire-2603.13536/job1_dbeecdvgdj9s73flkcn0/results_2603.13536.text; qia_runs/2026-10-24-fire-2603.13536/RESULT_2603.13536.md.text
grep: -0.930 [-1.208, -0.653] -> BELOW

### 8. recount_10.5281/zenodo.19754086 : KEEP
| number | how | source |
|---|---|---|
| title "Experimental Validation of Infinite Quantum Communication" | TRACED | qia_leads/recheck_published/src/recount_10.5281_zenodo.19754086.txt line 10 |
| own receiver test shows no transmitted bit | TRACED: Phase 4, ancilla on the receiving side reads 0 for bit 1 as for bit 0. P(ancilla=0 given bit 0) 97.99%, given bit 1 97.93%, a 0.06% difference the paper calls below the noise floor. Phase 4v2 (RZ, stronger coupling): bit 1 "still undetected" | same file lines 270-291 and 310 |
Note (optional): Section 4.5 claims a later Manchester run sent "HOLA" with 0% BER, "detailed in companion report". That data is not in this record, and the paper's own checklist leaves "full QND detection (not Manchester fallback)" unticked (line 401). A sharper cell: "The paper's own receiver test shows no transmitted bit (ancilla reads 0 for both bits, 97.99% and 97.93%)."
source: qia_leads/recheck_published/src/recount_10.5281_zenodo.19754086.txt
grep: P(ancilla=0 | bit=1) = 97.93%

### 9. k2025_marmara_2512.14280 : KEEP
| number | how | source |
|---|---|---|
| shortfalls 1.279 / 0.701 (n = 6), 2.30 / 1.56 (n = 8) from their counts (published cell) | TRACED: our script on their Zenodo counts: 1.2787 / 0.7005 and 2.2973 / 1.563 | qia_leads/audits/k2025_marmara_2512.14280/src/repro_marmara_out.txt (n = 6 and n = 8 lines). KNOWN_GOOD.md line 28 |
| "Reproduce" | TRACED: all eight shortfall rows PASS. Known-good in the run folder: raw 1.279, her mitigated 0.700 | KNOWN_GOOD.md section 4. qia_runs/2026-10-24-fill-marmara/known_good_marmara.text |
| ibm_fez, n = 6, DD on, 24 Oct 2026 | TRACED: J2 and J3 DD on, created 14:43-14:44Z on 24 Oct, qubits 0-5 | qia_runs/2026-10-24-fill-marmara/RESULT_MARMARA.md.text lines 1-3 |
| mitigated shortfall 1.808 +/- 0.017, bootstrap standard error | TRACED: 1.808 +- 0.017 (plug-in 1.804). The +- is the bootstrap sd (np.std over bootstrap replicates, bias-corrected point) | results_marmara.text line 4. marmara.py lines 112-116. PLAN_MARMARA.md.text line 16 |
| above 1 bit | TRACED: R1 mitigated vs 1 bit ABOVE | results_marmara.text line 5 |
| Table 1 readout 1.45E-2 | TRACED in the paper | qia_leads/audits/k2025_marmara_2512.14280/src/paper.txt lines 406-407 |
| 1.477E-2 in the record the run used | TRACED: median readout_error over 156 qubits in their stored record 0.0147705 | src/probe_marmara_out.txt line 3. KNOWN_GOOD.md line 31 |
source: qia_runs/2026-10-24-fill-marmara/results_marmara.text; qia_leads/audits/k2025_marmara_2512.14280/KNOWN_GOOD.md
grep: mitigated 1.808 +- 0.017

### 10. so_2610.21761 : KEEP
| number | how | source |
|---|---|---|
| abstract "accounts quantitatively" | TRACED | qia_leads/audits/giri_2610.21761_desk/src/paper.txt line 18 |
| chi2/N 6.0-47.3 at lambda = 1 | TRACED: Table I lambda = 1 column 6.0, 6.5, 34.0, 10.8, 47.3, 13.3 | src/paper.txt lines 1106-1137. out/desk_arithmetic.txt lines 4-9 |
| fitted lambda 1.34-1.95 | TRACED: Table I (1.75, 1.68, 1.95, 1.34, 1.89, 1.54) and Sec. IV G text "1.34–1.95 for all runs" | src/paper.txt lines 1129 and 1174 |
| different quantity from our factor | TRACED: lambda multiplies the RB gate error and 1/T1, 1/T2 in their model | AUDIT.md lines 10, 22 |
source: qia_leads/audits/giri_2610.21761_desk/out/desk_arithmetic.txt; qia_leads/audits/giri_2610.21761_desk/src/paper.txt
grep: (at lambda=1: 47.3)

### 11. recount_2512.21914 : FIX
| number | how | source |
|---|---|---|
| hardware 0.907 printed above the simulator | TRACED: consistency fidelity, simulation 0.904 +/- 0.008, hardware 0.907 +/- 0.008 | qia_leads/recheck_published/src/recount_2512.21914.txt lines 428-430 and Table 2 lines 446-447 |
| "Whether the simulator was noisy is not stated" | WRONG AS WORDED. The paper says it ran on "an ideal noiseless simulator" (line 350) and in Fig. 2 an ideal state vector with only 1010 and 1001 at 0.5 each, which gives consistency fidelity 1. Its own simulation counts (Table S1, lines 813-833, 8,192 shots) put 776 shots (9.5%) outside those two states, e.g. 249 on 1000. RECOMPUTED: (3460 + 3956) / 8192 = 0.905, which is the printed 0.904. So the simulator behind Table 2 was not noiseless, and the paper does not say what noise it had | same file lines 350-355, 364-366, 813-833 |
Note: Table S1's probability column sums to 0.962 (simulation) and 0.945 (hardware), so it is not counts / 8192. The counts column sums to 8,192 and reproduces the printed 0.904. The hardware counts give (3680 + 3792) / 8192 = 0.912 against the printed 0.907 (averaging over 20 runs may explain it; not checkable).
Suggested: measured: "The hardware value 0.907 is printed above the simulator's 0.904. The text calls the simulator ideal and noiseless, but its own simulation counts put 9.5% of shots outside the two states an ideal run allows, so the simulator had noise the paper does not describe." / qia_calibration: "F4 Name the simulator's noise: it is called noiseless, but its counts put 9.5% of shots outside the two allowed states."
source: qia_leads/recheck_published/src/recount_2512.21914.txt
grep: Consistency Fidelity (hardware) 0.907

### 12. nus_lanzhou_2610.22482 : KEEP
| number | how | source |
|---|---|---|
| "approaches zero" (their text) | TRACED, verbatim | qia_leads/audits/nus_lanzhou_2610.22482/src/paper.txt lines 395-396. Also qia_leads/recheck_published/src/nus_lanzhou_2610.22482.txt lines 319-320 |
| hardware Czz +0.034 to +0.070 on all 12 points K >= 0.415 | TRACED (DIGITIZED from the PDF's vector Fig. 3a, our script). 12 points, IBM min 0.0336, max 0.0704 | qia_leads/audits/nus_lanzhou_2610.22482/out/analysis.json ("fig3a_K>=0.415_n": 12, min/max/mean 0.0336 / 0.0704 / 0.0473). Per-point values in out/fig3a_digitized.json. AUDIT.md line 25 |
| DMRG about 0 | TRACED, DMRG -0.022 to +0.020 (mean -0.005) on the same 12 points | out/analysis.json ("fig3a_K>=0.415_DMRG_min_max_mean"). AUDIT.md line 25 |
| layer-0 dimer 0.833-0.871 | TRACED (DIGITIZED Fig. 5a): L=32 0.833, L=64 0.855, L=96 0.871 | out/analysis.json "fig5a_L32/64/96_VBS_layer0" |
| ideal 1 | TRACED, the paper's own "<O'_VBS>_d=0 = 1" | src/paper.txt lines 2428-2429 |
| device ibm_fez (in the audit, not in the cell) | TRACED | src/paper.txt line 1872 |
Note: the values are read off the figure (digitization error about 0.002 per AUDIT.md). The cell already says "(digitized)".
source: qia_leads/audits/nus_lanzhou_2610.22482/AUDIT.md; qia_leads/audits/nus_lanzhou_2610.22482/out/analysis.json; qia_leads/recheck_published/src/nus_lanzhou_2610.22482.txt
grep: +0.034 to +0.070 (mean +0.047)

### 13. nikhef_lhcb_velo : FIX
| number | how | source |
|---|---|---|
| "promising" placed in the abstract (published cell) | NOT IN THE ABSTRACT. The v2 abstract (cached text lines 13-27) has no "promising". The word is in the Discussion, about hardware results for small systems | qia_leads/recheck_published/src/nikhef_lhcb_velo.txt line 680. qia_leads/audits/nikhef_2601.07766/src/paper.txt line 325 |
| IBM Hellinger 0.2577 | RECOUNTED from their released data. Kept copy qia_leads/audits/nikhef_2601.07766/src/ext/tracking_results.json, sha256 31d791ee...53ce6, matching the hash the audit recorded for GitHub Xenofon-Chiotopoulos/OneBQF commit 92f0285. Key 3L_4T, Qiskit-Pittsburgh-Hardware-EM individual_runs, F_H = (sum sqrt(p q))^2 against the H2-1LE mean vector. Five runs 0.2534, 0.2618, 0.2543, 0.2676, 0.2517, mean 0.2577. Script: /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/r13/fh.py | also TRACED, src/recompute_fh_out.txt lines 13 and 51 |
| uniform 0.2499 | RECOUNTED: F_H of the uniform 32-bin vector against the same baseline = 0.2499 | recompute_fh_out.txt line 51 |
| 23-75% of the 3L_2T gap | TRACED, recompute_fh_out.txt lines 59-63 (sx 1.173 23%, sx 1.216 29%, CZ 1.386 52%, CZ 1.426 57%, CZ 1.557 75%). RECOMPUTED: emulator 0.8788 and hardware-EM 0.7883 (recounted, same script) with uniform 0.5. Lost signal scaled by f: F = 0.5 + 0.5(1 - f x 0.2424), closure = (0.8788 - F)/0.0905. Gives 23.2, 28.9, 51.7, 57.1, 74.6% | recompute_fh_out.txt lines 59-63 |
| our ibm_pittsburgh factors (23 Oct 2026) | TRACED: sx 1.173 [1.098, 1.348], CZ 1.426 [1.279, 1.557] (job dbdsofnpc3tc739knqq0). sx 1.216 [1.139, 1.341], CZ 1.386 [1.299, 1.553] (job dbducm8m94ac738quco0) | arxiv_one_readout/sweep_run/results_sweep_ibm_pittsburgh.text lines 7-8. results_sweep_ibm_pittsburgh_r2.text lines 7-8 |
| "RB, 23 Oct 2026" (how) | TRACED, same files (RB1 / RB2, IBM record 2026-10-23) | same |
Problem with 23-75%: the low end (23%) is a point estimate (sx 1.173). The high end (75%) is the top of the CZ 95% interval (1.557). At the point values the range is 23-57%. Across the 95% intervals it is 13-75% (sx 1.098 gives 13.1%, my arithmetic). Each factor is also applied alone, not together. The audit (AUDIT.md section 4) says both together are not additive.
Also: the 0.2577 vs 0.2499 is the 4-tracks-3-layers case, but the cell names no case. Next to "3L_2T" in the same cell, a reader could take it for that size (whose hardware value is 0.7883).
Suggested: published: "“promising” (Discussion). IBM Hellinger 0.2577 against uniform 0.2499 at 4 tracks, 3 layers (from their released data)" / measured: "Our ibm_pittsburgh gate factors, applied one at a time, close 23–57% of their 3L_2T emulator-to-hardware gap at the point values (13–75% across the 95% intervals)" / qia_calibration: "Q17 Scale the gate errors by our measured factors (ibm_pittsburgh, 23 Oct 2026): one at a time they close 23–57% of the 3L_2T emulator-to-hardware gap (13–75% across the intervals). At 4 tracks and 3 layers the hardware Hellinger 0.2577 sits near uniform 0.2499."
source: qia_leads/audits/nikhef_2601.07766/src/recompute_fh_out.txt; qia_leads/audits/nikhef_2601.07766/src/ext/tracking_results.json; arxiv_one_readout/sweep_run/results_sweep_ibm_pittsburgh.text
grep: F_H uniform=0.2499 | HW-EM runs mean 0.2577

### 14. kingston_constant : KEEP
| number | how | source |
|---|---|---|
| signal scale 0.010 | TRACED: least-squares slope through the origin, trained 100-probe job d7t8fsaudops7397lrbg, s = 0.0101 | qia_leads/audits/kingston_constant/check_kingston_constant_output.txt line 17 and the "+-" block below it |
| 95% interval 0.002-0.018 | RECOMPUTED: 0.0101 +/- 0.0081 = [0.0020, 0.0182]. The interval is binomial shot noise only | same file ("s = 0.0101 +- 0.0081") |
| 0.07 claimed | TRACED in the paper: kappa about 0.07 (abstract), "Signal Scale 1.0 0.07" in the table, lambda = 0.9255 | qia_leads/recheck_published/src/kingston_constant.txt lines 11, 245, 320, 485 |
| job records say fez / marrakesh | RECOUNTED: read the "backend" field straight from the IBM job-info JSON inside the authors' released zips (kept copy qia_leads/audits/kingston_constant/ext_repo/repo/calibration/). d7t8fsaudops7397lrbg is ibm_fez (created 2026-05-06), d7tudovljm6s73bd54q0 is ibm_marrakesh (2026-05-07), d7t3di2udops7397gb7g is ibm_kingston (2026-05-05) | zips in ext_repo/repo/calibration/mnist-trained and mnist-untrained. Also check_kingston_constant_output.txt lines 3, 14, 25 |
| paper says kingston | TRACED: abstract and "on the ibm kingston" | kingston_constant.txt lines 11, 53 |
| NC State, single author | TRACED: Wladimir Silva, North Carolina State University | kingston_constant.txt lines 3-5 |
Wording note (optional): one of the three saved jobs (the untrained 100-probe job) did run on ibm_kingston. The fez and marrakesh records are the two jobs behind the constant and behind Table I. Narrower: "The job records behind the constant and Table I say ibm_fez and ibm_marrakesh, not ibm_kingston." Also optional: "(95% interval 0.002-0.018, shot noise only)".
source: qia_leads/audits/kingston_constant/check_kingston_constant_output.txt; qia_leads/recheck_published/src/kingston_constant.txt
grep: s = 0.0101 +- 0.0081

### 15. fresh_pes_2609.30496 : KEEP
| number | how | source |
|---|---|---|
| 15.70 reproduces | TRACED: job 1 rel_err 15.696% from their released counts (our l1_repro.py) | qia_leads/audits/fresh_pes_2609.30496/src/l1_repro_out.txt line 4. Paper text line 1414 |
| 11.20 | TRACED: 11.196% | l1_repro_out.txt line 10 |
| 0.76 | TRACED: p_eff raw 0.7637% | l1_repro_out.txt line 11 |
| 0.57 | TRACED: p_eff corrected 0.5671% | l1_repro_out.txt line 12 |
| 0.002873 (references) | RECOUNTED: GitHub 0Shunya0/VQE_LGT (HEAD at fetch, 30 Oct), results/ibm_N3_L2_K0_references.json "median_cz_error": 0.002873171523854273 | copy /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/r15/data/. Kept: KNOWN_GOOD.md section 1 |
| 0.003048 (at runtime) | RECOUNTED: same repo, results/ibm_N3_L2_K0.json "median_cz_error_at_runtime": 0.00304759178932483 | same |
| "2-3x" in the paper | TRACED | qia_leads/recheck_published/src/fresh_pes_2609.30496.txt lines 1394-1395. src/paper.txt line 1418 |
| 1.40-1.99x | RECOMPUTED on one quantity (depolarizing p = 4r/3): 0.7637 / (4/3 x 0.2873) = 1.994, 0.5671 / (4/3 x 0.3048) = 1.396 (1.48 and 1.88 for the other pairings) | KNOWN_GOOD.md section 4 and /q 1 ("ratio range 1.40-1.99x") |
Note: 1.40-1.99x rests on the conversion r = 0.75 p (d = 4), which KNOWN_GOOD.md names. The cell does not say "on one quantity" in the calibration line. The measured cell does.
source: qia_leads/audits/fresh_pes_2609.30496/src/l1_repro_out.txt; qia_leads/audits/fresh_pes_2609.30496/KNOWN_GOOD.md
grep: ratio range 1.40-1.99x

### 16. pukyong_2609.13935 : KEEP
| number | how | source |
|---|---|---|
| 48q noise-fed control completes 12/12, attributable False | RECOUNTED: their anonymized repo (anonymous.4open.science/r/suture_source-5F07, file API, fetched 30 Oct) suture/results/a3_hardedge_summary.csv, row 48q: surv_suture 12, surv_junk 12, surv_purify 0, attributable False | /private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/p5/r16/data/a3_hardedge_summary.csv. Kept copy: qia_leads/audits/pukyong_suture_2609.13935/out/recompute.json ("hardedge_summary", "hard48_survival" junk 12) |
| "junk" = noise-fed control | TRACED: their run_a3.py comment, quoted in AUDIT.md (the same decoder on uniform random strings) | qia_leads/audits/pukyong_suture_2609.13935/AUDIT.md section on the 48-qubit cell |
| caption "completes every chain" at 48 and 78 | TRACED | src/paper.txt line 1401 (also 1455). recheck_published/src/pukyong_2609.13935.txt line 1179 |
| 78q stands | RECOUNTED: 78q row surv_junk 0, attributable True | same CSV |
source: qia_leads/audits/pukyong_suture_2609.13935/out/recompute.json; qia_leads/audits/pukyong_suture_2609.13935/AUDIT.md
grep: "surv_junk": "12"

### 17. qusoft_kingston : KEEP
| number | how | source |
|---|---|---|
| published: hardware below their noise model on both chains | TRACED: their model minus measured, chain21 +0.3287, chain11 +0.1383 (arithmetic on their tables) | qia_runs/2026-10-24-fill-qusoft/results_qusoft.text line 4. Paper text line 1132 |
| delivered CZ 1.49 times stated | TRACED: R3 CZRATIO +1.4943 [+1.3739, +1.5946], median delivered/stated over the 20 chain edges, same-job RB | results_qusoft.text line 13. RESULT_QUSOFT.md.text line 7 ("1.49 [1.37, 1.59]") |
| within about 0.04 on both chains | TRACED: R2 REMAIN chain21 +0.0426 [+0.0362, +0.0498], chain11 -0.0392 [-0.0489, -0.0282] | results_qusoft.text lines 8 and 10 |
| ibm_kingston, 24 Oct 2026, same-day | TRACED: run 24 Oct 2026 05:58-06:01Z, jobs A1 B1 B2 A2, stated record unchanged across the four saved records | RESULT_QUSOFT.md.text lines 1-3 |
Note: the first pass listed utah_rice and awuah-guo files for this row. Those are other studies (the awuah-guo gift folder only holds a copy of this run). The row's own folder is qia_runs/2026-10-24-fill-qusoft. Optional: the interval tops are 0.050 and 0.049, so "within about 0.04" holds on the point values. HP_8 (not in the cell) is left 0.355 off.
source: qia_runs/2026-10-24-fill-qusoft/results_qusoft.text; qia_runs/2026-10-24-fill-qusoft/RESULT_QUSOFT.md.text
grep: +1.4943 [+1.3739, +1.5946]

### 18. recount_2604.26175 : KEEP
| number | how | source |
|---|---|---|
| quote "consistently yields the smallest overall circuit depth across all problem classes" | TRACED | qia_leads/recheck_published/src/recount_2604.26175.txt lines 1115-1117. Repeated at lines 1222-1223 ("yields the smallest two-qubit depth in all cases") |
| TSP m = 5 1271 against m = 6 1368 | TRACED, Table 2 Full D2q | same file lines 1166-1167 |
| FLP and VRP hold | RECOMPUTED: FLP Full D2q 209, 221, 340, 182, 186, 282, 144, minimum 144 at m = 6. VRP 822, 1182, 837, 941, 857, 877, 734, minimum 734 at m = 6. TSP minimum 1271 at m = 5 | same file lines 1145-1167 |
Note: no data release is needed. Every figure is in the printed Table 2. "how" says "Recounted from their printed values", which is right.
source: qia_leads/recheck_published/src/recount_2604.26175.txt
grep: 5 456 1271 6 6

### 19. free_2509.11450 : KEEP
| number | how | source |
|---|---|---|
| quote "recovers optimal tours for wi4-wi5 and maintains Delta E/E_ideal < 5% up to 64 qubits" | TRACED | qia_leads/recheck_published/src/free_2509.11450.txt lines 378-379 |
| Table III qubits wi4 16, wi5 25, wi6 36, dj8 64, dj9 81 | TRACED (the table also has wi7 49, which the cell leaves out because it has no kingston row) | same file lines 363-368 |
| kingston wi4 gap 0.00% | TRACED (6700, ratio 1.000) | line 386 |
| kingston wi6 gap 47.8% (36 q) | TRACED (14502, 0.677). RECOMPUTED (14502 - 9815)/9815 = 47.75% | line 390 |
| kingston dj8 2.17% (64 q) | TRACED. RECOMPUTED (2822 - 2762)/2762 = 2.17% | line 392 |
| kingston dj9 20.3% (81 q) | TRACED. RECOMPUTED (2567 - 2134)/2134 = 20.29% | line 393 |
| no kingston wi5 row | TRACED: wi5 has aer sim and ibm brussels rows only | lines 387-388 |
Wording note (optional): the quoted sentence goes on "with occasional errors that signify performance collapse" (line 380). The authors' own clause concedes exceptions. The cell's "holds only for selected rows" is consistent with it. Quoting the clause would make the published cell fairer: "Text: 'maintains Delta E/E_ideal < 5% up to 64 qubits with occasional errors'". The "no kingston wi5 row" point stands on its own.
source: qia_leads/recheck_published/src/free_2509.11450.txt
grep: 14502 0.677 47.8 ibm kingston

### 20. smu_astar : KEEP
| number | how | source |
|---|---|---|
| F ≈ 0.1 at ~770 gates, stated 3e-3 (theirs) | TRACED paper | qia_leads/audits/smu_astar_2607.11637/src/paper.txt line 33 (abstract), 901, Table 4 lines 867-868 (3×10^-3 fez and marrakesh) |
| about 0.055 on ibm_fez | TRACED + RECOMPUTED: (1 - 3e-3 × 1.255)^770 = 0.0548. With the two job factors alone: 1.244 gives 0.056 and 1.269 gives 0.053 | qia_leads/audits/smu_astar_2607.11637/out/smu_projection.txt line 2. Factors in arxiv_one_readout/sweep_run/results_sweep_3.text line 9 (1.244) and results_sweep_r2_part.text line 9 (1.269), both 23 Oct |
| 0.024 on ibm_marrakesh | TRACED + RECOMPUTED: (1 - 3e-3 × 1.616)^770 = 0.0237 | smu_projection.txt line 4. Factor in sweep_run/results_sweep_3.text line 33 (1.616 [1.541, 1.750]) |
| 88 of 131 trajectories mix chips | TRACED: 131 rows with job records, and in 88 of them the printed backend ran only some of the jobs (the rest ran on another chip) | qia_leads/audits/smu_astar_2607.11637/out/smu_backend_match.txt lines 2-3. AUDIT.md section 4 item 4 ("88 have jobs on two or more named IBM chips") |
| "our factors, 23 Oct 2026" (qia_calibration) | TRACED: IBM record stamps 2026-10-23 | sweep_run/results_sweep_3.text lines 1 and 25 |
Note: the fez central factor in smu_projection.py is 1.255. The mean of the two job medians is 1.2565. Both give 0.055.
source: qia_leads/audits/smu_astar_2607.11637/out/smu_projection.txt; qia_leads/audits/smu_astar_2607.11637/out/smu_backend_match.txt; arxiv_one_readout/sweep_run/results_sweep_3.text
grep: central 0.0548

### 21. fire_2510.17692 : KEEP
| number | how | source |
|---|---|---|
| +32 µs, one ibm_torino qubit (published and qia_calibration) | RECOMPUTED: T10 344.6 - CPMG 312.6 = 32.0 µs. Qubit 10 of ibm_torino, one Ramsey session (28/01/2026) | qia_leads/recheck_published/src/fire_2510.17692.txt lines 1264-1266 (values) and 1223-1225 (qubit 10, date) |
| four qubits, ibm_fez, 25 Oct 2026, 2 jobs | TRACED: qubits 3, 92, 117, 70. Job A dbeo59fpc3tc739m2p1g and job B dbeo61npc3tc739m2qgg | qia_runs/2026-10-25-fire-t10/RESULT_T10.md.text lines 1-2. jobs_t10.json |
| +3.4 ± 2.1 µs (one standard error) pooled | TRACED: weighted mean 3.4097, se 2.1400 = sqrt(1/sum w), which is one standard error | qia_runs/2026-10-25-fire-t10/results_t10.text lines 171-173. t10_fill.py line 36 |
| 95% interval [-0.8, +7.6], consistent with zero | RECOMPUTED: 3.4097 ± 1.96 × 2.1400 = [-0.785, +7.604] | RESULT_T10.md.text line 11 |
Wording note (published cell only): the paper prints "CPMG" for the Ramsey comparison, with its pulse count not stated. "CPMG10" is our label (our CPMG is ten pi_y pulses, RESULT_T10.md.text line 15). Optional: "T10 beats CPMG by +32 µs". The measured cell's "CPMG10" correctly describes our run.
source: qia_runs/2026-10-25-fire-t10/RESULT_T10.md.text; qia_runs/2026-10-25-fire-t10/results_t10.text; qia_leads/recheck_published/src/fire_2510.17692.txt
grep: POOLED: dT = +3.4 +- 2.1 us (95% [-0.8, +7.6])

### 22. so_2610.18124 : FIX
| number | how | source |
|---|---|---|
| "up to two" (theirs), "2.01" | TRACED paper | qia_leads/audits/fauseweh_2610.18124_qualify/src/paper.txt lines 16 and 70 |
| maximum of 4 cells, 1.35-2.04 per cycle | TRACED: 2×1 1.35 and 2.04, 3×3 1.76 and 1.70. The maximum is 2.04 (2×1, 5-site) | qia_leads/audits/fauseweh_2610.18124_qualify/out/ratio_and_scatter.txt lines 1, 2, 8, 9 |
| depth-0 error 9.4% | TRACED: 2×1 patch, P(read 1) after the all-zeros preparation, mean 0.0941 (256 shots) | out/n0_readout_check.txt line 1 |
| their own ~1% calibration | TRACED: stored mean e10 0.0095 and e01 0.0138 (their 4096-shot calibration, not IBM's stated figure) | out/n0_readout_check.txt line 1. AUDIT.md "Two zero-QPU readings" item 1 |
| at most about 0.3° on the 2×1 layout | TRACED + interpolation: 6-8 simultaneous readouts (2×1) sit between our kingston dose rows. K = 1 of 39 gives pooled +0.0056 [-0.0903, +0.0784] (at most 0.09°). K = 10 of 39 gives -0.2755 [-0.4349, -0.1374]. The full pack (39 of 39) gives -2.8638 | arxiv_one_readout/control_run/results_prereg.txt lines 53 (ibm_kingston job dbck8c9gv2cc73eahbc0), 57, 61, 65 |
Wrong: the qia_calibration cell says "The readout kick at their dose is at most about 0.3°" with no patch named. The 3×3 patch has 20-24 simultaneous readouts, which falls between our 10-of-39 row (0.28°) and our 39-of-39 row (2.86°), so no dose row of ours brackets it (AUDIT.md "Dose-scaled kick", "The 3x3 value cannot be projected"). The 0.3° bound holds for the 2×1 patch only.
Precision note: "about 0.3°" is the point value of the 10-of-39 row. Its 95% interval reaches 0.43°.
Suggested qia_calibration: "Q12 F2 “Up to two” is the maximum of 4 cells (1.35–2.04 per cycle), depth-0 error is 9.4% against their ~1% calibration. On the 2×1 patch the readout kick at their dose is at most about 0.3°. The 3×3 dose is outside our measured range."
source: qia_leads/audits/fauseweh_2610.18124_qualify/out/n0_readout_check.txt; qia_leads/audits/fauseweh_2610.18124_qualify/out/ratio_and_scatter.txt; arxiv_one_readout/control_run/results_prereg.txt
grep: P(read1) per qubit mean 0.0941

### 23. utah_rice_rl : KEEP
| number | how | source |
|---|---|---|
| "real hardware" (theirs) | TRACED: "execute entirely on real IBM Quantum hardware", "8192 shots" | qia_leads/audits/utah_rice_2605.11375/src/paper.txt lines 1124-1133 |
| noisy-mode 16384-shot files behind the figures | TRACED: all 16 Fig. 11 cells (and the Fig. 9 keys) read from files with mode "noisy" and shots 16384, which reproduce the printed values | qia_leads/audits/utah_rice_2605.11375/out/recompute_fig11_zen_v0514.json (every cell: "mode": "noisy", "shots": 16384). recompute_fig9_zen_v0514.json lines 11-12 |
| 14/16 -> 13/16 | RECOMPUTED from the kept json: L3_tvd - rl_tvd > 0 in 13 of 16 cells. Their int() rule gives 14 non-negative (Kingston Grover -0.000122 truncates to 0). Paper prints "14 of 16" | recompute_fig11_zen_v0514.json. AUDIT.md line 41. Paper line 1366 |
| 145/17/154 over 316 | TRACED: ibm_torino all keys n 316, wins 145, ties 17, losses 154 | qia_leads/audits/utah_rice_2605.11375/out/strat_allkeys.json lines 4-7 |
Note: the audit's outcome is CANNOT_TELL on whether the plotted bars are the noisy files. "Backed by" in the measured cell matches what it found (the printed numbers reproduce from those files). The calibration cell asks only that the noisy-mode results be labelled as simulation, which they are.
source: qia_leads/audits/utah_rice_2605.11375/out/strat_allkeys.json; qia_leads/audits/utah_rice_2605.11375/out/recompute_fig11_zen_v0514.json; qia_leads/audits/utah_rice_2605.11375/AUDIT.md
grep: By sign it is 13 of 16 improved, not 14

### 24. uiu_dhaka : FIX
RECOUNTED from their public data: huggingface.co/datasets/sahilfarib/quantum-noise-transfer data/raw/calibration_A.json (ibm_fez) and calibration_B.json (ibm_marrakesh), both retrieved 2026-04-17 13:20. Copies in scratch p5/r24/, read with my own script p5/r24_cx.py (python3 -I).
| number | how | source |
|---|---|---|
| +70.7% (theirs) | RECOUNTED: mean gate_errors over 352 directed entries 0.032785 (fez) and 0.055975 (marrakesh), so +70.74% | paper (audit src/paper.txt) lines 454, 459, 487. qia_leads/audits/uiu_dhaka_2604_24397/out/dhaka_check_stdout.txt lines 8, 26, 42 |
| mean carried by couplers at error 1.0 | RECOUNTED: every entry ≥ 0.5 is exactly 1.0 (fez 10, marrakesh 18). They make up 10/352 / 0.032785 = 86.7% and 18/352 / 0.055975 = 91.4% of the means | dhaka_check_stdout.txt lines 10, 28. AUDIT.md section 3 |
| usable couplers +13% | RECOUNTED: mean excluding 1.0 entries 0.0045034 vs 0.0050991, so +13.2% | dhaka_check_stdout.txt lines 12, 30, 45 |
| medians -1.4% | RECOUNTED: 0.0027451 vs 0.0027074, so -1.37% | dhaka_check_stdout.txt lines 9, 27, 43 |
Wrong (wording): qia_calibration says "the gain is +13%". The +70.7% is the paper's between-chip difference in mean "CX gate error", not a gain. It should read "difference".
Wrong (how cell): "IBM's published record for the couplers they used". These figures are means and medians over all 352 directed coupler entries of each chip, from one record pull the authors saved (17 Apr 2026, 20.5 h after the fez job ran). They are not figures for the couplers their circuits used.
Suggested qia_calibration: "F2 Exclude couplers that IBM’s record lists at error 1.0: on usable couplers the difference is +13% (medians -1.4%), not +70.7%."
Suggested how: "IBM’s calibration record as saved in their released files (all 352 coupler entries per chip)"
source: qia_leads/audits/uiu_dhaka_2604_24397/out/dhaka_check_stdout.txt; qia_leads/audits/uiu_dhaka_2604_24397/AUDIT.md
grep: "cx_mean_excl_ge_0p5": 13.228383849311598

### 25. k2025_constantine_2509.18029 : KEEP
| number | how | source |
|---|---|---|
| 9 unmitigated and ZNE rows reproduce | TRACED: Table II (a), (b), (c) × (unmitigated, deg-1 ZNE, deg-2 ZNE) all PASS from their Zenodo 21264601 counts (Algiers deg-1 -12.8619 vs -12.8618 printed) | qia_leads/audits/k2025_constantine_2509.18029/src/repro_kagome_out.txt (PASS lines in each block). KNOWN_GOOD.md section 4 |
| REM reproduces only mirrored, Algiers -12.2592 vs printed -12.4031 | TRACED: unmirrored -12.2592 ± 0.0310, mirrored -12.4032 ± 0.0306 (PASS) | src/repro_kagome_out.txt line 13. src/repro_kagome_mirror_out.txt line 14. Paper src/paper.txt line 945 |
| 4.7 sigma | RECOMPUTED: (12.4031 - 12.2592) / 0.0306 = 4.70 | as above |
Note: the six REM+Positivity values (with and without deg-2 ZNE) reproduce neither way (differences up to 0.46, KNOWN_GOOD.md section 4 item 2, "Unresolved"). The cell makes no claim about them, so nothing in it is wrong. If Bones wants the cell complete: "the REM + Positivity rows do not reproduce".
source: qia_leads/audits/k2025_constantine_2509.18029/src/repro_kagome_out.txt; qia_leads/audits/k2025_constantine_2509.18029/src/repro_kagome_mirror_out.txt; qia_leads/audits/k2025_constantine_2509.18029/KNOWN_GOOD.md
grep: -12.2592 +- 0.0310

### 26. run_geopump : FIX
| number | how | source |
|---|---|---|
| ibm_kingston, 24 Oct 2026, tau = 60 | TRACED: jobs dbeafongdj9s73fleo0g and dbeaggfpc3tc739lboq0, 2026-10-24 | qia_runs/2026-10-24-fill-geopump/RESULT_GEOPUMP.md.text lines 2-3 |
| +3.60 T, 99% bootstrap [+3.27, +3.94] | TRACED: R2 Ap - Bp, Qtot_even +3.5997 [+3.2688, +3.9399], 99% band, B = 2000 | results_geopump.text line 26. run_real.py line 32. RESULT_GEOPUMP.md.text line 8 |
| "against an equal delay" | TRACED: Bp replaces the incoming measurement with a delay of its scheduled length (545 dt). CHECK 8 PASS on all 96 pairs | PLAN_GEOPUMP.md.text DESIGN. RESULT line 4 |
Wrong / incomplete (measured): (1) The 3.60 T is per cycle, from 192 incoming readouts per cycle (RESULT line 10). The cell gives neither. (2) It was measured on our prepared-bit version (Ap/Bp), not their exact circuits. The control R4 at tau 60 is BELOW, -0.95 [-1.54, -0.44] (RESULT lines 19-21): our version runs about 1 T hotter, and "how much of the 3.6 T applies to their exact circuit is CANNOT_TELL". The gift README (qia_runs/2026-10-30-gift-geopump/README.md, "What we cannot say") says the same.
Wrong (qia_calibration): "Q13 Charge each readout a spectator cost". In the QIA key, Q13 is coherence lost by untouched qubits next to a readout (public_mirror/indahl.ai/qia/key.html). Neither our run nor its plan reads that. The plan says the heat is blind to phase-type costs on S. The post-hoc split puts most of the cost on the read ancilla itself (q46 outgoing bit +0.029 to +0.038, q48 at most 0.005), a readout that disturbs the qubit it reads, not a spectator (RESULT lines 31-37). Bones to pick the tag. None of Q12-Q14 fits as written.
Suggested measured: "Our run on ibm_kingston (24 Oct 2026) at tau = 60, on a prepared-bit version of their circuit: the 192 incoming ancilla readouts per cycle, against an equal delay, add +3.60 T per cycle (99% bootstrap [+3.27, +3.94]) to the total even heat. Their pumped (odd) heat is unchanged (within 0.30 T). How much carries over to their exact circuits is not established (ours runs about 1 T hotter)."
Suggested qia_calibration: "Charge each ancilla readout its measured cost against an equal idle: on ibm_kingston (24 Oct 2026, tau = 60) the incoming readouts add +3.60 T per cycle to the even heat, mostly a 3 to 4 percent disturbance of the read ancilla."
source: qia_runs/2026-10-24-fill-geopump/RESULT_GEOPUMP.md.text; qia_runs/2026-10-24-fill-geopump/results_geopump.text; qia_runs/2026-10-30-gift-geopump/README.md
grep: tau 60: +3.60 [+3.27, +3.94]

### 27. fresh_usp_2609.33255 : KEEP
| claim | how | source |
|---|---|---|
| paper: "three later batches, each on a new calibration and a different set of qubits" | TRACED quote | qia_leads/audits/fresh_usp_2609.33255/src/paper.txt line 281 |
| batches 4-6 ran under one calibration record and one qubit set | RECOUNTED from their GitHub saeg/quanifi-replication (HEAD, fetched 30 Oct), experiments/results/grover_hw_matrix/manifests/ibm/*.manifest.json, with my own script p5/r27_man.py. Jobs daj6c9vi3e6s738psv0g, daj6mk0mhr3c73e8jka0 and daj7a31hvn6c73cu32c0 (submitted 09:00, 09:22, 10:03 on 13 Sep) carry identical candidate_calibrations (sha256 of the sorted JSON ad13d203 on all three, and their own snapshot_sha256 bf5015a4 identical), captured at 09:00:19, 09:22:20 and 10:03:52, with active qubits [82, 83, 96, 103] on all three. Batches 1-3 share a different snapshot (8d7c0e36) and qubits 140-143. Batch 0 has its own (18567b72) and qubits 138, 151, 152, 153 | KNOWN_GOOD.md lines 32-36 (same table, its own hash convention e1ca6ed7). Copies in scratch p5/r27/ |
| how: "Our run on ibm_kingston, 24 Oct 2026" | TRACED: the run exists (qia_runs/2026-10-24-fill-usp; gift README). No number from it appears in the cells | qia_runs/2026-10-30-gift-usp/README.md |
source: qia_leads/audits/fresh_usp_2609.33255/KNOWN_GOOD.md; qia_runs/2026-10-30-gift-usp/README.md
grep: batches 4, 5, 6 carry byte-identical stated records

### 28. run_boussahi : FIX
| number | how | source |
|---|---|---|
| "21 of 21 runs reproduce" | RECOUNTED from the kept output. The reproduction has 22 circuit-runs (probe 1 + main 16 + follow-up 5, matching the 3 + 48 + 15 shot arrays at 3 settings each), and all 22 equal their analysis.csv to 4 decimals. The boussahi AUDIT line 25 says "21", a miscount. The second audit of the same paper says 22 of 22 | qia_leads/audits/boussahi_qualify/out/reproduce_stdout.txt lines 1-22 (22 lines); reproduce_rows.json (22 rows); qia_leads/audits/constantine_fez_2610_19544/AUDIT.md lines 29, 64, 93 |
| one pair "excludes a drift" (published) | TRACED: "excludes a drift of the device between the jobs" | qia_leads/audits/boussahi_qualify/src/paper.txt lines 1638-1655; qia_leads/recheck_published/src/run_boussahi.txt lines 1604-1619 |
| 1 h 54 min apart | RECOMPUTED from their job records: running 16:21:54.9Z (main) to 18:15:47.2Z (follow-up), 27 Sep 2026 = 1 h 53 min 52 s | qia_leads/audits/boussahi_qualify/out/their_jobs.json; AUDIT.md lines 18, 47 |
| mean z² 0.944, permutation null 95% [0.892, 1.112] | TRACED: mean_z2_obs 0.94373, null_p2_5 0.89202, null_p97_5 1.11151 | qia_leads/audits/boussahi_qualify/out/drift_check.json lines 3-6 |
| s difference -0.0045 (job 1 minus job 3) | TRACED: s_job1 0.68868, s_job3 0.69323, s_diff -0.004546 | drift_check.json lines 8-10 |
| null SD 0.0100 | TRACED: sd_s_diff_null 0.0099987 | drift_check.json line 11 |
| "within about 0.02 (two null SD)" | RECOMPUTED: 2 x 0.0100 = 0.020. Strictly the 2-SD band around the observed difference is [-0.0245, +0.0155], so "about 0.02" holds | arithmetic |
| "defined after the data" | TRACED: "post-hoc, defined after the data, not planned" | qia_leads/audits/boussahi_qualify/AUDIT.md line 47 |
Note: the register's source_grep "21/21 runs reproduce" carries the same miscount.
Suggested: measured: "22 of 22 runs reproduce. From their own shots, ..." (rest unchanged).
source: qia_leads/audits/boussahi_qualify/out/drift_check.json; qia_leads/audits/boussahi_qualify/AUDIT.md; qia_leads/audits/constantine_fez_2610_19544/AUDIT.md; qia_leads/audits/boussahi_qualify/out/reproduce_stdout.txt
grep: 22/22 runs reproduce

### 29. arizona_anomaly : KEEP
| number | how | source |
|---|---|---|
| baseline R 1.30 (ibm_fez) | TRACED: Table 3 "Full circuit 1.30 Start" (layout 97/106/107/108, 151 operations) | qia_leads/audits/arizona_2604.17519/src/paper.txt lines 273, 558; qia_leads/recheck_published/src/arizona_anomaly.txt lines 266, 546 |
| baseline R 1.38 (ibm_marrakesh) | TRACED: "158 operations, 37 segments, R=1.38" | paper.txt line 551; arizona_anomaly.txt line 539 |
| sx 1.17-1.93 | TRACED as the min and max of the sx medians over all 14 sweep records: 1.173 (ibm_pittsburgh, 23 Oct) to 1.931 (ibm_phoenix, 23 Oct) | arxiv_one_readout/sweep_run/results_sweep_ibm_pittsburgh.text line 8; results_sweep_ibm_phoenix.text line 8 |
| CZ 1.18-1.62 | TRACED: 1.179 (ibm_boston, 23 Oct) to 1.616 (ibm_marrakesh, 23 Oct) | results_sweep_ibm_boston.text line 9; results_sweep_3.text line 33 |
| 23-24 Oct 2026 | TRACED: all 17 sweep job records are dated 23 Oct 21:04Z to 24 Oct 12:39Z. The four band ends all come from 23 Oct records | arxiv_one_readout/sweep_run/job_sweep_*.json |
| "threshold is crossed by the stated-figure miss alone" | TRACED as the audit's projection: tau 0.029 to 0.48 (0.06 typical), "A uniform stated-to-delivered miss of 1.24 to 1.6 exceeds it" | qia_leads/audits/arizona_2604.17519/AUDIT.md lines 51, 64, 98 |
Notes: (1) The band spans every chip we measured, including chips they did not use. The chip-specific bands are narrower and still contain both values: fez CZ 1.24 to sx 1.45 (results_sweep_3.text lines 8-9, results_sweep_r2_part.text lines 8-9) contains 1.30, and marrakesh sx 1.34 to CZ 1.62 contains 1.38. Optional wording: "inside our fez (1.24-1.45) and marrakesh (1.34-1.62) bands". (2) The audit says readout (f = 1) pulls R toward 1 by a share the paper does not print, so the measured cell's "crossed by the stated-figure miss alone" is a projection, labelled as such in AUDIT line 45. Wording note only.
source: qia_leads/audits/arizona_2604.17519/AUDIT.md; qia_leads/audits/arizona_2604.17519/src/paper.txt; arxiv_one_readout/sweep_run/results_sweep_ibm_phoenix.text; arxiv_one_readout/sweep_run/results_sweep_ibm_pittsburgh.text; arxiv_one_readout/sweep_run/results_sweep_ibm_boston.text; arxiv_one_readout/sweep_run/results_sweep_3.text
grep: R 1.30 (fez) and 1.38 (marrakesh)

### 30. ucf_lbnl_mcm : FIX
| number | how | source |
|---|---|---|
| "moved z by up to 47" | TRACED but misworded. z is the shift divided by the shot-noise SD. The largest z is +47.4 (GHZReset_29, 0.0471 to 0.4544, SD 0.0086). The largest score move is +0.4273 (GHZReset_21, 0.1396 to 0.5669). All 15 rebuilt scores reproduce the printed ones. 10 of 15 have \|z\| > 3 | qia_leads/audits/ucf_lbnl_mcm_2604.03360/src/run_to_run_out.txt lines 8-23 (our script on their Zenodo 21459804 counts) |
| "their own two runs" | TRACED: ibm_pittsburgh run 1 on 5 Dec 2025 and run 2 on 1 Mar 2026 (86 days), dates decoded from their job ids | xid_dates_out.txt lines 4, 21, 35-43; AUDIT.md line 7 |
| "with identical features" | TRACED: "identical feature rows run1 vs run2: True" | run_to_run_out.txt line 5 |
| "(run-to-run hardware change)" | NOT SUPPORTED as a cause. The audit names no cause: the transpiled circuits are not saved, and the transpiler may have chosen a different reset or MCM instruction ("CORRECTED: no cause named") | AUDIT.md lines 59, 62 |
Suggested: measured: "Their own repeat of the same circuits on ibm_pittsburgh, 86 days apart with identical features, moved scores by up to 0.43 (up to 47 shot-noise widths). Cause not identified." / qia_calibration: "Q18 Run repeats and report the spread: between their own two runs the same circuits moved by up to 0.43, up to 47 shot-noise widths."
source: qia_leads/audits/ucf_lbnl_mcm_2604.03360/src/run_to_run_out.txt; qia_leads/audits/ucf_lbnl_mcm_2604.03360/src/xid_dates_out.txt; qia_leads/audits/ucf_lbnl_mcm_2604.03360/AUDIT.md
grep: z +47.4

### 31. so_2609.34411 : FIX (quote symbol only)
| number / claim | how | source |
|---|---|---|
| "same reported two-qubit gate error of 2.03×10⁻³ and measured γ of 0.68 and 0.20" (published) | TRACED, but the paper prints capital Γ (\Gamma), not γ | qia_leads/audits/melbourne_2609.34411_qualify/src/paper.txt line 313; qia_leads/recheck_published/src/so_2609.34411.txt lines 636-637 |
| 2.03e-3 pair = 20-21 and 137-147: reported 2.0254e-3 and 2.0278e-3, Γ 0.676 and 0.203 | TRACED in our output. RECOUNTED from their released datasheet_comparison/comparison_data.csv (GitHub farhadfarokhigit/multi-tenant_quantum_leakage, main, sha256 c7553949...fa6107c, 176 rows) | qia_leads/audits/melbourne_2609.34411_qualify/out/reproduce3.txt lines 8-9; scratch p5/r31/comparison_data.csv, p5/r31_pair.py |
| "also differs in idle window" | RECOUNTED: tau 82.5 vs 101.1 us | same CSV; reproduce3.txt lines 8-9; AUDIT.md line 49 |
| "and probe T2" | RECOUNTED: reported probe T2 408.6 vs 101.1 us. The ZZ coupling is the same, zeta 1215 vs 1203 Hz | same CSV; AUDIT.md line 49 |
| "cannot be put on coherence alone" | TRACED as the audit's reading: the Γ gap sits in C(tau), the decay over the idle window, with the same ZZ coupling. Attribution CANNOT_TELL | AUDIT.md lines 49, 69 |
| "IBM's reported figures in their released data" (how) | TRACED: gate_error, t1/t2, readout and sx columns in comparison_data.csv | AUDIT.md line 18 |
Note (optional wording): "coherence" can be read two ways, as the paper's coherent-vs-stochastic error or as probe T2. Clearer: "The pair with the same IBM-reported CZ error has the same ZZ coupling (1215 vs 1203 Hz) but a different idle window (82.5 vs 101.1 us) and probe T2 (408.6 vs 101.1 us), so the leakage gap cannot be put on the CZ error's coherent part."
Suggested: published: "...the same reported two-qubit gate error of 2.03×10⁻³ and measured Γ of 0.68 and 0.20" (capital Γ). Measured and qia_calibration stand.
source: qia_leads/audits/melbourne_2609.34411_qualify/AUDIT.md; qia_leads/audits/melbourne_2609.34411_qualify/out/reproduce3.txt; qia_leads/audits/melbourne_2609.34411_qualify/src/paper.txt
grep: reported probe T2 408.6 vs 101.1 us

### 32. recount_2602.16233 : KEEP
| number | how | source |
|---|---|---|
| "5.5 ms" for 12-qubit one-cut template generation | TRACED: "(5.5 ms, 33 ms, 219 ms at one, two, three cuts for 12 qubits)" | qia_leads/recheck_published/src/recount_2602.16233.txt line 918 |
| Table 2 gives 5.7 ms | TRACED: row "12 2 1 12 2.1 5.7" (qubits, parts, cuts, K, T_part, T_gen) | same file line 940 |
| 33 and 219 ms hold | RECOMPUTED: Table 2 T_gen 33.1 (line 942) and 218.7 (line 943) round to 33 and 219 | same file lines 942-943 |
| University of Melbourne | TRACED: qCLOUDS Lab, The University of Melbourne | same file lines 3-6 |
source: qia_leads/recheck_published/src/recount_2602.16233.txt
grep: 12 2 1 12 2.1 5.7

### 33. protein_qsad : FIX
| number | how | source |
|---|---|---|
| Table 2: 2% labelled "≈ IBM 2Q gate (typical NISQ)" (published) | TRACED | qia_leads/audits/protein_qsad_2607.06971/src/paper.txt lines 277, 298-302 |
| "IBM's stated medians are 6.6-10.8 times lower than 2%" | TRACED but under-specified: x7.7 (fez), x10.8 (kingston), x6.6 (marrakesh), stated CZ medians 2.60e-3, 1.85e-3, 3.04e-3 from IBM records of 21 Oct 2026. RECOMPUTED from those records (held in qia_leads/audits/quepp_2603.14485/src/ext/backend_properties_ibm_*.json, read by this row's script): 7.68, 10.79, 6.57. Their runs were on ibm_cleveland on 20 and 22 Mar 2026, a chip we never measured. On our own 23 Oct sweep records the same ratio is 8.31 / 11.46 / 8.16, so the range depends on the record date. With 2% read as a depolarizing parameter p = (4/3) r it is 4.9-8.1 (timing_and_ratios_out.txt lines 25-27) | qia_leads/audits/protein_qsad_2607.06971/src/timing_and_ratios_out.txt lines 25-27; arxiv_one_readout/sweep_run/props_sweep_ibm_{fez,kingston,marrakesh}.json; scratch p5/r33_stated.py |
| "27x" printed | TRACED: "mean speedup of 27× and a maximum of 365×" | paper.txt line 264 |
| ratio of means 14.3x | RECOMPUTED: 28,036 / 1,966 = 14.26 | paper.txt line 264; timing_and_ratios_out.txt line 11 |
| 27x is a mean of ratios | RECOMPUTED by elimination: neither the ratio of means (14.3) nor of medians (9,870 / 1,470 = 6.7) gives 27, and "mean speedup" is a mean of per-case ratios. The per-case values are not printed | timing_and_ratios_out.txt line 11 |
| time totals disagree | RECOMPUTED: "23.0 hours (mean 22.3 min per protein)". 22.3 x 101 = 2,252 min = 37.5 h. 23.0 h / 101 = 13.7 min | paper.txt line 258; timing_and_ratios_out.txt line 7 |
| RMSD disagree | RECOMPUTED: mean 2.6 Å (Sec 5.3) vs mean 2.462 Å "across all 101 proteins" (Sec 5.7). Median 2.7 Å vs 2.51 Å (end-to-end, a different selection) | paper.txt lines 262, 357, 398 |
What would settle the cleveland side: one zero-QPU historical-properties call for ibm_cleveland at 2026-03-20 and 2026-03-22 (backend.properties(datetime=...)). It works only if the account can still see ibm_cleveland.
Wording: "RMSD totals" are means and medians, not totals.
Suggested: measured: "IBM's stated CZ medians on ibm_fez, ibm_kingston and ibm_marrakesh (21 Oct 2026 records) are 6.6-10.8 times lower than 2%. Their own chip, ibm_cleveland (March 2026), is not in our records. 27x is a mean of ratios (the ratio of means is 14.3x). Time totals and RMSD averages disagree." / qia_calibration: unchanged.
source: qia_leads/audits/protein_qsad_2607.06971/src/timing_and_ratios_out.txt; qia_leads/audits/protein_qsad_2607.06971/src/paper.txt
grep: ratio of means 14.26

### 34. multichip_multipliers : FIX
| number | how | source |
|---|---|---|
| CONSISTENT | TRACED: audit outcome "CONSISTENT with bound" | qia_leads/audits/chip_multipliers/AUDIT.md line 29 |
| "Their marrakesh 1.91x" | RECOMPUTED, but it is not their number: implied per-gate error 0.0063 (0.0027-0.0081) over "the backend's reported median of 0.0033" = 1.909 (0.818-2.455). The paper prints 1.91x as the ibm_kingston multiplier (paper.txt lines 28, 354). Their marrakesh multiplier is 2.07x | qia_leads/audits/chip_multipliers/src/paper.txt lines 347-348; check_multipliers_output.txt line 19 |
| "brackets our CZ 1.62" | TRACED: our marrakesh CZ factor 1.616 [1.541, 1.750] (23 Oct) lies inside 0.82-2.45 | arxiv_one_readout/sweep_run/results_sweep_3.text line 33; check_multipliers_output.txt line 19 |
| one sentence off, 36x | RECOMPUTED: 32^(3 - 1.966) = 36.0 over p = 16 to 512 with the cubic sharing the left-hand intercept (Fig. 3 caption). "About 600" = 512^1.034 = 633, normalised at p = 1 | paper.txt lines 47-48, 197, 208; check_multipliers_output.txt lines 27-29 |
| "36 under Fig. 3's normalisation" | TRACED: Fig. 3 caption "reference sharing the left-hand intercept" | paper.txt line 197 |
Note: the audit says this is not like with like. 1.91 is a composite mirror-circuit implied error over a reported median, and ours is per-gate delivered over stated CZ.
Suggested: measured: "CONSISTENT. Their marrakesh implied per-gate error 0.0063 (0.0027-0.0081) over the reported median 0.0033 is 1.91 (0.82-2.45), which contains our CZ factor 1.62. One sentence off: 36x, not about 600." / qia_calibration: unchanged.
source: qia_leads/audits/chip_multipliers/check_multipliers_output.txt; qia_leads/audits/chip_multipliers/src/paper.txt; arxiv_one_readout/sweep_run/results_sweep_3.text
grep: ratio 1.91 (0.82-2.45)

---

## Methods notes
- Authors' public data fetched on 30 Oct 2026 into SCR, read as data with python3 -I, none of their code run: arXiv 2609.35163v1 PDF (r06, Fig. 5 vectors re-read with PyMuPDF); GitHub 0Shunya0/VQE_LGT results JSONs (r15); anonymous.4open.science suture_source a3_hardedge_summary.csv (r16); Hugging Face sahilfarib/quantum-noise-transfer calibration_A/B.json (r24); GitHub saeg/quanifi-replication job manifests (r27); GitHub farhadfarokhigit/multi-tenant_quantum_leakage comparison_data.csv (r31).
- Our own kept data re-read: run folders under qia_runs (fire-2608.04486, fire-2603.13536, fill-marmara, fill-qusoft, fire-t10, fill-geopump), arxiv_one_readout/sweep_run and control_run results, and the audit folders named per row.
- Independent recounts written for this pass: SCR/r03/nz.py (nus_zib Table 1 intervals, with a shot-number sensitivity), SCR/r06/fig5.py and labels.py (kisti Fig. 5), SCR/r24_cx.py, SCR/r27_man.py, SCR/r31_pair.py, SCR/r33_stated.py, and the nikhef recount in SCR/r13/.
- Not done (would need an IBM call): ibm_cleveland historical properties at 2026-03-20 and 2026-03-22 for protein_qsad (backend.properties(datetime=...), zero QPU, only if the account can still see ibm_cleveland). No other row needs one.
- Rows where Bones has to choose wording: run_geopump (Q13 / "spectator cost" do not match what the run measured, none of Q12-Q14 fits as written), nus_zib (keep the inferred counts with the inference named, or drop the counts).
