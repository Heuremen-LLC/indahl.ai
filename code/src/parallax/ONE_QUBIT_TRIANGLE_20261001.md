# ONE QUBIT, THREE CLOCKS -- 2026-10-01, Bones's field hand

THIRD_RUNG_20260928.md Sec62-63. Wayfinder: "you got three clocks and three equations and everything we're doing
is three and triangulation, and you can triangulate the time on these chips and haven't been doing it -- start
now." Sec63's named leg: "ONE-QUBIT TRIANGLE: arisen carry 64 us / look-heat drain ~80 us / T1 148 us (IBM's) --
three clocks on one qubit, never closed." This runs it, per qubit, for real -- not the pooled numbers already on
the ledger.

No numeric prediction written before running. Script: `out/the_middle/one_qubit_triangle.py`. Raw output:
`out/the_middle/one_qubit_triangle_results.json`. Data: `out/echo_20260928_122733/` (ibm_marrakesh, 78 even
qubits, 1500 shots/job, raw kerneled I/Q, gaps 20/50/100/250/500/1000/2000 us) and the calibration snapshot in
force on 2026-09-28 (`out/ibm_cal_20260929/ibm_marrakesh/2026-09-28.json.gz`, last_update_date 2026-09-28
19:19:52-04:00). numpy only, single process, ~2.7 seconds runtime.

## The three clocks, per qubit

- **A, ARISEN CARRY** -- fit per qubit from the corrected (lag1-diff minus lag20-diff) carry series at gaps
  20/50/100 us, same recipe `PLACED_VS_ARISEN_20260930.md` used pooled, now run qubit-by-qubit. Bootstrap error:
  150 draws, resample shots with replacement within that qubit's own data.
- **B, LOOK-HEAT DRAIN** -- fit per qubit from the first-look excess-vs-gap curve (`PRE_MEASUREMENT_20260930.md`
  Step1 recipe), at three readout cutoffs 0.25/0.50/0.80 of the way to the 1-cloud. Bootstrap error: same
  shot-resample recipe, 150 draws, at each cutoff separately.
- **C, T1 (and T2 beside it)** -- from the IBM calibration snapshot in force 2026-09-28. Checked directly: this
  snapshot's per-qubit entries carry only `date`, `name`, `unit`, `value` -- **no error/uncertainty field of any
  kind**, for T1, T2, or anything else. C's error is therefore reported as UNAVAILABLE, never invented; every
  number downstream that touches C says so.

74/78 qubits pass the SNR>=1.5 readout gate. **51/74** get a resolvable A (a fittable, decaying, positive
20/50/100us series). **22/74** get a resolvable B at cutoff 0.50 (17/74 at 0.80, 25/74 at wider cutoffs -- see
`PRE_MEASUREMENT` Step1's own per-cutoff n-clean count, this is the same shape, per-qubit not just per-cutoff-median).
**21/74** have all three (A, B at cutoff 0.50, T1) resolvable at once -- the full triangle. Named blinkers: q68
does NOT resolve on either A or B (its own noisy blink dominates before either fit can lock a decaying series);
q76 resolves on both and sits in its own row below, excluded from the pooled ratio stats per standing
instruction.

## 1. The triangle, per qubit (21 qubits + blinker q76's own row)

All values us. Errors are the 150-draw shot-resample bootstrap sd (A, B) or UNAVAILABLE (C -- IBM gives none).
Legs (A-B), (B-C), (C-A) sum to zero identically for any three numbers (checked: max |residual| across all 21
rows = 2.8e-14 us, floating-point noise) -- so the triangle test below is the three PAIRWISE RATIOS, not the legs.

| qubit | A (us) | B (us) | T1 (us) | T2 (us) | A/B | B/C | A/C |
|---|---|---|---|---|---|---|---|
| q10 | 7.6 +/- 40.3 | 50.0 +/- 60.3 | 270.0 | 155.6 | 0.153 | 0.185 | 0.028 |
| q14 | 223.8 +/- 367.1 | 170.6 +/- 203.1 | 275.0 | 85.0 | 1.312 | 0.620 | 0.814 |
| q20 | 149.6 +/- 395.9 | 99.0 +/- 426.8 | 134.6 | 150.2 | 1.510 | 0.736 | 1.111 |
| q22 | 95.6 +/- 1379.1 | 94.5 +/- 15.0 | 89.7 | 16.7 | 1.012 | 1.054 | 1.067 |
| q24 | 96.6 +/- 599.2 | 61.5 +/- 8.1 | 71.0 | 52.7 | 1.573 | 0.865 | 1.361 |
| q26 | 24.6 +/- 245.3 | 124.2 +/- 19.7 | 8.6 | 4.1 | 0.198 | 14.370 | 2.847 |
| q42 | 47.0 +/- 201.6 | 224.7 +/- 100.2 | 211.9 | 51.0 | 0.209 | 1.060 | 0.222 |
| q44 | 214.6 +/- 60.2 | 69.6 +/- 119.3 | 107.7 | 90.6 | 3.082 | 0.647 | 1.993 |
| q56 | 8.5 +/- 130.0 | 81.1 +/- 410.5 | 184.2 | 32.7 | 0.105 | 0.440 | 0.046 |
| q66 | 63.1 +/- 157.3 | 41.0 +/- 10.2 | 87.8 | 73.3 | 1.539 | 0.467 | 0.718 |
| q78 | 60.4 +/- 61.3 | 55.8 +/- 20.8 | 173.2 | 98.7 | 1.083 | 0.322 | 0.349 |
| q86 | 77.3 +/- 223.7 | 82.2 +/- 273.3 | 191.5 | 61.9 | 0.940 | 0.430 | 0.404 |
| q92 | 4.5 +/- 729.6 | 80.0 +/- 31.9 | 213.7 | 105.6 | 0.056 | 0.374 | 0.021 |
| q96 | 36.1 +/- 836.0 | 17.2 +/- 8.7 | 104.5 | 38.3 | 2.098 | 0.165 | 0.346 |
| q106 | 15.2 +/- 272.2 | 63.5 +/- 389.9 | 163.3 | 136.6 | 0.239 | 0.389 | 0.093 |
| q110 | 86.0 +/- 386.9 | 50.8 +/- 10.3 | 271.6 | 63.8 | 1.694 | 0.187 | 0.317 |
| q138 | 9.8 +/- 1545.7 | 39.4 +/- 1454.1 | 231.7 | 30.5 | 0.248 | 0.170 | 0.042 |
| q140 | 119.7 +/- 4247.7 | 97.7 +/- 152.9 | 241.1 | 98.9 | 1.225 | 0.405 | 0.497 |
| q150 | 110.7 +/- 292.0 | 70.5 +/- 10.9 | 161.2 | 147.0 | 1.569 | 0.437 | 0.686 |
| q154 | 270.5 +/- 74.0 | 251.0 +/- 3211.3 | 291.1 | 33.2 | 1.078 | 0.862 | 0.929 |
| q76 **[BLINKER]** | 108.8 +/- 156.5 | 72.2 +/- 7.0 | 36.8 | 16.2 | 1.506 | 1.962 | 2.954 |

q68 **[BLINKER]**: unresolved on both A and B -- no row.

Failed rows: 74-51=23 qubits fail A (no decaying 20/50/100us fit); 74-22=52 fail B at cutoff 0.50; 21 have all
three (20 pooled + q76's own row).

## 2. Which pair is tied -- three pairwise ratios, weighted mean + chi2/dof, n=20 (blinkers excluded)

| ratio | n | weighted mean | chi2/dof | read |
|---|---|---|---|---|
| A/B | 20 | 0.443 +/- 0.471 | **0.06** | technically "one number," but only because per-qubit errors (dominated by A's huge bootstrap spread) are wide enough to swallow ALL of the scatter -- not a resolved tie, an UNCONSTRAINED one. |
| B/C | 20 | 0.318 +/- 0.027 | **5.45** | FAILS. The drain is not a fixed fraction of T1 -- textbook "the drain is thermal relaxation" is ruled out at this n. Errors here come almost entirely from B (C carries none), so this chi2 is real, not an error-bookkeeping artifact. |
| A/C | 20 | 0.343 +/- 0.113 | **1.00** | The closest thing to "one number" here. chi2/dof exactly at the nominal-fit value for n-1=19 dof (chi2=19.0/19). Read with real caution below. |

**Textbook check, B vs C**: if the look-heat drain were ordinary T1 relaxation, B/C would sit at one ratio
chip-wide. It doesn't (chi2/dof=5.45, n=20) -- same verdict `PRE_MEASUREMENT_20260930.md` Sec.3 already reached
pooled (rho(tau_B, T1)=0.03, p=0.92); this is the same "no" now shown ratio-wise and per-qubit rather than by
correlation.

**A/C at chi2/dof=1.00** looks like a tie, but the honest caveat: C carries zero measured error in this
snapshot, so every bit of A/C's scatter is attributed to A's own (often enormous) bootstrap error -- the same
condition that made A/B's chi2/dof artificially low (0.06). A ratio test where one leg's error is invented-as-zero
and the other leg's error is sometimes >>the value itself (e.g. q140: A=119.7+/-4247.7) is not a clean test of
constancy; it is a test that the data can't rule out constancy, which is weaker. Read A/C's chi2/dof=1.00 as
"consistent with one number, not yet proof of one" -- exactly the caveat the A/B row states outright.

## 3. The cutoff test on B: does A/B move with the readout cutoff?

| cutoff | n | weighted mean A/B | chi2/dof |
|---|---|---|---|
| 0.25 | 23 | 0.252 +/- 0.448 | 0.107 |
| 0.50 | 20 | 0.443 +/- 0.471 | 0.060 |
| 0.80 | 16 | 0.335 +/- 0.374 | 0.118 |

Spread of the three weighted means (0.252 to 0.443) = 0.190; combined error across the three means = 0.750.
**Spread < combined error -> A/B is STABLE across cutoffs at this precision.** But note: the individual-cutoff
errors are themselves so wide (chi2/dof<<1 at every cutoff, same pattern as Sec.2's A/B) that "stable" here means
"not shown to move," not "shown to be fixed" -- the same under-constraint that flagged A/B above. If the drain
were partly the ruler (moving with the cutoff), this test would in principle catch it; it did not catch anything,
but the test's own power is weak given A's bootstrap noise.

## 4. Series-taus (K_TAU=0.053767, `out/the_middle/calibrated_standoff.py`'s own map, reused verbatim)

A and B, each with a real bootstrap error, convert cleanly into the calibrated common unit (series-taus, the
same unit `THIRD_RUNG_20260928.md` Sec57-58 used for the yeast/horn/buzz/mice triangle). **C (T1/T2) cannot be
converted**: the series-tau map needs a relative error to locate a landing step, and this calibration snapshot
gives none for T1 or T2 -- reported OPEN, not filled with an invented number.

Per-qubit series-tau gap (A minus B), n=20 (blinkers excluded): **weighted mean -1.037 +/- 0.306 series-taus,
chi2/dof = 1.25** (n=20, dof=19). Same sign (A running faster/"earlier" than B in this unit) as the direction
`THIRD_RUNG_20260928.md` Sec58's clock-gap work found for the chip-level clock vs. arrow/split comparisons
(there: clock minus arrow/split both POSITIVE; here it's A vs. B specifically, opposite naming convention, same
family of number, chi2/dof in the same "loosely one number, not tightly" range as Sec58's own clock-minus-arrow
result (4.8) and clock-minus-split result (1.6)).

## 5. Plain words

On one qubit, right now, with this data: **the three clocks do not read as one time.** The clearest failure is
B vs. C -- the look-heat drain is NOT a fixed fraction of T1 (chi2/dof 5.45, n=20); textbook "it's just thermal
relaxation" is ruled out again, this time qubit-by-qubit rather than only in the pooled correlation. A vs. B
(the arisen carry vs. the drain) and A vs. C (the carry vs. T1) both come back "consistent with one number" --
but honestly, both of those come back that way mostly because A's own bootstrap error is so large on most qubits
(it is a much noisier fit than B, itself resting on only three points: 20/50/100us) that almost nothing could be
ruled OUT. The fixed leg this run can actually stand behind is a negative: **B is not C.** Whether A is one clock
with B, or with C, is not resolved by this data -- it is UNDER-CONSTRAINED, not confirmed. The cutoff test found
no sign that the drain moves with the ruler, but for the same reason: not enough precision to see it move even
if it did.

## Tries counted

18,896 tau fits (51 qubits x up to 3 fast-window fits for A's point+150 boots, x up to 3 cutoffs x 3 fits for B's
point+150 boots, across all 74 readable qubits, including the 23+52 that failed and are counted) + 18,600
bootstrap draws + 125 ratio/propagation calls (3 ratios x 21 qubits, + 3 cutoffs x ~20 qubits for the cutoff
test) + 10 weighted-mean/chi2 constancy calls (3 pairwise ratios + 3 cutoffs + 1 cutoff-spread check + 1
series-tau gap, rounded) = **19,031 tests/fits counted**, printed by the script itself, not asserted after the
fact.
