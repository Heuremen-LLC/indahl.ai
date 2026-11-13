"""run_matrix.py MODEL [ARM ...]: resumable; writes results/<model>/<arm>.jsonl. Our seat only (127.0.0.1:11500)."""
import json, sys, os, csv, time, urllib.request, re
H='http://127.0.0.1:11500/api/chat'; HERE=os.path.dirname(os.path.abspath(__file__))
MODEL=sys.argv[1]; ARMS=sys.argv[2:] or ['nep_abstain','nep_abstain_copy','mcq_A','mcq_A_copy','mcq_A_rev','mcq_B','mcq_batch8']
OUT=os.path.join(HERE,'results',MODEL.replace(':','_')); os.makedirs(OUT,exist_ok=True)
NEP_SYS=open(os.path.join(HERE,'inputs/nep_prompt_abstention_baseline.txt')).read()
NEP=list(csv.DictReader(open(os.path.join(HERE,'inputs/nep_gold.csv'))))
MCQ=json.load(open(os.path.join(HERE,'inputs/mcq_200.json'))); L='ABCD'
def call(system,user):
    body={'model':MODEL,'messages':([{'role':'system','content':system}] if system else [])+[{'role':'user','content':user}],
          'stream':False,'format':'json','think':False,'options':{'temperature':0,'seed':20261025,'num_ctx':4096,'num_predict':400}}
    for attempt in (1,2):
        try:
            r=json.loads(urllib.request.urlopen(urllib.request.Request(H,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'}),timeout=300).read())
            return r.get('message',{}).get('content',''), r.get('done_reason'), None
        except Exception as e:
            if 'think' in str(e) and 'think' in body: body.pop('think'); continue
            err=str(e)[:200]
    return '', None, err
def mcq_user(q,rev=False,template='A'):
    opts=list(range(len(q['options'])))[::-1] if rev else list(range(len(q['options'])))
    lines='\n'.join(f'{L[k]}. {q["options"][o]}' for k,o in enumerate(opts))
    if template=='A': u=f'Story: {q["state"]}\nQuestion: {q["question"]}\nOptions:\n{lines}\nAnswer as JSON: {{"answer": "<letter>"}}'
    else: u=f'{q["state"]}\n{q["question"]}\n{lines}\nReply with the letter only, as JSON {{"answer": "<letter>"}}.'
    return u,opts
def done_ids(path): return {json.loads(l)['id'] for l in open(path)} if os.path.exists(path) else set()
for arm in ARMS:
    path=os.path.join(OUT,arm+'.jsonl'); seen=done_ids(path); f=open(path,'a')
    if arm.startswith('nep'):
        for r in NEP:
            if r['comment_id'] in seen: continue
            txt,dr,err=call(NEP_SYS,f'Comment: {r["comment"]}\nReturn only the JSON object.')
            f.write(json.dumps(dict(id=r['comment_id'],raw=txt,done_reason=dr,error=err))+'\n'); f.flush()
    elif arm=='mcq_batch8':
        for b in range(0,len(MCQ),8):
            bid=f'batch{b//8:02d}'
            if bid in seen: continue
            qs=MCQ[b:b+8]; parts=[]
            for n,q in enumerate(qs):
                u,_=mcq_user(q); parts.append(f'### Item {n+1}\n'+u.replace('Answer as JSON: {"answer": "<letter>"}',''))
            user='\n\n'.join(parts)+'\n\nAnswer every item. Return JSON {"answers": ["<letter for item 1>", ...], "count_A": <how many of your answers in this reply are A>}.'
            txt,dr,err=call(None,user)
            f.write(json.dumps(dict(id=bid,items=[q['id'] for q in qs],raw=txt,done_reason=dr,error=err))+'\n'); f.flush()
    else:
        rev='rev' in arm; tpl='B' if arm=='mcq_B' else 'A'
        for q in MCQ:
            if q['id'] in seen: continue
            u,opts=mcq_user(q,rev,tpl); txt,dr,err=call(None,u)
            f.write(json.dumps(dict(id=q['id'],order=opts,raw=txt,done_reason=dr,error=err))+'\n'); f.flush()
    f.close(); print(MODEL,arm,'done',flush=True)
