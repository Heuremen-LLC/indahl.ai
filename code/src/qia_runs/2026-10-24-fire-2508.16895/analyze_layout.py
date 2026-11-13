"""analyze_layout.py -- ADDENDUM 2 readings (post-hoc, descriptive; same reading() band as the plan): per arm IDENT / THEIRS deviation from exact, and the paired arm gap L2 - L1 over the 16 non-ORTHO pairs."""
import json, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from swaprun import *
T99[15] = 2.947   # t(15) two-sided 99 % (scipy t.ppf(0.995, 15)); swaprun.py left unchanged
def gap_reading(f1, f2, pairs):
    k = np.array([p['cls'] != 'ORTHO' for p in pairs]); var = ((1 - f1 ** 2) + (1 - f2 ** 2)) / SHOTS
    return reading((f2 - f1)[k], var[k], SHOTS, 0.10)
if __name__ == '__main__':
    P = select(curves()); rec = json.load(open(f'{HERE}/job_layout.json')); raw = json.load(open(f'{HERE}/raw_layout.json'))
    F = {'L1': np.zeros(len(P)), 'L2': np.zeros(len(P))}
    for r in raw: F[r['arm']][r['pair']] = fhat(r['counts'])[0]
    for j in rec['jobs']: print(f"job {j['job_id']} status {j['status']} submitted {j['submitted_utc']} usage {j.get('usage')} timestamps {j.get('timestamps')}")
    ex = np.array([p['F'] for p in P]); cls = np.array([p['cls'] for p in P])
    for nm in ('L1', 'L2'):
        for c in ('IDENT', 'ORTHO', 'THEIRS'):
            k = cls == c; x = reading(F[nm][k] - ex[k], (1 - F[nm][k] ** 2) / SHOTS, SHOTS, SCALE[c])
            print(f"{nm} {c:<6} value {x['value']:+.4f} 99 % [{x['lo']:+.4f}, {x['hi']:+.4f}] -> {x['outcome']}")
    g = gap_reading(F['L1'], F['L2'], P); print(f"GAP L2 - L1 (16 non-ORTHO pairs) {g['value']:+.4f} 99 % [{g['lo']:+.4f}, {g['hi']:+.4f}] -> {g['outcome']}")
    from scipy.stats import spearmanr
    for nm in ('L1', 'L2'): print(f"{nm} spearman(F^, exact) 12 THEIRS {spearmanr(F[nm][cls == 'THEIRS'], ex[cls == 'THEIRS']).statistic:+.4f}; IDENT mean F^ {F[nm][cls == 'IDENT'].mean():.4f}; ratio F^/exact non-ORTHO median {np.median(F[nm][cls != 'ORTHO'] / ex[cls != 'ORTHO']):.4f}")
    for p, a, b2 in zip(P, F['L1'], F['L2']): print(f"  {p['cls']:>6} {p['A']:>3}-{p['B']:<3} exact {p['F']:.4f}  L1 {a:.3f}  L2 {b2:.3f}")
