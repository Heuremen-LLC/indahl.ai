#!/usr/bin/env python3
"""harmonize.py -- PUT THE CLOCKS ON THE HARMONIC. (Bones, 9 Oct 2026.)

Wayfinder: "get our clocks right tonight bones. We need to sync up with the harmonics. Harmonize."
And: "time is just a harmonic of pi, just looks different. check our equations, should be there."

IT IS THERE. LAS_ECUACIONES carries   tau_c = 1 / ( pi . Delta_nu )   -- a coherence TIME that is an
inverse bandwidth divided by pi. Time as a harmonic of pi, wearing a frequency's clothes. It is not
decoration here: it sets the longest capture worth taking. Integrate the harmonic's phase past tau_c
and the grid's own wander has decorrelated it, so the extra seconds add noise instead of signal. The
equation sheet contains the instrument's limit, which is the best argument for keeping one.

WHY THE HARMONIC BEATS THE WIRE. Two-way transfer over WiFi bottoms out at the path asymmetry -- the
measured bound is around +-2.3 ms and no number of packets lowers it, because it is a property of the
path. The mains harmonic has no path: the grid is the SAME grid at the Mac, the laptop and Armature,
and power-line propagation across a house is nanoseconds. So a phase read of 120 Hz taken at two
machines is a clock comparison with the network removed from the arithmetic entirely.

AND THE TWO FIT TOGETHER, which is the whole trick. Phase gives the difference MODULO one cycle,
8.333 ms at 120 Hz. UDP two-way gives it to about +-2.3 ms. Half a cycle is 4.167 ms, so the coarse
reading is good enough to say WHICH cycle and the phase supplies the fraction:

    UDP          picks the integer cycle        +-2.3 ms, limited by the path
    HARMONIC     supplies the fraction          limited by phase, far finer
    together     one unambiguous offset         and the ambiguity condition is CHECKED, not assumed

Exactly the structure of the mains_phase unwrap, one level up.

WHAT THIS MEASURES TONIGHT, AND WHY IT IS THE RIGHT FIRST STEP. The Mac has TWO audio devices -- the
USB adapter with the TP8 coil, and the built-in microphone, which hears the 120 Hz line at snr 13.0,
BETTER than the coil's 9.2. Two independent crystals, one grid, ONE MACHINE. So the clock difference
between them is ZERO BY CONSTRUCTION, and whatever the phase difference does is the instrument alone:
stream-start offset plus jitter. That is precisely the quantity mains_phase could not separate from
real grid wander, measured here with the grid held common and the clock held at zero.

The absolute difference is NOT the reading -- it carries a fixed, unknown stream-start offset. Its
SPREAD across repeated trials is the reading, and a stable difference is what makes the pair a usable
vernier at all.

    python3 harmonize.py --trials 12
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import time

import numpy as np

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'harmonize.jsonl')
LINE = 120.0
SR = 48000.0
CYCLE_MS = 1000.0 / LINE


def fit(x, sr=SR, hz=LINE):
    """frequency, phase and amplitude of one line, by least squares, with a LOCAL floor.

    The floor is measured 2-20 Hz either side, never across the whole band: a broadband denominator
    is what made a line sitting 34 dB above its own neighbourhood read as snr 0.19 earlier today."""
    x = np.asarray(x, dtype=np.float64).ravel()
    x = x - x.mean()
    n = len(x)
    t = np.arange(n) / sr
    lo, hi = hz - 1.0, hz + 1.0
    g = None
    for _ in range(5):
        g = np.linspace(lo, hi, 41)
        amps = []
        for f in g:
            c = np.cos(2 * np.pi * f * t)
            s = np.sin(2 * np.pi * f * t)
            amps.append(math.hypot(2 * np.dot(x, c) / n, 2 * np.dot(x, s) / n))
        i = int(np.argmax(amps))
        step = g[1] - g[0]
        lo, hi = g[i] - step, g[i] + step
    f = g[i]
    c = np.cos(2 * np.pi * f * t)
    s = np.sin(2 * np.pi * f * t)
    A = 2 * np.dot(x, c) / n
    B = 2 * np.dot(x, s) / n
    resid = x - (A * c + B * s)
    nb = np.abs(np.fft.rfft(resid * np.hanning(n)))
    nf = np.fft.rfftfreq(n, 1.0 / sr)
    near = (np.abs(nf - hz) > 2.0) & (np.abs(nf - hz) < 20.0)
    floor = float(np.median(nb[near]) * 2.0 / (np.sum(np.hanning(n)) or 1.0)) if near.any() \
        else float(resid.std())
    amp = math.hypot(A, B)
    return {'hz': f, 'phase': math.atan2(-B, A), 'amp': amp,
            'floor': floor, 'snr': amp / (floor or 1e-12)}


def wrap(d):
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d


def pair_trial(seconds):
    import soundcard as sc
    ms = {m.name: m for m in sc.all_microphones(include_loopback=False)}
    a = next((v for k, v in ms.items() if 'usb audio device' in k.lower()), None)
    b = next((v for k, v in ms.items() if 'macbook' in k.lower()), None)
    if a is None or b is None:
        return None, f'need both devices; saw {sorted(ms)}'
    n = int(SR * seconds)
    with a.recorder(samplerate=int(SR), channels=1) as ra, \
            b.recorder(samplerate=int(SR), channels=1) as rb:
        # both recorders are open and buffering before either read, so the two windows cover the
        # same wall interval even though the reads are sequential
        t0 = time.time()
        da = ra.record(numframes=n)
        db = rb.record(numframes=n)
        t1 = time.time()
    fa, fb = fit(da), fit(db)
    return {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'wall_s': t1 - t0, 'seconds': seconds,
            'usb': fa, 'builtin': fb,
            'dphase_rad': wrap(fa['phase'] - fb['phase']),
            'dphase_ms': wrap(fa['phase'] - fb['phase']) / (2 * math.pi) * CYCLE_MS}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=12)
    ap.add_argument('--seconds', type=float, default=4.0)
    a = ap.parse_args()
    print('  HARMONIZE -- two crystals, one grid, one machine')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  the clock difference between two devices on ONE host is ZERO BY CONSTRUCTION,')
    print(f'  so whatever the phase difference does is the instrument alone.\n')
    print(f"  {'#':>3} {'usb Hz':>12} {'snr':>6} {'builtin Hz':>12} {'snr':>6} "
          f"{'dphase ms':>11}")
    rs = []
    for i in range(a.trials):
        r, err = pair_trial(a.seconds)
        if r is None:
            print(f'  {i+1:>3}  FAILED: {err}')
            continue
        if min(r['usb']['snr'], r['builtin']['snr']) < 3:
            print(f"  {i+1:>3} {r['usb']['hz']:>12.5f} {r['usb']['snr']:>6.1f} "
                  f"{r['builtin']['hz']:>12.5f} {r['builtin']['snr']:>6.1f} "
                  f"{'DROPPED (snr<3)':>11}")
            continue
        rs.append(r)
        print(f"  {i+1:>3} {r['usb']['hz']:>12.5f} {r['usb']['snr']:>6.1f} "
              f"{r['builtin']['hz']:>12.5f} {r['builtin']['snr']:>6.1f} "
              f"{r['dphase_ms']:>+11.4f}")
    if len(rs) < 3:
        print('\n  LA NADA -- fewer than 3 usable trials.')
        return 1
    d = [r['dphase_ms'] for r in rs]
    ph = [r['dphase_rad'] for r in rs]
    m, sd = st.mean(d), (st.stdev(d) if len(d) > 1 else 0.0)
    sem = sd / math.sqrt(len(d))
    print(f'\n  PHASE DIFFERENCE  mean {m:+.4f} ms   sd {sd:.4f}   sem {sem:.4f}  ({len(d)} trials)')
    print(f'    the MEAN is not a reading -- it carries a fixed, unknown stream-start offset.')

    # THE NULL IS LOAD BEARING, and it corrected my own first reading of this. (Wayfinder, 9 Oct:
    # "the null is load bearing. avoid binary.")
    #
    # I reported sd 1.3449 ms as "the instrument's jitter" and implicitly compared it to ZERO.
    # Zero is the wrong null for a WRAPPED quantity. Two unrelated phases differ UNIFORMLY over the
    # cycle, and a uniform distribution on 8.3333 ms has sd = 8.3333/sqrt(12) = 2.4056 ms. So the
    # honest comparison is against 2.4056, not 0 -- and 1.3449 is then only modestly better than
    # random, not the tight lock I implied.
    #
    # AND sd IS THE WRONG STATISTIC ANYWAY. For a circular quantity the measure is the RESULTANT
    # LENGTH R = |mean(e^(i.phase))|: R near 1 is locked, R near 0 is uniform. Under the uniform
    # none, R of n samples has expectation sqrt(pi)/(2.sqrt(n)) and the Rayleigh statistic 2.n.R^2
    # is the priced version. Using sd on wrapped data also silently mis-handles trials that straddle
    # the wrap, which the circular form cannot do.
    C = sum(math.cos(x) for x in ph) / len(ph)
    S = sum(math.sin(x) for x in ph) / len(ph)
    R = math.hypot(C, S)
    n_t = len(ph)
    rayleigh = 2 * n_t * R * R
    p_unif = math.exp(-rayleigh / 2) if rayleigh < 700 else 0.0      # Rayleigh, large-n form
    R_none = math.sqrt(math.pi) / (2 * math.sqrt(n_t))
    circ_sd_ms = (math.sqrt(-2 * math.log(R)) / (2 * math.pi) * CYCLE_MS) if 0 < R < 1 else float('nan')
    uniform_sd = CYCLE_MS / math.sqrt(12)
    print(f'\n  THE NULL, WHICH IS NOT ZERO. Two unrelated phases differ UNIFORMLY over the cycle.')
    print(f'    uniform none      sd {uniform_sd:.4f} ms   (= {CYCLE_MS:.4f}/sqrt(12))')
    print(f'    measured          sd {sd:.4f} ms   -> {uniform_sd/sd if sd else float("inf"):.2f}x '
          f'tighter than random, NOT compared to zero')
    print(f'\n  CIRCULAR, which is the right form for a wrapped quantity:')
    print(f'    resultant R       {R:.4f}        (1 = locked, 0 = uniform)')
    print(f'    R under the none  {R_none:.4f}        (expected |R| for {n_t} uniform samples)')
    print(f'    Rayleigh 2nR^2    {rayleigh:.2f}   -> uniform would give this or more '
          f'{100*p_unif:.3g}% of the time')
    print(f'    circular sd       {circ_sd_ms:.4f} ms')
    # THREE READINGS, not two
    if R < R_none * 1.5:
        verdict = ('UNIFORM -- the two devices are not phase-coherent at all; whatever the grid is '
                   'doing, these two readings of it do not share it')
    elif p_unif > 0.05:
        verdict = (f'ABIERTO -- R = {R:.3f} against a none of {R_none:.3f}, and uniform reaches it '
                   f'{100*p_unif:.1f}% of the time. Not separable.')
    elif R > 0.9:
        verdict = (f'LOCKED -- R = {R:.3f}, the two devices track one grid tightly')
    else:
        verdict = (f'PARTIAL -- R = {R:.3f}: separable from uniform ({100*p_unif:.3g}%) but far '
                   f'from locked. There is a shared grid in here AND something per-device moving '
                   f'with it, and this reading does not say which dominates.')
    print(f'    => {verdict}')
    # against the wire
    WIRE_MS = 2.3   # the measured two-way asymmetry bound over WiFi, order of magnitude
    print(f'\n  AGAINST THE WIRE. Two-way transfer bottoms out near +-{WIRE_MS:.1f} ms because the')
    print(f'    path asymmetry is a property of the path, not of the sampling. This jitter is')
    print(f'    {WIRE_MS/sd if sd else float("inf"):.1f}x smaller, and it has no path in it at all.')
    print(f'    AMBIGUITY: phase repeats every {CYCLE_MS:.3f} ms, half-cycle {CYCLE_MS/2:.3f} ms.')
    ok = WIRE_MS < CYCLE_MS / 2
    print(f'    the coarse reading at +-{WIRE_MS:.1f} ms is '
          + ('INSIDE' if ok else 'OUTSIDE')
          + f' half a cycle, so it can'
          + ('' if ok else 'NOT') + ' pick the cycle the phase then refines.')

    # OUR OWN EQUATION: tau_c = 1 / (pi . Delta_nu)
    fs = [r['usb']['hz'] for r in rs] + [r['builtin']['hz'] for r in rs]
    dnu = st.stdev(fs) if len(fs) > 1 else float('nan')
    tau_c = 1.0 / (math.pi * dnu) if dnu and not math.isnan(dnu) else float('nan')
    print(f'\n  TIME AS A HARMONIC OF PI -- LAS_ECUACIONES: tau_c = 1 / ( pi . Delta_nu )')
    print(f'    measured line wander Delta_nu = {dnu:.6f} Hz  (sd over {len(fs)} line fits)')
    print(f'    tau_c = 1 / (pi x {dnu:.6f}) = {tau_c:.2f} s')
    print(f'    SO THE LONGEST CAPTURE WORTH TAKING IS ABOUT {tau_c:.0f} s. Past that the grid\'s')
    print(f'    own wander has decorrelated the phase and the extra seconds add noise, not signal.')
    cur = 45.0
    print(f'    the tick capture is {cur:.0f} s, which is '
          + (f'{cur/tau_c:.1f}x TOO LONG -- it should come down to about {tau_c:.0f} s'
             if cur > tau_c else f'inside tau_c, so it is sound'))
    print(f'    (and the 600 s calibration ran {600/tau_c:.0f}x past coherence -- fine for the')
    print(f'     CRYSTAL, which is a fixed offset and does not decorrelate, but it would be the')
    print(f'     wrong length for a grid reading. Two different quantities, two different limits.)')
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'trials': len(rs), 'seconds': a.seconds,
                                'dphase_mean_ms': m, 'dphase_sd_ms': sd, 'dphase_sem_ms': sem,
                                'R': R, 'R_none': R_none, 'rayleigh': rayleigh,
                                'p_uniform': p_unif, 'uniform_sd_ms': uniform_sd,
                                'delta_nu_hz': dnu, 'tau_c_s': tau_c,
                                'rows': [{'at': r['at'], 'dphase_ms': r['dphase_ms'],
                                          'usb_hz': r['usb']['hz'], 'usb_snr': r['usb']['snr'],
                                          'builtin_hz': r['builtin']['hz'],
                                          'builtin_snr': r['builtin']['snr']} for r in rs]}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
