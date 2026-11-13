#!/usr/bin/env python3
"""Referee's independent recount of WIKI Section 1 from data/raw (own code; does not import wiki_tick.py).
Usage: python3 -I recount.py <wiki_index_dir> <out_dir>"""
import sys, os, gzip, json, re, collections as C
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse, unquote

ROOT = sys.argv[1] if len(sys.argv) > 2 else "/Users/heuremen/bones-forge/wiki_index"; OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
RAW = os.path.join(ROOT, 'data', 'raw', 's1')
G = {  # group: (property, source, series, allowed units)
    'WB-POP': ('P1082', 'WB', 'SP.POP.TOTL', {'1', 'Q199'}),
    'WB-GDP': ('P2131', 'WB', 'NY.GDP.MKTP.CD', {'1', 'Q199', 'Q4917'}),
    'WB-GINI': ('P1125', 'WB', 'SI.POV.GINI', {'1', 'Q199'}),
    'WB-UNEMP': ('P1198', 'WB', 'SL.UEM.TOTL.ZS', {'1', 'Q199', 'Q11229'}),
    'UIS-LE': ('P2250', 'UIS', 'SP.DYN.LE00.IN', {'Q577', 'Q1092296'}),
    'UIS-TFR': ('P4841', 'UIS', 'SP.DYN.TFRT.IN', {'1', 'Q199'}),
}
LEGACY = {'ROM': 'ROU', 'ZAR': 'COD', 'TMP': 'TLS', 'ADO': 'AND', 'IMY': 'IMN', 'KSV': 'XKX', 'WBG': 'PSE'}
CHANGE = {'P21', 'P518', 'P642', 'P1013', 'P1001'}

def jl(p):
    with gzip.open(p, 'rt') as f: return json.load(f)

# ---------------- sources
def wb_tables(code):
    vers = jl(os.path.join(RAW, 'wb', 'versions.json.gz'))['source'][0]['concept'][0]['variable']
    older = []
    legacy_seen = C.Counter()
    for v in vers:
        p = os.path.join(RAW, 'wb', code, f"v{v['id']}.json.gz")
        if not os.path.exists(p): older.append((v['id'], v['value'], None)); continue
        d = jl(p)
        if not isinstance(d, dict) or 'source' not in d: older.append((v['id'], v['value'], None)); continue
        t = {}
        for r in d['source'].get('data') or []:
            if r.get('value') is None: continue
            var = {x['concept']: x['id'] for x in r['variable']}
            c = var.get('Country'); y = var.get('Time', '')
            if not y.startswith('YR'): continue
            if c in LEGACY: legacy_seen[c] += 1
            t[(LEGACY.get(c, c), int(y[2:]))] = Decimal(repr(r['value'])) if isinstance(r['value'], float) else Decimal(str(r['value']))
        older.append((v['id'], v['value'], t if t else None))
    cur = {}; page = 1
    while True:
        p = os.path.join(RAW, 'wb', code, f'current_p{page}.json.gz')
        d = jl(p); meta = d[0]
        for r in d[1] or []:
            if r.get('value') is None or not r.get('countryiso3code'): continue
            cur[(r['countryiso3code'], int(r['date']))] = Decimal(repr(r['value'])) if isinstance(r['value'], float) else Decimal(str(r['value']))
        if int(meta.get('pages') or 1) <= page: break
        page += 1
    return cur, older, legacy_seen, meta

def wb_codes_in_archive(code):
    vers = jl(os.path.join(RAW, 'wb', 'versions.json.gz'))['source'][0]['concept'][0]['variable']
    codes = C.Counter()
    for v in vers:
        p = os.path.join(RAW, 'wb', code, f"v{v['id']}.json.gz")
        if not os.path.exists(p): continue
        d = jl(p)
        if not isinstance(d, dict) or 'source' not in d: continue
        for r in d['source'].get('data') or []:
            if r.get('value') is None: continue
            var = {x['concept']: x['id'] for x in r['variable']}
            codes[var.get('Country')] += 1
    return codes

def uis_tables(code):
    vs = jl(os.path.join(RAW, 'uis', 'versions.json.gz'))
    dflt = jl(os.path.join(RAW, 'uis', 'version_default.json.gz'))['version']
    vs = sorted(((x['version'], x['publicationDate'][:10]) for x in vs), key=lambda x: x[1])
    tabs = {}
    for v, pub in vs:
        d = jl(os.path.join(RAW, 'uis', code, f'{v}.json.gz'))
        tabs[v] = {(r['geoUnit'], int(r['year'])): Decimal(str(r['value'])) for r in d['records'] if r.get('value') is not None}
    older = [(v, f'UIS {v} ({pub})', tabs[v]) for v, pub in vs if v != dflt]
    return tabs[dflt], older, dflt, vs, tabs

# ---------------- precision and matching (plan text)
def unit_of(amount):
    a = amount.lstrip('+-')
    if '.' in a:
        return Decimal(1).scaleb(-len(a.split('.')[1]))
    a = a.lstrip('0')
    if not a: return Decimal(1)
    s = len(a.rstrip('0')); k = len(a) - s
    return Decimal(1).scaleb(k if s >= 3 else max(0, k - (3 - s)))

def unit_written(amount):
    """Alternative: the last written significant digit, no three-digit floor."""
    a = amount.lstrip('+-')
    if '.' in a: return Decimal(1).scaleb(-len(a.split('.')[1]))
    a = a.lstrip('0')
    if not a: return Decimal(1)
    s = len(a.rstrip('0')); k = len(a) - s
    return Decimal(1).scaleb(k)

F32 = Decimal(2) ** -24
def match(v, u, r):
    return abs(v - r) <= u / 2 + abs(r) * F32 + Decimal('1e-9')

def match_strict(v, u, r):   # no single-precision allowance
    return abs(v - r) <= u / 2 + Decimal('1e-9')

def bin_of(v, u, iso, year, cur, older, m=match):
    c = None
    for i in iso:
        if (i, year) in cur: c = cur[(i, year)]; break
    seen = c is not None
    if c is not None and m(v, u, c): return 'MATCHES_CURRENT', None, c
    hits = []
    for rid, lab, t in older:
        if not t: continue
        r = None
        for i in iso:
            if (i, year) in t: r = t[(i, year)]; break
        if r is None: continue
        seen = True
        if m(v, u, r): hits.append((rid, lab))
    if hits: return 'MATCHES_AN_OLDER_RELEASE', hits, c
    if seen: return 'MATCHES_NO_RELEASE_READ', None, c
    return 'SOURCE_UNREADABLE', None, c

def size_of(v, u, c):
    if c is None: return 'CANNOT_TELL', None, 'no current value'
    if c == 0: return 'CANNOT_TELL', None, 'current zero'
    v = float(v); u = float(u); c = float(c)
    g = (v - c) / c; a = (v - u / 2 - c) / c; b = (v + u / 2 - c) / c
    lo, hi = min(a, b) - 2 ** -24, max(a, b) + 2 ** -24
    if lo > 0.01: return 'ABOVE', g, None
    if hi < -0.01: return 'BELOW', g, None
    if lo >= -0.01 and hi <= 0.01: return 'CONSISTENT', g, None
    return 'CANNOT_TELL', g, 'crosses'

# ---------------- frame
def frame_refs(claim, src):
    out = []
    for r in claim.get('references') or []:
        sn = r.get('snaks', {})
        ids = [s['datavalue']['value'].get('id') for s in sn.get('P248', []) if s.get('snaktype') == 'value']
        urls = [s['datavalue']['value'] for s in sn.get('P854', []) if s.get('snaktype') == 'value']
        if src == 'WB':
            hit = 'Q21540096' in ids or any(('worldbank.org' in u.lower()) or ('banquemondiale.org' in u.lower()) for u in urls)
        else:
            hit = 'Q3152127' in ids or any('uis.unesco.org' in u.lower() for u in urls)
        if hit: out.append(dict(ids=ids, urls=urls, retrieved=[s['datavalue']['value']['time'] for s in sn.get('P813', []) if s.get('snaktype') == 'value'], snaks=sorted(sn)))
    return out

def url_codes(u, src):
    if src == 'WB':
        return {m.upper() for m in re.findall(r'(?:indicator|indicateur)/([A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+)', u)}
    return {m.upper().rstrip('.') for m in re.findall(r'(SP\.[A-Za-z0-9.]+?)(?:&|%26|$)', unquote(u))}

def rows_of(gid):
    prop, src, series, units = G[gid]
    d = os.path.join(RAW, 'claims', gid)
    rows = {}; aside = C.Counter(); nst = 0; bounds = C.Counter()
    for f in sorted(os.listdir(d)):
        it = f.split('.')[0]
        raw = jl(os.path.join(d, f)); cl = raw['claims'].get(prop, [])
        isos = None
        has_pref = any(c.get('rank') == 'preferred' for c in cl)
        for c in cl:
            fr = frame_refs(c, src)
            if not fr: continue
            nst += 1
            if c.get('rank') == 'deprecated': aside['deprecated'] += 1; continue
            ms = c['mainsnak']
            if ms.get('snaktype') != 'value': aside['novalue'] += 1; continue
            codes = set()
            for x in fr:
                for u in x['urls']: codes |= url_codes(u, src)
            if codes and series not in codes: aside['other series'] += 1; continue
            q = c.get('qualifiers') or {}
            if CHANGE & set(q): aside['changing qualifier'] += 1; continue
            dv = ms['datavalue']['value']; unit = dv.get('unit', '1').rsplit('/', 1)[-1]
            if unit not in units: aside['unit'] += 1; continue
            ts = [x['datavalue']['value'] for x in q.get('P585', []) if x.get('snaktype') == 'value']
            if not ts: aside['no pit'] += 1; continue
            if len(ts) > 1: aside['multi pit'] += 1; continue
            t = ts[0]
            if t['precision'] < 9: aside['coarse pit'] += 1; continue
            y = int(t['time'][1:5]) if t['time'].startswith('+') else None
            if y is None: aside['bce'] += 1; continue
            amt = dv['amount']
            v = Decimal(amt.lstrip('+'))
            u = unit_of(amt)
            if 'upperBound' in dv: bounds['with bounds'] += 1
            default = c.get('rank') == 'preferred' or (c.get('rank') == 'normal' and not has_pref)
            key = (it, y, v)
            r = rows.get(key)
            if r is None:
                r = rows[key] = dict(group=gid, item=it, year=y, v=v, value=amt.lstrip('+'), u=u, uw=unit_written(amt), unit=unit, statements=[], default=False,
                                     ubound=None, lbound=None, urls=set(), stated_in=False, retrieved=set(), refsnaks=set())
            elif u < r['u']:
                r['u'] = u; r['value'] = amt.lstrip('+'); r['uw'] = unit_written(amt)
            if 'upperBound' in dv:
                r['ubound'] = Decimal(dv['upperBound']); r['lbound'] = Decimal(dv['lowerBound'])
            r['statements'].append(c['id']); r['default'] |= default
            for x in fr:
                r['urls'].update(x['urls']); r['retrieved'].update(x['retrieved'])
                r['stated_in'] |= ('Q21540096' in x['ids']) if src == 'WB' else ('Q3152127' in x['ids'])
                r['refsnaks'].update(x['snaks'])
    return list(rows.values()), aside, nst, bounds

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    iso_of = {}
    for gid in G:
        comb = jl(os.path.join(RAW, f'claims_{gid}.json.gz'))
        for it, rec in comb['items'].items(): iso_of[it] = rec['iso']
    srcs = {}
    for gid, (prop, src, series, units) in G.items():
        if src == 'WB':
            cur, older, leg, meta = wb_tables(series); srcs[gid] = (cur, older)
            print(gid, 'WB current values', len(cur), 'lastupdated', meta.get('lastupdated'), 'releases carrying', sum(1 for _, _, t in older if t), 'legacy codes seen', dict(leg))
        else:
            cur, older, dflt, vs, tabs = uis_tables(series); srcs[gid] = (cur, older)
            print(gid, 'UIS default', dflt, 'versions', len(vs), 'values in default', len(cur))
    allrows = []
    for gid in G:
        rows, aside, nst, bounds = rows_of(gid)
        cur, older = srcs[gid]
        for r in rows:
            r['iso'] = iso_of[r['item']]
            b, hits, c = bin_of(r['v'], r['u'], r['iso'], r['year'], cur, older)
            r['bin'] = b; r['hits'] = [h[1] for h in hits] if hits else None; r['current'] = c
            o, g, why = size_of(r['v'], r['u'], c); r['outcome'] = o; r['gap'] = g; r['why'] = why
        cnt = C.Counter(r['bin'] for r in rows); so = C.Counter(r['outcome'] for r in rows)
        print(f"{gid}: statements {nst} rows {len(rows)} items {len({r['item'] for r in rows})} aside {dict(aside)} bounds {dict(bounds)}")
        print('   bins', dict(cnt)); print('   size', dict(so))
        dr = [r for r in rows if r['default']]
        print('   defaults', len(dr), dict(C.Counter(r['bin'] for r in dr)))
        allrows += rows
    print('ALL rows', len(allrows), dict(C.Counter(r['bin'] for r in allrows)), dict(C.Counter(r['outcome'] for r in allrows)))
    def js(o):
        if isinstance(o, Decimal): return str(o)
        if isinstance(o, set): return sorted(o)
        raise TypeError(type(o))
    with gzip.open(os.path.join(OUT, 'ref_rows.json.gz'), 'wt') as f: json.dump(allrows, f, default=js)
