import re, os, glob, html, bisect, json, sys
root=os.path.expanduser('~/bones-forge'); exp=root+'/heuremen.org/experiments'
def parse(s):
    out=[]
    for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)?)(?:[eE]([+-]?\d+))?',s):
        try: v=float(m.group(1))
        except: continue
        if m.group(2):
            try: v*=10**int(m.group(2))
            except: continue
        out.append(v)
    return out
corpus=[]
for dp,dn,fn in os.walk(exp):
    for f in fn:
        if f.endswith('.text') or f=='README.text':
            p=os.path.join(dp,f)
            if os.path.getsize(p)>2_000_000: continue
            corpus+=parse(open(p,encoding='utf-8',errors='replace').read())
for l in open(root+'/ledger/ledger.jsonl'): 
    r=json.loads(l)
    if r['status']=='live': corpus+=parse(json.dumps({k:r.get(k) for k in ('claim','value','lo','hi')})+json.dumps(r['source']))
corpus=sorted(set(corpus)); print('corpus',len(corpus),flush=True)
def present(tok):
    dp=len(tok.split('.')[1]); v=float(tok); tol=0.5*10**(-dp)*1.0001+1e-12
    for scale in (1,100,0.01,1000,0.001):
        x=v/scale; t2=tol/scale
        i=bisect.bisect_left(corpus,x-t2)
        if i<len(corpus) and corpus[i]<=x+t2: return True
    return False
for f in ['live/index.html','live/technical-summary.html','live/what-we-measured.html','live/correlations.html']+sorted(glob.glob('live/experiments__2026-10-21-measurements__*.html')):
    raw=open(f,encoding='utf-8').read()
    body=re.sub(r'<script.*?</script>|<style.*?</style>','',raw.split('</head>')[1],flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',body))
    t=re.sub(r'\b[0-9a-f]{8,}\b','',t); t=re.sub(r'HLC-[0-9A-F]+','',t)
    toks=list(dict.fromkeys(re.findall(r'(?<![\w.])\d+\.\d{3,}(?![\w])',t)))
    miss=[x for x in toks if not present(x)]
    print(os.path.basename(f)[:60],len(toks),'missing',miss,flush=True)
