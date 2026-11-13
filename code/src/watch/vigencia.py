#!/usr/bin/env python3
"""vigencia.py -- IS THE LEDGER STILL ALIVE, AND WHO IS STANDING ON IT. (Bones, 12 Oct 2026.)

His bedtime order, 11 Oct: "run our seven against the system to see if we missed an area to tune.
our findings are the key man, use them to tune our shit."

`afinar.py` reads BUDGETS. This reads ARTIFACTS, and it was found by using afinar: chasing its
highest-load unmeasured budget into `calib.py` turned up something the budget scan cannot see --
**calib.jsonl stopped being written 27 hours ago and FOUR FILES STILL READ IT**, one of them
taking "the newest rows" as a live edge with no age check anywhere. Nothing in this house asked
whether an artifact it depends on is still being written.

    THE ABSENCE OF A PROCESS IS NOT THE ABSENCE OF WORK, and its converse is worse: a FILE that
    is still there reads exactly like a file that is still true. A dead ledger does not raise an
    error. It serves its last row forever.

THE BAR IS NOT A NUMBER I TYPED, and the first version of it was. I began with age against the
artifact's MEDIAN write gap, which ranked faults.jsonl worst at 1,549x. But faults.jsonl has
survived a 10,437 s pause in its own history and calib.jsonl never paused longer than 681 s, so a
house-wide notion of "fast" was doing the ranking. **Each artifact is now priced against ITS OWN
WORST GAP EVER** -- the longest silence it has actually come back from. Exceeding that is a state
the file has never been in before, it needs no constant from me, and the history IS the baseline,
built before the measurement it judges rather than after.

MEASURED 12 Oct, and the two populations do not touch:

    live    age/maxgap tops out at 0.99   (15 read artifacts, most of them under 0.03)
    dead    144x, 61x, 55x, 18x, 16x, 11x, and one at 2.2x

AND THE SEPARATION AT 1.0 IS NOT A FINDING -- the bar IS ratio > 1, so the gap there is the
definition doing the work. What the rule does NOT decide for itself is how far past its record a
dead ledger sits, and SIX OF SEVEN are at 10x or worse. A rule that was only just separating
would have them clustered at 1.1x. That is the part worth reporting.

FOUR OUTCOMES, exhaustive and disjoint, through outcomes.py:

    live        written more recently than its own longest survived silence
    dead        past its own record, AND something reads it -- the only bin worth acting on
    no_record   fewer than 4 timestamped rows, so the artifact cannot declare a cadence and this
                instrument CANNOT TELL. Not a pass and not a failure.
    unread      APPARATUS: load 0. Nobody stands on it, so its silence costs nothing and says
                nothing about whether the house is healthy.

RANKED BY LOAD FIRST, per his 6 Oct order: patch the hole most statements stand on, never the
cheap one. Load is the count of files in the tree naming the artifact.

AND THIS FILE DOES NOT RESTART ANYTHING. Several of the dead ledgers are clock files, and THE
CLOCK LANE IS CLOSED by his call on 11 Oct. Reviving a two-way offset measurement to feed a clock
would be reopening it. Reporting that four files read a 27-hour-old ledger as live is not.

    python3 vigencia.py          # the full table
    python3 vigencia.py --tick   # speaks only when an artifact CROSSES its own record, once
"""
import argparse
import ast
import datetime
import glob
import isostamp
import json
import os
import re
import statistics as st
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'vigencia.jsonl')
STATE = os.path.join(W, 'vigencia_state.json')

# MEASURED, not chosen, and CORRECTED: I first wrote 1.9 s here from no measurement at all, which
# is the exact object afinar.py exists to catch, in a file written an hour after building it. Timed:
# a full scan over 50 artifacts and 64 source files is 0.13 s wall. The leash below is 120 s, 920x
# the measured run, and nothing nested inside it has a budget of its own.
MIN_ROWS = 4          # fewer than four gaps cannot give a worst gap worth comparing against

# 12 Oct, THE THIRD FAULT THIS FILE FOUND IN ITSELF, and the most expensive one: the stamp reader
# was `"at"` followed by a QUOTED ISO string and nothing else. Two consequences, both measured by
# surveying the first rows of all 51 ledgers rather than guessing which keys exist:
#   * `observer.jsonl` -- OUR OWN LOOKS, the WE-ARE-HATS-TOO ledger -- keys its rows `at_local`.
#     26 good timestamps, and this file reported "cannot declare a cadence" about all of them.
#     An instrument that reads one spelling of a key and calls the others absent is the no_record
#     bin answering a question it CAN answer.
#   * `"at"` carrying an EPOCH NUMBER instead of a string (bonefish_tiempo, reloj_casa,
#     clock_triangle) missed the same way -- the key was right and the TYPE was not.
# GPS KEYS ARE DELIBERATELY EXCLUDED (gps, gps0, gps1, gps_mid). Those are the READING, not the
# row's own declaration of when it was written, and treating a measured value as a write time is
# an artifact's internal record used as a second independent reading. Excluding them costs
# nothing, measured: every file carrying a gps key also carries `at`.
# The PARSE itself lives in isostamp.py, because it is version-dependent and the bus
# runs Python 3.9 while this shell runs 3.14 -- read that file's docstring before
# touching any stamp in this house.
UNPARSEABLE = []     # files this interpreter could not parse; see deps()
NOT_CONSUMERS = set()  # files that DECLARE they read only to test; see deps()
STAMP_KEYS = ('at', 'at_local', 't', 'ts', 'mac_s', 'mac_wall')
STAMP = re.compile(
    r'"(' + '|'.join(STAMP_KEYS) + r')"\s*:\s*(?:"([0-9T:\-+\.]{19,})"|([0-9]{9,10}(?:\.[0-9]+)?))')


def stamps(path):
    """every timestamp the artifact declares about ITSELF, in the order it wrote them.

    ONE stamp per row, the first key that parses, so a row carrying both `at` and `ts` is not
    counted twice -- double-counting one write would halve every gap and make a dead ledger
    look like it had a faster cadence than it ever had.
    """
    ts, bad = [], 0
    try:
        for ln in open(path, encoding='utf-8', errors='replace'):
            for m in STAMP.finditer(ln):
                iso, epoch = m.group(2), m.group(3)
                if iso:
                    v = isostamp.parse(iso)
                else:
                    try:
                        v = float(epoch)
                    except Exception:
                        v = None
                if v is None:
                    bad += 1
                    continue
                ts.append(v)
                break
    except Exception:
        return [], 0
    return ts, bad


def deps(src):
    """{basename: (readers, writers)} for every .jsonl, BOTH MEASURED OFF THE SYNTAX TREE.

    12 Oct, THE FOURTH AND FIFTH FAULTS, and they were in the column his 6 Oct order ranks by:

    (4) THE WRITER WAS IDENTIFIED BY FILENAME. `rows.jsonl` was assumed to be written by
        `rows.py`, which does not exist -- the actual writer is `build_open.py`, which was
        therefore counted as a READER and inflated the load this file ranks by. Convention is
        not a measurement. A writer is now a file that OPENS the artifact in a mode containing
        w, a or x, read off the AST, and the search found four artifacts that NOTHING IN THE
        TREE WRITES -- a class the stem rule could not express, because it can only ever answer
        "is there a file of that name".
    (5) A READER NAMING THE ARTIFACT BY FULL PATH WAS INVISIBLE. The exact-quote test
        (`'faults.jsonl'`) could not see `os.path.expanduser('~/bones-forge/watch/faults.jsonl')`
        -- so faults.py, which appends to it at line 37, was not even in its dependency list.
        The basename may now sit anywhere inside a string constant.

    AND THE PROSE-MENTION RULE SURVIVES, now exactly instead of approximately: a bare-expression
    string IS a docstring, which the tree can tell us and a quote-test cannot. So this file's own
    docstring may name every ledger it discusses without standing on one.
    """
    out = {}
    trees = {}
    UNPARSEABLE.clear()
    NOT_CONSUMERS.clear()
    for p, s in src.items():
        try:
            trees[p] = ast.parse(s)
        except SyntaxError as e:
            # AND A FILE THIS INTERPRETER CANNOT PARSE IS NOT A FILE THAT READS NOTHING. Under
            # the bus's Python 3.9, live_board.py (a backslash inside an f-string, legal from
            # 3.12) dropped out of the dependency graph entirely -- so clock_triangle.jsonl lost
            # its only reader and moved from `live` to `unread`, the apparatus bin that means
            # "nobody stands on this, its silence costs nothing". A SyntaxError in the SCANNER
            # was being reported as a fact about the ARTIFACT. Counted and named, never skipped.
            UNPARSEABLE.append((os.path.basename(p), e.msg, e.lineno))
            continue
    for a in sorted(glob.glob(os.path.join(W, '*.jsonl'))):
        b = os.path.basename(a)
        readers, writers = set(), set()
        for p, tree in trees.items():
            # A TOOL THAT READS A LEDGER TO TEST IT DOES NOT STAND ON IT. 12 Oct, caught the
            # moment dos_asientos.py was written: its job table names nine ledgers, and this
            # scan moved seven of them out of `unread` and into `live` -- from "nobody reads
            # this, so its silence costs nothing" to "something stands on this". Nothing had
            # started standing on them. Load is meant to count the STATEMENTS that go wrong if
            # the ledger goes stale, and a two-run comparison makes no statement from the
            # contents at all. So a file may DECLARE itself not a consumer, with an explicit
            # module-level flag -- never a name pattern, never a guess at intent -- and every
            # exclusion is printed so the column can be audited rather than trusted.
            if p in NOT_CONSUMERS or declares_not_consumer(tree):
                NOT_CONSUMERS.add(p)
                continue
            role = role_of(tree, b)
            if role == 'writer':
                writers.add(p)
            elif role == 'reader':
                readers.add(p)
        out[b] = (readers, writers)
    return out


def declares_not_consumer(tree):
    """True if the module sets VIGENCIA_NOT_A_CONSUMER = True at module level."""
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'VIGENCIA_NOT_A_CONSUMER' for t in n.targets):
            return isinstance(n.value, ast.Constant) and n.value.value is True
    return False


def role_of(tree, b):
    """'writer' | 'reader' | None -- ONE file's relationship to ONE artifact, off the tree.

    Kept separate from deps() so it can be handed planted sources and tested in BOTH
    directions; a detector that is only ever run on the real tree has no known-good seat.
    """
    docs = {id(n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str)}
    named = [n for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and id(n) not in docs and b in n.value]
    if not named:
        return None
    held = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                isinstance(x, ast.Constant) and isinstance(x.value, str) and b in x.value
                for x in ast.walk(n.value)):
            held |= {t.id for t in n.targets if isinstance(t, ast.Name)}
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not n.args:
            continue
        f = n.func
        fn = (f.id if isinstance(f, ast.Name)
              else f.attr if isinstance(f, ast.Attribute) else '')
        if fn != 'open':
            continue
        mode = ''
        if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
            mode = str(n.args[1].value)
        for kw in n.keywords:
            if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                mode = str(kw.value.value)
        if not any(c in mode for c in 'wax'):
            continue
        tgt = n.args[0]
        if any(isinstance(x, ast.Constant) and isinstance(x.value, str) and b in x.value
               for x in ast.walk(tgt)) or \
           any(isinstance(x, ast.Name) and x.id in held for x in ast.walk(tgt)):
            return 'writer'
    return 'reader'


SELFTEST = (
    # (expected role, source) -- the shape, then the shape it must NOT be confused with.
    ('writer', "L = os.path.join(W, 'x.jsonl')\nwith open(L, 'a') as f:\n    f.write('r')\n"),
    ('writer', "open('/home/me/bones-forge/watch/x.jsonl', 'a').write('r')\n"),
    ('writer', "open(P, mode='w')\nP = os.path.expanduser('~/w/x.jsonl')\n"),
    ('reader', "for l in open(os.path.join(W, 'x.jsonl')):\n    pass\n"),
    ('reader', "L = os.path.join(W, 'x.jsonl')\nR = [json.loads(l) for l in open(L)]\n"),
    # the write that is to a DIFFERENT file in a module that also reads ours -- build_open.py's
    # exact shape, and the one the stem rule got wrong
    ('reader', "ROWS = os.path.join(H, 'x.jsonl')\nfor l in open(ROWS):\n    pass\n"
               "open(OUT, 'w').write(doc)\n"),
    (None, '"""this docstring names x.jsonl to explain itself."""\nz = 1\n'),
    (None, "y = 2  # x.jsonl in a comment is not a dependency\n"),
)


def selftest():
    bad = 0
    for want, s in SELFTEST:
        got = role_of(ast.parse(s), 'x.jsonl')
        ok = got == want
        bad += 0 if ok else 1
        print('  %-4s want %-7s got %-7s  %s' % ('ok' if ok else 'FAIL', want, got,
                                                 s.split('\n')[0][:62]))
    print('  %d of %d' % (len(SELFTEST) - bad, len(SELFTEST)))
    return 1 if bad else 0


def read():
    tree = [p for p in sorted(glob.glob(os.path.join(W, '*.py')))
            if '.bak' not in p and '.pre-' not in p]
    src = {}
    for p in tree:
        try:
            src[p] = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            pass
    # THE WRITER IS NOT A READER, and which file that is, is now MEASURED -- see deps().
    D = deps(src)
    rows = []
    for a in sorted(glob.glob(os.path.join(W, '*.jsonl'))):
        b = os.path.basename(a)
        readers, writers = D.get(b, (set(), set()))
        load = len(readers)
        try:
            mtime_age = time.time() - os.path.getmtime(a)
        except Exception:
            continue
        ts, unparsed = stamps(a)
        # 12 Oct, CAUGHT BY THIS FILE ON ME WITHIN THE HOUR. I used the filesystem mtime as the
        # age, then restored calib.jsonl from a backup during a self-test -- the copy bumped its
        # mtime to now while its newest ROW stayed 27 h old, and the next scan called it live.
        # mtime is the OBSERVER's stamp (the filesystem's) and the newest row is the WITNESS's own
        # declaration, and the question here -- is anything still WRITING this -- is the witness's
        # to answer. A touch, a copy, a backup restore all move mtime without writing a row.
        # Both are kept and their disagreement is reported, because that gap IS the catch.
        age = (time.time() - max(ts)) if ts else mtime_age
        gaps = [ts[i] - ts[i - 1] for i in range(1, len(ts)) if ts[i] > ts[i - 1]]
        maxgap = max(gaps) if len(gaps) >= MIN_ROWS else None
        rows.append({
            'artifact': b, 'load': load, 'age': age, 'rows': len(ts),
            'mtime_age': mtime_age,
            # judged ONLY where the artifact can declare a cadence; red.jsonl was flagged off a
            # typed 60 s floor, which is the no_record bin answering a question it cannot answer
            'touched_not_written': bool(maxgap and (age - mtime_age) > maxgap),
            'median_gap': st.median(gaps) if len(gaps) >= MIN_ROWS else None,
            'maxgap': maxgap,
            'ratio': (age / maxgap) if maxgap else None,
            'past_record': bool(maxgap and age > maxgap),
            'writers': sorted(os.path.basename(x) for x in writers),
            'readers': sorted(os.path.basename(x) for x in readers),
            # ORPHANED IS NOT A FIFTH OUTCOME, it is a second axis, and conflating the two would
            # be the collapse this house refuses. An orphan can be live (written by a hand or by
            # something outside the tree) or dead, and the four outcomes still partition every
            # artifact exactly once. What it adds is WHY: a dead ledger with a writer has a
            # process that stopped, and a dead ledger with none has no process to restart.
            'orphan': bool(load > 0 and not writers),
            # A PARSE FAILURE IS NOT AN ABSENCE OF DATA. Kept as its own number so it can never
            # be absorbed by the cannot-tell bin, which is where it hid for 5.5 h -- see
            # isostamp.py for the eight bus runs that reported 16 no_record against 9.
            'unparsed': unparsed,
        })
    return rows


def bins(rows):
    """FOUR OUTCOMES. Ordered so the predicates are disjoint by construction: the apparatus bin
    is taken first, then the cannot-tell, and only what is left is judged live or dead."""
    from outcomes import Outcomes
    O = Outcomes(subject=[
        ('dead', lambda r: r['load'] > 0 and r['maxgap'] and r['past_record']),
        ('live', lambda r: r['load'] > 0 and r['maxgap'] and not r['past_record']),
        ('no_record', lambda r: r['load'] > 0 and not r['maxgap']),
    ], apparatus=[
        ('unread', lambda r: r['load'] == 0),
    ])
    return O.tally(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tick', action='store_true')
    ap.add_argument('--selftest', action='store_true',
                    help='the reader/writer detector against planted sources, both directions')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.tick:
        # ITS OWN LEASH. The scan measured 0.13 s; 120 s is 920x and sits well inside one tick.
        import tickguard
        tickguard.guard('vigencia', 120)

    rows = read()
    t = bins(rows)
    dead = [r for r in rows if r['load'] > 0 and r['maxgap'] and r['past_record']]
    dead.sort(key=lambda r: (-r['load'], -(r['ratio'] or 0)))
    rec = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'n_artifacts': len(rows),
           'bins': {k: len(v) if hasattr(v, '__len__') else v for k, v in t.items()},
           'dead': [{'artifact': r['artifact'], 'load': r['load'], 'age_h': r['age'] / 3600.0,
                     'maxgap': r['maxgap'], 'ratio': r['ratio']} for r in dead]}
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(rec) + '\n')
    except Exception:
        pass

    if a.tick:
        # SPEAKS ONCE PER CROSSING, per the no-bulletin rule. An artifact already known dead is a
        # standing fact and repeating it every tick is the bulletin he retired; what is news is an
        # artifact going PAST ITS OWN RECORD for the first time, or coming back.
        prev = set()
        try:
            prev = set(json.load(open(STATE)).get('dead', []))
        except Exception:
            pass
        now = set(r['artifact'] for r in dead)
        for r in dead:
            if r['artifact'] not in prev:
                print('VIGENCIA: %s has not been written for %.1f h -- past its OWN worst gap of '
                      '%.0f s by %.0fx, and %d file%s read it'
                      % (r['artifact'], r['age'] / 3600.0, r['maxgap'], r['ratio'],
                         r['load'], '' if r['load'] == 1 else 's'))
        for b in sorted(prev - now):
            print('VIGENCIA: %s is being written again' % b)
        try:
            json.dump({'at': rec['at'], 'dead': sorted(now)}, open(STATE, 'w'))
        except Exception:
            pass
        return 0

    print('  VIGENCIA -- every ledger in the watch tree against ITS OWN worst gap ever.')
    print('  A dead ledger raises no error. It serves its last row forever, and a file that is')
    print('  still there reads exactly like a file that is still true.\n')
    print('  %d artifacts' % len(rows))
    for k in sorted(t):
        print('    %-12s %d' % (k, len(t[k]) if hasattr(t[k], '__len__') else t[k]))
    print('\n  DEAD -- past its own record AND something reads it. Ranked by load, the hole most')
    print('  statements stand on. THIS FILE RESTARTS NOTHING: several are clock files and that')
    print('  lane is closed.')
    if dead:
        print('    %-26s %-5s %-9s %-11s %s' % ('artifact', 'load', 'age(h)', 'own maxgap', 'past by'))
        for r in dead:
            print('    %-26s %-5d %-9.1f %-11.0f %.0fx'
                  % (r['artifact'], r['load'], r['age'] / 3600.0, r['maxgap'], r['ratio']))
    else:
        print('    none. Every read ledger is inside the longest silence it has come back from.')
    live = [r for r in rows if r['load'] > 0 and r['maxgap'] and not r['past_record']]
    if live and dead:
        # NOT "THE POPULATIONS DO NOT TOUCH" -- that sentence was in this file an hour ago and it
        # was CIRCULAR. The bar IS ratio > 1, so a gap at 1.0 is the definition doing the work and
        # not a measurement. What is actually measured is how FAR past its record a dead ledger
        # sits: if the rule were only just separating, the dead would cluster at 1.1x.
        rs = sorted(r['ratio'] for r in dead)
        print('\n  HOW FAR PAST, which is the part the rule does not decide for itself: the bar is')
        print('  ratio > 1 BY DEFINITION, so a gap at 1.0 would prove nothing. Measured, %d of %d'
              % (sum(1 for v in rs if v >= 10), len(rs)))
        print('  dead ledgers sit at 10x their own record or worse (%s) -- they are not marginal.'
              % ', '.join('%.0fx' % v for v in reversed(rs)))
    tnw = [r for r in rows if r['touched_not_written']]
    if tnw:
        print('\n  TOUCHED BUT NOT WRITTEN -- mtime moved and no new row appeared. A copy, a touch')
        print('  or a backup restore does this, and it makes a dead ledger read as live:')
        for r in tnw:
            print('    %-26s newest row %.1f h old, file touched %.1f h ago'
                  % (r['artifact'], r['age'] / 3600.0, r['mtime_age'] / 3600.0))
    orph = sorted([r for r in rows if r['orphan']], key=lambda r: -r['load'])
    if orph:
        print('\n  ORPHANED -- something reads it and NOTHING IN THE TREE WRITES IT. A second axis,')
        print('  not a fifth outcome: the four bins above still hold each artifact exactly once.')
        print('  It changes what can be done, not how dead a file is -- a dead ledger with a')
        print('  writer has a process that stopped, and one with no writer has none to restart:')
        for r in orph:
            print('    %-26s load %d   %-9s reads: %s'
                  % (r['artifact'], r['load'],
                     'DEAD %.0fx' % r['ratio'] if r['past_record'] else
                     ('live' if r['maxgap'] else 'cannot-tell'),
                     ', '.join(r['readers'])))
    if UNPARSEABLE:
        print('\n  THE SCANNER COULD NOT PARSE %d FILE(S) under %s, so their dependencies are'
              % (len(UNPARSEABLE), sys.version.split()[0]))
        print('  MISSING FROM EVERY LOAD COUNT ABOVE -- a fault in this reader, not in any artifact:')
        for nm, msg, ln in UNPARSEABLE:
            print('    %-26s line %s: %s' % (nm, ln, msg))
    if NOT_CONSUMERS:
        print('\n  NOT COUNTED AS READERS -- %d file(s) DECLARE they read ledgers only to test'
              % len(NOT_CONSUMERS))
        print('  them, so they are excluded from every load above. Printed so the column can be')
        print('  audited rather than trusted: %s'
              % ', '.join(sorted(os.path.basename(x) for x in NOT_CONSUMERS)))
    up = sorted([r for r in rows if r['unparsed']], key=lambda r: -r['unparsed'])
    if up:
        print('\n  UNPARSED -- rows carrying a stamp this reader could NOT read. Its own number,')
        print('  never folded into cannot-tell: the artifact HAS timestamps and the instrument')
        print('  failed on them, which is a statement about the reader. Running %s.'
              % sys.version.split()[0])
        for r in up:
            print('    %-26s %d unreadable stamp(s), %d readable' % (r['artifact'], r['unparsed'], r['rows']))
    nr = [r for r in rows if r['load'] > 0 and not r['maxgap']]
    print('\n  NO_RECORD -- %d read ledgers carry fewer than %d timestamped rows, so they cannot'
          % (len(nr), MIN_ROWS))
    print('  declare a cadence and this instrument CANNOT TELL. That is not a pass.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
