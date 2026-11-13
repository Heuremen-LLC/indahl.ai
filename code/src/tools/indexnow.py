#!/usr/bin/env python3
"""indexnow.py: after a release, tell IndexNow (Bing, Yandex, Seznam, Naver) which of our pages changed. Own public URLs only.
A page counts as changed when the built file's hash differs from the one last sent (tools/indexnow_state.json).
  python3 tools/indexnow.py            send the changed pages
  python3 tools/indexnow.py --init     record the current hashes without sending
  python3 tools/indexnow.py --urls U.. send exactly these URLs"""
import os, sys, re, json, hashlib, urllib.request
B = os.path.expanduser('~/bones-forge'); S = os.path.join(B, 'tools', 'indexnow_state.json')
KEY = '7b56a9a7df0179bc520502cd2021efb4'; HOST = 'indahl.ai'
def sitemap():
    t = urllib.request.urlopen(urllib.request.Request('https://indahl.ai/sitemap.xml?x=1', headers={'User-Agent': 'heuremen-indexnow/1'}), timeout=30).read().decode()
    return re.findall(r'<loc>(.*?)</loc>', t)
def local(url):
    p = url[len('https://indahl.ai'):].strip('/')
    for c in (('index.html',) if not p else (p + '.html', p + '/index.html')):
        f = os.path.join(B, 'indahl-ai', c)
        if os.path.exists(f): return f
    if p == 'r' or p.startswith('r/'):   # 10 Nov 2026: receipts live in the worker's public/r (ledger/receipts.py), one page per ledger row
        for c in (p + '.html', p + '/index.html'):
            f = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public', c)
            if os.path.exists(f): return f
def send(urls):
    if not urls: print('indexnow: nothing changed'); return 0
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': 'https://%s/%s.txt' % (HOST, KEY), 'urlList': urls}).encode()
    r = urllib.request.urlopen(urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'}), timeout=60)
    print('indexnow: sent %d urls, status %s' % (len(urls), r.status)); return r.status
try:
    state = json.load(open(S)) if os.path.exists(S) else {}
    if '--urls' in sys.argv: send(sys.argv[sys.argv.index('--urls') + 1:]); sys.exit(0)
    now = {}
    for u in sitemap():
        f = local(u)
        if f: now[u] = hashlib.sha256(re.sub(rb'<section class="rp-sec rp-stamps">.*?</section>', b'', re.sub(rb'\?v=[0-9a-f]{8}', b'', open(f, 'rb').read()), flags=re.S)).hexdigest()[:16]   # asset version hashes do not count as a page change, nor a receipt's timestamps section (10 Nov: a new stamp or archive copy is not a new receipt)
    if '--init' in sys.argv: json.dump(now, open(S, 'w')); print('indexnow: recorded %d' % len(now)); sys.exit(0)
    ch = [u for u, h in now.items() if state.get(u) != h]
    if send(ch) in (200, 202): state.update({u: now[u] for u in ch}); json.dump(state, open(S, 'w'))
except Exception as e: print('indexnow: skipped,', type(e).__name__, str(e)[:100])
