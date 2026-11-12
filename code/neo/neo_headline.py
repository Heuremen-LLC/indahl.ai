"""neo_headline.py: the NEO headline (big number and line) from the summary as served at /neo/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. 10 Nov 2026, referee R4: the split by lead and the dependence on one
archived copy are in the line itself. Standard library only."""
import time
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def rw(c, outcome='outcome', reason='reason'):
    """The reading word with its Faults and Guards 2.0 reason beside it when the outcome is CANNOT_TELL (feeds from before 12 Nov 2026 carry no reason)."""
    w = WORD.get(c[outcome], 'otherwise')
    if c[outcome] == 'CANNOT_TELL' and c.get(reason): w = '%s (%s)' % (w, c[reason])
    return w
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def headline(S):
    """11 Nov 2026, referee 2: the line leads with the split by lead time. First the short-lead result, then the all-leads reading and what it rests on."""
    cells = S['cells']; allc = cells[0]; far = cells[3]; near = cells[1]
    DEP = S.get('dependence') or {}; DC = {c['cell']: c for c in DEP.get('cells', [])}
    out_n = allc['above'] + allc['below']; d7 = DC.get('0 to 7 days') or {}
    s = ('Close-approach distance ranges that JPL stated 0 to 7 days before the approach: the latest JPL orbit solution put %d of %d inside the stated 3-sigma range, with a 95%% interval of %s to %s percent, and the cell reads %s'
         % (near['inside'], near['scored'], pc(near['lo']), pc(near['hi']), rw(near)))
    s += ('. One row outside would make it %s.' % rw(d7, 'outcome_if_one_outside', 'reason_if_one_outside')) if near['outcome'] == 'CONSISTENT' and d7.get('outcome_if_one_outside') and d7['outcome_if_one_outside'] != 'CONSISTENT' else '.'
    s += (' Across all lead times %d of %d are inside, with the latest solution %d farther than the stated range and %d closer.' % (allc['inside'], allc['scored'], allc['above'], allc['below']))
    if out_n and far['above'] + far['below'] == out_n: s += ' All %d were stated more than 30 days ahead.' % out_n
    s += (' Read against about 99.7 percent, which is our reading, the all-leads share is %s percent with a 95%% interval of %s to %s percent and reads %s.' % (pc(allc['share']), pc(allc['lo']), pc(allc['hi']), rw(allc)))
    dc, df = DC.get('all leads'), DC.get('more than 30 days')
    if dc and df and dc['from_copy_outside']:
        s += (' That reading rests mostly on one archived copy made on %s, which holds %d of the %d statements made more than 30 days ahead and %d of the %d rows outside. Without that copy %d of %d are inside and the cell reads %s.'
              % (time.strftime('%d %B %Y', time.strptime(DEP['copy_day'], '%Y%m%d')).lstrip('0'), df['from_copy_scored'], far['scored'], dc['from_copy_outside'], out_n, dc['without']['inside'], dc['without']['scored'], rw(dc['without'])))
    if near.get('req13') and allc.get('req13'): s += ' Rows behind the 0 to 7 day cell: %s Rows behind the all-leads cell: %s' % (near['req13']['line'], allc['req13']['line'])
    return '%d of %d' % (near['inside'], near['scored']), s
