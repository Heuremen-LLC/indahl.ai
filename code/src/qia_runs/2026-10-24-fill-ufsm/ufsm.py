"""ufsm.py -- free run for arXiv 2502.01824v3 (Brasil, Starke, Maziero; Federal University of Santa Maria, Brazil), ibm_kingston.
Their Fig 8(a) (no blocker) and 8(b) (measure+reset 'blocker' on mode B after the first beam splitter), rebuilt from their published
construction (XX(t): H H, CX, RZ(-2t), CX, H H; YY(t): Sdg Sdg H H, CX, RZ(-2t), CX, H H, S S; BS = XX(pi/8) YY(pi/8); M = XX(pi/4) YY(pi/4);
uA = X(0) BS M P(pi/2,0) BS M BS, measure; uB = X(0) BS, measure q1 -> c0, reset q1, M P(pi/2,0) BS M BS, measure q0 -> c1, q1 -> c2).
Ideal: (a) '01' and '10' 0.5 each; (b) '001' and '100' 0.5 each (qiskit key order c2 c1 c0).
Their question: the ideal-outcome deficit grows with each measure+reset (their data: (a) 1.24 pp, (b) 4.67 pp, extra 3.43 pp) and is it
the extra readout or more. Plus a 4-state readout bracket on the same two qubits (|00>,|01>,|10>,|11>) so the readout share is OURS."""
import numpy as np
from qiskit import QuantumCircuit
SHOTS = 8192; Z99 = 2.5758; SPREAD_P = 0.005   # instance-spread gate: chi-square across the 4 same-circuit instances, either config, p < 0.005
THEIRS = dict(def_a=0.012451, def_b=0.046729)      # their notebook counts through this code (known_good_ufsm.text), fractions
def XX(qc, t): qc.h([0, 1]); qc.cx(0, 1); qc.rz(-2 * t, 1); qc.cx(0, 1); qc.h([0, 1])
def YY(qc, t): qc.sdg([0, 1]); qc.h([0, 1]); qc.cx(0, 1); qc.rz(-2 * t, 1); qc.cx(0, 1); qc.h([0, 1]); qc.s([0, 1])
def BS(qc): XX(qc, np.pi / 8); YY(qc, np.pi / 8)
def MI(qc): XX(qc, np.pi / 4); YY(qc, np.pi / 4)
def uA():
    qc = QuantumCircuit(2, 2); qc.x(0); BS(qc); MI(qc); qc.p(np.pi / 2, 0); BS(qc); MI(qc); BS(qc); qc.measure([0, 1], [0, 1]); return qc
def uB():
    qc = QuantumCircuit(2, 3); qc.x(0); BS(qc); qc.measure(1, 0); qc.reset(1); MI(qc); qc.p(np.pi / 2, 0); BS(qc); MI(qc); BS(qc)
    qc.measure([0, 1], [1, 2]); return qc
def bracket(s):
    qc = QuantumCircuit(2, 2)
    if s[1] == '1': qc.x(0)
    if s[0] == '1': qc.x(1)
    qc.measure([0, 1], [0, 1]); return qc
BR = ('00', '01', '10', '11')
def plan(copy):
    """copy 1: brackets, a b b a; copy 2: b a a b, brackets (ABBA across the two jobs)"""
    if copy == 1: return [('br', s) for s in BR] + [('a', 0), ('b', 0), ('b', 1), ('a', 1)]
    return [('b', 2), ('a', 2), ('a', 3), ('b', 3)] + [('br', s) for s in BR]
def circuits(copy): return [uA() if k == 'a' else uB() if k == 'b' else bracket(l) for k, l in plan(copy)]
IDEAL = {'a': ('01', '10'), 'b': ('001', '100')}
def deficit(c, kind):
    n = sum(c.values()); return 1 - sum(c.get(k, 0) for k in IDEAL[kind]) / n, n
def flips(br):
    """per-qubit flip probabilities from the bracket: e[q][v] = P(read not-v | prepared v) for qubit q (q0 = c0 bit, q1 = c1 bit)"""
    e = {0: {}, 1: {}}
    for q in (0, 1):
        for v in '01':
            ok = n = 0
            for s in BR:
                if s[1 - q] != v: continue
                c = br[s]; n += sum(c.values()); ok += sum(cnt for b, cnt in c.items() if b[-1 - q] == v)
            e[q][v] = 1 - ok / n
    return e
def ro_deficit(e, kind):
    """readout-only deficit predicted from the bracket flips (independent flips; the mid-circuit read of q1 is given q1's terminal flips --
    an approximation, labelled in the plan)."""
    if kind == 'a':  # ideal 01 (q0=1,q1=0) and 10 (q0=0,q1=1)
        p01 = (1 - e[0]['1']) * (1 - e[1]['0']); p10 = (1 - e[0]['0']) * (1 - e[1]['1']); return 1 - (p01 + p10) / 2
    # (b): ideal 001 = (c0 mid q1 = 1, final q0 = 0, final q1 = 0); 100 = (mid q1 = 0, final q0 = 0, final q1 = 1)
    p001 = (1 - e[1]['1']) * (1 - e[0]['0']) * (1 - e[1]['0']); p100 = (1 - e[1]['0']) * (1 - e[0]['0']) * (1 - e[1]['1']); return 1 - (p001 + p100) / 2
def pool(entries, kind):
    out = {}
    for k, l, c in entries:
        if k == kind:
            for b, v in c.items(): out[b] = out.get(b, 0) + v
    return out
def readings(entries):
    a, b = pool(entries, 'a'), pool(entries, 'b'); br = {}
    for k, l, c in entries:
        if k == 'br':
            br.setdefault(l, {})
            for x, v in c.items(): br[l][x] = br[l].get(x, 0) + v
    da, na = deficit(a, 'a'); db, nb = deficit(b, 'b'); e = flips(br)
    D = db - da; Dc = D - (ro_deficit(e, 'b') - ro_deficit(e, 'a'))
    # instance spread: per-circuit deficits vs binomial
    from scipy.stats import chi2 as _chi2
    chis = []; pmin = 1.0
    for kind in ('a', 'b'):
        ds = [deficit(c, kind) for k, l, c in entries if k == kind]
        if len(ds) > 1:
            m = np.mean([d for d, n in ds]); var = m * (1 - m) / ds[0][1]; x2 = sum((d - m) ** 2 for d, n in ds) / var
            chis.append(np.var([d for d, n in ds], ddof=1) / var); pmin = min(pmin, float(_chi2.sf(x2, len(ds) - 1)))
    ratio = float(np.sqrt(max(chis))) if chis else float('nan')
    return dict(def_a=da, def_b=db, D=D, Dc=Dc, ro_a=ro_deficit(e, 'a'), ro_b=ro_deficit(e, 'b'), flips=e, spread_ratio=ratio, spread_p=pmin,
                asym_a=(a.get('01', 0) - a.get('10', 0)) / na)
def analyze(entries, nboot=300, seed=11):
    r = readings(entries); rng = np.random.default_rng(seed); bD = []; bDc = []
    for _ in range(nboot):
        ent = []
        for k, l, c in entries:
            ks = list(c); p = np.array([c[x] for x in ks], float); n = int(p.sum()); d = rng.multinomial(n, p / n); ent.append((k, l, dict(zip(ks, d))))
        rb = readings(ent); bD.append(rb['D']); bDc.append(rb['Dc'])
    sD, sDc = np.std(bD, ddof=1), np.std(bDc, ddof=1); r['sD'], r['sDc'] = sD, sDc
    theirs = THEIRS['def_b'] - THEIRS['def_a']; sT = float(np.sqrt(sum(d * (1 - d) / 40960 for d in THEIRS.values())))   # their pooled 5 x 8192-shot binomial sd
    def four(v, s, gate):
        if gate: return 'CANNOT_TELL'
        return 'ABOVE' if v - Z99 * s > 0 else 'BELOW' if v + Z99 * s < 0 else 'CONSISTENT'
    gate = not (r['spread_p'] >= SPREAD_P)
    r['R1'] = four(r['D'] - theirs, np.hypot(sD, sT), gate); r['R1_theirs'] = theirs
    r['R2'] = four(r['Dc'], sDc, gate)
    return r
