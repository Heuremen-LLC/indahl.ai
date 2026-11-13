import numpy as np; from ocean import analyse, GROUPS, REPS, SHOTS
rng = np.random.default_rng(11)
def world(params):
    R = {}
    for g in GROUPS:
        b, h = params[g]; R[g] = {'basis': [], 'ghz': []}
        for _ in range(REPS):
            k = rng.binomial(SHOTS, 1 - b); R[g]['basis'].append({'00000': k, '00001': SHOTS - k})
            k = rng.binomial(SHOTS, 1 - h); R[g]['ghz'].append({'00000': k // 2, '11111': k - k // 2, '01010': SHOTS - k})
    return analyse(R)
base = {'DRAIN': (0.12, 0.21), 'ANTI_DRAIN': (0.08, 0.47), 'CONTROL_1': (0.02, 0.89), 'CONTROL_2': (0.08, 0.15)}
L = []
for name, ah, want in (('HEALTH world (anti-healthy like drain)', (0.08, 0.17), 'CONSISTENT'), ('DIRECTION world (anti-healthy like their anti)', (0.08, 0.47), 'ABOVE'),
                       ('REVERSE world (anti-healthy better)', (0.08, 0.10), 'BELOW'), ('NOISE-ONLY world (all groups equal 0.1/0.2)', None, 'CONSISTENT')):
    p = dict(base); p['ANTI_HEALTHY'] = ah if ah else (0.1, 0.2)
    if ah is None: p = {g: (0.1, 0.2) for g in GROUPS}; p['CONTROL_1'] = (0.02, 0.89)
    r = world(p); o = r['DECIDER']['outcome']
    L.append('%-48s decider %.3f [%.3f, %.3f] -> %s (want %s) %s | known-good %s' % (name, r['DECIDER']['value'], *r['DECIDER']['ci95'], o, want, 'PASS' if o == want else 'FAIL', r['KNOWN_GOOD']['passed']))
p = dict(base); p['ANTI_HEALTHY'] = (0.08, 0.17); p['CONTROL_1'] = (0.02, 0.30); r = world(p); L.append('BROKEN-INSTRUMENT world (CONTROL_1 does not fail): known-good %s (want False) %s' % (r['KNOWN_GOOD']['passed'], 'PASS' if not r['KNOWN_GOOD']['passed'] else 'FAIL'))
fp = 0
for _ in range(300):
    p = dict(base); p['ANTI_HEALTHY'] = (0.12, 0.21); fp += world(p)['DECIDER']['outcome'] != 'CONSISTENT'
L.append('FLOOR: equal-delta world, 300 draws: %d resolve (expect ~5%%)' % fp)
open('synth_results_ocean.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
