# DISCO 2 LIGO -- steps 1-3 run, step 4 LOCKED (Bones, 2026-10-01)

Code: `out/disco2_ligo/disco2_ligo.py` (+ `out/disco2_ligo/fetch_data.py`). Results:
`out/disco2_ligo/steps123_results.json`. Pre-registration: `out/disco2_ligo/PREREG_LOG.txt`.
Reuses, by import, **unedited**: `out/darkwave_v1/darkwave_v1.py` (arrow, clock, split-(c), the
cutoff ladder), `out/disco2/disco2.py` (`cross_arrow_stat`), `out/three_on_three/core.py`
(`arrow_stat`, `fit_exp_decay`, `hilbert_envelope`), `out/yeast/three/split_v2.py`
(`candidate_a`, `candidate_b`, `candidate_c`, `naive_peaks_idx`). numpy/scipy/h5py/gwpy/gwosc,
single process, no multiprocessing. Full run: **26.5 s**, 0 runtime crashes/NaNs.

**Step 4 (opening the flagged data) was not run.** Step 2 found this file has no admissible
flagged-data trial at all (see below) -- this is reported, not worked around.

---

## WHERE IT BROKE AND WHY

| # | WHERE | WHY | WHAT IT MEANS |
|---|---|---|---|
| 1 | Step 2, flagged-seconds count | **Zero coincident flagged seconds.** H1_BURST_CAT3 flags 36 s (21 short glitch gaps) and L1_BURST_CAT3 flags 7 s (5 gaps) inside the 4096 s window, and CAT1/CAT2/CAT3 for both detectors flag **nothing at all** in this span (each is one unbroken "good" segment covering the whole 4096 s). The H1 and L1 BURST_CAT3 gaps never overlap in time anywhere in the file. | The darkwave arm as designed (coincident H1-L1 flagged stretches, stratified by flag class) has **no data to run on in this file, at all** -- not merely underpowered in the sense of a thin but nonzero sample. `p_min` is undefined (division by zero placements) for every class and overall. Step 4 is locked for an additional, stronger reason than "didn't fire the trigger": there is nothing to open. |
| 2 | Step 2, flag classification | GWOSC's public DQ segment lists for O1 (CAT1/CAT2/CAT3, BURST_CAT2/CAT3) are, by LIGO detchar construction, built from auxiliary/environmental/instrumental-state channels, safety-vetted against hardware injections specifically so they are *not* derived from the strain channel's own GW content. No public GWOSC timeline flag for this event is strain-derived (strain-based vetoes, e.g. search chi-squared cuts, are pipeline-internal and not published as timeline segments). So all five kept classes (CAT1/2/3, BURST_CAT2/3) are legitimately auxiliary; `*_DATA` (science-mode marker, not a quality veto) and the four `*_NO_*_HW_INJ` flags (hardware-injection absence markers, not quality cuts) were excluded as out of scope, logged with reasons in the JSON (`step2_flags.flags_excluded`). |
| 3 | darkwave_v1 / disco2, re-confirmed here | **Arrow is forced to flip sign exactly under reversal** (`arrow(x) + arrow(rev x) = 0` to ~1e-17, see unit tests). **Clock is forced reversal-invariant** (`clock(x) - clock(rev x) = 0` to ~1e-13). Both re-confirmed on H1, L1, and white noise. | Per DISCO2_HARNESS's own finding (breaks B/C there): any cross-witness "sign error" built from arrow or clock algebraically collapses to a forced, content-blind quantity. Only the split carries order-dependent information not already forced by the algebra -- this is why the split is the one pre-registered primary candidate, and why clock's injection table below reports no lag/sign recovery (N/A by construction, not a miss). |
| 4 | Step 3, split definitions (a) and (b) | Only split definition (c) (`candidate_c`, envelope-weighted time) is wired through the full darkwave cutoff ladder (`dw1.part_split`, imported verbatim). Definitions (a) (beat count) and (b) (Hilbert phase) are wired fresh in `disco2_ligo.py`, calling `sv2.candidate_a`/`candidate_b` verbatim, but **only at the raw (cutoff=1) rung**, scanned over a lag applied to L1 (step 4 samples, ±60 samples ≈ ±14.6 ms) rather than extended through the {1,2,3,5,8,13} ladder. | Scope limit, logged rather than hidden: the injection table's recovery rates for (a) and (b) reflect a single-rung, lag-scanned statistic, not the full ladder+Aitken machinery that (c) gets via `dw1.part_split`. This asymmetry is real and could favour (c) structurally; it does not appear to have (recovery rates for a/b/c are all low and close together -- see table below), but it is named as a possible confound in the primary choice, not swept under anything. |
| 5 | Step 3, floor control | **The floor control (same waveform, two off-source stretches of ONE detector) tracks the real two-detector injection's R_HL recovery curve almost exactly** (e.g. band 35-350 Hz, `published_lag_opposite_sign`: HL recovery 0.25/0.75/1.0/1.0 at SNR 5/10/20/40 vs floor 0.25/0.25/1.0/1.0). | This is expected, not a pipeline bug, but worth stating plainly: the injection method hand-codes the SAME deterministic lag/sign relationship into both "slots" regardless of whether the two slots are really H1+L1 or two H1 stretches, so at adequate SNR the measurement machinery (R_HL) reads that coded relationship back out of either pairing. The floor as built verifies the injection+measurement machinery is self-consistent; it does **not** test detector-pair specificity (a genuinely informative floor would need an independently-timed/independently-signed copy per slot, not a shared lag/sign code -- out of scope for this delivery, named here rather than silently claimed as a stronger floor than it is). |
| 6 | Step 3, chirp template | The injected waveform is a **Newtonian-order (leading order) inspiral chirp**, `f_low=35 -> f_isco=350 Hz`, `Mc=28 Msun`, Tukey-tapered -- a toy waveform in the same spirit as the toy chirps already used in FOR_SHUTTLE v3, not a full IMR template. Duration in-band ≈0.19 s, fits inside the 0.5 s on-source window. | Flagged so the injection recovery-rate numbers below are read as "this pipeline, on this toy signal shape," not as a claim about matched-filter performance against the true GW150914 waveform. |
| 7 | Step 3, SNR calibration | SNR is defined as `sqrt(sum(whitened+bandpassed template^2))`, the standard reduction of optimal matched-filter SNR to a simple norm once noise is whitened to ~unit variance per sample. Each detector's copy is independently normalized to the same nominal SNR using that detector's own ASD. | A real search would compute a joint network SNR and use the true PSD/response function; this is the correct order-of-magnitude approximation for a calibration run of this scope, named as such. |
| 8 | Step 3, primary readout | **None of the three split definitions reliably recovers lag+sign on the chirp injections, even at SNR 40** -- mean recovery rates pooled across bands/configs/SNRs: (a) 2.8%, (b) 3.5%, (c) 1.4% (n=36 each; chance-level tolerance window is ±3 samples out of a ±60-sample scan, i.e. ~5% by cell count alone, so none of the three clears even a naive chance floor convincingly). All three are within each other's spread (tie), so the tie-break falls to smallest spread: **(c)**. | This is written down as what it is: the primary readout was chosen because it has the smallest spread among three arms that all look close to chance on this metric, not because it demonstrably works. Per the no-promotion rule (quoted below), this makes a null step-4 result (were step 4 reachable, which per row 1 it is not) unsurprising and not informative either way. |
| 9 | Step 1, whitening | No failures. ASD fit on the first half of a held-out 297 s clean stretch (GPS 1126259646-1126259943, clear of all BURST_CAT3 gaps and of the event), variance checked on the untouched second half: H1 1.011, L1 1.025 (both within the ±0.15 tolerance declared before running). | Reported as a pass, not assumed; this is the only clean-held-out variance check run (one split per detector), named so the single data point isn't over-read as an exhaustive stability sweep. |

No crashes, no exceptions, no NaN-producing step anywhere in the run (`breaks` list in the JSON
from the live break-logger is empty; the rows above are additional honesty rows written by hand,
the same discipline DISCO2_HARNESS used for its "forced identity" and "scope limit" rows).

---

## 1. Step 1 -- unit tests

On 1 s (4096-sample) chunks: H1 (GPS 1126257464-1126257465, clean), L1 (same span), and seeded
white noise.

| series | arrow(x) | arrow(rev x) | sum | clock(x) (tau) | clock(rev x) | diff | both pass (machine precision)? |
|---|---|---|---|---|---|---|---|
| H1 | 4.416e-60 | -4.416e-60 | -5.66e-73 | 825.348469213015 | 825.348469213015 | 1.14e-13 | **YES** |
| L1 | 8.202e-59 | -8.202e-59 | 0.0 | 780.783766859735 | 780.783766859735 | 0.0 | **YES** |
| white noise (seed 0) | 0.009798 | -0.009798 | 1.73e-17 | 6390.490558518 | 6390.490558518 | 0.0 | **YES** |

Whitening variance (ASD fit on held-out first half of a 297 s clean stretch, variance checked on
the untouched second half, 148.5 s each):

| detector | fit window (s) | test window (s) | held-out variance |
|---|---|---|---|
| H1 | 148.5 | 148.5 | 1.0111 |
| L1 | 148.5 | 148.5 | 1.0249 |

All step-1 conditions pass. Step 1 did not stop the run.

---

## 2. Step 2 -- flagged-seconds count and power

Fetched: GWOSC 4096 s, 4096 Hz H1 + L1 strain, GPS [1126257414, 1126261510] (centred on GW150914,
1126259462.4), via `gwpy.timeseries.TimeSeries.fetch_open_data`. DQ/flag segment lists fetched via
the GWOSC timeline JSON API for the same span.

**Flags kept (auxiliary-channel-derived):** `{H1,L1}_CBC_CAT1`, `{H1,L1}_CBC_CAT2`,
`{H1,L1}_CBC_CAT3`, `{H1,L1}_BURST_CAT2`, `{H1,L1}_BURST_CAT3`.
**Flags excluded:** `{H1,L1}_DATA` (science-mode marker, not a quality veto), and the eight
`{H1,L1}_NO_{CBC,BURST,STOCH,DETCHAR}_HW_INJ` flags (hardware-injection-absence markers, not
quality cuts) -- reasons logged per-flag in the JSON.

| flag class | H1 flagged (s) | H1 gaps | L1 flagged (s) | L1 gaps | **coincident** flagged (s) | 0.5 s placements available | p_min |
|---|---|---|---|---|---|---|---|
| CBC_CAT1 | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| CBC_CAT2 | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| CBC_CAT3 | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| BURST_CAT2 | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| BURST_CAT3 | 36 | 21 | 7 | 5 | **0** | 0 | undefined |
| **overall** | | | | | **0** | **0** | **undefined (worse than >= 0.002)** |

**STATUS: UNDERPOWERED.** Not "thin but present" -- zero coincident flagged seconds across every
kept class, in this particular 4096 s file. (GW150914's on-source data happens to be unusually
clean: this is a well-known, scientifically clean event, so this null result about the *flag
overlap* is itself expected, not a tooling failure.) **Step 4 is not run, for this reason alone,
independent of the §0 read.**

---

## 3. Step 3 -- pipeline calibration

**Bands used** (all >= 35-200 Hz wide, per v4/v5): **35-350 Hz, 35-250 Hz, 50-300 Hz.**
Whitening: FFT-domain division by an ASD estimated (Welch, 4 s segments, 50% overlap) from a
297 s clean, science-quality stretch (GPS 1126259646-1126259943, clear of all kept flags and of
the event), rescaled by one calibration constant so that stretch's own whitened variance is 1
(then held out tested per step 1). The identical bandpass (4th-order Butterworth, `sosfiltfilt`)
is applied to both detectors at each band. Analytic-signal/Hilbert-based quantities (split
definition (b)'s phase) are computed on the long whitened+bandpassed stretch before any window is
cut. H1 and L1 are always cut at the **same GPS times**; on-source window = 0.5 s centred on
1126259462.4.

### 3a. R_HL -- real on-source event, all three bands

| band | recovered lag (samples) | recovered lag (ms) | sign | pass (27-31 samples, opposite sign)? |
|---|---|---|---|---|
| 35-350 Hz | -30 | -7.32 | **-1** | **PASS** |
| 35-250 Hz | -30 | -7.32 | **-1** | **PASS** |
| 50-300 Hz | -30 | -7.32 | **-1** | **PASS** |

All three bands recover **L1 leading H1 by ~30 samples, opposite sign** -- matching the expected
~28-29 samples within the stated pass/fail-on-sign-only rule. (Pass/fail is on sign per v4; the
1-2 sample offset from the oft-quoted 28.67 is within the resolution of a coarse-band, Butterworth
-filtered, non-matched-filter R_HL scan and is not treated as a failure.)

### 3b. Time slides on clean data (background for R_HL's own statistic)

400 non-overlapping 0.5 s L1 placements per band, offsets multiples of 0.5 s with
|offset| in [1 s, 1800 s] (far beyond the ±15 ms R_HL window), H1 held at the real on-source GPS,
both ends required clear of BURST_CAT3 gaps and the PSD segment.

| band | null mean (max\|R_HL\|) | null max | real event's max\|R_HL\| | rank from top | empirical tail p |
|---|---|---|---|---|---|
| 35-350 Hz | 0.0281 | 0.0459 | 0.1236 | 0 / 400 | **0.0** |
| 35-250 Hz | 0.0239 | 0.0458 | 0.1114 | 0 / 400 | **0.0** |
| 50-300 Hz | 0.0243 | 0.0525 | 0.1021 | 0 / 400 | **0.0** |

The real event sits at rank 0 in all three bands -- above every one of 400 slid nulls, by a factor
of ~2-3x even the null's own maximum. Reported as an empirical tail (0/400), never as a Gaussian
sigma.

### 3c. Injections -- recovery rate of lag + sign, by arm

Chirp (Newtonian inspiral toy, 35-350 Hz in-band, Mc=28 Msun, ~0.19 s), 3 configs x 4 SNRs x 4
trials x 3 bands, injected into clean off-source H1+L1 pairs (config lag/sign applied to L1's
copy), plus a floor run (same config, both copies into H1 alone at two different off-source
times). Table below: band 35-350 Hz (the other two bands tell the same story; full per-band/
per-config numbers are in the JSON).

| config | SNR | R_HL recovery | split (a) | split (b) | split (c) | clock | hunter | strain arrow |
|---|---|---|---|---|---|---|---|---|
| published (lag+opp. sign) | 5 | 0.25 | 0.0 | 0.0 | 0.25 | N/A (sign-blind) | N/A (rank only) | N/A (readout OPEN) |
| published | 10 | 0.75 | 0.0 | 0.0 | 0.0 | N/A | N/A | N/A |
| published | 20 | **1.0** | 0.0 | 0.0 | 0.0 | N/A | N/A | N/A |
| published | 40 | **1.0** | 0.0 | 0.0 | 0.0 | N/A | N/A | N/A |
| same lag, same sign | 5 | 0.0 | 0.0 | 0.25 | 0.0 | N/A | N/A | N/A |
| same lag, same sign | 20 | **1.0** | 0.25 | 0.0 | 0.0 | N/A | N/A | N/A |
| same lag, same sign | 40 | **1.0** | 0.0 | 0.0 | 0.0 | N/A | N/A | N/A |
| zero lag | 20 | **1.0** | 0.0 | 0.0 | 0.0 | N/A | N/A | N/A |
| zero lag | 40 | **1.0** | 0.25 | 0.0 | 0.0 | N/A | N/A | N/A |

**Pooled across all bands/configs/SNRs (n=36 cells each): split (a) mean recovery 2.8% (spread
7.9 pts), (b) 3.5% (spread 8.6 pts), (c) 1.4% (spread 5.7 pts).** R_HL climbs cleanly from ~0.25
at SNR 5 to 1.0 by SNR 20-40 in every config and band -- the pipeline's baseline cross-correlation
works exactly as expected. **None of the three split definitions shows a reliable lag/sign
recovery at any tested SNR**, including SNR 40. Clock and hunter have no lag/sign readout by
construction (clock is reversal-even/sign-blind; hunter reports a rho-distance rank, not a
lag/sign call) -- reported as context (tau ratios, rho distances) in the JSON, not forced into a
recovery-rate cell. Strain arrow's readout rule is declared OPEN per v5: the whole lag curve
(`cross_arrow_stat`, scanned ±60 samples) is in the JSON for every trial; no argmax verdict and no
recovery rate is computed for it, by design.

**Floor (same waveform, two off-source H1 stretches alone):** R_HL's recovery curve on the floor
is essentially identical to the real H1+L1 curve (e.g. published config: 0.25/0.25/1.0/1.0 at SNR
5/10/20/40 vs the real pair's 0.25/0.75/1.0/1.0). As row 5 above states plainly: this confirms the
injection+measurement machinery is self-consistent, not that the pipeline is insensitive to
detector identity -- the lag/sign relationship is coded into the injection itself regardless of
which two noise stretches it lands in.

### 3d. Primary readout choice (pre-registered before step 4, which is not reached anyway)

Per v5 §2's tie-break: best mean recovery, tie within combined spread -> smallest spread, tie on
spread -> (a). All three split definitions tied within each other's spread; **(c)** has the
smallest spread (5.7 pts vs 7.9/8.6) and is the logged primary. Full log, written before anything
touches flagged data, in `out/disco2_ligo/PREREG_LOG.txt`:

> PRIMARY READOUT CHOSEN: split definition (c)
> REASON: tied within spread among ['a', 'b', 'c']; smallest spread is (c)
>
> This is a valid pre-registration of an arbitrary choice; definition (c) was favoured in V1
> partly on results.
>
> No-promotion rule, verbatim: "If the primary readout is null and a secondary readout is
> significant, the result is null."
>
> [§0's YES and NO clauses copied verbatim from FOR_SHUTTLE_FIRING_V5_20261001.md -- see the log
> file for the full text]
>
> THIS LOG WAS WRITTEN BEFORE ANYTHING TOUCHED FLAGGED DATA. Step 2's flagged-seconds count,
> computed independently, found ZERO coincident flagged seconds... Step 4 is not run regardless
> of the choice logged above.

---

## 4. Bottom line

- **Step 1: all unit tests pass**, to machine precision, on H1, L1, and white noise; held-out
  whitened variance is within tolerance on both detectors.
- **Step 2: UNDERPOWERED**, and more specifically **zero** coincident auxiliary-flagged seconds
  in this 4096 s file across every kept flag class -- there is no admissible stratified-slide
  trial to run step 4 on here at all.
- **Step 3: the pipeline itself is sound** -- R_HL recovers the known ~29-sample, opposite-sign
  L1-leads-H1 relationship in all three bands on the real event, and the real event sits at rank
  0 of 400 time-slid nulls. R_HL also recovers injected lag+sign cleanly by SNR 20 in every
  tested configuration. **The framework's own primary candidate (the split, any of its three
  definitions) does not show a working lag/sign recovery on these injections at any SNR tested**,
  and the primary readout (c) was chosen only because it has the smallest spread among three
  near-chance arms, not because any of them works. Per the no-promotion rule, a null reading from
  (c) on real data (were step 4 reachable) would not be rescued by a better-looking secondary
  arm.
- **Step 4 is not run.** Both because step 2 forecloses it for this file (zero coincident flagged
  time) and because the task stops here regardless.

Files: `out/disco2_ligo/disco2_ligo.py`, `out/disco2_ligo/fetch_data.py`,
`out/disco2_ligo/data/{H1,L1}_4096s.hdf5` + `fetch_manifest.json`,
`out/disco2_ligo/steps123_results.json`, `out/disco2_ligo/PREREG_LOG.txt`.
