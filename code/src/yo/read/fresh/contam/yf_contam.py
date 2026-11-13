"""yf_contam.py -- Sage 5 Nov (pre-flight L3 VERDICT): is "fresh" true against what the adapters were ACTUALLY trained on, not the 688 list?
Inputs only: the fresh items (stamped in Addendum 3) and every train/valid file the nine adapters were trained on (yr*.yaml, shuffled, selflabel).
Reads no model output, no eval_fresh file, no OUTPUTS_YO_FRESH.

A unit is one sentence shown in a prompt (the numbered lines after "Sentences:"), normalised (lowercase, whitespace collapsed), 40+ characters.
For each fresh paper: how many of its distinct shown sentences also appear anywhere in training. Read beside two rulers built first:
  FLOOR   the same count for the original TEST split (148 papers out of the 688, never trained on): what unrelated papers share by chance
          (boilerplate, shared citations).
  PLANTED one training paper's prompts copied in as if fresh: must read as fully shared (the instrument sees an overlap when one exists).
Exact prompt matches are counted too."""
import json, re, sys, os, collections
Y = os.path.expanduser('~/bones-forge/yo/read')
TRAIN = [f'{Y}/data/train.jsonl', f'{Y}/data/valid.jsonl', f'{Y}/shuffled/data/train.jsonl', f'{Y}/shuffled/data/valid.jsonl',
         f'{Y}/shuffled/selflabel/data/train.jsonl', f'{Y}/shuffled/selflabel/data/valid.jsonl']
def sents(prompt):
    body = prompt.split('Sentences:\n', 1)[-1]
    out = set()
    for l in body.split('\n'):
        m = re.match(r'\s*\d+\.\s+(.*)', l)
        if m:
            s = re.sub(r'\s+', ' ', m.group(1).strip().lower())
            if len(s) >= 40: out.add(s)
    return out
def rows(p): return [json.loads(l) for l in open(p) if l.strip()]
train_s, train_p, n_train = collections.Counter(), set(), 0
for f in TRAIN:
    for r in rows(f):
        p = r.get('prompt') or r.get('text') or ''
        if not p and 'messages' in r: p = r['messages'][0]['content']
        train_p.add(p); n_train += 1
        for s in sents(p): train_s[s] += 1
print(f'training: {len(TRAIN)} files, {n_train} rows, {len(train_s)} distinct shown sentences')

def by_paper(items):
    d = collections.defaultdict(set); ex = collections.Counter()
    for r in items:
        d[r['paper']] |= sents(r['prompt'])
        if r['prompt'] in train_p: ex[r['paper']] += 1
    return d, ex
def report(name, items, ids=None):
    d, ex = by_paper(items)
    if ids is not None: d = {k: v for k, v in d.items() if k in ids}
    rows_ = []
    for k, ss in d.items():
        sh = [s for s in ss if s in train_s]
        rows_.append((len(sh) / len(ss) if ss else 0.0, len(sh), len(ss), k, sh))
    rows_.sort(reverse=True)
    fr = [r[0] for r in rows_]
    n_any = sum(1 for r in rows_ if r[1] > 0); n_half = sum(1 for r in rows_ if r[0] >= 0.5)
    print(f'\n== {name}: {len(rows_)} papers; exact prompt matches {sum(ex.get(r[3], 0) for r in rows_)}; '
          f'papers sharing >=1 sentence {n_any}; sharing >=50% {n_half}; max share {max(fr) if fr else 0:.3f}')
    for f_, a, b, k, sh in rows_[:6]:
        print(f'   {k}: {a} of {b} shown sentences also shown in training ({f_:.3f})' + (f'  e.g. "{sh[0][:90]}"' if sh else ''))
    return rows_

fresh = rows(f'{Y}/fresh/data/test_items_fresh.jsonl')
prim = set(open(f'{Y}/fresh/primary_ids.txt').read().split()); sens = set(open(f'{Y}/fresh/sensitivity_ids.txt').read().split())
old_test = rows(f'{Y}/data/test_items.jsonl')
report('FLOOR: original TEST split (in the 688, never trained on)', old_test)
tr0 = rows(f'{Y}/data/train.jsonl')[:3]
planted = [dict(paper='PLANTED:train_rows_0-2', prompt=r['prompt']) for r in tr0]
pr = report('PLANTED: three training prompts posing as a fresh paper', planted)
assert pr[0][0] == 1.0, 'known-good failed: a training prompt did not read as shared'
report('FRESH, primary set', fresh, prim)
report('FRESH, sensitivity set', fresh, sens)
report('FRESH, full set (secondary)', fresh)
