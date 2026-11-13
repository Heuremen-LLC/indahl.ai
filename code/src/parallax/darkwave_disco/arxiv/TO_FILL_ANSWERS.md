# TO_FILL answers (measurement paper 2026-10-04)

Source tags: [§n] ledger entry in /Users/heuremen/bones-forge/parallax/THIRD_RUNG_20260928.md (entries 1-33 there are headed "## n."); other tags are file paths. No value below is recomputed except where a command is given with its exact output. Times: IBM index times are EDT; Braket index times are UTC (EDT = UTC minus 4 h, marked "derived").

Status per gap:

| # | Gap | Status |
|---|---|---|
| 1 | Table 1, run10.py circuits × shots | filled |
| 2 | 3.5 ± 0.2 us computation | not recoverable as a computation (ledger/triangle-file arithmetic located; no script) |
| 3 | Section 3.3 hold-run qubit-by-qubit values | filled (and the paper's "within 0.002" sentence conflicts with §180; see 3) |
| 4 | Section 3.3 stopwatch widths | partly (reader reproduces the values, prints no widths; nearest widths located) |
| 5 | Section 3.4 §31 jobs, dates, delays, table | filled |
| 6 | Section 3.4 model and code for stopwatch_triangle.json | filled (code only exists in the session transcript; reproduced exactly; text embedded below) |
| 7 | Section 3.4 Rigetti task counts and dates | filled (mapping of experiment name to § inferred from matching dollar figures) |
| 8 | Section 3.5 the two variables and the mirror check | filled (mirror-check code only in session transcript; text embedded below) |
| 9 | Section 3.5 IBM job list, shots, gaps, threshold | filled; the 134 / 98 counts themselves have no script on disk |
| 10 | Section 3.5 two ibm_kingston carried qubits | filled |

---

## 1. "[TO FILL] × 585 per start" (Table 1, Short-delay levels repeated (run10.py))

Fill: **9 × 195**

- run10.py docstring: "START, LOOK, WAIT 60 us, LOOK for OFF / MID / ON, laid THREE times (copies), 195 shots each (585 per start)" [/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/run10.py]. Constants there: `COPIES = [1, 2, 3]`, `SHOTS5 = 195`; `specs()` yields one circuit per (copy, start) with `pre_waits_us: [0, 60]`.
- Freeze records: `shots_per_circuit: 195`, `order_seed: 20261102` [freeze_ibm_pittsburgh_run10.json; freeze_ibm_kingston_run10.json in the same folder].
- Fire records: each run10_results.npz has 18 arrays, `<start>|w60|c<copy>__L1` and `__L2`, each shape (195, 9) = 9 circuits (3 starts × 3 copies) × 2 looks, 195 shots, 9 qubits [data/fire/ibm_pittsburgh/run10_results.npz; data/fire/ibm_kingston/run10_results.npz]. Pittsburgh job davqu5492g1c7399clc0, Kingston job davquks92g1c7399cls0 [run10_job.json].
- Note: run10.py line "3 copies = 636 per (start, wait)" in the SHOTS5 comment is stale; 3 × 195 = 585, which matches the docstring and the paper.
- Start times in the paper cell (09:18:11 / 09:19:14) vs job records: submitted 09:18:12 and 09:19:15 EDT [run10_job.json]; created 13:18:12.8Z and 13:19:15.3Z [run10_payload_meta.json].

## 2. "[TO FILL: computation not in the release]" for 3.5 ± 0.2 us per readout [§135, §139]

Status: the computation is not recoverable. What exists:

- Ledger text: §135 "pile-up 3.5 +- 0.2 per look over 3 and 9 looks" (line 1905) and §139 "pile-up 3.5 +- 0.2, give-back 3.5-4.1" (line 1928) [THIRD_RUNG_20260928.md].
- Same numbers split by block size, in the file §135 cites: "pile-up (same job, 3 reads): 3 looks 3.6 +- 0.5 us each, 9 looks 3.5 +- 0.2 each" [/Users/heuremen/bones-forge/parallax/TRIANGLE_OF_FUCKUPS_20261002.md line 333; release copy /Users/heuremen/bones-forge/parallax/darkwave_disco/for_indahl_ai/fuckups/TRIANGLE_OF_FUCKUPS.md line 329]. So the ± 0.2 is the width attached to the 9-look value there.
- §132 states the underlying quantity in words: nine looks "add 27-37 us to the bit's age: about one look's own inside length (3.5 us) each" [THIRD_RUNG_20260928.md line 1884-1893].
- No script writes 3.5 or ± 0.2. Searched: out/qubit_fifth_run/*.py (readhold.py, readclose.py, readlook_3and9.py, readjump.py), the release code/, ~/.claude/jobs/ee23053e/tmp, and the earlier audits, which record the same finding: "'+-0.2' is not computed by any script on disk" [/Users/heuremen/bones-forge/parallax/darkwave_disco/internal/TRIPLE_PASS_20261003/PASS_C_OWN_CLOCK.md C13; PASS_A_OBSERVER.md line 363].
- Existing printed values for the same arms: hold_run.txt bit by bit 311.5 us (3 looks) and 327.0 us (9 looks) against 300; from the median bits 320.1 / 312.4 / 308.9 and 336.3 / 336.5 / 337.7 [reads/hold_run.txt]. The paper already derives 3.8 and 3.0 us per readout from these.
- Arithmetic observation (not attested in any source; derived here, do not cite as the source): the inverse-variance mean of 3.6 ± 0.5 and 3.5 ± 0.2 is 3.51 ± 0.19.

Suggested replacement text: "[§135, §139; TRIANGLE_OF_FUCKUPS.md Triangle II: 3 looks 3.6 ± 0.5 us each, 9 looks 3.5 ± 0.2 us each, same job, three reads; the script that produced these is not on disk]".

## 3. "[TO FILL: per-arm values and widths; the qubit-by-qubit computation is not printed in reads/hold_run.txt]" [§135]

Source: an existing script and its output, not in the release: /Users/heuremen/bones-forge/parallax/darkwave_disco/internal/reads_new/park_per_qubit.py (sha256 a73b56e8...19a83e1, matches the hash line in its output) and /Users/heuremen/bones-forge/parallax/darkwave_disco/internal/reads_new/park_per_qubit.txt. It makes the bookkeeping for each qubit from that qubit's own nothing-done 300-us level, cut into the laid intervals, as code/readhold.py book(); widths are 100 shot resamplings (seed 20261003). Recorded in §180 (THIRD_RUNG_20260928.md line 2049).

Important: §180 records that "'0.002 per qubit' was WRONG, it is the mean over qubits"; single qubits scatter about ±0.02 inside shot widths about 0.03, with about 5% of qubits within 0.002. The paper's sentences "all three arms close to bookkeeping within 0.002 [§135]" and "within 0.002 qubit by qubit [§135]" (end of 3.3) do not match park_per_qubit.txt.

Fill values (measured minus bookkeeping, ibm_pittsburgh hold run, jobs 71-73, all three reads; mean of the three reads, width sqrt(sum w^2)/3):

| Arm | Mean over qubits | Median over qubits | Share of qubits with abs(d) <= 0.002 |
|---|---|---|---|
| parked once (2 × 150 us) | +0.0017 ± 0.0013 | −0.0010 ± 0.0017 | 0.0546 ± 0.0099 |
| alternate quarters (4 × 75 us) | +0.0020 ± 0.0015 | −0.0040 ± 0.0022 | 0.0541 ± 0.0087 |
| alternate tenths (10 × 30 us) | +0.0014 ± 0.0015 | −0.0036 ± 0.0022 | 0.0494 ± 0.0091 |

Per job, mean over readable qubits (145 / 139 / 139 readable of 156):
- parked once: +0.0008 ± 0.0022, +0.0021 ± 0.0022, +0.0022 ± 0.0022
- alternate quarters: −0.0002 ± 0.0027, +0.0040 ± 0.0029, +0.0022 ± 0.0022
- alternate tenths: +0.0022 ± 0.0027, +0.0001 ± 0.0023, +0.0019 ± 0.0026

Each qubit averaged over the three reads (137 qubits readable in all three), then across qubits: mean +0.0018 / +0.0023 / +0.0013; median +0.0001 / −0.0039 / −0.0049; quartiles [−0.0079, +0.0117] / [−0.0151, +0.0079] / [−0.0171, +0.0105]; middle per-qubit width of the three-read average 0.0151 / 0.0162 / 0.0169 (parked once / quarters / tenths). Shot width of one qubit's difference in one job: 0.0260-0.0297 [park_per_qubit.txt section 1].

Earlier printing of the same quantity: "+0.0017 +- 0.0012, quarters +0.0020 +- 0.0014, tenths +0.0014 +- 0.0014" [TRIANGLE_OF_FUCKUPS_20261002.md line 339]; the reads_new widths are 0.0013 / 0.0015 / 0.0015 (§180 prints them as (13), (15), (15)). The median-qubit version in the paper's Table 11 is reproduced by the same script ("RULER ROW", matches reads/hold_run.txt lines 21-23).

To add these to the release, park_per_qubit.py and park_per_qubit.txt are not in SHA256SUMS.txt (§180: "Release join of reads_new: on Wayfinder's go").

## 4. "[TO FILL: widths; reads/witness_run.txt prints the two circuits' values ... and no widths.]"

Status: partly.

- Existing reader reproduces the values. Command (cwd matters; exact):
  `cd /Users/heuremen/bones-forge/parallax/out/qubit_fifth_run && python3 readwitness.py`
  Output lines (run here): "parked after 20 (reads what had already gone): 0.0719 0.0576   parked after 40: 0.1287 0.1409   never ON: +0.0023 -0.0017" and "left after 60 = 0.7896; lost by 20 = 0.0719, by 40 = 0.1287; plain fading from the yardstick alone says 0.0757 and 0.1457 (a ruler row)". The reader prints no width for these four numbers (readwitness.py line 44 prints a width only for the watched-minus-neighbours-OFF level and the neighbours-ON-minus-OFF level, formula 1.2533 × std / sqrt(39 emitters)).
- Widths for the same bookkeeping comparison exist from a second existing script (not in the release): /Users/heuremen/bones-forge/parallax/darkwave_disco/internal/reads_new/park_per_qubit.txt section 2, stopwatch run 81, 34 readable emitters of 39, d = emitter level (mean of the X-hand and Y-hand circuits) minus bookkeeping (1 − q20) q40 or (1 − q40) q20 with q_t = Y^(t/60) per emitter:
  - yardstick B1 (emitter ON 60 us, neighbours in |0>): parked after 20 us mean +0.0014 ± 0.0029, median +0.0012 ± 0.0043; parked after 40 us mean +0.0048 ± 0.0040, median +0.0032 ± 0.0060.
  - yardstick A3 (neighbours running as spectators): parked after 20 us mean +0.0005 ± 0.0026, median −0.0015 ± 0.0034; parked after 40 us mean +0.0030 ± 0.0041, median −0.0001 ± 0.0047.
  - Its ruler row prints the median-emitter version over all 39: "yardstick B1 0.7896; measured 0.0648 and 0.1348; bookkeeping 0.0647 and 0.1347". The paper says 0.1346; the ledger §134 and TRIANGLE_OF_FUCKUPS_20261002.md line 326 say 0.1346; park_per_qubit.txt prints 0.1347.
- Not available: a printed width for each of the two circuits' median-emitter values (0.0719 / 0.0576 and 0.1287 / 0.1409). run81_results.npz holds the shots (data/fire/ibm_pittsburgh/run81_results.npz, 300 shots), so a width can be computed, but no existing script prints one for these circuits; none is given here.

## 5. "[TO FILL: jobs, dates, delays, and which vendor table.]" for the §31 results

Source: /Users/heuremen/bones-forge/parallax/out/witness_crowd/WITNESS_CROWD.md (ledger §31 header: "778 within-job tests, Holm-corrected"), readings.json, extract.py, zzpred.py, geo.py; /Users/heuremen/bones-forge/parallax/darkwave_disco/arxiv/run_index/RUN_INDEX.csv.

Suggested fill text:

"ibm_fez: 25 finished jobs of 2026-09-28, 16:54 to 19:41 UTC (12:54 to 15:41 EDT) [WITNESS_CROWD.md 'Where'; readings.json lists 31 ibm_fez job IDs between 16:54:57 and 19:41:19 UTC]. Waits: 5 us is in every ibm_fez run and is the matched wait; q144 lengths are also given at 10 and 20 us (waits in readings.json for q144: 0-8, 10-12, 14-16, 20, 24, 35, 50 us). q144 was held in rooms of 0, 1, 2, 8, 10 and 77 other qubits (23 jobs); q143 0, 1, 8, 77; q138 1, 10, 77; q113 and q72 and q27 2 and 77 (pairs 5 minutes apart for q143, 12 for q138, 6 for q113 and q27 [WITNESS_CROWD.md 'Confounded']). Rigetti Cepheus-1-108Q: 246 tasks, 2026-09-28 23:41 UTC to 2026-09-29 01:57 UTC (19:41 to 21:57 EDT on 2026-09-28) [WITNESS_CROWD.md; RUN_INDEX.csv: witness 18 + wchip 24 + wobs 24 + whead 24 + wroom 48 + walt 24 + stack 54 + edge 30 = 246, derived here]; waits 0.5, 1, 2, 3, 4/4.5, 6 and 8, 16 us; matched waits 2 and 4-4.5 us (whole-chip comparison at 3, 4.5 and 6 us). Vendor table: for ibm_fez, the static ZZ coupling per linked pair (entries zz_<a><b>) in IBM's daily calibration of 2026-09-25, the newest on disk, three days older than the jobs [WITNESS_CROWD.md 'Calibration'; geo.py line 12-15, loading ~/bones-forge/holes/cache/ibm/ibm_fez/2026-09-25.json.gz]. Rigetti: the vendor gave no ZZ or frequency table [WITNESS_CROWD.md 'Confounded']."

Facts behind each clause:
- 25 finished jobs from raw_repull/, 16:54 to 19:41 UTC [WITNESS_CROWD.md line 7]. RUN_INDEX.csv ibm_fez rows from 2026-09-28 12:54:53 to 15:41:16 EDT.
- 246 tasks: "246 tasks from standoff/raw_repull/ (every column, every shot)" [WITNESS_CROWD.md]. RUN_INDEX.csv has 278 Braket tasks between 2026-09-28 23:34 and 2026-09-29 01:57 UTC; the 32 'blink' tasks (800 shots, blink hour 23:34 to 00:27 UTC) are the difference between 278 and 246.
- Rigetti experiment families and per-family task counts, shots and times: see item 7.
- The 5-us wait is "in every Fez run, and 2 and 4 us on Rigetti" [WITNESS_CROWD.md 'The one method'].
- ZZ table: "Fez zz table is 3 days stale. Rigetti has no zz or frequency data." [WITNESS_CROWD.md 'Confounded'].
- The paper's table values: 21.7 (q143 in |1>), 25.1 (half-and-half), -5.1 (q113 with q119), -19 (q138) come from that ibm_fez table [WITNESS_CROWD.md 'Per seat (Fez)'].
- ibm_fez job ID list (31 IDs in readings.json): dat9nnbojkfs738qcd90, dat9nt3g95ks73egj77g, dat9p7dvr3kc73el5khg, dat9s7bg95ks73egjcp0, dat9s7rojkfs738qcjag, dat9sblvr3kc73el5og0, dat9skbg95ks73egjd9g, dat9sojg95ks73egjdf0, dat9ssrojkfs738qck70, dat9tulvr3kc73el5q9g, dat9urjojkfs738qcmgg, dat9vlrojkfs738qcnk0, data0erojkfs738qcoe0, data13ihcrkc73dtse70, data3dbg95ks73egjl40, data423ojkfs738qcse0, data4dbg95ks73egjm8g, data4hjojkfs738qct3g, data4ljg95ks73egjmj0, datb2grojkfs738qe8jg, datb823g95ks73egl8e0, datbagtvr3kc73el7m2g, datbddrojkfs738qel70, datc3qbojkfs738qfk30, datc4n5vr3kc73el8phg, datc545vr3kc73el8q10, datc583g95ks73egmfrg, datc5bjg95ks73egmg50, datc5eqhcrkc73dtvb80, datc5jbg95ks73egmgmg, datc5n3g95ks73egmgvg. The text says 25; the extracted file lists 31 distinct IDs (not reconciled in any file).
- Not recoverable: which 25 of the 31; the files do not say.

## 6. "[TO FILL: the model, and the code that produced reads/stopwatch_triangle.json]"

Where the code is: not on disk as a file. It is a heredoc in the working session that wrote the file at 2026-10-02 12:36 EDT (file mtime), preserved in the session transcript /Users/heuremen/.claude/projects/-Users-heuremen/ee23053e-3f85-4ed1-a9bd-3a143716d4e1.jsonl, line 7579 (tool call timestamp 2026-10-02T16:36:40Z). I extracted it to /tmp/sw_code.py with only the output path changed and ran it from /Users/heuremen/bones-forge/parallax/out/qubit_fifth_run: `python3 /tmp/sw_code.py`. The JSON it wrote matches reads/stopwatch_triangle.json exactly (all 66 values of the three remainder arrays and the three kick arrays; maximum absolute difference 0.0; same `good` list). Exact printed output:

```
clocks used 66 | emitter fading time: middle 241 us, quarter points 170 305
RULER = ours     60-us arm: measured minus predicted, middle clock  +1.69 deg +- 4.60   |remainder| middle 20.2   kick per push middle -3.22 deg   turning rate middle 1.451 deg/us
      hand length kept, measured over predicted: 20 us 0.967   40 us 0.968   60 us 0.902 +- 0.033   (predicted kept by the ruler alone: 1.000 1.000 1.000)
RULER = emitter  60-us arm: measured minus predicted, middle clock  -1.42 deg +- 4.84   |remainder| middle 20.4   kick per push middle -0.03 deg   turning rate middle 1.624 deg/us
      hand length kept, measured over predicted: 20 us 1.000   40 us 0.979   60 us 1.019 +- 0.035   (predicted kept by the ruler alone: 0.978 0.992 0.921)
RULER = chip     60-us arm: measured minus predicted, middle clock  -0.68 deg +- 4.64   |remainder| middle 19.8   kick per push middle -0.11 deg   turning rate middle 1.614 deg/us
      hand length kept, measured over predicted: 20 us 0.988   40 us 0.975   60 us 0.998 +- 0.033   (predicted kept by the ruler alone: 0.978 0.992 0.920)
BY THIRDS OF THE EMITTER'S OWN FADING (fast -> slow): emitter fading time | 60-us remainder under its own fading | under the chip middle
     161 us |  -9.56 deg |  -5.83 deg   (22 clocks)
     241 us |  +7.04 deg |  +7.28 deg   (22 clocks)
     349 us |  -1.19 deg |  -1.84 deg   (22 clocks)
```

These match the paper: -1.4 ± 4.8 deg (emitter), hand 1.02 ± 0.035 (emitter) and 0.90 ± 0.03 (ours), kick -3.2 deg per X gate (ours), -0.03 (emitter); 66 spectators.

The model, as the code states it (suggested fill text):

"For each of the 66 spectators with a readable hand (hand length above 0.15 with the emitter off, and cloud separation above 3 widths for both the spectator and its emitter; run 81, ibm_pittsburgh), the spectator's expected hand after an emitter event is the average of exp(i ω t_on) over the time t_on its emitter spends in |1>. The emitter leaves |1> after an exponentially distributed time with mean τ, truncated at the interval; ω is a constant turning rate while the emitter is in |1>. For the arm 'parked after T1 us' (T1 = 20 or 40), E = exp(−T1/τ) exp(iωT1) + I(ω,τ,T1) G(ω,τ,60−T1), where I(ω,τ,T) = (1/τ)(1 − exp(−cT))/c with c = 1/τ − iω, and G(ω,τ,T) = I(ω,τ,T) + exp(−T/τ) exp(iωT): an emitter that fell before T1 is put back in |1> by the X gate and falls again for the remaining 60 − T1 us. For the 60-us arm, E = G(ω,τ,60). The 60-us arm is held out. ω (grid of 3201 values from −0.08 to +0.08 rad/us) and a phase step at the X gate (the code takes half the residual phase of the 20-us arm) are fixed from the 20-us and 40-us arms (angles relative to the emitter-off arm); the predicted angle of the 60-us arm is that step plus arg E; the remainder is measured minus predicted (deg), reported as the median over spectators, with width the standard deviation of 150 shot resamplings of the median. The three rulers differ only in τ: 'ours' τ = infinity (the laid time), 'emitter' τ = −60/ln(q60) with q60 the neighbours-off 60-us survival of that spectator's own emitter (middle 241 us, quarter points 170 and 305), 'chip' τ = −60/ln(median q60 over the 39 emitters); q60 is clipped to [0.3, 0.999]. The hand-length ratio is the measured |hand(60)/hand(0)| over the model's |E(ω,τ,60)|."

Code (verbatim from the transcript; the only change from what ran is that the output path is the original `data/reads/stopwatch_triangle.json`; run from /Users/heuremen/bones-forge/parallax/out/qubit_fifth_run):

```python
import json, numpy as np, warnings
warnings.filterwarnings('ignore')
D='data/fire/ibm_pittsburgh'; z=np.load(f'{D}/run81_results.npz'); RO=json.load(open('data/reads/witness_roles.json'))
EM=RO['emitters']; WOF={int(k):v for k,v in RO['witness_of'].items()}; W=sorted(WOF); FAR=RO['far']
L=lambda k: np.asarray(z[f'{k}__L1']).astype(complex)
m0=L('F0').mean(0); d=L('F1').mean(0)-m0; al=lambda x: np.real((x-m0)*np.conj(d))/np.abs(d)**2
sep=np.abs(d)/np.sqrt((np.abs(L('F0')-m0)**2).mean(0)/2)
P={k: al(L(k)) for k in [f'A{a}|{h}' for a in range(4) for h in 'XY']+['B1','B2']}
def hands(P): return {a: (2*P[f'A{a}|X'].mean(0)-1)-1j*(2*P[f'A{a}|Y'].mean(0)-1) for a in range(4)}
q60=np.clip(P['B1'].mean(0),0.3,0.999)
def G(om,tau,T):
    if not np.isfinite(tau): return np.exp(1j*om*T)
    c=1/tau-1j*om; I=(1/tau)*(1-np.exp(-c*T))/c; return I+np.exp(-T/tau)*np.exp(1j*om*T)
def I(om,tau,T):
    c=1/tau-1j*om; return (1/tau)*(1-np.exp(-c*T))/c
def E(om,tau,k):
    if not np.isfinite(tau): return np.exp(1j*om*{1:20,2:40,3:60}[k])
    if k==3: return G(om,tau,60)
    T1={1:20,2:40}[k]; return np.exp(-T1/tau)*np.exp(1j*om*T1)+I(om,tau,T1)*G(om,tau,60-T1)
wr=lambda a: (a+np.pi)%(2*np.pi)-np.pi
OM=np.linspace(-0.08,0.08,3201)
def closure(H, taus, clocks):
    """hold out the 60-us arm: solve omega, kick from the 20- and 40-us arms; predict the 60-us arm. returns per-clock remainder (deg), omega, kick, predicted |E3|, |E1|, |E2|"""
    out=[]
    for w in clocks:
        t=taus[w]; r={a: H[a][w]/H[0][w] for a in (1,2,3)}; th={a: np.angle(r[a]) for a in (1,2,3)}
        a1=np.angle(E(OM,t,1)); a2=np.angle(E(OM,t,2)); res=np.abs(wr((a2-a1)-(th[2]-th[1])))
        i=np.argmin(res+1e-9*np.abs(OM)); om=OM[i]; ph=wr(th[1]-a1[i])/2
        pred=ph+np.angle(E(om,t,3)); out.append((np.degrees(wr(th[3]-pred)), om, np.degrees(ph), abs(E(om,t,3)), abs(E(om,t,1)), abs(E(om,t,2)), abs(r[1]), abs(r[2]), abs(r[3]), res[i]))
    return np.array(out)
H=hands(P)
good=[w for w in W if abs(H[0][w])>0.15 and sep[w]>3 and sep[WOF[w]]>3]
tau_e={w: -60/np.log(q60[WOF[w]]) for w in W}; tau_chip=-60/np.log(np.median(q60[EM])); tau_c={w: tau_chip for w in W}; tau_o={w: np.inf for w in W}
print('clocks used',len(good),'| emitter fading time: middle %.0f us, quarter points %.0f %.0f'%(np.median([tau_e[w] for w in good]),np.percentile([tau_e[w] for w in good],25),np.percentile([tau_e[w] for w in good],75)))
rng=np.random.default_rng(7); B=150; boot={n:[] for n in ('ours','emitter','chip')}
res={}
for name,tt in (('ours',tau_o),('emitter',tau_e),('chip',tau_c)):
    C=closure(H,tt,good); res[name]=C
    for _ in range(B):
        Pb={k:v[rng.integers(0,v.shape[0],v.shape[0])] for k,v in P.items()}; Cb=closure(hands(Pb),tt,good); boot[name].append((np.median(Cb[:,0]),np.median(Cb[:,8]/Cb[:,3]) ))
for name in ('ours','emitter','chip'):
    C=res[name]; b=np.array(boot[name])
    print(f"RULER = {name:<8} 60-us arm: measured minus predicted, middle clock {np.median(C[:,0]):+6.2f} deg +- {b[:,0].std():.2f}   |remainder| middle {np.median(np.abs(C[:,0])):.1f}   kick per push middle {np.median(C[:,2]):+.2f} deg   turning rate middle {np.degrees(np.median(np.abs(C[:,1]))):.3f} deg/us")
    print(f"      hand length kept, measured over predicted: 20 us {np.median(C[:,6]/C[:,4]):.3f}   40 us {np.median(C[:,7]/C[:,5]):.3f}   60 us {np.median(C[:,8]/C[:,3]):.3f} +- {b[:,1].std():.3f}   (predicted kept by the ruler alone: {np.median(C[:,4]):.3f} {np.median(C[:,5]):.3f} {np.median(C[:,3]):.3f})")
# per-emitter edge: does each witness follow ITS OWN emitter's fading? 60-us remainder under own vs under a neighbour emitter's fading (other ruler, not a shuffle)
Ce=res['emitter']; Cc=res['chip']
te=np.array([tau_e[w] for w in good]); o=np.argsort(te); th=np.array_split(o,3)
print('BY THIRDS OF THE EMITTER\'S OWN FADING (fast -> slow): emitter fading time | 60-us remainder under its own fading | under the chip middle')
for t in th: print('   %5.0f us | %+6.2f deg | %+6.2f deg   (%d clocks)'%(np.median(te[t]),np.median(Ce[t,0]),np.median(Cc[t,0]),len(t)))
json.dump({'good':good,'remainder_deg':{n:res[n][:,0].tolist() for n in res},'kick_deg':{n:res[n][:,2].tolist() for n in res}}, open('data/reads/stopwatch_triangle.json','w'))```

Release status: reads/stopwatch_triangle.json is in SHA256SUMS.txt (8a0c9705...f990e); this code is not in code/.

## 7. "[TO FILL: task counts and dates for each Rigetti result.]"

Source: /Users/heuremen/bones-forge/parallax/darkwave_disco/arxiv/run_index/RUN_INDEX.csv (Braket times are UTC; EDT is derived by subtracting 4 h), scripts /Users/heuremen/bones-forge/standoff/witness*.py, task files /Users/heuremen/bones-forge/standoff/chip/<name>_tasks.json. The experiment name for each § was matched by the ledger's dollar figure: the index count of tasks × (0.30 + 0.000425 × shots) equals the ledger's figure in every case (20.70, 27.60, 27.60, 25.05, 50.10, 32.70). All tasks COMPLETED. Device Cepheus-1-108Q.

| Result in paper | Ledger | Index experiment (script) | Tasks × shots | Created (UTC) | EDT (derived) | Waits (us) |
|---|---|---|---|---|---|---|
| q0 driven to level 2, q9 / q1 clocks, q10 control | §7 ($20.70) | witness (witness.py) | 18 × 2000 | 2026-09-28 23:41:52-23:42:01 | 2026-09-28 19:41 | 4, 8, 16 |
| Earlier whole-chip run, 105 other spectators; q9 fall time 14.8 ± 5.3 us vs q0 readout 31.2 us | §10 ($27.60) | wchip (witness_chip.py) | 24 × 2000 | 2026-09-29 00:45:58-00:46:15 | 2026-09-28 20:45 | 0.5, 1, 2, 3, 4, 6 |
| Neighbours q1 / q9 respond to q0 state (1.8 / 1.9 and 10.5 / 22.4 times noise); far qubits q43, q45, q5, q35 respond to the drive pulse | §11 ($27.60) | wobs (witness_obs.py) | 24 × 2000 | 2026-09-29 00:51:04-00:51:18 | 2026-09-28 20:51 | 2, 4 |
| q9 the only spectator: pull −62.1 ± 0.6 deg/us, spread 16 kHz, fall time 20.9 us (16.5-29.5) vs 24.2 us | §11 ($25.05) | whead (witness_headline.py) | 24 tasks: 12 × 1000 (emitter at rest) + 12 × 2500 (emitter pushed) | 2026-09-29 00:58:59-00:59:09 | 2026-09-28 20:58 | 0.5, 1, 2, 3, 4.5, 6 |
| 0, 54 or 106 other spectators (rooms) | §12 ($50.10) | wroom (witness_room.py), with whead as the 0-spectator room | 48 tasks: 24 × 1000 + 24 × 2500 | 2026-09-29 01:26:59-01:27:26 | 2026-09-28 21:26 | 0.5, 1, 2, 3, 4.5, 6 |
| Alternating alone / full, two rounds (the 26.6 / 31.2 us pair) | §12 ($32.70) | walt (witness_alt.py) | 24 × 2500 | 2026-09-29 01:29:50-01:30:04 | 2026-09-28 21:29 | 0.5, 1, 2, 3, 4.5, 6 |

- §12's "0 / 54 / 106 others" rooms: 0 = whead; 54 (HALF) and 106 (FULL) = wroom [witness_room.py docstring: "HALF = every other qubit also a clock; FULL = every qubit a clock. With tonight's ALONE run (witness_headline.py) that is three points"].
- The paper sentence also cites §10, §11, §12 only; §7's fall-time numbers (chi-square 8.6 / 11.8 / 6.2 for six numbers; 4.295 and 4.631 GHz) come from the witness task family (18 tasks).
- Waits column from witness_*.py (WAITS) and readings.json families.
- Sum check against item 5: 18 + 24 + 24 + 24 + 48 + 24 + 54 (stack) + 30 (edge) = 246.
- Not recoverable from files: the ledger does not name the experiment (witness, wchip, ...) for each § entry; the pairing above rests on the matching dollar figures and script docstrings.

## 8. "[TO FILL: the two variables, and what the mirror check is]" [§5]

The two variables: the qubit's |2> (rung 2) population at the start of a shot, from the per-qubit fit of the eight-sequence shuffle (p2; sequences e, a, b, ab, ba, aba, bb, bab, 5000 shots each, where a flips |0>/|1> and b swaps |1>/|2>), and the same qubit's calibration readout fidelity from Rigetti's published properties (cepheus_props_20260928.json, column 3). The statistic is Spearman rank correlation [rigetti_chip.py analyze(), line 135; /Users/heuremen/bones-forge/standoff/rigetti_chip.py, also in the release as code_20261004/rigetti_chip.py].

Numbers (printed outputs, from the session transcript of 2026-09-28; session file /Users/heuremen/.claude/projects/-Users-heuremen/cdaa0097-9c26-4161-a8f4-92b4a70e0f85.jsonl, lines 14514 and 14520):
- Before the mirror check: "robust subset (no bound hits, swap > 0.75, fit cost < 20 for 2 spare numbers): 81 qubits ... rung 2 vs readout fidelity: rho -0.55 (p 1e-07, n 81)" (and vs T1: rho -0.26, p 0.019, n 81).
- After the mirror check: "81 clean-fit qubits: 56 have ONE answer for rung 2 (mirror excluded), 25 are AMBIGUOUS (readout and rung 2 can trade places) ... UNAMBIGUOUS qubits only: rung 2 vs readout fidelity rho -0.31 (p 0.021, n 56) ... unambiguous median rung 2 0.04%; above 1%: 4"; top unambiguous holders (24, '2.05%', 0.944), (48, '1.34%', 0.956), (40, '1.26%', 0.932), (33, '1.17%', 0.913).

The shuffle model has six parameters x = [p1, p2, r0, m1, m2, eta]: populations of levels 1 and 2 at the start, the probabilities that a qubit in level 0, 1 or 2 reads 0, and the swap fidelity eta [rigetti_gamble.py model()]. The mirror check fits each of the 81 qubits again from 24 starting points (six starting values of p2, 0.0005 to 0.1, crossed with four starting values of m2, 0.01 to 0.2), so that solutions on both sides of the exchange between p2 and m2 (level-2 population against how a level-2 qubit reads) are searched. Every solution whose fit cost is within 1.0 of the best is kept as equally good; a qubit is AMBIGUOUS if the kept solutions' rung-2 values span more than 0.005 (0.5 percentage points), and the correlation is recomputed on the unambiguous qubits using the lowest kept rung-2 value. The ledger's gloss: "readout blur and rung 2 can trade places" and "part of it was the ruler" [§5].

Suggested fill text: "The two variables are each qubit's |2> population at the start of a shot (from a fit to eight flip/swap sequences) and its calibrated readout fidelity [rigetti_chip.py analyze()]. The mirror check refits each qubit's eight sequences from 24 starting points, on both sides of the exchange between |2> population and the probability that a |2> qubit reads 0, and counts a qubit as ambiguous when equally good fits (cost within 1.0 of the best) span more than 0.5 percentage points of |2> population: 25 of the 81 clean-fit qubits are ambiguous and 56 are not."

Code location: not on disk as a script (/Users/heuremen/bones-forge/parallax/out/discards/DISCARD_MAP.md line 79 lists "mirror_check's 14 missing seats (no script)"). The code is a heredoc in the transcript (cdaa0097-..., line 14519, 2026-09-28T22:54:13Z). Output file: /Users/heuremen/bones-forge/standoff/chip/mirror_check.json (rows [q, lowest kept p2, highest kept p2, readout fidelity]; 81 rows). Verbatim code:

```python
import json, math, numpy as np
from scipy.stats import spearmanr
import rigetti_gamble as G
from scipy.optimize import least_squares
Z = dict(np.load('chip/run.npz')); QS = sorted(int(r[0]) for r in json.load(open('cepheus_props_20260928.json'))); R = {r['q']: r for r in json.load(open('chip/chip_rows.json'))}
S = G.SEQS; res = []
for k, q in enumerate(QS):
    r = R[q]
    if not (r['pushed'] and r['p2'] == r['p2'] and r['p2'] < 0.29 and r['p1'] < 0.29 and r['eta'] > 0.75 and r['fitq'] < 20): continue
    y = {s: 1 - Z[json.dumps(['shuffle', s])][:, k].mean() for s in S}; n = {s: Z[json.dumps(['shuffle', s])].shape[0] for s in S}
    resid = lambda x: [(G.model(x, s if s != 'e' else '') - y[s]) / math.sqrt(max(y[s] * (1 - y[s]), 1e-4) / n[s]) for s in S]
    sols = []
    for p2g in (0.0005, 0.003, 0.01, 0.03, 0.06, 0.1):          # search both sides of the mirror
        for m2g in (0.01, 0.04, 0.1, 0.2):
            f = least_squares(resid, [0.05, p2g, 0.95, 0.02, m2g, 0.95], bounds=([0, 0, 0.6, 0, 0, 0.7], [0.3, 0.3, 1, 0.3, 0.5, 1]))
            sols.append((f.cost, f.x[1], f.x[4]))
    best = min(c for c, *_ in sols)
    near = [(p2, m2) for c, p2, m2 in sols if c < best + 1.0]         # every solution within ~1 unit of the best: equally good
    lo, hi = min(p for p, _ in near), max(p for p, _ in near)
    res.append((q, lo, hi, r['readout']))
amb = [x for x in res if x[2] - x[1] > 0.005]; clean = [x for x in res if x[2] - x[1] <= 0.005]
print(f"{len(res)} clean-fit qubits: {len(clean)} have ONE answer for rung 2 (mirror excluded), {len(amb)} are AMBIGUOUS (readout and rung 2 can trade places)")
print('   ambiguous, with their readout:', [(q, f'{lo:.1%}-{hi:.1%}', round(ro, 3)) for q, lo, hi, ro in sorted(amb, key=lambda x: x[3])][:12])
if len(clean) > 5:
    rho, pv = spearmanr([x[3] for x in clean], [x[1] for x in clean]); print(f"   UNAMBIGUOUS qubits only: rung 2 vs readout fidelity rho {rho:+.2f} (p {pv:.2g}, n {len(clean)})")
    top = sorted(clean, key=lambda x: -x[1])[:8]; print('   unambiguous rung-2 holders:', [(q, f'{lo:.2%}', round(ro, 3)) for q, lo, hi, ro in top])
    print(f"   unambiguous median rung 2 {np.median([x[1] for x in clean]):.2%}; above 1%: {sum(1 for x in clean if x[1] > 0.01)}")
json.dump(res, open('chip/mirror_check.json', 'w'), indent=1, default=float)
```

Not recoverable: why 14 of the 95 pushed qubits are not among the 81 rows other than the filter in the code (pushed, p2 < 0.29, p1 < 0.29, eta > 0.75, fit cost < 20); the DISCARD_MAP says 12 seats never got a rung-2 push.

## 9. "[TO FILL: job list, shots, inter-shot gaps, and the cloud-exclusion threshold]" [§2, §22]

The §2 counts come from the parallax run's J1 jobs, the only jobs of that run with two readouts per shot (circuits D0 = measure, measure; D1 = X, measure, measure), on three chips, 78 even-numbered qubits each, 4000 shots per circuit [parallax_ibm.py docstring and plan; /Users/heuremen/bones-forge/parallax/out/<stamp>/meta.json]:

| Chip | J1 job ID | Run (EDT) | Folder |
|---|---|---|---|
| ibm_marrakesh | dat5rslvr3kc73el0klg | 2026-09-28 08:30:44 (running start, 12:30:44Z) | out/20260928_083041 |
| ibm_kingston | dat9ebbg95ks73egis2g | 2026-09-28 12:34:55 (16:34:55Z) | out/20260928_123452 |
| ibm_fez | dat9o2ihcrkc73dts3jg | 2026-09-28 12:55:40 (16:55:40Z) | out/20260928_125537 |

- Circuits per J1 job: P0, P1 (one readout), D0, D1 (two readouts); 4000 shots each; kerneled readout (one complex point per qubit per shot).
- Inter-shot gap: J1 used the backend default repetition delay, 250 us on all three chips (default_rep_delay 0.00025 s, range 0-2 ms) [/Users/heuremen/bones-forge/parallax/out/discards/ibm_backend_config.json; DISCARD_MAP.md lines 160, 201: "rep_delay default recorded as null. The value used (250 us) is only in the chip config"]. The same run's other jobs, one readout each: J2 20 us (2000 shots, P0, P1), J3 1 ms (2000 shots), J4 default again (2000 shots). Job IDs J2-J4: Marrakesh dat5rsqhcrkc73dtn700 / dat5rt3g95ks73egea00 / dat5rt3ojkfs738q7gf0; Kingston dat9eblvr3kc73el57fg / dat9ebtvr3kc73el57gg / dat9ec3ojkfs738qc24g; Fez dat9o2tvr3kc73el5j20 / dat9o33ojkfs738qcdu0 / dat9o33g95ks73egj7fg. The carried values by gap (item 10) come from J1/J2/J3 [Biblioteca, /Users/heuremen/bones-forge/gridsong/biblioteca.md lines 7598-7607].
- Cloud-exclusion threshold: "dots 'neither' on BOTH looks ... cut = >4 widths from both clouds, checked on half the refs" [biblioteca.md line 7598, entry "19:xx THE THIRD PLACE AT THE START, from existing data"]; "§2: 'neither cloud' = more than 4 widths from both, cut checked on half the references. ON DISK (J1-J4)" [DISCARD_MAP.md line 479]. Counts as recorded there: Marrakesh told 0: 134 vs 6.5 by chance, told 1: 100 vs 16; Kingston 98 vs 2 and 109 vs 10; Fez about none.
- Different cut in the same files: DISCARD_MAP.md line 199 gives 'off both clouds' = beyond 5 widths for the echo analysis (a different analysis, Marrakesh 12:27 EDT echo run), and PARALLAX_RESULTS.md in each folder prints "prepared 1, off both clouds 0.0000" (median over qubits) with its own geometry; those do not produce 134 / 98.
- Not recoverable: a script that prints 134 vs 6.5 and 98 vs 2 (and the chance values 6.5 and 2). It is not in out/20260928_*/ or the release; /Users/heuremen/bones-forge/parallax/out/ledger/LOOK_LEDGER.md entry P16 and PASS_A_OBSERVER.md B-entries list the claim without a script. The paper's window "2026-09-24 to 09-28": §2 names only the parallax run ("3 fridges") for these counts; the 17 IBM jobs of 9/24 (RUN_INDEX.csv; NOTHING_SWEEP_sep24_27.md) are not named in §2.

## 10. "[TO FILL: labels and values]" for the two ibm_kingston "carried" qubits [§5]

Labels: ibm_kingston q58 and q62. §5 lists "standing / carried / blinking third place on IBM (Marrakesh 14,24 / Kingston 58,62, Marrakesh 26 / Marrakesh 60,126)" [THIRD_RUNG_20260928.md line 43-44].

Values (share of shots outside both clouds at the start of a shot, at 20-us gaps; at 1-ms gaps):
- q58: 1.6% rising to 6.1% at 20-us gaps; 0.8% at 1 ms.
- q62: 2.3% rising to 9.4% at 20-us gaps; 0.5% at 1 ms; drains in roughly 150-200 us [§2: "Kingston 62: 2.3% -> 9.4% of shots with 20 us gaps, ~0.5% with 1 ms gaps. Drains in roughly 150-200 us."].
- Source of the q58 values: "CARRIED (Kingston 58/62/40): grows 4-14x with 20 us shot gaps (58: 1.6% -> 6.1%; 62: 2.3% -> 9.4%; 40: 0.13% -> 1.85%), drains by 1 ms gaps (0.8/0.5/0.05%)" [/Users/heuremen/bones-forge/gridsong/biblioteca.md line 7601]. The entry does not name the gap of the first number of each arrow (1.6%, 2.3%).
- Third ibm_kingston qubit in the same Biblioteca entry: q40, 0.13% to 1.85%, 0.05% at 1 ms; the §5 IBM list names only q58 and q62.
- Location of q58's rest-1 population: 96% of its rest 1s about 4.5 cloud-widths short of the 1 spot and 2.6 widths off to the side; q62 57% [/Users/heuremen/bones-forge/parallax/out/open_look/LOOK2_RUNS.md line 26].
- No script on disk prints these gap-by-gap values (the ledger and Biblioteca are the records).
