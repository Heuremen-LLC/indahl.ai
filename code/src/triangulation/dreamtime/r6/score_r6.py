"""score_r6.py -- THE CURVE, REPEATED, scored as called (DREAMTIME_R6_CALL_20261007.txt, 7b9c1827...): per seat-seed, per checkpoint, pairs late > early-padded AND late > early
(no filler), of all held-out pairs (English, 3 rotations averaged), binomial; the fixed scores: step 200, and the mean share over steps 120-240. Raw."""
import json, os, sys, collections
import numpy as np
from scipy.stats import binomtest
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r6')
ROT = json.load(open(os.path.join(HERE, 'r2_texts.json')))['rotations']
for seat in ('eu_s2', 'eu_s3', 'en_s2'):
    fn = f'{D}/curve_{seat}.jsonl'
    if not os.path.exists(fn): continue
    print(f'\nSEAT {seat}: step | loss | late>padded [p] | late>early [p]')
    sh = {'p': {}, 'e': {}}
    for l in open(fn):
        c = json.loads(l); acc = collections.defaultdict(list)
        for r in c['held']:
            rot = ROT[r['rot']]; h = r['held']; t = sum(h.values()) or 1e-12; acc[(r['arm'], r['pair'])].append(h[rot['COMMIT']] / t)
        P = {k: np.mean(v) for k, v in acc.items()}; pairs = sorted({k[1] for k in P if k[1]}); n = len(pairs)
        lp = sum(P[('L', p)] > P[('EP', p)] for p in pairs); le = sum(P[('L', p)] > P[('E', p)] for p in pairs); sh['p'][c['step']] = lp / n; sh['e'][c['step']] = le / n
        loss = f"{c['loss']:.3f}" if c['loss'] is not None else '  -  '
        print(f"   {c['step']:3} | {loss} | {lp:2}/{n} [{binomtest(lp, n).pvalue:.4f}] | {le:2}/{n} [{binomtest(le, n).pvalue:.4f}]")
    for k, lab in (('p', 'late>padded'), ('e', 'late>early')):
        s200 = sh[k].get(200); m = np.mean([v for s, v in sh[k].items() if 120 <= s <= 240])
        print(f'   FIXED SCORE {lab:11}: step 200 {s200:.2f} | mean 120-240 {m:.2f}')
