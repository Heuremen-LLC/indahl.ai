import json,collections
rows=[json.loads(l) for l in open('/Users/heuremen/bones-forge/watch/tp_score.jsonl') if l.strip()]
print(len(rows), rows[607]['at'], rows[608]['at'] if len(rows)>608 else '')
print(collections.Counter(tuple(sorted(r.keys())) for r in rows).most_common(5))
# monotone?
ats=[r['at'] for r in rows]; print('sorted',ats==sorted(ats))
R=rows[:608]
c=collections.Counter((r.get('caught'),r.get('by')) for r in R); print(c)
print(collections.Counter(r.get('lesson') for r in R))
b=[r for r in R if r.get('caught')=='BEFORE']; print(len(b))
print(collections.Counter(r['by'] for r in b))
f=R[:20]; print('first20',sum(r['caught']=='BEFORE' for r in f), sum(r['caught']=='BEFORE' and r['by']=='bones' for r in f), collections.Counter(r.get('lesson') for r in f))
print(collections.Counter(r['by'] for r in R))
import math
for k in [(148,608)]:
  p=k[0]/k[1]; print(p)
  se_b=math.sqrt(.077*.923/26); print('bar se',se_b,'z-with-bar', (p-.077)/math.sqrt(p*(1-p)/608+se_b**2),'z fixed',(p-.077)/math.sqrt(.077*.923/608))
  print('z sampling only', (p-.077)/math.sqrt(p*(1-p)/608))
