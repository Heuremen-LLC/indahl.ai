"""score_curve.py -- THE CURVE (r3; call DREAMTIME_R3_CALL_20261007.txt, 9879eef1...). Per seat, per checkpoint: QUBIT discrimination (held P(COMMIT): late minus early-padded,
mean over 15 pairs and 3 rotations; and pairs late > padded of 15) in en / th / eu, and the INORGANIC pull (idle arms: P(HOLD) in th / eu minus en, short + padded averaged),
plus the training loss. Printed as rows and a text bar per checkpoint. Raw."""
import json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r3')
X = json.load(open(os.path.join(HERE, 'r2_texts.json'))); ROT = X['rotations']; M = ('COMMIT', 'HOLD', 'NEXT')
def dist(rows):
    acc = collections.defaultdict(list)
    for r in rows:
        rot = ROT[r['rot']]; h = r['held']; t = sum(h.values()) or 1e-12
        acc[(r['lang'], r['arm'], r['pair'])].append(np.array([h[rot[m]] / t for m in M]))
    return {k: np.mean(v, 0) for k, v in acc.items()}
bar = lambda v, s=40: ('#' * int(round(max(0, v) * s))).ljust(int(s * 0.6)) if v == v else ''
for seat in ('en', 'th', 'eu'):
    fn = f'{D}/curve_{seat}.jsonl'
    if not os.path.exists(fn): continue
    C = [json.loads(l) for l in open(fn)]
    print(f'\nSEAT {seat}  (step | loss | QUBIT discrimination en / th / eu  [pairs late>padded of 15] | INORGANIC pull P(HOLD) th / eu vs en)')
    for c in C:
        P = dist(c['held']); pairs = sorted({k[2] for k in P if k[2]}); row = []
        for L in ('en', 'th', 'eu'):
            d = [P[(L, 'L', p)][0] - P[(L, 'EP', p)][0] for p in pairs]; row.append((np.mean(d), sum(x > 0 for x in d)))
        pull = [np.mean([P[(L, a, None)][1] - P[('en', a, None)][1] for a in ('N', 'NP')]) for L in ('th', 'eu')]
        loss = f"{c['loss']:.3f}" if c['loss'] is not None else '  -  '
        print(f"   {c['step']:3} | {loss} | " + '  '.join(f'{L} {v:+.3f} [{w:2}]' for L, (v, w) in zip(('en', 'th', 'eu'), row)) + f" | th {pull[0]:+.3f}  eu {pull[1]:+.3f}")
    print('   curve, English qubit discrimination (late - padded, x40):')
    for c in C:
        P = dist(c['held']); pairs = sorted({k[2] for k in P if k[2]}); v = np.mean([P[('en', 'L', p)][0] - P[('en', 'EP', p)][0] for p in pairs])
        print(f"   {c['step']:3} {'|' + bar(v)} {v:+.3f}")
