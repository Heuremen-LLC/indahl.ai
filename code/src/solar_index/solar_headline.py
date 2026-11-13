"""solar_headline.py: the SOLAR headline (big number and line) from the summary as served at /solar/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. The headline cell is fixed in PLAN.md: M-class flares, day one.
Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
SKILL = {'ABOVE': 'reads above, better than the base rate by more than 0.05', 'BELOW': 'reads below, worse than the base rate by more than 0.05', 'CONSISTENT': 'reads consistent with the base rate', 'CANNOT_TELL': 'reads cannot tell'}
def W(c): return WORD[c['outcome']] + (' (%s)' % c['reason'] if c.get('reason') else '')   # 12 Nov 2026: the CANNOT_TELL reason beside the word (Faults and Guards 2.0)
def pc(x, d=1): return '' if x is None else (('%.' + str(d) + 'f') % (100 * x))
def cell(S, ev, lead): return next(c for c in S['cells'] if c['event'] == ev and c['lead'] == lead)
def counted(c, minn): return [b for b in c['bins'] if b['n'] >= minn]
def headline(S):
    minn = S['frame']['min_n']; c = cell(S, 'M', 1); bs = counted(c, minn); k = c['skill']; h = S.get('headline') or {}
    cons = [b for b in bs if b['outcome'] in ('CANNOT_TELL', 'CONSISTENT')]; off = [b for b in bs if b['outcome'] in ('ABOVE', 'BELOW')]
    s = ('For M-class flares on the day after each forecast, the interval of the share of days with a flare held the chance NOAA SWPC stated in %d of %d bins of stated chance, so those bins read cannot tell (STRADDLES_EDGE). No bin reads consistent. A stated chance is a point figure with no tolerance.' % (len(cons), len(bs)))
    for side, word in (('ABOVE', 'more often'), ('BELOW', 'less often')):
        xs = [b for b in off if b['outcome'] == side]
        if xs:
            parts = ['%s percent of days where it stated %s percent' % (pc(b['observed']), pc(b['mean_stated'], 0)) for b in xs]
            s += ' In the other %d bins a flare came %s than stated: %s.' % (len(xs), word, (', '.join(parts[:-1]) + ' and ' + parts[-1]) if len(parts) > 1 else parts[0])
    bh = h.get('boot_holds_stated', h.get('boot_consistent'))
    if bh is not None:
        s += ' On a block bootstrap interval, which allows for runs of active days, the interval holds the stated chance in %d of %d.' % (bh, len(bs))
    s += (' The Brier skill against the base rate of the same days is %.2f, with a 95 percent block bootstrap interval of %.2f to %.2f, and %s%s.' % (k['bss'], k['lo'], k['hi'], SKILL[k['outcome']], (' (%s)' % k['reason']) if k.get('reason') else ''))
    a = h.get('all_bins') or {}
    if a:
        s += (' Across every scored event and day ahead, %d bins read cannot tell (STRADDLES_EDGE), %d above and %d below. M-class flares came more often than stated, and X-class flares and storms mostly came less often.'
              % (a.get('CANNOT_TELL', a.get('CONSISTENT', 0)), a.get('ABOVE', 0), a.get('BELOW', 0)))
    s += ' Middle latitude storms are scored against Fredericksburg K, our reading of a station the report does not name. Against planetary Kp the same chances sit close to what happened.'
    r13 = h.get('req13') or {}
    if r13.get('line'): s += ' Beside the headline bins: ' + r13['line']
    return '%d of %d' % (len(cons), len(bs)), s
