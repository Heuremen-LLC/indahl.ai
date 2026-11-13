"""reddy.py -- free calibration run for Zenodo 10.5281/zenodo.23123273 (Dhanunjay Reddy, Andhra University).
Their spot-check: t-shape Bell route on ibm_fez physical [16,3,2,4,5], Bell on logical 0 and 4 (graph distance 3), XX/YY/ZZ at 2000 shots,
F = (1+XX-YY+ZZ)/4 = 0.921 +/- 0.004 vs their Aer model 0.9203. Their own limit: 'it does not show the noise model fits other chips'.
This run: the same circuit on the same physical T on fez (repeat), kingston, boston, pittsburgh. Analysis is theirs: correlators from counts."""
import numpy as np
SIM_F = 0.9203; THEIR_F = 0.921; SHOTS = 2000
T_PHYS = [16, 3, 2, 4, 5]
def corr(counts):
    n = sum(counts.values()); same = sum(v for k, v in counts.items() if k.replace(' ', '')[-2:] in ('00', '11'))
    return (2 * same - n) / n, n
def analyse(cnt):
    """cnt: {'XX': counts, 'YY': counts, 'ZZ': counts} -> correlators, F and se (their formula)."""
    out = {}
    for b in ('XX', 'YY', 'ZZ'):
        c, n = corr(cnt[b]); out[b] = c; out['se_' + b] = float(np.sqrt((1 - c * c) / n))
    F = (1 + out['XX'] - out['YY'] + out['ZZ']) / 4; se = 0.25 * float(np.sqrt(out['se_XX'] ** 2 + out['se_YY'] ** 2 + out['se_ZZ'] ** 2))
    d = F - SIM_F; lo, hi = d - 1.96 * se, d + 1.96 * se
    oc = 'CANNOT_TELL' if 2 * 1.96 * se > 0.05 else ('ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT')
    out.update(F=F, se_F=se, vs_sim=dict(diff=d, ci95=[lo, hi], outcome=oc))
    return out
def build(backend=None):
    from qiskit import QuantumCircuit, transpile
    qc = QuantumCircuit(5); qc.h(0); qc.cx(0, 4)
    kw = dict(optimization_level=3, seed_transpiler=42, initial_layout=T_PHYS)
    routed = transpile(qc, backend=backend, **kw) if backend is not None else None
    return routed
def correlators(routed, backend=None):
    """Their build_correlator_circuits, verbatim logic: rotations on the physical qubits holding logical 0 and 4 after routing."""
    from qiskit import QuantumCircuit
    fl = routed.layout.final_index_layout(); p0, p1 = fl[0], fl[4]
    C = {}
    for b in ('ZZ', 'XX', 'YY'):
        qc = QuantumCircuit(routed.num_qubits, 2); qc.compose(routed, inplace=True)
        if b == 'XX': qc.h([p0, p1])
        if b == 'YY': qc.sdg([p0, p1]); qc.h([p0, p1])
        qc.measure([p0, p1], [0, 1]); C[b] = qc
    if backend is not None:   # ADDENDUM 1: translation + 1q merge only (opt 1, identity layout) (their record shows native sx/rz/cz only); layout and routing untouched
        from qiskit import transpile
        C = {k: transpile(v, backend=backend, optimization_level=1, initial_layout=list(range(v.num_qubits)), seed_transpiler=42) for k, v in C.items()}
    return C, (p0, p1)
