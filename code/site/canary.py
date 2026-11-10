#!/usr/bin/env python3
"""canary.py (10 Nov 2026): our own subscriptions on every follow channel, checked against the alert receipts each pass. Tick-bus rider.

Canaries (notify_state/canary.json, mode 600, never published):
  webhook  a signed webhook registered through the public /webhooks form to https://indahl.ai/canary/hook, every desk. The worker keeps a
           delivery (KV IRIS_BENCH canary_hook_log, newest 100) only when its Ed25519 signature verifies, and notes whether the HMAC matched.
  email    a plus-address on our own mailbox, signed up through the public footer form and confirmed by us (every box). This machine has no
           mailbox reader, so its arrivals are checked in a session and the rider reports it as not checked automatically.
  push     a browser subscription needs a running browser with a push service connection to receive. No headless setup can keep one, so
           there is no push canary. The rider says so.
Each pass, for every alert receipt that went out on a canary's channel after the canary started:
  MISSING   no delivery of that event reached the canary within the stated cadence plus slack (DEADLINE)
  LATE      it arrived, later than the deadline
  MISMATCH  the canary got an event that has no receipt, or a delivery whose shared-secret signature did not match
Any of these writes notify_state/canary_status.json with ok false, which watch/alerts_check.py turns into a Bones alert.
Canary sign-ups are left out of every transparency count (transparency.py reads the token prefixes here).

  python3 canary.py tick [--dry] [--log FILE] [--receipts FILE] [--now ISO]   --log / --receipts stand in for the KV log and the receipt chain (a test)
Python 3.9, standard library only."""
import datetime as D, json, os, re, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import alert_receipts as AR
CFG = os.path.join(AR.STATE, 'canary.json'); STATUS = os.path.join(AR.STATE, 'canary_status.json'); PUBLIC = os.path.join(AR.STATE, 'canary_public.json')
DEADLINE = 30 * 60   # webhooks_send.py runs every tick (about 5 minutes), plus 25 minutes for a retry and the KV write
A = sys.argv[1:]; DRY = '--dry' in A
def arg(k, d=None): return A[A.index(k) + 1] if k in A else d
def ts(iso): return D.datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp()


def kv_get(key):
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'get', key, '--namespace-id', AR.NS_PUBLIC, '--remote', '--text'], cwd=AR.W, env=env, capture_output=True, text=True, timeout=180)
    if r.returncode: return None
    return r.stdout.strip()


def check(cfg, log, receipts, now):
    out = {'webhook': [], 'email': [], 'push': []}
    wh = cfg.get('webhook') or {}
    if wh.get('since'):
        got = {}
        for d in log:
            for e in d.get('events', []):
                got.setdefault(AR.rid_slug(e), d)
            if d.get('hmac') is False: out['webhook'].append(('MISMATCH', d.get('delivery', '?'), 'shared-secret signature did not match'))
        rids = {r['id'] for r in receipts}
        for k, d in got.items():
            if k not in rids: out['webhook'].append(('MISMATCH', k, 'delivered to the canary, no receipt'))
        for r in receipts:
            if r.get('kind') != 'outcome_change' or 'webhook' not in r.get('channels', []) or not r.get('first_sent_at'): continue
            sent = ts((r.get('sent_at') or {}).get('webhook') or r['first_sent_at'])
            if sent < ts(wh['since']): continue
            d = got.get(r['id'])
            if d is None:
                if now - sent > DEADLINE: out['webhook'].append(('MISSING', r['id'], 'no delivery %d min after it went out' % ((now - sent) // 60)))
            elif ts(d['at']) - sent > DEADLINE: out['webhook'].append(('LATE', r['id'], 'arrived %d min after it went out' % ((ts(d['at']) - sent) // 60)))
    return out


def main():
    if A[:1] != ['tick']: print(__doc__); return 0
    try: cfg = json.load(open(CFG))
    except Exception: cfg = {}
    now = ts(arg('--now')) if arg('--now') else time.time()
    if arg('--log'): log = json.load(open(arg('--log')))
    elif not (cfg.get('webhook') or {}).get('since'): log = []   # no webhook canary yet: nothing to read
    else:
        v = kv_get('canary_hook_log')
        if v is None: return status(False, 'the canary log could not be read from the KV', {})
        try: log = json.loads(v[v.index('['):] if '[' in v else '[]')
        except Exception: return status(False, 'the canary log could not be parsed', {})
    if arg('--receipts'): receipts = json.load(open(arg('--receipts')))
    else: receipts = list(AR._load_chain()[0].values())
    res = check(cfg, log, receipts, now)
    bad = [(ch,) + x for ch, xs in res.items() for x in xs]
    for b in bad: print('canary: %s %s %s: %s' % b)
    pub = [{'channel': 'Webhook', 'checked': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now)), 'result': ('every alert arrived within %d minutes' % (DEADLINE // 60)) if not res['webhook'] else '%d problem(s): %s' % (len(res['webhook']), ', '.join(sorted({x[0].lower() for x in res['webhook']})))} if (cfg.get('webhook') or {}).get('since') else {'channel': 'Webhook', 'result': 'not set up'},
           {'channel': 'Email', 'result': 'set up, arrivals checked in a review session, not automatically' if (cfg.get('email') or {}).get('since') else 'not set up'},
           {'channel': 'Device notification', 'result': 'none: a test device would need a browser running at all times'}]
    if not DRY: json.dump(pub, open(PUBLIC, 'w'), indent=1)
    print('canary: %d receipts, %d canary deliveries, %d problem(s)' % (len(receipts), len(log), len(bad)))
    return status(not bad, '; '.join('%s %s %s' % (b[0], b[1], b[2]) for b in bad[:6]) or 'ok', res)


def status(ok, what, res):
    if not DRY: json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': bool(ok), 'what': what[:300]}, open(STATUS, 'w'))
    else: print('DRY status: ok=%s %s' % (ok, what))
    return 0 if ok else 1


if __name__ == '__main__': sys.exit(main())
