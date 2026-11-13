"""build_atlas.py (27 Oct 2026): data center map for ATLAS. Inputs: raw/osm_us.json (OpenStreetMap via Overpass, ODbL), raw/epoch_us_geocoded.json (Epoch AI, CC BY 4.0, geocoded by Census then Nominatim),
raw/states-10m.json (us-atlas 3.0.1, Census boundaries). Outputs: datacenters.json (every record kept), map_body.html (section + inline SVG), summary.json (counts for the ledger).
Contiguous states are drawn (Albers equal-area conic). Sites in Alaska, Hawaii and territories are in the data file and counted, not drawn."""
import json,math,os,re,html,collections,datetime
H=os.path.dirname(os.path.abspath(__file__))+'/'
osm=json.load(open(H+'raw/osm_us.json')); pulled=osm['osm3s']['timestamp_osm_base'][:10]
ep=json.load(open(H+'raw/epoch_us_geocoded.json'))
def inbox(lat,lon): return 24.3<=lat<=49.6 and -125.2<=lon<=-66.5
# --- records
recs=[]
for e in osm['elements']:
    t=e.get('tags',{}); lat=e.get('lat') or e['center']['lat']; lon=e.get('lon') or e['center']['lon']
    recs.append(dict(source='OpenStreetMap',osm=f"{e['type']}/{e['id']}",name=t.get('name') or t.get('operator') or '',operator=t.get('operator',''),lat=round(lat,5),lon=round(lon,5),
                     building=t.get('building',''),status=('construction' if t.get('building')=='construction' or 'construction' in t else '')))
# dedupe OSM features within ~250 m that share a name (way + node of one site) or both unnamed
def key(r): return (round(r['lat']/0.0025),round(r['lon']/0.0025),r['name'].lower())
seen={}; kept=[]; dup=0
for r in recs:
    k=key(r)
    if k in seen: dup+=1; continue
    seen[k]=1; kept.append(r)
osm_recs=kept
epoch_recs=[dict(source='Epoch AI',name=o['name'],operator=o['Owner'].split(' #')[0],mw=float(o['Current power (MW)'] or 0) or None,h100e=float(o['Current H100 equivalents'] or 0) or None,
                 capex_usd_b=float(o['Current total capital cost (2025 USD billions)'] or 0) or None,address=o['address'],lat=o['lat'],lon=o['lon'],placed=o['match'] or '') for o in ep]
# --- projection: Albers equal-area conic, parallels 29.5/45.5, origin (-96, 37.5)
phi1,phi2,phi0,lam0=map(math.radians,(29.5,45.5,37.5,-96.0))
n=(math.sin(phi1)+math.sin(phi2))/2; C=math.cos(phi1)**2+2*n*math.sin(phi1); r0=math.sqrt(C-2*n*math.sin(phi0))/n
def proj(lon,lat):
    ph,la=math.radians(lat),math.radians(lon); r=math.sqrt(C-2*n*math.sin(ph))/n; th=n*(la-lam0)
    return (r*math.sin(th), -(r0-r*math.cos(th)))
# --- states
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
skip={'02','15','72','78','60','66','69'}
polys=[]
for g in topo['objects']['states']['geometries']:
    if g['id'] in skip: continue
    rings=g['arcs'] if g['type']=='Polygon' else [r for p in g['arcs'] for r in p]
    polys.append([ring(r) for r in rings])
allp=[proj(lo,la) for p in polys for r in p for lo,la in r]
xs=[p[0] for p in allp]; ys=[p[1] for p in allp]; x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
W=960; S=(W-20)/(x1-x0); Hh=(y1-y0)*S+20
def P(lon,lat): x,y=proj(lon,lat); return (10+(x-x0)*S, 10+(y-y0)*S)
path=''
for p in polys:
    for r in p: path+='M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in (P(lo,la) for lo,la in r))+'Z'
# --- draw
dots=''; nd=0
for r in osm_recs:
    if inbox(r['lat'],r['lon']): x,y=P(r['lon'],r['lat']); dots+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" class="o"/>'; nd+=1
rings=''; ne=0
for r in sorted([e for e in epoch_recs if e['lat'] is not None and inbox(e['lat'],e['lon'])],key=lambda e:-(e['mw'] or 0)):
    x,y=P(r['lon'],r['lat']); rad=3+math.sqrt((r['mw'] or 20))*0.42
    rings+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" class="e"><title>{html.escape(r["name"])}'+(f', {r["mw"]:.0f} MW' if r['mw'] else '')+'</title></circle>'; ne+=1
svg=f'<svg viewBox="0 0 {W} {Hh:.0f}" role="img" aria-label="Map of the contiguous United States with data center sites from OpenStreetMap as small dots and AI data centers from Epoch AI as rings sized by power" class="atlasmap"><path d="{path}" class="st"/>{dots}{rings}</svg>'
# --- outputs
allrec=osm_recs+epoch_recs
json.dump(dict(pulled=pulled,osm=osm_recs,epoch=epoch_recs),open(H+'datacenters.json','w'))
outside_osm=sum(1 for r in osm_recs if not inbox(r['lat'],r['lon'])); unplaced_ep=sum(1 for e in epoch_recs if e['lat'] is None); outside_ep=sum(1 for e in epoch_recs if e['lat'] is not None and not inbox(e['lat'],e['lon']))
mwtot=sum(e['mw'] or 0 for e in epoch_recs if e['lat'] is not None and inbox(e['lat'],e['lon']))
summ=dict(pulled=pulled,osm_features=len(osm['elements']),osm_after_dedupe=len(osm_recs),osm_drawn=nd,osm_not_drawn=outside_osm,epoch_us=len(epoch_recs),epoch_drawn=ne,epoch_outside_contiguous=outside_ep,epoch_unplaced=unplaced_ep,epoch_mw_drawn=round(mwtot))
json.dump(summ,open(H+'summary.json','w')); open(H+'map.svg','w').write(svg); print(summ)
