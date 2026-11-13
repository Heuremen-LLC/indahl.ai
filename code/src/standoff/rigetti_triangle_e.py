"""TRIANGLE E: PUSHES OR TIME, ON THE UPPER PAIR OF RUNGS (Bones, 2026-10-04). Not a repeat: D held the push count at ten and moved L; E moves the push count at each L, so the
witness/booked gap D showed can be laid against pushes and against time in one batch.
OBSERVER  the seven emitters pushed 1<->2 N = 4 / 10 / 20 times across L = 1 / 2 / 4 us (gap g = L / N, 4 ns grid; each push 32 ns); starts |1>, |2>, |0>.
WITNESS   free clocks (1 / 2 / 3+ links; the upper rung's pull sits at 1 link, §209); references held |1> and held |2> for each L.
TIME      own decay from |2> (0.5 / 1 / 2 / 4 us) and from |1> (1 / 4 us); end state on three rungs after every train (X with the plain read, Y with swap-then-flip).
3 N x 3 L x 3 starts x 2 + 2 held x 3 L x 2 + 6 rulers x 2 + 8 cal = 86 tasks x 900 shots (cal 1500). No outcome written. BINARY CHECKPOINTS asserted: three N, three L, three starts, clocks at 1 / 2 / 3+.
  python rigetti_triangle_e.py dry | submit | collect"""
import math, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
import rigetti_triangle_d as D
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = D.EM; CL = C.CL; SH = 900; SH_CAL = 1500
NS = [4, 10, 20]; LS = [1, 2, 4]; STARTS = ['one', 'two', 'zero']
assert len(NS) >= 3 and len(LS) >= 3 and len(STARTS) >= 3 and all(Counter(min(C.D[q], 3) for q in CL if C.D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint E'
def gap(L, N): return RT._ns(L / N) * 1e6
def circ(fr, s, N, L, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    D.prep(c, fr, s)
    for q in CL: c.rx(q, math.pi / 2)
    if N:
        for _ in range(N):
            RT.wait(c, fr, gap(L, N)); D.up(c, fr)
    else: RT.wait(c, fr, L)
    D.readout(c, fr, hand); return Circuit().add_verbatim_box(c)
def items(fr):
    it = [(['cal', s, 'E'], RT.cal_circ(fr, D.AMPS, s), SH_CAL) for s in RT.SEQS]
    it += [([f'train_{s}', N, L, h], circ(fr, s, N, L, h), SH) for s in STARTS for N in NS for L in LS for h in 'XY']
    it += [([f'held_{s}', 0, L, h], circ(fr, s, 0, L, h), SH) for s in ('one', 'two') for L in LS for h in 'XY']
    it += [([f'ruler_{s}', w, seq], D.ruler(fr, s, w, seq), SH) for s, ws in (('two', D.R2), ('one', D.R1)) for w in ws for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(2026100450).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr); print(f'E: {len(it)} tasks, {sum(n for *_, n in it)} shots; gaps (us) ' + ' '.join(f'N{N}/L{L}:{gap(L, N):.3f}' for N in NS for L in LS))
        if m == 'dry':
            tr = [x for x in it if x[0][:3] == ['train_two', 20, 1] and x[0][3] == 'X'][0][1]; ins = [str(i) for i in tr.instructions]
            print('train_two N20 L1 hand X:', len(ins), 'instructions; pulse gates', sum('PulseGate' in x for x in ins)); return
        RT.guard_and_book('rigetti triangle E: upper-rung train, pushes 4/10/20 x L 1/2/4 us, starts 1/2/0, every clock', it); RT.send(dev, it, 'triE_tasks.json')
    elif m == 'collect': RT.collect('triE_tasks.json', 'triE.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
