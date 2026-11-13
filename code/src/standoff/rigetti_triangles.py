"""TWO TRIANGLES ON CEPHEUS (Bones, 2026-10-04; Wayfinder: "we can spend to the end, but it better be a fucking triangle"). Neither repeats a run already made.
A. THE q9 TRIANGLE, all three seats in one batch. OBSERVER: q0 put at rest / in |1> / in |2>, laid windows 0.5 / 1 / 2 / 4 / 6 us (9/28's ladder). WITNESS: every other qubit a clock, read on two hands
   (X paired with q0's plain read, Y with q0's swap-then-flip read), at 1 / 2 / 3+ links. TIME: q0's own |2> population after each window, from its rung-2 read (this batch's readout model): the seat that was empty.
   8 cal + 2 reference (no window) + 5 windows x 3 states x 2 = 40 tasks x 900 shots (cal 1500).
B. THE PUSH JUMP, NEIGHBOURS FROM TIME. The seven emitters of batch 3 get ten pushes back to back from |0>, read plain and through swap-then-flip; their neighbours in THREE states, interleaved in one round:
   at rest / pushed in step / held half-way as clocks. THREE rounds, minutes apart (time); each round its own 8-sequence readout calibration (observer). 3 x (8 + 3 x 2) = 42 tasks.
No outcome written for either. BINARY CHECKPOINTS asserted below: three states / five windows / clocks at 1, 2, 3+ links (A); three neighbour states / three rounds (B); the cap from the code.
CAP: 174 + 8 (the day so far) + 82 = 264 tasks; 179,000 + 121,800 = 300,800 shots.  python rigetti_triangles.py A-dry | A-submit | A-collect | B-dry | B-submit | B-collect"""
import json, math, os, sys, time
from collections import deque, Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
RT.DAY_CAP_TASKS, RT.DAY_CAP_SHOTS = 264, 300800
OUT = RT.OUT; QS = RT.QS; SH = 900; SH_CAL = 1500
FIT = json.load(open(os.path.join(OUT, 'tune_fit.json'))); AMPS = {q: (FIT[str(q)]['a_pi12'] if FIT[str(q)]['swing'] > 0.3 else 0.0) for q in QS}
E = json.load(open(os.path.join(OUT, 'cepheus_edges.json')))['edges']; NB = {q: set() for q in QS}
for a, b in E:
    if a in NB and b in NB: NB[a].add(b); NB[b].add(a)
# ---------- A
Q0 = 0; A_STATES = ['rest', 'one', 'two']; A_WIN = [0.5, 1, 2, 4, 6]; A_CLOCKS = [q for q in QS if q != Q0]
D = {Q0: 0}; dq = deque([Q0])
while dq:
    u = dq.popleft()
    for v in NB[u]:
        if v not in D: D[v] = D[u] + 1; dq.append(v)
assert len(A_STATES) >= 3 and len(A_WIN) >= 3 and all(Counter(min(D.get(q, 99), 3) for q in A_CLOCKS).get(k, 0) > 0 for k in (1, 2, 3)), 'checkpoint A'
assert FIT[str(Q0)]['swing'] > 0.3, 'q0 swap not tuned'
def a_circ(fr, state, w, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if state in ('one', 'two'): c.rx(Q0, math.pi)
    if state == 'two': c.pulse_gate([Q0], RT.f12(fr, {Q0: AMPS[Q0]}))
    for q in A_CLOCKS: c.rx(q, math.pi / 2)
    RT.wait(c, fr, w)
    if hand == 'Y':
        for q in A_CLOCKS: c.rz(q, math.pi / 2)
    for q in A_CLOCKS: c.rx(q, math.pi / 2)
    if hand == 'Y':                                                   # q0's swap-then-flip read rides with hand Y
        c.pulse_gate([Q0], RT.f12(fr, {Q0: AMPS[Q0]})); c.rx(Q0, math.pi)
    return Circuit().add_verbatim_box(c)
def a_items(fr):
    it = [(['cal', s, 'A'], RT.cal_circ(fr, AMPS, s), SH_CAL) for s in RT.SEQS] + [(['ref', 0, h], a_circ(fr, 'rest', 0, h), SH) for h in 'XY']
    it += [([st, w, h], a_circ(fr, st, w, h), SH) for st in A_STATES for w in A_WIN for h in 'XY']
    return it
# ---------- B
R = json.load(open(os.path.join(OUT, 'wit_roles.json'))); EM = R['emitters']; NBRS = sorted({n for q in EM for n in NB[q]} - set(EM))
B_STATES = ['rest', 'pushed', 'clock']; B_ROUNDS = [1, 2, 3]
assert len(B_STATES) >= 3 and len(B_ROUNDS) >= 3, 'checkpoint B'
def b_circ(fr, nstate, seq):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if nstate == 'clock':
        for q in NBRS: c.rx(q, math.pi / 2)
    for _ in range(RT.PUSHES):
        for q in EM: c.rx(q, math.pi)
        if nstate == 'pushed':
            for q in NBRS: c.rx(q, math.pi)
    if nstate == 'clock':
        for q in NBRS: c.rx(q, math.pi / 2)
    for ch in ('' if seq == 'e' else seq):
        if ch == 'a':
            for q in EM: c.rx(q, math.pi)
        else: c.pulse_gate(EM, RT.f12(fr, {q: AMPS[q] for q in EM}))
    return Circuit().add_verbatim_box(c)
def b_round(fr, r):
    it = [(['cal', s, r], RT.cal_circ(fr, AMPS, s), SH_CAL) for s in RT.SEQS] + [([ns, seq, r], b_circ(fr, ns, seq), SH) for ns in B_STATES for seq in ('e', 'ba')]
    return [it[i] for i in np.random.default_rng(202610050 + r).permutation(len(it))]
def main():
    m = sys.argv[1]; S = RT.state()
    if m in ('A-dry', 'A-submit'):
        dev, fr = RT.dev_frames(); items = a_items(fr); items = [items[i] for i in np.random.default_rng(20261005).permutation(len(items))]
        print(f'A: {len(items)} tasks, {sum(n for *_, n in items)} shots | clocks by links from q0 {dict(sorted(Counter(min(D.get(q, 99), 3) for q in A_CLOCKS).items()))} | day {S["tasks"]} / {RT.DAY_CAP_TASKS}')
        if m == 'A-dry':
            ins = [str(i) for i in items[0][1].instructions]; print('first circuit', items[0][0], len(ins), 'instructions; q0 ops:', [x[:70] for x in ins if 'Qubit(0)' in x and 'Qubit(1)' not in x]); return
        RT.guard_and_book('rigetti triangles A: q0 rest/1/2 x windows 0.5-6 us, every clock, q0 rung 2 read', items); RT.send(dev, items, 'triA_tasks.json')
    elif m == 'A-collect': RT.collect('triA_tasks.json', 'triA.npz')
    elif m in ('B-dry', 'B-submit'):
        dev, fr = RT.dev_frames(); print(f'B: emitters {EM}, their neighbours {len(NBRS)}; per round {8 + 6} tasks x 3 rounds | day {S["tasks"]} / {RT.DAY_CAP_TASKS}')
        if m == 'B-dry':
            it = b_round(fr, 1); ins = [str(i) for i in [x for x in it if x[0][0] == 'clock'][0][1].instructions]; print('clock-state circuit:', len(ins), 'instructions'); return
        allit = [b_round(fr, r) for r in B_ROUNDS]
        RT.guard_and_book('rigetti triangles B: 7 emitters pushed, neighbours rest/pushed/clock, 3 rounds', [x for it in allit for x in it])
        T = {'tasks': []}
        for r, it in zip(B_ROUNDS, allit):
            if r > 1: time.sleep(180)
            for tag, cc, n in it:
                t = dev.run(cc, shots=n, disable_qubit_rewiring=True); T['tasks'].append({'tag': tag, 'arn': t.id, 'sent': time.time()})
            json.dump(T, open(os.path.join(OUT, 'triB_tasks.json'), 'w'), indent=1); print('round', r, 'sent', flush=True)
    elif m == 'B-collect': RT.collect('triB_tasks.json', 'triB.npz')
    else: print(__doc__)
if __name__ == '__main__':
    main()
