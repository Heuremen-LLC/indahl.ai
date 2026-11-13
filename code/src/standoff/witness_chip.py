"""THE WITNESS, WHOLE CHIP -- 2026-09-28 night. Inside vs outside, same event, no splitting. Emitter q0 parked at rest (E0) or pushed to
rung 2 (E2) and left to fall. EVERY other qubit holds a clock. A clock is dragged only while the emitter sits on rung 2, so each
clock's own curve over the waits is the INSIDE survival curve; the emitter's readout (flip, read) is the OUTSIDE curve.
Dense early waits. No outcome written.   python witness_chip.py dry | submit | collect"""
import json, math, os, sys, time
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM = 0; WIT = [q for q in C.QS if q != EM]; ALLQ = [EM] + WIT; WAITS = [0.5, 1, 2, 3, 4, 6]; SHOTS = 2000
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def circ(fr, arm, w, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    c = Circuit()
    for q in ALLQ: c.rz(q, 0.0)
    for q in WIT: ry(c, q, math.pi / 2)
    if arm == 'E2':
        c.rx(EM, math.pi); c.pulse_gate([EM], PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(A_PI12), False)))
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps)
    c.rx(EM, math.pi)
    for q in WIT:
        if quad == 'Y': c.rz(q, -math.pi / 2)
        ry(c, q, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
SPEC = [(a, w, qd) for a in ('E0', 'E2') for w in WAITS for qd in ('X', 'Y')]
def main():
    mode = sys.argv[1]; cost = len(SPEC) * (C.PER_TASK + SHOTS * C.PER_SHOT)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [circ(fr, *s) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}, {len(WIT)} witness clocks')
        if mode == 'dry': return
        print('ledger', C.spend('witness whole chip: q0 falls, 106 clocks, dense early waits', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SHOTS, disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'wchip_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'wchip_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in ALLQ]]
        np.savez_compressed(os.path.join(C.OUT, 'wchip.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
