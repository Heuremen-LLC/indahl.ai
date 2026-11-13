#!/usr/bin/env python3
"""extract_gate_cost.py -- builds data/gate_cost.json from the private raw job results.

NOT needed to verify the numbers (verify_gate_cost.py reads only the JSON). Shown so the
extraction is auditable. Needs numpy and the raw per-job results (run<N>_results.npz, run<N>_meta.json)
under  <parallax>/out/qubit_fifth_run/data/fire/<chip>/ . Read-only on those files.

Per run it keeps, for every qubit whose two reference readout clouds (qubit prepared |0> and |1>) are
more than 4 widths apart ("readable"): the excited-population level after 2, 6 and 10 spaced X gates
(start |0>, an X after every 30 us), the level of a qubit prepared in |1> and left alone for 30, 90 and
300 us, and the standard error of each level over the shots.
Level = projection of the averaged IQ readout between the qubit's own |0> cloud (=0) and |1> cloud (=1).
"""
import json, os, sys
import numpy as np

ROOT = os.environ.get('PARALLAX', '/Users/heuremen/bones-forge/parallax')
FIRE = os.path.join(ROOT, 'out', 'qubit_fifth_run', 'data', 'fire')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'gate_cost.json')

# (chip, run, day label, group label)
RUNS = [('ibm_fez', 371, 'day1'), ('ibm_kingston', 392, 'day1'), ('ibm_boston', 441, 'day1'), ('ibm_phoenix', 531, 'day1'),
        ('ibm_boston', 711, 'day2'), ('ibm_boston', 712, 'day2'), ('ibm_boston', 713, 'day2'),
        ('ibm_kingston', 721, 'day2'), ('ibm_kingston', 722, 'day2'), ('ibm_kingston', 723, 'day2'),
        ('ibm_phoenix', 751, 'day2'), ('ibm_phoenix', 752, 'day2'), ('ibm_phoenix', 753, 'day2'),
        ('ibm_aachen', 841, 'oct6'), ('ibm_aachen', 842, 'oct6'), ('ibm_aachen', 843, 'oct6')]


def proj(x, c0, d):
    return np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2


def load(chip, run):
    D = os.path.join(FIRE, chip)
    m = json.load(open(os.path.join(D, f'run{run}_meta.json')))
    assert m.get('complete') is True
    z = np.load(os.path.join(D, f'run{run}_results.npz'))
    return m, {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}


def pack(A, zero, one, keys):
    """keys: output name -> raw key. zero/one: raw keys of the |0> and |1> reference readouts."""
    c0 = A[zero].mean(0); d = A[one].mean(0) - c0
    sep = np.abs(d) / np.sqrt((np.abs(A[zero] - c0) ** 2).mean(0) / 2)
    g = np.where(sep > 4)[0]
    out = {'qubits': [int(i) for i in g]}
    for name, k in keys.items():
        p = proj(A[k], c0, d)
        out[name] = [round(float(v), 7) for v in p.mean(0)[g]]
        out['se_' + name] = [round(float(v), 7) for v in (p.std(0, ddof=1) / np.sqrt(p.shape[0]))[g]]
    return out, A[zero].shape[0]


def main():
    runs = []
    for chip, run, day in RUNS:
        m, A = load(chip, run)
        keys = {'N2': 'OFF|N2', 'N6': 'OFF|N6', 'N10': 'OFF|N10', 'R30': 'RULER|ON|n30', 'R90': 'RULER|ON|n90', 'R300': 'RULER|ON|n300'}
        d, shots = pack(A, 'OFF|p0', 'ON|p0', keys)
        d.update(chip=chip, run=run, day=day, job_id=m.get('job_id'), started=m.get('start_time'), shots=shots, n_chip_qubits=m.get('n_chip_qubits'))
        runs.append(d)
    # Pittsburgh, 2 Oct (different job layout: frame references F0/F1, arms N2 / N6 / A30_30 = 2 / 6 / 10 pushes, 30 us apart)
    m, A = load('ibm_pittsburgh', 121)
    keys = {'N2': 'N2', 'N6': 'N6', 'N10': 'A30_30', 'R30': 'R30', 'R90': 'R90', 'R300': 'R300'}
    d, shots = pack(A, 'F0', 'F1', keys)
    d.update(chip='ibm_pittsburgh', run=121, day='day1', job_id=m.get('job_id'), started=m.get('start_time'), shots=shots, n_chip_qubits=m.get('n_chip_qubits'),
             note='Pittsburgh job has a different arm layout; 216 shots; ruler level clipped to [0.02, 1.2] in the original reader (own-interval), see README')
    runs.append(d)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'about': 'per-qubit levels for the gate-cost (spaced X-gate train) finding; see README.md', 'runs': runs}, open(OUT, 'w'), separators=(',', ':'))
    print('wrote', OUT, os.path.getsize(OUT), 'bytes,', len(runs), 'runs')


if __name__ == '__main__':
    main()
