"""synth_ufsm.py -- planted worlds through ufsm.analyze() (both copies, our shot counts), 200 draws each.
Readout model: independent per-qubit flips e[q][v] drawn per world; the measured bracket sees the same flips; the mid-circuit read of q1
uses q1's flips. Extra loss x moves mass from the ideal outcomes to the others uniformly.
  NULL     : (b) deficit = readout only (x_b = 0, small common loss in both)   -> R2 CONSISTENT
  EXTRA    : measure+reset costs 2 pp more than its readout                    -> R2 ABOVE
  OVERCORR : mid read cleaner than terminal (mid flips 0.4x)                   -> R2 BELOW
  THEIRS   : raw extra deficit = their 3.43 pp                                  -> R1 CONSISTENT
  VAR      : per-circuit loss jitter sd 0.6 pp                                  -> CANNOT_TELL
(second version: spread gate = chi-square p < 0.005; THEIRS world planted at raw extra deficit 3.428 pp -- both fixed before any job)"""
import sys, os, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ufsm
rng = np.random.default_rng(424242)
def dist_a(e, loss):
    p = {}
    for (q0, q1) in ((1, 0), (0, 1)):
        for r0 in (0, 1):
            for r1 in (0, 1):
                pr = (e[0][str(q0)] if r0 != q0 else 1 - e[0][str(q0)]) * (e[1][str(q1)] if r1 != q1 else 1 - e[1][str(q1)])
                k = f'{r1}{r0}'; p[k] = p.get(k, 0) + 0.5 * pr
    return mix(p, ufsm.IDEAL['a'], loss)
def dist_b(e, em, loss):
    p = {}
    for (m, f0, f1) in ((1, 0, 0), (0, 0, 1)):
        for rm in (0, 1):
            for r0 in (0, 1):
                for r1 in (0, 1):
                    pr = (em[str(m)] if rm != m else 1 - em[str(m)]) * (e[0][str(f0)] if r0 != f0 else 1 - e[0][str(f0)]) * (e[1][str(f1)] if r1 != f1 else 1 - e[1][str(f1)])
                    k = f'{r1}{r0}{rm}'; p[k] = p.get(k, 0) + 0.5 * pr
    return mix(p, ufsm.IDEAL['b'], loss)
def mix(p, ideal, loss):
    keys = sorted(p); others = [k for k in keys if k not in ideal]; q = dict(p)
    for k in ideal: q[k] = p[k] * (1 - loss)
    moved = sum(p[k] for k in ideal) * loss
    for k in others: q[k] = p[k] + moved / len(others)
    return q
def draw(p, n):
    ks = sorted(p); v = rng.multinomial(n, np.array([p[k] for k in ks]) / sum(p.values())); return dict(zip(ks, v))
def world(xb, la=0.004, mid=1.0, jitter=0.0, target_D=None):
    e = {0: {'0': rng.uniform(.003, .01), '1': rng.uniform(.008, .02)}, 1: {'0': rng.uniform(.003, .01), '1': rng.uniform(.008, .02)}}
    em = {v: e[1][v] * mid for v in '01'}; ents = []
    if target_D is not None:   # raw extra deficit planted at target_D: xb = target - readout-only difference
        xb = max(0.0, target_D - (ufsm.ro_deficit({0: e[0], 1: em}, 'b') - ufsm.ro_deficit(e, 'a')))
    for copy in (1, 2):
        for k, l in ufsm.plan(copy):
            if k == 'br':
                q0, q1 = int(l[1]), int(l[0]); p = {}
                for r0 in (0, 1):
                    for r1 in (0, 1):
                        p[f'{r1}{r0}'] = (e[0][str(q0)] if r0 != q0 else 1 - e[0][str(q0)]) * (e[1][str(q1)] if r1 != q1 else 1 - e[1][str(q1)])
                ents.append((k, l, draw(p, ufsm.SHOTS)))
            elif k == 'a': ents.append((k, l, draw(dist_a(e, max(0, la + rng.normal(0, jitter))), ufsm.SHOTS)))
            else: ents.append((k, l, draw(dist_b(e, em, max(0, la + xb + rng.normal(0, jitter))), ufsm.SHOTS)))
    return ufsm.analyze(ents, nboot=120, seed=int(rng.integers(1e9)))
W = {'NULL': dict(xb=0.0), 'EXTRA': dict(xb=0.02), 'OVERCORR': dict(xb=0.0, mid=0.4), 'THEIRS': dict(xb=0.0, target_D=0.03428), 'VAR': dict(xb=0.0, jitter=0.006)}
want = {'NULL': ('R2', 'CONSISTENT'), 'EXTRA': ('R2', 'ABOVE'), 'OVERCORR': ('R2', 'BELOW'), 'THEIRS': ('R1', 'CONSISTENT'), 'VAR': ('R2', 'CANNOT_TELL')}
for w, kw in W.items():
    rs = [world(**kw) for _ in range(200)]; c1 = {}; c2 = {}
    for r in rs: c1[r['R1']] = c1.get(r['R1'], 0) + 1; c2[r['R2']] = c2.get(r['R2'], 0) + 1
    key, out = want[w]; hit = (c1 if key == 'R1' else c2).get(out, 0) / 200
    print(f'{w:9s} R1 {c1}  R2 {c2}  planted {key}->{out} rate {hit:.3f}', flush=True)
