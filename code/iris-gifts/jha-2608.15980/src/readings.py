#!/usr/bin/env python3
"""K, J1, J2 (PLAN e0e4ac8, committed before this ran). Jha, arXiv 2608.15980. Our code; MultiPref read as data; no text printed."""
import os, json, math, random, collections
import numpy as np
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'multipref', 'MultiPref-Train.jsonl')
def lab(a):
    p = a.get('overall_pref') or ''
    return 'A' if p.startswith('A') else ('B' if p.startswith('B') else ('T' if p.startswith('Tie') else None))
rows = [json.loads(l) for l in open(F) if l.strip()]
vals = collections.Counter(a.get('overall_pref') for r in rows for a in (r['normal_worker_annotations'] + r['expert_worker_annotations']))
print('K comparisons %d (printed 10,461) | overall_pref values %s' % (len(rows), dict(vals)))
un = []
for r in rows:
    c = [lab(a) for a in r['normal_worker_annotations']]; e = [lab(a) for a in r['expert_worker_annotations']]
    if len(c) == 2 and len(e) == 2 and None not in c + e and c[0] == c[1] and e[0] == e[1]: un.append((c[0], e[0]))
d = sum(1 for c, e in un if c != e); rv = sum(1 for c, e in un if {c, e} == {'A', 'B'})
print('  both pools unanimous %d (printed 2,885) | labels differ %d = %.1f%% (printed 23.6) | reverse %d = %.1f%% (printed 9.2)' % (len(un), d, 100 * d / len(un), rv, 100 * rv / len(un)))
print('\nJ1 Table 3 with independent per-model shifts (SD 1.9 pp each), K models uniformly spaced, 1,000,000 draws per K, seed 42')
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
rng = np.random.default_rng(42)
for K, gap, printed in ((6, 4.0, 0.28), (10, 2.2, 0.86), (20, 1.1, 0.9997), (30, 0.7, 1.00), (50, 0.4, 1.00)):
    pos = np.arange(K) * gap; hit = 0; N = 1000000
    for _ in range(10):
        y = pos + rng.normal(0, 1.9, size=(N // 10, K)); hit += int(np.any(np.diff(y, axis=1) < 0, axis=1).sum())
    indep = 1 - (1 - Phi(-gap / 2.6)) ** (K - 1)
    print('  K %2d gap %.1f: independent adjacent swaps %.4f | independent per-model shifts %.4f | printed %s' % (K, gap, indep, hit / N, printed))
print('  0.8 pp pair: P(N(0, 2.6) > 0.8) = %.3f (printed 38%%)' % Phi(-0.8 / 2.6))
print('\nJ2 within-pool against cross-pool disagreement, single annotators, all comparisons with two labels in each pool')
W = []
for r in rows:
    c = [lab(a) for a in r['normal_worker_annotations']]; e = [lab(a) for a in r['expert_worker_annotations']]
    if len(c) != 2 or len(e) != 2 or None in c + e: continue
    diff = lambda x, y: x != y; rev = lambda x, y: {x, y} == {'A', 'B'}
    W.append((diff(*c), diff(*e), sum(diff(x, y) for x in c for y in e) / 4, rev(*c), rev(*e), sum(rev(x, y) for x in c for y in e) / 4))
A = np.array(W, dtype=float); n = len(A)
m = A.mean(0)
print('  comparisons %d | differ: crowd-crowd %.3f, expert-expert %.3f, crowd-expert %.3f | reverse: crowd-crowd %.3f, expert-expert %.3f, crowd-expert %.3f' % (n, *m))
r_ = np.random.default_rng(42); bs = []
for _ in range(2000):
    s = A[r_.integers(0, n, n)].mean(0); bs.append((s[2] - (s[0] + s[1]) / 2, s[5] - (s[3] + s[4]) / 2))
bs = np.array(bs); q = lambda k: (np.percentile(bs[:, k], 2.5), np.percentile(bs[:, k], 97.5))
print('  cross minus mean within, differ: %+.3f [%+.3f, %+.3f] | reverse: %+.3f [%+.3f, %+.3f]' % (m[2] - (m[0] + m[1]) / 2, *q(0), m[5] - (m[3] + m[4]) / 2, *q(1)))
# J1b (PLAN Addendum 1, defined after the data)
print('\nJ1b (defined after the data) J1 with SD 2.6/sqrt(2) per model, so the difference SD is the paper\'s 2.6 pp')
rng = np.random.default_rng(42); sd = 2.6 / math.sqrt(2)
for K, gap, printed in ((6, 4.0, 0.28), (10, 2.2, 0.86), (20, 1.1, 0.9997), (30, 0.7, 1.00), (50, 0.4, 1.00)):
    pos = np.arange(K) * gap; hit = 0; N = 1000000
    for _ in range(10):
        y = pos + rng.normal(0, sd, size=(N // 10, K)); hit += int(np.any(np.diff(y, axis=1) < 0, axis=1).sum())
    print('  K %2d gap %.1f: independent per-model shifts %.4f | printed %s' % (K, gap, hit / N, printed))
# J2b and J3 (PLAN Addendum 2, defined after the data)
print('\nJ2b and J3 (defined after the data) with annotator-grouped jackknife standard errors (delete one annotator id, every comparison it labelled)')
R = []
for r in rows:
    cw, ew = r['normal_worker_annotations'], r['expert_worker_annotations']
    c = [lab(a) for a in cw]; e = [lab(a) for a in ew]
    if len(c) != 2 or len(e) != 2 or None in c + e: continue
    R.append((c, e, set(a['evaluator'] for a in cw + ew)))
ids = sorted(set().union(*(x[2] for x in R)))
crowd_ids = set(a['evaluator'] for r in rows for a in r['normal_worker_annotations']); expert_ids = set(a['evaluator'] for r in rows for a in r['expert_worker_annotations'])
print('  comparisons %d | annotator ids %d (crowd %d, expert %d, in both pools %d)' % (len(R), len(ids), len(crowd_ids), len(expert_ids), len(crowd_ids & expert_ids)))
def stats(sub):
    A = np.array([(c[0] != c[1], e[0] != e[1], sum(x != y for x in c for y in e) / 4, {*c} == {'A', 'B'}, {*e} == {'A', 'B'}, sum({x, y} == {'A', 'B'} for x in c for y in e) / 4) for c, e, _ in sub], dtype=float).mean(0)
    j2 = (A[2] - (A[0] + A[1]) / 2, A[5] - (A[3] + A[4]) / 2)
    def split(pairs):
        k = [(p, q) for (p, q) in pairs if p[0] == p[1] and q[0] == q[1]]
        return len(k), sum(p[0] != q[0] for p, q in k), sum({p[0], q[0]} == {'A', 'B'} for p, q in k)
    act = split([((c[0], c[1]), (e[0], e[1])) for c, e, _ in sub])
    s1 = split([((c[0], e[0]), (c[1], e[1])) for c, e, _ in sub])
    s2 = split([((c[0], e[1]), (c[1], e[0])) for c, e, _ in sub])
    rate = lambda t: (t[1] / t[0], t[2] / t[0])
    return j2, act, s1, s2, rate(act), rate(s1), rate(s2)
full = stats(R)
def jk(f):
    th = []
    for g in ids:
        th.append(f(stats([x for x in R if g not in x[2]])))
    th = np.array(th); G = len(th)
    return np.sqrt((G - 1) / G * ((th - th.mean(0)) ** 2).sum(0))
J = jk(lambda s: [s[0][0], s[0][1], s[4][0] - s[5][0], s[4][0] - s[6][0], s[4][1] - s[5][1], s[4][1] - s[6][1], s[4][0], s[5][0], s[6][0]])
print('  J2b cross minus mean within, differ %+.3f (jackknife SE %.3f, +-1.96 SE [%+.3f, %+.3f]) | reverse %+.3f (SE %.3f, [%+.3f, %+.3f])' % (full[0][0], J[0], full[0][0] - 1.96 * J[0], full[0][0] + 1.96 * J[0], full[0][1], J[1], full[0][1] - 1.96 * J[1], full[0][1] + 1.96 * J[1]))
for name, t, rt in (('actual pools (crowd pair vs expert pair)', full[1], full[4]), ('mixed split 1 (crowd1+expert1 vs crowd2+expert2)', full[2], full[5]), ('mixed split 2 (crowd1+expert2 vs crowd2+expert1)', full[3], full[6])):
    print('  J3 %s: both pairs unanimous %d | majorities differ %d = %.1f%% | opposite winners %d = %.1f%%' % (name, t[0], t[1], 100 * rt[0], t[2], 100 * rt[1]))
for k, (lbl, v) in enumerate((('differ, actual minus split 1', full[4][0] - full[5][0]), ('differ, actual minus split 2', full[4][0] - full[6][0]), ('opposite, actual minus split 1', full[4][1] - full[5][1]), ('opposite, actual minus split 2', full[4][1] - full[6][1]))):
    se = J[2 + k]; print('  J3 pool excess %s: %+.1f pp (jackknife SE %.1f, +-1.96 SE [%+.1f, %+.1f])' % (lbl, 100 * v, 100 * se, 100 * (v - 1.96 * se), 100 * (v + 1.96 * se)))
