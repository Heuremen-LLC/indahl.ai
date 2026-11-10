"""tornado_headline.py: the TORNADO headline (big number and line) from the summary as served at /tornado/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. PLAN.md (Headline, fixed before the data): the United States closed-years
table, how many of the eight bands read each outcome, the 10 to 15 percent band with its interval, and the Kansas cell beside it. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def _cell(S, name, pre=False): return next(c for c in S['cells'] if c['cell'] == name and c['preliminary'] == pre)
def _band(c, name): return next(b for b in c['bands'] if b['band'] == name)
def headline(S):
    us = _cell(S, 'United States'); ks = _cell(S, 'Kansas'); b = _band(us, '10 to 15'); kb = _band(ks, '10 to 15'); bo = us['band_outcomes']
    y0, y1 = S['frame']['closed_years']
    s = ('Where the Storm Prediction Center drew a 10 to 15 percent chance of a tornado within 25 miles in its 1300 UTC Day 1 outlook from %d to %d, '
         'a tornado came within 25 miles of a point %s percent of the time, with a 95%% interval of %s to %s percent, and the band reads %s.'
         % (y0, y1, pc(b['freq']), pc(b['lo']), pc(b['hi']), WORD[b['outcome']]))
    # 10 Nov 2026, referee R10: bands with fewer than the plan's 30 days read cannot tell by rule and are named apart as too thin
    thin = sum(1 for x in us['bands'] if x['days'] < S['frame']['min_days'] and x['outcome'] == 'CANNOT_TELL'); bo = dict(bo, CANNOT_TELL=bo.get('CANNOT_TELL', 0) - thin)
    parts = [('%d %s' % (bo[k], WORD[k])) for k in ('CONSISTENT', 'ABOVE', 'BELOW', 'CANNOT_TELL') if bo.get(k)]
    if thin: parts.append('%d with fewer than %d days, too thin to read' % (thin, S['frame']['min_days']))
    s += ' Of the eight stated bands, %s.' % (', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0])
    s += (' In Kansas the same band held %s percent, from %s to %s percent, over %d days, and reads %s.' % (pc(kb['freq']), pc(kb['lo']), pc(kb['hi']), kb['days'], WORD[kb['outcome']])
          if kb['freq'] is not None else ' Kansas had no point-day in that band.')
    return '%s%%' % pc(b['freq']), s
