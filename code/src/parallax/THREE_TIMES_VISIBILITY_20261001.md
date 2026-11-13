# THREE TIMES ON THE CHIP -- WHEN DOES VISIBILITY SWITCH ON AND OFF

Wayfinder, ~02:25Z 10/1 (THIRD_RUNG_20260928.md Sec68): "IBM has two times, we need three; they go
invisible to each other." Builds directly on `CLOCK_EXISTENCE_20261001.md` (A = ~64us clustering
clock / arisen carry, B = look-heat drain, C = IBM's T1/T2; A<->B EXISTS only at readout cutoff
0.50 in that run's 3-cutoff check, C is mutually invisible with both on every snapshot day) and
`CHIP_TRIANGLE_20261001.md` (shot clocks vs the microsecond clock). THE CHASE: when does
visibility between the chip's clocks switch on and off?

**Scope.** Data on disk only. No expectation written before running. Raw first. Script:
`out/the_middle/three_times_visibility.py` (numpy only, single process, ~8s runtime). Raw output:
`out/the_middle/three_times_visibility_results.json`. Data: `out/echo_20260928_122733/`
(ibm_marrakesh, 78 even qubits, echo run timestamped 2026-09-28 ~12:27:33 UTC from its own
directory name -- stated as read, not independently measured), three IBM calibration snapshots
(`out/ibm_cal_20260929/ibm_marrakesh/2026-09-{26,27,28}.json.gz`, each entry carries its own
per-qubit `date` field for T1/T2), and `out/the_buzz/look_phase.json` (per-seat first-look tone
phase, tile-8 even seats 80/82/96/100/102/116, Fez J1 pubs p2/p3). 74/78 qubits pass the
SNR>=1.5 readout gate; clock A resolves 51/74 (fixed, cutoff-independent); clock B resolves
16-30/74 depending on cutoff (table below).

**Method.** Same existence-cell construction as `CLOCK_EXISTENCE_20261001.md`: ordered pair (X
predicts Y), real qubit set = qubits where both resolve, OLS R^2 + qubit-level bootstrap error
(500 draws), Spearman rho alongside, sign of the OLS slope kept. **The only null is the REVERSED
ASSIGNMENT of qubit labels** (X qubit-ascending, Y qubit-descending -- one deterministic
re-pairing, never a shuffle, stated as exactly that). Verdict: DOES NOT EXIST if real R^2 doesn't
clear its own bootstrap error; EXISTS if it clears its own error AND beats the reversed-label
R^2; UNRESOLVED if n<6 or it clears its own error but not the reversed null. Where n is too small
for a bootstrap to mean anything (the buzz vantage, n=4-6 seats), an EXACT permutation fraction is
used instead -- every ordering enumerated, not a Monte Carlo shuffle -- stated as exact every time.

---

## 1. The cutoff dial, fine (0.20 to 0.90, step 0.05, 15 rulers)

A<->B existence (R^2 is symmetric by OLS construction, so one row covers both directions):

| cutoff | n (B resolves) | n (both A & B) | real R^2 | boot err | rev R^2 (null) | verdict |
|---|---|---|---|---|---|---|
| 0.20 | 22 | 18 | 0.138 | 0.147 | 0.046 | DOES NOT EXIST |
| 0.25 | 30 | 24 | 0.034 | 0.117 | 0.004 | DOES NOT EXIST |
| 0.30 | 27 | 22 | 0.008 | 0.125 | 0.148 | DOES NOT EXIST |
| 0.35 | 29 | 25 | 0.003 | 0.171 | 0.103 | DOES NOT EXIST |
| **0.40** | 26 | 24 | **0.333** | 0.155 | 0.00004 | **EXISTS** |
| **0.45** | 27 | 23 | **0.206** | 0.170 | 0.011 | **EXISTS** |
| **0.50** | 22 | 21 | **0.273** | 0.226 | 0.067 | **EXISTS** |
| **0.55** | 24 | 22 | **0.174** | 0.149 | 0.010 | **EXISTS** |
| 0.60 | 25 | 23 | 0.007 | 0.125 | 0.014 | DOES NOT EXIST |
| **0.65** | 23 | 21 | **0.433** | 0.223 | 0.075 | **EXISTS** |
| 0.70 | 22 | 20 | 0.006 | 0.082 | 0.086 | DOES NOT EXIST |
| 0.75 | 21 | 18 | 0.001 | 0.068 | 0.053 | DOES NOT EXIST |
| 0.80 | 21 | 17 | 0.050 | 0.215 | 0.038 | DOES NOT EXIST |
| 0.85 | 16 | 14 | 0.016 | 0.091 | 0.161 | DOES NOT EXIST |
| 0.90 | 17 | 14 | 0.005 | 0.120 | 0.021 | DOES NOT EXIST |

**Where visibility turns on, peaks, and turns off:** it is NOT a single point at 0.50. It is a
**band from 0.40 to 0.55** (four consecutive EXISTS cutoffs), a gap at 0.60 (DOES NOT EXIST, R^2
collapses to 0.007), then an **isolated spike at 0.65** (the highest R^2 of the whole sweep,
0.433), and DOES NOT EXIST everywhere outside that -- the whole low end (0.20-0.35) and the whole
high end (0.70-0.90). The earlier 3-point check (0.25/0.50/0.80 only) made 0.50 look like a lone
peak; the finer 15-point sweep shows it sits inside a 0.40-0.55 plateau, with a second, separate,
higher peak at 0.65 that the coarser sweep never sampled.

**Is the peak a point or a band?** A band (0.40-0.55), plus a second disconnected point (0.65).
Not one clean dial setting -- two.

**Resolving-count curve as its own ruler:** n(both A&B resolve) ranges 14-25 across the sweep.
Correlation of the resolving count against the R^2 curve itself: **r = 0.28** -- weak, and the
resolving count does NOT track the R^2 shape. The EXISTS band (0.40-0.55, n=21-24) and the
isolated 0.65 peak (n=21) sit in the middle of the resolving-count range, not at its extremes;
the two highest-resolving cutoffs (0.35, n=25; 0.25, n=24 tied) both read DOES NOT EXIST. Whatever
turns visibility on and off at these cutoffs, it is not simply "more qubits resolve, so the fit
gets noisier or cleaner."

---

## 2. The published clock vs calibration age

**Finding before the test could even run: the chip was not calibrated on a spread of ages.** Per-
qubit T1 `date` fields (checked directly, all 156 chip qubits) hold only **6 distinct timestamps**
chip-wide: 144/156 qubits calibrated 8.41h before the echo run (2026-09-28 ~12:27:33 UTC), 6
qubits at 37.86h, and single qubits at 86.87h, 111.29h, 151.22h, and 329.56h. An even-rank tertile
split would have placed ties arbitrarily across band boundaries, so bands were drawn on the actual
clusters instead: **fresh** (<20h, the dominant batch), **mid** (20-60h), **stale** (>=60h).

Of the 76/78 echo qubits with a T1 date on record, **72 fall in the fresh band and only 2 each in
mid and stale** -- and of those 4 non-fresh qubits, **none** happens to also pass the SNR gate and
resolve clock A or B. Both the mid and stale existence cells are therefore **UNRESOLVED, n=0** for
every pair (A/B x T1/T2) -- not DOES NOT EXIST, genuinely untestable from this chip's own
calibration history on this day.

**Fresh band only** (n=51 for A-pairs, n=22 for B-pairs, same population as the main cutoff-0.50
matrix since it IS effectively the whole resolving population):

| pair | n | real R^2 | verdict |
|---|---|---|---|
| A <-> T1 | 51 | 0.013 | DOES NOT EXIST |
| A <-> T2 | 51 | 0.0005 | DOES NOT EXIST |
| B <-> T1 | 22 | 0.0017 | DOES NOT EXIST |
| B <-> T2 | 22 | 0.018 | DOES NOT EXIST |

**Does C exist to A/B for freshly calibrated qubits only?** Cannot be answered as posed -- the
chip gives almost no freshness contrast to test against (144/156 qubits share one calibration
timestamp), and within the one band that does have enough qubits to test, the answer is still NO:
C does not exist to A or B even restricted to the freshest qubits. The age variable this chip
actually offers is a 10-qubit tail of staleness against a 146-qubit uniform batch, too small to
resolve on either side of 60h.

---

## 3. The shot clock (buzz) as a third vantage

Tile-8's six even seats (80, 82, 96, 100, 102, 116) each have a first-look tone phase from
`look_phase.json` (circular mean of pubs p2/p3, Fez J1). Of those six, **four** (80, 96, 100, 116)
also resolve clock A on this (Marrakesh) echo run; 82 and 102 do not. n=4 is below the n>=6 floor
used elsewhere for a bootstrap, so an **exact permutation** test was used instead (all 24
orderings of y against fixed x, fraction of permutations with |r| >= |r_obs|, stated as exact):

| buzz phase vs | n | r_obs | sign | exact fraction |
|---|---|---|---|---|
| A | 4 | +0.758 | + | **1/24 = 0.042** |
| T1 | 4 | -0.549 | - | 13/24 = 0.542 |
| T2 | 4 | -0.562 | - | 9/24 = 0.375 |

**Buzz phase vs A is the one borderline result in this whole run**: 1/24 is the smallest possible
nonzero exact fraction obtainable with n=4 (only the observed ordering itself clears |r_obs|),
which lands exactly at the conventional 0.05 line by coincidence of n. It is flagged, not called
EXISTS or DOES NOT EXIST -- this script's verdict machinery requires n>=6 to issue either call,
and n=4 is openly too small to trust on its own; it did not clear a bootstrap because none was
run. Buzz phase shows no relation to T1 or T2 at this n (fractions 0.54 and 0.38, both far from
significant by any standard). The honest read: the shot clock's per-seat phase offset has a
suggestive, unverified lean toward A (the direct microsecond clock) and no visible lean toward C
(IBM's calibration) -- consistent with the main matrix's finding that A and C don't see each
other, but this one is n=4 and should not be leaned on.

---

## 4. The tile

Tile 8 (the buzz's tile: 80, 81, 82, 83, 96, 100, 101, 102, 103, 116) vs the rest of the chip,
A<->B existence at the primary cutoff 0.50:

| group | n | real R^2 | verdict |
|---|---|---|---|
| tile 8 | 1 | -- | UNRESOLVED (only 1 qubit resolves both A and B) |
| rest of chip | 20 | 0.255 | **EXISTS** |

Tile 8 itself cannot be tested at cutoff 0.50 -- of its 6 even seats, only one (q116, checked
directly) resolves both clock A and clock B at this cutoff; the rest of the chip's 20 doubly-
resolving qubits carry the whole EXISTS verdict from the main matrix. **The tile the buzz lives on
is the one place on the chip too thin to test**, not a place that fails the test.

Grouped into the remaining 15 tiles in bands of three (tile index order, tile 8 excluded):

| tiles | n | real R^2 | verdict |
|---|---|---|---|
| 0, 1, 2 | 5 | -- | UNRESOLVED (n<6) |
| 3, 4, 5 | 6 | 0.003 | DOES NOT EXIST |
| 6, 7, 9 | 3 | -- | UNRESOLVED (n<6) |
| 10, 11, 12 | 3 | -- | UNRESOLVED (n<6) |
| 13, 14, 15 | 3 | -- | UNRESOLVED (n<6) |

Every three-tile band is either UNRESOLVED for size or DOES NOT EXIST -- none individually
reproduces the whole-chip-minus-tile-8 EXISTS verdict. The EXISTS result at cutoff 0.50 is a
property of pooling the chip's resolving qubits broadly (n=20), not of any one small tile region;
no tile-sized subset, including tile 8, has enough resolving qubits on its own to confirm or
contradict it. **Does the buzz's tile see its clocks differently? Unknown -- it is the one tile
too sparse to put the question to.**

---

## 5. Plain words

**The dial settings where the chip's clocks exist to each other:** a band from readout cutoff
0.40 to 0.55 (four of four cutoffs in that range read EXISTS), plus one isolated spike at 0.65 that
a coarser 3-point sweep would have missed entirely. **The settings where they never do:** the
entire low end (0.20-0.35) and the entire high end (0.70-0.90) -- ten of fifteen cutoffs read
DOES NOT EXIST, and the number of qubits resolving at each cutoff does not explain the pattern
(r=0.28 against the R^2 curve). A<->B visibility is not a fixed property of the chip; it is a
property of where you set the readout line, and it switches on and off at least twice across the
dial, not once.

**C (IBM's T1/T2) remains invisible** to A and B even in the one slice of the data that could, in
principle, have shown otherwise (the freshest-calibrated qubits) -- but the test is weak: this
chip's calibration history on this day gives almost no age contrast to probe (144/156 qubits
share one timestamp), so "freshness doesn't help" is a real but thin finding, not a strong one.

**The shot clock (buzz) offers a genuinely new, independent vantage** on four tile-8 qubits, and
its one notable number -- phase vs A, exact fraction 1/24 -- leans toward A existing to the buzz,
not toward C. At n=4 this is a lead to revisit with more seats or more records, not a finding to
build on.

**The buzz's own tile is the one place the chip can't be tested on this echo run.** Tile 8 has
only 10 seats, 6 of them even (resolvable at all by this even-only run), and at the cutoffs that
otherwise show EXISTS, only one of those six clears both clock A and clock B. The tile that
carries the strongest anomalous signal elsewhere in this project (THE_BUZZ.md) is exactly the one
too small, on this particular dataset, to say whether its clocks behave like the rest of the
chip's.

---

## Failed rows / tries

- Clock A: 74-51=23 qubits fail to fit (no decaying 20/50/100us series) -- fixed across all 15
  cutoff tests (A does not depend on the readout cutoff).
- Clock B: fails for 74-n qubits per cutoff, n ranging 16-30 across the 15-point sweep (see table
  1) -- 15 separate resolve counts, none hidden.
- Age bands: mid band (20-60h) and stale band (>=60h) UNRESOLVED, n=0, for all 8 pair-tests (A/B
  x T1/T2) -- only 2 qubits per band have a T1 date in that range, and none of the 4 also resolves
  clock A or B. Reported as UNRESOLVED-for-size, not suppressed or treated as DOES NOT EXIST.
- Buzz vantage: 2 of 6 tile-8 even seats (82, 102) do not resolve clock A, dropped from the n=4
  comparison; T1/T2 comparisons used the same n=4 set, so sample size never silently grew.
- Tile tests: tile 8 alone UNRESOLVED (n=1); 4 of 5 three-tile groups UNRESOLVED (n<6, sizes 3 or
  5); only tiles {3,4,5} (n=6) and "rest of chip" (n=20) produced a verdict.
- Age timestamp parsing: all T1 `date` fields parsed successfully for 76/78 echo qubits; 2 qubits
  (checked: both already SNR-gated out or otherwise missing) have no T1 date on the 9/28 snapshot
  and are excluded from the age analysis entirely, not imputed.
- Echo run timestamp (2026-09-28 ~12:27:33 UTC) taken from the run directory's own name, as every
  prior doc in this project has used it (e.g. CLOCK_EXISTENCE_20261001.md's header) -- not an
  independently logged value on disk, flagged as read, not measured.

**Tries counted by the script itself: 142,773** -- 61,634 tau fits (clock A's one fit + bootstrap
draws, plus clock B's 15-cutoff fits + bootstraps, each counted individually) + 80,950 qubit-level
bootstrap draws (500 draws x each existence cell that reached the bootstrap stage: 15 cutoff cells
+ 2 reversed per cutoff... counted as the script's own accumulator reports, not recomputed by
hand) + 63 existence tests (15 cutoff x 2 directions + 2x4x3 age-band pairs + 2 tile cells + 2
rest-of-chip cells + 5 three-tile-group cells) + 82 Spearman calls (2 per existence test that
reached that stage) + 41 reversed-label calls (1 per existence test that reached that stage) + 3
exact-permutation enumerations (buzz vs A/T1/T2, 24 orderings each, 72 total correlation
evaluations inside those 3 calls).

---

# THE FLASH -- is 0.65 real? (2026-09-30, Bones's field hand)

Follows directly from Section 1 above: the coarse 0.05-step sweep sampled only 0.60 and 0.70
around the 0.65 spike, so it could not tell a true isolated point from a gap in sampling. Script:
`out/the_middle/the_flash.py` (numpy only, single process, ~7s runtime). Raw output:
`out/the_middle/the_flash_results.json`. Same data, same construction, same gate (74/78 qubits
pass SNR>=1.5; clock A resolves 51/74, fixed and cutoff-independent by construction -- confirmed
directly here, not re-derived, since A's internal threshold is hardcoded at 0.5 and never touches
the swept dial). **The only null is the REVERSED ASSIGNMENT of qubit labels**, stated as exactly
that, same as every other test in this project. No expectation written before running.

## 1. Is the 0.65 flash real? Fine sweep 0.56-0.72, step 0.01 (17 rulers)

| cutoff | n (both A&B) | real R^2 | boot err (300) | rev R^2 (null) | verdict | entered | left |
|---|---|---|---|---|---|---|---|
| 0.56 | 22 | 0.110 | 0.124 | 0.024 | DOES NOT EXIST | -- | -- |
| 0.57 | 21 | 0.199 | 0.177 | 0.084 | EXISTS | -- | q138 |
| 0.58 | 21 | 0.263 | 0.174 | 0.042 | EXISTS | -- | -- |
| 0.59 | 22 | 0.064 | 0.144 | 0.0002 | DOES NOT EXIST | q138 | -- |
| 0.60 | 23 | 0.007 | 0.145 | 0.014 | DOES NOT EXIST | q56 | -- |
| 0.61 | 22 | 0.153 | 0.171 | 0.039 | DOES NOT EXIST | -- | q138 |
| 0.62 | 22 | 0.228 | 0.197 | 0.050 | EXISTS | -- | -- |
| 0.63 | 22 | 0.278 | 0.215 | 0.062 | EXISTS | -- | -- |
| 0.64 | 22 | 0.322 | 0.206 | 0.058 | EXISTS | -- | -- |
| **0.65** | 21 | **0.433** | 0.222 | 0.075 | **EXISTS** | -- | **q56** |
| 0.66 | 19 | 0.001 | 0.084 | 0.024 | DOES NOT EXIST | -- | q14, q154 |
| 0.67 | 20 | 0.384 | 0.256 | 0.065 | EXISTS | q154 | -- |
| 0.68 | 20 | 0.309 | 0.223 | 0.075 | EXISTS | q14 | q42 |
| 0.69 | 19 | 0.004 | 0.067 | 0.063 | DOES NOT EXIST | -- | q154 |
| 0.70 | 20 | 0.006 | 0.080 | 0.086 | DOES NOT EXIST | q142 | -- |
| 0.71 | 19 | ~0.000 | 0.133 | 0.006 | DOES NOT EXIST | -- | q14 |
| 0.72 | 19 | ~0.000 | 0.116 | 0.004 | DOES NOT EXIST | -- | -- |

**Verdict: 0.65 is neither a lone point nor a bootstrap fluctuation -- it is the top of a narrow
rising sub-band (0.62-0.65, four consecutive EXISTS steps, R^2 climbing 0.228 -> 0.278 -> 0.322 ->
0.433), immediately followed by a single-step collapse at 0.66 (R^2 -> 0.001) and a second,
separate EXISTS pair at 0.67-0.68. The coarse 3-point and 15-point sweeps missed this structure
entirely because they sampled 0.60 and 0.70 and never looked at 0.66 directly.**

Checked against its own neighbors' bootstrap spread (the question asked): 0.65's R^2 (0.433) is
**within** cutoff 0.64's bootstrap spread (0.322 +/- 0.206 covers 0.433) -- the climb from 0.64 to
0.65 is NOT statistically distinguishable from noise on its own. But 0.65's R^2 is **not** within
0.66's spread (0.001 +/- 0.084 does not reach 0.433) -- the *drop* at 0.66 is the sharper,
better-resolved feature of the two edges. Read plainly: 0.65 is the peak of a real, multi-step
rising band, not a one-off spike, but the error bars at every step in this band are wide enough
(0.17-0.26) relative to the R^2 values themselves (0.11-0.43) that "0.65 specifically" is not
cleanly separable from "0.64 or 0.63" -- the honest claim is a band 0.62-0.65 with its maximum at
0.65, not a point.

**Resolving-set turnover is small and specific.** Across all 17 steps, only 6 distinct qubits ever
enter or leave the doubly-resolving set: q138 (flickers in/out 0.57-0.61, before the band of
interest), **q56 (leaves exactly at the 0.64->0.65 step, coincident with the jump to the sweep's
single highest R^2)**, q14 and q154 (both leave at the 0.66 collapse, q154 re-enters at 0.67, q14
re-enters at 0.68), and q142 (enters once at 0.70, in the dead zone). **q56 leaving the resolved
set is the one event that lines up exactly with the flash's peak** -- its departure, not an
arrival, is what coincides with the jump from R^2=0.322 (n=22) to R^2=0.433 (n=21). q14 and q154
leaving together is what coincides with the 0.66 collapse. No single qubit entering explains the
flash; one qubit's exit does.

## 2. Where is the band on the dot? (I/Q cloud geometry, 74 readable qubits)

Per qubit: the 0/1-cloud midpoint along the readout axis is **0.50 by construction** (the axis is
defined so cloud-0's median maps to 0 and cloud-1's median maps to 1) -- not an empirical finding,
stated as the geometric fact it is. The empirically meaningful number is the **equal-error
crossing fraction**, f = st0 / (st0 + st1), where st0 and st1 are the two clouds' robust (MAD)
widths along that axis -- the point where the 0-cloud's and 1-cloud's tails balance, which only
equals 0.50 when the clouds are equally wide.

| quantity | median | mean | std | min | max | n |
|---|---|---|---|---|---|---|
| equal-error crossing fraction | 0.5012 | 0.5034 | 0.0192 | 0.4661 | 0.6029 | 74 |
| 1-cloud inner edge (1 - st1, one sigma from center) | 0.8869 | 0.8809 | 0.0347 | -- | -- | 74 |

**Does the 0.40-0.55 band sit where the clouds overlap most?** Yes, closely. The equal-error
crossing's median (0.5012) sits inside the band, and **97.3% of all 74 qubits' individual crossing
fractions fall inside [0.40, 0.55]** -- the band is, almost without exception, exactly where each
qubit's own 0/1 clouds balance. The single widest outlier (max 0.6029) still falls short of the
flash point.

**Does 0.65 sit at the 1-cloud's inner edge?** No -- not even close. **Zero of 74 qubits** have an
equal-error crossing at or above 0.63 (none approach 0.65 from the overlap side), and the 1-cloud's
one-sigma inner edge sits at a pooled median of **0.887**, a full 0.237 above the flash point.
0.65 is not where the clouds balance (that's ~0.50, matching the band) and it is not where the
1-cloud's own tail begins to thin out (~0.89) -- it sits in the **dead middle of the 1-cloud's
body**, past the point where class-1 reads already dominate class-0 reads for essentially every
qubit, but well short of the region where the 1-cloud is nearly pure. There is no cloud-geometry
landmark at 0.65 for any qubit, individually or pooled; the flash is not explained by where the
dot's two populations physically sit.

## 3. Which clock does the switching: A, B, or the pair?

**Clock A is fixed by construction**: 51/74 resolve at every single one of the 17 cutoffs, because
clock A's internal classification threshold (0.5) is hardcoded in `corrected_carry()` and never
touches the swept readout-cutoff dial. A cannot be the thing switching -- it is literally the same
51 qubits with the same tau values at cutoff 0.56 as at cutoff 0.72.

**Clock B alone** resolves 19-25/74 across the fine window (tighter spread than the full 15-20-30
range of the original 0.05-step sweep), with no visible trend -- it does not monotonically shrink
or grow as the cutoff rises from 0.56 to 0.72. B's median tau wanders 74-92us with no step-pattern
matching the EXISTS/DOES NOT EXIST on/off pattern; the resolving-count-vs-R^2 correlation across
just this fine window is r=0.294 -- the same weak, non-explanatory value (r=0.28) found for the
full 15-point sweep. B's *membership* (which qubits resolve) changes qubit-by-qubit far more
sharply than B's *count* does -- six individual qubits flicker in and out across 17 steps, and
those flickers (q56 at 0.65, q14/q154 at 0.66) are exactly where the existence verdict flips.

**Verdict: it is clock B doing the switching, and specifically B's resolving-SET membership (which
individual qubits clear the readout threshold), not B's resolving-COUNT and not clock A at all.**
A is inert across the whole dial. The flash and the collapse that follows it are both qubit-level
exits from B's resolved set (q56 out at the flash; q14+q154 out at the collapse), not a change in
how many qubits resolve or in A's behavior.

## 4. Plain words

**Is the flash one qubit's doing?** Mostly, yes, at the edges of it. The 0.65 peak is the top of a
real four-step rising band (0.62-0.65), not a lone spike invented by coarse sampling -- but the
single qubit event that lines up exactly with the jump to the peak is q56 dropping out of clock
B's resolved set between 0.64 and 0.65. The band itself isn't "caused" by one qubit; its sharpest
edges (the step up into 0.65, and the collapse one step later at 0.66) each are.

**Where does the band sit on the readout dot?** Right where it should, geometrically: 0.40-0.55 is
almost exactly where each qubit's own 0-cloud and 1-cloud balance (97.3% of qubits' individual
equal-error crossings land inside that band). The 0.65 flash does NOT sit at any cloud landmark --
not the overlap point (~0.50) and not the 1-cloud's inner edge (~0.89, pooled median) -- it falls
in open space in the middle of the 1-cloud's body, where it has no obvious physical meaning from
the dot's geometry alone.

**Which clock switches?** Clock B, and specifically which qubits B resolves at a given cutoff --
not how many (count is flat and uncorrelated with the R^2 curve, same r~0.29 as before), and not
clock A, which is mathematically incapable of changing across this entire sweep.

## Failed rows / tries

- Clock A: fixed at 51/74 across all 17 fine cutoffs by construction, not independently
  recomputed per cutoff (recomputing would only reproduce identical numbers) -- confirmed, not
  assumed.
- Clock B: resolves 19-25/74 per cutoff across the 17-point fine sweep -- every count reported in
  the table above, none hidden.
- Cloud geometry: all 74 readable qubits produced a finite st0/st1 pair; none excluded or imputed.
- The 0.66 single-step collapse (R^2 0.433 -> 0.001) coincides with TWO qubits (q14, q154) leaving
  simultaneously, not one -- reported as such, not forced into the one-qubit framing that fits
  the 0.65 side.
- q138's flicker (0.57-0.61) sits outside the 0.62-0.68 region of interest and is reported as
  context, not folded into the flash's own account.

**Tries counted by the script itself: 128,068** -- 59,532 tau fits (clock A once per qubit, clock
B at 17 cutoffs x each qubit, plus every bootstrap draw's own fit) + 68,400 qubit-level bootstrap
draws (150 per clock-B fit x 17 cutoffs x 74 qubits for B's own error bars, plus 300 per existence
cell x 17 existence cells here) + 34 existence tests (17 cutoffs x 2 directions) + 68 Spearman
calls (2 per existence test, counted directly by the script's own accumulator) + 34 reversed-label
calls (1 per existence test).
