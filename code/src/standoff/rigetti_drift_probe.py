"""rigetti_drift_probe.py -- THE ROW AGAINST TIME SINCE CALIBRATION (Bones, 2026-10-05; Wayfinder's hat: "Calibration only takes care of one corner of the triangle").
One lean round = the seal's 4-us row, every corner re-read each round:
  OBSERVER  all three readout rulers re-measured every round (shared 8 seq + emitters-only rest / |1> 16 seq, 1500 shots each).
  WITNESS   the other qubits at rest | half-way (F copy) | |1> at readout, emitters held in |2> 4 us, e / ba arms, 1000 shots.
  TIME      the round's send time and the chip's calibration stamp (service updatedAt) are written with it.
30 tasks, 42,000 shots, ~$26.85 a round. No outcome written (a hat, not a call).
  python rigetti_drift_probe.py dry | submit N | collect N"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_d as D
import rigetti_triangle_g as G
import boto3
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
OUT = RT.OUT; SH = 1000; SH_CAL = 1500; CLK = ['rest', 'fcopy', 'late']; W = 4
def cal_stamp():
    d = boto3.client('braket', region_name='us-west-1').get_device(deviceArn='arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q')
    return json.loads(d['deviceCapabilities'])['service']['updatedAt']
def items(fr, n):
    it = [(['cal_shared', s, 1], RT.cal_circ(fr, D.AMPS, s), SH_CAL) for s in RT.SEQS]
    it += [([f'cal_em_{ck}', s, 1], G.cal_em(fr, ck, s), SH_CAL) for ck in ('rest', 'one') for s in RT.SEQS]
    it += [([ck, 'two', W, seq, 1], G.circ(fr, ck, 'two', W, seq), SH) for ck in CLK for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(20261005 + n).permutation(len(it))]
def main():
    m = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr, n)
        print(f'DRIFT PROBE round {n}: {len(it)} tasks, {sum(k for *_, k in it)} shots, est ${len(it) * RT.PER_TASK + sum(k for *_, k in it) * RT.PER_SHOT:.2f}')
        if m == 'dry': return
        cal = cal_stamp(); RT.guard_and_book(f'rigetti DRIFT PROBE round {n} (calibration {cal})', it)
        T = {'round': n, 'calibration': cal, 'sent': time.time(), 'tasks': []}
        for tag, cc, k in it:
            t = dev.run(cc, shots=k, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()})
        json.dump(T, open(os.path.join(OUT, f'drift_r{n:03d}_tasks.json'), 'w'), indent=1); print(f'round {n} sent, calibration {cal}', flush=True)
    elif m == 'collect': RT.collect(f'drift_r{n:03d}_tasks.json', f'drift_r{n:03d}.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
