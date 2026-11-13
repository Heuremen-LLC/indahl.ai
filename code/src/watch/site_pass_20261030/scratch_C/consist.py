import re, json, glob, os, html, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse as P
B = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/')
book = json.load(open(B + 'book_calibrated.json'))
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
print('book rows', len(book), 'pages', len(pages))
# slug mapping
def slug_of(r):
    sid = r['study_id']
    return sid
ids = collections.Counter(r['study_id'] for r in book)
print('dup study_id in book', [k for k, v in ids.items() if v > 1])
print('table counts', collections.Counter(r['table'] for r in book))
missing = [r['study_id'] for r in book if r['study_id'] not in pages]
print('book rows without page (by study_id):', missing[:40], len(missing))
extra = [n for n in pages if n not in {r['study_id'] for r in book}]
print('pages without book row (by study_id):', extra[:60], len(extra))

def norm_id(s):
    if s is None: return None
    return s.replace(':', '-')
bymap = {}
for r in book:
    for k in (r['study_id'], r.get('also')):
        if k: bymap.setdefault(norm_id(k), []).append(r)
unmatched = []
mapping = {}
for n, p in pages.items():
    rs = bymap.get(n)
    if not rs:
        unmatched.append(n); continue
    mapping[n] = rs
print('unmatched pages', unmatched)
amb = {n: [r['id'] for r in rs] for n, rs in mapping.items() if len(rs) > 1}
print('ambiguous', amb)
for r in book:
    if r['study_id'] is None: print('None study_id row', r['id'], r['organisation'], r['study'])
