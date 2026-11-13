"""pav_fill.py -- analysis. raw = {arm: counts}. Arms (job A): best_a, best_b, q25, q50, q75 (opt 1), best_opt0, best_opt3. Job B: best_jobB (opt 1).
Readings:
  THEIRS   each arm's delivered P(1) vs their 0.125 (four outcomes, width 1.96 se) and vs 0.5 (their exclusion; reported as z)
  LAYOUT   weighted chi2 of P(1) over best_a, q25, q50, q75 (dof 3): ABOVE (layout carries the number, p < 0.05) / CONSISTENT (a bound: range printed)
  COMPILE  best_opt0 - best_a and best_opt3 - best_a, z with both widths: ABOVE/BELOW/CONSISTENT
  DRIFT    best_jobB - mean(best_a, best_b): job-to-job, z: ABOVE/BELOW/CONSISTENT (a bound)
  KNOWN-GOOD best_a vs best_b, identical in one job: |diff| < 2.58 sd (shot noise only; same apparatus, so scaled to itself)."""
import numpy as np
from scipy import stats
from pav import p1, wilson, four, IDEAL
LAY = ['best_a', 'q25', 'q50', 'q75']
def arm(c):
    p, n, k = p1(c); se = float(np.sqrt(max(p * (1 - p), 1e-12) / n)); return dict(p1=p, n=n, k=k, se=se, wilson=wilson(k, n))
def cmp(a, b):
    d = a['p1'] - b['p1']; s = float(np.hypot(a['se'], b['se'])); z = d / s
    return dict(diff=d, sd=s, z=z, ci95=[d - 1.96 * s, d + 1.96 * s], outcome='ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
def analyse(raw):
    A = {k: arm(v) for k, v in raw.items()}
    out = {'arms': A}
    out['THEIRS'] = {k: dict(vs_0125=four(v['p1'], v['se'], IDEAL, True), dev=v['p1'] - IDEAL, z_vs_050=(0.5 - v['p1']) / v['se']) for k, v in A.items()}
    kg = cmp(A['best_a'], A['best_b']); out['KNOWN_GOOD'] = dict(rule='best_a vs best_b identical in one job: |diff| < 2.58 sd', **kg, passed=bool(abs(kg['z']) < 2.58))
    P = np.array([A[a]['p1'] for a in LAY]); S = np.array([A[a]['se'] for a in LAY]); w = 1 / S ** 2; m = (w * P).sum() / w.sum(); c2 = float((w * (P - m) ** 2).sum())
    pv = float(stats.chi2.sf(c2, 3)); out['LAYOUT'] = dict(p1=[float(x) for x in P], range=float(P.max() - P.min()), chi2=c2, dof=3, p=pv,
        outcome='ABOVE (layout carries the number)' if pv < 0.05 else 'CONSISTENT (no layout spread beyond shot noise; range is a bound)')
    out['COMPILE'] = {k: cmp(A[k], A['best_a']) for k in ('best_opt0', 'best_opt3') if k in A}
    if 'best_jobB' in A:
        both = dict(p1=(A['best_a']['p1'] + A['best_b']['p1']) / 2, se=float(np.hypot(A['best_a']['se'], A['best_b']['se']) / 2)); out['DRIFT'] = cmp(A['best_jobB'], both)
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
