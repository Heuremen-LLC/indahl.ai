import re, urllib.request, json, os, sys
names = ['tape','weights','airline','fedsep','revise','stack','pkginstall','seat','secrecords','change','hfsize','hflicense','pkglicense','arxivdrift','cadence','cada']
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'siteaudit'}), timeout=30)
        return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, b'', {}
    except Exception as e:
        return str(e), b'', {}
seen = {}
for n in names:
    h = open(f'{n}.html', encoding='utf-8').read()
    srcs = re.findall(r'<script[^>]+src="([^"]+)"', h)
    row = []
    for s in srcs:
        u = 'https://indahl.ai' + s if s.startswith('/') else s
        if u not in seen:
            c, b, hd = get(u + ('&' if '?' in u else '?') + 'w=3')
            seen[u] = (c, len(b), hd.get('content-type'))
        row.append((s, seen[u]))
    # feeds referenced in live.js
    js = open(f'/Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/public/{n}/live.js', encoding='utf-8').read()
    feeds = sorted(set(re.findall(r"fetch\('([^']+)'", js)))
    frows = []
    for f in feeds:
        c, b, hd = get('https://indahl.ai' + f + '?w=3')
        frows.append((f, c, len(b), hd.get('content-type'), hd.get('cache-control')))
    print(n); [print('   ', r) for r in row]; [print('   FEED', r) for r in frows]
