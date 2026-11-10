#!/usr/bin/env python3
"""webhooks_send.py (10 Nov 2026): the indahl.ai webhooks sender, a tick-bus rider beside alerts_send.py. Registration is in notify.js.

  python3 -I webhooks_send.py tick         queue new change rows for every webhook that follows their desk, then try every delivery that is due
  python3 -I webhooks_send.py tick --dry   what would be queued and sent, with no POST, no KV write and no state change
  --ledger FILE   read value rows from FILE instead of ledger/ledger.jsonl (a scratch copy, for a test)
  --state DIR     keep the queue and seen files in DIR instead of ~/bones-forge/notify_state/webhooks (a scratch folder, for a test)
  --kv FILE       a JSON file standing in for the private KV (a test)
  --allow-local   let a test deliver to http://127.0.0.1 (a local listener). Never used on the bus.

Events: the same change rows as the outcome alerts and the desk change feeds (notify_events.py). One delivery per webhook per run holds every
new event for it. A signed webhook gets {"type": "outcome_change", "events": [...]} with the headers X-Indahl-Event, X-Indahl-Delivery,
X-Indahl-Timestamp and X-Indahl-Signature: v1=<hex HMAC-SHA256 of "<timestamp>.<body>" under the webhook's secret>. Slack, Discord and Teams
addresses get a plain message in the app's own format (notify.js chatBody), one per event.
Retries: a delivery that gets no 2xx answer within 10 seconds is tried again about 5 minutes, 30 minutes, 2 hours and 6 hours later
(on the first tick after each), then dropped. After 10 failed attempts in a row on one webhook it is turned off: the KV record gets off (the
time) and f (the count), its manage page says so, and its queued deliveries are dropped. A success sets the count back to 0.
Guards: one run at a time (its own lock), at most 200 POSTs a run, redirects are not followed, an address that is not https or names an IP or a
private host is never posted to (the same rules as notify.js checkUrl). Addresses and secrets are never printed or logged."""
import fcntl, hashlib, hmac, ipaddress, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error, uuid
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import notify_events as NE
A = sys.argv[1:]
def arg(k, d=None): return A[A.index(k) + 1] if k in A else d
DRY, LOCAL = '--dry' in A, '--allow-local' in A
OUT = os.path.abspath(arg('--state', os.path.join(NE.STATE, 'webhooks')))
LEDGER = os.path.abspath(arg('--ledger', os.path.join(NE.B, 'ledger', 'ledger.jsonl')))
SEEN, QUEUE, FAILS, LOG, RUNLOCK = (os.path.join(OUT, n) for n in ('seen_rows.json', 'queue.json', 'fails.json', 'send.log', '.run.lock'))
DELAYS = [300, 1800, 7200, 21600]   # after attempts 1, 2, 3 and 4. Attempt 5 failing drops the delivery.
OFF_AFTER = 10; CAP = 200; UA = 'indahl.ai-webhooks/1.0 (+https://indahl.ai/webhooks)'
BADHOST = re.compile(r'(^localhost$|\.(localhost|local|localdomain|internal|intranet|lan|home|corp|private|arpa|test|invalid|example|onion)$)')


def log(s):
    if DRY: return
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')


def jload(p, d):
    try: return json.load(open(p))
    except Exception: return d


def jsave(p, o):
    if DRY: return
    json.dump(o, open(p + '.tmp', 'w'), indent=0, sort_keys=True); os.replace(p + '.tmp', p)


def url_ok(u):
    try: x = urllib.parse.urlsplit(u)
    except Exception: return False
    h = (x.hostname or '').lower().rstrip('.')
    if LOCAL and x.scheme == 'http' and h == '127.0.0.1': return True
    if x.scheme != 'https' or x.username or x.password or (x.port not in (None, 443)) or not h or '.' not in h or BADHOST.search(h): return False
    try: ipaddress.ip_address(h.strip('[]')); return False
    except ValueError: pass
    if re.search(r'\.\d+$', h) or h == 'indahl.ai' or h.endswith('.indahl.ai'): return False
    return resolves_public(h)


def resolves_public(h):
    """Every address the name resolves to must be on the public internet: this sender runs inside a home network, so a public name that
    points at a private, loopback, link-local, shared or multicast address is refused. Checked again before every attempt."""
    import socket
    try: infos = socket.getaddrinfo(h, 443, proto=socket.IPPROTO_TCP)
    except Exception: return False
    addrs = {i[4][0] for i in infos}
    try: return bool(addrs) and all(ipaddress.ip_address(a.split('%')[0]).is_global for a in addrs)
    except ValueError: return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
OPEN = urllib.request.build_opener(NoRedirect)


def sign(secret, ts, body):
    return 'v1=' + hmac.new(secret.encode(), ('%d.' % ts).encode() + body, hashlib.sha256).hexdigest()


def chat_body(kind, text):
    if kind == 'discord': return {'content': text[:1900], 'allowed_mentions': {'parse': []}}
    if kind == 'slack': return {'text': text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}
    return {'text': text}


def post(u, body, headers):
    if not url_ok(u): return False, 'refused address'
    req = urllib.request.Request(u, data=body, method='POST', headers=dict({'content-type': 'application/json', 'user-agent': UA}, **headers))
    try:
        with OPEN.open(req, timeout=10) as r: code = r.status
    except urllib.error.HTTPError as e: code = e.code
    except Exception as e: return False, type(e).__name__
    return 200 <= code <= 299, 'status %d' % code


def deliver(rec, evs, done=None):
    """-> (ok, why). rec is the full KV record (value). For a chat app each event is one message: done (a list in the queue item) collects
    the event ids already accepted, so a retry after a partial failure sends only the ones still missing, never a message twice."""
    if rec.get('k') in ('slack', 'discord', 'teams'):
        done = done if done is not None else []
        for ev in evs:
            if ev['id'] in done: continue
            t = 'indahl.ai outcome change\n' + NE.text(ev)
            ok, why = post(rec['u'], json.dumps(chat_body(rec['k'], t)).encode(), {})
            if not ok: return ok, why
            done.append(ev['id'])
        return True, 'ok'
    body = json.dumps({'type': 'outcome_change', 'events': evs, 'sent_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}, ensure_ascii=False, separators=(',', ':')).encode()
    ts = int(time.time())
    return post(rec['u'], body, {'x-indahl-event': 'outcome_change', 'x-indahl-delivery': str(uuid.uuid4()), 'x-indahl-timestamp': str(ts), 'x-indahl-signature': sign(rec['s'], ts, body)})


def main():
    if A[:1] != ['tick']: print(__doc__); return
    os.makedirs(OUT, exist_ok=True)
    rl = open(RUNLOCK, 'w')
    try: fcntl.flock(rl, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('webhooks: another run holds the lock, nothing done'); return
    kv = NE.KV(arg('--kv'))
    try:
        rows = NE.change_rows(NE.ledger_rows(LEDGER))
        seen = NE.seen(SEEN, [r['id'] for r in rows], DRY, 'change rows', log)
        queue = jload(QUEUE, []); fails = jload(FAILS, {})
        if not queue and (seen is None or not [r for r in rows if r['id'] not in seen]):   # nothing to send: the KV is not read
            NE.status('webhooks', True, 'nothing to send'); print('webhooks: nothing new and nothing queued'); return
        subs = dict(kv.list('wh:'))
    except Exception as e:
        NE.status('webhooks', False, 'the ledger or the webhook list could not be read: %s' % type(e).__name__); raise SystemExit('webhooks: ' + str(e))
    now = time.time()
    # a webhook its owner turned back on (no off in the KV record) starts again from 0
    for t in list(fails):
        if t not in subs or (fails[t].get('off') and not subs[t].get('off')): fails.pop(t)
    if seen is not None:
        new = [r for r in rows if r['id'] not in seen]
        if new: print('webhooks: %d new change row(s) on %s' % (len(new), ', '.join(sorted({r['desk'] for r in new}))))
        for t, md in sorted(subs.items()):
            if md.get('off'): continue
            evs = [NE.event(r) for r in new if md.get('all') or r['desk'] in (md.get('d') or [])]
            if evs: queue.append({'t': t, 'events': evs, 'n': 0, 'next': now, 'first': now})
        seen |= {r['id'] for r in new}
    due = [q for q in queue if q['next'] <= now and q['t'] in subs and not subs[q['t']].get('off')]
    print('webhooks: %d webhook(s), %d delivery(s) queued, %d due' % (len(subs), len(queue), len(due)))
    recs, sent, keep = {}, 0, []
    for q in queue:
        if q not in due or sent >= CAP or time.time() - now > 240:   # at most 200 POSTs and about 4 minutes a run, the rest wait for the next tick
            if q['t'] in subs and not subs[q['t']].get('off'): keep.append(q)
            continue
        t = q['t']
        if DRY: print('--- DRY delivery to webhook %s… (%s), %d event(s): %s' % (t[:8], subs[t].get('k'), len(q['events']), ', '.join(e['desk'] for e in q['events']))); keep.append(q); continue
        if t not in recs:
            v = kv.get('wh:' + t)
            try: recs[t] = json.loads(v) if v else None
            except ValueError: recs[t] = None
        rec = recs[t]
        if not rec: continue
        ok, why = deliver(rec, q['events'], q.setdefault('done', [])); sent += 1; q['n'] += 1
        f = fails.setdefault(t, {'n': 0})
        if ok:
            f['n'] = 0; log('ok %s… attempt %d, %d event(s)' % (t[:8], q['n'], len(q['events']))); continue
        f['n'] += 1; log('FAIL %s… attempt %d (%s), %d in a row' % (t[:8], q['n'], why, f['n']))
        if f['n'] >= OFF_AFTER:
            rec['off'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); rec['f'] = f['n']; f['off'] = rec['off']
            md = {k: rec[k] for k in ('u', 'k', 'd', 'at', 'all', 'off', 'f') if k in rec}
            kv.put('wh:' + t, json.dumps(rec, separators=(',', ':')), md); subs[t]['off'] = rec['off']
            log('TURNED OFF %s… after %d failed attempts in a row' % (t[:8], f['n'])); continue
        if q['n'] <= len(DELAYS): q['next'] = now + DELAYS[q['n'] - 1]; keep.append(q)
        else: log('DROPPED %s… delivery after %d attempts' % (t[:8], q['n']))
    keep = [q for q in keep if not subs.get(q['t'], {}).get('off')]
    if not DRY:
        if seen is not None: NE.save_seen(SEEN, seen)
        jsave(QUEUE, keep); jsave(FAILS, fails)
    NE.status('webhooks', True, '%d sent' % sent)
    print('webhooks: %d POST(s) this run, %d delivery(s) left in the queue' % (sent, len(keep)))


if __name__ == '__main__': main()
