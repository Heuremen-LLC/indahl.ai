import numpy as np; from shch_layout import analyse, ARMS
from shch import SHOTS
rng = np.random.default_rng(17)
def cnt(E):
    k = rng.binomial(SHOTS, (1 + E) / 2); return {'00': k // 2, '11': k - k // 2, '01': (SHOTS - k) // 2, '10': SHOTS - k - (SHOTS - k) // 2}
def arm(S, prod=1.37):
    e = S / 4; ep = prod / 4; return [cnt(x) for x in (-e, e, -e, -e)] + [cnt(x) for x in (-ep, ep, -ep, -ep)]
L = []
for name, Ss, want in (('NO layout effect', {'best_a': 2.65, 'best_b': 2.65, 'q25': 2.65, 'q50': 2.65, 'q75': 2.65}, 'CONSISTENT'),
                       ('LAYOUT spread 0.3', {'best_a': 2.72, 'best_b': 2.72, 'q25': 2.62, 'q50': 2.52, 'q75': 2.42}, 'ABOVE')):
    r = analyse({a: arm(Ss[a]) for a in ARMS}); L.append('%-18s range %.3f p %.4f -> %s | KG %s -> %s' % (name, r['LAYOUT']['range'], r['LAYOUT']['p'], r['LAYOUT']['outcome'], r['KNOWN_GOOD']['passed'], 'PASS' if want in r['LAYOUT']['outcome'] and r['KNOWN_GOOD']['passed'] else 'FAIL'))
r = analyse({a: arm(2.65 if a != 'best_b' else 2.35) for a in ARMS}); L.append('BROKEN copies (best_b off by 0.3): KG %s (want False) %s' % (r['KNOWN_GOOD']['passed'], 'PASS' if not r['KNOWN_GOOD']['passed'] else 'FAIL'))
fp = sum('ABOVE' in analyse({a: arm(2.65) for a in ARMS})['LAYOUT']['outcome'] for _ in range(200)); L.append('FLOOR: no-layout world, 200 draws, layout resolves %d (expect ~5%%)' % fp)
open('synth_results_shch_layout.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
