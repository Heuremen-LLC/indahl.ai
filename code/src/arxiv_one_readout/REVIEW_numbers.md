# Adversarial audit of arxiv_one_readout/main.tex: numbers, data and references

Audit date 2026-10-21. main.tex was NOT edited. Everything below was run or fetched during the audit.

Status key: MATCH = I reproduced the value from released data or by arithmetic on sourced numbers. MATCH-TEXT = equals a value printed in a project file, but I could not recompute it from data that ships with the release. MISMATCH = paper disagrees with source, or is internally inconsistent. UNSOURCED = no computation or source found.

Tally (this table): MATCH 52, MATCH-TEXT 18, MISMATCH 2, UNSOURCED 3, total 75 rows (some rows cover a whole table or list of numbers).

## 1. Scripts run

- `verify.py` (python3, from its directory): runs offline (standard library only; no network calls in the source). Exit clean. Sections 1-6 all print OK: per-chip R (cut) all seven identical; pooled 1.0207 +- 0.0092, chi2/dof 0.52, p 0.79; no-cut pooled 1.0405, chi2/dof 2.22, p 0.0384; 30 of 284 negative; pooled 1.0331 +- 0.0083, chi2/dof 0.88, 4.0 sigma vs 1, 7.0 sigma vs 12/11 (7.6 with negatives).
- `recompute_table.py`: ran as `python3 -I recompute_table.py <three-positions dir>`. It REQUIRES that path argument (the paper's data statement does not mention it). Output reproduces every Tab 1 row (n_all, n_above, n_neg, R cut, R non-neg, widths). rc=0.
- `split_seven_chips.py --planted`: ran, reproduces the whole injection table (0/0.1/0.2/0.5/1/2/5 us and P=1.0/1.0331/1.05/1.1).
- `split_seven_chips.py` (no flag, the intercept fit): FAILS with FileNotFoundError on `data/fire/ibm_marrakesh/run311_meta.json`. The raw `data/fire/` tree is not in the release (only `data/clocks`, `data/reads`). The intercept -0.036 +- 0.038 and Tab 3 therefore cannot be reproduced by a reader from the released files; I could only verify the pooling arithmetic from the Tab 3 values and match the table to `THE_APPARATUS_TERM_20261011.txt`.
- `chip_independence.py`: ran; verdict text matches the paper.
- Own checks (python/scipy): inverse-variance pooling of Tab 1 both ways; negative-population median ratio 0.28379; Spearman in negatives -0.0665; across-chip Spearman 0.8929 with exact permutation p 0.0123 (two-sided); Fisher exact on 100/1216 vs 15/608 = 5.9e-7; Rigetti per-job P/S aggregates; THE_COUNT shape-exponent means/sds.
- Rigetti: `readrigetti_look_lengths.py` needs `lookLengths_*.npz` and `cepheus_props_20260928.json`, which are NOT in the release folder (`time20261004/` is empty). I re-ran it from a scratch copy against /Users/heuremen/bones-forge/standoff/ and reproduced the four no-tone controls and the four 'ACROSS THE FOUR LENGTHS' lines exactly.

## 2. Number table

| # | number | location | paper value | reproduced value | status | note |
|---|---|---|---|---|---|---|
| 1 | Pooled R, cut only | Sec 3.1, Tab1, Sec 5 | 1.0207 +- 0.0092 | 1.0207 +- 0.0092 (verify.py s3; my own inverse-variance pooling of Tab 1 gives 1.0207, 0.0092) | MATCH |  |
| 2 | chi2/dof, p (cut only) | Sec 3.1 | 0.52; p=0.79 | 0.52; 0.794 | MATCH |  |
| 3 | SE from 1 (cut only) | Sec 3.1, Sec 5 | 2.2 | 2.25 (verify.py prints 2.2) | MATCH |  |
| 4 | Pooled R, non-negative | Abstract, Sec 3.1, Tab1, Sec 5 | 1.0331 +- 0.0083 | 1.0331 +- 0.0083 (verify.py s6; recomputed from Tab 1: 1.0331, 0.0083) | MATCH |  |
| 5 | chi2/dof, SE from 1 (non-neg) | Sec 3.1, Sec 5 | 0.88; 4.0 | 0.885; 4.01 | MATCH |  |
| 6 | 254 spectators | Abstract | 254 | 284 - 30 = 254 | MATCH |  |
| 7 | 284 of 524 spectator readings; 30 negative | Sec 2 Cuts, Tab1 | 284/524; 30 | 284/524 and 30 (verify.py s6; per-chip nall sums to 524, nabove to 284) | MATCH |  |
| 8 | Tab1 R(cut), 7 chips | Tab1 | 1.0457,1.0266,1.0282,1.0256,1.0172,1.0166,1.0022 | identical (verify.py s2 and recompute_table.py) | MATCH |  |
| 9 | Tab1 widths (cut), 7 chips | Tab1 | 0.0198,0.0495,0.0359,0.0215,0.0364,0.0306,0.0157 | identical (recompute_table.py, seed 20261011, 400 resamples) | MATCH |  |
| 10 | Tab1 R(non-neg) + widths, 7 chips | Tab1 | 1.0553/0.0238, 1.0453/0.0187, 1.0652/0.0386, 1.0410/0.0209, 1.0246/0.0391, 1.0336/0.0197, 1.0046/0.0161 | identical (recompute_table.py) | MATCH |  |
| 11 | Tab1 n column (43,43,31,27,23,63,54) | Tab1 | as shown | identical | MATCH | Pooled row n=284 is the cut-only n; the non-neg column pools 254, not 284 (caption says 'n counts spectators') |
| 12 | Tab1 neg. column (3,8,5,2,1,9,2 = 30) | Tab1 | as shown | identical | MATCH |  |
| 13 | Tab1 'spect. (us)' column | Tab1 + caption | 2.30,2.28,2.86,2.27,2.23,2.01,1.67 ('R x L') | Equals R(non-neg) x L for every chip (e.g. kingston 1.0553x2.18=2.30). R(cut) x L would be 2.28,2.24,2.76,2.24,2.22,1.97,1.66 | MISMATCH | Caption says 'R x L' without saying which R; the column silently uses the non-negative R, while the column sits next to both. Clarify. |
| 14 | Per-chip SE from 1: 'between 0.1 and 2.4' | Sec 3.1, 3.2, 5 | 0.1-2.4 | cut: 0.14-2.31; non-neg: 0.29-2.42 | MATCH |  |
| 15 | ibm_fez R = 1.0046 +- 0.0161 | Sec 3.1 | 1.0046 +- 0.0161 | 1.0046 +- 0.0161 | MATCH |  |
| 16 | Specification L (2.18 x4, 1.66, 1.94, 2.684) | Sec 2 | as shown | data/clocks stated_look_us identical | MATCH |  |
| 17 | Chip rates 2.91-10.25 deg/us | Sec 2 Circuits | 2.91-10.25 | results.json clock_rate_deg_per_us min 2.9088 (aachen), max 10.2536 (phoenix) | MATCH | Per-clock rates reach 28.99 (Amendment 02); paper says 'chip-level', fine |
| 18 | Spearman(rate, duration) -0.17 to -0.56 | Sec 2 Cuts | -0.17 to -0.56 | -0.170 to -0.558 (verify.py s1) | MATCH | results.json still says -0.20 to -0.34 (stale) |
| 19 | 4 deg/us cut; keep rule 0.15, 3 widths; window (-5,60); ladder {1,2,3,4,6,9}; delays 0..240; fit delays 10,20,30 | Sec 2 | as shown | split_seven_chips.py constants (CUT, LOOKS, WIN, WINDOW, keep rule) agree | MATCH | Fit through delays 10/20/30 not independently checked in code |
| 20 | Bootstrap 400 resamples, fixed seed | Sec 2 | 400, fixed seed | recompute_table.py: 400, seed 20261011 | MATCH |  |
| 21 | Injection slope ratios 0/0.2/1.0/5.0 -> 1.0007/1.0011/1.0026/0.9994 | Abstract, Sec 3.3 | 1.0007,1.0011,1.0026,0.9994 | 1.0007,1.0011,1.0026,0.9994 (split_seven_chips.py --planted, run by me) | MATCH | Re-run output identical, so seeded |
| 22 | Recovered intercepts -0.0042, 0.1907, 0.9775, 5.0000 | Sec 3.3 | as shown | identical | MATCH |  |
| 23 | Extra plants 0.1, 0.5, 2.0 'within 1.0026 of unity' | Sec 3.3 | within 1.0026 | 0.9991, 1.0017, 1.0009 | MATCH |  |
| 24 | Planted P=1.0331 returns 1.0342 | Sec 3.3 | 1.0342 | 1.0342 | MATCH |  |
| 25 | Injection design: L=1.66, noise 0.30, 400 fits | Sec 2 | as shown | planted() in code: L=1.66, rng.normal(0,0.30), 400 | MATCH |  |
| 26 | Intercept S = -0.036 +- 0.038 us | Abstract, Sec 3.3 | -0.036 +- 0.038 | -0.0361 +- 0.0375 from inverse-variance pooling of the 7 Tab3 S values (my calc); THE_APPARATUS_TERM prints the same | MATCH | Underlying per-chip S need raw data not in release (see data-availability) |
| 27 | chi2/dof of S, 0.18 on 6 dof | Sec 3.3 | 0.18 | 0.177 | MATCH |  |
| 28 | Mean P=1.047, chip sd 0.022 | Sec 3.3 | 1.047; 0.022 | 1.0469; 0.0221 (from Tab3 P column) | MATCH |  |
| 29 | 21 runs, 767 spectators | Abstract, Sec 3.3 | 21; 767 | 7 chips x 3 reads = 21; 76+113+106+152+85+167+68 = 767 | MATCH |  |
| 30 | Tab3 S, P and spectators, 7 chips | Tab3 | as shown | match THE_APPARATUS_TERM_20261011.txt row for row (all rounding consistent) | MATCH-TEXT | Not recomputable: split_seven_chips.py needs data/fire/*/run*_meta.json, absent from release |
| 31 | 305 jobs; 86/75/55/25/24/20/20 | Abstract, Sec 2 | 305; per chip as shown | runs.json: n_runs 305; Counter identical; 305 unique job_ids | MATCH |  |
| 32 | 302 with submission time; 2026-10-02 to 10-07 US Eastern | Sec 2 | 302; 10-02..10-07 | 3 null (aachen, kingston, pittsburgh); min 2026-10-02T08:47-04:00, max 2026-10-07T14:53-04:00 | MATCH |  |
| 33 | SHA-256 of each script frozen before submission | Sec 2 | ledger records it | Every runs.json row has code_sha256; frozen-before-submission is not checkable | MATCH-TEXT | Dense fez run (11 Oct) is NOT in the ledger (its 'runs 901-903' are unrelated pittsburgh entries in the ledger) |
| 34 | Seven backends named | Sec 2 | kingston,pittsburgh,marrakesh,fez,aachen,boston,phoenix | same seven in runs.json | MATCH |  |
| 35 | No-cut pooled/chi2/p: 1.0405, 2.22, 0.0384 | Sec 5 | 1.0405; 2.22; 0.0384 | verify.py s5 identical | MATCH | chi2 13.3 on 6 dof -> p=0.038 checks |
| 36 | No-cut 'released summary' chi2/dof 2.93, p=0.0074 | Sec 5 | 2.93; 0.0074 | results.json why_the_cut says the same; 17.6 on 6 dof -> p=0.0074 is self-consistent | MATCH-TEXT | Two released sources disagree (2.93 vs 2.22); paper discloses this |
| 37 | Aachen 69% below cut | Sec 5 | 69% | 51/74 = 68.9% | MATCH |  |
| 38 | Two-point scatter 0.0325 vs fit 0.0183; 2.4x the printed width | Sec 5 | 0.0325, 0.0183, 2.4 | results.json two_estimators text; 0.0325/0.0138 = 2.36 | MATCH-TEXT | Source for 0.0138 is results.json text only |
| 39 | 12/11 excluded at 7.0 (7.6) SE | Sec 5 | 7.0; 7.6 | 7.01; 7.61 | MATCH |  |
| 40 | 30/284 = 10.563 +- 1.824 % | Sec 5 | 10.563 +- 1.824 | 30/284 = 10.563 %; sqrt(p(1-p)/n) = 1.824 % | MATCH |  |
| 41 | |median negative| / median positive = 0.28379 +- 0.04477 | Sec 5 | 0.28379 +- 0.04477 | point value 0.28379 reproduced from data/clocks; width only in CALL text | MATCH | Width not recomputed (bootstrap spec absent) |
| 42 | Spearman(detuning, value) in negatives = -0.067, n=30 | Sec 5 | -0.067 | -0.0665 (n=30) | MATCH |  |
| 43 | Across-chip Spearman +0.893, n=7, exact p=0.0123 | Sec 5 | +0.893; 0.0123 | 0.8929; exact two-sided p = 0.0123 (5040 perms) | MATCH | One-sided is 0.0062 |
| 44 | Negative fraction 8.22 % edges vs 2.47 % middle, Fisher p=5.9e-7 | Sec 5 | 8.22; 2.47; 5.9e-7 | Counts 100/1216 vs 15/608 (Amendment 01) give Fisher p = 5.9e-7 (scipy) | MATCH | Denominators are 1,216/608 clock-by-k ROWS (3,354 total), not the 284 spectators; the paper does not say so and sits the sentence next to '30 of 284' |
| 45 | Rigetti negative fraction 35.2 % (515/1463); 36.99 vs 35.62 % | Sec 5 | as shown | 515/1463 = 35.20 %; other figures in Amendment 02 text | MATCH-TEXT | Rigetti npz not in release dir |
| 46 | P2 Spearman 0.097, 0.280; threshold 0.3; P1 failed, P3 not runnable | Sec 5 | as shown | Amendment 02 text agrees | MATCH-TEXT |  |
| 47 | Chip-independence: no pair survives; resolves overlap > ~0.8 | Sec 5 | as shown | chip_independence.py re-run: 'no pair survives correction ... cannot resolve Jaccard below about 0.8' | MATCH |  |
| 48 | Per-chip samples 23-63 | Sec 5 | 23-63 | min 23 (aachen), max 63 (phoenix) | MATCH |  |
| 49 | 'Seven of the eight processors from one vendor' | Sec 5 | 7 of 8 | 7 IBM + 1 Rigetti | MATCH |  |
| 50 | Pre-registered calls: 21 read, 3/2/2/1/12/1; 11 missed before re-read | Abstract, Sec 5 | 12 of 21 missed; breakdown | trail/index.html scoreboard identical; sums to 21; coin/CHAIN_FIT_EVAL.md F26 lists 4 land / 11 miss (older) | MATCH-TEXT | Not reproducible: hashed calls are narrative, not data |
| 51 | Rigetti no-tone controls 0.9922, 0.9881, 1.0005, 0.9919 | Sec 3.4 | as shown | Re-ran readrigetti_look_lengths.py on the 4 npz: 0.9922, 0.9881, 1.0005, 0.9919 | MATCH | Needed npz from /Users/heuremen/bones-forge/standoff/ and cepheus_props_20260928.json; NEITHER is in the released Rigetti folder (time20261004/ is empty) |
| 52 | Rigetti blind-fit P=1.0114 +- 0.0045, S=+0.0352 +- 0.0147 (3 jobs) | Sec 3.4 | as shown | From per-job values 1.0067/1.0203/1.0071 and 0.0179/0.0233/0.0645: mean 1.0114, sd/sqrt3 = 0.0045; 0.0352, 0.0147 | MATCH | Per-job values come from the HTML table, not recomputed from raw |
| 53 | Rigetti 4 jobs P=0.9930 +- 0.0186, S=+0.0544 +- 0.0219 | Sec 3.4 | as shown | 0.9930, 0.0186; 0.0544, 0.0219 (same per-job values + s06 0.9381/0.1121) | MATCH |  |
| 54 | Rigetti weighted: P=0.9561 +- 0.0101, S=+0.1018 +- 0.0265; 35.40 vs 36.0 | Sec 3.4 | as shown | THE_SECOND_VENDOR html amendment text; per-job values not printed | MATCH-TEXT | Cannot tell how many jobs the weighted fit uses (paper does not say) |
| 55 | Difference 0.0552 = 'four times' the quoted width | Sec 3.4 | 0.0552; 4x | 1.0114-0.9561 = 0.0553; /0.014 = 3.9 | MATCH |  |
| 56 | Offset significance 2.4 and 3.8 SE | Sec 3.4 | 2.4; 3.8 | 0.0352/0.0147=2.39; 0.1018/0.0265=3.84 | MATCH |  |
| 57 | Offset-only ratios 1.020-1.031 (blind), 1.058 (weighted); mean laid 1.75 | Sec 3.4 | as shown | 1+0.0352/1.75=1.020; 1+0.0544/1.75=1.031; 1+0.1018/1.75=1.058 | MATCH |  |
| 58 | Withdrawn 1.035 +- 0.014, 11 Oct 2026 | Abstract, Sec 3.4, 5 | as shown | Rigetti index.html and THE_SECOND_VENDOR html agree | MATCH-TEXT |  |
| 59 | Rigetti laid looks 1.0/1.5/2.0/2.5; 100 clocks per job; 'late September and 2026-10-04'; Cepheus-1-108Q | Sec 2 | as shown | txt output (1.00,1.50,2.00,2.50; 'W' per length); index.html 'late September and 4 October 2026' | MATCH | Excluded files r1 (strength 0.045) and tuned (0.12) confirmed in THE_SECOND_VENDOR txt |
| 60 | Rigetti offset 'about 0.04 us' | Abstract | 0.04 | 0.0352 (3-job blind) / 0.0544 (4-job) / 0.1018 (weighted) | MATCH | Abstract quotes the smallest of the three; body gives 0.04-0.10 |
| 61 | Dense fez run: 2026-10-11, 3 jobs, k=1..128 | Sec 2, Sec 3.5 | as shown | THE_COUNT: runs 901-903, 14 counts 1..128; date from index.html | MATCH-TEXT |  |
| 62 | Dense run: 4,179 measurements | Sec 3.5 | 4179 | Appears verbatim in index.html and trail; sum of k over the 14 counts x 3 jobs = 1332; cannot be derived from THE_COUNT | UNSOURCED | No derivation found |
| 63 | Worst chi2/dof 1.38 | Sec 3.5 | 1.38 | THE_COUNT run 902 seat 1: 1.380 (other fits 0.715,1.122,0.657,1.319,1.354; seat 3 values 22-32 are excluded as 'six fits') | MATCH |  |
| 64 | Shape exponents 0.823 +- 0.013 and 1.381 +- 0.074 | Sec 3.5 | as shown | per-read b: 0.829/0.809/0.832 -> mean 0.8233, sd 0.0125; 1.296/1.433/1.415 -> mean 1.3813, sd 0.0744 | MATCH | Width is the read-to-read sd (n=3), not a fit error |
| 65 | Cost vs idle 0.99-1.03 up to 9; 1.16-1.18 at 27 | Sec 3.5 | as shown | index.html / what-we-measured.html text | MATCH-TEXT | Paper says not re-analysed |
| 66 | '2.32 us' spectator and '3.79 us' qubit for 2.18 us spec | Abstract, Sec 3.2, Sec 5 | 2.32; 3.79 | 2.32 = ibm_kingston entry in trail (3 reads, 2-point). 3.79: no computation anywhere; Tab2 qubit values are 4.05/3.66/3.06/3.5 (simple mean of the three 4 Oct chips 3.59) | UNSOURCED | Paper flags itself with a TODO; abstract still states both without the caveat |
| 67 | Tab2 marrakesh 2.80/4.05/1.51/1.45 | Tab2 | as shown | trail/index.html identical; 4.05/2.684=1.509, 4.05/2.80=1.446 | MATCH-TEXT | Trail elsewhere gives marrakesh '1.00 / 1.52 / 1.52' |
| 68 | Tab2 kingston 2.32/3.66/1.68/1.57 | Tab2 | as shown | trail identical; 3.66/2.18=1.679; 3.66/2.32=1.578 (rounds to 1.58, trail says 1.57) | MATCH-TEXT | Rounding from unrounded source |
| 69 | Tab2 pittsburgh 4 Oct 2.27/3.06/1.40/1.35 | Tab2 | as shown | trail: '2.27 / 3.06 us; 1.040, 1.40, 1.35'; but trail elsewhere: '1.04 / 1.34 / 1.29' | MATCH-TEXT | Source has two different values for the same Pittsburgh 4 Oct read |
| 70 | Tab2 pittsburgh 2 Oct 2.37/3.5/1.606/1.477 | Tab2 | as shown | trail identical; 3.5/2.18=1.606; 3.5/2.37=1.477 | MATCH-TEXT |  |
| 71 | Tab2 fez --/--/1.54/1.51 | Tab2 | as shown | trail: '1.024 / 1.54 / 1.51' | MATCH-TEXT |  |
| 72 | Kingston 1-9 fit 1.59-1.74 vs 1.68 | Sec 3.2 | 1.59-1.74 | trail: '1.04-1.07 / 1.59-1.74 / 1.50-1.63' | MATCH-TEXT |  |
| 73 | q/spectator 1.22-1.35 (Boston, Pittsburgh, Phoenix), 1.45-1.78 (Kingston, Fez, Marrakesh) | Sec 3.2 | as shown | index.html / what-we-measured.html text; no per-chip derivation in the release | UNSOURCED | No per-chip numbers for Boston/Phoenix/Kingston range endpoints; also Pittsburgh 2 Oct q/spect = 1.477 lies OUTSIDE the 1.22-1.35 range assigned to Pittsburgh (Tab2) |
| 74 | 'Seven of seven' ordering | Abstract | 7 of 7 | Sec 3.2 states the second inequality is supported on six chips (no aachen value); the abstract does not say so | MISMATCH | Abstract contradicts body |
| 75 | Raw data ~22 GB | Sec 5, Data | 22 GB | README.md and results.json 'raw_data' | MATCH-TEXT |  |

Notes on the headline numbers asked about:
- 1.0331 +- 0.0083: reproduced three ways (verify.py, recompute_table.py, my own pooling). Abstract "254 spectators" is 284-30. The keeping-all value 1.0207 +- 0.0092 also reproduced.
- Planted costs 0, 0.2, 1.0, 5.0 us -> 1.0007, 1.0011, 1.0026, 0.9994: exact. Recovered intercepts exact.
- Intercept -0.036 +- 0.038 us, 21 runs, 767 spectators: arithmetic reproduced from Tab 3; per-spectator fits are not reproducible from the release.
- Job count 305 and per-backend counts exact. Date span: 302 stamped jobs span 2026-10-02 to 2026-10-07 (US Eastern); 62/42/26/47/125 jobs on 2/4/5/6/7 Oct; 3 null (aachen, kingston, pittsburgh).
- The paper's own TODOs (2.32 / 3.79 untraceable, no aachen qubit value) are confirmed as real gaps.

Other findings:
1. Abstract vs body: abstract says the ordering is "reported on seven of seven"; Sec 3.2 says the second inequality is supported on six. Also the abstract quotes 2.32 and 3.79 although the body says they are untraceable and "illustrative".
2. Tab 1 last column ("R x L") equals R(non-neg) x L, not R(cut) x L; caption does not say which.
3. Tab 1 pooled n=284 is for the cut-only column; the non-negative column pools 254.
4. Pittsburgh 2 Oct q/spectator = 1.477 sits in the range (1.45-1.78) the text assigns to the other group of chips, and above the 1.22-1.35 assigned to Pittsburgh. The trail page gives two different 4 Oct values for Pittsburgh (1.40/1.35 and 1.34/1.29) and two for Marrakesh (1.51/1.45 and 1.52/1.52).
5. The 8.22 % vs 2.47 % edge/middle fractions are over 1,216 and 608 clock-by-k rows (3,354 total, Amendment 01), not over the 284 spectators the preceding sentence discusses.
6. `verify.py` section 5 says the cut "is stated in advance"; the paper (correctly) says it was introduced after aachen looked like an outlier. The released script text contradicts the paper's own, more honest, account.
7. results.json still carries the superseded Spearman range (-0.20 to -0.34) and the no-cut 2.93/0.0074 that disagrees with verify.py's 2.22/0.0384 (the paper discloses the latter).
8. The 4,179 measurement count cannot be rebuilt from the ladder (sum k = 444 per job, 1,332 over three jobs).
9. The dense fez run (11 Oct) is not in runs.json, so the "SHA-256 frozen before submission" statement does not cover it. `runs.json` run numbers 901-903 are Pittsburgh entries from 6-7 Oct; the dense run uses the same numbers on fez (a different chip), which is a naming collision, not an error.
10. Rigetti: the paper does not state how many jobs enter the weighted fit (0.9561 +- 0.0101); the source does not either. Abstract's "about 0.04 us" is the low end of the 0.04-0.10 range in the body.

## 3. Data availability
- https://heuremen.org/experiments/2026-10-04-three-positions/ : HTTP 200 (curl -L).
- doi:10.5281/zenodo.23169756 : HTTP 404 at doi.org and at zenodo.org/records/23169756, as expected for a reserved draft. Do not submit with the DOI presented as live until it is published.
- Statement says `split_seven_chips.py (with --planted)` "produces the intercept fits and the injection test": true only for the injection test; the intercept fit needs the unreleased 22 GB raw tree.
- Statement says `recompute_table.py` is "supplied with this manuscript": it needs the path argument; `-I` flag in its docstring.
- The Rigetti results (Sec 3.4, negative-fraction held-out test) cannot be reproduced from the Rigetti experiment folder: `time20261004/` is empty and `cepheus_props_20260928.json` is missing; the arrays live in /Users/heuremen/bones-forge/standoff/.

## 4. References (arXiv API queried for all 20 IDs on 2026-10-21; all IDs exist)
| key | arXiv ID | title/authors/journal vs refs.bib | how main.tex cites it | status |
|---|---|---|---|---|
| Gambetta2006 | cond-mat/0602322 | match; PRA 74 042318 | MID in own resonator, dispersive regime: accurate. Intro sentence adds "and its neighbours" for [Gambetta, Boissonneault, Sank]: these papers treat a single qubit-resonator system | OK (minor overreach in Intro line 1) |
| Boissonneault2009 | 0810.1336 | match; PRA 79 013819 | accurate for dephasing/relaxation of the measured qubit | OK (same overreach) |
| Sank2016 | 1606.05721 | match; PRL 117 190503 | MIST at higher photon number: accurate | OK |
| McClure2016 | 1503.01456 | match; PR Applied 5 011001 | driven reset of resonator: accurate | OK |
| Bultink2016 | 1604.00916 | match; PR Applied 6 034008 | active resonator reset: accurate | OK; bib lacks doi (10.1103/PhysRevApplied.6.034008) |
| Walter2017 | 1701.06933 | arXiv title is "Realizing Rapid, High-Fidelity, Single-Shot Dispersive Readout..."; bib uses the journal title; PR Applied 7 054020 | cited among ways to shorten resonator emptying; paper is about fast readout via linewidth, Purcell filter, parametric amp, not depletion/reset | WEAK fit |
| Heinsoo2018 | 1801.07904 | match; PR Applied 10 034040 | dephasing of unintentionally measured qubits in multiplexed readout: abstract confirms | OK |
| Swiadek2024 | 2307.07765 | match; PRX Quantum 5 040326 | dynamic control of dispersive shift: accurate | OK |
| Chen2023 | 2208.05879 | match; npj QI 9 26 | cited in the group "ways to shorten resonator emptying (driven reset, active depletion, dynamic control of dispersive shift)". The paper is shelving + two-tone readout + ML, 140 ns, no amplifier; it is not about resonator depletion | MISCHARACTERISED in that group |
| Malekakhlagh2022 | 2206.12467 | match; PRA 106 052601 (doi from API) | cited for dephasing of unmeasured qubits "treated theoretically for bus-mediated coupling". Abstract: general time-dependent SW-Lindblad theory with a single dispersively read transmon as case study; nothing on neighbours or bus coupling | MISCHARACTERISED |
| Sundaresan2020 | 2007.02925 | match; PRX Quantum 1 020318 | spectator errors in fixed-frequency (cross resonance): accurate | OK |
| Kandala2021 | 2011.07050 | match; PRL 127 130501 | ZZ in fixed-frequency transmons: accurate | OK |
| Ketterer2023 | 2303.14103 | match; PR Applied 20 034065 | crosstalk on IBM chips: accurate | OK; bib lacks doi (10.1103/PhysRevApplied.20.034065) |
| Zhao2021 | 2110.12570 | title/authors match; published PRX Quantum 3 020301 (2022) | crosstalk in fixed-frequency transmons with tunable bus: accurate | OK; bib is @misc with year 2021 and no journal; cite the published version |
| Vallesa2026 | 2503.13225 | match; PRL 136 200801 (2026), doi 10.1103/wdfj-4nbt per API | "spectator effects during readout and their mitigation with tunable couplers": abstract covers single/two-qubit gates AND readout, so acceptable | OK |
| Corcoles2021 | 2102.01682 | match; PRL 127 100501 | dynamic circuits on IBM hardware: accurate | OK |
| Rudinger2022 | 2103.03008 | match; PR Applied 17 014014 (Crossref confirms; bib lacks doi 10.1103/PhysRevApplied.17.014014) | Intro says "Mid-circuit measurement on IBM hardware has been characterised with gate-set tomography and with a RB suite". Rudinger et al. measured a transmon in a Raytheon BBN multiqubit system, not IBM hardware | MISCHARACTERISED (IBM claim wrong for this citation) |
| Govia2023 | 2207.04836 | match; New J. Phys. 25 123016 | RB suite for measured and spectator qubits, IBM Falcon: accurate | OK |
| Mundada2019 | 1810.04182 | match; PR Applied 12 054023 | listed under "fixed-frequency transmon processors": it is a tunable-coupler circuit | WEAK fit; bib lacks doi (10.1103/PhysRevApplied.12.054023) |

No wrong IDs and no title/author mismatches. Author lists are truncated with "others" in several entries (apsrev will print literally "and others"; replace with full lists or `et al.` handling before submission).
