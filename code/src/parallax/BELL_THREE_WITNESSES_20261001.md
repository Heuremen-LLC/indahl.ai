# THREE WITNESSES -- does the NIST 50 us spot exist on Delft or Munich? 2026-10-01

Wayfinder's question: the NIST 2015 lead (`BELL_NEIGHBORS_20260930.md`, sharpened in
`BELL_DISCOUNT_20260930.md`) is Bob's click at trial t going with a lower Alice click rate at
t-5 (50 us at NIST's 100 kHz clock), ratio ~3.5, same sign in all 8 NIST runs, mirrored, isolated
(gone by lag 6, flat to lag 50). Does the SAME SPOT exist on Delft 2015 (NV centres, event-ready)
or Munich 2017 (atoms) -- different apparatus, different clock, different trial count? No
expectation written first. Raw first. Every test counted, sign kept, record vs record is the
judge (no shuffle). Script: `parallax/out/superposition_nist/three_witnesses.py`. Raw+pooled
output: `three_witnesses_results.json`. Log: `three_witnesses_stdout.log`.

**Tries: 316 raw test rows, 0 failed.** Delft run1 18 cells + run2 18 cells (2 directions x 3
lags x 3 splits each) = 36. Munich pairs: 2 sessions x 20 lags (-10..-1,+1..+10) x 2 directions x
3 splits = 240. Munich same-side exclusion (the real click/no-click analog): 2 sessions x 2 labs
x 10 lags = 40. 36+240+40 = 316.

## 1. LAYOUT -- what is a "trial" on each record?

- **NIST 2015** (from prior work, restated for comparison): a trial is one 100 kHz Pockels-cell
  clock tick, 10 us apart, EVERY tick logged whether or not a detector fired (click = any of 16
  window slots). 8 runs, 177.9M-356.5M trials each, strictly time-ordered by trial index. A fixed
  clock: lag 5 = exactly 50 us, always.
- **Delft 2015 (run1, Hensen et al. Nature 526)**: a "trial" here is a KEPT event-ready herald
  (245 of them, out of 4,746 candidate heralds, out of billions of unlogged attempts with no
  herald at all -- see `bell/README.md`). Settings (a,b) and both readout clicks (x=-1 is a real,
  logged no-click outcome, not a discard) exist for all 245. Trials ARE time-ordered (the file's
  own timestamp column, microsecond precision) but NOT evenly spaced: measured median gap between
  consecutive KEPT trials = **2,383 s** (~40 min), min **2.36 s**, max **172,019 s** (~2 days).
  There is no fixed clock -- "trial t+1" can be seconds or days after trial t.
- **Delft 2016 (run2, Hensen et al. Sci Rep 6, replication, same NV apparatus)**: 300 kept trials
  (old + new APD subsets concatenated in time order). Median gap **2,017 s**, min **5.08 s**, max
  **498,988 s**. Read as a same-apparatus robustness check on Delft run1, not a fourth witness.
- **Munich 2017 (Rosenfeld et al., atoms, two sessions on disk: 2016-04-15 n=10,201 pairs,
  2016-06-14 n=10,202 pairs)**: a "trial" in the `*_pairs.csv` file is a VALID matched atom-atom
  event (both labs' setting + result, Unix-ms timestamp, strictly time-ordered -- verified
  monotonic). Measured median gap: **20.5 s** (0415) / **46.3 s** (0614), min **85 ms** / **157
  ms**, max ~**6,619 s** / **19,841 s**. The raw `*_lab_1/2.csv` files additionally log EVERY
  attempt including excluded ones (maintenance, detector/laser malfunction, stated in a comment
  field) -- the one place a genuine click/no-click (valid/excluded) dimension exists on this
  record, tested separately in Part 3 below, same-side only (no cross-lab index exists for
  excluded attempts, only for matched valid pairs).

**Row for this section: Delft's 245 (run1) / 300 (run2) trials are far too few for a d=1..10
neighbor sweep with usable error bars at every split** -- per the task's own instruction, lag
1-3 only is run on Delft, both directions, unsplit and split by the far side's setting, with
plain binomial SE (not shuffle). Munich's ~10,200 pairs per session support the full d=
-10..-1,+1..+10 sweep as on NIST.

## 2. THE SAME TEST, converted to microseconds

### Delft (run1 / run2), lag 1-3, bob->alice and alice->bob, unsplit (n too small to also show
every split cell here; full 36-cell table in the JSON)

| record | lag | real median gap | bob->alice diff (pp) | se (pp) | z | alice->bob diff (pp) | se (pp) | z |
|---|---|---|---|---|---|---|---|---|
| run1 | 1 | 2,383 s | -5.28 | 4.61 | -1.14 | +1.84 | 4.45 | +0.41 |
| run1 | 2 | ~4,766 s | -3.15 | 4.64 | -0.68 | -4.16 | 4.44 | -0.94 |
| run1 | 3 | ~7,149 s | +3.74 | 4.62 | +0.81 | +1.03 | 4.49 | +0.23 |
| run2 | 1 | 2,017 s | -5.41 | 4.25 | -1.27 | +6.31 | 4.05 | +1.56 |
| run2 | 2 | ~4,035 s | -0.67 | 4.29 | -0.16 | +1.70 | 4.05 | +0.42 |
| run2 | 3 | ~6,052 s | +3.01 | 4.28 | +0.70 | -1.59 | 4.03 | -0.39 |

No cell reaches |z|>1.6 on either run, either direction, lag 1-3, with or without the
far-side-setting split (full 36 rows in JSON, worst split cell is run1 alice->bob lag2
split=bob-setting=0, z=-2.33, one of 36 -- in line with the ~0.7 expected hits above |z|=2 by
chance in 36 correlated tests, not called out as a lead on an n this small).

### Munich (both sessions), lag -10..+10, result-bit cross-witness, unsplit (full table: 240
cells in JSON; sample below)

CAVEAT carried through: `pairs.csv` has no no-click trial (every row is already a valid detected
event); "click" here is approximated by the measurement RESULT bit, the closest analog this file
offers. The real click/no-click test is Part 3.

| session | lag | real elapsed time (median) | bob->alice diff (pp) | se (pp) | z |
|---|---|---|---|---|---|
| 0415 | +1 | 20.5 s | -0.62 | 0.68 | -0.91 |
| 0415 | -1 | -20.5 s | -0.10 | 0.68 | -0.14 |
| 0415 | +5 | ~102 s | (in JSON) | | |
| 0614 | +1 | 46.3 s | +0.13 | 0.71 | +0.18 |
| 0614 | -1 | -46.3 s | +0.08 | 0.71 | +0.11 |

Across all 240 Munich result-bit cells (both sessions, both directions, lag 1-10, unsplit +2
splits), nothing clears |z|=2 with a consistent sign between the two sessions; the handful above
|z|=1.5 flip sign session to session (e.g. 0614 lag+1 split0 z=+1.19 vs 0415 lag+1 split0
z=-0.58). **No cross-session-agreeing cell anywhere in the Munich result-bit sweep.**

### Munich same-side exclusion test (Part 3, the genuine click/no-click analog)

| record | lag 1 | lag 5 | lag 10 | shape |
|---|---|---|---|---|
| 0415 lab_1 | z=+10.6, +0.147pp | z=+4.5, +0.108pp | z=+1.8, +0.058pp | smooth decay |
| 0415 lab_2 | z=+24.1, +0.410pp | z=+7.7, +0.292pp | z=+3.2, +0.164pp | smooth decay |
| 0614 lab_1 | z=+118.9, +3.08pp | z=+63.9, +2.94pp | z=+51.2, +2.84pp | smooth decay |
| 0614 lab_2 | z=+121.3, +4.29pp | z=+47.9, +3.78pp | z=+30.1, +3.23pp | smooth decay |

This IS a real, large, same-side neighbor effect -- but its shape is a slow, monotone decay from
lag 1 to lag 10 (full per-lag table in JSON), not an isolated spike. It is the signature of
exclusion periods running for many CONSECUTIVE attempts in a block (the comment field in the raw
csv names the cause directly: "Maintenance," detector/laser malfunction), which is exactly the
kind of block structure that makes neighboring attempts' exclusion status strongly correlated for
many lags in a row. This is the opposite shape from NIST's lead (isolated at lag 5, back to noise
by lag 6-7, flat to lag 50) -- an ordinary, named, mechanical cause, not a candidate for the same
phenomenon.

## 3. THE TRIANGLE

**The 50 us cell:**

| record | can the 50 us gap even be formed between two logged trials? | call |
|---|---|---|
| NIST | yes -- lag 5 = exactly 50 us on its fixed 100 kHz clock | ratio 3.59/3.52, AGREE 8/8 runs (prior work) |
| Delft (run1, run2) | **no** -- min gap ever observed between consecutive KEPT trials is 2.36 s / 5.08 s; even the full (pre-filter) candidate-herald stream's fastest back-to-back pair is 1.365 ms. 50 us is ~27x faster than the single fastest gap this record has ever logged. | **CAN'T BE READ** |
| Munich (both sessions) | **no** -- min gap ever observed between consecutive valid pairs is 85 ms / 157 ms. 50 us is >1,600x faster than the fastest gap logged. | **CAN'T BE READ** |

50 us sits deep inside a single inter-trial gap on both Delft and Munich -- not between two
trials, inside one. The test as specified (compare neighbor rate at the lag equal to 50 us) has
no cell to compute on either record: there is no pair of logged trials anywhere in either data
set separated by anything near 50 us. This is not a null result; it is "no instrument."

**The lag-1 (nearest-logged-neighbor) cell, as the control:**

| record | what "lag 1" means in real time | result | call |
|---|---|---|---|
| NIST | 10 us (fixed) | ratio 2.3 (unsplit, UNSTABLE) to 2.8 (setting-split, AGREE) across 8 runs -- small, real, reproducible | reference point |
| Delft run1/run2 | 2,017-2,383 s (median) | \|z\|<1.3 both runs, both directions | **CAN'T BE READ** -- wrong timescale AND no power |
| Munich 0415/0614 | 20.5 s / 46.3 s (median) | \|z\|<1.0 (session 0415) to \|z\|<1.4 (session 0614), opposite signs between the two sessions | **CAN'T BE READ** -- wrong timescale AND no power |

Two separate reasons the lag-1 control can't be read as agreement or disagreement with NIST: (1)
"lag 1" is NOT the same real-world time gap in any of the three records (10 us vs tens of
seconds vs thousands of seconds) -- these are not comparable cells even in name only; (2) Delft's
245/300 trials and Munich's ~10,200 pairs per session have nowhere near the statistical power to
see an effect the size of NIST's (0.01 pp needs ~10^8 trials to resolve at this sample's binomial
noise floor; Delft/Munich's se's here are 4-7 pp and 0.7-1.0 pp respectively, 400-700x too wide).
An effect of NIST's actual size would be invisible on either record even if it were there.

**STABLE DISAGREEMENT: zero cells, on either record, at either the 50 us cell or the lag-1
control** -- there is nothing to disagree WITH; both alternate cells are CAN'T BE READ, not a
contrary reading.

## 4. Plain words

Does the NIST 50 us spot travel to a second apparatus? **It cannot be tested on either Delft or
Munich, at all, with the data on disk.** Both are herald-triggered, irregularly-spaced-trial
experiments whose fastest-ever logged gap between two trials (1.4 ms candidate-herald rate at
Delft; 85 ms at Munich) is already 27-1,600x slower than the 50 us NIST spot sits at. The 50 us
gap doesn't fall between any two trials on these records -- it's buried inside the dead time of
one single trial. This isn't "we looked and it's not there" (a DISAGREE); it's "there's no clock
fine enough here to look" (CAN'T BE READ), and that absence of an instrument is itself the answer
to "is this NIST's hardware" -- it means NIST is currently the ONLY apparatus with a clock fast
enough to even pose the question, so "does it travel" has no second witness yet, loophole-free or
not.

What each record COULD say: at the only lags they actually support (1-3 trials for Delft, 1-10
for Munich, in whatever real seconds those lags happen to span), neither shows a cross-witness
neighbor effect clearing |z|=2 with a consistent sign across its own two sub-records (Delft
run1/run2; Munich's two sessions) -- but at sample sizes 400-700x too small to see NIST's actual
effect size, that's a null with no power behind it, not a clean miss. The one real same-side
neighbor effect found on Munich (lab exclusion flags, |z| up to 121) is a slow multi-lag decay
tied to named maintenance/malfunction blocks in the data itself -- a different, ordinary,
already-labeled cause, and a different shape (plateau, not spike) from the NIST lead either way.

**What would actually test this**: a Bell record with a trial clock in the tens-of-microseconds
range AND loophole-free status -- none of the three records on disk besides NIST has one. Vienna
(Giustina et al.) has no public per-trial data at all (see `bell/README.md`). Until a
microsecond-clock loophole-free record other than NIST surfaces, "does the 50 us spot travel" is
an open question with exactly one witness.
