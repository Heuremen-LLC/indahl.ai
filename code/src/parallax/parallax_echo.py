"""THE ECHO RUN (see PREREG_ECHO.md). python parallax_echo.py run|analyze <keyfile|outdir> [backend]"""
import json, os, sys, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import parallax_ibm as P
DELAYS = [20e-6, 50e-6, 100e-6, 250e-6, 500e-6, 1000e-6, 2000e-6]; SHOTS = 1500
def circs(nq):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    out = {}
    for name, flip in (('E0', False), ('E1', True)):
        q = QuantumRegister(nq, 'q'); a, b = ClassicalRegister(nq, 'm0'), ClassicalRegister(nq, 'm1')
        c = QuantumCircuit(q, a, b, name=name); c.measure(q, a)
        if flip: c.x(q)
        c.measure(q, b); out[name] = c
    return out
def run(keyfile, backend):
    from qiskit import transpile; from qiskit_ibm_runtime import SamplerV2
    s, be = P.chip(keyfile, backend); left = s.usage().get('usage_remaining_seconds', 0)
    if left < 150: sys.exit(f'BRAKE: {left} s left')
    Q = P.qubits(be); C = {k: transpile(v, backend=be, initial_layout=Q, optimization_level=0) for k, v in circs(len(Q)).items()}
    out = os.path.join(P.HERE, 'out', 'echo_' + time.strftime('%Y%m%d_%H%M%S')); os.makedirs(out)
    meta = {'backend': backend, 'qubits': Q, 'usage_before_s': left, 'jobs': []}; jobs = []
    for d in DELAYS:
        for name in ('E1', 'E0'):
            sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.execution.rep_delay = d; sm.options.max_execution_time = 30
            j = sm.run([C[name]], shots=SHOTS); jobs.append((name, d, j)); meta['jobs'].append({'pub': name, 'rep_delay': d, 'job_id': j.job_id()})
            print(name, f'{d*1e6:.0f}us', 'submitted', j.job_id(), flush=True); json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    for name, d, j in jobs:
        r = j.result()[0].data; np.savez_compressed(os.path.join(out, f'{name}_{int(d*1e6)}.npz'), m0=np.asarray(r.m0), m1=np.asarray(r.m1))
        print(name, f'{d*1e6:.0f}us', 'done', flush=True)
    meta['usage_after_s'] = s.usage().get('usage_remaining_seconds'); json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    print('OUT', out, 'left', meta['usage_after_s'])
def analyze(out, keyfile=None, backend=None):
    meta = json.load(open(os.path.join(out, 'meta.json'))); Q = meta['qubits']
    L = lambda n, d: np.load(os.path.join(out, f'{n}_{int(d*1e6)}.npz'))
    ref0, ref1 = L('E0', DELAYS[-1])['m1'], L('E1', DELAYS[-1])['m1']
    T1 = {}
    if keyfile:
        try:
            s, be = P.chip(keyfile, backend or meta['backend']); pr = be.properties()
            for q in Q:
                try: T1[q] = pr.t1(q) * 1e6
                except Exception: pass
        except Exception as e: print('T1 lookup failed', e)
    rows = []
    for k, q in enumerate(Q):
        c0, c1, a, t, p, st, sp = P.geometry(ref0[:, k], ref1[:, k])
        if st <= 0 or 1 / (2 * st) < 1.5: continue                          # blind readout: skip
        e = [float(np.mean(t(L('E1', d)['m0'][:, k]) > .5) - np.mean(t(L('E0', d)['m0'][:, k]) > .5)) for d in DELAYS]
        x, y = np.array(DELAYS) * 1e6, np.array(e); ok = y > 0.002
        tau = float(-1 / np.polyfit(x[ok], np.log(y[ok]), 1)[0]) if ok.sum() >= 3 and np.polyfit(x[ok], np.log(y[ok]), 1)[0] < 0 else None
        rows.append({'q': q, 'echo': e, 'tau_us': tau, 'T1_us': T1.get(q)})
    json.dump(rows, open(os.path.join(out, 'echo_per_qubit.json'), 'w'), indent=1)
    med = np.median(np.array([r['echo'] for r in rows]), axis=0)
    print(f"{len(rows)} readable qubits. Median echo (P(1) after a shot that ended in 1, minus after one that ended in 0):")
    for d, m in zip(DELAYS, med): print(f"  gap {d*1e6:6.0f} us: {m*100:6.2f}%")
    both = [(r['tau_us'], r['T1_us']) for r in rows if r['tau_us'] and r['T1_us']]
    if both:
        ratio = np.array([a / b for a, b in both]); print(f"tau/T1 over {len(both)} qubits: median {np.median(ratio):.2f}, middle half {np.percentile(ratio,25):.2f}-{np.percentile(ratio,75):.2f}")
        print('median tau', round(float(np.median([a for a, b in both])), 1), 'us | median T1', round(float(np.median([b for a, b in both])), 1), 'us')
if __name__ == '__main__':
    if sys.argv[1] == 'run': run(sys.argv[2], sys.argv[3])
    else: analyze(sys.argv[2], *(sys.argv[3:5]))
