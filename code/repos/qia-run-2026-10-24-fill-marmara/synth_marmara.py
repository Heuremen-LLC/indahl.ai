"""synth_marmara.py DIR -- planted worlds through marmara.analyze() (4 jobs x 1024, our exact plan), 40 draws per world, Pool(4).
Truth = per-message pre-readout distributions: their own MITIGATED n=6 distributions (population shortfall 0.70) mixed with the uniform
distribution over 64 outcomes at weight w chosen so the population shortfall hits the target. Readout = per-qubit flips from THEIR stored
record, applied exactly; the bracket sees the same flips.
Worlds: ADV (0.70, both arms) -> mitigated reading BELOW 1; EDGE (1.00) -> CONSISTENT; LOST (1.30) -> ABOVE; VAR (arm OFF jobs at 0.85 and
1.15) -> CANNOT_TELL; DDHELP (ON 0.70, OFF 1.00) -> R4 BELOW; DDSAME (both 0.85) -> R4 CONSISTENT."""
import sys, os, json, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import marmara as M
D = sys.argv[1]; MIT = json.load(open(f'{D}/fez_counts_mitigated_n_6.json')); REC = json.load(open(f'{D}/fez_readout_data_n_6.json'))
E0 = np.array([REC[str(q)]['prob_meas1_prep0'] for q in range(6)]); E1 = np.array([REC[str(q)]['prob_meas0_prep1'] for q in range(6)])
def base(m):
    c = MIT[m]; p = np.zeros(64)
    for s, v in c.items(): p[int(s, 2)] += v
    return p / p.sum()
BASE = {m: base(m) for m in M.MSGS}
def mixed(w): return {m: (1 - w) * BASE[m] + w / 64 for m in M.MSGS}
def shortfall(dists): return 6 - M.mi({m: {format(i, '06b'): float(v) for i, v in enumerate(p) if v > 0} for m, p in dists.items()})
def w_for(target):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if shortfall(mixed(mid)) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def flip(p):
    t = p.reshape([2] * 6)
    for q in range(6):
        A = np.array([[1 - E0[q], E1[q]], [E0[q], 1 - E1[q]]]); ax = 5 - q
        t = np.moveaxis(np.tensordot(A, np.moveaxis(t, ax, 0), axes=1), 0, ax)
    t = np.clip(t.reshape(-1), 0, None); return t / t.sum()
def job(dists, jobname, rng):
    ents = []
    for k, l in M.plan(jobname):
        if k == 'br':
            p = np.zeros(64); p[0 if l == '0' else 63] = 1.0; p = flip(p)
        else: p = flip(dists[l])
        v = rng.multinomial(M.SHOTS, p); ents.append((k, l, {format(i, '06b'): int(x) for i, x in enumerate(v) if x}))
    return ents
TARGETS = {'ADV': dict(off=(0.70, 0.70), on=(0.70, 0.70)), 'EDGE': dict(off=(1.0, 1.0), on=(1.0, 1.0)), 'LOST': dict(off=(1.30, 1.30), on=(1.30, 1.30)),
           'VAR': dict(off=(0.85, 1.15), on=(1.0, 1.0)), 'DDHELP': dict(off=(1.0, 1.0), on=(0.70, 0.70)), 'DDSAME': dict(off=(0.85, 0.85), on=(0.85, 0.85))}
WCACHE = {v: w_for(v) for v in sorted({x for T in TARGETS.values() for a in T.values() for x in a})}   # at import: spawned workers rebuild it
def one(args):
    name, i = args; rng = np.random.default_rng(1000 * i + hash(name) % 997); T = TARGETS[name]
    jobs = {'J1': job(mixed(WCACHE[T['off'][0]]), 'J1', rng), 'J4': job(mixed(WCACHE[T['off'][1]]), 'J4', rng),
            'J2': job(mixed(WCACHE[T['on'][0]]), 'J2', rng), 'J3': job(mixed(WCACHE[T['on'][1]]), 'J3', rng)}

    off = M.analyze_arm(jobs['J1'], jobs['J4'], nboot=60, seed=i); on = M.analyze_arm(jobs['J2'], jobs['J3'], nboot=60, seed=i + 1)
    d = on['mit'] - off['mit']; sd = np.hypot(on['smit'], off['smit']); r4 = M.four(d, sd, 0.0, off['gate'] or on['gate'])
    return name, off['R_mit'], on['R_mit'], r4
if __name__ == '__main__':
    print('mixing weights:', {k: round(v, 4) for k, v in WCACHE.items()}, '| check shortfall at ADV w:', round(shortfall(mixed(WCACHE[0.7])), 3), flush=True)
    tasks = [(n, i) for n in TARGETS for i in range(40)]
    with Pool(4, initializer=None) as P: res = P.map(one, tasks)
    want = {'ADV': ('off', 'BELOW'), 'EDGE': ('off', 'CONSISTENT'), 'LOST': ('off', 'ABOVE'), 'VAR': ('off', 'CANNOT_TELL'), 'DDHELP': ('R4', 'BELOW'), 'DDSAME': ('R4', 'CONSISTENT')}
    for n in TARGETS:
        rs = [r for r in res if r[0] == n]; c_off = {}; c_on = {}; c4 = {}
        for _, a, b, d in rs: c_off[a] = c_off.get(a, 0) + 1; c_on[b] = c_on.get(b, 0) + 1; c4[d] = c4.get(d, 0) + 1
        key, out = want[n]; src = {'off': c_off, 'R4': c4}[key]; print(f'{n:7s} OFF {c_off}  ON {c_on}  R4 {c4}  planted {key}->{out} rate {src.get(out,0)/len(rs):.3f}', flush=True)
