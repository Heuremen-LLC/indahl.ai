# Processors and apparatus: six published numbers, rechecked from the data

Run `python3 verify_processors_apparatus.py` (standard library only, about one second). It reads the three files in `data/` (0.8 MB) and prints each published claim beside the value it recomputes, marked OK or DIFFERS, with NOTE lines where the wording of a claim is not what the data say.

`extract_from_raw.py` shows how the JSON was cut from the private raw job output (numpy plus about 26 GB of raw I/Q files, not published). Nobody needs to run it to check the numbers. Nothing here submits an IBM job or uses the network.

Plain-language terms: a **look** is a qubit readout. A **clock** (spectator) is an untouched qubit held in superposition whose phase turns at a steady rate, so its phase says how much time passed. The **maker's value** is the manufacturer's stated number. A **push** is an X gate. A **park** is an idle method. A **ruler** is an estimator.

## Summary of what holds

| # | Claim | Recomputed | Verdict |
|---|---|---|---|
| 1 | Chips sort into two groups, 1.22-1.35 and 1.45-1.78, matching the maker's T2:T1 ordering; rank agreement +0.98, +0.93 | Ratios, ranges and both rank agreements reproduce (1.227 not 1.22). The "matches T2:T1 ordering" wording does not hold for Phoenix or within the high group. Aachen is the missing seventh chip and falls in the low group at 1.207 | Numbers OK, wording overstated |
| 2 | Decay time drifts between jobs, steady within one: Marrakesh 174/177/181, Kingston 260-266, Pittsburgh 294-297 | Numbers reproduce, but they are the three ruler copies inside the jobs, not three jobs | Mis-described |
| 3 | Idle control: three parking methods +0.0017/+0.0020/+0.0014; idle |0> gains +0.02 +- 0.15 % | All reproduce. The parking runs start in |1> with X gates, not "|0> and left". One chip | Numbers OK, description wrong |
| 4 | Below the single-exponential extrapolation at 30 us on 62-84 % of qubit-copies | Reproduces exactly from seven jobs on three chips | OK |
| 5 | Leakage capped at 0.26 +- 0.12 % per X gate | Raw shifts and the 1.48 degree gate shortfall reproduce. 0.26 equals four times the fitted linear term; the factor 4 is undocumented. It is a 2.2-sigma value, not an upper bound, and it covers all count-growing errors | Unverified convention |
| 6 | Simulated plant: nothing planted reads 1.000, 4 % reads 1.037-1.039 | Reproduced by a re-implementation (original script is not on disk) | OK within seed scatter |

## 1. The processor sort

**What is measured.** The looked-at qubits fade faster than plain idling would make them. T is the length of one look as read from the looked-at qubits' own decay (a qubit read k times, its level converted to "equivalent plain fading time", slope over k = 1, 2, 3, 4, 6, 9). W is the length of one look as read from untouched spectator qubits' phase turning (slope over the same k). The sort statistic is T/W.

**Source.** Look-ladder jobs on 4-6 October 2026, runs 311-313 Marrakesh, 331-333 and 661 Kingston, 351-353 and 511 Pittsburgh, 411-413 and 671 Fez, 431-433 Boston, 541-543 and 581-583 Phoenix, 801-803 Aachen. Job IDs are in `data/sort_witness_and_looked_at.json`. Private reader: `parallax/out/qubit_fifth_run/six_blind.py`, output `data/reads/six_blind_20261007.txt`. Ledger: `THIRD_RUNG_20260928.md`, sections 295, 317, 389.

**Reproduction.** The stdlib code reproduces all eight chip-days of the private script to the printed digit (pooled, blind and seeing), and the rank agreements +0.98 (pooled vs blind) and +0.93 (pooled vs seeing). "Blind" keeps spectators with no looked-at qubit within two bit pitches; "seeing" keeps those with two or more.

**Discrepancies.**
- **Aachen.** The page says seven processors. The ranges and the rank agreements cover six (Marrakesh, Kingston, Fez, Boston, Pittsburgh, Phoenix), and the rank agreements cover only five heavy-hex chips over eight chip-days. Phoenix was never run through the pooled/blind/seeing script, and neither was Aachen. Run with the same code, Aachen gives T/W 1.207 (blind 1.259, seeing 1.156): it joins the low group and would make that group 1.21-1.35. No Aachen T2:T1 is on file.
- **The low end.** The lowest Boston/Pittsburgh/Phoenix value is 1.227, not 1.22.
- **Phoenix and T2:T1.** The maker's median T2:T1 for Phoenix is 0.851 (below 1, like Kingston 0.638, Fez 0.683, Marrakesh 0.519), yet its T/W is 1.28-1.35, with Boston and Pittsburgh (T2:T1 1.18 and 1.16). So the published grouping does not follow T2:T1 for Phoenix. The ledger already says so (section 261: "the split does NOT carry to the square lattice").
- **Ordering versus split.** Across the six chips, T/W against maker T2:T1 gives a rank correlation of -0.77. The two chips with T2:T1 above 1 are the two lowest in T/W (1 chance in 15 by luck, six chips). Inside the high group the T/W order is Marrakesh, Kingston, Fez, the reverse of the T2:T1 order. The data support "T2:T1 above 1 sorts low", not an ordering.
- **Two groups or a continuum.** The gap at the claimed boundary is 0.099 (Phoenix 1.346 to Marrakesh 1.445). The largest gap anywhere is 0.210, inside the high group. Fez alone moves 0.220 between two days. Eleven chip-day values are too few to tell two groups from a continuum.
- **What +0.98 and +0.93 measure.** They are agreements between three ways of choosing spectators (all, blind, seeing), not agreements between T/W and the maker's number.

## 2. T1 drift

**What is measured.** In each time-design job a qubit prepared in |1> is left 300 us (in three copies, a, b, c, at different positions in the job) and its level is read. The "fading time" is -300 / ln(level at 300 us), median over readable qubits. It is the qubit's effective decay constant in this readout, about 1.1-1.2 times the maker's T1, not the maker's T1.

**Source.** Marrakesh and Kingston runs 301-303 (jobs db15r4bid5ic73eqmhs0, db15s4pb694s73drrg10, db15skrid5ic73eqmkvg and db15t52vog1s73fhmo3g, db15u31b694s73drrjvg, db161j6egvvc73bh6u50), Pittsburgh runs 361-363, all 4 October 2026. Private reader: `readtime.py`, `sumtime.py`, `checktime.py`. Ledger section 183.

**Reproduction.** Marrakesh copy means 174.0 / 177.3 / 180.7, Kingston 265.6 / 260.4 / 263.9, Pittsburgh run 361 copies 297.1 / 294.2 / 293.8, largest job-to-job move of any copy 9.8 us. All match the page.

**Discrepancy.** The values 174/177/181 are copies a/b/c of the ruler, each averaged over three jobs. They are not three jobs. Per job, Marrakesh averages 173.3, 180.1, 178.6. Pittsburgh's "294-297" is one job's three copies; across its three jobs the averages are 295.1, 301.4, 301.1. Inside Marrakesh job 1 the three copies already span 10.4 us, as much as the job-to-job movement, so "steady within one job" is not supported. The ledger records a read-1 slide inside a job that did not repeat. The label "T1" is also loose.

## 3. Idle control

**(a) Three parking methods.** Source: Pittsburgh hold runs 71-73 (jobs davtdgtj371s73dngms0, davtfd04oijs73e85n2g, davth95j371s73dngub0), 2 October 2026. Private reader: `darkwave_disco/internal/reads_new/park_per_qubit.py` and `.txt`, ledger section 180. The qubit starts in |1>, gets an X after each interval so alternate intervals are spent in |0>, for 300 us in total, as 2 x 150, 4 x 75 or 10 x 30 us. The residual is the measured level minus that qubit's own decay bookkeeping. Recomputed: +0.0017 +- 0.0013, +0.0020 +- 0.0014, +0.0014 +- 0.0014 (claim widths 0.0013, 0.0015, 0.0015; the claim used a bootstrap, this uses analytic shot error). The page says "a qubit prepared in |0> and left"; that is not what was run. All three means are positive, 1.2-1.4 sigma. One chip, one day.

**(b) Idle |0> after 300 us.** Source: run 121, Pittsburgh (job db00t8k92g1c7399m6hg), arm "OFF left alone 300 us"; ledger section 176. Recomputed +0.025 % with a width of 0.13 % (claim +0.02 +- 0.15 %). It is one job on one chip. The same arm in the 26 time-design jobs on six chips (section 2's design) reads +0.04 to +0.80 % per job, positive in every one (about +0.5 % typical); the private `SEVEN.md` says "idle |0> after 300 us: about +0.5 %". The ledger also quotes push-job idle arms of -0.43 +- 0.13 % (Marrakesh) and +0.26 +- 0.14 % (Kingston). So "+0.02 +- 0.15 %" is the smallest of several values, not the general result. "Heating is ruled out" rests on that Pittsburgh job; the others show a small positive gain that the page does not mention (it could be ordinary thermal repopulation over 300 us, which these data cannot separate from heating).

## 4. Non-exponential decay

**Source.** The time-design jobs of section 2 (private file `data/reads/decay_bend_per_qubit_20261004.txt`). Each qubit-copy's 300-us level fixes a single exponential; the 30-us level is compared with it. Recomputed shares below: Marrakesh 84, 80, 83 %; Kingston 78, 72, 75 %; Pittsburgh run 361 62 %. All seven match the file. The 62 % low end is one job; Pittsburgh's other two jobs give 65 and 63 %, and the other chips on disk (Fez 84-85 %, Boston 63-72 %, Aachen 64-65 %) all sit inside the same band, so the claim is robust. The wording "62-84 %" depends on which jobs are counted.

## 5. Leakage cap

**Source.** Pittsburgh push run 91-93 (jobs davuanc92g1c7399i8kg, davveh04oijs73e88tsg, davvf7c92g1c7399k1h0, 2 October 2026), back-to-back X gates with no wait. Ledger sections 147-148.

**Reproduction.** Shifts after 2 and 10 gates: OFF start +0.19 and +2.29 %, ON start -0.20 and -2.32 %. A model with a gate that falls short by an angle plus a term that grows linearly with gate count, shift(N) = N^2 eps^2 / 4 + N b, gives eps = 1.47 degrees (ledger 1.48 +- 0.14) and b = 0.065 +- 0.026 %. The published 0.26 +- 0.12 matches four times b (0.261 +- 0.104), not b itself. I found no file explaining the factor 4; the derivation was done in the review exchange.

**Discrepancies.** The value is a measurement 2.2 sigma from zero, not an upper bound; the ledger's bound is 0.49 % at two widths. It caps every error that grows with gate count (leakage, fading during the pulse, pulse noise), not leakage alone. It assumes the |2> population after N gates is equal for OFF and ON starts (ledger section 148, flagged secondary). One chip.

## 6. Simulated plant

**Source.** Ledger section 328 gives the result line (100 synthetic clocks, 2.3-5.6 degrees per us, looks of exactly the stated 2.18 us, 30 repeats: no noise 1.0000; phase noise 0.06 rad 0.9986 / 0.9990; planted 1.040 reads 1.0370 / 1.0387). The script that produced it is not on disk. `verify_processors_apparatus.py` re-implements it with the published inversion (`readlook_3and9.py`, function `two_ways`): no noise gives 1.0000 and a planted 4 % gives 1.0400 exactly; with 0.06 rad noise, over eight seeds, unplanted gives 0.998 and planted 1.038 (single seeds range 0.996-1.001 and 1.035-1.042). The claim holds, with a seed-to-seed scatter of about 0.003 and a downward bias from noise.

**Scope.** This tests the witness-clock ruler of section 1 only. It says nothing about the T/W ratio, and nothing about the equal-length-idle analysis that replaced the stated-duration comparison on 21 October 2026.

## Files

- `verify_processors_apparatus.py` runs all checks.
- `data/sort_witness_and_looked_at.json` (0.25 MB): per chip-day and run, witness-clock angles and looked-at-bit levels.
- `data/time_runs_ruler_copies.json` (0.45 MB): per run and readable qubit, the three ruler copies' levels and the idle-|0> level.
- `data/pittsburgh_park_idle_push.json` (0.08 MB): runs 71-73, 91-93 and 121, per-qubit levels and shot errors.
- `extract_from_raw.py` makes them from the raw files.

## Not stated in the sources

- Maker T2:T1 values (Marrakesh 0.519, Kingston 0.638, Pittsburgh 1.160, Fez 0.683 on 4 October; Boston 1.183; Phoenix 0.851) are copied from the ledger and read files (`three_seats_per_chip_20261004.txt`, `phoenix_maker_record_oct6_20261006.txt`, ledger line on Boston). They are IBM calibration records and are not re-derived here. Aachen's is not on file.
- The bootstrap widths in the private files are replaced here by analytic shot errors. The two agree to within 0.0002 for the park residuals and to 0.02 % for the idle arm.
