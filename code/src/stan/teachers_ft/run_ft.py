import sys,json,time,os,urllib.request
sys.path.insert(0,'/Users/heuremen/bones-forge/stan/scripts')
from common import code_block,ws,parse_obj,ALL_REASONS,S
D=S+'/teachers_ft'; CODES=['F1','F2','F6','F3']
T=json.load(open(S+'/teachers/config.json'))['teachers']
ret=json.load(open(S+'/ceiling_ft/retrieval.json')); ch=json.load(open(S+'/ceiling_ft/chunks.json'))
gold={x['id']:x for x in json.load(open(S+'/data/gold_items.json'))}
tpl=open(D+'/prompt_template.txt').read()
HEAD=tpl.split('CODE\n\n')[0]; TAIL='Answer with one JSON object only'+tpl.split('Answer with one JSON object only')[1]
def prompt(pid,code):
    cm={c['id']:c['text'] for c in ch[pid]}
    body='\n\n'.join('[%s]\n%s'%(r['chunk'],cm[r['chunk']]) for r in ret[pid][code])
    return HEAD+'CODE\n\n'+code_block(code)+'\n\nCHUNKS\n\n'+body+'\n\n'+TAIL.rstrip('\n')
def call(host,model,p):
    b={'model':model,'messages':[{'role':'user','content':p}],'stream':False,'think':False,'format':'json',
       'options':{'temperature':0,'seed':0,'num_predict':500,'num_ctx':12288},'keep_alive':'30m'}
    r=json.load(urllib.request.urlopen(urllib.request.Request(host+'/api/chat',json.dumps(b).encode(),{'Content-Type':'application/json'}),timeout=900))
    return r['message']['content'],r.get('prompt_eval_count')
def ground(o,pid,code):
    if not isinstance(o,dict): return 'parse_failed'
    q=ws(str(o.get('quote') or '')); st=str(o.get('status','')).upper()
    if st not in ('PRESENT','ABSENT','CANNOT_TELL','NOT_APPLICABLE'): return 'parse_failed'
    if st in('CANNOT_TELL','NOT_APPLICABLE'): return 'n/a'
    if not q: return 'not_found'
    cm={c['id']:ws(c['text']) for c in ch[pid]}; named=o.get('chunk_id')
    if named in cm and q in cm[named] and named in [r['chunk'] for r in ret[pid][code]]: return 'named_chunk'
    if any(q in cm[r['chunk']] for r in ret[pid][code]): return 'other_retrieved_chunk'
    return 'not_found'
if __name__=='__main__':
    name=sys.argv[1]; t=dict(T[name]); t['host']=os.environ.get('TEACHER_HOST',t['host']); out=D+('/outputs_%s.jsonl'%os.environ['OUT_TAG'] if os.environ.get('OUT_TAG') else '/outputs.jsonl')   # 12 Nov: Mac runs llama and gemma in parallel (same Ollama blobs, checked by digest), each to its own file
    done=set()
    if os.path.exists(out):
        for l in open(out):
            r=json.loads(l); done.add((r['teacher'],r['id'],r['code']))
    for pid in sorted(ret):
        assert gold[pid]['split']=='dev'
        for code in CODES:
            if (name,pid,code) in done: continue
            p=prompt(pid,code); t0=time.time()
            try: raw,n=call(t['host'],t['model'],p); err=None
            except Exception as e: raw,n,err='',None,str(e)[:200]
            o=parse_obj(raw)
            rec={'teacher':name,'id':pid,'code':code,'raw':raw,'parsed':o,'status':str(o.get('status','')).upper() if isinstance(o,dict) else 'PARSE_FAILED',
                 'reason':str(o.get('reason') or '').upper() if isinstance(o,dict) else '','grounding':ground(o,pid,code),'prompt_tokens':n,'secs':round(time.time()-t0,1),'error':err,'host':t['host']}
            open(out,'a').write(json.dumps(rec)+'\n')
