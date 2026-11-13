import sys, json, re, random
sys.path.insert(0, '/Users/heuremen/bones-forge/triangulation/triangle'); import triangle as T
D='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_iris_yorke/x/llm-judge-release-main/data/'
ARMS={'gpt-4.1':'full_factorial/C1F1D1.jsonl','claude-sonnet-4.5':'L1_swap/C1F1D1.jsonl','gemini-2.5-flash':'L1_swap_v2_flash_16k/C1F1D1.jsonl',
      'gemini-2.5-pro':'L1_swap_v2/C1F1D1.jsonl','gpt-4.1-oct-run1':'october_rerun/run1/C1F1D1.jsonl','gpt-4.1-oct-run2':'october_rerun/run2/C1F1D1.jsonl'}
def frames(t): return [h for h in T.exor_scan(t) if h[3]]
out={}; samples={}
for arm,f in ARMS.items():
    per={}; fl=[]
    for l in open(D+f):
        r=json.loads(l); fr=0; w=0
        for k in ('round1','round2'):
            t=r[k].get('raw') or ''; h=frames(t); fr+=len(h); w+=len(t.split())
            fl+=[(r["uid"],k,x[0],x[2][:220]) for x in h]
        per[r['uid']]=(fr,w,int(fr>0))
    out[arm]=per; samples[arm]=fl
P={}; 
for l in open(D+'preprocessed_pairs.jsonl'):
    r=json.loads(l)
    for arm,key in (('human-prompt','prompt'),('gpt-4.1-mini-answer','candidate_response'),('o3-mini-answer','baseline_response')):
        t=r[key] or ''; h=frames(t); out.setdefault(arm,{})[r['uid']]=(len(h),len(t.split()),int(len(h)>0)); samples.setdefault(arm,[]).extend((r["uid"],key,x[0],x[2][:220]) for x in h)
json.dump(out,open('counts.json','w')); json.dump(samples,open('samples_all.json','w'))
rng=random.Random(20261025); pick={a:rng.sample(s,min(20,len(s))) for a,s in samples.items()}
json.dump(pick,open('precision_sample.json','w'),indent=1)
print('scanned; counts written unread. sample sizes:',{a:len(v) for a,v in pick.items()})
