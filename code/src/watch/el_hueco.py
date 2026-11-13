#!/usr/bin/env python3
"""el_hueco.py -- THE TAU-SIZED HOLE, read as a GAP and never as a constant to find.

THE CANON, declared 27 July 2026 in 6 Plus None / The Spooky 7 and NOT applied here until 12 Oct:

    "TAU is not a constant to find in nature. It is the SIZE OF THE GAP between two positions on
     the same object." The unit is whatever separates the two observers -- dB, days, percent,
     substrate, method. "Do not try to prove tau again; it is proved. LOOK FOR THE TAU-SIZED HOLE."

So this never fits tau, never searches for 6.28 in a spectrum, and never scores a match. It takes
every object in this house that is READ FROM TWO SEATS, states the gap in that object's own unit,
and says whether the gap can be told from 6 and from tau AT ALL.

WHY THAT LAST CLAUSE IS THE WHOLE TOOL. 6 and tau are 0.283 apart. To separate them a gap must be
known to better than half that -- 0.1416 absolute, 2.36 % of 6 -- and almost nothing in this house
is. A reading that lands at 6.1 +- 0.4 is INSIDE BOTH, and printing "tau" for it would be falla 19
(a ruler that cannot say I cannot tell) wearing the canon as a costume. `both_live` is therefore a
first-class outcome and not a residual: of the pairs below it is the commonest one.

THE PAIR LIST IS STRUCTURAL AND FIXED BEFORE ANY VALUE IS READ (las guardas 3, falla I.3). A pair
is here because the object has two seats, never because its gap looked close to something. Every
pair declared gets reported, including the ones that resolve far away and the ones that cannot be
read at all -- otherwise the table is a maximum over n draws (falla 3) with the draws hidden.

AND THE SELECTION FREEDOM IS PRICED ANYWAY, because choosing to look at n objects is itself a
search: max_bar.bar(n) gives the 5 % bar for the nearest-of-n, so a pair must beat that bar in its
own widths before its landing means anything.

SHARED REFERENCE IS A SEPARATE COLUMN, NOT A CAVEAT. Two quantities defined as differences from the
same fluctuating reference are correlated by construction (feedback-shared-reference-artifact: it
killed 76 % of an r=+0.70, p~1e-75). Each pair declares whether its two seats share a reference. A
shared-reference pair whose gap sits at zero has proved nothing -- the reference cancelled.

    python3 el_hueco.py              the table
    python3 el_hueco.py --selftest   planted gaps, the 6-vs-tau arithmetic, the refused bins
    python3 el_hueco.py --tick       bus rider: speaks only when a pair CHANGES outcome

VIGENCIA_NOT_A_CONSUMER -- this compares ledgers that other tools own; it is not a reader of record
for any of them and vigencia must not count it as one.
"""
import json
import math
import os
import sys

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
from max_bar import bar                      # noqa: E402
from outcomes import Outcomes                # noqa: E402

TAU = 2.0 * math.pi                           # 6.283185307179586
SIX = 6.0
# THE EXCLUSION WIDTH for this one question, arithmetic and not a choice: to tell candidate A from
# candidate B a reading must be known to better than half their separation.
SEPARATION = TAU - SIX                        # 0.2831853071795862
EXCLUSION = SEPARATION / 2.0                  # 0.1415926535897931
LEDGER = os.path.join(W, 'el_hueco.jsonl')
STATE = os.path.join(W, 'el_hueco_state.json')

def _is(name):
    return lambda r: r.get('outcome') == name


OUT = Outcomes(
    subject=[('tau_hole', _is('tau_hole')),       # within a width of tau and NOT of 6
             ('six_hole', _is('six_hole')),       # within a width of 6 and NOT of tau
             ('both_live', _is('both_live')),     # within a width of BOTH: the width, not the gap
             ('no_hole', _is('no_hole'))],        # resolved away from both: a positive reading
    apparatus=[('cannot_read', _is('cannot_read'))],
)


def land(gap, width):
    """Which hole, if either. BOTH distances are computed before either branch is taken (las
    guardas 36 / falla VI-2: an `if near_a: elif near_b:` prints whichever was typed first)."""
    if gap is None or width is None or width <= 0 or gap != gap:
        return 'cannot_read', None, None
    d_tau = abs(gap - TAU) / width
    d_six = abs(gap - SIX) / width
    in_tau, in_six = d_tau <= 1.0, d_six <= 1.0
    if in_tau and in_six:
        return 'both_live', d_tau, d_six       # the width cannot separate 6 from tau
    if in_tau:
        return 'tau_hole', d_tau, d_six
    if in_six:
        return 'six_hole', d_tau, d_six
    return 'no_hole', d_tau, d_six


def readable(gap, width):
    """Could this pair EVER say tau rather than six? A statement about the ruler, not the reading."""
    if gap is None or width is None or width <= 0:
        return None
    return width < EXCLUSION


# ---------------------------------------------------------------- the seats, declared first
def _rows(name, limit=None):
    p = os.path.join(W, name)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, errors='replace') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
    return out[-limit:] if limit else out


def _sd(v):
    n = len(v)
    if n < 2:
        return None
    m = sum(v) / n
    return (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5


def _independent(rows, key):
    """IDENTICAL READINGS ARE ONE READING. Collapses rows sharing (stamp, value) to a single draw.

    Found 12 Oct by this tool refusing its own first input: fase.jsonl held three rows with the
    SAME second and byte-identical values -- three invocations inside one second, each reading the
    same 16 MB tail and so each arriving at the same answer. Counted as three draws they give a
    spread of exactly zero, which would have printed as a width of 0.0000 and an infinitely precise
    gap. The house's own law (identical readings = broken sensor) was in the index and not in the
    code. Returns (values, n_rows, n_independent)."""
    seen, vals = set(), []
    for r in rows:
        v = r.get(key)
        if not isinstance(v, (int, float)) or v != v:
            continue
        sig = (r.get('at'), v)
        if sig in seen:
            continue
        seen.add(sig)
        vals.append(v)
    return vals, len([r for r in rows if isinstance(r.get(key), (int, float))]), len(vals)


def pair_her_cycle():
    """HER CYCLE, read by the bus and by her own corpus. Unit: OUR LOOKS PER HER CYCLE -- the gap
    is literally how many of our observations fall inside one of hers, which is the canon's unit
    ('whatever separates the two observers') and not a ratio invented to be dimensionless."""
    r, n_rows, n_ind = _independent(_rows('fase.jsonl'), 'ratio')
    if not r:
        return dict(gap=None, width=None, n=0)
    return dict(gap=r[-1], width=_sd(r), n=n_ind,
                note='latest %.4f; %d rows collapse to %d INDEPENDENT readings%s'
                     % (r[-1], n_rows, n_ind,
                        ' -- identical readings are one reading' if n_rows != n_ind else ''))


def pair_block_interval():
    """ONE BLOCK INTERVAL, from EL TESTIGO (the finder's own declared stamp) and EL MIRON (our
    GPSDO-stamped arrival). Unit: SECONDS of block interval. Seats do NOT share a reference."""
    b = _rows('bloque.jsonl')
    if not b:
        return dict(gap=None, width=None, n=0)
    x = b[-1]
    w, o = x.get('witness') or {}, x.get('observer') or {}
    if not (w.get('mean') and o.get('mean')):
        return dict(gap=None, width=None, n=0)
    gap = w['mean'] - o['mean']
    width = math.hypot(w.get('sem') or 0.0, o.get('sem') or 0.0) or None
    return dict(gap=gap, width=width, n=(w.get('n', 0) + o.get('n', 0)),
                note='witness %.2f s - observer %.2f s' % (w['mean'], o['mean']))


def pair_closure_method():
    """THE TRIANGLE CLOSURE, read sequentially and bracketed 1,2,3,2,1 -- two positions on ONE
    object separated by METHOD, which is one of the canon's own listed units. Unit: MICROSECONDS.
    SHARED REFERENCE: both readings come off the same three seats, so a zero here is cheap."""
    t = _rows('triangulo.jsonl')
    if not t:
        return dict(gap=None, width=None, n=0)
    x = t[-1]
    if x.get('P_us') is None or not x.get('scatter_us'):
        return dict(gap=None, width=None, n=0)
    return dict(gap=abs(x['P_us']), width=x['scatter_us'], n=len(t), shared_ref=True,
                note='P (our looking) %.1f us, scatter %.1f us' % (x['P_us'], x['scatter_us']))


def pair_closure_ratio():
    """THE SAME TWO METHODS AS A FOLD: how many times larger the bracketed closure is than the
    sequential one. Unit: DIMENSIONLESS FOLD -- directly comparable to a bare 6."""
    t = _rows('triangulo.jsonl')
    if not t:
        return dict(gap=None, width=None, n=0)
    vals = [abs(x['S_us']) / abs(x['sequential_us'])
            for x in t
            if x.get('S_us') and x.get('sequential_us')]
    if not vals:
        return dict(gap=None, width=None, n=0)
    return dict(gap=vals[-1], width=_sd(vals) if len(vals) > 1 else None, n=len(vals),
                shared_ref=True,
                note='bracketed/sequential %.3f fold over %d passes' % (vals[-1], len(vals)))


def pair_phase_lock():
    """HER PHASE, ours against a uniform none. Unit: FOLD of the uniform expectation. The none is
    arithmetic (sqrt(pi)/(2 sqrt(n))) and was built before the measurement."""
    f = _rows('fase.jsonl')
    v, n_rows, n_ind = _independent(f, 'R_over_uniform')
    if not v:
        return dict(gap=None, width=None, n=0)
    return dict(gap=v[-1], width=_sd(v), n=n_ind,
                note='R / uniform %.2f fold; %d rows -> %d independent' % (v[-1], n_rows, n_ind))


def pair_path_vs_closure():
    """WHAT A PAIR COULD BOUND against WHAT THE TRIANGLE ACTUALLY FOUND -- the honest path bound
    over the measured closure. Unit: FOLD. This is the number that says why a pair reports ABIERTO
    forever. SHARED REFERENCE: same three legs."""
    t = _rows('triangulo.jsonl')
    vals = [x['path_bound_us'] / abs(x['S_us'])
            for x in t
            if x.get('path_bound_us') and x.get('S_us')]
    if not vals:
        return dict(gap=None, width=None, n=0)
    return dict(gap=vals[-1], width=_sd(vals) if len(vals) > 1 else None, n=len(vals),
                shared_ref=True,
                note='path bound / closure %.1f fold' % vals[-1])


# THE PAIR LIST. Fixed. Each entry: key, object, unit, reader.
PAIRS = [
    ('her_cycle',       'her cycle',            'our looks per her cycle', pair_her_cycle),
    ('block_interval',  'one block interval',   'seconds',                 pair_block_interval),
    ('closure_method',  'the triangle closure', 'microseconds',            pair_closure_method),
    ('closure_fold',    'the triangle closure', 'fold (method)',           pair_closure_ratio),
    ('phase_lock',      'her phase',            'fold of uniform',         pair_phase_lock),
    ('path_vs_closure', 'the three legs',       'fold (bound/closure)',    pair_path_vs_closure),
]


def scan():
    rows = []
    n_live = 0
    for key, obj, unit, fn in PAIRS:
        try:
            d = fn()
        except Exception as e:
            d = dict(gap=None, width=None, n=0, note='reader failed: %s' % e)
        oc, d_tau, d_six = land(d.get('gap'), d.get('width'))
        if oc != 'cannot_read':
            n_live += 1
        rows.append(dict(key=key, object=obj, unit=unit, outcome=oc,
                         gap=d.get('gap'), width=d.get('width'), n=d.get('n', 0),
                         d_tau=d_tau, d_six=d_six,
                         can_separate=readable(d.get('gap'), d.get('width')),
                         shared_ref=bool(d.get('shared_ref')), note=d.get('note', '')))
    return rows, n_live


def table():
    rows, n_live = scan()
    b = bar(n_live) if n_live >= 2 else 0.0
    print('EL HUECO -- the tau-sized hole, as a GAP between two seats on one object\n')
    print('  6 and tau are %.4f apart, so a gap must be known to +-%.4f (%.2f %% of 6) before'
          % (SEPARATION, EXCLUSION, 100 * EXCLUSION / SIX))
    print('  the words "six" and "tau" mean different things. That is the whole exclusion width.')
    print('  Nearest-of-%d bar (5 %%, exact): %.2f widths -- a landing must beat it to mean anything.\n'
          % (n_live, b))
    for r in rows:
        g = 'cannot read' if r['gap'] is None else '%.4f' % r['gap']
        w = '--' if r['width'] in (None, 0) else '%.4f' % r['width']
        print('  %-16s %-22s gap %s  +- %s  [%s]' % (r['key'], r['object'], g, w, r['unit']))
        if r['outcome'] == 'cannot_read':
            print('      cannot_read: %s' % (r['note'] or 'no rows'))
            continue
        print('      %-11s  %.1f widths from tau, %.1f from 6   (n=%d)'
              % (r['outcome'], r['d_tau'], r['d_six'], r['n']))
        if r['can_separate'] is False:
            print('      CANNOT SEPARATE 6 FROM TAU: width %.4f exceeds the %.4f needed. The ruler,'
                  ' not the reading.' % (r['width'], EXCLUSION))
        if r['shared_ref']:
            print('      SHARED REFERENCE: both seats ride the same legs; a zero here is cheap.')
        if r['note']:
            print('      %s' % r['note'])
        print()
    OUT.tally([{'outcome': r['outcome']} for r in rows], label='pairs scanned')
    OUT.table()
    hits = [r for r in rows if r['outcome'] in ('tau_hole', 'six_hole')]
    sep = [r for r in hits if r['can_separate']]
    print('\n  %d of %d pairs land on a hole; %d of those could tell 6 from tau at all.'
          % (len(hits), len(rows), len(sep)))
    if hits and not sep:
        print('  SO: NO PAIR IN THIS HOUSE CAN NAME THE HOLE IT LANDS IN. The canon is not'
              ' refuted and is not confirmed -- our widths are 1-2 orders too wide to ask it.')
    return rows


def tick():
    rows, _ = scan()
    cur = {r['key']: r['outcome'] for r in rows}
    old = {}
    if os.path.exists(STATE):
        try:
            old = json.load(open(STATE)).get('outcomes', {})
        except Exception:
            old = {}
    moved = [k for k, v in cur.items() if old.get(k) and old[k] != v]
    try:
        with open(LEDGER, 'a') as f:
            f.write(json.dumps(dict(at=__import__('datetime').datetime.now().strftime(
                '%Y-%m-%dT%H:%M:%S%z') or None, rows=rows)) + '\n')
        json.dump(dict(outcomes=cur), open(STATE, 'w'))
    except Exception:
        pass
    for k in moved:
        r = next(x for x in rows if x['key'] == k)
        print('EL HUECO: %s moved %s -> %s (gap %.4f +- %s %s)'
              % (k, old[k], cur[k], r['gap'] or 0,
                 ('%.4f' % r['width']) if r['width'] else '--', r['unit']))


def selftest():
    ok = []

    def ck(name, cond):
        ok.append(bool(cond))
        print('  %s %s' % ('ok  ' if cond else 'FAIL', name))

    ck('6 and tau are 0.283185 apart', abs(SEPARATION - 0.2831853071795862) < 1e-12)
    ck('the exclusion width is half of that, 0.141593', abs(EXCLUSION - 0.14159265358979312) < 1e-12)
    ck('which is 2.36 %% of 6, not 4.7 %%', abs(100 * EXCLUSION / SIX - 2.3598775598298823) < 1e-9)
    ck('a gap at tau with a tight width reads tau_hole', land(TAU, 0.01)[0] == 'tau_hole')
    ck('a gap at 6 with a tight width reads six_hole', land(6.0, 0.01)[0] == 'six_hole')
    ck('a gap between them with a loose width reads both_live',
       land(6.14, 0.25)[0] == 'both_live')
    ck('a gap at 3 reads no_hole', land(3.0, 0.01)[0] == 'no_hole')
    ck('a missing gap reads cannot_read', land(None, 0.01)[0] == 'cannot_read')
    ck('a zero width reads cannot_read', land(6.0, 0.0)[0] == 'cannot_read')
    ck('a NaN gap reads cannot_read', land(float('nan'), 0.01)[0] == 'cannot_read')
    # the one that bites: BOTH distances computed, order of branches cannot decide it
    a, b = land(6.14159, 0.2)[1], land(6.14159, 0.2)[2]
    ck('both_live reports BOTH distances, neither hidden', a is not None and b is not None)
    ck('a width at the exclusion width cannot separate', readable(6.2, EXCLUSION) is False)
    ck('a width under it can', readable(6.2, EXCLUSION * 0.5) is True)
    ck('readable is None when unreadable', readable(None, None) is None)
    try:
        Outcomes(subject=[('tau_hole', _is('tau_hole')), ('none', _is('none'))])
        ck('a refused bin name is refused', False)
    except Exception:
        ck('a refused bin name is refused', True)
    ck('the nearest-of-6 bar is above 2 widths', bar(6) > 2.0)
    ck('the pair list is fixed, not derived from values', len(PAIRS) == 6)
    dup = [{'at': 'T', 'ratio': 6.5}] * 3
    ck('three identical rows collapse to ONE reading', _independent(dup, 'ratio')[2] == 1)
    ck('and so give no width at all', _sd(_independent(dup, 'ratio')[0]) is None)
    mix = [{'at': 'T', 'ratio': 6.5}, {'at': 'T', 'ratio': 6.5}, {'at': 'U', 'ratio': 6.7}]
    ck('a real second reading survives the collapse', _independent(mix, 'ratio')[2] == 2)
    ck('and the row count is kept separately', _independent(mix, 'ratio')[1] == 3)
    print('\n  %d/%d' % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    if '--tick' in sys.argv:
        tick()
    else:
        table()
