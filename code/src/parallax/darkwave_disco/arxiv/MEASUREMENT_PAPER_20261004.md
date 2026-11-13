# A few-percent excess after spaced X-gate trains on three superconducting processors, the decay-bookkeeping control that removes it, and one readout timed three ways

**K. Indahl**


**Source tags.** Every number carries a tag. [reads/<file>] is a read file in the data release; [code/<file>] is frozen run or analysis code in the release; [§n] is entry n of the run ledger; [SHA256SUMS.txt] is the release's hash list; [derived here] marks arithmetic done in this draft on tagged numbers. "(one job)" marks a claim that rests on a single job. Times of day are EDT on 2026-10-02 unless stated; the 4 October runs are marked, and their read files and code are tagged [reads_20261004/<file>] and [code_20261004/<file>]. The 5 October files are tagged [reads_20261005/<file>] and [code_20261005/<file>].

---

## Abstract

On three IBM Heron processors, a qubit prepared in |0> and given ten X gates separated by idle intervals ends with more |1> population than one-exponential decay bookkeeping allows: +1.3 to +3.3% at 30-us intervals, +5.8% at 5 us, about zero at 150 us; a qubit prepared in |1> moves about as much the other way. The excess survives controls for excitation, leakage (at most 0.26 ± 0.12% per gate) and shot-to-shot carry-over, but not the bookkeeping: against each qubit's own decay curve in the same job it lies between −1.8% and +0.3% at intervals of 20 us and longer. We report it as accounted for by non-exponential decay; at 5-10 us, where our curve is interpolated, up to +3.4% remains. Against each interval's own decay it falls below zero, deepening by −0.0011 to −0.0020 per gate on three chips. We time one readout three ways: spectators read it at 1.02-1.07 times the vendor's stated duration on three chips, and at 0.97-1.01 of a readout tone we lay ourselves on a Rigetti processor. On Rigetti, where |2> is driven and read, the same train with every qubit driven exceeds one-exponential bookkeeping by +2.5 to +12.7%, while ten back-to-back gates alone move |0> by +7.6 to +9.0%, and that gate error rises from about 6% to about 10% when the neighbours are held on the equator. The spectators' state at readout scales a neighbour's |2> reading by 0.81-0.89 at every delay with the decay shape unchanged; the reverse effect is 1-3 degrees. A neighbour in |2> pulls a spectator by −62 deg/us (28 September) and −35 to −41 deg/us (4 October), and on both vendors a minority of qubits carry |2> population in three behaviours. Twenty-four calls written and hashed before their data are scored with misses included, beside the rate chance alone would give: four land, one meets its threshold inside its width, thirteen miss.

(Sources for every abstract number are in Sections 3.1-3.5.)

---

## 1 Introduction

The vendor of a superconducting processor publishes per-qubit numbers -- a measurement duration, relaxation times, couplings -- and experiments usually time their events with those numbers and book-keep their populations with one exponential decay per qubit. Here we report what happened when we did that and then tested the bookkeeping.

**The main result is a negative one.** A qubit prepared in |0> and given ten X gates separated by idle intervals ends with a few percent more |1> population than one-exponential decay bookkeeping allows, on three chips, in sixteen jobs over two days. It passes the controls for excitation, leakage and shot-to-shot carry-over listed in Section 3.2. It disappears when the bookkeeping uses each qubit's own decay curve measured in the same job: the decay right after preparation is faster than one exponential, and the excess is the size of that difference. We lead with it because it is a worked example of a few-percent excess that every other control we ran left standing, and because the control that removes it costs a handful of extra circuits in the same job.

Alongside it we report five measurements made with the same harness:

1. **The look.** One readout timed by three clocks: the vendor's stated duration; spectators evolving across a block of readouts on other qubits; and the decay the measured qubit shows per readout. On one chip two analysis methods give ratios 4-13% apart; we give both (Section 3.2).
2. **The park.** Whether a qubit's decay advances while it sits in |0> (Section 3.3).
3. **The witness.** Ramsey spectators reading a neighbour's |1> time; free spectators read through repeated readouts of other qubits at one, two and three or more links; and on Rigetti a neighbour in |2> (Section 3.4).
4. **The third level.** Per-qubit |2> populations at the start of a shot on two vendors, in three behaviours (Section 3.5).
5. **The second vendor, 4 October.** The push train with every qubit of Rigetti Cepheus driven, the same train on the |1>-|2> pair read by spectators, the spectators' |2> ruler measured round to round, and the readout cross-talk between spectators and emitters in both directions (Section 3.6).

No new physics is claimed. Comparisons are made within a single job unless stated. No numerical predictions were written before these runs; the run headers list outcome categories only [code/push.py; code/noname.py; code/hold.py; code/looktime.py; code/giveback.py; code/witness.py], and the 4 October morning and afternoon runs carry none [code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py], so those tests are post hoc. From the afternoon of 4 October, numbers were written and hashed before the data existed; Section 3.7 lists every one with its score, misses included, and the rate at which chance alone would score. Relaxation times of superconducting qubits wander in time through coupling to two-level-system (TLS) defects [4-8], so a decay curve gathered over a job is a mixture of exponentials; the bookkeeping control of Section 3.1 is a within-job case of that. Static ZZ coupling between fixed-frequency transmons shifts a qubit's frequency with its neighbour's state [9, 10], the shift the Ramsey spectators of Section 3.4 read. Leakage out of the two lowest levels and its removal [11], measurement-induced state transitions [12], cross-talk in multiplexed readout [13] and active reset [1] bound the controls of Sections 3.1-3.6. Krantz et al. review the device physics [14].

**Terms.** *Level*: the population estimate of Section 2.2 (0 at the |0> reference, 1 at the |1> reference). *Readout*: one measure instruction. *X gate* ("push"): the native x gate. *Halfway state*: the state made from |0> by one sx gate. *Emitter*: a qubit whose state a spectator reads. *Spectator* ("witness"): a neighbour of an emitter run as a Ramsey clock. *Far qubit*: a qubit wired to no emitter. *Interval*: a scheduled delay. *Median qubit*: the median over qubits (the ledger's "middle bit"). *Driven spectator*: a spectator whose emitter is held in |1>. *Free spectator*: a qubit held on the equator with no emitter driven (4 October).

---

## 2 Methods

### 2.1 Hardware and access

- **ibm_pittsburgh**: 156 qubits, Heron revision 3, all 156 in one measurement group [reads/pittsburgh_config_timing.json]; coupling map of 176 links read at fire [reads/witness_run.txt]. Static configuration at fire: dt = dtm = 4 ns; repetition-delay range 0-2 ms, default 250 us; dynamic repetition rate enabled; measure_esp disabled; acquire alignment 1, pulse alignment 1, granularity 1, minimum length 2 [reads/pittsburgh_config_timing.json]. Stated measurement duration 2.180 us on every qubit, read at 11:02:53 [reads/maker_look_length_pittsburgh.json].
- **ibm_marrakesh, ibm_kingston**: 156 qubits each, Heron revision 2, 176-link coupling maps read at fire on 2026-10-04 [reads_20261004/ibm_marrakesh_config_timing_lookwide.json; reads_20261004/ibm_kingston_config_timing_lookwide.json]. Stated measurement duration 2.684 us (ibm_marrakesh) and 2.180 us (ibm_kingston; and ibm_pittsburgh again), read on 2026-10-04 after each readout-timing run's first job had landed [reads_20261004/ibm_marrakesh_maker_look_length_20261004.json; reads_20261004/ibm_kingston_maker_look_length_20261004.json; reads_20261004/ibm_pittsburgh_maker_look_length_20261004.json]. ibm_fez (Heron [§24]) appears only in Sections 3.4-3.5.
- IBM jobs ran through Qiskit Runtime SamplerV2 (qiskit-ibm-runtime 0.49) [code/common.py].
- **Rigetti Cepheus-1-108Q** through Amazon Braket with pulse access; 563 tasks from 2026-09-25 to 2026-09-28 [§28, §154] and 680 tasks on 2026-10-04 [§192-§217; rigetti_20261004/braket_ledger.json].

### 2.2 Readout and state estimation

Readout is kerneled: one complex I/Q value per qubit per shot [code/common.py]. Per qubit and job, the means c0 and c1 of lone readouts of |0> and |1> (prepared and read at no delay, in the same job) define the |0>-|1> line. Each shot's value x is projected onto it, level = Re[(x − c0)(c1 − c0)*] / |c1 − c0|², so the |0> reference reads 0 and the |1> reference 1 [code/readclose.py; code/readnoname.py]. The mean level over shots is the population estimate. A |2> population reads at an unknown position x2 along the line.

Three further readings are kept from the same shots [code/readnoname.py; §144, §147]: the perpendicular component ("across the line"); the fraction of shots with level between 0.3 and 0.7 ("halfway band"); and the fraction more than three cloud widths from both cloud centres ("off both clouds"). The last two are reported minus what a mixture of the two reference clouds at the same level gives. Cloud width is sqrt(<|x − c0|²>/2) of the |0> reference; a qubit is *readable* when its cloud separation exceeds 4 widths (3 in the jump run) [code/readclose.py; code/readnoname.py; reads/jump_run.txt]. Some readers report median-qubit values over all qubits instead; Table 1 says which.

### 2.3 Settings

Every IBM job pins its sampler options: the vendor's qubit initialization at the start of each shot (init_qubits), kerneled readout, a fixed 500 us repetition delay, dynamical decoupling off, gate and measurement twirling off; SamplerV2 0.49 has no measurement-mitigation option [code/common.py]. A run refuses a chip whose configuration does not enable a dynamic repetition rate or whose repetition-delay range excludes 500 us [code/common.py]. Circuits use native x, sx, rz, delay and measure, with barriers in the spectator runs [code/push.py; code/looktime.py; code/noname.py]. Delays are laid in whole multiples of 16 dt (64 ns at dt = 4 ns) [code/common.py; code/push.py]. The order of circuits in each job is permuted by a seed written per job [code/common.py; code/push.py]. Whole-chip runs drive and read every qubit in every circuit, with no selection before the run [code/push.py; code/pushrep.py; code/noname.py]. The nine-qubit runs (runs 5, 7, 9) used nine qubits drawn by a written seed, in three groups of three [code/common.py; §114, §116].

### 2.4 Runs

**Table 1.** IBM runs used here. One read = one job. In the "start" columns, 0 / 1 / halfway name the prepared state.

| Run (script) | Chip | Run no. (jobs) | Start (EDT) | Circuits × shots | Qubits analysed | Used in |
|---|---|---|---|---|---|---|
| Two readouts, no delay (run5/run9/run7.py) | marrakesh / pittsburgh / kingston | 5 / 9 / 7 (one job each) | 08:47:45 / 09:13:47 / 09:14:34 | 36 × 212 | 9 each | 3.1 |
| Short-delay levels repeated (run10.py) | pittsburgh, kingston | 10 (one job each) | 09:18:11 / 09:19:14 | 9 × 195 (585 per start) | 9 each | 3.5 |
| Jump run (jump.py) | pittsburgh | 11-18 (8 jobs, 4 min apart) | 09:30-09:58 | 10 × 400 | 147 readable in all 8; re-rack over all 156 | 3.1, 3.5 |
| Tail run (tail.py) | pittsburgh | 21-23 (3) | 10:08 / 10:12 / 10:16 | 11 × 400 | all 156 (152 with a fitted clock) | 3.1, 3.5 |
| Lone readout (lone.py) | pittsburgh | 31 (one job) | 10:18 | 11 × 400 | all 156 | 3.5 |
| Hold run (hold.py) | pittsburgh | 71-73 (3) | 12:07 / 12:11 / 12:15 | 11 × 330 | all 156 (medians); 145 / 139 / 139 readable (means) | 3.1, 3.2, 3.5 |
| Spectator stopwatch (witness.py) | pittsburgh | 81 (one job of three planned) | 12:25:58 | 12 × 300 | 68 spectators with readable contrast | 3.2, 3.3 |
| Push run (push.py) | pittsburgh | 91-93 (3) | 13:09 / 14:26 / 14:27 | 14 × 400 | 141 | 3.5 |
| Readout timing (looktime.py) | pittsburgh | 101-103 (3) | 13:13 / 14:26 / 14:28 | 14 × 400 | 83 spectators | 3.1, 3.3 |
| One readout in a 300-us idle (giveback.py) | pittsburgh | 111-113 (3) | 14:25 / 14:27 / 14:29 | 6 × 1000 | 148 | 3.1 |
| Interval lengths and frame-held spectators (noname.py) | pittsburgh | 121 (one job of three planned) | submitted 16:05:54, landed 17:42 | 21 × 216 | 150 (75 spectators, 35 emitters) | 3.3, 3.5 |
| Push run, replication (pushrep.py) | marrakesh | 141 (one job of three planned) | 17:27:47, landed 17:28:08 | 14 × 400 | 143 | 3.5 |
| Push run, replication (pushrep.py) | kingston | 141 (one job of three planned) | 17:27:27, landed 17:30:03 | 14 × 400 | 147 | 3.1 |
| Push train, interval swept, decay read three times per job (time_wide.py) | marrakesh, kingston / pittsburgh | 301-303 (3 each) / 361 (one job) | 2026-10-04 10:07-10:21 / 11:11 | 50 × 300 | 136-138 / 142-147 / 149 | 3.1 |
| Readout timing, wide (look_wide.py) | marrakesh / kingston / pittsburgh | 311-313 / 331-333 (3 each) / 351 (one job) | 2026-10-04 10:26-10:31 / 10:41-10:51 / 11:09 | 37 × 400 | 77-86 spectators, 28-31 measured qubits | 3.2 |
| Free spectators (count_wide.py) | marrakesh / kingston | 321-323 / 341-343 (3 each) | 2026-10-04 10:33-10:39 / 10:55-11:04 | 34 × 300 | 119-121 spectators | 3.4 |

Sources: [reads/none_arm_three_chips.txt; reads/short_wait_across_time.txt; reads/jump_run.txt; reads/jump_rerack.txt; reads/tail_run.txt; reads/lone_vs_tail.txt; reads/hold_run.txt; reads/discarded_hold.txt; reads/witness_run.txt; reads/close_push.txt; reads/close_looktime.txt; reads/close_giveback.txt; reads/noname_read1.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt; fire_logs/fire_logs_noname.txt; fire_logs/fire_logs_move.txt; code/tail.py; code/lone.py; code/jump.py; code/hold.py; code/witness.py; code/push.py; code/pushrep.py; code/looktime.py; code/giveback.py; code/noname.py; §114-§117, §119, §121, §132, §134, §137, §139, §145, §152, §153; reads_20261004/paper_tables_20261004.md; code_20261004/time_wide.py; code_20261004/look_wide.py; code_20261004/count_wide.py; §182-§191]. 4 October job IDs: ibm_marrakesh: time db15r4bid5ic73eqmhs0, db15s4pb694s73drrg10, db15skrid5ic73eqmkvg / look db1644jid5ic73eqn2g0, db1657megvvc73bh72q0, db1661avog1s73fhn6e0 / witness db167erid5ic73eqn7gg, db168l2vog1s73fhnav0, db169p6egvvc73bh7a20; ibm_kingston: time db15t52vog1s73fhmo3g, db15u31b694s73drrjvg, db161j6egvvc73bh6u50 / look db16b22vog1s73fhnefg, db16ctuegvvc73bh7f10, db16ff9b694s73drsdag / witness db16hravog1s73fhnml0, db16iaavog1s73fhnn9g, db16llbid5ic73eqnp8g; ibm_pittsburgh: time db16p5hb694s73drsna0 / look db16oh6egvvc73bh7r90. Earlier IBM jobs and the Rigetti tasks of Sections 3.4-3.5 are described there.

### 2.5 Spectators

Emitters are taken in an order permuted by a written seed (20261810), each accepted only if it is at least three links from every earlier emitter; spectators are the qubits wired to an emitter; the rest are far qubits [code/witness.py; code/looktime.py; code/noname.py]. On ibm_pittsburgh's coupling map this gives 39 emitters, 86 spectators and 31 far qubits [reads/witness_run.txt; reads/looktime_roles.json]; the same seed gives the same roles in the readout-timing and interval-length jobs [§145; code/noname.py]. A spectator is put on the equator with sx and read at the end on two axes a quarter turn apart (sx, or rz(π/2) then sx); its hand is H = (2 L_X − 1) − i(2 L_Y − 1) from the two levels, with contrast |H| and phase arg H [code/readwitness.py; code/readclose.py]. In the interval-length job each spectator also receives a Y-axis π pulse, rz(−π/2) x rz(π/2), at every instant its emitter receives an X gate, so the spectator's own frame rotation cancels over each pair of intervals while its emitter's |1> time accumulates ("frame-held") [code/noname.py; §145]. In the 4 October readout-timing runs the same seed and rule are applied to each chip's coupling map read at fire, giving 39 emitters, 86 spectators and 31 far qubits on all three chips [reads_20261004/lookwide_roles_ibm_pittsburgh.json; code_20261004/look_wide.py]. In the free-spectator runs no emitter is driven: every qubit that is not a far qubit is put on the equator and read on two axes after the block, and is labelled afterwards by its number of links to the nearest far qubit [code_20261004/count_wide.py; code_20261004/readwitness_wide.py].

### 2.6 Decay bookkeeping

Population after a train is propagated as a two-state chain [code/readclose.py; code/readhold.py; code/readnoname.py]: during an interval of length L the |1> population survives with probability q_L and the rest goes to |0>; |0> does not change; each X gate swaps the two. The start is 0 (|0>), 1 (|1>), or the measured level of the halfway state. Two choices of q_L, both per qubit and from the same job:

- **one-exponential**: q_L = P(300 us)^(L/300), with P(300 us) the level of the qubit prepared in |1> and left 300 us [code/readclose.py; code/readhold.py; code/readnoname.py];
- **each interval's own**: q_L = P(L), the level of the qubit prepared in |1> and left L = 10, 30 or 90 us, measured in the same job (interval-length job only) [code/readnoname.py];
- **curve** (4 October): q_L read off the same job's |1>-idle levels at 0, 30, 100, 300 and 600 us, log-linear between points; each of the three copies of those arms gives its own curve and the tables average the three [code_20261004/readtime.py]. Below 30 us this curve is an interpolation, not a measurement.

The bookkeeping carries no gate error; back-to-back trains (no delay between X gates) measure gate error separately. *Excess* = measured level − bookkeeping.

### 2.7 Statistics and freezing

Values are means over readable qubits unless marked "median qubit"; the 4 October readers use 30-60 bootstrap resamples [code_20261004/paper_tables.py]. Widths are standard deviations over 100 bootstrap resamples of shots (200 in the stopwatch job), with written seeds [code/readclose.py; code/readnoname.py; code/readwitness.py]. For three jobs we give the mean with width sqrt(w1² + w2² + w3²)/3 and each job's value [code/readclose.py]; that width assumes independent jobs and does not include job-to-job wander. Hold-run "arm minus nothing" widths are the spread over the three jobs divided by √3 [code/readhold.py].

Before firing, each run's scripts and shared modules were hashed (sha256) together with its circuit ledger into one combined hash, and a fire refuses if the code on disk differs from the freeze [code/common.py]. The raw result payload is saved with its own sha256 before parsing [code/common.py]. Analysis scripts sit outside the freeze and were run on synthetic records before the data landed [§137b, §145].

### 2.8 Controls

- **Leakage to |2>**: the halfway band, off-both-clouds and across-the-line readings (Section 2.2); the back-to-back two- and ten-gate arms of the same jobs; and an extra-X identity, level(ending in |0>) + level(one more X) − 1 = P2(2 x2 − 1) [§146-§148; code/readnoname.py].
- **Excitation during |0> intervals**: each push job's own |0>-idle-300-us arm.
- **Shot-to-shot carry-over**: next-shot conditional levels in recorded shot order [§151, §152b; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt], with Rigetti's |2> carry-over through reset as a positive control [§18, §154].

---

## 3 Results

### 3.1 The push-train excess and the control that removes it

**Protocol** [code/push.py; code/pushrep.py]. Fourteen circuits per job: starts 0, 1 and halfway, each with no X gate, 2 or 10 X gates back to back, or 10 X gates spread over 300 us (a 30-us interval before each); plus starts 1 and 0 left idle for 300 us; one readout at the end; 400 shots. ibm_marrakesh and ibm_kingston ran the identical circuits and shots [code/pushrep.py; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

**Table 2.** Ten X gates spread over 300 us: measured level minus one-exponential bookkeeping, and the same jobs' idle arms.

| Chip (jobs) | Start 0 | Start 1 | Start halfway | Idle in 0, 300 us | Idle in 1, 300 us | Qubits |
|---|---|---|---|---|---|---|
| ibm_pittsburgh, push run (3) | +0.0200 ± 0.0016 | +0.0005 ± 0.0013 | +0.0034 ± 0.0014 | −0.0001 ± 0.0006 | 0.3131 ± 0.0013 | 141 |
| ibm_pittsburgh, hold run (3) | +0.0217 ± 0.0016 [§135] | +0.0014 ± 0.0014 [§135] | not run | not run | 0.3354 ± 0.0013 [reads/discarded_hold.txt] | 145 / 139 / 139 |
| ibm_marrakesh (one job) | +0.0274 ± 0.0028 | −0.0016 ± 0.0021 | +0.0117 ± 0.0024 | −0.0043 ± 0.0013 | 0.1786 ± 0.0019 | 143 |
| ibm_kingston (one job) | +0.0287 ± 0.0028 | −0.0124 ± 0.0024 | −0.0006 ± 0.0022 | +0.0026 ± 0.0014 | 0.2982 ± 0.0025 | 147 |

Sources: [reads/close_push.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt] unless tagged. The push run's three jobs give +0.0174 ± 0.0028, +0.0213 ± 0.0030 and +0.0213 ± 0.0023 for start 0 [reads/close_push.txt]. The hold run's start-0 arm on the median qubit gives +0.0154, +0.0139 and +0.0050 per job [§132; reads/hold_run.txt].

**Spread over qubits.** Start 0, qubit by qubit: ibm_pittsburgh (438 qubit-jobs) mean +0.0200, median +0.0133, 63% above zero, per-job medians +0.010 / +0.012 / +0.019 [§151]; ibm_marrakesh median +0.0229, 73% above zero; ibm_kingston median +0.0266, 76% [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt]. Start 1: medians −0.005 (41% above zero) [§151], −0.0047 (44%) and −0.0121 (34%) [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

**Table 3.** X gates back to back (no interval): level minus the no-gate arm [reads/close_push.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

| Chip (jobs) | Start 0, 2 X | Start 0, 10 X | Start 1, 2 X | Start 1, 10 X | Halfway, 2 X | Halfway, 10 X |
|---|---|---|---|---|---|---|
| ibm_pittsburgh (3) | +0.0019 ± 0.0006 | +0.0229 ± 0.0007 | −0.0020 ± 0.0007 | −0.0232 ± 0.0008 | −0.0262 ± 0.0019 | −0.1138 ± 0.0019 |
| ibm_marrakesh (one job) | +0.0063 ± 0.0013 | +0.0147 ± 0.0014 | −0.0045 ± 0.0014 | −0.0148 ± 0.0013 | +0.0017 ± 0.0030 | −0.0176 ± 0.0032 |
| ibm_kingston (one job) | +0.0029 ± 0.0017 | +0.0192 ± 0.0018 | −0.0071 ± 0.0014 | −0.0212 ± 0.0015 | −0.0190 ± 0.0036 | −0.0513 ± 0.0036 |

With no interval, starts 0 and 1 move by about equal and opposite amounts. From the ibm_pittsburgh arms, the X gate falls 1.48 ± 0.14 deg short of a half turn, plus 0.26 ± 0.12% per gate of any error that grows with the gate count (leakage wherever |2> reads, decay during the pulses, pulse noise), upper edge 0.49% [§147]. The shortfall alone predicts the halfway start's loss: 0.0258 ± 0.0024 for two gates (measured 0.0262 ± 0.0019) and 0.128 ± 0.012 for ten (measured 0.114 ± 0.002) [§149]. The spread-train excess does not follow the gate error: ibm_marrakesh has the smaller back-to-back shift (±0.0148 against ±0.023) and the larger excess (+0.0274 against +0.0200) [reads/rep_marrakesh_read1.txt; reads/close_push.txt; §152].

**The excess swept over interval length (4 October).** Every qubit of ibm_marrakesh and ibm_kingston (three jobs each) and ibm_pittsburgh (one job): starts 0, 1 and halfway, ten X gates each preceded by an interval of 5, 10, 20, 30, 45, 70, 100 or 150 us, one readout at the end. In the same jobs: the qubit's decay from |1> read at 30, 100, 300 and 600 us in three copies placed by the shuffled circuit order, an idle |0> at 300 and 600 us, an echo, and back-to-back trains [code_20261004/time_wide.py]. The 30-us row repeats the 2 October circuit. The tables below give start 0 and start 1 against one-exponential and curve bookkeeping [reads_20261004/paper_tables_20261004.md].

**Table 4.** Ten X gates, each after an interval; start 0; level minus bookkeeping (mean of three jobs, or one job on ibm_pittsburgh).

| Interval (us) | ibm_marrakesh (3) − ONE | ibm_marrakesh (3) − CURVE | ibm_kingston (3) − ONE | ibm_kingston (3) − CURVE | ibm_pittsburgh (1) − ONE | ibm_pittsburgh (1) − CURVE |
|---|---|---|---|---|---|---|
| 5 | +0.0575 ± 0.0016 | +0.0191 ± 0.0018 | +0.0576 ± 0.0014 | +0.0337 ± 0.0017 | +0.0267 ± 0.0021 | +0.0108 ± 0.0025 |
| 10 | +0.0538 ± 0.0019 | +0.0040 ± 0.0021 | +0.0529 ± 0.0016 | +0.0195 ± 0.0023 | +0.0263 ± 0.0025 | +0.0073 ± 0.0038 |
| 20 | +0.0394 ± 0.0021 | -0.0120 ± 0.0025 | +0.0414 ± 0.0019 | +0.0033 ± 0.0027 | +0.0201 ± 0.0025 | -0.0001 ± 0.0043 |
| 30 | +0.0302 ± 0.0020 | -0.0167 ± 0.0023 | +0.0325 ± 0.0019 | -0.0041 ± 0.0029 | +0.0171 ± 0.0028 | -0.0022 ± 0.0050 |
| 45 | +0.0158 ± 0.0021 | -0.0182 ± 0.0020 | +0.0213 ± 0.0020 | -0.0063 ± 0.0022 | +0.0096 ± 0.0031 | -0.0064 ± 0.0038 |
| 70 | +0.0110 ± 0.0019 | -0.0144 ± 0.0019 | +0.0145 ± 0.0018 | -0.0049 ± 0.0019 | +0.0151 ± 0.0029 | +0.0034 ± 0.0033 |
| 100 | +0.0076 ± 0.0017 | -0.0145 ± 0.0017 | +0.0098 ± 0.0018 | -0.0057 ± 0.0018 | +0.0063 ± 0.0031 | -0.0022 ± 0.0033 |
| 150 | -0.0003 ± 0.0019 | -0.0138 ± 0.0017 | +0.0058 ± 0.0019 | -0.0034 ± 0.0018 | +0.0050 ± 0.0024 | -0.0003 ± 0.0023 |

**Table 5.** The same, start 1.

| Interval (us) | ibm_marrakesh (3) − ONE | ibm_marrakesh (3) − CURVE | ibm_kingston (3) − ONE | ibm_kingston (3) − CURVE | ibm_pittsburgh (1) − ONE | ibm_pittsburgh (1) − CURVE |
|---|---|---|---|---|---|---|
| 5 | -0.0518 ± 0.0014 | -0.0196 ± 0.0015 | -0.0542 ± 0.0013 | -0.0329 ± 0.0014 | -0.0260 ± 0.0022 | -0.0146 ± 0.0024 |
| 10 | -0.0454 ± 0.0016 | -0.0104 ± 0.0018 | -0.0394 ± 0.0015 | -0.0129 ± 0.0019 | -0.0167 ± 0.0024 | -0.0068 ± 0.0032 |
| 20 | -0.0235 ± 0.0016 | -0.0022 ± 0.0019 | -0.0257 ± 0.0015 | -0.0033 ± 0.0021 | -0.0074 ± 0.0024 | -0.0035 ± 0.0037 |
| 30 | -0.0068 ± 0.0017 | -0.0018 ± 0.0018 | -0.0133 ± 0.0017 | -0.0004 ± 0.0022 | +0.0000 ± 0.0023 | -0.0017 ± 0.0038 |
| 45 | +0.0043 ± 0.0017 | -0.0043 ± 0.0017 | +0.0001 ± 0.0017 | +0.0027 ± 0.0018 | +0.0075 ± 0.0028 | +0.0028 ± 0.0031 |
| 70 | +0.0068 ± 0.0017 | -0.0104 ± 0.0017 | +0.0062 ± 0.0016 | -0.0006 ± 0.0016 | +0.0057 ± 0.0031 | -0.0019 ± 0.0031 |
| 100 | +0.0064 ± 0.0017 | -0.0135 ± 0.0016 | +0.0093 ± 0.0015 | -0.0020 ± 0.0015 | +0.0085 ± 0.0022 | +0.0001 ± 0.0023 |
| 150 | -0.0025 ± 0.0018 | -0.0156 ± 0.0017 | +0.0066 ± 0.0017 | -0.0017 ± 0.0016 | +0.0057 ± 0.0030 | +0.0007 ± 0.0029 |

Against one exponential, start 0 at 30 us reads +0.0302 ± 0.0020 (ibm_marrakesh) and +0.0325 ± 0.0019 (ibm_kingston), against +0.0274 ± 0.0028 and +0.0287 ± 0.0028 in their single 2 October jobs, and +0.0171 ± 0.0028 on ibm_pittsburgh (one job). The excess grows as the interval shortens, to +0.058 at 5 us on ibm_marrakesh and ibm_kingston and +0.027 on ibm_pittsburgh, and start 1 moves by about as much the other way at 5-20 us. Back-to-back trains in the same jobs move starts 0 and 1 by +1.0 to +1.2% and −1.0 to −1.1% for ten gates on all three chips; the halfway start moves +2.8% (ibm_marrakesh), −1.1% (ibm_kingston) and +2.6% (ibm_pittsburgh).

**Table 6.** X gates back to back (4 October): level minus the no-gate arm.

| Chip (jobs) | start 0, 2 X | start 0, 10 X | start 1, 2 X | start 1, 10 X | halfway, 2 X | halfway, 10 X |
|---|---|---|---|---|---|---|
| ibm_marrakesh (3) | +0.0027 ± 0.0009 | +0.0115 ± 0.0010 | -0.0010 ± 0.0009 | -0.0099 ± 0.0009 | +0.0135 ± 0.0022 | +0.0279 ± 0.0022 |
| ibm_kingston (3) | +0.0013 ± 0.0009 | +0.0108 ± 0.0010 | -0.0010 ± 0.0010 | -0.0104 ± 0.0010 | -0.0063 ± 0.0021 | -0.0107 ± 0.0019 |
| ibm_pittsburgh (1) | +0.0005 ± 0.0014 | +0.0100 ± 0.0013 | -0.0004 ± 0.0011 | -0.0107 ± 0.0012 | +0.0091 ± 0.0041 | +0.0261 ± 0.0033 |


**Controls.**
1. *Start-independent maps.* Relaxation toward a thermal population and an imperfect X gate act on the population as affine maps that do not depend on the start; they move all three starts alike and cannot produce an excess on start 0 alone. A check at an equilibrium population of 0.026 and per-interval survival 0.89 gives −0.104% [§146]. The same holds for any map independent of the start, such as constant leakage or a spectator-shifted pulse error [§147].
2. *Excitation during |0> intervals.* Every push job carries its own 300-us |0>-idle arm (Table 2). In the interval-length job, which holds the one remaining arm below, it reads +0.0002 ± 0.0015, capping excitation over the full 300 us at ~0.3% (2σ) [reads/noname_read1.txt; §176] (one job). Per 300 us: ibm_pittsburgh −0.0001 ± 0.0006, ibm_kingston +0.0026 ± 0.0014, ibm_marrakesh −0.0043 ± 0.0013 [reads/close_push.txt; reads/rep_kingston_read1.txt; reads/rep_marrakesh_read1.txt], against excesses of +0.0200, +0.0287 and +0.0274.
3. *Leakage to |2>.* (a) The halfway band, where |2> at x2 = 0.5 would read, is flat across arms: start-0 spread train +0.09% (all readable qubits; +0.14% on the 22-28 qubits with clouds more than 8 widths apart), hold run −0.00% / +0.13%, start-1 spread +0.07%, halfway spread +0.08%, idle in 1 +0.09% [§147, §148]; a |2> population carrying the +2.0% at x2 = 0.5 would put ~4% of shots there [§147]. On ibm_marrakesh / ibm_kingston the band reads +0.0004 / +0.0034 (start-0 spread) against +0.0007 / +0.0032 (start-1 spread) and +0.0010 / +0.0050 (halfway) [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt]. (b) Across the line, start-0 spread arm: −0.0001 ± 0.0005 (push run), +0.0001 ± 0.0006 (hold run) [reads/discarded_push.txt; reads/discarded_hold.txt]. (c) Spread across the line beyond the two-cloud mixture, +0.0003 ± 0.0001 for start-0 and start-1 spread arms alike; off both clouds +0.0011 ± 0.0003 (push run) and +0.0013 ± 0.0004 (hold run), with every arm that spent time or took gates at +0.0005 to +0.0012 [reads/discarded_push.txt; reads/discarded_hold.txt; §144]. (d) The back-to-back cap, 0.26 ± 0.12% per gate (0.49% at two widths) [§147]; x2 cancels from this cap to first order when the |2> population left after the train is the same for starts 0 and 1 [§148]. (e) The extra-X identity (interval-length job): −0.0006 ± 0.0043 (start 0) and −0.0007 ± 0.0040 (start 1) [reads/noname_read1.txt]; it is blind at x2 = 0.5 [§147], where (a) reads.
4. *Shot-to-shot carry-over.* In recorded shot order on ibm_pittsburgh the next shot of the start-0 spread arm ends in |1> no more often after a |1> ending than after a |0> ending: −0.002 ± 0.002 over three jobs, where a carry-over making the +2.0% would read ~+0.05; lags 2 and 5 the same; circuit to circuit at the same shot number, no more than an unrelated circuit; in one job (run 92) the start-0 spread arm followed the |0>-idle arm, whose shots almost never end in |1>, and its excess was +0.0213 [§151]. A bound without a model (next-shot lean after a |1> ending × share of shots ending in |1>): ibm_marrakesh +0.0108 × 0.39 = +0.004 of +0.027 [§152b; reads/rep_marrakesh_read1.txt]; ibm_kingston at most +0.0011 [reads/rep_kingston_read1.txt]. On Rigetti, where carry-over through |2> exists, the same kind of test finds it (Section 3.5) [§18, §154].
5. *Spread of decay times across qubits* moves all three starts alike (+0.005 to +0.013) [§139]. A single-qubit model of the gate shortfall with plain decay, dephasing and frame detuning gives equal and opposite start-0 / start-1 shifts and a negative halfway shift [§139].

**The control that removes it: each qubit's own decay.** A qubit's decay right after preparation is faster than one exponential through 300 us. In the interval-length job the |1>-idle arms keep 0.9463 ± 0.0019, 0.8609 ± 0.0025, 0.6846 ± 0.0029 and 0.3286 ± 0.0030 after 10, 30, 90 and 300 us; against one exponential through the 300-us point the first three sit −0.0141 ± 0.0019, −0.0259 ± 0.0024 and −0.0185 ± 0.0032 low [reads/noname_read1.txt] (one job). The same shape appears elsewhere: with no earlier readout the median qubit's decay clock is 208 us over the first 6.7 us and 260, 253 and 275 us over 6.7-20, 20-60 and 60-300 us (one job) [reads/lone_vs_tail.txt]; qubit by qubit the first 6.7 us run at 0.803 of the 60-300 us clock with no earlier readout (one job) and 0.686 after one readout (three jobs) [reads/lone_vs_tail.txt; reads/tail_run.txt]. Decay times also wander between jobs minutes apart: across the eight jump-run jobs a qubit's decay time scatters 1.35 times its shot width (median), more than twice on 25 qubits and three times on 4; its start-1 and start-halfway decay times, from separate circuits, move together (correlation +0.34 over all qubits, +0.71 on those 25) [§119; reads/jump_run.txt; reads/jump_cube.txt]. Single-qubit levels after a 60-us delay change by 0.2-0.4 within 4.5 minutes in both directions (rms over nine qubits 0.157 overnight and 0.164 in 4.5 minutes on ibm_pittsburgh, 0.141 overnight on ibm_kingston), while start-0 levels do not move (rms 0.011-0.019) [reads/short_wait_across_time.txt; §117].

**Table 7.** Interval-length job, ibm_pittsburgh, 150 readable qubits; level minus each bookkeeping [reads/noname_read1.txt] (one job). z is the own-interval excess over its width [derived here].

| Arm | Start | Interval in 0 / in 1 (us) | X gates | Level | − one-exponential | − own interval | z (own) |
|---|---|---|---|---|---|---|---|
| A30_30 | 0 | 30 / 30 | 10 | 0.3697 ± 0.0031 | +0.0126 ± 0.0032 | −0.0097 ± 0.0051 | −1.90 |
| A10_30 | 0 | 10 / 30 | 10 | 0.4217 ± 0.0030 | +0.0147 ± 0.0037 | −0.0139 ± 0.0071 | −1.96 |
| A90_30 | 0 | 90 / 30 | 10 | 0.2899 ± 0.0029 | +0.0270 ± 0.0029 | −0.0007 ± 0.0054 | −0.13 |
| A30_10 | 0 | 30 / 10 | 10 | 0.1710 ± 0.0024 | +0.0291 ± 0.0024 | +0.0170 ± 0.0064 | +2.66 |
| A30_90 | 0 | 30 / 90 | 10 | 0.6937 ± 0.0027 | −0.0050 ± 0.0033 | −0.0062 ± 0.0046 | −1.35 |
| A30_30f | 0 | 30 / 30 | 10 + 1 at end | 0.6296 ± 0.0032 | −0.0133 ± 0.0033 | +0.0091 ± 0.0052 | +1.75 |
| B30_30 | 1 | 30 / 30 | 10 | 0.6843 ± 0.0029 | −0.0022 ± 0.0031 | −0.0021 ± 0.0046 | −0.46 |
| B30_30f | 1 | 30 / 30 | 10 + 1 at end | 0.3150 ± 0.0029 | +0.0015 ± 0.0032 | +0.0014 ± 0.0046 | +0.30 |
| N2 | 0 | 30 / 30 | 2 | 0.1377 ± 0.0022 | +0.0245 ± 0.0025 | −0.0012 ± 0.0034 | −0.35 |
| N6 | 0 | 30 / 30 | 6 | 0.2854 ± 0.0030 | +0.0207 ± 0.0034 | −0.0058 ± 0.0052 | −1.12 |

Against each interval's own decay, the start-0 excess for 2, 6 and 10 gates is −0.0012 ± 0.0034, −0.0058 ± 0.0052 and −0.0097 ± 0.0051; the two bookkeepings differ by 2.6, 2.7 and 2.2% at those gate counts, the size of the excess [reads/noname_read1.txt; §155]. One more X gate at the end flips the residual with the qubit (one-exponential +0.0126 → −0.0133; own interval −0.0097 → +0.0091) [reads/noname_read1.txt]. Start 1 reads −0.0022 ± 0.0031 and −0.0021 ± 0.0046 under the two bookkeepings [reads/noname_read1.txt]. In this job the halfway band is flat in every arm (−0.17 to −0.01%), off-both-clouds is +0.07 to +0.25% in the pushed arms, and across the line is about 0 [reads/noname_read1.txt; §155]. In this job the 30/30 arm reads +0.0126 ± 0.0032 against one-exponential bookkeeping, where the same circuit read +0.0200 ± 0.0016 in the push-run jobs [reads/noname_read1.txt; reads/close_push.txt]; we do not compare across jobs (Section 4).

A reviewer pointed out that T1 fluctuation makes the ensemble decay a mixture of exponentials, which at short times lies below one exponential drawn through the long-time point; a bookkeeping that applies the measured short-time decay to every interval independently then over-subtracts, and a negative residual that grows with the number of intervals is the sign of that [§174]. The residuals in Table 7 have that shape. We take the excess against one-exponential bookkeeping to be accounted for by non-exponential decay.

**The same control on three chips (4 October).** Against each job's own decay curve, the start-0 excess at intervals of 20 us and longer reads −0.0182 to −0.0120 on ibm_marrakesh, −0.0063 to +0.0033 on ibm_kingston, and −0.0064 to +0.0034 on ibm_pittsburgh (one job); start 1 reads −0.0156 to −0.0018, −0.0033 to +0.0027 and −0.0035 to +0.0028 (tables above). At 5 and 10 us a residual remains: +0.0191 / +0.0040 (ibm_marrakesh), +0.0337 / +0.0195 (ibm_kingston) and +0.0108 / +0.0073 (ibm_pittsburgh) for start 0, with the opposite sign for start 1; there the curve is interpolated between its 0- and 30-us points (Section 2.6). The decay is faster than one exponential qubit by qubit, not only in the mean: at 30 us a qubit's |1> level sits below the exponential through its own 300-us level on 72-84% of qubit-copies on ibm_marrakesh and ibm_kingston (medians −0.020 to −0.036) and on 62% on ibm_pittsburgh (median −0.008), and above it at 600 us on 57-74% [reads_20261004/decay_bend_per_qubit_20261004.txt]. The decay time itself moves: the three copies give 168-183 us on ibm_marrakesh, 260-270 us on ibm_kingston and 294-297 us on ibm_pittsburgh; within a job the copies differ by up to 10 us (about two widths), and job means move by up to ~7 us between jobs minutes apart. The idle |0> arms read +0.0037 to +0.0080 after 300 us on ibm_marrakesh and ibm_kingston and +0.0004 on ibm_pittsburgh, against start-0 excesses of +0.030 and +0.033 at 30 us against one exponential [reads_20261004/paper_tables_20261004.md].

**Table 8.** The decay clock read three times per job (copies a, b, c): decay time from the 300-us level (median qubit); idle |0>; echo.

| Chip | job | copy a (us) | copy b (us) | copy c (us) | idle 0 300 us | idle 0 600 us | echo 30 / 100 / 300 us |
|---|---|---|---|---|---|---|---|
| ibm_marrakesh | 1 | 168.4 ± 3.3 | 172.6 ± 3.4 | 178.8 ± 3.4 | +0.0080 ± 0.0017 | -0.0020 ± 0.0016 | 0.252 / 0.482 / 0.501 |
| ibm_marrakesh | 2 | 177.9 ± 3.5 | 182.2 ± 3.6 | 180.2 ± 3.3 | +0.0057 ± 0.0017 | +0.0009 ± 0.0015 | 0.252 / 0.481 / 0.502 |
| ibm_marrakesh | 3 | 175.7 ± 3.7 | 177.2 ± 3.7 | 183.1 ± 3.1 | +0.0066 ± 0.0013 | -0.0005 ± 0.0013 | 0.255 / 0.484 / 0.496 |
| ibm_kingston | 1 | 267.4 ± 4.2 | 260.4 ± 4.0 | 261.0 ± 4.6 | +0.0063 ± 0.0018 | +0.0034 ± 0.0015 | 0.215 / 0.497 / 0.499 |
| ibm_kingston | 2 | 265.7 ± 4.1 | 260.5 ± 4.3 | 269.8 ± 4.0 | +0.0037 ± 0.0015 | +0.0032 ± 0.0014 | 0.216 / 0.493 / 0.498 |
| ibm_kingston | 3 | 263.8 ± 4.2 | 260.1 ± 4.4 | 260.9 ± 4.8 | +0.0046 ± 0.0016 | +0.0023 ± 0.0015 | 0.218 / 0.494 / 0.498 |
| ibm_pittsburgh | 1 | 297.1 ± 5.9 | 294.2 ± 4.4 | 293.8 ± 4.0 | +0.0004 ± 0.0011 | +0.0012 ± 0.0011 | 0.203 / 0.494 / 0.492 |


**What remains.** Of the ten arms in Table 7, one stands more than two widths above its own-interval bookkeeping: ten X gates with 30-us |0> intervals and 10-us |1> intervals, +0.0170 ± 0.0064 (z = 2.66) [reads/noname_read1.txt; derived here]. With ten arms this is 7.5% family-wise [§176] (one job). The |0>-interval series 10 / 30 / 90 us under own-interval bookkeeping (−0.0139 ± 0.0071, −0.0097 ± 0.0051, −0.0007 ± 0.0054) changes by 1.5σ end to end [§176]; the |1>-interval series 10 / 30 / 90 us (+0.0170, −0.0097, −0.0062) is not monotonic [reads/noname_read1.txt]. The 35 emitters of the spectator arms, given the same ten gates, read −0.0216 ± 0.0102 (start 0) and +0.0118 ± 0.0076 (start 1) against own-interval bookkeeping [reads/noname_read1.txt]; they are outside the family of ten, and the first is 2.1σ below zero [derived here]. ibm_kingston's start-1 column, −0.0124 ± 0.0024 in its single 2 October job, reads −0.0133 ± 0.0017 against one exponential and −0.0004 ± 0.0022 against its own curve in the three 4 October jobs at 30 us. Not accounted for: the chip-to-chip halfway start (Table 2 and Table 6) and the 5-10-us residual above. For the halfway start, a mixture of |0> and |1> lands on the line through starts 0 and 1 for any dynamics, with or without memory, if shots are independent [§148]; on ibm_pittsburgh the halfway start sits 4 widths off that line (+0.34 against +1.03%) [§147], which its own coherence, its neighbours' coherence, or shot-to-shot carry-over could produce [§148]. A run to separate these was frozen and not fired [§149, §157].

**A second chip for the slope with gate count (ibm_fez, 4 October, one job).** Start 0, an X gate after every 30-us interval, 2, 6 and 10 gates, every readable qubit (133), against three bookkeepings from the same job: each interval's own decay +0.0058 / −0.0050 / −0.0087, slope −0.00182 ± 0.00027 per gate; the 90-us level scaled +0.0252 / +0.0160 / +0.0067, slope −0.00231 ± 0.00028; one exponential through the 300-us level +0.0500 / +0.0463 / +0.0302, slope −0.00247 ± 0.00029 [reads_20261004/five_slope_fez_20261004.txt; reads_20261004/five_slope.py; reads_20261004/freeze_ibm_fez_run371.json; §202-§203]. On ibm_kingston (one job, 144 qubits, a third chip): +0.0038 / −0.0067 / −0.0120 against each interval's own decay, slope −0.00198 ± 0.00035; −0.00178 ± 0.00031 against the 90-us level; −0.00104 ± 0.00031 against one exponential [reads_20261004/five_slope_kingston_20261004.txt; code_20261004/five_slope_kingston2.py; §235]. On ibm_pittsburgh (2 October, own interval) the slope was −0.00106 ± ~0.0008. On ibm_pittsburgh's two further 4 October jobs of the swept train, start 0 against one exponential reads +0.0347 / +0.0332 (10 us), +0.0240 / +0.0196 (30 us), +0.0069 / +0.0111 (100 us), and against the curve within ±0.008 past 20 us [reads_20261004/time_wide_pittsburgh_reads123_20261004.txt; §229]. On ibm_fez (three jobs, a fourth chip): start 0 against one exponential +0.0627 / +0.0599 / +0.0431 / +0.0308 / +0.0169 / +0.0093 at 5 / 10 / 20 / 30 / 70 / 150 us, against the curve +0.0274 / +0.0132 / −0.0029 / −0.0094 / −0.0061 / −0.0043; ten back-to-back gates move |0> by +0.0095 to +0.0125 and |1> by −0.0092 to −0.0113; the decay time from the 300-us level is 150-154 us [reads_20261004/time_wide_fez_reads123_20261004.txt; §239]. Expressed per e-fold of interval on a log scale of the excess, the four chips fall off at different paces, and the pace orders with each chip's vendor-reported median T2/T1 on the day (ibm_pittsburgh 1.16, ibm_fez 0.68, ibm_kingston 0.64, ibm_marrakesh 0.52: slowest to fastest; four chips) [reads_20261004/two_ladder_four_chips_20261004.txt; reads_20261004/three_seats_per_chip_20261004.txt; §242, §246].

### 3.2 The look: one readout timed three ways

**Vendor.** The stated measurement duration on ibm_pittsburgh is 2.180 us on all 156 qubits [reads/maker_look_length_pittsburgh.json]; on ibm_kingston it was 2.18 us when read on 2026-10-01 [reads/jump_rerack.txt].

**Spectators.** In the readout-timing jobs [code/looktime.py] every emitter is held in |1> and every spectator runs as a free Ramsey clock. Far qubits are held in |0> and read 3 or 9 times back to back; barriers make every spectator's free evolution span the block, and spectators are not read until after it [code/looktime.py]. Delay arms of 0, 30, 60 and 120 us in the same jobs calibrate each spectator: its phase over 30 and 60 us is fitted as aT + bT², the block's phase is converted to elapsed time on that curve and divided by the number of readouts [code/readclose.py]. Over three jobs and 83 spectators: 2.3494 ± 0.0650 us per readout (block of 3) and 2.3699 ± 0.0318 us (block of 9) [reads/close_looktime.txt]. The three jobs give 2.4718 ± 0.0512, 2.2802 ± 0.0464 and 2.3578 ± 0.0659 us (block of 9), a spread larger than their shot widths [reads/close_looktime.txt]. Spectators wired to a measured qubit give 2.3244 ± 0.0413 us and those not wired 2.3652 ± 0.0487 us (block of 9) [reads/close_looktime.txt].

**The measured qubit.** Prepared in |1>, a qubit's level after a readout falls by more than its decay over the stated duration. Converted to the time its own decay would take to give the same fall, the estimators in Table 9 give 3.2 to 4.3 us per readout. The back-to-back fall scales with the qubit's decay time as decay over a fixed time does: in thirds of the chip sorted by decay time (221 / 282 / 352 us) the pair gives 3.25 / 2.94 / 3.49 us [reads/jump_rerack.txt], and in the jump run the fall times the decay time is 3.4 / 3.2 / 3.6 us by thirds [§119].

**Table 9.** One readout on ibm_pittsburgh, three clocks.

| Clock | Quantity | Value | Jobs | Source |
|---|---|---|---|---|
| Vendor | stated measurement duration, all 156 qubits | 2.180 us | read once | [reads/maker_look_length_pittsburgh.json] |
| Spectators | free-evolution time per readout, block of 3 | 2.3494 ± 0.0650 us | 3 | [reads/close_looktime.txt] |
| Spectators | free-evolution time per readout, block of 9 | 2.3699 ± 0.0318 us | 3 | [reads/close_looktime.txt] |
| Measured qubit | two readouts back to back, start 1, fall converted with each qubit's fitted decay (60 / 240 / 300 us): median qubit per job | 3.88, 4.26, 3.31, 3.20, 3.68, 3.20, 3.58, 3.58 us | 8 | [reads/jump_rerack.txt] |
| Measured qubit | same, each qubit over the 8 jobs, then median [quartiles] | 3.23 [2.36, 4.97] us | 8 | [reads/jump_rerack.txt] |
| Measured qubit | same, start halfway (own circuits) | 3.68 [1.88, 5.92] us; qubit by qubit minus start 1: −0.07 [−2.40, +1.56] us, co-moving +0.93 | 8 | [reads/jump_rerack.txt] |
| Measured qubit | two readouts back to back, fall converted on each qubit's 60-300 us clock, median qubit | 3.63 us (jobs 4.02, 3.51, 3.42); start halfway 3.19 us | 3 | [reads/tail_run.txt] |
| Measured qubit | one readout at 0 / 150 / 270 us inside a 300-us idle in 1: cost by the end | 3.5313 ± 0.8737 / 3.5569 ± 0.9309 / 4.0507 ± 0.9397 us | 3 | [reads/close_giveback.txt] |
| Measured qubit | per readout, from 3 and 9 readouts in 300 us | 3.5 ± 0.2 us | 3 | [§135, §139]: 3 readouts 3.6 ± 0.5 us each, 9 readouts 3.5 ± 0.2 us each, same job, three reads; the script that produced them was not kept |

**Two caveats in the same data.** (i) The single readout's cost read at the end of a 300-us idle wanders between jobs beyond its widths: one of the three give-back jobs reads 1.0228 ± 1.4946, 1.3144 ± 1.5800 and 0.7272 ± 1.5266 us at the three positions [reads/close_giveback.txt]; and in the hold-run jobs one readout at 150 us leaves the 300-us level unchanged within −0.0007 ± 0.0009 (median qubit; spread over jobs) [reads/hold_run.txt]. (ii) Extrapolating the long-time decay back to the first readout gives 8.27 [3.62, 12.85] us (start 1) and 6.12 [−0.07, 17.24] us (start halfway) instead [reads/jump_rerack.txt]; this includes the faster decay in the first ~20 us after preparation (Section 3.1) [§120, §121].

**Repeated readouts add up.** Nine readouts 30 us apart leave the qubit at 0.990, 0.973, 0.962, 0.947, 0.935, 0.922, 0.903, 0.894, 0.893 and 0.879 of its plain decay at successive readouts (median qubit, three jobs) [§132; reads/hold_run.txt]. At 300 us the arm minus the no-readout arm is −0.0131 ± 0.0017 (3 readouts) and −0.0289 ± 0.0014 (9 readouts) [reads/hold_run.txt]; qubit by qubit the time the qubit "says" passed is 311.5 us and 327.0 us against 300 us [reads/hold_run.txt], i.e. 3.8 and 3.0 us per readout [derived here].

**Ratios.** With 3.5 ± 0.2 us for the measured qubit and 2.3699 ± 0.0318 us for the spectators: spectator / vendor 1.087 ± 0.015; measured qubit / vendor 1.61 ± 0.09; measured qubit / spectator 1.48 ± 0.09 [derived here from §135 and reads/close_looktime.txt; widths propagated as independent].

**The same look on three chips, and a second method (4 October).** The readout-timing protocol was rebuilt to time the look three ways in one job. Spectators beside emitters held in |1> are read after blocks of 1, 2, 3, 4, 6 and 9 readouts on far qubits and after delays of 0-240 us; the time per readout is the slope over block size of each spectator's phase, converted to time on its own delay curve. The far qubits themselves are prepared in |1>, read 1-9 times, and their fall converted to time on their own decay over 10, 20 and 40 us; the time per readout is again the slope over block size [code_20261004/look_wide.py; code_20261004/readlook_wide.py].

**Table 10.** One readout timed three ways in one job, per job (4 October).

| Chip | job | vendor (us) | spectators (us) | measured qubit (us) | spectator / vendor | qubit / vendor | qubit / spectator |
|---|---|---|---|---|---|---|---|
| ibm_marrakesh | 1 | 2.684 | +2.760 ± 0.058 | +4.012 ± 0.255 | +1.028 ± 0.022 | +1.495 ± 0.095 | +1.454 ± 0.096 |
| ibm_marrakesh | 2 | 2.684 | +2.803 ± 0.068 | +4.125 ± 0.236 | +1.044 ± 0.025 | +1.537 ± 0.088 | +1.472 ± 0.096 |
| ibm_marrakesh | 3 | 2.684 | +2.846 ± 0.087 | +4.014 ± 0.252 | +1.060 ± 0.032 | +1.495 ± 0.094 | +1.410 ± 0.086 |
| ibm_marrakesh | mean | 2.684 | +2.803 ± 0.042 | +4.050 ± 0.143 | +1.044 ± 0.016 | +1.509 ± 0.053 | +1.445 ± 0.054 |
| ibm_kingston | 1 | 2.180 | +2.321 ± 0.034 | +3.788 ± 0.207 | +1.065 ± 0.016 | +1.738 ± 0.095 | +1.632 ± 0.093 |
| ibm_kingston | 2 | 2.180 | +2.312 ± 0.053 | +3.466 ± 0.269 | +1.061 ± 0.025 | +1.590 ± 0.123 | +1.499 ± 0.120 |
| ibm_kingston | 3 | 2.180 | +2.337 ± 0.051 | +3.715 ± 0.189 | +1.072 ± 0.023 | +1.704 ± 0.087 | +1.590 ± 0.095 |
| ibm_kingston | mean | 2.180 | +2.324 ± 0.027 | +3.656 ± 0.129 | +1.066 ± 0.012 | +1.677 ± 0.059 | +1.573 ± 0.060 |
| ibm_pittsburgh | 1 | 2.180 | +2.267 ± 0.047 | +3.063 ± 0.225 | +1.040 ± 0.022 | +1.405 ± 0.103 | +1.351 ± 0.103 |

On ibm_pittsburgh the same readout timed by the earlier method (Ratios, above) and by this one gives spectator / vendor 1.087 ± 0.015 and 1.040 ± 0.022 (−4.3%), measured qubit / vendor 1.61 ± 0.09 and 1.405 ± 0.103 (−12.7%), and measured qubit / spectator 1.48 ± 0.09 and 1.351 ± 0.103 (−8.7%) [derived here]. The earlier method takes the measured qubit's time from blocks of 3 and 9 readouts inside a 300-us idle and the spectators' from blocks of 3 and 9; the new one fits the slope over 1-9 readouts. A ratio that moves this much with the method is reported here as a measurement of the method as much as of the chip. With the new method, spectator / vendor stays at 1.040-1.072 on three chips while measured qubit / vendor ranges 1.40-1.74; on ibm_marrakesh the spectator time rose job by job (2.760, 2.803, 2.846 us), on ibm_kingston it held (2.312-2.337 us). On ibm_pittsburgh's three jobs: spectator / vendor 1.040 / 1.039 / 1.018, measured qubit / vendor 1.405 / 1.415 / 1.259 [reads_20261004/look_wide_pittsburgh_reads123_20261004.txt; §228].

**The same three clocks on a readout we lay ourselves (Rigetti Cepheus).** A 1-us tone on seven qubits' readout lines, then 0.5 us for the resonator to empty, is one look of laid length 1.5 us; every other qubit is a spectator whose frame is detuned by 100 kHz, and the look is one pulse block spanning all 107 qubits (a first run without that fence let the spectators skip the tone and timed only the shared 0.5 us; §231). A look with the tone at zero is the timing check: the spectators read it at 1.4937 us (0.996). At tone strengths 0.03 / 0.045 / 0.06: spectator / laid 0.994 / 1.008 / 0.968, measured qubit / laid 1.024 / 1.024 / 0.879 [rigetti_20261004/lookTri2_raw.txt; code_20261004/rigetti_look_triangle.py; §234]. The 2-7% by which spectators read IBM's readout beyond the vendor's stated duration does not appear when the duration is laid by us. On ibm_fez (vendor duration 1.66 us, three jobs): spectator / vendor 1.011 / 1.019 / 1.040, measured qubit / vendor 1.550 / 1.806 / 1.444 [reads_20261004/look_3and9_fez_20261004.txt; §239]. The same reads taken as the two-point slope between blocks of 3 and 9 readouts, the earlier method's construction, give spectator / vendor 0.97-1.04 (ibm_marrakesh), 1.03-1.11 (ibm_kingston), 1.03-1.06 (ibm_pittsburgh) and 0.99-1.04 (ibm_fez) [reads_20261004/look_3and9_three_chips_20261004.txt; code_20261004/readlook_3and9.py; §237].


**The same back-to-back pair on three chips** (nine qubits each; one job each). Second readout minus first: start 1, −0.0480 ± 0.0071 (ibm_marrakesh), −0.0272 ± 0.0060 (ibm_pittsburgh), −0.0204 ± 0.0053 (ibm_kingston); start halfway, −0.0163 ± 0.0051, −0.0142 ± 0.0057, −0.0067 ± 0.0053; start 0, +0.0018 ± 0.0029, +0.0082 ± 0.0036, −0.0092 ± 0.0043 [reads/none_arm_three_chips.txt]. The start-1 values are uneven across qubits: −0.006 to −0.272 on ibm_marrakesh, −0.013 to −0.119 on ibm_pittsburgh, +0.002 to −0.041 on ibm_kingston [reads/none_arm_three_chips.txt].

### 3.3 The park: intervals in |0>

If a qubit's decay advanced while it sits in |0>, populations after |0> intervals would fall below bookkeeping in which relaxation acts only during |1> intervals. Three tests on ibm_pittsburgh.

**Parked |1>-prepared qubits (hold run, three jobs).** Each arm starts in |1> and spends 300 us split into 2, 4 or 10 equal intervals with an X gate after each, so the qubit spends alternate intervals in |0> and the last X gate returns it [code/hold.py]. The bookkeeping uses only the same job's 300-us |1>-idle arm (one exponential); population that relaxed during a |1> interval is put back in |1> by the next X gate and relaxes again [code/readhold.py]. Table 11 gives the median-qubit comparison per job. Taken qubit by qubit and then averaged over the readable qubits (three jobs), each arm minus its bookkeeping is +0.0017 ± 0.0013 (parked once), +0.0020 ± 0.0015 (alternate quarters) and +0.0014 ± 0.0015 (alternate tenths); single qubits scatter about ± 0.02 inside shot widths of 0.026-0.030, and about 5 % of qubits sit within 0.002 [reads/park_per_qubit.txt; code/park_per_qubit.py; §180]. On the median qubit the "parked once" arm sits +0.0054 to +0.0086 above its bookkeeping in all three jobs [reads/hold_run.txt]; the ledger records this as an artifact of applying the bookkeeping to the median qubit [§135].

**Table 11.** Hold run, start 1, 300 us total; median qubit, jobs 1 / 2 / 3 [reads/hold_run.txt].

| Arm | Intervals | Bookkeeping | Measured | Measured − bookkeeping |
|---|---|---|---|---|
| parked once | 2 × 150 us | 0.7591 / 0.7600 / 0.7583 | 0.7656 / 0.7654 / 0.7670 | +0.0065 / +0.0054 / +0.0086 |
| alternate quarters | 4 × 75 us | 0.7189 / 0.7206 / 0.7173 | 0.7182 / 0.7203 / 0.7231 | −0.0007 / −0.0004 / +0.0058 |
| alternate tenths | 10 × 30 us | 0.6940 / 0.6963 / 0.6919 | 0.6943 / 0.6974 / 0.6887 | +0.0003 / +0.0011 / −0.0032 |

**Parked emitters (stopwatch job; one job).** Emitters held in |1> for 20 or 40 us and then moved to |0> by an X gate for the rest of a 60-us window end with |1> populations 0.0648 and 0.1348 (mean of the two spectator-axis circuits), against bookkeeping of 0.0647 and 0.1346 from each emitter's own 60-us survival, 0.7896 with its neighbours in |0> [reads/witness_run.txt; §134]. The bookkeeping reproduces as (1 − q20) q40 and (1 − q40) q20 with q_t = 0.7896^(t/60) [derived here]. The two circuits read 0.0719 / 0.0576 and 0.1287 / 0.1409 [reads/witness_run.txt; code/readwitness.py]. Per emitter (34 readable), level minus bookkeeping: +0.0014 ± 0.0029 after 20 us and +0.0048 ± 0.0040 after 40 us [reads/park_per_qubit.txt, section 2], which prints the 40-us bookkeeping as 0.1347.

**Idle |0> and readouts of |0>.** A qubit left in |0> for 300 us changes its level, relative to the same job's |0> reference, by −0.0001 ± 0.0006 (push run, three jobs) and +0.0002 ± 0.0015 (interval-length job; one job) on ibm_pittsburgh [reads/close_push.txt; reads/noname_read1.txt], +0.0026 ± 0.0014 on ibm_kingston and −0.0043 ± 0.0013 on ibm_marrakesh (one job each) [reads/rep_kingston_read1.txt; reads/rep_marrakesh_read1.txt]. Nine readouts of a |0> qubit through 300 us read +0.0013, +0.0002, +0.0009, +0.0014, −0.0001, +0.0014, +0.0005, +0.0005, +0.0010 and +0.0002 (median qubit, mean of three jobs) [reads/hold_run.txt].

At this resolution -- within 0.002 as a mean over qubits [reads/park_per_qubit.txt], within 0.0086 on the median qubit [reads/hold_run.txt] -- intervals in |0> add no relaxation and no excitation, and reading a |0> qubit does not excite it.

### 3.4 The witness: spectator readings of a neighbour

**What moves a spectator (ibm_fez, Rigetti).** The state of the qubit wired to it, and not the number of other qubits active [§31]. ibm_fez q144 ran at 28.2-28.8 kHz with 0, 1 or 77 other qubits active, none wired to it, keeping contrast 0.94-0.96; 34 further ibm_fez spectators read 0 ± 10 deg between large and small groups, contrast unchanged; Rigetti q9 was flat with 0, 11 or 53 non-neighbours in |1> and with 1 or 106 qubits read at the end [§31]. With its neighbour q143 in |1>, q144 ran at 21.9 kHz (vendor table: 21.7) and with q143 on the equator at 25.1 kHz (table: 25.1); q113's frequency moved −5.1 kHz with neighbour q119 in |1> (table: −5.1); q138 moved −20 deg with two neighbours in |1> (table: −19) [§31]. On Rigetti, every qubit in |1> against a checkerboard with no neighbour in |1> raised the spectators' median contrast decay from 0.092 to 0.123 per us, with 43 of 54 lower at 6 us [§31]. These rest on 778 within-job tests, Holm-corrected [§31]. ibm_fez: jobs of 28 September 2026, 16:54-19:41 UTC, with a 5-us wait; the analysis used 25 finished jobs, and the run index lists 31 ibm_fez job IDs in that window, which the analysis files do not reconcile; the coupling values quoted are from the vendor's ibm_fez ZZ table of 25 September. Cepheus-1-108Q: 246 tasks, 28 September 23:41 UTC to 29 September 01:57 UTC, waits 0.5-16 us, matched at 2 and 4-4.5 us [§31; RUN_INDEX.csv].

**A spectator timing its emitter's |1> interval (ibm_pittsburgh; one job).** Every emitter was held in |1> for 0, 20, 40 or 60 us and then moved to |0> for the rest of a 60-us window, while every other qubit ran as a Ramsey clock for the full window (300 shots) [code/witness.py; reads/witness_run.txt; §134].

**Table 12.** Spectator stopwatch; median spectator of 68 with readable contrast [reads/witness_run.txt] (one job).

| Emitter time in 1 (us) | 0 | 20 | 40 | 60 |
|---|---|---|---|---|
| Phase added by each further 20 us in 1, own sign + (deg) [quartiles] | -- | +33.9 [+27, +46] | +28.1 [+16, +39] | +23.9 [+17, +32] |
| Spectator contrast | 0.469 | 0.422 | 0.398 | 0.412 |
| Far-qubit contrast | 0.339 | 0.310 | 0.306 | 0.302 |
| Far-qubit phase change, magnitude / its shot width (deg) | -- | 20.2 / 15.7 | 18.7 / 16.6 | 9.7 / 16.5 |
| Spectator-timed duration in 1 (us) | -- | -- | 35.6 | 48.3 |

The second 20 us adds 0.78 of the first and the third 0.65 of the second (median spectator); the rate while the emitter is in |1>, from the 40-us arm, is 4.5 kHz [quartiles 3.4, 5.2] [reads/witness_run.txt]. The spectator-timed duration is the total phase divided by the phase rate of the first 20 us [code/readwitness.py]. Being watched does not change the emitter: its level after 60 us in |1> is 0.7896 with its neighbours in |0>, 0.7900 with them in |1>, and 0.7942 / 0.7824 with them running as spectators (the two readout-axis circuits); qubit by qubit, spectators minus neighbours-in-|0> −0.0029 ± 0.0086, neighbours-in-|1> minus neighbours-in-|0> +0.0040 ± 0.0136 [reads/witness_run.txt]. A model of each spectator driven by its emitter's own measured decay closes with a residual of −1.4 ± 4.8 deg, contrast ratio 1.02 ± 0.035 and no phase step at the emitter's X gate; driven by the laid time instead, the contrast ratio is 0.90 ± 0.03 and a −3.2 deg step per X gate is needed [§135; reads/stopwatch_triangle.json, 66 spectators] [code/stopwatch_triangle.py]. The model: for each of the 66 spectators with a readable hand, the expected hand is the average of exp(iωt) over the time t its emitter spends in |1>, taken as exponential with mean τ and cut at the interval, an emitter that fell before the X gate being put back in |1> to fall again; ω is fitted on the 20- and 40-us arms, the 60-us arm is held out, and τ is in turn the emitter's own measured fading time, the laid time (no fading), or the chip's middle fading time.

**Spectators during the readout-timing jobs (three jobs, 83 spectators).** With emitters in |1>, a spectator's phase (in the drive frame) advances at 3.1444 ± 0.0760 deg/us over the first 30 us [reads/close_looktime.txt]. Its contrast relative to no delay is 0.9209 ± 0.0040 after a block of 3 readouts on far qubits, 0.8256 ± 0.0052 after 9, and 0.7604 ± 0.0057 after 30 us of delay [reads/close_looktime.txt]. Whether a spectator's phase curve follows its own emitter's decay (median emitter decay time in these jobs 274.99 ± 4.27 us) better than the chip's typical decay is not resolved: fit residuals 12.8046 ± 1.0979 and 12.4828 ± 1.0555 deg, difference +0.0020 ± 0.0032 deg [reads/close_looktime.txt].

**Free spectators through repeated readouts of other qubits (4 October).** With no emitter driven, every qubit that is not a far qubit was held on the equator through blocks of 1-32 readouts on the 31 far qubits and through delays of 0-120 us (three jobs on each of ibm_marrakesh and ibm_kingston; 119-121 readable spectators) [code_20261004/count_wide.py]. The table gives the contrast kept, relative to no delay, by links to the nearest far qubit, and the readout duration timed on these spectators as in Section 3.2.

**Table 13.** Free spectators (4 October), mean of three jobs per chip.

**ibm_marrakesh**

| Links | spectators | 1 readout | 3 | 12 | 24 | 32 | 30 us delay | 120 us delay | readout timed (us) |
|---|---|---|---|---|---|---|---|---|---|
| 1 link | 39 | +0.900 ± 0.006 | +0.786 ± 0.009 | +0.453 ± 0.014 | +0.226 ± 0.013 | +0.138 ± 0.009 | +0.487 ± 0.012 | +0.111 ± 0.007 | +1.82 ± 0.13 |
| 2 links | 43 | +0.859 ± 0.008 | +0.694 ± 0.010 | +0.338 ± 0.012 | +0.137 ± 0.008 | +0.093 ± 0.006 | +0.388 ± 0.011 | +0.091 ± 0.006 | +1.26 ± 0.16 |
| 3+ links | 37 | +0.886 ± 0.006 | +0.777 ± 0.010 | +0.398 ± 0.011 | +0.142 ± 0.010 | +0.100 ± 0.007 | +0.453 ± 0.010 | +0.077 ± 0.006 | +1.64 ± 0.15 |

**ibm_kingston**

| Links | spectators | 1 readout | 3 | 12 | 24 | 32 | 30 us delay | 120 us delay | readout timed (us) |
|---|---|---|---|---|---|---|---|---|---|
| 1 link | 38 | +0.943 ± 0.005 | +0.901 ± 0.008 | +0.659 ± 0.010 | +0.344 ± 0.011 | +0.189 ± 0.010 | +0.628 ± 0.010 | +0.108 ± 0.008 | +1.56 ± 0.12 |
| 2 links | 45 | +0.952 ± 0.005 | +0.900 ± 0.006 | +0.616 ± 0.011 | +0.305 ± 0.010 | +0.148 ± 0.008 | +0.575 ± 0.011 | +0.088 ± 0.007 | +0.82 ± 0.16 |
| 3+ links | 38 | +0.948 ± 0.005 | +0.910 ± 0.006 | +0.648 ± 0.010 | +0.287 ± 0.010 | +0.143 ± 0.008 | +0.591 ± 0.011 | +0.075 ± 0.006 | +1.82 ± 0.10 |

A block of k readouts costs these spectators about what k times the vendor's duration of delay costs them (on ibm_marrakesh, 12 readouts, about 32 us, keep 0.34-0.45 against 0.39-0.49 after 30 us of delay). On both chips the spectators two links from the nearest far qubit time the readout shortest (1.26 ± 0.16 us against 1.64-1.82 on ibm_marrakesh; 0.82 ± 0.16 us against 1.56-1.82 on ibm_kingston), and on ibm_marrakesh they also keep the least contrast. Free spectators time the readout shorter than the vendor's duration on both chips; spectators beside emitters held in |1> time it longer (Section 3.2). What the two-link seats are in the coupling map was not examined. With the original reader, the readout duration timed on free spectators is 0.62 us in five groups on two chips (ibm_kingston: emitter seats at two and at three or more links, and two of the two-link contrast bands; ibm_marrakesh: the one-link low-contrast band), carried by q35 and q47 (ibm_marrakesh) and q99, q117 and q153 (ibm_kingston); two further readers are kept beside it (medians over all spectators 1.47 / 2.29 / 2.81 us on ibm_marrakesh, 1.45 / 2.22 / 2.35 us on ibm_kingston) [reads_20261004/the_062_rows_20261004.txt; §199-§200]. We report the recurrence as read. On ibm_pittsburgh's free spectators (three jobs, same reader) no group reads 0.62 us; the nearest are 0.56 and 0.53, in the two-link class [reads_20261004/witness_seats_kingston_pittsburgh_20261004.txt; code_20261004/readwitness_seats.py; §230]. On ibm_fez's free spectators (three jobs) the two-link class again times the readout shortest in every job: 0.71 / 0.45 / 0.74 us against 1.26 / 1.42 / 1.70 us at one link [§239].


**Frame-held spectators (interval-length job; one job).** Emitters received ten X gates with 30-us intervals, starting in |0> or |1>, while their spectators received the frame-holding Y pulses at the same instants (Section 2.5). 75 spectators and 35 emitters were readable [reads/noname_read1.txt].

**Table 14.** Frame-held spectators after 300 us [reads/noname_read1.txt] (one job).

| Quantity | Emitters started in 0 | Emitters started in 1 |
|---|---|---|
| Spectator contrast | 0.1603 ± 0.0070 | 0.1625 ± 0.0073 |
| Spectator phase (deg) | −120.35 ± 17.82 | +96.67 ± 19.02 |
| Spectator level, emitter ended in 1 minus ended in 0, hand X: measured / model | +0.0138 ± 0.0090 / +0.0328 ± 0.0116 | +0.0159 ± 0.0091 / −0.0293 ± 0.0102 |
| Same, hand Y: measured / model | −0.0188 ± 0.0075 / −0.0187 ± 0.0075 | −0.0524 ± 0.0085 / −0.0318 ± 0.0078 |

Half the phase difference between the two emitter starts, averaged over spectators, is −12.47 ± 4.95 deg; half their sum, the spectator's own residual phase, is +0.60 ± 4.51 deg [reads/noname_read1.txt]. The coupling read per spectator is 16.90 ± 1.81 deg per 30-us emitter interval in |1> (median) [reads/noname_read1.txt]. The model (Table 14) is each spectator fitted from its emitter's own decay [code/readnoname.py]; it agrees with the measured hand Y for emitters started in |0>, and for emitters started in |1> it differs in sign on hand X (3.3 widths) and by 1.8 widths on hand Y [reads/noname_read1.txt; §155]. Own-emitter versus chip-typical decay in the model is again not resolved: misfit 0.0751 ± 0.0071 against 0.0747 ± 0.0070, difference +0.0004 ± 0.0006 [reads/noname_read1.txt].

**A neighbour in |2> (Rigetti).** Emitter q0 is driven to |2> and left to fall; its neighbours q9 and q1 run as Ramsey clocks; q10, two links away, is the control [§7]. With q0 in |1> a neighbour's clock moves by about 0.3 deg/us; with q0 in |2>, q9 is pulled by −62 deg/us (−173 kHz) and q1 by −27 deg/us (−74 kHz), q10 by about 0 [§7]. The fall time from |2> read from the spectator is about 20 us, with fit residuals χ² of 8.6 (q9), 11.8 (q1) and 6.2 (q10) for six numbers [§7]; q0's |1>-|2> transition is at 4.295 GHz and q9 at 4.631 GHz [§7]. With q9 the only spectator and all else parked: pull −62.1 ± 0.6 deg/us, frequency spread 16 kHz (3.5σ); spectator fall time 20.9 us (16.5-29.5) against 24.2 us from q0's own readout; forcing the readout value on the spectator fit costs Δχ² = +0.2 [§11]. With 0, 54 or 106 other spectators active: spectator fall times 21.0 / 16.0 / 23.0 us against 24.2 / 21.0 / 20.4 us from q0's readout, Δχ² +0.2 / +0.9 / +0.1; pull −62.1 / −62.3 / −59.9 deg/us; spread 16 / 18 / 12 kHz [§12]. In an earlier whole-chip run (105 other spectators) q9's fall time, 14.8 ± 5.3 us, was shorter than q0's readout value of 31.2 us (30.0-32.6) [§10]; the isolated and alternating-group runs above do not repeat that difference [§11, §12]. Neighbours q1 / q9 respond to q0's state (1.8 / 1.9 times noise when the drive pulse is played with q0 at rest; 10.5 / 22.4 times with q0 in |2>); some far qubits respond to the drive pulse even with q0 at rest (for example q43 at 13.6 times noise; q45, q5, q35 about 3-4 times), and that response varies between batches (q43 strong in two batches, absent in a third) [§11]. Cepheus-1-108Q, 28-29 September (UTC): the q0 / q9 / q1 clocks 18 tasks × 2000 shots (23:41); the whole-chip run 24 × 2000 (00:46); the neighbour-response run 24 × 2000 (00:51); q9 alone 24 tasks, 12 × 1000 and 12 × 2500 (00:59); the rooms of 54 and 106 other spectators 48 tasks (01:27); alternating alone / full 24 × 2500 (01:30) [§7, §10-§12; RUN_INDEX.csv].

### 3.5 The third level

On the IBM path used here (native gates, standard measure) |2> is not read directly; ibm_pittsburgh's configuration lists measure_2 and reset_2 among supported instructions [reads/pittsburgh_config_timing.json], which were not used. On Rigetti with pulse access the |1>-|2> transition is driven and |2> is read [§5, §154]. On both vendors a minority of qubits carry a |2> population at the start of a shot, in three behaviours [§5, §6, §154]: **standing** (present at every inter-shot gap), **carried** (raised by a readout, carried into the next shot when shots are close, then draining), and **blinking** (switching on and off between batches minutes apart while the ordinary readout stays flat). Each has a textbook description: steady |2> occupancy; measurement-induced leakage that a |0>/|1> reset cannot clear; |2> population or transition-frequency switching [§6].

**Rigetti Cepheus-1-108Q (2026-09-25 to 09-28)** [§5, §6, §9, §18].
- *Baseline*: q0's |2> population at the start of a shot is 0.03 ± 0.17% alone and 0.29 ± 0.19% with the whole chip run in parallel; an entangling gate leaves +0.05 ± 0.39% on q0's |2> [§5].
- *Standing*: on 56 qubits read without ambiguity the median is 0.04%; q24 2.05%, q48 1.34%, q40 1.26%, q33 1.17% [§5]. q33 has the shortest lifetime on the chip (0.7 us) and q24 the seventh shortest; q24 and q33 are neighbours [§5, §6]. Worse readout goes with more |2>: ρ = −0.31 (p = 0.02, 56 qubits), −0.55 (81 qubits) before the "mirror check" [§5]. The two variables are each qubit's |2> population at the start of a shot (from a fit to eight flip/swap sequences) and its calibrated readout fidelity, as a Spearman correlation. The mirror check refits each qubit's eight sequences from 24 starting points, on both sides of the trade between |2> population and the chance that a |2> qubit reads 0, and counts a qubit as ambiguous when equally good fits (cost within 1.0 of the best) span more than 0.5 percentage points of |2> population: 25 of the 81 clean-fit qubits are ambiguous [code/mirror_check.py; reads/mirror_check.json]. On 25 qubits readout blur and |2> could not be separated [§5]. On three qubits (q67, q76, q85; q76 reads 1 on every shot) |2> could not be reached or read; they lie on a straight line of neighbours [§5, §6].
- *Carried*: q63 about 2.5%, q78 about 1.9%, q40 about 2.0%, draining within 60 us in all three batches; q61's drain in the first batch did not repeat [§5].
- *Blinking*: |2> read in three batches minutes apart: q52 2.0 / 2.2 / 8.9%, q36 8.5 / 9.9 / 18.9%, q5 1.7 / 5.3 / 1.7% [§5]; these qubits show no shot-to-shot memory [§6]; in a following hour of eight checks they did not blink (q52 one excursion) [§9]. The |1>-|2> frequency (Ramsey at 1.5 us) on 31 qubits with readable contrast jumped rarely and independently, about once per 7.5-minute interval, with no chip-wide simultaneous jump; two qubits hopped among a few levels held about 15 minutes with their ordinary readout flat [§9].
- *Carry-over through reset*: on q0 the reset clears |1> but sometimes leaves |2>, and the |2> left by one shot sets how the next shot starts (p = 0.001; about 0.01 after the splits examined) [§18]. An active reset made of a measurement and a conditional flip does not act on |2> [1; §20]. Section 3.1 uses this as a positive control for carry-over.

**IBM (ibm_marrakesh, ibm_kingston, ibm_fez; three two-readout jobs of 28 September)** [§2, §22]: dat5rslvr3kc73el0klg, dat9ebbg95ks73egis2g and dat9o2ihcrkc73dts3jg, 78 qubits each, 4000 shots per circuit, the backend's default 250-us gap between shots; a shot counts as outside both clouds when it lies more than 4 widths from both, the cut checked on half the references. The script that counted the shots below was not kept.
- Shots outside both the |0> and |1> clouds on both of two readouts: 134 on ibm_marrakesh against 6.5 expected by chance (prepared |0>), 98 on ibm_kingston against 2, about none on ibm_fez [§2]. On the qubits with the largest counts the rate is the same for prepared |0> and |1>: an X gate, which acts within {|0>, |1>}, does not move it [§2].
- *Standing*: ibm_marrakesh q14, about 1-3% at every inter-shot gap; q24, a floor of about 1% plus a carried part [§2].
- *Carried*: ibm_marrakesh q26, 4.6% of shots at 20-us gaps, gone by 250 us [§2]; two ibm_kingston qubits are also listed as carried: q58, 1.6 % rising to 6.1 % of shots at 20-us gaps and 0.8 % at 1-ms gaps, and q62, 2.3 % to 9.4 % and 0.5 % [§2, §5]. Chip-wide on ibm_marrakesh (74 readable qubits, inter-shot gaps 20 us to 2 ms), the median qubit reads 0.84% stray excitation at a 20-us gap above a 0.31% floor, draining on a ~72 us scale; nine per-qubit fits give drain times of 24-193 us (middle half 51-73 us) against relaxation times of 9-272 us, with no resolved relation (rank −0.6, p = 0.09) [§17, §20]; the nine fits were selected from 74 qubits [§22]. The carried excitation is not flipped by an X gate, sits in its own I/Q region off the |0>-|1> line on the same side on every chip, and lives ~55-80 us [§21].
- *Blinking*: ibm_marrakesh q60, 5-9% of shots in some jobs and about 0 in others minutes apart; q126 the same; q66, 13% in one job [§2].


### 3.6 Rigetti Cepheus, 4 October: the train on two pairs of levels and the spectators' readout

Every qubit is in every circuit; each qubit's |1>-|2> transition is driven by a 32-ns DRAG-Gaussian pulse on its |1>-|2> frame with a per-qubit amplitude (99 of 107 qubits reach |2>; median amplitude 0.155 against 0.150 on 28 September, per-qubit change median 0.000 [rigetti_20261004/tune_vs_0928.txt]); populations of |1> and |2> are solved per qubit from a plain read and a swap-then-flip read on an eight-sequence readout model calibrated in the same batch [code_20261004/rigetti_time.py; code_20261004/readrigetti_time.py; code_20261004/rigetti_gamble.py]. 900 shots per circuit, 1500 per calibration circuit. No outcome was written for any run [§192-§217].

**The push train, every qubit driven.** Ten X gates after intervals of 1, 3, 8 and 20 us from |0>: +0.127 / +0.110 / +0.066 / +0.025 against one exponential through 30 us, +0.073 / +0.048 / +0.037 / +0.016 against each qubit's own decay curve read in the same batch (0.83 / 0.63 / 0.33 at 3 / 10 / 30 us against 0.90 / 0.69 for one exponential); |2> 0.005-0.014 in every arm [rigetti_20261004/read1_raw_nocut.txt; §193]. Ten X gates back to back move |0> by +0.076 and |1> by −0.068: on this chip the gate error is the size of the excess. A second batch 188 s later repeats the short intervals and moves the long ones (20 us, own curve +0.016 -> +0.029) [rigetti_20261004/read2_raw_nocut.txt; §194]. The excess against the own curve depends on the readout-quality band (3 us: +0.041 / +0.053 tight, +0.026 / −0.008 middle, −0.028 / −0.013 loose, two batches); against one exponential it is +0.07 to +0.13 in every band [§194].

**The gate error and the neighbours.** Seven emitters at least five links apart, ten X gates back to back, their 22 neighbours at rest, driven in step, or held on the equator, interleaved, three rounds 3 minutes apart, each round with its own readout calibration: read-1 fraction 0.0643 / 0.0641 / 0.0584 (neighbours at rest), 0.0646 / 0.0656 / 0.0560 (driven in step), 0.1102 / 0.1010 / 0.1038 (on the equator) [rigetti_20261004/triB_raw.txt; §206]. Readout models were steady (r0 0.995-0.997).

**A spectator beside a |2> neighbour, all three clocks in one batch.** q0 at rest, in |1> or in |2> for 0.5-6 us; q0's own |2> population 0.893 / 0.888 / 0.847 / 0.733 / 0.586; q9 (one link) moves by −36.1 / −34.6 / −41.4 deg/us at 0.5 / 1 / 2 us with q0 in |2>, q1 by −27.5 / −19.4 / −21.0; with q0 in |1>, q1 −8.5 / −7.8 / −5.9 and q9 +0.5 / +5.9 / +1.7; 101 spectators three or more links away: medians −0.6 to +1.6 [rigetti_20261004/triA_raw.txt; §205]. q9's pull is −35 to −41 deg/us here against −62.1 ± 0.6 on 28 September (Section 3.4).

**Spectators reading a train on the |1>-|2> pair.** The seven emitters, prepared in |1> or |2>, receive ten |1>-|2> swaps over L = 1, 2 and 4 us; every other qubit is a free spectator. References at each L: emitters held in |1> and held in |2>. The time the emitters spend in |2>, as a spectator reads it, is (turn in the train − turn held in |1>) / ((turn held in |2> − turn held in |1>) / L); it is set beside the time laid (5 intervals of L/10) and the time booked from the emitters' own decay from |2> and from |1> read in the same batch [code_20261004/rigetti_triangle_d.py; code_20261004/readrigetti_triangle_d.py].

**Table 15.** Time in |2> during a ten-swap train on the |1>-|2> pair: laid, booked from the emitters' own decay, and read by the 22 spectators one link away (median and quartiles; where the wrapped and unwrapped readings differ both are given, with the quartiles of the unwrapped) [rigetti_20261004/triD_raw.txt].

| Start | L (us) | Laid (us) | Booked (us) | Spectators, 1 link (us) | Pull, level 2 minus level 1 (deg/us) |
|---|---|---|---|---|---|
| from 1 | 1 | 0.50 | 0.48 | 0.56 [0.36, 0.80] | −6.87 |
| from 1 | 2 | 1.00 | 0.91 | 0.92 [0.64, 1.04] | −7.31 |
| from 1 | 4 | 2.00 | 1.68 | 1.48 / 1.83 [0.55, 2.13] | −2.96 / −3.93 |
| from 2 | 1 | 0.50 | 0.49 | 0.64 [0.42, 0.81] | −6.87 |
| from 2 | 2 | 1.00 | 0.96 | 1.03 [0.80, 1.42] | −7.31 |
| from 2 | 4 | 2.00 | 1.85 | 2.09 [0.96, 2.50] | −2.96 / −3.93 |

At two links the pull is within ±1.5 deg/us of zero and the spectators' quartiles straddle zero. Each push adds 32 ns not counted in the laid column (0.16 us at half weight over ten pushes). A |0> start (the swap has nothing to act on) reads −0.20 / +0.07 / −0.78 us at one link. Across a second batch with 4, 10 and 20 swaps at each L, spectator-read over booked time is 0.86 / 1.30 / 1.16, 1.08 / 1.20 / 1.22, 1.15 / 1.47 / 1.14 (start |1>, N = 4 / 10 / 20, L = 1 / 2 / 4 us) and 0.80 / 1.54 / 1.28, 1.22 / 1.25 / 1.31, 1.04 / 1.46 / 1.24 (start |2>): no order with N, and the L = 2 us column is the highest in all six; the booked time repeats between the batches within 0.03 us, and the emitters' end state follows N (start |1>, |2> population after the train 0.15-0.19, 0.28-0.35, 0.35-0.38 for N = 4, 10, 20) [rigetti_20261004/triE_raw.txt; §211].

**The spectators' |2> ruler, round to round.** Emitters held at rest, in |1> or in |2> for 0.25-6 us, three rounds 3 minutes apart, each with its own readout calibration; the populations come from the same shots. Per unit population, the one-link spectators' |2> pull is −4.9 to −17.6 deg/us over windows and rounds (median −9.7, quartiles −11.2 and −8.0; at 4 us −8.0 / −9.3 / −8.1, at 0.5 us −17.6 / −15.2 / −7.4), the |1> pull −3.9 to +3.3 (median −1.1); the spectators' own drift between rounds (emitters at rest) is −1.2 to +3.7 deg/us; the populations repeat within 0.01-0.04 [rigetti_20261004/triF_raw.txt; §213].

**The spectators' state in the emitters' readout.** The emitters held in |2> for 0.5, 2 and 4 us, with every other qubit at rest; on the equator during the delay and rotated back by a full turn; on the equator and rotated by a further quarter turn (as in the runs above); in |1> throughout; or at rest during the delay and put in |1> just before readout. Populations are solved with three readout models: the shared calibration (every qubit runs the eight sequences), and emitter-only calibrations with the other qubits at rest or in |1> [code_20261004/rigetti_triangle_g.py; rigetti_20261004/triG_raw.txt; §215].

**Table 16.** The emitters' |2> population by the other qubits' state; three readout models (shared / emitter-only, others at rest / emitter-only, others in |1>).

| Other qubits | 0.5 us | 2 us | 4 us |
|---|---|---|---|
| at rest | 0.897 / 0.889 / 0.990 | 0.824 / 0.814 / 0.910 | 0.709 / 0.696 / 0.784 |
| equator, turned back | 0.817 / 0.801 / 0.894 | 0.715 / 0.697 / 0.781 | 0.638 / 0.621 / 0.700 |
| equator, quarter turn | 0.805 / 0.790 / 0.880 | 0.714 / 0.696 / 0.782 | 0.635 / 0.618 / 0.697 |
| in 1 throughout | 0.719 / 0.698 / 0.778 | 0.668 / 0.648 / 0.728 | 0.572 / 0.554 / 0.624 |
| in 1 at readout only | 0.731 / 0.711 / 0.795 | 0.678 / 0.657 / 0.736 | 0.577 / 0.556 / 0.630 |

The other qubits' state at readout, not during the delay, sets the reading (|1> throughout and |1> at readout only agree within 0.012; the two equator arms agree within 0.012 and sit between rest and |1>). The ratio to the rest arm is 0.815 / 0.823 / 0.814 (|1> at readout only) at every delay, and the decay shape, 4 us over 0.5 us, is 0.78-0.80 in all five arms. The matched model (others in |1>) takes about 40% of the difference. With the emitters in |1> the shift runs the other way (|1> population 0.935 -> 0.945, |2> 0.031 -> 0.018 at 0.5 us). In the opposite direction, emitters put in |1> or |2> at readout move the spectators' read by −3.0 to +2.2 deg (medians), and the pairing of read axes used throughout this section shifts the |2>-held arm by at most 0.75 deg/us at one link [rigetti_20261004/triH_raw.txt; §217].

**After a recalibration.** Cepheus recalibrated at 18:02Z; repeated afterwards, the order of the emitters' |2> reading by the spectators' state (rest > equator > |1> at readout) holds in all 15 delay-round cells under all three readout models, the |1>-at-readout / rest ratio is 0.82-0.89, and the upper-pair train reads the same booked time within 0.04 us [rigetti_20261004/sealA_raw.txt; rigetti_20261004/sealB_raw.txt; §220-§222]. The ratio of the two emitter-only readout models (others in |1> against others at rest) is 1.071-1.096 in all 45 cells after the recalibration, rising with the delay, and 1.114-1.133 before it [rigetti_20261004/rulers_as_rows.txt; §226]. In one round one emitter (q62) read low on |2> for about two seconds, three consecutive circuits, then returned [rigetti_20261004/sealA_dip_bonefish.txt; §221].

**The train against each interval's own decay at five spacings.** Ten X gates from |0> on all 107 qubits after intervals of 1, 2.618, 6.854, 17.944 and 46.979 us, against each qubit's decay over exactly that interval read three times in the same batch: +0.0042 / +0.0246 / +0.0174 / +0.0080 / −0.0198; ten back-to-back gates +0.0904 [rigetti_20261004/two_raw.txt; code_20261004/rigetti_two_call.py; §232].

### 3.7 Calls written before the data

From 4 October we wrote a number, or a stated criterion, for some runs before their data existed, hashed the text (sha256) and kept the file unchanged after; the files are in the release [calls/; SHA256SUMS.txt]. A file's hash is fixed when it is written; the time the data first existed is the job's or task's creation time on the vendor's record [RUN_INDEX.csv]. Two of the calls below sit in frozen run scripts, whose combined hash is fixed at freezing (Section 2.7).

**Where the called numbers come from.** The calls were taken from a working framework of ours ("The Bonefish", published separately at heuremen.org/7.pdf). It enters this paper only as the source of each called number: a spectator's timing of a readout at 12/11 of the vendor's stated duration; the measured qubit's own decay per readout at φ = 1.618 of it, and so at φ × 11/12 = 1.483 of the spectator's; a push-train excess that steps down a ladder (1/12)(1/φ)ⁿ = 8.33, 5.15, 3.18, 1.97, 1.22, 0.75 ... % as the interval grows; and a few ratios between readings (1.5, 0.750). No number in Sections 3.1-3.6 is compared to any of these; the only comparisons are the calls below.

**Table 17.** Every call written before its data, in order. Times are EDT on 4 October. "Width": one combined width of the reads' spread and shot resampling. Quantities: (a) slope per push against each interval's own decay; (b) excess after ten pushes against each interval's own decay, all 107 qubits, at 1 / 2.618 / 6.854 / 17.944 / 46.979 us; (c) excess against one exponential at 10 / 30 / 70 / 100 us, three reads; (d) spectator / vendor, measured qubit / vendor, measured qubit / spectator, 3-and-9 slope, three reads; (e) measured qubit / spectator; (f) spectator hand kept through 27 readouts over hand kept through the same laid time.

| # | Call (sha256, first 16) | Written / data from | Chip | Called | Width (as hashed; value used) | Read | Against the call's criterion |
|---|---|---|---|---|---|---|---|
| 1 (a) | frozen five_slope.py (0e245906ff3519c1) | 13:10 / 13:11 | ibm_fez | ibm_pittsburgh's −0.00106 ± ~0.0008, below zero from 6 pushes | none stated (about one combined width, 0.00084, per the ledger) | −0.00182 ± 0.00027; −0.0050 at 6 | no width stated; 0.9 widths |
| 2 (a) | frozen five_slope_kingston2.py (d087500138bcddba) | 16:13 / 16:13 | ibm_kingston | the same | none stated (about one combined width, 0.00087, per the ledger) | −0.00198 ± 0.00035; −0.0067 at 6 | no width stated; 1.05 widths |
| 3 (b) | TWO_CALL_CEPHEUS (8156c88650870b97) | 15:25 / evening | Cepheus-1-108Q | 8.33 / 5.15 / 3.18 / 1.97 / 1.22 % | none stated | +0.42 / +2.46 / +1.74 / +0.80 / −1.98 % | the size called: misses at all five |
| 4 (c) | IBM_FEZ_CALLS (dad0ff67e62953ed) | 18:06 / 18:07 | ibm_fez | 3.18 / 1.97 / 1.22 / 0.75 % | one combined width (0.33 / 0.23 / 0.32 / 0.12 points) | 5.99 / 3.08 / 1.69 / 1.43 % (± 0.3-0.4) | one width: misses at all four |
| 5 (d) | the same | 18:06 / 18:07 | ibm_fez | 1.09 / 1.62 / 1.48 | one combined width (read spread 0.025 / 0.22 / 0.20) | 1.024 ± ~0.025 / 1.54 / 1.51 | each within one width: misses (2.6 widths on the first) |
| 6 (e) | the same | 18:06 / 18:07 | ibm_fez | 1.5 | one combined width (read spread 0.26) | 1.509 (1.344 / 1.808 / 1.375; spread 0.26) | one width: lands |
| 7 (f) | the same | 18:06 / 18:07 | ibm_fez | 0.750 | one combined width (0.034) | 0.844 (0.872 / 0.855 / 0.807) | one width: misses (2.8 widths) |
| 8 | GOD_TAX_CALL_BOSTON (47a0377895b3a632) | 18:26 / 4 Oct night | ibm_boston | spectator / vendor over 12/11 below 1 by more than one width, and measured qubit / spectator within 3 % of 1.4832 | outside: one combined width (0.038); inside: ±3 % | 0.988 (0.3 widths below 1); 0.843 | both legs: misses |
| 9 (d) | ONE_SIX_CALL_BOSTON (bd7b491793c91d75) | 19:39 / 4 Oct night | ibm_boston | 1.09 / 1.62 / 1.48 | one combined width (0.042 / 0.136 / 0.096) | 1.078 / 1.348 / 1.250 | each within one width: misses (first ratio within; 2.0 and 2.4 widths) |
| 10 (e) | the same | 19:39 / 4 Oct night | ibm_boston | 1.5 | one combined width (0.096) | 1.250 | one width: misses (2.6 widths) |
| 11 (a) | FIVE_THREE_CALL_BOSTON (bfe1b824ccf45368) | 19:40 / 4 Oct 23:23 | ibm_boston | below zero from 6 pushes; negative under all three rulers; within one width of &minus;0.00190 | one combined width (0.00036) | &minus;0.0035 at 6; &minus;0.00139 / &minus;0.00148 / &minus;0.00139 | first two hold; the slope 1.4 widths out |
| 12 (f) | the same | 19:40 / 5 Oct | ibm_boston | 0.750 at 32 readouts | one combined width (the reads' spread; not printed) | 0.99 (1.000 / 0.901 / 0.991 by class) | one width: misses |
| 13 | BONEFISH_NUMBERS_BOSTON (89397820188cf2a9) | 20:26 / 5 Oct 02:10 | ibm_boston | ladder pace 0.921 (three jobs) | 0.073 + its own fit width (0.177) | 1.217 &plusmn; 0.104 | 0.073 + fit width: misses (1.67 widths) |
| 14 (a) | the same | 20:26 / 4 Oct 23:23 | ibm_boston | slope &minus;0.00110 per push | one width (0.00029) | &minus;0.00139 &plusmn; 0.00029 | one width: on the edge (1.0 width) |
| 15 | TOMORROW_CALLS (eb98f85caf8e170c) | 20:12 / 5 Oct 04:05 | Cepheus-1-108Q | the emitters' &#124;2&rang; at 4 us, others half-way, 0.618 | one combined width: round spread and resampling (0.0064); the readout models' spread (0.025) was not in the hash | 0.631 (0.638 / 0.631 / 0.624) | one width of round spread and refit resampling: misses (2.0 widths); 0.5 widths with the readout models' own spread counted |
| 16 | PHOENIX_CALL (93514fc06e84f143) | 5 Oct 07:49 / 07:53 | ibm_phoenix | spectator / vendor below 12/11 | threshold only: below 12/11 | 1.007 (&minus;7.7 %), about 2 widths below | holds |
| 17 (e) | the same | 5 Oct 07:49 / 07:53 | ibm_phoenix | measured qubit / spectator within 4 % of 1.4832 | ±4 % | 1.345 (1.529 / 1.286 / 1.220) | misses on the mean (read 1 inside) |
| 18 (a) | the same | 5 Oct 07:49 / 07:53 | ibm_phoenix | rung 8 per push; below zero from 6 pushes; negative under all three rulers | one combined width (0.00058) | &minus;0.00058 / &minus;0.00091 / &minus;0.00155 by ruler; +0.0019 at 6 | the sign holds; rung and depth miss |
| 19 (f) | the same | 5 Oct 07:49 / 08:12 | ibm_phoenix | 0.750 at 32 readouts | one combined width (unreadable) | the spectators' hand is at the floor (0.07&ndash;0.23) by 12&ndash;16 readouts | unreadable |
| 20 | TOMORROW_CALLS (eb98f85caf8e170c) | 4 Oct 20:12 / 5 Oct 14:01 | ibm_pittsburgh | spectator / vendor over 12/11 below 1 by more than one width | below 1 by more than one resampling width (0.021) | 0.975 (1.2 widths below; 1-9 fit 0.964) | holds |
| 21 | TIME_LEG_T2T1_CALL (abcc6db23328e666) | 4 Oct night / 5 Oct 14:01 | ibm_pittsburgh | measured qubit / spectator x the day's T2:T1 (1.138), within 4 % of 1.4832 | ±4 % | 1.385 (1-9 fit 1.466) | 4 %: misses (&minus;6.6 %, 0.7 of its own width); 1-9 fit &minus;1.1 % |
| 22 | PHOENIX_DAY2_CALL (c48719b13bbfff0a) | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | spectator / vendor below 12/11 | threshold only: below 12/11 | 1.081 (1.170 / 0.990 / 1.084), &minus;0.9 %; one combined width of shots, reads and the two rulers 0.068; 1-9 fit 1.052 (&minus;3.6 %) | below on both rulers; 0.15 combined widths, so the width does not separate it from 12/11 |
| 23 | the same | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | measured qubit / spectator x max(1, the day's T2:T1), within 4 % of 1.4832 (T2:T1 0.851, so x 1) | ±4 % | 1.296 (1.138 / 1.406 / 1.344); combined width 0.118; 1-9 fit 1.347 | 4 %: misses (&minus;12.6 %, 1.6 combined widths); 1-9 fit &minus;9.2 % |
| 24 | the same | 5 Oct 08:31 / 6 Oct 10:01 | ibm_phoenix | spectator hand's e-fold in laid time over its e-fold in readouts, over the vendor's duration, within 4 % of 0.750 in each distance class (1 / 2 / 3+ links) | ±4 % | 0.597 / 0.938 / 0.857 (three-job means); a curved-decay ruler on the same hands 1.03 / 1.05 / 1.00 | 4 %: misses in every class on the named ruler |

Two disclosures stand in the call files themselves: the Cepheus call's map from interval to ladder step was chosen after an earlier Cepheus batch at 1 / 3 / 8 / 20 us [§193], and the ibm_fez TWO call's map was read off ibm_pittsburgh's three reads [§229]. A re-read of the Cepheus run with the measured push error added to the bookkeeping brings the 1-us value to +8.84 % [rigetti_20261004/two_push_error_removed.txt; §237]; it was not called and is not scored.

**The clock ratio.** The role of each chip's stated T2:T1 in the time leg (row 21) was noticed after the fact, on 4 October, and only then written and hashed forward [calls/TIME_LEG_T2T1_CALL_20261005.txt]; its first forward read missed its own stated 4 % on the primary ruler (−6.6 %, inside its own width). It is reported here as an open ruler, not as a leg of the result.

**The ibm_phoenix rows.** On the square lattice (rows 16-19 and 22-24) the two rulers this paper compares disagree by a factor of 2.7 on one call, and one call is unreadable; those rows are printed with that disagreement standing beside them, and every count below is also given without them.

**The second ibm_phoenix day (rows 22-24).** Three disclosures. (i) Row 24's ruler was built on 5 October from the spectators of a different run type (no driven neighbours; readout counts 1-8) [§262]; the run armed for 6 October holds its spectators half-way beside driven neighbours and reads out 1-9 times, so the ruler was carried to it after the data, by a reader written that day [code_20261006/readlook_classes.py; code_20261006/efold_three_seats.py]. On the 5 October job of the 6 October type the same ruler reads 0.594 / 0.970 / 0.860, so it repeats from day to day on one run type and differs between run types on the same chip and day. (ii) The ruler moves with its own fit window: both hand curves bend, and on the 5 October spectators that gave 0.760 / 0.754 / 0.777 [the ledger printed 0.754 for one link; erratum §275], leaving out the 8-readout point gives 0.588 / 0.579 / 0.659. A curved-decay fit (ln h = &minus;(x/T)&sup2;) gives 1.00-1.06 of the vendor's duration on both run types, both days and every class; matching the laid time that leaves the same hand gives 1.02-1.13. All three are printed [reads_20261006/efold_three_seats_phoenix_20261006.txt]. (iii) The call asked for the day's T2:T1 to be read from the vendor's record before firing; it was read after the data (0.851) [reads_20261006/phoenix_maker_record_oct6_20261006.txt]. The record stamped 5 October 09:44 and the one stamped 6 October 12:25 carry the same median T1 and T2 to 0.1 us, and a request for the record in force at a given time returned one stamped later; row 23's factor is 1 under either reading.

**Not yet scored.** Hashed before its data: on ibm_pittsburgh on 6 October, the spectator / vendor ratio and the time leg with the chip's clock ratio [calls/TOMORROW_CALLS_20261005.txt; calls/TIME_LEG_T2T1_CALL_20261005.txt, abcc6db23328e666]. An erratum written after hashing corrects one sentence in two of the ibm_boston files: the chip had three earlier jobs from us, on 2 October [calls/ERRATUM_BOSTON_20261004.txt].

**Score so far.** Twenty-four calls read: 4 land (rows 1, 6, 16, 20), 1 meets its threshold by less than one width (row 22), 2 sit on the edge of their own width (rows 2, 14), 2 partly hold (rows 11, 18), 1 lands only when the readout models' own spread is counted in the width (row 15), 13 miss, 1 is unreadable (row 19).

**What chance would score (the stone test).** The framework holds about two dozen ratios between 0.25 and 3.5 and a seven-step ladder [code_20261004/stone_density.py]. A value drawn evenly on a log scale between 0.5 and 2 lies within 1 / 2 / 3 / 5 % of at least one of the 24 ratios 20 / 35 / 48 / 72 % of the time; between 0.25 and 3.5, 15 / 27 / 37 / 56 %. A value between 0.4 and 9 % lies within 1 / 2 / 3 / 5 % of a ladder step 4 / 9 / 13 / 23 % of the time [reads_20261004/stone_density_20261004.txt]. Because a match chosen after the fact from that many numbers is cheap, this paper names none; a call names one number before the data. For one named number, a value drawn evenly on a log scale over a factor of two either side lands within ± w with chance ln((1 + w)/(1 − w)) / ln 4: 4.3 % for w = 3 %, 25 % for the ± 17 % band of the one call that landed. Whether the calls taken together exceed chance is not claimed: the framework is probabilistic by construction, the calls' widths differ from one another (each is printed with its row), and the choice of null distribution is left to the reader. One worked example, under the log-uniform null above and with every assumption labelled, is in the release [reads_20261005/CHANCE_TABLE_20261005.md].

---

## 4 Limitations

1. **Replication depth.** The push train with intervals swept and the decay read in the same jobs has three jobs on each of ibm_marrakesh and ibm_kingston and one on ibm_pittsburgh (4 October). The interval-length job with own-interval arms (2 October) is one of three planned (runs 122-123 frozen, not fired) [§157], and the spectator stopwatch one of three [reads/witness_run.txt]. The 4 October readout-timing run has one job on ibm_pittsburgh, and the free-spectator run none there. Every own-interval number of 2 October and every frame-held spectator number rests on one job.
2. **Comparisons within jobs only.** Between jobs minutes apart, single-qubit decay times and levels move by more than the shot widths (Section 3.1) [§117, §119]; the same circuit read +0.0200 ± 0.0016 (push run) and +0.0126 ± 0.0032 (interval-length job) against one-exponential bookkeeping [reads/close_push.txt; reads/noname_read1.txt]. Quoted widths are shot-resampling widths; three-job widths assume independent jobs and do not include this wander. The spectator-timed readout duration and the single-readout cost at the end of a 300-us idle scatter between jobs beyond their widths (Section 3.2).
3. **Statistic.** Means over readable qubits and median-qubit values differ in places (Section 3.3; Table 2, hold run). No qubit is removed beyond the readable-cloud rule, so qubits with decay times of about 6 to 55 us (q31, q36, q57, q66, q90) and one that reads below its |0> reference at 300 us (q137) are inside the means [§121; reads/tail_run.txt].
4. **Not measured or not controlled.** (a) T1 shot by shot within a job: the non-exponential account rests on the decay shape within jobs and on decay-time wander between jobs. (b) |2> on IBM: not read directly on the path used; bounded indirectly (Section 3.1). A push train with a direct |2> read on Rigetti was designed and not run [§154]. (c) Pulse shapes: native gates only; an X gate built from two half-gates, the nearest available way to change leakage without changing the operation, was not run on the push train [§146, §147]. (d) What the vendor schedules during a readout: ibm_pittsburgh's configuration places all 156 qubits in one measurement group [reads/pittsburgh_config_timing.json]; whether readout tones reach unmeasured qubits during a readout block, and what fills the difference between the stated and the spectator-timed duration, were not measured. (e) The halfway start's offset and ibm_kingston's start-1 column (Section 3.1).
5. **Post hoc.** No numerical predictions were written before the runs of Sections 3.1-3.6, except the calls of Section 3.7. The 7.5% family-wise figure covers the ten arms of one job. These jobs are part of 72 IBM jobs fired on five chips over 2026-10-01/02 (71 landed) [§141], after exploratory analyses that counted about 3.44 million tests across 98 analyses through 2026-09-29 [§29]; no program-wide correction is applied.
6. **Method dependence.** On ibm_pittsburgh two analysis methods give readout-timing ratios 4-13% apart for the same readout (Section 3.2); both are given, and no ratio here is offered as a match to any constant.
7. **Rigetti, one day.** Section 3.6 rests on one day of 680 tasks on one chip; the spectators' |2> ruler moves 30-50% between rounds at a single delay, and the emitters' readout depends on the other qubits' state at readout (Table 16).
8. **Our own load.** Our first 197 jobs on six IBM chips, 24 September to 4 October (every key the service lists [RUN_INDEX.csv]; the 29 jobs fired after them are not in this comparison) set against the vendor's daily calibration record for 75 chip-days (12 with our jobs): the change at the next calibration does not follow our jobs that day (rank correlation +0.18 for T1, −0.02 for T2, −0.05 for readout error; after our busiest days, 37 jobs on ibm_fez on 28 September and 36 on ibm_pittsburgh on 2 October, T1 moved +5.9 and +11.3 us against a quiet-day spread of 12.8 us) [reads_20261004/our_looks_vs_maker_record_full197_20261004.txt; code_20261004/our_load_full.py]. A first read with the 121 jobs one key lists gave +0.18 / −0.03 / −0.04 [reads_20261004/our_looks_vs_maker_record_20261004.txt; §244]. Across the twelve readout-timing jobs, spectator / vendor does not follow our earlier jobs on the same chip (rank correlation +0.05) [reads_20261004/my_looks_vs_the_tax_20261004.txt; §243].
9. **The curve bookkeeping below 30 us** is interpolated between the 0- and 30-us points; the 5-10-us residuals of Section 3.1 rest on it.
10. **Earlier analyses.** The third-level results and the ibm_fez / Rigetti spectator results (Sections 3.4-3.5) come from analyses of 2026-09-24 to 09-29. Appendix A logs every run family with its read, the scripts that were kept are in the release, and the text says where a script was not kept (three numbers: the 3.5-us readout cost, the 134 / 98 outside-cloud counts, and the 25-of-31 ibm_fez job selection).

---

## 5 Data and code availability

The data release, archived at Zenodo (doi:10.5281/zenodo.23169756), holds, with a sha256 for every file [SHA256SUMS.txt; 913 entries]:

- **reads/** (38 files): the read outputs quoted here, the spectator role maps, and the vendor configuration fields read at fire;
- **code/** (42 files): frozen run scripts, the shared modules (common.py, live.py, parse_payload.py, analyze.py) and the analysis scripts;
- **fire_logs/** (fire_logs_after.txt is empty; the 4 October fire logs are fire_logs_time.txt, fire_logs_look.txt, fire_logs_witness.txt);
- **reads_20261004/**, **code_20261004/**: the 4 October tables (generated from the jobs), per-chip dumps, role maps, configuration and duration reads, the decay-bend read, and the run and reader scripts;
- **rigetti_20261004/**: every 4 October Rigetti batch as raw shots (.npz), the read outputs, the per-qubit tuning, the coupling map, and the task lists (task IDs with the account number blanked);
- **reads_20261005/**, **code_20261005/**, **rigetti_20261005/**: the 5 October reads, run and reader scripts (with the provenance check), and every 5 October Rigetti batch as raw shots;
- **calls/**, **freeze/**, **run_index/**, **early/**: every hashed call with its sha256 and OpenTimestamps proof, the freeze records, the job and task index, and the 24-29 September run folders;
- **trail/**: a copy of the correction log (thetrailtothepast.com) as of the archive date, so the corrections outlive the domain;
- **SHA256SUMS.txt**.

**Table 18.** First 12 hex digits of the sha256 of the files used most (full values in SHA256SUMS.txt).

| File | sha256 (first 12) | File | sha256 (first 12) |
|---|---|---|---|
| code/common.py | c617b49d7d4c | reads/close_push.txt | 59655cd6134c |
| code/push.py | fab8f31212d5 | reads/close_looktime.txt | 6c791c37fd97 |
| code/pushrep.py | 52eec89017b6 | reads/close_giveback.txt | 2513ec3903a0 |
| code/noname.py | 5876e1065595 | reads/noname_read1.txt | eb81afff39d8 |
| code/readnoname.py | 4beb62d96058 | reads/rep_marrakesh_read1.txt | 58e791f0e3ed |
| code/readclose.py | 969c53ceb77a | reads/rep_kingston_read1.txt | 46522636b6ac |
| code/looktime.py | 3cee772827f4 | reads/hold_run.txt | e06c3a17570f |
| code/giveback.py | 303116ff0368 | reads/witness_run.txt | 63a013a5e0e7 |
| code/hold.py | 42722568fd39 | reads/jump_rerack.txt | 17efa28f9ef1 |
| code/readhold.py | f7c672486001 | reads/tail_run.txt | 5570c55bbe69 |
| code/witness.py | fee6bd24d087 | code/jump.py | ec6a1898275b |
| code/readwitness.py | 84ebfbb4312b | code/rerack.py | ff700fe06259 |
| code/tail.py | 5251f897d93e | code/readtail.py | 2b0d5c0e52b4 |
| code/lone.py | caf8bea7bb5b | code/between.py (frozen, not fired) | c832aab64cac |

Freeze hashes combine the code hashes with each run's circuit ledger [code/common.py]. The interval-length job's combined freeze hash begins ce322e77 and ends 5b15 [§145]; the unfired halfway-separation run's begins 49e64f32 and ends 12a7 [§149]. The IBM job ID of run 121 is db00t8k92g1c7399m6hg [§145]. Every IBM job ID (226 jobs, six chips, 24 September - 5 October) and every Braket task ID (3,035 tasks on Cepheus-1-108Q, 25 September - 5 October; 2,899 completed, 116 cancelled, 20 failed), with chip, creation time and status as the vendors' own services list them, is in run_index/RUN_INDEX.csv, with the scripts that pulled the lists [run_index/pull_history.py; run_index/pull_other_keys.py; run_index/build_index.py]. The full freeze record of every fifth-run job (150 records, four of them for runs armed for 6 October: code hashes, circuit-ledger hash, combined hash, shots) is in freeze/. Ten run scripts of 4-6 October (eight fired, 20 runs; two armed for 6 October) list a sibling script in their freeze, so those records hash the sibling and not the file that fired; the fired files are hashed and timestamped beside them [calls/SIDE_FREEZE_20261005.txt], and their circuits are rebuilt and compared with the vendor's stored inputs run by run [data_provenance_20261005.txt]. The raw result payloads of the earlier runs and a physics-only extract of the run ledger [§170] go with the archived release.

---

## Acknowledgments

We thank Shuttle, whose passes over an earlier draft supplied the thermal-population algebra, the randomized-preparation design, and the T1-fluctuation account of the push-train excess [§146-§149, §174]. We acknowledge the use of IBM Quantum services for this work. The views expressed are those of the authors, and do not reflect the official policy or position of IBM or the IBM Quantum team. Rigetti runs used Amazon Braket.

**AI use.** This work was done with AI assistance. Bones, an inorganic intelligence (an AI system), designed the runs with the author, wrote the run and analysis code, and drafted the text; the author answers for every line.

## References

1. Karalekas, P. J. et al. A quantum-classical cloud platform optimized for variational hybrid algorithms. Quantum Sci. Technol. 5, 024003 (2020). doi:10.1088/2058-9565/ab7559
2. IBM Quantum, Qiskit Runtime (qiskit-ibm-runtime 0.49, SamplerV2), https://quantum.cloud.ibm.com (accessed 24 September - 4 October 2026).
3. Amazon Braket, Rigetti Cepheus-1-108Q, https://aws.amazon.com/braket/ (accessed 25 September - 4 October 2026).
4. Klimov, P. V. et al. Fluctuations of energy-relaxation times in superconducting qubits. Phys. Rev. Lett. 121, 090502 (2018). doi:10.1103/PhysRevLett.121.090502
5. Schlör, S. et al. Correlating decoherence in transmon qubits: low frequency noise by single fluctuators. Phys. Rev. Lett. 123, 190502 (2019). doi:10.1103/PhysRevLett.123.190502
6. Burnett, J. J. et al. Decoherence benchmarking of superconducting qubits. npj Quantum Inf. 5, 54 (2019). doi:10.1038/s41534-019-0168-5
7. Carroll, M. et al. Dynamics of superconducting qubit relaxation times. npj Quantum Inf. 8, 132 (2022). doi:10.1038/s41534-022-00643-y
8. Müller, C., Cole, J. H. & Lisenfeld, J. Towards understanding two-level-systems in amorphous solids: insights from quantum circuits. Rep. Prog. Phys. 82, 124501 (2019). doi:10.1088/1361-6633/ab3a7e
9. Kandala, A. et al. Demonstration of a high-fidelity CNOT gate for fixed-frequency transmons with engineered ZZ suppression. Phys. Rev. Lett. 127, 130501 (2021). doi:10.1103/PhysRevLett.127.130501
10. Sundaresan, N. et al. Reducing unitary and spectator errors in cross resonance with optimized rotary echoes. PRX Quantum 1, 020318 (2020). doi:10.1103/PRXQuantum.1.020318
11. McEwen, M. et al. Removing leakage-induced correlated errors in superconducting quantum error correction. Nat. Commun. 12, 1761 (2021). doi:10.1038/s41467-021-21982-y
12. Sank, D. et al. Measurement-induced state transitions in a superconducting qubit: beyond the rotating wave approximation. Phys. Rev. Lett. 117, 190503 (2016). doi:10.1103/PhysRevLett.117.190503
13. Heinsoo, J. et al. Rapid high-fidelity multiplexed readout of superconducting qubits. Phys. Rev. Applied 10, 034040 (2018). doi:10.1103/PhysRevApplied.10.034040
14. Krantz, P. et al. A quantum engineer's guide to superconducting qubits. Appl. Phys. Rev. 6, 021318 (2019). doi:10.1063/1.5089550

---

## Appendix A. Run log

This appendix records what was fired and what was read.

**Conventions.**
- Source of every count: RUN_INDEX.csv (3261 rows: one per IBM job or Braket task on record since 1 Sep 2026). Completed = IBM DONE or Braket COMPLETED; cancelled = Braket CANCELLED; failed = IBM ERROR or Braket FAILED; queued = IBM QUEUED (shown separately). Entry counts read "N jobs (or tasks): completed/cancelled/failed".
- Dates are the created field of the index. IBM stamps are local (EDT); Braket stamps are UTC, so tasks fired in the evening of one EDT day can carry the next date.
- A family is one date, one vendor and one experiment label of the index; for the 2, 4 and 5 October IBM jobs the label is the run script that fired (the index shows a sibling script's name for some 5 October runs; see the provenance note), and run numbers are listed in the script entry. The 22 drift rounds of 5 October, each its own label in the index, are one entry.
- Source tags: [§n] is entry n of the run ledger parallax/THIRD_RUNG_20260928.md. Other tags are paths relative to  (the Biblioteca is notebook, cited with its dated heading).
- Numbers are copied as recorded. Values taken from JSON read files are shown to four decimals (the files hold more digits). "No read on file" means no read of that family was found in the ledgers or read files searched.
- Chip names are as in the index. Qubit labels (q0, q9, ...) are the vendors' qubit numbers.
- Provenance note (5 October): ten run scripts of 4-6 October (eight fired, 20 runs; two armed for 6 October) name a sibling script in their freeze list, so their freeze records hash that sibling and not the file that fired. The fired files were hashed and timestamped beside the freezes in calls/SIDE_FREEZE_20261005.txt (sha256 a0f2943bb6190d7b...); a three-reader check (freeze, file time, circuits rebuilt against the vendor's stored inputs) is in data_provenance_20261005.txt.

### Totals by vendor and day

| Vendor | Day | Jobs/tasks | Completed | Cancelled | Failed | Queued |
|---|---|---|---|---|---|---|
| IBM (Qiskit Runtime) | 2026-09-24 | 17 | 16 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-09-28 | 65 | 65 | 0 | 0 | 0 |
| IBM (Qiskit Runtime) | 2026-10-01 | 3 | 3 | 0 | 0 | 0 |
| IBM (Qiskit Runtime) | 2026-10-02 | 72 | 71 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-10-04 | 43 | 42 | 0 | 1 | 0 |
| IBM (Qiskit Runtime) | 2026-10-05 | 26 | 26 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-25 | 21 | 21 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-26 | 204 | 184 | 0 | 20 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-28 | 94 | 94 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-09-29 | 244 | 244 | 0 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-10-04 | 1162 | 1046 | 116 | 0 | 0 |
| Rigetti Cepheus-1-108Q (Braket) | 2026-10-05 | 1310 | 1310 | 0 | 0 | 0 |
| **IBM (Qiskit Runtime)** | **all days** | **226** | **223** | **0** | **3** | **0** |
| **Rigetti Cepheus-1-108Q (Braket)** | **all days** | **3035** | **2899** | **116** | **20** | **0** |
| **Both vendors** | **all days** | **3261** | **3122** | **116** | **23** | **0** |

### Families, in date order

**2026-09-24 ibm_fez, ibm_kingston, ibm_marrakesh -- raw_repull (raw results only)** (14 jobs: 14/0/0)

What was laid: Fourteen jobs whose results exist only as raw re-pulled files [parallax/out/raw_repull/]. Jobs named in the discard map and the Biblioteca: the first idle-pair run on ibm_marrakesh (1 job, estimator, one entangled-pair circuit and two controls per pair) [notebook, 2026-09-24 ~17:20Z; parallax/out/discards/DISCARD_MAP.md, H5]; the second version of that run on ibm_marrakesh (10 jobs; per pair one parameterized circuit with an RZ rotation on qubit b between the CX and the RY, 12 angles in shuffled order, 2048 shots, plus two control circuits at 4096 shots, t = 30 us) [notebook, 2026-09-24 ~20:05Z]; one three-box job on ibm_kingston (weak probe, 8192 shots) [parallax/out/discards/DISCARD_MAP.md, H7; notebook, 2026-09-24 ~22:20Z]; and one three-box job with the dark box in the |11> corner on ibm_marrakesh [notebook, 2026-09-24 ~21:30Z]. One ibm_fez job in this group is not named in the ledgers searched.

What was read: First idle-pair run (ibm_marrakesh): t = 0, D = +0.0012 +/- 0.0024 (8 pairs); t = 30 us, D = +0.0054 +/- 0.0050 [notebook, 2026-09-24 ~17:20Z]. Second version (10 jobs): chi2 of the phase term 19.4 on 20 dof; D with the entangled circuit first +0.0124 +/- 0.0046; D with it last -0.0013 +/- 0.0154; D averaged over both orders +0.0056 +/- 0.0081 [notebook, 2026-09-24 ~19:10Z]. Three-box job on ibm_kingston: A +0.798 +/- 0.056, B +0.843 +/- 0.050, C -0.587 +/- 0.057, corner 11 +0.174 +/- 0.063 [notebook, 2026-09-24 ~21:14Z]. Three-box job with the dark box in the |11> corner (ibm_marrakesh): corner 11 -0.506 +/- 0.057, A_00 +0.773, B_01 +0.763, unused 10 +0.169 +/- 0.061 [notebook, 2026-09-24 ~21:31Z]. No read on file attributable to the ibm_fez job.

**2026-09-24 ibm_kingston, ibm_marrakesh -- NOTHING_SWEEP_sep24_27.md** (2 jobs: 1/0/1)

What was laid: Two jobs. The completed one is the ibm_kingston run of the idle-30-us pair experiment (8 qubit pairs, t = 30 us, entangled-pair circuit, two product-state controls, same mitigation as the ibm_marrakesh run) [parallax/NOTHING_SWEEP_sep24_27.md, item a1; notebook, 2026-09-24 ~17:20Z]. The failed one is attempt 1 of the second version of that experiment on ibm_marrakesh, 30 pubs [parallax/out/discards/DISCARD_MAP.md, H6].

What was read: ibm_kingston, t = 30 us: D = +0.00832 +/- 0.00291, 6 of 8 pairs positive [notebook, 2026-09-24 ~18:05Z]. No read on file for the failed job.

**2026-09-24 ibm_kingston -- FREE_CHECKS_20260929.md** (1 job: 1/0/0)

What was laid: One job named in the free-checks note as the job that read qubit pairs 16-23 and 144-145 on ibm_kingston; it was submitted in the same second as a one-qubit job on the same chip [parallax/FREE_CHECKS_20260929.md, item 1].

What was read: No read on file.

**2026-09-25 Cepheus-1-108Q -- round1** (21 tasks: 21/0/0)

What was laid: Step 1 on q0: find the 1-2 transition drive amplitude. Each circuit is an X gate (0 to 1), an f12 pulse of amplitude a, an X gate (1 to 0), then measure; anything the f12 pulse moved into |2> reads as 1. 21 amplitudes from 0.0 to 0.8, 300 shots each [standoff/braket_round1.py].

What was read: Fitted f12 half-turn amplitude 0.494; measured peak 0.94 at amplitude 0.48; contrast 0.8789; offset 0.0692; rmse 0.0234; 300 shots per point [standoff/round1_fit.json].

**2026-09-26 Cepheus-1-108Q -- step2** (42 tasks: 42/0/0)

What was laid: Step 2 on q0 in three parts: A, prepare |0>, |1>, |2> and read each plainly and after an X gate (1000 shots); B, prepare |2>, wait 0 to 35 us, read both ways (300 shots, 10 delays); C, Ramsey on the 1-2 transition at 4 MHz virtual detuning (300 shots, 16 delays from 0 to 1.5 us) [standoff/braket_round1_step2.py].

What was read: Part A, P(read 1) for prepared 0 / 1 / 2: plain 0.035 / 0.947 / 0.893; after the X gate 0.932 / 0.048 / 0.951. Part B, read after the X gate: 0.94 at 0 us and 0.5233 at 35 us [standoff/step2_results.json].

**2026-09-26 Cepheus-1-108Q -- two_clocks** (2 tasks: 2/0/0)

What was laid: Two tasks whose IDs were first found in the job-list file parallax/out/two_clocks/braket_tasks.json. One is the orphaned first try of the step 2b Ramsey (part C, delay 0, 300 shots; created between step 2 and step 2b and collected on 29 Sep) [standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json]. The other is the random-seed task: rx quarter turn on 80 qubits, 10,000 shots [standoff/dice_refill.py].

What was read: Orphan task: 280 of 300 shots read 1 [standoff/orphan_step2b_4f3a04f7-2eb6-44a4-a063-6c3acbef2454.json]. Seed task: 800000 raw bits, fraction of ones 0.5177 [standoff/pup_seeds.provenance.json].

**2026-09-26 Cepheus-1-108Q -- step2b** (21 tasks: 21/0/0)

What was laid: The Ramsey part of step 2 again at finer delays on a 4 ns grid, 500 shots per delay, q0 [standoff/braket_round1_step2.py; notebook, 2026-09-25 late].

What was read: P(read 1) at delays 0.0 / 0.05 / 0.1 / 0.15 / 0.2 us: 0.926 / 0.738 / 0.194 / 0.122 / 0.512 [standoff/step2b_results.json]. Recorded fit: 1-2 transition offset -0.16 MHz from the vendor frame, T2* about 6.6 us [notebook, 2026-09-25 late].

**2026-09-26 Cepheus-1-108Q -- step3** (35 tasks: 35/0/0)

What was laid: Native three-level three-box circuit on q0: prepare (|0> + i|1> + |2>)/sqrt3, post-select the same state with the |2> sign flipped; one box is opened by a strong measurement, giving branches 'found' and 'not found'; native rx, rz and f12 pulses only; the analysis was written in the script before the data [standoff/braket_round1_step3.py].

What was read: Fringe phase setting x0 = -3.0560. P at the post-selection setting: prepared state 0.0855; A not found 0.0136; B not found -0.0194; C not found 0.6052. Weak-value numbers from the recorded rule: A 0.9224, B 1.1447, C 0.2049 [standoff/step3_abl.json].

**2026-09-26 Cepheus-1-108Q -- grid16q** (16 tasks: 16/0/0)

What was laid: A 16-arm factorial on q0's three levels with four switches: S (the preparation applied twice), R (an X swap between preparation and read), B (post-select the second state instead of undoing the preparation), P (two f12 pulses that return populations unchanged); 3000 shots per arm; the ideal-model values were computed in the script before the data [standoff/grid16q.py].

What was read: Four-way term SRBP measured -0.0179 (+/- 0.0022 in the Biblioteca entry), ideal-model value -0.0188; arm (0,0,0,0) 0.9258 [standoff/grid16q_analysis.json; notebook, 2026-09-26 ~01:35Z].

**2026-09-26 Cepheus-1-108Q -- round2** (18 tasks: 18/0/0)

What was laid: Weak values of the three boxes with a pointer: q0 as the three-level system, q1 as the pointer started at 45 degrees, one native CZ, the box held in |1> chosen by shelving; 9 calibration tasks (q0 parked in 0 / 1 / 2, pointer read in X, Y, Z; 1000 shots) and 9 run tasks (3 shelving configurations x 3 bases; 3000 shots) [standoff/round2_hw.py; standoff/round2_weak.py].

What was read: Fitted W_A +1.015 +/- 0.076, W_B +0.831 +/- 0.073, W_C -0.838 +/- 0.092; CZ phase per level 0 / 1 / 2: -0.03 / 3.02 / 2.47 rad [notebook, 2026-09-26 ~04:00Z; standoff/round2_analysis.json].

**2026-09-26 Cepheus-1-108Q -- ring_rabi_q90** (9 tasks: 9/0/0)

What was laid: A 9-point f12 Rabi scan on q90, amplitudes 0.0 to 0.32 in steps of 0.04, 300 shots each [standoff/ring_rabi_q90_fit.json].

What was read: f12 half-turn amplitude 0.1645; contrast 0.9568; offset 0.0171; rmse 0.0189 [standoff/ring_rabi_q90_fit.json].

**2026-09-26 Cepheus-1-108Q -- ring** (26 tasks: 6/0/20)

What was laid: Two-witness five-context ring on q0 and q90 (qutrit readout): 5 contexts x 2 readout schemes x waits of 0 and 5 us, plus 6 in-job readout-calibration circuits, 26 tasks of 1900 shots; task order from random bytes of pup_seeds.bin [standoff/ring_two_witness.py; notebook, 2026-09-26 'THE RING -- PRE-REGISTRATION'].

What was read: 20 context tasks failed; 6 tasks completed. In-job readout rows, P(read 1) for prepared 0 / 1 / 2: q0 plain [.046, .931, .926], after X gate [.926, .055, .956]; q90 plain [.007, .933, .943], after X gate [.910, .006, .964] [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'; standoff/ring_analysis.json].

**2026-09-26 Cepheus-1-108Q -- plus_none** (14 tasks: 14/0/0)

What was laid: Five-step gate chain on q99, then a sixth slot in three variants at the same elapsed time D (2 us and 6 us): (a) an empty delay after the chain, (b) the same delay between steps 1 and 2, (c) X gate, delay, X gate; plus a reference with no D; two analysis settings (S1, S2); 1300 shots per task; task order from random bytes of pup_seeds.bin [standoff/plus_none.py].

What was read: P(1) difference a minus b: -0.005 +/- 0.015 (2 us, S1), +0.020 +/- 0.018 (2 us, S2), -0.025 +/- 0.019 (6 us, S1), -0.035 +/- 0.015 (6 us, S2). Variant c against variant a at S2: 0.22 against 0.74 (2 us), 0.14 against 0.80 (6 us) [notebook, 2026-09-26, 'THE PLUS NONE -- RESULT'; standoff/plus_none_analysis.json].

**2026-09-26 Cepheus-1-108Q -- ring_diag** (1 task: 1/0/0)

What was laid: One acceptance task of 100 shots: ring context 1, 5 us wait, readout scheme b, on q0 and q90, after the 01 rotations were rebuilt from native rx, rz, rx [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'; standoff/ring_diag_results.json].

What was read: P(read 1): q0 0.52, q90 0.62 [notebook, 2026-09-26 'THE RING -- RESULT: NOT RUN'].

**2026-09-26 Cepheus-1-108Q -- ring_rerun** (20 tasks: 20/0/0)

What was laid: The 20 ring context tasks again, with the 01 rotations built from native rx, rz, rx 1900 shots each; task order from pup_seeds.bin bytes 49856-49919 [notebook, 2026-09-26 ~16:55Z; standoff/ring_two_witness.py].

What was read: Ring sum S_corr (S_raw): q0, 0 us 2.204 +/- 0.024 (2.284 +/- 0.018); q0, 5 us 2.088 +/- 0.024 (2.183); q90, 0 us 2.114 +/- 0.021 (2.301 +/- 0.018); q90, 5 us 2.067 +/- 0.020. Cross-witness per-task correlation z between -1.7 and +2.6 [notebook, 2026-09-26 ~16:55Z; standoff/ring_analysis.json].

**2026-09-28 ibm_marrakesh -- 20260928_083041** (4 jobs: 4/0/0)

What was laid: The IBM half of the parallax run on ibm_marrakesh, 78 qubits (every even qubit), raw I/Q readout. J1 default shot spacing, 4000 shots (measure; X then measure; measure twice; X then measure twice); J2 spacing 20 us, 2000 shots; J3 spacing 1 ms, 2000 shots; J4 default spacing again, 2000 shots [parallax/parallax_ibm.py].

What was read: Medians over 78 qubits: prepared 0, one look, read 1 on 0.52% of shots; second look after a first look read 0, 0.08%; read 1 on both looks 0.39%; shots 20 us apart 1.15% against 0.40% for shots 1 ms apart; q26 off both clouds on 1.7% of prepared-1 shots [notebook, 2026-09-28 ~12:40Z].

**2026-09-28 ibm_marrakesh -- echo_20260928_122733** (14 jobs: 14/0/0)

What was laid: The echo run on ibm_marrakesh: each shot is a look, then an X gate (E1) or none (E0), then a look; 78 even qubits, 1500 shots, gap between shots 20, 50, 100, 250, 500, 1000 and 2000 us (14 jobs = 2 circuits x 7 gaps) [parallax/parallax_echo.py].

What was read: Median qubit, (after a 1 minus after a 0) first-look reading: 0.07% at a 20 us gap, 0.00% by 50 us. First look reads 1 on 0.70% of shots at 20 us, 0.47% at 50 us, 0.30% by 500 us; after a 0 ending 0.70% and after a 1 ending 0.77%. After the X gate the second look reads 0 on about 1.7% at every gap [notebook, 2026-09-28 ~17:00Z]. Chip-wide (74 readable qubits): 0.84% at a 20 us gap above a 0.31% floor [§17].

In the paper: Partly reported in Section 3.5 (the chip-wide drain numbers of §17); the other reads are given here.

**2026-09-28 ibm_kingston -- 20260928_123452** (4 jobs: 4/0/0)

What was laid: The same parallax run on ibm_kingston [parallax/parallax_ibm.py].

What was read: One look 0.39%, both looks 0.25%; 1 qubit (q146) with no readable separation; crowding 20 us against 1 ms 1.2x [notebook, 2026-09-28 ~17:25Z].

**2026-09-28 ibm_kingston -- darkwave_20260928_124527** (1 job: 1/0/0)

What was laid: Round 1 of the eraser circuit on ibm_kingston (qubits 47, 48, 64 as S, I, C), wait 5 us. Three qubits S (record), I (partner), C (coin), 8 phases, 4000 shots per phase: H on S, CX from S to I, phase on S, H on S, measure S (the record); then a wait; then C is flipped to a quantum coin and measured, and if C = 1 an H is applied to I before I is measured [parallax/darkwave_eraser.py].

What was read: Record alone V 0.026 +/- 0.016; sorted by the later coin: erased V 0.65 / 0.62 (+/- 0.03, for partner 0 / 1), path kept V 0.03 / 0.02 [notebook, 2026-09-28 ~17:55Z].

**2026-09-28 ibm_fez -- witness_crowd** (6 jobs: 6/0/0)

What was laid: The label is an analysis folder, not a run script: parallax/out/witness_crowd/ re-reads 25 finished ibm_fez jobs of 28 Sep from raw_repull and holds the readings of the 6 jobs counted here [parallax/out/witness_crowd/WITNESS_CROWD.md].

Reported in Section 3.4.

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125452** (3 jobs: 3/0/0)

What was laid: Round 2 on ibm_marrakesh, variants early (coin and partner read before the record), late5 and late50 (record, wait 5 or 50 us, coin) [parallax/PREREG_DARKWAVE.md, Round 2; parallax/darkwave_eraser.py].

What was read: Erased V early 0.96, late5 0.87, late50 0.54 [parallax/PREREG_DARKWAVE.md, Round 2 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_125452** (1 job: 1/0/0)

What was laid: Round 2 on ibm_fez, variant early (coin and partner read before the record), S, I, C = 143, 144, 70 [parallax/PREREG_DARKWAVE.md, Round 2; parallax/darkwave_eraser.py].

What was read: Erased V early 0.94; the same round records late5 0.27 and late50 0.09 for ibm_fez [parallax/PREREG_DARKWAVE.md, Round 2 result].

**2026-09-28 ibm_fez -- 20260928_125537** (4 jobs: 4/0/0)

What was laid: The same parallax run on ibm_fez [parallax/parallax_ibm.py].

What was read: One look 0.29%, both looks 0.21% [notebook, 2026-09-28 ~18:30Z].

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125804** (1 job: 1/0/0)

What was laid: Round 3 on ibm_marrakesh, variant late0 (record, zero wait, then the coin) [parallax/PREREG_DARKWAVE.md, Round 3; parallax/darkwave_eraser.py].

What was read: late0 erased V 0.98 / 0.95 [parallax/PREREG_DARKWAVE.md, Round 3 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_125951** (1 job: 1/0/0)

What was laid: Round 4 on ibm_fez, variant late50e (50 us wait with X, 25 us, X, 25 us on the partner) [parallax/PREREG_DARKWAVE.md, Round 4; parallax/darkwave_eraser.py].

What was read: late50e erased V 0.27 / 0.27 [parallax/PREREG_DARKWAVE.md, Round 4 result].

**2026-09-28 ibm_marrakesh -- darkwave_ibm_marrakesh_20260928_125951** (1 job: 1/0/0)

What was laid: Round 4 on ibm_marrakesh, variant late50e (50 us wait with X, 25 us, X, 25 us on the partner) [parallax/PREREG_DARKWAVE.md, Round 4; parallax/darkwave_eraser.py].

What was read: late50e erased V 0.59 / 0.59 [parallax/PREREG_DARKWAVE.md, Round 4 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_130429** (5 jobs: 5/0/0)

What was laid: Round 5 on ibm_fez (S, I, C = 143, 144, 70), variants late0, late2, late5, late10, late20 (record, wait of that many us, coin) [parallax/PREREG_DARKWAVE.md, Round 5; parallax/darkwave_eraser.py].

What was read: Erased V at 0 / 2 / 5 / 10 / 20 us: 0.93 / 0.74 / 0.08 / 0.78 / 0.60 [parallax/PREREG_DARKWAVE.md, Round 5 result].

**2026-09-28 ibm_fez -- partner_ibm_fez_130509** (1 job: 1/0/0)

What was laid: Free-evolution coherence of the partner qubit on ibm_fez (S = 143, I = 144): series 'alone' (S left in |0>) and 'after' (S put in |+> and measured first), partner H, wait 0 to 50 us (10 delays), read in X or Y, 2000 shots [parallax/partner_memory.py].

What was read: Coherence alone / after: 0.97 / 0.98 at 5 us, 0.95 / 0.93 at 12 us, 0.77 / 0.77 at 50 us [parallax/PREREG_DARKWAVE.md, Round 5 result].

**2026-09-28 ibm_fez -- beat_ibm_fez_130853** (1 job: 1/0/0)

What was laid: Round 6 on ibm_fez: one job, waits 0 to 24 us (15 values), 4 phases, 2000 shots, eraser variant late<w> [parallax/darkwave_beat.py].

What was read: Erased V at 0 / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 / 10 / 12 / 14 / 16 / 20 / 24 us: 0.96, 0.87, 0.76, 0.52, 0.37, 0.07, 0.22, 0.39, 0.58, 0.77, 0.75, 0.54, 0.13, 0.59, 0.56 [parallax/PREREG_DARKWAVE.md, Round 6 result].

**2026-09-28 ibm_fez -- split_ibm_fez_131030** (1 job: 1/0/0)

What was laid: Round 7 on ibm_fez, waits 0, 3, 5, 8, 10 us: (a) the record taken, a wait, then H on the partner always and read (no coin), 4 phases x 2000 shots; (b) entangled-memory arm, H on S, CX, read S, wait, read the partner in X or Y, split by S's outcome [parallax/darkwave_split.py].

What was read: (a) V at 0 / 3 / 5 / 8 / 10 us: 0.97 / 0.57 / 0.11 / 0.57 / 0.78. (b) coherence, S = 0 branch: 0.95 / 0.60 / 0.12 / 0.58 / 0.81 [parallax/PREREG_DARKWAVE.md, Round 7 result].

**2026-09-28 ibm_fez -- culprit_131215** (1 job: 1/0/0)

What was laid: Round 8 on ibm_fez, waits 0, 3, 5, 8, 10 us, 2000 shots: partner 144 started in |+>; arms with CZ(143,144) applied twice, CZ(145,144) applied twice, or no CZ; read 144 in X or Y [parallax/darkwave_culprit.py].

What was read: Coherence at 5 us: no gate 0.98; CZ(143) twice 0.95; CZ(145) twice 0.95 [parallax/PREREG_DARKWAVE.md, Round 8 result].

**2026-09-28 ibm_fez -- ring_131350** (1 job: 1/0/0)

What was laid: Round 9 on ibm_fez, waits 0, 3, 5, 8, 10 us, 2000 shots: H, CX, then either the twin S measured first and the partner waits (arm b), or both wait and S is measured afterwards (arm f); partner read in X or Y, split by S's outcome [parallax/darkwave_ring.py].

What was read: Partner coherence, S = 0 branch, at 0 / 3 / 5 / 8 / 10 us: S measured first 0.96 / 0.66 / 0.35 / 0.62 / 0.81; S measured after the wait 0.96 / 0.68 / 0.37 / 0.61 / 0.80 [parallax/PREREG_DARKWAVE.md, Round 9 result].

**2026-09-28 ibm_fez -- barrier_132014** (1 job: 1/0/0)

What was laid: Round 11 on ibm_fez, one job, waits 0, 3, 5, 8, 10 us, 2000 shots: arm b (twin measured first, no barrier), arm B (the same with a barrier after the twin's measurement), arm f (twin measured after the wait); partner read in X or Y per S outcome [parallax/darkwave_barrier.py].

What was read: Partner coherence S = 0 / S = 1 at 0 / 3 / 5 / 8 / 10 us. b: 0.97/0.96, 0.58/0.55, 0.09/0.12, 0.58/0.55, 0.80/0.78. B: 0.96/0.95, 0.95/0.95, 0.95/0.93, 0.90/0.90, 0.91/0.87. f: 0.97/0.97, 0.59/0.60, 0.12/0.13, 0.57/0.53, 0.80/0.79 [parallax/PREREG_DARKWAVE.md, Round 11 result].

**2026-09-28 ibm_fez -- alone_132136** (1 job: 1/0/0)

What was laid: Round 12 on ibm_fez: plain Ramsey on each of qubits 143 and 144 alone (the other left in |0>, barrier-pinned), waits 0, 2, 3, 5, 8, 11, 14 us, 2000 shots, read in X or Y [parallax/darkwave_alone.py].

What was read: Coherence alone at 0 / 2 / 3 / 5 / 8 / 11 / 14 us: q143 0.99, 0.77, 0.68, 0.29, 0.61, 0.89, 0.60; q144 1.00, 0.98, 0.95, 0.96, 0.93, 0.90, 0.88 [parallax/PREREG_DARKWAVE.md, Round 12 result].

**2026-09-28 ibm_fez -- darkwave_ibm_fez_20260928_132156** (3 jobs: 3/0/0)

What was laid: Round 13 on ibm_fez (S, I, C = 143, 144, 70), 8 phases, 4000 shots, one job per variant: late5 (no barrier), late5B and late50B (a barrier after the record) [parallax/PREREG_DARKWAVE.md, Round 13; parallax/darkwave_eraser.py].

What was read: late5: S alone 0.015, erased 0.130 / 0.137, path kept 0.027 / 0.016. late5B: S alone 0.026, erased 0.887 / 0.901, path kept 0.216 / 0.291. late50B: S alone 0.014, erased 0.317 / 0.330, path kept 0.102 / 0.261 [parallax/PREREG_DARKWAVE.md, Round 13 result].

**2026-09-28 ibm_fez -- listen_ibm_fez_142649** (1 job: 1/0/0)

What was laid: No question written first. Every even qubit of ibm_fez (78), plain Ramsey all at once, 12 waits from 0 to 20 us, read in X and Y, 2000 shots [parallax/listen.py].

What was read: q138 recorded as a second two-tone qubit, beat about 7-8 us [notebook, 2026-09-28 ~13:25 EDT block, entries after 'THE LISTEN']. No other headline number is recorded in the ledgers searched.

**2026-09-28 ibm_fez -- split2_143826** (1 job: 1/0/0)

What was laid: Round 14 on ibm_fez: qubits 143 and 138 alone, Ramsey 0 to 22 us every 1 us, read in X or Y, 1000 shots, a two-tone fit; plus 4000-shot circuits (143 at 5.5 us, 138 at 3.75 us) for shot-to-shot correlation [parallax/darkwave_split2.py].

What was read: q143: second tone on 0.26 of shots, notes 90 kHz apart; q138: 0.17, 139 kHz apart. Consecutive shots agree 0.75 on q143 (0.67 sixteen shots later) and 0.30 on q138 [parallax/PREREG_DARKWAVE.md, Round 14 result].

**2026-09-28 ibm_fez -- oddraw_ibm_fez_144417** (1 job: 1/0/0)

What was laid: Every odd qubit of ibm_fez (78), plain Ramsey all at once, 12 waits from 0 to 20 us, X and Y, 2000 shots, raw I/Q dots kept, two reference circuits (all 0, all 1); job datbagtvr3kc73el7m2g [parallax/listen_raw.py; parallax/out/oddraw_ibm_fez_144417/meta.json].

What was read: No read on file (the folder holds per-qubit tables and images; no headline number is recorded in the ledgers searched).

**2026-09-28 ibm_fez -- the_do_144952** (1 job: 1/0/0)

What was laid: Qubits 113, 72 and 27 on ibm_fez; two looks per shot; barriers pin the order; every circuit has the same number of looks; waits 0, 2, 5, 10, 20 us; 4000 shots; each cut checked on half the references first [parallax/the_do.py].

What was read: Seat 72: 'told-1 lands far only 24%, main->far on 2nd look 6.5%; told-0 far 2.6%'. Seat 113: the second look repeats the first look's landing spot, correlation 0.55 against 0.02 on seat 27. Cut check misfile 22-34% on seats 113 and 72 [notebook, 2026-09-28 14:50 entry].

**2026-09-28 ibm_fez -- ripples_153734** (1 job: 1/0/0)

What was laid: A straight chain of 7 ibm_fez qubits (104 to 110), all in superposition; the middle qubit (107) is looked at either before or after the other six are read; waits 0 and 5 us; 4000 shots; raw dots [parallax/ripples.py].

What was read: q108 tilts 7-10 deg with the answer of the looked-at qubit q107, the same whether q107 is looked at before or after [notebook, 2026-09-28 15:4x entry; job datc3qbojkfs738qfk30].

**2026-09-28 ibm_fez -- yeast_153906** (1 job: 1/0/0)

What was laid: One job of the budding run on ibm_fez, stone q108: the pond is every qubit within 3 hops, read first; the stone is read last; waits 5000 ns, 4000 shots; the next stone is the pond qubit that tilts most with the stone's answer in its own noise units [parallax/yeast.py].

What was read: Generation 1, stone 108: stone cut check 0.01, 10 pond qubits [parallax/out/yeast_153906/yeast.json]. No other read on file for this job.

**2026-09-28 ibm_fez -- yeast_153959** (4 jobs: 4/0/0)

What was laid: The same budding run started from stone q143, four generations (stones 143, 144, 145, 146), brake 15 s [parallax/yeast.py].

What was read: Stone cut check by generation 0.0065 / 0.009 / 0.0155 / 0.007 [parallax/out/yeast_153959/yeast.json]. Recorded tilts along the chain: 143 to 144 12 deg, 144 to 145 24.5 deg, 145 to 146 12.4 deg [notebook, 2026-09-28 15:5x entry].

**2026-09-28 Cepheus-1-108Q -- heatlens** (6 tasks: 6/0/0)

What was laid: Two-point heat measurement on q0: arm A f12 pulse at amplitude 0 and at the f12 half-turn amplitude, X, read (10,000 shots); arm B X, f12 pulse, X, read (500 shots); arm D one look of prepared 0 and prepared 1 (1000 shots); 6 tasks [standoff/braket_heat_vs_lens.py].

What was read: A swing 0.0243, B swing 0.447, heat Pe = 0.0515 +/- 0.0035; one look prepared 0 read 1: 0.046; prepared 1 read 0: 0.095; a+b-1 at rest -0.049 +/- 0.0114 [standoff/heatlens_analysis.json; notebook, 2026-09-28 ~17:45Z].

**2026-09-28 Cepheus-1-108Q -- gamble** (21 tasks: 21/0/0)

What was laid: Whole-qubit gamble on q0 with partner q1: shuffle of the at-rest state across levels 0, 1, 2 (8 gate sequences, 5000 shots), blink-and-train arms (swap 1-2 then flip 0-1, now and after a 60 us wait, 3 batches minutes apart, 3000 shots), and an entangled-versus-product pair read plainly and after the swap (6000 shots); 21 tasks [standoff/rigetti_gamble.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- tune** (8 tasks: 8/0/0)

What was laid: Whole-chip f12 tune: every qubit in parallel, X, f12 push of amplitude a (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75), X, read; 8 tasks of 1000 shots [standoff/rigetti_chip.py].

Reported in Sections 3.5 and 3.6.

**2026-09-28 Cepheus-1-108Q -- fine** (8 tasks: 8/0/0)

What was laid: Whole-chip f12 fine tune: the same circuit at amplitudes 0.04, 0.08, 0.12, 0.16, 0.24, 0.28, 0.32, 0.36; 8 tasks of 1000 shots; fitted jointly with the tune tasks [standoff/rigetti_chip.py].

Reported in Sections 3.5 and 3.6.

**2026-09-28 Cepheus-1-108Q -- run** (17 tasks: 17/0/0)

What was laid: Whole-chip shuffle: the at-rest state shuffled across levels 0, 1, 2 with 8 gate sequences on every qubit (5000 shots), then drain arms (swap-then-flip now, after 60 us, plain) in 3 batches minutes apart (2000 shots); 17 tasks [standoff/rigetti_chip.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- blink** (16 tasks: 16/0/0)

What was laid: The blink hour: whole chip, 8 checks about 7.5 minutes apart (23:34 to 00:27 UTC), each check a plain read, a swap-then-flip read and a 1-2 Ramsey at 1.5 us in two quadratures, 800 shots; the 32 tasks cross 00:00 UTC and are indexed as 16 + 16 [standoff/blink_hour.py].

Reported in Section 3.5.

**2026-09-28 Cepheus-1-108Q -- witness** (18 tasks: 18/0/0)

What was laid: Emitter q0 parked in 0 or 1 or pushed to level 2 and left to fall; clocks q9 and q1 (neighbours) and q10 (two links away) held in superposition through waits of 4, 8, 16 us; emitter read after a flip, each clock read in X or Y; 2000 shots; 18 tasks [standoff/witness.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- blink** (16 tasks: 16/0/0)

What was laid: The second half of the blink hour (checks continuing past 00:00 UTC; see the 28 Sep entry), 16 tasks of 800 shots [standoff/blink_hour.py].

Reported in Section 3.5.

**2026-09-29 Cepheus-1-108Q -- wchip** (24 tasks: 24/0/0)

What was laid: Whole-chip witness: emitter q0 at rest or pushed to level 2, every other qubit a clock, waits 0.5, 1, 2, 3, 4, 6 us, 2000 shots; 24 tasks [standoff/witness_chip.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- wobs** (24 tasks: 24/0/0)

What was laid: Who is watching: the same event with different sets of clocks (all clocks on, far clocks only, far clocks plus neighbours q1 and q9), arms rest, push with q0 at rest, and q0 pushed to level 2; waits 2 and 4 us; 2000 shots; 24 tasks [standoff/witness_obs.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- whead** (24 tasks: 24/0/0)

What was laid: One clock (q9) with every other qubit parked quiet; emitter q0 at rest or pushed to level 2; waits 0.5, 1, 2, 3, 4.5, 6 us; 1000 shots (rest) and 2500 shots (pushed); 24 tasks [standoff/witness_headline.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- wroom** (48 tasks: 48/0/0)

What was laid: The headline shot (q9 witness, emitter q0) with the room filled with other clocks: half (every other qubit) or full (every qubit); same waits; 1000 and 2500 shots; 48 tasks [standoff/witness_room.py].

Reported in Section 3.4.

**2026-09-29 Cepheus-1-108Q -- walt** (24 tasks: 24/0/0)

What was laid: Alternating rooms: q9 alone and the full room alternate task by task, two rounds, waits 0.5, 1, 2, 3, 4.5, 6 us, 2500 shots, emitter q0 pushed to level 2 each time; 24 tasks [standoff/witness_alt.py].

What was read: Emitter fall time, alone 26.6 us (26.0-27.6), full 31.2 us (30.0-32.4); at the first wait the full room reads 7.5% fell against 6.6% [§12].

**2026-09-29 Cepheus-1-108Q -- stack** (54 tasks: 54/0/0)

What was laid: Two shots with all outcomes kept: START, q0's heat at the start measured by the readout-proof swap trick plus a plain read, in rooms ALONE, HALF (54 clocks), FULL (106 clocks), rotated A,H,F then F,H,A; THREE, q0 at rest or at level 2, q9 the clock, q10 parked in 0 or 1, waits 1, 2, 4 us; 54 tasks [standoff/fuckup_stack.py].

What was read: START: ALONE 3.85% +/- 0.36, HALF 3.81 +/- 0.36, FULL 4.96 +/- 0.38; plain read 4.55 / 4.95 / 6.10%. THREE: q0's pull on q9 -60.9 deg/us (q10 at 0) and -62.2 (q10 at 1) [§13].

**2026-09-29 Cepheus-1-108Q -- edge** (30 tasks: 30/0/0)

What was laid: q0's heat at the start (swap trick plus plain read) with three rooms watching: ALONE, EDGE (q35, q62, q80), MIDDLE (q39, q58, q75); clocks lit at t = 0, 3 us wait; rotated ALONE, EDGE, MIDDLE then MIDDLE, EDGE, ALONE; 30 tasks [standoff/edge_room.py].

What was read: ALONE 3.83% +/- 0.36, EDGE 3.58 +/- 0.35, MIDDLE 2.23 +/- 0.35; MIDDLE 2.29 and 2.17 against ALONE 4.21 and 3.42 in the two rounds [§14].

**2026-10-01 ibm_kingston, ibm_phoenix, ibm_pittsburgh -- qubit_three_runs** (3 jobs: 3/0/0)

What was laid: Run 1 of the three-run qubit experiment on three chips (ibm_kingston, ibm_phoenix, ibm_pittsburgh): one look after a wait; 3 starts (|0>, halfway, |1>) x 3 waits, raw I/Q on every look; qubit groups of three (ibm_kingston: [[82,139,154],[38,92,96],[25,109,135]]) [§96, §97, §100; parallax/QUBIT_THREE_RUNS_APPROVED_20261001.md].

What was read: ibm_kingston: fading time 255.4 +/- 7.6 us; |1> start after 240 / 300 us 0.497 / 0.398; halfway start after 60 / 240 / 300 us 0.509 / 0.232 / 0.196. ibm_phoenix: fading time 177.1 +/- 5.7 us [§101]. ibm_pittsburgh (opened later): fading time, no earlier look, 269 us [§113].

**2026-10-02 ibm_kingston, ibm_phoenix, ibm_pittsburgh -- qubit_three_runs** (6 jobs: 6/0/0)

What was laid: Runs 2 and 3 of the same experiment on the same three chips: run 2 = start, look, wait, look; run 3 = start, look, wait, look, wait, look, with the two waits in mirrored order (short then long, long then short) [§96, §102, §107].

What was read: Run 2, ibm_kingston, look 2 after 60 / 240 / 300 us, |1> start 0.742 / 0.373 / 0.298, halfway 0.366 / 0.179 / 0.147; fading time from levels 261.6 +/- 7.8 us; from the look-to-look gap 157.2 +/- 17 us. ibm_phoenix: |1> start 0.643 / 0.245 / 0.158; fading time 178.2 +/- 6.4 us; from the gap 121.6 +/- 8.5 us [§105]. Run 3, fading time by 0 / 1 / 2 earlier looks: ibm_kingston 248.7 +/- 7.4 / 265.2 +/- 8.6 / 328.2 +/- 28; ibm_phoenix 182.5 +/- 5.4 / 179.5 +/- 6.2 / 184.2 +/- 16; refit on one window: ibm_kingston 253 +/- 10 / 270 +/- 9 / 274 +/- 15, ibm_phoenix 182 +/- 6 / 180 +/- 7 / 177 +/- 9, ibm_pittsburgh 277 +/- 10 / 288 +/- 11 / 286 +/- 15 [§108, §136]. Level at the long wait, |1> start, 0 / 1 / 2 earlier looks: ibm_kingston 0.302 / 0.302 / 0.261; ibm_phoenix 0.197 / 0.160 / 0.163; ibm_pittsburgh 0.314 / 0.347 / 0.319 [§108, §113]. ibm_pittsburgh run 2, look-to-look gap clock 234 us, level clock 283 us [§113].

**2026-10-02 ibm_boston -- qubit_stone_run** (3 jobs: 3/0/0)

What was laid: The three-run experiment on ibm_boston with waits 105 / 260 / 365 us (short + medium = long), 3 starts, 555 shots, blind qubit draw (seed 20261002), one job per run [parallax/QUBIT_STONE_RUN_BUILD_20261002.md; §111, §112].

What was read: ibm_boston: look-to-look gap clock 245 us, level clock 308 us (run 2); fading time with no earlier look 282 us; level clock by 0 / 1 / 2 earlier looks 278 / 310 / 314 us (widths 7-12, last 23-28); level at the long wait, |1> start, 0 / 1 / 2 earlier looks 0.273 / 0.279 / 0.262; qubit-to-qubit lopsidedness of the |0> start at look 1: 0.39 / 0.38, after waits (run 1) 0.74 / 0.78 / 1.12; remainder rms 0.076; third-look twin difference |0> -0.002, halfway -0.006, |1> +0.013 [§113].

**2026-10-02 ibm_marrakesh -- run5.py** (1 job: 1/0/0)

What was laid: One job on ibm_marrakesh, nine qubits drawn by a written seed, nothing written down before the run. Each circuit: start, look, wait, look; 3 starts (|0>, halfway, |1>) x 4 waits (none, 60, 240, 300 us) x 3 copies of the whole set = 36 circuits of 212 shots [parallax/out/qubit_fifth_run/run5.py; §114].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_pittsburgh -- run6.py** (1 job: 0/0/1)

What was laid: The no-wait arm (start, look, look) on ibm_pittsburgh, the same nine qubits, 3 starts x 3 copies = 9 circuits of 60 shots, fired under a 3 s cap [parallax/out/qubit_fifth_run/run6.py; §115].

What was read: No read on file (job status ERROR).

**2026-10-02 ibm_pittsburgh -- run9.py** (1 job: 1/0/0)

What was laid: The whole run-5 circuit set on ibm_pittsburgh (36 circuits of 212 shots), the same nine qubits [parallax/out/qubit_fifth_run/run9.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_kingston -- run7.py** (1 job: 1/0/0)

What was laid: The no-wait arm on ibm_kingston, the nine qubits of its run-1 freeze, 3 starts x 3 copies = 9 circuits of 212 shots [parallax/out/qubit_fifth_run/run7.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_kingston, ibm_pittsburgh -- run10.py** (2 jobs: 2/0/0)

What was laid: Copies of run 2's short-wait circuits (start, look, wait 60 us, look for |0>, halfway, |1>), three copies, 195 shots each (585 per start); ibm_pittsburgh and ibm_kingston, each on its own nine qubits [parallax/out/qubit_fifth_run/run10.py; §117].

What was read: Pittsburgh, |1> start, look-2 reading after the short wait, middle qubit of the nine: 0.797 (previous night), 0.728 (09:13), 0.797 (09:18); rms change over the nine qubits 0.157 (night to morning) and 0.164 (09:13 to 09:18). Kingston middle qubit 0.738 then 0.745, rms 0.141. Halfway start follows at about half size (rms 0.07-0.09); |0> start rms 0.01-0.02 [§117; parallax/out/qubit_fifth_run/data/reads/short_wait_across_time.txt].

Note: Table 1 of the paper lists this run; the paper reports no read from it.

**2026-10-02 ibm_pittsburgh -- jump.py** (8 jobs: 8/0/0)

What was laid: ibm_pittsburgh, every qubit: one job of 10 circuits x 400 shots fired 8 times, 4 minutes apart (start, look, wait none / 60 / 240 / 300 us, look, for |1> and halfway; |0> at none and 300 us) [parallax/out/qubit_fifth_run/jump.py; §118].

Reported in Section 3.1.

**2026-10-02 ibm_pittsburgh -- tail.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads 4 minutes apart, 11 circuits x 400 shots: start, look, wait, look at waits none / 6.7 / 20 / 60 / 300 us for |1> and halfway, |0> at none [parallax/out/qubit_fifth_run/tail.py].

Reported in Sections 3.1 and 3.2.

**2026-10-02 ibm_pittsburgh -- lone.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 11 circuits x 400 shots: start, wait, one look, at the waits of the tail run, with no first look [parallax/out/qubit_fifth_run/lone.py].

Reported in Section 3.1.

**2026-10-02 ibm_pittsburgh -- half.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads, 14 circuits x 360 shots: start, wait, one look, with the in-between state made by one half-push, or by a full push then a half-push, ON by one full push or by two half-pushes, at waits none / 6.7 / 20 us, and |0> by nothing or by two full pushes [parallax/out/qubit_fifth_run/half.py; §125].

What was read: Maker's stated look length read at 11:02: 2.180 us on all 156 qubits. Middle qubit, three reads, what one look keeps after 6.7 us / 20 us: in-between by one half-push 0.953 0.943 0.950 / 0.890 0.881 0.894; by full push then half-push 0.996 0.985 0.967 / 0.923 0.929 0.923; |1> by one full push 0.970 0.967 0.966 / 0.919 0.919 0.918; |1> by two half-pushes 0.968 0.969 0.971 / 0.919 0.918 0.918. Two-half-push |1> minus one-push |1>: +0.0006 +/- 0.0020 / +0.0006 +/- 0.0006. Far-side in-between minus |1>: +0.025 +/- 0.006 / +0.020 +/- 0.004; one-half-push in-between minus |1>: -0.016 +/- 0.003 / -0.027 +/- 0.002 [§125; parallax/out/qubit_fifth_run/data/reads/half_push.txt].

**2026-10-02 ibm_pittsburgh -- sides.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 19 circuits x 360 shots: one half-push with the frame turned 0 / 120 / 240 / 180 degrees, a full push then a half-push, |1>, each at none / 6.7 / 20 us, and |0> [parallax/out/qubit_fifth_run/sides.py; §128].

What was read: Kept minus |1>'s kept at 6.7 / 20 us: half-push frame turned 0 deg -0.010 / +0.003; 120 deg -0.012 / -0.017; 240 deg -0.004 / -0.010; 180 deg -0.020 / -0.016; full push then half-push +0.013 / +0.015. Far-side start minus the 180-degree start +0.039 +/- 0.011 (6.7 us), +0.018 +/- 0.011 (20 us); far-side start higher at no wait by 0.033 +/- 0.004 (0.528 against 0.495) [§129; parallax/out/qubit_fifth_run/data/reads/sides.txt].

**2026-10-02 ibm_pittsburgh -- turns.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, 20 circuits x 330 shots per read (reads 2 and 3 pulled before firing): start, wait, one look; the in-between reached by 1, 3, 5 and 9 quarter-turns, |1> by 2 and 6, |0> by 0 and 4, at waits none / 6.7 / 20 us [parallax/out/qubit_fifth_run/turns.py; §131].

What was read: One read. Level at none / 6.7 / 20 us (kept minus |1>'s kept at 6.7 / 20 us in brackets): in-between by 1 quarter-turn 0.497 / 0.476 / 0.444 (-0.009 / -0.018); by 3 0.527 / 0.517 / 0.491 (+0.026 / +0.020); by 5 0.465 / 0.438 / 0.417 (-0.014 / -0.012); by 9 0.441 / 0.422 / 0.400 (+0.000 / -0.005); |1> by 6 0.998 (-0.005 / -0.001); |0> by 4 +0.003 [§131].

**2026-10-02 ibm_pittsburgh -- hold.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads, 11 circuits x 330 shots: start |1>, 300 us of laid time, last look; inside the 300 us nothing, 1 / 3 / 9 looks, or 1 / 3 / 9 pushes to the far side; plus rulers (|0> with nine looks, |0> with ten pushes, lone looks of |0> and |1>) [parallax/out/qubit_fifth_run/hold.py].

Reported in Sections 3.1, 3.2 and 3.3.

**2026-10-02 ibm_pittsburgh -- witness.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one job of 12 circuits x 300 shots: emitters (39, no two within two links) told |1> for 0 / 20 / 40 / 60 us of a 60 us window; every qubit wired to an emitter held as a clock (86), read on two axes [parallax/out/qubit_fifth_run/witness.py].

Reported in Section 3.4.

**2026-10-02 ibm_pittsburgh -- push.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 14 circuits x 400 shots, one look at the end: starts |0>, |1>, halfway; pushes 0 / 2 back-to-back / 10 back-to-back / 10 spread (one every 30 us over 300 us); plus |1> and |0> left idle for 300 us (14 circuits in all) [parallax/out/qubit_fifth_run/push.py].

Reported in Sections 3.1 and 3.3.

**2026-10-02 ibm_pittsburgh -- looktime.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 14 circuits x 400 shots: emitters held |1>, every wired qubit a clock, far qubits looked at 3 or 9 times back-to-back inside the clocks' window; window arms 0 / 30 / 60 / 120 us [parallax/out/qubit_fifth_run/looktime.py].

Reported in Sections 3.2 and 3.4.

**2026-10-02 ibm_pittsburgh -- giveback.py** (3 jobs: 3/0/0)

What was laid: ibm_pittsburgh, every qubit, 3 reads of 6 circuits x 1000 shots in one job: |1>, 300 us of laid time, last look, with no look, or one look at 0 / 150 / 270 us; frame circuits [parallax/out/qubit_fifth_run/giveback.py].

Reported in Section 3.2.

**2026-10-02 ibm_marrakesh -- band.py** (24 jobs: 24/0/0)

What was laid: ibm_marrakesh, the 78 qubits of the 28 Sep echo run: each shot a look, an X gate or none, a look; E0 and E1 as separate jobs, 4 gaps (20 / 50 / 100 / 2000 us) x 2 = 8 jobs per read, 3 reads, 1500 shots [parallax/out/qubit_fifth_run/band.py; §137].

What was read: 73-74 of 78 qubits readable; clock A resolves on 51 qubits, clock B on 25-33. Readout-level band 0.62-0.65 (28 Sep values R^2 0.23 / 0.28 / 0.32 / 0.43): read 1 0.02-0.03, read 2 0.00-0.02, read 3 0.00-0.11. Readout-level band 0.40-0.54 (28 Sep 0.33, 0.31 / 0.26 / 0.27, 0.26): read 1 0.00-0.06, read 2 0.00-0.02, read 3 0.00-0.19. Read 3 at levels 0.67-0.68: 0.37, 0.34. Clock A middle 44 us on 28 Sep against 57 / 80 / 64 us on 2 Oct [§140; parallax/out/qubit_fifth_run/data/reads/band.txt].

**2026-10-02 ibm_pittsburgh -- noname.py** (1 job: 1/0/0)

What was laid: ibm_pittsburgh, every qubit, one read of 21 circuits x 216 shots (two more reads were planned): ten pushes with OFF / ON stretch lengths 30/30, 10/30, 90/30, 30/10, 30/90, one more push at the end, 2 and 6 pushes, the |1> start, rulers at 10 / 30 / 90 / 300 us, and emitter-and-spectator arms with frame-holding pulses [parallax/out/qubit_fifth_run/noname.py; §145].

Reported in Sections 3.1, 3.3 and 3.4.

**2026-10-02 ibm_kingston, ibm_marrakesh -- pushrep.py** (2 jobs: 2/0/0)

What was laid: The push run's 14 circuits x 400 shots, circuit for circuit, on ibm_kingston and ibm_marrakesh, one read each (two more per chip were planned) [parallax/out/qubit_fifth_run/pushrep.py; §151].

Reported in Sections 3.1 and 3.3.

**2026-10-04 ibm_kingston, ibm_marrakesh -- time_wide.py** (6 jobs: 6/0/0)

What was laid: ibm_marrakesh and ibm_kingston, every qubit, 3 reads each of 50 circuits x 300 shots: starts |0>, |1>, halfway; pushes 0 / 2 / 10 back-to-back; 10 pushes spread with spacing 5 to 150 us; in the same job the |1> decay at 30 / 100 / 300 / 600 us in three copies, idle |0> at 300 / 600 us and an echo [parallax/out/qubit_fifth_run/time_wide.py; §182].

Reported in Section 3.1.

**2026-10-04 ibm_marrakesh -- look_wide.py** (3 jobs: 3/0/0)

What was laid: ibm_marrakesh, 3 reads of 37 circuits x 400 shots: clocks held while the far qubits are looked at 1 / 2 / 3 / 4 / 6 / 9 times and over laid windows of 0 to 240 us; looked-at qubits' own fading [parallax/out/qubit_fifth_run/look_wide.py; §184].

Reported in Section 3.2.

**2026-10-04 ibm_marrakesh -- count_wide.py** (3 jobs: 3/0/0)

What was laid: ibm_marrakesh, 3 reads of 34 circuits x 300 shots: free clocks (no emitter driven) through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards [parallax/out/qubit_fifth_run/count_wide.py; §186].

Reported in Section 3.4.

**2026-10-04 ibm_kingston -- look_wide_kingston.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_kingston, 3 reads [parallax/out/qubit_fifth_run/look_wide_kingston.py; §188].

Reported in Section 3.2.

**2026-10-04 ibm_kingston -- count_wide_kingston.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_kingston, 3 reads [parallax/out/qubit_fifth_run/count_wide_kingston.py; §188].

Reported in Section 3.4.

**2026-10-04 ibm_pittsburgh -- look_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/look_wide_pittsburgh.py; §190, §228].

Reported in Section 3.2.

**2026-10-04 ibm_pittsburgh -- time_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/time_wide_pittsburgh.py; §190, §229].

Reported in Section 3.1.

**2026-10-04 ibm_fez -- five_slope.py** (1 job: 1/0/0)

What was laid: ibm_fez, every qubit, one read of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame [parallax/out/qubit_fifth_run/five_slope.py; §202].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_kingston -- five_slope_kingston.py** (1 job: 0/0/1)

What was laid: The five_slope circuits on ibm_kingston, first copy, run 391 [parallax/out/qubit_fifth_run/five_slope_kingston.py; §228].

What was read: No read on file (job status ERROR).

**2026-10-04 ibm_pittsburgh -- count_wide_pittsburgh.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_pittsburgh, 3 reads [parallax/out/qubit_fifth_run/count_wide_pittsburgh.py; §228, §230].

Reported in Section 3.4.

**2026-10-04 ibm_kingston -- five_slope_kingston2.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_kingston, second copy, run 392, with a 28 s cap [parallax/out/qubit_fifth_run/five_slope_kingston2.py; §235].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_fez -- time_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_fez, 3 reads (runs 401-403), call text hashed before firing [parallax/out/qubit_fifth_run/time_wide_fez.py; §238].

Reported in Sections 3.1 and 3.7.

**2026-10-04 ibm_fez -- look_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_fez, 3 reads (runs 411-413), call text hashed before firing [parallax/out/qubit_fifth_run/look_wide_fez.py; §238].

Reported in Sections 3.2 and 3.7.

**2026-10-04 ibm_fez -- count_wide_fez.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_fez, 3 reads (runs 421-423), call text hashed before firing [parallax/out/qubit_fifth_run/count_wide_fez.py; §238].

Reported in Sections 3.4 and 3.7.

**2026-10-04 ibm_boston -- look_wide_boston.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_boston, 3 reads (runs 431-433), call text hashed before the data existed [parallax/out/qubit_fifth_run/look_wide_boston.py; §240, §241].

Reported in Section 3.7.

Note: The earlier version of this appendix listed this family as 1 job, QUEUED (run 431). The rebuilt index lists runs 431-433, all DONE (runs 432 and 433 created 22:36 and 22:37 on 4 October).

**2026-10-04 ibm_boston -- five_slope_boston.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_boston, every qubit, one read (run 441) of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame; call text hashed before firing [parallax/out/qubit_fifth_run/five_slope_boston.py; §258].

Reported in Section 3.7.

**2026-10-04 Cepheus-1-108Q -- tune** (8 tasks: 8/0/0)

What was laid: Re-tune of the 1-2 swap on all 108 qubits, 8 tasks of 1000 shots [standoff/rigetti_time.py; §192-§193].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read1** (58 tasks: 58/0/0)

What was laid: Batch 1 of the time run on every qubit in parallel: starts 0 / 1 / halfway, ten X pushes after intervals of 0 / 1 / 3 / 8 / 20 us, each qubit's decay read at 3 / 10 / 30 us in three copies, each arm read plain and swap-then-flip with the batch's own 8-sequence readout calibration; 58 tasks [standoff/rigetti_time.py; §192-§193].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read2** (58 tasks: 58/0/0)

What was laid: Batch 2 of the same time run, 188 s after batch 1; 58 tasks [standoff/rigetti_time.py; §194].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- read3** (50 tasks: 50/0/0)

What was laid: Batch 3 of the same run with the witness layout: 7 emitters at least 5 links apart, 100 free clocks (22 / 40 / 38 at 1 / 2 / 3+ links), emitters held |1> for trains of 5 / 15 / 40 / 100 us from |0> and from |1>, clock references, an emitter ruler; 50 tasks [standoff/rigetti_time.py; §194].

What was read: Emitters' laid |1> time 5 / 15 / 40 / 100 us; booked from their own decay (25 us) 4.9 / 14.4 / 37.4 / 87.5 us from |0> and 5.1 / 15.5 / 41.1 / 96.8 us from |1>; end state on level 2 1.3-2.7%; clocks' readings of that time spread -50 to +70 us between quartiles. Clock hand kept 0.67 at 3 us and 0.27 at 10 us. Pull per us with emitters held in |1>: 0.059 (1 link), 0.028 (2 links), 0.029 falling to 0.011 (3+ links, 3 to 30 us) [§194; standoff/time20261004/read3_witness_raw.txt].

**2026-10-04 Cepheus-1-108Q -- q0_last** (8 tasks: 8/0/0)

What was laid: q0 at rest, in |1> and in |2>, watched by every other qubit as a clock over one 2 us window; 8 tasks of 900 shots, the last tasks under the day cap [standoff/rigetti_q0_last.py; §195].

What was read: Plain read of q0: rest 0.046, |1> 0.861, |2> 0.903. Clock turn over 2 us, q0 in |1> / in |2> minus at rest (deg/us): q9 +0.31 +/- 1.22 / -34.94 +/- 2.20; q1 -7.48 +/- 2.18 / -20.95 +/- 2.24; q10 -2.69 +/- 2.96 / +0.78 +/- 2.74; 101 clocks at 3+ links, median with q0 in |2> -0.62 (quartiles -2.73, +1.57) [§195; standoff/time20261004/q0_last_raw.txt].

**2026-10-04 Cepheus-1-108Q -- triA** (40 tasks: 40/0/0)

What was laid: q0 at rest / |1> / |2> for 0.5 to 6 us, every other qubit a clock, q0's own |2> population read in the same batch; 40 tasks [standoff/rigetti_triangles.py; §204].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triB** (42 tasks: 42/0/0)

What was laid: The 7 emitters pushed ten times back to back, their 22 neighbours at rest, pushed in step, or held as clocks, interleaved, three rounds 3 minutes apart, each with its own readout calibration; 42 tasks [standoff/rigetti_triangles.py; §204].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triC** (34 tasks: 34/0/0)

What was laid: The 7 emitters' |1> time during a ten-push train from |0> with L = 5 / 10 / 20 us (laid 2.50 / 5.00 / 10.00 us), echoed clocks, own-decay booking; 34 tasks [standoff/rigetti_triangle_c.py; §207].

What was read: Booked from own decay (0.881 / 0.696 / 0.568 / 0.390 at 1 / 5 / 10 / 20 us): 2.44 / 4.82 / 9.54 us; end state level 1 0.181 / 0.190 / 0.194, level 2 0.020 / 0.021 / 0.027. Clocks' medians at 1 / 2 / 3+ links: +2.75 / +1.56 / +1.82 us (L 5), +3.61 / +7.53 / +8.00 us (L 10), +10.77 / +6.91 / +6.23 us (L 20), quartiles spanning +/-10 to +/-30 us; pull from a |1> emitter 0.2-1.5 deg/us; hand kept 0.10-0.48 at L 5 [§207; standoff/time20261004/triC_raw.txt].

**2026-10-04 Cepheus-1-108Q -- triD** (50 tasks: 50/0/0)

What was laid: The push train on the 1-2 pair: 7 emitters pushed 1-2 ten times with a push after every 0.1 / 0.2 / 0.4 us, starts |1>, |2>, |0>, references held |1> and |2>, own-decay rulers; 50 tasks [standoff/rigetti_triangle_d.py; §208].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triE** (86 tasks: 86/0/0)

What was laid: N = 4 / 10 / 20 pushes across L = 1 / 2 / 4 us on the 1-2 pair, starts |1>, |2>, |0>, references held; 86 tasks [standoff/rigetti_triangle_e.py; §210].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triF** (132 tasks: 132/0/0)

What was laid: The 7 emitters held at rest / |1> / |2> for 0.25 to 6 us with every other qubit a clock, three rounds about 3 minutes apart, each with its own readout calibration; 132 tasks [standoff/rigetti_triangle_f.py; §212].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triG** (84 tasks: 84/0/0)

What was laid: Emitters held |1> or |2> for 0.5 / 2 / 4 us with the other qubits in five states (rest; halfway then turned back; the copy used in triF; |1> throughout; |1> at readout only); populations solved with three readout models; 84 tasks [standoff/rigetti_triangle_g.py; §214].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- triH** (30 tasks: 30/0/0)

What was laid: Clocks halfway for 0.5 / 2 / 4 us with the emitters at rest, emitters put in |0> / |1> / |2> at readout; the day's pairing of read axes on the held-|2> arm against both-plain and both-swap-then-flip; 30 tasks [standoff/rigetti_triangle_h.py; §216].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- sealA** (130 tasks: 130/0/0)

What was laid: After the vendor's recalibration (2026-10-04 18:02Z): emitters held in |2> for 2 / 3.5 / 4 / 4.5 / 6 us, other qubits at rest / the triF copy / |1> at readout only, three readout models, three rounds; 130 tasks [standoff/rigetti_seal.py; §219].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- sealB** (50 tasks: 50/0/0)

What was laid: Triangle D's circuits again after the recalibration; 50 tasks [standoff/rigetti_seal.py; §219].

Reported in Section 3.6.

**2026-10-04 Cepheus-1-108Q -- lookT** (18 tasks: 18/0/0)

What was laid: Our own look on Cepheus, step 1: a constant 1 us tone on each of the 7 emitters' readout frames at amplitudes 0 / 0.03 / 0.06 / 0.12 / 0.25 / 0.5, then 0.5 us to empty; emitters halfway (two hands) and in |1>; every other qubit halfway; 18 tasks [standoff/rigetti_look_tune.py; §224].

What was read: Looked-at qubits' coherence kept (mean of 7) at the six amplitudes: 1 / 0.30 / 0.36 / 0.92 / 1.99 / 2.09; |1> read-1 0.878 / 0.850 / 0.831 / 0.752 / 0.946 / 0.967. Clocks at 1 / 2 / 3+ links: kept 0.975-0.996 and turn -1.9 to +0.7 deg at 0.03-0.06; turn -15.4 / -9.7 / -4.3 deg at 0.12; turn -33 to -39 / -31 to -36 / -15 to -22 deg at 0.25-0.5 [§225; standoff/time20261004/lookT_raw.txt].

**2026-10-04 Cepheus-1-108Q -- lookTri** (84 tasks: 42/42/0)

What was laid: The look on Cepheus before the fence: the 1 us tone on the 7 emitters' readout frames at strengths 0.03 / 0.045 / 0.06, 1-6 looks, delays 0-9 us, 100 clocks with frames at +100 kHz, emitters in |1>; 42 tasks x 1500 shots. The same 42 circuits were sent twice [standoff/rigetti_look_triangle.py (backup .bak-20261004-preFence); §227, §228]. The index lists 42 completed and 42 cancelled.

What was read: Clocks turn -39.4 deg/us over the delays (moved frame 36.0). Clocks' time per look 0.484 / 0.508 / 0.500 / 0.497 us (strengths 0.03 / 0.045 / 0.06, wrapped and unwrapped). Looked-at qubits' own fall per 1.5 us look 1.441 / 1.501 / 1.143 us of plain delay (over laid 1.5 us: 0.961 / 1.001 / 0.762) [§231; standoff/time20261004/lookTri_raw.txt].

Note: Section 3.2 mentions this run (the missing fence, §231) and gives no numbers from it.

**2026-10-04 Cepheus-1-108Q -- two** (148 tasks: 74/74/0)

What was laid: A call hashed before firing: 107 qubits from |0>, ten pushes after intervals of 1 / 2.618 / 6.854 / 17.944 / 46.979 us, each against its own decay read three times in the same batch, plus back-to-back arms; 74 tasks. The same 74 circuits were sent twice [standoff/rigetti_two_call.py; §228, §232]. The index lists 74 completed and 74 cancelled.

Reported in Sections 3.6 and 3.7.

**2026-10-04 Cepheus-1-108Q -- lookTri2** (52 tasks: 52/0/0)

What was laid: The look on Cepheus with the fence: one pulse gate on all 107 qubits (barrier, the 1 us tone on the 7 emitters' readout frames, 1 us delay on every other frame, barrier), then the 0.5 us wait; strength 0.0 added as the timing check; 52 tasks of 1500 shots [standoff/rigetti_look_triangle.py; §233].

Reported in Section 3.2.


**2026-10-05 ibm_boston -- count_wide_boston.py** (3 jobs: 3/0/0)

What was laid: ibm_boston, every qubit, 3 reads (runs 451-453) of 34 circuits x 300 shots: free clocks (no emitter driven) through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards; call text hashed before firing [parallax/out/qubit_fifth_run/count_wide_boston.py; §258].

What was read: Hand kept through 32 looks over hand kept through the same laid time (mean of 3 reads), at 1 / 2 / 3+ links: 1.000 / 0.901 / 0.991. Laid time per look over the maker's look length on ibm_boston: 0.82-0.85 [§258, §262; parallax/out/qubit_fifth_run/data/reads/three_looks_minus_time_boston_20261005.txt].

In the paper: Partly reported in Section 3.7 (the 32-look ratio); the other reads are given here.

**2026-10-05 ibm_boston -- time_wide_boston.py** (3 jobs: 3/0/0)

What was laid: ibm_boston, every qubit, 3 reads (runs 461-463) of 50 circuits x 300 shots: starts |0>, |1>, halfway; pushes 0 / 2 / 10 back-to-back; 10 pushes spread with spacing 5 to 150 us; in the same job the |1> decay at 30 / 100 / 300 / 600 us in three copies, idle |0> at 300 / 600 us and an echo; call text hashed before the data existed [parallax/out/qubit_fifth_run/time_wide_boston.py; §259].

Reported in Section 3.7.

**2026-10-05 ibm_boston -- time_wide_boston2.py** (3 jobs: 3/0/0)

What was laid: The time_wide circuits on ibm_boston again, a second set of 3 reads (runs 471-473); no call written for it [parallax/out/qubit_fifth_run/time_wide_boston2.py; §265].

What was read: Ladder pace (rungs per e-fold of spacing, against one exponential) in firing order over the six jobs of runs 461-463 and 471-473: 1.314 / 1.268 / 1.088 / 1.110 / 0.940 / 1.081 (02:10 to 08:47 EDT); the chip's own decay time 272-282 us across the six; mean of the last four 1.055 (spread 0.08) [§265; parallax/out/qubit_fifth_run/data/reads/time_wide_boston_reads456_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes time_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- look_wide_phoenix.py** (3 jobs: 3/0/0)

What was laid: The look_wide circuits on ibm_phoenix (120 qubits), every qubit, 3 reads (runs 541-543) of 37 circuits x 400 shots; call text hashed before any run [parallax/out/qubit_fifth_run/look_wide_phoenix.py; §261].

Reported in Section 3.7.

Note: The freeze record for these runs hashes look_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- five_slope_phoenix.py** (1 job: 1/0/0)

What was laid: The five_slope circuits on ibm_phoenix, every qubit, one read (run 531) of 8 circuits x 800 shots: start |0>, 2 / 6 / 10 pushes with a push after every 30 us; |1> left 30 / 90 / 300 us; frame; call text hashed before any run [parallax/out/qubit_fifth_run/five_slope_phoenix.py; §261].

Reported in Section 3.7.

Note: The freeze record for this run hashes five_slope_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- count_wide_phoenix.py** (3 jobs: 3/0/0)

What was laid: The count_wide circuits on ibm_phoenix, every qubit, 3 reads (runs 551-553) of 34 circuits x 300 shots: free clocks through 1 to 32 looks at the far qubits and laid windows of 0 to 120 us; distance to the nearest looked-at qubit read afterwards; call text hashed before any run [parallax/out/qubit_fifth_run/count_wide_phoenix.py; §261].

What was read: Free clocks' hand kept 0.07-0.23 by 12-16 looks. Hand kept through 32 looks over hand kept through the same laid time, at 1 / 2 / 3+ links: 1.077 / 1.131 / 0.926; up to 8 looks, 1.03-1.15 in all three classes. Hand e-fold time 12-18 us; clocks' turn 6.8 / 13.2 / 10.2 deg/us; laid time per look 1.46-1.51 us, which is 0.754 / 0.754 / 0.777 of the maker's 1.94 us. Hand kept (1 link): 0.113 at 30 us laid and 0.178 at 60 us (+5.9 sd), 0.107 at 24 looks and 0.188 at 32 looks (+7.6 sd); 3+ links 0.077 and 0.214 (+6.4 sd), 0.077 and 0.191 (+5.5 sd); 2 links 0.085 and 0.112 from 24 to 32 looks (+2.3 sd) [§261-§263; parallax/out/qubit_fifth_run/data/reads/three_looks_minus_time_phoenix_20261005.txt].

In the paper: Partly reported in Section 3.7 (the 32-look call); the other reads are given here.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- ripple_phoenix.py** (2 jobs: 2/0/0)

What was laid: ibm_phoenix, every qubit, 2 reads (runs 561-562) of the count_wide circuits with dense laid windows (0 to 100 us every 10 us, then 120 / 140 / 160 us) and looks 1 / 4 / 8 / 16 / 24 / 28 / 32, 300 shots; no call written [parallax/out/qubit_fifth_run/ripple_phoenix.py; §264].

What was read: Free clocks' hand, per clock, kept against laid time, reads 1 / 2: 1 link 0.123 / 0.122 at 30 us, 0.210 / 0.202 at 60 us, 0.208 / 0.223 at 70 us, 0.100 / 0.090 at 100 us; 2 links 0.079 / 0.076 at 30 us, 0.131 / 0.101 at 60 us, 0.124 / 0.155 at 70 us, 0.084 / 0.087 at 100 us; 3+ links 0.104 / 0.079 at 30 us, 0.212 / 0.245 at 60 us, 0.216 / 0.252 at 70 us, 0.090 / 0.070 at 100 us; widths about 0.012-0.026. The reader marks rises at 60 us (1 link, both reads), 60 / 70 us (2 links), 50 / 60 us (3+ links) and at 120 us in read 2 (1 link, 3+ links) [§264; parallax/out/qubit_fifth_run/data/reads/ripple_phoenix_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_boston -- time_wide_boston3.py** (5 jobs: 5/0/0)

What was laid: The time_wide circuits on ibm_boston, 5 reads back to back (runs 481-485); no call written. Created 08:32 to 09:24 EDT; run 473 (08:47) was created between runs 481 and 482 [parallax/out/qubit_fifth_run/time_wide_boston3.py; §267].

What was read: Ladder pace (rungs per e-fold of spacing, against one exponential) for runs 481-485: 1.054 / 1.055 / 1.071 / 1.045 / 1.281. Across the eleven Boston jobs, a geometric settle fits with chi2 10.0 (3 parameters; flat 17.3), each step 0.42 of the last, settling at 1.056; a damped ring fits with chi2 7.9 (2 more parameters) [§267, §268; parallax/out/qubit_fifth_run/data/reads/time_wide_boston_reads789_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes time_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_phoenix -- ripple2_phoenix.py** (2 jobs: 2/0/0)

What was laid: ibm_phoenix, every qubit, 2 reads (runs 571-572) of the count_wide circuits with laid windows 0 / 10 / 30 / 60 / 90 / 100 to 160 every 10 us / 180 / 200 / 220 / 240 us and looks 1 / 8 / 16 / 32, 300 shots; no call written [parallax/out/qubit_fifth_run/ripple2_phoenix.py; §267].

What was read: Free clocks' hand kept at 60 us laid, reads 1 / 2: 1 link 0.181 / 0.204, 2 links 0.109 / 0.109, 3+ links 0.137 / 0.178; past 100 us 0.06-0.10 in every class, as recorded. The reader marks a rise at 60 us in 5 of 6 class-reads, and single later rises at 120 us (2 links, read 2) and 180 us (3+ links, read 1). Over the four dense reads (runs 561-562, 571-572; 21 laid times to 240 us), a damped beat fits with chi2 102 against 438 for a plain decay (1 link), 92 against 228 (2 links), 215 against 434 (3+ links); revival every 62-73 us, damping 22-38 us; the fitted second revival 0.003-0.021 against a floor of 0.08-0.09 [§267, §268; parallax/out/qubit_fifth_run/data/reads/ripple2_phoenix_20261005.txt].

Not reported in the paper body.

Note: The freeze record for these runs hashes count_wide_boston.py, not the script that fired; see the provenance note.

**2026-10-05 ibm_pittsburgh -- look_wide_pittsburgh_oct5.py** (1 job: 1/0/0)

What was laid: The look_wide circuits on ibm_pittsburgh, one read (run 511) after that day's recalibration, 37 circuits x 400 shots; the maker-look and time-leg reads, read against two calls hashed before the data [parallax/out/qubit_fifth_run/look_wide_pittsburgh_oct5.py; §269].

Reported in Section 3.7.

Note: The freeze record for this run hashes look_wide_pittsburgh.py, not the script that fired; see the provenance note.

**2026-10-05 Cepheus-1-108Q -- sealA** (650 tasks: 650/0/0)

What was laid: Step A of the seal circuits again, unchanged, after the vendor's recalibration of 2026-10-05 04:02Z (the chip recalibrates every 30 minutes: 04:02, 04:32, 05:02, 05:32Z): five sets of 130 tasks, the first created from 04:06Z (day 2's own set), four more from 05:00Z to 05:41Z by the riding script, one set after another. Each set: emitters held in |2> for 2 / 3.5 / 4 / 4.5 / 6 us, the other qubits at rest / the triF copy / |1> at readout only, three readout models, three rounds [standoff/rigetti_seal.py; standoff/ride_sealA.sh; §256, §260].

What was read: The four later sets, emitters' |2> after 4 us with the others half-way, em_rest model, rounds then set mean: 0.6129 / 0.6261 / 0.6422, 0.6270; 0.6473 / 0.6449 / 0.6597, 0.6506; 0.6090 / 0.6433 / 0.6016, 0.6180; 0.6602 / 0.6372 / 0.6289, 0.6421. Shared-model set means 0.6389 / 0.6506 / 0.6279 / 0.6510; em_one set means 0.6900 / 0.6912 / 0.6545 / 0.6699. Over the 18 rounds of day 1 and the five day-2 sets: 0.6016 to 0.6602, mean 0.6324. Two sets on the 05:02Z calibration, 11 minutes apart, read 0.651 and 0.618 [§260; standoff/time20261004/sealA_band_all_sets_20261005.txt].

In the paper: Partly reported in Section 3.7 (the first set of 130 tasks, the day-2 call); the four later sets are given here.

**2026-10-05 Cepheus-1-108Q -- drift_r001 to drift_r022 (22 rounds)** (660 tasks: 660/0/0)

What was laid: The drift probe: 22 rounds of 30 tasks (42,000 shots a round), one round about every 6 minutes from 10:58Z to 13:04Z, 2 to 26 minutes after the vendor's recalibrations (five calibrations, 10:32 to 13:02Z); no outcome written beforehand. Each round re-reads every corner of the seal's 4-us row: the three readout rulers (shared, 8 sequences; emitters-only with the others at rest and in |1>, 16 sequences; 1500 shots each) and the emitters held in |2> for 4 us with the other qubits at rest / half-way (the triF copy) / |1> at readout, two arms each, 1000 shots; the round's send time and the chip's calibration stamp are written with it [standoff/rigetti_drift_probe.py; standoff/ride_drift.sh; §266].

What was read: Emitters' |2> after 4 us with the others half-way, em_rest model, rounds 1 to 22 in one line: 0.6409 / 0.6322 / 0.6302 / 0.6174 / 0.6374 / 0.6330 / 0.6103 / 0.6303 / 0.6445 / 0.6308 / 0.6158 / 0.6012 / 0.6139 / 0.6251 / 0.5919 / 0.5978 / 0.6153 / 0.6122 / 0.6195 / 0.6219 / 0.6124 / 0.6072. By minutes since calibration, +2 / +8 / +14 / +20 / +26: 0.6132 / 0.6217 / 0.6266 / 0.6205 / 0.6200. All 22 rounds: 0.6201, spread 0.014, +0.3 % from 0.6180; 8 of 22 rounds within 1 % of 0.6180. Rest witness 0.66-0.68 and |1>-at-readout witness 0.56-0.57 by minutes since calibration [§266; standoff/time20261004/drift_rows_20261005.txt].

Not reported in the paper body.
