"""synth_pav.py -- the analysis on planted counts: IDEAL (0.125 everywhere), NOISY (all arms 0.20), LAYOUT (0.15/0.18/0.22/0.26), COMPILE (opt0 +0.08),
DRIFT (job B +0.04), BROKEN COPIES (best_b +0.05: KG must fail), BOTH (layout + compile). Floor: 200 null worlds (all arms 0.20), count LAYOUT ABOVE."""
import json, numpy as np
from pav import circuit, IDEAL, SHOTS
from pav_fill import analyse
from qiskit.quantum_info import Statevector
qc = circuit().remove_final_measurements(inplace=False); pr = Statevector(qc).probabilities([4]); assert abs(pr[1] - IDEAL) < 1e-12, pr
rng = np.random.default_rng(21)
ARMS = ['best_a', 'best_b', 'q25', 'q50', 'q75', 'best_opt0', 'best_opt3', 'best_jobB']
def world(p):
    out = {}
    for a in ARMS: k = int(rng.binomial(SHOTS, p.get(a, p['_'])) ); out[a] = {'1': k, '0': SHOTS - k}
    return out
W = {'IDEAL': {'_': 0.125}, 'NOISY_FLAT': {'_': 0.20}, 'LAYOUT': {'_': 0.15, 'q25': 0.18, 'q50': 0.22, 'q75': 0.26},
     'COMPILE': {'_': 0.20, 'best_opt0': 0.28}, 'DRIFT': {'_': 0.20, 'best_jobB': 0.24}, 'BROKEN_COPIES': {'_': 0.20, 'best_b': 0.25},
     'BOTH': {'_': 0.15, 'q25': 0.18, 'q50': 0.22, 'q75': 0.26, 'best_opt0': 0.25}}
res = {'ideal_statevector_P1': float(pr[1])}
for k, p in W.items():
    r = analyse(world(p)); res[k] = dict(KG=r['KNOWN_GOOD']['passed'], LAYOUT=r['LAYOUT']['outcome'], COMPILE={a: v['outcome'] for a, v in r['COMPILE'].items()},
                                         DRIFT=r['DRIFT']['outcome'], THEIRS_best=r['THEIRS']['best_a']['vs_0125'])
fl = sum(analyse(world({'_': 0.20}))['LAYOUT']['outcome'].startswith('ABOVE') for _ in range(200)); res['FLOOR_layout_above_in_200_nulls'] = fl
kgf = sum(not analyse(world({'_': 0.20}))['KNOWN_GOOD']['passed'] for _ in range(200)); res['FLOOR_kg_fail_in_200_nulls'] = kgf
open('synth_results_pav.text', 'w').write(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
