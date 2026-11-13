import json, re, sys, numpy as np, itertools, csv
D=sys.argv[1]  # release root (data only, nothing imported from it)
P=re.compile(r'\[\[([AB<>=]+)\]\]'); F=re.compile(r'\[([AB<>=]+)\]')
SC={'A>>B':-2,'A>B':-1,'A=B':0,'B>A':1,'B>>A':2}
def parse(t):
    u=t.upper(); m=P.findall(u) or F.findall(u); return m[-1] if m else None
mism=[0,0]
def load(run,cell):
    out={}
    for line in open(f'{D}/data/october_rerun/{run}/{cell}.jsonl'):
        r=json.loads(line); s=[]; fp=[]
        for k,sg in (('round1',1),('round2',-1)):
            v=parse(r[k].get('raw') or ''); mism[0]+=1; mism[1]+= (v!=r[k].get('verdict'))
            s.append(sg*SC[v] if v in SC else np.nan); fp.append(r[k].get('system_fingerprint'))
        out[r['uid']]=(np.nan if np.isnan(s).any() else sum(s)/2, tuple(fp), r.get('timestamp'))
    return out
cells=['C1F1D1','C1F1D2','C2F1D1','C2F1D2','C1F2D1','C1F2D2','C2F2D1','C2F2D2']
data={c:{r:load(r,c) for r in (['run1','run2','run3'] if c=='C1F1D1' else ['run1','run2'])} for c in cells}
diff=lambda a,b: 100*np.mean(np.sign(a)!=np.sign(b))
dflt=data['C1F1D1']; res={}
for c in cells[1:]:
    S=data[c]; uids=[u for u in dflt['run1'] if all(u in x and not np.isnan(x[u][0]) for x in list(dflt.values())+list(S.values()))]
    Dm=np.array([[dflt[r][u][0] for r in ('run1','run2','run3')] for u in uids]); Sm=np.array([[S[r][u][0] for r in ('run1','run2')] for u in uids])
    ch=np.mean([diff(Dm[:,i],Sm[:,j]) for i in range(3) for j in range(2)]); df=np.mean([diff(Dm[:,i],Dm[:,j]) for i,j in itertools.combinations(range(3),2)]); sf=diff(Sm[:,0],Sm[:,1])
    res[c]=dict(n=len(uids),score_change=50+25*Sm.mean()-(50+25*Dm.mean()),pct_diff=ch,default_floor=df,setup_floor=sf,excess_paper=ch-df,excess_both=ch-(df+sf)/2,excess_own=ch-sf)
ref={r['cell_id'] if 'cell_id' in r else r[list(r)[0]]:r for r in csv.DictReader(open(f'{D}/results/october_rerun/step2_table1_october.csv'))}
print('parser vs their stored verdict: %d of %d calls differ'%(mism[1],mism[0]))
for c,v in res.items():
    print(c, ' '.join(f'{k}={v[k]:.2f}' if k!='n' else f'n={v[k]}' for k in v))
# default rerun floor (abstract 21.2%): pairs of default runs on prompts complete in all 3
u3=[u for u in dflt['run1'] if all(u in dflt[r] and not np.isnan(dflt[r][u][0]) for r in dflt)]
for a,b in itertools.combinations(['run1','run2','run3'],2):
    A=np.array([dflt[a][u][0] for u in u3]);B=np.array([dflt[b][u][0] for u in u3]); print('default',a,b,'boundary %.1f%%'%diff(A,B),'score shift %+.2f'%(25*(B-A).mean()))
json.dump(dict(res=res,ref=ref),open('recount_out.json','w'),indent=1,default=str)
# B1 fingerprint carrier
rng=np.random.default_rng(20261025); print('--- B1')
for a,b in itertools.combinations(['run1','run2','run3'],2):
    same=[];dif=[]
    for u in u3:
        flip=np.sign(dflt[a][u][0])!=np.sign(dflt[b][u][0])
        (same if dflt[a][u][1]==dflt[b][u][1] else dif).append(flip)
    same,dif=np.array(same,float),np.array(dif,float)
    if min(len(same),len(dif))<30: print(a,b,'match n=%d differ n=%d -> CANNOT_TELL'%(len(same),len(dif))); continue
    bs=[dif[rng.integers(0,len(dif),len(dif))].mean()-same[rng.integers(0,len(same),len(same))].mean() for _ in range(20000)]
    lo,hi=np.percentile(bs,[2.5,97.5]); oc='ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'
    print(a,b,'match n=%d flip %.1f%% | differ n=%d flip %.1f%% | diff %+.1f pp [%+.1f, %+.1f] -> %s'%(len(same),100*same.mean(),len(dif),100*dif.mean(),100*(dif.mean()-same.mean()),100*lo,100*hi,oc))
# known-good: run vs itself
kg=sum(np.sign(dflt['run1'][u][0])!=np.sign(dflt['run1'][u][0]) for u in u3); print('known-good run1 vs run1 flips:',kg)
fps=set(f for r in dflt for u in dflt[r] for f in dflt[r][u][1]); print('distinct fingerprints in default runs:',len(fps), sorted(map(str,fps))[:8])
