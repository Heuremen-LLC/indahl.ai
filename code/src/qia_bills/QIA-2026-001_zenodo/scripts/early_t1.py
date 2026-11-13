import json,numpy as np,collections,datetime as D
S='/Users/heuremen/bones-forge/heuremen.org/experiments/2026-10-21-measurements/processors_apparatus/data/time_runs_ruler_copies.json'
d=json.load(open(S))['runs']
F=[json.loads(l) for l in open('/Users/heuremen/bones-forge/parallax/fleet_watch/fleet_records.jsonl')]
fl=collections.defaultdict(dict)
for r in F: fl[r['chip']][r['day']]=r
def tau(l): return -300/np.log(np.clip(l,0.02,0.98))
print('%-14s %4s %-19s %4s | our median tau (copies a,b,c) from 300us level | fleet record: day stamp  T1med  (record on the day, next day)'%('chip','run','start','nq'))
for r in d:
    R=np.array(r['rows']); L=R[:,[3,7,11]]
    t=np.median(tau(L),axis=0)
    day=r['start'][:10]; nd=(D.date.fromisoformat(day)+D.timedelta(days=1)).isoformat()
    f0=fl[r['chip']].get(day); f1=fl[r['chip']].get(nd)
    # also median of per-qubit mean tau
    print('%-14s %4d %-19s %4d | %6.1f %6.1f %6.1f | %s | %s'%(r['chip'],r['run'],r['start'][:19],len(R),*t,
        ('%s %s %.1f'%(day,f0['stamp'][5:16],f0['t1']) if f0 else day+' none'),('%s %s %.1f'%(nd,f1['stamp'][5:16],f1['t1']) if f1 else nd+' none')))
