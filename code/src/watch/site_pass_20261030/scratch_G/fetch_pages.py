import urllib.request, concurrent.futures as cf, os, sys, json, time
urls=[l.strip() for l in open('../lane_G_urls.txt') if l.strip()]
os.makedirs('pages',exist_ok=True)
def get(u):
    name=u.rstrip('/').split('/')[-1]
    for attempt in range(3):
        try:
            req=urllib.request.Request(u+'?w=1',headers={'User-Agent':'indahl-sitepass/1.0'})
            r=urllib.request.urlopen(req,timeout=30)
            body=r.read()
            open('pages/%s.html'%name,'wb').write(body)
            return u,r.status,len(body),dict(r.headers).get('Content-Type')
        except Exception as e:
            err=str(e)
            time.sleep(1)
    return u,'ERR',0,err
with cf.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(get,urls))
json.dump(res,open('fetch_results.json','w'))
import collections
print(collections.Counter(r[1] for r in res))
print([r for r in res if r[1]!=200])
