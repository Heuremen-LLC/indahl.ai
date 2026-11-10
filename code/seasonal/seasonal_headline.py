"""seasonal_headline.py: the SEASONAL headline (big number and line) from the summary as served at /seasonal/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def f(n): return '{:,}'.format(int(n))
def cell(S, name): return next(c for c in S['cells'] if c['cell'] == name)
def headline(S):
    t = cell(S, 'temperature, leaning'); p = cell(S, 'precipitation, leaning')
    h = {(x['variable'], x['score']): x for x in S['heidke']}; ht = h[('temp', 'non-EC score')]; hp = h[('prec', 'non-EC score')]
    ob = (S.get('after_data') or {}).get('observed_shares', {}).get('temp')
    s = ('When the Climate Prediction Center stated a chance of 40 percent or more for a temperature category in its 3-month outlook, the stated chance averaged %s percent and that category was observed in %s percent of grid cells, '
         'with a block bootstrap 95%% interval of %s to %s percent, so the reading is %s: it happened more often than stated. For precipitation the stated chance averaged %s percent and the category was observed %s percent of the time (%s to %s), %s. '
         % (pc(t['mean_stated']), pc(t['observed']), pc(t['lo']), pc(t['hi']), WORD[t['outcome']], pc(p['mean_stated']), pc(p['observed']), pc(p['lo']), pc(p['hi']), WORD[p['outcome']]))
    if t['outcome'] != 'ABOVE': s = s.replace(': it happened more often than stated', '')
    if ob: s += ('The thirds are set by CPC\'s 1981 to 2010 reference period, and over all cells and seasons temperature came in above normal %s percent of the time and below normal %s percent. ' % (pc(ob['above']), pc(ob['below'])))
    s += ('Our recompute of CPC\'s Heidke skill score from its own archive matches the score CPC states within 1 point in %d of %d temperature seasons and %d of %d precipitation seasons with a favoured cell.'
          % (ht['within_1_point'], ht['seasons'], hp['within_1_point'], hp['seasons']))
    return '%s%%' % pc(t['observed']), s
