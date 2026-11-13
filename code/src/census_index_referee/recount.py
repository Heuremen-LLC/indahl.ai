import csv,glob,gzip,json,os,math,collections,datetime
R='/Users/heuremen/bones-forge/census_index/'
def sh(m,k):
    t=int(m[:4])*12+int(m[5:7])-1+k; return '%04d-%02d'%(t//12,t%12+1)
def load(sid):
    vs=[];d={}
    for f in sorted(glob.glob(R+'data/cache/alfred/%s_[12]*.csv'%sid)):
        v=os.path.basename(f)[len(sid)+1:-4]; x={}
        for r in list(csv.reader(open(f)))[1:]:
            try:x[r[0][:7]]=float(r[1])
            except: pass
        if x: vs.append(v);d[v]=x
    return vs,d
def widths():
    W={}
    for f in sorted(glob.glob(R+'data/snapshots/*_errors.json.gz')):
        doc=json.load(gzip.open(f));rows=doc['rows'];h=rows[0]
        ds=os.path.basename(f).split('_')[1]
        for r in rows[1:]:
            g=lambda k:r[h.index(k)]
            if g('seasonally_adj')!='yes':continue
            try:v=float(g('cell_value'))
            except:continue
            W.setdefault((ds,g('category_code'),g('data_type_code'),g('geo_level_code'),g('time')),v)
    return W
W=widths()
SP=[]
for g,s,e in (('US','','US'),('NE','NE','NO'),('MW','MW','MW'),('S','S','SO'),('W','W','WE')):
    SP.append(('SALES',g,'HSN1F'+s,'ressales','ASOLD','E_TOTAL',e,1.645))
    SP.append(('STARTS',g,'HOUST'+s,'resconst','ASTARTS','E_TOTAL',e,1.645))
SP.append(('COMP','US','COMPUTSA','resconst','ACOMPLETIONS','E_TOTAL','US',1.645))
SP.append(('RETAIL','US','RSAFS','marts','44X72','E_SM','US',1.753))
def wilson(k,n,z=1.959964):
    if n==0:return (None,None)
    p=k/n;d=1+z*z/n;c=p+z*z/2/n;a=z*math.sqrt(p*(1-p)/n+z*z/4/n/n);return ((c-a)/d,(c+a)/d)
res={};allrows=[]
for nm,g,sid,ds,cat,dt,eg,mult in SP:
    vs,d=load(sid)
    fs={}
    for v in vs:
        for m in d[v]: fs.setdefault(m,v)
    # annual vintages: any month <= newest-14 changed
    av={}
    for i in range(1,len(vs)):
        a,b=d[vs[i-1]],d[vs[i]];n=max(b);mx=0;ch=0
        for m,x in b.items():
            if m<=sh(n,-14) and m in a and a[m]!=x: ch=1;mx=max(mx,abs(x-a[m])/abs(a[m]))
        if ch:av[vs[i]]=mx
    brk=None
    if nm=='RETAIL':
        big=[v for v,c in av.items() if c>0.03];brk=big[0] if big else None
    for m in sorted(fs):
        if m in d[vs[0]]:continue
        v1=fs[m];p1=d[v1][m];rse=W.get((ds,cat,dt,eg,m))
        for st in('S1','S2','S3'):
            tv=vs[-1] if st=='S3' else fs.get(sh(m,1 if st=='S1' else 2))
            if tv is None or m not in d.get(tv,{}) or (st=='S3' and tv<=v1): o='CT:missing';later=None
            else:
                later=d[tv][m]
                if rse is None:o='CT:nowidth'
                elif brk and v1<brk<=tv:o='CT:break'
                elif st!='S3' and any(v1<a<=tv for a in av):o='CT:annual'
                else:
                    h=mult*rse/100*p1
                    o='IN' if p1-h<=later<=p1+h else ('ABOVE' if later>p1+h else 'BELOW')
            allrows.append((nm,g,st,m,v1,p1,later,rse,o))
            res.setdefault((nm,g,st),collections.Counter())[o]+=1
    print(sid,'vintages',len(vs),'annual',len(av),'brk',brk)
out={}
for k,c in sorted(res.items()):
    n=c['IN']+c['ABOVE']+c['BELOW'];lo,hi=wilson(c['IN'],n)
    print(k,'in',c['IN'],'/',n,'above',c['ABOVE'],'below',c['BELOW'],'wilson',None if lo is None else (round(lo,4),round(hi,4)),{x:y for x,y in c.items() if x.startswith('CT')})
json.dump(allrows,open('/Users/heuremen/bones-forge/census_index_referee/my_rows.json','w'))
# compare to builder
S=json.load(open(R+'summary_census.json'));diff=0
nmap={'COMPLETIONS':'COMP','Northeast':'NE','Midwest':'MW','South':'S','West':'W'}
for c in S['cells']:
    s=nmap.get(c['series'],c['series']);g=nmap.get(c['geo'],c['geo'])
    mine=res.get((s,g,c['step']))
    if mine is None:
        if c['scored']:print('MISSING',c);diff+=1
        continue
    if (mine['IN'],mine['ABOVE'],mine['BELOW'])!=(c['inside'],c['above'],c['below']) and c['width_basis']!='none':
        print('DIFF',c['series'],c['geo'],c['step'],mine['IN'],mine['ABOVE'],mine['BELOW'],'vs',c['inside'],c['above'],c['below']);diff+=1
print('cell diffs',diff)
# row-level compare
B=json.load(open(R+'data/census.json'))
bm={(r['alfred'],r['month'],r['step']):r for r in B}
print('builder rows',len(B),'mine',len(allrows))
