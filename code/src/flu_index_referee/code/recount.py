import csv,glob,os,json,collections,math,datetime as dt
import numpy as np
H='/Users/heuremen/bones-forge/flu_index/data/raw/hub/'
OUT='/Users/heuremen/bones-forge/flu_index_referee/out/'
D=dt.date.fromisoformat
QS=['0.01','0.025','0.05']+['%.2f'%(x/100) for x in range(10,91,5)]+['0.95','0.975','0.99']
QS=sorted(set('%g'%float(x) for x in QS),key=float); assert len(QS)==23
def loadmodel(name):
    m={}  # (ref,loc,h)->(target_end,{q:val})
    dup=0;cross=0;files=0;nonint=0
    for f in sorted(glob.glob(H+'model-output/%s/*.csv'%name)):
        files+=1
        for r in csv.DictReader(open(f)):
            if r['target']!='wk inc flu hosp' or r['output_type']!='quantile': continue
            h=int(r['horizon'])
            if h<0: continue
            k=(r['reference_date'],r['location'],h)
            e=m.setdefault(k,[r['target_end_date'],{}])
            q=('%g'%float(r['output_type_id']))
            if q in e[1]: dup+=1
            e[1][q]=float(r['value'])
    return m,dup,files
# delivered
ts=collections.defaultdict(dict) # (loc,week)->{asof:set(values)}
for r in csv.DictReader(open(H+'target-data/time-series.csv')):
    if r['target']!='wk inc flu hosp': continue
    ts[(r['location'],r['target_end_date'])].setdefault(r['as_of'],set()).add(r['observation'])
def val(s):
    if len(s)!=1: return 'unread'
    try: return float(next(iter(s)))
    except ValueError: return 'unread'
def final(loc,wk):
    d=ts.get((loc,wk))
    if not d: return 'none'
    return val(d[max(d)])
def first(loc,wk):
    d=ts.get((loc,wk))
    if not d: return 'none'
    a=min(d)
    if (D(a)-D(wk)).days>14: return 'noearly'
    return val(d[a])
def out(y,l,u):
    if y is None: return 'CT'
    return 'C' if l<=y<=u else ('A' if y>u else 'B')
def season(ref):
    return '2023-24' if ref<='2024-07-31' else '2024-25' if ref<='2025-07-31' else '2025-26' if ref<='2026-07-31' else '2026-27'
def wis(q,y):
    s=0.5*abs(y-q['0.5'])
    for a in [0.02,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
        l=q['%g'%(a/2)];u=q['%g'%(1-a/2)]
        s+=(a/2)*((u-l)+(2/a)*max(l-y,0)+(2/a)*max(y-u,0))
    return s/11.5
ens,dupE,nfE=loadmodel('FluSight-ensemble'); base,dupB,nfB=loadmodel('FluSight-baseline')
rows=[];cross=0;ties=0;nq=0
for k in sorted(ens):
    ref,loc,h=k; te,q=ens[k]
    if len(q)!=23: nq+=1; continue
    vals=[q[x] for x in QS]
    if any(vals[i]>vals[i+1] for i in range(22)): cross+=1
    if q['0.25']==q['0.75']: ties+=1
    r=dict(ref=ref,loc=loc,h=h,week=te,season=season(ref))
    bq=base.get(k); hb=bq is not None and len(bq[1])==23
    for side,fn in (('final',final),('first',first)):
        y=fn(loc,te)
        if y=='none': y=None
        r[side]=y if not isinstance(y,str) else None
        ct = y=='noearly'
        for lv,(a,b) in (('50',('0.25','0.75')),('95',('0.025','0.975'))):
            o='CT' if ct else out(y,q[a],q[b]) if not isinstance(y,str) else 'CT'
            r['o%s_%s'%(lv,side)]=('NR' if (y is None and not ct) else o)
        if y is not None and not isinstance(y,str):
            r['wisE_'+side]=wis(q,y)
            if hb: r['wisB_'+side]=wis(bq[1],y)
    rows.append(r)
json.dump(rows,open(OUT+'rows.json','w'))
print('rows',len(rows),'files',nfE,nfB,'dup',dupE,dupB,'shortq',nq,'crossing',cross,'zero50',ties)
# diff
desk=json.load(open('/Users/heuremen/bones-forge/flu_index/data/flu.json'))['rows']
dk={(d['ref'],d['loc'],d['h']):d for d in desk}
mp={'CONSISTENT':'C','ABOVE':'A','BELOW':'B','NOTHING_RETURNED':'NR','CANNOT_TELL':'CT'}
diffs=[];only=0
for r in rows:
    d=dk.get((r['ref'],r['loc'],r['h']))
    if not d: only+=1;continue
    for lv in ('50','95'):
        for s in ('final','first'):
            dv=d['o%s_%s'%(lv,s)]
            if mp[dv]!=r['o%s_%s'%(lv,s)]: diffs.append((r['ref'],r['loc'],r['h'],lv,s,dv,r['o%s_%s'%(lv,s)]))
    for s in ('final','first'):
        if d[s]!=r[s]: diffs.append((r['ref'],r['loc'],r['h'],'val',s,d[s],r[s]))
        for w in ('E','B'):
            a=d.get('wis_%s_%s'%('ens' if w=='E' else 'base',s)); b=r.get('wis%s_%s'%(w,s))
            if (a is None)!=(b is None) or (a is not None and abs(a-b)>1e-3): diffs.append((r['ref'],r['loc'],r['h'],'wis'+w,s,a,b))
print('only referee',only,'only desk',len(dk)-len(rows)+only,'diffs',len(diffs)); print(diffs[:10])
json.dump(diffs,open(OUT+'diff_vs_desk.json','w'))
# counts
for lv in ('95','50'):
  for s in ('final','first'):
    print(lv,s,collections.Counter(r['o%s_%s'%(lv,s)] for r in rows))
# first-asof lag distribution
lag=collections.Counter()
for r in rows[:]:
    d=ts.get((r['loc'],r['week']))
    if d: lag[((D(min(d))-D(r['week'])).days)]+=1
print('first as_of lag days (rows):',sorted(lag.items()))
