#!/usr/bin/env python3
"""frame_landmarks.py: landmarks of the early web (PLAN.md Addendum 4, sample L1). Builds the frame from three public source families,
then the draw (every unit, in key order). No listed site is requested here.

A site counts when a source lists an address that points at the front page of a domain of its own: the host is the registered domain
(ICANN section of the Public Suffix List) or www. plus it, and the path is empty, "/", or an index file (index or default, .html, .htm,
.shtml, .php, .asp). Deep links and sites on someone else's domain (a page on a hosting service, a video on a video site) do not count.
Unit: one registered domain, whatever its sources. The address read is the front-page address as first listed. Era: the year it was
first listed by any source (1994-1996, 1997-2001, 2002-2008, 2009 and later).
Sources:
  wikipedia  "List of Internet phenomena" on English Wikipedia, read through the MediaWiki API: the last revision before the first day of
             each month from May 2004 to January 2010, and the current revision. Links inside <ref> tags, citation templates and
             comments are removed first. A domain from the monthly revisions counts if it appears in at least two of them. A domain in the
             current revision counts on that one revision. Year: the year of the first revision listing it (the current revision is 2026).
  webby      Webby Award winners 1997-2008, as built by scout_webby.py (data/landmarks/frame_webby.json). Year: the ceremony year.
  picks      Yahoo! Picks and Cool Site of the Day, as built by scout_picks.py (data/landmarks/frame_picks.json). Year: the pick date.
Readers' suggestions that the rule does not produce are kept in a separate sample, labelled suggested by readers, read by the same rules
and never mixed into the rates.
Usage: python3 -I frame_landmarks.py wiki | build | draw"""
import os, sys, re, json, time, html, urllib.parse, urllib.request, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H); sys.path.insert(0, os.path.join(ROOT, 'early'))
import frames_common as F, linkstate as L
OUT = os.path.join(ROOT, 'data', 'landmarks'); WIKI = os.path.join(OUT, 'wiki'); API = 'https://en.wikipedia.org/w/api.php?'
PAGE = 'List of Internet phenomena'
SUGGESTED = ['boredatwork.com', 'yourethemannowdog.com', 'badgerbadgerbadger.com']   # Wayfinder's examples, 9 Nov 2026
FRONT = re.compile(r'^/?((index|default|home)\.(html?|shtml|php|asp))?$', re.I)

def front_domain(u):
    """The registered domain if the address points at the front page of a domain of its own, else None."""
    n = F.norm(u)
    if not n: return None
    p = urllib.parse.urlsplit(n); h = (p.hostname or '').lower()
    if not h or L.is_ip(h) or p.query: return None
    rd = L.regdom(h)
    if not rd or '.' not in rd or h not in (rd, 'www.' + rd): return None
    if not FRONT.match(p.path or '/'): return None
    return rd, n

def _api(params):
    return json.loads(F.get(API + urllib.parse.urlencode(dict(params, format='json', formatversion='2')), gap=1.0))

def wiki_links(text):
    t = re.sub(r'<!--.*?-->', ' ', text, flags=re.S)
    t = re.sub(r'<ref[^>/]*/>', ' ', t, flags=re.I)
    t = re.sub(r'<ref\b[^>]*>.*?</ref\s*>', ' ', t, flags=re.I | re.S)
    for _ in range(4):   # citation templates, innermost first
        t = re.sub(r'\{\{\s*(cite|citation|webarchive|wayback|dead link)[^{}]*\}\}', ' ', t, flags=re.I)
    urls = re.findall(r'\[(https?://[^\s\]]+)', t) + re.findall(r'(?<![\[=/])(https?://[^\s\]|<>{}"]+)', t)
    return [u.rstrip('.,;:)\'"') for u in urls]

def wiki():
    os.makedirs(WIKI, exist_ok=True); revs = []
    y, m = 2004, 5
    while (y, m) <= (2010, 1):
        d = _api(dict(action='query', prop='revisions', titles=PAGE, rvlimit='1', rvprop='ids|timestamp', rvdir='older', rvstart='%04d-%02d-01T00:00:00Z' % (y, m)))
        pg = d['query']['pages'][0]
        if pg.get('revisions'): revs.append(dict(snapshot='%04d-%02d' % (y, m), revid=pg['revisions'][0]['revid'], ts=pg['revisions'][0]['timestamp']))
        m += 1
        if m == 13: y, m = y + 1, 1
    cur = _api(dict(action='query', prop='revisions', titles=PAGE, rvlimit='1', rvprop='ids|timestamp'))['query']['pages'][0]['revisions'][0]
    revs.append(dict(snapshot='current', revid=cur['revid'], ts=cur['timestamp']))
    seen = {}
    for r in revs:
        p = os.path.join(WIKI, 'rev_%d.wikitext' % r['revid'])
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            raw = F.get('https://en.wikipedia.org/w/index.php?' + urllib.parse.urlencode({'oldid': r['revid'], 'action': 'raw'}), gap=1.0)
            open(p + '.tmp', 'wb').write(raw); os.replace(p + '.tmp', p)
        doms = {}
        for u in wiki_links(open(p, encoding='utf-8', errors='replace').read()):
            fd = front_domain(u)
            if fd and not fd[0].endswith(('wikipedia.org', 'wikimedia.org', 'wikiquote.org', 'wiktionary.org')): doms.setdefault(fd[0], fd[1])
        r['domains'] = sorted(doms); r['addresses'] = doms
    F.write_json(os.path.join(OUT, 'frame_wiki_revisions.json'), revs)
    monthly = collections.Counter(d for r in revs if r['snapshot'] != 'current' for d in r['domains'])
    rows = []
    for r in revs:
        for d, addr in r['addresses'].items():
            if r['snapshot'] == 'current' or monthly[d] >= 2:
                rows.append(dict(source='wikipedia', year=int(r['ts'][:4]) if r['snapshot'] != 'current' else 2026, domain=d, url=addr, snapshot=r['snapshot'], revid=r['revid']))
    F.write_json(os.path.join(OUT, 'frame_wiki.json'), rows)
    print('revisions', len(revs), 'rows', len(rows), 'domains', len({x['domain'] for x in rows}))

def picks_year(d):
    m = re.match(r'(\d{4})', d or ''); return int(m.group(1)) if m else None

def build():
    rows = []
    wp = os.path.join(OUT, 'frame_wiki.json')
    if os.path.exists(wp): rows += json.load(open(wp))
    for fname, src in (('frame_webby.json', 'webby'), ('frame_picks.json', 'picks')):
        p = os.path.join(OUT, fname)
        if not os.path.exists(p): print('missing', fname); continue
        for r in json.load(open(p)):
            fd = front_domain(r.get('url') or '')
            yr = r.get('year') if src == 'webby' else picks_year(r.get('date'))
            if fd and yr: rows.append(dict(source=src, year=int(yr), domain=fd[0], url=fd[1], detail=(r.get('column') or r.get('award') or ''), listed_as=r.get('url')))
    units = {}
    for r in sorted(rows, key=lambda x: (x['year'], x['source'], x['url'])):
        u = units.setdefault(r['domain'], dict(domain=r['domain'], url=r['url'], first_listed=r['year'], sources=set()))
        u['sources'].add(r['source'])
    for u in units.values():
        y = u['first_listed']; u['era'] = '1994-1996' if y <= 1996 else ('1997-2001' if y <= 2001 else ('2002-2008' if y <= 2008 else '2009 and later'))
        u['sources'] = sorted(u['sources'])
    F.write_json(os.path.join(OUT, 'frame_landmarks.json'), dict(units=units, rows=len(rows), by_source=dict(collections.Counter(s for u in units.values() for s in u['sources'])),
                 by_era=dict(collections.Counter(u['era'] for u in units.values()))))
    print('rows', len(rows), 'units', len(units), dict(collections.Counter(u['era'] for u in units.values())))

def draw():
    sd = F.seed(); fr = json.load(open(os.path.join(OUT, 'frame_landmarks.json')))['units']
    units = [dict(id='landmarks|' + d, url=u['url'], era=u['era'], first_listed=u['first_listed'], sources=u['sources'], name=d, key=F.key(sd, 'landmarks', d)) for d, u in fr.items()]
    units.sort(key=lambda x: x['key'])
    F.write_json(os.path.join(OUT, 'sample_landmarks.json'), dict(units=units, frame_count=len(units)))
    miss = [d for d in SUGGESTED if d not in fr]
    sug = [dict(id='suggested|' + d, url='http://%s/' % d, era='suggested by readers', name=d, sources=['suggested by readers'], key=F.key(sd, 'suggested', d)) for d in miss]
    F.write_json(os.path.join(OUT, 'sample_suggested.json'), dict(units=sug, in_rule=[d for d in SUGGESTED if d in fr], not_in_rule=miss))
    print('landmarks', len(units), '| suggested examples produced by the rule:', [d for d in SUGGESTED if d in fr], '| not produced, read apart:', miss)

if __name__ == '__main__':
    {'wiki': wiki, 'build': build, 'draw': draw}[sys.argv[1]]()
