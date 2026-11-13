# THE STONE SHOT -- BUILD REPORT, 2026-10-02
The same three-run qubit experiment (THE CARD in `QUBIT_THREE_RUNS_APPROVED_20261001.md` applies in full), on a FOURTH chip, **ibm_boston** (box name "stone"), with the waits taken from the stone table. Code: `out/qubit_stone_run/` (copied from `out/qubit_three_runs/` v4; that folder was not edited, nothing in its `data/` was opened or listed; no freeze or prediction files were copied).

**THE DRY RUNS PROVE THE CODE PATH, NOT THE PHYSICS.** The local simulator has no raw I/Q: every I/Q number in every dry run is SYNTHETIC (fabricated from simulated 0/1 outcomes plus an injected fade and an injected per-look mark). Nothing a dry run says is about a qubit.

**This pass: `--fire` was never called against the account, no job was submitted, the IBM account was NOT contacted at all** (no usage, no backend list, no token use, no token file read). Nothing was queried, read or looked up about ibm_boston, ibm_pittsburgh or ibm_phoenix from any source. The names appear in code only as labels and as a deny-list in the HTTP guard. The fire path was tested in a scratch copy under /tmp against fakes, with the HTTP origin replaced by a local stub *before* the guard was installed, so a bug could not reach the network. No freeze files exist in the build folder (freezing was tested in the scratch copy), and `account_reads_log.jsonl` does not exist yet.

## Where it broke first
In the order found:
1. **The three-box machinery was wired through everything** (chip assignment by seed, OURS/MAKER/BLANK branches in fire, freeze, scoring, the nine-job fire order, prediction files, the audit, the side-by-side of chips). Nothing about it applies here, so it was cut out rather than left as dead paths: one chip, one box, no prediction file, no miss column, fire order 1 -> 2 -> 3.
2. **First sizing came out as a placeholder:** `SHOTS` was set to 0 in the copy until the sizer ran; `freeze.py` refuses while it is 0 (kept as a guard). Sizer result: 555.
3. **The simulator-break probe for "no fading during a WAIT" did not fire** (my first rewrite compared a bit mean to a threshold that the readout noise already satisfied; 2 breaks recorded instead of 3). Replaced by a direct comparison (ON after the long wait against ON after the short wait, Run 1): the third break is now recorded again. Simulator breaks are data; there are 3 in Run 1 and 2 in Runs 2 and 3: kerneled readout not modelled locally, rep_delay ignored locally, and (Run 1) no fade across a delay locally. The dry run injects a labelled synthetic fade instead.
4. **Two assertions in my scratch test failed and were test errors, not code errors:** (a) a refused fire does leave its read log in the results folder (reads are logged where they happen, by design), so "folder absent" was the wrong check; the right check (no meta / pending / job file) passes; (b) my own guard checks had already named the chip twice, so the count of requests naming ibm_boston was 8, not 6. Both corrected; 39 of 39 pass.
5. Trivial: `sed -i` on macOS refused my edit; done in Python instead.
6. Carried-over limit, not new: the simulator cannot do kerneled readout or fade during a WAIT, so the dry run substitutes synthetic I/Q and an injected fade.

## What each run is, in plain words
START: **OFF** (nothing put in), **MID** = both-and-neither (one `sx`), **ON** (`x`). LOOK: one reading of the qubit, raw I/Q kept every time. WAIT: a pause.
**Waits (from the stone table):** short **105 us** (the wave wheel minus the particle wheel, 365 - 260), medium **260 us** (the particle wheel), long **365 us** (the wave wheel). Laid on the 16-dt grid with medium = long - short, so **short + medium = long holds exactly** for any dt (asserted in `wait_dt_counts`; checked for six different dt). At dt 4 ns the realized waits are 105.024 / 259.968 / 364.992 us. The matched twin is 105 + 260 = 365. Every shot of every circuit begins with the machine's reset (init_qubits), which is not ours and is counted in the ledger.
- **Run 1, zero earlier looks of ours (after the machine's reset), "the shot":** START, WAIT w, LOOK. 3 starts x 3 waits (105 / 260 / 365) = 9 circuits, 9 looks. Reads the message.
- **Run 2, one earlier look, "the echo":** START, LOOK, WAIT w, LOOK. 9 circuits, 18 looks. Reads the clock: the look's own mark as the gap between look 1 and look 2.
- **Run 3, two earlier looks, mirrored twins, "the witness":** START, LOOK, WAIT a, LOOK, WAIT b, LOOK; twins {105,260} (matched: a+b = 365), {105,365} (a+b = 470), {260,365} (a+b = 625, THE STONE TWIN: particle-then-wave against wave-then-particle), each in both orders. 18 circuits, 54 looks. Reads the substrate.
- 81 looks of ours, 36 circuits; the same nine qubits (three groups of three) in all three runs; **blind draw**: indices 0..N-1 by the written seed 20261002, no calibration read, no usability check. Circuit order: seeded shuffles (run 1 seed 20261021, run 2 20261022, run 3 20261023). One job per run. No calibration or test circuits (OFF and ON are the calibration and the data at once; enforced by the ledger self-check).
- **Blind submit path, exactly as the BLANK chip did:** no calibration read, no properties, no target, no faulty-qubit check. The HTTP guard allows this chip only `/configuration` and `/status` (anything else naming it is refused and logged), refuses any URL naming another chip, any other host, and any job POST without `--confirm-submit`. Tested against fakes: exactly two requests name ibm_boston per fire, configuration and status; zero properties / target / defaults requests.

## The look ledger
1. **THE MACHINE'S RESET** (init_qubits): one entry per circuit, at the start of each shot (9 / 9 / 18 per run; 4995 / 4995 / 9990 events at 555 shots). Counted by the self-check; the sampler options are pinned explicitly (init_qubits True, DD off, twirling off for gates and measure, kerneled, rep_delay 500 us, max_execution_time) and the fire refuses if any pin is not what it should be.
2. **LOOKS TAKEN BEFORE RUN 1:** one entry: no read of ibm_boston of any kind has been made by this experiment (and any account read logged before run 1 starts is added automatically from `account_reads_log.jsonl`).
3. **READS AT FIRE** (`reads_at_fire`): the account-level requests (identity, instance, backend NAMES, usage; not a read of any chip), then exactly two chip reads, each logged as a look: "the chip's size and timing tick" (static configuration) and "is it up" (the status the SDK fetches at submit). They happen at the instant of firing; a fire without `--confirm-submit` stops after the account usage read and the budget guard and does NOT touch the chip.
4. Per circuit: the count of looks and, for each look, how many looks of ours came before it, and the wait just before and just after it (requested and realized).
5. The analysis prints which looks it read, flags any it did not (dry run: 9 / 18 / 54 read, 0 unread, 0 not in the ledger).

## Size: one shot count, 555, against 34 s
`size_shots()` = the largest single shot count for which the three per-job estimates (3.0 s per job + the sequence time) sum to at most 26.4 s, so that the fire guard (1.25 x this job's estimate + the estimates of the jobs still to come) is at most 33.0 s with 34 s on the account.

| job | circuits | per-job estimate (3.0 s + sequence) | 3.0 s x circuits worst case | max_execution_time if every job bills its estimate |
|---|---|---|---|---|
| run 1 | 9 | **6.72 s** (3.0 + 3.72) | 30.7 s | 14 s (34 - 19.7 for the later jobs; binds) |
| run 2 | 9 | **6.74 s** (3.0 + 3.74) | 30.7 s | 14 s (27.3 - 12.9; binds) |
| run 3 | 18 | **12.92 s** (3.0 + 9.92) | 63.9 s | 20 s (20.5 - 0; binds) |
| **total** | 36 | **26.38 s** | | |

**Fire guard at the first fire: 1.25 x 26.38 = 32.98 s <= 34.0 s: passes with 1.02 s to spare** (shots 556 would need 33.02 s). Tested against a fake account: with 34.0 s the first fire passes, with 32.9 s it BRAKES. All three starts and all three waits are kept; no start and no wait was cut. The worst case (3.0 s per circuit) cannot be covered at any shot count (36 circuits x 3.0 s = 108 s), so the guard stays on the per-job basis, as in the original. **The cap is a cancel:** a job that hits it returns nothing (reason 1305) and the time up to the cap is presumably billed. The caps are computed live from the usage the account returns, so they move if jobs bill more or less than their estimates. dt is assumed 4 ns for the estimate; the real dt is read at fire and the estimate and guard are recomputed with it.

## THE STONE (printed last, computed last, feeds nothing else)
The prediction is the stone table (`out/stone/node_table_raw.txt`). Its sha256 (**2308807b22945e32bebddbcd343bd7bb48a55402efe96b381e6ffabcca7276cb**, verified by hashing the file) is recorded in each freeze file, re-verified at fire (a mismatch refuses) and printed by the analysis against the file on disk and each run's freeze. There is no prediction file, no miss column, no BOX ON BOX audit (nothing of ours is predicted). The section prints exactly two readings and one blank, no verdict words:
- **A. THE TWO CLOCKS, in plain words:** how long the chip's own fade lasts as read from the *gap* between look 1 and look 2 (the look's mark fading with the wait), divided by how long it lasts as read from the *levels* (what a look reads after the wait). From Run 2 (gap: shared fit of look 1 to look 2; levels: look 2) and again from Run 3's first gap (gap: shared fit of look 1 to look 2; levels: look 3, Run 3's only level fit). Each printed as a number with its bootstrap width (and the spread across the three groups of three), beside the stone's particle/wave ratio 260/365 = 52/73 = 0.712329 and beside 13/20 = 0.65, with the distance to each in units of the measured width. The ratio width comes from one joint bootstrap of both fits.
- **B. THE NODE, in plain words:** the mirrored twin made of the particle wait and the wave wait, (260 then 365) minus (365 then 260), at the third look. Three differences per start (OFF / MID / ON): the difference of the **mean** of look 3, of the **look-1-to-look-3 change**, and of the **disagreement variance** between look 1 and look 3; each with its width, beside the stone's 0 (the wheels return together), with the distance from 0 in units of the measured width. Both orders cover the same total time (625 us).
- **C. BLANK:** one row that says "left blank on purpose" and prints nothing else.
In mode run1 both A and B print CAN'T READ (reading not in this mode); in run1+2 only A's Run 2 line is read; run1+2+3 reads everything. Stated, not corrected: Run 3's level fit is on look 3, which sits after a + b of elapsed time, not one wait. Everything else is kept: the three starts, the self-effect ladder at matched time (105 + 260 = 365), THE RETURN PASS, THE REMAINDER, carry-over, the drawn-qubit rows (a dead blind-drawn qubit is a row, not a pre-check), the look ledger and the CAN'T READ rows. Dry-run example (synthetic I/Q, code path only) is in `data/dryrun_logs/an_run1+2+3.log`.

## Exact command sequence (never run by the builder)
`PY=~/bones-forge/venv_quantum/bin/python`, `cd /Users/heuremen/bones-forge/parallax/out/qubit_stone_run`. **Freeze only when the code is final: any edit to `common.py`, `live.py`, `run{N}.py` or `analyze.py` after a freeze makes that run unscorable.** `parse_payload.py`, `recover.py`, `freeze.py` are outside the hash. Wayfinder reviews before the first fire.
```
$PY freeze.py --run 1     # no account contact: hashes code, ledger, seeds, waits, shots and the stone table sha256 (verified from the file)
$PY run1.py --fire --chip ibm_boston --box stone --confirm-submit     # refuses unless the freeze matches, the table hash holds, the account has 32.98 s
$PY freeze.py --run 2
$PY run2.py --fire --chip ibm_boston --box stone --confirm-submit     # refused until run 1 has landed
$PY freeze.py --run 3
$PY run3.py --fire --chip ibm_boston --box stone --confirm-submit     # refused until run 2 has landed
$PY analyze.py run1+2+3                                               # data/fire is the default; ends with THE STONE
# optional after each landing: $PY analyze.py run1 ;  $PY analyze.py run1+2
# if a result was lost: $PY recover.py --run N  (re-reads by the saved job id) ;  $PY recover.py --reparse --run N  (from the saved raw payload; no network)
```
Dry-run any step first: `$PY runN.py --dry-run` (synthetic, no account), `$PY runN.py --list-circuits`, `$PY runN.py --print-estimate`; `--data-dir data/dryrun` for analysing synthetic data. (Option, your call: freezing runs 2 and 3 before the first fire locks the analysis code before any data exists; cost: any fix after run 1 breaks all later freezes.) Without `--confirm-submit` a fire stops after the account usage read and the budget guard.

## Every ruler this shot carries that did not come from the stone
1. **The rest between shots** (rep_delay 500 us: the chip's own pause between one shot and the next; carry-over between shots is read, never corrected).
2. **The shot count** (555 per circuit: from the 34 s, not from the stone), and with it the width of every number.
3. **The frozen analysis** (the projection from the OFF centre to the ON centre, the median pooling over qubits, bootstrap of 200 over shots with its seed, the fading-time search edges 1 to 100000 us, the minimum of 30 shots, the three-cornered-hat solve, the shared-fit forms, the 16-dt grid that turns 105 / 260 / 365 into 105.024 / 259.968 / 364.992 us).
4. **The machine's reset** (init_qubits at the start of every shot: the maker's own look, not ours, whether it reads the bit cannot be confirmed from code; plus the pinned sampler options).
5. **The maker's unseen calibration** (whatever the chip's own calibration was when it ran decides its fade, readout and gate quality; we never read it, so we cannot name that ruler, only carry it).
6. **Blind-drawn bits** (which nine qubits: seed 20261002, drawn from 0..N-1 with no usability check; a dead one is a row).
Also carried, not from the stone: the circuit-order seeds (20261021 / 22 / 23), the sample of three starts (OFF / MID / ON) and the three-look design itself, the readout (kerneled I/Q) and its per-job frame (kernel drift between jobs is stamped, not corrected), the assumed dt and readout time in the estimate, the time between runs (measured from the jobs' own stamps, not removed), and the 34 s account that fixed the shot count.

## Still untested until real hardware
The same list as the three-chip build: the real server's answer to a job with three mid-circuit measurements on the same qubits in kerneled mode (and whether a rejected job is billed); the shape of the returned payload (saved raw first, repairable with `--reparse`); shot order; whether the pinned options are honoured server-side; the blind submit path against the real SDK and server (private SDK attributes, tested only against fakes; if the SDK names the chip in any other request the guard refuses and the fire fails loudly before submit); whether the usage answer supplies `usage_remaining_seconds` and whether billing is per job (3.0 s) or per circuit (3.0 s x circuits would end the account inside run 1); the chip's static configuration (dt, native gates) unknown until read at fire; kernel drift between jobs; the real fade and every real number.

## Tests (code path only, all synthetic / fake)
- Dry runs: `runN.py --dry-run` for N = 1, 2, 3 (555 shots, exit 0 each) into `data/dryrun/ibm_boston/` (each round-trips its synthetic I/Q through a RuntimeEncoder payload and the parser); `analyze.py run1`, `run1+2`, `run1+2+3 --data-dir data/dryrun`: exit 0 each, THE STONE section printed last in each. Logs: `data/dryrun_logs/` (`dry_run*.log`, `an_*.log`).
- `tests/test_stone.py` (scratch copy under /tmp, fake service, local HTTP stub): **39 checks, 39 PASS, 0 FAIL.** Covers: waits and exact closure for six dt; every other chip refused; written seeds; the shot count and guard (passes at 34 s, BRAKES at 32.9 s); table hash verified and a modified table REFUSED at freeze; freeze content and no-overwrite; run 2 refused before run 1 with zero requests; an edit to `analyze.py` after the freeze refuses the fire; no chip contact without `--confirm-submit`; three fake fires in order on the blind path with the caps printed; exactly two chip reads per fire in the ledger and zero properties / target / defaults requests.

## Files
`out/qubit_stone_run/`: `common.py`, `live.py`, `run1.py`, `run2.py`, `run3.py`, `freeze.py`, `recover.py`, `parse_payload.py` (outside the freeze), `analyze.py`, `tests/test_stone.py`, `data/dryrun/ibm_boston/` (synthetic), `data/dryrun_logs/`.
