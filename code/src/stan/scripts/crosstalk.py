import gate; gate.check()
import json,sys,concurrent.futures as cf,time
from common import *
name=sys.argv[1]; cfg=json.load(open(S+'/teachers/config.json'))['teachers']; T=cfg[name]; others=[n for n in cfg if n!=name]
pool={g['id']:g['text'] for g in all_pool()}
R1={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round1.jsonl'%n) if r['set']=='pool'} for n in cfg}
unload_others(T['host'],T['model'])
out=S+'/teachers/%s_round2.jsonl'%name; done={r['id'] for r in jl_read(out)}
def show(l):
    if l['flag']=='ungrounded': return 'status %s (its quote was not found in the text, so held as CANNOT_TELL METHOD_UNSTATED)'%l['was']
    return 'status %s%s%s'%(l['status'],(' reason '+l['reason']) if l['reason'] else '',(' quote "%s"'%l['quote']) if l['quote'] else '')
work=[]
for i,text in pool.items():
    if not all(i in R1[n] for n in cfg): continue
    dis=[c for c in CODES if len({key(R1[n][i]['labels'][c]) for n in cfg})>1]
    if dis and i not in done: work.append((i,text,dis))
print(name,len(work),'items with disagreement',flush=True)
_n=0
def one(w):
    i,text,dis=w
    p=RULES+'\n\nTwo other reviewers read the same text and labelled some codes differently. Look at their labels once and decide for yourself. You may keep your label or revise it. Quotes must be word for word from the text.\n\nCODES\n\n'+'\n\n'.join(code_block(c) for c in dis)+'\n\nTEXT\n'+text+'\n\nLABELS\n'
    for c in dis:
        p+='\n%s: your first label was %s\n'%(c,show(R1[name][i]['labels'][c]))
        for n in others: p+='  reviewer %s: %s\n'%(n,show(R1[n][i]['labels'][c]))
    p+='\nAnswer with one JSON object only, with a key for each of these codes ('+', '.join(dis)+'), each in the form {"status": "...", "reason": "...", "quote": "..."}.'
    global _n
    _n+=1
    if _n%25==0: unload_others(T['host'],T['model'])
    try: raw=ollama(T['host'],T['model'],p)
    except Exception: return None
    o=parse_obj(raw) or {}
    return {'id':i,'codes':dis,'raw':raw,'labels':{c:norm_label(c,o.get(c),text) for c in dis}}
with open(out,'a') as f, cf.ThreadPoolExecutor(1) as ex:
    for r in ex.map(one,work):
        if r: f.write(json.dumps(r)+'\n'); f.flush()
print('done',flush=True)
