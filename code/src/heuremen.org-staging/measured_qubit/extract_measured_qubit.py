#!/usr/bin/env python3
"""extract_measured_qubit.py -- (maintainer tool; needs numpy and the PRIVATE raw I/Q) reduce the raw look-wide runs to the per-qubit numbers
the estimators use, and write data/measured_qubit.json (+ data/ruler_check.json).  Readers are not expected to run this: verify_measured_qubit.py
needs only the JSON.   python3 extract_measured_qubit.py THREE_POSITIONS_DIR RAW_FIRE_DIR
The level arithmetic is copied from readlook_wide.py / readlook_3and9.py (same clouds, same separation, same final register); nothing is re-fit here."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
TP, FIRE = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
WIN = [0, 10, 20, 30, 60, 120, 240]; LOOKS = [1, 2, 3, 4, 6, 9]; OWN = [10, 20, 40]
RUN0 = {'ibm_marrakesh': 310, 'ibm_kingston': 330, 'ibm_pittsburgh': 350, 'ibm_fez': 410, 'ibm_boston': 430, 'ibm_phoenix': 540, 'ibm_aachen': 800}
runs = {(r['chip'], r['run']): r for r in json.load(open(os.path.join(TP, 'runs.json')))['runs']}
R = lambda x: float(f'{x:.12g}')


def load_wide(chip, r):
    D = os.path.join(FIRE, chip); m = json.load(open(os.path.join(D, f'run{r}_meta.json')))
    assert m.get('complete') is True
    z = np.load(os.path.join(D, f'run{r}_results.npz')); A = {}
    for k in z.files:
        base, reg = k.split('__'); A.setdefault(base, {})[reg] = np.asarray(z[k]).astype(complex)
    return m, {b: v[sorted(v, key=lambda x: int(x[1:]))[-1]] for b, v in A.items()}


out = {'what': 'per-qubit levels from the look-wide runs (reads 1-3 per chip) needed to recompute the measured-qubit time-equivalent', 'looks': LOOKS, 'own_waits_us': OWN, 'clock_windows_us': [0, 10, 20, 30], 'chips': {}}
for chip, r0 in RUN0.items():
    ro = json.load(open(os.path.join(TP, 'data', 'reads', f'lookwide_roles_{chip}.json')))
    mk = json.load(open(os.path.join(TP, 'data', 'reads', f'{chip}_maker_look_length_20261004.json')))
    maker = float(np.median(list(mk['measure_duration_s'].values()))) * 1e6
    WOF = {int(k): v for k, v in ro['witness_of'].items()}
    c = {'maker_us': R(maker), 'maker_file': f'{chip}_maker_look_length_20261004.json', 'reads': {}}
    for k in (1, 2, 3):
        run = r0 + k; m, A = load_wide(chip, run)
        c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0; sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)
        lv = {kk: (np.real((v - c0) * np.conj(d)) / np.abs(d) ** 2).mean(0) for kk, v in A.items()}
        far = {}; clk = {}; seps = {}
        for q in ro['far']:
            seps[str(q)] = R(sep[q])
            far[str(q)] = {'AW': [R(lv[f'AW{t}'][q]) for t in OWN], 'A': [R(lv[f'A{kk}'][q]) for kk in LOOKS]}
        for w, wo in WOF.items():
            seps[str(w)] = R(sep[w]); seps[str(wo)] = R(sep[wo])
            clk[str(w)] = {'witness_of': wo, 'T': {str(t): [R(lv[f'T{t}|X'][w]), R(lv[f'T{t}|Y'][w])] for t in WIN[:4]},
                           'K': {str(kk): [R(lv[f'K{kk}|X'][w]), R(lv[f'K{kk}|Y'][w])] for kk in LOOKS}}
        c['reads'][str(k)] = {'run': run, 'job_id': runs[(chip, run)]['job_id'], 'submitted_at': runs[(chip, run)]['submitted_at'], 'shots': m.get('shots'),
                              'sep': seps, 'far': far, 'clocks': clk}
    out['chips'][chip] = c
json.dump(out, open(os.path.join(OUT, 'measured_qubit.json'), 'w'), separators=(',', ':'))

# ---- ruler check: ON fading at 30 vs the single exponential through 300 us (time_wide runs: RULER|ON|n30|c, n300|c, c = a,b,c)
RW = {'ibm_marrakesh': [301, 302, 303], 'ibm_kingston': [301, 302, 303], 'ibm_pittsburgh': [361, 362, 363], 'ibm_fez': [401, 402, 403], 'ibm_phoenix': [531], 'ibm_aachen': [841, 842, 843], 'ibm_boston': [441]}
rc = {'what': 'time_wide ruler copies: per kept bit (clouds > 4 widths apart) and copy a/b/c, the ON survival after 30 us and after 300 us, as in readtime.py', 'chips': {}}
for chip, rl in RW.items():
    rc['chips'][chip] = {}
    for run in rl:
        D = os.path.join(FIRE, chip); mp = os.path.join(D, f'run{run}_meta.json')
        if not os.path.exists(mp): continue
        z = np.load(os.path.join(D, f'run{run}_results.npz'))
        if 'RULER|ON|n300|a' not in {k.split('__')[0] for k in z.files}: print('no ruler', chip, run); continue
        A = {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}
        c0 = A['OFF|p0'].mean(0); d = A['ON|p0'].mean(0) - c0; sep = np.abs(d) / np.sqrt((np.abs(A['OFF|p0'] - c0) ** 2).mean(0) / 2)
        lv = {k: (np.real((v - c0) * np.conj(d)) / np.abs(d) ** 2).mean(0) for k, v in A.items()}
        g = np.where(sep > 4)[0]
        rc['chips'][chip][str(run)] = {'job_id': runs.get((chip, run), {}).get('job_id'), 'n_bits_total': int(len(sep)),
            'bits': {str(q): {cc: [R(lv[f'RULER|ON|n30|{cc}'][q]), R(lv[f'RULER|ON|n300|{cc}'][q])] for cc in 'abc'} for q in g}, 'sep': {str(q): R(sep[q]) for q in g}}
json.dump(rc, open(os.path.join(OUT, 'ruler_check.json'), 'w'), separators=(',', ':'))
