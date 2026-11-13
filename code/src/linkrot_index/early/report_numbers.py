#!/usr/bin/env python3
"""report_numbers.py: prints the figures of summary_early.json, data/landmarks.json and data/ownname.json in compact form, read from
the files (never retyped). Shares are percent with Wilson 95% intervals."""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AB = {'LIVE_SAME': 'same', 'LIVE_CHANGED': 'chg', 'LIVE_NO_BASELINE': 'nocap', 'REDIRECTED_ELSEWHERE': 'elsew', 'PARKED_OR_FOR_SALE': 'park', 'ROBOTS_DISALLOWED': 'robots',
      'DEAD_DNS': 'dns', 'DEAD_CONNECT': 'conn', 'DEAD_HTTP': 'http', 'TIMEOUT': 'tmo', 'NOTHING_RETURNED': 'ours'}
def p(x): return '%.1f' % (100 * x) if x is not None else '-'
s = json.load(open(os.path.join(ROOT, 'summary_early.json')))
print('updated', s['updated'], 'gate', s['gate'])
for name, smp in s['samples'].items():
    print('\n== %s: read %d of %d drawn%s' % (smp['title'], smp['read'], smp['drawn'], (', era pending %d' % smp['era_pending']) if smp.get('era_pending') else ''))
    for col, c in smp['cols'].items():
        if not c['read']: continue
        parts = []
        for st, ab in AB.items():
            k = c['counts'][st]
            if k: parts.append('%s %d (%s [%s,%s])' % (ab, k, *[p(v) for v in c['shares'][st]]) if not c['too_few'] else '%s %d' % (ab, k))
        print('  %-26s n=%-4d %s' % (col, c['read'], '  '.join(parts)))
        u = c['unchanged']; m = u['median_years']
        if u['live']: print('  %-26s live %d, dated %d, median %s, >=10y %s/%s, LM median %s' % ('', u['live'], u['dated'], m and (m['median'], m['lo'], m['hi']), u['ten_years'][3], u['ten_years'][4], u['last_modified'] and u['last_modified']['median']))
        if c['dead_http_split']: print('  %-26s http split %s' % ('', c['dead_http_split']))
        if c['sensitivity']['compared']: print('  %-26s sensitivity %s' % ('', c['sensitivity']))
rf = s['repeat_floor']; print('\nrepeat floor: read twice %d, flips %d, share %s' % (rf['read_twice'], rf['flips'], [p(v) for v in rf['flip_share']]), rf['pairs'])
if s.get('parked_handcheck'): print('handcheck:', s['parked_handcheck'])
for f in ('landmarks.json', 'ownname.json'):
    fp = os.path.join(ROOT, 'data', f)
    if os.path.exists(fp): print('\n', f, 'present')
