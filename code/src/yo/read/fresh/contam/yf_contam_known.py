"""Known-positive check for yf_contam.py (/tp 5 Nov: the planted test only proved the ceiling for a copied prompt; the alternative that matters
is the SAME WORK under another DOI). Fresh papers already known to be the same work as one of the 688 (List version field, Sage's 4 pairs)
must read as shared IF their twin was trained on. Inputs only."""
import json, re, os, sys, collections
H = os.path.expanduser('~/bones-forge/yo/read/fresh')
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))   # USED, PAIRS, yd, Q
sys.argv = ['x']; ns = {}; exec(open(H + '/contam/yf_contam.py').read().split("fresh = rows(")[0], ns)   # train_s, sents, rows
train_s, sents, rows = ns['train_s'], ns['sents'], ns['rows']
split = {k: yd.split(k) for k in USED}
L = json.load(open(Q + 'matrix_page/list.json')); lr = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
by = {yd.norm(r['link']): r for r in lr}
fresh = rows(H + '/data/test_items_fresh.jsonl'); fp = collections.defaultdict(set)
for r in fresh: fp[r['paper']] |= sents(r['prompt'])
known = {}
for k in fp:
    v = str(by.get(k, {}).get('version', '')); m = re.search(r'(10\.\d{4,9}/[^\s)]+)', v) if 'open copy read' in v else None
    if m and 'doi:' + m.group(1).lower().rstrip('/.') in USED: known[k] = ('version field', 'doi:' + m.group(1).lower().rstrip('/.'))
    elif k in PAIRS: known[k] = ('Sage pair', PAIRS[k])
print(f'known same-work fresh papers: {len(known)}')
for k, (how, twin) in sorted(known.items(), key=lambda x: split.get(x[1][1], '')):
    ss = fp[k]; sh = [s for s in ss if s in train_s]
    print(f'  {k} <- {twin} [{how}; twin split {split.get(twin, "?")}]: {len(sh)} of {len(ss)} shown sentences in training ({len(sh)/len(ss) if ss else 0:.3f})')
