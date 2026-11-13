# R3: mode A (detailed feedback) vs B (pass/fail) on passing, unit = student x problem, problems 4-9, class days only.
# Our code: logistic regression with problem fixed effects by IRLS (independence working correlation) + student-cluster bootstrap.
# Their printed: exchangeable GEE OR 4.61 (system), 1.45 (re-grader), 1.39 (human). Ours is the independence estimator: labelled.
import csv,sys,re,collections,random,numpy as np
D=sys.argv[1]+'/data/'; random.seed(20261025)
rd=lambda f:list(csv.DictReader(open(D+f,encoding='utf-8-sig')))
codes={r['answer_id']:r for r in rd('human_codes_distinct_answers.csv')}
rj={r['serno']:r['rejudge_pass_majority']=='True' for r in rd('rejudge_batch2_single_seed.csv')}
PASS=re.compile(r'\[可不修改\]|\[通過\]')
U=collections.defaultdict(lambda:dict(sys=0,rg=0,hum=0,nA=0,n=0))
for s in rd('submissions.csv'):
    p=int(s['problem']); m=s['mode']; d=s['timestamp'][:10]
    if not(4<=p<=9) or not m: continue
    if not((p<=6 and d=='2026-04-02') or (p>=7 and d=='2026-04-09')): continue
    c=codes.get(s['answer_id']); u=U[(s['student'],p)]
    u['sys']|=bool(PASS.search(s['label_as_run'])); u['rg']|=rj.get(s['serno'],False)
    u['hum']|=bool(c and c['ok']=='1'); u['n']+=1; u['nA']+=(m=='A')
units=[(k[0],k[1],int(v['nA']/v['n']>=0.5),v['sys'],v['rg'],v['hum']) for k,v in U.items()]
print('units',len(units),'students',len({u[0] for u in units}))
probs=sorted({u[1] for u in units})
def fit(rows,yi):
    X=np.array([[1,r[2]]+[int(r[1]==q) for q in probs[1:]] for r in rows],float); y=np.array([r[yi] for r in rows],float)
    b=np.zeros(X.shape[1])
    for _ in range(50):
        mu=1/(1+np.exp(-X@b)); W=mu*(1-mu)+1e-9
        b=b+np.linalg.solve(X.T@(X*W[:,None])+1e-8*np.eye(len(b)),X.T@(y-mu))
    return np.exp(b[1])
by=collections.defaultdict(list); [by[u[0]].append(u) for u in units]; S=list(by)
for yi,lab in [(3,'system pass rate'),(4,'uniform re-grader'),(5,'human strict')]:
    A=[u[yi] for u in units if u[2]]; B=[u[yi] for u in units if not u[2]]
    est=fit(units,yi); bs=[]
    for _ in range(2000):
        rows=[u for s in random.choices(S,k=len(S)) for u in by[s]]
        try: bs.append(fit(rows,yi))
        except Exception: pass
    bs.sort(); lo,hi=bs[int(.025*len(bs))],bs[int(.975*len(bs))-1]
    oc='ABOVE' if lo>1 else 'BELOW' if hi<1 else 'CONSISTENT'
    print(f'{lab:18s} A={np.mean(A):.2f} B={np.mean(B):.2f} OR {est:.2f} [{lo:.2f}, {hi:.2f}] (cluster bootstrap, {len(bs)} draws) -> {oc}')
