import json,re
src=open('rates.py').read().split("for ev in('divorce'")[0]; ns={}; exec(src,ns); rows=ns['rows']; F=ns['F']
N=json.load(open('nchs_pos.json'))
pop={}
for y in range(2010,2025):
    if y==2020: continue
    r=json.load(open('/Users/heuremen/bones-forge/fidelity_index/data/raw/acs_%d.json'%y))['rows']; h=r[0]
    for x in r[1:]: d=dict(zip(h,x)); pop[(d['NAME'],y)]=float(d['B01003_001E'])
out={}
for ev in('divorce','marriage'):
    Rt=rows(F%ev); h=next(r for r in Rt if r[1:2]==['2024']); rate={r[0].strip():dict(zip(h[1:],r[1:])) for r in Rt[Rt.index(h)+1:] if r}
    print(ev)
    for y in range(2012,2020):
        fit={}
        for off in (-1,0,1):
            ok=tot=0
            for st,v in N[ev].items():
                if st=='United States' or st not in rate: continue
                n=v[y+off-2000]; rt=rate[st].get(str(y))
                if n is None or not rt or not re.fullmatch(r'[\d.]+',rt) or (st,y) not in pop: continue
                tot+=1; ok+=abs(n/pop[(st,y)]*1000-float(rt))<=0.1+1e-9
            fit[off]=(ok,tot)
        print(' rate yr',y,fit)
