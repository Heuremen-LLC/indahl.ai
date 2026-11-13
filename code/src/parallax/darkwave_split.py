"""Round 7: split the beat (see PREREG_DARKWAVE.md)."""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 3, 5, 8, 10]; PH = [0, math.pi / 2, math.pi, 3 * math.pi / 2]; SHOTS = 2000
def nocoin(phi, w):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); s, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'i'); c = QuantumCircuit(q, s, i)
    c.h(0); c.cx(0, 1); c.p(phi, 0); c.h(0); c.measure(0, s)
    if w: c.delay(w * 1000, 1, unit='ns')
    c.h(1); c.measure(1, i); return c
def entmem(w, quad):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); s, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'i'); c = QuantumCircuit(q, s, i)
    c.h(0); c.cx(0, 1); c.h(0); c.measure(0, s)            # H on S before reading: S's outcome leaves I in |+> or |->
    if w: c.delay(w * 1000, 1, unit='ns')
    if quad == 'Y': c.sdg(1)
    c.h(1); c.measure(1, i); return c
def main(keyfile, backend, A, B):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 80: sys.exit('BRAKE')
    spec = [('a', w, p) for w in WAITS for p in PH] + [('b', w, q) for w in WAITS for q in ('X', 'Y')]
    circs = [transpile(nocoin(x, w) if k == 'a' else entmem(w, x), backend=be, initial_layout=[A, B], optimization_level=1) for k, w, x in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    get = lambda k, w, x: list(zip(r[spec.index((k, w, x))].data.s.get_bitstrings(), r[spec.index((k, w, x))].data.i.get_bitstrings()))
    out = {'job': j.job_id(), 'a': [], 'b': []}
    print('(a) NO COIN, always erase: visibility of S fringes, sorted by the partner')
    for w in WAITS:
        vs = []
        for part in ('0', '1'):
            p0 = []
            for p in PH:
                sub = [sb for sb, ib in get('a', w, p) if ib == part]; p0.append(sum(1 for x in sub if x == '0') / max(1, len(sub)))
            a = (p0[0] - p0[2]) / 2; b = (p0[1] - p0[3]) / 2; vs.append(math.hypot(a, b) / (sum(p0) / 4))
        out['a'].append({'wait': w, 'V': vs}); print(f'   {w:2} us  V {vs[0]:.2f} / {vs[1]:.2f}')
    print('(b) ENTANGLED MEMORY: partner coherence and phase, by what the signal read')
    for w in WAITS:
        row = {'wait': w}
        for sv_ in ('0', '1', None):
            ex = []
            for qd in ('X', 'Y'):
                sub = [ib for sb, ib in get('b', w, qd) if sv_ is None or sb == sv_]; ex.append(1 - 2 * sum(int(x) for x in sub) / max(1, len(sub)))
            row[f'S{sv_ or "all"}'] = (math.hypot(*ex), math.degrees(math.atan2(ex[1], ex[0])))
        out['b'].append(row)
        print(f'   {w:2} us  S=0: C {row["S0"][0]:.2f} phase {row["S0"][1]:+5.0f} | S=1: C {row["S1"][0]:.2f} phase {row["S1"][1]:+5.0f} | pooled C {row["Sall"][0]:.2f}')
    d = os.path.join(D.HERE, 'out', 'split_' + backend + '_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1, default=str)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
