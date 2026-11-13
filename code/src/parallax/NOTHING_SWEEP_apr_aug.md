# NOTHING SWEEP, April -> August 2026 quantum data

Swept 9/28/2026 by Bones. Read-only on every existing file; no hardware runs; no provider network calls.
Lens: "the absence is the data." Hunting nothing-shaped things (too quiet, never seen, vanished, frozen, filed flat), not signals.
Every "chance" number below is the probability that plain physics plus shot noise gives that result or something more extreme.

Sources opened: `quantum_archive/quantum/` (April scripts, results_20260427.txt, QUBIT-DEFICIT-PROTOCOL.md, EMERGENCE-LOG-2026-04-05.md, quantum_entropy.txt, sealed_bet*.txt), `quantum_archive/event-horizon/*`, `quantum_archive/Kitchen Sink/event_horizon_*`, the seven August JSON + log pairs in `~/bones-forge/`, their scripts, `dark_floor_runs/open_everything_all_counts.json` (the 250 June-Aug circuits), the Biblioteca verdict lines (6241-6282, 7560-7600), `heuremen.org/ANOMALY-REGISTER.md`, and the cached daily IBM calibration snapshots in `holes/cache/ibm/<chip>/<day>.json.gz`. That cache is IBM's own record, already on disk, and it became the main outside ruler.

---

## HEADLINE (read this if nothing else)

1. **Kingston q1 and q16 share a failure onset in IBM's own calibration record.** On 9/24 these two seats read EXTRA 1s (q1 33%, q16 ~85%) while IBM's calibration called them healthy. In IBM's record, the same two seats started reading MISSING 1s on the same day, **July 21**: q1 went to 36-60% false-0 and q16 to 96.5-98.8% false-0, lasting to about Aug 17. They are the only 2 of 156 Kingston qubits that newly went bad on false-0 in that window (q80 went bad on false-1 the same day).
   - Chance that a random pair of Kingston qubits shares a failure-onset day (within 1 day) anywhere in the 3/1-9/25 record: **0.00074**. After a generous trial factor for choosing this test once I'd seen the series (x5-10), it is still **~0.5% or less**.
   - Plain-physics name: a shared readout-chain fault (multiplexed readout line or amplifier). q1 is 3 hops from q16 (1-2-3-16).
2. **Kingston q1: IBM's record and our shots disagree, in both directions.** IBM's calibration says q1 read 1 falsely 13-25% of the time (and 1 as 0 6-12%) on every calibration from 3/25 to 5/14. Our April shots on physical q1 say it was clean:
   - 4/5 GHZ-4 pinned [0,1,2,3]: q1 error ~0.53%, about 22 counts where the calibration predicts ~524.
   - 4/27: 49-123 counts where the calibration predicts ~463.
   - 9/24 is the reverse: calibration clean (1.0%), shots 33% false-1.
   - Wherever both can be checked, the "broken" record and the "broken" data never overlap.
   - q1 was also unstable inside April. The same forward GHZ-4 circuit on Kingston, submitted as two jobs seconds apart on 4/27 (d7nvmuqk… and d7nvmus9…), gave q1 = 66 and then 123 counts (**z = -4.15**).
   - This looks like the "BLINKING" seat class found 9/28 (third place switching over minutes). In the April-August data, it is the most nothing-shaped thing: a failure present in the record and absent from the shots.
3. **Too-quiet nulls: exactly as many as chance predicts.** 46 chi-square tests, 2 below p = 0.05, where 2.3 are expected by chance:
   - The August Event Horizon precision run: 10 identical repeats scattered at 0.58x shot noise (chi2/dof 0.33, p = 0.035), with **one value frozen three times** to 16 digits (p = 0.03; joint p = 0.003).
   - ghz_zzz's six predicted-zero angles (chi2/dof 0.18, p = 0.019). This **did not replicate**: the identical 12 circuits rerun 70 min later gave chi2/dof 1.25.
4. **Never-seen outcomes: none that plain noise doesn't explain.** Every zero cell with a meaningful expected count was checked against a decay-plus-readout model or IBM's per-qubit calibration.
5. **Vanished work: 14 items** (table C). Two share a feature: two runs landed inside IBM calibration blackouts. April 5 (all three chips uncalibrated from 4/4 14:25 to 4/6 19:52) and the 8/14 Mermin run (Kingston uncalibrated from 8/13 05:46 to 8/17 19:15). Chance: ordinary, since blackouts are weekends, ~2/7 of days.

---

## (a) TOO-QUIET nulls

Method: for every set with a flat ideal, or a fit whose shape is known, I computed chi-square against binomial shot noise. The variance is p(1-p)/N for probabilities and (1-E^2)/N for parities. The column "P(this quiet or quieter)" is the lower tail. Small values mean too quiet; values near 1 mean too loud.

### A1. Event Horizon precision, ibm_marrakesh, 2026-08-13 17:21-17:36 EDT, job d9v3aogb1g9c73a84a20
File: `~/bones-forge/event_horizon_precision_results.json` (+ .log, script event_horizon_precision.py)

- Ten identical pubs: Bell pair with RY(pi), observable -ZZ, 20,000 shots each, EstimatorV2 with readout mitigation (resilience 1, TREX).
- **The ten mitigated values sit exactly on a lattice.** value = k x 1.02521745e-4 with k an integer (max rounding error 0). That means readout mitigation divided every raw value by one shared factor, f = 0.97540283203125 = 15981/16384. That recovers the raw integers: **raw "disagree-flip" counts per rep = 345, 357, 345, 350, 321, 345, 355, 336, 344, 354 of 20,000** (raw ZZ = 0.9655).
- Plain physics expects scatter of sqrt(20000 x 0.01726 x 0.98274) = **18.4 counts**. Observed: **10.6**. chi2 = 2.97 on 9 dof, chi2/dof 0.33, **P = 0.035** (Monte Carlo 0.034).
- **Frozen value (item D1): 0.9898474438395595 appears 3 times** (reps 1, 3, 6 = raw count 345). Monte Carlo chance of any value appearing 3+ times in 10 binomial draws: **0.030**. Chance of that AND scatter this low: **0.003**.
- Two readings, and they can't be split without the job:
  - (i) An ordinary fluctuation.
  - (ii) The runtime returned a copied result for identical pubs. If 3 of the 10 are one draw, the 8 distinct values give chi2/dof 0.42, P = 0.11: no longer quiet.
  - The job sits behind the dead Aug-13 key, so it can't be re-fetched.
- Side note on the filed comparison (`noise_model_deficit_result.json`, 8/14 14:08): "measured deficit 1.018% vs noise-model 2.078%" puts a readout-MITIGATED number next to an UNMITIGATED simulation (on physical q0,q1, while the hardware layout was the transpiler's choice). The raw deficit recovered above is 3.45%, worse than the model. There is no missing noise.

### A2. ghz_zzz predicted-zero angles, ibm_marrakesh, 2026-08-13 18:30 EDT, job d9v4b87o3ppc73ajqdeg
File: `~/bones-forge/ghz_zzz_check_20260813_183141.json`

- GHZ-3 with tau/3 offsets. At theta = k*pi/3, the ideal <ZZZ> is exactly 0. Measured: **+0.0049, 0.0000, -0.0034, +0.0151, +0.0020, -0.0005**. Shot sigma = 1/sqrt(4096) = 0.0156.
- chi2 = 1.10 on 6 dof, **chi2/dof 0.18, P = 0.019**. theta = 1.047 split exactly 2048/2048 (chance 0.0125).
- **Replication test (same 12 circuits, same chip, 70 minutes later, inside idle_phase3 at 0 us delay, 19:41 EDT):** zero-angle values -0.0098, +0.0220, +0.0054, -0.0137, +0.0269, +0.0176, **chi2/dof 1.25 (P = 0.72). Did not replicate.**
- IBM re-ran Marrakesh's readout calibration at 18:38-18:41 EDT, between the two runs (all 156 qubits' readout numbers are dated 18:xx; T1/T2/gates 19:xx). The two runs of the same circuits also differ overall more than shot noise allows (8-outcome homogeneity chi2/dof 1.44 on 84 dof, P(this loud) = 0.995). That fits the recalibration.

### A3. Everything else: normal or loud
Full table below (46 tests). Nothing else sits below chi2/dof 0.5.

Loud sets (more scatter than shot noise), as the opposite-of-nothing context:
- n-body tau/3 flatness at N=3-7 (Fez 7/11).
- Pinata arb_1 and arb_2.
- idle_phase3 at 20-200 us (expected once T1 acts).
- The null-arm sweeps (the "nulls" were not nulls).
- The 18:31-vs-19:41 replicate.

| chi2/dof | dof | P(this quiet or quieter) | set | date | chip |
|---|---|---|---|---|---|
| 0.183 | 6 | 0.018 | <ZZZ> at the 6 predicted-zero angles, vs 0: ghz_zzz GHZ tau/3 (18:31) | 2026-08-13 | ibm_marrakesh |
| 0.330 | 9 | 0.035 | EH precision, 10 identical reps of Bell(theta=pi) <ZZ> | 2026-08-13 17:21-17:36 EDT | ibm_marrakesh |
| 0.727 | 11 | 0.287 | P(all_same) flatness, ghz_zzz tau/3 (ideal flat 1/16) | 2026-08-13 18:31 | ibm_marrakesh |
| 0.779 | 9 | 0.364 | <ZZZ> 12-pt sweep fit a*sin3t+b*cos3t+c: idle_phase3 tau3 1us | 2026-08-13 | ibm_marrakesh |
| 0.791 | 13 | 0.329 | 3-basis Y-null P(agree) vs 0.5 (13 angles) | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 0.883 | 22 | 0.381 | GHZ pinata arb_5: hw = a*ideal + b (24 pts) | 2026-07-11 12:18 | ibm_fez |
| 0.886 | 11 | 0.447 | 3-basis X-entangled P(agree) fit c+A*cos (13 angles) | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 0.910 | 23 | 0.415 | idle audit phase2 tau3 flatness (24 pts, variance only saved) | 2026-07-12 ~07:00 | ibm_kingston |
| 1.041 | 22 | 0.593 | tau differential: hw gap = a*ideal gap + b (24 circuits) | 2026-07-11 10:14 | ibm_kingston |
| 1.091 | 22 | 0.653 | GHZ pinata arb_3: hw = a*ideal + b | 2026-07-11 12:18 | ibm_fez |
| 1.152 | 11 | 0.685 | P(all_same) flatness, exp3 tau3 mitigated (variance only saved; upper bound) | 2026-08-13 16:52-17:36 | ibm_marrakesh |
| 1.154 | 12 | 0.689 | 3-basis Y-entangled P(agree) flat (ideal 0; mean-subtracted) | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 1.165 | 11 | 0.694 | 3-basis X-null P(agree) fit | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 1.171 | 23 | 0.741 | idle audit phase1 tau3 flatness (variance only saved) | 2026-07-12 ~07:00 | ibm_kingston |
| 1.181 | 11 | 0.706 | P(all_same) flatness, idle_phase3 tau3 5us | 2026-08-13 19:41 | ibm_marrakesh |
| 1.208 | 9 | 0.715 | <ZZZ> 12-pt fit: ghz_zzz (18:31) | 2026-08-13 | ibm_marrakesh |
| 1.214 | 13 | 0.739 | 3-basis Z-null P(agree) vs 0.5 | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 1.246 | 6 | 0.721 | <ZZZ> 6 zero angles: idle_phase3 tau3 0us (the replicate of A2) | 2026-08-13 19:41 | ibm_marrakesh |
| 1.284 | 9 | 0.760 | <ZZZ> 12-pt fit: idle_phase3 tau3 0us | 2026-08-13 | ibm_marrakesh |
| 1.286 | 11 | 0.775 | 3-basis Z-entangled P(agree) fit | 2026-06-25 18:47 | ibm_kingston q0,q1 |
| 1.349 | 6 | 0.769 | <ZZZ> 6 zero angles: null_arms plus3 | 2026-08-13 19:30 | ibm_marrakesh |
| 1.405 | 9 | 0.821 | <ZZZ> 12-pt fit: idle_phase3 tau3 5us | 2026-08-13 | ibm_marrakesh |
| 1.413 | 11 | 0.841 | P(all_same) flatness, idle_phase3 tau3 1us | 2026-08-13 19:41 | ibm_marrakesh |
| 1.440 | 84 | 0.995 | REPLICATE ghz_zzz vs idle_phase3 0us, same 12 circuits, 8-outcome homogeneity | 2026-08-13 | ibm_marrakesh |
| 1.460 | 25 | 0.936 | state_change 1q Ry sweep fit | 2026-08-13 19:32 | ibm_marrakesh |
| 1.461 | 11 | 0.861 | P(all_same) flatness, exp3 tau3 raw (variance only saved) | 2026-08-13 16:52 | ibm_marrakesh |
| 1.493 | 22 | 0.936 | GHZ pinata arb_4 fit | 2026-07-11 12:18 | ibm_fez |
| 1.496 | 23 | 0.941 | P(all_same) flatness, GHZ pinata tau/3 | 2026-07-11 12:18 | ibm_fez |
| 1.596 | 3 | 0.812 | Mermin: 4 setting magnitudes equal | 2026-08-14 11:14 | ibm_kingston |
| 1.642 | 22 | 0.971 | GHZ pinata arb_1 fit | 2026-07-11 12:18 | ibm_fez |
| 1.695 | 11 | 0.932 | P(all_same) flatness, idle_phase3 tau3 0us | 2026-08-13 19:41 | ibm_marrakesh |
| 1.714 | 11 | 0.936 | EH 4-outcome P(agree) fit c+A*cos | 2026-06-25 | ibm_kingston q0,q1 |
| 1.810 | 11 | 0.953 | idle_phase3 tau3 200us (not flat once T1 acts) | 2026-08-13 | ibm_marrakesh |
| 1.904 | 6 | 0.924 | <ZZZ> 6 zero angles: idle_phase3 tau3 1us | 2026-08-13 | ibm_marrakesh |
| 1.922 | 23 | 0.995 | n-body N=3 tau/3 flatness | 2026-07-11 14:59 | ibm_fez |
| 2.103 | 11 | 0.983 | idle_phase3 tau3 100us (not flat) | 2026-08-13 | ibm_marrakesh |
| 2.143 | 9 | 0.977 | <ZZZ> 12-pt fit: null_arms plus3 | 2026-08-13 19:30 | ibm_marrakesh |
| 2.399 | 11 | 0.994 | idle_phase3 tau3 20us (not flat) | 2026-08-13 | ibm_marrakesh |
| 2.468 | 23 | 1.000 | n-body N=7 tau/3 flatness | 2026-07-11 | ibm_fez |
| 2.561 | 22 | 1.000 | GHZ pinata arb_2 fit | 2026-07-11 | ibm_fez |
| 2.933 | 11 | 0.999 | idle_phase3 tau3 50us (not flat) | 2026-08-13 | ibm_marrakesh |
| 2.991 | 9 | 0.999 | <ZZZ> 12-pt fit: null_arms ztwirl | 2026-08-13 19:30 | ibm_marrakesh |
| 4.136 | 23 | 1.000 | n-body N=5 tau/3 flatness | 2026-07-11 | ibm_fez |
| 4.196 | 23 | 1.000 | n-body N=6 tau/3 (ideal 0) | 2026-07-11 | ibm_fez |
| 4.214 | 6 | 1.000 | <ZZZ> 6 zero angles: null_arms ztwirl (offset ~ -0.027, not zero) | 2026-08-13 | ibm_marrakesh |
| 9.247 | 6 | 1.000 | <ZZZ> 6 zero angles: idle_phase3 tau3 5us (decay adds a cos3t term) | 2026-08-13 | ibm_marrakesh |

Look-elsewhere: 46 tests, 2 at P < 0.05, 2.3 expected. **The too-quiet count is at chance.** April has no per-point repeat data (raw gone), so April can't be tested for quiet scatter.

---

## (b) NEVER-SEEN outcomes (zero or near-zero counts where plain noise expects >= 3)

All 250 June-August count tables were scanned. Zero cells exist in two experiments only.

| # | date / time | chip | where | numbers | plain-physics expectation | verdict |
|---|---|---|---|---|---|---|
| B1 | 8/13 19:30 EDT | ibm_marrakesh, layout unknown | ghz_null_arms `plus3`, theta=0.524: logical q2 is ideally a pure 0 | q2 read 1 in **2 of 4096** (outcomes 001/101/111 never seen) | IBM chip-median false-1 at 23:59Z 8/13 = 0.66%, so 27 expected (P = 7e-10). But 7% of Marrakesh qubits had false-1 <= 0.05%, and the no-entangling |+++> arm can be laid out on the chip's cleanest seats. Chance for a random chip qubit: 0.078 | nothing-shaped seat, ordinary explanation |
| B2 | same job | same | theta=4.712: logical q0 ideally pure 0 | q0 read 1 in **4 of 4096** (100/110 never seen) | 27 at chip median; random-qubit chance 0.127 | same |
| B3 | same job | same | ideally-1 cases | q0 lost 61, q1 lost 48, q2 lost 27 (of 4096); logical q1 false-1 = 31 (0.76%) | chip-median false-0 1.39%, so 57 expected | q2 is quiet in BOTH directions (0.05% / 0.66%); q1 is the noisiest of the three |
| B4 | 8/13 19:41 | ibm_marrakesh | idle_phase3 tau3 200 us, theta=0.524 and 2.618 | '111' = **0** in both | Model (0 us distribution x per-qubit fitted T1 survival 0.30-0.41 + 0.66% false-1): 2.28 and 1.85 expected, P(0) = 0.10 and 0.16 | not significant |
| B5 | same | same | all 1,148 cells with expected >= 3, all delays | only 2 cells with <= 2 observed (100us arb theta=3.665 '111': 2 vs 7.3, P = 0.024; 200us tau3 theta=2.094 '111': 2 vs 6.1, P = 0.057) | with 1,148 cells tested, two cells at P ~0.02-0.06 is what chance gives | none found |
| B6 | 7/11 12:18 | ibm_fez | pinata readout-confusion matrix | 25 zero cells | max expected in any zero cell = 0.47 (all are two-bit slips) | none found |
| B7 | 4/5 22:43 | ibm_kingston q0-q7 | QRNG 256 x 8-bit words | 94 of 256 patterns never seen | 94.7 +/- 7.7 expected | none found; textbook |

Side fact from B6: in the Fez pinata, logical q1 flips both ways at ~2% (0->1 2.05%, 1->0 2.01%) while q0/q2 gain 1s at 0.35%/0.16%. That's a seat that gains 1s as often as it loses them.

**(b) summary: no never-seen outcome survives a plain model.** The one sticky shape is B1-B3: in the |+++> arm, two seats were near-perfect readers (2 and 4 false 1s in 4096). That is expected when the transpiler picks the chip's quietest seats. It can't be confirmed, because the August layout sits behind the dead key.

---

## (c) VANISHED work

| # | when | what vanished | device | status / evidence |
|---|---|---|---|---|
| C1 | Apr 5-27 | **All April raw shots.** "Old IBM instance locked" (Biblioteca 6241). EMERGENCE-LOG says "All eight jobs live in IBM's permanent records", but they are no longer reachable. Only 3 April scripts ever wrote a file (qrng_kingston, quantum_bet, quantum_bet_100); all others printed to stdout only | Kingston/Marrakesh/Fez | unrecoverable |
| C2 | Apr 5 ~14:00 EDT | Eagle comparison (ibm_brisbane, kyiv, sherbrooke) **rejected**: "no backend matches criteria" (free tier Heron-only). Lumen's Eagle prediction archived, never run | — | never run |
| C3 | Apr 7 07:08 | `ghz8_fleet.py` is a **0-byte file**; the other fleet scripts exist | — | empty |
| C4 | Apr 27 | QUBIT-DEFICIT protocol Exp B (mid-circuit deficit) and Exp C (entanglement-scaled deficit) **never run**. B was measured 9/24 from dark_link shots; C never | Kingston | C still unrun |
| C5 | Jun 25 | IonQ **hardware call errored**; file is simulator only. Rigetti 6/26 file is simulator only | IonQ/Rigetti | no hardware data |
| C6 | Jun 25 17:41 EDT | June Event Horizon job "gone from IBM, can't be re-fetched" (Biblioteca 6253). Also: in IBM's record, the q0/q1 readout numbers stored in the file are dated 17:54 EDT, about 12 min after the file was saved (17:41 local). The file's own "17:52:53Z" label looks like the same moment mis-tagged as UTC | Kingston q0,q1 | unrecoverable |
| C7 | Jul 11-12 | **Idle-audit Phase 3, job d99nffl2su3c739kmfs0**: 480 circuits, 10 delays 0-200 us, Kingston. "submitted_but_queued" / "IBM free tier exhausted before job completed". **Never returned** | Kingston | finished 8/13 as a 168-circuit, 7-delay version on a different chip (Marrakesh); delays 0.5, 2, 10 us **never measured** |
| C8 | Jul 11-12 | **Per-outcome raw counts for every July run** (pinata, gradient, n-body, idle audit, tau): only P(all_same) or agree/disagree kept. Recovery attempt 8/13 18:28 (`find_ghz_jobs.py`, `scan_keys*.py` over 7 candidate keys) wrote `ghz_job_candidates.json` = **`[]`** (0 candidates) | Fez/Kingston | unrecoverable |
| C9 | Jul 11 | Paper 4 factorial (2,880 circuits) and Experiment 3 (basis-universal pinata, proposal 8/13 16:06) **never run** | — | never run |
| C10 | Aug 13 16:52-17:36 | Estimator runs saved **no counts**. exp3 saved only 6 variance numbers (the 72 per-angle values per run discarded); EH precision saved 10 mitigated values (raw recovered here by the lattice) | Marrakesh | partly recovered |
| C11 | Aug 13-14 | The **Aug-13 key is dead** ("no access to the instance"), so no August job can be re-fetched and **every August layout is unknown** | Marrakesh/Kingston | locked |
| C12 | Apr 4 14:15-14:25 -> Apr 6 19:25-19:55 | **IBM calibration blackout on all three chips**, covering the whole 4/5 first session and the 4/5 QRNG/coin flips | all 3 | IBM record |
| C13 | Aug 13 05:46 -> Aug 17 19:15 (Kingston); Aug 14 11:04/16:18 -> Aug 17 (Marrakesh/Fez) | **IBM calibration blackout**; the **8/14 11:14 Mermin run** sits inside Kingston's | all 3 | IBM record |
| C14 | Jun 25 | 3-basis X-null "broken" (a product state has structure in X), Y arm measures a different observable, so the three-basis comparison is void | Kingston q0,q1 | filed inconclusive |

---

## (d) FROZEN values

| # | when / where | the repeat | chance under plain physics | reading |
|---|---|---|---|---|
| D1 | EH precision, Marrakesh 8/13 17:21-17:36 | **0.9898474438395595 x3** of 10 reps (raw 345 of 20,000 each time) | 0.030 for any triple; 0.003 jointly with the low scatter | a fluctuation, OR the runtime returned a copied result for identical pubs. Untestable (dead key) |
| D2 | April 27 Exp A, Kingston, physical q0-q3 pinned | **Slot-matched equality:** forward q0 (measured 1st) = reverse q3 (measured 1st) = **59** counts; forward q1 (2nd) = reverse q2 (2nd) = **66**. Slots 3 and 4 differ (78 vs 98; 144 vs 116). Qubit-matched pairs: 0 of 4 equal | 2 of 4 slot pairs exactly equal under equal means: **0.006**. All 24 April-27 values: **5** exact equal pairs (also sim q0 = q3 = 55; B-Kingston q0 = q2 = 63; B-Fez q1 = q2 = 99) vs **2.1** expected, P = **0.060**; inside Exp A 3 vs 0.75, P = **0.043** | weak; it lines up with the "measurement order" story (same slot, same count), but the raw shots are gone, so it can't be retested |
| D3 | ghz_zzz theta=1.047 | parity exactly 2048/2048 | 0.0125 | part of A2 |
| D4 | Pinata Fez 7/11 | f_ghz baseline = 3982/4096 = confusion diagonal M[110,110] = 3982/4096 | ~0.2 (4 diagonal entries near 3982) | none |
| D5 | July value arrays (pinata, n-body) | exact duplicates within each 24-point array: all at or below expectation (e.g., pinata tau 1 vs 3.0 expected) | — | none |
| D6 | all 250 June-Aug count tables | identical full count tables | 0 found | none |
| D7 | tau-differential "sim" rows | totals 4094/4092, not 4096: the "simulator" is exact probabilities rounded down, zero shot noise | — | an artifact, not hardware; harmless |
| D8 | file level | `event-horizon/results_{ghz,gradient,nbody}.json` are byte-identical copies of the Kitchen Sink files | — | copies, not independent data |

Opposite of frozen, same April file: the Exp A forward run and the Exp B Kingston run are the **same circuit on the same chip in adjacent jobs**. They agree on q0 (59 vs 63), q2 and q3 (z 1.3, 1.2), but **q1 jumps 66 -> 123 (z = -4.15)**. Only q1 moved.

---

## (e) FLAT results filed as null / textbook / retracted (stack these)

| date | chip | run | actual numbers | filed as |
|---|---|---|---|---|
| 4/5 | Kingston/Marrakesh/Fez q0-3 | GHZ-4 chip triplet | noise 3.25% / 6.2% / 11.6%; Kingston pooled (n=3) q0 0.86, q1 0.55, q2 0.47, q3 0.67% (4096-shot run: q1-q3 0.51-0.54%) | "q2 always coldest" self-retracted (q1-3 tied at 4096 shots) |
| 4/5 22:48-22:52 | Kingston q0 | sealed coin flips | 7/20, 53/100 ones; longest runs 6 | fair (textbook) |
| 4/5 22:43 | Kingston q0-7 | QRNG | per-qubit P(1) 0.469-0.539 (max z 1.25); 94 of 256 patterns unseen vs 94.7 | textbook |
| 4/27 | Kingston | Exp A order reversal | fwd 1.44/1.61/1.90/3.52%; rev 2.83/2.39/1.61/1.44%; sim 1.34/1.20/0.95/1.34% | reinterpreted: measurement-order (readout timing) effect |
| 4/27 | 3 chips | Exp B triplet | q3 hottest: Kingston 3.05, Marrakesh 2.88, Fez 6.62% | "CONFOUNDED: q3 always measured last". IBM's 4/27 calibration also has Fez q3 as the worst reader (4.2% average); Kingston's calibration-worst is q1 (11.3%), which the data never shows |
| 4/27 | Kingston | Exp C Grover | iter 4: 1.1% ideal -> 4.1% hw | depolarizing, not resonance |
| 6/25 | Kingston q0,q1 | Event Horizon sweep | endpoint gap/rad 0.2998 vs 1/pi 0.3183; hw closer to 1/pi at 7/12 angles | noise shrinkage, not attraction |
| 6/25 | Kingston q0,q1 | 4-outcome | P01/P10 at 0 deg = 89/14 = 6.36x | explained: ~3.8% loss on q1 before the tilt |
| 6/25 | Kingston q0,q1 | 3-basis | Z-null chi2/dof 1.21; X-null not null; Y different observable | inconclusive / void |
| 7/11 00:21 | Fez | EH repeat | hw mean dev 0.703 vs sim 0.762 | noise shrinkage |
| 7/11 10:14 | Kingston | tau differential | locked metric: tau 0.064, arb 0.027, pi 0.080; T5 null gap -0.0112 +/- 0.0156 | H1 FAILS |
| 7/11 12:18 | Fez | GHZ pinata | tau/3 mean 0.0661 (ideal 1/16), var 2.16e-5; arb var 0.013-0.053 | ratio built into the design (ideal infinite) |
| 7/11 13:52 | Fez | gradient | r = 0.9916 vs sim | textbook |
| 7/11 14:59 | Fez | n-body | N=3/5/7 flat-ish (loud: chi2/dof 1.9-4.1); N=4 not flat by design; N=6 0.0029 vs ideal 0 | textbook (formula wrong for even N) |
| 7/12 | Kingston | idle audit | ratio 2180.9 -> 991.9; tau3 var 1.75e-5 -> 2.30e-5 | arbitrary sets' swing shrank |
| 8/13 16:52-17:36 | Marrakesh | exp3 readout | ratio 1557 raw -> 2083 mitigated | noise-floor meter |
| 8/13 17:21-17:36 | Marrakesh | EH precision | gap 0.98983 +/- 0.00034; per-rad 0.31507 [0.31486, 0.31529] excludes 1/pi and 1/3; "missing 0.01017 = 1/pi^4" | 1/pi^4 RETRACTED 9/24 |
| 8/13 18:31 | Marrakesh | ghz_zzz | amplitude 0.237 (pred 0.25), sign opposite to the written formula | textbook sin3t, sign convention |
| 8/13 19:30 | Marrakesh | null arms | plus3 amp 0.2695, ztwirl 0.2737 (sign-flipped) | "nulls" not nulls; ZZZ can't separate GHZ from product |
| 8/13 19:32 | Marrakesh | state change | smooth cos^2: c = 0.0039, A = 0.9895, phi = -0.005 rad | dial, not switch |
| 8/13 19:41 | Marrakesh | idle_phase3 | 1s lost 0 -> 0.02 (5us) -> 0.07 -> 0.14 -> 0.23 -> 0.34 (200us); per-qubit survival at 200us 0.32/0.30/0.41 | T1 decay |
| 8/14 11:14 | Kingston | Mermin | M = 3.798 +/- 0.007 (bound 2) | textbook GHZ |
| 8/14 14:08 | sim | noise-model deficit | sim 2.08% vs "measured 1.018%" | mismatched comparison (mitigated vs unmitigated); raw is 3.45% |

---

## ALIGN

| # | what lines up | items | honest chance | strength |
|---|---|---|---|---|
| L1 | **Same seats, same onset day**: Kingston q1 and q16 (the 9/24 extra-1 seats) both start failing in IBM's record on **2026-07-21** (false-0: q1 0.395, q16 0.978 on day one) and recover about 8/17-18. Only these two of 156 newly failed on false-0 in 7/21-8/12 (q80 failed on false-1 the same day) | 9/24 anomalies + IBM record | random-pair shared onset (+-1 day), whole Mar-Sep record: **7.4e-4**; ~0.5% after trial factor | **strong** |
| L2 | **q1's record and q1's shots never agree when either says "broken"**: record broken 3/25-5/14 (13-25% false-1), our shots clean on 4/5 (~22 vs ~524 expected counts) and 4/27 (49-123 vs ~463); record clean 9/24, shots 33% false-1. Plus the 4/27 q1 jump 66 -> 123 between adjacent jobs (z -4.15). **Same sign both times** (extra 1s): in April only the record shows it, on 9/24 only the shots do | C1/D2 April, 9/24 | the April mismatch alone is beyond chance (hundreds of counts); the "blinking seat" reading is an interpretation | **strong (mismatch), open (why)** |
| L3 | q1 also co-moves with **q96** (the April "coin-flip qubit", AR-009/013): both went bad 3/25 (with q102, q116) and both healed 5/15, the day q16 blipped (5/15-18) | IBM record | same shared-onset chance, 7.4e-4 per pair | supports a readout-group story |
| L4 | Both too-quiet hits (A1, A2) on Marrakesh 8/13, 17:21-18:31 EDT, parity observables, right before IBM's 18:38-18:41 readout recalibration | A1, A2 | 25 of 46 tests were Marrakesh 8/13, so both hits landing there: (25/46)^2 = ~0.3 | weak |
| L5 | "qubit 1" as the noisy / gaining seat: Fez pinata logical q1 (symmetric 2% flips), Marrakesh plus3 logical q1 (highest false-1, 0.76%), Kingston physical q1 | B3, B6, L2 | logical labels are not physical seats; P(both logical q1s worst by chance) = 1/9 | weak (naming coincidence) |
| L6 | Runs inside IBM calibration blackouts: 4/5 (all chips) and 8/14 Mermin (Kingston) | C12, C13 | blackouts are weekends, ~2/7 of days; 2 of ~8 run-days is ordinary | none |
| L7 | Measurement slot: April D2 (first- and second-measured slots give identical counts across order reversal) + the April "last measured hottest" | D2 | 0.006 local, ~0.06 across all April values | weak |
| L8 | Same number across experiments (1/16, 1/64 = 0.015625 = Kingston q1 false-0 on 6/25, 345/20000, 3982/4096, 0.98985) | — | nothing repeats beyond the within-file cases above | none found |
| L9 | Corner qubit 0 | April "q0 hottest" (4/5) | Fez q0 T1 = 42 us that day (calibration explains it); Marrakesh q0 hot in data (2.9%) but not in calibration (0.6%); Kingston q0 false-0 3.3% | Marrakesh q0 is a smaller record-vs-data mismatch; single run, can't retest |
| L10 | Time of day | all | runs cluster in EDT afternoons/evenings; no shared clock time beyond that | none found |

---

## What would test the strong ones (no new hardware needed)

1. **L1/L2, readout-group hypothesis.** q1's false-1 rate should depend on what q16 (or q96/q80) was doing in the same shot. In any 9/24 job where q1 and q16 were both measured, split q1's false-1 rate by q16's reading. If q1 and q16 were never measured in the same job, say so. That absence would itself explain why our shots and IBM's all-qubits-at-once calibration disagree.
2. **L2**: from the cache, pull q1's 4/5 and 4/27 readout-calibration timestamps against the job times (4/27 calibration 19:23 EDT is after the ~16:00 runs; 4/26 said 18.3%). The broken record brackets our clean shots on both sides.
3. **A1**: if any key can still list job d9v3aogb1g9c73a84a20, check whether pubs 0, 2 and 5 carry identical metadata. That separates "frozen copy" from "fluctuation".

Analysis scripts (throwaway, scratchpad): quiet.py, never.py, frozen.py. They reproduce every number above from the files named.
