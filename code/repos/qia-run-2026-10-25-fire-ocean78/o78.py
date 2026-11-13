"""o78.py -- free calibration run (Kumar) for Zenodo 10.5281/zenodo.22737706 (Dr Akshay Honrao, Quantum Ocean Part 78 'First Light').
Their Experiment 1 (fez): single qubit RY to superposition level S = 4|a|^2|b|^2 (0, 0.5, 1), 150 identity gates, return, error = P(1); printed slope +0.001 per S
(0.475 / 0.525 / 0.575 %) and the bound |g1| < 0.001. The paper does not state the compile. ZERO-QPU (before this plan): Qiskit 2.5.2 at opt 1-3 and at the default
preset removes all 150 id gates and cancels RY(t)RY(-t): every S becomes the SAME circuit (measure only). Only opt 0 keeps the idle (3.6 us at 24 ns per id).
This run, one job on fez, 40 qubits in parallel per circuit: COLLAPSED arm (their circuit at the default preset) x 3 S; REAL arm (opt 0, 150 id kept) x 3 S;
KG arm: RY(pi/2), no return (P(1) = 0.5 by construction). Units for intervals: qubits (bootstrap over the 40)."""
import numpy as np
QUBITS = [2, 4, 5, 6, 10, 16, 17, 22, 23, 24, 26, 28, 30, 36, 50, 58, 68, 71, 74, 75, 78, 86, 88, 90, 96, 104, 112, 115, 117, 123, 127, 132, 138, 142, 143, 144, 145, 147, 151, 154]
S_LEVELS = [0.0, 0.5, 1.0]; NID = 150; SHOTS = 10000; T_ID = 24e-9
theta = lambda S: float(np.arcsin(np.sqrt(S)))  # S = sin^2(theta) for RY(theta)|0>: 4|a|^2|b|^2 = sin^2(theta)
def logical(S, kind):
    from qiskit import QuantumCircuit
    n = len(QUBITS); qc = QuantumCircuit(n, n)
    for i in range(n):
        if kind == 'KG': qc.ry(np.pi / 2, i)
        else:
            qc.ry(theta(S), i)
            for _ in range(NID): qc.id(i)
            qc.ry(-theta(S), i)
    qc.measure(range(n), range(n)); return qc
def model_err(S, T1, T2, ro01):
    """P(1) after RY(t), idle t_idle with amplitude damping T1 and pure dephasing from T2, RY(-t); plus readout P(1|0) on the |0> part. Record T1/T2."""
    t = NID * T_ID; th = theta(S)
    r = np.array([np.sin(th), 0.0, np.cos(th)])       # Bloch vector after RY(th)
    g1 = np.exp(-t / T1); g2 = np.exp(-t / T2)
    r = np.array([r[0] * g2, r[1] * g2, 1 - (1 - r[2]) * g1])
    c, s = np.cos(-th), np.sin(-th); x, z = r[0], r[2]; z2 = -s * x + c * z     # RY(-th) about y: z' = -sin(a) x + cos(a) z with a = -th
    p1 = (1 - z2) / 2; return float(p1 + (1 - p1) * ro01)
def per_qubit_err(counts, n):
    tot = sum(counts.values()); e = np.zeros(n)
    for k, v in counts.items():
        b = k.replace(' ', '')[::-1]
        for i in range(n): e[i] += v * (b[i] == '1')
    return e / tot
def slope(errs):  # errs: 3 x nq -> per-qubit slope vs S
    S = np.array(S_LEVELS); X = S - S.mean(); return (X[:, None] * (errs - errs.mean(0))).sum(0) / (X ** 2).sum()
def boot(v, rng, n=2000):
    b = [rng.choice(v, len(v)).mean() for _ in range(n)]; return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
def oc(ci, w=0.004):
    lo, hi = ci; return 'CANNOT_TELL' if hi - lo > w else ('ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT')
def analyse(raw, rec):
    """raw[arm][S or 'KG'] = counts; rec = per-qubit (T1, T2, prob_meas1_prep0) from the record at submission."""
    rng = np.random.default_rng(7); n = len(QUBITS); out = {}
    for arm in ('COLLAPSED', 'REAL'):
        E = np.array([per_qubit_err(raw[arm][str(S)], n) for S in S_LEVELS]); sl = slope(E)
        out[arm] = dict(mean_err=[float(x) for x in E.mean(1)], slope=float(sl.mean()), slope_ci95=boot(sl, rng))
    pred = np.array([[model_err(S, *rec[q]) for q in QUBITS] for S in S_LEVELS]); psl = slope(pred)
    out['REAL']['record_model_slope'] = float(psl.mean())
    res = slope(np.array([per_qubit_err(raw['REAL'][str(S)], n) for S in S_LEVELS])) - psl
    out['REAL']['residual_over_record'] = dict(mean=float(res.mean()), ci95=boot(res, rng)); out['REAL']['residual_over_record']['outcome'] = oc(out['REAL']['residual_over_record']['ci95'])
    out['COLLAPSED']['outcome_vs_zero'] = oc(out['COLLAPSED']['slope_ci95']); out['REAL']['outcome_vs_zero'] = oc(out['REAL']['slope_ci95'])
    out['THEIRS'] = dict(slope=0.001, bound_g1=0.001)
    out['COLLAPSED']['their_0.001_inside'] = out['COLLAPSED']['slope_ci95'][0] <= 0.001 <= out['COLLAPSED']['slope_ci95'][1]
    out['REAL']['their_0.001_inside'] = out['REAL']['slope_ci95'][0] <= 0.001 <= out['REAL']['slope_ci95'][1]
    kg = per_qubit_err(raw['KG']['KG'], n); out['KNOWN_GOOD'] = dict(mean_P1=float(kg.mean()), rule='mean P(1) of RY(pi/2) over 40 qubits within 0.5 +/- 0.03', passed=bool(abs(kg.mean() - 0.5) < 0.03))
    return out
