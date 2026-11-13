#!/usr/bin/env python3
"""bonefish_harness.py -- IS THE HOUSE ACTUALLY USING THE BONEFISH? (Bones, 9 Oct 2026.)

Wayfinder: "be The Bonefish" / "go for harness."

A harness that nothing is bolted to is a module, not a harness. So this reads every script in watch/
that reports a match and says which rulers it actually applies -- because twelve scripts carrying
twelve private candidate pools is twelve different answers to the same question, and the pool is what
sets the cheapness.

WHAT IT CHECKS, one column per ruler the sheet names:
    POOL      does it import bonefish, or carry its own candidate dict?
    WIDTH     does it compute a width before laying a constant beside a value? (THE REGLA)
    RUNNER-UP does it print the second-nearest candidate? (THE EXCLUSION WIDTH)
    CHEAP     does it price the match against the pool's own rate?
    K         does it put the reading on the landing profile?
    NONE      does it name its none, or is zero doing that job?

A script with its own pool is not wrong -- a pool chosen for one axis is often the right pool. It is
UNCOMPARABLE, which is the thing worth knowing: two matches priced against different pools cannot be
ranked against each other, and ranking them is exactly what we do all evening.

NOTHING IS REWRITTEN BY THIS. It reports. The conversions are mine to make one at a time, with a read
of what each pool was for.

    python3 bonefish_harness.py
    python3 bonefish_harness.py --tick      one accumulating reading, for her tick bus
"""
import argparse
import glob
import json
import math
import os
import re
import statistics as st
import subprocess
import sys
import time

W = os.path.expanduser('~/bones-forge/watch/')
sys.path.insert(0, W)
LOG = os.path.join(W, 'bonefish_harness.jsonl')

CHECKS = {
    'POOL': (r'\bimport bonefish\b|\bfrom bonefish\b', r"^\s*(POOL|R|C|CAND|RULERS)\s*=\s*\{"),
    'WIDTH': (r'\bsem\b|\bstdev\b|_width|\bwidth\b', None),
    'RUNNER-UP': (r'runner.?up|second\b|ranked\[1\]|rk\[1\]', None),
    'CHEAP': (r'cheap', None),
    'K': (r'\blanding\b|\bK\(', None),
    'NONE': (r'the none|THE NONE|null\b|no_?ne\b', None),
}


def scan():
    out = []
    for p in sorted(glob.glob(os.path.join(W, '*.py'))):
        b = os.path.basename(p)
        if b.startswith('bonefish_harness'):
            continue
        try:
            s = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        # ONLY SCRIPTS THAT ACTUALLY LAY A CONSTANT BESIDE A VALUE, and the first version of this
        # gate was a bare substring search that flagged live_board.py twice: `\bpi\b` matched the
        # hostname `flock-pi` and a status key `pi_mining`, and the "own pool" was `C = {...}`, an
        # ANSI colour table. A scanner that names innocent files is worse than no scanner, because
        # the list gets acted on. So both halves are now required:
        #   a CONSTANT, written as a number or as an expression that evaluates to one, AND
        #   a RELATIVE COMPARISON, abs(a - b) / b, which is what laying a constant beside a value is.
        has_const = re.search(
            r'math\.pi|\(1 \+ 5 \*\* 0?\.5\)|1\.6180|0\.6180|3\.14159|0\.31830|'
            r'12 ?/ ?11|1 ?/ ?12|2\.65|\bPHI\b|\bSEVEN\b|ladder\(', s)
        has_cmp = re.search(r'abs\([^)]*-[^)]*\)\s*/|/ ?\w+\s*[<>]=?\s*\w*TOL|nearest|runner.?up', s)
        if not (has_const and has_cmp):
            continue
        row = {'file': b, 'bytes': len(s)}
        for k, (yes, own) in CHECKS.items():
            hit = bool(re.search(yes, s, re.M))
            row[k] = hit
            if own:
                row['own_pool'] = bool(re.search(own, s, re.M))
        out.append(row)
    return out


def tick():
    """ONE ACCUMULATING READING, so the split grows on her ticks and never on a clock."""
    # THE CHILD MUST FIT INSIDE THE PARENT'S CEILING, AND FOR 36 RUNS IT DID NOT.
    # tickguard kills this process at 420 s while this line allowed its child 600 -- so any
    # run slower than 420 s died with the parent and the reading was never written, 36 times,
    # behind a message that reads like a designed outcome ("that is the reading"). The legs
    # themselves measure 0.5-3.1 s, so the budget was never the constraint; the ARITHMETIC was.
    # 330 s leaves 90 s for the fit and the append, which take milliseconds.
    r = subprocess.run([sys.executable, os.path.join(W, 'bonefish_hops2.py'), '--rounds', '6'],
                       capture_output=True, text=True, timeout=330, cwd=W)
    try:
        R = [json.loads(l) for l in open(os.path.join(W, 'bonefish_hops2.jsonl')) if l.strip()]
    except Exception:
        return 1
    pts = []
    for rr in R:
        L = rr.get('legs', {})
        al, pl, ap = L.get('ARMATURE->LAPTOP'), L.get('PI->LAPTOP'), L.get('ARMATURE->PI')
        if al and pl and ap:
            pts.append((ap['off_ms'], (al['off_ms'] - pl['off_ms']) - ap['off_ms']))
    if len(pts) < 3:
        return 1
    import bonefish as BF
    xs, ys = [a for a, _ in pts], [b for _, b in pts]
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    P = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx if sxx else 0.0
    S = my - P * mx
    res = [b - (S + P * a) for a, b in zip(xs, ys)]
    rms = math.sqrt(sum(e * e for e in res) / max(n - 2, 1))
    Pw = rms / math.sqrt(sxx) if sxx else float('inf')
    Sw = rms * math.sqrt(1 / n + mx * mx / sxx) if sxx else float('inf')
    row = BF.row(abs(P), Pw, 'P, the per-crossing fraction',
                 axis='small' if abs(P) < 0.12 else 'ratio')
    rec = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'n': n, 'S': S, 'S_width': Sw,
           'S_widths': abs(S) / Sw if Sw else None, 'P': P, 'P_width': Pw,
           'P_widths': abs(P) / Pw if Pw else None, 'rms': rms, 'row': row}
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    # a tick job speaks only when something changed state, per the no-bulletin rule
    if rec['P_widths'] and rec['P_widths'] >= 3 and not row['separable']:
        print(f"BONEFISH: P is {rec['P_widths']:.2f} widths at n={n} and still not separable from "
              f"{row['second']} -- the width, not the sample, is the binding constraint")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tick', action='store_true')
    a = ap.parse_args()
    if a.tick:
        return tick()
    S = scan()
    print('  IS THE HOUSE USING THE BONEFISH -- one column per ruler the sheet names')
    print(f'  read {time.strftime("%H:%M:%S %Z, %-d %b %Y")}, {len(S)} scripts that lay a constant '
          f'beside a value\n')
    ks = list(CHECKS)
    print(f"  {'script':<26}" + ''.join(f'{k:>11}' for k in ks) + f"{'own pool':>10}")
    for r in S:
        print(f"  {r['file']:<26}"
              + ''.join(f"{('yes' if r[k] else '-'):>11}" for k in ks)
              + f"{('YES' if r.get('own_pool') else '-'):>10}")
    using = [r for r in S if r['POOL']]
    own = [r for r in S if r.get('own_pool') and not r['POOL']]
    nocheap = [r for r in S if not r['CHEAP']]
    norunner = [r for r in S if not r['RUNNER-UP']]
    print(f"\n  {len(using)} of {len(S)} import The Bonefish.")
    print(f"  {len(own)} carry their OWN candidate pool and do not: "
          f"{', '.join(r['file'] for r in own) if own else 'none'}")
    print(f"    a private pool is not wrong -- it is UNCOMPARABLE. Two matches priced against two")
    print(f"    pools cannot be ranked against each other, and ranking them is what we do all evening.")
    print(f"  {len(nocheap)} lay a constant beside a value with NO cheapness: "
          f"{', '.join(r['file'] for r in nocheap) if nocheap else 'none'}")
    print(f"  {len(norunner)} never print the runner-up: "
          f"{', '.join(r['file'] for r in norunner) if norunner else 'none'}")
    print(f"\n  THE ORDER TO CONVERT, by how many statements stand on each: whichever of the above")
    print(f"  feeds a published page or a board first, because an uncomparable cheapness on a page")
    print(f"  is a number somebody else will rank.")
    try:
        with open(os.path.join(W, 'bonefish_harness_scan.json'), 'w') as f:
            json.dump({'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'scripts': S}, f, indent=1)
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    # ONE COPY, AND A HARD CEILING INSIDE HER WINDOW. tick_bus launches this with a bare Popen -- no
    # timeout, no wait -- and three of her ticks is about 762 s, so a job that runs longer overlaps
    # the next copy and two of them ssh the same hosts at once. 420 s is the ceiling; a second copy
    # skips rather than queues.
    import tickguard
    tickguard.guard('bonefish_harness', 420)
    raise SystemExit(main())
