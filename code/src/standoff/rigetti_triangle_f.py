"""TRIANGLE F: THE RULER AS THE OBJECT (Bones, 2026-10-04; Wayfinder: "RULERS MEASURING RULERS"). Not a repeat: D and E divided every witness reading by one held-|2> pull per window; E showed the
gap riding with that window, and the pull moved between D and E. F measures the pull itself.
OBSERVER  the seven emitters held at rest / in |1> / in |2> for laid windows 0.25 / 0.5 / 1 / 2 / 4 / 6 us.
WITNESS   every other qubit a free clock (1 / 2 / 3+ links): three rulers measuring each other per window, pull |1>-|0>, |2>-|1>, |2>-|0>; wrapped and unwrapped along the window ladder.
TIME      the emitters' own rung populations in the same shots (X with the plain read, Y with swap-then-flip), so each window's pull is laid against the population that made it; and THREE rounds
          ~3 minutes apart, each with its own readout calibration (job to job).
3 rounds x (3 states x 6 windows x 2 + 8 cal) = 132 tasks x 900 shots (cal 1500). No outcome written. BINARY CHECKPOINTS asserted: three states, six windows, three rounds, clocks at 1 / 2 / 3+.
  python rigetti_triangle_f.py dry | submit | collect"""
import json, math, os, sys, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
import rigetti_triangle_d as D
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = D.EM; CL = C.CL; SH = 900; SH_CAL = 1500; OUT = RT.OUT
STATES = ['zero', 'one', 'two']; WIN = [0.25, 0.5, 1, 2, 4, 6]; ROUNDS = [1, 2, 3]
assert len(STATES) >= 3 and len(WIN) >= 3 and len(ROUNDS) >= 3 and all(Counter(min(C.D[q], 3) for q in CL if C.D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint F'
def circ(fr, s, w, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    D.prep(c, fr, s)
    for q in CL: c.rx(q, math.pi / 2)
    RT.wait(c, fr, w); D.readout(c, fr, hand); return Circuit().add_verbatim_box(c)
def rnd(fr, r):
    it = [(['cal', s, r], RT.cal_circ(fr, D.AMPS, s), SH_CAL) for s in RT.SEQS] + [([s, w, h, r], circ(fr, s, w, h), SH) for s in STATES for w in WIN for h in 'XY']
    return [it[i] for i in np.random.default_rng(202610046 + r).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); allit = [rnd(fr, r) for r in ROUNDS]; flat = [x for it in allit for x in it]
        print(f'F: {len(flat)} tasks, {sum(n for *_, n in flat)} shots; windows {WIN}; rounds {ROUNDS}')
        if m == 'dry':
            tr = [x for x in allit[0] if x[0][:3] == ['two', 1, 'Y']][0][1]; ins = [str(i) for i in tr.instructions]
            print('two w=1 hand Y:', len(ins), 'instructions; pulse gates', sum('PulseGate' in x for x in ins)); return
        RT.guard_and_book('rigetti triangle F: the ruler as the object, held 0/1/2 x 6 windows, 3 rounds', flat)
        T = {'tasks': []}
        for r, it in zip(ROUNDS, allit):
            if r > 1: time.sleep(180)
            for tag, cc, n in it:
                t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()})
            json.dump(T, open(os.path.join(OUT, 'triF_tasks.json'), 'w'), indent=1); print('round', r, 'sent', flush=True)
    elif m == 'collect': RT.collect('triF_tasks.json', 'triF.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
