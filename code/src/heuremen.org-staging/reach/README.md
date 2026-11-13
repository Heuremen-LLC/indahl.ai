# Reach: how far does one qubit's readout disturb its neighbours?

Staging package for the "reach" figures on heuremen.org (pages *what a look does*, *findings*, *what we measured*).
Run `python3 verify_reach.py` (standard library only, about 2 seconds). It reads `data/*.json` (220 KB) and prints every
published number beside the number recomputed from the data, marked OK or DIFF.

## What was measured

A superconducting processor measures a qubit by sending a microwave pulse through a resonator. The question is whether
that pulse also affects qubits that are *not* being measured.

Unmeasured **spectators** are used as stopwatches. Each spectator is prepared on the equator of the Bloch sphere (an equal
superposition) and left alone. It then precesses at its own rate (a few degrees per microsecond), so its phase is a clock.
The phase is read at three laid idle delays (10, 20, 30 us) and fitted with angle = c1 t + c2 t^2. While the spectator
idles, *k* other qubits (the **measured qubits**) are measured back to back (k = 1, 2, 3, 4, 6, 9), and the spectator's
phase is then read again. Inverting the fit turns the accumulated phase into an **equivalent elapsed time**. The slope of
equivalent time against k is the **time one readout appears to last, as seen by the spectator**.

* **reported / stated** = that slope divided by the readout duration the backend itself declares (the "stated" duration,
  `measure_duration`, from the backend configuration: 2.18 us on Boston/Kingston/Pittsburgh/Aachen, 1.66 us on Fez, 1.94 us on
  Phoenix, 2.684 us on Marrakesh). A value of 1 means the spectator sees exactly the stated duration. This is the "1-9 fit" estimator
  in the private code. A second estimator ("3-and-9": the slope between k=3 and k=9 only) is stored in the data but is not what the pages use.
* A spectator is kept if its equatorial amplitude is above 0.15 at zero delay and both its own and its partner qubit's
  calibration clouds are separated by more than 3 widths. Unlike the duration table, **no precession-rate cut is applied** in the reach analysis.
* **Idle (dark) control**: in the floor jobs one arm replaces every readout with an equal stretch of plain delay.
* **Spacing / pitch**: distance on the heavy-hex lattice drawn as a plan, in units of one qubit spacing along a row
  (rows are 2 units apart, bridge qubits sit half-way). *Within two spacings* means plan distance <= 2. On Phoenix (a square lattice, no plan) it
  means within two coupling links; Phoenix is flagged where it enters.
* **Intensity** = sum over all measured qubits of 1/r^2 (r in spacings, floored at 1). **Nearest** = distance to the nearest measured qubit.

All jobs: IBM Quantum, Heron-family processors, raw I/Q kerneled readout, dynamical decoupling and twirling off, 400 shots
per circuit, "init" reset (recorded in each run's settings). Raw I/Q is about 26 GB and stays private; `data/*.json` hold the
per-spectator values the estimator outputs, `tools/extract_reach.py` is the one-time reduction (it imports the original readers
unchanged and asserts that an independent copy of the arithmetic agrees to 1e-9).

## Experiments, chips, dates, jobs (all times EDT as recorded at submission)

| Data file | Experiment | Processor, date | Runs and IBM job IDs |
|---|---|---|---|
| `layout_A_pool.json` | Layout A: one random choice of which qubits are measured (role seed 20261810), same on every chip | Boston 4 Oct; Fez 4 and 6 Oct; Kingston 4 and 6 Oct; Marrakesh 4 Oct; Phoenix 5 and 6 Oct; Pittsburgh 4 and 5 Oct | 24 reads, run numbers and job IDs in each read of the file |
| `layout_B.json` | Layout B: an independent second random draw (role seed 20261007), otherwise identical circuits | Pittsburgh 7 Oct, runs 901-903 (db2s5s47f06c73aqepk0, db2savc2ljfc73d53beg, db2sg2k2ljfc73d53im0); Marrakesh 7 Oct, runs 911-913 (db2s9rfr11fs7397c2ug, db2sevk7f06c73aqf7ng, db2skk47f06c73aqfi40) | |
| `clusters.json` | Four clusters of measured qubits (25 of them) around four central spectators (qubits 43, 131, 102, 69) | Fez 7 Oct, runs 921-923 (db2s9rfr11fs7397c2u0, db2seuu8v0ts73c3eo40, db2sklc2ljfc73d53qvg); the same layout also on Pittsburgh (931-933), Marrakesh (951-953), Aachen (961-963) | |
| `floor.json` | Fall-off with distance: 12 measured qubits in one corner; spectators 3 or more spacings away; three arms per job (idle, stated readout, a shorter readout) | Pittsburgh 7 Oct, runs 1031-1033 (db32pe42ljfc73d5et60, db32umk7f06c73aqr20g, db333v42ljfc73d5fd7g); Fez 1081-1083; Aachen 1091-1092 (a third Aachen read was never run) | |

## Results: each published figure against the data

| Page claim | Recomputed | Status |
|---|---|---|
| Fall-off: 1.03 (3-5 spacings), 1.02 (6-8), <1.01 (9+), idle control 0.99 | Pittsburgh, reads 1 and 2 only, measured arm divided by idle arm: 1.031 / 1.025 / 1.009; idle arm 0.991 | Reproduces, but only under a choice the page does not state (see 1 below) |
| Intensity orders spectators best | Spearman, layout A pool (1283 spectator-reads): count +0.120, intensity +0.157, nearest -0.085; four-cluster chip, 1 read (52): +0.486 / +0.501 / -0.496 | Intensity is largest in every set; margins are small (see 2) |
| Dose-response, device A: 1.039 / 1.045 / 1.083 / 1.181 | 1.039 / 1.045 / 1.083 / 1.181 | Reproduces. "Device A" is six processors pooled, not one (see 3) |
| Device B: 1.032 (0), 1.176 (>=3) | Pittsburgh layout B: 1.032 / 1.176 | Reproduces. Not a different processor from A (see 3) |
| Marginal effect +0.21 per measured qubit in range | Slopes: 0.042 (layout A, per spectator-read), 0.044 (Pittsburgh A->B same spectators), 0.083 (layout B Pittsburgh); 0.047 from the published table | Does not hold: +0.21 is a subgroup median (12 spectators), not a slope (see 3) |
| Clusters: centres read 2.07, 2.29, 3.25 | 2.066 (centre 43, read 1), 2.285 (centre 102, read 1), 3.252 (centre 69, read 2) | Values reproduce; selection does not (see 4) |
| Open field 1.04 | 1.003 / 0.978 / 0.983 on reads 1/2/3 (pooled 0.983) | Does not reproduce (see 4) |

## Discrepancies and what they mean

**1. Fall-off with distance.** The page's three ratios are *measured-arm reported/stated divided by idle-arm reported/laid*,
from the first two of the three jobs of one chip (Pittsburgh). The "idle control 0.99" is the idle arm's absolute value (0.991),
a different scale from the three ratios, so the four numbers are not on one axis. Admitting the third job of the same experiment changes the picture:
3-5 spacings 1.014, 6-8 spacings 1.027, 9+ 0.999, so the 6-8 band is larger than the 3-5 band and nothing falls off monotonically. Read by read, the 3-5 band is
1.062 / 1.001 / 0.981: the scatter between jobs (0.035) is as large as the claimed excess. The same design on Fez (all three reads: 1.017 / 1.017 / 0.987) and Aachen (two reads:
0.998 / 1.011 / 1.001) shows no clear near-band excess either; in the project's own ledger the near-band excess "walks from read to read". With the shorter-readout arm the 3-5 band is 1.034 and the 6-8 band 0.985.
The data do not support a distance law; they are consistent with an effect of at most a few percent at 3-5 spacings that is at the noise level of 14 spectators per band.

**2. Predictor ranking.** The project's ranking code uses ordinal ranks, which break ties arbitrarily; count within two spacings has many ties (most spectators have 0).
With standard average-rank Spearman, on the four-cluster chip count is +0.486, not +0.316, i.e. practically tied with intensity (+0.501) and nearest (-0.496). On the layout-A pool
the ordering is intensity (+0.157) > count (+0.120) > nearest (-0.085), the bootstrap 95% interval of the intensity-minus-count difference is [+0.004, +0.070], and all three
correlations explain under 3% of rank variance. "Orders best" is literally true in every set but weakly supported on the cluster chip (interval spans zero), and the
page's wording ("neither predictor wins", "radiated") says more than the numbers do.

**3. Dose-response.**
* "Device A" is the average over *six* processors (Boston, Fez, Kingston, Marrakesh, Phoenix, Pittsburgh; 10 processor-days, 24 reads); each processor is first averaged over its days. One processor (Marrakesh)
  is not monotone; Phoenix's count is within two *links* (square lattice). The top bin exceeds the zero bin on all six.
* "Device B on a different processor" is Pittsburgh with a second random layout, three days later. Pittsburgh is *also one of the six processors in device A*, and there layout A shows no rise
  (1.011 -> 1.040 on 4 Oct; 1.010 -> 1.156 on 5 Oct, one read). The other layout-B experiment, on Marrakesh, goes the other way: 0.979 (0) to 0.688 (>=3, seven spectators). It is not on the page.
* If only spectators precessing faster than 4 deg/us (the cut the published duration table applies) are kept, layout A reads 1.026 / 1.032 / 1.049 / 1.066: the 0-to-3 rise shrinks from +0.142 to +0.040. Slowly precessing spectators give ill-conditioned fits and read long; the reach table does not remove them.
* **+0.21**: the project's ledger says "a clock that gains looked-at bits in sight gains look (+0.21 for one more)". That is the median change for the 12 Pittsburgh spectators that gained exactly one measured
  qubit between layout A and layout B (+0.214). The least-squares slope over the same 44 spectators is +0.044. The ladder in the page's own table rises about 0.05 per rung. On Marrakesh the same comparison gives a slope of +0.218 (dominated by four spectators) and a median of +0.027 for the gain-one group.

**4. Four clusters.** There are twelve (centre, read) cells in the Fez experiment (four centres, three jobs). Seven are readable (the other five have too little phase signal to fit): -0.424, 0.513, 1.429, 1.463, 2.066, 2.285, 3.252.
The three published values are the three *largest*: centres 43 and 102 on read 1, centre 69 on read 2. The fourth centre (131) was unreadable on reads 1 and 2. Read 3 of the same job gives 0.513, 1.429, -0.424, 1.463 for centres 43, 131, 102, 69
(a negative elapsed time is not a duration; it marks the estimator failing). The same layout on three other processors gives centres anywhere from -0.41 to 2.75 (Pittsburgh 43: 1.51; 131: -0.37; 102: 0.21; 69: 0.78; Marrakesh 43: 0.04; 102: 0.72 to 2.50; Aachen 43: 1.38 to 1.52; 69: 1.76 to 2.75).
So the supported statement is: on several processors, spectators surrounded by a cluster of measured qubits have readings that scatter widely and are often above 1; it is not "centres read 2.07, 2.29, 3.25". The page's 2.29 is 2.2848, which rounds to 2.28.
"1.04 in the open field" is not the open-field value of this job on this estimator (0.983 pooled; the other estimator gives 1.044 on read 1 alone, 0.973 and 1.002 on reads 2 and 3). 1.039 is the layout-A pool's zero bin (section 3), so the two may have been conflated.

## Suggested wording changes

* Say "six processors" for the layout-A dose-response; say layout B on Pittsburgh is a second layout on one of those processors; report the Marrakesh layout-B result.
* Drop "+0.21 per measured qubit"; the ladder is about 0.05 per measured qubit.
* Replace the fall-off table with all three Pittsburgh reads (and Fez, Aachen), or remove it; the bands do not separate.
* Show the cluster centres as all twelve cells with the five unreadable ones marked, or drop the claim.

## Files

* `verify_reach.py`, `data/layout_A_pool.json`, `data/layout_B.json`, `data/clusters.json`, `data/floor.json`
* `tools/extract_reach.py` (needs the private raw data and numpy/scipy; not needed to verify)
* Columns of the spectator rows: spectator qubit, measured qubits within two spacings, intensity, nearest measured (spacings), precession rate (deg/us), reported look in us (1-9 fit), reported look in us (3-and-9). `null` = the fit failed. Floor rows: qubit, distance, idle-arm, measured-arm, shorter-readout-arm look in us.
