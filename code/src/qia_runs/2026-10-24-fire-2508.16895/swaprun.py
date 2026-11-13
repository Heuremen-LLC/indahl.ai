"""swaprun.py -- free calibration run for arXiv 2508.16895v2 (Chan, Smith, Gabriel; "Quantum State Fidelity for Functional Neural Network
Construction"), the Ang circuit: angle embedding (one RX layer per 9-value tuning curve) on two 9-qubit registers, CNOT(i -> 9+i), H on
register 1, all 18 qubits measured; fidelity estimate F^ = mean over shots of (-1)^(sum_i s_i t_i) (their Sec. II C 1, ref [9]).
Exact value of this circuit: |<a|b>|^2 = prod_i cos^2((a_i - b_i)/2).  My own builder (their code never run); inputs = their released
data_tuning-curves_rescaled.csv (data only).  Fixed before any job (PLAN_SWAP.md.text)."""
import csv, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); THEIRS = os.path.join(HERE, 'src', 'theirs')
SHOTS = 1000; COPIES = 2; NQ = 9; SEED = 2508168950; TSEED = 1689
T99 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169, 11: 3.106, 12: 3.055, 13: 3.012, 19: 2.861}
SCALE = {'IDENT': 0.10, 'ORTHO': 0.10, 'THEIRS': 0.10, 'COPY': 0.05}
def curves(path=None):
    r = list(csv.reader(open(path or os.path.join(THEIRS, 'data_tuning-curves_rescaled.csv'))))
    return {int(float(x[0])): np.array([float(v) for v in x[1:]]) for x in r[1:]}
def exact(a, b): return float(np.prod(np.cos((np.asarray(a) - np.asarray(b)) / 2) ** 2))
def build(a, b, name='swap'):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2 * NQ, 2 * NQ, name=name)
    for i, x in enumerate(a): qc.rx(float(x), i)
    for i, x in enumerate(b): qc.rx(float(x), NQ + i)
    for i in range(NQ): qc.cx(i, NQ + i)
    for i in range(NQ): qc.h(i)
    qc.measure(range(2 * NQ), range(2 * NQ))
    return qc
def ortho(k):
    """constructed orthogonal pairs (NOT their data): delta tuning curves pi on one tone each, sums = pi as their L1 rescale; |<a|b>|^2 = 0"""
    P = [(0, 1), (2, 6), (4, 8), (3, 7)][k]; a = np.zeros(NQ); b = np.zeros(NQ); a[P[0]] = np.pi; b[P[1]] = np.pi; return a, b
def select(tc):
    """20 pairs, deterministic: 4 IDENT (a = b, exact 1; neurons by seed), 4 ORTHO (constructed, exact 0), 12 THEIRS (their distinct pairs:
    6 lowest exact overlap + 6 at exact-overlap quantiles 10/28/46/64/82/97 %)."""
    rng = np.random.default_rng(SEED); ids = sorted(tc)
    out = [dict(cls='IDENT', A=int(n), B=int(n), a=tc[n], b=tc[n]) for n in sorted(rng.choice(ids, 4, replace=False))]
    out += [dict(cls='ORTHO', A=-1 - k, B=-1 - k, a=ortho(k)[0], b=ortho(k)[1]) for k in range(4)]
    pairs = sorted(((exact(tc[a], tc[b]), a, b) for i, a in enumerate(ids) for b in ids[i + 1:]))
    pick = [pairs[i] for i in range(6)] + [pairs[int(q * (len(pairs) - 1))] for q in (0.10, 0.28, 0.46, 0.64, 0.82, 0.97)]
    out += [dict(cls='THEIRS', A=int(a), B=int(b), a=tc[a], b=tc[b]) for _, a, b in pick]
    for p in out: p['F'] = exact(p['a'], p['b'])
    return out
def parity_table():
    idx = np.arange(2 ** (2 * NQ)); return (-1.0) ** sum(((idx >> k) & 1) * ((idx >> (k + NQ)) & 1) for k in range(NQ))
def fhat(counts):
    """counts: {bitstring (Qiskit order, clbit 0 rightmost) or int: count} -> (F^, shots). Pair k = (clbit k, clbit 9+k)."""
    n = 0; s = 0
    for k, v in counts.items():
        i = int(k, 2) if isinstance(k, str) else int(k)
        par = sum(((i >> j) & 1) * ((i >> (j + NQ)) & 1) for j in range(NQ)); s += v * (-1) ** par; n += v
    return s / n, n
def reading(d, shot_var, n_shots, scale):
    """d: per-pair values (copy-averaged deviations); shot_var: per-pair shot variance of the copy-average. Mean, SE = max(sd/sqrt(n),
    sqrt(mean shot var / n)), t(n-1) at 99 %; outcome ABOVE lo > 0, BELOW hi < 0, CONSISTENT 0 inside and half <= scale, else CANNOT_TELL."""
    d = np.asarray(d, float); n = len(d); m = float(d.mean())
    se = max(float(d.std(ddof=1)) / np.sqrt(n) if n > 1 else np.inf, float(np.sqrt(np.mean(shot_var) / n))); h = T99[n - 1] * se
    lo, hi = m - h, m + h
    out = 'CANNOT_TELL' if n_shots < 0.9 * SHOTS else 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT' if h <= scale else 'CANNOT_TELL'
    return dict(value=m, lo=lo, hi=hi, half=h, n=n, outcome=out)
def readings(pairs, F):
    """pairs: list from select(); F: array [pair, copy] of F^; returns the four scored readings (fixed before any job)."""
    F = np.asarray(F, float); ex = np.array([p['F'] for p in pairs]); cls = np.array([p['cls'] for p in pairs]); fm = F.mean(1)
    var = (1 - np.clip(F, -1, 1) ** 2).mean(1) / SHOTS / F.shape[1]; R = {}
    for c in ('IDENT', 'ORTHO', 'THEIRS'):
        k = cls == c; R[c] = reading(fm[k] - ex[k], var[k], SHOTS, SCALE[c])
    R['COPY'] = reading(F[:, 1] - F[:, 0], 2 * var * F.shape[1], SHOTS, SCALE['COPY'])
    return R
