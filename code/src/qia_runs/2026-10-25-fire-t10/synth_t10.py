"""synth_t10.py -- planted worlds: SAME (all arms T 250 except free 150), THEIRS_EVERYWHERE (t10 345, cpmg 313, free 238 on all qubits),
QUBIT_DEPENDENT (t10 - cpmg = +60, 0, -30, +30), BROKEN COPIES (t10 copy b -40% on q0), DRIFT (job B t10 -30%). A = 0.45, binomial 2,000 shots.
Floors over 200 SAME-world nulls."""
import json, numpy as np
from t10 import DELAYS_US, SHOTS
from t10_fill import analyse
rng = np.random.default_rng(10); t = np.array(DELAYS_US, float)
def counts(Ts):
    out = []
    for tt in t:
        ps = [0.5 + 0.45 * np.exp(-tt / T) for T in Ts]; bits = [rng.random(SHOTS) < p for p in ps]
        keys = [''.join('1' if bits[i][s] else '0' for i in range(4))[::-1] for s in range(SHOTS)]
        c = {}
        for k in keys: c[k] = c.get(k, 0) + 1
        out.append(c)
    return out
def world(Tf, Tc, Tt, mod={}):
    raw = {'free': {'a': counts(Tf)}, 'cpmg': {'a': counts(Tc), 'jobB': counts(Tc)}, 't10': {'a': counts(Tt), 'b': counts(mod.get('b', Tt)), 'jobB': counts(mod.get('jobB', Tt))}}
    return raw
W = {'SAME': ([150] * 4, [250] * 4, [250] * 4, {}), 'THEIRS_EVERYWHERE': ([238] * 4, [313] * 4, [345] * 4, {}), 'QUBIT_DEPENDENT': ([150] * 4, [250] * 4, [310, 250, 220, 280], {}),
     'BROKEN_COPIES': ([150] * 4, [250] * 4, [250] * 4, {'b': [150, 250, 250, 250]}), 'DRIFT': ([150] * 4, [250] * 4, [250] * 4, {'jobB': [175] * 4})}
res = {}
for k, (a, b, c, m) in W.items():
    r = analyse(world(a, b, c, m)); res[k] = dict(KG=r['KNOWN_GOOD']['passed'], LAYOUT=r['LAYOUT']['outcome'], dT=[round(x, 1) for x in r['LAYOUT']['dT']], THEIRS=[x['outcome'] for x in r['THEIRS']['per_qubit']], RANK=r['RANK'], DRIFT=[x['outcome'] for x in r['DRIFT']])
fl = [analyse(world([150] * 4, [250] * 4, [250] * 4)) for _ in range(100)]
res['FLOOR_layout_above_100'] = sum(r['LAYOUT']['outcome'].startswith('ABOVE') for r in fl); res['FLOOR_kg_fail_100'] = sum(not r['KNOWN_GOOD']['passed'] for r in fl)
open('synth_results_t10.text', 'w').write(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
