"""forecasters.py -- indahl.ai/forecasters (10 Nov 2026). Every public forecaster our desks score, on one axis.

Called by build_site.py with one hook (add_pages). Also a gate: python3 forecasters.py --gate.

  Members  ~/bones-forge/forecasters/members.json, one entry per desk. A desk whose feed is not served yet, or whose feed has no rows the
           page can read, is left off and listed in forecasters/rows.json as held. A desk with rows 'feed' is read from the 'forecasters'
           block of its own live.json, so a new desk appears on the next build once it ships that block.
  Rows     only numbers the desks already publish: each desk's live feed (snapshotted to forecasters/feeds/ at build) and live ledger rows.
           No new readings. The outcome is the desk's own label, exactly as the desk gives it.
  Axis     one axis for both kinds of stated figure: the share the desk counts minus the share the statement implies, in percentage points.
           For a coverage claim that is delivered coverage minus stated coverage (or the outside share minus the stated outside share, as the
           desk counts it). For a probability forecast it is the reliability gap, observed frequency minus stated chance. The interval is the
           desk's own interval moved by the same stated share. The subtraction is drawn, never printed.
  Trace    every printed cell is a template plus references into a snapshot or a ledger row, and the literal text of a template holds no
           digit. The gate re-reads every reference, re-renders every cell and every chart position, checks the built page holds exactly
           those cells, and checks that no other text on the page carries a digit except the axis ticks.
Python 3.9+."""
import os, re, json, html, sys, datetime as D, urllib.request, concurrent.futures as CF

HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
FC = os.path.join(B, 'forecasters'); FEEDS = os.path.join(FC, 'feeds'); MEMBERS = os.path.join(FC, 'members.json'); ROWS = os.path.join(FC, 'rows.json')
LEDGER = os.path.join(B, 'ledger', 'ledger.jsonl'); SITE = 'https://indahl.ai'; PATH = '/forecasters'
E = html.escape
CELLS = ('desk', 'item', 'counts', 'stated', 'delivered', 'interval', 'outcome', 'read')
LAKE = {'mead': 'Lake Mead', 'powell': 'Lake Powell'}   # labels for feed keys that are codes; no digits


def members(): return json.load(open(MEMBERS))['members']


# ---------------------------------------------------------------- snapshots and references
def refresh():
    """Fetch every member feed (cache-busting) into forecasters/feeds/. A 404 or a failed fetch keeps no new snapshot."""
    os.makedirs(FEEDS, exist_ok=True); out = {}
    def one(m):
        p = os.path.join(FEEDS, m['slug'] + '.json')
        try:
            req = urllib.request.Request(SITE + m['feed'] + '?b=' + D.datetime.now(D.timezone.utc).strftime('%Y%m%d%H%M%S'), headers={'User-Agent': 'heuremen-forecasters/1'})
            d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode('utf-8'))
            if not isinstance(d, dict) or not d: raise ValueError('empty')
            json.dump(d, open(p, 'w'), ensure_ascii=False); return m['slug'], 'fresh'
        except Exception as e:
            return m['slug'], ('kept: %s' % e) if os.path.exists(p) else ('none: %s' % e)
    with CF.ThreadPoolExecutor(8) as ex:
        for k, st in ex.map(one, members()): out[k] = st
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

def dig(o, path, root=None):
    root = o if root is None else root
    for p in path:
        if isinstance(p, dict) and '$' in p: p = dig(root, p['$'], root)
        if isinstance(p, dict):
            if not isinstance(o, list): raise Miss('no list for %r' % (p,))
            o = next((x for x in o if isinstance(x, dict) and all(x.get(a) == b for a, b in p.items())), None)
            if o is None: raise Miss('no item %r' % (p,))
            continue
        try: o = o[p]
        except (KeyError, IndexError, TypeError): raise Miss('no %r' % (p,))
    return o

def resolve(ref):
    """('f', slug, *absolute path) into a snapshot, ('k', slug, *path, key) a key name, ('l', ledger id, field) into a live ledger row."""
    if ref[0] == 'f':
        o = snap(ref[1])
        if o is None: raise Miss('no snapshot %s' % ref[1])
        return dig(o, list(ref[2:]))
    if ref[0] == 'k':
        o = resolve(('f', ref[1]) + tuple(ref[2:-1]))
        if not isinstance(o, dict) or ref[-1] not in o: raise Miss('%s: no key %r' % (ref[1], ref[-1]))
        return ref[-1]
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

def _pct(v):
    """A share as the desk gives it, times 100, with no rounding beyond the desk's own digits (0.51 -> 51%, 0.1463 -> 14.63%)."""
    if v is None: return 'none'
    s = ('%.6f' % (float(v) * 100)).rstrip('0').rstrip('.'); return s + '%'

FMT = {
    '': lambda v: 'none' if v is None else _num(v),
    'pct': _pct,
    'p100': lambda v: 'none' if v is None else _num(v) + '%',      # a value the desk already gives in percent
    'lake': lambda v: LAKE[v],
}
_PH = re.compile(r'\{(\d+)(?::(\w+))?\}')

def render(cell):
    t, refs = cell
    vals = [resolve(tuple(r)) for r in refs]
    return _PH.sub(lambda m: FMT[m.group(2) or ''](vals[int(m.group(1))]), t)

def literal(cell): return _PH.sub('', cell[0])

def value(ref):
    v = resolve(tuple(ref))
    if v is None or isinstance(v, bool): raise Miss('no number at %r' % (ref,))
    return float(v)


# ---------------------------------------------------------------- rows
def _ref(r, slug, base):
    if 'f' in r: return ['f', slug] + list(base) + list(r['f'])
    if 'F' in r: return ['f', slug] + list(r['F'])
    if 'k' in r: raise Miss('k ref needs a key')
    if 'l' in r: return ['l'] + list(r['l'])
    raise Miss('bad ref %r' % (r,))

def _cell(spec, slug, base, key=None):
    """A cell spec is a plain string (no digits allowed), {'t': template, 'refs': [...]} or a single ref (printed as given)."""
    if isinstance(spec, str): return (spec, [])
    if 't' not in spec: spec = {'t': '{0}', 'refs': [spec]}
    refs = []
    for r in spec['refs']:
        if 'k' in r: refs.append(['k', slug] + list(r['k']) + [key])
        else: refs.append(_ref(r, slug, base))
    return (spec['t'], refs)

def _expand(m):
    """One entry per row: (base path, key or None, row spec). Explicit rows from members.json, or the feed's own block."""
    slug = m['slug']; d = snap(slug); out = []
    if d is None: raise Miss('feed not served')
    specs = m['rows']
    if specs == 'feed':
        blk = d.get('forecasters', {}).get('rows') if isinstance(d.get('forecasters'), dict) else None
        if not blk: raise Miss('feed has no forecasters block')
        for i, r in enumerate(blk):
            base = ['forecasters', 'rows', i]; sc = 1
            sp = {'kind': r.get('kind'), 'scale': sc, 'item': {'f': ['item']}, 'counts': {'f': ['counts']},
                  'stated': {'t': '{0:pct}' + (', our reading' if r.get('stated_by') == 'ours' else ''), 'refs': [{'f': ['stated']}]},
                  'delivered': ({'t': '{0} of {1}, {2:pct}', 'refs': [{'f': ['n']}, {'f': ['of']}, {'f': ['delivered']}]} if r.get('n') is not None and r.get('of') is not None
                                else {'t': '{0:pct}', 'refs': [{'f': ['delivered']}]}),
                  'interval': {'t': '{0:pct} to {1:pct}', 'refs': [{'f': ['lo']}, {'f': ['hi']}]}, 'outcome': {'f': ['outcome']},
                  'num': {'stated': {'f': ['stated']}, 'delivered': {'f': ['delivered']}, 'lo': {'f': ['lo']}, 'hi': {'f': ['hi']}},
                  'note_ref': {'f': ['interval']} if r.get('interval') else None}
            if r.get('brier_skill') is not None and r.get('brier_skill_lo') is not None and r.get('brier_skill_hi') is not None:
                sp['brier'] = {'t': '{0} ({1} to {2})', 'refs': [{'f': ['brier_skill']}, {'f': ['brier_skill_lo']}, {'f': ['brier_skill_hi']}]}
            out.append((base, None, sp))
        return out
    for sp in specs:
        if 'each' in sp:
            lst = dig(d, sp['each'])
            path = [dig(d, p['$']) if isinstance(p, dict) and '$' in p else p for p in sp['each']]
            for i in range(len(lst)): out.append((path + [i] + sp.get('sub', []), None, sp))
        elif 'key' in sp:
            obj = dig(d, sp['key'])
            for k in obj: out.append((list(sp['key']) + [k] + sp.get('sub', []), k, sp))
        else: out.append(([], None, sp))
    return out


def collect():
    """Every row the page shows, sorted by desk name then the desk's own order, plus the members held off and why."""
    rows, held = [], []
    for m in sorted(members(), key=lambda m: m['desk']):
        try: ex = _expand(m)
        except Miss as e: held.append({'desk': m['desk'], 'why': str(e)}); continue
        stamp = ('{0}', [['f', m['slug']] + list(m['stamp'])])
        for base, key, sp in ex:
            try:
                cells = {'desk': (m['desk'], []), 'item': _cell(sp['item'], m['slug'], base, key), 'counts': _cell(sp['counts'], m['slug'], base, key),
                         'stated': _cell(sp['stated'], m['slug'], base, key), 'delivered': _cell(sp['delivered'], m['slug'], base, key),
                         'interval': _cell(sp['interval'], m['slug'], base, key), 'outcome': _cell(sp['outcome'], m['slug'], base, key), 'read': stamp}
                if sp.get('brier'): cells['brier'] = _cell(sp['brier'], m['slug'], base, key)
                nums = {k: _ref(v, m['slug'], base) for k, v in sp['num'].items()}
                r = {'desk': m['desk'], 'slug': m['slug'], 'page': m['page'], 'source': m['source'], 'kind': sp['kind'], 'scale': sp.get('scale', 1),
                     'note': sp.get('note', ''), 'ours': bool(m.get('our_reading')), 'cells': cells, 'nums': nums}
                r['text'] = {c: render(v) for c, v in cells.items()}
                r['pos'] = position(r)
                rows.append(r)
            except (Miss, KeyError, ValueError, TypeError) as e:
                held.append({'desk': m['desk'], 'why': 'row %r: %s' % (base, e)})
    return rows, held


# ---------------------------------------------------------------- axis
def position(r):
    """Delivered minus stated, and the interval moved by the same stated share, in percentage points. Drawn, never printed."""
    k = 100.0 if r['scale'] == 1 else 1.0
    s, v, lo, hi = (value(r['nums'][x]) * k for x in ('stated', 'delivered', 'lo', 'hi'))
    return {'gap': round(v - s, 4), 'lo': round(lo - s, 4), 'hi': round(hi - s, 4)}

def domain(rows):
    lo = min([0.0] + [r['pos']['lo'] for r in rows]); hi = max([0.0] + [r['pos']['hi'] for r in rows])
    step = 10 if hi - lo <= 80 else 20
    a = step * int(-(-abs(lo) // step)) * (-1 if lo < 0 else 1) if lo < 0 else 0
    b = step * int(-(-hi // step)) if hi > 0 else 0
    if b - a < 2 * step: b = a + 2 * step
    return a, b, step

def ticks(a, b, step): return list(range(int(a), int(b) + 1, int(step)))

def tick_label(t): return '0' if t == 0 else ('+%d' % t if t > 0 else '&minus;%d' % -t)

def _x(v, a, b): return '%.3f%%' % (100.0 * (v - a) / (b - a))


# ---------------------------------------------------------------- page
INTRO = (
 '<section class="legal">'
 '<h2>Do public forecasters get it about as right as they say?</h2>'
 '<p>Several of our desks set a public forecaster&rsquo;s own stated figure beside what happened. This page puts cells from each desk on one axis, '
 'so the weather service and the lake projections, the Fed and the payroll estimates, and the asteroid distances can be read side by side. '
 'Each desk counts its own cells, and nothing on this page is counted again. Each desk&rsquo;s section names its cells, and the full tables are on its page.</p>'
 '<p>A stated figure comes in one of two kinds. A range with a stated coverage says how often the outcome should land inside it, or outside it. '
 'A probability forecast states a chance, and its reliability is how often the event happened when that chance was stated. '
 'On the axis each point is the share the desk counts minus the share the statement implies, in percentage points. Zero is a statement that held exactly. '
 'The bar is the desk&rsquo;s own interval, moved by the same stated share. '
 'Each desk&rsquo;s section says what its share counts, inside the range for some and outside it for others, so a point right of zero means that thing happened more often than stated.</p>'
 '<p>The label beside each point is the desk&rsquo;s own outcome, exactly as the desk gives it. ABOVE means the whole interval sits above the stated share and BELOW that it sits below. '
 'CONSISTENT means the interval holds the stated share and meets that desk&rsquo;s rule for width or size. CANNOT_TELL means it does not, so a point clear of zero can still read CANNOT_TELL when its cell is small or its interval wide.</p>'
 '<p>The members measure unlike things: precipitation at airports, lake levels, economic projections, payroll revisions and asteroid distances. '
 'Their units, sample sizes, intervals and outcome rules differ, and each desk&rsquo;s page says how its cells are made. '
 'The width of a bar reflects the desk&rsquo;s sample size and its interval method, and on some desks neighbouring cells are not independent of each other, as their pages say. '
 'This is not a ranking of agencies. The rows are sorted by desk name, never by how close they sit to zero.</p>'
 '<p>Where the stated share is our reading of the statement rather than the forecaster&rsquo;s own words, the desk&rsquo;s section and its rows say so. '
 'For a probability forecast a second score, Brier skill against climatology, is added in its own column when the desk&rsquo;s feed publishes it.</p>'
 '</section>')

OURS = 'The stated share is our reading.'

def _ival_style(p, a, b): return 'left:%s;width:%s' % (_x(p['lo'], a, b), '%.3f%%' % (100.0 * (p['hi'] - p['lo']) / (b - a)))

def _tip(r):
    t = r['text']; return f'{t["desk"]}, {t["item"]}, {t["counts"]}: stated {t["stated"]}, delivered {t["delivered"]}, interval {t["interval"]}, outcome {t["outcome"]}'

def _header(r):
    t = r['text']
    return (f'<div class="fcx-h"><a href="{r["page"]}">{E(r["desk"])}</a> <span>{E(r["source"])}</span>'
            f'<span class="fcx-c">Share counted: {E(t["counts"])}.' + (' ' + OURS if r.get('ours') else '') + '</span></div>')

def chart(rows):
    a, b, step = domain(rows); ts = ticks(a, b, step); z = _x(0, a, b)
    head = ''.join(f'<span class="fcx-tick" style="left:{_x(t, a, b)}">{tick_label(t)}</span>' for t in ts)
    grid = ''.join(f'<span class="fcx-g" style="left:{_x(t, a, b)}"></span>' for t in ts if t != 0)
    out = ['<figure class="fcx" aria-labelledby="fcx-cap">',
           '<figcaption id="fcx-cap" class="fcx-cap">Delivered minus stated, percentage points, with each desk&rsquo;s interval and its own outcome label</figcaption>',
           '<p class="fcx-key" aria-hidden="true"><span class="fcx-k"><i class="fcx-d c"></i> a range with a stated coverage</span> '
           '<span class="fcx-k"><i class="fcx-d p"></i> a probability forecast, reliability</span></p>',
           f'<div class="fcx-r fcx-ax" aria-hidden="true"><span class="fcx-l"></span><span class="fcx-s">{head}</span><span class="fcx-o"></span></div>']
    last = None
    for r in rows:
        t = r['text']; p = r['pos']
        if r['desk'] != last:
            out.append(_header(r)); last = r['desk']
        tip = _tip(r)
        out.append(f'<div class="fcx-r" tabindex="0" title="{E(tip)}" aria-label="{E(tip)}">'
                   f'<span class="fcx-l">{E(t["item"])}</span>'
                   f'<span class="fcx-s" aria-hidden="true">{grid}<span class="fcx-z" style="left:{z}"></span>'
                   f'<span class="fcx-i" style="{_ival_style(p, a, b)}"></span>'
                   f'<span class="fcx-d {"p" if r["kind"] == "probability" else "c"}" style="left:{_x(p["gap"], a, b)}"></span></span>'
                   f'<span class="fcx-o">{E(t["outcome"])}</span></div>')
    out.append('</figure>')
    return ''.join(out)

def table(rows):
    brier = any('brier' in r['text'] for r in rows)
    h = ['Desk', 'Cell', 'What the share counts', 'Stated', 'Delivered', 'Interval', 'Outcome'] + (['Brier skill'] if brier else []) + ['Read']
    body = []
    for r in rows:
        t = r['text']
        cells = [f'<a href="{r["page"]}">{E(t["desk"])}</a>', E(t['item']), E(t['counts']), E(t['stated']), E(t['delivered']), E(t['interval']), E(t['outcome'])]
        if brier: cells.append(E(t.get('brier', 'not published')))
        cells.append(E(t['read']))  # UTC, as the desk stamps it
        body.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
    notes = []
    for r in rows:
        n = f'{r["desk"]}: {r["note"]}' if r['note'] else ''
        if n and n not in notes: notes.append(n)
    return ('<section><h2>The cells, as each desk gives them</h2><div class="scroll"><table class="mtx fcx-t"><thead><tr>' + ''.join(f'<th>{x}</th>' for x in h)
            + '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div>'
            + ''.join(f'<p class="meta">{E(n)}</p>' for n in notes)
            + '<p class="meta">Read is the stamp of the desk&rsquo;s own feed, in UTC and in the desk&rsquo;s own format, when this page was built. The live figures are on each desk&rsquo;s page.</p></section>')

def body(rows):
    return INTRO + '<section>' + chart(rows) + '</section>' + table(rows) + (
        '<section class="legal"><h2>How a desk joins</h2><p>A desk joins this page when its feed carries its stated figure beside the delivered one, with an interval and an outcome. '
        'Desks being built join on the first build after they ship. Every number here comes from a desk feed or a ledger row, and the page is checked against both before it is released.</p></section>')

CSS = ('.fcx{margin:6px 0 0;padding:14px 14px 10px;background:var(--fcx-bg);color:var(--fcx-ink);border:1px solid var(--fcx-line);border-radius:2px;'
       '--fcx-bg:#f7f0e0;--fcx-ink:#1a1208;--fcx-mid:#5a4830;--fcx-line:#d9c9a3;--fcx-mark:#8a6410;--fcx-zero:#1a1208}'
       '@media (prefers-color-scheme:dark){.fcx{--fcx-bg:#1c1710;--fcx-ink:#efe5cf;--fcx-mid:#cbbf9f;--fcx-line:#4a3d26;--fcx-mark:#b08a2c;--fcx-zero:#efe5cf}.fcx a{color:#efe5cf}}'
       '.fcx-cap{font:600 13.5px sans-serif;color:var(--fcx-ink);margin:0 0 6px}.fcx-key{font:500 12.5px sans-serif;color:var(--fcx-mid);margin:0 0 8px;display:flex;gap:16px;flex-wrap:wrap}'
       '.fcx-k{display:inline-flex;align-items:center;gap:6px}.fcx-k .fcx-d{position:static;transform:none;display:inline-block}'
       '.fcx-r{display:grid;grid-template-columns:minmax(150px,34%) 1fr 104px;gap:10px;align-items:center;min-height:24px;border-radius:2px}'
       '.fcx-r[tabindex]:hover,.fcx-r[tabindex]:focus{background:var(--fcx-line);outline:none}.fcx-r[tabindex]:focus-visible{outline:2px solid var(--fcx-mark)}'
       '.fcx-l{font:500 12.5px/1.3 sans-serif;color:var(--fcx-ink)}.fcx-o{font:600 11.5px sans-serif;letter-spacing:.03em;color:var(--fcx-ink)}'
       '.fcx-s{position:relative;height:22px;margin:0 14px}'
       '.fcx-ax .fcx-s{height:18px;border-bottom:1px solid var(--fcx-line)}'
       '.fcx-tick{position:absolute;top:0;transform:translateX(-50%);font:500 11px sans-serif;color:var(--fcx-mid);white-space:nowrap}'
       '.fcx-g{position:absolute;top:0;bottom:0;width:1px;background:var(--fcx-line)}.fcx-z{position:absolute;top:-2px;bottom:-2px;width:1px;background:var(--fcx-zero)}'
       '.fcx-i{position:absolute;top:50%;height:2px;margin-top:-1px;background:var(--fcx-mark);border-radius:1px}'
       '.fcx-d{position:absolute;top:50%;width:9px;height:9px;transform:translate(-50%,-50%);background:var(--fcx-mark);box-shadow:0 0 0 2px var(--fcx-bg)}'
       '.fcx-d.c{border-radius:50%}.fcx-d.p{width:8px;height:8px;transform:translate(-50%,-50%) rotate(45deg);border-radius:1px}'
       '.fcx-h{font:600 12.5px sans-serif;letter-spacing:.06em;margin:12px 0 2px;color:var(--fcx-ink)}.fcx-h span{font-weight:500;letter-spacing:0;color:var(--fcx-mid);margin-left:6px}'
       '.fcx-c{display:block;font-weight:500;letter-spacing:0;color:var(--fcx-mid);margin:1px 0 0}.fcx-h .fcx-c{margin-left:0}.fcx-h a{color:var(--fcx-ink)}.fcx-t td{font-size:13.5px}'
       '@media(max-width:700px){.fcx{padding:10px 8px}.fcx-r{grid-template-columns:1fr 96px;gap:2px 6px}.fcx-o{font-size:10.5px;letter-spacing:0}.fcx-l{grid-column:1/-1}.fcx-ax .fcx-l{display:none}}'
       '@media (forced-colors:active){.fcx-d,.fcx-i,.fcx-z{background:CanvasText;forced-color-adjust:none}}')

MEMBER_LINK = '<p class="meta"><a href="/forecasters">FORECASTERS</a>: this desk beside the other public forecasters we score, on one axis.</p>'

def add_pages(PAGES, page, hero_slim, HOME=None, refresh_feeds=True):
    """The one hook build_site.py calls. Refreshes the snapshots, renders /forecasters, links it from each member desk, writes rows.json."""
    if refresh_feeds:
        st = refresh(); print('  forecasters feeds:', ', '.join('%s %s' % (k, v.split(':')[0]) for k, v in sorted(st.items())))
    rows, held = collect()
    if not rows: raise SystemExit('BUILD REFUSED: forecasters: no member rows')
    shown = sorted({r['desk'] for r in rows})
    desc = 'Every public forecaster the Heuremen LLC desks score, on one axis: stated coverage or stated chance against what happened, with each desk\'s interval and its own outcome label.'
    PAGES[PATH] = page(PATH, 'FORECASTERS | Stated Against Delivered, One Axis | Heuremen LLC', desc, body(rows), hero_slim('FORECASTERS &middot; Stated Against Delivered, One Axis'))
    if HOME is not None: HOME[PATH] = '/hermes'
    pages = sorted({r['page'] for r in rows})
    for p in pages:
        if p in PAGES and '</main>' in PAGES[p] and 'href="/forecasters"' not in PAGES[p]:
            i = PAGES[p].rfind('</main>'); PAGES[p] = PAGES[p][:i] + MEMBER_LINK + PAGES[p][i:]
    json.dump({'built': D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'shown': shown, 'held': held,
               'rows': [{k: r[k] for k in ('desk', 'slug', 'page', 'source', 'kind', 'scale', 'note', 'ours', 'cells', 'nums', 'text', 'pos')} for r in rows]},
              open(ROWS, 'w'), ensure_ascii=False, indent=1)
    print('forecasters: %d rows from %s, held %s' % (len(rows), ', '.join(shown), ', '.join(sorted({h['desk'] for h in held})) or 'none'))
    return rows


# ---------------------------------------------------------------- gate
_RC = re.compile(r'<a class="rcpt"[^>]*>[^<]*</a>')
def _txt(h): return html.unescape(re.sub(r'<[^>]+>', '', _RC.sub('', h))).strip()

def _sign_ok(out, pos):
    """The desk's label against the drawn interval: ABOVE wholly right of zero, BELOW wholly left, CONSISTENT holds zero. A flipped axis fails here."""
    if out == 'ABOVE': return pos['lo'] > 0
    if out == 'BELOW': return pos['hi'] < 0
    if out == 'CONSISTENT': return pos['lo'] <= 0 <= pos['hi']
    return out == 'CANNOT_TELL'

def gate():
    """Every number on /forecasters traces to a desk feed snapshot or a live ledger row, re-derived from members.json. Refuses on any miss."""
    errs = []
    try: built = json.load(open(ROWS))
    except Exception as e: print('FORECASTERS GATE: no rows.json, run the build first (%s)' % e); return 1
    for k, v in LAKE.items():
        if re.search(r'\d', v): errs.append('label %r has a digit' % v)
    for name, txt in (('intro', INTRO), ('member link', MEMBER_LINK), ('our-reading line', OURS)):
        if re.search(r'\d', _txt(txt)): errs.append('digit in the %s copy' % name)
    # 1 re-derive every row from members.json and the snapshots, and compare with what the build wrote
    fresh, held = collect()
    if [(r['desk'], r['text']) for r in fresh] != [(r['desk'], r['text']) for r in built['rows']]: errs.append('rows re-derived from members.json and the snapshots differ from the built rows')
    for n, r in enumerate(fresh):
        for c, (t, refs) in r['cells'].items():
            if re.search(r'\d', literal((t, refs))): errs.append('row %d %s: digit in literal text %r' % (n, c, t))
            for x in refs:
                if x[0] == 'l' and x[1] not in ledger(): errs.append('row %d: ledger row %s missing' % (n, x[1]))
        # the printed cells and the drawn position read the same numbers
        nm = r['nums']; ce = r['cells']
        if nm['stated'] not in ce['stated'][1]: errs.append('row %d: printed stated and drawn stated read different numbers' % n)
        if nm['delivered'] not in ce['delivered'][1]: errs.append('row %d: printed delivered and drawn delivered read different numbers' % n)
        if ce['interval'][1] != [nm['lo'], nm['hi']]: errs.append('row %d: printed interval and drawn interval read different numbers' % n)
        if not _sign_ok(r['text']['outcome'], r['pos']): errs.append('row %d (%s %s): label %s does not sit where the drawn interval sits %r' % (n, r['desk'], r['text']['item'], r['text']['outcome'], r['pos']))
        if r['text']['outcome'] not in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL'): errs.append('row %d: outcome %r is not one of the four' % (n, r['text']['outcome']))
    # 2 the built page holds exactly these rows, cell by cell, and nothing else with a digit
    p = os.path.join(HERE, 'forecasters.html')
    if not os.path.exists(p): errs.append('no forecasters.html')
    else:
        doc = open(p, encoding='utf-8').read(); main = doc[doc.find('<main'):doc.rfind('</main>')]
        head = doc[:doc.find('<main')]
        for tag in re.findall(r'<title>(.*?)</title>|<meta name="description" content="([^"]*)"', head):
            for x in tag:
                if x and re.search(r'\d', html.unescape(x)): errs.append('digit in title or description %r' % x[:60])
        brier = any('brier' in r['text'] for r in fresh)
        cols = ['desk', 'item', 'counts', 'stated', 'delivered', 'interval', 'outcome'] + (['brier'] if brier else []) + ['read']
        want = [[_txt(E(r['text'].get(c, 'not published'))) for c in cols] for r in fresh]
        got = [[_txt(td) for td in re.findall(r'<td>(.*?)</td>', tr, re.S)] for tr in re.findall(r'<tr><td>(.*?)</tr>', main, re.S)]
        got = [[_txt(x) for x in re.findall(r'<td>(.*?)</td>', '<tr><td>' + tr + '</tr>', re.S)] for tr in re.findall(r'<tr><td>(.*?)</tr>', main, re.S)]
        if got != want: errs.append('page table differs from the rows, cell by cell (%d rows on page, %d derived)' % (len(got), len(want)))
        a, b, step = domain(fresh)
        tk = re.findall(r'<span class="fcx-tick" style="left:([^"]+)">(.*?)</span>', main)
        if [(x, html.unescape(y)) for x, y in tk] != [(_x(t, a, b), html.unescape(tick_label(t))) for t in ticks(a, b, step)]: errs.append('axis ticks do not match the axis rule')
        if re.findall(r'<span class="fcx-d [cp]" style="left:([^"]+)">', main) != [_x(r['pos']['gap'], a, b) for r in fresh]: errs.append('chart points do not match the source positions')
        if re.findall(r'<span class="fcx-i" style="([^"]+)">', main) != [_ival_style(r['pos'], a, b) for r in fresh]: errs.append('chart intervals do not match the source positions')
        zs = set(re.findall(r'<span class="fcx-z" style="left:([^"]+)">', main))
        if zs != {_x(0, a, b)}: errs.append('zero line is not at zero')
        if [html.unescape(x) for x in re.findall(r'<div class="fcx-r" tabindex="0" title="([^"]*)"', main)] != [_tip(r) for r in fresh]: errs.append('chart hover text differs from the rows')
        if [_txt(x) for x in re.findall(r'<span class="fcx-l">(.*?)</span>', main) if _txt(x)] != [r['text']['item'] for r in fresh]: errs.append('chart labels differ from the rows')
        if [_txt(x) for x in re.findall(r'<span class="fcx-o">(.*?)</span>', main) if _txt(x)] != [r['text']['outcome'] for r in fresh]: errs.append('chart outcomes differ from the rows')
        hd = [_txt(x) for x in re.findall(r'<div class="fcx-h">(.*?)</div>', main, re.S)]
        last = None; wh = []
        for r in fresh:
            if r['desk'] != last: wh.append(_txt(_header(r))); last = r['desk']
        if hd != wh: errs.append('chart desk headers differ from the rows')
        # strip the figure and the table, then nothing left inside main may carry a digit except the blocks build_site.py adds to every page
        rest = re.sub(r'<figure class="fcx".*?</figure>', '', main, flags=re.S)
        rest = re.sub(r'<table.*?</table>', '', rest, flags=re.S)
        rest = re.sub(r'<(script|style|textarea)[^>]*>.*?</\1>', '', rest, flags=re.S)
        for blk in SITE_BLOCKS: rest = re.sub(blk, '', rest, flags=re.S)
        for m in re.finditer(r'\d', _txt(rest)):
            t = _txt(rest); errs.append('untraced digit in copy: %r' % t[max(0, m.start() - 50): m.end() + 20]); break
    for e in errs[:30]: print('  FORECASTERS', e)
    print(('FORECASTERS GATE: REFUSED, %d problems' % len(errs)) if errs else 'FORECASTERS GATE: every number on /forecasters traces to a desk feed or a ledger row (%d rows from %s)' % (len(fresh), ', '.join(sorted({r['desk'] for r in fresh}))))
    return 1 if errs else 0

# blocks build_site.py adds inside every page's main (filled in after the first full build: data links, page dates, the hero and the like)
SITE_BLOCKS = []


if __name__ == '__main__':
    if '--gate' in sys.argv: sys.exit(gate())
    if '--dry' in sys.argv:
        if '--refresh' in sys.argv: print(refresh())
        rows, held = collect()
        for r in rows: print(r['desk'], '|', ' | '.join(r['text'][c] for c in CELLS[1:]), '|', r['pos'])
        print('held:', held)
