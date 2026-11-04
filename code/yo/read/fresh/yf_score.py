"""yf_score.py -- scores the FRESH TEST per PLAN_YO_FRESH.md. Written and committed before any fresh reply exists.
Family A: YO Read 61-63 vs always-NO. Family A2 (Addendum 1): YO Read vs the BEST CONSTANT (fresh majority truth per field). Family B: YO Read seed i vs SELF-LABEL 73+i. Family C: SHUFFLED 71-73 vs always-NO. Per field, exact two-sided McNemar
on discordant pairs, Holm across the 9 tests of each family separately. Clears/beats = higher accuracy AND Holm p < 0.05. Unread counts wrong."""
import json, os
from math import comb
H = os.path.dirname(os.path.abspath(__file__)); F = ('DATES', 'LINK', 'REQUEST')
def binom_two(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
ld = lambda a: {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/eval_fresh_yo_{a}.jsonl')}
import sys
SET = sys.argv[1] if len(sys.argv) > 1 else 'primary'   # Addendum 2: verdicts on 'primary'; 'full' = the 288, secondary
items = [json.loads(l) for l in open(H + {'primary': '/data/test_items_primary.jsonl', 'sensitivity': '/data/test_items_sensitivity.jsonl', 'full': '/data/test_items_fresh.jsonl'}[SET])]
NO = {i['id']: i['answer'] == 'NO' for i in items}
import collections
BEST = {q: collections.Counter(i['answer'] for i in items if i['q'] == q).most_common(1)[0][0] for q in F}
BC = {i['id']: i['answer'] == BEST[i['q']] for i in items}
def holm(ts):
    order = sorted(range(len(ts)), key=lambda i: ts[i]['p']); prev = 0
    for r, i in enumerate(order): adj = min(1.0, max(prev, (len(ts) - r) * ts[i]['p'])); ts[i]['p_holm'] = adj; prev = adj
    for t in ts: t['win'] = t['right_a'] > t['right_b'] and t['p_holm'] < 0.05
    return ts
def pair(q, A, B, la, lb):
    its = [i['id'] for i in items if i['q'] == q]
    a = {k: A[k]['score'] == 1.0 for k in its}; b = B if isinstance(B, dict) and all(isinstance(v, bool) for v in B.values()) else {k: B[k]['score'] == 1.0 for k in its}
    bb = sum(a[k] and not b[k] for k in its); cc = sum(b[k] and not a[k] for k in its)
    return dict(q=q, a=la, b=lb, n=len(its), right_a=sum(a.values()), right_b=sum(b[k] for k in its), b_=bb, c_=cc, unread_a=sum(A[k]['pred'] is None for k in its), p=binom_two(bb, cc))
YO = {s: ld(f'read{s}') for s in (1, 2, 3)}; SL = {s: ld(f'self{s}') for s in (1, 2, 3)}; SH = {s: ld(f'shuf{s}') for s in (1, 2, 3)}
A = holm([pair(q, YO[s], NO, f'YO Read {60 + s}', 'always-NO') for q in F for s in (1, 2, 3)])
A2 = holm([pair(q, YO[s], BC, f'YO Read {60 + s}', f'always-{BEST[q]}') for q in F for s in (1, 2, 3)])
B = holm([pair(q, YO[s], SL[s], f'YO Read {60 + s}', f'self-label {73 + s}') for q in F for s in (1, 2, 3)])
C = holm([pair(q, SH[s], NO, f'shuffled {70 + s}', 'always-NO') for q in F for s in (1, 2, 3)])
C2 = holm([pair(q, SH[s], BC, f'shuffled {70 + s}', f'always-{BEST[q]}') for q in F for s in (1, 2, 3)])
L = [f'YO Read FRESH TEST (PLAN_YO_FRESH.md + Addenda 1-2), {SET.upper()} set' + {'primary': ' (verdicts read here with the sensitivity set; UNDERPOWERED below ~100 papers; measures agreement with the List reader F4 notes as parsed)', 'sensitivity': ' (primary minus 4 known-bad labels; a field is shown only if it holds here AND on primary)', 'full': ' (SECONDARY: includes default-YES labels and partial reads; no verdict read here)'}[SET] + f', {len({i["paper"] for i in items})} papers. Exact McNemar per field, Holm across 9 per family.']
L.append(f'Best constant per field (fresh majority truth): {BEST}. Families are separate claims, each Holm across its own 9, none corrected across families.')
for name, fam in (('A  YO Read vs always-NO', A), ('A2 YO Read vs best constant', A2), ('B  YO Read vs self-label', B), ('C  shuffled vs always-NO', C), ('C2 shuffled vs best constant', C2)):
    L.append('Family ' + name)
    for t in fam: L.append(f"  {t['q']:8s} {t['a']} {t['right_a']}/{t['n']} vs {t['b']} {t['right_b']}/{t['n']}; b {t['b_']} c {t['c_']}; unread {t['unread_a']}; p {t['p']:.4g}, Holm {t['p_holm']:.4g} -> {'AHEAD' if t['win'] else 'not shown'}")
for q in F:
    both = sum(x['win'] and y['win'] for x, y in zip([t for t in A if t['q'] == q], [t for t in A2 if t['q'] == q]))
    a = sum(t['win'] for t in A if t['q'] == q); a2 = sum(t['win'] for t in A2 if t['q'] == q); b = sum(t['win'] for t in B if t['q'] == q)
    c = sum(t['win'] for t in C if t['q'] == q); c2 = sum(t['win'] for t in C2 if t['q'] == q)
    L.append(f"{q}: A {a}/3, A2 {a2}/3, both {both}/3 -> {'REPLICATES' if both >= 2 else 'does not replicate'}; B {b}/3 -> {('PASS' if both >= 2 else 'PASS on B alone, NOT read as needing the real answers (field does not replicate; Addendum 2 item 8)') if b == 3 else 'not shown to need the real answers'}; C shuffled clearing always-NO {c}, best constant {c2}")
open(H + f'/results_fresh_{SET}.text', 'w').write('\n'.join(L) + '\n'); json.dump(dict(BEST=BEST, A=A, A2=A2, B=B, C=C, C2=C2), open(H + f'/results_fresh_{SET}.json', 'w'), indent=1); print('\n'.join(L))
