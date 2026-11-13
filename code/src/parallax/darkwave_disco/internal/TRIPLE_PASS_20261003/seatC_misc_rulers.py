#!/usr/bin/env python3
"""misc_rulers.py -- TRIPLE PASS seat C. Read-only. Three smaller rulers moved, from raw jobs on disk.
 (1) Run 121 frame-held spectators: the 'own leftover' half-sum (+0.6 +- 4.5 deg, readnoname.py: mean over witnesses of angle(va vb)/2)
     against: median; circular (angle of the summed va vb, halved); length-weighted; and the half-difference (coupling x ON time).
 (2) Push run 91-93 back-to-back arms: the per-push cap k (0.26 +- 0.12 %) from o_N + |u_N| = 2 sin^2(N e / 2) + (N / 2) k, N = 2, 10,
     under: projection / threshold assignment; all readable / clip-free.
 (3) The leakage-plus-TLS 'needed' leakage (2.96 % per push) re-solved on the crossings re-booked clip-free (the reviewer's two model rows,
     ledger line 1953, as reads_new/leak_tls_fit.py takes them; the rows are model numbers, not on disk as code).
Writes only seatC_misc_rulers.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
ROLES = json.load(open('/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/noname_roles.json'))
WOF = {int(k): int(v) for k, v in ROLES['witness_of'].items()}
OUT = os.path.join(HERE, 'seatC_misc_rulers.txt'); NB = 100


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def loadA(r):
    z = np.load(os.path.join(D, f'run{r}_results.npz')); return {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}


def frame(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    return al, np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)


def wit(A):
    al, sep = frame(A, 'F0', 'F1'); g = sep > 4; lv = {k: al(v).mean(0) for k, v in A.items()}
    W = np.array([w for w in WOF if g[w] and g[WOF[w]]], int)
    va = (2 * lv['WA|X'] - 1) + 1j * (1 - 2 * lv['WA|Y']); vb = (2 * lv['WB|X'] - 1) + 1j * (1 - 2 * lv['WB|Y'])
    hs = np.angle(va[W] * vb[W]) / 2; hd = np.angle(vb[W] * np.conj(va[W])) / 2
    prod = va[W] * vb[W]
    return {'leftover half-sum, mean (claimed), deg': np.degrees(hs).mean(), 'leftover half-sum, median, deg': np.degrees(np.median(hs)),
            'leftover half-sum, circular (angle of summed va*vb, halved), deg': np.degrees(np.angle(prod.sum()) / 2),
            'leftover half-sum, weighted by |va||vb|, deg': np.degrees((hs * np.abs(prod)).sum() / np.abs(prod).sum()),
            'half-difference |hd|, mean, deg (five ON stretches)': np.degrees(np.abs(hd)).mean(),
            'half-difference signed, mean, deg': np.degrees(hd).mean(), '_W': len(W)}


def cap(o2, u2, o10, u10):
    s2, s10 = o2 + abs(u2), o10 + abs(u10)
    best = None
    for e in np.linspace(0, np.radians(4), 40001):
        k = s2 - 2 * np.sin(e) ** 2
        r = 2 * np.sin(5 * e) ** 2 + 5 * k - s10
        if best is None or abs(r) < abs(best[0]): best = (r, e, k)
    return np.degrees(best[1]), best[2]


def push_cap(A, mode, sel_mode):
    c0 = A['OFF|p0'].mean(0); d = A['ON|p0'].mean(0) - c0; al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    sep = np.abs(d) / np.sqrt((np.abs(A['OFF|p0'] - c0) ** 2).mean(0) / 2); g = sep > 4
    if mode == 'proj': lv = {k: al(v).mean(0) for k, v in A.items()}
    else:
        e0 = (al(A['OFF|p0']) > 0.5).mean(0); e1 = 1 - (al(A['ON|p0']) > 0.5).mean(0); den = np.clip(1 - e0 - e1, 0.05, None)
        lv = {k: ((al(v) > 0.5).mean(0) - e0) / den for k, v in A.items()}
    if sel_mode == 'clip-free': g = g & (lv['ON|n300'] > 0.02)
    o2 = (lv['OFF|p2'] - lv['OFF|p0'])[g].mean(); o10 = (lv['OFF|p10'] - lv['OFF|p0'])[g].mean()
    u2 = (lv['ON|p2'] - lv['ON|p0'])[g].mean(); u10 = (lv['ON|p10'] - lv['ON|p0'])[g].mean()
    q = np.clip(lv['ON|n300'], 0.02, 0.98) ** 0.1; mid0 = lv['MID|p0']
    on, off = mid0.copy(), 1 - mid0
    for _ in range(10): on, off = off + on * (1 - q), on * q
    e, k = cap(o2, u2, o10, u10)
    return {'shortfall e (deg)': e, 'k per push (%)': 100 * k, 'MID spread minus one-clock book (%)': 100 * (lv['MID|s10'] - on)[g].mean()}


L = []; P = L.append; P(f'# script sha256 {sha(os.path.abspath(__file__))}')
rng = np.random.default_rng(20261003)
A = loadA(121); s = wit(A)
B = [wit({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}) for _ in range(NB)]
P(f'== (1) RUN 121 frame-held spectators [WITNESS], {s["_W"]} witness-emitter pairs; (shot width over {NB} resamples)')
for k in s:
    if not k.startswith('_'): P(f'   {k:<70} {s[k]:+.3f} ({np.std([b[k] for b in B]):.3f})')
P(''); P('== (2) PUSH RUN 91-93 back-to-back arms: the push shortfall e and the per-push cap k; MID start booked one-clock [OWN] beside it (three jobs averaged; width = SD over 40 resamples / sqrt 3)')
for mode in ('proj', 'thr'):
    for selm in ('readable', 'clip-free'):
        vals = []; wds = []
        for r in (91, 92, 93):
            A = loadA(r); s = push_cap(A, mode, selm)
            Bs = [push_cap({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}, mode, selm) for _ in range(40)]
            vals.append(s); wds.append({k: np.std([b[k] for b in Bs]) for k in s})
        P(f'   {mode:<4} {selm:<9} ' + ' | '.join(f'{k} {np.mean([v[k] for v in vals]):+.3f} ({np.sqrt(np.sum([w[k] ** 2 for w in wds])) / 3:.3f})' for k in vals[0]))
P('')
# (3) re-solve the reviewer's two rows on clip-free crossings (weights 1/width^2), rows from ledger line 1953 / reads_new/leak_tls_fit.py
LEAK = np.array([1.86, -1.34, 0.26]); TLS = np.array([-5.30, 6.08, -0.67])
def solve(meas, wid):
    Wm = np.diag(1 / np.array(wid) ** 2); X = np.vstack([LEAK, TLS]).T
    cov = np.linalg.inv(X.T @ Wm @ X); ab = cov @ X.T @ Wm @ np.array(meas); res = (np.array(meas) - X @ ab) / np.array(wid)
    return ab, np.sqrt(np.diag(cov)), res
for lab, meas, wid in (('claimed (one-clock, mean readable): OFF +2.00, ON +0.05, MID +0.34', [2.00, 0.05, 0.34], [0.16, 0.13, 0.14]),):
    ab, e, res = solve(meas, wid); P(f'== (3) {lab}: leakage {ab[0]:.2f} ({e[0]:.2f}) % per push, TLS {ab[1]:.2f} ({e[1]:.2f}); residuals/width {np.round(res, 2)}')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
