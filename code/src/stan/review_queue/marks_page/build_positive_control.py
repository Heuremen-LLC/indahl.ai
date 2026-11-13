"""Positive control for the spot-check judge + yes-rates by quotable cell (12 Nov 2026). Run from scripts/ dir."""
import json,random,re,collections,sys
sys.path.insert(0,'/Users/heuremen/bones-forge/stan/scripts')
from common import *
M=S+'/review_queue/marks_page/'
it=json.load(open(M+'items.json')); seen={x['id']:x['text'] for x in it}
Q={('F1','PRESENT'),('F1','ABSENT'),('F2','PRESENT'),('F2','ABSENT'),('F3','PRESENT')}
pos=[('caa68f493f80','improvements of up to 45 percent when using an optimized swap-out design'),
('9edf432b337f','observe up to a 50% error reduction in the fidelity'),
('9edf432b337f','reduces the overall schedule duration by up to 52% and errors by up to 38%'),
('7bbe789b0d83','reduces total error by up to 73\\% compared to conventional approaches'),
('eeeb59274f80','demonstrate up to 3-4x reduction in wall clock time'),
('eeeb59274f80','yielding up to 3x speedup'),
('117e55b1a2f6','We observe a relative gain of up to ~ 34% in out-of-sample test scores'),
('d0b570e43454','we find SP infidelities up to 6.57% and readout assignment errors up to 19.1%'),
('fad148ca986b','produces solutions up to 21.7% worse than the classical baseline'),
('eeeb59274f80','Simulated results predict over 5x speed-up in parallel execution mode.')]
bad=re.compile(r'\d|up ?to|best|max|project|predict|peak|highest|largest|record',re.I)
neg=[];used=set(i for i,_ in pos)
for i,t in seen.items():
    if i in used: continue
    body=t.split('\n\n',1)[-1]
    for s in re.split(r'(?<=[.!?])\s+',body)[:3]:
        if 40<len(s)<190 and not bad.search(s) and ws(s) in ws(t) and s in t:
            neg.append((i,s)); used.add(i); break
    if len(neg)==10: break
assert len(neg)==10 and all(ws(q) in ws(seen[i]) for i,q in pos+neg)
rows=[]
for kind,L in (('positive',pos),('negative',neg)):
    for i,q in L:
        rows.append({'set':'PC','kind':kind,'id':i,'code':'F2','label':'PRESENT','quote':q,'definition':code_block('F2'),'text':seen[i],'q':'Does the quote support the label?',
          'built_to_be':'yes' if kind=='positive' else 'no'})
random.Random(7777).shuffle(rows)
for n,r in enumerate(rows,1): r['n']=n
json.dump(rows,open(M+'positive_control.json','w'),indent=1)
for r in rows: print(r['n'],r['kind'],'|',r['quote'][:110])
# yes-rates
wf={'A-17':'yes','A-18':'yes','A-21':'yes','A-24':'yes','A-25':'yes','A-26':'yes','A-27':'yes','A-28':'yes','A-14':'no','A-16':'no','A-13':'ct','A-15':'ct','A-19':'ct','A-20':'ct','A-22':'ct','A-23':'ct'}
bm={m['key']:m for m in json.load(open(M+'bones_marks.json'))}
meta={'%s-%02d'%(x['set'],x['n']):x for x in it}
def tab(marks,keys,name):
    t=collections.defaultdict(collections.Counter); mix=collections.Counter()
    for k in keys:
        x=meta[k]; cell='quotable' if (x['code'],x['label']) in Q else 'non-quotable'
        t[cell][marks[k] if isinstance(marks[k],str) else marks[k]['mark']]+=1; mix[(x['code'],x['label'])]+=1
    print(name); 
    for cell in ('quotable','non-quotable'):
        c=t[cell];n=sum(c.values());print('  ',cell,dict(c),'yes-rate %s/%s'%(c['yes'],n))
    print('   code mix',{'%s %s'%k:v for k,v in sorted(mix.items())})
wk=['A-%02d'%n for n in range(13,29)]
tab(wf,wk,'Wayfinder A-13..A-28')
tab(bm,wk,'blind pass on the same A-13..A-28')
tab(bm,['A-%02d'%n for n in range(1,41)],'blind pass all A (40)')
tab(bm,['C-%02d'%n for n in range(1,21)],'blind pass all C (20)')
