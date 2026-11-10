#!/usr/bin/env python3
"""transparency.py (10 Nov 2026): the aggregate counts behind https://indahl.ai/transparency. Tick-bus rider (about hourly).

Counted over the last WINDOW days, by UTC day, for everyone together:
  alerts            alert events by desk (alert receipt chain, notify_state/alert_receipts.jsonl)
  email, confirm    alert emails and confirmation emails sent (outcome_alerts/send.log lines "ok <token>" and "ok confirm:<token>")
  webhook           webhook deliveries accepted (notify_state/webhooks/send.log "ok"), webhooks_off ("TURNED OFF")
  push              device notifications sent (notify_state/push/send.log "run end: N sent")
  unsub_alerts, unsub_newsletter, webhooks_deleted, push_removed
                    records that were in the private KV at the last pass and are gone now (unsubscribed, deleted or expired), from a local
                    snapshot that keeps only one-way hashes of the keys (notify_state/transparency_snap.json)
  deletions         deletion receipts written by the Your data buttons (KV delr:, kind and time only)
Not recorded yet, and said so on the page: bounces (the sender keeps a rolling check, not a count per message) and refused sign-ups (the
worker does not log refusals). Every cell under 5 is written as "fewer than 5" before anything leaves this machine. Our own canary
sign-ups (notify_state/canary.json) are left out of every count. Output: KV IRIS_BENCH transparency, and notify_state/transparency.json.

  python3 transparency.py tick [--dry] [--no-kv]      --no-kv skips the private KV reads (snapshot and deletions)
  python3 transparency.py selftest                     the suppression rule on a planted table
Python 3.9, standard library only."""
import collections as C, datetime as D, hashlib, json, os, re, sys, time
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H); sys.path.insert(0, H)
import alert_receipts as AR
WINDOW = 30; MIN = 5; FEW = 'fewer than 5'
SNAP = os.path.join(AR.STATE, 'transparency_snap.json'); EVENTS = os.path.join(AR.STATE, 'transparency_events.jsonl'); OUT = os.path.join(AR.STATE, 'transparency.json')
STATUS = os.path.join(AR.STATE, 'transparency_status.json')
LOGS = {'email': os.path.join(B, 'outcome_alerts', 'send.log'), 'webhook': os.path.join(AR.STATE, 'webhooks', 'send.log'), 'push': os.path.join(AR.STATE, 'push', 'send.log')}
A = sys.argv[1:]; DRY = '--dry' in A


def sup(n):
    return n if isinstance(n, int) and n >= MIN else FEW


def canary_prefixes():
    try: c = json.load(open(os.path.join(AR.STATE, 'canary.json')))
    except Exception: return set(), set()
    toks = {t for ch in c.values() if isinstance(ch, dict) for t in ch.get('tokens', [])}
    return {t[:12] for t in toks} | {t[:8] for t in toks}, {hashlib.sha256(t.encode()).hexdigest()[:20] for t in toks}


def from_logs(since, skip):
    """-> (counts per metric over the window, distinct token prefixes per metric)"""
    cnt = C.Counter(); who = C.defaultdict(set)
    def add(m, tok):
        if tok in skip: return
        cnt[m] += 1; who[m].add(tok)
    for ch, p in LOGS.items():
        try: lines = open(p, encoding='utf-8', errors='replace').read().splitlines()
        except FileNotFoundError: continue
        for l in lines:
            m = re.match(r'(\d{4}-\d\d-\d\d) \d\d:\d\d:\d\d (.*)$', l)
            if not m or m.group(1) < since: continue
            t = m.group(2)
            if ch == 'email':
                mm = re.match(r'ok confirm:([0-9a-f]+)', t)
                if mm: add('confirm', mm.group(1)[:12]); continue
                mm = re.match(r'ok ([0-9a-f]{6,})', t)
                if mm: add('email', mm.group(1)[:12])
            elif ch == 'webhook':
                mm = re.match(r'ok ([0-9a-f]+)', t)
                if mm: add('webhook', mm.group(1)[:8])
                mm = re.match(r'TURNED OFF ([0-9a-f]+)', t)
                if mm: add('webhooks_off', mm.group(1)[:8])
            elif ch == 'push':
                mm = re.match(r'run end: (\d+) sent', t)
                if mm: cnt['push'] += int(mm.group(1))
    return cnt, who


def kv_pass(skip_hash, since):
    """private KV: which records exist now (hashed), against the last pass; deletion receipts by kind and day"""
    import notify_events as NE
    kv = NE.KV(); cur = {}
    for pre, metric in (('al:', 'unsub_alerts'), ('nl:', 'unsub_newsletter'), ('wh:', 'webhooks_deleted'), ('ps:', 'push_removed')):
        cur[metric] = sorted({hashlib.sha256(k.encode()).hexdigest()[:20] for k, _ in kv.list(pre)} - skip_hash)
    dels = C.Counter()
    for k, md in kv.list('delr:'):
        if md.get('at') and md['at'][:10] >= since: dels['deletions'] += 1
    try: old = json.load(open(SNAP))
    except Exception: old = None
    day = time.strftime('%Y-%m-%d', time.gmtime()); gone = C.Counter()
    if old:
        for m, hs in cur.items(): gone[(day, m)] = len(set(old.get(m, [])) - set(hs))
    if not DRY:
        json.dump(cur, open(SNAP + '.tmp', 'w')); os.replace(SNAP + '.tmp', SNAP)
        with open(EVENTS, 'a') as f:
            for (d, m), n in gone.items():
                if n: f.write(json.dumps({'day': d, 'metric': m, 'n': n}) + '\n')
    return dels, old is None, len(cur.get('push_removed', []))


def build(cnt, who, receipts, since, not_recorded, canary, devices=0):
    """by_desk per day counts alert events (about desks, not people). Channel numbers are window totals only, with no split by day, so
    one cell cannot be found by subtracting others. A channel total is shown only when it holds at least 5 events AND at least 5
    distinct recipients (token prefixes for email and webhooks, devices on the list for notifications). Otherwise: fewer than 5."""
    by_desk = C.Counter()
    for r in receipts:
        d = (r.get('first_sent_at') or '')[:10]
        if d >= since: by_desk[(d, r['desk'], r.get('desk_name') or r['desk'].upper())] += 1
    tot = {}
    for m in ('email', 'confirm', 'webhook', 'webhooks_off'):
        n = cnt.get(m, 0); tot[m] = n if n >= MIN and len(who.get(m, ())) >= MIN else FEW
    tot['push'] = cnt.get('push', 0) if cnt.get('push', 0) >= MIN and devices >= MIN else FEW
    for m in ('unsub_alerts', 'unsub_newsletter', 'webhooks_deleted', 'push_removed', 'deletions'): tot[m] = sup(cnt.get(m, 0))
    tot['alerts'] = sup(sum(by_desk.values()))
    return {'updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'window_days': WINDOW, 'suppression': 'every count under %d is written as "%s", and a channel total also needs %d distinct recipients' % (MIN, FEW, MIN),
            'excluded': 'our own canary subscriptions', 'by_desk': [{'day': d, 'desk': dk, 'desk_name': nm, 'n': sup(n)} for (d, dk, nm), n in sorted(by_desk.items(), reverse=True)],
            'totals': tot, 'not_recorded': not_recorded, 'canary': canary}


def check_suppressed(d):
    """no integer under MIN anywhere in the public table"""
    bad = []
    def walk(x, path):
        if isinstance(x, bool): return
        if isinstance(x, int) and x < MIN and not path.endswith('window_days'): bad.append(path)
        elif isinstance(x, dict): [walk(v, path + '.' + k) for k, v in x.items()]
        elif isinstance(x, list): [walk(v, path + '[%d]' % i) for i, v in enumerate(x)]
    walk(d, ''); return bad


def main():
    if A[:1] == ['selftest']:
        d = build(C.Counter({'email': 9, 'push': 12, 'webhook': 7, 'deletions': 2}), {'email': {'a', 'b'}, 'webhook': set('abcdefg')},
                  [{'first_sent_at': '2026-11-10T01:00:00Z', 'desk': 'cone', 'desk_name': 'CONE'}] * 4 + [{'first_sent_at': '2026-11-09T01:00:00Z', 'desk': 'flu', 'desk_name': 'FLU'}] * 6, '2026-10-01', ['bounces'], [], devices=3)
        t = d['totals']; bd = {(r['day'], r['desk']): r['n'] for r in d['by_desk']}
        ok = t['email'] == FEW and t['webhook'] == 7 and t['push'] == FEW and t['deletions'] == FEW and t['alerts'] == 10 and bd[('2026-11-10', 'cone')] == FEW and bd[('2026-11-09', 'flu')] == 6 and not check_suppressed(d)
        print('transparency selftest:', 'ok' if ok else 'FAIL', '' if ok else json.dumps(d)); return 0 if ok else 1
    if A[:1] != ['tick']: print(__doc__); return 0
    since = (D.datetime.utcnow() - D.timedelta(days=WINDOW)).strftime('%Y-%m-%d')
    skip, skip_hash = canary_prefixes()
    cnt, who = from_logs(since, skip)
    first = False; devices = 0
    if '--no-kv' not in A:
        try:
            dels, first, devices = kv_pass(skip_hash, since); cnt.update(dels)
        except Exception as e:
            json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': False, 'what': 'private KV could not be read: %s' % type(e).__name__}, open(STATUS, 'w')); print('transparency: KV read failed'); return 1
    try:
        for l in open(EVENTS):
            x = json.loads(l)
            if x['day'] >= since: cnt[x['metric']] += x['n']
    except FileNotFoundError: pass
    try: canary = json.load(open(os.path.join(AR.STATE, 'canary_public.json')))
    except Exception: canary = []
    d = build(cnt, who, list(AR._load_chain()[0].values()), since, ['bounces', 'refused_signups'], canary, devices)
    bad = check_suppressed(d)
    if bad: print('transparency: REFUSED, unsuppressed cells', bad[:5]); return 1
    body = json.dumps(d, ensure_ascii=False, indent=1)
    if DRY: print(body); return 0
    open(OUT, 'w').write(body)
    ok = AR.kv_put('transparency', body)
    json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': bool(ok), 'what': 'written' if ok else 'KV write failed'}, open(STATUS, 'w'))
    print('transparency: written%s, KV %s' % (' (first snapshot, removals count from the next pass)' if first else '', 'ok' if ok else 'FAILED')); return 0 if ok else 1


if __name__ == '__main__': sys.exit(main())
