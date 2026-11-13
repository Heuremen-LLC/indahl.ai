import numpy as np; from lasky import analyse, SHOTS
rng = np.random.default_rng(31)
def cnt(p, n):
    k = rng.binomial(SHOTS, p); return {'0' * n: k // 2, '1' * n: k - k // 2, '0' * (n - 1) + '1': SHOTS - k}
def world(drift_sd, copy_break=0.0):
    jobs = []
    for j in range(4):
        J = {}
        for kind, p0, n in (('GHZ3', 0.88, 3), ('GHZ5', 0.80, 5)):
            p = np.clip(p0 + rng.normal(0, drift_sd), 0, 1); J[kind] = [cnt(p, n), cnt(np.clip(p + copy_break, 0, 1), n)]
        jobs.append(J)
    return analyse(jobs)
L = []
for name, d, want in (('NO DRIFT (gain separable)', 0.0, 'ABOVE'), ('DRIFT sd 0.03 (gain not separable)', 0.03, 'CONSISTENT')):
    r = world(d); L.append('%-36s GHZ3 z %.2f %s | GHZ5 z %.2f %s | KG %s -> %s' % (name, r['GHZ3']['z_of_their_gain'], r['GHZ3']['outcome'], r['GHZ5']['z_of_their_gain'], r['GHZ5']['outcome'], r['KNOWN_GOOD']['passed'],
             'PASS' if r['GHZ3']['outcome'] == want and r['KNOWN_GOOD']['passed'] else 'FAIL'))
r = world(0.0, copy_break=0.08); L.append('BROKEN copies (copy 2 off by 0.08): KG %s (want False) %s' % (r['KNOWN_GOOD']['passed'], 'PASS' if not r['KNOWN_GOOD']['passed'] else 'FAIL'))
fp = sum(not world(0.0)['KNOWN_GOOD']['passed'] for _ in range(200)); L.append('FLOOR: known-good false-fail rate with honest copies, 200 draws: %d (expect ~2 per check x 8 checks ~ 8%%)' % fp)
open('synth_results_lasky.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
