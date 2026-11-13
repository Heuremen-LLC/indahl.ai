"""cepheus_proximity.py -- Wayfinder, 7 Oct 2026: "the other qubits act like witnesses based on proximity? ... line of sight if that's a qubit thing".
Second vendor, nothing fired: the P2-R length sweeps on Cepheus (our tone on the seven looked-at qubits' readout frames, four laid lengths 1.0 / 1.5 / 2.0 / 2.5 us,
looks k = 1-4) re-read clock by clock, with the per-clock arithmetic of ladder_widths.py (turn per look / turn per us over the delays = us per look), and each clock
binned three ways:
  LINKS  to the nearest looked-at qubit (rigetti_triangle_c.D);
  SIGHT  straight-line distance on the chip's grid (q = 9 row + column, read off the coupling map: every edge is +1 or +9);
  DOSE   how many looked-at qubits sit within 2 grid pitches of the clock.
Per bin: W/laid averaged over the four lengths, and the clocks' slope across the four lengths (W per us of laid look). Widths: the clocks resampled (300 draws).
Raw, no verdict.   python cepheus_proximity.py [npz:amp ...]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if os.environ.get('DOSE'): import rigetti_look_dose          # the clustered looked-at set (7 Oct), set before the readers import it
import readrigetti_look_lengths as RD
import rigetti_triangle_c as C
L = RD.L; QS = RD.QS; slope = RD.slope; rng = np.random.default_rng(20261007)
XY = {q: (q % 9, q // 9) for q in QS}
EMXY = np.array([XY[q] for q in C.EM])


def sight(q):
    r = np.hypot(*(EMXY - np.array(XY[q])).T); return float(r.min()), int((r <= 2.0 + 1e-9).sum())


RULERS = {
    'links': (lambda q: C.D[q], [(1, 1, '1 link'), (2, 2, '2 links'), (3, 3, '3 links'), (4, 99, '4+ links')]),
    'sight': (lambda q: sight(q)[0], [(0.5, 1.0, '<=1 pitch'), (1.01, 2.0, '<=2 pitch'), (2.01, 3.0, '<=3 pitch'), (3.01, 99, '>3 pitch')]),
    'dose': (lambda q: sight(q)[1], [(0, 0, '0 in sight'), (1, 1, '1 in sight'), (2, 2, '2 in sight'), (3, 3, '3 in sight'), (4, 99, '4+ in sight')]),
}


def per_clock(f, amp):
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
    H = lambda key: (1 - 2 * raw[key + ('X',)].mean(0)) - 1j * (1 - 2 * raw[key + ('Y',)].mean(0))
    ang_d = np.unwrap(np.array([np.angle(H(('delay', 0, 0, d)) / H(('delay', 0, 0, 0))) for d in L.DELAYS]), axis=0)
    rate = np.array([slope(L.DELAYS, ang_d[:, i]) for i in range(len(QS))]); per = {}
    for T in L.TONES:
        ks = [0] + [k for k in (1, 2, 3, 4, 6) if ('look', amp, T, k, 'X') in raw]
        ang = np.unwrap(np.array([np.zeros(len(QS))] + [np.angle(H(('look', amp, T, k)) / H(('delay', 0, 0, 0))) for k in ks[1:]]), axis=0)
        per[T] = np.array([slope(ks, ang[:, i]) for i in range(len(QS))]) / rate
    return per


def stat(per, idx):
    laid = np.array([T + L.LT.RING for T in L.TONES]); med = np.array([np.nanmedian(per[T][idx]) for T in L.TONES])
    return float(np.mean(med / laid)), float(np.polyfit(laid, med, 1)[0])


if __name__ == '__main__':
    files = [(a, float(b)) for a, b in (x.split(':') for x in (sys.argv[1:] or ['lookLengths_s03.npz:0.03', 'lookLengths_s03b.npz:0.03', 'lookLengths_s03_day2.npz:0.03',
                                                                               'lookLengths_s06.npz:0.06', 'lookLengths_tuned.npz:0.12']))]
    P = [(f, a, per_clock(f, a)) for f, a in files]
    for name, (fn, bins) in RULERS.items():
        print(f'\nRULER {name.upper()}  (clocks per bin: ' + ', '.join(f'{lab} {sum(1 for q in C.CL if lo <= fn(q) <= hi)}' for lo, hi, lab in bins) + ')')
        for lo, hi, lab in bins:
            idx = np.array([QS.index(q) for q in C.CL if lo <= fn(q) <= hi])
            if len(idx) < 3: print(f'   {lab:11} too few clocks'); continue
            cells = []
            for f, a, per in P:
                s = stat(per, idx); B = np.array([stat(per, rng.choice(idx, len(idx))) for _ in range(300)]); w = np.nanstd(B, 0)
                cells.append(f'{a:.2f}{"b" if "s03b" in f else "d2" if "day2" in f else ""}: W/laid {s[0]:.3f}+-{w[0]:.3f} slope {s[1]:.3f}+-{w[1]:.3f}')
            print(f'   {lab:11} | ' + ' | '.join(cells))
    if os.environ.get('DOSE'):
        print('\nCENTRE CLOCKS (one clock each, W/laid over the four lengths; slope):')
        for q, lab in ((13, 'plus, 4 at one pitch'), (44, 'T, 3 at one pitch'), (56, 'pair, 2 at one pitch')):
            i = np.array([QS.index(q)]); print(f'   clock {q:3} ({lab:20}, {sight(q)[1]} within 2) | ' + ' | '.join(f'{f.split(".")[0][-2:]}: {stat(per, i)[0]:.3f} slope {stat(per, i)[1]:.3f}' for f, a, per in P))
