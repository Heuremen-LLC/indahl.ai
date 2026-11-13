# Gate cost: residual excited population after spaced X-gate trains

Staging package, not yet published. `python3 verify_gate_cost.py` (standard library only) recomputes every
gate-cost number the site states from `data/gate_cost.json` (295 KB) and prints each beside the claim.

## What was run
Seventeen IBM Quantum Sampler jobs on every qubit of the chip, 800 shots per circuit (Pittsburgh: 216), submitted
2 to 7 October 2026. Per job, for each qubit that can be read cleanly (its |0> and |1> readout clouds more than
4 widths apart) we kept the excited-population level for:

* start in |0>, then 2, 6 and 10 X gates, with a 30 microsecond wait after each X gate;
* start in |1> and left alone for 30, 90 and 300 microseconds (the decay reference).

Level is the projection of the averaged readout signal between the qubit's own |0> cloud (0) and |1> cloud (1).

| chip | run | date | IBM job id | readable qubits |
|---|---|---|---|---|
| ibm_pittsburgh | 121 | 2 Oct | db00t8k92g1c7399m6hg | 150 |
| ibm_fez | 371 | 4 Oct | db18h6bid5ic73eqq2f0 | 133 |
| ibm_kingston | 392 | 4 Oct | db1b6l3id5ic73eqtmt0 | 144 |
| ibm_boston | 441 | 4 Oct | db1hgb1b694s73ds9g0g | 153 |
| ibm_phoenix | 531 | 5 Oct | db1ovbhb694s73dsk380 | 116 |
| ibm_kingston | 721, 722, 723 | 6 Oct | db2o34u8v0ts73c36qv0, db2o8hu8v0ts73c3788g, db2odpc2ljfc73d4sg3g | 147, 148, 146 |
| ibm_phoenix | 751, 752, 753 | 6 Oct | db2ojdfr11fs73975jsg, db2ooac2ljfc73d4t8pg, db2p3947f06c73aq9iu0 | 116 each |
| ibm_aachen | 841, 842, 843 | 6 Oct | db2qqeocv0fc73e8rjm0, db2qvde118nc7390g4hg, db2r4adv86ts73dhk3c0 | 146, 147, 147 |
| ibm_boston | 711, 712, 713 | 7 Oct | db33cic2ljfc73d5fnqg, db33hjc7f06c73aqroh0, db340ic2ljfc73d5gohg | 152 each |

("Day 1" on the site = runs 371, 392, 441, 531, and Pittsburgh 121; "day 2" = 711-713, 721-723, 751-753.
Aachen is not on the site; it is included because the per-qubit tally in the lab notebook includes it.)

## Estimators, in plain physics terms
* Prediction. Assume the X gates are perfect and only energy relaxation acts. With q the probability an excited
  qubit is still excited after one 30 us wait, the excited population after n gates follows
  `on <- off + on*(1-q); off <- on*q`, starting from on=0, off=1.
* Residual = measured minus predicted, averaged over qubits, at n = 2, 6, 10.
* Slope per gate = least-squares slope of the residual against n (equal to (residual at 10 minus residual at 2) / 8).
* The three ways of choosing q, all from the same job: "own interval" = the 30 us survival measured directly;
  "90 us ruler" = (survival after 90 us) to the power 30/90; "one exponential" = (survival after 300 us) to the power 30/300.
  Survivals are clipped to [0.02, 1] (Pittsburgh's original reader used [0.02, 1.2]).
* "Averaged four ways": mean, median, 20 %-trimmed mean over qubits, and the share of qubits whose own 3-point slope is negative.
* Widths: the site's plus-or-minus values are shot-resampling widths that also resample the reference readouts.
  The data here are per-qubit levels with shot standard errors, so `verify_gate_cost.py` prints a first-order shot-noise
  width instead. It is smaller than the published width (0.00027 vs 0.00035 for Kingston day 1), consistent with the published
  width containing extra reference-readout noise. Published widths therefore cannot be reproduced exactly from this file.

## Result of the check (output of verify_gate_cost.py)
Reproduced to the published 5 decimals: Kingston day 1 (-0.00198), Kingston day 2 three-read mean (-0.00136),
Fez (-0.00182), Boston reads 711/712/713 (-0.00154 / -0.00080 / -0.00063), Pittsburgh (-0.00107 vs -0.00106; the
published value was computed from 4-decimal rounded points), "negative on all three rulers and all three averagings"
on all nine Fez/Kingston/Boston runs, and "54-70 % of qubits" (range over heavy-hex runs including Aachen).

## Discrepancies and things the site does not say
1. **Phoenix figures are unlabelled.** -0.00002 and -0.00010 are the day-2 three-read means on two different
   estimators (own interval, and 90 us ruler). They are not two reads. The page does not say so.
2. **Phoenix is not zero on every estimator, and day 1 is omitted.** Day 1 (run 531): own -0.00058 +- 0.00029
   (2.0 sigma), 90 us -0.00091, one-exponential -0.00155. Day-2 three-read mean on the one-exponential
   ruler: -0.00074. Only the own-interval and 90 us day-2 means are near zero. The page's "it is zero" holds only
   for those two choices.
3. **Boston day 1 is omitted** (-0.00139 +- 0.00026, 5 sigma) though the "8.5 times" maximum is built on it.
   The three Boston values shown are day-2 reads.
4. **"4 to 8.5 times the stated gate error" is not computed on one estimator.** The notebook says the 90 us ruler.
   Recomputed ratios (|slope| / stated error, day 1):

   | chip | claimed | own interval | 90 us ruler |
   |---|---|---|---|
   | boston | 8.5 | 8.53 | 9.08 |
   | kingston | 8.4 | 8.42 | 7.59 |
   | fez | 6.0 | 6.01 | 7.66 |
   | pittsburgh | 5.5 | 5.55 | 5.88 |
   | phoenix | 4.1 | 2.63 | 4.09 |

   Four chips match the own-interval slope; Phoenix alone matches the 90 us ruler. On a single estimator the claim
   becomes: own interval 5.5 to 8.5 for heavy-hex (Phoenix 2.6); 90 us ruler 5.9 to 9.1 for heavy-hex (Phoenix 4.1).
   The "4" lower bound on the page is the Phoenix figure, the chip the page says shows zero; the index page says
   "4-8.5x on every heavy-hex chip", which the data do not support. On the 90 us ruler Boston is 9.1, so 8.5 is
   not the maximum on that ruler. Day-2 ratios are lower (Boston three-read mean 6.1, single reads 9.5 / 4.9 / 3.8;
   Kingston 5.8).
5. **The stated gate errors cannot be verified here.** 1.63e-4 (Boston), 2.35e-4 (Kingston), 3.02e-4 (Fez),
   1.92e-4 (Pittsburgh), 2.22e-4 (Phoenix) are medians over qubits from a backend-properties read on
   6 Oct at 23:35 UTC. No saved file of that read was found; the slopes are from 2 to 7 Oct, calibration cycles differ,
   and the IBM calibration is not retrievable offline. These five numbers are labelled UNSOURCED in the script.
   Publish them with their source (the calibration record) or drop the ratio sentence.
6. **"54-70 % of individual qubits carry their own negative slope" does not separate chips.** Phoenix runs fall at
   46-57 %, inside the range; the heavy-hex low end is Aachen 842 (54 %) and Boston 712 (58 %), where a sign test
   against 50 % gives p = 0.41 and 0.06. Three-point per-qubit slopes are noisy, so ~50 % is the no-effect value.
   Over the three chips on the site the range is 58-70 %.
7. **"Negative under every estimator, every read, every heavy-hex chip"** holds for Fez, Kingston and Boston
   (9 of 9 runs, three rulers, three averagings). It fails on one Aachen read (842, one-exponential ruler), but Aachen is not on
   the site. Boston read 712 median is -0.00013 (close to zero).
8. Pittsburgh (-0.00106, used in the ratio) is not in the site table. Its width (+-0.0008) was formed from
   the two end points in quadrature, ignoring their shared reference; the first-order width here is 0.0005.

Not part of this package: the lab notebook also maps these slopes onto a numerical ladder; no such mapping is made or checked here.

## Files
* `verify_gate_cost.py` -- the checker.
* `data/gate_cost.json` -- per run: readable qubit indices, levels `N2 N6 N10` (2, 6, 10 gates), `R30 R90 R300`
  (decay reference), and `se_*` shot standard errors.
* `extract_gate_cost.py` -- how the JSON was built from the private raw files (needs numpy and the raw
  `run<N>_results.npz` files, about 22 GB private tree; not needed to verify). Source readers: `readfive_slope.py`,
  `five_wabac.py`, `readnoname.py` in `parallax/out/qubit_fifth_run/`. Their printed outputs, `data/reads/five_slope_*_2026100*.txt`
  and `five_wabac_20261007.txt`, match this package except as listed above; `readfive_slope.py` was re-run on all thirteen
  runs and reproduces the published slopes and widths there.
