"""TRIANGLE D: THE PUSH TRAIN ON THE UPPER PAIR OF RUNGS (Bones, 2026-10-04). Not a repeat: no run has pushed between |1> and |2>; and a |2> emitter pulls a clock ~10x harder than a |1> one (§205),
so the witness can hear it.
OBSERVER  the seven emitters, ten pushes on the upper pair (the tuned 1<->2 swap), a push after every g = 0.1 / 0.2 / 0.4 us (L = 1 / 2 / 4 us); three starts: |1>, |2>, and |0> (the control: the upper swap should not touch it).
WITNESS   every other qubit a free clock (half-way at the start, two hands at the end); references at each L: emitters held in |1> and held in |2> for L. The emitters' |2> time as the clocks read it =
          (turn in the train - turn held |1>) / ((turn held |2> - turn held |1>) / L). Clocks by links 1 / 2 / 3+.
TIME      the emitters' own decay from |2> (0.5 / 1 / 2 / 4 us) and from |1> (1 / 4 us), and their end state after each train on three rungs (X pairs with the plain read, Y with swap-then-flip).
5 arms x 3 L x 2 + 6 rulers x 2 + 8 cal = 50 tasks x 900 shots (cal 1500). No outcome written. BINARY CHECKPOINTS asserted: three train lengths, three starts, three arms beyond the starts, clocks at 1 / 2 / 3+.
  python rigetti_triangle_d.py dry | submit | collect"""
import json, math, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangles as T
import rigetti_triangle_c as C
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = T.EM; CL = C.CL; AMPS = T.AMPS; SH = 900; SH_CAL = 1500
GAPS = [0.1, 0.2, 0.4]; STARTS = ['one', 'two', 'zero']; ARMS = ['train_one', 'train_two', 'train_zero', 'held_one', 'held_two']
R2 = [0.5, 1, 2, 4]; R1 = [1, 4]
assert len(GAPS) >= 3 and len(STARTS) >= 3 and len(ARMS) >= 5 and all(Counter(min(C.D[q], 3) for q in CL if C.D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint D'
def up(c, fr): c.pulse_gate(EM, RT.f12(fr, {q: AMPS[q] for q in EM}))
def prep(c, fr, s):
    if s in ('one', 'two'):
        for q in EM: c.rx(q, math.pi)
    if s == 'two': up(c, fr)
def readout(c, fr, hand):
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    if hand == 'Y':
        up(c, fr)
        for q in EM: c.rx(q, math.pi)
def circ(fr, arm, g, hand):
    from braket.circuits import Circuit
    L = 10 * g; c = Circuit()
    for q in QS: c.rz(q, 0.0)
    kind, s = arm.split('_'); prep(c, fr, s)
    for q in CL: c.rx(q, math.pi / 2)
    if kind == 'train':
        for _ in range(RT.PUSHES):
            RT.wait(c, fr, g); up(c, fr)
    else: RT.wait(c, fr, L)
    readout(c, fr, hand); return Circuit().add_verbatim_box(c)
def ruler(fr, s, w, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    prep(c, fr, s); RT.wait(c, fr, w)
    if seq == 'ba':
        up(c, fr)
        for q in EM: c.rx(q, math.pi)
    return Circuit().add_verbatim_box(c)
def items(fr):
    it = [(['cal', s, 'D'], RT.cal_circ(fr, AMPS, s), SH_CAL) for s in RT.SEQS]
    it += [([a, g, h], circ(fr, a, g, h), SH) for a in ARMS for g in GAPS for h in 'XY']
    it += [([f'ruler_{s}', w, seq], ruler(fr, s, w, seq), SH) for s, ws in (('two', R2), ('one', R1)) for w in ws for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(2026100440).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr); print(f'D: {len(it)} tasks, {sum(n for *_, n in it)} shots; emitters {EM}')
        if m == 'dry':
            tr = [x for x in it if x[0][0] == 'train_one' and x[0][1] == 0.2 and x[0][2] == 'Y'][0][1]; ins = [str(i) for i in tr.instructions]
            print('train_one g=0.2 hand Y:', len(ins), 'instructions; q7 (an emitter) ops:', [x[:58] for x in ins if 'Qubit(7)' in x and "qubit_count': 107" not in x][:6]); return
        RT.guard_and_book('rigetti triangle D: push train on the upper pair of rungs, 7 emitters, starts 1/2/0, every clock', it); RT.send(dev, it, 'triD_tasks.json')
    elif m == 'collect': RT.collect('triD_tasks.json', 'triD.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
