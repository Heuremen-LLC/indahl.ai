"""notify.py -- the ways to follow indahl.ai besides email (10 Nov 2026). Build hook for build_site.py, and a gate.

  apply(PAGES, page, hero_slim, HOME, cssv, FEED)   once, after alerts.footer(PAGES)
    - /follow     every way to follow: the footer email form, this device, the calendar, the feeds, an OPML file, webhooks, the API and MCP
    - /webhooks   register an address for outcome changes (notify.js holds the routes, webhooks_send.py sends)
    - /changelog  site updates read from the release commits (git log of this repository), with its Atom feed /changelog.xml
    - writes into the worker's public folder: calendar.ics and <desk>/calendar.ics (notify_schedules.json), newsletter/feed.xml,
      changelog.xml and feeds.opml
    - on each desk that can send alerts: the "Notify me on this device" button and its calendar link. On each brand page that can: a link to
      /brand/<org>/changes.xml (served live by notify.js) with rel=alternate. On /newsletter: rel=alternate to its feed.
    - one "Follow" link in every footer, after Corrections
  gate()   python3 notify.py --gate: every built feed parses (feedparser if present, else XML), every calendar parses (icalendar if present, else
           a line check), every event cites a schedule URL, and the pages keep the public-copy rules (no semicolons, no house words)
Python 3.9+, standard library (feedparser and icalendar from ~/bones-forge/notify_state/venv for the gate when present)."""
import os, sys, re, json, html, hashlib, subprocess, datetime as D
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public')
sys.path.insert(0, os.path.join(B, 'ledger')); sys.path.insert(0, HERE)
SITE = 'https://indahl.ai'; HUB = 'https://pubsubhubbub.appspot.com/'
E = lambda s: html.escape(str(s), quote=True)
SCHED = os.path.join(HERE, 'notify_schedules.json')
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
EMB_A, EMB_B = '<!--emb-->', '<!--/emb-->'   # build_site's _page_dates leaves these blocks out, so adding them does not restamp a page

CSS = """
.np{margin:14px 0 6px}.np .btn{border:0;cursor:pointer;font-size:12px}.np-msg{display:block;font-size:14px;color:var(--mid);margin-top:6px}.np-msg:empty{display:none}
.nt-list{list-style:none;padding:0;margin:6px 0 12px}.nt-list li{margin:5px 0;line-height:1.4}.nt-cols{columns:2 260px;column-gap:28px}.nt-cols li{break-inside:avoid}
.whform input[type=url]{font:inherit;font-size:15px;padding:7px 9px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:100%;max-width:560px;box-sizing:border-box}
.whform .btn{border:0;cursor:pointer;margin-top:6px}.whform label.lbl{display:block;font-weight:600;margin:8px 0 4px}
.legal pre{background:var(--paper2);border:1px solid var(--rule);padding:10px 12px;overflow-x:auto;font-size:13px;line-height:1.45;max-width:100%}
code.whsec{word-break:break-all;font-size:14px}.cl-day{margin:0 0 6px}.cl-row{margin:3px 0;font-size:14.5px;line-height:1.45}.cl-tag{font-size:12px;font-family:Cinzel,Georgia,serif;letter-spacing:.06em;margin-right:6px}
"""


# ------------------------------------------------------------------------------------------------ shared
def _deny():
    import corrections as C
    return C.DENY, C.HANDS, C._argue()


def _desks():
    try: return json.load(open(os.path.join(HERE, 'alerts_map.json')))
    except Exception: return {'desks': {}, 'brands': {}}


def _write(rel, text):
    p = os.path.join(PUB, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p) or open(p, encoding='utf-8').read() != text:
        with open(p, 'w', encoding='utf-8', newline='') as f: f.write(text)
    return p


def _day(d):
    return '%d %s %d' % (d.day, MONTHS[d.month - 1], d.year)


# ------------------------------------------------------------------------------------------------ calendar (RFC 5545)
def _ics_text(s):
    return str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\r\n', '\\n').replace('\n', '\\n')


def _fold(line):
    """Lines of at most 75 octets, continued with CRLF and one space, never splitting a UTF-8 character."""
    out, cur, n = [], '', 0
    for ch in line:
        w = len(ch.encode('utf-8'))
        if n + w > (75 if not out else 74):
            out.append(cur); cur, n = '', 0
        cur += ch; n += w
    out.append(cur)
    return '\r\n '.join(out)


def _ymd(s): return s.replace('-', '')


def _vevent(uid, stamp, start, end_incl, summary, desc, url, cats, rrule=None):
    end = (D.date.fromisoformat(end_incl) + D.timedelta(days=1)).isoformat()   # DTEND of an all-day event is the day after (exclusive)
    L = ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp, 'DTSTART;VALUE=DATE:' + _ymd(start), 'DTEND;VALUE=DATE:' + _ymd(end)]
    if rrule: L.append('RRULE:' + rrule)
    L += ['SUMMARY:' + _ics_text(summary), 'DESCRIPTION:' + _ics_text(desc), 'URL:' + url, 'CATEGORIES:' + _ics_text(cats), 'TRANSP:TRANSPARENT', 'END:VEVENT']
    return L


def _vcal(name, desc, events):
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Heuremen LLC//indahl.ai calendar//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:' + _ics_text(name), 'X-WR-CALDESC:' + _ics_text(desc), 'X-WR-TIMEZONE:UTC',
         'REFRESH-INTERVAL;VALUE=DURATION:P1D', 'X-PUBLISHED-TTL:P1D']
    for ev in events: L += ev
    L.append('END:VCALENDAR')
    return '\r\n'.join(_fold(l) for l in L) + '\r\n'


def newsletter_event():
    return _vevent('newsletter-weekly@indahl.ai', '20261110T000000Z', '2026-11-10', '2026-11-10', 'Heuremen LLC weekly newsletter',
                   'The Heuremen LLC weekly newsletter goes out every Tuesday. Every issue is kept at https://indahl.ai/newsletter. '
                   'Sign up with the form at the foot of any page on indahl.ai.', SITE + '/newsletter', 'Heuremen LLC', rrule='FREQ=WEEKLY;BYDAY=TU')


def schedule_events(desk=None, names=None):
    s = json.load(open(SCHED)); out = []
    for src in s['sources']:
        if desk and src['desk'] != desk: continue
        nm = (names or {}).get(src['desk'], src['desk'].upper())
        for ev in src['events']:
            desc = ('%s Schedule as published at %s (read %s). The %s desk on indahl.ai: %s/%s'
                    % (src['note'], src['url'], _day(D.date.fromisoformat(src['read'])), nm, SITE, src['desk']))
            out.append(_vevent('%s-%s@indahl.ai' % (src['id'], _ymd(ev['date'])), _ymd(src['read']) + 'T000000Z', ev['date'], ev.get('end', ev['date']),
                               '%s: %s' % (src['title'], ev['label']), desc, src['url'], nm))
    return out


def calendars(PAGES, names):
    s = json.load(open(SCHED)); built = {}
    built['calendar.ics'] = _vcal('indahl.ai schedules', 'The Heuremen LLC weekly newsletter and the release dates the sources of the indahl.ai desks publish. Each event links its source schedule.',
                                  [newsletter_event()] + schedule_events(names=names))
    for desk in sorted({x['desk'] for x in s['sources']}):
        if '/' + desk not in PAGES: continue
        built['%s/calendar.ics' % desk] = _vcal('indahl.ai %s: source release dates' % names.get(desk, desk.upper()),
                                                'Release dates the source of the %s desk publishes, as stated on its schedule page.' % names.get(desk, desk.upper()),
                                                schedule_events(desk, names))
    for rel, text in built.items(): _write(rel, text)
    return built


# ------------------------------------------------------------------------------------------------ newsletter feed
def newsletter_feed(PAGES):
    import newsletter_pages as NP
    ents = []; today = D.date.today()
    for n, p in NP.issues():
        if '/newsletter/%d' % n not in PAGES: continue
        title, meta, blocks = NP.parse(open(p, encoding='utf-8').read())
        m = re.search(r'(\d{1,2}) (%s) (\d{4})' % '|'.join(MONTHS), meta)
        if not m: continue
        d = D.date(int(m.group(3)), MONTHS.index(m.group(2)) + 1, int(m.group(1)))
        if d > today: continue
        lead = re.sub(r'\*\*', '', next((v for k, v in blocks if k == 'p'), ''))
        ents.append((d, '<entry><id>tag:indahl.ai,2026:newsletter/%d</id><title>%s</title><link href="%s/newsletter/%d"/><updated>%sT00:00:00Z</updated>'
                        '<summary>%s</summary><content type="html">%s</content></entry>' % (n, E(title), SITE, n, d.isoformat(), E(lead[:400]), E(NP.body_html(blocks, True)))))
    ents.sort(key=lambda x: x[0], reverse=True)
    upd = (ents[0][0].isoformat() if ents else '2026-11-10') + 'T00:00:00Z'
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>tag:indahl.ai,2026:newsletter</id><title>Heuremen LLC weekly newsletter</title>'
         '<subtitle>Every issue of the weekly newsletter, as published on indahl.ai.</subtitle>'
         '<link href="%s/newsletter/feed.xml" rel="self"/><link href="%s" rel="hub"/><link href="%s/newsletter" rel="alternate"/><updated>%s</updated><author><name>Heuremen LLC</name></author>%s</feed>\n'
         % (SITE, HUB, SITE, upd, ''.join(e for _, e in ents)))
    _write('newsletter/feed.xml', x)
    return len(ents)


# ------------------------------------------------------------------------------------------------ changelog (release commits)
NEW_DESK = re.compile(r'^([A-Z][A-Z0-9]{1,}) desk\b(?! pack)(?!: data pack)')


def commits():
    """[(sha, utc datetime, message)] of this repository's release commits, newest first. Messages that would break the public-copy rules
    (house words, the hands rule, pitch voice) are left out, and the rest are printed as written."""
    try:
        out = subprocess.run(['git', '-C', HERE, 'log', '--since=2026-11-10T00:00:00-10:00', '--format=%H%x1f%aI%x1f%s'], capture_output=True, text=True, timeout=60).stdout
    except Exception: return []
    deny, hands, argue = _deny(); rows = []
    for l in out.splitlines():
        try: sha, at, msg = l.split('\x1f', 2)
        except ValueError: continue
        msg = msg.strip()
        if not msg or deny.search(msg) or hands.search(msg) or any(a.search(msg) for a in argue): continue
        if re.search(r'(?i)\b(wip|revert|merge|test|tmp|scratch|sage|kids?|house|held|private|staging|local|his|her|queen|sunflower|coin|client|principal)\b|bones-forge|/Users/|\bkv\b|\bwrangler\b|\.py\b|\.sh\b|\.jsonl?\b', msg): continue
        msg = msg.replace('; ', '. ').replace(';', ',')
        t = D.datetime.fromisoformat(at).astimezone(D.timezone.utc)
        rows.append((sha, t, msg))
    return rows


def changelog(PAGES, page, hero_slim):
    rows = commits()
    out = ['<section class="legal">',
           '<p>Every release of indahl.ai is one commit to the site&rsquo;s source, made by the release step after every check passes. This page lists those commits, newest first, with each message as written. A new desk, a new channel and a change to a method each show up here on the day they go live. Each release appears here once the next release is built. The list starts on 10 November 2026.</p>',
           '<p>Releases whose message names a person or an internal working file are left out of this list. Every release is stamped and listed with its files on <a href="/receipts/stamps">the release stamps page</a>, and every fix to a published reading is on <a href="/corrections">the corrections log</a>.</p>',
           '<p class="meta">Atom feed: <a href="/changelog.xml">changelog.xml</a> &middot; Code: <a href="https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/site/notify.py">notify.py</a></p>']
    day = None
    for sha, t, msg in rows:
        d = t.date()
        if d != day:
            if day is not None: out.append('</div>')
            day = d; out.append('<h2 id="d%s">%s</h2><div class="cl-day">' % (d.isoformat(), _day(d)))
        tag = '<span class="cl-tag">New desk</span> ' if NEW_DESK.match(msg) else ''
        out.append('<p class="cl-row" id="c%s">%s%s <span class="meta">%s UTC</span></p>' % (sha[:12], tag, E(msg), t.strftime('%H:%M')))
    if day is not None: out.append('</div>')
    out.append('</section>')
    PAGES['/changelog'] = page('/changelog', 'Changelog: Every Release of indahl.ai | Heuremen LLC', 'Every release of indahl.ai, newest first: new desks, new channels and method changes, read from the release commits of the site.',
                               '\n'.join(out), hero_slim('Changelog', 'Every release of indahl.ai'))
    PAGES['/changelog'] = PAGES['/changelog'].replace('</head>', '<link rel="alternate" type="application/atom+xml" title="indahl.ai changelog" href="/changelog.xml">\n</head>', 1)
    ent = []
    for sha, t, msg in rows[:60]:
        ts = t.strftime('%Y-%m-%dT%H:%M:%SZ')
        ent.append('<entry><id>tag:indahl.ai,2026:changelog/%s</id><title>%s</title><link href="%s/changelog#c%s"/><updated>%s</updated><summary>%s</summary>%s</entry>'
                   % (sha[:12], E(msg[:140]), SITE, sha[:12], ts, E(msg), '<category term="new desk"/>' if NEW_DESK.match(msg) else ''))
    upd = rows[0][1].strftime('%Y-%m-%dT%H:%M:%SZ') if rows else '2026-11-10T00:00:00Z'
    _write('changelog.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>tag:indahl.ai,2026:changelog</id><title>indahl.ai changelog</title>'
           '<subtitle>Every release of indahl.ai, read from the release commits.</subtitle><link href="%s/changelog.xml" rel="self"/><link href="%s" rel="hub"/><link href="%s/changelog" rel="alternate"/>'
           '<updated>%s</updated><author><name>Heuremen LLC</name></author>%s</feed>\n' % (SITE, HUB, SITE, upd, ''.join(ent)))
    return len(rows)


# ------------------------------------------------------------------------------------------------ OPML
def opml(desk_feeds, brands):
    o = lambda t, x, h: '<outline type="rss" text="%s" title="%s" xmlUrl="%s" htmlUrl="%s"/>' % (E(t), E(t), E(x), E(h))
    site = [o('Heuremen LLC: new studies and bench rounds', SITE + '/feed.xml', SITE + '/'), o('Heuremen LLC: corrections', SITE + '/corrections.xml', SITE + '/corrections'),
            o('Heuremen LLC weekly newsletter', SITE + '/newsletter/feed.xml', SITE + '/newsletter'), o('indahl.ai changelog', SITE + '/changelog.xml', SITE + '/changelog')]
    dk = [o('%s: changes to the headline' % n, '%s/%s/changes.xml' % (SITE, s), '%s/%s' % (SITE, s)) for s, n in desk_feeds]
    br = [o('%s: changes on the desks with rows about it' % n, '%s/brand/%s/changes.xml' % (SITE, s), '%s/brand/%s' % (SITE, s)) for s, n in brands]
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0"><head><title>indahl.ai feeds</title><ownerName>Heuremen LLC</ownerName><docs>http://opml.org/spec2.opml</docs></head><body>'
         '<outline text="Heuremen LLC" title="Heuremen LLC">%s</outline><outline text="Desks" title="Desks">%s</outline><outline text="Organisations" title="Organisations">%s</outline></body></opml>\n'
         % (''.join(site), ''.join(dk), ''.join(br)))
    _write('feeds.opml', x)


# ------------------------------------------------------------------------------------------------ pages
def _np(desk, cal=False, label=None):
    c = (' &middot; <a href="/%s/calendar.ics">Release dates of the source (calendar)</a>' % desk) if cal else ''
    return (EMB_A + '<section class="np"><p class="meta">Follow this desk: <a href="/%s/changes.xml">feed</a> &middot; <a href="/webhooks">webhook</a>%s &middot; <a href="/follow">every way to follow</a></p>'
            '<p><button type="button" class="btn np-btn" data-desk="%s" hidden>%s</button><span class="np-msg" role="status" aria-live="polite"></span></p></section>' % (desk, c, E(desk), label or 'Notify me on this device') + EMB_B)


def _script():
    v = hashlib.sha256(open(os.path.join(HERE, 'notify.js'), 'rb').read()).hexdigest()[:8]
    return '<script src="/notify.js?v=%s" defer></script>' % v


def follow_page(desk_feeds, cal_desks, names):
    dl = ''.join('<li><a href="/%s">%s</a>: <a href="/%s/changes.xml">changes.xml</a></li>' % (s, E(n), s) for s, n in desk_feeds)
    cl = ''.join('<li><a href="/%s">%s</a>: <a href="/%s/calendar.ics">calendar.ics</a></li>' % (s, E(names.get(s, s.upper())), s) for s in cal_desks)
    return ('<section class="legal">'
            '<p>Every way to follow indahl.ai. None of them needs an account.</p>'
            '<h2 id="email">Email</h2><p>The sign-up form at the foot of every page sends the weekly newsletter every Tuesday, news of new desks and new data, and an email when an outcome changes on the desks you pick. To pick desks, use <a href="/alerts">the email updates page</a>. Every email has a one-click unsubscribe.</p>'
            '<h2 id="device">Notifications on this device</h2><p>Your browser or phone can show a short notification when an outcome changes: the desk, the value before and now, and a link. Press the button to turn it on for every desk, or turn it on for one desk from that desk&rsquo;s page. Your browser asks for permission first. On an iPhone or iPad, add indahl.ai to your Home Screen first, then open it from there.</p>'
            + _np_all() +
            '<h2 id="calendar">Calendar</h2><p>One calendar holds the weekly newsletter and the release dates the sources of our desks publish, each event with a link to the source&rsquo;s own schedule page. Only dates the source states are listed.</p>'
            '<ul class="nt-list"><li><a href="webcal://indahl.ai/calendar.ics">Subscribe in your calendar app</a> &middot; <a href="/calendar.ics">calendar.ics</a></li></ul>'
            '<p>One desk at a time:</p><ul class="nt-list">' + cl + '</ul>'
            '<h2 id="feeds">Feeds</h2><p>Feeds work in any feed reader. Each one announces new entries through the public WebSub hub at pubsubhubbub.appspot.com, so a reader that supports it gets them without asking again and again.</p>'
            '<ul class="nt-list"><li>New studies, desks and bench rounds: <a href="/feed.xml">feed.xml</a> (Atom) &middot; <a href="/feed.json">feed.json</a> (JSON Feed)</li>'
            '<li>Corrections: <a href="/corrections.xml">corrections.xml</a></li><li>The weekly newsletter: <a href="/newsletter/feed.xml">newsletter/feed.xml</a></li>'
            '<li>Site updates: <a href="/changelog.xml">changelog.xml</a></li>'
            '<li>Every desk and organisation feed in one file, for one import into a feed reader: <a href="/feeds.opml" download>feeds.opml</a></li></ul>'
            '<p>Each desk posts to its own feed only when its headline makes a material change under the desk&rsquo;s rule:</p><ul class="nt-list nt-cols">' + dl + '</ul>'
            '<p>Each organisation our desks measure has a feed of the desks with rows about it, linked from its page under <a href="/brand">brand pages</a>, at /brand/&lt;name&gt;/changes.xml.</p>'
            '<h2 id="webhooks">Webhooks</h2><p>A webhook sends a signed POST to your server, or a message to a Slack, Discord or Microsoft Teams channel, when an outcome changes. <a href="/webhooks">Register a webhook</a>.</p>'
            '<h2 id="api">API and MCP</h2><p>Every live measurement is readable as JSON at <a href="/api">/api</a>, and by agents through the read-only MCP server at https://indahl.ai/mcp.</p>'
            '<p class="meta">What each of these keeps about you is on <a href="/privacy#follow">the privacy notice</a>.</p></section>')


def _np_all():
    return ('<p><button type="button" class="btn np-btn" data-desk="all" hidden>Notify me on this device about every desk</button>'
            '<span class="np-msg" role="status" aria-live="polite"></span></p>')


EXAMPLE = {"type": "outcome_change", "sent_at": "2026-11-12T15:05:11Z", "events": [{"type": "outcome_change", "id": "live.airq.value.20261112T150002Z",
           "desk": "airq", "desk_name": "AIRQ", "question": "Do air sensors meet the EPA's own targets?", "before": {"display": "41%", "outcome": "consistent"},
           "now": {"display": "37%", "outcome": "below"}, "feed_time": "12 Nov 15:00", "why": "The outcome changed from consistent to below.",
           "recorded_at": "2026-11-12T15:00:02Z", "url": "https://indahl.ai/airq", "feed": "https://indahl.ai/airq/changes.xml"}]}

VERIFY_PY = '''import hmac, hashlib, time

def verify(secret, headers, body):
    """body: the raw request body (bytes). headers: a case-insensitive mapping, as most frameworks give.
    Returns True when the delivery is ours and fresh."""
    ts = headers["X-Indahl-Timestamp"]
    if abs(time.time() - int(ts)) > 300:
        return False
    mac = hmac.new(secret.encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest("v1=" + mac, headers["X-Indahl-Signature"])'''

VERIFY_JS = '''const crypto = require("crypto");

function verify(secret, headers, body) {   // body: the raw request body as a Buffer
  const ts = headers["x-indahl-timestamp"];
  if (Math.abs(Date.now() / 1000 - Number(ts)) > 300) return false;
  const mac = "v1=" + crypto.createHmac("sha256", secret).update(ts + "." + body).digest("hex");
  const got = String(headers["x-indahl-signature"] || "");
  return got.length === mac.length && crypto.timingSafeEqual(Buffer.from(got), Buffer.from(mac));
}'''


def webhooks_page(desks):
    boxes = '<li><label><input type="checkbox" name="all" value="1"> <strong>Every desk</strong></label></li>' + ''.join(
        '<li><label><input type="checkbox" name="d" value="%s"> <strong>%s</strong> <span class="meta">%s</span></label></li>' % (E(s), E(n), E(q))
        for s, (n, q) in sorted(desks.items(), key=lambda x: x[1][0]))
    ex = dict(EXAMPLE); ev = dict(ex['events'][0])
    try:
        import live_headlines as LH; ev['question'] = LH.H2.get('airq', ev['question'])
    except Exception: pass
    ex['events'] = [ev]; ex = json.dumps(ex, indent=2, ensure_ascii=False)
    return ('<section class="legal">'
            '<p>A webhook sends a POST to an address you choose when an outcome changes on the desks you pick. A change is what the desk&rsquo;s ledger rule counts as one, the same events as the desk&rsquo;s change feed and the outcome emails. Moves inside the printed interval send nothing.</p>'
            '<h2 id="register">Register</h2>'
            '<form class="whform" method="post" action="/webhooks/register"><label class="lbl" for="whurl">Address (https)</label>'
            '<input id="whurl" type="url" name="url" required maxlength="500" placeholder="https://example.org/indahl-hook" autocomplete="off">'
            '<input class="nl-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<p class="lbl">Send a POST when an outcome changes on</p><ul class="nt-list nt-cols">' + boxes + '</ul>'
            '<button class="btn" type="submit">Register</button></form>'
            '<p>After you register you get a manage link, the only way to change or delete the webhook, and for a signed webhook a signing secret, shown once.</p>'
            '<h2 id="chat">Slack, Discord and Microsoft Teams</h2><p>An incoming-webhook address from Slack (hooks.slack.com), Discord (discord.com/api/webhooks) or Microsoft Teams (webhook.office.com) is recognised. It gets a plain message in the app&rsquo;s own format, one per change, with the desk, the value before and now, and a link. We send one test message when you register, and register the address only if the app accepts it.</p>'
            '<h2 id="ownership">Ownership check</h2><p>For any other address we first send one POST with the header <code>X-Indahl-Event: url_verification</code> and the body <code>{"type": "url_verification", "challenge": "&lt;random&gt;"}</code>. Your receiver must answer with status 200 and the challenge value, either as the whole body or as <code>{"challenge": "&lt;random&gt;"}</code>, within 10 seconds. Nothing is stored until it does.</p>'
            '<p>The address must start with https:// and name a host on the public internet. Addresses with an IP number, localhost or a private name are refused, and so is a name that points to a private network address, checked again before every delivery.</p>'
            '<h2 id="payload">What we send</h2><p>One POST per change pass holds every change for that webhook. The body is JSON. An example, with made-up values:</p><pre><code>' + E(ex) + '</code></pre>'
            '<p>Headers: <code>X-Indahl-Event: outcome_change</code>, <code>X-Indahl-Delivery</code> (an ID for each attempt), <code>X-Indahl-Timestamp</code> (Unix seconds) and <code>X-Indahl-Signature: v1=&lt;hex&gt;</code>, the HMAC-SHA256 of the timestamp, a full stop and the raw body, under your signing secret.</p>'
            '<h2 id="verify">Checking a delivery</h2><p>Recompute the signature from the raw body and compare it in constant time. Refuse a delivery whose timestamp is more than five minutes from your clock, so a copied delivery cannot be sent again later. In Python:</p>'
            '<pre><code>' + E(VERIFY_PY) + '</code></pre><p>In Node.js:</p><pre><code>' + E(VERIFY_JS) + '</code></pre>'
            '<h2 id="retries">Retries and turning off</h2><p>A message a chat app answered with a 2xx is not sent again, so a retry sends only the changes still missing. A delivery that gets no 2xx answer within 10 seconds is tried again about 5 minutes, 30 minutes, 2 hours and 6 hours later, then dropped. Redirects are not followed. After 10 failed attempts in a row the webhook is turned off and its manage page says when. You can turn it back on there, after the ownership check or test message passes again.</p>'
            '<h2 id="limits">Limits</h2><p>Each address can be registered once. Five registrations or turn-back-on checks per connection per hour. The list has room for 2,000 webhooks.</p>'
            '<p class="meta">What we keep: the address, the desks, the signing secret and the time of registration, until you delete the webhook. Details on <a href="/privacy#webhooks">the privacy notice</a>. Other ways to follow are on <a href="/follow">the follow page</a>.</p></section>')


def apply(PAGES, page, hero_slim, HOME=None, cssv='', FEED=None):
    import live_headlines as LH
    m = _desks(); desks, brands = m['desks'], m['brands']
    names = {s: d['name'] for s, d in LH.DESKS.items()}
    s = json.load(open(SCHED)); cal_desks = sorted({x['desk'] for x in s['sources'] if '/' + x['desk'] in PAGES})
    desk_feeds = sorted(((d, names.get(d, d.upper())) for d in desks if '/' + d in PAGES), key=lambda x: x[1])
    calendars(PAGES, names)
    nn = newsletter_feed(PAGES)
    nc = changelog(PAGES, page, hero_slim)
    opml(desk_feeds, sorted(((b, v[0]) for b, v in brands.items() if '/brand/' + b in PAGES), key=lambda x: x[1].lower()))
    PAGES['/follow'] = page('/follow', 'Follow indahl.ai: Email, Calendar, Feeds, Webhooks | Heuremen LLC',
                            'Every way to follow indahl.ai: email, notifications on this device, a calendar of source release dates, feeds, an OPML file, webhooks, the API and MCP.',
                            follow_page(desk_feeds, cal_desks, names), hero_slim('Follow', 'Every way to follow indahl.ai'))
    PAGES['/webhooks'] = page('/webhooks', 'Webhooks: Outcome Changes to Your Server or Chat | Heuremen LLC',
                              'A signed POST to your server, or a Slack, Discord or Teams message, when an outcome changes on the indahl.ai desks you pick.',
                              webhooks_page(desks), hero_slim('Webhooks', 'Outcome changes, sent to your server or chat'))
    tag = _script(); nd = nb = 0
    for k in ('/follow', '/webhooks', '/changelog'):
        PAGES[k] = PAGES[k].replace('@@CSSV@@', cssv)
        if HOME is not None: HOME[k] = '/hermes'
    PAGES['/follow'] = PAGES['/follow'].replace('</body>', tag + '\n</body>', 1)
    for d in desks:
        k = '/' + d
        if k not in PAGES or '</main>' not in PAGES[k] or 'class="np"' in PAGES[k]: continue
        doc = PAGES[k]; i = doc.rfind('</main>')
        PAGES[k] = doc[:i] + _np(d, d in cal_desks) + doc[i:]
        PAGES[k] = PAGES[k].replace('</body>', tag + '\n</body>', 1); nd += 1
    for b, (nm, ds) in brands.items():
        k = '/brand/' + b
        if k not in PAGES or '</main>' not in PAGES[k]: continue
        doc = PAGES[k].replace('</head>', '<link rel="alternate" type="application/atom+xml" title="%s: changes on the desks with rows about it" href="/brand/%s/changes.xml">\n</head>' % (E(nm), b), 1)
        i = doc.rfind('</main>')
        PAGES[k] = doc[:i] + EMB_A + '<p class="meta np">Changes on the desks with rows about %s: <a href="/brand/%s/changes.xml">feed (Atom)</a> &middot; <a href="/follow">every way to follow</a></p>' % (E(nm), b) + EMB_B + doc[i:]; nb += 1
    for k in [x for x in PAGES if x == '/newsletter' or re.match(r'^/newsletter/\d+$', x)]:
        PAGES[k] = PAGES[k].replace('</head>', '<link rel="alternate" type="application/atom+xml" title="Heuremen LLC weekly newsletter" href="/newsletter/feed.xml">\n</head>', 1)
    fl = 0
    for k in PAGES:
        d = PAGES[k]
        if '<a href="/corrections">Corrections</a><a href="/community">' in d and 'href="/follow">Follow</a>' not in d:
            PAGES[k] = d.replace('<a href="/corrections">Corrections</a><a href="/community">', '<a href="/corrections">Corrections</a><a href="/follow">Follow</a><a href="/community">', 1); fl += 1
    if FEED is not None:
        FEED.append(('/follow', 'Follow indahl.ai: Email, Calendar, Feeds, Webhooks', 'Every way to follow indahl.ai: email, notifications on this device, a calendar of source release dates, feeds, webhooks, the API and MCP.'))
        FEED.append(('/changelog', 'Changelog: Every Release of indahl.ai', 'Every release of indahl.ai, newest first, read from the release commits of the site.'))
    print('notify: /follow, /webhooks, /changelog (%d releases), %d newsletter issues in the feed, calendars, OPML, the device button on %d desks, brand feed links on %d pages, Follow in %d footers'
          % (nc, nn, nd, nb, fl))


# ------------------------------------------------------------------------------------------------ gate
def gate():
    bad = []
    try: import feedparser
    except ImportError: feedparser = None
    try: import icalendar
    except ImportError: icalendar = None
    import xml.dom.minidom as MD
    feeds = ['newsletter/feed.xml', 'changelog.xml', 'corrections.xml'] + sorted(os.path.relpath(p, PUB) for p in __import__('glob').glob(os.path.join(PUB, '*', 'changes.xml')))
    for rel in feeds:
        p = os.path.join(PUB, rel)
        if not os.path.exists(p): bad.append('missing feed ' + rel); continue
        raw = open(p, 'rb').read()
        try: MD.parseString(raw)
        except Exception as e: bad.append('%s does not parse as XML: %s' % (rel, e)); continue
        if feedparser:
            f = feedparser.parse(raw)
            if f.bozo: bad.append('%s: feedparser says %s' % (rel, f.bozo_exception))
            if not f.feed.get('title'): bad.append('%s has no title' % rel)
        if b'rel="hub"' not in raw: bad.append('%s names no WebSub hub' % rel)
    try: MD.parseString(open(os.path.join(PUB, 'feeds.opml'), 'rb').read())
    except Exception as e: bad.append('feeds.opml does not parse: %s' % e)
    for p in [os.path.join(PUB, 'calendar.ics')] + __import__('glob').glob(os.path.join(PUB, '*', 'calendar.ics')):
        raw = open(p, 'rb').read(); rel = os.path.relpath(p, PUB)
        if b'\r\n' not in raw or re.search(rb'(?<!\r)\n', raw): bad.append('%s: lines must end in CRLF' % rel)
        if any(len(l) > 75 for l in raw.split(b'\r\n')): bad.append('%s: a line longer than 75 octets' % rel)
        if icalendar:
            try:
                cal = icalendar.Calendar.from_ical(raw)
                for ev in cal.walk('VEVENT'):
                    for k in ('UID', 'DTSTAMP', 'DTSTART', 'SUMMARY'):
                        if ev.get(k) is None: bad.append('%s: an event without %s' % (rel, k))
                    if not str(ev.get('URL', '')).startswith('https://'): bad.append('%s: event %s cites no https schedule page' % (rel, ev.get('UID')))
            except Exception as e: bad.append('%s does not parse as iCalendar: %s' % (rel, e))
    deny, hands, argue = _deny()
    for name in ('follow.html', 'webhooks.html', 'changelog.html'):
        p = os.path.join(HERE, name)
        if not os.path.exists(p): continue
        a = open(p, encoding='utf-8').read(); i, j = a.find('<main'), a.rfind('</main>')
        t = html.unescape(re.sub(r'<pre>.*?</pre>', ' ', a[i:j], flags=re.S)); t = re.sub(r'<[^>]+>', ' ', t)
        if ';' in t: bad.append('%s: semicolon in the page text' % name)
        mm = deny.search(t) or hands.search(t)
        if mm: bad.append('%s: refused word %r' % (name, mm.group()))
    return bad


if __name__ == '__main__':
    if '--gate' in sys.argv:
        b = gate()
        if b: print('NOTIFY GATE FAILED:\n  ' + '\n  '.join(b)); sys.exit(1)
        print('notify gate: every feed, calendar and OPML file parses, every event cites its schedule'); sys.exit(0)
    print(__doc__)
