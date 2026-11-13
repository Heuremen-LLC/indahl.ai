# QUBIT THREE RUNS -- BUILD REPORT v2 (amended), 2026-10-01 night
Spec (the only design): `QUBIT_THREE_RUNS_APPROVED_20261001.md`, including "AMENDMENTS APPROVED BY WAYFINDER, 2026-10-01 night". Code: `out/qubit_three_runs/`. The v1 files are kept as `*_v1` (`common_v1.py`, `run1_v1.py` ... `analyze_v1.py`, `predictions_template_v1.json`, `data_v1/`, and the old report `QUBIT_THREE_RUNS_BUILD_20261001_v1.md`).
Nothing was submitted to hardware. `--fire` was never called. **The IBM account was not contacted at all in this pass** (no usage read, no backend query): every number below comes from the saved FakeKingston snapshot (calibration stamp 2026-04-15) and files already on disk. `--live-readonly` was removed from the code and the old `live_probe.py` was renamed `live_probe_v1_NOT_RUN_THIS_PASS.py`.

## READ THIS FIRST
**THE DRY RUN PROVES THE CODE PATH ONLY, NOT THE PHYSICS.** The local simulator has no raw I/Q, so every I/Q number in a dry run is SYNTHETIC (fabricated from simulated 0/1 outcomes, plus an injected fade of tau = 300 us over each wait and an injected 5 % per-earlier-look kill so the self-effect equation has something to find). Every dry-run results file and every report header says so. Nothing in `data/dryrun_*` says anything about the chip.
The last account state anyone read (v1 report) was 0 seconds left until 2026-10-22; it was NOT re-read this pass. Any `--fire` also refuses on its own budget guard.

## Where it broke first
In the order found:
1. **Simulator, run 1 dry run (same break as v1, reproduced):** `meas_type="kerneled"` (raw I/Q) on the local simulator raises `UFuncTypeError: ufunc 'multiply' did not contain a loop with signature matching types (complex128, <U5)`. Substitution, declared in every `run*_meta.json` under `simulator_breaks`: same circuits, bitstring measurement, each 0/1 placed in a synthetic Gaussian cloud around a fabricated per-qubit centre.
2. `rep_delay` is accepted and ignored locally (UserWarning). Rep-rate effects exist only on hardware.
3. The local noise model has no fading during a WAIT (Aer puts relaxation on gates, not on `delay`): ON start after a 1000 us wait still reads 0.95 mean bit locally (maker T1 alone would give about 0.03). The fit cannot be tested on simulated physics; the dry run injects a labelled synthetic fade instead.
4. **Design collision found while amending: the smaller variant had 2 groups of three. THREE BOXES need three groups.** Both variants now keep 3 groups (9 qubits). Qubits run in parallel, so this costs no QPU seconds; "never cut a three to a two" holds for starts, waits, groups.
5. **Design collision: run 1 no longer has a look without a wait** (it is START, WAIT, LOOK). The old "look 1 is the same reading in all three runs" drift is therefore not literal any more. Run 1's first look now sits after the shortest wait (19.968 us realized); runs 2 and 3's first look has no wait. The drift table says so and does not correct it.
6. **Design collision, the important one, found in the first combined dry output: F(2) is not a one-wait reading.** Run 3's third look sits after wait a THEN wait b, so it carries the fading over a; F(0) and F(1) carry one wait only. The second effect F(2) - F(1) therefore includes the fading over the earlier wait. The equation is computed exactly as written in the spec; beside every pooled row the same number is printed split by the earlier wait a, and the n = 2 clock is fitted against TOTAL elapsed time a + b (identical for both orders of a mirrored twin, which is what the twins buy). Flagged for Wayfinder in "Choices to confirm".
7. The FakeKingston snapshot has qubit 96 at readout error 0.49 (v1 finding); pooling across qubits stays the MEDIAN. Memory: no break at 9 qubits (cap 2048 MB, 1 thread, single process).

## What each run is, in plain words
START: **OFF** (nothing put in), **MID** = both-and-neither (one half-turn gate), **ON** (fully put in). LOOK: one reading of the qubit, raw I/Q kept every time (never cut to 0/1). WAIT: a pause. Waits: short 20 us, medium 100 us, long 1000 us (laid down as whole multiples of 16 clock ticks; realized 19.968 / 99.968 / 1000.000 us on the snapshot).
- **Run 1, ZERO earlier looks:** START, WAIT, LOOK once. 3 starts x 3 waits = **9 circuits**, 9 looks.
- **Run 2, ONE earlier look:** START, LOOK, WAIT, LOOK. 3 x 3 = **9 circuits**, 18 looks.
- **Run 3, TWO earlier looks, MIRRORED TWINS:** START, LOOK, WAIT a, LOOK, WAIT b, LOOK. For each pair of different waits both orders: twin {20,100} = (20,100) and (100,20); twin {20,1000} = (20,1000) and (1000,20); twin {100,1000} = (100,1000) and (1000,100). 3 pairs x 2 orders = 6 layouts, x 3 starts = **18 circuits**, 54 looks. The layout is written in `run3.py` and in the ledger.
- Same qubits in all three runs: random groups of three, seed 20261001: group 0 = [82,139,154], group 1 = [38,92,96], group 2 = [25,109,135] on the snapshot (**the live draw at fire time can differ; see risk 11**). Circuit order is a seeded shuffle (run 1 seed 20261011, run 2 20261012, run 3 20261013). One job per run, every circuit a pub of one sampler call. rep_delay 500 us fixed. Synthetic-I/Q seed 20261021, analysis seed 20261031.
- Recorded with each run: start and end time, calibration timestamp, the maker's published T1/T2/readout error per qubit (the OUTSIDE reading), code hash, look ledger.

## Every circuit in each run (START, WAIT, LOOK) -- no other circuit exists
There are **no separate calibration or test circuits**: OFF and ON are the calibration and the data at once. This is enforced three ways: (a) `build_ledger` lists every circuit and `ledger_self_check` refuses any start outside OFF/MID/ON; (b) `check_ledger_vs_circuits` counts the transpiled circuits: exactly n_looks x 9 measurements, one classical register per look, one delay per qubit per wait, no extra circuit; (c) `verify_arrays` and `analyze.load` refuse a results file whose arrays differ from the ledger by even one look. The lists below are generated from the ledgers (`data/dryrun_full/run*_look_ledger.json`).

**Run 1: 9 circuits, 9 looks in all, calibration or test circuits: 0.**

- `OFF|w20`: START OFF; WAIT 20 us; LOOK 1  (1 look: L1=0 before, after a 20 us wait)
- `OFF|w100`: START OFF; WAIT 100 us; LOOK 1  (1 look: L1=0 before, after a 100 us wait)
- `OFF|w1000`: START OFF; WAIT 1000 us; LOOK 1  (1 look: L1=0 before, after a 1000 us wait)
- `MID|w20`: START MID; WAIT 20 us; LOOK 1  (1 look: L1=0 before, after a 20 us wait)
- `MID|w100`: START MID; WAIT 100 us; LOOK 1  (1 look: L1=0 before, after a 100 us wait)
- `MID|w1000`: START MID; WAIT 1000 us; LOOK 1  (1 look: L1=0 before, after a 1000 us wait)
- `ON|w20`: START ON; WAIT 20 us; LOOK 1  (1 look: L1=0 before, after a 20 us wait)
- `ON|w100`: START ON; WAIT 100 us; LOOK 1  (1 look: L1=0 before, after a 100 us wait)
- `ON|w1000`: START ON; WAIT 1000 us; LOOK 1  (1 look: L1=0 before, after a 1000 us wait)

**Run 2: 9 circuits, 18 looks in all, calibration or test circuits: 0.**

- `OFF|w20`: START OFF; LOOK 1; WAIT 20 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait)
- `OFF|w100`: START OFF; LOOK 1; WAIT 100 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait)
- `OFF|w1000`: START OFF; LOOK 1; WAIT 1000 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait)
- `MID|w20`: START MID; LOOK 1; WAIT 20 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait)
- `MID|w100`: START MID; LOOK 1; WAIT 100 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait)
- `MID|w1000`: START MID; LOOK 1; WAIT 1000 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait)
- `ON|w20`: START ON; LOOK 1; WAIT 20 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait)
- `ON|w100`: START ON; LOOK 1; WAIT 100 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait)
- `ON|w1000`: START ON; LOOK 1; WAIT 1000 us; LOOK 2  (2 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait)

**Run 3: 18 circuits, 54 looks in all, calibration or test circuits: 0.**

- `OFF|w20-100`: START OFF; LOOK 1; WAIT 20 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)
- `OFF|w20-1000`: START OFF; LOOK 1; WAIT 20 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `OFF|w100-1000`: START OFF; LOOK 1; WAIT 100 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `OFF|w100-20`: START OFF; LOOK 1; WAIT 100 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `OFF|w1000-20`: START OFF; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `OFF|w1000-100`: START OFF; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)
- `MID|w20-100`: START MID; LOOK 1; WAIT 20 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)
- `MID|w20-1000`: START MID; LOOK 1; WAIT 20 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `MID|w100-1000`: START MID; LOOK 1; WAIT 100 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `MID|w100-20`: START MID; LOOK 1; WAIT 100 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `MID|w1000-20`: START MID; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `MID|w1000-100`: START MID; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)
- `ON|w20-100`: START ON; LOOK 1; WAIT 20 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)
- `ON|w20-1000`: START ON; LOOK 1; WAIT 20 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 20 us wait | L2=1 before, after a 20 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `ON|w100-1000`: START ON; LOOK 1; WAIT 100 us; LOOK 2; WAIT 1000 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 1000 us wait | L3=2 before, after a 1000 us wait)
- `ON|w100-20`: START ON; LOOK 1; WAIT 100 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 100 us wait | L2=1 before, after a 100 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `ON|w1000-20`: START ON; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 20 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 20 us wait | L3=2 before, after a 20 us wait)
- `ON|w1000-100`: START ON; LOOK 1; WAIT 1000 us; LOOK 2; WAIT 100 us; LOOK 3  (3 looks: L1=0 before, no wait before, before a 1000 us wait | L2=1 before, after a 1000 us wait, before a 100 us wait | L3=2 before, after a 100 us wait)

## The look ledger
Every circuit's results carry: the count of looks in it and, for each look, how many looks came before it, the wait just before it and the wait just after it (requested and realized). Saved as `run{N}_look_ledger.json` beside the results and embedded in `run{N}_meta.json` (`ledger`, `circuits`). Totals: run 1 = 9 looks, run 2 = 18, run 3 = 54, **81 looks in all**. No look exists that is not in the ledger and in the analysis: `analyze.py` tracks every look it reads (every projected look is wrapped so each access is recorded) and prints, per run, "looks read / in the analysis but not in the ledger / in the ledger but never read". Dry-run result, all three runs: every ledger look is read, none outside the ledger, none unread.

## The three boxes and their rotation
One box per group of three qubits: **OURS** (our sealed number), **MAKER** (the maker's published T1 of that group's qubits = its prediction, with the group's sd as width; exists only for the fading-time quantities MID, ON and shared, none for OFF and none for any other quantity), **BLANK** (no prediction; the group's results print with no miss column). Drawn by the written seed **BOX_SEED = 20261041** (a permutation of the three groups), then rotated by one box per run so every group sits in every box once:

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| group 0 [82,139,154] | OURS | MAKER | BLANK |
| group 1 [38,92,96] | MAKER | BLANK | OURS |
| group 2 [25,109,135] | BLANK | OURS | MAKER |

The box assignment is saved in each run's meta (`box_assignment`, `box_seed`). The assignment used to score a prediction file is the one of the run the file is sealed for. (`common.box_assignment`.)

## The prediction ledger and the guards
- **The prediction is a look.** Each entry in a prediction file records `written_at`, `data_seen` (none / maker / run1 / runs1+2), `predicted`, `width`; the file records `_run` and `_written_at`. Template: `predictions_template.json`, 228 quantities, regenerated by `analyze.py --make-template`.
- **`freeze.py --run N`** writes `freeze_run{N}.json` BEFORE any prediction: sha256 of `common.py` + `run{N}.py` (the circuit-building code), `analyze.py`, and the look ledger (requested form), plus `frozen_at`. `analyze.py` refuses to score a run's predictions if (a) the hash on file, the `code_hash` stored in the results meta, and the hash of the code on disk now do not all match; (b) the prediction's `_written_at` is earlier than `frozen_at`, or later than the start of the run; (c) an entry's `written_at` is earlier than the freeze, or its `data_seen` is not one the run could have had. The fire path runs the same freeze/prediction check (plus: file must be for this run) before it touches the account. Because `analyze.py` is in every freeze, **any edit to `analyze.py`, `common.py` or the run file after a freeze invalidates that run's predictions**: freeze only when the code is final.
- **Tested refusals** (in a throwaway copy `/tmp/qtr_test`, so no test freeze file sits in the build folder): prediction earlier than the freeze -> REFUSED; prediction later than run start -> REFUSED; analyze.py edited after the freeze -> REFUSED with the three hashes shown; results meta not complete -> REFUSED (nothing read); meta missing -> REFUSED; npz tampered -> REFUSED.
- **The miss column is computed last and feeds nothing.** Code inspection of `analyze.py`: `main()` runs (1) `load()` of every run (refuses incomplete), (2) `print_audit(hdr)` where `hdr` comes from `common.load_prediction_header`, which returns only `written_at`, `data_seen` and a boolean "is a number filled in" (never a number), (3) the measured quantities and reports, (4) the save of `analysis_*.json`, and only then (5) `score_predictions()`. `_load_prediction_numbers` is called exactly once, inside `score_predictions`; `_miss` is called only inside it (grep verified: the only call sites are lines inside `score_predictions`). No measured-quantity function (`q_run1/2/3`, `q_comb`, `quantify`, the reports) takes a prediction as an argument. Confirmed by experiment: `analysis_run1_2.json` is **byte-identical** with and without a prediction file. Scores are written to a separate `scores_run{N}_*.json`.
- **DON'T COUNT UNTIL IT LANDS.** (a) `save_results` writes the npz, the ledger, the maker clock, and only then the meta with `complete: true` and the npz hash, atomically; a stale meta is deleted first. (b) `analyze.load` refuses a run that is not marked complete, whose npz hash differs, or whose arrays differ from the ledger, and it does this for every run in the mode before any output. (c) The fire path submits one job, then calls `job.result()` once (which blocks until the job is final); it reads, prints and polls no outcome data, there is no progress tally, and `collect_results` refuses anything partial or odd (None, wrong pub count, BitArray, real-valued, wrong shape). If the job fails or times out nothing is saved. (d) A run fires once: if `data/fire_<variant>/run{N}_meta.json` exists the fire path refuses.

## THE CIRCULARITY AUDIT (printed at the top of every report)
Rule: a prediction is scored only if none of the data it was written from sits inside the measured quantity; if they overlap the row is **BOX ON BOX** and is not scored. "Data inside" a quantity = the runs whose raw looks enter it. Own-run quantities (`r1.*`, `r2.*`, `r3.*`) use their own frame, so they contain only their run. Combined quantities (`c.*`) use ONE frame from look 1 (no wait, no earlier look) of runs 2 and 3, so every `c.*` quantity contains runs 2 and 3, plus run 1 when a run-1 reading is in it (F(0), first effect, hunter's number, clocks involving n = 0). Drift rows contain all three. All 228 template quantities, scoreable by the stage at which the prediction is sealed (seen = what it was written from):

| sealed before | seen | r1 (41) | r2 (27) | r3 (55) | c combined (78) | drift (27) | **TOTAL (228)** | own-run quantities |
|---|---|---|---|---|---|---|---|---|
| run 1 | none | 41 | 27 | 55 | 78 | 27 | **228** | 41 of 41 |
| run 2 | run 1 | 0 | 27 | 55 | 39 | 0 | **121** | 27 of 27 |
| run 3 | runs 1+2 | 0 | 0 | 55 | 0 | 0 | **55** | 55 of 55 |

(The "BOX ON BOX" counts are 0, 107 and 173 respectively. Stage 2: all r1 and drift rows plus the 39 combined rows that contain run 1 -- F(0), first effect, hunter, clocks with n = 0 -- are boxed. Stage 3: every combined and drift row contains run 2, and the r1 and r2 rows are already-measured.) Also printed, per filled entry of a given file: `written_at | written from | data inside | scoreable or BOX ON BOX`. Run-by-run own-quantity count: **41 / 27 / 55 scoreable**. Combined rows scoreable only from a prediction written before run 1 (all 78) or before run 2 (39 of 78); none from a prediction written after runs 1+2.

## The self-effect equation, the three clocks, turning back time (analyze.py, combined mode)
- `F(n, wait, start)`, raw I/Q projected onto the per-qubit OFF-to-ON line of one common frame, median across qubits: n = 0 from run 1, n = 1 from run 2 (look 2), n = 2 from run 3 (look 3, pooled over the two twin orders whose last wait is that wait). **First effect = F(1) - F(0). Second effect = F(2) - F(1). The hunter's number = second / first**, per wait and per start, each with its bootstrap width (and the 16-84 % half-range, because a ratio's sd can be dragged by a near-zero denominator). No threshold, no verdict word. The split-by-earlier-wait rows and the F(2)-against-total-elapsed rows follow (see "Where it broke", item 6).
- **Three clocks:** fading time with 0, 1, 2 earlier looks (level fit G exp(-w/tau), per start and shared); log10 of each ratio (n=1/n=0, n=2/n=1, n=2/n=0), each with the third clock beside it. The maker T1 median is printed for scale only.
- **Turning back time:** for each twin, (a then b) minus (b then a), per start, for look 2 mean, look 3 mean, look1-to-look3 change, and look1-vs-look3 disagreement variance, all three twins side by side with widths. (Look 2 sits after a different wait in each order, so its difference is large by construction; look 3 and the total change are like for like. Stated in the output.)
- Per-run modes keep the three-cornered-hat solve, the remainder, and the inside / outside / maker clock comparison from v1. Run 1 now reads per wait: mean, variance, skew per start, the OFF+ON 50/50 pool at the same wait, MID minus pool.

## QPU-second estimates (same method as v1; computed by `estimate()` on the snapshot, no account)
3.0 s per job (measured from the real echo run) + shots x (rep_delay 500 us + looks x 1.6 us + waits). One job per run. Worst case charges 3.0 s per circuit.

| | shots/circuit | qubits | Run 1 (9 circ.) | Run 2 (9 circ.) | Run 3 (18 circ.) | **All three, per-job basis** | Worst case (3.0 s per circuit) |
|---|---|---|---|---|---|---|---|
| **FULL** | 1500 | 9 | 14.8 s | 14.8 s | 36.8 s | **66.4 s** | 165.4 s |
| **SMALLER** | 500 | 9 | 6.9 s | 6.9 s | 14.3 s | **28.1 s** | 127.1 s |

Fire guard (account must hold 1.25 x the worst case for that run): FULL 49 / 49 / 110 s = 208 s; SMALLER 39 / 39 / 82 s = 160 s. (v1 for comparison: full 40.0 s, smaller 19.3 s; the amendments add run 1's waits, 9 more circuits in run 3, and the smaller variant now uses 9 qubits, which costs nothing.) Sensitivity, not in the numbers above: rep_delay 1000 us instead of 500 us would give full 21.6 / 21.6 / 50.3 = 93.5 s and smaller 9.2 / 9.2 / 18.8 = 37.2 s (see risk 5).

## Commands (never run by the builder)
Order for each run N: freeze, then write the prediction, then (optionally) dry-run, then fire. `PY=~/bones-forge/venv_quantum/bin/python`, `cd /Users/heuremen/bones-forge/parallax/out/qubit_three_runs`.
```
$PY analyze.py --make-template my_pred_N.json         # fill _run, _written_at, and per entry written_at, data_seen, predicted, width
$PY freeze.py --run N                                  # BEFORE the prediction is written; --refreeze invalidates older predictions
$PY runN.py --list-circuits --variant full             # every circuit in plain words (no account)
$PY runN.py --dry-run --variant full                   # code path only, synthetic I/Q
$PY runN.py --fire --variant full --prediction-file my_pred_N.json --confirm-submit    # REAL HARDWARE. Not run by the builder.
$PY analyze.py run1     --data-dir data/fire_full --predictions my_pred_1.json
$PY analyze.py run1+2   --data-dir data/fire_full --predictions my_pred_2.json
$PY analyze.py run1+2+3 --data-dir data/fire_full --predictions my_pred_3.json
```
(`--variant min` for the smaller purchase.) The three real runs land in one folder, `data/fire_<variant>/`, so the combined modes can read them together. Without `--confirm-submit` a fire call still builds, checks the freeze and prediction, reads the account and backend and budget-checks, then stops: that is the first contact with the account and it is read-only; the dry runs make none.

## FIRE-PATH RISKS (read line by line against qiskit-ibm-runtime 0.49.0 and qiskit 2.5.2; NOT tested on hardware)
What the line-by-line read confirmed against the installed source: `QiskitRuntimeService(channel='ibm_quantum_platform', token=...)` is a valid channel in 0.49; `sm.options.execution.meas_type = 'kerneled'` and `.rep_delay` and `sm.options.max_execution_time` all exist and set (tested offline); `SamplerV2(mode=backend)` is job mode; `run(pubs, shots=)` coerces circuits to pubs; the client-side ISA check passes for all 18 run-3 circuits against the snapshot target; the DD-with-dynamic-circuits check does not fire (DD is off and there is no control flow or condition); a result arrives as a `PrimitiveResult` whose `DataBin` has one complex ndarray of shape `(shots, creg_size)` per classical register, named like the register (the executor-based decoder strips an `_iq` suffix; `collect_results` accepts both and was tested against a mock result, and refuses BitArray, real-valued, wrong-shape, None and wrong-pub-count results). What could still fail on real hardware:
1. **Mid-circuit measurement together with `meas_type="kerneled"` (and several measurements of the same qubit, one register per look) has never been run by anyone.** The client raises no objection; the server may. Unknown whether a rejected job is billed.
2. **The real shape and bit order of the returned arrays is assumed**: column j of register Lk = virtual qubit j = physical `all_q[j]` through `initial_layout`. `collect_results` checks shape and dtype but cannot check the column order.
3. **Timing alignment.** Circuits are transpiled at level 0 with no scheduling pass. Waits are whole multiples of 16 dt, but the start of each measurement after a gate is not aligned by any pass. The snapshot says alignment 1 (so it cannot show a problem); the live backend may say 16. Offline, `scheduling_method='alap'` transpiles fine on the snapshot (31694 dt for one run-3 circuit), but it was not adopted because it changes the circuits and cannot be validated without the live target.
4. **Kernel and frame drift between the three jobs.** Raw I/Q units are arbitrary and belong to a job's calibration. Run 1 is read in a frame built from runs 2 and 3, so a recalibration between jobs would put an offset or a scale change straight into F(1) - F(0). Calibration stamps are recorded per run and printed; nothing corrects for them (time between runs is measured, not removed).
5. **rep_delay 500 us is only about 1.7 x the maker T1 median (292 us).** `init_qubits` is a passive reset by waiting, so up to about 18 % of an excited population can carry into the next shot's start (ON and MID). A data-quality risk, not a code failure: the starts are "ON with some memory". Doubling it costs +27 s (full) / +9 s (smaller) for all three.
6. `rep_delay` needs `backend.dynamic_reprate_enabled`; the fire path refuses if the backend does not report it (read through the configuration fallback in `IBMBackend.__getattr__`), and refuses a rep_delay outside `rep_delay_range`.
7. `service.usage()` only contains `usage_remaining_seconds` when the account response has a limit or allocation field; otherwise `.get(..., 0)` yields 0 and the budget guard brakes. Fails safe, but could brake wrongly.
8. No `instance` is passed: with several instances on the key the service picks its default, which may not be the funded one.
9. `max_execution_time = ceil(3 x sequence + 20)` seconds (about 121 s for run 3 full). If hit, `result()` raises `RuntimeJobMaxTimeoutError`; nothing is saved, and the time is presumably still billed. Also if the process dies after submit there is no saved result and no recovery script: the printed job id is the only handle (`service.job(id)`; not written).
10. `IBMBackend.check_faulty(circuit)` raises if a chosen qubit is listed faulty on the day, and the live backend's `max_shots` limit was not read this pass (1500 shots per pub is assumed to be allowed).
11. **Qubit groups.** The groups printed here are drawn from the 2026-04 snapshot (which includes a qubit at 0.49 readout error). The live candidate list will differ, so the live groups will too. The first fire writes `qubit_groups_locked.json`; later fires refuse if the live draw differs from the locked groups. Consequence: if a qubit goes bad between runs, run 2 or 3 stops and a decision is needed. Dry runs cannot show the live groups.
12. The estimate assumes 1.6 us per look; the snapshot's measure instruction is 570 dt (about 2.3 us). Effect on the totals is under 0.2 % because rep_delay dominates.

## Choices to confirm with Wayfinder (things the spec did not decide)
1. F(2) pooled by last wait carries the earlier wait too (item 6 above). Built as written plus the split rows and a total-elapsed clock. Say if the hunter's number should use something else.
2. The "ONE frame" for the combined equations is look 1 of runs 2 and 3; run 1 has no wait-free look. Consequence in the circularity audit: every combined row contains runs 2 and 3.
3. The MAKER box exists only for the fading-time quantities (published T1 of the group's three qubits, sd as width); every other quantity has no maker number, so that group prints with no miss.
4. Drift = look 1 across runs, with run 1's look after the shortest wait; shown, not corrected.
5. Scoring uses the box assignment of the run the prediction file is sealed for, including combined quantities.
6. "Which runs see it" is still not decided by the code: it prints each run's own remainder with width in widths and no verdict.

## Dry runs and analysis passes (all synthetic, code path only)
`data/dryrun_full/` and `data/dryrun_min/`: `run{1,2,3}_results.npz`, `_meta.json` (complete, hashed), `_look_ledger.json`, `_maker_clock.json`, `analysis_run1.json`, `analysis_run1_2.json`, `analysis_run1_2_3.json`, `report_*.txt`. All three runs dry-ran on both variants, and `analyze.py run1`, `run1+2`, `run1+2+3` exit 0 on both (200 bootstrap draws for full, 100 for min), each with its own look-ledger check and circularity audit. Three simulator breaks per run (items 1-3 in "Where it broke"). Scoring, boxes, freeze and every refusal were exercised end to end in `/tmp/qtr_test` with synthetic predictions; those test freeze and prediction files are not in the build folder (no freeze exists yet: the real freeze belongs before the real predictions).

## Files
`out/qubit_three_runs/`: `common.py`, `run1.py`, `run2.py`, `run3.py`, `analyze.py`, `freeze.py`, `predictions_template.json` (228 quantities), `data/dryrun_full/`, `data/dryrun_min/`; v1 copies `*_v1.*`, `data_v1/`, `live_probe_v1_NOT_RUN_THIS_PASS.py`.
