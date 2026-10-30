#!/usr/bin/env python3
"""B1-B4 (PLAN 59f10de, committed before this ran). Bronder, arXiv 2607.14399. Our code; his logs and files read as data."""
import os, sys, json, math, random, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import L, pick, games, valid, strong, false_verdict
Z = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'zenodo')
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
def fisher2(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c; N = n1 + n2
    pr = lambda x: math.comb(n1, x) * math.comb(n2, k - x) / math.comb(N, k)
    p0 = pr(a); return min(1.0, sum(pr(x) for x in range(max(0, k - n2), min(k, n1) + 1) if pr(x) <= p0 * (1 + 1e-9)))
def sign2(k, n): return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(k, n - k) + 1)) / 2 ** n)
g0 = games(pick('zai-honest-epochs2')[0]); s2 = games(pick('s2-main')[0]); sd = games(pick('s2-disclosure')[0])
anchors = sorted({g['inst'] for g in g0} & {g['inst'] for g in s2})
print('B1 strong claims per anchor, binary grammar (Gate 0) against three-verdict grammar (series 2), all games counted')
for a in anchors:
    x = [g for g in g0 if g['inst'] == a]; y = [g for g in s2 if g['inst'] == a]; kx = sum(map(strong, x)); ky = sum(map(strong, y))
    print('  %s %2d/%d -> %2d/%d | Fisher exact p %.4f' % (a, kx, len(x), ky, len(y), fisher2(kx, len(x) - kx, ky, len(y) - ky)))
kx = sum(strong(g) for g in g0 if g['inst'] in anchors); ky = sum(strong(g) for g in s2 if g['inst'] in anchors)
print('  pooled %d/40 -> %d/40, drop %+.3f, Newcombe 95%% [%+.3f, %+.3f] (games share four anchors)' % ((kx, ky) + newcombe(kx, 40, ky, 40)))
print('\nB2 the disclosure contrast by instance (six solvable grid instances, valid games)')
six = sorted({g['inst'] for g in sd}); pos = neg = 0
for i in six:
    h = [g for g in s2 if g['inst'] == i and valid(g)]; d = [g for g in sd if g['inst'] == i and valid(g)]
    fh, fd = sum(map(false_verdict, h)), sum(map(false_verdict, d)); pos += fh > fd; neg += fd > fh
    print('  %s hidden false %d/%d | disclosed false %d/%d' % (i, fh, len(h), fd, len(d)))
print('  instances with more false verdicts hidden %d, disclosed %d, tied %d | exact sign test over instances p %.4f' % (pos, neg, len(six) - pos - neg, sign2(pos, pos + neg)))
print('  0 of 58: exact (Clopper-Pearson) 95%% upper bound %.4f' % (1 - 0.025 ** (1 / 58)))
print('\nB3 Gate 2 meter against none-lantern strong claims, instance as the cluster')
M = [g for g in games(pick('g2-meter', 'none', 'meter')[0]) if valid(g)]; N0 = [g for g in games(pick('g2-none', 'none', 'lantern')[0]) if valid(g)]
inst = sorted({g['inst'] for g in M} | {g['inst'] for g in N0})
pm = {i: (sum(strong(g) for g in M if g['inst'] == i), sum(1 for g in M if g['inst'] == i)) for i in inst}
pn = {i: (sum(strong(g) for g in N0 if g['inst'] == i), sum(1 for g in N0 if g['inst'] == i)) for i in inst}
above = sum(pm[i][0] / pm[i][1] > pn[i][0] / pn[i][1] for i in inst); below = sum(pm[i][0] / pm[i][1] < pn[i][0] / pn[i][1] for i in inst)
diff = lambda ids: sum(pm[i][0] for i in ids) / sum(pm[i][1] for i in ids) - sum(pn[i][0] for i in ids) / sum(pn[i][1] for i in ids)
r = random.Random(42); bs = sorted(diff([inst[r.randrange(len(inst))] for _ in inst]) for _ in range(10000))
d, lo, hi = newcombe(sum(v[0] for v in pm.values()), sum(v[1] for v in pm.values()), sum(v[0] for v in pn.values()), sum(v[1] for v in pn.values()))
print('  instances %d | meter %d/%d, none-lantern %d/%d | difference %+.3f' % (len(inst), sum(v[0] for v in pm.values()), sum(v[1] for v in pm.values()), sum(v[0] for v in pn.values()), sum(v[1] for v in pn.values()), diff(inst)))
print('  instance bootstrap 95%% [%+.3f, %+.3f] | binomial (Newcombe, games independent) [%+.3f, %+.3f] | meter above on %d instances, below on %d, tied %d, exact sign p %.4f' % (bs[249], bs[9749], lo, hi, above, below, len(inst) - above - below, sign2(above, above + below)))
print('\nB4 record items')
for d_, sk, rd in (('g2-none', 'none', 'lantern'), ('g2-mundane', 'mundane', 'lantern'), ('g2-heroic', 'heroic', 'lantern'), ('g2-incident', 'incident', 'lantern'), ('g2-meter', 'none', 'meter')):
    p, h = pick(d_, sk, rd); G = games(p); e = h['eval']
    print('  (a,c) %-11s games with a fidelity flag %2d/%d, flags in total %2d | revision %s dirty %s | generate config %s' % (d_, sum(g['flags'] > 0 for g in G), len(G), sum(g['flags'] for g in G), e['revision'].get('commit'), e['revision'].get('dirty'), e.get('model_generate_config')))
for d_ in ('zai-honest-epochs2', 's2-main', 's2-disclosure'):
    p, h = pick(d_); e = h['eval']; print('  (c)   %-18s revision %s dirty %s | generate config %s' % (d_, e['revision'].get('commit'), e['revision'].get('dirty'), e.get('model_generate_config')))
rows = [json.loads(l) for l in open(os.path.join(Z, 'hetero_values.jsonl')) if l.strip()]; k = collections.Counter(r['key'] for r in rows)
print('  (b) hetero_values.jsonl rows %d | unique keys %d | keys with two rows %d (each an error row and its retry: %s)' % (len(rows), len(k), sum(v > 1 for v in k.values()), all(any('error' in r['res'] for r in rows if r['key'] == kk) for kk, v in k.items() if v > 1)))
