"""ocean.py -- free calibration run (Kumar) for Zenodo 10.5281/zenodo.22856763 (Dr Akshay Honrao, Quantum Ocean Part 93 'The Quantum Computer's Compass').
Their claim: drain-direction qubits Q41-45 have the lowest entanglement penalty (GHZ err / basis err 1.79x) vs anti-drain Q29-33 (6.01x).
Their design, kept exactly: ibm_fez, groups of 5, basis circuit (measure all) and GHZ circuit (H on first, CX chain in group order), 500 shots, 8 reps.
Error = 1 - P(00000) for basis, 1 - P(00000) - P(11111) for GHZ; delta = GHZ err - basis err; penalty = GHZ err / basis err.
Added group ANTI_HEALTHY [28,29,30,31,18]: anti-drain region (3 of their anti qubits) on couplers the record calls healthy.
Decider: delta(ANTI_HEALTHY) - delta(DRAIN). Direction hypothesis predicts ~ +0.3 (their anti-minus-drain 0.30); coupler-health predicts ~0."""
import numpy as np
GROUPS = {'DRAIN': [41, 42, 43, 44, 45], 'ANTI_DRAIN': [29, 30, 31, 32, 33], 'CONTROL_1': [70, 71, 72, 73, 74], 'CONTROL_2': [130, 131, 132, 133, 134], 'ANTI_HEALTHY': [28, 29, 30, 31, 18]}
SHOTS, REPS = 500, 8
def errs(counts, kind):
    n = sum(counts.values()); g = lambda k: counts.get(k, 0)
    return 1 - g('00000') / n if kind == 'basis' else 1 - (g('00000') + g('11111')) / n
def analyse(R):
    """R[group][kind] = list of 8 counts dicts."""
    out = {}
    for g, d in R.items():
        b = np.array([errs(c, 'basis') for c in d['basis']]); h = np.array([errs(c, 'ghz') for c in d['ghz']]); dl = h - b
        out[g] = dict(basis=float(b.mean()), ghz=float(h.mean()), delta=float(dl.mean()), delta_sem=float(dl.std(ddof=1) / np.sqrt(len(dl))), penalty=float(h.mean() / b.mean()) if b.mean() > 0 else None)
    d = out['ANTI_HEALTHY']['delta'] - out['DRAIN']['delta']; s = float(np.hypot(out['ANTI_HEALTHY']['delta_sem'], out['DRAIN']['delta_sem']))
    T = 2.145  # t(0.975, df=14): two groups x 8 reps; z=1.96 gave a 7.7% floor in synth
    lo, hi = d - T * s, d + T * s
    oc = 'CANNOT_TELL' if hi - lo > 0.10 else ('ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT')
    out['DECIDER'] = dict(value=d, sem=s, ci95=[lo, hi], outcome=oc, direction_predicts='~+0.30 (their anti-minus-drain delta)', health_predicts='~0')
    out['KNOWN_GOOD'] = dict(control1_ghz_err=out['CONTROL_1']['ghz'], rule='> 0.70 (two couplers marked failed; theirs 0.8907)', passed=out['CONTROL_1']['ghz'] > 0.70)
    out['REPLICATION'] = dict(drain_penalty=out['DRAIN']['penalty'], anti_penalty=out['ANTI_DRAIN']['penalty'], drain_lower=(out['DRAIN']['penalty'] or 9) < (out['ANTI_DRAIN']['penalty'] or 0),
                              lowest_delta=min(GROUPS, key=lambda g: out[g]['delta']), lowest_ghz_err=min(GROUPS, key=lambda g: out[g]['ghz']))
    return out
def circuits():
    from qiskit import QuantumCircuit
    C = []
    for g in GROUPS:
        for kind in ('basis', 'ghz'):
            for r in range(REPS):
                qc = QuantumCircuit(5, 5, name=f'{g}|{kind}|{r}')
                if kind == 'ghz':
                    qc.h(0); [qc.cx(i, i + 1) for i in range(4)]
                qc.measure(range(5), range(5)); C.append(qc)
    return C
