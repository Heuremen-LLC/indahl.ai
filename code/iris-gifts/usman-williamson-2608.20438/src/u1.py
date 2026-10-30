#!/usr/bin/env python3
"""U1 (PLAN f08f83e and Addendum 1, committed before this ran): round-0 honest-agent post text across the four conditions of each block."""
import json, os, glob, collections
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'hf_64d770e', 'confirmatory')
blocks = collections.defaultdict(dict)
for p in glob.glob(T + '/*/*/*/seed*/*/posts.jsonl'):
    parts = p.split('/'); panel, model, topic, seed, cond = parts[-6:-1]
    cfg = json.load(open(os.path.join(os.path.dirname(p), 'config.json')))
    r0 = {}
    for l in open(p):
        d = json.loads(l)
        if d['round'] == 0 and d['agent_id'].startswith('a'): r0[d['agent_id']] = d['text']
    blocks[(panel, model, topic, seed)][cond] = (cfg.get('seed'), cfg.get('parallel_requests'), r0)
per = collections.defaultdict(lambda: collections.Counter()); seedbad = 0; incomplete = 0
for (panel, model, topic, seed), cs in sorted(blocks.items()):
    if len(cs) != 4: incomplete += 1; continue
    seeds = {v[0] for v in cs.values()}
    if len(seeds) != 1: seedbad += 1; continue
    agents = set.intersection(*(set(v[2]) for v in cs.values()))
    for a in agents:
        texts = {v[2][a] for v in cs.values()}
        per[(panel, model)]['identical' if len(texts) == 1 else 'differ'] += 1
    per[(panel, model)]['blocks'] += 1; per[(panel, model)]['parallel %s' % ({v[1] for v in cs.values()},)] += 1
print('blocks with other than four conditions: %d | blocks whose conditions carry different config seeds: %d' % (incomplete, seedbad))
tot = collections.Counter()
for (panel, model), c in sorted(per.items()):
    n = c['identical'] + c['differ']; tot['identical'] += c['identical']; tot['differ'] += c['differ']
    print('%-22s %-14s blocks %3d | round-0 honest agents %4d: identical in all four conditions %4d, differ %4d (%.3f) | %s' % (panel, model, c['blocks'], n, c['identical'], c['differ'], c['differ'] / n, [k for k in c if k.startswith('parallel')]))
n = tot['identical'] + tot['differ']; print('all: %d agents, identical %d, differ %d (%.3f)' % (n, tot['identical'], tot['differ'], tot['differ'] / n))
print('Bounds: posts are stored cut at 180 characters, so identical counts are upper bounds and differ counts lower bounds. The request is')
print('identical (prompt rebuilt byte for byte by the referee for all 1,344 agents); server state and the mix of concurrent requests are not,')
print('so this is a repeat floor for the whole serving setup as they ran it, not for sampling alone. No cause is named.')
