#!/usr/bin/env python3
"""clocks.py -- EVERY CLOCK'S ERROR MODEL, IN ONE PLACE. (Bones, 9 Oct 2026.)

Built because I gave the Wownero chain the wrong width for an entire day and then did 1/T arithmetic
on it to promise a result in 82 hours.

THE FAULT. I treated every clock as A COUNTER READ AT TWO MOMENTS: advance divided by span, with a
+-1 at each endpoint, so the fractional width is sqrt(2)/N and falls as 1/T. That is right for her
ticks and for Wen's rounds, which are OUR events and really do tick once per thing. It is wrong for
the chain. Blocks are ARRIVALS FROM A MEMORYLESS PROCESS at a difficulty target: the number in a
window has standard deviation sqrt(N), not 1. On the live span that understated the width 8.0x
(0.809% quoted, 6.479% real), and because a Poisson width falls as 1/sqrt(N) rather than 1/T, the
"82 hours to separate 13/12 from 12/11" was arithmetic on an error model the clock does not have.
The real figure is 92,156 blocks -- 256 days. The experiment was never available.

THE DEEPER VERSION OF THE SAME FAULT. A width is not a property of a measurement, it is a property of
THE PROCESS THAT GENERATED IT. Asking "how wide is this reading" without asking "what kind of thing
is this clock" is how an endpoint error ends up on a Poisson process. So the error model lives with
the clock, by name, and a caller cannot get a width without saying which clock it came from.

THREE KINDS, and the house owns clocks of all three:

    COUNTER   our own events, one tick per thing, read at two moments.
              fractional width sqrt(2)/N   falls as 1/T.      her ticks, Wen's rounds
    POISSON   arrivals from a memoryless process.
              fractional width 1/sqrt(N)   falls as 1/sqrt(T). the chain
    STAMPED   events carrying their own timestamp on a shared reference.
              width sigma*sqrt(2)/(N-1) on the INTERVAL, and no +-1 exists at all,
              because N is known and so is when the first and last happened.
                                                               her ticks via ticks.log, the GPSDO

  11 OCT, WITHDRAWN: THE 865x WAS A WIDTH ON THE WRONG TERM. The stamped read's sigma was the
  1-second ROUNDING of field 1 (0.2887 s). Field 1 is not her clock -- nova_resonance.py:2942
  writes it as datetime.now() ON THIS MAC at the moment the scribe's poll notices her row, so each
  stamp carries OUR POLL LAG, measured at sd 10.27 s over the 53 rows that now also carry her own
  stamp (ticks.log field 9, Supabase created_at). With the lag term in place the same ruler on 1204
  ticks reads 260.4938 +- 0.012076 s and the stamped read is 25x tighter than counting, not 865x.
  THE VALUE SURVIVES: on the same 52 adjacent pairs the span reads 326.8397 s off field 1 and
  327.0379 s off field 9, 0.198 s apart. It is the WIDTH that was wrong, by 36x like-for-like.

A clock can be more than one kind depending on how it is READ -- her ticks are a COUNTER in
loops_closure and STAMPED in ticks.log, and the stamped read is 865x tighter on the same 688 events.
That is not two opinions about one width. It is two different measurements, and the stamped one is
better because it asks when instead of how many.

AND A PRECISE NUMBER CAN STILL BE THE WRONG OBJECT. Her stamped interval is 250.5575 +- 0.000594 s
over 47.81 h, and the two halves of that span differ by 3,657 widths (247.4884 vs 253.6356). The
precision is real and the mean is meaningless: it is a sharp statement about the average of something
that does not sit still. So every reading here carries a STABILITY check beside its width, and a
quantity that moves more than its own width across the span is reported as MOVING, never as a value.

    python3 clocks.py        # the models, and the live widths under each
"""
import math

COUNTER, POISSON, STAMPED = 'counter', 'poisson', 'stamped'

KIND = {
    'ticks': COUNTER,       # her flywheel, read as a count in loops_closure
    'rounds': COUNTER,      # Wen's lessons
    'cycles': COUNTER,      # her cycles
    'height': POISSON,      # THE CHAIN. arrivals, not a counter. sqrt(N), falls as 1/sqrt(T)
    'mac_s': COUNTER,       # the Mac wall clock, and it is not independent of what it measures
    'gps_s': STAMPED,       # the GPSDO
}
WHY = {
    'height': 'blocks are memoryless arrivals at a difficulty target, so the count in a window has '
              'sd sqrt(N); it never had a fixed endpoint error and its width falls as 1/sqrt(T)',
    'gps_s': 'satellite time, independent of her, the chain, the pod and this host',
    'mac_s': 'this machine, and NOT independent of what it measures -- read to price others, never '
             'to schedule',
}


def fractional_width(name, n):
    """the fractional width a clock's own process puts on a count of n of its events.

    RAISES on an unknown clock rather than guessing. A guessed error model is exactly the fault
    this module exists to prevent, and a default would be a guess wearing a number."""
    k = KIND.get(name)
    if k is None:
        raise KeyError(f'no error model for clock {name!r} -- add it to KIND with its WHY, do not '
                       f'let it default. Guessing a width is the fault this file was built for.')
    if n <= 0:
        return float('inf')
    if k == POISSON:
        return 1.0 / math.sqrt(n)
    if k == COUNTER:
        return math.sqrt(2) / n
    return math.sqrt(2) / n          # a stamped read should use stamped_interval, not this


def ratio_width(value, num_name, num_n, den_name, den_n):
    """the width on num/den, each side priced by ITS OWN process."""
    a = fractional_width(num_name, num_n)
    b = fractional_width(den_name, den_n)
    return abs(value) * math.hypot(a, b)


def stamped_interval(times, sigma):
    """the interval between stamped events. NO +-1: N is known and so are the endpoints."""
    t = sorted(times)
    n = len(t) - 1
    if n < 2:
        return None
    return {'interval_s': (t[-1] - t[0]) / n, 'width_s': sigma * math.sqrt(2) / n, 'n': len(t)}


def span_needed(value, width, n_now, name, target_gap):
    """how much span it takes to resolve target_gap at 2 widths, under THIS clock's model.

    The whole point: a counter gets there as 1/T and a Poisson clock as 1/sqrt(T), so the same
    question has answers that differ by orders depending on which clock is the limit."""
    want = (target_gap / 2.0) / abs(value)
    k = KIND.get(name)
    if k == POISSON:
        n_need = 1.0 / want ** 2
    else:
        n_need = math.sqrt(2) / want
    return {'n_needed': n_need, 'n_now': n_now, 'times_more': n_need / max(n_now, 1),
            'model': k, 'falls_as': '1/sqrt(T)' if k == POISSON else '1/T'}


def moving(values, widths):
    """STABILITY. A quantity whose readings spread further than their own widths is MOVING, and a
    mean of it is a precise statement about nothing."""
    if len(values) < 2:
        return None
    spread = max(values) - min(values)
    w = math.hypot(max(widths), min(widths))
    return {'spread': spread, 'joint_width': w, 'widths_apart': spread / w if w else float('inf'),
            'moving': bool(w and spread / w >= 2)}


if __name__ == '__main__':
    import json
    import os
    print('  CLOCK ERROR MODELS\n')
    for n, k in KIND.items():
        print(f'    {n:<10} {k:<9} {WHY.get(n, "")}')
    f = os.path.expanduser('~/bones-forge/watch/loops_closure.jsonl')
    R = [json.loads(l) for l in open(f) if l.strip()]
    R = [r for r in R if r.get('height') and r.get('ticks') and r.get('rounds')]
    dt, dh, dr = (R[-1][k] - R[0][k] for k in ('ticks', 'height', 'rounds'))
    print(f'\n  live span: {dt} ticks, {dh} blocks, {dr} rounds\n')
    for nm, a, na, b, nb in (('ticks/block', 'ticks', dt, 'height', dh),
                             ('rounds/tick', 'rounds', dr, 'ticks', dt),
                             ('rounds/block', 'rounds', dr, 'height', dh)):
        v = na / nb
        w = ratio_width(v, a, na, b, nb)
        s = span_needed(v, w, nb, b, 0.00700)
        print(f'    {nm:<13} {v:.5f} +- {w:.5f} ({100*w/v:.3f}%)   to resolve 13/12 vs 12/11: '
              f'{s["n_needed"]:,.0f} of {b} ({s["times_more"]:,.0f}x more, width falls as '
              f'{s["falls_as"]})')
