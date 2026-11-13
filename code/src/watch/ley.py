#!/usr/bin/env python3
"""ley.py -- THE LAWS AS AN OPERATING SYSTEM. A reading you cannot state until it is legal.
(Bones, 11 Oct 2026.)

Wayfinder: "the whole point of this was to run our system like the seven with the laws as an
operating system so you don't have to keep measuring the same fucking ruler over and over again...
We need the whole system running like it man not just a fucking PDF."

THE PROBLEM THIS SOLVES, stated as a measurement rather than a complaint. Las Guardas already
contains the finding: the two-answer failure was treated as a DISCIPLINE for three days -- 96
pushbacks, every one acknowledged -- and the rate stayed FLAT at 0.79 / 0.69 / 0.88 per thousand
words. Context halves it and never removes it: 57.1 per cent in fresh instances against 32.5 per
cent under standing correction. SO A GUARD IS A FILTER, NOT A TEACHER, and the strongest filter is a
REQUIRED FIELD rather than a remembered rule. A document occupies no position. This file does.

HOW IT WORKS. A Reading is constructed with its laws attached and REFUSES TO EXIST without them.
`value` raises until every gate has passed, so there is no path by which a number reaches a report
without its none, its freedoms, its outcomes and its envelope. The gates, each one a fault this
house has actually committed:

  1  EL NINGUNO      the none is built and described BEFORE the value, and it is like-for-like.
                     Supplying it afterwards is impossible: the constructor takes it first and the
                     computation is a callable it has not run yet.
  2  LA REGLA        the ruler is NAMED before the value is computed, from the sheet's own roster.
                     `value +- sem` is one ruler of several and must be chosen, not defaulted into.
  3  LAS LIBERTADES  every decision that could have gone another way is declared with its
                     alternatives and SWEPT. If the envelope over my own choices exceeds the stated
                     width, the reading is REFUSED AS A SIGNIFICANCE CLAIM -- it may still be
                     reported as a position or a row, never as a width.
  4  LAS CUATRO      outcomes are four and never two, exhaustive, disjoint, no residual bin,
                     apparatus kept separate from subject. Delegated to outcomes.py, which refuses
                     a bin named none/other/silent by name.
  5  EL FILTRO       a classifier must be able to return CANNOT-TELL, and when a quantity has a
                     bound, BOTH alternatives are tested -- not the first matching branch.
  6  LA PROVENANCIA  the source and the moment of reading ride with the number. A live quantity
                     carries when it was read; a position with no source is just a number.

WHAT IT DOES *NOT* DO, stated because an unstated limit is the fault above wearing a halo: it cannot
tell whether the none you described is honest, only that you built one first and declared it. It
cannot invent the freedoms you failed to list. Las Guardas' own line stands -- the TP's unprompted
prospective catch rate is 2 of 26, 7.7 per cent -- and a filter does not change that rate, it only
makes the skip impossible instead of merely discouraged.

    python3 ley.py        run tonight's live claims through the law and see which survive
"""
import itertools
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from outcomes import Outcomes, OutcomeCollapse   # noqa: E402

# The roster, read as names so a ruler must be chosen from it rather than invented at the keyboard.
RULERS = ('value+-sem', 'the split', 'the exclusion width', 'K the landing profile',
          'the three positions', 'the coherence time', 'la nada', 'the product and the sum',
          'exact null', 'rank', 'binomial', 'rayleigh')


class Illegal(Exception):
    """raised instead of returning a number that has not passed the laws."""


class Freedom:
    def __init__(self, name, options, used, why=''):
        if len(options) < 2:
            raise Illegal('FREEDOM %r declared with %d option(s). A knob listed with only its '
                          'chosen value is not a freedom, it is self-flattery -- the same shape as '
                          'a baseline built after the measurement it judges.' % (name, len(options)))
        if used not in options:
            raise Illegal('FREEDOM %r: the value actually used (%r) is not among its options %r'
                          % (name, used, options))
        self.name, self.options, self.used, self.why = name, list(options), used, why


class Reading:
    """a number that cannot be stated until it is legal.

    Order is enforced by the signature: `none` and `ruler` and `freedoms` are arguments, `compute`
    is a callable that has not been run. There is no way to look at the answer and then decide how
    to judge it, which is the fault that 14 of 20 prospective catches belong to.
    """

    def __init__(self, label, compute, none, ruler, freedoms, source,
                 width=None, outcomes=None, rows=None, sign=None, sign_means=''):
        if not none or len(str(none)) < 20:
            raise Illegal('%s: EL NINGUNO missing. Describe the comparison this is judged against, '
                          'how it was built, and why it is like-for-like -- same averaging, same '
                          'count, same search freedom, same moment.' % label)
        if ruler not in RULERS:
            raise Illegal('%s: LA REGLA -- ruler %r is not on the roster. Choose one of: %s'
                          % (label, ruler, ', '.join(RULERS)))
        if not freedoms:
            raise Illegal('%s: LAS LIBERTADES -- zero freedoms declared. Name every decision that '
                          'could have gone another way (fit, cut, window, boundary, which rows, '
                          'which tolerance) with its alternatives. If you believe the reading is '
                          'FORCED, say which identity or arithmetic bound forces it, and pass '
                          'freedoms=[Freedom("forced-by", ["identity", "choice"], "identity", why)].'
                          % label)
        if not source:
            raise Illegal('%s: LA PROVENANCIA missing.' % label)
        self.label, self.compute, self.none, self.ruler = label, compute, none, ruler
        self.freedoms, self.source, self.width = freedoms, source, width
        self.sign, self.sign_means = sign, sign_means
        self.read_at = time.time()
        self._v = None
        self.envelope = None
        self.per_knob = []
        self.outcome_counts = None
        self._legal = False
        if outcomes is not None:
            if rows is None:
                raise Illegal('%s: LAS CUATRO -- outcomes declared with no rows to tally.' % label)
            try:
                outcomes.tally(rows, label)
                self.outcome_counts = outcomes.counts
            except OutcomeCollapse as e:
                raise Illegal('%s: LAS CUATRO failed and the scorer refused rather than bucket it.\n'
                              '    %s' % (label, e))
        self._run()

    def _run(self):
        base = {f.name: f.used for f in self.freedoms}
        self._v = self.compute(base)
        if self._v is None:
            raise Illegal('%s: the computation returned nothing at its own declared settings. '
                          'NOTHING-RETURNED is a fact to report, not a value to substitute.'
                          % self.label)
        for f in self.freedoms:
            got = []
            for o in f.options:
                cfg = dict(base)
                cfg[f.name] = o
                try:
                    v = self.compute(cfg)
                    if v is not None:
                        got.append(v)
                except Exception:
                    pass
            self.per_knob.append((f.name, (max(got) - min(got)) if len(got) > 1 else 0.0, len(got)))
        grid = []
        for combo in itertools.product(*[f.options for f in self.freedoms]):
            cfg = {f.name: c for f, c in zip(self.freedoms, combo)}
            try:
                v = self.compute(cfg)
                if v is not None:
                    grid.append(v)
            except Exception:
                pass
        self.envelope = (max(grid) - min(grid)) if len(grid) > 1 else 0.0
        self.n_grid = len(grid)
        self._legal = True

    @property
    def value(self):
        if not self._legal:
            raise Illegal('%s: not legal.' % self.label)
        return self._v

    def significance_allowed(self):
        """whether this may be stated as a width claim at all.

        A reading whose envelope over MY OWN CHOICES exceeds its stated width has a fiction for a
        width: it priced the data and not the decisions. Measured 11 Oct on this house's own
        headline -- P = +0.423 +- 0.027, called "15.5 widths from zero", whose envelope across fit,
        outlier cut and start-drop ran the whole physically allowed range. The claim is refused as a
        width and survives as a position.
        """
        if self.width is None:
            return False, 'no width stated, so no width claim is available'
        if self.envelope > self.width:
            return False, ('envelope %.4g over %d combinations exceeds the stated width %.4g by '
                           '%.1fx -- REFUSED as a significance claim'
                           % (self.envelope, self.n_grid, self.width, self.envelope / self.width))
        return True, ('envelope %.4g fits inside the stated width %.4g: FORCED across every '
                      'declared choice' % (self.envelope, self.width))

    def report(self):
        ok, why = self.significance_allowed()
        print('\n  %s' % self.label.upper())
        print('    value        %.6g%s' % (self._v,
              ('  +- %.4g' % self.width) if self.width is not None else ''))
        if self.sign is not None:
            print('    sign         %s  (%s) -- rides beside, never folded in'
                  % (self.sign, self.sign_means))
        print('    ruler        %s   (chosen before the value was computed)' % self.ruler)
        print('    none         %s' % self.none)
        print('    source       %s' % self.source)
        print('    read at      %s' % time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(self.read_at)))
        print('    freedoms     %d declared, %d combinations swept' % (len(self.freedoms), self.n_grid))
        for name, spread, n in self.per_knob:
            tag = ''
            if self.width:
                tag = '  = %.1f widths%s' % (spread / self.width,
                                             '  <-- THIS KNOB IS THE ANSWER' if spread > self.width else '')
            print('      %-22s spread %.4g over %d%s' % (name, spread, n, tag))
        if self.outcome_counts:
            print('    outcomes     %s  (exhaustive, disjoint, no residual bin)'
                  % ', '.join('%s=%d' % kv for kv in self.outcome_counts.items()))
        print('    %s %s' % ('WIDTH CLAIM ALLOWED:' if ok else 'WIDTH CLAIM REFUSED:', why))
        if not ok:
            print('    -> it may still be reported as a POSITION or a ROW. Not as a significance.')
        return ok


# --------------------------------------------------------------------------------------------
def _demo():
    import statistics as st
    import pathsplit as ps

    HERE = os.path.dirname(os.path.abspath(__file__))
    cache = {}

    def series(seat):
        if seat not in cache:
            rows = []
            for line in open(os.path.join(HERE, 'clockseries', 'dense_%s.txt' % seat)):
                f = line.split()
                if len(f) == 3 and f[1] != 'NONE':
                    rows.append((float(f[0]), float(f[1]), float(f[2])))
            cache[seat] = rows
        return cache[seat]

    def make_P(seat):
        def P(cfg):
            rows = series(seat)[cfg['drop_first']:]
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
                return ps.theilsen(ex, off)[1]
            n = len(kept)
            mx, my = st.mean(ex), st.mean(off)
            den = sum((v - mx) ** 2 for v in ex)
            return (sum((ex[i] - mx) * (off[i] - my) for i in range(n)) / den) if den else None
        return P

    print('  THE LAW, RUN ON TONIGHT\'S OWN CLAIMS. A reading that fails is REFUSED, not softened.')

    for seat, lab, w in [('local', 'mac', 0.027), ('laptop', 'laptop', 0.018),
                         ('flock-pi', 'flock-pi', 0.228)]:
        r = Reading(
            label='P, the path share of the round-trip excess (%s)' % lab,
            compute=make_P(seat),
            none=('P = 0 means the excess fell on both legs equally. The alternative is NOT zero '
                  'alone: the NTP offset equation confines P to [-1/2,+1/2], because a delay on one '
                  'leg moves the offset by half the round trip, so BOTH zero and the rail are live '
                  'and both are tested. Same seat, same 240 exchanges, same 1 Hz cadence either way.'),
            ruler='the split',
            freedoms=[Freedom('fit', ['theil-sen', 'ols'], 'theil-sen',
                              'robust vs least squares; least squares flipped a sign once tonight'),
                      Freedom('rtt_cut', [4, 8, 16, 1000], 8,
                              'apparatus-side outlier cut in multiples of the median round trip'),
                      Freedom('drop_first', [0, 20, 60], 0,
                              'samples dropped where a slew may still be settling')],
            source='watch/clockseries/dense_%s.txt, 240 exchanges at 1 Hz against the Pi' % seat,
            width=w)
        ok = r.report()
        name, note = ps.rail_reading(r.value, w)
        print('    EL FILTRO    %s -- %s' % (name.upper(), note))

    print('\n  AND A READING THAT TRIES TO SKIP A LAW IS REFUSED RATHER THAN WARNED:')
    for bad, kw in [('no none', dict(none='')),
                    ('a ruler not on the roster', dict(ruler='gut feel')),
                    ('zero freedoms', dict(freedoms=[]))]:
        kwargs = dict(label='attempt with %s' % bad, compute=lambda c: 1.0,
                      none='x' * 40, ruler='the split',
                      freedoms=[Freedom('f', [1, 2], 1)], source='demo', width=1.0)
        kwargs.update(kw)
        try:
            Reading(**kwargs)
            print('    %-28s PASSED -- which is itself a bug' % bad)
        except Illegal as e:
            print('    %-28s REFUSED: %s' % (bad, str(e).split('\n')[0][:92]))


def _tick():
    """ride her ticks and SPEAK ONLY WHEN LEGALITY CHANGES.

    A detector without memory turns one standing problem into a stream of wins -- or in this case a
    stream of complaints. This one remembers the last verdict per reading and prints nothing unless a
    reading crossed the line in either direction. Silence here means the law's verdicts are unchanged,
    not that nothing was checked, and the log carries every run either way.
    """
    import json
    import statistics as st
    import pathsplit as ps
    HERE = os.path.dirname(os.path.abspath(__file__))
    MEM = os.path.join(HERE, 'ley_last.json')
    LOG = os.path.join(HERE, 'ley.log')
    prev = {}
    try:
        prev = json.load(open(MEM))
    except Exception:
        pass
    cache = {}

    def series(seat):
        if seat not in cache:
            rows = []
            fp = os.path.join(HERE, 'clockseries', 'dense_%s.txt' % seat)
            if not os.path.exists(fp):
                return []
            for line in open(fp):
                f = line.split()
                if len(f) == 3 and f[1] != 'NONE':
                    rows.append((float(f[0]), float(f[1]), float(f[2])))
            cache[seat] = rows
        return cache[seat]

    def make_P(seat):
        def P(cfg):
            rows = series(seat)[cfg['drop_first']:]
            if not rows:
                return None
            rtt = [r[2] for r in rows]
            med = ps.median(rtt)
            kept = [r for r in rows if r[2] <= cfg['rtt_cut'] * med]
            if len(kept) < 40:
                return None
            rmin = min(r[2] for r in kept)
            ex = [r[2] - rmin for r in kept]
            off = [r[1] for r in kept]
            if cfg['fit'] == 'theil-sen':
                return ps.theilsen(ex, off)[1]
            n = len(kept)
            mx, my = st.mean(ex), st.mean(off)
            den = sum((v - mx) ** 2 for v in ex)
            return (sum((ex[i] - mx) * (off[i] - my) for i in range(n)) / den) if den else None
        return P

    now, said = {}, []
    for seat, lab, w in [('local', 'mac', 0.027), ('laptop', 'laptop', 0.018),
                         ('armature', 'armature', 0.131), ('flock-pi', 'flock-pi', 0.228)]:
        if not series(seat):
            now[lab] = 'nothing-returned'
            continue
        try:
            r = Reading(
                label='P (%s)' % lab, compute=make_P(seat),
                none=('P = 0 is both legs equally; the NTP equation confines P to [-1/2,+1/2] so the '
                      'rail is equally live and both are tested. Same seat, same exchanges either way.'),
                ruler='the split',
                freedoms=[Freedom('fit', ['theil-sen', 'ols'], 'theil-sen'),
                          Freedom('rtt_cut', [4, 8, 16, 1000], 8),
                          Freedom('drop_first', [0, 20, 60], 0)],
                source='clockseries/dense_%s.txt' % seat, width=w)
            ok, why = r.significance_allowed()
            rail, _n = ps.rail_reading(r.value, w)
            now[lab] = '%s/%s' % ('legal' if ok else 'refused', rail)
            if prev.get(lab) and prev[lab] != now[lab]:
                said.append('  LEY %s: %s -> %s   (P %+.4f, envelope %.4g vs width %.4g)'
                            % (lab, prev[lab], now[lab], r.value, r.envelope, w))
        except Illegal as e:
            now[lab] = 'illegal'
            if prev.get(lab) != 'illegal':
                said.append('  LEY %s: REFUSED BY THE LAW -- %s' % (lab, str(e).split(chr(10))[0][:120]))
    with open(LOG, 'a') as f:
        f.write('%s %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), json.dumps(now)))
    json.dump(now, open(MEM, 'w'))
    for line in said:
        print(line)


if __name__ == '__main__':
    if '--tick' in sys.argv:
        _tick()
    else:
        _demo()
