"""quake_headline.py: the QUAKE headline (big number and line) from the summary as served at /quake/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def headline(S):
    c = S['headline_cell']; f = '{:,}'.format
    s = ('USGS aftershock forecasts give a range for the number of M3 and larger aftershocks in the forecast zone and call it the 95%% confidence range. '
         'In the windows that have closed, the count in the USGS catalog fell inside the stated range in %s of %s, above it in %s and below it in %s. '
         'That is %s percent, with a 95%% interval of %s to %s percent that resamples whole groups of sequences, and against the stated 95 percent it reads %s. '
         % (f(c['inside']), f(c['scored']), f(c['above']), f(c['below']), pc(c['share']), pc(c['lo']), pc(c['hi']), WORD[c['outcome']]))
    W = S.get('cover_by_window') or []
    if W: s += 'By window: ' + ', '.join('%s %s percent (%s)' % (w['cell'].split(', ')[-1].replace('1 ', 'one '), pc(w['share']), WORD[w['outcome']]) for w in W) + '. '
    D = S.get('described') or {}; A = D.get('stated_10_percent_or_more_all'); SP = D.get('stated_10_percent_or_more') or []
    if A and A.get('scored'):
        s += ('Where the stated chance of at least one was 10 percent or more, at least one happened in %s of %s windows, %s percent against a mean stated chance of %s percent, which reads %s. '
              % (f(A['occurred']), f(A['scored']), pc(A['share']), pc(A['stated_mean']), WORD[A['outcome']]))
        def lab(x): return x['cell'].replace('every magnitude, ', '').replace('1 ', 'one-') .replace('one-day', 'one-day windows').replace('one-week', 'one-week windows').replace('one-month', 'one-month windows').replace('one-year', 'one-year windows')
        groups = {}
        for x in SP: groups.setdefault(WORD[x['outcome']], []).append('M4 and above' if x['cell'].startswith('M4') else lab(x))
        parts = ['%s for %s' % (w, ' and '.join(v) if len(v) < 3 else ', '.join(v[:-1]) + ' and ' + v[-1]) for w, v in groups.items()]
        s += 'Split, it reads ' + ', and '.join(parts) + '.'
    return '%s of %s' % (f(c['inside']), f(c['scored'])), s
