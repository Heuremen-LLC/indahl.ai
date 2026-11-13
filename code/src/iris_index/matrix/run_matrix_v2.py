"""run_matrix_v2.py MODEL: resumable; results_v2/<model>/<arm>.jsonl. Our seat only. No server JSON mode (addendum v2-1)."""
import json, sys, os, urllib.request
H='http://127.0.0.1:11500/api/chat'; HERE=os.path.dirname(os.path.abspath(__file__)); MODEL=sys.argv[1]
OUT=os.path.join(HERE,'results_v2',MODEL.replace(':','_')); os.makedirs(OUT,exist_ok=True)
M4=json.load(open(os.path.join(HERE,'inputs/mcq4_200.json'))); PC=json.load(open(os.path.join(HERE,'inputs/mcq4_poscontrol.json'))); L='ABCD'
def call(user):
    body={'model':MODEL,'messages':[{'role':'user','content':user}],'stream':False,'think':False,
          'options':{'temperature':0,'seed':20261025,'num_ctx':4096,'num_predict':500}}
    for _ in (1,2):
        try:
            r=json.loads(urllib.request.urlopen(urllib.request.Request(H,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'}),timeout=300).read())
            return r.get('message',{}).get('content',''), r.get('done_reason'), None
        except Exception as e:
            if 'think' in str(e) and 'think' in body: body.pop('think'); continue
            return '', None, str(e)[:200]
    return '', None, 'retry exhausted'
def order(n,kind): return list(range(n))[::-1] if kind=='rev' else (list(range(1,n))+[0] if kind=='rot' else list(range(n)))
def user(q,kind='id',tpl='A'):
    o=order(len(q['options']),kind); lines='\n'.join(f'{L[k]}. {q["options"][i]}' for k,i in enumerate(o))
    if tpl=='A': return f'Story: {q["state"]}\nQuestion: {q["question"]}\nOptions:\n{lines}\nAnswer as JSON: {{"answer": "<letter>"}}',o
    return f'{q["state"]}\n{q["question"]}\n{lines}\nReply with the letter only, as JSON {{"answer": "<letter>"}}.',o
def seen(p): return {json.loads(l)['id'] for l in open(p)} if os.path.exists(p) else set()
ARMS=[('mcq4_A',M4,'id','A'),('mcq4_A_copy',M4,'id','A'),('mcq4_rev',M4,'rev','A'),('mcq4_rot',M4,'rot','A'),('mcq4_B',M4,'id','B'),('pc_A',PC,'id','A'),('pc_rev',PC,'rev','A')]
for arm,Q,kind,tpl in ARMS:
    p=os.path.join(OUT,arm+'.jsonl'); s=seen(p); f=open(p,'a')
    for q in Q:
        if q['id'] in s: continue
        u,o=user(q,kind,tpl); txt,dr,err=call(u); f.write(json.dumps(dict(id=q['id'],order=o,raw=txt,done_reason=dr,error=err))+'\n'); f.flush()
    f.close(); print(MODEL,arm,'done',flush=True)
p=os.path.join(OUT,'mcq4_batch8.jsonl'); s=seen(p); f=open(p,'a')
for b in range(0,len(M4),8):
    bid=f'batch{b//8:02d}'
    if bid in s: continue
    qs=M4[b:b+8]; parts=[f'### Question {n+1} of {len(qs)}\n'+user(q)[0].replace('\nAnswer as JSON: {"answer": "<letter>"}','') for n,q in enumerate(qs)]
    u='\n\n'.join(parts)+f'\n\nThere are exactly {len(qs)} questions. Return JSON {{"answers": [exactly {len(qs)} letters, one per question in order], "count_A": <how many of your {len(qs)} answers are A>}}.'
    txt,dr,err=call(u); f.write(json.dumps(dict(id=bid,items=[q['id'] for q in qs],raw=txt,done_reason=dr,error=err))+'\n'); f.flush()
f.close(); print(MODEL,'mcq4_batch8 done',flush=True)
