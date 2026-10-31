"""pooters.py -- Page-Wootters history state on ibm_kingston, with and without a LOOK at the clock (24 Oct 2026; plan PLAN_POOTERS.md.text).
Qubits (index): 0 = c0 (clock bit 0), 1 = c1 (clock bit 1), 2 = s (system). t = c0 + 2 c1. theta = pi/4.
Ideal |Psi> = 1/2 sum_t |t> (x) RY(t theta)|0>.  Arm D: the 39-qubit pack idles 4 x 545 dt.  Arm M: the pack is read out 4 times (default measure).
Readings (all with four outcomes, shot bootstrap, per copy and pooled; FINAL = pooled if the copies agree, else CANNOT_TELL):
  R1 inside view, arm D: alpha(t) = atan2(<X_s>|t, <Z_s>|t) minus the same angle for the ideal state through the record's readout error (the none).
  R2 the look: per-qubit Z-rotation phi_q fitted as E_M = (M_c0 x M_c1 x M_s) E_D over all 63 Pauli expectations (phi, lambda per qubit);
     reported per readout (phi/4), deg. Sign convention as the control run: phase = atan2(<Y>,<X>), kick = phase_M - phase_D.
  R3 history fidelity change dF = F(M) - F(D), F = (1/8) sum_P <P> <P>_ideal (linear, no MLE).
  R4 tick uniformity under the look: delta = phi_c1 - 2 phi_c0 (total, deg). 0 = the look adds a phase linear in t (an evenly ticking clock).
Usage: pooters.py --synth   (planted worlds -> synth_results_pooters.text)
       pooters.py --real    (raw_pooters_J1.json, raw_pooters_J2.json, props_pooters_before_J1.json -> stdout)"""
import json, sys, os, itertools
import numpy as np
from scipy.optimize import least_squares
HERE = os.path.dirname(os.path.abspath(__file__))
THETA = np.pi / 4; NREAD = 4; LAB = 'IXYZ'
BAND = [0.5, 99.5]   # widened from [2.5, 97.5] before any job: the 95 % band gave 7.9 % false calls in the synthetic (synth_results_pooters_95band_FIRST.text)
SETTINGS = [''.join(s) for s in itertools.product('XYZ', repeat=3)]       # letter i = basis of qubit i (c0, c1, s)
PAULI = [np.eye(2), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1., -1.])]
H_ = np.array([[1, 1], [1, -1]]) / np.sqrt(2); SDG = np.diag([1, -1j])
ROT = {'X': H_, 'Y': H_ @ SDG, 'Z': np.eye(2)}

def ry(a): return np.array([np.cos(a / 2), np.sin(a / 2)])
def ideal_psi(theta=THETA):
    psi = np.zeros((2, 2, 2), complex)
    for x0, x1 in itertools.product((0, 1), repeat=2): psi[x0, x1, :] = 0.5 * ry((x0 + 2 * x1) * theta)
    return psi.reshape(8)
def kron3(a, b, c): return np.kron(np.kron(a, b), c)
def evec_of_rho(rho):
    return np.array([np.real(np.trace(rho @ kron3(PAULI[a], PAULI[b], PAULI[c]))) for a, b, c in itertools.product(range(4), repeat=3)])
E_IDEAL = evec_of_rho(np.outer(ideal_psi(), ideal_psi().conj()))

# ---------- counts -> probabilities -> Pauli expectations ----------
def probs_of_counts(c):
    """c: {bitstring 'b2b1b0' (fin[2] fin[1] fin[0] = s c1 c0): n} -> p[x0, x1, xs]"""
    p = np.zeros((2, 2, 2)); n = sum(c.values())
    for k, v in c.items(): p[int(k[-1]), int(k[-2]), int(k[-3])] += v
    return p / n, n
def evec(P):
    """P: {setting: p[2,2,2]} -> 64 expectations (index a*16+b*4+c, labels IXYZ), each averaged over every compatible setting"""
    E = np.zeros(64); E[0] = 1.0
    sgn = np.array([1, -1])
    for a, b, c in itertools.product(range(4), repeat=3):
        if a == b == c == 0: continue
        vals = []
        for st, p in P.items():
            if all(l == 0 or LAB[l] == st[q] for q, l in enumerate((a, b, c))):
                w = np.einsum('i,j,k->ijk', sgn if a else np.ones(2), sgn if b else np.ones(2), sgn if c else np.ones(2))
                vals.append((p * w).sum())
        E[a * 16 + b * 4 + c] = np.mean(vals)
    return E
def cond_s(P, t):
    """conditional <X_s>, <Y_s>, <Z_s> given clock reading t, from the settings with both clock bits read in Z"""
    x0, x1 = t % 2, t // 2; out = {}
    for b in 'XYZ':
        p = P['ZZ' + b][x0, x1, :]; out[b] = (p[0] - p[1]) / p.sum() if p.sum() > 0 else np.nan
    return out
def alpha(P, t):
    c = cond_s(P, t); return np.degrees(np.arctan2(c['X'], c['Z']))

# ---------- the look: per-qubit rotation + shrink fitted between arms ----------
def qmap(phi, lam):
    M = np.eye(4); c, s = np.cos(phi), np.sin(phi)
    M[1, 1], M[1, 2], M[2, 1], M[2, 2] = lam * c, -lam * s, lam * s, lam * c
    return M
def fit_look(ED, EM, x0=None):
    """least squares over (phi, lambda) per qubit. Point fit: 27 starts (phi in {-60, 0, +60} deg per qubit), lowest cost kept.
    Bootstrap fits: warm start at the point estimate (x0), one start -- so a resample cannot jump to another local minimum."""
    def res(x):
        T = kron3(qmap(x[0], x[3]), qmap(x[1], x[4]), qmap(x[2], x[5])); return (T @ ED - EM)[1:]
    lb, ub = [-np.pi] * 3 + [0] * 3, [np.pi] * 3 + [1.5] * 3
    starts = [x0] if x0 is not None else [list(np.radians(s)) + [1, 1, 1] for s in itertools.product((-60, 0, 60), repeat=3)]
    best = min((least_squares(res, x0=s, bounds=(lb, ub)) for s in starts), key=lambda r: r.cost)
    return np.degrees(best.x[:3]), best.x[3:], best.x
def fidelity(E): return float(E @ E_IDEAL) / 8.0

# ---------- readout model (from the record) ----------
def readout_none_P(p10, p01, theta=THETA):
    """ideal state through the record's assignment error, exact (no shots): {setting: p}"""
    rho = np.outer(ideal_psi(theta), ideal_psi(theta).conj()); return {st: assign(probs_exact(rho, st), p10, p01) for st in SETTINGS}
def probs_exact(rho, st):
    U = kron3(ROT[st[0]], ROT[st[1]], ROT[st[2]]); return np.real(np.diag(U @ rho @ U.conj().T)).reshape(2, 2, 2).clip(0)
def assign(p, p10, p01):
    for q in range(3):
        A = np.array([[1 - p10[q], p01[q]], [p10[q], 1 - p01[q]]]); p = np.moveaxis(np.tensordot(A, np.moveaxis(p, q, 0), axes=(1, 0)), 0, q)
    return p

# ---------- readings with four outcomes ----------
def outcome(lo, hi, ok=True):
    if not ok or not (np.isfinite(lo) and np.isfinite(hi)): return 'CANNOT_TELL'
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'
def readings_point(PD, PM, none_alpha, x0=None):
    ED, EM = evec(PD), evec(PM); phi, lam, xb = fit_look(ED, EM, x0)
    r = {f'R1 alpha(t={t}) - none [deg]': alpha(PD, t) - none_alpha[t] for t in range(4)}
    for q, nm in enumerate(('c0', 'c1', 's')): r[f'R2 kick {nm} [deg/readout]'] = phi[q] / NREAD
    r['R3 dF (M - D)'] = fidelity(EM) - fidelity(ED)
    r['R4 delta = phi_c1 - 2 phi_c0 [deg]'] = phi[1] - 2 * phi[0]
    return r, lam, fidelity(ED), fidelity(EM), xb
def resample(C, rng):
    return {st: dict(zip(c.keys(), rng.multinomial(sum(c.values()), np.array(list(c.values())) / sum(c.values())))) for st, c in C.items()}
def to_P(C): return {st: probs_of_counts(c)[0] for st, c in C.items()}
def coherent_enough(PD, n):
    """censor (check 24): a qubit's fitted kick is CANNOT_TELL if every X/Y-bearing expectation on it in arm D is under 5x shot noise"""
    ED = evec(PD); ok = []
    for q in range(3):
        idx = [i for i, (a, b, c) in enumerate(itertools.product(range(4), repeat=3)) if (a, b, c)[q] in (1, 2)]
        ok.append(np.max(np.abs(ED[idx])) > 5 / np.sqrt(n))
    return ok
def analyse(CD, CM, none_alpha, rng, B=400):
    r0, lam, FD, FM, xb = readings_point(to_P(CD), to_P(CM), none_alpha)
    bs = {k: [] for k in r0}
    for _ in range(B):
        rb, *_ = readings_point(to_P(resample(CD, rng)), to_P(resample(CM, rng)), none_alpha, x0=xb)
        for k, v in rb.items(): bs[k].append(v)
    n = min(sum(c.values()) for c in CD.values()); coh = coherent_enough(to_P(CD), n)
    out = {}
    for k, v in r0.items():
        lo, hi = np.percentile(bs[k], BAND); ok = True
        for q, nm in enumerate(('c0', 'c1', 's')):
            if f'kick {nm}' in k: ok = coh[q]
        if k.startswith('R4'): ok = coh[0] and coh[1]
        out[k] = (v, lo, hi, outcome(lo, hi, ok))
    return out, lam, FD, FM

# ---------- synthetic worlds ----------
def make_rho(theta, deph, phis=(0, 0, 0), lam_look=(1, 1, 1)):
    psi = ideal_psi(theta); rho = np.outer(psi, psi.conj())
    for q in range(3):
        U = [np.eye(2)] * 3; U = list(U); U[q] = np.diag([np.exp(-1j * phis[q] / 2), np.exp(1j * phis[q] / 2)])
        Uq = kron3(*U); rho = Uq @ rho @ Uq.conj().T
        l = deph[q] * lam_look[q]; D = np.ones((8, 8))
        bits = np.array([[(i >> (2 - qq)) & 1 for qq in range(3)] for i in range(8)])
        D[bits[:, q][:, None] != bits[:, q][None, :]] = l; rho = rho * D
    return rho
def sample(rho, p10, p01, shots, rng):
    C = {}
    for st in SETTINGS:
        p = assign(probs_exact(rho, st), p10, p01).reshape(8); p = p / p.sum(); k = rng.multinomial(shots, p)
        C[st] = {f'{(i >> 0) & 1}{(i >> 1) & 1}{(i >> 2) & 1}': int(v) for i, v in enumerate(k) if v}   # key = s c1 c0 (index i = x0*4 + x1*2 + xs)
    return C

if __name__ == '__main__' and '--synth' in sys.argv:
    rng = np.random.default_rng(20261024); SHOTS = 2000; NDRAW = int(os.environ.get('NDRAW', 40)); B = int(os.environ.get('BOOT', 100))
    p10 = [0.00122, 0.00317, 0.00806]; p01 = [0.00732, 0.00879, 0.01221]   # kingston record 24 Oct 07:12 EDT for q3 (c0), q23 (c1), q16 (s)
    none_alpha = [alpha(readout_none_P(p10, p01), t) for t in range(4)]
    DEPH = (0.92, 0.85, 0.9); d = np.radians
    W = {  # name: (theta_D, phis (total, rad), look shrink, expected outcomes)
      'W0 null (no look effect)':          (THETA, (0, 0, 0), (1, 1, 1), dict(c0='C', c1='C', s='C', dF='C', delta='C', a='CCCC')),
      'W1 clock only (-12, -72 deg)':      (THETA, (d(-12), d(-72), 0), (.97, .97, 1), dict(c0='B', c1='B', s='C', dF='B', delta='B', a='CCCC')),
      'W2 system only (-30 deg)':          (THETA, (0, 0, d(-30)), (1, 1, .97), dict(c0='C', c1='C', s='B', dF='B', delta='C', a='CCCC')),
      'W3 uniform clock + system':         (THETA, (d(-10), d(-20), d(-30)), (.97, .97, .97), dict(c0='B', c1='B', s='B', dF='B', delta='C', a='CCCC')),
      'W4 NEITHER (0.05 deg each)':        (THETA, (d(-.05), d(-.05), d(-.05)), (1, 1, 1), dict(c0='C', c1='C', s='C', dF='C', delta='C', a='CCCC')),
      'W5 D over-rotated +4 deg/tick':     (THETA + d(4), (0, 0, 0), (1, 1, 1), dict(c0='C', c1='C', s='C', dF='C', delta='C', a=None)),
      'W6 R1 null: D = ideal + readout':    (THETA, (0, 0, 0), (1, 1, 1), dict(c0='C', c1='C', s='C', dF='C', delta='C', a='CCCC')),
    }
    key = lambda k: ('a' if k.startswith('R1') else 'c0' if 'kick c0' in k else 'c1' if 'kick c1' in k else 's' if 'kick s' in k else 'dF' if k.startswith('R3') else 'delta')
    L = {'C': 'CONSISTENT', 'B': 'BELOW', 'A': 'ABOVE'}
    fa = nf = mi = nm = 0; lines = [f'pooters.py --synth  {NDRAW} draws per world, {SHOTS} shots x 27 settings x 2 arms, bootstrap {B}; readout from the kingston record; none alpha(t) = ' + ', '.join(f'{a:.2f}' for a in none_alpha)]
    for name, (thD, phis, lamL, exp) in W.items():
        tally = {}; deph = (1, 1, 1) if name[:2] in ('W5', 'W6') else DEPH; scoreR1 = name[:2] in ('W5', 'W6')
        for _ in range(NDRAW):
            CD = sample(make_rho(thD, deph), p10, p01, SHOTS, rng); CM = sample(make_rho(thD, deph, phis, lamL), p10, p01, SHOTS, rng)
            res, lam, FD, FM = analyse(CD, CM, none_alpha, rng, B=B)
            for k, (v, lo, hi, oc) in res.items():
                tally.setdefault(k, {}).setdefault(oc, 0); tally[k][oc] += 1
                kk = key(k)
                if kk == 'a' and not scoreR1: continue
                if kk == 'a':
                    if exp['a'] is None:   # W5: alpha(t) planted = t*4 deg above the none for t>=1 (plus dephasing effects): scored as ABOVE for t>=1, CONSISTENT t=0
                        t = int(k[11]); want = 'CONSISTENT' if t == 0 else 'ABOVE'
                    else: want = L[exp['a'][int(k[11])]]
                else: want = L[exp[kk]]
                if want == 'CONSISTENT': nf += 1; fa += oc != 'CONSISTENT'
                else: nm += 1; mi += oc != want
        lines.append(f'== {name}')
        for k, t in tally.items(): lines.append(f'   {k:40s} ' + '  '.join(f'{o} {n}' for o, n in sorted(t.items())))
    lines.append(f'FALSE CALLS (planted CONSISTENT read as ABOVE/BELOW): {fa}/{nf} = {100 * fa / nf:.1f} %   MISSES (planted ABOVE/BELOW read otherwise): {mi}/{nm} = {100 * mi / nm:.1f} %')
    print('\n'.join(lines))

if __name__ == '__main__' and '--real' in sys.argv:
    rng = np.random.default_rng(20261025)
    lay = json.load(open(f'{HERE}/job_pooters.json'))['layout']
    def none_for(J):   # the readout none from the record saved before that job (check 3); pooled uses J1's
        props = json.load(open(f'{HERE}/props_pooters_before_{J}.json'))
        rec = lambda q, name: [x['value'] for x in props['qubits'][q] if x['name'] == name][0]
        p10 = [rec(q, 'prob_meas1_prep0') for q in lay]; p01 = [rec(q, 'prob_meas0_prep1') for q in lay]
        na = [alpha(readout_none_P(p10, p01), t) for t in range(4)]
        print(f'record before {J}: layout c0,c1,s = {lay}; p10 {p10} p01 {p01}; none alpha(t) = ' + ', '.join(f'{a:.2f}' for a in na)); return na
    NONE = {'copy 0 (J1)': none_for('J1'), 'copy 1 (J2)': none_for('J2')}; NONE['pooled'] = NONE['copy 0 (J1)']
    print('ideal alpha(t) = 0, 45, 90, 135 deg; arm D ideal conditional Bloch of s = (sin t theta, 0, cos t theta)')
    copies = {}
    for J in ('J1', 'J2'):
        raw = json.load(open(f'{HERE}/raw_pooters_{J}.json'))
        copies[J] = ({e['setting']: e['counts'] for e in raw if e['arm'] == 'D'}, {e['setting']: e['counts'] for e in raw if e['arm'] == 'M'})
    pooled = tuple({st: {k: copies['J1'][a][st].get(k, 0) + copies['J2'][a][st].get(k, 0) for k in set(copies['J1'][a][st]) | set(copies['J2'][a][st])} for st in SETTINGS} for a in (0, 1))
    R = {}
    for lab, (CD, CM) in [('copy 0 (J1)', copies['J1']), ('copy 1 (J2)', copies['J2']), ('pooled', pooled)]:
        R[lab] = analyse(CD, CM, NONE[lab], rng)
        res, lam, FD, FM = R[lab]
        print(f'-- {lab}: F(D) {FD:.4f}  F(M) {FM:.4f}  fitted look shrink lambda c0,c1,s = ' + ', '.join(f'{l:.3f}' for l in lam))
        for t in range(4):
            for arm, CC in (('D', CD), ('M', CM)):
                c = cond_s(to_P(CC), t); print(f'   arm {arm} conditional Bloch of s | t={t}: X {c["X"]:+.3f} Y {c["Y"]:+.3f} Z {c["Z"]:+.3f}  length {np.sqrt(c["X"]**2 + c["Y"]**2 + c["Z"]**2):.3f}  (ideal {np.sin(t*THETA):+.3f} +0.000 {np.cos(t*THETA):+.3f}, length 1)')
        for k, (v, lo, hi, oc) in res.items(): print(f'   {k:40s} {v:+9.4f} [{lo:+9.4f}, {hi:+9.4f}] -> {oc}')
    print('FINAL (pooled if the copies agree, else CANNOT_TELL)')
    for k in R['pooled'][0]:
        o0, o1, (v, lo, hi, op) = R['copy 0 (J1)'][0][k][3], R['copy 1 (J2)'][0][k][3], R['pooled'][0][k]
        g = R['copy 1 (J2)'][0][k][0] - R['copy 0 (J1)'][0][k][0]
        fin = op if o0 == o1 else 'CANNOT_TELL'
        print(f'   {k:40s} {v:+9.4f} [{lo:+9.4f}, {hi:+9.4f}]  copies {o0}/{o1}  gap {g:+.4f}  -> {fin}' + (f'  (bound: |value| within [{lo:+.4f}, {hi:+.4f}])' if fin == 'CONSISTENT' else ''))
