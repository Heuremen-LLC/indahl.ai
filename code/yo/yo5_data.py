"""yo5_data.py -- builds YO v5 data per PLAN_YO_V5.md (committed c3b5b8c before this file). Reuses yo2_data's record reader, prompt format and
answer rules, yo3_data's item builders and yo4_data's whole-window and band builders unchanged. TRAIN5/VALID5 from the v2 TRAIN/VALID records;
TEST5 from TEST-period records (no v5 training item comes from that period). A same-date group is the set of qubits in one record whose older
T1/T2 date is identical; only groups of 8 or more are used."""
import json, random, os, sys, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yo2_data as D, yo3_data as Y3, yo4_data as Y4
OUT = HERE + '/data5'
def groups(S, Q):   # older T1/T2 date -> qubits, groups of 8 or more, with the age in hours
    g = collections.defaultdict(list)
    for q in Q: g[min(D.when(Q[q][f][1]) for f in ('T1', 'T2'))].append(q)
    return [(d, (S - d).total_seconds() / 3600, sorted(qs)) for d, qs in sorted(g.items()) if len(qs) >= 8]
def item_sd(b, S, Q, d, qs, k, kind):
    pick = random.Random(f'SD|{b}|{S.isoformat()}|{d.isoformat()}|{k}').sample(qs, 8)
    it = Y3.item_a_qubits(b, S, Q, pick, f'sd{kind}{k}'); it['id'] = it['id'].replace('A3|', 'A5|', 1) + '|' + d.isoformat(); it['age'] = None
    return it
def sd_items(recs, side, draws=1):
    out = []
    for b, S, p, Q in recs:
        for d, h, qs in groups(S, Q):
            if (side == 'old' and h > 24) or (side == 'young' and h < 24):
                for k in range(draws): it = item_sd(b, S, Q, d, qs, k, side); it['age'] = h; out.append(it)
    seen, uniq = set(), []
    for it in out:
        if it['prompt'] not in seen: seen.add(it['prompt']); uniq.append(it)
    return uniq
def band(items, lo, hi): return [i for i in items if lo <= i['age'] < hi]
def one_per_record(items, rng):
    by = collections.defaultdict(list)
    for i in items: by[i['record']].append(i)
    return [rng.choice(v) for k, v in sorted(by.items())]
def strip(i): return {k: v for k, v in i.items() if k != 'age'} | {'age_h': round(i['age'], 2)}
if __name__ == '__main__':
    recs = D.load_records(); test = [r for r in recs if r[1] >= D.CUT]; tr = [r for r in recs if r[1] < D.CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    print('records: train', len(tr), 'valid', len(va), 'test-period', len(test))
    rng = random.Random(551)
    old_tr = sd_items(tr, 'old', 2); young_tr = sd_items(tr, 'young')
    print('TRAIN same-date older available', len(old_tr), '| younger 20-24', len(band(young_tr, 20, 24)), '12-20', len(band(young_tr, 12, 20)), 'under 12', len(band(young_tr, 0, 12)))
    SD_old = rng.sample(old_tr, min(1200, len(old_tr)))
    SD_young = rng.sample(band(young_tr, 20, 24), 400) + rng.sample(band(young_tr, 12, 20), 400) + rng.sample(band(young_tr, 0, 12), 400)
    win_tr = [x for b, S, p, Q in tr for k in range(2) for x in [Y4.item_a_window(b, S, Q, k + 10)] if x]
    band_tr = [x for b, S, p, Q in tr for x in [Y4.item_a_band(b, S, Q, 1)] if x]
    A_win = rng.sample(win_tr, 1200); A_band = rng.sample(band_tr, 1200)
    A_rep = rng.sample([D.item_a(b, S, Q, 70) for b, S, p, Q in tr], 1200); C_rep = D.c_pool(tr, 600, 552)
    old_va = sd_items(va, 'old'); young_va = sd_items(va, 'young')
    VA = rng.sample(old_va, min(50, len(old_va))) + rng.sample(young_va, min(50, len(young_va))) + rng.sample([D.item_a(b, S, Q, 70) for b, S, p, Q in va], 100) + D.c_pool(va, 50, 553)
    old_te = sd_items(test, 'old'); young_te = sd_items(test, 'young')
    by = collections.defaultdict(list)
    for i in old_te: by[i['record']].append(i)
    old_te2 = [x for k, v in sorted(by.items()) for x in random.Random(f'T5|{k}').sample(v, min(2, len(v)))]
    T_old = rng.sample(old_te2, min(300, len(old_te2)))
    y1 = one_per_record(band(young_te, 18, 24), random.Random(554)); y2 = one_per_record(band(young_te, 0, 18), random.Random(555))
    T_young = rng.sample(y1, min(150, len(y1))) + rng.sample(y2, min(150, len(y2)))
    print('TEST5 same-date older available', len(old_te2), 'drawn', len(T_old), '| younger 18-24 records', len(y1), 'under 18 records', len(y2), 'drawn', len(T_young))
    TR = [strip(i) if 'age' in i else i for i in SD_old + SD_young] + A_win + A_band + A_rep + C_rep; random.Random(556).shuffle(TR)
    VA = [strip(i) if 'age' in i else i for i in VA]
    lens = [D.ntok(i['prompt'], i['answer']) for i in TR + VA]; print('tokens max', max(lens), 'median', sorted(lens)[len(lens) // 2])
    if max(lens) > D.MAXLEN: sys.exit('REFUSED: item over max length')
    te = [strip(i) for i in T_old + T_young]; te_recs = set(i['record'] for i in te)
    trv = set(f'{b}|{S.isoformat()}' for b, S, p, Q in tr + va); assert not (te_recs & trv), 'TEST5 overlaps TRAIN/VALID'
    assert all(json.loads(i['answer'])['stale'] == sorted(int(x) for x in __import__('re').findall(r'^q(\d+):', i['prompt'], 8)) for i in te if '|sdold' in i['id']), 'an older same-date item is not all stale'
    assert all(json.loads(i['answer'])['stale'] == [] for i in te if '|sdyoung' in i['id']), 'a younger same-date item has a stale qubit'
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (('train', TR), ('valid', VA)):
        with open(f'{OUT}/{name}.jsonl', 'w') as fh:
            for i in rows: fh.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(f'{OUT}/test_items.jsonl', 'w') as fh:
        for i in te: fh.write(json.dumps(i) + '\n')
    with open(HERE + '/DATA_YO_V5.sha256', 'w') as fh:
        for n in ('train', 'valid', 'test_items'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data5/{n}.jsonl\n')
    print('TRAIN5', len(TR), '(same-date older', len(SD_old), 'younger', len(SD_young), 'whole-window', len(A_win), 'band', len(A_band), 'replay A', len(A_rep), 'C', len(C_rep),
          ') VALID5', len(VA), '| TEST5 same-date older', len(T_old), 'younger', len(T_young))
