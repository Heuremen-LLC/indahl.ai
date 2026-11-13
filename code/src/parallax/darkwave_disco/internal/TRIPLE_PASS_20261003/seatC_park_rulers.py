#!/usr/bin/env python3
"""park_rulers.py -- TRIPLE PASS seat C. Read-only. THE PARK (a |1>-prepared qubit pushed to |0> for alternate stretches) with the decay ruler moved.
Hold runs 71-73 (P1 2x150 us, P3 4x75 us, P9 10x30 us LAID; start ON; X after each stretch) and stopwatch run 81 (39 emitters ON 20 / 40 us LAID,
then X to |0> for the rest of a 60-us LAID window). Claimed ruler [OWN]: one exponential from the same job's nothing-done arm, clip 0.02-0.98,
mean over readable qubits (reads_new/park_per_qubit.py). Moved:
  clip-free     -- the same, without the qubits whose nothing-done level sits at the clip (P300 <= 0.02);
  typ           -- the same over qubits with P300 in (0.1, 0.9);
  FOREIGN shape -- run 121's chip-wide two-part decay shape (fast fraction f, fast clock Tf, fitted there; this job's own P300 per qubit sets
                   the slow clock), booked three ways: own-smooth (the fast part at every entry into |1>), mix (T1-fluctuation: per-shot
                   fixed clock), once (the fast part only at the shot's first excitation). Cross-job, flagged.
Writes only seatC_park_rulers.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
ROLES = json.load(open('/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/witness_roles.json'))
OUT = os.path.join(HERE, 'seatC_park_rulers.txt'); NB = 100
F, TF = 0.020, 20.0          # run 121's fitted chip-wide shape (seatC_crossing_rulers.py / seatC_crossing_rulers3.py): f 0.020 (0.008), Tf 20 (11) us


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(r):
    z = np.load(os.path.join(D, f'run{r}_results.npz')); m = json.load(open(os.path.join(D, f'run{r}_meta.json')))
    return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


def frame(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)


def chain(start, qs):
    on = np.asarray(start, float) * 1.0; off = 1 - on
    for q in qs: on, off = off + on * (1 - q), on * q
    return on


def curves(p300):
    es = np.clip((p300 - F * np.exp(-300 / TF)) / (1 - F), 1e-4, 0.9999)
    smooth = lambda L: np.clip((1 - F) * es ** (L / 300) + F * np.exp(-L / TF), 0.001, 0.9999)
    slow = lambda L: es ** (L / 300); fast = lambda L: np.full(len(p300), np.exp(-L / TF))
    return smooth, slow, fast


def hold_stats(A):
    al, sep = frame(A, 'OFF|w0__L1', 'ON|w0__L1'); g = sep > 4
    lv = {a: al(A[f'ON|{a}__L1']).mean(0) for a in ('N0', 'P1', 'P3', 'P9')}
    p = lv['N0']; pc = np.clip(p, 0.02, 0.98); n = len(p); one = np.ones(n)
    clipfree = g & (p > 0.02); typ = g & (p > 0.1) & (p < 0.9)
    smooth, slow, fast = curves(np.clip(p, 1e-4, 0.9999)); out = {}
    for a, nseg in (('P1', 2), ('P3', 4), ('P9', 10)):
        L = 300 / nseg
        b_one = chain(one, [pc ** (1 / nseg)] * nseg)
        d = lv[a] - b_one
        out[f'{a} one-clock | mean readable (claimed)'] = d[g].mean(); out[f'{a} one-clock | clip-free'] = d[clipfree].mean(); out[f'{a} one-clock | typ'] = d[typ].mean()
        b_own = chain(one, [smooth(L)] * nseg)
        b_mix = (1 - F) * chain(one, [slow(L)] * nseg) + F * chain(one, [fast(L)] * nseg)
        b_once = (1 - F) * chain(one, [slow(L)] * nseg)  # ON start: fast loss once at t = 0 goes to |0>, the rest on the slow clock
        b_once = b_once + chain(np.zeros(n), [slow(L)] * nseg) * F  # the lost part, now in |0>, follows the chain from |0>
        for nm, b in (('own-smooth', b_own), ('mix', b_mix), ('once', b_once)):
            out[f'{a} FOREIGN {nm} | clip-free'] = (lv[a] - b)[clipfree].mean(); out[f'{a} FOREIGN {nm} | typ'] = (lv[a] - b)[typ].mean()
    out['_n'] = int(g.sum()); out['_nclip'] = int((g & ~clipfree).sum())
    return out


def stop_stats(A):
    EM = ROLES['emitters']; al, sep = frame(A, 'F0__L1', 'F1__L1')
    lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    gE = np.zeros(len(sep), bool); gE[EM] = True; gE &= sep > 4
    Y = lv['B1']; yc = np.clip(Y, 0.02, 0.98); clipfree = gE & (Y > 0.02)
    meas = {20: (lv['A1|X'] + lv['A1|Y']) / 2, 40: (lv['A2|X'] + lv['A2|Y']) / 2}
    out = {}
    # 60-us yardstick Y; as a 300-us-equivalent level for the shape: P300 = Y^5
    smooth, slow, fast = curves(np.clip(Y, 1e-4, 0.9999) ** 5)
    for t in (20, 40):
        b_one = (1 - yc ** (t / 60)) * yc ** ((60 - t) / 60)
        out[f'parked after {t} us, one-clock | mean readable emitters (claimed)'] = (meas[t] - b_one)[gE].mean()
        out[f'parked after {t} us, one-clock | clip-free'] = (meas[t] - b_one)[clipfree].mean()
        b_own = (1 - smooth(t)) * smooth(60 - t)
        b_mix = (1 - F) * (1 - slow(t)) * slow(60 - t) + F * (1 - fast(t)) * fast(60 - t)
        out[f'parked after {t} us, FOREIGN own-smooth | clip-free'] = (meas[t] - b_own)[clipfree].mean()
        out[f'parked after {t} us, FOREIGN mix | clip-free'] = (meas[t] - b_mix)[clipfree].mean()
    out['_n'] = int(gE.sum()); out['_nclip'] = int((gE & ~clipfree).sum())
    return out


def boot(fn, A, rng):
    B = []
    for _ in range(NB):
        idx = {}; R = {}
        for k, v in A.items():
            b = k.split('__')[0]
            if b not in idx: idx[b] = rng.integers(0, v.shape[0], v.shape[0])
            R[k] = v[idx[b]]
        B.append(fn(R))
    return {k: np.std([b[k] for b in B]) for k in B[0] if not k.startswith('_')}


L = []; P = L.append; P(f'# script sha256 {sha(os.path.abspath(__file__))}')
rng = np.random.default_rng(20261003)
per = []
for r in (71, 72, 73):
    m, A = load(r); s = hold_stats(A); w = boot(hold_stats, A, rng); per.append((s, w)); P(f'# run {r} job {m["job_id"]} results sha256 {sha(os.path.join(D, f"run{r}_results.npz"))}')
P(''); P('== HOLD RUN PARK (runs 71-73), start ON, 300 us LAID; residual = measured minus book [OWN], %; readable ' + '/'.join(str(s['_n']) for s, _ in per) + '; clip-bound ' + '/'.join(str(s['_nclip']) for s, _ in per))
for k in per[0][0]:
    if k.startswith('_'): continue
    v = np.array([s[k] for s, _ in per]); w = np.array([x[k] for _, x in per])
    P(f'   {k:<48} ' + '  '.join(f'{100 * a:+.2f}({100 * b:.2f})' for a, b in zip(v, w)) + f'  | all {100 * v.mean():+.2f}({100 * np.sqrt((w ** 2).sum()) / 3:.2f})')
m, A = load(81); s = stop_stats(A); w = boot(stop_stats, A, rng); P(f'# run 81 job {m["job_id"]} results sha256 {sha(os.path.join(D, "run81_results.npz"))}')
P(''); P(f'== STOPWATCH RUN 81 PARKED EMITTERS (one job), residual = measured (mean of the two hand circuits) minus book [OWN], %; readable emitters {s["_n"]}, clip-bound {s["_nclip"]}')
for k in s:
    if k.startswith('_'): continue
    P(f'   {k:<60} {100 * s[k]:+.2f}({100 * w[k]:.2f})')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
