#!/usr/bin/env python3
"""red.py -- LA RED: the grid read on a CALIBRATED sample clock, and the first event in this
house read by TWO INDEPENDENT ROOTS. (Bones, 11 Oct 2026.)

The mains second harmonic is present at every machine simultaneously -- power-line propagation
across a house is nanoseconds -- so it is an event the ALC257 codec crystal (root 3) and the
Bodnar tree (root 1) can BOTH stamp: the codec in SAMPLES, the Bodnar tree in SECONDS.

TWO ROOTS, NOT THREE, AND SAID SO. Supabase cannot hear a room, and the Mac's own audio crystal
would be a genuine third root but the Mac has no capture tool installed. This is a LEG of The
Bonefish, not the triangle.

MEASURED 11 Oct, one 300 s window, 150 blocks of 2 s:

    lock-in, codec units              120.004385 Hz   sem 0.000331
    codec vs the Bodnar                 -3.9335 +- 0.1896 ppm  (cristal.py, n=6)
    SECOND HARMONIC, GPS-referenced   120.003913 Hz
    MAINS                              60.001957 +- 0.000332 Hz
      width = 0.000574 (parameter sweep) (+) 0.000023 (calibration) (+) 0.000331 (sem), /2

AND THE CALIBRATION IS 25x SMALLER THAN THE PARAMETER SWEEP. That is the whole point of this
morning: the biblioteca said "measuring the grid with an uncalibrated sample clock is measuring a
rubber ruler against a rubber ruler", and the crystal is no longer the limit -- the lock-in's own
sensitivity to block length is.

THE OUTSIDE SEAT, and it reads THE WORLD and not us. The Eastern Interconnection's SCHEDULED
frequency is one of three discrete published values: 60.00 normally, 59.98 while correcting FAST
time error, 60.02 while correcting SLOW. Against the measurement:

    59.98  (fast TEC)   66.2 widths away   EXCLUDED
    60.02  (slow TEC)   54.4 widths away   EXCLUDED
    -> NO TIME ERROR CORRECTION was running in this window. A discrete, falsifiable outside claim.
    and the grid sat +1.957 mHz ABOVE its 60.00 schedule, resolved at 5.9 widths.

AND DO NOT CONFUSE THOSE TWO QUESTIONS. "Which schedule is active" and "is the frequency equal to
the schedule" are different, and the first printing of this conflated them -- it labelled 60.00
EXCLUDED at 5.9 widths as though that were a finding, when a schedule is a CONTROL TARGET and not
a prediction of a 300 s mean. The grid is never exactly on schedule; that is what the operators
are correcting toward.                                                                  (fa 19)

TWO ACCEPTANCE TESTS, AND THE FIRST USES NO CLOCK AT ALL:
  * THE HARMONIC RATIO IS FORCED BY ARITHMETIC. The 240 Hz line is the fourth harmonic, so
    f240/f120 must be exactly 2 whatever the crystal, the grid or the room do. Measured
    2.00000132 +- 0.00000780 -- 0.17 widths from 2. PASS. Nothing else here can catch the
    lock-in being WRONG rather than merely imprecise.                                    (gd 4)
  * THE PARAMETER SWEEP, which is what caught this morning's artifact: refit at block lengths
    1/2/4/8 s and with leading blocks dropped. Spread 0.000574 Hz, and that spread IS the width
    rather than the OLS sem, because it is the larger of the two.

THE RULERS THAT PICKED THE DESIGN. THE COHERENCE TIME: the grid's instantaneous frequency wanders
while its ACCUMULATED count is what operators hold, so dnu ~ 0.04 Hz gives tau_c ~ 8 s and
coherent integration past that smears the line -- hence 2 s blocks. EL PRODUCTO: a lock-in returns
two numbers and |.|^2 keeps one; the phase IS the measurement here, so both are kept.

NO AUDIO CONTENT IS KEPT OR EXAMINED. The raw capture is reduced on the laptop to the complex
amplitude at two frequencies per block and deleted; no speech band is looked at and no broadband
spectrum is returned beyond a local floor beside each line.

    python3 red.py                  one 300 s reading
    python3 red.py --seconds 600    narrower, and the sweep will say whether it earned it
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, 'red_worker.py')
LOG = os.path.join(HERE, 'red.jsonl')
HOST = 'laptop'
SCHEDULES = (('60.00  normal schedule', 60.00),
             ('59.98  FAST time-error correction', 59.98),
             ('60.02  SLOW time-error correction', 60.02))


def codec_ppm():
    """the ruler, from watch/cristal.py's own log. READ, never typed in here."""
    try:
        import cristal
        rows = [json.loads(l) for l in open(cristal.LOG) if l.strip()]
    except Exception:
        return None, None
    v = [r['codec_vs_laptop_ppm'] for r in rows
         if r.get('outcome') == 'committed' and r.get('codec_vs_laptop_ppm') is not None]
    if len(v) < 2:
        return None, None
    import statistics as st
    leg = [r.get('leg_ppm_chrony') or 0.0 for r in rows if r.get('outcome') == 'committed']
    skew = max([r.get('leg_skew_ppm') or 0.0 for r in rows if r.get('outcome') == 'committed']
               + [0.0])
    m = st.mean(v) + (st.mean(leg) if leg else 0.0)
    sem = st.stdev(v) / len(v) ** 0.5
    return m, (sem ** 2 + skew ** 2) ** 0.5


def read(seconds=300.0):
    src = open(WORKER).read()
    try:
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=12', '-o', 'BatchMode=yes', HOST,
                            'python3 - %g' % seconds],
                           input=src, capture_output=True, text=True, timeout=seconds + 300)
        return json.loads([l for l in (r.stdout or '').splitlines()
                           if l.strip().startswith('{')][-1])
    except Exception as e:
        return {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'outcome': 'nothing-returned',
                'err': '%s: %s' % (type(e).__name__, str(e)[:160])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=300.0)
    a = ap.parse_args()
    d = read(a.seconds)
    c, cw = codec_ppm()
    d['codec_ppm'], d['codec_ppm_width'] = c, cw
    if d.get('outcome') == 'committed' and c is not None:
        f = d['lines']['120']['f_hz_in_codec_units']
        sem = d['lines']['120']['sem_hz']
        sw = d.get('sweep_spread_hz') or 0.0
        d['harmonic2_gps_hz'] = f * (1.0 + c / 1e6)
        d['width_hz'] = (sw ** 2 + (abs(f) * cw / 1e6) ** 2 + sem ** 2) ** 0.5
        d['mains_hz'] = d['harmonic2_gps_hz'] / 2.0
        d['mains_width_hz'] = d['width_hz'] / 2.0
    with open(LOG, 'a') as f:
        f.write(json.dumps(d) + '\n')

    print('  LA RED -- the grid, on a calibrated sample clock')
    print('  ONE EVENT, TWO INDEPENDENT ROOTS: the codec crystal counts it, the Bodnar tree')
    print('  says what the counts are worth. (Two, not three -- Supabase cannot hear a room.)\n')
    if d.get('outcome') != 'committed':
        print('  OUTCOME %s\n  %s' % (str(d.get('outcome')).upper(), d.get('err')))
        return 0
    L = d['lines']
    print('  %-7s%17s%13s%11s%8s' % ('line', 'f (codec Hz)', 'sem', 'snr/blk', 'nblk'))
    for k in ('120', '240'):
        if k in L:
            print('  %-7s%17.6f%13.6f%11.1f%8d'
                  % (k, L[k]['f_hz_in_codec_units'], L[k]['sem_hz'],
                     L[k]['snr_block'] or float('nan'), L[k]['n_blocks']))
    hr, hw = d.get('harmonic_ratio'), d.get('harmonic_ratio_sem')
    if hr:
        print('\n  ACCEPTANCE 1, no clock in it: f240/f120 = %.8f +- %.8f -> %.2f widths from 2  %s'
              % (hr, hw, d['harmonic_widths_from_2'],
                 'PASS' if d['harmonic_widths_from_2'] < 3 else 'FAIL -- the lock-in is WRONG'))
    print('  ACCEPTANCE 2, block+drop sweep spread %.6f Hz %s'
          % (d['sweep_spread_hz'],
             '(this IS the width: larger than the sem)'
             if d['sweep_spread_hz'] > L['120']['sem_hz'] else '(smaller than the sem)'))
    if d.get('mains_hz'):
        print('\n  codec ruler  %+.4f +- %.4f ppm  -> %+.6f Hz at 120 Hz  (%.0fx under the sweep)'
              % (d['codec_ppm'], d['codec_ppm_width'],
                 L['120']['f_hz_in_codec_units'] * d['codec_ppm'] / 1e6,
                 d['sweep_spread_hz'] / max(1e-12, abs(L['120']['f_hz_in_codec_units'])
                                            * d['codec_ppm_width'] / 1e6)))
        print('  MAINS, %.0f s mean, GPS-referenced   %.6f +- %.6f Hz'
              % (d['seconds_asked'], d['mains_hz'], d['mains_width_hz']))
        print('\n  THE OUTSIDE SEAT -- the three PUBLISHED schedules, discrete candidates:')
        for nm, cand in SCHEDULES:
            w = abs(d['mains_hz'] - cand) / d['mains_width_hz']
            tag = ('EXCLUDED' if w > 3 else 'on schedule')
            if cand == 60.00 and w > 3:
                tag = 'nearest, and the grid is never exactly ON a schedule'
            print('    %-36s %6.2f -> %7.1f widths  %s' % (nm, cand, w, tag))
        print('    -> %s'
              % ('NO time-error correction was running: both offsets excluded.'
                 if min(abs(d['mains_hz'] - 59.98), abs(d['mains_hz'] - 60.02))
                 / d['mains_width_hz'] > 3 else 'a TEC offset is LIVE or cannot be excluded.'))
        off = (d['mains_hz'] - 60.0) * 1000.0
        print('    the grid sat %+.3f mHz off its 60.00 schedule; a line-frequency clock was '
              '%s' % (off, 'GAINING' if off > 0 else 'LOSING'))
        print('    at %.1f ppm during this window (%.2f s/day if it held).'
              % (abs(off / 1000) / 60 * 1e6, abs(off / 1000) / 60 * 86400))
    print('  OUTCOME  %s' % d['outcome'].upper())
    return 0


if __name__ == '__main__':
    sys.exit(main())
