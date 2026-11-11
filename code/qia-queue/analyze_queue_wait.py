"""Note 1 analysis (PLAN.md): pending count vs our jobs' wait. Rule as committed; run-level read per Note 2.
Schema: history.jsonl {backend,pending,operational,outcome,t}; jobs.jsonl {id,backend,created,wait_s}. wait_s = created -> running (IBM job record).
Runs: jobs carry no run id, so a run = consecutive jobs on one processor with gaps <= RUN_GAP_MIN minutes (assumption, stated in ANALYSIS.md)."""
import json, bisect, datetime as dt, collections
import numpy as np
from scipy.stats import spearmanr, rankdata
D='data/'; MAXAGE=90*60; MINJ=20; NB=4000; SEED=7; RUN_GAP_MIN=30
P=lambda s: dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
hist=collections.defaultdict(list)
for l in open(D+'history.jsonl'):
    r=json.loads(l)
    if r.get('outcome')=='COMMITTED' and isinstance(r.get('pending'),int) and r['backend']!='all': hist[r['backend']].append((P(r['t']),r['pending']))
for v in hist.values(): v.sort()
jobs=[json.loads(l) for l in open(D+'jobs.jsonl') if l.strip()]
byb=collections.defaultdict(list); dropped=collections.Counter(); total=collections.Counter()
for j in jobs:
    b=j['backend']; total[b]+=1; c=P(j['created']); h=hist.get(b,[]); i=bisect.bisect_left([x[0] for x in h],c)-1 if h else -1
    if i<0 or c-h[i][0]>MAXAGE: dropped[b]+=1; continue
    byb[b].append((c,h[i][1],j['wait_s']))
def rho(x,y):
    if len(set(x))<2 or len(set(y))<2: return np.nan
    return spearmanr(x,y)[0]
def ci(vals): 
    v=np.array([a for a in vals if not np.isnan(a)]); return (float(np.percentile(v,2.5)),float(np.percentile(v,97.5)),len(v)) if len(v) else (None,None,0)
def outcome(lo,hi,span,n):
    if n<MINJ or lo is None or span<3: return 'CANNOT_TELL'
    if lo>0.3: return 'ABOVE'
    if hi<0: return 'BELOW'
    if lo>=-0.3 and hi<=0.3: return 'CONSISTENT'
    return 'CANNOT_TELL'
out={}
for b in sorted(total):
    rows=sorted(byb.get(b,[])); n=len(rows); res=dict(joined=n,dropped=dropped[b],total=total[b])
    if n:
        c=np.array([r[0] for r in rows]); x=np.array([r[1] for r in rows],float); y=np.array([r[2] for r in rows])
        rid=np.concatenate([[0],np.cumsum(np.diff(c)>RUN_GAP_MIN*60)]); nr=int(rid.max()+1)
        span=float(x.max()/max(x.min(),1)); res.update(runs=nr,pending_min=int(x.min()),pending_max=int(x.max()),span=span,rho=None if np.isnan(rho(x,y)) else float(rho(x,y)))
    else: res.update(runs=0,rho=None,span=0)
    if n>=MINJ:
        rng=np.random.default_rng(SEED); bs=[]
        for _ in range(NB):
            k=rng.integers(0,n,n); bs.append(rho(x[k],y[k]))
        jl=ci(bs); res['job_ci']=jl[:2]
        rng=np.random.default_rng(SEED); groups=[np.where(rid==g)[0] for g in range(nr)]; bs=[]
        for _ in range(NB):
            k=np.concatenate([groups[g] for g in rng.integers(0,nr,nr)]); bs.append(rho(x[k],y[k]))
        rl=ci(bs); res['run_ci']=rl[:2]
        res['job_outcome']=outcome(jl[0],jl[1],span,n); res['outcome']=outcome(rl[0],rl[1],span,n)
        res['undefined_resamples']=dict(job=NB-jl[2],run=NB-rl[2])
    else: res['job_ci']=res['run_ci']=None; res['outcome']='CANNOT_TELL'; res['job_outcome']='CANNOT_TELL'
    out[b]=res
meta=dict(rule='PLAN.md Note 1 + Note 2',min_joined=MINJ,max_age_min=90,bootstrap=NB,seed=SEED,run_gap_min=RUN_GAP_MIN,history_first=min(min(t for t,_ in v) for v in hist.values()),history_last=max(max(t for t,_ in v) for v in hist.values()),jobs_total=len(jobs),jobs_joined=sum(r['joined'] for r in out.values()),jobs_dropped=sum(dropped.values()))
json.dump(dict(meta=meta,processors=out),open('analysis.json','w'),indent=1)
f=lambda v: '-' if v is None else '[%.2f, %.2f]'%tuple(v)
print('processor joined dropped runs rho job_ci run_ci outcome (job-level outcome)')
for b,r in out.items(): print(b,r['joined'],r['dropped'],r['runs'],'-' if r['rho'] is None else '%.2f'%r['rho'],f(r['job_ci']),f(r['run_ci']),r['outcome'],'(job:%s)'%r['job_outcome'],'span=%.1f'%r['span'],r.get('pending_min'),r.get('pending_max'))
print(meta['jobs_joined'],meta['jobs_dropped'])

# Sensitivity added after the first reading (30 min gap was chosen at analysis time; plan defines no run)
sens={}
for b in sorted(total):
    rows=sorted(byb.get(b,[])); n=len(rows); sens[b]={}
    if n<MINJ: continue
    c=np.array([r[0] for r in rows]); x=np.array([r[1] for r in rows],float); y=np.array([r[2] for r in rows]); span=float(x.max()/max(x.min(),1))
    for g in (10,30,60,120,240):
        rid=np.concatenate([[0],np.cumsum(np.diff(c)>g*60)]); nr=int(rid.max()+1); groups=[np.where(rid==k)[0] for k in range(nr)]
        rng=np.random.default_rng(SEED); bs=[]
        for _ in range(NB):
            k=np.concatenate([groups[q] for q in rng.integers(0,nr,nr)]); bs.append(rho(x[k],y[k]))
        lo,hi,_=ci(bs); sens[b][g]=dict(runs=nr,run_ci=[lo,hi],outcome=outcome(lo,hi,span,n))
d=json.load(open('analysis.json')); d['sensitivity_added_after_first_reading']=sens; json.dump(d,open('analysis.json','w'),indent=1)
print('processor gap runs run_ci outcome')
for b,v in sens.items():
    for g,r in v.items(): print(b,g,r['runs'],'[%.2f, %.2f]'%tuple(r['run_ci']),r['outcome'])
    print(b,'CHANGES' if len({r['outcome'] for r in v.values()})>1 else 'stable')
L=['','## Sensitivity to the run gap (added after the first reading)','The plan defines no run. The 30 minute gap above was chosen at analysis time. Run-level interval and outcome at other gaps:','','| processor | gap min | runs | run-level 95% | outcome |','|---|---|---|---|---|']
for b,v in sens.items():
    for g,r in v.items(): L.append('| %s | %d | %d | [%.2f, %.2f] | %s |'%(b,g,r['runs'],*r['run_ci'],r['outcome']))
ch=[b for b,v in sens.items() if len({r['outcome'] for r in v.values()})>1]
L+=['','Processors whose outcome changes across gaps: '+(', '.join(ch) or 'none')+'.']
open('ANALYSIS.md','a').write('\n'.join(L)+'\n')
