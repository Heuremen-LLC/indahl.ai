#!/usr/bin/env python3
"""disco3.py -- THE DARK SIDE OF THE POOL. (Bones, 9 Oct 2026.)

Wayfinder: "we disco yet or what?"

disco.py threw every ratio at the Seven and La Siete. disco2.py did it again with the night's faults
taken out. Neither of them asked the darkwave question, which is the one tonight's fold test handed us:

    THE POOL HAS DARK REGIONS -- stretches of the octave where NO candidate lives at any tolerance --
    AND THE HOUSE'S OWN RATIOS PILE INTO ONE OF THEM.

Bin 8 of the octave, 1.7411 to 1.8661, holds not one of the twelve intervals. It got 58 of an expected
50.4 of the house's 504 folded ratios, +15 per cent, while bins 5-7 -- which hold FOUR candidates
between them -- got 81 of an expected 151, down 46 per cent.

THAT IS NOT A MATCH AND IT IS NOT A MISS. It is the discarded half (DARKWAVE IS OURS, 28 Sept: the
discarded half, the edge, the absence -- NOT the textbook eraser). A reader built only to say "nearest
candidate" cannot see it, because its output has no word for "landed where nothing is."

SO THE READ IS INVERTED HERE. Instead of asking which candidate a value is near, this asks:

    LIT     the value sits inside some candidate's band at tolerance t
    DARK    it sits in a stretch no candidate reaches at t -- and the width of that stretch is known
    EDGE    it sits in a stretch that is dark at t but lit at 2t, which is the boundary layer

and then it asks the only question that can tell a finding from arithmetic:

    IS THE CLUSTERING THE CLOCKS, OR IS IT THE RATIO? Two numbers of similar size have a ratio near
    one, which folds into bin 0 -- that is arithmetic, not a clock. So THE SPLIT runs on the
    construction itself: the same max/min-then-fold applied to draws with the clocks' own magnitude
    spread, which is S, against the clocks' real ratios, which is S + P.

NO PREREG GUESS (standing, 28 Sept): no prediction is written here. The dark occupancy is measured,
the control is measured, and the difference is read raw.

    python3 disco3.py
"""
import json
import math
import os
import random
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
import bonefish as BF
import fold_price as FP

L2 = math.log(2.0)
R12 = FP.R12


def regions(tol, pool):
    """the LIT intervals of the octave at this tolerance, merged -- and therefore the DARK ones."""
    iv = []
    for v in pool.values():
        a = max(math.log(v * (1 - tol)), 0.0)
        b = min(math.log(v * (1 + tol)), L2)
        if b > a:
            iv.append((a, b))
    iv.sort()
    lit = []
    for a, b in iv:
        if lit and a <= lit[-1][1]:
            lit[-1] = (lit[-1][0], max(lit[-1][1], b))
        else:
            lit.append((a, b))
    dark, x = [], 0.0
    for a, b in lit:
        if a > x:
            dark.append((x, a))
        x = max(x, b)
    if x < L2:
        dark.append((x, L2))
    return lit, dark


def where(f, lit):
    return any(a <= math.log(f) <= b for a, b in lit)


def occupancy(vals, tol, pool):
    lit, dark = regions(tol, pool)
    lit2, _ = regions(2 * tol, pool)
    n = len(vals)
    inlit = sum(1 for f in vals if where(f, lit))
    edge = sum(1 for f in vals if not where(f, lit) and where(f, lit2))
    litspan = sum(b - a for a, b in lit) / L2
    return {'n': n, 'lit': inlit / n, 'dark': 1 - inlit / n, 'edge': edge / n,
            'lit_span': litspan, 'dark_span': 1 - litspan,
            'dark_excess': (1 - inlit / n) - (1 - litspan),
            'dark_regions': dark}


def control_flat(vals, seed=20261009, reps=400):
    """THE FLAT CONTROL, and it is BIASED -- kept only so the two can be compared.

    Drawing log-uniform over the magnitudes' full range is wrong twice over: the real pairs are not
    uniform in magnitude, and one loopback offset of 0.0000 ms stretches the range to seven decades
    that no real pair ever spanned. The house already learned this on 8 Oct -- the flat draw
    under-predicts the distribution-preserving shuffle, so the shuffle is the calibrated leg.
    """
    rng = random.Random(seed)
    v = [x for x in vals if x > 1e-6]
    lo, hi = math.log(min(v)), math.log(max(v))
    out = []
    for _ in range(reps):
        a, b = math.exp(rng.uniform(lo, hi)), math.exp(rng.uniform(lo, hi))
        out.append(FP.fold(max(a, b) / min(a, b)))
    return out


def control_shuffled(pairs, seed=20261009, reps=40):
    """THE CALIBRATED CONTROL: the SAME magnitudes, re-paired.

    `pairs` is the list of (a, b) the house actually ratioed. Shuffling which value meets which
    destroys the pairing and keeps the magnitude distribution EXACTLY -- so whatever is left is about
    which clock met which clock, and not about how big the numbers were.
    """
    rng = random.Random(seed)
    flat = [x for ab in pairs for x in ab]
    out = []
    for _ in range(reps):
        rng.shuffle(flat)
        for i in range(0, len(flat) - 1, 2):
            a, b = flat[i], flat[i + 1]
            if a > 1e-9 and b > 1e-9:
                out.append(FP.fold(max(a, b) / min(a, b)))
    return out


def house_pairs():
    """the actual (a, b) the house ratioed, so the shuffle re-pairs the very same numbers."""
    out = []
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        return out
    for rr in R:
        L = rr.get('legs', {})
        for field, key in (('off_ms', 'off'), ('bound_us', 'bnd')):
            vals = [abs(v[field]) for v in L.values() if v and v.get(field)]
            vals = [v for v in vals if v > 1e-9]
            for i in range(len(vals)):
                for j in range(i + 1, len(vals)):
                    out.append((vals[i], vals[j]))
    return out


def raw_magnitudes():
    """the legs' own magnitudes, which is what the ratios were built from."""
    mags = []
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        return mags
    for rr in R:
        for k, v in rr.get('legs', {}).items():
            if v:
                if v.get('off_ms'):
                    mags.append(abs(v['off_ms']))
                if v.get('bound_us'):
                    mags.append(v['bound_us'])
    return [m for m in mags if m > 0]


def pool_of():
    return R12


def house_readings():
    try:
        return [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        return []


def block_ratios(rr):
    """the folded ratios from ONE reading, which is the independent unit."""
    out = []
    L = rr.get('legs', {})
    for field in ('off_ms', 'bound_us'):
        v = [abs(x[field]) for x in L.values() if x and x.get(field) and abs(x[field]) > 1e-9]
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                out.append(FP.fold(max(v[i], v[j]) / min(v[i], v[j])))
    return out


def main():
    print('  THE DARK SIDE OF THE POOL -- where no candidate lives, and who is standing there')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    H = FP.house_ratios()
    M = raw_magnitudes()
    if len(H) < 50 or len(M) < 20:
        print('  not enough on disk.')
        return 1
    print(f'  {len(H)} folded ratios, built from {len(M)} leg magnitudes spanning '
          f'{min(M):.3f} to {max(M):.1f}\n')

    print('  THE POOL\'S DARK REGIONS, twelve folded intervals over one octave:')
    for t in (0.01, 0.021, 0.05):
        lit, dark = regions(t, R12)
        ds = sum(b - a for a, b in dark) / L2
        widest = max(dark, key=lambda ab: ab[1] - ab[0]) if dark else None
        print(f'    tol {100*t:>5.2f}%   {len(lit)} lit bands, {len(dark)} dark gaps, '
              f'{100*ds:.1f}% of the octave dark')
        if widest:
            print(f'                  widest gap {math.exp(widest[0]):.4f} to '
                  f'{math.exp(widest[1]):.4f}, {100*(widest[1]-widest[0])/L2:.1f}% of the octave')
    print()

    print('  OCCUPANCY -- the house against the control, at three tolerances:\n')
    PR = house_pairs()
    CF = control_flat(M)
    C = control_shuffled(PR)
    print(f'  the calibrated control re-pairs the same {len(set(x for ab in PR for x in ab))} '
          f'magnitudes into {len(C)} ratios; the flat draw gives {len(CF)}\n')
    print(f"  {'tol':>7}{'dark span':>11}{'house dark':>12}{'shuffled':>11}{'flat':>9}"
          f"{'house excess':>14}{'shuffled excess':>17}")
    rows = []
    for t in (0.01, 0.021, 0.05):
        h = occupancy(H, t, R12)
        c = occupancy(C, t, R12)
        cf = occupancy(CF, t, R12)
        h['flat_dark'] = cf['dark']
        rows.append((t, h, c))
        print(f"  {100*t:>6.2f}%{100*h['dark_span']:>10.2f}%{100*h['dark']:>11.2f}%"
              f"{100*c['dark']:>10.2f}%{100*cf['dark']:>8.2f}%{100*h['dark_excess']:>+13.2f}"
              f"{100*c['dark_excess']:>+16.2f}")
    print('\n    dark span is what the pool leaves unlit. house dark is how much of the house sits')
    print('    there. The EXCESS is the darkwave quantity: standing in the dark more than the dark')
    print('    is big. The control is the same arithmetic with no clock in it.\n')

    print('  THE SPLIT ON THE CONSTRUCTION -- S is the arithmetic, P is what is left:\n')
    # THE WIDTH COMES FROM A BLOCK BOOTSTRAP, NOT FROM THE RATIO COUNT. The 56 ratios inside one
    # reading share legs -- the same eight numbers make all of them -- so counting 504 ratios as 504
    # measurements overstates what is known. The independent unit is the READING, and there are nine.
    # Resampling whole readings widens the interval by about 1.4x here, which is less than it could
    # have been: the eight legs' magnitudes genuinely differ, so the ratios are not one measurement.
    blocks = [block_ratios(rr) for rr in house_readings()]
    blocks = [b for b in blocks if b]
    rng = random.Random(20261009)
    print(f'    the independent unit is the reading, and there are {len(blocks)} of them\n')
    for t, h, c in rows:
        S = c['dark_excess']
        P = h['dark_excess'] - S
        lit, _ = regions(t, pool_of())
        allf = [f for b in blocks for f in b]
        base = 1 - sum(1 for f in allf if where(f, lit)) / len(allf)
        bs = []
        for _ in range(3000):
            pick = [blocks[rng.randrange(len(blocks))] for _ in blocks]
            v = [f for b in pick for f in b]
            bs.append((1 - sum(1 for f in v if where(f, lit)) / len(v)) - base)
        wb = st.stdev(bs) if len(bs) > 2 else float('inf')
        cw = math.sqrt(max(c['dark'] * (1 - c['dark']), 1e-9) / c['n'])
        pw = math.sqrt(wb * wb + cw * cw)
        ratio_w = math.sqrt(max(h['dark'] * (1 - h['dark']), 1e-9) / h['n'] + cw * cw)
        print(f'    tol {100*t:>5.2f}%   S {100*S:+6.2f}   P {100*P:+6.2f} +- {100*pw:.2f}   '
              f'{abs(P)/pw if pw else 0:.2f} widths'
              f'   (counting ratios instead would say +-{100*ratio_w:.2f})')
    print()

    print('  BIN 8, THE LEAD -- 1.7411 to 1.8661, not one of the twelve intervals in it:')
    b8 = [f for f in H if 1.7411 <= f < 1.8661]
    c8 = [f for f in C if 1.7411 <= f < 1.8661]
    eh = len(H) / 10.0
    ec = len(C) / 10.0
    print(f'    the house      {len(b8):>5} of {eh:>6.1f} expected   {100*(len(b8)/eh-1):+6.1f}%')
    print(f'    the control    {len(c8):>5} of {ec:>6.1f} expected   {100*(len(c8)/ec-1):+6.1f}%')
    zh = (len(b8) - eh) / math.sqrt(eh * 0.9)
    zc = (len(c8) - ec) / math.sqrt(ec * 0.9)
    print(f'    {zh:+.2f} widths against {zc:+.2f} for the control')
    row = BF.row(len(b8) / eh, math.sqrt(eh * 0.9) / eh, 'bin 8 occupancy over expected',
                 what='a region of the octave the pool cannot see, read as an object')
    print(BF.show(row, '    '))
    print()
    print('  AND THE READING IS NOT A MATCH EITHER WAY. The question the dark asks is whether a')
    print('  quantity avoids the lit bands, and the only honest answer needs the control above --')
    print('  because two numbers of similar size make a ratio near one, and that is arithmetic.')
    try:
        with open(os.path.join(W, 'disco3.jsonl'), 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'n_house': len(H), 'n_control': len(C),
                                'rows': [{'tol': t,
                                          'house': {k: v for k, v in h.items()
                                                    if k != 'dark_regions'},
                                          'control': {k: v for k, v in c.items()
                                                      if k != 'dark_regions'}}
                                         for t, h, c in rows],
                                'bin8_house': len(b8), 'bin8_control': len(c8)}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
