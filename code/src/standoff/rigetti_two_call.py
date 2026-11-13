"""TWO'S CALL ON CEPHEUS (Bones, 2026-10-04 evening; Wayfinder: "CLOSE THE TRIANGLES PROOVE THE BONEFISH"). The call is written and hashed before this run:
parallax/darkwave_disco/calls/TWO_CALL_CEPHEUS_20261004.txt (sha256 8156c88650870b97...): crossing 8.33 / 5.15 / 3.18 / 1.97 / 1.22 % at spacings phi^0 / phi^2 / phi^4 / phi^6 / phi^8 us.
OBSERVER  the laid spacings 1 / 2.618 / 6.854 / 17.944 / 46.979 us, ten X pushes, every qubit; starts |0> (the call), |1>, halfway; back-to-back pushes (no time) for |0> and |1>.
TIME      each qubit's own decay over each spacing (|1> left that long), three copies spread through the batch; the batch's 8-sequence readout model; idle |0>.
WITNESS   the three copies of the ruler against each other, and the |1> start as the crossing's mirror.
(3 x 5 + 2) arms x 2 reads + 5 x 3 rulers x 2 + idle x 2 + 8 cal = 74 tasks x 900 shots (cal 1500). BINARY CHECKPOINTS asserted: five spacings, three starts, three ruler copies.
  python rigetti_two_call.py dry | submit | collect"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangles as T
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9
PHI = (1 + 5 ** .5) / 2
SP = [round(PHI ** (2 * n), 3) for n in range(5)]; STARTS = ['OFF', 'ON', 'MID']; COPIES = 'abc'; SH = 900; SH_CAL = 1500
assert len(SP) >= 3 and len(STARTS) >= 3 and len(COPIES) >= 3, 'binary checkpoint TWO'
def arms():
    A = [{'key': f'{s}|g{g}', 'start': s, 'gap': g, 'pushes': RT.PUSHES} for s in STARTS for g in SP]
    A += [{'key': f'{s}|g0', 'start': s, 'gap': 0, 'pushes': RT.PUSHES} for s in ('OFF', 'ON')]
    A += [{'key': f'RULER|ON|w{g}|{cp}', 'start': 'ON', 'gap': None, 'wait': g} for cp in COPIES for g in SP]
    A.append({'key': 'RULER|OFF|w46.979', 'start': 'OFF', 'gap': None, 'wait': SP[-1]})
    return A
def items(fr):
    it = [(['cal', s], RT.cal_circ(fr, T.AMPS, s), SH_CAL) for s in RT.SEQS]
    it += [([a['key'], seq], RT.build(fr, T.AMPS, a, seq), SH) for a in arms() for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(2026100492).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr)
        print(f'TWO CALL: {len(it)} tasks, {sum(n for *_, n in it)} shots, est ${len(it) * RT.PER_TASK + sum(n for *_, n in it) * RT.PER_SHOT:.2f}; spacings {SP} us')
        if m == 'dry':
            ins = [str(i) for i in [x for x in it if x[0] == ['OFF|g6.854', 'ba']][0][1].instructions]; print('OFF g6.854 ba:', len(ins), 'instr; pulse gates', sum('PulseGate' in x for x in ins)); return
        RT.guard_and_book('rigetti TWO CALL: ten pushes at phi^2n spacings, own-interval rulers x3, call hashed first', it); RT.send(dev, it, 'two_tasks.json')
    elif m == 'collect': RT.collect('two_tasks.json', 'two.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
