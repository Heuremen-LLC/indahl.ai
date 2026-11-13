"""cepheus_clock_triangle.py -- the clocks triangulated on Cepheus (7 Oct 2026; Wayfinder: "triangulate the qubits clocks ... always triangle"). For each clock, on each
of the four laid lengths: OBSERVER = the laid look (tone + 0.5 us); PHASE = turn per look / turn per us over the delays (as all night); HAND = hand kept per look read as
laid time on the clock's own hand-fade over the delays (log-line 0-15 us); and the HAND RULER AS AN OBJECT beside it: an honest synthetic clock with the clock's own fitted
fade exp(-(t/tau)^beta), looks costing exactly the laid time, read by the same hand ruler. Binned by looked-at qubits within 2 grid pitches. Raw, no verdict.
  [DOSE=1] python cepheus_clock_triangle.py npz:amp [npz:amp ...]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
from scipy.optimize import curve_fit
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if os.environ.get('DOSE'): import rigetti_look_dose
import readrigetti_look_lengths as RD
import rigetti_triangle_c as C
import cepheus_proximity as CP
L = RD.L; QS = RD.QS; slope = RD.slope; DL = np.array(L.DELAYS, float)


def clocks(f, amp):
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
    H = lambda key: (1 - 2 * raw[key + ('X',)].mean(0)) - 1j * (1 - 2 * raw[key + ('Y',)].mean(0))
    h0 = H(('delay', 0, 0, 0)); Hd = np.array([H(('delay', 0, 0, d)) / h0 for d in L.DELAYS])
    rate = np.array([slope(DL, np.unwrap(np.angle(Hd[:, i]))) for i in range(len(QS))])
    hand_d = np.clip(np.abs(Hd), 1e-3, None); g = np.array([np.polyfit(DL, np.log(hand_d[:, i]), 1)[0] for i in range(len(QS))])
    fits = {}
    for i in range(len(QS)):
        try: fits[i] = curve_fit(lambda t, tau, b: np.exp(-(t / tau) ** b), DL[1:], np.clip(hand_d[1:, i], 1e-3, 1.5), p0=[15, 1.2], bounds=([0.5, 0.3], [1e4, 3]))[0]
        except Exception: pass
    out = {}
    for T in L.TONES:
        laid = T + L.LT.RING; ks = [k for k in (1, 2, 3, 4, 6) if ('look', amp, T, k, 'X') in raw]; K = np.array(ks, float)
        Hk = np.array([H(('look', amp, T, k)) / h0 for k in ks])
        ph = np.array([slope([0] + ks, np.unwrap(np.r_[0, np.angle(Hk[:, i])])) for i in range(len(QS))]) / rate
        hd = np.array([slope(K, np.log(np.clip(np.abs(Hk[:, i]), 1e-3, None)) / g[i]) if g[i] < 0 else np.nan for i in range(len(QS))])
        hon = np.full(len(QS), np.nan)
        for i, (tau, b) in fits.items():
            ff = lambda t: np.exp(-(np.asarray(t, float) / tau) ** b); gg = np.polyfit(DL, np.log(np.clip(ff(DL), 1e-3, None)), 1)[0]
            if gg < 0: hon[i] = slope(K, np.log(np.clip(ff(K * laid), 1e-3, None)) / gg)
        out[T] = dict(laid=laid, ph=ph / laid, hd=hd / laid, hon=hon / laid)
    return out


if __name__ == '__main__':
    files = [(a, float(b)) for a, b in (x.split(':') for x in sys.argv[1:])]
    n2 = {q: CP.sight(q)[1] for q in C.CL}
    for f, amp in files:
        R = clocks(f, amp); print(f'\n{f} (strength {amp}): medians over clocks, mean over the four lengths')
        for lo, hi, lab in ((0, 0, '0 in sight'), (1, 1, '1 in sight'), (2, 2, '2 in sight'), (3, 3, '3 in sight'), (4, 99, '4+ in sight')):
            idx = np.array([QS.index(q) for q in C.CL if lo <= n2[q] <= hi])
            if len(idx) < 2: continue
            m = {s: np.mean([np.nanmedian(R[T][s][idx]) for T in L.TONES]) for s in ('ph', 'hd', 'hon')}
            rh = np.mean([np.nanmedian(R[T]['hd'][idx] / R[T]['hon'][idx]) for T in L.TONES])
            print(f'   {lab:11} n {len(idx):3} | PHASE/laid {m["ph"]:.3f} | HAND/laid {m["hd"]:.3f} | ruler on honest {m["hon"]:.3f} | HAND real/honest {rh:.3f} | HAND/PHASE {m["hd"] / m["ph"]:.3f} '
                  f'| [{CP_b(m["ph"]) if False else ""}]')
