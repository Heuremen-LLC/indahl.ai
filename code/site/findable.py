"""findable.py -- make indahl.ai easier to find, share and use (10 Nov 2026). Called by build_site.py; also a gate (python3 findable.py --gate).

  1 Dataset JSON-LD on every desk page and data-pack page (Google Dataset Search), dateModified from page_dates.json (the <main> change time).
  2 Share cards: one 1200x630 PNG per desk (question, headline number, outcome label, Heuremen LLC), cached by a hash of what it shows,
    written to the worker's public/og/<slug>.png and linked as /og/<slug>.png?v=<hash> (OpenGraph + Twitter tags on every page).
  3 Change feeds: /<desk>/changes.xml (Atom), built from the ledger's live_value rows (ledger/changes_feed.py), linked rel=alternate.
  4 A direct CSV link and an "Embed this number" snippet on each desk page (no script inside the snippet, no tracking).
The gate parses every served page's JSON-LD and refuses a Dataset without the fields Google requires (name, description of 50 to 5000
characters) or a page whose JSON-LD does not parse. Python 3.9+, Pillow for the cards."""
import os, re, json, html, hashlib, glob, time, datetime as D, urllib.request, concurrent.futures as CF, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public'); WORKER = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'worker.js')
SITE = 'https://indahl.ai'
sys.path.insert(0, os.path.join(B, 'ledger'))
ORG = {"@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/"}
CARD_V = 'c1'   # bump to redraw every card
DOIS = {}       # slot: '/water': '10.5281/zenodo.xxxxx' -> identifier on that page's Dataset once a DOI is minted
# spatialCoverage only where the page itself names the place
PLACE = {'/trials': 'United States', '/airq': 'United States', '/airline': 'United States', '/hpt': 'United States', '/revise': 'United States',
         '/fedsep': 'United States', '/forecast': 'United States', '/water': 'Lake Mead and Lake Powell, Colorado River, United States',
         '/atlas/electricity': 'United States', '/atlas/power-plants': 'United States', '/atlas/carbon': 'United States', '/atlas/planned-plants': 'United States'}
# temporalCoverage only where the page states the span of its data
TEMPORAL = {'/water': '2000/..', '/airq': '2025-06-01/2026-06-30', '/airline': '2019/2026'}
STATIC_FEED = {'/atlas/electricity': '/atlas/electricity.json', '/atlas/power-plants': '/atlas/plants.json', '/atlas/carbon': '/atlas/carbon.json',
               '/atlas/planned-plants': '/atlas/planned.json', '/yo': '/qia/yo.json'}
OUT_WORD = {'ABOVE': 'ABOVE', 'BELOW': 'BELOW', 'CONSISTENT': 'CONSISTENT', 'CANNOT_TELL': 'CANNOT TELL'}
EMB_A, EMB_B = '<!--emb-->', '<!--/emb-->'   # build_site's _page_dates strips this block, so a new read time alone never restamps a page


def _ledger():
    try: return [json.loads(l) for l in open(os.path.join(B, 'ledger', 'ledger.jsonl'))]
    except Exception: return []


def _headlines():
    try: return json.load(open(os.path.join(B, 'watch', 'headlines.json')))
    except Exception: return {'pages': {}}


def live_routes():
    """Every /<x>/live.json the worker serves."""
    try: w = open(WORKER).read()
    except Exception: return set()
    return set(re.findall(r"u\.pathname === '(/[a-z0-9/]+)/live\.json'", w))


def latest_values(rows):
    out = {}
    for r in rows:
        if r.get('kind') != 'live_value' or r.get('status') != 'live': continue
        s = r['live_of'].split('.')[1]
        if s not in out or r['history'][0]['at'] > out[s]['history'][0]['at']: out[s] = r
    return out


def _text(h): return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())


def _main(doc):
    a = doc.find('<main'); b = doc.rfind('</main>'); return doc[a:b] if a >= 0 and b > a else ''


def question(path, doc):
    try:
        from live_headlines import H2
        q = H2.get(path.strip('/'))
        if q: return q
    except Exception: pass
    m = re.search(r'<h2[^>]*>(.*?)</h2>', _main(doc).replace('<section id="hl-slot"', ''), re.S)
    return _text(m.group(1)) if m else ''


def technique(path, doc, what):
    t = _text(_main(doc)); iv = ''
    if 'Wilson' in t: iv = 'a 95 percent Wilson interval'
    elif re.search(r'(?i)bootstrap', t): iv = 'a 95 percent bootstrap interval'
    s = _text(what).rstrip('.')
    if iv and re.search(r'\bCANNOT[ _]TELL\b|cannot tell', t): return s + ', read with ' + iv + ' and an outcome of above, below, consistent or cannot tell.'
    if iv: return s + ', read with ' + iv + '.'
    return s + '.'


def _when(epoch): return time.strftime('%-d %b %Y, %H:%M UTC', time.gmtime(epoch))


def read_times(slugs):
    """The feed stamp behind each headline, read from the live feed with the ledger rule's own stamp path. Best effort, 8 s per feed."""
    try: import live_headlines as LH
    except Exception: return {}
    def one(s):
        spec = LH.DESKS.get(s)
        if not spec: return s, None
        try: d = LH.get(LH.feed_url(s)); return s, LH.stamp_epoch(LH.dig(d, spec['stamp']))
        except Exception: return s, None
    with CF.ThreadPoolExecutor(8) as ex: return dict(ex.map(one, slugs))


# ------------------------------------------------------------------------------------------------ share cards
_FONTS = os.path.join(PUB, 'fonts')
def _font(name, size):
    from PIL import ImageFont
    f = {'abril': 'abril-fatface-normal-804040b2.woff2', 'lora': 'lora-normal-6b102ab3.woff2', 'cinzel': 'cinzel-normal-ef95296c.woff2'}[name]
    return ImageFont.truetype(os.path.join(_FONTS, f), size)


def _wrap(draw, text, font, width, maxl):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines if len(lines) <= maxl else None


def _first_sentence(s):
    m = re.match(r'(.+?[.!?])(\s+[A-Z(]|$)', s); return m.group(1) if m else s


def draw_card(out, slug, label, q, big, line, outcome):
    from PIL import Image, ImageDraw
    INK, PAPER, MID, GOLD = (26, 18, 8), (247, 240, 224), (90, 72, 48), (200, 144, 42)
    im = Image.new('RGB', (1200, 630), INK); d = ImageDraw.Draw(im); d.rectangle([14, 14, 1185, 615], fill=PAPER)
    # the mark, small, top left, and the brand
    x0, y0, s = 64, 54, 46
    d.line([(x0 + s, y0), (x0 + 2 * s, y0 + 1.75 * s), (x0, y0 + 1.75 * s), (x0 + s, y0)], fill=INK, width=4, joint='curve')
    d.line([(x0 + s, y0 + 1.75 * s), (x0 + 1.5 * s, y0 + 0.68 * s), (x0 + 0.5 * s, y0 + 0.68 * s), (x0 + s, y0 + 1.75 * s)], fill=GOLD, width=4, joint='curve')
    d.ellipse([x0 + s - 4, y0 + 1.04 * s - 4, x0 + s + 4, y0 + 1.04 * s + 4], fill=GOLD)
    d.text((x0 + 2 * s + 24, y0 + 6), 'Heuremen LLC', font=_font('abril', 44), fill=INK)
    cf = _font('cinzel', 24); lw = d.textlength(label, font=cf); d.text((1136 - lw, y0 + 22), label, font=cf, fill=MID)
    d.rectangle([64, 158, 1136, 160], fill=GOLD)
    y = 186
    for size in (46, 40, 34):
        ql = _wrap(d, q, _font('lora', size), 1072, 2)
        if ql: break
    ql = ql or [q[:60]]
    for l in ql: d.text((64, y), l, font=_font('lora', size), fill=INK); y += int(size * 1.3)
    y += 14
    if big:
        for bs in (130, 110, 92, 76):
            bf = _font('abril', bs)
            if d.textlength(big, font=bf) <= (760 if outcome else 1072): break
        d.text((64, y), big, font=bf, fill=INK); bw = d.textlength(big, font=bf); bh = bf.getbbox(big)[3]
        if outcome:
            of = _font('cinzel', 30); ow = d.textlength(outcome, font=of); px = 64 + bw + 40; py = y + bh - 54
            if px + ow + 36 > 1136: px, py = 64, y + bh + 16
            d.rounded_rectangle([px, py, px + ow + 36, py + 50], radius=25, fill=INK); d.text((px + 18, py + 7), outcome, font=of, fill=PAPER)
        y += bh + 22
        if line:
            for ls in (28, 25, 22):
                ll = _wrap(d, line, _font('lora', ls), 1072, 3) or _wrap(d, _first_sentence(line), _font('lora', ls), 1072, 3)
                if ll and y + len(ll) * ls * 1.35 < 560: break
                ll = None
            for l in ll or []: d.text((64, y), l, font=_font('lora', ls), fill=MID); y += int(ls * 1.35)
    elif line:   # no headline number on this desk: the page's own description
        for ls in (32, 28, 25):
            ll = _wrap(d, line, _font('lora', ls), 1072, 5) or _wrap(d, _first_sentence(line), _font('lora', ls), 1072, 5)
            if ll and y + len(ll) * ls * 1.4 < 540: break
            ll = None
        for l in ll or []: d.text((64, y), l, font=_font('lora', ls), fill=MID); y += int(ls * 1.4)
    d.rectangle([64, 566, 284, 568], fill=GOLD)
    d.text((300, 550), 'indahl.ai/' + slug, font=_font('lora', 28), fill=MID)
    im.save(out, 'PNG', optimize=True)


def card(slug, label, q, big, line, outcome):
    """Draw /og/<slug>.png when what it shows changed. Returns the version hash for the ?v= stamp."""
    os.makedirs(os.path.join(PUB, 'og'), exist_ok=True)
    h = hashlib.sha256(json.dumps([CARD_V, label, q, big, line, outcome], ensure_ascii=False).encode()).hexdigest()[:10]
    idx_p = os.path.join(PUB, 'og', 'cards.json')
    try: idx = json.load(open(idx_p))
    except Exception: idx = {}
    out = os.path.join(PUB, 'og', slug.replace('/', '-') + '.png')
    if idx.get(slug) != h or not os.path.exists(out):
        draw_card(out, slug, label, q, big, line, outcome); idx[slug] = h
        json.dump(idx, open(idx_p, 'w'), indent=0, sort_keys=True)
    return h


# ------------------------------------------------------------------------------------------------ the pass
def _extract(zrel, member_suffix, out_name):
    """Copy one file out of a served zip next to it (same bytes as in the pack), so it has its own link. Returns its site path or None."""
    import zipfile
    z = os.path.join(PUB, zrel)
    if not os.path.isfile(z): return None
    try:
        with zipfile.ZipFile(z) as zf:
            m = next((n for n in zf.namelist() if n.endswith(member_suffix) and n.count('/') <= 2), None)
            if not m: return None
            data = zf.read(m)
    except Exception: return None
    out = os.path.join(os.path.dirname(z), out_name)
    if not os.path.exists(out) or open(out, 'rb').read() != data: open(out, 'wb').write(data)
    return '/' + os.path.relpath(out, PUB)


def _dois():
    try: d = json.load(open(os.path.join(B, 'ledger', 'zenodo_dois.json')))['packs']
    except Exception: return {}
    return {v['page'].replace(SITE, ''): v['concept_doi'] for v in d.values() if v.get('page') and v.get('concept_doi')}


def _desk_zip(p):
    """The pack a page's data sits in, as the Data pack button links it (build_site main(), _dpk_for)."""
    if p in ('/iris', '/yo') or p.startswith('/iris/'): return 'iris/iris-research-package.zip'
    if p == '/atlas' or p.startswith('/atlas/'): return 'atlas/atlas-data-pack.zip'
    if p == '/oy' or p.startswith('/oy/'): return 'oy/oy-data-pack.zip'
    if p == '/hermes/model' or p.startswith('/hermes/model/'): return 'hermes/model-data-pack.zip'
    s = p.strip('/')
    return '%s/%s-data-pack.zip' % (s, s) if s and '/' not in s else None


def packs(PAGES, DESKS=None):
    """{page: {zip, csv, license, desk}} for pack pages (their Download link) and for desk pages (their desk or division pack).
    The desk's outcomes CSV and each pack's LICENSE.txt are copied out of the zip so they have their own links."""
    out = {}; dois = _dois()
    if DESKS: _DESKSET.update(h for ds in DESKS.values() for h, n, w in ds)
    def lic(zrel):
        base = os.path.basename(zrel)[:-4]
        return _extract(zrel, '/LICENSE.txt', base + '-LICENSE.txt')
    for p, doc in PAGES.items():
        z = None
        if re.search(r'/(data-pack|package|kit)$', p):
            m = re.search(r'<a class="pkgbtn" href="/([^"?]+\.zip)[^"]*" download>', doc)
            z = m.group(1) if m else None
        elif p in _DESKSET:
            z = _desk_zip(p)
        elif p in ('/qia/list', '/iris/list'):
            z = '%s/%s-list-pack.zip' % (p.split('/')[1], p.split('/')[1])
        if not z or not os.path.isfile(os.path.join(PUB, z)): continue
        e = dict(zip='/' + z)
        l = lic(z)
        if l: e['license'] = SITE + l
        s = p.strip('/')
        if '/' not in s and z == '%s/%s-data-pack.zip' % (s, s):
            c = _extract(z, '/results/%s_outcomes.csv' % s, '%s_outcomes.csv' % s)
            if c: e['csv'] = c
        if dois.get(p): e['doi'] = dois[p]
        out[p] = e
    return out


_DESKSET = set()
def version_zips(PAGES):
    """Each link to a zip the site serves carries ?v=<first 12 of its sha256>, so the worker can cache it as immutable under that link."""
    shas = {}
    def v(m):
        p = m.group(2)
        if p not in shas:
            f = os.path.join(PUB, p.lstrip('/'))
            shas[p] = hashlib.sha256(open(f, 'rb').read()).hexdigest()[:12] if os.path.isfile(f) else None
        return m.group(1) + p + ('?v=' + shas[p] if shas[p] else '') + m.group(3)
    for k in PAGES: PAGES[k] = re.sub(r'(href=")(/[A-Za-z0-9_./-]+\.zip)(")', v, PAGES[k])
    return sum(1 for x in shas.values() if x)


def desk_paths(PAGES, DESKS):
    out = {}
    for dv, ds in DESKS.items():
        for h, n, w in ds:
            if h in PAGES and h not in out: out[h] = (dv, n, w)
    return out


def apply_main(PAGES, DESKS, packs=None):
    """Inside <main>: the CSV link, the change-feed link and the embed snippet on each desk page. Runs before page dates are taken."""
    packs = packs or {}; hl = _headlines(); P = hl.get('pages', {}); lv = latest_values(_ledger())
    desks = desk_paths(PAGES, DESKS)
    slugs = [p.strip('/') for p in desks if p.strip('/') in P]
    rt = read_times(slugs)
    import live_headlines as LH
    info = {}
    for path, (dv, name, what) in desks.items():
        doc = PAGES[path]; slug = path.strip('/'); h = P.get(slug) if '/' not in slug else None
        bits = []
        pk = packs.get(path) or {}
        if pk.get('csv'): bits.append('<a href="%s" download>Outcomes (CSV)</a>' % html.escape(pk['csv']))
        has_feed = slug in LH.DESKS and (LH.DESKS[slug].get('outcome') or LH.DESKS[slug]['kind'] != 'flip')
        if has_feed: bits.append('<a href="/%s/changes.xml">Changes to the headline (Atom)</a>' % slug)
        emb = ''
        if h and h.get('big'):
            t = rt.get(slug); when = ('Read ' + _when(t) + '.') if t else ('As of ' + _when(D.datetime.strptime(hl['updated'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=D.timezone.utc).timestamp()) + '.')
            oc = (lv.get(slug) or {}).get('reading', {}).get('outcome')
            snip = ('<p class="indahl-number"><a href="%s%s"><strong>%s</strong></a> %s %s%s Source: <a href="%s%s">%s, Heuremen LLC</a>.</p>'
                    % (SITE, path, html.escape(h['big']), html.escape(_first_sentence(h['line'])), html.escape(when),
                       (' Outcome: ' + OUT_WORD[oc].lower() + '.') if oc in OUT_WORD else '', SITE, path, html.escape(name)))
            emb = ('<h3>Embed this number</h3><p>Copy this into any page. It links back here and carries no script and no tracking.</p>'
                   '<textarea class="embedcode" readonly rows="4" aria-label="Embed code for the headline number">' + html.escape(snip) + '</textarea>')
        if not bits and not emb: continue
        blk = EMB_A + '<section class="share">' + (('<p class="meta">Data: ' + ' &middot; '.join(bits) + '</p>') if bits else '') + emb + '</section>' + EMB_B
        i = doc.rfind('</main>'); PAGES[path] = doc[:i] + blk + doc[i:]
        info[path] = dict(slug=slug, name=name, what=what, dv=dv, has_feed=has_feed, outcome=(lv.get(slug) or {}).get('reading', {}).get('outcome'), read=rt.get(slug))
    return info


def apply_head(PAGES, DESKS, LASTMOD, info, packs=None):
    """In <head>: share card tags, the change feed link, dateModified from the page's content change, and the Dataset on desk and pack pages."""
    packs = packs or {}; hl = _headlines().get('pages', {}); routes = live_routes()
    desks = desk_paths(PAGES, DESKS)
    for path in list(PAGES):
        doc = PAGES[path]; a = doc.find('</head>')
        if a < 0: continue
        head, rest = doc[:a], doc[a:]
        lm = (LASTMOD or {}).get(path)
        # dateModified on the page's own JSON-LD follows the time its main content last changed
        def fix(m):
            try: o = json.loads(m.group(1).replace('<\\/', '</'))
            except Exception: return m.group(0)
            if o.get('@type') == 'Dataset' and (path in desks or path in packs): return ''   # replaced below by the full Dataset
            if lm and 'dateModified' in o: o['dateModified'] = lm
            return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace('</', '<\\/') + '</script>'
        head = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix, head, flags=re.S)
        title = re.search(r'<meta property="og:title" content="([^"]*)"', head); title = html.unescape(title.group(1)) if title else 'Heuremen LLC'
        desc = re.search(r'<meta name="description" content="([^"]*)"', head); desc = html.unescape(desc.group(1)) if desc else ''
        add = []
        if path in desks:
            dv, name, what = desks[path]; slug = path.strip('/'); i = info.get(path, {})
            h = hl.get(slug) if '/' not in slug else None
            q = question(path, doc) or _text(what)
            label = (dv.strip('/').upper() + ' · ' + _text(name)) if dv != path else _text(name)
            oc = OUT_WORD.get(i.get('outcome') or '')
            sub = (h or {}).get('line', '') if h and h.get('big') else re.sub(r'^[A-Z][A-Za-z ]{1,24}: ', '', desc)
            sub = sub[:1].upper() + sub[1:]
            v = card(slug, label, q, (h or {}).get('big', ''), sub, oc)
            img = '%s/og/%s.png?v=%s' % (SITE, slug.replace('/', '-'), v)
            alt = q + ((': ' + h['big']) if h and h.get('big') else '') + ((' (' + oc.lower() + ')') if oc else '') + '. Heuremen LLC.'
            head = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="%s">' % html.escape(img), head)
            head = re.sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="%s">' % html.escape(img), head)
            add.append('<meta property="og:image:alt" content="%s">' % html.escape(alt)); add.append('<meta name="twitter:image:alt" content="%s">' % html.escape(alt))
            if i.get('has_feed'): add.append('<link rel="alternate" type="application/atom+xml" title="%s: changes to the headline" href="/%s/changes.xml">' % (html.escape(_text(name)), slug))
            feed = (path + '/live.json') if path in routes else STATIC_FEED.get(path)
            pk = packs.get(path) or {}
            dist = []
            if pk.get('zip'): dist.append({"@type": "DataDownload", "encodingFormat": "application/zip", "contentUrl": SITE + pk['zip']})
            if pk.get('csv'): dist.append({"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + pk['csv']})
            if feed: dist.append({"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + feed})
            if dist:
                ds = {"@context": "https://schema.org", "@type": "Dataset", "name": title.split(' | ')[0], "description": _ds_desc(q, desc), "url": SITE + path,
                      "creator": ORG, "publisher": ORG, "isAccessibleForFree": True, "license": pk.get('license') or (SITE + '/terms'),
                      "copyrightNotice": "Heuremen LLC. Free to download and cite with attribution. Not licensed for text and data mining or AI training.",
                      "measurementTechnique": technique(path, doc, what), "distribution": dist, "inLanguage": "en"}
                if lm: ds["dateModified"] = lm
                if DOIS.get(path) or pk.get('doi'): ds["identifier"] = 'https://doi.org/' + (DOIS.get(path) or pk['doi'])
                if TEMPORAL.get(path): ds["temporalCoverage"] = TEMPORAL[path]
                if PLACE.get(path): ds["spatialCoverage"] = {"@type": "Place", "name": PLACE[path]}
                vm = []
                if h and h.get('big'): vm.append({"@type": "PropertyValue", "name": "Headline", "description": _first_sentence(h['line']), "value": h['big']})
                if oc: vm.append({"@type": "PropertyValue", "name": "Outcome", "description": "Above, below, consistent with or cannot tell against the stated figure, under the rule in the desk plan.", "value": oc.lower()})
                if vm: ds["variableMeasured"] = vm
                add.append('<script type="application/ld+json">' + json.dumps(ds, ensure_ascii=False).replace('</', '<\\/') + '</script>')
        elif path in packs:
            pk = packs[path]; dist = [{"@type": "DataDownload", "encodingFormat": "application/zip", "contentUrl": SITE + pk['zip']}] if pk.get('zip') else []
            if pk.get('csv'): dist.append({"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + pk['csv']})
            if dist:
                ds = {"@context": "https://schema.org", "@type": "Dataset", "name": title.split(' | ')[0], "description": _ds_desc('', desc), "url": SITE + path,
                      "creator": ORG, "publisher": ORG, "isAccessibleForFree": True, "license": pk.get('license') or (SITE + '/terms'), "distribution": dist, "inLanguage": "en"}
                if lm: ds["dateModified"] = lm
                if pk.get('desk') and pk['desk'] in PAGES: ds["isBasedOn"] = SITE + pk['desk']
                if DOIS.get(path) or pk.get('doi'): ds["identifier"] = 'https://doi.org/' + (DOIS.get(path) or pk['doi'])
                add.append('<script type="application/ld+json">' + json.dumps(ds, ensure_ascii=False).replace('</', '<\\/') + '</script>')
        PAGES[path] = head + '\n'.join([''] + add + ['']) + rest


def _ds_desc(q, desc):
    d = desc.strip()
    if q and q.rstrip('?.').lower() not in d.lower(): d = (q.rstrip() + ('' if q.rstrip()[-1:] in '?.' else '.') + ' ' + d).strip()
    if len(d) < 50: d = (d + ' Heuremen LLC, live readings with a source for every row.').strip()
    return d[:5000]


# ------------------------------------------------------------------------------------------------ change feeds (static copy, the KV copy is pushed by live_headlines.py)
def write_changes():
    import changes_feed as CFD
    return len(CFD.write())


# ------------------------------------------------------------------------------------------------ gate
REQ = ('name', 'description')
def check_doc(doc):
    errs = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
        try: o = json.loads(m.group(1).replace('<\\/', '</'))
        except Exception as e: errs.append('JSON-LD does not parse: %s' % e); continue
        if o.get('@context') != 'https://schema.org' or not o.get('@type'): errs.append('JSON-LD without schema.org @context or @type')
        if o.get('@type') == 'Dataset':
            for k in REQ:
                if not o.get(k): errs.append('Dataset without %s' % k)
            if not (50 <= len(o.get('description', '')) <= 5000): errs.append('Dataset description is %d characters (Google needs 50 to 5000)' % len(o.get('description', '')))
            for dd in o.get('distribution', []):
                if dd.get('@type') != 'DataDownload' or not dd.get('contentUrl') or not dd.get('encodingFormat'): errs.append('Dataset distribution without DataDownload contentUrl and encodingFormat')
            for k in ('url', 'license', 'creator'):
                if not o.get(k): errs.append('Dataset without %s' % k)
            if 'identifier' in o and not o['identifier']: errs.append('Dataset with an empty identifier')
            if o.get('dateModified') and not re.match(r'\d{4}-\d\d-\d\d', o['dateModified']): errs.append('Dataset dateModified is not a date')
    return errs


def gate(paths=None):
    if paths is None:
        pj = open(os.path.join(HERE, 'pages.js')).read(); paths = [os.path.join(HERE, f) for f in re.findall(r"from '\./([^']+\.html)'", pj)]
    bad = 0; nds = 0
    for p in paths:
        s = open(p, encoding='utf-8').read(); nds += s.count('"@type": "Dataset"')
        for e in check_doc(s): print('  JSONLD %s: %s' % (os.path.relpath(p, HERE), e)); bad += 1
    print('jsonld gate: %d pages, %d datasets; breaches: %d' % (len(paths), nds, bad)); return bad


if __name__ == '__main__':
    if '--gate' in sys.argv: sys.exit(1 if gate() else 0)
    print(__doc__)
