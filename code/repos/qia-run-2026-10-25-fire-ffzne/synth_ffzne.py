"""synth_ffzne.py -- planted worlds with the chosen scores: LINEAR (<Z> = 1 - 0.9 score), LINEAR_OFFSET (<Z> = 0.95 - 0.9 score), LAYOUT_NOT_SCORE
(per-layout values scrambled: q25 lowest), BROKEN COPIES (s1_b - 0.05), DRIFT (job B - 0.04). Width per arm 0.004. Floors over 200 linear nulls."""
import json, numpy as np
from ffzne_fill import analyse
L = json.load(open('layouts_chosen.json')); sc = {k: L[k]['score'] for k in ('s1', 'mid', 'worst', 'q25', 'q75')}; rng = np.random.default_rng(5)
ARMS = ['s1_a', 's1_b', 'mid', 'worst', 'q25', 'q75', 's1_jobB']
def world(f, extra={}):
    return {a: (f(sc[a.split('_')[0]]) + extra.get(a, 0) + rng.normal(0, 0.004), 0.004) for a in ARMS}
W = {'LINEAR': (lambda s: 1 - 0.9 * s, {}), 'LINEAR_OFFSET': (lambda s: 0.95 - 0.9 * s, {}), 'LAYOUT_NOT_SCORE': (lambda s: 1 - 0.9 * s, {'q25': -0.12, 'mid': +0.05}),
     'BROKEN_COPIES': (lambda s: 1 - 0.9 * s, {'s1_b': -0.05}), 'DRIFT': (lambda s: 1 - 0.9 * s, {'s1_jobB': -0.04})}
res = {}
for k, (f, ex) in W.items():
    r = analyse(world(f, ex), sc); res[k] = dict(KG=r['KNOWN_GOOD']['passed'], THEIRS_E0=round(r['THEIRS']['E0'], 4), LINEAR=r['LINEAR']['outcome'], PAIR=r['PAIR']['outcome'], E0_spread=round(r['E0_spread'], 4), DRIFT=r['DRIFT']['outcome'])
res['FLOOR_linear_above_200'] = sum(analyse(world(lambda s: 1 - 0.9 * s), sc)['LINEAR']['outcome'].startswith('ABOVE') for _ in range(200))
res['FLOOR_kg_fail_200'] = sum(not analyse(world(lambda s: 1 - 0.9 * s), sc)['KNOWN_GOOD']['passed'] for _ in range(200))
open('synth_results_ffzne.text', 'w').write(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
