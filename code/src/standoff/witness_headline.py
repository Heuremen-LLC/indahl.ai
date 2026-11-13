"""THE HEADLINE SHOT -- 2026-09-28 night. One clean witness (q9, next door), every other qubit parked quiet. Emitter q0 at rest (E0) or
pushed to rung 2 (E2). Two things measured separately, all four combinations left open (jitter y/n x gap y/n):
 JITTER: E2 shots whose emitter still sits on rung 2 at the end -> any smear of q9's drag there is rung 2 being restless.
 GAP   : the full E2 curve (jitter taken out) timed from INSIDE by q9, against the OUTSIDE curve from q0's own readout.
No outcome written.   python witness_headline.py dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM, WQ = 0, 9; ALLQ = [EM, WQ]; WAITS = [0.5, 1, 2, 3, 4.5, 6]; SH = {'E0': 1000, 'E2': 2500}
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def circ(fr, arm, w, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    c = Circuit(); c.rz(EM, 0.0); c.rz(WQ, 0.0); ry(c, WQ, math.pi / 2)
    if arm == 'E2': c.rx(EM, math.pi); c.pulse_gate([EM], PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(A_PI12), False)))
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps); c.rx(EM, math.pi)
    if quad == 'Y': c.rz(WQ, -math.pi / 2)
    ry(c, WQ, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
SPEC = [(a, w, qd) for a in ('E0', 'E2') for w in WAITS for qd in 'XY']
def main():
    mode = sys.argv[1]; cost = sum(C.PER_TASK + SH[a] * C.PER_SHOT for a, _, _ in SPEC)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [circ(fr, *s) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}')
        if mode == 'dry': return
        print('ledger', C.spend('headline: q9 witness alone, jitter + gap', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SH[s[0]], disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'whead_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'whead_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in ALLQ]]
        np.savez_compressed(os.path.join(C.OUT, 'whead.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
