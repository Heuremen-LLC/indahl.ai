#!/usr/bin/env python3
"""audit.py: IBM published-calibration audit per AUDIT_PLAN.md. Reads records/*/*.json.gz only. Writes audit.json."""
import gzip, json, glob, os, datetime as D, collections as C
H = os.path.dirname(os.path.abspath(__file__)); P = D.datetime.fromisoformat
out = {}; allflags = []
for b in sorted(os.listdir(os.path.join(H, 'records'))):
    fs = sorted(glob.glob(os.path.join(H, 'records', b, '*.json.gz'))); recs = [json.load(gzip.open(f)) for f in fs]
    a = dict(records=len(recs), latest_stamp=recs[-1]['last_update_date'], flags_a=[], flags_b=[], age24=C.Counter(), age7d=C.Counter(), entries=0, restamps=[])
    flat = []
    for r in recs:
        st = P(r['last_update_date']); d = {}
        for i, q in enumerate(r['qubits']):
            e = {x['name']: x for x in q}
            for x in q:
                d[(i, x['name'])] = (x['value'], x['date'])
            if 'T1' in e and 'T2' in e:
                ratio = e['T2']['value'] / e['T1']['value']; gap = abs((P(e['T1']['date']) - P(e['T2']['date'])).total_seconds()) / 3600
                if ratio > 2.0: a['flags_a'].append(dict(stamp=r['last_update_date'], qubit=i, ratio=round(ratio, 3), t1=round(e['T1']['value'], 3), t2=round(e['T2']['value'], 3), outcome='ABOVE' if ratio > 2.5 else 'CANNOT_TELL'))
                if gap > 24: a['flags_b'].append(dict(stamp=r['last_update_date'], qubit=i, gap_h=round(gap, 1), t1_date=e['T1']['date'], t2_date=e['T2']['date']))
        flat.append(d)
    lat = recs[-1]; st = P(lat['last_update_date'])
    for i, q in enumerate(lat['qubits']):
        for x in q:
            if x.get('date'):
                a['entries'] += 1; age = (st - P(x['date'])).total_seconds() / 3600
                if age > 24: a['age24'][x['name']] += 1
                if age > 168: a['age7d'][x['name']] += 1
    for x, y in zip(flat, flat[1:]):
        ch = sum(1 for k in set(x) & set(y) if x[k] != y[k]); a['restamps'].append('CHANGED' if ch else 'NO_CHANGE')
    a['age24'] = dict(a['age24']); a['age7d'] = dict(a['age7d'])
    for f in a['flags_a']: f['persistent'] = sum(1 for g in a['flags_a'] if g['qubit'] == f['qubit']) >= 2
    out[b] = a
json.dump(out, open(os.path.join(H, 'audit.json'), 'w'), indent=1)
for b, a in out.items():
    print(b, 'records', a['records'], '| A ABOVE', sum(f['outcome'] == 'ABOVE' for f in a['flags_a']), 'CANNOT_TELL', sum(f['outcome'] == 'CANNOT_TELL' for f in a['flags_a']), '| B mismatch', len(a['flags_b']), '| >24h', sum(a['age24'].values()), '>7d', sum(a['age7d'].values()), 'of', a['entries'], '| restamps', C.Counter(a['restamps']))

# ---- summary for the QIA page: latest record per processor, ABOVE flags with their raw entries, published to KV qia_audit (plan: AUDIT_PLAN.md)
import subprocess, time
rows = []; flagged = []
for b, a in out.items():
    lat = a['latest_stamp']; fa = [f for f in a['flags_a'] if f['stamp'] == lat]; fb = [f for f in a['flags_b'] if f['stamp'] == lat]
    rc = C.Counter(a['restamps'])
    rows.append(dict(backend=b, stamp=lat, records=a['records'], entries=a['entries'], above=sum(f['outcome'] == 'ABOVE' for f in fa), cannot_tell=sum(f['outcome'] == 'CANNOT_TELL' for f in fa),
                     mismatch=len(fb), max_gap_h=max([f['gap_h'] for f in fb], default=0), age24=sum(a['age24'].values()), age7d=sum(a['age7d'].values()),
                     restamps_no_change=rc['NO_CHANGE'], restamps_changed=rc['CHANGED']))
    r = json.load(gzip.open(sorted(glob.glob(os.path.join(H, 'records', b, '*.json.gz')))[-1]))
    for f in fa:
        if f['outcome'] != 'ABOVE': continue
        e = {x['name']: x for x in r['qubits'][f['qubit']]}
        seen = sum(1 for g in a['flags_a'] if g['qubit'] == f['qubit'] and g['outcome'] == 'ABOVE')
        flagged.append(dict(backend=b, qubit=f['qubit'], ratio=f['ratio'], t1=f['t1'], t1_date=e['T1']['date'], t2=f['t2'], t2_date=e['T2']['date'], records_seen=seen, records=a['records']))
summ = dict(updated=D.datetime.now(D.timezone.utc).strftime('%d %b %H:%M'), processors=rows, flagged=flagged)
json.dump(summ, open(os.path.join(H, 'audit_summary.json'), 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'qia_audit', '--path', os.path.join(H, 'audit_summary.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                   cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
print('qia_audit', 'published' if p.returncode == 0 else 'publish FAILED')
