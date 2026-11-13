"""yf_contam_meta.py -- Sage 5 Nov: same-work versions often share little text, but they share AUTHORS and TITLE. Inputs only.
For each paper, every trained paper (TRAIN+VALID of the 688) is scored on:
  A = author-surname overlap |S1 & S2| / min(|S1|, |S2|)   (surname = last word of the name, ascii-lowercased; empty list -> 0)
  T = title-word Jaccard (lowercase words of 3+ letters, minus a short stopword list)
FLAG RULE, fixed before any score was seen (5 Nov, this docstring is committed with the first run):
  the top-scoring trained paper (score A + T) is flagged as a possible same work if (A >= 0.5 and T >= 0.3) or T >= 0.6.
KNOWN-GOOD first: the 8 known same-work fresh papers whose twin was trained must have the twin as top match AND be flagged.
  Sage's bar: at least 7 of 8. FLOOR: the same rule on the 148 TEST papers (never trained) gives the false-hit rate.
Every fresh primary/sensitivity paper it flags is read by hand beside its match before any output is read."""
import json, os, re, unicodedata, collections
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); Q = os.path.expanduser('~/bones-forge/qia_leads/')
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))
M = json.load(open(H + '/contam/meta_cache.json'))
STOP = set('the and for with from via into onto using use under over its our their this that are was were has have not but can quantum'.split())
def sur(n):
    n = unicodedata.normalize('NFKD', n or '').encode('ascii', 'ignore').decode().lower()
    n = n.split(',')[0] if ',' in n else n.split()[-1] if n.split() else ''
    return re.sub(r'[^a-z]', '', n)
def tw(t): return {w for w in re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()) if len(w) >= 3 and w not in STOP}
def feats(k): m = M.get(k, {}); return ({s for s in map(sur, m.get('authors') or []) if s}, tw(m.get('title')))
TR = sorted(k for k in USED if yd.split(k) in ('TRAIN', 'VALID')); TE = sorted(k for k in USED if yd.split(k) == 'TEST')
FT = {k: feats(k) for k in TR}
def top(k):
    a1, t1 = feats(k); sc = []
    for j in TR:
        if j == k: continue
        a2, t2 = FT[j]
        A = len(a1 & a2) / min(len(a1), len(a2)) if a1 and a2 else 0.0
        T = len(t1 & t2) / len(t1 | t2) if t1 and t2 else 0.0
        sc.append((A + T, A, T, j))
    sc.sort(reverse=True); b = sc[0]; m2 = sc[1][0] if len(sc) > 1 else 0.0
    flag = (b[1] >= 0.5 and b[2] >= 0.3) or b[2] >= 0.6
    return dict(match=b[3], score=b[0], A=b[1], T=b[2], margin=b[0] - m2, flag=flag, has_meta=bool(a1 or t1))
fresh = {json.loads(l)['paper'] for l in open(H + '/data/test_items_fresh.jsonl')}
L = json.load(open(Q + 'matrix_page/list.json')); lr = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
by = {yd.norm(r['link']): r for r in lr}; known = {}
for k in fresh:
    v = str(by.get(k, {}).get('version', '')); m = re.search(r'(10\.\d{4,9}/[^\s)]+)', v) if 'open copy read' in v else None
    if m and 'doi:' + m.group(1).lower().rstrip('/.') in USED: known[k] = 'doi:' + m.group(1).lower().rstrip('/.')
    elif k in PAIRS: known[k] = PAIRS[k]
print(f'metadata: {sum(1 for k in list(fresh) + TR + TE if M.get(k, {}).get("authors"))} of {len(fresh) + len(TR) + len(TE)} papers have authors')
print('\n== KNOWN-GOOD (trained twins): twin must be top match and flagged')
ok = 0; n = 0
for k, t in sorted(known.items()):
    if t not in TR: continue
    r = top(k); n += 1; hit = r['match'] == t and r['flag']; ok += hit
    print(f'  {k} <- {t}: top {r["match"]} A {r["A"]:.2f} T {r["T"]:.2f} margin {r["margin"]:.2f} flag {r["flag"]}  {"FOUND" if hit else "MISSED"}')
print(f'known-good: {ok} of {n} (bar: 7 of 8)')
fl = [top(k) for k in TE]
print(f'\n== FLOOR: 148 TEST papers flagged: {sum(r["flag"] for r in fl)} ({sum(r["flag"] for r in fl) / len(fl):.3f}); no metadata: {sum(not r["has_meta"] for r in fl)}')
for k, r in zip(TE, fl):
    if r['flag']: print(f'  {k} ~ {r["match"]}: A {r["A"]:.2f} T {r["T"]:.2f}')
prim = set(open(H + '/primary_ids.txt').read().split()); sens = set(open(H + '/sensitivity_ids.txt').read().split())
for name, ids in (('primary', prim), ('sensitivity', sens), ('full', fresh)):
    rs = {k: top(k) for k in sorted(ids)}
    print(f'\n== FRESH {name}: {len(rs)} papers; flagged {sum(r["flag"] for r in rs.values())}; no metadata {sum(not r["has_meta"] for r in rs.values())}')
    for k, r in rs.items():
        if r['flag']: print(f'  FLAG {k} ~ {r["match"]}: A {r["A"]:.2f} T {r["T"]:.2f} margin {r["margin"]:.2f}' + ('  [known same work]' if k in known else ''))
