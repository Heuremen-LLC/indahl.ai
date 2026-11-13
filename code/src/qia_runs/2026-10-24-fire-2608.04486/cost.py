"""cost.py -- zero-QPU: measurement bases and ideal shot-noise width of Var C2 = <C2^2> - <C2>^2 for the two exemplars (k=1 solvable, k=0 mixed),
per-basis sampling of the QWC groups (joint grouping of C2 and C2^2 terms, as one Estimator PUB), with and without the C2/C2^2 covariance."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pds
from qiskit.quantum_info import SparsePauliOp, Operator, Statevector, Pauli
nq, Ce, ex = pds.exemplars(3)
A = SparsePauliOp.from_operator(Operator(Ce)).simplify(); B = SparsePauliOp.from_operator(Operator(Ce @ Ce)).simplify()
ca = dict(zip(A.paulis.to_labels(), A.coeffs.real)); cb = dict(zip(B.paulis.to_labels(), B.coeffs.real))
labs = sorted(set(ca) | set(cb)); groups = SparsePauliOp(labs).group_commuting(qubit_wise=True)
def basis_of(g):
    s = ['I'] * nq
    for l in g.paulis.to_labels():
        for i, c in enumerate(l):
            if c != 'I': s[i] = c
    return ''.join(s)
def per_shot_moments(w, bas):
    """exact joint distribution of (a, b) = (sum_t ca_t z_t, sum_t cb_t z_t) for one shot in basis bas"""
    sv = Statevector(w)
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(nq)
    for i, c in enumerate(reversed(bas)):  # label index 0 = highest qubit
        if c == 'X': qc.h(i)
        if c == 'Y': qc.sdg(i); qc.h(i)
    p = sv.evolve(qc).probabilities()
    return p
out = {}
for k in (1, 0):
    w = ex[k]['w']; tot = dict(VA=0., VB=0., CAB=0.)
    for g in groups:
        bas = basis_of(g); p = per_shot_moments(w, bas); ts = g.paulis.to_labels()
        a = np.zeros(2 ** nq); b = np.zeros(2 ** nq)
        for x in range(2 ** nq):
            bits = format(x, '0%db' % nq)  # bits[0] = highest qubit, matches label order
            for t in ts:
                z = (-1) ** sum(int(bits[i]) for i, c in enumerate(t) if c != 'I')
                a[x] += ca.get(t, 0) * z; b[x] += cb.get(t, 0) * z
        ma, mb = p @ a, p @ b
        tot['VA'] += p @ (a - ma) ** 2; tot['VB'] += p @ (b - mb) ** 2; tot['CAB'] += p @ ((a - ma) * (b - mb))
    m1 = ex[k]['C2']
    out[k] = dict(kind=ex[k]['kind'], C2=m1, C2sq=ex[k]['C2sq'], per_shot=tot,
                  sd_indep_1shot=float(np.sqrt(tot['VB'] + 4 * m1 ** 2 * tot['VA'])),
                  sd_cov_1shot=float(np.sqrt(max(tot['VB'] + 4 * m1 ** 2 * tot['VA'] - 4 * m1 * tot['CAB'], 0))))
nb = len(groups)
res = dict(n_bases=nb, n_terms_C2=len(A), n_terms_C2sq=len(B), states=out)
for S in (4000, 6000, 60000, 240000):
    s1, s0 = out[1]['sd_indep_1shot'] / np.sqrt(S), out[0]['sd_indep_1shot'] / np.sqrt(S)
    c1, c0 = out[1]['sd_cov_1shot'] / np.sqrt(S), out[0]['sd_cov_1shot'] / np.sqrt(S)
    res['S%d' % S] = dict(sd_solv_indep=s1, sd_mix_indep=s0, sd_diff_indep=float(np.hypot(s1, s0)), z_diff_indep=240 / float(np.hypot(s1, s0)),
                          sd_diff_cov=float(np.hypot(c1, c0)), z_diff_cov=240 / float(np.hypot(c1, c0)), shots_per_pub=nb * S)
print(json.dumps(res, indent=1, default=float))
