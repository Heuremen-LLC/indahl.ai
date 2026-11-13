"""build_planned.py (28 Oct 2026): ATLAS planned power plants from EIA-860M September 2026, Planned sheet. Outputs under electricity/: planned.json, planned_summary.json, planned_rows_text.txt, map_planned.svg."""
import json,os,sys,collections,html,math
H=os.path.dirname(os.path.abspath(__file__))+'/'
sys.path.insert(0,H); sys.path.insert(0,H+'electricity')
import mapkit as M
from xlsxread import rows
exec(open(H+'build_plants.py').read().split("def cat(")[0].split("CAT=")[1].join(["CAT=",""])) if False else None
CAT={'NG':'gas','BIT':'coal','SUB':'coal','LIG':'coal','RC':'coal','WC':'coal','ANT':'coal','SGC':'coal','NUC':'nuclear','WND':'wind','SUN':'solar','MWH':'storage','DFO':'oil','RFO':'oil','KER':'oil','JF':'oil','WO':'oil','PC':'oil'}
LABEL={'gas':'Natural gas','coal':'Coal','nuclear':'Nuclear','hydro':'Hydro','wind':'Wind','solar':'Solar','storage':'Storage','oil':'Petroleum','other':'Other'}
ORDER=['gas','coal','nuclear','hydro','wind','solar','storage','oil','other']
def cat(es,pm):
    if pm=='PS': return 'storage'
    if es=='WAT': return 'hydro'
    return CAT.get(es,'other')
GROUPS=[('build','Under construction or complete, not yet operating',('(U)','(V)','(TS)')),('approved','Approvals received, not under construction',('(T)',)),('pending','Approvals pending',('(L)',)),('planned','Planned, approvals not started',('(P)',))]
def grp(st):
    for k,_,codes in GROUPS:
        if any(st.startswith(c) for c in codes): return k
    return 'other'
G=rows(H+'electricity/raw/eia860m_sep2026.xlsx',1); h=G[2]; ix={c:i for i,c in enumerate(h)}
plants={}; gens=0
for x in G[3:]:
    if len(x)<21 or not isinstance(x[0],float): continue
    gens+=1; pid=int(x[ix['Plant ID']]); mw=float(x[ix['Nameplate Capacity (MW)']] or 0); f=cat(x[ix['Energy Source Code']],x[ix['Prime Mover Code']]); g=grp(x[ix['Status']])
    yr=int(x[ix['Planned Operation Year']]) if isinstance(x[ix['Planned Operation Year']],float) else None
    p=plants.setdefault(pid,dict(code=pid,name=x[ix['Plant Name']],state=x[ix['Plant State']],utility=x[ix['Entity Name']],lat=float(x[ix['Latitude']]),lon=float(x[ix['Longitude']]),mw={},status_mw={},years=[],generators=0))
    p['mw'][f]=p['mw'].get(f,0)+mw; p['status_mw'][g]=p['status_mw'].get(g,0)+mw; p['generators']+=1
    if yr: p['years'].append((yr,mw,f))
tot=collections.Counter(); fg=collections.defaultdict(collections.Counter); byyr=collections.defaultdict(collections.Counter); bystate=collections.defaultdict(collections.Counter)
for p in plants.values():
    p['total_mw']=round(sum(p['mw'].values()),1); p['dominant']=max(p['mw'],key=p['mw'].get); p['first_year']=min((y for y,_,_ in p['years']),default=None); p['last_year']=max((y for y,_,_ in p['years']),default=None)
    p['mw']={k:round(v,1) for k,v in p['mw'].items()}; p['status_mw']={k:round(v,1) for k,v in p['status_mw'].items()}
    for yr,mw,f in p['years']: byyr[min(max(yr,2026),2031)][f]+=mw
    for f,mw in p['mw'].items(): tot[f]+=mw; bystate[p['state']][f]+=mw
    for g,mw in p['status_mw'].items(): pass
# fuel x status from generators (recompute from rows for exact attribution)
for x in G[3:]:
    if len(x)<21 or not isinstance(x[0],float): continue
    fg[cat(x[ix['Energy Source Code']],x[ix['Prime Mover Code']])][grp(x[ix['Status']])]+=float(x[ix['Nameplate Capacity (MW)']] or 0)
grand=sum(tot.values())
op=sorted(plants.values(),key=lambda p:-p['total_mw'])
json.dump(dict(built='2026-10-28',source='EIA-860M September 2026, Planned sheet. Status groups: '+'; '.join(f"{n}: {', '.join(c)}" for k,n,c in GROUPS)+'. Plant fuel = fuel with the most planned capacity at the plant.',plants=op),open(H+'electricity/planned.json','w'))
drawn=[p for p in op if p['total_mw']>=25 and M.inbox(p['lat'],p['lon'])]
path=''.join('M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in (M.Pt(lo,la) for lo,la in r))+'Z' for poly in M.drawn.values() for pl in poly for r in pl)
dots=''
for p in sorted(drawn,key=lambda p:-p['total_mw']):
    x,y=M.Pt(p['lon'],p['lat']); r=min(1.3+math.sqrt(p['total_mw'])*0.11,9)
    ti=f'<title>{html.escape(p["name"])}, {html.escape(p["state"])}: {LABEL[p["dominant"]].lower()}, {p["total_mw"]:,.0f} MW planned</title>' if p['total_mw']>=100 else ''
    dots+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="f-{p["dominant"]}">{ti}</circle>' if ti else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="f-{p["dominant"]}"/>'
svg=f'<svg viewBox="0 0 {M.W} {M.HT:.0f}" role="img" aria-label="Map of the contiguous United States with planned power plants of 25 megawatts or more, colored by main fuel and sized by capacity, and AI data centers as rings" class="atlasmap plmap"><path d="{path}" class="st"/>{dots}{M.rings}</svg>'
open(H+'electricity/map_planned.svg','w').write(svg)
f1=lambda v:f'{v/1000:,.1f}'
lines=[]
for c in ORDER:
    if tot[c]>0: lines.append(f"FUEL {LABEL[c]} "+' '.join(f1(fg[c][k]) for k,_,_ in GROUPS)+f" {f1(tot[c])} {tot[c]/grand*100:.1f}")
for yr in sorted(byyr): lines.append(f"YEAR {'2031 and later' if yr==2031 else ('2026 or earlier' if yr==2026 else yr)} "+' '.join(f1(byyr[yr][c]) for c in ORDER)+f" {f1(sum(byyr[yr].values()))}")
for p in op[:20]: lines.append(f"PLANT {p['name']} {p['state']} {p['utility']} {LABEL[p['dominant']]} {p['total_mw']:,.0f} {p['first_year']}")
E=json.load(open(H+'electricity/electricity.json'))['states']
for ab,v in sorted(E.items(),key=lambda kv:kv[1]['name']):
    s=bystate.get(ab,{}); lines.append(f"STATE {v['name']} "+' '.join(f1(s.get(c,0)) for c in ORDER)+f" {f1(sum(s.values()))}")
open(H+'electricity/planned_rows_text.txt','w').write('\n'.join(lines)+'\n')
json.dump(dict(plants=len(plants),generators=gens,plants_drawn=len(drawn),total_gw=round(grand/1000,1)),open(H+'electricity/planned_summary.json','w'),separators=(',',':'),sort_keys=True)
print(len(plants),'planned plants',gens,'generators',len(drawn),'drawn',round(grand/1000,1),'GW'); print(lines[:9]); print([l for l in lines if l.startswith('YEAR')]); print(lines[len(lines)-52:len(lines)-50])
