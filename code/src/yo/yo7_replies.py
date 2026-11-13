"""yo7_replies.py (1 Nov 2026): the reply read PLAN_YO_V7 requires before any comparison. Structural only, no scores: per model and set, how
many replies parse, how many are empty, echo the prompt or run long, how many flagged numbers fall outside the qubits shown (the v6 referee's
catch), then 10 replies per item kind printed in full (fixed seed) for reading. Same parsing as yo6_compare.flagged and yo4_compare."""
import json, os, random, collections, sys
H = os.path.dirname(os.path.abspath(__file__))
def load(f): return {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/{f}')} if os.path.exists(f'{H}/{f}') else {}
T4 = {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/data4/test_items.jsonl')}
T6 = {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/data6/test_items.jsonl')}
FU = {json.loads(l)['id']: json.loads(l) for l in open(f'{H}/data7/future_items.jsonl')} if os.path.exists(f'{H}/data7/future_items.jsonl') else {}
def parsed(out):
    try: return json.loads(out[out.index('{'):out.rindex('}') + 1])
    except Exception: return None
def shown(it): return set(int(l[1:l.index(':')]) for l in it['prompt'].splitlines() if l.startswith('q') and ':' in l)
def kind(iid): return iid.split('|')[0] if '|' not in iid else ('|'.join(p for p in iid.split('|') if p in ('yprev', 'ystale', 'sdold')) or iid.split('|')[0])
rng = random.Random(7)
for name, items, files in (('TEST4', T4, ('eval4_yo_v7.jsonl', 'eval4_yo_v7b.jsonl')), ('TEST6', T6, ('eval6_test6_yo_v7.jsonl', 'eval6_test6_yo_v7b.jsonl')),
                           ('FUTURE7', FU, ('eval6_future7_yo_v4.jsonl', 'eval6_future7_yo_v7.jsonl', 'eval6_future7_yo_v7b.jsonl'))):
    for f in files:
        ev = load(f); c = collections.Counter(); off = []
        for iid, r in ev.items():
            o = r.get('out', ''); p = parsed(o); it = items.get(iid)
            if not o.strip(): c['empty'] += 1
            if p is None and it and it.get('job') != 'C': c['no JSON'] += 1
            if it and it['prompt'][:60] in o: c['echoes prompt'] += 1
            if len(o) > 1500: c['over 1,500 chars'] += 1
            if p and it and isinstance(p, dict) and it.get('job', 'A') == 'A':
                bad = set(int(x) for x in p.get('stale', []) if str(x).lstrip('-').isdigit()) - shown(it)
                if bad: off.append((iid, sorted(bad)))
        print(f'{name} {f}: replies {len(ev)} of {len(items)} items | {dict(c) or "no structural problems"} | off-record flagged numbers: {sum(len(b) for _, b in off)} in {len(off)} items')
        for iid, b in off: print('    off-record', iid, b)
print('\nSAMPLE (10 per kind and model, fixed seed 7), printed in full:')
for name, items, files in (('TEST6', T6, ('eval6_test6_yo_v7.jsonl', 'eval6_test6_yo_v7b.jsonl')), ('TEST4', T4, ('eval4_yo_v7.jsonl', 'eval4_yo_v7b.jsonl'))):
    for f in files:
        ev = load(f); by = collections.defaultdict(list)
        for iid in ev: by[kind(iid) if name == 'TEST6' else items[iid].get('job', '?')].append(iid)
        for k, ids in sorted(by.items()):
            for iid in rng.sample(sorted(ids), min(10, len(ids))):
                print(f'{name} {f} [{k}] {iid[:70]} -> {ev[iid].get("out", "").strip()[:220]}')
