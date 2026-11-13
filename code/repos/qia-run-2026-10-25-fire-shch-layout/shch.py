"""shch.py -- free calibration run (Kumar) for Zenodo 10.5281/zenodo.22770646 (Vitaly Shcherbak, Montenegro), Local Friendliness test.
Their runs: fez S = 2.6627 (job id not retained), marrakesh 2.7185, marrakesh 2.4047; 8000 shots, 4 circuits; spread attributed to 'normal drift in gate
calibration on real devices over time'. Their circuit (local_friendliness_experiment_en.ipynb, code read with credential lines filtered), verbatim below.
This run: fez A, kingston B, kingston B, fez A in one session, same physical qubits [109,110,118] (q0 = centre), opt level 1 as theirs, 8000 shots;
plus a PRODUCT arm (|01>, no entanglement), which cannot exceed S = 2."""
import numpy as np
from qiskit import QuantumCircuit
theta1, theta3, beta2, beta3 = 0.0, np.pi / 2, np.pi / 4, 3 * np.pi / 4
SHOTS = 8000; LAYOUT = [109, 110, 118]
def prepare_singlet(qc, a, b): qc.h(a); qc.cx(a, b); qc.z(a); qc.x(b)
def rotate_measure(qc, q, c, ang): qc.ry(-ang, q); qc.measure(q, c)
def build_circuit(x, y, product=False):
    qc = QuantumCircuit(3, 2)
    if product: qc.x(1)
    else: prepare_singlet(qc, 0, 1)
    qc.cx(0, 2)
    if x == 'PEEK': qc.measure(2, 0)
    elif x == 'REVERSE3': qc.cx(0, 2); rotate_measure(qc, 0, 0, theta3)
    rotate_measure(qc, 1, 1, y); return qc
SETTINGS = [('PEEK', beta2), ('PEEK', beta3), ('REVERSE3', beta2), ('REVERSE3', beta3)]
def circuits():
    return [build_circuit(x, y) for x, y in SETTINGS] + [build_circuit(x, y, True) for x, y in SETTINGS]
def E_of(counts):
    n = sum(counts.values()); E = sum((1 - 2 * int(k[1])) * (1 - 2 * int(k[0])) * v for k, v in counts.items()) / n; return E, n
def S_of(cl):
    Es = [E_of(c) for c in cl]; E = [e for e, _ in Es]; S = -E[0] + E[1] - E[2] - E[3]
    se = float(np.sqrt(sum((1 - e * e) / n for e, n in Es))); return S, se, E
def outcome(d, se, width=0.2):
    lo, hi = d - 1.96 * se, d + 1.96 * se
    return dict(value=d, se=se, ci95=[lo, hi], outcome='CANNOT_TELL' if hi - lo > width else ('ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'))
def analyse(jobs):
    """jobs: list of dicts {label, backend, counts: 8 count dicts (4 singlet then 4 product)}."""
    out = {'jobs': []}
    for j in jobs:
        S, se, E = S_of(j['counts'][:4]); Sp, sep, _ = S_of(j['counts'][4:])
        out['jobs'].append(dict(label=j['label'], backend=j['backend'], S=S, se=se, E=E, S_product=Sp, se_product=sep))
    J = {x['label']: x for x in out['jobs']}
    out['drift_fez'] = outcome(J['A2']['S'] - J['A1']['S'], float(np.hypot(J['A2']['se'], J['A1']['se'])))
    out['drift_kingston'] = outcome(J['B2']['S'] - J['B1']['S'], float(np.hypot(J['B2']['se'], J['B1']['se'])))
    fz = (J['A1']['S'] + J['A2']['S']) / 2; kg = (J['B1']['S'] + J['B2']['S']) / 2
    out['chip_fez_minus_kingston'] = outcome(fz - kg, float(0.5 * np.sqrt(sum(J[k]['se'] ** 2 for k in J))))
    out['their_spread'] = 2.7185 - 2.4047
    out['violation_every_job'] = all(x['S'] - 1.96 * x['se'] > 2 for x in out['jobs'])
    out['KNOWN_GOOD'] = dict(rule='product arm S must sit at or below the bound 2 (S_product + 1.96 se < 2.0) in every job', passed=all(x['S_product'] + 1.96 * x['se_product'] < 2.0 for x in out['jobs']))
    return out
