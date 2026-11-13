"""build_atlasmap.py (30 Oct 2026): the ATLAS map with switchable layers, and the cost-to-scale arithmetic for the AI data centers.
Inputs (all already in atlas/): datacenters.json (OpenStreetMap and Epoch AI, build_atlas.py), epoch_fixes.json (placement corrections, this script only),
electricity/electricity.json (EIA-861 2024 prices, build_electricity.py), electricity/carbon.json (EPA eGRID2023), electricity/plants.json (EIA-860M operating),
electricity/planned.json (EIA-860M planned), raw/states-10m.json through mapkit.py (same Albers projection as map.svg).
Outputs: electricity/scale.json, scale_summary.json, scale_rows_text.txt, and the page fragments atlasmap_fragment.html, scale_fragment.html, atlasmap.css, atlasmap_report.txt.
The layers switch with CSS only (radio buttons and checkboxes, :has()), because indahl.ai pages allow no inline script. Run: python3 -I build_atlasmap.py"""
import json,math,os,sys,re,html,collections,datetime
from decimal import Decimal as D,ROUND_HALF_UP
H=os.path.dirname(os.path.abspath(__file__))+'/'
sys.path.insert(0,H); import mapkit as M
E=H+'electricity/'
EL=json.load(open(E+'electricity.json')); CB=json.load(open(E+'carbon.json')); PL=json.load(open(E+'plants.json')); PN=json.load(open(E+'planned.json'))
DC=json.load(open(H+'datacenters.json')); FX={f['name']:f for f in json.load(open(H+'epoch_fixes.json'))['fixes']}
_d=datetime.date.fromisoformat(DC['pulled']); PULLED=f'{_d.day} {_d.strftime("%b %Y")}'
esc=html.escape
REPORT=[]
def say(*a):
    s=' '.join(str(x) for x in a); REPORT.append(s); print(s)
# ---------------------------------------------------------------- placement of the Epoch sites
def inring(lon,lat,r):
    c=False; j=len(r)-1
    for i in range(len(r)):
        xi,yi=r[i]; xj,yj=r[j]
        if (yi>lat)!=(yj>lat) and lon<(xj-xi)*(lat-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def state_of(lon,lat):
    for ab,polys in M.shapes.items():
        for p in polys:
            if inring(lon,lat,p[0]): return ab
    return None
FULL=sorted((n for n in M.NAMES if n!='District of Columbia'),key=len,reverse=True)
def addr_state(a):
    """The state a record's own address text names, or None when it names none or more than one."""
    if not a: return None
    found=set(); t=a
    for nm in FULL:
        pat=r'\b'+re.escape(nm)+r'\b'
        if re.search(pat,t,re.I): found.add(M.NAMES[nm]); t=re.sub(pat,' ',t,flags=re.I)
    for m in re.finditer(r'(?<![A-Za-z])([A-Z]{2})\b[,.\s]*\d{5}',a):
        if m.group(1) in M.ABBR2NAME: found.add(m.group(1))
    return found.pop() if len(found)==1 else None
sites=[]
for e in DC['epoch']:
    fx=FX.get(e['name']); lat,lon=(fx['lat'],fx['lon']) if fx else (e['lat'],e['lon'])
    ats=addr_state(e['address']); st=None; how=None
    if lat is not None:
        st=state_of(lon,lat); how='point, corrected' if fx else 'point'
        if st and ats and st!=ats: sys.exit(f'CONFLICT {e["name"]}: point is in {st}, address text names {ats}')
        if fx and fx['state']!=st: sys.exit(f'FIX for {e["name"]} lands in {st}, not {fx["state"]}')
    if st is None and ats: st=ats; how='address text'
    sites.append(dict(name=e['name'],owner=(e['operator'] or '').strip(),mw=e['mw'],h100e=e['h100e'],lat=lat,lon=lon,address=e['address'],state=st,how=how))
# ---------------------------------------------------------------- cost to scale: stated megawatts x 8,760 hours x the state's 2024 average price
HRS=D(8760); ST=EL['states']
def usd(mw,cents): return D(str(mw))*HRS*D(str(cents))*D(10)      # MW x h = MWh, x 1000 = kWh, x cents / 100 = dollars, so x 10 x cents
def q(x,p): return x.quantize(D(p),ROUND_HALF_UP)
def rate(st,sec): return ST[st]['sectors'][sec]['price']
for s in sites:
    s['cost_i']=s['cost_c']=None
    if s['state'] and s['mw']:
        s['rate_i']=rate(s['state'],'industrial'); s['rate_c']=rate(s['state'],'commercial')
        s['mwh']=D(str(s['mw']))*HRS; s['cost_i']=usd(s['mw'],s['rate_i']); s['cost_c']=usd(s['mw'],s['rate_c'])
counted=[s for s in sites if s['cost_i'] is not None]; counted.sort(key=lambda s:(-s['cost_i'],s['name']))
withmw=[s for s in sites if s['mw']]; placed=[s for s in sites if s['state']]
nopl_mw=[s for s in withmw if not s['state']]; nopl=[s for s in sites if not s['state']]
tot_i=sum(s['cost_i'] for s in counted); tot_c=sum(s['cost_c'] for s in counted); tot_mw=sum(D(str(s['mw'])) for s in counted); tot_mwh=tot_mw*HRS
mil=lambda x:q(x/D(1000000),'0.1')
say('sites',len(sites),'with stated power',len(withmw),'placed',len(placed),'counted',len(counted),'stated but not placed',len(nopl_mw),[s['name'] for s in nopl_mw],'not placed at all',len(nopl))
say('how placed',collections.Counter(s['how'] for s in placed))
say('total industrial USD',tot_i,'= million',mil(tot_i),'; commercial',mil(tot_c),'; MW',tot_mw,'; MWh',tot_mwh)
rounded_sum=sum(mil(s['cost_i']) for s in counted); say('sum of the rows as printed',rounded_sum,'against the total as printed',mil(tot_i))
f1=lambda x:f'{x:,.1f}'
def fmw(mw):
    d=D(str(mw)).normalize(); t=f'{d:f}'
    if '.' in t: t=t.rstrip('0').rstrip('.')
    n=D(t); return f'{n:,.2f}'.rstrip('0').rstrip('.') if n!=n.to_integral() else f'{int(n):,}'
bystate=collections.OrderedDict()
for s in sorted(counted,key=lambda s:M.ABBR2NAME[s['state']]):
    b=bystate.setdefault(s['state'],dict(sites=0,mw=D(0),cost_i=D(0))); b['sites']+=1; b['mw']+=D(str(s['mw'])); b['cost_i']+=s['cost_i']
# records that land on the same map point
pts=collections.defaultdict(list)
for s in sites:
    if s['lat'] is not None: pts[(round(s['lat'],5),round(s['lon'],5))].append(s)
shared=[g for g in pts.values() if len(g)>1]
say('records sharing a map point',[[x['name'] for x in g] for g in shared])
shared_mw=[g for g in shared if sum(1 for x in g if x['mw'])>1]
# ---------------------------------------------------------------- lines the ledger greps (the page prints the same text)
def owner(s): return s['owner'] or 'Not listed'
lines=[]
for s in counted: lines.append(f"SITE {s['name']} {owner(s)} {s['state']} {fmw(s['mw'])} {s['rate_i']:.2f} {f1(mil(s['cost_i']))}")
for s in nopl_mw: lines.append(f"UNPLACED {s['name']} {owner(s)} {fmw(s['mw'])}")
for ab,b in bystate.items(): lines.append(f"STATE {M.ABBR2NAME[ab]} {rate(ab,'industrial'):.2f} {rate(ab,'commercial'):.2f} {b['sites']} {fmw(b['mw'])} {f1(mil(b['cost_i']))}")
T=dict(sites_us=len(sites),with_power=len(withmw),placed=len(placed),counted=len(counted),not_counted_with_power=len(nopl_mw),with_power_mw_not_counted=fmw(sum(D(str(s['mw'])) for s in nopl_mw)),
       not_placed=len(nopl),without_power=len(sites)-len(withmw),total_mw=fmw(tot_mw),total_twh=f'{q(tot_mwh/D(1000000),"0.1")}',total_musd=f1(mil(tot_i)),total_busd=f'{q(tot_i/D(1000000000),"0.1")}',total_musd_commercial=f1(mil(tot_c)),total_busd_commercial=f'{q(tot_c/D(1000000000),"0.1")}',
       states_with_sites=len(bystate))
# 10 Nov 2026 (newsletter audit): a figure beside the total, never in it. The sites with a stated power and no address are left out of the total,
# because the rule places a site only from its map point or its own address text. Their own cited sources name the state of each, so the page
# also prints what the total would be with them placed there. NAMED is the state each record's cited source names, read by hand on 10 Nov 2026.
NAMED={'Google Mesa':('AZ','its cited DCD article on the Mesa campus in Arizona'),'Google Kansas City East':('MO','its cited Hunt Midwest press release, Hunt Midwest Business Center, Kansas City, Missouri'),'Google Storey County':('NV','its cited Nevada Division of Environmental Protection permit application')}
named=[s for s in nopl_mw if s['name'] in NAMED]
add_i=sum(usd(s['mw'],rate(NAMED[s['name']][0],'industrial')) for s in named)
T.update(beside_named_sites=len(named),beside_named_mw=fmw(sum(D(str(s['mw'])) for s in named)),beside_named_add_musd=f1(mil(add_i)),beside_total_musd=f1(mil(tot_i+add_i)),beside_total_busd=f'{q((tot_i+add_i)/D(1000000000),"0.1")}',
         beside_rule='not in the total: the three sites placed in the state their own cited source names, at that state\'s 2024 industrial price, defined 10 Nov 2026')
say('beside: named sites',[(s['name'],NAMED[s['name']][0],rate(NAMED[s['name']][0],'industrial')) for s in named],'add million',mil(add_i),'total million',mil(tot_i+add_i))
lines.append('TOTAL '+f"{T['counted']} {T['total_mw']} {T['total_twh']} {T['total_musd']}")
_f0=counted[0]; _mwh=D(str(_f0['mw']))*HRS
lines.append(f"EXAMPLE {_f0['name']} {fmw(_f0['mw'])} {_mwh:,.0f} {_f0['rate_i']:.2f} {f1(mil(_f0['cost_i']))}")
lines.append('TOTALCOMMERCIAL '+T['total_musd_commercial'])
lines.append('BESIDE '+f"{T['beside_named_sites']} {T['beside_named_mw']} {T['beside_named_add_musd']} {T['beside_total_musd']}")
lines.append('COUNTS '+f"{T['sites_us']} {T['with_power']} {T['placed']} {T['counted']} {T['not_counted_with_power']} {T['with_power_mw_not_counted']} {T['not_placed']} {T['without_power']}")
open(E+'scale_rows_text.txt','w').write('\n'.join(lines)+'\n')
json.dump(dict(built=datetime.date(2026,10,30).isoformat(),hours_per_year=8760,price_year=2024,unit_price='cents per kilowatthour',unit_cost='dollars per year',
  method='For each Epoch AI site that states a current power and sits in a state: stated megawatts x 8,760 hours x the average price paid by industrial customers in that state in 2024 (EIA-861 sales table, revenue divided by sales), expressed in dollars. The commercial column is the same arithmetic at the state commercial price. This is full stated power for a full year at a state average price. It is not any site\'s contract price or bill and not a forecast. The state comes from the geocoded point, or from the state named in Epoch\'s own address text where the geocoders found no point.',
  sources=dict(power='Epoch AI, AI data centers (CC BY 4.0), field Current power (MW), pulled '+PULLED,price='EIA-861 2024, Sales to Ultimate Customers, computed in electricity/electricity.json by build_electricity.py'),
  corrections=list(FX.values()),totals=T,
  states={ab:dict(name=M.ABBR2NAME[ab],industrial_cents_kwh=rate(ab,'industrial'),commercial_cents_kwh=rate(ab,'commercial'),sites=b['sites'],stated_mw=float(b['mw']),annual_cost_usd=float(q(b['cost_i'],'0.01'))) for ab,b in bystate.items()},
  sites=[dict(name=s['name'],owner=s['owner'],state=s['state'],state_from=s['how'],stated_mw=s['mw'],lat=s['lat'],lon=s['lon'],
              industrial_cents_kwh=s.get('rate_i'),annual_mwh=(float(s['mwh']) if s['cost_i'] is not None else None),annual_cost_usd_industrial=(float(q(s['cost_i'],'0.01')) if s['cost_i'] is not None else None),
              commercial_cents_kwh=s.get('rate_c'),annual_cost_usd_commercial=(float(q(s['cost_c'],'0.01')) if s['cost_c'] is not None else None)) for s in sites]),open(E+'scale.json','w'),indent=1)
json.dump(T,open(E+'scale_summary.json','w'),separators=(',',':'),sort_keys=True)
# ---------------------------------------------------------------- state outlines: arcs simplified once (shared borders stay shared), integer tenths of a pixel, relative moves
TOL=0.35
topo=json.load(open(H+'raw/states-10m.json')); sc,tr=topo['transform']['scale'],topo['transform']['translate']
def dp(pts,tol):
    if len(pts)<3: return pts
    keep=[False]*len(pts); keep[0]=keep[-1]=True; stack=[(0,len(pts)-1)]
    while stack:
        a,b=stack.pop(); (ax,ay),(bx,by)=pts[a],pts[b]; dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy); mx,mi=-1,None
        for i in range(a+1,b):
            px,py=pts[i]; d=(abs(dy*(px-ax)-dx*(py-ay))/L) if L>0 else math.hypot(px-ax,py-ay)
            if d>mx: mx,mi=d,i
        if mx>tol: keep[mi]=True; stack+=[(a,mi),(mi,b)]
    return [p for p,k in zip(pts,keep) if k]
full_pts=simp_pts=0; arcs_full=[]; arcs_simp=[]
for a in topo['arcs']:
    x=y=0; ps=[]
    for dx,dy in a: x+=dx; y+=dy; ps.append(M.Pt(x*sc[0]+tr[0],y*sc[1]+tr[1]))
    arcs_full.append(ps); s2=dp(ps,TOL); arcs_simp.append(s2); full_pts+=len(ps); simp_pts+=len(s2)
def ring_idx(idx,arcs):
    pts=[]
    for i in idx:
        a=arcs[i] if i>=0 else arcs[~i][::-1]
        pts+=a if not pts else a[1:]
    return pts
def n1(v):
    s=('-' if v<0 else '')+(str(abs(v)//10) if abs(v)>=10 else '')+('.'+str(abs(v)%10) if abs(v)%10 else '')
    return s or '0'
def enc_ring(pts):
    q=[(round(x*10),round(y*10)) for x,y in pts]
    if q[0]==q[-1]: q=q[:-1]
    ded=[q[0]]
    for p in q[1:]:
        if p!=ded[-1]: ded.append(p)
    if len(ded)<3: return ''
    out=[f'M{n1(ded[0][0])} {n1(ded[0][1])}l']; px,py=ded[0]; toks=[]
    for x,y in ded[1:]: toks+= [n1(x-px),n1(y-py)]; px,py=x,y
    s=''
    for t in toks: s+= (t if (not s or t.startswith('-')) else ' '+t)
    return out[0]+s+'z'
def area(pts): return abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))))/2
state_d={}; bytes_full=bytes_simp=0; dropped=0; dropped_in={}
for g in topo['objects']['states']['geometries']:
    ab=M.NAMES.get(g['properties']['name'])
    if not ab or ab in ('AK','HI'): continue
    polys=[g['arcs']] if g['type']=='Polygon' else g['arcs']; d=''; df=''
    for p in polys:
        for r in p:
            df+=enc_ring(ring_idx(r,arcs_full)); rp=ring_idx(r,arcs_simp)
            if area(rp)<0.4: dropped+=1; dropped_in[ab]=dropped_in.get(ab,0)+1; continue
            d+=enc_ring(rp)
    state_d[ab]=d; bytes_full+=len(df); bytes_simp+=len(d)
KMPX=6371/M.SC
say(f'outline simplification: tolerance {TOL} px = about {TOL*KMPX:.1f} km; islands under 0.4 square pixels = about {0.4*KMPX*KMPX:.0f} square kilometers are not drawn ({dropped} rings, by state {dropped_in})')
say(f'outlines: {full_pts} points before, {simp_pts} after tolerance {TOL} px of 960 (about {TOL*4.8:.1f} km); path data {bytes_full} bytes before, {bytes_simp} after; rings under 0.4 square pixels dropped: {dropped}')
# ---------------------------------------------------------------- shading classes (the same five quantile bins as the state maps)
def bins(vals,dec):
    v=sorted(vals); edges=[round(v[int(len(v)*k/5)],dec) for k in (1,2,3,4)]
    return edges,(lambda x:1+sum(x>=e for e in edges))
drawn=sorted(M.drawn)
pi={ab:ST[ab]['sectors']['industrial']['price'] for ab in drawn}; pc={ab:ST[ab]['sectors']['commercial']['price'] for ab in drawn}; pk={ab:CB['states'][ab]['co2_lb_mwh'] for ab in drawn}
ei,ci=bins(pi.values(),1); ec,cc=bins(pc.values(),1); ek,ck=bins(pk.values(),0)
def legtxt(edges,fmt): return [f'under {fmt(edges[0])}']+[f'{fmt(edges[i])} to {fmt(edges[i+1])}' for i in range(3)]+[f'{fmt(edges[3])} and over']
assert legtxt(ei,lambda v:f'{v:.1f}')==EL['legend']['industrial'],(legtxt(ei,lambda v:f'{v:.1f}'),EL['legend']['industrial'])
assert legtxt(ec,lambda v:f'{v:.1f}')==EL['legend']['commercial']
assert legtxt(ek,lambda v:f'{v:,.0f}')==CB['legend'],(legtxt(ek,lambda v:f'{v:,.0f}'),CB['legend'])
say('legend edges match the state maps: industrial',ei,'commercial',ec,'carbon',ek)
body=''
for ab in drawn:
    t=f'{M.ABBR2NAME[ab]}: industrial {pi[ab]:.1f} and commercial {pc[ab]:.1f} cents per kilowatthour in 2024, {pk[ab]:,.0f} pounds of CO2 per megawatthour generated in 2023'
    body+=f'<path d="{state_d[ab]}" class="st i{ci(pi[ab])} m{cc(pc[ab])} k{ck(pk[ab])}"><title>{esc(t)}</title></path>'
# ---------------------------------------------------------------- dot layers
def Pt10(lon,lat): x,y=M.Pt(lon,lat); return round(x*10),round(y*10)
def dots_path(points):
    """zero-length round-capped segments: one path per class, relative moves, scanline order"""
    q=sorted(points,key=lambda p:(p[1]//60,p[0])); s=''; px=py=0
    for x,y in q:
        s+=('M' if not s else 'm')+(n1(x) if not s else n1(x-px))+' '+(n1(y) if not s else n1(y-py))+'h0'; px,py=x,y
    return s
FUELS=[('gas','Natural gas','#c0782e'),('coal','Coal','#6b6b6b'),('nuclear','Nuclear','#7a4fa3'),('hydro','Hydro','#2b78b4'),('wind','Wind','#2e9a8a'),('solar','Solar','#e0b000'),('storage','Storage','#d0408a'),('oil','Petroleum','#a65d57'),('other','Other','#aaaaaa')]
OP_BINS=[(25,100),(100,500),(500,1500),(1500,1e9)]
op=[p for p in PL['plants'] if p['total_mw']>=25 and p['lat'] is not None and M.inbox(p['lat'],p['lon'])]
say('operating plants drawn',len(op),'of',len(PL['plants']))
g_plants=''; big=''
for bi in range(3,-1,-1):
    for fk,_,_ in FUELS:
        pts=[Pt10(p['lon'],p['lat']) for p in op if p['dominant']==fk and OP_BINS[bi][0]<=p['total_mw']<OP_BINS[bi][1] and p['total_mw']<1000]
        pts_b=[p for p in op if p['dominant']==fk and OP_BINS[bi][0]<=p['total_mw']<OP_BINS[bi][1] and p['total_mw']>=1000]
        if pts: g_plants+=f'<path d="{dots_path(pts)}" class="pf-{fk} b{bi+1}"/>'
        for p in pts_b:
            x,y=M.Pt(p['lon'],p['lat']); big+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{[1.8,2.6,3.8,5.5][bi]:.1f}" class="pc-{fk}"><title>{esc(p["name"])}, {esc(p["state"])}: {dict((k,n) for k,n,_ in FUELS)[fk].lower()}, {p["total_mw"]:,.0f} MW</title></circle>'
n_big=sum(1 for p in op if p['total_mw']>=1000)
g_plants+=big
PN_BINS=[(25,100,1.7),(100,500,2.5),(500,1500,3.6),(1500,1e9,5.0)]
pn=[p for p in PN['plants'] if p['total_mw']>=25 and M.inbox(p['lat'],p['lon'])]
say('planned plants drawn',len(pn),'of',len(PN['plants']))
g_planned=''
for bi in range(3,-1,-1):
    lo,hi,h=PN_BINS[bi]
    for fk,_,_ in FUELS:
        sel=[Pt10(p['lon'],p['lat']) for p in pn if p['dominant']==fk and lo<=p['total_mw']<hi]
        if not sel: continue
        hh=round(h*10); s=''; px=py=None
        for x,y in sorted(sel,key=lambda p:(p[1]//60,p[0])):
            s+=(f'M{n1(x-hh)} {n1(y-hh)}' if px is None else f'm{n1(x-px)} {n1(y-py)}')+f'h{n1(2*hh)}v{n1(2*hh)}h{n1(-2*hh)}z'; px,py=x,y
        g_planned+=f'<path d="{s}" class="qf-{fk}"/>'
osm=[(Pt10(r['lon'],r['lat'])) for r in DC['osm'] if M.inbox(r['lat'],r['lon'])]
say('OSM features drawn',len(osm),'of',len(DC['osm']))
g_osm=f'<path d="{dots_path(osm)}"/>'
R0=lambda mw:max(2.2,0.55*math.sqrt(mw))
g_epoch=''
for s in sorted([s for s in sites if s['lat'] is not None and M.inbox(s['lat'],s['lon'])],key=lambda s:-(s['mw'] or 0)):
    x,y=M.Pt(s['lon'],s['lat'])
    if s['mw']:
        t=f"{s['name']}, {owner(s)}: {fmw(s['mw'])} MW stated"+(f", {f1(mil(s['cost_i']))} million dollars a year at {s['rate_i']:.2f} cents per kilowatthour in {M.ABBR2NAME[s['state']]}" if s['cost_i'] is not None else '')
        g_epoch+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R0(s["mw"]):.1f}" class="e"><title>{esc(t)}</title></circle>'
    else:
        g_epoch+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" class="e0"><title>{esc(s["name"])}, {esc(owner(s))}: no power stated</title></circle>'
n_epoch_drawn=sum(1 for s in sites if s['lat'] is not None and M.inbox(s['lat'],s['lon']))
say('Epoch sites drawn',n_epoch_drawn)
svg=(f'<svg viewBox="0 0 {M.W} {M.HT:.0f}" role="img" aria-label="Map of the contiguous United States. The state shading and the dot layers are chosen with the controls above the map. By default the states are shaded by the 2024 industrial electricity price and the Epoch AI data centers are drawn as rings sized by stated power." class="amapsvg">'
     f'<g class="g-states">{body}</g><g class="g-plants">{g_plants}</g><g class="g-planned">{g_planned}</g><g class="g-osm">{g_osm}</g><g class="g-epoch">{g_epoch}</g></svg>')
say('map svg bytes',len(svg.encode()),'(states',len(body.encode()),'plants',len(g_plants.encode()),'planned',len(g_planned.encode()),'osm',len(g_osm.encode()),'epoch',len(g_epoch.encode()),')')
# ---------------------------------------------------------------- legends and controls
def swatches(texts,cls):
    return '<ul class="swl">'+''.join(f'<li><i class="sw l{i+1}"></i>{esc(t)}</li>' for i,t in enumerate(texts))+'</ul>'
n_pl=len(PL['plants']); n_pn=len(PN['plants'])
lg_ind=('<div class="lg lg-ind"><p class="lgh">Industrial customers, cents per kilowatthour, 2024</p>'+swatches(legtxt(ei,lambda v:f'{v:.1f}'),'i')+
        '<p class="src">Source: U.S. Energy Information Administration, EIA-861 sales to ultimate customers for 2024. Price is revenue divided by sales for each state. Read 28 Oct 2026.</p></div>')
lg_com=('<div class="lg lg-com"><p class="lgh">Commercial customers, cents per kilowatthour, 2024</p>'+swatches(legtxt(ec,lambda v:f'{v:.1f}'),'m')+
        '<p class="src">Source: U.S. Energy Information Administration, EIA-861 sales to ultimate customers for 2024. Price is revenue divided by sales for each state. Read 28 Oct 2026.</p></div>')
lg_co2=('<div class="lg lg-co2"><p class="lgh">Carbon intensity of generation, pounds of CO2 per megawatthour, 2023</p>'+swatches(legtxt(ek,lambda v:f'{v:,.0f}'),'k')+
        '<p class="src">Source: U.S. Environmental Protection Agency, eGRID2023 revision 2, state total output emission rates. It counts what the plants in each state emit, not the carbon in the power its customers use. Read 28 Oct 2026.</p></div>')
lg_none='<div class="lg lg-none"><p class="lgh">No state shading</p><p class="src">The state outlines are from the U.S. Census Bureau boundaries through us-atlas.</p></div>'
ring_key=''.join(f'<circle cx="{cx}" cy="21" r="{R0(mw):.1f}" class="e"/>' for cx,mw in ((22,100),(62,500),(114,1000)))
dl_epoch=(f'<div class="dl dl-epoch"><p class="lgh"><svg viewBox="0 0 150 42" class="key kring" aria-hidden="true">{ring_key}<text x="22" y="40" class="kt">100</text><text x="62" y="40" class="kt">500</text><text x="114" y="40" class="kt">1,000 MW</text></svg>Epoch AI data centers, sized by stated power</p>'
          f'<p class="src">Dashed ring: no power stated. Power is Epoch AI&rsquo;s current figure, which Epoch describes as an estimate of IT power. Source: Epoch AI, AI data centers (CC BY 4.0), pulled {PULLED}. Sites without a usable address are not drawn.</p></div>')
dl_osm=(f'<div class="dl dl-osm"><p class="lgh"><svg viewBox="0 0 30 14" class="key" aria-hidden="true"><path d="M8 7h0M15 7h0M22 7h0" class="kd"/></svg>OpenStreetMap data center features</p>'
        f'<p class="src">Features tagged as data centers, near-duplicates within 250 meters with the same name merged. Source: OpenStreetMap contributors (ODbL), pulled {PULLED} through Overpass.</p></div>')
fz=''.join(f'<li><i class="fz fz-{k}"></i>{esc(n)}</li>' for k,n,_ in FUELS)
dsz=''.join(f'<circle cx="{cx}" cy="10" r="{d/2:.1f}" class="kdot"/>' for cx,d in ((8,3.6),(22,5.2),(38,7.6),(58,11)))
dl_pl=(f'<div class="dl dl-plants"><p class="lgh"><svg viewBox="0 0 74 20" class="key" aria-hidden="true">{dsz}</svg>Operating power plants, by main fuel, sized by capacity</p><ul class="fzl">{fz}</ul>'
       f'<p class="src">Size steps are 25 to 100, 100 to 500, 500 to 1,500 and over 1,500 megawatts. Plants under 25 megawatts and plants outside the contiguous states are not drawn, which leaves {len(op):,} of the {n_pl:,} operating plants. Nothing else was thinned. Source: U.S. Energy Information Administration, EIA-860M for September 2026, read 28 Oct 2026.</p></div>')
sq=''.join(f'<rect x="{cx-h}" y="{10-h}" width="{2*h}" height="{2*h}" class="kq"/>' for cx,h in ((8,1.7),(22,2.5),(38,3.6),(58,5.0)))
dl_pn=(f'<div class="dl dl-planned"><p class="lgh"><svg viewBox="0 0 74 20" class="key" aria-hidden="true">{sq}</svg>Planned power plants, by main fuel, sized by planned capacity</p><ul class="fzl">{fz}</ul>'
       f'<p class="src">Hollow squares in the same fuel colors. Planned is a stage in EIA&rsquo;s list and not a promise. Plants under 25 megawatts and plants outside the contiguous states are not drawn, which leaves {len(pn):,} of the {n_pn:,} planned plants. Source: U.S. Energy Information Administration, EIA-860M for September 2026, Planned sheet, read 28 Oct 2026.</p></div>')
ctl=('<div class="amap-ctl">'
 '<fieldset><legend>State shading, one at a time</legend>'
 '<label class="opt"><input type="radio" name="amap-sh" id="sh-ind" checked> Industrial price, 2024</label>'
 '<label class="opt"><input type="radio" name="amap-sh" id="sh-com"> Commercial price, 2024</label>'
 '<label class="opt"><input type="radio" name="amap-sh" id="sh-co2"> Carbon intensity, 2023</label>'
 '<label class="opt"><input type="radio" name="amap-sh" id="sh-none"> None</label></fieldset>'
 '<fieldset><legend>Dots, any combination</legend>'
 '<label class="opt"><input type="checkbox" id="d-epoch" checked> Epoch AI data centers</label>'
 '<label class="opt"><input type="checkbox" id="d-osm"> OpenStreetMap data centers</label>'
 '<label class="opt"><input type="checkbox" id="d-plants"> Operating power plants</label>'
 '<label class="opt"><input type="checkbox" id="d-planned"> Planned power plants</label></fieldset></div>')
frag=f'<div class="amap" id="atlas-map">{ctl}{svg}<div class="amap-leg"><div class="lgs">{lg_ind}{lg_com}{lg_co2}{lg_none}</div><div class="dls">{dl_epoch}{dl_osm}{dl_pl}{dl_pn}</div></div></div>'
open(H+'atlasmap_fragment.html','w',encoding='utf-8').write(frag)
say('fragment bytes',len(frag.encode()))
# ---------------------------------------------------------------- css (the page CSS is plain, so the layer switches are :has() rules)
css=['/* ATLAS one map (build_atlasmap.py, 30 Oct 2026): layers switch with radio buttons and checkboxes, no script */',
 '.amap{margin:8px 0 18px}.amap-ctl{display:flex;flex-wrap:wrap;gap:8px 16px;margin:0 0 8px}.amap fieldset{border:1px solid var(--rule);margin:0;padding:4px 12px 6px;flex:1 1 280px;min-width:0}',
 '.amap legend{font:600 13px sans-serif;color:var(--mid);padding:0 6px}.amap .opt{display:inline-flex;align-items:center;gap:7px;font-size:14.5px;line-height:1.3;min-height:34px;margin:0 14px 0 0;cursor:pointer}',
 '.amap input{width:18px;height:18px;margin:0;accent-color:var(--goldink)}.amapsvg{width:100%;height:auto;max-width:960px;display:block;margin:6px 0}',
 '.amapsvg .st{fill:var(--paper2);stroke:var(--paper);stroke-width:.7}']
sel=lambda cls,n:f'.amapsvg .st.{cls}{n}'
op_=[.1,.25,.4,.55,.72]
for n in range(1,6): css.append(f'.amapsvg .st.i{n}{{fill:var(--goldink);fill-opacity:{op_[n-1]}}}')
for key,cls in (('com','m'),('co2','k')):
    css.append(f'.amap:has(#sh-{key}:checked) .st{{fill:var(--paper2);fill-opacity:1}}')
    for n in range(1,6): css.append(f'.amap:has(#sh-{key}:checked) .st.{cls}{n}{{fill:var(--goldink);fill-opacity:{op_[n-1]}}}')
css.append('.amap:has(#sh-none:checked) .st{fill:var(--paper2);fill-opacity:1;stroke:var(--rule);stroke-width:.5}')
css+=['.amapsvg .g-plants,.amapsvg .g-planned,.amapsvg .g-osm{display:none}',
 '.amap:has(#d-plants:checked) .g-plants,.amap:has(#d-planned:checked) .g-planned,.amap:has(#d-osm:checked) .g-osm{display:inline}.amap:has(#d-epoch:not(:checked)) .g-epoch{display:none}',
 '.amapsvg .g-plants path{fill:none;stroke-linecap:round;stroke-opacity:.8}.amapsvg .g-plants .b1{stroke-width:3.6}.amapsvg .g-plants .b2{stroke-width:5.2}.amapsvg .g-plants .b3{stroke-width:7.6}.amapsvg .g-plants .b4{stroke-width:11}',
 '.amapsvg .g-plants circle{fill-opacity:.8;stroke:var(--paper);stroke-width:.4}.amapsvg .g-planned path{fill:none;stroke-width:1.2;stroke-opacity:.9}',
 '.amapsvg .g-osm path{fill:none;stroke:var(--ink);stroke-opacity:.55;stroke-linecap:round;stroke-width:3}',
 '.amapsvg .e{fill:var(--goldink);fill-opacity:.25;stroke:var(--goldink);stroke-width:1}.amapsvg .e0{fill:none;stroke:var(--goldink);stroke-width:1;stroke-dasharray:2 1.5}']
for k,_,c in FUELS: css.append(f'.amapsvg .pf-{k}{{stroke:{c}}}.amapsvg .pc-{k}{{fill:{c}}}.amapsvg .qf-{k}{{stroke:{c}}}.amap .fz-{k}{{background:{c}}}')
css+=['.amap-leg{display:flex;flex-wrap:wrap;gap:6px 22px;align-items:flex-start}.amap-leg .lgs{flex:1 1 300px;min-width:0}.amap-leg .dls{flex:1 1 300px;min-width:0}',
 '.amap .lg,.amap .dl{margin:0 0 10px}.amap .lgh{font:600 13.5px sans-serif;color:var(--ink);margin:0 0 4px}.amap .src{font-size:12.5px;line-height:1.4;color:var(--mid);margin:2px 0 0}',
 '.amap .swl,.amap .fzl{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:2px 12px}.amap .swl li,.amap .fzl li{font-size:13px;display:inline-flex;align-items:center;gap:5px;margin:0}',
 '.amap .sw{display:inline-block;width:20px;height:12px;border:1px solid var(--rule);background:var(--paper2);position:relative}.amap .sw:before{content:"";position:absolute;left:0;top:0;right:0;bottom:0;background:var(--goldink)}',
 '.amap .fz{display:inline-block;width:10px;height:10px;border-radius:50%}.amap .key{width:auto;height:20px;vertical-align:middle;margin-right:8px;display:inline-block}.amap .key.kring{height:40px}.amap .key text{font:500 10px sans-serif;fill:var(--mid);text-anchor:middle}',
 '.amap .key .e{fill:var(--goldink);fill-opacity:.25;stroke:var(--goldink);stroke-width:1}.amap .key .kd{fill:none;stroke:var(--ink);stroke-opacity:.55;stroke-linecap:round;stroke-width:3}.amap .key .kdot{fill:var(--mid);fill-opacity:.8}.amap .key .kq{fill:none;stroke:var(--mid);stroke-width:1.2}',
 '.amap .lg-com,.amap .lg-co2,.amap .lg-none{display:none}.amap:has(#sh-com:checked) .lg-ind,.amap:has(#sh-co2:checked) .lg-ind,.amap:has(#sh-none:checked) .lg-ind{display:none}',
 '.amap:has(#sh-com:checked) .lg-com,.amap:has(#sh-co2:checked) .lg-co2,.amap:has(#sh-none:checked) .lg-none{display:block}',
 '.amap .dl-osm,.amap .dl-plants,.amap .dl-planned{display:none}.amap:has(#d-osm:checked) .dl-osm,.amap:has(#d-plants:checked) .dl-plants,.amap:has(#d-planned:checked) .dl-planned{display:block}.amap:has(#d-epoch:not(:checked)) .dl-epoch{display:none}']
for n in range(1,6): css.append(f'.amap .sw.l{n}:before{{opacity:{op_[n-1]}}}')
css.append('.mtx tfoot td{font-weight:700;border-top:2px solid var(--rule)}')
css.append('@media (max-width:600px){.amap fieldset{display:grid;grid-template-columns:1fr 1fr;gap:0 8px}.amap .opt{min-height:40px;margin:0}.amapsvg .g-osm path{stroke-width:4.5}.amapsvg .g-plants .b1{stroke-width:5.4}.amapsvg .g-plants .b2{stroke-width:7.2}.amapsvg .g-plants .b3{stroke-width:10}.amapsvg .g-plants .b4{stroke-width:14}.amapsvg .g-planned path{stroke-width:2}.amapsvg .e,.amapsvg .e0{stroke-width:2}.amapsvg .st{stroke-width:1}}')
open(H+'atlasmap.css','w').write('\n'.join(css)+'\n')
say('css bytes',len('\n'.join(css).encode()))

# ---------------------------------------------------------------- the cost-to-scale text and tables (build_site.py puts these on /atlas)
first=counted[0]; ex_mwh=D(str(first['mw']))*HRS
def fint(d): return f'{d:,.0f}' if d==d.to_integral() else f'{d:,.2f}'
lead=(f"<p>One year of electricity for the AI data centers in Epoch AI&rsquo;s dataset, at each site&rsquo;s full stated power and each state&rsquo;s average 2024 industrial price, comes to <strong>{T['total_busd']} billion dollars</strong>. "
      f"That is {T['total_musd']} million dollars for {T['total_mw']} megawatts and {T['total_twh']} terawatthours, across {T['counted']} sites that state a power and sit in a state we could place.</p>"
      "<p>It is arithmetic on two published figures and not a forecast. Epoch AI states each site&rsquo;s power, in a dataset we pulled on "+PULLED+". The U.S. Energy Information Administration&rsquo;s EIA-861 data for 2024 gives each state&rsquo;s average industrial price. "
      "It is full stated power for a full year at the state average, and not any site&rsquo;s contract price or actual bill.</p>")
open(H+'scale_lead.html','w',encoding='utf-8').write(lead)
am=[s for s in sites if s['how']=='address text']
fx_txt=''.join(f"<p>The geocoders placed {esc(f['name'])} in Kansas from a city and ZIP match. Its Epoch address names Papillion, Nebraska, and the replacement point is on Gold Coast Road in ZIP 68138 (OpenStreetMap Nominatim, looked up 30 Oct 2026). The map and the table use Nebraska.</p>" for f in FX.values() if f['name']=='Google Papillion')
am_txt=(' Where the geocoders found no point, the state is the one Epoch&rsquo;s own address text names. That applies to '+' and '.join(f"{esc(s['name'])} ({M.ABBR2NAME[s['state']]}{'' if s['mw'] else ', no stated power'})" for s in am)+'.') if am else ''
sh_txt=', and '.join(f"{esc(g[0]['name'])} with {esc(g[1]['name'])}" for g in [[x for x in grp if x['mw']] for grp in shared_mw])
nopl_names=', '.join(esc(s['name']) for s in nopl_mw[:-1])+' and '+esc(nopl_mw[-1]['name'])
mrows=''.join(f"<tr><td>{esc(s['name'])}</td><td>{esc(owner(s))}</td><td>{s['state']}</td><td>{fmw(s['mw'])}</td><td>{s['rate_i']:.2f}</td><td>{f1(mil(s['cost_i']))}</td></tr>" for s in counted)
mfoot=f"<tfoot><tr><td>Total</td><td>{T['counted']} sites</td><td></td><td>{T['total_mw']}</td><td></td><td>{T['total_musd']}</td></tr></tfoot>"
srows=''.join(f"<tr><td>{M.ABBR2NAME[ab]}</td><td>{rate(ab,'industrial'):.2f}</td><td>{rate(ab,'commercial'):.2f}</td><td>{b['sites']}</td><td>{fmw(b['mw'])}</td><td>{f1(mil(b['cost_i']))}</td></tr>" for ab,b in bystate.items())
urows=''.join(f"<tr><td>{esc(s['name'])}</td><td>{esc(owner(s))}</td><td>{fmw(s['mw'])}</td></tr>" for s in nopl_mw)
beside_txt=(f"<p>Beside the total, not in it: each of those {T['beside_named_sites']} sites names its state in the source Epoch cites for it, "+', '.join(f"{esc(s['name'])} in {M.ABBR2NAME[NAMED[s['name']][0]]}" for s in named)+f". Placed there at each state&rsquo;s 2024 industrial price, they would add {T['beside_named_add_musd']} million dollars, for {T['beside_total_musd']} million, about {T['beside_total_busd']} billion dollars. They stay out of the total because the rule places a site only from its map point or its own address, and these three records give neither. This figure was added on 10 Nov 2026.</p>" if named else '')   # 10 Nov 2026 (newsletter audit): the figure beside the total
body=(
 '<h2>How the cost is worked</h2>'
 f"<p>For each site, stated megawatts times 8,760 hours gives megawatthours. Megawatthours times the state&rsquo;s industrial price in cents per kilowatthour, with 1,000 kilowatthours to the megawatthour and 100 cents to the dollar, gives dollars. "
 f"Example, {esc(first['name'])}: {fmw(first['mw'])} MW &times; 8,760 hours = {fint(ex_mwh)} MWh, and {fint(ex_mwh)} MWh &times; {first['rate_i']:.2f} cents per kilowatthour = {f1(mil(first['cost_i']))} million dollars.</p>"
 f"<p>Epoch AI&rsquo;s dataset lists {T['sites_us']} data centers in the United States. {T['with_power']} state a power and {T['without_power']} do not. {T['counted']} of the {T['with_power']} that state a power are in a state we could place, and the total covers those {T['counted']}. "
 f"The other {T['not_counted_with_power']}, {nopl_names}, state {T['with_power_mw_not_counted']} megawatts between them and give no address, so they are not in the total. {T['not_placed']} of the {T['sites_us']} sites could not be placed in a state at all.{am_txt}</p>"
 f"{beside_txt}"
 f"<p>The state comes from the point where the site was placed on the map, with one correction. {fx_txt[3:-4] if fx_txt else ''}</p>"
 f"<p>Epoch describes its power figures as estimates of IT power, the power of the computing equipment, so the power a whole site draws with cooling and other loads is not in them. {'Two pairs of records with a stated power land on the same map point: '+sh_txt+'. Each record is counted once, as Epoch lists it.' if shared_mw else ''}</p>"
 f"<p>At each state&rsquo;s commercial price instead of its industrial price, the same arithmetic gives {T['total_musd_commercial']} million dollars. Each row below is rounded to 0.1 million dollars and the total is added before rounding. Prices are EIA-861 averages for 2024, computed as revenue divided by sales as on the <a href=\"/atlas/electricity\">electricity page</a>. Power is from Epoch AI, AI data centers (CC BY 4.0), pulled {PULLED}.</p>"
 '<h2>Annual cost by site</h2><p>Sites in order of annual cost at the state industrial price, 2024.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>Site</th><th>Owner</th><th>State</th><th>Stated power, MW</th><th>Industrial price, cents per kWh, 2024</th><th>Annual cost, millions of dollars</th></tr></thead><tbody>'+mrows+'</tbody>'+mfoot+'</table></div>'
 '<h2>Sites with a stated power that are not in the total</h2><div class="scroll"><table class="mtx"><thead><tr><th>Site</th><th>Owner</th><th>Stated power, MW</th></tr></thead><tbody>'+urows+'</tbody></table></div>'
 '<h2>State prices used</h2><p>Average prices paid by industrial and commercial customers in 2024 from EIA-861, for the states with at least one site in the total. Annual cost is at the industrial price.</p>'
 '<div class="scroll"><table class="mtx"><thead><tr><th>State</th><th>Industrial, cents per kWh</th><th>Commercial, cents per kWh</th><th>Sites</th><th>Stated power, MW</th><th>Annual cost, millions of dollars</th></tr></thead><tbody>'+srows+'</tbody></table></div>'
 '<p><a class="btn ghost" href="/atlas/scale.json">Cost to scale (JSON)</a></p>')
open(H+'scale_body.html','w',encoding='utf-8').write(body)
say('scale fragments bytes',len(lead.encode()),len(body.encode()))
open(H+'atlasmap_report.txt','w').write('\n'.join(REPORT)+'\n')
