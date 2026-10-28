#!/usr/bin/env python3
"""T1 per TIME_PLAN: each server's own stated error bound E = root dispersion + root delay / 2 against the measured offset o and path half-delay h.
CONSISTENT if |o| + h <= E, ABOVE if |o| - h > E, else CANNOT_TELL. Kept sample per round = minimum-delay query. Median over rounds. Writes claims_time_t1.json."""
import sys, json, statistics as S, collections as C
seat = sys.argv[1]; files = sys.argv[2:]
rows = [json.loads(l) for f in files for l in open(f)]
ref = [r for r in rows if 'reference' in r]; rows = [r for r in rows if 'server' in r]
stat = C.defaultdict(C.Counter); kept = C.defaultdict(list)
for r in rows: stat[r['server']][r['status']] += 1
byround = C.defaultdict(list)
for r in rows:
    if r['status'] == 'COMMITTED': byround[(r['server'], r['round'])].append(r)
for (s, rd), v in byround.items(): kept[s].append(min(v, key=lambda r: r['delay']))
out = []
for s in sorted(stat):
    k = kept.get(s, [])
    if not k:
        out.append(dict(server=s, outcome='NOTHING_RETURNED' if stat[s]['NOTHING_RETURNED'] else 'REFUSED', counts=dict(stat[s]))); continue
    o = S.median(x['offset'] for x in k); h = S.median(x['delay'] / 2 for x in k); E = S.median(x['root_disp'] + x['root_delay'] / 2 for x in k)
    oc = 'CONSISTENT' if abs(o) + h <= E else ('ABOVE' if abs(o) - h > E else 'CANNOT_TELL')
    out.append(dict(server=s, outcome=oc, rounds=len(k), offset_ms=round(o*1e3, 2), half_delay_ms=round(h*1e3, 2), stated_bound_ms=round(E*1e3, 2), stratum=k[0]['stratum'], refid=k[0]['refid'], counts=dict(stat[s])))
refd = ref[-1]['reference'] if ref else {}
offs = [x['offset_ms'] for x in out if x.get('offset_ms') is not None]
import time as _t
summ = dict(updated=_t.strftime('%d %b %H:%M', _t.gmtime()), seat=seat, reference=dict(source=refd.get('Reference ID', ''), stratum=refd.get('Stratum', ''), system_time=refd.get('System time', ''), rms=refd.get('RMS offset', ''), root_dispersion=refd.get('Root dispersion', '')),
    seat_part_ms=round(S.median(offs), 2) if offs else None, totals=dict(C.Counter(x['outcome'] for x in out)), rounds=max((x.get('rounds', 0) for x in out), default=0), servers=out)
json.dump(summ, open('summary_time.json', 'w'), indent=1)
json.dump(dict(seat=seat, reference=refd, servers=out), open('claims_time_t1.json', 'w'), indent=1)
print(C.Counter(x['outcome'] for x in out))
for x in out: print(x['server'].ljust(28), x['outcome'].ljust(16), x.get('offset_ms'), x.get('half_delay_ms'), x.get('stated_bound_ms'), x.get('stratum'), x['counts'])
print(ref[0]['reference'] if ref else '')
