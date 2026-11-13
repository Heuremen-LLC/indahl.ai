# QUBIT THREE RUNS ON THREE CHIPS -- BUILD REPORT v4, 2026-10-01 night (fixes A-L)
Spec (the only design): `QUBIT_THREE_RUNS_APPROVED_20261001.md` (THE CARD, binding) incl. the night amendments. Code: `out/qubit_three_runs/`. The previous build is kept as `*_v3` (`common_v3.py`, `live_v3.py`, `run1_v3.py` ... `analyze_v3.py`, `freeze_v3.py`, `recover_v3.py`, `predictions_template_v3.json`, `predictions_run1_ours_DRAFT_v3.json`, and the previous text of this report `QUBIT_THREE_RUNS_BUILD_20261001_v3.md`); older: `*_v2`, `*_v1`.

**THE DRY RUNS PROVE THE CODE PATH, NOT THE PHYSICS.** The local simulator has no raw I/Q: every I/Q number in every dry run is SYNTHETIC (fabricated from simulated 0/1 outcomes plus an injected fade and an injected per-look mark). Nothing a dry run says is about a qubit.

**This pass: `--fire` was never called, no job was submitted, the IBM account was NOT contacted at all** (no usage, no backend list, no token use). **Nothing was queried, read or looked up about ibm_phoenix, ibm_pittsburgh or ibm_boston from any source**: the names appear in the code only as labels from the written-seed assignment, and the tests ran against local fakes with the HTTP origin replaced by a local stub *before* the guard was installed, so a bug could not have reached the network. `account_reads_log.jsonl` in the build folder was not touched (its last line is still the 22:00 entry from the earlier pass; tests wrote to a scratch log).

## THE FIXES (A-L), what each does now
| # | fix | status |
|---|---|---|
| A | The machine's reset is a look: sampler options pinned; the reset is a ledger entry on every circuit of every chip; Run 1 relabelled | DONE, tested |
| B | THE RETURN PASS (analysis, combined mode run 1+2+3) | DONE, tested on synthetic I/Q |
| C | Scoring recomputes the prediction file's sha256 and refuses unless it equals the hash recorded at fire; refuses entries dated after the run start or before the freeze | DONE, tested |
| D | Every account/chip read made by fire() is logged at the moment it happens, refused / failed / no `--confirm-submit` included | DONE, tested |
| E | Raw payload saved untouched first; parsing reads the saved payload; `recover.py --reparse`; parser in `parse_payload.py`, outside the freeze | DONE, tested |
| F | MAKER chip read once, at freeze; at fire it goes the blind submit path; numbers from the freeze file | DONE, tested |
| G | BLANK's configuration read and the SDK's status fetch are the accepted minimum, happen at the instant of firing, are ledger looks; the HTTP guard allows nothing else for that chip and logs every request | DONE, tested against fakes (never on the real SDK/server) |
| H | fire() refuses unless every earlier job in the fixed run-major order has landed | DONE, tested |
| I | max_execution_time = the code's own worst case, capped by what the account can spare; printed | DONE, tested (table below) |
| J | The two identity quantities dropped from the template and the draft; stale note fixed | DONE (template 237 -> 235) |
| K | NOTED list: failed faulty-qubit lookup refuses (OURS); missing maker T1/T2 printed CAN'T READ with reason; NaN qubits in a pooled median counted and printed; end_time from the job's metadata; analyze default dir is data/fire | DONE, tested |
| L | `freeze.py --all-run N` | DONE, tested in a scratch copy against fakes; NOT run against the live account |

### A. The machine's reset is a look
- **Sampler options now pinned explicitly** (`common.PINNED_OPTIONS`, `pin_sampler_options`, called on every fire; the dry run builds the same object and records it): `execution.init_qubits = True`, `dynamical_decoupling.enable = False`, `twirling.enable_gates = False`, `twirling.enable_measure = False`, plus the ones we always set: `execution.meas_type = 'kerneled'`, `execution.rep_delay = 0.0005`, `max_execution_time`, `environment.job_tags`. The fire path refuses to continue if any pinned value is not what it should be.
- **Every option `SamplerV2` exposes in qiskit-ibm-runtime 0.49** (read off `SamplerOptions`): `max_execution_time`; `environment.{log_level, job_tags, private}`; `simulator.{noise_model, seed_simulator, coupling_map, basis_gates}` (local sim only); `default_shots`; `dynamical_decoupling.{enable, sequence_type, extra_slack_distribution, scheduling_method, skip_reset_qubits}`; `execution.{init_qubits, rep_delay, meas_type}`; `twirling.{enable_gates, enable_measure, num_randomizations, shots_per_randomization, strategy}`; `experimental`; `_VERSION`. **There is NO measurement-mitigation / resilience option in SamplerV2 0.49 at all** (`SamplerOptions` has no such field), so there is nothing to switch off; the report says so rather than pinning something that does not exist. The sub-options of DD and twirling (sequence type, strategy, number of randomizations...) are left Unset because they only act when `enable` is True and it is pinned False.
- **Evidence the pins reach the wire:** a test captures what the SDK hands to the service (`inputs['options']`): `{"dynamical_decoupling": {"enable": false}, "twirling": {"enable_gates": false, "enable_measure": false}, "execution": {"init_qubits": true, "rep_delay": 0.0005, "meas_type": "kerneled"}}`, runtime options `max_execution_time, log_level, job_tags, private, backend, instance`. All six are sent explicitly now, not left to server defaults. (The test used a fake service; the real server's behaviour on them is untested.)
- **The ledger.** Every circuit of every run on every chip carries `machine_reset`: *"THE MACHINE'S RESET (init_qubits): the maker's own action before our START; counted as a look by the machine; identical on all three chips; whether it reads the bit cannot be confirmed from code."*, `when: at the start of each shot, before our START`. `ledger_self_check` counts it: every circuit must carry exactly that entry, `n_machine_resets_per_shot` must equal the number of circuits (9 / 9 / 18), and `machine_reset_events_total` (circuits x shots: 7551 / 7551 / 15102 per chip) must be a whole number of shots per circuit. A ledger with a missing or altered entry is refused (tested). The analysis prints the reset line, its counts and the pinned options for every run.
- **Relabelled everywhere:** Run 1 = "zero earlier looks **of ours (after the machine's reset)**" (code, plain-words circuit lines, report titles, docstrings, the `sits` text of the ledger, the three clocks header, the matched-hunter text). Look 2 / look 3 counts of earlier looks are our looks only, the same words.

### B. THE RETURN PASS (combined mode run 1+2+3 only)
Run 3 solves each look's own error from the other two (the three-cornered-hat solve, `hat1` = the first look's own error variance). The return pass carries that solved first-look error back onto Run 1's lone look, per start (OFF / MID / ON, and ALL = the mean of the three) and per wait (60 / 240 / 300), each row with its bootstrap width and the group-of-three spread:
- `ret.<start>.w<wait>.measured` = the spread (variance, in OFF-to-ON separations squared) of Run 1's lone look as measured;
- `ret.<start>.w<wait>.look` = the part attributable to the look = Run 3's solved first-look error variance for that start (pooled over the six layouts);
- `ret.<start>.w<wait>.remains` = measured minus that part. **THE REMAINDER:** printed raw, negatives kept, never zeroed, no verdict word, with `ret.remainder_rms` and a line in the closing "THE REMAINDER" sentence ("THE RETURN PASS (runs 1 and 3, Run 3's frame) = x +-w (n widths)").
- **One frame, chosen so the rows hold exactly Run 1 and Run 3 data:** Run 3's own frame (look 1 of every OFF and every ON circuit of Run 3). Run 1's looks are projected into it. No Run 2 data enters. (The other combined quantities use a frame from runs 2+3; those rows contain runs 2 and 3.)
- **Stated plainly, so the remainder is read right:** Run 3's first look has no wait before it, Run 1's lone look sits after a wait. The part carried back is the same number at each wait; nothing is rescaled for the wait (that would be invented physics). Whatever depends on the wait therefore lands in THE REMAINDER by construction. The units are variances (a spread cannot be subtracted from a mean level), so "Run 1's reading" here is the spread of its look, not its mean.
- **Box-on-box audit:** `data_of('ret.*') = {1, 3}`. The audit prints, in every report, "THE RETURN PASS rows ... data inside = runs [1, 3] ... written from run 1 (shared [1]) or runs 1+2 (shared [1]): BOX ON BOX, not scored; written from nothing or the maker's numbers: scoreable." If a prediction file contains a `ret.*` name, scoring applies the same overlap rule (tested). The return-pass names are not in the sealable template (no prediction is asked for them).

### C. The prediction file cannot be edited after the fact
Scoring reads the prediction file once as bytes, compares its sha256 with the hash recorded in the run's meta at fire, and parses those same bytes; unequal -> REFUSED, nothing scored (tested: a single edited number refuses; restoring the sealed copy, which the fire path also saves as `run{N}_prediction_sealed_copy.json`, scores again). Each entry's `written_at` must be inside [freeze, run start]; an entry dated after the start or before the freeze is "not scored" with the reason, others still score (tested both). At fire, `check_freeze` also refuses a header or entry dated in the future. The ruler identities are never scored even if present.

### D. Reads are logged even when the fire fails
`fire()` writes every account/chip read to `account_reads_log.jsonl` the moment it has happened (account reads; the chip's configuration; OURS' properties; the requests at the instant of firing; and always a final line "NO job submitted: refused, failed, or no --confirm-submit" or "job submitted"), through a `finally`. The same entries go to `run{N}_fire_reads.json` and from there into the run's look ledger as `reads_at_fire`. Tested: a fire without `--confirm-submit`, a fire refused by the budget guard, and a fire that fails in parsing each leave their reads in the log. **New behaviour, said plainly:** for MAKER and BLANK a fire without `--confirm-submit` stops after the account usage read and the budget guard and does NOT touch the chip at all (its configuration read is a look and belongs to the instant of firing); OURS, as before, reads its own configuration and properties on a no-confirm check.

### E. The raw payload is saved first; the parser is outside the freeze
- Sequence after submit: job id to disk (fsync) -> wait once for the final state -> **raw results payload saved untouched** (`run{N}_payload_raw.json`: the service's own JSON text for the job's results; fsync'd, atomic; with `run{N}_payload_meta.json` = its sha256, how it was obtained and the job's own metadata) -> only then parsed, **from the saved payload**, by `parse_payload.py`.
- **`recover.py --reparse --run N --chip C --box B`** rebuilds the results file from the saved payload: no network, no account contact (tested: zero requests). An existing result set is moved aside (`*.before_reparse_<stamp>`), never deleted. A failed parse leaves the payload on disk and the job file says `--reparse`.
- **Said plainly: `parse_payload.py` is NOT part of any freeze hash (`code_files()` lists `common.py`, `live.py`, `run{N}.py`, `analyze.py` only), on purpose.** The real kerneled result of a circuit with three measurements on the same qubits has never been parsed by anyone; the shape or field names assumed in the parser may be wrong. If the parser were inside `common.py`, repairing a wrong assumption would change the freeze hash and make the run unscorable. The payload is saved untouched before the parser runs, so a repair can change how the data is read, never what the machine returned. Every results file records the sha256 of the payload and of the parser that read it (`meta.parser_sha256`), and the report prints both. What stays inside the freeze is the VALIDATION (`verify_arrays`: exact set of looks from the ledger, shape (shots, 9), complex, finite), which a parser cannot loosen. Tested: editing `parse_payload.py` leaves the freeze hash unchanged; editing `analyze.py` changes it.

### F. The MAKER chip is read once
The MAKER's published calibration (T1/T2/readout of the nine qubits, calibration stamp, qubit count) is read **once, at the run-1 freeze**. The freezes of runs 2 and 3 **copy** the run-1 numbers and groups (`maker_calibration_copied_from`); the chip is not asked again. At fire time the MAKER chip uses the same blind submit path as BLANK: no properties, no target, no faulty-qubit check; its groups and clock come from the freeze file (the qubit count read at fire must equal the freeze's). The report prints only the freeze-time numbers (`maker_clock_source` says "FREEZE FILE (read once, at freeze time ...)"). Tested: zero properties requests and zero properties calls for the maker at fire. OURS (ibm_kingston) may still read its own properties at fire time; the fire prints, and the meta records, **both calibration timestamps** (`calibration_timestamp_at_freeze`, `calibration_timestamp_at_fire`). A failed faulty-qubit lookup at the MAKER's one freeze-time read is recorded loudly in the freeze file (`faulty_lookup: FAILED: ...`) instead of refusing (a refusal would force a second read of that chip); for OURS it refuses (K).

### G. The BLANK chip: the minimum, at the instant of firing, as looks
`fire()` for BLANK (and MAKER): open service + usage -> budget guard on the nominal estimate -> (only with `--confirm-submit`) **configuration read** -> build -> real-dt estimate and guard -> pending file -> `sm.run`, during which the SDK fetches the **status** -> POST job. The two chip reads are written to the ledger as *"THE CHIP'S SIZE AND TIMING TICK (its static configuration: qubit count, dt, rep_delay range) ... a read of the chip"* and *"IS IT UP (the status the SDK fetches at submit) ... a read of the chip"* (`reads_at_fire`). The HTTP guard (`live.py`) now allows a blind chip **only** `/configuration` and `/status` (anything else naming it, including `/properties`, `/defaults`, `/target`, the bare chip URL, any other sub-path, is refused), refuses the left-alone chip, any other host, and any job POST without `--confirm-submit`, and **logs every request it sees in every branch** (allowed or refused; the old code left one refusal branch unlogged). Tested against fakes: exactly two requests name the BLANK chip, `configuration` and `status`. **Never tested against the real SDK/server:** if the SDK makes any other request naming a blind chip, the guard will refuse it and the fire will fail loudly before submit, with the refusal in the log.

### H, I. Fire order and the execution cap
**H.** `fire()` refuses unless every earlier job in the fixed order has landed (complete marker). Order, run-major: run 1 on ibm_kingston, ibm_phoenix, ibm_pittsburgh; then run 2 in that order; then run 3. The refusal lists what has not landed. Tested (run 2 before run 1, blank before ours/maker, ...). A job that failed counts as not landed, so nothing later fires until it is recovered.
**I.** `max_execution_time = min( ceil(this job's own worst case = 3.0 s per circuit + sequence), floor(remaining seconds - per-job estimates of the jobs still to come) )`, printed with both terms and which one binds; if it would fall below the job's own per-job estimate the fire refuses. With a fresh 133 s account and each earlier job using its estimate, the nine caps are:

| job | per-job estimate | worst case (3.0 s x circuits + seq.) | remaining before | later jobs' estimates | **max_execution_time** | binds |
|---|---|---|---|---|---|---|
| run 1 ibm_kingston | 8.30 s | 32.3 s | 133.0 | 91.6 | **33 s** | worst case |
| run 1 ibm_phoenix | 8.30 | 32.3 | 124.7 | 83.3 | **33 s** | worst case |
| run 1 ibm_pittsburgh | 8.30 | 32.3 | 116.4 | 75.0 | **33 s** | worst case |
| run 2 ibm_kingston | 8.32 | 32.3 | 108.1 | 66.7 | **33 s** | worst case |
| run 2 ibm_phoenix | 8.32 | 32.3 | 99.8 | 58.4 | **33 s** | worst case |
| run 2 ibm_pittsburgh | 8.32 | 32.3 | 91.5 | 50.1 | **33 s** | worst case |
| run 3 ibm_kingston | 16.69 | 67.7 | 83.1 | 33.4 | **49 s** | remaining minus later jobs |
| run 3 ibm_phoenix | 16.69 | 67.7 | 66.4 | 16.7 | **49 s** | remaining minus later jobs |
| run 3 ibm_pittsburgh | 16.69 | 67.7 | 49.8 | 0 | **49 s** | remaining minus later jobs |

Totals: nine jobs = **99.94 s** by the per-job estimate (shots 839, unchanged); the fire guard needs 1.25 x (this + every job not yet landed) = 124.9 s at the first fire. The live caps are computed from the real remaining seconds the usage call returns, so they will differ if jobs bill more or less than their estimates. **The cap is a cancel:** a job that hits it returns nothing (RuntimeJobMaxTimeoutError, reason 1305) and the time up to the cap is presumably billed. The worst case (3.0 s per circuit) cannot be covered for all nine jobs at any shot count (108 circuits x 3.0 s = 324 s), which is why the guard stays on the per-job basis.

### J, K, L
- **J.** `r1.OFF.w60.mean` and `r1.ON.w60.mean` are not in `predictions_template.json` (now **235** quantities) or `predictions_run1_ours_DRAFT.json` (50 predicted numbers unchanged, none touched). They are still measured and printed in the report, labelled "ruler identity: 0 / 1 by construction, never predicted or scored". The template's stale note (boxes rotating per group) is replaced by the whole-chip text. The fading time for an OFF start (`r1.tauF.OFF`, `c.tauF.n0.OFF`) stays in the template as NO BASIS (null).
- **K.** (1) `candidates_from_backend` raises `FaultyLookupFailed` for OURS when the faulty-qubit lookup fails (freeze and fire both refuse). (2) `maker_clock` keeps the reason for every missing T1/T2/readout/timestamp; the report prints "CAN'T READ: n of m qubits have a published T1 (need 2); reasons: ..." and every pair that needs it is CAN'T READ; maker scoring prints CAN'T READ with the reason instead of silently skipping. (3) Every pooled row records `n_qubits_dropped_nan` / `n_qubits_pooled` and `line()` prints "[k of n qubits NaN: dropped from the pooled median]" (also for the carry-over rows). (4) `end_time` (and the job's running stamp) come from the job's own metadata (`metrics().timestamps`); if absent it is None, and the report prints CAN'T READ for "time between runs"; the client clock is never used instead. (5) `analyze.py --data-dir` defaults to `data/fire`; pass `--data-dir data/dryrun` for synthetic data. Also: `recover.py --use-id` no longer silently ignores an existing job file (it says so).
- **L.** `freeze.py --all-run N` freezes run N on all three chips (from the written-seed assignment): OURS reads the live chip, MAKER reads its chip at run 1 and copies at runs 2 and 3, BLANK hashes code and seed only (no account contact). One account open serves the chips; refuses to overwrite without `--refreeze`; refuses `--run/--chip/--box` beside it; refuses the left-alone chip. Tested with `--fake` in a scratch copy for runs 1, 2, 3; **not run against the live account.**

## Where it broke first (this pass)
In the order found:
1. **Nothing in the old fire path logged reads before the end** (it was the mechanical check's MUST FIX 3; confirmed by tracing the code): a refused fire left no trace. Fixed at the source: reads are logged where they happen, plus a forced final line, so even a fire that read nothing leaves its outcome.
2. **The old guard left one refusal branch unlogged and allowed anything-but-"properties" on a blind chip.** Replaced by an allow-list (configuration and status only) and logging in every branch.
3. **My first end-to-end fake fire failed an assertion that looked like a bug and was not:** the pinned options are not at the top of what the SDK hands over but under `inputs['options']`; the assertion read the wrong level. Corrected the test; the evidence above is the corrected one.
4. **A test I wrote for the "entry dated after the run start" refusal first failed because my own test file's header date was later than the run start** (the header is also bounded by the start): the refusal that fired was the right one. Corrected the test to isolate the entry rule.
5. **A relabelling edit broke `analyze.py` with a quote inside a single-quoted string** (the apostrophe in "machine's reset"). Caught at import, fixed, and the full flow rerun afterwards.
6. Carried-over limit, not new: **the simulator still cannot do kerneled readout or fade during a WAIT** (3 simulator breaks are recorded in every dry run's meta); the dry run therefore substitutes synthetic I/Q and an injected fade. That is the "code path, not physics" boundary.

## What each run is, in plain words
START: **OFF** (nothing put in), **MID** = both-and-neither (one `sx`), **ON** (`x`). LOOK: one reading of the qubit, raw I/Q kept every time. WAIT: a pause. Waits: short 60, medium 240, long 300 us, laid on the 16-dt grid with short + medium = long exactly (realized 59.968 / 240.000 / 299.968 us at dt 4 ns). **Every shot of every circuit begins with the machine's reset (init_qubits), which is not ours and is counted in the ledger.**
- **Run 1, zero earlier looks of ours (after the machine's reset):** START, WAIT, LOOK. 3 starts x 3 waits = 9 circuits, 9 looks.
- **Run 2, one earlier look:** START, LOOK, WAIT, LOOK. 9 circuits, 18 looks.
- **Run 3, two earlier looks, mirrored twins:** START, LOOK, WAIT a, LOOK, WAIT b, LOOK; twins {60,240} (matched: a+b = 300), {60,300}, {240,300}, each in both orders. 18 circuits, 54 looks.
- 81 looks of ours per chip, 243 on three chips; 36 circuits per chip, 108 on three chips; 839 shots per circuit. Same nine qubits (three groups of three) in all runs of a chip. Circuit order: seeded shuffles (run 1 seed 20261011, run 2 20261012, run 3 20261013). One job per (chip, run). No calibration or test circuits (OFF and ON are the calibration and the data at once; enforced by the ledger self-check, `check_ledger_vs_circuits` and `verify_arrays`). The full circuit lists are printed by `python run1.py --list-circuits` (and run2, run3), each line now opening with the machine's reset.

## The look ledger
1. **THE MACHINE'S RESET** (fix A): one entry per circuit, at the start of each shot, on every chip (9 / 9 / 18 per run per chip; 7551 / 7551 / 15102 events per run per chip). Counted by the self-check.
2. **LOOKS TAKEN BEFORE RUN 1** (opening section, unchanged text): the five earlier read-only account/calibration looks of the earlier passes (their exact times and the cost-limit amount are not on file; edit `PRE_RUN1_STATIC` in `common.py`; see the note below) and every entry of `account_reads_log.jsonl` made before run 1 started. None touched a bit.
3. **READS AT FIRE** (`reads_at_fire`, new): every account and chip read the fire itself made, in plain words. **BLANK and MAKER: exactly two chip reads: "size and timing tick" (configuration) and "is it up" (status).** OURS: configuration, calibration/properties, status.
4. Per circuit: the count of looks and, for each look, how many looks of ours came before it, the wait just before and just after it (requested and realized).
Note: `PRE_RUN1_STATIC` sits in `common.py`, which is hashed, so correcting those five lines must be done BEFORE the freezes.

## The three boxes (whole chips)
| box | chip | prediction | what is read | freeze hashes |
|---|---|---|---|---|
| OURS | ibm_kingston | our sealed numbers + widths, one file per run | live qubit list + calibration at each freeze; configuration + properties + status at fire | code + ledger + groups |
| MAKER | ibm_phoenix | its published calibration, read ONCE at the run-1 freeze, is the only prediction | at the run-1 freeze: calibration. At fire: configuration + status only (blind path) | code + ledger + groups + the numbers |
| BLANK | ibm_pittsburgh | none (a file is refused) | at fire: configuration + status only | code + the seed only |
| left alone | ibm_boston | -- | never touched in any way (the guard refuses any URL naming it) | -- |
(Chip assignment comes from the written seed `SEED_CHIPS = 20261061`; a pure function, no account contact.)

## THE CIRCULARITY AUDIT
Printed first in every report; reads only prediction headers. Scoreable counts by the stage at which a prediction is sealed (template of 235; the return-pass rows are marked separately, see B):

| sealed before | seen | r1 (39) | r2 (27) | r3 (55) | c (87) | drift (27) | **TOTAL (235)** |
|---|---|---|---|---|---|---|---|
| run 1 | none | 39 | 27 | 55 | 87 | 27 | **235** |
| run 2 | run 1 | 0 | 27 | 55 | 45 | 0 | **127** |
| run 3 | runs 1+2 | 0 | 0 | 55 | 0 | 0 | **55** |

## EXACT COMMAND SEQUENCE (never run by the builder)
`PY=~/bones-forge/venv_quantum/bin/python`, `cd /Users/heuremen/bones-forge/parallax/out/qubit_three_runs`. K = ibm_kingston (OURS), M = ibm_phoenix (MAKER), B = ibm_pittsburgh (BLANK). **Freeze only when the code is final: any edit to `common.py`, `live.py`, `run{N}.py` or `analyze.py` after a freeze makes that run unscorable. `parse_payload.py`, `recover.py`, `freeze.py` are outside the hash.**
```
### RUN 1
$PY analyze.py --make-template pred_1.json          # (once) a blank prediction file; 235 quantities
$PY freeze.py --all-run 1                           # FREEZE ALL THREE CHIPS: K reads its live qubit list (groups drawn, written into the freeze);
                                                    # M's published calibration is read ONCE here; B hashes code + seed only (no account contact for B)
#   SEAL THE KINGSTON PREDICTION: fill pred_1.json NOW (after the freeze): _run = 1, _written_at, and per entry written_at / data_seen / predicted / width.
#   Only OURS (ibm_kingston) has a prediction file. Then:  shasum -a 256 pred_1.json   -> post the hash on indahl.ai BEFORE firing. Wayfinder reviews before the fire.
$PY run1.py --fire --chip ibm_kingston   --box ours  --prediction-file pred_1.json --confirm-submit
$PY run1.py --fire --chip ibm_phoenix    --box maker --confirm-submit    # refused until run 1 on ibm_kingston has landed
$PY run1.py --fire --chip ibm_pittsburgh --box blank --confirm-submit    # refused until ibm_kingston and ibm_phoenix have landed
#   (add nothing in between; do not count anything until it lands. Analysis of Kingston run 1 is allowed after it lands:
#    $PY analyze.py run1 --chip ibm_kingston --predictions pred_1.json   ; the BLANK chip's results are not opened by any mode until all nine have landed)
### RUN 2
$PY freeze.py --all-run 2                           # K re-reads its live list (refuses if the saved qubits are gone); M COPIES run 1's numbers (no second read); B code + seed
#   seal pred_2.json (data_seen = run1 at most), post its sha256
$PY run2.py --fire --chip ibm_kingston   --box ours  --prediction-file pred_2.json --confirm-submit
$PY run2.py --fire --chip ibm_phoenix    --box maker --confirm-submit
$PY run2.py --fire --chip ibm_pittsburgh --box blank --confirm-submit
### RUN 3
$PY freeze.py --all-run 3
#   seal pred_3.json (data_seen = runs1+2 at most), post its sha256
$PY run3.py --fire --chip ibm_kingston   --box ours  --prediction-file pred_3.json --confirm-submit
$PY run3.py --fire --chip ibm_phoenix    --box maker --confirm-submit
$PY run3.py --fire --chip ibm_pittsburgh --box blank --confirm-submit
### AFTER ALL NINE HAVE LANDED
$PY analyze.py all --predictions pred_1.json pred_2.json pred_3.json                  # the three chips side by side; --data-dir defaults to data/fire
$PY analyze.py run1+2+3 --chip ibm_kingston --predictions pred_3.json                 # includes THE RETURN PASS
### IF A JOB'S RESULT WAS LOST, OR THE PARSE FAILED
$PY recover.py --run N --chip C --box B             # re-reads a finished job by its saved id (--find, then --use-id ID, if the id file is missing)
$PY recover.py --reparse --run N --chip C --box B   # rebuilds the results from the SAVED raw payload with parse_payload.py: no network, no account
```
Option for the owner: freezing runs 2 and 3 *before the first fire* (`--all-run 2`, `--all-run 3` right after `--all-run 1`) locks the analysis code before any data exists, which closes the gap where analysis code could be adjusted between runs. Cost: any analysis fix after run 1 then breaks all later freezes. Predictions for runs 2 and 3 would still be written after their freezes. Not enforced by the code; your call.
`--confirm-submit` is the only thing that submits. Without it a fire stops after the guards (OURS: after its account and chip reads; MAKER and BLANK: before their chip is contacted at all). Dry-run any step first: `$PY runN.py --dry-run --chip C --box B [--prediction-file P]` (synthetic, no account) and `$PY runN.py --list-circuits`.

## STILL UNTESTED UNTIL REAL HARDWARE
1. **The real server's response to a job with three mid-circuit measurements on the same qubits and `meas_type='kerneled'`** (one register per look): accepted or not, and whether a rejected job is billed. The client raises no objection; nobody here has run it.
2. **The shape and naming of the returned payload.** `parse_payload.py` assumes `(shots, 9)` complex per register named `L1..Lk`. The raw payload is saved first, so a wrong assumption is repairable (`--reparse`), but the shape itself is unseen.
3. **Shot order** of the returned arrays is not documented as the order the shots ran; the carry-over reading is meaningless if it is not kept (it would read near zero and cannot say so).
4. **Whether the pinned options are honoured server-side** (init_qubits True, DD off, twirling off): they are sent explicitly (shown against a fake service), but the real server's behaviour is untested. **Whether the machine's reset reads the bit cannot be confirmed from code**; it is in the ledger as a look either way.
5. **The blind submit path against the real SDK and server** (private SDK attributes `SamplerV2._backend/_service`, `service._run`; works on 0.49 only). New this pass: it is used for MAKER as well as BLANK. The new guard allow-list (`/configuration`, `/status` only) has been tested against fakes; if the real SDK makes any other request naming a blind chip the fire fails loudly before submit. It also skips the client's ISA check; if a blind chip's native set lacks `sx` or `x` the server rejects the job. A blind qubit that is dead or listed faulty may make the server reject the whole job.
6. **`usage_remaining_seconds`**: whether the paid instance's usage answer supplies it (the guard refuses without it) and whether the service bills by the per-job basis (3.0 s per job) or per circuit (3.0 s x circuits would exhaust 133 s after about four jobs).
7. **`job.metrics()` timestamps** (`finished`, `running`) against the real service: if absent, end_time is None and the time-between-runs rows are CAN'T READ (by design, never the client clock).
8. **The maker chip's and blank chip's static configuration** (qubit count, dt, native gates): unknown until read at fire; the waits close for any dt (asserted), the estimate assumes dt = 4 ns.
9. **Kernel/frame drift between jobs** (raw I/Q units belong to a job's calibration); stamps are recorded, nothing corrects. Run 1 is read in frames built from other jobs.
10. **The real fade of a qubit across a WAIT and the real physics in every quantity**: nothing in a dry run says anything about them.

## Dry runs and tests (all synthetic / fake, code path only)
- **Nine dry runs** (3 runs x 3 chips, 839 shots) into `data/dryrun/<chip>/`, each now round-tripping its synthetic I/Q through a `RuntimeEncoder` payload and `parse_payload.parse` before saving; **every analysis mode** (`run1`, `run1+2`, `run1+2+3` on OURS and MAKER, `run1` on BLANK once all nine have landed, and `all`) with the circularity audit, the look ledger (machine's reset line, pinned options, payload and parser hashes), the carry-over rows, the per-qubit rows, THE RETURN PASS and THE REMAINDER. The logs and the results of the final run are listed at the end of this file.
- **Scratch-copy flow** (`/tmp/qtr4/flow`: `freeze.py --all-run 1,2,3 --fake`, predictions sealed after the freezes, nine dry runs with the prediction hash recorded, scoring in modes run1, run1+2, run1+2+3, all): scoring prints the hash line, BOX ON BOX rows for predictions written from run 1 on quantities containing run 1 (including a `ret.*` entry), the maker's miss from the freeze-time numbers, and refuses after a prediction file was edited.
- **Refusal tests** (all REFUSED as intended): BLANK chip analysed with only run 1 landed; `all` with one run; MAKER given a prediction file; the left-alone chip; run 2 before run 1; blank before ours/maker; fire without `--confirm-submit` (stops, and the maker/blank chip is not contacted); fire with 50 s in the account (BRAKE); blind chip properties/defaults/target/bare URL/any other path; non-IBM host; job POST without confirm; failed faulty lookup (OURS); prediction file edited after fire; entry dated after the start / before the freeze / in the future; ledger without the machine's reset; incomplete results; wrong chip/box pair; `--all-run` overwrite and mixed arguments.
- Unit/integration tests: `out/qubit_three_runs/tests_v4/test_v4.py` (builds a scratch copy of the code in /tmp, fake service, local HTTP stub; **103 checks, 103 PASS, 0 FAIL** in the final run). `tests_v4/flow.sh` is the scratch-copy flow (freeze --all-run with fakes, predictions, nine dry runs, scoring, refusals); `tests_v4/final.sh` is the final pass below.

## Files
`out/qubit_three_runs/`: `common.py`, `live.py`, `run1.py`, `run2.py`, `run3.py`, `analyze.py`, `freeze.py`, `recover.py`, **`parse_payload.py` (new; outside the freeze)**, `predictions_template.json` (235), `predictions_run1_ours_DRAFT.json` (50 predicted, identities removed), `account_reads_log.jsonl` (untouched this pass), `live_kingston_readonly_20261001.json`, `data/dryrun/`. Previous: `*_v3.py`, `predictions_template_v3.json`, `predictions_run1_ours_DRAFT_v3.json`, `../../QUBIT_THREE_RUNS_BUILD_20261001_v3.md`; older `*_v2`, `*_v1`, `data/dryrun_full`, `data/dryrun_min`, `data_v1/`.

## FINAL RUN (after the last code edit), all exit 0
Nine dry runs (3 runs x 3 chips, 839 shots): exit 0 each. Analysis on `data/dryrun`: OURS `run1`, `run1+2`, `run1+2+3`; MAKER `run1`, `run1+2`, `run1+2+3`; BLANK `run1` (allowed because all nine landed in the dry set); `all` (the three chips side by side, THE RETURN PASS included in every chip's rows): **exit 0 each.** `test_v4.py`: **103 PASS, 0 FAIL.** The scratch flow with predictions (`scratch_flow.out`) exercised scoring in run1, run1+2, run1+2+3 and all, the BOX ON BOX rows (including a `ret.*` entry written from run 1), the identity row never scored, the maker's miss from the freeze-time numbers, and the refusals (blank gate, `all` with one run, maker given a prediction file, left-alone chip, prediction file edited after fire). Logs: `out/qubit_three_runs/data/dryrun_logs_v4/` (`dry_*.log`, `an_*.log`, `test_v4.log`, `final_run.out`, `scratch_flow.out`). Every one of those reports says, at the foot, that the I/Q is synthetic and the run proves the code path only.
**The dry run proves the code path, not the physics.** A green dry run says the plumbing (freeze, guards, ledger, payload, parser, analysis, scoring, refusals) behaves as written against fakes and synthetic numbers. It says nothing about what a qubit will do, nothing about what the server will accept, and nothing about whether any number in any quantity means what we hope. The list under "STILL UNTESTED UNTIL REAL HARDWARE" is the boundary.
