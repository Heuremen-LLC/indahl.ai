# QUBIT THREE RUNS ON THREE CHIPS -- BUILD REPORT v3, 2026-10-01 night
Spec (the only design): `QUBIT_THREE_RUNS_APPROVED_20261001.md` incl. the night amendments, plus the fixes 1-8 and the owner's WHOLE-CHIP BOXES change. Code: `out/qubit_three_runs/`. The previous build is kept as `*_v2` (`common_v2.py`, `run1_v2.py` ... `analyze_v2.py`, `freeze_v2.py`, `predictions_template_v2.json`, `data/dryrun_full`, `data/dryrun_min`, and this report's previous text `QUBIT_THREE_RUNS_BUILD_20261001_v2.md`); v1 files are `*_v1`.
**Nothing was submitted. `--fire` was never called. No job exists.** The IBM account was touched only read-only and **only `ibm_kingston` was queried** (list in "LOOKS TAKEN BEFORE RUN 1"). `ibm_boston`, `ibm_phoenix`, `ibm_pittsburgh`: no configuration, properties, calibration, status or target was requested, no transpile against them, nothing; their names appeared in the backend list once (count only was printed; the HTTP guard recorded zero requests naming them: `grep -c` of the read log for the three names = 0). The usage (remaining seconds) call was NOT made in this pass.

## READ THIS FIRST
**THE DRY RUNS PROVE THE CODE PATH ONLY, NOT THE PHYSICS.** The local simulator has no raw I/Q, so every I/Q number in a dry run is SYNTHETIC (fabricated from simulated 0/1 outcomes, plus an injected fade over each wait -- tau 300 / 250 / 350 us for the OURS / MAKER / BLANK stand-ins -- and an injected 5 % per-earlier-look kill so the self-effect equation has something to find). In a dry run the chip names are labels only; every simulation runs on the saved FakeKingston snapshot (2026-04) and a BLANK dry run reads no calibration from it.
**The shot count is 839 for all nine jobs. The 3.0-s-per-circuit worst case CANNOT fit nine jobs in 133 s at any shot count** (108 circuits x 3.0 s = 324 s before a single shot). The per-job estimate (3.0 s per job + sequence) fits: **99.9 s** for all nine, with a 33 s margin, and 1.25 x 99.9 = 124.9 s is under 133 s.

## The fix list (what was changed, in the order asked)
1. **THE WAITS CLOSE.** short 60 / medium 240 / long 300 us, laid as whole multiples of 16 dt with medium = long - short in dt counts (asserted for any dt). On ibm_kingston's live dt (4 ns) the realized waits are 59.968 / 240.000 / 299.968 us, and 59.968 + 240.000 = 299.968 exactly. Run 3's third look in BOTH orders of the {60,240} twin sits after 300 us of waiting, the same wait as Run 1's one look and Run 2's second look. The hunter's number is printed at MATCHED elapsed time: F(0,long) run 1, F(1,long) run 2, F(2,long) run 3 via the {60,240} twin (both orders shown, then their mean): `c.Fm.n2.*`, `c.effm2.*`, `c.hunterm.*` (the first effect is `c.eff1.*.w300`). All three mirrored twins stay in Run 3. **Stated plainly: only the {60,240} twin is matched in elapsed time to Runs 1 and 2. The twins {60,300} (total 360 us) and {240,300} (540 us) are read against their own mirror only.** The unmatched pooled version (`c.hunter.*`, F(2) pooled over layouts by last wait) is printed beside it, labelled as mixing "one more look" with "more time passed". Remaining difference, not corrected and stated in the output: each earlier look also takes its own readout (about 2.2 us).
2. **PAID INSTANCE.** `live.py` builds the service from the CRN in `~/bones-forge/.ibm_quantum_instance_crn` and the token in `.ibm_quantum_key_3` (fallback `.ibm_quantum_key_parallax`); tokens are never printed and error text is scrubbed. Read-only check done 2026-10-01 21:33: **it connects with key_3 and the instance CRN; `ibm_kingston` is listed** (6 backend names in the list; count only).
3. **NOTHING GETS LOST.** At submit the sequence is: pending file written (everything knowable, fsync'd) -> `sm.run` -> **the job id is written to `run{N}_job.json` (fsync'd, atomic) as the first thing after the call returns, before anything is printed or awaited** -> `job.result()` once. A job tag `qtr-<chip>-run<N>` is also set, so `recover.py --find` can list the job even if the id file were lost. **`recover.py --run N --chip C --box B`** re-reads a finished job by the saved id and writes the normal results file (tested with fakes: timed-out job -> raises, nothing saved, id and pending files remain; non-DONE job -> refused, nothing written; DONE job -> normal results file with the complete marker, arrays identical, job id in the meta; a second recover refuses). `max_execution_time` = ceil(2 x the job's estimate + 5 s), never below 1.25 x the estimate and never more than leaves every later job its own estimate (first job: 22 s for an 8.3 s estimate). **If a job hits it:** qiskit-ibm-runtime 0.49 documents "forcibly cancelled"; `result()` raises `RuntimeJobMaxTimeoutError` (status ERROR, reason code 1305, "CANCELLED - RAN TOO LONG"); no results are returned, so nothing is saved; system time up to the cap is presumably still billed; `run{N}_job.json` is rewritten with the error and the recover command; `recover.py` says the job is not DONE.
4. **SIZE.** See "Shot count" below.
5. **LOOKS BEFORE RUN 1.** Every look ledger now opens with the section "LOOKS TAKEN BEFORE RUN 1" (see below). Any further read-only account or calibration read, in a build pass or at freeze time, is appended to `account_reads_log.jsonl` by `live.log_read` and appears in that section.
6. **SHOT ORDER.** The returned raw I/Q is documented by qiskit-ibm-runtime (`SamplerExecutionOptionsV2.meas_type`) as a complex array of shape `(*pub_shape, num_shots, creg_size)` per classical register for `"kerneled"` (per shot, not averaged; `avg_kerneled` is the averaged one), and `collect_results` refuses anything not `(839, 9)` complex. **Nothing in the documentation says the shot axis is in the order the shots were run**; our code neither sorts nor reorders. This is a fire-path risk (item 2 below). The analysis now reports `carry.r{N}.{start}.corr` and `.slope`: how the LAST look of one shot relates to the FIRST look of the next shot (rep_delay 500 us), per start, median across qubits, bootstrap width over pairs plus the group spread; pairs never cross a circuit and are centred within the circuit (a first version without the centring read a spurious 0.12 on iid synthetic data, because circuits with different means were pooled; fixed). No correction is applied anywhere; it is a reading. Tested: iid synthetic data reads 0.00 +- 0.01; a planted 0.25 carry reads 0.2-0.5.
7. **QUBIT GROUPS.** `freeze.py --run 1` reads the live chip's current qubit list (read-only), draws the three groups of three by the written seed 20261001 and writes them into the freeze file; runs 2 and 3 copy run 1's groups and REFUSE if any is no longer in the live list. The fire path re-checks usability against the live list and refuses. Tested live on ibm_kingston in a scratch folder (not the build folder): 156 candidates, none faulty, groups [[82,139,154],[38,92,96],[25,109,135]], calibration stamp 2026-10-01T21:02:25-04:00, run 2 freeze copied them. The groups are part of the freeze hash. (For MAKER: same, from that chip's own list. For BLANK see below: blind draw.)
8. Circularity audit, all nine dry runs and every analysis mode re-run end to end: see "Dry runs".

## THE OWNER'S CHANGE: THE BOXES ARE WHOLE CHIPS
- **OURS = ibm_kingston.** Sealed predictions with numbers and widths, as built. Freeze reads the live qubit list.
- **MAKER = ibm_phoenix, BLANK = ibm_pittsburgh, left alone entirely = ibm_boston.** Drawn by the written seed `SEED_CHIPS = 20261061` (`common.chip_assignment()`, a pure function: no account contact). Every script refuses the left-alone chip and any chip/box pair that disagrees with the draw (tested).
- **MAKER:** the maker's published calibration (T1/T2/readout of the drawn qubits + its stamp) is read at each freeze and written into the freeze file and its hash; it is the chip's only prediction (the miss is vs the median T1 of the nine qubits, width = their sd, fading-time quantities only). The fire path REFUSES a prediction file for it.
- **BLANK:** no prediction file (refused), no calibration, no properties, no target, no usability check. **Freeze hashes the code and the seed only** (`freeze.py` makes no account contact for it). Circuits are single-qubit only and built **without a transpile and without a target**: width = the chip's qubit count, only x / sx / delay / measure, on qubit numbers drawn **blind by the written seed `SEED_BLIND = 20261051` from 0..N-1**. `check_structure` proves they are native by construction (x/sx/delay/measure only, only the nine chosen qubits). If a drawn qubit is dead it shows up as a ROW in the results (`THE DRAWN QUBITS` table: OFF-to-ON separation / OFF cloud width, "CAN'T READ" when the clouds overlap); nothing is checked beforehand, nothing dropped. **Where N comes from:** the chip's own static configuration (`GET /backends/<name>/configuration`: n_qubits, dt, rep_delay range), read at fire time, which is not calibration. Public documentation did not give me N for these three names (a search returned only "Heron: 156 qubits" generically and nothing on the three names), so I did not use it. **If you want zero configuration read, N and dt would have to be hard-coded from a source I could not find.** Waits need dt, so the configuration is also where the timing grid comes from.
- **How the BLANK submit avoids calibration (the SDK would not):** `SamplerV2(mode=<IBMBackend>).run` reads `backend.target` (= the chip's PROPERTIES, i.e. calibration) and calls `check_faulty` (properties again) for every pub, and merely `getattr(backend, 'dynamic_reprate_enabled')` also triggers a properties fetch (`IBMBackend.__getattr__`). So the BLANK primitive is built around a stub service (`common._BlindService`) that forwards to `service._run` with the backend given as a NAME; the service then fetches only the configuration and the status. Tested live on ibm_kingston **treated as blind** (the guard refuses properties/calibration/defaults URLs and any job POST): requests were token, resource lookups, backend list, `/backends/ibm_kingston/configuration` and nothing else, zero refused; `sm.run` with 18 pubs, `meas_type=kerneled`, `rep_delay`, `max_execution_time` 22 and the job tag reached a recorder that stood in for the service -- nothing was sent.
- **The HTTP guard (`live.py`)** patches `requests.Session.request`: it refuses any URL naming a chip that is not in the allowed set (so the left-alone chip, and in a build pass every chip but ibm_kingston, cannot be reached by any call), refuses properties/calibration/defaults for a BLIND chip, refuses any job submission unless `--confirm-submit` was given, and logs every request (method and path only) into the read log.
- **The BLANK results are not opened by any analysis mode until all nine jobs have landed** (only the small meta files are read for that check). Tested: with only run 1 landed `analyze.py run1 --chip ibm_pittsburgh` REFUSED and opened nothing.
- **The analysis lays the three chips side by side for every reading** (`analyze.py all`): OURS / MAKER / BLANK, then each chip read against the mean of the other two (value +- combined width), no verdict word. The miss column exists only for OURS and MAKER; BLANK prints "no prediction and no miss column, by design". The old per-group box rotation (BOX_SEED) is gone.
- **Which chip's data may a prediction be written from:** OURS predictions may be written from ibm_kingston's own earlier runs only (`data_seen` none / maker / run1 / runs1+2). No MAKER or BLANK data feeds any prediction.

## Where it broke first
In the order found:
1. **Design collision, the first one: the worst-case guard cannot cover nine jobs.** 9 jobs = 108 circuits; 3.0 s per circuit = 324 s > 133 s before a shot is run (worst case at 839 shots: 396.9 s). So the guard is on the per-job basis with a 25 % margin; the worst case is printed beside it. Said plainly in "Shot count".
2. **The SDK would have read the BLANK chip's calibration at submit** (see above): `SamplerV2` reads `backend.target` and `check_faulty`; plain attribute access on an `IBMBackend` also fetches properties. My own v2 fire path (`getattr(be, 'dynamic_reprate_enabled')`, a transpile against `be.target`) would have done it. Replaced: configuration-only reads (`be.configuration()`), hand-built native circuits, the stub service.
3. **`service.backends()` with no name builds a backend object for every chip, which fetches every chip's configuration.** Never used. The name list comes from `_discover_backends_from_instance` (one `/backends` list call) and a single chip is opened with `service.backend(name)`.
4. First carry-over reading on iid synthetic data came out 0.12 +- 0.01: pooled circuits with different means. Centred per circuit; planted-carry test added.
5. v2 text said each wait sits in each gap 4 times in run 3; the layout gives 6 per wait per gap over 18 circuits. Fixed in the output text.
6. Simulator, as before (reproduced, declared in every `run*_meta.json` under `simulator_breaks`): `meas_type="kerneled"` raises `UFuncTypeError` locally (substitution: same circuits, bitstring measurement, each 0/1 placed in a synthetic Gaussian cloud); `rep_delay` is accepted and ignored locally; the local noise model has no fading during a WAIT (ON start after a 300 us wait reads 0.96 mean bit locally where the maker T1 median 292 us alone gives about 0.36), so the injected synthetic fade carries the fit.
7. Live read vs the old snapshot: ibm_kingston today reports **dt 4 ns, delay granularity 1, min_length 2, acquire and pulse alignment 1** and no `max_shots`/`max_circuits` limit (both null). Waits are still laid on a 16-dt grid.

## What each run is, in plain words
START: **OFF** (nothing put in), **MID** = both-and-neither (one half-turn gate, `sx`), **ON** (fully put in, `x`). LOOK: one reading of the qubit, raw I/Q kept every time (never cut to 0/1). WAIT: a pause. Waits: short 60 us, medium 240 us, long 300 us (realized 59.968 / 240.000 / 299.968 on ibm_kingston). The three runs are fired on each of the three chips: nine jobs.
- **Run 1, ZERO earlier looks:** START, WAIT, LOOK once. 3 starts x 3 waits = **9 circuits**, 9 looks.
- **Run 2, ONE earlier look:** START, LOOK, WAIT, LOOK. 3 x 3 = **9 circuits**, 18 looks.
- **Run 3, TWO earlier looks, MIRRORED TWINS:** START, LOOK, WAIT a, LOOK, WAIT b, LOOK. For each pair of different waits both orders: twin {60,240} (the matched one: a+b = 300) = (60,240) and (240,60); twin {60,300} = (60,300) and (300,60); twin {240,300} = (240,300) and (300,240). 3 starts x 6 layouts = **18 circuits**, 54 looks.
- Same nine qubits (three groups of three) in all three runs of a chip. OURS and MAKER: seeded shuffle of the chip's live qubit list at freeze; BLANK: blind draw from 0..N-1 (on a 156-qubit chip: [[26,106,108],[12,112,141],[46,103,144]]). Circuit order: seeded shuffle (run 1 seed 20261011, run 2 20261012, run 3 20261013). One job per (chip, run), every circuit a pub of one sampler call. rep_delay 500 us fixed. Synthetic-I/Q seed 20261021 + box index; analysis seed 20261031.
- Recorded with each run: start and end time, calibration stamp (OURS, MAKER), the maker's published T1/T2/readout per qubit (OURS, MAKER; **none for BLANK**), code hash, look ledger, job id, the max_execution_time used.

## Every circuit in each run (START, WAIT, LOOK) -- no other circuit exists
There are **no separate calibration or test circuits**: OFF and ON are the calibration and the data at once. Enforced three ways: (a) `build_ledger` lists every circuit and `ledger_self_check` refuses any start outside OFF/MID/ON; (b) `check_ledger_vs_circuits` counts the built circuits: exactly n_looks x 9 measurements, one classical register per look, one delay per qubit per wait; (c) `verify_arrays` and `analyze.load` refuse a results file whose arrays differ from the ledger by even one look. Each circuit below is the same on every chip; only the nine qubit numbers differ.

**Run 1: 9 circuits, 9 looks in all, calibration or test circuits: 0.**

- `OFF|w60`: START OFF; WAIT 60 us (realized 59.968 us); LOOK 1 [0 look(s) before it]
- `OFF|w240`: START OFF; WAIT 240 us (realized 240.000 us); LOOK 1 [0 look(s) before it]
- `OFF|w300`: START OFF; WAIT 300 us (realized 299.968 us); LOOK 1 [0 look(s) before it]
- `MID|w60`: START MID; WAIT 60 us (realized 59.968 us); LOOK 1 [0 look(s) before it]
- `MID|w240`: START MID; WAIT 240 us (realized 240.000 us); LOOK 1 [0 look(s) before it]
- `MID|w300`: START MID; WAIT 300 us (realized 299.968 us); LOOK 1 [0 look(s) before it]
- `ON|w60`: START ON; WAIT 60 us (realized 59.968 us); LOOK 1 [0 look(s) before it]
- `ON|w240`: START ON; WAIT 240 us (realized 240.000 us); LOOK 1 [0 look(s) before it]
- `ON|w300`: START ON; WAIT 300 us (realized 299.968 us); LOOK 1 [0 look(s) before it]

**Run 2: 9 circuits, 18 looks in all, calibration or test circuits: 0.**

- `OFF|w60`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]
- `OFF|w240`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]
- `OFF|w300`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]
- `MID|w60`: START MID; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]
- `MID|w240`: START MID; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]
- `MID|w300`: START MID; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]
- `ON|w60`: START ON; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]
- `ON|w240`: START ON; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]
- `ON|w300`: START ON; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]

**Run 3: 18 circuits, 54 looks in all, calibration or test circuits: 0.**

- `OFF|w60-240`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]
- `OFF|w60-300`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `OFF|w240-300`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `OFF|w240-60`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `OFF|w300-60`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `OFF|w300-240`: START OFF; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]
- `MID|w60-240`: START MID; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]
- `MID|w60-300`: START MID; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `MID|w240-300`: START MID; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `MID|w240-60`: START MID; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `MID|w300-60`: START MID; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `MID|w300-240`: START MID; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]
- `ON|w60-240`: START ON; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]
- `ON|w60-300`: START ON; LOOK 1 [0 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `ON|w240-300`: START ON; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 3 [2 look(s) before it]
- `ON|w240-60`: START ON; LOOK 1 [0 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `ON|w300-60`: START ON; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 60 us (realized 59.968 us); LOOK 3 [2 look(s) before it]
- `ON|w300-240`: START ON; LOOK 1 [0 look(s) before it]; WAIT 300 us (realized 299.968 us); LOOK 2 [1 look(s) before it]; WAIT 240 us (realized 240.000 us); LOOK 3 [2 look(s) before it]

## The look ledger
Opens with **LOOKS TAKEN BEFORE RUN 1** (None touched a bit):
1. 2026-10-01 (time of day not on file): read-only account check, REMAINING TIME (usage), by the v1 build pass: it read 0 seconds left until 2026-10-22 on the old instance.
2. 2026-10-01 (not on file): read-only account check, WHICH KEYS SEE THE INSTANCE (no key printed).
3. 2026-10-01 (not on file): read-only account check, THE BACKEND LIST.
4. 2026-10-01 (not on file): ONE read of the maker's published calibration numbers (T1/T2/readout of the drawn qubits, ibm_kingston) by an earlier build pass (v1 `live_probe.py`).
5. 2026-10-01 (not on file): ledger line noting the instance's COST LIMIT (the amount is not on file in this folder).
6. 2026-10-01 21:33:18: this pass: connected with the instance CRN and key_3; backend NAME list (ibm_kingston listed).
7. 2026-10-01 21:33:20: this pass: **ibm_kingston only**: configuration + properties (the maker's published calibration) + target: qubit list, timing grid, rep and shot limits. Snapshot saved: `live_kingston_readonly_20261001.json`.
8. 2026-10-01 21:59:42: this pass: ibm_kingston only: configuration only, to test the BLIND submit path without submitting.
9. 2026-10-01 21:59:59: this pass: ibm_kingston only: freeze run 1 test in a scratch folder (read-only live qubit list + calibration stamp).
10. 2026-10-01 22:00:04: this pass: same for the run 2 freeze test.
**Items 1-5 are copied from your list; their exact times and the cost-limit amount are not recorded in any file I could find, so the ledger says "not on file" rather than inventing them. Please correct those five lines if you have the times** (edit `PRE_RUN1_STATIC` in `common.py`; it is not part of any freeze hash).
After that, per circuit: the count of looks in it and, for each look, how many looks came before it, the wait just before it and just after it (requested and realized). Saved as `run{N}_look_ledger.json` beside the results and embedded in `run{N}_meta.json`. Totals per chip: run 1 = 9 looks, run 2 = 18, run 3 = 54, **81 looks per chip, 243 on three chips**. `analyze.py` tracks every look it reads and prints, per run, "looks read / in the analysis but not in the ledger / in the ledger but never read": every dry-run result is all read, none outside the ledger, none unread.

## The three boxes (whole chips)
| box | chip | prediction | calibration read | freeze hashes |
|---|---|---|---|---|
| OURS | ibm_kingston | our sealed numbers + widths, one file per run | live qubit list + calibration at freeze and at fire (target needed for the submit check) | code + ledger + groups |
| MAKER | ibm_phoenix | the maker's published calibration read at freeze = the only prediction; none of ours | at freeze (each run) and at fire | code + ledger + groups + the calibration numbers |
| BLANK | ibm_pittsburgh | none (a file is refused) | none: configuration only (N, dt) at fire; no properties, no target | code + the seed only |
| left alone | ibm_boston | -- | never touched in any way (the guard refuses any URL naming it) | -- |

## The prediction ledger and the guards
- **The prediction is a look.** Each entry records `written_at`, `data_seen` (none / maker / run1 / runs1+2, of ibm_kingston's own data), `predicted`, `width`; the file records `_run` and `_written_at`. Template `predictions_template.json`: **237 quantities** (228 + the 9 matched-hunter quantities), regenerated by `analyze.py --make-template`.
- **`freeze.py --run N --chip C --box B`** writes `freeze_<chip>_run{N}.json` BEFORE any prediction (hashes as in the box table, plus `frozen_at`). The fire path refuses unless the freeze came from the LIVE chip (`source: live`, never `--fake`), its hash matches the code and ledger on disk, (OURS) the prediction file is later than the freeze with every entry's `written_at` and `data_seen` allowed, (MAKER / BLANK) no prediction file is given. `analyze.py` scoring refuses if the hash on file, the hash stored in the results and the hash of the code now do not all match, or if the groups differ, or if the prediction is earlier than the freeze or later than the run's start. Any edit to `common.py`, `live.py`, `run{N}.py` or `analyze.py` after a freeze invalidates that run's freeze: **freeze only when the code is final.**
- **Tested refusals** (scratch copy `/tmp/qtr_copy`, so no test freeze exists in the build folder): maker given a prediction file -> REFUSED; BLANK chip analysed with run 1 only landed -> REFUSED; prediction earlier than freeze / later than run start / code edited after the freeze / meta incomplete / npz tampered -> REFUSED (v2 tests, same code paths); left-alone chip and wrong chip/box pairs -> REFUSED; "BOX ON BOX" (written from run1, quantity contains run 1) -> not scored.
- **The miss column is computed last and feeds nothing.** `main()` loads and measures everything, prints, saves `analysis_*.json`, and only then calls `score_ours` / `score_maker`. The audit reads only prediction headers. Scores go to separate `scores_*.json`.
- **DON'T COUNT UNTIL IT LANDS.** `save_results` writes the npz, ledger, maker clock, then the meta with `complete: true` last, atomically; `analyze.load` refuses incomplete runs; the fire path reads the finished result once and prints no outcome; if the job fails or times out nothing is saved. A (chip, run) fires once: a pending or finished record refuses a second fire (use `recover.py`).

## THE CIRCULARITY AUDIT (printed at the top of every report)
Rule: a prediction is scored only if none of the data it was written from sits inside the measured quantity; if they overlap the row is BOX ON BOX and not scored. All **237** template quantities, by the stage at which the prediction is sealed (seen = what it was written from):

| sealed before | seen | r1 (41) | r2 (27) | r3 (55) | c combined (87) | drift (27) | **TOTAL scoreable (237)** | BOX ON BOX | own-run quantities |
|---|---|---|---|---|---|---|---|---|---|
| run 1 | none | 41 | 27 | 55 | 87 | 27 | **237** | 0 | 41 of 41 |
| run 2 | run 1 | 0 | 27 | 55 | 45 | 0 | **127** | 110 | 27 of 27 |
| run 3 | runs 1+2 | 0 | 0 | 55 | 0 | 0 | **55** | 182 | 55 of 55 |

(The 9 new matched quantities: `c.Fm.n2.*` and `c.effm2.*` contain runs 2+3 and are scoreable at stage 2; `c.hunterm.*` contain all three and are scoreable only from a prediction written before run 1.) Own-run quantities: 41 / 27 / 55 scoreable.

## Shot count and seconds
**ONE shot count for all nine jobs: 839 shots per circuit.** Method: 3.0 s per job (measured from the real echo run) + shots x (rep_delay 500 us + looks x 2.2 us + the realized waits). Largest S with the nine-job per-job total <= 100 s (`common.size_shots`, margin 33 s of 133 s, and 1.25 x 100 = 125 <= 133 so the guard can pass on a fresh account).

| per chip, 839 shots | Run 1 (9 circ.) | Run 2 (9 circ.) | Run 3 (18 circ.) | per chip | **three chips (nine jobs)** |
|---|---|---|---|---|---|
| **per-job estimate** (3.0 s per job + sequence) | 8.30 s | 8.32 s | 16.69 s | 33.31 s | **99.94 s** |
| **worst case** (3.0 s per circuit + sequence) | 32.30 s | 32.32 s | 67.69 s | 132.31 s | **396.94 s** |

**The worst case cannot fit nine jobs, or even one chip's three runs plus anything else, at any shot count** (324 s from the circuit charge alone). If the 3.0 s is really per circuit, the account is dry after about 4 jobs. The per-job basis is what the guard uses; the worst case is printed beside it at every fire.
**The fire guard:** a job may start only if the account's remaining seconds >= 1.25 x (this job's per-job estimate + the per-job estimates of every job not yet landed, all chips). On a fresh 133 s account the first job needs 124.9 s. **If the usage call returns no `usage_remaining_seconds` field (or a non-number) the guard REFUSES** (tested: `{}`, None, NaN, string -> refused; 133 -> passes for all nine; 100 -> refuses). That field exists only when the account answer has a limit or allocation field (qiskit-ibm-runtime builds it); it was NOT read in this pass, so whether the paid instance supplies it is unconfirmed until the first fire call.
**Firing order that loses the least if time runs out: run-major, OURS then MAKER then BLANK within each run** (`FIRE_ORDER`): 1-ours, 1-maker, 1-blank, 2-ours, 2-maker, 2-blank, 3-ours, 3-maker, 3-blank. Cumulative per-job seconds: 24.9 after run 1 on all three chips, 49.9 after run 2, 99.9 after run 3. Run 3 is the largest (16.7 s each) and the last, so if time runs short only the self-effect equation (needs all three runs) is lost, and the three-chip side-by-side of runs 1 and 2 (message and clock) survives. Chip-major order would keep each chip's three runs close in time (less kernel/frame drift between a chip's jobs, risk 4) but a shortfall would cost a whole chip and with it every three-chip comparison. Say if you prefer chip-major; the guard counts every job not yet landed in either order.

## Commands (never run by the builder)
`PY=~/bones-forge/venv_quantum/bin/python`, `cd /Users/heuremen/bones-forge/parallax/out/qubit_three_runs`. K = ibm_kingston (OURS), M = ibm_phoenix (MAKER), B = ibm_pittsburgh (BLANK). **Order (run-major):**
```
# STAGE 1
$PY analyze.py --make-template pred_1.json
$PY freeze.py --run 1 --chip ibm_kingston  --box ours    # live read-only qubit list; groups drawn and written to the freeze
$PY freeze.py --run 1 --chip ibm_phoenix   --box maker   # reads the maker's published calibration = its prediction
$PY freeze.py --run 1 --chip ibm_pittsburgh --box blank  # no account contact
#   SEAL + POST prediction 1 (fill pred_1.json AFTER the freeze: _run, _written_at, per entry written_at/data_seen/predicted/width)
$PY run1.py --fire --chip ibm_kingston   --box ours  --prediction-file pred_1.json --confirm-submit
$PY run1.py --fire --chip ibm_phoenix    --box maker --confirm-submit
$PY run1.py --fire --chip ibm_pittsburgh --box blank --confirm-submit
$PY analyze.py run1 --chip ibm_kingston --predictions pred_1.json     # OURS; (MAKER: analyze.py run1 --chip ibm_phoenix). BLANK refuses until all nine landed
# STAGE 2: freeze 2 (K, M, B) -> seal prediction 2 (written from run 1 of ibm_kingston only) -> fire 2 (K, M, B) -> analyze.py run1+2 --chip ibm_kingston --predictions pred_2.json
# STAGE 3: freeze 3 (K, M, B) -> seal prediction 3 -> fire 3 (K, M, B) -> analyze.py run1+2+3 --chip ibm_kingston --predictions pred_3.json
# AFTER ALL NINE HAVE LANDED:
$PY analyze.py all --data-dir data/fire --predictions pred_1.json pred_2.json pred_3.json
# if a job's result was lost or the process died after submit:
$PY recover.py --run N --chip C --box B        # (--find, then --use-id ID, if the id file is missing)
```
Dry-run any step first: `$PY runN.py --dry-run --chip C --box B` (synthetic, no account) and `$PY runN.py --list-circuits`. Real results land in `data/fire/<chip>/`. Without `--confirm-submit` a fire call builds, checks the freeze, reads the account (usage, the chip's configuration; for OURS/MAKER also its properties) and the guard, prints the budget line and STOPS: that is a read-only first contact.

## REMAINING FIRE-PATH RISKS (read against qiskit-ibm-runtime 0.49.0 and qiskit 2.5.2; NOT tested on hardware)
1. **Mid-circuit measurement together with `meas_type="kerneled"`, one register per look, has never been run by anyone.** The client raises no objection; the server may. Unknown whether a rejected job is billed.
2. **Shot order is not guaranteed by the API.** The documented result is a `(num_shots, creg_size)` array per register; nothing documents that row i is the i-th shot executed. If order is not kept, the carry-over reading is meaningless (it would read near zero) and cannot tell you so. Also the column order of the nine qubits (column j = the j-th qubit of the sorted list) is assumed, and `collect_results` cannot check it.
3. **The BLANK submit uses private SDK attributes** (`SamplerV2._backend`, `._service`, `service._run`) around a stub: tested only against fakes and against kingston's configuration path with a recorder standing in for the send; the real submit has not happened. It skips the client's ISA check (structure is checked by `check_structure` only), so a native-gate or timing problem on the BLANK chip would be rejected by the server, not caught before. If BLANK's native set lacks `sx` or `x`, its job is rejected (unknown for these chips; OURS and MAKER are checked against their live target).
4. **A blind qubit that is dead or listed faulty may make the server reject the whole BLANK job** (no pre-check by rule, and the SDK's `check_faulty` is bypassed). The result would be a failed job, not a row.
5. **Kernel and frame drift between the jobs.** Raw I/Q units belong to a job's calibration; run 1 is read in a frame built from runs 2 and 3. Calibration stamps are recorded per run; nothing corrects. In run-major order a chip's three jobs are far apart (sealing and posting predictions between stages).
6. **rep_delay 500 us is about 1.7 x the maker T1 median (292 us)**; `init_qubits` is a passive reset. The new carry-over reading measures exactly this; no correction.
7. **The guard's basis is the per-job estimate (3.0 s per job from a one-pub job), with 25 % margin and about 8 s spare on 133 s.** Our jobs have 9 or 18 pubs; if the service charges more than about 33 % over the estimate, later jobs are refused by the guard (run-major order puts the least valuable job last). `usage_remaining_seconds` unconfirmed (see above).
8. **max_execution_time** can still be too tight if the real run is far slower than the estimate; then the job is cancelled, nothing returned, billed up to the cap.
9. **A (chip, run) with a pending file and no job file refuses a second fire** (a crash between pending and submit leaves one): delete the pending file only after `recover.py --find` shows no job.
10. **Timing alignment.** The live target reports granularity 1 and alignments 1 (so no scheduling pass was added), but circuits are not run through any scheduling pass and the real hardware constraint (16 dt) is respected by construction for the waits only.
11. **Chips differ.** MAKER's and BLANK's dt, native gates, and qubit count are unknown until their configuration is read at fire time. The waits close for any dt (asserted), but the estimate and the shot sizing assume dt = 4 ns.
12. Account contact that cannot be avoided: the service constructor does two instance-resource lookups, and every OURS/MAKER fire reads that chip's calibration (design); BLANK's configuration read is the only look it gets, at the moment of its run.

## Choices to confirm with Wayfinder
1. Shot count 839 (per-job total 99.9 s of 133 s, guard need 124.9 s, 8 s spare). The largest count the guard can accept at all is 913 (per-job total 106.4 s; 1.25 x = 133); 1219 would use all 133 s with no margin and the guard would refuse it. I chose 100 s as the margin because the 3.0 s per job comes from a one-pub job and ours have 9 or 18 pubs.
2. Guard basis = per-job estimate x 1.25 (the worst-case basis cannot pass for nine jobs).
3. Firing order run-major (above).
4. BLANK reads the chip's static configuration (N, dt) at fire time. Alternative needs a documentation source for N and dt that I could not find.
5. MAKER's prediction = median published T1 of its nine qubits, sd as width, fading-time quantities only.
6. OURS predictions may be written only from ibm_kingston's own runs.
7. Items 1-5 of the opening ledger section: exact times and the cost-limit amount are not on file.
8. F(2) pooled by last wait is kept as the unmatched version beside the matched hunter (fix 1).

## Dry runs and analysis passes (all synthetic, code path only)
`data/dryrun/<chip>/` for ibm_kingston (OURS), ibm_phoenix (MAKER), ibm_pittsburgh (BLANK): `run{1,2,3}_results.npz`, `_meta.json`, `_look_ledger.json`, `_maker_clock.json` (not for BLANK), `analysis_*.json`, plus `data/dryrun/analysis_all.json`. **All nine dry runs ran at 839 shots; every analysis mode exited 0:** `run1`, `run1+2`, `run1+2+3` on OURS and MAKER, `run1` on BLANK (all nine landed, so it opened), and `all` (the three chips side by side, with the matched hunter, the unmatched pooled hunter, the carry-over rows, the per-qubit rows, the look ledger with its opening section, and the circularity audit). Each prints its ledger check. The scratch-copy flow (`/tmp/qtr_copy`, fake freezes) also exercised freeze -> prediction -> dry run -> scoring for OURS (3 stages, BOX ON BOX rows), MAKER scoring from the freeze-file calibration, and the refusals. Unit tests (`/tmp/qtr/test_units.py`): waits close on the grid at three different dt, guard refusals/passes, max_execution_time bounds, job id on disk before the wait, timed-out job, recover (all four cases), the BLANK stub, chip draw and refusals, blind draw: all pass.

## Files
`out/qubit_three_runs/`: `common.py`, `live.py`, `run1.py`, `run2.py`, `run3.py`, `analyze.py`, `freeze.py`, `recover.py`, `predictions_template.json` (237), `account_reads_log.jsonl`, `live_kingston_readonly_20261001.json`, `data/dryrun/`; previous: `*_v2.py`, `predictions_template_v2.json`, `data/dryrun_full`, `data/dryrun_min`; v1: `*_v1.*`, `data_v1/`, `live_probe_v1_NOT_RUN_THIS_PASS.py`.
