#!/usr/bin/env python3
"""withheld.py -- DOES A GENERATOR DECIDE ON A QUANTITY IT NEVER SHOWS? Read-only. (Bones, 9 Oct 2026.)

Wayfinder: "remember to hardcode your mistakes somewhere man, we need that trail to move forward...
nobody said shit about training on your fuckups.....kind of our story, isn't it bones?"
And my own outside rating, minutes earlier: the fault ledger RECORDS faults and does not CHECK me
against them. A file I do not read before writing is a diary, not a trail.

THE FAULT THIS CHECKS, found three times on 9 Oct in three different files:

    physics_cases.py   computed k1, v1, k2, v2 -- the rival candidate that is the ONLY difference
                       between COMMIT and HOLD -- and left all four out of the readings.
    gen_train.py       computed `split` and `moved` in widths, branched the label on them, and put
                       neither on the page. Its own comment had said since 6 Oct that the label is
                       "decided by arithmetic on our numbers".
    seven_cases.py     the same label() shape, same omission.

    THE SHAPE: a variable is computed, the verdict branches on it, and its value never reaches the
    text the reader is shown. The question withholds the fact that decides it. Measured cost: every
    seat on every pod scored 0/29 on the kind that needed the withheld number, and 0/400 on two
    physics kinds, matched exactly by an UNTRAINED control -- the signature of a question with no
    answer in it.

HOW IT LOOKS: for every function, find the names that appear in a branch condition which assigns a
label-ish variable (mode/kind/verdict/gold/label), then check whether that name's VALUE is ever
interpolated into a string in the same function. A name used only in the condition and never shown
is a withheld quantity.

IT CANNOT PROVE INNOCENCE. A name may be shown under another spelling, or the value may be implied by
two numbers that ARE shown. This flags candidates for a human read; it does not grade them.

    python3 withheld.py
"""
import ast
import glob
import os
import sys

ROOTS = [os.path.expanduser('~/bones-forge/triangulation/wen_data'),
         os.path.expanduser('~/bones-forge/watch')]
LABELY = {'mode', 'kind', 'verdict', 'gold', 'label', 'why', 'state'}
SKIP = ('.bak', '/qvenv/', 'site-packages', 'withheld.py')


# 9 Oct: THE DETECTOR FAILED ITS OWN LADDER, 0 of 3, and the reason is the whole point. In
# gen_train.py the withheld quantity `split` IS interpolated into a string -- the `why` string -- so a
# naive "is it shown anywhere" test counts it as shown. But `why` is metadata: it explains the label to
# the log and never reaches the reader. The generator tells ITSELF the answer and withholds it from the
# question. So a string only counts as SHOWN if it is not an explanation.
EXPLAIN = {'why', 'reason', 'rationale', 'note', 'explanation', 'detail', 'msg', 'log'}


def _in_explanation(node, fn):
    """is this formatted value inside an assignment to why/reason/..., or a dict value for such a key?"""
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            names = set()
            for t in n.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
                if isinstance(t, ast.Tuple):
                    names |= {e.id for e in t.elts if isinstance(e, ast.Name)}
            if names & EXPLAIN and node in set(ast.walk(n.value)):
                return True
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and str(k.value).lower() in EXPLAIN:
                    if node in set(ast.walk(v)):
                        return True
        if isinstance(n, ast.Call):
            for kw in n.keywords:
                if kw.arg and kw.arg.lower() in EXPLAIN and node in set(ast.walk(kw.value)):
                    return True
    return False


def shown_names(fn):
    """every name whose VALUE reaches a string A READER SEES -- explanations do not count."""
    out = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.FormattedValue):
            if _in_explanation(n, fn):
                continue
            for sub in ast.walk(n.value):
                if isinstance(sub, ast.Name):
                    out.add(sub.id)
        # .format(a=x) and % (x,) also count as showing
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'format':
            for a in list(n.args) + [k.value for k in n.keywords]:
                for sub in ast.walk(a):
                    if isinstance(sub, ast.Name):
                        out.add(sub.id)
    return out


def deciding_names(fn):
    """names appearing in the test of an `if` whose body assigns something label-ish."""
    out = set()
    for n in ast.walk(fn):
        if not isinstance(n, ast.If):
            continue
        assigns = set()
        for b in list(n.body) + list(n.orelse):
            for sub in ast.walk(b):
                if isinstance(sub, ast.Assign):
                    for t in sub.targets:
                        if isinstance(t, ast.Name):
                            assigns.add(t.id)
                        if isinstance(t, ast.Tuple):
                            assigns |= {e.id for e in t.elts if isinstance(e, ast.Name)}
                if isinstance(sub, ast.Return):
                    assigns.add('__return__')
        if not (assigns & LABELY or '__return__' in assigns):
            continue
        for sub in ast.walk(n.test):
            if isinstance(sub, ast.Name):
                out.add(sub.id)
    return out


def computed_names(fn):
    """names assigned from an expression that does arithmetic -- i.e. derived, not handed in."""
    out = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.BinOp, ast.Call, ast.IfExp)):
            has_math = any(isinstance(s, ast.BinOp) for s in ast.walk(n.value))
            if not has_math:
                continue
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out.add(t.id)
    return out


def main():
    print('  WITHHELD -- a quantity the verdict branches on that the reader never sees')
    print('  candidates only. A name may be shown under another spelling; this does not grade.\n')
    hits = 0
    for root in ROOTS:
        for p in sorted(glob.glob(os.path.join(root, '*.py'))):
            if any(s in p for s in SKIP):
                continue
            try:
                tree = ast.parse(open(p, encoding='utf-8').read())
            except Exception:
                continue
            for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef,))]:
                dec = deciding_names(fn)
                comp = computed_names(fn)
                shown = shown_names(fn)
                withheld = sorted((dec & comp) - shown)
                if not withheld:
                    continue
                hits += 1
                rel = p.replace(os.path.expanduser('~'), '~')
                print(f'  {rel}:{fn.lineno}  {fn.name}()')
                print(f'      decides on and never shows: {", ".join(withheld)}')
    if not hits:
        print('  NOTHING FLAGGED across every generator read.')
    else:
        print(f'\n  {hits} function(s) flagged. Each one is a question that may be withholding the')
        print('  fact that answers it. Read them; the three found by hand on 9 Oct all looked like this.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
