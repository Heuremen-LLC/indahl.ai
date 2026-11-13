import numpy as np, json, math
D='/Users/heuremen/bones-forge/seasonal_index/data/raw/cpc_verif_grid/'
rd=lambda f:np.fromfile(D+f,dtype='<f4').reshape(-1,684)
SEED=20261110; REPS=2000
BINS=[('under 25',-1e9,25),('25 to 30',25,31),('31 to 35',31,36),('36 to 39',36,40),('40 to 49',40,50),('50 to 59',50,60),('60 and over',60,1e9)]
def mult(S,B,reps=REPS,seed=SEED,starts_rule='full'):
    # own implementation: moving blocks, start uniform on 0..S-B, ceil(S/B) blocks, multiplicity matrix
    rng=np.random.default_rng(seed); nb=math.ceil(S/B)
    st=rng.integers(0,S-B+1,size=(reps,nb)); M=np.zeros((reps,S))
    for r in range(reps):
        idx=(st[r][:,None]+np.arange(B)[None,:]).ravel(); M[r]=np.bincount(idx,minlength=S)
    return M
def ci(num,den,M):
    a=M@num;b=M@den;ok=b>0;r=a[ok]/b[ok];return np.percentile(r,2.5),np.percentile(r,97.5)
def outcome(lo,hi,st,n,ns):
    if n<30 or ns<24: return 'CANNOT_TELL'
    if lo>st:return 'ABOVE'
    if hi<st:return 'BELOW'
    if hi-lo<=0.10:return 'CONSISTENT'
    return 'CANNOT_TELL'
def load(v):
    A=rd(f'{v}01_forecast_above.bi');B=rd(f'{v}01_forecast_below.bi');O=rd(f'{v}_seas_verif.bi')
    S=len(O);m=O[0]!=-9999
    A=A[:S][:,m];B=B[:S][:,m];O=O[:S][:,m]
    return {'above':(A,1),'near':(100-A-B,0),'below':(B,-1)},O
def cells(v,blocks=(12,)):
    P,O=load(v);S=len(O);res={}
    Ms={b:mult(S,b) for b in blocks}
    def mk(name,sel):
        num=np.zeros(S);den=np.zeros(S);ssum=0;n=0
        for c,(X,code) in P.items():
            s=sel(c,X);num+=(s&(O==code)).sum(1);den+=s.sum(1);ssum+=X[s].sum();n+=s.sum()
        ns=int((den>0).sum());st=ssum/n/100 if n else None
        d=dict(rows=int(n),seasons=ns,mean_stated=None if not n else round(st,4),observed=None if not n else round(num.sum()/n,4),hits=int(num.sum()))
        for b,M in Ms.items():
            lo,hi=ci(num,den,M) if n else (None,None)
            d[b]=dict(lo=None if lo is None else round(lo,4),hi=None if hi is None else round(hi,4),outcome=outcome(lo,hi,st,n,ns) if n else 'CANNOT_TELL')
        return d
    res['leaning']=mk('leaning',lambda c,X:X>=40)
    for c in P:
        for bn,a,b in BINS: res[f'{c}|{bn}']=mk('',lambda cc,X,c=c,a=a,b=b:(X>=a)&(X<b) if cc==c else np.zeros(X.shape,bool))
    return res
if __name__=='__main__':
    out={v:cells(v,(6,12,24)) for v in ['temp','prec']}
    json.dump(out,open('../out/rows.json','w'),indent=1)
    desk=json.load(open('/Users/heuremen/bones-forge/seasonal_index/summary_seasonal.json'))['cells']
    diffs=[];flips=[]
    for c in desk:
        v=c['variable'];key='leaning' if c['category']=='any' else f"{c['category']}|{c['bin']}"
        r=out[v][key]
        d=dict(cell=c['cell'],rows=(c['rows'],r['rows']),seasons=(c['seasons'],r['seasons']),stated=(c['mean_stated'],r['mean_stated']),obs=(c['observed'],r['observed']),hits=(c['hits'],r['hits']),
               lo=(c['lo'],r[12]['lo']),hi=(c['hi'],r[12]['hi']),outcome=(c['outcome'],r[12]['outcome']))
        diffs.append(d)
        for b in (6,24):
            if r[b]['outcome']!=r[12]['outcome']: flips.append((c['cell'],b,r[12]['outcome'],r[b]['outcome'],r[b]['lo'],r[b]['hi']))
    json.dump(diffs,open('../out/diff_vs_desk.json','w'),indent=1)
    cnt=lambda f:sum(1 for d in diffs if f(d))
    print('cells',len(diffs),'rows diff',cnt(lambda d:d['rows'][0]!=d['rows'][1]),'seasons diff',cnt(lambda d:d['seasons'][0]!=d['seasons'][1]),'hits diff',cnt(lambda d:d['hits'][0]!=d['hits'][1]),
      'stated diff',cnt(lambda d:d['stated'][0]!=d['stated'][1]),'obs diff',cnt(lambda d:d['obs'][0]!=d['obs'][1]),'outcome diff',cnt(lambda d:d['outcome'][0]!=d['outcome'][1]))
    ml=max(max(abs(d['lo'][0]-d['lo'][1]),abs(d['hi'][0]-d['hi'][1])) for d in diffs if d['lo'][0] is not None);print('max interval diff',ml)
    for d in diffs:
        if d['outcome'][0]!=d['outcome'][1]: print('OUTCOME DIFF',d)
    print('FLIPS vs block 12:');[print(f) for f in flips]
    for v in out: print(v,'leaning',{b:out[v]['leaning'][b] for b in (6,12,24)})
