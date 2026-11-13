#!/usr/bin/env python3
"""hold_crossing.py -- THE HOLD RUN'S OFF-start ten-push crossing, mean over qubits, from the raw jobs (ibm_pittsburgh). No hardware contact.
Reads (read-only):  parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh/run{71,72,73}_* (hold run) and run{91,92,93}_* (push run, ruler row)
Writes only:        darkwave_disco/internal/reads_new/hold_crossing.txt
Computed the same way as reads/close_push.txt's +0.0200 +- 0.0016: code/readclose.py push_stats() copied (frame from lone looks, readable =
separation > 4 widths, one-exponential bookkeeping q = clip(P300, 0.02, 0.98)^(1/10), mean over readable qubits), 100 bootstrap resamples of shots
with readclose.py's own seed (20261002), three reads combined as readclose.py three(). The push run is recomputed first as a ruler row."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
OUT = os.path.join(HERE, 'hold_crossing.txt')
NB = 100; SEED = 20261002


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


def crossing(A, keys):
    """keys: frame OFF, frame ON, the 300-us nothing-done ON arm, the OFF-start spread arm, the ON-start spread arm (code/readclose.py push_stats)."""
    f0, f1, n300, offs, ons = keys
    al, sep = frame(A, f0, f1); g = sep > 4
    lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    q = np.clip(lv[n300], 0.02, 0.98) ** 0.1
    z, o = np.zeros_like(q), np.ones_like(q)
    dO = lv[offs] - book(z, q, 10); dN = lv[ons] - book(o, q, 10)
    return {'OFF': dO[g].mean(), 'ON': dN[g].mean(), 'OFF median qubit': np.median(dO[g]), 'OFF share above 0': np.mean(dO[g] > 0), '_bits': int(g.sum())}


def three(vals, widths):                                   # code/readclose.py three()
    v = np.array(vals); w = np.array(widths)
    return v.mean(), np.sqrt((w ** 2).sum()) / len(v), [v[i] - np.mean(np.delete(v, i)) for i in range(len(v))]


def run_set(runs, keys):
    rng = np.random.default_rng(SEED); R = []                  # readclose.py: one generator, seeded once, used read after read
    for r in runs:
        m, A = load(r); s = crossing(A, keys); B = [crossing(resample(A, rng), keys) for _ in range(NB)]
        R.append((r, m, s, {k: np.std([b[k] for b in B]) for k in s if not k.startswith('_')}))
    return R


L = []; P = L.append
me = os.path.abspath(__file__)
P(f'# script sha256 {sha(me)}  {os.path.relpath(me, "/Users/heuremen/bones-forge/parallax")}')
for r in (71, 72, 73, 91, 92, 93):
    for f in (f'run{r}_meta.json', f'run{r}_results.npz'): P(f'# input  sha256 {sha(os.path.join(RAW, f))}  out/qubit_fifth_run/data/fire/ibm_pittsburgh/{f}')
HOLD = run_set((71, 72, 73), ('OFF|w0__L1', 'ON|w0__L1', 'ON|N0', 'OFF|P9', 'ON|P9'))
PUSH = run_set((91, 92, 93), ('OFF|p0__L1', 'ON|p0__L1', 'ON|n300', 'OFF|s10', 'ON|s10'))
hdr = '; '.join(f"run {r} job {m['job_id']} started {m['start_time'][11:19]} EDT, results read {m['result_read_at'][11:19]} EDT, {m['shots']} shots" for r, m, _, _ in HOLD)
P(f'THE HOLD RUN\'S CROSSING -- ibm_pittsburgh hold run (runs 71/72/73: {hdr}). Script: reads_new/hold_crossing.py.')
P('Clock key: LAID = laid time; OWN = the qubit\'s own decay (here: its own 300-us nothing-done survival, one exponential, cut into ten LAID 30-us intervals); WITNESS = a spectator.')
P('Arm: start OFF, ten intervals of 30 us LAID with an X after each (alternate intervals in |1>), one look. The same circuit as the push run\'s OFF spread arm.')
P('Quantity: measured level minus one-exponential bookkeeping [OWN], mean over readable qubits (separation > 4 widths), widths from 100 shot resamples; as code/readclose.py push_stats().')
P('')
for title, R in (('HOLD RUN (runs 71, 72, 73)', HOLD), ('RULER ROW -- the push run (runs 91, 92, 93) through the same code; reads/close_push.txt:4 and :7 print +0.0200 +- 0.0016 and +0.0005 +- 0.0013', PUSH)):
    P(f'== {title}; readable qubits ' + ' / '.join(str(s['_bits']) for _, _, s, _ in R))
    for k, lab in (('OFF', 'start OFF, ten pushes 30 us apart, minus bookkeeping [OWN]'), ('ON', 'start ON, same pushes, minus bookkeeping [OWN]'),
                   ('OFF median qubit', 'start OFF, median qubit of the same per-qubit differences [OWN]'), ('OFF share above 0', 'start OFF, share of qubits above zero [OWN]')):
        vals = [s[k] for _, _, s, _ in R]; wds = [w[k] for _, _, _, w in R]; mn, wd, oth = three(vals, wds)
        P(f'   {lab:<66} ' + '  '.join(f'{v:+.4f} +- {w:.4f}' for v, w in zip(vals, wds)) + f'   | all {mn:+.4f} +- {wd:.4f}   each minus the other two ' + ' '.join(f'{x:+.4f}' for x in oth))
    P('')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
