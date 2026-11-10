"""neo_headline.py: the NEO headline (big number and line) from the summary as served at /neo/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. 10 Nov 2026, referee R4: the split by lead and the dependence on one
archived copy are in the line itself. Standard library only."""
import time
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def headline(S):
    cells = S['cells']; allc = cells[0]; far = cells[3]; near = cells[1]
    DEP = S.get('dependence') or {}; DC = {c['cell']: c for c in DEP.get('cells', [])}
    out_n = allc['above'] + allc['below']
    s = ('Close-approach distances from the latest JPL orbit solution fell inside the 3-sigma range JPL had stated from an earlier solution. '
         'The latest solution puts %d farther than the stated range and %d closer.' % (allc['above'], allc['below']))
    if out_n and far['above'] + far['below'] == out_n: s += ' All %d were stated more than 30 days ahead.' % out_n
    dc, df = DC.get('all leads'), DC.get('more than 30 days')
    if dc and df and dc['from_copy_outside']:
        s += (' %d of them come from one archived copy made on %s, which holds %d of the %d statements made more than 30 days ahead. Without that copy %d of %d are inside.'
              % (dc['from_copy_outside'], time.strftime('%d %B %Y', time.strptime(DEP['copy_day'], '%Y%m%d')).lstrip('0'), df['from_copy_scored'], far['scored'], dc['without']['inside'], dc['without']['scored']))
    s += (' Read against about 99.7 percent, which is our reading, the share is %s percent with a 95%% interval of %s to %s percent and reads %s.' % (pc(allc['share']), pc(allc['lo']), pc(allc['hi']), WORD[allc['outcome']]))
    d7 = DC.get('0 to 7 days') or {}
    s += ' Stated 0 to 7 days ahead, %d of %d were inside and the cell reads %s' % (near['inside'], near['scored'], WORD[near['outcome']])
    s += (', and one row outside would make it %s.' % WORD[d7['outcome_if_one_outside']]) if near['outcome'] == 'CONSISTENT' and d7.get('outcome_if_one_outside') and d7['outcome_if_one_outside'] != 'CONSISTENT' else '.'
    return '%d of %d' % (allc['inside'], allc['scored']), s
