import json,collections,numpy as np
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
rows=json.load(open(OUT+'rows.json'))
rng=np.random.default_rng(31)
def boot(items):
    d=collections.defaultdict(lambda:[0,0])
    for s,i in items: d[s][0]+=i; d[s][1]+=1
    ins=np.array([v[0] for v in d.values()]);n=np.array([v[1] for v in d.values()]);k=len(ins)
    idx=rng.integers(0,k,size=(2000,k)); sh=ins[idx].sum(1)/n[idx].sum(1)
    return ins.sum()/n.sum(),np.percentile(sh,2.5),np.percentile(sh,97.5)
def cl(sh,lo,hi):
    if lo>=0.6167 and hi<=0.7167: return 'CONSISTENT'
    if lo>0.7167: return 'ABOVE'
    if hi<0.6167: return 'BELOW'
    return 'CANNOT_TELL'
res={}
for b in('AL','EP'):
    for L in (12,24,36,48,72,96,120):
        sel=[r for r in rows if r['basin']==b and r['lead']==L and r['grp']=='final' and r['outcome'] in('INSIDE','OUTSIDE')]
        base=cl(*boot([(r['storm'],r['outcome']=='INSIDE') for r in sel]))
        ch=[]
        for y in range(2010,2026):
            rest=[r for r in sel if r['season']!=y]
            if not rest or len(rest)==len(sel): continue
            o=cl(*boot([(r['storm'],r['outcome']=='INSIDE') for r in rest]))
            if o!=base: ch.append((y,o))
        res['%s_%d'%(b,L)]=(base,ch)
        print(b,L,base,ch)
json.dump(res,open(OUT+'loso_circles.json','w'),indent=1)
