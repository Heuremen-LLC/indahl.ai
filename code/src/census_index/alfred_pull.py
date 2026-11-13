#!/usr/bin/env python3
"""alfred_pull.py: ALFRED (St. Louis Fed) vintages, one call per series and vintage date, cached in data/cache/alfred, paced 1.2 s, keyless. Vintage dates come from the series' ALFRED download page. A vintage date is the day ALFRED first saw the values (a stand-in for the Census release date, see PLAN.md). --offline: cache only."""
import os, sys, re, time, urllib.request, json
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
SERIES = ['HSN1F', 'HSN1FNE', 'HSN1FMW', 'HSN1FS', 'HSN1FW', 'HOUST', 'HOUSTNE', 'HOUSTMW', 'HOUSTS', 'HOUSTW', 'PERMIT', 'COMPUTSA', 'RSAFS']
FROM_VINTAGE = '2016-01-01'
C = 'data/cache/alfred'; os.makedirs(C, exist_ok=True)
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u), timeout=60).read().decode()
        except Exception as ex: err = ex; time.sleep(5)
    raise err
def vintages(s):
    p = os.path.join(C, s + '_vintages.json')
    if os.path.exists(p) and not ('--refresh-vintages' in sys.argv and time.time() - os.path.getmtime(p) > 86400 and '--offline' not in sys.argv): return json.load(open(p))   # 11 Nov: the rider asks for the list again once a day, so a new vintage is found
    if '--offline' in sys.argv: return []
    try: t = get('https://alfred.stlouisfed.org/series/downloaddata?seid=' + s); time.sleep(1.2)
    except Exception:
        if os.path.exists(p): return json.load(open(p))
        raise
    v = sorted(set(re.findall(r'<option value="(20\d\d-\d\d-\d\d|19\d\d-\d\d-\d\d)">', t)))
    json.dump(v, open(p, 'w')); return v
if __name__ == '__main__':
    n = 0
    for s in ([a for a in sys.argv[1:] if not a.startswith('--')] or SERIES):
        vs = [v for v in vintages(s) if v >= FROM_VINTAGE]; print(s, len(vs), flush=True)
        for v in vs:
            p = os.path.join(C, '%s_%s.csv' % (s, v))
            if os.path.exists(p) or '--offline' in sys.argv: continue
            try: t = get('https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=%s&vintage_date=%s&cosd=2012-01-01' % (s, v))
            except Exception as ex: print('fail', s, v, type(ex).__name__); continue
            if not t.startswith('observation_date'): print('bad', s, v, t[:60].replace('\n', ' ')); continue
            open(p, 'w').write(t); n += 1; time.sleep(1.2)
    print('pulled', n)
