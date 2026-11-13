import sys,json
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
exec(S.split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
summ=json.load(open('/Users/heuremen/bones-forge/quake_index/summary_quake.json'))
# 1 outside-row sensitivity: score outside rows too (window closed, zone stated)
extra=[]
for r in rows:
    if r['status']!='outside' or r['zone'] is None or r['kind']!='bin': continue
    if r['t1']+7*DAY>fetched[r['seq']]: continue
    n=count(r['seq'],r['zone'],r['t0'],r['t1'],r['mag'])
    r2=dict(r); r2['count']=n; r2['occurred']=n>=1; r2['outcome']='CONSISTENT' if r['nmin']<=n<=r['nmax'] else ('ABOVE' if n>r['nmax'] else 'BELOW'); extra.append(r2)
allr=BIN+extra
for nm,rs in (('in frame only M3',[r for r in BIN if r['mag']==3.0]),('with out-of-frame rows M3',[r for r in allr if r['mag']==3.0])):
    k=sum(1 for r in rs if r['outcome']=='CONSISTENT'); print(nm,len(rs),k,round(k/len(rs),4))
rs=[r for r in extra if r['mag']==3.0]; k=sum(1 for r in rs if r['outcome']=='CONSISTENT'); print('out-of-frame M3 only',len(rs),k,round(k/len(rs),4))
rs=[r for r in allr if r['p']>=0.1]; print('p>=10 with outside: share %.3f stated %.3f n %d'%(sum(r['occurred'] for r in rs)/len(rs),sum(r['p'] for r in rs)/len(rs),len(rs)))
# 2 counter gate (own implementation)
tot=agree=0
for eid,p in versions:
    doc,why=load_forecast(p)
    if not doc: continue
    mp=doc['model']['parameters']
    if 'Sequence Specific' not in (doc['model'].get('name') or ''): continue
    zone=None
    if mp.get('regionType')=='circle': zone=(mp['regionCenterLat'],mp['regionCenterLon'],mp['regionRadius'],None,None)
    else:
        fd=R+'forecast/%s_%s_%d_data.json'%(p['code'],p['source'],p['updateTime'])
        if os.path.exists(fd):
            P=json.load(open(fd))['parameters']; rg=P.get('aftershock_search_region') or {}
            if 'center' in rg: zone=(rg['center']['lat'],rg['center']['lon'],rg['radius'],P.get('min_depth'),P.get('max_depth'))
    if not zone: continue
    obs=[o['count'] for o in doc.get('observations',[]) if o['magnitude']==3.0]
    if not obs or obs[0]<1: continue
    n=count(eid,zone,events[eid]['time']+1,doc['creationTime'],3.0)
    tot+=1
    if abs(n-obs[0])<=max(2,0.2*obs[0]): agree+=1
print('counter gate (mine): %d of %d agree (desk 604 of 655)'%(agree,tot))
# 3 leave-block-out
def share(rs,f): return sum(1 for r in rs if f(r))/len(rs)
m3=[r for r in BIN if r['mag']==3.0]
bc=C.Counter(r['block'] for r in m3)
top=[b for b,_ in bc.most_common(5)]
print('M3 headline minus each of top 5 blocks:')
for b in top:
    rs=[r for r in m3 if r['block']!=b]; c=cover_cell('x',rs); print(' drop',b,len(rs),'share %.4f lo %.4f hi %.4f %s'%(c['share'],c['lo'],c['hi'],c['outcome']))
rs=[r for r in m3 if r['block'] not in top]; c=cover_cell('x',rs); print(' drop top5',len(rs),'share %.4f lo %.4f hi %.4f %s'%(c['share'],c['lo'],c['hi'],c['outcome']))
# per-block shares of M3 inside
bl=C.defaultdict(lambda:[0,0])
for r in m3: x=bl[r['block']]; x[0]+=r['outcome']=='CONSISTENT'; x[1]+=1
ordered=sorted(bl.items(),key=lambda kv:-kv[1][1])[:8]
print([(k,v[1],round(v[0]/v[1],3)) for k,v in ordered])
# p>=10 leave out top blocks
hi=[r for r in BIN if r['p']>=0.1]; hb=C.Counter(r['block'] for r in hi); print('p>=10 top blocks',[(k,round(v/len(hi),3)) for k,v in hb.most_common(5)])
for b,_ in hb.most_common(3):
    rs=[r for r in hi if r['block']!=b]; c=rel_cell('x',rs); print(' drop',b,len(rs),'share %.3f stated %.3f [%.3f,%.3f] %s'%(c['share'],c['stated'],c['lo'],c['hi'],c['outcome']))
# per-block: fraction of blocks with share<stated for p>=10
nb=0;nbelow=0
g=C.defaultdict(list)
for r in hi: g[r['block']].append(r)
for b,v in g.items():
    if len(v)>=30: nb+=1; nbelow+= (sum(r['occurred'] for r in v)/len(v)) < (sum(r['p'] for r in v)/len(v))
print('blocks with >=30 rows p>=10:',nb,'of which observed < stated:',nbelow)
# 4 first version
first={}
for eid,p in versions:
    doc,why=load_forecast(p)
    if not doc: continue
    if eid not in first or p['updateTime']<first[eid][0]: first[eid]=(p['updateTime'],p)
fr=[r for r in m3 if r['issued']==first[r['seq']][0]]
print('first-version M3 rows',len(fr),sum(1 for r in fr if r['outcome']=='CONSISTENT'),'desk',summ['described']['first_forecast_cover']['scored'],summ['described']['first_forecast_cover']['inside'])
# what do the sequences with zone not stated look like
ns=C.Counter(r['seq'] for r in rows if r['status']=='unscored' and r['outcome']=='CANNOT_TELL'); print('zone-not-stated rows by seq',ns.most_common(5), len(ns))
# max zone radius per event for PR
rad=C.defaultdict(float)
for r in rows:
    if r['zone']: rad[r['seq']]=max(rad[r['seq']],r['zone'][2])
print('pr2020007007 max zone radius',rad['pr2020007007'],'catalog',len(cat['pr2020007007']))
print('largest zones',sorted(rad.items(),key=lambda kv:-kv[1])[:5])
# near duplicates detail
for eid in ('aka2026jcufoy','us7000quxl'):
    ev=events[eid]; t0s=sorted(set(r['t0'] for r in rows if r['seq']==eid))[:1]; print(eid,ev['mag'],ev['time'],'first window t0 - main (min):',(t0s[0]-ev['time'])/60000 if t0s else None)
# depth none
nd=sum(1 for eid in ids for e in cat[eid] if e[3] is None); print('catalog events with no depth',nd)
# mag precision
dec=C.Counter(len(str(e[4]).split('.')[-1]) for eid in ids for e in cat[eid][:2000]); print('mag decimals',dec)
# net by window for M3
for nm,f in (('us',lambda r:r['net']=='us'),('regional',lambda r:r['net']!='us')):
    for w in ('1 Day','1 Week','1 Month','1 Year'):
        rs=[r for r in m3 if f(r) and r['window']==w]; k=sum(1 for r in rs if r['outcome']=='CONSISTENT'); print(nm,w,len(rs),k,round(k/len(rs),4))
print(summ['described']['cover_by_network'])
