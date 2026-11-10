#!/usr/bin/env python3
"""wiki_tick.py: WIKI desk of the HERMES division (Heuremen LLC), per PLAN.md and its addenda (committed before any comparison was read).

Section 1, cited figures against their source: Wikidata statements whose reference cites the World Bank (population, GDP, Gini,
unemployment) or the UNESCO Institute for Statistics (life expectancy, fertility), read against that source's current release and
every archived release it keeps.
Section 2, the Foundation's numbers against its own data: the Wikimedia Foundation's stated figures (homepage, projects page,
annual report 2024-2025, DSA filings) against the Wikimedia Analytics API, site statistics and the DSA tables themselves.

Read-only. Keyless. One request at a time, paced. No timers or cron: run it from a shell, or let the tick bus call it.
Run:  venv/bin/python wiki_tick.py                    (every step)
      venv/bin/python wiki_tick.py --steps s1_wb      (one or more steps, comma separated)
      venv/bin/python wiki_tick.py --offline          (score from the cached raw files only)
      venv/bin/python wiki_tick.py --publish          (every step, then put data/wiki_live.json in the site KV as wiki_live)
      venv/bin/python -I wiki_tick.py --publish --due-days 7   (what the tick bus runs every 36 ticks: a new reading once the last is 7 days old)
Writes data/raw/*, data/wiki.json (full), data/wiki_live.json (public slim feed), summary_wiki.json. Publishes only with --publish.
"""
import os, sys, re, json, time, gzip, math, hashlib, random, argparse, calendar, datetime as D, collections as C, html as HTML
import urllib.request, urllib.parse, urllib.error
from decimal import Decimal, InvalidOperation

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); os.chdir(H)
import heuremen_kit as K

UA = 'HeuremenLLC-research/1.0 (https://indahl.ai)'
RAW = os.path.join(H, 'data', 'raw'); os.makedirs(RAW, exist_ok=True)
LOG = os.path.join(RAW, 'http.log')
OFFLINE = False
NOW = time.time()
MATCH, OLDER, NOREL, UNREAD = 'MATCHES_CURRENT', 'MATCHES_AN_OLDER_RELEASE', 'MATCHES_NO_RELEASE_READ', 'SOURCE_UNREADABLE'
BINS = (MATCH, OLDER, NOREL, UNREAD)
OUTS = (K.ABOVE, K.BELOW, K.CONSISTENT, K.CANNOT_TELL)
SIZE = 0.01            # PLAN: size that matters, 1 percent of the source's current figure
F32 = 2.0 ** -24       # PLAN: single-precision storage at the source


# ----------------------------------------------------------------------------------------------------------- network and cache
def log(msg):
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ ', time.gmtime()) + msg + '\n')

_last = {}
WM_HOSTS = ('wikipedia.org', 'wikimedia.org', 'wikidata.org', 'mediawiki.org', 'wiktionary.org', 'wikibooks.org', 'wikinews.org', 'wikiquote.org',
            'wikisource.org', 'wikiversity.org', 'wikivoyage.org', 'wikimediafoundation.org')
def http(url, data=None, headers=None, pace=0.35, tries=5, timeout=90, host_key=None):
    """One request at a time with a minimum gap per host. Every Wikimedia host shares one gap of at least 0.31 s (under 200 a minute;
    note 2.11). The query service keeps its own gap. Honours Retry-After on 429 and 5xx. Returns (status, bytes)."""
    host = urllib.parse.urlparse(url).netloc
    hk = host_key or ('wikimedia' if host.endswith(WM_HOSTS) and host != 'query.wikidata.org' else host)
    if hk == 'wikimedia': pace = max(pace, 0.31)
    for i in range(tries):
        gap = pace - (time.time() - _last.get(hk, 0))
        if gap > 0: time.sleep(gap)
        _last[hk] = time.time()
        h = {'User-Agent': UA, 'Accept-Encoding': 'gzip'}; h.update(headers or {})
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                if r.headers.get('Content-Encoding') == 'gzip': b = gzip.decompress(b)
                log(f'200 {len(b)} {url[:300]}'); return 200, b
        except urllib.error.HTTPError as e:
            log(f'{e.code} {url[:300]}')
            if e.code in (429, 500, 502, 503, 504):
                w = e.headers.get('Retry-After'); w = int(w) if (w and w.isdigit()) else 10 * (i + 1)
                time.sleep(min(max(w, 5), 120)); continue
            return e.code, b''
        except Exception as e:
            log(f'ERR {type(e).__name__} {e} {url[:300]}'); time.sleep(5 * (i + 1))
    return -1, b''

def cpath(*parts): p = os.path.join(RAW, *parts); os.makedirs(os.path.dirname(p), exist_ok=True); return p

def get_json(url, cache, permanent=False, **kw):
    """Fetch JSON, keep a gzipped copy at cache (relative to data/raw). permanent: never re-fetch once cached (archived releases)."""
    p = cpath(cache)
    if (permanent or OFFLINE) and os.path.exists(p):
        with gzip.open(p, 'rt') as f: return json.load(f)
    if OFFLINE: return None
    st, b = http(url, **kw)
    if st != 200: return {'_status': st}
    try: d = json.loads(b)
    except Exception: return {'_status': 'not json'}
    with gzip.open(p, 'wt') as f: json.dump(d, f)
    return d

def get_text(url, cache, permanent=False, **kw):
    p = cpath(cache)
    if (permanent or OFFLINE) and os.path.exists(p):
        with gzip.open(p, 'rt') as f: return f.read()
    if OFFLINE: return None
    st, b = http(url, **kw)
    if st != 200: return None
    t = b.decode('utf8', 'replace')
    with gzip.open(p, 'wt') as f: f.write(t)
    return t

def wdqs(query, cache):
    p = cpath(cache)
    if OFFLINE and os.path.exists(p):
        with gzip.open(p, 'rt') as f: return json.load(f)['results']['bindings']
    st, b = http('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query': query, 'format': 'json'}).encode(),
                 headers={'Accept': 'application/sparql-results+json', 'Content-Type': 'application/x-www-form-urlencoded'}, pace=3.0)
    if st != 200: raise RuntimeError(f'WDQS {st}')
    d = json.loads(b)
    with gzip.open(p, 'wt') as f: json.dump(d, f)
    return d['results']['bindings']

def sha256(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf8')).hexdigest()
def iso_utc(t=None): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t or time.time()))


# ----------------------------------------------------------------------------------------------------------- section 1: frame
WB_SRC, UIS_SRC = 'Q21540096', 'Q3152127'
GROUPS = [
    dict(id='WB-POP', prop='P1082', src='WB', series='SP.POP.TOTL', label='Population', units={'1', 'Q199'}),
    dict(id='WB-GDP', prop='P2131', src='WB', series='NY.GDP.MKTP.CD', label='GDP, current US$', units={'1', 'Q199', 'Q4917'}),
    dict(id='WB-GINI', prop='P1125', src='WB', series='SI.POV.GINI', label='Gini coefficient', units={'1', 'Q199'}),
    dict(id='WB-UNEMP', prop='P1198', src='WB', series='SL.UEM.TOTL.ZS', label='Unemployment rate', units={'1', 'Q199', 'Q11229'}),
    dict(id='UIS-LE', prop='P2250', src='UIS', series='SP.DYN.LE00.IN', label='Life expectancy at birth', units={'Q577', 'Q1092296'}),
    dict(id='UIS-TFR', prop='P4841', src='UIS', series='SP.DYN.TFRT.IN', label='Total fertility rate', units={'1', 'Q199'}),
]
SECONDARY_WB = ['SP.DYN.LE00.IN', 'SP.DYN.TFRT.IN']     # PLAN sub-reading 3 (descriptive)
CHANGE_QUALS = {'P21', 'P518', 'P642', 'P1013', 'P1001'}
LEGACY = {'ROM': 'ROU', 'ZAR': 'COD', 'TMP': 'TLS', 'ADO': 'AND', 'IMY': 'IMN', 'KSV': 'XKX', 'WBG': 'PSE'}
REF_FILTER = {
    'WB': '{ ?ref pr:P248 wd:Q21540096 } UNION { ?ref pr:P854 ?u . FILTER(CONTAINS(LCASE(STR(?u)), "worldbank.org") || CONTAINS(LCASE(STR(?u)), "banquemondiale.org")) }',
    'UIS': '{ ?ref pr:P248 wd:Q3152127 } UNION { ?ref pr:P854 ?u . FILTER(CONTAINS(LCASE(STR(?u)), "uis.unesco.org")) }'}

def step_s1_frame():
    """List the items in each group's frame (query service), then read every statement of that property from the live API."""
    meta = {}
    for g in GROUPS:
        q = f"SELECT DISTINCT ?item ?iso WHERE {{ ?item wdt:P298 ?iso . ?item p:{g['prop']} ?st . ?st prov:wasDerivedFrom ?ref . {REF_FILTER[g['src']]} }}"
        b = wdqs(q, f"s1/wdqs_items_{g['id']}.json.gz")
        items = C.defaultdict(set)
        for x in b: items[x['item']['value'].rsplit('/', 1)[1]].add(x['iso']['value'])
        claims, fail = {}, []
        for i, it in enumerate(sorted(items, key=lambda s: int(s[1:]))):
            d = get_json(f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={it}&property={g['prop']}&format=json",
                         f"s1/claims/{g['id']}/{it}.json.gz", pace=0.6)
            if not d or '_status' in d or 'claims' not in d: fail.append(it); continue
            claims[it] = {'iso': sorted(items[it]), 'claims': d['claims'].get(g['prop'], [])}
        with gzip.open(cpath(f"s1/claims_{g['id']}.json.gz"), 'wt') as f: json.dump({'read': iso_utc(), 'items': claims, 'failed': fail}, f)
        meta[g['id']] = dict(items=len(items), read=len(claims), failed=fail)
        print(f"s1_frame {g['id']}: {len(items)} items in frame, {len(claims)} read, {len(fail)} failed", flush=True)
    return meta


# ----------------------------------------------------------------------------------------------------------- section 1: sources
def wb_versions():
    d = get_json('https://api.worldbank.org/v2/sources/57/version?format=json&per_page=500', 's1/wb/versions.json.gz', pace=1.0)
    v = d['source'][0]['concept'][0]['variable']
    return [(x['id'], x['value']) for x in v]

def wb_archive(code, ver, offline_only=False):
    """One archived WDI release of one series: {(iso3, year): value}. None when the release does not carry the series."""
    cache = f's1/wb/{code}/v{ver}.json.gz'
    if offline_only and not os.path.exists(cpath(cache)): return None
    out, page = {}, 1
    while True:
        d = get_json(f'https://api.worldbank.org/v2/sources/57/country/all/series/{code}/version/{ver}/time/all?format=json&per_page=25000&page={page}',
                     cache if page == 1 else cache.replace('.json.gz', f'_p{page}.json.gz'), permanent=True, pace=1.0)
        if not isinstance(d, dict) or 'source' not in d: return None
        for r in d['source'].get('data') or []:
            if r['value'] is None: continue
            var = {x['concept']: x['id'] for x in r['variable']}
            iso = LEGACY.get(var.get('Country'), var.get('Country')); t = var.get('Time', '')
            if not t.startswith('YR'): continue
            out[(iso, int(t[2:]))] = float(r['value'])
        if int(d.get('pages') or 1) <= page: break
        page += 1
    return out

def wb_current(code):
    out, page, meta = {}, 1, None
    while True:
        d = get_json(f'https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&source=2&page={page}',
                     f's1/wb/{code}/current_p{page}.json.gz', pace=1.0)
        if not isinstance(d, list) or len(d) < 2: return None, {'error': str(d)[:200]}
        meta = d[0]
        for r in d[1] or []:
            if r['value'] is None or not r.get('countryiso3code'): continue
            out[(r['countryiso3code'], int(r['date']))] = float(r['value'])
        if int(meta.get('pages') or 1) <= page: break
        page += 1
    return out, {'lastupdated': meta.get('lastupdated'), 'total': meta.get('total')}

def step_s1_wb(codes=None):
    vers = wb_versions(); codes = codes or [g['series'] for g in GROUPS if g['src'] == 'WB'] + SECONDARY_WB
    for code in codes:
        cur, m = wb_current(code)
        print(f'wb {code} current: {len(cur or {})} values, last updated {m.get("lastupdated")}', flush=True)
        n_car = 0
        for vid, _ in vers:
            a = wb_archive(code, vid)
            n_car += a is not None and len(a) > 0
        print(f'wb {code}: {n_car} of {len(vers)} archived releases carry the series', flush=True)

def uis_versions():
    d = get_json('https://api.uis.unesco.org/api/public/versions', 's1/uis/versions.json.gz', pace=1.0)
    dv = get_json('https://api.uis.unesco.org/api/public/versions/default', 's1/uis/version_default.json.gz', pace=1.0)
    vs = sorted(((x['version'], x['publicationDate'][:10], (x.get('description') or '')) for x in d), key=lambda x: x[1])
    return vs, dv['version']

def uis_release(code, ver):
    d = get_json(f'https://api.uis.unesco.org/api/public/data/indicators?indicator={code}&geoUnitType=NATIONAL&version={ver}',
                 f's1/uis/{code}/{ver}.json.gz', permanent=True, pace=1.0)
    if not isinstance(d, dict) or 'records' not in d: return None
    return {(r['geoUnit'], int(r['year'])): float(r['value']) for r in d['records'] if r.get('value') is not None}

def step_s1_uis():
    vs, dflt = uis_versions()
    for g in GROUPS:
        if g['src'] != 'UIS': continue
        n = [len(uis_release(g['series'], v) or {}) for v, _, _ in vs]
        print(f"uis {g['series']}: {len(vs)} versions read, default {dflt}, values per version {min(n)} to {max(n)}", flush=True)


# ----------------------------------------------------------------------------------------------------------- section 1: matching
def written_unit(amount):
    """PLAN written precision: d decimals -> 10^-d; a whole number with s significant digits and k trailing zeros -> 10^k when s >= 3,
    else 10^(k - (3 - s)), never below 1."""
    a = amount.lstrip('+')
    if a.startswith('-'): a = a[1:]
    if 'e' in a.lower(): raise ValueError('exponent form ' + amount)
    if '.' in a:
        return Decimal(1).scaleb(-len(a.split('.', 1)[1]))
    digits = a.lstrip('0') or '0'
    k = len(digits) - len(digits.rstrip('0')); s = len(digits.rstrip('0'))
    if digits == '0': return Decimal(1)
    e = k if s >= 3 else max(0, k - (3 - s))
    return Decimal(1).scaleb(e)

def matches(v, u, r):
    return abs(float(v) - r) <= float(u) / 2 + abs(r) * F32 + 1e-9

def matches_half_unit(v, u, r):
    """Sensitivity (note 2.6, defined after the data): half a written unit only, no single-precision term."""
    return abs(float(v) - r) <= float(u) / 2 + 1e-9

def cut_equal(v, u, r):
    """Sensitivity: the release value with its digits cut (not rounded) at the written unit equals the cited value."""
    from decimal import ROUND_DOWN
    q = (Decimal(repr(r)) / u).to_integral_value(rounding=ROUND_DOWN) * u
    return q == v

class Source:
    """current: {(iso, year): value}; older: [(release_id, label, {(iso, year): value} or None)] oldest first."""
    def __init__(self, name, current, current_label, older):
        self.name, self.current, self.current_label, self.older = name, current or {}, current_label, older
    def lookup(self, table, isos, year):
        for i in isos:
            if (i, year) in table: return table[(i, year)]
        return None

def bin_row(v, u, isos, year, src, m=None):
    m = m or matches
    cur = src.lookup(src.current, isos, year)
    seen = cur is not None
    if cur is not None and m(v, u, cur): return dict(bin=MATCH)
    hits = []
    for rid, lab, tab in src.older:
        if tab is None: continue
        r = src.lookup(tab, isos, year)
        if r is None: continue
        seen = True
        if m(v, u, r): hits.append((rid, lab))
    if hits: return dict(bin=OLDER, first=hits[0][1], last=hits[-1][1], last_id=hits[-1][0], n_releases=len(hits))
    if seen: return dict(bin=NOREL)
    return dict(bin=UNREAD, reason='no value for this country and year in any release read')

def size_row(v, u, cur):
    """PLAN size reading: g = (cited - current)/current, interval from the written precision; four outcomes against plus or minus 1 percent."""
    if cur is None: return dict(outcome=K.CANNOT_TELL, reason='no current value')
    if cur == 0: return dict(outcome=K.CANNOT_TELL, reason='current value is zero')
    fv, fu = float(v), float(u)
    g = (fv - cur) / cur; a = (fv - fu / 2 - cur) / cur; b = (fv + fu / 2 - cur) / cur
    lo, hi = min(a, b), max(a, b)          # note 2.3: no single-precision widening here, as the plan's size rule states
    return dict(outcome=K.classify(lo, hi, -SIZE, SIZE), gap=g, gap_lo=lo, gap_hi=hi)


def refs_of(claim, src):
    """Frame references of a claim for a source: list of (stated_in_hit, urls, codes, retrieved)."""
    out = []
    for r in claim.get('references', []) or []:
        sn = r.get('snaks', {})
        ids = {s['datavalue']['value'].get('id') for s in sn.get('P248', []) if s.get('snaktype') == 'value'}
        urls = [s['datavalue']['value'] for s in sn.get('P854', []) if s.get('snaktype') == 'value']
        retr = [s['datavalue']['value']['time'][1:11] for s in sn.get('P813', []) if s.get('snaktype') == 'value']
        if src == 'WB':
            hit = WB_SRC in ids or any(re.search(r'worldbank\.org|banquemondiale\.org', u, re.I) for u in urls)
            codes = {m.upper() for u in urls for m in re.findall(r'(?:indicator|indicateur)/([A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+)', u)}
        else:
            hit = UIS_SRC in ids or any(re.search(r'uis\.unesco\.org', u, re.I) for u in urls)
            codes = {m.upper().rstrip('.') for u in urls for m in re.findall(r'(SP\.[A-Za-z0-9.]+?)(?:&|%26|$)', urllib.parse.unquote(u))}
        if hit: out.append(dict(stated_in=(WB_SRC in ids) if src == 'WB' else (UIS_SRC in ids), urls=urls, codes=codes, retrieved=retr))
    return out

def build_rows(g, frame):
    """PLAN frame rules. Returns (rows, set_aside Counter, statements in frame)."""
    rows, aside, n_st = {}, C.Counter(), 0
    for it, rec in frame['items'].items():
        cl = rec['claims']; isos = rec['iso']
        has_pref = any(c.get('rank') == 'preferred' for c in cl)
        for c in cl:
            fr = refs_of(c, g['src'])
            if not fr: continue
            n_st += 1
            ms = c.get('mainsnak', {})
            if c.get('rank') == 'deprecated': aside['deprecated rank'] += 1; continue
            if ms.get('snaktype') != 'value': aside['no value (unknown or none)'] += 1; continue
            codes = set().union(*[r['codes'] for r in fr])
            if codes and g['series'] not in codes: aside['reference names another series'] += 1; continue
            q = c.get('qualifiers', {}) or {}
            if CHANGE_QUALS & set(q): aside['qualifier that changes what is measured'] += 1; continue
            dv = ms['datavalue']['value']
            unit = dv.get('unit', '1').rsplit('/', 1)[-1]
            if unit not in g['units']: aside['unit other than the group\'s'] += 1; continue
            ts = [x['datavalue']['value'] for x in q.get('P585', []) if x.get('snaktype') == 'value']
            if not ts: aside['no point in time'] += 1; continue
            if len(ts) > 1: aside['more than one point in time'] += 1; continue
            t = ts[0]
            if int(t.get('precision', 0)) < 9: aside['point in time coarser than a year'] += 1; continue
            if not t['time'].startswith('+'): aside['point in time before year 1'] += 1; continue
            year = int(t['time'][1:5])
            amt = dv['amount']
            try: v = Decimal(amt.lstrip('+')); u = written_unit(amt)
            except (InvalidOperation, ValueError): aside['amount not readable'] += 1; continue
            default = c.get('rank') == 'preferred' or (c.get('rank') == 'normal' and not has_pref)
            key = (it, year, v)
            r = rows.get(key)
            if r is None:
                r = rows[key] = dict(group=g['id'], item=it, iso=isos, series=g['series'], year=year, value=amt.lstrip('+'), v=v, u=u,
                                     unit=unit, statements=[], ranks=set(), default=False, stated_in=False, urls=set(), retrieved=set())
            elif u < r['u']: r['u'] = u; r['value'] = amt.lstrip('+')
            r['statements'].append(c.get('id')); r['ranks'].add(c.get('rank')); r['default'] |= default
            r['stated_in'] |= any(x['stated_in'] for x in fr)
            for x in fr: r['urls'].update(x['urls']); r['retrieved'].update(x['retrieved'])
    return list(rows.values()), aside, n_st


def load_sources(offline_only=False):
    """Build Source objects per series from the cached reads (fetching what is missing unless offline)."""
    srcs, meta = {}, {}
    vers = wb_versions()
    for code in [g['series'] for g in GROUPS if g['src'] == 'WB'] + SECONDARY_WB:
        cur, m = wb_current(code)
        older = [(vid, lab, wb_archive(code, vid, offline_only)) for vid, lab in vers]
        srcs[('WB', code)] = Source('World Bank', cur, f"current release (last updated {m.get('lastupdated')})", older)
        meta[('WB', code)] = dict(current_values=len(cur or {}), lastupdated=m.get('lastupdated'), releases_read=len(vers),
                                  releases_carrying=sum(1 for _, _, t in older if t))
    vs, dflt = uis_versions()
    for g in GROUPS:
        if g['src'] != 'UIS': continue
        tabs = {v: uis_release(g['series'], v) for v, _, _ in vs}
        lab = {v: f'UIS version {v} ({p})' for v, p, _ in vs}
        older = [(v, lab[v], tabs[v]) for v, _, _ in vs if v != dflt]
        srcs[('UIS', g['series'])] = Source('UIS', tabs[dflt], lab[dflt], older)
        distinct = len({hashlib.sha256(json.dumps(sorted((k[0], k[1], v) for k, v in t.items())).encode()).hexdigest() for t in tabs.values() if t})
        meta[('UIS', g['series'])] = dict(current_values=len(tabs[dflt] or {}), default_version=dflt, releases_read=len(vs),
                                          releases_carrying=sum(1 for t in tabs.values() if t), distinct_value_sets=distinct,
                                          first_version=vs[0][0], first_published=vs[0][1])
    return srcs, meta


def boot_shares(rows, keyf, cats, n=2000, seed=7):
    """PLAN: 95% interval from resampling countries with replacement (percentile). Returns {cat: (lo, hi)}."""
    by = C.defaultdict(lambda: C.Counter())
    for r in rows: by[r['item']][keyf(r)] += 1
    items = list(by); rng = random.Random(seed); res = {c: [] for c in cats}
    if not items: return {c: (None, None) for c in cats}
    for _ in range(n):
        tot = C.Counter(); m = 0
        for _ in items:
            cc = by[items[rng.randrange(len(items))]]; tot.update(cc); m += sum(cc.values())
        for c in cats: res[c].append(tot[c] / m if m else 0.0)
    out = {}
    for c in cats:
        s = sorted(res[c]); out[c] = (s[int(0.025 * n)], s[min(n - 1, int(0.975 * n))])
    return out

def share_table(rows, keyf, cats):
    n = len(rows); cnt = C.Counter(keyf(r) for r in rows); bs = boot_shares(rows, keyf, cats)
    out = {}
    for c in cats:
        lo, hi = K.wilson(cnt[c], n)
        out[c] = dict(k=cnt[c], n=n, share=(cnt[c] / n) if n else None, wilson95=[lo, hi], country95=list(bs[c]))
    return out


def known_good_s1(srcs, country_codes=None):
    """PLAN known-good 1: planted rows through the same matcher and size rule, on a country in the frame (note 2.12), not an aggregate."""
    res = []
    src = srcs[('WB', 'SP.POP.TOTL')]
    # find a country-year whose current value differs from a value carried only by older releases
    pick = None
    for (iso, yr), c in sorted(src.current.items()):
        if yr < 1990 or c < 1e6: continue
        if country_codes and iso not in country_codes: continue
        olds = [(rid, lab, t[(iso, yr)]) for rid, lab, t in src.older if t and (iso, yr) in t]
        diff = [x for x in olds if not matches(Decimal(int(x[2])), Decimal(1), c) and abs(x[2] - c) > 10]
        if diff:
            o = diff[-1]
            if not any(matches(Decimal(int(o[2])), Decimal(1), t[(iso, yr)]) for rid, lab, t in src.older if t and (iso, yr) in t and rid > o[0]):
                pick = (iso, yr, c, o); break
    if pick is None: return False, dict(error='no country-year found to plant on')
    iso, yr, c, (orid, olab, oval) = pick
    def plant(name, v, u, isos, want_bin=None, want_last=None, want_out=None):
        b = bin_row(Decimal(v), Decimal(u), isos, yr, src); s = size_row(Decimal(v), Decimal(u), src.lookup(src.current, isos, yr))
        ok = (want_bin is None or b['bin'] == want_bin) and (want_last is None or b.get('last_id') == want_last) and (want_out is None or s['outcome'] == want_out)
        res.append(dict(test=name, ok=ok, bin=b['bin'], last=b.get('last'), outcome=s['outcome']))
    plant('equal to the current release', repr(int(c)), 1, [iso], MATCH)
    plant('equal to a value only an older release carried', repr(int(oval)), 1, [iso], OLDER, orid)
    far = c * 1.005
    while any(matches(Decimal(int(far)), Decimal(1), t[(iso, yr)]) for _, _, t in src.older if t and (iso, yr) in t): far *= 1.001
    plant('0.5 percent away from every release', repr(int(far)), 1, [iso], NOREL)
    plant('a code no release carries', repr(int(c)), 1, ['ZZZ'], UNREAD)
    plant('gap +2 percent', repr(int(c * 1.02)), 1, [iso], want_out=K.ABOVE)
    plant('gap -2 percent', repr(int(c * 0.98)), 1, [iso], want_out=K.BELOW)
    plant('gap +0.5 percent', repr(int(c * 1.005)), 1, [iso], want_out=K.CONSISTENT)
    v3 = float(f'{c * 1.01:.3g}'); u3 = written_unit(repr(int(v3)))
    plant('gap +1 percent written to three significant digits', repr(int(v3)), u3, [iso], want_out=K.CANNOT_TELL)
    ok = all(r['ok'] for r in res)
    # precision rule unit tests
    pr = [('+28171682', 1), ('+24036000', 1000), ('+7000000', 10000), ('+72.50', Decimal('0.01')), ('+2.1', Decimal('0.1')), ('+50', 1), ('+1210000000', 10000000)]
    prok = all(written_unit(a) == Decimal(w) for a, w in pr)
    res.append(dict(test='written precision rule on seven examples', ok=prok))
    return ok and prok, dict(planted_on=f'{iso} {yr}', current=c, older_value=oval, older_release=olab, tests=res)

def known_good_scout(srcs):
    """PLAN known-good 2: our pull of each release the scout pulled equals the scout's file."""
    d = os.path.expanduser('~/bones-forge/research_wiki/samples/cited/wdi_archive/')
    src = srcs[('WB', 'SP.POP.TOTL')]; ours = {rid: t for rid, _, t in src.older}
    out = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith('.json.gz'): continue
        ver = f[1:7]
        with gzip.open(os.path.join(d, f), 'rt') as fh: s = json.load(fh)['source']['data']
        theirs = {}
        for r in s:
            if r['value'] is None: continue
            var = {x['concept']: x['id'] for x in r['variable']}
            theirs[(LEGACY.get(var['Country'], var['Country']), int(var['Time'][2:]))] = float(r['value'])
        mine = ours.get(ver) or {}
        same = len(mine) == len(theirs) and all(abs(mine.get(k, float('nan')) - v) <= 1e-9 * max(1, abs(v)) for k, v in theirs.items())
        out.append(dict(release=ver, values_ours=len(mine), values_scout=len(theirs), equal=same))
    return all(x['equal'] for x in out) and len(out) > 0, out


def score_s1(srcs, smeta):
    groups, all_rows, frame_meta = {}, [], {}
    for g in GROUPS:
        with gzip.open(cpath(f"s1/claims_{g['id']}.json.gz"), 'rt') as f: frame = json.load(f)
        rows, aside, n_st = build_rows(g, frame)
        src = srcs[(g['src'], g['series'])]
        for r in rows:
            r.update(bin_row(r['v'], r['u'], r['iso'], r['year'], src))
            cur = src.lookup(src.current, r['iso'], r['year']); r['current'] = cur
            s = size_row(r['v'], r['u'], cur); r['outcome'] = s['outcome']; r['gap'] = s.get('gap'); r['gap_lo'] = s.get('gap_lo'); r['gap_hi'] = s.get('gap_hi')
            if 'reason' in s: r['outcome_reason'] = s['reason']
        frame_meta[g['id']] = dict(items_in_frame=len(frame['items']), items_failed=frame.get('failed', []), frame_read=frame.get('read'),
                                   statements_in_frame=n_st, set_aside=dict(aside), rows=len(rows))
        all_rows += rows
    # secondary reading for UIS rows (descriptive): the plain World Bank bin and the newest World Bank release carrying the value
    for r in all_rows:
        if r['group'].startswith('UIS') and r['bin'] in (NOREL, UNREAD):
            b = bin_row(r['v'], r['u'], r['iso'], r['year'], srcs[('WB', r['series'])])
            r['wb_secondary'] = b['bin']; r['wb_newest'] = b.get('last'); r['wb_newest_id'] = b.get('last_id')
    return all_rows, frame_meta


def sensitivity_s1(rows, srcs):
    """Readings defined after the data (note 2): the tolerance sensitivity (F1) and the wrong-year chance match (F3). No bin changes."""
    out = {}
    for g in GROUPS:
        rs = [r for r in rows if r['group'] == g['id']]; src = srcs[(g['src'], g['series'])]
        half = C.Counter(); moved = C.Counter(); kinds = C.Counter(); ex = {}
        for r in rs:
            b0 = r['bin']; b1 = bin_row(r['v'], r['u'], r['iso'], r['year'], src, m=matches_half_unit)['bin']; half[b1] += 1
            if b1 != b0:
                moved[f'{b0} -> {b1}'] += 1
                bc = bin_row(r['v'], r['u'], r['iso'], r['year'], src, m=lambda v, u, x: matches_half_unit(v, u, x) or cut_equal(v, u, x))['bin']
                k = 'cut' if bc == b0 else 'revision'; kinds[k] += 1
                ex.setdefault(k, dict(item=r['item'], iso=r['iso'][0], year=r['year'], cited=r['value'], current=r['current'], bin=b0, half_unit_bin=b1, cut_bin=bc))
        # wrong-year chance match: each figure read against every release's value two years earlier and two years later
        tries = hits = wt = wh = 0
        for r in rs:
            for dy in (-2, 2):
                b = bin_row(r['v'], r['u'], r['iso'], r['year'] + dy, src)['bin']
                if b == UNREAD: continue
                tries += 1; hit = b in (MATCH, OLDER); hits += hit
                if '.' not in r['value']: wt += 1; wh += hit
        cons = C.Counter(r['item'] for r in rs if r['outcome'] == K.CONSISTENT)
        top = cons.most_common(1)[0] if cons else None
        out[g['id']] = dict(half_unit_bins={b: half[b] for b in BINS}, moved=sum(moved.values()), moved_by=dict(moved), moved_kinds=dict(kinds), examples=ex,
                            wrong_year=dict(tries=tries, matches=hits, share=hits / tries if tries else None,
                                            whole_tries=wt, whole_matches=wh, whole_share=wh / wt if wt else None),
                            consistent_top_country=dict(item=top[0], rows=top[1], of=sum(cons.values())) if top else None)
    return out


def summarize_s1(rows, frame_meta, smeta):
    out = {}; load_names(); load_labels([r['item'] for r in rows])
    def block(rs):
        nm = [r for r in rs if r['bin'] != MATCH and r['current'] is not None and r['gap'] is not None]
        med = sorted(abs(r['gap']) for r in nm); medv = (med[len(med) // 2] if len(med) % 2 else (med[len(med) // 2 - 1] + med[len(med) // 2]) / 2) if med else None
        return dict(rows=len(rs), countries=len({r['item'] for r in rs}), country_years=len({(r['item'], r['year']) for r in rs}),
                    written_whole=sum(1 for r in rs if '.' not in r['value']),
                    written_whole_size=dict(C.Counter(r['outcome'] for r in rs if '.' not in r['value'])),
                    bins=share_table(rs, lambda r: r['bin'], BINS), size=share_table(rs, lambda r: r['outcome'], OUTS),
                    size_cannot_tell_reasons=dict(C.Counter(r.get('outcome_reason', 'interval crosses 1 percent') for r in rs if r['outcome'] == K.CANNOT_TELL)),
                    median_abs_gap_not_matching_current=medv,
                    newest_matching_release_by_year=dict(sorted(C.Counter(r['last_id'][:4] for r in rs if r['bin'] == OLDER).items())),
                    on_the_line=[dict(item=it, label=LABELS.get(it), rows=len(v), years=[min(x['year'] for x in v), max(x['year'] for x in v)],
                                      outcomes=dict(C.Counter(x['outcome'] for x in v)))
                                 for it, v in C.OrderedDict((it, [x for x in rs if x['item'] == it and x['gap'] is not None and abs(abs(x['gap']) - SIZE) < 1e-6])
                                                            for it in sorted({x['item'] for x in rs if x['gap'] is not None and abs(abs(x['gap']) - SIZE) < 1e-6})).items()],
                    years=[min(r['year'] for r in rs), max(r['year'] for r in rs)] if rs else None)
    for g in GROUPS:
        rs = [r for r in rows if r['group'] == g['id']]
        b = block(rs); b['defaults'] = block([r for r in rs if r['default']])
        b['label'] = g['label']; b['series'] = g['series']; b['source'] = 'World Bank WDI' if g['src'] == 'WB' else 'UNESCO Institute for Statistics'
        b['property'] = g['prop']; b['frame'] = frame_meta[g['id']]; b['source_read'] = smeta[(g['src'], g['series'])]
        if g['id'] == 'WB-GDP':
            b['by_unit'] = {u: dict(C.Counter(r['bin'] for r in rs if r['unit'] == u)) for u in sorted({r['unit'] for r in rs})}
        if g['src'] == 'UIS':
            b['wb_secondary'] = {f'{k[0]} -> {k[1]}': v for k, v in C.Counter((r['bin'], r['wb_secondary']) for r in rs if 'wb_secondary' in r).most_common()}
            nr = [r for r in rs if r['bin'] == NOREL]
            b['wb_secondary_norel'] = dict(rows=len(nr), match_current=sum(1 for r in nr if r.get('wb_secondary') == MATCH),
                                          match_older=sum(1 for r in nr if r.get('wb_secondary') == OLDER),
                                          match_none=sum(1 for r in nr if r.get('wb_secondary') == NOREL),
                                          nothing=sum(1 for r in nr if r.get('wb_secondary') == UNREAD),
                                          newest_by_year=dict(sorted(C.Counter((r.get('wb_newest_id') or '')[:4] for r in nr if r.get('wb_secondary') == OLDER).items())))
            b['uis_citation'] = dict(rows=len(rs), cite_uis_stat=sum(1 for r in rs if any('data.uis.unesco.org' in u.lower() for u in r['urls'])),
                                     no_retrieved=sum(1 for r in rs if not r['retrieved']),
                                     retrieved_months=dict(sorted(C.Counter(min(r['retrieved'])[:7] for r in rs if r['retrieved']).items())))
        # listing rule: 10 default rows with the largest absolute gap, and every default row beyond 10 percent
        ds = sorted([r for r in rs if r['default'] and r['gap'] is not None], key=lambda r: -abs(r['gap']))
        lst = ds[:10] + [r for r in ds[10:] if abs(r['gap']) > 0.10]
        b['notable'] = [row_public(r) for r in lst]
        # defined after the data: figures that returned nothing because the item's code is not the source's code for that territory
        ph = []
        for r in rs:
            if r['bin'] == UNREAD and r['iso'] and r['iso'][0] in POST_HOC_ALIAS and SRCS_REF:
                src = SRCS_REF[(g['src'], g['series'])]; a = POST_HOC_ALIAS[r['iso'][0]]
                bb = bin_row(r['v'], r['u'], [a], r['year'], src)
                ph.append(dict(item=r['item'], code=r['iso'][0], alias=a, year=r['year'], cited=r['value'], bin_under_alias=bb['bin'], newest_release=bb.get('last')))
        if ph: b['post_hoc_alias'] = dict(note='defined after the data; the bins above are unchanged', rows=ph,
                                          counts=dict(C.Counter(x['bin_under_alias'] for x in ph)))
        out[g['id']] = b
    allb = block(rows); allb['defaults'] = block([r for r in rows if r['default']])
    out['ALL'] = allb
    return out

NAMES = {}; LABELS = {}; SRCS_REF = {}
POST_HOC_ALIAS = {'DHY': 'BEN', 'XKS': 'XKX'}   # defined after the data (PLAN note 1): Dahomey's ISO 3166-3 code, Kosovo's code in Wikidata
def load_labels(items):
    """English labels of the items, from the Wikidata API (50 per call, cached)."""
    items = sorted(set(items), key=lambda x: int(x[1:]))
    for i in range(0, len(items), 50):
        chunk = items[i:i + 50]
        d = get_json('https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&format=json&ids=' + '|'.join(chunk),
                     f's1/labels/{chunk[0]}_{len(chunk)}_{hashlib.sha1("|".join(chunk).encode()).hexdigest()[:8]}.json.gz', pace=0.6)
        for q, e in ((d or {}).get('entities') or {}).items():
            lab = (e.get('labels') or {}).get('en', {}).get('value')
            if lab: LABELS[q] = lab

def load_names():
    p = cpath('s1/wb/SP.POP.TOTL/current_p1.json.gz')
    if os.path.exists(p):
        with gzip.open(p, 'rt') as f: d = json.load(f)
        for r in d[1] or []:
            if r.get('countryiso3code'): NAMES[r['countryiso3code']] = r['country']['value']

def row_public(r):
    g = next(x for x in GROUPS if x['id'] == r['group']); iso = r['iso'][0] if r['iso'] else None
    if g['src'] == 'WB':
        cur_url = f"https://api.worldbank.org/v2/country/{iso}/indicator/{g['series']}?date={r['year']}&format=json"
        old_url = f"https://api.worldbank.org/v2/sources/57/country/{iso}/series/{g['series']}/version/{r['last_id']}/time/YR{r['year']}?format=json" if r.get('last_id') else None
    else:
        cur_url = f"https://api.uis.unesco.org/api/public/data/indicators?indicator={g['series']}&geoUnit={iso}&start={r['year']}&end={r['year']}"
        old_url = cur_url + f"&version={r['last_id']}" if r.get('last_id') else None
    wb_url = (f"https://api.worldbank.org/v2/sources/57/country/{iso}/series/{g['series']}/version/{r['wb_newest_id']}/time/YR{r['year']}?format=json"
              if r.get('wb_newest_id') else None)
    return dict(group=r['group'], item=r['item'], iso=iso, name=LABELS.get(r['item']) or NAMES.get(iso, iso), year=r['year'], cited=r['value'], current=r['current'],
                gap=r['gap'], bin=r['bin'], newest_release=r.get('last'), first_release=r.get('first'), n_releases=r.get('n_releases'), outcome=r['outcome'],
                default=r['default'], statements=r['statements'][:3], wikidata_url=f"https://www.wikidata.org/wiki/{r['item']}#{g['prop']}",
                source_url=cur_url, release_url=old_url, written_whole='.' not in r['value'],
                wb_secondary=r.get('wb_secondary'), wb_newest=r.get('wb_newest'), wb_release_url=wb_url)


def hand_check_s1(rows, srcs, n=10, seed=11):
    """PLAN known-good 3: seeded draw of rows, read again from the query service (Wikidata value) and the single-country source call."""
    rng = random.Random(seed); pool = sorted(rows, key=lambda r: (r['group'], r['item'], r['year'], str(r['v'])))
    pick = rng.sample(pool, min(n, len(pool))); out = []
    for r in pick:
        g = next(x for x in GROUPS if x['id'] == r['group']); sid = r['statements'][0]
        q = f"SELECT ?a WHERE {{ wds:{sid.replace('$', '-')} psv:{g['prop']} ?n . ?n wikibase:quantityAmount ?a . }}"
        try: b = wdqs(q, f"s1/handcheck/{sid.replace('$', '_')}.json.gz"); wd = b[0]['a']['value'] if b else None
        except Exception as e: wd = f'error {e}'
        iso = r['iso'][0]
        if g['src'] == 'WB':
            d = get_json(f"https://api.worldbank.org/v2/country/{iso}/indicator/{g['series']}?date={r['year']}&format=json&source=2",
                         f"s1/handcheck/wb_{iso}_{g['series']}_{r['year']}.json.gz", pace=1.0)
            sv = d[1][0]['value'] if isinstance(d, list) and len(d) > 1 and d[1] else None
        else:
            d = get_json(f"https://api.uis.unesco.org/api/public/data/indicators?indicator={g['series']}&geoUnit={iso}&start={r['year']}&end={r['year']}",
                         f"s1/handcheck/uis_{iso}_{g['series']}_{r['year']}.json.gz", pace=1.0)
            sv = d['records'][0]['value'] if isinstance(d, dict) and d.get('records') else None
        wd_ok = wd is not None and not str(wd).startswith('error') and Decimal(str(wd)) == r['v']
        src_ok = (sv is None and r['current'] is None) or (sv is not None and r['current'] is not None and abs(float(sv) - r['current']) <= 1e-9 * max(1, abs(r['current'])))
        out.append(dict(group=r['group'], item=r['item'], iso=iso, year=r['year'], statement=sid, cited=r['value'], query_service=wd,
                        source_single_call=sv, source_bulk=r['current'], wikidata_agrees=wd_ok, source_agrees=src_ok))
    return out


HAND_QUOTA = [('WB-POP', 3), ('WB-GDP', 2), ('WB-GINI', 1), ('WB-UNEMP', 1), ('UIS-LE', 2), ('UIS-TFR', 1)]
def step_s1_handcheck():
    """PLAN known-good 3, run as the plan specifies (note 2.2): ten rows drawn with seed 11 across groups (quota above, defined after the first
    run), each opened in the live Wikidata entity JSON (wbgetentities: value, year, rank, reference) and in the source's single-country record
    for the release its bin names."""
    with gzip.open(cpath('s1/rows.json.gz'), 'rt') as f: rows = json.load(f)
    rng = random.Random(11); pick = []
    for gid, n in HAND_QUOTA:
        pool = sorted([r for r in rows if r['group'] == gid], key=lambda r: (r['item'], r['year'], r['value']))
        pick += rng.sample(pool, n)
    out = []
    for r in pick:
        g = next(x for x in GROUPS if x['id'] == r['group']); sid = r['statements'][0]; it = r['item']; iso = r['iso'][0]; y = r['year']
        ent = get_json(f'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={it}&props=claims&format=json', f's1/handcheck_plan/{it}.json.gz', pace=0.6)
        cl = next((c for c in ((ent or {}).get('entities', {}).get(it, {}).get('claims', {}).get(g['prop'], [])) if c.get('id') == sid), None)
        wd = {}
        if cl:
            dv = cl['mainsnak']['datavalue']['value']; ts = [q['datavalue']['value']['time'] for q in (cl.get('qualifiers') or {}).get('P585', []) if q.get('snaktype') == 'value']
            wd = dict(amount=dv['amount'].lstrip('+'), year=int(ts[0][1:5]) if ts else None, rank=cl.get('rank'), frame_reference=bool(refs_of(cl, g['src'])))
        v = Decimal(r['value']); u = written_unit(r['value'])
        if g['src'] == 'WB':
            d = get_json(f"https://api.worldbank.org/v2/country/{iso}/indicator/{g['series']}?date={y}&format=json&source=2", f"s1/handcheck_plan/wb_{iso}_{g['series']}_{y}.json.gz", pace=1.0)
            cur = d[1][0]['value'] if isinstance(d, list) and len(d) > 1 and d[1] else None
            rel = None
            if r.get('last_id'):
                a = get_json(f"https://api.worldbank.org/v2/sources/57/country/{iso}/series/{g['series']}/version/{r['last_id']}/time/YR{y}?format=json",
                             f"s1/handcheck_plan/wbrel_{iso}_{g['series']}_{r['last_id']}_{y}.json.gz", pace=1.0)
                dd = a.get('source', {}).get('data') if isinstance(a, dict) else None; rel = dd[0]['value'] if dd else None
        else:
            base = f"https://api.uis.unesco.org/api/public/data/indicators?indicator={g['series']}&geoUnit={iso}&start={y}&end={y}"
            d = get_json(base, f"s1/handcheck_plan/uis_{iso}_{g['series']}_{y}.json.gz", pace=1.0)
            cur = d['records'][0]['value'] if isinstance(d, dict) and d.get('records') else None
            rel = None
            if r.get('last_id'):
                a = get_json(base + f"&version={r['last_id']}", f"s1/handcheck_plan/uisrel_{iso}_{g['series']}_{r['last_id']}_{y}.json.gz", pace=1.0)
                rel = a['records'][0]['value'] if isinstance(a, dict) and a.get('records') else None
        cur_m = cur is not None and matches(v, u, float(cur))
        if r['bin'] == MATCH: bin_ok = cur_m
        elif r['bin'] == OLDER: bin_ok = rel is not None and matches(v, u, float(rel)) and not cur_m
        elif r['bin'] == NOREL: bin_ok = not cur_m
        else: bin_ok = cur is None
        ok = dict(value=bool(wd) and Decimal(wd['amount']) == v, year=wd.get('year') == y, rank=wd.get('rank') in r['ranks'], reference=wd.get('frame_reference', False),
                  current=(cur is None and r['current'] is None) or (cur is not None and r['current'] is not None and abs(float(cur) - r['current']) <= 1e-9 * max(1, abs(r['current']))),
                  bin=bin_ok)
        out.append(dict(group=r['group'], item=it, iso=iso, year=y, statement=sid, cited=r['value'], bin=r['bin'], newest_release=r.get('last'), wikidata=wd,
                        source_current=cur, source_release=rel, checks=ok, all_agree=all(ok.values())))
    json.dump(dict(read=iso_utc(), draw='seed 11, quota ' + ', '.join(f'{g} {n}' for g, n in HAND_QUOTA), rows=out), open(cpath('s1/handcheck_plan.json'), 'w'), indent=1, default=jsonable)
    print(f"hand check as planned: {sum(1 for x in out if x['all_agree'])} of {len(out)} agree on value, year, rank, reference, current value and bin", flush=True)
    for x in out:
        if not x['all_agree']: print('  DISAGREE', x, flush=True)
    return dict(rows=len(out), agree=sum(1 for x in out if x['all_agree']))


def step_s1_notable():
    """PLAN hand check: every row under the listing rule is re-read before it is shown: the statement from the query service
    (value, rank, year) and the source's single-country record for the current release and for the named older release."""
    s1 = json.load(open(cpath('s1/s1_summary.json'))); out = []
    for gid, g in s1['groups'].items():
        if gid == 'ALL': continue
        grp = next(x for x in GROUPS if x['id'] == gid)
        for r in g.get('notable', []):
            sid = r['statements'][0]; w = sid.replace('$', '-')
            q = (f"SELECT ?a ?rank ?t WHERE {{ wds:{w} psv:{grp['prop']} ?n . ?n wikibase:quantityAmount ?a . wds:{w} wikibase:rank ?rank . "
                 f"OPTIONAL {{ wds:{w} pq:P585 ?t }} }}")
            try:
                b = wdqs(q, f"s1/notable/{sid.replace('$', '_')}.json.gz"); b = b[0] if b else {}
                wd_val, wd_rank, wd_t = b.get('a', {}).get('value'), b.get('rank', {}).get('value', '').rsplit('#', 1)[-1], b.get('t', {}).get('value', '')[:4]
            except Exception as e:
                wd_val, wd_rank, wd_t = f'error {e}', '', ''
            cur = get_json(r['source_url'], f"s1/notable/src_{gid}_{r['iso']}_{r['year']}.json.gz", pace=1.0)
            if grp['src'] == 'WB': cv = cur[1][0]['value'] if isinstance(cur, list) and len(cur) > 1 and cur[1] else None
            else: cv = cur['records'][0]['value'] if isinstance(cur, dict) and cur.get('records') else None
            rv = None
            if r.get('release_url'):
                rel = get_json(r['release_url'], f"s1/notable/rel_{gid}_{r['iso']}_{r['year']}.json.gz", pace=1.0)
                if grp['src'] == 'WB':
                    dd = (rel or {}).get('source', {}).get('data') if isinstance(rel, dict) else None
                    rv = dd[0]['value'] if dd else None
                else: rv = rel['records'][0]['value'] if isinstance(rel, dict) and rel.get('records') else None
            ok_wd = wd_val is not None and not str(wd_val).startswith('error') and Decimal(str(wd_val)) == Decimal(r['cited']) and wd_t == str(r['year'])
            ok_cur = (cv is None and r['current'] is None) or (cv is not None and r['current'] is not None and abs(float(cv) - r['current']) <= 1e-9 * max(1, abs(r['current'])))
            ok_rel = (r.get('release_url') is None) or (rv is not None and matches(Decimal(r['cited']), written_unit(r['cited']), float(rv)))
            out.append(dict(group=gid, item=r['item'], iso=r['iso'], year=r['year'], statement=sid, cited=r['cited'], wd_query_service=wd_val, wd_rank=wd_rank,
                            wd_year=wd_t, source_current=cv, release=r.get('newest_release'), release_value=rv, wikidata_agrees=ok_wd, current_agrees=ok_cur,
                            release_agrees=ok_rel, all_agree=ok_wd and ok_cur and ok_rel))
    json.dump(out, open(cpath('s1/notable_check.json'), 'w'), indent=1, default=jsonable)
    bad = [x for x in out if not x['all_agree']]
    print(f'notable rows re-read: {len(out)}, all agree {len(out) - len(bad)}, disagree {len(bad)}', flush=True)
    for x in bad: print('  DISAGREE', x, flush=True)
    return dict(rows=len(out), disagree=len(bad))


# ----------------------------------------------------------------------------------------------------------- section 2: stated side
PAGES = {'home': 'https://wikimediafoundation.org/',
         'projects': 'https://wikimediafoundation.org/what-we-do/wikimedia-projects/',
         'ar': 'https://wikimediafoundation.org/annualreports/2024-2025-annual-report/'}
PAGE_NAMES = {'home': 'Wikimedia Foundation homepage', 'projects': 'Wikimedia Foundation projects page', 'ar': 'Wikimedia Foundation Annual Report 2024-2025'}
WAYBACK_FROM = {'home': '2024', 'projects': '2022', 'ar': '2025'}
STATED = [
    dict(id='home_views', page='home', pat=r'Wikipedia receives nearly 15 billion views each month\.', word='nearly', X=15e9, kind='views', window='latest12', stated_scope='Wikipedia'),
    dict(id='home_volunteers', page='home', pat=r'The Wikimedia Foundation supports nearly 265,000 volunteers every month\.', word='nearly', X=265000, kind='volunteers', window='latest12', scope='all_wikis'),
    dict(id='home_edits', page='home', pat=r'Every minute 324 new edits are made to Wikipedia\.', word='plain', X=324, unit=1, kind='edits', window='latest12'),
    dict(id='home_articles', page='home', pat=r'With over 67 million articles, in 300\+ languages', word='over', X=67e6, kind='articles', window='today',
         quote_pat=r'With over 67 million articles, in 300\+ languages, Wikipedia is the home of trusted information online\.', focus='over 67 million articles'),
    dict(id='home_languages', page='home', pat=r'in 300\+ languages', word='plus', X=300, kind='languages', window='today', quote_pat=r'300\+ languages'),
    dict(id='home_built_by', page='home', pat=r'Wikipedia is built by nearly 250,000 volunteers', word='nearly', X=250000, kind='volunteers', window='latest12', scope='wikipedias',
         quote_pat=r'Wikipedia is built by nearly 250,000 volunteers[^.]*\.'),
    dict(id='projects_commons', page='projects', pat=r'114 million images, photographs, videos and music files and counting', word='counting', X=114e6, kind='commons', window='today'),
    dict(id='ar_edits_more', page='ar', pat=r'More than 340 edits every minute\.', word='over', X=340, kind='edits', window='fy2425'),
    dict(id='ar_articles_more', page='ar', pat=r'More than 66 million articles\.', word='over', X=66e6, kind='articles', window='moments'),
    dict(id='ar_articles', page='ar', pat=r'66 million Wikipedia articles', word='plain', X=66e6, unit=1e6, kind='articles', window='moments'),
    dict(id='ar_languages', page='ar', pat=r'300\+ Languages on Wikipedia', word='plus', X=300, kind='languages', window='moments'),
    dict(id='ar_commons', page='ar', pat=r'135 million freely usable media files on Wikimedia Commons', word='plain', X=135e6, unit=1e6, kind='commons', window='moments'),
    dict(id='ar_edits', page='ar', pat=r'324 edits to Wikipedia every minute', word='plain', X=324, unit=1, kind='edits', window='fy2425'),
    dict(id='ar_volunteer_editors', page='ar', pat=r'250,000 volunteer editors of Wikipedia around the world', word='plain', X=250000, unit=10000, kind='volunteers', window='fy2425', scope='wikipedias'),
    dict(id='ar_volunteers_more', page='ar', pat=r'Volunteer contributors add the knowledge on Wikipedia, and they live in almost every country of the world, numbering more than 250,000\.',
         word='over', X=250000, kind='volunteers', window='fy2425', scope='wikipedias'),
    dict(id='ar_views', page='ar', pat=r'Nearly 15 billion views on Wikipedia every month', word='nearly', X=15e9, kind='views', window='fy2425', stated_scope='Wikipedia'),
]
BLOCK = r'(?:p|div|br|li|ul|ol|h[1-6]|section|article|header|footer|figure|figcaption|tr|td|th|table|blockquote|nav|main|aside)'

def page_text(h):
    t = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', h)
    t = re.sub(r'(?i)</?' + BLOCK + r'\b[^>]*>', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = HTML.unescape(t).replace(' ', ' ').replace('’', "'")
    return re.sub(r'\s+', ' ', t).strip()

def step_s2_stated():
    out = {}
    for k, url in PAGES.items():
        st, b = http(url, pace=2.0)
        rec = dict(url=url, read=iso_utc(), status=st)
        if st == 200:
            h = b.decode('utf8', 'replace'); t = page_text(h)
            ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
            with gzip.open(cpath(f'stated/{k}_{ts}.html.gz'), 'wt') as f: f.write(h)
            with gzip.open(cpath(f'stated/{k}_latest.txt.gz'), 'wt') as f: f.write(t)
            rec.update(sha256_html=sha256(b), chars=len(t), file=f'data/raw/stated/{k}_{ts}.html.gz')
        out[k] = rec
    json.dump(out, open(cpath('stated/pages_read.json'), 'w'), indent=1)
    return {k: dict(status=v['status'], read=v['read']) for k, v in out.items()}

PILCROW = '\u00b6'
def page_text_blocks(h):
    """Like page_text, with every block boundary kept as a pilcrow, to tell a sentence from a figure card (lead-in, number, caption)."""
    t = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', h)
    t = re.sub(r'(?i)</?' + BLOCK + r'\b[^>]*>', f' {PILCROW} ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = HTML.unescape(t).replace('\u00a0', ' ').replace('\u2019', "'")
    t = re.sub(r'\s+', ' ', t)
    return re.sub(r'(?:\s*' + PILCROW + r'\s*)+', f' {PILCROW} ', t).strip()

def is_card(quote, tb):
    sep = r'(?:\s*' + PILCROW + r'\s*|\s+)'
    pat = sep.join(re.escape(w) for w in quote.split(' '))
    m = re.search(pat, tb)
    return bool(m) and PILCROW in m.group(0)

def stated_quotes():
    pr = json.load(open(cpath('stated/pages_read.json')))
    res = []; blocks = {}
    for s in STATED:
        p = cpath(f"stated/{s['page']}_latest.txt.gz")
        t = gzip.open(p, 'rt').read() if os.path.exists(p) else ''
        if s['page'] not in blocks:
            f = pr.get(s['page'], {}).get('file'); hp = os.path.join(H, f) if f else None
            blocks[s['page']] = page_text_blocks(gzip.open(hp, 'rt').read()) if hp and os.path.exists(hp) else ''
        m = re.search(s['pat'], t); mq = re.search(s.get('quote_pat') or s['pat'], t)
        q = mq.group(0) if mq else (m.group(0) if m else None)
        res.append(dict(s, url=PAGES[s['page']], page_name=PAGE_NAMES[s['page']], read=pr.get(s['page'], {}).get('read'),
                        quote=q, found=bool(m), card=bool(q) and is_card(q, blocks[s['page']])))
    return res


# ----------------------------------------------------------------------------------------------------------- section 2: wayback
def wayback_text(page, ts, original):
    p = cpath(f'wayback/{page}/{ts}.txt.gz')
    if os.path.exists(p): return gzip.open(p, 'rt').read()
    if OFFLINE: return None
    st, b = http(f'https://web.archive.org/web/{ts}id_/{original}', pace=6.0, tries=3, timeout=60)
    if st != 200: return None
    t = page_text(b.decode('utf8', 'replace'))
    with gzip.open(p, 'wt') as f: f.write(t)
    return t

def step_s2_wayback():
    res = {}
    for page, url in PAGES.items():
        cdx = get_json(f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(url.replace('https://', ''), safe='/')}&output=json&from={WAYBACK_FROM[page]}"
                       f"&filter=statuscode:200&collapse=digest&fl=timestamp,digest,original", f'wayback/cdx_{page}.json.gz', pace=3.0)
        caps = [dict(ts=r[0], original=r[2]) for r in (cdx[1:] if isinstance(cdx, list) else [])]
        for s in [x for x in STATED if x['page'] == page]:
            def has(i):
                for j in (i, i + 1, i - 1, i + 2):            # a capture that will not load is replaced by a neighbour
                    if 0 <= j < len(caps):
                        t = wayback_text(page, caps[j]['ts'], caps[j]['original'])
                        if t is not None: return j, bool(re.search(s['pat'], t))
                return i, None
            r = dict(captures=len(caps))
            if not caps: r['note'] = 'no captures listed'; res[s['id']] = r; continue
            jn, last_has = has(len(caps) - 1)
            if last_has is None: r['note'] = 'latest capture could not be read'; res[s['id']] = r; continue
            if not last_has: r.update(note='not in the latest capture', latest_capture=caps[jn]['ts']); res[s['id']] = r; continue
            j0, first_has = has(0)
            if first_has:
                r.update(first_with=caps[j0]['ts'], last_without=None, note=f'in the earliest capture read (from {WAYBACK_FROM[page]})')
                mids = sorted({j0 + (jn - j0) * q // 5 for q in (1, 2, 3, 4)} - {j0, jn})
                chk = [(caps[j]['ts'], has(j)[1]) for j in mids]
                r['stays_check'] = [dict(capture=c[0], carries=c[1]) for c in chk]
                if any(c[1] is False for c in chk): r['note'] = 'the phrase is missing from a later capture, so the first capture is not a start date'
                res[s['id']] = r; continue
            lo, hi = j0, jn
            while hi - lo > 1:
                mid = (lo + hi) // 2; j, h = has(mid)
                if h is None: r['note'] = 'a capture in the bisection could not be read'; break
                if h: hi = j if j > lo else hi
                else: lo = j if j < hi else lo
                if j <= lo and h: break
            r.update(first_with=caps[hi]['ts'], last_without=caps[lo]['ts'])
            # bisection assumes the phrase stays once added: four evenly spaced later captures must carry it
            later = sorted({hi + (jn - hi) * q // 5 for q in (1, 2, 3, 4)} - {hi, jn})
            chk = [(caps[j]['ts'],) + (has(j)[1],) for j in later]
            r['stays_check'] = [dict(capture=c[0], carries=c[1]) for c in chk]
            if any(c[1] is False for c in chk): r['note'] = 'the phrase is missing from a later capture, so the first capture is not a start date'
            res[s['id']] = r
            print(f"wayback {s['id']}: first with {r.get('first_with')}, last without {r.get('last_without')} {r.get('note', '')}", flush=True)
    json.dump(res, open(cpath('wayback/firstseen.json'), 'w'), indent=1)
    return {k: (v.get('first_with'), v.get('last_without'), v.get('note')) for k, v in res.items()}


# ----------------------------------------------------------------------------------------------------------- section 2: delivered side
AQS = 'https://wikimedia.org/api/rest_v1/metrics'
FAMILY_UNIQUES = {'Wikibooks': 'all-wikibooks-projects', 'Wikidata': 'www.wikidata.org', 'Wikimedia Commons': 'commons.wikimedia.org',
                  'Wikinews': 'all-wikinews-projects', 'Wikipedia': 'all-wikipedia-projects', 'Wikiquote': 'all-wikiquote-projects',
                  'Wikisource': 'all-wikisource-projects', 'Wikispecies': 'species.wikimedia.org', 'Wikiversity': 'all-wikiversity-projects',
                  'Wikivoyage': 'all-wikivoyage-projects', 'Wiktionary': 'all-wiktionary-projects'}

def month_start(t=None):
    d = D.datetime.fromtimestamp(t or NOW, D.timezone.utc); return D.date(d.year, d.month, 1)

def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12); return D.date(d.year + y, m + 1, 1)

def sites():
    sm = get_json('https://meta.wikimedia.org/w/api.php?action=sitematrix&format=json&smsiteprop=url|dbname|code|sitename&smlangprop=code|site',
                  's2/sitematrix.json.gz', pace=0.5)
    out = []
    for k, v in sm['sitematrix'].items():
        if k == 'count': continue
        lst = v if k == 'specials' else v.get('site', [])
        for s in lst:
            out.append(dict(dbname=s['dbname'], url=s['url'], code=s.get('code'), closed='closed' in s, private='private' in s, fishbowl='fishbowl' in s))
    return out

def step_s2_aqs():
    ss = sites(); end_m = month_start(); end_s = end_m.strftime('%Y%m%d'); start_s = '20240101'
    wps = [s for s in ss if s['code'] == 'wiki' and s['url'].endswith('.wikipedia.org') and not s['private']]
    open_sites = [s for s in ss if not s['closed'] and not s['private'] and not s['fishbowl']]
    meta = dict(wikipedias=len(wps), wikipedias_open=sum(1 for s in wps if not s['closed']), open_sites=len(open_sites), end=end_s)
    # page views: every Wikipedia edition, human and all agents
    pv = {}
    for s in wps:
        dom = s['url'].replace('https://', ''); row = {}
        for ag in ('user', 'all-agents'):
            d = get_json(f'{AQS}/pageviews/aggregate/{dom}/all-access/{ag}/monthly/{start_s}00/{end_s}00', f's2/pv/{dom}_{ag}.json.gz', pace=0.35)
            row[ag] = {it['timestamp'][:6]: it['views'] for it in (d or {}).get('items', [])}
        pv[s['dbname']] = dict(domain=dom, closed=s['closed'], **row)
    allp = {ag: get_json(f'{AQS}/pageviews/aggregate/all-projects/all-access/{ag}/monthly/{start_s}00/{end_s}00', f's2/pv_allprojects_{ag}.json.gz', pace=0.35)
            for ag in ('user', 'all-agents')}
    # edits, all Wikipedias
    ed = {}
    for et in ('all-editor-types', 'user', 'anonymous', 'group-bot', 'name-bot'):
        for pt in ('all-page-types', 'content'):
            ed[f'{et}|{pt}'] = get_json(f'{AQS}/edits/aggregate/all-wikipedia-projects/{et}/{pt}/monthly/{start_s}/{end_s}', f's2/edits_{et}_{pt}.json.gz', pace=0.35)
    # editors per open wiki (registered, non-bot), 1+ edits and 1..4 edits
    eds = {}
    for i, s in enumerate(open_sites):
        dom = s['url'].replace('https://', ''); row = dict(domain=dom, wikipedia=s['code'] == 'wiki' and dom.endswith('.wikipedia.org'))
        for lvl in ('all-activity-levels', '1..4-edits'):
            d = get_json(f'{AQS}/editors/aggregate/{dom}/user/all-page-types/{lvl}/monthly/{start_s}/{end_s}', f's2/editors/{dom}_{lvl}.json.gz', pace=0.35)
            res = (d or {}).get('items', [{}])[0].get('results', []) if (d or {}).get('items') else []
            row[lvl] = {r['timestamp'][:7]: r['editors'] for r in res}
        eds[s['dbname']] = row
        if i % 100 == 0: print(f'editors {i} of {len(open_sites)}', flush=True)
    # site statistics: every Wikipedia edition (articles), Commons (files)
    st = {}
    for s in wps + [x for x in ss if x['dbname'] == 'commonswiki']:
        d = get_json(f"{s['url']}/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json", f"s2/siteinfo/{s['dbname']}.json.gz", pace=0.3)
        st[s['dbname']] = dict(closed=s['closed'], stats=(d or {}).get('query', {}).get('statistics'))
    # unique devices per project family for the DSA windows
    un = {}
    last_day = (end_m - D.timedelta(days=1)).strftime('%Y%m%d')
    for fam, proj in FAMILY_UNIQUES.items():
        d = get_json(f'{AQS}/unique-devices/{proj}/all-sites/monthly/20220801/{last_day}', f's2/uniques_{proj}.json.gz', pace=0.35)
        un[fam] = {it['timestamp'][:6]: it['devices'] for it in (d or {}).get('items', [])}
    with gzip.open(cpath('s2/delivered.json.gz'), 'wt') as f:
        json.dump(dict(read=iso_utc(), meta=meta, pageviews=pv, allprojects={ag: {it['timestamp'][:6]: it['views'] for it in (v or {}).get('items', [])} for ag, v in allp.items()},
                       edits={k: {r['timestamp'][:7]: r['edits'] for r in (v or {}).get('items', [{}])[0].get('results', [])} if (v or {}).get('items') else {} for k, v in ed.items()},
                       editors=eds, siteinfo=st, uniques=un), f)
    return meta

STATS_PAGE = 'Data:Wikipedia statistics/data.tab'
def stats_revision(ts_iso, name):
    """The revision of Commons Data:Wikipedia statistics/data.tab in force at ts_iso (CC0, posted by a bot from each wiki's site statistics)."""
    url = ('https://commons.wikimedia.org/w/api.php?action=query&prop=revisions&titles=' + urllib.parse.quote(STATS_PAGE) +
           f'&rvlimit=1&rvstart={ts_iso}&rvdir=older&rvprop=timestamp|ids|content&rvslots=main&format=json')
    d = get_json(url, f's2/moments/{name}.json.gz', permanent=True, pace=1.0)
    pg = list(d['query']['pages'].values())[0]; rv = pg['revisions'][0]
    c = json.loads(rv['slots']['main']['*']); fields = [x['name'] for x in c['schema']['fields']]
    return rv, c, {n: fields.index(n) for n in fields}, {r[0]: r for r in c['data']}

def step_s2_moments():
    """Note 2.1 (defined after the data, referee B1): annual report counts read at the end of the report's year and just before the report
    page's first capture, from the statistics table's revision in force then. Today's reading stays the direct site statistics read."""
    ss = sites()
    wp = {s['url'].replace('https://', '').replace('.org', ''): s['closed'] for s in ss if s['code'] == 'wiki' and s['url'].endswith('.wikipedia.org') and not s['private']}
    fs = json.load(open(cpath('wayback/firstseen.json')))
    first = min(v['first_with'] for k, v in fs.items() if k.startswith('ar_') and v.get('first_with'))
    t_first = D.datetime.strptime(first, '%Y%m%d%H%M%S').replace(tzinfo=D.timezone.utc) - D.timedelta(seconds=1)
    dl = json.load(gzip.open(cpath('s2/delivered.json.gz'), 'rt'))
    moments = [('year_end', "at the end of the report's year (30 June 2025)", '2025-06-30T23:59:59Z'),
               ('before_first_capture', f"just before the report page's first capture ({t_first.day} {t_first.strftime('%b %Y')})", t_first.strftime('%Y-%m-%dT%H:%M:%SZ')),
               ('today_table', 'the table at the time of our direct read (a cross-check, not a reading)', dl['read'])]
    out = dict(report_first_capture=first)
    for mid, label, ts in moments:
        rv, c, ix, rows = stats_revision(ts, mid)
        ed = [r for site, r in rows.items() if site in wp]
        out[mid] = dict(label=label, at=ts, revision=rv['revid'], revision_time=rv['timestamp'], description=(c.get('description') or {}).get('en'), licence=c.get('license'),
                        url=f"https://commons.wikimedia.org/w/index.php?title=Data:Wikipedia_statistics/data.tab&oldid={rv['revid']}",
                        A1=sum(r[ix['articles']] for r in ed if not wp[r[0]]), A2=sum(r[ix['articles']] for r in ed),
                        L1=sum(1 for r in ed if not wp[r[0]]), L2=len(ed),
                        C1=rows['commons.wikimedia'][ix['files']] if 'commons.wikimedia' in rows else None,
                        table_total_row=rows['total.wikipedia'][ix['articles']] if 'total.wikipedia' in rows else None)
        print(f"moment {mid}: revision {rv['revid']} {rv['timestamp']}, articles {out[mid]['A2']:,} (open {out[mid]['A1']:,}), editions {out[mid]['L2']} (open {out[mid]['L1']}), Commons files {out[mid]['C1']:,}", flush=True)
    json.dump(out, open(cpath('s2/moments.json'), 'w'), indent=1)
    return {k: dict(A2=v['A2'], C1=v['C1'], revision=v['revision']) for k, v in out.items() if isinstance(v, dict)}

def step_s2_dsa():
    t = get_text('https://foundation.wikimedia.org/w/index.php?title=Legal:Wikimedia_Foundation_European_Union_Compliance/Digital_Services_Act_Userbase_Statistics&action=raw',
                 'stated/dsa_userbase_latest.wikitext.gz', pace=1.0)
    out = dict(read=iso_utc(), url='https://foundation.wikimedia.org/wiki/Legal:EU_DSA_Userbase_Statistics', sha256=sha256(t or ''))
    files = ['File:Wikipedia_-_DSA_transparency_report_2026-02-28.xls', 'File:Wikipedia_-_DSA_transparency_report_template_2026-08-31.xls']
    ii = get_json('https://foundation.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|sha1|timestamp&format=json&titles=' + urllib.parse.quote('|'.join(files)),
                  's2/dsa_imageinfo.json.gz', pace=1.0)
    out['harmonised'] = []
    for pg in (ii or {}).get('query', {}).get('pages', {}).values():
        info = (pg.get('imageinfo') or [{}])[0]; clean = (info.get('url') or '').split('?')[0] or None
        rec = dict(title=pg.get('title'), url=clean, sha1=info.get('sha1'), timestamp=info.get('timestamp'))
        if clean:
            p = cpath('stated/' + clean.rsplit('/', 1)[1])
            if not os.path.exists(p) and not OFFLINE:
                st, b = http(clean, pace=1.0)
                if st == 200:
                    open(p, 'wb').write(b)
            if os.path.exists(p):
                b = open(p, 'rb').read(); rec['sha1_ok'] = hashlib.sha1(b).hexdigest() == info.get('sha1'); rec['file'] = p
        out['harmonised'].append(rec)
    rv = get_json('https://foundation.wikimedia.org/w/api.php?action=query&prop=revisions&revids=546663|546664&rvprop=ids|timestamp|comment|content&rvslots=main&format=json',
                  's2/dsa_revisions_546663_546664.json.gz', permanent=True, pace=1.0)
    out['revisions_read'] = [dict(revid=r['revid'], timestamp=r['timestamp'], comment=r.get('comment')) for pg in ((rv or {}).get('query', {}).get('pages', {}).values()) for r in pg.get('revisions', [])]
    json.dump(out, open(cpath('stated/dsa_read.json'), 'w'), indent=1)
    return dict(userbase_chars=len(t or ''), harmonised=[(r['title'], r.get('sha1_ok')) for r in out['harmonised']])


def parse_userbase(t):
    """The two tables of the DSA userbase page: families x windows, member states x windows."""
    tables = []
    for tb in re.findall(r'\{\|(.*?)\n\|\}', t, re.S):
        rows = [r for r in re.split(r'\n\|-', tb)]
        head = [c.strip() for c in re.findall(r'\n!([^\n]*)', rows[0])]
        body = []
        for r in rows[1:]:
            cells = [c.strip() for c in re.split(r'\n\|', '\n' + r.strip())[1:]]
            if not cells: continue
            name = re.sub(r"<[^>]+>|''+|\[\[|\]\]", '', cells[0]).strip()
            vals = [re.sub(r"'''|<ref.*?(</ref>|/>)", '', c).strip() for c in cells[1:]]
            body.append((name, vals))
        tables.append(dict(head=[h for h in head if h], body=body))
    return tables

MONTHS = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}
def window_months(label):
    ms = re.findall(r'([A-Za-z]{3})[a-z]*\.?\s*(\d{4})', label)
    if len(ms) != 2: return None
    a = D.date(int(ms[0][1]), MONTHS[ms[0][0].lower()], 1); b = D.date(int(ms[1][1]), MONTHS[ms[1][0].lower()], 1)
    out = []; d = a
    while d <= b: out.append(d.strftime('%Y%m')); d = add_months(d, 1)
    return out

EU_CODES = {'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
            'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'EL': 'Greece', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia', 'LT': 'Lithuania',
            'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia', 'SI': 'Slovenia',
            'SP': 'Spain', 'ES': 'Spain', 'SE': 'Sweden'}

def read_harmonised(path):
    try: import xlrd
    except ImportError: return None, 'xlrd not available'
    b = xlrd.open_workbook(path); s = b.sheet_by_name('10_AMAR'); rows = []
    for r in range(1, s.nrows):
        v = s.row_values(r)
        if len(v) >= 7 and str(v[1]).strip() == 'Wikipedia': rows.append(dict(period=str(v[2]).strip(), scope=str(v[5]).strip(), value=float(v[6])))
    return rows, None


# ----------------------------------------------------------------------------------------------------------- section 2: scoring
def band_of(s):
    X = s['X']; w = s['word']
    if w == 'nearly': return dict(lo=0.9 * X, hi=X, lo_open=False, text=f'{0.9 * X:,.0f} to {X:,.0f}')
    if w == 'over': return dict(lo=X, hi=math.inf, lo_open=True, text=f'above {X:,.0f}')
    if w in ('plus', 'counting'): return dict(lo=X, hi=math.inf, lo_open=False, text=f'{X:,.0f} or more')
    h = s['unit'] / 2; return dict(lo=X - h, hi=X + h, lo_open=False, text=f'{X - h:,.0f} to {X + h:,.0f}' if h >= 1 else f'{X - h:,} to {X + h:,}')

def outcome_band(b, dlo, dhi):
    """PLAN Section 2: the stated band relative to the delivered interval."""
    if dlo is None or dhi is None: return K.CANNOT_TELL
    if b['lo'] > dhi or (b['lo_open'] and b['lo'] >= dhi): return K.ABOVE
    if b['hi'] < dlo: return K.BELOW
    inside_lo = (dlo > b['lo']) if b['lo_open'] else (dlo >= b['lo'])
    if inside_lo and dhi <= b['hi']: return K.CONSISTENT
    return K.CANNOT_TELL

def known_good_s2():
    b = dict(lo=13.5, hi=15, lo_open=False); o = dict(lo=67, hi=math.inf, lo_open=True); p = dict(lo=300, hi=math.inf, lo_open=False)
    cases = [(b, 11, 13, K.ABOVE), (b, 16, 20, K.BELOW), (b, 14, 14.5, K.CONSISTENT), (b, 13, 14, K.CANNOT_TELL), (b, 14, 16, K.CANNOT_TELL),
             (o, 68.7, 68.7, K.CONSISTENT), (o, 66, 66, K.ABOVE), (o, 67, 67, K.ABOVE), (o, 66, 68, K.CANNOT_TELL), (p, 300, 300, K.CONSISTENT), (p, 299, 299, K.ABOVE)]
    res = [dict(band=[c[0]['lo'], c[0]['hi']], delivered=[c[1], c[2]], want=c[3], got=outcome_band(c[0], c[1], c[2])) for c in cases]
    for r in res: r['ok'] = r['want'] == r['got']
    nb = band_of(dict(X=15e9, word='nearly')); pb = band_of(dict(X=324, word='plain', unit=1)); vb = band_of(dict(X=250000, word='plain', unit=10000))
    bands_ok = nb['lo'] == 13.5e9 and nb['hi'] == 15e9 and pb['lo'] == 323.5 and pb['hi'] == 324.5 and vb['lo'] == 245000 and vb['hi'] == 255000
    res.append(dict(test='word rules on three figures', ok=bands_ok))
    return all(r['ok'] for r in res), res

def months_in(window, first_seen=None):
    if window == 'latest12':
        e = add_months(month_start(), -1); return [add_months(e, -i).strftime('%Y%m') for i in range(11, -1, -1)]
    if window == 'fy2425':
        return [add_months(D.date(2024, 7, 1), i).strftime('%Y%m') for i in range(12)]
    if window == 'pre_first' and first_seen:
        f = D.date(int(first_seen[:4]), int(first_seen[4:6]), 1); return [add_months(f, -i).strftime('%Y%m') for i in range(12, 0, -1)]
    return []

def series_stats(series, months):
    vals = [series.get(m) for m in months]
    if not months or any(v is None for v in vals): return dict(months=months, missing=[m for m, v in zip(months, vals) if v is None])
    return dict(months=[months[0], months[-1]], lo=min(vals), hi=max(vals), mean=sum(vals) / len(vals), n=len(vals))

def score_s2():
    dl = json.load(gzip.open(cpath('s2/delivered.json.gz'), 'rt'))
    pv, ed = dl['pageviews'], dl['edits']
    allmonths = sorted({m for v in pv.values() for ag in ('user', 'all-agents') for m in v[ag]})
    V = {'V1': {m: sum(v['user'].get(m, 0) for v in pv.values()) for m in allmonths},
         'V2': {m: sum(v['all-agents'].get(m, 0) for v in pv.values()) for m in allmonths},
         'V3': dl['allprojects']['user'], 'V4': dl['allprojects']['all-agents']}
    no_rows = {m: sum(1 for v in pv.values() if m not in v['user']) for m in allmonths}
    def per_min(d):
        return {k.replace('-', ''): v / (calendar.monthrange(int(k[:4]), int(k[5:7]))[1] * 1440) for k, v in d.items()}
    E = {'E1': per_min(ed['all-editor-types|all-page-types']),
         'E2': per_min({k: ed['user|all-page-types'].get(k, 0) + ed['anonymous|all-page-types'].get(k, 0) for k in ed['user|all-page-types']}),
         'E3': per_min(ed['all-editor-types|content']),
         'E4': per_min({k: ed['user|content'].get(k, 0) + ed['anonymous|content'].get(k, 0) for k in ed['user|content']})}
    si = dl['siteinfo']
    arts_open = sum((v['stats'] or {}).get('articles', 0) for k, v in si.items() if k != 'commonswiki' and not v['closed'])
    arts_all = sum((v['stats'] or {}).get('articles', 0) for k, v in si.items() if k != 'commonswiki')
    no_stats = [k for k, v in si.items() if not v['stats']]
    n_open = sum(1 for k, v in si.items() if k != 'commonswiki' and not v['closed']); n_all = sum(1 for k in si if k != 'commonswiki')
    files = (si.get('commonswiki', {}).get('stats') or {}).get('images')
    DEF = {
        'views': [('V1', 'Wikipedia, every edition, human traffic'), ('V2', 'Wikipedia, every edition, all agents'), ('V3', 'All Wikimedia projects, human traffic'), ('V4', 'All Wikimedia projects, all agents')],
        'edits': [('E1', 'All Wikipedias, every editor type including bots, all pages'), ('E2', 'All Wikipedias, registered and anonymous editors without bots, all pages'),
                  ('E3', 'All Wikipedias, every editor type including bots, content pages'), ('E4', 'All Wikipedias, without bots, content pages')],
        'articles': [('A1', 'Sum of article counts, open Wikipedias'), ('A2', 'Sum of article counts, every Wikipedia edition including closed')],
        'languages': [('L1', 'Open Wikipedia editions'), ('L2', 'Every Wikipedia edition including closed')],
        'commons': [('C1', 'Commons file count')]}
    POINT = {'A1': arts_open, 'A2': arts_all, 'L1': n_open, 'L2': n_all, 'C1': files}
    SER = dict(V, **E)
    # volunteers bounds
    eds = dl['editors']
    def vol_bounds(months, wp_only):
        out = {}
        for lvl in ('1+', '5+'):
            lows, highs = [], []
            for m in months:
                mm = f'{m[:4]}-{m[4:]}'; vals = []
                for k, v in eds.items():
                    if wp_only and not v['wikipedia']: continue
                    a = v['all-activity-levels'].get(mm)
                    if a is None: continue
                    vals.append(a if lvl == '1+' else a - v['1..4-edits'].get(mm, 0))
                if vals: lows.append(max(vals)); highs.append(sum(vals))
            out[lvl] = dict(lower_mean=sum(lows) / len(lows) if lows else None, upper_mean=sum(highs) / len(highs) if highs else None,
                            lower_range=[min(lows), max(lows)] if lows else None, upper_range=[min(highs), max(highs)] if highs else None, months=len(lows))
        return out
    wb = json.load(open(cpath('wayback/firstseen.json'))) if os.path.exists(cpath('wayback/firstseen.json')) else {}
    MOM = json.load(open(cpath('s2/moments.json'))) if os.path.exists(cpath('s2/moments.json')) else {}
    VB = {w: dict(all_wikis=vol_bounds(months_in(w), False), wikipedias=vol_bounds(months_in(w), True), months=[months_in(w)[0], months_in(w)[-1]])
          for w in ('latest12', 'fy2425')}
    figs = []
    for s in stated_quotes():
        b = band_of(s); f = dict(id=s['id'], page=s['page'], page_name=s['page_name'], url=s['url'], read=s['read'], quote=s['quote'], found=s['found'], card=s.get('card'),
                                 focus=s.get('focus'), word=s['word'], stated=s['X'], band=[b['lo'], b['hi'] if b['hi'] != math.inf else None], band_text=b['text'],
                                 kind=s['kind'], window=s['window'], wayback=wb.get(s['id'], {}))
        if s['kind'] == 'volunteers':
            w = s['window'] if s['window'] in VB else 'latest12'; own = VB[w][s['scope']]
            f.update(outcome=K.CANNOT_TELL, reason='The Analytics API counts editors per wiki only. It has no count of people deduplicated across wikis.',
                     scope=s['scope'], bounds=dict(all_wikis=VB[w]['all_wikis'], wikipedias=VB[w]['wikipedias'], months=VB[w]['months']),
                     placement=dict(note='defined after the data', one_plus=outcome_band(b, own['1+']['lower_mean'], own['1+']['upper_mean']),
                                    five_plus=outcome_band(b, own['5+']['lower_mean'], own['5+']['upper_mean'])))
            figs.append(f); continue
        defs = []
        if s['window'] == 'moments':
            # note 2.1, defined after the data: the report does not state the moment its counts describe, so three moments are candidates
            for mid in ('year_end', 'before_first_capture', 'today'):
                for did, dname in DEF[s['kind']]:
                    if mid == 'today':
                        v = POINT[did]; lab = 'today'; srcn = 'site statistics read directly'; url = None
                    else:
                        m = MOM.get(mid, {}); v = m.get(did); lab = m.get('label', mid)
                        srcn = f"statistics table revision {m.get('revision')} ({(m.get('revision_time') or '')[:16].replace('T', ' ')} UTC)"; url = m.get('url')
                    st = dict(lo=v, hi=v, mean=v) if v is not None else dict(missing=['value'])
                    o = outcome_band(b, st.get('lo'), st.get('hi'))
                    defs.append(dict(id=f'{did}@{mid}', base=did, moment=mid, moment_label=lab, name=f'{dname}, {lab}', source=srcn, source_url=url,
                                     outcome=o, mean_reading=o, in_outcome=True, **st))
        else:
            for did, dname in DEF[s['kind']]:
                if did in POINT:
                    v = POINT[did]; st = dict(lo=v, hi=v, mean=v) if v is not None else dict(missing=['value'])
                else:
                    st = series_stats(SER[did], months_in(s['window']))
                o = outcome_band(b, st.get('lo'), st.get('hi')); om = outcome_band(b, st.get('mean'), st.get('mean')) if 'mean' in st else K.CANNOT_TELL
                # note 2.4: a figure that names Wikipedia states its scope, so the all-projects candidates are shown for reference only
                inout = not (s.get('stated_scope') == 'Wikipedia' and did in ('V3', 'V4'))
                d = dict(id=did, name=dname, outcome=o, mean_reading=om, in_outcome=inout, **st)
                if s['window'] in ('latest12',) and did in SER and wb.get(s['id'], {}).get('first_with'):
                    d['pre_first_capture'] = series_stats(SER[did], months_in('pre_first', wb[s['id']]['first_with']))
                defs.append(d)
        used = [d for d in defs if d.get('in_outcome', True)]
        outs = {d['outcome'] for d in used}
        f['definitions'] = defs
        f['outcome'] = outs.pop() if len(outs) == 1 else K.CANNOT_TELL
        if len({d['outcome'] for d in used}) > 1:
            f['reason'] = ('The report does not state the moment its counts describe, and the readings at the three moments disagree (defined after the data).'
                           if s['window'] == 'moments' else 'The Foundation does not state the definition, and the candidate definitions disagree.')
            f['straddle'] = K.ABOVE in {d['outcome'] for d in used} and K.BELOW in {d['outcome'] for d in used}
        figs.append(f)
    # DSA
    dsa = dict()
    t = get_text('https://foundation.wikimedia.org/w/index.php?title=Legal:Wikimedia_Foundation_European_Union_Compliance/Digital_Services_Act_Userbase_Statistics&action=raw',
                 'stated/dsa_userbase_latest.wikitext.gz')
    dread = json.load(open(cpath('stated/dsa_read.json')))
    tabs = parse_userbase(t or '')
    fam_tab = next((x for x in tabs if any('Wikipedia' == r[0] for r in x['body'])), None)
    ms_tab = next((x for x in tabs if any('Finland' == r[0] for r in x['body'])), None)
    def num(c):
        c = re.sub(r'[^\d]', '', c); return int(c) if c else None
    cells = []
    for tb, nm in ((fam_tab, 'families'), (ms_tab, 'member states')):
        if not tb: continue
        for name, vals in tb['body']:
            if name.lower().startswith('est.'): continue
            for h, c in zip(tb['head'], vals):
                n = num(c)
                if n is not None: cells.append((nm, name, h, n))
    off = [dict(table=a, row=b, window=c, value=n) for a, b, c, n in cells if n % 1000]
    # PLAN DSA check 1: CONSISTENT when no cell departs; otherwise the count and the cells are printed, with no outcome label
    dsa['rounding'] = dict(statement="These estimates have been rounded to the nearest '000", cells=len(cells), not_whole_thousands=off,
                           outcome=(K.CANNOT_TELL if not cells else (K.CONSISTENT if not off else None)), read=dread['read'], url=dread['url'])
    # harmonised reports
    harm = []
    for h in dread.get('harmonised', []):
        if not h.get('file'): harm.append(dict(title=h['title'], outcome=K.CANNOT_TELL, reason='file not read')); continue
        rows, err = read_harmonised(h['file'])
        if rows is None: harm.append(dict(title=h['title'], outcome=K.CANNOT_TELL, reason=err)); continue
        tot = [r for r in rows if r['scope'] == 'TOTAL']; mem = [r for r in rows if r['scope'] != 'TOTAL']
        period = tot[0]['period'] if tot else None; T = tot[0]['value'] if tot else None; S = sum(r['value'] for r in mem)
        diff = (T - S) if T is not None else None
        o = K.CANNOT_TELL if diff is None else (K.CONSISTENT if abs(diff) <= 13500 else (K.ABOVE if diff > 0 else K.BELOW))
        # cross-filing against the page's member-state column for the same half-year
        col = None
        if ms_tab and period:
            a, z = period.split('/'); want = window_months_from_dates(a, z)
            for i, hh in enumerate(ms_tab['head']):
                if window_months(hh) == want: col = i
        cross = None
        if col is not None:
            page = {name: num(vals[col]) for name, vals in ms_tab['body'] if not name.lower().startswith('est.') and col < len(vals)}
            eq = [r['scope'] for r in mem if page.get(EU_CODES.get(r['scope'])) == int(r['value'])]
            ne = [dict(code=r['scope'], report=int(r['value']), page=page.get(EU_CODES.get(r['scope']))) for r in mem if page.get(EU_CODES.get(r['scope'])) != int(r['value'])]
            cross = dict(window=ms_tab['head'][col], equal=len(eq), differ=ne)
        harm.append(dict(title=h['title'], url=h.get('url'), sha1=h.get('sha1'), period=period, total=T, member_sum=S, member_rows=len(mem), difference=diff,
                         outcome=o, codes_not_iso=[r['scope'] for r in mem if r['scope'] in ('SP', 'EL')], cross_filing=cross))
    dsa['harmonised'] = harm
    # bound: stated EU devices against global unique devices
    un = dl['uniques']; bound = []
    if fam_tab:
        factor = 2.4
        for name, vals in fam_tab['body']:
            if name.lower().startswith('est.') or name not in FAMILY_UNIQUES: continue
            for h, c in zip(fam_tab['head'], vals):
                ms = window_months(h); n = num(c)
                if not ms or n is None: continue
                g = [un.get(name, {}).get(m) for m in ms]
                if any(x is None for x in g):
                    bound.append(dict(family=name, window=h, stated=n, outcome=K.CANNOT_TELL, reason='global unique devices missing for a month of the window')); continue
                gm = sum(g) / len(g); eu = n * factor
                bound.append(dict(family=name, window=h, stated=n, stated_devices=eu, global_devices_mean=gm, implied_eu_share=eu / gm,
                                  outcome=K.ABOVE if eu > gm else K.CONSISTENT))
    dsa['bound'] = bound
    # repeats in consecutive half-years (descriptive)
    reps = []
    if ms_tab:
        for name, vals in ms_tab['body']:
            if name.lower().startswith('est.'): continue
            ns = [num(v) for v in vals]; run = 1
            for i in range(1, len(ns)):
                run = run + 1 if ns[i] is not None and ns[i] == ns[i - 1] else 1
                if run >= 2 and (i == len(ns) - 1 or ns[i + 1] != ns[i]):
                    reps.append(dict(member_state=name, value=ns[i], half_years=run, windows=[ms_tab['head'][i - run + 1], ms_tab['head'][i]]))
    dsa['repeats'] = reps
    dsa['figure_itself'] = dict(outcome=K.CANNOT_TELL, reason='The DSA figures are EU unique devices divided by 2.4. EU-only device counts are not published, so the figures cannot be rebuilt from public data.')
    # descriptive (note 2.10): the page revision that set Finland's January to June 2025 figure, and the page's own note on that column
    fr = None
    p = cpath('s2/dsa_revisions_546663_546664.json.gz')
    if os.path.exists(p):
        revs = {r['revid']: r for pg in json.load(gzip.open(p, 'rt'))['query']['pages'].values() for r in pg['revisions']}
        def fin(rv):
            tb = next((x for x in parse_userbase(rv['slots']['main']['*']) if any('Finland' == r[0] for r in x['body'])), None)
            row = next(v for nm, v in tb['body'] if nm == 'Finland')
            return {h: num(c) for h, c in zip(tb['head'], row)}
        if 546663 in revs and 546664 in revs:
            a, z = fin(revs[546663]), fin(revs[546664])
            note = re.search(r'a\.\s*(Original data for Jan 2025 - June 2025 was updated[^.]*\.)', t or '')
            fr = dict(revid=546664, timestamp=revs[546664]['timestamp'], comment=revs[546664].get('comment'),
                      changes=[dict(window=h, before=a.get(h), after=z.get(h)) for h in z if a.get(h) != z.get(h)],
                      note=re.sub(r'\s+', ' ', note.group(1)) if note else None,
                      diff_url='https://foundation.wikimedia.org/w/index.php?title=Legal%3AEU_DSA_Userbase_Statistics&diff=546664&oldid=546663')
    dsa['finland_revision'] = fr
    dsa['tables'] = dict(families=fam_tab, member_states=ms_tab)
    meta = dict(delivered_read=dl['read'], wikipedias=dl['meta'], months_with_editions_missing_pageviews={m: n for m, n in no_rows.items() if n},
                editions_without_site_statistics=no_stats, articles_open=arts_open, articles_all=arts_all, open_editions=n_open, all_editions=n_all, commons_files=files,
                volunteer_bounds=VB, moments=MOM)
    return figs, dsa, meta

def window_months_from_dates(a, z):
    a = D.date.fromisoformat(a); z = D.date.fromisoformat(z); out = []; d = D.date(a.year, a.month, 1)
    while d <= z: out.append(d.strftime('%Y%m')); d = add_months(d, 1)
    return out


# ----------------------------------------------------------------------------------------------------------- publish
def jsonable(o):
    if isinstance(o, Decimal): return str(o)
    if isinstance(o, set): return sorted(o)
    if isinstance(o, float) and (math.isinf(o) or math.isnan(o)): return None
    raise TypeError(type(o))

def step_s1_score():
    srcs, smeta = load_sources(offline_only=OFFLINE)
    codes = set()
    for g in GROUPS:
        with gzip.open(cpath(f"s1/claims_{g['id']}.json.gz"), 'rt') as f: codes.update(*[rec['iso'] for rec in json.load(f)['items'].values()])
    kg_ok, kg = known_good_s1(srcs, codes)
    sc_ok, sc = known_good_scout(srcs)
    rows, fmeta = score_s1(srcs, smeta); SRCS_REF.update(srcs)
    passed, msg = K.known_good(lambda c: c, kg_ok)
    if not passed:
        for r in rows: r['outcome_before_gate'] = r['outcome']; r['outcome'] = K.CANNOT_TELL
    summ = summarize_s1(rows, fmeta, {k: v for k, v in smeta.items()})
    sens = sensitivity_s1(rows, srcs)
    for gid, v in sens.items():
        if v.get('consistent_top_country'): v['consistent_top_country']['label'] = LABELS.get(v['consistent_top_country']['item'])
        summ[gid]['sensitivity'] = v
    hc = hand_check_s1(rows, srcs)        # first run (query service, uniform draw); kept for the record, note 2.2
    hcp = json.load(open(cpath('s1/handcheck_plan.json'))) if os.path.exists(cpath('s1/handcheck_plan.json')) else None
    s1 = dict(read=iso_utc(), known_good=dict(passed=kg_ok, planted=kg, scout_cross_check=dict(passed=sc_ok, releases=sc), gate=msg),
              hand_check_first_run=hc, hand_check=hcp, groups=summ, source_meta={f'{a}:{b}': v for (a, b), v in smeta.items()})
    with gzip.open(cpath('s1/rows.json.gz'), 'wt') as f: json.dump([{k: v for k, v in r.items() if k not in ('v',)} for r in rows], f, default=jsonable)
    json.dump(s1, open(cpath('s1/s1_summary.json'), 'w'), indent=1, default=jsonable)
    a = summ['ALL']
    print(f"s1: {a['rows']} rows, {a['countries']} countries; bins " + ', '.join(f"{b} {a['bins'][b]['k']}" for b in BINS) +
          f"; known-good {'passed' if kg_ok else 'FAILED'}, scout cross-check {'passed' if sc_ok else 'FAILED'}", flush=True)
    return dict(rows=a['rows'], known_good=kg_ok, scout=sc_ok)

def step_s2_score():
    kg_ok, kg = known_good_s2()
    figs, dsa, meta = score_s2()
    if not kg_ok:
        for f in figs: f['outcome_before_gate'] = f['outcome']; f['outcome'] = K.CANNOT_TELL
    s2 = dict(read=iso_utc(), known_good=dict(passed=kg_ok, tests=kg), figures=figs, dsa=dsa, meta=meta)
    json.dump(s2, open(cpath('s2/s2_summary.json'), 'w'), indent=1, default=jsonable)
    print('s2: ' + '; '.join(f"{f['id']} {f['outcome']}" for f in figs), flush=True)
    return dict(figures=len(figs), known_good=kg_ok)

def step_publish():
    s1 = json.load(open(cpath('s1/s1_summary.json'))); s2 = json.load(open(cpath('s2/s2_summary.json')))
    full = dict(desk='WIKI', division='HERMES', updated=iso_utc(), plan='PLAN.md', section1=s1, section2=s2,
                licences=dict(wikidata='CC0', analytics='CC0', worldbank='CC BY 4.0', uis='CC BY-SA 4.0', foundation_pages='CC BY-SA 4.0'))
    json.dump(full, open(os.path.join(H, 'data', 'wiki.json'), 'w'), indent=1)
    live = slim(s1, s2)
    json.dump(live, open(os.path.join(H, 'data', 'wiki_live.json'), 'w'), separators=(',', ':'))   # 10 Nov 2026 (ship): compact, as it goes to the KV
    summ = dict(updated=live['updated'], section1={g: dict(rows=v['rows'], countries=v['countries'], **{b: v['bins'][b]['k'] for b in BINS},
                                                            **{'size_' + o: v['size'][o]['k'] for o in OUTS}) for g, v in s1['groups'].items()},
                section2={f['id']: f['outcome'] for f in s2['figures']},
                dsa=dict(rounding=s2['dsa']['rounding']['outcome'], harmonised=[h['outcome'] for h in s2['dsa']['harmonised']],
                         bound_above=sum(1 for b in s2['dsa']['bound'] if b['outcome'] == K.ABOVE), bound_cells=len(s2['dsa']['bound'])),
                known_good=dict(s1=s1['known_good']['passed'], s1_scout=s1['known_good']['scout_cross_check']['passed'], s2=s2['known_good']['passed']))
    json.dump(summ, open(os.path.join(H, 'summary_wiki.json'), 'w'), indent=1)
    print('published locally: data/wiki.json, data/wiki_live.json, summary_wiki.json', flush=True)
    return dict(updated=summ['updated'])

def slim(s1, s2):
    def sh(t): return {k: dict(k=v['k'], n=v['n'], share=v['share'], wilson95=v['wilson95'], country95=v['country95']) for k, v in t.items()}
    g1 = {}
    for gid, v in s1['groups'].items():
        g1[gid] = dict(label=v.get('label', 'All groups'), series=v.get('series'), source=v.get('source'), property=v.get('property'),
                       rows=v['rows'], countries=v['countries'], country_years=v['country_years'], years=v['years'], bins=sh(v['bins']), size=sh(v['size']),
                       written_whole=v.get('written_whole'), written_whole_size=v.get('written_whole_size'),
                       on_the_line=v.get('on_the_line') or [],
                       median_abs_gap_not_matching_current=v['median_abs_gap_not_matching_current'], newest_matching_release_by_year=v['newest_matching_release_by_year'],
                       defaults=dict(rows=v['defaults']['rows'], countries=v['defaults']['countries'], bins=sh(v['defaults']['bins']), size=sh(v['defaults']['size'])),
                       notable=v.get('notable', []), set_aside=v.get('frame', {}).get('set_aside'), source_read=v.get('source_read'),
                       post_hoc_alias=v.get('post_hoc_alias'), sensitivity=v.get('sensitivity'), uis_citation=v.get('uis_citation'),
                       wb_secondary_norel=v.get('wb_secondary_norel'),
                       wb_secondary=v.get('wb_secondary'), by_unit=v.get('by_unit'))
    figs = []
    for f in s2['figures']:
        figs.append({k: f.get(k) for k in ('id', 'page_name', 'url', 'read', 'quote', 'found', 'card', 'focus', 'stated', 'word', 'band', 'band_text', 'window', 'outcome',
                                           'reason', 'straddle', 'bounds', 'scope', 'placement', 'wayback')} |
                    dict(definitions=[{k: d.get(k) for k in ('id', 'base', 'name', 'moment', 'moment_label', 'source', 'source_url', 'outcome', 'mean_reading', 'in_outcome',
                                                             'lo', 'hi', 'mean', 'months', 'pre_first_capture')} for d in f.get('definitions', [])]))
    nc = json.load(open(cpath('s1/notable_check.json'))) if os.path.exists(cpath('s1/notable_check.json')) else []
    ncm = {(x['group'], x['statement']): x['all_agree'] for x in nc}
    for gid, v in g1.items():
        for r in v['notable']: r['reread_agrees'] = ncm.get((gid, r['statements'][0]))
    d = s2['dsa']
    hcp = (s1.get('hand_check') or {}).get('rows') or []
    # 10 Nov 2026 (ship): the stamp is the time the reading was scored (the later of the two sections), written YYYY-MM-DD HH:MM UTC so the
    # drift seat and the LIVE tags can read its age. The earlier form, with the year after the month, did not parse there.
    rd = max(s1.get('read') or '', s2.get('read') or '') or iso_utc()
    return dict(desk='WIKI', updated=rd[:10] + ' ' + rd[11:16] + ' UTC', section1=g1, section2=figs,
                volunteer_bounds=s2['meta'].get('volunteer_bounds'), moments=s2['meta'].get('moments'),
                dsa=dict(rounding=d['rounding'], harmonised=d['harmonised'], bound=d['bound'], repeats=d['repeats'], figure_itself=d['figure_itself'],
                         finland_revision=d.get('finland_revision')),
                hand_check_plan=dict(draw=(s1.get('hand_check') or {}).get('draw'), rows=[{k: h[k] for k in ('group', 'iso', 'year', 'bin', 'checks', 'all_agree')} for h in hcp]),
                known_good=dict(s1=s1['known_good']['passed'], s1_scout=s1['known_good']['scout_cross_check']['passed'], s2=s2['known_good']['passed']),
                hand_check_first_run=[{k: h[k] for k in ('group', 'iso', 'year', 'wikidata_agrees', 'source_agrees')} for h in s1.get('hand_check_first_run', [])])


# ----------------------------------------------------------------------------------------------------------- main
STEPS_S1 = ['s1_frame', 's1_wb', 's1_uis', 's1_score', 's1_handcheck', 's1_notable', 's1_score']

def main():
    global OFFLINE
    ap = argparse.ArgumentParser(); ap.add_argument('--steps', default='all'); ap.add_argument('--offline', action='store_true')
    ap.add_argument('--publish', action='store_true', help='after the steps, put data/wiki_live.json in the site KV (key wiki_live)')
    ap.add_argument('--due-days', type=float, default=0, help='with --publish: start only when the reading in data/wiki_live.json is at least this many days old')
    a = ap.parse_args(); OFFLINE = a.offline
    if a.publish:   # 10 Nov 2026 (ship): the tick bus calls this every 36 ticks; a run starts once the last reading is 7 days old, and never beside another run
        if a.due_days:
            try: last = D.datetime.strptime(json.load(open(os.path.join(H, 'data', 'wiki_live.json')))['updated'], '%Y-%m-%d %H:%M UTC').replace(tzinfo=D.timezone.utc).timestamp()
            except Exception: last = 0
            if time.time() - last < a.due_days * 86400: return
        import fcntl
        lk = open(os.path.join(H, 'data', 'run.lock'), 'w')
        try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError: print('wiki: a run is already going, this one did not start', flush=True); return
    steps = (STEPS_S1 + STEPS_S2 + ['publish']) if a.steps == 'all' else a.steps.split(',')
    state_p = os.path.join(H, 'data', 'state.json')
    for s in steps:
        t0 = time.time(); print(f'== {s}', flush=True)
        r = STEP_FN[s]()
        state = json.load(open(state_p)) if os.path.exists(state_p) else {}   # re-read before writing: steps may run in parallel
        if r is not None: state[s] = r
        state.setdefault('_ran', {})[s] = dict(at=iso_utc(), secs=round(time.time() - t0, 1), offline=OFFLINE)
        json.dump(state, open(state_p, 'w'), indent=1, default=str)
    if a.publish:
        if 'publish' not in steps: print('wiki: --publish needs the publish step, nothing put in the KV', flush=True); return
        import subprocess
        env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
        p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'wiki_live', '--path', os.path.join(H, 'data', 'wiki_live.json'),
                            '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                           cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
        print('wiki: ' + json.load(open(os.path.join(H, 'data', 'wiki_live.json')))['updated'] + (' published' if p.returncode == 0 else ' publish FAILED'), flush=True)

STEPS_S2 = ['s2_stated', 's2_wayback', 's2_aqs', 's2_moments', 's2_dsa', 's2_score']
STEP_FN = {'s1_frame': step_s1_frame, 's1_wb': step_s1_wb, 's1_uis': step_s1_uis, 's1_score': step_s1_score, 's1_notable': step_s1_notable, 's1_handcheck': step_s1_handcheck,
           's2_moments': step_s2_moments,
           's2_stated': step_s2_stated, 's2_wayback': step_s2_wayback, 's2_aqs': step_s2_aqs, 's2_dsa': step_s2_dsa, 's2_score': step_s2_score,
           'publish': step_publish}

if __name__ == '__main__':
    main()
