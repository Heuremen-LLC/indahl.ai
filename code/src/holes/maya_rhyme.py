"""CRAZY HAT: Maya calendar restarted at 13.0.0.0.0 (2012-12-21, GMT correlation 584283), laid over every outside glitch we have.
Wayfinder 9/27: "we're not looking for correlation, shit just needs to rhyme a little bit... this proves absolutely nothing."
Outside records only (IBM calibration gaps, NIST beacon gaps, LIGO holes, Braket failures, the 9/24 IBM anomalies) + his own dates."""
import json, datetime as dt, collections
NAMES = ["Imix","Ik'","Ak'bal","K'an","Chikchan","Kimi","Manik'","Lamat","Muluk","Ok","Chuwen","Eb'","B'en","Ix","Men","K'ib'","Kab'an","Etz'nab'","Kawak","Ajaw"]
GLOSS = {"Imix":"crocodile/water","Ik'":"wind","Ak'bal":"night","K'an":"seed","Chikchan":"serpent","Kimi":"death","Manik'":"deer","Lamat":"star/Venus","Muluk":"water/jade","Ok":"dog","Chuwen":"monkey/weaver","Eb'":"road","B'en":"reed","Ix":"jaguar","Men":"eagle","K'ib'":"owl/vulture","Kab'an":"earth/quake","Etz'nab'":"flint/mirror","Kawak":"storm","Ajaw":"lord/sun"}
HAAB = ["Pop","Wo'","Sip","Sotz'","Sek","Xul","Yaxk'in","Mol","Ch'en","Yax","Sak'","Keh","Mak","K'ank'in","Muwan","Pax","K'ayab","Kumk'u","Wayeb'"]
EPOCH = 584283; RESTART = dt.date(2012, 12, 21)
def jdn(d): return d.toordinal() + 1721425
def maya(d):
    n = jdn(d) - EPOCH; t = (n + 3) % 13 + 1; nm = NAMES[(n + 19) % 20]; h = (n + 348) % 365
    s = (d - RESTART).days; lc = [s // 144000, s % 144000 // 7200, s % 7200 // 360, s % 360 // 20, s % 20]
    return {'date': d.isoformat(), 'tz': f"{t} {nm}", 'tz_num': t, 'tz_name': nm, 'haab': f"{h % 20} {HAAB[h // 20]}", 'since': s,
            'lc': ".".join(map(str, [13 + lc[0]] + lc[1:])) if s >= 0 else '(before restart)', 'kin0': s % 20 == 0, 'tun0': s % 360 == 0, 'venus': s % 584, 'tz_round': s // 260, 'tz_pos': s % 260}
assert maya(dt.date(2012, 12, 21))['tz'] == '4 Ajaw' and maya(dt.date(2012, 12, 21))['haab'] == "3 K'ank'in"
print('check 2026-07-05 =', maya(dt.date(2026, 7, 5))['tz'], '(July session said 8 Kan)')
d = lambda s: dt.date.fromisoformat(str(s)[:10])
ev = []
for j in json.load(open('anomaly_jobs.json')): ev.append(('IBM anomaly: ' + j['anomaly'][:40], d(j['created'])))
for x in ('2023-11-11', '2023-11-12', '2023-11-13'): ev.append(('NIST beacon burst (+ H1 camera crash loop)', d(x)))
H = [json.loads(l) for l in open('outside_holes.jsonl')]
def dur(r):
    try: return (dt.datetime.fromisoformat(r['ended']) - dt.datetime.fromisoformat(r['at'])).total_seconds()
    except Exception: return 0
for prov in sorted({r['provider'] for r in H}):
    for r in sorted([r for r in H if r['provider'] == prov], key=dur, reverse=True)[:6]: ev.append((f"{prov} {r.get('device') or ''} longest hole ({dur(r)/3600:.0f} h)", d(r['at'])))
L = [json.loads(l) for l in open('ligo_holes.jsonl')]
k0 = sorted(L[0].keys()); 
def ldur(r):
    for a, b in (('start', 'end'), ('at', 'ended'), ('t0', 't1')):
        if a in r and b in r:
            try: return float(r[b]) - float(r[a])
            except Exception:
                try: return (dt.datetime.fromisoformat(str(r[b])) - dt.datetime.fromisoformat(str(r[a]))).total_seconds()
                except Exception: return 0
    return 0
def ldate(r):
    for a in ('start_utc', 'at', 'start', 't0'):
        if a in r:
            v = r[a]
            try: return d(v)
            except Exception:
                try: return (dt.datetime(1980, 1, 6) + dt.timedelta(seconds=float(v) - 18)).date()   # GPS seconds
                except Exception: pass
    return None
for det in sorted({r.get('detector') or r.get('ifo') or r.get('device') or '?' for r in L}):
    rs = [r for r in L if (r.get('detector') or r.get('ifo') or r.get('device') or '?') == det]
    for r in sorted(rs, key=ldur, reverse=True)[:4]:
        dd = ldate(r)
        if dd: ev.append((f"LIGO {det} longest hole ({ldur(r)/3600:.0f} h)", dd))
try:
    for l in open('../standoff/absence_ledger.jsonl'):
        r = json.loads(l)
        if r.get('provider') == 'aws-braket' and r.get('status') == 'FAILED': ev.append(('Braket task FAILED', d(r['at'])))
except Exception: pass
ev += [('WAYFINDER: the Aug convergence "where nothing happened"', dt.date(2026, 8, 12)), ('WAYFINDER: the flood weekend (rain gauge ~5 in)', dt.date(2026, 9, 27)),
       ('RESTART 13.0.0.0.0', dt.date(2012, 12, 21))]
seen = set(); rows = []
for lab, dd in ev:
    if (lab, dd) in seen: continue
    seen.add((lab, dd)); rows.append((lab, maya(dd)))
rows.sort(key=lambda x: x[1]['date'])
out = ['# THE MAYA RHYME (crazy hat; proves nothing; outside records only)', '', f'{len(rows)} dated events. Calendar restarted at 13.0.0.0.0 = 4 Ajaw 3 K\'ank\'in (2012-12-21).', '',
       '| date | Long Count since restart | Tzolk\'in | Haab\' | event |', '|---|---|---|---|---|']
for lab, m in rows: out.append(f"| {m['date']} | {m['lc']} | {m['tz']} ({GLOSS[m['tz_name']]}) | {m['haab']} | {lab}{' -- WINAL TURNS' if m['kin0'] else ''}{' -- TUN TURNS' if m['tun0'] else ''} |")
c = collections.Counter(n for n, _ in {(m['tz_name'], m['date']) for _, m in rows}); cn = collections.Counter(m['tz'] for _, m in rows)   # distinct dates; cn = collections.Counter(m['tz'] for _, m in rows)
out += ['', 'Day-signs that repeat (distinct dates; 32 dates / 20 signs = ~1.6 each by chance): ' + ', '.join(f"{k} ({GLOSS[k]}) x{v}" for k, v in c.most_common(8)),
        'Exact same Tzolk\'in day on different dates: ' + '; '.join(f"{k}: " + ', '.join(sorted({m['date'] for _, m in rows if m['tz'] == k})) for k, v in cn.items() if len({m['date'] for _, m in rows if m['tz'] == k}) > 1)]
open('maya_rhyme.md', 'w').write('\n'.join(out)); print('\n'.join(out))
