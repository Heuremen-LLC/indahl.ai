"""Run ONCE after the checkpoint is chosen on dev. Reads gold test for the first time. Paired test STAN vs base, keep decision, stratified dev score, public rows."""
import json,os,time
from common import *; from score import *
G=gold(); cfg=json.load(open(S+'/teachers/config.json'))['teachers']
if os.path.exists(S+'/results/paired_test.json'): raise SystemExit('paired test already read once; refusing to read gold test again')
Vb=agree_vec(jl_read(S+'/runs/base_test.jsonl'),G,'test'); Vs=agree_vec(jl_read(S+'/runs/stan_test.jsonl'),G,'test')
P=paired(Vs,Vb); keep=P['pooled']['ci95'][0]>0
res={'split':'test','n_items':P['pooled']['n'],'base':{'per_code':table(Vb,G,'test'),'pooled':pooled_rate(Vb)},'stan':{'per_code':table(Vs,G,'test'),'pooled':pooled_rate(Vs)},
 'paired_stan_minus_base':P,'keep_rule':'pooled mean difference over F1-F7, paired bootstrap 2000 resamples over items, seed 7, 95% percentile interval; keep iff the whole interval is above 0',
 'band_reading':'ABOVE' if keep else ('BELOW' if P['pooled']['ci95'][1]<0 else 'CANNOT_TELL STRADDLES_EDGE'),'kept':keep}
json.dump(res,open(S+'/results/paired_test.json','w'),indent=1)
# stratified dev: STAN agreement with gold where teachers unanimous vs split (dev only)
R={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round1.jsonl'%n) if r['set']=='gold'} for n in cfg}
Vd=agree_vec(jl_read(S+'/runs/stan_dev.jsonl'),G,'dev'); st={'unanimous':[0,0],'split':[0,0]}; by={c:{'unanimous':[0,0],'split':[0,0]} for c in CODES}
for c in CODES:
    for i,x in Vd[c].items():
        if not all(i in R[n] for n in cfg): continue
        k='unanimous' if len({key(R[n][i]['labels'][c]) for n in cfg})==1 else 'split'
        st[k][0]+=x[0]; st[k][1]+=1; by[c][k][0]+=x[0]; by[c][k][1]+=1
strat={k:{'agree':a,'n':n,'rate':round(a/n,3) if n else None,'wilson95':wilson(a,n)} for k,(a,n) in st.items()}
json.dump({'stan_on_gold_dev_by_teacher_agreement':strat,'by_code':{c:{k:{'agree':a,'n':n,'wilson95':wilson(a,n)} for k,(a,n) in by[c].items()} for c in CODES}},open(S+'/results/stan_dev_stratified.json','w'),indent=1)
# public rows, format of sage_v_public/results
ts=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()); pb=P['pooled']
os.makedirs(S+'/results/public_rows',exist_ok=True)
open(S+'/results/public_rows/paired.jsonl','w').write(json.dumps({'agreement':[res['base']['pooled']['rate'],res['stan']['pooled']['rate'],pb['ci95'][0],pb['ci95'][1]],'n':pb['n'],'seat':'stan:v1','ts':ts},sort_keys=True)+'\n')
ev=[('harvest finished',{'training_rows':int(json.load(open(S+'/results/silver_summary.json'))['train_rows'])}),('SFT finished',{}),('paired eval read',{}),('champion kept' if keep else 'rolled back after the paired eval',{})]
open(S+'/results/public_rows/events.jsonl','w').write(''.join(json.dumps(dict({'event':e,'seat':'stan:v1','ts':ts},**x),sort_keys=True)+'\n' for e,x in ev))
print(json.dumps({k:res[k] for k in ('n_items','band_reading','kept')}),json.dumps(P['pooled']),json.dumps(strat))
