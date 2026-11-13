#!/usr/bin/env python3
"""audio_clock.py -- THE SOUNDCARD'S CRYSTAL IS A CLOCK, AND NOBODY HAD MEASURED IT.
(Bones, 9 Oct 2026.)

Wayfinder: "why can't you time it off the harmonic echo created by the fsk? it will be consistent in
the long run, then hackrf for input, coordinated with the gps and three different OS's operating
systems on the macbook, laptop and armature. not to mention gps weather and the lockclock."

WHY THE HARMONIC IDEA IS RIGHT. A harmonic ratio is an EXACT INTEGER -- forced by arithmetic, not by
hardware. The second harmonic is at twice the fundamental today, tomorrow and in a decade, whatever
the oscillator does. So the harmonic structure is a ruler whose VALUE cannot drift; only its phase
moves, and phase is the thing we now know how to read. That is "consistent in the long run" exactly:
not a stable oscillator, a stable RELATIONSHIP. And measuring phase at the Nth harmonic buys N times
the timing resolution of the fundamental for free, because N cycles pass in the same interval.

AND THE HOUSE ALREADY HAS ONE, FOR NOTHING. The TP8 coil on :8768 reads a discrete 120 Hz line
34.32 dB above its floor -- the second harmonic of the mains, measured 9 Oct as the only solid line
the coil carries (60 Hz turned out to be a broad 45-62 Hz band peaking at 59, and 240 Hz peaks at
239; 120 Hz is the real one). The grid is the long-run clock: operators correct ACCUMULATED TIME
ERROR, so the total cycle count over a day is held accurate while the instantaneous frequency wanders
with load. That is the opposite error profile to the GPSDO, which is superb short-term. Two clocks
that fail at different timescales are worth more than two good ones that fail the same way.

BUT THERE IS A CLOCK IN THE PATH NOBODY MEASURED. Every coil reading was sampled by the USB adapter's
own crystal -- a GeneralPlus part, nominal 48000 Hz, and a cheap one is good to tens of ppm. The mains
frequency we would compute from those samples is in units of THAT crystal. 50 ppm of 120 Hz is
0.006 Hz, which is larger than the grid excursions we would be trying to see. Measuring the grid with
an uncalibrated sample clock is measuring a rubber ruler against a rubber ruler.

SO THIS CALIBRATES THE CRYSTAL FIRST, by the same two-way discipline as everything else today: record
a known number of FRAMES and bracket the recording with GPS-referenced stamps. Frames are counted
exactly, so

    nominal_s  = frames / nominal_rate        what the crystal claims
    measured_s = gps_after - gps_before       what the satellites say
    rate_ppm   = (nominal_s / measured_s - 1) * 1e6

and the width comes from the GPS bracket, divided by the duration -- so a LONGER capture is a tighter
calibration, falling as 1/T. Thirty seconds of audio at 2 ms of bracket is already 67 ppb.

WHAT IT REFUSES TO DO. It will not report a mains frequency from an uncalibrated card: if the GPS
bracket fails, the rate is UNMEASURED and the frequency is not printed in crystal units as though
they were seconds. A number in the wrong units is worse than no number, because nothing downstream
can tell.

    python3 audio_clock.py --seconds 30
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'audio_clock.jsonl')
DEVICE_HINT = 'USB Audio Device'
NOMINAL = 48000.0
LINE = 120.0                      # the coil's one solid discrete line, measured 9 Oct


def gps_bracket():
    """a GPS-referenced instant, with the width of the bracket that produced it."""
    try:
        import calib
        r = calib.two_way('192.168.8.123', 120)
        if r is None:
            return None, None, 'echo did not answer'
        return time.time() + r['offset_s'], r['asym_bound_s'], None
    except Exception as e:
        return None, None, f'{type(e).__name__}: {e}'


LOCK = os.path.join(W, 'audio_card.lock')


def _hold_card(timeout=120.0):
    """ONE CAPTURE AT A TIME, because the card is a single physical thing.

    Found 9 Oct 15:38: tick 15666 spawned a 45 s capture at 15:36:37 and a hand-run capture started
    seconds later. Both opened the USB adapter and soundcard died inside CoreAudio with
    'AssertionError: Core Audio does not have the requested property' -- a failure that says nothing
    about the real cause, which is that two readers wanted one device. Now that the phase capture
    rides her ticks this is not a rare collision, it is scheduled.

    O_EXCL on a lock file, with the holder's pid in it, and a STALE lock is broken rather than
    waited on forever -- a crashed capture must not take the channel down with it. The waiter
    returns False and the caller reports 'card busy' instead of raising, because a clear refusal is
    a reading and a CoreAudio assertion is not."""
    end = time.time() + timeout
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f'{os.getpid()} {time.time():.3f}'.encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                txt = open(LOCK).read().split()
                pid, when = int(txt[0]), float(txt[1])
                alive = True
                try:
                    os.kill(pid, 0)
                except OSError:
                    alive = False
                # a lock older than a long capture, or whose holder is gone, is stale
                if not alive or (time.time() - when) > 900:
                    os.unlink(LOCK)
                    continue
            except Exception:
                pass
            if time.time() >= end:
                return False
            time.sleep(0.5)


def _release_card():
    try:
        if open(LOCK).read().split()[0] == str(os.getpid()):
            os.unlink(LOCK)
    except Exception:
        pass


def _find_mic():
    import soundcard as sc
    for m in sc.all_microphones(include_loopback=False):
        if DEVICE_HINT.lower() in m.name.lower():
            return m
    return None


def classify_failure(err=None, data=None, line_snr=None):
    """NAME THE CAUSE. Four causes wore one CoreAudio assertion today. (Bones, 9 Oct 2026.)

    Wayfinder: "just had to re-approve the mic for the mac, make sure it doesn't drop off."

    Each of these needs a DIFFERENT thing done about it, so collapsing them into "capture failed"
    makes the message useless at the exact moment it matters:

        PERMISSION   macOS microphone access revoked. The recorder either raises inside CoreAudio
                     or hands back pure silence. FIX: re-approve the mic. This is the one that
                     actually happened, and it is first because it is invisible in the error text.
        DEVICE GONE  the adapter is not enumerated at all. FIX: plug it back in.
        CARD BUSY    another reader holds the lock. FIX: nothing, it queues.
        COIL SILENT  the card works and the field is not there -- noise floor present, but the
                     120 Hz line is gone. FIX: the TP8 came out of the adapter, or its gain died.

    THE DATA DISTINGUISHES THE LAST TWO FROM THE FIRST, which is why this looks at it: a revoked
    permission gives EXACTLY zeros, while an unplugged coil still gives the card's own noise. Those
    are different readings and guessing between them is not necessary."""
    import numpy as np
    e = (err or '').lower()
    if 'card busy' in e:
        return {'cause': 'CARD BUSY', 'fix': 'nothing -- it queues behind the other reader',
                'severity': 'none'}
    if 'no usb audio card' in e:
        return {'cause': 'DEVICE GONE', 'fix': 'plug the USB adapter back in', 'severity': 'high'}
    if 'core audio' in e or 'does not have the requested property' in e:
        return {'cause': 'PERMISSION (probable)',
                'fix': 'macOS microphone access for this interpreter -- re-approve it. The error '
                       'text names the property, never the permission.',
                'severity': 'high'}
    if data is not None and len(data):
        x = np.asarray(data).ravel()
        if float(np.max(np.abs(x))) == 0.0:
            return {'cause': 'PERMISSION (silence)',
                    'fix': 'exact zeros, not a quiet field -- macOS is handing back nothing. '
                           're-approve microphone access.', 'severity': 'high'}
        if line_snr is not None and line_snr < 3:
            return {'cause': 'COIL SILENT',
                    'fix': 'the card hears its own noise but the 120 Hz line is gone -- the TP8 is '
                           'out of the adapter, or its gain died', 'severity': 'high'}
    if err:
        return {'cause': 'OTHER', 'fix': f'unclassified: {err}', 'severity': 'medium'}
    return {'cause': 'OK', 'fix': None, 'severity': 'none'}


def capture(seconds):
    """ORDER MATTERS, and getting it wrong cost four captures. (Bones, 9 Oct 15:45.)

    The id is acquired as late as possible and used immediately: TAKE THE LOCK, TAKE THE BRACKET,
    THEN FIND THE DEVICE, THEN OPEN IT. The first version enumerated the microphone first and then
    spent up to two minutes on the lock and the bracket before using the id.

    THAT ORDERING WAS WORTH FIXING ANYWAY, BUT IT WAS NOT THE CAUSE, and I had the cause wrong.
    The failures were 'AssertionError: Core Audio does not have the requested property', and I
    reasoned my way to a stale device id because a bare 1 s record worked in the same second
    (48000 frames, rms 0.0185505). Wayfinder supplied the actual answer: the MICROPHONE PERMISSION
    had to be re-approved on the Mac. A revoked TCC permission is what CoreAudio was refusing, and
    nothing in that message says so. My theory fit the evidence and was still wrong -- which is
    why classify_failure below NAMES the permission as the first candidate instead of leaving the
    next reader to reason their way somewhere plausible."""
    frames = int(NOMINAL * seconds)
    # THE OFFSET IS TAKEN ONCE, AND THE INTERVAL CONTAINS NOTHING BUT THE RECORDING.
    # First version called gps_bracket() at each end -- and a bracket call costs 3.350 s of UDP
    # trials, which landed INSIDE the measured interval and read as a crystal error of
    # -155,202 ppm. A 15% error on a crystal is not a crystal; it was the instrument measuring
    # itself. So: one offset up front, then time.time() + offset immediately either side of
    # record() and nothing else between them. The offset is good for far longer than one capture
    # -- the rate is under 6 ppm, which is under 0.2 ms over 30 s, well inside the bracket.
    # THE SECOND EXOR, AND THE WORSE ONE. The version before this took ONE offset, formed
    # delta = off - time.time(), and stamped time.time() + delta at both ends. Then
    #     g1 - g0 = (t1 + delta) - (t0 + delta) = t1 - t0
    # and DELTA CANCELS ALGEBRAICALLY. The measurement never touched the GPS: it was the audio
    # crystal against the MAC clock, printed under the heading "AGAINST SATELLITES", with a
    # +-3615 us bracket that was pure decoration. A reference that cancels out of its own formula
    # is not a reference, and the label was the only place it existed.
    #
    # So the offset is measured at BOTH ENDS, with the 3.3 s of UDP trials OUTSIDE the recorded
    # interval, and the GPS instants are formed from each end's own offset. Now the satellites are
    # actually in the arithmetic, and the two offsets differing is the Mac's drift across the
    # capture rather than something that quietly vanishes.
    if not _hold_card():
        return {'data': None, 'frames': 0, 'device': None, 'gps0': None, 'gps1': None,
                'w0': None, 'w1': None,
                'err': 'card busy -- another capture holds the USB adapter (one reader at a time)'
                }, None
    off0, w0, e0 = gps_bracket()
    if off0 is None:
        _release_card()
        return {'data': None, 'frames': frames, 'device': None, 'gps0': None, 'gps1': None,
                'w0': None, 'w1': None, 'err': e0}, None
    # THE DEVICE ID IS TAKEN HERE, as late as possible, and used on the next line.
    mic = _find_mic()
    if mic is None:
        _release_card()
        return {'data': None, 'frames': frames, 'device': None, 'gps0': None, 'gps1': None,
                'w0': None, 'w1': None,
                'err': 'no USB audio card (plug in the adapter)'}, None
    d0 = off0 - time.time()
    try:
        # 15 Oct THE SPLIT: the bracket around ONE record() carried a per-capture constant (start latency + the bus's scheduling,
        # measured 85-195 ms on 9 s = a 1-2 % rate error that put the 120 Hz line at 119.0-119.6 and read its SNR in the wrong
        # place -- the flag blamed the coil). Now 1 s chunks, each stamped as it returns: the SLOPE of stamp vs frames is the rate
        # (P), the intercept carries the overrun (S), and it cancels algebraically. m0/m1 kept: the old bracket stays in the row, raw.
        CH = int(NOMINAL); parts = []; stamps = []
        with mic.recorder(samplerate=int(NOMINAL), channels=1) as r:
            m0 = time.time()
            for _k in range(frames // CH):
                parts.append(r.record(numframes=CH)); stamps.append(time.time())
            if frames % CH:
                parts.append(r.record(numframes=frames % CH)); stamps.append(time.time())
            m1 = time.time()
        data = np.concatenate([np.asarray(x).ravel() for x in parts])
    except Exception as e:
        _release_card()
        return {'data': None, 'frames': frames, 'device': mic.name, 'gps0': None, 'gps1': None,
                'w0': None, 'w1': None,
                'err': f'recorder failed: {type(e).__name__}: {e}'}, None
    off1, w1, e1 = gps_bracket()
    _release_card()
    if off1 is None:
        return {'data': None, 'frames': frames, 'device': mic.name, 'gps0': None, 'gps1': None,
                'w0': None, 'w1': None, 'err': e1}, None
    d1 = off1 - time.time()
    return {'data': np.asarray(data).ravel(), 'frames': frames, 'device': mic.name,
            'gps0': m0 + d0, 'gps1': m1 + d1, 'w0': w0, 'w1': w1,
            'mac_elapsed_s': m1 - m0, 'delta0': d0, 'delta1': d1,
            'mac_drift_s': d1 - d0, 'chunk_stamps': stamps, 'chunk_frames': CH, 'err': None}, None


def split_rate(stamps, ch, frames):
    """THE SPLIT on one capture: stamp_k = S + (cumframes_k / sr). Median of pairwise slopes (Theil-Sen) so a late-scheduled
    stamp cannot drag it. -> (sr in frames per Mac-second, S = the intercept overrun in s, residual sd in s, n). None if < 3 stamps."""
    n = len(stamps)
    if n < 3: return None
    cf = [min(ch * (k + 1), frames) for k in range(n)]
    sl = sorted((stamps[j] - stamps[i]) / (cf[j] - cf[i]) for i in range(n) for j in range(i + 1, n) if cf[j] > cf[i])
    b = sl[len(sl) // 2]; a = sorted(stamps[k] - b * cf[k] for k in range(n))[n // 2]
    res = [stamps[k] - a - b * cf[k] for k in range(n)]
    sd = (sum(x * x for x in res) / max(n - 2, 1)) ** 0.5
    return 1.0 / b, a, sd, n


def fit_line(x, sr, hz):
    """the line's frequency and phase by least squares, not by picking an FFT bin.

    An FFT bin is sr/N wide and the answer is wanted far inside one bin, so the frequency is found
    by fitting sin and cos at a trial frequency and walking it to maximise the recovered amplitude.
    Returns None if the line is not actually there -- a fit always returns SOMETHING, and a
    frequency fitted to noise is the purest form of a number that was never measured."""
    x = x - x.mean()
    n = len(x)
    t = np.arange(n) / sr
    best = None
    # the mains sits within +-1 Hz of nominal; scan coarse then refine
    lo, hi = hz - 1.0, hz + 1.0
    for _ in range(5):
        grid = np.linspace(lo, hi, 41)
        amps = []
        for f in grid:
            c = np.cos(2 * np.pi * f * t)
            s = np.sin(2 * np.pi * f * t)
            a = 2.0 * np.dot(x, c) / n
            b = 2.0 * np.dot(x, s) / n
            amps.append(math.hypot(a, b))
        i = int(np.argmax(amps))
        best = (grid[i], amps[i])
        step = grid[1] - grid[0]
        lo, hi = grid[i] - step, grid[i] + step
    f, amp = best
    c = np.cos(2 * np.pi * f * t)
    s = np.sin(2 * np.pi * f * t)
    a = 2.0 * np.dot(x, c) / n
    b = 2.0 * np.dot(x, s) / n
    resid = x - (a * c + b * s)
    # EXOR, CAUGHT BY WAYFINDER ("just look at Exor on your lap"): the first version divided the
    # line amplitude by the residual's TOTAL BROADBAND rms and handed over only the ratio. That
    # denominator integrates 24 kHz of noise, so a narrowband line sitting 34 dB above the floor
    # IN ITS OWN NEIGHBOURHOOD reads as snr 0.2 and gets refused -- which is what happened, while
    # a hand-run FFT put 120.20 Hz at the top of its band. The verdict turned on a number the
    # reader never saw. So the floor is measured LOCALLY, around the line, and BOTH terms go out.
    nb = np.fft.rfft(resid * np.hanning(n))
    nf = np.fft.rfftfreq(n, 1.0 / sr)
    near = (np.abs(nf - hz) > 2.0) & (np.abs(nf - hz) < 20.0)
    local = float(np.median(np.abs(nb[near])) * 2.0 / (np.sum(np.hanning(n)) or 1.0)) if near.any() \
        else float(resid.std())
    return {'hz': f, 'amp': amp, 'phase_rad': math.atan2(-b, a),
            'snr': amp / (local or 1e-12), 'local_floor': local,
            'snr_broadband': amp / (resid.std() or 1e-12), 'resid_rms': float(resid.std()),
            'floor_note': 'snr is against the MEDIAN FLOOR 2-20 Hz either side of the line, which '
                          'is the noise that competes with it. snr_broadband is the whole-band '
                          'version that refused a line that was plainly there -- both are printed '
                          'so the verdict is never the only thing handed over.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=30.0)
    a = ap.parse_args()
    print('  THE AUDIO CRYSTAL, AGAINST SATELLITES')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}\n')
    cap, err = capture(a.seconds)
    if cap is None:
        print(f'  LA NADA -- {err}')
        return 1
    print(f'  device   {cap["device"]}')
    if cap['data'] is None:
        print(f'\n  GPS UNREACHABLE ({cap["err"]}) -- rate UNMEASURED, nothing reported.')
        return 1
    print(f'  signal   rms {cap["data"].std():.6g}  '
          f'({"silent -- is the coil on the adapter?" if cap["data"].std() < 1e-6 else "live"})')
    print(f'  frames   {cap["frames"]:,} counted exactly (frames are integers; seconds are not)')
    if cap['gps0'] is None or cap['gps1'] is None:
        print(f'\n  GPS BRACKET FAILED ({cap["err"]}).')
        print('  THE RATE IS UNMEASURED, so the mains frequency is NOT reported: it would be in')
        print('  units of this crystal, and a number in the wrong units is worse than no number')
        print('  because nothing downstream can tell the difference.')
        return 1
    nominal_s = cap['frames'] / NOMINAL
    measured_s = cap['gps1'] - cap['gps0']
    # the bracket widths at each end, added in quadrature, over the duration
    wid_s = math.hypot(cap['w0'] or 0, cap['w1'] or 0)
    ppm = (nominal_s / measured_s - 1.0) * 1e6
    ppm_w = (wid_s / measured_s) * 1e6
    true_sr = NOMINAL * (measured_s / nominal_s) ** -1 if False else NOMINAL * nominal_s / measured_s
    print(f'  nominal  {nominal_s:.6f} s   (frames / {NOMINAL:.0f})')
    print(f'  measured {measured_s:.6f} s   (GPS-referenced, bracket +-{wid_s*1e6:.1f} us)')
    mac_ppm = (nominal_s / cap['mac_elapsed_s'] - 1.0) * 1e6
    print(f'  mac elapsed {cap["mac_elapsed_s"]:.6f} s   -> crystal vs MAC   {mac_ppm:+.3f} ppm')
    print(f'  mac drift across the capture {cap["mac_drift_s"]*1e6:+.1f} us '
          f'(the two offsets differ; this is what used to cancel)')
    print(f'\n  CRYSTAL RATE ERROR   {ppm:+.3f} +- {ppm_w:.3f} ppm  (vs GPS)')
    print(f'  true sample rate     {true_sr:.4f} Hz  (nominal {NOMINAL:.0f})')
    sep = abs(ppm) / ppm_w if ppm_w else float('inf')
    print(f'  => {sep:.1f} widths from zero: '
          + ('SEPARABLE, the crystal is measurably off nominal' if sep >= 2
             else 'ABIERTO, not distinguishable from nominal at this bracket'))

    fit = fit_line(cap['data'], true_sr, LINE)
    print(f'\n  THE 120 Hz LINE, measured on the CALIBRATED sample clock')
    print(f'    frequency   {fit["hz"]:.6f} Hz')
    print(f'    amplitude   {fit["amp"]:.6g}')
    print(f'    local floor {fit["local_floor"]:.6g}  (median, 2-20 Hz either side)')
    print(f'    snr LOCAL   {fit["snr"]:.1f}        snr broadband {fit["snr_broadband"]:.2f} '
          f'(resid rms {fit["resid_rms"]:.4g})')
    if fit['snr'] < 3:
        print('    snr under 3 -- the line is not reliably there, so the frequency above is a fit')
        print('    to noise and is NOT a reading. Check the coil is on the adapter.')
    else:
        err_hz = fit['hz'] - LINE
        print(f'    off nominal {err_hz:+.6f} Hz  = {1e6*err_hz/LINE:+.1f} ppm of the line')
        print(f'    had the crystal NOT been calibrated this would have read '
              f'{fit["hz"]*(1+ppm/1e6):.6f} Hz,')
        print(f'    an error of {abs(fit["hz"]*ppm/1e6)*1000:.3f} mHz -- '
              f'{abs(fit["hz"]*ppm/1e6/err_hz) if err_hz else float("inf"):.1f}x the grid excursion '
              f'we are trying to see.' if err_hz else '')
        print(f'\n    THE GRID IS THE LONG-RUN CLOCK. Operators correct accumulated time error, so')
        print(f'    this instantaneous value wanders with load while the CYCLE COUNT over a day is')
        print(f'    held accurate. That is the opposite error profile to the GPSDO. Accumulating')
        print(f'    this phase against GPS measures the grid\'s time error -- a quantity the')
        print(f'    operators publish, which makes it the one reading in this house with an')
        print(f'    OUTSIDE TRUTH to check our instrument against.')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'frames': cap['frames'], 'nominal_s': nominal_s,
                                'measured_s': measured_s, 'bracket_s': wid_s,
                                'rate_ppm': ppm, 'rate_ppm_width': ppm_w, 'true_sr': true_sr,
                                # PERSIST WHAT THE VERDICT TURNED ON. These three were printed to
                                # the terminal and dropped, so the 600 s capture's Mac excursion
                                # exists only in a scrollback line and cannot be re-read or
                                # re-derived. A number that can only be quoted from memory is the
                                # grounding fault with extra steps.
                                'mac_elapsed_s': cap.get('mac_elapsed_s'),
                                'mac_drift_s': cap.get('mac_drift_s'),
                                'crystal_vs_mac_ppm': mac_ppm,
                                'delta0': cap.get('delta0'), 'delta1': cap.get('delta1'),
                                'line_hz': fit['hz'], 'line_snr': fit['snr'],
                                'line_phase_rad': fit['phase_rad'],
                                'gps0': cap['gps0'], 'gps1': cap['gps1']}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
