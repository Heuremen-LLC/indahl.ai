"""entities.py -- follow any company or named thing on indahl.ai (10 Nov 2026, owner: "What if I'm only interested in what we're doing
with Falcon and not all of IRIS LAB?", "IBM should have the right to get updates on being calibrated by us", "any brand name, any company
should have an alert option anywhere on the site where it's mentioned").

One entity index, generated from the data at each build, shared by the pages, the worker and the sender:
  kinds   company, organisation, agency (each with a brand page, /brand/<slug>, from brands/entities.json), model (models and model families),
          backend (quantum processors and services), school, package (each with a light page, /e/<kind>/<slug>).
  rows    a row is about an entity when the entity is named in its subject: a brand-page row (brands.py, the desks' own feeds), or a table row on
          any served page whose first cell names it (exact case, whole word). A page that names it elsewhere in its text is listed as named on.
  files   entities_index.json (this folder: the whole index, read by alerts.py, alerts_send.py and the gate) and the worker's public
          /e/index.json (id, kind, name, a few other names and the page, for the search on /alerts; nothing else).
The match is exact case and whole word, on the entity's name and the other names it is shown under, minus a stoplist of names that are also
common words. Text inside links, headings, quotes, code, forms and scripts never counts.
  python3 entities.py --gate    the entity pages hold only rows traced to a served page or a brand-page row, every followable id has a page
Python 3.9+."""
import os, re, json, html, hashlib, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public')
ENT = os.path.join(B, 'brands', 'entities.json'); INDEX = os.path.join(HERE, 'entities_index.json'); PUBIDX = os.path.join(PUB, 'e', 'index.json')
SITE = 'https://indahl.ai'
E = html.escape
KIND_LABEL = {'company': 'Companies', 'organisation': 'Organisations', 'agency': 'Agencies and sources', 'model': 'Models', 'backend': 'Quantum backends',
              'school': 'Schools', 'package': 'Packages'}
KIND_WORD = {'company': 'company', 'organisation': 'organisation', 'agency': 'agency', 'model': 'model', 'backend': 'quantum backend', 'school': 'school', 'package': 'package'}
BRAND_KINDS = ('company', 'organisation', 'agency')
DIV_ORDER = ['/qia', '/iris', '/oy', '/atlas', '/hermes']
DIV_NAME = {'/qia': 'QIA', '/iris': 'IRIS', '/oy': 'OY', '/atlas': 'ATLAS', '/hermes': 'HERMES'}

# names that are also common words or other things: never matched in text (the entity keeps its other names)
STOP = {'Meta', 'Box', 'Square', 'Target', 'Apple', 'Energy', 'Labor', 'Signal', 'Oracle', 'Command', 'Time',
        'Change', 'Support', 'Model', 'Models', 'Open', 'Mistral AI', 'Discord', 'Slack', 'Notion', 'Zoom', 'Ring', 'Nest', 'Shell', 'Visa', 'Delta',
        'United', 'American', 'Frontier', 'Spirit', 'Alaska', 'Southwest', 'Allegiant', 'JetBlue', 'Hawaiian', 'Republic', 'Envoy', 'Endeavor',
        'Health', 'Labs', 'Cloud', 'Store', 'Search', 'Maps', 'Play', 'Shopping', 'News', 'Pool', 'Federal', 'National', 'Department', 'Office',
        'Institute', 'Center', 'University', 'College', 'School', 'Foundation', 'Project', 'Index', 'Desk', 'Quantum', 'Falcon training',
        'Bayer', 'Ford', 'Lilly', 'Allen', 'Wells', 'Graham', 'Morgan', 'Lincoln', 'Mayo', 'Baylor'}   # companies named like people: author lists carry the same words
# airlines are named in AIRLINE rows by their carrier names, which are ordinary words in other sentences; their rows still reach their pages
WORDS = None
def _words():
    global WORDS
    if WORDS is None:
        try: WORDS = {w.strip() for w in open('/usr/share/dict/words') if w.strip() and w.strip().islower()}
        except Exception: WORDS = set()
    return WORDS

# pages that never give rows, mentions or (in the bell pass) links: receipts, the brand and entity pages themselves, legal pages, the
# newsletter issues, the forms and answer shells, logs of our own corrections and releases
SKIP_EXACT = {'/alerts', '/privacy', '/terms', '/conflict-of-interest', '/agree', '/inquiry', '/inquire-ok', '/inquire-error', '/404', '/request',
              '/respond', '/correction', '/corrections', '/changelog', '/security/policy', '/security/thanks', '/mydata', '/week', '/newsletter',
              '/brand', '/follow', '/webhooks', '/verify', '/transparency', '/reproduce', '/security', '/security/self', '/contact', '/media', '/vault', '/tape'}
SKIP_PREFIX = ('/r/', '/brand/', '/e/', '/newsletter/', '/week/', '/receipts/')


def skipped(path):
    return path in SKIP_EXACT or path.startswith(SKIP_PREFIX)


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:80] or 'x'


# ------------------------------------------------------------------------------------------------ text of a page
VOL = [re.compile(r'\d{4}-\d\d-\d\d[T ]\d\d:\d\d(:\d\d(\.\d+)?)?(Z|[+-]\d\d:?\d\d)?( UTC)?'),
       re.compile(r'(?i)\b(updated|last read|read|checked|as of)\s+(\d{1,2} [A-Z][a-z]{2}\s+)?\d\d:\d\d( UTC)?')]


def txt(h):
    """visible text of an HTML fragment: bells, receipt links and entity links leave no trace, tags become spaces"""
    h = re.sub(r'<a class="(?:fb|rcpt)[^"]*"[^>]*>.*?</a>', '', h, flags=re.S)
    h = re.sub(r'<a class="ent"[^>]*>(.*?)</a>', r'\1', h, flags=re.S)
    h = re.sub(r'(?is)<(script|style|noscript|svg)\b.*?</\1>', ' ', h)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def sig_text(t):
    for r in VOL: t = r.sub(' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def main_of(doc):
    a = doc.find('<main'); b = doc.rfind('</main>')
    return doc[a:b] if a >= 0 and b > a else ''


def title_of(doc):
    m = re.search(r'<title>(.*?)</title>', doc, re.S)
    return html.unescape(m.group(1).split(' | ')[0]).strip() if m else ''


QUIET = re.compile(r'(?is)<(script|style|noscript|svg|a|h1|h2|h3|h4|h5|h6|blockquote|q|code|pre|kbd|samp|label|button|select|option|textarea|form|figcaption|summary)\b.*?</\1\s*>')


def tables(main):
    """[(heading, headers, [cells...] per row)] for every table in a page's <main>: cells as visible text, nearest heading before the table"""
    out = []
    for m in re.finditer(r'(?is)<table\b.*?</table>', main):
        t = m.group(0)
        hs = re.findall(r'(?is)<h[23][^>]*>(.*?)</h[23]>', main[:m.start()])
        head = txt(hs[-1]) if hs else ''
        ths = [txt(x) for x in re.findall(r'(?is)<thead\b.*?</thead>', t)[:1] for x in re.findall(r'(?is)<th[^>]*>(.*?)</th>', x)]
        rows = []
        for tr in re.findall(r'(?is)<tr\b[^>]*>(.*?)</tr>', t):
            if '<td' not in tr: continue
            cs = [txt(c) for c in re.findall(r'(?is)<t[dh]\b[^>]*>(.*?)</t[dh]>', tr)]
            if cs: rows.append(cs)
        out.append((head, ths, rows))
    return out


# ------------------------------------------------------------------------------------------------ the entities
def model_key(raw):
    """one key for the forms a model is shown under: tiiuae/Falcon3-7B, Falcon3 7B and falcon3:7b are one model. Families and sizes stay apart."""
    s = raw.split('/')[-1].lower()
    s = re.sub(r'[:_\-]+', ' ', s)
    s = re.sub(r'\s+(instruct|it|chat|hf)$', '', s.strip())
    s = re.sub(r'([a-z])\s+(\d)', r'\1\2', s)
    return re.sub(r'\s+', ' ', s).strip()


def family_of(key):
    """the family word of a model key when a version or size follows it (falcon3 3b, granite 4.1 3b, mistral 7b), else none"""
    m = re.match(r'([a-z]+)(?:\d|\s\d)', key)
    return m.group(1) if m else ''


MAKER_PREFIX = re.compile(r'^(IBM|NVIDIA|Google|Meta|Microsoft|Mistral|Alibaba|Amazon|OpenAI|Anthropic|DeepSeek|Cohere|xAI|AI2|Ai2)\s+')
OLLAMA = re.compile(r'(?<![\w/.:-])([a-z][a-z0-9.]*(?:-[a-z0-9.]+)?:\d+(?:\.\d+)?[bm])(?![\w.:-])')
HFNAME = re.compile(r'(?<![\w/.-])([A-Z][A-Za-z]+\d(?:\.\d)?[ -]\d+(?:\.\d+)?B(?: Instruct)?)(?![\w.-])')
BACKEND = re.compile(r'(?<![\w/.-])(ibm_[a-z]+)(?![\w])')
BRAKET_DEVICES = [('Cepheus-1-108Q', 'Rigetti Cepheus-1-108Q', 'rigetti'), ('Ankaa-3', 'Rigetti Ankaa-3', 'rigetti'), ('H1-1', 'Quantinuum H1-1', 'quantinuum'),
                  ('Aria1', 'IonQ Aria1', 'ionq'), ('Aria-1', 'IonQ Aria-1', 'ionq'), ('Forte-1', 'IonQ Forte-1', 'ionq')]


def _good_name(n, kind):
    """a name that may be matched in text: not a stopword, not a lone common word (an all-caps acronym of three or more letters passes)"""
    n = n.strip()
    if len(n) < 3 or n in STOP or '|' in n: return False
    if re.fullmatch(r'[A-Za-z]+', n) and n.lower() in _words() and not (n.isupper() and len(n) >= 3): return False
    if n.islower() and kind not in ('model', 'backend', 'package') and '.' not in n: return False   # a bare lowercase word (a product slug) is not a name in prose
    if re.fullmatch(r'\d+', n): return False
    return True


def load_brands():
    ent = json.load(open(ENT))
    out = {}
    for e in ent['entities']:
        k = {'nonprofit': 'organisation', 'university': 'organisation'}.get(e['kind'], e['kind'])
        if k not in BRAND_KINDS: k = 'organisation'
        names = [e['name']] + [a['raw'] for a in e['aliases']] + list(e.get('names') or [])
        out[e['slug']] = dict(id=e['slug'], kind=k, name=e['name'], slug=e['slug'], url='/brand/' + e['slug'],
                              names=list(dict.fromkeys(n for n in names if n)), match=list(dict.fromkeys(n for n in names if _good_name(n, k))))
    return out


def build_entities(PAGES, brand_rows):
    """every entity: the brand entities, then models, model families, backends, schools and packages found in the data"""
    ents = load_brands()
    # models: brand-page rows that name a model (AILUMINATE systems, MODEL card rounds, HFSIZE and HFLICENSE repositories), and the model
    # names in the tables and text of the IRIS and HERMES pages (Ollama names such as falcon3:3b, and Falcon3 3B Instruct)
    raws = {}
    for r in brand_rows:
        if r['key'] in ('ailuminate', 'model_live', 'hfsize', 'hflicense'):
            for raw in r.get('raws') or []:
                if r['key'] == 'ailuminate' and raw == 'MLCommons': continue
                raws.setdefault(raw, set()).add(r['key'])
    for p, d in PAGES.items():
        if skipped(p) or not (p.startswith('/iris') or p in ('/hosts', '/weights', '/hfsize', '/hflicense', '/hermes/model', '/ailuminate')): continue
        t = txt(main_of(d))
        for m in OLLAMA.finditer(t): raws.setdefault(m.group(1), set()).add('page')
        for m in HFNAME.finditer(t): raws.setdefault(m.group(1), set()).add('page')
    models = {}
    for raw in raws:
        nm = MAKER_PREFIX.sub('', raw) if not raw.startswith('IBM Granite') else raw[4:]
        k = model_key(nm)
        if not re.search(r'\d', k) or len(k) < 3: continue
        models.setdefault(k, []).append(raw)
    fams = {}
    for k, rs in models.items():
        disp = sorted(rs, key=lambda x: ('/' in x, x.islower(), len(x)))[0]
        disp = disp.split('/')[-1]
        s = slugify(k)
        names = list(dict.fromkeys(rs + [x.split('/')[-1] for x in rs]))
        ents['model/' + s] = dict(id='model/' + s, kind='model', name=disp, slug=s, url='/e/model/' + s, names=names, match=[n for n in names if _good_name(n, 'model')], key=k)
        f = family_of(k)
        if f and len(f) >= 3: fams.setdefault(f, []).append('model/' + s)
    for f, ms in fams.items():
        # the family name as the rows write it (Falcon, Granite, Qwen), matched in text only when it is capitalised there
        forms = [re.match(r'[A-Za-z]+', ents[m]['name']).group(0) for m in ms if re.match(r'[A-Za-z]+', ents[m]['name'])]
        cap = [x for x in forms if x[:1].isupper() and x.lower() == f]
        disp = (max(set(cap), key=cap.count) if cap else f.capitalize())
        if disp in STOP or len(disp) < 3: continue
        s = slugify(f) + '-family'
        ents['model/' + s] = dict(id='model/' + s, kind='model', kword='model family', name=disp, slug=s, url='/e/model/' + s, names=[disp, 'model family'], match=[disp], family=sorted(ms))
    # quantum backends: IBM processors (QIA calibration, audit and mirror rows) and the devices on Amazon Braket, and Amazon Braket itself
    bk = set()
    for p, d in PAGES.items():
        if not p.startswith('/qia') and p not in ('/yo', '/darkwave'): continue
        bk |= set(BACKEND.findall(txt(main_of(d))))
    for r in brand_rows:
        if r['key'] == 'qia':
            m = BACKEND.search(r['item'])
            if m: bk.add(m.group(1))
    for b in sorted(bk):
        if b in ('ibm_sim',): continue
        nice = 'IBM ' + b[4:].capitalize()
        s = slugify(b)
        ents['backend/' + s] = dict(id='backend/' + s, kind='backend', name=b, slug=s, url='/e/backend/' + s, names=[b, nice], match=[b, nice], maker='ibm')
    alltext = {p: txt(main_of(d)) for p, d in PAGES.items() if p.startswith('/qia')}
    for dev, full, maker in BRAKET_DEVICES:
        if any(dev in t for t in alltext.values()):
            s = slugify(full)
            ents['backend/' + s] = dict(id='backend/' + s, kind='backend', name=full, slug=s, url='/e/backend/' + s, names=[full, dev], match=[full, dev], maker=maker)
    if any('Amazon Braket' in t for t in alltext.values()):
        ents['backend/amazon-braket'] = dict(id='backend/amazon-braket', kind='backend', name='Amazon Braket', slug='amazon-braket', url='/e/backend/amazon-braket',
                                             names=['Amazon Braket'], match=['Amazon Braket'], maker='aws')
    # schools: each OY school page, by the name on it. The OY page is the school's page (no second page); a school that is also an
    # organisation with a brand page (a trial sponsor) stays one entity, the brand, with a link to its OY page
    bnames = {n: i for i, e in ents.items() if e['kind'] in BRAND_KINDS for n in (e['name'],)}
    for p, d in PAGES.items():
        if p.startswith('/oy/school/'):
            n = title_of(d)
            if not n or len(n) < 4: continue
            if n in bnames: ents[bnames[n]]['home'] = p; continue
            s = slugify(n)
            if 'school/' + s in ents: s = s + '-' + p.rsplit('/', 1)[1]
            ents['school/' + s] = dict(id='school/' + s, kind='school', name=n, slug=s, url=p, own_page=False, names=[n], match=[n] if _good_name(n, 'school') and ' ' in n else [], home=p)
    # packages: the projects the package desks list (their rows are the desk's rows that name the project first)
    for r in brand_rows:
        if r['key'] not in ('pkglicense', 'pkginstall'): continue
        n = r['item'].split(' (')[0].strip()
        if not n or len(n) > 60 or ' ' in n: continue
        s = slugify(n)
        ents.setdefault('package/' + s, dict(id='package/' + s, kind='package', name=n, slug=s, url='/e/package/' + s, names=[n], match=[], item_prefix=n + ' ('))
    return ents


# ------------------------------------------------------------------------------------------------ the matcher
class Matcher:
    """one pass over a text finds every entity name in it: exact case, whole word, longest name first"""
    def __init__(self, ents, kinds=None):
        self.by = {}
        for i, e in ents.items():
            if kinds and e['kind'] not in kinds: continue
            for n in e['match']:
                self.by.setdefault(n, set()).add(i)
        # a name two entities share (a brand and a model) goes to neither in text
        self.by = {n: next(iter(v)) for n, v in self.by.items() if len(v) == 1}
        names = sorted(self.by, key=len, reverse=True)
        self.rx = re.compile(r'(?<![\w@/.\-])(' + '|'.join(re.escape(n) for n in names) + r')(?![\w@/\-]|\.\w)') if names else None

    def find(self, t, bells=False):
        """matches, minus a name that is the tail of a longer proper name (Virginia Wesleyan University is not Wesleyan University). With bells,
        also minus a one-word name that starts a longer proper name (Amazon Madison Mega Site), where the longer name is the subject."""
        if not self.rx or not t: return []
        out = []
        for m in self.rx.finditer(t):
            pre = re.search(r'([A-Z][\w.&\'-]*)\s+$', t[max(0, m.start(1) - 40):m.start(1)])
            if pre and pre.group(1) not in LEAD_OK: continue
            if bells and ' ' not in m.group(1) and re.match(r'\s+[A-Z][a-z]', t[m.end(1):m.end(1) + 3]): continue
            out.append((m.start(1), m.end(1), self.by[m.group(1)]))
        return out


LEAD_OK = {'The', 'A', 'An', 'In', 'On', 'At', 'By', 'For', 'From', 'With', 'And', 'Of', 'To', 'As', 'Its', 'Their', 'Our', 'Both', 'Each', 'Every', 'When',
           'Where', 'How', 'What', 'Why', 'If', 'Not', 'No', 'All', 'But', 'Or', 'Than', 'Then', 'This', 'That', 'These', 'Those', 'Under', 'Over', 'Against',
           'Before', 'After', 'Since', 'Until', 'While', 'Via', 'Per', 'Like', 'Unlike', 'Only', 'Also', 'Source', 'Sources', 'Data', 'Read', 'See'}


def desk_of(path, desks, home):
    """(desk path, desk label, division) for a served page"""
    p = path.split('#')[0]
    lab = {}
    for dv, lst in desks.items():
        for h, n, _w in lst: lab[h.split('#')[0]] = (html.unescape(n), dv)
    if p == '/': return '/', 'Home', '/hermes'
    for q in (p, '/' + p.strip('/').split('/')[0] + ('/' + p.strip('/').split('/')[1] if p.count('/') >= 2 else '')):
        if q in lab: return q, lab[q][0], lab[q][1]
    for dv in DIV_ORDER:
        if p == dv: return p, DIV_NAME[dv], dv
        if p.startswith(dv + '/'):
            seg = dv + '/' + p[len(dv) + 1:].split('/')[0]
            if seg in lab: return seg, lab[seg][0], lab[seg][1]
            return dv, DIV_NAME[dv], dv
    seg = '/' + p.strip('/').split('/')[0]
    if seg in lab: return seg, lab[seg][0], lab[seg][1]
    dv = home.get(p) or home.get(seg) or '/hermes'
    return seg, seg.strip('/').upper(), dv if dv in DIV_NAME else '/hermes'


SUBJECT = re.compile(r'(?i)^(processor|backend|device|model|models|system|vendor|company|organi[sz]ation|sponsor|school|institution|platform|server|provider|host|repo|repository|project|package|brand|agency|source|maker|publisher)\b')


def scan(PAGES, ents, desks, home, covered=None):
    """{entity id: {'rows': [page rows], 'named': [pages]}}. A page row: {page, title, desk, dlabel, div, head, headers, cells}.
    covered: {entity id: set of desk pages} already given by brand-page rows, so the same desk is not copied twice."""
    M = Matcher(ents)
    out = {}
    for p in sorted(PAGES):
        if skipped(p): continue
        doc = PAGES[p]; main = main_of(doc)
        if not main: continue
        dk, dl, dv = desk_of(p, desks, home); ti = title_of(doc)
        seen_rows = set()
        for head, ths, rows in tables(main):
            subj = [0] + [j for j, h in enumerate(ths) if j and SUBJECT.match(h or '')]
            for cs in rows:
                hit = [x for j in subj if j < len(cs) for x in M.find(cs[j])]
                if not hit: continue
                ids = list(dict.fromkeys(i for _, _, i in hit))
                for i in ids:
                    if covered and dk in covered.get(i, ()): continue
                    k = (i, tuple(cs))
                    if k in seen_rows: continue
                    seen_rows.add(k)
                    out.setdefault(i, {'rows': [], 'named': []})['rows'].append(dict(page=p, title=ti, desk=dk, dlabel=dl, div=dv, head=head, headers=ths[:len(cs)], cells=cs))
        quiet = txt(QUIET.sub(' ', main))
        for _, _, i in M.find(quiet):
            d = out.setdefault(i, {'rows': [], 'named': []})
            if p not in d['named']: d['named'].append(p)
        # a section whose heading names it (the Falcon training section on IRIS LAB): followed as one block of text
        for sec in re.split(r'(?=<h[23][\s>])', main):
            hm = re.match(r'(?is)<h([23])([^>]*)>(.*?)</h\1>', sec)
            if not hm: continue
            ht = txt(hm.group(3)); anc = re.search(r'\bid="([^"]+)"', hm.group(2))
            for i in dict.fromkeys(x for _, _, x in M.find(ht)):
                out.setdefault(i, {'rows': [], 'named': []}).setdefault('sections', []).append(
                    dict(page=p, title=ti, desk=dk, dlabel=dl, div=dv, head=ht, anchor=anc.group(1) if anc else '', sig=sig_text(txt(sec))))
    # rows-only kinds (packages) match on the first cell of their own desk tables
    return out


# ------------------------------------------------------------------------------------------------ build hook
def build(PAGES, brand_rows, desks, home):
    """the index: every entity with the rows and pages it appears on, written for the worker, the sender and the pages. Returns it."""
    ents = build_entities(PAGES, brand_rows)
    covered, feed = {}, {}
    rawmap = {}
    for e in ents.values():
        if e['kind'] == 'model' and 'key' in e:
            for n in e['names']: rawmap[n] = e['id']
    pref = [(e['item_prefix'], e['id']) for e in ents.values() if e.get('item_prefix')]
    for n, r in enumerate(brand_rows):
        ids = [s for s, _ in r['on']] + [rawmap[x] for x in (r.get('raws') or []) if x in rawmap] + [i for pf, i in pref if r['item'].startswith(pf)]
        for i in dict.fromkeys(ids):
            feed.setdefault(i, []).append(n); covered.setdefault(i, set()).add(r['link'].split('#')[0])
    found = scan(PAGES, ents, desks, home, covered)
    for e in ents.values():   # a family holds its models' rows and pages
        if e.get('family'):
            f = found.setdefault(e['id'], {'rows': [], 'named': []})
            for m in e['family']:
                g = found.get(m) or {'rows': [], 'named': []}
                f['rows'] += [r for r in g['rows'] if r not in f['rows']]
                f['named'] += [p for p in g['named'] if p not in f['named']]
                f.setdefault('sections', []).extend(x for x in g.get('sections', []) if x not in f.get('sections', []))
            feed[e['id']] = sorted({n for m in e['family'] for n in feed.get(m, [])})
    idx = {}
    for i, e in ents.items():
        fr = feed.get(i, []); f = found.get(i, {'rows': [], 'named': []})
        if not fr and not f['rows'] and not f['named'] and not f.get('sections'): continue
        desks_on = {}
        for n in fr:
            r = brand_rows[n]; dk, dl, dv = desk_of(r['link'], desks, home); desks_on.setdefault(dk, (dl, dv))
        for r in f['rows']: desks_on.setdefault(r['desk'], (r['dlabel'], r['div']))
        for p in f['named']:
            dk, dl, dv = desk_of(p, desks, home); desks_on.setdefault(dk, (dl, dv))
        idx[i] = dict(e, feed=fr, covered=sorted(covered.get(i, ())), page_rows=f['rows'], sections=[{k: v for k, v in x.items() if k != 'sig'} for x in f.get('sections', [])], named=[p for p in f['named'] if p not in {r['page'] for r in f['rows']}],
                      desks=[[k, v[0], v[1]] for k, v in sorted(desks_on.items(), key=lambda x: (DIV_ORDER.index(x[1][1]) if x[1][1] in DIV_ORDER else 9, x[1][0]))])
    return idx


def write(idx, desks=None, home=None):
    json.dump({'entities': idx, 'desks': desks or {}, 'home': home or {}}, open(INDEX, 'w'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    os.makedirs(os.path.dirname(PUBIDX), exist_ok=True)
    short = [[i, e['kind'], e['name'], [n for n in e['names'] if n != e['name']][:3], e['url']] for i, e in sorted(idx.items(), key=lambda x: (x[1]['kind'], x[1]['name'].lower()))]
    body = json.dumps({'kinds': KIND_LABEL, 'e': short}, ensure_ascii=False, separators=(',', ':'))
    if not os.path.exists(PUBIDX) or open(PUBIDX, encoding='utf-8').read() != body: open(PUBIDX, 'w', encoding='utf-8').write(body)
    js = os.path.join(PUB, 'e', 'search.js')
    if not os.path.exists(js) or open(js).read() != SEARCH_JS: open(js, 'w').write(SEARCH_JS)


def load():
    return json.load(open(INDEX))['entities']


# ------------------------------------------------------------------------------------------------ pages
def page_rows_html(rows, h=2):
    """page rows grouped by division, then page and table, each cell as the page shows it, with a link to the page"""
    o = []; by = {}
    for r in rows: by.setdefault(r['div'], {}).setdefault((r['page'], r['title'], r['head'], tuple(r['headers'])), []).append(r)
    for dv in sorted(by, key=lambda d: DIV_ORDER.index(d) if d in DIV_ORDER else 9):
        o.append('<h%d>%s</h%d>' % (h, E(DIV_NAME.get(dv, dv.strip('/').upper())), h))
        for (p, ti, hd, ths), rs in by[dv].items():
            o.append('<h%d><a href="%s">%s</a>%s</h%d>' % (h + 1, E(p), E(ti or p), (' &middot; ' + E(hd)) if hd else '', h + 1))
            n = max(len(r['cells']) for r in rs)
            o.append('<div class="scroll"><table class="mtx"><thead><tr>' + ''.join('<th>%s</th>' % E(ths[j] if j < len(ths) else '') for j in range(n)) + '</tr></thead><tbody>')
            for r in rs: o.append('<tr>' + ''.join('<td class="pr">%s</td>' % E(c) for c in r['cells']) + ''.join('<td class="pr"></td>' for _ in range(n - len(r['cells']))) + '</tr>')
            o.append('</tbody></table></div>')
    return ''.join(o)


def sections_html(secs, h=2):
    if not secs: return ''
    li = ''.join('<li><a href="%s">%s</a> <span class="meta">on %s, %s</span></li>' % (E(x['page'] + ('#' + x['anchor'] if x['anchor'] else '')), E(x['head']), E(x['title'] or x['page']), E(DIV_NAME.get(x['div'], '')))
                 for x in secs)
    return '<h%d>Sections about it</h%d><ul>%s</ul>' % (h, h, li)


def named_html(paths, PAGES, desks, home):
    if not paths: return ''
    li = []
    for p in sorted(paths, key=lambda p: (DIV_ORDER.index(desk_of(p, desks, home)[2]) if desk_of(p, desks, home)[2] in DIV_ORDER else 9, p)):
        dk, dl, dv = desk_of(p, desks, home)
        li.append('<li><a href="%s">%s</a> <span class="meta">%s</span></li>' % (E(p), E(title_of(PAGES[p]) or p), E(DIV_NAME.get(dv, ''))))
    return '<h2>Named on these pages</h2><ul>' + ''.join(li) + '</ul>'


def brand_extra(slug, idx, PAGES, desks, home):
    """for a brand page: the page rows (rows about it on pages beyond its desks' feeds) and the pages that name it"""
    e = idx.get(slug)
    if not e: return ''
    o = ('<p><a href="%s">The OY page for %s</a></p>' % (E(e['home']), E(e['name']))) if e.get('home') and e['home'] in PAGES else ''
    if e['page_rows']: o += '<h2 id="on-other-pages">Rows about %s on other pages</h2><p class="meta">Each row as the page shows it. The page holds the current reading.</p>' % E(e['name']) + page_rows_html(e['page_rows'], 3)
    o += sections_html(e.get('sections')) + named_html(e['named'], PAGES, desks, home)
    return o


def add_pages(PAGES, page, hero_slim, HOME, idx, brand_rows, desks, home, render_rows):
    """/e/<kind>/<slug> for every entity that is not a brand. render_rows(numbers) renders brand-page rows (the traced cells) as a table."""
    n = 0
    for i, e in sorted(idx.items()):
        if e['kind'] in BRAND_KINDS or e.get('own_page') is False: continue
        kw = e.get('kword') or KIND_WORD[e['kind']]; nm = E(e['name'])
        o = ['<section class="legal"><p class="meta">%s &middot; <a href="/alerts">Follow any named thing</a></p>' % E(KIND_LABEL[e['kind']])]
        if e.get('family'):
            o.append('<p>Every row the desks of Heuremen LLC publish about a model in the %s family, and every page that names the family or one of its models. Models in the family: %s.</p>'
                     % (E(e['name']), ', '.join('<a href="%s">%s</a>' % (E(idx[m]['url']), E(idx[m]['name'])) for m in e['family'] if m in idx) or 'none with rows yet'))
        else:
            o.append('<p>Every row the desks of Heuremen LLC publish about %s, and every page that names it. Each row links to the page that holds the current reading.</p>' % nm)
        if e.get('home') and e['home'] in PAGES: o.append('<p><a href="%s">The OY page for %s</a></p>' % (E(e['home']), nm))
        if e.get('maker') and e['maker'] in idx: o.append('<p>Made or run by <a href="%s">%s</a>.</p>' % (E(idx[e['maker']]['url']), E(idx[e['maker']]['name'])))
        other = [x for x in e['names'] if x != e['name']] if not e.get('family') else []
        if other: o.append('<p class="meta">Also shown as %s.</p>' % ', '.join('<strong>%s</strong>' % E(x) for x in other[:12]))
        if e['feed']: o.append(render_rows(e['feed']))
        if e['page_rows']: o.append(page_rows_html(e['page_rows']))
        o.append(sections_html(e.get('sections')))
        o.append(named_html(e['named'], PAGES, desks, home))
        o.append('<p class="meta">Rows are as each page showed them when this page was built. No row here is a new reading. The outcome is the desk&rsquo;s own word. '
                 'To correct or remove a row, use the <a href="/correction">correction or removal form</a>.</p></section>')
        path = e['url']
        PAGES[path] = page(path, '%s | %s | Heuremen LLC' % (e['name'], KIND_LABEL[e['kind']]),
                           'Every row the Heuremen LLC desks publish about the %s %s, grouped by division, with a link to each page.' % (kw, e['name']), ''.join(o), hero_slim(nm))
        if HOME is not None: HOME[path] = desk_of(e['page_rows'][0]['page'], desks, home)[2] if e['page_rows'] else '/hermes'
        n += 1
    print('entities: %d entities indexed (%s), %d light pages' % (len(idx), ', '.join('%d %s' % (sum(1 for e in idx.values() if e['kind'] == k), k) for k in KIND_LABEL), n))
    return n


SEARCH_JS = """// Follow any named thing: search over /e/index.json, grouped by kind. Ticks a box in the form on this page. No tracking, nothing sent.
(function () {
  var q = document.getElementById('ent-q'), out = document.getElementById('ent-res'), picked = document.getElementById('ent-picked'); if (!q || !out || !picked) return;
  var data = null, K = {};
  function load(cb) { if (data) return cb(); fetch('/e/index.json').then(function (r) { return r.json(); }).then(function (d) { data = d.e; K = d.kinds; cb(); }).catch(function () { out.textContent = 'The list could not be loaded.'; }); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function add(id, name, kind) {
    if (picked.querySelector('input[value="' + id.replace(/"/g, '') + '"]')) { picked.querySelector('input[value="' + id.replace(/"/g, '') + '"]').checked = true; return; }
    var l = document.createElement('label'); l.innerHTML = '<input type="checkbox" name="en" checked> Rows about ' + esc(name) + ' <span class="meta">' + esc(kind) + '</span>';
    l.firstChild.value = id; picked.appendChild(l); picked.hidden = false;
  }
  window.hlcFollow = function (id) { load(function () { for (var i = 0; i < data.length; i++) if (data[i][0] === id) { add(id, data[i][2], (K[data[i][1]] || '').replace(/s$/, '')); return; } }); };
  q.addEventListener('input', function () {
    var t = q.value.trim().toLowerCase(); if (t.length < 2) { out.innerHTML = ''; return; }
    load(function () {
      var g = {}, n = 0;
      for (var i = 0; i < data.length && n < 60; i++) { var e = data[i], hay = (e[2] + ' ' + e[3].join(' ')).toLowerCase(); if (hay.indexOf(t) >= 0) { (g[e[1]] = g[e[1]] || []).push(e); n++; } }
      var h = '';
      Object.keys(K).forEach(function (k) { if (!g[k]) return; h += '<p class="su-dh">' + esc(K[k]) + '</p><ul class="su-list">' + g[k].map(function (e) { return '<li><button type="button" class="linkbtn" data-id="' + esc(e[0]) + '" data-n="' + esc(e[2]) + '" data-k="' + esc(K[k]) + '">Follow</button> <a href="' + esc(e[4]) + '">' + esc(e[2]) + '</a>' + (e[3].length ? ' <span class="meta">' + esc(e[3].join(', ')) + '</span>' : '') + '</li>'; }).join('') + '</ul>'; });
      out.innerHTML = h || '<p class="meta">Nothing by that name is on a desk yet.</p>';
    });
  });
  out.addEventListener('click', function (ev) { var b = ev.target.closest ? ev.target.closest('button[data-id]') : null; if (!b) return; add(b.getAttribute('data-id'), b.getAttribute('data-n'), b.getAttribute('data-k').replace(/s$/, '')); b.textContent = 'Ticked'; });
  var m = /[?&]e=([^&]+)/.exec(location.search); if (m) window.hlcFollow(decodeURIComponent(m[1]));
})();
"""


# ------------------------------------------------------------------------------------------------ Follow beside names (the bell pass)
# 10 Nov 2026 evening (owner: "any brand name, any company should have an alert option anywhere on the site where it's mentioned"). After every
# page is final, a known name in a page's body text gets a link to its page and a small Follow link (to /alerts?e=<id>, which ticks it; with
# script it ticks the box in the form at the foot of the page). Once per page per entity in the text, and in table rows where it is the subject.
# Never: outside <main>, inside a link, heading, quote, code, form, label, button or script, in a block that names the issued bill, on the
# pages skipped() names (receipts, legal pages, newsletter issues, brand and entity pages). The visible text never changes but for the added
# Follow labels, which carry class nosig so the update emails never count them. BELLS records each page's hash without them, for the gate.
BELLS = os.path.join(HERE, 'entity_bells.json')
MASK = re.compile(r'(?is)<(a|h[1-6]|blockquote|q|code|pre|kbd|samp|script|style|noscript|svg|label|button|select|textarea|form|summary|figcaption|cite|title)\b.*?</\1\s*>'
                  r'|<(span|p|small|em|strong|b|i|div|li)\b[^>]*class="[^"]*\b(?:nosig|rcpt|su|quote)\b[^"]*"[^>]*>.*?</\2\s*>'
                  r'|<(p|li|tr|dd|dt|caption)\b[^>]*>(?:(?!</\3>).)*?QIA-2026-001.*?</\3\s*>|<!--.*?-->')
PAIR = re.compile(r'<a class="ent" href="[^"]*">([^<]*)</a><a class="fb nosig" href="/alerts\?e=[^"]*" data-e="[^"]*" data-n="[^"]*" rel="nofollow">Follow</a>')
ROW_CAP = 20
BELL_SKIP = {'/forecasters'}   # its gate reads the chart's own markup cell for cell (forecasters.py), so its names stay plain


NEST = re.compile(r'(?is)<(span|p|small|em|strong|b|i|div|li)\b[^>]*class="[^"]*\b(?:nosig|rcpt|su|quote)\b[^"]*"[^>]*>(.*?)</\1\s*>')


def nested_masks(h):
    """masked class blocks (nosig, rcpt, su, quote) that hold a tag of their own name: MASK's short match would end early there, so refuse"""
    return [m.group(1) for m in NEST.finditer(h) if re.search(r'(?i)<%s\b' % m.group(1), m.group(2))]


def unbell(doc):
    return PAIR.sub(r'\1', doc)


def _masked(h):
    """the fragment with every region a bell may not enter swapped for a placeholder, and the list to put them back"""
    keep = []
    def sub(m): keep.append(m.group(0)); return '\ue000%d\ue001' % (len(keep) - 1)
    return MASK.sub(sub, h), keep


def _unmask(h, keep):
    return re.sub('\ue000(\\d+)\ue001', lambda m: keep[int(m.group(1))], h)


def _in_quote(t, i):
    pre = t[:i]
    return (pre.count('\u201c') + pre.count('&ldquo;')) > (pre.count('\u201d') + pre.count('&rdquo;')) or (pre.count('"') + pre.count('&quot;')) % 2 == 1


def _bell(i, e, name):
    return ('<a class="ent" href="%s">%s</a><a class="fb nosig" href="/alerts?e=%s" data-e="%s" data-n="%s" rel="nofollow">Follow</a>'
            % (E(e['url']), name, E(i.replace('/', '%2F')), E(i), E(e['name'])))


def _wrap(h, M, idx, page, done, limit_one=False):
    """put bells on the text nodes of h: each entity not in done, at its first eligible place. Returns (new html, ids belled)"""
    mh, keep = _masked(h)
    parts = re.split(r'(<[^>]+>)', mh); got = []
    for k in range(0, len(parts), 2):
        t = parts[k]
        if not t.strip() or '\ue000' in t and not re.sub('\ue000\\d+\ue001', '', t).strip(): continue
        out = []; pos = 0
        for a, b, i in M.find(t, bells=True):
            if i in done or i in got or idx[i]['url'] == page: continue
            nxt = t[b:b + 1]; prv = t[a - 1:a] if a else ''
            if nxt in ("'", '\u2019', '&') or prv in ('&', '#') or _in_quote(t, a): continue
            out.append(t[pos:a]); out.append(_bell(i, idx[i], t[a:b])); pos = b; got.append(i)
            if limit_one: break
        if out: out.append(t[pos:]); parts[k] = ''.join(out)
        if limit_one and got: break
    return _unmask(''.join(parts), keep), got


def bell_pass(PAGES, idx=None):
    """the Follow links beside names on every served page; records each page's hash without them (entity_bells.json) for the gate"""
    idx = idx if idx is not None else load()
    M = Matcher({i: e for i, e in idx.items() if e['kind'] != 'package'})
    rec = {}; nb = nr = np_ = 0
    for p in sorted(PAGES):
        doc = PAGES[p]
        if skipped(p) or p in BELL_SKIP or '<main' not in doc: continue
        a = doc.find('<main'); a = doc.find('>', a) + 1; b = doc.rfind('</main>')
        main = doc[a:b]; done = set(); rows = 0
        if nested_masks(main): raise SystemExit('BUILD REFUSED: %s has a nested nosig, rcpt, su or quote block the bell pass cannot mask safely' % p)
        # table rows: the subject cells (the first cell, or a column headed Processor, Model, Vendor and the like)
        def table(m):
            nonlocal rows
            t = m.group(0)
            ths = [txt(x) for x in re.findall(r'(?is)<thead\b.*?</thead>', t)[:1] for x in re.findall(r'(?is)<th[^>]*>(.*?)</th>', x)]
            subj = {0} | {j for j, hd in enumerate(ths) if j and SUBJECT.match(hd or '')}
            def tr(mr):
                nonlocal rows
                if rows >= ROW_CAP or '<td' not in mr.group(0): return mr.group(0)
                cells = list(re.finditer(r'(?is)(<t[dh]\b[^>]*>)(.*?)(</t[dh]>)', mr.group(0)))
                out = mr.group(0); shift = 0; seen = set()
                for j, c in enumerate(cells):
                    if j not in subj: continue
                    new, got = _wrap(c.group(2), M, idx, p, seen, limit_one=True)
                    if got:
                        seen |= set(got); rows += 1
                        s0, e0 = c.start(2) + shift, c.end(2) + shift
                        out = out[:s0] + new + out[e0:]; shift += len(new) - (e0 - s0)
                return out
            return re.sub(r'(?is)<tr\b[^>]*>.*?</tr>', tr, t)
        tabs = []
        def stash(m): tabs.append(table(m)); return '\ue002%d\ue003' % (len(tabs) - 1)
        body = re.sub(r'(?is)<table\b.*?</table>', stash, main)
        body, got = _wrap(body, M, idx, p, done)
        body = re.sub('\ue002(\\d+)\ue003', lambda m: tabs[int(m.group(1))], body)
        new = doc[:a] + body + doc[b:]
        if new != doc:
            if unbell(new) != doc: raise SystemExit('BUILD REFUSED: the bell pass changed more than its links on %s' % p)
            PAGES[p] = new; np_ += 1; nb += len(got); nr += rows
        rec[p] = hashlib.sha256(doc.encode('utf-8')).hexdigest()[:20]
    json.dump(rec, open(BELLS, 'w'), sort_keys=True, separators=(',', ':'))
    print('entities: Follow beside names on %d pages (%d in text, %d in table rows)' % (np_, nb, nr))
    return np_


def bell_gate():
    """every served page: without its Follow links it is byte for byte the page as built before the pass, no Follow link sits outside <main>
    or in a region it may not enter, every link names a known entity and its page, and skipped pages carry none"""
    errs = []
    try: idx = load(); rec = json.load(open(BELLS))
    except Exception as ex: print('BELL GATE: no index or entity_bells.json (%s)' % ex); return 1
    served = re.findall(r"from '\./([^']+\.html)'", open(os.path.join(HERE, 'pages.js')).read())
    n = nb = 0
    for f in served:
        p = '/' + f[:-5]; p = '/' if p == '/index' else p
        doc = open(os.path.join(HERE, f), encoding='utf-8').read(); n += 1
        pairs = list(PAIR.finditer(doc)); nb += len(pairs)
        loose = len(re.findall(r'<a class="fb nosig"', doc)) - len(pairs) + len(re.findall(r'<a class="ent"', doc)) - len(pairs)
        if loose: errs.append('%s: a Follow link or name link outside a pair' % p)
        if not pairs: continue
        if nested_masks(doc[doc.find('<main'):doc.rfind('</main>')]): errs.append('%s: a nested nosig, rcpt, su or quote block' % p)
        if skipped(p) or p in BELL_SKIP: errs.append('%s: a skipped page carries Follow links' % p); continue
        if p not in rec: errs.append('%s: no record of the page before the pass' % p); continue
        if hashlib.sha256(unbell(doc).encode('utf-8')).hexdigest()[:20] != rec[p]: errs.append('%s: without its Follow links the page is not the page as built' % p)
        a = doc.find('<main'); b = doc.rfind('</main>')
        for m in pairs:
            if not (a < m.start() < b): errs.append('%s: a Follow link outside <main>' % p)
            ent = re.match(r'<a class="ent" href="([^"]*)">', m.group(0)).group(1); eid = re.search(r'data-e="([^"]*)"', m.group(0)).group(1)
            if html.unescape(eid) not in idx: errs.append('%s: Follow link for unknown %s' % (p, eid))
            elif html.unescape(ent) != idx[html.unescape(eid)]['url']: errs.append('%s: name link %s is not the page of %s' % (p, ent, eid))
        # mark each pair, then mask the regions a bell may not enter: a mark inside a masked region is a breach
        marked = PAIR.sub(lambda m: '\ue010' + m.group(1) + '\ue011', doc[a:b])
        mh, keep = _masked(marked)
        if any('\ue010' in k for k in keep): errs.append('%s: a Follow link inside a link, heading, quote, code, form or bill block' % p)
        if '\ue010' in doc[:a] or '\ue010' in doc[b:]: errs.append('%s: mark outside main' % p)
    for x in errs[:30]: print('  BELLS', x)
    print(('BELL GATE: REFUSED, %d problems' % len(errs)) if errs else 'BELL GATE: %d served pages read, %d Follow links, each page unchanged without them and none in a forbidden region' % (n, nb))
    return 1 if errs else 0


# ------------------------------------------------------------------------------------------------ gate
def gate():
    """every entity page holds only rows traced to its source page (each cell text in a table row of the built source page) or a traced brand-page
    row, and every followable entity id in the worker's list has a built page"""
    errs = []
    try: idx = load()
    except Exception as ex: print('ENTITIES GATE: no entities_index.json (%s)' % ex); return 1
    built = {}
    try: brows = json.load(open(os.path.join(B, 'brands', 'rows.json')))['rows']
    except Exception: brows = []
    import brands as BR
    def brows_cells(n):
        r = brows[n] if n < len(brows) else {}
        return [r.get(c, '') for c in BR.CELLS] + [BR.ROLE['named'], r.get('desk', '')]
    def page_file(p): return os.path.join(HERE, (p.strip('/') or 'index') + '.html')
    def rowset(p):
        if p not in built:
            f = page_file(p)
            built[p] = {tuple(cs) for _, _, rows in tables(main_of(open(f, encoding='utf-8').read())) for cs in rows} if os.path.exists(f) else None
        return built[p]
    for i, e in idx.items():
        f = page_file(e['url'])
        if not os.path.exists(f): errs.append('%s: no page %s' % (i, e['url'])); continue
        if e.get('own_page') is False: continue   # a school: its OY page is its page, and rows about it are followed, not copied
        doc = open(f, encoding='utf-8').read(); main = main_of(doc)
        prc = re.findall(r'<td class="pr">(.*?)</td>', main, re.S)
        frc = [html.unescape(x) for x in re.findall(r'<td class="fr">(.*?)</td>', main, re.S)]
        if frc:
            fr_ok = {c for n in e['feed'] for c in brows_cells(n)}
            for c in frc:
                if c not in fr_ok: errs.append('%s: brand-page row cell %r on %s is not a traced cell of its rows' % (i, c[:60], e['url']))
        want = []
        for r in e['page_rows']:
            src = rowset(r['page'])
            if src is None: errs.append('%s: source page %s not built' % (i, r['page'])); continue
            if tuple(r['cells']) not in src: errs.append('%s: row %r is not on %s as built' % (i, ' | '.join(r['cells'])[:80], r['page']))
            want += r['cells']
        got = [html.unescape(x) for x in prc if x != '']
        if sorted(got) != sorted(c for c in want if c != ''): errs.append('%s: page-row cells on %s differ from the index (%d against %d)' % (i, e['url'], len(got), len([c for c in want if c])))
        for c in got:
            if c and not any(c in r['cells'] for r in e['page_rows']): errs.append('%s: untraced page-row cell %r' % (i, c[:60]))
    pidx = json.load(open(PUBIDX))['e']
    if sorted(x[0] for x in pidx) != sorted(idx): errs.append('public /e/index.json lists other ids than the index')
    lj = os.path.join(HERE, 'alerts_list.js')
    if os.path.exists(lj):
        m = re.search(r'export const ALERT_ENTS = (\{.*?\});\n', open(lj, encoding='utf-8').read(), re.S)
        if not m: errs.append('alerts_list.js has no ALERT_ENTS')
        elif sorted(json.loads(m.group(1))) != sorted(idx): errs.append('ALERT_ENTS lists other ids than the index')
    for x in errs[:30]: print('  ENTITIES', x)
    print(('ENTITIES GATE: REFUSED, %d problems' % len(errs)) if errs else 'ENTITIES GATE: every entity page traces its rows to a served page or a brand-page row (%d entities)' % len(idx))
    return 1 if errs else 0


if __name__ == '__main__':
    if '--gate' in sys.argv: sys.exit(gate() | (bell_gate() if os.path.exists(BELLS) else 0))
    if '--bell-gate' in sys.argv: sys.exit(bell_gate())
    print(__doc__)
