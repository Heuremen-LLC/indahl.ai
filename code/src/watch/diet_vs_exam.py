#!/usr/bin/env python3
"""diet_vs_exam.py -- IS ANY READER IN THIS HOUSE EXAMINED ON A DIET IT WAS NEVER FED?
Read-only. (Bones, 9 Oct 2026.)

Wayfinder: "make sure you're applying everything to everyone."

On 9 Oct one fault was isolated in Wen: the kind 'split' is 2.26% of the best pod's training mix and
24.2% of its exam -- a 10.7x under-representation -- and it accounts for 33 of the 37 cases every seat
misses together. The ballast turned out to be the council pool: 7,424 rows of 8,558, 87% of everything
tick4 saw, containing ZERO split cases.

That is not a Wen fault. It is a SHAPE, and this file looks for the same shape everywhere:

    1. DIET vs EXAM     is a category a large share of the exam and a small share of the training?
    2. SAME TARGET      do two supposedly independent readers receive identical gold on every case?
                        (moe and larry did: seat_gold branches on ONE kind, so two of three seats
                        were one seat from round 0, and their jaccard of 0.784 was the design.)
    3. ZERO FOR N       is a whole category scored 0-of-n by EVERY reader including the control?
                        A category an untrained control also fails is not a hard category.
    4. BALLAST          does one pool dominate the diet while teaching none of the missing skill?

AND IT APPLIES TO ME. My own seats stack has the same two faults, found this morning by hand:
OBSERVER and SHEP missed exactly the same 18 of 36 labelled cases (jaccard 1.0, XOR 0) -- same base
weights, same prompt, so the control and the seat it prices are one reader. And the seats were scored
against six named laws while being prompted with no law named: generic prompt 3/6 and flagged nothing,
named prompt 6/6 and flagged exactly the three real faults. That is DIET vs EXAM in a prompt instead of
a pool. Same shape, different substrate.

    python3 diet_vs_exam.py
"""
import collections
import glob
import json
import os
import sys

WD = os.path.expanduser('~/bones-forge/triangulation/wen_data')
TR = os.path.expanduser('~/bones-forge/triangulation/triangle')


def load(path):
    try:
        return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    except Exception:
        return []


def kinds(rows):
    return collections.Counter(r.get('kind') for r in rows if r.get('kind'))


def diet_vs_exam(name, pools, exam_paths, note=''):
    """pools: [(path, weight)]. exam_paths: EVERY pool the reader is scored on, not one of them."""
    if isinstance(exam_paths, str):
        exam_paths = [exam_paths]
    exam = []
    for p in exam_paths:
        exam += load(p)
    if not exam:
        return {'reader': name, 'readable': False,
                'why': f'no exam found in {[os.path.basename(x) for x in exam_paths]}'}
    ek = kinds(exam)
    tot = 0
    dk = collections.Counter()
    for p, w in pools:
        rows = load(p)
        tot += len(rows) * w
        for k, v in kinds(rows).items():
            dk[k] += v * w
        if rows and not kinds(rows):
            dk['(unlabelled)'] += len(rows) * w
    if not tot:
        return {'reader': name, 'readable': False, 'why': 'no training pool found'}
    out = []
    for k, en in ek.most_common():
        es = en / len(exam)
        ds = dk.get(k, 0) / tot
        ratio = (es / ds) if ds else float('inf')
        out.append({'kind': k, 'exam_share': es, 'diet_share': ds, 'under_by': ratio,
                    'exam_n': en, 'diet_rows': dk.get(k, 0)})
    out.sort(key=lambda r: -r['under_by'])
    # the ballast: the biggest pool that teaches none of the worst-served kind
    worst = out[0]['kind'] if out else None
    ballast = None
    for p, w in pools:
        rows = load(p)
        if not rows:
            continue
        share = len(rows) * w / tot
        if share > 0.4 and kinds(rows).get(worst, 0) == 0:
            ballast = (os.path.basename(p), round(100 * share, 1))
    return {'reader': name, 'readable': True, 'exam_n': len(exam), 'diet_rows': tot,
            'rows': out, 'ballast': ballast, 'note': note}


def report(d):
    print(f"\n  === {d['reader']} ===")
    if not d['readable']:
        print(f"    LA NADA -- {d['why']}")
        return
    print(f"    diet {d['diet_rows']} weighted rows   exam {d['exam_n']} cases")
    print(f"    {'kind':<14} {'exam':>8} {'diet':>8} {'under by':>10}")
    for r in d['rows']:
        u = '  inf' if r['under_by'] == float('inf') else f"{r['under_by']:.1f}x"
        flag = '   <-- NEVER TAUGHT' if r['diet_rows'] == 0 else (
               '   <-- under-fed' if r['under_by'] >= 3 else '')
        print(f"    {str(r['kind']):<14} {100*r['exam_share']:>7.1f}% {100*r['diet_share']:>7.2f}% {u:>10}{flag}")
    if d['ballast']:
        print(f"    BALLAST: {d['ballast'][0]} is {d['ballast'][1]}% of the diet and teaches "
              f"none of the worst-served kind.")
    if d.get('note'):
        print(f"    {d['note']}")


def zero_for_n():
    """check 3, on whatever exam output is on disk: a kind every reader fails."""
    print('\n  === ZERO FOR N -- a category every reader misses, control included ===')
    found = False
    for log in sorted(glob.glob(os.path.join(WD, 'pods', '*', 'log.txt'))):
        pod = os.path.basename(os.path.dirname(log))
        txt = open(log).read()
        i = txt.rfind('EXAM round ')
        if i < 0:
            continue
        try:
            d = json.loads(txt[txt.index('{', i):].split('\n')[0])
        except Exception:
            continue
        bk = next((v for k, v in d.items() if k.startswith('held_out_by_kind')), None)
        if not bk:
            continue
        dead = []
        for kind, v in sorted(bk.items()):
            if all(int(str(x).split('/')[0]) == 0 for x in v.values()):
                dead.append((kind, int(str(list(v.values())[0]).split('/')[1])))
        if dead:
            found = True
            tot = sum(n for _k, n in dead)
            print(f"    {pod}: {', '.join(f'{k} 0/{n}' for k, n in dead)}   = {tot} cases "
                  f"no reader gets, control included")
    if not found:
        print('    none found in any pod log on disk')


def same_target():
    """check 2: readers handed identical gold. Read from the exam's own by-kind table."""
    print('\n  === SAME TARGET -- two readers scoring identically on every kind ===')
    for log in sorted(glob.glob(os.path.join(WD, 'pods', '*', 'log.txt'))):
        pod = os.path.basename(os.path.dirname(log))
        txt = open(log).read()
        i = txt.rfind('EXAM round ')
        if i < 0:
            continue
        try:
            d = json.loads(txt[txt.index('{', i):].split('\n')[0])
        except Exception:
            continue
        bk = next((v for k, v in d.items() if k.startswith('held_out_by_kind')), None)
        if not bk:
            continue
        readers = sorted({r for v in bk.values() for r in v})
        for a in readers:
            for b in readers:
                if a >= b:
                    continue
                diffs = [abs(int(str(v[a]).split('/')[0]) - int(str(v[b]).split('/')[0]))
                         for v in bk.values() if a in v and b in v]
                if diffs and max(diffs) <= 2:
                    print(f"    {pod}: {a} and {b} never differ by more than {max(diffs)} on any "
                          f"kind -- one seat wearing two hats?")


def main():
    print('  DIET vs EXAM -- every reader in the house, read-only')
    print('  the shape: a category that is a large share of the exam and a small share of the diet.')
    # 9 Oct, CAUGHT AFTER IT HAD ALREADY PRODUCED A HEADLINE: this compared the diet against
    # test.jsonl alone -- 120 cases -- and reported "split is under-fed 10.7x". The pods are scored on
    # EVERY exam pool: test 120 + real_test 24 + council_test 132 + physics_test 1200 = 1476, of which
    # PHYSICS IS 81.3%. Against the real denominator the four kinds are slightly OVER-fed and the true
    # mismatches reverse: council 86.7% of diet against 8.9% of exam, and physics 81.3% of the exam
    # taught to tick4 at weight ZERO. An auditor with the wrong denominator is worse than none, because
    # its output gets quoted.
    for pod, pw in (('tick2', 1), ('tick3', 4), ('tick4', 0)):
        d = diet_vs_exam(
            f'WEN / {pod} (physics weight {pw})',
            [(os.path.join(WD, 'train.jsonl'), 1),
             (os.path.join(WD, 'real_train.jsonl'), 3),
             (os.path.join(WD, 'council_train.jsonl'), 1),
             (os.path.join(WD, 'physics_train.jsonl'), pw)],
            [os.path.join(WD, f) for f in ('test.jsonl', 'real_test.jsonl',
                                           'council_test.jsonl', 'physics_test.jsonl')])
        report(d)
    zero_for_n()
    same_target()
    print('\n  === BONES / my own seats stack ===')
    print('    MEASURED BY HAND 9 Oct, not by this file: OBSERVER and SHEP missed exactly the same')
    print('    18 of 36 labelled cases -- jaccard 1.0, XOR 0. Same base weights, same prompt. The')
    print('    control and the seat it prices are ONE READER. (check 2, failed)')
    print('    And the diet/exam mismatch lives in the PROMPT, not a pool: scored against six named')
    print('    laws while prompted with no law named. Same model, same 6 cases, temperature 0 --')
    print('    generic prompt 3/6 flagging nothing, named prompt 6/6 flagging exactly the 3 real')
    print('    faults. (check 1, failed)')
    print('    NOT AUTOMATED HERE: my seats have no persisted exam, so this file cannot read them.')
    print('    That absence is itself the finding -- Wen has 150 rounds of logs and I have none.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
