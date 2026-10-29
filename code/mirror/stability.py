#!/usr/bin/env python3
"""stability.py: IBM calibration stability index per STABILITY_PLAN.md. Reads records/*/*.json.gz, writes stability_summary.json and publishes KV qia_stability."""
import gzip, json, glob, os, sys, subprocess, statistics as S, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); import heuremen_kit as K
P = D.datetime.fromisoformat; rows = []
for b in sorted(os.listdir(os.path.join(H, 'records'))):
    fs = sorted(glob.glob(os.path.join(H, 'records', b, '*.json.gz'))); recs = [json.load(gzip.open(f)) for f in fs]; first, last = recs[0], recs[-1]
    span = (P(last['last_update_date']) - P(first['last_update_date'])).total_seconds() / 86400
    def ent(r):
        d = {}
        for i, q in enumerate(r['qubits']):
            for e in q: d[(i, e['name'])] = e
        return d
    fe, le = ent(first), ent(last); common = [i for i in range(len(last['qubits'])) if (i, 'T1') in fe and (i, 'T1') in le and (i, 'T2') in fe and (i, 'T2') in le]
    r1 = sum(1 for i in common if fe[(i, 'T1')]['date'] != le[(i, 'T1')]['date']); r2 = sum(1 for i in common if fe[(i, 'T2')]['date'] != le[(i, 'T2')]['date'])
    st = P(last['last_update_date']); ages1 = []; ages2 = []; apart = 0; n12 = 0
    for i in range(len(last['qubits'])):
        if (i, 'T1') in le and (i, 'T2') in le:
            n12 += 1; a1 = (st - P(le[(i, 'T1')]['date'])).total_seconds() / 3600; a2 = (st - P(le[(i, 'T2')]['date'])).total_seconds() / 3600; ages1.append(a1); ages2.append(a2)
            apart += abs((P(le[(i, 'T1')]['date']) - P(le[(i, 'T2')]['date'])).total_seconds()) > 86400
    bad2 = set(); bad25 = set(); gap = set()
    for r in recs:
        d = ent(r)
        for i in range(len(r['qubits'])):
            if (i, 'T1') in d and (i, 'T2') in d:
                ratio = d[(i, 'T2')]['value'] / d[(i, 'T1')]['value']
                if ratio > 2: bad2.add(i)
                if ratio > 2.5: bad25.add(i)
                if abs((P(d[(i, 'T1')]['date']) - P(d[(i, 'T2')]['date'])).total_seconds()) > 86400: gap.add(i)
    clean = n12 - len(bad2 | gap); small = len(recs) < 20 or span < 14; w = lambda k, n: [round(x, 4) for x in K.wilson(k, n)]
    rows.append(dict(backend=b, records=len(recs), first=first['last_update_date'][:16], last=last['last_update_date'][:16], days=round(span, 2), qubits=len(last['qubits']), too_few=small,
                     remeasured_t1=[r1, len(common)] + w(r1, len(common)), remeasured_t2=[r2, len(common)] + w(r2, len(common)), apart=[apart, n12] + w(apart, n12),
                     median_age_t1_h=round(S.median(ages1), 1), median_age_t2_h=round(S.median(ages2), 1), flagged_over_2=len(bad2), flagged_over_2_5=len(bad25), clean_throughout=clean))
out = dict(updated=D.datetime.now(D.timezone.utc).strftime('%d %b %H:%M'), processors=rows); json.dump(out, open(os.path.join(H, 'stability_summary.json'), 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'qia_stability', '--path', os.path.join(H, 'stability_summary.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
for r in rows: print(r['backend'], 'records', r['records'], 'days', r['days'], 't1 remeasured', r['remeasured_t1'][:2], 'apart', r['apart'][:2], 'flagged>2', r['flagged_over_2'], '>2.5', r['flagged_over_2_5'], 'clean', r['clean_throughout'], 'TOO FEW' if r['too_few'] else '')
print('qia_stability', 'published' if p.returncode == 0 else 'publish FAILED')
