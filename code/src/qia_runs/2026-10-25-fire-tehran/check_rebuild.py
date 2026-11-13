"""check_rebuild.py -- (1) our estimators on THEIR released Round 1 counts must give their printed numbers; (2) our rebuilt circuits,
noiseless, must give the exact values of their study (N1 none 0.790 / 0.607, native 1, oracle-like N1corr near 1, probes -> angle 0)."""
import sys, os, json, gzip, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tele import *
from qiskit.quantum_info import Statevector
R = sys.argv[1] + '/data/hardware/ibm_kingston_2026-10-04/'
d = json.load(gzip.open(R + 'counts/db16p1bid5ic73eqnsug.json.gz', 'rt')); ix = json.load(open(R + 'circuits/R1_main_ibm_kingston.json'))['index']
sh = {}
for p in d['pubs']:
    labs = ix[p['label']]; regs = list(p['shots_int']); multi = isinstance(p['shots_int'][regs[0]][0], list)
    for i, l in enumerate(labs): sh[l] = {r: (p['shots_int'][r][i] if multi else p['shots_int'][r]) for r in regs}
out = {'theirs_data': {}, 'noiseless': {}}
for blk, st in [('R1_nativeA', 'product_HT'), ('R1_nativeA', 'bell_30_70'), ('R1_N1none', 'product_HT'), ('R1_N1none', 'bell_30_70')]:
    t = tables({b: (sh[f'{blk}_{st}_{b}']['alice'], sh[f'{blk}_{st}_{b}']['bob']) for b in BASES9})
    out['theirs_data'][f'{blk}_{st}'] = round(lin_F(t, message_state(st)), 4)
pt = {}
for j in range(3):
    for name, ax in PROBES:
        e = sh[f'R1_fp_tomo9_s{j}_{ax}']; pt[f'probe_s{j}_{ax}'] = np.bincount(frame_keys(e['alice'], e['bob'], ax * 2), minlength=4)
out['theirs_data']['fingerprint_rad'] = {k: round(v, 4) for k, v in fingerprint(pt).items()}
def exact_tabs(qc, shots=None):
    q = qc.copy_empty_like(); [q.append(ins) for ins in qc.data if ins.operation.name != 'measure']; q.remove_final_measurements(); pr = Statevector(q).probabilities()   # index bit k = qubit k
    i = np.arange(64); al, bo = i & 15, i >> 4; return al, bo, pr
def exact_counts(qc, bases):
    al, bo, pr = exact_tabs(qc); k = frame_keys(al, bo, bases); return np.array([pr[k == v].sum() for v in range(4)]) * 1e6
for blk in ('native', 'N1none', 'N1corr'):
    for st in ('product_HT', 'bell_30_70'):
        t = {b: exact_counts(c, b) for (_, c), b in zip(block_circuits(blk, st), BASES9)}
        out['noiseless'][f'{blk}_{st}'] = round(lin_F(t, message_state(st)), 6)
pc = {l: exact_counts(c, l.split('_')[-1] * 2) for l, c in probe_circuits()}
out['noiseless']['fingerprint_rad'] = {k: round(v, 6) for k, v in fingerprint(pc).items()}
out['their_printed'] = dict(R1_nativeA=[0.8751, 0.8608], R1_N1none=[0.7109, 0.5217], fingerprint=[0.1084, 0.1593], noiseless_N1none=[0.790, 0.607])
print(json.dumps(out, indent=1)); open('check_rebuild.text', 'w').write(json.dumps(out, indent=1))
