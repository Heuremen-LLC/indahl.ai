# SEALED DISCO 2 JOB -- Kingston, the second fridge, 2026-10-01

Scripts: `out/sealed_disco2/build_sealed_job.py`, `out/sealed_disco2/analyze_sealed_job.py`. Dry-run only here
(local simulator, no submission). Account loading follows `out/placed_vs_arisen/kingston_placed_vs_arisen.py` /
`parallax_ibm.py` / `parallax_echo.py`. Single process, no multiprocessing, no heavy local simulation (dry-run
shot counts kept small: 150-300). Seed: **20261001** (today's date), used for every qubit-group draw and every
submission-order shuffle. No expected numbers or guesses are written anywhere below.

**Revision history (2026-10-01):**
1. Claim A redesigned mid-build from a two-witness/two-step circuit into a three-witness, three-firing Latin
   square (Wayfinder). The two-witness version never reached a dry run and is not kept as a separate artifact.
2. Outside review (same day) returned four more revisions, applied below: (1) the three firings are now
   INTERLEAVED inside ONE job, not three separate jobs; (2) the primary statistic (arrow / third-moment) is
   flagged as having NO dry run, pipeline-only on synthetic I/Q; (3) claim A is renamed **THE BACKACTION
   TRIANGLE**, with the three reads named as causally chained, not independent witnesses; (4) the three-cornered
   hat and loop closure keep their names and machinery. The three-firing (pre-interleave) version from revision
   1 is kept below as **SECTION 1-SUPERSEDED** rather than deleted.

---

## WHERE THE SIMULATOR BROKE

Standing instruction: a simulator break is data, not a blocker to route around. Four breaks were hit and kept;
none were silently routed around without leaving the broken row in place. Full detail in
`out/sealed_disco2/out/dryrun_*/simulator_breaks.json` (one file per dry-run invocation; identical break set in
both the `full` and `min` variants run for this report).

| # | WHERE (circuit/claim/control, option, line) | WHY (exact error) | WHAT IT MEANS for the real fire |
|---|---|---|---|
| 1 | `meas_type="kerneled"` (I/Q / meas_level=1) via `SamplerV2(mode=FakeKingston())`, local testing mode, at ANY qubit count | `IndexError: index 0 is out of bounds for axis 1 with size 0` inside `BackendSamplerV2._postprocess_pub` (it tries to split raw memory into (I,Q) floats, but the local fake-backend simulator returns bitstring memory, not complex samples) | The local path has **no kerneled-measurement model at all**. Claims A-D here all need level-1 I/Q, and none of them can be produced locally, at any width. The real fire still requests `meas_type="kerneled"` against `ibm_kingston` hardware, which **does** support it (`parallax_ibm.py`, `parallax_echo.py`, `kingston_placed_vs_arisen.py` all read real kerneled I/Q from this exact backend family) -- every claim here is testable on real hardware, just not locally. SUBSTITUTION used for the dry run: same circuits run with default (bitstring) measurement locally, then each 0/1 mapped onto a synthetic Gaussian I/Q cloud parameterized by this backend's own published readout error. Declared, not silent; this broken row stays in `simulator_breaks.json` regardless. |
| 2 | Full design width (~30-50 qubits: 3 random triples + tile-8 + idle neighbors) simulated locally with FakeKingston's own (Kraus-channel) noise model attached, `method="automatic"` | `ERROR: [Experiment 0] a circuit requires more memory than max_memory_mb` | Statevector/density-matrix memory scales exponentially; a circuit spanning dozens of the chip's 156 qubits with a realistic noise model is far beyond local memory, regardless of real hardware (which never simulates a statevector at all). Tried `method="stabilizer"` as a fix (exact for this Clifford-only gate set, X/reset/delay/measure, no entangling gates) -- that *solves* the memory ceiling but trades it for break #3. WORKAROUND actually used: the qubit set is narrowed to <=12 qubits (one random triple + two tile-8 qubits + idle neighbors) **for local simulation only**; the `--fire` design keeps its full qubit set untouched. |
| 3 | `method="stabilizer"` vs FakeKingston's built-in thermal-relaxation noise model (attempted fix for #2) | `ERROR: [Experiment 0] Noise model contains invalid instructions {"instructions": {kraus}} for "stabilizer" method` | FakeKingston's default noise model applies Kraus (amplitude/phase damping) channels to model real T1/T2/readout error; the stabilizer method can only simulate Clifford unitaries + resets/measurements, not general Kraus channels. So fixes #2 and #3 fight each other: stabilizer solves memory but kills the noise model; keeping the noise model needs density_matrix/automatic, which reintroduces memory failure at full width. Resolved by narrowing width (break #2's workaround) and keeping `method="automatic"` with the real noise model attached -- exact tradeoff kept visible rather than silently picking one side. |
| 4 | `rep_delay` (control #4, rep-rate heating) set via `sm.options.execution.rep_delay` on `SamplerV2(mode=FakeKingston())` | `UserWarning: Options {'execution': {'rep_delay': ...}} have no effect in local testing mode.` | The local simulator accepts the option without error but silently ignores it -- no between-shot thermal/relaxation model exists locally, so a dry run cannot show any rep-rate-heating effect at any value. On the real fire, `rep_delay` is a genuine physical dead-time the control electronics insert between shots, so **control #4 is only testable on real hardware, not locally.** The plan still carries all three rep_delay values (20/250/1000 us) into the real design; the dry run only proves the plumbing runs, not the physics. |

A fifth non-break, noted for completeness: `.array` on a bitstring `BitArray` returns packed bytes, not a
simple (shots, qubits) 0/1 array -- `.to_bool_array()` is the correct accessor. This was **my own extraction
bug**, not a simulator limitation, and was fixed directly in the code rather than logged as a break.

Also note: control #6's prep-|2> reference circuit is **not available on this backend's target at all** (no
exposed `x12`/`ef`-type gate) -- true in simulation AND on real hardware, so it is reported as a design-level
"unsupported on this backend" row rather than a simulator-only break. The rest of control #6 (|2> visibility
inside kept I/Q) is unaffected and stands on the real fire.

---

## 1-SUPERSEDED. Claim A (pre-outside-review) -- the chip two-step, THREE witnesses / THREE firings (Latin square)

**SUPERSEDED by section 1 below** (outside review, same day): this version submitted each firing as its own
separate job (three jobs total for claim A) and called the claim "the chip two-step" / treated the three reads
as independent witnesses. Kept here verbatim for the record, not deleted.

One event, one qubit, read three times in a single shot: mid-circuit look 1, mid-circuit look 2, final look 3,
I/Q kept (meas_type=kerneled) on all three. The **hardware knob that distinguishes the three witnesses is the
explicit readout delay before that look** -- the time since the previous look (or since state prep, for look
1) -- built with real `delay()` instructions, the same multi-gap spacings used elsewhere in this project
(`GAP_ROLES = {A: 20us, B: 100us, C: 1000us}`, matching the Marrakesh echo's own delay set). No other per-look
hardware knob is exposed by Qiskit's Sampler interface on this backend (there is no way to request a different
integration kernel or measurement duration per individual mid-circuit look) -- so the rotation is over this one
real knob (gap duration) crossed with seat position and firing order, as instructed when no second knob exists.

Three firings rotate which gap role sits in which seat (3x3 Latin square), so seat position is never confounded
with gap duration:

| firing | seat 1 (before look 1) | seat 2 (before look 2) | seat 3 (before look 3) |
|---|---|---|---|
| firing1 | A (20 us) | B (100 us) | C (1000 us) |
| firing2 | B (100 us) | C (1000 us) | A (20 us) |
| firing3 | C (1000 us) | A (20 us) | B (100 us) |

Each firing is its own IBM job (two pubs: prep-0 and prep-1, same gap set). A fourth, smaller job adds a
reset-between-looks variant (firing-1's gap set, prep-1 only) as the reset-vs-no-reset half of control #3; the
long-delay half of control #3 is covered for free, in every firing, by role C (1000 us) landing in some seat.
The single-look circle control (`P0_1L`/`P1_1L`, one job, two pubs) stands beside the three-witness design
exactly as it did in the two-witness version: each witness's own forward/reversed closure is computed from it,
offline, beside the three-way result.

**Analysis (claim A), run end to end in `analyze_sealed_job.py` section "Claim A"):**
- **(a) Three-cornered hat**, solved per qubit per firing per prep from the three pairwise difference variances
  (look1-look2, look2-look3, look1-look3): `s1=(v12+v13-v23)/2`, `s2=(v12+v23-v13)/2`, `s3=(v13+v23-v12)/2`.
  Solved **raw, never clipped** -- negative solutions are reported as negative (the dry run on the min variant
  found 0/30 rows negative; this is a pipeline proof, not a physics result, since the dry run carries no real
  decay-vs-delay physics in its bit layer, see WHERE THE SIMULATOR BROKE #2/#3).
- **(b) Loop closure**: `(look1-look2)+(look2-look3)-(look1-look3)` is an algebraic identity and must read 0 up
  to floating-point noise on every row -- run as the ruler row beside the hat, not as a finding.
- **(c) Witness/seat/order decomposition**: a Latin-square ANOVA (grand mean + seat effect + firing/order
  effect + witness/role effect) on the (firing x seat) table of mean excitation fraction, exploiting that each
  role appears exactly once per row and once per column of the 3x3 square.

---

## 1. Claim A -- THE BACKACTION TRIANGLE (renamed from "the chip two-step" / "Disco 2 on the chip")

One event, one qubit, read three times in a single shot: mid-circuit look 1, mid-circuit look 2, final look 3,
I/Q kept (meas_type=kerneled) on all three. **The three reads are CAUSALLY CHAINED, not three independent
witnesses of one event**: read 2 measures the state that read 1's OWN measurement left behind, and read 3
measures what read 2 left. A measurement is not a passive look here -- it is an act that can change the state
it reads (backaction), on top of whatever the qubit does on its own between reads (evolution/decay). So any
difference between reads is **backaction plus evolution, entangled together**, not a clean disagreement between
independent observers. This reading replaces the "two witnesses of one event" framing the Disco 2 rack uses for
separate-instrument pairs (THE_DISCO_2_20261001.md) -- that framing fits two SEPARATE instruments reading the
SAME external record; it does not fit three sequential reads of the SAME qubit, where each read can disturb
what the next read sees. The name "the backaction triangle" is chosen to say this plainly in every later
reference, rather than re-import the two-witness language this design does not actually satisfy.

The **hardware knob that distinguishes the three reads is the explicit readout delay before that read** -- the
time since the previous read (or since state prep, for read 1) -- built with real `delay()` instructions, the
same multi-gap spacings used elsewhere in this project (`GAP_ROLES = {A: 20us, B: 100us, C: 1000us}`, matching
the Marrakesh echo's own delay set). No other per-read hardware knob is exposed by Qiskit's Sampler interface on
this backend (there is no way to request a different integration kernel or measurement duration per individual
mid-circuit read) -- so the rotation is over this one real knob (gap duration) crossed with seat position and
firing order, as instructed when no second knob exists.

Three firings rotate which gap role sits in which seat (3x3 Latin square), so seat position is never confounded
with gap duration:

| firing | seat 1 (before read 1) | seat 2 (before read 2) | seat 3 (before read 3) |
|---|---|---|---|
| firing1 | A (20 us) | B (100 us) | C (1000 us) |
| firing2 | B (100 us) | C (1000 us) | A (20 us) |
| firing3 | C (1000 us) | A (20 us) | B (100 us) |

**All three firings are now INTERLEAVED INSIDE ONE JOB** (one `SamplerV2.run()` call, 6 pubs: P0/P1 x
firing1/2/3), per outside review: three separately-submitted jobs would let calibration/thermal drift *between*
jobs leak into the firing-to-firing comparison, confounding "which firing" with "which job, run at a slightly
different moment." The pub order inside this one job is shuffled with the same seed (`20261001`) and the
realized order is written to `meta.json` (`backaction_triangle_pub_order_seeded`) on every run. A separate,
smaller job adds a reset-between-reads variant (firing-1's gap set, prep-1 only) as the reset-vs-no-reset half
of control #3; the long-delay half of control #3 is covered for free, in every firing, by role C (1000 us)
landing in some seat. The single-look circle control (`P0_1L`/`P1_1L`, its own job, two pubs) stands beside the
triangle exactly as before: each read's own forward/reversed closure is computed from it, offline, beside the
three-way result.

**PRIMARY STATISTIC HAS NO DRY RUN.** The arrow -- A(k) = <x^2 x_{t+k}> - <x x_{t+k}^2>, this project's own
"message" statistic (THE_DISCO_2_20261001.md part 1) -- and any third-moment-type statistic is **identically
zero on any two-valued (discriminated-bit) record, under any encoding**, because x^2 is affine in x whenever x
takes only two values (0/1, or any other two-valued relabeling). So these statistics MUST be computed on raw
I/Q, never on thresholded bits. WHERE THE SIMULATOR BROKE #1 (above) establishes that the local simulator
cannot produce real I/Q at all, at any qubit count -- **so there is no dry run of this primary statistic's real
physics, full stop.** What `analyze_sealed_job.py` actually runs, and what the "confirmed end to end" claim in
section 5 below means, is the PIPELINE against SUBSTITUTED SYNTHETIC I/Q (fabricated Gaussian clouds keyed to
ideal bit outcomes, declared in break #1) -- never against real kerneled data, because none exists locally.
This is stated here plainly, not left implicit: a dry run passing is evidence the code runs, not evidence about
backaction, evolution, or any other physical claim.

**Analysis, run end to end in `analyze_sealed_job.py`'s "Claim A" section (on synthetic I/Q only, per the above):**
- **(a) Three-cornered hat**, solved per qubit per firing per prep from the three pairwise difference variances
  (read1-read2, read2-read3, read1-read3): `s1=(v12+v13-v23)/2`, `s2=(v12+v23-v13)/2`, `s3=(v13+v23-v12)/2`.
  Solved **raw, never clipped** -- negative solutions are reported as negative. Name and machinery unchanged by
  the rename: this is still "the three-cornered hat," now understood as splitting out backaction+evolution
  variance per read rather than per independent witness.
- **(b) Loop closure**: `(read1-read2)+(read2-read3)-(read1-read3)` is an algebraic identity and must read 0 up
  to floating-point noise on every row -- run as the ruler row beside the hat, not as a finding. Name and
  machinery unchanged.
- **(c) Witness/seat/order decomposition**: a Latin-square ANOVA (grand mean + seat effect + firing/order
  effect + role effect) on the (firing x seat) table of mean excitation fraction, exploiting that each role
  appears exactly once per row and once per column of the 3x3 square.

---

## 2. Claims B, C, D and the controls -- mapped to circuits

| Claim / rule-out | What it needs | Circuit(s) that answer it | Job tag(s) |
|---|---|---|---|
| **A** -- THE BACKACTION TRIANGLE (3 causally-chained reads) | mid-circuit x2 + final read, same qubit, I/Q, circle control, interleaved in ONE job | `P0_firingN`/`P1_firingN` (N=1,2,3, one job); `P0_1L`/`P1_1L` | `G_BACKACTION_TRIANGLE`, `G_CIRCLE` |
| **B** -- placed vs arisen, Kingston, same multi-gap spacings as Marrakesh echo | E1 (placed, gate-written) vs E0 (arisen, nothing placed) across the 7 (full) / 3 (min) echo delays | `E0`, `E1` | `G_ECHO` |
| **C** -- second band: both clocks (multi-gap echo clock + drain clock), I/Q, cutoff-movable | clock A = echo tau fit (claim B's own data); clock B = drain built from the backaction triangle's read1->read2 / read2->read3 transitions, pooled by the actual gap duration used (A/B/C) | `E0`/`E1` (clock A); `P0_firingN`/`P1_firingN` transitions (clock B) | `G_ECHO`, `G_BACKACTION_TRIANGLE` |
| **D** -- raw I/Q kept, cutoff movable after the fact | meas_type=kerneled on every pub | all pubs in every job | all tags |
| **1** -- calibration drift, interleaved not just at start | prep-0/prep-1 single-look rows appearing more than once across the job's submission order | `P0_1L`/`P1_1L` (`G_CIRCLE`) vs `P1_firing1`'s own seat-1 (`G_BACKACTION_TRIANGLE`) | `G_CIRCLE`, `G_BACKACTION_TRIANGLE` |
| **2** -- readout crosstalk / groups of 3, idle neighbors in the same shot | random triples + tile-8, each with an idle topological neighbor measured (never gated) in every circuit | every circuit (built on `all_q` = active ∪ idle neighbors) | all tags |
| **3** -- reset leakage; no-reset variant + long-delay variant | a reset-between-reads circuit beside the default no-reset one; role C (1000us) as the long gap | `P1_firing1_reset` (reset variant); role C in every firing (long-delay, free) | `G_RESET_CONTROL`, `G_BACKACTION_TRIANGLE` |
| **4** -- rep-rate heating, >=3 rep_delay values | three distinct `rep_delay` settings across the job package | `G_BACKACTION_TRIANGLE`/`G_RESET_CONTROL` (20us), `G_CIRCLE` (250us), `G_T1LADDER` (1000us); `G_ECHO` separately sweeps its own 3-7 gaps | all tags except `G_ECHO` |
| **5** -- T1 ladder, same qubits, same job | explicit X-then-delay-then-measure ladder | `T1_<delay>` | `G_T1LADDER` |
| **6** -- |2> visible in I/Q; prep-2 reference if supported | meas_type=kerneled (structural); prep-2 attempted, reported UNSUPPORTED on this backend | `PREP2` (not built: no x12/ef gate on this target) | n/a -- see WHERE THE SIMULATOR BROKE |
| **7** -- qubit choice at random in groups of 3 (seeded), tile-8 named | `pick_qubits()`, `RNG = np.random.default_rng(20261001)` | all circuits (qubit layout) | all tags |
| **8** -- pulse-sequence order randomized (seeded) | job-group submission order shuffled with the same seed | n/a (submission order, not circuit content) | all tags |

---

## 3. Qubits, seed, backend

- **Backend:** `ibm_kingston` (the second fridge; Marrakesh records already on disk serve as the other-chip
  judge per the house's method laws -- no shuffle-based significance used anywhere in the analysis).
- **Seed:** `20261001` (`numpy.random.default_rng(20261001)`), used for (a) the three random triples drawn from
  all even/odd addressable qubits excluding tile-8, (b) the job-group submission order shuffle, and (c) the pub
  order WITHIN the backaction-triangle job (6 pubs: P0/P1 x firing1/2/3), written to `meta.json` as
  `backaction_triangle_pub_order_seeded` on every run.
- **Tile-8** (named group, control #7): `[80, 81, 82, 83, 96, 100, 101, 102, 103, 116]` -- taken verbatim from
  `out/the_buzz/heron.py`'s WIRE_MAP carving (Heron r2, 156-seat layout). **Assumption, flagged:** this carving
  was built against Marrakesh and is applied to Kingston here because both report 156 qubits (Heron r2) in this
  venv's fake backends; it has not been independently re-derived from Kingston's own physical row/column
  numbering, so "tile 8" here names the same SEAT INDICES as on Marrakesh, not independently confirmed to be
  the same physical die region on Kingston.
- **Random triples drawn this run** (from `pick_qubits()`, seed 20261001): `rand1=[44,126,139]`,
  `rand2=[28,125,134]`, `rand3=[33,105,145]` -- these feed the real `--fire` design; the dry run further
  narrows to a <=12-qubit local-simulation-only subset (see WHERE THE SIMULATOR BROKE #2).
- **Idle neighbors:** one per active qubit, drawn from the backend's own coupling map, never gated, measured in
  every shot alongside the active groups (control #2).

---

## 4. QPU-second estimate

**Method:** PRIMARY term is an empirical per-job overhead, calibrated against the real Marrakesh echo run's own
recorded usage draw-down (`out/echo_20260928_122733/meta.json`: 582s -> 540s = 42s across 14 separately-submitted
`SamplerV2` jobs, 1500 shots each) = **3.0 s/job**. This dominates the raw shot-sequence time on jobs this
short (IBM's own job-management/queue-to-run overhead, not gate+readout duration). SECONDARY term is a named,
explicit shot-sequence-time model (`READOUT_US=1.6`, `RESET_US=1.5`, `GATE_US=0.05`, all stated assumptions, not
measurements) -- small next to the overhead term here. Both terms are printed separately by `build_sealed_job.py
--dry-run` so the overhead assumption is never hidden inside a single number.

**UPDATED after the outside review's interleaving revision** (the backaction triangle's 3 firings now share ONE
job instead of 3 separate jobs -- 2 fewer jobs, 6.0 s less overhead, on both variants):

| Variant | Jobs | Overhead term | Sequence-time term | **Total estimate** | Threshold (refuses below) |
|---|---|---|---|---|---|
| **full** | 1 backaction-triangle (6 pubs, interleaved) + 1 reset-control + 1 circle + 14 echo (7 gaps x 2 preps) + 1 T1-ladder = **18 jobs** | 54.0 s | 3.45 s | **57.5 s** | 90 s |
| **min** | 1 backaction-triangle (6 pubs, interleaved) + 1 reset-control + 1 circle + 6 echo (3 gaps x 2 preps) + 1 T1-ladder = **10 jobs** | 30.0 s | 1.2 s | **31.2 s** | 40 s |

(Numbers above are the actual printed output of `build_sealed_job.py --dry-run --variant {full,min}`, re-run
2026-10-01 after applying the interleaving revision; they are an engineering runtime estimate, not a physics
prediction, and carry the stated assumptions openly.) **Note on the budget band:** interleaving the three firings
into one job is a genuine cost reduction (fewer job-management overheads), so both variants now land slightly
below the original 60-90s / ~40s target bands (full: 57.5s vs 60-90s; min: 31.2s vs ~40s). This is reported
as-is rather than padded back up with extra shots to hit a number -- the interleaving was requested specifically
to remove a confound (inter-job drift), and its side effect of being cheaper is not fought. The fire-refusal
thresholds (90s / 40s) are kept as a safety margin ABOVE these lower estimates, not retuned downward to match
them, so --fire still requires more account headroom than either variant is estimated to need.

**Per-firing share of the single interleaved job:** the three firings no longer have a separable per-firing
cost (that was the point of merging them) -- the backaction-triangle job's 1 job-overhead (3.0 s) is shared
across all 6 pubs (3 firings x 2 preps) plus its own sequence-time share (~3 x 20us/100us/1000us gaps x 2 preps
x shots), on the order of 0.1-0.5 s of the job's total. Isolating one firing alone (hypothetically, back to a
separate job) would cost ~3.0 s overhead + a few hundredths of a second sequence time, matching the pre-revision
per-firing figure from SECTION 1-SUPERSEDED -- the interleaved job's total is close to, but ~6 s cheaper than,
three such jobs added together.

**Fire-refusal thresholds** (`build_sealed_job.py --fire`, not used by this agent): full variant refuses below
90 s remaining; min variant refuses below 40 s. Both are checked against `QiskitRuntimeService(...).usage()`
before any submission, same pattern as `parallax_ibm.py`/`parallax_echo.py`'s existing brake.

**Exact command to fire** (not run by this agent):
```
~/bones-forge/venv_quantum/bin/python3 out/sealed_disco2/build_sealed_job.py --fire \
    --keyfile ~/bones-forge/.ibm_quantum_key_<N> --variant full   # or --variant min
```

---

## 5. Dry run + analysis, confirmed end to end

```
~/bones-forge/venv_quantum/bin/python3 out/sealed_disco2/build_sealed_job.py --dry-run --variant min
~/bones-forge/venv_quantum/bin/python3 out/sealed_disco2/build_sealed_job.py --dry-run --variant full
~/bones-forge/venv_quantum/bin/python3 out/sealed_disco2/analyze_sealed_job.py out/sealed_disco2/out/dryrun_min_<stamp>
~/bones-forge/venv_quantum/bin/python3 out/sealed_disco2/analyze_sealed_job.py out/sealed_disco2/out/dryrun_full_<stamp>
```

Both dry runs and both analysis passes completed with exit code 0, no uncaught exceptions, writing
`dryrun_data.npz` + `meta.json` + `simulator_breaks.json` (build step) and `ANALYSIS_RESULTS.{json,md}`
(analysis step) each time. The analysis step produced every section required (claim A's hat/closure/ANOVA,
claim B's per-qubit clock-A fit table, claim C's cutoff-swept clock-B series, claim D's same-array two-cutoff
demonstration, and all 8 controls as their own tables) with zero rows silently dropped -- unresolved fits and
small-n cells are reported as such (e.g. claim C's clock-A-vs-clock-B existence correlation is explicitly left
unresolved in the dry run, flagged as too small an n, rather than forced into a false verdict).

**What the dry run does NOT prove:** it proves the pipeline (circuits transpile, jobs submit locally, data
flows into the analysis, every section runs without crashing). It proves nothing about the physics -- the
narrowed qubit set, the synthetic I/Q layer, and the no-op `rep_delay` locally mean no claim's actual numeric
outcome here should be read as a result. That is the point of the WHERE THE SIMULATOR BROKE section above:
the breaks are the honest boundary between "this plumbing works" and "this is real data." Per section 1's
PRIMARY STATISTIC note, this is most true of the backaction triangle's own hat/closure/ANOVA numbers -- those
exist in this dry run ONLY as a pipeline proof against fabricated I/Q, never as a measurement.

**Re-run after the four outside-review revisions (2026-10-01, same day):** both variants were rebuilt and
dry-run again with the interleaved single-job backaction-triangle design (`out/dryrun_min_20261001_095307`,
`out/dryrun_full_20261001_095426`), and `analyze_sealed_job.py` was re-run against both with exit code 0 and no
uncaught exceptions, including the new `backaction_triangle_pub_order_seeded` readout under control 8. The four
WHERE THE SIMULATOR BROKE rows are unchanged by this revision (same four breaks recur identically in both new
`simulator_breaks.json` files) -- the interleaving change affects job/submission structure, not what the local
simulator can or cannot do.
