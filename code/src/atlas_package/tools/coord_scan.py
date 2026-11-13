"""Two rough checks. Rule 1 (state box): flags plants and planned records whose point is outside a generous box around the stated state.
Rule: box is the state's approximate extent widened by 1.0 degree on every side. Alaska, Hawaii and DC have their own boxes.
Rule 2 (nearest same-state record): plants and planned plants are pooled by stated state, and a record is flagged when the nearest other record of its state is more than NEAR_KM away. Alaska and Hawaii are skipped because their records are far apart by nature."""
import json, os, sys
S = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/public/atlas/')
BOX = {  # lat_min, lat_max, lon_min, lon_max
'AL':(30.2,35.0,-88.5,-84.9),'AK':(51.0,71.5,-180,-129),'AZ':(31.3,37.0,-114.9,-109.0),'AR':(33.0,36.5,-94.7,-89.6),'CA':(32.5,42.0,-124.5,-114.1),
'CO':(37.0,41.0,-109.1,-102.0),'CT':(41.0,42.1,-73.8,-71.8),'DE':(38.4,39.9,-75.8,-75.0),'DC':(38.7,39.0,-77.2,-76.9),'FL':(24.4,31.1,-87.7,-79.9),
'GA':(30.3,35.1,-85.7,-80.8),'HI':(18.8,22.3,-160.3,-154.7),'ID':(41.9,49.1,-117.3,-111.0),'IL':(36.9,42.6,-91.6,-87.0),'IN':(37.7,41.8,-88.1,-84.7),
'IA':(40.3,43.6,-96.7,-90.1),'KS':(36.9,40.1,-102.1,-94.5),'KY':(36.4,39.2,-89.6,-81.9),'LA':(28.9,33.1,-94.1,-88.8),'ME':(43.0,47.5,-71.1,-66.9),
'MD':(37.8,39.8,-79.5,-75.0),'MA':(41.2,42.9,-73.6,-69.9),'MI':(41.6,48.3,-90.5,-82.1),'MN':(43.4,49.4,-97.3,-89.4),'MS':(30.1,35.0,-91.7,-88.0),
'MO':(35.9,40.7,-95.8,-89.0),'MT':(44.3,49.1,-116.1,-104.0),'NE':(39.9,43.1,-104.1,-95.2),'NV':(35.0,42.1,-120.1,-114.0),'NH':(42.6,45.4,-72.6,-70.6),
'NJ':(38.9,41.4,-75.6,-73.8),'NM':(31.3,37.1,-109.1,-103.0),'NY':(40.4,45.1,-79.8,-71.8),'NC':(33.8,36.6,-84.4,-75.4),'ND':(45.9,49.1,-104.1,-96.5),
'OH':(38.4,42.0,-84.9,-80.5),'OK':(33.6,37.1,-103.1,-94.4),'OR':(41.9,46.3,-124.7,-116.4),'PA':(39.7,42.3,-80.6,-74.6),'RI':(41.1,42.1,-71.9,-71.1),
'SC':(32.0,35.3,-83.4,-78.5),'SD':(42.4,46.0,-104.1,-96.4),'TN':(34.9,36.7,-90.4,-81.6),'TX':(25.8,36.6,-106.7,-93.5),'UT':(36.9,42.1,-114.1,-109.0),
'VT':(42.7,45.1,-73.5,-71.4),'VA':(36.5,39.5,-83.7,-75.2),'WA':(45.5,49.1,-124.9,-116.9),'WV':(37.1,40.7,-82.7,-77.7),'WI':(42.4,47.1,-92.9,-86.7),'WY':(40.9,45.1,-111.1,-104.0)}
NEAR_KM = 140
import math, collections
def hav(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d)); x = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
def scan_all():
    """returns [(file, record, {'box': bool, 'near_km': float or None})] for flagged records"""
    recs = [(f, p) for f in ('plants.json', 'planned.json') for p in json.load(open(S + f))['plants']]
    by = collections.defaultdict(list)
    for f, p in recs: by[p['state']].append(p)
    out = []
    for f, p in recs:
        b = BOX[p['state']]; la, lo = p['lat'], p['lon']
        box = not (b[0] - 1 <= la <= b[1] + 1 and b[2] - 1 <= lo <= b[3] + 1); near = None
        if p['state'] not in ('AK', 'HI') and len(by[p['state']]) > 1:
            d = min(hav(la, lo, q['lat'], q['lon']) for q in by[p['state']] if q is not p)
            if d > NEAR_KM: near = round(d)
        if box or near: out.append((f, p, {'box': box, 'near_km': near}))
    return out
def scan(fname):
    out = []; unk = set()
    for p in json.load(open(S + fname))['plants']:
        b = BOX.get(p['state'])
        if not b: unk.add(p['state']); continue
        la, lo = p['lat'], p['lon']
        if not (b[0] - 1 <= la <= b[1] + 1 and b[2] - 1 <= lo <= b[3] + 1): out.append(p)
    return out, unk
if __name__ == '__main__':
    for f, p, w in scan_all(): print(f, p['code'], p['name'], p['state'], p['lat'], p['lon'], w)
    for f in ():
        o, unk = scan(f); print(f, len(o), 'flagged; states without a box:', sorted(unk))
        for p in o: print('  ', p['code'], p['name'], p['state'], p.get('county', ''), p['lat'], p['lon'])
