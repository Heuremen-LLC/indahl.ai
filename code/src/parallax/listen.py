"""THE LISTEN -- 2026-09-28, Wayfinder: "have you tried even once to send a run without a pre-registered hypothesis?" No. So: no
question, no prediction. Every even qubit on the chip (the parallax set), plain Ramsey all at once, 12 waits, read X and Y. Save
everything raw; afterwards, just look at who does what."""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
WAITS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]; SHOTS = 2000
def circ(nq, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(nq, 'q'); m = ClassicalRegister(nq, 'm'); c = QuantumCircuit(q, m)
    c.h(q); c.barrier()
    if w: c.delay(w * 1000, q, unit='ns')
    c.barrier()
    if quad == 'Y': c.sdg(q)
    c.h(q); c.measure(q, m); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile; import numpy as np
    sv, be = P.chip(keyfile, backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 60: sys.exit('BRAKE')
    Q = P.qubits(be); spec = [(w, qd) for w in WAITS for qd in ('X', 'Y')]
    circs = [transpile(circ(len(Q), w, qd), backend=be, initial_layout=Q, optimization_level=0) for w, qd in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 60; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), len(Q), 'qubits', flush=True); r = j.result()
    E = {}
    for k, (w, qd) in enumerate(spec):
        bits = np.array([[int(b) for b in s[::-1]] for s in r[k].data.m.get_bitstrings()])   # column i = qubit Q[i]
        E[(w, qd)] = 1 - 2 * bits.mean(0)
    C = np.array([[math.hypot(E[(w, 'X')][i], E[(w, 'Y')][i]) for w in WAITS] for i in range(len(Q))])
    d = os.path.join(P.HERE, 'out', 'listen_' + backend + '_' + time.strftime('%H%M%S')); os.makedirs(d)
    json.dump({'job': j.job_id(), 'backend': backend, 'qubits': Q, 'waits_us': WAITS, 'C': C.tolist(),
               'X': {str(w): E[(w, 'X')].tolist() for w in WAITS}, 'Y': {str(w): E[(w, 'Y')].tolist() for w in WAITS}}, open(os.path.join(d, 'raw.json'), 'w'))
    print('waits us:', ' '.join(f'{w:>4}' for w in WAITS))
    for i, q in enumerate(Q): print(f'q{q:<4}', ' '.join(f'{c:4.2f}' for c in C[i]))
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
