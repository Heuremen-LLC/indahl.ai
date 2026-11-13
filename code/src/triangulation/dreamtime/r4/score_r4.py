"""score_r4.py -- THE BISCUIT under two rulers (call DREAMTIME_R4_CALL_20261007.txt, 49765f5e...). Idle-arm mode distribution (3 rotations averaged): P(HOLD) in L minus English,
per seat, Bones' text vs NLLB's; the compass (late vs early-padded) under each ruler. Raw."""
import json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r4')
ROT = json.load(open(os.path.join(HERE, 'r2_texts.json')))['rotations']; M = ('COMMIT', 'HOLD', 'NEXT')
R = [json.loads(l) for s in ('en', 'th', 'eu') if os.path.exists(f'{D}/r4_{s}.jsonl') for l in open(f'{D}/r4_{s}.jsonl')]
acc = collections.defaultdict(list)
for r in R:
    rot = ROT[r['rot']]; h = r['held']; t = sum(h.values()) or 1e-12; acc[(r['seat'], r['ruler'], r['lang'], r['arm'], r['pair'])].append(np.array([h[rot[m]] / t for m in M]))
P = {k: np.mean(v, 0) for k, v in acc.items()}
print('THE BISCUIT UNDER TWO RULERS: idle-arm P(HOLD) in L minus English (mean of N and NP), and P(COMMIT) beside')
for s in ('en', 'th', 'eu'):
    for L in ('th', 'eu'):
        row = []
        for ru in ('bones', 'nllb'):
            dh = np.mean([P[(s, ru, L, a, None)][1] - P[(s, 'bones', 'en', a, None)][1] for a in ('N', 'NP')]); dc = np.mean([P[(s, ru, L, a, None)][0] - P[(s, 'bones', 'en', a, None)][0] for a in ('N', 'NP')])
            row.append(f'{ru:5} HOLD {dh:+.3f} COMMIT {dc:+.3f}')
        print(f'   seat {s} in {L}: ' + '  |  '.join(row))
print('THE COMPASS under each ruler: pairs late > early-padded of 15 (held P(COMMIT))')
pairs = sorted({k[4] for k in P if k[4]})
for s in ('en', 'th', 'eu'):
    for L in ('th', 'eu'):
        print(f'   seat {s} in {L}: ' + '  '.join(f"{ru} {sum(P[(s, ru, L, 'L', p)][0] > P[(s, ru, L, 'EP', p)][0] for p in pairs)}/15" for ru in ('bones', 'nllb')))
