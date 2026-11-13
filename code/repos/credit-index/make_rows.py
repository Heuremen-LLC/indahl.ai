#!/usr/bin/env python3
"""make_rows.py: writes the credit.* ledger rows as status 'staged' from summary_credit.json, with snippets read from the draft page credit.html
(table rows as the page prints them). Rerunnable while the rows are staged: a staged row is rewritten with a history line. A live row is never touched.
  make_rows.py stage     write or refresh the staged rows
  make_rows.py live      flip every staged credit.* row to live (run inside the ship command only)"""
import os, sys, json, re, html
B = os.path.expanduser('~/bones-forge'); sys.path.insert(0, B + '/ledger')
import ledger as LG
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, 'summary_credit.json')))
CK = 'credit_index/CHECKS.md'
def norm(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
PAGE = open(os.path.join(H, 'credit.html')).read()
TROWS = [norm(r) for r in re.findall(r'(?s)<tr>(.*?)</tr>', PAGE)]
def trow(*starts):
    hits = [r for r in TROWS if all(x in r for x in starts) and r.startswith(starts[0])]
    assert len(hits) >= 1, starts
    return hits[0]
def pc(x, d=2): return ('%.' + str(d) + 'f') % (100 * x)
def num(x): return '{:,}'.format(int(x))
CHECKS_TXT = open(os.path.join(B, CK)).read()
def grep_line(prefix):
    m = [l for l in CHECKS_TXT.splitlines() if prefix in l]; assert m, prefix; return prefix
rows = []
for r in S['ruler1']:
    y = r['year']
    rows.append(dict(id='credit.timely.%d' % y, claim='CREDIT, CFPB complaint database %d: share of complaints flagged timely, company-month block bootstrap 95 percent interval, against the CFPB printed %s (band %s to %s percent)' % (y, r['printed'], pc(r['band'][0]), pc(r['band'][1])),
                     value='%.6f' % r['timely'], lo='%.6f' % r['lo'], hi='%.6f' % r['hi'], unit='%s of %s complaints timely' % (num(r['rows'] - r['not_timely']), num(r['rows'])), outcome=r['outcome'],
                     grep='timely %d: %s of %s' % (y, num(r['rows'] - r['not_timely']), num(r['rows'])), snip=trow('%d %s' % (y, r['printed']))))
SHORT = {'EQUIFAX, INC.': 'equifax', 'Experian Information Solutions Inc.': 'experian', 'TRANSUNION INTERMEDIATE HOLDINGS, INC.': 'transunion'}
for c in S['companies']:
    if c['year'] == 2025 and c['bureau']:
        rows.append(dict(id='credit.bureau.%s.2025' % SHORT[c['company']], claim='CREDIT, %s 2025: share of complaints flagged not timely, against the 0.35 to 0.45 percent the CFPB printed 99.6 percent leaves (an all-company average, not a per-company limit)' % c['company'],
                         value='%.6f' % c['share'], lo='%.6f' % c['lo'], hi='%.6f' % c['hi'], unit='%s not timely of %s complaints' % (num(c['not_timely']), num(c['rows'])), outcome=c['outcome'],
                         grep='%s 2025: %s not timely of %s' % (c['company'], num(c['not_timely']), num(c['rows'])), snip=trow(html.escape(c['company']).replace('&amp;', '&'), num(c['rows']))))
t = S['tally_companies']['2025']; n = sum(v for k, v in t.items() if k != 'too_few')
rows.append(dict(id='credit.companies.2025', claim='CREDIT, companies with at least 1,000 complaints across at least 10 months of 2025, read against the share the CFPB printed figure leaves: below, consistent, above, cannot tell',
                 value=str(n), lo=None, hi=None, unit='%d below, %d consistent, %d above, %d cannot tell' % (t.get('BELOW', 0), t.get('CONSISTENT', 0), t.get('ABOVE', 0), t.get('CANNOT_TELL', 0)), outcome='COUNT',
                 grep='companies 2025: %d read' % n, snip=trow('2025 %d' % n)))
d = next(x for x in S['q1d'] if x['year'] == 2025)
rows.append(dict(id='credit.sent.2025', claim='CREDIT, CFPB complaint database 2025: share of complaints sent to the company 0 or 1 day after receipt, against the CFPB printed 97% in a day or less (band 96.5 to 97.5 percent)',
                 value='%.6f' % d['share'], lo='%.6f' % d['lo'], hi='%.6f' % d['hi'], unit='%s of %s complaints' % (num(d['within_1_day']), num(d['rows'])), outcome=d['outcome'],
                 grep='sent 2025: %s of %s' % (num(d['within_1_day']), num(d['rows'])), snip=trow('2025 %s' % num(d['rows']))))
rows.append(dict(id='credit.fcra30', claim='CREDIT, 15 U.S.C. 1681i 30-day reinvestigation period: not measurable from the CFPB complaint database (no company response date, no bureau dispute receipt date)',
                 value='not measurable', lo=None, hi=None, unit='', outcome='CANNOT_TELL', grep='fcra30: cannot tell',
                 snip='Reading: cannot tell. The database records the date the CFPB received the complaint and the date it sent it to the company.'))
tc = next(x for x in S['tccp'] if x['period'] == '2025 H2')
rows.append(dict(id='credit.tccp.2025h2', claim='CREDIT, TCCP survey second half of 2025: median stated purchase APR across top 25 issuer plans, beside G.19 2025 Q4 all accounts and accounts assessed interest (not like for like)',
                 value='%.2f' % tc['top25_median'], lo=None, hi=None, unit='percent, G.19 %.2f and %.2f' % (tc['g19_all_accounts'], tc['g19_assessed_interest']), outcome='CANNOT_TELL',
                 grep='tccp 2025 H2: top 25 median %.2f' % tc['top25_median'], snip=trow('2025 H2 %s' % num(tc['plans']))))
tf = S['tally_company_family_2025']
rows.append(dict(id='credit.compfam.2025', claim='CREDIT, company and product family pairs with at least 1,000 complaints across at least 10 months of 2025, read against the share the CFPB printed figure leaves',
                 value=str(sum(v for k, v in tf.items() if k != 'too_few')), lo=None, hi=None, unit='%d below, %d above, %d cannot tell' % (tf.get('BELOW', 0), tf.get('ABOVE', 0), tf.get('CANNOT_TELL', 0) + tf.get('CONSISTENT', 0)), outcome='COUNT',
                 grep='compfam 2025: %d read' % sum(v for k, v in tf.items() if k != 'too_few'),
                 snip='at least 10 months: %d below, %d above, %d cannot tell' % (tf.get('BELOW', 0), tf.get('ABOVE', 0), tf.get('CANNOT_TELL', 0) + tf.get('CONSISTENT', 0))))
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'print'
    if mode == 'grep':   # the lines CHECKS.md must carry for the sources
        for r in rows: print('  - ' + r['grep'])
        sys.exit(0)
    if mode == 'print':
        for r in rows: print(r['id'], r['value'], r['outcome'], '|', r['snip'][:120])
        sys.exit(0)
    L = LG.load(); ck = LG.checks_ref(CK)
    if mode == 'stage':
        pn = norm(PAGE)
        for r in rows:
            assert norm(r['snip']) in pn, ('snippet not on the draft page', r['id'])
            assert r['grep'] in CHECKS_TXT, ('CHECKS.md lacks', r['grep'])
            old = L.get(r['id'])
            if old and old['status'] != 'staged': print('left alone (not staged):', r['id']); continue
            hist = (old['history'] if old else []) + [dict(at=LG.now(), change='staged' if not old else 'restaged', evidence=CK)]
            L[r['id']] = dict(checks=ck, id=r['id'], claim=r['claim'], value=r['value'], lo=r['lo'], hi=r['hi'], unit=r['unit'], outcome=r['outcome'],
                              source=dict(file=CK, grep=r['grep']), surfaces=[dict(surface='desk_credit', text=r['snip'])], status='staged', history=hist)
        LG.save(L); print('staged', len(rows))
    elif mode == 'live':
        n = 0
        for k, r in L.items():
            if k.startswith('credit.') and r['status'] == 'staged':
                r['status'] = 'live'; r['history'].append(dict(at=LG.now(), change="status: 'staged' -> 'live'", why='CREDIT page in build_site.py, shipped in this ship step', evidence=CK)); n += 1
        LG.save(L); print('live', n)
