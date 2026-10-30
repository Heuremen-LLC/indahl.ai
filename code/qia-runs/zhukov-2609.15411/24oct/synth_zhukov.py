"""synth_zhukov.py -- zhukov.py run on PLANTED data before any job. Truths are HIS own measured distributions (raw/003 control block, raw/005 chain-C circuits, per circuit and lane),
with qubit 16 (lane 0) and our ten extra arms modelled from the world parameters. Four jobs in ABBA order, 1024 shots unless stated; his comparator data (chain-C counts, control counts)
are redrawn from the same truth in every run (a noisy sample, as in life).
WORLDS (every world plants a verdict for every scored reading): NEITHER (q16 at stated, nothing moves) | ANOMALY read-out flavour (q16 as he measured, per-read flips) | ANOMALY state
flavour (q16 as he measured, state already wrong before the read) | DRIFT (job-level mixing toward uniform, lanes 1-6) | SLOT apparatus artefact (circuit-position noise, no drift) |
PHASE (+25 deg on the Strang r=8 chain-C phase) | BELOW (stated record far above delivered) | BOTH (state anomaly + drift + phase) | LOW SHOTS (3 shots per circuit, anomaly on) | SMALL drift
(below detection, reported not scored).
SCORING (fixed here before any job): each world is run REPS times with fresh counts; every scored reading must return its expected outcome in >= 90 % of runs (GREY = reported, not scored: SMALL drift for B; C_MIN in the drift worlds, where the
between-job t-term on 3 dof is the width and a mean shift smaller than it is rightly not called); in NEITHER the false rate
(runs not returning the expected outcome) must be <= 5 % per scored reading, i.e. >= 95 % as expected."""
import sys, os, json, zlib, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zhukov as Z
NC, S6 = Z.NC, 6
Q3, Q2 = dict(p10=0.0005, p01=0.0078), dict(p10=0.0122, p01=0.0132)
EPS_FLIP, T1, DELAY_US = 0.01, 367.0, 100.03
DEF = dict(p10=0.0093, p01=0.0122, flavor='readout', stated16=(0.0090, 0.0095, 0.0120, 0.0125), lin=0.0, slot=0.0, phase=0.0, shots=1024)
WORLDS = {
 'NEITHER': (dict(), {}),
 'ANOMALY read-out flavour': (dict(p10=0.73, p01=0.13), dict(A=1)),
 'ANOMALY state flavour': (dict(p10=0.73, p01=0.13, flavor='state'), dict(A=1, S='BELOW', D='BELOW')),
 'DRIFT (job-level mixing, +0.02 per job)': (dict(lin=0.02), dict(BW='ABOVE', CMIN='GREY')),
 'SLOT apparatus artefact (+0.001 noise per circuit position)': (dict(slot=0.001), dict(BS='ABOVE', CMIN='BELOW')),
 'PHASE (+25 deg on Strang r=8)': (dict(phase=25.0), dict(CS='ABOVE')),
 'BELOW (stated record far above delivered)': (dict(stated16=(0.05, 0.06, 0.05, 0.06)), dict(A='BELOW')),
 'BOTH (state anomaly + drift + phase)': (dict(p10=0.73, p01=0.13, flavor='state', lin=0.02, phase=25.0), dict(A=1, S='BELOW', D='BELOW', BW='ABOVE', CS='ABOVE', CMIN='GREY')),
 'LOW SHOTS (3 per circuit, anomaly on)': (dict(p10=0.73, p01=0.13, shots=3), 'CT'),
 'SMALL drift (+0.001 per job; reported, not scored)': (dict(lin=0.001), 'GREY')}
KEY = dict(BW='B_WITHIN median T (A1|A2, B1|B2)', BS='B_SLOT median T (A1+A2 | B1+B2)', CS='C_STRANG8 signed phase error at Jt=4/3 (deg)',
           CMIN='C_MIN mean over chains of min correct joint-outcome prob (ours - his, raw/003 controls)', D='D0 DLY prep0 100us minus none')
def expect_world(spec):
    names = Z.SCORED
    if spec == 'CT': return {n: 'CANNOT_TELL' for n in names}
    if spec == 'GREY': return {n: ('GREY' if n.startswith('B_') else 'CONSISTENT') for n in names}
    e = {n: 'CONSISTENT' for n in names}
    for k, v in spec.items():
        if k == 'A':
            for n in names:
                if n.startswith('A q16'): e[n] = 'ABOVE' if v == 1 else v
        elif k == 'S': e['S0 MM prep0'] = e['S1 MM prep1'] = v
        else: e[KEY[k]] = v
    return e

# ---------------------------------------------------------------- truth
def mix(p, e): return (1 - e) * p + e / 8
def reweight(p, new_mean):
    mu = float(p @ Z.EIG1); a = (new_mean - mu) / (1 - mu * new_mean); q = p * (1 + a * Z.EIG1); return q / q.sum()
def base_p(i, lane):
    c = Z.SET[i]; r = Z.rows(c['src'])[c['row']]; k = np.array(r['lanes'][str(lane)]['counts'], float); return k / k.sum()
def bit_prob(prep, p10, p01): return p10 if prep == 0 else 1 - p01
def lane0_p(i, w):
    c = Z.SET[i]; pat = c['spec']['pattern'] if c['kind'] == 'spam' else 0; b = [(pat >> 2) & 1, (pat >> 1) & 1, pat & 1]
    q = [bit_prob(b[0], w['p10'], w['p01']), bit_prob(b[1], Q3['p10'], Q3['p01']), bit_prob(b[2], Q2['p10'], Q2['p01'])]; p = np.zeros(8)
    for code in range(8):
        pr = 1.0
        for j, bj in enumerate([(code >> 2) & 1, (code >> 1) & 1, code & 1]): pr *= q[j] if bj else 1 - q[j]
        p[code] = pr
    return p
def truth(w):
    """P[t, i, k, 8] for t in ORDER positions (A1 B1 B2 A2); extras handled separately."""
    P = np.zeros((4, NC, S6, 8)); pm = {}
    for t, lab in enumerate(Z.ORDER):
        pos = Z.slot_pos(lab)
        for i, c in enumerate(Z.SET):
            if c['src'] == 'X': continue
            for k, lane in enumerate(Z.LANES):
                if lane not in c['lanes']: continue
                if lane == 0: P[t, i, k] = lane0_p(i, w); continue
                key = (i, lane)
                if key not in pm: pm[key] = base_p(i, lane)
                P[t, i, k] = mix(pm[key], w['lin'] * t + w['slot'] * pos[i])
    if w['phase']:                      # rotate C1 of the Strang r=8 chain-C by +phase (signed error grows), reweight each circuit's x1 marginal
        m = {b: sum(base_p(i, 3) for i in Z.CHAINC[('strang8', b)]) / 2 for b in ('XXX', 'YYY')}
        x, y = m['XXX'] @ Z.EIG1, m['YYY'] @ Z.EIG1; c1 = (x + 1j * y) * np.exp(1j * np.radians(w['phase']))
        for b, nm in (('XXX', c1.real), ('YYY', c1.imag)):
            for i in Z.CHAINC[('strang8', b)]:
                for t in range(4):
                    k = Z.LANES.index(3); lin_slot = w['lin'] * t + w['slot'] * Z.slot_pos(Z.ORDER[t])[i]
                    P[t, i, k] = mix(reweight(base_p(i, 3), nm), lin_slot)
    return P
def draw(P, shots, rng):
    cum = np.cumsum(P, axis=-1)[..., :7]; U = rng.random(P.shape[:-1] + (shots,))
    return (U[..., None] >= cum[..., None, :]).sum(-1).astype(np.uint8)       # (4, NC, 6, shots)
def gen(w, rng):
    P = truth(w); shots = w['shots']; cod = draw(P, shots, rng)                # (4, NC, 6, S)
    codes = np.full((4, NC, shots, 6), 255, np.uint8)
    for t in range(4):
        for i, c in enumerate(Z.SET):
            if c['src'] == 'X': continue
            for k, lane in enumerate(Z.LANES):
                if lane in c['lanes']: codes[t, i, :, k] = cod[t, i, k]
    p10, p01 = w['p10'], w['p01']; P1 = {0: p10, 1: 1 - p01}
    for t in range(4):
        for i, c in enumerate(Z.SET):
            if c['src'] != 'X': continue
            nm = c['spec']['name']; b = 0 if nm == 'MMC' else int(nm[-1]); pr = Q3['p10'] if nm == 'MMC' else P1[b]
            if nm.startswith('MM'):
                if w['flavor'] == 'readout' or nm == 'MMC': r1 = rng.random(shots) < pr; r2 = rng.random(shots) < pr
                else:
                    s = rng.random(shots) < pr; r1 = s ^ (rng.random(shots) < EPS_FLIP); r2 = s ^ (rng.random(shots) < EPS_FLIP)
                codes[t, i, :, 0] = r1.astype(np.uint8) | (r2.astype(np.uint8) << 1)
            else:
                pd = pr if (w['flavor'] == 'readout' or b == 1) else pr * np.exp(-DELAY_US / T1) + 0.003
                codes[t, i, :, 0] = (rng.random(shots) < pd).astype(np.uint8)
    # his comparator data, redrawn from the unmodified truth
    his_p = {}
    for method in ('strang8', 'exact'):
        his_p[method] = {b: sum(np.bincount(draw(base_p(i, 3)[None, :], SH, rng).ravel(), minlength=8)[:8] for i in Z.CHAINC[(method, b)]).astype(float) for b in ('XXX', 'YYY')}
    his_k = {}
    for lane in Z.SCI:
        k = []
        for i in Z.CTRL:
            c = Z.SET[i]; p = base_p(i, lane); idp = Z.ref_probs(i, lane, 'ideal_probabilities'); k.append(float((draw(p[None, :], SH, rng) == idp.argmax()).sum()))
        his_k[lane] = np.array(k)
    return codes, his_p, his_k
SH = 1024
def stated_ranges(w):
    s16 = w['stated16']; return {16: s16, 3: (Q3['p10'] * 0.95, Q3['p10'] * 1.05, Q3['p01'] * 0.95, Q3['p01'] * 1.05), 2: (Q2['p10'] * 0.95, Q2['p10'] * 1.05, Q2['p01'] * 0.95, Q2['p01'] * 1.05)}

# ---------------------------------------------------------------- runs
def one_run(args):
    name, wd, seed = args; w = dict(DEF, **wd); rng = np.random.default_rng(seed); codes, hp, hk = gen(w, rng)
    res = Z.analyse(codes, stated_ranges(w), hp, hk, rng, B=300); return {k: res[k]['outcome'] for k in res}, {k: res[k]['value'] for k in res}
def run_world(name, reps, pool):
    wd, spec = WORLDS[name]; e = expect_world(spec); args = [(name, wd, 1000 * (zlib.crc32(name.encode()) % 997) + r) for r in range(reps)]
    return pool.map(one_run, args), e
if __name__ == '__main__':
    reps_n = int(sys.argv[1]) if len(sys.argv) > 1 else 100; reps = int(sys.argv[2]) if len(sys.argv) > 2 else 40; only = sys.argv[3] if len(sys.argv) > 3 else None
    table = []
    with Pool(16) as pool:
        for name in WORLDS:
            if only and only not in name: continue
            R = reps_n if name == 'NEITHER' else reps; out, e = run_world(name, R, pool); ok = True; print('==', name, f'({R} runs)')
            for k in Z.SCORED:
                got = [o[0][k] for o in out]; dist = {x: got.count(x) for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if got.count(x)}
                if e[k] == 'GREY': print(f'   {k:92s} expect GREY (not scored) got {dist}'); continue
                rate = float(np.mean([g == e[k] for g in got])); need = 0.95 if name == 'NEITHER' else 0.90; good = rate >= need; ok &= good
                print(f'   {k:92s} expect {e[k]:11s} got {dist} ({rate:.0%} as expected{"; false rate " + format(1 - rate, ".0%") if name == "NEITHER" else ""}) -> {"ok" if good else "FAIL"}')
            table.append((name, ok, 'GREY' in e.values()))
    print('\nSYNTHETIC TABLE (' + str(reps_n) + ' runs NEITHER, ' + str(reps) + ' per other world)')
    for n, ok, g in table: print(f'  {"PASS" if ok else "FAIL"}  {n}' + ('  (some readings reported, not scored: GREY)' if g else ''))
    print('ALL WORLDS PASS' if all(ok for _, ok, _ in table) else 'NOT ALL WORLDS PASS')
