"""tara.py -- CHSH RE-TEST of arXiv 2512.04016 (Tasar & Ocal Tasar, independent, Madrid) on ibm_fez. Their chip (ibm_torino) is retired:
this is a re-test of the same construction on a different chip, NOT a calibration of their Torino data.
Construction (their paper prints no angles/qubits; we use the standard optimal CHSH settings, which match their printed sign pattern
E00,E01,E10 > 0, E11 < 0): Bell pair H(q0) CX(q0,q1); measure A along angle a in the XZ plane, B along b, via RY(-theta) then Z.
a0 = 0, a1 = pi/2, b0 = pi/4, b1 = -pi/4; E(a,b) = <(-1)^(A+B)>; S = E00 + E01 + E10 - E11 (ideal 2 sqrt 2).
Shots: their file = 10 cycles x 4 settings x 1500. Ours: same, settings interleaved per cycle, plus a 4-state readout bracket
(|00>,|01>,|10>,|11>) at the start and end of the job (descriptive only)."""
import numpy as np
from qiskit import QuantumCircuit
A = [0.0, np.pi / 2]; B = [np.pi / 4, -np.pi / 4]; SHOTS = 1500; CYCLES = 10
THEIRS_S, THEIRS_SE = 2.7320, 0.0119          # their 60,000-shot table through this code (known-good)
Z99 = 2.5758; SPREAD_MAX = 1.5
def chsh_circ(i, j):
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1); qc.ry(-A[i], 0); qc.ry(-B[j], 1); qc.measure([0, 1], [0, 1]); return qc
def bracket_circ(s):
    qc = QuantumCircuit(2, 2)
    if s[1] == '1': qc.x(0)
    if s[0] == '1': qc.x(1)
    qc.measure([0, 1], [0, 1]); return qc
def plan():
    """list of (kind, label) in submission order"""
    order = [('bracket', s) for s in ('00', '01', '10', '11')]
    for c in range(CYCLES): order += [('chsh', (c, i, j)) for i in (0, 1) for j in (0, 1)]
    order += [('bracket', s) for s in ('00', '01', '10', '11')]
    return order
def circuits():
    return [chsh_circ(l[1], l[2]) if k == 'chsh' else bracket_circ(l) for k, l in plan()]
def corr(counts):
    """counts: dict bitstring 'ba' (qiskit order: c1 c0) -> n ; returns E = <(-1)^(a+b)>, n"""
    n = sum(counts.values()); same = sum(v for k, v in counts.items() if k[-1] == k[-2]); return (2 * same - n) / n, n
def S_of(E): return E[0][0] + E[0][1] + E[1][0] - E[1][1]
def analyze(entries):
    """entries: list of (kind, label, counts) in submission order"""
    pooled = {(i, j): {} for i in (0, 1) for j in (0, 1)}; cyc = {}
    for k, l, cts in entries:
        if k != 'chsh': continue
        c, i, j = l
        for b, v in cts.items(): pooled[(i, j)][b] = pooled[(i, j)].get(b, 0) + v
        cyc.setdefault(c, {})[(i, j)] = corr(cts)
    E = [[corr(pooled[(i, j)])[0] for j in (0, 1)] for i in (0, 1)]; N = [[corr(pooled[(i, j)])[1] for j in (0, 1)] for i in (0, 1)]
    S = S_of(E); se = np.sqrt(sum((1 - E[i][j] ** 2) / N[i][j] for i in (0, 1) for j in (0, 1)))
    Sc = []; sec = []
    for c in sorted(cyc):
        e = [[cyc[c][(i, j)][0] for j in (0, 1)] for i in (0, 1)]; Sc.append(S_of(e))
        sec.append(np.sqrt(sum((1 - e[i][j] ** 2) / cyc[c][(i, j)][1] for i in (0, 1) for j in (0, 1))))
    ratio = float(np.std(Sc, ddof=1) / np.sqrt(np.mean(np.square(sec)))) if len(Sc) > 1 else float('nan')
    D = S - THEIRS_S; sd = np.sqrt(se ** 2 + THEIRS_SE ** 2)
    if not (ratio <= SPREAD_MAX): r1 = 'CANNOT_TELL'
    elif D - Z99 * sd > 0: r1 = 'ABOVE'
    elif D + Z99 * sd < 0: r1 = 'BELOW'
    else: r1 = 'CONSISTENT'
    v = S - 2.0
    r2 = 'ABOVE' if v - Z99 * se > 0 else 'BELOW' if v + Z99 * se < 0 else 'CONSISTENT'
    # descriptive: bracket confusion and bracket-corrected S (tensor-product inversion of per-qubit flips)
    br = {}
    for k, l, cts in entries:
        if k == 'bracket':
            for b, vv in cts.items(): br.setdefault(l, {}); br[l][b] = br[l].get(b, 0) + vv
    out = dict(E=E, N=N, S=S, se=se, cycle_S=Sc, spread_ratio=ratio, D=D, D_sd=sd, R1=r1, R2=r2, bracket=br)
    if len(br) == 4:
        def p(prep, q, val):  # P(qubit q reads val | prepared prep)
            c = br[prep]; n = sum(c.values()); return sum(v for b, v in c.items() if b[-1 - q] == val) / n
        e = {q: (p('00', q, '1') + p('11' if q else '11', q, '0')) for q in (0, 1)}
        out['bracket_flip_sum'] = e
        Ec = [[E[i][j] / ((1 - e[0]) * (1 - e[1])) for j in (0, 1)] for i in (0, 1)]; out['S_bracket_corrected'] = S_of(Ec)
    return out
def table_entries(csv_path):
    """their released 60,000-shot table (x,y,a,b) -> entries in OUR format, in file order (10 cycles of 4 x 1500)"""
    rows = np.loadtxt(csv_path, delimiter=',', skiprows=1, dtype=int); ents = []
    for blk in range(len(rows) // SHOTS):
        r = rows[blk * SHOTS:(blk + 1) * SHOTS]; x, y = int(r[0, 0]), int(r[0, 1]); assert (r[:, 0] == x).all() and (r[:, 1] == y).all()
        cts = {}
        for a, b in r[:, 2:]: k = f'{b}{a}'; cts[k] = cts.get(k, 0) + 1
        ents.append(('chsh', (blk // 4, x, y), cts))
    return ents
