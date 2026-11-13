import sys,json,re
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
exec(S.split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
m3=[r for r in BIN if r['mag']==3.0]
flag=[]
for r in m3:
    ev=events[r['seq']]; ts,ms=zone_events(r['seq'],r['zone'])
    a=bisect.bisect_left(ts,r['t0']); b=bisect.bisect_left(ts,r['t1'])
    r['later_big']=any(m>=ev['mag'] for m in ms[a:b])
fl=[r for r in m3 if r['later_big']]; un=[r for r in m3 if not r['later_big']]
for nm,rs in (('flagged (an event as large as the mainshock inside window and zone)',fl),('rest',un)):
    k=sum(1 for r in rs if r['outcome']=='CONSISTENT'); print(nm,len(rs),k,round(k/len(rs),4),'above',sum(1 for r in rs if r['outcome']=='ABOVE'),'below',sum(1 for r in rs if r['outcome']=='BELOW'))
c=cover_cell('rest',un,1); print('headline without flagged rows: share %.4f [%.4f,%.4f] %s bl%d'%(c['share'],c['lo'],c['hi'],c['outcome'],c['blocks']))
print('flagged by window',C.Counter(r['window'] for r in fl))
print('flagged sequences',len({r['seq'] for r in fl}))
# 1 year w/o flagged
y=[r for r in un if r['window']=='1 Year']; c=cover_cell('y',y,1); print('1 year without flagged: n %d share %.4f [%.4f,%.4f] %s'%(c['scored'],c['share'],c['lo'],c['hi'],c['outcome']))
# exclusion matters?
n_ex=0
for r in BIN[:]:
    ev=events[r['seq']]
    for (t,la,lo,dp,m,ii,i) in cat[r['seq']]:
        pass
    break
ex_in=0
for eid in ids:
    ev=events[eid]; exs=[e for e in cat[eid] if e[5]&ev['ids']]
    tmin=min((r['t0'] for r in BIN if r['seq']==eid),default=None)
    for e in exs:
        if tmin is not None and e[0]>=tmin: ex_in+=1
print('excluded catalog events that fall at/after the earliest scored window start:',ex_in)
# data-file id list vs detail ids
import glob
diff=0;tot=0
for f in glob.glob(R+'forecast/*_data.json'):
    d=json.load(open(f)); ml=d['mainshock'].get('mainshock_id_list') or []; pe=d.get('pdl_event_id')
    if pe in events:
        tot+=1
        if not set(ml)<=events[pe]['ids']: diff+=1; print('  id list not subset',pe,ml,events[pe]['ids'])
print('data files id list checked',tot,'not subset',diff)
res=json.load(open('/Users/heuremen/bones-forge/quake_index_referee/out/recount.json'))
print('rel blocks',[c['blocks'] for c in res['rel']])
