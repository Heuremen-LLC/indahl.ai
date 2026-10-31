"""kumar.py -- circuits and readings for the ABBA run (A1 B1 B2 A2) of Aryan Kumar's mid-circuit-measurement spectator PROBE (arXiv 2610.28705v1) on ibm_marrakesh.
His code (theirs/common.py, job2_core.py, job4_drift.py) is READ AS TEXT ONLY and never executed. The circuit builder below is my own re-implementation of the
construction described in that text; it is checked against his manifests (twirl metadata of all 200 instances of job2 and of job4 must be equal, see circuits_check()).
A = his job2 probe set (seed 20261003), B = his job4 probe set (seed 20261007). Qubits 4-5-6 (target, ancilla, spectator), measure_2 mid-circuit measurement,
10 settings (8 corners + (2,2,1),(2,2,3)) x 20 twirl instances x 1000 shots, SamplerV2, twirling OFF, dynamical decoupling OFF (manual twirls are in the circuits).

READINGS (units: the 20 twirl instances per set; observable <Xs>, baseline = setting (1,1,1); b_LM = his log-scale L x M coefficient, coded x = lambda - 2).
  DA  DRIFT   A2 - A1 baseline <Xs> (identical circuits and twirl draws, paired by instance).            S = 0.0561  (his printed job2->job4 baseline shift, 0.9058 -> 0.9619)
  SET TWIRL-SET B - A baseline <Xs> under ABBA (job-averaged per instance; different twirl draws).       S = 0.0561   guard (|DA| + hDA)/2 (a step between jobs leaves half in B-A)
  BLM b_LM(B) - b_LM(A) under ABBA, log scale, delta-method SE.                                          S = 0.0044  (his printed minimum detectable effect for b_LM)   same guard in b_LM units
  DP  STATED  delivered baseline minus the stated-T2 projection exp(-t/T2) (1 - 2 e_ro) of spectator qubit 6, from the record pulled just before each job.   S = 0.0168 (his job4 miss)
Band: two-sided t(19) at 99 % (alpha 0.01), fixed before any synth (four scored readings; family false rate about 4 % nominal).
Outcomes: ABOVE s - guard > h ; BELOW s + guard < -h ; CONSISTENT inside and h + guard <= S ; CANNOT_TELL otherwise (or any setting mean < 0.05).
Sign: DA = A2 - A1 (positive = baseline rose over the run); SET and BLM = B minus A (positive = his job4 set higher); DP = delivered minus projection."""
import numpy as np, zlib, json
from scipy import stats
FACTORIAL = [(g, l, m) for g in (1, 3) for l in (1, 3) for m in (1, 3)] + [(2, 2, 1), (2, 2, 3)]
FACT = FACTORIAL[:8]
SEED_A, SEED_B = 20261003, 20261007
K, SHOTS, LAYOUT, M_REF, TAU_FF = 20, 1000, [4, 5, 6], 3, 1.0e-6
BID = zlib.crc32(b'probe')
LABELS = ('A1', 'B1', 'B2', 'A2'); SET_OF = {'A1': 'A', 'A2': 'A', 'B1': 'B', 'B2': 'B'}
S_SHIFT, S_BLM, S_DP = 0.0561, 0.0044, 0.0168
ALPHA = 0.01; TQ = float(stats.t.ppf(1 - ALPHA / 2, K - 1))

# ---------------------------------------------------------------- circuits (own re-implementation, checked against his manifests)
def echo_seq(q, n, gran):
    r = lambda v: (v // gran) * gran
    if q % 2 == 0:
        a = r(n // 2); return [a, 'x', n - a, 'x']
    a, b = r(n // 4), r(n // 2); return [a, 'x', b, 'x', n - a - b]
def conj(pa, pb):
    xb = lambda p: p in (1, 2); zb = lambda p: p in (2, 3)
    mk = lambda x, z: {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}[(int(x), int(z))]
    return mk(xb(pa), zb(pa) ^ xb(pb)), mk(xb(pb), zb(pb) ^ xb(pa))
class Timing:
    """durations in seconds from the backend target (physical qubits LAYOUT)"""
    def __init__(self, target):
        self.t = target; self.dt = target.dt; self.gran = int(getattr(target, 'granularity', 1) or 1); self.minlen = int(getattr(target, 'min_length', 1) or 1)
    def dur(self, name, q):
        try: d = self.t[name][(q,)].duration; return float(d) if d else 0.0
        except KeyError: return 0.0
    def slot(self, v): p = LAYOUT[v]; return self.dur('measure_2', p) + 2 * self.dur('x', p)
    def to_dt(self, sec):
        n = int(round(sec / self.dt / self.gran)) * self.gran
        if 0 < n < self.minlen: n = int(np.ceil(self.minlen / self.gran)) * self.gran
        return n
def build_one(lam, seed, si, k, tim, window_dt=None):
    """one probe circuit. lam = (G, L, M). window_dt: use his recorded window length (exactly his circuit) instead of the live target's."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit.classical import expr
    from qiskit_ibm_runtime.circuit import MidCircuitMeasure
    G, L, M = lam; rng = np.random.default_rng([seed, BID, si, k]); fold_half = bool(rng.integers(2))
    qc = QuantumCircuit(QuantumRegister(3, 'q')); mreg = ClassicalRegister(M, 'mcm'); qc.add_register(mreg)
    meta = {'bench': 'probe', 'setting': list(lam), 'cz_twirl': [], 'folds': [], 'mcm_twirl': []}
    t, a, s = 0, 1, 2
    P = lambda p, q: (qc.x(q) if p == 1 else qc.y(q) if p == 2 else qc.z(q) if p == 3 else None)
    qc.h(s); qc.h(a)
    nf = {1: 1, 3: 3, 5: 5}.get(G, 3 if fold_half else 1); meta['folds'].append(nf)
    for _ in range(nf):
        pa, pb = int(rng.integers(4)), int(rng.integers(4)); P(pa, a); P(pb, t); qc.cz(a, t); ca, cb = conj(pa, pb); P(ca, a); P(cb, t)
        qc.barrier(a, t); meta['cz_twirl'].append([pa, pb])
    bits, R, mi = [], 0, 0                                                       # mid-circuit measurement of the ancilla, M repeats
    for _ in range(M):
        r = int(rng.integers(2)); R ^= r
        if r: qc.x(a)
        c = mreg[mi]; mi += 1; qc.append(MidCircuitMeasure(), [a], [c])
        if r: qc.x(a)
        bits.append(c)
    meta['mcm_twirl'].append({'qubit': a, 'R': R, 'first_clbit': mi - M})
    slot = max(tim.slot(q) for q in (t, a, s)); tau_w = M_REF * slot + TAU_FF; pad = max(M_REF - M, 0) * slot; total = pad + (L - 1) * tau_w
    n = tim.to_dt(total) if window_dt is None else int(window_dt)
    meta.update({'pad_s': pad, 'delta_s': (L - 1) * tau_w, 'tau_w_s': tau_w, 'echo': True, 'window_dt': n})
    qc.barrier(t, a, s)
    for q in (t, a, s):
        for part in echo_seq(q, n, tim.gran):
            if part == 'x': qc.x(q); qc.barrier(q)
            elif part > 0: qc.delay(max(part, tim.minlen), q, unit='dt')
    qc.barrier(t, a, s)
    if R: qc.x(t)                                                                # conditional X on the target, parity of the M bits xor R
    e = expr.lift(bits[0])
    for c in bits[1:]: e = expr.bit_xor(e, expr.lift(c))
    with qc.if_test(e): qc.x(t)
    fin = ClassicalRegister(3, 'fin'); qc.add_register(fin); fmap = {}
    for i, (q, b, lab) in enumerate([(s, 'X', 's'), (t, 'Z', 't'), (a, 'Z', 'a')]):
        if b == 'X': qc.h(q)
        r = int(rng.integers(2))
        if r: qc.x(q)
        qc.measure(q, fin[i]); fmap[lab] = [i, r]
    meta['fin_map'] = fmap; meta.update({'twirl': k, 'seed': [seed, BID, si, k], 'pad_on': True})
    return qc, meta
def build_set(seed, tim, his_metas=None):
    out = []
    for si, lam in enumerate(FACTORIAL):
        for k in range(K):
            wd = None
            if his_metas is not None: wd = next(m['window_dt'] for m in his_metas if m['setting'] == list(lam) and m['twirl'] == k)
            out.append(build_one(lam, seed, si, k, tim, wd))
    return out
def meta_equal(m, h):
    """my rebuilt metadata equals his manifest's (twirl draws, folds, mcm R, fin_map, window); floats to 1e-12"""
    ks = ('setting', 'cz_twirl', 'folds', 'mcm_twirl', 'fin_map', 'window_dt', 'echo', 'twirl', 'seed', 'pad_on')
    if any(m[k] != h[k] for k in ks): return False
    return all(abs(m[k] - h[k]) < 1e-12 for k in ('pad_s', 'delta_s', 'tau_w_s'))
def his_probe_metas(manifest_path):
    man = json.load(open(manifest_path)); return [s for s in man['subjobs'] if s['bench'] == 'probe'][0]['metas']
def check_isa(logical, isa):
    lo, io = logical.count_ops(), isa.count_ops(); bad = []
    if sum(n for g, n in io.items() if g in ('cz', 'ecr', 'cx', 'swap', 'rzz')) != lo.get('cz', 0): bad.append('2q gates changed')
    if io.get('if_else', 0) != lo.get('if_else', 0): bad.append('if_else changed')
    meas = lambda o: o.get('measure', 0) + o.get('measure_2', 0)
    if meas(io) != meas(lo): bad.append('measurements changed')
    if io.get('delay', 0) != lo.get('delay', 0): bad.append('delays changed')
    return bad

# ---------------------------------------------------------------- decoding and readings
def obs_xs(rec):
    """<Xs> of one instance from counts_fin; key string = highest clbit first, fin_map gives [bit index, twirl flip]"""
    idx, flip = rec['fin_map']['s']; tot = 0.0; n = 0
    for key, c in rec['counts_fin'].items():
        bit = int(key.replace(' ', '')[len(key.replace(' ', '')) - 1 - idx]) ^ flip; tot += (1 - 2 * bit) * c; n += c
    return tot / n
def inst_of(recs):
    """dict setting -> array(K) of per-instance <Xs>, ordered by twirl index"""
    d = {}
    for r in recs: d.setdefault(tuple(r['setting']), {})[r['twirl']] = obs_xs(r)
    return {s: np.array([v[k] for k in range(K)]) for s, v in d.items()}
def blm_of(means):
    f = {s: np.log(means[s]) for s in FACT}
    return sum((l - 2) * (m - 2) * f[(g, l, m)] for (g, l, m) in FACT) / 8
def blm_var(se_by_setting, mu_by_setting):
    """delta method: var(b_LM) = sum_s c_s^2 var(ln mu_s) / 64, c_s = (l-2)(m-2) = +-1"""
    return sum((se_by_setting[s] / mu_by_setting[s]) ** 2 for s in FACT) / 64
def proj(t2_s, ro, t_s):
    """stated-T2 projection of the spectator <Xs>: exp(-t/T2) (1 - 2 readout error); IBM's T2 is an echo T2 used as a single-exponential rate (assumption, /q 1)"""
    return float(np.exp(-t_s / t2_s) * (1 - 2 * ro))
def outcome(s, h, S, guard=0.0, censored=False):
    if censored: return 'CANNOT_TELL'
    if s - guard > h: return 'ABOVE'
    if s + guard < -h: return 'BELOW'
    return 'CONSISTENT' if h + guard <= S else 'CANNOT_TELL'
def readings(inst, p):
    """inst: label -> {setting -> array(K)} for A1 B1 B2 A2.  p: label -> stated-T2 projection of the baseline for that job (from the record pulled before it)."""
    base = {l: inst[l][(1, 1, 1)] for l in LABELS}
    # DA: drift, identical circuits, paired by instance
    d = base['A2'] - base['A1']; sA = float(d.mean()); hA = float(TQ * d.std(ddof=1) / np.sqrt(K))
    dB = base['B2'] - base['B1']; sBd = float(dB.mean()); hBd = float(TQ * dB.std(ddof=1) / np.sqrt(K))
    mu_all = {l: {s: inst[l][s].mean() for s in FACT} for l in LABELS}; cens = min(min(mu_all[l].values()) for l in LABELS) < 0.05
    # bLM drift (guard in b_LM units): bLM(A2) - bLM(A1), delta method with paired per-setting differences
    def blm_drift(l1, l2):
        v = 0.0
        for s in FACT:
            dd = inst[l2][s] - inst[l1][s]; mbar = (inst[l1][s].mean() + inst[l2][s].mean()) / 2
            v += (dd.std(ddof=1) / np.sqrt(K) / mbar) ** 2 / 64
        return blm_of(mu_all[l2]) - blm_of(mu_all[l1]), TQ * np.sqrt(v)
    bdA, hbdA = blm_drift('A1', 'A2')
    # job-averaged per instance, per set
    av = {X: {s: (inst[{'A': 'A1', 'B': 'B1'}[X]][s] + inst[{'A': 'A2', 'B': 'B2'}[X]][s]) / 2 for s in FACT} for X in 'AB'}
    a_k, b_k = av['A'][(1, 1, 1)], av['B'][(1, 1, 1)]
    seSET = float(np.sqrt(a_k.var(ddof=1) / K + b_k.var(ddof=1) / K)); hSET = TQ * seSET; sSET = float(b_k.mean() - a_k.mean())
    gSET = (abs(sA) + hA) / 2
    muX = {X: {s: av[X][s].mean() for s in FACT} for X in 'AB'}; seX = {X: {s: av[X][s].std(ddof=1) / np.sqrt(K) for s in FACT} for X in 'AB'}
    sB = blm_of(muX['B']) - blm_of(muX['A']); hB = TQ * float(np.sqrt(blm_var(seX['B'], muX['B']) + blm_var(seX['A'], muX['A']))); gB = (abs(bdA) + hbdA) / 2
    # DP: delivered baseline minus stated-T2 projection
    pA, pB = (p['A1'] + p['A2']) / 2, (p['B1'] + p['B2']) / 2
    sD = float((a_k.mean() + b_k.mean()) / 2 - (pA + pB) / 2); hD = float(TQ * 0.5 * seSET)
    return dict(DA=sA, hDA=hA, DA_outcome=outcome(sA, hA, S_SHIFT, 0.0, cens),
                B2_minus_B1=sBd, hB2B1=hBd,
                SET=sSET, hSET=float(hSET), guardSET=float(gSET), SET_outcome=outcome(sSET, hSET, S_SHIFT, gSET, cens),
                BLM=float(sB), hBLM=hB, guardBLM=float(gB), BLM_outcome=outcome(sB, hB, S_BLM, gB, cens),
                bLM_A=float(blm_of(muX['A'])), bLM_B=float(blm_of(muX['B'])), bLM_A2_minus_A1=float(bdA),
                DP=sD, hDP=hD, DP_outcome=outcome(sD, hD, S_DP, 0.0, cens),
                baseline={l: float(base[l].mean()) for l in LABELS}, censored=bool(cens))
