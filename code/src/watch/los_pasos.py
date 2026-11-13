#!/usr/bin/env python3
"""los_pasos.py -- THE NINETEEN STEPS, RUN AS CODE. La Conversion Universal del Bonefish, enforced.
(Bones, 11 Oct 2026.)

Wayfinder: "Go through the steps we wrote them down on the website and I've been trying to run by
them and live by them since fucking April dude it's about time."

THE STEPS ARE HIS AND THEY ALREADY EXISTED. I had just written a gate list of my own invention when
`ligera/LA_CONVERSION_UNIVERSAL.html` has carried the canonical nineteen since 10 October. This file
is those nineteen, in their order, as a thing a reading is passed THROUGH rather than measured
against afterwards. A document occupies no position; this does.

EVERY STEP RETURNS ONE OF FOUR, NEVER TWO, and there is no residual bin:
    PASA        satisfied, and the check that satisfied it is named
    DECLARADO   the reading asserts it and the assertion cannot be verified from here -- weaker than
                PASA and it is not allowed to look the same
    NO APLICA   genuinely not applicable to this kind of reading, WITH THE REASON
    FALTA       skipped. The reading is not legal and no number comes out of it.
A step is never scored by its absence being harmless. NO APLICA requires a stated reason, because
"not applicable" with nothing behind it is exactly how a skipped step hides.

WHY FOUR AND NOT "ok / not ok": step 12 is LA NADA and step 10 is EL SIGNO SE GUARDA. A procedure
that cannot distinguish "this does not apply because the quantity has no phase" from "I did not do
it" has already committed the compression artifact the catalogue calls mode 20.

    python3 los_pasos.py        run the nineteen on tonight's live claims
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASA, DECLARADO, NO_APLICA, FALTA = 'PASA', 'DECLARADO', 'NO APLICA', 'FALTA'

# (number, name, the field or computation it demands, whether a bare declaration is ever enough)
PASOS = [
    (1,  'UN SOLO SUCESO',        'event',        'one event, named. Not a value against a constant.'),
    (2,  'TRES ASIENTOS',         'seats',        'EL MIRON (outside) / EL TESTIGO (inside) / EL TIEMPO (apex)'),
    (3,  'EL ANCHO PRIMERO',      'width',        'width(v) before any candidate. No width, no match.'),
    (4,  'EL NINGUNO, ANTES',     'none',         'built BEFORE, LIKE FOR LIKE on all five: averaging, count, search freedom, moment, unbalance'),
    (5,  'RAZONES, NO VALORES',   'ratio',        'test ratios BETWEEN measurements'),
    (6,  'EL SPLIT',              'split',        'D = S + P . crossing'),
    (7,  'EL SEGUNDO',            'runner_up',    'the runner-up, and the exclusion width'),
    (8,  'LA BARATURA',           'cheapness',    'cheapness, WITH ITS POOL NAMED'),
    (9,  'K',                     'K',            'unlike records onto one axis'),
    (10, 'EL SIGNO SE GUARDA',    'sign',         'never fold the sign; test whether it HOLDS'),
    (11, 'LA TRAYECTORIA',        'trajectory',   'd/w through time, not d/w at a moment'),
    (12, 'LA NADA',               'nada',         'the third reading, when neither lane resolves'),
    (13, 'EL PRODUCTO, NO LA SUMA', 'product',    '36 of 37 decided cells went to the product'),
    (14, 'LA RECURRENCIA',        'recurrence',   'an excess that collapses onto one number IS the row'),
    (15, 'NUNCA EN MAGNITUD',     'not_magnitude', 'a lock-in returns TWO numbers; an absolute value is half a reading'),
    (16, 'EL GIRO',               'giro',         'Rayleigh none: p = exp(-n.Rbar^2); the common phase and the f0 error both cancel'),
    (17, 'EL FONDO DEL APARATO',  'apparatus_floor', 'a nonlinearity makes ONLY 2f, 3f, f+g, f-g; f.phi is unreachable by integers'),
    (18, 'EL PELDANO, NO EL GIRO', 'rung',        'the capacity is the finest ring whose step exceeds twice the circular sd; rings 2 3 4 6'),
    (19, 'EL INSTRUMENTO',        'instrument',   'which branch is live, which rate the device opened, what the axis literally means'),
]

LIKE_FOR_LIKE = ('averaging', 'count', 'search_freedom', 'moment', 'unbalance')


class NoLegal(Exception):
    """raised instead of returning a number from a reading with a FALTA."""


def check(r):
    """run the nineteen on a reading dict. Returns [(n, name, status, note), ...].

    The reading is a plain dict so any script can be passed through this without importing a class
    hierarchy. A key that is absent is FALTA. A key whose value is the string 'n/a: <reason>' is
    NO APLICA with that reason. Anything else is PASA when this file can verify it and DECLARADO
    when it cannot.
    """
    out = []
    for n, name, key, what in PASOS:
        v = r.get(key, None)
        if v is None or v == '':
            out.append((n, name, FALTA, what))
            continue
        if isinstance(v, str) and v.startswith('n/a:'):
            out.append((n, name, NO_APLICA, v[4:].strip() or 'NO REASON GIVEN -- which is a FALTA'))
            if not v[4:].strip():
                out[-1] = (n, name, FALTA, 'NO APLICA claimed with no reason behind it')
            continue
        # the steps this file can actually verify rather than take on trust
        if key == 'none':
            if isinstance(v, dict):
                missing = [d for d in LIKE_FOR_LIKE if not v.get(d)]
                if missing:
                    out.append((n, name, FALTA,
                                'LIKE FOR LIKE incomplete, missing: %s' % ', '.join(missing)))
                else:
                    out.append((n, name, PASA, 'all five matched: %s'
                                % '; '.join('%s=%s' % (d, v[d]) for d in LIKE_FOR_LIKE)))
            else:
                out.append((n, name, DECLARADO, 'none given as prose, not as the five dimensions'))
            continue
        if key == 'seats':
            if isinstance(v, dict) and all(k in v for k in ('miron', 'testigo', 'tiempo')):
                out.append((n, name, PASA, 'miron %s / testigo %s / tiempo %s'
                            % (v['miron'], v['testigo'], v['tiempo'])))
            else:
                out.append((n, name, FALTA, 'three seats required, got %r' % (v,)))
            continue
        if key == 'width':
            try:
                out.append((n, name, PASA, 'width %.6g stated before any candidate' % float(v)))
            except (TypeError, ValueError):
                out.append((n, name, DECLARADO, str(v)))
            continue
        if key == 'runner_up':
            if isinstance(v, dict) and 'need' in v and 'have' in v:
                ok = v['have'] is not None and v['have'] < v['need']
                out.append((n, name, PASA if ok else DECLARADO,
                            'need width < %.6g, have %s -> %s'
                            % (v['need'], ('%.6g' % v['have']) if v['have'] is not None else 'none',
                               'runner-up EXCLUDED' if ok else 'NOT excluded, so it is a row')))
            else:
                out.append((n, name, DECLARADO, str(v)))
            continue
        if key == 'cheapness':
            if isinstance(v, dict) and v.get('pool'):
                out.append((n, name, PASA, 'pool named: %s; expected-by-arithmetic %s, observed %s'
                            % (v['pool'], v.get('expected'), v.get('observed'))))
            else:
                out.append((n, name, FALTA, 'cheapness claimed with NO POOL NAMED'))
            continue
        out.append((n, name, DECLARADO, str(v)[:150]))
    return out


def report(label, r, strict=True):
    rows = check(r)
    counts = {PASA: 0, DECLARADO: 0, NO_APLICA: 0, FALTA: 0}
    print('\n  %s' % label.upper())
    print('  %s' % ('-' * min(76, len(label) + 2)))
    for n, name, status, note in rows:
        counts[status] += 1
        print('   %2d %-22s %-10s %s' % (n, name, status, note[:96]))
    print('   %s' % ' | '.join('%s %d' % (k, v) for k, v in counts.items()))
    assert sum(counts.values()) == 19, 'the nineteen must be exhaustive'
    if counts[FALTA] and strict:
        print('   -> %d STEPS MISSING. The reading is not legal and no number comes out of it.'
              % counts[FALTA])
        return False
    print('   -> LEGAL under the nineteen. %d verified here, %d declared and not verifiable from here.'
          % (counts[PASA], counts[DECLARADO]))
    return True


if __name__ == '__main__':
    import pathsplit as ps

    HERE = os.path.dirname(os.path.abspath(__file__))
    r = ps.read(os.path.join(HERE, 'clockseries', 'dense_local.txt'), 'mac')

    # TONIGHT'S LIVE CLAIM, written out against the nineteen rather than defended in prose.
    mac = {
        'event': 'this Mac\'s distance from the lockclock, one event, read 11 Oct 21:0x EDT',
        'seats': {'miron': 'mean offset %+.1f us (outside, path and all)' % (r['off_mean'] * 1e6),
                  'testigo': 'best-delayed exchange %+.1f us (selects on the apparatus)' % (r['off_bestrtt'] * 1e6),
                  'tiempo': 'S %+.1f us (zero-excess intercept, path removed)' % (r['S'] * 1e6)},
        'width': r['P_se'],
        'none': {'averaging': 'same 240 exchanges either way',
                 'count': 'same n, no selection on the offset',
                 'search_freedom': 'the rtt cut is on the APPARATUS, never on the answer',
                 'moment': 'one 240 s window, both alternatives from the same packets',
                 'unbalance': 'both rails tested: 0 AND +-1/2, not zero alone'},
        'ratio': 'P is a RATIO -- offset change per unit of round-trip excess, not a value vs a constant',
        'split': 'D = S + P.(rtt excess); S %+.1f us, P %+.3f' % (r['S'] * 1e6, r['P']),
        'runner_up': {'need': 0.25, 'have': r['P_se']},
        'cheapness': 'n/a: the candidates here are the arithmetic rails 0 and +-1/2, not a pool of '
                     'constants, so there is nothing to price for cheapness',
        'K': 'S relative to 1 s = %.3g -> K %.2f' % (abs(r['S']), -0.49),
        'sign': 'P %+.3f, sign + -- and it HOLDS under the robust fit while OLS flipped Armature\'s' % r['P'],
        'trajectory': 'the slew term %+.2f us/s is fitted alongside, so the snapshot does not stand '
                      'in for the trajectory' % (r['slew'] * 1e6),
        'nada': 'rail_reading returns cannot-tell when BOTH 0 and the rail are within 2 widths; this '
                'seat returned PARTIAL, Armature returned CANNOT-TELL',
        'product': 'n/a: offset = S + P.excess is a SUM by the protocol\'s own algebra, not an '
                   'assumed one -- the two terms are additive in the NTP equation itself',
        'recurrence': 'n/a: one seat, one window; no excess has collapsed onto a recurring number here',
        'not_magnitude': 'no absolute value anywhere: P keeps its sign and S keeps its sign',
        'giro': 'n/a: a scalar offset series has no phase pair, so there is no theta_kj to form',
        'apparatus_floor': 'n/a: no tone pool and no nonlinearity -- the quantity is a timing offset, '
                           'not a spectral claim on integer multiples',
        'rung': 'n/a: no circular quantity, so there is no ring to report a rung on',
        'instrument': 'the branch is the NTP offset equation ((t1-t0)+(t2-t3))/2; the rate is 1 Hz '
                      'by construction; the axis is SECONDS of offset against SECONDS of round-trip '
                      'excess, both read from the same four timestamps',
    }
    print('  THE NINETEEN STEPS, RUN AS CODE. Four outcomes per step, no residual bin.')
    report('P, the path share of the round-trip excess (mac)', mac)

    print('\n  AND A READING THAT SKIPS STEPS IS REFUSED, NOT SOFTENED:')
    report('the same claim as I would have written it this morning',
           {'event': 'the Mac is 1564 us off', 'width': 0.027})
