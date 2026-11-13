import numpy as np; from shch import analyse, SHOTS
rng = np.random.default_rng(13)
def counts_for(E):  # two bits with correlator E, uniform marginals
    p_same = (1 + E) / 2; k = rng.binomial(SHOTS, p_same); return {'00': k // 2, '11': k - k // 2, '01': (SHOTS - k) // 2, '10': SHOTS - k - (SHOTS - k) // 2}
def job(label, b, S, prodS=1.0):
    e = S / 4; Es = [-e, e, -e, -e]; ep = prodS / 4; Ep = [-ep, ep, -ep, -ep]
    return dict(label=label, backend=b, counts=[counts_for(x) for x in Es] + [counts_for(x) for x in Ep])
L = []
def world(name, sA1, sB1, sB2, sA2, want, prod=1.0, kg=True):
    r = analyse([job('A1', 'fez', sA1, prod), job('B1', 'kingston', sB1, prod), job('B2', 'kingston', sB2, prod), job('A2', 'fez', sA2, prod)])
    got = (r['drift_fez']['outcome'], r['drift_kingston']['outcome'], r['chip_fez_minus_kingston']['outcome'])
    ok = (got == want if kg else True) and r['KNOWN_GOOD']['passed'] == kg   # the broken world scores the known-good only (first draft also scored its chip line, which hit the 5% floor)
    L.append('%-38s drift fez %s, drift kingston %s, chip %s; known-good %s -> %s' % (name, *got, r['KNOWN_GOOD']['passed'], 'PASS' if ok else 'FAIL'))
world('STABLE, same chips', 2.65, 2.65, 2.65, 2.65, ('CONSISTENT', 'CONSISTENT', 'CONSISTENT'))
world('CHIP difference only (0.3)', 2.70, 2.40, 2.40, 2.70, ('CONSISTENT', 'CONSISTENT', 'ABOVE'))
world('DRIFT on fez (-0.3)', 2.70, 2.60, 2.60, 2.40, ('BELOW', 'CONSISTENT', 'CONSISTENT'))
world('BOTH (drift kingston + chip)', 2.70, 2.55, 2.30, 2.70, ('CONSISTENT', 'BELOW', 'ABOVE'))
world('BROKEN instrument (product reads 2.4)', 2.65, 2.65, 2.65, 2.65, ('CONSISTENT', 'CONSISTENT', 'CONSISTENT'), prod=2.4, kg=False)
fp = 0
for _ in range(300):
    r = analyse([job('A1', 'fez', 2.6), job('B1', 'kingston', 2.6), job('B2', 'kingston', 2.6), job('A2', 'fez', 2.6)]); fp += r['drift_fez']['outcome'] != 'CONSISTENT'
L.append('FLOOR: stable world, 300 draws, fez drift resolves %d times (expect ~5%%)' % fp)
open('synth_results_shch.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
