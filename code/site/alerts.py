"""alerts.py -- outcome alerts on indahl.ai (10 Nov 2026). Build hook for build_site.py, called once after the brand pages are built.

  apply(PAGES, page, hero_slim, HOME, bb, rows)
    - the desks that can send an alert: every live-headline desk (ledger/live_headlines.py DESKS) whose rule can write a value row after its
      baseline (a flip rule with no outcome never can) and whose page is built
    - the organisations that can: a brand page with rows on at least one of those desks
    - writes alerts_list.js (the worker's list of desks and organisations) and alerts_map.json (the same, read by alerts_send.py)
    - builds /alerts (the one sign-up form with every desk listed)
  footer(PAGES)   (10 Nov 2026) the one sign-up form in every footer: newsletter, new desks and new data, every desk, and on a desk page or a
    brand page that can send alerts, that desk or that organisation, ticked. Call it once after every page is built.
The worker side is alerts.js (/signup, and newsletter.js for the newsletter box). The sender is alerts_send.py, a tick-bus rider. Python 3.9+."""
import os, sys, json, html, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(B, 'ledger'))
E = html.escape
MAP = os.path.join(HERE, 'alerts_map.json'); LIST_JS = os.path.join(HERE, 'alerts_list.js')
JS_HASH_SRC = 'signup.js v1'   # bump with a change to the script served at /signup.js (alerts.js), so browsers fetch the new one

# 10 Nov 2026 (owner's word): ONE sign-up form, in the footer of every page and on /alerts, in place of the footer newsletter field and the
# in-page alert box. Boxes: nl (weekly newsletter, at once), up (new desks and new data), all (every desk), d=<desk>, o=<organisation>.
CSS = """
.su{max-width:640px;margin:0 auto 12px;padding:4px 0 12px;border-bottom:1px solid #4a3d24;text-align:left}.su-h{margin:0 0 6px;font-weight:600;color:#efe5cf;font-size:15px}
.su-row{display:flex;gap:8px;margin:0 0 6px}.su input[type=email]{font:inherit;font-size:15px;padding:6px 8px;border:1px solid #4a3d24;background:#fffaf0;color:#1a1208;flex:1 1 auto;min-width:0;max-width:340px}
.su .btn{flex:none;background:var(--lit);color:var(--cave);padding:6px 14px;border:0;font:inherit;font-size:15px;cursor:pointer}.su .btn:hover{background:#f3e2a0}
.su-c{display:flex;flex-wrap:wrap;gap:2px 18px;margin:0 0 4px}.su-c label{display:inline-flex;align-items:flex-start;gap:6px;font-size:13.5px;line-height:1.35;color:#efe5cf;padding:3px 0}.su-c input{margin:2px 0 0;flex:none}
.su-say{font-size:12.5px;color:#cbbf9f;margin:4px 0 0;line-height:1.45}.foot .su-say a{display:inline;padding:0;font-size:inherit;color:#efe5cf;text-decoration:underline}
.su-msg{margin:6px 0 0;font-weight:600;color:#efe5cf;font-size:14px}.su-msg:empty{display:none}.nl-hp{position:absolute!important;left:-9999px!important;width:1px;height:1px;opacity:0}
main .su{margin:14px 0 10px;border-bottom:0;border-top:1px solid var(--rule);padding-top:12px}main .su-h,main .su-c label,main .su-msg{color:var(--ink)}main .su-say{color:var(--mid)}main .su input[type=email]{border-color:var(--rule);background:var(--paper)}
main .su .btn{background:var(--ink);color:var(--paper)}.su-list{list-style:none;padding:0;margin:6px 0 12px}.su-list li{margin:6px 0;line-height:1.4}.su-list input{vertical-align:-2px;margin:0 4px 0 0}
@media (max-width:520px){.su-c{flex-direction:column;gap:0}.su-c label{font-size:14px;padding:5px 0}}
"""


def _box(name, value, label, on):
    return '<label><input type="checkbox" name="%s" value="%s"%s> %s</label>' % (name, E(value), ' checked' if on else '', label)


def signup_form(extra='', listing=''):
    """The one form. extra: the desk or organisation box this page adds (ticked). listing: the full desk list (on /alerts only)."""
    return ('<form class="su" action="/signup" method="post"><p class="su-h">Email updates</p>'
            '<div class="su-row"><input type="email" name="email" required maxlength="160" autocomplete="email" placeholder="Email address" aria-label="Email address">'
            '<button class="btn" type="submit">Sign up</button></div>'
            '<input class="nl-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<div class="su-c">' + _box('nl', '1', 'Weekly newsletter, every Tuesday', True) + extra
            + _box('up', '1', 'New desks and new data', False) + _box('all', '1', 'Outcome changes on every desk', False) + '</div>' + listing
            + '<p class="su-say">The newsletter starts at once. The other boxes start only after you confirm by email. Every email has its own one-click unsubscribe link. '
            '<a href="/newsletter">Newsletter issues</a> &middot; ' + ('' if listing else '<a href="/alerts">Pick desks</a> &middot; ') + '<a href="/privacy#signup">Privacy</a></p>'
            '<p class="su-msg" role="status" aria-live="polite"></p></form>')


def desk_box(slug, name):
    return _box('d', slug, 'Outcome changes on this desk (%s)' % E(name), True)


def brand_box(slug, name):
    return _box('o', slug, 'Outcome changes on desks with rows about %s' % E(name), True)


FOOT = '<footer class="foot"><div class="wrap">'
NO_FOOT_FORM = ('/alerts', '/inquire-ok')   # /alerts carries the form in the page; /inquire-ok is the shell of the worker's answer pages


def script_tag():
    return '<script src="/signup.js?v=%s" defer></script>' % hashlib.sha256(JS_HASH_SRC.encode()).hexdigest()[:8]


def footer(PAGES):
    """Put the form in every footer (call once, after every page is built). Returns the number of pages."""
    m = json.load(open(MAP)); desks, brands = m['desks'], m['brands']; n = 0; tag = script_tag()
    for k in list(PAGES):
        d = PAGES[k]
        if k in NO_FOOT_FORM or FOOT not in d or 'class="su"' in d: continue
        extra = ''
        if k.lstrip('/') in desks: extra = desk_box(k.lstrip('/'), desks[k.lstrip('/')][0])
        elif k.startswith('/brand/') and k[7:] in brands: extra = brand_box(k[7:], brands[k[7:]][0])
        d = d.replace(FOOT, FOOT + signup_form(extra), 1); n += 1
        PAGES[k] = d
    for k, d in PAGES.items():
        if 'class="su"' in d and '/signup.js' not in d and '</body>' in d: PAGES[k] = d.replace('</body>', tag + '\n</body>', 1)
    print('signup: the one sign-up form in %d footers' % n)
    return n


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


def _names(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def apply(PAGES, page, hero_slim, HOME, bb, rows):
    desks = alertable(PAGES); brands = brand_desks(bb, rows, desks)
    json.dump({'desks': desks, 'brands': brands}, open(MAP, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
    js = ('// Generated by alerts.py at each build: the desks and organisations an outcome alert can follow. Do not edit by hand.\n'
          'export const ALERT_DESKS = %s;\nexport const ALERT_BRANDS = %s;\n' % (json.dumps(desks, ensure_ascii=False, sort_keys=True), json.dumps(brands, ensure_ascii=False, sort_keys=True)))
    if not os.path.exists(LIST_JS) or open(LIST_JS, encoding='utf-8').read() != js: open(LIST_JS, 'w', encoding='utf-8').write(js)
    li = ''.join('<li><label><input type="checkbox" name="d" value="%s"> <strong>%s</strong> <span class="meta">%s</span></label> <a href="/%s">desk</a></li>'
                 % (E(s), E(nm), E(q), E(s)) for s, (nm, q) in sorted(desks.items(), key=lambda x: x[1][0]))
    listing = '<p class="su-h">Outcome changes on the desks you tick</p><ul class="su-list">' + li + '</ul>'
    body = ('<section class="legal"><p>One form for every email from indahl.ai. The same form sits at the foot of the site&rsquo;s pages.</p>'
            '<p>The weekly newsletter comes every Tuesday and starts at once. New desks and new data sends one email when a new desk goes live or a desk '
            'publishes its first value under its change rule. Outcome changes sends one email when an outcome changes on a desk you follow. A change is what the '
            'desk&rsquo;s ledger rule counts as one: the outcome moves, for example from consistent to above, or a new value passes the rule the desk states. '
            'Moves inside the printed interval stay on the page and send nothing. Several changes found in one pass come in one email.</p>'
            '<p>For every box but the newsletter, we email a confirmation link first and send nothing else until you open it. Every email has a link to unsubscribe, '
            'and every alert has a link to change what you get. Each desk&rsquo;s changes are also on its own feed, for example <a href="/airq/changes.xml">/airq/changes.xml</a>, '
            'and each <a href="/brand">brand page</a> offers the desks with rows about that organisation.</p>'
            + signup_form('', listing) + '</section>')
    PAGES['/alerts'] = page('/alerts', 'Email Updates | Heuremen LLC', 'The weekly newsletter, new desks and new data, and an email when an outcome changes on the indahl.ai desks you follow, with a confirmation link first for alerts.',
                            body, hero_slim('Email Updates'))
    if HOME is not None: HOME['/alerts'] = '/hermes'
    print('alerts: %d desks and %d brand pages can send alerts, /alerts built (the form goes in the footers in footer())' % (len(desks), sum(1 for s in brands if '/brand/' + s in PAGES)))
    return desks, brands
