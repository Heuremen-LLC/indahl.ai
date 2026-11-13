#!/usr/bin/env python3
"""cristal.py -- EL TERCER RINCON: the third Bonefish corner, and it needed no antenna.
(Bones, 11 Oct 2026.)

THE HOUSE HAD TWO INDEPENDENT CLOCK ROOTS. Measured this morning with reloj_casa.py, every link
read: the Leo Bodnar LBE-1421 on flock-pi roots the Pi at stratum 1 and the Mac, Armature, the
laptop AND the HackRF Pro's sample clock under it; Supabase's Postgres created_at is the only
clock not downstream of it. The Bonefish needs three corners, and a parent with its servo child
is not two clocks -- the loop's job is to force their rates equal.

THE THIRD IS THE LAPTOP'S ALC257 AUDIO CODEC CRYSTAL, and it costs nothing. It is downstream of
neither the Bodnar nor Supabase. It is a RATE reference rather than a time reference, which is
all the triangle wants: it tests ratios between READS, never a number against a constant.

MEASURED 11 Oct, pooled over 6 runs of 120-180 s, ~900 in-band points each:

    CODEC vs the LAPTOP's own clock   -3.930 ppm   sd 0.2965   sem 0.121   (n=6)
    CODEC vs the BODNAR               -3.934 ppm   +- 0.190 ppm
                                      = 0.121 (stat, n=6) (+) 0.146 (chrony skew)
    within-stream model-choice spread  0.005 to 0.076 ppm
    excluded:  slaved to the corrected system clock   +0.000 ppm   20.7 widths
    excluded:  derived from the platform oscillator  -12.068 ppm   42.9 widths

Those two exclusions are the point. A counter that looked independent could have been either of
those, and both were named BEFORE the reading and priced against it. The laptop's own oscillator
runs 12.068 ppm slow (chronyc Frequency) while chrony holds its residual freq to -0.004 ppm, so
the two impostors sit on OPPOSITE sides of the reading and neither survives.             (fa 26)

AND THE FIRST READING THAT MAKES IT A ROOT USES NO NETWORK AT ALL: hw_ptr against this laptop's
own clock. That is the comparison a slaved counter could not survive, and nothing in it rests on
a path, a cable or a peer.

=============================================================================================
TWO OF MY OWN NUMBERS WITHDRAWN HERE, kept beside the corrections.                     (gd 16)

(a) "-4.553 +- 0.193 ppm, and putting the laptop on ETHERNET is what collapses the systematic."
    Wayfinder: "laptop has to go through the pi to get on the etherner bones, unless there's a
    usb adapter for ut." The right question to ask of a prescription, and asking it showed the
    prescription was WRONG, not merely awkward. Nothing needs to be bought or plugged in. The
    network was only ever carrying the REFERENCE LEG -- the laptop's rate against the Bodnar --
    and chrony measures that leg continuously from hundreds of filtered samples:

        chrony leg   -0.0020, -0.0080, -0.0010 ppm    stable to 0.004 ppm, skew 0.146
        echo leg     -0.7224, +0.6866, -1.3754 ppm    scatters ~1 ppm      <- 250x worse

    I had built a second, worse instrument for a quantity already being read properly, and then
    prescribed hardware to fix my own instrument.                                       (gd 4)

(b) "-3.725 +- 0.013 ppm" for codec-vs-laptop. That sd came from THREE draws, and an sd from
    three draws carries about 50% of its own value -- quoting a sem off it as the width was
    reading the dice. Pooled over 6 runs: sd 0.2965, sem 0.121. TEN TIMES looser. And the
    ~0.3 ppm run-to-run wander is not noise to be averaged away, it IS the stability of this
    corner (thermal, most likely), which the n=3 batch made look 100x better than it is.
                                                                           (fa 3, gd 9)
=============================================================================================

THE ECHO IS KEPT AS A SECOND SEAT ON THE LEG, and its disagreement with chrony is reported
rather than resolved: that gap is a reading about the wifi path, not a nuisance.          (gd 12)

=============================================================================================
TWO INSTRUMENTS WERE WITHDRAWN TO GET HERE. Both are in cristal_worker.py's docstring with their
numbers; the short version, because the shape recurs:

  * WHOLE-PROCESS TIMING at several durations, to split the per-run setup S from the scaling P.
    The setup cost moved 43 ms between runs, so S was not common to every run -- the one thing
    THE SPLIT requires. On a 5 s lever that is 8,685 ppm.
  * IN-BAND BYTE ARRIVAL, stamping (bytes_so_far, t) off the pipe. Four 60 s runs agreed to
    sd 2.82 ppm on -301.76 ppm and I was one keystroke from publishing that as the third corner.
    Refitting the SAME streams while dropping k leading chunks swept the answer 355 ppm, every
    value reproducible to ~1.5 ppm. REPRODUCIBILITY IS NOT ACCURACY: four agreeing runs were the
    apparatus's deterministic startup wearing the crystal's name.                    (fa 4, 24)

So the count is taken from the CODEC'S OWN COUNTER -- hw_ptr out of
/proc/asound/card1/pcm0c/sub0/status -- which is a sample counter and therefore linear in true
time by construction. And THE DROP SWEEP IS NOW THE ACCEPTANCE TEST on every stream, from both
ends: a flat sweep is the only thing that earns the number.
=============================================================================================

NO AUDIO CONTENT IS READ, STORED OR EXAMINED, and nothing audible is ever produced. arecord's
samples go to /dev/null; this reads a counter out of /proc.

    python3 cristal.py                 one 180 s reading
    python3 cristal.py --seconds 60    shorter, and the width will say so
    python3 cristal.py --last          the last reading on file, with its age
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, 'cristal_worker.py')
LOG = os.path.join(HERE, 'cristal.jsonl')
HOST = 'laptop'
SEAT = 'ALC257 codec crystal (laptop)'


def read(seconds=180.0, poll=0.2, timeout=None):
    """Run the worker ON the laptop and bring back one reading.

    The source is piped in, exactly as three_clocks.py does with pi_gps.py, so nothing has to be
    installed or kept in sync on the far machine -- the house holds one copy of the instrument.
    """
    src = open(WORKER).read()
    to = timeout or (seconds + 180)
    try:
        r = subprocess.run(['ssh', '-o', 'ConnectTimeout=12', '-o', 'BatchMode=yes', HOST,
                            'python3 - %g %g' % (seconds, poll)],
                           input=src, capture_output=True, text=True, timeout=to)
        return json.loads((r.stdout or '').strip().splitlines()[-1])
    except Exception as e:
        return {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'outcome': 'nothing-returned',
                'err': '%s: %s' % (type(e).__name__, str(e)[:160]), 'seat': SEAT}


def last():
    """the most recent reading on file, or None. Carries the moment it was read."""
    try:
        rows = [json.loads(l) for l in open(LOG) if l.strip()]
    except Exception:
        return None
    good = [r for r in rows if r.get('outcome') == 'committed']
    return good[-1] if good else (rows[-1] if rows else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=180.0)
    ap.add_argument('--poll', type=float, default=0.2)
    ap.add_argument('--last', action='store_true')
    a = ap.parse_args()

    if a.last:
        d = last()
        if not d:
            print('  NOTHING ON FILE at %s' % LOG)
            return 0
        age = time.time() - time.mktime(time.strptime(d['at'][:19], '%Y-%m-%dT%H:%M:%S'))
        print('  last reading %s  (%.1f min ago)  outcome %s' % (d['at'], age / 60.0, d['outcome']))
        if d.get('rate_ppm') is not None:
            # THE CHRONY LEG IS THE ONE THAT GETS PRINTED. Showing rate_ppm here while
            # reloj_casa.py showed rate_ppm_via_chrony put TWO numbers for one reading into the
            # house's own output, 1.4 ppm apart -- which is the start of a file disagreeing with
            # itself about an object, the exact shape that cost this morning.             (fa 24)
            print('  %s   %+.3f ppm vs the Bodnar   (vs the laptop clock %+.3f)'
                  % (SEAT, d.get('rate_ppm_via_chrony', d['rate_ppm']),
                     d.get('codec_vs_laptop_ppm', float('nan'))))
            print('  sweep spread %.3f ppm   leg: chrony %+.4f, my echo %s -- kept, not resolved'
                  % (d.get('sweep_spread_ppm') or float('nan'),
                     d.get('leg_ppm_chrony') or float('nan'),
                     ('%+.4f' % d['leg_ppm_echo']) if d.get('leg_ppm_echo') is not None else 'n/a'))
        return 0

    d = read(a.seconds, a.poll)
    d['seat'] = SEAT
    with open(LOG, 'a') as f:
        f.write(json.dumps(d) + '\n')

    print('  EL TERCER RINCON -- an oscillator this house does not discipline')
    print('  seat %s' % SEAT)
    print('  reference %s\n' % d.get('reference', 'flock-pi (stratum 1, refclock = the Bodnar)'))
    if d.get('outcome') != 'committed':
        print('  OUTCOME  %s' % str(d.get('outcome')).upper())
        print('  %s' % d.get('err'))
        return 0
    print('  source   %s   device %s' % (d['source'], d['device']))
    print('  points   %d in band over %.1f s   read bracket %.0f us median   wraps %d'
          % (d['n_points'], d['fit_span_s'], d['read_bracket_us_median'], d['hw_ptr_wraps']))
    print('  fit      residual %.4f ms  (the byte-arrival instrument gave 34.8 ms)'
          % d['fit_resid_ms'])
    print()
    print('  CODEC vs LAPTOP  %+.3f ppm   <- no network in this one; it is what makes it a ROOT'
          % (d.get('codec_vs_laptop_ppm') or float('nan')))
    print('  CODEC vs BODNAR  %+.3f ppm   true sr %.4f Hz   (leg from chrony, not my echo)'
          % (d.get('rate_ppm_via_chrony', d['rate_ppm']), d['true_sr']))
    print('  ACCEPTANCE   drop sweep spread %.3f ppm, both ends -- %s'
          % (d['sweep_spread_ppm'],
             'FLAT, the number is earned' if d['sweep_spread_ppm'] < 1.0
             else 'NOT FLAT: the series is not a line and this reading is WITHDRAWN'))
    print('  the servo    laptop vs Pi %+.3f +- %.3f ppm   (its OSCILLATOR is 11.985 ppm slow'
          % (d['laptop_vs_pi_ppm'], d['laptop_vs_pi_ppm_sem']))
    print('               while chrony holds residual freq +0.002 ppm. A disciplined pair has no')
    print('               rate difference to read, which is why it cannot be two corners. And my')
    print('               echo disagrees with chrony here, over wifi: that gap is the systematic.)')
    print('  OUTCOME  %s' % d['outcome'].upper())
    return 0


if __name__ == '__main__':
    sys.exit(main())
