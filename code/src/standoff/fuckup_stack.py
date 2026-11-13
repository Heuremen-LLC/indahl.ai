"""THE FUCK-UP STACK -- 2026-09-28 night. Two shots, nothing written first, all outcomes kept.
 START: q0's heat at the start measured the readout-proof way (third-rung trick: A = push(a) -> flip -> read; B = flip -> push(a) ->
   flip -> read; a in {0, pi12}; heat = A-swing / (A-swing + B-swing)), plus a plain read. Rooms: ALONE (nobody watching), HALF (54
   clocks), FULL (106 clocks), clocks lit at t=0, 3 us wait, then the emitter sequence, clocks closed. Rotated: A,H,F then F,H,A.
 THREE: q0 at rest (E0) or on rung 2 (E2); q9 = the clock; q10 = third body parked at 0 or at 1. Waits 1,2,4 us, X/Y.
  python fuckup_stack.py dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM, WQ, TB = 0, 9, 10; ALLQ = list(C.QS); others = [q for q in C.QS if q != EM]
ROOMS = {'ALONE': [], 'HALF': others[::2], 'FULL': others}
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']; WAIT0 = 3
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def push(fr, amp):
    from braket.pulse import PulseSequence, DragGaussianWaveform
    return PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(amp), False))
def wait_all(c, fr, w):
    from braket.pulse import PulseSequence
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps)
def start_circ(fr, room, part, amp):
    from braket.circuits import Circuit
    c = Circuit(); clocks = ROOMS[room]
    for q in ALLQ: c.rz(q, 0.0)
    for q in clocks: ry(c, q, math.pi / 2)
    wait_all(c, fr, WAIT0)
    if part == 'A':
        if amp: c.pulse_gate([EM], push(fr, amp))
        c.rx(EM, math.pi)
    elif part == 'B':
        c.rx(EM, math.pi)
        if amp: c.pulse_gate([EM], push(fr, amp))
        c.rx(EM, math.pi)
    for q in clocks: ry(c, q, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
def three_circ(fr, arm, tb, w, quad):
    from braket.circuits import Circuit
    c = Circuit()
    for q in ALLQ: c.rz(q, 0.0)
    ry(c, WQ, math.pi / 2)
    if tb == 1: c.rx(TB, math.pi)
    if arm == 'E2': c.rx(EM, math.pi); c.pulse_gate([EM], push(fr, A_PI12))
    wait_all(c, fr, w); c.rx(EM, math.pi)
    if quad == 'Y': c.rz(WQ, -math.pi / 2)
    ry(c, WQ, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
START = []
for rnd, order in ((1, ('ALONE', 'HALF', 'FULL')), (2, ('FULL', 'HALF', 'ALONE'))):
    for room in order: START += [('start', rnd, room, 'A', 0, 4000), ('start', rnd, room, 'A', 1, 4000), ('start', rnd, room, 'B', 0, 1000), ('start', rnd, room, 'B', 1, 1000), ('start', rnd, room, 'D', 0, 1000)]
THREE = [('three', arm, tb, w, qd, 1500) for tb in (0, 1) for arm in ('E0', 'E2') for w in (1, 2, 4) for qd in 'XY']
SPEC = START + THREE
def main():
    mode = sys.argv[1]; cost = sum(C.PER_TASK + s[-1] * C.PER_SHOT for s in SPEC)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [start_circ(fr, s[2], s[3], A_PI12 if s[4] else 0) if s[0] == 'start' else three_circ(fr, *s[1:5]) for s in SPEC]
        print(f'{len(SPEC)} tasks, ${cost:.2f}')
        if mode == 'dry': return
        print('ledger', C.spend('fuck-up stack: observers & the start (RPM, rotated rooms) + three-body', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=s[-1], disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s[:-1]), 'arn': t.id}); print('sent', s[:-1], flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'stack_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'stack_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in (EM, WQ, TB)]]
        np.savez_compressed(os.path.join(C.OUT, 'stack.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
