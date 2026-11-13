import re, sys, os, json, urllib.request, urllib.error, urllib.parse, concurrent.futures as cf, html
D = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0 (site-pass-A; read-only check)'}
pages = sorted(f for f in os.listdir(os.path.join(D,'pages')) if f.endswith('.html'))
links = {}   # url -> set(pages)
for f in pages:
    t = open(os.path.join(D,'pages',f),encoding='utf-8',errors='replace').read()
    for m in re.finditer(r'(?:href|src|action)="([^"#][^"]*)"', t):
        u = html.unescape(m.group(1))
        if u.startswith(('mailto:','tel:','javascript:','data:')): continue
        u = urllib.parse.urljoin('https://indahl.ai/', u)
        links.setdefault(u,set()).add(f)
def chk(u):
    for meth in ('HEAD','GET'):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA, method=meth), timeout=30)
            return r.status
        except urllib.error.HTTPError as e:
            if meth=='HEAD' and e.code in (403,405,400,501,404): continue
            return e.code
        except Exception as e:
            if meth=='HEAD': continue
            return 'ERR '+type(e).__name__
    return None
res = {}
with cf.ThreadPoolExecutor(8) as ex:
    futs = {ex.submit(chk,u):u for u in links}
    for fu in cf.as_completed(futs): res[futs[fu]] = fu.result()
bad = {u:s for u,s in res.items() if s != 200}
print(len(links),'distinct links;', len(bad),'not 200')
for u,s in sorted(bad.items()): print(s,u,sorted(links[u]))
json.dump({u:[res[u],sorted(links[u])] for u in links}, open(os.path.join(D,'links.json'),'w'), indent=0)
