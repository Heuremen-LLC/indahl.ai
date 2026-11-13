import csv,sys,random,statistics as st,collections,math,numpy as np
R=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))); print('rows',len(R),collections.Counter(r['condition'] for r in R))
g=collections.defaultdict(list)
for r in R: g[r['condition']].append(r)
f=lambda r,k: float(r[k])
for c,rs in g.items():
    print(f"{c:12s} n {len(rs)} pre {100*st.mean(f(r,'preTest') for r in rs):.2f}% post {100*st.mean(f(r,'postTest') for r in rs):.2f}% gain {100*st.mean(f(r,'learningGain') for r in rs):.2f}%")
random.seed(20261025)
cg=[f(r,'learningGain') for r in g['ChatGPT']]; hg=[f(r,'learningGain') for r in g['Human tutor']]; kg=[f(r,'learningGain') for r in g['No-hint control']]
def diff_ci(a,b,B=10000,lvl=(2.5,97.5)):
    d=st.mean(a)-st.mean(b); bs=sorted(st.mean(random.choices(a,k=len(a)))-st.mean(random.choices(b,k=len(b))) for _ in range(B))
    return d,bs[int(lvl[0]/100*B)],bs[int(lvl[1]/100*B)-1]
pooled=math.sqrt((st.variance(cg)*(len(cg)-1)+st.variance(hg)*(len(hg)-1))/(len(cg)+len(hg)-2)); bound=0.5*pooled
d,lo,hi=diff_ci(cg,hg); d90,lo90,hi90=diff_ci(cg,hg,lvl=(5,95))
print(f'B2 ChatGPT - human gain: {100*d:+.2f} pts, 95% [{100*lo:+.2f}, {100*hi:+.2f}], 90% [{100*lo90:+.2f}, {100*hi90:+.2f}]; d=0.5 bound = +/-{100*bound:.2f} pts ->',
      'EQUIVALENT (90% CI inside bound)' if (lo90>-bound and hi90<bound) else 'NOT SHOWN EQUIVALENT')
d,lo,hi=diff_ci(hg,kg); print(f'B4 human - control gain: {100*d:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]')
d,lo,hi=diff_ci(cg,kg); print(f'    ChatGPT - control gain: {100*d:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]')
# B3 adjusted: post ~ condition + pre + lesson dummies (OLS)
les=sorted({r['lesson'] for r in R}); conds=['Human tutor','ChatGPT']
X=np.array([[1,float(r['condition']=='Human tutor'),float(r['condition']=='ChatGPT'),f(r,'preTest')]+[float(r['lesson']==l) for l in les[1:]] for r in R]); y=np.array([f(r,'postTest') for r in R])
b=np.linalg.lstsq(X,y,rcond=None)[0]; e=y-X@b; n,k=X.shape; V=np.linalg.inv(X.T@X)*(e@e/(n-k)); se=np.sqrt(np.diag(V))
print(f'B3 post adjusted for pre + lesson: human vs control {100*b[1]:+.2f} ({100*se[1]:.2f}); ChatGPT vs control {100*b[2]:+.2f} ({100*se[2]:.2f}); ChatGPT - human {100*(b[2]-b[1]):+.2f} ({100*math.sqrt(V[2,2]+V[1,1]-2*V[1,2]):.2f})')
