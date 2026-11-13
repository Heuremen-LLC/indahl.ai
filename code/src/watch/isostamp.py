#!/usr/bin/env python3
"""isostamp.py -- ONE TIMESTAMP PARSER FOR THE HOUSE, because the bus runs a different Python
than the shell does. (Bones, 12 Oct 2026.)

FOUND BY READING vigencia.py'S OWN RECORD, not by suspecting it. Its ledger holds one row per
run, and eight consecutive bus runs between 02:28 and 08:01 reported ONE dead ledger where a
hand-run minutes later reported five. The bins in those rows are the measurement:

    on the bus      dead 1   live 3   no_record 16   unread 30
    in my shell     dead 5   live 9   no_record  9   unread 27

Seven artifacts that CAN declare a cadence were being filed as CANNOT TELL, and the cause is not
in any of our arithmetic:

    the shell       Python 3.14.7   /opt/homebrew/bin/python3
    the bus         Python 3.9.6    /Library/Developer/CommandLineTools/.../Python.app

and `datetime.fromisoformat` BEFORE 3.11 accepts only `+HH:MM`. Every one of these raises
ValueError under 3.9 and parses under 3.11+:

    2026-10-09T14:52:37-0400     a numeric offset with no colon -- calib.jsonl, audio_clock.jsonl
    2026-10-08T21:30-0400        the same, to the minute -- faults.jsonl
    2026-10-12T12:10:43.281Z     a Z -- her flywheel log

`rows.jsonl` writes a NAIVE stamp, `2026-10-07T22:45:27`, which 3.9 parses -- and that is the
whole reason it was the single survivor in all eight of those runs. The one artifact that looked
healthy looked healthy for a reason that had nothing to do with its health.

TWO FAULTS, AND THE SECOND IS THE ONE WORTH KEEPING:

    1. the parse was version-dependent, and the version was not ours to choose
    2. A BARE `except Exception: pass` AROUND A PARSE TURNS A FAILURE INTO AN ABSENCE. The file
       had timestamps. The reader could not read them. It reported "fewer than 4 timestamped
       rows, so this instrument CANNOT TELL" -- which is a true sentence about the reader and a
       false one about the artifact, and it is indistinguishable in the output from a genuinely
       unstampable file. So parse() never raises AND NEVER HIDES: callers get None and are
       expected to COUNT it, and vigencia now prints an UNPARSED line that no cannot-tell bin
       can absorb.

Nothing here is a clock. This reads stamps other files already wrote; it sets nothing, steers
nothing and does not compare two seats.

    python3 isostamp.py --selftest     # and run it under BOTH interpreters, which is the point
"""
import datetime
import re
import sys

# `2026-10-09T14:52:37-0400` -> `2026-10-09T14:52:37-04:00`, and a trailing Z -> `+00:00`.
# Applied BEFORE handing the string to the stdlib, so 3.9 and 3.14 see the same input.
_OFF = re.compile(r'([+-])([0-9]{2})([0-9]{2})$')


def parse(s):
    """epoch seconds (float) for an ISO-ish stamp, or None. NEVER RAISES, NEVER GUESSES.

    A naive stamp -- no offset at all -- is returned on the LOCAL clock, because every naive
    stamp in this house was written by a local `time.strftime` or `datetime.now()`. Reading it
    as UTC would silently shift it by the offset and make a fresh row look four hours stale.
    """
    if not isinstance(s, str):
        return None
    t = s.strip()
    if not t:
        return None
    if t.endswith('Z') or t.endswith('z'):
        t = t[:-1] + '+00:00'
    t = _OFF.sub(r'\1\2:\3', t)
    try:
        d = datetime.datetime.fromisoformat(t)
    except Exception:
        return None
    try:
        return d.timestamp()
    except Exception:
        return None


CASES = (
    # (input, must parse) -- the forms this house actually writes, read off the ledgers
    ('2026-10-09T14:52:37-0400', True),      # calib.jsonl, audio_clock.jsonl
    ('2026-10-08T21:30-0400', True),         # faults.jsonl, to the minute
    ('2026-10-12T12:10:43.281Z', True),      # her flywheel log
    ('2026-10-07T22:45:27', True),           # rows.jsonl, naive
    ('2026-10-09T14:52:37-04:00', True),     # the form 3.9 already accepted
    ('2026-10-12T08:11:04', True),           # two_twelve.json
    ('', False),
    (None, False),
    ('not a date', False),
    ('2026-13-45T99:99:99', False),          # shaped like one and is not one
)


def selftest():
    bad = 0
    for s, want in CASES:
        got = parse(s)
        ok = (got is not None) == want
        bad += 0 if ok else 1
        print('  %-4s %-28r -> %s' % ('ok' if ok else 'FAIL', s,
                                      ('%.0f' % got) if got else 'None'))
    # AND THE OFFSET MUST ACTUALLY BE HONOURED, not merely accepted: the same instant written
    # two ways must land on the same epoch, or the colon-stripping repair is cosmetic.
    a, b = parse('2026-10-09T14:52:37-0400'), parse('2026-10-09T18:52:37+00:00')
    same = a is not None and b is not None and abs(a - b) < 1e-6
    print('  %-4s -0400 and +00:00 forms of one instant agree' % ('ok' if same else 'FAIL'))
    bad += 0 if same else 1
    print('  %d of %d   (%s)' % (len(CASES) + 1 - bad, len(CASES) + 1, sys.version.split()[0]))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else 0)
