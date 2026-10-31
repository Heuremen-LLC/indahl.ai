"""ball.py -- analysis + synthetic for the UChicago run (PLAN_BALL.md.text). 24 Oct 2026.
Their protocol (arXiv 2606.00433v3, S7.2): Pauli input P in {I,X,Y,Z} on |0>, then L = 3 consecutive MCMs, each preceded by a random Z^c;
record the 3-bit string w = w1 w2 w3. Equal weighting of the four inputs gives the maximally mixed input pi = (1/2, 1/2).
Gauge invariants (their "Equation (4), together with p(0), gives the five gauge invariants"): with S_n = Pr(first n readouts all 0) =
1^T M0^n pi, Cayley-Hamilton gives S_2 = T0 S_1 - D0 and S_3 = T0 S_2 - D0 S_1, so T0 = tr M0, D0 = det M0 follow from S_1..S_3; the same
with ones gives T1, D1; and p0 = S_1. Plus two exchangeability readings defined by us: a12 = Pr(w1=1,w2=0) - Pr(w1=0,w2=1) and a23 the
same for (w2,w3). With no change of state between readouts any readout model gives a = 0 exactly; a > 0 means 1 -> 0 transitions
(decay) outnumber 0 -> 1 (excitation).
Usage: ball.py --synth   (synthetic worlds -> synth_results_ball.text)
       ball.py --real    (reads raw_ball_J1.npz, raw_ball_J2.npz, job_ball.json -> results)"""
import json, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
BAND = (0.5, 99.5)          # 99 % shot-bootstrap band, fixed before any job (Page-Wootters and an earlier run needed it; checked again in the synthetic)
B = 400
NAMES = ['p0', 'T0', 'D0', 'T1', 'D1', 'a12', 'a23']
L = 3

# ---------- invariants from an 8-vector of string probabilities, index = w1 + 2 w2 + 4 w3 ----------
def _bits(i): return (i & 1, (i >> 1) & 1, (i >> 2) & 1)
_W = np.array([_bits(i) for i in range(8)])            # (8, 3)
def invariants(P):
    """P: (..., 8) probabilities. Returns (..., 7) in NAMES order."""
    P = np.asarray(P, float)
    def run(v):  # S_n for a run of n readouts all equal to v
        m1 = (_W[:, 0] == v); m2 = m1 & (_W[:, 1] == v); m3 = m2 & (_W[:, 2] == v)
        return P[..., m1].sum(-1), P[..., m2].sum(-1), P[..., m3].sum(-1)
    out = []
    S1, S2, S3 = run(0); R1, R2, R3 = run(1)
    with np.errstate(divide='ignore', invalid='ignore'):
        T0 = (S3 - S1 * S2) / (S2 - S1 ** 2); D0 = T0 * S1 - S2
        T1 = (R3 - R1 * R2) / (R2 - R1 ** 2); D1 = T1 * R1 - R2
    def pair(a, b, x, y): return P[..., (_W[:, a] == x) & (_W[:, b] == y)].sum(-1)
    a12 = pair(0, 1, 1, 0) - pair(0, 1, 0, 1); a23 = pair(1, 2, 1, 0) - pair(1, 2, 0, 1)
    return np.stack([S1, T0, D0, T1, D1, a12, a23], -1)

def strings_from_bits(m1, m2, m3):
    """m_l: (shots, K) bool -> (K, 8) counts"""
    idx = m1.astype(int) + 2 * m2.astype(int) + 4 * m3.astype(int)
    return np.stack([np.bincount(idx[:, k], minlength=8) for k in range(idx.shape[1])])

def boot_inv(C, rng, B=B):
    """C: (Q, 8) counts. Returns point (Q,7) and draws (B,Q,7)."""
    C = np.asarray(C); n = C.sum(1); P = C / n[:, None]
    draws = np.stack([rng.multinomial(n[q], P[q], size=B) / n[q] for q in range(len(C))], 1)   # (B,Q,8)
    return invariants(P), invariants(draws)

def outcome(lo, hi, ok=True):
    if not ok or not (np.isfinite(lo) and np.isfinite(hi)): return 'CANNOT_TELL'
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'

def band(x): return np.nanpercentile(x, BAND[0], axis=0), np.nanpercentile(x, BAND[1], axis=0)

# ---------- reading 3: Ramsey phase on unmeasured neighbours ----------
def phase_of(nx0, nx, ny0, ny):
    """nx0 = count of 0 in X basis of nx shots; returns phase atan2(<Y>, <X>) [rad] and coherence"""
    X = 2 * nx0 / nx - 1; Y = 2 * ny0 / ny - 1
    return np.arctan2(Y, X), np.hypot(X, Y)
def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi
def kick_readings(CM, CD, rng, B=B, ok=None):
    """CM/CD: dict basis -> (N, 2) array [count0, shots] per neighbour. Returns per-neighbour kick deg/readout point+draws, and coherence in D."""
    def draw(C):
        n = C[:, 1]; p = C[:, 0] / n
        return rng.binomial(n[None, :].repeat(B, 0), p[None, :].repeat(B, 0))
    phM, _ = phase_of(CM['X'][:, 0], CM['X'][:, 1], CM['Y'][:, 0], CM['Y'][:, 1])
    phD, cohD = phase_of(CD['X'][:, 0], CD['X'][:, 1], CD['Y'][:, 0], CD['Y'][:, 1])
    k0 = np.degrees(wrap(phM - phD)) / L
    bM, _ = phase_of(draw(CM['X']), CM['X'][:, 1], draw(CM['Y']), CM['Y'][:, 1])
    bD, _ = phase_of(draw(CD['X']), CD['X'][:, 1], draw(CD['Y']), CD['Y'][:, 1])
    kb = np.degrees(wrap(bM - bD)) / L
    n = min(CD['X'][:, 1].min(), CD['Y'][:, 1].min())
    keep = cohD > 5 / np.sqrt(n)                      # censor (check 24)
    if ok is not None: keep = keep & ok
    return k0, kb, keep, cohD

# ---------- the full set of readings for one copy (or pooled) ----------
def readings(arms, rng):
    """arms: {'A': (Q,8), 'Bhi': (Q,8), 'Blo': (4,8), 'Blo_idx': list of 4 indices into Q, 'CM': {...}, 'CD': {...}, 'nb_ok': bool array}"""
    R = {}
    pA, dA = boot_inv(arms['A'], rng); pH, dH = boot_inv(arms['Bhi'], rng); pL, dL = boot_inv(arms['Blo'], rng)
    li = arms['Blo_idx']
    # reading 1: arm A medians over targets (values with bands; a12/a23 also get an outcome vs 0)
    for j, nm in enumerate(NAMES):
        v = np.nanmedian(pA[:, j]); lo, hi = band(np.nanmedian(dA[:, :, j], 1))
        R[f'R1 A median {nm}'] = (v, lo, hi, outcome(lo, hi) if nm in ('a12', 'a23') else 'VALUE')
    R['_A_point'] = pA; R['_A_band'] = band(dA)
    R['_a12_pos'] = int(np.sum(pA[:, 5] > 0)); R['_Q'] = len(pA)
    # reading 2: does K matter? median over targets of the per-target difference
    for lab, p, d, idx in [('Bhi-A', pH, dH, slice(None)), ('Blo-A', pL, dL, li)]:
        diff_p = p - pA[idx]; diff_d = d - dA[:, idx]
        for j, nm in enumerate(NAMES):
            v = np.nanmedian(diff_p[:, j]); lo, hi = band(np.nanmedian(diff_d[:, :, j], 1))
            R[f'R2 {lab} median d{nm}'] = (v, lo, hi, outcome(lo, hi))
        lo_q, hi_q = band(diff_d)
        R[f'_{lab}_perq'] = [[outcome(lo_q[q, j], hi_q[q, j]) for j in range(len(NAMES))] for q in range(len(diff_p))]
    # reading 3: neighbour phase, readout minus equal idle, deg per readout
    k0, kb, keep, coh = kick_readings(arms['CM'], arms['CD'], rng, ok=arms.get('nb_ok'))
    if keep.sum() >= 3:
        v = float(np.median(k0[keep])); lo, hi = band(np.median(kb[:, keep], 1)); o = outcome(lo, hi)
    else: v, lo, hi, o = np.nan, np.nan, np.nan, 'CANNOT_TELL'
    R['R3 neighbour kick median [deg/readout]'] = (v, lo, hi, o); R['_nb_kept'] = int(keep.sum()); R['_nb_total'] = len(keep)
    return R

def known_good(R):
    v, lo, hi, o = R['R1 A median a12']
    ok = (lo > 0) and (R['_a12_pos'] >= 16)
    return ok, f"a12 median {v:+.5f} [{lo:+.5f}, {hi:+.5f}] {o}; a12 > 0 on {R['_a12_pos']} of {R['_Q']} targets -> {'PASS' if ok else 'FAIL'}"

# ---------- synthetic ----------
def instrument(e10, e01, eta_dn, eta_up):
    """product model: outcome from pre-state with readout errors, post-state flips independent of outcome. M[o][s', s]"""
    Po = np.array([[1 - e10, e01], [e10, 1 - e01]])             # Po[o, s]
    Ps = np.array([[1 - eta_up, eta_dn], [eta_up, 1 - eta_dn]])  # Ps[s', s]
    return [Ps * Po[o][None, :] for o in (0, 1)]
def string_probs(M, pi=(0.5, 0.5)):
    pi = np.array(pi); P = np.zeros(8)
    for i in range(8):
        w = _bits(i); v = pi.copy()
        for o in w: v = M[o] @ v
        P[i] = v.sum()
    return P
def sim_counts(params, shots, rng):
    return np.stack([rng.multinomial(shots, string_probs(instrument(*p))) for p in params])
def sim_ramsey(coh, phi0, kick_total, e10, e01, shots, rng):
    out = {}
    for basis, f in (('X', np.cos), ('Y', np.sin)):
        p0 = (1 + coh * f(phi0 + kick_total)) / 2
        p0m = p0 * (1 - e10) + (1 - p0) * e01            # read 0: from |0> kept, from |1> mis-read
        out[basis] = np.stack([rng.binomial(shots, p0m), np.full(len(p0m), shots)], 1)
    return out

def synth(path):
    rng = np.random.default_rng(20261024)
    cfg = json.load(open(f'{HERE}/synth_config.json'))
    Q = cfg['Q']; NB = cfg['NB']; shA = cfg['shots_A']; shL = cfg['shots_Blo']; shC = cfg['shots_C_per_basis']
    base = np.array(cfg['targets_params'])        # (Q, 4): e10, e01, eta_dn, eta_up from the kingston record
    nbr = np.array(cfg['nb_readout'])            # (NB, 2)
    li = cfg['Blo_idx']
    worlds = {
        'S0 null (no K dependence, no phase)':       dict(hi=(1, 1, 1, 1), lo=(1, 1, 1, 1), kick=0.0),
        'S1 K dependence only (hi: eta_dn x1.5, e01 x1.3; lo: eta_dn x0.7)': dict(hi=(1, 1.3, 1.5, 1), lo=(1, 1, 0.7, 1), kick=0.0),
        'S2 phase only (-1.0 deg/readout, spread 0.5)': dict(hi=(1, 1, 1, 1), lo=(1, 1, 1, 1), kick=-1.0),
        'S3 both':                                    dict(hi=(1, 1.3, 1.5, 1), lo=(1, 1, 0.7, 1), kick=-1.0),
        'S4 NEITHER resolvable (hi eta_dn x1.03, kick -0.03)': dict(hi=(1, 1, 1.03, 1), lo=(1, 1, 1.0, 1), kick=-0.03),
        'S5 known-good null (eta_dn = eta_up = 0.002: no decay/excitation asymmetry)': dict(hi=(1, 1, 1, 1), lo=(1, 1, 1, 1), kick=0.0, sym=True),
    }
    ND = cfg['draws']; lines = [f'SYNTHETIC -- ball.py, {ND} draws per world, bootstrap {B}, band {BAND}; Q={Q} targets, Blo on {len(li)}, NB={NB} neighbours;'
                               f' shots per copy: A/Bhi {shA} per target, Blo {shL} per target, C {shC} per basis per arm. Two copies + pooled; FINAL = pooled if copies agree.']
    tot_null = tot_false = 0; kg_pass = 0; kg_n = 0; kg_sym_pass = 0
    for wname, w in worlds.items():
        tally = {}
        perq_false = perq_n = 0
        for d in range(ND):
            copies = []
            kick_q = (w['kick'] + (0.5 * rng.standard_normal(NB) if abs(w['kick']) > 0.5 else 0.0)) * L
            coh = rng.uniform(0.8, 0.95, NB); phi0 = rng.uniform(-np.pi, np.pi, NB)
            b0 = base.copy()
            if w.get('sym'): b0[:, 2] = 0.002; b0[:, 3] = 0.002
            for c in range(2):
                pA = b0; pH = b0 * np.array(w['hi']); pL = b0[li] * np.array(w['lo'])
                arms = dict(A=sim_counts(pA, shA, rng), Bhi=sim_counts(pH, shA, rng), Blo=sim_counts(pL, shL, rng), Blo_idx=li,
                            CM=sim_ramsey(coh, phi0, np.radians(kick_q), nbr[:, 0], nbr[:, 1], shC, rng),
                            CD=sim_ramsey(coh, phi0, 0.0, nbr[:, 0], nbr[:, 1], shC, rng))
                copies.append(arms)
            pooled = dict(A=copies[0]['A'] + copies[1]['A'], Bhi=copies[0]['Bhi'] + copies[1]['Bhi'], Blo=copies[0]['Blo'] + copies[1]['Blo'], Blo_idx=li,
                          CM={b: np.stack([copies[0]['CM'][b][:, 0] + copies[1]['CM'][b][:, 0], copies[0]['CM'][b][:, 1] + copies[1]['CM'][b][:, 1]], 1) for b in 'XY'},
                          CD={b: np.stack([copies[0]['CD'][b][:, 0] + copies[1]['CD'][b][:, 0], copies[0]['CD'][b][:, 1] + copies[1]['CD'][b][:, 1]], 1) for b in 'XY'})
            R0, R1, RP = readings(copies[0], rng), readings(copies[1], rng), readings(pooled, rng)
            ok, _ = known_good(RP)
            if w.get('sym'): kg_sym_pass = kg_sym_pass + ok
            else: kg_pass += ok; kg_n += 1
            for k in RP:
                if k.startswith('_') or RP[k][3] == 'VALUE': continue
                fin = RP[k][3] if R0[k][3] == R1[k][3] else 'CANNOT_TELL'
                tally.setdefault(k, {}).setdefault(fin, 0); tally[k][fin] += 1
            # per-target floor (null parts only)
            for lab, planted in (('Bhi-A', w['hi'] != (1, 1, 1, 1)), ('Blo-A', w['lo'] != (1, 1, 1, 1))):
                if planted: continue
                for row in RP[f'_{lab}_perq']:
                    for o in row: perq_n += 1; perq_false += (o in ('ABOVE', 'BELOW'))
        lines.append(f'== {wname}')
        null_k = lambda k: (k.startswith('R2 Bhi') and w['hi'] == (1, 1, 1, 1)) or (k.startswith('R2 Blo') and w['lo'] == (1, 1, 1, 1)) or (k.startswith('R3') and w['kick'] == 0)
        for k, t in tally.items():
            tag = ' [null]' if null_k(k) else ''
            lines.append(f'   {k:44s} ' + '  '.join(f'{o} {n}' for o, n in sorted(t.items())) + tag)
            if null_k(k):
                tot_null += sum(t.values()); tot_false += t.get('ABOVE', 0) + t.get('BELOW', 0)
        if perq_n: lines.append(f'   per-target floor (null comparisons): {perq_false} of {perq_n} per-target readings resolved ({100*perq_false/perq_n:.1f} %)')
    lines.append(f'KNOWN-GOOD rule (a12) passed in {kg_pass} of {kg_n} synthetic pooled runs with eta_dn > eta_up (their printed reading), and in {kg_sym_pass} of {ND} runs of S5 where the asymmetry is absent (must be ~0).')
    lines.append(f'FLOOR: {tot_false} false calls in {tot_null} planted-null summary readings ({100*tot_false/max(tot_null,1):.1f} %).')
    open(path, 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))

def load_real():
    rec = json.load(open(f'{HERE}/job_ball.json')); out = {}
    for J in ('J1', 'J2'):
        z = np.load(f'{HERE}/raw_ball_{J}.npz', allow_pickle=False); out[J] = z
    return rec, out

def assemble(rec, z):
    """counts per arm for one job from saved per-circuit bit arrays"""
    meta = rec['meta']; T = rec['targets']; NB = rec['neighbours']; Q = len(T)
    A = np.zeros((Q, 8), int); H = np.zeros((Q, 8), int); Lo = np.zeros((len(rec['Blo']), 8), int)
    C = {arm: {b: np.zeros((len(NB), 2), int) for b in 'XY'} for arm in ('M', 'D')}
    for i, m in enumerate(meta):
        if m['arm'] in ('A', 'Bhi', 'Blo'):
            S = strings_from_bits(z[f'm1_{i}'], z[f'm2_{i}'], z[f'm3_{i}'])        # columns = measured set of that circuit
            if m['arm'] == 'A': A += S[:Q]
            elif m['arm'] == 'Bhi': H += S[:Q]
            else: Lo[rec['Blo'].index(m['target'])] += S[0]
        else:
            f = z[f'fin_{i}']; C[m['arm'][1]][m['basis']][:, 0] += (~f).sum(0); C[m['arm'][1]][m['basis']][:, 1] += f.shape[0]
    return dict(A=A, Bhi=H, Blo=Lo, Blo_idx=[T.index(t) for t in rec['Blo']], CM=C['M'], CD=C['D'])

def real():
    rec, raw = load_real(); rng = np.random.default_rng(7)
    arms = {J: assemble(rec, raw[J]) for J in ('J1', 'J2')}
    nb_ok = np.array(rec['nb_readout_ok'])
    for J in arms: arms[J]['nb_ok'] = nb_ok
    pooled = {k: arms['J1'][k] + arms['J2'][k] for k in ('A', 'Bhi', 'Blo')}; pooled['Blo_idx'] = arms['J1']['Blo_idx']; pooled['nb_ok'] = nb_ok
    for arm in ('CM', 'CD'): pooled[arm] = {b: arms['J1'][arm][b] + arms['J2'][arm][b] for b in 'XY'}
    R = {'copy 0 (J1)': readings(arms['J1'], rng), 'copy 1 (J2)': readings(arms['J2'], rng), 'pooled': readings(pooled, rng)}
    ok, kgline = known_good(R['pooled'])
    print(f'=== ibm_kingston UChicago run; jobs {", ".join(j["job_id"] for j in rec["jobs"])}')
    print('KNOWN-GOOD (pooled): ' + kgline + ('' if ok else '  -> readings R2 and R3 are NOT DECIDED (instrument not established on this run)'))
    print('FINAL (pooled if the copies agree, else CANNOT_TELL)')
    for k in R['pooled']:
        if k.startswith('_'): continue
        o0, o1 = R['copy 0 (J1)'][k][3], R['copy 1 (J2)'][k][3]; v, lo, hi, op = R['pooled'][k]
        g = R['copy 1 (J2)'][k][0] - R['copy 0 (J1)'][k][0]
        fin = op if op == 'VALUE' else (op if o0 == o1 else 'CANNOT_TELL')
        if not ok and (k.startswith('R2') or k.startswith('R3')): fin = 'NOT DECIDED (' + fin + ')'
        print(f'   {k:44s} {v:+10.5f} [{lo:+10.5f}, {hi:+10.5f}]  copies {o0}/{o1}  gap {g:+.5f}  -> {fin}')
    P = R['pooled']; print(f"   neighbours kept for R3: {P['_nb_kept']} of {P['_nb_total']}")
    for lab in ('Bhi-A', 'Blo-A'):
        rows = P[f'_{lab}_perq']; cnt = {}
        for row in rows:
            for o in row: cnt[o] = cnt.get(o, 0) + 1
        print(f'   per-target {lab}: {cnt} over {len(rows)} targets x {len(NAMES)} invariants (null floor in synth_results_ball.text)')
    print('Per-target arm A values (pooled), with 99 % bands:')
    pA = P['_A_point']; lo, hi = P['_A_band']
    for q, t in enumerate(rec['targets']):
        print(f'   q{t:<4d} ' + '  '.join(f'{nm} {pA[q, j]:+.5f} [{lo[q, j]:+.5f},{hi[q, j]:+.5f}]' for j, nm in enumerate(NAMES)))

if __name__ == '__main__':
    if '--synth' in sys.argv: synth(f'{HERE}/synth_results_ball.text')
    elif '--real' in sys.argv: real()
