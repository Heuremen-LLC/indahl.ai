"""yo3_data.py -- builds YO v3 data per PLAN_YO_V3.md (committed d70fcbe before this file). Reuses yo2_data's record reader, prompt format and
answer rules unchanged. TRAIN3/VALID3 from the v2 TRAIN/VALID records; TEST3 from TEST-period records that no v2 TEST item came from."""
import json, random, os, sys, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yo2_data as D
OUT = HERE + '/data3'
def gaps(S, Q): return {q: max((S - D.when(Q[q][f][1])).total_seconds() / 3600 for f in ('T1', 'T2')) for q in Q}
def item_a_qubits(b, S, Q, qs, tag):
    lines, stale, zero = [], [], []
    for q in sorted(qs):
        e = Q[q]; parts = []
        for f in D.FIELDS:
            if f not in e or e[f][0] is None: continue
            v, t = e[f]; parts.append(f'{f}={D.g4(v)} ({D.hm(D.when(t))})' if t else f'{f}={D.g4(v)}')
            if f in ('T1', 'T2') and (S - D.when(t)).total_seconds() > 86400 and q not in stale: stale.append(q)
            if f in D.ERRS and v == 0: zero.append(f'{q}:{f}')
        lines.append(f'q{q}: ' + ', '.join(parts))
    prompt = f'{D.RULE_A}\nBackend {b}, last-calibration stamp {D.hm(S)} UTC.\n' + '\n'.join(lines)
    return dict(job='A', id=f'A3|{tag}|{b}|{S.isoformat()}', record=f'{b}|{S.isoformat()}', prompt=prompt, answer=json.dumps({'stale': sorted(stale), 'zero': sorted(zero)}))
def c_pool_n(recs, per_class, seed, draws):   # yo2_data.c_pool with more draws per record (TEST3's fresh records are fewer)
    pools = collections.defaultdict(list)
    for b, S, p, Q in recs:
        for k in range(draws):
            it = D.item_c(b, S, Q, k)
            if it: pools[it['answer']].append(it)
    rng = random.Random(seed); out = []
    for cls in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL'):
        assert len(pools[cls]) >= per_class, (cls, len(pools[cls])); out += rng.sample(pools[cls], per_class)
    rng.shuffle(out); return out
def item_a_band(b, S, Q, k):
    rng = random.Random(f'A3band|{b}|{S.isoformat()}|{k}'); g = gaps(S, Q)
    band = sorted(q for q in Q if 20 <= g[q] <= 50); rest = sorted(q for q in Q if q not in band)
    nb = min(len(band), rng.randint(3, 5)); pick = rng.sample(band, nb) + rng.sample(rest, 8 - nb) if len(rest) >= 8 - nb else None
    return item_a_qubits(b, S, Q, pick, f'band{k}') if pick else None
if __name__ == '__main__':
    recs = D.load_records(); test = [r for r in recs if r[1] >= D.CUT]; tr = [r for r in recs if r[1] < D.CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    used = set(json.loads(l)['record'] for l in open(HERE + '/data2/test_items.jsonl'))
    fresh = [r for r in test if f'{r[0]}|{r[1].isoformat()}' not in used]
    print('records: train', len(tr), 'valid', len(va), 'test-period', len(test), 'fresh for TEST3', len(fresh))
    rng = random.Random(331)
    band_tr = [x for b, S, p, Q in tr for k in range(2) for x in [item_a_band(b, S, Q, k)] if x]
    band_va = [x for b, S, p, Q in va for k in range(1) for x in [item_a_band(b, S, Q, k)] if x]
    A_band = rng.sample(band_tr, 2400); A_rep = rng.sample([D.item_a(b, S, Q, k + 10) for b, S, p, Q in tr for k in range(1)], 1200)
    C_rep = D.c_pool(tr, 600, 332)
    A_va = rng.sample(band_va, 100) + rng.sample([D.item_a(b, S, Q, 10) for b, S, p, Q in va], 100); C_va = D.c_pool(va, 50, 333)
    A_te = rng.sample([D.item_a(b, S, Q, 20) for b, S, p, Q in fresh], 400); C_te = c_pool_n(fresh, 100, 334, 40)
    TR = A_band + A_rep + C_rep; VA = A_va + C_va; random.Random(335).shuffle(TR)
    lens = [D.ntok(i['prompt'], i['answer']) for i in TR + VA]; print('tokens max', max(lens), 'median', sorted(lens)[len(lens) // 2])
    if max(lens) > D.MAXLEN: sys.exit('REFUSED: item over max length')
    te_recs = set(i['record'] for i in A_te + C_te); assert not (te_recs & used), 'TEST3 overlaps v2 TEST'
    trv = set(f'{b}|{S.isoformat()}' for b, S, p, Q in tr + va); assert not (te_recs & trv), 'TEST3 overlaps TRAIN/VALID'
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (('train', TR), ('valid', VA)):
        with open(f'{OUT}/{name}.jsonl', 'w') as fh:
            for i in rows: fh.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(f'{OUT}/test_items.jsonl', 'w') as fh:
        for i in A_te + C_te: fh.write(json.dumps(i) + '\n')
    with open(HERE + '/DATA_YO_V3.sha256', 'w') as fh:
        for n in ('train', 'valid', 'test_items'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data3/{n}.jsonl\n')
    st = [q for i in A_band for q in json.loads(i['answer'])['stale']]
    print('TRAIN3 band items', len(A_band), 'stale qubits in them', len(st), '| TEST3 A empty', sum(json.loads(i['answer']) == {'stale': [], 'zero': []} for i in A_te), 'of 400')
