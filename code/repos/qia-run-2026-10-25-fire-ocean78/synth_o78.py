import numpy as np; from o78 import QUBITS, S_LEVELS, SHOTS, analyse, model_err
rng = np.random.default_rng(21); n = len(QUBITS)
rec = {q: (rng.uniform(120e-6, 300e-6), rng.uniform(80e-6, 200e-6), rng.uniform(0.002, 0.012)) for q in QUBITS}
def counts(p):  # independent qubits with P(1) = p[i]; a few thousand shots synthesized as bitstrings
    bits = (rng.random((SHOTS, n)) < p[None, :]).astype(int); c = {}
    for row in bits: k = ''.join(map(str, row[::-1])); c[k] = c.get(k, 0) + 1
    return c
def world(collapsed_slope, real_extra, kg=0.5):
    raw = {'COLLAPSED': {}, 'REAL': {}, 'KG': {}}
    base = np.array([rec[q][2] for q in QUBITS])
    for S in S_LEVELS:
        raw['COLLAPSED'][str(S)] = counts(base + collapsed_slope * S)
        raw['REAL'][str(S)] = counts(np.array([model_err(S, *rec[q]) for q in QUBITS]) + real_extra * S)
    raw['KG']['KG'] = counts(np.full(n, kg)); return analyse(raw, rec)
L = []
for name, cs, re_, kg, want in (('STANDARD physics (no g1)', 0.0, 0.0, 0.5, ('CONSISTENT', 'CONSISTENT', True)), ('G1 = +0.003 in the real idle', 0.0, 0.003, 0.5, ('CONSISTENT', 'ABOVE', True)),
                                ('COLLAPSED shows their 0.001 (impossible if identical)', 0.001, 0.0, 0.5, ('ABOVE', 'CONSISTENT', True)), ('BROKEN decoder (KG reads 0.3)', 0.0, 0.0, 0.3, (None, None, False))):
    r = world(cs, re_, kg); got = (r['COLLAPSED']['outcome_vs_zero'], r['REAL']['residual_over_record']['outcome'], r['KNOWN_GOOD']['passed'])
    ok = (got == want) if want[0] else (got[2] == want[2])
    L.append('%-52s collapsed slope %+.5f %s | real slope %+.4f model %+.4f residual %s | KG %.3f %s -> %s' % (name, r['COLLAPSED']['slope'], got[0], r['REAL']['slope'], r['REAL']['record_model_slope'], got[1], r['KNOWN_GOOD']['mean_P1'], got[2], 'PASS' if ok else 'FAIL'))
fp = sum(world(0.0, 0.0)['REAL']['residual_over_record']['outcome'] != 'CONSISTENT' for _ in range(60)); L.append('FLOOR: standard world, 60 draws, residual resolves %d (first STANDARD draw above resolved at ~2.3 sigma: a floor hit, kept, not reseeded)' % fp)
open('synth_results_o78.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
