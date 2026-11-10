"""brands.py -- brand pages for indahl.ai (10 Nov 2026). One page per organisation our desks measure, at /brand/<slug>, and an index at /brand.

Called by build_site.py with one hook (add_pages). Also a gate: python3 brands.py --gate.

  Rows   only rows the desks already publish: each desk's live feed (snapshotted to brands/feeds/ at build), the SOCIAL section summaries,
         the MODEL claims file and the ledger. No new readings, no adjectives, no cause. The outcome is the desk's own word.
  Names  brands/entities.json maps each name exactly as a desk shows it to one page, with how the tie was decided. Distinct legal entities
         are merged only where the page note says so. Individuals never get a page. A name not in the map stays on its desk only.
  Trace  every cell is a template plus references into a snapshot or a ledger row. The literal text of a template holds no digit, so every
         number on a brand page comes from a reference. The gate re-reads every reference, re-renders every cell, and checks each built page
         and CSV holds exactly those cells.
Python 3.9+."""
import os, re, json, html, csv, io, sys, datetime as D, urllib.request, concurrent.futures as CF

HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
BR = os.path.join(B, 'brands'); FEEDS = os.path.join(BR, 'feeds'); ENT = os.path.join(BR, 'entities.json'); ROWS = os.path.join(BR, 'rows.json')
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public'); CSVDIR = os.path.join(PUB, 'brand')
LEDGER = os.path.join(B, 'ledger', 'ledger.jsonl'); SITE = 'https://indahl.ai'
E = html.escape

# key: (source, desk name, desk page). A url source is fetched at build and kept in brands/feeds/<key>.json, a file source is copied there.
SRC = {
    'uptime': ('url:/uptime/live.json', 'UPTIME', '/uptime'), 'time': ('url:/time/live.json', 'TIME', '/time'), 'cada': ('url:/cada/live.json', 'CADA', '/cada'),
    'support': ('url:/support/live.json', 'SUPPORT', '/support'), 'change': ('url:/change/live.json', 'CHANGE', '/change'),
    'model_live': ('url:/hermes/model/live.json', 'MODEL', '/hermes/model'), 'model': ('file:mlperf_index/sad_claims.json', 'MODEL', '/hermes/model'),
    'qia': ('url:/qia/cal.json', 'QIA', '/qia'), 'forecast': ('url:/forecast/live.json', 'FORECAST', '/forecast'), 'water': ('url:/water/live.json', 'WATER', '/water'),
    'fedsep': ('url:/fedsep/live.json', 'FEDSEP', '/fedsep'), 'revise': ('url:/revise/live.json', 'REVISE', '/revise'), 'cadence': ('url:/cadence/live.json', 'CADENCE', '/cadence'),
    'trials': ('url:/trials/live.json', 'TRIALS', '/trials'), 'airline': ('url:/airline/live.json', 'AIRLINE', '/airline'), 'airq': ('url:/airq/live.json', 'AIRQ', '/airq'),
    'ailuminate': ('url:/ailuminate/live.json', 'AILUMINATE', '/ailuminate'), 'secrecords': ('url:/secrecords/live.json', 'SECRECORDS', '/secrecords'),
    'hfsize': ('url:/hfsize/live.json', 'HFSIZE', '/hfsize'), 'hflicense': ('url:/hflicense/live.json', 'HFLICENSE', '/hflicense'),
    'pkglicense': ('url:/pkglicense/live.json', 'PKGLICENSE', '/pkglicense'), 'wiki': ('url:/wiki/live.json', 'WIKI', '/wiki'), 'credit': ('file:credit_index/data/credit_live.json', 'CREDIT', '/credit'),
    'social_dsa': ('file:cloudflare-workers/heuremen-door/public/social/dsa.json', 'SOCIAL', '/social#social-dsa'),
    'social_tiktok': ('file:social_index/tiktok/summary_tiktok.json', 'SOCIAL', '/social#social-tiktok'),
    'social_bluesky': ('file:social_index/bluesky/summary_bluesky.json', 'SOCIAL', '/social#social-bluesky'),
    'social_adspend': ('ledger', 'SOCIAL', '/social#adspend'),
}
# Labels for feed keys that are codes. A label is used only when its key is in the snapshot, and each digit in a label is a digit of its key.
LBL = {'now_vs_2025': 'now against 2025', 'y2025_vs_2019': '2025 against 2019', 'p10': 'readout P(1|0)', 'p01': 'readout P(0|1)', 't1': 'T1',
       '0': 'at first sight', '3600': 'after one hour', '21600': 'after six hours', '86400': 'after a day'}
ROLE = {'statement': 'Its statement', 'service': 'Its service, measured', 'record': 'Its record, the yardstick', 'named': 'Named in the row'}


# ---------------------------------------------------------------- snapshots and references
def refresh(keys=None):
    """Fetch every url feed (cache-busting) and copy every file source into brands/feeds/. A failed fetch keeps the last snapshot."""
    os.makedirs(FEEDS, exist_ok=True); keys = keys or list(SRC); out = {}
    def one(k):
        s = SRC[k][0]
        if s == 'ledger': return k, 'ledger'
        try:
            if s.startswith('url:'):
                req = urllib.request.Request(SITE + s[4:] + '?b=' + D.datetime.now(D.timezone.utc).strftime('%Y%m%d%H%M%S'), headers={'User-Agent': 'heuremen-brands/1'})
                d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode('utf-8'))
            else: d = json.load(open(os.path.join(B, s[5:])))
            if not isinstance(d, dict) or not d: raise ValueError('empty')
            json.dump(d, open(os.path.join(FEEDS, k + '.json'), 'w'), ensure_ascii=False); return k, 'fresh'
        except Exception as e:
            return k, ('kept: %s' % e) if os.path.exists(os.path.join(FEEDS, k + '.json')) else ('MISSING: %s' % e)
    with CF.ThreadPoolExecutor(8) as ex:
        for k, st in ex.map(one, keys): out[k] = st
    return out


_SNAP = {}; _LED = None
def snap(k):
    if k not in _SNAP:
        p = os.path.join(FEEDS, k + '.json'); _SNAP[k] = json.load(open(p)) if os.path.exists(p) else None
    return _SNAP[k]

def ledger():
    global _LED
    if _LED is None:
        _LED = {}
        for l in open(LEDGER):
            r = json.loads(l); _LED[r['id']] = r
    return _LED

class Miss(Exception): pass
SKIP = {}

def resolve(ref):
    """('f', key, *path) into a snapshot, ('l', ledger id, field) into a live ledger row."""
    if ref[0] == 'f':
        o = snap(ref[1])
        if o is None: raise Miss('no snapshot %s' % ref[1])
        for p in ref[2:]:
            try: o = o[p]
            except (KeyError, IndexError, TypeError): raise Miss('%s: no %r' % (ref[1], p))
        return o
    if ref[0] in ('k', 'kname', 'lbl'):
        o = resolve(('f', ref[1]) + tuple(ref[2:-1]))
        if not isinstance(o, dict) or ref[-1] not in o: raise Miss('%s: no key %r' % (ref[1], ref[-1]))
        if ref[0] == 'k': return ref[-1]
        if ref[0] == 'kname': return ref[-1].rsplit('|', 1)[0]
        return LBL[ref[-1]]
    if ref[0] == 'lat':
        r = ledger().get(ref[1])
        if not r or r.get('status') != 'live': raise Miss('ledger row %s not live' % ref[1])
        return r['history'][-1]['at']
    if ref[0] == 'l':
        r = ledger().get(ref[1])
        if not r or r.get('status') != 'live': raise Miss('ledger row %s not live' % ref[1])
        return r.get(ref[2])
    raise Miss('bad ref %r' % (ref,))


def _num(v):
    if isinstance(v, bool): return str(v)
    if isinstance(v, int): return f'{v:,}'
    if isinstance(v, float):
        if v.is_integer() and abs(v) >= 1000: return f'{int(v):,}'
        return repr(v)
    return str(v)

FMT = {
    '': lambda v: 'none' if v is None else _num(v),
    'pct': lambda v: 'none' if v is None else ('%.1f%%' % (float(v) * 100)),          # a share as the desk gives it, times 100, one decimal
    'out': lambda v: 'none' if v in (None, '') else str(v).replace('_', ' '),         # an outcome word exactly as the desk gives it, underscore as a space
    'q': lambda v: '' if v is None else str(v),                                        # quoted text as the desk gives it
    'ind': lambda v: 'operational' if v == 'none' else str(v or ''),                   # a status page indicator as the UPTIME desk prints it
}
_PH = re.compile(r'\{(\d+)(?::(\w+))?\}')

def render(cell):
    t, refs = cell
    vals = [resolve(r) for r in refs]
    return _PH.sub(lambda m: FMT[m.group(2) or ''](vals[int(m.group(1))]), t)

def literal(cell): return _PH.sub('', cell[0])


# ---------------------------------------------------------------- rows
def C(t, *refs): return (t, list(refs))
NONE = ('', [])

def R(key, raws, question, item, stated=NONE, delivered=NONE, interval=NONE, outcome=NONE, note=NONE, read=NONE, link=None, receipt=None):
    return {'key': key, 'raws': raws, 'question': C(question), 'item': item, 'stated': stated, 'delivered': delivered, 'interval': interval,
            'outcome': outcome, 'note': note, 'read': read, 'link': link or SRC[key][2], 'receipt': receipt}

def _upd(k):
    d = snap(k) or {}
    for f in ('updated', 'read', 'updated_utc', 'built'):
        if d.get(f): return C('{0}', ('f', k, f))
    return NONE

def _interval(k, path, lo='share_lo', hi='share_hi', pct=True):
    sp = ':pct' if pct else ''
    return C('{0%s} to {1%s}' % (sp, sp), ('f', k, *path, lo), ('f', k, *path, hi))


def ex_uptime():
    k = 'uptime'; d = snap(k); rd = _upd(k); out = []
    for i, v in enumerate(d.get('vendors', [])):
        p = ('f', k, 'vendors', i)
        out.append(R(k, [(v['vendor'], 'statement')], "Does a vendor's status page agree with independent probes?", C('{0} status page against our probes', p + ('vendor',)),
                     C('page says now: {0:ind}', p + ('indicator_now',)),
                     C('page said operational and both seats failed in {0} of {1} rounds. Page said trouble and both seats failed in {2}. One seat failed in {3}', p + ('disagree',), p + ('rounds',), p + ('confirm',), p + ('blips',)),
                     C('expected from the floor: {0}', p + ('expected_from_floor',)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_time():
    k = 'time'; d = snap(k); rd = _upd(k); out = []
    for i, s in enumerate(d.get('servers', [])):
        p = ('f', k, 'servers', i)
        has = s.get('stated_bound_ms') is not None
        out.append(R(k, [(s['server'], 'statement')], 'Does a public time server stay inside its own stated error bound?', C('{0}', p + ('server',)),
                     C('stated bound {0} ms', p + ('stated_bound_ms',)) if has else NONE,
                     C('offset {0} ms, path half-delay {1} ms', p + ('offset_ms',), p + ('half_delay_ms',)) if s.get('offset_ms') is not None else NONE,
                     NONE, C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_cada():
    k = 'cada'; d = snap(k); rd = _upd(k); out = []
    for i, r in enumerate(d.get('resolvers', [])):
        for cp in ('0', '3600', '21600', '86400'):
            c = r.get('checkpoints', {}).get(cp)
            if not c or not c.get('n'): continue
            p = ('f', k, 'resolvers', i, 'checkpoints', cp)
            out.append(R(k, [(r['resolver'], 'service')], 'Does a public DNS filter block fresh malware and phishing domains, and how fast?',
                         C('{0}, {1}', ('f', k, 'resolvers', i, 'resolver'), ('lbl', k, 'resolvers', i, 'checkpoints', cp)), NONE,
                         C('refused {0} of {1} live listed domains, {2}%', p + ('k',), p + ('n',), p + ('wilson', 0)),
                         C('{0}% to {1}%', p + ('wilson', 1), p + ('wilson', 2)), C('this desk gives no outcome'), read=rd))
    return out

def ex_support():
    k = 'support'; d = snap(k); rd = _upd(k); out = []
    for prod in d.get('by_product', {}):
        p = ('f', k, 'by_product', prod)
        out.append(R(k, [(prod, 'statement')], 'Is a cycle that is stated as supported still being released?', C('{0}', ('k', k, 'by_product', prod)),
                     C('stated as supported: {0} cycles', p + ('tested',)), C('no release in more than a year: {0} of them', p + ('unreleased',)),
                     _interval(k, ('by_product', prod)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_change():
    k = 'change'; d = snap(k); rd = _upd(k); out = []
    for i, u in enumerate(d.get('upcoming', [])):
        p = ('f', k, 'upcoming', i)
        out.append(R(k, [(u['vendor'], 'statement')], 'When a vendor says something ends on a date, does the date hold?', C('{0}', p + ('item',)),
                     C('shutdown date stated: {0}', p + ('shutdown',)), C('{0} days left at the read', p + ('days_left',)), NONE,
                     C('not passed yet, so not in the test'), read=rd))
    for i, c in enumerate(d.get('change_list', [])):
        p = ('f', k, 'change_list', i)
        out.append(R(k, [(c['vendor'], 'statement')], 'When a vendor says something ends on a date, does the date hold?', C('{0}', p + ('item',)),
                     C('was: {0:q}', p + ('was',)) if c.get('was') else NONE, C('now: {0:q}', p + ('now',)) if c.get('now') else C('removed from the page') if c.get('kind') == 'REMOVED' else NONE,
                     NONE, C('change logged: {0:out}', p + ('kind',)), C('{0:q}', p + ('note',)) if c.get('note') else NONE, read=C('{0}', p + ('date',))))
    for v in d.get('notice', {}):
        p = ('f', k, 'notice', v)
        out.append(R(k, [(v, 'statement')], 'When a vendor says something ends on a date, does the date hold?', C('{0}, notice from deprecation date to shutdown date', ('k', k, 'notice', v)),
                     NONE, C('median {0} days, shortest {1}, under thirty days: {2} of {3}', p + ('median',), p + ('shortest',), p + ('under30',), p + ('n',)), NONE, C('this table gives no outcome'), read=rd))
    for v in d.get('lifespan', {}):
        p = ('f', k, 'lifespan', v)
        nm = v.split(',')[0]
        out.append(R(k, [(nm, 'statement')], 'When a vendor says something ends on a date, does the date hold?', C('{0}, lifespan from release to shutdown', ('k', k, 'lifespan', v)),
                     NONE, C('median {0} days, shortest {1}, under six months: {2} of {3}', p + ('median',), p + ('shortest',), p + ('under180',), p + ('n',)), NONE, C('this table gives no outcome'), read=rd))
    return out

def ex_model():
    k = 'model'; d = snap(k); out = []; L = ledger()
    by = {}
    for lid, r in L.items():
        if lid.startswith('sad.') and r.get('status') == 'live':
            m = re.search(r' statement ([A-Z0-9]+) held', r.get('claim', ''))
            if m: by.setdefault(m.group(1), []).append(lid)
    srcs = {s['key']: s for s in d['summary']['sources']}
    for i, c in enumerate(d.get('claims', [])):
        p = ('f', k, 'claims', i); src = srcs.get(c['source_key'], {})
        rid = [x for x in by.get(c['id'], []) if x.split('.')[-1] == c['id'].lower()]
        slug = re.sub(r'[^a-z0-9]+', '-', c['source_key'].lower()).strip('-')
        out.append(R(k, [(c['vendor'], 'statement')], 'Does a vendor statement match the published MLCommons results?', C('{0:q}', p + ('statement',)),
                     C('{0:q}', p + ('stated',)), C('{0:q}', p + ('in_file',)), NONE, C('{0:out}', p + ('outcome',)),
                     C('compared: {0:q}. {1:q}', p + ('compared',), p + ('note',)) if c.get('note') else C('compared: {0:q}', p + ('compared',)),
                     C('fetched {0}', p + ('source', 'fetched')), link='/hermes/model/source/' + slug, receipt=rid[0] if len(rid) == 1 else None))
    return out

def ex_model_live():
    k = 'model_live'; d = snap(k); out = []; L = ledger()
    for i, rd_ in enumerate(d.get('rounds', [])):
        for j, c in enumerate(rd_.get('claims', [])):
            p = ('f', k, 'rounds', i, 'claims', j)
            rid = [lid for lid, r in L.items() if lid.startswith('model.') and r.get('status') == 'live' and (rd_['model'] + ' card claim ' + c['name'] + ' ' + str(c['stated']) + ':') in r.get('claim', '')]
            out.append(R(k, [(rd_['model'], 'statement')], "Does a model card's score hold when we run it?", C('{0}, {1}', ('f', k, 'rounds', i, 'model'), p + ('name',)),
                         C('card states {0:q}', p + ('stated',)), C('our run: {0:q}', p + ('ours',)) if c.get('ours') else NONE, NONE,
                         C('{0:out}', p + ('outcome',)) if c.get('outcome') else C('no outcome'), C('{0:q}', p + ('state',)) if c.get('state') else NONE,
                         C('{0}', ('f', k, 'rounds', i, 'updated')) if rd_.get('updated') else C('{0}', ('f', k, 'updated')), receipt=rid[0] if len(rid) == 1 else None))
    return out

def ex_qia():
    k = 'qia'; d = snap(k); out = []
    for proc in sorted(d.get('processors', {})):
        for q in ('p10', 'p01', 't1'):
            p = ('f', k, 'processors', proc, 'counts', q)
            if resolve_safe(p) is None: continue
            out.append(R(k, [('IBM processors', 'statement')], "Does IBM's published calibration match what we measure on the same qubits?",
                         C('{0}, {1}', ('k', k, 'processors', proc), ('lbl', k, 'processors', proc, 'counts', q)),
                         C('the record IBM had in force when our job ran'), C('{0} qubits read', ('f', k, 'processors', proc, 'qubits_read')), NONE,
                         C('IBM above ours {0}, below {1}, consistent {2}, cannot tell {3}', p + ('ABOVE',), p + ('BELOW',), p + ('CONSISTENT',), p + ('CANNOT_TELL',)),
                         read=C('{0}', ('f', k, 'processors', proc, 'window_utc', 0))))
    return out

def resolve_safe(ref):
    try: return resolve(ref)
    except Miss: return None

def ex_forecast():
    k = 'forecast'; d = snap(k); rd = _upd(k); out = []
    prim = d.get('primary'); base = (prim,) if prim and isinstance(d.get(prim), dict) and d[prim].get('cells') else ()
    cells = (d[prim]['cells'] if base else d.get('cells', []))
    for i, c in enumerate(cells):
        p = ('f', k, *base, 'cells', i)
        out.append(R(k, [('National Weather Service', 'statement')], 'Does the stated chance of precipitation match what happened?',
                     C('stated chance {0} percent, lead {1}', p + ('bin',), p + ('lead',)), C('mean stated {0} percent', p + ('mean_stated',)),
                     C('happened in {0} percent of {1} periods', p + ('observed',), p + ('n',)), C('{0} to {1} percent', p + ('lo',), p + ('hi',)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_water():
    k = 'water'; d = snap(k); rd = _upd(k); out = []
    lake = {'mead': 'Lake Mead', 'powell': 'Lake Powell'}
    for res, v in d.get('headline_lead6', {}).items():
        if res not in lake: continue
        b = ('f', k, 'headline_lead6', res, 'band')
        if 'band' in v:
            out.append(R(k, [('Reclamation', 'statement')], 'When Reclamation projects a lake level, where does the lake end up?', C(lake[res] + ', six months ahead, inside the Probable Minimum to Maximum range'),
                         C('the range should hold the level about eighty percent of the time'), C('inside in {0} of {1} months ({2} above, {3} below)', b + ('inside',), b + ('n',), b + ('above',), b + ('below',)),
                         C('{0:pct} to {1:pct}', b + ('lo',), b + ('hi',)), C('{0:out}', b + ('outcome',)), read=rd))
        m = ('f', k, 'headline_lead6', res, 'mp')
        if 'mp' in v:
            out.append(R(k, [('Reclamation', 'statement')], 'When Reclamation projects a lake level, where does the lake end up?', C(lake[res] + ', six months ahead, most probable level'),
                         C('the most probable level'), C('the lake ended above it in {0} of {1} months', m + ('above',), m + ('n',)),
                         C('{0:pct} to {1:pct}', m + ('lo',), m + ('hi',)), C('{0:out}', m + ('outcome',)), read=rd))
    for i, g in enumerate(d.get('usgs_revisions', {}).get('gauges', [])):
        p = ('f', k, 'usgs_revisions', 'gauges', i)
        out.append(R(k, [('USGS', 'statement')], 'Is provisional gauge data later revised beyond a threshold?', C('gauge {0}, parameter {1}', p + ('site',), p + ('parameter',)),
                     C('provisional days stored: {0}', p + ('provisional_days_stored',)), C('approved since: {0}, revised beyond {1}: {2}', p + ('approved_since',), p + ('threshold',), p + ('revised_beyond_threshold',)),
                     C('{0} to {1}', p + ('lo',), p + ('hi',)), C('{0:out}', p + ('outcome',)), read=C('first read {0}', ('f', k, 'usgs_revisions', 'first_read'))))
    return out

def ex_fedsep():
    k = 'fedsep'; d = snap(k); rd = _upd(k); out = []
    q = "Do the Fed's stated ranges describe what happened?"
    for name in d.get('pooled', {}):
        p = ('f', k, 'pooled', name)
        out.append(R(k, [('Federal Reserve', 'statement')], q, C('{0}', ('k', k, 'pooled', name)), C('the range should hold the outcome about seventy percent of the time'),
                     C('outside the range: {0} of {1}', p + ('outside',), p + ('triples',)), _interval(k, ('pooled', name)), C('{0:out}', p + ('outcome',)), read=rd))
    pv = d.get('per_variable', {})
    items = pv.items() if isinstance(pv, dict) else []
    for name, v in items:
        p = ('f', k, 'per_variable', name)
        out.append(R(k, [('Federal Reserve', 'statement')], q, C('{0}', ('k', k, 'per_variable', name)), C('the range should hold the outcome about seventy percent of the time'),
                     C('outside the range: {0} of {1}', p + ('outside',), p + ('n',)), _interval(k, ('per_variable', name)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_revise():
    k = 'revise'; d = snap(k); rd = _upd(k); out = []
    for name in d.get('counts', {}):
        p = ('f', k, 'counts', name)
        out.append(R(k, [('BLS', 'statement')], 'How far does a first estimate move?', C('payroll change, {0}', ('k', k, 'counts', name)), C('the margin the Bureau of Labor Statistics states'),
                     C('moved by more than the margin in {0} of {1} months', p + ('exceed',), p + ('months',)), _interval(k, ('counts', name)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_cadence():
    k = 'cadence'; d = snap(k); out = []
    for i, pt in enumerate(d.get('portals', [])):
        p = ('f', k, 'portals', i)
        out.append(R(k, [(pt['portal'], 'statement')], 'Do government datasets update as often as their portals state?', C('{0} portal', p + ('portal',)),
                     C('series stating a cadence and readable: {0}', p + ('readable',)), C('on schedule {0}, behind {1}, cannot tell {2}', p + ('consistent',), p + ('below',), p + ('cannot_tell',)),
                     C('behind: {0}% ({1}% to {2}%)', p + ('below_share', 0), p + ('below_share', 1), p + ('below_share', 2)), C('this table counts outcomes per series'), read=C('{0}', p + ('read',))))
    return out

def ex_trials():
    k = 'trials'; d = snap(k); rd = _upd(k); out = []
    for sp in d.get('sponsors', {}):
        p = ('f', k, 'sponsors', sp)
        out.append(R(k, [(sp, 'service')], 'Results due against results posted', C('{0}', ('kname', k, 'sponsors', sp)),
                     C('records with results due: {0}', p + ('n',)), C('results posted {0}, no results on the record {1}', p + ('posted',), p + ('no_results',)),
                     C('{0:pct} to {1:pct} with no results', p + ('lo',), p + ('hi',)), C('{0:out}', p + ('outcome',)), read=rd))
    return out

def ex_airline():
    k = 'airline'; d = snap(k); rd = _upd(k); out = []
    for sec in ('now_vs_2025', 'y2025_vs_2019'):
        for al in d.get(sec, {}):
            p = ('f', k, sec, al)
            out.append(R(k, [(al, 'statement')], 'Are schedules getting longer while flights are not?', C('{0}, {1}', ('k', k, sec, al), ('lbl', k, sec)),
                         C('scheduled time changed by {0} minutes', p + ('change',)), C('flown time changed by {0} minutes', p + ('flown_change',)),
                         C('{0} to {1} minutes', p + ('change_ci', 0), p + ('change_ci', 1)) if (d[sec][al].get('change_ci')) else NONE, C('{0:out}', p + ('outcome',)),
                         C('routes: {0}, late share: {1:q}', p + ('routes',), p + ('late',)), read=rd))
    return out

def ex_airq():
    k = 'airq'; d = snap(k); rd = _upd(k); out = []
    for name in d.get('comparison', {}):
        p = ('f', k, 'comparison', name)
        out.append(R(k, [('PurpleAir', 'service'), ('EPA', 'record')], 'Do the sensors meet the targets the EPA wrote down?', C('{0}', ('k', k, 'comparison', name)),
                     C("the EPA's published performance targets for fine particulate sensors"), C('monitors whose sensor misses the targets: {0} of {1}', p + ('n',), p + ('of',)),
                     _interval(k, ('comparison', name)), C('{0:out}', p + ('outcome',)), C('window: {0:q}', ('f', k, 'window')), read=rd))
    return out

def ex_ailuminate():
    k = 'ailuminate'; d = snap(k); rd = _upd(k); out = []
    st = ('f', k, 'stability')
    out.append(R(k, [('MLCommons', 'statement')], 'Do the published results stay what they say?', C('published scores kept, read after read'),
                 C('the reference set is fixed, so scores already published do not shift'), C('systems changed: {0} of {1}, over {2} reads', st + ('n',), st + ('of',), st + ('reads',)),
                 _interval(k, ('stability',)), C('{0:out}', st + ('outcome',)), read=rd))
    for sy in d.get('table', {}):
        p = ('f', k, 'table', sy)
        out.append(R(k, [(sy, 'named'), ('MLCommons', 'statement')], 'Do the published results stay what they say?', C('{0}', ('k', k, 'table', sy)),
                     C('overall percentile {0}', p + ('overall',)), C('mean of its category percentiles {0}', p + ('mean_cats',)),
                     C('categories from {0} to {1}', p + ('lowest',), p + ('highest',)), C('{0:out}', p + ('agree',)), C('released {0:q}', p + ('release',)), read=rd))
    return out

def ex_secrecords():
    k = 'secrecords'; d = snap(k); rd = _upd(k); out = []
    for i, x in enumerate(d.get('disagree_list', [])):
        p = ('f', k, 'disagree_list', i)
        out.append(R(k, [(x['domain'], 'statement')], "Do a domain's security records do what they say?", C('{0}, {1:q}', p + ('domain',), p + ('claim',)),
                     C('{0:q}', p + ('claim',)), C('record: {0:q}', p + ('record',)), NONE, C('does not meet the rule, read in full'), C('{0:q}', p + ('reason',)), read=rd))
    return out

def ex_hf(k, q):
    d = snap(k); rd = _upd(k); out = []
    for lst in ('disagree_list', 'mixed_list'):
        for i, x in enumerate(d.get(lst, []) or []):
            p = ('f', k, lst, i); org = x['repo'].split('/')[0]
            if k == 'hfsize':
                out.append(R(k, [(org, 'statement')], q, C('{0}', p + ('repo',)), C('size in the name: {0:q}', p + ('stated',)), C('parameters in the weights: {0:q}', p + ('actual',)),
                             NONE, C('mismatch, read in full'), C('{0:q}', p + ('reason',)), read=rd))
            else:
                out.append(R(k, [(org, 'statement')], q, C('{0}', p + ('repo',)), C('license tag: {0:q}', p + ('tag',)), C('license file: {0:q}', p + ('file',)),
                             NONE, C('tag and file differ, read in full'), C('{0:q}', p + ('note',)), read=rd))
    return out

def ex_pkglicense():
    k = 'pkglicense'; d = snap(k); rd = _upd(k); out = []
    for i, x in enumerate(d.get('disagree_list', [])):
        p = ('f', k, 'disagree_list', i); org = x['repo'].split('/')[0]
        out.append(R(k, [(org, 'statement')], 'Is the license a package states the license of its repository?', C('{0} ({1})', p + ('project',), p + ('repo',)),
                     C('{0:q}', p + ('stated',)), C('repository license: {0:q}', p + ('repo_license',)), NONE, C('disagree, read in full'), C('{0:q}', p + ('reason',)), read=rd))
    return out

def ex_wiki():
    k = 'wiki'; d = snap(k); rd = _upd(k); out = []
    for i, s in enumerate(d.get('section2', [])):
        p = ('f', k, 'section2', i)
        defs = [(j, x) for j, x in enumerate(s.get('definitions') or []) if x.get('in_outcome') and x.get('lo') is not None][:3]
        dl = NONE
        if defs:
            t = '. '.join('{%d:q}: {%d} to {%d}' % (3 * n, 3 * n + 1, 3 * n + 2) for n in range(len(defs)))
            refs = [r for j, _ in defs for r in (p + ('definitions', j, 'name'), p + ('definitions', j, 'lo'), p + ('definitions', j, 'hi'))]
            dl = C(t, *refs)
        out.append(R(k, [('Wikimedia Foundation', 'statement')], 'Do the figures the Wikimedia Foundation states match its own data?', C('{0:q}', p + ('quote',)),
                     C('{0:q}', p + ('band_text',)) if s.get('band_text') else NONE, dl, NONE, C('{0:out}', p + ('outcome',)),
                     C('{0:q} on {1:q}', p + ('reason',), p + ('page_name',)) if s.get('reason') else C('on {0:q}', p + ('page_name',)), read=C('{0}', p + ('read',))))
    return out

def ex_social_dsa():
    k = 'social_dsa'; d = snap(k); out = []
    q = "Does a platform's EU transparency report match its filings in the DSA Transparency Database?"
    for i, r in enumerate(d.get('rows', [])):
        if not r.get('outcome'): continue                      # label-split rows carry no outcome on the desk
        p = ('f', k, 'rows', i)
        item = C('{0}, {1}, {2}, {3}', p + ('platform',), p + ('period',), p + ('measure',), p + ('view',))
        if r.get('stated') is not None and r.get('ratio') is not None:
            st, dl, iv = C('report: {0}', p + ('stated',)), C('database over report: {0}, database {1}', p + ('ratio',), p + ('database', 'D_app')), C('{0} to {1}', p + ('ratio_lo',), p + ('ratio_hi',))
        elif r.get('stated_share') is not None:
            st, dl, iv = C('report share: {0:pct}', p + ('stated_share',)), C('database share: {0:pct}', p + ('delivered_share',)), C('difference {0} to {1} points', p + ('diff_lo_points',), p + ('diff_hi_points',))
        else:
            st = C('report: {0}', p + ('stated',)) if r.get('stated') is not None else NONE
            dl = C('database: {0}', p + ('database',)) if isinstance(r.get('database'), (int, float)) else NONE
            iv = NONE
        nt = C('{0:q}' + (' A rule set after the data is used, as the desk says.' if (r.get('rules_after_data') or r.get('defined_after_data')) else ''), p + ('reason',)) if r.get('reason') else NONE
        out.append(R(k, [(r['platform'], 'statement')], q, item, st, dl, iv, C('{0:out}', p + ('outcome',)), nt, read=C('half-year {0}', p + ('period',))))
    return out

def ex_social_tiktok():
    k = 'social_tiktok'; d = snap(k); rd = _upd(k); out = []
    for i, r in enumerate(d.get('eu_rows', [])):
        p = ('f', k, 'eu_rows', i)
        out.append(R(k, [('TikTok', 'statement')], "Does TikTok's quarterly report match its EU filings?", C('{0}, {1}', p + ('quarter',), p + ('measure',)),
                     C('report: {0}', p + ('stated',)), C('database: {0}', p + ('delivered',)), C('gap from {0} to {1}', p + ('gap', 0), p + ('gap', 1)) if r.get('gap') else NONE,
                     C('{0:out}', p + ('outcome',)), C('{0:q}', p + ('reason',)) if r.get('reason') else NONE, read=rd))
    return out

def ex_social_bluesky():
    k = 'social_bluesky'; d = snap(k); rd = _upd(k); out = []
    for i, r in enumerate(d.get('rows', [])):
        p = ('f', k, 'rows', i)
        out.append(R(k, [('Bluesky', 'statement')], "Does Bluesky's transparency report match its signed label stream?", C('{0:q}', p + ('what',)),
                     C('Bluesky states {0:q}', p + ('stated',)), C('stream, first reading: {0}', p + ('delivered',)),
                     C('{0} to {1}', p + ('interval', 0), p + ('interval', 1)) if r.get('interval') else NONE, C('{0:out}', p + ('outcome',)), C('{0:q}', p + ('reason',)) if r.get('reason') else NONE, read=rd))
    return out

def ex_ledger_social():
    out = []
    for lid, r in ledger().items():
        if r.get('status') != 'live': continue
        if lid.startswith('social.adspend.'):
            out.append(R('social_adspend', [('Google', 'statement')], "Does Google's stated election ad spend match the committee's FEC filings?", C('{0:q}', ('l', lid, 'claim')),
                         NONE, C('{0} {1:q}', ('l', lid, 'value'), ('l', lid, 'unit')), NONE, C('a count of rows on the desk'), read=C('{0}', ('lat', lid)), receipt=lid))
    return out

def ex_credit():
    k = 'credit'; d = snap(k); rd = _upd(k); out = []
    if d is None: raise Miss('no snapshot credit')
    for i, r in enumerate(d.get('ruler1', [])):
        p = ('f', k, 'ruler1', i)
        out.append(R(k, [('CFPB', 'statement')], 'Does the timely response share the CFPB prints match its own complaint database?', C('complaints received in {0:q}', p + ('year',)),
                     C('printed: {0:q} of complaints sent to companies', p + ('printed',)), C('database: {0:pct} of {1} complaints', p + ('timely',), p + ('rows',)), C('{0:pct} to {1:pct}', p + ('lo',), p + ('hi',)),
                     C('{0:out}', p + ('outcome',)), C('the printed figure counts every complaint sent, the database the published ones'), read=rd))
    for i, c in enumerate(d.get('companies', [])):
        if not c.get('bureau'): continue
        p = ('f', k, 'companies', i)
        out.append(R(k, [(c['company'], 'named')], 'How often is a company flagged not timely against the share the CFPB printed figure leaves?', C('complaints received in {0:q}', p + ('year',)),
                     C('printed all-company figure leaves {0:pct} to {1:pct} not timely', p + ('band', 0), p + ('band', 1)), C('not timely: {0} of {1}', p + ('not_timely',), p + ('rows',)),
                     C('{0:pct} to {1:pct}', p + ('lo',), p + ('hi',)), C('{0:out}', p + ('outcome',)), C('the printed figure is an all-company average, not a per-company limit'), read=rd))
    return out

EXTRACT = [ex_uptime, ex_time, ex_cada, ex_support, ex_change, ex_model, ex_model_live, ex_qia, ex_forecast, ex_water, ex_fedsep, ex_revise, ex_cadence,
           ex_trials, ex_airline, ex_airq, ex_ailuminate, ex_secrecords, lambda: ex_hf('hfsize', "Does the size in a model's name match the weights?"),
           lambda: ex_hf('hflicense', 'Does the license tag of a model match its license file?'), ex_pkglicense, ex_wiki, ex_social_dsa, ex_social_tiktok, ex_social_bluesky, ex_ledger_social, ex_credit]


# ---------------------------------------------------------------- build
CELLS = ('item', 'stated', 'delivered', 'interval', 'outcome', 'note', 'read')
COLS = [('item', 'Row'), ('role', 'Role'), ('stated', 'Stated'), ('delivered', 'Delivered'), ('interval', 'Interval'), ('outcome', 'Outcome'), ('note', 'Note'), ('read', 'Read')]

def entities():
    return json.load(open(ENT))

def _receipt_url(rid):
    return ('/r/' + rid) if rid and os.path.exists(os.path.join(PUB, 'r', rid + '.html')) else ''

def collect():
    """Every row of every extractor, rendered, with the pages it belongs on. Returns (rows, unmapped)."""
    ent = entities(); amap = {}
    for e in ent['entities']:
        for a in e['aliases']: amap[(a['desk'], a['raw'])] = e['slug']
    excl = {(x['desk'], x['raw']) for x in ent['excluded']}
    rows, unmapped = [], {}; skipped = []
    for fn in EXTRACT:
        try: got = fn()
        except Miss as m: print('  brands: extractor skipped (%s)' % m); continue
        for r in got:
            on = []
            for raw, role in r['raws']:
                s = amap.get((r['key'], raw))
                if s: on.append((s, role))
                elif (r['key'], raw) not in excl: unmapped.setdefault(r['key'], set()).add(raw)
            if not on: continue
            try: out = {c: render(r[c]) for c in CELLS}
            except Miss as m: skipped.append('%s: %s' % (r['key'], m)); SKIP[r['key']] = SKIP.get(r['key'], 0) + 1; continue
            out.update({'key': r['key'], 'desk': SRC[r['key']][1], 'question': r['question'][0], 'link': r['link'], 'receipt': r['receipt'] or '',
                        'receipt_url': _receipt_url(r['receipt']), 'on': on, 'cells': {c: r[c] for c in CELLS}})
            rows.append(out)
    if skipped: print('  brands: %d rows left off, a field the row needs is not in its feed (first: %s)' % (len(skipped), skipped[0]))
    return rows, {k: sorted(v) for k, v in unmapped.items()}

def by_brand(rows):
    ent = {e['slug']: e for e in entities()['entities']}; out = {}
    for i, r in enumerate(rows):
        for s, role in r['on']: out.setdefault(s, []).append((i, role))
    return {s: (ent[s], v) for s, v in out.items()}

def _csv(e, rows, items):
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['brand', 'desk', 'desk_page', 'question', 'row', 'role', 'stated', 'delivered', 'interval', 'outcome', 'note', 'read', 'receipt'])
    for i, role in items:
        r = rows[i]
        w.writerow([e['name'], r['desk'], SITE + r['link'], r['question'], r['item'], ROLE[role], r['stated'], r['delivered'], r['interval'], r['outcome'], r['note'], r['read'], (SITE + r['receipt_url']) if r['receipt_url'] else ''])
    return buf.getvalue()

def _desks_line(names):
    names = list(dict.fromkeys(names))
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]

def _page_body(e, rows, items, csv_href):
    s = e['slug']; nm = E(e['name'])
    o = [f'<section class="legal"><p class="meta"><a href="/brand">Brands</a> &middot; Stated against delivered</p>',
         f'<p>Every row the desks of Heuremen LLC publish about {nm}: the desk, the question, what was stated, what was delivered, the outcome the desk gives and when the desk read it. '
         'Each row links to its desk, which holds the current reading.</p>',
         f'<p><a href="{csv_href}" download>These rows as CSV</a> &middot; Named here and want to answer a row? <a href="/respond?u=brand-{E(s)}">Respond</a></p>']
    if e.get('note'): o.append(f'<p class="meta">{E(e["note"])}</p>')
    used = {(rows[i]['key']) for i, _ in items}
    al = [a for a in e['aliases'] if a['desk'] in used]
    o.append('<h2>Names on this page</h2><ul>' + ''.join(f'<li><strong>{E(a["raw"])}</strong> on {E(SRC[a["desk"]][1])}: {E(a["decided"])}.</li>' for a in al) + '</ul>')
    groups = {}
    for i, role in items: groups.setdefault(rows[i]['desk'], {}).setdefault(rows[i]['question'], []).append((i, role))
    for desk in sorted(groups):
        o.append(f'<h2 id="{E(desk.lower())}">{E(desk)}</h2>')
        for q, its in groups[desk].items():
            o.append(f'<h3>{E(q)}</h3><div class="scroll"><table class="mtx"><thead><tr>' + ''.join(f'<th>{t}</th>' for _, t in COLS) + '<th>Links</th></tr></thead><tbody>')
            for i, role in its:
                r = rows[i]
                lk = f'<a href="{E(r["link"])}">{E(r["desk"])}</a>' + (f' &middot; <a href="{E(r["receipt_url"])}">receipt</a>' if r['receipt_url'] else '')
                o.append('<tr>' + ''.join('<td>' + E(ROLE[role] if c == 'role' else r[c]) + '</td>' for c, _ in COLS) + f'<td class="lk">{lk}</td></tr>')
            o.append('</tbody></table></div>')
    o.append('<p class="meta">The outcome is the desk&rsquo;s own word. Above, below, consistent and cannot tell are kept apart and never folded together. '
             'Rows are as each desk last read them when this page was built, and the read time is on every row. No row here is a new reading. '
             'To correct or remove a row, use the <a href="/correction">correction or removal form</a>.</p></section>')
    return ''.join(o)

def _dataset(e, path, csv_href, aliases, desks):
    d = (f'Rows the Heuremen LLC desks publish about {e["name"]}, from {_desks_line(desks)}: the question, the stated figure, the delivered figure, '
         'the outcome the desk gives (above, below, consistent or cannot tell, kept apart), the interval and the read time, with a link to each desk.')
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": f'{e["name"]}: stated against delivered', "description": d, "url": SITE + path,
          "creator": {"@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/"}, "publisher": {"@type": "Organization", "name": "Heuremen LLC", "url": SITE + "/"},
          "isAccessibleForFree": True, "license": SITE + "/terms", "dateModified": D.date.today().isoformat(), "inLanguage": "en",
          "copyrightNotice": "Heuremen LLC. Free to download and cite with attribution. Not licensed for text and data mining or AI training.",
          "about": {"@type": "Organization", "name": e['name']}, "keywords": list(dict.fromkeys([e['name']] + aliases)),
          "variableMeasured": ["stated figure", "delivered figure", "outcome", "interval", "read time"],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + csv_href}]}
    return '<script type="application/ld+json">' + json.dumps(ds, ensure_ascii=False).replace('</', '<\\/') + '</script>'

SEARCH_JS = """// Brand index search: filters the list as you type. No tracking, nothing sent.
(function () {
  var q = document.getElementById('brand-q'), li = document.querySelectorAll('#brand-list li'), n = document.getElementById('brand-none'); if (!q) return;
  q.addEventListener('input', function () {
    var t = q.value.toLowerCase().trim(), shown = 0;
    li.forEach(function (x) { var on = !t || x.getAttribute('data-n').indexOf(t) >= 0; x.hidden = !on; if (on) shown++; });
    if (n) n.hidden = shown > 0;
  });
})();
"""

def add_pages(PAGES, page, hero_slim, HOME=None, FEED=None, refresh_feeds=True):
    """The one hook build_site.py calls. Refreshes the snapshots, renders every brand page and the index into PAGES, writes the CSVs and rows.json."""
    if refresh_feeds:
        st = refresh(); bad = {k: v for k, v in st.items() if v.startswith('MISSING')}
        if bad: print('  brands: no snapshot for', bad)
    rows, unmapped = collect(); bb = by_brand(rows)
    os.makedirs(CSVDIR, exist_ok=True)
    keep = set()
    idx = []
    for s, (e, items) in sorted(bb.items(), key=lambda x: x[1][0]['name'].lower()):
        path = '/brand/' + s; csv_href = '/brand/' + s + '.csv'; keep.add(s + '.csv')
        open(os.path.join(CSVDIR, s + '.csv'), 'w', encoding='utf-8').write(_csv(e, rows, items))
        used = {rows[i]['key'] for i, _ in items}
        desks = [rows[i]['desk'] for i, _ in items]
        aliases = [a['raw'] for a in e['aliases'] if a['desk'] in used]
        desc = f'{e["name"]}: every row the Heuremen LLC desks publish about it, from {_desks_line(desks)}, with the stated figure, the delivered figure, the outcome and the read time.'
        body = _page_body(e, rows, items, csv_href) + _dataset(e, path, csv_href, aliases, desks)
        PAGES[path] = page(path, f'{e["name"]}: Stated Against Delivered | Brands | Heuremen LLC', desc, body, hero_slim(E(e['name'])))
        if HOME is not None: HOME[path] = '/hermes'
        other = [a for a in aliases if a.lower() != e['name'].lower()]
        idx.append(f'<li data-n="{E(" ".join([e["name"]] + aliases).lower())}"><a href="{path}">{E(e["name"])}</a> <span class="meta">Rows on {E(_desks_line(desks))}'
                   + (f'. Also named {E(_desks_line(other[:4]))}' + (' and others' if len(other) > 4 else '') if other else '') + '.</span></li>')
    for f in os.listdir(CSVDIR):
        if f.endswith('.csv') and f not in keep: os.remove(os.path.join(CSVDIR, f))
    open(os.path.join(CSVDIR, 'search.js'), 'w').write(SEARCH_JS)
    ibody = ('<section class="legal"><p>One page for each company, agency and organisation our desks measure. Each page lists every row the desks publish about it, '
             'with the desk, the question, the stated figure, the delivered figure, the outcome and the read time. People never get a page.</p>'
             '<p><label for="brand-q">Find an organisation</label> <input type="search" id="brand-q" placeholder="Name, service or domain" autocomplete="off"></p>'
             '<p id="brand-none" class="meta" hidden>No organisation by that name is on a desk yet.</p>'
             '<ul id="brand-list">' + ''.join(idx) + '</ul>'
             '<p class="meta">How each name was tied to its page is on the page. Distinct legal entities are merged only where the page says so. '
             'Names a desk shows that are not tied to a page stay on their desk. <a href="/brand/entities.json">The entity map (JSON)</a>.</p></section>'
             '<script src="/brand/search.js" defer></script>')
    import shutil; shutil.copyfile(ENT, os.path.join(CSVDIR, 'entities.json'))   # the served copy, byte for byte (ledger/copies.json: brand_entities)
    PAGES['/brand'] = page('/brand', 'Brands: Organisations Our Desks Measure | Heuremen LLC',
                           'Every company, agency and organisation the Heuremen LLC desks measure, each with a page of the rows published about it: stated, delivered, outcome and read time.',
                           ibody, hero_slim('Brands'))
    if HOME is not None: HOME['/brand'] = '/hermes'
    if '/hermes' in PAGES and '</main>' in PAGES['/hermes'] and 'href="/brand"' not in PAGES['/hermes']:
        i = PAGES['/hermes'].rfind('</main>')
        PAGES['/hermes'] = PAGES['/hermes'][:i] + '<p class="meta"><a href="/brand">Brands</a>: one page for each organisation our desks measure, with every row about it.</p>' + PAGES['/hermes'][i:]
    json.dump({'built': D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'rows': rows, 'unmapped': unmapped}, open(ROWS, 'w'), ensure_ascii=False, default=list)
    print('brands: %d brand pages and the index' % len(bb))
    return bb


# ---------------------------------------------------------------- gate
def gate():
    """Every brand-page number traces to a desk row or a ledger row. Refuses on any miss."""
    errs = []
    try: built = json.load(open(ROWS))
    except Exception as e: print('BRANDS GATE: no rows.json (%s)' % e); return 1
    for k, v in LBL.items():
        if any(ch.isdigit() and ch not in k for ch in v): errs.append('label %r has a digit its key %r does not' % (v, k))
    ent = entities(); slugs = {e['slug'] for e in ent['entities']}
    ex = {(x['desk'], x['raw']) for x in ent['excluded']}
    for e in ent['entities']:
        for a in e['aliases']:
            if (a['desk'], a['raw']) in ex: errs.append('excluded name %r is also an alias' % a['raw'])
            if not a.get('decided'): errs.append('alias %r without how it was decided' % a['raw'])
    pages = {}
    for n, r in enumerate(built['rows']):
        for c in CELLS:
            t, refs = r['cells'][c]; refs = [tuple(x) for x in refs]
            if re.search(r'\d', literal((t, refs))): errs.append('row %d %s: digit in literal text %r' % (n, c, t))
            try: v = render((t, refs))
            except Miss as m: errs.append('row %d %s: %s' % (n, c, m)); continue
            if v != r[c]: errs.append('row %d %s: built %r, source now %r' % (n, c, r[c], v))
            for x in refs:
                if x[0] == 'l' and not str(x[1]): errs.append('row %d: empty ledger id' % n)
        if r['receipt'] and r['receipt'] not in ledger(): errs.append('row %d: receipt %s not in the ledger' % (n, r['receipt']))
        for s, _ in r['on']:
            if s not in slugs: errs.append('row %d on unknown page %s' % (n, s))
            pages.setdefault(s, []).append(r)
    for s, rs in pages.items():
        p = os.path.join(HERE, 'brand', s + '.html')
        if not os.path.exists(p): errs.append('no page brand/%s.html' % s); continue
        doc = open(p, encoding='utf-8').read(); main = doc[doc.find('<main'):doc.rfind('</main>')]
        cells = set(re.findall(r'<td>(.*?)</td>', main, re.S))
        for r in rs:
            for c in CELLS:
                if r[c] and E(r[c]) not in cells: errs.append('brand/%s: cell %r not on the page' % (s, r[c][:60]))
        # every number on the page's tables is in a traced cell
        tr = {E(r[c]) for r in rs for c in CELLS}
        for td in cells:
            if re.search(r'\d', td) and td not in tr: errs.append('brand/%s: untraced cell %r' % (s, td[:60]))
        cp = os.path.join(CSVDIR, s + '.csv')
        if not os.path.exists(cp): errs.append('no CSV for %s' % s)
        else:
            got = list(csv.DictReader(open(cp, encoding='utf-8')))
            if len(got) != len(rs): errs.append('%s.csv: %d rows, page has %d' % (s, len(got), len(rs)))
            want = {r[c] for r in rs for c in CELLS}
            for g in got:
                for c in ('row', 'stated', 'delivered', 'interval', 'outcome', 'note', 'read'):
                    if g[c] and g[c] not in want: errs.append('%s.csv: untraced %s %r' % (s, c, g[c][:60]))
    for f in os.listdir(os.path.join(HERE, 'brand')) if os.path.isdir(os.path.join(HERE, 'brand')) else []:
        if f.endswith('.html') and f[:-5] not in pages: errs.append('stale page brand/%s' % f)
    for e in errs[:30]: print('  BRANDS', e)
    print(('BRANDS GATE: REFUSED, %d problems' % len(errs)) if errs else 'BRANDS GATE: every brand-page number traces to a desk row or a ledger row (%d rows, %d pages)' % (len(built['rows']), len(pages)))
    return 1 if errs else 0


if __name__ == '__main__':
    if '--gate' in sys.argv: sys.exit(gate())
    if '--dry' in sys.argv:
        if '--refresh' in sys.argv: print(refresh())
        rows, un = collect(); bb = by_brand(rows)
        print(len(rows), 'rows on', len(bb), 'pages'); print('unmapped:', json.dumps(un)[:3000])
