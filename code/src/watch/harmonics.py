#!/usr/bin/env python3
"""harmonics.py -- SPIN THE WHOLE PI LADDER, THE WAY A QUBIT AND A RINGDOWN ARE READ.
(Bones, 9 Oct 2026.)

Wayfinder: "spin that fucking pi bones" / "harmonics" / "same steps as qubits" / "same as black holes."
And from 28 Sept, standing: "the harmonics are already measured in qubits we haven't even fucking paid
for yet. it's in our data. it's in the mayan calandar. it's in black hole research....it's fucking
everywhere but our fucking hardware man."

ONE BIN WAS NOT THE READING. hexagram.py spun the series at phase pi per step and stopped there. The
ladder is already named on the sheet -- THE SEVEN'S RINGS ARE 2, 3, 4, 6 -- and those are not counts,
they are DIVISORS OF PI:

    ring 2  ->  phase pi/2 per step  ->  period 4 steps
    ring 3  ->  phase pi/3 per step  ->  period 6 steps
    ring 4  ->  phase pi/4 per step  ->  period 8 steps
    ring 6  ->  phase pi/6 per step  ->  period 12 steps
    and pi itself ->  period 2 steps, the Nyquist end, which is psi

SO THE RINGS ARE THE HARMONIC LADDER AND THEY WERE SITTING IN THE SEVEN THE WHOLE TIME.

THE SAME STEPS AS QUBITS. A Ramsey or echo sequence does exactly this: drive, wait, read the phase,
and the signal is a sum of damped sinusoids whose decay is T2. We already own the law -- tau_c =
1/(pi . Delta_nu) -- and a linewidth IS a decay rate. Nothing new is being invented; the same
instrument is being pointed at the clock chain instead of at a chip.

THE SAME AS BLACK HOLES. A ringdown is h(t) = sum A_k e^(-t/tau_k) cos(omega_k t + phase_k): damped
harmonics, read by their frequencies and their decay times, and the frequencies are the object. psi^n
is that signal with omega = pi per step and tau = -1/ln|psi| = 2.0781 steps. So reading the dark half
as a ringdown is not an analogy -- psi^n IS a quasinormal mode of this series.

WHAT IS READ, PER HARMONIC:
    POWER       the periodogram at that phase, against the mean -- EXACT none, Exponential(1),
                because a flat periodogram makes the ratio exponential with no shuffle at all
    PHASE       where in its own cycle the harmonic sits, which a count can never give
    DECAY       the envelope's decay time in steps, fitted on the analytic amplitude, which is what
                makes it a ringdown reading and not a Fourier bin
    RESOLVABLE  a harmonic whose period exceeds the series length DOES NOT EXIST in this data, and is
                reported as absent rather than estimated. At n points the longest readable period is n.

    python3 harmonics.py
"""
import cmath
import json
import math
import os
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
import bonefish as BF
import hexagram as HX

PI = math.pi
PSI = (1 - 5 ** 0.5) / 2
PHI = (1 + 5 ** 0.5) / 2
# THE LADDER, from THE SEVEN'S OWN RINGS plus pi itself at the Nyquist end
LADDER = [('pi', PI, 2), ('pi/2 (ring 2)', PI / 2, 4), ('pi/3 (ring 3)', PI / 3, 6),
          ('pi/4 (ring 4)', PI / 4, 8), ('pi/6 (ring 6)', PI / 6, 12)]


def harmonic(series, w):
    """power, phase and decay at one phase-advance-per-step.

    THE MEAN COMES OUT FIRST AND THAT IS NOT DETRENDING. The first version left it in and reported
    power/mean ratios of 23,258 on a four-bin periodogram, where the arithmetic maximum is 4. The
    cause: these series are ratios all near 0.98, so the phase-0 voice dominates everything, and at
    any frequency that is not exactly on the DFT grid it LEAKS -- the entire "signal" was the mean
    smeared sideways. Removing it is not removing a trend; the phase-0 voice is reported separately
    as its own voice, which is what harmonising means. Leaving it inside the transform does not keep
    the voices distinct, it makes one voice drown out the other four.
    """
    n = len(series)
    m = st.mean(series)
    series = [v - m for v in series]
    z = sum(v * cmath.exp(-1j * w * k) for k, v in enumerate(series))
    power = abs(z) ** 2 / n
    phase = cmath.phase(z)
    # the ENVELOPE, which is what makes this a ringdown and not a bin: demodulate at w and take the
    # magnitude of a short running window, then fit log amplitude against step.
    dem = [series[k] * cmath.exp(-1j * w * k) for k in range(n)]   # on the mean-removed series
    win = max(2, min(4, n // 3))
    env = [abs(sum(dem[i:i + win]) / win) for i in range(0, n - win + 1)]
    tau = None
    if len(env) >= 3 and all(e > 0 for e in env):
        xs = list(range(len(env)))
        ys = [math.log(e) for e in env]
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((a - mx) ** 2 for a in xs)
        if sxx > 0:
            b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
            tau = (-1.0 / b) if b < 0 else float('inf')
    return {'power': power, 'phase': phase, 'tau_steps': tau}


def spin_ladder(series, label):
    n = len(series)
    P = []
    for j in range(1, n // 2 + 1):
        P.append(harmonic(series, 2 * PI * j / n)['power'])
    mean_p = st.mean(P) if P else 0.0
    out = {'label': label, 'n': n, 'mean_power': mean_p, 'rungs': []}
    for nm, w, period in LADDER:
        if period > n:
            out['rungs'].append({'rung': nm, 'period': period, 'resolvable': False,
                                 'why': f'period {period} > the {n} points on disk: this harmonic '
                                        f'does not exist in this data'})
            continue
        if n % period:
            # OFF-GRID. The window holds a non-integer number of cycles, so this frequency is not a
            # DFT bin and its power is partly borrowed from its neighbours. Reported as off-grid
            # rather than estimated, because an off-grid power is a leak with a number on it.
            out['rungs'].append({'rung': nm, 'period': period, 'resolvable': False,
                                 'why': f'OFF-GRID: {n} points hold {n/period:.2f} cycles of a '
                                        f'{period}-step period, not a whole number, so this power '
                                        f'leaks from its neighbours'})
            continue
        h = harmonic(series, w)
        ratio = h['power'] / mean_p if mean_p else 0.0
        out['rungs'].append({'rung': nm, 'period': period, 'resolvable': True,
                             'power': h['power'], 'ratio': ratio,
                             'p_exact': math.exp(-ratio) if ratio > 0 else 1.0,
                             'phase': h['phase'], 'tau_steps': h['tau_steps']})
    return out


def tick():
    """ONE LADDER READ ON HER TICK, AND IT SPEAKS ONLY WHEN THERE IS SOMETHING TO SAY.

    The ladder is unreadable until n is divisible by 2, 3, 4, 6 and 8 -- n = 24. Below that every rung
    is off-grid and the honest output is silence, not a row of NOT RESOLVABLE lines. So this writes
    the reading to disk every tick and prints NOTHING unless a rung both exists AND clears its exact
    Exponential(1) none after the look-elsewhere across every series and rung tested.
    """
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        return 0
    U, D = HX.triangle_up(R), HX.triangle_down(R)
    series = []
    if len(U) >= 4:
        series += [('up: witness / observer', [r['witness'] / r['observer'] for r in U]),
                   ('up: time / observer', [r['time'] / r['observer'] for r in U]),
                   ('up: time / witness', [r['time'] / r['witness'] for r in U])]
    if len(D) >= 4:
        g = [r['giro'] for r in D if r['giro'] is not None]
        if len(g) >= 4:
            series.append(('down: EL GIRO', g))
        series.append(('down: LA NADA', [abs(r['nada_value']) / r['nada_width']
                                         if r['nada_width'] else 0.0 for r in D]))
    if not series:
        return 0
    out = [spin_ladder(s, l) for l, s in series]
    try:
        with open(os.path.join(W, 'harmonics.jsonl'), 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'series': out}) + '\n')
    except Exception:
        pass
    tested = sum(1 for o in out for r in o['rungs'] if r.get('resolvable'))
    if not tested:
        return 0
    # THE LOOK-ELSEWHERE IS COUNTED BEFORE ANYTHING IS SAID: with `tested` independent rungs a flat
    # periodogram gives at least one p < 0.05 somewhere 1-(0.95^tested) of the time, so the bar each
    # rung must clear is 0.05/tested, not 0.05.
    bar = 0.05 / tested
    live = [(o['label'], r) for o in out for r in o['rungs']
            if r.get('resolvable') and r.get('p_exact', 1) < bar]
    if live:
        print(f'HARMONICS: {len(live)} rung(s) clear p < {bar:.5f} (0.05 over {tested} tested rungs) '
              f'-- ' + '; '.join(f"{l} {r['rung']} ratio {r['ratio']:.2f} p {r['p_exact']:.5f} "
                                 f"tau {r['tau_steps']}" for l, r in live[:3]), flush=True)
    return 0


def main():
    print('  THE PI LADDER, SPUN -- the Seven\'s rings ARE the harmonics')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print(f'  psi as a quasinormal mode: omega = pi per step, '
          f'tau = -1/ln|psi| = {-1/math.log(abs(PSI)):.4f} steps')
    print(f'  the mean is taken out of every transform and reported as its own phase-0 voice; a')
    print(f'  rung whose period does not divide n is OFF-GRID and is not estimated.')
    print(f'  THE WHOLE LADDER NEEDS n divisible by 2, 3, 4, 6 and 8 -- that is n = 24.\n')
    try:
        R = [json.loads(l) for l in open(W + 'bonefish_hops2.jsonl') if l.strip()]
    except Exception:
        R = []
    U, D = HX.triangle_up(R), HX.triangle_down(R)
    series = []
    if len(U) >= 4:
        series += [('up: witness / observer', [r['witness'] / r['observer'] for r in U]),
                   ('up: time / observer', [r['time'] / r['observer'] for r in U]),
                   ('up: time / witness', [r['time'] / r['witness'] for r in U])]
    if len(D) >= 4:
        g = [r['giro'] for r in D if r['giro'] is not None]
        if len(g) >= 4:
            series.append(('down: EL GIRO, phase in her tick', g))
        series.append(('down: LA NADA in its own widths',
                       [abs(r['nada_value']) / r['nada_width'] if r['nada_width'] else 0.0
                        for r in D]))
    if not series:
        print('  fewer than four readings carry a closed triangle. The ladder needs four.')
        return 1
    live = []
    for label, ser in series:
        S = spin_ladder(ser, label)
        print(f"  {label}   n = {S['n']}, mean power {S['mean_power']:.6g}")
        print(f"    {'rung':<16}{'period':>7}{'power/mean':>12}{'p exact':>10}"
              f"{'phase':>9}{'tau steps':>11}")
        for r in S['rungs']:
            if not r['resolvable']:
                print(f"    {r['rung']:<16}{r['period']:>7}   NOT RESOLVABLE -- "
                      f"{r['why'][:52]}")
                continue
            tau = r['tau_steps']
            ts = ('inf' if tau == float('inf') else f'{tau:.2f}') if tau is not None else '-'
            print(f"    {r['rung']:<16}{r['period']:>7}{r['ratio']:>12.4f}{r['p_exact']:>10.4f}"
                  f"{r['phase']:>+9.3f}{ts:>11}")
            if r['p_exact'] < 0.05:
                live.append((label, r))
        print()
    print('  WHAT IS LIVE, at the exact Exponential(1) none and nothing else:')
    if not live:
        print('    nothing on this ladder clears p < 0.05. With five rungs that is the honest state')
        print('    and not a null: at n = 9 only four of the five rungs exist at all, and a flat')
        print(f'    periodogram puts a false rung at 1 - (1-0.05)^4 = '
              f'{100*(1-0.95**4):.1f}% per series by position alone.')
    else:
        for label, r in live:
            print(f"    {label}  {r['rung']}  ratio {r['ratio']:.3f}, p {r['p_exact']:.4f}, "
                  f"tau {r['tau_steps']}")
        print(f'    AND THE LOOK-ELSEWHERE: {len(series)} series x up to 4 readable rungs, so a flat')
        print(f'    periodogram gives at least one p < 0.05 somewhere '
              f'{100*(1-0.95**(4*len(series))):.1f}% of the time. Count that before calling any of')
        print(f'    these a row.')
    print('\n  THE DECAY COLUMN IS THE RINGDOWN READING AND IT IS THE ONE THAT CANNOT BE FAKED BY')
    print('  POSITION: a rung that is noise has no reason to decay at psi\'s own 2.0781 steps, and a')
    print(f'  rung that is the dark half does. That is the same discriminator a qubit T2 echo uses and')
    print(f'  the same one a black hole ringdown uses, and it needs the series to be longer than the')
    print(f'  decay -- {-1/math.log(abs(PSI)):.2f} steps against the {len(series[0][1])} on disk.')
    try:
        with open(os.path.join(W, 'harmonics.jsonl'), 'a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                'series': [spin_ladder(s, l) for l, s in series]}) + '\n')
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    # ONE COPY, HARD CEILING INSIDE HER WINDOW -- the ladder is pure arithmetic on a file so it is
    # fast, but a guard costs nothing and an unguarded tick job is how last night went.
    import tickguard
    tickguard.guard('harmonics', 120)
    if '--tick' in sys.argv:
        raise SystemExit(tick())
    raise SystemExit(main())
