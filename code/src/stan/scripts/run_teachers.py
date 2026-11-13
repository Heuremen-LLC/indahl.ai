import gate; gate.check()
import json,sys,time,os,concurrent.futures as cf
from common import *
name=sys.argv[1]; T=json.load(open(S+'/teachers/config.json'))['teachers'][name]
items=[]
SL=int(sys.argv[2]) if len(sys.argv)>2 else 1
P=json.load(open(S+'/data/pool.json'))[:100] if SL==1 else json.load(open(S+'/data/slices/slice_%02d.json'%SL))   # Amendment 2: first slice is the first 100 of the seeded pool
for g in P: items.append(('pool',g['id'],g['text']))
for g in (json.load(open(S+'/data/gold_items.json')) if SL==1 else []):
    if g.get('text') and g['split']=='dev': items.append(('gold',g['id'],g['text']))   # pre-registered: teachers see gold dev only
unload_others(T['host'],T['model'])
out=S+'/teachers/%s_round1.jsonl'%name
done={(r['set'],r['id']) for r in jl_read(out)}
todo=[x for x in items if (x[0],x[1]) not in done]
print(name,len(todo),'todo',flush=True)
_n=0
def one(x):
    s,i,text=x; t=time.time()
    global _n
    _n+=1
    if _n%25==0: unload_others(T['host'],T['model'])
    try: raw=ollama(T['host'],T['model'],teacher_prompt(text))
    except Exception as e: return None
    o=parse_obj(raw); labs={}
    for c in CODES:
        labs[c]=norm_label(c,(o or {}).get(c),text)
    return {'set':s,'id':i,'raw':raw,'labels':labs,'secs':round(time.time()-t,1)}
with open(out,'a') as f, cf.ThreadPoolExecutor(1) as ex:
    for r in ex.map(one,todo):
        if r: f.write(json.dumps(r)+'\n'); f.flush()
print('done',flush=True)
