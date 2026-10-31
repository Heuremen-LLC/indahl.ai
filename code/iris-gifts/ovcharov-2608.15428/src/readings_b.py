#!/usr/bin/env python3
"""R2b, R2c, R8 of PLAN.md Addendum 4 (e079cda, committed before this ran; defined after the data). Our code; his files read as data."""
import os, json, collections
import numpy as np
from scipy import stats
G = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); R = G + '/runs'; T = G + '/theirs/predictions'
def load(m, model, arm, rep):
    out = {}
    for l in open('%s/%s/%s_%s_r%d.jsonl' % (R, m, model, arm, rep), encoding='utf-8'):
        d = json.loads(l); out[d['id']] = d
    return out
def cls(d): return 'error' if d.get('err') else ('none' if d.get('pred') is None else 'ABCD'[d['pred']])
def cp(k, n): return (stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
def stuart_maxwell(a, b, cats='ABCD'):
    keep = [(x, y) for x, y in zip(a, b) if x in cats and y in cats]; k = len(cats); N = np.zeros((k, k))
    for x, y in keep: N[cats.index(x), cats.index(y)] += 1
    d = (N.sum(1) - N.sum(0))[:-1]; S = np.zeros((k - 1, k - 1))
    for i in range(k - 1):
        for j in range(k - 1):
            S[i, j] = (N[i].sum() + N[:, i].sum() - 2 * N[i, i]) if i == j else -(N[i, j] + N[j, i])
    chi = float(d @ np.linalg.solve(S, d)); return chi, k - 1, float(stats.chi2.sf(chi, k - 1)), len(keep)
print('R2b across-setup letter changes (Armature r1 against Mac r1), Clopper-Pearson 95%, against each setup\'s repeat floor (Fisher exact)')
for model in ('llama3.1-8b', 'ministral-3-8b'):
    for arm in ('B', 'F'):
        A1, A2, M1, M2 = (load(m, model, arm, r) for m, r in (('armature', 1), ('armature', 2), ('mac', 1), ('mac', 2)))
        ids = sorted(A1); n = len(ids)
        x = sum(cls(A1[i]) != cls(M1[i]) for i in ids); fa = sum(cls(A1[i]) != cls(A2[i]) for i in ids); fm = sum(cls(M1[i]) != cls(M2[i]) for i in ids)
        xp = [i for i in ids if cls(A1[i]) in 'ABCD' and cls(M1[i]) in 'ABCD' and len(cls(A1[i])) == 1 and len(cls(M1[i])) == 1]; xx = sum(cls(A1[i]) != cls(M1[i]) for i in xp)
        pa = stats.fisher_exact([[x, n - x], [fa, n - fa]])[1]; pm = stats.fisher_exact([[x, n - x], [fm, n - fm]])[1]
        lo, hi = cp(x, n); mlo, mhi = cp(fm, n)
        print('  %-15s arm %s: across %d of %d = %.2f%% [%.2f, %.2f] | floor Armature %d (Fisher p %.2g) | floor Mac %d, upper bound %.3f%% (Fisher p %.2g) | both parsed: %d of %d' % (
            model, arm, x, n, 100 * x / n, 100 * lo, 100 * hi, fa, pa, fm, 100 * mhi, pm, xx, len(xp)))
print('\nR2c paired accuracy across setups (Armature r1 minus Mac r1), exact McNemar on items right on one side only; Stuart-Maxwell on the four letters')
for model in ('llama3.1-8b', 'ministral-3-8b'):
    for arm in ('B', 'F'):
        A1, M1 = load('armature', model, arm, 1), load('mac', model, arm, 1); ids = sorted(A1); n = len(ids)
        ca = np.array([A1[i].get('pred') == A1[i]['gold'] for i in ids]); cm = np.array([M1[i].get('pred') == M1[i]['gold'] for i in ids])
        b, c = int((ca & ~cm).sum()), int((cm & ~ca).sum()); p = 1.0 if b + c == 0 else min(1.0, 2 * stats.binom.cdf(min(b, c), b + c, 0.5))
        sm = stuart_maxwell([cls(A1[i]) for i in ids], [cls(M1[i]) for i in ids])
        print('  %-15s arm %s: accuracy %.4f and %.4f, difference %+.2f pp | right on Armature only %d, on Mac only %d, exact p %.3g | Stuart-Maxwell chi2 %.1f (df %d) p %.2g over %d items parsed on both' % (
            model, arm, ca.mean(), cm.mean(), 100 * (ca.mean() - cm.mean()), b, c, p, *sm))
print('\nR8 his own reruns (his released predictions): letter changes between his runs on the items both hold')
def his(f, mode):
    D = collections.defaultdict(dict)
    for l in open(os.path.join(T, f), encoding='utf-8'):
        r = json.loads(l)
        if r['mode'] == mode: D[r['model']][r['id']] = r
    return D
S, A = his('small_models.jsonl', 'blind'), his('scenario_a.jsonl', 'blind')
hc = lambda r: 'none' if r.get('pred') in (None, '') else str(r['pred'])
for m in sorted(S):
    if m not in A: continue
    ids = sorted(set(S[m]) & set(A[m])); k = sum(hc(S[m][i]) != hc(A[m][i]) for i in ids); lo, hi = cp(k, len(ids))
    acc = lambda D: np.mean([hc(D[i]) == str(D[i]['gold']) for i in ids])
    print('  %-14s blind, 600-item run against full run, %d shared items: %d differ = %.1f%% [%.1f, %.1f] | accuracy %.4f and %.4f' % (m, len(ids), k, 100 * k / len(ids), 100 * lo, 100 * hi, acc(S[m]), acc(A[m])))
F2, F4 = his('small_models.jsonl', 'full')['llama-3.1-8b'], his('small_models_4096.jsonl', 'full')['llama-3.1-8b']
ids = sorted(set(F2) & set(F4)); k = sum(hc(F2[i]) != hc(F4[i]) for i in ids); lo, hi = cp(k, len(ids))
print('  llama-3.1-8b full, 2,048 against 4,096 tokens, %d shared items: %d differ = %.1f%% [%.1f, %.1f]' % (len(ids), k, 100 * k / len(ids), 100 * lo, 100 * hi))
