#!/usr/bin/env python3
"""R7b (PLAN Addendum 5, 141db96, committed before this ran; defined after the data): R7 with unparsed replies counted as wrong.
Blind accuracy over every item id asked (an id with any parsed row takes it), habit over the parsed items as in R7. Paired bootstrap over ids,
2,000 resamples, seed 20261030. His scenario_a.jsonl read as data only; Pixtral Large left out (partial file)."""
import json, os, collections, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
byid = collections.defaultdict(dict)
for l in open(T + '/predictions/scenario_a.jsonl'):
    r = json.loads(l); d = byid[r['model']]
    if r['id'] not in d or (d[r['id']][0] is None and r.get('pred') in (0, 1, 2, 3)): d[r['id']] = (r.get('pred') if r.get('pred') in (0, 1, 2, 3) else None, r['gold'])
def stat(p, g, ok):
    acc = ((p == g) & ok).mean(-1); w = ok.sum(-1)
    h = sum(((p == j) & ok).sum(-1) / w * ((g == j) & ok).sum(-1) / w for j in range(4)); return acc, h, acc - h
print('model            ids   parsed   blind (unparsed wrong)   habit   excess   95% bound')
for m in sorted(byid):
    if m == 'pixtral-large': continue
    v = list(byid[m].values()); ok = np.array([x[0] is not None for x in v]); p = np.array([x[0] if x[0] is not None else -1 for x in v]); g = np.array([x[1] for x in v]); n = len(v)
    acc, h, ex = stat(p, g, ok); i = np.random.default_rng(20261030).integers(0, n, size=(2000, n)); lo, hi = np.percentile(stat(p[i], g[i], ok[i])[2], [2.5, 97.5])
    print('%-15s %5d   %5d    %.4f                   %.4f   %+.4f  [%+.4f, %+.4f]%s' % (m, n, ok.sum(), acc, h, ex, lo, hi, "   (the gate's own model)" if m == 'haiku-4.5' else ''))
