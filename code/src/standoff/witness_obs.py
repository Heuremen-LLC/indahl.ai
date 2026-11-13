"""WHO'S WATCHING -- 2026-09-28 night. Wayfinder: "the resonance comes back with the frequency of the observer... account for the new
measurements in the system." Same event (q0 to rung 2), different sets of observers (clocks) inside the system. No outcome written.
 LEAK : all clocks on; arms E0 (rest) vs EP (the f12 push fired with q0 on rung 0 -- the push does nothing to q0 itself).
 FAR  : clocks ON only on far noticers q5,q43,q45,q35,q62,q80 + far controls q7,q13,q30,q50; neighbors q1,q9 parked at 0. E0 vs E2.
 FAR+N: the same plus q1,q9 as clocks. E0 vs E2.
 waits 2, 4 us; X/Y.   python witness_obs.py dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM = 0; ALLQ = [q for q in C.QS]; FAR = [5, 43, 45, 35, 62, 80, 7, 13, 30, 50]; NB = [1, 9]
CONF = {'LEAK': [q for q in C.QS if q != EM], 'FAR': FAR, 'FARN': FAR + NB}
WAITS = [2, 4]; SHOTS = 2000
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def circ(fr, conf, arm, w, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    clocks = CONF[conf]; c = Circuit()
    for q in ALLQ: c.rz(q, 0.0)
    for q in clocks: ry(c, q, math.pi / 2)
    if arm == 'E2': c.rx(EM, math.pi)
    if arm in ('E2', 'EP'): c.pulse_gate([EM], PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(A_PI12), False)))
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps)
    c.rx(EM, math.pi)
    for q in clocks:
        if quad == 'Y': c.rz(q, -math.pi / 2)
        ry(c, q, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
SPEC = [('LEAK', a, w, qd) for a in ('E0', 'EP') for w in WAITS for qd in 'XY'] + [(cf, a, w, qd) for cf in ('FAR', 'FARN') for a in ('E0', 'E2') for w in WAITS for qd in 'XY']
def main():
    mode = sys.argv[1]; cost = len(SPEC) * (C.PER_TASK + SHOTS * C.PER_SHOT)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [circ(fr, *s) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}')
        if mode == 'dry': return
        print('ledger', C.spend("who's watching: leak / far only / far + neighbors", cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SHOTS, disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'wobs_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'wobs_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in ALLQ]]
        np.savez_compressed(os.path.join(C.OUT, 'wobs.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
