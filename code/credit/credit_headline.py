"""credit_headline.py: the CREDIT headline (big number and line) from the summary as served at /credit/live.json. Used by build_page.py and by
watch/headlines.py, so the page and the live headline say the same thing. PLAN.md (Headline, fixed before the data): ruler one for 2025, the database
timely share with its interval against the printed 99.6 percent and its outcome, then the three bureaus' 2025 not timely shares, and the count of
companies reading each outcome under ruler two in 2025. Standard library only."""
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
SHORT = {'EQUIFAX, INC.': 'Equifax', 'Experian Information Solutions Inc.': 'Experian', 'TRANSUNION INTERMEDIATE HOLDINGS, INC.': 'TransUnion'}
def rw(c, o='outcome', r='reason', edge=False):
    """The reading word with its Faults and Guards 2.0 reason beside it when the outcome is CANNOT_TELL, and the at-the-edge mark (feeds from before 12 Nov 2026 carry no reason)."""
    w = WORD.get(c.get(o), '')
    parts = ([c[r]] if c.get(o) == 'CANNOT_TELL' and c.get(r) else []) + (['at the edge'] if edge else [])
    return w + (' (%s)' % ', '.join(parts) if parts else '')
def pc(x, d=2): return '' if x is None else ('%.' + str(d) + 'f') % (100 * x)
def num(x): return '{:,}'.format(int(x))
def headline(S):
    r = next(x for x in S['ruler1'] if x['year'] == 2025)
    s = ('In 2025 the CFPB printed that companies gave a timely response to %s of complaints sent to them. In the public complaint database, %s of %s complaints received that year are flagged timely, '
         '%s percent with a 95%% interval of %s to %s percent, and the reading is %s.' % (r['printed'], num(r['rows'] - r['not_timely']), num(r['rows']), pc(r['timely']), pc(r['lo']), pc(r['hi']), rw(r)))
    bs = [c for c in S['companies'] if c['year'] == 2025 and c['bureau']]
    bs.sort(key=lambda c: list(SHORT).index(c['company']))
    s += ' The three nationwide credit bureaus: ' + ', '.join('%s %s not timely of %s' % (SHORT[c['company']], num(c['not_timely']), num(c['rows'])) for c in bs[:-1]) + ' and %s %s of %s.' % (SHORT[bs[-1]['company']], num(bs[-1]['not_timely']), num(bs[-1]['rows']))
    t = S['tally_companies'].get('2025') or S['tally_companies'].get(2025)
    n = sum(v for k, v in t.items() if k != 'too_few')
    s += (' Of the %d companies with at least 1,000 complaints across at least 10 months of 2025, %d had a not timely share below the share the printed figure leaves, %d above it and %d cannot tell.'
          % (n, t.get('BELOW', 0), t.get('ABOVE', 0), t.get('CANNOT_TELL', 0) + t.get('CONSISTENT', 0)))
    if r.get('req13'): s += ' Readings behind the 2025 headline, the pooled reading and each company read: %s' % r['req13']['line']
    return '%s%%' % pc(r['timely']), s
