"""score_dream.py -- scores DREAMTIME (call DREAMTIME_CALL_20261007.txt, b23e787c...). Reads pods/<tag>/answers_*.jsonl + judge.jsonl. For each seat x prompt set (language,
ruler): the mode word (first mode word in any language within the first 40 characters), RIGHT (early: HOLD or NEXT; late: COMMIT), FORCED LANDING (COMMIT on early), the
INSIDE corner (first-token mass on the prompt language's mode words vs on the English ones), and the Italian judge's read on both its rulers, with its agreement with the mode
word. Shot size printed (n = 15 per stage). THE RULER: the spread between Bones' and the seat's own translation on the same seat and language. Raw."""
import json, os, sys, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); tag = sys.argv[1] if len(sys.argv) > 1 else 'r1'; D = os.path.join(HERE, 'pods', tag)
T = json.load(open(os.path.join(HERE, 'translations.json'))); MW = T['modes']
INV = {}
for L, m in MW.items():
    for k, w in m.items(): INV[w.lower()] = k
JW = {'conferma': 'COMMIT', 'aspetta': 'HOLD', 'prossimo': 'NEXT', 'entrambi': 'BOTH'}
def mode_of(text):
    t = text.strip().lower()[:60]; best = None
    for w, k in INV.items():
        i = t.find(w.lower())
        if i >= 0 and (best is None or i < best[0]): best = (i, k)
    return best[1] if best else 'NONE'
A = [json.loads(l) for s in ('en', 'th', 'eu') if os.path.exists(f'{D}/answers_{s}.jsonl') for l in open(f'{D}/answers_{s}.jsonl')]
J = {}
if os.path.exists(f'{D}/judge.jsonl'):
    for l in open(f'{D}/judge.jsonl'):
        r = json.loads(l); w = re.sub(r'[^a-zà-ù]', ' ', r['judge'].lower()).split()
        J[(r['seat'], r['lang'], r['ruler'], r['id'], r['judge_ruler'])] = next((JW[x] for x in w if x in JW), 'NONE')
cells = collections.defaultdict(list)
for a in A: cells[(a['seat'], a['lang'], a['ruler'])].append(a)
print(f'DREAMTIME {tag}: {len(A)} answers. Cells: seat x (prompt language, ruler). n = 15 early + 15 late per cell.')
print(f'   {"seat":4} {"lang":4} {"ruler":6} | {"right":>5} {"FORCED (COMMIT on early)":>24} {"late COMMIT":>11} {"no mode":>7} | inside: own-lang / English first-token mass | judge (bones / own) agrees w/ mode')
res = {}
for (seat, L, ru), xs in sorted(cells.items()):
    md = {x['id']: mode_of(x['answer']) for x in xs}
    early = [x for x in xs if x['id'].endswith('e')]; late = [x for x in xs if x['id'].endswith('l')]
    right = sum(md[x['id']] in ('HOLD', 'NEXT') for x in early) + sum(md[x['id']] == 'COMMIT' for x in late)
    forced = sum(md[x['id']] == 'COMMIT' for x in early); lc = sum(md[x['id']] == 'COMMIT' for x in late); none = sum(v == 'NONE' for v in md.values())
    own = [sum(x['first_token_mass'].get(w, 0) for w in MW[L].values()) for x in xs]; eng = [sum(x['first_token_mass'].get(w, 0) for w in MW['en'].values()) for x in xs]
    ja = []
    for jr in ('bones', 'seat'):
        js = [J.get((seat, L, ru, x['id'], jr)) for x in xs]; ok = [j for j in js if j]
        ja.append(f"{sum(j == md[x['id']] for j, x in zip(js, xs) if j)}/{len(ok)}" if ok else '-')
    res[(seat, L, ru)] = (right, forced)
    print(f'   {seat:4} {L:4} {ru:6} | {right:3}/30 {forced:13}/15 {lc:10}/15 {none:7} | {sum(own) / len(own):.3f} / {sum(eng) / len(eng):.3f} | {ja[0]} / {ja[1]}')
print(' THE RULER (Bones vs the seat\'s own translation, same seat, same language): forced landings')
for seat in ('en', 'th', 'eu'):
    for L in ('th', 'eu'):
        b, s = res.get((seat, L, 'bones')), res.get((seat, L, 'seat'))
        if b and s: print(f'   seat {seat} in {L}: Bones {b[1]}/15, seat-translated {s[1]}/15 -> ruler spread {abs(b[1] - s[1])}')
