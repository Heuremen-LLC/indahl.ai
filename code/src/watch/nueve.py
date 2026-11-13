#!/usr/bin/env python3
"""nueve.py -- HOW MANY POINTS BEFORE A TRAJECTORY CAN CHOOSE? (Bones, 9 Oct 2026.)

Wayfinder: "maybe the nuevos need nueves?"

The standing reader fires a slope off THREE points. Three points give a direction, not a coefficient --
I said that about the split an hour ago and then built the trajectory with the same hole. And NINE is
the ladder's own rung for CHOICE (8 clock, 9 choice, 10 null, 11 measurement cancelling itself), so
the question is whether the arithmetic puts the discriminator's threshold there.

NOT ASSERTED. MEASURED. The darkwave discriminator has to tell two shapes apart:

    A TRUE MATCH    d/w FLAT        slope 0
    A COINCIDENCE   d/w ~ sqrt(n)   slope 1 against sqrt(n), by construction

So the threshold is an EXCLUSION WIDTH on the slope itself: how many points before the two slopes are
separated by more than the fit's own scatter? That depends on one thing the house can measure -- how
noisy a single d/w reading is -- and on nothing else.

THE NONE IS BUILT IN. A flat trajectory and a sqrt(n) trajectory are simulated at the same noise, the
same n, the same spacing; the threshold is where they stop overlapping. No shuffle, no guess, and the
answer is a number of readings rather than a yes.

    python3 nueve.py
"""
import json
import math
import os
import random
import statistics as st
import sys

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)


def fit_slope(xs, ys):
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    if sxx <= 0 or n < 3:
        return None, None
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
    a0 = my - b * mx
    res = [c - (a0 + b * a) for a, c in zip(xs, ys)]
    rms = math.sqrt(sum(e * e for e in res) / (n - 2))
    return b, rms / math.sqrt(sxx)


def measured_scatter():
    """HOW NOISY IS ONE d/w READING? From the house's own standing log, not from a guess."""
    try:
        P = [json.loads(l) for l in open(W + 'nueva_standing.jsonl') if l.strip()]
    except Exception:
        return None, 0
    by = {}
    for p in P:
        if p.get('d_over_w') is not None:
            by.setdefault(p['q'], []).append(p['d_over_w'])
    sc = [st.stdev(v) for v in by.values() if len(v) >= 3]
    return (st.mean(sc) if sc else None), len(sc)


def threshold(noise, seed=20261009, reps=3000, nmax=24):
    """the smallest point-count at which FLAT and sqrt(n) stop overlapping at two widths."""
    rng = random.Random(seed)
    out = []
    for k in range(3, nmax + 1):
        # the n values a standing reader actually sees: n grows as readings accumulate
        ns = [3 + i for i in range(k)]
        xs = [math.sqrt(v) for v in ns]
        sep = 0
        for _ in range(reps):
            yf = [0.0 + rng.gauss(0, noise) for _ in xs]                 # a true match: flat
            yc = [x + rng.gauss(0, noise) for x in xs]                   # a coincidence: ~ sqrt(n)
            bf, wf = fit_slope(xs, yf)
            bc, wc = fit_slope(xs, yc)
            if None in (bf, wf, bc, wc):
                continue
            w = math.sqrt(wf * wf + wc * wc)
            if w and abs(bc - bf) > 2 * w:
                sep += 1
        out.append((k, sep / reps))
    return out


def main():
    print('  HOW MANY POINTS BEFORE A TRAJECTORY CAN CHOOSE')
    print(f'  read {__import__("time").strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    noise, k = measured_scatter()
    if noise is None:
        noise = 0.5
        print(f'  the standing log has no question with three points yet, so the scatter on one d/w')
        print(f'  reading is not measured. Running at {noise} and the threshold below moves with it --')
        print(f'  that is the honest state, not a result.\n')
    else:
        print(f'  one d/w reading scatters by {noise:.4f}, measured across {k} standing questions\n')
    print('  FLAT vs sqrt(n), separated at two widths, as points accumulate:\n')
    print(f"  {'points':>8}{'n span':>12}{'separated':>12}")
    T = threshold(noise)
    hit = None
    for kk, frac in T:
        mark = ''
        if frac >= 0.5 and hit is None:
            hit = kk
            mark = '   <- half the time'
        if frac >= 0.9 and kk == next((a for a, b in T if b >= 0.9), None):
            mark += '   <- nine times in ten'
        print(f"  {kk:>8}{f'3 to {3+kk-1}':>12}{100*frac:>11.1f}%{mark}")
    nine = dict(T).get(9)
    three = dict(T).get(3)
    print(f'\n  AT THREE POINTS the two shapes separate {100*three:.1f}% of the time. That is what the')
    print(f'  standing reader was firing a verdict off.')
    print(f'  AT NINE POINTS they separate {100*nine:.1f}% of the time.')
    if hit:
        print(f'  THE THRESHOLD -- better than even odds of telling them apart -- IS {hit} POINTS.')
        print(f'    the ladder puts CHOICE at nine, and the arithmetic here puts the choice at {hit}.')
        if hit == 9:
            print(f'    THEY ARE THE SAME NUMBER, and it is one row, not a reason: a threshold could')
            print(f'    have landed on any integer from 3 to 24, so this is 1 in 22 by position alone')
            print(f'    -- 4.5 per cent, which is a row worth keeping and nothing more until the')
            print(f'    scatter above is measured on more than {k} questions.')
        else:
            print(f'    NOT NINE. The ladder says nine and the arithmetic says {hit}, and the')
            print(f'    arithmetic is the one that was measured. The nuevos need {hit}.')
    print(f'\n  SO THE STANDING READER\'S GATE MOVES FROM 3 TO {hit or "unknown"}: below it a trajectory')
    print(f'  is recorded and not fitted, the same way an unreadable width already is.')
    return hit


if __name__ == '__main__':
    h = main()
    print(f'\n  gate = {h}')
