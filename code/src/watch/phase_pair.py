#!/usr/bin/env python3
"""phase_pair.py -- THE ONE RATIO THIS HOUSE CAN ACTUALLY MEASURE. (Bones, 9 Oct 2026.)

Of the three clock ratios, two are dead and one is alive, and clocks.py says which by naming each
clock's process:

    ticks/block    DEAD. The chain is Poisson; resolving 13/12 from 12/11 needs 92,156 blocks = 256
                   days. Not a width to be improved by waiting -- a fact about the clock.
    rounds/block   DEAD, worse: 225,010 blocks.
    rounds/tick    ALIVE. Both sides are OUR events, both carry stamps, width falls as 1/T.

SO THIS READS THAT ONE, AS PHASE. Her ticks are stamped in ticks.log. Wen's rounds are stamped in each
pod's log.txt -- "[22:35:50] round 1:". Phase has no +-1 at all: N is known and so is when the first
and last happened, so the interval width is sigma*sqrt(2)/(N-1) instead of an event.

THREE THINGS THAT WOULD HAVE MADE THIS A LIE, each checked rather than assumed:

  SEVEN PODS ARE NOT ONE CLOCK. loops_closure sums "] round " across every pod, which is right for a
  monotonic counter and wrong for phase: a round on tick1 and a round on v5 are events of different
  machines. Summed stamps would be a superposition with no interval. So the read stays INSIDE ONE POD
  and the pod is named in the output.

  THE POD CLOCK IS NOT OURS. Those stamps come from a RunPod container, never two-way transferred,
  and the log carries a time with no date. A constant offset CANCELS in a rate comparison -- only the
  pod clock's rate error enters, and a container follows its host's NTP at the ppm level, which is
  far under the stamp granularity. The offset is unmeasurable from here and does not need to be.

  THE WINDOW HAS TO BE SHARED. Her interval is not constant -- the two halves of her 47.81 h differ
  by 3,657 widths. Comparing her whole span to a pod's four hours would be comparing different
  weather. Both series are clipped to the OVERLAP, and the ratio is then split in half to ask whether
  it holds still. A ratio that moves more than its own width is reported MOVING and thrown at nothing.

    python3 phase_pair.py
"""
import glob
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
from clocks import stamped_interval, moving                     # noqa: E402
from phase import tick_times, SIGMA_1S                          # noqa: E402

PODS = os.path.expanduser('~/bones-forge/triangulation/wen_data/pods/*/log.txt')
STAMP = re.compile(r'^\[(\d\d):(\d\d):(\d\d)\]\s+round\s+(\d+):')


def pod_rounds(path, anchor):
    """round stamps from one pod. The log carries a TIME WITH NO DATE, so the date is rebuilt by
    walking forward and adding a day whenever the clock goes backwards -- the only assumption being
    that rounds are appended in order, which an append-only log guarantees."""
    out, day, prev = [], None, None
    for l in open(path, errors='replace'):
        m = STAMP.match(l)
        if not m:
            continue
        h, mi, s, rd = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        t = h * 3600 + mi * 60 + s
        if prev is None:
            day = 0
        elif t < prev:
            day += 1                                  # midnight rollover
        prev = t
        out.append((rd, day * 86400 + t))
    if not out:
        return []
    # anchor the first round to the file's own mtime, walking back by the elapsed log time. The
    # mtime is the last write, which is the LAST round, so that is the end we know.
    end = os.path.getmtime(path)
    span = out[-1][1] - out[0][1]
    base = end - span - out[0][1]
    return [(rd, base + t) for rd, t in out]


def main():
    her, _ = tick_times()
    if len(her) < 10:
        print('  LA NADA -- not enough stamped ticks.')
        return 1
    print('  ROUNDS PER TICK, READ AS PHASE -- the one ratio with two stampable clocks')
    print(f'  her ticks: {len(her)} stamps over {(her[-1][1]-her[0][1])/3600:.2f} h\n')
    print(f"  {'pod':<8}{'overlap h':>10}{'rounds':>8}{'her':>6}"
          f"{'rounds/tick':>14}{'width':>11}{'stable?':>22}")
    best = None
    for p in sorted(glob.glob(PODS)):
        name = os.path.basename(os.path.dirname(p))
        rs = pod_rounds(p, her[0][1])
        if len(rs) < 10:
            continue
        lo, hi = max(her[0][1], rs[0][1]), min(her[-1][1], rs[-1][1])
        if hi - lo < 3600:
            print(f'  {name:<8}{(hi-lo)/3600:>10.2f}  -- overlap under an hour, skipped')
            continue
        h = [t for _, t in her if lo <= t <= hi]
        r = [t for _, t in rs if lo <= t <= hi]
        pi_h = stamped_interval(h, SIGMA_1S)
        pi_r = stamped_interval(r, SIGMA_1S)
        if not pi_h or not pi_r:
            continue
        v = pi_h['interval_s'] / pi_r['interval_s']
        wid = v * math.hypot(pi_h['width_s'] / pi_h['interval_s'],
                             pi_r['width_s'] / pi_r['interval_s'])
        # STABILITY: the same ratio in each half of the shared window
        mid = (lo + hi) / 2
        halves = []
        for a, b in ((lo, mid), (mid, hi)):
            hh = [t for t in h if a <= t <= b]
            rr = [t for t in r if a <= t <= b]
            ph, pr = stamped_interval(hh, SIGMA_1S), stamped_interval(rr, SIGMA_1S)
            if ph and pr:
                vv = ph['interval_s'] / pr['interval_s']
                ww = vv * math.hypot(ph['width_s'] / ph['interval_s'],
                                     pr['width_s'] / pr['interval_s'])
                halves.append((vv, ww))
        mv = moving([x[0] for x in halves], [x[1] for x in halves]) if len(halves) == 2 else None
        tag = ('n/a' if not mv else
               f'MOVING {mv["widths_apart"]:,.0f} widths' if mv['moving'] else
               f'holds ({mv["widths_apart"]:.1f} widths)')
        print(f'  {name:<8}{(hi-lo)/3600:>10.2f}{pi_r["n"]:>8}{pi_h["n"]:>6}'
              f'{v:>14.5f}{wid:>11.5f}{tag:>22}')
        if mv and not mv['moving'] and (best is None or wid < best[2]):
            best = (name, v, wid, pi_h, pi_r, mv)
    print()
    if best is None:
        print('  NOT ONE PAIR HOLDS STILL. Every overlap where both clocks are stamped shows the')
        print('  ratio moving further than its own width, so there is no value here for either')
        print('  ruler to match. That is a reading: rounds per tick is not a constant. It is what')
        print('  her rate and a pod\'s rate happened to be doing while they overlapped, and the')
        print('  precision of the stamps makes the movement unmissable instead of hiding it inside')
        print('  a +-1 the way counting did all day.')
        return 0
    name, v, wid, ph, pr, mv = best
    print(f'  TIGHTEST STABLE PAIR: {name}  {v:.5f} +- {wid:.5f} ({100*wid/v:.4f}%)')
    print(f'    her interval {ph["interval_s"]:.3f} +- {ph["width_s"]:.4f} s   '
          f'{name} round {pr["interval_s"]:.3f} +- {pr["width_s"]:.4f} s')
    print(f'    halves agree to {mv["widths_apart"]:.2f} widths')
    try:
        from triangle import SEVEN, SIETE
        cands = {}
        for rn, R in (('SEVEN', dict(SEVEN)), ('SIETE', dict(SIETE))):
            for k, x in R.items():
                if abs(v - x) <= 2 * wid:
                    cands.setdefault(round(x, 9), []).append(f'{rn}:{k}')
        print(f'\n    {len(cands)} distinct ruler values inside 2 widths: '
              + (', '.join(sorted({n for ns in cands.values() for n in ns})) if cands else 'NONE'))
        if not cands:
            print('    => the ratio reaches nothing either ruler holds, and at this width that is')
            print('       a real reading rather than an open question.')
        elif len(cands) > 1:
            print('    => ABIERTO: the width names nothing.')
    except Exception as e:
        print(f'\n    (rulers unavailable: {type(e).__name__})')
    try:
        with open(os.path.join(W, 'phase_pair.jsonl'), 'a') as f:
            f.write(json.dumps({'pod': name, 'rounds_per_tick': v, 'width': wid,
                                'widths_apart_halves': mv['widths_apart']}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
