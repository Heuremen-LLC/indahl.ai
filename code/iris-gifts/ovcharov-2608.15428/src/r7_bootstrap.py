#!/usr/bin/env python3
"""R7 (PLAN Addendum 2, committed 618b624 before this ran): paired item bootstrap of each model's excess = blind - habit, habit = sum_j q_j g_j
with q the model's answer shares and g the gold shares of the items its reply was parsed on (the rule that rebuilds his Table 4).
2,000 resamples, 95% percentile interval, three seeds (20261030, 1, 2). Outcome against zero and against +0.015 (his largest "within" excess).
A bound whose seed-to-seed spread reaches its distance from the line is an edge: CANNOT_TELL on that line with this ruler.
Reads his scenario_a.jsonl as data only. Pixtral Large left out (partial file)."""
import json, os, collections, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs')
rows = collections.defaultdict(list)
for l in open(T + '/predictions/scenario_a.jsonl'):
    r = json.loads(l)
    if r.get('pred') in (0, 1, 2, 3): rows[r['model']].append((r['pred'], r['gold']))
B, SEEDS = 2000, (20261030, 1, 2)
def stat(p, g):
    acc = (p == g).mean(-1); h = sum((p == j).mean(-1) * (g == j).mean(-1) for j in range(4)); return acc, h, acc - h
def verdict(bounds, line):
    lo, hi = bounds[:, 0], bounds[:, 1]
    if (lo > line).all(): side, d, sp = 'ABOVE', lo.min() - line, np.ptp(lo)
    elif (hi < line).all(): side, d, sp = 'BELOW', line - hi.max(), np.ptp(hi)
    elif (lo <= line).all() and (hi >= line).all(): return 'CONSISTENT'
    else: return 'CANNOT_TELL (edge)'
    return side if d > sp else 'CANNOT_TELL (edge)'
print('model            n     blind   habit   excess   95% bounds, seeds 20261030 / 1 / 2                      vs 0                 vs +0.015')
for m in sorted(rows):
    if m == 'pixtral-large': continue
    a = np.array(rows[m]); p, g = a[:, 0], a[:, 1]; n = len(a); acc, h, ex = stat(p, g); bs = []
    for s in SEEDS:
        i = np.random.default_rng(s).integers(0, n, size=(B, n)); bs.append(np.percentile(stat(p[i], g[i])[2], [2.5, 97.5]))
    bs = np.array(bs)
    print('%-15s %5d   %.3f   %.3f   %+.4f  %s   %-20s %s%s' % (m, n, acc, h, ex, ' '.join('[%+.4f, %+.4f]' % tuple(b) for b in bs),
          verdict(bs, 0.0), verdict(bs, 0.015), "   (the gate's own model)" if m == 'haiku-4.5' else ''))
