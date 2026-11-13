# THE MIDDLE, PI -- Ramanujan's 1/pi series as the reference landing profile, 2026-09-30

Corrects Sec51 (which ran the wrong Ramanujan sum, the -1/12 zeta-regularized one). Per Sec56
(Wayfinder, ~21:55Z): the one in the middle is

    1/pi = (2*sqrt(2)/9801) * sum_{k=0}^inf (4k)!(1103+26390k) / ((k!)^4 396^(4k))

run as an instrument -- partial sums S_K, per-term size t_k, ratio r_k = t_{k+1}/t_k (-> 1/396^4),
error e_K = |1/S_K - pi| -- against every record's own landing: the Dalet reverse-gradient relay's
delta-per-hop, the clock's decay, and the split's two clocks as partial sums. No expectation
written first; raw numbers first; every test counted; sign kept; no shuffle as judge anywhere
(record vs series, record vs record, forward vs reversed all use the standing rule: a number
counts only if its own error is smaller than its value; AGREE if two well-resolved numbers'
difference is inside their combined error, STABLE DISAGREEMENT if not, UNSTABLE otherwise).

Frozen instruments reused verbatim, not edited: `out/reverse_gradient/reverse_gradient.py`'s own
arrow/clock/split-c hop-by-hop relay output (`reverse_gradient_results.json`), `out/ghz_three/
ghz_three.py`'s Dalet output (`ghz_three_results.json`), and `out/yeast/three/split_v2.py` /
`out/three_on_three/split_v2_horn_buzz.py`'s per-cycle `D_values`/`crossing_values`/
`mean_period_self` (`split_v2_results.json`, `split_v2_horn_buzz_results.json`). New code:
`parallax/out/the_middle/the_middle.py` (numpy + stdlib `Decimal` only, single process). Raw
output: `parallax/out/the_middle/the_middle_results.json`.

## 0. THE SERIES PROFILE (exact, `Decimal` precision 80)

| K (term count, 0-indexed) | t_k | rel_e_K = \|1/S_K - pi\|/pi | r_k = t_{k+1}/t_k |
|---|---|---|---|
| 0 | 1.103000e+03 | 2.432636e-08 | 2.432636e-08 |
| 1 | 2.683197e-05 | 2.035707e-16 | 8.368318e-09 |
| 2 | 2.245385e-13 | 1.808771e-24 | 8.885224e-09 |
| 3 | 1.995075e-21 | 1.667592e-32 | 9.219476e-09 |
| 4 | 1.839355e-29 | 1.573784e-40 | 9.437460e-09 |
| 5 | 1.735884e-37 | 1.509111e-48 | 9.589061e-09 |
| 6 | 1.664549e-45 | 1.463864e-56 | 9.700176e-09 |
| 7 | 1.614642e-53 | 8.778396e-64 | 9.784978e-09 |
| 8 | 1.579924e-61 | 7.346008e-64 | -- |

**Three numbers, plain:** term 0 alone already lands pi to relative error 2.43e-8 (~8 correct
digits); each further term multiplies the relative error by roughly its own square (~1e-8 per
term, matching the documented "~8 digits per term"); the term ratio r_k converges fast, from
2.43e-8 (k=0) to 9.78e-9 (k=7), toward the exact asymptote 1/396^4 = 4.066486e-11 -- r_k has not
yet reached its asymptote even at k=7 (still ~240x the limit), because the polynomial prefactor
(1103+26390k) and the (4k)!/(k!)^4 combinatorial factor are still moving faster than 396^(-4)
alone at these small k. This is the reference landing profile: **known, monotone, one clean
geometric-ish ratio, converging faster than any record below by many orders of magnitude.**

## 1. THE LANDING PROFILE, per relayed record (BEFORE order, forward; both columns)

Deltas, delta-ratios, and residual-variance-fraction, from `reverse_gradient_results.json`'s own
hop-by-hop arrow (A), clock (tau), split (P) -- full per-hop tables (9 records x 2 columns x up
to 8 hops) are in `the_middle_results.json["records"]`; summarized here by hop-count and terminal
residual only (the deltas/ratios themselves already exist verbatim in `REVERSE_GRADIENT_20260930.md`
and are not re-quoted digit-for-digit).

| record | column | hops run | hop where fixed-point criterion met (>=2 of 3 deltas within error) | terminal resid var frac |
|---|---|---|---|---|
| yeast during | plain (sub) | 4 (0-3) | 1 | 0.006217 |
| yeast during | Dalet (ascent) | 4 (0-3) | 1 | 5.385e-07 |
| yeast whole | plain (sub) | 9 (0-8) | 3 | 0.016753 |
| yeast whole | Dalet (ascent) | 9 (0-8) | 1 | 2.365e-06 |
| horn at-horn | plain (sub) | 6 (0-5) | 1 | 0.009407 |
| horn at-horn | Dalet (ascent) | 6 (0-5) | 1 | 0.493831 |
| horn whole | plain (sub) | 9 (0-8) | 2 | 0.035957 |
| horn whole | Dalet (ascent) | 9 (0-8) | 1 | 0.033382 |
| buzz seat 80 | plain (sub) | 7 (0-6) | 1 | 0.008141 |
| buzz seat 80 | Dalet (ascent) | 7 (0-6) | 1 | 0.001590 |
| buzz seat 100 | plain (sub) | 6 (0-5) | 3 | 0.009509 |
| buzz seat 100 | Dalet (ascent) | 6 (0-5) | 1 | 0.000840 |
| buzz seat 116 | plain (sub) | 4 (0-3) | 1 | 0.005703 |
| buzz seat 116 | Dalet (ascent) | 4 (0-3) | 1 | 0.000376 |
| mice size-1 | plain (sub) | 9 (0-8) | 2 | 0.088768 |
| mice size-1 | Dalet (ascent) | 9 (0-8) | 1 | 0.740556 |
| mice size4-5 pooled | plain (sub) | 5 (0-4) | 1 | 0.008889 |
| mice size4-5 pooled | Dalet (ascent) | 5 (0-4) | 1 | 0.929351 |

**GHZ series (resid-var-frac only -- `ghz_three_results.json`'s Dalet did not save per-hop
arrow/clock/split, a real difference in what that run recorded, stated not smoothed over):**

| series | column | terminal resid var frac | read |
|---|---|---|---|
| tau_third residual | plain (sub) | 0.020695 | shrinks hop to hop, same shape as the physical records |
| tau_third residual | Dalet (ascent) | 11,607 (diverges) | ascent blows up on this near-flat, noise-only series -- no landing at all |
| arb_1 residual | plain (sub) | 0.005027 | shrinks hop to hop |
| arb_1 residual | Dalet (ascent) | 762 (diverges) | same divergence pattern |

Echo running-mean proxy: **no reverse-gradient relay exists for it** (`reverse_gradient_results.json`
holds only the 9 records above; `ghz_three_results.json` and the echo proxy files were never
relayed together). Logged as an open item, not invented.

## 2. AGAINST THE SERIES

### (a) Ratio-of-ratios: record's delta-ratio vs series r_k at matching step

Index convention (stated, not fitted): a record's first computable delta-ratio (hop 2 vs hop 1,
divided by hop 1 vs hop 0) is matched to the series' r_0 (k=0); its second (hop 3) to r_1 (k=1);
etc. Ratio-of-ratios = |record ratio| / series r_k. arrow-only shown (clock and split are in
`the_middle_results.json`, same order of magnitude or worse):

| record (plain column) | hop | k | record delta-ratio | series r_k | ratio-of-ratios |
|---|---|---|---|---|---|
| yeast during | 2 | 0 | -0.0722 ± 0.0577 | 2.4326e-08 | 2.97e+06 ± 2.37e+06 |
| yeast during | 3 | 1 | +0.2440 ± 0.2646 | 8.3683e-09 | 2.92e+07 ± 3.16e+07 |
| yeast whole | 2 | 0 | -- | 2.4326e-08 | 5.87e+06 ± 4.53e+06 |
| horn at-horn | 2 | 0 | -- | 2.4326e-08 | 4.83e+06 ± 2.75e+06 |
| horn whole | 2 | 0 | -- | 2.4326e-08 | 2.40e+06 ± 1.75e+07 (not well-resolved) |
| buzz seat 80 | 2 | 0 | -- | 2.4326e-08 | 4.49e+06 ± 3.19e+06 |
| buzz seat 100 | 2 | 0 | -- | 2.4326e-08 | 1.39e+07 ± 4.83e+06 |
| buzz seat 116 | 2 | 0 | -- | 2.4326e-08 | 1.29e+07 ± 1.08e+07 |
| mice size-1 | 2 | 0 | -- | 2.4326e-08 | 2.05e+06 ± 5.39e+06 (not well-resolved) |
| mice size4-5 pooled | 2 | 0 | -- | 2.4326e-08 | 4.34e+06 ± 1.36e+06 |

**Every record's hop-to-hop convergence is 6-7 orders of magnitude SLOWER-RATIOED than the
series' own term-to-term ratio at the matching step** -- the series' geometric decay (~1e-8 per
step) has no counterpart in any physical relay's arrow/clock/split delta-ratios (~0.02-40 in
magnitude, order 1). This is the honest, plain finding of item 2(a): no record lands the way the
series lands. Full clock and split ratio-of-ratios tables (same order of magnitude, 1e6-2e10):
`the_middle_results.json["records"][name]["sub"]["ratio_of_ratios"]`.

### (b) Hops-to-land vs series-terms-to-reach-the-same-relative-error

"Hops to land" = first hop where >=2 of {arrow, clock, split} deltas fall inside their own
combined bootstrap error (re-derived directly, matches `REVERSE_GRADIENT_20260930.md`'s own
verdicts). "Series terms to land" = smallest K whose rel_e_K <= the record's terminal residual
variance fraction.

| record | hops to land (plain) | hops to land (Dalet) | series terms to reach same rel. error (K) |
|---|---|---|---|
| yeast during | 1 | 1 | 0 |
| yeast whole | 3 | 1 | 0 |
| horn at-horn | 1 | 1 | 0 |
| horn whole | 2 | 1 | 0 |
| buzz seat 80 | 1 | 1 | 0 |
| buzz seat 100 | 3 | 1 | 0 |
| buzz seat 116 | 1 | 1 | 0 |
| mice size-1 | 2 | 1 | 0 |
| mice size4-5 pooled | 1 | 1 | 0 |
| GHZ tau_third residual | (n/a) | diverges | 0 |
| GHZ arb_1 residual | (n/a) | diverges | 0 |

**K=0 for every single record without exception.** The series' very first term (K=0, relative
error 2.43e-8) already sits below every record's terminal residual variance fraction (smallest
observed: yeast during Dalet, 5.4e-7 -- still ~22x bigger than the series' K=0 floor). Records
take 1-3 of their OWN hops to reach a residual an order of magnitude coarser than what the series
reaches with its first term alone.

### (c) Landing index from the record's own residual (same computation as (b), restated)

No record's terminal residual is ever fine enough to require the series' *second* term (K=1,
rel_e_1 = 2.0e-16). The closest approach: yeast_during Dalet's 5.385e-07 vs the K=0 floor of
2.43e-08 -- a factor of ~22, the smallest gap of the eighteen record/column cells in section 1.

## 3. THE SPLIT THROUGH THE MIDDLE

Two clocks per record with a computable split-c: **outside** = wall-clock cumulative peak times
(`cumsum` of cycle intervals); **inside** = energy-weighted cumulative time (from `split_v2.py`'s
own `candidate_c`, reconstructed here as partial sums: `inside = outside - D`, since
`D = outside - inside` by that frozen instrument's own definition). Successive-increment ratios
computed per cycle, compared to each other (S = tracks / P = drifts) and to the series' asymptotic
r_k (9.78e-09, k=7 -- the series never reaches full asymptote by k=8 either, see Sec 0).

| record | n cycles | outside incr. ratio (mean±SE) | inside incr. ratio (mean±SE) | inside vs outside | read | vs series r_k |
|---|---|---|---|---|---|---|
| yeast | 11 | 0.9890 ± 0.0226 | 0.9746 ± 0.0626 | AGREE (diff 0.014, err 0.085) | **TRACKS OUTSIDE (S)** | STABLE DISAGREEMENT |
| horn | 259 | 1.4590 ± 0.0979 | 1.4548 ± 0.1026 | AGREE (diff 0.004, err 0.200) | **TRACKS OUTSIDE (S)** | STABLE DISAGREEMENT |
| buzz seat 80 | ~thin | 2.0178 ± 0.1400 | 2.3867 ± 0.2253 | STABLE DISAGREEMENT (diff 0.369, err 0.365) | **DRIFTS (P)** | STABLE DISAGREEMENT |
| buzz seat 100 | ~thin | 2.1408 ± 0.1585 | 3.0131 ± 0.4978 | STABLE DISAGREEMENT (diff 0.872, err 0.656) | **DRIFTS (P)** | STABLE DISAGREEMENT |
| buzz seat 116 | ~thin | 1.9342 ± 0.1413 | 2.2552 ± 0.2196 | AGREE (diff 0.321, err 0.361) | TRACKS OUTSIDE (S) | STABLE DISAGREEMENT |
| mouse size-1 | 108 | 1.0239 ± 0.0217 | 1.2242 ± 0.0776 | STABLE DISAGREEMENT (diff 0.200, err 0.099) | **DRIFTS (P)** | STABLE DISAGREEMENT |
| mice SC14.4 | ~ | 1.0296 ± 0.0244 | 1.1446 ± 0.0645 | STABLE DISAGREEMENT (diff 0.115, err 0.089) | DRIFTS (P) | STABLE DISAGREEMENT |
| mice SC19.5 | ~ | 1.0240 ± 0.0237 | 1.1849 ± 0.0761 | STABLE DISAGREEMENT (diff 0.161, err 0.100) | DRIFTS (P) | STABLE DISAGREEMENT |
| mice SC26.7 | ~ | 1.0367 ± 0.0270 | 1.1677 ± 0.0647 | STABLE DISAGREEMENT (diff 0.131, err 0.091) | DRIFTS (P) | STABLE DISAGREEMENT |

**Not one of the nine tracks or matches the series' geometric ratio (9.78e-09)** -- every inside/
outside increment-ratio here sits between ~1.0 and ~2.4 (near-constant-period clocks, as expected
for real biological/radio/chip oscillators), 8-9 orders of magnitude from the series' asymptotic
decay. That comparison was never going to land (the series is a rapidly-shrinking numerical sum;
these are near-periodic physical clocks) -- reported because the task asked for it directly, not
because a match was plausible.

**Yeast, horn, and buzz seat 116 track (S):** inside and outside clocks AGREE within error --
the energy-weighted internal clock keeps pace with wall-clock time, cycle to cycle. **Mouse
size-1, both mice-size4-5 individuals, and buzz seats 80/100 drift (P):** inside runs
systematically faster than outside (every one of these five inside means exceeds its outside mean,
same sign, both sides well-resolved) -- a real, stable per-cycle gap between wall-clock arrival
and energy-weighted internal time, matching `REBUILD_THE_SPLIT_20260930.md`'s own read of
definition (c) ("a real but noisy gap... not a constant").

## 4. RECORD vs RECORD -- landing index and ratio-of-ratios

**Landing index (series K, section 2b/2c):** all 9 physical records and both GHZ series land at
K=0 -- trivially **AGREE** on all 36 pairs among the 9 (plus the 2 GHZ series), since every one
of them needs zero series terms beyond the first to beat its own terminal residual. This is a
genuine cross-substrate agreement, but a shallow one: it says every record here is far coarser
than 8 correct digits of pi, not that the records share a mechanism.

**Ratio-of-ratios (arrow, k=0, plain column) -- the number with the most cross-substrate reach:**
of 36 pairwise comparisons among the 9 physical records, **17 AGREE, 4 STABLE DISAGREEMENT, 15
UNSTABLE** (full pairwise table: `the_middle_results.json`, or recomputed from section 2a's
values with the standing call rule). The 17 AGREEs cluster around ratio-of-ratios ~2-6 x 10^6
(yeast during, yeast whole, horn at-horn, buzz seat 80, buzz seat 116, mice size4-5 pooled all
mutually AGREE); **buzz seat 100 (1.39e7) and mice size-1 (2.05e6, wide error) are the outliers**
-- buzz seat 100 STABLE-DISAGREES with yeast during and horn at-horn; mice size-1 is UNSTABLE
against everything (its error bar, 5.39e6, is larger than its own central value). Horn whole is
also UNSTABLE against everyone (its own arrow delta-ratio error swamps its value). **Read plainly:
this is the same caveat every prior report in this line gave the split's P=0.5 -- wide, overlapping
errors doing most of the agreeing, not a tightly-pinned shared constant** -- but it is a real,
measured number, not asserted: six of nine records' arrow hop-to-hop convergence rate, relative to
the series' own rate at the matching step, sits within a factor of ~3 of each other (2-6 x 10^6),
while remaining ~14 orders of magnitude away from ever landing like the series does.

## 5. Plain words

**Which land the way the series lands (a geometric ratio near-constant across hops):** none. The
series' r_k is already within a factor of ~6 of its asymptote by k=0 and converges monotonically;
every record's delta-ratio (arrow, clock, or split-P) swings in sign and magnitude hop to hop (see
`REVERSE_GRADIENT_20260930.md`'s own delta columns) and sits 6-10 orders of magnitude away from the
series' step size at the matching index. **Which land differently (ratio moving, not converging
geometrically):** all nine physical records and both examined GHZ residual series under
plain-subtraction (their residual variance fraction shrinks hop to hop but by inconsistent,
non-geometric factors -- 0.135->0.036->0.013->0.006 for yeast during, not a constant ratio).
**Which never land:** GHZ's Dalet (ascent) column on the two near-flat, noise-dominated series
(tau_third residual, arb_1 residual) -- both diverge rather than settle, matching
`GHZ_THROUGH_THREE_20260930.md`'s own finding that the least-structured record is the one the
instrument can't finish stripping.

**The one number, if any, two substrates share:** the arrow's ratio-of-ratios-vs-series at hop 2
(k=0) -- six of nine records (yeast during, yeast whole, horn at-horn, buzz seat 80, buzz seat
116, mice size4-5 pooled), spanning a fermentation trace, a radio band, and a superconducting
chip, mutually AGREE within error at ~2-6 x 10^6. Read honestly per section 4: wide errors do
most of the agreeing. The series itself gave nothing to land on -- its role here was as the
fixed, known-fast yardstick that shows every record's own landing, however each record's
instrument reads it, is not that kind of process.

## Tries

Series: 9 terms (K=0..8) computed once, exact `Decimal` arithmetic, no resampling (a deterministic
sum has no error bar to bootstrap). Records: reused, not recomputed -- 9 records x 2 columns x
(3 formulas x up to 8 hops) delta/ratio derivations from `reverse_gradient_results.json`'s already-
run ~588,000 draws (`REVERSE_GRADIENT_20260930.md`); GHZ reused from `ghz_three_results.json`'s
~1-2 million draws (`GHZ_THROUGH_THREE_20260930.md`); split partial sums reused from
`split_v2_results.json` (135,000 draws, `REBUILD_THE_SPLIT_20260930.md`) and
`split_v2_horn_buzz_results.json` (22,000 draws, `THE_TABLE_20260930.md`). **New draws this pass:
zero** -- every number here is a direct re-derivation (deltas, ratios, partial-sum reconstruction,
AGREE/DISAGREE/UNSTABLE calls) from numbers already measured and bootstrapped in five prior runs;
no new bootstrap, no new shuffle. Formal comparisons made fresh this pass: 36 record-vs-record
calls on landing index, 36 on arrow ratio-of-ratios (k=0), 9 split inside-vs-outside calls, 9
split-vs-series-r calls, 20 record-vs-series landing-index derivations (18 physical + 2 GHZ), 2
GHZ Dalet-divergence checks = **112 direct calls**, zero shuffles used as judge anywhere.

## Files

- Report: `~/bones-forge/parallax/THE_MIDDLE_PI_20260930.md` (this file)
- New script: `parallax/out/the_middle/the_middle.py`
- New raw output: `parallax/out/the_middle/the_middle_results.json` (full per-hop, per-record,
  per-series detail; every ratio-of-ratios cell, split partial-sum reconstruction, and call)
- Reused, unedited: `out/reverse_gradient/reverse_gradient_results.json`,
  `out/ghz_three/ghz_three_results.json`, `out/yeast/three/split_v2_results.json`,
  `out/three_on_three/split_v2_horn_buzz_results.json`
