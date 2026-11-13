"""Rerun of the same-author / metadata match for the 10 trained papers whose training text came from another record (yf_textrecord.out):
match every primary and sensitivity paper against the metadata of the record ACTUALLY READ. Inputs only; records fetched read-only."""
import json, os, re, urllib.request, urllib.parse, unicodedata
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); M = json.load(open(H + '/contam/meta_cache.json'))
READ = {'ax:2205.00864': 'doi:10.1103/physrevc.106.034325', 'ax:2408.07997': 'doi:10.1002/qute.70484', 'ax:2411.19308': 'doi:10.1145/3695053.3731036',
        'ax:2502.20710': 'doi:10.1145/3676536.3676689', 'doi:10.5281/zenodo.19303627': 'doi:10.5281/zenodo.18671523', 'doi:10.5281/zenodo.20108939': 'doi:10.5281/zenodo.20108875',
        'doi:10.5281/zenodo.21987398': 'doi:10.5281/zenodo.21987397', 'doi:10.5281/zenodo.22644883': 'doi:10.5281/zenodo.22072152',
        'doi:10.5281/zenodo.22809021': 'doi:10.5281/zenodo.22736832', 'doi:10.5281/zenodo.22849729': 'doi:10.5281/zenodo.19633727'}
UA = {'User-Agent': 'Heuremen-LLC-research/1.0 (mailto:heuremen@heuremen.com)'}
for r in READ.values():
    if r in M: continue
    d = r[4:]
    if 'zenodo.' in d:
        m = json.loads(urllib.request.urlopen(urllib.request.Request('https://zenodo.org/api/records/' + d.rsplit('zenodo.', 1)[1], headers=UA), timeout=40).read())['metadata']
        M[r] = dict(title=m.get('title'), authors=[c.get('name') for c in m.get('creators', [])], src='zenodo')
    else:
        m = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/' + urllib.parse.quote(d), headers=UA), timeout=40).read())['message']
        M[r] = dict(title=(m.get('title') or [None])[0], authors=[' '.join(filter(None, (a.get('given'), a.get('family')))) for a in m.get('author', [])], src='crossref')
json.dump(M, open(H + '/contam/meta_cache.json', 'w'), indent=0)
def names(k):
    out = set()
    for n in filter(None, M.get(k, {}).get('authors') or []):
        n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower(); n = re.sub(r'\b(dr|prof|mr|mrs|ms|phd|md)\b\.?', ' ', n).strip(' ,')
        last, first = ([x.strip() for x in n.split(',', 1)] if ',' in n else ((n.split() or [''])[-1], (n.split() or [''])[0]))
        if re.sub(r'[^a-z]', '', last): out.add(re.sub(r'[^a-z]', '', last) + ' ' + re.sub(r'[^a-z]', '', first)[:1])
    return out
STOP = set('the and for with from via into onto using use under over its our their this that are was were has have not but can quantum'.split())
tw = lambda t: {w for w in re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()) if len(w) >= 3 and w not in STOP}
ps = set(open(H + '/primary_ids.txt').read().split()) | set(open(H + '/sensitivity_ids.txt').read().split())
hits = 0
for k, r in READ.items():
    a2, t2 = names(r), tw(M[r].get('title'))
    print(f'{k} read via {r}: {(M[r].get("title") or "")[:80]} | {", ".join((M[r].get("authors") or [])[:3])}')
    for f in sorted(ps):
        a1, t1 = names(f), tw(M[f].get('title'))
        A = len(a1 & a2) / min(len(a1), len(a2)) if a1 and a2 else 0.0; T = len(t1 & t2) / len(t1 | t2) if t1 and t2 else 0.0
        if A >= 0.5 or T >= 0.3: hits += 1; print(f'    HIT {f}: authors {A:.2f} title {T:.2f} | {(M[f].get("title") or "")[:80]}')
print(f'hits in primary/sensitivity: {hits}')
