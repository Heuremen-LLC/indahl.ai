"""SKIP A STONE -- 2026-09-28, first-edition crazy hats, no outcomes written. A straight chain of seven clean Fez qubits,
104-105-106-[107]-108-109-110. Everyone in superposition. The middle one (the stone) gets LOOKED AT. The other six (the pond,
1, 2 and 3 steps out each side) are only read afterwards. Two ways: the stone looked at FIRST (before the pond is read), or LAST
(after). Same idle time both ways. Raw dots. Nothing predicted."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
CHAIN = [104, 105, 106, 107, 108, 109, 110]; STONE = 3; POND = [0, 1, 2, 4, 5, 6]; WAITS = [0, 5]; SHOTS = 4000; MEAS_NS = 1660
def circ(kind, w=0, quad='X'):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(7, 'q'); s = ClassicalRegister(1, 's'); b = ClassicalRegister(6, 'b'); c = QuantumCircuit(q, s, b)
    if kind in ('P0', 'P1'):
        if kind == 'P1': c.x(q)
        c.measure(q[STONE], s[0]); c.measure([q[k] for k in POND], b); return c
    c.h(q); c.barrier()
    if kind == 'first': c.measure(q[STONE], s[0])
    else: c.delay(MEAS_NS, q[STONE], unit='ns')
    c.barrier()
    if w: c.delay(w * 1000, q, unit='ns')
    c.barrier()
    for k in POND:
        if quad == 'Y': c.sdg(q[k])
        c.h(q[k])
    c.measure([q[k] for k in POND], b)
    if kind == 'last': c.barrier(); c.measure(q[STONE], s[0])
    return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    sv, be = P.chip(keyfile, backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 40: sys.exit('BRAKE')
    spec = [('P0', 0, '-'), ('P1', 0, '-')] + [(k, w, qd) for k in ('first', 'last') for w in WAITS for qd in ('X', 'Y')]
    circs = [transpile(circ(k, w, qd), backend=be, initial_layout=CHAIN, optimization_level=0) for k, w, qd in spec]
    sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.max_execution_time = 60
    j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    d = os.path.join(P.HERE, 'out', 'ripples_' + time.strftime('%H%M%S')); os.makedirs(d)
    np.savez_compressed(os.path.join(d, 'raw.npz'), **{f'{k}_{w}_{qd}_{reg}': np.asarray(getattr(r[n].data, reg)) for n, (k, w, qd) in enumerate(spec) for reg in ('s', 'b')})
    json.dump({'job': j.job_id(), 'backend': backend, 'chain': CHAIN, 'stone': CHAIN[STONE], 'pond': [CHAIN[k] for k in POND], 'waits_us': WAITS, 'spec': spec, 'shots': SHOTS}, open(os.path.join(d, 'meta.json'), 'w'))
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
