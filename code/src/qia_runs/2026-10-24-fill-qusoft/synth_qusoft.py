"""synth_qusoft.py -- qusoft.py run on PLANTED data before any job. Design shape = the real one: 20 chain edges + 8 HP_8 edges, W (3 x 28) with 3 cz per SWAP on the chain edges and 198 cz on the HP_8 edges
(their Table 12 n2q), P_noiseless (1, 1, 0.931470 their Table 11), stated cz per edge and stated readout per qubit drawn once at the scale of their p2q = 2.0e-3 and readout 1e-2, RB lengths and shots as in qusoft.py.
Truth per job j and target c: P = P_noiseless x prod_edge (1 - f_cz[j] s_e)^W x R[j,c] x d[j,c] x slot, R = readout-string survival; the readout string carries the same slot factor; RB survival = 0.75 x 0.92 p^m + 1/4, err = 3/4 (1-p) = f_cz[j] s_e.
Counts are binomial at 4096 (targets, readout) and 2 x 250 (RB). Worlds: NEITHER (stated record is right, nothing moves), CZ (delivered cz 1.31 x stated, our Part 0 kingston factor), CZ-BIG (3 x),
UNEXPLAINED (extra decoherence d = 0.6, delivered = stated), BOTH (cz 1.31 x and d = 0.6), READOUT (readout failure 2 x stated), DRIFT step (cz +50 % after job index 1, the target follows),
DRIFT linear (cz +15 % per job), JITTER (job-level offsets on d, neither linear nor a step), SLOT (position inside the job costs 0.04 % per circuit), SMALL linear (cz +0.5 % per job), LOW SHOTS (30 shots per target and readout string, 20 per RB cell: the intervals are wider than their scales -> CANNOT_TELL by the rule below).
SCORING (fixed here, before any job): each world is run REPS times (NEITHER_REPS for NEITHER). Per reading: hw = median over runs of the interval (signed, ratio) or null (drift) half-width; U = hw (signed, ratio) or the median null upper bound (drift);
expected = CANNOT_TELL if hw exceeds 1.4 x the reading's resolvability scale (qusoft.py), GREY (not scored) between 0.7 x and 1.4 x of it; else for signed: ABOVE if TRUE >= 1.5 U, BELOW if TRUE <= -1.5 U, CONSISTENT if |TRUE| <= 0.2 U, else GREY (reported, not scored);
drift: ABOVE if TRUE >= 1.5 U, CONSISTENT if TRUE <= 0.2 U. A world PASSES if every scored reading returns its expected outcome in >= 85 % of runs. NEITHER FALSE RATE: ABOVE or BELOW calls per reading over NEITHER_REPS runs
must be <= NEITHER_MAX (about 5 % plus binomial slack): a reading over the line is widened (qusoft.BAND) BEFORE any job."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qusoft as Q
T = Q.parse_theirs(); SC = Q.scales(T)
NE, NC_RB = 28, 60; rng0 = np.random.default_rng(11)
W = np.zeros((3, NE)); W[0, :20] = 3; W[1, :10] = 3; W[2, 20:] = [25, 25, 25, 25, 25, 25, 24, 24]
S_E = rng0.uniform(1.2e-3, 3.0e-3, NE)
RO_FAIL = {c: rng0.uniform(0.004, 0.016, Q.NQ[c]) for c in Q.TARGETS}; RO_STATED = np.array([np.prod(1 - RO_FAIL[c]) for c in Q.TARGETS])
D = dict(edges=[(i, i + 1) for i in range(NE)], W=W, line_idx=np.arange(20), pnl=np.array([1.0, 1.0, Q.pnl_hp(8, 7)]), stated_cz=S_E, ro_stated_surv=RO_STATED)
D['model_stated'] = Q.model_stated_of(D, S_E, RO_STATED)
NC = 6 + NC_RB; POS = {'A': np.array([0, 1, 2, 3, 4, 5]), 'B': NC - 1 - np.array([0, 1, 2, 3, 4, 5])}
JIT = np.array([1.0, 0.97, 1.0, 0.975])
def world(f_cz=lambda j: 1.0, f_ro=1.0, d=lambda j, c: 1.0, slot=0.0):
    fc = np.array([f_cz(j) for j in range(4)]); e = fc[:, None] * S_E[None, :]                              # (4, NE)
    Rtrue = np.array([[1 - f_ro * (1 - RO_STATED[c]) for c in range(3)] for j in range(4)])
    sl = np.array([[1 - slot * POS[Q.ORDER[j][0]][c] for c in range(3)] for j in range(4)]); slr = np.array([[1 - slot * POS[Q.ORDER[j][0]][3 + c] for c in range(3)] for j in range(4)])
    dd = np.array([[d(j, c) for c in range(3)] for j in range(4)])
    Pt = np.array([D['pnl'] * np.exp(W @ np.log1p(-e[j])) * Rtrue[j] * dd[j] * sl[j] for j in range(4)]); Rt = Rtrue * slr
    p = 1 - e / 0.75; Srb = 0.75 * 0.92 * p[:, :, None] ** np.array(Q.M2, float)[None, None, :] + 0.25
    return Pt, Rt, Srb
WORLDS = {
 'NEITHER': (dict(), (4096, 500)),
 'CZ (delivered cz 1.31 x stated)': (dict(f_cz=lambda j: 1.31), (4096, 500)),
 'CZ-BIG (3 x)': (dict(f_cz=lambda j: 3.0), (4096, 500)),
 'UNEXPLAINED (d = 0.6)': (dict(d=lambda j, c: 0.6), (4096, 500)),
 'BOTH (cz 1.31 x, d = 0.6)': (dict(f_cz=lambda j: 1.31, d=lambda j, c: 0.6), (4096, 500)),
 'READOUT (failure 2 x stated)': (dict(f_ro=2.0), (4096, 500)),
 'DRIFT step (cz +50 % after job index 1)': (dict(f_cz=lambda j: 1.0 + 0.5 * (j >= 2)), (4096, 500)),
 'DRIFT linear (cz +15 % per job)': (dict(f_cz=lambda j: 1.0 + 0.15 * j), (4096, 500)),
 'JITTER (job offsets on d)': (dict(d=lambda j, c: JIT[j]), (4096, 500)),
 'SLOT (0.04 % per circuit position)': (dict(slot=4e-4), (4096, 500)),
 'SMALL linear (cz +0.5 % per job)': (dict(f_cz=lambda j: 1.0 + 0.005 * j), (4096, 500)),
 'LOW SHOTS (30 / 20)': (dict(), (30, 20))}
REPS, NEITHER_REPS, NEITHER_MAX, BREP = 40, 200, 15, 400
def draw(Pt, Rt, Srb, nsh, nrb, rng):
    return dict(Kt=rng.binomial(nsh, Pt).astype(float), Kr=rng.binomial(nsh, Rt).astype(float), Krb=rng.binomial(nrb, Srb).astype(float))
def expect(k, true, U, hw, sc):
    tag = k[:2]
    if tag in Q.SIGNED + Q.RATIO:
        scale = sc['gap'][k.split()[-1]] / 4 if tag in Q.SIGNED else sc['ratio'] if tag == 'R3' else sc['ratio_ro']; t = true - (1.0 if tag in Q.RATIO else 0.0)
        if hw > 1.4 * scale: return 'CANNOT_TELL'
        if hw > 0.7 * scale: return 'GREY'
        return 'ABOVE' if t >= 1.5 * U else 'BELOW' if t <= -1.5 * U else 'CONSISTENT' if abs(t) <= 0.2 * U else 'GREY'
    scale = sc['drift_p'] if tag in Q.DRIFT_P else sc['cz']
    if hw >= 1.4 * scale: return 'CANNOT_TELL'
    if hw >= 0.7 * scale: return 'GREY'
    return 'ABOVE' if true >= 1.5 * U else 'CONSISTENT' if true <= 0.2 * U else 'GREY'
if __name__ == '__main__':
    reps_only = [a for a in sys.argv[1:] if not a.startswith('-')]; rng = np.random.default_rng(5); table = []; neither = None
    for name, (kw, (nsh, nrb)) in WORLDS.items():
        if reps_only and not any(name.startswith(a) for a in reps_only): continue
        Pt, Rt, Srb = world(**kw); Q.SHOTS, Q.NRB = nsh, nrb
        true = {k: float(v) for k, v in Q.stats(dict(Kt=Pt * nsh, Kr=Rt * nsh, Krb=Srb * nrb), D).items()}
        reps = NEITHER_REPS if name == 'NEITHER' else REPS; runs = []
        for _ in range(reps): runs.append(Q.analyse(draw(Pt, Rt, Srb, nsh, nrb, rng), D, SC, rng, B=BREP)[1])
        print('==', name, f'({reps} runs; shots {nsh}, RB {nrb})'); print('   TRUE (noise-free): ' + ', '.join(f'{k} {v:+.4f}' for k, v in true.items()))
        ok = True
        for k in true:
            U = float(np.median([r[k][4] if k[:2] in Q.SIGNED + Q.RATIO else r[k][6] for r in runs]))
            hw = float(np.median([r[k][4] for r in runs])); exp = expect(k, true[k], U, hw, SC)
            got = [r[k][3] for r in runs]; rate = float(np.mean([g == exp for g in got])); dist = {o: got.count(o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL') if got.count(o)}
            good = exp == 'GREY' or rate >= 0.85; ok &= good
            print(f'   {k:26s} expect {exp:11s} got {dist} ({rate:.0%}) {"[not scored]" if exp == "GREY" else ""} -> {"ok" if good else "FAIL"}')
        if name == 'NEITHER': neither = {k: sum(r[k][3] in ('ABOVE', 'BELOW') for r in runs) for k in true}; neither_n = reps
        table.append((name, ok))
    print('\nSYNTHETIC TABLE'); [print(f'  {"PASS" if ok else "FAIL"}  {n}') for n, ok in table]
    if neither:
        print(f'\nNEITHER FALSE RATE (ABOVE or BELOW calls in {neither_n} runs; line = {NEITHER_MAX}/{neither_n}):')
        for k, v in neither.items(): print(f'  {k:26s} {v:3d}/{neither_n} = {v / neither_n:.1%}  {"ok" if v <= NEITHER_MAX else "OVER THE LINE"}')
        print('NEITHER FALSE RATE ' + ('WITHIN THE LINE on every reading' if all(v <= NEITHER_MAX for v in neither.values()) else 'OVER THE LINE on: ' + ', '.join(k for k, v in neither.items() if v > NEITHER_MAX)))
    print('ALL WORLDS PASS' if all(ok for _, ok in table) else 'NOT ALL WORLDS PASS')
