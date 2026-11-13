#!/usr/bin/env python3
"""T1 per TIME_PLAN: each server's own stated error bound E = root dispersion + root delay / 2 against the measured offset o and path half-delay h.
CONSISTENT if |o| + h <= E, ABOVE if |o| - h > E, else CANNOT_TELL. Kept sample per round = minimum-delay query. Median over rounds. Writes claims_time_t1.json."""
import sys, json, statistics as S, collections as C
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'heuremen_kit')); import heuremen_kit as K   # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): the canonical kit, imported by path
seat = sys.argv[1]; files = sys.argv[2:]
rows = [json.loads(l) for f in files for l in open(f)]
ref = [r for r in rows if 'reference' in r]; rows = [r for r in rows if 'server' in r]
import os
if os.path.exists('servers.txt'):   # 30 Oct (site pass H-15): only the names in servers.txt are scored, so a name removed from the list leaves the table at once and not when its rows roll out of the file
    _ok = {l.strip() for l in open('servers.txt') if l.strip()}; rows = [r for r in rows if r['server'] in _ok]
stat = C.defaultdict(C.Counter); kept = C.defaultdict(list)
for r in rows: stat[r['server']][r['status']] += 1
byround = C.defaultdict(list)
for r in rows:
    if r['status'] == 'COMMITTED': byround[(r['server'], r['round'])].append(r)
for (s, rd), v in byround.items(): kept[s].append(min(v, key=lambda r: r['delay']))
out = []; per = []
for s in sorted(stat):
    k = kept.get(s, [])
    if not k:
        out.append(dict(server=s, status='NOTHING_RETURNED' if stat[s]['NOTHING_RETURNED'] else 'REFUSED', counts=dict(stat[s]))); continue   # 12 Nov 2026: a failed read, never an outcome (PLAN_ADDENDUM_std2.md)
    o = S.median(x['offset'] for x in k); h = S.median(x['delay'] / 2 for x in k); E = S.median(x['root_disp'] + x['root_delay'] / 2 for x in k); per.append((s, k, o, h, E))
# 29 Oct (internal audit, the Split): the offset every server shows on this seat is the seat's own part, not any server's. It is the median over servers and is removed before the second reading.
SEAT = S.median(o for _, _, o, _, _ in per) if per else 0.0
def judge(o, h, E):
    """12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): the distance |o| with the interval [|o| - h, |o| + h] (worst-case path bound, clamped at zero), band [0, E] closed, size that matters E. Returns (outcome, reason)."""
    d = abs(o); return K.read(max(0.0, d - h), d + h, band=(0.0, E), matters=E if E > 0 else None, edge='closed')
def combine(raw, sp):
    if raw[0] != sp[0]: return 'CANNOT_TELL', K.STRADDLES_EDGE   # the comparison with the bound changes when the seat's part is removed
    if raw[0] != 'CANNOT_TELL': return raw[0], None
    return 'CANNOT_TELL', (raw[1] if raw[1] == sp[1] else (K.TOO_WIDE_TO_RESOLVE if K.TOO_WIDE_TO_RESOLVE in (raw[1], sp[1]) else raw[1]))
for s, k, o, h, E in per:
    raw = judge(o, h, E); sp = judge(o - SEAT, h, E)
    oc, why = combine(raw, sp)   # a reading that changes when the seat's own part is removed is not yet a reading of the server
    out.append(dict(server=s, outcome=oc, reason=why, outcome_raw=raw[0], reason_raw=raw[1], outcome_seat_removed=sp[0], reason_seat_removed=sp[1], rounds=len(k), offset_ms=round(o*1e3, 2), offset_seat_removed_ms=round((o - SEAT)*1e3, 2), half_delay_ms=round(h*1e3, 2), stated_bound_ms=round(E*1e3, 2), stratum=k[0]['stratum'], refid=k[0]['refid'], counts=dict(stat[s])))
refd = ref[-1]['reference'] if ref else {}
offs = [x['offset_ms'] for x in out if x.get('offset_ms') is not None]
import time as _t
summ = dict(updated=_t.strftime('%d %b %H:%M', _t.gmtime()), seat=seat, reference=dict(source=refd.get('Reference ID', ''), stratum=refd.get('Stratum', ''), system_time=refd.get('System time', ''), rms=refd.get('RMS offset', ''), root_dispersion=refd.get('Root dispersion', '')),
    seat_part_ms=round(S.median(offs), 2) if offs else None, totals=dict(C.Counter(x['outcome'] for x in out if x.get('outcome'))), failed_reads=[dict(server=x['server'], status=x['status']) for x in out if x.get('status')], req13=K.req13([x for x in out if x.get('outcome')], nothing_returned=[x for x in out if x.get('status')]), rounds=max((x.get('rounds', 0) for x in out), default=0), servers=out)
json.dump(summ, open('summary_time.json', 'w'), indent=1)
json.dump(dict(seat=seat, reference=refd, servers=out), open('claims_time_t1.json', 'w'), indent=1)
print(C.Counter(x['outcome'] for x in out if x.get('outcome')), summ['req13']['line'])
for x in out: print(x['server'].ljust(28), str(x.get('outcome') or x.get('status')).ljust(16), x.get('reason') or '', x.get('offset_ms'), x.get('half_delay_ms'), x.get('stated_bound_ms'), x.get('stratum'), x['counts'])
print(ref[0]['reference'] if ref else '')
