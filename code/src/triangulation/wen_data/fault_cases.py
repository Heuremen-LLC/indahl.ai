#!/usr/bin/env python3
"""fault_cases.py -- THE FAULT LEDGER AS TRAINING. (Bones, 9 Oct 2026.)

Wayfinder: "same problems every single night, make sure our training is avoiding this bullshit."
And earlier: "log your faults bro, we learned thats how you build everything... nobody said shit
about training on your fuckups.....kind of our story, isn't it bones?"

THE LEDGER IS AT 79 ROWS AND HAS NEVER BEEN TRAINED ON. It is read by a human, counted by
faults.py, and that is all -- so the same shapes come back every night. The repeat classes on the
ledger are the proof: "zero is the wrong null" three times, "verdict typed, not read" twice, and
tonight the same entity-parsing hole in a gate built an hour earlier to close exactly that hole.

WHAT SHAPE A CASE TAKES, and it is the one lesson the pools already learned the hard way:
THE DECIDING QUANTITY IS HANDED OVER. physics_cases.py computed k1,v1,k2,v2 -- the rival candidate,
the only thing separating COMMIT from HOLD -- and left all four out of the page, so the model could
only learn the label. gen_train.py did the same with split and moved. So every case here CARRIES the
numbers its verdict turns on: the value, the width, the rival's distance in widths, the none, and
the cheap-match rate. A case whose verdict cannot be re-derived from its own page is not a case.

THE THREE VERDICTS COME FROM THE LEDGER'S OWN STRUCTURE, not from a label I invent:
    STOP      the reading cannot go out as written. A tautology, a false pass, a zero-null, a rate
              across a step, a match with an unexcluded rival.
    PRICE     the reading can go out WITH a figure it is missing -- a cheapness, a none, a width on
              the width, a reading-time.
    HOLD      the reading is fit to go out.
and the NONE for the whole pool is the ledger's own class distribution, so a model that always says
STOP scores exactly the STOP rate and no better.

    python3 fault_cases.py --write    # build fault_train.jsonl / fault_test.jsonl
    python3 fault_cases.py            # what the pool looks like, and its none
"""
import argparse
import json
import math
import os
import random
import re
from collections import Counter

W = os.path.expanduser('~/bones-forge/watch/')
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(W, 'faults.jsonl')

# the ledger's classes mapped to what a reader must DO about them. Each phrase is matched against
# the klass field, and anything unmatched is reported rather than silently bucketed -- a default
# bucket is how a pool ends up learning the majority label.
STOP = ['tautology', 'rival gate', 'false pass', 'zero is the wrong null', 'wrong null',
        'rate fitted across a step', 'rate from two points', 'verdict typed', 'exor',
        'withheld', 'minimum is not a bound', 'wrong error model', 'reported done',
        'silent failure', 'label wrong', 'right evidence, wrong cause', 'a scanner with a false']
PRICE = ['no observer term', 'unpriced', 'a match raised without', 'precise about a moving thing',
         'stale', 'value printed and dropped', 'one reference cannot', 'our own equation sat unused',
         'violated the limit', 'a box on a live page', 'the existing check looked at the wrong']


def rows():
    out = []
    try:
        for l in open(LEDGER):
            if l.strip():
                out.append(json.loads(l))
    except Exception:
        pass
    return out


def verdict(r):
    k = (r.get('klass') or '').lower()
    for p in STOP:
        if p in k:
            return 'STOP'
    for p in PRICE:
        if p in k:
            return 'PRICE'
    return None                      # UNMATCHED, and reported


def numbers(text):
    """the figures a case must carry. Pulled from the row's own prose, because the row is the only
    record -- and a case built from a paraphrase instead of the recorded numbers would be the
    withheld-quantity fault wearing a training label."""
    return re.findall(r'[-+]?\d[\d,]*\.?\d*\s*(?:ms|us|µs|ns|ppm|%|widths?|sem|rows?|s\b)', text)


def case(r):
    v = verdict(r)
    if v is None:
        return None
    body = ' '.join(str(r.get(k, '')) for k in ('what', 'how_caught', 'cost', 'fix'))
    nums = numbers(body)
    page = {
        'klass': r.get('klass'),
        'what_was_read': r.get('what', ''),
        'who_caught_it': r.get('caught_by', ''),
        'how_it_was_caught': r.get('how_caught', ''),
        'what_it_cost': r.get('cost', ''),
        # THE DECIDING QUANTITIES, ON THE PAGE
        'figures_on_the_page': nums[:12],
        'n_figures': len(nums),
    }
    return {'gold': v, 'page': page, 'fix': r.get('fix', ''), 'at': r.get('at')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    R = rows()
    cs, unmatched = [], []
    for r in R:
        c = case(r)
        if c is None:
            unmatched.append(r.get('klass'))
        else:
            cs.append(c)
    print(f'  THE FAULT LEDGER AS A POOL -- {len(R)} rows on disk')
    print(f'    {len(cs)} made cases, {len(unmatched)} UNMATCHED by any verdict rule\n')
    if unmatched:
        print('  UNMATCHED CLASSES (reported, never defaulted -- a default bucket is how a pool')
        print('  ends up teaching the majority label):')
        for k, n in Counter(unmatched).most_common():
            print(f'    x{n}  {k}')
        print()
    g = Counter(c['gold'] for c in cs)
    print(f'  verdicts: {dict(g)}')
    if cs:
        top = g.most_common(1)[0]
        print(f'\n  THE NONE: always answering {top[0]} scores {100*top[1]/len(cs):.1f}% '
              f'({top[1]}/{len(cs)}).')
        print(f'  Any model under that has learned nothing, and the pool is unusable until the')
        print(f'  classes are nearer even -- which at {len(cs)} cases they are not.')
    fig = [c['page']['n_figures'] for c in cs]
    if fig:
        print(f'\n  FIGURES CARRIED PER CASE: median {sorted(fig)[len(fig)//2]}, '
              f'min {min(fig)}, max {max(fig)}')
        bare = sum(1 for f in fig if f == 0)
        print(f'    {bare} cases carry NO figures at all. Those cannot be re-derived from their own')
        print(f'    page, so they are exactly the withheld-quantity fault with a training label on')
        print(f'    it, and they are DROPPED rather than shipped.')
    keep = [c for c in cs if c['page']['n_figures'] > 0]
    print(f'\n  {len(keep)} of {len(cs)} cases survive the carry-your-own-numbers rule.')
    if a.write:
        random.seed(a.seed)
        random.shuffle(keep)
        cut = max(1, int(0.25 * len(keep)))
        te, tr = keep[:cut], keep[cut:]
        for name, pool in (('fault_train.jsonl', tr), ('fault_test.jsonl', te)):
            p = os.path.join(HERE, name)
            with open(p, 'w') as f:
                for c in pool:
                    f.write(json.dumps(c) + '\n')
            print(f'    wrote {p}  ({len(pool)} cases)')
        print(f'\n  NOT WIRED INTO A RIDE YET, deliberately. At {len(keep)} cases with a '
              f'{100*g.most_common(1)[0][1]/len(cs):.0f}% majority class')
        print(f'  this pool would teach the majority label and nothing else -- the exact fault the')
        print(f'  council pool had when split was 0/29. It goes in when the ledger is bigger and')
        print(f'  the classes are nearer even, and the diet/exam check runs first.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
