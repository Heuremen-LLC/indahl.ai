#!/usr/bin/env python3
"""Addendum 3 (committed e795929 before this ran, defined after the data): known-good for the annotator-aware rulers on J2b and J3. Our code."""
import os, json
import numpy as np
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'multipref', 'MultiPref-Train.jsonl')
def lab(a):
    p = a.get('overall_pref') or ''
    return 'A' if p.startswith('A') else ('B' if p.startswith('B') else ('T' if p.startswith('Tie') else None))
C, E, IC, IE = [], [], [], []
for l in open(F):
    if not l.strip(): continue
    r = json.loads(l); cw, ew = r['normal_worker_annotations'], r['expert_worker_annotations']
    c = [lab(a) for a in cw]; e = [lab(a) for a in ew]
    if len(c) != 2 or len(e) != 2 or None in c + e: continue
    C.append(c); E.append(e); IC.append([a['evaluator'] for a in cw]); IE.append([a['evaluator'] for a in ew])
C, E = np.array(C), np.array(E); n = len(C)
ne = lambda x, y: (x != y).astype(float); op = lambda x, y: (((x == 'A') & (y == 'B')) | ((x == 'B') & (y == 'A'))).astype(float)
c0, c1, e0, e1 = C[:, 0], C[:, 1], E[:, 0], E[:, 1]
M = np.stack([ne(c0, c1), ne(e0, e1), (ne(c0, e0) + ne(c0, e1) + ne(c1, e0) + ne(c1, e1)) / 4,
              op(c0, c1), op(e0, e1), (op(c0, e0) + op(c0, e1) + op(c1, e0) + op(c1, e1)) / 4], 1)
ka, k1, k2 = ((c0 == c1) & (e0 == e1)).astype(float), ((c0 == e0) & (c1 == e1)).astype(float), ((c0 == e1) & (c1 == e0)).astype(float)
S = np.stack([ka, ka * ne(c0, e0), ka * op(c0, e0), k1, k1 * ne(c0, c1), k1 * op(c0, c1), k2, k2 * ne(c0, c1), k2 * op(c0, c1)], 1)
NAMES = ['J2 differ cross-within', 'J2 reverse cross-within', 'J3 differ actual-split1', 'J3 differ actual-split2', 'J3 opposite actual-split1', 'J3 opposite actual-split2']
def stat(W):  # W: (reps, n) weights
    m = W @ M / W.sum(1, keepdims=True); s = W @ S
    ra, r1, r2 = s[:, 1] / s[:, 0], s[:, 4] / s[:, 3], s[:, 7] / s[:, 6]; oa, o1, o2 = s[:, 2] / s[:, 0], s[:, 5] / s[:, 3], s[:, 8] / s[:, 6]
    return np.stack([m[:, 2] - (m[:, 0] + m[:, 1]) / 2, m[:, 5] - (m[:, 3] + m[:, 4]) / 2, ra - r1, ra - r2, oa - o1, oa - o2], 1)
def rulers(IC, IE, rng):
    ids = sorted(set(np.ravel(IC)) | set(np.ravel(IE))); ix = {g: i for i, g in enumerate(ids)}
    A = np.array([[ix[g] for g in a + b] for a, b in zip(IC, IE)])  # (n, 4)
    G = len(ids); onehot = np.zeros((n, G), bool)
    for j in range(4): onehot[np.arange(n), A[:, j]] = True
    th = stat((~onehot.T).astype(float)); jk = np.sqrt((G - 1) / G * ((th - th.mean(0)) ** 2).sum(0))
    P = rng.poisson(1.0, size=(2000, G)).astype(float); W = P[:, A[:, 0]] * P[:, A[:, 1]] * P[:, A[:, 2]] * P[:, A[:, 3]]
    pw = stat(W).std(0, ddof=1)
    cb = stat(rng.poisson(1.0, size=(2000, n)).astype(float)).std(0, ddof=1)
    return jk, pw, cb
full = stat(np.ones((1, n)))[0]
rng = np.random.default_rng(42)
jk, pw, cb = rulers(IC, IE, rng)
print('Real ids: value | jackknife SE | product-weight annotator bootstrap SE | comparison bootstrap SE')
for k, nm in enumerate(NAMES): print('  %-28s %+.4f | %.4f | %.4f | %.4f' % (nm, full[k], jk[k], pw[k], cb[k]))
print('\nKnown-good: evaluator ids shuffled within each pool, 20 shuffles, seed 42 (ids carry no information, so the comparison bootstrap is the right width)')
R = []
for s in range(20):
    fc = np.ravel(IC).copy(); fe = np.ravel(IE).copy(); rng.shuffle(fc); rng.shuffle(fe)
    R.append(rulers(fc.reshape(-1, 2).tolist(), fe.reshape(-1, 2).tolist(), rng))
R = np.array(R)  # (20, 3, 6)
print('  mean over shuffles: jackknife SE / comparison SE | product-weight SE / comparison SE')
for k, nm in enumerate(NAMES): print('  %-28s %.2f | %.2f' % (nm, (R[:, 0, k] / R[:, 2, k]).mean(), (R[:, 1, k] / R[:, 2, k]).mean()))
print('\nReal ids, ratio to the comparison SE: jackknife | product-weight')
for k, nm in enumerate(NAMES): print('  %-28s %.2f | %.2f' % (nm, jk[k] / cb[k], pw[k] / cb[k]))
