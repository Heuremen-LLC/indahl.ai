"""synth_aqcel.py -- planted worlds through the committed analyze_aqcel.analyze (same code as the real job; B smaller for speed).
World generator: each arm's true output = mixture of its base distribution with the uniform 64-string distribution (or, for a CTRL planted
above its noiseless 0.272, a mixture of the control's noiseless output with the ideal p), mixed to hit the planted fidelity by bisection;
then per-qubit asymmetric readout error (e0 ~ U[0.003, 0.02], e1 ~ U[0.01, 0.04] per physical qubit, redrawn each draw), multinomial
shots exactly as in the job (4 copies x 5000 per arm; 4 x 2500 per calibration circuit; 13-qubit union).
Usage: synth_aqcel.py <ndraws> <B>   -> synth_results_aqcel.text"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import analyze_aqcel as Z

# fixed inputs from the dry run (dry_run_aqcel.text): measured physical qubits per arm and the union; p and the control's noiseless output
INP = json.load(open(os.path.join(HERE, 'synth_inputs_aqcel.json')))
MEAS, UNION, P, DCTRL = INP['meas'], INP['union'], INP['p'], INP['d_ctrl']
PV, DC = Z.pvec(P), Z.pvec(DCTRL)
U = np.full(64, 1 / 64)

WORLDS = {  # planted F per arm (V2 may be a list per copy), planted primary outcome
    'CLEAN':    (dict(Q=.46, V1=.99, V2=.99, CTRL=.25), 'CLEAN'),
    'FILL':     (dict(Q=.70, V1=.98, V2=.99, CTRL=.25), 'FILL'),
    'GAPLOW':   (dict(Q=.46, V1=.94, V2=.95, CTRL=.25), 'GAP'),
    'GAPCTRL':  (dict(Q=.40, V1=.80, V2=.80, CTRL=.90), 'GAP'),
    'BOTH':     (dict(Q=.46, V1=.97, V2=.97, CTRL=.97), 'CANNOT_TELL'),
    'NOADV':    (dict(Q=.99, V1=.99, V2=.99, CTRL=.25), 'GAP'),
    'DRIFT':    (dict(Q=.46, V1=.99, V2=[.99, .95, .99, .95], CTRL=.25), 'CANNOT_TELL'),
    'CALSHIFT': (dict(Q=.46, V1=.99, V2=.99, CTRL=.25), 'CLEAN'),   # artefact: arms' e1 is 0.003 above the calibration's (within-job size)
    'CALSHIFT10': (dict(Q=.46, V1=.99, V2=.99, CTRL=.25), None),    # sensitivity: arms' e1 0.01 above the calibration's: reported, not scored
    'EDGE':     (dict(Q=.46, V1=.985, V2=.985, CTRL=.25), None),   # on the rounding edge: reported, not scored
}


def mix_to(target, base, other):
    lo, hi = 0.0, 1.0
    f = lambda m: Z.fid(PV, (1 - m) * base + m * other)
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f(mid) - target) * (f(lo) - target) <= 0:
            hi = mid
        else:
            lo = mid
    return (1 - lo) * base + lo * other


def true_dist(arm, F):
    if arm == 'CTRL':
        return mix_to(F, DC, PV) if F > Z.fid(PV, DC) else mix_to(F, DC, U)
    return mix_to(F, PV, U)


def readout(d, e0, e1):
    t = d.reshape((2,) * 6)
    for i in range(6):
        M = np.array([[1 - e0[i], e1[i]], [e0[i], 1 - e1[i]]])
        t = np.moveaxis(np.tensordot(M, t, axes=([1], [5 - i])), 0, 5 - i)
    v = t.reshape(-1); return v / v.sum()


def draw(world, rng):
    plant, _ = WORLDS[world]
    e0u = rng.uniform(.003, .02, len(UNION)); e1u = rng.uniform(.01, .04, len(UNION))
    shift = {'CALSHIFT': 0.003, 'CALSHIFT10': 0.01}.get(world, 0.0)
    ent = []
    cache = {}
    for r in range(4):
        for lab in ('CAL0', 'CAL1'):
            flip = lab == 'CAL1'
            bits = np.array([(rng.random(2500) < ((1 - e1u[j]) if flip else e0u[j])).astype(int) for j in range(len(UNION))])
            cnt = {}
            for col in bits.T:
                k = ''.join(str(b) for b in col[::-1]); cnt[k] = cnt.get(k, 0) + 1
            ent.append([lab, r, cnt])
        for a in ('Q', 'V1', 'V2', 'CTRL'):
            F = plant[a][r] if isinstance(plant[a], list) else plant[a]
            key = (a, F)
            if key not in cache:
                cache[key] = true_dist(a, F)
            ix = [UNION.index(q) for q in MEAS[a]]
            obs = readout(cache[key], e0u[ix], np.clip(e1u[ix] + shift, 0, .5))
            c = rng.multinomial(5000, obs)
            ent.append([a, r, {format(k, '06b'): int(v) for k, v in enumerate(c) if v}])
    return ent


def run_world(args):
    w, nd, B = args
    plant, want = WORLDS[w]
    rng = np.random.default_rng([ord(c) for c in w] + [20261024])
    tally = {}; secs = {}; fv2 = []
    for d in range(nd):
        R = Z.analyze(draw(w, rng), MEAS, UNION, P, B=B, seed=d)
        tally[R['primary']] = tally.get(R['primary'], 0) + 1
        s = R['secondary']['V2_vs_099']; secs[s] = secs.get(s, 0) + 1; fv2.append(R['arms']['V2']['F'])
    rate = tally.get(want, 0) / nd if want else float('nan')
    return w, want, tally, secs, rate, float(np.mean(fv2))


if __name__ == '__main__':
    from multiprocessing import Pool
    nd, B = int(sys.argv[1]), int(sys.argv[2])
    with Pool(4) as pool:
        res = pool.map(run_world, [(w, nd, B) for w in WORLDS])
    lines, fc_all = [], []
    for w, want, tally, secs, rate, mf in res:
        if want:
            fc_all.append(1 - rate)
        lines.append(f'{w:10s} planted {want}  primary {tally}  V2-vs-0.99 {secs}  mean F_V2 {mf:.4f}  planted-rate {rate:.3f}  false-call {1 - rate:.3f}')
    lines.append(f'MAX false-call over scored worlds {max(fc_all):.3f}; MEAN {np.mean(fc_all):.3f}  (draws {nd} per world, B {B})')
    print('\n'.join(lines))
    open(os.path.join(HERE, 'synth_results_aqcel.text'), 'w').write('\n'.join(lines) + '\n')
