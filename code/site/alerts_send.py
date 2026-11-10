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

What counts as a change: every live_value row live_headlines.py writes after a desk's baseline row. That is an outcome flip, or a new value
past the desk's material-change rule (outside the previous interval, or a field the plan's rule reads changed). A subscriber gets the rows of the
desks they ticked plus the desks with rows about the organisations they ticked, all of one run in ONE email. The first run of the sender marks
every row already in the ledger as seen, so it never mails history.

10 Nov 2026 (the combined sign-up form): a record with all = 1 follows every desk. A record with up = 1 also gets new desks and new data:
a desk's first value under the change rule, and a new desk page, read from weekly.py events (kinds 'first' and 'desk'), the same events
/week lists. Kept in seen_up.json like seen_rows.json (the first run marks every event already there as seen). One email per subscriber per
run holds both sections. An event is marked seen only when every subscriber who should get it has been sent it.

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
SUBS = arg('--subs'); WEEKSTATE = arg('--weekstate')
SEEN_UP = os.path.join(OUT, 'seen_up.json')
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
    """[(token, metadata)] for one KV prefix. Metadata holds the address: never printed."""
    if SUBS: return [tuple(x) for x in json.load(open(SUBS)).get(prefix, [])]
    import newsletter_send as NS
    rc, out = wr('kv', 'key', 'list', '--prefix', prefix, '--namespace-id', NS.NS, '--remote')
    if rc: raise SystemExit('alerts: the %s list could not be read (wrangler kv key list failed)' % prefix.rstrip(':'))
    return [(k['name'][len(prefix):], k.get('metadata') or {}) for k in json.loads(out[out.index('['):])]


def postal():
    try: return open(POSTAL_FILE, encoding='utf-8').read().strip().splitlines()[0].strip()
    except Exception: return ''


def amap():
    return json.load(open(MAP))


def _names(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def send_one(to, subject, t, h, hdr):
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


def guard_recipient(e):
    if '@' not in e: raise SystemExit('alerts: a record carries no address; nothing sent')
    if TEST and not e.lower().endswith('@heuremen.com'): raise SystemExit('alerts: --test and a recipient outside heuremen.com; nothing sent')


# ------------------------------------------------------------------------------------------------ confirmations
def follows(d, o, m, al=False):
    if al: return 'every desk'
    what = []
    if d: what.append(('the desk ' if len(d) == 1 else 'the desks ') + _names(m['desks'][s][0] for s in d if s in m['desks']))
    if o: what.append('the desks with rows about ' + _names(m['brands'][s][0] for s in o if s in m['brands']))
    return _names(what) if what else ''


def asks(d, o, m, al, up):
    w = follows(d, o, m, al); p = []
    if w: p.append('when an outcome changes on ' + w)
    if up: p.append('when a new desk goes live or a desk publishes its first value')
    return ', and '.join(p)


def confirm_text(ptok, d, o, m, al=False, up=False):
    url = '%s/alerts/confirm?t=%s' % (SITE, ptok)
    body = ('This address was entered on indahl.ai to get an email %s.\n\n'
            'To start these emails, open this link and press Confirm:\n%s\n\n'
            'The link works for two days. If you did not ask for this, ignore this email. Nothing more will be sent.' % (asks(d, o, m, al, up), url))
    foot = ['Heuremen LLC'] + ([postal()] if postal() else []) + ['Privacy: %s/privacy#alerts' % SITE]
    return wrap(body, foot)


def confirmations(m):
    pend = kv_list('alp:')
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    todo = [(t, md) for t, md in sorted(pend, key=lambda x: x[1].get('at', '')) if 'confirm:%s' % t[:12] not in done]
    print('alerts: %d sign-up(s) waiting for a confirmation email' % len(todo))
    sent = 0
    for n, (t, md) in enumerate(todo[:CAP]):
        e = md.get('e', ''); guard_recipient(e)
        txt, h = confirm_text(t, md.get('d') or [], md.get('o') or [], m, bool(md.get('all')), bool(md.get('up')))
        if DRY: print('--- DRY confirmation (placeholder token):\n' + txt.replace(t, 'x' * 40)); continue
        ok, err = send_one(e, 'Confirm your indahl.ai email alerts', txt, h, [])
        if not ok: log('STOPPED confirm:%s %s' % (t[:12], err)); print('STOPPED at confirm', t[:12], err); sys.exit(2)
        with open(PROG, 'a') as f: f.write('confirm:%s\n' % t[:12])
        log('ok confirm:%s' % t[:12]); sent += 1
        if n + 1 < min(CAP, len(todo)): time.sleep(random.uniform(25, 75))
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


def alert_text(tok, chs, d, o, m, al=False, ups=(), up=False):
    import live_headlines as LH
    blocks = []
    for ch in chs:
        b = describe(ch)
        why = [m['brands'][s][0] for s in o if s in m['brands'] and ch['desk'] in m['brands'][s][1]]
        if not al and ch['desk'] not in d and why: b += '\nYou follow %s, which has rows on this desk.' % _names(why)
        blocks.append(b)
    names = list(dict.fromkeys(LH.DESKS.get(ch['desk'], {}).get('name', ch['desk'].upper()) for ch in chs))
    parts = []
    if chs:
        parts.append(('An outcome changed on a desk you follow on indahl.ai.\n\n' if len(chs) == 1 else 'Outcomes changed on desks you follow on indahl.ai.\n\n') + '\n\n'.join(blocks))
    if ups:
        parts.append(('New on indahl.ai.\n\n' if not chs else 'Also new on indahl.ai.\n\n') + '\n\n'.join(describe_up(x) for x in ups))
    body = '\n\n'.join(parts)
    if chs: subject = ('Outcome change on ' if len(chs) == 1 else 'Outcome changes on ') + _names(names) + (', and new on indahl.ai' if ups else '')
    else:
        nd = [x for x in ups if x['kind'] == 'desk']
        subject = 'New on indahl.ai: ' + _names(list(dict.fromkeys(x['desk'] for x in ups))) if len(ups) <= 3 else 'New desks and new data on indahl.ai' if nd else 'New data on indahl.ai'
    follow = []
    w = follows(d, o, m, al)
    if w: follow.append('outcome changes on ' + w)
    if up: follow.append('new desks and new data')
    manage, unsub = '%s/alerts/manage?t=%s' % (SITE, tok), '%s/alerts/unsubscribe?t=%s' % (SITE, tok)
    foot = (['Heuremen LLC'] + ([postal()] if postal() else [])
            + ['You are receiving this because this address confirmed email from indahl.ai for %s.' % _names(follow),
               'Change what you get or unsubscribe: ' + manage, 'Unsubscribe with one click: ' + unsub, 'Privacy: %s/privacy#alerts' % SITE])
    t, h = wrap(body, foot)
    return subject, t, h, ['List-Unsubscribe:<%s>' % unsub, 'List-Unsubscribe-Post:List-Unsubscribe=One-Click']


def _read_seen(path, ids, label):
    """The seen set, or None on the first run (which marks every id seen and sends nothing)."""
    if os.path.exists(path): return set(json.load(open(path)))
    if not DRY:
        os.makedirs(OUT, exist_ok=True); json.dump(sorted(ids), open(path, 'w'), indent=0)
        log('first run (%s): %d existing marked seen, nothing sent' % (label, len(ids)))
    print('alerts: first run for %s, %d existing marked seen, nothing sent' % (label, len(ids))); return None


def alerts(m):
    rows = value_rows()
    seen = _read_seen(SEEN, [r['id'] for r in rows], 'change rows')
    new = [r for r in rows if r['id'] not in seen] if seen is not None else []
    try: ups_all = up_events(_ledger_rows())
    except Exception as ex: print('alerts: new desks and new data could not be read (%s), none this run' % type(ex).__name__); ups_all = None
    seen_up = _read_seen(SEEN_UP, [x['uid'] for x in ups_all], 'new desks and new data') if ups_all is not None else None
    new_up = [x for x in ups_all if x['uid'] not in seen_up] if seen_up is not None else []
    if not new and not new_up: print('alerts: no new change rows and no new desks or first values'); return 0
    if new: print('alerts: %d new change row(s) on %s' % (len(new), ', '.join(sorted({r['desk'] for r in new}))))
    if new_up: print('alerts: %d new desk(s) or first value(s): %s' % (len(new_up), ', '.join(x['desk'] for x in new_up)))
    subs = kv_list('al:')
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    # progress is kept per event and subscriber ('ev:<id>:<token prefix>'), so a run stopped part way, or new events arriving before the
    # next run, never send anyone an event twice (no older batch keys were ever written: no alert had been sent before this change)
    pk = lambda uid, tok: 'ev:%s:%s' % (uid.replace(' ', '_'), tok[:12])
    def had(uid, tok): return pk(uid, tok) in done
    plan = []
    for tok, md in sorted(subs, key=lambda x: x[0]):
        d, o, al, up = md.get('d') or [], md.get('o') or [], bool(md.get('all')), bool(md.get('up'))
        follow = set(d) | {x for s in o if s in m['brands'] for x in m['brands'][s][1]}
        chs = [r for r in new if (al or r['desk'] in follow) and not had(r['id'], tok)]
        ups = [x for x in new_up if not had(x['uid'], tok)] if up else []
        if chs or ups: plan.append((tok, md, chs, ups))
    print('alerts: %d confirmed subscriber(s), %d to email this run (at most %d)' % (len(subs), len(plan), CAP))
    recent = []
    for n, (tok, md, chs, ups) in enumerate(plan[:CAP], 1):
        e = md.get('e', ''); guard_recipient(e)
        subject, t, h, hdr = alert_text(tok, chs, md.get('d') or [], md.get('o') or [], m, bool(md.get('all')), ups, bool(md.get('up')))
        if DRY: print('--- DRY email, subject %r (placeholder token):\n%s' % (subject, t.replace(tok, 'x' * 40))); continue
        ok, err = send_one(e, subject, t, h, hdr)
        if not ok: log('STOPPED %s %s' % (tok[:12], err)); print('STOPPED at', tok[:12], err); sys.exit(2)
        with open(PROG, 'a') as f: f.write(''.join(pk(x, tok) + '\n' for x in [r['id'] for r in chs] + [x['uid'] for x in ups]))
        log('ok %s (%d row(s), %d update(s))' % (tok[:12], len(chs), len(ups))); recent.append(e)
        if n % 20 == 0:
            import newsletter_send as NS
            time.sleep(90)
            try: st = NS.statuses(recent[-20:])
            except Exception as ex: log('STOPPED: delivery check failed (%s)' % type(ex).__name__); print('STOPPED: delivery check failed'); sys.exit(4)
            bad = sum(1 for v in st.values() if v[0] not in ('delivered', 'no record yet', 'queued', 'sent', 'pending'))
            log('CHECK last 20: %d not delivered' % bad)
            if bad > 2: print('STOPPED: more than 2 of the last 20 bounced'); log('STOPPED on bounce guard'); sys.exit(3)
        if n < min(CAP, len(plan)): time.sleep(random.uniform(25, 75))
    if DRY: return 0
    if len(plan) <= CAP:   # every subscriber who should get these has them: mark them seen
        if new: json.dump(sorted(seen | {r['id'] for r in new}), open(SEEN + '.tmp', 'w'), indent=0); os.replace(SEEN + '.tmp', SEEN)
        if new_up: json.dump(sorted(seen_up | {x['uid'] for x in new_up}), open(SEEN_UP + '.tmp', 'w'), indent=0); os.replace(SEEN_UP + '.tmp', SEEN_UP)
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
