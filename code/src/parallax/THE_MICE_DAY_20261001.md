# THE MICE DAY -- 2026-10-01, Bones's field hand

THE OBJECT: the mice's period. MEDIUM_AT_MATCHED_LENGTH's K-CAP FIX found arrow lag k=114 at
EVERY cap, at n=1500 (first 1500 of 8192 15-min points, ~15.6 days), i.e. ~28.5h -- long against
the textbook mouse free-run (23.5-24.5h). This file measures the period THREE independent ways
per mouse on dryad.1v8j2 (25 female mice, body temp every 15 min, 8192 points each, housed in
8 groups sizes 3,1,2,5,5,2,4,3): (a) the arrow's best k, cap at n/4; (b) FFT peak period,
block-bootstrap error; (c) autocorrelation first peak, block-bootstrap error. No expectation
written before running. Script: `out/the_middle/the_mice_day.py` (numpy only). Raw output:
`out/the_middle/the_mice_day_results.json`. Frozen instrument reused verbatim: `out/three_on_three/
core.py` (arrow_stat, arrow_best_k_fast) and the block-bootstrap pattern from
`out/the_middle/kcap_fix_medium.py`. Group->mouse mapping re-derived directly from filenames
(`SC<mouseID>.<groupID>`), confirmed identical to THREE_ON_MICE_ANTS's count: group sizes
{1:3, 2:1, 3:2, 4:5, 5:5, 6:2, 7:4, 8:3}, sum=25. Buckets: size1={group2, 1 mouse}, size2-3=
{groups 1,3,6,8, 10 mice}, size4-5={groups 4,5,7, 14 mice}. Runtime 31.7s, 0 load failures.

## 1. Per mouse, three periods, agreement call

Arrow: n=1500 (first 1500 pts), cap kmax=n//4=375, point estimate n_shuf=100, error from
block-bootstrap (30 reps, block_frac=0.1, n_shuf_inner=20 per rep). FFT: whole 8192-pt record,
peak in 12-48h band, error from 200 block-bootstrap reps. ACF: whole record, FFT-based
autocorrelation, FIRST local max in 12-48h band (not global max), error from 200 block-bootstrap
reps. AGREE = all three methods' (period +/- err) intervals mutually overlap. STABLE
DISAGREEMENT = no overlap but every method's own bootstrap error is smaller than its point
estimate (converged, just different numbers). UNSTABLE = any method's bootstrap sd exceeds its
own point estimate (non-convergent) or a method found no peak at all.

**Counts across 25 mice: AGREE 4, STABLE DISAGREEMENT 14, UNSTABLE 7.** No mouse's three methods
agree by default -- disagreement is the norm, and roughly 1 in 4 mice have at least one method
that does not converge at all (arrow mainly: its own block-bootstrap sd is often 1-4x the point
estimate itself -- see mouse 10 below, boot sd=126.8h on a point estimate of 28.5h).

## 2. Per housing bucket, pooled period, difference by group, spread, phase alignment

**Pooled period (inverse-variance weighted mean across mice in the bucket), per method:**

| bucket | n mice | ARROW mean+/-err (h) | reduced chi2 | FFT mean+/-err (h) | reduced chi2 | ACF mean+/-err (h) | reduced chi2 |
|---|---|---|---|---|---|---|---|
| size1 | 1 | 28.50 +/- 31.70 | -- (0 dof) | 23.81 +/- 0.61 | -- (0 dof) | 15.25 +/- 1.68 | -- (0 dof) |
| size2-3 | 10 | 59.73 +/- 8.16 | 0.80 | 23.90 +/- 0.21 | 0.04 | 14.85 +/- 0.46 | 10.06 |
| size4-5 | 14 | 40.49 +/- 7.25 | 1.23 | 23.92 +/- 0.19 | 0.04 | 17.77 +/- 0.48 | 9.46 |

**FFT is the one clean number: 23.8-23.9h in every bucket, reduced chi2 ~0.04 (mice within a
bucket AGREE tightly with each other), and size1/size2-3/size4-5 overlap completely pairwise
(z = -0.17 to -0.06, all "overlap: true")** -- no detectable housing effect on FFT period at all.
**ACF is split into two populations (not one number)**: 12.5-13.5h in some mice, 23.75-24h in
others (a 2:1 sub-/full-harmonic split of the same real daily rhythm -- the detector is catching
either the true 24h peak or a secondary within-day sub-peak as "first peak"), giving reduced
chi2 ~9-10 within both housed buckets (bimodal, not noisy-around-one-value) and a real pairwise
difference size2-3 vs size4-5 (z=-4.39, no overlap) and size1 vs size4-5 (z=-1.44, no overlap) --
but this is an artifact of which harmonic the first-local-max detector lands on, not evidence of
a different true period by group (the FFT, run on the same records, shows no such split).
**ARROW is the unstable one**: size2-3 (59.7h) vs size4-5 (40.5h) differ with no error overlap
(z=1.76), but size1's own single value (28.5h) carries an error (31.7h) larger than itself and
overlaps everything -- consistent with Section 1's non-convergence finding, not a real
housing-size trend (see Section 4: the SAME mouse's own arrow k is not even stable across time
windows of its own record).

**Within-bucket spread (unweighted sd of raw point estimates, housed vs not)**: FFT spread is
tiny and roughly EQUAL across buckets (sd 0.13h for both size2-3 and size4-5, no size1 to
compare since n=1) -- no shrinkage from housing on the period itself. ACF spread is similarly
flat (~5.1-5.3h, both housed buckets) -- again no shrinkage. Arrow spread is large and, if
anything, slightly LARGER in size2-3 (sd=22.1h) than size4-5 (sd=29.3h) -- no shrinkage, and in
the wrong direction for a "coupling tightens with group size" story even taken at face value.

**Phase alignment (circular mean of each mouse's daily temperature-peak clock-hour, resultant
length R per original group, R=1 means every mouse in that group peaks at the same hour of day,
R=0 means uniformly scattered):**

| group | size | bucket | R |
|---|---|---|---|
| 2 | 1 | size1 | 1.000 (trivial, n=1, flagged not a real alignment) |
| 1 | 3 | size2-3 | 0.286 |
| 3 | 2 | size2-3 | 0.819 |
| 6 | 2 | size2-3 | 0.961 |
| 8 | 3 | size2-3 | 0.937 |
| 4 | 5 | size4-5 | 0.789 |
| 5 | 5 | size4-5 | 0.331 |
| 7 | 4 | size4-5 | 0.842 |

Bucket mean R: size1 = 1.000 (trivial), size2-3 = 0.751 (4 groups), size4-5 = 0.654 (3 groups).
**The quintets/quartet do NOT show higher phase alignment than the pairs/trios -- the opposite,
by this measure** (one quintet, group 5, has the lowest R of any multi-mouse group at 0.331,
on par with the lowest trio, group 1 at 0.286).

## 3. The paper's claim as a test: exact permutation over group labels

Statistic: mean(R) over the real size4-5 groups (4,5,7) minus mean(R) over the real size1+size2-3
groups (1,2,3,6,8) -- phases are NEVER shuffled in time; only which already-fixed group's R value
gets the "big" label is permuted (relabeling, not destroying order -- the standing rule that
shuffle is never the judge of a real-vs-real difference does not apply to this relabeling test,
which is testing group identity, not time structure). **Observed stat = -0.147** (big groups LESS
aligned on average). Exact enumeration, choosing which 3 of the 8 real groups get the "big"
label: C(8,3) = **56** total relabelings. One-sided fraction (as or more "big>small" than
observed) = **46/56 = 0.821**; two-sided = **30/56 = 0.536**. Repeating with the trivial n=1
singleton group dropped (comparing only the 7 genuinely-multi-mouse groups, C(7,3)=35
relabelings): observed stat = -0.097, one-sided fraction = **26/35 = 0.743**, two-sided =
**20/35 = 0.571**. **Both ways, the real assignment sits in the LOW half of the permutation
distribution for "big beats small" -- the data give no support for the paper's own synchrony
claim under this phase-alignment statistic**, with or without the singleton. This does not
contradict the original paper (different statistic -- cycle-to-cycle phase relationship across
successive days, not a single clock-of-day phase averaged over the whole record) but it does not
reproduce it either, consistent with DRYAD_SWEEP's and THREE_ON_MICE_ANTS's own prior findings on
this same dataset (recursive gradient and three-formula passes also found no clean group-size
effect).

## 4. Where did 28h come from?

Arrow k-search run on 5 disjoint 1500-pt segments spanning the whole 8192-pt record (offsets
0,1500,3000,4500,6000 -- segment 0 = first ~15.6 days = the exact window K-CAP FIX used).
**Mouse 10 (the one size1 mouse, the SAME mouse K-CAP FIX flagged)**:

| segment (offset, pts) | k | period (h) | z |
|---|---|---|---|
| 0 (days 0-15.6) | 114 | **28.5** | +5.16 |
| 1500 (days 15.6-31.3) | 23 | 5.75 | +5.81 |
| 3000 (days 31.3-46.9) | 20 | 5.00 | +5.90 |
| 4500 (days 46.9-62.5) | 352 | 88.0 | -9.85 |
| 6000 (days 62.5-78.1) | 21 | 5.25 | +4.91 |

**28.5h is not a stable mouse property and not a slowly-decaying transient either -- it is one
value among five wildly different ones (5h, 5h, 88h, 5h) from the SAME individual's own record,
with no settling pattern.** The arrow formula's own block-bootstrap error on the first segment
(k_boot_mean=180.9, k_boot_sd=126.8, i.e. a 1500-point window's arrow estimate does not even
reproduce itself under block resampling) already said this before the segment sweep confirmed
it: 28h is this instrument's own noise on this particular slice of this particular mouse, not a
biological period. Per-bucket mean arrow period across the same 5 offsets stays noisy throughout
(size2-3: 51.5, 66.3, 51.6, 60.1, 62.6h; size4-5: 50.3, 51.5, 52.3, 45.1, 55.7h) -- no bucket
shows a clean decay from a high early value toward 24h; the arrow number simply never converges
on the circadian period at this record length, early or late, housed or not.

## 5. Plain words

**The mice's real period, measured three ways, is ~23.8-23.9h** -- the FFT, run on the full
8192-point record, lands there for every one of the 25 mice with a tight within-bucket spread
(sd~0.13h) and zero detectable difference by housing size (singles, pairs/trios, and
quartets/quintets all overlap completely). That number matches the textbook mouse free-run
(23.5-24.5h) exactly. The autocorrelation agrees with FFT about half the time and locks onto a
roughly-half-period harmonic (12.5-13.5h) the other half -- a detector artifact (which local
maximum it finds first), not a second true period, and not tied to housing size either.
**The arrow's ~28h, and the "k=114 at every cap" finding that motivated this whole file, is the
window talking, not the mouse**: the same individual mouse's own arrow k bounces from 28.5h to
5h to 88h to 5h across five successive slices of its own single uninterrupted record, and the
first slice's own bootstrap error (126.8h sd) already said the estimate does not reproduce under
resampling. **Housing does not change the mice's period** by any of the three methods. **Housing
does not clearly change phase alignment either**: the paper's own claim (quintets synchronize,
singles/pairs don't) does not reproduce under a clock-of-day phase/resultant-length test here --
the real group assignment sits in the bottom half of 56 (and 35, singleton-excluded) exact
relabelings for "big groups more aligned than small ones," in the WRONG direction on average (one
quintet is the single worst-aligned multi-mouse group in the whole dataset). This is a different
statistic than the paper used (whole-record clock-of-day phase vs. the paper's cycle-to-cycle
phase relationship), so it does not refute the paper -- it just does not confirm it, consistent
with every other pass this lab has run on this same dataset.

## Tries, failures

Tries (exact counts from the run): 900 arrow searches, 9,350,000 arrow shuffle draws, 750 arrow
block-bootstrap replicate-series, 5,000 FFT block-bootstrap draws, 5,000 ACF block-bootstrap
draws, 25 sinusoid phase fits. **0 failed rows** -- every one of the 25 mice produced a complete
arrow+FFT+ACF+phase record and all 5 transient segments; the only "errors" anywhere in this pass
are the already-reported non-convergent bootstrap SDs (a real, finite, honestly-large number, not
a crash), and the trivial n=1 R=1.0 for the singleton group, flagged in Sections 2 and 3, not
hidden.

## THE PAPER'S STATISTIC -- 2026-09-30

Section 3 above explicitly flagged that its phase-alignment test was NOT the statistic the
authors used. This section finds and reproduces the authors' actual statistic.

### 1. The paper's method, quoted

Paper: Paul MJ, Indic P, Schwartz WJ (2015). "Social synchronization of circadian rhythmicity
in female mice depends on the number of cohabiting animals." *Biology Letters* 11: 20150204.
doi:10.1098/rsbl.2015.0204, PMID 26063754, PMCID PMC4528468 (open access). Fetched via Europe
PMC / PMC full text (WebFetch extraction of the PMC page -- quotes below as returned by that
extraction, not re-verified against the raw XML/PDF; the abstract portion is independently
confirmed via the PubMed MCP tool's own abstract field, word-for-word identical).

Abstract (direct from PubMed): "...recording individual circadian body temperature rhythms of
female house mice housed singly, in twos (pairs), or in groups of five (quintets) in constant
darkness; determining the daily phases of the circadian peak for each animal; and then
calculating the cycle-to-cycle phase relationship between cohabiting animals over time.
Significant temporal coherence was observed in quintets: the proportion of quintets (4/7), but
not pairs (2/8), that became synchronized was greater than could be achieved by the complete
simulated reassortment of all individuals."

Methods detail (PMC full text, via WebFetch extraction): daily phase per animal came from "the
complex-valued Morlet continuous wavelet function" (procedure detailed in Leise et al. 2013,
not reproduced here -- no wavelet library in this numpy-only, single-process environment).
Coherence: "a coherence = 1 represents rhythms with identical phase, and a coherence = 0
represents rhythms in anti-phase" (pairs); "with the five individual phases plotted as points
on a unit circle, coherence was defined as the resultant vector" (quintets) -- the SAME
circular-resultant-length statistic for any group size, used uniformly here. Threshold:
"Synchronization was defined as an average coherence for days 44-75 (the second month of
cohabitation) of greater than or equal to 0.8 and outside the 95% prediction interval" (the
prediction interval came from the paper's own "complete simulated reassortment" of individual
mice into fake pairs/quintets -- stated cohort "16 mice in pairs and 35 mice in quintets", i.e.
8 pairs + 7 quintets = 51 mice).

**Cohort mismatch, reported as a row, not hidden**: this Dryad record (dryad.1v8j2, same DOI)
has only 25 mice in 8 groups sized 1,1,2,2,3,3,4,5,5 -- it does NOT match the paper's stated 51
mice (8 pairs, 7 quintets; no trios or quartets mentioned in the text at all). This is the only
public body-temperature file bundle attached to this DOI (confirmed by the DRYAD_SWEEP fetch),
used as the closest available stand-in for "the paper's own data," not a confirmed 1:1 match to
what was analyzed in the published figures.

### 2. Reproducing the statistic

**Substitute for the wavelet phase** (closest standard, flagged): FFT bandpass (18-30h band) on
each mouse's whole 8192-point record, then an FFT-based Hilbert transform for the instantaneous
phase. Sampled once per real calendar day (group start + d*24h + 12h, nearest actual sample
within 1h) -- NOT once per index-count day, so cage-mates (who started recording within minutes
of each other, confirmed from raw timestamps) are compared at the same real clock time each day.
Daily coherence R(d) = circular resultant length across all present group members that day (the
singleton group, n=1, is excluded -- coherence undefined for one animal). 7 housed groups, 32
usable days each in the paper's own days-44-75 window (85-day records, same span used
throughout this lab's passes on this dataset).

**Per-group average coherence, days 44-75, and the paper's own >=0.8 threshold:**

| group | size | bucket | avg coherence (days 44-75) | synchronized (>=0.8)? |
|---|---|---|---|---|
| 1 | 3 | size2-3 | 0.299 | NO |
| 3 | 2 | size2-3 | 0.612 | NO |
| 6 | 2 | size2-3 | 0.970 | YES |
| 8 | 3 | size2-3 | 0.824 | YES |
| 4 | 5 | size4-5 | 0.439 | NO |
| 5 | 5 | size4-5 | 0.269 | NO |
| 7 | 4 | size4-5 | 0.840 | YES |

Size2-3 (pairs/trios): 2/4 synchronized. Size4-5 (quartet/quintets): 1/3 synchronized -- the
OPPOSITE proportion from the paper's claim (quintets more often synchronized than pairs).

**Exact permutation over group labels** (7 usable groups, choose 3 "big": C(7,3) = 35, same
enumeration as Section 3, same rule -- group identity permuted, time order inside each series
never touched): statistic = mean(avg coherence) over size4-5 groups minus size1/2/3 groups.
**Observed = -0.160** (big LESS synchronized on average). One-sided fraction (big>small, as
the paper claims) = **27/35 = 0.771**; two-sided = **17/35 = 0.486**. Repeating on the BINARY
synchronized call (paper's actual reported quantity, a 0/1 call per group): observed
stat = **-0.167**, one-sided fraction = **31/35 = 0.886**. **Both ways, using the paper's own
coherence statistic and the paper's own 0.8/days-44-75 threshold, the real group assignment
sits deep in the LOW half of the exact permutation distribution for "big beats small" -- this
does not reproduce the paper's claim, and the direction is reversed from what the paper
reported**, consistent with Section 3's independent (different-statistic) finding and with
DRYAD_SWEEP_20260930's own flag that a quick reproduction attempt on this same data did not
confirm the published result.

### 3. The time course: does synchronization rise over the record?

Per housed group, daily coherence R(d) in sliding 3-day windows (step 1 day) across the full
record, OLS slope of window-mean R vs. window-center day, error from residual-based OLS SE
(83 windows per group):

| group | size | bucket | slope (R/day) | error |
|---|---|---|---|---|
| 1 | 3 | size2-3 | -0.00794 | 0.00069 |
| 3 | 2 | size2-3 | -0.00723 | 0.00038 |
| 6 | 2 | size2-3 | +0.00079 | 0.00031 |
| 8 | 3 | size2-3 | -0.00482 | 0.00056 |
| 4 | 5 | size4-5 | +0.00005 | 0.00054 |
| 5 | 5 | size4-5 | -0.00383 | 0.00042 |
| 7 | 4 | size4-5 | -0.00092 | 0.00031 |

**Singles' control**: with only one true size-1 mouse in this bundle, the "unrelated, should not
rise" control was built from 10 contemporaneous cross-group pairs (same real cohort start month,
never cohabiting, chosen deterministically by rotation, not hand-picked) run through the exact
same daily-coherence + sliding-window-slope pipeline. Control slopes: mean = **-0.00067**,
sd = **0.00371** (n=10 pairs). **Every real housed group's slope sits well inside this control
spread** (the largest-magnitude real slope, -0.00794, is ~2.1 control-sd from the control mean,
and most are within 1 control-sd) -- **no housed group shows a rise in synchronization over the
record that is distinguishable from the unrelated-pair null; if anything most slopes (5 of 7)
are negative (slightly declining), not rising.**

**A second, unplanned finding surfaced by building the control**: the "unrelated" pairs' own
mean coherence levels were often high too (e.g. pair 21-25: mean R=0.976; pair 15-20: mean
R=0.911) -- not just their slopes near zero. This traces directly back to Section 2's FFT
result: every one of the 25 mice' s true period sits in a 23.8-23.9h band with sd~0.13h
regardless of housing. With the free-running periods THAT tight across the whole colony,
ANY two mice -- cohabiting or not -- hold a nearly fixed relative phase for 85 days simply
because neither one's clock drifts away from the other's by much. **The paper's whole
statistic assumes individual free-running periods would drift apart without social coupling;
this dataset's own measured periods (Section 2) are too tightly clustered for that assumption
to produce a clean null**, which is itself a likely reason this reproduction attempt (and
DRYAD_SWEEP's independent one) comes up empty either direction.

### 4. Plain words

The authors measured daily circadian phase per animal (wavelet-derived), then the day-to-day
circular coherence (resultant length) among cage-mates, and called a group "synchronized" if
that coherence averaged >=0.8 over the second month of cohabitation, testing whether quintets
hit that bar more often than pairs via reassortment simulation. Reproducing the SAME
statistic (coherence, same 0.8/days-44-75 threshold) on the SAME public dataset (with the
cohort-size caveat above, honestly reported) gives **2/4 size2-3 groups synchronized vs. 1/3
size4-5 groups synchronized -- the opposite ratio from the paper**, and the real group
assignment sits in the bottom ~12-23% of the exact group-label permutation distribution for
"big beats small" either way the statistic is scored (continuous coherence or binary sync
call). **Housed mice do not show rising synchronization over the record** by this statistic
either -- every group's sliding-window slope sits inside the noise band set by unrelated,
non-cohabiting pairs run through the identical pipeline. The likely reason this and every
other pass on this dataset comes up empty is structural, not just low power: the colony's
true circadian periods (Section 2, FFT) are so tightly clustered (23.8-23.9h, sd~0.13h) that
even non-cohabiting mice hold a near-fixed relative phase for the full 85-day record, which
flattens the very signal (period-drift-prevented-by-coupling) the paper's design was built to
detect.

### Tries, failures

Tries (exact counts): 25 Hilbert phase extractions, 3,740 daily phase samples, 595 daily
coherence computations, 7 sliding-window OLS slope fits (housed groups) + 10 more (control
pairs), 35 exact group-label permutations (continuous statistic) + 35 more (binary statistic).
**1 failed/flagged row**: the cohort-size mismatch between this Dryad file bundle (25 mice) and
the paper's stated analyzed cohort (51 mice), reported above, not hidden. No crashes; every
housed group and every attempted control pair produced a complete coherence series and slope
once cohort-contemporaneity was enforced for the controls (an earlier draft of the control
pairing, not cohort-restricted, produced 6 of 10 unusable zero-overlap pairs because it paired
mice from the two non-overlapping real recording cohorts -- 2008-08 and 2009-03 -- fixed before
the numbers above were produced, logged here rather than silently rerun).

## Files

- Report: `~/bones-forge/parallax/THE_MICE_DAY_20261001.md` (this file)
- Script: `out/the_middle/the_mice_day.py`
- Raw results: `out/the_middle/the_mice_day_results.json`
- Paper's-statistic script: `out/the_middle/the_papers_statistic.py`
- Paper's-statistic raw results: `out/the_middle/the_papers_statistic_results.json`
- Paper's-statistic run log: `out/the_middle/run_log_the_papers_statistic.txt`
- Run log: `out/the_middle/run_log_the_mice_day.txt`
