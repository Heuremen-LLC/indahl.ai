#!/usr/bin/env python3
"""Q1, Q2 (PLAN ec9e65a, committed before this ran). Saqlain, arXiv 2610.29812. Our code; his cache and results read as data only."""
import json, os, math, collections
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
L = [json.loads(l) for l in open(T + '/cache/pubmed.jsonl')]
by = collections.defaultdict(list)
for k, v in L: by[k].append(v)
rep = {k: vs for k, vs in by.items() if k.startswith('search:') and len(vs) > 1}
memb = sum(1 for vs in rep.values() if len({frozenset(v) for v in vs}) > 1)
order = sum(1 for vs in rep.values() if len({tuple(v) for v in vs}) > 1 and len({frozenset(v) for v in vs}) == 1)
print('Q1 PubMed searches cached more than once: %d | returned a different set of PMIDs: %d | same set, different order only: %d | identical: %d'
      % (len(rep), memb, order, len(rep) - memb - order))
print('   copies per repeated search: %s; the replay loader keeps the last copy of each key' % dict(collections.Counter(len(v) for v in rep.values())))
def load(m, c): return {d['id']: d for d in (json.loads(l) for l in open('%s/results/%s__%s.jsonl' % (T, m, c)))}
def mcn(b, c):
    n = b + c; return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n) if n else 1.0
print('\nQ2 accuracy on claims whose gold is SUPPORT or CONTRADICT, per harness, and oracle against each harness paired per claim')
S = json.load(open(T + '/results/summary.json'))
for m in sorted(S):
    R = {c: load(m, c) for c in ('closed', 'single', 'agent', 'oracle')}
    sc = [i for i, d in R['oracle'].items() if d['gold'] in ('SUPPORT', 'CONTRADICT')]
    ok = {c: {i: R[c][i]['label'] == R[c][i]['gold'] for i in sc if i in R[c]} for c in R}
    allacc = {c: sum(R[c][i]['label'] == R[c][i]['gold'] for i in R[c]) / len(R[c]) for c in R}
    print('  %s: SUPPORT/CONTRADICT claims %d | %s' % (m, len(sc), ' | '.join('%s %d/%d (all-claim accuracy %.2f, stored %.2f)' % (c, sum(ok[c].values()), len(ok[c]), allacc[c], S[m][c]['acc']) for c in R)))
    for c in ('closed', 'single', 'agent'):
        b = sum(ok['oracle'][i] and not ok[c][i] for i in sc); cc = sum(ok[c][i] and not ok['oracle'][i] for i in sc)
        print('     oracle against %-6s: oracle-only right %2d, %s-only right %2d, exact McNemar p %.3g' % (c, b, c, cc, mcn(b, cc)))
# Q2 second ruler (same reading): the paired difference in SUPPORT/CONTRADICT accuracy, oracle minus each harness, with a 95% paired bootstrap
# over the 64 claims (10,000 resamples, seeds 1, 2, 3), so "without sacrificing" can be read as a bound.
import random
print('\nQ2 paired difference, oracle minus harness, SUPPORT/CONTRADICT claims, 95% paired bootstrap (three seeds)')
for m in sorted(S):
    R = {c: load(m, c) for c in ('closed', 'single', 'agent', 'oracle')}
    sc = [i for i, d in R['oracle'].items() if d['gold'] in ('SUPPORT', 'CONTRADICT')]
    for c in ('closed', 'agent'):
        d = [int(R['oracle'][i]['label'] == R['oracle'][i]['gold']) - int(R[c][i]['label'] == R[c][i]['gold']) for i in sc]
        cis = []
        for seed in (1, 2, 3):
            rg = random.Random(seed); bs = sorted(sum(d[rg.randrange(len(d))] for _ in d) / len(d) for _ in range(10000)); cis.append((bs[249], bs[9749]))
        print('  %-22s oracle minus %-6s %+.3f %s' % (m, c, sum(d) / len(d), ' '.join('[%+.3f, %+.3f]' % x for x in cis)))

# Addendum 1 (Q1b, Q2b, Q2c)
print('\nQ1b each differing repeated search: which backbone results file recorded the first and the second cached list')
recs = {m: {} for m in S}
for m in S:
    for c in ('single', 'agent'):
        for d in load(m, c).values():
            import ast as _ast
            qs = d.get('queries') or []; qs = _ast.literal_eval(qs) if isinstance(qs, str) else qs   # stored as text in his files
            rt = d.get('retrieved') or []; rt = _ast.literal_eval(rt) if isinstance(rt, str) else rt
            for q in qs: recs[m].setdefault(q, set()).add(tuple(rt))   # keyed by query text; cache keys are search:<retmax>:<query>
for k, vs in rep.items():
    if len({tuple(v) for v in vs}) > 1:
        qt = k.split(':', 2)[2]
        who = lambda lst: [m.split('-')[1] for m in S if any(tuple(lst) == r for r in recs[m].get(qt, set()))]
        print('  %-62s first list in %s | second list in %s' % (k[:62], who(vs[0]) or '-', who(vs[1]) or '-'))
print('  his loader reads the cache line by line into a dict, so the last line for a key wins')
print('\nQ2b oracle minus each harness on SUPPORT/CONTRADICT, paired bootstrap 95% (seed 1); Q2c predicted NEI against 36 gold NEI, NEI precision')
for m in sorted(S):
    R = {c: load(m, c) for c in ('closed', 'single', 'agent', 'oracle')}
    sc = [i for i, d in R['oracle'].items() if d['gold'] in ('SUPPORT', 'CONTRADICT')]
    for c in ('closed', 'single', 'agent'):
        d = [int(R['oracle'][i]['label'] == R['oracle'][i]['gold']) - int(R[c][i]['label'] == R[c][i]['gold']) for i in sc]
        rg = random.Random(1); bs = sorted(sum(d[rg.randrange(len(d))] for _ in d) / len(d) for _ in range(10000))
        print('  %-22s oracle minus %-6s %+.3f [%+.3f, %+.3f]' % (m, c, sum(d) / len(d), bs[249], bs[9749]))
    for c in ('closed', 'single', 'agent', 'oracle'):
        pn = [i for i, d in R[c].items() if d['label'] == 'NEI']; tp = sum(R[c][i]['gold'] == 'NEI' for i in pn)
        abst_sc = sum(R[c][i]['label'] == 'NEI' for i in sc)
        print('     %-6s predicts NEI on %2d (gold NEI 36) | NEI precision %.2f | abstains on %2d of the 64 SUPPORT/CONTRADICT claims' % (c, len(pn), tp / len(pn) if pn else float('nan'), abst_sc))
