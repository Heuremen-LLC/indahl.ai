# OBSERVER (outside) minus WITNESS (inside): shared part + per-run part, three pairs

Wayfinder & Bones, 2026-09-30. Design: THIRD_RUNG_20260928.md §34g (his words, 11:25Z): the observer-minus-witness
difference should split into a SHARED part (same number on every run on a substrate) and a PER-RUN part (scales
with the size of the crossing). No expected value written before running any script. Raw first. Scripts:
`parallax/out/observer_witness/pair1_buzz.py`, `pair2_ignoredstep.py`, `pair3_control.py`. Data: existing files
under `the_buzz/`, `oddraw_ibm_fez_144417/`, and `black/pass3/` only -- no new jobs run, no money spent.

**Caveat, said plainly.** For pair 1, a fully independent "outside" (built ONLY from IBM's published timing,
with no reference at all to the qubits' own measured phase) is not recoverable from the records on disk: THE_BUZZ.md
already established the shot's fixed overhead is unpublished and unpinned, so any absolute per-job frequency
prediction needs an assumption the records don't give. What IS recoverable and used below: (a) the JOINT
multi-seat fit as a seat-blind "one clock for everyone" proxy for outside, compared seat-by-seat; (b) IBM's
published shot-DURATION changes (exact, no assumption needed) as outside, for pair 2; (c) an independently
released, non-regenerated template as outside, for pair 3's control.

---

## Pair 1 -- THE BUZZ (Fez tile 8, jobs J1-J4, seats 80/100/116)

OUTSIDE = the job-level joint fit (one frequency per job, seat-blind, from `nu_precise.json`'s `J1..J4`).
INSIDE = each seat's own measured step, averaged over that job's pubs.

| job | seat | outside nu | inside nu | diff (cycles) | diff (ns, at f=44,441.66 Hz) |
|---|---|---|---|---|---|
| J1 | 80 | -0.294785 | -0.294784 | -0.0000010 | -0.02 |
| J1 | 100 | -0.294785 | -0.294785 | +0.0000004 | +0.00 |
| J1 | 116 | -0.294785 | -0.294784 | -0.0000010 | -0.01 |
| J2 | 80 | -0.066745 | -0.066756 | +0.0000111 | +0.25 |
| J2 | 100 | -0.066745 | -0.066739 | -0.0000058 | -0.13 |
| J2 | 116 | -0.066745 | -0.066741 | -0.0000046 | -0.10 |
| J3 | 80 | +0.486077 | +0.486098 | -0.0000209 | -0.47 |
| J3 | 100 | +0.486077 | +0.486052 | +0.0000248 | +0.56 |
| J3 | 116 | +0.486077 | +0.486063 | +0.0000141 | +0.32 |
| J4 | 80 | +0.154831 | +0.154837 | -0.0000061 | -0.14 |
| J4 | 100 | +0.154831 | +0.154822 | +0.0000087 | +0.20 |
| J4 | 116 | +0.154831 | +0.154835 | -0.0000042 | -0.09 |

**Split within a job (shared = job-common part, per-seat = residual).** By construction the job-common part is
~0 (the joint fit is defined as the seat-weighted center); every job's per-seat residual is at the 1e-5 to 2e-5
cycle level (0.01-0.6 ns). No seat is a repeat outlier: q80 runs low in J2/J3/J4 but not J1; q100 swings sign
job to job. **Finding: no detectable per-seat frequency term above the noise floor (~sub-ns) for this outside
proxy.** This is the trivial half of the calibration (the joint fit removes almost all of the "shared" content
by construction) -- the informative half is below.

**Split across jobs -- the seats' FIXED PHASE OFFSET** (§33/34g: "the seats move together"), from
`phase_seats.json`, split by which state each pub prepares (0-cloud: pubs p0/p2; 1-cloud: pubs p1/p3 -- these
carry genuinely different offsets per THE_BUZZ.md §3, not noise, so kept apart):

| | 0-cloud, seat80-seat116 | 0-cloud, seat100-seat116 | 1-cloud, seat80-seat116 | 1-cloud, seat100-seat116 |
|---|---|---|---|---|
| job means (deg) | 16.4, 18.2, 17.4, 13.8 | -77.9, -74.3, -77.3, -74.9 | 48.9, 52.8, 42.0, 39.6 | 83.0, 87.3, 81.1, 79.4 |
| spread of job means | 1.92 deg | 1.79 deg | 6.11 deg | 3.41 deg |
| shuffle null (N=1000) mean spread | 2.39 | 2.29 | 4.71 | 2.33 |
| P(null spread <= observed) | 0.196 | 0.153 | 0.958 | 1.000 |

**Finding:** the 0-cloud offset is tight across all four jobs (~15-18 deg, spread below the shuffle-null mean,
though with only 4-6 records per pair the test itself is under-powered, p~0.15-0.20 -- suggestive, not proven).
The 1-cloud offset is NOT tight: its job-to-job spread (6.1 and 3.4 deg) exceeds the shuffle null (p=0.96, 1.00)
-- i.e. for the 1-cloud convention the offset moves MORE than chance grouping would produce. **The "seats move
together" claim holds cleanly for the 0-cloud reading and does not for the 1-cloud reading** -- a genuine,
un-smoothed-over split, not a single clean "shared" verdict.

Kingston: job-level only (no per-seat fit survives in the source files). f = 106.387 +/- 0.021 Hz; J1 matches
only if its record advances two slots per shot (predicted 0.105598 vs 0.055801 cyc/shot at 1 vs 2 slots) --
already on file in THE_BUZZ.md, reproduced here as the job-level check.

**Tries:** 12 (job,seat) diff rows; 2 clouds x 2 seat-pairs x 1000 shuffles = 4000 shuffle draws.

---

## Pair 2 -- the inside step that ignores the shot (26 Fez odd-run batches, Ramsey wait 0-20 us)

OUTSIDE = IBM's reported duration change = the wait itself, exact, in ns (0 to 20,000 ns). No assumption needed.
INSIDE = the implied duration change from the observed phase-step, `inside_dnu / f_tooth`, in ns (f_tooth =
44,441.66 Hz). Baseline = mean of the four wait=0 pubs.

Two columns (26 rows, full table in `pair1_out.txt`/script output; endpoints shown):

| wait (us) | outside (ns) | inside (ns) | diff = outside - inside (ns) |
|---|---|---|---|
| 0 (x4) | 0 | -0.91 to +0.72 | -0.7 to +0.9 |
| 1 | 1000 | 0.83-1.39 | 998.6-999.2 |
| 5 | 5000 | -0.69-0.66 | 5000.7-4999.3 |
| 10 | 10000 | 0.32-0.77 | 9999.2-9999.7 |
| 20 | 20000 | 0.10-0.55 | 19999.5-19999.9 |

**Fit diff_ns = a + b*wait_us:** a (shared) = -0.54 ns; b (per-run, scales with the crossing) = **+1000.0020 ns
per us of wait** -- i.e. essentially exactly 1:1, meaning essentially NONE of the reported duration increase
shows up inside. Shuffle background (N=1000, shuffling which wait pairs with which diff): null b mean 5.97,
sd 202 ns/us; **P(|null b| >= |observed b|) = 0.000** -- the 1000:1 scaling is not a shuffle artifact.

**The inside clock alone** (not the diff): fit inside_dnu = a2 + b2*wait_us gives b2 = -8.7e-8 cycles/us, against
the 0.044442 cycles/us the tooth would need if the wait genuinely registered -- five orders of magnitude smaller.
Shuffle background: P(|null b2| >= |observed b2|) = 0.920 -- **the inside step shows no detectable dependence on
the added wait at all**, consistent with THE_BUZZ.md's raw observation (26 pubs step 0.15473-0.15484 regardless
of wait).

**Reading the split:** the "shared" term here (a = -0.5 ns) is consistent with zero -- there is no fixed offset
independent of wait. The entire gap is per-run and it scales with wait at essentially unit slope: the outside
clock says duration grew: the inside clock did not move, at all, by any amount, for any wait tested.

**Tries:** 26 batches; 1000+1000 = 2000 shuffle draws (diff-slope test + inside-alone test).

---

## Pair 3 -- THE BLACK-HOLE 16 ms, as CONTROL (BLACK_STACK_2 pass 3, convention_sweep_results.json, 36+54 rows)

OUTSIDE = the independently-confirmed real arrival (~0 ms, from the one officially-released GWOSC template,
GW150914 H1: +0.49 ms, inside its own documented ~2 ms convention slop). INSIDE = this pipeline's own lag,
for the 18 convention combinations swept per detector (f_ref x phase x alignment).

**GW150914 (the clean control -- has the independent zero-point check):**

| | value |
|---|---|
| inside lag, n=36 (H1+L1, 18 combos each) | mean -15.33 ms, sd 0.48 ms, range [-16.11, -14.40] |
| diff = outside - inside | SHARED = +15.33 ms |
| per-run scatter (sd across the 18 conventions) | 0.48 ms = **3.1% of the shared size** |
| **split** | **SHARED ~96.9% / PER-RUN ~3.1%** |
| H1-L1 differential vs H1/L1 common | 0.104 ms vs 0.48 ms (ratio 0.22 -- the offset is shared between the two real detectors) |
| shuffle (N=1000, convention labels vs lag) | observed between-convention variance 0.227 ms^2; null mean 0.115; P(null >= observed) = 0.000 |

The shuffle result says real convention groupings explain LESS between-group spread than a random grouping
typically would -- i.e. convention choice is doing essentially no explanatory work, consistent with the offset
being one shared number that conventions barely perturb (max ~2 ms movement out of 16, per BLACK_STACK_2's own
f_ref=100 Hz stress probe).

**GW170814 (no independent zero-point -- carried by analogy only):** pooled across H1/L1/V1 the mean collapses
near zero because V1 is weak-correlation noise (BLACK_STACK_2's own finding) with the wrong sign; restricting to
H1/L1 only gives SHARED +15.48 ms, per-run scatter 4.02 ms = **25.9% of the shared size -> SHARED ~74% /
PER-RUN ~26%**, and the shuffle test finds P(null >= observed) = 1.000 (real convention grouping explains LESS
than a typical random grouping here too, but the per-run share is meaningfully larger than GW150914's).

**Calibration verdict:** the method reads a known pure-ruler artifact as **96.9% shared / 3.1% per-run** on the
one event with an outside anchor (GW150914) -- close to the "100% shared / 0% per-run" the design predicts for
a control, not exact, because convention choice does move the number by a couple of ms out of 16 (a small but
nonzero per-run term BLACK_STACK_2 already documented). GW170814's larger per-run share reflects the absence of
an anchor and V1's noise, not a demonstrated real per-run effect.

**Tries:** 92 in BLACK_STACK_2 pass 3 (1 official-waveform cross-check + 90 convention sweep + 1 wrapper
spot-check); here: 36 (GW150914) + 54 (GW170814) rows re-used, no new correlations run; 1000+1000 shuffle draws.

---

## Test count, all three pairs

| pair | raw rows | shuffle draws |
|---|---|---|
| 1 THE BUZZ | 12 (job,seat) + 12 (cloud,pair) offset series | 4,000 |
| 2 ignored step | 26 batches | 2,000 |
| 3 control | 36 + 54 sweep rows (of 92 total pass-3 tries) | 2,000 |
