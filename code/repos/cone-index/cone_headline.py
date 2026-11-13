"""cone_headline.py: the CONE headline (big number and line) from the summary as served at /cone/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. The headline cell is fixed in PLAN.md: the Atlantic whole-path cell.
Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def seasons_phrase(S):
    fl = S['frame']['final_last']; last = min(fl.values()) if fl else None
    miss = [y for y in S['sources'].get('radii_missing', []) if last and y <= last]
    s = '%d to %d' % (S['frame']['seasons_first'], last)
    if miss: s += ' (%s left out, no cone radii were found for %s)' % (', '.join(map(str, miss)), 'it' if len(miss) == 1 else 'them')
    return s
def headline(S):
    cells = S['cells']; al = cells[0]; ep = cells[1]; circ = [c for c in cells if c['kind'] == 'circle']
    tally = {}
    for c in circ: tally[c['outcome']] = tally.get(c['outcome'], 0) + 1
    vt = {}
    for b in S.get('verification_tally', {}).values():
        for k, v in b.items(): vt[k] = vt.get(k, 0) + v
    compared = vt.get('CONSISTENT', 0) + vt.get('ABOVE', 0) + vt.get('BELOW', 0)
    s = ('Atlantic forecasts from the National Hurricane Center, seasons %s, with all five days of track: the storm center stayed inside the forecast cone for the whole path in %s percent '
         '(95%% interval %s to %s percent, resampled by storm). NHC states about 60 to 70 percent, and the cell reads %s.' % (seasons_phrase(S), pc(al['share']), pc(al['lo']), pc(al['hi']), WORD[al['outcome']]))
    s += (' This share covers the {:,} forecasts whose storm stayed a tropical or subtropical cyclone for all five days. A further {:,} did not and are not in the share. NHC does not say which forecasts its 60 to 70 percent covers.'.format(al['scored'], al['nothing_returned']))
    s += ' In the East Pacific it was {:,} of {:,}, %s percent (%s to %s), which reads %s.'.format(ep['inside'], ep['scored']) % ( pc(ep['share']), pc(ep['lo']), pc(ep['hi']), WORD[ep['outcome']])
    if circ:
        lo_s, hi_s = min(c['share'] for c in circ), max(c['share'] for c in circ)
        above = lo_s > 2 / 3
        s += ' Read one lead time at a time against two-thirds (61.7 to 71.7 percent is our reading), %s, from %s to %s percent' % ('every share is above two-thirds' if above else 'the shares run', pc(lo_s), pc(hi_s))
        cons = [c for c in circ if c['outcome'] == 'CONSISTENT']; ct = [c for c in circ if c['outcome'] == 'CANNOT_TELL']
        if len(cons) == 1 and len(ct) == len(circ) - 1: s += ', and all but the %s %d h cell read cannot tell.' % (cons[0]['cell'].split(',')[0], cons[0]['lead'])
        elif len(ct) == len(circ): s += ', and every one reads cannot tell.'
        else: s += '.'
    if compared:
        s += (' NHC\'s own yearly averages of forecast distance agree with our recount from the same files wherever the case counts are within 5 percent.' if vt.get('CONSISTENT', 0) == compared
              else ' NHC\'s own yearly averages of forecast distance differ from our recount in some seasons where the case counts are within 5 percent.')
    return '{:,} of {:,}'.format(al['inside'], al['scored']), s
