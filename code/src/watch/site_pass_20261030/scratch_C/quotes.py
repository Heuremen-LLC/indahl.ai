import json, re, os, unicodedata, sys
B = os.path.expanduser('~/bones-forge'); H = B + '/qia_leads/recheck_published'
BK = json.load(open(B + '/qia_leads/matrix_page/book_calibrated.json'))
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    for a, b in (('−', '-'), ('–', '-'), ('—', '-'), ('‘', "'"), ('’', "'"), ('“', '"'), ('”', '"'), ('­', ''), ('ﬁ', 'fi'), ('ﬂ', 'fl')):
        s = s.replace(a, b)
    s = re.sub(r'-\s*\n\s*', '', s); s = re.sub(r'\s+', ' ', s); return s.lower()
def squash(s): return re.sub(r'[^0-9a-z]', '', s)
QUO = re.compile(r'"([^"]{8,})"|“([^”]{8,})”|(?<![A-Za-z])\'([^\']{8,}?)\'(?![A-Za-z])')
out = []
for r in BK:
    rid = r['id']; f = f'{H}/src/' + rid.replace('/', '_') + '.txt'
    if not os.path.exists(f): continue
    raw = open(f).read(); txt = norm(raw); sq = squash(txt)
    for fld in ('measured', 'qia_calibration', 'how'):
        v = r.get(fld) or ''
        for g in QUO.findall(v):
            q = [x for x in g if x][0]
            nq = norm(q)
            parts = [p.strip() for p in re.split(r'\s*\.\.\.\s*|\s*\[\.\.\.\]\s*|…', nq) if p.strip()]
            ok = all((p in txt or squash(p) in sq) for p in parts if len(squash(p)) >= 5)
            out.append((rid, r['study_id'], fld, q, ok, len(parts)))
bad = [o for o in out if not o[4]]
print('quotes in measured/cal/how:', len(out), 'not found verbatim:', len(bad))
for o in bad: print(o[0], '|', o[1], '|', o[2], '|', o[3][:150], '| parts', o[5])
json.dump(bad, open('quotes_bad.json', 'w'), indent=1)
