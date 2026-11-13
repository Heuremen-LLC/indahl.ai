#!/usr/bin/env python3
"""el_contador.py -- THE CRYSTAL RATE OFF A COUNTER THE SERVO CANNOT TOUCH.

Reads a seat file written by seat_samples.py (t  offset  rtt  counter) and returns the seat
oscillator's rate against the reference, in ppm, from COLUMN 4 -- the unsteered hardware counter --
rather than from the system clock in column 2.

WHY THIS FILE EXISTS, 11 Oct 2026. A 3 h Armature run measured the free-running system clock at
-10.5722 +- 0.0010 ppm for 129.33 minutes and then w32time STEPPED it -6.747371 s in one sample.
Pooled across that single step the same file reads -767.1708 +- 5.0595 ppm. Nothing in the fit
complains: the residual sd is 1.9 SECONDS and the width is small, because a width answers "how well
does a line fit" and never "is a line the right object". The counter has no step to pool across.

AND THE WIDTH THAT COMES OUT OF THE FIT IS NOT THE WIDTH OF THE QUANTITY. On that same free-running
segment the two halves read -10.5341 +- 0.0030 and -10.4880 +- 0.0020 ppm: 0.046 ppm apart, which is
FIFTEEN of their own widths. The rate is not a constant over two hours -- it warms -- so the honest
number carries the SEGMENT-TO-SEGMENT SPREAD, not the regression's standard error. This reader
prints both and says which one to carry, every time, so the smaller one can never be quoted alone.

    python3 el_contador.py <seat.txt> [label] [--segments N]

Four outcomes are kept: a NONE line is nothing-returned and is never interpolated, and a file with
fewer than two usable segments gets CANNOT-TELL rather than a number with no width.
"""
import sys
import numpy as np

RAIL_PPM = 1e6


def load(path):
    t, off, rtt, cnt = [], [], [], []
    lost = 0
    for line in open(path):
        f = line.split()
        if len(f) < 4:
            continue
        if f[1] == 'NONE':
            lost += 1                                  # counted, never filled in
            continue
        t.append(float(f[0])); off.append(float(f[1])); rtt.append(float(f[2])); cnt.append(float(f[3]))
    return (np.array(t), np.array(off), np.array(rtt), np.array(cnt), lost)


def rate_ppm(x, y):
    """slope of y on x, minus one, in ppm, with the regression's own standard error.

    THE ARGUMENT ORDER IS THE SIGN, and it was wrong on the first write: called as (counter, true)
    it returns d(true)/d(counter), which is POSITIVE for a counter running slow. The quantity wanted
    is the seat's rate against the reference, d(seat)/d(reference) - 1, so the REFERENCE goes first.
    Caught by a planted seat before any real file was read: planted -7.5000 ppm came back +7.5004,
    right magnitude, inverted sign. A magnitude ruler never carries a sign -- the sign rides beside
    it, and here it rides in the order of two arguments."""
    A = np.vstack([x - x[0], np.ones(len(x))]).T
    (m, c), *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ [m, c]
    den = np.std(x - x[0]) * np.sqrt(len(x))
    sem = res.std() / den if den > 0 else np.nan
    return (m - 1.0) * RAIL_PPM, sem * RAIL_PPM, res.std()


def robust_rate_ppm(true, cnt, min_gap_s=300.0, n_pairs=20000, seed=20261011):
    """THEIL-SEN over WIDELY SEPARATED PAIRS. The carried estimator, and the only one here that
    passed a test on known truth.

    WHY NOT LEAST SQUARES. The counter is regressed against true = local + offset, so THE SERVO
    REACHES COLUMN 4 THROUGH THE X-AXIS. On the full 3 h Armature run the 90-120 min segment held
    3 steps and an offset swinging -0.169 to +0.133 s; 0.020 s of x-axis distortion over 1800 s is
    -11.2 ppm of fake rate, and least squares duly reported -14.75 ppm where the rate was about +11.
    EARLIER CLAIM CORRECTED: a step cannot destroy the counter COLUMN, but it does distort the time
    axis that column is measured against. "Immune to the servo" was too strong.

    WHY NOT A MEDIAN OF CONSECUTIVE PAIRS. Robust, and BIASED: a ratio whose denominator also carries
    noise is biased, and over a 0.75 s step the counter's read jitter is a large share of the
    interval. On the planted seat (truth -7.5000) it returned -7.7577, off by 0.258 ppm. It was
    written here first and removed for failing that test.

    WHY THIS ONE. Pairs separated by at least min_gap_s give a long lever, so read jitter is divided
    by a big interval instead of a small one, and the median still cannot be moved by a few bad
    pairs. On the planted seat it returns -7.5000 at a 60 s gap and -7.5001 at 300 / 600 / 1800 s --
    error at or under 0.0001 ppm, and stable across the gap choice, which is the check that the gap
    is not a tuned parameter.

    Returns (ppm, n_pairs)."""
    rng = np.random.default_rng(seed)
    n = len(true)
    if n < 60: return (np.nan, 0)
    sl, tries = [], 0
    while len(sl) < n_pairs and tries < n_pairs * 20:
        i, j = rng.integers(0, n, 2); tries += 1
        if true[j] - true[i] >= min_gap_s: sl.append((cnt[j] - cnt[i]) / (true[j] - true[i]))
        elif true[i] - true[j] >= min_gap_s: sl.append((cnt[i] - cnt[j]) / (true[i] - true[j]))
    if len(sl) < 30: return (np.nan, len(sl))
    return (float(np.median(sl) - 1.0) * RAIL_PPM, len(sl))


def steps(off, thresh=0.05):
    """where the SYSTEM clock was stepped. Not used to correct anything -- used to say out loud that
    column 2 is unusable across these points while column 4 is not."""
    d = np.diff(off)
    return np.where(np.abs(d) > thresh)[0], d


def main():
    argv = sys.argv[1:]
    nseg = 4
    if '--segments' in argv:
        i = argv.index('--segments'); nseg = int(argv[i + 1]); del argv[i:i + 2]
    if not argv:
        print(__doc__); return 1
    path = argv[0]; label = argv[1] if len(argv) > 1 else path
    t, off, rtt, cnt, lost = load(path)
    n = len(t)
    print('\nEL CONTADOR -- %s' % label)
    print('  committed %d, nothing-returned %d, span %.3f h, rtt median %.3f ms'
          % (n, lost, (t[-1] - t[0]) / 3600 if n > 1 else 0, np.median(rtt) * 1e3 if n else float('nan')))
    if n < 60:
        print('  CANNOT-TELL: fewer than 60 committed exchanges.'); return 0

    js, d = steps(off)
    print('  system-clock steps over 50 ms: %d%s'
          % (len(js), '' if not len(js) else '  ' + ', '.join(
              '%+.6f s at %.2f min' % (d[j], (t[j] - t[0]) / 60) for j in js[:4])))
    if len(js):
        print('    -> COLUMN 2 (the system clock) CANNOT be pooled across those points. Column 4 can.')

    # the quantity, off the counter. TRUE TIME IS t + off, never t: t is this seat's own clock
    # reading, so regressing against t would measure the counter against the thing the servo steers.
    true = t + off
    r, sem, rsd = rate_ppm(true, cnt)
    rr, npair = robust_rate_ppm(true, cnt)
    print('  COUNTER vs the reference, pooled:  %+10.4f ppm   (fit sem %.4f, residual sd %.3f ms)'
          % (r, sem, rsd * 1e3))
    print('  COUNTER, THEIL-SEN (carry this):  %+10.4f ppm   (%d pairs, gap >= 300 s)'
          % (rr, npair))
    print('     Least squares above takes the servo in through the x-axis; Theil-Sen does not, and')
    print('     it returns the planted truth to 0.0001 ppm where a consecutive-pair median is off 0.26.')

    # and the same thing off the system clock, printed beside it so the difference is visible
    rs, sems, rsds = rate_ppm(true, t)
    print('  SYSTEM CLOCK vs the reference:     %+10.4f ppm   (fit sem %.4f, residual sd %.3f ms)%s'
          % (rs, sems, rsds * 1e3, '   <- SERVO, not the crystal' if len(js) or abs(rs) < abs(r) / 4 else ''))

    # THE WIDTH THAT MATTERS: segment to segment
    idx = np.array_split(np.arange(n), nseg)
    seg = [rate_ppm(true[i], cnt[i]) for i in idx if len(i) > 30]
    if len(seg) < 2:
        print('  CANNOT-TELL on the width: fewer than two usable segments.'); return 0
    # A SEGMENT WHOSE OWN FIT WILL NOT RESOLVE IS NOT A READING OF THE RATE, and the commonest
    # cause is reading a file that is still being written: the last segment is truncated, or the
    # servo was thrashing through it. It is NAMED, never silently dropped -- four outcomes, no
    # residual bin (watch/outcomes.py's rule applied to segments).
    sems = np.array([x[1] for x in seg])
    med = float(np.median(sems))
    usable = [k for k, x in enumerate(seg) if x[1] <= 10 * med]
    print('  in %d segments of %.1f min each:' % (len(seg), (t[-1] - t[0]) / 60 / len(seg)))
    for k, (v, se, _rs) in enumerate(seg):
        print('     %d  %+10.4f ppm  (its own fit sem %.4f)%s'
              % (k + 1, v, se, '' if k in usable else '   <- WILL NOT RESOLVE, over 10x the median'
                                                      ' segment sem; named, not carried'))
    if len(usable) < 2:
        print('  CANNOT-TELL: fewer than two segments resolve.'); return 0
    if len(usable) < len(seg):
        print('  carrying %d of %d segments; %s excluded above by its own width, not by its value'
              % (len(usable), len(seg), 'segment ' + ', '.join(str(k + 1) for k in range(len(seg))
                                                               if k not in usable)))
    seg = [seg[k] for k in usable]
    vals = np.array([x[0] for x in seg])
    spread = float(vals.max() - vals.min())
    sd = float(vals.std(ddof=1))
    worst = max(x[1] for x in seg)
    print('  SPREAD %.4f ppm, sd %.4f ppm over %d segments.' % (spread, sd, len(seg)))
    print('  CARRY THIS:  %+.4f +- %.4f ppm   (the segment sd, %.0fx the pooled fit sem of %.4f)'
          % (vals.mean(), sd, sd / sem if sem else float('nan'), sem))
    print('  The fit sem is how well a line fits; the segment sd is how much the quantity moves.')
    if sd > 3 * worst:
        print('  AND THE RATE IS NOT A CONSTANT HERE: the segments disagree by more than %.0f of their '
              'own widths, so any single value quoted off this file is a value at a moment.'
              % (spread / worst))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
