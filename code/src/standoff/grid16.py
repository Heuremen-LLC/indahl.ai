"""ALL FOUR AT THE GATE -- the 16-arm standoff grid. Bones for Wayfinder, 2026-09-25. SIMULATION ONLY (nothing sent to Braket).

One shared standoff, four switches (2x2x2x2 = 16 arms):
  S  SIX BODIES  n = 6 bodies in the GHZ standoff instead of 3.
  R  RECRUIT     body 0 is measured IN TUNE (X); the rest keep their standoff, its sign steered by that result (feed-forward,
                 done in software: every run is kept). With n = 3 the two left are a Bell pair.
  B  BLONDIE     the last body is measured in X and the run is KEPT ONLY IF it reads + (the rig). Discard rate reported.
  P  PINATA      a common phase THETA on every body still in the standoff (removed bodies are measured first).
                 k bodies left -> the standoff feels k*THETA.
Order in every arm: GHZ(n) -> [R, B remove their bodies: X-basis readout] -> [P: rz(THETA) on the k left] -> X-basis readout.
(Removed bodies are read at the end of the circuit; rz on the others commutes with that, so this is exactly equivalent to
removing them first. No mid-circuit measurement needed on Rigetti.)
ONE observable per arm: E = the X-parity of the k bodies left, times the recruit sign (if R), over the kept runs (if B).
Ideal: E = cos(k * THETA), k = n - R - B. Factorial contrasts (effects coded -1/+1, contrast = sum(sign*E)/8) give main effects,
all interactions, and the four-way S x R x B x P term, each with a bootstrap error bar.

Noise model (assumptions, stated): readout flip 4.2% per qubit (tonight's Cepheus q0: 3.5% / 5.3%), 2-qubit gate
depolarizing 1.5%, 1-qubit 0.1%. Transpiled to Rigetti-native rx / rz / cz.
  ~/bones-forge/qvenv/bin/python grid16.py
"""
import itertools, json, math, time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

THETA = 0.45            # rad per body; chosen so cos(k*THETA) spans k = 1..6 without wrapping past pi
P_READ, P2Q, P1Q = 0.042, 0.015, 0.001
FACTORS = ['S', 'R', 'B', 'P']
PER_TASK, PER_SHOT = 0.30, 0.000425
LEDGER_SPENT, CAP = 65.28, 100.00

def arm_circuit(S, R, B, P):
    n = 6 if S else 3
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1): qc.cx(i, i + 1)
    removed = ([0] if R else []) + ([n - 1] if B else [])
    left = [q for q in range(n) if q not in removed]
    if P:
        for q in left: qc.rz(THETA, q)
    for q in range(n): qc.h(q)          # every body read in X (removed ones too -- that IS their removal)
    qc.measure(range(n), range(n))
    return qc, n, left, removed

def observable(counts, n, left, R, B):
    """returns (E, kept_fraction, per-shot values for bootstrap)"""
    vals = []; tot = 0
    for key, v in counts.items():
        b = [int(key[-1 - i]) for i in range(n)]; tot += v
        if B and b[n - 1] == 1: continue                   # Blondie: keep only runs where the last body reads +
        par = (-1) ** (sum(b[q] for q in left) % 2)
        if R: par *= (-1) ** b[0]                          # recruit steers the sign
        vals += [par] * v
    vals = np.array(vals, dtype=float)
    return (vals.mean() if len(vals) else float('nan')), len(vals) / tot, vals

def noise_model():
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(P2Q, 2), ['cz'])
    nm.add_all_qubit_quantum_error(depolarizing_error(P1Q, 1), ['rx'])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - P_READ, P_READ], [P_READ, 1 - P_READ]]))
    return nm

def contrasts(E):
    """E: dict arm-tuple -> value. Returns every factorial contrast (main, 2-, 3-, 4-way)."""
    out = {}
    for r in range(1, 5):
        for combo in itertools.combinations(range(4), r):
            s = 0.0
            for arm, e in E.items():
                sign = 1
                for i in combo: sign *= (1 if arm[i] else -1)
                s += sign * e
            out[''.join(FACTORS[i] for i in combo)] = s / 8
    return out

def run(sim, shots, seed=212):
    arms = list(itertools.product([0, 1], repeat=4))
    circs, meta = [], []
    for arm in arms:
        qc, n, left, removed = arm_circuit(*arm); circs.append(qc); meta.append((n, left, removed))
    tq = transpile(circs, basis_gates=['rx', 'rz', 'cz', 'measure'], optimization_level=1, seed_transpiler=7)
    res = sim.run(tq, shots=shots, seed_simulator=seed).result()
    E, kept, vals = {}, {}, {}
    for i, arm in enumerate(arms):
        n, left, _ = meta[i]
        E[arm], kept[arm], vals[arm] = observable(res.get_counts(i), n, left, arm[1], arm[2])
    return E, kept, vals, tq

def bootstrap(vals, reps=400, seed=7):
    rng = np.random.default_rng(seed); draws = []
    for _ in range(reps):
        Eb = {arm: rng.choice(v, size=len(v), replace=True).mean() for arm, v in vals.items()}
        draws.append(contrasts(Eb))
    return {k: float(np.std([d[k] for d in draws])) for k in draws[0]}

def ideal_E(arm):
    S, R, B, P = arm; k = (6 if S else 3) - R - B
    return math.cos(k * THETA) if P else 1.0

def main():
    arms = list(itertools.product([0, 1], repeat=4))
    ideal = contrasts({a: ideal_E(a) for a in arms})
    print('IDEAL (analytic, E = cos(k*THETA)):  four-way SRBP = %+.4f' % ideal['SRBP'])
    print('  all contrasts:', ' '.join(f'{k}={v:+.3f}' for k, v in ideal.items()))
    out = {'made': time.strftime('%Y-%m-%dT%H:%M:%S'), 'theta': THETA, 'noise': {'readout': P_READ, 'p2q': P2Q, 'p1q': P1Q},
           'ideal': ideal, 'runs': {}}
    noisy = AerSimulator(noise_model=noise_model())
    for shots in (1000, 3000):
        E, kept, vals, tq = run(noisy, shots)
        c = contrasts(E); err = bootstrap(vals)
        print(f'\nNOISY, {shots} shots/arm:  four-way SRBP = {c["SRBP"]:+.4f} +/- {err["SRBP"]:.4f}   (ideal {ideal["SRBP"]:+.4f})')
        print('  per arm (S R B P: E, kept):')
        for a in arms: print(f'    {a}: E {E[a]:+.3f} (ideal {ideal_E(a):+.3f})  kept {kept[a]:.0%}')
        print('  contrasts +/- 1 sigma:', ' '.join(f'{k}={v:+.3f}+/-{err[k]:.3f}' for k, v in c.items()))
        out['runs'][shots] = {'E': {str(a): E[a] for a in arms}, 'kept': {str(a): kept[a] for a in arms},
                              'contrasts': c, 'sigma': err}
    # shots needed: sigma(SRBP) scales 1/sqrt(N); resolve 0.05 at 3 sigma
    s3000 = out['runs'][3000]['sigma']['SRBP']; target = 0.05 / 3
    need = int(math.ceil(3000 * (s3000 / target) ** 2))
    print(f'\nshots/arm to resolve a 0.05 four-way term at 3 sigma: {need}  (sigma at 3000 = {s3000:.4f})')
    print('\nBRAKET COST (16 tasks, one circuit per arm)   ledger $%.2f of $%.2f' % (LEDGER_SPENT, CAP))
    table = []
    for N in (1000, 3000, need, 10000):
        cost = 16 * (PER_TASK + N * PER_SHOT); fits = LEDGER_SPENT + cost <= CAP
        table.append({'shots': N, 'cost': round(cost, 2), 'fits': fits})
        print(f'  {N:>6} shots/arm  ${cost:6.2f}   {"fits" if fits else "DOES NOT FIT"} (total ${LEDGER_SPENT + cost:.2f})')
    out['shots_needed_3sigma_0p05'] = need; out['cost_table'] = table
    json.dump(out, open('grid16_results.json', 'w'), indent=1)
    print('\nreceipts: grid16_results.json')

if __name__ == '__main__':
    main()
