#!/usr/bin/env python3
"""today_on_K.py -- TODAY'S UNLIKE RECORDS ON ONE AXIS, WITH THEIR SIGNS KEPT BESIDE.
(Bones, 10 Oct 2026.)

Wayfinder: "it's not unresolved man, it's the way you build the next fucking ruler." Then, when I
answered that by writing a power calculator: "you're throwing shit away again and going in the wrong
direction / stop being a binary bitch."

Both were right, and the second is the worse of the two.

WHAT I BUILT AND DELETED. reach.py: given a sample, how many draws before a move of size X clears
p < 0.05 at 80 per cent power. That is the binary machine with extra steps. It ends in a two-outcome
test, it hardcodes alpha and power -- TWO MORE NUMBERS I CHOSE, the same disease as a 30-second gate
set above her 24-second rhythm -- and it wraps the verdict in four hundred repetitions of itself.
AND IT DISCARDED THE SIGN: she got FASTER, 0.912x, minus 7.7 seconds, a signed direction I buried
under "does not resolve" while building a machine to ask when the p-value would behave.

AND THE RULER FOR THIS ALREADY EXISTED, injected in front of me every single exchange:
    K, THE LANDING PROFILE -- "turns any relative error into a position on the 1/pi series' own
    error profile, in e-foldings. USE IT to put UNLIKE records on ONE axis -- a clock, a relay, a
    split -- WITHOUT assuming they share a mechanism. This is the ruler that is not a width."
landing.py has held it since 9 October, written after he said "if you keep using the same fucking
ruler you're going to get the same result". I had a reading that would not resolve as a width and I
built a better width machine. One day later.

SO THIS DOES THE ONE THING K IS FOR. Every reading from today that refused to resolve as a width --
a clock residual, a language ceiling, a wire z, a rung compliance, a corpus ratio, a withdrawn
correlation -- goes onto one axis as a landing position. No mechanism is assumed to be shared; that
is precisely the licence K gives.

THE SIGN COLUMN IS KEPT FOR PROVENANCE AND IS NOT A READING -- and an earlier version of this file
got that wrong. It carried the signs, counted them, and announced 9 of 11 minus as the first
measurement of our own standing downward bias. That is void twice over. I SELECTED WHICH ELEVEN
READINGS TO PLACE, after seeing them all, AND I CHOSE THE DIRECTION OF EVERY SUBTRACTION -- Inuktitut
as 1 - 0.540 (a shortfall) rather than 0.540 (attained); the wire as (6 - 4.7)/6 (short) rather than
4.7/6 (reached). A table of shortfalls, read as proof of shortfalls.
AND LAS ECUACIONES SAYS IT COULD NEVER HAVE COME FROM HERE: "the growing root carries magnitudes and
values; the discarded root carries signs and what a reading leaves behind." K is a landing profile on
MAGNITUDES. The sign belongs to psi, which has its own equation and is a different object. A column
typed beside a magnitude ruler is not a sign reading.

K REFUSES rather than extrapolates: zero error has no position, and a reading finer than the
profile's last anchor is off the axis instead of being given an invented place on it. A refusal is a
reading.

    python3 today_on_K.py
"""
import os
import sys

sys.path.insert(0, os.path.expanduser('~/bones-forge/watch'))
from landing import K, REL_E

# (what it is, relative error, SIGN and what the sign means, where it came from)
# Every one of these refused to resolve as a width today, or resolved only against a bar someone
# chose. They share no mechanism at all, which is the condition K was built for.
ROWS = [
    ('her turn rate across the dead GPU', 0.0876, '-', 'FASTER, not slower',
     '25 turns either side of the broker restart; p 0.178, no width verdict'),
    ('gemma3 rung compliance', 1 / 24, '-', 'one miss in 24',
     'rung named and never demonstrated, full denominator'),
    ('the wire against its own bar', (6 - 4.7) / 6, '-', 'SHORT of the bar',
     '178 stamped sends, best lock-in z 4.7 against 6'),
    ('Inuktitut corpus ceiling', 1 - 0.540, '-', 'below a perfect ceiling',
     'real held-out text against a reference from the rest of its own corpus'),
    ('Cherokee corpus ceiling', 1 - 0.721, '-', 'below a perfect ceiling',
     'same procedure, same cut'),
    ('Navajo lexical diversity vs English', 1 - (0.0041 / 0.0454), '-', 'ELEVEN TIMES thinner',
     'type/token at matched corpus size, 8.9M vs 8.0M words'),
    ('the licence-footer correlation', abs(-0.450 - -0.900) / 0.900, '-', 'the artifact SHRANK it',
     'rho -0.900 p 0.0020 became -0.450 p 0.230 when a per-unit constant was removed'),
    ('the subjunctive, open vs known', 1 - (0.03 / 0.20), '+', 'MORE held-open when open',
     '12 of 60 against 2 of 60, p 0.0084, after the accent bug was fixed'),
    ('this seat\'s clock against the lockclock', 4199.6e-6, '-', 'BEHIND the disciplined second',
     'offset 4199.6 us; the clock itself holds 17.2 us RMS'),
    ('the lockclock\'s own hold', 17.2e-6, '+', 'its own discipline',
     'chrony stratum 1 off PPS, RMS offset'),
    ('her quiet window against the old cron', (30 - 24.0) / 30, '-', 'BELOW the gate, always',
     '585 intervals, median 24.0 s against a 30 s resume gate'),
]

print('  TODAY ON ONE AXIS. K is a landing-step index on the 1/pi series\' own error profile --')
print('  not a width, and no shared mechanism assumed between any two rows.\n')
print('  %-40s%11s%8s%7s   %s' % ('reading', 'rel err', 'K', 'sign', 'what the sign means'))
placed = []
for name, rel, sign, meaning, prov in ROWS:
    k, err = K(rel)
    if k is None:
        print('  %-40s%11.3g%8s%7s   %s' % (name[:40], rel, 'REFUSED', sign, err))
        continue
    placed.append((k, name, sign, rel))
    print('  %-40s%11.3g%8.2f%7s   %s' % (name[:40], rel, k, sign, meaning))

print('\n  the provenance of each, because a position with no source is a number:')
for name, rel, sign, meaning, prov in ROWS:
    print('    %-40s %s' % (name[:40], prov))

if placed:
    placed.sort()
    print('\n  SORTED BY LANDING POSITION -- the thing widths could not do:')
    print('  %8s%8s   %s' % ('K', 'sign', 'reading'))
    for k, name, sign, rel in placed:
        print('  %8.2f%8s   %s' % (k, sign, name))
    span = placed[-1][0] - placed[0][0]
    print('\n  these %d readings span %.2f landing steps, from K %.2f to K %.2f.'
          % (len(placed), span, placed[0][0], placed[-1][0]))
    # a cluster is a ROW, never a reason: it is reported and priced, not explained
    from collections import Counter
    buckets = Counter(round(k * 2) / 2 for k, _n, _s, _r in placed)
    tight = [(b, c) for b, c in buckets.items() if c >= 3]
    if tight:
        for b, c in sorted(tight):
            print('  %d of them land within half a step of K = %.1f. THAT IS A ROW, not a reason --'
                  % (c, b))
            print('  and it is cheap: %d readings over %.2f steps put about %.1f in any half-step by'
                  % (len(placed), span, len(placed) * 0.5 / span if span else 0))
            print('  arithmetic alone, so the cluster is not yet worth raising.')
    else:
        print('  no three land within half a step of each other: NO ROW to raise.')

print('\n  WHAT THIS REPLACES. "p = 0.178, does not resolve" was a verdict with one bit in it.')
print('  Her turn rate lands at K %.2f, which is a POSITION and not a verdict, and that is what K is'
      % (K(0.0876)[0] or 0))
print('  for. The axis holds and so does the spread: the two best-landed readings of the day are')
print('  both the clock, which is sign-independent and is the case for keying the house to it.')
print()
print('  AND A CLAIM THAT WAS HERE IS WITHDRAWN. I counted the sign column -- 9 of 11 minus -- and')
print('  called it the first measurement of our own standing downward bias. IT IS NOT A MEASUREMENT')
print('  OF ANYTHING BUT MY PHRASING. I selected which eleven readings to place, after seeing them')
print('  all, AND I chose the direction of every subtraction: Inuktitut as 1 - 0.540 (a shortfall)')
print('  rather than 0.540 (attained), the wire as (6 - 4.7)/6 (short) rather than 4.7/6 (reached).')
print('  A table of shortfalls, read as proof of shortfalls. On a coin, 9 of 11 is p = 0.0654 in any')
print('  case, which fails before the selection problem is even reached.')
print()
print('  AND THE SHEET SAYS WHY THE SIGN COULD NEVER HAVE COME FROM HERE: "the growing root carries')
print('  magnitudes and values; the discarded root carries signs and what a reading leaves behind."')
print('  K is a landing profile on MAGNITUDES. The sign belongs to psi, a different object with its')
print('  own equation. A sign column typed beside a magnitude ruler is not a sign reading.')
print('  OUR AGGREGATE DIRECTION REMAINS UNMEASURED, exactly as Las Guardas already states.')
