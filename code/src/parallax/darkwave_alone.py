"""Round 12: is the ring qubit 143's own two-toned heartbeat? Ramsey on each qubit alone (see PREREG_DARKWAVE.md)"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 2, 3, 5, 8, 11, 14]; SHOTS = 2000
def circ(who, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); i = ClassicalRegister(1, 'i'); c = QuantumCircuit(q, i)
    c.h(who); c.barrier()
    if w: c.delay(w * 1000, who, unit='ns')
    c.barrier()
    if quad == 'Y': c.sdg(who)
    c.h(who); c.measure(who, i); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 70: sys.exit('BRAKE')
    spec = [(who, w, q) for who in (0, 1) for w in WAITS for q in ('X', 'Y')]
    circs = [transpile(circ(who, w, q), backend=be, initial_layout=[143, 144], optimization_level=0) for who, w, q in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    out = {'job': j.job_id(), 'rows': []}
    for who, name in ((0, 'q143 (twin) alone'), (1, 'q144 (partner) alone')):
        line = []
        for w in WAITS:
            ex = [1 - 2 * sum(int(x) for x in r[spec.index((who, w, q))].data.i.get_bitstrings()) / SHOTS for q in ('X', 'Y')]
            C = math.hypot(*ex); out['rows'].append({'who': who, 'wait': w, 'X': ex[0], 'Y': ex[1], 'C': C}); line.append(f'{w}us {C:.2f}')
        print(f'{name:22s} coherence: ' + '  '.join(line))
    d = os.path.join(D.HERE, 'out', 'alone_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
