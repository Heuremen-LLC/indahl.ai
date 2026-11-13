#!/usr/bin/env python3
"""faults.py -- the fault ledger (Bones, 8 Oct 2026).

Wayfinder: "log your faults bro, we learned thats how you build everything."

WHY A LEDGER AND NOT PROSE. Faults already get written up -- in el-rastro.pdf, in docstrings, in the
osteography. Prose cannot be counted, so it cannot answer the only questions that matter about a fault:
is this one new, how many of them are the SAME fault, and WHO caught it. The repeat-offender guard was
built on 8 Oct because one stale value was caught five times with no escalation; this is that same lesson
applied to me instead of to a number.

THE COLUMN THAT COSTS THE MOST IS 'caught_by'. A fault I found myself is a working check. A fault Wayfinder
found is a check that does not exist. A fault found by a children's novel is neither.

    python3 faults.py              # the counts
    python3 faults.py --add        # append rows from stdin as json lines
"""
import collections, json, os, sys

LEDGER = os.path.expanduser('~/bones-forge/watch/faults.jsonl')


def rows():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for ln in open(LEDGER):
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def main():
    if '--add' in sys.argv:
        n = 0
        with open(LEDGER, 'a') as f:
            for ln in sys.stdin:
                if ln.strip():
                    json.loads(ln); f.write(ln if ln.endswith('\n') else ln + '\n'); n += 1
        print(f'  {n} rows appended, {len(rows())} total')
        return
    r = rows()
    if not r:
        print('  no ledger yet'); return
    print(f'  THE FAULT LEDGER -- {len(r)} rows')
    by = collections.Counter(x['caught_by'] for x in r)
    cl = collections.Counter(x['klass'] for x in r)
    print(f'\n  WHO CAUGHT IT   (a fault I caught is a working check; one Wayfinder caught is a missing one)')
    for k, v in by.most_common():
        print(f'      {v:3d}  {k}')
    print(f'\n  CLASS           (a class with more than one row is a HABIT, not a slip)')
    for k, v in cl.most_common():
        print(f'      {v:3d}  {k}' + ('   <-- REPEAT' if v > 1 else ''))
    rep = [k for k, v in cl.items() if v > 1]
    print(f'\n  {len(rep)} of {len(cl)} classes repeat. Those are the ones a check has to exist for.')
    for x in r:
        if x['klass'] in rep:
            pass
    mine = by.get('bones', 0)
    print(f"  self-caught {mine}/{len(r)} = {100*mine/len(r):.0f}%  -- the rest were caught by someone or "
          f"something outside me, and each of those is a check this house does not have.")


if __name__ == '__main__':
    main()
