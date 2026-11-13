#!/usr/bin/env python3
"""slopes.py: the damping slope of each of Boussahi's hardware circuits, recomputed from his stored shots and his stored exact correlators with my own code.
His code was never executed. Reads theirs/ only. Method as his paper states it: slope = <c_hw, c_exact> / <c_exact, c_exact> over the m = 800 correlators, c_hw from the three settings X, Y, Z of the 13-qubit chain.
Correlator set (his definition): weight-3 same-letter Paulis, ordered assignment: family-major (X, Y, Z), subsets of the 13 qubits in lexicographic order, the first m = 800 of 3 x 286 = 858."""
import os, sys, json, csv
from itertools import combinations
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); T = H + '/theirs'
N, K, M = 13, 3, 800
def fwht(a):
    a = np.array(a, dtype=np.float64, copy=True); h = 1; n = a.shape[-1]
    while h < n:
        a = a.reshape(a.shape[:-1] + (n // (2 * h), 2, h)); x = a[..., 0, :].copy(); y = a[..., 1, :]; a[..., 0, :] = x + y; a[..., 1, :] = x - y; a = a.reshape(a.shape[:-3] + (n,)) if False else a.reshape(a.shape[:-3] + (n,)); h *= 2
    return a
def cset():
    masks = np.array([sum(1 << q for q in s) for s in combinations(range(N), K)], dtype=np.int64)
    fam = np.repeat(np.arange(3), len(masks)); mask = np.tile(masks, 3); return fam[:M], mask[:M]
FAM, MASK = cset()
def correlators(per):
    """per: dict setting -> array of outcome integers (qubit 0 is the lowest bit)."""
    p = np.zeros((3, 1 << N))
    for b, s in enumerate('XYZ'):
        v = np.bincount(per[s].astype(np.int64), minlength=1 << N).astype(np.float64); p[b] = v / v.sum()
    par = np.stack([fwht(p[b]) for b in range(3)])
    return par[FAM, MASK]
def main():
    jobs = json.load(open(T + '/e14/jobs.json')); ref = {}
    for r in csv.DictReader(open(T + '/e14/analysis.csv')): ref[(r['job_id'], r['graph'], r['ansatz'], r['recipe'], int(r['seed']))] = r
    worst, n_ok, n = 0.0, 0, 0; out = []
    for rec in jobs:
        f = T + '/e14/shots_%s.npz' % rec['job_id']
        if not os.path.exists(f): continue
        sh = np.load(f); groups = {}
        for i, m in enumerate(rec['pubs']): groups.setdefault((m['graph'], m['ansatz'], m['recipe'], m['seed']), {})[m['setting']] = sh['pub%d' % i]
        for (g, a, rcp, seed), per in groups.items():
            if a != 'native': continue
            th = np.load(T + '/theta/%s_native_%s.npz' % (g, rcp)); c = th['c_exact'][seed][:M]
            ch = correlators(per); slope = float(ch @ c / (c @ c)); key = (rec['job_id'], g, a, rcp, seed)
            if key not in ref: continue
            mine = dict(job=rec['job_id'], graph=g, recipe=rcp, seed=seed, slope=slope, theirs=float(ref[key]['slope']), diff=slope - float(ref[key]['slope']))
            fam = FAM; sb = {}
            for b, lab in enumerate('XYZ'):
                sel = fam == b; sb[lab] = float(ch[sel] @ c[sel] / (c[sel] @ c[sel])); mine['theirs_' + lab] = float(ref[key]['slope_' + lab]); mine['slope_' + lab] = sb[lab]
            mine['resid_sd'] = float(np.std(ch - slope * c)); mine['theirs_resid_sd'] = float(ref[key]['resid_sd']); mine['sign_agree'] = float(np.mean(np.sign(ch) == np.sign(c))); mine['theirs_sign_agree'] = float(ref[key]['sign_agree'])
            out.append(mine); n += 1; worst = max(worst, abs(mine['diff']), max(abs(mine['slope_' + l] - mine['theirs_' + l]) for l in 'XYZ')); n_ok += int(abs(mine['diff']) < 5e-4)
    json.dump(out, open(H + '/slopes_reproduced.json', 'w'), indent=1)
    for o in out: print('%s %-4s %-12s seed %d  slope mine %.4f theirs %.4f  (X %.3f/%.3f Y %.3f/%.3f Z %.3f/%.3f)' % (o['job'][:6], o['graph'], o['recipe'], o['seed'], o['slope'], o['theirs'], o['slope_X'], o['theirs_X'], o['slope_Y'], o['theirs_Y'], o['slope_Z'], o['theirs_Z']))
    print('circuits %d, slope within 0.0005 of his printed value: %d, worst absolute difference over slope and its three basis slopes: %.6f' % (n, n_ok, worst))
if __name__ == '__main__': main()
