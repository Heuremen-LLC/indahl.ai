"""ONE FOR THE ROAD -- 2026-09-28 night. Crazy Hat protocol, nothing written first. q0's heat at the start, readout-proof (third-rung
A/B trick + plain read), with three rooms watching: ALONE (nobody), EDGE (q35, q62, q80 = last column; heard q0's push; hop in rung-2
pitch), MIDDLE (q39, q58, q75 = middle columns, same rows, unflagged). Clocks lit at t=0, 3 us wait, emitter sequence, clocks closed.
Rotated: ALONE, EDGE, MIDDLE then MIDDLE, EDGE, ALONE.   python edge_room.py dry | submit | collect"""
import json, os, sys
import numpy as np
os.environ.setdefault('AWS_PROFILE', 'braket'); os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-1')
import rigetti_chip as C
import fuckup_stack as S
S.ROOMS.update({'EDGE': [35, 62, 80], 'MIDDLE': [39, 58, 75]})
SPEC = []
for rnd, order in ((1, ('ALONE', 'EDGE', 'MIDDLE')), (2, ('MIDDLE', 'EDGE', 'ALONE'))):
    for room in order: SPEC += [('start', rnd, room, 'A', 0, 4000), ('start', rnd, room, 'A', 1, 4000), ('start', rnd, room, 'B', 0, 1000), ('start', rnd, room, 'B', 1, 1000), ('start', rnd, room, 'D', 0, 1000)]
def main():
    mode = sys.argv[1]; cost = sum(C.PER_TASK + s[-1] * C.PER_SHOT for s in SPEC)
    if mode in ('dry', 'submit'):
        from braket.aws import AwsDevice
        dev = AwsDevice(C.DEVICE); fr = {q: dev.frames[f'Transmon_{q}_charge_tx_f12'] for q in S.ALLQ}
        circs = [S.start_circ(fr, s[2], s[3], S.A_PI12 if s[4] else 0) for s in SPEC]; print(f'{len(SPEC)} tasks, ${cost:.2f}')
        if mode == 'dry': return
        print('ledger', C.spend('one for the road: edge room vs middle room vs alone (q0 heat, readout-proof, rotated)', cost)); T = {'tasks': []}
        for s, cc in zip(SPEC, circs):
            t = dev.run(cc, shots=s[-1], disable_qubit_rewiring=True); T['tasks'].append({'tag': list(s[:-1]), 'arn': t.id}); print('sent', s[:-1], flush=True)
            json.dump(T, open(os.path.join(C.OUT, 'edge_tasks.json'), 'w'), indent=1)
        return
    if mode == 'collect':
        from braket.aws import AwsQuantumTask
        T = json.load(open(os.path.join(C.OUT, 'edge_tasks.json'))); arrs = {}; st = []
        for t in T['tasks']:
            task = AwsQuantumTask(t['arn']); s = task.state(); st.append(s)
            if s == 'COMPLETED':
                r = task.result(); mq = list(r.measured_qubits); m = np.asarray(r.measurements); arrs[json.dumps(t['tag'])] = m[:, [mq.index(q) for q in (0, 35, 62, 80, 39, 58, 75)]]
        np.savez_compressed(os.path.join(C.OUT, 'edge.npz'), **arrs); print({x: st.count(x) for x in set(st)}); return
if __name__ == '__main__': main()
