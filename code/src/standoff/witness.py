"""THE WITNESS -- 2026-09-28 night. Wayfinder: "we need the measurement another qubit would get, from inside the system."
Emitter q0: parked on rung 0 (E0), rung 1 (E1), or pushed to rung 2 (E2) and left to fall (rung 2 -> 1, ~12 us, one packet of energy).
Witness clocks, all held in superposition through the wait: q9 and q1 (direct neighbors), q10 (two steps away, control).
After the wait: emitter read after a flip (E2: 0 = it fell to rung 1, 1 = still on rung 2); each clock read in X or Y.
No outcome written. Split every clock by fell / didn't fall; subtract what the plain lean (E0/E1/E2 parked) predicts; look at what's left.
  python witness.py dry | submit | collect | analyze"""
import json, math, os, sys, time
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM = 0; WIT = [9, 1, 10]; ALLQ = [EM] + WIT; WAITS = [4, 8, 16]; SHOTS = 2000
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def circ(dev, fr, arm, w, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    c = Circuit()
    for q in ALLQ: c.rz(q, 0.0)
    for q in WIT: ry(c, q, math.pi / 2)                                  # clocks start
    if arm in ('E1', 'E2'): c.rx(EM, math.pi)
    if arm == 'E2': c.pulse_gate([EM], PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(A_PI12), False)))
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps)                                               # the wait: everyone idle, the emitter may fall
    c.rx(EM, math.pi)                                                    # emitter flip: rung 1 -> reads 0 (fell), rung 2 stays (reads 1)
    for q in WIT:
        if quad == 'Y': c.rz(q, -math.pi / 2)
        ry(c, q, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
SPEC = [(a, w, qd) for a in ('E0', 'E1', 'E2') for w in WAITS for qd in ('X', 'Y')]
def main():
    mode = sys.argv[1]; cost = len(SPEC) * (C.PER_TASK + SHOTS * C.PER_SHOT)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [circ(dev, fr, *s) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}, emitter push {A_PI12:.3f}')
        if mode == 'dry': print(str(circs[-1])[:1200]); return
        print('ledger', C.spend('witness: q0 falls from rung 2, clocks q9/q1/q10', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SHOTS, disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
        json.dump(T, open(os.path.join(C.OUT, 'witness_tasks.json'), 'w'), indent=1); return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'witness_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in ALLQ]]
        np.savez_compressed(os.path.join(C.OUT, 'witness.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
