#!/usr/bin/env python3
"""red_worker.py -- LA RED: the grid read on a CALIBRATED sample clock. Runs on the laptop.
(Bones, 11 Oct 2026.)

ONE EVENT, TWO INDEPENDENT ROOTS. The mains second harmonic is present at every machine in the
house simultaneously -- power-line propagation across a house is nanoseconds -- so it is an event
the ALC257 codec crystal (root 3) and the Bodnar tree (root 1) can BOTH stamp. The codec stamps it
in SAMPLES; the Bodnar tree supplies the seconds those samples are worth. That is the first read
of one event by two genuinely independent roots in this house.

IT IS TWO ROOTS AND NOT THREE, STATED PLAINLY. Supabase cannot hear a room; the Mac's own audio
crystal would be a third but the Mac has no capture tool installed (no soundcard, no ffmpeg, no
sox). So this is a leg of The Bonefish, not the whole triangle.

AND IT IS THE MEASUREMENT THE BIBLIOTECA SAID WAS BLOCKED: "measuring the grid with an
uncalibrated sample clock is measuring a rubber ruler against a rubber ruler." The ruler is now
calibrated -- the codec is -3.934 +- 0.190 ppm against the Bodnar (watch/cristal.py), which at
120 Hz is 0.0000228 Hz. Grid excursions are ~0.04 Hz at the second harmonic, so the ruler is no
longer the limit.

THREE RULERS OFF THE SHEET, AND THEY PICKED THE DESIGN:

  THE COHERENCE TIME, tau_c = 1/(pi.dnu). The grid's instantaneous frequency wanders while its
  ACCUMULATED cycle count is held accurate by operators, so dnu ~ 0.04 Hz at 120 Hz gives
  tau_c ~ 8 s. Integrating coherently past that smears the line into noise. Hence 2 s blocks --
  inside coherence, and unambiguous for phase steps up to +-0.25 Hz.

  EL PRODUCTO: a lock-in returns TWO numbers and |.|^2 keeps one. The phase is the entire
  measurement here, so both are kept: magnitude for the SNR, phase for the frequency.

  THE EXCLUSION / ACCEPTANCE: the 240 Hz line is the FOURTH harmonic, and a harmonic ratio is an
  EXACT INTEGER forced by arithmetic, not by hardware. So f240/f120 must be 2.000000 whatever the
  crystal, the grid or the room do. That test needs NO CLOCK AT ALL, and it is the only thing here
  that can catch the lock-in being wrong rather than merely imprecise.                   (gd 4)

AND THE PARAMETER SWEEP RIDES ALONG, because that is what caught this morning's artifact: the
frequency is refit at several block lengths and with leading blocks dropped. A reading that moves
with the block length is a statement about the block length.

NO AUDIO CONTENT LEAVES THIS PROCESS. The raw file is written to /tmp, reduced to the complex
amplitude at two frequencies per block, and deleted. No speech band is examined, no broadband
spectrum is returned beyond a local noise floor beside each line.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

NOMINAL_FS = 48000.0
DEV = 'hw:1,0'
RAW = '/tmp/red_capture.raw'
LINES = (120.0, 240.0)


def chrony_leg():
    import re
    try:
        t = subprocess.run(['chronyc', 'tracking'], capture_output=True, text=True,
                           timeout=10).stdout or ''
    except Exception as e:
        return {'err': str(e)[:80]}
    d = {}
    for k, nm in (('Residual freq', 'resid_ppm'), ('Skew', 'skew_ppm')):
        m = re.search(r'^%s\s*:\s*([-+0-9.eE]+)' % k, t, re.M)
        if m:
            d[nm] = float(m.group(1))
    return d


def lockin(x, f0, fs, block_s):
    """complex amplitude per block at f0, assuming fs. BOTH numbers kept."""
    n = int(block_s * fs)
    nb = len(x) // n
    if nb < 4:
        return None
    out = []
    for k in range(nb):
        seg = x[k * n:(k + 1) * n]
        idx = np.arange(k * n, (k + 1) * n, dtype=np.float64)
        ph = -2.0j * np.pi * f0 * idx / fs
        out.append(np.sum(seg * np.exp(ph)) / n)
    return np.asarray(out), n / fs


def freq_from_phase(A, dt, f0):
    """mean frequency over the window from the UNWRAPPED phase slope, with its own sem.

    The slope is the measurement; the residual about the line is the grid's wander inside the
    window, which is a reading and not an error.
    """
    ph = np.unwrap(np.angle(A))
    t = np.arange(len(ph)) * dt
    tm = t - t.mean()
    sxx = float((tm * tm).sum())
    if sxx <= 0:
        return None
    b = float((tm * (ph - ph.mean())).sum() / sxx)
    resid = ph - (ph.mean() + b * tm)
    s2 = float((resid ** 2).sum() / max(1, len(ph) - 2))
    return {'f_offset_hz': b / (2 * np.pi), 'f_hz_in_codec_units': f0 + b / (2 * np.pi),
            'sem_hz': (s2 / sxx) ** 0.5 / (2 * np.pi),
            'phase_resid_rad': s2 ** 0.5, 'n_blocks': len(ph),
            'wander_hz_rms': s2 ** 0.5 / (2 * np.pi * dt)}


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    leg0 = chrony_leg()
    t0 = time.time()
    n = int(NOMINAL_FS * secs)
    subprocess.run('arecord -D %s -f S16_LE -r %d -c 2 --samples=%d -t raw 2>/dev/null > %s'
                   % (DEV, int(NOMINAL_FS), n, RAW), shell=True, timeout=secs + 180)
    t1 = time.time()
    leg1 = chrony_leg()

    x = np.fromfile(RAW, dtype='<i2').astype(np.float64)
    try:
        os.unlink(RAW)
    except OSError:
        pass
    got = len(x) // 2
    x = x.reshape(-1, 2).mean(axis=1)
    x -= x.mean()

    row = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'seconds_asked': secs,
           'frames_got': got, 'frames_asked': n, 'wall_s': t1 - t0,
           'rms_counts': float(x.std()), 'device': DEV,
           'chrony_leg_before': leg0, 'chrony_leg_after': leg1}
    if got != n:
        row.update(outcome='refused', err='SHORT: asked %d frames got %d' % (n, got))
        print(json.dumps(row)); return 0

    res = {}
    for f0 in LINES:
        r = lockin(x, f0, NOMINAL_FS, 2.0)
        if r is None:
            continue
        A, dt = r
        d = freq_from_phase(A, dt, f0)
        mag = float(np.abs(A).mean())
        d['mag_mean'] = mag
        # local floor: the same lock-in 3-8 Hz off the line, where no harmonic lives
        off = []
        for df in (-8.0, -5.0, -3.0, 3.0, 5.0, 8.0):
            rr = lockin(x, f0 + df, NOMINAL_FS, 2.0)
            if rr:
                off.append(float(np.abs(rr[0]).mean()))
        d['floor_mean'] = float(np.median(off)) if off else None
        d['snr_block'] = (mag / d['floor_mean']) if d['floor_mean'] else None
        res['%g' % f0] = d
    row['lines'] = res

    # ACCEPTANCE 1: the harmonic ratio is forced by arithmetic. No clock involved.
    if '120' in res and '240' in res:
        f1 = res['120']['f_hz_in_codec_units']; f2 = res['240']['f_hz_in_codec_units']
        s1 = res['120']['sem_hz']; s2 = res['240']['sem_hz']
        ratio = f2 / f1
        rsem = ratio * ((s2 / f2) ** 2 + (s1 / f1) ** 2) ** 0.5
        row['harmonic_ratio'] = ratio
        row['harmonic_ratio_sem'] = rsem
        row['harmonic_widths_from_2'] = abs(ratio - 2.0) / rsem if rsem else None

    # ACCEPTANCE 2: block-length and drop sweep on the 120 Hz line
    sweep = {}
    for bs in (1.0, 2.0, 4.0, 8.0):
        r = lockin(x, 120.0, NOMINAL_FS, bs)
        if r:
            d = freq_from_phase(r[0], r[1], 120.0)
            if d:
                sweep['block_%g' % bs] = d['f_hz_in_codec_units']
    r2 = lockin(x, 120.0, NOMINAL_FS, 2.0)
    if r2:
        for k in (0, 2, 5, 10):
            if len(r2[0]) - k >= 10:
                d = freq_from_phase(r2[0][k:], r2[1], 120.0)
                if d:
                    sweep['drop_%d' % k] = d['f_hz_in_codec_units']
    row['sweep_hz'] = sweep
    v = [x for x in sweep.values() if x is not None]
    row['sweep_spread_hz'] = (max(v) - min(v)) if v else None
    row['outcome'] = 'committed'
    print(json.dumps(row))
    return 0


if __name__ == '__main__':
    sys.exit(main())
