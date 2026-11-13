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
def folder_nums(folder):
    out=[]
    for dp,dn,fn in os.walk(folder):
        for f in fn:
            if f.endswith(('.text','.txt','.py','.md')) or (f.endswith('.json') and not f.startswith(('props_','backend_','raw_','ibm_jobs','rigetti'))):
                p=os.path.join(dp,f)
                if os.path.getsize(p)>3_000_000: continue
                try: out+=parse(open(p,encoding='utf-8',errors='replace').read())
                except: pass
    return out
cache={}
def fnums(folder):
    if folder not in cache: cache[folder]=sorted(set(folder_nums(folder)))
    return cache[folder]
def present(corpus,tok):
    dp=len(tok.split('.')[1]) if '.' in tok else 0
    v=float(tok); tol=0.5*10**(-dp)*1.0001+1e-12
    for scale in (1,100,0.01,1000,0.001,1e6,1e-6):
        x=v/scale; t2=tol/scale
        i=bisect.bisect_left(corpus,x-t2)
        if i<len(corpus) and corpus[i]<=x+t2: return True
    return False
links=json.load(open('links2.json'))
page_links={}
for t,pp in links.items():
    for p in pp: page_links.setdefault(p,set()).add(t)
ledger_nums=sorted(set(parse(open(root+'/ledger/ledger.jsonl').read())))
out={}
for f in sorted(glob.glob('live/*.html')):
    name=os.path.basename(f)
    raw=open(f,encoding='utf-8').read()
    # page url
    url=None
    # reconstruct from name
    loc=name.replace('__','/').replace('index.html','')
    url='https://heuremen.org/'+('' if loc=='index.html' else loc)
    if loc=='': url='https://heuremen.org/'
    # folders: the page's own folder + folders of linked experiment pages
    folders=set()
    for t in page_links.get(url,set()):
        m=re.match(r'https://heuremen.org/(experiments/[^/]+(?:/[^/]+)?)/',t)
        if m: folders.add(os.path.join(root,'heuremen.org',m.group(1)))
        elif t.startswith('https://heuremen.org/experiments/') and '.' in t.rsplit('/',1)[-1]:
            folders.add(os.path.dirname(os.path.join(root,'heuremen.org',t[len('https://heuremen.org/'):])))
    own=os.path.dirname(os.path.join(root,'heuremen.org',loc)) if loc not in('',) else root+'/heuremen.org'
    if own!=root+'/heuremen.org': folders.add(own)
    corpus=set(ledger_nums) if True else set()
    for fo in folders:
        if os.path.isdir(fo) and fo!=root+'/heuremen.org': corpus|=set(fnums(fo))
    corpus=sorted(corpus)
    body=raw.split('</head>')[1]
    body=re.sub(r'<script.*?</script>|<style.*?</style>','',body,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',body))
    t=re.sub(r'\b[0-9a-f]{8,}\b','',t); t=re.sub(r'\bdb[a-z0-9]{18,}\b','',t); t=re.sub(r'HLC-[0-9A-F]+','',t)
    toks=[x for x in dict.fromkeys(re.findall(r'(?<![\w.])\d+\.\d{3,}(?![\w])',t))]
    miss=[x for x in toks if not present(corpus,x)]
    out[name]=(len(toks),miss,len(folders))
    print(name[:70],len(toks),'missing',len(miss),miss[:30],flush=True)
json.dump(out,open('numcheck2_out.json','w'))
