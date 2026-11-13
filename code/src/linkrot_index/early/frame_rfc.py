#!/usr/bin/env python3
"""frame_rfc.py: addresses cited in RFCs (PLAN.md Addendum 3, sample E3). Builds the frame and, once the seed exists, the draw.
Frame: every RFC published 1993-01-01 to 2017-12-31 per the RFC Editor's rfc-index.xml, read as plain text (rsync module
rfcs-text-only). Only the reference sections count: from a heading at the left margin whose words are References (optionally numbered
and optionally Normative, Informative, Non-Normative or Informational) to the next heading at the left margin, with page headers,
page footers and form feeds removed first. Addresses: <http...> in angle brackets, joined across line breaks, and bare http(s)
addresses outside brackets, trailing punctuation removed; example and reserved hosts dropped. Unit: one distinct address. Era: year of
the earliest RFC citing it (1993-1996, 1997-2001, 2002-2008, 2009-2017). Draw: per era, the 150 units with the smallest key among
addresses on other hosts and the 50 with the smallest key among addresses on IETF and IANA hosts (rfc-editor.org, ietf.org, iana.org,
iab.org, irtf.org, iesg.org, isoc.org, internetsociety.org), reported apart. An era with fewer units gives all of them.
Usage: python3 -I frame_rfc.py build   |   python3 -I frame_rfc.py draw"""
import os, sys, re, json, subprocess, xml.etree.ElementTree as ET, urllib.parse
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import frames_common as F
OUT = os.path.join(F.DATA, 'rfc'); TXT = os.path.join(OUT, 'text')
ERAS = (('1993-1996', 1993, 1996), ('1997-2001', 1997, 2001), ('2002-2008', 2002, 2008), ('2009-2017', 2009, 2017))
PER_ERA = 150          # addresses on other hosts, per era
PER_ERA_IETF = 50      # addresses on IETF and IANA hosts, per era, reported apart
IETF = ('rfc-editor.org', 'ietf.org', 'iana.org', 'iab.org', 'irtf.org', 'iesg.org', 'isoc.org', 'internetsociety.org')
HEAD = re.compile(r'^(?:[A-Z0-9]+(?:\.[0-9]+)*\.?\s+)?(?:(?:normative|informative|non-normative|informational)\s+)?references?\s*$', re.I)
PAGE = re.compile(r'^(?:RFC \d+\s.*|.*\[Page \d+\]\s*)$')

def family(u):
    h = (urllib.parse.urlsplit(u).hostname or '').lower()
    return 'ietf' if any(h == d or h.endswith('.' + d) for d in IETF) else 'other'

def era_of(y):
    for n, a, b in ERAS:
        if a <= y <= b: return n

def index():
    p = os.path.join(OUT, 'rfc-index.xml')
    if not os.path.exists(p):
        os.makedirs(OUT, exist_ok=True); open(p, 'wb').write(F.get('https://www.rfc-editor.org/rfc-index.xml', timeout=120))
    ns = {'r': 'https://www.rfc-editor.org/rfc-index'}; out = {}
    for e in ET.parse(p).getroot().findall('r:rfc-entry', ns):
        did = e.findtext('r:doc-id', namespaces=ns); y = e.findtext('r:date/r:year', namespaces=ns); m = e.findtext('r:date/r:month', namespaces=ns)
        if did and y and 1993 <= int(y) <= 2017: out[int(did[3:])] = dict(year=int(y), month=m)
    return out

def ref_sections(text):
    lines = [l for l in text.replace('\r', '').split('\n') if '\f' not in l and not PAGE.match(l)]
    secs, cur = [], None
    for l in lines:
        if l and not l[0].isspace():
            if HEAD.match(l.strip()): cur = []; secs.append(cur); continue
            cur = None; continue
        if cur is not None: cur.append(l)
    return ['\n'.join(s) for s in secs]

BR = re.compile(r'<\s*(?:URL:)?\s*(https?://[^<>]+?)\s*>', re.I | re.S)
BARE = re.compile(r'https?://[^\s<>"\']+', re.I)
def addresses(text):
    out = set()
    for sec in ref_sections(text):
        for m in BR.finditer(sec): out.add(re.sub(r'\s+', '', m.group(1)))
        for m in BARE.finditer(BR.sub(' ', sec)): out.add(m.group(0).rstrip('.,;:)]\'"'))
    res = set()
    for u in out:
        n = F.norm(u)
        if n and not F.EXAMPLE_HOSTS.search(urllib.parse.urlsplit(n).hostname or ''): res.add(n)
    return sorted(res)

def build():
    idx = index(); os.makedirs(TXT, exist_ok=True)
    want = ['rfc%d.txt' % n for n in sorted(idx) if not os.path.exists(os.path.join(TXT, 'rfc%d.txt' % n))]
    if want:
        lst = os.path.join(OUT, 'want.txt'); open(lst, 'w').write('\n'.join(want) + '\n')
        r = subprocess.run(['rsync', '-a', '--timeout=120', '--files-from=' + lst, 'rsync.rfc-editor.org::rfcs-text-only/', TXT + '/'], capture_output=True, text=True)
        print('rsync', r.returncode, r.stderr[-300:])
    units, per_rfc, missing = {}, {}, []
    for n in sorted(idx):
        p = os.path.join(TXT, 'rfc%d.txt' % n)
        if not os.path.exists(p): missing.append(n); continue
        addrs = addresses(open(p, encoding='utf-8', errors='replace').read()); per_rfc[n] = len(addrs)
        for u in addrs:
            y = idx[n]['year']
            if u not in units or y < units[u]['year'] or (y == units[u]['year'] and n < units[u]['rfc']): units[u] = dict(year=y, rfc=n)
    for u in units: units[u]['era'] = era_of(units[u]['year'])
    F.write_json(os.path.join(OUT, 'frame_rfc.json'), dict(rfcs=len(idx), rfcs_read=len(per_rfc), rfcs_missing=missing, rfcs_with_address=sum(1 for v in per_rfc.values() if v), units=units,
                 era_counts={n: sum(1 for v in units.values() if v['era'] == n) for n, _, _ in ERAS}))
    print('RFCs', len(idx), 'read', len(per_rfc), 'missing', len(missing), 'units', len(units), {n: sum(1 for v in units.values() if v['era'] == n) for n, _, _ in ERAS})

def draw():
    sd = F.seed(); fr = json.load(open(os.path.join(OUT, 'frame_rfc.json'))); units = []
    counts = {}
    for n, _, _ in ERAS:
        for fam, cap in (('other', PER_ERA), ('ietf', PER_ERA_IETF)):
            pool = [u for u, v in fr['units'].items() if v['era'] == n and family(u) == fam]; counts['%s|%s' % (n, fam)] = len(pool)
            for k, u in sorted((F.key(sd, 'rfc', u), u) for u in pool)[:cap]:
                units.append(dict(id='rfc|' + u, url=u, era=n, family=fam, year=fr['units'][u]['year'], rfc=fr['units'][u]['rfc'], key=k))
    F.write_json(os.path.join(OUT, 'sample_rfc.json'), dict(units=units, frame_counts=counts))
    print('drawn', len(units))

if __name__ == '__main__':
    {'build': build, 'draw': draw}[sys.argv[1]]()
