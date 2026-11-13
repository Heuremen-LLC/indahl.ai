#!/usr/bin/env python3
"""build_cost_data.py -- PROVENANCE ONLY (needs numpy and the private shot data; verify_cost.py does not).

Reduces the raw IBM shot files to the compact JSON in data/. Run once, read-only on the source tree:
    /Users/heuremen/bones-forge/venv_quantum/bin/python build_cost_data.py
Source: parallax/out/qubit_fifth_run/data/fire/<chip>/run<N>_results.npz (complex readout points,
shots x qubits per circuit) and run<N>_job.json (IBM job id).  The reduction is the one in
read_the_count.py / readwitness_wide.py, unchanged:
  level of a qubit  = mean over shots of Re[(z - c0) conj(d)] / |d|^2, with c0 = mean of the all-0 circuit
                      and d = (mean of the all-1 circuit) - c0 (0 = all in ground state, 1 = all excited)
  kept qubit        = the all-0 and all-1 clouds are more than 3 widths apart
  hand of a spectator = (2 lvX - 1) - i (2 lvY - 1), measured on two axes a quarter-turn apart;
                      only |hand(arm) / hand(no wait)| is stored (a clock must start with |hand| > 0.15)

NOTE: the "published_reader_output" block inside fez_count_20261011.json (point widths from 40 shot-level resamplings,
seed 20261011) was added by running read_the_count.py unchanged on the same raw shots; this script does not regenerate it.
"""
import json, os, sys
from collections import deque
import numpy as np
SRC = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def load(chip, r):
    z = np.load(f'{SRC}data/fire/{chip}/run{r}_results.npz'); A = {}
    for k in z.files:
        base, reg = k.split('__'); A.setdefault(base, {})[reg] = np.asarray(z[k]).astype(complex)
    A = {b: v[sorted(v, key=lambda x: int(x[1:]))[-1]] for b, v in A.items()}
    job = json.load(open(f'{SRC}data/fire/{chip}/run{r}_job.json'))
    meta = json.load(open(f'{SRC}data/fire/{chip}/run{r}_meta.json'))
    return A, job, meta

def levels(A):
    c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0
    sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)
    lv = {k: (np.real((v - c0) * np.conj(d)) / np.abs(d) ** 2).mean(0) for k, v in A.items()}
    return sep, lv

def r4(x): return round(float(x), 5)

def build_fez():
    LOOKS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]; WIN = [0, 10, 20, 30, 60, 120, 240]; OWN = [10, 20, 40]
    RO = json.load(open(f'{SRC}data/reads/lookwide_roles_ibm_fez.json'))
    WOF = {int(k): v for k, v in RO['witness_of'].items()}
    jobs = []
    for r in (901, 902, 903):
        A, job, meta = load('ibm_fez', r); sep, lv = levels(A)
        FAR = [q for q in RO['far'] if sep[q] > 3]
        H = {a: (2 * lv[f'{a}|X'] - 1) - 1j * (2 * lv[f'{a}|Y'] - 1) for a in [f'T{t}' for t in WIN] + [f'K{k}' for k in LOOKS]}
        W = [w for w in sorted(WOF) if abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3]
        jobs.append({'run': r, 'job_id': job['job_id'], 'submitted': job['submitted_at'], 'shots': int(meta['shots']),
            'looked_at_bits': [{'qubit': int(q), 'on_after_k_looks': [r4(lv[f'A{k}'][q]) for k in LOOKS],
                                'on_after_plain_wait': [r4(lv[f'AW{t}'][q]) for t in OWN]} for q in FAR],
            'spectators': [{'qubit': int(w), 'hand_after_k_looks': [r4(abs(H[f'K{k}'][w] / H['T0'][w])) for k in LOOKS],
                            'hand_after_laid_wait': [r4(abs(H[f'T{t}'][w] / H['T0'][w])) for t in WIN[1:]]} for w in W]})
    json.dump({'chip': 'ibm_fez', 'date': '2026-10-11', 'look_counts': LOOKS, 'laid_waits_us': WIN[1:], 'own_waits_us': OWN,
               'stated_look_us': 1.66, 'jobs': jobs}, open(os.path.join(OUT, 'fez_count_20261011.json'), 'w'), separators=(',', ':'))

def build_kingston():
    LOOKS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]; WIN = [0, 10, 20, 30, 60, 120]
    RO = json.load(open(f'{SRC}data/reads/countwide_roles_ibm_kingston.json'))
    FAR = set(RO['far']); nb = {q: set() for q in range(RO['n'])}
    for a, b in RO['edges']: nb[a].add(b); nb[b].add(a)
    DIST = {q: 0 for q in FAR}; dq = deque(FAR)
    while dq:
        u = dq.popleft()
        for v in nb[u]:
            if v not in DIST: DIST[v] = DIST[u] + 1; dq.append(v)
    runs = []
    for day, rs in (('2026-10-04', (341, 342, 343)), ('2026-10-06', (761, 762, 763))):
        for r in rs:
            A, job, meta = load('ibm_kingston', r); sep, lv = levels(A)
            H = {a: (2 * lv[f'{a}|X'] - 1) - 1j * (2 * lv[f'{a}|Y'] - 1) for a in [f'T{t}' for t in WIN] + [f'K{k}' for k in LOOKS]}
            ok = [q for q in range(RO['n']) if q not in FAR and sep[q] > 3 and abs(H['T0'][q]) > 0.15 and q in DIST]
            runs.append({'day': day, 'run': r, 'job_id': job['job_id'], 'submitted': job['submitted_at'], 'shots': int(meta['shots']),
                'spectators': [{'qubit': int(q), 'links_to_nearest_measured': int(min(DIST[q], 3)),
                                'hand_after_k_looks': [r4(abs(H[f'K{k}'][q] / H['T0'][q])) for k in LOOKS],
                                'hand_after_laid_wait': [r4(abs(H[f'T{t}'][q] / H['T0'][q])) for t in WIN[1:]]} for q in ok]})
    json.dump({'chip': 'ibm_kingston', 'look_counts': LOOKS, 'laid_waits_us': WIN[1:], 'stated_look_us': 2.18,
               'ledger_measured_look_us': {'2026-10-04': 2.323, '2026-10-06': 2.402}, 'runs': runs},
              open(os.path.join(OUT, 'kingston_spectators_20261004_06.json'), 'w'), separators=(',', ':'))

if __name__ == '__main__':
    build_kingston(); build_fez()
