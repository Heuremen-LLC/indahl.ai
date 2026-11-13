import json, collections as C
mine = json.load(open('../out/rows.json')); desk = json.load(open('/Users/heuremen/bones-forge/steo_index/data/steo.json'))['rows']
S = json.load(open('/Users/heuremen/bones-forge/steo_index/summary_steo.json'))
k = lambda r: (r['issue'], r['series'], r.get('ym') or r.get('month'))
M = {k(r): r for r in mine}; Dk = {k(r): r for r in desk}
print(len(M), len(Dk), len(mine), len(desk))
print('only mine', len(set(M)-set(Dk)), 'only desk', len(set(Dk)-set(M)))
for x in sorted(set(Dk)-set(M))[:50]: print('desk only', x, {a: Dk[x][a] for a in ('lower','upper','spot','outcome','copy','released')})
for x in sorted(set(M)-set(Dk))[:50]: print('mine only', x, M[x])
d = 0
for x in set(M) & set(Dk):
    a, b = M[x], Dk[x]
    if (a['lo'], a['up'], a['spot'], a['lead']) != (b['lower'], b['upper'], b['spot'], b['lead']) or a['out'] != b['outcome_add1'] and False: d += 1; print('val diff', x, a, b)
print('value diffs', d)
print(S['rows'], S['sources'])
