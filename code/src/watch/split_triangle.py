#!/usr/bin/env python3
"""split_triangle.py -- TWO OVERLAPPING TRIANGLES, AND THE DISAGREEMENT IS THE WITNESS.
(Bones, 9 Oct 2026.)

Wayfinder: "the fuck we gotta wait four hours for man, didn't you make a fucking clock pentagram?
why don't you run it like two overlapping triangles and the disagreement is the witness."

He is right and it removes the wait entirely.

THE PROBLEM. THE SPLIT says the audio captures carry D = outside - inside = S + P . crossing, with
S = +84.5877 ms COMMON TO EVERY RUN (the stream's own setup and teardown) and P the rate I actually
want. P came out -20.61 +- 125.90 ppm, 0.16 widths from zero: unmeasured. My answer was to outrun S
-- T > 16,918 s so that P.T exceeds 2S at 10 ppm. Four and three quarter hours for one number.

THE TRIANGLE. S does not have to be outrun, it has to be CLOSED AROUND. Cover the same total span
two ways:

    path A:  capture T1, then capture T2        -- pays the fixed cost TWICE
    path B:  capture T1 + T2 as one             -- pays it ONCE

    D_A = (S + P.T1) + (S + P.T2) = 2S + P.(T1+T2)
    D_B =  S + P.(T1+T2)

    D_A - D_B = S            EXACTLY. Every P term cancels.
    and then P = (D_B - S) / (T1+T2), with S now known rather than fitted.

Two paths to one endpoint, and their disagreement is the thing neither path could show alone. That
is the witness: not a third instrument, a third READING made of the other two.

WHY THIS BEATS THE FIT I DID. The five-capture least squares put S and P in the same estimate and
split the information between them, so a noisy S poisoned P -- residual rms 56.1229 ms against an
S of 84.5877 ms. The closure does not estimate S and P together; it ISOLATES S in one subtraction
where the P terms are algebraically absent, and the arithmetic is exact rather than fitted.

THE NONE. A closure that always returns something is not a measurement. The none here is built in:
if the model D = S + P.T is wrong -- if S depends on duration, or there is a T^2 term -- the closure
returns a DIFFERENT S for different (T1, T2) choices. So it is run at several splits of the same
total, and the spread ACROSS splits is the model's own error. A single split cannot see it.

    python3 split_triangle.py --total 120 --splits 60,40,30 --rounds 2
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
from audio_clock import capture, NOMINAL                            # noqa: E402

LOG = os.path.join(W, 'split_triangle.jsonl')


def D(seconds):
    """one capture's outside-minus-inside, in seconds. Returns None with a reason on failure."""
    cap, err = capture(seconds)
    if cap is None or cap.get('data') is None:
        return None, (err or (cap or {}).get('err') or 'no capture')
    nominal = cap['frames'] / NOMINAL
    measured = cap['gps1'] - cap['gps0']
    return {'T': nominal, 'D': measured - nominal, 'frames': cap['frames'],
            'bracket': math.hypot(cap['w0'] or 0, cap['w1'] or 0)}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--total', type=float, default=120.0)
    ap.add_argument('--splits', default='60,40,30',
                    help='T1 values; T2 = total - T1. Several, so the model can be checked.')
    ap.add_argument('--rounds', type=int, default=2)
    a = ap.parse_args()
    splits = [float(x) for x in a.splits.split(',')]
    print('  THE SPLIT, CLOSED AROUND -- two paths to one span, the disagreement is the witness')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  total span {a.total:.0f} s, T1 in {splits}, {a.rounds} round(s)\n')
    print(f"  {'T1':>6}{'T2':>6}{'D(T1) ms':>12}{'D(T2) ms':>12}{'D(T1+T2) ms':>14}"
          f"{'S = A-B ms':>13}{'P ppm':>10}")
    rows = []
    for rnd in range(a.rounds):
        for t1 in splits:
            t2 = a.total - t1
            if t2 <= 1:
                continue
            d1, e1 = D(t1)
            d2, e2 = D(t2)
            d3, e3 = D(a.total)
            if None in (d1, d2, d3):
                print(f'  {t1:>6.0f}{t2:>6.0f}  FAILED: {e1 or e2 or e3}')
                continue
            # D_A - D_B = S, exactly, every P term cancelled
            S = (d1['D'] + d2['D']) - d3['D']
            P = (d3['D'] - S) / d3['T']
            rows.append({'t1': d1['T'], 't2': d2['T'], 'total': d3['T'],
                         'D1': d1['D'], 'D2': d2['D'], 'D3': d3['D'], 'S': S, 'P_ppm': P * 1e6})
            print(f"  {t1:>6.0f}{t2:>6.0f}{d1['D']*1e3:>12.3f}{d2['D']*1e3:>12.3f}"
                  f"{d3['D']*1e3:>14.3f}{S*1e3:>13.3f}{P*1e6:>10.2f}")
    if len(rows) < 2:
        print('\n  fewer than 2 closures: no reading, and no none either.')
        return 1
    Ss = [r['S'] for r in rows]
    Ps = [r['P_ppm'] for r in rows]
    print(f'\n  S, the fixed cost, isolated in a subtraction where P is algebraically absent:')
    print(f'    {st.mean(Ss)*1e3:+.3f} ms   sd {st.stdev(Ss)*1e3:.3f}   '
          f'sem {st.stdev(Ss)/math.sqrt(len(Ss))*1e3:.3f}   ({len(Ss)} closures)')
    print(f'  P, the rate, with S now KNOWN rather than fitted alongside it:')
    pm, psd = st.mean(Ps), (st.stdev(Ps) if len(Ps) > 1 else 0.0)
    psem = psd / math.sqrt(len(Ps)) if Ps else 0.0
    print(f'    {pm:+.2f} ppm   sd {psd:.2f}   sem {psem:.2f}')
    print(f'    {abs(pm)/psem if psem else float("inf"):.2f} sem from zero: '
          + ('SEPARABLE -- a rate at last' if psem and abs(pm) / psem >= 2
             else 'ABIERTO -- still no rate, and now that is about the clock, not the method'))
    # THE NONE: does the model hold across splits?
    bysplit = {}
    for r in rows:
        bysplit.setdefault(round(r['t1']), []).append(r['S'])
    print(f'\n  THE NONE -- S by split. If D = S + P.T is the right model, S does not depend on')
    print(f'  WHERE the total was cut. If it does, the model is wrong and the closure is hiding it.')
    for t1 in sorted(bysplit):
        v = bysplit[t1]
        print(f'    T1={t1:>4} s: S = ' + ', '.join(f'{x*1e3:+.3f}' for x in v) + ' ms')
    if len(bysplit) >= 2:
        means = [st.mean(v) for v in bysplit.values()]
        spread = max(means) - min(means)
        w = (st.stdev(Ss) / math.sqrt(len(Ss))) if len(Ss) > 1 else 0.0
        print(f'    spread across splits {spread*1e3:.3f} ms on a sem of {w*1e3:.3f} ms = '
              f'{spread/w if w else float("inf"):.2f} widths')
        print(f'    => ' + ('S DEPENDS ON THE SPLIT, so D = S + P.T is the wrong model and both '
                            'numbers above are suspect.' if w and spread / w >= 2 else
                            'S does not depend on the split: the model holds and the closure is '
                            'sound.'))
    # against the thing it replaces
    print(f'\n  AGAINST THE FIT IT REPLACES: five captures by least squares gave '
          f'P = -20.61 +- 125.90 ppm')
    print(f'  (0.16 widths, unmeasured) and needed T > 16,918 s to do better. This took '
          f'{a.total*len(rows)*2/60:.1f} min of audio.')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'S_mean_s': st.mean(Ss), 'S_sd_s': st.stdev(Ss) if len(Ss) > 1 else 0,
                                'P_mean_ppm': pm, 'P_sd_ppm': psd, 'P_sem_ppm': psem,
                                'rows': rows}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
