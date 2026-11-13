"""score_r5.py -- THE NATIVE MATCH scored as called (DREAMTIME_R5_CALL_20261007.txt, 9eeb4ee2...): per seat x language x ruler, pairs with held P(COMMIT) on LATE > on
EARLY-PADDED (digit marks, 3 rotations averaged), binomial vs 50%. The filler leg beside: late > early (unpadded), and the filler's own pull (EP - E). Raw."""
import json, os, sys, collections
import numpy as np
from scipy.stats import binomtest
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r5')
ROT = json.load(open(os.path.join(HERE, 'r2_texts.json')))['rotations']; M = ('COMMIT', 'HOLD', 'NEXT')
acc = collections.defaultdict(list)
for s in ('en', 'th', 'eu'):
    if not os.path.exists(f'{D}/r5_{s}.jsonl'): continue
    for l in open(f'{D}/r5_{s}.jsonl'):
        r = json.loads(l); rot = ROT[r['rot']]; h = r['held']; t = sum(h.values()) or 1e-12
        acc[(r['seat'], r['ruler'], r['lang'], r['arm'], r['pair'])].append(h[rot['COMMIT']] / t)
P = {k: float(np.mean(v)) for k, v in acc.items()}; pairs = sorted({k[4] for k in P if k[4]})
print(f'THE NATIVE MATCH, {len(pairs)} fresh pairs. Cells: seat / ruler / language. late>padded [p] | late>early (no filler) [p] | filler pull EP-E (mean P(C))')
for s in ('en', 'th', 'eu'):
    for ru, L in (('en', 'en'), ('nllb', 'th'), ('nllb', 'eu'), ('madlad', 'th'), ('madlad', 'eu')):
        if (s, ru, L, 'L', pairs[0]) not in P: continue
        lp = sum(P[(s, ru, L, 'L', p)] > P[(s, ru, L, 'EP', p)] for p in pairs); le = sum(P[(s, ru, L, 'L', p)] > P[(s, ru, L, 'E', p)] for p in pairs)
        fp = np.mean([P[(s, ru, L, 'EP', p)] - P[(s, ru, L, 'E', p)] for p in pairs]); n = len(pairs)
        tag = ' <- NATIVE' if (s, L) in (('th', 'th'), ('eu', 'eu')) else ''
        print(f'   seat {s} {ru:6} {L} | {lp:2}/{n} [{binomtest(lp, n).pvalue:.4f}] | {le:2}/{n} [{binomtest(le, n).pvalue:.4f}] | {fp:+.3f}{tag}')
