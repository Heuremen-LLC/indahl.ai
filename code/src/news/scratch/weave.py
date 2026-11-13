import json,re,sqlite3
deeps=[d for d in json.load(open('deeps.json')) if 12388<=d['cycle']<=12402]
print('landed',len(deeps),[ (d['cycle'],d['at'][11:19],d['status']) for d in deeps])
from collections import Counter
print(Counter(d['status'] for d in deeps))
con=sqlite3.connect('/Users/heuremen/bones-forge/gridsong/nova_corpus.db')
prior=con.execute("select cycle,nova_says from cycles_v2 where source='nova_flywheel' and cycle<12388 order by cycle desc limit 400").fetchall()
def toks(s): return re.findall(r"[a-z0-9']+",(s or '').lower())
def jac(a,b):
    a,b=set(a),set(b)
    return len(a&b)/max(1,len(a|b))
def lrun(a,b):
    # longest common word run
    best=0
    idx={}
    for i,w in enumerate(b): idx.setdefault(w,[]).append(i)
    prev={}
    for i,w in enumerate(a):
        cur={}
        for j in idx.get(w,[]):
            cur[j]=prev.get(j-1,0)+1
            if cur[j]>best: best=cur[j]
        prev=cur
    return best
allprev=[(c,toks(s)) for c,s in prior]
seen=[]
for d in deeps:
    t=toks(d['synthesis'])
    names=[n for n in ('Anvil','Loom','Forge') if n in d['synthesis']]
    exact=[c for c,s in prior if s and d['synthesis'].strip() and d['synthesis'].strip() in s]
    br=(0,None); bj=(0,None)
    for c,p in allprev[:60]+seen:
        r=lrun(t,p); j=jac(t,p)
        if r>br[0]: br=(r,c)
        if j>bj[0]: bj=(round(j,2),c)
    seen.append((d['cycle'],t))
    print(d['cycle'],d['status'],'names',len(names),'minority' if d['synthesis'].lstrip().startswith('Minority report') else '-','len',len(d['synthesis']),'run',br,'jac',bj,'exact',exact[:2], 'same_next' if d['synthesis'].strip()==str(d['next']).strip() else '')
for d in deeps:
    print('\n#####',d['cycle'],d['status'],'Q:',d['question']); print('S:',d['synthesis'][:1200]); print('N:',d['next'][:200]); print('flags:',d.get('flags'))
