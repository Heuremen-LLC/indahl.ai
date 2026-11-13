import os, re, sys
from decimal import Decimal
ROOT=os.path.expanduser('~/bones-forge/heuremen.org/experiments')
toks=sys.argv[1:]
pat=re.compile(r'(?<![\w.])[+\-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')
targets=[]
for t in toks:
    s=t.lstrip('+').replace('−','-')
    d=Decimal(s); q=Decimal(1).scaleb(-(len(s.split('.')[1]) if '.' in s else 0))
    targets.append((t,d,q))
hits={t:[] for t,_,_ in targets}
for dp,dn,fn in os.walk(ROOT):
    for f in fn:
        if not f.endswith(('.text','.txt','.md')): continue
        p=os.path.join(dp,f)
        try: txt=open(p,errors='ignore').read()
        except: continue
        if len(txt)>5_000_000: continue
        for ln,line in enumerate(txt.split('\n'),1):
            for m in pat.findall(line):
                try:
                    v=Decimal(m.lstrip('+'))
                    if abs(v)>Decimal('1e6') or (v!=0 and abs(v)<Decimal('1e-9')): continue
                except: continue
                for t,d,q in targets:
                    for fct in (Decimal(1),Decimal(100)):
                        w=v*fct
                        if abs(abs(w)-abs(d))<=q/2+Decimal('1e-12') and (w>=0)==(d>=0):
                            if len(hits[t])<6: hits[t].append((os.path.relpath(p,ROOT),ln,line.strip()[:200]))
for t in hits:
    print('==',t)
    for h in hits[t]: print('  ',h)
