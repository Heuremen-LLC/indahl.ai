"""Round 10: is it the |11> piece going through the gate? (see PREREG_DARKWAVE.md)"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 3, 5, 8, 10]; SHOTS = 2000
def circ(arm, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); s, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'i'); c = QuantumCircuit(q, s, i)
    if arm in ('h', 'j'): c.x(0)
    else: c.h(0)
    c.h(1)
    if arm in ('h', 'i'): c.cz(0, 1); c.cz(0, 1)
    if w: c.delay(w * 1000, 1, unit='ns')
    if arm == 'i': c.h(0)
    c.measure(0, s)
    if quad == 'Y': c.sdg(1)
    c.h(1); c.measure(1, i); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 70: sys.exit('BRAKE')
    spec = [(a, w, q) for a in ('j', 'h', 'i') for w in WAITS for q in ('X', 'Y')]
    circs = [transpile(circ(a, w, q), backend=be, initial_layout=[143, 144], optimization_level=0) for a, w, q in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    out = {'job': j.job_id(), 'rows': []}; name = {'j': 'twin=1, no gate (control)', 'h': 'twin=1, gate twice', 'i': 'twin=+, gate twice'}
    for a in ('j', 'h', 'i'):
        line = []
        for w in WAITS:
            ex = []
            for q in ('X', 'Y'):
                bits = r[spec.index((a, w, q))].data.i.get_bitstrings(); ex.append(1 - 2 * sum(int(x) for x in bits) / len(bits))
            C = math.hypot(*ex); out['rows'].append({'arm': a, 'wait': w, 'C': C}); line.append(f'{w}us {C:.2f}')
        print(f'{name[a]:28s} partner coherence: ' + '  '.join(line))
    d = os.path.join(D.HERE, 'out', 'eleven_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
