"""n47.py -- free calibration run (Kumar) for Zenodo 10.5281/zenodo.21938548 (N47Lab, 'Observation of a Classical Prethermal DTC').
Their registered falsifiable prediction 4: 'Under an extended allocation (100k+ shots per circuit), the 3-qubit peak should persist at MI ~ 0.16 +/- 0.01.
Falsified if the peak collapses to the finite-shot floor.'  Their protocol, as printed: |0>^N, H on all, CP(phi) on all pairs, H on all, measure Z;
'separate' control: P(phi/N) per qubit instead of CP; PASM-H: extra H before CP instead of the final H layer. MI between the first two qubits, Miller-Madow.
Noiseless QM of the printed circuit (zero QPU, before this plan): MI = 0 at phi = pi for N = 2..6; PASM-H MI = 0 at every phi; N=2 phi=pi/4 MI = 0.0822."""
import numpy as np, itertools
ARMS = [('P3_PI', 3, np.pi, 'std', 100000), ('P2_PI', 2, np.pi, 'std', 20000), ('P2_PI4', 2, np.pi / 4, 'std', 20000), ('H2_PI2', 2, np.pi / 2, 'H', 20000), ('S3_PI', 3, np.pi, 'sep', 20000)]
def circuit(N, phi, v):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(N, N); qc.h(range(N))
    if v == 'H': qc.h(range(N))
    if v == 'sep': [qc.p(phi / N, q) for q in range(N)]
    else:
        for a, b in itertools.combinations(range(N), 2): qc.cp(phi, a, b)
    if v in ('std', 'sep'): qc.h(range(N))
    qc.measure(range(N), range(N)); return qc
def ideal(N, phi, v):
    from qiskit.quantum_info import Statevector
    qc = circuit(N, phi, v); qc.remove_final_measurements(); p = Statevector(qc).probabilities()
    return mi_from_p({format(i, '0%db' % N): x for i, x in enumerate(p)}, N, n=None)
def mi_from_p(cnt, N, n):
    P = np.zeros((2, 2)); tot = sum(cnt.values())
    for k, v in cnt.items():
        k = k.replace(' ', ''); P[int(k[-1]), int(k[-2])] += v   # qubit 0 = rightmost bit, qubit 1 = next
    P = P / tot; px, py = P.sum(1), P.sum(0)
    I = sum(P[a, b] * np.log2(P[a, b] / (px[a] * py[b])) for a in range(2) for b in range(2) if P[a, b] > 0)
    if n:  # Miller-Madow, as theirs: (k+ - 1)/(2n) nats -> bits, minus the marginals' corrections
        kj = (P > 0).sum(); kx = (px > 0).sum(); ky = (py > 0).sum()
        I -= ((kx - 1) + (ky - 1) - (kj - 1)) / (2 * n * np.log(2))
    return float(I)
def analyse(raw):
    rng = np.random.default_rng(5); out = {}
    for name, N, phi, v, shots in ARMS:
        cnt = raw[name]; keys = list(cnt); w = np.array([cnt[k] for k in keys], float); n = int(w.sum())
        I = mi_from_p(cnt, N, n); bs = []
        for _ in range(400):
            d = rng.multinomial(n, w / n); bs.append(mi_from_p(dict(zip(keys, d)), N, n))
        lo, hi = np.percentile(bs, [2.5, 97.5]); out[name] = dict(MI=I, ci95=[float(lo), float(hi)], ideal=ideal(N, phi, v), shots=n)
    p = out['P3_PI']; lo, hi = p['ci95']
    floor = 3 / (2 * p['shots'] * np.log(2))
    oc = 'CONSISTENT with their 0.16 +/- 0.01' if (lo <= 0.17 and hi >= 0.15) else ('BELOW their band' if hi < 0.15 else 'ABOVE their band')
    out['PREDICTION_4'] = dict(MI=p['MI'], ci95=p['ci95'], their_band=[0.15, 0.17], outcome=oc, collapsed_to_floor=bool(hi < 10 * floor + 0.002), floor_bits=floor)
    out['KNOWN_GOOD'] = dict(sep_MI=out['S3_PI']['MI'], rule='separate control must read MI < 0.002 (theirs <= 1e-4; ideal 0)', passed=out['S3_PI']['MI'] < 0.002)
    return out
