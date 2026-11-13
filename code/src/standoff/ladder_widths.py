"""ladder_widths.py -- the strength ladder (0.03 / 0.06 / 0.12) with widths: the same per-clock reads as readrigetti_look_lengths.py, resampled over the
100 witness clocks (300 draws) for every median, the across-lengths line, and our look over the no-look check."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
import readrigetti_look_lengths as RD
L = RD.L; QS = RD.QS; cl = RD.cl; slope = RD.slope; rng = np.random.default_rng(20261006)
for f, amp in [(a, float(b)) for a, b in (x.split(':') for x in (sys.argv[1:] or ['lookLengths_s03.npz:0.03', 'lookLengths_s06.npz:0.06', 'lookLengths_tuned.npz:0.12']))]:
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
    H = lambda key: (1 - 2 * raw[key + ('X',)].mean(0)) - 1j * (1 - 2 * raw[key + ('Y',)].mean(0))
    ang_d = np.unwrap(np.array([np.angle(H(('delay', 0, 0, d)) / H(('delay', 0, 0, 0))) for d in L.DELAYS]), axis=0)
    rate = np.array([slope(L.DELAYS, ang_d[:, i]) for i in range(len(QS))]); per = {}
    for T in L.TONES + ['check']:
        key = (lambda k: ('look', amp, T, k)) if T != 'check' else (lambda k: ('check', 0.0, 1.0, k)); ks = [0] + ([1, 2, 3, 4] if T != 'check' else L.CHECK_KS)
        ang = np.unwrap(np.array([np.zeros(len(QS))] + [np.angle(H(key(k)) / H(('delay', 0, 0, 0))) for k in ks[1:]]), axis=0)
        per[T] = (np.array([slope(ks, ang[:, i]) for i in range(len(QS))]) / rate)[cl]
    laid = {T: (1.0 if T == 'check' else T) + L.LT.RING for T in per}
    def stat(idx):
        med = {T: np.nanmedian(v[idx]) for T, v in per.items()}; x = np.array([laid[T] for T in L.TONES]); y = np.array([med[T] for T in L.TONES])
        m, c = np.polyfit(x, y, 1); look = np.mean([med[T] / laid[T] for T in L.TONES]); return m, c, look, med['check'] / laid['check'], look / (med['check'] / laid['check'])
    s0 = stat(np.arange(len(cl))); B = np.array([stat(rng.integers(0, len(cl), len(cl))) for _ in range(300)]); w = np.nanstd(B, 0)
    print(f'strength {amp:.2f}: slope {s0[0]:.3f} +- {w[0]:.3f} | intercept {s0[1]:+.3f} +- {w[1]:.3f} us | our look W/laid {s0[2]:.3f} +- {w[2]:.3f} | no-look check {s0[3]:.3f} +- {w[3]:.3f} | look / check {s0[4]:.3f} +- {w[4]:.3f}')
