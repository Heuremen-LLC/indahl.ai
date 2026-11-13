import json,urllib.request,urllib.error,concurrent.futures as cf,collections,time,socket,ssl,re,threading
from urllib.parse import urlparse
L=json.load(open('ext_links.json'))
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
hostlock=collections.defaultdict(threading.Lock)
def chk(u):
    h=urlparse(u).netloc
    out=dict(url=u,status=None,final=None,ctype=None,err=None,redirected=False)
    for attempt in range(2):
        try:
            with hostlock[h]:
                req=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'text/html,application/pdf,*/*'})
                r=urllib.request.urlopen(req,timeout=20)
                b=r.read(4096)
                time.sleep(0.2)
            out.update(status=r.status,final=r.geturl(),ctype=r.headers.get('Content-Type'),redirected=(r.geturl()!=u))
            return out
        except urllib.error.HTTPError as e:
            out.update(status=e.code,final=e.geturl(),err=str(e)[:80])
            if e.code in (429,503) and attempt==0: time.sleep(3); continue
            return out
        except Exception as e:
            out.update(err=type(e).__name__+': '+str(e)[:100])
            time.sleep(1)
    return out
with cf.ThreadPoolExecutor(16) as ex: res=list(ex.map(chk,sorted(L)))
json.dump(res,open('ext_results.json','w'))
c=collections.Counter((r['status'] if r['status'] else 'ERR') for r in res)
print(c)
