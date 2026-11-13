#!/usr/bin/env python3
"""park_per_qubit.py -- THE PARK, qubit by qubit, from the raw jobs on disk (ibm_pittsburgh). No hardware contact.
Reads (read-only):  parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh/run{71,72,73,81}_{meta.json,results.npz}
                    parallax/out/qubit_fifth_run/data/reads/witness_roles.json
Writes only:        darkwave_disco/internal/reads_new/park_per_qubit.txt
Steps copied from the frozen readers, not imported: frame() and resample() from code/readclose.py, book() from code/readhold.py.
One change from code/readhold.py:35: the bookkeeping is made for EACH qubit from that qubit's own nothing-done arm,
not once for the median qubit. Every number names its clock: LAID (laid time), WITNESS (a spectator), OWN (the qubit's own decay)."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
ROLES = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/witness_roles.json'
OUT = os.path.join(HERE, 'park_per_qubit.txt')
NB = 100; SEED = 20261003; TOL = 0.002; SEP = 4.0
HOLD = (71, 72, 73); STOP = 81
SCHEMES = (('P1', 2, 'parked once      (2 x 150 us LAID)'), ('P3', 4, 'alternate quarters (4 x 75 us LAID)'), ('P9', 10, 'alternate tenths   (10 x 30 us LAID)'))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load(r):
    m = json.load(open(os.path.join(RAW, f'run{r}_meta.json')))
    if m.get('complete') is not True: raise SystemExit(f'run {r} not complete')
    z = np.load(os.path.join(RAW, f'run{r}_results.npz'))
    return m, {k: np.asarray(z[k]).astype(complex) for k in z.files}


def resample(A, rng):                      # readclose.py: one shot draw per circuit, shared by that circuit's registers
    out, idx = {}, {}
    for k, v in A.items():
        b = k.split('__')[0]
        if b not in idx: idx[b] = rng.integers(0, v.shape[0], v.shape[0])
        out[k] = v[idx[b]]
    return out


def frame(A, off, on):                     # readclose.py: OFF -> 0, ON -> 1 along the line; separation in cloud widths
    c0 = A[off].mean(0); d = A[on].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[off] - c0) ** 2).mean(0) / 2)


def book(p300, nseg):                      # readhold.py book(): fade one stretch (ON -> OFF with chance 1 - q), then the push swaps; start ON
    q = p300 ** (1.0 / nseg); on, off = np.ones_like(q), np.zeros_like(q)
    for _ in range(nseg): on, off = off + on * (1 - q), on * q
    return on


def hold_d(A):
    al, sep = frame(A, 'OFF|w0__L1', 'ON|w0__L1')
    lv = {k: al(A[k + '__L1']).mean(0) for k in ('ON|N0', 'ON|P1', 'ON|P3', 'ON|P9')}
    p300 = np.clip(lv['ON|N0'], 0.02, 0.98)
    return {s: lv['ON|' + s] - book(p300, n) for s, n, _ in SCHEMES}, sep, lv


def stop_d(A, EM):
    al, sep = frame(A, 'F0__L1', 'F1__L1')
    lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
    out = {}
    for yname, Y in (('B1', lv['B1']), ('A3', (lv['A3|X'] + lv['A3|Y']) / 2)):
        y = np.clip(Y[EM], 0.02, 0.98); q20, q40 = y ** (1 / 3), y ** (2 / 3)
        out[('20', yname)] = (lv['A1|X'] + lv['A1|Y'])[EM] / 2 - (1 - q20) * q40
        out[('40', yname)] = (lv['A2|X'] + lv['A2|Y'])[EM] / 2 - (1 - q40) * q20
    return out, sep[EM], lv


def stats(d, g):
    x = d[g]
    return np.array([x.mean(), np.median(x), np.percentile(x, 25), np.percentile(x, 75), np.mean(np.abs(x) <= TOL)])


def three(vals, widths):                   # readclose.py three(): mean, sqrt(sum w^2)/3, each minus the other two
    v = np.array(vals); w = np.array(widths)
    return v.mean(), np.sqrt((w ** 2).sum()) / len(v), [v[i] - np.mean(np.delete(v, i)) for i in range(len(v))]


L = []; P = L.append
me = os.path.abspath(__file__)
P(f'# script sha256 {sha(me)}  {os.path.relpath(me, "/Users/heuremen/bones-forge/parallax")}')
for r in HOLD + (STOP,):
    for f in (f'run{r}_meta.json', f'run{r}_results.npz'): P(f'# input  sha256 {sha(os.path.join(RAW, f))}  out/qubit_fifth_run/data/fire/ibm_pittsburgh/{f}')
P(f'# input  sha256 {sha(ROLES)}  out/qubit_fifth_run/data/reads/witness_roles.json')
M = {r: load(r) for r in HOLD + (STOP,)}
hdr = '; '.join(f"run {r} job {M[r][0]['job_id']} started {M[r][0]['start_time'][11:19]} EDT, results read {M[r][0]['result_read_at'][11:19]} EDT, {M[r][0]['shots']} shots" for r in HOLD)
P(f'THE PARK, QUBIT BY QUBIT -- ibm_pittsburgh hold run (runs 71/72/73: {hdr}) and stopwatch run 81 (job {M[STOP][0]["job_id"]}, '
  f'started {M[STOP][0]["start_time"][11:19]} EDT, results read {M[STOP][0]["result_read_at"][11:19]} EDT, {M[STOP][0]["shots"]} shots). Script: reads_new/park_per_qubit.py.')
P(f'Clock key: LAID = laid time (the intervals we schedule); OWN = the qubit\'s own decay (here: its own 300-us nothing-done survival in the same job); WITNESS = a spectator. '
  f'Widths: {NB} bootstrap resamples of shots (seed {SEED}), frame and readable set redrawn each time, as code/readclose.py. Readable = cloud separation > {SEP:g} widths.')
P('')
P('== 1. HOLD RUN, start ON, 300 us LAID, X after every interval (alternate intervals spent in |0>); last look.')
P('   d = measured level minus bookkeeping, PER QUBIT. Bookkeeping [OWN]: that qubit\'s nothing-done level after 300 us, cut into the LAID intervals; ')
P('   relaxation only while in |1>; what relaxed is put back by the next X and relaxes again (code/readhold.py book()).')
P(f'   columns: mean over qubits | median | quartiles | share of qubits with |d| <= {TOL} | middle per-qubit shot width of d   [all OWN, intervals LAID]')
rng = np.random.default_rng(SEED)
per = {}; dq = {}; widthq = {}
for r in HOLD:
    m, A = M[r]
    d, sep, lv = hold_d(A); g = sep > SEP
    boots = []; bq = {s: [] for s, _, _ in SCHEMES}
    for _ in range(NB):
        B = resample(A, rng); db, sb, _ = hold_d(B); gb = sb > SEP
        boots.append({s: stats(db[s], gb) for s, _, _ in SCHEMES})
        for s, _, _ in SCHEMES: bq[s].append(db[s])
    per[r] = {s: (stats(d[s], g), np.std([b[s] for b in boots], axis=0)) for s, _, _ in SCHEMES}
    dq[r] = (d, g); widthq[r] = {s: np.std(bq[s], axis=0) for s, _, _ in SCHEMES}
    P(f'   -- run {r} ({int(g.sum())} readable of {len(g)})')
    for s, n, name in SCHEMES:
        v, w = per[r][s]
        P(f'      {name}: mean {v[0]:+.4f} +- {w[0]:.4f} | median {v[1]:+.4f} +- {w[1]:.4f} | quartiles [{v[2]:+.4f}, {v[3]:+.4f}] | within {TOL}: {v[4]:.3f} +- {w[4]:.3f} | shot width {np.median(widthq[r][s][g]):.4f}   [OWN, intervals LAID]')
P('   -- all three reads (mean of the three; width sqrt(sum w^2)/3; each read minus the other two)')
for s, n, name in SCHEMES:
    row = []
    for j, lab in ((0, 'mean'), (1, 'median'), (4, f'share within {TOL}')):
        mn, wd, oth = three([per[r][s][0][j] for r in HOLD], [per[r][s][1][j] for r in HOLD])
        row.append(f'{lab} {mn:+.4f} +- {wd:.4f} [{" ".join(f"{x:+.4f}" for x in oth)}]')
    P(f'      {name}: ' + ' | '.join(row) + '   [OWN, intervals LAID]')
P('   -- each qubit averaged over the three reads (qubits readable in all three), then across qubits')
gall = dq[71][1] & dq[72][1] & dq[73][1]
for s, n, name in SCHEMES:
    davg = np.mean([dq[r][0][s] for r in HOLD], axis=0)
    wq = np.sqrt(sum(widthq[r][s] ** 2 for r in HOLD)) / 3
    v = stats(davg, gall)
    P(f'      {name}: {int(gall.sum())} qubits | mean {v[0]:+.4f} | median {v[1]:+.4f} | quartiles [{v[2]:+.4f}, {v[3]:+.4f}] | within {TOL}: {v[4]:.3f} | middle per-qubit width of the three-read average {np.median(wq[gall]):.4f}   [OWN, intervals LAID]')
P('   -- RULER ROW: the frozen reader\'s median-qubit version (code/readhold.py:35; all 156 qubits, no cut), recomputed here; it should print reads/hold_run.txt:21-23')
for s, n, name in SCHEMES:
    vals = []
    for r in HOLD:
        _, A = M[r]; al, _ = frame(A, 'OFF|w0__L1', 'ON|w0__L1')
        n0 = float(np.median(al(A['ON|N0__L1']).mean(0))); ms = float(np.median(al(A[f'ON|{s}__L1']).mean(0)))
        q = n0 ** (1.0 / n); on, off = 1.0, 0.0
        for _ in range(n): on, off = off + on * (1 - q), on * q
        vals.append((on, ms))
    P(f'      {name}: bookkeeping ' + ' '.join(f'{b:.4f}' for b, _ in vals) + '   measured ' + ' '.join(f'{x:.4f}' for _, x in vals) + '   difference ' + ' '.join(f'{x - b:+.4f}' for b, x in vals) + '   [OWN, median qubit]')
P('')
roles = json.load(open(ROLES)); EM = np.array(sorted(roles['emitters']), int)
m, A = M[STOP]
d, sepE, lv = stop_d(A, EM); gE = sepE > SEP
boots = []; rngS = np.random.default_rng(SEED + 1)
for _ in range(NB):
    B = resample(A, rngS); db, sb, _ = stop_d(B, EM); gb = sb > SEP
    boots.append({k: stats(db[k], gb) for k in d})
P(f'== 2. STOPWATCH RUN 81 (one job), the {len(EM)} emitters: ON for 20 or 40 us LAID, then X to |0> for the rest of a 60-us LAID window; last look.')
P('   d = the emitter\'s level (mean of the X-hand and Y-hand circuits) minus bookkeeping (1 - q20) q40 or (1 - q40) q20, with q_t = Y^(t/60) PER EMITTER.')
P('   Yardstick Y [OWN]: B1 = that emitter ON for 60 us with its neighbours in |0> (as the ledger, §134); A3 = ON for 60 us with its neighbours running as spectators (the parked arms\' own neighbour state).')
P(f'   {int(gE.sum())} readable emitters of {len(EM)}.')
for (t, y), lab in ((('20', 'B1'), 'parked after 20 us, yardstick B1'), (('40', 'B1'), 'parked after 40 us, yardstick B1'), (('20', 'A3'), 'parked after 20 us, yardstick A3'), (('40', 'A3'), 'parked after 40 us, yardstick A3')):
    v = stats(d[(t, y)], gE); w = np.std([b[(t, y)] for b in boots], axis=0)
    P(f'      {lab}: mean {v[0]:+.4f} +- {w[0]:.4f} | median {v[1]:+.4f} +- {w[1]:.4f} | quartiles [{v[2]:+.4f}, {v[3]:+.4f}] | within {TOL}: {v[4]:.3f} +- {w[4]:.3f}   [OWN, intervals LAID]')
med = lambda key: float(np.median(lv[key][EM]))
y = med('B1'); q20, q40 = y ** (1 / 3), y ** (2 / 3)
P(f'   -- RULER ROW (median emitter, all {len(EM)}, as code/readwitness.py and ledger §134): yardstick B1 {y:.4f}; measured {(med("A1|X") + med("A1|Y")) / 2:.4f} and {(med("A2|X") + med("A2|Y")) / 2:.4f}; '
  f'bookkeeping {(1 - q20) * q40:.4f} and {(1 - q40) * q20:.4f}   [OWN]')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
