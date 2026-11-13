"""THE DARKWAVE ERASER (see PREREG_DARKWAVE.md). python darkwave_eraser.py sim | run <keyfile> <backend> | analyze <outdir>"""
import json, os, sys, time, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PHIS = [2 * math.pi * k / 8 for k in range(8)]; SHOTS = 4000
def circuit(phi, variant='late5'):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(3, 'q'); s, c, i = ClassicalRegister(1, 's'), ClassicalRegister(1, 'c'), ClassicalRegister(1, 'i')
    qc = QuantumCircuit(q, s, c, i)          # q0 = S (signal), q1 = I (partner), q2 = C (coin)
    qc.h(0); qc.cx(0, 1)
    if variant == 'early':                   # the choice BEFORE the record
        qc.h(2); qc.measure(2, c)
        with qc.if_test((c, 1)): qc.h(1)
        qc.measure(1, i); qc.p(phi, 0); qc.h(0); qc.measure(0, s); return qc
    qc.p(phi, 0); qc.h(0); qc.measure(0, s)
    pin = variant.endswith('B'); v = variant[:-1] if pin else variant   # ...B = BARRIER after the record: it is truly made first (9/28 rd 11)
    if pin: qc.barrier()
    d = {'late50': 50000, 'late0': 0, 'late50e': 0}.get(v, 5000)
    if v.startswith('late') and v[4:].isdigit(): d = int(v[4:]) * 1000   # lateN = N microseconds
    if d: qc.delay(d, 1, unit='ns')
    if variant == 'late50e':   # echo on the partner during a 50 us wait: X, 25 us, X, 25 us (logically identity)
        qc.x(1); qc.delay(25000, 1, unit='ns'); qc.x(1); qc.delay(25000, 1, unit='ns')
    qc.h(2); qc.measure(2, c)
    with qc.if_test((c, 1)): qc.h(1)
    qc.measure(1, i); return qc
def tally(counts_s, counts_c, counts_i):
    # per-shot bitstrings -> dict of subsets
    return counts_s, counts_c, counts_i
def vis(phis, p):
    X = np.stack([np.ones(len(phis)), np.cos(phis), np.sin(phis)], 1); b, *_ = np.linalg.lstsq(X, np.array(p), rcond=None)
    amp = math.hypot(b[1], b[2]); return amp / b[0] if b[0] else float('nan'), b
def analyze_shots(per_phi):
    out = {}
    for name, sel in (('S alone', lambda c, i: True), ('coin 1 (erased), partner 0', lambda c, i: c == 1 and i == 0),
                      ('coin 1 (erased), partner 1', lambda c, i: c == 1 and i == 1), ('coin 0 (path kept), partner 0', lambda c, i: c == 0 and i == 0),
                      ('coin 0 (path kept), partner 1', lambda c, i: c == 0 and i == 1)):
        p, n = [], []
        for shots in per_phi:
            sub = [s for s, c, i in shots if sel(c, i)]; n.append(len(sub)); p.append(sum(1 for s in sub if s == 0) / max(1, len(sub)))
        V, b = vis(np.array(PHIS), p); eV = math.sqrt(2 / (8 * max(1, min(n)))) / max(b[0], 1e-9) * 1.0
        out[name] = {'P_S0': p, 'n': n, 'visibility': V, 'vis_err': eV}
        print(f'{name:32s} V = {V:.3f} +/- {eV:.3f}   P(S=0) by phase: ' + ' '.join(f'{x:.2f}' for x in p))
    return out
def shots_from(result):
    s = result.data.s.get_bitstrings(); c = result.data.c.get_bitstrings(); i = result.data.i.get_bitstrings()
    return [(int(a), int(b), int(d)) for a, b, d in zip(s, c, i)]
def sim():
    from qiskit_aer import AerSimulator; from qiskit_ibm_runtime import SamplerV2; from qiskit import transpile
    be = AerSimulator(); sm = SamplerV2(mode=be); r = sm.run([transpile(circuit(p), be) for p in PHIS], shots=SHOTS).result()
    analyze_shots([shots_from(x) for x in r])
def run(keyfile, backend):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    s = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = s.backend(backend)
    left = s.usage().get('usage_remaining_seconds', 0)
    if left < 100: sys.exit(f'BRAKE: {left} s left')
    t = be.target; best = None
    for (a, b), props in t['cz'].items() if 'cz' in t.operation_names else t['ecr'].items():
        e = (props.error or 1) + t['measure'][(a,)].error + t['measure'][(b,)].error
        if best is None or e < best[0]: best = (e, a, b)
    _, A, B = best; C = min((q for q in range(be.num_qubits) if q not in (A, B)), key=lambda q: t['measure'][(q,)].error)
    variants = (sys.argv[4].split(',') if len(sys.argv) > 4 else ['late5'])
    out = os.path.join(HERE, 'out', 'darkwave_' + backend + '_' + time.strftime('%Y%m%d_%H%M%S')); os.makedirs(out); res = {}
    for v in variants:
        circs = [transpile(circuit(p, v), backend=be, initial_layout=[A, B, C], optimization_level=1) for p in PHIS]
        sm = SamplerV2(mode=be); sm.options.max_execution_time = 60; j = sm.run(circs, shots=SHOTS)
        print(v, 'submitted', j.job_id(), 'qubits S,I,C =', A, B, C, flush=True); r = j.result(); per = [shots_from(x) for x in r]
        json.dump({'backend': backend, 'variant': v, 'job': j.job_id(), 'qubits': [A, B, C], 'phis': PHIS, 'shots': per}, open(os.path.join(out, f'raw_{v}.json'), 'w'))
        print('--', v, '--'); res[v] = analyze_shots(per)
    json.dump(res, open(os.path.join(out, 'result.json'), 'w'), indent=1)
    print('OUT', out, 'left', s.usage().get('usage_remaining_seconds'))
if __name__ == '__main__':
    {'sim': lambda: sim(), 'run': lambda: run(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
