import json,numpy as np,collections
F=[json.loads(l) for l in open('/Users/heuremen/bones-forge/parallax/fleet_watch/fleet_records.jsonl')]
by=collections.defaultdict(list)
for r in F: by[r['chip']].append(r)
allc=[]
for c,rs in by.items():
    rs.sort(key=lambda r:r['day'])
    # distinct records by (stamp,t1,t2)
    dist=[]; 
    for r in rs:
        if not dist or (r['t1'],r['t2'])!=(dist[-1]['t1'],dist[-1]['t2']): dist.append(r)
    ch=[(b['t1']/a['t1']-1) for a,b in zip(dist,dist[1:])]
    abs_us=[abs(b['t1']-a['t1']) for a,b in zip(dist,dist[1:])]
    ch2=[(b['t2']/a['t2']-1) for a,b in zip(dist,dist[1:])]
    allc+=ch
    print('%-15s records %d, distinct (T1,T2) sets %d, T1 median range %.1f-%.1f us; consecutive distinct sets: median |change| %.1f us (%.1f%%), max %.1f us (%.1f%%); T2 median |change| %.1f%%'%(c,len(rs),len(dist),min(r['t1'] for r in rs),max(r['t1'] for r in rs),np.median(abs_us),100*np.median(np.abs(ch)),max(abs_us),100*max(np.abs(ch)),100*np.median(np.abs(ch2))))
print('all chips: median |daily change of published T1 median| %.1f%%, 90th pct %.1f%%'%(100*np.median(np.abs(allc)),100*np.percentile(np.abs(allc),90)))
