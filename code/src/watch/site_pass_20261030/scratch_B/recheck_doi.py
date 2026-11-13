import json,urllib.request,urllib.error,time,ssl
from concurrent.futures import ThreadPoolExecutor
res=json.load(open('sweep_other.json'))
bad=[r for r in res if not (isinstance(r[1],int) and r[1]<400)]
ctx=ssl.create_default_context()
def chk(r):
    u=r[0]; 
    if not u.startswith('https://doi.org/'): return r,'nonDOI'
    doi=u[len('https://doi.org/'):]
    time.sleep(0.15)
    try:
        req=urllib.request.Request('https://doi.org/api/handles/'+doi,headers={'User-Agent':'Mozilla/5.0 (site-pass link check)'})
        d=json.load(urllib.request.urlopen(req,timeout=25,context=ctx)); return r,'handle rc=%s'%d.get('responseCode')
    except urllib.error.HTTPError as e: return r,'handle HTTP %s'%e.code
    except Exception as e: return r,'handle ERR '+type(e).__name__
out=[]
with ThreadPoolExecutor(4) as ex:
    for x in ex.map(chk,bad): out.append(x)
from collections import Counter
print(Counter(o[1] for o in out))
for r,s in out:
    if s!='handle rc=1': print(r[0],r[1],s)
