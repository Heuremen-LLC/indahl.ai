"""our_load_full.py -- our IBM jobs against the maker's daily calibration record, every job on every key (197, 24 Sep - 4 Oct), beside the first read (121 jobs, §244).
Same arithmetic as §244, recovered verbatim from the session; only the job list changed. Run from this folder."""
import json, datetime as D, statistics as S
H={tuple(k.split('|')): v for k,v in json.load(open('maker_history_20261004.json')).items() if 'err' not in v}
jobs=[(D.datetime.fromisoformat(r[0]), r[1]) for r in json.load(open('all_ibm_jobs_197.json'))]
print("OUR LOOKS AGAINST THE MAKER'S RECORD (IBM daily calibration, 18 Sep - 4 Oct; our jobs 24 Sep - 4 Oct, all four keys, 197 jobs). Per chip-day: our jobs that day, then the change at the maker's next calibration.")
rows=[]
for (ch,day),v in sorted(H.items()):
    d=D.date.fromisoformat(day); nxt=H.get((ch,(d+D.timedelta(days=1)).isoformat()))
    n=sum(1 for t,b in jobs if b==ch and t.date()==d)
    if nxt and nxt['updated']!=v['updated']:
        rows.append((ch,day,n,nxt['t1']-v['t1'],nxt['t2']-v['t2'],(nxt['ro']-v['ro'])*1e4))
for r in rows:
    if r[2]: print(f"  {r[0]:<15} {r[1]}: our jobs {r[2]:>3} | next calibration: T1 {r[3]:+6.1f} us, T2 {r[4]:+6.1f} us, readout error {r[5]:+5.1f} x1e-4")
def sp(x,y):
    rx=[sorted(x).index(a)+ (x.count(a)-1)/2 for a in x]; ry=[sorted(y).index(a)+(y.count(a)-1)/2 for a in y]; mx=S.mean(rx); my=S.mean(ry)
    return sum((a-mx)*(b-my) for a,b in zip(rx,ry))/((sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))**.5)
ns=[r[2] for r in rows]
quiet=[r for r in rows if r[2]==0]; busy=[r for r in rows if r[2]>0]
print(f"  chip-days {len(rows)} ({len(busy)} with our jobs, {len(quiet)} without)")
for i,nm in ((3,'T1'),(4,'T2'),(5,'readout error')):
    print(f"  {nm:<14}: rank correlation with our jobs that day {sp(ns,[r[i] for r in rows]):+.2f} | mean change after our days {S.mean(r[i] for r in busy):+.2f}, after quiet days {S.mean(r[i] for r in quiet):+.2f} (spread of quiet days {S.pstdev(r[i] for r in quiet):.2f})")