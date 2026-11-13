# independent recount; does not import neo_tick
import json,glob,gzip,os,re,math,hashlib,calendar,time,collections as C,sys
B='/Users/heuremen/bones-forge/neo_index/'
def jd_of_ts(ts): return calendar.timegm(time.strptime(ts[:14],'%Y%m%d%H%M%S'))/86400+2440587.5
def f(x):
    try:
        v=float(x); return v if math.isfinite(v) else None
    except: return None
def rows_of(doc):
    if not isinstance(doc,dict) or 'Close Approach' not in doc.get('signature',{}).get('source',''): return None
    fl=doc.get('fields'); 
    if not fl or 'data' not in doc: return None
    need=['des','orbit_id','jd','dist','dist_min','dist_max']
    if any(n not in fl for n in need): return None
    out=[]
    for r in doc['data']:
        x=dict(zip(fl,r))
        if 'body' in x and x['body']!='Earth': continue
        out.append(dict(des=str(x['des']).split('|')[-1].strip(),oid=str(x['orbit_id']),jd=f(x['jd']),d=f(x['dist']),lo=f(x['dist_min']),hi=f(x['dist_max'])))
    return out
copies=[]
cdx=json.load(open(B+'data/raw/wayback/cdx_cad_api.json'))[1:]
import urllib.parse
for ts,orig,sc,ln in cdx:
    q=urllib.parse.parse_qs(urllib.parse.urlsplit(orig).query); body=(q.get('body') or ['Earth'])[0]
    p=B+'data/raw/wayback/cad_%s_%s.json'%(ts,hashlib.sha1(orig.encode()).hexdigest()[:8])
    if body!='Earth' or not os.path.exists(p): continue
    try: rs=rows_of(json.load(open(p)))
    except: continue
    if rs is None: continue
    copies.append(('wb',ts,jd_of_ts(ts),rs))
for p in sorted(glob.glob(B+'data/snapshots/cad_*.json.gz')):
    ts=re.search(r'_(\d{8}T\d{6})Z',p).group(1).replace('T','')
    rs=rows_of(json.load(gzip.open(p)))
    if rs: copies.append(('own',ts,jd_of_ts(ts),rs))
print('copies used',len(copies),C.Counter(c[0] for c in copies))
cur=json.load(open(B+'data/raw/cad_current.json'))
curs=rows_of(cur); bydes=C.defaultdict(list)
for r in curs: bydes[r['des']].append(r)
NOW=jd_of_ts('20261111095331')
# cluster approaches per des
alljd=C.defaultdict(list)
for src,ts,cj,rs in copies:
    for r in rs:
        if r['jd'] and r['d'] is not None and r['d']<=0.05 and r['jd']>=2460310.5: alljd[r['des']].append(r['jd'])
anch={}
for des,l in alljd.items():
    l=sorted(set(l)); gs=[]
    for j in l:
        if gs and j-gs[-1][-1]<=10: gs[-1].append(j)
        else: gs.append([j])
    anch[des]=gs
def grp(des,j):
    for i,g in enumerate(anch[des]):
        if g[0]-1e-9<=j<=g[-1]+1e-9: return i
first={}
for src,ts,cj,rs in sorted(copies,key=lambda c:c[2]):
    for r in rs:
        if not r['jd'] or r['d'] is None or r['d']>0.05 or r['jd']<2460310.5: continue
        if cj>=r['jd']: continue
        k=(r['des'],grp(r['des'],r['jd']),r['oid'])
        if k not in first: first[k]=dict(r,cj=cj,ts=ts,src=src)
def nearest(des,jd,pool):
    b=None
    for r in pool:
        if r['jd'] and abs(r['jd']-jd)<=10 and (b is None or abs(r['jd']-jd)<abs(b['jd']-jd)): b=r
    return b
def cachelook(des,jd):
    p=B+'data/cache/des_%s_%d.json'%(re.sub(r'\W+','_',des),round(jd))
    if not os.path.exists(p): return None
    rs=rows_of(json.load(open(p))) or []
    return nearest(des,jd,rs)
rows=[]; miss_cache=0
for (des,g,oid),s in first.items():
    if s['jd']>NOW: oc='NOT_YET'; why=None; d=None
    else:
        d=nearest(des,s['jd'],bydes.get(des,[])) or cachelook(des,s['jd'])
        lo,hi=s['lo'],s['hi']
        if lo is None or hi is None or lo>hi: oc,why='CANNOT_TELL','unreadable'
        elif d is None: oc,why='CANNOT_TELL','no record'
        elif d['lo'] is None or d['hi'] is None or d['lo']>d['hi'] or d['d'] is None: oc,why='CANNOT_TELL','unreadable'
        elif d['oid']==s['oid']: oc,why='CANNOT_TELL','same solution'
        elif hi-lo>0.05: oc,why='CANNOT_TELL','wide range'
        elif d['lo']>hi: oc,why='ABOVE',None
        elif d['hi']<lo: oc,why='BELOW',None
        elif d['lo']>=lo and d['hi']<=hi: oc,why='CONSISTENT',None
        else: oc,why='CANNOT_TELL','edge'
    rows.append(dict(des=des,g=g,oid=oid,jd=s['jd'],lead=s['jd']-s['cj'],ts=s['ts'],src=s['src'],oc=oc,why=why,lo=s['lo'],hi=s['hi'],d=d,s=s))
best={}
for r in rows:
    k=(r['des'],r['g'])
    if k not in best or r['lead']>best[k]['lead']: best[k]=r
head=list(best.values())
def wilson(k,n,z=1.959963984540054):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return c-h,c+h
def cellout(rs):
    seen=set(); once=[]
    for r in sorted(rs,key=lambda r:r['jd']):
        if r['des'] in seen: continue
        seen.add(r['des']); once.append(r)
    cnt=C.Counter(r['oc'] for r in once); n=cnt['CONSISTENT']+cnt['ABOVE']+cnt['BELOW']; k=cnt['CONSISTENT']
    lo,hi=wilson(k,n) if n else (0,1)
    o='CANNOT_TELL' if n<10 else 'BELOW' if hi<0.9973 else 'ABOVE' if lo>0.9973 else 'CONSISTENT' if lo>=0.98 else 'CANNOT_TELL'
    why=C.Counter(r['why'] for r in once if r['oc']=='CANNOT_TELL')
    return dict(objs=len(once),scored=n,inside=k,above=cnt['ABOVE'],below=cnt['BELOW'],ct=cnt['CANNOT_TELL'],not_yet=cnt['NOT_YET'],lo=round(lo,4),hi=round(hi,4),out=o,why=dict(why)),once
def lead(rs,a,b): return [r for r in rs if (a<r['lead']<=b)]
LE=[('all',-1,1e9),('0-7',-1,7),('8-30',7,30),('>30',30,1e9)]
res={}
for nm,a,b in LE:
    c,once=cellout(lead(head,a,b)); res[nm]=c; print(nm,c)
c,_=cellout([r for r in head if time.strftime('%Y-%m',time.gmtime((r['jd']-2440587.5)*86400))=='2026-08']); print('aug26',c)
# without feb 9 2024 copy
c,_=cellout([r for r in head if r['ts'][:8]!='20240209']); print('without feb9 (heads w/ other copies)',c)
# alternative: drop the copy then recompute heads
import copy as cp
json.dump([dict(des=r['des'],g=r['g'],oid=r['oid'],jd=r['jd'],lead=r['lead'],ts=r['ts'],oc=r['oc'],why=r['why']) for r in rows],open('/Users/heuremen/bones-forge/neo_index_referee/my_rows.json','w'))
print('rows',len(rows),'headline',len(head))
