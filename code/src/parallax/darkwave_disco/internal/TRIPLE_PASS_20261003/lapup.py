#!/usr/bin/env python3
"""TRIPLE PASS, seat A (the observer, LAID): lap-up arithmetic from read files and raw jobs, read-only.
Writes ONLY lapup.txt beside this script. No hardware contact. Every number names its clock:
LAID (laid time / the maker's numbers), WITNESS (a spectator), OWN (the qubit's own decay).
Sections:
  1. The two replication reads (ibm_marrakesh / ibm_kingston run 141) recomputed from the raw jobs with the frozen
     push reader's own push_stats() (code/readclose.py), widths from 100 shot resamples with its seed. No reader for
     these two reads is in the release; this is the push run's reader pointed at the same circuits.
  2. The leakage cap and the push shortfall from reads/close_push.txt lines 2, 3, 5, 6 (as 7_TRACE_FIXES item 8a).
  3. The three look ratios with shot widths and with job-scatter widths.
  4. Job-scatter widths for the look-time and give-back reads (three jobs each).
  5. The stopwatch park bookkeeping (q_t = 0.7896^(t/60)).
  6. The 9/25 Rigetti qutrit three-box B_not value (-0.019) with a binomial bootstrap width.
  7. The noname job: two-ruler gap at 2/6/10 pushes, z of each own-ruler arm, family-wise numbers.
  8. The gap-clock / level-clock ratio, Kingston Run 2, with its width; the same reader on the other chips (ledger §114).
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'lapup.txt')
SANDBOX = os.path.join(HERE, 'rerun', 'qubit_fifth_run')
REL = '/Users/heuremen/bones-forge/parallax/darkwave_disco/for_indahl_ai/data/reads'
L = []
P = L.append

# ------------------------------------------------------------------------------------------------ 1
sys.path.insert(0, SANDBOX)
import readclose as RC   # the frozen release reader (copied into the sandbox); its push_stats/resample/frame/book are used as is


def load_chip(chip, run):
    d = os.path.join(SANDBOX, 'data', 'fire', chip)
    m = json.load(open(os.path.join(d, f'run{run}_meta.json')))
    assert m.get('complete') is True
    z = np.load(os.path.join(d, f'run{run}_results.npz'))
    return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


P('== 1. REPLICATION READS FROM THE RAW JOBS (code/readclose.py push_stats, 100 shot resamples, seed 20261002 as the reader)')
for chip, label in (('ibm_marrakesh', 'rep_marrakesh_read1.txt'), ('ibm_kingston', 'rep_kingston_read1.txt')):
    RC.RNG = np.random.default_rng(20261002)
    m, A = load_chip(chip, 141)
    s = RC.push_stats(A)
    B = [RC.push_stats(RC.resample(A)) for _ in range(RC.NB)]
    w = {k: float(np.nanstd([b[k] for b in B])) for k in s if not k.startswith('_')}
    P(f'   {chip} run 141 job {m.get("job_id")} (LAID: created {m.get("job_created_at")}, running {m.get("job_running_at")}, end {m.get("end_time")}); readable bits {s["_bits"]}; shots {m.get("shots")}; compare reads/{label}')
    for k in [k for k in s if not k.startswith('_')]:
        P(f'      {k:<46} {s[k]:+.4f} +- {w[k]:.4f}')
    # bit by bit (hole-check lines)
    al, sep = RC.frame(A, 'OFF|p0__L1', 'ON|p0__L1'); g = sep > 4
    lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    q = np.clip(lv['ON|n300'], 0.02, 0.98) ** 0.1
    dO = (lv['OFF|s10'] - RC.book(np.zeros_like(q), q, 10))[g]
    dN = (lv['ON|s10'] - RC.book(np.ones_like(q), q, 10))[g]
    P(f'      bit by bit OFF s10: mean {dO.mean():+.4f} median {np.median(dO):+.4f} share>0 {np.mean(dO > 0):.2f} | ON s10: mean {dN.mean():+.4f} median {np.median(dN):+.4f} share>0 {np.mean(dN > 0):.2f}')

# ------------------------------------------------------------------------------------------------ 2
P('')
P('== 2. THE PUSH SHORTFALL AND THE COUNT-GROWING CAP, from reads/close_push.txt lines 2, 3, 5, 6 (three jobs, LAID gate counts)')
o2, so2 = 0.0019, 0.0006; o10, so10 = 0.0229, 0.0007; u2, su2 = 0.0020, 0.0007; u10, su10 = 0.0232, 0.0008


def solve(o2, o10, u2, u10):
    # o_N + |u_N| = 2 sin^2(N e / 2) + (N/2) k   for N = 2, 10 ; solve e (rad) and k
    s2 = o2 + u2; s10 = o10 + u10
    def f(e): return (s10 - 2 * math.sin(10 * e / 2) ** 2) - 5 * (s2 - 2 * math.sin(2 * e / 2) ** 2)
    lo, hi = 1e-6, 0.2
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0: hi = mid
        else: lo = mid
    e = (lo + hi) / 2
    k = s2 - 2 * math.sin(e) ** 2
    return math.degrees(e), k
e0, k0 = solve(o2, o10, u2, u10)
rng = np.random.default_rng(1)
E, K = [], []
for _ in range(20000):
    e, k = solve(rng.normal(o2, so2), rng.normal(o10, so10), rng.normal(u2, su2), rng.normal(u10, su10))
    E.append(e); K.append(k)
P(f'   shortfall {e0:.3f} deg (redraw sd {np.std(E):.3f}); count-growing part {100 * k0:.3f} % per push (redraw sd {100 * np.std(K):.3f}); upper edge (k + 2 sd) {100 * (k0 + 2 * np.std(K)):.3f} %')
P(f'   halfway start predicted from the shortfall alone: 2 X {math.sin(math.radians(2 * e0)) / 2:.4f}, 10 X {math.sin(math.radians(10 * e0)) / 2:.4f}  (close_push.txt:8,9 measured -0.0262, -0.1138)')

# ------------------------------------------------------------------------------------------------ 3, 4
P('')
P('== 3/4. THE LOOK: three numbers from three different firings, with shot widths and job-scatter widths')
maker = 2.180                                     # LAID: reads/maker_look_length_pittsburgh.json, 156 bits, read 11:02:53
lt9 = np.array([2.4718, 2.2802, 2.3578]); lt9w = np.array([0.0512, 0.0464, 0.0659])   # WITNESS, close_looktime.txt:6
lt3 = np.array([2.4940, 2.1654, 2.3888]); lt3w = np.array([0.1124, 0.1017, 0.1225])   # WITNESS, close_looktime.txt:2
gb = {0: [6.5260, 1.0228, 3.0449], 150: [3.4501, 1.3144, 5.9062], 270: [4.5403, 0.7272, 6.8846]}   # OWN, close_giveback.txt:2,4,6
for name, v, w in (('witness, block of 9 (close_looktime.txt:6)', lt9, lt9w), ('witness, block of 3 (close_looktime.txt:2)', lt3, lt3w)):
    mean = v.mean(); shot = math.sqrt((w ** 2).sum()) / 3; scat = v.std(ddof=1) / math.sqrt(3)
    P(f'   {name}: per job {v.round(4).tolist()} | mean {mean:.4f} | shot width {shot:.4f} | job-scatter width (sd/sqrt3) {scat:.4f} | job sd {v.std(ddof=1):.4f}')
for pos, v in gb.items():
    v = np.array(v); P(f'   give-back, look at {pos} us (close_giveback.txt): per job {v.tolist()} | mean {v.mean():.4f} | job sd {v.std(ddof=1):.3f} | job-scatter width {v.std(ddof=1) / math.sqrt(3):.3f}')
W = lt9.mean(); Ws = math.sqrt((lt9w ** 2).sum()) / 3; Wj = lt9.std(ddof=1) / math.sqrt(3)
Q = 3.5; Qs = 0.2
P(f'   witness / maker = {W / maker:.4f} +- {Ws / maker:.4f} (shot) / +- {Wj / maker:.4f} (job scatter);  12/11 = {12 / 11:.4f}')
P(f'   qubit(3.5 +- 0.2, ledger §135 only) / maker = {Q / maker:.4f} +- {Qs / maker:.4f};  phi = {(1 + 5 ** 0.5) / 2:.4f}')
P(f'   qubit / witness = {Q / W:.4f} +- {Q / W * math.sqrt((Qs / Q) ** 2 + (Ws / W) ** 2):.4f};  phi x 11/12 = {(1 + 5 ** 0.5) / 2 * 11 / 12:.4f}')
for lab, q in (('jump run per-job median range low (jump_rerack.txt:7-14, none_ON)', 3.20), ('jump run per-job high', 4.26), ('jump run bit-by-bit middle (jump_rerack.txt:16)', 3.23),
               ('tail run (tail_run.txt; ledger §121 3.63)', 3.63), ('hold run 3 looks (hold_run.txt:6, (311.5-300)/3)', (311.5 - 300) / 3), ('hold run 9 looks (hold_run.txt:7, (327.0-300)/9)', (327.0 - 300) / 9),
               ('give-back mean at 0 / 150 / 270 us', 3.5313), ('', 3.5569), ('', 4.0507)):
    P(f'      qubit clock from {lab or "  same"}: {q:.3f} us -> qubit/maker {q / maker:.3f}, qubit/witness {q / W:.3f}')

# ------------------------------------------------------------------------------------------------ 5
P('')
P('== 5. STOPWATCH PARK BOOKKEEPING (run 81, one job; yardstick 0.7896 = median emitter, neighbours OFF, witness_run.txt:19)')
Y = 0.7896; q20 = Y ** (20 / 60); q40 = Y ** (40 / 60)
P(f'   (1-q20) q40 = {(1 - q20) * q40:.5f};  (1-q40) q20 = {(1 - q40) * q20:.5f}   | measured (witness_run.txt:21, mean of the two hand circuits) {(0.0719 + 0.0576) / 2:.5f}, {(0.1287 + 0.1409) / 2:.5f}; the two circuits differ by {0.0719 - 0.0576:+.4f}, {0.1287 - 0.1409:+.4f}')

# ------------------------------------------------------------------------------------------------ 6
P('')
P('== 6. RIGETTI 9/25 QUTRIT THREE-BOX, B_not at phi (standoff/step3_results.json, step2_results.json; analysis copied from standoff/braket_round1_step3.py analyze())')
S = '/Users/heuremen/bones-forge/standoff'
R3 = json.load(open(os.path.join(S, 'step3_results.json')))['results']
S2 = json.load(open(os.path.join(S, 'step2_results.json')))['results']
cal = {r['prep']: (r['p_read1'], r['shots']) for r in S2 if r['part'] == 'A' and r['read'] == 'a'}
SC = ['psi', 'A_not', 'B_not', 'C_not']


def at_phi(R, calp):
    r0, rn = calp[0], (calp[1] + calp[2]) / 2
    corr = lambda read0: (read0 - (1 - rn)) / ((1 - r0) - (1 - rn))
    d = {}
    for r in R: d.setdefault(r['name'], {})[r['x']] = corr(1 - r['p'])
    fit = {}
    for n in SC:
        xs = np.array(sorted(d[n])); ys = np.array([d[n][x] for x in xs])
        X = np.vstack([np.ones_like(xs), np.cos(xs), np.sin(xs)]).T; c, *_ = np.linalg.lstsq(X, ys, rcond=None); fit[n] = c
    c = fit['psi']; x0 = math.atan2(c[2], c[1]); xphi = x0 - math.pi
    return {n: float(np.dot(fit[n], [1, math.cos(xphi), math.sin(xphi)])) for n in SC}, x0


base = [{'name': r['name'], 'x': r['x'], 'p': r['p_read1']} for r in R3 if r['name'] in SC]
v0, x0 = at_phi(base, {k: v[0] for k, v in cal.items()})
rng = np.random.default_rng(20261003); BS = []
for _ in range(4000):
    Rb = [{'name': r['name'], 'x': r['x'], 'p': rng.binomial(1000, r['p']) / 1000} for r in base]
    cb = {k: rng.binomial(v[1], v[0]) / v[1] for k, v in cal.items()}
    BS.append(at_phi(Rb, cb)[0])
for n in SC:
    vals = np.array([b[n] for b in BS])
    P(f'   {n:<6} at phi: {v0[n]:+.4f}  binomial bootstrap sd {vals.std():.4f}  (95% band {np.percentile(vals, 2.5):+.4f} .. {np.percentile(vals, 97.5):+.4f})  [35 tasks x 1000 shots LAID; x0 = {x0:.3f} rad]')

# ------------------------------------------------------------------------------------------------ 7
P('')
P('== 7. NO-NAME JOB (run 121, one job): own-ruler residuals (reads/noname_read1.txt), two-ruler gap, family-wise')
core = {'A30_30': (-0.0097, 0.0051, 0.0126), 'A10_30': (-0.0139, 0.0071, 0.0147), 'A90_30': (-0.0007, 0.0054, 0.0270), 'A30_10': (0.0170, 0.0064, 0.0291),
        'A30_90': (-0.0062, 0.0046, -0.0050), 'A30_30f': (0.0091, 0.0052, -0.0133), 'B30_30': (-0.0021, 0.0046, -0.0022), 'B30_30f': (0.0014, 0.0046, 0.0015),
        'N2': (-0.0012, 0.0034, 0.0245), 'N6': (-0.0058, 0.0052, 0.0207)}
from math import erf, sqrt
pz = lambda z: 1 - erf(abs(z) / sqrt(2))
for k, (own, w, one) in core.items():
    P(f'   {k:<8} own {own:+.4f} +- {w:.4f}  z {own / w:+.2f}  | one-clock {one:+.4f} | one minus own {one - own:+.4f}')
z = 0.0170 / 0.0064; p = pz(z)
P(f'   A30_10: z {z:.3f}, two-sided p {p:.4f}, Sidak over 10 {1 - (1 - p) ** 10:.4f}, Bonferroni {min(1, 10 * p):.4f}; at z rounded 2.66: Sidak {1 - (1 - pz(2.66)) ** 10:.4f}')
P(f'   arms beyond 2 widths among the 10: {[k for k, v in core.items() if abs(v[0] / v[1]) > 2]}; beyond 1.9: {[k for k, v in core.items() if abs(v[0] / v[1]) > 1.9]}')
P('   other printed quantities of the same job beyond 2 widths (read lines): A30_30 off-both +0.0025(0.0008) z 3.1; B30_30f off-both +0.0020(0.0008) z 2.5;'
  ' A30_90 off-both +0.0019(0.0008) z 2.4; B30_30f across +0.0023(0.0011) z 2.1; emitters started OFF -0.0216(0.0102) z -2.1; witness hand X, started ON, measured minus model 3.3 widths')

# ------------------------------------------------------------------------------------------------ 8
P('')
P('== 8. GAP CLOCK / LEVEL CLOCK (one look then a wait; out/qubit_three_runs/data/reads/run12_kingston.txt:227,236)')
g, gw, lv_, lw = 157.2, 16.95, 261.6, 7.783
r = g / lv_; rw = r * math.sqrt((gw / g) ** 2 + (lw / lv_) ** 2)
P(f'   Kingston Run 2 (one job, 9 bits): {g} +- {gw} / {lv_} +- {lw} = {r:.3f} +- {rw:.3f}; 1/ratio = {1 / r:.3f} +- {rw / r ** 2:.3f}')
P('   same reader, other jobs (ledger §113-§116): Phoenix 0.68 +- 0.07, Marrakesh run 5 0.61 +- 0.08, Pittsburgh run 9 0.66 +- 0.10, Boston 0.80 +- 0.11, Pittsburgh run 2 0.83 +- 0.11')

open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
