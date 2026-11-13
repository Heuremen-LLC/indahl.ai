import json, collections
D='/Users/heuremen/bones-forge/fidelity_index/'
N=json.load(open('nchs_pos.json')); YS=[y for y in range(2010,2025) if y!=2020]
def num(x):
    try: v=float(x)
    except: return None
    return None if v<0 else v
acs={}
for y in YS:
    r=json.load(open(D+'data/raw/acs_%d.json'%y))['rows']; h=r[0]
    for x in r[1:]:
        d=dict(zip(h,x))
        if d['NAME']!='Puerto Rico': acs[(d['NAME'],y)]=d
assert len({s for s,_ in acs})==51
def oc(n,e,m,y):
    if y==2024: return 'CT','nostated'
    if n is None: return 'CT','noreport'
    e=num(e); m=num(m)
    if e is None or m is None: return 'CT','noacs'
    lo=max(0,e-m); hi=e+m
    return ('ABOVE' if n>hi else 'BELOW' if n<lo else 'INSIDE'),None
rows=[]
for ev,k,t in (('DIVORCE','divorce','B12503'),('MARRIAGE','marriage','B12501')):
    for st in N[k]:
        if st in('United States','Not reported'): continue
        for y in YS:
            n=N[k][st][y-2000] if y<=2023 else None; d=acs[(st,y)]
            w=oc(n,d[t+'_010E'],d[t+'_010M'],y); m=oc(n,d[t+'_005E'],d[t+'_005M'],y)
            sp = w[0] in('ABOVE','BELOW','INSIDE') and m[0] in('ABOVE','BELOW','INSIDE') and w[0]!=m[0]
            rows.append(dict(ev=ev,st=st,y=y,n=n,w=w,m=m,sp=sp,e=num(d[t+'_010E']),moe=num(d[t+'_010M']),me=num(d[t+'_005E']),mmoe=num(d[t+'_005M'])))
json.dump(rows,open('my_rows.json','w'))
mine=collections.defaultdict(collections.Counter)
for r in rows:
    mine[r['ev']][r['w'][0] if r['w'][0]!='CT' else 'CT:'+r['w'][1]]+=1; mine[r['ev']]['split']+=r['sp']; mine[r['ev']]['rows']+=1
for e in mine: print(e,dict(mine[e]))
theirs=json.load(open(D+'data/fidelity.json'))
print(len(theirs),theirs[0].keys())
mp={(r['ev'],r['st'],r['y']):r for r in rows}; diffs=[]
for t in theirs:
    r=mp[(t['event'],t['state'],t['year'])]
    mo={'INSIDE':'CONSISTENT','CT':'CANNOT_TELL'}.get(r['w'][0],r['w'][0])
    if t['outcome']!=mo or t['reason']!={None:None,'nostated':'no stated count','noreport':'state does not report','noacs':'no ACS interval'}[r['w'][1]] or bool(t['sex_split'])!=r['sp'] or t['nchs']!=r['n']: diffs.append((t['event'],t['state'],t['year'],t['outcome'],mo))
print('row diffs',len(diffs),diffs[:10], 'sets equal', len(theirs)==len(rows))
# destination
for ev,D_ in (('DIVORCE',{'Nevada'}),('MARRIAGE',{'Nevada','Hawaii'})):
    c=collections.Counter(r['w'][0] for r in rows if r['ev']==ev and r['st'] in D_); print('dest',ev,dict(c))
    c=collections.Counter(r['w'][0] for r in rows if r['ev']==ev and r['st'] not in D_); print('exdest',ev,dict(c))
# DE 2018 divorce
print([ (r['st'],r['y'],r['w']) for r in rows if r['w'][1]=='noacs'])
