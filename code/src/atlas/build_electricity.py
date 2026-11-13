"""build_electricity.py (28 Oct 2026): ATLAS electricity layer. Inputs (all U.S. Energy Information Administration, public):
  electricity/raw/f861_2024/Sales_Ult_Cust_2024.xlsx  EIA-861 retail sales by utility, 2024 (revenue, sales, customers by sector)
  electricity/raw/annual_generation_state.xlsx        State Historical Tables, net generation by state and energy source (2024 used)
  raw/states-10m.json (us-atlas, Census boundaries), datacenters.json (ATLAS data centers).
Outputs: electricity/electricity.json, electricity/utilities.json, electricity/map_industrial.svg, electricity/map_commercial.svg, electricity/summary.json.
Price = revenue / sales, in cents per kilowatthour, by EIA's own rule (note under the 861 table): revenue sums Parts A, B, C and D, sales sum Parts A, B and D."""
import json,math,os,sys,collections,html,datetime
H=os.path.dirname(os.path.abspath(__file__))+'/'
sys.path.insert(0,H+'electricity'); from xlsxread import rows
NAMES={'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
ABBR2NAME={v:k for k,v in NAMES.items()}
num=lambda v: v if isinstance(v,(int,float)) else 0.0
# ---------- EIA-861 sales
S=rows(H+'electricity/raw/f861_2024/Sales_Ult_Cust_2024.xlsx',0)
data=[x for x in S[3:] if x and isinstance(x[0],float)]
SEC={'residential':(9,10,11),'commercial':(12,13,14),'industrial':(15,16,17),'transportation':(18,19,20),'total':(21,22,23)}
def agg(rs):
    out={}
    for sec,(ri,si,ci) in SEC.items():
        rev=sum(num(x[ri]) for x in rs if x[3] in 'ABCD'); sal=sum(num(x[si]) for x in rs if x[3] in 'ABD')
        out[sec]=dict(revenue_k=round(rev,1),sales_mwh=round(sal,1),price=(round(rev/sal*100,2) if sal>0 else None))
    return out
byst=collections.defaultdict(list)
for x in data: byst[x[6]].append(x)
states={}
for st,rs in byst.items():
    if st not in ABBR2NAME: continue
    own=collections.defaultdict(float)
    for x in rs:
        if x[3] in 'ABD': own[x[7] or ('EIA adjustment' if x[1]==99999 else 'Not stated')]+=num(x[22])
    states[st]=dict(name=ABBR2NAME[st],sectors=agg(rs),ownership_sales_twh={k:round(v/1e6,3) for k,v in sorted(own.items(),key=lambda kv:-kv[1])})
us_sec=agg([x for x in data if x[6] in ABBR2NAME])
own_us=collections.defaultdict(lambda:[set(),0.0])
for x in data:
    if x[6] in ABBR2NAME and x[3] in 'ABD': o=own_us[x[7] or ('EIA adjustment' if x[1]==99999 else 'Not stated')]; o[0].add(x[1]); o[1]+=num(x[22])
ownership=[dict(type=k,utilities=len(v[0]),sales_twh=round(v[1]/1e6,1)) for k,v in sorted(own_us.items(),key=lambda kv:-kv[1][1])]
# ---------- utilities: bundled (Part A) rows, one per utility and state
utilities=[]
for x in data:
    if x[3]!='A' or x[6] not in ABBR2NAME: continue
    row=dict(utility_number=int(x[1]),name=x[2],state=x[6],ownership=x[7] or ('EIA adjustment' if x[1]==99999 else 'Not stated'),ba_code=x[8] or '',data_type=x[5])
    for sec,(ri,si,ci) in SEC.items():
        rev,sal=num(x[ri]),num(x[si]); row[sec+'_price']=round(rev/sal*100,2) if sal>0 else None; row[sec+'_sales_mwh']=round(sal,1)
    utilities.append(row)
# ---------- generation
G=rows(H+'electricity/raw/annual_generation_state.xlsx',0)
gen=collections.defaultdict(dict)
for x in G[2:]:
    if x and isinstance(x[0],float) and x[0]==2024.0 and x[2]=='Total Electric Power Industry': gen[x[1]][x[3]]=x[4]
GROUP=[('coal','Coal'),('gas','Natural Gas'),('nuclear','Nuclear'),('hydro','Hydroelectric Conventional'),('wind','Wind'),('solar','Solar Thermal and Photovoltaic')]
def genmix(d):
    tot=d.get('Total'); 
    if not tot or tot<=0: return None
    g={k:d.get(src,0.0) for k,src in GROUP}; g['other']=tot-sum(g.values()); g['total']=tot
    return dict(mwh={k:round(v) for k,v in g.items()},share={k:round(v/tot*100,1) for k,v in g.items() if k!='total'})
for st in states: states[st]['generation']=genmix(gen.get(st,{}))
us_gen=genmix(gen.get('US-Total',{}))
# ---------- data centers per state (point in polygon, outer rings)
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
shapes={}
for g in topo['objects']['states']['geometries']:
    ab=NAMES.get(g['properties']['name'])
    if not ab: continue
    polys=[g['arcs']] if g['type']=='Polygon' else g['arcs']
    shapes[ab]=[[ring(r) for r in p] for p in polys]
def inring(lon,lat,r):
    c=False; j=len(r)-1
    for i in range(len(r)):
        xi,yi=r[i]; xj,yj=r[j]
        if (yi>lat)!=(yj>lat) and lon<(xj-xi)*(lat-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def state_of(lon,lat):
    for ab,polys in shapes.items():
        for p in polys:
            if inring(lon,lat,p[0]): return ab
    return None
dc=json.load(open(H+'datacenters.json'))
cnt=collections.defaultdict(lambda:dict(osm_features=0,epoch_sites=0,epoch_mw=0.0)); unplaced=dict(osm=0,epoch=0)
for r in dc['osm']:
    s=state_of(r['lon'],r['lat'])
    if s: cnt[s]['osm_features']+=1
    else: unplaced['osm']+=1
for r in dc['epoch']:
    if r['lat'] is None: unplaced['epoch']+=1; continue
    s=state_of(r['lon'],r['lat'])
    if s: cnt[s]['epoch_sites']+=1; cnt[s]['epoch_mw']+=r['mw'] or 0
    else: unplaced['epoch']+=1
for st in states: c=cnt.get(st,dict(osm_features=0,epoch_sites=0,epoch_mw=0.0)); states[st]['data_centers']=dict(osm_features=c['osm_features'],epoch_sites=c['epoch_sites'],epoch_mw=round(c['epoch_mw']))
# ---------- maps
phi1,phi2,phi0,lam0=map(math.radians,(29.5,45.5,37.5,-96.0))
n=(math.sin(phi1)+math.sin(phi2))/2; C=math.cos(phi1)**2+2*n*math.sin(phi1); r0=math.sqrt(C-2*n*math.sin(phi0))/n
def proj(lon,lat):
    ph,la=math.radians(lat),math.radians(lon); r=math.sqrt(C-2*n*math.sin(ph))/n; th=n*(la-lam0)
    return (r*math.sin(th), -(r0-r*math.cos(th)))
drawn={ab:p for ab,p in shapes.items() if ab not in('AK','HI')}
allp=[proj(lo,la) for p in drawn.values() for poly in p for r in poly for lo,la in r]
xs=[p[0] for p in allp]; ys=[p[1] for p in allp]; x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
W=960; SC=(W-20)/(x1-x0); HT=(y1-y0)*SC+20
def Pt(lon,lat): x,y=proj(lon,lat); return (10+(x-x0)*SC, 10+(y-y0)*SC)
def inbox(lat,lon): return 24.3<=lat<=49.6 and -125.2<=lon<=-66.5
dots=''.join(f'<circle cx="{Pt(r["lon"],r["lat"])[0]:.1f}" cy="{Pt(r["lon"],r["lat"])[1]:.1f}" r="1.5" class="o"/>' for r in dc['osm'] if inbox(r['lat'],r['lon']))
rings=''
for r in sorted([e for e in dc['epoch'] if e['lat'] is not None and inbox(e['lat'],e['lon'])],key=lambda e:-(e['mw'] or 0)):
    x,y=Pt(r['lon'],r['lat']); rings+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3+math.sqrt(r["mw"] or 20)*0.42:.1f}" class="e"><title>{html.escape(r["name"])}'+(f', {r["mw"]:.0f} MW' if r['mw'] else '')+'</title></circle>'
SMALL={'CT','RI','NJ','DE','MD','DC','MA','NH','VT'}
def cent(polys):
    best=max(polys,key=lambda p:len(p[0])); pts=[Pt(lo,la) for lo,la in best[0]]
    return (min(p[0] for p in pts)+max(p[0] for p in pts))/2,(min(p[1] for p in pts)+max(p[1] for p in pts))/2
maps={}; legends={}
for sec in ('industrial','commercial'):
    vals=sorted(states[a]['sectors'][sec]['price'] for a in drawn if a in states and states[a]['sectors'][sec]['price'])
    q=[vals[int(len(vals)*k/5)] for k in (1,2,3,4)]; edges=[round(v,1) for v in q]
    def cls(v): return 1+sum(v>=e for e in edges)
    body=''; labels=''
    for ab in sorted(drawn):
        st=states.get(ab); v=st['sectors'][sec]['price'] if st else None
        d=''.join('M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in (Pt(lo,la) for lo,la in r))+'Z' for poly in drawn[ab] for r in poly)
        c=cls(v) if v else 0
        body+=f'<path d="{d}" class="s{c}"><title>{ABBR2NAME[ab]}: {v:.1f} cents/kWh</title></path>' if v else f'<path d="{d}" class="s0"/>'
        if v and ab not in SMALL: x,y=cent(drawn[ab]); labels+=f'<text x="{x:.0f}" y="{y+3:.0f}" class="lb">{v:.1f}</text>'
    maps[sec]=f'<svg viewBox="0 0 {W} {HT:.0f}" role="img" aria-label="Map of the contiguous United States shaded by the average price of electricity sold to {sec} customers in 2024, with data center sites over it" class="atlasmap elmap">{body}{labels}{dots}{rings}</svg>'
    legends[sec]=[f'under {edges[0]:.1f}']+[f'{edges[i]:.1f} to {edges[i+1]:.1f}' for i in range(3)]+[f'{edges[3]:.1f} and over']
    open(H+f'electricity/map_{sec}.svg','w').write(maps[sec])
out=dict(built=datetime.date(2026,10,28).isoformat(),price_year=2024,generation_year=2024,unit='cents per kilowatthour',
   method='Average price = revenue divided by sales. Revenue sums Parts A, B, C and D of the EIA-861 sales table and sales sum Parts A, B and D, as the note under the table says. Generation shares are net generation by energy source over total net generation, Total Electric Power Industry, utility-scale. Other is total minus the named sources and includes petroleum, biomass, geothermal, other gases and pumped storage.',
   sources=dict(sales='EIA-861 annual electric power industry report, Sales to Ultimate Customers 2024 (Sales_Ult_Cust_2024.xlsx)',generation='EIA State Historical Tables, net generation by state and energy source (annual_generation_state.xlsx)'),
   us=dict(sectors=us_sec,generation=us_gen,ownership=ownership),states=states,legend=legends,unplaced_data_centers=unplaced)
json.dump(out,open(H+'electricity/electricity.json','w'),indent=1); json.dump(dict(year=2024,note='Bundled (EIA-861 Part A) rows, one per utility and state. Price in cents per kilowatthour, revenue divided by sales.',utilities=utilities),open(H+'electricity/utilities.json','w'))
tot_own=sum(o['sales_twh'] for o in ownership)
summ=dict(states=len(states),utilities=len(utilities),us_prices={k:v['price'] for k,v in us_sec.items()},ownership=[dict(o,share=round(o['sales_twh']/tot_own*100,1)) for o in ownership],us_generation_twh={k:round(v/1e6,1) for k,v in us_gen['mwh'].items()},us_generation_share=us_gen['share'])
json.dump(summ,open(H+'electricity/summary.json','w'),separators=(',',':'),sort_keys=True)
print(summ['us_prices'],len(states),'states',len(utilities),'bundled utility rows'); print(ownership[:4]); print(us_gen['share']); print(unplaced)
for sec in legends: print(sec,legends[sec])
