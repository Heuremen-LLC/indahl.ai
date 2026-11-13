"""STAN-E: local-model errata drafter (12 Nov 2026). For each SAGAR paper text, split into ~6000-character chunks and ask a local
model to list internal numeric contradictions inside the chunk. Output is a candidate list, scored later against Bones-verified SAGAR
rows (sagar/index/verified.jsonl). Resumable. Usage: HOST=http://... MODEL=... OUT=name python3 errata_drafter.py"""
import json,os,re,sys,time,urllib.request
S='/Users/heuremen/bones-forge/sagar/index'; D='/Users/heuremen/bones-forge/stan/errata'
HOST=os.environ['HOST']; MODEL=os.environ['MODEL']; OUT=D+'/out_%s.jsonl'%os.environ['OUT']
papers=[]
for f in sorted(os.listdir(S)):
    if re.match(r'(batch_\d+|control_\d+)_draft\.jsonl$',f):
        papers+=[json.loads(l)['arxiv'] for l in open(S+'/'+f)]
papers=[p for p in dict.fromkeys(papers) if os.path.exists(S+'/text/%s.txt'%p)]
done=set()
if os.path.exists(OUT):
    for l in open(OUT): r=json.loads(l); done.add((r['arxiv'],r['chunk']))
P=("You check a physics paper excerpt for internal numeric errors. List only cases where two statements in THIS excerpt cannot both be "
"right: a number in the text that differs from the same quantity in a table or caption in the excerpt; a percentage that does not equal "
"count/total from printed numbers; components that do not sum to a printed total; a probability or ratio that does not follow from printed "
"inputs. Do the arithmetic. Ignore rounding differences in the last printed digit. Do not report style, wording or physics opinions. "
"Answer with JSON only: {\"errors\": [{\"quote_a\": \"verbatim text\", \"quote_b\": \"verbatim text\", \"arithmetic\": \"...\", \"why\": \"...\"}]} "
"and {\"errors\": []} if none.\n\nEXCERPT:\n")
def call(text):
    b={'model':MODEL,'messages':[{'role':'user','content':P+text}],'stream':False,'think':False,'format':'json',
       'options':{'temperature':0,'seed':0,'num_predict':700,'num_ctx':8192},'keep_alive':'30m'}
    r=json.load(urllib.request.urlopen(urllib.request.Request(HOST+'/api/chat',json.dumps(b).encode(),{'Content-Type':'application/json'}),timeout=900))
    return r['message']['content']
for p in papers:
    t=re.sub(r'[ \t]+',' ',open(S+'/text/%s.txt'%p,errors='replace').read())
    chunks=[t[i:i+6000] for i in range(0,len(t),5400)]
    for k,c in enumerate(chunks):
        if (p,k) in done: continue
        t0=time.time()
        try: raw=call(c); err=None
        except Exception as e: raw,err='',str(e)[:200]
        try: errs=json.loads(raw).get('errors',[])
        except Exception: errs=None
        open(OUT,'a').write(json.dumps({'arxiv':p,'chunk':k,'n_chunks':len(chunks),'errors':errs,'raw':raw if errs is None else '','secs':round(time.time()-t0,1),'err':err,'model':MODEL})+'\n')
print('done')
