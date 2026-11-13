# own PDF level check: does the issue PDF have a page with "95% NYMEX", "confidence", and the series name on the SAME page?
import sys, json, re, os
import pypdf
D = '/Users/heuremen/bones-forge/steo_index/data/'
rows = json.load(open('../out/rows.json'))
issues = sorted({(r['issue'], r['series']) for r in rows if r['level'] is None})
out = {}
cache = {}
for iss, s in issues:
    f = D+'raw/archives/%s.pdf' % iss
    if not os.path.exists(f): out['%s/%s' % (iss, s)] = None; continue
    if iss not in cache:
        pages = []
        for pg in pypdf.PdfReader(f).pages:
            try: pages.append(pg.extract_text() or '')
            except Exception: pages.append('')
        cache[iss] = pages
    res = {'pagehit': False, 'anywhere95': False}
    for tx in cache[iss]:
        if re.search(r'95\s*%\s*NYMEX', tx): res['anywhere95'] = True
        if re.search(r'95\s*%\s*NYMEX', tx) and re.search('confidence', tx, re.I) and re.search(r'West Texas|WTI' if s == 'WTI' else 'Henry Hub', tx): res['pagehit'] = True
    out['%s/%s' % (iss, s)] = res
json.dump(out, open('../out/pdf_levels_ref.json', 'w'), indent=0)
desk = json.load(open(D+'pdf_levels.json'))
dif = [(k, out.get(k), desk.get(k)) for k in set(out) | set(desk) if (out.get(k) or {}).get('pagehit') != desk.get(k)]
print(len(out), 'keys; diffs vs desk pdf_levels.json:', dif)
print({k: v for k, v in out.items() if not (v and v['pagehit'])})
