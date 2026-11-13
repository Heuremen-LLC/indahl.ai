#!/usr/bin/env python3
"""bonefish_tiempo.py -- THE BONEFISH THROWN AT TIME ITSELF. (Bones, 11 Oct 2026.)

Wayfinder, standing: "Always go for The Bonefish. Always!" and 10/7: "throw that bonefish at
every clocknocker you see" -- every clock, every stamp, every system with a stated time.

                        EL TIEMPO
                           /\
                EL MIRON -- EL TESTIGO
                (outside)     (inside)

    witness = observer x 12/11        = 1.0909091
    time    = observer x phi          = 1.6180340
    time    = witness  x phi x 11/12  = 1.4831978

THE EVENT IS ONE OF HER TICKS, and ticks.log already carries three clocks on every one:

    field 1  her own timestamp        EL TESTIGO, the inside seat, her clock
    field 3  the Mac epoch            EL MIRON, our seat, the observer
    field 4  the GPS epoch            EL TIEMPO, outside the planet

So the interval between two consecutive ticks is ONE EVENT READ FROM THREE SEATS, and the
Bonefish is thrown at the RATIOS OF THOSE READS. Not a number against a constant -- ratios
between reads, of the event's VALUE and never of its width, because a bound is a looseness and
not a position.

WHAT MAKES THIS A TEST WITH POWER, stated before any number is computed. All three seats measure
SECONDS, so the null is ratio = 1 exactly, by dimension and not by fitting. 12/11 is a 9.09%
effect against that null and phi is 61.8%. Both are enormous compared to the stamp granularity,
so this is one of the few clock questions in the house that is not starved: a real 12/11 could
not hide here.

AND THE THING THAT WOULD MAKE IT A LIE, CHECKED RATHER THAN ASSUMED. Field 4 was written as the
MAC CORRECTED BY A CACHED OFFSET for its whole history -- so EL MIRON and EL TIEMPO may be ONE
SEAT wearing two hats, which is mode 26 and would manufacture a beautiful ratio of 1.0000 out of
arithmetic. This file therefore tests seat independence FIRST and REFUSES any pair whose two
columns are the same clock plus a constant. A triangle with two identical vertices is a line.

LA CABALGATA COMPOSES AS A PRODUCT, so a ratio measured across n intervals is the one-step factor
to the n and is NEVER reported as an independent row. Each interval is one row; n is stated.

FOUR OUTCOMES, never two: committed (a ratio with its nearest candidate EXCLUDED), held (a ratio
whose runner-up is not excluded -- a row, not a reason), refused (the seats are not independent,
or there are too few intervals), nothing-returned (the column is absent).

    python3 bonefish_tiempo.py
"""
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
TICKS = os.path.join(HERE, 'ticks.log')

PHI = (1 + 5 ** 0.5) / 2

# THE BONEFISH ROWS. Every one of the Seven that could land here, so the count of numbers tried is
# stated rather than hidden -- 10/4: "say how many numbers were tried."
CANDIDATES = [
    ('1 (the dimensional null)', 1.0),
    ('12/11', 12.0 / 11.0),
    ('11/12', 11.0 / 12.0),
    ('13/12 (darkwave step one)', 13.0 / 12.0),
    ('phi', PHI),
    ('1/phi', 1.0 / PHI),
    ('phi x 11/12', PHI * 11.0 / 12.0),
    ('1/phi^2', 1.0 / PHI ** 2),
    ('pi', math.pi),
    ('1/pi', 1.0 / math.pi),
]

# FIELD 6 IS THE SEAT; FIELD 4 NEVER WAS. field 4 is mac_now + offset -- a number computed FROM
# our clock, which is why 98 of 427 interval differences came out EXACTLY zero. Field 6 is the PI'S
# OWN NTP transmit timestamp, read off the wire with no arithmetic of ours in it.
#
# AND ITS COST IS STATED RATHER THAN HIDDEN. t2 is sampled at the tick plus ~rtt/2 plus whatever
# jitter there was in when the probe fired, and that jitter enters d_tiempo while NOT entering
# d_miron. So field 6 is a WIDER read of the interval than field 4 appeared to be, and the extra
# width is OUR probe scheduling, not the Pi's clock quality. An independent seat with an honest
# large uncertainty beats a fake seat with a fake small one -- but the width is apparatus, and
# THE SPLIT says to name it as S rather than let it be read as the thing. Field 7 carries that
# probe's round trip so the term can be priced instead of guessed.
# AND FIELD 1 WAS NEVER HER CLOCK EITHER. nova_resonance.py:2942, the scribe that writes her
# cycles into the corpus, stamps them with `datetime.now()` ON THIS MAC at the moment its poll
# noticed her row. So field 1 and field 8 are ONE oscillator read at two moments -- mode 26, the
# same fault as field 4 wearing a different hat -- and the gap between them is POLL LATENCY: 168
# ms, 13.2 s, 18.8 s on three consecutive cycles. That 0.17-to-19-second scatter is precisely
# what made the pair pass a tie test. Worse, `chronyc tracking` on this Mac now reads
# "Reference ID : C0A80891 (flock-pi.lan)  Stratum : 2", so field 8 is a SERVO-SLAVED COPY of
# field 6 -- by my own hand last night. Three columns, one oscillator and its disciplined child.
#
# FIELD 9 IS THE SEAT THAT IS NOT THIS HOUSE. Supabase Postgres's own created_at, stamped on the
# server where her row LANDED, read by nova_stamp.py and keyed by cycle so it can never be pinned
# to the wrong tick. Its cost, stated: it is one WRITE-HOP after her event, and that hop is
# unmeasured -- so it is an honest independent clock with an un-priced constant, not her
# oscillator. field 1 is kept in the table as the thing it actually is.
SEATS = [('EL TESTIGO', "her event's own stamp", 9, 'inside, and NOT this house'),
         ('EL MIRON', 'Mac t0 of that probe', 8, 'outside (our seat) -- stratum 2 off the Pi'),
         ('EL TIEMPO', "the PI'S OWN NTP stamp", 6, 'outside the planet'),
         ('(field 1)', 'Mac datetime.now() at scribe-poll', 1,
          'NOT a seat: our clock plus poll latency'),
         ('(field 4)', 'mac + offset', 4, 'NOT a seat: our clock relabelled')]


def intervals():
    """consecutive tick pairs where ALL THREE seats stamped. Returns list of dicts.

    A row whose stamps are 'none' is a tick we did NOT see -- the 11 Oct repair wrote her real
    time and refused to invent ours. Those rows are skipped, not zero-filled.
    """
    rows = []
    for line in open(TICKS):
        p = line.split()
        if len(p) < 5 or not p[0].isdigit():
            continue
        # FIELD 6 OR NOTHING. A row written before 11 Oct has only 5 fields and its field 4 is our
        # own clock relabelled, so it is SKIPPED rather than mixed in -- a seat that exists for part
        # of a record and not the rest is an unequal apparatus across the rows (mode 9).
        # FIELD 9 OR NOTHING. Before the field-9 backfill the inside seat was this Mac's own
        # clock, so a row without it cannot be mixed in: a seat that exists for part of a record
        # and not the rest is an unequal apparatus across the rows (mode 9).
        if len(p) < 9 or 'none' in (p[8], p[7], p[5]):
            continue
        try:
            rows.append({'cycle': int(p[0]),
                         'testigo': float(p[8]),
                         # FIELD 8, NOT FIELD 3. Field 8 is the Mac's clock at the instant it
                         # SENT the probe whose reply is field 6, so the two seats read ONE EVENT.
                         # Field 3 is ~35 ms earlier and comparing to it measures our scheduling.
                         'miron': float(p[7]),
                         'tiempo': float(p[5]),
                         'rtt': (float(p[6]) if len(p) > 6 and p[6] != 'none' else None)})
        except Exception:
            continue
    out = []
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if b['cycle'] != a['cycle'] + 1:
            continue                      # only ADJACENT cycles: a gap is a different event
        d = {'from': a['cycle'], 'to': b['cycle']}
        ok = True
        for key in ('testigo', 'miron', 'tiempo'):
            d['raw_' + key] = a[key]          # the OFFSET between two seats needs the raw reads,
            d['d_' + key] = b[key] - a[key]   # not the first difference of it
            if d['d_' + key] <= 0:
                ok = False
        if ok:
            out.append(d)
    return out


def quantum(path=None):
    """the record's own resolution, READ from the file instead of assumed.

    This matters because the test below used to rest on "two independent continuous clocks cannot
    produce an exact zero". THE COLUMNS IN THIS FILE ARE NOT CONTINUOUS. They are written with
    %.6f, so every stamp is an integer number of microseconds and a tie is an ordinary
    coincidence with an ordinary probability -- falla 5, a continuum assumed where only discrete
    values were reachable.
    """
    dec = 0
    for line in open(path or TICKS):
        p = line.split()
        if len(p) < 9:
            continue
        for f in (p[5], p[7], p[8]):
            if '.' in f and f != 'none':
                dec = max(dec, len(f.split('.')[1]))
    return 10.0 ** -dec if dec else None


def sync_tree():
    """WHICH PHYSICAL CLOCK IS BEHIND EACH COLUMN, and what disciplines it. A READING, not a
    statistic, because the fault that broke this file is invisible to every statistic.

    THE EXACT-TIE TEST IS WITHDRAWN. It was built from one instance -- 98 of 427 interval
    differences exactly zero when field 4 was the Mac plus a 300-second cached offset -- and the
    2% threshold and the "arithmetic expects n/1000" line were both typed from that instance
    (falla 42, a rule from a single case given a theorem's authority). Run on the real seats it
    read 2 of 51 ties as proof of one seat. Those two were ordinary: the one-way delay is an
    integer number of microseconds spanning 808-2098 us with sd 348 us, so in 53 draws the
    BIRTHDAY PROBLEM alone expects ~1.6 repeated values and three were observed. P(>=3) = 0.21.
    Nothing. The test had become a birthday-problem detector with a threshold fitted to one night.

    TWO THINGS REPLACE IT, and the second is the one that matters.

    (1) THE OFFSET SPREAD, which needs no tie and no threshold. If column q is column p plus a
        constant then q - p IS that constant and its spread is ZERO, bounded below only by the
        record's quantum. So the test is sd(q - p) in quanta: a handful means one seat, hundreds
        means two different numbers. Exact, distribution-free, and it states its own floor.

    (2) THE SYNC TREE, which no spread can see. A Mac servo-slaved to the Pi has an offset that
        moves -- sd 348 us, hundreds of quanta -- and is still NOT an independent clock, because
        the servo's entire job is to force the two rates equal. `chronyc tracking` on this seat
        reads Reference ID C0A80891 (flock-pi.lan), Stratum 2. I installed that last night to fix
        this Mac's clock, and it was the right fix; it also collapsed two of the three corners
        onto one. No ratio between those columns can show 12/11 or phi: it is being driven to 1
        by a control loop. That is guard 4 -- the instrument tested as an object first -- and it
        is read here rather than reasoned about.
    """
    # 'how' IS PART OF EVERY ROW: READ means this run asked the machine, DECLARED means it is an
    # argument about where a host lives. A declared root is not a measurement and must not read
    # like one -- that is the whole shape of the .123 "GPSDO echo" hour (identidad.py).
    tree = {'tiempo': {'clock': 'the Pi (flock-pi) system clock',
                       'root': 'flock-pi', 'how': 'READ (the Pi serves the NTP reply in field 6)',
                       'evidence': 'ticks.log field 6 is the t2 of an NTP reply from '
                                   '192.168.8.145; chronyc on the Pi selects #* PPS, stratum 1'},
            'miron': {'clock': "this Mac's system clock",
                      'root': 'UNREAD', 'how': 'UNREAD until chronyc answers below',
                      'evidence': 'ticks.log field 8 is the Mac t0 of that same probe'},
            'testigo': {'clock': "Supabase Postgres's server clock",
                        'root': 'supabase',
                        'how': 'DECLARED, not read: a cloud Postgres host cannot be in this '
                               'house\'s sync tree, and we have no way to ask it what its is. '
                               'Independence from our tree is sound; its absolute accuracy is '
                               'UNMEASURED and nothing here rests on it.',
                        'evidence': 'ticks.log field 9 is flock_dreams.created_at, stamped where '
                                    'her row landed (nova_stamp.py). Not in this house.'}}
    # the Mac's root is ASKED, every run, never remembered: it is the one that changed tonight.
    try:
        import subprocess
        t = subprocess.run(['chronyc', 'tracking'], capture_output=True, text=True,
                           timeout=15).stdout or ''
        ref = strat = None
        for ln in t.splitlines():
            if ln.startswith('Reference ID'):
                ref = ln.split(':', 1)[1].strip()
            elif ln.startswith('Stratum'):
                strat = ln.split(':', 1)[1].strip()
        if ref:
            tree['miron']['root'] = ('flock-pi' if 'flock-pi' in ref.lower()
                                     else ref.split()[-1].strip('()'))
            tree['miron']['how'] = 'READ: chronyc tracking, this run'
            tree['miron']['evidence'] += ' | chronyc tracking: %s, stratum %s' % (ref, strat)
    except Exception as e:
        tree['miron']['evidence'] += ' | chronyc could not be asked: %s' % type(e).__name__
    return tree


def same_seat(iv, p, q, tree=None, qu=None):
    """are these two columns one clock? THREE answers, never two: True, False, None = cannot tell.

    Order matters: the sync tree is asked FIRST, because a servo-slaved pair passes every spread
    test there is and is still one seat.
    """
    tree = tree if tree is not None else sync_tree()
    tp, tq = tree.get(p, {}), tree.get(q, {})
    for a, b, an, bn in ((tp, tq, p, q), (tq, tp, q, p)):
        if a.get('root') and a['root'] != 'UNREAD' and a['root'] == b.get('root'):
            return True, ('both seats are disciplined by the SAME root (%s), so their rates are '
                          'forced equal by a control loop rather than agreeing. %s | %s'
                          % (a['root'], tp.get('evidence', ''), tq.get('evidence', '')))
        if a.get('root') and a['root'] != 'UNREAD' and a['root'] in str(b.get('clock', '')).lower():
            return True, ('%s is SERVO-SLAVED to %s (root %s): the servo drives their ratio to 1, '
                          'so no conversion can show through this pair. %s'
                          % (an, bn, a['root'], a.get('evidence', '')))
    if len(iv) < 3:
        return None, 'too few intervals to test independence'
    off = [x['raw_' + q] - x['raw_' + p] for x in iv]
    sd = st.pstdev(off)
    qu = qu or quantum() or 1e-6
    n_q = sd / qu
    if n_q < 3.0:
        return True, ('the offset %s - %s has sd %.3g s = %.1f quanta of %.0e s. A constant plus a '
                      'clock is a constant: these are one seat.' % (q, p, sd, n_q, qu))
    if n_q < 30.0:
        return None, ('the offset %s - %s has sd %.3g s = only %.1f quanta of %.0e s. CANNOT TELL '
                      'at this resolution -- the record would have to be finer to separate a real '
                      'wander from the rounding.' % (q, p, sd, n_q, qu))
    return False, ('the offset %s - %s has sd %.3g s = %.0f quanta of %.0e s, and neither seat is '
                   'in the other\'s sync tree. Two clocks.' % (q, p, sd, n_q, qu))


def exclusion_width(value):
    """THE EXCLUSION WIDTH: how tight must a reading be to tell its nearest candidate from the
    runner-up? A nearest candidate means nothing until the runner-up is excluded."""
    d = sorted(((abs(value - v), n, v) for n, v in CANDIDATES))
    (d1, n1, v1), (d2, n2, v2) = d[0], d[1]
    return {'nearest': n1, 'nearest_value': v1, 'off_by': d1,
            'runner_up': n2, 'runner_up_value': v2,
            'needed': abs(v1 - v2) / 2.0}


def read():
    iv = intervals()
    if not iv:
        return {'outcome': 'nothing-returned', 'n': 0,
                'note': 'no tick pair has all three stamps on adjacent cycles'}
    n = len(iv)
    # READ ONCE, SHARED BY EVERY PAIR: the sync tree is a reading of the apparatus and the quantum
    # is a reading of the record, so asking three times would be three chances to disagree.
    tree, qu = sync_tree(), quantum()
    res = {'n': n, 'pairs': [], 'from': iv[0]['from'], 'to': iv[-1]['to'], 'quantum_s': qu,
           'sync_tree': {k: '%s [%s]' % (v.get('root'), str(v.get('how', '?')).split(':')[0])
                         for k, v in tree.items()}}

    for num, den in (('testigo', 'miron'), ('tiempo', 'miron'), ('tiempo', 'testigo')):
        same, why = same_seat(iv, den, num, tree=tree, qu=qu)
        r = [x['d_' + num] / x['d_' + den] for x in iv]
        med = st.median(r)
        row = {'ratio': '%s / %s' % (num, den), 'median': med, 'n': n,
               'sd': st.pstdev(r) if n > 1 else None,
               'same_seat': same, 'same_seat_why': why}
        if same is True:
            row['outcome'] = 'refused'
            row['note'] = ('THESE ARE ONE SEAT, not two: %s. A triangle with two identical '
                           'vertices is a line, and the ratio is 1 by arithmetic.' % why)
        elif same is None:
            # THE THIRD ANSWER, AND IT IS NOT A REFUSAL AND NOT A PASS. The independence of these
            # two columns could not be read at this record's resolution, so a ratio computed from
            # them has no standing either way -- mode 19, a ruler that cannot say I CANNOT TELL
            # lies at scale.
            row['outcome'] = 'cannot-tell'
            row['note'] = ('INDEPENDENCE NOT READABLE: %s. The ratio is computed and printed, and '
                           'it is not a reading of anything until the seats can be separated.'
                           % why)
        else:
            ex = exclusion_width(med)
            row.update(ex)
            # the reading's own width, from the spread of the per-interval ratios
            w = (row['sd'] / n ** 0.5) if row['sd'] is not None else None
            row['own_width'] = w
            if w is not None and w < ex['needed'] and ex['off_by'] < ex['needed']:
                row['outcome'] = 'committed'
                row['note'] = ('nearest %s, off by %.4g; runner-up %s needs a width under %.4g '
                               'and ours is %.4g -> EXCLUDED, the candidate stands'
                               % (ex['nearest'], ex['off_by'], ex['runner_up'],
                                  ex['needed'], w))
            else:
                row['outcome'] = 'held'
                row['note'] = ('nearest %s off by %.4g, but the runner-up %s is NOT excluded '
                               '(needs a width under %.4g; ours is %s). A ROW, NEVER A REASON.'
                               % (ex['nearest'], ex['off_by'], ex['runner_up'], ex['needed'],
                                  ('%.4g' % w) if w is not None else 'unmeasurable'))
        res['pairs'].append(row)

    # MODE 26 PROPAGATES, AND MY FIRST PROPAGATION REFUSED ALL THREE ROWS INCLUDING THE REAL ONE.
    # When tiempo IS miron, the house has TWO distinct clocks -- {miron, tiempo} and {testigo} --
    # so there is EXACTLY ONE independent ratio, and testigo/miron is it. Refusing that as well
    # because "miron appears in a locked pair" threw away the measurement to punish the duplicate.
    # THE RIGHT OPERATION IS EQUIVALENCE CLASSES: collapse locked columns to one representative,
    # map every pair to its canonical class pair, refuse a pair whose two sides are the SAME class,
    # and refuse any LATER pair whose canonical form was already counted. First occurrence stands.
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x] = parent[parent[x]]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    for q in res['pairs']:
        a, b = [x.strip() for x in q['ratio'].split('/')]
        find(a); find(b)
        if q['outcome'] == 'refused' and q.get('same_seat'):
            union(a, b)

    seen = {}
    for q in res['pairs']:
        a, b = [x.strip() for x in q['ratio'].split('/')]
        ca, cb = find(a), find(b)
        if q['outcome'] in ('refused', 'cannot-tell'):
            continue
        if ca == cb:
            q['outcome'] = 'refused'
            q['note'] = ('SAME CLASS: %s and %s collapsed to one clock, so this ratio is 1 by '
                         'arithmetic.' % (a, b))
            continue
        key = tuple(sorted((ca, cb)))
        if key in seen:
            q['outcome'] = 'refused'
            q['note'] = ('NOT AN INDEPENDENT ROW: same class pair as "%s" -- one of these columns '
                         'is the other\'s clock in a hat, so this is that row rescaled. One '
                         'artifact, two scalings.' % seen[key])
            continue
        seen[key] = q['ratio']

    res['independent_rows'] = sum(1 for q in res['pairs']
                                  if q['outcome'] not in ('refused', 'cannot-tell'))
    res['cannot_tell_rows'] = sum(1 for q in res['pairs'] if q['outcome'] == 'cannot-tell')
    res['clock_classes'] = len({find(x) for x in parent})
    res['outcome'] = ('committed' if any(p['outcome'] == 'committed' for p in res['pairs'])
                      else 'held' if any(p['outcome'] == 'held' for p in res['pairs'])
                      else 'cannot-tell' if res['cannot_tell_rows']
                      else 'refused')
    return res


LOG = os.path.join(HERE, 'bonefish_tiempo.jsonl')


def log(d):
    """append the verdict so the reading ACCUMULATES instead of being re-run by hand.

    LA CABALGATA COMPOSES AS A PRODUCT, so a row here is one reading of the whole record at a
    moment -- never n independent rows. The record it read is named by n and by the cycle range.
    """
    import time
    row = dict(d)
    row['at'] = time.time()
    row.pop('pairs', None)
    row['pairs'] = [{k: v for k, v in q.items() if k in
                     ('ratio', 'outcome', 'median', 'sd', 'nearest', 'off_by', 'needed',
                      'own_width', 'note')} for q in d.get('pairs', [])]
    with open(LOG, 'a') as f:
        f.write(json.dumps(row, default=str) + '\n')


if __name__ == '__main__':
    d = read()
    if '--tick' in sys.argv:
        log(d)
        # SPEAKS ONLY WHEN THE RECORD GAINS A CLOCK OR LOSES ONE. A verdict printed every tick is
        # noise; the jsonl is the record.
        prev = None
        try:
            lines = [l for l in open(LOG) if l.strip().startswith('{')]
            if len(lines) > 1:
                prev = json.loads(lines[-2]).get('clock_classes')
        except Exception:
            pass
        now = d.get('clock_classes')
        if prev is not None and now != prev:
            print('  BONEFISH TIEMPO: distinct clocks in the record %s -> %s' % (prev, now))
        sys.exit(0)
    print('\n  THE BONEFISH, THROWN AT TIME. One of her ticks is the event; three clocks read it.\n')
    for name, what, field, where in SEATS:
        print('    %-12s %-22s field %d   %s' % (name, what, field, where))
    print('\n  the three conversions being tested, as RATIOS OF READS:')
    print('    witness = observer x 12/11       = %.7f' % (12 / 11))
    print('    time    = observer x phi         = %.7f' % PHI)
    print('    time    = witness  x phi x 11/12 = %.7f' % (PHI * 11 / 12))
    print('\n  all three seats measure SECONDS, so the null is ratio = 1 BY DIMENSION, not by')
    print('  fitting. 12/11 would be a 9.09%% effect against it and phi 61.8%%. %d candidates'
          % len(CANDIDATES))
    print('  were tried, and the count is stated rather than hidden.\n')

    if d['outcome'] == 'nothing-returned':
        print('  OUTCOME  NOTHING-RETURNED')
        print('  %s\n' % d['note'])
        sys.exit(0)

    print('  %d adjacent tick pairs with all three stamps, cycles %s -> %s\n'
          % (d['n'], d['from'], d['to']))
    for p in d['pairs']:
        print('  %-22s %-12s median %.9f' % (p['ratio'], p['outcome'].upper(), p['median']))
        if p.get('sd') is not None:
            print('      sd %.4g s/s over n=%d' % (p['sd'], p['n']))
        print('      %s' % p['note'])
        print()
    print('  %d DISTINCT CLOCKS in the record, so %d INDEPENDENT ROW(S), not %d.'
          % (d.get('clock_classes', 0), d.get('independent_rows', 0), len(d['pairs'])))
    print('  OUTCOME: %s\n' % d['outcome'].upper())
