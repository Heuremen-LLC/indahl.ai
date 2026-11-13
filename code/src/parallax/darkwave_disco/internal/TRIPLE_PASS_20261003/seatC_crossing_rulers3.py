#!/usr/bin/env python3
"""seatC_crossing_rulers3.py -- TRIPLE PASS seat C. Read-only. Run 121 only (ibm_pittsburgh, job db00t8k92g1c7399m6hg).
The per-entry ("each stretch its own") ruler without the per-qubit noise: q_L = each qubit's SMOOTH decay curve at L, the curve being
the chip-wide two-part shape fitted in this job ((1-f) exp(-t/Ts) + f exp(-t/Tf), Ts per qubit from its own P300) -- 'own-smooth'.
Beside it the claimed per-qubit 'own' (noisy R_L per qubit) and 'one', ten arms, chi2, mean over readable and over P300 in (0.1, 0.9).
Also: the noise-curvature bias of the per-qubit own book, measured by simulation (each qubit's smooth curve + its own shot noise).
Writes only seatC_crossing_rulers3.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIRE = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
OUT = os.path.join(HERE, 'seatC_crossing_rulers3.txt'); NB = 100
ARMS = {'A30_30': ('OFF', [30, 30] * 5, False), 'A10_30': ('OFF', [10, 30] * 5, False), 'A90_30': ('OFF', [90, 30] * 5, False),
        'A30_10': ('OFF', [30, 10] * 5, False), 'A30_90': ('OFF', [30, 90] * 5, False), 'A30_30f': ('OFF', [30, 30] * 5, True),
        'B30_30': ('ON', [30, 30] * 5, False), 'B30_30f': ('ON', [30, 30] * 5, True), 'N2': ('OFF', [30, 30], False), 'N6': ('OFF', [30, 30] * 3, False)}
TF = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60]); FG = np.linspace(0, 0.12, 61)


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def book(start, qs, flip=False):
    on = np.asarray(start, float) * 1.0; off = 1 - on
    for q in qs: on, off = off + on * (1 - q), on * q
    if flip: on, off = off, on
    return on


def levels(A):
    c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0
    al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    return {k: al(v).mean(0) for k, v in A.items()}, np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2), al


def fit(R, sel):
    best = (np.inf, 0, 10)
    for Tf in TF:
        for f in FG:
            es = np.clip((R[300] - f * np.exp(-300 / Tf)) / (1 - f), 1e-4, 0.9999); r = 0
            for L in (10, 30, 90): r += ((R[L] - ((1 - f) * es ** (L / 300) + f * np.exp(-L / Tf)))[sel] ** 2).sum()
            if r < best[0]: best = (r, f, Tf)
    return best[1], best[2]


def stats(A):
    lv, sep, _ = levels(A); g = sep > 4; R = {L: lv[f'R{L}'] for L in (10, 30, 90, 300)}; p300 = R[300]
    typ = g & (p300 > 0.1) & (p300 < 0.9); f, Tf = fit(R, typ)
    es = np.clip((p300 - f * np.exp(-300 / Tf)) / (1 - f), 1e-4, 0.9999)
    smooth = lambda L: np.clip((1 - f) * es ** (L / 300) + f * np.exp(-L / Tf), 0.01, 0.999)
    one = lambda L: np.clip(p300, 0.02, 0.98) ** (L / 300); own = lambda L: np.clip(R[L], 0.02, 1.2)
    out = {'f': f, 'Tf': Tf}
    for k, (st, S, fl) in ARMS.items():
        s0 = np.zeros(len(p300)) if st == 'OFF' else np.ones(len(p300))
        for nm, fn in (('one', one), ('own', own), ('own-smooth', smooth)):
            d = lv[k] - book(s0, [fn(L) for L in S], fl)
            out[f'{k}|{nm}|mean'] = d[g].mean(); out[f'{k}|{nm}|typ'] = d[typ].mean()
    return out


def sim_bias(A, rng, nsim=40):
    """each qubit's smooth curve taken as true; draw its R_L with its own per-shot spread at 216 shots; book with the noisy per-qubit q_L;
    the mean over qubits minus the noise-free book = the per-qubit own ruler's noise-curvature bias (OFF arm A30_30 and ON arm B30_30)."""
    lv, sep, al = levels(A); g = sep > 4; R = {L: lv[f'R{L}'] for L in (10, 30, 90, 300)}; p300 = R[300]
    typ = g & (p300 > 0.1) & (p300 < 0.9); f, Tf = fit(R, typ)
    es = np.clip((p300 - f * np.exp(-300 / Tf)) / (1 - f), 1e-4, 0.9999)
    true = {L: np.clip((1 - f) * es ** (L / 300) + f * np.exp(-L / Tf), 0.01, 0.999) for L in (10, 30, 90)}
    sd = {L: al(A[f'R{L}']).std(0) / np.sqrt(A[f'R{L}'].shape[0]) for L in (10, 30, 90)}
    out = {}
    for k in ('A30_30', 'B30_30', 'A30_10', 'N2'):
        st, S, fl = ARMS[k]; s0 = np.zeros(len(p300)) if st == 'OFF' else np.ones(len(p300))
        b_true = book(s0, [true[L] for L in S], fl)
        bias = []
        for _ in range(nsim):
            noisy = {L: np.clip(true[L] + rng.normal(0, sd[L]), 0.02, 1.2) for L in (10, 30, 90)}
            bias.append((book(s0, [noisy[L] for L in S], fl) - b_true)[typ].mean())
        out[k] = (np.mean(bias), np.std(bias) / np.sqrt(nsim), float(np.median(sd[30][typ])))
    return out


z = np.load(os.path.join(FIRE, 'run121_results.npz')); A = {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}
m = json.load(open(os.path.join(FIRE, 'run121_meta.json')))
rng = np.random.default_rng(20261003); s = stats(A)
B = [stats({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}) for _ in range(NB)]
w = {k: np.std([b[k] for b in B]) for k in s}
L = []; P = L.append
P(f'# script sha256 {sha(os.path.abspath(__file__))}; input run121_results.npz sha256 {sha(os.path.join(FIRE, "run121_results.npz"))}')
P(f'RUN 121, ibm_pittsburgh, job {m["job_id"]}. Chip-wide shape fitted in this job: fast fraction f = {s["f"]:.4f} ({w["f"]:.4f}), fast clock Tf = {s["Tf"]:.1f} ({w["Tf"]:.1f}) us [OWN].')
P('Residual = measured level minus book, % of population; (shot width). Clocks: one = one exponential through 300 us [OWN]; own = per-qubit R_L per stretch [OWN, claimed];')
P('own-smooth = per-entry, each qubit\'s smooth fitted curve at L [OWN]. Stretches are LAID.')
for stt in ('mean', 'typ'):
    P(f'  statistic: {stt}')
    chi = {}
    for k in ARMS:
        row = []
        for nm in ('one', 'own', 'own-smooth'):
            v, e = s[f'{k}|{nm}|{stt}'], w[f'{k}|{nm}|{stt}']; row.append(f'{nm} {100 * v:+.2f} ({100 * e:.2f})'); chi[nm] = chi.get(nm, 0) + (v / e) ** 2
        P(f'    {k:<8} ' + ' | '.join(row))
    P('    chi2 over ten arms: ' + ' | '.join(f'{nm} {c:.1f}' for nm, c in chi.items()))
bias = sim_bias(A, np.random.default_rng(7))
P('NOISE-CURVATURE BIAS of the per-qubit own book (simulated: each typical qubit\'s smooth curve as truth, its own per-shot spread, 216 shots, 40 draws):')
for k, (b, e, sd30) in bias.items():
    P(f'    {k:<8} book shifted by {100 * b:+.2f} % ({100 * e:.2f}) -> residual shifted by {-100 * b:+.2f} %   (median per-qubit width of R30: {sd30:.4f})')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
