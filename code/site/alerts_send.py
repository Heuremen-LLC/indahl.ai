#!/usr/bin/env python3
"""alerts_send.py (10 Nov 2026): outcome alerts for indahl.ai, sent through Cloudflare Email Sending (heuremen.com: DKIM, SPF and DMARC pass,
bounces to cf-bounce.heuremen.com) on the same path, pacing and guards as newsletter_send.py and send_guarded.py.

  python3 -I alerts_send.py tick          the tick-bus rider: confirmation links for new sign-ups, then alerts for new value rows
  python3 -I alerts_send.py tick --dry    what would go out: counts, desks and the text with a placeholder token. Nothing sent or recorded.
  --ledger FILE    read value rows from FILE instead of ledger/ledger.jsonl (a scratch copy, for a test)
  --state DIR      keep the progress files in DIR instead of ~/bones-forge/outcome_alerts (a scratch folder, for a test)
  --test           refuse to send unless every recipient is an address at heuremen.com

What counts as a change: every live_value row live_headlines.py writes after a desk's baseline row. That is an outcome flip, or a new value
past the desk's material-change rule (outside the previous interval, or a field the plan's rule reads changed). A subscriber gets the rows of the
desks they ticked plus the desks with rows about the organisations they ticked, all of one run in ONE email. The first run of the sender marks
every row already in the ledger as seen, so it never mails history.

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
def confirm_text(ptok, d, o, m):
    what = []
    if d: what.append(('the desk ' if len(d) == 1 else 'the desks ') + _names(m['desks'][s][0] for s in d if s in m['desks']))
    if o: what.append('the desks with rows about ' + _names(m['brands'][s][0] for s in o if s in m['brands']))
    url = '%s/alerts/confirm?t=%s' % (SITE, ptok)
    body = ('This address was entered on indahl.ai to get an email when an outcome changes on %s.\n\n'
            'To start the alerts, open this link and press Confirm:\n%s\n\n'
            'The link works for two days. If you did not ask for this, ignore this email. Nothing more will be sent.' % (_names(what), url))
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
        txt, h = confirm_text(t, md.get('d') or [], md.get('o') or [], m)
        if DRY: print('--- DRY confirmation (placeholder token):\n' + txt.replace(t, 'x' * 40)); continue
        ok, err = send_one(e, 'Confirm your indahl.ai outcome alerts', txt, h, [])
        if not ok: log('STOPPED confirm:%s %s' % (t[:12], err)); print('STOPPED at confirm', t[:12], err); sys.exit(2)
        with open(PROG, 'a') as f: f.write('confirm:%s\n' % t[:12])
        log('ok confirm:%s' % t[:12]); sent += 1
        if n + 1 < min(CAP, len(todo)): time.sleep(random.uniform(25, 75))
    return sent


# ------------------------------------------------------------------------------------------------ alerts
def value_rows():
    """Every non-baseline live_value row, oldest first, each with the row before it on the same desk."""
    lk = open(LH_LOCK, 'a'); fcntl.flock(lk, fcntl.LOCK_SH)   # live_headlines.py writes under LOCK_EX on this file
    try: rows = [json.loads(l) for l in open(LEDGER, encoding='utf-8') if l.strip()]
    finally: fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    vals = [r for r in rows if r.get('kind') == 'live_value' and r.get('reading') and r.get('live_of', '').startswith('live.')]
    vals.sort(key=lambda r: r['history'][0]['at'])
    out, last = [], {}
    for r in vals:
        desk = r['live_of'].split('.')[1]; prev = last.get(desk); last[desk] = r
        if prev is None or str(r['history'][0].get('why', '')).startswith('baseline'): continue
        out.append(dict(id=r['id'], desk=desk, prev=prev['reading'], cur=r['reading'], at=r['history'][0]['at']))
    return out


def describe(ch):
    import live_headlines as LH, changes_feed as CF
    spec = LH.DESKS.get(ch['desk'], {}); p, c = ch['prev'], ch['cur']
    return '%s: %s\nBefore: %s. Now: %s, at the feed time %s. %s\n%s/%s' % (
        spec.get('name', ch['desk'].upper()), LH.H2.get(ch['desk'], ''), CF._show(p), CF._show(c), c.get('stamp') or ch['at'][:16], CF._why(spec, p, c), SITE, ch['desk'])


def alert_text(tok, chs, d, o, m):
    import live_headlines as LH
    blocks = []
    for ch in chs:
        b = describe(ch)
        why = [m['brands'][s][0] for s in o if s in m['brands'] and ch['desk'] in m['brands'][s][1]]
        if ch['desk'] not in d and why: b += '\nYou follow %s, which has rows on this desk.' % _names(why)
        blocks.append(b)
    names = list(dict.fromkeys(LH.DESKS.get(ch['desk'], {}).get('name', ch['desk'].upper()) for ch in chs))
    subject = 'Outcome change on ' + _names(names) if len(chs) == 1 else 'Outcome changes on ' + _names(names)
    body = ('An outcome changed on a desk you follow on indahl.ai.\n\n' if len(chs) == 1 else 'Outcomes changed on desks you follow on indahl.ai.\n\n') + '\n\n'.join(blocks)
    follow = []
    if d: follow.append(_names(m['desks'][s][0] for s in d if s in m['desks']))
    if o: follow.append('the desks with rows about ' + _names(m['brands'][s][0] for s in o if s in m['brands']))
    manage, unsub = '%s/alerts/manage?t=%s' % (SITE, tok), '%s/alerts/unsubscribe?t=%s' % (SITE, tok)
    foot = (['Heuremen LLC'] + ([postal()] if postal() else [])
            + ['You are receiving this because this address confirmed outcome alerts on indahl.ai for %s.' % _names(follow),
               'Manage your desks or unsubscribe: ' + manage, 'Unsubscribe with one click: ' + unsub, 'Privacy: %s/privacy#alerts' % SITE])
    t, h = wrap(body, foot)
    return subject, t, h, ['List-Unsubscribe:<%s>' % unsub, 'List-Unsubscribe-Post:List-Unsubscribe=One-Click']


def alerts(m):
    rows = value_rows()
    if not os.path.exists(SEEN):
        if not DRY:
            os.makedirs(OUT, exist_ok=True); json.dump(sorted(r['id'] for r in rows), open(SEEN, 'w'), indent=0)
            log('first run: %d existing change rows marked seen, nothing sent' % len(rows))
        print('alerts: first run, %d existing change rows marked seen, nothing sent' % len(rows)); return 0
    seen = set(json.load(open(SEEN)))
    new = [r for r in rows if r['id'] not in seen]
    if not new: print('alerts: no new change rows'); return 0
    print('alerts: %d new change row(s) on %s' % (len(new), ', '.join(sorted({r['desk'] for r in new}))))
    subs = kv_list('al:')
    done = set(open(PROG).read().split()) if os.path.exists(PROG) else set()
    batch = 'rows-' + new[0]['id'] + '-' + new[-1]['id']
    plan = []
    for tok, md in sorted(subs, key=lambda x: x[0]):
        d, o = md.get('d') or [], md.get('o') or []
        follow = set(d) | {x for s in o if s in m['brands'] for x in m['brands'][s][1]}
        chs = [r for r in new if r['desk'] in follow]
        if chs and '%s:%s' % (batch, tok[:12]) not in done: plan.append((tok, md, chs))
    print('alerts: %d confirmed subscriber(s), %d to email this run (at most %d)' % (len(subs), len(plan), CAP))
    recent = []
    for n, (tok, md, chs) in enumerate(plan[:CAP], 1):
        e = md.get('e', ''); guard_recipient(e)
        subject, t, h, hdr = alert_text(tok, chs, md.get('d') or [], md.get('o') or [], m)
        if DRY: print('--- DRY alert, subject %r (placeholder token):\n%s' % (subject, t.replace(tok, 'x' * 40))); continue
        ok, err = send_one(e, subject, t, h, hdr); pk = '%s:%s' % (batch, tok[:12])
        if not ok: log('STOPPED %s %s' % (pk, err)); print('STOPPED at', pk, err); sys.exit(2)
        with open(PROG, 'a') as f: f.write(pk + '\n')
        log('ok %s (%d row(s))' % (pk, len(chs))); recent.append(e)
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
    if len(plan) <= CAP:   # every subscriber who follows these rows has them: mark the rows seen
        json.dump(sorted(seen | {r['id'] for r in new}), open(SEEN + '.tmp', 'w'), indent=0); os.replace(SEEN + '.tmp', SEEN)
    log('run end: %d alert email(s), batch %s' % (len(recent), batch)); print('alerts: %d alert email(s) sent' % len(recent))
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
