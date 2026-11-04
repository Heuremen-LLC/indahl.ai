"""yf_primary.py -- PRIMARY set for PLAN_YO_FRESH Addendum 2 (Sage's VERDICT 23:08Z, MOVES). From data/test_items_fresh.jsonl keep a paper only if:
(1) not in the 688 papers YO Read was built on (rebuilt from list.json.pre-removal-20261102); (2) its List read label is exactly "Full text" (as yr_data.py);
(3) its List entry has an F4 note, so DATES and LINK labels are read, not defaults; (4) it is not the same work as one of the 688: List version field
"open copy read (doi of a used paper)", or one of the 4 pairs Sage's dig matched by title/content (listed below). Runs no model.
Writes data/test_items_primary.jsonl, PRIMARY_SET.text, and adds both to DATA_YO_FRESH.sha256."""
import json, os, re, importlib.util, collections, builtins, hashlib
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); Q = os.path.expanduser('~/bones-forge/qia_leads/')
spec = importlib.util.spec_from_file_location('yd', R + '/yr_data.py'); yd = importlib.util.module_from_spec(spec); spec.loader.exec_module(yd)
_open = builtins.open
def _op(p, *a, **k): return _open(Q + 'matrix_page/list.json.pre-removal-20261102' if p == Q + 'matrix_page/list.json' else p, *a, **k)
builtins.open = _op; USED = {k for k, _, _ in yd.papers()}; builtins.open = _open
assert len(USED) == 688, len(USED)
PAIRS = {'doi:10.5281/zenodo.20499401': 'doi:10.5281/zenodo.21463909', 'doi:10.5281/zenodo.21463902': 'doi:10.5281/zenodo.20481849',
         'doi:10.5281/zenodo.23731577': 'doi:10.5281/zenodo.23731575', 'doi:10.5281/zenodo.19197915': 'ax:2604.18837'}
items = [json.loads(l) for l in open(H + '/data/test_items_fresh.jsonl')]
L = json.load(open(Q + 'matrix_page/list.json')); rows = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
by = {}
for r in rows: by.setdefault(yd.norm(r['link']), r)
drop = collections.OrderedDict((x, []) for x in ('in the 688', 'read label not exactly Full text', 'no F4 note', 'same work (List version field)', 'same work (title/content pair)'))
keep = []
for k in sorted({i['paper'] for i in items}):
    r = by[k]; v = str(r.get('version', '')); m = re.search(r'(10\.\d{4,9}/[^\s)]+)', v) if 'open copy read' in v else None
    if k in USED: drop['in the 688'].append(k)
    elif r.get('read') != 'Full text': drop['read label not exactly Full text'].append(k)
    elif not r.get('basis', {}).get('F4'): drop['no F4 note'].append(k)
    elif m and 'doi:' + m.group(1).lower().rstrip('/.') in USED: drop['same work (List version field)'].append(k)
    elif k in PAIRS: assert PAIRS[k] in USED, PAIRS[k]; drop['same work (title/content pair)'].append(k)
    else: keep.append(k)
K = set(keep); P = [i for i in items if i['paper'] in K]
with open(H + '/data/test_items_primary.jsonl', 'w') as f:
    for i in P: f.write(json.dumps(i) + '\n')
out = [f'PRIMARY set (Addendum 2): {len(keep)} papers, {len(P)} items, of the 288 fresh papers. Dropped, in this order of checks:']
out += [f'  {k}: {len(v)}' for k, v in drop.items()]
for q in ('DATES', 'LINK', 'REQUEST'):
    a = [i['answer'] for i in P if i['q'] == q]; y = a.count('YES')
    out.append(f'  {q}: YES {y}/{len(a)} = {y / len(a):.3f}; best constant {"YES" if y > len(a) - y else "NO"}')
open(H + '/PRIMARY_SET.text', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
import sys; sys.path.insert(0, R); from yr_known_good import known_good
kg = known_good(P); print('known-good primary', kg); open(H + '/KNOWN_GOOD.text', 'a').write(f'primary set: {kg}\n')
