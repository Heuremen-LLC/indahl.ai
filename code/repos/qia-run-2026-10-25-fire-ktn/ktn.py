"""ktn.py -- free calibration fill (Kumar) for Zenodo 10.5281/zenodo.23122648 (Independent Researcher, Yaounde, Cameroon; RATISS Labs).
Their record: woven arm on ibm_fez (job da81b5m0ukec7383sf20) score 0.1823; aligned arm score -0.0778 with job id 'dcc12f86-...' (a UUID, the form a
local simulator returns, no backend field); 'hardware' contrast 0.2601; the preprint text says '+0.34 on real hardware' (0.3362 is their exact reference).
This fill: BOTH arms on fez in ONE job, their circuits and metric verbatim, on their default compile (no layout, opt 1) twice + three rule-chosen chains."""
import numpy as np
from itertools import combinations
from ktnmetric import coupled_metric
N = 4; PAIRS = [(0, 1), (1, 2), (2, 3), (0, 3)]; SHOTS = 4096
def woven():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(N); a = np.zeros(2 ** N, complex)
    for p in combinations(range(N), 2): a[(1 << p[0]) | (1 << p[1])] = 1.0
    qc.initialize(a / np.linalg.norm(a), range(N)); return qc
def aligned():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(N); qc.x(0); qc.x(1); return qc
def basis_circs(base):
    out = []
    for b in ('Z', 'XX', 'YY'):
        qc = base.copy()
        if b == 'XX':
            for q in range(N): qc.h(q)
        if b == 'YY':
            for q in range(N): qc.sdg(q); qc.h(q)
        qc.measure_all(); out.append(qc)
    return out
def _exp(counts, i, j):
    tot = sum(counts.values()); return sum((1.0 if k[::-1][i] == k[::-1][j] else -1.0) * n for k, n in counts.items()) / tot
def C_from(counts3, postselect=True):
    z, xx, yy = counts3
    if postselect: z = {b: n for b, n in z.items() if b.count('1') == 2}
    C = np.zeros((N, N)); tot = sum(z.values())
    for b, n in z.items():
        for q in range(N): C[q, q] += int(b[::-1][q]) * n / tot
    for i, j in PAIRS: C[i, j] = C[j, i] = 0.25 * (_exp(xx, i, j) + _exp(yy, i, j))
    return C
def diag_raw(zc):
    tot = sum(zc.values()); return [sum(int(b[::-1][q]) * n for b, n in zc.items()) / tot for q in range(N)]
def analyse(raw):
    """raw[arm] = {'woven': [Z,XX,YY counts], 'aligned': [Z,XX,YY counts]}"""
    out = {}
    for arm, d in raw.items():
        w = coupled_metric(C_from(d['woven']))['score']; a = coupled_metric(C_from(d['aligned']))['score']
        out[arm] = dict(woven=w, aligned=a, contrast=w - a, aligned_diag_raw=diag_raw(d['aligned'][0]))
    cs = [out[k]['contrast'] for k in out]
    out['SUMMARY'] = dict(contrasts={k: out[k]['contrast'] for k in raw}, min=min(cs), max=max(cs), theirs_hw=0.2601, theirs_headline=0.34, exact=0.3362,
                          headline_inside_hw_range=bool(min(cs) <= 0.34 <= max(cs)), theirs_hw_inside_range=bool(min(cs) <= 0.2601 <= max(cs)),
                          default_copy_gap=out['default_a']['contrast'] - out['default_b']['contrast'])
    kg = all(abs(out[k]['aligned_diag_raw'][0] - 1) < 0.06 and abs(out[k]['aligned_diag_raw'][1] - 1) < 0.06 and out[k]['aligned_diag_raw'][2] < 0.06 and out[k]['aligned_diag_raw'][3] < 0.06 for k in raw)
    out['KNOWN_GOOD'] = dict(rule='aligned |0011> raw Z diagonal within 0.06 of [1,1,0,0] in every arm (a computational basis state; the answer is known)', passed=kg)
    return out
