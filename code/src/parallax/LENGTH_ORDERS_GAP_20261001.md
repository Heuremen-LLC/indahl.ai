# LENGTH ORDERS THE GAP -- 2026-10-01, Bones's field hand

Wayfinder's prior reading (COPPER_800/GAP_PER_MEDIUM/NEURONS addenda): across six substrates,
clock-minus-split (G_s, series-taus) orders EXACTLY by record length in samples -- copper 800/-0.25,
fermentation 996/+1.45, chip 2150/+2.07, mouse 8192/+2.14, radio 15325/+2.70, neurons 271208/+3.70
(rho=+1.00, exact odds 1/720). Two readings were left open: (a) a medium property that happens to
scale with how long we recorded, or (b) the ruler -- a longer record always shows a bigger gap
because the autocorrelation clock's fitted tau (or the split's inside clock) grows with sample
count BY CONSTRUCTION, regardless of medium. This file settles it the only honest way: truncate the
SAME record to different lengths and see if the ordering reappears inside one substrate.

No expectation written before running. Script: `out/the_middle/length_orders_gap.py` (numpy only).
Raw output: `out/the_middle/length_orders_gap_results.json`. Frozen instruments reused verbatim, not
edited: `core.py` (arrow_stat/arrow_best_k_fast/fit_exp_decay/bootstrap_tau_fast/split_fit/
split_bootstrap_fast/hilbert_envelope), `split_v2.py` (naive_peaks_idx/candidate_c),
`calibrated_standoff.py` (K_of_relerr/series_taus, SAME frozen K_TAU=0.053767). The clock recipe is
NEURONS_20261001.md Sec3's exact one (autocorrelation -> Hilbert envelope -> exp-decay fit), here
computed via a zero-padded FFT (Wiener-Khinchin) instead of `np.correlate(...,'full')` so it stays
tractable at n=271,208+ -- confirmed to give the identical autocorrelation values, not a new
statistic. The only genuinely new code: the segmenter, the per-segment measure/convert/gap loop,
and the slope/units/inside-clock arithmetic on top.

## 0. Records and segmentation

Four records, nested-prefix truncation at lengths {800, 2000, 8000, 15000, 50000, 271000},
**wherever the record allows**, up to **three disjoint, sequential, non-overlapping segments** per
length (`n_segs = min(3, floor(n_total/L))`); fewer when the record doesn't allow 3, reported not
padded:

| substrate | source | n_total | dt (native) |
|---|---|---|---|
| neurons | culture 1-1, day 25 (bursting), 10ms population-rate bins | 271,208 | 0.010 s |
| radio | horn, 4080MHz band power, whole record | 29,226 | 0.330 s |
| mouse | SC10.2 body temperature (size-1) | 8,192 | 0.25 h |
| yeast (short control) | NADH whole record, digitized | 1,531 | 1.31 s |

Lengths available per record: neurons gets all six (271,000 as 1 segment); radio gets 800/2000/8000
(3 segments each) + 15,000 (1 segment only, floor(29226/15000)=1); mouse gets 800/2000 (3 segments
requested, 2 resolved -- see failed rows) + 8000 requested but its 1 segment's clock fit failed
(OPEN); yeast gets only 800 (1 segment, record too short for anything else -- confirms it as the
short control, not a 5th truncation substrate).

## 1. TRUNCATION TABLE -- G_s (clock-minus-split, series-taus) vs length, per substrate

Pooled (weighted mean + chi-square) across the resolved disjoint segments at each length:

| substrate | n | G_s (pooled) | err | n_segs resolved | reduced chi2 |
|---|---|---|---|---|---|
| **neurons** | 800 | +0.761 | 0.819 | 3/3 | 0.12 |
| neurons | 2,000 | +1.635 | 0.615 | 3/3 | 2.05 |
| neurons | 8,000 | +3.354 | 0.630 | 3/3 | 0.13 |
| neurons | 15,000 | +3.304 | 0.626 | 3/3 | 0.25 |
| neurons | 50,000 | +3.214 | 0.639 | 3/3 | 0.03 |
| neurons | 271,000 | +3.797 | 1.169 | 1/1 | -- |
| **radio** | 800 | -0.024 | 1.134 | 2/3 (1 clock fit failed) | 0.16 |
| radio | 2,000 | +1.566 | 0.822 | 3/3 | 3.16 |
| radio | 8,000 | +3.916 | 0.683 | 3/3 | 0.04 |
| radio | 15,000 | +3.422 | 1.076 | 1/1 | -- |
| **mouse** | 800 | +0.372 | 0.360 | 2/3 (1 clock fit failed) | 0.30 |
| mouse | 2,000 | -0.189 | 1.160 | 2/3 (1 clock fit failed) | 0.02 |
| mouse | 8,000 | OPEN | -- | 0/1 (clock fit failed, non-finite tau) | -- |
| **yeast (control)** | 800 | +2.903 | 0.717 | 1/1 | -- |

**Read off the table directly: neurons and radio BOTH climb with length inside their own single
record** -- neurons runs +0.76 -> +1.64 -> +3.35 -> +3.30 -> +3.21 -> +3.80 as n goes 800 ->
271,000 (rising then flattening past ~8,000); radio runs -0.02 -> +1.57 -> +3.92 -> +3.42 over the
same length range it has available. **This is the same shape the six-substrate table showed**,
reproduced on ONE record each. Mouse's own truncation is too thin to read (only 2-of-3 segments
resolved at each of its two usable lengths, and its longest length failed outright) -- consistent
with noise, not evidence against the pattern. Yeast, the short control, has only one point by
construction (record too short to truncate further) -- it cannot test anything, but its single
point (+2.90 at n=800) sits well above neurons' and radio's own n=800 points (+0.76, -0.02), a
reminder that **medium identity still matters at fixed length even if length also matters within a
medium** -- the two readings are not mutually exclusive.

## 2. THE CROSS-SUBSTRATE LINE vs THE WITHIN-SUBSTRATE LINE

Weighted least squares, G_s = a + b*log10(n), weights = 1/err²:

**Across** (the six published substrate-level G_s numbers, copied verbatim: copper
GAP_PER_MEDIUM/COPPER_800, fermentation/chip/mouse/radio GAP_PER_MEDIUM Sec1, neurons NEURONS Sec4):

| | b | b_err | n points | reduced chi2 |
|---|---|---|---|---|
| **b_across** | **+1.060** | **0.336** | 6 | 1.28 |

**Within** (this pass's own pooled truncation points, per substrate):

| substrate | b_within | b_within_err | n points | reduced chi2 |
|---|---|---|---|---|
| **neurons** | **+1.238** | **0.413** | 6 | 0.78 |
| **radio** | **+3.182** | **1.006** | 4 | 0.61 |
| mouse | -1.409 | 3.053 | 2 (0 dof -- unconstrained) | -- |
| yeast | OPEN -- 1 point, no slope fittable | -- | 1 | -- |

**Calls** (diff vs combined error; STABLE DISAGREEMENT requires same-direction evidence across more
than one pairing, per the standing rule -- checked below):

| substrate | diff (b_within - b_across) | combined err | call |
|---|---|---|---|
| neurons | 0.178 | 0.533 | **AGREE** |
| radio | 2.122 | 1.056 | DIFFERS beyond combined error (diff/err = 2.01) -> both resolvable b_within values (neurons, radio) share b_across's sign (positive) -> **STABLE DISAGREEMENT**, not UNSTABLE |
| mouse | 2.469 | 3.070 | AGREE (errs too wide to say anything -- OPEN in practice) |
| yeast | -- | -- | OPEN |

**Read: b_within is NOT zero on either substrate that could be measured** (neurons +1.24±0.41,
radio +3.18±1.01, both >2 sigma from zero) **and both sit on the SAME side of zero as b_across
(+1.06±0.34)** -- radio's own within-record slope is in fact STEEPER than the across-substrate one,
not flatter. This is the opposite of what "the medium carries it, length does not act within a
record" would predict (that reading needs b_within consistent with 0). **Length orders the gap
within a single record, not just across different media** -- the honest call is that the
across-substrate ordering is AT LEAST PARTLY a ruler effect, confirmed on two of the two substrates
long enough to test it this way.

## 3. UNITS CHECK -- does the exact ordering survive length in beats or in seconds?

Beat period (native units) and sample interval, read from GAP_PER_MEDIUM Sec3 for fermentation/
chip/mouse/radio; copper's dt from `copper_lines_800.json`'s own median sample spacing (~60.0s) and
its own flagged lag-5-sample period (COPPER_800's only significant cell); neurons' period from THIS
pass's own full-record (n=271,208) arrow best-k (k=9 samples, i.e. a 0.09s native period) -- the
only new per-record quantity computed in this section, everything else is a citation.

| substrate | n (samples, the claim's order) | n in **beats** | n in **seconds** |
|---|---|---|---|
| copper | 800 | 160.0 | 48,000 |
| fermentation | 995.5 | 25.9 | 1,304.1 |
| chip | 2,149.7 | 25.9 | 1,343.6 (MIXED UNITS, flagged in GAP_PER_MEDIUM too) |
| mouse | 8,192.0 | 199.8 | 7,372,800 |
| radio | 15,324.5 | 199.1 | 5,057.1 |
| neurons | 271,208.0 | 38,744.0 | 2,712.1 |

Exact permutation test, n=6 (720 orderings), Spearman rho of each unit's ordering against the
sample-count order that produced rho=+1.00 (2/720 is the floor for a perfect match at n=6):

| unit | rho vs sample-count order | exact fraction (of 720) |
|---|---|---|
| beats | +0.771 | 74/720 = 0.103 |
| seconds | +0.086 | 662/720 = 0.919 |

**Neither physical unit reproduces the exact ordering.** Beats comes closer (rho=0.77, still a long
way from the 2/720 floor a true physical-length effect would need) because mouse and radio land
almost on top of each other (199.8 vs 199.1 beats) and neurons' huge beat count still sorts last;
seconds is essentially uncorrelated (rho=0.09, fraction 0.92 -- a coin flip) because mouse's 0.25h
bins turn its modest sample count into the LARGEST real-time span of all six substrates (7.4 million
seconds = 85 days), completely out of step with its G_s rank. **The ordering that is "exact" (1/720)
lives specifically in raw sample count, not in any physically meaningful length (cycles elapsed or
wall-clock time elapsed).** That is itself the clearest single piece of evidence for the ruler
reading: a genuine medium/wave-speed effect would be expected to track a physical length, not an
analysis parameter (how many numbers happen to sit in the file).

## 4. THE SPLIT'S INSIDE CLOCK ALONE

`candidate_c`'s "inside time" is `cumsum((|x|/mean|x|) * dt)` -- by construction its total range is
very close to `n * dt` whenever the amplitude-weight averages near 1 over the record (which it does
for every stationary-ish substrate here). Measured directly, slope of total inside-time vs n (plain
OLS across this pass's own truncation segments) against each record's own dt:

| substrate | slope (inside-time vs n) | dt (native) | ratio slope/dt |
|---|---|---|---|
| neurons | 0.0100000 | 0.0100000 | 1.0000 |
| radio | 0.3299974 | 0.3300002 | 0.99999 |
| mouse | 0.2499841 | 0.2500000 | 0.99994 |
| yeast | OPEN (1 point, no slope fittable) | 1.31 | -- |

**The inside clock's growth rate equals the sample interval to 4-5 significant figures, on every
substrate tested.** This is not a property of the medium at all: the energy-weighted "inside time"
is, to within rounding, just elapsed wall-clock time, so its TOTAL RANGE is `n * dt` by algebra, for
any record, in any substrate, regardless of what is actually happening inside it. **The split's own
clock inherits a pure length dependence from its construction, with a number: slope/dt = 1.000
±0.0001 across all three substrates measured.** Whatever genuine medium signal exists in P (the
split's slope coefficient) rides on top of an inside-time axis whose total span is fixed by n and dt
alone -- length is baked into the ruler here, explicitly, not inferred.

## 5. Plain words

**Is "length orders the gap" a ruler, a medium property, or both?** Both, with the ruler now shown
directly, not just inferred. **It is a ruler**: (1) truncating a SINGLE record (neurons, radio)
reproduces the same positive, length-correlated climb in G_s that the six-substrate table showed --
b_within = +1.24±0.41 (neurons) and +3.18±1.01 (radio), both clearly nonzero and both the same sign
as the across-substrate slope (+1.06±0.34); neurons' own within-slope statistically AGREES with the
across-substrate slope, and radio's, while nominally a STABLE DISAGREEMENT (steeper, not flatter),
is on the SAME side of zero, not the opposite one a pure "medium only" reading would need. (2) The
exact 1-in-720 ordering lives specifically in raw sample count: converting to beats drops the match
to 74/720, converting to seconds drops it to 662/720 (indistinguishable from chance) -- a genuine
medium/wave-speed property should survive in a physical unit; this one does not. (3) The split's own
inside-time construction grows with slope = dt to 4 decimal places, meaning part of what the gap is
built from is wall-clock elapsed time by algebra, not a measurement of anything medium-specific.

**It may ALSO be partly a medium property**: at matched n=800, yeast's G_s (+2.90±0.72) sits well
above neurons' (+0.76±0.82) and radio's (-0.02±1.13) own n=800 points -- medium identity still
separates records at fixed length, so collapsing everything to "it's only the ruler" would overclaim
in the other direction. **The honest reading: the six-substrate exact ordering is NOT primarily a
property of the medium that happens to correlate with how long we recorded it -- the within-record
truncation shows the SAME growth happens on a fixed medium just by looking at more of it, and the
growth's unit-dependence (sample count only, not beats, not seconds) and the split's own
construction both point at the ruler as the dominant mechanism.** Not fully solved: mouse's own
truncation is too thin (clock fits failed on 3 of 6 attempted segments/lengths) to add a third
within-record confirmation, and the within-substrate slopes themselves disagree with each other
(1.24 vs 3.18) enough that "the" within-record slope is not yet one number -- a seventh substrate or
a cleaner mouse record would settle how steep the ruler effect actually is, not whether it exists.

## Failed rows

9 failed cells, all logged, none dropped silently: radio length-800 segment (1600,2400) clock fit
non-finite; radio lengths 50,000 and 271,000 unavailable (record too short, n_total=29,226); mouse
length-800 segment (1600,2400) and length-2000 segment (4000,6000) clock fits non-finite; mouse
length-8000's only segment clock fit non-finite (OPEN cell, no G_s/G_a at that length); mouse
lengths 15,000/50,000/271,000 unavailable (n_total=8,192); yeast lengths 2,000/8,000/15,000/50,000/
271,000 unavailable (n_total=1,531, by design the short control).

## Tries

**Measurement pass:** 34 segment-computations (16 neurons + 10 radio + 7 mouse + 1 yeast) x 3
formulas (arrow, clock, split) each attempted once; arrow = 100-shuffle floor per k x up to 29 k's
searched (`arrow_best_k_fast`, vectorized) + 300-draw bootstrap; clock = FFT-based autocorrelation +
Hilbert envelope + exp-decay fit + 300-draw `bootstrap_tau_fast`; split = `naive_peaks_idx` +
`candidate_c` + 300-draw `split_bootstrap_fast`. Counted by the script's own counters: **98,600
shuffle draws, 29,400 bootstrap draws**. Every resolved (clock, arrow) and (clock, split) pair
converted through the frozen K(rel_err) map at 20,000 Monte Carlo draws each (reduced from the
frozen instrument's default 200,000 to keep 34 segments x up to 3 quantities tractable in one pass,
stated not hidden): **1,960,000 MC propagation draws**. 11 pooled weighted-mean/chi-square cells (one
per resolved substrate x length). 4 weighted log-log slope fits (within-substrate) + 1 across-
substrate slope fit (6 points, cited not refit). 2 exact permutation tests (beats, seconds), n=6,
**1,440 total orderings enumerated** (720 each), zero asymptotic p-values. 3 inside-clock-growth OLS
fits (neurons, radio, mouse; yeast open). **Grand total this pass: 98,600 shuffles + 29,400
bootstraps + 1,960,000 MC draws + 1,440 exact permutations enumerated. Runtime 8.4 s, single
process.**

## Files

- Report: `~/bones-forge/parallax/LENGTH_ORDERS_GAP_20261001.md` (this file)
- New script: `parallax/out/the_middle/length_orders_gap.py` (numpy only)
- New raw output: `parallax/out/the_middle/length_orders_gap_results.json`
- Run log: `parallax/out/the_middle/run_log_length_orders.txt`
- Reused, unedited: `parallax/out/three_on_three/core.py`, `parallax/out/yeast/three/split_v2.py`,
  `parallax/out/the_middle/calibrated_standoff.py` (K_of_relerr/series_taus/K_TAU/propagate,
  imported verbatim), `parallax/out/three_on_three/load_horn.py`
- Raw data read directly: `parallax/out/neurons/raw/1-1-25.spk.txt` (bursting day, culture 1-1),
  `parallax/out/three_on_three/horn_4080_pull.csv` (via load_horn), `parallax/out/dryad_sweep/
  mice_social_sync/Body Temperature files/SC10.2 255041 11.26.08.txt`, `parallax/out/yeast/
  nadh_fig4_raw_digitized.csv`
- Cited for the across-substrate line and the units-check period/dt columns, not recomputed:
  `GAP_PER_MEDIUM_20261001.md` Sec3, `COPPER_800_20260930.md` Sec3b, `NEURONS_20261001.md` Sec4,
  `parallax/out/copper_nodes/data/copper_lines_800.json` (dt only)
