# THE NEIGHBORS -- what do the trials AROUND a click think of it? NIST 2015, 2026-09-30

Wayfinder's question: not the matched trial (the Bell correlation, everybody's instrument) -- the trials
AROUND it. No expectation written before running. Data: 8 NIST 2015 loophole-free Bell test runs,
`~/bones-forge/public_bell/nist2015/*.hdf5`, 177.9M-356.5M trials each, aligned by trial index at Alice and
Bob. Streamed in 10M-row HDF5 chunks into per-run boolean arrays (reuses `pipeline.py`'s `load_run`), freed
before the next run. CLICK = any of 16 Pockels-window slots fired. SETTING = the per-trial RNG choice bit
(boolean). No shuffle used as judge anywhere; every number below is printed by `neighbors.py`.

Scripts: `parallax/out/superposition_nist/neighbors.py`. Raw per-run results (1,360 rows):
`neighbors_raw.json`. Run-vs-run pooled cells (170): `neighbors_runvrun.json`, `neighbors_table_dump.csv`.
Log: `neighbors_log.txt` / `neighbors_stdout.log`.

Total wall time: 2,353 s (~39 min) for all 8 runs, no bootstrap loops (pure vectorized binomial arithmetic).

## Tries counted

- Part 1 (cross-witness neighborhood): 2 directions (Bob->Alice, Alice->Bob) x 8 runs x [10 lags + 3 groups]
  x [1 unsplit + 2 source-setting + 2 target-setting] = **1,040 raw test rows**, pooling to **130 run-vs-run
  cells**.
- Part 2 (the null's own neighbors, same side): 2 sides x 8 runs x 10 lags = **160 raw test rows**, pooling
  to **20 run-vs-run cells** (each lag's +d and -d land on the SAME cell key by construction here -- see
  note below).
- Part 3 (setting neighbors): 2 direction-pairs x 8 runs x 10 lags = **160 raw test rows**, pooling to **20
  run-vs-run cells**.
- **Grand total: 1,360 raw test rows, 170 run-vs-run pooled cells.** Every cell in the table below is a row;
  none were dropped except cells where a run legitimately had zero trials in a split subgroup (none occurred
  -- all 170 cells have all 8 runs).

Note on Part 2's lag symmetry: `carry_lag(click, click, lag)` conditions on click at t and reads the outcome
at t+lag; for a stationary same-side series the (t, t+lag) and (t, t-lag) pairs draw from the same population
of adjacent-click gaps up to edge effects, so lag+k and lag-k came out numerically identical to 5+ decimal
places in every run (confirmed in the raw json) -- that identity is expected symmetry of the statistic, not
new information, and is reported as-is (both lag+k and lag-k rows kept, not merged, per "every failed cell a
row" / "count every test").

## 1. CROSS-WITNESS NEIGHBORHOOD -- Bob click -> Alice's neighbor rate (and mirror), minus Alice's own
   overall rate, binomial SE on the conditioned side only

130 pooled cells (89 AGREE / 41 UNSTABLE / 0 STABLE DISAGREEMENT across the 8 runs). Strongest cells by
|pooled diff| / between-run SE (the ratio that answers "beyond the between-run spread"):

| direction | cell | split | pooled diff (pp) | between-run SE (pp) | ratio | run-vs-run call |
|---|---|---|---|---|---|---|
| a->b | lag-5 | target_setting=1 | -0.01083 | 0.00302 | **3.59** | AGREE |
| b->a | lag+5 | source_setting=1 | -0.00647 | 0.00184 | **3.52** | AGREE |
| a->b | lag-4 | source_setting=0 | -0.01169 | 0.00348 | 3.36 | AGREE |
| b->a | lag+4 | target_setting=0 | -0.00550 | 0.00164 | 3.36 | AGREE |
| b->a | lag+5 | (unsplit) | -0.00551 | 0.00181 | 3.04 | AGREE |
| a->b | lag-5 | (unsplit) | -0.00615 | 0.00209 | 2.94 | AGREE |
| a->b | group_far_neg | source_setting=0 | -0.00729 | 0.00259 | 2.81 | AGREE |
| b->a | lag+1 | source_setting=1 | +0.00585 | 0.00209 | 2.80 | AGREE |
| b->a | lag+1 | (unsplit) | +0.00697 | 0.00303 | 2.30 | **UNSTABLE** |

Strongest cell overall: **a->b, lag-5, split on target's (Bob's) setting at t+d = 1**: pooled -0.01083 pp,
between-run SE 0.00302 pp, ratio 3.59, and the run-vs-run call is AGREE (all 8 runs' own binomial error bars
cover the pooled value -- the effect, small as it is, replicates in direction and rough size across all 8
runs, not just one). 21 of 130 cells clear ratio >= 2 (chance expectation for a two-sided z-like threshold on
130 independent tests would be ~6; correlated/nested lags and mirrored directions mean these are not
independent draws, so this is suggestive, not corrected-significant). 5 clear ratio >= 3; only the top 2
clear ratio >= 3.5. None of the 130 cells is a STABLE DISAGREEMENT (mixed sign or error-unmatched runs beyond
spread with 8 same-signed runs) -- the "b->a lag+1 unsplit" cell has ratio 2.30 but is called UNSTABLE because
individual runs' own binomial error bars do not all cover the pooled value, i.e. the runs disagree with EACH
OTHER more than their own statistical error would predict, even though the sign is consistent.

## 2. THE NULL'S OWN NEIGHBORS -- same side, click rate at t+d given non-click at t minus given click at t

20 pooled cells (12 AGREE / 8 UNSTABLE). Strongest:

| side | lag | pooled diff (pp) | between-run SE (pp) | ratio | call |
|---|---|---|---|---|---|
| a | lag-2 / lag+2 | -0.00366 | 0.00243 | 1.50 | AGREE |
| b | lag-5 / lag+5 | +0.00294 | 0.00206 | 1.43 | AGREE |
| b | lag-2 | +0.00211 | 0.00201 | 1.05 | AGREE |

Nothing here clears ratio 2. Extending the earlier arisen-carry result (lags 1-3, positive only) to both
signs and out to 5 lags finds no side/lag where a click's own-side neighbors (before OR after) read
differently from a non-click's neighbors beyond the between-run spread. Run 03_12/b/lag-5 alone hits z=2.07
within its own binomial error, but the other 7 runs scatter around zero and pull the pooled ratio to 1.43 --
exactly the kind of single-run flicker the run-vs-run test is built to catch and discount.

## 3. SETTING NEIGHBORS -- click rate at t given the OTHER side's setting at t+d

20 pooled cells (17 AGREE / 3 UNSTABLE). Strongest:

| direction | lag | pooled diff (pp) | between-run SE (pp) | ratio | call |
|---|---|---|---|---|---|
| Alice's setting -> Bob's click | lag-1 | -0.00039 | 0.00018 | **2.22** | AGREE |
| Alice's setting -> Bob's click | lag+4 | -0.00037 | 0.00018 | 2.06 | AGREE |
| Alice's setting -> Bob's click | lag+5 | -0.00031 | 0.00016 | 2.02 | AGREE |
| Alice's setting -> Bob's click | lag-4 | -0.00024 | 0.00013 | 1.78 | AGREE |

Strongest cell: **Alice's setting at t-1 predicts Bob's click rate at t**, pooled -0.00039 pp, ratio 2.22,
AGREE across all 8 runs -- consistent direction, tiny magnitude (four orders smaller than a percentage
point). This sits right next to lag 0's already-known result (the standing "Bob's click rate 0.53% +/- 0.13%
lower after HIS OWN previous setting was 1", a same-side, lag-1, own-setting effect logged separately in
`SUPERPOSITION_NIST_20260930.md` / `THIRD_RUNG §29`) but is a DIFFERENT, cross-witness test (the FAR side's
setting, not the near side's own history) and is ~13x smaller. The Bob->Alice mirror direction produced no
cell above ratio 1.8 (not tabled above; full numbers in the CSV).

## 4. RUN vs RUN, all 170 cells

Verdict counts (pooled with between-run spread as the error, never within-run binomial alone):

| verdict | count |
|---|---|
| AGREE | 118 |
| UNSTABLE | 52 |
| STABLE DISAGREEMENT | 0 |

Zero cells are a STABLE DISAGREEMENT anywhere in this record: no lag, direction, or setting split has all 8
runs pointing the same nonzero way with each run individually outside the pooled value's error bars in a
consistent direction. Every non-AGREE cell is UNSTABLE (mixed sign, or same-sign but not matching a common
value within each run's own error) rather than a clean same-signed disagreement. By part: Part 1 89/41 (AGREE/
UNSTABLE), Part 2 12/8, Part 3 17/3.

## 5. Plain words

Is there any lag, direction, or setting split where the neighbors of a click read differently from the
neighbors of a non-click, beyond the between-run spread? **Two cells, out of 170, clear a pooled/between-run
ratio of 3.5**, both in Part 1 (cross-witness): a->b lag-5 split on Bob's setting (ratio 3.59) and b->a lag+5
split on Bob's setting (ratio 3.52) -- both AGREE across all 8 runs, both landing at the outer edge (+/-5
trials) of the neighborhood window, both involving the SAME setting variable (Bob's), both negative. A third
and fourth cell sit at ratio 3.36 (also lag+/-4, also setting-split, also AGREE). None of the 20 same-side
"null's own neighbor" cells (Part 2) or the 20 far-setting cells (Part 3) clears ratio 2.3. With 170 total
cells and correlated/nested tests (mirrored directions, overlapping lag groups, setting splits of the same
lag), a naive chance count at |ratio|>=3.5 would be well under 1; getting 2 is a lead, not a result -- it sits
at the far lags (4-5 trials, tens of microseconds away at 100 kHz), not the near ones, is not replicated at
the matching unsplit lag with the same strength (unsplit lag+/-5 sits at ratio ~3.0, still real but weaker),
and needs an independent record or a pre-declared re-check before it is anything more than the outer edge of
this table.

## LAGS TO 50

Extending the outer-edge lead: the two mirrored strongest cells from Part 1 (a->b lag-5 / b->a lag+5, both
split on Bob's setting = 1, ratio 3.59 / 3.52) run out to d in {-50..-1, +1..+50} on both directions,
unsplit AND on the winning split (Bob's setting at the earlier-in-pair time index -- `target_setting` for
a->b, `source_setting` for b->a). Streamed per run, same loader (`pipeline.load_run`), 8 runs, wall time
5,163 s (~86 min). Script: `parallax/out/superposition_nist/lags50.py`. Raw per-lag rows (4,800):
`lags50_raw.json`. Pooled per-lag cells (600): `lags50_lagtable.json`. Pooled band cells (36):
`lags50_bandtable.json`. Sign-symmetry rows (18): `lags50_signtable.json`.

**Tries:** 2 directions x 8 runs x 100 lags x (1 unsplit + 2 split values) = **4,800 raw per-lag rows**,
pooling to **600 run-vs-run lag cells**. Banding (|d| 1-5, 6-20, 21-50) x sign (before/after) x 2 directions
x 3 conditions (unsplit + 2 split values) = **36 pooled band cells**, giving **18 before-minus-after rows**.
Grand total this extension: **4,854 raw+pooled test rows**, on top of the 1,360 already logged.

### 1. Full profile, both directions, the winning split

Near the origin the profile matches Part 1 exactly (cross-checked bit-for-bit against `neighbors_raw.json`
at lag-5/target_setting for a->b: n1, n_total, p1, baseline, diff_pp, se_pp all identical). Sample, pooled
diff (pp) / between-run SE (pp) / ratio, a->b split on Bob's setting=1:

| lag | diff (pp) | SE (pp) | ratio | call |
|---|---|---|---|---|
| -1 | +0.00984 | 0.00359 | 2.74 | AGREE |
| -2 | -0.00741 | 0.00493 | 1.50 | AGREE |
| -3 | +0.00154 | 0.00535 | 0.29 | AGREE |
| -4 | -0.00576 | 0.00496 | 1.16 | UNSTABLE |
| **-5** | **-0.01083** | **0.00302** | **3.59** | **AGREE** |
| -6 | -0.00442 | 0.00281 | 1.58 | AGREE |
| -7 | +0.00088 | 0.00250 | 0.35 | AGREE |
| -8 | +0.00099 | 0.00336 | 0.29 | AGREE |
| -9 | +0.00175 | 0.00681 | 0.26 | UNSTABLE |
| -10 | +0.00167 | 0.00595 | 0.28 | UNSTABLE |
| -15 | +0.00242 | 0.00604 | 0.40 | UNSTABLE |
| -20 | -0.00102 | 0.00430 | 0.24 | UNSTABLE |
| -25 | -0.00567 | 0.00533 | 1.06 | AGREE |
| -30 | -0.00392 | 0.00534 | 0.73 | UNSTABLE |
| -40 | +0.00667 | 0.00575 | 1.16 | AGREE |
| -50 | -0.00173 | 0.00272 | 0.64 | AGREE |

Mirror, b->a split on Bob's setting=1 (positive lags), same pattern: lag+1 ratio 2.80, +2 1.51, +3 0.23,
+4 1.10, **+5 3.52 (AGREE)**, +6 1.59, +7 0.37, +8 0.33, +9 0.24, +10 0.27, and every sampled lag out to
+50 stays under ratio 1.2 with mixed sign. Full 600-cell table in `lags50_lagtable.json`.

### 2. Band read: spike, edge, or plateau?

Pooled band values (pp) with between-run SE, both winning-split directions:

| direction/split | sign | band 1-5 | band 6-20 | band 21-50 |
|---|---|---|---|---|
| a->b, target_setting=1 | before (neg) | -0.00252 +/- 0.00249 (ratio 1.01) | +0.00219 +/- 0.00099 (2.21, AGREE) | +0.00059 +/- 0.00091 (0.65, AGREE) |
| a->b, target_setting=1 | after (pos) | -0.00051 +/- 0.00152 (0.33) | +0.00020 +/- 0.00156 (0.13) | -0.00058 +/- 0.00109 (0.53) |
| b->a, source_setting=1 | before (neg) | -0.00024 +/- 0.00085 (0.28) | +0.00005 +/- 0.00094 (0.05) | -0.00032 +/- 0.00064 (0.51) |
| b->a, source_setting=1 | after (pos) | -0.00148 +/- 0.00144 (1.03) | +0.00126 +/- 0.00059 (2.15, AGREE) | +0.00038 +/- 0.00053 (0.71) |

Reading the profile lag-by-lag (not banded) settles the question directly: **it is a spike, not an edge or a
plateau**. lag-5 (and its mirror lag+5) sit at ratio ~3.5-3.6; the immediate neighbor lag-6/+6 drops to ratio
~1.6; by lag-7/+7 it is back to ratio <0.4; and every lag from 9 out to 50 (both directions, both signs)
stays under ratio ~1.2 with no consistent sign run. Once lag-5 is diluted into its own band (1-5, which
also holds -1..-4), the band-pooled ratio falls to ~1.0-1.03 -- the same dilution that made the earlier
"unsplit lag+/-5 ratio ~3.0 vs unsplit band weaker" note in Part 1. The profile does **not** keep climbing
past -5/+5 (rules out "edge of something longer"), and it is **not** a sustained few-lag band (rules out
"plateau") -- it is one isolated point in an otherwise flat, sign-mixed 100-lag profile out to 50 trials.
The one band that clears ratio 2 in either direction (a->b 6-20 before, AGREE at 2.21; b->a 6-20 after,
AGREE at 2.15) is 6-20 lags out, a DIFFERENT band from the lead, weaker, and not mirrored on the same side
in both directions -- not a replication of the -5/+5 finding, and not investigated further here (would need
its own pre-declared check).

### 3. Sign symmetry (before minus after), pooled by band

| direction/split | band | before (neg) pp | after (pos) pp | before-after (pp) | SE (pp) | ratio |
|---|---|---|---|---|---|---|
| a->b target_setting=1 | 1-5 | -0.00252 | -0.00051 | -0.00201 | 0.00292 | 0.69 |
| a->b target_setting=1 | 6-20 | +0.00219 | +0.00020 | +0.00199 | 0.00185 | 1.08 |
| a->b target_setting=1 | 21-50 | +0.00059 | -0.00058 | +0.00117 | 0.00141 | 0.82 |
| b->a source_setting=1 | 1-5 | -0.00024 | -0.00148 | +0.00124 | 0.00167 | 0.74 |
| b->a source_setting=1 | 6-20 | +0.00005 | +0.00126 | -0.00122 | 0.00111 | 1.10 |
| b->a source_setting=1 | 21-50 | +0.00059\* | +0.00038 | -0.00070 | 0.00083 | 0.84 |

(\*sign convention per direction; full 18-row table in `lags50_signtable.json`.) **Verdict: same, within
noise.** No band clears ratio 1.2 for before-vs-after; the before and after profiles are statistically
indistinguishable at the band level. The lag-5/lag+5 spike itself is, by construction, the mirror pairing
(a->b lag-5 IS the before-side read of the same b->a lag+5 after-side read at the same absolute lag
distance from a shared reference), so it does not independently test sign symmetry -- the two headline cells
are one relationship viewed from each side, not two.

### 4. Trial timing in microseconds

Trials run at 100 kHz (stated in `public_bell/README.md`, confirmed in NIST's own
`file_folder_descriptions.pdf`): **1 trial = 10 us**. Band edges: 1-5 lags = 10-50 us; 6-20 lags = 60-200 us;
21-50 lags = 210-500 us. The lag-5/lag+5 spike sits at **50 us** from the reference click. The NIST
documentation states two other timing numbers, neither of which was guessed: the GPS pulse-per-second
signal has "~10 ns jitter, but can have 100 ns jumps," and two of the eight runs (21_15, 22_20) were taken
with the Pockels-cell turn-on deliberately shifted by **200 ns** ("lightconeshift" adjustment) -- both are
orders of magnitude below the 10 us trial period and below the 50 us where the spike sits, so neither
documented scale offers a mechanical match to this lag. No other timing scale (a expected correlation
length, a known noise period, etc.) is stated in the README or the PDF; none is asserted here.

### 5. Plain words

Out to +/-50 trials (500 us), there is exactly one place where the far witness's record reads differently
from the between-run spread: **lag 5 trials before/after a click (50 us), on the split by Bob's own setting
at that lag, both mirrored directions, ratio ~3.5-3.6, AGREE across all 8 runs.** It is a genuine isolated
spike -- gone by the very next lag (ratio drops to ~1.6 at lag 6, ~0.3 by lag 7) and never returns anywhere
in the remaining 45 lags out to 50 (500 us) in either direction. Banding it in with its neighbors (as any of
the three band groupings does) dilutes it back to ratio ~1.0, which is why it never showed up as a "band"
result and only shows as a single-lag spike. The before (negative-lag) and after (positive-lag) profiles
are symmetric within error at the band level -- no directional (time-arrow) asymmetry beyond noise. This
extension does not turn the outer-edge lead into "the beginning of something longer" -- the 45 lags past it,
all the way to 500 us, are flat and sign-mixed. It also does not make the lead go away: one isolated,
AGREE-across-8-runs, ratio-3.5+ spike at a specific, non-arbitrary offset (50 us, the same offset in both
mirrored directions) sitting inside 600 lag cells of otherwise-noise is still a genuinely unusual single
point, just not one with company nearby. Needs an independent record or a pre-declared re-check, same as
Part 1 said.
