"""alerts.py -- email alerts on indahl.ai (10 Nov 2026). Build hook for build_site.py, called once after the brand pages are built.

  apply(PAGES, page, hero_slim, HOME, bb, rows, desks=DESKS)
    - the desks that send OUTCOME changes: every live-headline desk (ledger/live_headlines.py DESKS) whose rule can write a value row after
      its baseline (a flip rule with no outcome never can) and whose page is built
    - (10 Nov evening, owner: "don't we have a LOT more than what's listed here?") every other desk and every division page sends UPDATES:
      one email when the page's published data changes. The change signal per page is in SIGNALS below (a public feed's data fields, or the
      visible text of the page's <main> as published), never a timestamp alone.
    - (10 Nov evening, owner: "the live ones specifying when they alert") each desk carries how often we check it, from the tick-bus rider
      that reads it (watch/tick_bus.py, interval in ticks times the median tick of watch/ticks.log). A desk with a public feed must have a
      check no slower than the feed's freshness limit (nodes_repo/drift/targets.json, the limits /seat reads): the build is REFUSED otherwise.
    - the organisations that can send alerts: a brand page with rows on at least one outcome desk
    - writes alerts_list.js (the worker's lists) and alerts_map.json (the same, read by alerts_send.py), and builds /alerts
  footer(PAGES)   the one sign-up form in every footer: newsletter, new desks and new data, every desk, and on a desk, division or brand page
    that desk, division or organisation, ticked. Call it once after every page is built.
The worker side is alerts.js (/signup, and newsletter.js for the newsletter box). The sender is alerts_send.py, a tick-bus rider. Python 3.9+."""
import os, sys, json, html, hashlib, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(B, 'ledger'))
E = html.escape
MAP = os.path.join(HERE, 'alerts_map.json'); LIST_JS = os.path.join(HERE, 'alerts_list.js')
JS_HASH_SRC = 'signup.js v3'   # bump with a change to the script served at /signup.js (alerts.js), so browsers fetch the new one
TICK_BUS = os.path.join(B, 'watch', 'tick_bus.py'); TICKS = os.path.join(B, 'watch', 'ticks.log'); TARGETS = os.path.join(B, 'nodes_repo', 'drift', 'targets.json')

# 10 Nov 2026 (owner's word): ONE sign-up form, in the footer of every page and on /alerts. Boxes: nl (weekly newsletter, at once), up (new desks
# and new data), all (outcome changes on every desk), d=<desk> (outcome changes), u=<page> (updates), dv=<division> (everything in it),
# o=<organisation>, and f = delivery (now, day, week).
CSS = """
.su{max-width:640px;margin:0 auto 12px;padding:4px 0 12px;border-bottom:1px solid #4a3d24;text-align:left}.su-h{margin:0 0 6px;font-weight:600;color:#efe5cf;font-size:15px}
.su-row{display:flex;gap:8px;margin:0 0 6px}.su input[type=email]{font:inherit;font-size:15px;padding:6px 8px;border:1px solid #4a3d24;background:#fffaf0;color:#1a1208;flex:1 1 auto;min-width:0;max-width:340px}
.su .btn{flex:none;background:var(--lit);color:var(--cave);padding:6px 14px;border:0;font:inherit;font-size:15px;cursor:pointer}.su .btn:hover{background:#f3e2a0}
.su-c{display:flex;flex-wrap:wrap;gap:2px 18px;margin:0 0 4px}.su-c label{display:inline-flex;align-items:flex-start;gap:6px;font-size:13.5px;line-height:1.35;color:#efe5cf;padding:3px 0}.su-c input{margin:2px 0 0;flex:none}
.su-f{display:block;font-size:13px;color:#cbbf9f;margin:2px 0 4px}.su-f select{font:inherit;font-size:13px;padding:2px 4px;margin-left:4px;max-width:100%}
.su-say{font-size:12.5px;color:#cbbf9f;margin:4px 0 0;line-height:1.45}.foot .su-say a{display:inline;padding:0;font-size:inherit;color:#efe5cf;text-decoration:underline}
.su-msg{margin:6px 0 0;font-weight:600;color:#efe5cf;font-size:14px}.su-msg:empty{display:none}.nl-hp{position:absolute!important;left:-9999px!important;width:1px;height:1px;opacity:0}
main .su{margin:14px 0 10px;border-bottom:0;border-top:1px solid var(--rule);padding-top:12px}main .su-h,main .su-c label,main .su-msg{color:var(--ink)}main .su-say,main .su-f{color:var(--mid)}main .su input[type=email]{border-color:var(--rule);background:var(--paper)}
main .su .btn{background:var(--ink);color:var(--paper)}.su-list{list-style:none;padding:0;margin:4px 0 12px}.su-list li{margin:6px 0;line-height:1.4}.su-list input{vertical-align:-2px;margin:0 4px 0 0}
.ent-q{font:inherit;font-size:15px;padding:6px 8px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:100%;max-width:420px;box-sizing:border-box}
.linkbtn{font:inherit;font-size:13px;padding:1px 8px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);cursor:pointer}#ent-picked{margin:6px 0 10px}
a.fb{display:inline-block;font-size:11.5px;line-height:1.3;padding:0 5px;margin:0 0 0 4px;border:1px solid var(--rule);border-radius:3px;text-decoration:none;color:var(--mid);vertical-align:1px;white-space:nowrap}a.fb:hover{color:var(--ink);border-color:var(--ink)}a.ent{color:inherit}
.su-div{margin:14px 0 4px}.su-dh{margin:0 0 2px;font-weight:600}.su-dh input{vertical-align:-2px;margin:0 6px 0 0}.su-k{display:block;font-size:13px;color:var(--mid)}
@media (max-width:520px){.su-f select{font-size:16px}.su-c{flex-direction:column;gap:0}.su-c label{font-size:14px;padding:5px 0}.su-list li{margin:9px 0}}
"""

# ------------------------------------------------------------------------------------------------ divisions and change signals
DIV_ORDER = ['/qia', '/iris', '/oy', '/atlas', '/hermes']
DIV_NAME = {'/qia': 'QIA', '/iris': 'IRIS', '/oy': 'OY', '/atlas': 'ATLAS', '/hermes': 'HERMES'}
# QIA has no desk list in build_site DESKS: its own page (the audit, the Book and the Braket rows) and its List and Key are its pages.
QIA_PAGES = [('/qia/list', 'THE LIST', 'Every indexed quantum study with its receipt'), ('/qia/key', 'KEY', 'The QIA codes, problem by problem')]

# The change signal of an UPDATE page. 'feeds': public feeds and the data fields of each that count as the page's published data (read times,
# ages and running read counts left out, so a re-read that finds nothing new sends nothing). Every update page is also followed on the visible
# text of its <main> as published (the public mirror of each release), so a new release that changes what the page says sends one email.
# Path syntax: a.b walks keys, x[] walks a list (each item named by its id fields), * walks every key of an object, {a,b} keeps those keys.
SIGNALS = {
    'uptime': {'/uptime/live.json': ['totals', 'vendors[].incidents[].name']},
    'time': {'/time/live.json': ['totals', 'servers[].{outcome,outcome_2}']},
    'cada': {'/cada/live.json': ['resolvers[].checkpoints.*.state']},
    'seat': {'/seat/live.json': ['rolling.*.outcome', 'incidents[].{first,saw}', 'not_matching']},
    'forecast': {'/forecast/live.json': ['measurable.cells[].outcome', 'cells[].outcome']},
    'arxivdrift': {'/arxivdrift/live.json': ['classes.*.n', 'drifted[].{latest,cls}']},
    'wiki': {'/wiki/live.json': ['@all']},
    'social': {'/social/live.json': ['headline.big', 'outcomes.*.outcomes']},
    'predictions': {'/predictions/live.json': ['resolved', 'fortune', 'entries', 'binary.all']},
    'stack': {'/stack/live.json': ['tally.*.n', 'rows[].outcome']},
    'hflicense': {'/hflicense/live.json': ['comparison.*.{n,of,outcome}', 'mixed_list[].note', 'disagree_list[].note']},
    'rank': {'/rank/live.json': ['headline.big', 'claims', 'checks[].{match,mismatch,cannot_tell}']},
    'yo': {'/qia/yo.json': ['adapter'], '/iris/yo.json': ['state', 'result.rows']},
    'iris/lab': {'/iris/live.json': ['done[].title', 'running[].title']},
    'qia': {'/qia/audit.json': ['processors[].{above,cannot_tell,mismatch}', 'flagged[].qubit']},
}
# Desks whose readings can flip back and forth between reads (a time server, a status page, a filter, the outside seat): a change is sent only
# once it has held for this many minutes, so a flip that reverts sends nothing. The label says so.
DWELL = {'time': 60, 'uptime': 60, 'cada': 60, 'seat': 60}
# the tick-bus script that reads each desk, where the folder name alone does not say (folder minus _index otherwise)
RIDER_SLUG = {'caca_index': 'cada', 'bts_index': 'airline', 'status_index': 'uptime', 'now_index': 'predictions', 'iris_index': 'iris/lab',
              'qia_mirror': 'qia', 'qia_queue': 'qia', 'qia_cal': 'qia', 'yo': 'yo'}
LH_EVERY = 12      # ledger/live_headlines.py rides every 12 ticks: an outcome change is written, and so can be sent, at most this often
SENDER_EVERY = 1   # alerts_send.py rides every tick


def riders():
    """{desk slug: smallest rider interval in ticks} from watch/tick_bus.py (live lines only)."""
    out = {}
    for line in open(TICK_BUS, encoding='utf-8').read().splitlines():
        if line.strip().startswith('#'): continue
        for m in re.finditer(r'\((\d+),\s*\[', line):
            seg = line[m.end():].split('#', 1)[0]
            seg = seg[:seg.find(']),') if ']),' in seg else len(seg)]
            paths = [p for p in re.findall(r"bones-forge/([A-Za-z0-9_\-]+)/([A-Za-z0-9_\-\.]+)", seg) if p[0] not in ('qvenv', 'notify_state') and p[1] != 'venv']
            if not paths: continue
            d, f = paths[-1]
            if d in ('watch', 'indahl-ai', 'ledger', 'tools', 'archive', 'gridsong', 'sage_library', 'api_seat', 'public_progress', 'nova_feed', 'bq_index', 'the_show', 'darkwave_daily'): continue
            if d == 'bts_index' and f != 'nas_tick.py': continue
            s = RIDER_SLUG.get(d, d[:-6] if d.endswith('_index') else d)
            out[s] = min(out.get(s, 10 ** 9), int(m.group(1)))
    return out


def tick_minutes():
    tt = []
    for l in open(TICKS).read().splitlines()[-120:]:
        try: tt.append(float(l.split()[3]))
        except (IndexError, ValueError): pass
    gaps = [b - a for a, b in zip(tt, tt[1:]) if b > a]
    return statistics.median(gaps) / 60 if gaps else 5.0


def feed_limits():
    """{desk slug: freshness limit in hours}: the strictest limit /seat holds among the desk's feeds (the feeds in SIGNALS for an update page,
    else /<desk>/live.json)."""
    per = {f: float(lim) for f, lim in json.load(open(TARGETS))['feeds']}
    out = {}
    for f, lim in per.items():
        if f.endswith('/live.json') and f.count('/') == 1: out[f.split('/')[0]] = lim
    for s, fs in SIGNALS.items():
        ls = [per[f.lstrip('/')] for f in fs if f.lstrip('/') in per]
        if ls: out[s] = min(ls)
    out.pop('iris', None)   # /iris/live.json is the LAB queue, named in SIGNALS under iris/lab
    return out


def every_label(m):
    """A plain label for a check interval in minutes, rounded the way a reader says it."""
    if m <= 7: return 'about every 5 minutes'
    if m <= 12: return 'about every 10 minutes'
    if m <= 22: return 'about every 15 minutes'
    if m <= 45: return 'about every 30 minutes'
    if m <= 90: return 'about every hour'
    h = m / 60
    if h < 20: return 'about every %d hours' % round(h)
    if h <= 36: return 'about once a day'
    d = h / 24
    if d < 5: return 'about every %d days' % round(d)
    if d <= 9: return 'about once a week'
    return 'about every %d days' % round(d)


def cadence(slug, mode, rid, tmin, lim):
    """(label, minutes or None, source) for one followable page. Outcome changes: the desk's read, and live_headlines' pass that writes the
    change row. Updates on a feed: the desk's read (the sender looks every tick). Updates on the page alone: when a new version is published."""
    r = rid.get(slug)
    if mode == 'outcome':
        if r is None and slug in lim: m, src = lim[slug] * 60, 'feed limit'
        elif r is None: m, src = LH_EVERY * tmin, 'ledger pass'
        else: m, src = max(r, LH_EVERY) * tmin, 'rider'
        return 'checked ' + every_label(m), round(m), src
    if slug in SIGNALS:
        if r is None and slug in lim: m, src = lim[slug] * 60, 'feed limit'
        elif r is None: m, src = SENDER_EVERY * tmin, 'sender'
        else: m, src = max(r, SENDER_EVERY) * tmin, 'rider'
        if slug in DWELL: return 'checked %s, sent once a change holds for %s' % (every_label(m), {60: 'an hour', 30: 'half an hour'}[DWELL[slug]]), round(m + DWELL[slug]), src
        return 'checked ' + every_label(m), round(m), src
    return 'when we publish a new version', None, 'release'


def check_cadence(items, lim):
    """The gate: a page whose stated check is slower than its feed's freshness limit, or a feed signal on a page /seat does not hold to a
    limit, refuses the build."""
    bad = []
    for s, it in items.items():
        if it['every_min'] is not None and s in lim and it['every_min'] - DWELL.get(s, 0) > lim[s] * 60 * 1.05:
            bad.append('%s states %s (%d min) but its feed limit is %.1f h' % (s, it['every'], it['every_min'], lim[s]))
        for f in SIGNALS.get(s, {}):
            if f.lstrip('/') not in {x for x, _ in json.load(open(TARGETS))['feeds']}: bad.append('%s follows %s, which has no freshness limit' % (s, f))
    if bad: raise SystemExit('BUILD REFUSED: alert cadence: ' + '; '.join(bad[:8]))


# ------------------------------------------------------------------------------------------------ the form
def _box(name, value, label, on):
    return '<label><input type="checkbox" name="%s" value="%s"%s> %s</label>' % (name, E(value), ' checked' if on else '', label)


DELIVERY = [('now', 'as it happens'), ('day', 'in one daily digest'), ('week', 'in one weekly digest on Tuesdays')]


def delivery_select():
    return ('<label class="su-f">Alerts and updates come <select name="f" aria-label="How often alerts and updates come">'
            + ''.join('<option value="%s"%s>%s</option>' % (v, ' selected' if v == 'now' else '', t) for v, t in DELIVERY) + '</select></label>')


def signup_form(extra='', listing=''):
    """The one form. extra: the desk, division or organisation box this page adds (ticked). listing: the full list (on /alerts only)."""
    return ('<form class="su" action="/signup" method="post"><p class="su-h">Email updates</p>'
            '<div class="su-row"><input type="email" name="email" required maxlength="160" autocomplete="email" placeholder="Email address" aria-label="Email address">'
            '<button class="btn" type="submit">Sign up</button></div>'
            '<input class="nl-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<div class="su-c">' + _box('nl', '1', 'Weekly newsletter, every Tuesday', True) + extra
            + _box('up', '1', 'New desks and new data', False) + _box('all', '1', 'Outcome changes on every desk', False) + '</div>' + delivery_select() + listing
            + '<p class="su-say">The newsletter starts at once. The other boxes start only after you confirm by email. Every email has its own one-click unsubscribe link. '
            '<a href="/newsletter">Newsletter issues</a> &middot; ' + ('' if listing else '<a href="/alerts">Every desk and division</a> &middot; ') + '<a href="/privacy#signup">Privacy</a></p>'
            '<p class="su-msg" role="status" aria-live="polite"></p></form>')


def item_box(slug, it):
    if it['mode'] == 'outcome': return _box('d', slug, 'Outcome changes on this desk (%s), %s' % (E(it['name']), E(it['every'])), True)
    if it['mode'] == 'division': return _box('dv', slug, 'Everything in this division (%s)' % E(it['name']), True)
    if it['every_min'] is None: return _box('u', slug, 'Updates to this page (%s), sent %s' % (E(it['name']), E(it['every'])), True)
    return _box('u', slug, 'Updates on this desk (%s), %s' % (E(it['name']), E(it['every'])), True)


def brand_box(slug, name):
    return _box('o', slug, 'Outcome changes on desks with rows about %s' % E(name), True)


# 10 Nov 2026 evening (owner: follow any company or named thing): en=<entity id>, one email when a row about it changes or a new row about it
# appears on any desk. Rows from the desks' feeds are read about every ENT_EVERY minutes; rows on pages change when a new version is published.
ENT_EVERY = 30


def ent_every(e):
    return ('checked ' + every_label(ENT_EVERY)) if e.get('feed') else 'sent when we publish a new version'


def ent_box(i, e, on=True):
    import entities as EN
    return _box('en', i, 'Rows about this %s (%s), %s' % (e.get('kword') or EN.KIND_WORD[e['kind']], E(e['name']), ent_every(e)), on)


FOOT = '<footer class="foot"><div class="wrap">'
NO_FOOT_FORM = ('/alerts', '/inquire-ok')   # /alerts carries the form in the page; /inquire-ok is the shell of the worker's answer pages


def script_tag():
    return '<script src="/signup.js?v=%s" defer></script>' % hashlib.sha256(JS_HASH_SRC.encode()).hexdigest()[:8]


def footer(PAGES):
    """Put the form in every footer (call once, after every page is built). Returns the number of pages."""
    m = json.load(open(MAP)); items, brands = m['follow'], m['brands']; n = 0; tag = script_tag()
    import entities as EN
    try: eidx = EN.load()
    except Exception: eidx = {}
    by_url = {e['url']: i for i, e in eidx.items()}
    for k in list(PAGES):
        d = PAGES[k]
        if k in NO_FOOT_FORM or FOOT not in d or 'class="su"' in d: continue
        extra = ''; s = k.lstrip('/')
        if s in items: extra = item_box(s, items[s])
        elif k in by_url: extra = ent_box(by_url[k], eidx[by_url[k]])   # a brand page, an entity page or an OY school page: this company or named thing
        elif k.startswith('/brand/') and k[7:] in brands: extra = brand_box(k[7:], brands[k[7:]][0])
        d = d.replace(FOOT, FOOT + signup_form(extra), 1); n += 1
        PAGES[k] = d
    for k, d in PAGES.items():
        if 'class="su"' in d and '/signup.js' not in d and '</body>' in d: PAGES[k] = d.replace('</body>', tag + '\n</body>', 1)
    print('signup: the one sign-up form in %d footers' % n)
    return n


# ------------------------------------------------------------------------------------------------ the lists
def alertable(PAGES):
    import live_headlines as LH
    out = {}
    for s, spec in LH.DESKS.items():
        if spec['kind'] == 'flip' and not spec.get('outcome'): continue
        if '/' + s not in PAGES: continue
        out[s] = [spec['name'], LH.H2.get(s, '')]
    return out


def brand_desks(bb, rows, desks):
    out = {}
    for slug, (e, items) in bb.items():
        ds = sorted({rows[i]['key'] for i, _ in items if rows[i]['key'] in desks})
        if ds: out[slug] = [e['name'], ds]
    return out


def follow_items(PAGES, desks, outcome):
    """{slug: {name, what, div, mode, every, every_min, src}} for every desk and division page, plus {div slug: [name, [slugs]]}."""
    rid, tmin, lim = riders(), tick_minutes(), feed_limits()
    items, divs = {}, {}
    for dv in DIV_ORDER:
        if dv not in PAGES: continue
        ds = [x for x in (QIA_PAGES if dv == '/qia' else desks.get(dv, [])) if x[0] in PAGES]
        dslug = dv.lstrip('/')
        lab, mn, src = cadence(dslug, 'update', rid, tmin, lim)
        items[dslug] = dict(name=DIV_NAME[dv], what='The division page', div=dslug, mode='division', page_every=lab, page_every_min=mn, every='each desk at its own pace', every_min=None, src=src)
        sl = []
        for h, n, w in ds:
            s = h.lstrip('/')
            if s in items: continue
            mode = 'outcome' if s in outcome else 'update'
            lab, mn, src = cadence(s, mode, rid, tmin, lim)
            items[s] = dict(name=html.unescape(n), what=html.unescape(w), div=dslug, mode=mode, every=lab, every_min=mn, src=src)
            sl.append(s)
        divs[dslug] = [DIV_NAME[dv], sl]
    check_cadence({s: it for s, it in items.items() if it['mode'] != 'division'}, lim)
    return items, divs, round(tmin, 2)


def _names(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def kind_label(it):
    if it['mode'] == 'outcome': return 'Outcome changes, ' + it['every']
    if it['every_min'] is None: return 'Updates, sent ' + it['every']
    return 'Updates, ' + it['every']


def apply(PAGES, page, hero_slim, HOME, bb, rows, desks=None):
    out_desks = alertable(PAGES); brands = brand_desks(bb, rows, out_desks)
    items, divs, tmin = follow_items(PAGES, desks or {}, out_desks)
    for s, (nm, q) in out_desks.items():   # an outcome desk outside every division list still gets a line (none today)
        if s not in items:
            lab, mn, src = cadence(s, 'outcome', riders(), tmin, feed_limits())
            items[s] = dict(name=nm, what=q, div='', mode='outcome', every=lab, every_min=mn, src=src)
    sig = {s: SIGNALS.get(s, {}) for s, it in items.items() if it['mode'] != 'outcome'}
    dwell = {s: DWELL[s] for s in sig if s in DWELL}
    import entities as EN
    try: eidx = EN.load()
    except Exception: eidx = {}
    ents = {i: {'name': e['name'], 'kind': e['kind'], 'kword': e.get('kword') or EN.KIND_WORD[e['kind']], 'url': e['url'], 'feed': bool(e['feed'])} for i, e in eidx.items()}
    json.dump({'desks': out_desks, 'brands': brands, 'follow': items, 'divs': divs, 'signals': sig, 'dwell': dwell, 'tick_min': tmin, 'ents': ents, 'ent_every': ENT_EVERY},
              open(MAP, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
    ups = {s: [it['name'], it['what'], kind_label(it), it['div']] for s, it in items.items() if it['mode'] == 'update'}
    for s, it in items.items():   # a division's own page can be followed alone (u=<division>), as on /alerts
        if it['mode'] == 'division': ups[s] = [it['name'] + ' main page', it['what'], 'Updates, ' + (it['page_every'] if it['page_every_min'] is not None else 'sent when we publish a new version'), s]
    dvl = {s: [v[0], v[1]] for s, v in divs.items()}
    every = {s: kind_label(it) for s, it in items.items() if it['mode'] == 'outcome'}
    js = ('// Generated by alerts.py at each build: what an alert can follow. Do not edit by hand.\n'
          'export const ALERT_DESKS = %s;\nexport const ALERT_BRANDS = %s;\nexport const ALERT_UPS = %s;\nexport const ALERT_DIVS = %s;\nexport const ALERT_EVERY = %s;\nexport const ALERT_ENTS = %s;\n'
          % tuple(json.dumps(x, ensure_ascii=False, sort_keys=k) for x, k in ((out_desks, True), (brands, True), (ups, True), (dvl, False), (every, True),
                                                                              ({i: [e['name'], e['kword']] for i, e in ents.items()}, True))))   # divisions keep the menu order
    if not os.path.exists(LIST_JS) or open(LIST_JS, encoding='utf-8').read() != js: open(LIST_JS, 'w', encoding='utf-8').write(js)
    # /alerts: grouped by division, each with its own "everything in this division" box, then its desks
    blocks = []
    for dslug, (dname, sl) in divs.items():
        li = ''
        for s in sl:
            it = items[s]
            nm = 'd' if it['mode'] == 'outcome' else 'u'
            li += ('<li><label><input type="checkbox" name="%s" value="%s"> <strong>%s</strong> <span class="meta">%s</span></label> <span class="su-k">%s</span> <a href="/%s">page</a></li>'
                   % (nm, E(s), E(it['name']), E(it['what']), E(kind_label(it)), E(s)))
        blocks.append('<div class="su-div"><p class="su-dh"><label><input type="checkbox" name="dv" value="%s"><a href="/%s">%s</a>: everything in this division</label></p>'
                      '<ul class="su-list"><li><label><input type="checkbox" name="u" value="%s"> <strong>%s main page</strong></label> <span class="su-k">Updates, %s</span></li>%s</ul></div>'
                      % (E(dslug), E(dslug), E(dname), E(dslug), E(dname), E(items[dslug]['page_every'] if items[dslug]['page_every_min'] is not None else 'sent when we publish a new version'), li))
    listing = ('<p class="su-h" id="named">Companies, models and other named things</p>'
               '<p class="su-k">One email when a row about it changes or a new row about it appears, on any desk in any division. Rows the desks read from their feeds are '
               + E(ent_every({'feed': 1})) + '. Rows on other pages are sent when we publish a new version.</p>'
               '<p><label for="ent-q">Find a company, agency, model, quantum backend, school or package</label><br><input type="search" id="ent-q" class="ent-q" autocomplete="off" placeholder="IBM, Falcon, ibm_kingston, NOAA"></p>'
               '<div id="ent-picked" class="su-c" hidden></div><div id="ent-res" aria-live="polite"></div>'
               '<noscript><p class="su-k">Every company and organisation has a <a href="/brand">brand page</a> with its own box in the form at its foot.</p></noscript>'
               '<p class="su-h">The desks and divisions you tick</p>' + ''.join(blocks))
    body = ('<section class="legal"><p>One form for every email from indahl.ai. The same form sits at the foot of the site&rsquo;s pages.</p>'
            '<p>The weekly newsletter comes every Tuesday and starts at once. New desks and new data sends one email when a new desk goes live, when a desk '
            'publishes its first value under its change rule, and when a release adds an entry to the <a href="/changelog">changelog</a>.</p>'
            '<p>Desks marked outcome changes send one email when an outcome changes. A change is what the desk&rsquo;s ledger rule counts as one: the outcome '
            'moves, for example from consistent to above, or a new value passes the rule the desk states. Moves inside the printed interval stay on the page and send nothing. '
            'Desks and pages marked updates send one email when the data the page publishes changes: a row added, a count or an outcome that moved, or a new release '
            'that changes what the page says. A re-read that finds nothing new sends nothing, and neither does a change to the site&rsquo;s layout. '
            'Each line says how often we check it, and so how soon an email can follow a change, or that it is sent when we publish a new version. A division box covers the division page and every desk in it.</p>'
            '<p>You can have alerts and updates as they happen, in one daily digest or in one weekly digest on Tuesdays. Several changes found together come in one email.</p>'
            '<p>For every box but the newsletter, we email a confirmation link first and send nothing else until you open it. Every email has a link to unsubscribe, '
            'and every alert has a link to change what you get. Each outcome desk&rsquo;s changes are also on its own feed, for example <a href="/airq/changes.xml">/airq/changes.xml</a>, '
            'and each <a href="/brand">brand page</a> offers the rows about that organisation.</p>'
            '<p>You can also follow one company, agency, model, model family, quantum backend, school or package: search for it below, or tick the box at the foot of its page. '
            'One email comes when a row about it changes or a new row about it appears on any desk.</p>'
            + signup_form('', listing) + '</section><script src="/e/search.js" defer></script>')
    PAGES['/alerts'] = page('/alerts', 'Email Updates | Heuremen LLC', 'The weekly newsletter, new desks and new data, and an email when an outcome or the published data changes on the indahl.ai desks and divisions you follow, with a confirmation link first for alerts.',
                            body, hero_slim('Email Updates'))
    if HOME is not None: HOME['/alerts'] = '/hermes'
    nu = sum(1 for it in items.values() if it['mode'] == 'update')
    print('alerts: %d outcome desks, %d update pages, %d divisions and %d brand pages can send alerts (median tick %.1f min), /alerts built'
          % (len(out_desks), nu, len(divs), sum(1 for s in brands if '/brand/' + s in PAGES), tmin))
    return out_desks, brands
