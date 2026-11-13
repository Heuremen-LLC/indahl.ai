import json,time,urllib.request,urllib.parse
UA='heuremen-neo-referee/0.1'
d=json.load(open('/Users/heuremen/bones-forge/neo_index/data/neo.json'))['rows']
H=[r for r in d if r['headline']]
out=[r for r in H if r['outcome'] in('ABOVE','BELOW')]
cons=[r for r in H if r['outcome']=='CONSISTENT' and r['stated_copy'][:8]!='20240209'][::40][:3]
cons+= [r for r in H if r['outcome']=='CONSISTENT' and r['stated_copy'][:8]=='20240209' and r['lead_days']>365][::30][:2]
def get(u):
    time.sleep(1.5)
    req=urllib.request.Request(u,headers={'User-Agent':UA})
    return json.loads(urllib.request.urlopen(req,timeout=60).read())
res=[]
for r in out+cons:
    des=r['latest_des']; jd=r['stated_jd']
    a=time.strftime('%Y-%m-%d',time.gmtime((jd-8-2440587.5)*86400)); b=time.strftime('%Y-%m-%d',time.gmtime((jd+8-2440587.5)*86400))
    o=dict(des=r['des'],latest_des=des,approach=r['approach'],outcome=r['outcome'],stored=(r['latest_orbit'],r['latest_min'],r['latest'],r['latest_max']))
    try:
        c=get('https://ssd-api.jpl.nasa.gov/cad.api?des=%s&date-min=%s&date-max=%s&dist-max=0.5'%(urllib.parse.quote(des),a,b))
        f=c['fields']; rows=[dict(zip(f,x)) for x in c['data']]
        x=min(rows,key=lambda x:abs(float(x['jd'])-jd)) if rows else None
        o['live_cad']=(x['orbit_id'],float(x['dist_min']),float(x['dist']),float(x['dist_max'])) if x else None
    except Exception as e: o['live_cad']='ERR %s'%e
    try:
        s=get('https://ssd-api.jpl.nasa.gov/sbdb.api?des=%s'%urllib.parse.quote(des))
        orb=s.get('orbit',{}); o['live_sbdb']=(orb.get('orbit_id'),orb.get('soln_date'),orb.get('condition_code'),orb.get('data_arc'))
    except Exception as e: o['live_sbdb']='ERR %s'%e
    st=o['stored']; lc=o['live_cad']
    o['cad_match']= isinstance(lc,tuple) and str(lc[0])==str(st[0]) and all(abs(lc[i]-st[i])<=1e-9 for i in (1,2,3))
    o['sbdb_orbit_match']= isinstance(o['live_sbdb'],tuple) and str(o['live_sbdb'][0])==str(st[0])
    res.append(o); print(o['des'],o['approach'],o['outcome'],'cad',o['cad_match'],'sbdb',o['sbdb_orbit_match'],lc if not o['cad_match'] else '',o['live_sbdb'] if not o['sbdb_orbit_match'] else '',flush=True)
json.dump(res,open('/Users/heuremen/bones-forge/neo_index_referee/live_check.json','w'),indent=1)
