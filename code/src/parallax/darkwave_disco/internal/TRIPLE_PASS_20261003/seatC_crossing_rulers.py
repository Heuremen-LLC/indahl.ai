#!/usr/bin/env python3
"""seatC_crossing_rulers.py -- TRIPLE PASS seat C (the own clock). Read-only. The push-train crossing under moved rulers.
Reads raw jobs (read-only) from parallax/out/qubit_fifth_run/data/fire/; writes only crossing_rulers.txt beside this script.
Rulers moved (each named by its clock: LAID = laid time; OWN = the qubit's own decay clock; WITNESS = spectator):
  DECAY CLOCK (OWN) used to book the train:
    one   -- one exponential through the same job's 300-us |1>-idle level, q_L = P300^(L/300)            [the claimed ruler]
    own   -- each stretch its own: q_L = the same job's |1>-idle level after L (run 121 only)            [the claimed alternative]
    mix   -- T1-fluctuation mixture: chip-wide fast fraction f and fast clock Tf fitted to the same job's 10/30/90/300 levels,
             each qubit's slow clock from its own P300; the book is the shot-mixture of the two books   (run 121 only)
    long  -- the slow component of that same mixture alone (the fast part never recurs in the train)       (run 121 only)
    once  -- the slow component plus the fast loss ONCE, at the shot's first excitation                     (run 121 only)
  STATE ASSIGNMENT: proj = projection on the |0>-|1> line from the same job's calibration clouds (claimed);
                    thr  = hard cut at the line's midpoint, corrected with the same job's assignment matrix.
  STATISTIC: mean over readable qubits (claimed) / median of per-qubit differences / mean over qubits whose P300 lies in
             (0.10, 0.90) (where the 0.02 clip and short-clock qubits do not bind) / readable cut at 8 widths instead of 4.
Widths: 100 shot resamples per arm (seed 20261003); three-job widths sqrt(sum w^2)/3 as code/readclose.py three()."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIRE = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire'
OUT = os.path.join(HERE, 'seatC_crossing_rulers.txt')
NB = 100


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(chip, r):
    m = json.load(open(os.path.join(FIRE, chip, f'run{r}_meta.json')))
    assert m.get('complete') is True
    z = np.load(os.path.join(FIRE, chip, f'run{r}_results.npz'))
    return m, {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files if k.endswith('__L1')}


def frames(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    sep = np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)
    proj = {k: al(v).mean(0) for k, v in A.items()}
    e0 = (al(A[f0]) > 0.5).mean(0); e1 = 1 - (al(A[f1]) > 0.5).mean(0)
    den = np.clip(1 - e0 - e1, 0.05, None)
    thr = {k: (((al(v) > 0.5).mean(0)) - e0) / den for k, v in A.items()}
    return proj, thr, sep


def book(start, qs, flip=False):
    on = np.asarray(start, float) * 1.0; off = 1 - on
    for q in qs: on, off = off + on * (1 - q), on * q
    if flip: on, off = off, on
    return on


def book_once(start, qs_slow, f_loss, flip=False):
    """slow decay every stretch; the fast loss f_loss applied once, to the population at the shot's first excitation."""
    on = np.asarray(start, float) * 1.0; off = 1 - on; first = np.asarray(start, float) > 0.5
    if np.all(first): on = on * (1 - f_loss); off = 1 - on      # ON start: excited at t=0, fast loss then
    excited = np.all(first)
    for q in qs_slow:
        on, off = off + on * (1 - q), on * q                     # stretch then X
        if not excited:                                          # OFF start: the first X excites; the fast loss rides the first ON stretch
            on = on * (1 - f_loss); off = 1 - on; excited = True
    if flip: on, off = off, on
    return on


STATS = ('mean', 'median', 'typ', 'sep8')


def summarize(d, g, g8, typ):
    return {'mean': d[g].mean(), 'median': np.median(d[g]), 'typ': d[g & typ].mean(), 'sep8': d[g8].mean()}


# ------------------------------------------------------------------------------------------------ push-shape jobs (14 circuits)
def push_job(A):
    out = {}
    proj, thr, sep = frames(A, 'OFF|p0', 'ON|p0'); g = sep > 4; g8 = sep > 8
    for lab, lv in (('proj', proj), ('thr', thr)):
        p300 = lv['ON|n300']; typ = (p300 > 0.10) & (p300 < 0.90); q = np.clip(p300, 0.02, 0.98) ** 0.1
        for s, start in (('OFF', np.zeros(len(p300))), ('ON', np.ones(len(p300)))):
            d = lv[f'{s}|s10'] - book(start, [q] * 10)
            for st, v in summarize(d, g, g8, typ).items(): out[f'{s} spread minus one-clock book | {lab} | {st}'] = v
        out[f'idle |0> 300 us | {lab} | mean'] = lv['OFF|n300'][g].mean()
        out[f'idle |1> 300 us (P300) | {lab} | mean'] = p300[g].mean()
        out[f'idle |1> 300 us (P300) | {lab} | median'] = np.median(p300[g])
    out['_n'] = int(g.sum()); out['_n_typ'] = int((g & (proj['ON|n300'] > 0.1) & (proj['ON|n300'] < 0.9)).sum()); out['_n8'] = int(g8.sum())
    return out


def hold_job(A):
    out = {}
    proj, thr, sep = frames(A, 'OFF|w0', 'ON|w0'); g = sep > 4; g8 = sep > 8
    for lab, lv in (('proj', proj), ('thr', thr)):
        p300 = lv['ON|N0']; typ = (p300 > 0.10) & (p300 < 0.90); q = np.clip(p300, 0.02, 0.98) ** 0.1
        for s, key, start in (('OFF', 'OFF|P9', np.zeros(len(p300))), ('ON', 'ON|P9', np.ones(len(p300)))):
            d = lv[key] - book(start, [q] * 10)
            for st, v in summarize(d, g, g8, typ).items(): out[f'{s} spread minus one-clock book | {lab} | {st}'] = v
        out[f'idle |1> 300 us (P300) | {lab} | mean'] = p300[g].mean()
        out[f'idle |1> 300 us (P300) | {lab} | median'] = np.median(p300[g])
    out['_n'] = int(g.sum()); out['_n_typ'] = int((g & (proj['ON|N0'] > 0.1) & (proj['ON|N0'] < 0.9)).sum()); out['_n8'] = int(g8.sum())
    return out


# ------------------------------------------------------------------------------------------------ run 121 (all rulers)
NONAME = {'A30_30': ('OFF', [30, 30] * 5, False), 'A10_30': ('OFF', [10, 30] * 5, False), 'A90_30': ('OFF', [90, 30] * 5, False),
          'A30_10': ('OFF', [30, 10] * 5, False), 'A30_90': ('OFF', [30, 90] * 5, False), 'A30_30f': ('OFF', [30, 30] * 5, True),
          'B30_30': ('ON', [30, 30] * 5, False), 'B30_30f': ('ON', [30, 30] * 5, True), 'N2': ('OFF', [30, 30], False), 'N6': ('OFF', [30, 30] * 3, False)}
TF_GRID = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60]); F_GRID = np.linspace(0.0, 0.12, 61)


def fit_mixture(R, sel):
    """chip-wide fast fraction f and fast clock Tf; per-qubit slow clock from P300: P(t) = (1-f) exp(-t/Ts) + f exp(-t/Tf)."""
    best = (np.inf, 0.0, 10.0)
    for Tf in TF_GRID:
        for f in F_GRID:
            es = np.clip((R[300] - f * np.exp(-300 / Tf)) / (1 - f), 1e-4, 0.9999)       # exp(-300/Ts)
            res = 0.0
            for L in (10, 30, 90):
                pred = (1 - f) * es ** (L / 300) + f * np.exp(-L / Tf); res += ((R[L] - pred)[sel] ** 2).sum()
            if res < best[0]: best = (res, f, Tf)
    return best[1], best[2]


def noname_job(A, want_fit=False):
    out = {}
    proj, thr, sep = frames(A, 'F0', 'F1'); g = sep > 4; g8 = sep > 8
    for lab, lv in (('proj', proj), ('thr', thr)):
        R = {L: lv[f'R{L}'] for L in (10, 30, 90, 300)}; p300 = R[300]; typ = (p300 > 0.10) & (p300 < 0.90)
        sel = g & typ
        f, Tf = fit_mixture(R, sel)
        es = np.clip((p300 - f * np.exp(-300 / Tf)) / (1 - f), 1e-4, 0.9999)
        qone = lambda L: np.clip(p300, 0.02, 0.98) ** (L / 300.0)
        qown = lambda L: np.clip(R[L], 0.02, 1.2)
        qslow = lambda L: es ** (L / 300.0)
        qfast = lambda L: np.full(len(p300), np.exp(-L / Tf))
        if lab == 'proj':
            out['mixture fit: fast fraction f'] = f; out['mixture fit: fast clock Tf (us)'] = Tf
            for L in (10, 30, 90):
                out[f'decay shape: R{L} minus one-clock (mean, typ)'] = (R[L] - qone(L))[sel].mean()
                out[f'decay shape: R{L} minus mixture fit (mean, typ)'] = (R[L] - ((1 - f) * es ** (L / 300) + f * np.exp(-L / Tf)))[sel].mean()
        for key, (st, stretches, flip) in NONAME.items():
            start = np.zeros(len(p300)) if st == 'OFF' else np.ones(len(p300))
            books = {'one': book(start, [qone(L) for L in stretches], flip),
                     'own': book(start, [qown(L) for L in stretches], flip),
                     'mix': (1 - f) * book(start, [qslow(L) for L in stretches], flip) + f * book(start, [qfast(L) for L in stretches], flip),
                     'long': book(start, [qslow(L) for L in stretches], flip),
                     'once': book_once(start, [qslow(L) for L in stretches], f, flip)}
            for bk, b in books.items():
                d = lv[key] - b
                for stt, v in summarize(d, g, g8, typ).items(): out[f'{key} minus {bk} book | {lab} | {stt}'] = v
        out[f'idle |0> 300 us | {lab} | mean'] = lv['Z300'][g].mean()
        out[f'idle |1> 300 us (P300) | {lab} | mean'] = p300[g].mean(); out[f'idle |1> 300 us (P300) | {lab} | median'] = np.median(p300[g])
    out['_n'] = int(g.sum()); out['_n_typ'] = int((g & (proj['R300'] > 0.1) & (proj['R300'] < 0.9)).sum()); out['_n8'] = int(g8.sum())
    return out


def boot(fn, A, rng):
    B = []
    for _ in range(NB):
        B.append(fn({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}))
    return {k: np.nanstd([b[k] for b in B]) for k in B[0] if not k.startswith('_')}


def three(vals, widths):
    v = np.array(vals); w = np.array(widths); return v.mean(), np.sqrt((w ** 2).sum()) / len(v)


L = []; P = L.append
me = os.path.abspath(__file__); P(f'# script sha256 {sha(me)}')
JOBS = [('PUSH RUN, ibm_pittsburgh', 'ibm_pittsburgh', (91, 92, 93), push_job), ('HOLD RUN, ibm_pittsburgh', 'ibm_pittsburgh', (71, 72, 73), hold_job),
        ('PUSH REPLICATION, ibm_marrakesh', 'ibm_marrakesh', (141,), push_job), ('PUSH REPLICATION, ibm_kingston', 'ibm_kingston', (141,), push_job),
        ('INTERVAL-LENGTH JOB (run 121), ibm_pittsburgh', 'ibm_pittsburgh', (121,), noname_job)]
for title, chip, runs, fn in JOBS:
    rng = np.random.default_rng(20261003); per = []
    for r in runs:
        for f in (f'run{r}_meta.json', f'run{r}_results.npz'): P(f'# input sha256 {sha(os.path.join(FIRE, chip, f))}  {chip}/{f}')
        m, A = load(chip, r); s = fn(A); w = boot(fn, A, rng); per.append((r, m, s, w))
    P(''); P(f'== {title}: runs {list(runs)}; jobs ' + ', '.join(f"{m['job_id']} ({m['start_time'][11:19]})" for _, m, _, _ in per)
      + '; readable (sep>4) ' + '/'.join(str(s['_n']) for _, _, s, _ in per) + '; of them P300 in (0.1,0.9) ' + '/'.join(str(s['_n_typ']) for _, _, s, _ in per)
      + '; sep>8 ' + '/'.join(str(s['_n8']) for _, _, s, _ in per))
    for k in per[0][2]:
        if k.startswith('_'): continue
        vals = [s[k] for _, _, s, _ in per]; wds = [w[k] for _, _, _, w in per]
        if len(per) > 1:
            mn, wd = three(vals, wds)
            P(f'   {k:<70} ' + '  '.join(f'{v:+.4f}({w:.4f})' for v, w in zip(vals, wds)) + f'  | all {mn:+.4f}({wd:.4f})')
        else:
            P(f'   {k:<70} {vals[0]:+.4f}({wds[0]:.4f})')
    if fn is noname_job:   # chi2 over the ten arms for each book, stat = mean, proj
        s, w = per[0][2], per[0][3]
        for stt in STATS:
            row = []
            for bk in ('one', 'own', 'mix', 'long', 'once'):
                z = [s[f'{a} minus {bk} book | proj | {stt}'] / w[f'{a} minus {bk} book | proj | {stt}'] for a in NONAME]
                row.append(f'{bk} chi2 {np.sum(np.square(z)):7.1f}')
            P(f'   CHI2 over the ten arms (residual/width)^2, proj, statistic {stt:<6}: ' + ' | '.join(row) + '   (ten arms; widths are shot widths of the residual)')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
