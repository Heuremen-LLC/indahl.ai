# What a measurement costs: reproducing the numbers

    python3 verify_cost.py

Standard library only, no account, no network, about 15 seconds. It reads the two files in `data/`
(228 KB together), recomputes each figure the site gives for this topic, and prints it beside the
site's value with OK or DIFFERS. This folder is a staging copy; nothing under `heuremen.org/` was
changed.

The claims come from `findings.html` (section "A measurement costs what it takes", and the paragraphs
after "Coherence falls as measurements pile up"), `what-we-measured.html` and `index.html`.

## What was measured, on which chip, when

Every number is a fraction of the coherence a qubit started with. 1 means all of it is left, 0 means
none. Untouched qubits ("spectators") sit next to qubits that are being measured over and over.

| Data file | Chip | Date | IBM job IDs |
|---|---|---|---|
| `kingston_spectators_20261004_06.json` | ibm_kingston | 4 Oct 2026, 10:55-11:04 EDT | db16hravog1s73fhnml0, db16iaavog1s73fhnn9g, db16llbid5ic73eqnp8g (lab run numbers 341, 342, 343) |
| | | 6 Oct 2026, 23:18-23:41 EDT | db2rk4u8v0ts73c3dbcg, db2rp87r11fs7397b73g, db2rug68v0ts73c3dt50 (runs 761, 762, 763) |
| `fez_count_20261011.json` | ibm_fez | 11 Oct 2026, 15:58 and 17:00-17:09 EDT | db5ukk4lf4us73c4j3gg, db5vhnamb58s738b2n50, db5vk14vf2bc73d0fs80 (runs 901, 902, 903) |

Each Kingston job: 300 shots per circuit, a ladder of 1, 2, 3, 4, 6, 8, 12, 16, 24, 32 measurements
in a row, plus idle waits of 10, 20, 30, 60, 120 microseconds. About 120 untouched qubits are kept
per job, sorted by how many wires lie between them and the nearest measured qubit (1, 2, 3 or more).
Each Fez job: 400 shots per circuit, a ladder of 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128
measurements, 30 measured qubits, 79 / 83 / 83 untouched qubits kept (jobs 1 / 2 / 3).

The Kingston table is the source for the first claim ("0.99-1.03 up to 9, 1.16-1.18 at 27"). The
site does not name a chip for that table; the lab ledger line it matches
(`THIRD_RUNG_20260928.md`, entries 338, 344, 346, 347) is Kingston, two days. The Fez jobs are the
source for the second claim (shape exponents, the 0.965 / 0.067 / 0.661 numbers).

## How each quantity is computed

* **Level of a qubit.** Each readout gives a point in a plane. Circuits that prepare all qubits in
  0 and all in 1 give the two ends of a ruler; the level is where a qubit's mean point falls on that
  ruler (0 = ground state, 1 = excited). A qubit is kept only if the two ends are more than 3 widths
  apart.
* **Coherence of an untouched qubit.** Prepared half-way between 0 and 1 and read on two axes a
  quarter-turn apart; the "hand" is the length of the resulting arrow, and "kept" is that length
  after the wait or the measurements divided by its length with no wait. Only qubits that start with
  an arrow longer than 0.15 are used. Per distance group the median over qubits is taken.
* **Measured qubit** (Fez). Starts in 1, is measured k times in a row; the level is the fraction still
  in 1. Reported on the 0-to-1 axis, as the site does ("F0-F1 axis").
* **Stretched exponential.** `A * exp(-(k/k0)^b)`; b = 1 is a plain exponential. Fitted by least
  squares weighted by the point widths; the first point (used to normalise) is left out. The width of
  each point is the spread over 40 resamplings of the shots (read from the file, because the shots
  themselves are not in this package).
* **Cost against idle (Kingston).** `kept after k measurements / kept after idling for k times the
  length of one measurement`, averaged over the three distance groups, then over jobs. Length of one
  measurement: manufacturer's stated 2.18 us, or the lab ledger's "measured" 2.323 us (4 Oct) and
  2.402 us (6 Oct) (these two are copied from the ledger, not recomputed here). The idle curve is
  either fitted (stretched exponential through the 10/20/30 us waits, or through all waits) or read
  straight off the measured waits with no fit.

## Result: claim by claim

### 1. "0.99-1.03 for k up to 9 (six reads, two days); 1.16-1.18 at k = 27"

| | site | recomputed | verdict |
|---|---|---|---|
| k = 3 and 9, kept / kept, six jobs | 0.99-1.03 | 0.977-1.026 (fitted idle curve, ledger look length) | OK within 0.02 |
| k = 27, kept / kept | not a ratio the page words this way | 0.68-0.97 per job; day means 0.860 and 0.815 | |
| k = 27, "coherence lost / coherence lost" (the page's wording) | 1.16-1.18 | 1.02-1.17 per job; day means 1.07 and 1.10 | DIFFERS |
| k = 27, idle read off the measured waits, no fit | 1.16-1.18 | kept/kept 1.01-1.10; lost/lost 0.97-1.00 | DIFFERS |

What the numbers say:

* The page words the ratio as lost over lost. The lab ledger's score is kept over kept (entries 338-347:
  27 measurements "keep 0.836 / 0.839 of what the same laid time keeps", "16-20 % beyond"). These are
  different quantities. At k = 3 the lost / lost ratio runs 0.95-1.30 because the loss is only a few
  percent, so "0.99-1.03" does not hold for lost / lost at k = 3; it holds for kept / kept.
* The ledger's 27-measurement scorer is not on disk (the file `three_looks_minus_time_20261004.txt`
  header says its reader was "recovered from this session's transcript"). My reconstruction gives
  0.860 (day 1) and 0.815 (day 2) where the ledger gives 0.836 and 0.839.
* The "1.16-1.18" cannot be reproduced under any definition tried. 1 / (kept ratio) gives 1.17 (day 1)
  but 1.23-1.25 (day 2). The nearest single number is one job (run 761) with lost / lost 1.169.
* The 27-measurement excess depends on how the idle curve is built. The jobs have no 27-measurement
  point (ladder runs 24 then 32), and 27 x 2.3 us = 62 us sits at the end of the idle waits that fit
  the curve. Fitted through 10/20/30 us only, 27 measurements keep 0.68-0.97 of the idle value. Fitted
  through all waits up to 120 us, 0.92-1.01. Read straight off the waits with no fit, 1.01-1.10.
  A direct check with no fit at all (60 us of idle against 60 / 2.3 = 25-26 measurements): measured
  qubits keep 1.08, 1.10, 1.08, 1.09, 1.17, 1.18 times as much as the idle ones. The data show no
  extra cost at 27 on Kingston when the idle reference is measured and not extrapolated.

### 2. The 11 October Fez count

| | site | recomputed | verdict |
|---|---|---|---|
| Fits of the six curves (3 jobs x 2 groups) | all pass, worst chi2/dof 1.38 | 0.72 / 1.38 / 1.32 and 1.12 / 0.66 / 1.35; worst 1.38 | OK |
| Run-structure p | 0.88 / 0.97 / 0.30 and 0.93 / 1.00 / 0.15 | same | OK |
| Shape exponent, measured qubit | 0.823 +- 0.013 | 0.823 +- 0.012 | OK |
| Shape exponent, untouched qubits | 1.381 +- 0.074 | 1.381 +- 0.074 | OK |
| Separation | 7.4 widths | 7.41 | OK |
| Measured qubit below plain exponential | 14.1 widths | 14.5 (14.05 if exponents are first rounded to 3 places, as the page did) | rounding only |
| Level after 1 measurement | 0.965 | 0.9649 (job 1) | OK |
| Level after 128 measurements | 0.067 | 0.0670 (job 1) | OK |
| Level after 40 us idle | 0.661 | 0.6610 (job 1, same bits, same job) | OK |
| Crossing of 1/2 at | 25.5 measurements | 25.45 (job 1) | OK for job 1 only |

The fit numbers match the published reader (`read_the_count.py`, run on the raw shots here, and
`THE_COUNT_20261011.txt`) to the digit; `verify_cost.py` repeats the fits independently from the stored
per-qubit levels and agrees.

## What is mis-stated or needs a change on the site

1. **"40 us of plain idle" is not an equal-time comparison with 128 measurements.** 128 measurements
   at the manufacturer's stated 1.66 us take 212 us, five times longer than 40 us. The idle arm for
   the measured qubits stops at 40 us. Comparing 0.067 with 0.661 therefore mixes five times the time.
   `what-we-measured.html` calls it "a comparable stretch"; it is not. Equal-time pairs that the
   same jobs do contain (k measurements against k x 1.66 us of idle, measured qubit, three jobs):
   6 vs 10 us: 0.826, 0.799, 0.816 against 0.879, 0.853, 0.874;
   12 vs 20 us: 0.694, 0.669, 0.677 against 0.796, 0.752, 0.781;
   24 vs 40 us: 0.517, 0.481, 0.498 against 0.661, 0.623, 0.647.
   So at equal time the measured qubit is lower, by 0.05-0.15. That is a sound statement; the 128 vs
   40 us one is not. (The idle value 0.661 itself is correct and is from the same job and the same qubits.)
2. **0.965 / 0.067 / 0.661 and the 25.5 crossing come from the first of the three jobs only.** The
   other two give 0.955 / 0.055 / 0.623 and 0.964 / 0.060 / 0.647, and crossings at 22.6 and 23.9.
   The published reader hard-codes the sentence "passes 1/2 at 25.5 looks" in the notes of all three
   jobs, so the other two jobs' notes carry the wrong number.
3. **"79 spectator qubits per read"** is true of job 1 only; jobs 2 and 3 keep 83.
4. **The widths in "0.823 +- 0.013" and "1.381 +- 0.074" are the spread of three numbers**, as the page
   says, and the page's 7.4 divides by the spread of single jobs. The uncertainty of the mean of
   three is smaller by sqrt(3): that would give 12.8 widths. The fits' own per-job widths are
   0.007-0.009 and 0.078-0.081. With n = 3 these widths are themselves very uncertain.
5. **"All six fits pass" leaves out a third curve** in each job (a no-measurement control with only
   5 points), whose stretched-exponential fit fails badly (chi2/dof 22.8 / 32.2 / 28.2). The page's
   count of six is correct as worded (three jobs x two groups); say that the control arm is not
   fitted by this form.
6. **The 1.16-1.18 line** (above) is not reproducible as worded and the Kingston data do not show an
   excess at 27 once the idle reference is not extrapolated. It also appears on the page directly
   above the Fez paragraphs without naming Kingston or its two days.
7. **"kept through 3 measurements 0.921 +- 0.004, through 9 0.826 +- 0.005, through 30 us idle 0.760
   +- 0.006"** sits among the Fez paragraphs but is not in the Fez count (that ladder has no 9; k = 3
   gives 0.904 / 0.897 / 0.897 on the 0-to-1 axis). The ledger (entries 161 and 191) names 0.921 / 0.826
   as an older result from the 30 Sept to 2 Oct work ("old 0.921 / 0.826"). I did not recompute it and
   it is not in this package.
8. The ledger cites the Kingston 4 Oct reads as "runs 331-333". The count jobs are runs 341-343;
   331-333 are a different, shorter ladder (up to 9 measurements) on the same day.

## Can an outside reader reproduce these from the published files today?

* `the_count.py` is the script that **submits** the jobs to IBM hardware (account and credentials
  needed; it imports `common.py` and `live.py`, and also refers to `analyze.py`, which is not in the
  folder). It cannot be run from published files and does not compute any of the numbers above.
* `read_the_count.py` is the reader. It needs `data/fire/ibm_fez/run901_meta.json` and
  `run901_results.npz` (about 228 MB per job). **Those raw files are not published** under
  `heuremen.org/experiments`; only the roles file `data/reads/lookwide_roles_ibm_fez.json` is. The
  site README states the raw data are about 22 GB and available on request.
* `THE_COUNT_20261011.txt` is the reader's printed output for the three Fez jobs. I ran the
  reader on the raw shots from the private tree; its output matched that text digit for digit. This
  package adds the compact data (`data/fez_count_20261011.json`) so the fits can be rerun without the
  raw shots.
* Nothing published reproduces the Kingston table; the scoring script is missing (see above).

## Files

* `verify_cost.py` - the check. `data/*.json` - the reduced data (levels per qubit, point widths from
  the shot-level resampling, job IDs).
* `build_cost_data.py` - how the JSON was made from the raw shots (needs numpy and the private data;
  provenance only).
* Widths of single points and of b come from resampling the shots 40 times (seed 20261011), done in the
  published `read_the_count.py`; the shots are not in this package, so `verify_cost.py` reads those
  widths from the file and cross-checks b's width by redrawing points from them.
