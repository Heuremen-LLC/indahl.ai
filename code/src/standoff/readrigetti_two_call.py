"""readrigetti_two_call.py -- TWO's call on Cepheus, read on three seats. Raw, no verdict, nothing cut.
OBSERVER  the laid spacings phi^0..phi^8 us; the |0> start against (a) each interval's OWN decay (|1> left exactly that long, per ruler copy a / b / c) and (b) the CURVE (log-linear through the copy's points).
TIME      the three ruler copies beside each other; idle |0>; back-to-back pushes (the push's own error).
WITNESS   the |1> start (the mirror) and the halfway start, against the same rulers; three readout-width bands, nothing cut.
The hashed call (calls/TWO_CALL_CEPHEUS_20261004.txt) printed beside each spacing; the nearest of the ladder and the Seven's numbers beside each reading."""
import json, math, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_two_call as W
QS = W.RT.QS; PHI = W.PHI
LADDER = {f'rung {n}': 1 / 12 / PHI ** n for n in range(7)}; LADDER['friction 1/(12 pi)'] = 1 / (12 * math.pi)
near = lambda x: (lambda k: f'{k} ({LADDER[k] * 100:.2f} %) {(x / LADDER[k] - 1) * 100:+.1f}%')(min(LADDER, key=lambda k: abs(x / LADDER[k] - 1)))


def main():
    Z = {tuple(json.loads(k)[:2]): v for k, v in np.load(os.path.join(W.RT.OUT, 'two.npz')).items()}
    cal = RR.calib(Z); keep = [q for q in QS if q in cal]
    wid = np.array([cal[q]['e'][4] if np.isfinite(cal[q]['e'][4]) else np.inf for q in keep]); band = np.argsort(np.argsort(wid)) * 3 // len(keep)
    def pops(key, ks):
        return np.array([RR.solve(cal[q]['x'], 1 - Z[(key, 'e')][:, QS.index(q)].mean(), 1 - Z[(key, 'ba')][:, QS.index(q)].mean()) for q in ks])
    print(f'TWO CALL ON CEPHEUS: {len(keep)} qubits with a readout model (no cut). Bands by rung-2 readout width: ' + ' / '.join(f'{int((band == b).sum())}' for b in range(3)))
    for nm, ks in (('ALL', keep), ('TIGHT', [q for q, b in zip(keep, band) if b == 0]), ('MID', [q for q, b in zip(keep, band) if b == 1]), ('LOOSE', [q for q, b in zip(keep, band) if b == 2])):
        R = {(cp, g): pops(f'RULER|ON|w{g}|{cp}', ks)[:, 0] for cp in W.COPIES for g in W.SP}
        idle = pops('RULER|OFF|w46.979', ks)
        print(f'\n [{nm}, {len(ks)} qubits] TIME own decay (rung 1 left after g, copies a / b / c): ' + ' | '.join(f'{g} us ' + '/'.join(f'{R[(cp, g)].mean():.4f}' for cp in W.COPIES) for g in W.SP)
              + f' | idle |0> 47 us rung 1 / 2 {idle[:, 0].mean():+.4f} / {idle[:, 1].mean():+.4f}')
        for st, m0 in (('OFF', 0.0), ('ON', 1.0), ('MID', 0.5)):
            if st != 'MID':
                b2b = pops(f'{st}|g0', ks)[:, 0]; print(f'   {st} back to back (no time): rung 1 minus start {(b2b - RR.book(m0, 1.0, W.RT.PUSHES)).mean():+.4f}')
            for n, g in enumerate(W.SP):
                P = pops(f'{st}|g{g}', ks); r1 = P[:, 0]; own, cur = [], []
                for cp in W.COPIES:
                    own.append((r1 - RR.book(m0, np.clip(R[(cp, g)], 0.02, 1), W.RT.PUSHES)).mean())
                    ts = np.array([0.0] + W.SP); Ls = np.log(np.clip(np.vstack([np.ones(len(ks))] + [R[(cp, gg)] for gg in W.SP]), 0.02, 1))
                    j = int(min(max(np.searchsorted(ts, g) - 1, 0), len(ts) - 2)); f = (g - ts[j]) / (ts[j + 1] - ts[j]); qc = np.exp(Ls[j] + f * (Ls[j + 1] - Ls[j]))
                    cur.append((r1 - RR.book(m0, qc, W.RT.PUSHES)).mean())
                o = np.mean(own); line = f'   {st} g {g:>6} us: OWN {"/".join(f"{x:+.4f}" for x in own)} mean {o:+.4f} | CURVE mean {np.mean(cur):+.4f} | rung 2 {P[:, 1].mean():+.4f}'
                if st == 'OFF': line += f' || CALL {100 / 12 / PHI ** n:.2f} % | nearest: {near(abs(o)) if o else "--"}'
                print(line)


if __name__ == '__main__':
    main()
