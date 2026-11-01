"""yo4_data.py -- builds YO v4 data per PLAN_YO_V4.md (committed 8c5a448 before this file). Reuses yo2_data's record reader, prompt format and
answer rules and yo3_data's item builders unchanged. TRAIN4/VALID4 from the v2 TRAIN/VALID records; TEST4 from TEST-period records that no v2 TEST
item and no TEST3 item came from."""
import json, random, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yo2_data as D, yo3_data as Y3
OUT = HERE + '/data4'
def item_a_window(b, S, Q, k):   # all 8 qubits from the 20 to 50 h window, from records that hold at least 8 such qubits
    g = Y3.gaps(S, Q); win = sorted(q for q in Q if 20 <= g[q] <= 50)
    if len(win) < 8: return None
    it = Y3.item_a_qubits(b, S, Q, random.Random(f'A4win|{b}|{S.isoformat()}|{k}').sample(win, 8), f'win{k}'); it['id'] = it['id'].replace('A3|', 'A4|', 1); return it
def item_a_band(b, S, Q, k):
    it = Y3.item_a_band(b, S, Q, k + 40)
    if it: it['id'] = it['id'].replace('A3|', 'A4|', 1)
    return it
if __name__ == '__main__':
    recs = D.load_records(); test = [r for r in recs if r[1] >= D.CUT]; tr = [r for r in recs if r[1] < D.CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    used = set(json.loads(l)['record'] for f in ('/data2/test_items.jsonl', '/data3/test_items.jsonl') for l in open(HERE + f))
    fresh = [r for r in test if f'{r[0]}|{r[1].isoformat()}' not in used]
    print('records: train', len(tr), 'valid', len(va), 'test-period', len(test), 'fresh for TEST4', len(fresh))
    rng = random.Random(441)
    win_tr = [x for b, S, p, Q in tr for k in range(2) for x in [item_a_window(b, S, Q, k)] if x]
    band_tr = [x for b, S, p, Q in tr for x in [item_a_band(b, S, Q, 0)] if x]
    print('TRAIN whole-window items available', len(win_tr), 'band items available', len(band_tr))
    A_win = rng.sample(win_tr, 2400); A_band = rng.sample(band_tr, 1200)
    A_rep = rng.sample([D.item_a(b, S, Q, k + 50) for b, S, p, Q in tr for k in range(1)], 1200); C_rep = D.c_pool(tr, 600, 442)
    win_va = [x for b, S, p, Q in va for x in [item_a_window(b, S, Q, 0)] if x]
    A_va = rng.sample(win_va, min(100, len(win_va))) + rng.sample([D.item_a(b, S, Q, 50) for b, S, p, Q in va], 100); C_va = D.c_pool(va, 50, 443)
    win_te = [x for b, S, p, Q in fresh for x in [item_a_window(b, S, Q, 0)] if x]
    print('TEST4 whole-window records available', len(win_te))
    A_te_win = rng.sample(win_te, min(200, len(win_te))); A_te = rng.sample([D.item_a(b, S, Q, 60) for b, S, p, Q in fresh], 200)
    C_te = Y3.c_pool_n(fresh, 100, 444, 40)
    TR = A_win + A_band + A_rep + C_rep; VA = A_va + C_va; random.Random(445).shuffle(TR)
    lens = [D.ntok(i['prompt'], i['answer']) for i in TR + VA]; print('tokens max', max(lens), 'median', sorted(lens)[len(lens) // 2])
    if max(lens) > D.MAXLEN: sys.exit('REFUSED: item over max length')
    te_recs = set(i['record'] for i in A_te_win + A_te + C_te); assert not (te_recs & used), 'TEST4 overlaps v2 TEST or TEST3'
    trv = set(f'{b}|{S.isoformat()}' for b, S, p, Q in tr + va); assert not (te_recs & trv), 'TEST4 overlaps TRAIN/VALID'
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (('train', TR), ('valid', VA)):
        with open(f'{OUT}/{name}.jsonl', 'w') as fh:
            for i in rows: fh.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(f'{OUT}/test_items.jsonl', 'w') as fh:
        for i in A_te_win + A_te + C_te: fh.write(json.dumps(i) + '\n')
    with open(HERE + '/DATA_YO_V4.sha256', 'w') as fh:
        for n in ('train', 'valid', 'test_items'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data4/{n}.jsonl\n')
    print('TRAIN4', len(TR), '(whole-window', len(A_win), 'band', len(A_band), 'replay A', len(A_rep), 'C', len(C_rep), ') VALID4', len(VA),
          '| TEST4 whole-window', len(A_te_win), 'general A', len(A_te), 'C', len(C_te))
