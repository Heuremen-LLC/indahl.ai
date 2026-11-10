#!/usr/bin/env python3
"""websub_ping.py (10 Nov 2026): tell the public WebSub hub that an indahl.ai feed changed, so a feed reader subscribed through the hub gets
the entry without polling. Every Atom feed names the hub with <link rel="hub" href="https://pubsubhubbub.appspot.com/"/>.

  websub_ping.py ship            after a ship (ledger/ship.sh): ping each built feed whose content changed since the last ping
  websub_ping.py desks SLUG ...  after ledger/changes_feed.py push (a desk's headline moved): that desk's feed, the organisation feeds that
                                 read it, and the site feeds
  websub_ping.py ship --dry      list what would be pinged

A ping is POST hub.mode=publish&hub.url=<feed> to the hub, which answers 204 and then fetches the feed itself. Failures never stop a ship
or a tick: they are written to notify_state/websub_status.json, and watch/alerts_check.py opens an alert for Bones until a later ping
succeeds. Python 3.9, standard library only."""
import hashlib, json, os, sys, time, urllib.parse, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H)
PUB = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public')
STATE = os.path.join(B, 'notify_state'); HASHES = os.path.join(STATE, 'websub_hashes.json'); STATUS = os.path.join(STATE, 'websub_status.json')
HUB = 'https://pubsubhubbub.appspot.com/'; SITE = 'https://indahl.ai'
DRY = '--dry' in sys.argv


def brands_of(desks):
    try: m = json.load(open(os.path.join(H, 'alerts_map.json')))['brands']
    except Exception: return []
    return sorted(s for s, (_, ds) in m.items() if set(ds) & set(desks))


def built_feeds():
    """{feed URL: sha of what decides its content}. The site feed and its JSON copy follow the built feed entries."""
    out = {}
    def h(p):
        try: return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        except OSError: return None
    for rel in ('corrections.xml', 'newsletter/feed.xml', 'changelog.xml'):
        x = h(os.path.join(PUB, rel))
        if x: out[SITE + '/' + rel] = x
    fe = h(os.path.join(H, 'feed-entries.html'))
    if fe: out[SITE + '/feed.xml'] = fe; out[SITE + '/feed.json'] = fe
    for d in sorted(os.listdir(PUB)):
        x = h(os.path.join(PUB, d, 'changes.xml'))
        if x: out['%s/%s/changes.xml' % (SITE, d)] = x
    return out


def ping(urls):
    ok, bad = [], []
    for u in urls:
        if DRY: print('  would ping', u); ok.append(u); continue
        data = urllib.parse.urlencode({'hub.mode': 'publish', 'hub.url': u}).encode()
        req = urllib.request.Request(HUB, data=data, method='POST', headers={'content-type': 'application/x-www-form-urlencoded', 'user-agent': 'indahl.ai-websub/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=15) as r: code = r.status
        except urllib.error.HTTPError as e: code = e.code
        except Exception as e: code = type(e).__name__
        (ok if code in (200, 202, 204) else bad).append(u if code in (200, 202, 204) else '%s (%s)' % (u, code))
        time.sleep(0.2)
    return ok, bad


def record(kind, ok, bad):
    if DRY: return
    os.makedirs(STATE, exist_ok=True)
    try: prev = json.load(open(STATUS))
    except Exception: prev = {}
    st = {'at': time.strftime('%Y-%m-%d %H:%M'), 'kind': kind, 'pinged': len(ok), 'failed': bad[:20], 'ok': not bad}
    if bad: st['failing_since'] = prev.get('failing_since') or st['at']
    json.dump(st, open(STATUS, 'w'), indent=1)


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ['ship']:
            cur = built_feeds()
            try: old = json.load(open(HASHES))
            except Exception: old = {}
            todo = [u for u, x in sorted(cur.items()) if old.get(u) != x]
            desks = [u.split('/')[3] for u in todo if u.endswith('/changes.xml') and u.count('/') == 4]
            todo += ['%s/brand/%s/changes.xml' % (SITE, s) for s in brands_of(desks)]
            ok, bad = ping(todo)
            if not DRY:
                json.dump({u: x for u, x in cur.items() if not any(b.startswith(u + ' ') for b in bad)}, open(HASHES, 'w'), indent=0, sort_keys=True)
            record('ship', ok, bad)
            print('websub: %d feed(s) pinged after the ship, %d failed' % (len(ok), len(bad)))
        elif a[:1] == ['desks']:
            ds = [s for s in a[1:] if not s.startswith('--')]
            todo = ['%s/%s/changes.xml' % (SITE, s) for s in ds] + ['%s/brand/%s/changes.xml' % (SITE, s) for s in brands_of(ds)]
            ok, bad = ping(todo); record('desks', ok, bad)
            print('websub: %d feed(s) pinged, %d failed' % (len(ok), len(bad)))
        else: print(__doc__)
    except Exception as e:   # never break a ship or a tick
        record(a[:1][0] if a else '?', [], ['websub_ping.py itself (%s)' % type(e).__name__]); print('websub: ping step failed (%s), alert written' % type(e).__name__)


if __name__ == '__main__': main()
