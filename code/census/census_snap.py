#!/usr/bin/env python3
"""census_snap.py: dated copies of the Census EITS economic-indicator responses, error fields included. EITS serves only the current vintage, so a copy not made on release day loses the as-printed value and error figure.
At most one pull per 6 hours (data/snapshots/last_pull.json). A response is written only when its rows differ from the last copy of the same endpoint (every pull is logged in data/snapshots/pull_log.jsonl). Files are gzip, tracked in git.
The Census API key is read from the owner's accounts folder at call time. It is never printed, never saved, and stripped from every saved URL. --force: ignore the 6 hour limit. --selftest: no network.
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import os, sys, json, gzip, time, hashlib, urllib.request, urllib.parse, fcntl, re
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
SD = 'data/snapshots'; os.makedirs(SD, exist_ok=True)
KEYFILE = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/census_api_key.txt')
UA = 'indahl.ai-census-desk (Heuremen LLC; snapshots of public Census API series)'
B = 'https://api.census.gov/data/timeseries/'
G = 'cell_value,data_type_code,category_code,geo_level_code,error_data,seasonally_adj,time_slot_id'
ENDPOINTS = {  # name: url without key
 'ressales_values': B + 'eits/ressales?get=%s&time=from+2016-01&error_data=no' % G,
 'ressales_errors': B + 'eits/ressales?get=%s&time=from+2016-01&error_data=yes' % G,
 'resconst_values': B + 'eits/resconst?get=%s&time=from+2016-01&error_data=no&for=us:*' % G,
 'resconst_errors': B + 'eits/resconst?get=%s&time=from+2016-01&error_data=yes&for=us:*' % G,
 'marts_values': B + 'eits/marts?get=%s&time=from+2016-01&error_data=no&for=us:*' % G,
 'marts_errors': B + 'eits/marts?get=%s&time=from+2016-01&error_data=yes&for=us:*' % G,
 'advm3_values': B + 'eits/advm3?get=%s&time=from+2024-01&error_data=no&for=us:*' % G,
 'vip_values': B + 'eits/vip?get=%s&time=from+2024-01&error_data=no&for=us:*' % G,
 'vip_errors': B + 'eits/vip?get=%s&time=from+2024-01&error_data=yes&for=us:*' % G,
 'trade_imports_enduse': B + 'intltrade/imports/enduse?get=I_ENDUSE,GEN_VAL_MO&time=from+2024-01&COMM_LVL=EU1&SUMMARY_LVL=DET',
 'trade_exports_enduse': B + 'intltrade/exports/enduse?get=E_ENDUSE,ALL_VAL_MO&time=from+2024-01&COMM_LVL=EU1&SUMMARY_LVL=DET',
}
def strip_key(u): return re.sub(r'([?&])key=[^&]*&?', r'\1', u).rstrip('?&')
def selftest():
    ok = True
    u = strip_key('https://x/y?get=a&key=SECRET123&time=2020'); ok &= ('SECRET' not in u and u == 'https://x/y?get=a&time=2020')
    ok &= strip_key('https://x/y?get=a&key=Z') == 'https://x/y?get=a'
    for n, u in ENDPOINTS.items(): ok &= 'key=' not in u
    print('census_snap selftest', 'PASSED' if ok else 'FAILED'); return ok
if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
lk = open('.census_snap.lock', 'a')
try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: sys.exit(0)
LP = os.path.join(SD, 'last_pull.json')
now = time.time()
try: last = json.load(open(LP))['t']
except Exception: last = 0
if now - last < 6 * 3600 and '--force' not in sys.argv: sys.exit(0)
try: key = open(KEYFILE).read().strip()
except Exception: key = None
def latest_hash(name):
    fs = sorted(f for f in os.listdir(SD) if f.endswith('_%s.json.gz' % name))
    if not fs: return None
    try: return json.load(gzip.open(os.path.join(SD, fs[-1])))['rows_sha256']
    except Exception: return None
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(now)); log = []
for name, url in ENDPOINTS.items():
    full = url + (('&' if '?' in url else '?') + 'key=' + urllib.parse.quote(key)) if key else url
    rec = dict(t=stamp, name=name)
    try:
        req = urllib.request.Request(full, headers={'User-Agent': UA})
        raw = urllib.request.urlopen(req, timeout=90).read()
        rows = json.loads(raw)
        sha = hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
        rec.update(rows=len(rows) - 1, rows_sha256=sha)
        if sha == latest_hash(name): rec['written'] = False
        else:
            doc = dict(name=name, url=strip_key(url), fetched_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)), rows_sha256=sha, rows=rows)
            with gzip.open(os.path.join(SD, '%s_%s.json.gz' % (stamp, name)), 'wt') as f: json.dump(doc, f, separators=(',', ':'))
            rec['written'] = True
    except Exception as ex:
        rec.update(error=type(ex).__name__ + ' ' + re.sub(r'key=[^&\s]+', 'key=X', str(ex))[:120], written=False)
    log.append(rec); time.sleep(1.5)
with open(os.path.join(SD, 'pull_log.jsonl'), 'a') as f:
    for r in log: f.write(json.dumps(r) + '\n')
json.dump(dict(t=now, stamp=stamp), open(LP, 'w'))
print(json.dumps([{k: v for k, v in r.items() if k != 'rows_sha256'} for r in log]))
