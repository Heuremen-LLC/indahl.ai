"""flu_headline.py: the FLU headline (big number and line) from the summary as served at /flu/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def f(n): return '{:,}'.format(int(n))
def cell(S, name, level, side='final'):
    return next(c for c in S['cells'] if c['cell'] == name and c['level'] == level and c['side'] == side)
def headline(S):
    a = cell(S, 'all horizons', '95'); b = cell(S, 'all horizons', '50'); w = next(c for c in S['wis'] if c['cell'] == 'all horizons' and c['side'] == 'final')
    af = cell(S, 'all horizons', '95', 'first'); sens = {(x['block_weeks'], x['level']): x for x in (S.get('after_data') or {}).get('block_sensitivity', [])}
    b13 = sens.get((13, '95'))
    s = ('The latest reported weekly count of flu hospital admissions fell inside the 95 percent interval the CDC FluSight ensemble stated for it in %s percent of forecasts, each one location, one week and one horizon from 0 to 3 weeks ahead, '
         'with a block bootstrap 95%% interval of %s to %s percent, so the reading is %s.%s The count was above the stated interval %s percent of the time and below it %s percent. '
         'The stated 50 percent interval held it %s percent of the time and reads %s. ' % (pc(a['share']), pc(a['lo']), pc(a['hi']), WORD[a['outcome']],
            (' That rests on the plan\'s blocks of 4 weeks. With blocks of 13 weeks, tried after the data, the interval runs from %s to %s percent and would read %s.' % (pc(b13['lo']), pc(b13['hi']), WORD[b13['outcome']])) if b13 and b13['outcome'] != a['outcome'] else '',
            pc(a['share_above']), pc(a['share_below']), pc(b['share']), WORD[b['outcome']]))
    s += 'Against the first reported count the share is %s percent, %s to %s, and reads %s. ' % (pc(af['share']), pc(af['lo']), pc(af['hi']), WORD[af['outcome']])
    if w['ratio'] is not None:
        s += 'On the same rows the ensemble\'s weighted interval score was %.2f times the hub baseline model\'s (%.2f to %.2f).' % (w['ratio'], w['lo'], w['hi'])
    return '%s of %s' % (f(a['inside']), f(a['scored'])), s
