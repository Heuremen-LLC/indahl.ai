"""vqc_fill.py -- analysis. raw = {arm: [84 counts dicts]}; arms theirs_a, theirs_b (their physical [144,143,142,141]), best, q50, q75 (job A),
theirs_jobB (job B). p_exact from the vendored circuit (rebuilds theirs to 1e-15).
Per arm: accuracy and label agreement vs exact (descriptive, with Wilson), and the contraction lam from p_b - 1/2 = lam (p_e - 1/2) (weighted LS,
per-row binomial widths, with an offset c): lam = 1 means the chip delivers the exact probabilities, lam < 1 shrinks them toward 1/2 (what flips labels).
LAYOUT: chi2 of lam over theirs_a, best, q50, q75 (dof 3): ABOVE if p < 0.05, else CONSISTENT (range a bound).
DRIFT: lam(theirs_jobB) - mean lam(theirs_a, theirs_b), four outcomes.
THEIRS: accuracy drop vs exact on their placement today beside their 0.048 (10 Oct), and the layout range in accuracy beside their encoding gap
(exact z1 0.893 vs exact zz2 0.643 on the same 84 = 0.25).
KNOWN-GOOD: theirs_a vs theirs_b identical in one job: |lam diff| < 2.58 sd."""
import numpy as np
from scipy import stats
from vqc import p1_counts
def wil(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [float(c - h), float(c + h)]
def lam(pb, pe, n=1024):
    """weighted LS of p_b - 1/2 = c + lam (p_e - 1/2); returns lam, se_lam, c, se_c (widths floored at reduced chi2 >= 1)."""
    X = np.column_stack([np.ones(len(pe)), pe - 0.5]); yv = pb - 0.5; w = 1 / (np.clip(pb * (1 - pb), 1e-4, None) / n)
    A = X.T @ (w[:, None] * X); b = np.linalg.solve(A, X.T @ (w * yv)); r = yv - X @ b; s2 = max(float((w * r * r).sum() / (len(pe) - 2)), 1.0)
    cov = np.linalg.inv(A) * s2; return float(b[1]), float(np.sqrt(cov[1, 1])), float(b[0]), float(np.sqrt(cov[0, 0]))
def analyse(raw, pe, y):
    out = {'arms': {}}; L = {}; C = {}
    for a, cs in raw.items():
        pb = np.array([p1_counts(c) for c in cs]); l, se, c0, sc0 = lam(pb, pe); L[a] = (l, se); C[a] = (c0, sc0)
        acc = int(((pb >= .5) == y).sum()); agr = int(((pb >= .5) == (pe >= .5)).sum())
        out['arms'][a] = dict(lam=l, lam_se=se, offset=c0, offset_se=sc0, accuracy=acc / len(y), acc_wilson=wil(acc, len(y)), agreement=agr / len(y), mean_abs_dev=float(np.abs(pb - pe).mean()))
    def cmp(a, b):
        d = a[0] - b[0]; s = float(np.hypot(a[1], b[1])); return dict(diff=d, sd=s, z=d / s, outcome='ABOVE' if d - 1.96 * s > 0 else 'BELOW' if d + 1.96 * s < 0 else 'CONSISTENT')
    kg = cmp(L['theirs_a'], L['theirs_b']); out['KNOWN_GOOD'] = dict(rule='theirs_a vs theirs_b identical in one job: |z| < 2.58 on lam', **kg, passed=bool(abs(kg['z']) < 2.58))
    A = ['theirs_a', 'best', 'q50', 'q75']; l = np.array([L[a][0] for a in A]); s = np.array([L[a][1] for a in A]); w = 1 / s ** 2; m = (w * l).sum() / w.sum(); c2 = float((w * (l - m) ** 2).sum()); pv = float(stats.chi2.sf(c2, 3))
    accs = [out['arms'][a]['accuracy'] for a in A]
    cc = np.array([C[a][0] for a in A]); cs_ = np.array([C[a][1] for a in A]); wc = 1 / cs_ ** 2; mc = (wc * cc).sum() / wc.sum(); c2c = float((wc * (cc - mc) ** 2).sum())
    out['LAYOUT_OFFSET'] = dict(offset=[float(x) for x in cc], chi2=c2c, p=float(stats.chi2.sf(c2c, 3)))
    out['LAYOUT'] = dict(lam=[float(x) for x in l], chi2=c2, p=pv, outcome='ABOVE (layout carries the number)' if pv < 0.05 else 'CONSISTENT (range is a bound)',
                         accuracy=accs, accuracy_range=float(max(accs) - min(accs)), their_encoding_gap=0.25)
    mb = ((L['theirs_a'][0] + L['theirs_b'][0]) / 2, float(np.hypot(L['theirs_a'][1], L['theirs_b'][1]) / 2)); out['DRIFT'] = cmp(L['theirs_jobB'], mb)
    ex = float(((pe >= .5) == y).mean()); out['THEIRS'] = dict(exact_accuracy=ex, today_drop=ex - (out['arms']['theirs_a']['accuracy'] + out['arms']['theirs_b']['accuracy']) / 2, their_drop_10oct=0.0476)
    if not out['KNOWN_GOOD']['passed']: out['VERDICT'] = 'NOT DECIDED: known-good failed'
    return out
