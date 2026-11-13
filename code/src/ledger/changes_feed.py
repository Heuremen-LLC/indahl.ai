#!/usr/bin/env python3
"""changes_feed.py: one Atom feed per live desk, /<desk>/changes.xml, posting only when the desk's headline makes a material change under the
ledger rule (10 Nov 2026). The entries are the desk's live_value rows written by live_headlines.py run. The first row of a desk is the
baseline and is not a change, so it posts nothing. Each later row is one entry: the previous value and outcome, the new ones, the time, a link.

  changes_feed.py build            write every feed into the worker's public/<desk>/changes.xml (build_site.py does this on every build)
  changes_feed.py push SLUG ...    write and put those feeds to the KV key changes_<slug> (live_headlines.py run calls this after it writes)
  changes_feed.py print SLUG       print one feed
Python 3.9, standard library only."""
import os, sys, json, html, subprocess, datetime as D
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PUB = os.path.join(ROOT, 'cloudflare-workers', 'heuremen-door', 'public'); W = os.path.join(ROOT, 'cloudflare-workers', 'heuremen-door')
NS = 'ecb59d96b07c43bdac14271687eae5af'; SITE = 'https://indahl.ai'
sys.path.insert(0, HERE)
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}


def _utc(iso):
    t = D.datetime.fromisoformat(iso)
    if t.tzinfo is None: t = t.replace(tzinfo=D.timezone.utc)
    return t.astimezone(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _show(rd):
    o = rd.get('outcome'); return rd.get('display', '') + ((' (' + WORD[o] + ')') if o in WORD else '')


def _bound(spec, x):
    if x is None: return ''
    try: x = float(x)
    except Exception: return str(x)
    return ('%.0f%%' % (100 * x)) if spec.get('show') in ('pct', 'n_of', 'of_minus_n') else ('%.1f%%' % (100 * x) if spec.get('show') == 'pct1' else '%g' % x)


def _why(spec, prev, cur):
    po, co = prev.get('outcome'), cur.get('outcome')
    if po in WORD and co in WORD and po != co: return 'The outcome changed from %s to %s.' % (WORD[po], WORD[co])
    if spec.get('kind') == 'interval' and prev.get('lo') is not None:
        return 'The number moved outside the interval printed with the previous value, %s to %s.' % (_bound(spec, prev['lo']), _bound(spec, prev['hi']))
    if spec.get('kind') == 'set': return 'A figure that the desk\'s stated rule reads changed.'
    return 'The headline changed under the desk\'s rule.'


def feed(slug, rows=None):
    import live_headlines as LH
    spec = LH.DESKS.get(slug)
    if not spec or (spec['kind'] == 'flip' and not spec.get('outcome')): return None
    if rows is None: rows = [json.loads(l) for l in open(os.path.join(HERE, 'ledger.jsonl'))]
    vals = sorted((r for r in rows if r.get('kind') == 'live_value' and r.get('live_of') == 'live.%s.headline' % slug and r.get('reading')), key=lambda r: r['history'][0]['at'])
    name = spec['name']; url = '%s/%s' % (SITE, slug); e = html.escape
    entries = []
    for prev, cur in zip(vals, vals[1:]):
        p, c = prev['reading'], cur['reading']; at = _utc(cur['history'][0]['at'])
        title = '%s: %s to %s' % (name, _show(p), _show(c))
        summ = 'Before: %s. Now: %s, at the feed time %s. %s' % (_show(p), _show(c), c.get('stamp') or at, _why(spec, p, c))
        entries.append('<entry><id>tag:indahl.ai,2026:%s</id><title>%s</title><link href="%s"/><updated>%s</updated><summary>%s</summary></entry>' % (e(cur['id']), e(title), url, at, e(summ)))
    upd = _utc(vals[-1]['history'][0]['at']) if vals else '2026-11-10T12:04:08Z'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>tag:indahl.ai,2026:changes:%s</id><title>%s: changes to the headline</title>'
            '<subtitle>An entry is posted only when the headline makes a material change under the desk\'s rule.</subtitle>'
            '<link href="%s/%s/changes.xml" rel="self"/><link href="https://pubsubhubbub.appspot.com/" rel="hub"/><link href="%s" rel="alternate"/><updated>%s</updated><author><name>Heuremen LLC</name></author>%s</feed>\n'
            % (slug, e(name), SITE, slug, url, upd, ''.join(reversed(entries))))


def all_feeds():
    import live_headlines as LH
    rows = [json.loads(l) for l in open(os.path.join(HERE, 'ledger.jsonl'))]
    return {s: x for s in LH.DESKS for x in [feed(s, rows)] if x}


def write(slugs=None):
    fs = all_feeds(); out = []
    for s, x in fs.items():
        if slugs and s not in slugs: continue
        p = os.path.join(PUB, s, 'changes.xml'); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != x: open(p, 'w', encoding='utf-8').write(x)
        out.append((s, p))
    return out


def push(slugs):
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    for s, p in write(slugs):
        r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'changes_' + s, '--path', p, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
        print('changes_feed: %s %s' % (s, 'published' if r.returncode == 0 else 'publish FAILED'))
    try: subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'indahl-ai', 'websub_ping.py'), 'desks'] + list(slugs), timeout=600)   # 10 Nov 2026: tell the WebSub hub once (failures alert Bones, never stop the tick)
    except Exception: pass


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['build']: print('changes_feed: %d feeds written' % len(write()))
    elif a[:1] == ['push']: push(a[1:])
    elif a[:1] == ['print']: print(feed(a[1]))
    else: print(__doc__)
