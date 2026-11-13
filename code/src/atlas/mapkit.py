"""mapkit.py: shared pieces for the ATLAS state maps (Albers projection, Census state outlines, data center overlay, state choropleth)."""
import json,math,os,html
H=os.path.dirname(os.path.abspath(__file__))+'/'
NAMES={'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
ABBR2NAME={v:k for k,v in NAMES.items()}
topo=json.load(open(H+'raw/states-10m.json')); _sc,_tr=topo['transform']['scale'],topo['transform']['translate']
_arcs=[]
for a in topo['arcs']:
    x=y=0; pts=[]
    for dx,dy in a: x+=dx; y+=dy; pts.append((x*_sc[0]+_tr[0],y*_sc[1]+_tr[1]))
    _arcs.append(pts)
def _ring(idx):
    pts=[]
    for i in idx:
        a=_arcs[i] if i>=0 else _arcs[~i][::-1]
        pts+=a if not pts else a[1:]
    return pts
shapes={}
for g in topo['objects']['states']['geometries']:
    ab=NAMES.get(g['properties']['name'])
    if ab: shapes[ab]=[[_ring(r) for r in p] for p in ([g['arcs']] if g['type']=='Polygon' else g['arcs'])]
_phi1,_phi2,_phi0,_lam0=map(math.radians,(29.5,45.5,37.5,-96.0))
_n=(math.sin(_phi1)+math.sin(_phi2))/2; _C=math.cos(_phi1)**2+2*_n*math.sin(_phi1); _r0=math.sqrt(_C-2*_n*math.sin(_phi0))/_n
def proj(lon,lat):
    ph,la=math.radians(lat),math.radians(lon); r=math.sqrt(_C-2*_n*math.sin(ph))/_n; th=_n*(la-_lam0)
    return (r*math.sin(th), -(_r0-r*math.cos(th)))
drawn={ab:p for ab,p in shapes.items() if ab not in('AK','HI')}
_allp=[proj(lo,la) for p in drawn.values() for poly in p for r in poly for lo,la in r]
_xs=[p[0] for p in _allp]; _ys=[p[1] for p in _allp]; _x0,_x1,_y0,_y1=min(_xs),max(_xs),min(_ys),max(_ys)
W=960; SC=(W-20)/(_x1-_x0); HT=(_y1-_y0)*SC+20
def Pt(lon,lat): x,y=proj(lon,lat); return (10+(x-_x0)*SC,10+(y-_y0)*SC)
def inbox(lat,lon): return 24.3<=lat<=49.6 and -125.2<=lon<=-66.5
dc=json.load(open(H+'datacenters.json'))
dots=''.join(f'<circle cx="{Pt(r["lon"],r["lat"])[0]:.1f}" cy="{Pt(r["lon"],r["lat"])[1]:.1f}" r="1.5" class="o"/>' for r in dc['osm'] if inbox(r['lat'],r['lon']))
rings=''
for r in sorted([e for e in dc['epoch'] if e['lat'] is not None and inbox(e['lat'],e['lon'])],key=lambda e:-(e['mw'] or 0)):
    x,y=Pt(r['lon'],r['lat']); rings+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3+math.sqrt(r["mw"] or 20)*0.42:.1f}" class="e"><title>{html.escape(r["name"])}'+(f', {r["mw"]:.0f} MW' if r['mw'] else '')+'</title></circle>'
SMALL={'CT','RI','NJ','DE','MD','DC','MA','NH','VT'}
def _cent(polys):
    best=max(polys,key=lambda p:len(p[0])); pts=[Pt(lo,la) for lo,la in best[0]]
    return (min(p[0] for p in pts)+max(p[0] for p in pts))/2,(min(p[1] for p in pts)+max(p[1] for p in pts))/2
def choropleth(values,fmt,unit,aria,decimals=1):
    """values: {abbr: number}. Five quantile bins. Returns (svg, legend labels)."""
    vals=sorted(values[a] for a in drawn if values.get(a) is not None)
    edges=[round(vals[int(len(vals)*k/5)],decimals) for k in (1,2,3,4)]
    cls=lambda v:1+sum(v>=e for e in edges)
    body=''; labels=''
    for ab in sorted(drawn):
        v=values.get(ab); d=''.join('M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in (Pt(lo,la) for lo,la in r))+'Z' for poly in drawn[ab] for r in poly)
        if v is None: body+=f'<path d="{d}" class="s0"/>'; continue
        body+=f'<path d="{d}" class="s{cls(v)}"><title>{ABBR2NAME[ab]}: {fmt(v)} {unit}</title></path>'
        if ab not in SMALL: x,y=_cent(drawn[ab]); labels+=f'<text x="{x:.0f}" y="{y+3:.0f}" class="lb">{fmt(v)}</text>'
    svg=f'<svg viewBox="0 0 {W} {HT:.0f}" role="img" aria-label="{aria}" class="atlasmap elmap">{body}{labels}{dots}{rings}</svg>'
    f=lambda v:fmt(v)
    leg=[f'under {f(edges[0])}']+[f'{f(edges[i])} to {f(edges[i+1])}' for i in range(3)]+[f'{f(edges[3])} and over']
    return svg,leg
