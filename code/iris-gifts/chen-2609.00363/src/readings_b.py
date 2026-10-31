#!/usr/bin/env python3
"""K1b, K1c, K2b and the K2 median fix (PLAN.md Addendum 1, e2371f7, committed before this ran; defined after the data). Our code."""
import os, json, hashlib, statistics
import numpy as np
from scipy import stats
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'repo', 'experiment', 'artifacts'); J = lambda *p: json.load(open(os.path.join(A, *p)))
sha = lambda *p: hashlib.sha256(open(os.path.join(A, *p), 'rb').read()).hexdigest()
def cp(k, n): return (stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
def exact_p(b, c): n = b + c; return 1.0 if n == 0 else min(1.0, 2 * stats.binom.cdf(min(b, c), n, 0.5))
C64, T64 = J('tf64v6b_CUTLASS.json'), J('tf64v6b_TRITON.json')
rs = C64['manifest']['rails_sha256']; assert rs == T64['manifest']['rails_sha256']
cand = [f for f in os.listdir(A) if f.endswith('.json') and sha(f) == rs]
print('K1b rail of the 64-prompt grid: the file whose sha256 equals the manifest rails_sha256: %s' % cand)
rail = J(cand[0]); assert len(rail) == 64 and all(len(r) == 256 for r in rail)
M = {}
for nm, d in (('CUTLASS', C64), ('TRITON', T64)):
    M[nm] = np.array([[s['top1_id'] != rail[i][j] for j, s in enumerate(r['steps'])] for i, r in enumerate(d['records'])])
    k = int(M[nm].sum()); n = M[nm].size; lo, hi = cp(k, n)
    k1 = int(M[nm][:, 1:].sum()); n1 = M[nm][:, 1:].size
    print('  %-7s prefill top-1 differs from the rail at %d of %d = %.2f%% [%.2f, %.2f] | without position 0: %d of %d = %.2f%%' % (nm, k, n, 100 * k / n, 100 * lo, 100 * hi, k1, n1, 100 * k1 / n1))
c, t = M['CUTLASS'], M['TRITON']; b1 = int((c & ~t).sum()); b2 = int((t & ~c).sum())
per = t.mean(1) - c.mean(1); rng = np.random.default_rng(42); bs = [per[rng.integers(0, 64, 64)].mean() for _ in range(10000)]
print('  paired by position: CUTLASS only %d, TRITON only %d, both %d | exact p %.3g | Triton minus CUTLASS %+.2f pp, prompt-cluster bootstrap [%+.2f, %+.2f] | prompts with Triton higher %d, CUTLASS higher %d' % (
    b1, b2, int((c & t).sum()), exact_p(b1, b2), 100 * per.mean(), 100 * np.percentile(bs, 2.5), 100 * np.percentile(bs, 97.5), int((per > 0).sum()), int((per < 0).sum())))
q = [100 * c[:, a:a + 64].mean() for a in (0, 64, 128, 192)]
print('  CUTLASS share by position window 0-63, 64-127, 128-191, 192-255: %s' % ', '.join('%.1f%%' % x for x in q))
print('\nK1c the 8-prompt grid without position 0 and tie-neutral (rail token log probability strictly below the top-1 log probability)')
T8 = {a: J('tf_%s.json' % a) for a in ('CUTLASS', 'TRITON')}; F = {}
for a, d in T8.items():
    allp = [(i, j, s) for i, p in enumerate(d) for j, s in enumerate(p)]
    ties = sum(1 for _, _, s in allp if s['top1_id'] != s['chosen_id'] and s['chosen_lp'] == s['top1_lp'])
    F[a] = [s['chosen_lp'] < s['top1_lp'] for i, j, s in allp if j > 0]
    k, n = sum(F[a]), len(F[a]); lo, hi = cp(k, n)
    print('  %-7s mismatches that are exact log-probability ties broken by token id: %d | without position 0 and tie-neutral: %d of %d = %.1f%% [%.1f, %.1f]' % (a, ties, k, n, 100 * k / n, 100 * lo, 100 * hi))
b1 = sum(1 for x, y in zip(F['CUTLASS'], F['TRITON']) if x and not y); b2 = sum(1 for x, y in zip(F['CUTLASS'], F['TRITON']) if y and not x)
print('  paired: CUTLASS only %d, TRITON only %d | exact p %.3g' % (b1, b2, exact_p(b1, b2)))
print('\nK2 medians recomputed (median of first differing index over prompts that differ)')
def first(a, b): return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
for nm, a, b in (('1.7B own scales (Table V)', J('p8_results/e2e/qwen3-1.7b-int8-w8a8/tokens_CUTLASS.json'), J('p8_results/e2e/qwen3-1.7b-int8-w8a8/tokens_TRITON.json')),
                 ('8B own scales (Table V)', J('p8_results/e2e_8b/qwen3-8b-int8-w8a8/tokens_CUTLASS.json'), J('p8_results/e2e_8b/qwen3-8b-int8-w8a8/tokens_TRITON.json')),
                 ('14B own scales (Table V)', J('p8_results/e2e_14b/qwen3-14b-int8-w8a8/tokens_CUTLASS.json'), J('p8_results/e2e_14b/qwen3-14b-int8-w8a8/tokens_TRITON.json')),
                 ('1.7B companion 64 prompts', J('tokens64_CUTLASS.json'), J('tokens64_TRITON.json')), ('8B companion 16 prompts', J('raw8b_CUTLASS.json'), J('raw8b_TRITON.json'))):
    f = [first(x, y) for x, y in zip(a, b)]; num = [x for x in f if x is not None]
    print('  %-28s prompts %2d, differ %2d | median %s, quartiles %s and %s | index 0 on %d' % (nm, len(f), len(num), statistics.median(num), *[float(x) for x in np.percentile(num, [25, 75])], num.count(0)))
print('\nK2b the same kernel across batch configurations, 1.7B: the batch-8 run (w1) against the same prompts in the batch-64 run (first 64 tokens)')
p8 = [p[0]['pos'] for p in T8['CUTLASS']]; p64 = [r['steps'][0]['pos'] for r in C64['records'][:8]]
print('  prompt identity by prompt length (first teacher-forced position): batch-8 %s, batch-64 first 8 %s, equal %s' % (p8, p64, p8 == p64))
cal = J('calib_prompts.json'); ph = [r.get('prompt_sha') for r in C64['records'][:8]]
for a in ('CUTLASS', 'TRITON'):
    w = J('w1', 'tokens_%s.json' % a); g = [r[:64] for r in J('tokens64_%s.json' % a)[:8]]
    f = [first(x, y) for x, y in zip(w, g)]; num = [x for x in f if x is not None]
    print('  %-7s batch-8 against batch-64: identical %d of 8 | first differing index per prompt %s | median %s' % (a, f.count(None), ['same' if x is None else x for x in f], statistics.median(num) if num else 'none'))
w = (J('w1', 'tokens_CUTLASS.json'), J('w1', 'tokens_TRITON.json')); g = ([r[:64] for r in J('tokens64_CUTLASS.json')[:8]], [r[:64] for r in J('tokens64_TRITON.json')[:8]])
print('  cross-kernel first index on these 8 prompts: batch-8 %s | batch-64 %s' % ([first(x, y) for x, y in zip(*w)], [first(x, y) for x, y in zip(*g)]))
