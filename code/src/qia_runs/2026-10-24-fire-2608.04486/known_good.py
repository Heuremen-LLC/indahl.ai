"""known_good.py -- zero-QPU KNOWN-GOOD: (a) their printed hardware numbers recomputed from their released kingston_device_N3.json;
(b) their printed construction facts (exact Var 240 / 0, 128 terms in 39 QWC groups, 136 in 41) from OUR rebuild pds.py."""
import sys, os, json, math, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); import pds
from qiskit.quantum_info import SparsePauliOp, Operator
d = json.load(open(os.path.join(H, 'src', 'kingston_device_N3.json'))); s = {x['kind']: x for x in d['states']}
def var(x): return x['C2sq'] - x['C2'] ** 2, math.hypot(x['C2sq_err'], 2 * x['C2'] * x['C2_err'])
vm, em = var(s['mixed']); vs, es = var(s['solvable'])
rows = [('mixed Var C2 (printed 236 +- 78)', vm, em, abs(vm - 236) < 0.5 and abs(em - 78) < 0.5),
        ('solvable Var C2 (printed 36 +- 136)', vs, es, abs(vs - 36) < 0.5 and abs(es - 136) < 0.5),
        ('ratio (printed 6.6)', vm / vs, None, abs(vm / vs - 6.6) < 0.05),
        ('direct difference sigma (printed ~1.3)', (vm - vs) / math.hypot(em, es), None, abs((vm - vs) / math.hypot(em, es) - 1.3) < 0.05),
        ('mixed nonzero sigma (printed ~3)', vm / em, None, abs(vm / em - 3) < 0.1)]
nq, Ce, ex = pds.exemplars(3)
A = SparsePauliOp.from_operator(Operator(Ce)).simplify(); B = SparsePauliOp.from_operator(Operator(Ce @ Ce)).simplify()
gA, gB = len(A.group_commuting(qubit_wise=True)), len(B.group_commuting(qubit_wise=True))
rows += [('rebuild: mixed k=0 exact Var (printed 240)', ex[0]['lv'], None, abs(ex[0]['lv'] - 240) < 1e-6),
         ('rebuild: mixed k=0 is |0000> (printed)', float(abs(ex[0]['w'][0])), None, abs(abs(ex[0]['w'][0]) - 1) < 1e-9),
         ('rebuild: solvable k=1 exact Var (printed 0; released exact_labvar 2.3e-12)', ex[1]['lv'], None, abs(ex[1]['lv']) < 1e-6),
         ('rebuild: C2 terms/groups (printed 128 in 39)', len(A) * 1000 + gA, None, (len(A), gA) == (128, 39)),
         ('rebuild: C2^2 terms/groups (printed 136 in 41)', len(B) * 1000 + gB, None, (len(B), gB) == (136, 41))]
ok = all(r[3] for r in rows)
for n, v, e, p in rows: print(('PASS ' if p else 'FAIL ') + n + ': ' + ('%.4f' % v) + ('' if e is None else ' +- %.3f' % e))
print('KNOWN-GOOD', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
