"""analyze_swap.py -- readings for the 2508.16895 swap run under PLAN_SWAP.md.text (scored: IDENT, ORTHO, THEIRS, COPY; the rest descriptive).
Usage: python -I analyze_swap.py > results_swap.text"""
import json, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from swaprun import *
from scipy.stats import spearmanr
if __name__ == '__main__':
    P = select(curves()); rec = json.load(open(f'{HERE}/job_swap.json')); raw = json.load(open(f'{HERE}/raw_swap.json'))
    F = np.full((len(P), 2), np.nan); N = np.zeros((len(P), 2))
    for r in raw: F[r['pair'], r['copy'] - 1], N[r['pair'], r['copy'] - 1] = fhat(r['counts'])
    for j in rec['jobs']: print(f"job {j['job_id']} attempt {j['attempt']} status {j['status']} submitted {j['submitted_utc']} usage {j.get('usage')} timestamps {j.get('timestamps')}")
    print(f"layouts (first pair) {rec['layouts'][0]}; depth {min(rec['depth'])}-{max(rec['depth'])}; min shots per circuit {int(N.min())}")
    R = readings(P, F)
    for k in ('IDENT', 'ORTHO', 'THEIRS', 'COPY'):
        x = R[k]; print(f"SCORED {k:<6} value {x['value']:+.4f}  99 % [{x['lo']:+.4f}, {x['hi']:+.4f}] (half {x['half']:.4f}, n {x['n']}, scale {SCALE[k]})  -> {x['outcome']}")
    print('per pair (F^ copy 1, copy 2, exact):')
    for p, f in zip(P, F): print(f"  {p['cls']:>6} {p['A']:>3}-{p['B']:<3} exact {p['F']:.4f}  F^ {f[0]:.3f} {f[1]:.3f}  mean-exact {f.mean() - p['F']:+.4f}")
    ex = np.array([p['F'] for p in P]); cls = np.array([p['cls'] for p in P]); fm = F.mean(1); k = cls != 'ORTHO'
    print(f"DESCRIPTIVE (not scored): ratio F^/exact IDENT+THEIRS median {np.median(fm[k] / ex[k]):.4f}; spearman(F^, exact) over IDENT+THEIRS distinct pairs {spearmanr(fm[cls == 'THEIRS'], ex[cls == 'THEIRS']).statistic:+.4f} (12 THEIRS pairs)")
    print(f"DESCRIPTIVE: their 2025 identical-pair F^ (S/1000) median 0.853 over 76 (known_good_swap.text); today's IDENT mean {fm[cls == 'IDENT'].mean():.4f}")
