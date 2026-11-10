#!/usr/bin/env python3
"""push_send.py (10 Nov 2026): device notifications for indahl.ai (Web Push with VAPID), a tick-bus rider beside alerts_send.py.
Sign-up is in notify.js (/push/subscribe), the notification is shown by the service worker (public/sw.js). Encryption and the VAPID signature
are done by pywebpush (RFC 8291 aes128gcm, RFC 8292), never by hand. Run it with ~/bones-forge/notify_state/venv/bin/python.

  push_send.py tick           one short notification per device per new change row on the desks it follows (desk name, before to now, link)
  push_send.py tick --dry     what would be sent, nothing sent or recorded
  --ledger FILE / --state DIR / --kv FILE    scratch copies, for a test (as webhooks_send.py)
  --endpoint-override URL     send every notification to URL instead of the device's push service (a test with a local receiver)

The VAPID private key is read from ~/Documents/Heuremen LLC/ACCOUNTS/indahl_vapid_private.pem (chmod 600, outside every repository) and is
never printed. A push service answering 404 or 410 means the device unsubscribed: its record is deleted from the KV. Other failures are
logged and the row is not retried (a late notification is worse than none). One run at a time, at most 2,000 sends a run."""
import fcntl, json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import notify_events as NE
A = sys.argv[1:]
def arg(k, d=None): return A[A.index(k) + 1] if k in A else d
DRY = '--dry' in A
OUT = os.path.abspath(arg('--state', os.path.join(NE.STATE, 'push')))
LEDGER = os.path.abspath(arg('--ledger', os.path.join(NE.B, 'ledger', 'ledger.jsonl')))
KEY = os.path.expanduser(arg('--key', '~/Documents/Heuremen LLC/ACCOUNTS/indahl_vapid_private.pem'))
OVERRIDE = arg('--endpoint-override')
SEEN, LOG, RUNLOCK = (os.path.join(OUT, n) for n in ('seen_rows.json', 'send.log', '.run.lock'))
CAP = 50000; SUBJECT = 'mailto:indahl@heuremen.com'


def log(s):
    if DRY: return
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, 'a') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + s + '\n')


def payload(ev):
    """The notification: desk name and what changed, the desk link. Kept short, under the size every push service takes."""
    body = 'Before: %s. Now: %s.' % (NE.show(ev['before']), NE.show(ev['now']))
    return {'title': '%s: the headline changed' % ev['desk_name'], 'body': body[:180], 'url': ev['url'], 'tag': 'indahl-' + ev['desk']}


def main():
    if A[:1] != ['tick']: print(__doc__); return
    os.makedirs(OUT, exist_ok=True)
    rl = open(RUNLOCK, 'w')
    try: fcntl.flock(rl, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('push: another run holds the lock, nothing done'); return
    kv = NE.KV(arg('--kv'))
    try:
        rows = NE.change_rows(NE.ledger_rows(LEDGER))
        seen = NE.seen(SEEN, [r['id'] for r in rows], DRY, 'change rows', log)
        if seen is None: NE.status('push', True, 'first run'); return
        new = [r for r in rows if r['id'] not in seen]
        if not new: print('push: no new change rows'); NE.status('push', True, 'nothing new'); return
        subs = kv.list('ps:')
    except Exception as e:
        NE.status('push', False, 'the ledger or the device list could not be read: %s' % type(e).__name__); raise SystemExit('push: ' + str(e))
    print('push: %d new change row(s) on %s, %d device(s)' % (len(new), ', '.join(sorted({r['desk'] for r in new})), len(subs)))
    evs = [NE.event(r) for r in new]
    if not DRY:
        try:
            from pywebpush import webpush, WebPushException
            from py_vapid import Vapid
            vapid = Vapid.from_file(KEY)
        except Exception as e:
            NE.status('push', False, 'pywebpush or the VAPID key could not be loaded: %s' % type(e).__name__); raise SystemExit('push: cannot load the sender')
    sent = gone = bad = 0; done_ids = set()   # 10 Nov: events that reached at least one device get a public receipt (alert_receipts.py)
    for t, md in subs:
        mine = [e for e in evs if md.get('all') or e['desk'] in (md.get('d') or [])]
        for ev in mine:
            if sent >= CAP: break
            pl = payload(ev)
            if DRY: print('--- DRY push to device %s…: %s' % (t[:8], json.dumps(pl))); continue
            info = {'endpoint': OVERRIDE or md['e'], 'keys': {'p256dh': md['k']['p'], 'auth': md['k']['a']}}
            try:
                webpush(info, json.dumps(pl), vapid_private_key=vapid, vapid_claims={'sub': SUBJECT}, ttl=86400, timeout=10)
                sent += 1; done_ids.add(ev['id'])
            except WebPushException as e:
                code = getattr(e.response, 'status_code', None)
                if code in (404, 410):
                    kv.delete('ps:' + t); kv.delete('psh:' + NE_hash(md['e'])); kv.bump('psn', -1); gone += 1; log('GONE %s… (%s)' % (t[:8], code)); break
                bad += 1; log('FAIL %s… %s' % (t[:8], code or type(e).__name__))
            except Exception as e:
                bad += 1; log('FAIL %s… %s' % (t[:8], type(e).__name__))
    if not DRY:
        NE.save_seen(SEEN, seen | {r['id'] for r in new})
        log('run end: %d sent, %d gone, %d failed' % (sent, gone, bad))
        try:
            import alert_receipts as AR
            for ev in evs:
                if ev['id'] in done_ids: AR.record(ev, 'push')
        except Exception as e: log('receipt FAILED %s' % type(e).__name__); NE.status('push', False, 'alert receipt could not be written: %s' % type(e).__name__); return
    NE.status('push', True, '%d sent, %d gone, %d failed' % (sent, gone, bad))
    print('push: %d sent, %d device(s) gone, %d failed' % (sent, gone, bad))


def NE_hash(endpoint):
    """psh:<first 32 hex of sha256('psend|' + endpoint)>, as notify.js writes it."""
    import hashlib
    return hashlib.sha256(('psend|' + endpoint).encode()).hexdigest()[:32]


if __name__ == '__main__': main()
