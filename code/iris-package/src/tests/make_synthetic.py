#!/usr/bin/env python3
"""make_synthetic.py: writes the synthetic dataset in tests/data/ with answers planted on purpose, and PLANTED.json with the planted counts.
Nothing here is real model output. Deterministic: the same files come out every time."""
import json, os, random
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'data'); os.makedirs(D, exist_ok=True)
R = random.Random(20261101); N = 400; ids = [f'q{i:03d}' for i in range(N)]
def dump(name, rows):
    with open(os.path.join(D, name), 'w') as f:
        for r in rows: f.write(json.dumps(r) + '\n')
def flip(base, rw, wr, rng):
    """copy of base (dict id->bool) with exactly rw right-to-wrong and wr wrong-to-right flips"""
    right = sorted(k for k, v in base.items() if v); wrong = sorted(k for k, v in base.items() if not v)
    out = dict(base)
    for k in rng.sample(right, rw): out[k] = False
    for k in rng.sample(wrong, wr): out[k] = True
    return out
def rows(m, tag): return [dict(id=k, correct=m[k], run=tag) for k in ids]
A1 = {k: R.random() < 0.7 for k in ids}
A2 = flip(A1, 20, 10, R)      # repeat of A: 20 right-to-wrong, 10 wrong-to-right
B1 = flip(A1, 60, 10, R)      # A right and B wrong 60, A wrong and B right 10  -> A above B
C1 = flip(A1, 5, 5, R)        # 5 and 5 -> consistent
E1 = flip(A1, 14, 6, R)       # 14 and 6 -> cannot tell
for n, m in (('A1', A1), ('A2', A2), ('B1', B1), ('C1', C1), ('E1', E1)): dump(n + '.jsonl', rows(m, n))
# parser data: three labels, 60 replies each. The reply ends with the answer. 'good' parser is always right, 'bad' parser always takes the wrong number,
# 'edge' parser is wrong on 6 of the 60 (every tenth)
def reply(i): return f'Let us work it out. First we get {i + 3}, then the answer is {i}.'
P = []
for fam in ('good', 'bad', 'edge'):
    for i in range(60):
        wrong = fam == 'bad' or (fam == 'edge' and i % 10 == 0)
        P.append(dict(id=f'{fam}-{i:02d}', family=fam, reply=reply(i), pred=str(i + 3) if wrong else str(i)))
dump('parser.jsonl', P)
json.dump(dict(items=N, A1_vs_A2=dict(right_to_wrong=20, wrong_to_right=10, net=-10, repeat_floor=30 / N),
               A1_vs_B1=dict(A_right_B_wrong=60, A_wrong_B_right=10, outcome='ABOVE'), B1_vs_A1=dict(outcome='BELOW'),
               A1_vs_C1=dict(A_right_B_wrong=5, A_wrong_B_right=5, outcome='CONSISTENT'), A1_vs_E1=dict(A_right_B_wrong=14, A_wrong_B_right=6, outcome='CANNOT_TELL'),
               parser=dict(good='0 mis-parsed in every reply', bad='every reply mis-parsed', edge='exactly 6 of 60 replies mis-parsed (ids edge-00, edge-10, ... edge-50)')),
          open(os.path.join(D, 'PLANTED.json'), 'w'), indent=1)
print('wrote', D)
