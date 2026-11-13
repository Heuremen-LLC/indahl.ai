#!/usr/bin/env python3
"""leak_tls_fit.py -- re-runs the fit behind ledger §146's "2.96% leakage per push" from what is on disk. No hardware contact.
What exists on disk: the reviewer's two model ROWS, as numbers only (THIRD_RUNG_20260928.md:1953; disco_deck/project/slides/tri3.html):
   leakage row, at 1% leakage per push:  OFF +1.86, ON -1.34, in-between +0.26  (% of population, vs one-exponential bookkeeping)
   TLS row, at TLS strength 1:           OFF -5.30, ON +6.08, in-between -0.67
and the measured crossings (push run, raw jobs runs 91/92/93). The fit is weighted least squares of the three measured starts on
a x (leakage row) + b x (TLS row), each row scaled linearly. The reviewer's simulation that made the rows is NOT on disk.
Reads (read-only): parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh/run{91,92,93}_*.  Writes only: reads_new/leak_tls_fit.txt."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
OUT = os.path.join(HERE, 'leak_tls_fit.txt')
NB = 100; SEED = 20261002
LEAK = np.array([1.86, -1.34, 0.26])        # per 1 % leakage per push (reviewer's row; ledger line 1953)
TLS = np.array([-5.30, 6.08, -0.67])        # per unit TLS strength (reviewer's row; ledger line 1953)
STARTS = ('OFF', 'ON', 'in-between')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(r):
    m = json.load(open(os.path.join(RAW, f'run{r}_meta.json')))
    if m.get('complete') is not True: raise SystemExit(f'run {r} not complete')
    z = np.load(os.path.join(RAW, f'run{r}_results.npz'))
    return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


def frame(A, off, on):                                     # code/readclose.py frame()
    c0 = A[off].mean(0); d = A[on].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[off] - c0) ** 2).mean(0) / 2)


def resample(A, rng):                                      # code/readclose.py resample()
    out, idx = {}, {}
    for k, v in A.items():
        b = k.split('__')[0]
        if b not in idx: idx[b] = rng.integers(0, v.shape[0], v.shape[0])
        out[k] = v[idx[b]]
    return out


def book(m0, q, nseg):                                     # code/readclose.py book()
    on, off = m0, 1 - m0
    for _ in range(nseg): on, off = off + on * (1 - q), on * q
    return on


def spread(A):                                             # code/readclose.py push_stats(), the three spread arms only
    al, sep = frame(A, 'OFF|p0__L1', 'ON|p0__L1'); g = sep > 4
    lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    q = np.clip(lv['ON|n300'], 0.02, 0.98) ** 0.1
    st = {'OFF': np.zeros_like(q), 'ON': np.ones_like(q), 'MID': lv['MID|p0']}
    return {s: (lv[f'{s}|s10'] - book(st[s], q, 10))[g].mean() for s in ('OFF', 'ON', 'MID')}


def wls(y, s, rows):
    X = np.vstack(rows).T; W = np.diag(1 / s ** 2)
    C = np.linalg.inv(X.T @ W @ X); p = C @ X.T @ W @ y; pred = X @ p
    return p, np.sqrt(np.diag(C)), C, pred, (y - pred) / s, float((((y - pred) / s) ** 2).sum())


L = []; P = L.append
me = os.path.abspath(__file__)
P(f'# script sha256 {sha(me)}  {os.path.relpath(me, "/Users/heuremen/bones-forge/parallax")}')
for r in (91, 92, 93):
    for f in (f'run{r}_meta.json', f'run{r}_results.npz'): P(f'# input  sha256 {sha(os.path.join(RAW, f))}  out/qubit_fifth_run/data/fire/ibm_pittsburgh/{f}')
P(f'# input  sha256 {sha("/Users/heuremen/bones-forge/parallax/THIRD_RUNG_20260928.md")}  THIRD_RUNG_20260928.md (line 1953 holds the two rows; read, not edited)')
rng = np.random.default_rng(SEED); per = []; M = {}
for r in (91, 92, 93):
    m, A = load(r); M[r] = m; s = spread(A); B = [spread(resample(A, rng)) for _ in range(NB)]
    per.append((s, {k: np.std([b[k] for b in B]) for k in s}))
hdr = '; '.join(f"run {r} job {M[r]['job_id']} started {M[r]['start_time'][11:19]} EDT, results read {M[r]['result_read_at'][11:19]} EDT, {M[r]['shots']} shots" for r in (91, 92, 93))
P(f'THE LEAKAGE-PLUS-TLS FIT (ledger §146), RE-RUN -- inputs from the ibm_pittsburgh push run (runs 91/92/93: {hdr}). Script: reads_new/leak_tls_fit.py.')
P('Clock key: LAID = laid time and gate count; OWN = the qubit\'s own decay (here: one-exponential bookkeeping from its 300-us nothing-done survival); WITNESS = a spectator.')
P('Model rows are the reviewer\'s simulated shifts of the same quantity (level minus one-exponential bookkeeping [OWN]); a = leakage in % per LAID push; b = TLS strength in the reviewer\'s units (no clock).')
P('')
ym = []; sm = []
for k in ('OFF', 'ON', 'MID'):
    v = np.array([p[0][k] for p in per]); w = np.array([p[1][k] for p in per])
    ym.append(100 * v.mean()); sm.append(100 * np.sqrt((w ** 2).sum()) / 3)
ym, sm = np.array(ym), np.array(sm)
P('== INPUTS, ten pushes 30 us LAID apart, measured minus bookkeeping [OWN], %, mean of three reads (width sqrt(sum w^2)/3):')
P('   recomputed from the raw jobs: ' + '   '.join(f'{n} {y:+.3f} +- {s:.3f}' for n, y, s in zip(STARTS, ym, sm)))
P('   as written in the ledger (line 1953, rounded): OFF +2.00 +- 0.16   ON +0.05 +- 0.13   in-between +0.34 +- 0.14')
P('')
for title, y, s in (('FIT ON THE LEDGER\'S ROUNDED INPUTS', np.array([2.00, 0.05, 0.34]), np.array([0.16, 0.13, 0.14])), ('FIT ON THE INPUTS RECOMPUTED FROM THE RAW JOBS', ym, sm)):
    P(f'== {title}')
    for name, rows, pn in (('leakage row alone', [LEAK], ['a (% leakage per LAID push)']), ('TLS row alone', [TLS], ['b (TLS strength)']), ('both rows together', [LEAK, TLS], ['a (% leakage per LAID push)', 'b (TLS strength)'])):
        p, e, C, pred, res, chi = wls(y, s, rows)
        par = '; '.join(f'{lab} = {pv:+.3f} +- {ev:.3f}' for lab, pv, ev in zip(pn, p, e))
        corr = f'; correlation of a and b {C[0, 1] / np.sqrt(C[0, 0] * C[1, 1]):+.3f}' if len(p) == 2 else ''
        P(f'   {name}: {par}{corr}')
        P(f'      model gives [OWN] ' + '   '.join(f'{n} {v:+.3f}' for n, v in zip(STARTS, pred)) + '   | measured minus model, in widths: ' + '   '.join(f'{n} {v:+.2f}' for n, v in zip(STARTS, res)) + f'   | chi2 {chi:.2f} on {3 - len(p)} dof')
    P('')
P('== NOT ON DISK (so not re-run): the reviewer\'s simulation that produced the two rows -- its code, its pulse and leakage model, where |2> reads on the')
P('   OFF -> ON line (x2), its TLS model and what "strength 1" means. Without it the rows cannot be regenerated, and the fit\'s one assumption -- each row')
P('   scales linearly with its parameter (2.96 % per push = 2.96 x the 1 %-per-push row) -- cannot be checked. Searched: THIRD_RUNG_20260928.md, parallax/ text files')
P('   (*.md *.txt *.py *.json), parallax/disco_deck/, the session scratch folder; the rows appear only as numbers in the ledger (line 1953) and the deck slide tri3.html.')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
