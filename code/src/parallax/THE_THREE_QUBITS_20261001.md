# THE THREE QUBITS -- what q56, q14 and q154 are, and whether the flash needs the carry

Wayfinder, following THREE_TIMES_VISIBILITY_20261001.md's "THE FLASH" section (2026-09-30): the
0.62-0.65 rising sub-band in clock A<->B existence R^2 peaks exactly when **q56** leaves clock B's
resolved set (0.64->0.65), and collapses exactly when **q14** and **q154** leave together
(0.65->0.66). This asks what those three qubits (plus the three other qubits that ever flicker
across the same 17-cutoff sweep -- q138, q142, q42) have on file, whether the band survives
without the short-gap decay fit ("the carry"), and whether a second chip shows anything like it.

**Scope.** Data on disk only. No expectation written before running. Raw first. Script:
`out/the_middle/the_three_qubits.py` (numpy only, single process, ~43s runtime). Raw output:
`out/the_middle/the_three_qubits_results.json`. Data: `out/echo_20260928_122733/` (ibm_marrakesh,
78 even qubits, 74 pass SNR>=1.5), `out/ibm_cal_20260929/ibm_marrakesh/{2026-09-26,2026-09-28}.json.gz`
calibration snapshots, `out/20260928_123452/` (ibm_kingston parallax run, 78 even qubits, two
looks per shot on J1), and `out/the_buzz/heron.py`'s tile carving (read verbatim, asserted
layout). **The only null is the REVERSED ASSIGNMENT of qubit labels**, stated as exactly that,
same construction as every prior script in this project.

---

## 1. The three qubits (and the three other flicker qubits)

Full report card, all values read or computed directly, none imputed:

| qubit | tile | T1 9/26->9/28 (us) | T1 swing | T2 9/26->9/28 (us) | T2 swing | RO err 9/28 | A tau (us) | B tau @0.50 | B tau @0.65 | crossing frac | blink rate @2000us | in tile8 | in blinkers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **q56** | 4 | 135.21 -> 184.21 | **x1.362** | 22.09 -> 32.69 | x1.480 | 0.0056 | 8.49 | 81.14 | -- (left set) | 0.5170 | 0.0027 | no | no |
| **q14** | 3 | 347.83 -> 274.99 | **x0.791** | 79.29 -> 85.01 | x1.072 | 0.0071 | 223.83 | 170.56 | 734.90 | 0.5151 | 0.0334 | no | no |
| **q154** | 15 | 299.63 -> 291.12 | x0.972 | 32.10 -> 33.20 | x1.034 | 0.0092 | 270.52 | 251.01 | 1289.50 | 0.5041 | 0.0040 | no | no |
| q138 | 14 | 241.15 -> 231.68 | x0.961 | 119.42 -> 30.48 | x0.255 | 0.0054 | 9.76 | 39.36 | -- (left set) | 0.5074 | 0.0133 | no | no |
| q142 | 12 | 107.33 -> 170.72 | x1.591 | 45.74 -> 136.90 | x2.993 | 0.0200 | 158.55 | -- (never resolves) | -- | 0.4850 | 0.0207 | no | no |
| q42 | 4 | 166.96 -> 211.91 | x1.269 | 117.03 -> 50.98 | x0.436 | 0.0116 | 47.04 | 224.67 | 63.83 | 0.5000 | 0.0060 | no | no |

(A tau is clock A's fixed decay time, FAST=[20,50,100]us; B tau is clock B's decay time at the
given cutoff; "crossing frac" is the equal-error point st0/(st0+st1) along the readout axis;
"blink rate" is the fraction of consecutive-shot transitions across the 0.5 threshold in the
2000us-gap series, pooled over E0/E1.)

**All six are readable (SNR>=1.5) and all six resolve clock A** (A is cutoff-independent by
construction). **None of the six sits in tile 8** (the Fez/Kingston buzz tile) **or in the named
blinkers {q68, q76}** -- these are a different population from every prior named list in this
project. q56 and q42 share tile 4; the other four sit on four more different tiles (3, 12, 14,
15) -- the six flicker qubits are spread across five of the chip's sixteen tiles, not clustered.

### Is there anything the three (q56, q14, q154) share that the other 71 don't?

Nine candidate properties tested, exact permutation fraction = C(k,3)/C(74,3) wherever all three
land inside a subgroup of size k (an exact hypergeometric point, not a Monte Carlo draw):

| candidate property | k (of 74) | all three share it? | exact fraction C(k,3)/C(74,3) |
|---|---|---|---|
| resolves clock A | 51 | **yes** | **0.3213** |
| equal-error crossing fraction above the readable-set median | 37 | **yes** | **0.1199** |
| T1 swing direction (down, 9/26->9/28) | 43 | no | -- |
| T1 swing direction (up/flat) | 31 | no | -- |
| T2 swing direction (down) | 35 | no | -- |
| readout error above median | 37 | no | -- |
| blink rate @2000us above median | 37 | no | -- |
| share the same tile | -- | no (tiles 4, 3, 15) | -- |
| any of the three in the named blinkers {68,76} | 2 | no | -- |
| any of the three in tile 8 | 4 | no | -- |

**Only two of nine candidates hold for all three, and both are weak.** Resolving clock A is
necessary just to be a candidate for this whole flicker analysis (51/74 already resolve it, so a
random triple lands inside that set 32% of the time by chance alone) -- not a distinguishing
property. The equal-error crossing fraction is more interesting: all three (0.5151, 0.5170,
0.5041) sit above the readable-set median, a configuration a random triple would also produce
12.0% of the time -- a lean, not a rare coincidence. T1 swing direction, T2 swing direction,
readout error rank, blink rate, and tile membership all fail to be shared. **No tile, no blinker
list, and no T1/T2/readout-error property distinguishes these three qubits from the chip's other
71** -- what they share is being three of the fixed 51 clock-A resolvers with slightly
overlap-shifted (not clean 50/50) 0/1 clouds, and nothing more specific found on file.

---

## 2. The second band without the carry

Same 17-cutoff fine sweep (0.56-0.72, step 0.01). A tau-fit decay ("the carry") cannot be built
from a single gap, so each of the three conditions below uses a **raw single-gap statistic**
instead of a fitted tau: clock A's raw value is `corrected_carry(gap)` (the lag1-vs-lag20 carry
statistic itself, undecayed) and clock B's raw value is the plain rate `P(readout > cutoff)` at
that one gap (no excess-vs-floor subtraction, since the floor and the test point would otherwise
be the same gap in the 2000/2000 condition). Three curves, same existence-cell machinery
(OLS R^2 + qubit bootstrap + reversed-label null):

| cutoff | 20/20 R^2 | verdict | 2000/2000 R^2 | verdict | 20/2000 R^2 | verdict |
|---|---|---|---|---|---|---|
| 0.56 | 0.0287 | DOES NOT EXIST | 0.0013 | DOES NOT EXIST | 0.0083 | DOES NOT EXIST |
| 0.60 | 0.0268 | DOES NOT EXIST | 0.0016 | DOES NOT EXIST | 0.0098 | DOES NOT EXIST |
| 0.65 | 0.0219 | DOES NOT EXIST | 0.0018 | DOES NOT EXIST | 0.0131 | DOES NOT EXIST |
| 0.66 | 0.0214 | DOES NOT EXIST | 0.0016 | DOES NOT EXIST | 0.0140 | DOES NOT EXIST |
| 0.72 | 0.0139 | DOES NOT EXIST | 0.0009 | DOES NOT EXIST | 0.0207 | DOES NOT EXIST |

(full 17-row table in the raw JSON; every one of all 51 cells across all three conditions reads
DOES NOT EXIST, R^2 never exceeds 0.029 anywhere, and none of the three curves shows any trace of
a rise toward 0.65 or a collapse at 0.66.)

**Verdict: the band needs the carry.** Strip the tau fit down to a raw single-gap number -- at
20us (where the clustering is present), at 2000us (where it's gone), or mixed -- and the entire
0.56-0.72 existence structure disappears flat, everywhere, in all three conditions. The 0.62-0.65
rise and the 0.66 collapse are not a property of the readout cutoff interacting with a raw
short-gap or long-gap rate; they are a property of the fitted decay time specifically, which only
exists once you have the multi-gap series to fit (FAST=[20,50,100]us) and the per-qubit set that
clears a given cutoff at each of those three gaps. No carry, no band.

---

## 3. The band's other witness: Kingston

The Kingston parallax run (`out/20260928_123452/`) has a different design from Marrakesh's
echo run -- no 7-point multi-gap echo series exists for it. What it does give: three distinct
single-look gaps across separate jobs (J2=20us, J4=250us [IBM's unrecorded default, same
assumption used elsewhere in this project], J3=1000us) for a genuine clock-A tau fit, and one job
(J1) with **two looks per shot** (D0/D1 pubs) for a direct two-look drain as clock B's analog (no
tau fit possible or needed -- one job, one number per cutoff).

- 77/78 qubits pass SNR>=1.5 (vs Marrakesh's 74/78).
- Clock A (3-gap tau fit) resolves 29/77 qubits -- smaller than Marrakesh's 51/74, consistent with
  Kingston's gap set (20/250/1000us) being coarser than Marrakesh's (20/50/100us).
- The fine sweep (0.56-0.72, 17 cutoffs) against the two-look drain: **R^2 never exceeds 0.0012
  anywhere in the whole sweep**, bootstrap error is 30-50x the signal at every cutoff
  (R^2 ~0.0002-0.0012 against boot err ~0.028-0.050), and **zero of 17 cutoffs reads EXISTS**.

**Verdict: no band on Kingston, in open space, with this construction.** The chip's own clock A
tau fit resolves plenty of qubits (29), but it carries no detectable relationship to the two-look
drain at any cutoff from 0.56 to 0.72 -- not a weak echo of Marrakesh's structure, a flat null
across the entire dial. This is a different clock-B analog (two-look drain within one job, not a
3-gap decay-vs-floor fit), so it cannot rule out that Marrakesh's specific construction would also
find something on Kingston if replicated gap-for-gap -- but with the data Kingston actually
offers, the band does not reproduce.

---

## 4. Plain words

**What are the three qubits?** q56, q14 and q154 are three of Marrakesh's 51 fixed clock-A
resolvers, scattered across three different tiles (4, 3, 15) with no tile, blinker-list, T1/T2
swing-direction, or readout-error property in common. The only shared trait found on file is a
mild one: all three sit on the high side of the chip's equal-error 0/1-crossing-fraction median
(a configuration ~12% of random triples would also show) -- a lean, not a signature. They are not
corner qubits, not tile-8 qubits, not the named blinkers, and not unusually fast- or slow-swinging
on T1/T2 between 9/26 and 9/28. What makes them notable is purely dynamical, not structural: q56
is the one qubit whose clock-B resolution exit lines up with the band's peak, and q14+q154 are the
pair whose simultaneous exit lines up with its collapse one cutoff later.

**Does the second band need the carry?** Yes, cleanly. Replacing the fitted decay time with any
raw single-gap statistic -- short gap alone, long gap alone, or mixed -- erases the entire
existence structure across all 17 cutoffs in all three conditions. The band is a property of the
fit, not of any one gap's raw readout rate.

**Does a second chip show a band in open space?** No. Kingston, read through its own available
clocks (a 3-gap tau fit for A, a one-job two-look drain for B), shows no existence band anywhere
in the same 0.56-0.72 cutoff range -- R^2 stays at or below 0.0012 the whole way, dwarfed by its
own bootstrap error at every step.

---

## Failed rows / tries

- B(0.65) is unresolved (`None`) for q56 and q138 -- both already left clock B's resolving set by
  that cutoff (0.65 and 0.61 respectively) -- reported as such, not imputed or back-filled.
- q142 never resolves clock B at either 0.50 or 0.65 -- its excess curve never produces a valid
  decay fit at these cutoffs on this chip; reported as unresolved, not forced.
- "share_same_tile" and the two "any-in-named-list" checks (blinkers, tile8) have no meaningful k
  for the exact-fraction formula (the three qubits don't form a shared subgroup for those
  properties) -- reported as "no" with no fraction computed, not a 0.000 placeholder.
- Kingston's clock-B analog (two-look drain, J1 only) is a genuinely different construction from
  Marrakesh's 3-gap decay-vs-floor clock B -- the null result does not rule out Marrakesh's exact
  method reproducing on Kingston if a matching multi-gap echo run existed for it; none does on
  disk.
- Kingston's J4/J1 rep_delay is recorded as `null` in `meta.json`; assumed IBM's default 250us,
  the same assumption THE_BUZZ.md and CHIP_TRIANGLE_20261001.md make elsewhere for unset
  rep_delay fields -- flagged as an assumption, not an independent measurement.
- The fine-sweep resolving-set reproduction in Section 1 used a cheap 50-draw bootstrap (vs the
  original 300) purely to recover qubit entry/exit membership per cutoff for the report table --
  verdicts from this cheap pass are not re-asserted as EXISTS/DOES NOT EXIST findings; the
  verdicts already stand from THE_FLASH's own 300-draw run.

**Tries counted by the script itself: 23,149** -- 1,557 tau fits (clock A once per qubit on both
chips + clock B at 0.50/0.65/17-cutoff-cheap-pass on Marrakesh + Kingston's 3-gap clock A) +
21,250 qubit-level bootstrap draws (300 per existence cell x 51 cells for the three raw-gap
curves + Kingston's 17 cells, plus 50 per cheap resolving-set pass x 16 cutoffs) + 85 existence
tests (3 conditions x 17 cutoffs + 17 Kingston cutoffs + 16 cheap resolving-set passes + a few
scalar cells) + 170 Spearman calls (2 per existence test) + 85 reversed-label calls (1 per
existence test) + 2 permutation evaluations (the two shared properties that cleared the
all-three-share filter).
