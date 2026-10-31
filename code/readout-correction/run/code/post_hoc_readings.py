"""post_hoc_readings.py -- readings DEFINED AFTER THE DATA (after the results referee, 31 Oct), labelled as such wherever they appear.
(1) per-qubit scale of today's look kick against the committed 21 Oct table: Theil-Sen slope of today's pooled M kick (wrapped, N=8) on the
    committed unwrapped N=8 kick, 99 % bootstrap over qubits; and the share of qubits whose |kick| is smaller today.
(2) dose disagreement promised by the plan: committed N=4 vs N=8 kicks differing by more than 2 deg/readout (count of qubits), and the same for
    today's fresh table (job C).
(3) residual distance left above the shot floor, promised by the plan as a 'lost' reading: |E_X - E_none|^2 - floor for the clock, pooled.
(4) clock-qubit entries: committed N=4 kick vs fresh N=4 kick per clock qubit."""
import sys, os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, analyze_keystone as A, pooters as PW
from analyze import wrap
rng = np.random.default_rng(1031)
out = ['post_hoc_readings.py -- DEFINED AFTER THE DATA (31 Oct, after the results referee)']
for chip in ('ibm_kingston', 'ibm_marrakesh'):
    job = json.load(open(f'{HERE}/job_keystone_{chip}.json')); keys = [tuple(k) for k in job['keys']]
    Z = {lab: np.load(f'{HERE}/raw_keystone_{chip}_{lab}.npz') for lab in ('A', 'B')}
    T = K.table(chip); S = [int(q) for q in T['S']]; Kt = T['kicks_deg_per_readout']
    Zc = {(k[1], k[2]): [Z['A'][f'fin_{keys.index(k)}'], Z['B'][f'fin_{keys.index(k)}']] for k in keys if k[0] == 'S'}
    r = K.read_S(Zc, S, rng); today = r['M']['kick']; comm = np.array([Kt[str(q)][6] for q in S])
    f = lambda ix: A.theil_sen(comm[ix], today[ix]); v = f(np.arange(len(S))); bs = [f(rng.integers(0, len(S), len(S))) for _ in range(800)]
    lo, hi = np.percentile(bs, [0.5, 99.5]); smaller = float(np.mean(np.abs(today) < np.abs(comm)))
    out.append(f'{chip}: (1) per-qubit scale today/committed (Theil-Sen) {v:.3f} [{lo:.3f}, {hi:.3f}] (99 %); |kick| smaller today on {smaller:.0%} of the 117')
    d4 = np.array([Kt[str(q)][8] - Kt[str(q)][6] for q in S]); F = json.load(open(f'{HERE}/fresh_kicks_{chip}.json'))['kicks']
    f48 = np.array([F[str(q)]['k4'] - F[str(q)]['k8'] for q in S])
    out.append(f'   (2) dose: committed N=4 vs N=8 differ by > 2 deg/readout on {int(np.sum(np.abs(d4) > 2))} of 117; fresh table on {int(np.sum(np.abs(f48) > 2))} of 117')
    CC = {lab: {a: {st: K.counts3([Z[lab][f'fin_{keys.index(("C", a, st))}']]) for st in K.SET_C} for a in K.ARMS} for lab in ('A', 'B')}
    pooled = {a: {st: {k: CC['A'][a][st].get(k, 0) + CC['B'][a][st].get(k, 0) for k in set(CC['A'][a][st]) | set(CC['B'][a][st])} for st in K.SET_C} for a in K.ARMS}
    E = {a: PW.evec(PW.to_P(pooled[a]))[1:] for a in K.ARMS}
    EA = {a: PW.evec(PW.to_P(CC['A'][a]))[1:] for a in ('D', 'M')}; EB = {a: PW.evec(PW.to_P(CC['B'][a]))[1:] for a in ('D', 'M')}
    floor = (np.sum((EA['D'] - EB['D']) ** 2) + np.sum((EA['M'] - EB['M']) ** 2)) / 4
    dist = {a: float(np.sum((E[a] - E[K.NONE[a]]) ** 2)) for a in ('M', 'MC', 'MF', 'ME')}
    out.append(f'   (3) clock |E_X - E_none|^2 (pooled): ' + ', '.join(f'{a} {d:.3f}' for a, d in dist.items()) + f'; shot floor {floor:.3f}')
    c0, s, c1 = job['clock']
    out.append(f'   (4) clock entries, committed N=4 vs fresh N=4 kick (deg/readout): ' + ', '.join(f'q{q} {Kt[str(q)][8]:+.2f} vs {F[str(q)]["k4"]:+.2f}' for q in (c0, s, c1)))
open(f'{HERE}/results_post_hoc.text', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
