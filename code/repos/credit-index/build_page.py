#!/usr/bin/env python3
"""build_page.py: writes credit.html, the desk's page draft, from summary_credit.json. Reads no network. The live page is built by the site build, which
takes the body from this file. Aggregate company-level figures only."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from credit_headline import headline, SHORT
S = json.load(open('summary_credit.json'))
e = html.escape
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', None: ''}
def pc(x, d=2):
    if x is None: return ''
    return ('%.' + str(d) + 'f') % (100 * x)
def iv(lo, hi, d=2): return '' if lo is None else '%s to %s' % (pc(lo, d), pc(hi, d))
def num(x): return '{:,}'.format(int(x))
def table(head, rows, cls='bench'):
    return ('<div class="tw"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, ''.join('<th>%s</th>' % h for h in head),
            ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)))
G = S['gates']; SRC = S['source']; F = S['frame']
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
gate_line = 'All known-good checks passed on this run.' if G['passed'] else 'A known-good check did not pass on this run, so every reading shows cannot tell.'
api = '. '.join('%s: %s in our count, %s from the CFPB search service' % (e(x['cell']), num(x['ours']), '' if x['api'] is None else num(x['api'])) for x in G['api_check'])

# ruler one
r1 = [[str(x['year']), e(x['printed']), e(x['printed_sent']), num(x['rows']), num(x['not_timely']), pc(x['timely']), iv(x['lo'], x['hi']),
       '%s to %s' % (pc(x['band'][0]), pc(x['band'][1])), WORD[x['outcome']] + (' (at the edge)' if x.get('at_edge_display') else ''), pc(x['database_share_of_printed_count'], 1), pc(x['printed_base_if_unpublished_timely_display'])] for x in S['ruler1']]
T1 = table(['Year', 'CFPB printed timely share', 'Complaints the CFPB says it sent', 'Complaints in the database', 'Not timely in the database', 'Timely, percent', '95% interval, percent', 'Band the printed figure allows, percent', 'Reading', 'Database count as a share of the printed count, percent', 'Timely share on the printed count if every unpublished complaint was timely, percent (shown only)'], r1)
r25 = next(x for x in S['ruler1'] if x['year'] == 2025)

# ruler two, 2025 companies
c25 = sorted([c for c in S['companies'] if c['year'] == 2025], key=lambda c: -c['rows'])
rows2 = [[e(c['company']), num(c['rows']), num(c['not_timely']), str(c['months']), pc(c['share'], 3), iv(c['lo'], c['hi'], 3), WORD[c['outcome']] + (' (at the edge)' if c.get('at_edge_display') else ''), iv(c['wilson'][0], c['wilson'][1], 3)] for c in c25]
T2 = table(['Company, as the database names it', 'Complaints', 'Not timely', 'Months', 'Not timely, percent', '95% interval, percent', 'Reading against 0.35 to 0.45', 'Wilson interval, percent (shown only)'], rows2)
tl = S['tally_companies']
rowsT = [[y, str(sum(v for k, v in tl[y].items() if k != 'too_few')), str(tl[y].get('BELOW', 0)), str(tl[y].get('CONSISTENT', 0)), str(tl[y].get('ABOVE', 0)), str(tl[y].get('CANNOT_TELL', 0)), num(tl[y].get('too_few', 0))] for y in sorted(tl)]
BANDS = {x['year']: x['band'] for x in S['ruler1']}
TT = table(['Year', 'Companies read', 'Below', 'Consistent', 'Above', 'Cannot tell', 'Companies with fewer than 1,000 complaints or 10 months'], rowsT)
WD = S.get('wilson_display_2025') or {}
w_turn = WD.get('BELOW|CANNOT_TELL', 0); w_up = WD.get('CANNOT_TELL|ABOVE', 0)
bw = [[e(c['company']), num(c['rows']), num(c['not_timely']), pc(c['share'], 4), iv(c['lo'], c['hi'], 4), iv(c['band'][0], c['band'][1], 3), WORD[c['outcome_display']]] for c in S['bureau_window']]
on = [[str(x['year']), num(x['rows']), num(x['not_timely']), pc(x['share'], 2), iv(x['lo'], x['hi'])] for x in S['others_nt']]
cf = sorted(S['comp_fam'], key=lambda c: (c['family'], -c['rows']))
TCF = table(['Company', 'Product family', 'Complaints', 'Not timely', 'Not timely, percent', '95% interval, percent', 'Reading against 0.35 to 0.45'],
            [[e(c['company']), e(c['family']), num(c['rows']), num(c['not_timely']), pc(c['share'], 3), iv(c['lo'], c['hi'], 3), WORD[c['outcome']] + (' (at the edge)' if c.get('at_edge_display') else '')] for c in cf])
tf = S['tally_company_family_2025']

# Q1b responses
def resp_table(yr):
    R = next(r for r in S['responses'] if str(r['year']) == str(yr))
    cats = [s['category'] for s in R['cells'][0]['shares']]
    keep = [c for c in cats if any(next(s for s in cell['shares'] if s['category'] == c)['rows'] for cell in R['cells'])]
    head = ['Group', 'Complaints'] + [e(c) + ', percent (95% interval)' for c in keep]
    rows = []
    for cell in R['cells']:
        sh = {s['category']: s for s in cell['shares']}
        rows.append([e(SHORT.get(cell['group'], cell['group'])), num(cell['rows'])] + ['%s (%s)' % (pc(sh[c]['share']), iv(sh[c]['lo'], sh[c]['hi'])) for c in keep])
    return table(head, rows)
T1b = {yr: resp_table(yr) for yr in (2021, 2022, 2023, 2024, 2025, 'window')}
TB = S['q1b_table1']['printed']
TB1 = table(['Year', 'Closed with monetary relief', 'Closed with non-monetary relief', 'Closed with explanation', 'Admin response', 'Company reviewing', 'No timely response', 'Reading'],
            [[y, e(TB[y]['monetary']), e(TB[y]['non_monetary']), e(TB[y]['explanation']), e(TB[y]['admin']), e(TB[y]['reviewing']), e(TB[y]['not_timely']), 'cannot tell'] for y in sorted(TB)])

# Q1c
Q = S['q1c']
lagrows = [[e(SHORT[x['company']]), str(x['year'])] + [num(x['buckets'][k]) for k in ('0 or 1', '2 to 7', '8 to 30', 'over 30')] for x in Q['lag']]
TL = table(['Bureau', 'Year', 'Sent in 0 or 1 day', '2 to 7 days', '8 to 30 days', 'Over 30 days'], lagrows)
TQ = table(['Bureau', 'Year', 'Credit reporting complaints', 'Not timely', 'Not timely, percent', '95% interval, percent'],
           [[e(SHORT[x['company']]), str(x['year']), num(x['rows']), num(x['not_timely']), pc(x['share'], 3), iv(x['lo'], x['hi'], 3)] for x in Q['bureau_credit_reporting_not_timely']])
# Q1d
TD = table(['Year', 'Complaints with both dates', 'Sent in 0 or 1 day', 'Share, percent', '95% interval, percent', 'Sent before received', 'Reading against 96.5 to 97.5'],
           [[str(x['year']), num(x['rows']), num(x['within_1_day']), pc(x['share'], 1), iv(x['lo'], x['hi'], 1), num(x['sent_before_received']), WORD[x['outcome']] if x['outcome'] else 'no printed figure'] for x in S['q1d']])
d25 = next(x for x in S['q1d'] if x['year'] == 2025)
# Q2
def f2(x): return '' if x is None else '%.2f' % x
TC = table(['Survey half year', 'Plans', 'Plans stating a minimum purchase APR', 'Plans with a median purchase APR', 'Median purchase APR, all plans', '10th to 90th percentile', 'Top 25 issuer plans', 'Median, top 25', '10th to 90th, top 25', 'Lowest to highest stated', 'G.19 quarter', 'G.19 all accounts', 'G.19 accounts assessed interest', 'Reading'],
           [[e(t['period']), num(t['plans']), num(t['plans_with_min']), num(t['plans_with_apr']), f2(t['median_of_medians']), '%s to %s' % (f2(t['p10']), f2(t['p90'])), '' if t['top25_plans'] is None else num(t['top25_plans']),
             f2(t['top25_median']), '' if t['top25_p10'] is None else '%s to %s' % (f2(t['top25_p10']), f2(t['top25_p90'])), '%s to %s' % (f2(t['lowest_min']), f2(t['highest_max'])),
             e(t['g19_quarter']), f2(t['g19_all_accounts']), f2(t['g19_assessed_interest']), WORD[t['outcome']]] for t in S['tccp'] if 'plans' in t])
TF = table(['Survey half year', 'Plans stating a late fee above $0', 'Median late fee above $0, dollars'], [[e(t['period']), num(t['late_fee_plans']), f2(t['late_fee_median'])] for t in S['tccp'] if 'plans' in t])
flag = [t for t in S['tccp'] if t.get('top25_plans')]
out_all = [t['period'] for t in flag if not t.get('display_all_accounts_inside_top25_p10_p90')]; out_ass = [t['period'] for t in flag if not t.get('display_assessed_inside_top25_p10_p90')]
def _lst(v): return v[0] if len(v) == 1 else ', '.join(v[:-1]) + ' and ' + v[-1]
inside_txt = ('The G.19 rate on accounts assessed interest falls inside the 10th to 90th percentile of the top 25 issuers\' plan medians in every half year with that flag%s. The all accounts rate falls %s (shown only).'
              % ('' if not out_ass else ' except ' + _lst(out_ass), 'inside it in every one' if not out_all else 'below the 10th percentile in ' + _lst(out_all) + ' and inside it in the other half years'))
na_cells = sum(t.get('not_applicable_code_cells', 0) for t in S['tccp'] if 'plans' in t)

body = hl + '''<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>
<h2>When the CFPB states how companies answer complaints, what does its own database show?</h2>
<p>The Consumer Financial Protection Bureau sends consumer complaints to the companies named in them and publishes the complaints in its Consumer Complaint Database. Its complaint page says: &ldquo;Companies generally respond in 15 days.&rdquo; and &ldquo;In some cases, the company will let you know their response is in progress and provide a final response in 60 days.&rdquo; Its annual reports define the database flag: &ldquo;Complaints in which a company did not provide a response within 15 calendar days of the complaint being sent to the company&mdash;or within 60 days if it requested more time&mdash;are reflected in the Consumer Complaint Database as not having received a timely response.&rdquo;</p>
<p>Each annual report prints one share for all companies. The 2025 report says companies were &ldquo;providing a timely response to 99.6%% of the more than 5.9 million complaints sent to them for review in 2025.&rdquo; The 2024 report says 99.7%%, the 2023 report 99.6%%, and the 2022 and 2021 reports 99%%. The 2025 report also says: &ldquo;Of those complaints sent to companies, the Bureau sent 97%% to a company in a day or less.&rdquo;</p>
<p>This page sets those printed figures beside the database itself, complaints received from 1 January 2021 to 31 December 2025, the last five complete years. It reads the database file of %s (%s complaints in the window). It names companies as the database names them and uses company-level counts only. No complaint text, ZIP code, state or detail about any person is read into this page.</p>
<p>A printed figure such as 99.6 percent is read as the band its rounding allows, here 99.55 to 99.65 percent. The printed figure counts every complaint sent to companies that year. The database holds the complaints published by the download date, which is fewer (for 2025, %s in the database against more than 5.9 million sent). So the two bases differ, and the page prints both counts. The 2025 report says: &ldquo;Complaints closed with an Alerted CFPB response are not published in the Consumer Complaint Database.&rdquo; Alerted CFPB is one of its administrative responses. The 2023 and 2024 reports cite this database for their count of complaints not given a timely response. If every complaint sent and not published had a timely response, the timely share on the printed count would sit inside the printed band in each year, as the table shows. So a cannot tell here comes from the width of the interval.</p>
<p>Complaints cluster by company and month. One company's handling or one wave of filings moves many complaints at once. Every interval here is a 95 percent interval from a bootstrap that draws whole company-months, 2,000 draws. It does not cover a wave that moves many companies in the same month. Each cell draws with the plan's seed joined to a checksum of the cell's name, so a cell gives the same interval on every run. A reading whose interval ends within 0.01 points of a band edge is marked at the edge, and another seed can move it. %s On the first run the rule check failed and every reading showed cannot tell. Its planted test drew one cell and asked that the interval hold the planted share, which one draw can miss by chance. The test now asks that 34 of 40 planted cells hold it, and the readings below come from the run after that change. The plan, with the rules, the cells and the bands, was committed before any printed figure was set beside the database.</p>
<h2>All companies, year by year</h2>
<p>The database's timely share for each year against the CFPB's printed share for that year.</p>
%s
<p class="bench-note">Reading: above if the whole 95%% interval is above the band, below if it is under the band, consistent if it lies inside, otherwise cannot tell. For 2025 the report also says &ldquo;more than 99%%&rdquo;. Against that the 2025 interval reads %s (shown only).</p>
<h2>Each company against the printed figure</h2>
<p>The printed share is an average over all companies. It is not a limit set for any one company, and the CFPB states no per-company figure. It is the only number the CFPB prints, so each company's share of complaints flagged not timely is set beside the share the printed figure leaves for that year (for 2025, 0.35 to 0.45 percent). Below means fewer complaints flagged not timely than that, above means more. A company is read in a year when it has at least 1,000 complaints across at least 10 months. The interval draws that company's months.</p>
%s
<p class="bench-note">A company with no complaint flagged not timely has a bootstrap interval of zero width. The Wilson interval, which does not draw months, is shown beside it and decides nothing. Under it %d of the below readings in 2025 would read cannot tell and %d cannot tell readings would read above. This column was added after the data. &ldquo;Servicer under contract with Federal Student Aid&rdquo; is the name the database gives, and every one of its rows records an untimely response.</p>
<h3>Companies read each year</h3>
%s
<h3>The three bureaus across all five years</h3>
<p>Shown only. Each bureau's not timely share over the window, against the band the printed figures leave, weighted by that bureau's complaints in each year.</p>
%s
<h3>All other companies pooled</h3>
%s
<h3>Company and product family, the latest year</h3>
<p>The same rule for each company and product family with at least 1,000 complaints in 2025 across at least 10 months: %d below, %d above, %d cannot tell, %s with fewer complaints or months. Product families group the database's product names, fixed in the plan.</p>
<details><summary>Every company and product family read</summary>
%s
</details>
<h2>How the three credit bureaus closed complaints</h2>
<p>The database records how each company says it responded. Equifax, Experian and TransUnion are the database's EQUIFAX, INC., Experian Information Solutions Inc. and TRANSUNION INTERMEDIATE HOLDINGS, INC. This part is descriptive. No stated figure exists for any one company, so there is no reading.</p>
<h3>The latest complete year</h3>
%s
<h3>The whole window</h3>
%s
<details><summary>Each year from 2021 to 2024</summary>
<p><b>2021</b></p>
%s
<p><b>2022</b></p>
%s
<p><b>2023</b></p>
%s
<p><b>2024</b></p>
%s
</details>
<p>The CFPB's annual report prints its own Table 1, &ldquo;How companies have responded to consumer complaints&rdquo;, with a row for credit or consumer reporting. It is shown here beside the database. Table 1 counts complaints closed with an admin response, which the database does not publish, so the two bases differ and the reading is cannot tell.</p>
%s
<h2>The thirty-day reinvestigation period</h2>
<p>The Fair Credit Reporting Act, 15 U.S.C. 1681i(a)(1)(A), says that when a consumer disputes an item and &ldquo;notifies the agency directly, or indirectly through a reseller, of such dispute, the agency shall, free of charge, conduct a reasonable reinvestigation&rdquo; and finish it &ldquo;before the end of the 30-day period beginning on the date on which the agency receives the notice of the dispute from the consumer or reseller.&rdquo; Subparagraph (B) allows &ldquo;not more than 15 additional days&rdquo; when the consumer sends relevant information during the period.</p>
<p>The same section, 1681i(e)(3), covers complaints the Bureau sends on to the nationwide bureaus. Each bureau shall &ldquo;review each such complaint to determine whether all legal obligations imposed on the consumer reporting agency under this subchapter ... have been met&rdquo;, &ldquo;provide reports on a regular basis to the Bureau&rdquo; and keep records. It sets no number of days.</p>
<p><b>Reading: cannot tell.</b> %s So the database cannot show whether any reinvestigation finished within 30 days. Two things it does hold are shown below and decide nothing: how many days the CFPB took to send each bureau its credit reporting complaints, and the share of those complaints the CFPB flagged not timely under its own 15 and 60 day rule.</p>
%s
%s
<h2>How fast the CFPB sent complaints on</h2>
<p>The database records the date the CFPB received each complaint and the date it sent it to the company. The share sent in 0 or 1 day, against the 2025 report's &ldquo;97%% to a company in a day or less&rdquo;, read as 96.5 to 97.5 percent. The report counts all complaints sent and the database the published ones.</p>
%s
<p class="bench-note">For 2025 the database shows %s percent sent in 0 or 1 day, with a 95%% interval of %s to %s percent, and the reading is %s. Earlier years have no printed figure and are shown only.</p>
<h2>Card plan APRs beside the Federal Reserve averages</h2>
<p>Every six months the CFPB's Terms of Credit Card Plans survey publishes the plans card issuers report, one row per plan, with the purchase APRs each plan states. The Federal Reserve's G.19 release prints two card rates for commercial banks each quarter. In its words, &ldquo;the rate for all accounts is the stated APR averaged across all credit card accounts at all reporting banks&rdquo; and &ldquo;the rate for accounts assessed interest is the annualized ratio of total finance charges at all reporting banks to the total average daily balances against which the finance charges were assessed&rdquo;.</p>
<p><b>Reading: cannot tell, not like for like.</b> The survey states APRs offered on plans, one row per plan with no weight for how many accounts it holds, and it includes credit unions and smaller issuers. G.19 averages APRs held on all accounts at reporting commercial banks, weighted by account or by balance. The two are set side by side and no reading is drawn. %s</p>
%s
<p class="bench-note">APRs in percent. A plan's purchase APR is the survey's median purchase APR for that plan (in the 2022 second-half file, the median APR column of the purchase section). The top 25 issuer flag is in the files from the second half of 2023. Plans with no purchase APR in the median column are counted and left out of the medians. Up to the first half of 2024 about four plans in ten carry a median, from the second half of 2024 about nineteen in twenty, so the medians do not run as one series across that change. The files write 9.99 or 9.98 in an APR cell for not applicable (999 percent). Those %s cells are counted apart and left out.</p>
<p>Fees the plans state have no delivered counterpart in a public aggregate read for this page, so they are shown with no reading.</p>
%s
<h2>Nothing returned</h2>
<p>Counted apart and never folded into a reading. Complaints with a timely value other than Yes or No: %s. Complaints with an unreadable date: %s. Complaints with no sent date: %s. Duplicate complaint numbers: %s. Complaints received outside the window: %s. TCCP files that could not be read: %s.</p>
<h2>What this page holds and what it leaves out</h2>
<p>Left out: complaint text, ZIP codes, states, tags, issues and company public responses, the Philadelphia Fed series built from the Y-14 filings, and the New York Fed household debt report. A reading says where the database sits against a printed figure. It does not say why, and it does not say whether any complaint was right.</p>
<p class="meta">By Wayfinder and Bones, Heuremen LLC.</p>
<p class="meta">Sources: CFPB Consumer Complaint Database, full file of %s (sha256 %s). CFPB Consumer Response Annual Reports for 2021 to 2025. CFPB complaint process and data use pages. 15 U.S.C. 1681i and 12 U.S.C. 5534 as printed by the Legal Information Institute. CFPB Terms of Credit Card Plans survey files, second half of 2022 to second half of 2025. Federal Reserve G.19 terms of credit history table. All read without a key, one request at a time. Generated %s. Heuremen LLC.</p>
<p class="meta">Known-good check against the CFPB search service: %s.</p>
<p class="meta">The headline is read again about once a week. The newest run is always in <a href="/credit/live.json">/credit/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/credit">credit</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://www.consumerfinance.gov/data-research/consumer-complaints/">CFPB Consumer Complaint Database</a> &middot; <a href="https://www.consumerfinance.gov/data-research/research-reports/2025-consumer-response-annual-report/">CFPB Consumer Response Annual Report</a> &middot; <a href="https://www.consumerfinance.gov/complaint/process/">CFPB complaint process</a> &middot; <a href="https://www.law.cornell.edu/uscode/text/15/1681i">15 U.S.C. 1681i</a> &middot; <a href="https://www.consumerfinance.gov/data-research/credit-card-data/terms-credit-card-plans-survey/">Terms of Credit Card Plans survey</a> &middot; <a href="https://www.federalreserve.gov/releases/g19/HIST/cc_hist_tc_levels.html">Federal Reserve G.19</a></p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=credit-all">Respond</a></p>
<section id="replies" data-prefix="credit"></section><script src="/replies.js" defer></script>''' % (
    e(SRC['file_time'][:10]), num(SRC['rows_in_window']), num(r25['rows']), gate_line,
    T1, WORD[r25.get('more_than_99', {}).get('outcome_display')],
    T2, w_turn, w_up, TT, table(['Bureau', 'Complaints', 'Not timely', 'Not timely, percent', '95% interval, percent', 'Weighted band, percent', 'Reading (shown only)'], bw),
    table(['Year', 'Complaints', 'Not timely', 'Not timely, percent', '95% interval, percent'], on),
    tf.get('BELOW', 0), tf.get('ABOVE', 0), tf.get('CANNOT_TELL', 0) + tf.get('CONSISTENT', 0), num(tf.get('too_few', 0)), TCF,
    T1b[2025], T1b['window'], T1b[2021], T1b[2022], T1b[2023], T1b[2024], TB1,
    e(Q['why']), TL, TQ, TD, pc(d25['share'], 1), pc(d25['lo'], 1), pc(d25['hi'], 1), WORD[d25['outcome']],
    inside_txt, TC, na_cells, TF,
    num(SRC['timely_other']), num(SRC['bad_date']), num(SRC['no_sent_date']), num(SRC['duplicate_rows']), num(SRC['outside_window']), num(sum(1 for t in S['tccp'] if 'nothing_returned' in t)),
    e(SRC['file_time'][:10]), e(SRC['sha256'][:16]), e(S['generated'][:10]), api)
TITLE = 'CREDIT | Stated Complaint Responses and Card Terms Against the Public Record | Heuremen LLC'
DESC = 'CREDIT: the CFPB printed timely response and forwarding shares against its own complaint database, each company against the printed figure, how the credit bureaus closed complaints, and card plan APRs beside the Federal Reserve averages.'
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/credit">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">CREDIT</b> &middot; Stated Complaint Responses and Card Terms Against the Public Record</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('credit.html', 'w').write(page); print('credit.html', len(page))
