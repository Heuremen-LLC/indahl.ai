"""THE DO -- 2026-09-28, the five don'ts turned around. Seats 113 and 72 (cursed on all three chips) + 27 (cleanest odd seat).
 order pinned (barriers) | no guess written | raw dots, no fit | every circuit the SAME number of looks | every cut checked on
 half the references before it touches anything else.  Two looks per shot (the morning's parallax): tank or lens?"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
QS = [113, 72, 27]; WAITS = [0, 2, 5, 10, 20]; SHOTS = 4000
def circ(kind, w=0):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(3, 'q'); m1 = ClassicalRegister(3, 'm1'); m2 = ClassicalRegister(3, 'm2'); c = QuantumCircuit(q, m1, m2)
    if kind in ('P1', 'D1'): c.x(q)
    if kind in ('X', 'Y'):
        c.h(q); c.barrier()
        if w: c.delay(w * 1000, q, unit='ns')
        c.barrier()
        if kind == 'Y': c.sdg(q)
        c.h(q)
    c.barrier(); c.measure(q, m1); c.barrier(); c.measure(q, m2); return c     # every circuit looks twice: same ruler everywhere
def main(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    sv, be = P.chip(keyfile, backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 45: sys.exit('BRAKE')
    spec = [('P0', 0), ('P1', 0)] + [(k, w) for w in WAITS for k in ('X', 'Y')]
    circs = [transpile(circ(k, w), backend=be, initial_layout=QS, optimization_level=0) for k, w in spec]
    sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.max_execution_time = 60
    j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    d = os.path.join(P.HERE, 'out', 'the_do_' + time.strftime('%H%M%S')); os.makedirs(d)
    np.savez_compressed(os.path.join(d, 'raw.npz'), **{f'{k}_{w}_{reg}': np.asarray(getattr(r[n].data, reg)) for n, (k, w) in enumerate(spec) for reg in ('m1', 'm2')})
    json.dump({'job': j.job_id(), 'backend': backend, 'qubits': QS, 'waits_us': WAITS, 'spec': spec, 'shots': SHOTS}, open(os.path.join(d, 'meta.json'), 'w'))
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
