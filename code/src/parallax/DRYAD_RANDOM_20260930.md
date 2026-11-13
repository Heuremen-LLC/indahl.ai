# DRYAD RANDOM PICK, 2026-09-30 -- THE THREE FORMULAS ON A RANDOM RECORD

Wayfinder: "pick a random topic in the Dryad and hit that shit too... find one that gets us laid."
Seed = UTC minute at run time (18:28Z) = 28. Word list index 28 mod 20 = 8 -> **"bird"**.
Page = 28 mod 5 + 1 = **4**. Index into page = 28 mod 100 = **28**.

## The pick

Index 28 (page 4, word "bird"): *"Data for: Phantom rivers filter birds and bats by acoustic
niche"* (doi:10.5061/dryad.n5tb2rbsv) -- SKIPPED, only file is a 110.6MB zip, over budget, no
small tabular file to check. Checked 29-34 in order, all skipped (cross-sectional demography/
collision/radar/arthropod tables, no fine repeated-measurement series -- full log in
`parallax/out/dryad_random/covid_birds/SOURCE.txt`). Landed on **index 35**:

**"Rapid behavioural response of urban birds to COVID-19 lockdown"** (Gordo et al. 2020,
doi:10.5061/dryad.8w9ghx3kc, primary article doi:10.1098/rspb.2020.2513). 126,315 species-detection
rows from a Spanish citizen-science bird survey, `pres` (0/1) x `hour_std` (survey start time,
standardized: -1=sunrise, 0=noon, +1=sunset; actual range -1.168 to +1.109 here). Pooling all
16 species and all 3 site-history groups and binning `hour_std` into 60 equal-width bins gives a
genuine repeated-measurement series: **pooled detection rate across the dawn-to-dusk day**, a
dawn-chorus-adjacent detectability arc (sharp rise pre-dawn, plateau ~0.4-0.55, sharp fall after
dusk). n_obs/bin backing each rate point: 32-4547 (uneven, kept as a column).

No periodic cycle exists in this record (one arc, not an oscillation) -- flagged before running
THE SPLIT.

## The three cells (windows = first/mid/last third of the 60-bin arc: dawn/midday/dusk)

| formula | window | value | error | reversed-trace value | reversed error | verdict |
|---|---|---|---|---|---|---|
| ARROW A(k) | dawn | +0.004677 (k=6) | boot sd 0.00606 | -0.004677 | 0.00602 | **AGREE** |
| ARROW A(k) | midday | -0.004007 (k=5) | boot sd 0.00293 | +0.004007 | 0.00284 | **UNSTABLE** (flips sign, |A|<error either way) |
| ARROW A(k) | dusk | +0.003616 (k=3) | boot sd 0.00257 | -0.003616 | 0.00263 | **UNSTABLE** |
| CLOCK tau | dusk decay | 0.440 (hourstd units) | boot sd 2.91 | -0.440 (reversed) | boot sd 4.96 | **AGREE** (both swamped by error -- tau unresolvable at n=20/window, not a real decay measurement) |
| CLOCK tau | dawn onset | -0.415 | boot sd (huge, see below) | -- | -- | same-order-of-magnitude as dusk tau, ratio -0.94 |
| SPLIT D | -- | S=-0.113, P=0.117 (n=16 "cycles") | resid sd 0.061 | -- | -- | **NOT COMPARABLE -- FAILED**, computed only on a degenerate proxy (n_obs sampling-effort local maxima, not a real periodic signal); logged, not sold as real |

Bootstrap errors are resampled WITHIN real pairs/cycles (not label-shuffled); 1000-shuffle floors
were also computed per the task spec but are not the verdict (shuffles can only refind
themselves).

## Forward vs backward chain, and vs the yeast record

- **Forward chain (split -> arrow -> clock) is BROKEN at step 1**: split has no legitimate input
  (no periodic cycles), so it cannot feed arrow or clock. Backward chain (clock -> arrow -> split)
  runs clock and arrow fine but breaks at split for the identical structural reason. **Both chains
  fail at the same place, for the same reason** -- not a numeric disagreement, a missing-data wall.
- **Arrow**: AGREEs in sign-flip-under-reversal in the dawn window (as designed), but is
  statistically indistinguishable from its own error bar in midday and dusk (z of order 1-2.4 on
  n=20-point windows -- thin). Best-k's (3-6 bins) are all small relative to window length (20
  bins), no dominant scale found.
- **Clock**: both fitted tau's (dawn -0.42, dusk 0.44, in hour_std units, ratio -0.94, same order
  of magnitude) come with bootstrap sd's 7-11x the point estimate -- **unresolvable at this window
  length (n=20 bins/window)**, read as "roughly flat, no confident decay constant," same character
  as the yeast record's weak before/after clock fits (log-residuals 0.58-0.59 there too).
- **vs yeast** (`THREE_ON_YEAST_20260930.md`): yeast's arrow found real signal (z up to 5.8,
  clean sign-flip under reversal in all 4 windows); this bird record's arrow only clean-agrees in
  1 of 3 windows and is noise-level in the other 2. Yeast's clock taus (688-1179s, tight in one
  fit) dwarfed its arrow k's by 6-15x -- a real scale mismatch; this record's clock and arrow
  scales aren't comparable at all (different units, hour_std vs bin-count) and clock itself
  didn't resolve. Yeast's split had a real (if thin, n=11, partly circular) periodic structure to
  work with; this record's split has **none** -- a harder, more honest failure than yeast's
  caveated one. **Three-way call: this record is a strictly noisier, structurally poorer cousin of
  the yeast standoff** -- same tools, same non-convergence pattern, but with less real signal to
  even disagree about.

## Error rows (nothing thrown away)

| stage | detail | raw numbers |
|---|---|---|
| split | fewer than 4 real periodic peaks exist in the detection-rate series itself (0 -- it's one arc); computed only on n_obs (sampling-effort) local maxima as a proxy, 16 "cycles" found this way | S=-0.113, P=0.117, resid sd=0.061 -- flagged degenerate, not a real split |
| clock (dawn) | log-residual not tightly constrained; bootstrap tau sd (2.91) is ~7x the point estimate (0.415) | tau=-0.415, C0 fit n=20 |
| clock (dusk) | same: bootstrap tau sd (2.91 fwd / 4.96 rev) ~7-11x point estimate (0.440) | tau=0.440 fwd, -0.440 rev |
| arrow (midday, dusk) | z (2.27, 2.35) nominally "significant" vs shuffle floor but sign flips and magnitude collapses under time-reversal at n=20 -- read as window-length artifact, not real order | A=-0.00401 (midday), +0.00362 (dusk), boot sd same order as A itself |

## Tries

1 Dryad page/index lookup, 1 skipped record (110MB zip, over budget), 6 further
cross-sectional records checked and skipped in sequence (29-34), landed on 1 usable record
(index 35). 1 download via version-level zip_assembly (file-level endpoint 401'd, worked
around). 1 binning script, 1 three-formulas script (adapted from
`parallax/out/yeast/three/three_formulas.py` + `backwards.py`'s AGREE/STABLE
DISAGREEMENT/UNSTABLE verdict rule), run once, no retries needed after the endpoint fix.

Files: `~/bones-forge/parallax/out/dryad_random/covid_birds/` (raw txt, SOURCE.txt,
dawn_chorus_series.csv, three_formulas_birds.py, results.json).
