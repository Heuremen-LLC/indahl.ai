"""build_plants.py (28 Oct 2026): ATLAS power plants. Input: EIA-860M September 2026 (Operating sheet, status operating, nameplate capacity) and EIA-860 2024 (Plant table for coordinates),
raw/states-10m.json, datacenters.json. Outputs under electricity/: plants.json, map_plants.svg, plants_summary.json, plants_rows_text.txt."""
import json,math,os,sys,collections,html
H=os.path.dirname(os.path.abspath(__file__))+'/'
sys.path.insert(0,H+'electricity'); from xlsxread import rows,hyperlinks
import re
CAT={'NG':'gas','BIT':'coal','SUB':'coal','LIG':'coal','RC':'coal','WC':'coal','ANT':'coal','SGC':'coal','NUC':'nuclear','WND':'wind','SUN':'solar','MWH':'storage',
     'DFO':'oil','RFO':'oil','KER':'oil','JF':'oil','WO':'oil','PC':'oil'}
LABEL={'gas':'Natural gas','coal':'Coal','nuclear':'Nuclear','hydro':'Hydro','wind':'Wind','solar':'Solar','storage':'Storage','oil':'Petroleum','other':'Other'}
ORDER=['gas','coal','nuclear','hydro','wind','solar','storage','oil','other']
def cat(es,pm):
    if pm=='PS': return 'storage'
    if es=='WAT': return 'hydro'
    return CAT.get(es,'other')
P=rows(H+'electricity/raw/eia860/2___Plant_Y2024.xlsx',0); ph=P[1]; pi={h:i for i,h in enumerate(ph)}
def fl(v):
    try: return float(v)
    except (TypeError,ValueError): return None
plants={}
for x in P[2:]:
    if len(x)<12 or not isinstance(x[0],float): continue
    plants[int(x[pi['Plant Code']])]=dict(code=int(x[pi['Plant Code']]),name=x[pi['Plant Name']],state=x[pi['State']],county=x[pi['County']],lat=fl(x[pi['Latitude']]),lon=fl(x[pi['Longitude']]),utility=x[pi['Utility Name']],mw={},generators=0)
G=rows(H+'electricity/raw/eia860m_sep2026.xlsx',0); gh=G[2]; gi={h:i for i,h in enumerate(gh)}
HL=hyperlinks(H+'electricity/raw/eia860m_sep2026.xlsx',0); COORD={}   # the Google Map link in each row carries the plant's coordinates
for ref,t in HL.items():
    if not ref.startswith('E'): continue
    r=int(ref[1:]); m=re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)',t)
    if m and r-1<len(G) and G[r-1] and isinstance(G[r-1][0],float): COORD[int(G[r-1][gi['Plant ID']])]=(float(m.group(1)),float(m.group(2)))   # EIA-860M, September 2026, Operating sheet
for x in G[3:]:
    if len(x)<24 or not isinstance(x[0],float) or not str(x[gi['Status']]).startswith('(OP)'): continue
    p=plants.get(int(x[gi['Plant ID']]))
    if not p:
        p=plants[int(x[gi['Plant ID']])]=dict(code=int(x[gi['Plant ID']]),name=x[gi['Plant Name']],state=x[gi['Plant State']],county=x[gi['County']],lat=None,lon=None,utility=x[gi['Entity Name']],mw={},generators=0)
    p['utility']=x[gi['Entity Name']]; p['name']=x[gi['Plant Name']]; p['state']=x[gi['Plant State']]
    if p['code'] in COORD: p['lat'],p['lon']=COORD[p['code']]
    c=cat(x[gi['Energy Source Code']],x[gi['Prime Mover Code']]); mw=float(x[gi['Nameplate Capacity (MW)']] or 0)
    p['mw'][c]=p['mw'].get(c,0.0)+mw; p['generators']+=1
op=[]
for p in plants.values():
    if not p['mw']: continue
    p['total_mw']=round(sum(p['mw'].values()),1); p['mw']={k:round(v,1) for k,v in p['mw'].items()}; p['dominant']=max(p['mw'],key=p['mw'].get); op.append(p)
# totals
tot=collections.Counter(); cnt=collections.Counter(); bystate=collections.defaultdict(collections.Counter)
for p in op:
    for c,v in p['mw'].items(): tot[c]+=v; bystate[p['state']][c]+=v
    cnt[p['dominant']]+=1
grand=sum(tot.values())
json.dump(dict(built='2026-10-28',source='EIA-860M September 2026 (operating generators, nameplate capacity in MW), with plant coordinates from the map link in each row (EIA-860 2024 where a row has none). Fuel group from Energy Source 1 and Prime Mover: '+'; '.join(f'{k}={v}' for k,v in CAT.items())+'; WAT=hydro (pumped storage PS counts as storage); other = every remaining code.',plants=sorted(op,key=lambda p:-p['total_mw'])),open(H+'electricity/plants.json','w'))
# map
NAMES={}
import importlib.util
topo=json.load(open(H+'raw/states-10m.json')); sc,tr=topo['transform']['scale'],topo['transform']['translate']
arcs=[]
for a in topo['arcs']:
    x=y=0; pts=[]
    for dx,dy in a: x+=dx; y+=dy; pts.append((x*sc[0]+tr[0],y*sc[1]+tr[1]))
    arcs.append(pts)
def ring(idx):
    pts=[]
    for i in idx:
        a=arcs[i] if i>=0 else arcs[~i][::-1]
        pts+=a if not pts else a[1:]
    return pts
phi1,phi2,phi0,lam0=map(math.radians,(29.5,45.5,37.5,-96.0))
n=(math.sin(phi1)+math.sin(phi2))/2; C=math.cos(phi1)**2+2*n*math.sin(phi1); r0=math.sqrt(C-2*n*math.sin(phi0))/n
def proj(lon,lat):
    ph,la=math.radians(lat),math.radians(lon); r=math.sqrt(C-2*n*math.sin(ph))/n; th=n*(la-lam0)
    return (r*math.sin(th), -(r0-r*math.cos(th)))
skip={'02','15','72','78','60','66','69'}; polys=[]
for g in topo['objects']['states']['geometries']:
    if g['id'] in skip: continue
    rings=g['arcs'] if g['type']=='Polygon' else [r for p in g['arcs'] for r in p]
    polys.append([ring(r) for r in rings])
allp=[proj(lo,la) for p in polys for r in p for lo,la in r]; xs=[p[0] for p in allp]; ys=[p[1] for p in allp]; x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
W=960; SC=(W-20)/(x1-x0); HT=(y1-y0)*SC+20
def Pt(lon,lat): x,y=proj(lon,lat); return (10+(x-x0)*SC,10+(y-y0)*SC)
def inbox(lat,lon): return 24.3<=lat<=49.6 and -125.2<=lon<=-66.5
path=''.join('M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in (Pt(lo,la) for lo,la in r))+'Z' for p in polys for r in p)
MIN=25.0; drawn=[p for p in op if p['total_mw']>=MIN and p['lat'] is not None and inbox(p['lat'],p['lon'])]
noloc=sum(1 for p in op if p['lat'] is None)
dots=''
for p in sorted(drawn,key=lambda p:-p['total_mw']):
    x,y=Pt(p['lon'],p['lat']); r=min(1.3+math.sqrt(p['total_mw'])*0.11,9)
    ti=f'<title>{html.escape(p["name"])}, {html.escape(p["state"])}: {LABEL[p["dominant"]].lower()}, {p["total_mw"]:,.0f} MW</title>' if p['total_mw']>=100 else ''
    dots+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="f-{p["dominant"]}">{ti}</circle>' if ti else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="f-{p["dominant"]}"/>'
dc=json.load(open(H+'datacenters.json')); rings=''
for r in sorted([e for e in dc['epoch'] if e['lat'] is not None and inbox(e['lat'],e['lon'])],key=lambda e:-(e['mw'] or 0)):
    x,y=Pt(r['lon'],r['lat']); rings+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3+math.sqrt(r["mw"] or 20)*0.42:.1f}" class="e"><title>{html.escape(r["name"])}'+(f', {r["mw"]:.0f} MW' if r['mw'] else '')+'</title></circle>'
svg=f'<svg viewBox="0 0 {W} {HT:.0f}" role="img" aria-label="Map of the contiguous United States with operating power plants of {MIN:.0f} megawatts or more, colored by main fuel and sized by capacity, and AI data centers as rings" class="atlasmap plmap"><path d="{path}" class="st"/>{dots}{rings}</svg>'
open(H+'electricity/map_plants.svg','w').write(svg)
# rows for the page and the ledger
f=lambda v:f'{v:,.1f}'
rowsfuel=[(c,tot[c]/1000,cnt[c],tot[c]/grand*100) for c in ORDER if tot[c]>0]
top=sorted(op,key=lambda p:-p['total_mw'])[:20]
lines=[f"FUEL {LABEL[c]} {f(gw)} {cnt[c]:,} {sh:.1f}" for c,gw,cn,sh in rowsfuel]
lines+=[f"PLANT {p['name']} {p['state']} {p['utility']} {LABEL[p['dominant']]} {p['total_mw']:,.0f}" for p in top]
SN={}
E=json.load(open(H+'electricity/electricity.json'))
for ab,v in sorted(E['states'].items(),key=lambda kv:kv[1]['name']):
    s=bystate.get(ab,{}); lines.append(f"STATE {v['name']} "+' '.join(f"{s.get(c,0)/1000:,.1f}" for c in ORDER)+f" {sum(s.values())/1000:,.1f}")
open(H+'electricity/plants_rows_text.txt','w').write('\n'.join(lines)+'\n')
json.dump(dict(plants_operating=len(op),plants_drawn=len(drawn),plants_without_location=noloc,min_mw_drawn=MIN,total_gw=round(grand/1000,1),generators_operating=sum(p['generators'] for p in op),fuel=[dict(fuel=c,gw=round(gw,1),plants=cn,share=round(sh,1)) for c,gw,cn,sh in rowsfuel]),open(H+'electricity/plants_summary.json','w'),separators=(',',':'),sort_keys=True)
print(len(op),'operating plants',len(drawn),'drawn (>=%d MW)'%MIN,round(grand/1000,1),'GW'); print(lines[:9]); print(lines[9:12])
