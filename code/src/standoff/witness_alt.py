"""ALTERNATING ROOMS -- 2026-09-28 night. Does the emitter's rung 2 empty faster when the room is full of observers, or was that drift?
ALONE (only q9 a clock) and FULL (every qubit a clock) alternate task by task, two rounds, same waits. Emitter q0 pushed to rung 2
(E2) each time; its own readout times the fall (outside); q9 X-clock rides along. No outcome written.  dry | submit | collect"""
import json, math, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
import witness_room as WR
EM, WQ = 0, 9; WAITS = [0.5, 1, 2, 3, 4.5, 6]; SH = 2500
CONF = {'ALONE': [WQ], 'FULL': WR.CONF['FULL']}
def circ(fr, conf, w):
    WR.CONF[conf] = CONF[conf]; return WR.circ(fr, conf, 'E2', w, 'X')
SPEC = [(rnd, conf, w) for rnd in (1, 2) for w in WAITS for conf in ('ALONE', 'FULL')]     # alternate every task
def main():
    mode = sys.argv[1]; cost = len(SPEC) * (C.PER_TASK + SH * C.PER_SHOT)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in C.QS}
        circs = [circ(fr, cf, w) for _, cf, w in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}')
        if mode == 'dry': return
        print('ledger', C.spend('alternating rooms: alone vs full, fall time', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=SH, disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s), 'arn': t.id}); print('sent', s, flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'walt_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'walt_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in (EM, WQ)]]
        np.savez_compressed(os.path.join(C.OUT, 'walt.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
