#!/usr/bin/env python3
"""alerts_send.py (10 Nov 2026): outcome alerts for indahl.ai, sent through Cloudflare Email Sending (heuremen.com: DKIM, SPF and DMARC pass,
bounces to cf-bounce.heuremen.com) on the same path, pacing and guards as newsletter_send.py and send_guarded.py.

  python3 -I alerts_send.py tick          the tick-bus rider: confirmation links for new sign-ups, then alerts for new value rows
  python3 -I alerts_send.py tick --dry    what would go out: counts, desks and the text with a placeholder token. Nothing sent or recorded.
  --ledger FILE    read value rows from FILE instead of ledger/ledger.jsonl (a scratch copy, for a test)
  --state DIR      keep the progress files in DIR instead of ~/bones-forge/outcome_alerts (a scratch folder, for a test)
  --test           refuse to send unless every recipient is an address at heuremen.com
  --subs FILE      read the subscriber lists from FILE ({"al:": [[token, metadata]], "alp:": [...]}) instead of the private KV (a test)
  --weekstate FILE read new desks from FILE instead of weekly.py's week_state.json (a test)
  --mirror DIR     read published pages from DIR instead of the public mirror (a test)
  --feeds DIR      read public feeds and changelog.xml from DIR (path under it as on the site) instead of indahl.ai (a test)
  --now ISO        the time of this pass (a test of the daily and weekly digests)
  --fake-send DIR  write each email to a file in DIR instead of sending it, with no pauses (a test: needs --subs, nothing leaves the machine)

What counts as a change: every live_value row live_headlines.py writes after a desk's baseline row. That is an outcome flip, or a new value
past the desk's material-change rule (outside the previous interval, or a field the plan's rule reads changed). A subscriber gets the rows of the
desks they ticked plus the desks with rows about the organisations they ticked, all of one run in ONE email. The first run of the sender marks
every row already in the ledger as seen, so it never mails history.

10 Nov 2026 (the combined sign-up form): a record with all = 1 follows every desk. A record with up = 1 also gets new desks and new data:
a desk's first value under the change rule, and a new desk page, read from weekly.py events (kinds 'first' and 'desk'), the same events
/week lists. Kept in seen_up.json like seen_rows.json (the first run marks every event already there as seen). One email per subscriber per
run holds both sections. An event is marked seen only when every subscriber who should get it has been sent it.

10 Nov 2026 evening (owner: every desk and division can be followed; "the live ones specifying when they alert"):
  - records keep their choices in the KV value (metadata holds only a time): d (outcome desks), o (organisations), u (pages followed for
    updates), dv (divisions), all, up and f (delivery: now, day or week). The list is read with one key listing and bulk reads of the values.
  - UPDATES: for every page in alerts_map.json 'signals' (desks without a change rule, the QIA List and Key, and each division page), the
    published data is compared with the last pass: the data fields named for its public feed (read from indahl.ai), and the visible text of
    its <main> in the public mirror of the latest release. Read times are never part of it. A change is one event that says what moved.
    The first pass seeds updates_state.json and sends nothing. A page new to the list is seeded on its first pass, also sending nothing.
  - New desks and new data also carries each new entry of the published changelog (/changelog.xml), seen in seen_cl.json, seeded the same way.
  - Every event found is written to events.jsonl (kept ten days) and marked seen at once. Delivery reads that journal: 'now' on the pass
    that finds it, 'day' once a day on the first pass after 13:00 UTC, 'week' on Tuesdays on the first pass after 13:00 UTC. Progress stays
    per event and subscriber, so no event reaches anyone twice, and an event found before a subscriber confirmed is never sent to them.

Order: live_headlines.py run holds ledger/.live_headlines.lock while it writes. This reads the ledger under the same lock, so a row half written
is never read and a row written while this runs is picked up on the next tick.
Guards: one run at a time (its own lock); --cap N emails per run (default 60); 25 to 75 s between sends; after every 20 sends it reads
Cloudflare's own delivery records for today and STOPS if more than 2 of the last 20 bounced; it stops on throttle, auth failure or any error.
A row is marked seen only when every subscriber who follows its desk has been sent it, so a stopped run resumes without double sending.
Addresses are read from the private KV at send time and never printed or written. Logs and progress name the token prefix only."""
import json, os, random, re, sys, time, html, fcntl
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H); sys.path.insert(0, H); sys.path.insert(0, os.path.join(B, 'ledger'))
A = sys.argv[1:]
def arg(k, d=None): return A[A.index(k) + 1] if k in A else d
DRY, TEST = '--dry' in A, '--test' in A; CAP = int(arg('--cap', 60))
OUT = os.path.abspath(arg('--state', os.path.join(B, 'outcome_alerts')))
LEDGER = os.path.abspath(arg('--ledger', os.path.join(B, 'ledger', 'ledger.jsonl')))
SUBS = arg('--subs'); WEEKSTATE = arg('--weekstate'); FAKE = arg('--fake-send'); MIRROR = os.path.abspath(arg('--mirror', os.path.join(B, 'public_mirror', 'indahl.ai'))); FEEDS = arg('--feeds'); NOW = arg('--now')
SEEN_UP = os.path.join(OUT, 'seen_up.json'); SEEN_CL = os.path.join(OUT, 'seen_cl.json'); UPD = os.path.join(OUT, 'updates_state.json')
JOURNAL = os.path.join(OUT, 'events.jsonl'); DIGEST = os.path.join(OUT, 'digest_last.json')
SEEN, PROG, LOG, RUNLOCK = os.path.join(OUT, 'seen_rows.json'), os.path.join(OUT, 'sent.progress'), os.path.join(OUT, 'send.log'), os.path.join(OUT, '.run.lock')
LH_LOCK = os.path.join(B, 'ledger', '.live_headlines.lock')
MAP = os.path.join(H, 'alerts_map.json')
FROM, FROM_NAME, SITE = 'Indahl@heuremen.com', 'Heuremen LLC', 'https://indahl.ai'
# CAN-SPAM postal address hook: the alerts are transactional and opt-in, but a postal line can be added to every footer by writing it (one line)
# to this file, outside every repository. Empty or missing: no line. Nothing else changes.
POSTAL_FILE = os.path.join(B, 'outcome_alerts', 'footer_postal_address.txt')


def log(s):
    if DRY: return
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')


def wr(*a):
    import newsletter_send as NS
    return NS.wr(*a)


def kv_list(prefix):
    """[(token, record)] for one KV prefix: the key list, then the values in bulk (choices live in the value since 10 Nov evening; a record
    written before then also has them in its metadata, which fills any field the value lacks). Records hold the address: never printed."""
    if SUBS:
        out = []
        for x in json.load(open(SUBS)).get(prefix, []):
            md = dict(x[1] or {}); v = x[2] if len(x) > 2 else None
            try: rec = json.loads(v) if isinstance(v, str) else (v or {})
            except ValueError: rec = {}
            out.append((x[0], dict(md, **(rec if isinstance(rec, dict) else {}))))
        return out
    import newsletter_send as NS
    rc, out = wr('kv', 'key', 'list', '--prefix', prefix, '--namespace-id', NS.NS, '--remote')
    if rc: raise SystemExit('alerts: the %s list could not be read (wrangler kv key list failed)' % prefix.rstrip(':'))
    keys = [(k['name'], k.get('metadata') or {}) for k in json.loads(out[out.index('['):])]
    vals = {}
    for i in range(0, len(keys), 100):
        tmp = os.path.join(OUT, '.bulk_keys.json'); json.dump([k for k, _ in keys[i:i + 100]], open(tmp, 'w'))
        rc, o = wr('kv', 'bulk', 'get', tmp, '--namespace-id', NS.NS, '--remote')
        os.remove(tmp)
        if rc: raise SystemExit('alerts: the %s values could not be read (wrangler kv bulk get failed)' % prefix.rstrip(':'))
        vals.update(json.loads(o[o.index('{'):]))
    res = []
    for k, md in keys:
        v = vals.get(k)
        if isinstance(v, dict) and isinstance(v.get('value'), str): v = v['value']   # wrangler's local mode wraps each value
        try: rec = json.loads(v) if isinstance(v, str) else {}
        except ValueError: rec = {}
        if not isinstance(rec, dict): rec = {}
        res.append((k[len(prefix):], dict(md, **rec)))
    return res


def postal():
    try: return open(POSTAL_FILE, encoding='utf-8').read().strip().splitlines()[0].strip()
    except Exception: return ''


def amap():
    return json.load(open(MAP))


def _names(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def send_one(to, subject, t, h, hdr):
    if FAKE:
        if not SUBS: raise SystemExit('alerts: --fake-send needs --subs')
        os.makedirs(FAKE, exist_ok=True); n = len(os.listdir(FAKE)) + 1
        open(os.path.join(FAKE, '%03d.txt' % n), 'w').write('To: %s\nSubject: %s\n%s\n\n%s' % (to, subject, '\n'.join(hdr), t)); return True, ''
    cmd = ['send', '--from', FROM, '--from-name', FROM_NAME, '--subject', subject, '--text', t, '--html', h, '--to', to]
    for x in hdr: cmd += ['--header', x]
    rc, out = wr('email', 'sending', *cmd)
    if 'Authentication error' in out:
        wr('whoami'); time.sleep(5); rc, out = wr('email', 'sending', *cmd)
    ok = rc == 0 and 'Queued for' in out
    err = '' if ok else ' '.join(l.strip() for l in out.splitlines() if 'email.sending' in l or 'ERROR' in l or 'code:' in l)[:300].replace(to, '<to>')
    return ok, err


def as_html(text):
    out = []
    for blk in re.split(r'\n\s*\n', text.strip()):
        b = html.escape(blk).replace('\n', '<br>')
        b = re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', b)
        out.append('<p>%s</p>' % b)
    return '\n'.join(out)


def wrap(body_text, foot_lines):
    t = body_text.rstrip() + '\n\n--\n' + '\n'.join(foot_lines) + '\n'
    fh = '<br>'.join(re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', html.escape(l)) for l in foot_lines)
    h = ('<!doctype html><html><body style="font-family:Georgia,serif;font-size:16px;line-height:1.5;color:#1a1208;max-width:640px">%s'
         '<hr><p style="font-size:13px;color:#555">%s</p></body></html>' % (as_html(body_text), fh))
    return t, h


def readable(tok, r):
    """A record with no address (its value could not be read) is skipped and logged by its token prefix, so one bad record never stops the run."""
    if '@' in str(r.get('e', '')): return True
    log('SKIPPED %s: no readable address in the record' % tok[:12]); print('alerts: skipped one record with no readable address (%s)' % tok[:12]); return False


def guard_recipient(e):
    if '@' not in e: raise SystemExit('alerts: a record carries no address; nothing sent')
    if TEST and not e.lower().endswith('@heuremen.com'): raise SystemExit('alerts: --test and a recipient outside heuremen.com; nothing sent')


# ------------------------------------------------------------------------------------------------ confirmations
FREQ = {'now': '', 'day': 'in one daily digest', 'week': 'in one weekly digest on Tuesdays'}


def follows(d, o, m, al=False):
    if al: return 'every desk'
    what = []
    if d: what.append(('the desk ' if len(d) == 1 else 'the desks ') + _names(m['desks'][s][0] for s in d if s in m['desks']))
    if o: what.append('the desks with rows about ' + _names(m['brands'][s][0] for s in o if s in m['brands']))
    return _names(what) if what else ''


def _uname(m, s):
    it = m['follow'].get(s, {}); return it.get('name', s.upper()) + (' main page' if it.get('mode') == 'division' else '')


def follow_parts(r, m):
    d, o, u, dv = r.get('d') or [], r.get('o') or [], r.get('u') or [], r.get('dv') or []
    p = []; w = follows(d, o, m, bool(r.get('all')))
    if w: p.append('outcome changes on ' + w)
    u = [s for s in u if s in m['follow']]; dv = [s for s in dv if s in m['divs']]
    if u: p.append('updates on ' + _names(_uname(m, s) for s in u))
    if dv: p.append('everything in ' + ('the division ' if len(dv) == 1 else 'the divisions ') + _names(m['divs'][s][0] for s in dv))
    if r.get('up'): p.append('new desks and new data')
    return p


def asks(r, m):
    p = []; w = follows(r.get('d') or [], r.get('o') or [], m, bool(r.get('all')))
    if w: p.append('when an outcome changes on ' + w)
    u = [s for s in (r.get('u') or []) if s in m['follow']]; dv = [s for s in (r.get('dv') or []) if s in m['divs']]
    if u: p.append('when the published data changes on ' + _names(_uname(m, s) for s in u))
    if dv: p.append('when anything changes in ' + ('the division ' if len(dv) == 1 else 'the divisions ') + _names(m['divs'][s][0] for s in dv))
    if r.get('up'): p.append('when a new desk goes live, a desk publishes its first value or the changelog gains an entry')
    return ', and '.join(p) + ((', ' + FREQ[r['f']]) if FREQ.get(r.get('f') or 'now') else '')


def confirm_text(ptok, r, m):
    url = '%s/alerts/confirm?t=%s' % (SITE, ptok)
    body = ('This address was entered on indahl.ai to get an email %s.\n\n'
            'To start these emails, open this link and press Confirm:\n%s\n\n'
            'The link works for two days. If you did not ask for this, ignore this email. Nothing more will be sent.' % (asks(r, m), url))
    foot = ['Heuremen LLC'] + ([postal()] if postal() else []) + ['Privacy: %s/privacy#alerts' % SITE]
    return wrap(body, foot)


def confirmations(m):
    pend = kv_list('alp:')
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    todo = [(t, md) for t, md in sorted(pend, key=lambda x: x[1].get('at', '')) if 'confirm:%s' % t[:12] not in done and readable(t, md)]
    print('alerts: %d sign-up(s) waiting for a confirmation email' % len(todo))
    sent = 0
    for n, (t, md) in enumerate(todo[:CAP]):
        e = md.get('e', ''); guard_recipient(e)
        txt, h = confirm_text(t, md, m)
        if DRY: print('--- DRY confirmation (placeholder token):\n' + txt.replace(t, 'x' * 40)); continue
        ok, err = send_one(e, 'Confirm your indahl.ai email alerts', txt, h, [])
        if not ok: log('STOPPED confirm:%s %s' % (t[:12], err)); print('STOPPED at confirm', t[:12], err); sys.exit(2)
        with open(PROG, 'a') as f: f.write('confirm:%s\n' % t[:12])
        log('ok confirm:%s' % t[:12]); sent += 1
        if n + 1 < min(CAP, len(todo)) and not FAKE: time.sleep(random.uniform(25, 75))
    return sent


# ------------------------------------------------------------------------------------------------ alerts
_ROWS = None
def _ledger_rows():
    """The ledger, read once per run under live_headlines' lock."""
    global _ROWS
    if _ROWS is None:
        lk = open(LH_LOCK, 'a'); fcntl.flock(lk, fcntl.LOCK_SH)   # live_headlines.py writes under LOCK_EX on this file
        try: _ROWS = [json.loads(l) for l in open(LEDGER, encoding='utf-8') if l.strip()]
        finally: fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    return _ROWS


def value_rows():
    """Every non-baseline live_value row, oldest first, each with the row before it on the same desk."""
    rows = _ledger_rows()
    vals = [r for r in rows if r.get('kind') == 'live_value' and r.get('reading') and r.get('live_of', '').startswith('live.')]
    vals.sort(key=lambda r: r['history'][0]['at'])
    out, last = [], {}
    for r in vals:
        desk = r['live_of'].split('.')[1]; prev = last.get(desk); last[desk] = r
        if prev is None or str(r['history'][0].get('why', '')).startswith('baseline'): continue
        out.append(dict(id=r['id'], desk=desk, prev=prev['reading'], cur=r['reading'], at=r['history'][0]['at']))
    return out


def up_events(rows):
    """New desks and first values (weekly.py events, kinds 'first' and 'desk'), oldest first, each with a stable id."""
    import weekly as WK
    st = json.load(open(WEEKSTATE)) if WEEKSTATE else None
    out = []
    for x in WK.headline_events(rows) + WK.desk_events(st):
        if x['kind'] == 'first': out.append(dict(x, uid=x['id']))
        elif x['kind'] == 'desk': out.append(dict(x, uid='desk:' + x['path']))
    return sorted(out, key=lambda x: x['at'])


def describe_up(x):
    when = x['at'].strftime('%d %b %Y, %H:%M UTC').lstrip('0')
    if x['kind'] == 'desk':
        return 'New desk: %s\n%s. Published %s.\n%s%s' % (x['desk'], x['what'].rstrip('.'), when, SITE, x['path'])
    return 'First value under the change rule: %s\n%s%s. Recorded %s.\n%s/%s' % (x['desk'], x['now'], (', interval ' + x['interval']) if x.get('interval') else '', when, SITE, x['slug'])


def describe(ch):
    import live_headlines as LH, changes_feed as CF
    spec = LH.DESKS.get(ch['desk'], {}); p, c = ch['prev'], ch['cur']
    return '%s: %s\nBefore: %s. Now: %s, at the feed time %s. %s\n%s/%s' % (
        spec.get('name', ch['desk'].upper()), LH.H2.get(ch['desk'], ''), CF._show(p), CF._show(c), c.get('stamp') or ch['at'][:16], CF._why(spec, p, c), SITE, ch['desk'])


# ------------------------------------------------------------------------------------------------ updates (the published data of a page)
import hashlib, urllib.request, datetime as D
ID_KEYS = ('vendor', 'server', 'resolver', 'backend', 'page', 'test', 'id', 'key', 'school', 'figure', 'bin', 'lead', 'cell', 'name', 'title', 'repo', 'first')
VOLATILE = re.compile(r'(?i)^(updated|generated|read|read_at|checked|built_utc|built|stamp|stamps|at|age|age_h|last_probe|newest_probe_hours|log_sha256|log_rows|chain|seat2|revision_time)$')   # revision_time: a Wikipedia edit time, moved by outside edits


def _idname(it, i):
    if isinstance(it, dict):
        ids = [str(it[k]) for k in ID_KEYS if isinstance(it.get(k), (str, int)) and str(it.get(k))][:2]
        return ' '.join(ids)[:90] if ids else '#%d' % (i + 1)
    return str(it)[:90]


def _strip(o):
    if isinstance(o, dict): return {k: _strip(v) for k, v in o.items() if not VOLATILE.match(k)}
    if isinstance(o, list): return [_strip(v) for v in o]
    return o


def _walk(o, toks, label):
    if not toks: yield label, o; return
    t, rest = toks[0], toks[1:]
    if t == '*':
        if isinstance(o, dict):
            for k, v in o.items(): yield from _walk(v, rest, label + [str(k)])
    elif t.endswith('[]'):
        lst = o.get(t[:-2]) if isinstance(o, dict) else None
        if isinstance(lst, list):
            for i, it in enumerate(lst): yield from _walk(it, rest, label + [t[:-2] + ': ' + _idname(it, i)])
    elif t.startswith('{'):
        if isinstance(o, dict):
            for k in t[1:-1].split(','):
                if k in o: yield label + ([] if k in ('name', 'title') and label else [k]), o[k]
    elif isinstance(o, dict) and t in o:
        yield from _walk(o[t], rest, label + ([] if t in ('name', 'title') and label and not rest else [t]))


def extract(doc, picks):
    """{label: value as canonical JSON} for the data fields a page's signal names."""
    out = {}
    for pk in picks:
        if pk == '@all':
            for k, v in _strip(doc).items(): out[k] = json.dumps(v, sort_keys=True, ensure_ascii=False)
            continue
        for lab, v in _walk(doc, pk.split('.'), []): out[' / '.join(lab)] = json.dumps(_strip(v), sort_keys=True, ensure_ascii=False)
    return out


def fetch(path):
    if FEEDS:
        f = os.path.join(FEEDS, path.lstrip('/'))
        return open(f, encoding='utf-8').read() if os.path.exists(f) else None
    try:
        rq = urllib.request.Request(SITE + path + '?x=%d' % time.time(), headers={'User-Agent': 'indahl-alerts/1 (+https://indahl.ai/alerts)', 'Cache-Control': 'no-cache'})
        return urllib.request.urlopen(rq, timeout=30).read().decode('utf-8')
    except Exception: return None


def main_text(doc):
    """The visible text of a page's <main>: tags, scripts, styles, version stamps and the read-time embed block left out, so a change to the
    layout, the menu or the footer is no change. Anything marked class="nosig" (labels the site adds, not data) is left out too."""
    a = doc.find('<main'); b = doc.rfind('</main>'); m = doc[a:b] if a >= 0 and b > a else ''
    m = re.sub(r'(?s)<!--emb-->.*?<!--/emb-->', ' ', m)
    m = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', m)
    m = re.sub(r'(?is)<([a-z]+)[^>]*\bclass="[^"]*\bnosig\b[^"]*"[^>]*>.*?</\1>', ' ', m)
    m = re.sub(r'\?v=[0-9a-f]{6,}', '', m)
    m = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', m))
    # read times printed on a page (a "Read" column, "Last read 21:36 UTC") say when we looked, not what we found
    m = re.sub(r'\d{4}-\d\d-\d\d[T ]\d\d:\d\d(:\d\d(\.\d+)?)?(Z|[+-]\d\d:?\d\d)?( UTC)?', ' ', m)
    m = re.sub(r'(?i)\b(updated|last read|read|checked|as of)\s+(\d{1,2} [A-Z][a-z]{2}\s+)?\d\d:\d\d( UTC)?', ' ', m)
    return re.sub(r'\s+', ' ', m).strip()


def page_hash(slug):
    f = os.path.join(MIRROR, ('index' if slug == '' else slug) + '.html')
    if not os.path.exists(f): return None
    t = main_text(open(f, encoding='utf-8').read())
    return hashlib.sha256(t.encode('utf-8')).hexdigest()[:16] if t else None


def _short(v):
    try: x = json.loads(v)
    except Exception: x = v
    t = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, separators=(', ', ': '))
    return t if len(t) <= 90 else t[:87] + '...'


def _diff(prev, x):
    lines = []
    ch = [k for k in x if k in prev and x[k] != prev[k]]; ad = [k for k in x if k not in prev]; rm = [k for k in prev if k not in x]
    for k in ch[:6]: lines.append('%s: %s, now %s' % (k, _short(prev[k]), _short(x[k])))
    for k in ad[:6]: lines.append('Added: %s%s' % (k, '' if _short(x[k]) in k else ' = ' + _short(x[k])))
    for k in rm[:3]: lines.append('No longer listed: %s' % k)
    more = len(ch) + len(ad) + len(rm) - min(len(ch), 6) - min(len(ad), 6) - min(len(rm), 3)
    if more > 0: lines.append('And %d more change%s in the same data.' % (more, '' if more == 1 else 's'))
    return lines


def _sig(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:12]


def update_events(m):
    """[(event)] for every followed page whose published data changed since the last pass, and the new state. Seeds on the first pass.
    A page in m['dwell'] keeps a changed feed reading as a candidate until the same reading has held for that many minutes."""
    st = _load(UPD, None)
    first = st is None; st = st or {}; new_st = {}; evs = []
    now = _now(); dwell = m.get('dwell', {})
    for slug, feeds in sorted(m.get('signals', {}).items()):
        old = st.get(slug) or {}; seeded = slug in st
        committed = dict(old.get('feeds') or {}); reading = {}
        for f, picks in feeds.items():
            raw = fetch(f)
            try: x = extract(json.loads(raw), picks) if raw else None
            except ValueError: x = None
            reading[f] = x if x else committed.get(f)          # unreadable or empty this pass: keep the last reading, say nothing
        cur = {'main': page_hash(slug) or old.get('main'), 'feeds': dict(committed)}
        lines = []
        moved = {f: x for f, x in reading.items() if x is not None and committed.get(f) is not None and x != committed[f]}
        fresh = {f: x for f, x in reading.items() if x is not None and committed.get(f) is None}
        cur['feeds'].update(fresh)                               # a feed seen for the first time is seeded, never reported
        if moved:
            hold = dwell.get(slug, 0); cand = old.get('cand') or {}; sg = _sig(moved)
            if hold and not (cand.get('sig') == sg and (now - D.datetime.fromisoformat(cand['since'].replace('Z', '+00:00'))).total_seconds() >= hold * 60):
                cur['cand'] = {'sig': sg, 'since': cand['since'] if cand.get('sig') == sg else now.strftime('%Y-%m-%dT%H:%M:%SZ')}
                moved = {}
            for f, x in moved.items(): lines += _diff(committed[f], x); cur['feeds'][f] = x
        new_st[slug] = cur
        if first or not seeded: continue
        page_moved = cur['main'] and old.get('main') and cur['main'] != old.get('main')
        if not lines and not page_moved: continue
        it = m['follow'].get(slug, {}); name = _uname(m, slug)
        body = '%s%s\n' % (name, (' (%s)' % m['divs'][it['div']][0]) if it.get('div') in m.get('divs', {}) and it.get('mode') != 'division' else '')
        if lines: body += 'The published data changed:\n' + '\n'.join('  ' + l for l in lines) + '\n'
        if page_moved: body += ('A new version of the page was also published.\n' if lines else 'A new version of the page was published, and what it says changed.\n')
        body += '%s/%s' % (SITE, slug)
        old_s = _sig({'main': old.get('main'), 'feeds': old.get('feeds')}); new_s = _sig({'main': cur['main'], 'feeds': cur['feeds']})
        evs.append(dict(id='upd:%s:%s-%s' % (slug, old_s, new_s), kind='upd', key=slug, name=name, at=now.strftime('%Y-%m-%dT%H:%M:%SZ'), text=body))
    if first: print('alerts: first run for updates, %d pages seeded, nothing sent' % len(new_st)); log('first run (updates): %d pages seeded, nothing sent' % len(new_st))
    return evs, new_st


def changelog_events():
    raw = fetch('/changelog.xml')
    if not raw: return None
    out = []
    for e in re.findall(r'(?s)<entry>(.*?)</entry>', raw):
        i = re.search(r'<id>[^<]*changelog/([0-9a-f]+)</id>', e); t = re.search(r'<title>(.*?)</title>', e, re.S); u = re.search(r'<updated>(.*?)</updated>', e)
        if not (i and t and u): continue
        out.append(dict(uid='cl:' + i.group(1), title=html.unescape(t.group(1)), at=u.group(1), newdesk='term="new desk"' in e, link='%s/changelog#c%s' % (SITE, i.group(1))))
    return sorted(out, key=lambda x: x['at'])


# ------------------------------------------------------------------------------------------------ the journal and delivery
def _now():
    return D.datetime.fromisoformat(NOW.replace('Z', '+00:00')) if NOW else D.datetime.now(D.timezone.utc)


def journal_read():
    if not os.path.exists(JOURNAL): return []
    cut = (_now() - D.timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
    out = []
    for l in open(JOURNAL, encoding='utf-8'):
        try: e = json.loads(l)
        except ValueError: continue
        if e.get('at', '') >= cut: out.append(e)
    return out


def journal_add(evs, keep):
    if DRY: return
    rows = keep + evs
    with open(JOURNAL + '.tmp', 'w', encoding='utf-8') as f: f.write(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in rows))
    os.replace(JOURNAL + '.tmp', JOURNAL)


def wants(ev, r, m):
    d, o, u, dv = set(r.get('d') or []), r.get('o') or [], set(r.get('u') or []), set(r.get('dv') or [])
    if ev['kind'] == 'chg':
        k = ev['key']; div = m['follow'].get(k, {}).get('div')
        return bool(r.get('all')) or k in d or any(k in m['brands'].get(s, ['', []])[1] for s in o) or (div in dv)
    if ev['kind'] == 'upd':
        k = ev['key']; div = m['follow'].get(k, {}).get('div')
        return k in u or (div in dv)
    if ev['kind'] == 'up': return bool(r.get('up'))
    return False


def due(r, tok, last):
    """Is this subscriber's delivery due on this pass?"""
    f = r.get('f') or 'now'; now = _now()
    if f == 'now': return True
    prev = last.get(tok[:12]); prev = D.datetime.fromisoformat(prev.replace('Z', '+00:00')) if prev else None
    if now.hour < 13: return False
    if f == 'day': return prev is None or prev.date() < now.date()
    if f == 'week': return now.weekday() == 1 and (prev is None or (now - prev).days >= 6)
    return False


def alert_text(tok, r, evs, m):
    chs = [e for e in evs if e['kind'] == 'chg']; upd = [e for e in evs if e['kind'] == 'upd']; ups = [e for e in evs if e['kind'] == 'up']
    o = r.get('o') or []; d = r.get('d') or []
    parts = []
    if chs:
        blocks = []
        for e in chs:
            b = e['text']
            why = [m['brands'][s][0] for s in o if s in m['brands'] and e['key'] in m['brands'][s][1]]
            if not r.get('all') and e['key'] not in d and why: b += '\nYou follow %s, which has rows on this desk.' % _names(why)
            blocks.append(b)
        parts.append(('An outcome changed on a desk you follow on indahl.ai.\n\n' if len(chs) == 1 else 'Outcomes changed on desks you follow on indahl.ai.\n\n') + '\n\n'.join(blocks))
    if upd:
        parts.append(('The published data changed on a page you follow.\n\n' if len(upd) == 1 else 'The published data changed on pages you follow.\n\n') + '\n\n'.join(e['text'] for e in upd))
    if ups:
        parts.append(('New on indahl.ai.\n\n' if not (chs or upd) else 'Also new on indahl.ai.\n\n') + '\n\n'.join(e['text'] for e in ups))
    f = r.get('f') or 'now'
    if f == 'day': subject = 'Your daily indahl.ai digest'
    elif f == 'week': subject = 'Your weekly indahl.ai digest'
    elif chs:
        names = list(dict.fromkeys(e['name'] for e in chs))
        subject = ('Outcome change on ' if len(chs) == 1 else 'Outcome changes on ') + _names(names) + (', and more on indahl.ai' if upd or ups else '')
    elif upd:
        names = list(dict.fromkeys(e['name'] for e in upd))
        subject = ('Update on ' if len(names) == 1 else 'Updates on ') + (_names(names) if len(names) <= 3 else 'pages you follow on indahl.ai') + (', and new on indahl.ai' if ups else '')
    else:
        nd = [e for e in ups if e.get('newdesk')]
        subject = 'New on indahl.ai: ' + _names(list(dict.fromkeys(e['name'] for e in ups))) if len(ups) <= 3 else 'New desks and new data on indahl.ai' if nd else 'New on indahl.ai'
    body = '\n\n'.join(parts)
    fp = follow_parts(r, m)
    manage, unsub = '%s/alerts/manage?t=%s' % (SITE, tok), '%s/alerts/unsubscribe?t=%s' % (SITE, tok)
    foot = (['Heuremen LLC'] + ([postal()] if postal() else [])
            + ['You are receiving this because this address confirmed email from indahl.ai for %s%s.' % (_names(fp) if fp else 'alerts', (', ' + FREQ[f]) if FREQ.get(f) else ''),
               'Change what you get or unsubscribe: ' + manage, 'Unsubscribe with one click: ' + unsub, 'Privacy: %s/privacy#alerts' % SITE])
    t, h = wrap(body, foot)
    return subject, t, h, ['List-Unsubscribe:<%s>' % unsub, 'List-Unsubscribe-Post:List-Unsubscribe=One-Click']


def _load(path, default):
    """A state file, or default when it is missing or cannot be read (logged, so a truncated file never stops every pass)."""
    if not os.path.exists(path): return default
    try: return json.load(open(path))
    except ValueError: log('state file %s could not be read, treated as missing' % os.path.basename(path)); return default


def _read_seen(path, ids, label):
    """The seen set, or None on the first run (which marks every id seen and sends nothing). An unreadable file counts as a first run."""
    v = _load(path, None)
    if v is not None: return set(v)
    if not DRY:
        os.makedirs(OUT, exist_ok=True); json.dump(sorted(ids), open(path, 'w'), indent=0)
        log('first run (%s): %d existing marked seen, nothing sent' % (label, len(ids)))
    print('alerts: first run for %s, %d existing marked seen, nothing sent' % (label, len(ids))); return None


def _save_seen(path, ids):
    if DRY: return
    json.dump(sorted(ids), open(path + '.tmp', 'w'), indent=0); os.replace(path + '.tmp', path)


def detect(m):
    """Find every new event, write it to the journal and mark it seen. Returns the journal (the last ten days)."""
    now = _now().strftime('%Y-%m-%dT%H:%M:%SZ'); evs = []
    rows = value_rows()
    seen = _read_seen(SEEN, [r['id'] for r in rows], 'change rows')
    new = [r for r in rows if r['id'] not in seen] if seen is not None else []
    for r in new:
        import live_headlines as LH
        evs.append(dict(id=r['id'], kind='chg', key=r['desk'], name=LH.DESKS.get(r['desk'], {}).get('name', r['desk'].upper()), at=now, text=describe(r)))
    try: ups_all = up_events(_ledger_rows())
    except Exception as ex: print('alerts: new desks and new data could not be read (%s), none this run' % type(ex).__name__); ups_all = None
    seen_up = _read_seen(SEEN_UP, [x['uid'] for x in ups_all], 'new desks and new data') if ups_all is not None else None
    new_up = [x for x in ups_all if x['uid'] not in seen_up] if seen_up is not None else []
    for x in new_up: evs.append(dict(id=x['uid'], kind='up', key=x.get('slug') or x.get('path', ''), name=x['desk'], newdesk=x['kind'] == 'desk', at=now, text=describe_up(x)))
    cl = changelog_events()
    seen_cl = _read_seen(SEEN_CL, [x['uid'] for x in cl], 'changelog entries') if cl is not None else None
    new_cl = [x for x in cl if x['uid'] not in seen_cl] if seen_cl is not None else []
    for x in new_cl:
        evs.append(dict(id=x['uid'], kind='up', key='changelog', name=(x['title'] if len(x['title']) <= 60 else x['title'][:57] + '...'), newdesk=x['newdesk'], at=now,
                        text='New on the changelog: %s\nReleased %s.\n%s' % (x['title'], x['at'][:16].replace('T', ' ') + ' UTC', x['link'])))
    upd, new_st = update_events(m)
    evs += upd
    keep = journal_read()
    have = {e['id'] for e in keep}; evs = [e for e in evs if e['id'] not in have]
    journal_add(evs, keep)
    if not DRY:
        if new: _save_seen(SEEN, seen | {r['id'] for r in new})
        if new_up: _save_seen(SEEN_UP, seen_up | {x['uid'] for x in new_up})
        if new_cl: _save_seen(SEEN_CL, seen_cl | {x['uid'] for x in new_cl})
        json.dump(new_st, open(UPD + '.tmp', 'w'), indent=0, sort_keys=True); os.replace(UPD + '.tmp', UPD)
    for k, lab in (('chg', 'change row'), ('up', 'new desk, first value or changelog entry'), ('upd', 'page update')):
        n = sum(1 for e in evs if e['kind'] == k)
        if n: print('alerts: %d new %s(s): %s' % (n, lab, ', '.join(sorted({e['name'] for e in evs if e['kind'] == k}))))
    return keep + evs


def alerts(m):
    n0 = len(journal_read()); jr = detect(m); fresh = len(jr) > n0
    if not jr: print('alerts: nothing in the journal'); return 0
    # the subscriber list is read on a pass that found something new, and otherwise at most once an hour (for digests that fall due, and
    # for a run that stopped part way)
    mark = os.path.join(OUT, '.last_list')
    if not fresh and os.path.exists(mark) and time.time() - os.path.getmtime(mark) < 3600 and not NOW:
        print('alerts: nothing new this pass, the list was read within the hour'); return 0
    subs = kv_list('al:')
    if not DRY: open(mark, 'w').close()
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    last = _load(DIGEST, {})
    # progress is kept per event and subscriber ('ev:<id>:<token prefix>'), so a run stopped part way never sends anyone an event twice
    pk = lambda uid, tok: 'ev:%s:%s' % (uid.replace(' ', '_'), tok[:12])
    plan = []
    for tok, r in sorted(subs, key=lambda x: x[0]):
        if not readable(tok, r): continue
        since = r.get('c') or r.get('at') or ''
        evs = [e for e in jr if e['at'] >= since and pk(e['id'], tok) not in done and wants(e, r, m)]
        if evs and due(r, tok, last): plan.append((tok, r, evs))
    print('alerts: %d confirmed subscriber(s), %d to email this run (at most %d)' % (len(subs), len(plan), CAP))
    recent = []
    for n, (tok, r, evs) in enumerate(plan[:CAP], 1):
        e = r.get('e', ''); guard_recipient(e)
        subject, t, h, hdr = alert_text(tok, r, evs, m)
        if DRY: print('--- DRY email, subject %r (placeholder token):\n%s' % (subject, t.replace(tok, 'x' * 40))); continue
        ok, err = send_one(e, subject, t, h, hdr)
        if not ok: log('STOPPED %s %s' % (tok[:12], err)); print('STOPPED at', tok[:12], err); sys.exit(2)
        with open(PROG, 'a') as f: f.write(''.join(pk(x['id'], tok) + '\n' for x in evs))
        if (r.get('f') or 'now') != 'now':
            last[tok[:12]] = _now().strftime('%Y-%m-%dT%H:%M:%SZ'); json.dump(last, open(DIGEST + '.tmp', 'w')); os.replace(DIGEST + '.tmp', DIGEST)
        log('ok %s (%d event(s), %s)' % (tok[:12], len(evs), r.get('f') or 'now')); recent.append(e)
        if n % 20 == 0 and not FAKE:
            import newsletter_send as NS
            time.sleep(90)
            try: st = NS.statuses(recent[-20:])
            except Exception as ex: log('STOPPED: delivery check failed (%s)' % type(ex).__name__); print('STOPPED: delivery check failed'); sys.exit(4)
            bad = sum(1 for v in st.values() if v[0] not in ('delivered', 'no record yet', 'queued', 'sent', 'pending'))
            log('CHECK last 20: %d not delivered' % bad)
            if bad > 2: print('STOPPED: more than 2 of the last 20 bounced'); log('STOPPED on bounce guard'); sys.exit(3)
        if n < min(CAP, len(plan)) and not FAKE: time.sleep(random.uniform(25, 75))
    if DRY: return 0
    log('run end: %d email(s)' % len(recent)); print('alerts: %d email(s) sent' % len(recent))
    return len(recent)


def main():
    if A[:1] != ['tick']: print(__doc__); return
    os.makedirs(OUT, exist_ok=True)
    rl = open(RUNLOCK, 'w')
    try: fcntl.flock(rl, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('alerts: another run holds the lock, nothing done'); return
    m = amap()
    confirmations(m)
    alerts(m)


if __name__ == '__main__': main()
