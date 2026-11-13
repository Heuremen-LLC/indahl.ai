"""known_good_aqcel.py -- their released numbers reproduced from their released outputs through OUR committed rebuild (zero QPU).
Their released outputs used (printed in tutorial_aqcel.ipynb at tag v2.0.0, run by them with their code on AerSimulator; and Table 2 of v4):
  ideal 1-step distribution printed twice at 10k shots: {001101 .0972, 001100 .6312, 000101 .1307, 000100 .1409} and
                                                        {001101 .0994, 000101 .1319, 001100 .6350, 000100 .1337}
  Aqcel-v2 thr 0.05 -> 11 CX (AerSimulator opt 3, .decompose()), F_sim 0.9598 and 0.9629 (10k shots each)
  Table 2 ideal topology: Qiskit 115; Aqcel-v1 41 (thr 0.01), 23 (0.05); Aqcel-v2 25 (0.01), 11 (0.05)
PASS RULE (fixed in the plan): ideal distribution chi2 p > 0.001 against BOTH printed 10k-shot draws; Aqcel-v2 counts exactly 25 and 11;
|F_sim(v2, 0.05) - printed| <= 0.01 for both printed values. Qiskit-only and Aqcel-v1 counts are REPORTED, not in the rule (see plan)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import aqcel_rebuild as A
from scipy.stats import chi2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
PRINTED = [{'001101': .0972, '001100': .6312, '000101': .1307, '000100': .1409}, {'001101': .0994, '000101': .1319, '001100': .6350, '000100': .1337}]
qc = A.qps1(); p = A.ideal_dist(qc)
lines = ['ideal (ours, exact): ' + str({k: round(v, 4) for k, v in sorted(p.items(), key=lambda x: -x[1])})]
ok = True
for i, d in enumerate(PRINTED):
    n = 10000; st = sum((n * d[k] - n * p[k]) ** 2 / (n * p[k]) for k in p); pv = chi2.sf(st, len(p) - 1)
    lines.append(f'printed ideal draw {i + 1}: chi2 {st:.2f} (dof {len(p) - 1}) p = {pv:.3f}'); ok &= pv > 0.001
pm = generate_preset_pass_manager(backend=AerSimulator(), optimization_level=3)
cx = lambda c: pm.run(c).decompose().count_ops().get('cx')
res = {}
for thr in (0.01, 0.05):
    for v in (1, 2):
        q, nm, npair = A.aqcel(qc, thr, v); res[(v, thr)] = (cx(q), A.hellinger_fidelity(p, A.ideal_dist(q)), nm, npair)
printed_cx = {(1, .01): 41, (1, .05): 23, (2, .01): 25, (2, .05): 11}
lines.append(f'Qiskit-only (original) CX: ours {cx(qc)}  printed 115  [reported, not in rule: Qiskit 2.5.2 here vs 1.2.2 / 2.3.0 theirs]')
for k, (c, f, nm, npair) in res.items():
    lines.append(f'Aqcel-v{k[0]} thr {k[1]}: CX ours {c} printed {printed_cx[k]}; F_sim {f:.4f}; control-state reads {nm}; CX pairs removed {npair}')
ok &= res[(2, .01)][0] == 25 and res[(2, .05)][0] == 11
for fp in (0.9598, 0.9629):
    d = res[(2, .05)][1] - fp; lines.append(f'F_sim v2 0.05: ours {res[(2, .05)][1]:.4f} vs printed {fp} diff {d:+.4f}'); ok &= abs(d) <= 0.01
lines.append('KNOWN-GOOD ' + ('PASS' if ok else 'FAIL'))
lines.append('NOT reproduced (reported): Qiskit-only CX and Aqcel-v1 CX (our exact-probability v1 keeps fewer controls than theirs).')
txt = '\n'.join(lines); print(txt); open(os.path.join(HERE, 'known_good_aqcel.text'), 'w').write(txt + '\n')
