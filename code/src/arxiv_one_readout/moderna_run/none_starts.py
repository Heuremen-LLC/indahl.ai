"""none_starts.py -- how many random starts of plain single-bit-flip descent find the exact optimum, per instance (defined after
none_test.text was read: it measures the effort, not a new pass/fail). Same generator and seed as none_test.py; also 133 and 150
variables (the 2025 paper's hardware sizes)."""
import sys, time, numpy as np
sys.path.insert(0, '.'); import mrna_qubo as M
rng = np.random.default_rng(2024)
def find(nvar, tries=20000):
    for _ in range(tries):
        L = int(rng.integers(20, 80)); s = M.random_seq(L, rng); Q, h, J = M.build(s)
        if len(Q) == nvar: return s, h, J
for nvar in (26, 40, 50, 80, 133, 150):
    need, secs, n_ok = [], [], 0
    for k in range(12):
        f = find(nvar)
        if f is None: continue
        s, h, J = f; Eopt, xopt, st = M.exact(h, J)
        if st != 0: continue
        n_ok += 1; t0 = time.time(); found = None
        for i in range(1, 100001):
            x = M.local_search(h, J, rng.integers(0, 2, nvar) * (rng.random(nvar) < 0.2), rng)
            if M.energy(x, h, J) <= Eopt + 1e-9: found = i; break
        need.append(found if found else np.inf); secs.append(time.time() - t0)
    need = np.array(need, float)
    print(f'{nvar:3d} variables, {n_ok} sequences: starts to the exact optimum median {np.median(need):.0f}, max {np.max(need):.0f}, '
          f'found in {int(np.isfinite(need).sum())} of {n_ok} within 100,000 starts | laptop seconds median {np.median(secs):.3f}, max {np.max(secs):.2f}', flush=True)
