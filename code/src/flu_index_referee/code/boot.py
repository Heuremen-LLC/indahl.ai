import json,math,collections,numpy as np
OUT='/Users/heuremen/bones-forge/flu_index_referee/out/'
rows=json.load(open(OUT+'rows.json'))
S=json.load(open('/Users/heuremen/bones-forge/flu_index/summary_flu.json'))
weeks=sorted({r['week'] for r in rows if r['o95_final'] in('C','A','B')}); W=len(weeks); wi={w:i for i,w in enumerate(weeks)}
def draws(L,reps=2000,seed=20261110,circ=False):
    rng=np.random.default_rng(seed); nb=math.ceil(W/L); M=np.zeros((reps,W))
    for i in range(reps):
        st=rng.integers(0,W-L+1,nb)
        for s in st: M[i,s:s+L]+=1
    return M
def agg(sel,num,den):
    n=np.zeros(W);d=np.zeros(W)
    for r in sel:
        i=wi.get(r['week'])
        if i is None: continue
        a,b=num(r),den(r)
        n[i]+=a;d[i]+=b
    return n,d
def interval(n,d,M):
    N=M@n;Dd=M@d;ok=Dd>0
    s=N[ok]/Dd[ok]; return np.percentile(s,[2.5,97.5])
def rule(p,lo,hi,scored,nweeks,maxw):
    if scored<30 or nweeks<8: return 'CANNOT_TELL'
    if hi<p: return 'BELOW'
    if lo>p: return 'ABOVE'
    return 'CONSISTENT' if hi-lo<=maxw else 'CANNOT_TELL'
def cellsel(name):
    if name=='all horizons': return rows
    if name.startswith('horizon'): return [r for r in rows if r['h']==int(name.split()[1])]
    if name.startswith('season'): return [r for r in rows if r['season']==name.split()[1]]
    return [r for r in rows if r['loc']==name]
Ms={L:draws(L) for L in (4,8,13)}
res=[];flip=[]
def cov(name,lv,side):
    sel=cellsel(name); k='o%s_%s'%(lv,side)
    sc=[r for r in sel if r[k] in('C','A','B')]
    n,d=agg(sc,lambda r:r[k]=='C',lambda r:1)
    return sc,n,d
allc=list(S['cells'])
for loc in S['by_location']:
    for c in loc['cells']: allc.append(dict(c,cell=loc['loc']))
out=[]
for c in allc:
    sc,n,d=cov(c['cell'],c['level'],c['side'])
    nw=len({r['week'] for r in sc}); p=c['stated']
    row=dict(cell=c['cell'],level=c['level'],side=c['side'],scored=len(sc),inside=int(n.sum()),desk_scored=c['scored'],desk_inside=c['inside'],nw=nw,desk_lo=c['lo'],desk_hi=c['hi'],desk_out=c['outcome'])
    for L,M in Ms.items():
        lo,hi=interval(n,d,M) if len(sc) else (None,None)
        row['lo%d'%L]=lo;row['hi%d'%L]=hi
        row['out%d'%L]=rule(p,lo,hi,len(sc),nw,0.10) if lo is not None else 'CANNOT_TELL'
    out.append(row)
wo=[]
for w in S['wis']:
    name=w['cell'];side=w['side']
    sel=[r for r in cellsel(name) if ('wisE_'+side) in r and ('wisB_'+side) in r]
    n,d=agg(sel,lambda r:r['wisE_'+side],lambda r:r['wisB_'+side])
    nw=len({r['week'] for r in sel}); ratio=n.sum()/d.sum()
    row=dict(cell=name,side=side,rows=len(sel),desk_rows=w['rows'],ratio=ratio,desk_ratio=w['ratio'],desk_lo=w['lo'],desk_hi=w['hi'],desk_out=w['outcome'])
    for L,M in Ms.items():
        lo,hi=interval(n,d,M); row['lo%d'%L]=lo;row['hi%d'%L]=hi
        if len(sel)<30 or nw<8: o='CANNOT_TELL'
        elif hi<1:o='BELOW'
        elif lo>1:o='ABOVE'
        else:o='CONSISTENT' if hi-lo<=0.2 else 'CANNOT_TELL'
        row['out%d'%L]=o
    wo.append(row)
json.dump(dict(cov=out,wis=wo),open(OUT+'boot.json','w'),indent=1,default=float)
cnt=sum(1 for r in out if r['scored']!=r['desk_scored'] or r['inside']!=r['desk_inside'])
print('cov cells',len(out),'count mismatches',cnt)
mism=[r for r in out if r['out4']!=r['desk_out']]
print('outcome mismatches at L=4:',len(mism))
for r in mism: print(r['cell'],r['level'],r['side'],r['desk_out'],r['out4'],'desk',r['desk_lo'],r['desk_hi'],'ref',r['lo4'] and round(r['lo4'],4),r['hi4'] and round(r['hi4'],4))
md=max(max(abs(r['lo4']-r['desk_lo']),abs(r['hi4']-r['desk_hi'])) for r in out if r['lo4'] is not None)
print('max endpoint diff',md)
for L in (8,13):
    ch=[r for r in out if r['out%d'%L]!=r['out4']]
    print('L',L,'changes vs L4:',len(ch))
    for r in ch[:40]: print('  ',r['cell'],r['level'],r['side'],r['out4'],'->',r['out%d'%L],round(r['lo%d'%L],3),round(r['hi%d'%L],3))
print('WIS rows mism',sum(1 for r in wo if r['rows']!=r['desk_rows']),'ratio max diff',max(abs(r['ratio']-r['desk_ratio']) for r in wo))
for r in wo:
    print(r['cell'],r['side'],round(r['ratio'],4),r['desk_ratio'],'desk',r['desk_lo'],r['desk_hi'],r['desk_out'],'| ref',round(r['lo4'],3),round(r['hi4'],3),r['out4'],'L8',r['out8'],round(r['lo8'],3),round(r['hi8'],3))
print('headline cell:',[ (r['lo4'],r['hi4'],r['lo8'],r['hi8'],r['lo13'],r['hi13']) for r in out if r['cell']=='all horizons' and r['level']=='95' and r['side']=='final'])
