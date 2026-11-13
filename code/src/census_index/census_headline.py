"""census_headline.py: the CENSUS headline (big number and line) from the summary as served at /census/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. Standard library only."""
SER = {'SALES': 'new home sales', 'STARTS': 'housing starts', 'COMPLETIONS': 'housing completions', 'RETAIL': 'advance retail and food services sales'}
READ = {'ABOVE': 'a share above 90 percent', 'BELOW': 'a share below 90 percent', 'CONSISTENT': 'a share consistent with 90 percent', 'CANNOT_TELL': 'a share that cannot be read against 90 percent'}
MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
NUM = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}
def reading(c): return READ[c['outcome']] + (' (%s)' % c['reason'] if c['outcome'] == 'CANNOT_TELL' and c.get('reason') else '')   # 12 Nov 2026: Faults and Guards 2.0, the reason sits beside the word
def cell(S, s, st, geo='US'): return next((c for c in S['cells'] if c['series'] == s and c['geo'] == geo and c['step'] == st), None)
def mname(m): return '%s %s' % (MON[int(m[5:7]) - 1], m[:4])
def join(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
def p90_range(S, series):
    v = [cell(S, s, st)['p90_abs_miss_half_widths'] for s in series for st in ('S1', 'S2') if cell(S, s, st) and cell(S, s, st)['p90_abs_miss_half_widths'] is not None]
    return min(v), max(v)
def headline(S):
    h = p90_range(S, ('SALES', 'STARTS', 'COMPLETIONS')); r = p90_range(S, ('RETAIL',))
    s1 = [cell(S, k, 'S1') for k in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL')]
    outs = {c['outcome'] for c in s1}
    parts = ['%s in %d of %d months' % (SER[c['series']], c['inside'], c['scored']) for c in s1]
    tail = ('each %s' % reading(s1[0])) if len({reading(c) for c in s1}) == 1 else '; '.join('%s %s' % (SER[c['series']], reading(c)) for c in s1).replace(';', ',')
    srm = (S.get('same_release_months') or {}).get('HSN1F') or []
    t = ('Census states a 90 percent sampling interval with each first print. Later revisions are small next to it. For the second and third print, the 90th percentile of the miss, in stated half-widths, is %.2f to %.2f for the national housing series and %.2f to %.2f for advance retail. '
         'For the second print, the later value sat inside the interval for %s, %s. '
         % (h[0], h[1], r[0], r[1], join(parts), tail))
    if srm: t += 'In %s months (%s) the second print came in the same release as the first, so those rows show no revision. ' % (NUM.get(len(srm), str(len(srm))), join([mname(m) for m in srm]))
    t += 'A share is read against the figure 90 percent with no tolerance, so a cell reads above, below or cannot tell. ' 
    r13 = S.get('headline_req13')
    if r13: t += 'For the rows of the four second print cells, %s ' % r13['line']
    t += 'The interval states sampling error of the level, so a later value inside it is not a test of the stated width. The tables on the desk page hold every step.'
    c0 = s1[0]
    return '%d of %d' % (c0['inside'], c0['scored']), t
