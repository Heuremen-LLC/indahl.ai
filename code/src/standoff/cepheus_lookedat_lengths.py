"""cepheus_lookedat_lengths.py -- the READOUT MODEL's third (and fourth) length (ledger §339: T = s (O - d), two IBM lengths fit it by construction). Cepheus length sweeps,
already in hand: the looked-at qubits start in |1>, take k looks of our tone (laid 1.0 / 1.5 / 2.0 / 2.5 us), and are read in the same shots. Their fall per look is read as
time on their OWN fall over the delays (log-line, 0-15 us) -- the TIME seat; slope over k = their clock's time per look. Beside it the clocks' PHASE seat (W) and the laid
look (OBSERVER). Across four lengths: T against laid -- a straight line (s, d) or a bend. Raw, no verdict.   python cepheus_lookedat_lengths.py [npz:amp ...]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if os.environ.get('DOSE'): import rigetti_look_dose
import readrigetti_look_lengths as RD
import rigetti_triangle_c as C
L = RD.L; QS = RD.QS; slope = RD.slope; DL = np.array(L.DELAYS, float); em = [QS.index(q) for q in C.EM]; cl = RD.cl
files = [(a, float(b)) for a, b in (x.split(':') for x in (sys.argv[1:] or ['lookLengths_s03.npz:0.03', 'lookLengths_s03b.npz:0.03', 'lookLengths_s03_day2.npz:0.03',
                                                                           'lookLengths_s06.npz:0.06', 'lookLengths_tuned.npz:0.12']))]
for f, amp in files:
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
    P1 = lambda key: (raw[key + ('X',)].mean(0) + raw[key + ('Y',)].mean(0)) / 2          # looked-at qubits get no hand turn: X and Y arms both read their |1>
    p0 = P1(('delay', 0, 0, 0)); pd = np.clip(np.array([P1(('delay', 0, 0, d)) for d in L.DELAYS]) / p0, 1e-3, None)
    g = np.array([np.polyfit(DL, np.log(pd[:, i]), 1)[0] for i in range(len(QS))])
    rows = []
    for T in L.TONES:
        laid = T + L.LT.RING; ks = [k for k in (1, 2, 3, 4, 6) if ('look', amp, T, k, 'X') in raw]
        pk = np.clip(np.array([P1(('look', amp, T, k)) for k in ks]) / p0, 1e-3, None)
        tl = np.array([slope(ks, np.log(pk[:, i]) / g[i]) if g[i] < 0 else np.nan for i in em])
        rows.append((laid, np.nanmedian(tl)))
    x = np.array([r[0] for r in rows]); y = np.array([r[1] for r in rows]); s, c = np.polyfit(x, y, 1); res = y - (s * x + c)
    q = np.polyfit(x, y, 2)
    print(f'{f:26} amp {amp:.2f} | looked-at T per look at laid {" / ".join(f"{a:.1f}:{b:.3f}" for a, b in rows)} us | T/laid {" / ".join(f"{b / a:.3f}" for a, b in rows)}'
          f' | line s {s:.3f}, d {-c / s if s else np.nan:+.3f} us, worst residual {np.max(np.abs(res)):.3f} us | curvature {q[0]:+.3f} /us')
