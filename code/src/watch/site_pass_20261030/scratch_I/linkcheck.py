import json, urllib.request, urllib.error, concurrent.futures, re
L=json.load(open('links.json'))
urls=[]
for u,pgs in L.items():
    if u.startswith('#') or u.startswith('mailto:') or u.startswith('javascript:'): continue
    full = u if u.startswith('http') else 'https://indahl.ai' + (u if u.startswith('/') else '/' + u)
    urls.append((u, full, pgs))
def chk(t):
    u, full, pgs = t
    for method in ('HEAD','GET'):
        try:
            req=urllib.request.Request(full, method=method, headers={'User-Agent':'Mozilla/5.0 (siteaudit)'})
            r=urllib.request.urlopen(req, timeout=30)
            return (u, full, r.status, pgs)
        except urllib.error.HTTPError as e:
            if method=='HEAD' and e.code in (403,405,404,400,429,501): continue
            return (u, full, e.code, pgs)
        except Exception as e:
            if method=='HEAD': continue
            return (u, full, 'ERR '+type(e).__name__+str(e)[:50], pgs)
    return (u, full, '?', pgs)
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(chk, urls))
bad=[r for r in res if r[2]!=200]
print(len(res), 'checked;', len(bad), 'not 200')
for r in bad: print(r[2], r[1], r[3][:4])
json.dump(res, open('linkcheck.json','w'))
