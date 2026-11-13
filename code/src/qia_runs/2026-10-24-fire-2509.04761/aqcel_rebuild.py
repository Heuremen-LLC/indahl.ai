"""aqcel_rebuild.py -- OUR rebuild (not their code) of the 1-step QPS circuit of arXiv 2509.04761v4 and of the Aqcel-v1 / Aqcel-v2 passes.
Built from: the paper's text (Sec. 2, 3.1, 3.2, 4.1) and from READING (never running) their released generator sample/onestepSim_LBNL.py and
the Aqcel library (tag v2.0.0 for v2, tag v1 for v1). Differences from theirs, stated:
  * control-qubit state 'measurements' use the EXACT probabilities of the current optimized prefix (statevector), not 100k sampled shots on
    hardware or Aer; so no shot/hardware noise enters the optimisation (paper Fig. 4 says theirs fluctuates for v1 at low threshold).
  * v2 = v1 removal + CX-pair removal under the paper's three sufficient conditions (Sec. 3.2), certified on the exact prefix state; the
    label manager's only role with exact probabilities is to skip measurements, which cannot change a removal decision except where labels
    are MORE conservative than the measurement; we do not emulate that (stated as a difference; the known-good counts test it).
QPS 1-step parameters as released: eps 0.001, gL 2, gR 1, gLR (g12) 1, dophisplit 1; registers p0(3) p1(3) h1 e phi a b; measure p0,p1."""
import math
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import RYGate, XGate, CXGate, RCCXGate, CCXGate
from qiskit.quantum_info import Statevector

EPS, GL, GR, GLR = 0.001, 2.0, 1.0, 1.0


def qps1(measure=True):
    gp = math.sqrt(abs((GL - GR) ** 2 + 4 * GLR * GLR))
    if GL > GR:
        gp = -gp
    gA, gB = (GL + GR - gp) / 2, (GL + GR + gp) / 2
    qS = math.sqrt(abs((gp + GL - GR) / (2 * gp)))
    Delta_f = lambda t, g: math.exp(g ** 2 * math.log(t) / (4 * math.pi))
    p0, p1 = QuantumRegister(3, 'p0'), QuantumRegister(3, 'p1')
    h1, e, phi, a, b = (QuantumRegister(1, n) for n in ('h1', 'e', 'phi', 'a', 'b'))
    regs = [p0, p1, h1, e, phi, a, b]
    qc = QuantumCircuit(*regs, ClassicalRegister(6, 'meas')) if measure else QuantumCircuit(*regs)

    def flips(q, ctrl):
        for qq, c in zip(q, ctrl):
            if c == 0:
                qc.x(qq)

    def cnx(q, ctrl, t):
        flips(q, ctrl); qc.mcx(list(q), t); flips(q, ctrl)

    def cn_ry(entry, q, ctrl, t):
        flips(q, ctrl); qc.append(RYGate(2 * np.arccos(entry)).control(len(q)), list(q) + [t]); flips(q, ctrl)

    qc.x(p0[2])
    qc.cry(2 * np.arcsin(-qS), p0[2], p0[0])
    t_up, t_low = EPS ** 0, EPS ** 1
    qcount = [p0[0], p0[1], p0[2]]
    cnx(qcount, [0, 0, 1], a[0]); cnx(qcount, [1, 0, 1], b[0])
    d1 = math.sqrt(Delta_f(t_low, gA)) / math.sqrt(Delta_f(t_up, gA))
    d2 = math.sqrt(Delta_f(t_low, gB)) / math.sqrt(Delta_f(t_up, gA))
    qc.cry(2 * np.arccos(d1), a[0], e[0]); qc.cry(2 * np.arccos(d2), b[0], e[0])
    qem = [e[0], p0[0], p0[1], p0[2]]
    cn_ry(0, qem, [1, 0, 0, 1], h1[0]); cn_ry(0, qem, [1, 1, 0, 1], h1[0])
    cnx(qcount, [0, 0, 1], a[0]); cnx(qcount, [1, 0, 1], b[0])
    qc.cx(h1[0], p1[0])
    qc.cry(2 * np.arcsin(qS), p0[2], p0[0]); qc.cry(2 * np.arcsin(qS), p1[2], p1[0])
    if measure:
        for i in range(6):
            qc.measure(i, i)
    return qc


# ---------- decomposition of multi-controlled gates (Aqcel rule: RCCX ladder on ancillas w, then one singly-controlled U) ----------
def decompose_mcu(qc):
    big = []
    for ins in qc.data:
        nq = len(ins.qubits)
        if nq > 3 or (nq == 3 and ins.operation.name not in ('ccx', 'rccx')):
            nc = ins.operation.num_ctrl_qubits
            base1 = ins.operation.base_gate.control(1)
            big.append(nc - 2 if base1.name == 'cx' else nc - 1)
    if not big:
        return qc
    w = QuantumRegister(max(big), 'w')
    new = QuantumCircuit(*qc.qregs, w, *qc.cregs)
    for ins in qc.data:
        nq = len(ins.qubits)
        if nq > 3 or (nq == 3 and ins.operation.name not in ('ccx', 'rccx')):
            nc = ins.operation.num_ctrl_qubits
            base1 = ins.operation.base_gate.control(1)
            nanc = nc - 2 if base1.name == 'cx' else nc - 1
            c, t = list(ins.qubits[:nc]), ins.qubits[nc]
            new.append(RCCXGate(), [c[0], c[1], w[0]])
            for i in range(nanc - 1):
                new.append(RCCXGate(), [c[i + 2], w[i], w[i + 1]])
            if base1.name == 'cx':
                new.append(CCXGate(), [w[nanc - 1], c[-1], t])
            else:
                new.append(base1, [w[nanc - 1], t])
            for i in reversed(range(nanc - 1)):
                new.append(RCCXGate(), [c[i + 2], w[i], w[i + 1]])
            new.append(RCCXGate(), [c[0], c[1], w[0]])
        else:
            new.append(ins.operation, ins.qubits, ins.clbits)
    return new


# ---------- cancel a gate against the next gate that touches it, when identical qubits and inverse (RCCX pairs always) ----------
def _cancels(p, c):
    if p.operation.name in ('barrier', 'measure', 'reset') or c.operation.name in ('barrier', 'measure', 'reset'):
        return False
    if tuple(p.qubits) != tuple(c.qubits):
        return False
    if p.operation.name == 'rccx' and c.operation.name == 'rccx':
        return True
    try:
        return p.operation.inverse() == c.operation
    except Exception:
        return False


def remove_adjacent(qc):
    data = list(qc.data)
    changed = True
    while changed:
        changed = False
        for i, p in enumerate(data):
            if p.operation.name in ('barrier', 'measure', 'reset'):
                continue
            for j in range(i + 1, len(data)):
                c = data[j]
                if (p.qubits[-1] in c.qubits) or (c.qubits[-1] in p.qubits):
                    if _cancels(p, c):
                        del data[j]; del data[i]; changed = True
                    break
            if changed:
                break
    out = qc.copy_empty_like()
    for ins in data:
        out.append(ins.operation, ins.qubits, ins.clbits)
    return out


# ---------- exact control-state 'measurement' on the optimized prefix ----------
def _probs(prefix, ctrl):
    sv = Statevector(prefix.remove_final_measurements(inplace=False))
    idx = [prefix.find_bit(q).index for q in ctrl]
    pr = sv.probabilities(idx)  # little-endian over idx: index k -> bit j of k is ctrl[j]
    return {tuple((k >> j) & 1 for j in range(len(idx))): float(v) for k, v in enumerate(pr)}


def remove_controlled_operations(qc, thr):
    """Aqcel-v1 judge rules (v1 tag remove_controlled_operations.judge / run_qc), probabilities exact. Returns (circuit, n_measurements)."""
    new = QuantumCircuit(*qc.qregs)
    stack_q, stack_alt = [], []
    nmeas = 0
    for ins in qc.data:
        op, qs = ins.operation, ins.qubits
        if op.name == 'measure':
            if not new.cregs:
                for cr in qc.cregs:
                    new.add_register(cr)
            new.append(op, qs, ins.clbits); continue
        if len(qs) > 1 and op.name != 'barrier':
            if op.name == 'rccx' and tuple(qs) in stack_q:
                alt = stack_alt[-1]
                if alt is not None:
                    new.append(alt[0], alt[1])
                stack_q.pop(); stack_alt.pop(); continue
            ctrl, t = list(qs[:-1]), qs[-1]
            P = _probs(new, ctrl); nmeas += 1
            S = {k for k, v in P.items() if v >= thr}
            alt = None
            if op.name in ('ccx', 'rccx'):
                c0, c1 = ctrl
                if (1, 1) not in S:
                    pass
                elif S == {(1, 1)}:
                    alt = (XGate(), [t])
                elif (0, 1) not in S:
                    alt = (CXGate(), [c1, t])
                elif (1, 0) not in S:
                    alt = (CXGate(), [c0, t])
                else:
                    alt = (op, list(qs))
            else:
                if (1,) not in S:
                    pass
                elif (0,) not in S:
                    alt = (op.base_gate, [t])
                else:
                    alt = (op, list(qs))
            if alt is not None:
                new.append(alt[0], alt[1])
            if op.name == 'rccx':
                stack_q.append(tuple(qs))
                stack_alt.append(alt)
        else:
            new.append(op, qs, ins.clbits)
    return new, nmeas


# ---------- CX-pair removal (paper Sec. 3.2, three sufficient conditions, certified on the exact prefix state) ----------
DIAG = {'rz', 'p', 'z', 's', 'sdg', 't', 'tdg', 'u1'}


def cx_pair_removal(qc):
    data = list(qc.data)
    n_removed = 0
    progress = True
    while progress:
        progress = False
        for i, g in enumerate(data):
            if g.operation.name != 'cx':
                continue
            c, t = g.qubits
            j = next((k for k in range(i + 1, len(data)) if data[k].operation.name == 'cx' and tuple(data[k].qubits) == (c, t)), None)
            if j is None:
                continue
            ok = True
            for k in range(i + 1, j):
                h = data[k]; qk = list(h.qubits)
                if h.operation.name == 'barrier':
                    continue
                if t in qk and (len(qk) == 1 or qk[-1] == t):   # cond. 2: t only ever a control between the pair
                    ok = False; break
                if c in qk and qk[-1] == c and not (len(qk) == 1 and h.operation.name in DIAG):   # cond. 3: c's value unchanged
                    ok = False; break
                if h.operation.name == 'measure':
                    ok = False; break
            if not ok:
                continue
            pre = qc.copy_empty_like()
            for h in data[:i]:
                if h.operation.name != 'measure':
                    pre.append(h.operation, h.qubits, h.clbits)
            sv = Statevector(pre.remove_final_measurements(inplace=False))
            if sv.probabilities([qc.find_bit(t).index])[1] > 1e-12:   # cond. 1: t exactly |0> before the first CX
                continue
            newmid = []
            for k in range(i + 1, j):
                h = data[k]; qk = list(h.qubits)
                if t in qk:
                    if c in qk:   # both c and t control the gate -> controlled on c only
                        newmid.append((CXGate(), [c, qk[-1]], [])) if h.operation.name in ('ccx', 'rccx') else newmid.append(None)
                        if newmid[-1] is None:
                            ok = False; break
                    else:
                        newmid.append((h.operation, [c if q == t else q for q in qk], list(h.clbits)))
                else:
                    newmid.append((h.operation, qk, list(h.clbits)))
            if not ok:
                continue
            tmp = qc.copy_empty_like()
            for h in data[:i]:
                tmp.append(h.operation, h.qubits, h.clbits)
            for op, q, cl in newmid:
                tmp.append(op, q, cl)
            for h in data[j + 1:]:
                tmp.append(h.operation, h.qubits, h.clbits)
            data = list(tmp.data); n_removed += 1; progress = True
            break
    out = qc.copy_empty_like()
    for h in data:
        out.append(h.operation, h.qubits, h.clbits)
    return out, n_removed


def aqcel(qc, thr, version):
    q1 = remove_adjacent(decompose_mcu(qc))
    q2, nm = remove_controlled_operations(q1, thr)
    q3 = remove_adjacent(q2)
    npairs = 0
    if version == 2:
        q3, npairs = cx_pair_removal(q3)
        q3 = remove_adjacent(q3)
    return q3, nm, npairs


def ideal_dist(qc, nbits=6):
    """exact output distribution over the 6 measured bits (qubits 0-5 -> clbits 0-5), keys as Qiskit bitstrings (clbit 5 leftmost)."""
    u = qc.remove_final_measurements(inplace=False)
    pr = Statevector(u).probabilities(list(range(nbits)))
    return {format(k, '0%db' % nbits): float(v) for k, v in enumerate(pr) if v > 1e-15}


def hellinger_fidelity(p, q):
    keys = set(p) | set(q)
    return float(sum(math.sqrt(max(p.get(k, 0.0), 0.0) * max(q.get(k, 0.0), 0.0)) for k in keys) ** 2)
