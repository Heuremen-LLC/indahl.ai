"""THE PARTNER'S MEMORY (2026-09-28, Bones; see PREREG_DARKWAVE.md round 5). Free-evolution coherence of the eraser's partner qubit.
Series 'alone': neighbor S left in |0>. Series 'after': neighbor S put in |+> and MEASURED first (like the eraser), then the partner waits.
Partner: H, wait t, then read X (H) or Y (sdg, H). Coherence C(t) = sqrt(<X>^2 + <Y>^2); in 'after' also split by S's outcome.
  python partner_memory.py run <keyfile> <backend> <S> <I>"""
import json, os, sys, time, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); DELAYS = [0, 1, 2, 3, 5, 8, 12, 20, 35, 50]; SHOTS = 2000
def circ(t_us, quad, after):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(2, 'q'); s, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'i'); c = QuantumCircuit(q, s, i)
    if after: c.h(0); c.measure(0, s)
    c.h(1)
    if t_us: c.delay(int(t_us * 1000), 1, unit='ns')
    if quad == 'Y': c.sdg(1)
    c.h(1); c.measure(1, i); return c
def run(keyfile, backend, S, I):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 60: sys.exit('BRAKE')
    spec = [(t, qd, af) for af in (False, True) for t in DELAYS for qd in ('X', 'Y')]
    circs = [transpile(circ(t, qd, af), backend=be, initial_layout=[S, I], optimization_level=0) for t, qd, af in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 60; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    data = {}
    for (t, qd, af), pr in zip(spec, r):
        sb = pr.data.s.get_bitstrings(); ib = pr.data.i.get_bitstrings(); data[(t, qd, af)] = list(zip(sb, ib))
    out = {'backend': backend, 'S': S, 'I': I, 'job': j.job_id(), 'rows': []}
    print(f'{"t us":>5} | alone C | after C (all) | after C given S=0 | S=1')
    for t in DELAYS:
        def coh(af, cond=None):
            ex = []
            for qd in ('X', 'Y'):
                sh = [iv for sv_, iv in data[(t, qd, af)] if cond is None or sv_ == cond]; ex.append(1 - 2 * sum(int(x) for x in sh) / max(1, len(sh)))
            return math.hypot(*ex)
        row = {'t_us': t, 'alone': coh(False), 'after': coh(True), 'after_S0': coh(True, '0'), 'after_S1': coh(True, '1')}; out['rows'].append(row)
        print(f'{t:5} | {row["alone"]:.3f}   | {row["after"]:.3f}         | {row["after_S0"]:.3f}             | {row["after_S1"]:.3f}')
    d = os.path.join(HERE, 'out', f'partner_{backend}_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump(out, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': run(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
