"""hebrew.py -- circuits and readings for the Hebrew University run (arXiv 2506.11270v2, Santos & Uzdin), ibm_fez, 24 Oct 2026.
Their claim (Fig. 1): spectators given an equal delay during repeated mid-circuit readouts are 'automatically mitigated'. Their checks are
computational-basis fidelities. This run reads the untouched neighbours of their printed 20-qubit fez set (qubits 0-19) in a PHASE basis.
Arms per round count N in {1,3,5,7,13}: M = the 20 qubits measured N times; D = the 20 idle for N x the measure duration; MD = measure then a
short delay (their 'short delay between the measurements' idea); DD = idle for N x (measure + delay). Neighbours (within two couplings) in |+>,
read in X or Y; state-check qubits (distance 3) in |1>, read in Z. KNOWN-GOOD arm KG: the committed 21 Oct fez 39-qubit pack E measured 8 times
vs idle, its 117 untouched S qubits in |+>, read XX / YY (the committed control-run design, same convention)."""
import json, os
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister
H = os.path.expanduser('<local>')
M20 = list(range(20))                                   # their printed ibm_fez 20-qubit set
NB = [23, 27, 31, 35, 22, 24, 26, 28, 30, 32, 34]       # untouched, within two couplings of M20 (coupling map, 24 Oct)
ONE = [21, 25, 29, 33]                                  # distance 3, prepared |1>, read Z (state check)
NS = [1, 3, 5, 7, 13]; ARMS = ['M', 'D', 'MD', 'DD']; SETS = ['X', 'Y']
LM = 415                                                # measure duration on fez, dt (= committed control-run L)
LG = 250                                                # inter-round delay for MD/DD, dt = 1.0 us
SHOTS = 6000
CTRL = json.load(open(H + '/arxiv_one_readout/control_run/job_ibm_fez.json')); E39, S117 = CTRL['E'], CTRL['S']
BAND = 99.0; S_KICK = 0.25; S_COH = 0.002               # scales fixed 24 Oct before any job: 0.25 deg/readout = what 11 neighbours x 6000 shots resolve (synthetic null ~+-0.1-0.2); coherence 0.002/readout

def rot(qc, q, b):
    if b == 'X': qc.h(q)
    elif b == 'Y': qc.sdg(q); qc.h(q)

def circuit(arm, N, setting, n=156):
    qc = QuantumCircuit(n); mid = ClassicalRegister(len(M20), 'mid'); fin = ClassicalRegister(len(NB) + len(ONE), 'fin')
    qc.add_register(mid); qc.add_register(fin)
    for q in NB: qc.h(q)
    for q in ONE: qc.x(q)
    qc.barrier()
    for _ in range(N):
        if arm in ('M', 'MD'): qc.measure(M20, mid)
        else: qc.delay(LM, M20, unit='dt')
        if arm in ('MD', 'DD'): qc.delay(LG, M20, unit='dt')
        qc.barrier()
    for q in NB: rot(qc, q, setting)
    qc.measure(NB + ONE, list(fin))
    return qc

def kg_circuit(arm, setting, n=156, N=8):
    qc = QuantumCircuit(n); mid = ClassicalRegister(len(E39), 'mid'); fin = ClassicalRegister(len(S117), 'fin')
    qc.add_register(mid); qc.add_register(fin)
    for q in S117: qc.h(q)
    qc.barrier()
    for _ in range(N):
        if arm == 'M': qc.measure(E39, mid)
        else: qc.delay(LM, E39, unit='dt')
        qc.barrier()
    for q in S117: rot(qc, q, setting)
    qc.measure(S117, list(fin)); return qc

def build():
    circs, meta = [], []
    for arm in ARMS:
        for N in NS:
            for st in SETS: circs.append(circuit(arm, N, st)); meta.append(dict(kind='main', arm=arm, N=N, setting=st))
    for arm in ('M', 'D'):
        for st in SETS: circs.append(kg_circuit(arm, st)); meta.append(dict(kind='kg', arm=arm, N=8, setting=st))
    return circs, meta

# ------------------------------------------------------------------ analysis (bits[i] = bool array shots x nbits, little-endian fin order)
wrap = lambda a: (a + np.pi) % (2 * np.pi) - np.pi
def outcome(lo, hi, S):
    if lo > 0: return 'ABOVE'
    if hi < 0: return 'BELOW'
    if -S <= lo and hi <= S: return 'CONSISTENT'
    return 'CANNOT_TELL'
def boot_median(v, rng, B=4000):
    v = np.asarray(v); bs = [np.median(rng.choice(v, len(v))) for _ in range(B)]; a = (100 - BAND) / 2
    return float(np.median(v)), float(np.percentile(bs, a)), float(np.percentile(bs, 100 - a))
def expv(meta, bits, sel, nq, kind='main'):
    arrs = [bits[i] for i, m in enumerate(meta) if m['kind'] == kind and all(m[k] == v for k, v in sel.items())]
    a = np.concatenate(arrs); return np.array([(1 - 2 * a[:, k]).mean() for k in range(nq)])
def phase(meta, bits, arm, N, nq, kind='main'):
    x = expv(meta, bits, dict(arm=arm, N=N, setting='X'), nq, kind); y = expv(meta, bits, dict(arm=arm, N=N, setting='Y'), nq, kind)
    return np.arctan2(y, x), np.hypot(x, y)
def slopes(meta, bits, a, b):
    """per neighbour: least-squares slope through the origin of wrap(phi_a - phi_b) in deg vs N, and of ln(r_a/r_b) vs N"""
    d = np.array([np.degrees(wrap(phase(meta, bits, a, N, len(NB))[0] - phase(meta, bits, b, N, len(NB))[0])) for N in NS])   # NS x NB
    c = np.array([np.log(phase(meta, bits, a, N, len(NB))[1] / phase(meta, bits, b, N, len(NB))[1]) for N in NS])
    n = np.array(NS, float)[:, None]; den = float((n ** 2).sum())
    return (n * d).sum(0) / den, (n * c).sum(0) / den, d
def readings(meta, bits, rng):
    kM, cM, dM = slopes(meta, bits, 'M', 'D'); kG, cG, dG = slopes(meta, bits, 'MD', 'DD')
    r = {}
    for name, v, S in (('R1 kick M-D (deg/readout)', kM, S_KICK), ('R2 kick MD-DD (deg/readout)', kG, S_KICK),
                       ('R2b delay effect (R1-R2 per neighbour)', kM - kG, S_KICK), ('R3 coherence ln(rM/rD) per readout', cM, S_COH),
                       ('R3b coherence with delay', cG, S_COH)):
        m, lo, hi = boot_median(v, rng); r[name] = (m, lo, hi, outcome(lo, hi, S))
    r['_profile_M_D_deg'] = np.median(dM, axis=1).round(3).tolist(); r['_profile_MD_DD_deg'] = np.median(dG, axis=1).round(3).tolist()
    r['_state_check_P1_at_N13'] = {arm: round(float(np.mean([(1 - expv(meta, bits, dict(arm=arm, N=13, setting=s), len(NB) + len(ONE))[len(NB):]) / 2
                                                            for s in SETS])), 4) for arm in ARMS}
    return r
def kg_reading(meta, bits, rng):
    pM, _ = phase(meta, bits, 'M', 8, len(S117), 'kg'); pD, _ = phase(meta, bits, 'D', 8, len(S117), 'kg')
    k = np.degrees(wrap(pM - pD)) / 8; m, lo, hi = boot_median(k, rng)
    ok = (-3.24 <= m <= -0.81) and hi < 0
    return dict(median=m, lo=lo, hi=hi, PASS=ok)
