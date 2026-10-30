#!/usr/bin/env python3
"""Known-good for Bronder, arXiv 2607.14399 (PLAN 59f10de). Table 2, Table 3, Gate 2 meter and none-lantern strong-claim rates."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import pick, games, valid, outcome, strong, won, false_verdict
g0 = games(pick('zai-honest-epochs2')[0]); s2 = games(pick('s2-main')[0]); sd = games(pick('s2-disclosure')[0])
anchors = sorted({g['inst'] for g in g0} & {g['inst'] for g in s2}); print('anchors in both Gate 0 and s2-main:', anchors)
for nm, G in (('Gate 0 (binary)', g0), ('series 2 (three-verdict)', s2)):
    c = collections.Counter(outcome(g) if valid(g) else 'invalid' for g in G if g['inst'] in anchors)
    print('  %-26s %s | strong %d/%d' % (nm, dict(c), sum(strong(g) for g in G if g['inst'] in anchors), sum(1 for g in G if g['inst'] in anchors)))
print('wins anywhere (event types win/won/quest_complete): s2-main %d, disclosure %d | terminals s2-main %s, disclosure %s' % (sum(won(g) for g in s2), sum(won(g) for g in sd), dict(collections.Counter(g['terminal'] for g in s2)), dict(collections.Counter(g['terminal'] for g in sd))))
six = sorted({g['inst'] for g in sd}); H = [g for g in s2 if g['inst'] in six]
for nm, G in (('hidden (s2-main, six instances)', H), ('disclosed (s2-disclosure)', sd)):
    V = [g for g in G if valid(g)]
    print('  %-32s valid %d/%d | HALT %d | false %d | pin games %d' % (nm, len(V), len(G), sum(g['terminal'] == 'HALT' for g in V), sum(false_verdict(g) for g in V), sum(g['events'].get('pin', 0) > 0 for g in V)))
for d, sk, rd in (('g2-meter', 'none', 'meter'), ('g2-none', 'none', 'lantern')):
    G = [g for g in games(pick(d, sk, rd)[0]) if valid(g)]
    print('  %-9s strong %d/%d = %.3f' % (d, sum(strong(g) for g in G), len(G), sum(strong(g) for g in G) / len(G)))
