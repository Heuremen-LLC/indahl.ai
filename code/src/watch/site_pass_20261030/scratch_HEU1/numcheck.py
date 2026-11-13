import re, os, glob, html, bisect, json, sys
root=os.path.expanduser('~/bones-forge')
exp=root+'/heuremen.org/experiments'
numre=re.compile(r'(?<![\w.])(\d+\.\d+|\d+)(?:[eE]([+-]?\d+))?')
def parse(s):
    out=[]
    for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)?)(?:[eE]([+-]?\d+))?',s):
        try: v=float(m.group(1))
        except Exception: continue
        if m.group(2):
            try: v*=10**int(m.group(2))
            except Exception: continue
        out.append(v)
    return out
corpus=[]
nfiles=0
for dp,dn,fn in os.walk(exp):
    for f in fn:
        if f.endswith(('.text','.txt','.py','.md')) and not f.startswith('ibm_jobs') and not f.startswith('rigetti_tasks') and not f.startswith('backend_properties') and not f.startswith('props_') and not f.startswith('raw_'):
            p=os.path.join(dp,f)
            if os.path.getsize(p)>3_000_000: continue
            try: t=open(p,encoding='utf-8',errors='replace').read()
            except: continue
            nfiles+=1
            corpus+=parse(t)
# ledger
for l in open(root+'/ledger/ledger.jsonl'):
    corpus+=parse(l)
corpus=sorted(set(corpus))
print('files',nfiles,'corpus',len(corpus),file=sys.stderr)
def present(tok):
    dp=len(tok.split('.')[1]) if '.' in tok else 0
    v=float(tok)
    tol=0.5*10**(-dp)*1.0001+1e-12
    for scale in (1,100,0.01,1000,0.001,1e6,1e-6):
        x=v/scale; t2=tol/scale
        i=bisect.bisect_left(corpus,x-t2)
        if i<len(corpus) and corpus[i]<=x+t2: return True
    return False
def pagetext(f):
    raw=open(f,encoding='utf-8').read()
    body=raw.split('</head>')[1]
    body=re.sub(r'<script.*?</script>|<style.*?</style>','',body,flags=re.S)
    body=re.sub(r'<a [^>]*>(.*?)</a>',r'\1',body,flags=re.S)  # keep link text but
    t=html.unescape(re.sub(r'<[^>]+>',' ',body))
    return t
res={}
for f in sorted(glob.glob('live/*.html')):
    t=pagetext(f)
    # drop file-name like tokens, job ids, hash fragments, dates/times
    t=re.sub(r'\b[0-9a-f]{8,}\b','',t)
    t=re.sub(r'\bdb[a-z0-9]{18,}\b','',t)
    t=re.sub(r'HLC-[0-9A-F]+','',t)
    t=re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\b','',t)
    toks=re.findall(r'(?<![\w.])\d+\.\d+(?![\w])',t)
    toks=[x for x in toks]
    miss=[]
    for tk in dict.fromkeys(toks):
        if not present(tk): miss.append(tk)
    res[f]=(len(set(toks)),miss)
    print(os.path.basename(f)[:70],len(set(toks)),'missing',len(miss),flush=True)
json.dump({k:v for k,v in res.items()},open('numcheck_out.json','w'))
