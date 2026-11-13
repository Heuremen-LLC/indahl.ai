import sys,json
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
exec(S.split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
# radius sensitivity
for f in (0.997,1.003):
    chg=0; cc=0; ins=0
    for r in BIN:
        z=r['zone']; z2=(z[0],z[1],z[2]*f,z[3],z[4])
        ts,ms=zone_events_cache=None,None
        zcache.pop((r['seq'],z2),None)
        n=count(r['seq'],z2,r['t0'],r['t1'],r['mag'])
        o='CONSISTENT' if r['nmin']<=n<=r['nmax'] else ('ABOVE' if n>r['nmax'] else 'BELOW')
        if n!=r['count']: cc+=1
        if o!=r['outcome']: chg+=1
        if r['mag']==3.0 and o=='CONSISTENT': ins+=1
    print('radius x%.3f: rows with different count %d, different outcome %d, M3 inside %d of 31950'%(f,cc,chg,ins),flush=True)
    zcache.clear()
# first in-frame version per seq
first={}
for r in BIN:
    if r['seq'] not in first or r['issued']<first[r['seq']]: first[r['seq']]=r['issued']
fr=[r for r in BIN if r['mag']==3.0 and r['issued']==first[r['seq']]]
print('first scored version per sequence, M3:',len(fr),sum(1 for r in fr if r['outcome']=='CONSISTENT'))
# deleted event? first version by sequence in terms of update time overall
# gap between catalog fetch and window end for scored windows
import statistics
age=[(fetched[r['seq']]-r['t1'])/DAY for r in BIN if r['mag']==3.0]
print('days between window end and catalog read: min %.1f p10 %.1f median %.1f'%(min(age),sorted(age)[len(age)//10],statistics.median(age)))
print('scored M3 rows whose window ended <30 days before catalog read:',sum(1 for a in age if a<30),'of',len(age))
# rows by index time more than 1 day late
idx={}
for eid,p in versions: idx[(eid,p['updateTime'])]=p.get('indexTime')
late=[r for r in BIN if idx.get((r['seq'],r['issued'])) and idx[(r['seq'],r['issued'])]>r['t0']]
print('indexTime after t0:',len(late),'more than 1 day:',sum(1 for r in late if idx[(r['seq'],r['issued'])]-r['t0']>DAY),'M3',sum(1 for r in late if r['mag']==3.0))
# rows per version equal? M3 appears every version
vers_with_m3=len(set((r['seq'],r['issued']) for r in BIN if r['mag']==3.0)); print('versions with M3 scored row',vers_with_m3)
# version counts per window label that appear
print(C.Counter(r['window'] for r in BIN if r['mag']==3.0))
# magnitude bins offered by version
print(C.Counter(r['mag'] for r in BIN))
# 0,0 ranges
z=sum(1 for r in BIN if r['mag']==3.0 and r['nmin']==0 and r['nmax']==0); print('M3 rows with range 0-0',z)
# headline excluding versions that are 0-0 ranges? degenerate: share inside among nonzero ranges
nz=[r for r in BIN if r['mag']==3.0 and r['nmax']>0]; print('M3 nmax>0 rows',len(nz),sum(1 for r in nz if r['outcome']=='CONSISTENT'))
