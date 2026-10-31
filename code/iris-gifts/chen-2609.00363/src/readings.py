#!/usr/bin/env python3
"""K1-K3 of PLAN.md (2cb3a14, committed before this ran). arXiv 2609.00363. Our code; their files read as data."""
import os, json, collections, statistics
from scipy import stats
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'repo', 'experiment', 'artifacts'); J = lambda *p: json.load(open(os.path.join(A, *p)))
def cp(k, n): return (stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
def exact_p(b, c): n = b + c; return 1.0 if n == 0 else min(1.0, 2 * stats.binom.cdf(min(b, c), n, 0.5))
print('K1 prefill against decode: positions where the teacher-forced top-1 differs from the chosen (decoded) token, 8 prompts x 64')
T = {a: J('tf_%s.json' % a) for a in ('CUTLASS', 'TRITON')}
same_rail = all(sc['chosen_id'] == st['chosen_id'] for pc, pt in zip(T['CUTLASS'], T['TRITON']) for sc, st in zip(pc, pt))
print('  chosen-token sequences identical between the two arms\' files: %s; positions aligned: %s' % (same_rail, all(sc['pos'] == st['pos'] for pc, pt in zip(T['CUTLASS'], T['TRITON']) for sc, st in zip(pc, pt))))
rail = [[s['chosen_id'] for s in p] for p in T['CUTLASS']]
for f in ('tokens_CUTLASS.json', 'tokens_TRITON.json'): print('  the shared rail equals the companion greedy run %s on %d of 8 prompts' % (f, sum(a == b for a, b in zip(rail, J('w1', f)))))
print('  so the CUTLASS row is prefill against its own decode, and the TRITON row is Triton prefill against the CUTLASS decode')
D = {}
for a in T:
    flags = [s['top1_id'] != s['chosen_id'] for p in T[a] for s in p]; k, n = sum(flags), len(flags); D[a] = flags; lo, hi = cp(k, n)
    per = [sum(s['top1_id'] != s['chosen_id'] for s in p) for p in T[a]]
    print('  %-7s %d of %d = %.1f%% [%.1f, %.1f] | per prompt %s' % (a, k, n, 100 * k / n, 100 * lo, 100 * hi, per))
b = sum(1 for x, y in zip(D['CUTLASS'], D['TRITON']) if x and not y); c = sum(1 for x, y in zip(D['CUTLASS'], D['TRITON']) if y and not x)
print('  paired by position (CUTLASS prefill vs Triton prefill, both against the CUTLASS rail): CUTLASS only %d, TRITON only %d, both %d | exact test p %.3g' % (b, c, sum(1 for x, y in zip(D['CUTLASS'], D['TRITON']) if x and y), exact_p(b, c)))
r64 = J('tf64v6b_TRITON.json')['records'][0]['steps'][0]
print('  64-prompt files: steps carry %s and no decoded token; their rail is a separate file found by hash, read in readings_b.py (K1b, Addendum 1)' % sorted(r64))
print('\nK2 first token index where two greedy sequences differ (64 tokens per prompt unless stated; "same" = identical sequence)')
def first(a, b): return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), 'same' if len(a) == len(b) else min(len(a), len(b)))
pairs = []
for size, d in (('1.7B', 'e2e/qwen3-1.7b-int8-w8a8'), ('8B', 'e2e_8b/qwen3-8b-int8-w8a8'), ('14B', 'e2e_14b/qwen3-14b-int8-w8a8')):
    pairs.append(('%s own scales, CUTLASS vs TRITON (Table V)' % size, J('p8_results', d, 'tokens_CUTLASS.json'), J('p8_results', d, 'tokens_TRITON.json')))
for size, d in (('1.7B', 'e2e/qwen3-1.7b-int8-pow2_nearest'), ('8B', 'e2e_8b/qwen3-8b-int8-pow2_nearest'), ('14B', 'e2e_14b/qwen3-14b-int8-pow2_nearest')):
    pairs.append(('%s requantized pow2, CUTLASS vs TRITON' % size, J('p8_results', d, 'tokens_CUTLASS.json'), J('p8_results', d, 'tokens_TRITON.json')))
pairs += [('1.7B companion 64 prompts, CUTLASS vs TRITON', J('tokens64_CUTLASS.json'), J('tokens64_TRITON.json')),
          ('8B companion 16 prompts, CUTLASS vs TRITON', J('raw8b_CUTLASS.json'), J('raw8b_TRITON.json')),
          ('1.7B companion 8 prompts, CUTLASS vs TRITON', J('w1', 'tokens_CUTLASS.json'), J('w1', 'tokens_TRITON.json')),
          ('1.7B companion 8 prompts, CUTLASS vs CUTLASS repeat', J('w1', 'tokens_CUTLASS.json'), J('w1', 'tokens_CUTLASS2.json')),
          ('1.7B companion 8 prompts, TRITON vs TRITON repeat', J('w1', 'tokens_TRITON.json'), J('w1', 'tokens_TRITON2.json'))]
for nm, a, b in pairs:
    f = [first(x, y) for x, y in zip(a, b)]; num = sorted(x for x in f if x != 'same')
    print('  %-52s prompts %2d, tokens %s | identical %2d | first differing index: %s%s' % (nm, len(a), sorted({len(x) for x in a}), f.count('same'),
          ('median %s, range %s to %s' % (statistics.median(num), num[0], num[-1])) if num else 'none', (' | per prompt %s' % f) if len(f) <= 16 else ''))
print('\nK3 scorecard with exact intervals (Clopper-Pearson 95%): cells where the fault moved the output, and cells detected by any check, by fault and regime')
rows = J('p5p6_results', 'p5_sensitivity.json')['rows']; g = collections.defaultdict(list)
for r in rows: g[(r['fault'], r['regime'])].append(r)
for (fa, rg), L in sorted(g.items()):
    n = len(L); ko = sum(r['fault_observable'] for r in L); kd = sum(any(c.get('fired') for c in r['checks'].values()) for r in L)
    kdo = sum(any(c.get('fired') for c in r['checks'].values()) for r in L if r['fault_observable'])
    lo, hi = cp(ko, n); l2, h2 = cp(kdo, ko) if ko else (float('nan'),) * 2
    print('  %-34s %-5s cells %4d | output moved %4d = %5.1f%% [%5.1f, %5.1f] | any check fired %4d | fired among moved %4d of %4d%s' % (
          fa, rg, n, ko, 100 * ko / n, 100 * lo, 100 * hi, kd, kdo, ko, (' = %.1f%% [%.1f, %.1f]' % (100 * kdo / ko, 100 * l2, 100 * h2)) if ko else ''))
