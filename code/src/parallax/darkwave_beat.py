"""Round 6: the darkwave beat, finely (see PREREG_DARKWAVE.md). One job: waits x 4 phases."""
import sys, os, json, math, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import darkwave_eraser as D
WAITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24]; PH = [0, math.pi / 2, math.pi, 3 * math.pi / 2]; SHOTS = 2000
def main(keyfile, backend, A, B, C):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2; from qiskit import transpile
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(keyfile).read().strip()); be = sv.backend(backend)
    if sv.usage().get('usage_remaining_seconds', 0) < 80: sys.exit('BRAKE')
    spec = [(w, p) for w in WAITS for p in PH]
    circs = [transpile(D.circuit(p, f'late{w}'), backend=be, initial_layout=[A, B, C], optimization_level=1) for w, p in spec]
    sm = SamplerV2(mode=be); sm.options.max_execution_time = 90; j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    rows = []
    for w in WAITS:
        vs = []
        for part in (0, 1):
            p0 = []
            for p in PH:
                sh = D.shots_from(r[spec.index((w, p))]); sub = [s for s, c, i in sh if c == 1 and i == part]; p0.append(sum(1 for s in sub if s == 0) / max(1, len(sub)))
            a = (p0[0] - p0[2]) / 2; b = (p0[1] - p0[3]) / 2; off = sum(p0) / 4; vs.append((math.hypot(a, b) / off, math.degrees(math.atan2(-b, a))))
        rows.append({'wait_us': w, 'V_partner0': vs[0][0], 'phase0_deg': vs[0][1], 'V_partner1': vs[1][0], 'phase1_deg': vs[1][1]})
        print(f'{w:3} us  V {vs[0][0]:.2f} / {vs[1][0]:.2f}   fringe phase {vs[0][1]:+6.0f} / {vs[1][1]:+6.0f} deg')
    d = os.path.join(D.HERE, 'out', 'beat_' + backend + '_' + time.strftime('%H%M%S')); os.makedirs(d); json.dump({'job': j.job_id(), 'rows': rows}, open(os.path.join(d, 'result.json'), 'w'), indent=1)
    print('OUT', d, 'left', sv.usage().get('usage_remaining_seconds'))
if __name__ == '__main__': main(sys.argv[1], sys.argv[2], *map(int, sys.argv[3:6]))
