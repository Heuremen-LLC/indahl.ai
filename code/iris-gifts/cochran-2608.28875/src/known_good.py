#!/usr/bin/env python3
"""known_good.py (ours): H1 of Cochran, Dodson and Nore (arXiv 2608.28875) from their per_side_outcomes.csv. Per side, paired difference
in WER points (full - none) per model; median; 10,000-resample bootstrap percentile 95% CI over sides (three seeds); Wilcoxon signed-rank,
zero differences dropped, exact two-sided p by full enumeration of signs (n = 19 allows it). Reads their file as data only."""
import csv, os, itertools, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theirs', 'release', 'per_side_outcomes.csv')
W = {}
for r in csv.DictReader(open(T)): W[(r['side_id'], r['model'], r['arm'])] = float(r['wer']) * 100
sides = sorted({k[0] for k in W}); models = sorted({k[1] for k in W})
def wilcoxon_exact(d):
    d = np.array([x for x in d if x != 0]); n = len(d); a = np.abs(d); order = a.argsort(); ranks = np.empty(n)
    i = 0; s = a[order]
    while i < n:   # average ranks for ties
        j = i
        while j + 1 < n and s[j + 1] == s[i]: j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    wplus = ranks[d > 0].sum(); signs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(bool)
    dist = (signs * ranks).sum(1); mu = ranks.sum() / 2; obs = abs(wplus - mu)
    return n, wplus, float((np.abs(dist - mu) >= obs - 1e-9).mean())
for m in models:
    d = np.array([W[(s, m, 'full')] - W[(s, m, 'none')] for s in sides])
    cis = []
    for seed in (20260710, 1, 2):
        rng = np.random.default_rng(seed); i = rng.integers(0, len(d), size=(10000, len(d))); cis.append(np.percentile(np.median(d[i], 1), [2.5, 97.5]))
    n, wp, p = wilcoxon_exact(d)
    print('%-18s n %d  median full-none %+.2f WER pt  95%% CI (three seeds) %s  Wilcoxon exact p %.3f (n nonzero %d, W+ %.1f)' % (m, len(d), np.median(d), ' '.join('[%+.2f, %+.2f]' % tuple(c) for c in cis), p, n, wp))
