#!/usr/bin/env python3
"""nas_tick.py: AIRLINE FAA keeper per PLAN.md addendum 3. Every snapshot of the FAA airport delay feed, as published, with a live display."""
import os, sys, json, time, hashlib, subprocess, urllib.request, urllib.error, xml.etree.ElementTree as ET
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('nas: plan not committed'); sys.exit(0)
URL = 'https://nasstatus.faa.gov/api/airport-status-information'; UA = {'User-Agent': 'heuremen-airline/0.1 (+https://indahl.ai/airline)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def parse(xmltext):
    """-> (update_time, {type name: [ {field: text, ...}, ... ]}) with every field as published; no filtering"""
    root = ET.fromstring(xmltext); ut = (root.findtext('Update_Time') or '').strip(); out = {}
    for dt in root.findall('Delay_type'):
        name = (dt.findtext('Name') or '').strip(); items = []
        for lst in dt:
            if lst.tag == 'Name' or len(list(lst)) == 0: continue
            for it in lst:
                row = {}
                def walk(e, pre):
                    for c in e:
                        key = pre + c.tag
                        for a, v in c.attrib.items(): row[key + '@' + a] = v
                        if len(list(c)): walk(c, key + '.')
                        elif (c.text or '').strip(): row[key] = c.text.strip()
                walk(it, ''); items.append(row)
        out[name] = items
    return ut, out
def gate():
    x = ('<AIRPORT_STATUS_INFORMATION><Update_Time>Thu Oct 29 18:48:19 2026 GMT</Update_Time><Delay_type><Name>Ground Delay Programs</Name><Ground_Delay_List><Ground_Delay><ARPT>SAN</ARPT><Reason>airport volume</Reason><Avg>28 minutes</Avg><Max>1 hour and 4 minutes</Max></Ground_Delay></Ground_Delay_List></Delay_type>'
         '<Delay_type><Name>General Arrival/Departure Delay Info</Name><Arrival_Departure_Delay_List><Delay><ARPT>SEA</ARPT><Reason>RWY:Construction</Reason><Arrival_Departure Type="Departure"><Min>16 minutes</Min><Max>30 minutes</Max><Trend>Increasing</Trend></Arrival_Departure></Delay></Arrival_Departure_Delay_List></Delay_type>'
         '<Delay_type><Name>Ground Stops</Name><Ground_Stop_List><Program><ARPT>EWR</ARPT><Reason>thunderstorms</Reason><End_Time>8:15 pm EDT</End_Time></Program></Ground_Stop_List></Delay_type>'
         '<Delay_type><Name>Airport Closures</Name><Airport_Closure_List><Airport><ARPT>XYZ</ARPT><Reason>runway</Reason></Airport></Airport_Closure_List></Delay_type></AIRPORT_STATUS_INFORMATION>')
    ut, d = parse(x); ok = ut.startswith('Thu Oct 29') and d['Ground Delay Programs'][0] == {'ARPT': 'SAN', 'Reason': 'airport volume', 'Avg': '28 minutes', 'Max': '1 hour and 4 minutes'}
    g = d['General Arrival/Departure Delay Info'][0]; ok &= g['ARPT'] == 'SEA' and g['Arrival_Departure@Type'] == 'Departure' and g['Arrival_Departure.Min'] == '16 minutes' and g['Arrival_Departure.Trend'] == 'Increasing'
    ok &= d['Ground Stops'][0]['End_Time'] == '8:15 pm EDT' and d['Airport Closures'][0]['ARPT'] == 'XYZ'
    ut2, d2 = parse('<AIRPORT_STATUS_INFORMATION><Update_Time>t</Update_Time><Delay_type><Name>Ground Delay Programs</Name></Delay_type></AIRPORT_STATUS_INFORMATION>'); ok &= d2 == {'Ground Delay Programs': []}
    return bool(ok)
if not gate(): print('nas: GATE FAILED'); sys.exit(1)
now = time.time(); snap = dict(t=now)
try:
    b = urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=30).read(); ut, d = parse(b); snap.update(update_time=ut, types=d)
except Exception as e: snap.update(status='NOTHING_RETURNED', why=type(e).__name__)
open('data/snapshots.jsonl', 'a').write(json.dumps(snap) + '\n')
# ---- live display, merged into the page summary
snaps = sum(1 for _ in open('data/snapshots.jsonl')); first = json.loads(open('data/snapshots.jsonl').readline())['t']
S = json.load(open('summary_airline.json')) if os.path.exists('summary_airline.json') else {}
rows = {}
if 'types' in snap:
    for tname, items in snap['types'].items():
        for it in items:
            arp = it.get('ARPT') or it.get('Airport') or '?'
            stated = ', '.join('%s %s' % (k.split('.')[-1], v) for k, v in it.items() if k not in ('ARPT', 'Reason') and not k.endswith('@Type') and k.split('.')[-1] in ('Avg', 'Max', 'Min', 'Trend', 'End_Time', 'Start', 'Reopen'))
            kind = tname + ((' (' + it['Arrival_Departure@Type'] + ')') if it.get('Arrival_Departure@Type') else '')
            rows['%s, %s' % (arp, kind)] = dict(reason=it.get('Reason', ''), stated=stated)
S['faa'] = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), feed_time=snap.get('update_time', 'not returned'), snapshots=snaps, first_snapshot=time.strftime('%d %b %H:%M UTC', time.gmtime(first)), airports_now=len({k.split(',')[0] for k in rows}), now=rows, status=snap.get('status', 'read'))
S['faa_line'] = 'FAA feed: %d snapshots kept since %s. Airports with a program now: %d.' % (snaps, S['faa']['first_snapshot'], S['faa']['airports_now'])
json.dump(S, open('summary_airline.json', 'w'), indent=1)
fp = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()[:12]; st = 'data/nas_state.json'; prev = json.load(open(st)) if os.path.exists(st) else {}
if prev.get('fp') != fp or now - prev.get('t', 0) > 1500:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'airline_live', '--path', os.path.join(H, 'summary_airline.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
    if r.returncode == 0: json.dump(dict(fp=fp, t=now), open(st, 'w'))
    print('nas: snapshot', snaps, len(rows), 'airport programs now', 'published' if r.returncode == 0 else 'publish FAILED')
else: print('nas: snapshot', snaps, len(rows), 'unchanged')
