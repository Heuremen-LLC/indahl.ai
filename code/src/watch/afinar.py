#!/usr/bin/env python3
"""afinar.py -- OUR OWN FINDINGS, POINTED AT OUR OWN HOUSE. (Bones, 11 Oct 2026.)

Wayfinder, going to bed on 11 Oct: "run our seven against the system to see if we missed an area
to tune. our findings are the key man, use them to tune our shit. then check it all again."

THE FINDING THIS INSTRUMENT IS BUILT OUT OF, and it is ours, measured, twice in one night:

    11 Oct, EL TERCER RINCON: "REPRODUCIBILITY IS NOT ACCURACY -- 4 runs agreed to sd 2.82 ppm on
    a number that swept 355 ppm with a DEFAULT PARAMETER."

    11 Oct, THE BONEFISH HARNESS: tickguard kills bonefish_harness at 420 s while the harness
    allowed its hops2 child 600 s. Any run slower than 420 s died with the parent and wrote
    NOTHING -- 36 times -- behind a log line that reads like a designed outcome. The legs it was
    blamed on measure 0.5 to 3.1 s. The budget was never the constraint. THE ARITHMETIC WAS.

So the hole is not a missing measurement. It is a NUMBER NOBODY CHOSE. A default parameter is the
one object in the house that carries a result's full width while presenting as a detail, and the
reproducibility finding says four agreeing runs cannot see it. Nothing in this house looks for them.

WHAT THIS DOES NOT DO. It does not hunt a clock -- that lane is closed by his call on 11 Oct
("chasing you're own time tale"), and the whole spread of house crystal rates is 13.74 ppm against
conversions 6,065x outside it. It does not test the Seven against anything; el_miron.py owns the pi
band with its tolerance declared in advance and its 22 trials printed, and a second scorer on the
same numbers would be a second ruler built to agree. It reads PARAMETERS, not physics.

THE FOUR OUTCOMES, and one of them is exact.

    INCONSISTENT   ARITHMETIC, NOT JUDGMENT. A nested budget whose inner allowance is greater than
                   or equal to its outer ceiling. The inner can never be observed to finish, so the
                   reading it carries is unreachable by construction. This is the bin that catches
                   tonight's bug, and it needs no opinion about what a good timeout is.
    UNMEASURED     a budget with no measured basis anywhere near it. A TEXT READING, and it is named
                   as one below, because it reads comments rather than runs anything.
    MEASURED       a basis is cited at the constant: a number with a unit, or the word measured, or
                   a sweep, within a few lines.
    NOT-A-BUDGET   matched the pattern and is not one -- a port, a byte count, a year, a version.

RANKED BY LOAD, per his 6 Oct order: the hole most statements stand on, never the easy one. Load is
the count of files in the tree that import the carrier or read the artifact it writes, so a bad
default inside a script nothing reads is correctly reported as cheap.

AND THE TEXT READING IS NOT A MEASUREMENT. UNMEASURED and MEASURED are decided by reading source
comments. That is a heuristic over prose and it is the weaker half of this file; INCONSISTENT is
arithmetic over two integers in the same file and is the half worth acting on. Both are printed.
Never collapse them.

    python3 afinar.py                 # the full table
    python3 afinar.py --tick          # speaks ONLY when an INCONSISTENT budget exists, or the
                                      # unmeasured count changes. Silence = the house is unchanged.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'afinar.jsonl')
STATE = os.path.join(W, 'afinar_state.json')

# A BUDGET: a number that bounds how long something is allowed to take, or how far it may go
# before being cut. These are the names that carry a result's width while presenting as a detail.
# 12 Oct, FOUND BY USING IT: this pattern was CASE-SENSITIVE and required the budget word to be
# the WHOLE identifier, so it read `timeout=330` and was blind to `SSH_TIMEOUT = 25`. Module-level
# constants are conventionally UPPERCASE, which is to say the detector could not see the budgets
# most likely to be load-bearing. Writing bloque.py exposed it: six budgets in the file and this
# found ONE. Now the word may sit anywhere inside the identifier, in any case.
BUDGET = re.compile(
    r'\b([A-Za-z_]*(?:timeout|ceiling|deadline|max_min|max_sec|maxtime|budget|'
    r'rounds|n_pairs|min_gap_s|limit|window|seconds|clock_cache|minexp|kmax)[A-Za-z_0-9]*)\b'
    r'\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)', re.I)
# the time-like names, matched as a SUBSTRING now that the identifier may carry a prefix
TIMEISH = re.compile(r'(?i)timeout|deadline|max_sec|maxtime|budget|seconds|ceiling')
# the outer ceiling a file imposes on ITSELF
CEILING = re.compile(r'tickguard\.guard\(\s*[\'"][^\'"]+[\'"]\s*,\s*([0-9]+)')
# a cited basis: a measured number with a unit, or the words that mean somebody ran it
BASIS = re.compile(r'(?i)measured|timed|observed|\bsweep\b|per-leg|'
                   r'[0-9]+(?:\.[0-9]+)?\s*(?:ms|s\b|us|µs|ppm|GB|MB|H/s|cores)')
# matched the pattern and is not a budget
NOTBUDGET = re.compile(r'(?i)\bport\b|\bversion\b|^20[0-9][0-9]$|\bbytes\b|\bencoding\b')


def budgets(path):
    """every budget in one file, with its line, its basis window and the file's own ceiling."""
    try:
        src = open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return None, []
    lines = src.split('\n')
    c = CEILING.search(src)
    ceiling = int(c.group(1)) if c else None
    out = []
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith('#'):
            continue                      # a commented-out budget binds nothing
        for m in BUDGET.finditer(ln):
            name, val = m.group(1), float(m.group(2))
            lo, hi = max(0, i - 4), min(len(lines), i + 3)
            near = '\n'.join(lines[lo:hi])
            out.append({'name': name, 'value': val, 'line': i + 1,
                        'basis': bool(BASIS.search(near)),
                        'notbudget': bool(NOTBUDGET.search(ln)),
                        'text': ln.strip()[:120]})
    return ceiling, out


def load(path, tree):
    """how many files in the tree import this one or read the artifact it writes."""
    stem = os.path.basename(path)[:-3]
    arts = [stem + e for e in ('.jsonl', '.json', '_state.json')]
    n = 0
    for p in tree:
        if p == path:
            continue
        try:
            s = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        if re.search(r'\bimport\s+%s\b|\bfrom\s+%s\b' % (stem, stem), s) or any(a in s for a in arts):
            n += 1
    return n


def read():
    tree = sorted(glob.glob(os.path.join(W, '*.py')))
    tree = [p for p in tree if '.bak' not in p and '.pre-' not in p]
    rows = []
    for p in tree:
        ceiling, bs = budgets(p)
        if not bs:
            continue
        ld = load(p, tree)
        for b in bs:
            b = dict(b)
            b['file'] = os.path.basename(p)
            b['ceiling'] = ceiling
            # THE ARITHMETIC BIN: an inner allowance at or over the outer ceiling. 'rounds' and the
            # other count-like budgets are not seconds, so only time-like names are compared.
            b['inconsistent'] = bool(
                ceiling and TIMEISH.search(b['name']) and b['value'] >= ceiling)
            b['load'] = ld
            rows.append(b)
    return rows


def bins(rows):
    """FOUR OUTCOMES, EXHAUSTIVE AND DISJOINT, checked by outcomes.py rather than asserted here."""
    from outcomes import Outcomes
    O = Outcomes(subject=[
        ('inconsistent', lambda r: r['inconsistent']),
        ('measured', lambda r: not r['inconsistent'] and not r['notbudget'] and r['basis']),
        ('unmeasured', lambda r: not r['inconsistent'] and not r['notbudget'] and not r['basis']),
    ], apparatus=[
        ('not_a_budget', lambda r: not r['inconsistent'] and r['notbudget']),
    ])
    return O.tally(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tick', action='store_true')
    a = ap.parse_args()
    if a.tick:
        # ITS OWN LEASH, like every other tick job. The scan reads 62 files and takes about 5 s
        # measured, so 120 s is 24x headroom and still far inside one of her ticks.
        import tickguard
        tickguard.guard('afinar', 120)
    rows = read()
    t = bins(rows)
    bad = [r for r in rows if r['inconsistent']]
    un = [r for r in rows if not r['inconsistent'] and not r['notbudget'] and not r['basis']]
    un.sort(key=lambda r: (-r['load'], r['file']))
    rec = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'n_budgets': len(rows),
           'inconsistent': len(bad), 'unmeasured': len(un),
           'measured': sum(1 for r in rows if not r['inconsistent'] and not r['notbudget'] and r['basis']),
           'worst': [{'file': r['file'], 'line': r['line'], 'name': r['name'],
                      'value': r['value'], 'load': r['load']} for r in un[:12]],
           'bad': [{'file': r['file'], 'line': r['line'], 'name': r['name'],
                    'value': r['value'], 'ceiling': r['ceiling'], 'load': r['load']} for r in bad]}
    try:
        with open(LOG, 'a') as f:
            f.write(json.dumps(rec) + '\n')
    except Exception:
        pass

    if a.tick:
        # SPEAKS ONLY WHEN SOMETHING CHANGED STATE, per the no-bulletin rule. An INCONSISTENT budget
        # speaks every tick it exists, because it is arithmetic and it is costing readings right now.
        prev = {}
        try:
            prev = json.load(open(STATE))
        except Exception:
            pass
        say = []
        for r in rec['bad']:
            say.append('AFINAR: %s:%d allows its child %s=%g inside a %s s ceiling -- that reading '
                       'cannot be observed to finish (load %d)'
                       % (r['file'], r['line'], r['name'], r['value'], r['ceiling'], r['load']))
        if prev.get('unmeasured') is not None and rec['unmeasured'] != prev['unmeasured']:
            say.append('AFINAR: unmeasured budgets %d -> %d of %d'
                       % (prev['unmeasured'], rec['unmeasured'], rec['n_budgets']))
        for s in say:
            print(s)
        try:
            json.dump({'unmeasured': rec['unmeasured'], 'inconsistent': rec['inconsistent'],
                       'at': rec['at']}, open(STATE, 'w'))
        except Exception:
            pass
        return 0

    print('  AFINAR -- every budget in the watch tree, ranked by what stands on it')
    print('  THE FINDING THIS IS BUILT ON: a default parameter swept a result 355 ppm while four')
    print('  runs agreed to 2.82 ppm. A number nobody chose carries a full width as a detail.\n')
    print('  %d budgets in %d files' % (len(rows), len(set(r['file'] for r in rows))))
    for k, v in sorted(t.items()):
        print('    %-16s %d' % (k, len(v) if hasattr(v, '__len__') else v))
    print('\n  INCONSISTENT -- ARITHMETIC. inner allowance >= outer ceiling, so the inner can never')
    print('  be observed to finish. This is the bin that is worth acting on.')
    if bad:
        for r in bad:
            print('    %-26s line %-5d %s=%-7g ceiling %-5s load %d'
                  % (r['file'], r['line'], r['name'], r['value'], r['ceiling'], r['load']))
    else:
        print('    none. Every nested budget in the tree fits inside its own ceiling.')
    print('\n  UNMEASURED -- A TEXT READING, not a measurement: it reads comments, it runs nothing.')
    print('  Ranked by load: files that other files import or whose artifacts they read.')
    print('    %-26s %-6s %-18s %-9s %s' % ('file', 'line', 'budget', 'value', 'load'))
    for r in un[:16]:
        # 12 Oct: THIS PRINTED %.0f AND SHOWED calib.py's timeout=0.4 AS "0". A detector that
        # misdisplays a sub-second budget as zero invents a bug to chase -- the instrument wrong
        # about itself. %g keeps 0.4 as 0.4 and 330 as 330.
        print('    %-26s %-6d %-18s %-9g %d' % (r['file'], r['line'], r['name'], r['value'], r['load']))
    print('\n  AND NEITHER BIN IS THE OTHER. INCONSISTENT is two integers in one file. UNMEASURED is')
    print('  prose. A budget can be perfectly measured and still be wrong; this file cannot tell.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
