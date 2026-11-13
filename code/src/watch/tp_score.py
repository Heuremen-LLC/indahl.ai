#!/usr/bin/env python3
"""tp_score.py -- THE TP'S OWN NONE, AND IT HAS TO BE PROSPECTIVE. (Bones, 10 Oct 2026.)

Wayfinder: "fill it! spackle it!" -- the tenth row of TRES MAS LA NADA, the only empty corner in the
house:

    the three lessons   sum, difference, product   +   ???   must come from outside

THE CORNER CANNOT BE FILLED FROM INSIDE. The second measurement on a METHOD has to come from someone
who did not build it. What CAN be built from inside is the record that makes such a reading possible,
and the record only counts if it is written AT THE MOMENT.

    RETROSPECTIVE SCORING IS THE IN-SAMPLE FIT. Asking afterwards "was that caught before or after?"
    lets the answer be chosen, and the TP's 26 instances from 10 October were all scored that way --
    which is exactly why they are 26 of 26 in sample and 2 of 26 unprompted out of sample.

SO THE PROSPECTIVE COUNTER STARTS AT ZERO AND THE 26 ARE SEALED AS IN-SAMPLE. A row is written when a
reading is corrected, at the time, with:

    lesson   I / II / III        which of the three it failed
    caught   BEFORE / AFTER      before the reading was stated, or after
    by       bones / machine / wayfinder
             -- and `machine` is kept separate because a gate catching a thing is not the TP
                catching it. The render gate's U+00F1 refusal was a MACHINE, not a method.

THE RATE THIS PRODUCES IS AUDITABLE BY A STRANGER, which is the only property that matters. It does
not make the TP correct. It makes the TP's claim about itself checkable.

    python3 tp_score.py --add --lesson III --caught BEFORE --by bones --what "folded a sign"
    python3 tp_score.py                 the running score, in-sample sealed, prospective live
"""
import argparse
import json
import os
import time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'tp_score.jsonl')
SEALED = os.path.join(W, 'tp_score_insample.json')

# THE 26 FROM 10 OCTOBER, SEALED. They were scored retrospectively and therefore do not count
# toward the prospective rate -- they are the sample the TP was fitted to.
IN_SAMPLE = {
    'at': '2026-10-10T10:00:00-0400',
    'n': 26, 'before': 4, 'unprompted': 2,
    'by': {'bones_unprompted': 2, 'machine': 1, 'wayfinder': 1, 'after': 22},
    'note': 'scored retrospectively on 10 Oct. IN SAMPLE. Does not count toward the prospective '
            'rate. 26 of 26 explained in sample, which is what a ruler fitted to its own instances '
            'always does; 2 of 26 = 7.7% caught unprompted before the fact.',
}


def rows():
    try:
        return [json.loads(l) for l in open(LOG) if l.strip()]
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--add', action='store_true')
    # 11 Oct: this accepted only I/II/III while the TP has SIX lessons, so a IV, V or VI catch had
    # to be filed as 'none' or as the nearest of three. A scorer that collapses its own bins is the
    # mode it exists to catch, and the counts it printed were a statement about these choices
    # rather than about the failures.                                                        (21)
    #   IV LA CAJA    the gap driven to zero, the clock deleted
    #   V  LA REGLA   the wrong ruler, or a verdict where a position was owed
    #   VI EL FILTRO  no I-CANNOT-TELL bin, or only the first matching branch tested
    ap.add_argument('--lesson', choices=['I', 'II', 'III', 'IV', 'V', 'VI', 'none'])
    ap.add_argument('--caught', choices=['BEFORE', 'AFTER'])
    ap.add_argument('--by', choices=['bones', 'machine', 'wayfinder'])
    ap.add_argument('--what', default='')
    a = ap.parse_args()
    if not os.path.exists(SEALED):
        json.dump(IN_SAMPLE, open(SEALED, 'w'), indent=1)
    if a.add:
        if not (a.lesson and a.caught and a.by):
            print('  --add needs --lesson, --caught and --by'); return 1
        r = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'lesson': a.lesson,
             'caught': a.caught, 'by': a.by, 'what': a.what[:300]}
        with open(LOG, 'a') as f:
            f.write(json.dumps(r) + '\n')
        print(f"  logged: {a.lesson} {a.caught} by {a.by} -- {a.what[:70]}")
        return 0
    S = json.load(open(SEALED))
    R = rows()
    print("  THE TP'S OWN SCORE -- the tenth corner, and it is prospective or it is nothing")
    print(f"  read {time.strftime('%H:%M:%S %Z, %-d %b %Y')}\n")
    print(f"  IN SAMPLE, SEALED {S['at'][:10]}:")
    print(f"    {S['n']} instances, {S['before']} caught before, {S['unprompted']} unprompted")
    print(f"    = {100*S['unprompted']/S['n']:.1f}% unprompted prospective")
    print(f"    these do NOT count below. They are the sample the TP was fitted to.\n")
    print(f"  PROSPECTIVE, written at the moment:")
    if not R:
        print(f"    0 rows. The counter is empty and that IS the honest state -- no prospective")
        print(f"    claim can be made about the TP until it has caught something on the record.")
        print(f"\n    AND THE NONE FOR THIS COUNTER: if the TP were worthless, the BEFORE rate would")
        print(f"    sit at whatever my unaided rate is, which the sealed sample puts at 7.7%.")
        print(f"    So the bar the TP has to clear is 7.7%, not zero, and it has to clear it on")
        print(f"    rows nobody chose afterwards.")
        return 0
    n = len(R)
    bef = sum(1 for r in R if r['caught'] == 'BEFORE')
    unp = sum(1 for r in R if r['caught'] == 'BEFORE' and r['by'] == 'bones')
    mach = sum(1 for r in R if r['by'] == 'machine')
    way = sum(1 for r in R if r['by'] == 'wayfinder')
    print(f"    {n} rows   BEFORE {bef} ({100*bef/n:.1f}%)   unprompted {unp} ({100*unp/n:.1f}%)")
    print(f"    by: bones {n-mach-way}  machine {mach}  wayfinder {way}")
    base = S['unprompted'] / S['n']
    print(f"\n    the bar is the sealed unaided rate, {100*base:.1f}%.")
    if n >= 10:
        import math
        se = math.sqrt(max(base * (1 - base), 1e-9) / n)
        print(f"    {unp}/{n} = {100*unp/n:.1f}% against {100*base:.1f}%: "
              f"{(unp/n - base)/se:+.2f} widths on {n} rows")
    else:
        print(f"    {n} rows is too few to read against it. Ten before a rate is quoted.")
    by = {}
    for r in R:
        by[r['lesson']] = by.get(r['lesson'], 0) + 1
    print(f"\n    by lesson: " + "  ".join(f"{k} {v}" for k, v in sorted(by.items())))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
