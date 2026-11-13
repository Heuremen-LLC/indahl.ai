import json,sys,time,threading,urllib.request,urllib.error,ssl
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
d=json.load(open('links.json'))
hosts=sys.argv[1].split(','); conc=int(sys.argv[2]); delay=float(sys.argv[3]); outp=sys.argv[4]
urls=[u for u in d if urlparse(u).netloc in hosts]
ctx=ssl.create_default_context()
def get(u):
    time.sleep(delay)
    for method in ('HEAD','GET'):
        req=urllib.request.Request(u,method=method,headers={'User-Agent':'Mozilla/5.0 (site-pass link check; Heuremen LLC)'})
        try:
            r=urllib.request.urlopen(req,timeout=25,context=ctx); return u,r.status,r.geturl()
        except urllib.error.HTTPError as e:
            if method=='HEAD' and e.code in (403,405,429,400,404,500,501,503): 
                if e.code==429: time.sleep(3)
                continue
            return u,e.code,''
        except Exception as e:
            if method=='GET': return u,'ERR '+type(e).__name__+' '+str(e)[:80],''
    return u,'??',''
res=[]
with ThreadPoolExecutor(conc) as ex:
    for r in ex.map(get,urls): res.append(r)
json.dump(res,open(outp,'w'))
bad=[r for r in res if not (isinstance(r[1],int) and r[1]<400)]
print(len(res),'checked',len(bad),'bad')
for b in bad[:80]: print(b)
