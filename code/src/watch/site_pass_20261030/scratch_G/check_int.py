import json,urllib.request,concurrent.futures as cf,collections,time
L=json.load(open('int_links.json'))
def chk(u):
    for a in range(2):
        try:
            req=urllib.request.Request(u,headers={'User-Agent':'indahl-sitepass/1.0'})
            r=urllib.request.urlopen(req,timeout=25)
            b=r.read(200000)
            return u,r.status,r.geturl(),len(b)
        except urllib.error.HTTPError as e:
            return u,e.code,e.geturl(),0
        except Exception as e:
            err=str(e); time.sleep(1)
    return u,'ERR',err,0
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(chk,sorted(L)))
json.dump(res,open('int_results.json','w'))
print(collections.Counter(r[1] for r in res))
for r in res:
    if r[1]!=200 or r[2]!=r[0] and not r[2].startswith(r[0].split('#')[0]): print(r)
