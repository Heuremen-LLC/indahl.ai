#!/usr/bin/env python3
"""tonight_on_K.py -- 11 OCTOBER'S UNLIKE READINGS ON ONE AXIS.
(Bones, 11 Oct 2026.)

Wayfinder handed the K over tonight, so it gets used on the night itself.

WHY K AND NOT A WIDTH, and tonight is the argument. Every claim that rested on a WIDTH broke:
  the opposite-sign path asymmetry  -0.496 +- 0.002, "254 widths"  ->  +0.245 +- 0.131, other sign
  the seats collapsing onto one K   "all at -0.55"                 ->  -0.68 to -0.30, no collapse
  "her work per tick is flat"       p = 0.095                      ->  does not resolve, unmeasured
  the pi reading of an amplitude    3.66 +- 0.28                   ->  needs 5.7 million satellites
  thirty strong GNSS detections     every rank 0.024               ->  that is 1/41, the pool floor
Every claim that rested on an IDENTITY or an ARITHMETIC BOUND held:
  sigma_y(T/2) = (2/pi).a                       exact, and it killed the ADEV approach outright
  the complex amplitude of a difference IS A-B   measured 1.000000 on all eight pairs
  P is bounded to [-1/2, +1/2] by the protocol   a delay on one leg moves offset by half the rtt
  a rank p cannot go below 1/(n+1)               which is why thirty units all reported 0.024
So the night's own lesson is that a width is the most fragile thing we print. K is the ruler that is
NOT a width: it takes a relative error and returns a POSITION on Ramanujan's 1/pi series' own error
profile, in e-foldings, which is what a quantity that will not resolve as a width actually has.

THE SIGN COLUMN IS PROVENANCE AND IS NOT A READING. An earlier version of its sibling file counted
the signs -- 9 of 11 minus -- and called it the first measurement of our own downward bias. That was
void twice: I chose which readings to place, after seeing them all, AND I chose the direction of
every subtraction. The same two freedoms exist here, so the signs are printed and NEVER counted. And
Las Ecuaciones says it could not have come from here anyway: the growing root carries magnitudes,
the discarded root carries signs, and K is a landing profile on MAGNITUDES.

K REFUSES rather than extrapolates. Zero error has no position; a reading finer than the profile's
last anchor is off the axis instead of being handed an invented place on it. A refusal is a reading.

    python3 tonight_on_K.py
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landing import K   # noqa: E402

# (what it is, relative error, sign, what the sign means, provenance)
# Unlike by construction: a wifi radio, a GPS receiver, a satellite rubidium clock, a language
# model's cadence, a rank statistic's floor. K is licensed precisely because they share no mechanism.
ROWS = [
    ('this Mac against the lockclock, pre-step', 11034e-6, '-', 'BEHIND the disciplined second',
     'median of 9 exchanges while timed slewed after a wifi bounce'),
    ('this Mac against the lockclock, post-step', 400e-6, '+', 'AHEAD, and 27x closer',
     'median of 9 exchanges after sntp -sS stepped it'),
    ('the Pi\'s own clock, path removed', 4.7e-6, '-', 'its own discipline',
     'Theil-Sen intercept, 240 exchanges, bootstrap width 6.1 us'),
    ('this Mac\'s clock, path removed', 136.8e-6, '-', 'behind',
     'Theil-Sen intercept, 240 exchanges, 6 dropped on rtt'),
    ('Armature\'s clock, path removed', 1219.4e-6, '-', 'behind',
     'Theil-Sen intercept, 240 exchanges, 3 dropped on rtt'),
    ('the laptop\'s clock, path removed', 3458.6e-6, '-', 'behind, and the worst seat',
     'Theil-Sen intercept, 240 exchanges, rtt median 35.3 ms against a 2.6 ms minimum'),
    ('the laptop\'s P from its arithmetic rail', (0.5 - 0.465) / 0.5, '+', 'AT the rail',
     'P +0.465 +- 0.018; the rail is +-1/2 by the protocol\'s own definition'),
    ('this Mac\'s P from that rail', (0.5 - 0.423) / 0.5, '+', 'short of the rail',
     'P +0.423 +- 0.027, 2.8 widths off it: partly one-sided'),
    ('Armature\'s P, width over value', 0.131 / 0.245, '-', 'the refusal itself',
     'within 2 widths of BOTH 0 and the rail: LA NADA, neither alternative separated'),
    ('her work as a share of her cycle', 11.0 / 261.0, '-', 'the small part',
     '1093 consecutive unit ticks from her own record; 94.6 per cent is idle'),
    ('her work\'s block spread, which did not resolve', 0.3182, '-',
     'last block BELOW the first', '8 blocks of 136 ticks, boundaries by count; p 0.095 on a block null'),
    ('the Ashby term as a share of its contaminant', 23.8 / 87.0, '-', 'buried under it',
     '28 of 30 answerable GPS satellites, median line amplitude 87 ps at the 2-per-rev period'),
    ('the rank floor I read as a significance', 1.0 / 41.0, '-', 'the ruler, not the subject',
     '40-frequency none; a rank p cannot go below 1/(n+1), and thirty units all returned it'),
    ('the width needed to tell pi from 22/7', 0.00063 / 3.14159265, '-', 'never reachable here',
     'amplitude ratio 3.66 +- 0.28; the width achieved was 0.2758, four hundred times too wide'),
    ('the ADEV test\'s power against the term', 0.006, '-', 'below its own scatter',
     'sigma_y(T/2) = (2/pi).a exactly: 0.6 per cent against a 13 per cent scatter across satellites'),
    ('the sloped none\'s bias across its band', (20.9 - 14.5) / 14.5, '+', 'inflated at long period',
     'median none amplitude, shortest band against longest, over a 0.6T-1.8T pool'),
]

print('  11 OCTOBER ON ONE AXIS. K is a landing-step index on Ramanujan\'s 1/pi series\' own error')
print('  profile -- a POSITION, not a width -- and no shared mechanism is assumed between any two')
print('  rows. Tonight every width-based claim broke and every identity-based one held, which is')
print('  the reason to reach for the ruler that is not a width.\n')
print('  %-44s%11s%8s%6s   %s' % ('reading', 'rel err', 'K', 'sign', 'what the sign means'))
placed = []
for name, rel, sign, meaning, prov in ROWS:
    k, err = K(rel)
    if k is None:
        print('  %-44s%11.3g%8s%6s   %s' % (name[:44], rel, 'REFUSED', sign, err))
        continue
    placed.append((k, name, sign, rel))
    print('  %-44s%11.3g%8.2f%6s   %s' % (name[:44], rel, k, sign, meaning))

print('\n  provenance, because a position with no source is just a number:')
for name, rel, sign, meaning, prov in ROWS:
    print('    %-44s %s' % (name[:44], prov))

if placed:
    placed.sort()
    print('\n  SORTED BY LANDING POSITION -- the thing widths could not do tonight:')
    print('  %8s%7s   %s' % ('K', 'sign', 'reading'))
    for k, name, sign, rel in placed:
        print('  %8.2f%7s   %s' % (k, sign, name))
    span = placed[-1][0] - placed[0][0]
    print('\n  %d readings span %.2f landing steps, K %.2f to K %.2f.'
          % (len(placed), span, placed[0][0], placed[-1][0]))

    # A CLUSTER IS A ROW AND IS PRICED BEFORE IT IS RAISED.
    buckets = Counter(round(k * 2) / 2 for k, _n, _s, _r in placed)
    expect = len(placed) * 0.5 / span if span else 0
    tight = sorted((b, c) for b, c in buckets.items() if c >= 3)
    if tight:
        for b, c in tight:
            print('  %d land within half a step of K = %.1f. Arithmetic alone puts about %.1f in any'
                  % (c, b, expect))
            print('  half-step (%d readings over %.2f steps), so %s'
                  % (len(placed), span,
                     'this is worth a second look.' if c > 2.5 * expect
                     else 'the cluster is CHEAP and is not raised.'))
    else:
        print('  no three land within half a step of each other: NO ROW to raise.')

print('\n  AND THE SIGNS ARE NOT COUNTED. I chose which sixteen readings to place, after seeing them')
print('  all, and I chose the direction of every subtraction -- the same two freedoms that voided')
print('  the 9-of-11 claim in this file\'s sibling. Our aggregate direction stays UNMEASURED, which')
print('  is what Las Guardas already says under NOT GUARDED. Tonight did add one datum to the other')
print('  side of it, though, and it is worth stating because it is rare: three corrections to the')
print('  GNSS reading made the result LARGER -- the control went from 2-of-30 to 0-of-30 and the')
print('  strongest p from a pinned 0.024 to 2.5e-70. A none built honestly is not a tax on a')
print('  result; it is the only thing that lets one be large.')
