# CLOSE THE FREE ONES — the four zero-cost closing tests from THE_PROOF_SHAPE, 2026-09-30

Bones's field hand. No expectation written before running any script. Raw numbers first, every test counted,
background stated for every claim, no binary splits. Scripts: `parallax/out/close_free/*.py`. Raw JSON output
sits next to each script. Single process throughout; no quantum runs, no money, one ssh check to the laptop
that turned out to be unnecessary (the copper data pull already lives on this Mac at
`parallax/out/copper_nodes/data/`, identical file the RECURSIVE_GRADIENT pass already used).

---

## 1. RIGETTI CARRY CLOCK (row 4) — STILL OPEN, no time constant fittable; lag-structure only

**Raw check on the timing question first.** Read `rigetti_chip.py` (the actual submission script behind
`run.npz`/`blink.npz`) directly. Every `shuffle` task (`e,a,b,ab,ba,aba,bb,bab`) is ONE Braket task of 5000
shots run back-to-back at the hardware's fixed native shot cadence — no swept wait/gap parameter exists inside
a shuffle series. The only `wait_us` knob in the whole dataset is the separate `blink` stage's single
before/after pair (0 vs 60us, a one-shot snapshot, not a sweep). **Conclusion: Rigetti's data carry no
inter-shot timing structure analogous to Marrakesh's 20/50/100/250/500/1000/2000us gap sweep.** No real-time
carry-clock fit (no tau, no bootstrap band) is possible from this dataset — forcing one would mean inventing a
timescale the data don't have. Reported instead: lag-structure only, in units of shots.

**Method check.** Recomputing q0's rung-2 group from raw `run.npz` reproduces THE_PROOF_SHAPE's cited numbers
exactly at lag-1: combined `ab+aba+bab` → nff=64 vs exp=88.03 (ratio 0.73); `aba+bab` only → nff=25 vs exp=42.70
(ratio 0.59). This confirms the extraction is right before extending it.

**Lag-1/2/3, q0 rung-2 group (success leaves |2>), from the same raw shot arrays:**

| group | lag | nf (trials) | nff (observed) | exp_ff (independence) | ratio | z | p (two-sided) |
|---|---|---|---|---|---|---|---|
| ab+aba+bab | 1 | 1129 | 64 | 88.03 | 0.727 | −2.37 | 0.018 |
| ab+aba+bab | 2 | 1129 | 84 | 88.03 | 0.954 | −0.12 | 0.906 |
| ab+aba+bab | 3 | 1129 | 79 | 88.03 | 0.897 | −0.68 | 0.495 |
| aba+bab only | 1 | 653 | 25 | 42.70 | 0.585 | −2.79 | 0.005 |
| aba+bab only | 2 | 653 | 37 | 42.70 | 0.866 | −0.89 | 0.372 |
| aba+bab only | 3 | 653 | 31 | 42.70 | 0.726 | −1.84 | 0.065 |

Chip-wide (all pushed qubits, same rung-2 grouping, for shape comparison): lag-1 ratio 1.003, lag-2 1.005, lag-3
1.006 — flat, no deficit at any lag (q0 is specific, the chip average is not).

**Reading it.** q0's rung-2 leak is a *deficit* (fewer fail-after-fail than independence predicts), not an
excess like Marrakesh's carry — opposite sign from the object row 4 was trying to match against. It is
strongest and significant at lag-1 (z=−2.37/−2.79, p=0.018/0.005) and fades toward the chip's flat 1.00 ratio by
lag-2 (p=0.91/0.37) and lag-3 (p=0.50/0.065, the aba/bab-only lag-3 is the closest of the fading tail to
significance but still short of it). **Shape verdict: it decays away within about 2-3 shots, the same qualitative
"gone within a few steps" shape as Marrakesh's 63.8us exponential, but on an axis (shot count) that cannot be
converted to microseconds from anything on disk, and with the opposite sign of effect.** Not the same
measured object as Marrakesh's; a genuine but different, unexplained short-lag anti-correlation.

**Tries:** 18 distinct statistical tests (3 seqs × 3 lags for q0 per-sequence arrays, computed as an
intermediate step; 2 groupings × 3 lags for the combined/deep q0 tests; 3 lags chip-wide) = 9 + 6 + 3 = 18, each
drawn from the full raw shot arrays already on disk (no new shots).

**CLOSED / STILL OPEN: STILL OPEN.** No carry-clock (tau) exists to fit — the data don't carry the timing
knob the test needed. What's added: q0's rung-2 leak is now characterized at lag-1/2/3 (not just lag-1), shown
to be a *decaying deficit*, distinct in sign from Marrakesh's carry, chip-wide-null-confirmed as q0-specific.
The mechanism itself remains unexplained.

---

## 2. OBSERVER_WITNESS PAIR 1, CLOUD-BLIND (row 40) — STILL OPEN, sharper but not adjudicated

**Data.** 12 seat-offset dots total (`phase_seats.json`, `J_seatdiff`): J1 has 6 (3 per cloud), J2/J3/J4 have 2
each (1 per cloud). True 0-cloud job means (deg): d80 = [16.4, 18.2, 17.4, 13.8], spread 1.92; d100 = [−77.9,
−74.3, −77.3, −74.9], spread 1.79. True 1-cloud: d80 spread 6.11, d100 spread 3.41 (all matching
OBSERVER_WITNESS_20260930.md exactly — pipeline check passed).

**Cloud-blind rerun.** For each job, randomly draw (without replacement) the SAME COUNT of that job's own dots
as the true 0-cloud count for that job — i.e., forget which pub (p0/p1/p2/p3) produced each dot, keep only the
job-level group sizes — 1000 draws, both resulting random bins pooled (n=2000 bin-draws).

- Cloud-blind random-bin spread: d80 mean 13.00° (sd 3.79°), d100 mean 68.41° (sd 19.17°) — an order of
  magnitude looser than either true cloud's spread.
- P(a cloud-blind random bin is at least as tight as the observed 0-cloud spread) = **0.006** for both d80 and
  d100 (6/2000 draws).
- Contrast, same test against the 1-cloud spread: P = 0.051 (d80), 0.012 (d100).

**Reading it, plainly.** A random bin that mixes true-0-cloud and true-1-cloud dots together is almost never as
tight as the real 0-cloud grouping (p=0.006) — because the two clouds sit on genuinely different absolute
offset scales (0-cloud ~14-18°, 1-cloud ~40-53° for d80; opposite-signed for d100), so mixing them inflates
variance by construction. **This means the tight cross-job lock does NOT survive if the cloud label is thrown
away — you cannot reconstruct 0-cloud's tightness from an arbitrary same-sized grouping of the pooled dots.**
That is expected once you know the two clouds carry different fixed offsets (already established in THE_BUZZ.md
§3, cited in the design note); it does not, by itself, separate "seats genuinely lock together within the
0-cloud" from "0-cloud readout is intrinsically lower-variance for a reason unrelated to inter-seat locking
(e.g., proximity to a fixed point in the readout basis)" — a possible confound this test was not built to rule
out. The report's own earlier caveat ("design flaw or real physics not adjudicated") stands.

**Tries:** 1000 draws × 2 bins (A/B) = 2000 cloud-blind spread computations, per column (d80, d100) = 4000 total
random-bin evaluations, plus 4 observed-vs-null comparisons (p-values).

**CLOSED / STILL OPEN: STILL OPEN.** The requested cloud-blind test ran cleanly and adds a real number
(p=0.006: the tightness needs the true cloud label to reconstruct), but it does not adjudicate the open
question posed by the record itself — real seat-lock vs. an artifact of the 0-cloud state's own readout
geometry. That would need a different control (e.g., an independent 0-cloud-only readout-noise-floor estimate),
outside this pass's scope.

---

## 3. OBSERVER_WITNESS PAIR 3, GW170814 ANCHOR (row 42) — STILL OPEN, does not move toward 97/3

Two independent anchors built for GW170814 (H1, L1 — V1 excluded per BLACK_STACK_2's own "weak correlation"
finding), and the same pipeline run on GW150914 for a same-method comparison.

**Anchor A — the data's own whitened peak**, pass4's exact method (`find_data_peak_index`), 3 cutoffs per
detector, no template involved:

| event | det | narrow_30_300 offset from PE-predicted (ms) | wide_20_500 (ms) | wide_20_1000 (ms) |
|---|---|---|---|---|
| GW170814 | H1 | −16.12 | −13.19 | +42.72 |
| GW170814 | L1 | −18.16 | −18.16 | −33.79 |
| GW150914 | H1 | −13.98 | −16.66 | −37.90 |
| GW150914 | L1 | −13.84 | −13.84 | +42.07 |

Re-split (18 conventions × 2 detectors) against Anchor A, per detector:

| event | det | shared (ms) | per-run sd (ms) | SHARED % | PER-RUN % |
|---|---|---|---|---|---|
| GW170814 | H1 | +19.42 | 4.18 | 78.5% | 21.5% |
| GW170814 | L1 | −7.37 | 3.99 | 45.9% | 54.1% |
| GW150914 | H1 | −7.42 | 0.51 | 93.1% | 6.9% |
| GW150914 | L1 | +20.02 | 0.44 | 97.8% | 2.2% |

Pooling H1+L1 is not usable for either event — the two detectors' Anchor-A shared terms have opposite signs
(driven by cutoff-dependent noise peaks, e.g. GW170814 H1's wide_20_1000 cutoff grabs a +42.7ms outlier), so a
pooled percentage becomes a meaningless negative number. Per-detector is the only valid read.

**Anchor B — matched filter, PE-default convention (f_ref=20, phase_as_stored, peak_amplitude alignment)**,
i.e. one of the 18 sweep rows itself used as the zero-point (already computed in `convention_sweep_results.json`,
reused not rerun): this is **circular by construction** — using a sweep point as its own reference forces
shared≈0, so per-run dominates (98-300%) for BOTH events equally. It confirms nothing new and is reported here
only because it was asked for; it has no discriminating power for this split.

**Reading it.** Using the only non-circular anchor (A, the data's own peak), GW150914's per-detector split
(93-98% shared) is close to its official-template-anchored 96.9%/3.1% — a good consistency check on the method.
GW170814's per-detector split (78.5%/21.5% H1; 45.9%/54.1% L1) does **not** move toward GW150914's number under
this anchor — L1 in particular has a WORSE (more per-run) split than the original global 74/26 estimate that
prompted this test.

**Tries:** 2 anchors × 2 events × 2 detectors × 18 conventions = 144 re-split computations, plus 12 data-peak
extractions (2 events × 2 detectors × 3 cutoffs) for Anchor A.

**CLOSED / STILL OPEN: STILL OPEN.** Two independent anchors built; neither moves GW170814 toward GW150914's
tight split — if anything L1 alone looks less resolved (54% per-run) than the original combined estimate. The
per-run term is real and anchor-choice-robust, not an artifact of lacking an official template; the open
neighbor (GW170814's larger, unexplained per-run share) stands, now on firmer footing rather than closed.

---

## 4. RECURSIVE GRADIENT frac(fwd>bwd) FLOOR (row 43) — CLOSED, consistent with noise

Built the missing floor: 1000 shuffles per series (not the mean-gradient's existing 200), specifically for the
`frac(fwd>bwd)` statistic itself, all 4 copper bins, all 3 memories (n=226 minute-samples per series, identical
file `parallax/out/copper_nodes/data/data.jsonl` the original pass used — no laptop pull needed, already local).

| Hz (actual bin) | mem | observed frac(fwd>bwd) | 1000-shuffle floor | null mean / sd | empirical p (two-sided) |
|---|---|---|---|---|---|
| 300 (300.41) | 0.5 | 0.527 | [0.460, 0.544] | 0.502 / 0.022 | 0.363 |
| 300 | 0.1 | 0.500 | [0.385, 0.602] | 0.499 / 0.057 | 1.000 |
| 300 | 0.02 | 0.350 | [0.000, 1.000] | 0.496 / 0.301 | 0.586 |
| 212 (211.72) | 0.5 | 0.487 | [0.456, 0.540] | 0.501 / 0.021 | 0.591 |
| 212 | 0.1 | 0.535 | [0.385, 0.624] | 0.499 / 0.061 | 0.540 |
| 212 | 0.02 | 0.850 | [0.000, 1.000] | 0.485 / 0.309 | 0.332 |
| **200 (200.27)** | 0.5 | 0.491 | [0.456, 0.544] | 0.499 / 0.022 | 0.785 |
| 200 | 0.1 | 0.438 | [0.385, 0.615] | 0.501 / 0.059 | 0.321 |
| **200** | **0.02** | **0.018** | **[0.000, 1.000]** | 0.506 / 0.324 | **0.098** |
| 12 (12.40) | 0.5 | 0.474 | [0.456, 0.544] | 0.500 / 0.023 | 0.287 |
| **12** | **0.1** | **0.389** | [0.381, 0.615] | 0.500 / 0.060 | **0.071** |
| 12 | 0.02 | 0.049 | [0.000, 1.000] | 0.516 / 0.309 | 0.201 |

**Raw finding.** At the fastest memory (0.02) the naive 2.5th/97.5th-percentile floor saturates to [0.000, 1.000]
for every series (the long-memory EMA makes the shuffled null itself bimodal/extreme, so the percentile-band
floor is uninformative there by construction) — this is exactly why a floor built specifically for this
statistic, not just outside-band membership, was needed. Using the empirical two-sided p-value against the null
distribution's shape instead: **200Hz's flagged extreme (0.018 at mem=0.02) gives p=0.098; 12Hz's flagged
extreme (0.049 at mem=0.02) gives p=0.201.** Neither clears p<0.05. The next-closest candidate, 12Hz at mem=0.1
(0.389), gives p=0.071 — also short. 300Hz and 212Hz sit well inside their floors at every memory (p≥0.29 for
mem 0.5/0.1; the mem=0.02 floor is uninformative for all four by the same saturation).

**Tries:** 4 series × 3 memories × 1000 shuffles = 12,000 shuffle draws (12 series×memory cells).

**CLOSED / STILL OPEN: CLOSED.** With its own floor built, 200Hz's and 12Hz's frac(fwd>bwd) extremity is a
measured null (p=0.098 and 0.201, neither significant) against an explicit 1000-shuffle background — the loose
end ("flagged, not claimed") is now measured-explained as ordinary scatter from a long-memory EMA's own null
distribution shape, not a real directional signal.

---

## Counts, this pass

- **CLOSED:** 1 of 4 (row 43, frac(fwd>bwd) floor).
- **STILL OPEN:** 3 of 4 (row 4, no timing knob to fit — lag-structure characterized instead; row 40, cloud-blind
  test sharpens but doesn't adjudicate; row 42, two independent anchors built, neither closes the gap).
- **Total tries across all four tests:** 18 (row 4) + 4000 (row 40, random-bin draws) + 144 (row 42, re-splits)
  + 12,000 (row 43, shuffle draws) = **16,162** counted statistical draws/tests, on data already on disk, single
  process, no money spent.
