"""ghz_fill.py -- analysis. raw = {arm: counts} with population arms best_a, best_b, q25, q50, q75, unpinned (job A), best_jobB, unpinned_jobB (job B),
and parity arms par0..par7 (best path, job A).
  THEIRS  P per arm beside their 0.692 / 0.503.
  LAYOUT  weighted chi2 of P over best_a, q25, q50, q75 (dof 3): ABOVE if p < 0.05, else CONSISTENT (range a bound); range vs their 0.189.
  DRIFT   best_jobB - mean(best_a, best_b) and unpinned_jobB - unpinned, four outcomes with both widths (a bound at minute spacing).
  FIDELITY on the best path: F = (P + C)/2 vs their F = P; the gap P - F with its width.
  KNOWN-GOOD best_a vs best_b, identical in one job: |diff| < 2.58 sd (shot noise; same apparatus)."""
import numpy as np
from scipy import stats
from ghz import population, parity, coherence, PHIS
def cmp(a, b):
    d = a[0] - b[0]; s = float(np.hypot(a[1], b[1])); return dict(diff=d, sd=s, z=d / s, ci95=[d - 1.96 * s, d + 1.96 * s], outcome='ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
def analyse(raw):
    P = {k: population(v) for k, v in raw.items() if not k.startswith('par')}
    out = {'P': {k: dict(p=v[0], se=v[1]) for k, v in P.items()}, 'theirs': dict(run1=0.692, run2=0.503, delta=0.189)}
    kg = cmp(P['best_a'], P['best_b']); out['KNOWN_GOOD'] = dict(rule='best_a vs best_b identical in one job: |z| < 2.58', **kg, passed=bool(abs(kg['z']) < 2.58))
    L = ['best_a', 'q25', 'q50', 'q75']; p = np.array([P[a][0] for a in L]); s = np.array([P[a][1] for a in L]); w = 1 / s ** 2; m = (w * p).sum() / w.sum(); c2 = float((w * (p - m) ** 2).sum()); pv = float(stats.chi2.sf(c2, 3))
    out['LAYOUT'] = dict(P=[float(x) for x in p], range=float(p.max() - p.min()), share_of_their_0189=float((p.max() - p.min()) / 0.189), chi2=c2, p=pv, outcome='ABOVE (layout carries the number)' if pv < 0.05 else 'CONSISTENT (range is a bound)')
    mean_best = ((P['best_a'][0] + P['best_b'][0]) / 2, float(np.hypot(P['best_a'][1], P['best_b'][1]) / 2))
    out['DRIFT'] = dict(best=cmp(P['best_jobB'], mean_best), unpinned=cmp(P['unpinned_jobB'], P['unpinned']))
    par = [(f, *parity(raw['par%d' % i])) for i, f in enumerate(PHIS)]; C, sC = coherence(par); Pb = mean_best
    F = (Pb[0] + C) / 2; sF = float(np.hypot(Pb[1], sC) / 2)
    out['FIDELITY'] = dict(P_best=Pb[0], C=C, C_se=sC, F=F, F_se=sF, P_minus_F=Pb[0] - F, P_minus_F_se=float(np.hypot(Pb[1], sC) / 2), parity=[dict(phi=f, mean=m_, se=e) for f, m_, e in par])
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
