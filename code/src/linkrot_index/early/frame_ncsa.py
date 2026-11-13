#!/usr/bin/env python3
"""frame_ncsa.py: NCSA "What's New" 1993-1996 (PLAN.md Addendum 3, sample E1). Builds the frame and, once the seed exists, the draw.
Frame: every monthly page named whats-new-MMYY.html under www.ncsa.uiuc.edu/SDG/Software/Mosaic/Docs/old-whats-new/ that the
Wayback Machine holds as a 200 text/html capture, each read once at its earliest capture (raw, id_ form). Addresses: the href of every
<a> tag, resolved against the page, http and https only (other schemes counted, not checked), minus the Mosaic documentation tree
(http://www.ncsa.uiuc.edu/SDG/Software/Mosaic/), which holds the column's own navigation. Unit: one distinct address. Era: 1993-1996;
the month of first listing is kept. Draw: the 500 units with the smallest key.
Usage: python3 -I frame_ncsa.py build   |   python3 -I frame_ncsa.py draw"""
import os, sys, re, json, urllib.parse, collections
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import frames_common as F
OUT = os.path.join(F.DATA, 'ncsa'); CACHE = os.path.join(F.DATA, 'ncsa_cache'); N = 500
NAV = 'http://www.ncsa.uiuc.edu/SDG/Software/Mosaic/'
HREF = re.compile(r'<a\s[^>]*?href\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I | re.S)

def build():
    cdx = json.loads(F.get('https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode({'url': 'www.ncsa.uiuc.edu/SDG/Software/Mosaic/Docs/old-whats-new/', 'matchType': 'prefix', 'output': 'json',
                     'fl': 'timestamp,original,mimetype', 'filter': ['statuscode:200', 'mimetype:text/html'], 'collapse': 'urlkey'}, doseq=True), gap=1.2))
    pages = sorted(((r[1], r[0]) for r in cdx[1:] if re.search(r'/whats-new-(\d\d)(\d\d)\.html$', r[1])), key=lambda x: x[0])
    units, schemes, per_page = {}, collections.Counter(), {}
    os.makedirs(CACHE, exist_ok=True)
    for orig, ts in pages:
        mm, yy = re.search(r'whats-new-(\d\d)(\d\d)\.html$', orig).groups(); month = '19%s-%s' % (yy, mm)
        cp = os.path.join(CACHE, os.path.basename(orig))
        if not os.path.exists(cp) or os.path.getsize(cp) == 0:
            raw = F.get('https://web.archive.org/web/%sid_/%s' % (ts, orig), gap=1.2); open(cp + '.tmp', 'wb').write(raw); os.replace(cp + '.tmp', cp)
        raw = open(cp, 'rb').read().decode('latin-1'); n = 0
        base = orig.replace(':80/', '/')
        for m in HREF.finditer(raw):
            h = (m.group(1) or m.group(2) or m.group(3) or '').strip()
            sch = (urllib.parse.urlsplit(re.sub(r'\s+', '', h)).scheme or 'relative').lower(); schemes[sch] += 1
            u = F.norm(urllib.parse.urljoin(base, re.sub(r'\s+', '', h)))
            if not u or u.startswith(NAV): continue
            n += 1
            if u not in units or month < units[u]['month']: units[u] = dict(month=month, page=orig, capture=ts)
        per_page[month] = n
    F.write_json(os.path.join(OUT, 'frame_ncsa.json'), dict(pages=[dict(page=o, capture=t) for o, t in pages], per_page=per_page, schemes=dict(schemes), units=units,
                 year_counts=dict(collections.Counter(v['month'][:4] for v in units.values()))))
    print('pages', len(pages), 'units', len(units), dict(collections.Counter(v['month'][:4] for v in units.values())), 'schemes', dict(schemes))

def draw():
    sd = F.seed(); fr = json.load(open(os.path.join(OUT, 'frame_ncsa.json')))
    cand = sorted((F.key(sd, 'ncsa', u), u) for u in fr['units'])[:N]
    units = [dict(id='ncsa|' + u, url=u, era='1993-1996', month=fr['units'][u]['month'], key=k) for k, u in cand]
    F.write_json(os.path.join(OUT, 'sample_ncsa.json'), dict(units=units, frame_count=len(fr['units'])))
    print('drawn', len(units))

if __name__ == '__main__':
    {'build': build, 'draw': draw}[sys.argv[1]]()
