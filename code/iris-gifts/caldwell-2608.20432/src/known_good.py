#!/usr/bin/env python3
"""Known-good for Caldwell, arXiv 2608.20432 (PLAN 9f4b8a9). Alignment per judge from the released traces, ties as misses (their metrics.py)."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JUDGES, PRINTED, load, pairs
for j in JUDGES:
    P = load(j); pr = pairs(P); c = collections.Counter(pr.values()); n = len(pr)
    miss = collections.Counter((v2, k[2]) for k, v in P.items() for v2 in ('initial', 'final') if v2 not in v)
    decl = {(k[0], k[1]) for k in P}
    absent = len(decl) * 3 - len(P)   # (declaration, replicate) keys with neither trajectory
    print('%-24s declarations %d | complete pairs %d | aligned %d tie %d inverted %d | alignment %.1f%% (printed %.1f) | pairs with one trajectory missing %s, with both missing %d' % (
        j, len(decl), n, c['aligned'], c['tie'], c['inverted'], 100 * c['aligned'] / n, PRINTED[j][0], dict(miss) or 'none', absent))
