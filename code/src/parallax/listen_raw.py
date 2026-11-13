"""THE ODD HALF, raw -- 2026-09-28. No guess. Every odd qubit on Fez (the half nobody looked at today), plain Ramsey all at once,
12 waits, X and Y. Readout kept as RAW DOTS (kerneled I/Q) -- the chip's own 0/1 call is a ruler too, so we don't let it make it.
Two reference circuits (all at 0, all flipped to 1) so the dots have somewhere to sit."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
WAITS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]; SHOTS = 2000
def circ(nq, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(nq, 'q'); m = ClassicalRegister(nq, 'm1'); c = QuantumCircuit(q, m)
    if quad in ('P0', 'P1'):
        if quad == 'P1': c.x(q)
        c.measure(q, m); return c
    c.h(q); c.barrier()
    if w: c.delay(w * 1000, q, unit='ns')
    c.barrier()
    if quad == 'Y': c.sdg(q)
    c.h(q); c.measure(q, m); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    sv, be = P.chip(keyfile, backend); t = be.target
    if sv.usage().get('usage_remaining_seconds', 0) < 40: sys.exit('BRAKE')
    Q = [q for q in range(1, be.num_qubits, 2) if t['measure'].get((q,)) is not None and t['x'].get((q,)) is not None]
    spec = [(0, 'P0'), (0, 'P1')] + [(w, qd) for w in WAITS for qd in ('X', 'Y')]
    circs = [transpile(circ(len(Q), w, qd), backend=be, initial_layout=Q, optimization_level=0) for w, qd in spec]
    sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.max_execution_time = 60
    j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), len(Q), 'odd qubits', flush=True); r = j.result()
    d = os.path.join(P.HERE, 'out', 'oddraw_' + backend + '_' + time.strftime('%H%M%S')); os.makedirs(d)
    np.savez_compressed(os.path.join(d, 'raw.npz'), **{f'{qd}_{w}': np.asarray(r[k].data.m1) for k, (w, qd) in enumerate(spec)})
    json.dump({'job': j.job_id(), 'backend': backend, 'qubits': Q, 'waits_us': WAITS, 'spec': spec}, open(os.path.join(d, 'meta.json'), 'w'))
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
