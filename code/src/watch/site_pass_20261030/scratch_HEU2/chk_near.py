import json, re, os, sys
from decimal import Decimal
ROOT=os.path.expanduser('~/bones-forge')
rows=[json.loads(l) for l in open(os.path.join(ROOT,'ledger/ledger.jsonl'))]
surf=sys.argv[1]; maxd=int(sys.argv[2])
numre=re.compile(r'(?<![\w.])[+\-−]?\d+\.\d+(?:[eE][+-]?\d+)?')
out=[]; nrow=0
for r in rows:
    if r['status']!='live': continue
    sn=[s['text'] for s in r['surfaces'] if s['surface']==surf]
    if not sn: continue
    nrow+=1
    f=r['source']['file']; sp=f if f.startswith('/') else os.path.join(ROOT,f)
    if not os.path.exists(sp): continue
    txt=open(sp,errors='ignore').read()
    g=r['source']['grep']; i=txt.find(g)
    if i<0: continue
    gl=txt[:i].count('\n')
    lines=txt.split('\n')
    # candidate lines per value
    for s in sn:
        s2=s.replace('−','-')
        for t in numre.findall(s2):
            tt=t.lstrip('+')
            try: d=Decimal(tt)
            except: continue
            q=Decimal(1).scaleb(-(len(tt.split('.')[1].split('e')[0].split('E')[0]) if '.' in tt else 0))
            best=None
            for ln,line in enumerate(lines):
                for m in numre.findall(line.replace('−','-')):
                    try: v=Decimal(m.lstrip('+'))
                    except: continue
                    if abs(v)>Decimal('1e6'): continue
                    for fct in (Decimal(1),Decimal(100),Decimal('0.01')):
                        w=v*fct
                        if abs(abs(w)-abs(d))<=q/2+Decimal('1e-12'):
                            dist=abs(ln-gl)
                            if best is None or dist<best: best=dist
            if best is None: out.append((r['id'],t,'NOT IN FILE'))
            elif best>maxd: out.append((r['id'],t,f'nearest {best} lines from grep line {gl+1}', f))
print('rows',nrow,'flagged tokens',len(out))
for o in out: print(o)
