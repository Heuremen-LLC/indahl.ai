"""yo7_data.py -- builds YO v7 training data per PLAN_YO_V7.md (committed before this file), from yo6_data.py. Reuses yo2_data's record reader, prompt format and
answer rules, yo3_data's item builder, yo4_data's whole-window builder and yo5_data's same-date groups, with new draw seeds for every kind.
TRAIN6/VALID6 from the v2 TRAIN/VALID records; TEST6 from TEST-period records (no v6 training item comes from that period)."""
import json, random, os, sys, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yo2_data as D, yo3_data as Y3, yo4_data as Y4, yo5_data as Y5
OUT = HERE + '/data7'
def tag(it, t, extra=''):
    it['id'] = it['id'].replace('A3|', 'A6|', 1).replace('|sd', '|' + t, 1) + extra; return it
def older(Q, q): return min(D.when(Q[q][f][1]) for f in ('T1', 'T2'))
def young_prev(recs, k):   # 8 qubits from one group under 24 h old whose date is on an earlier UTC calendar day than the stamp
    out = []
    for b, S, p, Q in recs:
        for d, h, qs in Y5.groups(S, Q):
            if h < 24 and d.date() < S.date():
                pick = random.Random(f'YP|{b}|{S.isoformat()}|{d.isoformat()}|{k}').sample(qs, 8)
                it = Y3.item_a_qubits(b, S, Q, pick, f'yprev{k}'); it['id'] = it['id'].replace('A3|', 'A6|', 1) + '|' + d.isoformat(); it['age'] = h; out.append(it)
    return out
def young_stale(recs, k):   # 7 young + 1 stale or 6 young + 2 stale, young from one group under 24 h old, stale from the same record
    out = []
    for b, S, p, Q in recs:
        stale = sorted(q for q in Q if (S - older(Q, q)).total_seconds() > 86400)
        for d, h, qs in Y5.groups(S, Q):
            if h >= 24: continue
            for ny, ns in ((7, 1), (6, 2)):
                if len(qs) < ny or len(stale) < ns: continue
                r = random.Random(f'YS|{b}|{S.isoformat()}|{d.isoformat()}|{ny}|{k}')
                it = Y3.item_a_qubits(b, S, Q, r.sample(qs, ny) + r.sample(stale, ns), f'ystale{ny}{k}'); it['id'] = it['id'].replace('A3|', 'A6|', 1) + '|' + d.isoformat()
                it['age'] = h; it['n_stale'] = ns; out.append(it)
    return out
def sd(recs, side, k):
    out = []
    for b, S, p, Q in recs:
        for d, h, qs in Y5.groups(S, Q):
            if (side == 'old' and h > 24) or (side == 'young' and h < 24):
                it = Y5.item_sd(b, S, Q, d, qs, k, side); it['age'] = h; out.append(it)
    return out
def one_per_record(items, rng, cap=1):
    by = collections.defaultdict(list)
    for i in items: by[i['record']].append(i)
    return [x for r, v in sorted(by.items()) for x in rng.sample(v, min(cap, len(v)))]
def strip(i): return {k: v for k, v in i.items() if k not in ('age', 'n_stale')} | {'age_h': round(i['age'], 2)} | ({'n_stale': i['n_stale']} if 'n_stale' in i else {})
def take(pool, n, rng, name):
    if len(pool) < n: print(f'  {name}: only {len(pool)} available, all used')
    return rng.sample(pool, min(n, len(pool)))
if __name__ == '__main__':
    recs = D.load_records(); test = [r for r in recs if r[1] >= D.CUT]; tr = [r for r in recs if r[1] < D.CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    print('records: train', len(tr), 'valid', len(va), 'test-period', len(test))
    rng = random.Random(771)
    yp, ys = young_prev(tr, 7), young_stale(tr, 7)
    ys7, ys6 = [i for i in ys if i['n_stale'] == 1], [i for i in ys if i['n_stale'] == 2]
    print('TRAIN available: young previous-day', len(yp), '| young with 1 stale', len(ys7), '| young with 2 stale', len(ys6))
    YP = take(yp, 1200, rng, 'young previous-day'); YS = take(ys7, 600, rng, 'young with 1 stale') + take(ys6, 600, rng, 'young with 2 stale')
    SDO = take(sd(tr, 'old', 7) + sd(tr, 'old', 8), 1200, rng, 'same-date older'); SDY = take(sd(tr, 'young', 7), 600, rng, 'same-date younger')
    win = [x for b, S, p, Q in tr for k in range(2) for x in [Y4.item_a_window(b, S, Q, 30 + k)] if x]; A_win = take(win, 2400, rng, 'whole-window')
    bnd = [x for b, S, p, Q in tr for x in [Y4.item_a_band(b, S, Q, 7)] if x]; A_band = take(bnd, 1200, rng, 'band')
    A_rep = rng.sample([D.item_a(b, S, Q, 90) for b, S, p, Q in tr], 1200); C_rep = D.c_pool(tr, 600, 772)
    VA = take(young_prev(va, 0), 50, rng, 'valid yprev') + take(young_stale(va, 0), 50, rng, 'valid ystale') + take(sd(va, 'old', 2), 50, rng, 'valid sdold') + \
         rng.sample([D.item_a(b, S, Q, 80) for b, S, p, Q in va], 100) + D.c_pool(va, 50, 773)
    TR = [strip(i) if 'age' in i else i for i in YP + YS + SDO + SDY] + A_win + A_band + A_rep + C_rep; random.Random(777).shuffle(TR)
    VA = [strip(i) if 'age' in i else i for i in VA]
    lens = [D.ntok(i['prompt'], i['answer']) for i in TR + VA]; print('tokens max', max(lens), 'median', sorted(lens)[len(lens) // 2])
    if max(lens) > D.MAXLEN: sys.exit('REFUSED: item over max length')
    te6 = set(__import__('json').loads(l)['record'] for l in open(HERE + '/data6/test_items.jsonl')); trv = set(f'{b}|{S.isoformat()}' for b, S, p, Q in tr + va); assert not (te6 & trv), 'TEST6 overlaps TRAIN/VALID'
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (('train', TR), ('valid', VA)):
        with open(f'{OUT}/{name}.jsonl', 'w') as fh:
            for i in rows: fh.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(HERE + '/DATA_YO_V7.sha256', 'w') as fh:
        for n in ('train', 'valid'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data6/{n}.jsonl\n')
    print('TRAIN7', len(TR), '(young previous-day', len(YP), 'young with stale', len(YS), 'same-date older', len(SDO), 'same-date younger', len(SDY),
          'whole-window', len(A_win), 'band', len(A_band), 'replay A', len(A_rep), 'C', len(C_rep), ') VALID7', len(VA))
