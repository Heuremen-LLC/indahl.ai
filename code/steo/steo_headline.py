"""steo_headline.py: the STEO headline (big number and line) from the summary as served at /steo/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def f(n): return '{:,}'.format(int(n))
def cell(cells, s, name): return next(c for c in cells if c['series'] == s and c['cell'] == name)
def headline(S):
    w = cell(S['cells'], 'WTI', 'all leads'); h = cell(S['cells'], 'HH', 'all leads')
    w2 = cell(S['cells_addendum1'], 'WTI', 'all leads'); h2 = cell(S['cells_addendum1'], 'HH', 'all leads')
    s = ('The monthly average WTI crude oil spot price landed inside the 95 percent interval EIA stated for that month in an earlier Short-Term Energy Outlook in %s percent of stated months, '
         'with a block bootstrap 95%% interval of %s to %s percent, and reads %s. %s '
         'For Henry Hub natural gas the share is %s percent, %s to %s, and reads %s. '
         % (pc(w['share']), pc(w['lo']), pc(w['hi']), WORD[w['outcome']], ('It was never above the interval and was below it %s percent of the time.' % pc(w['share_below'])) if not w['above'] else ('It was above the interval %s percent of the time and below it %s percent.' % (pc(w['share_above']), pc(w['share_below']))), pc(h['share']), pc(h['lo']), pc(h['hi']), WORD[h['outcome']]))
    s += ('These are the issues whose workbook states the 95 percent level. Adding the later issues whose workbook leaves the level out and whose report labels it 95 percent, a reading we added after the data, '
          'WTI is %s percent (%s to %s, %s) and Henry Hub %s percent (%s to %s, %s).'
          % (pc(w2['share']), pc(w2['lo']), pc(w2['hi']), WORD[w2['outcome']], pc(h2['share']), pc(h2['lo']), pc(h2['hi']), WORD[h2['outcome']]))
    return '%s of %s' % (f(w['inside']), f(w['scored'])), s
