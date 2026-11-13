"""marmara.py -- free run for arXiv 2512.14280v3 (Saba Arife Bozpolat, Physics Department, Marmara University, Istanbul), ibm_fez, n = 6.
Construction (their Eq. 1 and Algorithm 1): U = prod_{k=1}^{n-1} CX(0->k) H(0); encode message b = b_{n-1}..b_0 on the sender's qubits
q0..q_{n-2}: Z(q0) if b0; X(q0) if b_{n-1}; for i = 1..n-2: X(q_i) if b_i, X(q_i) if b_{n-1} (repeated X cancel); decode U^dagger, measure
q_k -> c_k. Ideal: the read-out bitstring (qiskit key c_{n-1}..c_0) equals the message. Plus a readout bracket (all |0>, all |1>) on the
same six qubits. Readings use mutual information I(M; M^) with a uniform message prior; shortfall = n - I (bits); classical bound n - 1."""
import numpy as np
from qiskit import QuantumCircuit
N = 6; SHOTS = 1024; Z99 = 2.5758   # 4 jobs x 1024: arms DD OFF / DD ON, order OFF ON ON OFF; each arm pools 2048 shots per message
THEIRS = dict(raw=1.279, mit=0.701)          # their Zenodo counts through this code (known_good_marmara.text)
def circ_fanout(msg, n=N):
    """their U exactly (fan-out CX 0->k); used only to check the protocol in simulation"""
    b = [int(c) for c in reversed(msg)]
    qc = QuantumCircuit(n, n); qc.h(0)
    for k in range(1, n): qc.cx(0, k)
    if b[0]: qc.z(0)
    if b[n - 1]: qc.x(0)
    for i in range(1, n - 1):
        if b[i] ^ b[n - 1]: qc.x(i)
    qc.barrier()
    for k in range(n - 1, 0, -1): qc.cx(0, k)
    qc.h(0); qc.measure(range(n), range(n)); return qc
def circ_chain(msg, n=N):
    """NOT RUN (kept as a record of the alternative considered): the same resource state |G0> = U|0> prepared by a nearest-neighbour CX chain (H0, CX 0-1, 1-2, ..., (n-2)-(n-1)),
    their Algorithm 1 encoding unchanged, a barrier (their stats record one), then the inverse chain and H0. The decode reads a fixed
    bijection of the message (RELABEL, built in simulation); mutual information is invariant under it. Reason: on qubits 0..5 of fez
    (a line) the fan-out routes to 21 CZ for 000000 vs their recorded 12; the chain is 10."""
    b = [int(c) for c in reversed(msg)]
    qc = QuantumCircuit(n, n); qc.h(0)
    for k in range(1, n): qc.cx(k - 1, k)
    if b[0]: qc.z(0)
    if b[n - 1]: qc.x(0)
    for i in range(1, n - 1):
        if b[i] ^ b[n - 1]: qc.x(i)
    qc.barrier()
    for k in range(n - 1, 0, -1): qc.cx(k - 1, k)
    qc.h(0); qc.measure(range(n), range(n)); return qc
RELABEL = {}   # identity: what we run is their fan-out U (circ = circ_fanout), whose ideal outcome IS the message
circ = circ_fanout   # their exact construction + a barrier between encode and decode (their stats record one barrier)
def build_relabel():
    from qiskit.quantum_info import Statevector
    out = {}
    for m in [format(x, f'0{N}b') for x in range(2 ** N)]:
        c = circ_chain(m).remove_final_measurements(inplace=False); p = Statevector(c).probabilities_dict()
        k = max(p, key=p.get); assert p[k] > 1 - 1e-9, (m, p); out[k] = m
    assert len(out) == 2 ** N; return out
def bracket(v, n=N):
    qc = QuantumCircuit(n, n)
    if v: qc.x(range(n))
    qc.measure(range(n), range(n)); return qc
MSGS = [format(m, f'0{N}b') for m in range(2 ** N)]
JOBS = [('J1', 'off'), ('J2', 'on'), ('J3', 'on'), ('J4', 'off')]
def plan(job):
    body = [('m', m) for m in MSGS]
    if job in ('J2', 'J4'): body = body[::-1]
    return [('br', '0'), ('br', '1')] + body + [('br', '0'), ('br', '1')]
def circuits(job): return [circ(l) if k == 'm' else bracket(int(l)) for k, l in plan(job)]
def mi(cond):
    """cond: dict msg -> dict outcome -> weight (counts or probabilities). Uniform prior over msgs. Returns I(M;M^) in bits."""
    msgs = list(cond); pm = 1 / len(msgs); pout = {}; joint = []
    for m in msgs:
        c = cond[m]; t = sum(c.values())
        for o, v in c.items():
            if v <= 0: continue
            p = pm * v / t; joint.append((m, o, p)); pout[o] = pout.get(o, 0) + p
    return sum(p * np.log2(p / (pm * pout[o])) for m, o, p in joint)
def flips(br):
    """per-qubit P(read 1 | all |0>) and P(read 0 | all |1>) from the bracket counts"""
    e0 = np.zeros(N); e1 = np.zeros(N); n0 = sum(br['0'].values()); n1 = sum(br['1'].values())
    for s, v in br['0'].items():
        for q in range(N): e0[q] += v * (s[-1 - q] == '1')
    for s, v in br['1'].items():
        for q in range(N): e1[q] += v * (s[-1 - q] == '0')
    return e0 / n0, e1 / n1
def mitigate(counts, e0, e1):
    """tensor-product inversion of per-qubit 2x2 confusion matrices, then clip negatives and renormalise (stated method)."""
    p = np.zeros(2 ** N); tot = sum(counts.values())
    for s, v in counts.items(): p[int(s, 2)] += v / tot
    p = p.reshape([2] * N)   # axis 0 = bit N-1 ... axis N-1 = bit 0
    for q in range(N):
        A = np.array([[1 - e0[q], e1[q]], [e0[q], 1 - e1[q]]]); Ai = np.linalg.inv(A); ax = N - 1 - q
        p = np.moveaxis(np.tensordot(Ai, np.moveaxis(p, ax, 0), axes=1), 0, ax)
    p = np.clip(p.reshape(-1), 0, None); p /= p.sum()
    return {format(i, f'0{N}b'): float(v) for i, v in enumerate(p) if v > 0}
def pool(entries, relabel=None):
    """message circuits' outcomes are mapped through the bijection (relabel) so that the ideal outcome of message m is m"""
    cond = {}; br = {'0': {}, '1': {}}
    for k, l, c in entries:
        tgt = cond.setdefault(l, {}) if k == 'm' else br[l]
        for s, v in c.items():
            s2 = (relabel or RELABEL).get(s, s) if k == 'm' else s
            tgt[s2] = tgt.get(s2, 0) + v
    return cond, br
def readings(entries, relabel=None):
    cond, br = pool(entries, relabel={}); e0, e1 = flips(br)        # raw outcome labels (mitigation acts on physical bits)
    rl = RELABEL if relabel is None else relabel
    re = lambda d: {rl.get(s, s): v for s, v in d.items()}
    raw = N - mi(cond); mit = N - mi({m: mitigate(c, e0, e1) for m, c in cond.items()})   # MI invariant under the bijection
    cond = {m: re(c) for m, c in cond.items()}
    succ = np.mean([cond[m].get(m, 0) / sum(cond[m].values()) for m in cond])
    return dict(raw=raw, mit=mit, succ=succ, e0=e0.tolist(), e1=e1.tolist())
def _boot(ents, rng):
    out = []
    for k, l, c in ents:
        ks = list(c); p = np.array([c[x] for x in ks], float); n = int(p.sum()); out.append((k, l, dict(zip(ks, rng.multinomial(n, p / n)))))
    return out
def four(v, s, ref, gate=False):
    if gate: return 'CANNOT_TELL'
    return 'ABOVE' if v - Z99 * s > ref else 'BELOW' if v + Z99 * s < ref else 'CONSISTENT'
def analyze_arm(ja, jb, nboot=150, seed=5):
    """two jobs of one arm. Gate: their raw shortfalls disagree beyond 99 % (each job's own bootstrap sd)."""
    rng = np.random.default_rng(seed); r = readings(ja + jb); ra = readings(ja); rb = readings(jb)
    B = [readings(_boot(ja, rng) + _boot(jb, rng)) for _ in range(nboot)]
    Ba = [readings(_boot(ja, rng))['raw'] for _ in range(max(40, nboot // 3))]; Bb = [readings(_boot(jb, rng))['raw'] for _ in range(max(40, nboot // 3))]
    sraw = np.std([b['raw'] for b in B], ddof=1); smit = np.std([b['mit'] for b in B], ddof=1)
    # bootstrap bias correction (fixed before any job, after the first synthetic showed EDGE reading ABOVE 10-17 %): theta_bc = 2 theta - mean(theta*)
    r['raw_plugin'], r['mit_plugin'] = r['raw'], r['mit']
    r['raw'] = 2 * r['raw'] - np.mean([b['raw'] for b in B]); r['mit'] = 2 * r['mit'] - np.mean([b['mit'] for b in B])
    ra = dict(ra, raw=2 * ra['raw'] - np.mean(Ba)); rb = dict(rb, raw=2 * rb['raw'] - np.mean(Bb))
    gap = ra['raw'] - rb['raw']; sgap = np.hypot(np.std(Ba, ddof=1), np.std(Bb, ddof=1)); gate = abs(gap) > Z99 * sgap
    r.update(sraw=sraw, smit=smit, copy_gap=gap, sgap=sgap, gate=bool(gate), R_mit=four(r['mit'], smit, 1.0, gate), R_raw=four(r['raw'], sraw, 1.0, gate),
             R_vs_theirs_raw=four(r['raw'] - THEIRS['raw'], sraw, 0.0, gate), mit_boot=[b['mit'] for b in B])
    return r
def analyze(jobs):
    """jobs: dict J1..J4 -> entries"""
    off = analyze_arm(jobs['J1'], jobs['J4'], seed=5); on = analyze_arm(jobs['J2'], jobs['J3'], seed=6)
    d = on['mit'] - off['mit']; sd = np.hypot(on['smit'], off['smit'])
    return dict(off=off, on=on, R4=four(d, sd, 0.0, off['gate'] or on['gate']), R4_value=d, R4_sd=sd)
