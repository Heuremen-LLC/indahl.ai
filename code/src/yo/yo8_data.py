"""yo8_data.py -- builds YO v8 data per PLAN_YO_V8.md (committed before this file). data8/train.jsonl = data7 train + 2,400 border verdict
items from TRAIN records; data8/valid.jsonl = data7 valid + 100 border items from VALID records; data8/test8c_items.jsonl = 800 border items
from TEST-period records (200 per kind, draw seed 881). Answers by yo2_data.truth on the rounded printed values. Writes DATA_YO_V8.sha256."""
import json, random, os, sys, re, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yo2_data as D
OUT = HERE + '/data8'; KINDS = ('margin-in', 'margin-out', 'ref-past', 'ref-short')
def item_border(b, S, Q, k, kind, tagp):
    rng = random.Random(f'B8|{tagp}|{b}|{S.isoformat()}|{k}|{kind}'); q = rng.choice(sorted(Q)); f = rng.choice(['T1', 'T2'])
    r = round(float(Q[q][f][0]), 1)
    if r < 5: return None
    d = round(0.10 * r, 1); u = rng.uniform(0.005, 0.25) * d; side = rng.choice((1, -1))
    if kind.startswith('margin'):
        edge = r + side * d + (-side * u if kind == 'margin-in' else side * u)   # near end: inside or outside reference +- margin
        far = r - side * d + side * rng.uniform(0.05, 0.9) * d                   # other end inside the band
    else:
        edge = r + side * u if kind == 'ref-past' else r - side * u               # near end just past the reference or just short of it
        far = edge + side * rng.uniform(0.1, 0.8) * r                             # interval extends away from the reference
    lo, hi = round(min(edge, far), 1), round(max(edge, far), 1)
    if lo <= 0 or lo >= hi: return None
    prompt = (f'{D.RULE_C}\nBackend {b}, qubit {q}: stated {f} = {r} microseconds (record stamp {D.hm(S)} UTC). '
              f'Measured {f}: 95% interval [{lo}, {hi}] microseconds. Margin: {d} microseconds.')
    return dict(job='C', id=f'C8|{kind}|{b}|{S.isoformat()}|{k}', record=f'{b}|{S.isoformat()}', kind=kind, prompt=prompt,
                answer=D.truth(r, lo, hi, d), r=r, lo=lo, hi=hi, d=d)
def pool(recs, kind, tagp, per_rec=3):
    return [x for b, S, p, Q in recs for k in range(per_rec) for x in [item_border(b, S, Q, k, kind, tagp)] if x]
def recheck(it):   # synthetic check: truth recomputed from the printed text only
    m = re.search(r'stated T[12] = ([\d.]+) .*interval \[([\d.]+), ([\d.]+)\].*Margin: ([\d.]+)', it['prompt'])
    r, lo, hi, d = map(float, m.groups()); assert D.truth(r, lo, hi, d) == it['answer'], it['id']
if __name__ == '__main__':
    recs = D.load_records(); test = [r for r in recs if r[1] >= D.CUT]; tr = [r for r in recs if r[1] < D.CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    rng = random.Random(880)
    B_tr = [x for kd in KINDS for x in rng.sample(pool(tr, kd, 'tr'), 600)]
    B_va = [x for kd in KINDS for x in rng.sample(pool(va, kd, 'va'), 25)]
    rt = random.Random(881); B_te = [x for kd in KINDS for x in rt.sample(pool(test, kd, 'te'), 200)]
    for it in B_tr + B_va + B_te: recheck(it)
    assert not ({i['record'] for i in B_te} & {f'{b}|{S.isoformat()}' for b, S, p, Q in tr + va}), 'TEST8C overlaps TRAIN/VALID'
    lens = [D.ntok(i['prompt'], i['answer']) for i in B_tr + B_va]
    if max(lens) > D.MAXLEN: sys.exit('REFUSED: item over max length')
    os.makedirs(OUT, exist_ok=True)
    for name, extra in (('train', B_tr), ('valid', B_va)):
        rows = [l for l in open(f'{HERE}/data7/{name}.jsonl') if l.strip()] + [json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n' for i in extra]
        random.Random(882 if name == 'train' else 883).shuffle(rows); open(f'{OUT}/{name}.jsonl', 'w').writelines(rows)
    with open(f'{OUT}/test8c_items.jsonl', 'w') as fh:
        for i in B_te: fh.write(json.dumps(i) + '\n')
    with open(HERE + '/DATA_YO_V8.sha256', 'w') as fh:
        for n in ('train', 'valid', 'test8c_items'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data8/{n}.jsonl\n')
    print('border TRAIN', len(B_tr), 'truths', dict(collections.Counter(i['answer'] for i in B_tr)))
    print('TEST8C', len(B_te), 'records', len({i['record'] for i in B_te}), 'truths by kind',
          {kd: dict(collections.Counter(i['answer'] for i in B_te if i['kind'] == kd)) for kd in KINDS})
