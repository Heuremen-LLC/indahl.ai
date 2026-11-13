"""synth_ghz.py -- planted worlds: IDEAL-NOISY (P 0.6, C 0.5 everywhere), LAYOUT (P 0.70/0.62/0.55/0.48), DRIFT (job B -0.10), BROKEN COPIES (best_b -0.06),
COHERENT-ZERO (C 0: classical mix, P 0.6), BOTH (layout + drift). Floors over 200 null worlds. Statevector check of the parity circuit: parity = cos(N phi)."""
import json, numpy as np
from ghz import ghz, N, SHOTS, PHIS
from ghz_fill import analyse
from qiskit.quantum_info import Statevector
for f in PHIS[:3]:
    qc = ghz(phi=f).remove_final_measurements(inplace=False); pr = Statevector(qc).probabilities_dict()
    par = sum(v * (1 - 2 * (b.count('1') % 2)) for b, v in pr.items()); assert abs(par - np.cos(N * f)) < 1e-9, (f, par)
rng = np.random.default_rng(12)
POP = ['best_a', 'best_b', 'q25', 'q50', 'q75', 'unpinned', 'best_jobB', 'unpinned_jobB']
def world(Pm, C):
    raw = {}
    for a in POP:
        p = Pm.get(a, Pm['_']); k = rng.binomial(SHOTS, p); k1 = rng.binomial(k, 0.5); raw[a] = {'0' * N: int(k1), '1' * N: int(k - k1), '0' * (N - 1) + '1': int(SHOTS - k)}
    for i, f in enumerate(PHIS):
        m = C * np.cos(N * f); ke = rng.binomial(SHOTS, (1 + m) / 2); raw['par%d' % i] = {'0' * N: int(ke), '0' * (N - 1) + '1': int(SHOTS - ke)}
    return raw
W = {'NOISY_FLAT': ({'_': 0.6}, 0.5), 'LAYOUT': ({'_': 0.70, 'q25': 0.62, 'q50': 0.55, 'q75': 0.48}, 0.5), 'DRIFT': ({'_': 0.6, 'best_jobB': 0.5, 'unpinned_jobB': 0.5}, 0.5),
     'BROKEN_COPIES': ({'_': 0.6, 'best_b': 0.54}, 0.5), 'COHERENCE_ZERO': ({'_': 0.6}, 0.0), 'BOTH': ({'_': 0.70, 'q25': 0.62, 'q50': 0.55, 'q75': 0.48, 'best_jobB': 0.60}, 0.5)}
res = {}
for k, (Pm, C) in W.items():
    r = analyse(world(Pm, C)); res[k] = dict(KG=r['KNOWN_GOOD']['passed'], LAYOUT=r['LAYOUT']['outcome'], DRIFT_best=r['DRIFT']['best']['outcome'], DRIFT_unpinned=r['DRIFT']['unpinned']['outcome'],
                                          F=round(r['FIDELITY']['F'], 4), C=round(r['FIDELITY']['C'], 4), C_se=round(r['FIDELITY']['C_se'], 4))
res['FLOOR_layout_above_200'] = sum(analyse(world({'_': 0.6}, 0.5))['LAYOUT']['outcome'].startswith('ABOVE') for _ in range(200))
res['FLOOR_kg_fail_200'] = sum(not analyse(world({'_': 0.6}, 0.5))['KNOWN_GOOD']['passed'] for _ in range(200))
open('synth_results_ghz.text', 'w').write(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
