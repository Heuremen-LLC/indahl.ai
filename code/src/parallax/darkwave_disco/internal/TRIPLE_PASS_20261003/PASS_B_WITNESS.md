# TRIPLE PASS, SEAT B -- THE WITNESS, ACROSS FIRINGS (3 October 2026)

Read-only audit by Bones. Nothing was edited, nothing was submitted. New files from this seat: this page, `pass_b_arith.py` (sha256 `82e38effdd0ee357de49a256d437786dd0f6e7e30fe368255d49713d4baf4317`) and its printout `pass_b_arith.txt` (sha256 `9f95e3f344f3db2612ac82dfbf3ea146a7655a0789c667cb4561dda85f5f934b`). Every number marked "derived here" is arithmetic in that script, on numbers typed in from the reads it names.

## How to read this page

**Clocks (The Stake).** Every number carries one tag.
- **LAID** = our laid time, the maker's stated timings, the maker's job stamps.
- **WITNESS** = a spectator qubit's reading, or another firing reading the same thing.
- **OWN** = the qubit's own decay clock: its level, its own fitted decay times, and any bookkeeping built from its own survival in the same job.

**Times.** Times are the maker's "running" stamps, converted to EDT [LAID]. They come from the fire records as indexed in `TRIPLE_PASS_20261003/index_firings.txt`, an index another seat built today and that I read only. Where a read prints a submit time instead, I say so. The 9/28 family carries the folder stamps (UTC), as the ledger does.

**FRICTION.** Two witnesses are in friction when their ±width bars do not touch: |a − b| > wa + wb. Every friction pair also carries its gap in combined widths, sqrt(wa² + wb²), for reference. A value printed without a width cannot be placed. It is laid beside the others and marked "no width".

**Witness count.** Each count is given as firings (jobs) / chips / days / designs. Three reads of one run are one firing with three jobs.

**Sources.**
- The ledger is `parallax/THIRD_RUNG_20260928.md`, cited as §n.
- Reads are in `parallax/out/qubit_fifth_run/data/reads/`. This folder is byte-identical to `darkwave_disco/for_indahl_ai/data/reads/` (checked with `diff -rq`).
- The 10/3 re-reads are in `darkwave_disco/internal/reads_new/`.
- Runs 1-3 are in `out/qubit_three_runs/data/reads/`. The Boston shot is in `out/qubit_stone_run/data/reads/`.
- Run 121 seen from three seats is in `internal/THREE_SEATS_RUN121_20261003.md`.

## The corpus walked (every hardware firing that touches a claimed quantity)

**IBM, 9/24-9/28.**
- The fire records list 113 re-pulled jobs: Marrakesh 64, Kingston 9, Fez 40.
- Of these I used:
  - the 9/28 parallax two-look runs (Marrakesh `20260928_083041`, Kingston `_123452`, Fez `_125537`);
  - the 9/28 echo (Marrakesh `echo_20260928_122733`, 14 jobs at gaps of 20 us to 2 ms);
  - the 9/24 three-box, dark_floor and dark_link jobs;
  - the Fez crowd and listen records (§31);
  - the Fez/Kingston tile-8 buzz records (§33, §40 "34g run").
- The 9/28 Fez darkwave, beat, partner, split, ring, alone, barrier, eleven, culprit, oddraw, the_do and ripples folders feed none of the quantities below. The only exception is the order of looking (§19 item 6, the eraser's late measurements).

**Older records the ledger cites.** The April 27 Q-BERT runs (Kingston, then three chips) and the August sweep (§15-16). These are not part of the 9/24-9/28 re-pull.

**Rigetti Cepheus-1-108Q, 9/25-9/28.** 563 tasks (§28). Used: §5-§14, §18, §21, §31, §36d, the step-3 qutrit three-box.

**IBM, 10/1-10/2.** 75 fire records, 74 with results:
- Runs 1-3 on Kingston, Phoenix and Pittsburgh (10/1 23:09 to 10/2 02:00);
- the Boston stone shot. The maker's stamps say it ran **08:18:55 / 08:19:14 / 08:19:39 EDT**; the ledger §112 wrote "~10:15". This is a LAID-clock row of its own, and it puts Boston before run 5;
- run 5 (Marrakesh 08:47:48);
- run 6 (Pittsburgh, cancelled, nothing returned);
- run 9 (Pittsburgh 09:14:12);
- run 7 (Kingston 09:14:36);
- run 10 (Pittsburgh 09:18:57, Kingston 09:19:16);
- the jump run, runs 11-18 (09:31-09:59);
- the tail run, runs 21-23 (10:09 / 10:13 / 10:17), and the lone look, run 31 (10:18:45);
- the half-push run, runs 41-43 (ran 11:38:46 / 11:39:42 / 11:43:42);
- the sides run, run 51 (11:53:28), and the turns run, run 61 (12:05:35);
- the hold run, runs 71-73 (12:07:32 / 12:11:33 / 12:15:33), and the stopwatch, run 81 (12:26:00);
- the push run, runs 91-93 (13:09:51 / 14:26:15 / 14:27:43);
- the look-time run, runs 101-103. These ran 14:25:04 / 14:26:42 / 14:28:33; run 101 was submitted at 13:13:55;
- the give-back run, runs 111-113 (14:25:36 / 14:27:12 / 14:29:08);
- the band runs 210-237 (Marrakesh, 24 jobs, 14:30-14:38);
- the move: run 141 on Marrakesh (17:27:54) and run 141 on Kingston (17:28:13);
- the no-name shot, run 121 (Pittsburgh, ran 17:41:43 after 96 minutes in the queue).

**Frozen, never fired.** Runs 8, 52-53, 82-83, 122-123, 131-133, and 142-143 on Kingston and on Marrakesh. None of them is a witness.

---

# A. THE LOOK

## Q1. The look, LAID: the maker's stated length of one readout

**Claims.**
- 7_PUBLIC Finding One: "the maker's stated look: 2.18 us".
- The ratios in Findings One, Three, Four and Six.
- LAWS Law 5.
- Paper §3.1, Table 2.

**Positions.**
- LAID: this quantity.
- WITNESS: Q2.
- OWN: Q3.

| when [LAID] | firing | chip | value | source |
|---|---|---|---|---|
| 10/1 21:33:20 EDT (calibration stamp 21:02:25) | live read before Run 1 | ibm_kingston | 2.18 us, median = max over 156 qubits [LAID] | `out/qubit_three_runs/live_kingston_readonly_20261001.json` |
| 10/2 11:02:53 EDT | read during the half-push submission | ibm_pittsburgh | 2.180 us, min = max over 156 qubits [LAID] | `reads/maker_look_length_pittsburgh.json`; `close_looktime.txt:18` |

**Lap one (oldest to newest).**
- Kingston's table reads 2.18 us.
- 13 hours later, Pittsburgh's table reads 2.180 us.
- Neither table carries a width. Each is one number given to every qubit.

**Lap two (newest to oldest).**
- Pittsburgh's own number (11:02) moves into the seat that Kingston's number filled in §120 (1) at 10:05. There, the jump re-rack used "Kingston's, read 10/1; Pittsburgh's not read" as the outside leg. The value in that seat does not change.
- No other chip's stated look is on disk: Marrakesh, Fez, Phoenix and Boston were never read.

**FRICTION.** None.

**Independent witnesses.** 2 reads (2 jobs' worth of configuration) / 2 chips / 2 days / 1 kind (the maker's table).

## Q2. The look, WITNESS: spectators time one readout

**Claims.**
- 7_PUBLIC Finding One: "2.37 ± 0.03 us".
- LAWS Law 5.
- Paper Table 2: 2.3494 ± 0.0650 (block of 3) and 2.3699 ± 0.0318 (block of 9).

**Positions.** WITNESS = spectator phase over a block of readouts on far qubits, converted to time on a curve fitted from LAID delays of 0/30/60/120 us. The spectator clock is calibrated in LAID microseconds.

| ran [LAID] | job | 3 looks, us [WITNESS] | 9 looks, us [WITNESS] | not wired, 3 / 9 | wired, 3 / 9 |
|---|---|---|---|---|---|
| 14:25:04 | 101 | 2.4940 ± 0.1124 | 2.4718 ± 0.0512 | 2.6494 / 2.5589 | 2.3111 / 2.3424 |
| 14:26:42 | 102 | 2.1654 ± 0.1017 | 2.2802 ± 0.0464 | 2.1719 / 2.3154 | 2.1299 / 2.2310 |
| 14:28:33 | 103 | 2.3888 ± 0.1225 | 2.3578 ± 0.0659 | 2.4847 / 2.2212 | 2.2710 / 2.3998 |
| all three | 101-103 | 2.3494 ± 0.0650 | 2.3699 ± 0.0318 | 2.4353 ± 0.0965 / 2.3652 ± 0.0487 | 2.2373 ± 0.0841 / 2.3244 ± 0.0413 |

Source: `close_looktime.txt:2-8`. 83 spectators.

**Close neighbours: other witnesses reading a LAID interval, in the order they were taken.**
- The tile-8 buzz on Fez, 9/2x (§40, 34g run). A readout-line tone reads 0.1-1.4 ns for every laid Ramsey wait from 0 to 20 us, across 26 batches [WITNESS: not a qubit].
- The stopwatch, run 81, at 12:26. Spectators time an emitter's laid ON interval at 35.6 us for a LAID 40 us and 48.3 us for a LAID 60 us. These are medians; no width is printed (`witness_run.txt:16`).
- Run 121 at 17:41. t_W = 14.63 ± 0.85 us of ON time per LAID 30.016-us stretch, read at the reader's ensemble coupling (THREE_SEATS; "seat 3 on another scale").

**Lap one.**
- The buzz never sees the 0-20 us waits.
- The stopwatch sees 0.89x and 0.80x of the laid ON time, by its own normalisation.
- The look-time jobs read 2.47 → 2.28 → 2.36 us per look (block of 9), each job two minutes after the last.
- Run 121's witnesses read 0.49x of the laid ON stretch, at the ensemble coupling.

**Lap two.**
- **Run 121 on the look-time run.** Run 121 holds the same spectator roles (same seed). It reads the emitter's ON time short of the LAID time, not long. But it reads an ON interval through a coupling, and the look-time run reads a readout block through free precession. One cannot be converted into the other with a number on disk.
- **Job 103 on jobs 101-102.** The three jobs, taken within three and a half minutes, spread 2.28-2.47 us. That spread is wider than any one job's shot width. The "± 0.03" is the shot width of the mean, and it does not hold this wander. The paper says so too.
- **The stopwatch on the buzz.** A spectator qubit DOES advance with laid time, at roughly 0.8-0.9x by its own ruler. The buzz does not advance at all. See Q26.

**FRICTION.**
- Job 101 vs job 102, 9 looks: **2.4718 ± 0.0512 vs 2.2802 ± 0.0464 us** (gap 0.192, bars 0.098; 2.8 combined widths).
- Job 101 vs job 102, 3 looks: **2.4940 ± 0.1124 vs 2.1654 ± 0.1017 us** (2.2 combined widths).
- Not wired vs wired, 3 looks, same jobs: **2.4353 ± 0.0965 vs 2.2373 ± 0.0841 us** (1.6 combined widths). In the 9-look block the bars touch (2.3652 ± 0.0487 vs 2.3244 ± 0.0413).
- The three-job mean vs the maker: **2.3699 ± 0.0318 vs 2.180 [LAID, no width]** (gap 0.190; six of the spectators' own widths).

**Independent witnesses.** 1 firing (3 jobs) / 1 chip / 1 day / 1 design. No other chip and no other day has a spectator-timed readout.

## Q3. The look, OWN: what one look costs the looked-at qubit, in its own decay time

**Claims.**
- 7_PUBLIC Finding One: "3.5 ± 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back".
- LAWS Law 5.
- Paper Table 2: eight jobs, 3.2-4.3 us; "Repeated readouts add up"; caveats (i) and (ii).

**Positions.**
- LAID: the stated 2.18 us.
- WITNESS: 2.37 us.
- OWN: the bit's level falls by as much as its own decay over the times below.

| ran [LAID] | firing (jobs) | chip, bits | reading [clock] | value | source |
|---|---|---|---|---|---|
| 10/2 00:14 / 00:43 / 00:53 | Run 2, Kingston / Phoenix / Pittsburgh (1 each) | 9 bits each | "bite": level 60 us after a look, minus plain fading at the chip's own level clock [OWN level, LAID 60 us] | −0.053 ± 0.014 / −0.071 ± 0.020 / −0.008 ± 0.012 | §113(2), §114(2) |
| 08:19 | Boston Run 2 (1) | 9 bits | same bite [OWN] | −0.048 ± 0.019 | §113-§114 |
| 08:47 | run 5, Marrakesh (1) | 9 bits | look, look again with no laid time, ON: look 2 − look 1 [OWN level] | −0.0480 ± 0.0071 → **11.0 ± 1.7 us** on τ 223 us (derived here) | `none_arm_three_chips.txt:6`; `run5_marrakesh.txt:83` |
| 08:47 | run 5 | 9 bits | bite at 60 us [OWN] | −0.079 ± 0.026 | `run5_marrakesh.txt` |
| 09:14:12 | run 9, Pittsburgh (1) | 9 bits | no-time pair [OWN] | −0.0272 ± 0.0060 → **7.3 ± 1.6 us** (τ 263) (derived) | `none_arm_three_chips.txt:27` |
| 09:14:12 | run 9 | 9 bits | bite at 60 us [OWN] | −0.068 ± 0.019 | `run9_pittsburgh.txt:90` |
| 09:14:36 | run 7, Kingston (1) | 9 bits | no-time pair [OWN] | −0.0204 ± 0.0053 → **5.3 ± 1.4 us** (τ 255 from Run 1) (derived) | `none_arm_three_chips.txt:48` |
| 09:31-09:59 | jump run 11-18 (8) | Pittsburgh, 154-156 bits | no-time pair, per-job median bit [OWN] | 3.88, 4.26, 3.31, 3.20, 3.68, 3.20, 3.58, 3.58 us (no per-job width printed); each bit over 8 jobs: 3.23 [2.36, 4.97]; MID 3.68 [1.88, 5.92]; read back from the waits: 8.27 [3.62, 12.85]; bite × clock by thirds 3.4 / 3.2 / 3.6 | `jump_rerack.txt:7-28`; §119(5) |
| 10:09-10:17 | tail run 21-23 (3) | Pittsburgh, 152 bits | extra time at no wait, median bit [OWN] | 4.02 [1.27, 6.20] / 3.51 [1.73, 6.05] / 3.42 [1.00, 6.19]; over the reads 3.63 (ON), 3.19 (MID); by thirds 3.44 / 3.73 / 3.41 | `tail_run.txt:9-22` |
| 10:18:45 | lone look 31 against the tail (1 + 3) | Pittsburgh | one look over none at no wait, bit by bit [OWN level] | 0.9858 (about 1.4 % at once) | `lone_vs_tail.txt:12` |
| 12:07-12:16 | hold run 71-73 (3) | Pittsburgh | one look at 150 us, end level minus nothing done [OWN] | −0.0007 ± 0.0009 → **0.57 ± 0.73 us** (derived); bit by bit "says 300.0 us" | `hold_run.txt:5,13` |
| 12:07-12:16 | hold run (3) | Pittsburgh | 3 / 9 looks 30 us apart, per look [OWN] | 3.83 / 3.00 us (bit by bit); middle bits 6.70 / 4.13 / 2.97 and 4.03 / 4.06 / 4.19 | `hold_run.txt:6-7` (derived) |
| 14:25:36 / 14:27:12 / 14:29:08 | give-back 111-113 (3) | Pittsburgh, 148 bits | one look at 0 / 150 / 270 us, cost by the end [OWN] | 3.5313 ± 0.8737 / 3.5569 ± 0.9309 / 4.0507 ± 0.9397; per job at 0: 6.53 / 1.02 / 3.04; at 150: 3.45 / 1.31 / 5.91; at 270: 4.54 / 0.73 / 6.88 (each ± 1.5-1.9) | `close_giveback.txt:2-6` |
| 10/2 afternoon, no fire | ledger §135 | Pittsburgh | "pile-up 3.5 ± 0.2 per look over 3 and 9 looks" | 3.5 ± 0.2 (the computation is not in the release) | §135; 7_TRACE item 5 |

**Lap one.**
- Overnight, the bites at 60 us read −0.053 (Kingston) and −0.071 (Phoenix); Pittsburgh's reads −0.008. Boston (08:19) reads −0.048.
- In the morning:
  - the no-time pair on nine blind bits reads 11.0 us (Marrakesh), 7.3 us (Pittsburgh) and 5.3 us (Kingston), all derived;
  - Pittsburgh's bite reads −0.068;
  - on all 156 bits, the jump run's eight jobs read 3.2-4.3 us at the median bit, and the tail run reads 3.4-4.0 us.
- At noon, the hold run's nine looks add 3.0 us each and three looks 3.8 us each, while one look at 150 us leaves 0.6 ± 0.7 us.
- At 14:25-14:29, a single look reads 3.5 / 3.6 / 4.1 ± 0.9 us. One of those three jobs (112) sits near 1 us at all three positions.

**Lap two.**
- **Give-back (14:25-14:29) on the hold run (12:07).**
  - Give-back puts 3.56 ± 0.93 us on a single look at 150 us. The hold run's single look at 150 us left 0.57 ± 0.73 us. The bars do not touch.
  - Inside give-back, the jobs themselves spread 0.7-6.9 us.
  - So "never given back" stands on the three-job mean. Two of give-back's jobs, and the hold run's one-look arm, sit far from it.
- **The hold run on the jump and tail runs.**
  - Repeated looks cost 3.0-3.8 us each on the bit-by-bit count. That is inside the jump/tail range of 3.2-4.3.
  - On the median bit, three looks cost 3.0-6.7 us per look. Two statistics on one job.
- **The jump run (156 bits) on run 9 (nine bits).**
  - Same chip, 17-45 minutes later. Run 9's nine bits give 7.3 ± 1.6 us (derived). The jump run's median bit gives 3.2-4.3 us.
  - §116(3) and §117 name run 9's bits q12, q108 and q141 as the ones "in their short state" that morning. They carry run 9's largest no-time drops: −0.060, −0.119, −0.062.
  - Different bits and a different statistic (mean of nine against median of 156).
- **Run 9 (09:14) on Run 2 (00:53).** Pittsburgh's bite goes −0.008 ± 0.012 → −0.068 ± 0.019. §117 then reads 0.2-0.4 swings in single bits within 4.5 minutes.
- **Runs 5/9/7 on each other.**
  - The no-time drop on three chips, within 27 minutes: Marrakesh −0.0480, Pittsburgh −0.0272, Kingston −0.0204.
  - These are three chips with three sizes; Marrakesh's bars are apart from the other two.
  - The 3.5 us headline, and the 1.48 stretch built on it, come from Pittsburgh's full-chip runs only.

**FRICTION.**
- Give-back job 111 vs job 112, look at 0 us: **6.53 ± 1.51 vs 1.02 ± 1.49 us** (2.6 combined widths).
- Job 112 vs job 113, look at 150 us: **1.31 ± 1.58 vs 5.91 ± 1.57**.
- Job 112 vs job 113, look at 270 us: **0.73 ± 1.53 vs 6.88 ± 1.87**.
- One look at 150 us: give-back **3.56 ± 0.93 us** vs hold run **0.57 ± 0.73 us** (derived; 2.5 combined widths).
- No-time drop: Marrakesh **−0.0480 ± 0.0071** vs Kingston **−0.0204 ± 0.0053** (3.1 combined widths), and vs Pittsburgh run 9 **−0.0272 ± 0.0060**.
- In us (derived): Marrakesh **11.0 ± 1.7** vs Kingston **5.3 ± 1.4**.
- Pittsburgh run 9's nine bits, **7.3 ± 1.6 us** (derived), vs the §135 pile-up **3.5 ± 0.2 us**.
- Bite at 60 us: Pittsburgh Run 2 **−0.008 ± 0.012** vs run 9 **−0.068 ± 0.019**, vs Kingston Run 2 **−0.053 ± 0.014**, and vs Marrakesh run 5 **−0.079 ± 0.026**.

**Independent witnesses.** 12 firings (Run 2 ×3 chips, Boston, runs 5/9/7, jump, tail, lone, hold, give-back), plus the §135 statement / 5 chips (Pittsburgh, Kingston, Marrakesh, Phoenix, Boston) / 2 days / 4 designs (no-time pair; bite at 60 us; looks inside a 300-us idle; one look at three positions). The number printed in 7 (3.5 ± 0.2) is one ledger statement on one chip.

## Q4. The three ratios, and the stretch 1.48

**Claims.**
- 7_PUBLIC Finding One: witness/maker 1.087 (12/11), qubit/maker 1.606 (phi), qubit/witness 1.477 (phi × 11/12).
- Finding Four residents: 1.083, 1.520, 1.603.
- Finding Six: "The look stretches the qubit 1.48x against its witnesses; the photon ring over the horizon is 1.5". The call: "1.5 on every chip".
- Paper "Ratios": 1.087 ± 0.015, 1.61 ± 0.09, 1.48 ± 0.09.

**Positions.**
- Built from Q1 [LAID], Q2 [WITNESS] and Q3 [OWN].
- Only ibm_pittsburgh has all three.
- On Kingston: LAID (2.18) and OWN (run 7, Run 2 bite); no WITNESS.
- On Marrakesh: OWN only.

**The same ratio with each OWN witness in turn** (WITNESS 2.3699 ± 0.0318, LAID 2.180; derived here, `pass_b_arith.txt` §2):

| OWN witness | us | qubit/maker | qubit/witness |
|---|---|---|---|
| §135 pile-up (the one 7 uses) | 3.50 ± 0.20 | 1.61 ± 0.09 | **1.48 ± 0.09** |
| jump, lowest / highest job median | 3.20 / 4.26 (no width) | 1.47 / 1.95 | 1.35 / 1.80 |
| jump, each bit over 8 jobs | 3.23 | 1.48 | 1.36 |
| tail over 3 jobs | 3.63 | 1.67 | 1.53 |
| hold, 3 looks / 9 looks (bit by bit) | 3.83 / 3.00 | 1.76 / 1.38 | 1.62 / 1.27 |
| give-back at 0 / 150 / 270 us | 3.53 ± 0.87 / 3.56 ± 0.93 / 4.05 ± 0.94 | 1.62 / 1.63 / 1.86 (± 0.4) | 1.49 / 1.50 / 1.71 (± 0.4) |
| give-back job 112 / 113 at 270 us | 0.73 ± 1.53 / 6.88 ± 1.87 | 0.33 / 3.16 | 0.31 ± 0.64 / 2.91 ± 0.79 |
| run 9, nine bits (derived) | 7.26 ± 1.62 | 3.33 ± 0.74 | 3.06 ± 0.68 |
| Kingston run 7 (no WITNESS on that chip) | 5.26 ± 1.38 | 2.41 ± 0.63 | -- |

**Lap one.**
- The morning's nine-bit runs put qubit/maker at 2.4-5.0 on three chips (derived).
- The full-chip Pittsburgh runs (jump, tail, hold, give-back) put qubit/witness between 1.27 and 1.80.
- The pile-up estimate gives 1.48 ± 0.09.

**Lap two.**
- The witness leg (14:25-14:28) is one run. Its three jobs alone move qubit/witness by ±0.07 (3.5 / 2.47 = 1.42 to 3.5 / 2.28 = 1.54).
- The OWN leg depends on which Pittsburgh firing stands in it: 1.27-1.80 across the full-chip runs.
- The "1.5 on every chip" call has no second-chip witness at all. No other chip ever had its readout timed by spectators.

**FRICTION.**
- qubit/witness **1.48 ± 0.09** (§135 pile-up) vs **3.06 ± 0.68** (run 9's nine bits, derived).
- **1.48 ± 0.09** vs **2.91 ± 0.79** (give-back job 113 at 270 us).
- **1.48 ± 0.09** vs **0.31 ± 0.64** (give-back job 112 at 270 us).

**Independent witnesses.** All three legs together on 1 chip / 1 day. The WITNESS leg is 1 firing (3 jobs).

---

# B. THE QUBIT'S OWN CLOCKS

## Q5. What a |1> keeps after 300 us (Pittsburgh "0.313-0.335")

**Claims.**
- 7_PUBLIC Finding Three: pi ↔ 1/pi, "a Pittsburgh qubit keeps 0.313-0.335 of itself after 300 us".
- §159: "a Pittsburgh bit keeps ~0.31 after 300 us vs the universe's ~0.31 matter share".
- Paper Table 6, idle-in-1 column.

**Positions.** OWN level after a LAID 300 us.

| ran [LAID] | firing | bits, statistic | kept at 300 us [OWN] | source |
|---|---|---|---|---|
| 10/2 00:05 / 00:53 / 02:00 | Pittsburgh Runs 1 / 2 / 3 | 9 bits; 0 / 1 / 2 earlier looks | 0.314 / 0.347 (Run 2 frame 0.351 ± 0.013) / 0.319 | §113(4); `all_three_chips.txt:202` |
| 09:14 | run 9 | 9 bits, one earlier look | 0.2808 ± 0.0144 | `run9_pittsburgh.txt:43` |
| 10:09 / 10:13 / 10:17 | tail run | median bit, one earlier look | 0.3290 / 0.3362 / 0.3233 | `tail_run.txt:5-7` |
| 10:18 | lone look | median bit, no look | 0.3277 | `lone_vs_tail.txt:5` |
| 12:07 / 12:11 / 12:15 | hold run | mean over readable | 0.3336 ± 0.0021 / 0.3361 ± 0.0022 / 0.3366 ± 0.0026 → **0.3354 ± 0.0013**; median bit 0.3546 / 0.3600 / 0.3497 | `discarded_hold.txt:144`; `hold_run.txt:4` |
| 13:09 / 14:26 / 14:27 | push run | mean, 141 bits | 0.3164 ± 0.0019 / 0.3101 ± 0.0025 / 0.3129 ± 0.0024 → **0.3131 ± 0.0013** | `close_push.txt:12` |
| 14:25 / 14:27 / 14:29 | give-back | mean, 148 bits | 0.3241 ± 0.0014 / 0.3195 ± 0.0015 / 0.3135 ± 0.0015 → **0.3190 ± 0.0009** | `close_giveback.txt:8` |
| 17:41 | run 121 | mean, 150 bits | **0.3286 ± 0.0030** | `noname_read1.txt:6` |

**Other chips.**
- Kingston:
  - Run 2: 0.2977 ± 0.0121 (9 bits, one look);
  - Run 1-3 ladder: 0.302 / 0.302 / 0.261;
  - run 141: 0.2982 ± 0.0025.
- Marrakesh:
  - run 5: 0.2445 ± 0.0139 (9 bits, one look);
  - run 141: 0.1786 ± 0.0019.
- Phoenix: 0.197 / 0.160 / 0.163.
- Boston: 0.273 / 0.279 / 0.262.
- (Run 1's own frame normalises to the 60-us level, so its printed "0.398" is a different ruler.)

**Lap one.** Over one day Pittsburgh's 300-us level goes 0.31 (night) → 0.28 (09:14, nine bits) → 0.32-0.34 (10:09-10:18) → 0.335 (hold, 12:07) → 0.313 (push, 13:09-14:27) → 0.319 (give-back, 14:25-14:29) → 0.329 (run 121, 17:41).

**Lap two.**
- **Run 121 on everything before it.** It sits between the push run and the hold run, with bars apart from both.
- **Give-back on push.**
  - Jobs from the two runs interleave inside 14:25-14:29: 111, 92, 112, 93, 113.
  - Push 92 (14:26:15) reads 0.3101 ± 0.0025; give-back 112 (14:27:12) reads 0.3195 ± 0.0015, one minute later. The bars are apart.
  - Push 93 (14:27:43) at 0.3129 and give-back 113 (14:29:08) at 0.3135 touch.
- **Give-back's own three jobs.** 0.3241 → 0.3135 within 4 minutes; bars apart.
- **Push (13:09) on hold (12:07).** 0.3131 against 0.3354, twelve combined widths.
- The range "0.313-0.335" printed in 7 is the push run's mean at one end and the hold run's mean at the other. Those two witnesses do not agree with each other.

**FRICTION** (all Pittsburgh unless named):
- push **0.3131 ± 0.0013** vs hold **0.3354 ± 0.0013** (12.1 combined widths);
- give-back **0.3190 ± 0.0009** vs hold (10.4);
- push vs give-back (3.7);
- hold vs run 121 **0.3286 ± 0.0030** (2.1);
- push vs run 121 (4.7);
- give-back job 111 **0.3241 ± 0.0014** vs job 113 **0.3135 ± 0.0015** (5.2);
- push job 92 **0.3101 ± 0.0025** vs give-back job 112 **0.3195 ± 0.0015** (3.2);
- Run 2 (nine bits) **0.351 ± 0.013** vs run 9 (nine bits) **0.2808 ± 0.0144** (3.7);
- Marrakesh run 141 **0.1786 ± 0.0019** vs run 5 **0.2445 ± 0.0139** (different bit sets).

**Independent witnesses.** Pittsburgh: 8 firings (18 jobs) / 1 chip / 2 calendar days (one night and one day). Other chips: 4 chips, 6 firings.

## Q6. The qubit's two clocks

7_PUBLIC Finding Three pairs two kinds under 4/3 ↔ 3/4: "0.756 (one read, no earlier look) and 0.775 ± 0.009 (eight reads)". It uses Kingston's gap clock "0.60" as a 1/phi resident (Findings Three and Four, 1/0.60 = 1.667), and §159 adds "two clocks 9/12".

**(a) Early stretch against late stretch, |1> start, no look first.** [OWN, LAID stretch edges]

| ran | firing | early clock | late clock | early/late |
|---|---|---|---|---|
| 10:18 | lone look (1 job) | 0-6.7 us: 208 | 60-300: 275 | **0.756** (median-bit levels); bit by bit 0.803 |
| 10:09-10:17 | tail run (3 jobs), ONE look first | 0-6.7 | long clock | 0.720 / 0.740 / 0.625 per job; 0.686 over the jobs |
| 11:38-11:43 | half-push (3 jobs), ON | 0-6.7: 219 / 201 / 196 | 6.7-20: 248 / 258 / 258 | 0.88 / 0.78 / 0.76 (to the second stretch only) |
| 11:53 | sides (1 job), ON | 186 (derived) | 6.7-20: 258 | 0.72 (derived) |
| 12:05 | turns (1 job), ON by 2 quarter-turns | 217 (derived) | 253 | 0.86 (derived) |
| 17:41 | run 121 (1 job), in-job rulers | 0-10 us: 181 ± 7 | 0-300: 270 ± 2 | **0.672 ± 0.025** (derived); 0-30: 0.743; 0-90: 0.881 |

Run 121's ruler shape, against one exponential through its own 300-us point: −0.0141 ± 0.0019 (10 us), −0.0259 ± 0.0024 (30 us), −0.0185 ± 0.0032 (90 us) (`noname_read1.txt:7-9`).

**(b) Gap clock / level clock (START, LOOK, WAIT, LOOK; LAID waits 60 / 240 / 300).** [OWN]

| ran | firing | chip | gap / level |
|---|---|---|---|
| 10/2 00:14 | Run 2 | Kingston, 9 bits | 157 / 262 = **0.60 ± 0.07** |
| 00:43 | Run 2 | Phoenix | 122 / 178 = 0.68 ± 0.07 |
| 00:53 | Run 2 | Pittsburgh | 234 / 283 = 0.83 ± 0.11 |
| 01:03 / 01:20 | Run 3 | Kingston / Phoenix | gap clocks 139.6 ± 8.4 / 124 ± 7.4 (no ratio printed) |
| 08:19 | Run 2 | Boston | 245 / 308 = 0.80 ± 0.11 |
| 08:47 | run 5 | Marrakesh | 136 / 223 = 0.6076 ± 0.0822 (copies 0.586 / 0.618 / 0.598) |
| 09:14 | run 9 | Pittsburgh, same nine bits as Run 2 | 173 / 263 = 0.658 ± 0.100 |
| 09:31-09:59 | jump run (8 jobs) | Pittsburgh, all bits, every bit, no cut | per job 0.750, 0.774, 0.806, 0.730, 0.799, 0.782, 0.790, 0.767 → **0.775 ± 0.009** (the ± is the spread of the eight job values over √8; shot widths not printed; the number lives in §120 only, and no read file prints it) |

Sources: §105, §108(h), §113(1), §114(1), §116(2); `run5_marrakesh.txt:86`; `run9_pittsburgh.txt:86`; §120(2).

**(c) A jumping bit's short and long levels across reads** (jump run, the 25 bits past the cut): ON 0.717 ± 0.008, MID on ON's sorting 0.763 ± 0.023. A made-up smear through the same reader gives 0.704 / 0.751 (`jump_run.txt:21-22`; §119(3)).

**Lap one.**
- Overnight, the gap/level ratio reads 0.60 (Kingston), 0.68 (Phoenix) and 0.83 (Pittsburgh). In the morning it reads 0.80 (Boston), 0.61 (Marrakesh) and 0.66 (Pittsburgh's same nine bits).
- The jump run reads 0.73-0.81 across eight jobs.
- With no look, the early/late clock reads 0.756 (lone), then 0.72-0.88 (half-push, sides, turns; second stretch only), and finally 0.672 ± 0.025 (run 121).

**Lap two.**
- **Run 121 (17:41) on the lone look (10:18).** Its 10-us ruler puts the early clock at 0.67 of the 300-us clock. The lone job put it at 0.756 (0-6.7 us against 60-300 us).
  - Different stretch edges, so a neighbour, not a repeat.
  - Both have the bit fading faster early.
- **The jump run (all 156 bits) on the morning's nine-bit chips.**
  - It reads 0.775 ± 0.009, with bars apart from Kingston 0.60, Marrakesh 0.61, Phoenix 0.68 and Pittsburgh's own nine bits at 0.66.
  - Its bars touch Boston 0.80 and Pittsburgh Run 2 0.83.
- **Run 9 on Run 2.** Same nine bits, 8 hours and one maintenance apart: 0.83 → 0.66. §117 then read 0.157-0.164 rms single-bit swings within 4.5 minutes.
- 7 draws its 1/phi resident (0.60, Kingston, nine bits, one job) and its 3/4 resident (0.775, Pittsburgh, 156 bits, eight jobs) from the same design family. The two sit 2.5 combined widths apart.

**FRICTION.**
- Pittsburgh jump **0.775 ± 0.009** vs:
  - Kingston **0.60 ± 0.07** (2.5 combined widths);
  - Marrakesh **0.6076 ± 0.0822** (2.0);
  - Phoenix **0.68 ± 0.07** (1.4);
  - Pittsburgh run 9 **0.658 ± 0.100** (1.2).
- Kingston **0.60 ± 0.07** vs Pittsburgh Run 2 **0.83 ± 0.11** (1.8), and vs Boston **0.80 ± 0.11** (1.5).
- Early/late, run 121 **0.672 ± 0.025** (derived) vs jump two-clock **0.775 ± 0.009** (3.9). These are different definitions, kept here because 7 files both under "the qubit's two clocks".

**Independent witnesses.**
- (a): 6 firings (10 jobs) / 1 chip / 1 day.
- (b): 9 firings (16 jobs) / 5 chips / 2 days.
- The 0.756 rests on one job; the 0.60 rests on one job.

## Q7. The halfway state's early clock (123 us; "0.59 of the |1> state's")

**Claims.** 7_PUBLIC Finding Three: "the halfway state's early decay clock at 0.59 of the |1> state's (123 / 208 us, one read)". §156 lists the 0.6 family.

**Positions.** OWN clock over the first LAID 6.7 us, from middle-bit levels. None of these reads prints a width for these clocks.

| ran | firing | halfway early clock, us | ON early clock, us | halfway / ON |
|---|---|---|---|---|
| 10:18 | lone look (1 job) | 123 (bit by bit 0.263 of its own 60-300 clock) | 208 | **0.591** |
| 11:38 / 11:39 / 11:43 | half-push (3 jobs), one half-push | 139 / 114 / 131 (bit by bit 83) | 219 / 201 / 196 (bit by bit 207) | 0.635 / 0.567 / 0.668 |
| same | half-push, far side (full push + half-push) | 1732 / 452 / 201 | -- | -- |
| 11:53 | sides (1 job), frame turned 0 / 120 / 240 / 180 deg | 132 / 143 / 124 / 110 (derived) | 186 (derived) | 0.707 / 0.764 / 0.664 / 0.588 |
| 12:05 | turns (1 job), 1 / 5 / 9 quarter-turns; 3 (far side) | 163 / 111 / 154; 354 | 217 | 0.750 / 0.512 / 0.707 |
| 10:09-10:17 | tail run, ONE look first | 207 / 240 / 200 | 235 / 250 / 234 | 0.88 / 0.96 / 0.85 |

**Lap one.**
- The lone job gives 0.59.
- The half-push run, 80 minutes later, gives 0.57-0.67.
- The sides run gives 0.59-0.76, depending on the frame angle.
- The turns run gives 0.51-0.75, depending on the number of turns.
- After one look (tail), the halfway state's early clock sits near ON's (0.85-0.96).

**Lap two.**
- The turns and sides runs say the early halfway clock moves with how the halfway state was reached. The far-side starts read 201-1732 us early (half-push 1732 / 452 / 201; sides 285; turns 354). The one-half-push starts read 110-163.
- The half-push run (three jobs) brackets the lone job's 0.59 (0.57-0.67).
- The 0.59 itself is one job, and its ratio divides a halfway clock by the |1> clock of the same job (7_TRACE item 12).

**FRICTION.** None can be placed: no widths.

**Independent witnesses.** 5 firings (9 jobs) / 1 chip / 1 day. The printed 0.59 rests on 1 job.

## Q8. Decay times wander between jobs (underneath every cross-job comparison)

**Claims.**
- Paper §3.5 and Limitation 2: a qubit's decay time scatters 1.35x its shot width across 8 jobs, and single-qubit levels move 0.2-0.4 within 4.5 minutes.
- 7_PUBLIC Methods: "Comparisons are made only within a single job".

**Positions.** OWN clocks and levels, read at LAID times.

**IBM's own published T1 [LAID, the maker's table].** 9/26 → 9/28, per qubit: 0.32x to 4.87x. The median |log ratio| is 0.219 / 0.226 / 0.203 on Marrakesh / Kingston / Fez (§69).

**9/28 → 10/2 Marrakesh (§140; band runs 210-237).**
- The carry clock A keeps no rank: −0.06 / +0.03 / +0.10. Its middle size goes 44 us → 57 / 80 / 64 us.
- The drain clock B: −0.00 / +0.10 / −0.18 against 9/28; +0.47 / +0.44 / +0.48 between the 10/2 reads.

**Pittsburgh middle-bit |1> clocks across 10/2 [OWN].**

| firing | clock |
|---|---|
| Run 1 tauF (nine bits) | 269 ± 6 |
| matched window (§136) | 277 ± 10 / 288 ± 11 / 286 ± 15 |
| run 9 level clock | 263.1 ± 10.8 |
| jump ON clock per job | 295.5, 296.3, 284.5, 286.8, 282.2, 295.2, 284.0, 279.8 (one bit's shot width 21.7) |
| tail long clock | 286 / 287 / 276 |
| look-time emitter fading | 270.7 ± 8.0 / 281.8 ± 7.1 / 272.4 ± 7.0 |
| run 121, 0-300 | 269.6 ± 2.2 (derived) |

**Single bits [OWN level at a LAID 60 us after a look]** (`short_wait_across_time.txt`):
- Pittsburgh, night → 09:13: rms 0.157 (q108 −0.375, q12 −0.216).
- Pittsburgh, 09:13 → 09:18: rms 0.164 (q108 +0.372).
- Kingston, night → 09:19: rms 0.141.
- OFF levels move 0.011-0.019 rms.

**The jump run.**
- A bit's ON clock scatters 1.35x its shot width (middle).
- 25 bits scatter more than 2x, and 4 bits more than 3x.
- ON and MID clocks co-move +0.34 over all bits and +0.71 on the 25.

**Lap one.**
- The maker's table swings by factors of 3-5 on single qubits over two days.
- Single bits swing 0.2-0.4 in level overnight and again within 4.5 minutes.
- Middle-bit clocks drift 263-296 us over the day.
- Marrakesh's inside clocks do not keep their 9/28 order on 10/2.

**Lap two.** Every later firing on Pittsburgh reads a middle clock inside 263-296 us, and every one of them re-reads single bits by 0.1-0.4 within minutes. This wander is the width that none of the Q5, Q6, Q11 and Q12 cross-job shot widths carry.

**FRICTION.** Not split into pairs. The quantity is itself the spread.

**Independent witnesses.** Many (maker 3 days × 3 chips; 10/2 Pittsburgh 7 firings; Marrakesh 2 days).

## Q9. The microsecond clock against the shot clocks (+1.88 ± 1.16 series-taus)

**Claims.** 7_PUBLIC Finding Four: step two (1.923) has no ratio on the chip; "the microsecond clock sits +1.88 ± 1.16 series-taus from the shot clocks (a separation, not a ratio)".

**Positions.**
- Clocks in the house's series-tau unit (§57).
- The carry: OWN, microseconds.
- The echo, buzz and GHZ clocks: shots and angle-steps [LAID shot spacing].

**Witnesses (records).**
- The 9/28 Marrakesh echo:
  - carry τ 64 us (§36d: 63.8 us, 90 % band 41.8-85.0);
  - shot clocks 249 ± 24 shots at 20 us and 186 ± 21 shots at 2000 us.
- The buzz: Fez/Kingston tile 8.
- The GHZ pinata: Fez, 7/11, 6.56 steps.

**Readings.**
- §62: carry − echo = **+1.88 ± 1.16**; GHZ − carry = **−2.02 ± 1.18**. With the carry, the four clocks close at χ²/dof 2.60; without it, at 0.00. One shot would have to last ~5,600 us for the echo's two shot clocks to be one clock.
- §58: clock − split +1.83 ± 0.16 (χ²/dof 1.6, 19 rows across substrates); clock − arrow +1.10 ± 0.08 (χ²/dof 4.8).
- §60: the chip's own per-medium gap +2.07.
- §63: carry − drain (two microsecond clocks on one qubit) **−1.04 ± 0.31** (20 qubits).

**Lap one.** The echo (9/28) gives the carry. The chip triangle (§62, 10/1) places it +1.88 from the echo and −2.02 from the GHZ; the same size with opposite sign.

**Lap two.**
- §63 reads the carry against the other microsecond clock on the same qubits (the drain) at −1.04 ± 0.31.
- §140 (10/2 band reads) finds the carry clock's typical size at 57-80 us against 44 us on 9/28, with no rank kept. The microsecond leg itself moved between 9/28 and 10/2 (no widths printed).

**FRICTION.** None between like-defined pairs.

**Independent witnesses.** The microsecond leg is 1 firing (the 9/28 echo, 14 jobs) / 1 chip. The shot-clock legs are 3 records (echo, buzz, GHZ) / 2 chips / dates 7/11, 9/2x and 9/28.

## Q10. The 0.62-0.65 band (9/28)

**Claims.** 7_PUBLIC Finding Three: values near 0.618 recur, including "a 0.62-0.65 band on 9/28".

**Positions.**
- R² between two OWN inside clocks (carry A, drain B), across bits.
- The x-axis is a readout cutoff [LAID by us].

| record | cutoff 0.62 | 0.63 | 0.64 | 0.65 | 0.66 | 0.67 | 0.68 |
|---|---|---|---|---|---|---|---|
| 9/28 echo, Marrakesh | 0.228 ± 0.197 | 0.278 ± 0.215 | 0.322 ± 0.206 | **0.433 ± 0.222** | 0.001 ± 0.084 | 0.384 ± 0.256 | 0.309 ± 0.223 |
| 10/2 read 1 (runs 210-217) | 0.024 ± 0.145 | 0.024 ± 0.127 | 0.024 ± 0.144 | 0.025 ± 0.155 | 0.028 | 0.028 | 0.028 |
| 10/2 read 2 (220-227) | 0.000 ± 0.052 | 0.002 ± 0.089 | 0.017 ± 0.057 | 0.021 ± 0.060 | 0.024 | 0.016 | 0.009 |
| 10/2 read 3 (230-237) | 0.107 ± 0.187 | 0.040 ± 0.085 | 0.024 ± 0.101 | 0.004 ± 0.125 | 0.004 | 0.367 ± 0.281 | 0.339 ± 0.249 |

Source: `band.txt:9-15`. Kingston (9/28): no band on its own construction (R² ≤ 0.0012), using a different clock B (§69).

**Lap one.** 9/28 shows the band rising to 0.43 at 0.65 and gone at 0.66. On 10/2, three reads on the same 78 bits with the same code show nothing at 0.62-0.65. Read 3 shows a lift at 0.67-0.68, carried by one bit entering (q142).

**Lap two.**
- The 10/2 reads say the 9/28 band does not repeat on its own instrument four days later.
- Read 3's 0.67-0.68 lift sits on the 9/28 record's own 0.67-0.68 values (0.384, 0.309). The bars touch.
- §140 reads it as the inside clocks' own wander (Q8).

**FRICTION.** 9/28 **0.433 ± 0.222** vs 10/2 **0.025 ± 0.155 / 0.021 ± 0.060 / 0.004 ± 0.125**, all at cutoff 0.65 (1.5-1.8 combined widths; the bars do not touch).

**Independent witnesses.** 2 firings (1 + 24 jobs) / 1 chip / 2 days. Kingston is a different construction.

---

# C. THE CROSSING

## Q11. The crossing, start |0>: ten pushes 30 us apart, against one-exponential bookkeeping

**Claims.**
- 7_PUBLIC Status and Finding Two:
  - Pittsburgh +2.00 ± 0.16 (push run, three reads); the hold run's +2.17 ± 0.17;
  - Marrakesh +2.74 ± 0.28 and Kingston +2.87 ± 0.28 (one read each);
  - three-chip mean 2.54 % against the friction 2.65 %.
- Finding Four: sin²(pitch/2) = 2.19 % against 2.00 / 2.17.
- LAWS Law 4: "+2.0 to +2.9 % on three chips".
- Paper Table 6.

**Positions.** OWN level minus OWN bookkeeping (each qubit's own 300-us survival spread over the LAID 30-us intervals).

| ran | firing | chip, bits | crossing [OWN] | median qubit / share above 0 |
|---|---|---|---|---|
| 12:07 / 12:11 / 12:15 | hold run 71-73 | Pittsburgh 145 / 139 / 139 | +0.0190 ± 0.0030 / +0.0251 ± 0.0029 / +0.0210 ± 0.0028 → **+0.0217 ± 0.0017** | +0.0174 ± 0.0025 / 0.686 |
| 13:09 / 14:26 / 14:27 | push run 91-93 | Pittsburgh 141 | +0.0174 ± 0.0028 / +0.0213 ± 0.0030 / +0.0213 ± 0.0023 → **+0.0200 ± 0.0016** | +0.0137 ± 0.0023 / 0.627 |
| 17:27:54 | run 141 | Marrakesh 143 | **+0.0274 ± 0.0028** | +0.0229 / 0.73 |
| 17:28:13 | run 141 | Kingston 147 | **+0.0287 ± 0.0028** | +0.0266 / 0.76 |
| 17:41:43 | run 121, A30_30 (same laying) | Pittsburgh 150 | **+0.0126 ± 0.0032** | -- |
| 17:41:43 | run 121, N2 / N6 (2 / 6 pushes) | Pittsburgh | +0.0245 ± 0.0025 / +0.0207 ± 0.0034 | -- |
| 17:41:43 | run 121, A30_30 vs WA (same train, same emitters; THREE_SEATS seat 2) | 75 pairs | +0.0218 ± 0.0072 vs +0.0081 ± 0.0058 | -- |

Sources:
- `reads_new/hold_crossing.txt:20-29`;
- `close_push.txt:4`;
- `rep_marrakesh_read1.txt:4,16`;
- `rep_kingston_read1.txt:4,15`;
- `noname_read1.txt:27,59,63`;
- THREE_SEATS table.

The hold run's median-qubit values in `hold_run.txt:32` (+0.0154, +0.0139, +0.0050) are the frozen reader's median-bit version.

**The three-chip mean, with each Pittsburgh witness in turn** (derived):
- push run → 2.537 ± 0.142;
- hold run → 2.593 ± 0.144;
- run 121 → 2.290 ± 0.170.
- Against 100/(12 pi) = 2.6526, these sit −0.8, −0.4 and −2.1 widths away.

**Lap one.**
- The hold run gives 1.9-2.5 % per job. The push run gives 1.7-2.1 % per job.
- Marrakesh gives 2.7 %, then Kingston 2.9 %, 20 seconds apart.
- Pittsburgh's run 121 gives 1.26 % on the same laying 13 minutes later, with 2.45 % at two pushes and 2.07 % at six.

**Lap two.**
- **Run 121 on all four earlier witnesses.**
  - Its anchor arm (identical laying) reads 1.26 ± 0.32. The bars are apart from the push run, the hold run, Marrakesh and Kingston.
  - In the same job, its own short-stretch rulers sit 1.4-2.6 % under one exponential (Q6a, Q14). That is the size of the crossing.
  - Its witness arm (WA: same train, same emitters, neighbours frame-held) reads the long-clock crossing at +0.81 ± 0.58 against A30_30's +2.18 ± 0.72 on the same emitters.
- **Kingston and Marrakesh on Pittsburgh.**
  - Both are bigger than the push run and the hold run, with bars apart. Marrakesh has the smallest back-to-back mirror (±1.5 %) and a larger crossing (2.7 %).
  - Each is one job.
- **Push on hold.** Same circuit, 1-2 hours later: 2.00 against 2.17, bars touch. Hold job 72 (+0.0251) and push job 91 (+0.0174) do not touch.
- The mean against the median, per chip: 2.00 / 1.37 (push), 2.17 / 1.74 (hold), 2.74 / 2.29, 2.87 / 2.66. Every chip's mean sits above its median.

**FRICTION.**
- Push **+0.0200 ± 0.0016** vs Marrakesh **+0.0274 ± 0.0028** (2.3), and vs Kingston **+0.0287 ± 0.0028** (2.7).
- Hold **+0.0217 ± 0.0017** vs Kingston (2.1), and vs Marrakesh (1.7).
- Run 121 **+0.0126 ± 0.0032** vs push (2.1), hold (2.5), Marrakesh (3.5) and Kingston (3.8).
- Hold job 71 **+0.0190 ± 0.0030** vs job 72 **+0.0251 ± 0.0029** (1.5).
- Push job 91 **+0.0174 ± 0.0028** vs hold job 72 (1.9).
- Inside run 121: N2 **+0.0245 ± 0.0025** vs A30_30 (2.9); A30_30 vs WA on the same emitters, **+0.0218 ± 0.0072 vs +0.0081 ± 0.0058** (seat 2, 1.5).

**Independent witnesses.** 5 firings (9 jobs) / 3 chips / 1 day / 2 designs (push and hold circuit; run 121's anchor in a mixed job). Off Pittsburgh: 1 job per chip.

## Q12. The |1> column (and Kingston's −1.24 %)

**Claims.**
- 7_PUBLIC Finding Two: "Prepared |1>: +0.05 ± 0.13, −0.16 ± 0.21, −1.24 ± 0.24".
- Finding Seven: "Kingston ... −1.24 ± 0.24 % against its decay clock (one read)" against rung four 1.216 % and the neutron's 1.20 ± 0.54 %.
- Open list: "Kingston's |1> column".
- Paper: "not accounted for here".

**Positions.** OWN level minus OWN bookkeeping, LAID 30-us intervals.

**The witnesses, in time order** [OWN]:

| ran | firing | value |
|---|---|---|
| 12:07-12:16 | hold run (Pittsburgh) | +0.0022 ± 0.0029 / +0.0001 ± 0.0026 / +0.0019 ± 0.0023 → **+0.0014 ± 0.0015** |
| 13:09-14:27 | push run (Pittsburgh) | −0.0021 ± 0.0027 / +0.0026 ± 0.0022 / +0.0009 ± 0.0019 → **+0.0005 ± 0.0013**; median −0.005 (41 % above 0) |
| 17:27 | Marrakesh run 141 | **−0.0016 ± 0.0021**; median −0.0047 (44 %) |
| 17:28 | Kingston run 141 | **−0.0124 ± 0.0024**; median −0.0121 (34 % above 0) |
| 17:41 | run 121 (Pittsburgh), B30_30 one-clock | −0.0022 ± 0.0031; own stretches −0.0021 ± 0.0046 |
| 17:41 | run 121, WB (seat 2, 35 emitters) | −0.0094 ± 0.0052; pairs −0.0080 ± 0.0051 |

**Same circuit.** Hold.py's "parked on alternate tenths" arm IS this circuit: start ON, [30 us, X] ×10, look. Its per-qubit numbers equal the hold-run |1> column read for read (`reads_new/park_per_qubit.txt:21,25,29` against `hold_crossing.txt:21`). So Q20's third park closure and this column are one measurement.

**Kingston neighbours in the same job.**
- Back-to-back ten pushes: ON −0.0212 ± 0.0015 and OFF +0.0192 ± 0.0018.
- ON left alone 300 us: 0.2982.
- No-time look pair (run 7, 09:14): −0.0204 ± 0.0053.

**Lap one.** Pittsburgh's hold and push runs read 0.0, Marrakesh reads 0.0, and Kingston reads −1.24 %. Run 121 then reads Pittsburgh at −0.2 % (core arm) and −0.9 % (witness-arm emitters).

**Lap two.**
- **Run 121 on Kingston.**
  - Its core arm reads −0.22 ± 0.31; the bars do not touch Kingston's.
  - On the 35 emitters alone (THREE_SEATS, seat 2), the core arm reads −0.61 ± 0.65 % and the witness arm (WB, same train, frame-held neighbours) −0.94 ± 0.52 %. These two touch each other, and both touch Kingston's −1.24 ± 0.24.
  - On all 150 bits, the core arm's −0.22 ± 0.31 does not touch Kingston's.
- **Kingston on everything before it.** −1.24 % stands alone in the column, on one job. The rung-four 1.216 % sits 0.1 of its width away.

**FRICTION.** Kingston **−0.0124 ± 0.0024** vs:
- Pittsburgh push **+0.0005 ± 0.0013** (4.7);
- Pittsburgh hold **+0.0014 ± 0.0015** (4.9);
- Marrakesh **−0.0016 ± 0.0021** (3.4);
- run 121 B30_30 **−0.0022 ± 0.0031** (2.6).

**Independent witnesses.** 4 firings (8 jobs) / 3 chips / 1 day. The −1.24 % itself is 1 job.

## Q13. The halfway column, and its distance from the OFF-ON line

**Claims.**
- 7_PUBLIC Open list: "the halfway state".
- Paper: "on ibm_pittsburgh the halfway start sits 4 widths off that line (+0.34 against +1.03 %)"; "the chip-to-chip halfway start ... not accounted for".

**Positions.** OWN level minus OWN bookkeeping. The line is (OFF + ON)/2 (derived; MID's own level is 0.4946 / 0.5040 / 0.5046).

| chip (jobs) | halfway [OWN] | line | offset from line (derived) |
|---|---|---|---|
| Pittsburgh push (3), 13:09-14:27 | +0.0034 ± 0.0014 | +1.025 ± 0.103 % | **−0.685 ± 0.174 %** (−3.9 widths) |
| Marrakesh 141 (1), 17:27 | +0.0117 ± 0.0024 | +1.290 ± 0.175 % | **−0.120 ± 0.297 %** (−0.4) |
| Kingston 141 (1), 17:28 | −0.0006 ± 0.0022 | +0.815 ± 0.184 % | **−0.875 ± 0.287 %** (−3.0) |

**Back-to-back ten pushes on the halfway state** (same jobs): Pittsburgh −0.1138 ± 0.0019; Marrakesh −0.0176 ± 0.0032; Kingston −0.0513 ± 0.0036.

**Lap one.** Pittsburgh's halfway start sits below its line. Marrakesh's sits on its line. Kingston's sits below.

**Lap two.**
- Kingston (17:28) reads a halfway offset like Pittsburgh's (bars touch). Marrakesh (17:27) reads one unlike either (bars apart).
- The back-to-back halfway loss differs 6x between Pittsburgh and Marrakesh (−0.114 against −0.018). Read as a protractor, it gives each chip its own push shortfall; Q18 lays those beside the OFF/ON arms.

**FRICTION.**
- Halfway column: Pittsburgh **+0.0034 ± 0.0014** vs Marrakesh **+0.0117 ± 0.0024** (3.0); Marrakesh vs Kingston **−0.0006 ± 0.0022** (3.8); Pittsburgh vs Kingston (1.5).
- Offset from line: Pittsburgh **−0.685 ± 0.174** vs Marrakesh **−0.120 ± 0.297** (1.6); Marrakesh vs Kingston **−0.875 ± 0.287** (1.8).

**Independent witnesses.** 3 firings (5 jobs) / 3 chips / 1 day. The in-between shot meant to separate own coherence, neighbours and shots talking (runs 131-133) was frozen and not fired.

## Q14. The gap between the two bookkeepings (2.2-2.7 % "at every push count")

**Claims.**
- 7_PUBLIC Status and Finding Two: "The short-time and long-time decay sit 2.2-2.7 % apart at every push count".
- LAWS Law 5: "two rulers, one qubit, one delta".
- Paper Table 8 text: 2.6 / 2.7 / 2.2.

**Positions.** OWN minus OWN: one-exponential book minus each-stretch book, same job, LAID stretches.

**Run 121, one job, per arm.** One-clock residual minus own-stretch residual, derived from `noname_read1.txt`:

| arm | gap |
|---|---|
| N2 | 2.57 % |
| N6 | 2.65 % |
| A30_30 | 2.23 % |
| A10_30 | 2.86 % |
| A90_30 | 2.77 % |
| A30_10 | 1.21 % |
| A30_90 | 0.12 % |
| A30_30f (ends ON) | −2.24 % |
| B30_30 | −0.01 % |
| B30_30f | +0.01 % |

THREE_SEATS, pooled over twelve arms: seat 2 − seat 1 = +0.0106 (pairs), +0.0103 (35 emitters).

The ruler shape in the same job: −1.41 ± 0.19 %, −2.59 ± 0.24 % and −1.85 ± 0.32 % at 10, 30 and 90 us.

**Neighbours on other firings.** None has own-stretch rulers (push, hold, Marrakesh, Kingston). The early-fast decay itself shows on the lone, tail, half-push, sides and turns runs (Q6a).

**Lap one.** One job:
- 2.2-2.7 % for the OFF-start 30/30 laying at 2, 6 and 10 pushes;
- 0.1-2.9 % for the other OFF-start layings;
- −2.2 % when the OFF start gets one more push at the end;
- ±0 for the ON starts.

**Lap two.**
- "At every push count" covers three arms of one laying in one job.
- No later firing exists. No earlier firing carries the second ruler.
- The early-fast decay that makes the gap is visible on five earlier Pittsburgh firings (Q6a). On Marrakesh and Kingston it was never measured.

**FRICTION.** None (one job).

**Independent witnesses.** 1 firing (1 job) / 1 chip.

## Q15. The below-zero depth per push (−0.12 / −0.58 / −0.97 %)

**Claims.**
- 7_PUBLIC Finding Five: "deeper with every push added: −0.12, −0.58, −0.97 %".
- The call: "keeps its slope on a second chip".
- §166: "the none's minus sign".

**Positions.** OWN level minus OWN each-stretch book, LAID 30/30 stretches.

| count | 150 bits (`noname_read1.txt:58,62,26`) | 35 emitters (THREE_SEATS) | 75 pairs |
|---|---|---|---|
| 2 pushes | −0.0012 ± 0.0034 | −0.0006 ± 0.0064 | −0.0011 ± 0.0069 |
| 6 pushes | −0.0058 ± 0.0052 | −0.0096 ± 0.0102 | −0.0112 ± 0.0105 |
| 10 pushes | −0.0097 ± 0.0051 | −0.0100 ± 0.0114 | −0.0108 ± 0.0117 |
| 10 pushes, same train in the witness arm (WA) | -- | −0.0216 ± 0.0102 | −0.0245 ± 0.0107 |

**Slope from 2 to 10 pushes** (derived): −0.106 ± 0.077 % per push. The three arms share rulers in one job, so their widths are not independent.

**Lap one.** One job. The three counts deepen in order. Each count sits within 0.4-1.9 of its own widths of zero.

**Lap two.**
- No second chip, and no second job on this chip, has own-stretch rulers.
- Inside the same job, the WA emitters on the same 10-push train read −2.2 ± 1.0 %. That is twice the core arm's −1.0 % (bars touch).
- 7_TRACE and §174 file the drift with pushes as the shape over-subtraction leaves when the short-time ruler is applied to every stretch.

**FRICTION.** None placeable (bars touch inside the job; no other job).

**Independent witnesses.** 1 firing (1 job) / 1 chip. The called second-chip slope has no witness.

## Q16. The 10-us |1>-stretch arm (+1.7 ± 0.6 %; one arm in ten)

**Claims.**
- 7_PUBLIC Status and Finding Two: "+1.7 ± 0.6 % above the decay bookkeeping ... one arm in ten (7.6 % family-wise)".
- Paper: 7.5 %.

**Positions.** OWN minus OWN each-stretch book; LAID 30-us |0> and 10-us |1> stretches.

**Witnesses, all run 121 (17:41).**
- A30_10: **+0.0170 ± 0.0064** (150 bits); pairs +0.0289 ± 0.0117; 35 emitters +0.0302 ± 0.0107.
- One-clock: +0.0291 ± 0.0024.
- The family of ten: z 2.656 → 7.6 % (Šidák), 7.5 % at z rounded to 2.66 (7_TRACE item 9).
- The |0>-time series: A10_30 / A30_30 / A90_30 = −0.0139 / −0.0097 / −0.0007 (1.5σ end to end).
- The |1>-time series: A30_10 / A30_30 / A30_90 = +0.0170 / −0.0097 / −0.0062.

**Neighbours on other firings.**
- The stopwatch (12:26): emitters ON 20 or 40 us, then parked. They close on their own book: median emitter 0.0648 / 0.1348 against 0.0647 / 0.1347; per-emitter mean +0.0014 ± 0.0029 / +0.0048 ± 0.0040 (`reads_new/park_per_qubit.txt:47-51`).
- The hold run's alternate quarters and tenths (75-us and 30-us |1> stretches): +0.0020 ± 0.0015 and +0.0014 ± 0.0015 on one-clock books.
- No firing other than run 121 has a 10-us |1> stretch.

**Lap one.** One job. **Lap two.** Nothing after it. The shortest |1> stretches on any other firing (20 us, stopwatch) close on their own book.

**FRICTION.** None.

**Independent witnesses.** 1 firing (1 job) / 1 chip.

## Q17. Heating while the qubit idles in |0> (300 us)

**Claims.**
- 7_PUBLIC Status and Finding Two: "+0.02 ± 0.15 % after 300 us in |0>; across the three chips' push jobs −0.43 to +0.26 % per 300 us". 7 sets heating aside on these arms.
- LAWS Law 4.
- Paper control 2.

**Positions.** OWN level after a LAID 300 us in |0>.

| ran | firing | chip, bits | level [OWN] |
|---|---|---|---|
| 10/1 23:09 / 23:10 / 10/2 00:05 | Run 1 (one look after the wait) | Kingston / Phoenix / Pittsburgh, 9 bits | +0.0021 ± 0.0058 / −0.0030 ± 0.0059 / −0.0022 ± 0.0046 |
| 08:47 | run 5 (one look first) | Marrakesh, 9 | −0.0023 ± 0.0027 |
| 09:14 | run 9 (one look first) | Pittsburgh, 9 | +0.0013 ± 0.0033 |
| 09:31-09:59 | jump (one look first; median bit) | Pittsburgh, 147 | +0.0008, +0.0016, +0.0009, +0.0023, +0.0009, +0.0003, +0.0009, +0.0030 |
| 12:07-12:16 | hold, OFF read 9 times through 300 us (median) | Pittsburgh | +0.0013 … +0.0002 |
| 13:09-14:27 | push run | Pittsburgh, 141 | −0.0009 ± 0.0011 / −0.0004 ± 0.0010 / +0.0011 ± 0.0009 → **−0.0001 ± 0.0006** |
| 17:27 | Marrakesh 141 | 143 | **−0.0043 ± 0.0013** |
| 17:28 | Kingston 141 | 147 | **+0.0026 ± 0.0014** |
| 17:41 | run 121 | Pittsburgh, 150 | **+0.0002 ± 0.0015** |

Sources: `all_three_chips.txt:128`; `run5_marrakesh.txt:35`; `run9_pittsburgh.txt:35`; `jump_run.txt:5-12`; `hold_run.txt:31`; `close_push.txt:11`; `rep_*:11`; `noname_read1.txt:10`.

**Lap one.** Every reading sits within ±0.005 of zero. On the push-run design, the three chips' single jobs land at −0.43 %, −0.01 % and +0.26 %.

**Lap two.**
- **Run 121 on the push run.** Same chip, same arm, bars touch.
- **Kingston (17:28) on Marrakesh (17:27).** 20 seconds apart, the same circuit: −0.43 % on one chip and +0.26 % on the other. The bars are apart.
- The earlier, smaller firings (runs 1, 5, 9) have widths of 0.3-0.6 %. They hold every later value inside their bars.

**FRICTION.**
- Marrakesh **−0.0043 ± 0.0013** vs Kingston **+0.0026 ± 0.0014** (3.6).
- Marrakesh vs Pittsburgh push **−0.0001 ± 0.0006** (2.9).
- Kingston vs Pittsburgh push (1.8).

**Independent witnesses.** 11 firings (22 jobs) / 4 chips (Kingston, Phoenix, Pittsburgh, Marrakesh) / 2 days / 3 designs.

## Q18. Leakage and the push's own error (cap 0.26 ± 0.12 % per push; shortfall 1.48 ± 0.14°; the model's 2.96 ± 0.28 %)

**Claims.**
- 7_PUBLIC Finding Two: "Leakage is capped at 0.26 ± 0.12 % per push, against 2.96 ± 0.28 % per push that a leakage-plus-TLS model needs".
- Paper Table 7 text, and controls 3(a)-(f).

**Positions.**
- OWN level shifts after a LAID push count with no time between pushes.
- The model is not a firing: the reviewer's rows, not on disk.

**The same solve on every chip that ran the back-to-back arms** (derived here, `pass_b_arith.txt` §3). The model is o_N + |u_N| = 2 sin²(N e / 2) + (N/2) k.

| chip (jobs), ran | S2 = o2 + abs(u2) | S10 = o10 + abs(u10) | two-parameter solve | bound from ten pushes alone, k ≤ S10/5 | shortfall if k = 0 (10 / 2 pushes) |
|---|---|---|---|---|---|
| Pittsburgh (3), 13:09-14:27 | 0.0039 ± 0.0009 | 0.0461 ± 0.0011 | e **1.476 ± 0.135°**, k **0.256 ± 0.116 %** per push | 0.92 ± 0.02 % | 1.75° / 2.53° |
| Marrakesh (1), 17:27 | 0.0108 ± 0.0019 | 0.0295 ± 0.0019 | **no real solution** (S10 − 5 S2 = −0.0245) | 0.59 ± 0.04 % | 1.40° / 4.21° |
| Kingston (1), 17:28 | 0.0100 ± 0.0022 | 0.0404 ± 0.0023 | **no real solution** (S10 − 5 S2 = −0.0096) | 0.81 ± 0.05 % | 1.63° / 4.05° |

**Other readings of the same error.**
- The halfway loss predicted from 1.48° (Pittsburgh): 0.0258 ± 0.0024 for 2 X and 0.128 ± 0.012 for 10 X. Measured: 0.0262 ± 0.0019 and 0.1138 ± 0.0019 (§149).
- The turns run (12:05): each extra whole turn drops the in-between start, 0.497 → 0.465 → 0.441.
- §139's "~1.7 deg short" is the k = 0 reading (1.75°).

**The halfway arm as a protractor, on every chip.** The same jobs' back-to-back pushes on the halfway state, with level change = sin(N e)/2, the model §149 used (derived here, `pass_b_arith.txt` §9). [OWN level, LAID push count]

| chip (jobs) | halfway, 2 X | e from 2 X | halfway, 10 X | e from 10 X |
|---|---|---|---|---|
| Pittsburgh (3) | −0.0262 ± 0.0019 | 1.502 ± 0.109° | −0.1138 ± 0.0019 | **1.316 ± 0.022°** |
| Marrakesh (1) | +0.0017 ± 0.0030 | −0.097 ± 0.172° | −0.0176 ± 0.0032 | **0.202 ± 0.037°** |
| Kingston (1) | −0.0190 ± 0.0036 | 1.089 ± 0.206° | −0.0513 ± 0.0036 | **0.589 ± 0.041°** |

If each chip's shortfall is the one its own 10-X halfway arm reads, the ten-push OFF/ON mirror leaves k = 0.578 ± 0.038 % per push on Marrakesh and 0.702 ± 0.046 % on Kingston.

**Where a third level would land** [OWN shot positions]:
- Pittsburgh push and hold:
  - halfway band +0.09 % (OFF spread; +0.14 % on bits more than 8 widths apart) and hold −0.00 % / +0.13 %;
  - across the line −0.0001 ± 0.0005 / +0.0001 ± 0.0006;
  - off both clouds +0.0011 ± 0.0003 / +0.0013 ± 0.0004.
- Marrakesh:
  - halfway band +0.0004 / +0.0007 / +0.0010;
  - off both −0.0001;
  - across +0.0022 to +0.0052 in every arm (no widths printed).
- Kingston:
  - halfway band +0.0034 / +0.0032 / +0.0050;
  - off both ~0;
  - across +0.0007 to +0.0031.
- Run 121:
  - halfway band −0.17 to −0.01 %;
  - off both +0.07 to +0.25 % in pushed arms;
  - flip identity −0.0006 ± 0.0043 (OFF) / −0.0007 ± 0.0040 (ON).
- The leak+TLS model's need: 2.958 ± 0.279 % per push, TLS 0.660 ± 0.076, correlation +0.97, χ² 0.01 on 1 dof. Re-fitted on 10/3 from the ledger's two rows; the rows themselves cannot be regenerated (`reads_new/leak_tls_fit.txt`).

**Lap one.**
- Pittsburgh's OFF/ON arms solve to 1.48° and 0.26 % per push. Its halfway arm reads 1.32° (10 X) and 1.50° (2 X).
- Marrakesh's and Kingston's single jobs do not solve: their two-push sums are larger than a fifth of their ten-push sums. The loosest bound from the ten-push arms alone is 0.59 % (Marrakesh), 0.81 % (Kingston) and 0.92 % (Pittsburgh) per push.
- Their halfway arms read shortfalls of 0.20° (Marrakesh) and 0.59° (Kingston) over ten pushes.

**Lap two.**
- **Kingston and Marrakesh on Pittsburgh.** On their arms, the two-number model of the push error that produced the cap does not close.
  - Their halfway protractors read a shortfall 2-6x smaller than Pittsburgh's.
  - With that shortfall, their ten-push mirrors leave 0.58 % and 0.70 % per push of count-growing error. That is 2-3x Pittsburgh's 0.26 ± 0.12.
  - Every one of these sits under the model's 2.96 %.
- **Inside Pittsburgh.** The halfway protractor at 10 X (1.316 ± 0.022°) and the OFF/ON solve (1.476 ± 0.135°) have bars that do not touch, by a hair. §149's own line reads the same pair as "1.2 widths" (0.128 ± 0.012 predicted against 0.114 ± 0.002 measured).
- **Run 121 on the push run.** Its flip identity and halfway band read ~0 for the anchor laying. The halfway band reads flat on all four firings.

**FRICTION.**
- The solve exists on Pittsburgh (S10 − 5 S2 = **+0.0266**) and not on Marrakesh (**−0.0245**) or Kingston (**−0.0096**). This is a model's root, not a width comparison.
- Shortfall from the 10-X halfway arm: Pittsburgh **1.316 ± 0.022°** vs Marrakesh **0.202 ± 0.037°** (26 combined widths) and vs Kingston **0.589 ± 0.041°** (15); Marrakesh vs Kingston (7.0).
- Within each chip, 10 X vs 2 X halfway shortfall:
  - Pittsburgh **1.316 ± 0.022 vs 1.502 ± 0.109°** (1.7);
  - Marrakesh **0.202 ± 0.037 vs −0.097 ± 0.172°** (1.7);
  - Kingston **0.589 ± 0.041 vs 1.089 ± 0.206°** (2.4).
- Pittsburgh: halfway 10 X **1.316 ± 0.022°** vs OFF/ON solve **1.476 ± 0.135°** (1.2).
- Halfway band, Kingston **+0.0034** vs Marrakesh **+0.0004** (no widths printed).

**Independent witnesses.** The cap: 3 firings (5 jobs) / 3 chips / 1 day. The 2.96 %: 1 model, not on disk.

## Q19. Shots talking: carry-over between shots, and placed against arisen

**Claims.**
- LAWS Law 3: "On Rigetti it survives the reset and carries into the next shot; on IBM, shots don't talk (−0.002 ± 0.002)".
- LAWS Law 4: "what the reset erases is what was placed (0.067 %); what arose on its own stays (+23 points at 20 us, gone by 500)".
- Paper control 4.

**Positions.** OWN level of shot n+1 against shot n's ending, at a LAID gap between shots.

| record | gap [LAID] | reading [OWN] | width |
|---|---|---|---|
| Rigetti q90, 9/26 | -- | a failure never follows a failure: 0 of 128 (8.6 expected) | -- |
| Rigetti q90 chip-wide, 9/28 | -- | the 9/26 rule not there (1 series against ~5 by chance) | -- |
| Rigetti q0, 9/28 (§18, §36d) | task shots | reset clears rung 1, sometimes leaves rung 2, which sets the next start: P 0.001; 64 against 88 (P 0.002). The rung-2 leftover is a deficit at lag 1 (25 against 42.7, p 0.005) | p only |
| Marrakesh echo, 9/28 12:27Z | 20 / 50 / 100 / 250 / 500 / 1000 / 2000 us | placed 1: 0.067 % at 20 us. Arisen 1: **+22.97 / +16.62 / +6.71 / +1.66 / −0.57 / +0.54 / −0.12 pp**; τ 63.8 us (90 % band 41.8-85.0) | shuffle p < 0.003 |
| same record, other readers | 20 us | LOOK1: 43.5 % against 10.9 % expected. LOOK2: +17 pts (Marrakesh/Kingston), +7 Fez. First pass ~19.7 % against 1-2 % | -- |
| Kingston parallax, 9/28 12:34Z | 20 us / 1000 us / default ×2 | +11.07 pp / −0.29 pp / −0.20 pp (p 0.053) and +0.44 pp (p 0.003) | p only |
| Fez held clocks (§21) | default | phase memory r 0.18 next shot, 0.05 at 100 shots (phase, not population) | -- |
| Kingston Runs 1-3, 10/1-10/2 | 500 us | carry corr OFF 0.0092 ± 0.0089 / 0.0019 ± 0.0084 / −0.0072 ± 0.0065; ON −0.0002 ± 0.0098 / −0.0046 ± 0.0093 / −0.0020 ± 0.0073 | shot |
| Pittsburgh push (and hold), 10/2 | 500 us | next shot after an ON ending, OFF spread arm: **−0.002 ± 0.002** (3 jobs); lags 2 and 5 the same | shot |
| Marrakesh 141 | 500 us | lean +0.0108 × share ending ON 0.39 = **+0.004** of +0.027 | no width |
| Kingston 141 | 500 us | +0.0027 × 0.40 = **at most +0.0011** (ON left alone: +0.0136 × 0.30 = +0.0041) | no width |

**Lap one.**
- Rigetti shows a carry through rung 2.
- The 9/28 IBM echo shows the arisen 1 carrying +23 pp at 20 us and fading by 250-500 us; the placed 1 shows nothing.
- Kingston's parallax carries half that.
- At 500 us, every IBM run on 10/1-10/2 reads near zero.

**Lap two.**
- The 10/2 500-us IBM witnesses sit at the gap where the 9/28 echo had already faded to noise (−0.57 pp at 500 us). They read the same thing at the same gap; they do not test the 20-us carry.
- The two 9/28 Kingston default-gap jobs disagree in sign (+0.44 pp, p 0.003, against −0.20 pp, p 0.053). They print no widths.

**FRICTION.** None placeable with widths. Unplaced (no widths):
- Marrakesh +22.97 pp against Kingston +11.07 pp at 20 us;
- the Kingston default-gap pair +0.44 against −0.20 pp;
- LOOK1 / LOOK2 / pre-measurement readers of one Marrakesh record: +32.6 / +17 / ~+18 / +22.97 pp.

**Independent witnesses.** IBM: 7 firings / 4 chips / 3 days. Rigetti: 2 records / 1 chip.

---

# D. THE PARK

## Q20. The park: a qubit's clock runs only while it is in |1>

**Claims.**
- 7_PUBLIC Finding Six: "on the mean over qubits, three ways of parking close to each qubit's own decay bookkeeping within 0.002 (+0.0017 ± 0.0013, +0.0020 ± 0.0015, +0.0014 ± 0.0015; single qubits scatter about ± 0.02 ...), and an emitter parked after 20 / 40 us reads 0.0648 / 0.1348 against 0.0647 / 0.1346".
- 7's closed list: "the park ... three rulers".
- LAWS Law 4: "per-qubit bookkeeping closes to 0.002 across three parking schemes".
- Paper §3.2.

**Positions.** OWN level minus OWN book (relaxation only during |1>), LAID intervals.

| ran | firing | arm | per-qubit mean [OWN] | median qubit | share within 0.002 |
|---|---|---|---|---|---|
| 12:07 / 12:11 / 12:15 | hold 71-73 | once (2 × 150 us) | +0.0008 ± 0.0022 / +0.0021 ± 0.0022 / +0.0022 ± 0.0022 → **+0.0017 ± 0.0013** | +0.0065 / +0.0054 / +0.0086 | 4-7 % |
| same | hold | quarters (4 × 75) | −0.0002 ± 0.0027 / +0.0040 ± 0.0029 / +0.0022 ± 0.0022 → **+0.0020 ± 0.0015** | −0.0007 / −0.0004 / +0.0058 | 4-8 % |
| same | hold | tenths (10 × 30) | +0.0022 ± 0.0027 / +0.0001 ± 0.0023 / +0.0019 ± 0.0026 → **+0.0014 ± 0.0015** | +0.0003 / +0.0011 / −0.0032 | 4-7 % |
| 12:26 | stopwatch 81 | emitter ON 20 / 40 us, then parked | +0.0014 ± 0.0029 / +0.0048 ± 0.0040 (yardstick B1); +0.0005 ± 0.0026 / +0.0030 ± 0.0041 (A3); median 0.0648 / 0.1348 against 0.0647 / 0.1347 | -- | 12 % / 0 % |

The per-qubit quartiles in the hold run are about [−0.025, +0.020] (`reads_new/park_per_qubit.txt:19-41`).

**The tenths arm on every chip.** The tenths laying is the same circuit as the crossing's |1> column (Q12):

| witness | value |
|---|---|
| Pittsburgh push (13:09-14:27) | +0.0005 ± 0.0013 |
| Marrakesh (17:27) | −0.0016 ± 0.0021 |
| Kingston (17:28) | **−0.0124 ± 0.0024** |
| Pittsburgh run 121 B30_30 (17:41) | −0.0022 ± 0.0031 |

**Reading |0> nine times through 300 us** (hold, median): +0.0013, +0.0002, +0.0009, +0.0014, −0.0001, +0.0014, +0.0005, +0.0005, +0.0010, +0.0002.

**Lap one.**
- Hold run (12:07): three ways of parking, each closing within ±0.002 on the mean over qubits.
- Stopwatch (12:26): two parked emitters closing within 0.005.
- Push run (13:09): the tenths laying closes again.
- Marrakesh closes.
- Kingston (17:28) does not: −1.24 %.

**Lap two.**
- **Kingston's run 141 on the hold run's tenths arm.** The same circuit, on the third chip, sits 1.38 % away, with bars apart. On that chip the |1> column and the park's tenths laying are one number, and it is the one 7 lists as open.
- **The 10/3 per-qubit re-read on the LAWS line.** About 5 % of single qubits sit within 0.002. The "0.002" is a mean over qubits; the per-qubit scatter is ±0.02. The LAWS draft (13:06) still says "per-qubit bookkeeping closes to 0.002"; the re-read came at 13:28.
- **The stopwatch on the hold run.** A second design (emitter parked once, 20 or 40 us) closes within its widths on its own book.

**FRICTION.** Tenths / |1> column: Kingston **−0.0124 ± 0.0024** vs Pittsburgh hold **+0.0014 ± 0.0015** (4.9) and push **+0.0005 ± 0.0013** (4.7). The full list is in Q12.

**Independent witnesses.** 3 firings on Pittsburgh (hold 3 jobs, stopwatch 1, plus the push run for tenths) + Marrakesh and Kingston for tenths only / 3 chips / 1 day / 2 designs. "Once" and "quarters" stand on 1 firing (3 jobs) / 1 chip.

---

# E. THE SPECTATORS

## Q21. A free-running spectator's kept coherence (0.921 / 0.826 / 0.760)

**Claims.**
- 7_PUBLIC Finding Three: "0.921 ± 0.004, 0.826 ± 0.005, 0.760 ± 0.006 (11/12, 10/12, 9/12) through 3 looks, 9 looks and 30 us".
- The call: "27 looks leave 0.750, and 81 leave 0.667".
- LAWS Law 2.
- Paper §3.3.
- RESIDUAL_LEDGER: +1.06 / −1.49 / +1.82 widths.

**Positions.** WITNESS hand length over its own no-window length; LAID 30 us, or 3 / 9 readouts on far qubits.

| ran | job | 3 looks | 9 looks | 30 us LAID |
|---|---|---|---|---|
| 14:25:04 | 101 | 0.9219 ± 0.0072 | 0.8307 ± 0.0086 | 0.7585 ± 0.0084 |
| 14:26:42 | 102 | 0.9225 ± 0.0067 | 0.8166 ± 0.0100 | 0.7744 ± 0.0103 |
| 14:28:33 | 103 | 0.9184 ± 0.0067 | 0.8295 ± 0.0082 | 0.7484 ± 0.0107 |
| all | 101-103 | **0.9209 ± 0.0040** | **0.8256 ± 0.0052** | **0.7604 ± 0.0057** |

**Neighbours (different normalisation, different design).**
- The stopwatch (12:26): absolute hand length after a 60-us window, 0.469 with the emitter OFF and 0.422 / 0.398 / 0.412 with it ON for 20 / 40 / 60 us; far clocks 0.339 → 0.30.
- Run 121 (17:41): frame-held hands keep 0.1603 ± 0.0070 / 0.1625 ± 0.0073 after 300 us.
- Fez q144 (9/2x): hand 0.94-0.96 with 0 / 1 / 77 others active (§31).
- Rigetti: contrast fade 0.092 → 0.123 per us with neighbours lit (§31).

**Lap one.** Three jobs within 3.5 minutes. The 3-look values agree; the 9-look values touch; the 30-us values spread 0.748-0.774.

**Lap two.**
- No later firing reads a free spectator through looks at other qubits. Run 121's spectators are frame-held and pulsed: a different instrument.
- The called 27- and 81-look points have no witness.

**FRICTION.** 30 us: job 102 **0.7744 ± 0.0103** vs job 103 **0.7484 ± 0.0107** (1.75 combined widths).

**Independent witnesses.** 1 firing (3 jobs) / 1 chip / 1 day / 1 design.

## Q22. The spectator's free precession (3.144 ± 0.076 deg/us)

**Claims.**
- 7_PUBLIC Finding Three: "the spectator's free precession turns 3.144 ± 0.076 degrees per microsecond" against pi.
- RESIDUAL_LEDGER: +0.03 widths.

**Positions.** WITNESS phase, in the drive frame with emitters in |1>, per LAID us over the first 30 us.

| job (ran) | deg/us [WITNESS per LAID] |
|---|---|
| 101 (14:25) | 3.0349 ± 0.1459 |
| 102 (14:26) | 3.0581 ± 0.1318 |
| 103 (14:28) | **3.3403 ± 0.1154** |
| all | **3.1444 ± 0.0760** (= 8.73 ± 0.21 kHz) |

Source: `close_looktime.txt:11`.

**Neighbours.**
- The stopwatch's turn, measured against its own emitter-OFF arm (the coupling part only): 4.5 kHz = 1.62 deg/us (Q23).
- Fez q144 free: 28.2-28.8 kHz (10.2-10.4 deg/us); with q143 in |1>: 21.9 kHz.

**Lap one.** One run: 3.03 (14:25) → 3.06 (14:26) → 3.34 (14:28) deg/us.

**Lap two.**
- Job 103 sits 0.28-0.31 above jobs 101-102, within 3.5 minutes. The pi match (3.1444) is the mean of a run whose last job sits apart from its first two.
- No later firing re-reads this frame rate. The stopwatch (earlier) reads only the coupling part.

**FRICTION.**
- Job 103 **3.3403 ± 0.1154** vs job 101 **3.0349 ± 0.1459** (1.6).
- Job 103 vs job 102 **3.0581 ± 0.1318** (1.6).

**Independent witnesses.** 1 firing (3 jobs) / 1 chip.

## Q23. The spectator's coupling to its emitter's |1> time (16.9 deg per 30-us stretch)

**Claims.**
- 7_PUBLIC Finding Four: "The spectator turns 16.9 degrees per 30-us |1> stretch", against the golden spiral's 17.03.
- §159: sin²(0.563 deg/us × 30 us / 2) = 2.16 %.
- Paper §3.3.

**Positions.** WITNESS phase per LAID us of emitter-ON time, on the same 39 emitter / 86 spectator roles (same seed) on Pittsburgh.

| ran | firing | reading [WITNESS] | per 30 us of emitter-ON (derived) |
|---|---|---|---|
| 12:26 | stopwatch 81 (68 readable spectators, own sign +) | +33.9 / +28.1 / +23.9 deg per successive 20 us [quartiles 27-46 / 16-39 / 17-32]; rate from the 40-us arm 4.5 kHz [3.4, 5.2] | **48.6 deg [36.7, 56.2]**; first 20 us → 50.8 |
| 17:41 | run 121 (75 pairs, frame-held, fitted with the emitter's own fading) | median abs(theta) **16.9023 ± 1.8085** deg per stretch (0.563 deg/us = 1.565 kHz) | 16.9 |
| same job, THREE_SEATS | raw half-difference, abs(hd)/5 | **8.238 ± 0.481** deg per LAID ON stretch (ceiling 18) | -- |

**The instrument's own walls.**
- Run 121's fit grid stops at ±0.6 rad = **34.4 deg per stretch** (1.15 deg/us, 3.18 kHz; `readnoname.py` TH). The half-difference folds at ±90 deg (abs(hd)/5 ≤ 18).
- 4 pairs sit on the grid edge.
- 53 of 75 per-pair fits jump more than 10 deg in over a third of resamples.

**Lap one.** At 12:26, the free stopwatch witnesses turn 1.6-1.7 deg per us of emitter-ON. At 17:41, the same roles, frame-held, fit 0.56 deg/us.

**Lap two.**
- **Run 121 on the stopwatch.** It reads a third of the stopwatch's rate. The stopwatch's rate (48.6 deg per 30 us) lies above run 121's fit ceiling (34.4 deg per stretch) and above its half-difference's fold.
- **THREE_SEATS on the reader's 16.9.** The raw half-difference per laid stretch is 8.24 ± 0.48. The reader's model at 16.9 books 11.70 per stretch with chip-typical fading and 16.90 with no fading.
- The 16.9 that 7 lays beside 17.03 is the reader's median over fitted pairs. Two other readings on the same roles sit at 8.2 and ~49.

**FRICTION.**
- Stopwatch **48.6 deg per 30 us** (lower quartile 36.7 as its bar) vs run 121 **16.90 ± 1.81** (2.6 combined widths).
- Within run 121: **16.90 ± 1.81** (fit) vs **8.24 ± 0.48** (raw half-difference per laid stretch) (4.6). These are two rulers on one job.

**Independent witnesses.** 2 firings (2 jobs) / 1 chip / 1 day / 2 designs.

## Q24. The spectator's own leftover (+0.6 deg)

**Claims.**
- LAWS Plus None: "a spectator qubit, after everything we know how to cancel is cancelled, keeps a leftover of +0.6 degrees".
- §156: the 0.6 family (hat room).

**Positions.** WITNESS half-sum angle, frame-held.

| reading | value |
|---|---|
| run 121, the reader | **+0.5963 ± 4.5115 deg** |
| run 121, THREE_SEATS | +0.596 ± 4.384 |

**Neighbours.**
- The stopwatch triangle (12:26 + §135): driven by the emitter's own fading, the witness closes at −1.4 ± 4.8 deg.
- The stopwatch's far clocks turn 20.2 / 18.7 / 9.7 deg against shot widths of 15.7 / 16.6 / 16.5.
- Look-time: own-minus-typical misfit +0.0020 ± 0.0032 deg.
- §145's statevector check: the frame drift moves the hand by 0.00 deg.

**Lap one.** The stopwatch closes at −1.4 ± 4.8 deg (12:26). Run 121's leftover reads +0.60 ± 4.51 deg (17:41).

**Lap two.**
- Run 121's value sits 0.13 of its own width from zero. Its width (4.5 deg) is 7.5 times the value.
- The stopwatch's closure (−1.4 ± 4.8) touches it. No firing reads this leftover at a width that could hold 0.6.

**FRICTION.** None.

**Independent witnesses.** 1 firing (1 job) / 1 chip.

## Q25. Does a spectator follow its own emitter's clock, or the laid clock?

**Claims.**
- 7_PUBLIC Open list: "whether a clock follows its own emitter".
- TRIANGLE IV ("STANDS: the bit's own clock and its neighbour's count of it agree; OUR clock is the odd one out").
- Paper §3.3.

**Positions.**
- WITNESS model residuals with OWN fading.
- Against the LAID time.
- Against the chip-typical OWN fading.

| ran | firing | own fading | laid time | own minus typical |
|---|---|---|---|---|
| 12:26 | stopwatch triangle (`stopwatch_triangle.json`, 66 spectators; the producing script is not in the release) | residual −1.4 ± 4.8 deg, hand 1.02 ± 0.035, kick 0 | hand 0.90 ± 0.03, kick −3.2 deg per X | -- |
| 14:25-14:28 | look-time (3 jobs) | misfit 12.8046 ± 1.0979 deg | -- | +0.0020 ± 0.0032 deg |
| 17:41 | run 121 (1 job) | misfit 0.0751 ± 0.0071 | -- | +0.0004 ± 0.0006 |

**THREE_SEATS on run 121.** Two witnesses of the same emitter, on the same shots, differ by 5.07 ± 0.48 deg per stretch (one pair's shot width 3.90). Example, emitter 70: 3.49 against 17.62.

**Lap one.** The stopwatch separates own fading from laid time. Look-time and run 121 cannot separate own fading from chip-typical fading.

**Lap two.**
- Run 121 is the third reading. It splits own from typical by 0.0004 ± 0.0006 and adds a within-emitter spread larger than the shot width.
- The stopwatch's split (own against laid) has not been repeated on any later job.

**FRICTION.** None placeable. The own-vs-laid contrast and the own-vs-typical contrast are different questions.

**Independent witnesses.** 3 firings (5 jobs) / 1 chip. The own-vs-laid split is 1 job.

## Q26. Does an inside clock see the laid time?

**Claims.**
- 7_PUBLIC closed list: "the inside never sees the outside's laid time".
- LAWS Plus None: "the inside never reads the outside's laid time -- a spectator's clock is blind to how long we waited".
- TRIANGLE W1 and VIII.

**Positions.** A WITNESS reading against a LAID duration.

| record | instrument | LAID duration | inside reading |
|---|---|---|---|
| Fez tile 8, 9/2x (§33, §40 34g run; 26 batches) | the buzz: a readout-line tone, which no qubit carries (§33) | Ramsey waits 0-20 us | 0.1-1.4 ns whatever the wait; shared term −0.5 ns; per-run term 1000.0 ns per us (the laid number, 1:1). Calibrated on GW150914 at 96.9 / 3.1 |
| Pittsburgh 12:26, stopwatch | spectator qubits | emitter ON 40 / 60 us | 35.6 / 48.3 us (median; no width) |
| Pittsburgh 14:25-14:28, look-time | spectator qubits | delays 0-120 us; readout blocks | phase 3.1444 ± 0.0760 deg per laid us; one readout 2.3699 ± 0.0318 us against the laid 2.180 |
| Pittsburgh 17:41, run 121 | frame-held spectator qubits | 5 × 30.016 us ON | t_W 14.63 ± 0.85 us per stretch, at the ensemble coupling |

**Lap one.** The buzz reads none of the laid waits. Spectator qubits read laid time at 0.8-0.9x (stopwatch), 1.09x of a readout (look-time) and ~0.49x (run 121's normalisation).

**Lap two.**
- Every later spectator-qubit firing on Pittsburgh registers laid durations, each at its own scale.
- The "never sees" rests on the buzz. The buzz lives on one tile of two chips, and §33 says the qubits do not carry it.
- The LAWS sentence names "a spectator's clock". The spectator qubits on record read the waits.

**FRICTION.** Stated in numbers, instruments named:
- the buzz: **0 of 0-20 us** (per-run term exactly the laid number; shared −0.5 ns);
- spectator qubits: **3.1444 ± 0.0760 deg per laid us**;
- spectator qubits: **2.37 ± 0.03 us per 2.18-us laid readout**;
- spectator qubits: **35.6 / 48.3 us per 40 / 60 laid us** (no width).

**Independent witnesses.** The buzz: 1 instrument (26 batches) / 2 chips' tile 8. Spectator qubits: 3 firings / 1 chip.

## Q27. What moves a spectator: the state of what is wired to it, not the head count

**Claims.**
- Paper §3.3 ("What moves a spectator").
- TRIANGLE W4.

**Positions.** WITNESS frequency or phase, against a LAID set of neighbour states.

**Fez, 9/24-9/28 (§31, 778 within-job tests, Holm-corrected).**
- q144 runs at 28.2-28.8 kHz with 0, 1 or 77 others active, contrast 0.94-0.96.
- With q143 in |1>: 21.9 kHz (vendor table 21.7). With q143 half: 25.1 (table 25.1).
- q113: −5.1 kHz (table −5.1). q138: −20 deg (table −19).
- 34 seats: 0 ± 10 deg between big and small groups.
- Leftovers:
  - q144 −33 deg beyond the table in the yeast hour (seats with no neighbour change moved up to 40 deg);
  - q27 −4.6 kHz across 6 minutes;
  - q143's second-tone share 0.27 ↔ 0.5 within 13 s.

**Rigetti, 9/28.**
- q9 is flat with 0 / 11 / 53 lit non-neighbours, and with 1 / 106 read at the end.
- Checkerboard: median fade 0.092 → 0.123 per us (43 of 54 shorter); q37 0.8-0.97 → 0.17; q30 0.66 → 0.35.

**Pittsburgh, 10/2.**
- Look-time spectators wired / not wired to a looked-at bit: 2.2373 / 2.4353 us (3 looks); 2.3244 / 2.3652 (9 looks).
- Stopwatch far clocks turn inside their own widths.

**Lap one.** Fez (9/24-28): the head count moves nothing; a lit wired neighbour moves q144 by ~6.6 kHz, as the vendor's table says. Rigetti (9/28): lit neighbours shorten 43 of 54 clocks. Pittsburgh (10/2): far clocks hold still while emitters switch.

**Lap two.**
- **Pittsburgh's look-time (10/2) on Fez's head-count null.** Wired and not-wired spectators part by 0.20 us in the 3-look block and touch in the 9-look block.
- **Fez on itself.** Its seats match the vendor's table to 0.0-0.2 kHz in one hour. The same q144 sits 33 deg beyond the table in another hour (the yeast hour).

**FRICTION.**
- Wired vs not wired, 3 looks: **2.2373 ± 0.0841 vs 2.4353 ± 0.0965** (listed in Q2).
- The q144 table match against its −33 deg hour: no widths.

**Independent witnesses.** Fez: many jobs over 9/24-28. Rigetti: 1 night. Pittsburgh: 2 firings.

## Q28. Being watched, and the emitter's own decay

**Claims.**
- Paper §3.3: "Being watched does not change the emitter".
- 7's closed list: "the order of looking sets the heat" (Rigetti rooms).

**Positions.** OWN level of the emitter, against a LAID neighbour state.

| ran | firing | reading [OWN] |
|---|---|---|
| 9/28 night | Rigetti rooms (q0 falling from rung 2; outside fall time) | back to back 24.2 → 21.0 → 20.4 us; alternating alone **26.6 (26.0-27.6)** against full **31.2 (30.0-32.4)** |
| 9/28 night | Rigetti q0 start heat (rooms rotated, with the readout cross-check of §13) | alone 3.85 ± 0.36 %, half 3.81 ± 0.36, full **4.96 ± 0.38**; alone 3.83 ± 0.36, edge 3.58 ± 0.35, middle trio **2.23 ± 0.35** |
| 9/29 (§21) | q0's own flip error, task to task | 5.3-9.9 %; rooms pooled 7.0 / 7.5 / 7.2 / 7.2 % |
| 9/2x (§21) | IBM, end-of-shot readout | 78 qubits read against 2-7: no change |
| 10/2 12:26 | stopwatch (emitter ON 60 us) | neighbours OFF 0.7896, ON 0.7900, as clocks 0.7942 / 0.7824; bit by bit **−0.0029 ± 0.0086** (clocks − OFF), +0.0040 ± 0.0136 (ON − OFF) |
| 10/2 17:41 | run 121 (same 10-push train, same emitters) | neighbours pushed alike (A30_30) **0.3696 ± 0.0067** against neighbours frame-held as witnesses (WA) **0.3559 ± 0.0042**; ON start 0.6858 ± 0.0060 against 0.6819 ± 0.0045; retest r +0.787 / +0.779 |

**Lap one.** On Rigetti, the room moves q0's start heat by ±1-1.6 % and its fall time by +4.6 us. On IBM the stopwatch shows no change at 60 us, but run 121 shows a 1.4-point lower end level for OFF-started emitters whose neighbours are held as witnesses.

**Lap two.**
- **Run 121 on the stopwatch.** The bars of the two "watched minus not" readings touch (−0.0029 ± 0.0086 against −0.0137 ± 0.0079). Run 121's own pair, inside one job, has bars apart for the OFF start.
- **§21 (9/29) on the Rigetti rooms (9/28).** q0's own flicker between tasks (5.3-9.9 %) is larger than any room difference. TRIANGLE VII keeps "room or flicker" as its open seat.

**FRICTION.**
- Run 121 A30_30 **0.3696 ± 0.0067** vs WA **0.3559 ± 0.0042** (1.7).
- Rigetti alternating alone **26.6 (26.0-27.6)** vs full **31.2 (30.0-32.4) us**.
- Rigetti start heat: alone **3.85 ± 0.36** vs full **4.96 ± 0.38** (2.1); alone **3.83 ± 0.36** vs middle **2.23 ± 0.35** (3.2).

**Independent witnesses.** IBM: 2 firings / 1 chip / 1 day. Rigetti: ~4 task sets / 1 chip / 1 night.

## Q29. Rigetti: a neighbour in |2> pulls the spectator; fall time inside and outside

**Claims.** Paper abstract and §3.3: "a Rigetti neighbour in |2> pulls a spectator by −62.1 ± 0.6 deg/us"; the inside and outside fall times.

**Positions.**
- WITNESS: q9's pull and its inside fall time.
- OWN: q0's own readout fall time.
- LAID: the waits.

| 9/28 firing | pull on q9 [WITNESS] | inside fall time, us [WITNESS] | outside fall time, us [OWN] |
|---|---|---|---|
| §7 witness ($20.70) | −62 deg/us (q1 −27; q10 ~0; rung 1 ~0.3) | ~20 (§7) | -- |
| "the first run", as §10 cites it (likely the §7 task set, read another way) | -- | q9 ~8, q1 ~2 | 28 |
| §10 whole chip (106 clocks) | −60 | **14.8 ± 5.3** (q5 6.2 ± 4.5) | **31.2 (30.0-32.6)** |
| §11 headline (q9 alone) | **−62.1 ± 0.6**; spread 16 kHz | 20.9 (16.5-29.5) | 24.2 (Δχ² +0.2 to force it) |
| §12 rooms 0 / 54 / 106 | −62.1 / −62.3 / −59.9 | 21.0 / 16.0 / 23.0 | 24.2 / 21.0 / 20.4 |
| §13 three-body | −60.9 (q10 at 0) / −62.2 (q10 at 1) | -- | -- |

**Lap one.** The pull holds at −60 to −62.3 across five task sets. The inside fall time goes ~8 → ~20 → 14.8 → 20.9 → 16-23. The outside goes 28 → 31.2 → 24.2 → 20.4-24.2 (and 26.6 / 31.2 alternating, Q28).

**Lap two.** The headline and the rooms put inside and outside within each other's ranges. The earlier whole-chip run does not, and §11-§12 do not repeat its gap. q0's own outside fall time moves 20.4-31.2 us across one night's tasks.

**FRICTION.**
- Whole-chip inside **14.8 ± 5.3** vs outside **31.2 (30.0-32.6)** (3.0).
- q0's outside fall time across tasks: **31.2 (30.0-32.6)** (§10) vs **24.2** (§11) / **20.4** (§12) (no widths on the latter).
- Pull, headline **−62.1 ± 0.6** vs full room **−59.9**. No width is printed for the full room; the ledger itself reads it at "~2.5 sigma, maybe".

**Independent witnesses.** ~6 task sets / 1 chip / 1 night / 1 emitter-spectator pair (q0-q9).

---

# F. THE THIRD LEVEL, THE ORDER, THE SILENT BRANCH

## Q30. The third level at the start of a shot: standing, carried, blinking, on two vendors

**Claims.**
- 7's closed list: "the third level's three behaviours on two vendors".
- LAWS Law 3.
- Paper §3.4.

**Positions.** OWN populations at the start of a shot, LAID inter-shot gaps.

**IBM, 9/28 parallax two-look runs** (Marrakesh 08:30Z, Kingston 12:34Z, Fez 12:55Z) and the echo (Marrakesh 12:27Z):
- Off-both-clouds dots on both looks:
  - Marrakesh 134 against 6.5 by chance (told 0) and 100 against 16 (told 1);
  - Kingston 98 against 2 and 109 against 10;
  - Fez ~none (§2; Biblioteca 9/28 19:xx).
- Standing: Marrakesh q14 ~1-3 % at every gap; q24 ~1 % floor plus a carried bump.
- Carried:
  - Kingston q58 1.6 → 6.1 %, q62 2.3 → 9.4 %, q40 0.13 → 1.85 % at 20-us gaps, drained by 1 ms (drain ~150-200 us);
  - Marrakesh q26 4.6 % at 20 us, gone by 250;
  - chip-wide Marrakesh 0.84 % at 20 us over a 0.31 % floor, draining ~72 us (nine fits 24-193 us);
  - own spot off the line: Kingston q58 96 %, Marrakesh q24 92 % (§21);
  - lifetime ~55-80 us.
- Blinking: Marrakesh q60 5-9 % / ~0 minutes apart; q126 the same; q66 13 % in one job.

**Rigetti, 9/28.**
- Baseline q0: 0.03 ± 0.17 % alone, 0.29 ± 0.19 % with the whole chip.
- Standing: median 0.04 %; q24 2.05, q48 1.34, q40 1.26, q33 1.17 %.
- Carried: q63 ~2.5, q78 ~1.9, q40 ~2.0 %, draining within 60 us in all three batches; q61 did not repeat.
- Blinking: q52 2.0 / 2.2 / 8.9 %; q36 8.5 / 9.9 / 18.9 %; q5 1.7 / 5.3 / 1.7 %.
- The blink hour (8 checks): q52 / q36 / q5 did not blink (q52 one blip).
- q62: 6 % → 31-60 % → 3 % inside one task (§18).

**IBM, 10/2 Pittsburgh.**
- "No third place on Pittsburgh: same-shot, they come back at the misread rate and sit where zeros sit" (§135 II).
- Off both clouds +0.0011 ± 0.0003 (push) and +0.0013 ± 0.0004 (hold).
- Marrakesh and Kingston (10/2, run 141): off both ~0.

**Lap one.** 9/28: three behaviours on three IBM chips (Fez ~none) and on Rigetti. 9/28 night: the blink hour finds no blink on the blinkers. 10/2: Pittsburgh (a fourth IBM chip) shows no third place for its lost ones.

**Lap two.**
- **The blink hour (later the same night) on the blink batches.** The three blinkers held steady for an hour (no numbers printed). The earlier blink (q36 8.5 → 18.9 %) is intermittent on the record.
- **10/2 Pittsburgh on 9/28.** The full-chip runs on a fourth chip read off-both at 0.1 % (no seat-level map was made). The paper's IBM third-level job list is still "TO FILL".

**FRICTION.** None placeable (no widths on the seat percentages). Unplaced: q36's 18.9 % batch against the blink hour's steady reads.

**Independent witnesses.** IBM: 4 chips (3 with the third level, Fez ~none, Pittsburgh none) / 9/28 + 10/2. Rigetti: 1 chip / 9/28, 3 batches + 8 checks.

## Q31. The order of looking sets the heat

**Claims.** 7's closed list: "the order of looking sets the heat". (The paper's literature line: textbook, §20.)

**Positions.** OWN heat (stray 1s), against LAID order.

**Witnesses.**
- **April 27, Kingston, Exp A.**
  - Read in turn: the last read runs hottest (forward q3 3.52 %, reversed q0 2.83 %).
  - Read all at once: 0.95-1.34 %.
  - The slot set the counts: 59 = 59, 66 = 66.
- **Exp B, three chips.** q3 hottest on all three (Fez 6.62 %), but q3 is always measured last.
- **9/24 three-box.** System qubits carry 3.5-5 % extra 1s.
- **9/24 Marrakesh cold seats.** q62 2 in 32,768; q134 20 in 83,968. This partly rode a 9/23-24 spell (§18).
- **9/24 dark_floor.** v2 bell first +1.24 ± 0.46 %, bell last −0.13 %; run 1 +0.76 %. dark_link forward −0.76 ± 0.36 %.
- **9/28 IBM echo.** Crowded looks raise stray 1s 0.30 → 0.70 %.
- **9/28 Rigetti rooms.** +1.1 % (full), −1.6 % (middle trio).
- **9/28 rounds 1-9.** The chip moved unpinned measurements late, and the eraser fringe read 0.13 instead of 0.89.

**Lap one.** April (in turn = hot, together = cold) → 9/24 (first = cold, last = hot) → 9/28 (crowded = hotter; full room = hotter, middle trio = colder).

**Lap two.**
- **§20 (9/29) on all of them.** Textbook order effects (Govia 2023, Hothem 2025, Harper).
- **§21 (9/29) on the 9/28 rooms.** q0's task-to-task flicker (5.3-9.9 %) is the rooms' size.
- **§21 on the crowd.** 78 read against 2-7 changes nothing at end-of-shot on IBM.
- No 10/1-10/3 firing was designed to vary the order.

**FRICTION.** Rigetti start heat (Q28). Elsewhere, no widths.

**Independent witnesses.** 6 eras of records / 4 chips + Rigetti / April-September. Not one firing among them was designed for the order (§16).

## Q32. The qutrit three-box silent branch (−0.019)

**Claims.** 7_PUBLIC Finding Five: "A qutrit three-box silent branch read below zero too, −0.019 (one run)".

**Positions.** An OWN readout-corrected probability.

**Witnesses.**
- **Rigetti step 3, 9/25 (Cepheus q0, 35 tasks).**
  - B_not −0.019, A_not +0.014.
  - In the same run: A 0.92, B 1.15, C 0.205 (ideal 1, 1, 0.2).
  - The readout correction assumes 2 outcomes (`NOTHING_SWEEP_sep24_27.md:88,223`; DISCARD_MAP).
- **Neighbour: the IBM 9/24 qubit three-box (4 runs).** The empty box reads "present" at **+0.121 ± 0.031**; the impossible cells +0.21; readout bias explains at most +0.03 (§16C). LOOK_LEDGER: at chance against the full count (331 expected by luck).

**Lap one.**
- 9/24, IBM qubits: the empty box reads +0.121 ± 0.031, above zero.
- 9/25, Rigetti qutrit: B_not reads −0.019 with no width, below zero.

**Lap two.**
- **Rigetti (later) on itself.** The same run's B branch sits 0.15 above its ceiling of 1. The corrected probabilities in that run leave [0, 1] by up to 0.15. B_not sits 0.019 below 0.
- **Rigetti on IBM.** The two vendors' empty branches sit on opposite sides of zero. Nothing later re-reads either.

**FRICTION.** None placeable. B_not carries no width.

**Independent witnesses.** 1 firing (35 tasks) / 1 chip.

---

# THE TABLE

The friction column gives the pairs whose bars do not touch, with gaps in combined widths in brackets. Every pair is computed in `pass_b_arith.txt` §6.

| quantity | used for | independent witnesses | friction (numbers) |
|---|---|---|---|
| Q1 look, LAID 2.18 us | 7 F1 / F3 / F4 / F6; Law 5; paper T2 | 2 reads / 2 chips / 2 days | none |
| Q2 look, WITNESS 2.37 ± 0.03 us | 7 F1, ratios; Law 5; paper T2 | **1 firing (3 jobs) / 1 chip** | job 101 2.4718 ± 0.0512 vs 102 2.2802 ± 0.0464 (2.8); 3 looks 2.4940 ± 0.1124 vs 2.1654 ± 0.1017 (2.2); not wired 2.4353 ± 0.0965 vs wired 2.2373 ± 0.0841 (1.6); 2.3699 ± 0.0318 vs maker 2.180 (no width) |
| Q3 look, OWN 3.5 ± 0.2 us | 7 F1; Law 5; paper T2 | 12 firings + the §135 statement / 5 chips / 2 days. The printed ± 0.2 is **1 ledger statement** | give-back 111 6.53 ± 1.51 vs 112 1.02 ± 1.49; 112 vs 113 at 150 us 1.31 ± 1.58 vs 5.91 ± 1.57, at 270 us 0.73 ± 1.53 vs 6.88 ± 1.87; one look at 150 us 3.56 ± 0.93 (give-back) vs 0.57 ± 0.73 (hold, derived); no-time drop Marrakesh −0.0480 ± 0.0071 vs Kingston −0.0204 ± 0.0053 (3.1) and vs Pittsburgh −0.0272 ± 0.0060; in us 11.0 ± 1.7 vs 5.3 ± 1.4; run 9 7.3 ± 1.6 vs pile-up 3.5 ± 0.2; bite Pittsburgh Run 2 −0.008 ± 0.012 vs run 9 −0.068 ± 0.019, vs Kingston −0.053 ± 0.014, vs Marrakesh −0.079 ± 0.026 |
| Q4 ratios 1.087 / 1.606 / 1.477, the stretch 1.48 | 7 F1 / F4 / F6 (call: 1.5 on every chip) | **1 chip / 1 day**; the WITNESS leg is 1 firing | qubit/witness 1.48 ± 0.09 vs 3.06 ± 0.68 (run 9); vs 2.91 ± 0.79 and 0.31 ± 0.64 (give-back 113 / 112 at 270 us) |
| Q5 the \|1> kept at 300 us, "0.313-0.335" | 7 F3 (1/pi); §159 | Pittsburgh 8 firings / 18 jobs / 1 chip; 4 other chips | push 0.3131 ± 0.0013 vs hold 0.3354 ± 0.0013 (12.1); give-back 0.3190 ± 0.0009 vs hold (10.4); push vs give-back (3.7); hold vs run 121 0.3286 ± 0.0030 (2.1); push vs run 121 (4.7); give-back 111 0.3241 ± 0.0014 vs 113 0.3135 ± 0.0015 (5.2); push 92 0.3101 ± 0.0025 vs give-back 112 0.3195 ± 0.0015 (3.2); Run 2 0.351 ± 0.013 vs run 9 0.2808 ± 0.0144 (3.7); Marrakesh 141 0.1786 ± 0.0019 vs run 5 0.2445 ± 0.0139 |
| Q6 two clocks: 0.756 / 0.775 ± 0.009 / gap clock 0.60 | 7 F3 (3/4, 1/phi), F4 (1.667) | (a) 6 firings / 1 chip; (b) 9 firings / 5 chips. **0.756 = 1 job; 0.60 = 1 job; 0.775 = ledger only** | jump 0.775 ± 0.009 vs Kingston 0.60 ± 0.07 (2.5), Marrakesh 0.6076 ± 0.0822 (2.0), Phoenix 0.68 ± 0.07 (1.4), Pittsburgh run 9 0.658 ± 0.100 (1.2); Kingston 0.60 vs Pittsburgh Run 2 0.83 ± 0.11 (1.8), Boston 0.80 ± 0.11 (1.5); run 121 early/late 0.672 ± 0.025 vs 0.775 ± 0.009 (3.9) |
| Q7 halfway early clock 0.59 | 7 F3 | 5 firings / 1 chip. **The 0.59 = 1 job** | none placeable (no widths; later jobs 0.51-0.76) |
| Q8 decay-time wander | paper L2; 7 Methods | many | it is the spread (maker T1 0.32-4.87x; single bits 0.157-0.164 rms in minutes) |
| Q9 microsecond vs shot clocks +1.88 ± 1.16 | 7 F4 | **1 microsecond firing (9/28 echo) / 1 chip** | none |
| Q10 the 0.62-0.65 band | 7 F3 | 2 firings / 1 chip / 2 days | 9/28 0.433 ± 0.222 vs 10/2 0.025 ± 0.155 / 0.021 ± 0.060 / 0.004 ± 0.125 (cutoff 0.65) |
| Q11 the crossing, start 0 | 7 Status / F2 / F4; Law 4; paper T6 | 5 firings / 9 jobs / 3 chips / 1 day; **off Pittsburgh, 1 job per chip** | push +0.0200 ± 0.0016 vs Marrakesh +0.0274 ± 0.0028 (2.3), Kingston +0.0287 ± 0.0028 (2.7); hold +0.0217 ± 0.0017 vs Kingston (2.1), Marrakesh (1.7); run 121 +0.0126 ± 0.0032 vs push (2.1), hold (2.5), Marrakesh (3.5), Kingston (3.8); hold 71 +0.0190 ± 0.0030 vs 72 +0.0251 ± 0.0029 (1.5); push 91 +0.0174 ± 0.0028 vs hold 72 (1.9); run 121 N2 +0.0245 ± 0.0025 vs A30_30 (2.9); A30_30 +0.0218 ± 0.0072 vs WA +0.0081 ± 0.0058 (1.5) |
| Q12 the \|1> column; Kingston −1.24 | 7 F2, F7 (rung four, neutron); open list | 4 firings / 3 chips. **−1.24 = 1 job** | Kingston −0.0124 ± 0.0024 vs Pittsburgh push +0.0005 ± 0.0013 (4.7), hold +0.0014 ± 0.0015 (4.9), Marrakesh −0.0016 ± 0.0021 (3.4), run 121 B30_30 −0.0022 ± 0.0031 (2.6) |
| Q13 the halfway column / off the line | 7 open list; paper | 3 firings / 3 chips | Pittsburgh +0.0034 ± 0.0014 vs Marrakesh +0.0117 ± 0.0024 (3.0); Marrakesh vs Kingston −0.0006 ± 0.0022 (3.8); Pittsburgh vs Kingston (1.5); offset −0.685 ± 0.174 vs −0.120 ± 0.297 (1.6); −0.120 ± 0.297 vs −0.875 ± 0.287 (1.8) |
| Q14 two bookkeepings 2.2-2.7 % apart | 7 Status / F2; Law 5; paper | **1 firing (1 job) / 1 chip** | none |
| Q15 below-zero depth −0.12 / −0.58 / −0.97 | 7 F5 (call: same slope on a 2nd chip) | **1 firing (1 job) / 1 chip** | none |
| Q16 10-us \|1> arm +1.7 ± 0.6 (7.6 %) | 7 Status / F2; paper | **1 firing (1 job) / 1 chip** | none |
| Q17 idle heating | 7 Status / F2; Law 4; paper | 11 firings / 4 chips / 2 days | Marrakesh −0.0043 ± 0.0013 vs Kingston +0.0026 ± 0.0014 (3.6); Marrakesh vs Pittsburgh push −0.0001 ± 0.0006 (2.9); Kingston vs push (1.8) |
| Q18 leakage cap 0.26 ± 0.12 %, shortfall 1.48°, model 2.96 ± 0.28 % | 7 F2; paper | the cap: 3 firings / 3 chips. **2.96 = 1 model, not on disk** | two-number solve: Pittsburgh S10 − 5 S2 = +0.0266 (root), Marrakesh −0.0245 and Kingston −0.0096 (no root); bounds 0.92 / 0.59 / 0.81 % per push; halfway-arm shortfall (10 X) Pittsburgh 1.316 ± 0.022° vs Marrakesh 0.202 ± 0.037° (26) vs Kingston 0.589 ± 0.041° (15; M vs K 7.0); 10 X vs 2 X on each chip: 1.316 ± 0.022 vs 1.502 ± 0.109 (1.7), 0.202 ± 0.037 vs −0.097 ± 0.172 (1.7), 0.589 ± 0.041 vs 1.089 ± 0.206 (2.4); Pittsburgh halfway 1.316 ± 0.022 vs OFF/ON solve 1.476 ± 0.135 (1.2) |
| Q19 shots talking; placed vs arisen | Law 3, Law 4; paper ctrl 4 | IBM 7 firings / 4 chips / 3 days; Rigetti 2 records | none placeable (+22.97 vs +11.07 pp; +0.44 vs −0.20 pp: no widths) |
| Q20 the park | 7 F6, closed list; Law 4; paper §3.2 | tenths: 4 chips' firings; once / quarters: **1 firing (3 jobs)**; stopwatch 1 job | tenths circuit = the \|1> column: Kingston −0.0124 ± 0.0024 vs Pittsburgh hold +0.0014 ± 0.0015 (4.9), push +0.0005 ± 0.0013 (4.7) |
| Q21 spectator kept 0.921 / 0.826 / 0.760 | 7 F3 (call: 27 looks → 0.750); Law 2 | **1 firing (3 jobs) / 1 chip** | 30 us: job 102 0.7744 ± 0.0103 vs 103 0.7484 ± 0.0107 (1.75) |
| Q22 precession 3.144 ± 0.076 | 7 F3 (pi) | **1 firing (3 jobs) / 1 chip** | job 103 3.3403 ± 0.1154 vs 101 3.0349 ± 0.1459 (1.6) and vs 102 3.0581 ± 0.1318 (1.6) |
| Q23 coupling 16.9 deg / 30 us | 7 F4 (17.03); §159 | 2 firings / 1 chip | stopwatch 48.6 [36.7, 56.2] vs run 121 16.90 ± 1.81 (2.6); in-job 16.90 ± 1.81 vs abs(hd)/5 8.24 ± 0.48 (4.6) |
| Q24 spectator leftover +0.6 deg | LAWS Plus None | **1 firing (1 job)** | none |
| Q25 does a spectator follow its own emitter | 7 open list; paper | 3 firings / 1 chip; own-vs-laid **1 job** | none placeable |
| Q26 the inside never sees the laid time | 7 closed list; LAWS Plus None | buzz: 1 instrument / 2 chips' tile 8; spectators 3 firings | buzz 0 of 0-20 us (per-run 1:1, shared −0.5 ns) vs spectator qubits 3.1444 ± 0.0760 deg per laid us, 2.37 ± 0.03 us per 2.18-us laid readout, 35.6 / 48.3 per 40 / 60 laid us |
| Q27 what moves a spectator | paper §3.3 | Fez many jobs; Rigetti 1 night; Pittsburgh 2 firings | wired vs not wired (see Q2) |
| Q28 being watched and the emitter | paper §3.3; closed list (order) | IBM 2 firings; Rigetti ~4 task sets | run 121 A30_30 0.3696 ± 0.0067 vs WA 0.3559 ± 0.0042 (1.7); Rigetti alone 26.6 (26.0-27.6) vs full 31.2 (30.0-32.4) us; heat alone 3.85 ± 0.36 vs full 4.96 ± 0.38 (2.1); alone 3.83 ± 0.36 vs middle 2.23 ± 0.35 (3.2) |
| Q29 Rigetti pull −62.1 ± 0.6; fall times | paper abstract, §3.3 | ~6 task sets / 1 chip / 1 night | whole-chip inside 14.8 ± 5.3 vs outside 31.2 (30.0-32.6) (3.0); pull −62.1 ± 0.6 vs −59.9 (no width; ledger "~2.5 sigma") |
| Q30 third level, three behaviours, two vendors | 7 closed list; Law 3; paper §3.4 | IBM 4 chips (Fez ~none, Pittsburgh none) / Rigetti 1 chip | none placeable |
| Q31 the order of looking sets the heat | 7 closed list | 6 eras / 4 chips + Rigetti; none designed for it | Rigetti heat (Q28) |
| Q32 qutrit silent branch −0.019 | 7 F5 | **1 firing (35 tasks) / 1 chip** | none placeable (no width) |

**Standing on one witness only** (one firing, or one ledger statement):
- **Q2**: the spectator-timed look, 2.37 ± 0.03.
- **Q3**: the printed 3.5 ± 0.2 (one ledger statement, not reproducible from the release).
- **Q4**: the three ratios and the stretch 1.48. One chip; their witness leg is one firing.
- **Q6**: the 0.756 (one job) and the 0.60 (one job). The 0.775 is a ledger line with no read file behind it.
- **Q7**: the 0.59 (one job).
- **Q9**: the microsecond leg, the 9/28 echo.
- **Q12**: Kingston's −1.24 (one job).
- **Q14**: the 2.2-2.7 % gap.
- **Q15**: the below-zero depth.
- **Q16**: the 10-us arm.
- **Q18**: the 2.96 % (a model not on disk).
- **Q20**: the park's "once" and "quarters" (one firing).
- **Q21**: the spectator's kept coherence.
- **Q22**: the precession.
- **Q24**: the +0.6 deg.
- **Q25**: the own-vs-laid split (one job).
- **Q32**: −0.019.
- Off Pittsburgh, every crossing column (Q11-Q13, Q17-Q18) is one job per chip.
