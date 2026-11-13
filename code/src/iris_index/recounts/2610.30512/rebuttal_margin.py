# DEFINED AFTER THE DATA: tests the rebuttal "prompts whose backend changed were closer to the boundary".
import json,sys,numpy as np
sys.argv=[sys.argv[0],sys.argv[1]]; exec(open('recount.py').read().split("ref={")[0])  # reuse loaders only
u3=[u for u in dflt['run1'] if all(u in dflt[r] and not np.isnan(dflt[r][u][0]) for r in dflt)]
rows=[(abs(dflt['run3'][u][0]), dflt['run1'][u][1]==dflt['run2'][u][1], np.sign(dflt['run1'][u][0])!=np.sign(dflt['run2'][u][0]), dflt['run1'][u][1], dflt['run2'][u][1]) for u in u3]
m=np.array([r[0] for r in rows]); same=np.array([r[1] for r in rows]); flip=np.array([r[2] for r in rows],float)
print('mean |margin| run3: match %.3f  differ %.3f'%(m[same].mean(), m[~same].mean()))
w=[];tot=0
for b in sorted(set(m)):
    s=(m==b)
    a,d=flip[s&same],flip[s&~same]
    print(' margin %.1f: match n=%3d flip %5.1f%% | differ n=%3d flip %5.1f%%'%(b,len(a),100*a.mean() if len(a) else np.nan,len(d),100*d.mean() if len(d) else np.nan))
    if len(a) and len(d): w.append((len(a)*len(d)/(len(a)+len(d)), d.mean()-a.mean()))
est=sum(x*y for x,y in w)/sum(x for x,_ in w)
rng=np.random.default_rng(20261025); bs=[]
for _ in range(20000):
    i=rng.integers(0,len(m),len(m)); mm,ss,ff=m[i],same[i],flip[i]; ww=[]
    for b in set(mm):
        s=mm==b; a,d=ff[s&ss],ff[s&~ss]
        if len(a) and len(d): ww.append((len(a)*len(d)/(len(a)+len(d)),d.mean()-a.mean()))
    bs.append(sum(x*y for x,y in ww)/sum(x for x,_ in ww))
lo,hi=np.percentile(bs,[2.5,97.5]); print('margin-stratified diff %+.1f pp [%+.1f, %+.1f] -> %s'%(100*est,100*lo,100*hi,'ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'))
# which rounds changed backend
r1=sum(1 for r in rows if r[3][0]!=r[4][0]); r2=sum(1 for r in rows if r[3][1]!=r[4][1]); print('round1 backend changed on %d prompts, round2 on %d'%(r1,r2))
from collections import Counter; print('run1 fps',Counter(f for r in rows for f in r[3]).most_common(4)); print('run2 fps',Counter(f for r in rows for f in r[4]).most_common(4))
