"""synth_vqc.py -- planted worlds on the real 84 exact probabilities: EXACT (lam 1), FLAT (lam 0.8 every arm), LAYOUT (0.85/0.75/0.6/0.45),
DRIFT (job B lam -0.15), BROKEN COPIES (theirs_b lam -0.15). Floors over 200 flat nulls."""
import json, numpy as np
from vqc import features, p_exact, SHOTS
from vqc_fill import analyse
Q, y = features(); pe = np.array([p_exact(x) for x in Q]); rng = np.random.default_rng(3)
ARMS = ['theirs_a', 'theirs_b', 'best', 'q50', 'q75', 'theirs_jobB']
def world(L):
    raw = {}
    for a in ARMS:
        p = 0.5 + (0.06 if (a == 'q75' and 'OFF' in str(L)) else 0) + L.get(a, L['_']) * (pe - 0.5); k = rng.binomial(SHOTS, p); raw[a] = [{'0001': int(ki), '0000': int(SHOTS - ki)} for ki in k]
    return raw
W = {'OFFSET_LAYOUT': {'_': 0.8, 'q75': 0.8, 'OFF': 1}, 'EXACT': {'_': 1.0}, 'FLAT': {'_': 0.8}, 'LAYOUT': {'_': 0.85, 'q50': 0.6, 'q75': 0.45, 'best': 0.75}, 'DRIFT': {'_': 0.8, 'theirs_jobB': 0.65}, 'BROKEN_COPIES': {'_': 0.8, 'theirs_b': 0.65}}
res = {}
for k, L in W.items():
    r = analyse(world(L), pe, y); res[k] = dict(KG=r['KNOWN_GOOD']['passed'], LAYOUT=r['LAYOUT']['outcome'], DRIFT=r['DRIFT']['outcome'], lam=[round(x, 3) for x in r['LAYOUT']['lam']], acc=r['LAYOUT']['accuracy'], offset_p=round(r['LAYOUT_OFFSET']['p'], 4))
res['FLOOR_layout_above_200'] = sum(analyse(world({'_': 0.8}), pe, y)['LAYOUT']['outcome'].startswith('ABOVE') for _ in range(200))
res['FLOOR_kg_fail_200'] = sum(not analyse(world({'_': 0.8}), pe, y)['KNOWN_GOOD']['passed'] for _ in range(200))
open('synth_results_vqc.text', 'w').write(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
