import csv,sys,collections,numpy as np
D=sys.argv[1]; rows=[r for r in csv.DictReader(open(D,encoding='utf-8-sig'))]
print('rows',len(rows),'honors rows',sum(r['Honors']=='1' for r in rows))
def build(rs):
    rs=[r for r in rs if r['gpa_prev'] not in ('','NA') and r['Part2Tot'] not in ('','NA') and r['Part3Tot'] not in ('','NA')]
    fe=[]
    for k in ['teacher','Session','Grader','Year']:
        lv=sorted({r[k] for r in rs}); fe+= [(k,v) for v in lv[1:]]
    X=np.array([[1,float(r['GPTBase']),float(r['GPTTutor']),float(r['gpa_prev'])]+[float(r[k]==v) for k,v in fe] for r in rs])
    return rs,X
def ols(X,y,cl):
    XtX=np.linalg.pinv(X.T@X); b=XtX@X.T@y; e=y-X@b
    G=sorted(set(cl)); idx={g:[i for i,c in enumerate(cl) if c==g] for g in G}
    meat=sum(np.outer(X[ii].T@e[ii],X[ii].T@e[ii]) for ii in idx.values())
    n,k=X.shape; c=len(G)/(len(G)-1)*(n-1)/(n-k)
    V=c*XtX@meat@XtX; return b,np.sqrt(np.diag(V)),e,idx
def wild(X,y,cl,j,B=9999,seed=20261025):
    b,se,_,idx=ols(X,y,cl); t0=b[j]/se[j]
    Xr=np.delete(X,j,1); br=np.linalg.pinv(Xr.T@Xr)@Xr.T@y; fr=Xr@br; er=y-fr
    rng=np.random.default_rng(seed); G=list(idx); cnt=0
    for _ in range(B):
        w=rng.choice([-1,1],len(G)); ys=fr.copy()
        for g,wg in zip(G,w): ys[idx[g]]+=wg*er[idx[g]]
        bs,ses,_,_=ols(X,ys,cl); cnt+=abs(bs[j]/ses[j])>=abs(t0)
    return t0,(cnt+1)/(B+1)
for label,rs0 in [('main (honors excluded)',[r for r in rows if r['Honors']=='0']),('honors included (post-hoc)',rows)]:
    rs,X=build(rs0); cl=[r['Class'] for r in rs]
    arms=collections.defaultdict(set); [arms[r['Class']].add(r['Treatment arm']) for r in rs]
    print('==',label,'obs',len(rs),'students',len({r['Student ID'] for r in rs}),'classes',len(set(cl)),'arms per class',collections.Counter(len(a) for a in arms.values()),
          'classes per arm',collections.Counter(next(iter(a)) for a in arms.values() if len(a)==1))
    for ycol,name in [('Part2Tot','practice'),('Part3Tot','exam')]:
        y=np.array([float(r[ycol]) for r in rs]); b,se,_,_=ols(X,y,cl)
        cm=np.mean([float(r[ycol]) for r in rs if r['Treatment arm']=='control'])
        print(f'  {name}: GPTBase {b[1]:+.3f} ({se[1]:.3f})  GPTTutor {b[2]:+.3f} ({se[2]:.3f})  control mean {cm:.3f}  Base/mean {100*b[1]/cm:+.0f}%  Tutor/mean {100*b[2]/cm:+.0f}%')
        if ycol=='Part3Tot' and 'main' in label:
            t,p=wild(X,y,cl,1,B=1999); print(f'    wild cluster bootstrap (Rademacher, restricted, 1,999 draws) GPTBase exam: t={t:.2f}, p={p:.3f}')
# ---- added (labelled, after the first output): known-good for the wild bootstrap + randomization inference
if '--ri' in sys.argv:
    rs,X=build([r for r in rows if r['Honors']=='0']); cl=[r['Class'] for r in rs]
    y2=np.array([float(r['Part2Tot']) for r in rs]); y3=np.array([float(r['Part3Tot']) for r in rs])
    t,p=wild(X,y2,cl,1,B=999); print(f'known-good: wild bootstrap on PRACTICE GPTBase t={t:.2f} p={p:.3f} (should be small)')
    cls=sorted(set(cl)); arm={r['Class']:r['Treatment arm'] for r in rs}; yr={r['Class']:r['Year'] for r in rs}
    b0,_,_,_=ols(X,y3,cl); obs=b0[1]; rng=np.random.default_rng(20261025); cnt=0; B=2000
    for _ in range(B):
        perm={}
        for g in sorted(set(yr.values())):
            cs=[c for c in cls if yr[c]==g]; labs=[arm[c] for c in cs]; rng.shuffle(labs); perm.update(dict(zip(cs,labs)))
        Xp=X.copy(); Xp[:,1]=[float(perm[c]=='vanilla') for c in cl]; Xp[:,2]=[float(perm[c]=='augmented') for c in cl]
        bp=np.linalg.pinv(Xp.T@Xp)@Xp.T@y3; cnt+=abs(bp[1])>=abs(obs)
    print(f'randomization inference (arm labels permuted across classes within grade, {B} draws): GPTBase exam {obs:+.3f}, p={(cnt+1)/(B+1):.3f}')
    print('arm-label check: vanilla<->GPTBase?', all((r['Treatment arm']=='vanilla')==(r['GPTBase']=='1') for r in rs))
