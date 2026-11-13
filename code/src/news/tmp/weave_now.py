import json,re
from collections import Counter
recs=[]
for l in open('ledger_tail.jsonl','rb').read().decode('utf-8','replace').splitlines():
    try: recs.append(json.loads(l))
    except Exception: pass
deeps=[r for r in recs if r.get('kind')=='deep']
LO,HI=13006,13020
cur=[d for d in deeps if LO<=d['cycle']<=HI]
prior=[d for d in deeps if d['cycle']<LO]
def toks(s): return re.findall(r"[a-z0-9']+",(s or '').lower())
def jac(a,b):
    a,b=set(a),set(b); return len(a&b)/max(1,len(a|b))
def lrun(a,b):
    best=0; idx={}
    for i,w in enumerate(b): idx.setdefault(w,[]).append(i)
    prev={}
    for i,w in enumerate(a):
        c={}
        for j in idx.get(w,[]):
            c[j]=prev.get(j-1,0)+1
            if c[j]>best: best=c[j]
        prev=c
    return best
try: sd=json.load(open('sage_dreams.json'))
except Exception: sd=[]
sage=[('sage:'+x.get('dreamer','?')+x.get('created_at','')[11:16],toks(x.get('dream',''))) for x in sd]
seen=[(d['cycle'],toks(d['synthesis'])) for d in prior]
print('landed',len(cur),Counter(d['status'] for d in cur))
for d in cur:
    t=toks(d['synthesis'])
    names=[n for n in ('Anvil','Loom','Forge') if n in d['synthesis']]
    br=(0,None); bj=(0,None); sj=(0,None); sr=(0,None)
    for c,p in seen:
        r=lrun(t,p); j=jac(t,p)
        if r>br[0]: br=(r,c)
        if j>bj[0]: bj=(round(j,2),c)
    for c,p in sage:
        r=lrun(t,p); j=jac(t,p)
        if r>sr[0]: sr=(r,c)
        if j>sj[0]: sj=(round(j,2),c)
    seen.append((d['cycle'],t))
    print(d['cycle'],d['at'][11:19],d['status'],'names',len(names),'minority' if d['synthesis'].lstrip().startswith('Minority report') else '-','len',len(d['synthesis']),'run',br,'jac',bj,'sageJ',sj,'sageRun',sr,'SAME_NEXT' if d['synthesis'].strip()==str(d['next']).strip() else '','flags',repr(d.get('flags'))[:60])
import sys
if len(sys.argv)>1:
    for d in cur:
        print('\n#####',d['cycle'],d['status'],'Q:',d['question']); print('S:',d['synthesis'][:1300]); print('N:',str(d['next'])[:250])
