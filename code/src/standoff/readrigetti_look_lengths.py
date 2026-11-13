"""readrigetti_look_lengths.py -- P2-R (6 Oct 2026, Bones): the witness clocks on OUR look at four laid lengths, Cepheus. Built on the 4 Oct look-triangle
reader (readrigetti_look_triangle.py), unchanged in method: per clock, turn per look (slope over k = 1-6, unwrapped from k = 0) / turn per us (slope over
the delays) = us per look; all clocks' median. The OBSERVER is ours: the laid look = tone + 0.5 us empty. Printed per length: W, W / laid (RATIO),
W - laid (OFFSET, us); and the no-tone check (laid 1.5 us, the scheduler). An honest clock reads RATIO 1 and OFFSET 0 at every length. Raw, no verdict.
  P2R_NPZ=lookLengths_r1.npz python readrigetti_look_lengths.py"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rigetti_look_lengths as L
import rigetti_triangle_c as C
QS = L.QS; idx = {q: QS.index(q) for q in QS}
cl = [idx[q] for q in C.CL]


def slope(x, y):
    x = np.asarray(x, float); A = np.vstack([x, np.ones_like(x)]).T; return np.linalg.lstsq(A, y, rcond=None)[0][0]


def main():
    f = os.environ.get('P2R_NPZ', 'lookLengths_r1.npz')
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
    P = lambda key: raw[key].mean(0)
    H = lambda key: (1 - 2 * P(key + ('X',))) - 1j * (1 - 2 * P(key + ('Y',)))
    D = L.DELAYS
    ang_d = np.unwrap(np.array([np.angle(H(('delay', 0, 0, d)) / H(('delay', 0, 0, 0))) for d in D]), axis=0)
    rate = np.array([slope(D, ang_d[:, i]) for i in range(len(QS))])
    print(f'{f}: CHECK clocks turn {np.degrees(np.median(rate[cl])):+.1f} deg/us over the delays (the moved frame alone: {L.DETUNE * 360 / 1e6:.1f})')
    # 11 Oct FIX: the strength came from the MODULE DEFAULT (L.STRENGTH = 0.045) while five of the
    # six collected files were taken at 0.03 or 0.06, so every one of them died on a KeyError and
    # only r1 had ever been read. The strength belongs to the FILE, so it is read off the file's own
    # keys. If a file carries more than one, each is reported separately rather than pooled.
    strengths = sorted({k[1] for k in raw if k[0] == 'look'})
    assert strengths, 'no look arms in %s' % f
    print('  strengths present in this file: %s' % strengths)
    ST = float(os.environ.get('P2R_READ_STRENGTH', strengths[0]))
    print('  reading strength %.3f' % ST)
    # AND THE SAME FIX ONE LAYER DOWN: the COUNT ladder and the TONE list were module defaults too,
    # so a file collected with fewer counts died on k=6 after the strength was fixed. Everything that
    # describes what was collected now comes from the file's own keys. A module default describing
    # someone else's run is how five of six files went unread for five days.
    tones = sorted({k[2] for k in raw if k[0] == 'look' and k[1] == ST})
    rows = []
    for T in tones + ['check']:
        key = (lambda k: ('look', ST, T, k)) if T != 'check' else (lambda k: ('check', 0.0, 1.0, k))
        have = sorted({k[3] for k in raw if k[0] == ('look' if T != 'check' else 'check')
                       and (k[1] == ST if T != 'check' else True)
                       and (k[2] == T if T != 'check' else k[2] == 1.0)})
        ks = [0] + have
        if len(have) < 3:
            print('  tone %-7s CANNOT-TELL: only %d counts collected' % (T, len(have))); continue
        ang = np.unwrap(np.array([np.zeros(len(QS))] + [np.angle(H(key(k)) / H(('delay', 0, 0, 0))) for k in ks[1:]]), axis=0)
        per = np.array([slope(ks, ang[:, i]) for i in range(len(QS))]); W = per / rate
        laid = (1.0 if T == 'check' else T) + L.LT.RING
        w = np.nanmedian(W[cl]); q1, q3 = np.nanpercentile(W[cl], [25, 75])
        rows.append((T, laid, w))
        print(f"  {'no-tone check' if T == 'check' else f'tone {T} us':14} laid {laid:.2f} us | W {w:.4f} us [quartiles {q1:.3f}, {q3:.3f}] | RATIO {w / laid:.4f} | OFFSET {w - laid:+.4f} us")
    L4 = [(laid, w) for T, laid, w in rows if T != 'check']
    x = np.array([a for a, _ in L4]); y = np.array([b for _, b in L4]); A = np.vstack([x, np.ones_like(x)]).T
    (m, c0) = np.linalg.lstsq(A, y, rcond=None)[0]
    print(f'  ACROSS THE FOUR LENGTHS: W = {m:.4f} x laid {c0:+.4f} us  (an honest clock: slope 1, intercept 0; a fixed extra: slope 1, intercept > 0; a ratio: slope != 1, intercept 0)')


if __name__ == '__main__':
    main()
