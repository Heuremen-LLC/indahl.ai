#!/usr/bin/env python3
"""N1, N2 (PLAN 01ec345, committed before this ran). Nakayashiki and Watanabe, arXiv 2607.29274. Our code. Their JSON read as data; the arm
metadata table is read out of panel-agreement.py as text with ast.literal_eval (nothing of theirs is executed)."""
import json, os, ast, re, statistics
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'anc')
src = open(T + '/panel-agreement.py').read(); META = ast.literal_eval(re.search(r'META = (\{.*?\n\})', src, re.S).group(1))
D = json.load(open(T + '/panel-agreement.json')); P = D['pairs']; TY = D['typicality']
arms = sorted({p['a'] for p in P} | {p['b'] for p in P})
def rank(v): s = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); [r.__setitem__(i, k) for k, i in enumerate(s)]; return r
print('N1 per arm: mean agreement with the other %d arms beside agreement with readers (their typicality), %d arms' % (len(arms) - 1, len(arms)))
mm, mr = [], []
for a in sorted(arms, key=lambda a: -TY[a]['est']):
    v = [p['est'] for p in P if a in (p['a'], p['b'])]; mm.append(statistics.mean(v)); mr.append(TY[a]['est'])
    print('  %-5s %-22s with models %+.3f (n %d) | with readers %+.3f [%+.3f, %+.3f] | ratio %.1f' % (a, META[a][0], mm[-1], len(v), TY[a]['est'], TY[a]['lo'], TY[a]['hi'], mm[-1] / TY[a]['est'] if TY[a]['est'] else float('nan')))
r1, r2 = rank(mm), rank(mr); n = len(r1); rho = 1 - 6 * sum((x - y) ** 2 for x, y in zip(r1, r2)) / (n * (n * n - 1))
print('  Spearman rank correlation across arms, with-models against with-readers: %+.2f (n %d)' % (rho, n))
print('\nN2 Table 2 medians: their stored value (upper middle for even counts) against the exact median')
groups = {
    'same vendor': lambda x, y: META[x][1] == META[y][1], 'different vendor': lambda x, y: META[x][1] != META[y][1],
    'same country': lambda x, y: META[x][2] == META[y][2], 'different country': lambda x, y: META[x][2] != META[y][2],
    'both closed': lambda x, y: META[x][5] == META[y][5] == 'closed', 'both open': lambda x, y: 'open' in META[x][5] and 'open' in META[y][5],
    'both frontier': lambda x, y: META[x][4] == META[y][4] == 'frontier', 'both small': lambda x, y: META[x][4] == META[y][4] == 'small',
    'CROSS-EVERYTHING': lambda x, y: META[x][1] != META[y][1] and META[x][2] != META[y][2] and META[x][4] != META[y][4] and META[x][5] != META[y][5]}
for g, fn in groups.items():
    vs = sorted(p['est'] for p in P if fn(p['a'], p['b']))
    print('  %-18s n %3d | stored %+.4f (prints %+.3f) | exact median %+.4f (prints %+.3f) | %s' % (g, len(vs), D['groups'][g]['median'], D['groups'][g]['median'], statistics.median(vs), statistics.median(vs), 'same' if round(D['groups'][g]['median'], 3) == round(statistics.median(vs), 3) else 'differs at the third place'))
print('\nReading note (after the referee pass): both columns come from the same per-arm excess machinery and the pair matrix is close to rank one,')
print('so the release cannot tell whether the shared factor is the model or how many sentences each arm returns (their HARNESS-DEFECTS.md, D1);')
print('the rankings needed to test it are not released. The paper reports the group version (newer models closer to readers and to each other).')
print('Of the medians, two are printed in the paper (Table 2): both closed +0.174 (exact +0.172) and same country +0.090 (exact +0.089).')
