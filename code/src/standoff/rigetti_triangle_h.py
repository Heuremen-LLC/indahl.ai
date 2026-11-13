"""TRIANGLE H: THE REVERSE ROAD, THE EMITTERS INSIDE THE CLOCKS' READ (Bones, 2026-10-04). Not a repeat: G showed the clocks' state at readout scaling the emitters' read (§215). Every witness number
today paired hand X with the emitters' plain read and hand Y with their swap-then-flip read, so the emitters stood in different states at the clocks' X and Y reads. H measures that road.
OBSERVER  clocks half-way for 0.5 / 2 / 4 us with the emitters at rest through the window; at readout the emitters are put in |0>, |1> or |2> (late), on both hands.
WITNESS   the clocks' turn and hand kept, emitter-late |1> and |2> against |0>, per clock, 1 / 2 / 3+ links (a readout offset, deg, not deg/us).
TIME      the pairing used all day, on the held-|2> arm (emitters in |2> through the window): hands paired (X plain, Y swap-then-flip) vs (both plain) vs (both swap-then-flip), at each window.
3 late x 2 hands x 3 windows + 4 pairings x 3 windows = 30 tasks x 1500 shots. No outcome written. BINARY CHECKPOINTS asserted: three late states, three windows, three pairings beyond the day's.
  python rigetti_triangle_h.py dry | submit | collect"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
import rigetti_triangle_d as D
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = D.EM; CL = C.CL; SH = 1500
LATE = ['zero', 'one', 'two']; WIN = [0.5, 2, 4]; PAIR = [('e', 'X'), ('e', 'Y'), ('ba', 'X'), ('ba', 'Y')]
assert len(LATE) >= 3 and len(WIN) >= 3 and len(PAIR) >= 4, 'binary checkpoint H'
def clocks_out(c, hand):
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
def late(fr, s, w, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    for q in CL: c.rx(q, math.pi / 2)
    RT.wait(c, fr, w); clocks_out(c, hand); D.prep(c, fr, s); return Circuit().add_verbatim_box(c)
def paired(fr, w, seq, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    D.prep(c, fr, 'two')
    for q in CL: c.rx(q, math.pi / 2)
    RT.wait(c, fr, w); clocks_out(c, hand)
    if seq == 'ba':
        D.up(c, fr)
        for q in EM: c.rx(q, math.pi)
    return Circuit().add_verbatim_box(c)
def items(fr):
    it = [(['late', s, w, h], late(fr, s, w, h), SH) for s in LATE for w in WIN for h in 'XY']
    it += [(['pair', seq, w, h], paired(fr, w, seq, h), SH) for seq, h in PAIR for w in WIN]
    return [it[i] for i in np.random.default_rng(2026100480).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr); print(f'H: {len(it)} tasks, {sum(n for *_, n in it)} shots')
        if m == 'dry':
            for tag in (['late', 'two', 2, 'Y'], ['pair', 'ba', 2, 'X']):
                ins = [str(i) for i in [x for x in it if x[0] == tag][0][1].instructions]
                print(' ', tag, len(ins), 'instr; q7 (emitter):', [x.split("'operator': ")[1][:20] for x in ins if 'Qubit(7)' in x and "qubit_count': 107" not in x],
                      '| q9 (clock):', [x.split("'operator': ")[1][:20] for x in ins if 'Qubit(9)' in x and "qubit_count': 107" not in x])
            return
        RT.guard_and_book('rigetti triangle H: emitters inside the clocks read, late 0/1/2 x 3 windows, 4 pairings', it); RT.send(dev, it, 'triH_tasks.json')
    elif m == 'collect': RT.collect('triH_tasks.json', 'triH.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
