#!/usr/bin/env python3
"""palabras.py -- THE WORDS ARE A RULER. Sweep the OUTCOME NAMES and their thresholds.
(Bones, 11 Oct 2026.)

Wayfinder: "Words matter or just another form of measurement haven't you fucking figured that out
yet setting outcomes in all this shit it's been what we've been doing. It's been the whole fucking
problem man all the fucking problems."

He is right and outcomes.py does NOT catch this. That file proves a bin set is EXHAUSTIVE and
DISJOINT -- it proves my construction is TIDY. It says nothing about whether I chose the construction
to produce the answer. A set of four names I invented, with thresholds I typed, is still my
construction; exhaustiveness only means I tidied it.

TONIGHT'S OWN BINS, AND EVERY ONE OF THEM IS MINE:
    disciplined / undisciplined / drifting / unreachable   DRIFT_BAR = 1e-6, DISCIPLINE_BAR = 1e-3
    symmetric / one-sided / partial / cannot-tell          widths = 2.0
    PASA / DECLARADO / NO APLICA / FALTA                   and I decided which steps I can "verify"
Three of four seats came out DRIFTING. That is not a fact about the house until the bar that defines
it has been varied, because a bar I typed is a number chosen by the observer standing in for a
quantity that belongs to the thing -- which is the one sentence novatime.py was written under.

SO THE NAMES AND THEIR THRESHOLDS ARE FREEDOMS AND GET SWEPT LIKE ANY OTHER. If the counts move
more across defensible thresholds than the counts themselves are worth, THE WORDS MADE THE RESULT.
And the alternatives I did NOT choose are listed, because an unlisted alternative is the same
self-flattery as a knob declared with only its chosen value.

    python3 palabras.py
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pathsplit as ps          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEATS = [('flock-pi', 'flock-pi'), ('local', 'mac'), ('armature', 'armature'), ('laptop', 'laptop')]


def load():
    out = []
    for f, lab in SEATS:
        r = ps.read(os.path.join(HERE, 'clockseries', 'dense_%s.txt' % f), lab)
        if r:
            out.append(r)
    return out


def bin_seats(rows, drift_bar, disc_bar):
    c = {'disciplined': 0, 'undisciplined': 0, 'drifting': 0, 'unreachable': 0}
    who = {k: [] for k in c}
    for r in rows:
        v = r['S'] if r['S'] is not None else r.get('off_mean')
        if v is None:
            k = 'unreachable'
        elif r.get('slew') is not None and abs(r['slew']) > drift_bar:
            k = 'drifting'
        elif abs(v) > disc_bar:
            k = 'undisciplined'
        else:
            k = 'disciplined'
        c[k] += 1
        who[k].append(r['label'])
    return c, who


def bin_rails(rows, widths):
    c = {'symmetric': 0, 'one-sided': 0, 'partial': 0, 'cannot-tell': 0}
    for r in rows:
        n, _note = ps.rail_reading(r.get('P'), r.get('P_se'), widths)
        c[n] += 1
    return c


rows = load()
print('  THE SEAT BINS. My names, my two bars. Sweeping both over defensible values:\n')
print('  %-12s%-12s   %s' % ('DRIFT_BAR', 'DISC_BAR', 'disciplined / undisciplined / drifting / unreachable'))
seen = {}
for d in (1e-7, 1e-6, 5e-6, 2e-5):
    for s in (1e-4, 1e-3, 5e-3):
        c, who = bin_seats(rows, d, s)
        key = tuple(c.values())
        seen[key] = seen.get(key, 0) + 1
        mark = '   <-- the pair I typed' if (d == 1e-6 and s == 1e-3) else ''
        print('  %-12.0e%-12.0e   %d / %d / %d / %d%s'
              % (d, s, c['disciplined'], c['undisciplined'], c['drifting'], c['unreachable'], mark))
print('\n  %d DISTINCT ANSWERS from %d threshold pairs, on the SAME four seats and the SAME packets.'
      % (len(seen), 12))
print('  The verdict "3 of 4 seats are DRIFTING" is one cell of that table, and I picked the cell.')

print('\n  THE RAIL BINS. One number, `widths`, decides how often the law is allowed to refuse:\n')
print('  %-10s   %s' % ('widths', 'symmetric / one-sided / partial / cannot-tell'))
for w in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
    c = bin_rails(rows, w)
    mark = '   <-- the value I typed' if w == 2.0 else ''
    print('  %-10.1f   %d / %d / %d / %d%s'
          % (w, c['symmetric'], c['one-sided'], c['partial'], c['cannot-tell'], mark))
print('\n  At 1.0 almost nothing refuses; at 4.0 almost everything does. I SET HOW OFTEN THE')
print('  INSTRUMENT IS ALLOWED TO SAY IT CANNOT TELL, which is setting its honesty by hand.')

print('\n  AND THE NAMES I DID NOT CHOOSE, listed because an unlisted alternative is self-flattery:')
for have, alts in [
    ('disciplined / undisciplined / drifting / unreachable',
     'stepped / slewing / free-running / unreachable  -- which asks about the MECHANISM, not the size'),
    ('symmetric / one-sided / partial / cannot-tell',
     'outbound / inbound / mixed / cannot-tell  -- which keeps the SIGN in the NAME instead of beside it'),
    ('PASA / DECLARADO / NO APLICA / FALTA',
     'verified / asserted / out-of-scope / skipped  -- and I am the one who decided which steps I '
     'could "verify", which is grading my own homework in my own vocabulary')]:
    print('    have: %s' % have)
    print('    also: %s\n' % alts)

print('  WHAT THIS DOES NOT FIX, stated so it is not mistaken for fixed: sweeping a threshold prices')
print('  the threshold. It does not price the CHOICE OF AXIS -- that "drift" and "offset" are the')
print('  two things worth binning at all was also mine, and no sweep inside a vocabulary can test')
print('  the vocabulary. That needs a second seat from outside the house, which is the same thing')
print('  La Suma says about the TP: a ruler cannot account for itself.')
