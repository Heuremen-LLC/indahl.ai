"""fake-file check of ball.py --real: planted instrument (product model, eta_dn 0.012, eta_up 0.001) and a -2.0 deg/readout neighbour kick."""
import sys, os, json, shutil, numpy as np
D = sys.argv[1]; F = sys.argv[2]; sys.path.insert(0, D)
import fire_ball as fb, ball
sel = json.load(open(f'{D}/selection_ball.json')); T, NB, LO = sel['targets'], sel['neighbours'], sel['Blo']
_, meta = fb.build_all(156, T, NB, LO, np.random.default_rng(fb.SEED))
rng = np.random.default_rng(5)
M = ball.instrument(0.01, 0.02, 0.012, 0.001)
def strings(nq, shots):
    out = np.zeros((3, shots, nq), bool)
    for k in range(nq):
        s = rng.integers(2, size=shots)
        for l in range(3):
            pre = s.copy(); po1 = np.where(pre == 0, 0.01, 0.98); o = rng.random(shots) < po1; out[l, :, k] = o
            up = (pre == 0) & (rng.random(shots) < 0.001); dn = (pre == 1) & (rng.random(shots) < 0.012); s = np.where(up, 1, np.where(dn, 0, pre))
    return out
coh = rng.uniform(0.8, 0.95, len(NB)); phi0 = rng.uniform(-np.pi, np.pi, len(NB))
for J in ('J1', 'J2'):
    z = {}
    for i, m in enumerate(meta):
        if m['arm'] in ('A', 'Bhi', 'Blo'):
            nq = len(T) if m['arm'] == 'A' else len(T) + len(NB) if m['arm'] == 'Bhi' else 1
            b = strings(nq, m['shots']); z[f'm1_{i}'], z[f'm2_{i}'], z[f'm3_{i}'] = b[0], b[1], b[2]
        else:
            ph = phi0 + (np.radians(-2.0 * 3) if m['arm'] == 'CM' else 0.0)
            f = np.cos if m['basis'] == 'X' else np.sin
            p0 = (1 + coh * f(ph)) / 2
            z[f'fin_{i}'] = rng.random((m['shots'], len(NB))) > p0[None, :]     # True = read 1
    np.savez_compressed(f'{F}/raw_ball_{J}.npz', **z)
json.dump(dict(chip='fake', targets=T, neighbours=NB, Blo=LO, nb_readout_ok=[True] * len(NB), meta=meta,
               jobs=[dict(job_id='FAKE1'), dict(job_id='FAKE2')]), open(f'{F}/job_ball.json', 'w'))
shutil.copy(f'{D}/ball.py', f'{F}/ball.py')
