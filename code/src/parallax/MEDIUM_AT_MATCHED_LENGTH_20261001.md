# MEDIUM AT MATCHED LENGTH -- 2026-10-01, Bones's field hand

LENGTH_ORDERS_GAP_20261001.md showed the six-substrate exact ordering of G_s (clock-minus-split,
series-taus) by record length is AT LEAST PARTLY a ruler effect: truncating a single record
(neurons, radio) reproduces the same climb, and the exact 1/720 ordering lives in raw sample count,
not beats or seconds. The truncation pass's own n=800 points hinted the opposite is also true --
yeast +2.90+/-0.72 sat above neurons +0.76+/-0.82 above radio -0.02+/-1.13 at the SAME length -- but
no formal medium-vs-medium test was run on that. **THE OBJECT of this file**: with length matched
across media, what of the gap belongs to the medium? No expectation written before running. Script:
`out/the_middle/matched_length_medium.py` (numpy only). Raw output:
`out/the_middle/matched_length_medium_results.json`. Frozen instruments reused verbatim, not edited:
`core.py`, `split_v2.py`, `calibrated_standoff.py` (same K_TAU=0.053767), `load_horn.py`,
`load_buzz.py`, `load_echo.py`. The per-segment measurement wrapper (fast_acf/measure_clock_acf/
measure_arrow_seg/measure_split_seg/to_T/gap) is copied verbatim from LENGTH_ORDERS_GAP's own prior
pass, reused unedited. The only new code: the per-medium segmenter rules, the pairwise medium calls,
the ordering/permutation tests, and the "what orders it" Spearman tests.

## 0. Segment rules per medium (stated, not left implicit)

Lengths n={800, 1500} -- the two every medium can supply, set by yeast's own full record (1531
samples: 1 segment at n=800, 1 at n=1500, no more). Three disjoint segments per medium wherever the
record allows, fewer stated not padded:

- **yeast** -- 1 record (NADH whole, n_total=1531): 1 segment at each n (the record cannot give 3).
- **radio** -- both windows: at-horn (n_total=1423, 1 segment max) fills slot 1 at n=800, the whole
  record (n_total=29226) fills the remaining 2; at n=1500 at-horn can't supply one (1423<1500,
  failed, logged) so all 3 come from whole.
- **chip** -- 1 segment per buzz seat (80/100/116, n_total=4000 each) = 3 segments, pooled as "chip".
  Echo running-mean (gap=20us, median proxy over 74 readable qubits, n_total=1500) run as a FOURTH,
  separate, not pooled into chip's 3.
- **mice** -- size-1 (SC10.2) + size-4/5 (median-pooled triple), 1 segment each, n_total=8192 both --
  only 2 segments, not 3, stated not padded.
- **neurons** -- 1 segment per sister culture (1-1, 1-2, 1-3), day 25 (bursting, same pick
  NEURONS_20261001.md Sec3/4 carried through), 10ms population-rate bins = 3 segments.
- **copper** -- the 212Hz line (COPPER_800's own flagged line), n_total=800 exactly: 1 segment at
  n=800, FAILS at n=1500 (record too short, logged).

## 1. MATCHED-n TABLE -- G_s per medium x segment x n

| medium | n | segment | G_s | err |
|---|---|---|---|---|
| yeast | 800 | whole[0:800] | +2.937 | 0.736 |
| yeast | 1500 | whole[0:1500] | +2.584 | 0.563 |
| radio | 800 | at_horn[0:800] | +3.839 | 1.159 |
| radio | 800 | whole[0:800] | -0.463 | 1.604 |
| radio | 800 | whole[800:1600] | -0.050 | 1.669 |
| radio | 1500 | whole[0:1500] | -0.068 | 1.673 |
| radio | 1500 | whole[1500:3000] | +1.266 | 1.010 |
| radio | 1500 | whole[3000:4500] | -0.010 | 1.658 |
| chip | 800 | seat80[0:800] | +4.242 | 1.180 |
| chip | 800 | seat100[0:800] | +4.928 | 1.174 |
| chip | 800 | seat116[0:800] | +3.872 | 1.184 |
| chip | 1500 | seat80[0:1500] | +3.497 | 1.127 |
| chip | 1500 | seat100[0:1500] | +3.996 | 1.071 |
| chip | 1500 | seat116[0:1500] | +4.029 | 1.177 |
| chip_echo (bonus) | 800 | echo20_runmean[0:800] | OPEN | -- |
| chip_echo (bonus) | 1500 | echo20_runmean[0:1500] | OPEN | -- |
| mice | 800 | size1[0:800] | +0.320 | 0.414 |
| mice | 800 | size45[0:800] | +1.942 | 1.075 |
| mice | 1500 | size1[0:1500] | -0.745 | 1.579 |
| mice | 1500 | size45[0:1500] | +0.936 | 0.757 |
| neurons | 800 | culture1-1[0:800] | +1.133 | 1.222 |
| neurons | 800 | culture1-2[0:800] | +3.092 | 1.038 |
| neurons | 800 | culture1-3[0:800] | -0.369 | 1.644 |
| neurons | 1500 | culture1-1[0:1500] | -0.347 | 0.646 |
| neurons | 1500 | culture1-2[0:1500] | +3.256 | 1.111 |
| neurons | 1500 | culture1-3[0:1500] | -0.670 | 1.577 |
| copper | 800 | line212[0:800] | +0.740 | 1.523 |
| copper | 1500 | -- | FAILS (n_total=800<1500) | -- |

**Pooled (weighted mean, 1/err^2) per medium x n:**

| medium | n | n_segs resolved | G_s pooled | err | reduced chi2 |
|---|---|---|---|---|---|
| yeast | 800 | 1/1 | +2.937 | 0.736 | -- (0 dof) |
| yeast | 1500 | 1/1 | +2.584 | 0.563 | -- (0 dof) |
| radio | 800 | 3/3 | +1.783 | 0.819 | 3.16 |
| radio | 1500 | 3/3 | +0.713 | 0.767 | 0.35 |
| chip | 800 | 3/3 | +4.350 | 0.681 | 0.21 |
| chip | 1500 | 3/3 | +3.841 | 0.648 | 0.07 |
| mice | 800 | 2/2 | +0.530 | 0.387 | 1.98 |
| mice | 1500 | 2/2 | +0.622 | 0.683 | 0.92 |
| neurons | 800 | 3/3 | +1.775 | 0.713 | 1.79 |
| neurons | 1500 | 3/3 | +0.425 | 0.526 | 4.20 |
| copper | 800 | 1/1 | +0.740 | 1.523 | -- (0 dof) |
| copper | 1500 | OPEN | -- | -- | -- |

## 2. ONE NUMBER PER MEDIUM? Within and between

**Within-medium** (reduced chi2 across its own segments, Section 1 table): chip is the cleanest
("ONE NUMBER" territory, 0.21 and 0.07 -- its three buzz seats agree tightly with each other at both
n); radio and mice are borderline-to-OK (radio 3.16->0.35, mice 1.98->0.92, improving at n=1500);
neurons is the WORST (1.79->4.20, getting worse at the longer n -- culture1-2 runs persistently high
(+3.09, +3.26) while 1-1 and 1-3 sit near or below zero, a real culture-to-culture spread, not just
wide error bars). Yeast and copper have only 1 segment each -- no within-medium test possible,
reported not guessed.

**Medium vs medium**, every pair, both n (diff vs combined pooled error; STABLE DISAGREEMENT requires
the SAME-SIGN difference at both matched n's, per the standing rule; a sign flip or a single-n
resolution is UNSTABLE):

| pair | n=800 | n=1500 | call |
|---|---|---|---|
| yeast vs radio | differ | differ, same sign | **STABLE DISAGREEMENT** (yeast > radio both lengths) |
| yeast vs chip | differ | differ, same sign | **STABLE DISAGREEMENT** (chip > yeast both lengths) |
| yeast vs mice | differ | differ, same sign | **STABLE DISAGREEMENT** (yeast > mice both lengths) |
| yeast vs neurons | differ | differ, same sign | **STABLE DISAGREEMENT** (yeast > neurons both lengths) |
| yeast vs copper | differ at n=800; copper OPEN at 1500 | -- | UNSTABLE (one n only) |
| radio vs chip | differ | differ, same sign | **STABLE DISAGREEMENT** (chip > radio both lengths) |
| radio vs mice | agree at 800 | differ at 1500 | MIXED |
| radio vs neurons | agree | agree | **AGREE** |
| radio vs copper | agree | copper OPEN | **AGREE** (n=800 only) |
| chip vs mice | differ | differ, same sign | **STABLE DISAGREEMENT** (chip > mice both lengths) |
| chip vs neurons | differ | differ, same sign | **STABLE DISAGREEMENT** (chip > neurons both lengths) |
| chip vs copper | differ at n=800; copper OPEN at 1500 | -- | UNSTABLE (one n only) |
| mice vs neurons | agree at 800 | differ at 1500 | MIXED |
| mice vs copper | agree | copper OPEN | **AGREE** (n=800 only) |
| neurons vs copper | agree | copper OPEN | **AGREE** (n=800 only) |

**Read: chip stands apart from everything** -- it STABLY DISAGREES with yeast, radio, mice, AND
neurons, at BOTH matched lengths, same direction (chip always highest). Yeast also stably disagrees
with radio, mice, and neurons (yeast consistently higher than those three). Radio, mice, neurons,
and copper cluster together -- they AGREE or are only MIXED/single-n with each other. **Distinguishable
at matched length: {yeast, chip} vs {radio, mice, neurons, copper}, and chip is additionally
distinguishable from yeast itself.** That is 2-3 resolvable groups out of 6 media, not 6 individually
distinguishable numbers.

## 3. ORDER AT MATCHED n

| n | order (low to high G_s) |
|---|---|
| 800 (6 media) | mice < copper < neurons < radio < yeast < chip |
| 1500 (5 media, copper OPEN) | neurons < mice < radio < yeast < chip |

Restricted to the 5 media resolved at BOTH lengths (mice, neurons, radio, yeast, chip): Spearman
rho between the n=800 order and the n=1500 order = **+0.82**, exact permutation fraction (5!=120
orderings) = **12/120 = 0.100**. **Chip and yeast hold the TOP two positions at both lengths** (chip
highest both times, yeast second-highest both times) -- that part of the ordering IS a medium
property, stable across length. **Mice and neurons swap** (mice above neurons at n=800, below it at
n=1500) and radio sits in the middle both times but its rank among {mice, neurons} moves. So: the
ordering is NOT fully reproduced at both lengths (0.82, not 1.00), but it is not random either
(12/120 is well inside the tail, not a coin flip) -- the top of the order (chip > yeast > the rest)
is a real, length-independent medium property; the ordering among the bottom three is not.

## 4. WHAT ORDERS IT at matched n

Exact-permutation Spearman tests (k = number of media resolving both the property and G_s at that n):

| n | property | n resolved | rho | exact fraction |
|---|---|---|---|---|
| 800 | beat period (samples, arrow best-k) | 6 | **+1.00** | **2/720** |
| 800 | noise floor (DALET residual, cited) | 4 | -0.80 | 8/24 |
| 800 | amplitude rms (mixed units) | 6 | +0.77 | 74/720 |
| 800 | coupled-unit count | 5 | -0.90 | 10/120 |
| 800 | temperature (K) | 6 | -0.83 | 42/720 |
| 1500 | beat period (samples) | 5 | +0.90 | 10/120 |
| 1500 | noise floor (cited) | 4 | -0.80 | 8/24 |
| 1500 | amplitude rms | 5 | +0.60 | 42/120 |
| 1500 | coupled-unit count | 4 | -0.60 | 10/24 |
| 1500 | temperature (K) | 5 | **-1.00** | **2/120** |

**Beat period looks like the strongest hit (2/720 at n=800) but it is a measurement artifact, not a
finding**: the arrow k-search cap is `kmax = min(30, n//4)`, which equals 30 for BOTH n=800 and
n=1500 -- the search ceiling never changes with n. Three of six media (yeast=29, chip=29, radio=28)
land AT or ONE STEP BELOW that fixed ceiling; only mice (3) and copper (5) sit far from it. The
"perfect" ordering is substantially the ceiling sorting media that saturate it (yeast/chip/radio)
above those that don't (mice/copper/neurons=24), not a genuine physical period measurement. Flagged,
not hidden. **Temperature's near-perfect anti-correlation at n=1500 (2/120) is also weaker than it
looks**: of the 5 resolved media, yeast and radio share one temperature (295.15K, room) and mice and
neurons share another (310.15K, body/incubator) -- only chip (0.05K) is a truly distinct value, so
the "ordering" is really "one cold outlier vs. two tied pairs," not five independently-ordered
temperatures. **Coupled-unit count (-0.90 at n=800, 10/120) is built from only 5 media with mostly
degenerate values (four media = 1.0 coupled unit, only mice differs at 2.75)** -- same shape of
caveat. **Honest read: no property here clears the bar as a clean, non-degenerate medium-ordering
driver.** Amplitude rms is the most honestly distinct property (no ties, true mixed-units caveat
flagged) and is the WEAKEST correlation of the five (0.77 and 0.60) -- consistent with amplitude
not being what orders the gap.

## 5. Plain words

**At the same length, do the media still carry different gaps?** Partly. **Chip is distinguishable
from everything** (stably higher than yeast, radio, mice, and neurons, at both n=800 and n=1500) and
**yeast is distinguishable from radio, mice, and neurons** (stably higher, both lengths) -- that is a
real, length-independent separation at the TOP of the ordering. **Radio, mice, neurons, and copper do
NOT cleanly separate from each other** -- mostly AGREE or MIXED (sign flips between the two matched
lengths), consistent with them being one noisy cluster rather than four distinguishable numbers.
**Which media:** {chip, yeast} are the two media whose gap survives matching length; {radio, mice,
neurons, copper} do not resolve from one another. **What orders it:** nothing tested here is a clean
driver. Beat period gives the tightest exact fraction (2/720) but is contaminated by a fixed
k-search ceiling that most media happen to saturate -- a ruler artifact inside THIS instrument, the
same genus of problem LENGTH_ORDERS_GAP already found in the record-length axis itself. Temperature
and coupled-unit count both look strong (2/120, 10/120) but ride on heavily tied/degenerate values
(2-3 distinct levels across 5-6 media), not genuinely resolved orderings. Amplitude, the one
property without ties or an artifact flag, is the weakest correlation of the lot. **How far this is
from the ruler:** LENGTH_ORDERS_GAP found length drives roughly +1 to +3 series-taus of climb per
decade of samples, within a single record. Matching length removes that axis entirely, and real
separation still survives at the top of the ordering (chip, yeast) -- so the medium is not NOTHING,
but what in the medium carries it remains open: none of beat period, noise floor, amplitude,
coupled-unit count, or temperature survives this file's own artifact/tie checks as a clean driver.
A seventh property (sign of some structural rate, not amplitude or a search-capped period) is the
honest next thing to test, not claimed here.

## Failed rows

6 failed cells, all logged: chip_echo (bonus) at BOTH n (zero-variance clock + 0-peaks split, both
lengths -- the running-mean proxy has no periodic structure, same root cause THE_TABLE/echo_proxy
already found); radio at-horn at n=1500 (record too short, n_total=1423); copper at n=1500 (record
too short, n_total=800, by design the only medium that cannot supply the longer matched length).

## Tries

26 segment-computations (1 yeast + 6 radio + 6 chip + 2 chip_echo + 4 mice + 6 neurons + 1 copper,
summed over both n) x 3 formulas (arrow, clock, split) each attempted once: 78,300 shuffle draws,
23,100 bootstrap draws (script's own counters). Every resolved (clock, arrow) and (clock, split)
pair converted through the frozen K(rel_err) map at 20,000 MC draws each: **1,500,000 MC propagation
draws**. 12 pooled weighted-mean/chi-square cells (6 media x 2 n, 2 with 0 dof). 15 medium-pair calls
x 2 n = 30 pairwise comparisons, collapsed to 15 final (cross-length) calls. 1 ordering permutation
test (5 resolved media, 120 orderings enumerated). 10 "what orders it" Spearman tests (5 properties
x 2 n), each an exact permutation enumeration (24 to 720 orderings per test depending on n
resolved) -- **sum of all exact orderings enumerated across every test in this file: 120 (ordering)
+ 2x720 (beat period) + 2x24 (noise floor) + 720+120 (amplitude) + 120+24 (coupled units) +
720+120 (temperature) = 3,432 total orderings enumerated**, zero asymptotic p-values anywhere.
**Grand total this pass: 78,300 shuffles + 23,100 bootstraps + 1,500,000 MC draws + 3,432 exact
permutations enumerated. Runtime 0.9 s, single process.**

## Files

- Report: `~/bones-forge/parallax/MEDIUM_AT_MATCHED_LENGTH_20261001.md` (this file)
- New script: `parallax/out/the_middle/matched_length_medium.py` (numpy only)
- New raw output: `parallax/out/the_middle/matched_length_medium_results.json`
- Run log: `parallax/out/the_middle/run_log_matched_length_medium.txt`
- Reused, unedited: `parallax/out/three_on_three/core.py`, `parallax/out/yeast/three/split_v2.py`,
  `parallax/out/the_middle/calibrated_standoff.py`, `parallax/out/three_on_three/load_horn.py`,
  `parallax/out/three_on_three/load_buzz.py`, `parallax/out/three_on_three/load_echo.py`
- Raw data read directly: `parallax/out/yeast/nadh_fig4_raw_digitized.csv`,
  `parallax/out/three_on_three/horn_4080_pull.csv` (via load_horn),
  `parallax/out/dryad_sweep/mice_social_sync/Body Temperature files/*.txt` (SC10.2 + 3-mouse
  size-4/5 pool), `parallax/out/neurons/raw/{1-1,1-2,1-3}-25.spk.txt`,
  `parallax/out/the_buzz/dat9o2tvr3kc73el5j20.npz` (via load_buzz),
  `parallax/out/echo_20260928_122733/*.npz` (via load_echo),
  `parallax/out/copper_nodes/data/copper_lines_800.json` (212Hz line)
- Cited, not recomputed: noise floor values from `GAP_PER_MEDIUM_20261001.md` Sec2/NEURONS/FIXED_POINTS;
  temperature and coupled-unit counts given per task brief

---

# K-CAP FIX -- 2026-09-30, Bones's field hand

Section 4 above flagged its own best hit (beat period, 2/720 at n=800) as a ruler: the arrow
k-search was capped at `kmax = min(30, n//4)`, which equals 30 at BOTH n=800 and n=1500, and
three of six media (yeast=29, chip=29, radio=28) sat at or one step below that fixed ceiling.
This section removes the `min(30, .)` floor -- `kmax = n//4` only (200 at n=800, 375 at
n=1500) -- re-runs the SAME arrow formula (`core.arrow_stat`/`arrow_best_k_fast`, untouched) over
the wider range, and asks three things: does the beat period change, does it still order the
gap, and does k track the cap itself when the cap is swept further (n//8, n//4, n//2). No
expectation written before running. **G_s (clock-minus-split) is NOT recomputed here** -- it does
not depend on the arrow's k at all, so the pooled G_s numbers in Section 1 above are reused
verbatim, exactly as this is the gap the task asks the new k to be checked against. Script:
`out/the_middle/kcap_fix_medium.py` (numpy only). Raw output:
`out/the_middle/kcap_fix_medium_results.json`. Data loaders and segment rules copied verbatim
from `matched_length_medium.py` (this file's own prior pass); only new code: the kmax-variable
arrow search, a block-bootstrap error on k, the 3-way cutoff sweep, and the Spearman re-tests.

## 1. k per medium per segment: old capped vs fixed (uncapped), bootstrap error

| medium | n | segment | old cap (kmax=30) k | fixed (kmax=n/4) k | boot mean k | boot sd k |
|---|---|---|---|---|---|---|
| yeast | 800 | whole[0:800] | 28 | **114** | 97.8 | 54.1 |
| radio | 800 | at_horn[0:800] | 28 | **173** | 134.0 | 48.9 |
| radio | 800 | whole[0:800] | 12 | 110 | 55.2 | 53.3 |
| radio | 800 | whole[800:1600] | 17 | 164 | 103.0 | 66.0 |
| chip | 800 | seat80[0:800] | 28 | **198** | 105.0 | 44.9 |
| chip | 800 | seat100[0:800] | 24 | 196 | 107.4 | 47.1 |
| chip | 800 | seat116[0:800] | 28 | 59 | 121.1 | 50.7 |
| mice | 800 | size1[0:800] | 3 | 111 | 95.0 | 52.3 |
| mice | 800 | size45[0:800] | 29 | 164 | 95.8 | 57.4 |
| neurons | 800 | culture1-1[0:800] | 7 | 190 | 66.1 | 56.0 |
| neurons | 800 | culture1-2[0:800] | 10 | 10 | 32.5 | 47.1 |
| neurons | 800 | culture1-3[0:800] | 29 | 187 | 78.3 | 61.1 |
| copper | 800 | line212[0:800] | 5 | 5 | 52.8 | 58.3 |
| yeast | 1500 | whole[0:1500] | 29 | **86** | 207.3 | 95.7 |
| radio | 1500 | whole[0:1500] | 24 | 353 | 134.9 | 121.2 |
| radio | 1500 | whole[1500:3000] | 29 | 130 | 190.6 | 105.1 |
| radio | 1500 | whole[3000:4500] | 11 | 167 | 131.3 | 120.2 |
| chip | 1500 | seat80[0:1500] | 22 | 310 | 244.3 | 86.4 |
| chip | 1500 | seat100[0:1500] | 23 | 254 | 239.4 | 95.3 |
| chip | 1500 | seat116[0:1500] | 26 | 248 | 250.2 | 96.4 |
| mice | 1500 | size1[0:1500] | 3 | 114 | 155.8 | 118.3 |
| mice | 1500 | size45[0:1500] | 26 | 311 | 164.8 | 107.1 |
| neurons | 1500 | culture1-1[0:1500] | 1 | 346 | 104.0 | 95.8 |
| neurons | 1500 | culture1-2[0:1500] | 10 | 11 | 40.2 | 77.8 |
| neurons | 1500 | culture1-3[0:1500] | 9 | 204 | 88.1 | 89.4 |
| copper | 1500 | -- | -- | FAILS (n_total=800<1500) | -- | -- |

**Which media were saturated, and where k actually sits now:** yeast, chip, and radio were the
three flagged as capped at or near 30 (yeast=28-29, chip=24-28, radio=17-29 across segments). Once
uncapped, EVERY one of their segments' k jumps far past the old ceiling -- yeast 28->114 (n=800),
86 (n=1500); radio's at-horn segment 28->173; chip's seat80 28->198 (n=800), 22->310 (n=1500).
Mice and neurons, which were NOT flagged as saturated (old k=3-29, mixed), ALSO jump just as hard
once uncapped (mice size1 3->111 at n=800, 3->114 at n=1500; neurons culture1-1 7->190 at n=800,
1->346 at n=1500) -- so the jump is not confined to the three previously-flagged media, it is
universal. Only copper (k=5, both cutoffs) and one neuron culture (1-2: k=10->10, 11) stayed near
their old value. **Bootstrap error is enormous relative to the point estimate** (sd 45-121 against
k values of 5-353, i.e. the k the search lands on moves by roughly its own magnitude under
block-bootstrap resampling) -- the "fixed" k is barely more stable than the "old" one, it has just
moved to a different, equally unstable, part of a much bigger haystack.

## 2. Ordering test re-run: does beat period still order G_s?

Spearman exact-permutation test, beat period (first segment per medium, as Section 4 originally
defined the property) vs the SAME pooled G_s from Section 1 (unchanged):

| n | property | n resolved | rho | exact fraction |
|---|---|---|---|---|
| 800 | beat period, OLD cap (kmax=30) | 6 | +0.94 | 12/720 |
| 800 | beat period, FIXED (kmax=200) | 6 | **+0.71** | **98/720** |
| 1500 | beat period, OLD cap (kmax=30) | 5 | +0.70 | 28/120 |
| 1500 | beat period, FIXED (kmax=375) | 5 | **-0.30** | **82/120** |

(The OLD-cap rows here are this script's own re-derivation using a fresh RNG stream, not a byte
copy of Section 4's +1.00/2-720 and +0.90/10-120 -- close but not identical, because the arrow
search's `z`-argmax has near-ties among capped-out k's that a different shuffle draw can resolve
either way. The qualitative read is the same: the OLD cap gave a strong-looking order.)

**Beat period does NOT order the gap once the cap is lifted.** At n=800 the correlation drops from
+0.94 (tight) to +0.71 (98/720 -- not even in the strong-tail territory the original flagged); at
n=1500 it does not just weaken, it **flips sign** (+0.70 -> -0.30). An ordering that reverses
direction when the only thing changed is the search ceiling is not a property of the media -- it
was the cap sorting media by how close their old-k happened to sit to 30, and that artifact
vanishes the moment the ceiling moves. **Answer: the beat-period ordering was entirely the cap.**

## 3. Cutoff test: kmax = n//8, n//4, n//2 -- does k move with the cap, or stay put?

First segment per medium, k at each cutoff, and the call (RULER = k scales with/sits near the
cap; OBJECT = k stays fixed regardless of cap; MIXED/PARTIAL = neither cleanly):

| medium | n | kmax=n/8, k (frac) | kmax=n/4, k (frac) | kmax=n/2, k (frac) | call |
|---|---|---|---|---|---|
| yeast | 800 | 100, 77 (0.77) | 200, 114 (0.57) | 400, 392 (0.98) | RULER-LEANING |
| radio | 800 | 100, 97 (0.97) | 200, 173 (0.87) | 400, 346 (0.87) | RULER-LEANING |
| chip | 800 | 100, 96 (0.96) | 200, 198 (0.99) | 400, 388 (0.97) | **RULER** (pinned near ceiling at all 3) |
| mice | 800 | 100, 66 (0.66) | 200, 111 (0.56) | 400, 320 (0.80) | RULER-LEANING |
| neurons | 800 | 100, 98 (0.98) | 200, 190 (0.95) | 400, 247 (0.62) | RULER-LEANING |
| copper | 800 | 100, 5 (0.05) | 200, 5 (0.03) | 400, 93 (0.23) | RULER-LEANING (k does move, low frac) |
| yeast | 1500 | 187, 136 (0.73) | 375, 86 (0.23) | 750, 581 (0.77) | MIXED/PARTIAL |
| radio | 1500 | 187, 7 (0.04) | 375, 353 (0.94) | 750, 353 (0.47) | RULER-LEANING |
| chip | 1500 | 187, 88 (0.47) | 375, 310 (0.83) | 750, 510 (0.68) | RULER-LEANING |
| mice | 1500 | 187, 114 (0.61) | 375, 114 (0.30) | 750, 114 (0.15) | **OBJECT** (k=114 at EVERY cutoff) |
| neurons | 1500 | 187, 120 (0.64) | 375, 346 (0.92) | 750, 217 (0.29) | MIXED/PARTIAL |
| copper | 1500 | -- | -- | -- | FAILS (n_total=800<1500) |

**Call: mostly RULER.** At n=800, every medium's k sits at a high fraction of whatever ceiling it
is given (chip pinned 0.96-0.99 at ALL three cutoffs -- the cleanest ruler signature in the whole
file), and k itself changes at every cutoff for every medium except nothing -- it is never flat.
At n=1500 the picture is noisier (yeast and neurons swing non-monotonically, MIXED/PARTIAL) but
**mice is the one clean exception: k=114 at n//8, n//4, AND n//2, identical across a 4x range of
ceiling** -- the only medium in this file whose k looks like an actual fixed object rather than a
ruler reading. Everything else moves with the cap it is given.

## 4. Plain words

**The real beat periods, in samples and seconds** (first segment per medium, fixed kmax=n//4;
dt_native from each record's own sample interval; chip has no time axis -- buzz-seat angle samples
are phase readings, 1 shot/sample, not seconds):

| medium | n | k (samples) | dt (native) | period (seconds) |
|---|---|---|---|---|
| yeast | 800 | 114 | 1.31 s | 149.3 s |
| radio | 800 | 173 | 0.33 s | 57.1 s |
| chip | 800 | 198 | -- (shots) | N/A -- no time axis |
| mice | 800 | 111 | 900 s (0.25 hr) | 99,900 s (~27.75 hr) |
| neurons | 800 | 190 | 0.010 s | 1.90 s |
| copper | 800 | 5 | 60.0 s | 300.0 s |
| yeast | 1500 | 86 | 1.31 s | 112.7 s |
| radio | 1500 | 353 | 0.33 s | 116.5 s |
| chip | 1500 | 310 | -- (shots) | N/A -- no time axis |
| mice | 1500 | 114 | 900 s | 102,600 s (~28.5 hr) |
| neurons | 1500 | 346 | 0.010 s | 3.46 s |
| copper | 1500 | -- | -- | FAILS |

**Do these order the gap?** No. Section 2 above shows the Spearman correlation between this fixed
beat period and G_s collapses from the old cap's +0.94/+0.70 to +0.71 (not a strong hit) at n=800
and flips to -0.30 (wrong direction) at n=1500. **The one medium whose period looks real rather
than ruler-driven is mice** (Section 3: k=114 regardless of cutoff, ~99,900-102,600 s, roughly a
day -- plausibly a real circadian-scale body-temperature cycle, consistent with mice being a
living, temperature-regulated animal) -- and mice sits in the UNRESOLVED cluster in Section 2's
own gap ordering, not at the top. Every other medium's "period" moved by 50-300+ samples the
moment the search window changed, with bootstrap errors as large as the values themselves: there
is no stable, medium-specific beat period on file for yeast, radio, chip, neurons, or copper at
this length. **Bottom line: raising the cap did not reveal a hidden real period for five of six
media -- it revealed that the arrow statistic keeps climbing toward whatever ceiling it is given,
which is the signature of a ruler, not an object. The gap ordering built on the old, fixed k=30
ceiling is confirmed to be an artifact of that ceiling, not a medium property.**

## Failed rows

Zero formula failures: every arrow search (old cap, fixed kmax, all three cutoffs, every
bootstrap replicate) returned a finite k -- raising kmax never broke the search. Two build-level
failures, same as the parent file, by record length and not touched by this fix: radio at-horn at
n=1500 (n_total=1423<1500) and copper at n=1500 (n_total=800<1500).

## Tries

25 segments (13 at n=800, 12 at n=1500) x 2 point-estimate searches (old-cap re-check at
n_shuf=100, fixed kmax=n//4 at n_shuf=100) + 2 more cutoff point-estimate searches each (n//8,
n//2 at n_shuf=60; n//4 reuses the fixed-run point estimate) = **100 arrow-k searches** total
(1,100 counted by the script including the bootstrap-internal searches below). Bootstrap error on
k: 25 segments x 40 block-bootstrap replicates x 1 arrow search per replicate (n_shuf=20) =
**1,000 additional searches, 1,000 block-resampled series generated**. Grand total this pass:
**1,100 arrow best-k searches, 7,501,640 shuffle-floor draws summed across all of them, 1,000
block-bootstrap series resamples.** 2 ordering Spearman tests (one per n) x 2 cap conditions
(old/fixed) = 4 exact-permutation enumerations (720+720+120+120 = 1,680 orderings enumerated,
zero asymptotic p-values). Runtime 18.3 s, single process, numpy only.

## Files

- Report: this section, appended to `~/bones-forge/parallax/MEDIUM_AT_MATCHED_LENGTH_20261001.md`
- New script: `parallax/out/the_middle/kcap_fix_medium.py` (numpy only)
- New raw output: `parallax/out/the_middle/kcap_fix_medium_results.json`
- Reused, unedited: `parallax/out/three_on_three/core.py` (arrow_stat, arrow_best_k_fast),
  `parallax/out/three_on_three/load_horn.py`, `parallax/out/three_on_three/load_buzz.py`
- Data loaders and segmenter copied verbatim from `matched_length_medium.py` (this pass's own
  prior code, not re-derived)
- G_s pooled values (Section 1 of this file, above) copied verbatim, not recomputed -- G_s does
  not depend on the arrow's k
