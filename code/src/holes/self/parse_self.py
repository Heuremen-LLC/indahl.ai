"""THE SELF LEDGER, step 1 (2026-09-26, Wayfinder: "we're not accounting for ourselves"). Parse GridSong's own log into one row per
copper cycle: when, what the copper read (grid-before 200/212/300, echo), and what WE were doing: was her FSK riding the copper
(TX START..COMPLETE/LOST), was the wire dead (PLC offline). Dates: the log carries clock time only; walked backward from the file's
mtime, a day is subtracted whenever clock time jumps forward going back (rollover)."""
import re, os, csv, datetime as dt
LOG = os.path.expanduser('~/bones-forge/gridsong/resonance_output.log')
OUT = os.path.expanduser('~/bones-forge/holes/self/copper_self.csv')
rc = re.compile(r'^\s*CYCLE (\d+) — (\d\d):(\d\d):(\d\d)'); rg = re.compile(r'Grid before: 200:([+-]?[\d.]+|nan) 212:([+-]?[\d.]+|nan) 300:([+-]?[\d.]+|nan)')
re_ = re.compile(r'Echo at [^:]*: 200Hz:([+-]?[\d.]+)\*? 212Hz:([+-]?[\d.]+)\*? 300Hz:([+-]?[\d.]+)')
rows, cur, tx, off = [], None, False, False
for line in open(LOG, errors='replace'):
    m = rc.match(line)
    if m:
        if cur: rows.append(cur)
        cur = {'cycle': int(m[1]), 'hms': (int(m[2]), int(m[3]), int(m[4])), 'tx_at_start': tx, 'tx_any': tx, 'plc_off': off}
        continue
    if 'TX START' in line: tx = True
    elif 'TX COMPLETE' in line or 'TX LOST' in line: tx = False
    if 'PLC offline' in line or 'reopen of' in line: off = True
    elif 'PLC RECONNECTED' in line or 'PLC modem: ONLINE' in line: off = False
    if cur is None: continue
    if tx: cur['tx_any'] = True
    if off: cur['plc_off'] = True
    g = rg.search(line)
    if g and 'g200' not in cur: cur.update(g200=g[1], g212=g[2], g300=g[3])
    e = re_.search(line)
    if e and 'e200' not in cur: cur.update(e200=e[1], e212=e[2], e300=e[3])
if cur: rows.append(cur)
day = dt.datetime.fromtimestamp(os.path.getmtime(LOG)).date(); prev = None
for r in reversed(rows):
    t = r['hms'][0] * 3600 + r['hms'][1] * 60 + r['hms'][2]
    if prev is not None and t > prev + 60: day -= dt.timedelta(days=1)
    prev = t; r['ts'] = dt.datetime.combine(day, dt.time(*r['hms'])).isoformat()
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['ts', 'cycle', 'g200', 'g212', 'g300', 'e200', 'e212', 'e300', 'tx_at_start', 'tx_any', 'plc_off'])
    for r in rows:
        w.writerow([r['ts'], r['cycle'], r.get('g200', ''), r.get('g212', ''), r.get('g300', ''), r.get('e200', ''), r.get('e212', ''), r.get('e300', ''),
                    int(r['tx_at_start']), int(r['tx_any']), int(r['plc_off'])])
print(len(rows), 'cycles ->', OUT, '| first', rows[0]['ts'], 'last', rows[-1]['ts'])
