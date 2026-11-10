#!/usr/bin/env python3
"""notify_events.py (10 Nov 2026): what webhooks_send.py and push_send.py share.

The events are the same as the outcome alerts (alerts_send.py) and the desk change feeds (ledger/changes_feed.py): every live_value row
ledger/live_headlines.py writes after a desk's baseline row. Each sender keeps its own seen file, and its first run marks every row already in
the ledger as seen, so it never sends history. The ledger is read under live_headlines' lock, so a half-written row is never read.
The private KV INDAHL_INQUIRIES is read and written through wrangler, as newsletter_send.py does. Records are never printed: logs name the
token prefix only. Python 3.9, standard library only."""
import fcntl, json, os, re, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(B, 'ledger'))
W = os.path.join(B, 'cloudflare-workers', 'heuremen-door'); NS = '034b2ec99c3843099b3d5888d9e246d0'   # INDAHL_INQUIRIES
ENV = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
LH_LOCK = os.path.join(B, 'ledger', '.live_headlines.lock')
STATE = os.path.join(B, 'notify_state')
SITE = 'https://indahl.ai'


def wr(*a):
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', *a], cwd=W, env=ENV, capture_output=True, text=True, timeout=180)
    return r.returncode, re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)


class KV:
    """The private KV through wrangler, or a JSON file standing in for it (a test: {key: {"value": ..., "metadata": {...}}})."""
    def __init__(self, path=None):
        self.path = path
        self.d = json.load(open(path)) if path else None

    def _save(self):
        if self.path: json.dump(self.d, open(self.path, 'w'), indent=1, sort_keys=True)

    def list(self, prefix):
        if self.d is not None: return [(k[len(prefix):], v.get('metadata') or {}) for k, v in sorted(self.d.items()) if k.startswith(prefix)]
        rc, out = wr('kv', 'key', 'list', '--prefix', prefix, '--namespace-id', NS, '--remote')
        if rc: raise RuntimeError('wrangler kv key list %s failed' % prefix)
        return [(k['name'][len(prefix):], k.get('metadata') or {}) for k in json.loads(out[out.index('['):])]

    def get(self, key):
        if self.d is not None: return (self.d.get(key) or {}).get('value')
        rc, out = wr('kv', 'key', 'get', key, '--namespace-id', NS, '--remote', '--text')
        return None if rc else out.strip()

    def put(self, key, value, metadata=None):
        if self.d is not None:
            self.d[key] = {'value': value, 'metadata': metadata}; self._save(); return True
        os.makedirs(STATE, exist_ok=True); tmp = os.path.join(STATE, '.kv_put.tmp')   # the value goes by file, never on a command line
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f: f.write(value)
        a = ['kv', 'key', 'put', key, '--path', tmp, '--namespace-id', NS, '--remote']
        if metadata is not None: a += ['--metadata', json.dumps(metadata, separators=(',', ':'))]
        try: return wr(*a)[0] == 0
        finally:
            try: os.remove(tmp)
            except OSError: pass

    def delete(self, key):
        if self.d is not None:
            self.d.pop(key, None); self._save(); return True
        return wr('kv', 'key', 'delete', key, '--namespace-id', NS, '--remote')[0] == 0

    def bump(self, key, by):
        try: n = int(self.get(key) or 0)
        except ValueError: n = 0
        self.put(key, str(max(0, n + by)))


def ledger_rows(path):
    lk = open(LH_LOCK, 'a'); fcntl.flock(lk, fcntl.LOCK_SH)   # live_headlines.py writes under LOCK_EX on this file
    try: return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    finally: fcntl.flock(lk, fcntl.LOCK_UN); lk.close()


def change_rows(rows, guard=True):
    """Every non-baseline live_value row, oldest first, with the row before it on the same desk (the same rule as alerts_send.value_rows).
    10 Nov 2026 (alert_receipts.guard): with guard on, a row whose number is not published yet (row not live, desk headline not live, or the
    desk page not in the latest public mirror commit) is left out and logged as refused, with a Bones alert. It is not marked seen, so it
    goes out on the first tick after it is published."""
    vals = [r for r in rows if r.get('kind') == 'live_value' and r.get('reading') and r.get('live_of', '').startswith('live.')]
    vals.sort(key=lambda r: r['history'][0]['at'])
    out, last = [], {}
    for r in vals:
        desk = r['live_of'].split('.')[1]; prev = last.get(desk); last[desk] = r
        if prev is None or str(r['history'][0].get('why', '')).startswith('baseline'): continue
        out.append(dict(id=r['id'], desk=desk, prev=prev['reading'], cur=r['reading'], at=r['history'][0]['at']))
    if guard and out: out = _guarded(out, rows)
    return out


def _guarded(out, rows):
    import alert_receipts as AR
    idx = {r['id']: (r, b'') for r in rows}
    try: AR.raw_rows
    except AttributeError: return out
    import datetime as _D
    old = (_D.datetime.now(_D.timezone.utc) - _D.timedelta(days=7)).isoformat()
    keep = [c for c in out if (AR.utc(c['at']) and AR.utc(c['at']) < old[:19] + 'Z') or AR.guard(c['id'], rows=idx)[0]]   # rows older than 7 days went out long ago and are not guarded again
    if len(keep) == len(out): AR.guard_clear()
    return keep


def event(ch):
    """One change as the public event both senders describe (the words of the desk's change feed)."""
    import live_headlines as LH, changes_feed as CF
    spec = LH.DESKS.get(ch['desk'], {}); p, c = ch['prev'], ch['cur']
    side = lambda r: {'display': r.get('display', ''), 'outcome': (CF.WORD.get(r.get('outcome')) if r.get('outcome') else None)}
    return {'type': 'outcome_change', 'id': ch['id'], 'desk': ch['desk'], 'desk_name': spec.get('name', ch['desk'].upper()),
            'question': LH.H2.get(ch['desk'], ''), 'before': side(p), 'now': side(c), 'feed_time': c.get('stamp') or None,
            'why': CF._why(spec, p, c), 'recorded_at': CF._utc(ch['at']), 'url': '%s/%s' % (SITE, ch['desk']),
            'feed': '%s/%s/changes.xml' % (SITE, ch['desk'])}


def show(side):
    return side['display'] + ((' (' + side['outcome'] + ')') if side.get('outcome') else '')


def text(ev):
    return '%s: %s\nBefore: %s. Now: %s. %s\n%s' % (ev['desk_name'], ev['question'], show(ev['before']), show(ev['now']), ev['why'], ev['url'])


def seen(path, ids, dry, label, log):
    """The seen set, or None on the first run (which marks every id seen and sends nothing)."""
    if os.path.exists(path): return set(json.load(open(path)))
    if not dry:
        os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(sorted(ids), open(path, 'w'), indent=0)
        log('first run: %d existing %s marked seen, nothing sent' % (len(ids), label))
    print('first run: %d existing %s marked seen, nothing sent' % (len(ids), label)); return None


def save_seen(path, s):
    json.dump(sorted(s), open(path + '.tmp', 'w'), indent=0); os.replace(path + '.tmp', path)


def status(name, ok, what=''):
    """notify_state/<name>_status.json, read by watch/alerts_check.py: a run that could not do its job opens an alert for Bones."""
    os.makedirs(STATE, exist_ok=True)
    json.dump({'at': time.strftime('%Y-%m-%d %H:%M'), 'ok': bool(ok), 'what': what[:300]}, open(os.path.join(STATE, name + '_status.json'), 'w'))
