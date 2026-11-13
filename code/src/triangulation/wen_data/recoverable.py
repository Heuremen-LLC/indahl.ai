#!/usr/bin/env python3
"""recoverable.py -- CAN THE LABEL BE DERIVED FROM WHAT THE READER IS SHOWN? (Bones, 9 Oct 2026.)

Exists because the guard caught me quoting 93.79% twice from memory after reading it once. A figure I
retype is a figure that goes stale; a figure I run is not. This is the one command that answers it, so
there is nothing left to remember.
"""
import json, math, re, sys, time

T = 2.0
NUM = r'([+\-]\d+(?:\.\d+)?)'
PATS = [rf'reads {NUM} against its own error {NUM}', rf'end to end: {NUM}, error {NUM}',
        rf'came out {NUM} \+- {NUM}', rf'gives {NUM} with {NUM} of error', rf'gives {NUM} \+- {NUM}']


def w(k, n):
    p = k / n
    return 100 * p, 100 * math.sqrt(p * (1 - p) / n)


def physics(u):
    nc = re.search(rf'nearest candidate \S+ at {NUM}', u)
    ap = re.search(rf'the two candidates sit {NUM} apart', u)
    t = u.split('The claim:')[-1]
    m = next((x for x in (re.search(p, t) for p in PATS) if x), None)
    if not (nc and ap and m):
        return None
    v1 = float(nc.group(1)); gap = abs(float(ap.group(1)))
    r = float(m.group(1)); er = abs(float(m.group(2)))
    if er <= 0:
        return None
    if er >= abs(r):
        return 'NEXT'
    nw = abs(r - v1) / er; rw = gap / er
    return 'COMMIT' if (nw <= T and rw >= 2.0) else ('HOLD' if nw <= T else 'NEXT')


def synth(u):
    m1 = re.search(r'furthest two rulers sit ([\d.]+) widths apart', u)
    m2 = re.search(r'the reading moved ([\d.]+) widths', u)
    if not (m1 and m2):
        return 'NEXT'
    return 'HOLD' if (float(m1.group(1)) > 1.5 or float(m2.group(1)) > 2.0) else 'COMMIT'


def main():
    print(f'  RECOVERABLE -- read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}')
    print('  per case in the pool whose readings the parser can read\n')
    for f, fn in (('physics_train.jsonl', physics), ('physics_test.jsonl', physics),
                  ('train.jsonl', synth)):
        try:
            rows = [json.loads(l) for l in open(f) if l.strip()]
        except Exception as e:
            print(f'  {f:<22} unreadable: {e}'); continue
        ok = n = 0
        for r in rows:
            u = [m for m in r['messages'] if m['role'] == 'user'][0]['content']
            g = fn(u)
            if g is None:
                continue
            n += 1; ok += (g == (r.get('mode') or r.get('gold')))
        if not n:
            print(f'  {f:<22} nothing parseable'); continue
        p, se = w(ok, n)
        print(f'  {f:<22} {ok}/{n} = {p:.2f}% +- {se:.2f}pp')
    return 0


if __name__ == '__main__':
    sys.exit(main())
