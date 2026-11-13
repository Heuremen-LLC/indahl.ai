"""TRIANGLE C: THE CROSSING ON CEPHEUS WITH A WITNESS THAT OUTLASTS IT (Bones, 2026-10-04; Wayfinder: "fire at will... triangles only"). Not a repeat: batch 3's free clocks forgot in ~10 us;
these clocks are ECHOED (pi at the end of the train), so static detuning cancels and what stays is what the emitters did while the clocks ran.
OBSERVER  the laid train: the seven emitters of batch 3 from |0>, ten pushes a pulse every g = 0.5 / 1 / 2 us (train L = 5 / 10 / 20 us), then idle L.
WITNESS   every other qubit an echoed clock: half-way at 0, pi at L (the train's end), read at 2L on two hands; references at each L: emitters held in |1> for the first half then flipped back (the pull scale),
          and emitters at rest (the baseline). The emitters' |1> time during the train, as the clocks read it = (train - rest) / ((held - rest) / L). Clocks by links to the nearest emitter, 1 / 2 / 3+.
TIME      each emitter's own decay (|1> left 1 / 5 / 10 / 20 us) and its end state after the train, on three rungs (this batch's readout model; X pairs with the plain read, Y with swap-then-flip).
3 L x 3 arms x 2 + 4 x 2 + 8 cal = 34 tasks x 900 shots (cal 1500). No outcome written. BINARY CHECKPOINTS asserted: three train lengths, three arms, clocks at 1 / 2 / 3+ links, four ruler waits.
  python rigetti_triangle_c.py dry | submit | collect"""
import json, math, os, sys
from collections import deque, Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
import rigetti_triangles as T
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 10 ** 6, 10 ** 9          # Wayfinder: no budget of mine; "until Capital One tells us to stop" -- spend still booked per stage in braket_ledger.json
OUT = RT.OUT; QS = RT.QS; EM = T.EM; CL = [q for q in QS if q not in EM]; AMPS = T.AMPS; SH = 900; SH_CAL = 1500
GAPS = [0.5, 1, 2]; ARMS = ['train', 'held', 'rest']; EMRULER = [1, 5, 10, 20]
D = {}
for q in CL:
    seen = {q: 0}; dq = deque([q]); best = None
    while dq:
        u = dq.popleft()
        if u in EM: best = seen[u]; break
        for v in T.NB[u]:
            if v not in seen: seen[v] = seen[u] + 1; dq.append(v)
    D[q] = best
assert len(GAPS) >= 3 and len(ARMS) >= 3 and len(EMRULER) >= 3 and all(Counter(min(D[q], 3) for q in CL if D[q]).get(k, 0) > 0 for k in (1, 2, 3)), 'binary checkpoint C'
def circ(fr, arm, g, hand):
    from braket.circuits import Circuit
    L = 10 * g; c = Circuit()
    for q in QS: c.rz(q, 0.0)
    for q in CL: c.rx(q, math.pi / 2)
    if arm == 'train':
        for _ in range(RT.PUSHES):
            RT.wait(c, fr, g)
            for q in EM: c.rx(q, math.pi)
    elif arm == 'held':
        for q in EM: c.rx(q, math.pi)
        RT.wait(c, fr, L)
        for q in EM: c.rx(q, math.pi)
    else: RT.wait(c, fr, L)
    for q in CL: c.rx(q, math.pi)                       # the echo, at the train's end
    RT.wait(c, fr, L)
    if hand == 'Y':
        for q in CL: c.rz(q, math.pi / 2)
    for q in CL: c.rx(q, math.pi / 2)
    if hand == 'Y':
        c.pulse_gate(EM, RT.f12(fr, {q: AMPS[q] for q in EM}))
        for q in EM: c.rx(q, math.pi)
    return Circuit().add_verbatim_box(c)
def ruler(fr, w, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    for q in EM: c.rx(q, math.pi)
    RT.wait(c, fr, w)
    for ch in ('' if seq == 'e' else seq):
        if ch == 'a':
            for q in EM: c.rx(q, math.pi)
        else: c.pulse_gate(EM, RT.f12(fr, {q: AMPS[q] for q in EM}))
    return Circuit().add_verbatim_box(c)
def items(fr):
    it = [(['cal', s, 'C'], RT.cal_circ(fr, AMPS, s), SH_CAL) for s in RT.SEQS]
    it += [([a, g, h], circ(fr, a, g, h), SH) for a in ARMS for g in GAPS for h in 'XY']
    it += [(['emruler', w, s], ruler(fr, w, s), SH) for w in EMRULER for s in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(2026100430).permutation(len(it))]
def main():
    m = sys.argv[1]
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); it = items(fr)
        print(f'C: {len(it)} tasks, {sum(n for *_, n in it)} shots; emitters {EM}; clocks by links {dict(sorted(Counter(min(D[q], 3) for q in CL if D[q]).items()))}')
        if m == 'dry':
            tr = [x for x in it if x[0][0] == 'train' and x[0][1] == 1 and x[0][2] == 'Y'][0][1]; ins = [str(i) for i in tr.instructions]
            print('train g=1 hand Y:', len(ins), 'instructions; q9 (a clock) ops:', [x[:60] for x in ins if 'Qubit(9)' in x and 'qubit_count\': 107' not in x][:8]); return
        RT.guard_and_book('rigetti triangle C: crossing with echoed witnesses, 7 emitters, L 5/10/20 us', it); RT.send(dev, it, 'triC_tasks.json')
    elif m == 'collect': RT.collect('triC_tasks.json', 'triC.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
