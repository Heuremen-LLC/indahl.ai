import numpy as np; from ktn import woven, aligned, basis_circs, analyse, SHOTS
from qiskit.quantum_info import Statevector
rng = np.random.default_rng(23)
def sample(qc, flip=0.0):
    qc = qc.remove_final_measurements(inplace=False); p = Statevector(qc).probabilities(); k = rng.multinomial(SHOTS, p)
    c = {format(i, '04b'): int(v) for i, v in enumerate(k) if v}
    if flip:  # crude readout noise: flip each bit with probability flip
        out = {}
        for b, n in c.items():
            for _ in range(n):
                bb = ''.join(ch if rng.random() > flip else ('1' if ch == '0' else '0') for ch in b); out[bb] = out.get(bb, 0) + 1
        c = out
    return c
def arm(flip): return {'woven': [sample(q, flip) for q in basis_circs(woven())], 'aligned': [sample(q, flip) for q in basis_circs(aligned())]}
L = []
r = analyse({k: arm(0.0) for k in ('default_a', 'default_b', 'best', 'q50', 'q75')}); L.append('NOISELESS sampling: contrasts %s, KG %s' % ({k: round(v, 3) for k, v in r['SUMMARY']['contrasts'].items()}, r['KNOWN_GOOD']['passed']))
r = analyse({k: arm(0.02) for k in ('default_a', 'default_b', 'best', 'q50', 'q75')}); L.append('READOUT 2%%: contrasts %s, KG %s' % ({k: round(v, 3) for k, v in r['SUMMARY']['contrasts'].items()}, r['KNOWN_GOOD']['passed']))
r = analyse({k: arm(0.1) for k in ('default_a', 'default_b', 'best', 'q50', 'q75')}); L.append('BROKEN readout 10%%: KG %s (want False) %s' % (r['KNOWN_GOOD']['passed'], 'PASS' if not r['KNOWN_GOOD']['passed'] else 'FAIL'))
open('synth_results_ktn.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
