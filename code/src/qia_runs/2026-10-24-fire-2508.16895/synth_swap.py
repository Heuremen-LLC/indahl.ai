"""synth_swap.py -- run swaprun.readings on planted worlds (binomial shot noise per circuit, 1000 shots, 2 copies), BEFORE any job.
Usage: python -I synth_swap.py > synth_results_swap.text"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from swaprun import *
P = select(curves()); EX = np.array([p['F'] for p in P]); CLS = np.array([p['cls'] for p in P]); RD = ('IDENT', 'ORTHO', 'THEIRS', 'COPY')
def world(rng, f=lambda e, c: e, scatter=0.0, drift=1.0):
    t = np.array([f(e, c) for e, c in zip(EX, CLS)]) + np.where(CLS == 'IDENT', -np.abs(rng.normal(0, scatter, len(EX))), rng.normal(0, scatter, len(EX)))
    t = np.clip(t, -1, 1); T = np.stack([t, np.clip(t * drift, -1, 1)], 1)
    return 2 * rng.binomial(SHOTS, (1 + T) / 2) / SHOTS - 1
X = None   # not asserted
WORLDS = [  # name, runs, true-F function, pair scatter sd, copy-2 factor, expected outcome per reading (None = not asserted)
    ('NEITHER (true = exact)', 400, lambda e, c: e, 0.0, 1.0, dict(IDENT='CONSISTENT', ORTHO='CONSISTENT', THEIRS='CONSISTENT', COPY='CONSISTENT')),
    ('BELOW: x0.853 (their 2025 identical-pair shrink)', 100, lambda e, c: 0.853 * e, 0.0, 1.0, dict(IDENT='BELOW', ORTHO='CONSISTENT', THEIRS='BELOW', COPY='CONSISTENT')),
    ('ABOVE: +0.10 offset (not on IDENT, capped 1)', 100, lambda e, c: e if c == 'IDENT' else e + 0.10, 0.0, 1.0, dict(IDENT='CONSISTENT', ORTHO='ABOVE', THEIRS='ABOVE', COPY='CONSISTENT')),
    ('BOTH: compression 0.85 F + 0.10', 100, lambda e, c: 0.85 * e + 0.10, 0.0, 1.0, dict(IDENT='BELOW', ORTHO='ABOVE', THEIRS=X, COPY='CONSISTENT')),
    ('DRIFT: BELOW world, copy 2 x0.95 (POWER ONLY, not gated)', 100, lambda e, c: 0.853 * e, 0.0, 0.95, dict(IDENT='BELOW', ORTHO=X, THEIRS='BELOW', COPY='power')),
    ('DRIFT: BELOW world, copy 2 x0.92', 100, lambda e, c: 0.853 * e, 0.0, 0.92, dict(IDENT='BELOW', ORTHO=X, THEIRS='BELOW', COPY='BELOW')),
    ('ARTEFACT: NEITHER + pair scatter sd 0.03 (layout per pair)', 400, lambda e, c: e, 0.03, 1.0, dict(IDENT=X, ORTHO='notAB', THEIRS='notAB', COPY='CONSISTENT')),
    ('BELOW + pair scatter sd 0.05', 100, lambda e, c: 0.853 * e, 0.05, 1.0, dict(IDENT='BELOW', ORTHO=X, THEIRS='BELOW', COPY='CONSISTENT')),
]
if __name__ == '__main__':
    rng = np.random.default_rng(20261024); allpass = True
    print(f'synth for swaprun.readings: {len(P)} pairs ({sum(CLS=="IDENT")} IDENT, {sum(CLS=="ORTHO")} ORTHO, {sum(CLS=="THEIRS")} THEIRS) x {COPIES} copies x {SHOTS} shots; band t(n-1) 99 %; scales {SCALE}')
    for name, n, f, sc, dr, exp in WORLDS:
        tally = {r: {} for r in RD}; hit = {r: 0 for r in RD}; halves = {r: [] for r in RD}
        for _ in range(n):
            R = readings(P, world(rng, f, sc, dr))
            for r in RD:
                o = R[r]['outcome']; tally[r][o] = tally[r].get(o, 0) + 1; halves[r].append(R[r]['half'])
                e = exp[r]; hit[r] += (e in (None, 'power')) or (o == e) or (e in ('notAB', 'CONSISTENT') and o not in ('ABOVE', 'BELOW'))
        print(f'\n{name}  ({n} runs)')
        for r in RD:
            e = exp[r]; rate = hit[r] / n; ab = (tally[r].get('ABOVE', 0) + tally[r].get('BELOW', 0)) / n
            ct = tally[r].get('CANNOT_TELL', 0) / n; pw = tally[r].get('BELOW', 0) / n
            gate = None if e in (None, 'power') else (ab <= 0.05 if e in ('CONSISTENT', 'notAB') else rate >= 0.80)
            ok = 'not asserted' if e is None else f'power {pw*100:.0f} % (not gated)' if e == 'power' else ('PASS' if gate else 'FAIL'); allpass &= (gate is not False)
            print(f'  {r:<7} expect {str(e):<11} got {tally[r]}  match {rate*100:5.1f} %  CANNOT_TELL {tally[r].get('CANNOT_TELL', 0)/n*100:5.1f} %  false-resolution (ABOVE/BELOW) {ab*100:5.1f} %  median half-width {np.median(halves[r]):.4f}  {ok}')
    print('\nGATES (second table, set before any job): a reading expected CONSISTENT/notAB passes if its false resolution (ABOVE or BELOW) is <= 5 %; CANNOT_TELL is not a false call and is printed. A reading expected ABOVE/BELOW needs >= 80 % (power).')
    print('ALL WORLDS PASS' if allpass else 'SOME WORLD FAILS')
