import numpy as np; from n47 import ARMS, analyse, ideal
rng = np.random.default_rng(9)
def draw(N, shots, corr):  # corr: probability shift creating MI between q0,q1 (others uniform)
    p = {}
    for i in range(2 ** N):
        b = format(i, '0%db' % N); q0, q1 = int(b[-1]), int(b[-2]); p[b] = (1 + (corr if q0 == q1 else -corr)) / 2 ** N
    k = list(p); c = rng.multinomial(shots, np.array([p[x] for x in k])); return dict(zip(k, c))
L = []
def world(name, c3, csep, want, kg):
    raw = {}
    for a, N, phi, v, s in ARMS: raw[a] = draw(N, s, c3 if a == 'P3_PI' else (csep if a == 'S3_PI' else 0.0))
    r = analyse(raw); o = r['PREDICTION_4']['outcome']; ok = (want in o) and (r['KNOWN_GOOD']['passed'] == kg)
    L.append('%-44s P3 MI %.4f [%.4f, %.4f] -> %s ; known-good %s %s' % (name, r['P3_PI']['MI'], *r['P3_PI']['ci95'], o, r['KNOWN_GOOD']['passed'], 'PASS' if ok else 'FAIL'))
world('THEIRS world (MI ~0.16 at N=3)', 0.45, 0.0, 'CONSISTENT', True)
world('QM world (ideal 0 at N=3, phi=pi)', 0.0, 0.0, 'BELOW', True)
world('HALF world (MI ~0.04)', 0.23, 0.0, 'BELOW', True)
world('BROKEN-CONTROL world (separate shows MI)', 0.45, 0.2, 'CONSISTENT', False)
L.append('IDEAL (printed circuit): P3_PI %.4f  P2_PI %.4f  P2_PI4 %.4f  H2_PI2 %.4f  S3_PI %.4f' % tuple(ideal(N, phi, v) for _, N, phi, v, _ in ARMS))
open('synth_results_n47.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
