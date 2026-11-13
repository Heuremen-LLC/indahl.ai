"""THE SEAL ON CEPHEUS (Bones, 2026-10-04; Wayfinder: "If we can seal the deal then fucking do it... stop after each step for a binary check, we'll do it together").
Fired AFTER the chip's recalibration of 2026-10-04 18:02Z (triangles D-H ran before it). Two steps, each fired only on Wayfinder's yes:
STEP A  the |2> rows with the clocks' state at readout, on a denser window ladder.
  OBSERVER  the seven emitters (as D-H) held in |2> for 2 / 3.5 / 4 / 4.5 / 6 us; three readout models (shared every round; emitters-only with the others at rest / in |1>, round 1).
  WITNESS   the other qubits at rest | F's copy (half-way, half-way again at the end) | |1> at readout only.
  TIME      three rounds ~3 min apart, each its own shared calibration; set beside F / G (before the recalibration).
  3 rounds x (3 x 5 x 2 arms x 1000 shots + 8 cal x 1500) + 16 cal x 1500 = 130 tasks, 150,000 shots.
STEP B  triangle D again, unchanged circuits (the upper-rung train), after the recalibration: 50 tasks, 49,800 shots.
No outcome written. BINARY CHECKPOINTS asserted: windows, clock states, readout models, rounds -- three or more of each.
  python rigetti_seal.py A-dry | A-submit | A-collect | B-dry | B-submit | B-collect"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_d as D
import rigetti_triangle_g as G
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
OUT = RT.OUT; SH = 1000; SH_CAL = 1500
WIN = [2, 3.5, 4, 4.5, 6]; CLK = ['rest', 'fcopy', 'late']; MODELS = ['shared', 'em_rest', 'em_one']; ROUNDS = [1, 2, 3]
assert len(WIN) >= 3 and len(CLK) >= 3 and len(MODELS) >= 3 and len(ROUNDS) >= 3, 'binary checkpoint SEAL'
def a_round(fr, r):
    it = [(['cal_shared', s, r], RT.cal_circ(fr, D.AMPS, s), SH_CAL) for s in RT.SEQS]
    if r == 1: it += [([f'cal_em_{ck}', s, r], G.cal_em(fr, ck, s), SH_CAL) for ck in ('rest', 'one') for s in RT.SEQS]
    it += [([ck, 'two', w, seq, r], G.circ(fr, ck, 'two', w, seq), SH) for ck in CLK for w in WIN for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(202610049 + r).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('A-dry', 'A-submit'):
        dev, fr = RT.dev_frames(); allit = [a_round(fr, r) for r in ROUNDS]; flat = [x for it in allit for x in it]
        print(f'SEAL A: {len(flat)} tasks, {sum(n for *_, n in flat)} shots, est ${len(flat) * RT.PER_TASK + sum(n for *_, n in flat) * RT.PER_SHOT:.2f}; windows {WIN}; clocks {CLK}; rounds {ROUNDS}')
        if m == 'A-dry':
            for ck in CLK:
                ins = [str(i) for i in [x for x in allit[0] if x[0] == [ck, 'two', 4, 'ba', 1]][0][1].instructions]
                print(f'  {ck:<6} two w4 ba: {len(ins)} instr; q7 (emitter):', [x.split("'operator': ")[1][:18] for x in ins if 'Qubit(7)' in x and "qubit_count': 107" not in x],
                      '| q9 (clock):', [x.split("'operator': ")[1][:18] for x in ins if 'Qubit(9)' in x and "qubit_count': 107" not in x])
            return
        RT.guard_and_book('rigetti SEAL A: |2> held 2-6 us, clocks rest/F-copy/late-|1>, 3 models, 3 rounds, after recalibration', flat)
        T = {'tasks': []}
        for r, it in zip(ROUNDS, allit):
            if r > 1: time.sleep(180)
            for tag, cc, n in it:
                t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()})
            json.dump(T, open(os.path.join(OUT, 'sealA_tasks.json'), 'w'), indent=1); print('round', r, 'sent', flush=True)
    elif m == 'A-collect': RT.collect('sealA_tasks.json', 'sealA.npz')
    elif m in ('B-dry', 'B-submit'):
        dev, fr = RT.dev_frames(); it = D.items(fr)
        print(f'SEAL B (triangle D again): {len(it)} tasks, {sum(n for *_, n in it)} shots, est ${len(it) * RT.PER_TASK + sum(n for *_, n in it) * RT.PER_SHOT:.2f}')
        if m == 'B-dry': return
        RT.guard_and_book('rigetti SEAL B: triangle D again after recalibration', it); RT.send(dev, it, 'sealB_tasks.json')
    elif m == 'B-collect': RT.collect('sealB_tasks.json', 'sealB.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
