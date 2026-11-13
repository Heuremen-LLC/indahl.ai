#!/usr/bin/env python3
"""crossing_rulers2.py -- TRIPLE PASS seat C. Read-only. Companion to seatC_crossing_rulers.py (same loaders, same books).
  (a) the crossing with only the clip-bound qubits removed (P300 <= 0.02 or >= 0.98 -- where code/readclose.py's clip sets the clock);
  (b) the crossing by thirds of each qubit's own P300 (its OWN 300-us survival);
  (c) the early-decay shortfall at 30 us (OWN) that would absorb each job's crossing: the chip-wide dq such that the OFF-start
      residual against q30 = P300^(1/10) - dq is zero (mean over readable; and over P300 in (0.1, 0.9)), with its shot width;
      beside it the shortfall measured where it can be (run 121, the only job with 10/30/90-us |1>-idle arms);
  (d) FOREIGN ruler (cross-job, cross-chip, flagged): every push job booked with run 121's measured shortfall (typ mean) as a chip-wide shift;
  (e) the three-chip mean under each ruler.
Writes only seatC_crossing_rulers2.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIRE = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire'
OUT = os.path.join(HERE, 'seatC_crossing_rulers2.txt'); NB = 100


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(chip, r):
    m = json.load(open(os.path.join(FIRE, chip, f'run{r}_meta.json'))); assert m.get('complete') is True
    z = np.load(os.path.join(FIRE, chip, f'run{r}_results.npz'))
    return m, {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files if k.endswith('__L1')}


def proj(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    return {k: al(v).mean(0) for k, v in A.items()}, np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)


def book(start, q, n=10):
    on = np.asarray(start, float) * 1.0; off = 1 - on
    for _ in range(n): on, off = off + on * (1 - q), on * q
    return on


KEYS = {'push': ('OFF|p0', 'ON|p0', 'ON|n300', 'OFF|s10', 'ON|s10'), 'hold': ('OFF|w0', 'ON|w0', 'ON|N0', 'OFF|P9', 'ON|P9'),
        'noname': ('F0', 'F1', 'R300', 'A30_30', 'B30_30')}
SHIFT121 = None   # filled from run 121 (typ mean of R30 - P300^(1/10))


def job_stats(A, kind):
    f0, f1, n300, offk, onk = KEYS[kind]
    lv, sep = proj(A, f0, f1); g = sep > 4; p300 = lv[n300]; n = len(p300)
    q = np.clip(p300, 0.02, 0.98) ** 0.1; z0 = np.zeros(n); o1 = np.ones(n)
    dO = lv[offk] - book(z0, q); dN = lv[onk] - book(o1, q)
    clipfree = g & (p300 > 0.02) & (p300 < 0.98); typ = g & (p300 > 0.1) & (p300 < 0.9)
    out = {'OFF one-clock, mean readable': dO[g].mean(), 'OFF one-clock, clip-free': dO[clipfree].mean(),
           'ON one-clock, mean readable': dN[g].mean(), 'ON one-clock, clip-free': dN[clipfree].mean(),
           '_n': int(g.sum()), '_nclip': int((g & ~clipfree).sum())}
    # thirds of P300 among clip-free readable
    idx = np.where(clipfree)[0]; o = idx[np.argsort(p300[idx])]; th = np.array_split(o, 3)
    for j, t in enumerate(th):
        out[f'OFF one-clock, P300 third {j + 1}'] = dO[t].mean(); out[f'ON one-clock, P300 third {j + 1}'] = dN[t].mean()
        out[f'P300 third {j + 1} middle'] = np.median(p300[t])
    # the shortfall dq that zeroes the OFF residual (bisection on a chip-wide shift)
    for lab, sel in (('readable', g & (p300 > 0.02)), ('typ', typ)):
        lo, hi = -0.05, 0.10
        for _ in range(50):
            mid = 0.5 * (lo + hi); qq = np.clip(q - mid, 0.01, 0.999)
            r = (lv[offk] - book(z0, qq))[sel].mean()
            lo, hi = (mid, hi) if r > 0 else (lo, mid)
        out[f'shortfall dq at 30 us that zeroes the OFF residual ({lab})'] = 0.5 * (lo + hi)
    if SHIFT121 is not None:
        qq = np.clip(q - SHIFT121, 0.01, 0.999)
        out['FOREIGN: OFF with run-121 shortfall, mean readable'] = (lv[offk] - book(z0, qq))[g].mean()
        out['FOREIGN: ON with run-121 shortfall, mean readable'] = (lv[onk] - book(o1, qq))[g].mean()
        out['FOREIGN: OFF with run-121 shortfall, typ'] = (lv[offk] - book(z0, qq))[typ].mean()
    if kind == 'noname':
        R30 = lv['R30']; out['MEASURED shortfall R30 - P300^0.1, typ mean'] = (q - R30)[typ].mean()
        out['MEASURED shortfall R30 - P300^0.1, readable mean'] = (q - R30)[g].mean()
        out['MEASURED shortfall R30 - P300^0.1, readable median'] = np.median((q - R30)[g])
    return out


def boot(A, kind, rng):
    B = [job_stats({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}, kind) for _ in range(NB)]
    return {k: np.nanstd([b[k] for b in B]) for k in B[0] if not k.startswith('_')}


L = []; P = L.append; P(f'# script sha256 {sha(os.path.abspath(__file__))}')
rng = np.random.default_rng(20261003)
m121, A121 = load('ibm_pittsburgh', 121); s121 = job_stats(A121, 'noname'); w121 = boot(A121, 'noname', rng)
SHIFT121 = s121['MEASURED shortfall R30 - P300^0.1, typ mean']
P(f'RUN 121 (job {m121["job_id"]}): measured early-decay shortfall at 30 us [OWN], typ mean {SHIFT121:+.4f} ({w121["MEASURED shortfall R30 - P300^0.1, typ mean"]:.4f}); '
  f'readable mean {s121["MEASURED shortfall R30 - P300^0.1, readable mean"]:+.4f} ({w121["MEASURED shortfall R30 - P300^0.1, readable mean"]:.4f}); readable median {s121["MEASURED shortfall R30 - P300^0.1, readable median"]:+.4f}')
JOBS = [('PUSH RUN ibm_pittsburgh', 'ibm_pittsburgh', (91, 92, 93), 'push'), ('HOLD RUN ibm_pittsburgh', 'ibm_pittsburgh', (71, 72, 73), 'hold'),
        ('PUSH REP ibm_marrakesh', 'ibm_marrakesh', (141,), 'push'), ('PUSH REP ibm_kingston', 'ibm_kingston', (141,), 'push'),
        ('RUN 121 A30_30/B30_30 ibm_pittsburgh', 'ibm_pittsburgh', (121,), 'noname')]
RES = {}
for title, chip, runs, kind in JOBS:
    per = []
    for r in runs:
        m, A = load(chip, r); s = job_stats(A, kind); w = boot(A, kind, rng); per.append((s, w))
    P(''); P(f'== {title} runs {list(runs)}; readable ' + '/'.join(str(s["_n"]) for s, _ in per) + '; clip-bound among them ' + '/'.join(str(s["_nclip"]) for s, _ in per))
    RES[title] = {}
    for k in per[0][0]:
        if k.startswith('_'): continue
        v = np.array([s[k] for s, _ in per]); w = np.array([x[k] for _, x in per]); mn = v.mean(); wd = np.sqrt((w ** 2).sum()) / len(v)
        RES[title][k] = (mn, wd)
        P(f'   {k:<66} ' + '  '.join(f'{a:+.4f}({b:.4f})' for a, b in zip(v, w)) + (f'  | all {mn:+.4f}({wd:.4f})' if len(v) > 1 else ''))
P('')
P('== THREE-CHIP MEAN of the OFF crossing (push run for Pittsburgh; one job each elsewhere), under each ruler [OWN clock named]:')
for k in ('OFF one-clock, mean readable', 'OFF one-clock, clip-free', 'FOREIGN: OFF with run-121 shortfall, mean readable'):
    vals = [RES[t][k] for t in ('PUSH RUN ibm_pittsburgh', 'PUSH REP ibm_marrakesh', 'PUSH REP ibm_kingston')]
    mn = np.mean([v for v, _ in vals]); wd = np.sqrt(np.sum([w ** 2 for _, w in vals])) / 3
    P(f'   {k:<66} ' + '  '.join(f'{v:+.4f}({w:.4f})' for v, w in vals) + f'  | three-chip mean {mn:+.4f}({wd:.4f})')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
