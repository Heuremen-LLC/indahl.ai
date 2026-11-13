"""THE LAST 8 TASKS (Bones, 2026-10-04; Wayfinder: "Fire away but don't fuck up... set binary checkpoints"). The same emitter and clocks as 9/28 section 7, read today.
q0 is the emitter, in THREE states: rest / |1> (rx pi) / |2> (rx pi, then today's tuned 1<->2 swap, amplitude from time20261004/tune_fit.json). Every other qubit is a clock:
put half-way, free for 2 us, read on two hands (X: rx pi/2; Y: rz pi/2, rx pi/2). Reference: the clocks at no window with q0 at rest. 8 tasks x 900 shots.
Clocks by links from q0: q1, q9 (1 link; 9/28's pair), 3 at 2 links (q10, 9/28's control, among them), 101 at 3 or more.
The single 2-us window is forced by the budget and set by the clocks' own rulers, with no outcome written: the hand a clock keeps (batch 3: 0.67 at 3 us, falling) and the
+-180 deg a two-hand clock can read before it wraps, held against the largest turn rate on this chip's record (9/28, used here as a ruler, not a call).
BINARY CHECKPOINTS (asserted before anything is built): three emitter states; clocks present at 1, 2 and 3+ links; the day cap from the code; no yes/no gate in the reader.
  python rigetti_q0_last.py dry | submit | collect | read"""
import json, math, os, sys, time
from collections import deque, Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_time as RT
HERE = RT.HERE; OUT = RT.OUT; QS = RT.QS; EMITTER = 0; T_US = 2; SH = 900
STATES = ['rest', 'one', 'two']; HANDS = ['X', 'Y']
FIT = json.load(open(os.path.join(OUT, 'tune_fit.json'))); E = json.load(open(os.path.join(OUT, 'cepheus_edges.json')))['edges']
NB = {q: set() for q in QS}
for a, b in E:
    if a in NB and b in NB: NB[a].add(b); NB[b].add(a)
D = {EMITTER: 0}; dq = deque([EMITTER])
while dq:
    u = dq.popleft()
    for v in NB[u]:
        if v not in D: D[v] = D[u] + 1; dq.append(v)
CLOCKS = [q for q in QS if q != EMITTER]; CLS = Counter(min(D.get(q, 99), 3) for q in CLOCKS)
ITEMS = [(['ref', 'T0', h], 'rest', 0, h) for h in HANDS] + [([s, f'T{T_US}', h], s, T_US, h) for s in STATES for h in HANDS]
# ---- binary checkpoints
assert len(STATES) >= 3, 'emitter needs three states'
assert all(CLS.get(k, 0) > 0 for k in (1, 2, 3)), f'clocks must sit at 1, 2 and 3+ links: {CLS}'
assert FIT[str(EMITTER)]['swing'] > 0.3, 'q0 swap not tuned today'
S = RT.state()
if len(sys.argv) > 1 and sys.argv[1] in ('dry', 'submit'):        # the cap guards spending only; collect and read spend nothing
    assert S['tasks'] + len(ITEMS) <= RT.DAY_CAP_TASKS and S['shots'] + SH * len(ITEMS) <= RT.DAY_CAP_SHOTS, f"past the cap: {S['tasks']} + {len(ITEMS)} tasks"


def circ(fr, state, t, hand):
    from braket.circuits import Circuit
    c = Circuit()
    for q in QS: c.rz(q, 0.0)
    if state in ('one', 'two'): c.rx(EMITTER, math.pi)
    if state == 'two': c.pulse_gate([EMITTER], RT.f12(fr, {EMITTER: FIT[str(EMITTER)]['a_pi12']}))
    for q in CLOCKS: c.rx(q, math.pi / 2)
    RT.wait(c, fr, t)
    if hand == 'Y':
        for q in CLOCKS: c.rz(q, math.pi / 2)
    for q in CLOCKS: c.rx(q, math.pi / 2)
    return Circuit().add_verbatim_box(c)


def main():
    m = sys.argv[1]
    print(f'checkpoints passed: states {STATES}; clocks by links {dict(sorted(CLS.items()))} (3 = 3+); day {S["tasks"]} + {len(ITEMS)} <= {RT.DAY_CAP_TASKS} tasks, {S["shots"]} + {SH * len(ITEMS)} <= {RT.DAY_CAP_SHOTS} shots')
    if m in ('dry', 'submit'):
        dev, fr = RT.dev_frames(); items = [(tag, circ(fr, s, t, h), SH) for tag, s, t, h in ITEMS]
        if m == 'dry':
            c = items[-1][1]; ins = [str(i) for i in c.instructions]
            print('last circuit (q0 in |2>, hand Y):', len(ins), 'instructions; q0 ops:', [x[:80] for x in ins if 'Qubit(0)' in x and 'Qubit(1)' not in x][:6])
            print('q9 ops:', [x[:70] for x in ins if 'Qubit(9)' in x][:6]); return
        RT.guard_and_book('rigetti time: the last 8 -- q0 (rest / |1> / |2>) watched by every clock, 2 us', items); RT.send(dev, items, 'q0_last_tasks.json')
    elif m == 'collect': RT.collect('q0_last_tasks.json', 'q0_last.npz')
    elif m == 'read':
        Z = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(OUT, 'q0_last.npz')).items()}
        p1 = lambda tag: Z[tag].mean(0); H = lambda a, t: (1 - 2 * p1((a, t, 'X'))) - 1j * (1 - 2 * p1((a, t, 'Y')))
        H0 = H('ref', 'T0'); idx = {q: QS.index(q) for q in QS}
        print('q0 plain read P(1): rest %.3f | |1> %.3f | |2> %.3f (|2> reads mostly as 1 on this readout)' % tuple(p1((s, f'T{T_US}', 'X'))[idx[0]] for s in STATES))
        rng = np.random.default_rng(2026100499)
        def turn(s, q):
            i = idx[q]; a = np.angle(H(s, f'T{T_US}')[i] / H('rest', f'T{T_US}')[i]); return np.degrees(a) / T_US
        def width(s, q):
            i = idx[q]; v = []
            for _ in range(200):
                Zb = {k: x[rng.integers(0, x.shape[0], x.shape[0])] for k, x in Z.items()}
                pb = lambda tag: Zb[tag].mean(0); Hb = lambda a, t: (1 - 2 * pb((a, t, 'X'))) - 1j * (1 - 2 * pb((a, t, 'Y')))
                v.append(np.degrees(np.angle(Hb(s, f'T{T_US}')[i] / Hb('rest', f'T{T_US}')[i])) / T_US)
            return np.std(v)
        kept = lambda q: abs(H('rest', f'T{T_US}')[idx[q]] / H0[idx[q]])
        print(f'pull on each clock, deg per us over {T_US} us, q0 in |1> and in |2> minus at rest (every clock read; hand kept at rest beside it):')
        for q in sorted(CLOCKS, key=lambda q: (D.get(q, 99), q)):
            if D.get(q, 99) <= 2: print(f'   q{q:<3} {D[q]} link(s): |1> {turn("one", q):+7.2f} +- {width("one", q):5.2f} | |2> {turn("two", q):+8.2f} +- {width("two", q):5.2f} | hand kept {kept(q):.2f}')
        far = [q for q in CLOCKS if D.get(q, 99) >= 3]; t1 = np.array([turn('one', q) for q in far]); t2 = np.array([turn('two', q) for q in far]); k = np.array([kept(q) for q in far])
        band = np.argsort(np.argsort(k)) * 3 // len(far)
        print(f'   3+ links ({len(far)} clocks): |1> median {np.median(t1):+.2f} [quartiles {np.percentile(t1, 25):+.2f}, {np.percentile(t1, 75):+.2f}] | |2> median {np.median(t2):+.2f} [{np.percentile(t2, 25):+.2f}, {np.percentile(t2, 75):+.2f}]')
        print('   3+ links by hand-kept band low / mid / high: |2> ' + ' / '.join(f'{np.median(t2[band == b]):+.2f}' for b in range(3)) + ' | hand ' + ' / '.join(f'{np.median(k[band == b]):.2f}' for b in range(3)))
    else: print(__doc__)


if __name__ == '__main__':
    main()
