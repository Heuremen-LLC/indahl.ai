#!/usr/bin/env python3
"""known_good.py (ours): Prejzner, arXiv 2609.32042. Pass rate per model and quantization on the 67-task main suite with repair off, and
the Q3_K_M to Q2_K paired table (n11, n10, n01, n00) with an exact two-sided McNemar p. Reads per_task_main67.csv as data only."""
import csv, os, math, collections
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'release_data', 'matrices', 'per_task_main67.csv')
P = collections.defaultdict(dict)
for r in csv.DictReader(open(T)):
    if r['suite'] == 'main67' and r['repair'] == 'off': P[(r['model_id'], r['quant'])][r['task_id']] = int(r['passed'])
Q = ['Q8_0', 'Q6_K', 'Q5_K_M', 'Q4_K_M', 'Q3_K_M', 'Q2_K']
for m in sorted({k[0] for k in P}):
    print('%-24s %s' % (m, '  '.join('%s %.3f (n %d)' % (q, sum(P[(m, q)].values()) / len(P[(m, q)]), len(P[(m, q)])) for q in Q if (m, q) in P)))
    a, b = P[(m, 'Q3_K_M')], P[(m, 'Q2_K')]; t = sorted(set(a) & set(b))
    n11 = sum(a[x] and b[x] for x in t); n10 = sum(a[x] and not b[x] for x in t); n01 = sum(not a[x] and b[x] for x in t); n00 = len(t) - n11 - n10 - n01
    N = n10 + n01; p = min(1.0, 2 * sum(math.comb(N, i) for i in range(min(n10, n01) + 1)) / 2 ** N)
    print('   Q3_K_M to Q2_K: %.3f to %.3f | n11 %d n10 %d n01 %d n00 %d | exact McNemar p %.5f' % ((n11 + n10) / len(t), (n11 + n01) / len(t), n11, n10, n01, n00, p))
