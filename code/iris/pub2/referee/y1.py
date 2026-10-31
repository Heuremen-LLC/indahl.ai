import json,sys,collections,numpy as np
D=sys.argv[1]
exec(open('recounts/2610.30512/recount.py').read().split("ref={")[0].replace("D=sys.argv[1]","D=sys.argv[1]"))
u3=[u for u in dflt['run1'] if all(u in dflt[r] and not np.isnan(dflt[r][u][0]) for r in dflt)]
print(len(u3))
for r in ('run1','run2','run3'):
    c=collections.Counter(dflt[r][u][1] for u in u3); print(r,c.most_common(6))
    ts=sorted(dflt[r][u][2] for u in u3 if dflt[r][u][2]); print(' ts',ts[0],ts[-1])
# time structure of match: order of prompts
order=list(dflt['run1'].keys())
same=np.array([dflt['run1'][u][1]==dflt['run2'][u][1] for u in u3])
flip=np.array([np.sign(dflt['run1'][u][0])!=np.sign(dflt['run2'][u][0]) for u in u3])
# permutation test
rng=np.random.default_rng(1);obs=flip[~same].mean()-flip[same].mean()
p=np.mean([ (lambda s: flip[~s].mean()-flip[s].mean())(rng.permutation(same))>=obs for _ in range(20000)]);print('perm p',p,obs)
# position in file vs same
idx=np.arange(len(u3)); print('corr pos/same',np.corrcoef(idx,same)[0,1])
# split by position halves
h=len(u3)//2
for nm,s in (('first',slice(0,h)),('second',slice(h,None))):
    sm,fl=same[s],flip[s]; print(nm,'match',sm.sum(),fl[sm].mean(),'differ',(~sm).sum(),fl[~sm].mean())
# which fp pairs
pc=collections.Counter(); pf=collections.defaultdict(list)
for u,f in zip(u3,flip):
    k=(dflt['run1'][u][1],dflt['run2'][u][1]); pf[k].append(f)
for k,v in sorted(pf.items(),key=lambda x:-len(x[1]))[:10]: print(k,len(v),np.mean(v))
