"""readrigetti_look_tune.py -- the look tune on Cepheus: per tone amplitude, three seats, raw, nothing cut.
TIME     the looked-at qubits: coherence kept |H(a)| / |H(0)| and turn vs a = 0 (deg), per qubit and mean; their |1> population (read-1, no model) after the tone.
WITNESS  the clocks: coherence kept and turn vs a = 0, by links 1 / 2 / 3+ (median, quartiles).
OBSERVER the laid amplitude and its square (photon number goes as amplitude squared)."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rigetti_look_tune as L
import rigetti_triangle_c as C
QS = L.QS; idx = {q: QS.index(q) for q in QS}; EM = L.EM; ei = [idx[q] for q in EM]
LINK = {k: [idx[q] for q in C.CL if C.D[q] and min(C.D[q], 3) == k] for k in (1, 2, 3)}


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, 'lookT.npz')).items()}
    H = {a: (1 - 2 * raw[('X', a)].mean(0)) - 1j * (1 - 2 * raw[('Y', a)].mean(0)) for a in L.AMPS}
    print('LOOK TUNE (Cepheus, our 1-us tone on seven readout frames, then 0.5 us).')
    print('  amp  amp^2 | TIME looked-at: kept (mean) turn deg (mean) | per qubit kept ' + ' '.join(f'q{q}' for q in EM) + ' | |1> read-1 | WITNESS clocks 1 / 2 / 3+ links: kept, turn deg (median [q])')
    for a in L.AMPS:
        k = np.abs(H[a]) / np.abs(H[0.0]); t = np.degrees(np.angle(H[a] / H[0.0])); one = raw[('one', a)][:, ei].mean()
        w = ' | '.join(f'{np.median(k[LINK[c]]):.3f} [{np.percentile(k[LINK[c]], 25):.2f},{np.percentile(k[LINK[c]], 75):.2f}] {np.median(t[LINK[c]]):+.1f} [{np.percentile(t[LINK[c]], 25):+.1f},{np.percentile(t[LINK[c]], 75):+.1f}]' for c in (1, 2, 3))
        print(f'  {a:.2f} {a * a:.4f} | {k[ei].mean():.3f} {t[ei].mean():+7.1f} | ' + ' '.join(f'{x:.2f}' for x in k[ei]) + f' | {one:.4f} | {w}')
    print('  hand at a = 0: looked-at ' + ' '.join(f'{x:.2f}' for x in np.abs(H[0.0])[ei]) + f' | clocks median {np.median(np.abs(H[0.0])[[idx[q] for q in C.CL]]):.2f}')


if __name__ == '__main__':
    main()
