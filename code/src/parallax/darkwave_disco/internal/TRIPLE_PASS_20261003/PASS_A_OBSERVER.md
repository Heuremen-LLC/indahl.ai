# TRIPLE PASS, SEAT A -- THE OBSERVER (LAID)
Bones, 2026-10-03. Read-only audit of every quantum-hardware firing the project records. Nothing edited outside this folder; nothing submitted to hardware.

## How to read this pass
- **Clocks (The Stake).** [LAID] = laid time, the maker's stamps and stated timings, gate counts we scheduled. [WITNESS] = a spectator qubit, or another firing reading this one. [OWN] = the measured qubit's own decay clock. A number with no clock of its own (a count, a probability) is marked [no clock].
- **Times** are the maker's stamps from the job/task records (created / running / finished), converted to EDT, unless marked "submit" (our side) or "ledger stamp".
- **Widths** are shot-resampling widths as printed in the read. "Job scatter" = sd of the per-job values / sqrt(number of jobs); it holds the job-to-job wander the shot width does not.
- **Lap up** = from the read file to the claimed number (re-run or re-derived where a reader and the raw exist). **Lap down** = from the claimed number back to the read: does the claim say more (more reads, smaller width, another quantity, another chip, another time)?
- **n** = reads (jobs/tasks) and chips behind each claimed number, and the look-elsewhere count inside that job (arms laid, quantities the read prints).
- **Claim documents**, quoted with line numbers as they stand at this pass: `7_PUBLIC.md` (7P:n), `for_heuremen_org/LAWS_UPDATE_DRAFT.md` (LAWS:n), `internal/MEASUREMENT_PAPER_DRAFT_20261003.md` (PAPER:n). Ledger = `parallax/THIRD_RUNG_20260928.md` (§n, ledger:line).

## What this pass ran (all on disk; files beside this one)
- `index_firings.py` -> `index_firings.json/.txt`: every IBM job on disk (188: 48 on 9/24, 65 on 9/28, 75 on 10/1-10/2) and every Braket task (563) with the maker's stamps, shots, charged seconds, payload hashes, freeze hashes.
- `rerun_setup.sh` + `rerun/`: the release's frozen readers (`for_indahl_ai/data/code/`) re-run on the raw jobs in a sandbox (inputs symlinked file by file; every write lands in `rerun/`). **Byte-identical to the release reads:** close_push, close_looktime, close_giveback, noname_read1, hold_run (.txt and .json), witness_run (.txt and .json), lone_vs_tail, tail_run, jump_rerack, jump_run, jump_cube, none_arm_three_chips, short_wait_across_time, half_push, sides, discarded_push, discarded_hold, run9_pittsburgh, and the readers' own JSON outputs jump_run, none_arm_three_chips, short_wait_across_time, tail_run, sides_read1 (25 files). run5_marrakesh: every number identical, title line differs ("THE NONE SHAPE" vs "THE NONE"; read5.py was edited after the read was written).
- `lapup.py` -> `lapup.txt`: (1) the two replication reads, which have no reader in the release, recomputed from the raw jobs with the frozen push reader's own `push_stats()`: every printed number matches `rep_marrakesh_read1.txt` and `rep_kingston_read1.txt`; (2) push shortfall and count-growing cap; (3) look ratios with shot and job-scatter widths; (4) give-back job scatter; (5) stopwatch park bookkeeping; (6) the 9/25 Rigetti three-box value with a binomial width; (7) the no-name job's ten-arm family; (8) the gap-clock ratio.
- `lapup_push_bits.py` -> `lapup_push_bits.txt`: two ledger-only push-run numbers re-derived from the raw jobs (the 438 bit-reads of PAPER:223; the shot-to-shot lean of LAWS:17 / PAPER:239), for all five push jobs. Re-run outputs sit in `rerun/out/`.
- Release integrity: all 83 `SHA256SUMS.txt` entries match their files; every freeze (89 freeze files, 35 distinct combined hashes) lists per-file hashes that match the code on disk, and all 74 job metas on disk carry their freeze's combined hash at fire; the release code equals the frozen code of every 10/2 run family. Not in the release: the run scripts of runs 1 and 3 (10/1-10/2) and all of the Boston (stone) code.

## The laid totals
- **IBM, 10/1 23:09 - 10/2 17:42 EDT:** 75 jobs fired, 74 landed (run 6 cancelled by the maker at its cap, nothing returned); 387 s on the payload meters + 2 s billed for run 6 = 389 s; 327,260 circuit-shots (74 jobs). Five chips: ibm_pittsburgh 37, ibm_marrakesh 26, ibm_kingston 6, ibm_phoenix 3, ibm_boston 3. Ledger §141/§143 count "72 jobs (71 landed), 371 s, 311,524 shots": that is the state at 15:10 EDT, before runs 121 and 141 x 2 (+18 s, +15,736 circuit-shots).
- **IBM, 9/28 08:30 - 15:41 EDT:** 65 jobs (Marrakesh 23, Fez 37, Kingston 5), 586 s charged, all DONE. **IBM, 9/24:** 48 jobs (Marrakesh 41, Kingston 4, Fez 3), 1,849 s charged, 47 DONE, 1 ERROR (job 6073 = daqmtobt55cs738rvdfg).
- **Rigetti Cepheus-1-108Q via Amazon Braket:** 563 tasks, created 9/25 17:03 - 9/28 21:57 EDT (UTC 9/25 21:03 - 9/29 01:57); 543 COMPLETED, 20 FAILED (the 9/26 ring rejections). 225 tasks on 9/25-26, 338 on 9/28.
- **Older firings the ledger records:** 2026-04-27 Q-BERT (raw gone), 2026-07-11 GHZ pinata (counts on disk, no job id), 2026-08-13 (ledger row only).
- **After 10/2 17:42 EDT nothing fired.** The chain was stopped by hand 18:00:37 (`data/fire_logs_move.txt`). Frozen, never fired: runs 8; 52-53 (sides); 82-83 (stopwatch); 122-123 (no-name); 131-133 (between); 142-143 on Kingston and Marrakesh (pushrep). 10/3: no firing.
- **What the ledger records of the laid side:** of the 75 job ids of 10/1-10/2, one is in the ledger (run 121, §145); freeze hashes for runs 1 (Kingston), 5, 121 and the unfired 131; prediction hashes for Kingston runs 1-3. The other job ids, settings and payload hashes live in the fire records on disk (`out/qubit_*_run/data/fire/*/run*_{job,meta,payload_meta}.json`), not in the ledger. 7P:34 says "the ledger records each job's ID, settings and hash"; PAPER:306 says the same facts are "kept with each run's fire records, outside the release". This file lists all of them.

---
## A. FIRINGS BEFORE 9/28 THAT A CLAIM LEANS ON (date order)

### A01 · 2026-04-27 · Q-BERT Experiments A and B · ibm_kingston (B also ibm_marrakesh, ibm_fez)
- **Laid.** [LAID] Exp A: 4 qubits read in turn (forward, reversed) and all at once, ibm_kingston, job d7nvmuqk4prs73dsqd80, with a twin job (d7nvmus9...) submitted seconds later (`NOTHING_SWEEP_apr_aug.md`:21). Exp B: a triplet on three chips. Circuits, shots, waits: not on disk. No freeze. Raw shots gone (ledger §22: "Gone for good: ... April/August raw"; `FREE_CHECKS_20260929.md`:22).
- **Used for.** 7P:102 "Closed, three rulers each: ... the order of looking sets the heat." (its April leg, ledger §15-16, §154).
- **Lap up.** No read file. The numbers exist as table rows only, no widths: `NOTHING_SWEEP_apr_aug.md`:184 "fwd 1.44/1.61/1.90/3.52%; rev 2.83/2.39/1.61/1.44%; sim 1.34/1.20/0.95/1.34%"; :185 "q3 hottest: Kingston 3.05, Marrakesh 2.88, Fez 6.62%".
- **Lap down.** The same rows label themselves "reinterpreted: measurement-order (readout timing) effect" and "CONFOUNDED: q3 always measured last"; ledger §15: "in April the last-read qubit also idled longer (textbook idle time)". The twin jobs of one circuit read q1 = 66 then 123 counts (z -4.15, NOTHING_SWEEP:21): job-to-job wander as large as the effect.
- **n.** 2 Kingston jobs (Exp A) + Exp B on 3 chips; arms per job not on disk.
- **CARRIES:** table rows with no widths and no raw | **LAPS DON'T MEET** (nothing to re-read; the rows are filed as a timing confound).

### A02 · 2026-07-11 · GHZ pinata · ibm_fez
- **Laid.** [LAID] `quantum_archive/Kitchen Sink/event_horizon_ghz_20260711_121806.json`: backend ibm_fez, 4096 shots per setting, 24 settings in the tau/3 series. No job id; the shot spacing is not recorded ("Assumed IBM's default, 250 us ... Flagged as an assumption", `CHIP_TRIANGLE_20261001.md`:36).
- **Used for.** 7P:68 "1.923 / no ratio on the chip -- the microsecond clock sits +1.88 +- 1.16 series-taus from the shot clocks (a separation, not a ratio)": the GHZ record is one of the three "shot clocks" (with the 9/28 echo, B02, and the 9/28 Fez parallax J2, B06).
- **Lap up.** `CHIP_TRIANGLE_20261001.md`:82 "GHZ | -18.982 | 1.151"; :86 "carry - echo | +1.883 | 1.156".
- **Lap down.** See B02 for the whole leg. Here: the GHZ clock's microseconds rest on the assumed 250-us spacing and on a solved per-shot overhead of ~5,600 us that the same file finds "200-500x the buzz's own recorded fixed part (8.6 us Fez, 11.2-11.4 Kingston)" (ledger:1295-1296).
- **n.** one run, one chip, 24 settings x 4096 shots [LAID]; job id unknown.
- **CARRIES:** an angle record whose time unit is assumed | **LAPS DON'T MEET** (its clock is an assumption, not a laid record).

### A03 · 2026-08-13 · EH precision · ibm_marrakesh
- **Laid.** Ledger row only (§16D "0.9898474438395595 three times"; `NOTHING_SWEEP_apr_aug.md`:196-197, "8/13 16:52-17:36"). Raw gone.
- **Used for.** None of the three claim documents.
- **CARRIES:** a ledger row | not used.

### A04 · 2026-09-24 13:02-14:50 EDT · dark_floor v1 + v2 (Estimator) · ibm_marrakesh, ibm_kingston · 13 jobs
- **Laid.** [LAID] v1: Marrakesh daqlf73t55cs738rtfv0 (created 13:02:20, 48 pubs x 8192 shots, 358 s), Kingston daqljjqkqcdc73aau0n0 (13:11:44, 24 pubs x 8192, 187 s). v2 attempt 1: daqmtobt55cs738rvdfg (14:41:38, ERROR; 12 s charged, 8.64 s of circuits ran, results never returned; ledger §19). v2 resend: 10 jobs x 3 pubs (2048/4096 shots), 14:45:10-14:45:20, 64 s each. The re-pull metadata of all 12 landed Estimator jobs shows measure twirling ON and readout mitigation ON (every 10/1-10/2 job ran with both off). No freeze on disk.
- **Used for.** 7P:102 "the order of looking sets the heat", through ledger §19 items 3-4 ("+0.76% excess -> 'ordering artifact'"; "bell FIRST +1.24% +/- 0.46, bell LAST -0.13%").
- **Lap up.** Estimator expectation values in `~/bones-forge/dark_floor_runs/dark_floor_*real*.json`; ledger §22: "The 9/24 Estimator verdicts had readout correction + twirling baked in". No reader re-run here (no shots exist: Estimator returns averages).
- **Lap down.** The legs are mitigated averages, with the order balanced away in the design that made them; the claim reads them as part of a closed three-ruler result.
- **n.** 12 landed jobs + 1 failed, 2 chips.
- **CARRIES:** mitigated averages from two chips | **LAPS DON'T MEET** (no shot record behind the order leg; the averages carry the instrument's own correction).

### A05 · 2026-09-24 16:10-16:38 EDT · dark_link (21 jobs), dark_edge (probe + 3), space_time_same (1) · ibm_marrakesh · 26 jobs
- **Laid.** [LAID] dark_link run 1: 6 jobs x 16 pubs x 4096 shots (16:10:13-16:10:20, 20 s each; account key .ibm_quantum_key_3); balanced rerun: 15 jobs x 16 pubs (16:16:05-16:16:17); dark_edge probe daqohpmekp0c73ar2pn0 (16:32:38, 2 pubs, kerneled) + 3 jobs x 16 pubs (16:33:50-16:33:53); space_time_same daqoklakqcdc73ab21cg (16:38:45, 28 pubs). Pre-registered in `gridsong/biblioteca.md`:6173-6199.
- **Used for.** Not quoted in 7P, LAWS or PAPER. (Ledger §1 "the joining eats the one" rests on dark_edge raw dots; §16A's "first looked at = cold" seats come from 9/24 Marrakesh.)
- **CARRIES:** pre-registered nulls on 9/24 (biblioteca:6200) | not used by the claims.

### A06 · 2026-09-24 16:52-17:31 EDT · arrow panels (3), space_time_same (2), three_box (3), three_box_11 (1) · Marrakesh, Kingston, Fez · 9 jobs
- **Laid.** [LAID] arrow panels: Marrakesh daqor7eekp0c73ar35gg (16:52:45, 42 pubs), Kingston daqorotb46qs73a1iccg (16:53:55, 42), Fez daqp5ndb46qs73a1imvg (17:15:09, 42); space_time_same Kingston daqorouekp0c73ar365g (28), Fez daqp61eekp0c73ar3hg0 (28); three_box Marrakesh daqp4prt55cs738s27mg (17:13:11), Kingston daqp52bt55cs738s280g (17:13:45), Fez daqp5ajt55cs738s28ag (17:14:18), each 4 pubs x 8192; three_box_11 Marrakesh daqpd5rt55cs738s2ipg (17:31:03).
- **Used for.** 7P:102 "the order of looking sets the heat", through ledger §16A: "Sept 24, three-box (3 chips): the probe is measured 68-348 ns BEFORE the system qubits; the system qubits carry 3.5-5% extra 1s (filed as gate error). Last looked at = hot."
- **Lap up.** `~/bones-forge/dark_floor_runs/three_box_real_ibm_*.json`, `raw_threebox_all.json` (32 circuits x 8192). The 68-348 ns ordering is a scheduler fact read from the compiled circuits [LAID], not a laid choice. No release reader.
- **Lap down.** The "extra 1s" are filed in their own run as gate error; the claim's "closed, three rulers each" treats them as one of the order-of-looking rulers.
- **n.** 4 three-box jobs on 3 chips (one per chip, Marrakesh twice), 4 pubs each.
- **CARRIES:** one job per chip, a per-chip excess of 1s with the probe read first | **LAPS DON'T MEET** (the run itself files the excess as gate error; no width is quoted where it is used).

### A07 · 2026-09-25 17:03 - 23:22 EDT · Rigetti q0, round 1 steps 1/2/2b/3, grid16q qutrit, round 2 · Cepheus-1-108Q · 154 tasks
- **Laid.** [LAID] step 1 (f12 Rabi): 21 tasks x 300 shots (UTC 9/25 21:03:34-41); step 2 (readout + Tuco + Ramsey): 42 tasks x 300/1000 (9/26 01:14:19-35); step 2b: 21 x 500 (01:16:21-28) + 1 orphan task (4f3a04f7..., 01:15:57); **step 3, native three-box q0: 35 tasks x 1000 shots (01:21:24-37)**; grid16q: 16 x 3000 (01:36); round 2: 18 tasks x 1000/3000 (03:19-03:21). All on q0, `disable_qubit_rewiring`. Scripts `standoff/braket_round1*.py`, `grid16q.py`, `round2_*.py`; pre-registration text inside `braket_round1_step3.py`:17. No hash freeze.
- **Used for.** 7P:75 (Finding Five) "A qutrit three-box silent branch read below zero too, -0.019 (one run). § 154-155."
- **Lap up.** `standoff/step3_abl.json` "B_not": -0.019355. Recomputed with the script's own analysis (sinusoid fit to 8 readout-corrected points, read at x0 - pi): -0.0194 [no clock]. **Width, not in any file:** binomial bootstrap over the 35 step-3 tasks and the 3 step-2 calibration tasks: sd 0.0102, 95% band -0.0394 .. +0.0005 (`lapup.txt` section 6). Sibling branches of the same fit: A_not +0.0136 +- 0.0107, psi +0.0855 +- 0.0112, C_not +0.6052 +- 0.0118.
- **Lap down.** The claim prints -0.019 with no width; at +-0.010 it sits 1.9 widths below zero. The quantity is a fitted curve evaluated at a fitted phase (x0 = -3.056 rad), corrected with a readout calibration from other tasks: not a raw branch population. 7P:75 sets it beside the no-name job's -0.12 / -0.58 / -0.97 % (another vendor, another day, another quantity, another unit). The ledger cite "§ 154-155" holds it as "one run" (§154) and does not print it at §155.
- **n.** 35 tasks + 3 calibration tasks, one qubit, one chip; 4 branch values + an ABL triple out of one fit (look-elsewhere inside the firing: 7 printed numbers).
- **CARRIES:** one firing, one qubit, a fitted branch value -0.019 +- 0.010 [no clock] | **LAPS DON'T MEET** (width absent where claimed; set beside a different quantity as if one sign).

### A08 · 2026-09-26 08:12 - 12:53 EDT · Rigetti pup dice, ring (q90 Rabi, KCBS), plus-none q99, ring diagnostic, ring rerun · 71 tasks
- **Laid.** [LAID] dice 1 task x 10,000 (80 columns, 12:12:48 UTC); ring q90 Rabi 9 x 300 (16:24 UTC); ring KCBS main 26 x 1900, **20 FAILED** (16:25 UTC; ledger §19 "Braket's 20 Ring rejections"); plus-none q99 14 x 1300; ring diagnostic 1 x 100; ring rerun 20 x 1900 (16:52 UTC).
- **Used for.** None of the three documents. (Ledger §154 keeps "q90 'a failure never follows a failure'" as a weakened row; §18 found it absent chip-wide on 9/28.)
- **CARRIES:** a q90 row | not used.

---
## B. 2026-09-28: IBM BY DAY, RIGETTI BY NIGHT (date order, maker's stamps)

### B01 · 9/28 08:30 EDT · THE PARALLAX RUN · ibm_marrakesh · 4 jobs
- **Laid.** [LAID] 78 even qubits, kerneled two-look shots. J1 dat5rslvr3kc73el0klg (4 pubs x 4000, default spacing; created 08:30:42, ran 08:30:44, done 08:36:42), J2 dat5rsqhcrkc73dtn700 (2 x 2000, 20-us spacing; ran 08:33:36), J3 dat5rt3g95ks73egea00 (2 x 2000, 1 ms; ran 08:34:31), J4 dat5rt3ojkfs738q7gf0 (2 x 2000; ran 08:36:17). 18 s charged (600 -> 582 left). No freeze. Folder `out/20260928_083041/`.
- **Used for.** PAPER:203 "Shots outside both the |0> and |1> clouds on both of two readouts: 134 on ibm_marrakesh against 6.5 expected by chance (prepared |0>)"; LAWS:15-16 "a third level shows on a minority of qubits on IBM ... in three behaviours"; 7P:102 "the third level's three behaviours on two vendors".
- **Lap up.** No read file or script prints 134 / 6.5. The count is an in-session analysis recorded at `gridsong/biblioteca.md`:7598-7600 ("parallax J1-J4 raw dots, two looks, 3 fridges; cut = >4 widths from both clouds, checked on half the refs ... Marrakesh told0 134 vs 6.5 chance, told1 100 vs 16") and ledger §2. The run's own summary (`PARALLAX_RESULTS.md`) prints "prepared 0, off both clouds 0.0000" (median over qubits). Raw on disk (J1-J4 .npz).
- **Lap down.** PAPER:202 dates these counts "two-readout jobs among those of 2026-09-24 to 09-28"; the laid record puts the counts on the three 9/28 parallax runs (B01, B03, B06) only. The "6.5 by chance" has no stated model in a file.
- **n.** 4 jobs, 1 chip, 78 qubits; the summary prints 12 quantities + 3 seat lists.
- **CARRIES:** four jobs on one chip: a count of off-both shots on a few seats, no file behind the count | **LAPS DON'T MEET** (no read; PAPER's date range is wider than the laid jobs).

### B02 · 9/28 12:27 EDT · THE ECHO (pre-registered) · ibm_marrakesh · 14 jobs
- **Laid.** [LAID] Pre-registration `parallax/PREREG_ECHO.md` (written before any shot): E1 = look, X, look; E0 = look, look; 78 even qubits, 1500 shots, raw I/Q; shot spacing (rep_delay) 20, 50, 100, 250, 500, 1000, 2000 us, one job per spacing per E. Jobs (E1/E0 pairs in order of spacing): dat9atjojkfs738qbtr0 / dat9atqhcrkc73dtrkdg (20 us), dat9atrojkfs738qbtsg / dat9au5vr3kc73el53h0 (50), dat9audvr3kc73el53hg / dat9aujg95ks73egio2g (100), dat9autvr3kc73el53i0 / dat9aurojkfs738qbtug (250), dat9av2hcrkc73dtrkhg / dat9avahcrkc73dtrki0 (500), dat9avlvr3kc73el53j0 / dat9avihcrkc73dtrkj0 (1000), dat9avqhcrkc73dtrkk0 / dat9b05vr3kc73el53kg (2000). **All 14 created 12:27:34-12:27:44 and started running 12:27:36-12:27:59 EDT; the last finished 12:28:13.** 42 s charged (582 -> 540). No hash freeze (the pre-registration text is the seal).
- **Used for.**
  - LAWS:26 "MEASURED: what the reset erases is what was placed (0.067 %); what arose on its own stays (+23 points at 20 us, gone by 500)."
  - 7P:62 "values near 0.618 recur (... a 0.62-0.65 band on 9/28)".
  - 7P:68 the "+1.88 +- 1.16 series-taus" (the carry clock and the echo clock come from this firing).
  - PAPER:205 "Chip-wide on ibm_marrakesh (74 readable qubits, inter-shot gaps 20 us to 2 ms), the median qubit reads 0.84% stray excitation at a 20-us gap above a 0.31% floor, draining on a ~72 us scale ...", "ibm_marrakesh q26, 4.6% of shots at 20-us gaps, gone by 250 us"; PAPER:206 "Blinking: ibm_marrakesh q60, 5-9% of shots in some jobs and about 0 in others minutes apart; q126 the same; q66, 13% in one job [§2]"; PAPER:204 standing q14/q24.
  - 7P:102 "the order of looking sets the heat" (ledger §15: "crowded looks raise stray 1s 0.30% -> 0.70%").
- **Lap up.**
  - 0.067 %: `PRE_MEASUREMENT_20260930.md`:165 "| 20 | **0.067%** | 0.07% |" (median qubit, P(m0=1 | E1 file) - P(m0=1 | E0 file); the pre-registered quantity, reproduced by a second pipeline). No width printed.
  - +23 points: `PRE_MEASUREMENT_20260930.md`:236 "| 20 | **+22.97pp** |", the "(lag-1 diff) - (lag-20 diff), pooled and shot-weighted"; :240 "| 500 | -0.56pp (noise) |". No width printed.
  - The band: `out/qubit_fifth_run/data/reads/band.txt` (the 10/2 copy of the band's own code, checked to reproduce 9/28: `data/band/flash_original_check.txt`): 9/28 R^2 at readout cutoffs 0.62 / 0.63 / 0.64 / 0.65 = 0.228 +- 0.197, 0.278 +- 0.215, 0.322 +- 0.206, 0.433 +- 0.222 [no clock: correlation of two fitted per-qubit clocks across ~23 resolving qubits].
  - +1.88: see A02 and the lap down below.
  - 0.84 % / 0.31 % / ~72 us: `out/echo_heat_by_gap.json` (ledger §17); not re-run here.
- **Lap down.**
  - "stays": the +23 points is a same-qubit clustering statistic (lag-1 minus lag-20 conditioning, pooled, shot-weighted, dominated at long gaps by blinking qubits q68 17.1 %, q76 11.7 %; PRE_MEASUREMENT:206-209). The same record read with a direction-capable ruler (ledger §65b, `DIRECTION_RULER_20261001.md`) gives "0 of 72 qubits carry a direction at any gap", raw mirror counts "001 = 2601 vs 100 = 2595" at 20 us: the clustering reads the same forwards and backwards. The law's "what arose on its own stays" says more than the read (a forward carry); the number also travels without its width and without its pooled, shot-weighted definition.
  - The band: 0.62-0.65 is a readout-cutoff position along the |0>-|1> line (a fraction of the cloud distance), not a ratio of two clocks; each R^2 there is 1.0-2.0 of its own widths from zero; the same 17-cutoff scan labels 0.57-0.58 and 0.67-0.68 "EXISTS" too. **The band was re-fired** (Q19 below, 24 jobs, three reads, same 78 qubits, same code): 0.62-0.65 reads 0.00-0.11 in all three (ledger §140: "Not there, three reads"). 7P:62 quotes the 9/28 value and not the re-fire.
  - +1.88 series-taus: the conversion code says "This conversion depends ONLY on a quantity's *relative* bootstrap error, not on its native value or unit" (`out/the_middle/chip_triangle.py`:133-134). The +1.88 is the difference between the carry clock's mapped relative error (62.8 +- 13.1 us, rel. 0.21) and the echo clock's (rel. ~1.0), i.e. a difference of widths, not of clock values; and the "carry" was itself renamed "symmetric clustering" (ledger §65). The claim reads it as a separation of clocks.
  - "minutes apart" (PAPER:206; ledger §2 "Marrakesh 60 -- 5-9% of shots in some jobs, ~0 in others minutes apart"; biblioteca:7611 "Each gap was its own job minutes apart"): **[LAID] the 14 echo jobs started running within 23 seconds of each other** (12:27:36-12:27:59). Between jobs, the shot spacing (20 us -> 2 ms) and E0/E1 change too. Rigetti's blink batches were minutes apart (B15 below); the IBM ones were not.
- **n.** 14 jobs (one per spacing per E), 1 chip, 78 qubits (74-75 readable); one circuit per job. The pre-registration fixed 2 questions; the later readings of the same record are many (pre-measurement: 240 tries; three-times-visibility flash: 128,068 tries; clocks from three places: 51,665 tries; direction ruler: 847 tries; ledger §36, §65, §65b, §68).
- **CARRIES:** one firing, one chip: the pre-registered E1-E0 echo at 0.07 % (median qubit, no width), and a cloud of later readings | **LAPS DON'T MEET** (LAWS:26 "stays" against a direction-blind clustering read; 7P:62 band without its re-fire; 7P:68 a difference of relative errors read as a clock separation; PAPER:206 "minutes" against 23 laid seconds).

### B03 · 9/28 12:34 EDT · THE PARALLAX RUN · ibm_kingston · 4 jobs
- **Laid.** [LAID] Same design as B01. J1 dat9ebbg95ks73egis2g (4 x 4000; ran 12:34:55-12:35:14), J2 dat9eblvr3kc73el57fg (20 us), J3 dat9ebtvr3kc73el57gg (1 ms), J4 dat9ec3ojkfs738qc24g. 17 s (540 -> 523).
- **Used for.** PAPER:203 "98 on ibm_kingston against 2"; PAPER:205 "two ibm_kingston qubits are also listed as carried [§5]"; ledger §2 "Kingston 62: 2.3% -> 9.4% of shots with 20 us gaps"; ledger §36d "Kingston ... +11.1 pp carry at 20 us"; LAWS:15-16 and 7P:102 (third level, two vendors).
- **Lap up / down.** As B01: the counts are in `gridsong/biblioteca.md`:7600-7605 only (seats 58 / 62 / 40: "1.6% -> 6.1%; 2.3% -> 9.4%; 0.13% -> 1.85%"). Its run summary prints "prepared 1, off both clouds 0.0000" (median). PAPER leaves the seat labels out (ledger:376 keeps one of them internal).
- **n.** 4 jobs, 1 chip, 78 qubits.
- **CARRIES:** four jobs on one chip: carried off-both counts on 3 seats | **LAPS DON'T MEET** (no read file; same date-range point as B01).

### B04 · 9/28 12:39 EDT · RIGETTI heat-vs-lens RPM, q0 · Cepheus-1-108Q · 6 tasks
- **Laid.** [LAID] 6 tasks (2 x 10,000, 2 x 1000, 2 x 500 shots), UTC 16:39:42-43; `standoff/heatlens_tasks.json`; $11.58 (`braket_ledger.json`).
- **Used for.** None of the three documents.
- **CARRIES:** six q0 tasks | not used.

### B05 · 9/28 12:45-13:22 EDT · THE DARKWAVE (eraser) ROUNDS · ibm_kingston, ibm_fez, ibm_marrakesh · 19 jobs in 6 firings
- **Laid.** [LAID] 8 pubs x 4000 shots each, 3 qubits, bits only: Kingston dat9j9tvr3kc73el5d3g (12:45:27; qubits 47/48/64); Fez + Marrakesh 12:54:53-12:55:36 (early / late5 / late50; 6 jobs); 12:58:05-06 (late0; 2); 12:59:52 (late50e; 2); Fez 13:04:29-13:05:55 (late0/2/5/10/20; 5); Fez 13:21:57-13:22:30 (late5 / late50B / late5B; 3). 11-12 s each.
- **Used for.** Not quoted. Ledger §19 item 6 ("9/28 rounds 1-9: the chip moved unpinned measurements LATE -> eraser fringe 0.13 instead of 0.89 -> 'TRAP'") feeds the order-of-looking pattern note behind 7P:102.
- **CARRIES:** 19 eraser jobs on three chips | not used by a number in the claims.

### B06 · 9/28 12:55 EDT · THE PARALLAX RUN · ibm_fez · 4 jobs
- **Laid.** [LAID] Same design as B01. J1 dat9o2ihcrkc73dts3jg (4 x 4000; created 12:55:38; ran 12:55:40-12:56:15), J2 dat9o2tvr3kc73el5j20 (2 x 2000, 20 us), J3 dat9o33ojkfs738qcdu0 (1 ms), J4 dat9o33g95ks73egj7fg.
- **Used for.** PAPER:203 "about none on ibm_fez"; 7P:68 via the "buzz" clock (`CHIP_TRIANGLE_20261001.md`:48 "buzz | shots | 51.689 @ 20us (J2)"); LAWS:41 and 7P:102 indirectly (the buzz is the W1 object, see B10).
- **Lap up.** `out/the_buzz/THE_BUZZ.md`:51-52 (J1/J2 phase steps per shot: -0.2947848 +- 0.0000026 and -0.0667452 +- 0.0000127 cycles); `CHIP_TRIANGLE`:48, :81 "buzz | -18.934 | 1.147".
- **Lap down.** The buzz is a tone in the readout records of tile-8 seats; ledger:462 (§33) "the qubits don't carry it". As in B02, its series-tau value depends only on its relative error.
- **n.** 4 jobs, 1 chip, 78 qubits; the buzz reading uses 3 seats.
- **CARRIES:** a readout-line tone on 3 seats, one chip | **LAPS DON'T MEET** (for 7P:68: a relative-error map, see B02).

### B07 · 9/28 13:04-13:21 EDT · FEZ WITNESS JOBS: partner, beat, split, culprit, ring, eleven, barrier, alone · ibm_fez · 8 jobs, 8 firings
- **Laid.** [LAID] partner dat9s7rojkfs738qcjag (13:04:31, 40 pubs x 2000), beat dat9tulvr3kc73el5q9g (13:08:10, 60 pubs), split dat9urjojkfs738qcmgg (13:10:06, 30), culprit dat9vlrojkfs738qcnk0 (13:11:51, 30), ring data0erojkfs738qcoe0 (13:13:31, 20), eleven data13ihcrkc73dtse70 (13:14:55, 30), barrier data3dbg95ks73egjl40 (13:19:49, 30), alone data423ojkfs738qcse0 (13:21:12, 28). 2000 shots, a few clock qubits (q143/q144 and neighbours), bits. No freeze.
- **Used for.** PAPER:158 "ibm_fez q144 ran at 28.2-28.8 kHz with 0, 1 or 77 other qubits active ... With its neighbour q143 in |1>, q144 ran at 21.9 kHz (vendor table: 21.7) ... These rest on 778 within-job tests, Holm-corrected [§31]."
- **Lap up.** `out/witness_crowd/WITNESS_CROWD.md`:35 "28.6, 28.2 and 28.8 kHz with 0 others; ... 28.8 +/- 0.2 with 77 others"; the 778 tests: `final_tests.py` -> `final_tests.json` (not re-run here).
- **Lap down.** [LAID] "vendor table" = the IBM Fez calibration of **9/25** ("the newest on disk (there is no 9/28 Fez snapshot in either cache)", WITNESS_CROWD.md:13), set against runs of 9/28. WITNESS_CROWD.md:97: "Fez room size rides with the clock. The small rooms ran 16:54-17:22, the big rooms at 18:26 and 18:43, and yeast/ripples at 19:37-19:41": crowd size and laid time move together.
- **n.** These 8 jobs are part of the 25 Fez jobs (9/28 16:54-19:41 UTC) and 246 Rigetti tasks that WITNESS_CROWD read; 778 within-job tests over all of them, Holm-corrected.
- **CARRIES:** eight jobs, one chip, one clock seat at a time | **LAPS MEET** for the kHz readings as printed in WITNESS_CROWD.md; the table comparison runs a 3-day-old calibration against them (PAPER [TO FILL] "which vendor table" = Fez 9/25, Rigetti 9/28).

### B08 · 9/28 14:26 EDT · THE LISTEN · ibm_fez · 1 job
- **Laid.** [LAID] datb2grojkfs738qe8jg (created 14:26:11, ran 14:26:13-14:26:48), 24 pubs x 2000, 78 even qubits held as clocks (`out/listen_ibm_fez_142649/raw.json`). 15 s.
- **Used for.** PAPER:158 ("77 other qubits active"), via WITNESS_CROWD (ledger §31).
- **CARRIES:** one job, one chip: the big-room clock readings | **LAPS MEET** (as B07).

### B09 · 9/28 14:38 EDT · split2 · ibm_fez · 1 job
- **Laid.** [LAID] datb823g95ks73egl8e0 (14:38:00), 48 pubs x 1000, qubits 143/138.
- **Used for.** PAPER:158 "q138 moved -20 deg with two neighbours in |1> (table: -19)" (WITNESS_CROWD; ledger §31).
- **CARRIES:** one job, one chip, two clock seats | **LAPS MEET** (as B07; 9/25 table).

### B10 · 9/28 14:43 EDT · oddraw (the odd half, raw I/Q) · ibm_fez · 1 job
- **Laid.** [LAID] datbagtvr3kc73el7m2g (created 14:43:15, ran 14:43:21-14:44:13), 26 pubs x 2000, 78 odd qubits, kerneled; Ramsey waits 0-20 us inside the shots. 16 s.
- **Used for.**
  - 7P:102 "Closed, three rulers each: ... the inside never sees the outside's laid time".
  - LAWS:41 "MEASURED: the inside never reads the outside's laid time -- a spectator's clock is blind to how long we waited."
- **Lap up.** `parallax/OBSERVER_WITNESS_20260930.md`:72-96 (Pair 2, "26 Fez odd-run batches, Ramsey wait 0-20 us"): fit diff = a + b x wait, a = -0.54 ns, b = +1000.0020 ns per us; `TRIANGLE_OF_FUCKUPS_20261002.md`:137-140 (row W1). The "inside clock" is the buzz's phase step per shot on seats 81 and 103 (THE_BUZZ.md:55: "odd run (26 pubs x 2000), seats 81 and 103 ... +0.154798").
- **Lap down.**
  - The read's inside clock is a readout-line tone on two seats; ledger:462 (§33) "the qubits don't carry it (no Ramsey swing at the step)". LAWS:41 calls it "a spectator's clock". Spectator **qubits** in other firings do follow laid time: the look-time jobs (Q17) calibrate every spectator on laid delays of 0/30/60/120 us and read 3.1444 +- 0.0760 deg/us over the first 30 us [WITNESS against LAID]; the stopwatch (Q15) reads 35.6 / 48.3 us for laid 40 / 60 us of emitter-ON.
  - The 1:1 slope is an identity of the construction (per-run part = outside number minus an inside number near zero; TRIANGLE:441 "Shuttle's catch ('the 1:1 is an identity') is right about the algebra").
- **n.** 1 job, 1 chip, 2 seats, 26 pubs; 2,000 shuffle draws in the pair test.
- **CARRIES:** one job: a readout tone's per-shot step that does not move with a 0-20-us in-shot wait | **LAPS DON'T MEET** (LAWS:41 names a spectator qubit's clock; the read is a readout tone, and spectator qubits in Q15/Q17/Q20 do track laid time; 7P:102 calls it closed by three rulers on one job).

### B11 · 9/28 14:49 EDT · the_do · ibm_fez · 1 job
- **Laid.** [LAID] datbddrojkfs738qel70 (14:49:27), 12 pubs x 4000, qubits 113/72/27.
- **Used for.** PAPER:158 "q113's frequency moved -5.1 kHz with neighbour q119 in |1> (table: -5.1)" (WITNESS_CROWD; ledger §31).
- **CARRIES:** one job, one chip, three clock seats | **LAPS MEET** (as B07; 9/25 table).

### B12 · 9/28 15:37 EDT · ripples · ibm_fez · 1 job
- **Laid.** [LAID] datc3qbojkfs738qfk30 (15:37:13), 10 pubs x 4000. **Used for.** WITNESS_CROWD's "others read during the wait vs at the end: 24 tests, nothing" (not quoted in a claim). **CARRIES:** one job | not used by a number.

### B13 · 9/28 15:39-15:41 EDT · the yeast hour · ibm_fez · 7 jobs in 3 firings
- **Laid.** [LAID] datc4n5vr3kc73el8phg (15:39:08); datc545vr3kc73el8q10, datc583g95ks73egmfrg, datc5bjg95ks73egmg50, datc5eqhcrkc73dtvb80 (15:40:01-15:40:43); datc5jbg95ks73egmgmg, datc5n3g95ks73egmgvg (15:41:02-16). 4 pubs x 4000 each.
- **Used for.** PAPER:158 ("8 and 10 others", q144 with both wired neighbours half-and-half) via WITNESS_CROWD.md:46-54.
- **CARRIES:** seven jobs, one chip, ponds changing every 13-40 s | **LAPS MEET** (as B07).

### B14 · 9/28 18:34-18:44 EDT · RIGETTI'S GAMBLE (shuffle, blink/train, Bell) · q0/q1 · 21 tasks
- **Laid.** [LAID] 21 tasks x 3000-6000 shots (UTC 22:34:27-22:44:39), `standoff/gamble_tasks.json`, counts in `gamble_results.json`; $44.98.
- **Used for.** PAPER:196 "q0's |2> population at the start of a shot is 0.03 +- 0.17% alone ... an entangling gate leaves +0.05 +- 0.39% on q0's |2> [§5]".
- **Lap up.** Ledger §5 only ("q0 alone: rung 2 at start 0.03% +/- 0.17%"; "Bell ... +0.05% +/- 0.39%"). `gamble_results.json` holds counts, not these derived values; no analysis script or read on disk.
- **Lap down.** FREE_CHECKS_20260929.md:117-119: "On q0, the sequences that end on rung 2 carry part of their own previous shot. So q0's start number (0.29%) is partly the previous shot."
- **n.** 21 tasks, one firing, 2 qubits.
- **CARRIES:** a q0 rung-2 start value at its width, ledger-only | **LAPS DON'T MEET** (no read file between the counts and the number).

### B15 · 9/28 18:40-19:02 EDT · RIGETTI WHOLE CHIP: f12 tune (8), fine tune (8), chip run (17) · 107 columns · 33 tasks
- **Laid.** [LAID] tune 8 x 1000 (UTC 22:40:58-22:41:03), fine 8 x 1000 (22:51:17-20), run 17 tasks: 8 shuffle sequences x 5000 shots (22:52:01-05) + blink batches of 3 tasks x 2000 at **22:52:06, 22:57:11, 23:02:14** (five minutes apart). `standoff/chip/{tune,fine,run}_tasks.json`, `run.npz`, `chip_rows.json`, `mirror_check.json`; $5.80 + $5.80 + $29.75.
- **Used for.**
  - PAPER:196-199 (Rigetti baseline 0.29 +- 0.19 %; standing q24 2.05 %, q48 1.34 %, q40 1.26 %, q33 1.17 %, median 0.04 % on 56 qubits; rho -0.31 (p 0.02); carried q63 / q78 / q40; blinking q52 2.0 / 2.2 / 8.9 %, q36 8.5 / 9.9 / 18.9 %, q5 1.7 / 5.3 / 1.7 %).
  - PAPER:200, LAWS:16 "On Rigetti it survives the reset and carries into the next shot", 7P:33 "Shot-to-shot carry-over is tested on both vendors": ledger §18 / FREE_CHECKS §3 read q0's carry on this run's shuffle tasks.
  - 7P:102 "the third level's three behaviours on two vendors".
- **Lap up.** Standing: `mirror_check.json` rows read q24 0.0205, q48 0.0134, q40 0.0126, q33 0.0117 (the 2.05 / 1.34 / 1.26 / 1.17 %; 81 rows, median 0.0021 over all rows; the "56 unambiguous, median 0.04 %" subset is not a file); `chip_rows.json` q0 p2 = 0.0029 +- 0.0019 (the 0.29 +- 0.19 %). rho -0.31, the carried drains and the blink batches (2.0 / 2.2 / 8.9 % ...) are ledger §5 only. Carry: FREE_CHECKS_20260929.md:99-100 "Success leaves rung 2 (ab, aba, bab): 64 vs 88 (P 0.002) ... (aba, bab): 25 vs 43 (P 0.001)"; :110 "Counting the five ways I split q0, call it about 1 in 100". No reader script on disk for these numbers.
- **Lap down.** The carry is one qubit: FREE_CHECKS:108 "q0 is the lowest of 95 pushed qubits on the rung-2 test; q49 is next (P 0.004)"; :119 "Most qubits show no carry"; whole chip "failure right after a failure: 231,443 times, against 230,392 by chance" (:84). LAWS:16 says Rigetti's third level "survives the reset and carries into the next shot", vendor-wide; the read is q0 (8 shuffle tasks of this run), about 1 in 100 after the splits.
- **n.** 33 tasks, one firing family, 107 columns; carry: 8 shuffle tasks x 5000 shots on q0, 95 qubits tested; blinking: 3 batches.
- **CARRIES:** one firing: per-qubit rung-2 maps (two rulers: chip_rows + mirror check), and one qubit's carry at ~1 in 100 | **LAPS DON'T MEET** for LAWS:16 (vendor-wide wording on a one-qubit read) and for PAPER:197-199's rho / carried / blinking values (ledger §5 only); MEET for the standing values and q0's start value as the two files print them.

### B16 · 9/28 19:34-20:27 EDT · THE BLINK HOUR · Rigetti whole chip · 32 tasks
- **Laid.** [LAID] 8 checks x 4 tasks x 800 shots (UTC 23:34:20 ... 00:27:25, one check every 7.5 min), 107 columns; `standoff/blink_hour.py`, `chip/blink_tasks.json`, `blink.npz`, `blink_rows.json`; $20.48.
- **Used for.** PAPER:199 "in a following hour of eight checks they did not blink (q52 one excursion) [§9]. The |1>-|2> frequency (Ramsey at 1.5 us) on 31 qubits with readable contrast jumped rarely and independently, about once per 7.5-minute interval".
- **Lap up.** Ledger §9 only; `blink_rows.json` per-qubit rows on disk; no reader output for "31 qubits" / "~1 per 7.5-min interval".
- **n.** 32 tasks, 8 checks, 107 qubits.
- **CARRIES:** an hour of 8 checks; the claimed numbers equal ledger §9 | **LAPS DON'T MEET** (no read file or script below §9; PAPER:274 says these analysis files are not in the release).

### B17 · 9/28 19:41 EDT · THE WITNESS · Rigetti q0 -> q9, q1, q10 · 18 tasks
- **Laid.** [LAID] 18 tasks x 2000 shots, 4 columns (UTC 23:41:52-23:42:01); `standoff/witness.py`, `chip/witness_tasks.json`, `witness.npz`; $20.70.
- **Used for.** PAPER:189 "With q0 in |1> a neighbour's clock moves by about 0.3 deg/us; with q0 in |2>, q9 is pulled by -62 deg/us (-173 kHz) and q1 by -27 deg/us (-74 kHz), q10 by about 0 [§7]. The fall time from |2> read from the spectator is about 20 us, with fit residuals chi2 of 8.6 (q9), 11.8 (q1) and 6.2 (q10)".
- **Lap up.** Ledger §7 only; raw on disk; no analysis script or read file. Ledger §7 records a first pass withdrawn ("a 10-sigma leftover on q9; it was MY alias (clock sampled every 4 us)").
- **n.** 18 tasks, 4 qubits, waits sampled every 4 us.
- **CARRIES:** one firing: the rung-2 pull on two neighbours [WITNESS]; the claimed numbers equal ledger §7 | **LAPS DON'T MEET** (no read file or script below §7).

### B18 · 9/28 20:45 EDT · WITNESS, WHOLE CHIP · 24 tasks
- **Laid.** [LAID] 24 x 2000, 107 columns (UTC 00:45:58-00:46:15); `witness_chip.py`, `wchip.npz`; $27.60.
- **Used for.** PAPER:189 "In an earlier whole-chip run (105 other spectators) q9's fall time, 14.8 +- 5.3 us, was shorter than q0's readout value of 31.2 us (30.0-32.6) [§10]".
- **CARRIES:** one firing [WITNESS 14.8 +- 5.3 us vs OWN 31.2 us], equal to ledger §10; PAPER also prints that later firings do not repeat it | **LAPS DON'T MEET** (no read file below §10).

### B19 · 9/28 20:51 EDT · WHO'S WATCHING · 24 tasks
- **Laid.** [LAID] 24 x 2000 (UTC 00:51:04-18); `witness_obs.py`, `wobs.npz`; $27.60.
- **Used for.** PAPER:189 "Neighbours q1 / q9 respond to q0's state (1.8 / 1.9 times noise ... 10.5 / 22.4 times with q0 in |2>); some far qubits respond to the drive pulse even with q0 at rest (for example q43 at 13.6 times noise ...)".
- **CARRIES:** one firing; the claimed values equal ledger §11 | **LAPS DON'T MEET** (no read file below §11).

### B20 · 9/28 20:58 EDT · THE HEADLINE (q9 alone as witness) · 24 tasks
- **Laid.** [LAID] 24 tasks x 1000/2500, 2 columns (UTC 00:58:59-00:59:09); `witness_headline.py`, `whead.npz`; $25.05.
- **Used for.** PAPER:14 (abstract) "a Rigetti neighbour in |2> pulls a spectator by -62.1 +- 0.6 deg/us"; PAPER:189 "pull -62.1 +- 0.6 deg/us, frequency spread 16 kHz (3.5 sigma); spectator fall time 20.9 us (16.5-29.5) against 24.2 us from q0's own readout; forcing the readout value on the spectator fit costs delta-chi2 = +0.2 [§11]".
- **Lap up.** Ledger §11 only. The firing script (`witness_headline.py`, 44 lines) fires and collects; no analysis code or read file on disk computes -62.1 +- 0.6.
- **n.** 24 tasks, 2 qubits.
- **CARRIES:** one firing: a rung-2 pull [WITNESS] at +-0.6 deg/us, a number with no file below the ledger | **LAPS DON'T MEET** (no read file below §11: PAPER's abstract carries a number no file or script on disk regenerates; PAPER:189's "[TO FILL: task counts and dates]" = 24 tasks, 9/28 20:58 EDT).

### B21 · 9/28 21:26-21:30 EDT · THE ROOMS (full / half room 48; alternating rooms 24) · 72 tasks
- **Laid.** [LAID] wroom 48 x 1000/2500 (UTC 01:26:59-01:27:26), walt 24 x 2500 (01:29:50-01:30:04); `witness_room.py`, `witness_alt.py`; $50.10 + $32.70.
- **Used for.** PAPER:189 "With 0, 54 or 106 other spectators active: spectator fall times 21.0 / 16.0 / 23.0 us against 24.2 / 21.0 / 20.4 us from q0's readout, delta-chi2 +0.2 / +0.9 / +0.1; pull -62.1 / -62.3 / -59.9 deg/us; spread 16 / 18 / 12 kHz [§12]".
- **Lap down.** Ledger §12: the back-to-back room trend was "drift, retracted"; the alternating difference "has a ruler suspect"; ledger §21: "§12-14 Rigetti rooms (+1.1% full, -1.6% middle trio): inside q0's task-to-task flicker. NOT supported."
- **CARRIES:** one firing pair; PAPER:189's values equal ledger §12 | **LAPS DON'T MEET** (no read file below §12).

### B22 · 9/28 21:43 EDT · THE FUCK-UP STACK (rooms rotated, readout-proof; three-body) · 54 tasks
- **Laid.** [LAID] 54 tasks x 1000/1500/4000 (UTC 01:43:39-01:44:08); `fuckup_stack.py`, `stack.npz`; $59.55.
- **Used for.** 7P:102 "the order of looking sets the heat" (ledger §154: "on Rigetti a full room of watchers heats an emitter's start +1.1% and a middle trio cools it -1.6%, rotated and readout-proof").
- **Lap down.** Ledger §21: "§12-14 Rigetti rooms (+1.1% full, -1.6% middle trio): inside q0's task-to-task flicker. NOT supported." (LOOK2: q0's flip error flickers 5.3-9.9 % between tasks seconds apart.)
- **n.** 54 tasks, rooms rotated A,H,F then F,H,A (two rounds).
- **CARRIES:** +1.1 % +- 0.5 (ALONE 3.85 +- 0.36 vs FULL 4.96 +- 0.38) inside a 5.3-9.9 % task-to-task flicker | **LAPS DON'T MEET** (7P:102 counts it in a closed line; the ledger's own §21 marks it not supported).

### B23 · 9/28 21:57 EDT · ONE FOR THE ROAD (edge / middle / alone rooms) · 30 tasks
- **Laid.** [LAID] 30 tasks x 1000/4000 (UTC 01:57:22-35); `edge_room.py`, `edge.npz`; $37.05. Braket spend that night ~$385 (`braket_ledger.json`).
- **Used for.** 7P:102 (the "middle trio cools it -1.6%" leg; ledger §14, §154).
- **Lap down.** As B22: ledger §21 "NOT supported".
- **CARRIES:** -1.6 % (~3 sigma by the ledger) inside the same flicker | **LAPS DON'T MEET** (as B22).

---
## Q. 2026-10-01/02: THE QUBIT RUNS (IBM, 75 jobs; maker's stamps in EDT; every job: kerneled readout, init_qubits on, dynamical decoupling and twirling off, 500-us repetition delay except Q19)

### Q01 · 10/1 23:09 - 10/2 00:05 · RUN 1 (START, WAIT, LOOK) · ibm_kingston, ibm_phoenix, ibm_pittsburgh · 3 jobs
- **Laid.** [LAID] Kingston davi10il7guc73cetuhg (created 23:09:54, ran 23:09:56-23:10:06, 8 s), Phoenix davi1804oijs73e7j3m0 (23:10:24; ran 23:10:26-23:20:16, 9 s), Pittsburgh davi5u492g1c7398uckg (23:20:24; queued 45 min; ran 00:05:32-00:05:46, 8 s). 9 circuits x 839 shots; 9 qubits per chip in three groups of three (Kingston [[82,139,154],[38,92,96],[25,109,135]]; Pittsburgh 12 26 46 103 106 108 112 141 144, blind seed); waits 60 / 240 / 300 us. Freezes a7bad9613d64... (23:09:01; = ledger "a7bad961"), 664bb6f2dd93..., 7e689c65fd0a...; Kingston prediction sealed 23:09:29, SHA-256 d1fff2eb...; Kingston calibration stamp read at fire 2026-10-01T22:25:23-04:00. The run1.py script is not in the release.
- **Used for.** None of the three documents.
- **CARRIES:** one job per chip | not used.

### Q02 · 10/2 00:14 - 00:53 · RUN 2 (START, LOOK, WAIT, LOOK) · Kingston, Phoenix, Pittsburgh · 3 jobs
- **Laid.** [LAID] Kingston daviv3492g1c739900ag (created 00:14:04, ran 00:14:05-00:14:17), Phoenix daviv7o4oijs73e7ktg0 (00:14:23; ran 00:43:08-00:53:16), Pittsburgh davjhgtj371s73dn19rg (00:53:23; ran 00:53:24-00:53:36). 9 x 839, same qubits, waits 60 / 240 / 300 us. Freezes 695d35cea68c... / 80fff8a88646... / f502ca910326... (00:06:50). Kingston prediction SHA-256 124814c7... (25 quantities).
- **Used for.** 7P:62 "values near 0.618 recur (the gap clock 0.60; ...)"; 7P:68 "1.658 / the gap clock read from the other position, 1/0.60 = 1.667".
- **Lap up.** `out/qubit_three_runs/data/reads/run12_kingston.txt`:227 "r2.tau.shared 157.2 +-16.95" [OWN, gap clock] and :236 "r2.tauF.shared 261.6 +-7.783" [OWN, level clock] -> 0.601 +- 0.067; 1/ratio 1.664 +- 0.186 (`lapup.txt` section 8).
- **Lap down.** Both claims print 0.60 / 1.667 without the +-0.07 / +-0.19. The same reader on the other jobs reads 0.68 +- 0.07 (Phoenix, this run), 0.83 +- 0.11 (Pittsburgh, this run), 0.80 +- 0.11 (Boston), 0.61 +- 0.08 (Marrakesh run 5), 0.66 +- 0.10 (Pittsburgh run 9) (ledger §113-§116): the claim quotes the lowest of six. Ledger §105: "The gap fit has three waits and is weakly pinned"; ledger §117 puts the between-chip spread of this ratio inside the bits' own minute-scale jumps.
- **n.** 1 job, 1 chip, 9 qubits, 9 circuits; the Kingston run-2 read scores 25 sealed quantities plus its open lines.
- **CARRIES:** one job, nine qubits: gap/level 0.60 +- 0.07 [OWN/OWN] | **LAPS DON'T MEET** (width dropped; one value of six that span 0.60-0.83).

### Q03 · 10/2 01:03 - 02:00 · RUN 3 (three looks, mirrored twins) · Kingston, Phoenix, Pittsburgh · 3 jobs
- **Laid.** [LAID] Kingston davjm684oijs73e7mf70 (01:03:21; ran 01:03:23-01:03:48, 16 s), Phoenix davjmek92g1c73991i80 (01:03:54; ran 01:20:21-02:00:10, 17 s), Pittsburgh davkgslj371s73dn376g (02:00:18; ran 02:00:20-02:00:44, 16 s). 18 x 839. Freezes c910845457ee... / 451f82705c07... / 143f0e946c50... (00:55:19); Kingston prediction SHA-256 b9e4a901... (53 quantities). Ledger §108 stamps "ALL NINE LANDED (10/2 ~01:50 EDT)"; the last job finished 02:00:44.
- **Used for.** None of the three documents.
- **CARRIES:** one job per chip | not used.

### Q04 · 10/2 08:18 - 08:19 · THE STONE SHOT · ibm_boston · 3 jobs
- **Laid.** [LAID] davq2b492g1c7399bmj0 (created 08:18:52, ran 08:18:55-08:19:06), davq2g5j371s73dnbnk0 (08:19:12; ran -08:19:22), davq2m492g1c7399bn1g (08:19:36; ran -08:19:55). 9 / 9 / 18 circuits x 555 shots; waits 105.024 / 259.968 / 364.992 us; seed 20261002; freezes 8dbb63c3afd0... (08:18:46), aac02817be73... (08:19:07), 1b4f0de657cc... (08:19:31); table hash 2308807b... in each freeze; 6 + 6 + 12 = 24 s. **Ledger §112 stamps the fire "10/2 ~10:15 EDT"; the maker's stamps put it at 08:18:52-08:19:55, before run 5.** Code not in the release.
- **Used for.** None of the three documents (kept off every published page, §110-§111).
- **CARRIES:** three jobs on one chip | not used.

### Q05 · 10/2 08:47 · RUN 5 (THE NONE SHAPE) · ibm_marrakesh · 1 job
- **Laid.** [LAID] davqfsil7guc73cfbr60 (created 08:47:46, ran 08:47:48-08:47:59, 7 s). 36 circuits x 212 shots (three copies of 3 starts x 4 waits: none, 60, 240, 300 us); bits 12 26 46 103 106 108 112 141 144 (blind seed); freeze 9fa6fe7cc3b1...b267c5 (08:47:30; = ledger "9fa6fe7c...267c5").
- **Used for.** PAPER:61 (Table 1) and PAPER:134 "start 1, -0.0480 +- 0.0071 (ibm_marrakesh) ... start halfway, -0.0163 +- 0.0051 ... start 0, +0.0018 +- 0.0029".
- **Lap up.** `none_arm_three_chips.txt`:4-6 (re-run identical): "none.OFF 0.0018 +-0.0029", "none.MID -0.0163 +-0.0051", "none.ON -0.0480 +-0.0071" [OWN, no laid wait between the two looks].
- **n.** 1 job, 1 chip, 9 qubits; 36 circuits; the read prints 15 lines per chip + 27 per-bit values.
- **CARRIES:** one job, nine qubits: second look minus first [OWN] -0.048 +- 0.007 from |1> | **LAPS MEET**.

### Q06 · 10/2 08:53 - 09:11 · RUN 6 (burned) · ibm_pittsburgh · 1 job
- **Laid.** [LAID] davqiodj371s73dncang; freeze d107d940b984... (08:53:40); 9 circuits planned; no payload, no results; the maker cancelled it at the 3-s cap after an 18-min queue; 2 s billed (ledger §115).
- **Used for.** Counted in "72 jobs fired / 71 landed" (§141); no number.
- **CARRIES:** nothing returned | not used.

### Q07 · 10/2 09:13 - 09:14 · RUN 9 (Pittsburgh, run-5 shape) and RUN 7 (Kingston, the none arm) · 2 jobs
- **Laid.** [LAID] Run 9 davqs304oijs73e81gig (created 09:13:48, ran 09:14:12-09:14:28), **36 x 212**, freeze b7a94aef9c34... (09:13:33). Run 7 davqseql7guc73cfc7ug (09:14:35, ran 09:14:36-09:14:53), **9 x 212** (the none arm only, 3 copies of 3 starts), freeze 16d2e4b164f3... (09:13:33). Kingston bits 25 38 82 92 96 109 135 139 154.
- **Used for.** PAPER:61 Table 1 "Two readouts, no delay (run5/run9/run7.py) | ... | 36 x 212 | 9 each"; PAPER:134 "-0.0272 +- 0.0060 (ibm_pittsburgh), -0.0204 +- 0.0053 (ibm_kingston)".
- **Lap up.** `none_arm_three_chips.txt`:27 "none.ON -0.0272 +-0.0060" and :48 "none.ON -0.0204 +-0.0053" (re-run identical); `run9_pittsburgh.txt` identical.
- **Lap down.** Table 1 lists run 7 as 36 x 212; the laid job is 9 x 212.
- **n.** 2 jobs, 2 chips, 9 qubits each.
- **CARRIES:** one job per chip, nine qubits: the no-wait second-look step [OWN] | **LAPS MEET** for PAPER:134; **DON'T MEET** for PAPER:61's circuit count of run 7.

### Q08 · 10/2 09:18 - 09:19 · RUN 10 (short-wait column again) · Pittsburgh, Kingston · 2 jobs
- **Laid.** [LAID] Pittsburgh davqu5492g1c7399clc0 (created 09:18:12; queued; ran 09:18:57-09:19:09), Kingston davquks92g1c7399cls0 (09:19:15; ran 09:19:16-09:19:22). Each **9 circuits x 195 shots** (3 copies x 3 starts = 585 shots per start); freezes 54d16b5f22f5... / ea05e0d1f749... (09:17:58).
- **Used for.** PAPER:62 Table 1 "[TO FILL] x 585 per start" (= 9 x 195); PAPER:242 "Single-qubit levels after a 60-us delay change by 0.2-0.4 within 4.5 minutes in both directions (rms over nine qubits 0.157 overnight and 0.164 in 4.5 minutes on ibm_pittsburgh, 0.141 overnight on ibm_kingston)".
- **Lap up.** `short_wait_across_time.txt`:12, :15, :45 (re-run identical). [LAID] Pittsburgh run 9 began 09:14:12 and run 10 at 09:18:57: 4 min 45 s apart; "overnight" = run 2 (00:53:24) to run 9: 8 h 21 min (Kingston: 00:14:05 to 09:19:16).
- **n.** 2 jobs (+ the run-2 and run-9 jobs they are read against), 9 qubits per chip.
- **CARRIES:** jobs minutes apart on the same nine qubits: rms level change 0.157 / 0.164 / 0.141 [OWN at a laid 60-us wait] | **LAPS MEET**.

### Q09 · 10/2 09:30 - 09:59 · THE JUMP RUN · ibm_pittsburgh · 8 jobs (runs 11-18)
- **Laid.** [LAID] davr44il7guc73cfcing, davr60il7guc73cfcmc0, davr7stj371s73dnd6sg, davr9ok92g1c7399d9r0, davrbktj371s73dnddgg, davrdgtj371s73dndfdg, davrfcil7guc73cfd4pg, davrh8o4oijs73e82gkg; created 09:30:59, 09:34:58, 09:38:59, 09:42:58, 09:46:59, 09:50:59, 09:54:59, 09:58:59; 5 s each. 10 circuits x 400; all 156 qubits; waits none / 60 / 240 / 300 us; freeze 38dbbc67fa53... (09:26:33, one freeze for all 8).
- **Used for.**
  - PAPER:14 "a qubit prepared in |1> loses per readout the population of 3.2 to 4.3 us of its own decay (eight jobs)"; PAPER Table 2 rows (PAPER:121-123), PAPER:112, PAPER:128 (ii), PAPER:242 (decay-time scatter 1.35x; 25 qubits; +0.34 / +0.71).
  - 7P:62 "4/3 and 3/4: the qubit's two clocks sit at ... 0.775 +- 0.009 (eight reads) of each other."
  - 7P:50 / LAWS:35 "3.5 +- 0.2 us" through ledger §135 ("immediate 3.2-4.3").
- **Lap up.** `jump_rerack.txt`:7-14 none_ON per-read medians 3.88, 4.26, 3.31, 3.20, 3.68, 3.20, 3.58, 3.58 us; :16 "none_ON 3.23 [2.36 4.97]"; :18-19 fit_ON 8.27 [3.62 12.85], fit_MID 6.12 [-0.07 17.24] (all re-run identical) [OWN, converted with each qubit's fitted decay].
- **Lap down.**
  - 0.775 +- 0.009: **no read file prints it.** `jump_run.txt`, `jump_rerack.txt` and `jump_cube.txt` (re-run identical) do not hold it; the eight per-read middles "0.750 0.774 0.806 0.730 0.799 0.782 0.790 0.767" exist only at ledger:1831 (§120) and in TRIANGLE_OF_FUCKUPS. Their mean is 0.775 and sd/sqrt(8) is 0.009 (so the width is a job-scatter width), but the computation that made the middles is not in the release.
  - Per-look 3.2-4.3 us: the jump run prints per-job medians of a no-wait second-look drop [OWN], 3.20-4.26; the "3.5 +- 0.2" of 7P:50 is not among them (see Q14).
- **n.** 8 jobs, 1 chip, 156 qubits (147 readable in all 8); 10 circuits; three reads print several hundred numbers (4 look-length estimators x 8 reads, three thirds, arrow table of 48 cells, rows).
- **CARRIES:** eight jobs on one chip: per-job no-wait look cost 3.2-4.3 us [OWN], decay-time wander between jobs | **LAPS MEET** for PAPER:14 and Table 2; **DON'T MEET** for 7P:62's 0.775 +- 0.009 (no read file holds it).

### Q10 · 10/2 10:08 - 10:18 · THE TAIL RUN (3 jobs) and THE LONE LOOK (1 job) · ibm_pittsburgh
- **Laid.** [LAID] Tail runs 21-23: davrluil7guc73cfdfa0, davrnqs92g1c7399duc0, davrpmql7guc73cfdmkg (created 10:08:58, 10:12:59, 10:16:59), 11 x 400, freeze 0214371e97f3... (10:08:42). Lone run 31: davrqgtj371s73dne4v0 (created 10:18:43, ran 10:18:45-10:18:56), 11 x 400, freeze 2d76621f2225... (10:18:38). All 156 qubits; waits none / 6.72 / 19.97 / 59.97 / 299.97 us.
- **Used for.** 7P:62 "the halfway state's early decay clock at 0.59 of the |1> state's (123 / 208 us, one read)" and "the qubit's two clocks sit at 0.756 (one read, no earlier look)"; PAPER:64-65 (Table 1), PAPER:124 (tail 3.63 us), PAPER:242 ("208 us over the first 6.7 us and 260, 253 and 275 us"; "0.803 ... and 0.686").
- **Lap up.** `lone_vs_tail.txt`:16 "NO earlier look: 208 260 253 275" and :38 "NO earlier look: 123 190 283 277" (re-run identical) [OWN stretch clocks, middle bits, no width printed]: 208/275 = 0.756, 123/208 = 0.591 [derived].
- **Lap down.** Both claimed ratios come from the lone job (one job); the read prints no widths for the middle-bit stretch clocks. The same read's bit-by-bit column for the |1> state's first stretch over its own 60-300-us clock is 0.803 (:21), not 0.756; ledger §121(3): "the two ways of pooling disagree on which is shorter: unsettled". 7P:62 now words both as one read, which is what they are.
- **n.** 1 lone job (+3 tail jobs for the "one earlier look" rows), 1 chip, 156 qubits; 11 circuits each.
- **CARRIES:** one job: the |1> state's first-stretch clock 208 us and the halfway state's 123 us [OWN], no widths | **LAPS MEET** on the printed lines (one read, as worded); the second pooling in the same file (0.803) is not quoted beside 0.756.

### Q11 · 10/2 11:02 - 11:48 · THE HALF-PUSH RUN (3 jobs) and the maker's look length (a configuration read) · ibm_pittsburgh
- **Laid.** [LAID] davsf8k92g1c7399fa50 (created 11:02:58; queued 36 min; ran 11:38:46-11:39:32), davt0f84oijs73e84t50 (11:39:41; ran -11:41:04), davt2b04oijs73e8504g (11:43:41; ran -11:48:50); 14 x 360; freeze 8018d3c258f9... (11:00:33). The maker's stated measurement duration was read at **11:02:53** from the chip's published properties: `maker_look_length_pittsburgh.json`, 156 values, every one 2.18 us.
- **Used for.** 7P:50 "The maker's stated look: 2.18 us."; LAWS:34 "the maker's stated 2.18 us"; PAPER:40, PAPER:108, PAPER:118 (Table 2 row 1).
- **Lap up.** `maker_look_length_pittsburgh.json`: min = max = 2.18 us over 156 qubits [LAID]. (`readclose.py` prints "the maker's stated length of one look on this chip (read 11:02): 2.180 us" as a fixed string, not read from the file.)
- **n.** one configuration read; the half-push jobs themselves feed no claimed number.
- **CARRIES:** the maker's published 2.18 us, read once at 11:02:53 [LAID] | **LAPS MEET**.

### Q12 · 10/2 11:53 · THE SIDES RUN · ibm_pittsburgh · 1 job (2 frozen, not fired)
- **Laid.** [LAID] davt6tlj371s73dngc70 (created 11:53:26, ran 11:53:28-11:59:57), 19 x 360, freeze 9c65bb714b80... (11:53:16).
- **Used for.** None of the three documents.
- **CARRIES:** one job | not used.

### Q13 · 10/2 12:05 · THE TURNS RUN · ibm_pittsburgh · 1 job (2 pulled)
- **Laid.** [LAID] davtcjc92g1c7399gm70 (created 12:05:33, ran 12:05:35-12:05:55), 20 x 330, freeze 9cde18ebf691... (12:01:07); reads 2-3 pulled (`out/qubit_fifth_run/pulled/`).
- **Used for.** None of the three documents (its read is in `hold_run.txt`:36-43).
- **CARRIES:** one job | not used.

### Q14 · 10/2 12:07 - 12:16 · THE HOLD RUN · ibm_pittsburgh · 3 jobs (runs 71-73)
- **Laid.** [LAID] davtdgtj371s73dngms0, davtfd04oijs73e85n2g, davth95j371s73dngub0; created 12:07:31, 12:11:32, 12:15:32; ran 12:07:32-12:07:54, 12:11:33-12:12:44, 12:15:33-12:16:30; 11 circuits x 330; all 156 qubits (145 / 139 / 139 readable); every arm START ON (two arms OFF), 300 us laid, last look; freeze 49b3042018b1... (12:07:11).
- **Used for.**
  - 7P:56 "the hold run's three reads give +2.17 +- 0.17"; 7P:69 "2.17 +- 0.17 (hold run, three reads)".
  - 7P:85 "on the mean over qubits, three ways of parking close to each qubit's own decay bookkeeping within 0.002 (+0.0017 +- 0.0013, +0.0020 +- 0.0015, +0.0014 +- 0.0015; single qubits scatter about +- 0.02 ...)"; 7P:102 "the park".
  - 7P:62 "a Pittsburgh qubit keeps 0.313-0.335 of itself after 300 us" (the 0.335).
  - LAWS:25 "MEASURED: a qubit parked in |0> doesn't age -- per-qubit bookkeeping closes to 0.002 across three parking schemes."
  - PAPER:66, PAPER:130 (repeated readouts), PAPER:140 "Done qubit by qubit, all three arms close to bookkeeping within 0.002 [§135]", PAPER:146-148 (Table 3), PAPER:152, PAPER:154 "within 0.002 qubit by qubit [§135]", PAPER:217 (Table 6 hold row), PAPER:128 (i).
  - 7P:50 / LAWS:35 "3.5 +- 0.2 us" (ledger §135: "pile-up 3.5 +- 0.2 per look over 3 and 9 looks").
- **Lap up.**
  - `hold_run.txt` (re-run identical): :13 "1 look on the way ... all: -0.0007 +- 0.0009"; :14 "3 looks ... -0.0131 +- 0.0017"; :15 "9 looks ... -0.0289 +- 0.0014"; :6 "3 looks ... bit by bit: 311.5"; :7 "9 looks ... bit by bit: 327.0"; :21-23 median-qubit park rows (+0.0065 +0.0054 +0.0086 / ...).
  - `internal/reads_new/hold_crossing.txt`: OFF start, ten pushes, mean over qubits "+0.0190 +- 0.0030 +0.0251 +- 0.0029 +0.0210 +- 0.0028 | all +0.0217 +- 0.0017" [OWN; LAID 30-us intervals].
  - `internal/reads_new/park_per_qubit.txt` (three-read means): parked once +0.0017 +- 0.0013, quarters +0.0020 +- 0.0015, tenths +0.0014 +- 0.0015 [OWN; intervals LAID]; **share of qubits within 0.002: 0.055 +- 0.010, 0.054 +- 0.009, 0.049 +- 0.009**; per-qubit quartiles about +-0.02.
  - `discarded_hold.txt`:144 "ON|N0 ... +0.3354 (0.0013)" (the 0.335; 300 us laid).
  - Per look from :6-:7: (311.5 - 300) / 3 = 3.8 us, (327.0 - 300) / 9 = 3.0 us [OWN, derived].
- **Lap down.**
  - LAWS:25 "per-qubit bookkeeping closes to 0.002": per qubit, about 5 % of qubits close within 0.002; the **mean over qubits** closes within 0.002. Same for PAPER:140 and PAPER:154 ("qubit by qubit ... within 0.002"; the paper was drafted at 12:54, before §180 found this at 13:29). 7P:85 already says "on the mean over qubits".
  - 3.5 +- 0.2 per look: this firing reads 3.8 (3 looks) and 3.0 (9 looks) us per look, and 3.0-6.7 / 4.0-4.2 on the median qubit; no read or script computes +-0.2 (PAPER:126 marks it [TO FILL]).
  - "never given back" (7P:50): this firing's one look at 150 us leaves the 300-us level at -0.0007 +- 0.0009 and adds no time bit by bit ("bit by bit: 300.0", :5): the opposite reading to the give-back firing (Q18).
  - 0.335 is the level after a laid 300 us: the 1/pi landing of 7P:62 is set by the laid wait chosen.
- **n.** 3 jobs, 1 chip, 139-145 readable qubits; 11 circuits; hold_run.txt prints about 45 numbers, discarded_hold.txt about 200.
- **CARRIES:** three jobs, one chip: the OFF-start ten-push crossing +0.0217 +- 0.0017 [OWN; LAID 30-us intervals]; the park as a mean over qubits within 0.002; per-look costs 3.0 / 3.8 us | **LAPS MEET** for 7P:56, 7P:69, 7P:85; **DON'T MEET** for LAWS:25, PAPER:140, PAPER:154 (per qubit), for the +-0.2 of 7P:50 / LAWS:35, and for "never given back".

### Q15 · 10/2 12:25 · THE STOPWATCH · ibm_pittsburgh · 1 job (of 3 planned)
- **Laid.** [LAID] davtm5ql7guc73cfgtlg (created 12:25:59, ran 12:26:00-12:29:29), 12 x 300; roles from the chip's static configuration read at fire (176 links): 39 emitters, 86 witness clocks, 31 far clocks (`witness_roles.json`); emitter ON for 0 / 20 / 40 / 60 us laid, then X to |0> for the rest of a 60-us window; freeze a7f440f5c781... (12:25:47); runs 82-83 frozen, never fired. Fired before review (ledger §134, owned).
- **Used for.** 7P:85 "an emitter parked after 20 / 40 us reads 0.0648 / 0.1348 against 0.0647 / 0.1346 (one read)"; 7P:102 "the park"; PAPER:67, PAPER:150, PAPER:160-172 (Table 4; 35.6 / 48.3 us; 4.5 kHz; being watched -0.0029 +- 0.0086; the model closure -1.4 +- 4.8 deg, contrast 1.02 +- 0.035 / 0.90 +- 0.03 from `stopwatch_triangle.json`).
- **Lap up.** `witness_run.txt`:21 "parked after 20 (reads what had already gone): 0.0719 0.0576   parked after 40: 0.1287 0.1409" (two hand circuits; re-run identical) -> means 0.06475 / 0.13480 [derived]; bookkeeping with the yardstick 0.7896 (:19, median emitter, neighbours OFF): (1 - q20) q40 = 0.06469, (1 - q40) q20 = 0.13468 [OWN; LAID 20/40-us intervals] (`lapup.txt` section 5). `reads_new/park_per_qubit.txt` prints the same ruler row as 0.0647 / 0.1347; 7P:85 prints 0.1346.
- **Lap down.** The claim's agreement is at 1e-4; the read's own two circuits of each quantity differ by +0.0143 and -0.0122. Per emitter (34 readable), the same bookkeeping leaves +0.0014 +- 0.0029 and +0.0048 +- 0.0040 (quartiles [-0.008, +0.010], [-0.015, +0.026]; `park_per_qubit.txt` section 2). The 1e-4 match is a median-level against a median-yardstick at one read. `stopwatch_triangle.json` has no producing script in the release (PAPER open question 4).
- **n.** 1 job, 1 chip, 39 emitters / 68 readable witnesses; 12 circuits; witness_run.txt prints about 35 numbers.
- **CARRIES:** one job: parked-emitter levels within bookkeeping on the median emitter, and per emitter within +0.0014 +- 0.0029 / +0.0048 +- 0.0040 [OWN; LAID]; witness turns 33.9 / 28.1 / 23.9 deg per 20 us [WITNESS] | **LAPS DON'T MEET** for 7P:85's precision (1e-4 claimed; the read's two circuits differ by 1.4e-2); MEET for PAPER Table 4 values.

### Q16 · 10/2 13:09 / 14:26 / 14:27 · THE PUSH RUN · ibm_pittsburgh · 3 jobs (runs 91-93)
- **Laid.** [LAID] davuanc92g1c7399i8kg (created 13:09:49, ran 13:09:51-13:13:43), davveh04oijs73e88tsg (14:26:12; ran 14:26:14-14:26:29), davvf7c92g1c7399k1h0 (14:27:41; ran 14:27:43-14:28:21): read 1 ran 76 minutes before reads 2-3. 14 circuits x 400: starts OFF / ON / halfway x (no X, 2 X, 10 X back to back, 10 X with 30.016 us before each, laid 300.16 us) + ON and OFF idle 299.968 us; all 156 qubits (141 readable); circuit order seed 20261911; freeze 6d9e6588cecc... (13:09:17); payload sha256 59141e1f... / 686b0f95... / 4982da70....
- **Used for.**
  - 7P:56 "Pittsburgh +2.00 +- 0.16 % (push run, three reads ...)"; "Prepared |1>: +0.05 +- 0.13"; idle "-0.43 to +0.26 % per 300 us"; "Leakage is capped at 0.26 +- 0.12 % per push, against 2.96 +- 0.28 % per push ..."; "Three-chip mean 2.54 %". 7P:69 "Pittsburgh's crossing, 2.00 +- 0.16 (push run, three reads)". 7P:62 "0.313" (the 300-us level).
  - LAWS:27 "+2.0 to +2.9 % on three chips"; LAWS:17 "on IBM, shots don't talk (-0.002 +- 0.002)".
  - PAPER:14, 68, 216 (Table 6), 223 ("438 qubit-jobs ... median +0.0133, 63% ... per-job medians +0.010 / +0.012 / +0.019 [§151]"), 229 (Table 7), 233 ("1.48 +- 0.14 deg ... 0.26 +- 0.12% per gate ... 0.0258 +- 0.0024 ... 0.128 +- 0.012"), 236-240 (controls; "-0.002 +- 0.002 over three jobs [§151]").
- **Lap up.**
  - `close_push.txt` (re-run identical): :4 "+0.0174 +- 0.0028 +0.0213 +- 0.0030 +0.0213 +- 0.0023 | all +0.0200 +- 0.0016" [OWN one-exponential bookkeeping from :12; LAID 30-us intervals]; :7 "all +0.0005 +- 0.0013"; :11 "all -0.0001 +- 0.0006"; :12 "all +0.3131 +- 0.0013".
  - From :2, :3, :5, :6: shortfall 1.483 deg (redraw sd 0.133), count-growing part 0.256 % (sd 0.115) per push, upper edge 0.485 %; halfway start predicted 0.0259 (2 X) and 0.1279 (10 X) against -0.0262 / -0.1138 measured (`lapup.txt` section 2).
  - `reads_new/leak_tls_fit.txt`: 2.958 +- 0.279 % per laid push from the reviewer's two model rows (numbers at ledger:1953) fitted to these jobs.
  - Ledger-only lines, re-derived here from the raw jobs (`lapup_push_bits.txt`): 438 bit-reads, mean +0.0200, median +0.0133, 63 % above zero, per-read medians +0.0103 / +0.0119 / +0.0189 (PAPER:223 meets); next-shot lean of the OFF spread arm +0.0009 +- 0.0040 / -0.0069 +- 0.0039 / -0.0010 +- 0.0038, mean -0.0023 +- 0.0023 (the "-0.002 +- 0.002" meets; this ruler reproduces the replication reads' OFF and ON spread-arm lean lines exactly; their ON-idle line keeps a slightly different set of bits: +0.0065 here vs +0.0077 printed on Marrakesh, +0.0134 vs +0.0136 on Kingston).
- **Lap down.**
  - LAWS:17 "on IBM, shots don't talk": the read is one arm (OFF spread) on one chip at a laid 500-us spacing. In the same jobs the ON-idle arm leans +0.0120 +- 0.0045 and +0.0076 +- 0.0042 (runs 92, 93); the replication reads print +0.0077 (Marrakesh) and +0.0136 (Kingston) for that arm; and IBM's own 9/28 jobs at 20-us spacing hold carried off-line population into the next shot (B02, B03). The law is wider than the read.
  - 2.96 % rests on rows from a simulation that is not on disk (7P:56 says so).
- **n.** 3 jobs, 1 chip, 141 qubits; 14 circuits; close_push.txt prints 12 quantities.
- **CARRIES:** three jobs, one chip, 14 arms: OFF spread arm +0.0200 +- 0.0016 against one-exponential bookkeeping [OWN; LAID 30-us intervals] (job values +0.0174 / +0.0213 / +0.0213), ON +0.0005 +- 0.0013, back-to-back mirror +-0.023, shortfall 1.48 deg and 0.26 % per push | **LAPS MEET** for 7P:56, 7P:69, LAWS:27 (Pittsburgh leg), PAPER:216-240; **DON'T MEET** for LAWS:17 (one arm, one chip, 500-us spacing, read as all of IBM).

### Q17 · 10/2 13:13 submit, 14:25 - 14:28 run · LOOK-TIME · ibm_pittsburgh · 3 jobs (runs 101-103)
- **Laid.** [LAID] davucks92g1c7399iak0 (created 13:13:55; **queued 71 min; ran 14:25:04-14:25:23**), davveo2l7guc73cfjjtg (14:26:40; ran 14:26:42-14:26:59), davvfjs92g1c7399k200 (14:28:31; ran 14:28:33-14:28:54): the three reads ran within 3 min 50 s. 14 circuits x 400: emitters held in |1>; every wired qubit a free Ramsey clock (sx, read on two axes); far qubits looked at 3 or 9 times back to back inside the clocks' window (barriers); laid delay arms 0 / 30 / 60 / 120 us. Roles by seed 20261810 (`looktime_roles.json`: same 39 / 86 / 31 as Q15); 83 readable clocks. Freeze 5f17cd0a23a4... (13:09:17). Static configuration timing saved at fire (`pittsburgh_config_timing.json`: dt 4 ns; one measurement group of all 156 qubits).
- **Used for.**
  - 7P:50 "Spectator qubits ticking inside the chip: 2.37 +- 0.03 us ... Witness over maker 1.087 (12/11 = 1.091) ... qubit over witness 1.477"; 7P:68 (1.087; 1.477); 7P:85 "The look stretches the qubit 1.48x against its witnesses".
  - 7P:62 "a free-running spectator keeps 0.92 of its coherence (0.9209 +- 0.0040) through three looks at other qubits"; "the spectator's free precession turns 3.144 +- 0.076 degrees per microsecond"; "0.921 +- 0.004, 0.826 +- 0.005, 0.760 +- 0.006 (11/12, 10/12, 9/12 ...) through 3 looks, 9 looks and 30 us".
  - LAWS:10-11 (the three coherences); LAWS:34-35 "the spectator qubits' 2.37 +- 0.03 us".
  - PAPER:69, 110, 119-120 (Table 2), 132 (ratios), 174.
- **Lap up.** `close_looktime.txt` (re-run identical): :6 "+2.4718 +- 0.0512 +2.2802 +- 0.0464 +2.3578 +- 0.0659 | all +2.3699 +- 0.0318"; :2 "all +2.3494 +- 0.0650" (block of 3); :5 "+0.9209 +- 0.0040"; :9 "+0.8256 +- 0.0052"; :10 "+0.7604 +- 0.0057"; :11 "+3.1444 +- 0.0760". Derived (`lapup.txt` section 3): witness / maker = 1.0871 +- 0.0146 (shot) or +- 0.0255 (job scatter); 3.5 / 2.3699 = 1.477 +- 0.087 (with the ledger's +-0.2).
- **Lap down.**
  - What the 2.37 is: each spectator's phase across the readout block, converted to microseconds on that spectator's own phase-versus-**laid**-delay curve (aT + bT^2 fitted on the 30- and 60-us delay arms; `readclose.py`; PAPER:110). It is a WITNESS phase expressed in LAID units: anything that moves a spectator's frequency during the block (the whole chip is one measurement group) reads as time, and whatever the scheduler places between back-to-back looks is inside it (not read; PAPER:272(d)).
  - Width: the three jobs scatter more than their shot widths (sd 0.096 us; job-scatter width 0.056, against the quoted 0.032). 7P quotes the block of 9; the block of 3 reads 2.3494 +- 0.0650 (job sd 0.168).
  - [LAID] PAPER:69 and the read's header give "13:13 / 14:26 / 14:28": 13:13 is the submit stamp of read 1, which ran at 14:25:04.
  - 3.144 deg/us is in the drive frame (PAPER:174 says so; 7P:62 does not): each spectator's offset from its drive frame plus its emitter's pull, i.e. 8.73 kHz or 0.0549 rad/us; the pi landing lives in the degree-per-microsecond unit pair. The three jobs read 3.03 / 3.06 / 3.34 (sd 0.17).
  - The countdown 0.921 / 0.826 / 0.760 mixes two arms: 3 looks, 9 looks, and a laid 30-us delay with no looks.
  - "One readout look, timed from three positions" (7P:50; LAWS:34): the three numbers come from three different firings at three times: the maker's figure read at 11:02:53 (Q11), this firing at 14:25-14:28, and the qubit's own figure from ledger §135 built on the jump (09:30-09:59), hold (12:07-12:16) and give-back (14:25-14:30) jobs. No single job times one readout three ways.
- **n.** 3 jobs, 1 chip, 83 spectators; 14 circuits; close_looktime.txt prints 14 quantities.
- **CARRIES:** three jobs, one chip: spectator phase per look in laid-delay units 2.37 +- 0.03 (shot) / +- 0.06 (job scatter) [WITNESS in LAID units]; spectator coherence kept 0.921 / 0.826 / 0.760 [WITNESS] | **LAPS MEET** for the printed values (7P:62, LAWS:10-11, PAPER:174); **DON'T MEET** for "one readout ... timed from three positions" (three firings) and for "+- 0.03" as the look's width (job scatter +- 0.06).

### Q18 · 10/2 14:25 - 14:30 · THE GIVE-BACK RUN · ibm_pittsburgh · 3 jobs (runs 111-113)
- **Laid.** [LAID] davve7g4oijs73e88t6g (created 14:25:34, ran 14:25:35-14:26:00), davvevs92g1c7399k180 (14:27:11; ran -14:27:30), davvfslj371s73dnk2q0 (14:29:06; ran -14:30:05). 6 circuits x 1000: ON, laid 300 us, last look; one look at 0 / 150 / 270 us or none, + two reference circuits; 148 readable qubits; freeze 214c5cfcec25... (13:09:17).
- **Used for.** 7P:50 "The looked-at qubit's own ageing: 3.5 +- 0.2 us (3.5 / 3.6 / 4.1 wherever the look sits), never given back."; PAPER:70, PAPER:125 (Table 2: 3.5313 +- 0.8737 / 3.5569 +- 0.9309 / 4.0507 +- 0.9397), PAPER:128 (i).
- **Lap up.** `close_giveback.txt` (re-run identical): :2 "+6.5260 +- 1.5081 +1.0228 +- 1.4946 +3.0449 +- 1.5366 | all +3.5313 +- 0.8737"; :4 "... | all +3.5569 +- 0.9309"; :6 "... | all +4.0507 +- 0.9397" [OWN, us of the qubit's own decay by the end].
- **Lap down.** 7P:50 prints 3.5 / 3.6 / 4.1 without the +-0.9. The three jobs read 6.53 / 1.02 / 3.04, 3.45 / 1.31 / 5.91 and 4.54 / 0.73 / 6.88 us (job sd 2.3-3.1 us; job-scatter widths 1.3-1.8 us, about twice the shot widths); job 112 reads near 1 us at all three positions. "Never given back" sits against the hold run's one-look arm (Q14), which reads no added time.
- **n.** 3 jobs, 1 chip, 148 qubits; 6 circuits; 7 printed quantities.
- **CARRIES:** three jobs, one chip: a lone look's cost by the end 3.5 / 3.6 / 4.1 +- 0.9 (shot) / +- 1.3-1.8 (job scatter) us [OWN] | **LAPS DON'T MEET** (widths dropped; "never given back" against Q14's lone-look arm).

### Q19 · 10/2 14:30 - 14:38 · THE BAND (the 9/28 echo again) · ibm_marrakesh · 24 jobs (runs 210-237)
- **Laid.** [LAID] 24 jobs created 14:30:18-14:38:26 (davvgelj371s73dnk40g ... davvk8g4oijs73e897q0), each 1 circuit x 1500 shots on the echo's 78 even qubits; repetition delay **20 / 50 / 100 / 2000 us** (not 500); E0 and E1 as separate jobs, 8 jobs per read, 3 reads; freeze 7b5b191542ba... (13:09:17); 2 or 5 s each.
- **Used for.** None of the three documents. It is the re-fire of the band 7P:62 quotes from 9/28 (B02).
- **Lap up.** `out/qubit_fifth_run/data/reads/band.txt` (the band's own code, checked to reproduce 9/28): at cutoffs 0.62-0.65, R^2 0.024-0.025 (read 1), 0.000-0.021 (read 2), 0.004-0.107 (read 3); ledger §140 "Not there, three reads."
- **CARRIES:** three reads x 8 jobs, one chip: no band at 0.62-0.65 | not used (and not set beside the 9/28 band it re-fires).

### Q20 · 10/2 16:05 submit, 17:41 run · THE NO-NAME SHOT · ibm_pittsburgh · 1 job (of 3 planned)
- **Laid.** [LAID] db00t8k92g1c7399m6hg (= ledger §145; created 16:05:54, **queued 95.8 min, ran 17:41:43-17:42:04**); 21 circuits x 216 shots; all 156 qubits (150 readable; 75 witness-emitter pairs on 35 emitters); arms: lone looks OFF / ON; ON left alone 10 / 30 / 90 / 300 us; OFF left alone 300 us; ten pushes with OFF/ON stretches 30/30, 10/30, 90/30, 30/10, 30/90 (laid 30.016-us grid), 30/30 + one more push, ON-start 30/30 and + one, 2 and 6 pushes; witness arms (frame-held spectators) on two hands; freeze ce322e777188...f55b15 (16:05:31; = ledger "ce322e77...5b15"); payload sha256 3dd3c3fa...; runs 122-123 frozen, never fired.
- **Used for.**
  - 7P:14 "measured against each stretch's own decay it drops below zero (-0.12 / -0.58 / -0.97 % with pushes) ... (a qubit left in |0> for 300 us gains +0.02 +- 0.15 %) ... One variant (10-us |1> stretches) reads +1.7 +- 0.6 % ... one arm in ten (7.6 % family-wise)".
  - 7P:56 "The short-time and long-time decay sit 2.2-2.7 % apart at every push count -- the size of the crossing"; the idle arm; the 10-us variant; 7.6 %.
  - 7P:68 "The spectator turns 16.9 degrees per 30-us |1> stretch."; 7P:69 (the 16.9 against the golden climb 17.03).
  - 7P:75 "the crossing lands below zero, deeper with every push added: -0.12, -0.58, -0.97 %".
  - LAWS:28-30 (idle arm; "one arm in ten (7.6 % family-wise)"); LAWS:36 "2.2-2.7 % apart at every push count"; LAWS:40 "a spectator qubit, after everything we know how to cancel is cancelled, keeps a leftover of +0.6 degrees."
  - PAPER:14, 71, 176-187 (Table 5), 237, 238(f), 242, 246-263 (Table 8), 269.
- **Lap up.** `noname_read1.txt` (re-run identical; and §181's reader copy reproduces all 83 lines): :10 "ruler: OFF left alone 300 us (level) +0.0002(0.0015)"; own-interval :58 N2 "-0.0012(0.0034)", :62 N6 "-0.0058(0.0052)", :26 A30_30 "-0.0097(0.0051)"; one-clock :59 "+0.0245", :63 "+0.0207", :27 "+0.0126" -> gaps 2.57 / 2.65 / 2.23 % [OWN short vs OWN long]; :38 "A30_10: minus each-stretch-own-ruler book +0.0170(0.0064)" -> z 2.656, two-sided p 0.0079, Sidak over ten 0.0763 (7.6 %); :77 "coupling read by the witness (deg per 30-us ON stretch, median) +16.9023(1.8085)"; :70 "witness half-sum, its own leftover (deg) +0.5963(4.5115)".
- **Lap down.**
  - 7P:14 and 7P:75 print -0.12 / -0.58 / -0.97 % without their widths (+-0.34 / +-0.52 / +-0.51): -0.35, -1.12 and -1.90 widths from zero. "Lands below zero, deeper with every push" is not what 0.35 widths at 2 pushes says. PAPER:14 prints the widths.
  - "2.2-2.7 % ... the size of the crossing": in this job the ten-push one-clock crossing is +1.26 +- 0.32 %, smaller than its own 2.2 % gap; the "size" matched is the push run's +2.00 (Q16, other jobs, three hours earlier). PAPER:259 itself: "we do not compare across jobs".
  - "one arm in ten": the job prints 83 quantities; outside the ten-arm family, and leaving aside the ruler-shape and one-clock lines (non-zero by construction), six more sit beyond two widths (off-both A30_30 +0.0025(8) z 3.1, B30_30f z 2.5, A30_90 z 2.4; across-the-line B30_30f z 2.1; emitters started OFF -0.0216(102) z -2.1; the witness hand X for ON-started emitters 3.3 widths from its model). The 7.6 % covers the ten.
  - 16.9 deg (7P:68, 7P:69): the read line is a **fitted model coupling** (median over pairs of the own-fading witness fit), and the claim drops its +-1.81. The same job read without that model, as the witness's half-difference per laid ON stretch, gives 8.24 +- 0.48 deg (median 8.01) (`THREE_SEATS_RUN121_20261003.md`:50-51); the per-pair fit "lands more than 10 deg from its full-data value in more than a third of shot resamples for 53 of 75 pairs" (:247). "The spectator turns 16.9 degrees" says the witness turned by that much; the read says the model coupling is 16.9.
  - LAWS:40 "+0.6 degrees": the read is +0.60 +- 4.51 deg (0.13 widths from zero); the width is dropped.
- **n.** 1 job, 1 chip, 150 qubits; 21 circuits; 83 printed quantities; a ten-arm family for the 7.6 %.
- **CARRIES:** one job, one chip: own-interval residuals -0.12 +- 0.34 / -0.58 +- 0.52 / -0.97 +- 0.51 % at 2 / 6 / 10 pushes [OWN short-time; LAID intervals], the idle arm +0.02 +- 0.15 %, A30_10 +1.70 +- 0.64 % (7.6 % over ten arms) | **LAPS MEET** for the idle arm and the 7.6 %; **DON'T MEET** for 7P:14 and 7P:75 (widths dropped where "below zero" is the claim), 7P:56 / LAWS:36 ("size of the crossing" across jobs), 7P:68-69 (16.9 is a fitted coupling; the observed turn is 8.2 +- 0.5), LAWS:40 (+-4.5 dropped).

### Q21 · 10/2 17:27 - 17:30 · THE MOVE: the push run on two more chips · ibm_marrakesh, ibm_kingston · 2 jobs (run 141 each, of 3 planned)
- **Laid.** [LAID] Marrakesh db023m492g1c7399o9vg (created 17:27:52, ran 17:27:53-17:28:05), Kingston db023hal7guc73cfnvl0 (17:27:33; ran 17:28:13-17:30:00). The push run circuit for circuit, 14 x 400, all 156 qubits (143 / 147 readable); freezes 0acf02d98c52... / 56901639d015... (17:23:33); fire log `fire_logs_move.txt` "17:27:27 KINGSTON 1 firing", "17:27:47 MARRAKESH 1 firing"; runs 142-143 frozen on both chips, never fired.
- **Used for.** 7P:11 "Outside Pittsburgh the crossing is one read per chip (n = 1 on Marrakesh and on Kingston)"; 7P:56 "Marrakesh +2.74 +- 0.28, Kingston +2.87 +- 0.28 (one read each) ... Prepared |1>: ... -0.16 +- 0.21, -1.24 +- 0.24 ... idle -0.43 to +0.26 %"; 7P:91 (Finding Seven) "Kingston: a qubit prepared |1> and pushed ten times ends -1.24 +- 0.24 % against its decay clock (one read)"; LAWS:27; PAPER:72-73, 218-219, 223, 230-231, 237, 239, 263.
- **Lap up.** The release has no reader for these two reads. Recomputed here from the raw jobs with the frozen push reader's `push_stats()` (`lapup.txt` section 1): every printed line of `rep_marrakesh_read1.txt` and `rep_kingston_read1.txt` matches (e.g. :4 "+0.0274 +- 0.0028" and "+0.0287 +- 0.0028"; Kingston :7 "-0.0124 +- 0.0024"; Marrakesh :11 "-0.0043 +- 0.0013"; bit-by-bit and lean lines identical).
- **Lap down.** "One read each" is stated. Finding Seven: "its decay clock" is the one-exponential bookkeeping from the same job's 300-us idle arm; Kingston has no own-interval arms, and the no-name job (Q20) shows that bookkeeping carries a 2.2-2.7 % short/long gap on Pittsburgh (PAPER:263 lists Kingston's start-1 column as "not accounted for here"). The -1.24 is one column (start |1>) of one chip, chosen among the three chips' start-|1> columns (+0.05 +- 0.13, -0.16 +- 0.21, -1.24 +- 0.24) and the job's 12 printed quantities. Marrakesh's idle arm, -0.0043 +- 0.0013, sits 3.3 widths below zero inside "-0.43 to +0.26 %".
- **n.** 2 jobs (one per chip), 2 chips, 143 / 147 qubits; 14 circuits each; about 29 printed numbers per read.
- **CARRIES:** one job per chip: OFF spread arm minus one-exponential bookkeeping +2.74 +- 0.28 % (Marrakesh), +2.87 +- 0.28 % (Kingston) [OWN; LAID 30-us intervals]; Kingston's start-|1> column -1.24 +- 0.24 % | **LAPS MEET** for 7P:11, 7P:56, 7P:91, LAWS:27 and PAPER's tables (the numbers are the reads; the selection is stated in n).

---
## METHODS LINES AGAINST THE LAID RECORD
- 7P:31 "a fixed 500 us repetition delay": 51 of the 75 jobs of 10/1-10/2 ran at 500 us; the 24 band jobs (Q19) ran at 20 / 50 / 100 / 2000 us by design; the 9/28 jobs ran at the default, 20 us, 1 ms, or 20 us - 2 ms (B01-B13). 7P:31 "the whole-chip runs drive and read every qubit": all 156 in every 10/2 whole-chip job (meta `all_q`), LAPS MEET.
- 7P:34 "the ledger records each job's ID, settings and hash": the ledger holds 1 of the 75 job ids of 10/1-10/2 (run 121) and 4 freeze hashes; the rest are in the fire records on disk. LAPS DON'T MEET (the records exist; not where 7P says).
- PAPER:42 "qiskit-ibm-runtime 0.49": every payload's metrics read "qiskit_ibm_runtime-0.49.0". PAPER:53 "Delays are laid in whole multiples of 16 dt (64 ns)": the laid waits in the fire records are 30.016 us (469 x 64 ns), 299.968 us, 300.16 us, 6.72 / 19.97 / 59.97 us: LAPS MEET.
- PAPER:43 "563 tasks from 2026-09-25 to 2026-09-28": 563 (543 completed, 20 failed), created 9/25 17:03 to 9/28 21:57 EDT: LAPS MEET.
- PAPER:273 "These jobs are part of 72 IBM jobs fired on five chips over 2026-10-01/02 (71 landed) [§141]": the laid count is 75 fired, 74 landed, 389 s; the 72 predates the paper's own runs 121 and 141 x 2. LAPS DON'T MEET.
- PAPER:69 (Table 1) look-time start "13:13": submit stamp; the job ran at 14:25:04 (Q17). PAPER:61 (Table 1) run 7 "36 x 212": laid 9 x 212 (Q07). PAPER:62 (Table 1) run 10 "[TO FILL] x 585 per start": 9 x 195 (Q08). PAPER:189 "[TO FILL: task counts and dates for each Rigetti result]": §7 18 tasks 9/28 19:41; §10 24 tasks 20:45; §11 24 + 24 tasks 20:51 / 20:58; §12 48 + 24 tasks 21:26 / 21:29 (EDT). PAPER:202 "[TO FILL: job list ...]": B01, B02, B03, B06 above.

---
## TABLE: firing | used for | n | laps meet?

| firing (LAID) | used for | n | laps meet? |
|---|---|---|---|
| A01 · 4/27 Q-BERT A/B, Kingston (+Marrakesh, Fez) | 7P:102 order of looking | 2 jobs + Exp B on 3 chips; raw gone | DON'T: no read; rows filed as a timing confound |
| A02 · 7/11 GHZ pinata, Fez | 7P:68 (+1.88, GHZ leg) | 1 run, 24 x 4096; spacing assumed | DON'T: time unit assumed |
| A03 · 8/13 EH precision, Marrakesh | none | ledger row | not used |
| A04 · 9/24 dark_floor v1/v2 (Estimator), Marrakesh, Kingston | 7P:102 (via §19) | 12 jobs + 1 failed, 2 chips | DON'T: mitigated averages, no shots |
| A05 · 9/24 dark_link / dark_edge / space_time_same, Marrakesh | none | 26 jobs | not used |
| A06 · 9/24 arrow panels, three_box x3 chips, three_box_11 | 7P:102 (via §16A) | 4 three-box jobs, 3 chips | DON'T: excess filed as gate error, no width |
| A07 · 9/25 Rigetti q0 round 1-2 (step 3 three-box) | 7P:75 (-0.019) | 35 + 3 tasks, 1 qubit | DON'T: +-0.010 absent; fitted value at a fitted phase |
| A08 · 9/26 Rigetti dice / ring / plus-none | none | 71 tasks (20 failed) | not used |
| B01 · 9/28 08:30 parallax, Marrakesh | PAPER:203; LAWS:15-16; 7P:102 | 4 jobs, 78 q | DON'T: the count is in no file; PAPER's date range |
| B02 · 9/28 12:27 echo (pre-registered), Marrakesh | LAWS:26; 7P:62 (band); 7P:68 (+1.88); PAPER:204-206; 7P:102 | 14 jobs started within 23 s, 78 q | DON'T: "stays" vs a direction-blind read; band re-fire unquoted; relative-error map; "minutes" vs 23 s |
| B03 · 9/28 12:34 parallax, Kingston | PAPER:203, 205; LAWS:15-16; 7P:102 | 4 jobs, 78 q | DON'T: no read file |
| B04 · 9/28 12:39 Rigetti heat-vs-lens | none | 6 tasks | not used |
| B05 · 9/28 12:45-13:22 darkwave rounds, Kingston/Fez/Marrakesh | (pattern note only) | 19 jobs, 6 firings | not used by a number |
| B06 · 9/28 12:55 parallax, Fez | PAPER:203; 7P:68 (buzz leg) | 4 jobs, 78 q | DON'T for 7P:68 |
| B07 · 9/28 13:04-13:21 Fez witness jobs (partner, beat, split, culprit, ring, eleven, barrier, alone) | PAPER:158 | 8 jobs; of 25 Fez jobs + 246 Rigetti tasks, 778 tests | MEET (WITNESS_CROWD files; table = Fez calibration of 9/25) |
| B08 · 9/28 14:26 listen, Fez | PAPER:158 | 1 job | MEET |
| B09 · 9/28 14:38 split2, Fez | PAPER:158 | 1 job | MEET |
| B10 · 9/28 14:43 oddraw, Fez | 7P:102; LAWS:41 | 1 job, 2 seats, 26 pubs | DON'T: a readout tone, not a spectator qubit; 1:1 by identity |
| B11 · 9/28 14:49 the_do, Fez | PAPER:158 | 1 job | MEET |
| B12 · 9/28 15:37 ripples, Fez | none | 1 job | not used |
| B13 · 9/28 15:39-15:41 yeast hour, Fez | PAPER:158 | 7 jobs | MEET |
| B14 · 9/28 18:34 Rigetti Gamble | PAPER:196 | 21 tasks | DON'T: ledger §5 only |
| B15 · 9/28 18:40-19:02 Rigetti whole chip (tune, fine, run) | PAPER:196-200; LAWS:16; 7P:33; 7P:102 | 33 tasks, 107 columns; carry on 8 tasks, q0 | DON'T for LAWS:16 and PAPER:197-199 rho / carried / blink; MEET for standing values |
| B16 · 9/28 19:34-20:27 blink hour | PAPER:199 | 32 tasks | DON'T: ledger §9 only |
| B17 · 9/28 19:41 witness | PAPER:189 | 18 tasks, 4 q | DON'T: ledger §7 only |
| B18 · 9/28 20:45 witness whole chip | PAPER:189 | 24 tasks | DON'T: ledger §10 only |
| B19 · 9/28 20:51 who's watching | PAPER:189 | 24 tasks | DON'T: ledger §11 only |
| B20 · 9/28 20:58 headline (q9 alone) | PAPER:14 (abstract), PAPER:189 | 24 tasks, 2 q | DON'T: ledger §11 only |
| B21 · 9/28 21:26-21:30 rooms | PAPER:189 | 72 tasks | DON'T: ledger §12 only |
| B22 · 9/28 21:43 fuck-up stack | 7P:102 | 54 tasks | DON'T: ledger §21 "NOT supported" |
| B23 · 9/28 21:57 one for the road | 7P:102 | 30 tasks | DON'T: as B22 |
| Q01 · 10/1 23:09 Run 1, Kingston/Phoenix/Pittsburgh | none | 3 jobs | not used |
| Q02 · 10/2 00:14 Run 2 | 7P:62 (0.60); 7P:68 (1.667) | 1 job (Kingston), 9 q | DON'T: +-0.07 dropped; lowest of six |
| Q03 · 10/2 01:03 Run 3 | none | 3 jobs | not used |
| Q04 · 10/2 08:18 stone shot, Boston | none | 3 jobs (ledger stamp ~2 h late) | not used |
| Q05 · 10/2 08:47 Run 5, Marrakesh | PAPER:61, 134 | 1 job, 9 q | MEET |
| Q06 · 10/2 08:53-09:11 Run 6, Pittsburgh | count only | nothing returned | not used |
| Q07 · 10/2 09:13 Runs 9 + 7 | PAPER:61, 134 | 2 jobs, 2 chips | MEET (134); DON'T (Table 1: run 7 is 9 x 212) |
| Q08 · 10/2 09:18 Run 10 | PAPER:62, 242 | 2 jobs | MEET |
| Q09 · 10/2 09:30-09:59 jump run | PAPER:14, 112, 121-123, 128, 242; 7P:62 (0.775); 7P:50 via §135 | 8 jobs, 147 q | MEET (PAPER); DON'T (0.775 in no read) |
| Q10 · 10/2 10:08-10:18 tail + lone | 7P:62 (0.756, 0.59); PAPER:124, 242 | 3 + 1 jobs | MEET (one read, no widths) |
| Q11 · 10/2 11:02 half-push + maker's look length | 7P:50 (2.18); LAWS:34; PAPER:108, 118 | 1 config read at 11:02:53 | MEET |
| Q12 · 10/2 11:53 sides | none | 1 job | not used |
| Q13 · 10/2 12:05 turns | none | 1 job (2 pulled) | not used |
| Q14 · 10/2 12:07-12:16 hold | 7P:56, 62 (0.335), 69, 85; LAWS:25; PAPER:130, 140, 146-154, 217; 7P:50 via §135 | 3 jobs, 139-145 q | MEET (7P:56/69/85); DON'T (LAWS:25, PAPER:140/154 per qubit; +-0.2; "never given back") |
| Q15 · 10/2 12:25 stopwatch | 7P:85; PAPER:150, 160-172 | 1 job, 39 emitters | DON'T (7P:85's 1e-4); MEET (Table 4) |
| Q16 · 10/2 13:09 / 14:26 / 14:27 push | 7P:56, 62 (0.313), 69; LAWS:17, 27; PAPER:216-240 | 3 jobs, 141 q | MEET; DON'T for LAWS:17 |
| Q17 · 10/2 14:25-14:28 look-time | 7P:50, 62, 68, 85; LAWS:10-11, 34-35; PAPER:110-132, 174 | 3 jobs, 83 spectators | MEET (printed values); DON'T ("three positions" = three firings; +-0.03 vs job scatter +-0.06) |
| Q18 · 10/2 14:25-14:30 give-back | 7P:50; PAPER:125, 128 | 3 jobs, 148 q | DON'T: +-0.9 dropped; "never given back" vs Q14 |
| Q19 · 10/2 14:30-14:38 band | none (re-fire of B02's band) | 24 jobs | not used, and not set beside the 9/28 band |
| Q20 · 10/2 17:41 no-name | 7P:14, 56, 68-69, 75; LAWS:28-30, 36, 40; PAPER:176-187, 237-263 | 1 job, 150 q, 83 printed quantities | MEET (idle arm, 7.6 %); DON'T (widths; 16.9; +0.6; cross-job size) |
| Q21 · 10/2 17:27-17:30 the move, Marrakesh + Kingston | 7P:11, 56, 91; LAWS:27; PAPER:218-239 | 1 job per chip | MEET |

---
## WHERE THE LAPS DON'T MEET (exact)
1. **7P:14, 7P:75** "-0.12 / -0.58 / -0.97 %": the widths +-0.34 / +-0.52 / +-0.51 are dropped; the values sit 0.35 / 1.12 / 1.90 widths below zero (Q20, one job).
2. **7P:50, LAWS:35, PAPER:126** "3.5 +- 0.2 us": in no read or script; the reads give 3.20-4.26 (jump, per job), 3.0 / 3.8 (hold, per look), 3.5 / 3.6 / 4.1 +- 0.9 (give-back). The ratios 1.606 and 1.477 inherit the +-0.2 (Q09, Q14, Q18).
3. **7P:50** "3.5 / 3.6 / 4.1 ... never given back": +-0.9 dropped; job scatter 1.3-1.8 us; the hold run's lone look adds no time (Q18 vs Q14).
4. **7P:50, LAWS:34** "One readout look, timed from three positions": three firings at three times (11:02:53; 14:25-14:28; 09:30-14:30); the 2.37 is spectator phase in laid-delay units, +-0.03 shot / +-0.06 job scatter (Q11, Q17).
5. **7P:56, LAWS:36** "2.2-2.7 % apart ... the size of the crossing": the same job's crossing is +1.26 +- 0.32 %; the match is to other jobs (Q20 vs Q16).
6. **7P:62, 7P:68** "the gap clock 0.60", "1/0.60 = 1.667": +-0.07 / +-0.19 dropped; the lowest of six values (0.60-0.83) by the same reader (Q02).
7. **7P:62** "a 0.62-0.65 band on 9/28": a readout-cutoff position, R^2 0.23-0.43 +- 0.20-0.22; the 10/2 re-fire reads 0.00-0.11 there (B02, Q19).
8. **7P:62** "0.775 +- 0.009 (eight reads)": no read file holds it (Q09).
9. **7P:68** "+1.88 +- 1.16 series-taus ... a separation": the series-tau value depends only on each clock's relative error; the GHZ leg's time unit is assumed (B02, B06, A02).
10. **7P:68-69** "The spectator turns 16.9 degrees per 30-us |1> stretch": a fitted model coupling (+-1.81 dropped); the observed turn per laid stretch is 8.24 +- 0.48 (Q20).
11. **7P:75** "-0.019 (one run)": width +-0.010 absent (1.9 widths); a fitted value at a fitted phase, set beside a different quantity (A07).
12. **7P:85** "0.0648 / 0.1348 against 0.0647 / 0.1346": agreement at 1e-4; the read's two circuits differ by 1.4e-2; per emitter +0.0014 +- 0.0029 / +0.0048 +- 0.0040 (Q15).
13. **7P:102, LAWS:41** "the inside never sees / never reads the outside's laid time ... a spectator's clock is blind to how long we waited": one job, a readout tone on two seats, slope 1:1 by construction; spectator qubits in Q15, Q17, Q20 do track laid time (B10).
14. **7P:102** "the order of looking sets the heat": April raw gone (A01), 9/24 legs mitigated or filed as gate error (A04, A06), Rigetti rooms "NOT supported" in ledger §21 (B22, B23).
15. **7P:102, LAWS:15-16, PAPER:202-206** third level on IBM: the 134 / 98 counts are in no file (B01, B03); dated 9/24-9/28 but laid on 9/28 only; IBM "blinking ... minutes apart" ran within 23 s (B02).
16. **LAWS:16** "On Rigetti it survives the reset and carries into the next shot": one qubit (q0) of 95, about 1 in 100 after splits (B15).
17. **LAWS:17** "on IBM, shots don't talk (-0.002 +- 0.002)": one arm, one chip, 500-us spacing; the ON-idle arm leans +0.008 to +0.014 in 4 of 5 push jobs; 9/28 IBM at 20 us carries (Q16, B02, B03).
18. **LAWS:25, PAPER:140, PAPER:154** "per-qubit bookkeeping closes to 0.002": about 5 % of qubits do; the mean over qubits does (Q14).
19. **LAWS:26** "what arose on its own stays (+23 points at 20 us, gone by 500)": no width; a pooled clustering that reads the same forwards and backwards (B02).
20. **LAWS:40** "+0.6 degrees": +0.60 +- 4.51 in the read (Q20).
21. **PAPER:14 (abstract), PAPER:189, PAPER:196 (q0 alone, Bell), PAPER:197 (rho), PAPER:198-199 (carried, blinking, the blink hour)** Rigetti witness and third-level numbers: no read file below ledger §5, §7, §9-§12 (B14-B21; PAPER:274 says so). The standing values of PAPER:197 and q0's whole-chip start value do have files (B15).
22. **PAPER:61, PAPER:69, PAPER:273** Table 1 run 7 (9 x 212), look-time read 1 (ran 14:25), job count (75 / 74).
23. **7P:34** "the ledger records each job's ID, settings and hash": 1 of 75 job ids is in the ledger.

## FIRINGS THAT CARRY A CLAIMED NUMBER ALONE (one firing, no second firing behind the number)
- **Q20 no-name (1 job):** 7P:14 / 7P:75 (-0.12 / -0.58 / -0.97 %), the idle arm (+0.02 +- 0.15 %), the 10-us variant (+1.7 +- 0.6 %, 7.6 %), 2.2-2.7 %, 16.9 deg; LAWS:28-30, 36, 40; PAPER Tables 5 and 8.
- **Q21 Kingston run 141 (1 job):** Finding Seven's -1.24 +- 0.24 % and +2.87 +- 0.28 %. **Q21 Marrakesh run 141 (1 job):** +2.74 +- 0.28 %, -0.16 +- 0.21 %.
- **Q15 stopwatch (1 job):** 7P:85's parked emitters; PAPER Table 4.
- **Q10 lone look (1 job):** 7P:62's 0.756 and 0.59.
- **Q02 Kingston run 2 (1 job):** 7P:62's 0.60, 7P:68's 1.667.
- **Q17 look-time (3 jobs, one firing):** 2.37 us, 0.921 / 0.826 / 0.760, 3.144 deg/us.
- **Q18 give-back (3 jobs):** 3.5 / 3.6 / 4.1 us. **Q16 push (3 jobs):** Pittsburgh's +2.00 %, 0.313, the 0.26 %-per-push cap, -0.002. **Q14 hold (3 jobs):** +2.17 %, the park means, 0.335. **Q11 (one configuration read):** 2.18 us.
- **B02 echo (14 jobs in 23 s):** LAWS:26 (0.067 %, +23 points), 7P:62's band. **B10 oddraw (1 job):** "the inside never sees the outside's laid time".
- **A07 Rigetti step 3 (35 tasks):** -0.019. **B20 Rigetti headline (24 tasks):** the abstract's -62.1 +- 0.6 deg/us. **B15 Rigetti chip run (8 shuffle tasks on q0):** LAWS:16's carry.
- Numbers built from more than one firing: 7P:50's three ratios (Q11 + Q17 + §135 over Q09 / Q14 / Q18), the three-chip mean 2.54 % (Q16 + Q21), "+2.0 to +2.9 %" and "-0.43 to +0.26 %" (Q16 + Q21), the +1.88 (B02 + B06 + A02), the order of looking (A01, A04, A06, B02, B22, B23), the third level on two vendors (B01, B02, B03, B15, B16).
