"""Round 14: THE SPLIT -- how the two voices of 143 and 138 divide the shots, and whether a voice lasts from shot to shot."""
import sys, os, json, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
QS = [143, 138]; WAITS = list(range(0, 23)); SHOTS = 1000; MEM = {143: 5500, 138: 3750}; MSHOTS = 4000
def circ(w_ns, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); m = ClassicalRegister(2, 'm'); c = QuantumCircuit(q, m)
    c.h(q); c.barrier()
    for k in (0, 1):
        if w_ns[k]: c.delay(w_ns[k], k, unit='ns')
    c.barrier()
    if quad == 'Y': c.sdg(q)
    c.h(q); c.measure(q, m); return c
def fit(t, z):
    """complex two-tone fit: z(t) = A e^{-t/T} [(1-p) e^{i w1 t} + p e^{i w2 t}]  (t in us, w in rad/us)"""
    from scipy.optimize import least_squares
    best = None
    for gap0 in np.linspace(0.2, 1.2, 11):
        for p0 in (0.2, 0.35, 0.5):
            def res(x):
                A, T, p, w1, w2 = x; m = A * np.exp(-t / T) * ((1 - p) * np.exp(1j * w1 * t) + p * np.exp(1j * w2 * t)); d = m - z
                return np.concatenate([d.real, d.imag])
            w0 = np.angle(z[1] / z[0]) if abs(z[0]) > 0 else 0
            r = least_squares(res, [abs(z[0]), 30, p0, w0, w0 + gap0], bounds=([0, 1, 0, -10, -10], [1.2, 1e4, 0.5, 10, 10]))
            if best is None or r.cost < best.cost: best = r
    A, T, p, w1, w2 = best.x; return {'A': A, 'T2_us': T, 'p_second': p, 'gap_kHz': abs(w2 - w1) / (2 * math.pi) * 1e3, 'cost': best.cost}
def main(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    sv, be = P.chip(keyfile, backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 50: sys.exit('BRAKE')
    spec = [(w, qd) for w in WAITS for qd in ('X', 'Y')]
    circs = [transpile(circ([w * 1000, w * 1000], qd), backend=be, initial_layout=QS, optimization_level=0) for w, qd in spec]
    mem = [transpile(circ([MEM[143], MEM[138]], qd), backend=be, initial_layout=QS, optimization_level=0) for qd in ('X', 'Y')]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 60
    j = sm.run([(c,) for c in circs] + [(c, None, MSHOTS) for c in mem], shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    out = {'job': j.job_id(), 'qubits': QS, 'waits_us': WAITS}
    for k, q in enumerate(QS):
        ex = {}
        for n, (w, qd) in enumerate(spec):
            b = r[n].data.m.get_bitstrings(); ex[(w, qd)] = 1 - 2 * np.mean([int(s[::-1][k]) for s in b])
        z = np.array([ex[(w, 'X')] + 1j * ex[(w, 'Y')] for w in WAITS]); C = np.abs(z); f = fit(np.array(WAITS, float), z)
        ac = []
        for n in (0, 1):
            x = np.array([int(s[::-1][k]) for s in r[len(spec) + n].data.m.get_bitstrings()], float); x -= x.mean()
            ac.append([float((x[:-L] * x[L:]).mean() / x.var()) for L in (1, 2, 4, 16)])
        out[str(q)] = {'C': C.tolist(), 'X': z.real.tolist(), 'Y': z.imag.tolist(), 'fit': f, 'shot_memory_lag_1_2_4_16': ac}
        print(f"q{q}: coherence " + ' '.join(f'{c:.2f}' for c in C))
        print(f"   fit: second voice {f['p_second']:.2f} of shots, gap {f['gap_kHz']:.0f} kHz, fade {f['T2_us']:.0f} us | shot-to-shot memory (lag 1,2,4,16; X then Y): {ac}")
    d = os.path.join(P.HERE, 'out', 'split2_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
