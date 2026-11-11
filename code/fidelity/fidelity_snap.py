#!/usr/bin/env python3
"""fidelity_snap.py (11 Nov 2026): dated copies of the three NCHS XLSX workbooks the FIDELITY desk reads (state marriage rates, state divorce rates, national rates).
The tick_bus rider runs it every 264 ticks (about a day). A file is written to data/snapshots/ only when its bytes differ from the newest copy of the same workbook,
and every pull is logged in data/snapshots/pull_log.jsonl. Snapshot only: it never builds, scores, publishes or touches the ledger, and it never reads any key.
At most one pull per 20 hours (data/snapshots/last_pull.json), --force ignores that. --selftest: no network. 2024 state counts stay cannot tell until NCHS publishes them."""
import os, sys, json, time, hashlib, fcntl, glob, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
SD = 'data/snapshots'; os.makedirs(SD, exist_ok=True)
B = 'https://www.cdc.gov/nchs/data/dvs/marriage-divorce/'
FILES = ['state-marriage-rates-90-95-00-24.xlsx', 'state-divorce-rates-90-95-00-24.xlsx', 'national-marriage-divorce-rates-00-24.xlsx']
# no custom User-Agent: cdc.gov answers 403 to the descriptive agent strings tried and 200 to the HTTP library's own default, which is what this sends
def newest(name):
    fs = sorted(glob.glob('%s/*_%s' % (SD, name))); return hashlib.sha256(open(fs[-1], 'rb').read()).hexdigest() if fs else None
def is_xlsx(b): return b[:2] == b'PK' and len(b) > 5000
def selftest():
    ok = is_xlsx(b'PK' + b'0' * 6000) and not is_xlsx(b'<html>') and not is_xlsx(b'PK12')
    ok &= all(f.endswith('.xlsx') and '/' not in f for f in FILES) and B.startswith('https://www.cdc.gov/')
    print('fidelity_snap selftest', 'PASSED' if ok else 'FAILED'); return ok
if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
lk = open('.fidelity_snap.lock', 'a')
try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: sys.exit(0)
LP = os.path.join(SD, 'last_pull.json'); now = time.time()
try: last = json.load(open(LP))['t']
except Exception: last = 0
if now - last < 20 * 3600 and '--force' not in sys.argv: sys.exit(0)
day = time.strftime('%Y%m%d', time.gmtime(now)); log = []
for name in FILES:
    rec = dict(file=name, at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)))
    try:
        b = urllib.request.urlopen(urllib.request.Request(B + name), timeout=60).read()
        if not is_xlsx(b): rec['result'] = 'not an xlsx, nothing kept'
        else:
            h = hashlib.sha256(b).hexdigest(); rec['sha256'] = h
            if h == newest(name): rec['result'] = 'unchanged'
            else:
                dst = '%s/%s_%s' % (SD, day, name)
                if os.path.exists(dst): dst = '%s/%sT%s_%s' % (SD, day, time.strftime('%H%M%S', time.gmtime(now)), name)
                open(dst, 'wb').write(b); rec['result'] = 'new copy ' + os.path.basename(dst)
    except Exception as ex: rec['result'] = 'pull failed: %s' % type(ex).__name__
    log.append(rec); time.sleep(2)
with open(os.path.join(SD, 'pull_log.jsonl'), 'a') as f:
    for r in log: f.write(json.dumps(r) + '\n')
if any(not r['result'].startswith('pull failed') for r in log): json.dump({'t': now}, open(LP, 'w'))
print(json.dumps(log))
