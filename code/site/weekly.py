#!/usr/bin/env python3
"""weekly.py: the weekly changes page, /week and /week/<yyyy-ww> (10 Nov 2026).

A week runs from Tuesday 00:00 US Eastern to the next Tuesday 00:00 (owner's word, 10 Nov 2026: the newsletter goes out every Tuesday and each
edition covers Tuesday to Tuesday). Its slug is the ISO year and week number of the Tuesday that starts it, so 2026-46 is 10 to 17 November 2026.

What a week lists, all of it read from records, nothing written by hand:
  Headline changes   every live_value ledger row (ledger/live_headlines.py) written in the week that follows an earlier value row of the same desk:
                     the desk, the previous value and outcome, the new ones, the interval printed with the new value, the time and a link.
                     Superseded rows are read too, so a desk that changed twice in a week shows both changes.
  First values       a desk's first live_value row (the baseline under the change rule), with its value, interval, time and link.
  New desks          a desk page (build_site.py DESKS) whose page first appears in the public repository in the week (git history of
                     public_mirror/indahl.ai). Pages present in that repository's first commit carry no date and are never listed.
  Corrections        none yet: indahl.ai has no /corrections page. When it exists, its rows belong here.

  weekly.py tick            tick-bus rider: renders /week and any week that ended since the last build into the worker's KV, only on change
  weekly.py print [SLUG]    the page body (HTML) of a week, default the current one
  weekly.py text [SLUG]     the plain-text edition of a week, default the last complete one (what newsletter_send.py sends)
  weekly.py selftest        week boundaries and the change pairs on planted rows
build_site.py calls apply(PAGES, page, hero_slim, DESKS) once per build. Python 3.9, standard library only."""
import os, sys, json, re, html, hashlib, subprocess, datetime as D
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(ROOT, 'ledger'); MIRROR = os.path.join(ROOT, 'public_mirror', 'indahl.ai')
STATE = os.path.join(HERE, 'week_state.json'); TICK_STATE = os.path.join(HERE, '.week_tick.json')
W = os.path.join(ROOT, 'cloudflare-workers', 'heuremen-door'); NS = 'ecb59d96b07c43bdac14271687eae5af'   # IRIS_BENCH, the KV the live feeds use
SITE = 'https://indahl.ai'; ET = ZoneInfo('America/New_York'); UTC = D.timezone.utc
sys.path.insert(0, LEDGER)
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
e = lambda s: html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------------------------------------------- weeks
def week_start(t):
    """The Tuesday 00:00 US Eastern that starts the week holding t (an aware datetime)."""
    l = t.astimezone(ET); d = l.date() - D.timedelta(days=(l.weekday() - 1) % 7)
    return D.datetime(d.year, d.month, d.day, tzinfo=ET)


def slug_of(start):
    y, w, _ = start.date().isocalendar(); return '%d-%02d' % (y, w)


def start_of(slug):
    y, w = (int(x) for x in slug.split('-')); d = D.date.fromisocalendar(y, w, 2)
    return D.datetime(d.year, d.month, d.day, tzinfo=ET)


def next_start(start):   # calendar-safe across the daylight saving change
    d = (start + D.timedelta(days=8)).date(); d -= D.timedelta(days=(d.weekday() - 1) % 7); return D.datetime(d.year, d.month, d.day, tzinfo=ET)


def day(t): l = t.astimezone(ET); return '%d %s %d' % (l.day, MON[l.month - 1], l.year)
def when(t): u = t.astimezone(UTC); return '%d %s %d, %02d:%02d UTC' % (u.day, MON[u.month - 1][:3], u.year, u.hour, u.minute)
def span(start): end = next_start(start); return 'Tuesday %s to Tuesday %s' % (day(start), day(end))


# ---------------------------------------------------------------------------------------------------------------- records
def _rows():
    return [json.loads(l) for l in open(os.path.join(LEDGER, 'ledger.jsonl'), encoding='utf-8')]


def _at(r): return D.datetime.fromisoformat(r['history'][0]['at']).astimezone(UTC)


def _bound(show, x):
    if x is None: return ''
    try: x = float(x)
    except Exception: return str(x)
    return ('%.0f%%' % (100 * x)) if show in ('pct', 'n_of', 'of_minus_n') else ('%.1f%%' % (100 * x) if show == 'pct1' else '%g' % x)


def _show(rd): o = rd.get('outcome'); return rd.get('display', '') + ((' (' + WORD[o] + ')') if o in WORD else '')


def headline_events(rows=None):
    """Every value row as an event: kind 'change' (with its previous row) or 'first' (the desk's baseline)."""
    import live_headlines as LH
    rows = _rows() if rows is None else rows; out = []
    for slug, spec in LH.DESKS.items():
        vals = sorted((r for r in rows if r.get('kind') == 'live_value' and r.get('live_of') == 'live.%s.headline' % slug and r.get('reading')), key=_at)
        for i, cur in enumerate(vals):
            c = cur['reading']; iv = ('%s to %s' % (_bound(spec['show'], c['lo']), _bound(spec['show'], c['hi']))) if c.get('lo') is not None and c.get('hi') is not None else ''
            ev = dict(kind='first' if i == 0 else 'change', desk=spec['name'], slug=slug, at=_at(cur), now=_show(c), interval=iv, stamp=c.get('stamp') or '', id=cur['id'])
            if i:
                p = vals[i - 1]['reading']; ev['before'] = _show(p)
                po, co = p.get('outcome'), c.get('outcome')
                if po in WORD and co in WORD and po != co: ev['why'] = 'The outcome changed from %s to %s.' % (WORD[po], WORD[co])
                elif spec['kind'] == 'interval' and p.get('lo') is not None: ev['why'] = 'The number moved outside the interval printed with the previous value, %s to %s.' % (_bound(spec['show'], p['lo']), _bound(spec['show'], p['hi']))
                elif spec['kind'] == 'set': ev['why'] = 'A figure that the desk\'s stated rule reads changed.'
                else: ev['why'] = 'The headline changed under the desk\'s rule.'
            out.append(ev)
    return out


def _mirror_firsts(names):
    """path -> first commit time of its page in the public repository, for pages added after that repository's first commit."""
    if not os.path.isdir(os.path.join(MIRROR, '.git')): return {}
    try:
        root = subprocess.run(['git', '-C', MIRROR, 'rev-list', '--max-parents=0', 'HEAD'], capture_output=True, text=True).stdout.split()
        log = subprocess.run(['git', '-C', MIRROR, 'log', '--diff-filter=A', '--format=C %H %cI', '--name-only', '--', *names.values()], capture_output=True, text=True).stdout
    except Exception: return {}
    out = {}; inv = {v: k for k, v in names.items()}; cur = None
    for ln in log.splitlines():
        if ln.startswith('C '): _, sha, t = ln.split(' ', 2); cur = None if sha in root else D.datetime.fromisoformat(t).astimezone(UTC)
        elif ln.strip() in inv and cur is not None: out[inv[ln.strip()]] = cur   # newest first, so the last one seen is the first add
    return out


def load_state():
    try: return json.load(open(STATE))
    except Exception: return {'desks': [], 'first_seen': {}}


def update_state(desks, now=None):
    """desks: [(path, name, what)]. A desk's first-seen time is its first add in the public repository, else the first build that lists it."""
    now = now or D.datetime.now(UTC); st = load_state(); fs = st.get('first_seen', {})
    names = {p: p.strip('/') + '.html' for p, n, w in desks}
    mf = _mirror_firsts({p: f for p, f in names.items() if p not in fs})
    for p, n, w in desks:
        if p in fs: continue
        if p in mf: fs[p] = mf[p].strftime('%Y-%m-%dT%H:%M:%SZ')
        elif st.get('desks'): fs[p] = now.strftime('%Y-%m-%dT%H:%M:%SZ')   # new since the last build and not yet in the public repository
        else: fs[p] = None                                                 # first run: a page with no dated first add is never listed as new
    st = {'desks': [list(x) for x in desks], 'first_seen': fs}
    json.dump(st, open(STATE, 'w'), indent=1, sort_keys=True); return st


def desk_events(st=None):
    st = st or load_state(); names = {p: (n, w) for p, n, w in st.get('desks', [])}; out = []
    for p, t in st.get('first_seen', {}).items():
        if t and p in names:
            out.append(dict(kind='desk', desk=html.unescape(names[p][0]), what=html.unescape(names[p][1]), path=p, at=D.datetime.fromisoformat(t.replace('Z', '+00:00'))))
    return out


def events(rows=None, st=None):
    return sorted(headline_events(rows) + desk_events(st), key=lambda x: x['at'])


def week_events(slug, evs=None):
    a = start_of(slug); b = next_start(a); evs = events() if evs is None else evs
    return [x for x in evs if a <= x['at'] < b]


def weeks(evs=None, now=None):
    """Every week slug from the first week with an event through the current week, oldest first."""
    now = now or D.datetime.now(UTC); evs = events() if evs is None else evs
    cur = week_start(now); s = week_start(min(x['at'] for x in evs)) if evs else cur; out = []
    while s <= cur: out.append(slug_of(s)); s = next_start(s)
    return out


def current_slug(now=None): return slug_of(week_start(now or D.datetime.now(UTC)))
def last_complete_slug(now=None): return slug_of(week_start(week_start(now or D.datetime.now(UTC)) - D.timedelta(hours=1)))


# ---------------------------------------------------------------------------------------------------------------- render
def _link(x): return SITE + ('/' + x['slug'] if x['kind'] != 'desk' else x['path'])
RECEIPTS = os.path.join(W, 'public', 'r')
def _rcpt(x):   # the ledger row's receipt page, when the build has made it (a row written since the last build has none yet)
    return (' <a class="wkr" href="/r/%s">Receipt</a>' % e(x['id'])) if x.get('id') and os.path.exists(os.path.join(RECEIPTS, x['id'] + '.html')) else ''


def body(slug, evs=None, now=None, all_weeks=None):
    now = now or D.datetime.now(UTC); a = start_of(slug); ev = week_events(slug, evs)
    cur = slug == current_slug(now)
    ch = [x for x in ev if x['kind'] == 'change']; fi = [x for x in ev if x['kind'] == 'first']; dk = [x for x in ev if x['kind'] == 'desk']
    o = ['<!--WEEK--><section class="legal week">']
    o.append('<p>%s. %s</p>' % (e(span(a)), 'This week is still open and this page adds each change as it is recorded.' if cur else 'This week is closed.'))
    o.append('<p class="meta">An entry is added only when a desk headline makes a material change under the ledger rule, when a desk records its first value under that rule, or when a new desk is published. Times are UTC.</p>')
    if ch:
        o.append('<h2>Headline changes</h2><ul class="wk">')
        for x in ch:
            o.append('<li><a href="%s">%s</a>: %s to %s%s. %s <span class="wkt">%s</span>%s</li>' % (e(_link(x)), e(x['desk']), e(x['before']), e(x['now']),
                     (', interval ' + e(x['interval'])) if x['interval'] else '', e(x['why']), e(when(x['at'])), _rcpt(x)))
        o.append('</ul>')
    if fi:
        o.append('<h2>First values under the change rule</h2><ul class="wk">')
        for x in fi:
            o.append('<li><a href="%s">%s</a>: %s%s. <span class="wkt">%s</span>%s</li>' % (e(_link(x)), e(x['desk']), e(x['now']), (', interval ' + e(x['interval'])) if x['interval'] else '', e(when(x['at'])), _rcpt(x)))
        o.append('</ul>')
    if dk:
        o.append('<h2>New desks</h2><ul class="wk">')
        for x in dk:
            o.append('<li><a href="%s">%s</a>: %s. <span class="wkt">%s</span></li>' % (e(_link(x)), e(x['desk']), e(x['what'].rstrip('.')), e(when(x['at']))))
        o.append('</ul>')
    if not ev: o.append('<p>No changes have been recorded in this week%s.</p>' % (' so far' if cur else ''))
    o.append('<!--NEWS--><h2>By email</h2><p>The sign-up form at the foot of this page emails this page every Tuesday. The same form can send new desks and new data, and outcome changes on the desks you pick.</p><!--/NEWS-->')   # 10 Nov 2026: the one form is in the footer (alerts.py signup_form)
    o.append('<h2>Newsletter</h2><p>Every issue of the newsletter, as published: <a href="/newsletter">indahl.ai/newsletter</a>.</p>')   # 10 Nov 2026 (newsletter_pages.py)
    past = [s for s in (all_weeks or weeks(evs, now)) if s != slug]
    if past:
        o.append('<h2>Other weeks</h2><ul class="wk">' + ''.join('<li><a href="%s">%s</a></li>' % ('/week' if s == current_slug(now) else '/week/' + s, e(span(start_of(s)))) for s in reversed(past)) + '</ul>')
    o.append('</section><!--/WEEK-->')
    return ''.join(o)


def text(slug, evs=None, now=None):
    """The plain-text edition: the same entries as the page, one per paragraph."""
    now = now or D.datetime.now(UTC); a = start_of(slug); ev = week_events(slug, evs)
    L = ['Weekly changes on indahl.ai', span(a) + '.', '', 'Page: %s/week/%s' % (SITE, slug), '']
    sec = [('Headline changes', [x for x in ev if x['kind'] == 'change'], lambda x: '%s: %s to %s%s. %s %s.' % (x['desk'], x['before'], x['now'], (', interval ' + x['interval']) if x['interval'] else '', x['why'], when(x['at']))),
           ('First values under the change rule', [x for x in ev if x['kind'] == 'first'], lambda x: '%s: %s%s. %s.' % (x['desk'], x['now'], (', interval ' + x['interval']) if x['interval'] else '', when(x['at']))),
           ('New desks', [x for x in ev if x['kind'] == 'desk'], lambda x: '%s: %s. %s.' % (x['desk'], x['what'].rstrip('.'), when(x['at'])))]
    for h, xs, f in sec:
        if not xs: continue
        L += [h, '']
        for x in xs: L += [f(x), _link(x), '']
    if not ev: L += ['No changes were recorded in this week.', '']
    return '\n'.join(L).rstrip() + '\n'


# 10 Nov 2026: the footer newsletter field is gone. The one sign-up form (newsletter, updates, alerts) is built in alerts.py and posts to /signup.
CSS = """
.week ul.wk{padding-left:18px}.week ul.wk li{margin:6px 0;line-height:1.45}.wkt{color:var(--mid);font-size:14px;white-space:nowrap}.wkr{font-size:14px;margin-left:8px}
"""


def _page(slug, page, hero_slim, evs, now, all_weeks, current):
    a = start_of(slug); path = '/week' if current else '/week/' + slug
    title = ('Weekly Changes | Heuremen LLC' if current else 'Weekly Changes, Week of %s | Heuremen LLC' % day(a))
    desc = 'What changed on indahl.ai in the week from Tuesday %s: headline changes under the ledger rule, first values and new desks, each with its time and link.' % day(a)
    return page(path, title, desc, body(slug, evs, now, all_weeks), hero_slim('Weekly Changes', span(a)))


def apply(PAGES, page, hero_slim, DESKS, now=None):
    """Build hook: /week and every past week. (The sign-up form in every footer is alerts.footer, since 10 Nov 2026.)"""
    now = now or D.datetime.now(UTC)
    desks = []; seen = set()
    for d, ds in DESKS.items():
        for p, n, w in ds:
            if p in PAGES and p not in seen: seen.add(p); desks.append((p, n, w))
    st = update_state(desks, now); evs = events(st=st); ws = weeks(evs, now); cur = current_slug(now)
    for s in ws: PAGES['/week' if s == cur else '/week/' + s] = _page(s, page, hero_slim, evs, now, ws, s == cur)
    # the version stamps on the stylesheet and scripts are copied from the home page, since these pages are built after the stamps were set
    ref = PAGES.get('/', ''); stamps = dict(re.findall(r'(/[\w./-]+\.(?:css|js))\?v=([0-9a-f]+)', ref))
    for k in list(PAGES):
        d = PAGES[k]
        if k == '/week' or k.startswith('/week/'):
            d = d.replace('@@CSSV@@', stamps.get('/style.css', ''))
            d = re.sub(r'(/[\w./-]+\.(?:css|js))\?v=[0-9a-f@A-Z]+', lambda m: m.group(1) + '?v=' + stamps.get(m.group(1), m.group(0).split('?v=')[1]), d)
        PAGES[k] = d
    return ws


JS_HASH_SRC = 'newsletter.js v2'   # no page loads /newsletter.js since 10 Nov 2026 (the one form uses /signup.js, alerts.py); kept served for cached pages


# ---------------------------------------------------------------------------------------------------------------- tick (rider)
def render_from_shell(slug, now=None):
    """The built week.html is the shell (header, nav, footer as last shipped). The week body is swapped in, and for a past week the title,
    description and canonical address are set to that week."""
    sh = open(os.path.join(HERE, 'week.html'), encoding='utf-8').read()
    now = now or D.datetime.now(UTC); evs = events(); ws = weeks(evs, now)
    i, j = sh.index('<!--WEEK-->'), sh.index('<!--/WEEK-->') + len('<!--/WEEK-->')
    doc = sh[:i] + body(slug, evs, now, ws) + sh[j:]
    if slug != current_slug(now):
        a = start_of(slug)
        doc = doc.replace('Weekly Changes | Heuremen LLC', 'Weekly Changes, Week of %s | Heuremen LLC' % day(a))
        doc = re.sub(r'(https://indahl\.ai/week)(["<])', r'\1/' + slug + r'\2', doc)
    m = re.search(r'<p class="hsub">(.*?)</p>', doc)
    if m: doc = doc.replace(m.group(0), '<p class="hsub">%s</p>' % e(span(start_of(slug))), 1)
    return doc


def tick(now=None):
    """Put /week (and each week that ended since the last build) into KV when it differs from what was last put. The worker serves the KV
    copy before the built page. One KV write per changed page, so a quiet week costs nothing."""
    now = now or D.datetime.now(UTC)
    if not os.path.exists(os.path.join(HERE, 'week.html')): print('weekly: no built week.html yet, nothing put'); return
    try: ts = json.load(open(TICK_STATE))
    except Exception: ts = {}
    built = set(re.findall(r"'/week/(\d{4}-\d{2})'", open(os.path.join(HERE, 'pages.js')).read())) if os.path.exists(os.path.join(HERE, 'pages.js')) else set()
    cur = current_slug(now); todo = [('week_current', cur)] + [('week_' + s, s) for s in weeks(now=now) if s != cur and s not in built]
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    for key, s in todo:
        doc = render_from_shell(s, now); h = hashlib.sha256(doc.encode()).hexdigest()[:16]
        if ts.get(key) == h: continue
        p = os.path.join(HERE, '.week_put.html'); open(p, 'w', encoding='utf-8').write(doc)
        r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', key, '--path', p, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
        ok = r.returncode == 0; print('weekly: %s (%s) %s' % (key, s, 'put' if ok else 'put FAILED'))
        if ok: ts[key] = h
    json.dump(ts, open(TICK_STATE, 'w'))


# ---------------------------------------------------------------------------------------------------------------- selftest
def selftest():
    t = lambda *a: D.datetime(*a, tzinfo=ET)
    assert week_start(t(2026, 11, 10, 0, 0)) == t(2026, 11, 10) and week_start(t(2026, 11, 9, 23, 59)) == t(2026, 11, 3)
    assert week_start(t(2026, 11, 16, 23, 0)) == t(2026, 11, 10) and slug_of(t(2026, 11, 10)) == '2026-46' and start_of('2026-46') == t(2026, 11, 10)
    assert next_start(t(2026, 10, 27)) == t(2026, 11, 3)   # across the end of daylight saving time (1 Nov 2026)
    assert last_complete_slug(t(2026, 11, 10, 9, 0).astimezone(UTC)) == '2026-45' and current_slug(t(2026, 11, 10, 9, 0).astimezone(UTC)) == '2026-46'
    h = lambda at, rid, rd: dict(kind='live_value', live_of='live.airq.headline', id=rid, reading=rd, history=[dict(at=at)], status='superseded')
    rows = [h('2026-11-10T07:00:00-05:00', 'a', dict(display='93%', outcome='ABOVE', lo=0.87, hi=0.96, stamp='s')),
            h('2026-11-12T07:00:00-05:00', 'b', dict(display='97%', outcome='ABOVE', lo=0.94, hi=0.99, stamp='s')),
            h('2026-11-13T07:00:00-05:00', 'c', dict(display='60%', outcome='CANNOT_TELL', lo=0.4, hi=0.8, stamp='s'))]
    ev = [x for x in headline_events(rows) if x['slug'] == 'airq']
    assert [x['kind'] for x in ev] == ['first', 'change', 'change'] and ev[1]['before'] == '93% (above)' and 'outside the interval' in ev[1]['why'] and 'changed from above to cannot tell' in ev[2]['why']
    assert ev[1]['interval'] == '94% to 99%'
    assert len(week_events('2026-46', ev)) == 3 and not week_events('2026-45', ev)
    assert '@' not in text('2026-46', ev, t(2026, 11, 18).astimezone(UTC))
    print('weekly selftest: Tuesday weeks, slugs, the daylight saving change and the change pairs read as planted')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['tick']: tick()
    elif a[:1] == ['print']: print(body(a[1] if len(a) > 1 else current_slug()))
    elif a[:1] == ['text']: print(text(a[1] if len(a) > 1 else last_complete_slug()), end='')
    elif a[:1] == ['selftest']: selftest()
    else: print(__doc__)
