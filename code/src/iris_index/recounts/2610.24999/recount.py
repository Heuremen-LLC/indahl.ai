import json, sys, numpy as np
C=sys.argv[1]
def load(n):
    R={}
    for l in open(f'{C}/{n}.jsonl'):
        r=json.loads(l); t={x['code'] for x in (r.get('techniques') or [])}; R[r['idx']]=(t,{c.split('.T')[0] for c in t})
    return R
runs={n:load(n) for n in ('b1a','b1b','b4','b8')}; ids=sorted(set.intersection(*[set(v) for v in runs.values()]))
def counts(a,b,k):
    A,B=runs[a],runs[b]; return np.array([[len(A[i][k]&B[i][k]),len(A[i][k]-B[i][k]),len(B[i][k]-A[i][k])] for i in ids],float)
def mf1(c): tp,fp,fn=c.sum(0); return 2*tp/(2*tp+fp+fn)
for k,lab in ((0,'technique'),(1,'class')):
    for a,b in (('b1a','b1b'),('b4','b1a'),('b4','b1b'),('b8','b1a'),('b8','b1b')): print(f'{lab:9s} {b} vs {a}: micro-F1 {mf1(counts(a,b,k)):.3f}')
rng=np.random.default_rng(20261025); idx=rng.integers(0,len(ids),(20000,len(ids)))
for k,lab in ((0,'technique'),(1,'class')):
    base=counts('b1a','b1b',k)
    for bt in ('b4','b8'):
        ca,cb=counts(bt,'b1a',k),counts(bt,'b1b',k)
        def vf(c): s=c[idx].sum(1); return 2*s[:,0]/(2*s[:,0]+s[:,1]+s[:,2])
        d=(vf(ca)+vf(cb))/2-vf(base); pt=(mf1(ca)+mf1(cb))/2-mf1(base); lo,hi=np.percentile(d,[2.5,97.5])
        print(f'B {lab:9s} {bt} vs b1 minus b1a-b1b floor: {pt:+.3f} [{lo:+.3f}, {hi:+.3f}] {"ABOVE" if lo>0 else "BELOW" if hi<0 else "CONSISTENT"}')
print('records',len(ids))
