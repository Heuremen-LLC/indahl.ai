import sys,json,re,html
sys.argv=['x']
S=open('/Users/heuremen/bones-forge/quake_index_referee/code/recount.py').read()
exec(S.split("# ---- intervals")[0])
exec(S.split("# ---- intervals")[1].split("BIN = [r for r in sc")[0])
BIN=[r for r in sc if r['kind']=='bin']
FOR=re.compile(r'(Canada|Micronesia|Russia|Afghanistan|Venezuela|Colombia|Indonesia|Panama|Vanuatu|Burma|Cuba)')
foreign_ids={e['id'] for e in events.values() if FOR.search(e['title'])}
print('foreign events',len(foreign_ids), 'with scored rows',len({r['seq'] for r in BIN if r['seq'] in foreign_ids}))
out={}
def line(c): return '%s n=%d share %.4f [%.4f,%.4f] bl%d %s'%(c['cell'],c['scored'],c['share'],c['lo'],c['hi'],c['blocks'],c['outcome'])
for nm,f in (('US and territories',lambda r:r['seq'] not in foreign_ids),('elsewhere',lambda r:r['seq'] in foreign_ids)):
    m3=[r for r in BIN if r['mag']==3.0 and f(r)]
    c=cover_cell('M3 cover '+nm,m3,1); print(line(c)); out['m3_'+nm]=c
    for w in ('1 Day','1 Week','1 Month','1 Year'):
        c=cover_cell('  M3 %s %s'%(nm,w),[r for r in m3 if r['window']==w],1); print(line(c))
    hi=[r for r in BIN if r['p']>=0.1 and f(r)]
    c=rel_cell('p>=10 '+nm,hi,1); print('%s n=%d occ %d stated %.3f share %.3f [%.3f,%.3f] bl%d %s'%(c['cell'],c['scored'],c['occurred'],c['stated'],c['share'],c['lo'],c['hi'],c['blocks'],c['outcome']))
    for lbl,ff in (('M3',lambda r:r['mag']==3.0),('M4up',lambda r:r['mag']>=4)):
        h2=[r for r in hi if ff(r)]
        if h2:
            c=rel_cell('  p>=10 %s %s'%(nm,lbl),h2,1); print('%s n=%d share %.3f stated %.3f [%.3f,%.3f] bl%d %s'%(c['cell'],c['scored'],c['share'],c['stated'],c['lo'],c['hi'],c['blocks'],c['outcome']))
    for i in range(3,10):
        rs=[r for r in BIN if pbin(r['p'])==i and f(r)]
        if rs: c=rel_cell('  bin %d'%i,rs,1); print('   bin%g-%g n=%d share %.3f stated %.3f %s'%(PB[i]*100,PB[i+1]*100,c['scored'],c['share'],c['stated'],c['outcome']))
# nonzero-range coverage by magnitude
print('coverage excluding rows whose range is exactly 0 to 0')
for m in (3.0,4.0,5.0,6.0,7.0):
    rs=[r for r in BIN if r['mag']==m]; nz=[r for r in rs if r['nmax']>0]; z=[r for r in rs if r['nmax']==0]
    k=sum(1 for r in nz if r['outcome']=='CONSISTENT'); kz=sum(1 for r in z if r['outcome']=='CONSISTENT')
    c=cover_cell('nz',nz,1) if nz else None
    print('M%g: all %d, range 0-0: %d rows (%.1f%%) inside %d (%.4f); nonzero-range: %d rows inside %d (%.4f) %s'%(m,len(rs),len(z),100*len(z)/len(rs),kz,kz/max(1,len(z)),len(nz),k,k/max(1,len(nz)), (c and '[%.4f,%.4f] %s bl%d'%(c['lo'],c['hi'],c['outcome'],c['blocks']))))
nz=[r for r in BIN if r['nmax']>0]; c=cover_cell('nz all',nz,1); print('all mags nonzero-range',c['scored'],c['inside'],round(c['share'],4),'[%.4f,%.4f]'%(c['lo'],c['hi']),c['outcome'])
# lag per version
vl={}
for r in rows:
    if r['status']=='outside':
        k=(r['seq'],r['issued']); vl.setdefault(k,[]).append((r['issued']-r['t0'])/60000)
firstlag=sorted(min(v) for v in vl.values()); maxlag=sorted(max(v) for v in vl.values())
import statistics
print('late versions',len(vl),'median of smallest-lag window %.1f, of largest %.1f; versions with any window >1 day late: %d; with smallest >1 day: %d'%(statistics.median(firstlag),statistics.median(maxlag),sum(1 for x in maxlag if x>1440),sum(1 for x in firstlag if x>1440)))
wl=sorted((r['issued']-r['t0'])/60000 for r in {(r['seq'],r['issued'],r['t0']):r for r in rows if r['status']=='outside'}.values())
print('per (version,window): n',len(wl),'median %.1f; >1 day %d; <=15 min %d'%(statistics.median(wl),sum(1 for x in wl if x>1440),sum(1 for x in wl if x<=15)))
# page vs summary
summ=json.load(open('/Users/heuremen/bones-forge/quake_index/summary_quake.json'))
h=open('/Users/heuremen/bones-forge/quake_index/quake.html').read()
main=re.search(r'<main.*?</main>',h,re.S).group(0); txt=html.unescape(re.sub(r'<[^>]+>',' ',main)); txt=re.sub(r'\s+',' ',txt)
miss=[]
f=lambda x:'{:,}'.format(x)
def p1(x): return '%.1f'%(100*x)
for c in summ['cover_by_magnitude']+summ['cover_by_window']+[summ['cover_all']]:
    for s in (f(c['scored']),f(c['inside']),f(c['above']),f(c['below']),p1(c['share']),'%s to %s'%(p1(c['wilson'][0]),p1(c['wilson'][1])),'%s to %s'%(p1(c['lo']),p1(c['hi']))):
        if s not in txt: miss.append((c['cell'],s))
for c in summ['reliability']:
    for s in (f(c['scored']),f(c['occurred']),p1(c['stated_mean']),p1(c['share']),'%s to %s'%(p1(c['wilson'][0]),p1(c['wilson'][1]))):
        if s not in txt: miss.append((c['cell'],s))
print('page numbers not found as formatted:',miss[:20],len(miss))
