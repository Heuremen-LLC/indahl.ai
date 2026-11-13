"""ffzne_fill.py -- analysis. ev = {arm: (<Z>, std)}; scores from layouts_chosen.json.
  THEIRS  FF-ZNE as they run it: linear fit of <Z> vs score over (s1_a, mid, worst), extrapolated to score 0 -> E0; deviation |1 - E0|.
  LINEAR  weighted linear fit of <Z> vs score over the five distinct layouts (s1_a, q25, mid, q75, worst): chi2 on 3 dof. ABOVE (the record score is
          not a linear carrier of the delivered value; p < 0.05) / CONSISTENT (a bound).
  PAIR    mid vs q75: near-equal scores (0.373 / 0.381), different qubits; their <Z> difference minus the 5-point slope's prediction, both widths.
  ALT     the same extrapolation from the other two triples drawn from our five (s1, q25, q75) and (q25, mid, worst): spread of E0.
  DRIFT   job B s1 - mean(s1_a, s1_b).
  KNOWN-GOOD s1_a vs s1_b identical in one job: |diff| < 2.58 sd."""
import numpy as np
from scipy import stats
def fit(xs, ys, ss):
    X = np.column_stack([np.ones(len(xs)), xs]); W = np.diag(1 / np.array(ss) ** 2); cov = np.linalg.inv(X.T @ W @ X); b = cov @ X.T @ W @ np.array(ys)
    r = np.array(ys) - X @ b; c2 = float(r @ W @ r); return b, cov, c2
def cmp(a, b):
    d = a[0] - b[0]; s = float(np.hypot(a[1], b[1])); return dict(diff=d, sd=s, z=d / s, outcome='ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
def analyse(ev, sc):
    out = {'ev': {k: dict(Z=v[0], std=v[1]) for k, v in ev.items()}, 'scores': sc}
    kg = cmp(ev['s1_a'], ev['s1_b']); out['KNOWN_GOOD'] = dict(rule='s1_a vs s1_b identical in one job: |z| < 2.58', **kg, passed=bool(abs(kg['z']) < 2.58))
    def e0(arms):
        b, cov, c2 = fit([sc[a.split('_')[0]] for a in arms], [ev[a][0] for a in arms], [ev[a][1] for a in arms]); return dict(arms=arms, E0=float(b[0]), E0_se=float(np.sqrt(cov[0, 0])), slope=float(b[1]), dev_from_1=float(abs(1 - b[0])), chi2=c2)
    out['THEIRS'] = e0(['s1_a', 'mid', 'worst'])
    five = ['s1_a', 'q25', 'mid', 'q75', 'worst']; b, cov, c2 = fit([sc[a.split('_')[0]] for a in five], [ev[a][0] for a in five], [ev[a][1] for a in five]); p = float(stats.chi2.sf(c2, 3))
    out['LINEAR'] = dict(E0=float(b[0]), slope=float(b[1]), chi2=c2, dof=3, p=p, outcome='ABOVE (record score is not a linear carrier)' if p < 0.05 else 'CONSISTENT (linear within widths; a bound)')
    pr_ = b[1] * (sc['mid'] - sc['q75']); d = ev['mid'][0] - ev['q75'][0] - pr_; s = float(np.hypot(ev['mid'][1], ev['q75'][1]))
    out['PAIR'] = dict(diff_minus_slope_prediction=d, sd=s, z=d / s, outcome='ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
    out['ALT'] = [e0(['s1_a', 'q25', 'q75']), e0(['q25', 'mid', 'worst'])]; E = [out['THEIRS']['E0']] + [a['E0'] for a in out['ALT']]; out['E0_spread'] = float(max(E) - min(E))
    mb = ((ev['s1_a'][0] + ev['s1_b'][0]) / 2, float(np.hypot(ev['s1_a'][1], ev['s1_b'][1]) / 2)); out['DRIFT'] = cmp(ev['s1_jobB'], mb)
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
