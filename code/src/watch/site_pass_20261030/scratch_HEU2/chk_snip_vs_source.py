import json, re, os, sys, html
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
ROOT = os.path.expanduser('~/bones-forge')
surf = sys.argv[1]
rows=[json.loads(l) for l in open(os.path.join(ROOT,'ledger/ledger.jsonl'))]
numre = re.compile(r'(?<![\w.])[+\-−]?\d+(?:\.\d+)?(?:e[+-]?\d+)?')
def toks(s):
    s=s.replace('−','-')
    return [t for t in numre.findall(s)]
cache={}
def srctoks(path):
    if path in cache: return cache[path]
    sp=path if path.startswith('/') else os.path.join(ROOT,path)
    if not os.path.exists(sp): cache[path]=None; return None
    txt=open(sp,errors='ignore').read().replace('−','-')
    # collect number tokens as Decimals
    vals=set()
    for t in re.findall(r'(?<![\w.])[+\-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', txt):
        try: vals.add(Decimal(t))
        except: pass
    cache[path]=(vals,txt); return cache[path]
def match(tok, vals):
    t=tok.lstrip('+')
    try: d=Decimal(t)
    except: return True
    q=Decimal(1).scaleb(-(len(t.split('.')[1]) if '.' in t else 0))
    cands=[d]
    for sh in (0,2,-2,3,-3,6,-6):  # percent / unit scalings
        pass
    for v in vals:
        for f in (Decimal(1), Decimal(100), Decimal(1)/Decimal(100), Decimal(1000), Decimal(1)/Decimal(1000), Decimal(10), Decimal(1)/Decimal(10)):
            w=v*f
            try:
                if abs(w-d) <= q/2 + Decimal('1e-12'): return True
                if abs(abs(w)-abs(d)) <= q/2 + Decimal('1e-12'): return True
            except: pass
    return False
bad=[]; n=0
for r in rows:
    if r['status']!='live': continue
    for s in r['surfaces']:
        if s['surface']!=surf: continue
        n+=1
        # all source files for the row: main source plus any 'also' sources
        files=[r['source']['file']]
        for k in ('also','sources','more'):
            if k in r.get('source',{}): 
                v=r['source'][k]; files+= v if isinstance(v,list) else [v]
        # raw snippet from tex file text (before normalising)
        sn=s['text']
        sn=re.sub(r'\\[a-zA-Z]+\{?','  ',sn)  # drop commands
        miss=[]
        valsall=set()
        for f in files:
            st=srctoks(f)
            if st: valsall|=st[0]
        # also include row's own value/lo/hi
        for k in ('value','lo','hi'):
            for t in toks(str(r.get(k) or '')):
                try: valsall.add(Decimal(t.lstrip('+')))
                except: pass
        for t in toks(sn):
            if re.fullmatch(r'[+-]?\d{1,2}',t) and '.' not in t: continue  # skip small ints
            if not match(t, valsall): miss.append(t)
        if miss: bad.append((r['id'], miss, sn[:120].replace('\n',' '), r['source']['file']))
print('snippets',n,'with tokens not found in source file(s)',len(bad))
for b in bad: print(b)
