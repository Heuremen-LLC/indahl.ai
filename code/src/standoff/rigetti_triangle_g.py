"""TRIANGLE G: THE WITNESS IN THE CLOCK'S TIME SEAT (Bones, 2026-10-04). Not a repeat: F read the emitters' |2> lower and |1> higher with the clocks running than D/E did with the clocks at
rest (§213). G lays the witnesses' state as the variable, and splits the window from the readout.
OBSERVER  the seven emitters held in |1> or |2> for 0.5 / 2 / 4 us; the other qubits in five states: rest | half-way during the window then swung back to |0> (rx 2pi in all) | F's copy (half-way, half-way
          again at the end) | |1> throughout | rest during the window, |1> only at readout.
TIME      the emitters' own populations on three rungs, solved with THREE readout models laid beside each other: the shared one (every qubit runs the 8 sequences), emitters-only with the others at
          rest, emitters-only with the others in |1>.
WITNESS   the five clock states themselves: what the emitters read depends on, or doesn't, where the clocks are during the window and where they are at readout.
5 x 2 x 3 x 2 = 60 arms x 1500 shots + 3 x 8 cal x 1500 = 84 tasks. No outcome written. BINARY CHECKPOINTS asserted: five clock states, three windows, three readout models.
  python rigetti_triangle_g.py dry | submit | collect"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangle_c as C
import rigetti_triangle_d as D
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
QS = RT.QS; EM = D.EM; CL = C.CL; SH = 1500
CLK = ['rest', 'back', 'fcopy', 'one', 'late']; WIN = [0.5, 2, 4]; MODELS = ['shared', 'em_rest', 'em_one']
assert len(CLK) >= 3 and len(WIN) >= 3 and len(MODELS) >= 3, 'binary checkpoint G'
def em_read(c, fr, seq):
    for ch in ('' if seq == 'e' else seq):
        if ch == 'a':
            for q in EM: c.rx(q, math.pi)
        else: D.up(c, fr)
def circ(fr, ck, s, w, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    D.prep(c, fr, s)
    if ck in ('back', 'fcopy'):
        for q in CL: c.rx(q, math.pi / 2)
    elif ck == 'one':
        for q in CL: c.rx(q, math.pi)
    RT.wait(c, fr, w)
    if ck in ('back', 'fcopy'):
        for q in CL: c.rx(q, math.pi / 2)
    if ck in ('back', 'late'):
        for q in CL: c.rx(q, math.pi)
    em_read(c, fr, seq); return Circuit().add_verbatim_box(c)
def cal_em(fr, ck, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if ck == 'one':
        for q in CL: c.rx(q, math.pi)
    em_read(c, fr, seq); return Circuit().add_verbatim_box(c)
def items(fr):
    it = [(['cal_shared', s], RT.cal_circ(fr, D.AMPS, s), SH) for s in RT.SEQS]
    it += [([f'cal_em_{ck}', s], cal_em(fr, ck, s), SH) for ck in ('rest', 'one') for s in RT.SEQS]
    it += [([ck, s, w, seq], circ(fr, ck, s, w, seq), SH) for ck in CLK for s in ('one', 'two') for w in WIN for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(2026100470).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr); print(f'G: {len(it)} tasks, {sum(n for *_, n in it)} shots')
        if m == 'dry':
            for ck in CLK:
                tr = [x for x in it if x[0] == [ck, 'two', 2, 'ba']][0][1]; ins = [str(i) for i in tr.instructions]
                print(f'  {ck:<6} two w2 ba: {len(ins)} instr; q9 (a clock) ops:', [x.split("'operator': ")[1][:22] for x in ins if 'Qubit(9)' in x and "qubit_count': 107" not in x])
            return
        RT.guard_and_book('rigetti triangle G: the witness in the time seat, 5 clock states x |1>/|2> x 3 windows, 3 readout models', it); RT.send(dev, it, 'triG_tasks.json')
    elif m == 'collect': RT.collect('triG_tasks.json', 'triG.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
