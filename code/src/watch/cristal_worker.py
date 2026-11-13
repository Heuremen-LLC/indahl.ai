#!/usr/bin/env python3
"""cristal_hwptr.py -- EL TERCER RINCON, read from the CODEC'S OWN COUNTER.
(Bones, 11 Oct 2026. Third instrument for one quantity, and the first two are why.)

THE QUANTITY: the rate of the ALC257 audio codec's sample clock, in Bodnar-referenced seconds.
It matters because the house has exactly two independent clock roots -- the Leo Bodnar LBE-1421
on flock-pi (which roots the Pi, the Mac, Armature, the laptop and the HackRF Pro's sample
clock) and Supabase -- and The Bonefish needs three. This codec's crystal is downstream of
neither. It is a RATE reference, which is all the triangle wants: ratios between READS.

=============================================================================================
TWO INSTRUMENTS WITHDRAWN BEFORE THIS ONE, and the numbers are the whole argument for it.

(1) WHOLE-PROCESS TIMING, several durations, fitting elapsed against frames to split the
    per-run setup cost S from the part P that scales. Killed by its own premise:
        5.0 s asked -> elapsed 5.2036 s   overhead 0.2036 s
        10.0 s asked -> elapsed 10.1607 s  overhead 0.1607 s
    The overhead moved 43 ms between two runs minutes apart, so S was NOT common to every run,
    which is the one thing THE SPLIT requires of it. On a 5 s lever that is 8,685 ppm.     (fa 8)

(2) IN-BAND BYTE-ARRIVAL TIMING: one continuous stream, (bytes_so_far, t) stamped at every
    chunk, least-squares fitted. It LOOKED excellent -- 4 runs of 60 s on hw:1,0 gave
    -300.32, -305.97, -300.01, -300.73 ppm, mean -301.76, sd 2.82. Reproducible to 3 ppm,
    n=4, and I was one keystroke from publishing it as the third corner.
    THEN THE SAME STREAM WAS REFITTED DROPPING k LEADING CHUNKS, 120 s runs, n=3 each:
        drop 0   -98.08 +- 1.71      drop 10   +98.98 +- 1.22
        drop 1   -77.75 +- 1.62      drop 20  +256.80 +- 0.60
        drop 2   -57.51 +- 1.55      drop 40   +80.51 +- 0.50
        drop 5    +2.65 +- 1.40
    THE ANSWER SWEEPS 355 ppm WITH A FREE PARAMETER while every single value is reproducible
    to ~1.5 ppm. And the 60 s runs read -301.76 +- 1.41 where the 120 s runs read -57.51 +-
    0.90 at the SAME setting: 244 ppm apart with 1 ppm widths, 170 sems. Bytes arrive when the
    pipe and the scheduler say so, not when the codec does, and a straight line through a lumpy
    series has a slope that depends on the window. The run-to-run reproducibility was the
    apparatus's DETERMINISTIC startup behaviour wearing the crystal's name.           (fa 4, 24)

    THE LESSON THAT BUILT THIS FILE: reproducibility is not accuracy. Four agreeing runs made a
    window-dependent artifact look like a measured constant, and only varying a parameter I had
    picked by default exposed it.
=============================================================================================

SO THE COUNT COMES FROM THE CODEC AND NOT FROM THE PIPE. /proc/asound/cardN/pcm0c/sub0/status
exposes `hw_ptr`: the hardware sample position, advanced by the codec's own clock. It is linear
in true time BY CONSTRUCTION -- it is a sample counter -- so there is no buffer-filling
structure for a line to curve through. The only noise left is the latency of reading /proc,
which is sub-millisecond, zero-mean, and averages down instead of accumulating.

`tstamp` in that file reads 0.000000000 on this kernel, so the stamp is taken here, bracketing
the read and using the midpoint. The bracket width is recorded per sample, not assumed.

AND THE DROP SWEEP IS NOW THE ACCEPTANCE TEST, not an afterthought. The same refit that killed
instrument (2) runs on every stream here, from both ends. A FLAT sweep is the only thing that
earns the number; a sloping one means the series is still not a line and the reading is
withdrawn by the instrument itself rather than by me later.

SECONDS COME FROM THE PI: stratum 1, refclock = the Bodnar. A thread samples the two-way offset
to 192.168.8.145:8769 throughout (min rtt 1.536 ms), those offsets are themselves fitted, and
every stamp is converted to Pi-referenced seconds before the rate fit.

NO AUDIO CONTENT IS READ, STORED OR EXAMINED. arecord's samples go to /dev/null and this process
never sees them; it reads a counter out of /proc. Nothing audible is ever produced.
"""
import json
import re
import socket
import subprocess as _sp
import subprocess
import sys
import threading
import time

PI = ('192.168.8.145', 8769)
NOMINAL = 48000.0
CARD, DEV = 1, 'hw:1,0'
STATUS = '/proc/asound/card%d/pcm0c/sub0/status' % CARD
OUT = '/home/ctrai/cristal_hwptr.jsonl'


def two_way(trials=25, timeout=0.4):
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.settimeout(timeout)
    rs = []
    for _ in range(trials):
        try:
            t0 = time.time()
            sk.sendto(b'?', PI)
            d, _ = sk.recvfrom(128)
            t3 = time.time()
            t1, t2 = (float(x) for x in d.split())
            rs.append(((t3 - t0) - (t2 - t1), ((t1 - t0) + (t2 - t3)) / 2.0))
        except Exception:
            continue
    sk.close()
    if not rs:
        return None
    rs.sort()
    return {'offset_s': rs[0][1], 'min_delay_s': rs[0][0], 'n': len(rs),
            'at': (t0 + time.time()) / 2.0}


def chrony_leg():
    """THE REFERENCE LEG, FROM THE INSTRUMENT THAT ALREADY MEASURES IT WELL.

    11 Oct, and this replaces a UDP echo I had no business using for this. The quantity needed is
    the rate of this laptop's CORRECTED system clock against flock-pi (whose refclock is the Leo
    Bodnar). chrony measures exactly that, continuously, filtering hundreds of min-delay samples
    over hours. My two-way echo measured it from 3 samples over 180 s across WIFI and got:

        echo:    +0.828 +- 0.185 ppm   (3 x 180 s)   and  -1.526 +- 1.295 ppm  (one 60 s run)
        chrony:  residual freq -0.002 ppm, skew 0.129 ppm, applied freq moving 0.008 ppm / 200 s

    The echo was wrong by about 0.83 ppm and ~60x looser. Wayfinder, when I prescribed an ethernet
    cable to fix it: "laptop has to go through the pi to get on the etherner bones, unless there's
    a usb adapter for ut." Which is the right question to ask of a prescription -- and the cable
    was never the fix. THE REFERENCE LEG WAS NEVER THE NETWORK'S JOB; it was chrony's, and I had
    built a worse second instrument for a quantity already being read properly.          (gd 4)

    `Residual freq` is the leftover rate error of the corrected clock against the selected source,
    so codec-vs-Bodnar = codec-vs-this-clock + residual. `Skew` is chrony's own bound on it and
    becomes the width. Returned with both ends sampled, because a leg read once is a leg assumed.
    """
    try:
        t = _sp.run(['chronyc', 'tracking'], capture_output=True, text=True, timeout=10).stdout or ''
    except Exception as e:
        return {'err': '%s: %s' % (type(e).__name__, e)}
    d = {}
    for key, name in (('Residual freq', 'resid_ppm'), ('Skew', 'skew_ppm'),
                      ('Frequency', 'freq_ppm'), ('RMS offset', 'rms_s')):
        m = re.search(r'^%s\s*:\s*([-+0-9.eE]+)' % key, t, re.M)
        if m:
            d[name] = float(m.group(1))
    m = re.search(r'^Reference ID\s*:\s*(.+)$', t, re.M)
    d['refid'] = m.group(1).strip() if m else None
    if 'slow' in t.split('Frequency')[-1].split('\n')[0] and 'freq_ppm' in d:
        d['freq_ppm'] = -abs(d['freq_ppm'])          # 'N ppm slow' -> the oscillator is low
    return d


def fit(ts, ys):
    n = len(ts)
    if n < 3:
        return None
    tm = sum(ts) / n
    tt = [t - tm for t in ts]
    sxx = sum(t * t for t in tt)
    if sxx <= 0:
        return None
    ym = sum(ys) / n
    b = sum(t * (y - ym) for t, y in zip(tt, ys)) / sxx
    resid = [y - (ym + b * t) for t, y in zip(tt, ys)]
    s2 = sum(r * r for r in resid) / (n - 2)
    return {'slope': b, 'slope_sem': (s2 / sxx) ** 0.5, 'resid_sd': s2 ** 0.5,
            'n': n, 'span_s': max(ts) - min(ts), 'y_at_tmean': ym, 't_mean': tm}


class Offsets(threading.Thread):
    def __init__(self, every):
        super().__init__(daemon=True)
        self.every, self.stop, self.rows = every, threading.Event(), []

    def run(self):
        while not self.stop.is_set():
            r = two_way()
            if r:
                self.rows.append(r)
            self.stop.wait(self.every)


def read_hw_ptr():
    """(hw_ptr, stamp, bracket_s) -- the read is bracketed and the midpoint used."""
    a = time.time()
    try:
        with open(STATUS) as f:
            txt = f.read()
    except OSError:
        return None
    b = time.time()
    if 'RUNNING' not in txt:
        return None
    m = re.search(r'^hw_ptr\s*:\s*(\d+)', txt, re.M)
    if not m:
        return None
    return int(m.group(1)), (a + b) / 2.0, b - a


def measure(seconds=120.0, poll=0.2):
    offs = Offsets(every=max(5.0, seconds / 20.0))
    offs.start()
    p = subprocess.Popen(
        ['arecord', '-D', DEV, '-f', 'S16_LE', '-r', str(int(NOMINAL)), '-c', '2',
         '--samples=%d' % int(NOMINAL * (seconds + 8)), '-t', 'raw'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)                                   # let the stream reach RUNNING

    leg0 = chrony_leg()
    pts, brackets, wraps = [], [], 0
    base, last = 0, None
    t_end = time.time() + seconds
    while time.time() < t_end:
        r = read_hw_ptr()
        if r:
            hp, ts, w = r
            if last is not None and hp < last:
                base += last                          # unwrap, counted not assumed away
                wraps += 1
            last = hp
            pts.append((base + hp, ts))
            brackets.append(w)
        time.sleep(poll)
    leg1 = chrony_leg()
    offs.stop.set()
    offs.join(timeout=20)
    try:
        p.terminate()
        p.wait(timeout=20)
    except Exception:
        pass

    row = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'seconds_asked': seconds, 'poll_s': poll,
           'n_points': len(pts), 'n_offsets': len(offs.rows), 'hw_ptr_wraps': wraps,
           'read_bracket_us_median': (sorted(brackets)[len(brackets) // 2] * 1e6)
           if brackets else None,
           'source': STATUS, 'device': DEV,
           'reference': 'flock-pi 192.168.8.145 (stratum 1, refclock = Leo Bodnar LBE-1421)'}
    if len(pts) < 20:
        row.update(outcome='nothing-returned',
                   err='only %d hw_ptr reads; the stream never reached RUNNING or /proc went '
                       'away' % len(pts))
        return row
    if len(offs.rows) < 3:
        row.update(outcome='nothing-returned',
                   err='the Pi echo answered %d times and the offset fit needs 3; the interval '
                       'would be in laptop seconds under a Pi label' % len(offs.rows))
        return row

    of = fit([r['at'] for r in offs.rows], [r['offset_s'] for r in offs.rows])
    row.update(laptop_vs_pi_ppm=of['slope'] * 1e6, laptop_vs_pi_ppm_sem=of['slope_sem'] * 1e6,
               offset_resid_us=of['resid_sd'] * 1e6, offset_span_s=of['span_s'])

    def to_pi(t):
        return t + (of['y_at_tmean'] + of['slope'] * (t - of['t_mean']))

    def rate_of(sl):
        f = fit([to_pi(t) for _, t in sl], [float(h) for h, _ in sl])
        if not f:
            return None, None, None
        return ((f['slope'] / NOMINAL - 1.0) * 1e6, (f['slope_sem'] / NOMINAL) * 1e6,
                f['resid_sd'])

    # CODEC AGAINST THIS LAPTOP'S OWN CORRECTED CLOCK -- no network in it at all. This is the
    # reading that makes the codec a ROOT: a counter that differs from the clock it would have to
    # BE cannot be that clock, and nothing in it rests on a path.
    f_raw = fit([t for _, t in pts], [float(h) for h, _ in pts])
    row['codec_vs_laptop_ppm'] = ((f_raw['slope'] / NOMINAL - 1.0) * 1e6) if f_raw else None
    row['codec_vs_laptop_sem_OLS'] = ((f_raw['slope_sem'] / NOMINAL) * 1e6) if f_raw else None

    # THE LEG, TWO SEATS, AND THE DISAGREEMENT KEPT RATHER THAN RESOLVED.               (gd 12)
    row['chrony_leg_before'], row['chrony_leg_after'] = leg0, leg1
    resid_ppm = leg1.get('resid_ppm', leg0.get('resid_ppm'))
    skew_ppm = max(leg0.get('skew_ppm', 0.0) or 0.0, leg1.get('skew_ppm', 0.0) or 0.0) or None
    if row['codec_vs_laptop_ppm'] is not None and resid_ppm is not None:
        row['rate_ppm_via_chrony'] = row['codec_vs_laptop_ppm'] + resid_ppm
        row['leg_ppm_chrony'] = resid_ppm
        row['leg_skew_ppm'] = skew_ppm

    rate, sem, resid = rate_of(pts)
    row.update(rate_ppm=rate, rate_ppm_sem_OLS=sem, fit_resid_frames=resid,
               fit_resid_ms=(resid / NOMINAL * 1e3) if resid else None,
               true_sr=NOMINAL * (1.0 + rate / 1e6), fit_span_s=to_pi(pts[-1][1]) - to_pi(pts[0][1]))

    # THE ACCEPTANCE TEST. Drop k from the front, then k from the back. If the answer moves, the
    # series is not a line and this instrument has not measured the crystal either.
    sweep_f, sweep_b = {}, {}
    for k in (0, 2, 5, 10, 20, 40, 80):
        if len(pts) - k >= 20:
            sweep_f[k] = rate_of(pts[k:])[0]
            sweep_b[k] = rate_of(pts[:len(pts) - k])[0]
    row['sweep_front_ppm'], row['sweep_back_ppm'] = sweep_f, sweep_b
    if row.get('rate_ppm_via_chrony') is not None and rate is not None:
        # the echo leg minus the chrony leg: a reading ABOUT THE WIFI PATH, not a nuisance
        row['leg_ppm_echo'] = row.get('laptop_vs_pi_ppm')
        row['leg_disagreement_ppm'] = rate - row['rate_ppm_via_chrony']
    vals = [v for v in list(sweep_f.values()) + list(sweep_b.values()) if v is not None]
    row['sweep_spread_ppm'] = (max(vals) - min(vals)) if vals else None
    row['outcome'] = 'committed'
    return row


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
    poll = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    r = measure(secs, poll)
    with open(OUT, 'a') as f:
        f.write(json.dumps(r) + '\n')
    print(json.dumps(r), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
