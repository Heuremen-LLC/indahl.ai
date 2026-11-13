"""synth_tara.py -- planted worlds through analyze(); 400 draws each. Worlds: NULL (their E: S 2.732), ABOVE (S 2.83), BELOW (S 2.63),
NEAR (S 2.745, must read CONSISTENT), VAR (cycle-to-cycle E shift sd 0.03: must read CANNOT_TELL), CLASSICAL (S 1.9: R2 BELOW)."""
import sys, numpy as np; sys.path.insert(0, __file__.rsplit('/', 1)[0]); import tara
rng = np.random.default_rng(20261024); base = np.array([[0.6976, 0.6673], [0.6653, -0.7017]])
def world(scale, var=0.0):
    ents = []
    for k, l in tara.plan():
        if k == 'bracket':
            n0 = rng.binomial(tara.SHOTS, 0.99); ents.append((k, l, {l: n0, ('11' if l == '00' else '00'): tara.SHOTS - n0})); continue
        c, i, j = l; E = np.clip(base[i, j] * scale + rng.normal(0, var), -1, 1); ns = rng.binomial(tara.SHOTS, (1 + E) / 2)
        ents.append((k, l, {'00': ns, '01': tara.SHOTS - ns}))
    return tara.analyze(ents)
W = {'NULL': (1.0, 0), 'ABOVE': (2.83 / 2.732, 0), 'BELOW': (2.63 / 2.732, 0), 'NEAR': (2.745 / 2.732, 0), 'VAR': (1.0, 0.03), 'CLASSICAL': (1.9 / 2.732, 0)}
want = {'NULL': 'CONSISTENT', 'ABOVE': 'ABOVE', 'BELOW': 'BELOW', 'NEAR': 'CONSISTENT', 'VAR': 'CANNOT_TELL', 'CLASSICAL': None}
for w, (s, v) in W.items():
    rs = [world(s, v) for _ in range(400)]; c = {}
    for r in rs: c[r['R1']] = c.get(r['R1'], 0) + 1
    r2 = {}
    for r in rs: r2[r['R2']] = r2.get(r['R2'], 0) + 1
    hit = c.get(want[w], 0) / 400 if want[w] else float('nan')
    print(f'{w:9s} R1 {c}  R2 {r2}  planted->{want[w]} rate {hit:.3f}')
