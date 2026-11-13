import sys,json
sys.argv=['x']
src=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read().split("# ---- intervals")[0]
exec(src)
exec(open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read().split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
out={}
# 1 mainshock exclusion
nomatch=[];dup=[]
for eid in ids:
    ev=events[eid]; main=ev['ids']
    hit=[e for e in cat[eid] if e[5]&main]
    near=[e for e in cat[eid] if not (e[5]&main) and abs(e[0]-ev['time'])<=120000 and hav(ev['lat'],ev['lon'],e[1],e[2])<=30 and e[4]>=ev['mag']-0.3]
    if not hit: nomatch.append(eid)
    if near: dup.append((eid,[(e[6],e[4],e[0]-ev['time']) for e in near]))
    # larger-than-mainshock later events
out['mainshock_not_in_catalog']=nomatch; out['near_duplicates_not_excluded']=dup[:20]
# events whose catalog contains an event as big or bigger after mainshock
bigger=[]
for eid in ids:
    ev=events[eid]; main=ev['ids']
    b=[(e[6],e[4],(e[0]-ev['time'])/DAY) for e in cat[eid] if not(e[5]&main) and e[4]>=ev['mag'] and e[0]>ev['time']]
    if b: bigger.append((eid,ev['mag'],b[:3]))
out['later_as_large']=bigger
print('mainshock ids missing from catalog:',nomatch)
print('near-duplicate not excluded:',dup[:10])
print('later >= mainshock mag, in the catalog circle:',len(bigger),bigger[:8])
# is each later-larger event itself an oaf event (in events list)?
allids=set()
for e in events.values(): allids|=e['ids']
inlist=[(eid,[x for x in b if x[0] in allids]) for eid,m,b in bigger]
print('of those, in oaf list:',sum(1 for a,b in inlist if b))
# 2 boundaries
tb=0;rows_aff=0
for r in BIN:
    ts,ms=zone_events(r['seq'],r['zone'])
    a=bisect.bisect_left(ts,r['t0']); a2=bisect.bisect_right(ts,r['t0']); b=bisect.bisect_left(ts,r['t1']); b2=bisect.bisect_right(ts,r['t1'])
    if a2>a or b2>b: rows_aff+=1
print('rows with an event exactly at t0 or t1:',rows_aff)
# sensitivity: (t0,t1] instead
chg=0
for r in BIN:
    ts,ms=zone_events(r['seq'],r['zone'])
    a=bisect.bisect_right(ts,r['t0']); b=bisect.bisect_right(ts,r['t1'])
    n=sum(1 for m in ms[a:b] if m>=r['mag'])
    o='CONSISTENT' if r['nmin']<=n<=r['nmax'] else ('ABOVE' if n>r['nmax'] else 'BELOW')
    if o!=r['outcome']: chg+=1
print('outcome changes with (t0,t1]:',chg)
# in_zone '<' vs '<='  and zone radius edge
edge=0
for r in BIN[:0]: pass
# 3 zones: catalog circle covers zones?
cmax={}
for eid in ids:
    q=json.load(gzip.open(R+'catalog/%s.json.gz'%eid))['query']; cmax[eid]=q['maxradiuskm']
short=C.Counter(); worst=[]
for eid,p in versions:
    pass
seen=set()
for r in rows:
    if r['zone'] is None or r['status']=='outside': continue
    k=(r['seq'],r['zone'])
    if k in seen: continue
    seen.add(k)
    reach=hav(events[r['seq']]['lat'],events[r['seq']]['lon'],r['zone'][0],r['zone'][1])+r['zone'][2]
    if reach>cmax[r['seq']]+0.5: short[r['seq']]+=1; worst.append((r['seq'],reach,cmax[r['seq']]))
print('zones reaching beyond catalog circle:',dict(short),worst[:3])
# zone-offset: distance of zone center from mainshock, and radius distribution
offs=[hav(events[r['seq']]['lat'],events[r['seq']]['lon'],r['zone'][0],r['zone'][1]) for r in BIN[::50]]
print('zone center offset km max %.1f median %.1f'%(max(offs),sorted(offs)[len(offs)//2]))
rads=C.Counter(r['zone'][2] for r in BIN); print('radius km distribution',sorted(rads.items())[:12], 'n zones')
# consistency across forecast.json -> data switch for the same event
import glob
sw=[]
byev=C.defaultdict(list)
for eid,p in versions:
    doc,why=load_forecast(p)
    if not doc: continue
    mp=doc['model']['parameters']
    byev[eid].append((p['updateTime'],mp.get('regionType'),mp.get('regionCenterLat'),mp.get('regionCenterLon'),mp.get('regionRadius'),p))
cmp_=[]
for eid,v in byev.items():
    v.sort(key=lambda x:x[0])
    for a,b in zip(v,v[1:]):
        if a[1] is None and b[1]=='circle':
            fd=R+'forecast/%s_%s_%d_data.json'%(a[5]['code'],a[5]['source'],a[0])
            if os.path.exists(fd):
                rg=json.load(open(fd))['parameters'].get('aftershock_search_region')
                if rg: cmp_.append((eid,a[0],rg['center']['lat'],rg['center']['lon'],rg['radius'],b[0],b[2],b[3],b[4],(b[0]-a[0])/3600000))
print('adjacent data->circle switch pairs:',len(cmp_))
for x in cmp_[:8]: print(x)
# 4 index time vs update time
late_idx=0;tot=0;rows_flip=[]
idxmap={}
for eid,p in versions:
    idxmap[(eid,p['updateTime'])]=p.get('indexTime')
for r in BIN:
    it=idxmap.get((r['seq'],r['issued']))
    tot+=1
    if it is not None and it>r['t0']: late_idx+=1; rows_flip.append(r)
print('scored M-bin rows whose version indexTime is after t0:',late_idx,'of',tot)
rest=[r for r in BIN if not(r in rows_flip)] if False else None
fl=set(id(r) for r in rows_flip)
sub=[r for r in BIN if id(r) not in fl and r['mag']==3.0]
print('M3 without those rows:',len(sub),sum(1 for r in sub if r['outcome']=='CONSISTENT'))
# lag index-update
lags=[ (p.get('indexTime',0)-p['updateTime'])/1000 for e,p in versions if isinstance(p['contents'],dict)]
lags.sort(); print('index-update lag s: median %.1f p90 %.1f p99 %.1f max %.0f'%(lags[len(lags)//2],lags[int(.9*len(lags))],lags[int(.99*len(lags))],lags[-1]))
# 5 creationTime frame
cr=0
for eid,p in versions:
    pass
# 6 block dominance
bc=C.Counter(r['block'] for r in BIN if r['mag']==3.0)
tot=sum(bc.values()); print('top blocks share of M3 rows',[(k,round(v/tot,3)) for k,v in bc.most_common(6)])
out['block_top']=bc.most_common(8)
json.dump(out,open('/Users/heuremen/bones-forge/quake_index_referee/out/analysis1.json','w'),default=str,indent=1)
