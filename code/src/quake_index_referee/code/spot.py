import sys,json,time,urllib.request,urllib.parse,datetime
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
BIN=[r for r in sc if r['kind']=='bin']
import random
rng=random.Random(5)
def pick(f,key=None,n=1):
    c=[r for r in BIN if f(r)]
    if key: c.sort(key=key); return c[:n]
    return rng.sample(c,n)
cands=[]
# high-prob miss, small zone event with modest catalog
cands+= [('high-p miss',r) for r in pick(lambda r:r['p']>=0.99 and r['count']==0 and r['mag']==3.0 and len(cat[r['seq']])<3000,n=2)]
# large ABOVE row (count modest)
cands+= [('large above',r) for r in pick(lambda r:r['outcome']=='ABOVE' and r['count']<4000 and r['mag']==3.0,key=lambda r:-(r['count']-r['nmax']),n=2)]
cands+= [('1 year BELOW',r) for r in pick(lambda r:r['outcome']=='BELOW' and r['window']=='1 Year' and r['mag']==3.0 and len(cat[r['seq']])<5000,n=1)]
cands+= [('random consistent',r) for r in pick(lambda r:r['outcome']=='CONSISTENT' and r['count']>=3 and r['zone'][3] is None,n=2)]
cands+= [('depth-filtered zone',r) for r in pick(lambda r:r['zone'][3] is not None and r['count']>=1 and r['mag']==3.0,n=1)]
def iso(ms): return datetime.datetime.fromtimestamp(ms/1000,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.')+'%03d'%(ms%1000)
res=[]
for tag,r in cands:
    z=r['zone']
    q=dict(format='geojson',starttime=iso(r['t0']),endtime=iso(r['t1']-1),latitude=z[0],longitude=z[1],maxradiuskm=z[2],minmagnitude=r['mag'],eventtype='earthquake')
    if z[3] is not None: q['mindepth']=z[3]; q['maxdepth']=z[4]
    url='https://earthquake.usgs.gov/fdsnws/event/1/count?'+urllib.parse.urlencode(q)
    req=urllib.request.Request(url,headers={'User-Agent':'heuremen-quake-referee/0.1 (+https://indahl.ai/quake)'})
    try:
        body=urllib.request.urlopen(req,timeout=60).read().decode()
        cnt=json.loads(body)['count']
    except Exception as e: cnt='ERR '+repr(e)[:80]
    res.append(dict(tag=tag,seq=r['seq'],window=r['window'],mag=r['mag'],p=r['p'],nmin=r['nmin'],nmax=r['nmax'],mine=r['count'],comcat=cnt,url=url))
    print(tag,r['seq'],r['window'],'M%g'%r['mag'],'p',r['p'],'[%d,%d]'%(r['nmin'],r['nmax']),'mine',r['count'],'ComCat',cnt,flush=True)
    time.sleep(1.2)
json.dump(res,open('/Users/heuremen/bones-forge/quake_index_referee/out/spot_checks.json','w'),indent=1)
