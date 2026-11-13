"""readrigetti_witness.py -- batch 3 of rigetti_time.py, THE WITNESS. Raw, plain, no verdict word. Rulers measuring rulers:
 OBSERVER  our laid clock: the emitter's nominal time in |1> during the train (pushes alternate it: 5 of the 10 gaps from |0>, 5 from |1>... counted from the start state).
 TIME      the emitter's own clock: its |1> time booked from its own decay (one exponential through its 30-us rung-1 level, from the emitter ruler arms), and its end state
           on three rungs (same readout model as batches 1-2, from this batch's calibration).
 WITNESS   the clocks: each clock's extra turn during the train, over its turn with the emitters at rest for the same laid time, divided by its pull rate (its turn per us with the
           emitters held in |1>, minus at rest): the emitter's |1> time as the clock reads it. By links to the nearest emitter: 1 / 2 / 3+. Hands kept are printed too.
Each clock's own laid-time curve is its ruler. No clock is cut: every clock is read, and the hand each kept and its pull are columns; the clocks are also split into three bands by hand kept (groups of three, not a pass/fail line)."""
import json, os, sys, warnings
from collections import deque
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'time20261004'); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_time as RT
QS = RT.QS; NB = 30
R = json.load(open(os.path.join(OUT, 'wit_roles.json'))); EM = R['emitters']; CL = R['clocks']; NBR = {int(k): v for k, v in R['neighbours'].items()}


def dist():
    d = {}
    for q in CL:
        seen = {q: 0}; fr = deque([q]); best = None
        while fr:
            u = fr.popleft()
            if u in EM: best = seen[u]; break
            for v in NBR[u]:
                if v not in seen: seen[v] = seen[u] + 1; fr.append(v)
        d[q] = best
    return d
D = dist(); CLS = {'1 link': [q for q in CL if D[q] == 1], '2 links': [q for q in CL if D[q] == 2], '3+ links': [q for q in CL if D[q] and D[q] >= 3]}


def stats(Z, cal):
    p1 = lambda key, h: Z[(key, h)].mean(0)                                           # P(read 1) per qubit
    H = lambda key: (1 - 2 * p1(key, 'X')) - 1j * (1 - 2 * p1(key, 'Y'))              # the clock's hand
    out = {}; idx = {q: QS.index(q) for q in QS}
    H0 = H('REF|rest|T0')
    ang = lambda key: np.angle(H(key) / H0); kept = lambda key: np.abs(H(key) / H0)
    em_i = [idx[q] for q in EM if q in cal]
    # TIME: emitter ruler + own |1> time per gap
    L = {w: np.array([RR.solve(cal[q]['x'], 1 - Z[(f'EMRULER|w{w}', 'e')][:, idx[q]].mean(), 1 - Z[(f'EMRULER|w{w}', 'ba')][:, idx[q]].mean()) for q in EM if q in cal]) for w in RT.EM_RULER}
    for w in RT.EM_RULER: out[f'TIME emitters, |1> then {w:>2} us: rung 1 / rung 2'] = (L[w][:, 0].mean(), L[w][:, 1].mean())
    tau = -30 / np.log(np.clip(L[30][:, 0], 0.02, 0.98)); out['TIME emitters, decay time from the 30-us level (us)'] = (float(np.median(tau)),)
    for st in RT.WIT_STARTS:
        for g in RT.SPACINGS:
            key = f'W|{st}|g{g}'
            P = np.array([RR.solve(cal[q]['x'], 1 - Z[(key, 'X')][:, idx[q]].mean(), 1 - Z[(key, 'Y')][:, idx[q]].mean()) for q in EM if q in cal])
            out[f'TIME emitters {st} g{g:>2}: end state rung 1 / rung 2'] = (P[:, 0].mean(), P[:, 1].mean())
            # |1> time booked from each emitter's own decay, and the laid (nominal) |1> time
            on = 1.0 if st == 'ON' else 0.0; book = np.zeros(len(tau)); nominal = 0.0; pop = np.full(len(tau), on)
            for _ in range(RT.PUSHES):
                book += pop * tau * (1 - np.exp(-g / tau)); nominal += g * (1 if on > 0.5 else 0)
                pop = 1 - pop * np.exp(-g / tau); on = 1 - on
            out[f'OBSERVER {st} g{g:>2}: emitter |1> time, laid (us)'] = (nominal,)
            out[f'TIME     {st} g{g:>2}: emitter |1> time, own decay (us)'] = (float(np.mean(book)),)
            T = 10 * g
            if T in RT.WIT_T and T > 0:
                for name, Q in CLS.items():
                    qi = [idx[q] for q in Q]
                    a_tr = ang(key)[qi]; a_rest = ang(f'REF|rest|T{T}')[qi]; k_tr = kept(key)[qi]
                    pull = []
                    for t in RT.WIT_T_ON:
                        pull.append((np.angle(H(f'REF|held1|T{t}')[qi] / H0[qi]) - ang(f'REF|rest|T{t}')[qi]) / t)
                    pull = np.median(np.array(pull), axis=0)
                    extra = np.angle(np.exp(1j * (a_tr - a_rest))); est = extra / np.where(pull == 0, np.nan, pull)
                    out[f'WITNESS {st} g{g:>2} {name}: emitter |1> time read by every clock, median [quartiles] (us)'] = (float(np.nanmedian(est)), float(np.nanpercentile(est, 25)), float(np.nanpercentile(est, 75)))
                    band = np.argsort(np.argsort(k_tr)) * 3 // max(len(k_tr), 1)                  # three bands by hand kept through the train: no cut, no discard
                    out[f'WITNESS {st} g{g:>2} {name}: the same by hand-kept band low / mid / high (us)'] = tuple(float(np.nanmedian(est[band == b])) if np.any(band == b) else np.nan for b in range(3))
                    out[f'WITNESS {st} g{g:>2} {name}: hand kept, band medians low / mid / high'] = tuple(float(np.median(k_tr[band == b])) if np.any(band == b) else np.nan for b in range(3))
                    out[f'WITNESS {st} g{g:>2} {name}: pull per us, median [quartiles] (rad/us)'] = (float(np.median(pull)), float(np.percentile(pull, 25)), float(np.percentile(pull, 75)))
                    out[f'WITNESS {st} g{g:>2} {name}: hand kept through the train / through laid time'] = (float(np.median(k_tr)), float(np.median(kept(f'REF|rest|T{T}')[qi])))
    for name, Q in CLS.items():
        qi = [idx[q] for q in Q]
        for t in RT.WIT_T[1:]: out[f'WITNESS ruler {name}: hand kept after {t:>2} us laid, emitters at rest'] = (float(np.median(kept(f'REF|rest|T{t}')[qi])),)
        pr = [np.median(np.abs((np.angle(H(f'REF|held1|T{t}')[qi] / H0[qi]) - ang(f'REF|rest|T{t}')[qi]) / t)) for t in RT.WIT_T_ON]
        out[f'WITNESS ruler {name}: pull per us with emitters held in |1>, at 3 / 10 / 30 us (rad/us)'] = tuple(float(x) for x in pr)
    return out


def main():
    Zr = dict(np.load(os.path.join(OUT, 'read3.npz'))); Z = {tuple(json.loads(t)[:2]): v for t, v in Zr.items()}
    cal = RR.calib(Z)                                                                  # every emitter with a fitted model; its readout width is printed, not used as a gate
    print('emitter readout models (rung-2 readout width):', {q: round(float(cal[q]['e'][4]), 3) for q in EM if q in cal}, '| no model:', [q for q in EM if q not in cal])
    s = stats(Z, cal); rng = np.random.default_rng(2026100413); B = []
    for _ in range(NB):
        B.append(stats({k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in Z.items()}, cal))
    print(f"\nRIGETTI TIME, batch 3, THE WITNESS: {len(EM)} emitters ({sum(1 for q in EM if q in cal)} with a readout model), clocks by links "
          + ', '.join(f'{k} {len(v)}' for k, v in CLS.items()) + '.')
    for k, v in s.items():
        w = np.nanstd([np.array(b.get(k, [np.nan] * len(v)), dtype=float) for b in B], axis=0)
        print(f'   {k:<92} ' + '  '.join(f'{a:+.4f} +- {b:.4f}' if np.isfinite(a) else '--' for a, b in zip(np.atleast_1d(np.array(v, dtype=float)), np.atleast_1d(w))))


if __name__ == '__main__':
    main()
