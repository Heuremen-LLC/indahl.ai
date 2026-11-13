"""Round 9: does the measurement breaking the entanglement start the ringing? (see PREREG_DARKWAVE.md)"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 3, 5, 8, 10]; SHOTS = 2000
def circ(arm, w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); s, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'i'); c = QuantumCircuit(q, s, i)
    c.h(0); c.cx(0, 1)
    if arm == 'b': c.h(0); c.measure(0, s)
    if w: c.delay(w * 1000, 1, unit='ns')
    if arm == 'f':
        if w: c.delay(w * 1000, 0, unit='ns')
        c.h(0); c.measure(0, s)
    if quad == 'Y': c.sdg(1)
    c.h(1); c.measure(1, i); return c
def main(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 70: sys.exit('BRAKE')
    spec = [(a, w, q) for a in ('b', 'f') for w in WAITS for q in ('X', 'Y')]
    circs = [transpile(circ(a, w, q), backend=be, initial_layout=[143, 144], optimization_level=1) for a, w, q in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    out = {'job': j.job_id(), 'rows': []}; name = {'b': 'twin measured FIRST', 'f': 'twin measured AFTER wait'}
    for a in ('b', 'f'):
        line = []
        for w in WAITS:
            cs = []
            for sv_ in ('0', '1'):
                ex = []
                for q in ('X', 'Y'):
                    pr = r[spec.index((a, w, q))]; sub = [ib for sb, ib in zip(pr.data.s.get_bitstrings(), pr.data.i.get_bitstrings()) if sb == sv_]
                    ex.append(1 - 2 * sum(int(x) for x in sub) / max(1, len(sub)))
                cs.append(math.hypot(*ex))
            out['rows'].append({'arm': a, 'wait': w, 'C_S0': cs[0], 'C_S1': cs[1]}); line.append(f'{w}us {cs[0]:.2f}/{cs[1]:.2f}')
        print(f'{name[a]:24s} partner coherence (S=0/S=1): ' + '  '.join(line))
    d = os.path.join(D.HERE, 'out', 'ring_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
