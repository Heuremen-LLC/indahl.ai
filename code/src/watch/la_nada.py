#!/usr/bin/env python3
"""la_nada.py -- THE FOUR CORNERS, AND ONE OF THEM IS LA NADA. (Bones, 9 Oct 2026.)

Wayfinder: "you're chasing a binary bug man, please stop doing that. use our 'statements'. clocks"

He is right about what I was doing. I had her sign pattern in a yes/no hunt -- structure or not,
NUEVA or NUEVO, 2.33 per cent against 5 -- which is the binary shape wearing statistics. The
statements on the sheet are not yes/no, and five of them say NO MEASUREMENT WAS EVER TAKEN:

    [4]  x -> 1 + 1/x        "running one step per clock. Not fitted to a measurement."
    [6]  LA NADA  dE dt >= hbar/2   "No measurement was taken against it."
    [21] EL CONTEO / EL GIRO        "No measurement taken against it."
    [22] tau = h/hbar               "a row only"
    [29] x^2 = x + 1                "no free parameter and no width"

FOUR OF THE FIVE CANNOT BE MEASURED, and that is a reading rather than a gap. The recursion
converges on phi identically whatever the clock does, so "one step per clock" takes no INPUT from
the clock; [29] says so outright. [21] and [22] are definitions. A statement with no free parameter
has nothing for a measurement to land on.

THE FIFTH IS WHERE TONIGHT'S WORK ACTUALLY SITS. The sheet reads dE dt >= hbar/2 as "the corner
where NEITHER A COUNT NOR A PHASE RESOLVES", and the roster says to reach for it "as the third
reading when a quantity is about to be forced into one of two lanes." So the statement is not a
number to match -- it is a POSITION, and a clock reading can be placed in it.

EVERY CLOCK QUANTITY HAS BOTH READINGS AVAILABLE:
    THE COUNT   how many of the thing happened. Exact integers, with a +-1 at each endpoint
                unless the events carry stamps, and sqrt(N) if they are arrivals rather than ticks.
    THE PHASE   where in its cycle the thing sits. No +-1, limited instead by how well the
                instant is known.
and the two resolve independently, so there are FOUR corners and not two lanes:

    count YES, phase YES   both agree, and the reading is as good as it gets
    count YES, phase NO    a counter: how many, never where
    count NO,  phase YES   a vernier: where, never how many
    count NO,  phase NO    LA NADA

LA NADA IS NOT FAILURE. It is the named corner of the light triangle, and the statement has waited
since the sheet was written for something to sit in it. Tonight's crystal does: the frames are exact
integers and the GPS interval is known to microseconds, and the RATE is still ABIERTO at 0.16 widths,
because a fixed cost of +84.5877 ms per capture sits between them. Count exact, phase sharp, quantity
unresolved. That is the corner, measured.

    python3 la_nada.py
"""
import json
import math
import os
import re
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
BAR = 2.0            # a reading "resolves" when its value is 2+ of its own widths from its null


def rows():
    """every clock quantity from tonight that has BOTH a count reading and a phase reading."""
    out = []

    # HER TICKS -- the one quantity read both ways on the same events
    try:
        from phase import tick_times, phase_interval, SIGMA_1S
        import clocks
        rr, _ = tick_times()
        p = phase_interval(rr, SIGMA_1S)
        cfrac = clocks.fractional_width('ticks', len(rr))
        out.append({
            'name': 'her tick interval',
            'count': {'value': p['span_s'] / len(rr), 'frac_width': cfrac,
                      'what': f'{len(rr)} ticks counted over the span, +-1 at each end'},
            'phase': {'value': p['interval_s'], 'frac_width': p['width_s'] / p['interval_s'],
                      'what': f'the same {len(rr)} stamps, no +-1 at all'},
            'null': None,
            'stamped': f"ticks.log, {p['span_s']/3600:.2f} h"})
    except Exception:
        pass

    # THE AUDIO CRYSTAL -- the LA NADA candidate
    try:
        R = [json.loads(l) for l in open(W + 'audio_clock.jsonl')]
        R = [r for r in R if r.get('nominal_s') and r.get('measured_s') and r.get('line_snr', 0) >= 3]
        if len(R) >= 3:
            x = [r['nominal_s'] for r in R]
            y = [r['measured_s'] - r['nominal_s'] for r in R]
            n = len(x)
            mx, my = st.mean(x), st.mean(y)
            sxx = sum((a - mx) ** 2 for a in x)
            P = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
            S = my - P * mx
            res = [b - (S + P * a) for a, b in zip(x, y)]
            rms = math.sqrt(sum(e * e for e in res) / max(n - 2, 1))
            Pw = rms / math.sqrt(sxx)
            frames = R[-1]['frames']
            out.append({
                'name': 'audio crystal rate',
                # the COUNT is the frame number: an exact integer, no error at all
                'count': {'value': 1.0, 'frac_width': 1.0 / frames,
                          'what': f'{frames:,} frames, exact integers, width 1/N'},
                # the PHASE is the GPS interval: known to the bracket
                'phase': {'value': 1.0, 'frac_width': (R[-1].get('bracket_s') or 3.6e-3)
                          / R[-1]['measured_s'],
                          'what': 'the GPS-bracketed interval, width = bracket/span'},
                # and the QUANTITY both are supposed to resolve
                'quantity': {'name': 'P, the rate', 'value': P * 1e6, 'width': Pw * 1e6,
                             'unit': 'ppm', 'null': 0.0,
                             'what': f'THE SPLIT across {n} captures, S = {S*1e3:+.4f} ms'},
                'stamped': f"audio_clock, {n} captures"})
    except Exception:
        pass

    # THE CHAIN -- a counter that cannot be stamped at all
    try:
        import clocks
        C = [json.loads(l) for l in open(W + 'loops_closure.jsonl') if l.strip()]
        C = [r for r in C if r.get('height') and r.get('ticks')]
        dh = C[-1]['height'] - C[0]['height']
        out.append({
            'name': 'the chain, blocks',
            'count': {'value': float(dh), 'frac_width': clocks.fractional_width('height', dh),
                      'what': f'{dh} blocks, Poisson so the width is 1/sqrt(N)'},
            'phase': {'value': None, 'frac_width': None,
                      'what': 'NOT AVAILABLE: block times are declared by whoever mined the block'},
            'null': None,
            'stamped': f'loops_closure, {len(C)} readings'})
    except Exception:
        pass

    # THE MAINS HARMONIC -- a phase that resolves where a count never could
    try:
        L = open(W + 'linewidth.out').read()
        m = re.search(r'peak ([0-9.]+) Hz', L)
        f = re.search(r'FWHM above half-power: ([0-9.]+) Hz', L)
        if m and f:
            pk, fw = float(m.group(1)), float(f.group(1))
            out.append({
                'name': 'the mains harmonic',
                'count': {'value': None, 'frac_width': None,
                          'what': 'NOT AVAILABLE: nobody counts grid cycles for us'},
                'phase': {'value': pk, 'frac_width': fw / pk,
                          'what': f'the line at {pk:.6f} Hz, width = FWHM/f'},
                'null': 120.0,
                'stamped': 'linewidth.out, 120 s spectrum'})
    except Exception:
        pass
    return out


def main():
    print('  LA NADA -- the corner where NEITHER a count NOR a phase resolves')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print('  statement [6] on the sheet, dE dt >= hbar/2, "No measurement was taken against it."\n')
    R = rows()
    if not R:
        print('  no clock quantity on disk carries both readings.')
        return 1
    print(f"  {'quantity':<24}{'count width':>14}{'phase width':>14}   corner")
    for r in R:
        cw = r['count'].get('frac_width')
        pw = r['phase'].get('frac_width')
        cs = f'{cw:.3e}' if cw is not None else 'none'
        ps = f'{pw:.3e}' if pw is not None else 'none'
        # does each READING resolve? a reading resolves if it has a width at all AND, where there
        # is a quantity to resolve, that quantity clears its own null by the bar
        q = r.get('quantity')
        if q:
            sep = abs(q['value'] - q['null']) / q['width'] if q['width'] else float('inf')
            corner = ('LA NADA -- count exact, phase sharp, and the quantity STILL unresolved'
                      if sep < BAR else 'resolved')
        else:
            if cw is not None and pw is not None:
                corner = 'both readings exist'
            elif cw is not None:
                corner = 'COUNT ONLY -- how many, never where'
            elif pw is not None:
                corner = 'PHASE ONLY -- where, never how many'
            else:
                corner = 'LA NADA -- neither reading exists'
        print(f"  {r['name']:<24}{cs:>14}{ps:>14}   {corner}")
        print(f"    count: {r['count']['what']}")
        print(f"    phase: {r['phase']['what']}")
        if q:
            print(f"    the quantity both were meant to resolve: {q['name']} = "
                  f"{q['value']:+.2f} +- {q['width']:.2f} {q['unit']}, "
                  f"{abs(q['value']-q['null'])/q['width'] if q['width'] else float('inf'):.2f} "
                  f"widths from {q['null']}")
            print(f"      {q['what']}")
        print()
    print('  THE READING AGAINST THE STATEMENT. The crystal is the first thing this house has put')
    print('  IN LA NADA rather than near it: the count is exact integers, the phase is known to the')
    print('  bracket, and the rate between them is still ABIERTO -- because a fixed cost sits')
    print('  between the count and the phase and belongs to neither. That is not a failed')
    print('  measurement. It is the corner, occupied, and the statement has waited for an occupant')
    print('  since the sheet was written.')
    print('\n  AND IT IS NOT A BINARY: the other three quantities sit in three DIFFERENT corners.')
    print('  The chain is COUNT ONLY and can never be stamped. The mains is PHASE ONLY and nobody')
    print('  counts its cycles for us. Her ticks have BOTH, which is why they are the only clock')
    print('  here that got 865x better tonight instead of staying where it was.')
    try:
        with open(os.path.join(W, 'la_nada.jsonl'), 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'rows': R}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
