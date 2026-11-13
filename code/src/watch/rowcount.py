"""ROWCOUNT -- a row count is not an event count. Wayfinder and Bones, 20 Oct 2026.

His: "this is also loadbearing, dig into it man."

WHY THIS EXISTS. On 20 Oct I read twelve EAR_LOST rows as twelve faults. Their timestamps were seven
seconds apart on each of two seats, and seven seconds is the retry period in the ear's own code
(`except: log(...); await asyncio.sleep(5)` plus a ~2 s connect). Twelve rows described ONE fault per
seat. In the same hour I quoted "distinct peers seen: 230" off a log written by three rigs, because a
stratum redial mints a fresh ephemeral port and the socket count is a reconnect counter in a costume.

    A ROW COUNT CARRIES THE CADENCE THAT WROTE IT.
    rows = duration_of_the_condition / writing_period   ->  that measures THE LOOP, not the world.

LAS GUARDAS, first principle: a guard is a FILTER, NOT A TEACHER, and the strongest one is a REQUIRED
FIELD rather than a remembered rule. The remembered version failed twice in one hour. So:

    THIS OBJECT REFUSES TO BE USED AS A NUMBER. int(), float() and arithmetic all raise. A caller
    must say .rows or .runs out loud and therefore has to have decided which one it means.

AND IT REFUSES TO COLLAPSE BLINDLY. The collapse is only meaningful where the repetition IS a loop,
so it reports rows, runs, the measured within-identity cadence and the largest within-run gap, and
sets a STATE which is one of four -- never two:

    INFLATED      the rows are tight, regular and identical: the count is the loop's
    CLEAN         runs == rows: nothing merged, the count stands
    CANNOT_TELL   too few rows, or no cadence can be measured, or a within-run gap sits far above
                  the cadence so the run may be two
    OVERCOLLAPSED the caller's own identity is too coarse: distinct payloads got merged

The second fault is the one that bit: my first collapser grouped the STREAM, so rows alternating
house, nj, house, nj never merged and the artifact survived. HERE THE SPLIT BY IDENTITY HAPPENS
FIRST, ALWAYS, and each identity's own series is collapsed on its own cadence.

AND SEPARATELY: THE APPARATUS DOES NOT BELONG IN THE SUBJECT'S COLUMN. On the same log, 207 of 230
connects were our own watchdog probing the stratum port -- and because the local miner runs over
loopback too, our observer and our subject SHARE AN ADDRESS. Address is not identity when the
observer lives where the observed lives. `subject_only` takes the gate that admits a real subject
row and reports what it removed, by name, rather than quietly filtering.
"""


class Refused(Exception):
    """Raised when a RowCount is used as though it were already a number."""


class RowCount(object):
    __slots__ = ('rows', 'runs', 'cadence', 'max_gap', 'state', 'by_identity', 'why')

    def __init__(self, rows, runs, cadence, max_gap, state, by_identity, why):
        self.rows = rows
        self.runs = runs
        self.cadence = cadence
        self.max_gap = max_gap
        self.state = state
        self.by_identity = by_identity
        self.why = why

    # THE TEETH. A bare row count is the fault, so this cannot be spent as one.
    def _refuse(self, *a, **k):
        raise Refused(
            'a RowCount is not a number. say .rows (%d) or .runs (%d) explicitly -- the whole point '
            'is that they differ: %s' % (self.rows, self.runs, self.why))

    __int__ = __float__ = __index__ = _refuse
    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = _refuse
    __truediv__ = __rtruediv__ = __lt__ = __gt__ = __le__ = __ge__ = _refuse

    def __repr__(self):
        return ('<RowCount %s rows=%d runs=%d cadence=%s max_gap=%s>'
                % (self.state, self.rows, self.runs,
                   ('%.1fs' % self.cadence) if self.cadence is not None else 'CANNOT_TELL',
                   ('%.0fs' % self.max_gap) if self.max_gap is not None else '-'))

    def line(self):
        return '%s  %s' % (repr(self), self.why)


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def count(items, break_at=3.0, min_for_cadence=3, payload=None):
    """items: iterable of (when, identity) or (when, identity, payload).

    THE SPLIT BY IDENTITY HAPPENS FIRST. Each identity's own series is collapsed on its OWN measured
    cadence, so interleaved identities cannot hide a retry loop -- which is exactly how the founding
    case escaped the first version of this.
    """
    rec = []
    for it in items:
        if len(it) == 2:
            rec.append((it[0], it[1], None))
        else:
            rec.append((it[0], it[1], it[2]))
    if not rec:
        return RowCount(0, 0, None, None, 'CANNOT_TELL', {},
                        'ZERO ROWS. a zero-row reading is BLIND, never agreement')

    per = {}
    for when, ident, pay in rec:
        per.setdefault(ident, []).append((when, pay))

    out = {}
    tot_runs = 0
    cads, worsts = [], []
    overcollapsed = False
    for ident, series in per.items():
        series.sort()
        gaps = [b[0] - a[0] for a, b in zip(series, series[1:]) if b[0] > a[0]]
        cad = _median(gaps) if len(gaps) >= min_for_cadence else None
        if cad is None or cad <= 0:
            runs, worst = len(series), None
        else:
            cut = break_at * cad
            runs, worst, cur = 1, 0.0, series[0]
            for prev, nxt in zip(series, series[1:]):
                d = nxt[0] - prev[0]
                if d <= cut:
                    worst = max(worst, d)
                else:
                    runs += 1
            # distinct payloads merged into one run means the caller's identity is too coarse
            if len({p for _, p in series if p is not None}) > 1 and runs < len(series):
                overcollapsed = True
        out[ident] = {'rows': len(series), 'runs': runs, 'cadence': cad, 'max_gap': worst}
        tot_runs += runs
        if cad is not None:
            cads.append(cad)
        if worst:
            worsts.append(worst)

    rows = len(rec)
    cadence = _median(cads) if cads else None
    worst = max(worsts) if worsts else None

    if overcollapsed:
        state = 'OVERCOLLAPSED'
        why = ('distinct payloads were merged into one run: the identity you passed is too coarse, '
               'so .runs is an UNDERCOUNT. use a finer identity before trusting it')
    elif cadence is None:
        state = 'CANNOT_TELL'
        why = ('no identity has %d gaps, so no writing cadence can be measured and nothing can be '
               'collapsed. .rows stands only because .runs could not be computed' % min_for_cadence)
    elif worst is not None and worst > 2 * break_at * cadence:
        state = 'CANNOT_TELL'
        why = ('a within-run gap of %.0fs sits far above the %.1fs cadence, so a run may be two. '
               'neither count is safe yet' % (worst, cadence))
    elif tot_runs < rows:
        state = 'INFLATED'
        why = ('%d rows describe %d event(s): the row count is inflated %.1fx by a writing cadence '
               'of %.1fs. USE .runs' % (rows, tot_runs, rows / float(tot_runs), cadence))
    else:
        state = 'CLEAN'
        why = ('nothing merged at a %.1fs cadence, so rows and events agree. USE .rows' % cadence)

    return RowCount(rows, tot_runs, cadence, worst, state, out, why)


def subject_only(items, is_subject, name='rows'):
    """Split APPARATUS rows out of SUBJECT rows and NAME what left.

    20 Oct: 207 of 230 connects in the miners' own log were our own watchdog probing the stratum
    port, and because the local miner runs over loopback the observer and the subject SHARE AN
    ADDRESS. A silent filter would have left that invisible, so this returns the kept rows and a
    line saying exactly how much of the record was us.
    """
    kept, dropped = [], []
    for it in items:
        (kept if is_subject(it) else dropped).append(it)
    n = len(kept) + len(dropped)
    frac = (100.0 * len(dropped) / n) if n else 0.0
    note = ('%s: %d of %d rows (%.1f%%) were THE APPARATUS and are excluded; %d remain as the '
            'subject.%s' % (name, len(dropped), n, frac, len(kept),
                            '  THE APPARATUS OUTNUMBERS THE SUBJECT -- any reading of this record '
                            'without the split was mostly us.' if len(dropped) > len(kept) else ''))
    return kept, dropped, note


if __name__ == '__main__':
    # SELF-TEST ON THE REAL CASE, so the module proves itself rather than asserting it.
    print('--- the founding case: 12 EAR_LOST rows, two seats, 7 s apart ---')
    t0 = 1792468046.0
    ear = []
    for s in ('house', 'nj'):
        for k in range(6):
            ear.append((t0 + 7 * k, s))
    rc = count(ear)
    print(rc.line())
    for ident, d in sorted(rc.by_identity.items()):
        print('   %-6s rows=%d runs=%d cadence=%.1fs' % (ident, d['rows'], d['runs'], d['cadence']))
    assert rc.state == 'INFLATED', rc.state
    assert rc.runs == 2, rc.runs          # one fault per seat
    try:
        int(rc)
        raise SystemExit('FAILED: a RowCount let itself be used as a number')
    except Refused as e:
        print('   refused as a number, correctly: %s' % str(e)[:90])

    print()
    print('--- genuine separate events must NOT collapse ---')
    shares = [(t0 + 26 * k, 'rig1', 'share%d' % k) for k in range(12)]
    rc2 = count(shares)
    print(rc2.line())
    assert rc2.state == 'OVERCOLLAPSED', rc2.state

    print()
    print('--- the apparatus in the subject column ---')
    rows = [('probe', i) for i in range(207)] + [('rig', i) for i in range(23)]
    kept, dropped, note = subject_only(rows, lambda r: r[0] == 'rig', name='MINER connects')
    print('   ' + note)
    assert len(kept) == 23
    print()
    print('ALL SELF-TESTS HELD.')
