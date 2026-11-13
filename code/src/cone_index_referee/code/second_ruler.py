import sys, json, re, collections
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
import numpy as np, pypdf
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
DESK='/Users/heuremen/bones-forge/cone_index/'
LEADS=[12,24,36,48,72,96,120]
def pdf(f):
    r=pypdf.PdfReader(DESK+'data/raw/docs/'+f); t="\n".join(p.extract_text() for p in r.pages)
    out={}
    for l in t.split('\n'):
        m=re.match(r'^(\d{4}) ((?:[\d.]+ \d+ ?)+)$',l.strip()+' ')
        if not m: continue
        nums=m.group(2).split()
        pairs=[(float(nums[i]),int(nums[i+1])) for i in range(0,len(nums)-1,2)]
        out[int(m.group(1))]=pairs
    return out
ST={'AL':pdf('1989-present_OFCL_ATL_annual_trk_errors.pdf'),'EP':pdf('1989-present_OFCL_EPAC_annual_trk_errors.pdf')}
HOURS=[0,12,24,36,48,72,96,120]
print({b:(min(v),max(v),len(v)) for b,v in ST.items()}, [len(v) for v in ST['AL'].values()][-3:])
rows=json.load(open(OUT+'rows.json'))
rng=np.random.default_rng(4242)
g=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rows:
    if r['tc'] and r['season']<=2025: g[(r['basin'],r['season'],r['lead'])][r['storm']].append(r['dist'])
res=[]
for b in('AL','EP'):
    for y in range(2010,2026):
        for L in LEADS:
            d=g.get((b,y,L),{})
            vals=[x for v in d.values() for x in v]; n=len(vals)
            pr=ST[b].get(y)
            sv,sn=(None,None)
            if pr and len(pr)==8: sv,sn=pr[HOURS.index(L)]
            ours=sum(vals)/n if n else None
            band=max(1.0,0.02*sv) if sv else None
            if sv is None or n==0: oc='CANNOT_TELL'
            elif abs(n-sn)>max(2,0.05*sn): oc='CANNOT_TELL'
            elif abs(ours-sv)<=band: oc='CONSISTENT'
            else: oc='ABOVE' if ours>sv else 'BELOW'
            res.append(dict(basin=b,season=y,lead=L,ours=ours,n=n,stated=sv,n_stated=sn,outcome=oc,storms=len(d)))
json.dump(res,open(OUT+'second_ruler_ref.json','w'),indent=1)
print(len(res),collections.Counter((r['basin'],r['outcome']) for r in res))
desk=json.load(open(DESK+'summary_cone.json'))['verification']
dm={(v['basin'],v['season'],v['lead']):v for v in desk}
bad=[]
for r in res:
    v=dm.get((r['basin'],r['season'],r['lead']))
    if not v: bad.append(('missing',r)); continue
    if v['outcome']!=r['outcome'] or v['n_ours']!=r['n'] or v['stated']!=r['stated'] or v['n_stated']!=r['n_stated'] or abs(round(r['ours'],1)-v['ours'])>0.051: bad.append((r,v))
print('desk rows',len(desk),'diffs',len(bad))
for x in bad[:6]: print(x)
for r in res:
    if r['outcome']!='CONSISTENT': print(r)
print('max |ours-stated| over comparable rows',max(abs(r['ours']-r['stated']) for r in res if r['outcome']=='CONSISTENT'))
print('max n diff',max(abs(r['n']-r['n_stated']) for r in res if r['outcome']=='CONSISTENT'))
# exact-match share
ex=[r for r in res if r['outcome']=='CONSISTENT' and abs(round(r['ours'],1)-r['stated'])<=0.1]
print('within 0.1 n mi',len(ex),'of',sum(1 for r in res if r['outcome']=='CONSISTENT'))
