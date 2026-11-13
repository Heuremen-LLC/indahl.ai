"""eritrea.py -- free calibration run for the Eritrea Institute of Technology mid-circuit teleportation benchmark (V. Rai, S. Farhat; Scientific Reports 2026; Zenodo 10.5281/zenodo.20767111; ibm_fez).
Analysis and circuit builders only (fire is fire_eritrea.py). Their code was never executed; their circuits are rebuilt from circuits/full_protocol.qasm and the Methods.
Their own words: "The measured fidelity is left unconnected to device calibration. It is precisely this gap that we set out to fill."
Design: their full-protocol teleportation, 4 angles (pi/6, pi/3, pi/2, 2pi/3: sin(theta) > 0.3) x X/Y/Z tomography of q2 = 12 circuits, 8,192 shots (theirs), qubits [0,1,2], optimization_level 1 (theirs),
transpiled ONCE and sent unchanged in four jobs, order ABBA over circuit order: A1 (A order) | B1 (reversed) | B2 (reversed) | A2 (A order). The backend record is saved BEFORE every job.
Plus the Ramsey arm on the feedforward neighbour (physical q2, adjacent to q1): q0,q1 in |1>, q2 in |+>; arm R = mid-circuit readout of q0 and q1, arm I = idle of the same length; X and Y readout of q2; 4,900 shots.
MODEL (their "device-informed noise model", rebuilt exactly as an 8x8 density-matrix calculation of the same circuit pieces, no shot noise): predicted from THE RECORD SAVED BEFORE THAT JOB with BOTH conversions
  A = their convention (stated gate error passed straight in as the depolarising parameter, symmetric readout, no relaxation),  B = the correct one (lambda = 2 r one qubit, r/0.75 two qubits; r = RB average infidelity).
READINGS (fixed in advance; four outcomes each: ABOVE / BELOW / CONSISTENT / CANNOT_TELL; 99 % band; shot-noise null = same statistic on 2000 binomial redraws; signed):
  R1 LINK-A   mean over the 4 jobs of (hardware F - model F by convention A from that job's record), F = mean over the 4 angles of (1 + <X> sin + <Z> cos)/2, their definition.
  R2 LINK-B   the same with convention B.      null: hardware drawn at the MODEL's own expectations (hardware = model + shot noise).
  R3 DRIFT    F(A2) - F(A1), same circuits, same order, jobs 1 and 4.  null: both drawn at their pooled expectations.
  R4 KICK     per-readout phase of q2 from the Ramsey arm: (psi_R - psi_I)/2 degrees, psi = atan2(<Y>, <X>), two readouts (q0, q1) in arm R. null: both arms at the pooled expectations.
  Reported, not scored: per-job D_j, STEP (jobs 3,4 minus 1,2)/2, SLOT (A minus B)/2, the record stamps of the four saved records.
  RESOLVABILITY: fixed in advance from THEIR numbers, never from ours: a reading is CANNOT_TELL if its null half-width exceeds the scale.
     S_F = |their model value 0.953 - their hardware mean of the six full-protocol fidelities (0.9454 from their raw counts)| = 0.0076, for R1, R2, R3 (an F movement the size of the gap they call "reproduces");
     S_psi = |their pooled apparent Z-rotation of the received state, full protocol, computed from their raw counts (psi = atan2(<Y>,<X>), four usable angles)| = 1.79 deg, for R4.
A reading is the size of the quantity on this chip, today, for their circuit. It is not a finding about their 14 and 17 Jun runs."""
import json, sys, math, os, itertools
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
T = f'{HERE}/theirs'
ANGS = [('pi/6', math.pi / 6), ('pi/3', math.pi / 3), ('pi/2', math.pi / 2), ('2pi/3', 2 * math.pi / 3)]
ALL_ANGS = [('0', 0.0)] + ANGS + [('pi', math.pi)]
BASES = 'XYZ'
SHOTS_T, SHOTS_R = 8192, 4900
TELE = [f'tele|{a}|{b}' for a, _ in ANGS for b in BASES]
RAM = ['ram|R|X', 'ram|R|Y', 'ram|I|X', 'ram|I|Y']
A_ORDER = TELE + RAM
B_ORDER = A_ORDER[::-1]
ORDER = ['A1', 'B1', 'B2', 'A2']
THEIR_MODEL_FULL = 0.953                   # their Table 3, noise-model column, full protocol (paper)
BAND = (0.5, 99.5)                         # percentile band of the shot-noise null (ADDENDUM 1)
SIN = np.array([math.sin(t) for _, t in ANGS]); COS = np.array([math.cos(t) for _, t in ANGS])

# ---------------- circuits (qiskit imported lazily; used by fire and by the model) ----------------
def tele_circuit(theta, basis):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(3, 'q'); c0 = ClassicalRegister(1, 'c0'); c1 = ClassicalRegister(1, 'c1'); c2 = ClassicalRegister(1, 'c2')
    qc = QuantumCircuit(q, c0, c1, c2)
    qc.ry(theta, 0); qc.h(1); qc.cx(1, 2); qc.barrier()          # full protocol of their circuits/full_protocol.qasm
    qc.cx(0, 1); qc.h(0); qc.measure(0, c0); qc.measure(1, c1); qc.barrier()
    with qc.if_test((c1, 1)): qc.x(2)
    with qc.if_test((c0, 1)): qc.z(2)
    qc.barrier()
    if basis == 'X': qc.h(2)
    elif basis == 'Y': qc.sdg(2); qc.h(2)
    qc.measure(2, c2)
    return qc
def ram_circuit(arm, basis, delay_dt):
    """q0,q1 in |1>, q2 in |+>. arm R: mid-circuit readout of q0,q1; arm I: idle of delay_dt on all three. Then q2 basis rotation and a final readout of all three (identical in both arms)."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(3, 'q'); mid = ClassicalRegister(2, 'mid'); fin = ClassicalRegister(2, 'fin'); c2 = ClassicalRegister(1, 'c2')
    qc = QuantumCircuit(q, mid, fin, c2)
    qc.x(0); qc.x(1); qc.h(2); qc.barrier()
    if arm == 'R': qc.measure(0, mid[0]); qc.measure(1, mid[1])
    else: qc.delay(delay_dt, 0); qc.delay(delay_dt, 1); qc.delay(delay_dt, 2)
    qc.barrier()
    if basis == 'X': qc.h(2)
    elif basis == 'Y': qc.sdg(2); qc.h(2)
    qc.measure(0, fin[0]); qc.measure(1, fin[1]); qc.measure(2, c2)
    return qc
def circuit_for(cid, delay_dt=None):
    p = cid.split('|')
    if p[0] == 'tele': return tele_circuit(dict(ALL_ANGS)[p[1]], p[2])
    return ram_circuit(p[1], p[2], delay_dt)

# ---------------- their data, their known-good ----------------
def rhu(x, n):
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))
def ev(c):
    n0, n1 = c.get('0', 0), c.get('1', 0); return (n0 - n1) / (n0 + n1)
def load_theirs():
    return json.load(open(f'{T}/raw_data/raw_counts.json'))
def their_F(raw, mode, a, th):
    e = {b: ev(raw[f'{mode}|{a}|{b}']) for b in BASES}; return (1 + e['X'] * math.sin(th) + e['Z'] * math.cos(th)) / 2
def their_scales(raw):
    """S_F and S_psi from THEIR published numbers / raw counts (see header)."""
    fm = np.mean([their_F(raw, 'full', a, t) for a, t in ALL_ANGS]); S_F = abs(THEIR_MODEL_FULL - fm)
    num = den = 0.0
    for a, t in ALL_ANGS:
        if math.sin(t) <= 0.3: continue
        X = {b: raw[f'full|{a}|{b}'] for b in 'XY'}; x, y = ev(X['X']), ev(X['Y']); n = sum(X['X'].values())
        sx = math.sqrt(max(1e-12, 1 - x * x) / n); sy = math.sqrt(max(1e-12, 1 - y * y) / n)
        psi = math.degrees(math.atan2(y, x)); s = math.degrees(math.sqrt((x * sy) ** 2 + (y * sx) ** 2) / (x * x + y * y)); w = 1 / s ** 2; num += w * psi; den += w
    return S_F, abs(num / den), num / den
def known_good_published(raw):
    """18 published fidelities: source_data_full.csv (4 dp) and table_values.csv Table 2 (3 dp) from their raw counts, through this file."""
    import csv
    src = {(r['mode'], r['theta_label']): float(r['F']) for r in csv.DictReader(open(f'{T}/processed_data/source_data_full.csv'))}
    tv = {(r['series'], r['angle']): float(r['value']) for r in csv.DictReader(open(f'{T}/processed_data/table_values.csv')) if r['table'] == 'T2' and r['quantity'] == 'F'}
    ok4 = ok3 = 0; n = 0; lines = []
    for mode in ('full', 'no_entanglement', 'no_feedforward'):
        for a, t in ALL_ANGS:
            f4 = rhu(their_F(raw, mode, a, t), 4); f3 = rhu(f4, 3); n += 1
            ok4 += f4 == src[(mode, a)]; ok3 += f3 == tv[(mode, a)]
            if f4 != src[(mode, a)] or f3 != tv[(mode, a)]: lines.append(f'   MISMATCH {mode} {a}: mine {f4} / {f3}, published {src[(mode, a)]} / {tv[(mode, a)]}')
    mean = float(np.mean([their_F(raw, 'full', a, t) for a, t in ALL_ANGS]))
    return ok4, ok3, n, mean, lines

# ---------------- the model (exact; rebuilt from the paper's Methods and their README; their code not run) ----------------
I2 = np.eye(2); X_ = np.array([[0, 1], [1, 0]], complex); Z_ = np.diag([1, -1]).astype(complex); Y_ = np.array([[0, -1j], [1j, 0]])
SX_ = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])
def RZ(a): return np.diag([np.exp(-1j * a / 2), np.exp(1j * a / 2)])
def op1(U, k):
    m = [I2] * 3; m[k] = U; return np.kron(np.kron(m[0], m[1]), m[2])
def czm(a, b):
    d = np.ones(8, complex)
    for i in range(8):
        bits = [(i >> 2) & 1, (i >> 1) & 1, i & 1]
        if bits[a] == 1 and bits[b] == 1: d[i] = -1
    return np.diag(d)
PAULI = [np.eye(2), X_, Y_, Z_]
def full_depol(rho, qs):
    res = np.zeros_like(rho)
    for combo in itertools.product(range(4), repeat=len(qs)):
        mats = [np.eye(2)] * 3
        for k, c in zip(qs, combo): mats[k] = PAULI[c]
        U = np.kron(np.kron(mats[0], mats[1]), mats[2]); res += U @ rho @ U.conj().T
    return res / (4 ** len(qs))
def depol(rho, lam, qs): return (1 - lam) * rho + lam * full_depol(rho, qs)
_PIECES = {}
def pieces(mode, th, meas):
    key = (mode, round(th, 9), meas)
    if key not in _PIECES:
        from qiskit import QuantumCircuit, transpile
        a = QuantumCircuit(3); a.ry(th, 0)
        if mode != 'no_entanglement': a.h(1); a.cx(1, 2)
        a.cx(0, 1); a.h(0)
        b = QuantumCircuit(3)
        if meas == 'X': b.h(2)
        elif meas == 'Y': b.sdg(2); b.h(2)
        _PIECES[key] = [transpile(c, basis_gates=['rz', 'sx', 'x', 'cz'], initial_layout=[0, 1, 2], seed_transpiler=1234) for c in (a, b)]
    return _PIECES[key]
def apply_seq(rho, qc, m):
    for ins in qc.data:
        n = ins.operation.name; qs = [qc.find_bit(q).index for q in ins.qubits]
        if n == 'rz': U = op1(RZ(float(ins.operation.params[0])), qs[0]); rho = U @ rho @ U.conj().T
        elif n in ('sx', 'x'):
            U = op1(SX_ if n == 'sx' else X_, qs[0]); rho = U @ rho @ U.conj().T; rho = depol(rho, m['l1'][qs[0]], [qs[0]])
        elif n == 'cz':
            U = czm(*qs); rho = U @ rho @ U.conj().T; rho = depol(rho, m['l2'][tuple(sorted(qs))], list(qs))
        elif n == 'barrier': pass
        else: raise ValueError(n)
    return rho
def measure(rho, k, p):
    out = {0: np.zeros_like(rho), 1: np.zeros_like(rho)}
    for t in (0, 1):
        P = op1(np.diag([1 - t, t]).astype(complex), k); r = P @ rho @ P
        for rep in (0, 1): out[rep] += r * ((1 - p) if rep == t else p)
    return out
def run_model(mode, th, meas, m):
    rho = np.zeros((8, 8), complex); rho[0, 0] = 1; pa, pb = pieces(mode, th, meas); rho = apply_seq(rho, pa, m)
    P0 = P1 = 0.0
    for r1, rh1 in measure(rho, 1, m['ro'][1]).items():
        for r0, rh in measure(rh1, 0, m['ro'][0]).items():
            if mode != 'no_feedforward':
                if r1 == 1: U = op1(X_, 2); rh = U @ rh @ U.conj().T; rh = depol(rh, m['l1'][2], [2])
                if r0 == 1: U = op1(Z_, 2); rh = U @ rh @ U.conj().T
            rh = apply_seq(rh, pb, m); f = measure(rh, 2, m['ro'][2]); P0 += np.trace(f[0]).real; P1 += np.trace(f[1]).real
    return (P0 - P1) / (P0 + P1)
def stated(cal):
    """sx error, cz error, readout error of physical qubits 0,1,2 from a backend-properties dict (same layout as their main_calibration.json)."""
    def gerr(gate, qs):
        for g in cal['gates']:
            if g['gate'] == gate and tuple(g['qubits']) == tuple(qs):
                for p in g['parameters']:
                    if p['name'] == 'gate_error': return float(p['value'])
    sx = {q: gerr('sx', [q]) for q in range(3)}; cz = {(0, 1): gerr('cz', (0, 1)), (1, 2): gerr('cz', (1, 2))}
    ro = {q: float([e['value'] for e in cal['qubits'][q] if e['name'] == 'readout_error'][0]) for q in range(3)}
    return sx, cz, ro
def conv_model(cal, conv):
    sx, cz, ro = stated(cal); c1, c2 = (1.0, 1.0) if conv == 'A' else (2.0, 1 / 0.75)
    return {'l1': {q: min(1, c1 * e) for q, e in sx.items()}, 'l2': {k: min(1, c2 * e) for k, e in cz.items()}, 'ro': {q: min(.5, p) for q, p in ro.items()}}
def model_E(cal, conv, mode='full', angs=None):
    """(4 angles, 3 bases) model expectations for the record cal under convention conv."""
    angs = angs or ANGS; m = conv_model(cal, conv)
    return np.array([[run_model(mode, t, b, m) for b in BASES] for _, t in angs])
def known_good_model(cal):
    """their model value by their convention (A) from their own stamp, six angles, three modes; ours vs their Table 3 (0.953 / 0.752 / 0.496)."""
    out = {}
    for mode in ('full', 'no_entanglement', 'no_feedforward'):
        E = model_E(cal, 'A', mode, ALL_ANGS); s = np.array([math.sin(t) for _, t in ALL_ANGS]); c = np.array([math.cos(t) for _, t in ALL_ANGS])
        out[mode] = float(np.mean((1 + E[:, 0] * s + E[:, 2] * c) / 2))
    return out

# ---------------- statistics ----------------
def Fa(E):
    """E (..., 4 angles, 3 bases) expectations -> mean over angles of (1 + <X> sin + <Z> cos)/2."""
    return ((1 + E[..., :, 0] * SIN + E[..., :, 2] * COS) / 2).mean(axis=-1)
def drawE(E, B, rng, shots):
    return 2 * rng.binomial(shots, np.clip((1 + np.broadcast_to(E, (B,) + E.shape)) / 2, 0, 1)) / shots - 1
def psi_deg(E):
    return np.degrees(np.arctan2(E[..., 1], E[..., 0]))
def four(v, nlo, nhi, resolvable):
    if not resolvable: return 'CANNOT_TELL'
    return 'ABOVE' if v > nhi else 'BELOW' if v < nlo else 'CONSISTENT'
def analyse(Jt, Jr, mods, scales, rng, B=2000, shots_t=SHOTS_T, shots_r=SHOTS_R, Bint=500):
    """Jt (4 jobs, 4 angles, 3 bases) counts of outcome 0; Jr (4 jobs, 2 arms [R,I], 2 bases [X,Y]) counts of 0; mods {'A': (4,4,3), 'B': (4,4,3)} model expectations per job from that job's record.
    Returns (lines, results dict name -> (value, lo, hi, nlo, nhi, outcome))."""
    S_F, S_psi = scales
    Eh = 2 * Jt / shots_t - 1; Fh = Fa(Eh); res = {}
    def put(name, v, bsamp, nsamp, scale, unit):
        b = bsamp + (v - np.median(bsamp)); lo, hi = np.percentile(b, [2.5, 97.5]); nlo, nhi = np.percentile(nsamp, list(BAND))
        ok = (nhi - nlo) / 2 < scale; res[name] = (float(v), float(lo), float(hi), float(nlo), float(nhi), four(v, nlo, nhi, ok))
    for conv, nm in (('A', 'R1 LINK-A (hw F - model F, their convention)'), ('B', 'R2 LINK-B (hw F - model F, converted)')):
        Em = mods[conv]; Fm = Fa(Em); v = np.mean(Fh - Fm)
        put(nm, v, (Fa(drawE(Eh, Bint, rng, shots_t)) - Fm).mean(axis=-1), (Fa(drawE(Em, B, rng, shots_t)) - Fm).mean(axis=-1), S_F, 'F')
    Ep = (Eh[0] + Eh[3]) / 2
    put('R3 DRIFT (F(A2) - F(A1))', Fh[3] - Fh[0], Fa(drawE(Eh[3], Bint, rng, shots_t)) - Fa(drawE(Eh[0], Bint, rng, shots_t)),
        Fa(drawE(Ep, B, rng, shots_t)) - Fa(drawE(Ep, B, rng, shots_t)), S_F, 'F')
    Ek = 2 * Jr.sum(axis=0) / (4 * shots_r) - 1                          # (2 arms, 2 bases), pooled over the four jobs
    kick = lambda E: (psi_deg(E[..., 0, :]) - psi_deg(E[..., 1, :])) / 2
    Epool = Ek.mean(axis=0)
    put('R4 KICK (deg per readout, (psi_R - psi_I)/2)', kick(Ek), kick(drawE(Ek, Bint, rng, 4 * shots_r)), kick(np.stack([drawE(Epool, B, rng, 4 * shots_r), drawE(Epool, B, rng, 4 * shots_r)], axis=1)), S_psi, 'deg')
    # reported, not scored
    Ea = Eh.mean(axis=0); step = lambda F: (F[..., 2] + F[..., 3] - F[..., 0] - F[..., 1]) / 2; slot = lambda F: (F[..., 0] + F[..., 3] - F[..., 1] - F[..., 2]) / 2
    for nm, fn in (('STEP (F jobs 3,4 minus 1,2)/2', step), ('SLOT (F A minus B)/2', slot)):
        put(nm, fn(Fh), fn(Fa(drawE(Eh, Bint, rng, shots_t))), fn(Fa(drawE(np.broadcast_to(Ea, (4,) + Ea.shape), B, rng, shots_t))), S_F, 'F')
    lines = []
    for k, (v, lo, hi, nlo, nhi, o) in res.items():
        sc = S_psi if k.startswith('R4') else S_F; u = 'deg' if k.startswith('R4') else ''
        lines.append(f'{k:52s} = {v:+.5f} [{lo:+.5f}, {hi:+.5f}] {u} shot-null [{nlo:+.5f}, {nhi:+.5f}] their scale {sc:.4f} -> {o}{"  [reported, not scored]" if not k[:2] in ("R1", "R2", "R3", "R4") else ""}')
    for j, lab in enumerate(ORDER):
        lines.append(f'  job {lab}: hardware F {Fh[j]:.5f}   model A {Fa(mods["A"][j]):.5f}   model B {Fa(mods["B"][j]):.5f}   D_A {Fh[j] - Fa(mods["A"][j]):+.5f}   D_B {Fh[j] - Fa(mods["B"][j]):+.5f}')
    return lines, res

def record_models(cals):
    """cals: 4 backend-properties dicts (the record saved before A1, B1, B2, A2) -> {'A': (4,4,3), 'B': (4,4,3)}."""
    return {c: np.array([model_E(cal, c) for cal in cals]) for c in ('A', 'B')}
def record_stamps(cals):
    out = []
    for cal in cals:
        sx, cz, ro = stated(cal); out.append(f"stamp {cal.get('last_update_date')}: sx {[round(sx[q], 5) for q in range(3)]} cz01 {cz[(0, 1)]:.4f} cz12 {cz[(1, 2)]:.4f} ro {[round(ro[q], 4) for q in range(3)]}")
    return out

if __name__ == '__main__':
    raw = load_theirs(); ok4, ok3, n, mean, bad = known_good_published(raw); S_F, S_psi, psi = their_scales(raw)
    cal = json.load(open(f'{T}/raw_data/main_calibration.json')); mod = known_good_model(cal)
    d = abs(mod['full'] - THEIR_MODEL_FULL)
    print(f'R0 KNOWN-GOOD (A) their 18 published fidelities from their raw counts through this file: {ok4}/{n} equal at 4 decimals (source_data_full.csv), {ok3}/{n} equal at 3 decimals (Table 2); mean full protocol {mean:.4f} (published 0.9454 / 0.945) -> {"PASS" if ok4 == n and ok3 == n and rhu(mean, 4) == 0.9454 else "FAIL"}')
    for l in bad: print(l)
    print(f'R0 KNOWN-GOOD (B) their model value by their convention (A) from their own 14 Jun stamp, exact density matrix: full {mod["full"]:.4f} vs their Table 3 {THEIR_MODEL_FULL} (|diff| {d:.4f}); no-ent {mod["no_entanglement"]:.4f} vs 0.752; no-ff {mod["no_feedforward"]:.4f} vs 0.496; '
          f'rule fixed before any job: |diff| <= 0.005, their README: "version-dependent to ~0.005" (theirs is a shot-noise qiskit-aer draw, ours is exact) -> {"PASS" if d <= 0.005 else "FAIL"}')
    print(f'SCALES from their numbers: S_F = |{THEIR_MODEL_FULL} - {mean:.4f}| = {S_F:.4f}; S_psi = |pooled apparent Z-rotation of their full-protocol received state| = {S_psi:.2f} deg (signed {psi:+.2f})')
    if len(sys.argv) > 1 and sys.argv[1] == '--real':
        rec = json.load(open(f'{HERE}/job_eritrea.json')); rng = np.random.default_rng(24); J = {}; cals = []
        for lab in ORDER:
            raw_j = json.load(open(f'{HERE}/raw_eritrea_{lab}.json')); J[lab] = raw_j
            cals.append(json.load(open(f'{HERE}/props_eritrea_before_{lab}.json')))
        n0 = lambda c, cid: c[cid].get('0', 0)
        Jt = np.array([[[n0(J[l], f'tele|{a}|{b}') for b in BASES] for a, _ in ANGS] for l in ORDER])
        Jr = np.array([[[n0(J[l], f'ram|{arm}|{b}') for b in 'XY'] for arm in 'RI'] for l in ORDER])
        print('\n'.join(record_stamps(cals)))
        lines, r1 = analyse(Jt, Jr, record_models(cals), (S_F, S_psi), rng); print('\n'.join(lines))
        for j, lab in enumerate(ORDER):                                                                  # kick per job (the four jobs are the units, /q 22): reported, not scored
            Ej = 2 * Jr[j] / SHOTS_R - 1; print(f'  job {lab}: kick {(psi_deg(Ej[0]) - psi_deg(Ej[1])) / 2:+.3f} deg per readout')
        nxt = cals[1:] + [json.load(open(f'{HERE}/props_eritrea_after.json'))]                           # record bracket (/q 3): the same readings with the NEXT saved record in place of each job's own
        print('RECORD BRACKET (each job modelled from the record saved AFTER it instead of BEFORE it):'); lines2, r2 = analyse(Jt, Jr, record_models(nxt), (S_F, S_psi), rng); print('\n'.join(lines2[:2]))
        for k in list(r1)[:2]: print(f'   {k.split(" (")[0]}: before-record {r1[k][5]}, after-record {r2[k][5]} -> {"same" if r1[k][5] == r2[k][5] else "DIFFERENT: read as CANNOT_TELL as to the record"}')
