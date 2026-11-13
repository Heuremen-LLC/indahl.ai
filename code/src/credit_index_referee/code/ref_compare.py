import json, sys
D = json.load(open(sys.argv[1])); R = json.load(open(sys.argv[2]))
diffs = []
def cmp(label, a, b):
    if a != b:
        diffs.append(f'{label}: desk={a} referee={b}')
print('desk generated', D['generated'], 'gates', {k: v for k, v in D['gates'].items() if k != 'api_check'})
S = D['source']; st = R['stats']
cmp('rows_in_window', S['rows_in_window'], st['in_window']); cmp('outside_window', S['outside_window'], st['outside'])
cmp('duplicate_ids', S['duplicate_ids'], st['dup_ids_window']); cmp('bad_date', S['bad_date'], st['bad_date'])
print('dup ids whole file (referee)', st['dup_ids_all'])
iv = []
for d, r in zip(D['ruler1'], R['ruler1']):
    y = d['year']
    for k in ('rows', 'not_timely', 'company_months'):
        cmp(f'ruler1 {y} {k}', d[k], r[k])
    cmp(f'ruler1 {y} timely', round(d['timely'], 6), round(r['timely'], 6))
    ob = d.get('outcome_before_gate', d['outcome'])
    cmp(f'ruler1 {y} outcome_before_gate', ob, r['outcome'])
    iv.append((f'ruler1 {y}', d['lo'], d['hi'], round(r['lo'], 6), round(r['hi'], 6), ob, r['outcome'], d['outcome']))
    if y == 2025:
        cmp('ruler1 2025 more_than_99', d['more_than_99']['outcome_display'], r['more_than_99'])
# companies
dk = {(c['company'], c['year']): c for c in D['companies']}
rk = {(c['company'], c['year']): c for c in R['companies']}
for k in sorted(set(dk) | set(rk), key=str):
    if k not in dk: diffs.append(f'company {k} only in referee'); continue
    if k not in rk: diffs.append(f'company {k} only in desk'); continue
    for f in ('rows', 'not_timely', 'months'):
        cmp(f'company {k} {f}', dk[k][f], rk[k][f])
    ob = dk[k].get('outcome_before_gate', dk[k]['outcome'])
    if ob != rk[k]['outcome']:
        diffs.append(f'company {k} outcome desk={ob} [{dk[k]["lo"]},{dk[k]["hi"]}] referee={rk[k]["outcome"]} [{rk[k]["lo"]:.6f},{rk[k]["hi"]:.6f}] band={dk[k].get("band")}')
from collections import Counter
for y in range(2021, 2026):
    dt = Counter(c.get('outcome_before_gate', c['outcome']) for c in D['companies'] if c['year'] == y)
    dt['too_few'] = D['tally_companies'][str(y)].get('too_few')
    rt = dict(R['tally'][str(y)])
    cmp(f'tally {y}', dict(sorted(dt.items())), dict(sorted(rt.items())))
dk = {(c['company'], c['family']): c for c in D['comp_fam']}
rk = {(c['company'], c['family']): c for c in R['comp_fam']}
cmp('comp_fam keys', len(dk), len(rk))
for k in sorted(set(dk) | set(rk), key=str):
    if k not in dk or k not in rk: diffs.append(f'comp_fam {k} only in {"referee" if k not in dk else "desk"}'); continue
    for f in ('rows', 'not_timely', 'months'):
        cmp(f'comp_fam {k} {f}', dk[k][f], rk[k][f])
    ob = dk[k].get('outcome_before_gate', dk[k]['outcome'])
    if ob != rk[k]['outcome']:
        diffs.append(f'comp_fam {k} outcome desk={ob} [{dk[k]["lo"]},{dk[k]["hi"]}] referee={rk[k]["outcome"]} [{rk[k]["lo"]:.6f},{rk[k]["hi"]:.6f}]')
cmp('tally_cf too_few', D['tally_company_family_2025'].get('too_few'), R['tally_cf'].get('too_few'))
for d, r in zip(D['bureau_window'], R['bureau_window']):
    for f in ('rows', 'not_timely', 'months'):
        cmp(f'bureau_window {d["company"]} {f}', d[f], r[f])
    cmp(f'bureau_window {d["company"]} band', [round(x, 6) for x in d['band']], [round(x, 6) for x in r['band']])
    cmp(f'bureau_window {d["company"]} outcome', d['outcome_display'], r['outcome'])
for d, r in zip(D['others_nt'], R['others_nt']):
    for f in ('rows', 'not_timely'):
        cmp(f'others_nt {d["year"]} {f}', d[f], r[f])
for d, r in zip(D['responses'], R['responses']):
    for dc in d['cells']:
        rc = [c for c in r['cells'] if c['group'] == dc['group']][0]
        cmp(f'resp {d["year"]} {dc["group"]} rows', dc['rows'], rc['rows'])
        cmp(f'resp {d["year"]} {dc["group"]} company_months', dc['company_months'], rc['company_months'])
        rmap = {s['category']: s['rows'] for s in rc['shares']}
        for s in dc['shares']:
            cmp(f'resp {d["year"]} {dc["group"]} {s["category"]}', s['rows'], rmap.get(s['category']))
        extra = {k: v for k, v in rmap.items() if v and k not in {s['category'] for s in dc['shares']}}
        if extra: diffs.append(f'resp {d["year"]} {dc["group"]} categories missing from desk: {extra}')
for d, r in zip(D['q1c']['lag'], R['lag']):
    cmp(f'lag {d["company"]} {d["year"]}', d['buckets'], r['buckets'])
for d, r in zip(D['q1c']['bureau_credit_reporting_not_timely'], R['bcr']):
    cmp(f'bcr {d["company"]} {d["year"]}', (d['rows'], d['not_timely']), (r['rows'], r['not_timely']))
for d, r in zip(D['q1d'], R['q1d']):
    cmp(f'q1d {d["year"]}', (d['rows'], d['within_1_day'], d['sent_before_received']), (r['rows'], r['within_1_day'], r['sent_before_received']))
    if d['year'] == 2025:
        cmp('q1d 2025 outcome', d.get('outcome_before_gate', d['outcome']), r['outcome'])
        iv.append(('q1d 2025', d['lo'], d['hi'], round(r['lo'], 6), round(r['hi'], 6), d.get('outcome_before_gate'), r['outcome'], d['outcome']))
print('DIFFS', len(diffs))
for x in diffs: print(' ', x)
print('INTERVALS (label, desk lo, desk hi, ref lo, ref hi, desk outcome_before_gate, ref outcome, desk published outcome)')
for x in iv: print(' ', x)
