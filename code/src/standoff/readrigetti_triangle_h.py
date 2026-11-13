"""readrigetti_triangle_h.py -- triangle H: the emitters' state at readout inside the clocks' read. Raw, no verdict, nothing cut.
LATE  turn (deg) and hand ratio of emitter-late |1>, |2> against |0>, per window, 1 / 2 / 3+ links (medians, quartiles).
PAIR  on the held-|2> arm: the day's pairing (X plain, Y swap-then-flip) against both-plain and both-swap-then-flip: turn offset (deg) and that offset as deg/us of the window."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rigetti_triangle_c as C
import rigetti_triangle_h as Hh
QS = Hh.QS; idx = {q: QS.index(q) for q in QS}
LINK = {k: [idx[q] for q in C.CL if C.D[q] and min(C.D[q], 3) == k] for k in (1, 2, 3)}
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, 'triH.npz')).items()}
P = lambda key: raw[key].mean(0)
def show(nm, a, w=None):
    out = []
    for k in (1, 2, 3):
        x = np.degrees(a[LINK[k]]); s = f'{k}{"+" if k == 3 else ""} link {np.median(x):+7.2f} [{np.percentile(x, 25):+.2f}, {np.percentile(x, 75):+.2f}]'
        if w: s += f' = {np.median(x) / w:+.2f} deg/us'
        out.append(s)
    print(f'    {nm}: ' + ' | '.join(out))
print('LATE: emitters at rest through the window, put in |1> / |2> at readout, against |0> (turn deg; hand ratio median, all clocks)')
for w in Hh.WIN:
    H = {s: (1 - 2 * P(('late', s, w, 'X'))) - 1j * (1 - 2 * P(('late', s, w, 'Y'))) for s in Hh.LATE}
    print(f'  window {w} us; hand kept |0> late {np.median(np.abs(H["zero"])):.3f}')
    for s in ('one', 'two'):
        show(f'late |{1 if s == "one" else 2}> turn', np.angle(H[s] / H['zero'])); print(f'      hand ratio {np.median(np.abs(H[s]) / np.abs(H["zero"])):.4f}')
print('PAIR: held-|2> arm, the day\'s pairing (X plain, Y swap-then-flip) against the other two')
for w in Hh.WIN:
    Hp = lambda sx, sy: (1 - 2 * P(('pair', sx, w, 'X'))) - 1j * (1 - 2 * P(('pair', sy, w, 'Y')))
    day = Hp('e', 'ba'); print(f'  window {w} us')
    show('day vs both-plain   ', np.angle(day / Hp('e', 'e')), w); show('day vs both-swapflip', np.angle(day / Hp('ba', 'ba')), w)
