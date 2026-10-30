#!/usr/bin/env python3
"""C1-C5 (PLAN 9f4b8a9, committed before this ran). Caldwell, arXiv 2608.20432. Our code; their traces and make_frontier.py read as data."""
import os, sys, collections, random, re, ast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JUDGES, PRINTED, load, pairs, binom2, T
D = {j: load(j) for j in JUDGES}; PR = {j: pairs(D[j]) for j in JUDGES}
def decls(j): return sorted({(k[0], k[1]) for k in D[j]})
print('C1 sign test with the declaration as the unit (aligned in at least two replicates), beside the pooled test')
for j in JUDGES:
    pr = PR[j]; c = collections.Counter(pr.values())
    pooled = binom2(c['aligned'], c['aligned'] + c['inverted'])
    al = nal = inv = tie = short = 0
    for dk in decls(j):
        v = [pr[(dk[0], dk[1], r)] for r in (1, 2, 3) if (dk[0], dk[1], r) in pr]
        short += len(v) < 3; a = v.count('aligned'); i = v.count('inverted')
        al += a >= 2; nal += a < 2; inv += i > a; tie += (i == a)
    dm = sum(1 for dk in decls(j) if sum(1 for r in (1, 2, 3) if PR[j].get((dk[0], dk[1], r)) == 'aligned') > sum(1 for r in (1, 2, 3) if PR[j].get((dk[0], dk[1], r)) == 'inverted'))
    p1 = binom2(al, al + nal); p2 = binom2(dm, dm + inv)
    print('  %-24s pooled pairs aligned %d vs inverted %d p %.1e | declarations aligned %d of %d (%.1f%%) p %.1e | majority direction aligned %d vs inverted %d (tied %d) p %.1e | <1e-5 at declaration level: %s | declarations with fewer than 3 pairs %d' % (
        j, c['aligned'], c['inverted'], pooled, al, al + nal, 100 * al / (al + nal), p1, dm, inv, tie, p2, 'yes' if p1 < 1e-5 else 'NO', short))
print('\nC2 ties three ways, declaration-clustered bootstrap 95% (10,000, seed 42)')
res = {}
for j in JUDGES:
    pr = PR[j]; agg = []
    for dk in decls(j):
        v = [pr[(dk[0], dk[1], r)] for r in (1, 2, 3) if (dk[0], dk[1], r) in pr]
        agg.append((v.count('aligned'), v.count('tie'), v.count('inverted')))
    def stats(rows):
        a = sum(x[0] for x in rows); t = sum(x[1] for x in rows); i = sum(x[2] for x in rows); n = a + t + i
        return a / n, (a + t / 2) / n, a / (a + i)
    pt = stats(agg); rng = random.Random(42); bs = [stats([agg[rng.randrange(len(agg))] for _ in agg]) for _ in range(10000)]
    ci = [sorted(b[k] for b in bs) for k in range(3)]; q = lambda s: (s[249], s[9749])
    t = sum(x[1] for x in agg) / sum(sum(x) for x in agg); res[j] = pt
    print('  %-24s ties %4.1f%% | ties as misses %.1f [%.1f, %.1f] (chance line %.1f) | ties as half %.1f [%.1f, %.1f] | ties left out %.1f [%.1f, %.1f]' % (
        j, 100 * t, 100 * pt[0], *(100 * x for x in q(ci[0])), 100 * (1 - t) / 2, 100 * pt[1], *(100 * x for x in q(ci[1])), 100 * pt[2], *(100 * x for x in q(ci[2]))))
for k, nm in enumerate(('ties as misses', 'ties as half', 'ties left out')):
    print('  order, %-14s: %s' % (nm, ' > '.join('%s %.1f' % (j.split('-2026')[0], 100 * res[j][k]) for j in sorted(JUDGES, key=lambda j: -res[j][k]))))
print('\nC3 replicate flips per judge (binary verdict aligned or not; three-way aligned / tie / inverted beside it)')
for j in JUDGES:
    pr = PR[j]; pb = pt3 = n2 = 0; any_b = any_3 = n3 = 0
    for dk in decls(j):
        v = {r: pr.get((dk[0], dk[1], r)) for r in (1, 2, 3)}
        for r1, r2 in ((1, 2), (1, 3), (2, 3)):
            if v[r1] and v[r2]:
                n2 += 1; pb += (v[r1] == 'aligned') != (v[r2] == 'aligned'); pt3 += v[r1] != v[r2]
        if all(v.values()):
            n3 += 1; any_b += len({x == 'aligned' for x in v.values()}) > 1; any_3 += len(set(v.values())) > 1
    print('  %-24s two replicates differ: binary %.1f%%, three-way %.1f%% (%d comparisons) | three replicates not all equal: binary %.1f%%, three-way %.1f%% (%d declarations)' % (
        j, 100 * pb / n2, 100 * pt3 / n2, n2, 100 * any_b / n3, 100 * any_3 / n3, n3))
print('\nC4 lost pairs counted as misses over all 654 pairs')
for j in JUDGES:
    c = collections.Counter(PR[j].values()); n = len(PR[j]); lost = 654 - n
    print('  %-24s complete %d, lost %d | released pairs %.2f%% | lost as misses %.2f%% | printed %.1f' % (j, n, lost, 100 * c['aligned'] / n, 100 * c['aligned'] / 654, PRINTED[j][0]))
print('\nC5 cost per pair at the repo price table (make_frontier.py), every prompt token at the fresh-input rate: an upper bound')
src = open(os.path.join(T, 'gh', 'scripts', 'make_frontier.py')).read(); PRICE = ast.literal_eval(re.search(r'PRICING = (\{.*?\n\})', src, re.S).group(1))
for j in JUDGES:
    if j not in PRICE: print('  %-24s not in the repo price table (printed %.3f)' % (j, PRINTED[j][1])); continue
    rin, rout, rc = PRICE[j]; tot = 0.0; n = 0
    for k, v in D[j].items():
        if 'initial' in v and 'final' in v:
            n += 1; tot += sum(v[x]['pt'] * rin + v[x]['ct'] * rout for x in ('initial', 'final')) / 1e6
    print('  %-24s rates in %.3f out %.3f per million | upper bound %.4f USD per pair over %d pairs | printed %.3f | printed %s the bound' % (j, rin, rout, tot / n, n, PRINTED[j][1], 'ABOVE' if PRINTED[j][1] > tot / n + 0.0005 else 'within'))
# C5b (PLAN Addendum 1, defined after the data)
j = 'gpt-5.4-mini-2026-03-17'; tin = tout = 0; n = 0
for k, v in D[j].items():
    if 'initial' in v and 'final' in v: n += 1; tin += v['initial']['pt'] + v['final']['pt']; tout += v['initial']['ct'] + v['final']['ct']
print('\nC5b (defined after the data) %s: mean tokens per pair, prompt %.0f, completion %.0f | at 0.75 in and 4.50 out per million, all prompt fresh: %.4f USD per pair (printed 0.136)' % (j, tin / n, tout / n, (tin * 0.75 + tout * 4.50) / 1e6 / n))
# C1b, C2b, C6 (PLAN Addendum 2, defined after the data)
print('\nC1b (defined after the data) exact sign test on each replicate alone')
for j in JUDGES:
    out = []
    for r in (1, 2, 3):
        v = [x for k, x in PR[j].items() if k[2] == r]; a = v.count('aligned'); i = v.count('inverted')
        out.append('r%d %d/%d p %.1e (ties out %.1e)' % (r, a, len(v), binom2(a, len(v)), binom2(a, a + i)))
    print('  %-24s %s' % (j, ' | '.join(out)))
print('\nC2b (defined after the data) paired gaps between judges adjacent in Table 1, declaration-clustered bootstrap 95% (10,000, seed 42)')
agg = {}
for j in JUDGES:
    agg[j] = {}
    for dk in decls(j):
        v = [PR[j][(dk[0], dk[1], r)] for r in (1, 2, 3) if (dk[0], dk[1], r) in PR[j]]
        agg[j][dk] = (v.count('aligned'), v.count('tie'), v.count('inverted'))
D_ = sorted(set.intersection(*[set(agg[j]) for j in JUDGES]))
def rate(rows, rule):
    a = sum(x[0] for x in rows); t = sum(x[1] for x in rows); i = sum(x[2] for x in rows)
    return (a / (a + t + i), (a + t / 2) / (a + t + i), a / (a + i))[rule]
rng = random.Random(42); idx = [[rng.randrange(len(D_)) for _ in D_] for _ in range(10000)]
for x, y in zip(JUDGES, JUDGES[1:]):
    cells = []
    for rule, nm in ((0, 'misses'), (1, 'half'), (2, 'left out')):
        d0 = 100 * (rate([agg[x][k] for k in D_], rule) - rate([agg[y][k] for k in D_], rule))
        bs = sorted(100 * (rate([agg[x][D_[k]] for k in ix], rule) - rate([agg[y][D_[k]] for k in ix], rule)) for ix in idx)
        cells.append('ties %s %+.1f [%+.1f, %+.1f]' % (nm, d0, bs[249], bs[9749]))
    print('  %s minus %s: %s' % (x.split('-2026')[0], y.split('-2026')[0], ' | '.join(cells)))
print('\nC6 (defined after the data) make_frontier.py line 158:', open(os.path.join(T, 'gh', 'scripts', 'make_frontier.py')).read().split('\n')[157].strip())
print('  observed tie share of pairs:', {j.split('-2026')[0]: round(100 * collections.Counter(PR[j].values())['tie'] / len(PR[j]), 1) for j in JUDGES})
