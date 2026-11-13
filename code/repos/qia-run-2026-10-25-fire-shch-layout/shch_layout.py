"""shch_layout.py -- second free calibration run for Zenodo 22770646 (Shcherbak): is LAYOUT the carrier of their 0.31 S spread?
Run 1 (25 Oct, layout pinned) bounded drift within a chip at 0.06. Their notebook pins no layout (least_busy, opt 1).
This run: one fez job, their circuit on four triples fixed by rule before the job (best, 25th, 50th, 75th percentile of record quality), best twice (KG)."""
import json, numpy as np
from shch import S_of, circuits, SHOTS
ARMS = ['best_a', 'best_b', 'q25', 'q50', 'q75']
def analyse(raw):
    out = {}
    for a in ARMS:
        S, se, E = S_of(raw[a][:4]); Sp, sep, _ = S_of(raw[a][4:]); out[a] = dict(S=S, se=se, S_product=Sp)
    d = out['best_a']['S'] - out['best_b']['S']; sd = float(np.hypot(out['best_a']['se'], out['best_b']['se']))
    out['KNOWN_GOOD'] = dict(rule='best layout run twice in one job: copies agree within 2.58 se, and every product arm S + 1.96 se < 2', copy_diff=d, copy_sd=sd,
                             passed=bool(abs(d) < 2.58 * sd and all(out[a]['S_product'] + 1.96 * 0.02 < 2.0 for a in ARMS)))
    L = ['best_a', 'q25', 'q50', 'q75']; Ss = np.array([out[a]['S'] for a in L]); ses = np.array([out[a]['se'] for a in L])
    w = 1 / ses ** 2; m = (w * Ss).sum() / w.sum(); chi2 = float((w * (Ss - m) ** 2).sum())
    from scipy import stats
    p = float(stats.chi2.sf(chi2, len(L) - 1)); rng_ = float(Ss.max() - Ss.min())
    out['LAYOUT'] = dict(S=[float(x) for x in Ss], range=rng_, chi2=chi2, dof=len(L) - 1, p=p, their_spread=0.3138, drift_bound_run1=0.06,
                         outcome='ABOVE (layout spread resolves)' if p < 0.05 else 'CONSISTENT (no layout spread beyond shot noise; a bound)',
                         share_of_their_spread=rng_ / 0.3138)
    return out
