#!/usr/bin/env python3
"""mood_read.py -- READ THE MOOD TEST, re-scoring from the raw replies. (Bones, 10 Oct 2026.)

The run logged the raw reply for every call, so the verdict is recomputed here rather than trusted
from collection time -- which is what let the pilot's two scoring faults be fixed without rerunning:

  * 'UNKNOWN: 1' had been scored as HELD while naming a value. An unknown followed by a number is
    a COMMIT.
  * a bare '150' had been scored NEITHER, which conflated "did not follow the format" with "did not
    commit". A bare number IS a commit; only the format was missed.

THE COMPETENCE GATE, which is the whole reason the control questions exist. If a model is simply
weaker in one language it will say UNKNOWN more often in that language, and that is indistinguishable
from "holding the unresolved state" unless something separates them. So: a language is admitted only
if the model answers the KNOWN-ANSWER controls correctly in it. A language that fails the controls is
reported and excluded, never averaged in.

THE NONE IS EXACT. Under no language effect the commit counts are binomial with one shared rate, so
the comparison is a 2 x L contingency table on admitted languages only -- and the rungs are compared
as groups, each with more than one language where possible, so a rung can disagree with itself.
"""
import json, math, os, re, sys
from collections import defaultdict

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'mood_test.jsonl')
TRUTH = {'c1': 6, 'c2': 51}


def score(reply):
    if not reply or reply.startswith('<<'):
        return 'ERROR'
    r = reply.upper()
    unk = bool(re.search(r'UNKNOWN|DESCONOCID|INCONNU|未知|NO SE SABE|ON NE SAIT', r))
    num = bool(re.search(r'[-+]?\d[\d.,]*', r))
    if num:
        return 'COMMITTED'
    if unk:
        return 'HELD'
    return 'NEITHER'


def ctrl_ok(qid, reply):
    """did it get the known answer right, in any format, in any language?"""
    want = TRUTH[qid]
    for m in re.finditer(r'[-+]?\d[\d.]*', reply.replace(',', '')):
        try:
            if abs(float(m.group(0)) - want) < 1e-9:
                return True
        except ValueError:
            pass
    return False


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else None
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    if model:
        rows = [r for r in rows if r['model'] == model]
    if not rows:
        print('  no rows'); return 1
    models = sorted({r['model'] for r in rows})
    print(f'  THE MODEL TEST -- {len(rows)} calls, model(s) {", ".join(models)}')
    print(f'  re-scored from the raw replies, not from the collection-time verdict\n')

    # ---- the competence gate
    print('  THE COMPETENCE GATE -- known-answer controls, by language')
    print(f"    {'lang':<6}{'rung':<12}{'controls right':>16}{'rate':>8}   admitted?")
    admitted = {}
    for lg in sorted({r['lang'] for r in rows}):
        c = [r for r in rows if r['lang'] == lg and r['kind'] == 'control']
        ok = sum(1 for r in c if ctrl_ok(r['qid'], r.get('reply', '')))
        rate = ok / len(c) if c else 0.0
        rung = c[0]['rung'] if c else '?'
        admitted[lg] = rate >= 0.70
        print(f"    {lg:<6}{rung:<12}{ok:>8} of {len(c):<5}{rate:>8.2f}   "
              + ('YES' if admitted[lg] else 'NO -- excluded, its UNKNOWNs are incompetence'))
    adm = [lg for lg, v in admitted.items() if v]
    print(f'\n    {len(adm)} of {len(admitted)} languages admitted: {", ".join(adm) or "NONE"}')
    if len(adm) < 2:
        print('\n  FEWER THAN TWO LANGUAGES CLEAR THE GATE, so there is no comparison to make.')
        print('  That is the reading: this model is not an instrument for this question. The test')
        print('  is not negative -- it was never run, because the apparatus failed its own control.')
        return 0

    # ---- the open questions, admitted languages only
    print('\n  THE OPEN QUESTIONS -- a named number is a COMMIT; no known value exists')
    print(f"    {'lang':<6}{'rung':<12}{'committed':>11}{'held':>7}{'neither':>9}{'err':>5}{'commit rate':>13}")
    tab = {}
    for lg in adm:
        o = [r for r in rows if r['lang'] == lg and r['kind'] == 'open']
        v = [score(r.get('reply', '')) for r in o]
        c, h, n, e = (v.count('COMMITTED'), v.count('HELD'), v.count('NEITHER'), v.count('ERROR'))
        dec = c + h
        tab[lg] = (c, h, o[0]['rung'])
        print(f"    {lg:<6}{o[0]['rung']:<12}{c:>11}{h:>7}{n:>9}{e:>5}"
              + (f'{c/dec:>13.3f}' if dec else f"{'--':>13}"))

    # ---- the exact none: one shared rate across admitted languages
    C = sum(t[0] for t in tab.values()); H = sum(t[1] for t in tab.values())
    N = C + H
    if N == 0 or not (C and H):
        print(f'\n  every admitted language went the same way ({C} committed, {H} held) -- no spread')
        print('  to test. The reading is that the commit rate is 1.0 or 0.0 regardless of language.')
        return 0
    p0 = C / N
    chi = 0.0
    dof = -1
    for lg, (c, h, _) in tab.items():
        m = c + h
        if m == 0: continue
        dof += 1
        for obs, pr in ((c, p0), (h, 1 - p0)):
            exp = m * pr
            if exp > 0: chi += (obs - exp) ** 2 / exp
    print(f'\n  THE NONE, exact and unshuffled: under no language effect every admitted language')
    print(f'  draws from ONE binomial rate, p0 = {p0:.4f} = {C}/{N}.')
    print(f'    chi-square {chi:.3f} on {dof} dof, expectation {dof} +- {math.sqrt(2*dof) if dof>0 else 0:.2f}')
    if dof > 0:
        sep = abs(chi - dof) / math.sqrt(2 * dof)
        print(f'    {sep:.2f} widths from its expectation: '
              + ('A LANGUAGE EFFECT' if sep >= 2 else 'NO LANGUAGE EFFECT at this count'))

    # ---- rungs as groups
    print('\n  BY RUNG -- more than one language per rung where possible, so a rung can disagree')
    g = defaultdict(lambda: [0, 0, []])
    for lg, (c, h, rung) in tab.items():
        g[rung][0] += c; g[rung][1] += h; g[rung][2].append(lg)
    print(f"    {'rung':<14}{'langs':<14}{'committed':>11}{'held':>7}{'rate':>9}")
    for rung, (c, h, lgs) in sorted(g.items()):
        print(f"    {rung:<14}{','.join(lgs):<14}{c:>11}{h:>7}"
              + (f'{c/(c+h):>9.3f}' if c + h else f"{'--':>9}"))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
