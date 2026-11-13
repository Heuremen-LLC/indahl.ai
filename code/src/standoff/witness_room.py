"""THE FULL ROOM -- 2026-09-28 night, Wayfinder: "double down... let it ride." The headline shot (q9 witness, q0 emitter, same waits,
same shots) repeated with the room filled with observers: HALF = every other qubit also a clock; FULL = every qubit a clock.
With tonight's ALONE run (witness_headline.py) that is three points: 0 / half / full observers. No outcome written.
  python witness_room.py dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
EM, WQ = 0, 9; ALLQ = list(C.QS); WAITS = [0.5, 1, 2, 3, 4.5, 6]; SH = {'E0': 1000, 'E2': 2500}
others = [q for q in C.QS if q not in (EM, WQ)]
CONF = {'HALF': [WQ] + others[::2], 'FULL': [WQ] + others}
A_PI12 = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))['0']['a_pi12']
def ry(c, q, t): c.rz(q, -math.pi / 2); c.rx(q, t); c.rz(q, math.pi / 2)
def circ(fr, conf, arm, w, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    clocks = CONF[conf]; c = Circuit()
    for q in ALLQ: c.rz(q, 0.0)
    for q in clocks: ry(c, q, math.pi / 2)
    if arm == 'E2': c.rx(EM, math.pi); c.pulse_gate([EM], PulseSequence().play(fr[EM], DragGaussianWaveform(C.WF_LEN, C.WF_SIGMA, 0.0, float(A_PI12), False)))
    ps = PulseSequence()
    for q in ALLQ: ps = ps.delay(fr[q], C._ns(w))
    c.pulse_gate(ALLQ, ps); c.rx(EM, math.pi)
    for q in clocks:
        if quad == 'Y': c.rz(q, -math.pi / 2)
        ry(c, q, -math.pi / 2)
    return Circuit().add_verbatim_box(c)
SPEC = [(cf, a, w, qd) for cf in ('HALF', 'FULL') for a in ('E0', 'E2') for w in WAITS for qd in 'XY']
def main():
    mode = sys.argv[1]; cost = sum(C.PER_TASK + SH[a] * C.PER_SHOT for _, a, _, _ in SPEC)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in ALLQ}
        circs = [circ(fr, *s) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}; half room {len(CONF["HALF"])} clocks, full room {len(CONF["FULL"])}')
        if mode == 'dry': return
        print('ledger', C.spend('full room: q9 witness with half / all clocks on', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SH[s[1]], disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'wroom_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'wroom_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in (EM, WQ)]]
        np.savez_compressed(os.path.join(C.OUT, 'wroom.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
