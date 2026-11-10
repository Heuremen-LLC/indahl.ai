#!/usr/bin/env python3
"""alert_receipts.py (10 Nov 2026): a public receipt for every alert event, and the guard that refuses an alert for an unpublished number.

A receipt is per event, not per person: the desk, the value before and now, the interval when the ledger row has one, the ledger row id and
the sha256 of the row as it stood when the alert went out, the time the change was found, and the kinds of channel that carried it (email,
device notification, webhook). It never holds subscriber data: no address, URL, endpoint, token or per-person count.

Where receipts live
  notify_state/alert_receipts.jsonl   append-only, hash-chained (each line carries prev and hash), one line per new receipt or new channel.
                                      archive/digest.py hashes this file into the archive chain, so its OpenTimestamps stamp covers alerts.
  KV IRIS_BENCH alert_r_<id>          the receipt as JSON, served at https://indahl.ai/r/alert/<id> (HTML, no script) and
                                      /r/alert/<id>.json (signed by the worker with the published Ed25519 key). alert_r_index lists them.

Hooks for the senders (one line each)
  guard(row_id) -> (ok, why)          refuses unless the change row is live (or superseded after being live) in the ledger, its desk headline
                                      row is live, and the desk page is in the latest public mirror commit after a ship whose mirror step
                                      passed (ledger/public_push_status.json). A refusal is logged and opens a Bones alert, never silent.
  record(event, channel)              upsert the receipt for one event (notify_events.event() dict, or an "update" event) and one channel kind.
  notify_events.change_rows calls guard() for every change row (webhooks_send.py and push_send.py read through it), and push_send.py
  calls record(). Senders not wired yet are covered by sweep(): every row a sender's seen file holds after its first run gets a receipt.

  python3 alert_receipts.py tick [--dry]   sweep the senders' seen files, write new receipts, push changed ones to the KV
  python3 alert_receipts.py guard ROW_ID   print what the guard says about one row
  python3 alert_receipts.py gate           every receipt line chains, every KV-bound receipt holds only the allowed fields, render has no script
Python 3.9, standard library only."""
import datetime as D, fcntl, hashlib, html, json, os, re, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(B, 'ledger'))
STATE = os.path.join(B, 'notify_state'); CHAIN = os.path.join(STATE, 'alert_receipts.jsonl'); LOCK = os.path.join(STATE, '.alert_receipts.lock')
REFUSALS = os.path.join(STATE, 'alert_guard_refusals.jsonl'); STATUS = os.path.join(STATE, 'alert_guard_status.json')
BASE = os.path.join(STATE, 'alert_receipts_baseline.json')   # rows the senders had already marked seen before receipts existed
LEDGER = os.path.join(B, 'ledger', 'ledger.jsonl'); MIRROR = os.path.join(B, 'public_mirror', 'indahl.ai'); PUSHST = os.path.join(B, 'ledger', 'public_push_status.json')
W = os.path.join(B, 'cloudflare-workers', 'heuremen-door'); NS_PUBLIC = 'ecb59d96b07c43bdac14271687eae5af'   # IRIS_BENCH, the public-data KV
SEEN_FILES = {'email': os.path.join(B, 'outcome_alerts', 'seen_rows.json'), 'webhook': os.path.join(STATE, 'webhooks', 'seen_rows.json'),
              'push': os.path.join(STATE, 'push', 'seen_rows.json')}
SWEEP = ()   # referee 10 Nov: a seen file marks a row even with no recipient, so it cannot say a channel carried it. Push and webhooks call record()
             # after an accepted delivery. Email waits for its one-line hook in alerts_send.py. The tick re-pushes receipts the KV missed.
PUSHED = os.path.join(STATE, 'alert_receipts_kv.json')
CHANNEL_WORD = {'email': 'email alert', 'push': 'device notification', 'webhook': 'webhook'}
FIELDS = {'id', 'kind', 'desk', 'desk_name', 'question', 'before', 'now', 'interval', 'unit', 'ledger_row', 'ledger_row_sha256', 'ledger_receipt',
          'found_at', 'first_sent_at', 'sent_at', 'channels', 'seq', 'chain_hash', 'why'}
A = sys.argv[1:]; DRY = '--dry' in A


def utc(iso):
    try: return D.datetime.fromisoformat(str(iso).replace('Z', '+00:00')).astimezone(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception: return None


def now(): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def rid_slug(s): return re.sub(r'[^A-Za-z0-9._-]', lambda m: '~%02X' % ord(m.group()), s.replace('flock', 'house'))[:150]


def raw_rows():
    out = {}
    lk = open(os.path.join(B, 'ledger', '.live_headlines.lock'), 'a'); fcntl.flock(lk, fcntl.LOCK_SH)
    try:
        for ln in open(LEDGER, 'rb').read().splitlines():
            if ln.strip():
                r = json.loads(ln); out[r['id']] = (r, ln)
    finally: fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    return out


# ------------------------------------------------------------------ the guard
def _alert_bones(key, what):
    """A Bones alert through watch/alerts_check.py: it reads notify_state/<name>_status.json and keeps it open while ok is False."""
    if DRY: return
    os.makedirs(STATE, exist_ok=True)
    json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': False, 'what': what[:300], 'key': key}, open(STATUS, 'w'))


def _mirror_has(rel):
    try: return subprocess.run(['git', '-C', MIRROR, 'cat-file', '-e', 'HEAD:' + rel], capture_output=True, timeout=30).returncode == 0
    except Exception: return False


_MC = {}
def guard(row_id, rows=None, log=True):
    rows = rows or raw_rows(); why = None
    r = (rows.get(row_id) or (None, None))[0]
    if r is None: why = 'no ledger row'
    elif r.get('status') not in ('live', 'superseded'): why = 'ledger row is %s, not live' % r.get('status')
    else:
        lo = r.get('live_of') or ''
        head = (rows.get(lo) or (None, None))[0] if lo else None
        desk = lo.split('.')[1] if lo.count('.') >= 2 else None
        if lo and (head is None or head.get('status') != 'live'): why = 'desk headline row %s is not live' % lo
        elif desk is None: why = 'the row names no desk'
        else:
            try: ps = json.load(open(PUSHST))
            except Exception: ps = {}
            if not ps.get('ok') or not ps.get('site_pages'): why = 'the last ship did not mirror the site pages (public_push_status.json)'
            elif not (_MC[desk] if desk in _MC else _MC.setdefault(desk, _mirror_has(desk + '.html'))): why = 'desk page %s.html is not in the latest public mirror commit' % desk
    if why and log: refuse(row_id, why)
    return (why is None), (why or 'ok')


def refuse(row_id, why):
    """Logged once per row and reason, and a Bones alert stays open (alerts_check.py 2e) until a later pass sends nothing refused."""
    seen = set()
    try:
        for l in open(REFUSALS): x = json.loads(l); seen.add((x['row'], x['why']))
    except Exception: pass
    if (row_id, why) not in seen and not DRY:
        os.makedirs(STATE, exist_ok=True)
        with open(REFUSALS, 'a') as f: f.write(json.dumps({'at': now(), 'row': row_id, 'why': why}) + '\n')
    _alert_bones('refused:' + row_id, 'alert refused for %s: %s' % (row_id, why))


def guard_clear():
    """called at the end of a pass that refused nothing: closes the Bones alert"""
    if DRY: return
    try:
        if json.load(open(STATUS)).get('ok') is False:
            json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': True, 'what': 'no refusal this pass'}, open(STATUS, 'w'))
    except Exception: pass


# ------------------------------------------------------------------ receipts
def _load_chain():
    out = {}; last = None; seq = 0
    try:
        for l in open(CHAIN):
            if not l.strip(): continue
            x = json.loads(l); rc = dict(x['receipt']); rc['chain_hash'] = x['hash']; out[rc['id']] = rc; last = x['hash']; seq = x['seq']
    except FileNotFoundError: pass
    return out, last, seq


def _append(rec):
    """one chained line: {seq, at, prev, receipt, hash = sha256(prev + canonical receipt)}"""
    _, last, seq = _load_chain()
    rec = dict(rec); rec.pop('chain_hash', None); rec['seq'] = seq + 1
    body = json.dumps(rec, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    h = hashlib.sha256(((last or '') + body).encode()).hexdigest()
    rec['chain_hash'] = h
    line = {'seq': seq + 1, 'at': now(), 'prev': last, 'receipt': {k: v for k, v in rec.items() if k != 'chain_hash'}, 'hash': h}
    if not DRY:
        with open(CHAIN, 'a') as f: f.write(json.dumps(line, sort_keys=True, ensure_ascii=False) + '\n')
    return rec


def build(event, rows=None):
    """the public receipt fields for one event, from the ledger row (never from subscriber data)"""
    rows = rows or raw_rows()
    if event.get('type', 'outcome_change') == 'outcome_change':
        r, ln = rows.get(event['id'], (None, None))
        iv = None
        if r and r.get('lo') not in (None, '') and r.get('hi') not in (None, ''): iv = [str(r['lo']), str(r['hi'])]
        rr = event['id']
        return {'id': rid_slug(rr), 'kind': 'outcome_change', 'desk': event['desk'], 'desk_name': event.get('desk_name') or event['desk'].upper(),
                'question': event.get('question') or '', 'before': event.get('before'), 'now': event.get('now'), 'why': event.get('why') or '',
                'interval': iv, 'unit': (r or {}).get('unit') or '', 'ledger_row': rr.replace('flock', 'house'),
                'ledger_row_sha256': hashlib.sha256(ln).hexdigest() if ln else None, 'ledger_receipt': '/r/' + rid_slug(rr) if r and r.get('status') != 'staged' else None,
                'found_at': utc(((r or {}).get('history') or [{}])[0].get('at')) or event.get('recorded_at'), 'first_sent_at': None, 'channels': []}
    uid = str(event.get('uid') or event.get('id'))   # an update: a new desk or a first value (alerts_send.py up events)
    return {'id': rid_slug('up.' + uid), 'kind': 'update', 'desk': event.get('desk') or '', 'desk_name': event.get('desk_name') or (event.get('desk') or '').upper(),
            'question': event.get('title') or event.get('what') or '', 'before': None, 'now': None, 'why': event.get('why') or '', 'interval': None, 'unit': '',
            'ledger_row': event.get('row'), 'ledger_row_sha256': None, 'ledger_receipt': None, 'found_at': utc(event.get('at')) or now(),
            'first_sent_at': None, 'channels': []}


def record(event, channel, rows=None, push=True):
    """upsert: a new receipt, or one more channel kind on an existing one. Returns the receipt id."""
    if channel not in CHANNEL_WORD: raise ValueError('unknown channel ' + channel)
    os.makedirs(STATE, exist_ok=True)
    lk = open(LOCK, 'a'); fcntl.flock(lk, fcntl.LOCK_EX)
    try:
        have, _, _ = _load_chain(); new = build(event, rows); cur = have.get(new['id'])
        if cur and channel in cur.get('channels', []): return cur['id']
        rec = dict(cur or new); rec['channels'] = sorted(set((cur or {}).get('channels', [])) | {channel})
        rec['first_sent_at'] = (cur or {}).get('first_sent_at') or now()
        rec['sent_at'] = dict((cur or {}).get('sent_at') or {}, **{channel: now()})
        rec = _append({k: v for k, v in rec.items() if k in FIELDS})
    finally: fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    if push: kv_push([rec])
    return rec['id']


def _wr(*a):
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', *a], cwd=W, env=env, capture_output=True, text=True, timeout=180)
    return r.returncode


def kv_put(key, value):
    if DRY: return True
    import tempfile
    os.makedirs(STATE, exist_ok=True); fd, tmp = tempfile.mkstemp(prefix='.kv_pub.', dir=STATE)
    with os.fdopen(fd, 'w') as f: f.write(value)
    try: return _wr('kv', 'key', 'put', key, '--path', tmp, '--namespace-id', NS_PUBLIC, '--remote') == 0
    finally:
        try: os.remove(tmp)
        except OSError: pass


def kv_push(recs):
    ok = True
    try: done = json.load(open(PUSHED))
    except Exception: done = {}
    for r in recs:
        w = kv_put('alert_r_' + r['id'], json.dumps(public(r), ensure_ascii=False, separators=(',', ':')))
        if w: done[r['id']] = r.get('chain_hash')
        ok &= w
    if not DRY:
        json.dump(done, open(PUSHED + '.tmp', 'w')); os.replace(PUSHED + '.tmp', PUSHED)
    have, _, _ = _load_chain()
    idx = sorted(({'id': x['id'], 'desk': x['desk'], 'desk_name': x['desk_name'], 'kind': x['kind'], 'found_at': x['found_at'], 'first_sent_at': x['first_sent_at'], 'channels': x['channels']}
                  for x in have.values()), key=lambda x: x['first_sent_at'] or '', reverse=True)[:500]
    ok &= kv_put('alert_r_index', json.dumps({'updated': now(), 'receipts': idx}, ensure_ascii=False, separators=(',', ':')))
    return ok


def public(r):
    out = {k: r.get(k) for k in sorted(FIELDS)}
    bad = check_public(out)
    if bad: raise ValueError('alert receipt %s refused: %s' % (r.get('id'), bad))
    return out


PRIVATE = re.compile(r'(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|https?://(?!indahl\.ai/)|\bendpoint\b|\btoken\b|fcm\.googleapis|push\.apple|mozilla\.com')
def check_public(d):
    if set(d) - FIELDS: return 'fields %s' % sorted(set(d) - FIELDS)
    if PRIVATE.search(json.dumps(d, ensure_ascii=False)): return 'looks like subscriber data'
    return None


def retry():
    """receipts whose newest chain line never reached the KV are pushed again"""
    have, _, _ = _load_chain()
    try: done = json.load(open(PUSHED))
    except Exception: done = {}
    miss = [r for r in have.values() if done.get(r['id']) != r.get('chain_hash')]
    if miss: kv_push(miss); print('alert receipts: %d receipt(s) pushed again' % len(miss))


# ------------------------------------------------------------------ sweep (senders not yet wired)
def sweep():
    import notify_events as NE
    rows = raw_rows(); changes = {c['id']: c for c in NE.change_rows([r for r, _ in rows.values()], guard=False)}
    if not os.path.exists(BASE):
        base = {}
        for ch, p in SEEN_FILES.items():
            try: base[ch] = sorted(json.load(open(p)))
            except Exception: base[ch] = []
        if not DRY: json.dump(base, open(BASE, 'w'), indent=0)
        print('alert receipts: baseline taken (%s), nothing recorded' % ', '.join('%s %d' % (k, len(v)) for k, v in base.items())); return 0
    base = json.load(open(BASE)); have, _, _ = _load_chain(); n = 0; changed = []
    for ch, p in SEEN_FILES.items():
        if ch not in SWEEP: continue
        try: seen = set(json.load(open(p)))
        except Exception: continue
        for i in sorted(seen - set(base.get(ch, []))):
            if i not in changes: continue
            sl = rid_slug(i)
            if sl in have and ch in have[sl].get('channels', []): continue
            rid = record(NE.event(changes[i]), ch, rows=rows, push=False); have, _, _ = _load_chain(); changed.append(have[rid]); n += 1
    if changed: kv_push(list({r['id']: r for r in changed}.values()))
    have, _, _ = _load_chain(); retry()
    print('alert receipts: %d new receipt line(s), %d receipts in all' % (n, len(have))); return n


# ------------------------------------------------------------------ render (the worker renders from the same fields; this copy is for the gate)
def render(r):
    E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
    side = lambda s: (E(s.get('display')) + (' (' + E(s['outcome']) + ')' if s.get('outcome') else '')) if s else ''
    rows = [('Desk', '<a href="/%s">%s</a>' % (E(r['desk']), E(r['desk_name']))), ('Question', E(r['question'])), ('Before', side(r['before'])), ('Now', side(r['now']))]
    if r.get('interval'): rows.append(('Interval', E(r['interval'][0]) + ' to ' + E(r['interval'][1])))
    rows += [('Ledger row', ('<a href="%s">%s</a>' % (E(r['ledger_receipt']), E(r['ledger_row']))) if r.get('ledger_receipt') else E(r['ledger_row'])),
             ('Row sha256', '<code>%s</code>' % E(r['ledger_row_sha256'])), ('Found', E(r['found_at'])), ('First sent', E(r['first_sent_at'])),
             ('Channels', E(', '.join(CHANNEL_WORD[c] for c in r['channels']))), ('Chain hash', '<code>%s</code>' % E(r['chain_hash']))]
    return '<table class="rp-t">' + ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % x for x in rows) + '</table>'


def gate():
    bad = []; last = None
    try: lines = [json.loads(l) for l in open(CHAIN) if l.strip()]
    except FileNotFoundError: lines = []
    for x in lines:
        rec = dict(x['receipt']); body = json.dumps(rec, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        if x['prev'] != last or hashlib.sha256(((last or '') + body).encode()).hexdigest() != x['hash']: bad.append('chain breaks at seq %s' % x['seq'])
        last = x['hash']; rec['chain_hash'] = x['hash']
        b = check_public({k: rec.get(k) for k in FIELDS})
        if b: bad.append('%s: %s' % (rec.get('id'), b))
        if re.search(r'(?i)<script', render(rec)): bad.append('%s: script in render' % rec.get('id'))
    print('alert receipts gate: %d chained lines; breaches: %d' % (len(lines), len(bad)))
    for b in bad[:20]: print('  ' + b)
    return 1 if bad else 0


if __name__ == '__main__':
    c = A[:1]
    if c == ['tick']:
        lk = open(os.path.join(STATE, '.alert_receipts_tick.lock'), 'w')
        try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError: print('alert receipts: another run holds the lock'); sys.exit(0)
        sweep()
    elif c == ['guard'] and len(A) > 1: print(guard(A[1], log=False))
    elif c == ['gate']: sys.exit(gate())
    else: print(__doc__)
