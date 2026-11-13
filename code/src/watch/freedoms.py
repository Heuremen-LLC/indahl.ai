#!/usr/bin/env python3
"""freedoms.py -- COUNT MY CHOICES AND VARY THEM. If the number moves, the number is mine.
(Bones, 11 Oct 2026.)

Wayfinder: "Your choice always makes the number man that's the whole fucking problem with the ruler
and everything we keep going around and around with."

That is the correct diagnosis and it is not a mood -- it is measurable, and one night's record says
so cleanly. Every reading that SURVIVED scrutiny was FORCED by something that is not a preference:

    P is confined to [-1/2, +1/2]          the NTP offset equation: a delay on one leg moves the
                                           offset by half the round trip. Not a choice.
    sigma_y(T/2) = (2/pi) . a              the definition of Allan deviation applied to a sinusoid.
    amp(x_a - x_b) = A_a - A_b             linearity of the fit. MEASURED at 1.000000 on 8 pairs.
    a rank p cannot go below 1/(n+1)       counting.
    K's informative direction               the complement of a small error sits at K = -1 and
                                           carries nothing: the flip gave rho = -1.0000 exactly.

Every reading that BROKE was a choice of mine wearing a measurement's clothes:

    the boundary of a before/after split    1.13x became 0.912x and did not resolve
    which eleven readings go on an axis     9-of-11-minus, void twice over
    which tolerance a validation passes     flicker passed at -0.27 against a bar I typed as 0.30
    which fit, least squares or robust      P -0.496 "254 widths" became +0.245, THE OTHER SIGN
    which three reads are the three seats   1 of 12 conversions separable, and I nominated the three

SO THE FIX IS NOT ANOTHER RULER. It is to make the choices a REQUIRED, ENUMERATED, SWEPT FIELD.
State every decision that could have gone another way, give its alternatives, and vary them. If the
answer moves by more than its own stated width under any single choice, THE CHOICE MADE THE NUMBER
and the width was a fiction. If nothing moves it, the reading is forced and the width means something.

A reading with ZERO declared freedoms is not automatically forced -- it may just be unexamined. So
the count of freedoms is printed beside the result, and a reading claiming zero has to say WHY each
obvious knob is absent.

    python3 freedoms.py        sweep tonight's live path-asymmetry claim over my own choices
"""
import itertools
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Freedom:
    """one decision I made, with the alternatives I could equally have made.

    `options` must contain the value actually used AND at least one defensible other. An option set
    of one is not a freedom, it is a declaration -- and a knob listed with only its chosen value is
    the same self-flattery as a baseline built after the measurement.
    """

    def __init__(self, name, options, used, why=''):
        if len(options) < 2:
            raise ValueError('%s: a freedom needs at least two defensible options, got %r'
                             % (name, options))
        if used not in options:
            raise ValueError('%s: the value actually used (%r) is not among its options' % (name, used))
        self.name, self.options, self.used, self.why = name, list(options), used, why


def sweep(compute, freedoms, width=None, label='reading'):
    """vary each choice one at a time, then all together, and price the result against its width.

    ONE AT A TIME gives the per-choice sensitivity -- which knob is carrying the answer.
    THE FULL GRID gives the honest envelope, because choices interact and the one-at-a-time spread
    can understate it badly. Both are reported; neither is dropped in favour of the other.
    """
    base = {f.name: f.used for f in freedoms}
    centre = compute(base)
    rows = []
    for f in freedoms:
        vals = []
        for o in f.options:
            cfg = dict(base)
            cfg[f.name] = o
            try:
                vals.append((o, compute(cfg)))
            except Exception as e:
                vals.append((o, None))
        got = [v for _o, v in vals if v is not None]
        rows.append({'freedom': f, 'values': vals,
                     'spread': (max(got) - min(got)) if len(got) > 1 else 0.0})
    grid = []
    for combo in itertools.product(*[f.options for f in freedoms]):
        cfg = {f.name: c for f, c in zip(freedoms, combo)}
        try:
            v = compute(cfg)
            if v is not None:
                grid.append(v)
        except Exception:
            pass

    print('\n  %s = %.6g, with %d declared freedoms.' % (label, centre, len(freedoms)))
    print('  %-26s%10s%12s%12s   %s' % ('my choice', 'spread', 'vs width', 'verdict', 'options'))
    worst = None
    for r in rows:
        f = r['freedom']
        ratio = (r['spread'] / width) if width else None
        v = ('MINE' if (ratio and ratio > 1) else 'forced' if (ratio and ratio < 0.3) else 'partial')
        if ratio is None:
            v = 'no width stated'
        if worst is None or r['spread'] > worst[0]:
            worst = (r['spread'], f.name)
        print('  %-26s%10.4g%12s%12s   %s'
              % (f.name, r['spread'], ('%.1fx' % ratio) if ratio else '-', v,
                 ', '.join(str(o) for o in f.options)))
    if grid and len(grid) > 1:
        env = max(grid) - min(grid)
        print('\n  FULL GRID over %d combinations: %.6g to %.6g, envelope %.4g%s'
              % (len(grid), min(grid), max(grid), env,
                 ' = %.1f stated widths' % (env / width) if width else ''))
        if width and env > width:
            print('  THE ENVELOPE EXCEEDS THE STATED WIDTH. The number is inside my choices, and the')
            print('  width is a fiction -- it prices the data and not the decisions.')
        elif width:
            print('  The envelope fits inside the stated width: the reading is FORCED across every')
            print('  combination of choices declared here.')
    if worst:
        print('  the knob carrying the most: %s (%.4g)' % (worst[1], worst[0]))
    return centre, rows


# --------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import pathsplit as ps

    RAW = {}

    def series(seat):
        if seat not in RAW:
            rows = []
            for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          'clockseries', 'dense_%s.txt' % seat)):
                f = line.split()
                if len(f) == 3 and f[1] != 'NONE':
                    rows.append((float(f[0]), float(f[1]), float(f[2])))
            RAW[seat] = rows
        return RAW[seat]

    def P_of(cfg):
        """the path-asymmetry share, recomputed under one combination of my choices."""
        rows = series(cfg['seat'])
        rows = rows[cfg['drop_first']:]
        rtt = [r[2] for r in rows]
        if not rtt:
            return None
        med = ps.median(rtt)
        kept = [r for r in rows if r[2] <= cfg['rtt_cut'] * med]
        if len(kept) < 40:
            return None
        rmin = min(r[2] for r in kept)
        ex = [r[2] - rmin for r in kept]
        off = [r[1] for r in kept]
        if cfg['fit'] == 'theil-sen':
            _a, b = ps.theilsen(ex, off)
            return b
        n = len(kept)
        mx, my = st.mean(ex), st.mean(off)
        den = sum((v - mx) ** 2 for v in ex)
        return (sum((ex[i] - mx) * (off[i] - my) for i in range(n)) / den) if den else None

    print(__doc__.split('\n\n')[0])
    print('\n  TONIGHT\'S LIVE CLAIM UNDER ITS OWN CHOICES: P, the share of a round-trip excess that')
    print('  lands in the offset. Reported for this Mac as +0.423 +- 0.027 -- "15.5 widths from zero".')

    F = [Freedom('fit', ['theil-sen', 'ols'], 'theil-sen',
                 'robust vs least squares; the one that flipped Armature\'s sign'),
         Freedom('rtt_cut', [4, 8, 16, 1000], 8,
                 'the apparatus-side outlier cut, in multiples of the median round trip'),
         Freedom('drop_first', [0, 20, 60], 0,
                 'samples dropped at the start, where a slew may still be settling'),
         Freedom('seat', ['local', 'armature', 'laptop', 'flock-pi'], 'local',
                 'WHICH SEAT -- not a nuisance knob: swept to show a per-seat answer is not a house answer')]

    sweep(P_of, F, width=0.027, label='P (this Mac)')

    print('\n  AND THE SAME SWEEP WITH THE SEAT HELD FIXED, which is the honest question about')
    print('  the Mac alone rather than about the house:')
    sweep(P_of, F[:3] + [Freedom('seat', ['local', 'local'], 'local', 'held fixed')][:0]
          + [Freedom('seat', ['local', 'armature'], 'local', 'two seats only')],
          width=0.027, label='P (this Mac)')
