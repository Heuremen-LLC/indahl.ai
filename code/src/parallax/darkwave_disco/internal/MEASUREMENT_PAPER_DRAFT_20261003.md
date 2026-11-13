# One readout timed three ways, idle-interval decay bookkeeping, spectator-qubit readings and third-level populations on IBM Heron and Rigetti superconducting processors

**[AUTHOR -- real name at submission, his call]**
Heuremen

*Draft of 3 October 2026. Internal; not posted.*

**Source tags.** Every number carries a tag. [reads/<file>] is a read file in the data release; [code/<file>] is frozen run or analysis code in the release; [§n] is entry n of the run ledger; [SHA256SUMS.txt] is the release's hash list; [derived here] marks arithmetic done in this draft on tagged numbers. "(one job)" marks a claim that rests on a single job. Times of day are EDT on 2026-10-02 unless stated. [TO FILL: ...] marks what the sources do not hold.

---

## Abstract

We report measurements on IBM Heron processors (ibm_pittsburgh, ibm_marrakesh, ibm_kingston, ibm_fez) and a Rigetti processor (Cepheus-1-108Q). On ibm_pittsburgh the vendor states that a readout lasts 2.180 us; spectator qubits evolving freely across a block of readouts on other qubits time it at 2.37 ± 0.03 us; a qubit prepared in |1> loses per readout the population of 3.2 to 4.3 us of its own decay (eight jobs). Intervals spent in |0> add no resolved decay or excitation. Ramsey spectators read a neighbour's |1> time; a Rigetti neighbour in |2> pulls a spectator by −62.1 ± 0.6 deg/us. On both vendors a minority of qubits carry |2> population that is standing, carried between shots, or switching over minutes. A qubit prepared in |0> and given ten X gates 30 us apart ends +2.00 ± 0.16% (ibm_pittsburgh) to +2.87 ± 0.28% (ibm_kingston, one job) more in |1> than one-exponential decay bookkeeping allows. Against each interval's own measured decay (one job) the excess is −0.12 ± 0.34% to −0.97 ± 0.51%: it is accounted for by non-exponential decay. Idle |0> arms bound excitation; one of ten arms remains, at 7.5% family-wise.

(Sources for every abstract number are in Sections 3.1-3.5.)

---

## 1 Introduction

The vendor of a superconducting processor publishes per-qubit numbers -- a measurement duration, relaxation times, couplings -- and experiments usually time their events with those numbers and with the delays they schedule. Here we time and book-keep a few elementary operations a second and a third way: with spectator qubits whose phase advances at a rate set by a neighbour, and with the measured qubit's own decay. We report five measurements.

1. **The look.** One readout on ibm_pittsburgh timed by three clocks: the vendor's stated duration; spectators evolving freely across a block of readouts on other qubits; and the decay the measured qubit shows per readout (Section 3.1).
2. **The park.** Whether a qubit's decay advances while it sits in |0>: populations after X-gate trains that move a |1>-prepared qubit into |0> for alternate intervals, against bookkeeping in which relaxation acts only during |1> intervals (Section 3.2).
3. **The witness.** Ramsey spectators reading a neighbour's |1> time, and on Rigetti a neighbour in |2> (Section 3.3).
4. **The third level.** Per-qubit |2> populations at the start of a shot on two vendors, in three behaviours (Section 3.4).
5. **The push-train excess.** A qubit prepared in |0> and given ten X gates 30 us apart ends with more |1> population than one-exponential decay bookkeeping allows, on three chips. We report it as a negative result: against each interval's own measured decay the excess is not there, and we list the controls (Section 3.5).

No new physics is claimed. Comparisons are made within a single job unless stated. No numerical predictions were written before these runs; the run headers list outcome categories only [code/push.py; code/noname.py; code/hold.py; code/looktime.py; code/giveback.py; code/witness.py], so every test below is post hoc. [TO FILL: related work -- spectator (ZZ) sensing, T1 fluctuation from two-level-system (TLS) defects, leakage and reset, measurement-induced state changes. The sources cite only Karalekas et al. 2020.]

**Terms.** *Level*: the population estimate of Section 2.2 (0 at the |0> reference, 1 at the |1> reference). *Readout*: one measure instruction. *X gate* ("push"): the native x gate. *Halfway state*: the state made from |0> by one sx gate. *Emitter*: a qubit whose state a spectator reads. *Spectator* ("witness"): a neighbour of an emitter run as a Ramsey clock. *Far qubit*: a qubit wired to no emitter. *Interval*: a scheduled delay. *Median qubit*: the median over qubits (the ledger's "middle bit").

---

## 2 Methods

### 2.1 Hardware and access

- **ibm_pittsburgh**: 156 qubits, Heron revision 3, all 156 in one measurement group [reads/pittsburgh_config_timing.json]; coupling map of 176 links read at fire [reads/witness_run.txt]. Static configuration at fire: dt = dtm = 4 ns; repetition-delay range 0-2 ms, default 250 us; dynamic repetition rate enabled; measure_esp disabled; acquire alignment 1, pulse alignment 1, granularity 1, minimum length 2 [reads/pittsburgh_config_timing.json]. Stated measurement duration 2.180 us on every qubit, read at 11:02:53 [reads/maker_look_length_pittsburgh.json].
- **ibm_marrakesh, ibm_kingston**: IBM Heron [§24]. [TO FILL: processor revision and qubit count.] ibm_fez (Heron [§24]) appears only in Sections 3.3-3.4.
- IBM jobs ran through Qiskit Runtime SamplerV2 (qiskit-ibm-runtime 0.49) [code/common.py].
- **Rigetti Cepheus-1-108Q** through Amazon Braket with pulse access; 563 tasks from 2026-09-25 to 2026-09-28 [§28, §154].

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
| Short-delay levels repeated (run10.py) | pittsburgh, kingston | 10 (one job each) | 09:18:11 / 09:19:14 | [TO FILL] × 585 per start | 9 each | 3.5 |
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
| Push run, replication (pushrep.py) | kingston | 141 (one job of three planned) | 17:27:27, landed 17:30:03 | 14 × 400 | 147 | 3.5 |

Sources: [reads/none_arm_three_chips.txt; reads/short_wait_across_time.txt; reads/jump_run.txt; reads/jump_rerack.txt; reads/tail_run.txt; reads/lone_vs_tail.txt; reads/hold_run.txt; reads/discarded_hold.txt; reads/witness_run.txt; reads/close_push.txt; reads/close_looktime.txt; reads/close_giveback.txt; reads/noname_read1.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt; fire_logs/fire_logs_noname.txt; fire_logs/fire_logs_move.txt; code/tail.py; code/lone.py; code/jump.py; code/hold.py; code/witness.py; code/push.py; code/pushrep.py; code/looktime.py; code/giveback.py; code/noname.py; §114-§117, §119, §121, §132, §134, §137, §139, §145, §152, §153]. Earlier IBM jobs and the Rigetti tasks of Sections 3.3-3.4 are described there.

### 2.5 Spectators

Emitters are taken in an order permuted by a written seed (20261810), each accepted only if it is at least three links from every earlier emitter; spectators are the qubits wired to an emitter; the rest are far qubits [code/witness.py; code/looktime.py; code/noname.py]. On ibm_pittsburgh's coupling map this gives 39 emitters, 86 spectators and 31 far qubits [reads/witness_run.txt; reads/looktime_roles.json]; the same seed gives the same roles in the readout-timing and interval-length jobs [§145; code/noname.py]. A spectator is put on the equator with sx and read at the end on two axes a quarter turn apart (sx, or rz(π/2) then sx); its hand is H = (2 L_X − 1) − i(2 L_Y − 1) from the two levels, with contrast |H| and phase arg H [code/readwitness.py; code/readclose.py]. In the interval-length job each spectator also receives a Y-axis π pulse, rz(−π/2) x rz(π/2), at every instant its emitter receives an X gate, so the spectator's own frame rotation cancels over each pair of intervals while its emitter's |1> time accumulates ("frame-held") [code/noname.py; §145].

### 2.6 Decay bookkeeping

Population after a train is propagated as a two-state chain [code/readclose.py; code/readhold.py; code/readnoname.py]: during an interval of length L the |1> population survives with probability q_L and the rest goes to |0>; |0> does not change; each X gate swaps the two. The start is 0 (|0>), 1 (|1>), or the measured level of the halfway state. Two choices of q_L, both per qubit and from the same job:

- **one-exponential**: q_L = P(300 us)^(L/300), with P(300 us) the level of the qubit prepared in |1> and left 300 us [code/readclose.py; code/readhold.py; code/readnoname.py];
- **each interval's own**: q_L = P(L), the level of the qubit prepared in |1> and left L = 10, 30 or 90 us, measured in the same job (interval-length job only) [code/readnoname.py].

The bookkeeping carries no gate error; back-to-back trains (no delay between X gates) measure gate error separately. *Excess* = measured level − bookkeeping.

### 2.7 Statistics and freezing

Values are means over readable qubits unless marked "median qubit". Widths are standard deviations over 100 bootstrap resamples of shots (200 in the stopwatch job), with written seeds [code/readclose.py; code/readnoname.py; code/readwitness.py]. For three jobs we give the mean with width sqrt(w1² + w2² + w3²)/3 and each job's value [code/readclose.py]; that width assumes independent jobs and does not include job-to-job wander. Hold-run "arm minus nothing" widths are the spread over the three jobs divided by √3 [code/readhold.py].

Before firing, each run's scripts and shared modules were hashed (sha256) together with its circuit ledger into one combined hash, and a fire refuses if the code on disk differs from the freeze [code/common.py]. The raw result payload is saved with its own sha256 before parsing [code/common.py]. Analysis scripts sit outside the freeze and were run on synthetic records before the data landed [§137b, §145].

### 2.8 Controls

- **Leakage to |2>**: the halfway band, off-both-clouds and across-the-line readings (Section 2.2); the back-to-back two- and ten-gate arms of the same jobs; and an extra-X identity, level(ending in |0>) + level(one more X) − 1 = P2(2 x2 − 1) [§146-§148; code/readnoname.py].
- **Excitation during |0> intervals**: each push job's own |0>-idle-300-us arm.
- **Shot-to-shot carry-over**: next-shot conditional levels in recorded shot order [§151, §152b; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt], with Rigetti's |2> carry-over through reset as a positive control [§18, §154].

---

## 3 Results

### 3.1 The look: one readout timed three ways

**Vendor.** The stated measurement duration on ibm_pittsburgh is 2.180 us on all 156 qubits [reads/maker_look_length_pittsburgh.json]; on ibm_kingston it was 2.18 us when read on 2026-10-01 [reads/jump_rerack.txt].

**Spectators.** In the readout-timing jobs [code/looktime.py] every emitter is held in |1> and every spectator runs as a free Ramsey clock. Far qubits are held in |0> and read 3 or 9 times back to back; barriers make every spectator's free evolution span the block, and spectators are not read until after it [code/looktime.py]. Delay arms of 0, 30, 60 and 120 us in the same jobs calibrate each spectator: its phase over 30 and 60 us is fitted as aT + bT², the block's phase is converted to elapsed time on that curve and divided by the number of readouts [code/readclose.py]. Over three jobs and 83 spectators: 2.3494 ± 0.0650 us per readout (block of 3) and 2.3699 ± 0.0318 us (block of 9) [reads/close_looktime.txt]. The three jobs give 2.4718 ± 0.0512, 2.2802 ± 0.0464 and 2.3578 ± 0.0659 us (block of 9), a spread larger than their shot widths [reads/close_looktime.txt]. Spectators wired to a measured qubit give 2.3244 ± 0.0413 us and those not wired 2.3652 ± 0.0487 us (block of 9) [reads/close_looktime.txt].

**The measured qubit.** Prepared in |1>, a qubit's level after a readout falls by more than its decay over the stated duration. Converted to the time its own decay would take to give the same fall, the estimators in Table 2 give 3.2 to 4.3 us per readout. The back-to-back fall scales with the qubit's decay time as decay over a fixed time does: in thirds of the chip sorted by decay time (221 / 282 / 352 us) the pair gives 3.25 / 2.94 / 3.49 us [reads/jump_rerack.txt], and in the jump run the fall times the decay time is 3.4 / 3.2 / 3.6 us by thirds [§119].

**Table 2.** One readout on ibm_pittsburgh, three clocks.

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
| Measured qubit | per readout, from 3 and 9 readouts in 300 us | 3.5 ± 0.2 us | 3 | [§135, §139] [TO FILL: computation not in the release] |

**Two caveats in the same data.** (i) The single readout's cost read at the end of a 300-us idle wanders between jobs beyond its widths: one of the three give-back jobs reads 1.0228 ± 1.4946, 1.3144 ± 1.5800 and 0.7272 ± 1.5266 us at the three positions [reads/close_giveback.txt]; and in the hold-run jobs one readout at 150 us leaves the 300-us level unchanged within −0.0007 ± 0.0009 (median qubit; spread over jobs) [reads/hold_run.txt]. (ii) Extrapolating the long-time decay back to the first readout gives 8.27 [3.62, 12.85] us (start 1) and 6.12 [−0.07, 17.24] us (start halfway) instead [reads/jump_rerack.txt]; this includes the faster decay in the first ~20 us after preparation (Section 3.5) [§120, §121].

**Repeated readouts add up.** Nine readouts 30 us apart leave the qubit at 0.990, 0.973, 0.962, 0.947, 0.935, 0.922, 0.903, 0.894, 0.893 and 0.879 of its plain decay at successive readouts (median qubit, three jobs) [§132; reads/hold_run.txt]. At 300 us the arm minus the no-readout arm is −0.0131 ± 0.0017 (3 readouts) and −0.0289 ± 0.0014 (9 readouts) [reads/hold_run.txt]; qubit by qubit the time the qubit "says" passed is 311.5 us and 327.0 us against 300 us [reads/hold_run.txt], i.e. 3.8 and 3.0 us per readout [derived here].

**Ratios.** With 3.5 ± 0.2 us for the measured qubit and 2.3699 ± 0.0318 us for the spectators: spectator / vendor 1.087 ± 0.015; measured qubit / vendor 1.61 ± 0.09; measured qubit / spectator 1.48 ± 0.09 [derived here from §135 and reads/close_looktime.txt; widths propagated as independent].

**The same back-to-back pair on three chips** (nine qubits each; one job each). Second readout minus first: start 1, −0.0480 ± 0.0071 (ibm_marrakesh), −0.0272 ± 0.0060 (ibm_pittsburgh), −0.0204 ± 0.0053 (ibm_kingston); start halfway, −0.0163 ± 0.0051, −0.0142 ± 0.0057, −0.0067 ± 0.0053; start 0, +0.0018 ± 0.0029, +0.0082 ± 0.0036, −0.0092 ± 0.0043 [reads/none_arm_three_chips.txt]. The start-1 values are uneven across qubits: −0.006 to −0.272 on ibm_marrakesh, −0.013 to −0.119 on ibm_pittsburgh, +0.002 to −0.041 on ibm_kingston [reads/none_arm_three_chips.txt].

### 3.2 The park: intervals in |0>

If a qubit's decay advanced while it sits in |0>, populations after |0> intervals would fall below bookkeeping in which relaxation acts only during |1> intervals. Three tests on ibm_pittsburgh.

**Parked |1>-prepared qubits (hold run, three jobs).** Each arm starts in |1> and spends 300 us split into 2, 4 or 10 equal intervals with an X gate after each, so the qubit spends alternate intervals in |0> and the last X gate returns it [code/hold.py]. The bookkeeping uses only the same job's 300-us |1>-idle arm (one exponential); population that relaxed during a |1> interval is put back in |1> by the next X gate and relaxes again [code/readhold.py]. Table 3 gives the median-qubit comparison per job. Done qubit by qubit, all three arms close to bookkeeping within 0.002 [§135] [TO FILL: per-arm values and widths; the qubit-by-qubit computation is not printed in reads/hold_run.txt]. On the median qubit the "parked once" arm sits +0.0054 to +0.0086 above its bookkeeping in all three jobs [reads/hold_run.txt]; the ledger records this as an artifact of applying the bookkeeping to the median qubit [§135].

**Table 3.** Hold run, start 1, 300 us total; median qubit, jobs 1 / 2 / 3 [reads/hold_run.txt].

| Arm | Intervals | Bookkeeping | Measured | Measured − bookkeeping |
|---|---|---|---|---|
| parked once | 2 × 150 us | 0.7591 / 0.7600 / 0.7583 | 0.7656 / 0.7654 / 0.7670 | +0.0065 / +0.0054 / +0.0086 |
| alternate quarters | 4 × 75 us | 0.7189 / 0.7206 / 0.7173 | 0.7182 / 0.7203 / 0.7231 | −0.0007 / −0.0004 / +0.0058 |
| alternate tenths | 10 × 30 us | 0.6940 / 0.6963 / 0.6919 | 0.6943 / 0.6974 / 0.6887 | +0.0003 / +0.0011 / −0.0032 |

**Parked emitters (stopwatch job; one job).** Emitters held in |1> for 20 or 40 us and then moved to |0> by an X gate for the rest of a 60-us window end with |1> populations 0.0648 and 0.1348 (mean of the two spectator-axis circuits), against bookkeeping of 0.0647 and 0.1346 from each emitter's own 60-us survival, 0.7896 with its neighbours in |0> [reads/witness_run.txt; §134]. The bookkeeping reproduces as (1 − q20) q40 and (1 − q40) q20 with q_t = 0.7896^(t/60) [derived here]. [TO FILL: widths; reads/witness_run.txt prints the two circuits' values (0.0719 / 0.0576 and 0.1287 / 0.1409) and no widths.]

**Idle |0> and readouts of |0>.** A qubit left in |0> for 300 us changes its level, relative to the same job's |0> reference, by −0.0001 ± 0.0006 (push run, three jobs) and +0.0002 ± 0.0015 (interval-length job; one job) on ibm_pittsburgh [reads/close_push.txt; reads/noname_read1.txt], +0.0026 ± 0.0014 on ibm_kingston and −0.0043 ± 0.0013 on ibm_marrakesh (one job each) [reads/rep_kingston_read1.txt; reads/rep_marrakesh_read1.txt]. Nine readouts of a |0> qubit through 300 us read +0.0013, +0.0002, +0.0009, +0.0014, −0.0001, +0.0014, +0.0005, +0.0005, +0.0010 and +0.0002 (median qubit, mean of three jobs) [reads/hold_run.txt].

At this resolution -- within 0.002 qubit by qubit [§135], within 0.0086 on the median qubit [reads/hold_run.txt] -- intervals in |0> add no relaxation and no excitation, and reading a |0> qubit does not excite it.

### 3.3 The witness: spectator readings of a neighbour

**What moves a spectator (ibm_fez, Rigetti).** The state of the qubit wired to it, and not the number of other qubits active [§31]. ibm_fez q144 ran at 28.2-28.8 kHz with 0, 1 or 77 other qubits active, none wired to it, keeping contrast 0.94-0.96; 34 further ibm_fez spectators read 0 ± 10 deg between large and small groups, contrast unchanged; Rigetti q9 was flat with 0, 11 or 53 non-neighbours in |1> and with 1 or 106 qubits read at the end [§31]. With its neighbour q143 in |1>, q144 ran at 21.9 kHz (vendor table: 21.7) and with q143 on the equator at 25.1 kHz (table: 25.1); q113's frequency moved −5.1 kHz with neighbour q119 in |1> (table: −5.1); q138 moved −20 deg with two neighbours in |1> (table: −19) [§31]. On Rigetti, every qubit in |1> against a checkerboard with no neighbour in |1> raised the spectators' median contrast decay from 0.092 to 0.123 per us, with 43 of 54 lower at 6 us [§31]. These rest on 778 within-job tests, Holm-corrected [§31]. [TO FILL: jobs, dates, delays, and which vendor table.]

**A spectator timing its emitter's |1> interval (ibm_pittsburgh; one job).** Every emitter was held in |1> for 0, 20, 40 or 60 us and then moved to |0> for the rest of a 60-us window, while every other qubit ran as a Ramsey clock for the full window (300 shots) [code/witness.py; reads/witness_run.txt; §134].

**Table 4.** Spectator stopwatch; median spectator of 68 with readable contrast [reads/witness_run.txt] (one job).

| Emitter time in 1 (us) | 0 | 20 | 40 | 60 |
|---|---|---|---|---|
| Phase added by each further 20 us in 1, own sign + (deg) [quartiles] | -- | +33.9 [+27, +46] | +28.1 [+16, +39] | +23.9 [+17, +32] |
| Spectator contrast | 0.469 | 0.422 | 0.398 | 0.412 |
| Far-qubit contrast | 0.339 | 0.310 | 0.306 | 0.302 |
| Far-qubit phase change, magnitude / its shot width (deg) | -- | 20.2 / 15.7 | 18.7 / 16.6 | 9.7 / 16.5 |
| Spectator-timed duration in 1 (us) | -- | -- | 35.6 | 48.3 |

The second 20 us adds 0.78 of the first and the third 0.65 of the second (median spectator); the rate while the emitter is in |1>, from the 40-us arm, is 4.5 kHz [quartiles 3.4, 5.2] [reads/witness_run.txt]. The spectator-timed duration is the total phase divided by the phase rate of the first 20 us [code/readwitness.py]. Being watched does not change the emitter: its level after 60 us in |1> is 0.7896 with its neighbours in |0>, 0.7900 with them in |1>, and 0.7942 / 0.7824 with them running as spectators (the two readout-axis circuits); qubit by qubit, spectators minus neighbours-in-|0> −0.0029 ± 0.0086, neighbours-in-|1> minus neighbours-in-|0> +0.0040 ± 0.0136 [reads/witness_run.txt]. A model of each spectator driven by its emitter's own measured decay closes with a residual of −1.4 ± 4.8 deg, contrast ratio 1.02 ± 0.035 and no phase step at the emitter's X gate; driven by the laid time instead, the contrast ratio is 0.90 ± 0.03 and a −3.2 deg step per X gate is needed [§135; reads/stopwatch_triangle.json, 66 spectators] [TO FILL: the model, and the code that produced reads/stopwatch_triangle.json].

**Spectators during the readout-timing jobs (three jobs, 83 spectators).** With emitters in |1>, a spectator's phase (in the drive frame) advances at 3.1444 ± 0.0760 deg/us over the first 30 us [reads/close_looktime.txt]. Its contrast relative to no delay is 0.9209 ± 0.0040 after a block of 3 readouts on far qubits, 0.8256 ± 0.0052 after 9, and 0.7604 ± 0.0057 after 30 us of delay [reads/close_looktime.txt]. Whether a spectator's phase curve follows its own emitter's decay (median emitter decay time in these jobs 274.99 ± 4.27 us) better than the chip's typical decay is not resolved: fit residuals 12.8046 ± 1.0979 and 12.4828 ± 1.0555 deg, difference +0.0020 ± 0.0032 deg [reads/close_looktime.txt].

**Frame-held spectators (interval-length job; one job).** Emitters received ten X gates with 30-us intervals, starting in |0> or |1>, while their spectators received the frame-holding Y pulses at the same instants (Section 2.5). 75 spectators and 35 emitters were readable [reads/noname_read1.txt].

**Table 5.** Frame-held spectators after 300 us [reads/noname_read1.txt] (one job).

| Quantity | Emitters started in 0 | Emitters started in 1 |
|---|---|---|
| Spectator contrast | 0.1603 ± 0.0070 | 0.1625 ± 0.0073 |
| Spectator phase (deg) | −120.35 ± 17.82 | +96.67 ± 19.02 |
| Spectator level, emitter ended in 1 minus ended in 0, hand X: measured / model | +0.0138 ± 0.0090 / +0.0328 ± 0.0116 | +0.0159 ± 0.0091 / −0.0293 ± 0.0102 |
| Same, hand Y: measured / model | −0.0188 ± 0.0075 / −0.0187 ± 0.0075 | −0.0524 ± 0.0085 / −0.0318 ± 0.0078 |

Half the phase difference between the two emitter starts, averaged over spectators, is −12.47 ± 4.95 deg; half their sum, the spectator's own residual phase, is +0.60 ± 4.51 deg [reads/noname_read1.txt]. The coupling read per spectator is 16.90 ± 1.81 deg per 30-us emitter interval in |1> (median) [reads/noname_read1.txt]. The model (Table 5) is each spectator fitted from its emitter's own decay [code/readnoname.py]; it agrees with the measured hand Y for emitters started in |0>, and for emitters started in |1> it differs in sign on hand X (3.3 widths) and by 1.8 widths on hand Y [reads/noname_read1.txt; §155]. Own-emitter versus chip-typical decay in the model is again not resolved: misfit 0.0751 ± 0.0071 against 0.0747 ± 0.0070, difference +0.0004 ± 0.0006 [reads/noname_read1.txt].

**A neighbour in |2> (Rigetti).** Emitter q0 is driven to |2> and left to fall; its neighbours q9 and q1 run as Ramsey clocks; q10, two links away, is the control [§7]. With q0 in |1> a neighbour's clock moves by about 0.3 deg/us; with q0 in |2>, q9 is pulled by −62 deg/us (−173 kHz) and q1 by −27 deg/us (−74 kHz), q10 by about 0 [§7]. The fall time from |2> read from the spectator is about 20 us, with fit residuals χ² of 8.6 (q9), 11.8 (q1) and 6.2 (q10) for six numbers [§7]; q0's |1>-|2> transition is at 4.295 GHz and q9 at 4.631 GHz [§7]. With q9 the only spectator and all else parked: pull −62.1 ± 0.6 deg/us, frequency spread 16 kHz (3.5σ); spectator fall time 20.9 us (16.5-29.5) against 24.2 us from q0's own readout; forcing the readout value on the spectator fit costs Δχ² = +0.2 [§11]. With 0, 54 or 106 other spectators active: spectator fall times 21.0 / 16.0 / 23.0 us against 24.2 / 21.0 / 20.4 us from q0's readout, Δχ² +0.2 / +0.9 / +0.1; pull −62.1 / −62.3 / −59.9 deg/us; spread 16 / 18 / 12 kHz [§12]. In an earlier whole-chip run (105 other spectators) q9's fall time, 14.8 ± 5.3 us, was shorter than q0's readout value of 31.2 us (30.0-32.6) [§10]; the isolated and alternating-group runs above do not repeat that difference [§11, §12]. Neighbours q1 / q9 respond to q0's state (1.8 / 1.9 times noise when the drive pulse is played with q0 at rest; 10.5 / 22.4 times with q0 in |2>); some far qubits respond to the drive pulse even with q0 at rest (for example q43 at 13.6 times noise; q45, q5, q35 about 3-4 times), and that response varies between batches (q43 strong in two batches, absent in a third) [§11]. [TO FILL: task counts and dates for each Rigetti result.]

### 3.4 The third level

On the IBM path used here (native gates, standard measure) |2> is not read directly; ibm_pittsburgh's configuration lists measure_2 and reset_2 among supported instructions [reads/pittsburgh_config_timing.json], which were not used. On Rigetti with pulse access the |1>-|2> transition is driven and |2> is read [§5, §154]. On both vendors a minority of qubits carry a |2> population at the start of a shot, in three behaviours [§5, §6, §154]: **standing** (present at every inter-shot gap), **carried** (raised by a readout, carried into the next shot when shots are close, then draining), and **blinking** (switching on and off between batches minutes apart while the ordinary readout stays flat). Each has a textbook description: steady |2> occupancy; measurement-induced leakage that a |0>/|1> reset cannot clear; |2> population or transition-frequency switching [§6].

**Rigetti Cepheus-1-108Q (2026-09-25 to 09-28)** [§5, §6, §9, §18].
- *Baseline*: q0's |2> population at the start of a shot is 0.03 ± 0.17% alone and 0.29 ± 0.19% with the whole chip run in parallel; an entangling gate leaves +0.05 ± 0.39% on q0's |2> [§5].
- *Standing*: on 56 qubits read without ambiguity the median is 0.04%; q24 2.05%, q48 1.34%, q40 1.26%, q33 1.17% [§5]. q33 has the shortest lifetime on the chip (0.7 us) and q24 the seventh shortest; q24 and q33 are neighbours [§5, §6]. Worse readout goes with more |2>: ρ = −0.31 (p = 0.02), −0.55 before the "mirror check" [§5] [TO FILL: the two variables, and what the mirror check is]. On 25 qubits readout blur and |2> could not be separated [§5]. On three qubits (q67, q76, q85; q76 reads 1 on every shot) |2> could not be reached or read; they lie on a straight line of neighbours [§5, §6].
- *Carried*: q63 about 2.5%, q78 about 1.9%, q40 about 2.0%, draining within 60 us in all three batches; q61's drain in the first batch did not repeat [§5].
- *Blinking*: |2> read in three batches minutes apart: q52 2.0 / 2.2 / 8.9%, q36 8.5 / 9.9 / 18.9%, q5 1.7 / 5.3 / 1.7% [§5]; these qubits show no shot-to-shot memory [§6]; in a following hour of eight checks they did not blink (q52 one excursion) [§9]. The |1>-|2> frequency (Ramsey at 1.5 us) on 31 qubits with readable contrast jumped rarely and independently, about once per 7.5-minute interval, with no chip-wide simultaneous jump; two qubits hopped among a few levels held about 15 minutes with their ordinary readout flat [§9].
- *Carry-over through reset*: on q0 the reset clears |1> but sometimes leaves |2>, and the |2> left by one shot sets how the next shot starts (p = 0.001; about 0.01 after the splits examined) [§18]. An active reset made of a measurement and a conditional flip does not act on |2> (Karalekas et al. 2020) [§20]. Section 3.5 uses this as a positive control for carry-over.

**IBM (ibm_marrakesh, ibm_kingston, ibm_fez; two-readout jobs among those of 2026-09-24 to 09-28)** [§2, §22] [TO FILL: job list, shots, inter-shot gaps, and the cloud-exclusion threshold].
- Shots outside both the |0> and |1> clouds on both of two readouts: 134 on ibm_marrakesh against 6.5 expected by chance (prepared |0>), 98 on ibm_kingston against 2, about none on ibm_fez [§2]. On the qubits with the largest counts the rate is the same for prepared |0> and |1>: an X gate, which acts within {|0>, |1>}, does not move it [§2].
- *Standing*: ibm_marrakesh q14, about 1-3% at every inter-shot gap; q24, a floor of about 1% plus a carried part [§2].
- *Carried*: ibm_marrakesh q26, 4.6% of shots at 20-us gaps, gone by 250 us [§2]; two ibm_kingston qubits are also listed as carried [§5] [TO FILL: labels and values]. Chip-wide on ibm_marrakesh (74 readable qubits, inter-shot gaps 20 us to 2 ms), the median qubit reads 0.84% stray excitation at a 20-us gap above a 0.31% floor, draining on a ~72 us scale; nine per-qubit fits give drain times of 24-193 us (middle half 51-73 us) against relaxation times of 9-272 us, with no resolved relation (rank −0.6, p = 0.09) [§17, §20]; the nine fits were selected from 74 qubits [§22]. The carried excitation is not flipped by an X gate, sits in its own I/Q region off the |0>-|1> line on the same side on every chip, and lives ~55-80 us [§21].
- *Blinking*: ibm_marrakesh q60, 5-9% of shots in some jobs and about 0 in others minutes apart; q126 the same; q66, 13% in one job [§2].

### 3.5 The push-train excess (a negative result)

**Protocol** [code/push.py; code/pushrep.py]. Fourteen circuits per job: starts 0, 1 and halfway, each with no X gate, 2 or 10 X gates back to back, or 10 X gates spread over 300 us (a 30-us interval before each); plus starts 1 and 0 left idle for 300 us; one readout at the end; 400 shots. ibm_marrakesh and ibm_kingston ran the identical circuits and shots [code/pushrep.py; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

**Table 6.** Ten X gates spread over 300 us: measured level minus one-exponential bookkeeping, and the same jobs' idle arms.

| Chip (jobs) | Start 0 | Start 1 | Start halfway | Idle in 0, 300 us | Idle in 1, 300 us | Qubits |
|---|---|---|---|---|---|---|
| ibm_pittsburgh, push run (3) | +0.0200 ± 0.0016 | +0.0005 ± 0.0013 | +0.0034 ± 0.0014 | −0.0001 ± 0.0006 | 0.3131 ± 0.0013 | 141 |
| ibm_pittsburgh, hold run (3) | +0.0217 ± 0.0016 [§135] | +0.0014 ± 0.0014 [§135] | not run | not run | 0.3354 ± 0.0013 [reads/discarded_hold.txt] | 145 / 139 / 139 |
| ibm_marrakesh (one job) | +0.0274 ± 0.0028 | −0.0016 ± 0.0021 | +0.0117 ± 0.0024 | −0.0043 ± 0.0013 | 0.1786 ± 0.0019 | 143 |
| ibm_kingston (one job) | +0.0287 ± 0.0028 | −0.0124 ± 0.0024 | −0.0006 ± 0.0022 | +0.0026 ± 0.0014 | 0.2982 ± 0.0025 | 147 |

Sources: [reads/close_push.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt] unless tagged. The push run's three jobs give +0.0174 ± 0.0028, +0.0213 ± 0.0030 and +0.0213 ± 0.0023 for start 0 [reads/close_push.txt]. The hold run's start-0 arm on the median qubit gives +0.0154, +0.0139 and +0.0050 per job [§132; reads/hold_run.txt].

**Spread over qubits.** Start 0, qubit by qubit: ibm_pittsburgh (438 qubit-jobs) mean +0.0200, median +0.0133, 63% above zero, per-job medians +0.010 / +0.012 / +0.019 [§151]; ibm_marrakesh median +0.0229, 73% above zero; ibm_kingston median +0.0266, 76% [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt]. Start 1: medians −0.005 (41% above zero) [§151], −0.0047 (44%) and −0.0121 (34%) [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

**Table 7.** X gates back to back (no interval): level minus the no-gate arm [reads/close_push.txt; reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt].

| Chip (jobs) | Start 0, 2 X | Start 0, 10 X | Start 1, 2 X | Start 1, 10 X | Halfway, 2 X | Halfway, 10 X |
|---|---|---|---|---|---|---|
| ibm_pittsburgh (3) | +0.0019 ± 0.0006 | +0.0229 ± 0.0007 | −0.0020 ± 0.0007 | −0.0232 ± 0.0008 | −0.0262 ± 0.0019 | −0.1138 ± 0.0019 |
| ibm_marrakesh (one job) | +0.0063 ± 0.0013 | +0.0147 ± 0.0014 | −0.0045 ± 0.0014 | −0.0148 ± 0.0013 | +0.0017 ± 0.0030 | −0.0176 ± 0.0032 |
| ibm_kingston (one job) | +0.0029 ± 0.0017 | +0.0192 ± 0.0018 | −0.0071 ± 0.0014 | −0.0212 ± 0.0015 | −0.0190 ± 0.0036 | −0.0513 ± 0.0036 |

With no interval, starts 0 and 1 move by about equal and opposite amounts. From the ibm_pittsburgh arms, the X gate falls 1.48 ± 0.14 deg short of a half turn, plus 0.26 ± 0.12% per gate of any error that grows with the gate count (leakage wherever |2> reads, decay during the pulses, pulse noise), upper edge 0.49% [§147]. The shortfall alone predicts the halfway start's loss: 0.0258 ± 0.0024 for two gates (measured 0.0262 ± 0.0019) and 0.128 ± 0.012 for ten (measured 0.114 ± 0.002) [§149]. The spread-train excess does not follow the gate error: ibm_marrakesh has the smaller back-to-back shift (±0.0148 against ±0.023) and the larger excess (+0.0274 against +0.0200) [reads/rep_marrakesh_read1.txt; reads/close_push.txt; §152].

**Controls.**
1. *Start-independent maps.* Relaxation toward a thermal population and an imperfect X gate act on the population as affine maps that do not depend on the start; they move all three starts alike and cannot produce an excess on start 0 alone. A check at an equilibrium population of 0.026 and per-interval survival 0.89 gives −0.104% [§146]. The same holds for any map independent of the start, such as constant leakage or a spectator-shifted pulse error [§147].
2. *Excitation during |0> intervals.* Every push job carries its own 300-us |0>-idle arm (Table 6). In the interval-length job, which holds the one remaining arm below, it reads +0.0002 ± 0.0015, capping excitation over the full 300 us at ~0.3% (2σ) [reads/noname_read1.txt; §176] (one job). Per 300 us: ibm_pittsburgh −0.0001 ± 0.0006, ibm_kingston +0.0026 ± 0.0014, ibm_marrakesh −0.0043 ± 0.0013 [reads/close_push.txt; reads/rep_kingston_read1.txt; reads/rep_marrakesh_read1.txt], against excesses of +0.0200, +0.0287 and +0.0274.
3. *Leakage to |2>.* (a) The halfway band, where |2> at x2 = 0.5 would read, is flat across arms: start-0 spread train +0.09% (all readable qubits; +0.14% on the 22-28 qubits with clouds more than 8 widths apart), hold run −0.00% / +0.13%, start-1 spread +0.07%, halfway spread +0.08%, idle in 1 +0.09% [§147, §148]; a |2> population carrying the +2.0% at x2 = 0.5 would put ~4% of shots there [§147]. On ibm_marrakesh / ibm_kingston the band reads +0.0004 / +0.0034 (start-0 spread) against +0.0007 / +0.0032 (start-1 spread) and +0.0010 / +0.0050 (halfway) [reads/rep_marrakesh_read1.txt; reads/rep_kingston_read1.txt]. (b) Across the line, start-0 spread arm: −0.0001 ± 0.0005 (push run), +0.0001 ± 0.0006 (hold run) [reads/discarded_push.txt; reads/discarded_hold.txt]. (c) Spread across the line beyond the two-cloud mixture, +0.0003 ± 0.0001 for start-0 and start-1 spread arms alike; off both clouds +0.0011 ± 0.0003 (push run) and +0.0013 ± 0.0004 (hold run), with every arm that spent time or took gates at +0.0005 to +0.0012 [reads/discarded_push.txt; reads/discarded_hold.txt; §144]. (d) The back-to-back cap, 0.26 ± 0.12% per gate (0.49% at two widths), against 2.96% per gate needed by a leakage-plus-TLS model to fit all three starts [§146, §147]; x2 cancels from this cap to first order when the |2> population left after the train is the same for starts 0 and 1 [§148]. (e) A leakage-only model misses start 0 by 5.6 widths and start 1 by 6.5; a TLS-only model misses by 8.4 and 6.1 [§146]. (f) The extra-X identity (interval-length job): −0.0006 ± 0.0043 (start 0) and −0.0007 ± 0.0040 (start 1) [reads/noname_read1.txt]; it is blind at x2 = 0.5 [§147], where (a) reads.
4. *Shot-to-shot carry-over.* In recorded shot order on ibm_pittsburgh the next shot of the start-0 spread arm ends in |1> no more often after a |1> ending than after a |0> ending: −0.002 ± 0.002 over three jobs, where a carry-over making the +2.0% would read ~+0.05; lags 2 and 5 the same; circuit to circuit at the same shot number, no more than an unrelated circuit; in one job (run 92) the start-0 spread arm followed the |0>-idle arm, whose shots almost never end in |1>, and its excess was +0.0213 [§151]. A bound without a model (next-shot lean after a |1> ending × share of shots ending in |1>): ibm_marrakesh +0.0108 × 0.39 = +0.004 of +0.027 [§152b; reads/rep_marrakesh_read1.txt]; ibm_kingston at most +0.0011 [reads/rep_kingston_read1.txt]. On Rigetti, where carry-over through |2> exists, the same kind of test finds it (Section 3.4) [§18, §154].
5. *Spread of decay times across qubits* moves all three starts alike (+0.005 to +0.013) [§139]. A single-qubit model of the gate shortfall with plain decay, dephasing and frame detuning gives equal and opposite start-0 / start-1 shifts and a negative halfway shift [§139].

**Non-exponential decay.** A qubit's decay right after preparation is faster than one exponential through 300 us. In the interval-length job the |1>-idle arms keep 0.9463 ± 0.0019, 0.8609 ± 0.0025, 0.6846 ± 0.0029 and 0.3286 ± 0.0030 after 10, 30, 90 and 300 us; against one exponential through the 300-us point the first three sit −0.0141 ± 0.0019, −0.0259 ± 0.0024 and −0.0185 ± 0.0032 low [reads/noname_read1.txt] (one job). The same shape appears elsewhere: with no earlier readout the median qubit's decay clock is 208 us over the first 6.7 us and 260, 253 and 275 us over 6.7-20, 20-60 and 60-300 us (one job) [reads/lone_vs_tail.txt]; qubit by qubit the first 6.7 us run at 0.803 of the 60-300 us clock with no earlier readout (one job) and 0.686 after one readout (three jobs) [reads/lone_vs_tail.txt; reads/tail_run.txt]. Decay times also wander between jobs minutes apart: across the eight jump-run jobs a qubit's decay time scatters 1.35 times its shot width (median), more than twice on 25 qubits and three times on 4; its start-1 and start-halfway decay times, from separate circuits, move together (correlation +0.34 over all qubits, +0.71 on those 25) [§119; reads/jump_run.txt; reads/jump_cube.txt]. Single-qubit levels after a 60-us delay change by 0.2-0.4 within 4.5 minutes in both directions (rms over nine qubits 0.157 overnight and 0.164 in 4.5 minutes on ibm_pittsburgh, 0.141 overnight on ibm_kingston), while start-0 levels do not move (rms 0.011-0.019) [reads/short_wait_across_time.txt; §117].

**Table 8.** Interval-length job, ibm_pittsburgh, 150 readable qubits; level minus each bookkeeping [reads/noname_read1.txt] (one job). z is the own-interval excess over its width [derived here].

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

A reviewer pointed out that T1 fluctuation makes the ensemble decay a mixture of exponentials, which at short times lies below one exponential drawn through the long-time point; a bookkeeping that applies the measured short-time decay to every interval independently then over-subtracts, and a negative residual that grows with the number of intervals is the sign of that [§174]. The residuals in Table 8 have that shape. We take the excess against one-exponential bookkeeping to be accounted for by non-exponential decay.

**What remains.** Of the ten arms in Table 8, one stands more than two widths above its own-interval bookkeeping: ten X gates with 30-us |0> intervals and 10-us |1> intervals, +0.0170 ± 0.0064 (z = 2.66) [reads/noname_read1.txt; derived here]. With ten arms this is 7.5% family-wise [§176] (one job). The |0>-interval series 10 / 30 / 90 us under own-interval bookkeeping (−0.0139 ± 0.0071, −0.0097 ± 0.0051, −0.0007 ± 0.0054) changes by 1.5σ end to end [§176]; the |1>-interval series 10 / 30 / 90 us (+0.0170, −0.0097, −0.0062) is not monotonic [reads/noname_read1.txt]. The 35 emitters of the spectator arms, given the same ten gates, read −0.0216 ± 0.0102 (start 0) and +0.0118 ± 0.0076 (start 1) against own-interval bookkeeping [reads/noname_read1.txt]; they are outside the family of ten, and the first is 2.1σ below zero [derived here]. Not accounted for here, with one job each and no own-interval arms: ibm_kingston's start-1 column (−0.0124 ± 0.0024) and the chip-to-chip halfway start (Table 6). For the halfway start, a mixture of |0> and |1> lands on the line through starts 0 and 1 for any dynamics, with or without memory, if shots are independent [§148]; on ibm_pittsburgh the halfway start sits 4 widths off that line (+0.34 against +1.03%) [§147], which its own coherence, its neighbours' coherence, or shot-to-shot carry-over could produce [§148]. A run to separate these was frozen and not fired [§149, §157].

---

## 4 Limitations

1. **Replication depth.** Outside ibm_pittsburgh the push train was read once per chip (ibm_marrakesh run 141, ibm_kingston run 141); reads 2-3 on each were frozen and not fired [§151, §157]. The interval-length job is one of three planned (runs 122-123 frozen, not fired) [§157], and the spectator stopwatch one of three [reads/witness_run.txt]. Every own-interval number in Section 3.5 and every frame-held spectator number in Section 3.3 rests on one job.
2. **Comparisons within jobs only.** Between jobs minutes apart, single-qubit decay times and levels move by more than the shot widths (Section 3.5) [§117, §119]; the same circuit read +0.0200 ± 0.0016 (push run) and +0.0126 ± 0.0032 (interval-length job) against one-exponential bookkeeping [reads/close_push.txt; reads/noname_read1.txt]. Quoted widths are shot-resampling widths; three-job widths assume independent jobs and do not include this wander. The spectator-timed readout duration and the single-readout cost at the end of a 300-us idle scatter between jobs beyond their widths (Section 3.1).
3. **Statistic.** Means over readable qubits and median-qubit values differ in places (Section 3.2; Table 6, hold run). No qubit is removed beyond the readable-cloud rule, so qubits with decay times of about 6 to 55 us (q31, q36, q57, q66, q90) and one that reads below its |0> reference at 300 us (q137) are inside the means [§121; reads/tail_run.txt].
4. **Not measured or not controlled.** (a) T1 shot by shot within a job: the non-exponential account rests on the decay shape within jobs and on decay-time wander between jobs. (b) |2> on IBM: not read directly on the path used; bounded indirectly (Section 3.5). A push train with a direct |2> read on Rigetti was designed and not run [§154]. (c) Pulse shapes: native gates only; an X gate built from two half-gates, the nearest available way to change leakage without changing the operation, was not run on the push train [§146, §147]. (d) What the vendor schedules during a readout: ibm_pittsburgh's configuration places all 156 qubits in one measurement group [reads/pittsburgh_config_timing.json]; whether readout tones reach unmeasured qubits during a readout block, and what fills the difference between the stated and the spectator-timed duration, were not measured. (e) The halfway start's offset and ibm_kingston's start-1 column (Section 3.5).
5. **Post hoc.** No numerical predictions were written before these runs. The 7.5% family-wise figure covers the ten arms of one job. These jobs are part of 72 IBM jobs fired on five chips over 2026-10-01/02 (71 landed) [§141], after exploratory analyses that counted about 3.44 million tests across 98 analyses through 2026-09-29 [§29]; no program-wide correction is applied.
6. **Earlier analyses.** The third-level results and the ibm_fez / Rigetti spectator results (Sections 3.3-3.4) come from analyses of 2026-09-24 to 09-29 whose analysis files are not in this release [TO FILL].

---

## 5 Data and code availability

The data release (links at submission) holds, with a sha256 for every file [SHA256SUMS.txt; all 83 entries re-checked against the files for this draft]:

- **reads/** (38 files): the read outputs quoted here, the spectator role maps, and the vendor configuration fields read at fire;
- **code/** (42 files): frozen run scripts, the shared modules (common.py, live.py, parse_payload.py, analyze.py) and the analysis scripts;
- **fire_logs/** (3 files; fire_logs_after.txt is empty);
- **SHA256SUMS.txt**.

**Table 9.** First 12 hex digits of the sha256 of the files used most (full values in SHA256SUMS.txt).

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

Freeze hashes combine the code hashes with each run's circuit ledger [code/common.py]. The interval-length job's combined freeze hash begins ce322e77 and ends 5b15 [§145]; the unfired halfway-separation run's begins 49e64f32 and ends 12a7 [§149]. The IBM job ID of run 121 is db00t8k92g1c7399m6hg [§145]. [TO FILL: job IDs and full freeze hashes for every other job (kept with each run's fire records, outside the release); the raw result payloads and their sha256; the Rigetti task records (563 tasks, re-pulled with results [§28]); a physics-only extract of the run ledger [§170].]

---

## Acknowledgments

We thank an outside reviewer whose passes over an earlier draft supplied the thermal-population algebra, the leakage and TLS model comparisons, the randomized-preparation design, and the T1-fluctuation account of the push-train excess [§146-§149, §174] [TO FILL: name and permission]. [TO FILL: acknowledgment wording required by IBM Quantum and Amazon Braket.]

**AI use.** Bones, an AI (Anthropic's Claude), designed the runs with the author, wrote the run and analysis code, and drafted this text; the author answers for every line.

## References

1. Karalekas, P. J., et al. (2020). arXiv:2001.04449. Active reset by measurement and conditional flip [§20]. [TO FILL: full reference.]
2. Qiskit Runtime, qiskit-ibm-runtime 0.49, SamplerV2 [code/common.py]. [TO FILL: citation form.]
3. Amazon Braket, Rigetti Cepheus-1-108Q [§154]. [TO FILL: citation form.]
4. [TO FILL: T1 fluctuation and TLS defects; ZZ coupling and spectator sensing; leakage and reset; measurement-induced state changes; readout duration on IBM devices.]

Wayfinder and Bones

---

## OPEN QUESTIONS FOR THE AUTHORS

(Internal; not part of the paper.)

1. **Hold-run qubit-by-qubit numbers** -- park closure "within 0.002", start 0 +0.0217 ± 0.0016, start 1 +0.0014 ± 0.0014 -- exist only in §135. reads/hold_run.txt prints median-qubit values that differ (parked once +0.0054 to +0.0086; start 0 +0.0050 to +0.0154). Which statistic goes in the paper, and where is the code that computed them?
2. **3.5 ± 0.2 us per readout** [§135, §139]: the computation is not in the release. The hold run's qubit-by-qubit times give 3.8 us (3 readouts) and 3.0 us (9 readouts) per readout. Keep 3.5 ± 0.2, or lead with the eight-job range 3.20-4.26 us?
3. **Single-readout cost**: give-back 3.5-4.1 ± 0.9 us (one job near 1 us at all three positions) against the hold run's single readout at 150 us, −0.0007 ± 0.0009 in level. Report both as drafted, or rerun?
4. **reads/stopwatch_triangle.json** has no producing script in code/; §135's spectator closure (−1.4 ± 4.8 deg, contrast 1.02 ± 0.035 / 0.90 ± 0.03, −3.2 deg per X gate) cannot be regenerated from the release.
5. **The 7.5% family-wise**: it reproduces as 1 − (1 − p)^10 with two-sided p at z = 2.66 (7.6% at the unrounded z = 2.656). Confirm the method, and whether the family should include the two emitter-subset rows (one at −2.1σ).
6. **Ratios** (1.087 ± 0.015, 1.61 ± 0.09, 1.48 ± 0.09): widths are propagated in this draft. Print the ratios at all, or only the three durations?
7. **Missing run facts**: job IDs for every IBM job except run 121; per-job freeze hashes; processor revision and qubit count for ibm_marrakesh and ibm_kingston; circuit count for run 10.
8. **IBM third level**: job list, inter-shot gaps, shots and cloud-exclusion threshold for the two-readout counts [§2]; what "2.3% -> 9.4%" compares in §2; the percentages in §21; whether to print the ibm_kingston carried-qubit labels (left out here).
9. **Rigetti**: what the "mirror check" is; the two variables behind ρ = −0.31; what q33's "0.7 us" lifetime is; task counts per result; whether the task records go in the release.
10. **measure_2 / reset_2** appear in ibm_pittsburgh's supported instructions [reads/pittsburgh_config_timing.json]. Could a direct |2> read on IBM replace the indirect leakage bounds?
11. **Open arms**: ibm_kingston's start-1 column and the halfway start stay unaccounted for. The halfway-separation run (between.py) and replication reads 2-3 are frozen and unfired.
12. **Spectator-versus-table results** (§31): which jobs, which dates, which vendor table.
13. **fire_logs/fire_logs_after.txt is empty** (its sha256 is that of an empty file). Intended?
14. **References**: only Karalekas et al. 2020 is in the sources; the T1-fluctuation / TLS, ZZ-spectator, leakage / reset and measurement-induced-transition literature needs adding and checking. Reviewer acknowledgment: name and permission.
15. **7_PUBLIC's Methods line** "qubits run in random groups of three" holds only for the nine-qubit runs; the whole-chip runs drive every qubit. This draft says so.
