"""Referee second pass: final outcomes from the independent implementation (Addendum 4 and 6.3 notes as listed in PLAN.md, then 6.7), counted."""
import sys, os, json, collections as C
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from second_pass import *
from second_pass_share import share
NOTES = [  # PLAN.md Addendum 4.3 and 6.3: (platform, periods, measures, direction)
    ('Snapchat', ('2025H2', '2026H1'), ('total', 'solely', 'not', 'share'), 'inflated'), ('Snapchat', ('2026H1',), ('total', 'not', 'share'), 'inflated'),
    ('Snapchat', ('2025H2', '2026H1'), ('notice_tf',), 'deflated'), ('Snapchat', ('2025H2',), ('notice', 'notice_tf'), 'deflated'),
    ('X', ('2025H2', '2026H1'), ('own_auto',), 'inflated'), ('Amazon Store', ('2025H2', '2026H1'), ('own_illegal',), 'deflated'),
    ('Amazon Store', ('2025H2', '2026H1'), ('own_tc',), 'inflated'), ('Booking.com', ('2025H2', '2026H1'), ('notice', 'notice_tf'), 'inflated'),
    ('Facebook', ('2025H2', '2026H1'), ('total', 'solely', 'not', 'own', 'own_tc', 'own_auto', 'share'), 'both'),
    ('Instagram', ('2025H2', '2026H1'), ('total', 'solely', 'not', 'own', 'own_tc', 'own_auto', 'share'), 'both')]
HIT = {'inflated': ('BELOW', 'CONSISTENT'), 'deflated': ('ABOVE', 'CONSISTENT'), 'both': ('ABOVE', 'BELOW', 'CONSISTENT')}
out = {}
views = [(('main', s), s) for s in NAMES] + [(('ads', s), s + ' (ads)') for s in ADS] + [(('combined', None), 'Facebook and Instagram')]
for view, name in views:
    meas = ('total', 'solely', 'not', 'own', 'own_illegal', 'own_tc', 'own_auto', 'notice', 'notice_tf') if view[0] == 'main' else (('total', 'solely', 'not', 'own_tc') if view[0] == 'ads' else ('total', 'solely', 'not', 'own', 'own_tc', 'own_auto'))
    for per in PER:
        if view[0] != 'combined' and '%s|%s' % (view[1], per) not in ST:
            if view[0] == 'main':
                for m in meas: out[(name, per, m)] = 'NOTHING_RETURNED'
            continue
        for m in meas: out[(name, per, m)] = row(view, per, m)['oc']
        sh = share(view, per)
        if sh: out[(name, per, 'share')] = sh['oc']
for (p, pers, ms, dr) in NOTES:
    for per in pers:
        for m in ms:
            if out.get((p, per, m)) in HIT[dr]: out[(p, per, m)] = 'CANNOT_TELL'
splits = 0
for (p, per, m), o in list(out.items()):
    for a, b in (('solely', 'not'), ('own_illegal', 'own_tc')):
        if m == a and {out.get((p, per, a)), out.get((p, per, b))} == {'ABOVE', 'BELOW'}:
            out[(p, per, a)] = out[(p, per, b)] = 'CANNOT_TELL'; splits += 1
# Wikipedia rows (no database name: database 0) are taken as published
rows = json.load(open(os.path.join(DSA, 'data', 'dsa.json')))
for r in rows:
    if r['platform'] == 'Wikipedia': out[(r['platform'], r['period'], r['measure'])] = r['outcome']
pub = {(r['platform'], r['period'], r['measure']): r['outcome'] for r in rows if r.get('measure') != 'label_split'}
miss = [k for k in pub if k not in out]; extra = [k for k in out if k not in pub]
diff = [(k, out[k], pub[k]) for k in pub if k in out and out[k] != pub[k]]
grp = lambda k: 'ads' if k[0].endswith('(ads)') else ('combined' if k[0] == 'Facebook and Instagram' else 'original')
for g in ('original', 'ads', 'combined'): print(g, dict(C.Counter(v for k, v in out.items() if grp(k) == g)))
print('label splits', splits, '| rows not computed', miss[:5], '| extra', extra[:5], '| outcome differences', len(diff), diff[:10])
