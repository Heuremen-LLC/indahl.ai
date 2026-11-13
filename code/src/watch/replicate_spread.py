#!/usr/bin/env python3
"""replicate_spread.py -- HOW MUCH TWO IDENTICAL RUNS DIFFER, READ FROM DISK. (Bones, 9 Oct 2026.)

Wayfinder, 9 Oct: "you and you magnitudes bones...."

WHY THIS FILE EXISTS. On 9 Oct the three finished pods were compared and the two MATCHED ones -- same
config, no physics in either -- scored 90 and 99 of 102 on Meilong. That 9-point gap is the floor under
every margin this house reports: a Meilong-vs-vote gap smaller than the gap between two runs of the SAME
thing is not a result. So the caveat went onto three boards -- and I TYPED 9 AND 2.45 INTO ALL THREE.

That is the identical fault I had just removed. 4.1x was typed into a comment and went stale; 9 and 2.45
were typed into three files to fix it. A number that moves must be read, not written down.

AND THE DEEPER ONE, WHICH IS THE MAGNITUDE HABIT. Comparing two replicates by their TOTALS (90 vs 99) is
a magnitude: it cannot say whether they disagreed on 9 cases or on 30 against 21. The Exor asked of two
replicates is "WHICH ONE OF YOU GOT THIS CASE", and that is an EDGE, not a difference. It was
unanswerable from disk because the exam saved tallies and never cases. That is now fixed in
wen_stooges_tick.py (per_case rides with the tallies), so from the NEXT ride this file reads the real
edge. Until then it reads totals and SAYS SO, every time, rather than quietly presenting a magnitude as
if it were the spread.

    python3 replicate_spread.py
"""
import glob
import json
import math
import os
import re
import statistics as st

PODS = os.path.expanduser('~/bones-forge/triangulation/wen_data/pods')


def _last_exam(logpath):
    try:
        txt = open(logpath).read()
    except Exception:
        return None, None
    i = txt.rfind('EXAM round ')
    if i < 0:
        return None, None
    rnd = re.match(r'EXAM round (\d+)', txt[i:])
    try:
        d = json.loads(txt[txt.index('{', i):].split('\n')[0])
    except Exception:
        return None, None
    return (int(rnd.group(1)) if rnd else None), d


def _hardware(pod):
    """the silicon a pod ran on. Read because it is an UNCONTROLLED VARIABLE: on the 8-9 Oct rides
    tick2 and tick4 were A6000 and tick3 -- the only pod with physics in its training -- was an A40,
    so that comparison is confounded with hardware as well as with run-to-run variance."""
    try:
        s = open(os.path.join(PODS, pod, 'stack.txt')).read()
        m = re.search(r'(NVIDIA [A-Za-z0-9 ]+)', s)
        return m.group(1).strip() if m else None
    except Exception:
        return None


def read_pods(min_round=150):
    out = {}
    for d in sorted(glob.glob(os.path.join(PODS, '*', 'log.txt'))):
        pod = os.path.basename(os.path.dirname(d))
        rnd, ex = _last_exam(d)
        if not ex or (min_round and (rnd or 0) < min_round):
            continue
        mei = ex.get('wen MEILONG (seats composed as a product)') or {}
        vot = ex.get('wen (three seats decided)') or {}
        if not mei or not vot:
            continue
        n = sum(mei.get(k, 0) for k in ('LANDED', 'STUCK', 'HELD', 'EARLY FLIP'))
        out[pod] = {
            'round': rnd, 'n': n,
            'meilong_right': mei.get('LANDED', 0) + mei.get('HELD', 0),
            'vote_right': vot.get('LANDED', 0) + vot.get('HELD', 0),
            'hardware': _hardware(pod),
            'per_case': ex.get('per_case (the cases, not just the counts -- so two pods can be read '
                               'as an edge)'),
            'age_min': round((os.path.getmtime(d) - 0) and
                             (__import__('time').time() - os.path.getmtime(d)) / 60, 1),
        }
    return out


def spread(pods=None, min_round=150):
    """the replicate spread, measured. Returns the EDGE when the cases are on disk, the TOTALS
    otherwise, and always says which it gave."""
    P = pods if pods is not None else read_pods(min_round)
    if len(P) < 2:
        return {'readable': False, 'n_pods': len(P),
                'verdict': f'LA NADA -- {len(P)} pod(s) with a round-{min_round} exam. A replicate '
                           f'spread needs at least two runs of the same thing.'}
    names = sorted(P)
    hw = {p: P[p]['hardware'] for p in names}
    same_hw = len(set(v for v in hw.values() if v)) <= 1
    scores = {p: P[p]['meilong_right'] for p in names}
    N = max(P[p]['n'] for p in names)
    # THE EDGE, when the cases exist
    edges = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            pa, pb = P[a].get('per_case'), P[b].get('per_case')
            if pa and pb and pa.get('right_meilong') and pb.get('right_meilong'):
                ra, rb = pa['right_meilong'], pb['right_meilong']
                m = min(len(ra), len(rb))
                a_only = sum(1 for k in range(m) if ra[k] and not rb[k])
                b_only = sum(1 for k in range(m) if rb[k] and not ra[k])
                x = a_only + b_only
                edges[f'{a}^{b}'] = {
                    'xor': x, 'a_only': a_only, 'b_only': b_only, 'cases': m,
                    'dom': round((a_only - b_only) / x, 4) if x else None,
                    'NOTE': 'the cases exactly one pod got. THIS is the spread; the score difference '
                            'is only its net.'}
    rng = max(scores.values()) - min(scores.values())
    sd = st.stdev(scores.values()) if len(scores) > 1 else None
    se = math.sqrt(sum((scores[p] / N) * (1 - scores[p] / N) / N for p in names[:2]))
    widths = (rng / N) / se if se else None
    return {
        'readable': True, 'n_pods': len(P), 'cases_per_pod': N,
        'scores': scores, 'hardware': hw, 'same_hardware': same_hw,
        'range': rng, 'stdev': round(sd, 2) if sd else None,
        'range_in_widths': round(widths, 2) if widths else None,
        'EDGES': edges or None,
        'basis': ('EDGE -- per-case, the real disagreement' if edges else
                  'TOTALS ONLY -- the exam on disk saved counts, not cases, so this is a MAGNITUDE '
                  'and cannot say whether the pods disagreed on few cases or on many in both '
                  'directions. Fixed for the next ride; not retroactive.'),
        'CONFOUND': (None if same_hw else
                     f'HARDWARE IS NOT CONTROLLED: {hw}. A pod that differs in config AND silicon '
                     f'cannot separate the two.'),
        'verdict': (f'two or more runs differ by {rng} of {N} '
                    + (f'({widths:.2f} widths)' if widths else '')
                    + '. A reported margin smaller than this is inside run-to-run variance.'),
    }


if __name__ == '__main__':
    import sys
    s = spread()
    print('  REPLICATE SPREAD, read from disk')
    if not s['readable']:
        print(f"  {s['verdict']}")
        sys.exit(0)
    print(f"  {s['n_pods']} pods, {s['cases_per_pod']} cases each")
    for p, v in sorted(s['scores'].items()):
        print(f"    {p:<8} meilong right {v:>4}   {s['hardware'].get(p)}")
    print(f"  range {s['range']}  stdev {s['stdev']}  = {s['range_in_widths']} widths")
    print(f"  BASIS: {s['basis']}")
    if s['CONFOUND']:
        print(f"  CONFOUND: {s['CONFOUND']}")
    if s['EDGES']:
        print('  EDGES (per-case, the real disagreement):')
        for k, e in s['EDGES'].items():
            print(f"    {k:<16} xor {e['xor']}  {e['a_only']} / {e['b_only']}  dom {e['dom']}")
    print(f"  => {s['verdict']}")


# ================================================================ WHAT A BOARD SHOULD CALL
# 9 Oct: the exam now emits reading rows, but no exam has RUN through that code -- the pods finished
# at 04:43 and every exam on disk predates it. So a board pointed only at the new block would show
# nothing until the next ride, and the three bare margins would stay bare in the meantime.
#
# This reads the block WHEN IT IS THERE and builds the same rows FROM THE TALLIES when it is not, so
# the enforcement starts today on frozen data and keeps working after the next ride changes the shape.
# One function, three consumers: the margin cannot be computed three different ways again.

import sys as _sys
_sys.path.insert(0, os.path.expanduser('~/bones-forge/watch'))
import reading as _rd


def exam_readings(ex, at=None):
    """every headline number of one exam as a reading row, block-or-tallies.
    Returns {'rows': {...}, 'source': 'block'|'tallies', 'margin': row-or-None}."""
    blk = next((v for k, v in ex.items() if k.startswith('readings (')), None)
    if blk and blk.get('rows'):
        rows = dict(blk['rows'])
        return {'rows': rows, 'source': 'block',
                'margin': rows.get('wen MEILONG vs the vote')}

    def right(t): return (t or {}).get('LANDED', 0) + (t or {}).get('HELD', 0)

    def n(t): return sum((t or {}).get(k, 0) for k in ('LANDED', 'STUCK', 'HELD', 'EARLY FLIP'))
    shep = ex.get('shep')
    if not shep:
        return {'rows': {}, 'source': 'none', 'margin': None}
    sh = right(shep)
    rows = {}
    for nm in ('moe', 'larry', 'curly', 'wen (three seats decided)'):
        t = ex.get(nm)
        if t:
            rows[nm] = _rd.as_row(_rd.count(right(t), n(t), null=sh, name=f'{nm} right', at=at,
                                            null_is_empirical=True))
    mt = ex.get('wen MEILONG (seats composed as a product)')
    vt = ex.get('wen (three seats decided)')
    margin = None
    if mt and vt:
        margin = _rd.as_row(_rd.count(right(mt), n(mt), null=right(vt), name='Meilong right',
                                      at=at, null_is_empirical=True))
        rows['wen MEILONG vs the vote'] = margin
    return {'rows': rows, 'source': 'tallies (computed here; this exam predates the readings block)',
            'margin': margin}


def margin_line(ex, at=None):
    """the single line a board prints for the Meilong margin. The verdict leads, so no truncation
    from the left can remove it, and there is no path that returns a bare number."""
    r = exam_readings(ex, at)
    if not r['margin']:
        return 'LA NADA -- this exam has no Meilong row'
    return _rd.show(r['margin'])
