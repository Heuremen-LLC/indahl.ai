#!/usr/bin/env python3
"""J3p (PLAN Addendum 4, committed before this ran, defined after the data): order-free mixed-pairing baseline and its excess. Our code."""
import os, json
import numpy as np
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'multipref', 'MultiPref-Train.jsonl')
def lab(a):
    p = a.get('overall_pref') or ''
    return 'A' if p.startswith('A') else ('B' if p.startswith('B') else ('T' if p.startswith('Tie') else None))
X = []; IDS = []
for l in open(F):
    if not l.strip(): continue
    r = json.loads(l); c = [lab(a) for a in r['normal_worker_annotations']]; e = [lab(a) for a in r['expert_worker_annotations']]
    if len(c) == 2 and len(e) == 2 and None not in c + e:
        X.append(c + e); IDS.append([a['evaluator'] for a in r['normal_worker_annotations'] + r['expert_worker_annotations']])
X = np.array(X); n = len(X); c0, c1, e0, e1 = X.T
opp = lambda x, y: ((x == 'A') & (y == 'B')) | ((x == 'B') & (y == 'A'))
ka = (c0 == c1) & (e0 == e1); k1 = (c0 == e0) & (c1 == e1); k2 = (c0 == e1) & (c1 == e0)
M = np.stack([ka, ka & (c0 != e0), ka & opp(c0, e0), k1 | False, k1 & (c0 != c1), k1 & opp(c0, c1), k2, k2 & (c0 != c1), k2 & opp(c0, c1)], 1).astype(float)
def st(W):
    s = W @ M; pk = s[:, 3] + s[:, 6]
    return np.stack([s[:, 1] / s[:, 0], s[:, 2] / s[:, 0], (s[:, 4] + s[:, 7]) / pk, (s[:, 5] + s[:, 8]) / pk], 1)
f = st(np.ones((1, n)))[0]; s = M.sum(0)
print('comparisons %d | actual pools: kept %d, differ %d = %.1f%%, opposite %d = %.1f%%' % (n, s[0], s[1], 100 * f[0], s[2], 100 * f[1]))
print('J3p both mixed pairings pooled: kept %d, differ %d = %.1f%%, opposite %d = %.1f%%' % (s[3] + s[6], s[4] + s[7], 100 * f[2], s[5] + s[8], 100 * f[3]))
print('  four-way agreement (all four annotators unanimous): %d; comparisons split two against two: %d' % (int(((c0 == c1) & (c1 == e0) & (e0 == e1)).sum()), int(((ka | k1 | k2) & ~((c0 == c1) & (c1 == e0) & (e0 == e1))).sum())))
rng = np.random.default_rng(42); bs = st(rng.poisson(1.0, size=(4000, n)).astype(float))
ex = bs[:, [0, 1]] - bs[:, [2, 3]]; e = f[[0, 1]] - f[[2, 3]]; se = ex.std(0, ddof=1)
ids = sorted(set(np.ravel(IDS))); ix = {g: i for i, g in enumerate(ids)}; A = np.array([[ix[g] for g in r] for r in IDS]); G = len(ids)
on = np.zeros((n, G), bool)
for j in range(4): on[np.arange(n), A[:, j]] = True
th = st((~on.T).astype(float)); tx = th[:, [0, 1]] - th[:, [2, 3]]; jk = np.sqrt((G - 1) / G * ((tx - tx.mean(0)) ** 2).sum(0))
for k, nm in enumerate(('differ', 'opposite')):
    print('  excess %s: %+.2f pp | comparison bootstrap SE %.2f, +-1.96 SE [%+.1f, %+.1f] | jackknife (upper width) SE %.2f, [%+.1f, %+.1f]' % (nm, 100 * e[k], 100 * se[k], 100 * (e[k] - 1.96 * se[k]), 100 * (e[k] + 1.96 * se[k]), 100 * jk[k], 100 * (e[k] - 1.96 * jk[k]), 100 * (e[k] + 1.96 * jk[k])))
