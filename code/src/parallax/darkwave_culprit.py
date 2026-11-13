"""Round 8: who is the hidden party? (see PREREG_DARKWAVE.md)"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 3, 5, 8, 10]; SHOTS = 2000
def circ(arm, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(3, 'q'); i = ClassicalRegister(1, 'i'); c = QuantumCircuit(q, i)   # q0=143, q1=144 (partner), q2=145
    c.h(1)
    if arm == 'c': c.cz(0, 1); c.cz(0, 1)
    if arm == 'd': c.cz(2, 1); c.cz(2, 1)
    if w: c.delay(w * 1000, 1, unit='ns')
    if quad == 'Y': c.sdg(1)
    c.h(1); c.measure(1, i); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 80: sys.exit('BRAKE')
    spec = [(a, w, q) for a in ('e', 'c', 'd') for w in WAITS for q in ('X', 'Y')]
    circs = [transpile(circ(a, w, q), backend=be, initial_layout=[143, 144, 145], optimization_level=0) for a, w, q in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    out = {'job': j.job_id(), 'rows': []}; name = {'e': 'no gate (control)', 'c': 'CZ with 143 twice', 'd': 'CZ with 145 twice'}
    for a in ('e', 'c', 'd'):
        cs = []
        for w in WAITS:
            ex = []
            for q in ('X', 'Y'):
                bits = r[spec.index((a, w, q))].data.i.get_bitstrings(); ex.append(1 - 2 * sum(int(x) for x in bits) / len(bits))
            cs.append(math.hypot(*ex)); out['rows'].append({'arm': a, 'wait': w, 'C': cs[-1], 'phase_deg': math.degrees(math.atan2(ex[1], ex[0]))})
        print(f'{name[a]:20s} coherence at ' + '  '.join(f'{w}us {c:.2f}' for w, c in zip(WAITS, cs)))
    d = os.path.join(D.HERE, 'out', 'culprit_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
