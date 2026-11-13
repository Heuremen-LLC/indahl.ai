#!/usr/bin/env python3
"""frame_fedreg.py: Federal Register sample (PLAN.md Addendum 3, sample G1). Builds the frame and, once the seed exists, the draw.
Frame: every document the federalregister.gov API (keyless) returns for the search term "http", published 1995-01-01 to 2017-12-31,
listed month by month so no query passes the API's result cap. Eras by publication date: 1995-1996, 1997-2001, 2002-2008, 2009-2017.
Draw, per era: documents in key order (frames_common.key); each one's raw text is read and its addresses are the href values of its
<a> tags, minus the delivery header line ("From the Federal Register Online via ..."), minus example and reserved hosts. A document
with no address is passed over and counted. The first 150 documents with an address are the sample, and from each the one address
with the smallest key is drawn. The unit is that document's drawn address; the same address drawn from two documents is read once
and counted for each.
Usage: python3 -I frame_fedreg.py build   |   python3 -I frame_fedreg.py draw"""
import os, sys, re, json, calendar, urllib.parse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'early'))
import frames_common as F
OUT = os.path.join(os.path.dirname(H), 'data', 'gov')
ERAS = (('1995-1996', 1995, 1996), ('1997-2001', 1997, 2001), ('2002-2008', 2002, 2008), ('2009-2017', 2009, 2017))
PER_ERA = 150
API = 'https://www.federalregister.gov/api/v1/documents.json?'

def era_of(y):
    for name, a, b in ERAS:
        if a <= y <= b: return name

def build():
    path = os.path.join(OUT, 'frame_fedreg.json'); have = json.load(open(path)) if os.path.exists(path) else {'months': {}, 'docs': {}}
    for y in range(1995, 2018):
        for m in range(1, 13):
            mk = '%04d-%02d' % (y, m)
            if mk in have['months']: continue
            last = calendar.monthrange(y, m)[1]; page, n = 1, 0
            while True:
                q = [('conditions[term]', 'http'), ('conditions[publication_date][gte]', '%s-01' % mk), ('conditions[publication_date][lte]', '%s-%02d' % (mk, last)),
                     ('per_page', '1000'), ('page', str(page)), ('order', 'oldest')] + [('fields[]', f) for f in ('document_number', 'publication_date', 'raw_text_url', 'type')]
                d = json.loads(F.get(API + urllib.parse.urlencode(q)))
                if d.get('count', 0) >= 10000: raise SystemExit('month %s reaches the API cap; split it' % mk)
                for r in d.get('results', []):
                    have['docs'][r['document_number']] = dict(date=r['publication_date'], raw=r.get('raw_text_url'), type=r.get('type'), era=era_of(int(r['publication_date'][:4])))
                    n += 1
                if not d.get('next_page_url'): break
                page += 1
            have['months'][mk] = dict(count=d.get('count', 0), listed=n)
            F.write_json(path, have); print(mk, d.get('count', 0), flush=True)
    print('frame: %d documents' % len(have['docs']))

HDR = re.compile(r'^From the Federal Register Online via.*$', re.M)
HREF = re.compile(r'<a\s[^>]*?href\s*=\s*["\']([^"\']+)["\']', re.I)
def addresses(raw_text):
    t = HDR.sub('', raw_text); out = []
    for h in HREF.findall(t):
        u = F.norm(h)
        if u and not F.EXAMPLE_HOSTS.search(urllib.parse.urlsplit(u).hostname or ''): out.append(u)
    return sorted(set(out))

def draw():
    sd = F.seed(); fr = json.load(open(os.path.join(OUT, 'frame_fedreg.json')))
    cache = os.path.join(OUT, 'text_cache'); os.makedirs(cache, exist_ok=True)
    path = os.path.join(OUT, 'sample_fedreg.json'); out = json.load(open(path)) if os.path.exists(path) else {'units': [], 'passed_over': {}, 'read': {}}
    done_docs = {u['doc'] for u in out['units']} | set(x for v in out['passed_over'].values() for x in v)
    for name, a, b in ERAS:
        docs = sorted((F.key(sd, 'fedreg', dn), dn) for dn, d in fr['docs'].items() if d['era'] == name)
        got = sum(1 for u in out['units'] if u['era'] == name); out['read'].setdefault(name, 0)
        for k, dn in docs:
            if got >= PER_ERA: break
            if dn in done_docs: continue
            d = fr['docs'][dn]; cp = os.path.join(cache, dn + '.txt')
            if os.path.exists(cp): txt = open(cp, encoding='utf-8', errors='replace').read()
            else:
                try: txt = F.get(d['raw']).decode('utf-8', 'replace')
                except Exception as e: print('skip (fetch failed, retried next run)', dn, e); continue
                open(cp, 'w', encoding='utf-8').write(txt)
            out['read'][name] += 1
            addrs = addresses(txt)
            if not addrs: out['passed_over'].setdefault(name, []).append(dn); continue
            pick = min(addrs, key=lambda u: F.key(sd, 'fedreg|' + dn, u))
            out['units'].append(dict(id='fedreg|' + dn, doc=dn, date=d['date'], era=name, url=pick, key=k, addresses_in_doc=len(addrs))); got += 1
            F.write_json(path, out)
        print(name, 'units', got, 'passed over', len(out['passed_over'].get(name, [])), flush=True)
    out['frame_counts'] = {name: sum(1 for d in fr['docs'].values() if d['era'] == name) for name, _, _ in ERAS}
    F.write_json(path, out)

if __name__ == '__main__':
    {'build': build, 'draw': draw}[sys.argv[1]]()
