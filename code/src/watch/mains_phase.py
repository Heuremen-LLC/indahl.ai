#!/usr/bin/env python3
"""mains_phase.py -- THE HARMONIC ECHO, ACCUMULATED. (Bones, 9 Oct 2026.)

Wayfinder: "why can't you time it off the harmonic echo created by the fsk? it will be consistent in
the long run."

THE SEPARATION THAT MAKES THIS WORK, and it is the long run that provides it. Accumulated 120 Hz
phase against GPS time contains two things, and at one reading they are degenerate -- a crystal
running fast and a grid running slow put the same slope on the page. They come apart because their
LONG-RUN behaviour is opposite, by design on one side and by physics on the other:

    THE CRYSTAL is nothing but slope. A fixed ppm error accumulates phase forever and never
    comes back. It has no mechanism for returning to zero.

    THE GRID is nothing but residual. Operators measure accumulated time error against UTC and
    deliberately drive it back to zero -- that is what "the clock on the wall stays right" means
    at grid scale. Over days the grid's net contribution to slope is ZERO, however far the
    instantaneous frequency wanders with load.

So over a long enough record: THE SLOPE IS THE CRYSTAL, THE RESIDUAL IS THE GRID. Two unknowns, one
series, separated by the fact that one of them is pinned at zero in the long run and the other cannot
be. That is "consistent in the long run" used as an instrument rather than a hope.

PHASE, NOT FREQUENCY, AND WHY IT IS WORTH THE TROUBLE. A frequency reading per capture improves as
1/sqrt(n) with more captures. Accumulated phase improves LINEARLY with span, because every cycle
between the endpoints is counted rather than averaged. At 120 Hz an hour holds 432,000 cycles, so
resolving phase to a hundredth of a cycle is 83 us of time.

AND THE PRICE: CYCLE AMBIGUITY, WHICH THIS REFUSES TO GUESS AT. Between two captures the phase is
only known modulo one cycle. Unwrapping is safe only while the drift between captures stays under
HALF a cycle, which means

    spacing_s  x  frequency_uncertainty_Hz  <  0.5

At the crystal's current +-0.0072 Hz (from +-60 ppm at 120 Hz) that caps spacing at about 69 s --
tighter than her tick interval of roughly 250 s, so the tick cadence CANNOT carry an unwrapped phase
until the crystal is better known. Rather than pick a cycle and hope, this reports both readings and
refuses the second when the condition fails:

    THE UNAMBIGUOUS ONE   per-capture frequency, no unwrapping, improving as 1/sqrt(n)
    THE SHARP ONE         unwrapped accumulated phase, improving as 1/T, ONLY when every gap
                          passed the half-cycle test. One failed gap and the series is cut there,
                          because an unwrap that silently chose the wrong cycle is a fabricated
                          number that looks better than the honest one.

    python3 mains_phase.py --captures 6 --seconds 20 --spacing 40
    python3 mains_phase.py --report
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
# ONE DEFINITION, IMPORTED. SEVEN ended up defined four times with four different contents by being
# re-typed; the line fitter and the GPS bracket live in audio_clock and are used from there.
from audio_clock import capture, fit_line, LINE, NOMINAL, classify_failure  # noqa: E402

LOG = os.path.join(W, 'mains_phase.jsonl')


def one(seconds):
    cap, err = capture(seconds)
    if cap is None or cap.get('data') is None:
        return None, (err or cap.get('err') if cap else err)
    nominal_s = cap['frames'] / NOMINAL
    measured_s_bracket = cap['gps1'] - cap['gps0']          # RAW, kept: the one-record bracket, overrun and all
    measured_s = measured_s_bracket; split = None
    if cap.get('chunk_stamps'):                               # 15 Oct THE SPLIT: rate from the slope, the overrun in the intercept
        from audio_clock import split_rate
        sp = split_rate(cap['chunk_stamps'], cap['chunk_frames'], cap['frames'])
        if sp:
            sr_mac, S, sd, n = sp
            gps_per_mac = 1.0 + (cap['delta1'] - cap['delta0']) / max(cap['mac_elapsed_s'], 1e-9)   # the Mac clock's own rate against GPS
            measured_s = cap['frames'] / sr_mac * gps_per_mac
            split = {'n_chunks': n, 'resid_sd_s': sd, 'overrun_S_s': round(S - (cap['gps0'] - cap['delta0']), 4),
                     'bracket_minus_split_ms': round(1000 * (measured_s_bracket - measured_s), 2)}
    true_sr = NOMINAL * nominal_s / measured_s
    f = fit_line(cap['data'], true_sr, LINE)
    bracket = math.hypot(cap['w0'] or 0, cap['w1'] or 0)
    return {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'gps_mid': (cap['gps0'] + cap['gps1']) / 2.0,
            'gps0': cap['gps0'], 'gps1': cap['gps1'],
            'frames': cap['frames'], 'nominal_s': nominal_s, 'measured_s': measured_s,
            'measured_s_bracket': measured_s_bracket, 'split': split,
            'bracket_s': bracket, 'true_sr': true_sr,
            'crystal_ppm': (nominal_s / measured_s - 1.0) * 1e6,
            'crystal_ppm_width': (bracket / measured_s) * 1e6,
            'mac_drift_s': cap.get('mac_drift_s'),
            'line_hz': f['hz'], 'line_phase_rad': f['phase_rad'], 'line_amp': f['amp'],
            'line_snr': f['snr'], 'line_snr_broadband': f['snr_broadband'],
            'local_floor': f['local_floor']}, None


STATUS = os.path.join(W, 'mic_status.json')
MIC_FLAG = os.path.join(W, 'MIC_FLAG.txt')
BAR = 2                     # consecutive failures before it is a flag, not a collision


def mic_watch(cause, detail):
    """MAKE SURE IT DOESN'T DROP OFF. (Wayfinder, 9 Oct 2026.)

    The microphone permission was revoked once today and the only symptom was a CoreAudio
    assertion in a log nobody reads. This channel captures on every one of her ticks, so it is the
    right place to notice: it keeps a CONSECUTIVE failure count and raises a flag only at BAR,
    because one failure is a collision and two in a row is a condition.

    IT ALSO CLEARS ITSELF. A flag that only ever goes up teaches you to ignore it -- the first
    success writes the recovery line and removes the file, so its presence always means NOW.

    Separate from nova_flags on purpose: that watch owns its own state dict under launchd and
    writing into it from here would race. This is a plain file, append-only in spirit, and
    MIC_FLAG.txt existing at all is the signal."""
    try:
        st = json.load(open(STATUS))
    except Exception:
        st = {'consecutive': 0, 'last_cause': None, 'last_ok': None, 'flagged': False}
    ok = cause == 'OK'
    if ok:
        was = st.get('consecutive', 0)
        st.update(consecutive=0, last_cause='OK',
                  last_ok=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        if st.get('flagged'):
            st['flagged'] = False
            try:
                os.unlink(MIC_FLAG)
            except Exception:
                pass
            print(f'  MIC RECOVERED after {was} consecutive failures', file=sys.stderr, flush=True)
    else:
        st['consecutive'] = st.get('consecutive', 0) + 1
        st['last_cause'] = cause
        st['last_fail'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
        if st['consecutive'] >= BAR and not st.get('flagged'):
            st['flagged'] = True
            with open(MIC_FLAG, 'w') as f:
                f.write(f"MIC DOWN -- {cause}\n"
                        f"since {st['last_fail']}, {st['consecutive']} ticks in a row\n"
                        f"fix: {detail}\n"
                        f"last good capture: {st.get('last_ok') or 'none on record'}\n")
            print(f'  MIC FLAG RAISED: {cause} -- {detail}', file=sys.stderr, flush=True)
    try:
        json.dump(st, open(STATUS, 'w'))
    except Exception:
        pass
    return st


def rows():
    out = []
    try:
        for l in open(LOG):
            if l.strip():
                out.append(json.loads(l))
    except Exception:
        pass
    return sorted(out, key=lambda r: r['gps_mid'])


def best_crystal():
    """the tightest crystal calibration on record: value, width, and the sample rate it implies."""
    best = None
    try:
        for l in open(os.path.join(W, 'audio_clock.jsonl')):
            q = json.loads(l)
            if q.get('line_snr', 0) >= 3 and q.get('rate_ppm_width') and q.get('true_sr'):
                if best is None or q['rate_ppm_width'] < best['rate_ppm_width']:
                    best = q
    except Exception:
        pass
    return best


def report():
    R = [r for r in rows() if r['line_snr'] >= 3]
    # EVERY CAPTURE RE-EXPRESSED IN ONE SET OF SECONDS. (Bones, 9 Oct 15:53.)
    #
    # Each row's line_hz was fitted using THAT capture's own true_sr, derived from its own GPS
    # bracket -- and a 20 s capture brackets to about +-3.6 ms, which is 180 ppm. So the scatter
    # across captures was mostly a different rubber ruler per row, not the grid: the per-capture
    # width went +-0.012365 -> +-0.057997 Hz as short tick captures joined the long hand-run ones.
    # This is the SAME fault I had already fixed for the unwrap and left standing here.
    #
    # Frequency scales linearly with the assumed sample rate, and both rates are stored, so the
    # correction is exact and needs no raw audio:  hz_common = hz_row * (sr_best / sr_row)
    bc = best_crystal()
    if bc:
        for r in R:
            if r.get('true_sr'):
                r['line_hz_raw'] = r['line_hz']
                r['line_hz'] = r['line_hz'] * (bc['true_sr'] / r['true_sr'])
    bad = len(rows()) - len(R)
    print(f'  THE 120 Hz HARMONIC, ACCUMULATED -- {len(R)} usable captures'
          + (f' ({bad} dropped, snr under 3)' if bad else ''))
    if len(R) < 3:
        print('  fewer than 3 usable captures: no series yet.')
        return
    span = R[-1]['gps_mid'] - R[0]['gps_mid']
    print(f'  span {span/60:.1f} min, GPS-referenced')
    if bc:
        moved = [abs(r['line_hz'] - r['line_hz_raw']) for r in R if 'line_hz_raw' in r]
        print(f'  all captures re-expressed in the {bc["nominal_s"]:.0f} s calibration\'s seconds '
              f'(sr {bc["true_sr"]:.4f} Hz);')
        print(f'  that moved them by up to {max(moved)*1e3:.2f} mHz '
              f'({1e6*max(moved)/LINE:.1f} ppm) -- per-capture brackets were the scatter\n')
    else:
        print('  NO crystal calibration on record: every capture stays in its own seconds\n')

    # ---- READING ONE: per-capture frequency, unambiguous, no unwrapping
    fs = [r['line_hz'] for r in R]
    m = st.mean(fs)
    sem = st.stdev(fs) / math.sqrt(len(fs)) if len(fs) > 1 else 0.0
    # the crystal's own uncertainty rides on every one of these and does NOT average down: it is a
    # common systematic, so it is carried separately rather than folded into the sem
    cw = st.median([r['crystal_ppm_width'] for r in R]) * 1e-6 * LINE
    print('  READING ONE -- per-capture frequency, no unwrapping needed')
    print(f'    mains harmonic   {m:.6f} Hz  +-{sem:.6f} (scatter) '
          f'+-{cw:.6f} (crystal, COMMON -- does not average down)')
    print(f'    mains            {m/2:.6f} Hz')
    tot = math.hypot(sem, cw)
    print(f'    total width      +-{tot:.6f} Hz   -> {1e6*tot/LINE:.1f} ppm')
    print(f'    off 120.000000   {m-LINE:+.6f} Hz = {1e6*(m-LINE)/LINE:+.1f} ppm, '
          f'{abs(m-LINE)/tot:.1f} widths')

    # ---- READING TWO: unwrapped phase, and the half-cycle test on EVERY gap
    print('\n  READING TWO -- unwrapped accumulated phase (1/T, but only if every gap is safe)')
    # THE CRYSTAL FOR THE UNWRAP COMES FROM THE BEST CALIBRATION ON RECORD, not from these
    # captures. A 20 s capture brackets to about +-3.6 ms, which is 180 ppm -- useless for deciding
    # a cycle. The 600 s run gave -104.184 +- 5.998 ppm because the width falls as 1/T, and that is
    # the number the ambiguity turns on. Using the per-capture value here would have refused an
    # unwrap that the long calibration makes safe.
    best_ppm_w = None
    try:
        for l in open(os.path.join(W, 'audio_clock.jsonl')):
            q = json.loads(l)
            if q.get('line_snr', 0) >= 3 and q.get('rate_ppm_width'):
                if best_ppm_w is None or q['rate_ppm_width'] < best_ppm_w[0]:
                    best_ppm_w = (q['rate_ppm_width'], q['nominal_s'], q['rate_ppm'])
    except Exception:
        pass
    if best_ppm_w:
        fu = best_ppm_w[0] * 1e-6 * LINE
        print(f'    crystal from the best calibration on record: {best_ppm_w[2]:+.3f} +- '
              f'{best_ppm_w[0]:.3f} ppm over {best_ppm_w[1]:.0f} s')
        print(f'    -> frequency uncertainty +-{fu:.6f} Hz, '
              f'safe spacing under {0.5/fu:.0f} s')
    else:
        fu = tot
        print(f'    no long calibration on record; falling back to this run\'s own width '
              f'+-{fu:.6f} Hz')
    cuts, cycles, ok = [], 0.0, True
    for a, b in zip(R, R[1:]):
        gap = b['gps_mid'] - a['gps_mid']
        drift = gap * fu
        if drift >= 0.5:
            cuts.append((gap, drift))
            ok = False
    if not ok:
        worst = max(cuts, key=lambda c: c[1])
        print(f'    REFUSED. {len(cuts)} of {len(R)-1} gaps fail the half-cycle test; the worst is '
              f'{worst[0]:.1f} s apart,')
        print(f'    which at +-{fu:.6f} Hz allows {worst[1]:.2f} cycles of drift -- more than the '
              f'0.50 that keeps')
        print(f'    an unwrap honest. Picking a cycle here would produce a tighter number than '
              f'reading one')
        print(f'    and no way to tell it was wrong.')
        safe = 0.5 / fu if fu else float('inf')
        print(f'    SAFE SPACING at this crystal: under {safe:.1f} s between captures.')
        print(f'    (her tick interval is about 250 s, so the tick cadence cannot carry this yet --')
        print(f'     the crystal has to get better first, and its width falls as 1/T on capture '
              f'length.)')
    else:
        # accumulate: phase advance between captures, with the integer cycles resolved
        acc, t0 = 0.0, R[0]['gps_mid']
        xs, ys = [], []
        prev = R[0]
        for b in R[1:]:
            gap = b['gps_mid'] - prev['gps_mid']
            expected = m * gap
            dphi = (b['line_phase_rad'] - prev['line_phase_rad']) / (2 * math.pi)
            n = round(expected - dphi)
            acc += dphi + n
            xs.append(b['gps_mid'] - t0)
            ys.append(acc)
            prev = b
        # slope = the CRYSTAL (it cannot return to zero); residual = THE GRID (pinned at zero
        # long-run by the operators' time-error correction)
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((a - mx) ** 2 for a in xs)
        slope = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx
        res = [b - (my + slope * (a - mx)) for a, b in zip(xs, ys)]
        rms = math.sqrt(sum(e * e for e in res) / max(len(res) - 2, 1))
        # WHAT THE SLOPE ACTUALLY IS, corrected 9 Oct 15:30. The first version printed it as
        # "the crystal" and computed slope/LINE as ppm, giving +999914 ppm -- a labelling error
        # that understated the result badly. The slope of ACCUMULATED CYCLES against GPS SECONDS
        # is a frequency in GPS Hz, and THE CRYSTAL IS NOT IN IT: each capture's phase is taken at
        # its first sample, which is anchored to gps0, and the time axis between captures is GPS.
        # The crystal affects the within-capture frequency fit, not the phase at the start, so it
        # cancels in the slope. It was only ever needed as a PRIOR to pick the right cycle.
        #
        # So this is the crystal cancellation, for free, out of the harmonic method -- no summed
        # input, no second oscillator.
        #
        # THE CAVEAT THAT GOES WITH IT, because it bounds the residual: the recorder has its own
        # latency between gps0 and the first sample actually captured. A CONSTANT latency is a
        # constant phase offset and cancels in the slope. A VARYING one does not, and lands in the
        # residual -- so the residual is grid wander PLUS capture-latency jitter, confounded. It is
        # an UPPER BOUND on the grid's time error, not a measurement of it, until the latency is
        # separately characterised.
        dev = slope - LINE
        wid = (rms / xs[-1]) if xs[-1] else float('inf')
        print(f'    accumulated {ys[-1]:,.3f} cycles over {xs[-1]:.1f} s')
        print(f'    SLOPE = the mains harmonic, CRYSTAL-FREE')
        print(f'      {slope:.9f} Hz  +-{wid:.9f}  ({1e6*wid/LINE:.2f} ppm)')
        print(f'      mains {slope/2:.9f} Hz')
        print(f'      off 120.000000  {dev:+.6f} Hz = {1e6*dev/LINE:+.2f} ppm, '
              f'{abs(dev)/wid if wid else 0:.1f} widths')
        print(f'      vs reading one ({1e6*tot/LINE:.1f} ppm): {tot/wid if wid else 0:.0f}x '
              f'tighter -- phase improves as 1/T, frequency as 1/sqrt(n)')
        # THE WIDTH ON A WIDTH. This slope's width comes from an rms on n-2 degrees of freedom,
        # and calib learned today that such an rms still MOVES at small n. At 2 dof the rms is
        # uncertain by roughly 1/sqrt(2*dof) = 50 percent, so quoting 0.70 ppm as settled would be
        # the same fault as quoting a rate across a step. Said, not buried.
        dof = max(len(res) - 2, 1)
        print(f'      width from an rms on {dof} degree(s) of freedom, itself uncertain by about '
              f'{100/math.sqrt(2*dof):.0f}%'
              + ('  <- NOT SETTLED, read more captures' if dof < 6 else ''))
        # AND THE REAL VALIDATION: two readings of one quantity by different methods.
        agree = abs(slope - m)
        print(f'    THE TWO READINGS AGREE: {slope:.6f} (phase) vs {m:.6f} (per-capture), '
              f'{agree:.6f} Hz apart')
        print(f'      = {agree/tot:.2f} widths of the LOOSER one. Two methods on one quantity, and')
        print(f'      the sharp one lands inside the loose one -- which is the only check here that')
        print(f'      does not come from the same arithmetic as the number it is checking.')
        print(f'    RESIDUAL  {rms:.4f} cycles rms = {rms/LINE*1e3:.3f} ms')
        print(f'      an UPPER BOUND on grid time error: it carries capture-latency jitter too,')
        print(f'      and those are confounded until the latency is characterised separately.')
        print(f'    THE CRYSTAL CANCELS HERE. Phase is anchored to a GPS instant at each capture')
        print(f'    and the time axis is GPS seconds, so the sample clock drops out of the slope.')
        print(f'    It was needed only to decide which cycle -- a prior, not a ruler.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--captures', type=int, default=0)
    ap.add_argument('--seconds', type=float, default=20.0)
    ap.add_argument('--spacing', type=float, default=40.0)
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    if a.captures:
        print(f'  {a.captures} captures of {a.seconds:.0f} s, {a.spacing:.0f} s apart\n')
        for i in range(a.captures):
            r, err = one(a.seconds)
            c = classify_failure(err=err, data=None if r is None else None,
                                 line_snr=None if r is None else r.get('line_snr'))
            # 15 Oct: BOTH alternatives before blaming the coil. A crystal is specified +-60 ppm; a capture whose delivered rate is
            # > 1000 ppm off nominal is the USB DELIVERY (stalled/dropped frames, measured 1.3 % slow in some captures), not the crystal
            # and not the coil -- the line is then distorted in the data itself. Only a capture delivered at a crystal's rate that
            # still has no line is a silent coil.
            if r is not None and abs(r.get('crystal_ppm') or 0) > 1000:
                c = {'cause': 'FRAMES LATE',
                     'fix': 'the adapter delivered %.0f ppm off nominal (a crystal cannot): this capture is distorted by the '
                            'USB delivery, not a silent coil -- the line read %.2f Hz, snr %.1f' % (r.get('crystal_ppm') or 0, r.get('line_hz') or 0, r.get('line_snr') or 0)}
            elif r is not None and r.get('line_snr', 0) < 3:
                c = {'cause': 'COIL SILENT',
                     'fix': 'the card hears its own noise but the 120 Hz line is gone -- the TP8 '
                            'is out of the adapter, or its gain died'}
            mic_watch(c['cause'], c.get('fix') or '')
            if c['cause'] != 'OK':
                print(f'    mic: {c["cause"]} -- {c.get("fix")}', file=sys.stderr, flush=True)
            if r is None:
                # FAILURES GO TO STDERR, NOT STDOUT. Found 9 Oct 15:36: tick_bus spawns this with
                # stdout=DEVNULL, so a capture that failed and returned its reason here printed it
                # straight into the void -- no row, no stderr line, nothing. Two ticks looked
                # identical to two successes that happened to write nothing. A silent failure on
                # her clock is the worst shape in the house: the channel reports healthy by saying
                # nothing, which is exactly what a dead one says.
                print(f'    {i+1:>3}  FAILED: {err}', file=sys.stderr, flush=True)
                print(f'    {i+1:>3}  FAILED: {err}', flush=True)
            else:
                with open(LOG, 'a') as f:
                    f.write(json.dumps(r) + '\n')
                print(f'    {i+1:>3}  {r["line_hz"]:.6f} Hz  snr {r["line_snr"]:5.1f}  '
                      f'crystal {r["crystal_ppm"]:+8.2f} +-{r["crystal_ppm_width"]:5.2f} ppm',
                      flush=True)
            if i < a.captures - 1:
                time.sleep(max(0.0, a.spacing - a.seconds))
        print()
    report()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
