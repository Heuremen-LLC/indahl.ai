"""known_good.py -- zero-QPU seat for arXiv 2603.13536v1.  No hardware counts, job ids or tabulated values are released (Fig. 1-5 are
plots; the repo holds code only), so the paper's numbers cannot be reproduced from data.  What CAN be checked through my committed code:
 (1) my Hamiltonian equals Qiskit's SparsePauliOp matrix of the same terms (the operator the circuits evolve under);
 (2) the paper's PRINTED statements for its exact-contamination protocol (main.py: seeds s+100, shot seeds s+200, eta = 0.2, 5 seeds;
     paper text: 2000 shots, and 3000 for Fig. 1): "For small systems like n=8 ... both Random SQD and AS-SQD attain near
     machine-precision agreement"; "Standard SQD errors increase rapidly with n"; "AS-SQD consistently achieves the best accuracy
     across all evaluated sizes".  PASS rule (fixed before running): n=8 median error of Random and AS-SQD < 1e-8; at n=10 and 12
     median AS < median Random < median Standard; Standard median increases with n.
 (3) dimension check for their hardware n=8 line ("AS-SQD at n=8 identified and converged precisely to the true ground state (error
     ~10^-14)"): AS-SQD started from 3000 UNIFORMLY RANDOM bitstrings (no device, no circuit) at n=8 -- descriptive.
Usage: python -I src/known_good.py  (writes known_good_2603.13536.text)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from assqd import *

out = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)

# (1) operator check
for n in (8, 12):
    M = Model(n, 100); op = sparse_pauli_op(n, M.terms).to_matrix(sparse=True)
    p(f'(1) n={n} seed 100: max |my H - SparsePauliOp H| = {abs(op - M.H).max():.2e}; E0 = {M.E0:.6f}, E1 = {M.E1:.6f}')

# (2) printed statements, exact-contamination protocol
res = {}
for shots in (2000, 3000):
    for n in (8, 10, 12):
        e = {'standard': [], 'random': [], 'en': []}; t0 = time.time()
        for s in range(5):
            M = Model(n, s + 100); pr = 0.8 * M.p0 + 0.2 * M.p1
            c = sample(np.random.default_rng(s + 200), pr, shots)
            for m in e: e[m].append(abs(run(M, c, m, rng=np.random.default_rng(1000 + s))[0] - M.E0))
        res[(shots, n)] = {m: float(np.median(v)) for m, v in e.items()}
        p(f'(2) shots {shots} n={n}: median |E-E0| standard {res[(shots,n)]["standard"]:.3e}  random {res[(shots,n)]["random"]:.3e}  '
          f'AS-SQD {res[(shots,n)]["en"]:.3e}   per-seed AS {["%.1e" % x for x in e["en"]]}  random {["%.1e" % x for x in e["random"]]}  ({time.time()-t0:.1f} s)')
ok = True
for shots in (2000, 3000):
    r = res
    a = r[(shots, 8)]['random'] < 1e-8 and r[(shots, 8)]['en'] < 1e-8
    b = all(r[(shots, n)]['en'] < r[(shots, n)]['random'] < r[(shots, n)]['standard'] for n in (10, 12))
    c = r[(shots, 8)]['standard'] < r[(shots, 10)]['standard'] < r[(shots, 12)]['standard']
    p(f'(2) shots {shots}: n=8 both near machine precision {a}; AS < Random < Standard at n=10,12 {b}; Standard grows with n {c}')
    ok &= a and b and c
p(f'(2) KNOWN-GOOD (printed statements of the exact-contamination protocol): {"PASS" if ok else "FAIL"}')

# (3) n=8 from uniform random strings
e = []
for s in range(5):
    M = Model(8, s + 100); c = sample(np.random.default_rng(s + 300), np.ones(256), 3000)
    E, Sa = run(M, c, 'en'); e.append(abs(E - M.E0)); n_s = len(Sa)
p(f'(3) n=8, AS-SQD from 3000 uniform random strings (no device): |E-E0| per seed {["%.1e" % x for x in e]}; final subspace {n_s} of 256')
er = []
for s in range(5):
    M = Model(8, s + 100); c = sample(np.random.default_rng(s + 300), np.ones(256), 3000)
    er.append(abs(run(M, c, 'random', rng=np.random.default_rng(s))[0] - M.E0))
p(f'(3) n=8, Random SQD from the same uniform strings: |E-E0| per seed {["%.1e" % x for x in er]}')
p('(3) reading: H conserves total Z, so AS-SQD (candidates from the dominant support only) cannot leave the Z-sector its restricted ground vector sits in; '
  'from uniform strings it reaches E0 at n=8 only when that sector is the ground sector. The n=8 hardware "~1e-14" is reachable by dimension, not guaranteed by it.')
# (4) zero QPU: does the rebuilt circuit (noiseless) carry ground-state information at n=12?
from circuits import trotter, ideal_probs, T0, T1
for s in range(100, 110):
    M = Model(12, s); i0 = ideal_probs(trotter(12, M.terms, T0)); i1 = ideal_probs(trotter(12, M.terms, T1))
    p(f'(4) n=12 seed {s}: noiseless circuit overlap sum_b p_circ(b) |psi0(b)|^2: t=0.6 {i0 @ M.p0:.6f}, t=1.2 {i1 @ M.p0:.6f}; uniform {1/4096:.6f}; '
      f'circuit weight in the ground-state sector (6 ones) t=0.6 {i0[[bin(b).count("1") == 6 for b in range(4096)]].sum():.4f} (binomial 924/4096 = {924/4096:.4f})')
open(os.path.join(HERE, '..', 'known_good_2603.13536.text'), 'w').write('\n'.join(out) + '\n')
