#!/usr/bin/env python3
"""build_page.py: writes petrol_body.html (the page body, draft, for the site builder to wrap), petrol_headline.json and the two row CSVs from summary_petrol.json. Reads no network. Every number comes from the summary."""
import json, os, sys, html, csv
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
from petrol_headline import headline, mname
S = json.load(open('summary_petrol.json')); e = html.escape
if not S['gates_all_passed'] or not S['plan_matches_seal']: print('gates or seal not clean, no page'); sys.exit(1)
P1, P2 = S['part1'], S['part2']; OUT = ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')
def n(x, d=0): return '' if x is None else ('{:,.%df}' % d).format(x)
def cts(c): return ''.join('<td>%d</td>' % c[o] for o in OUT)
def tb(head, rows): return '<div class="tw"><table class="bench"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (''.join('<th>%s</th>' % h for h in head), ''.join(rows))
big, line = headline(S); hm = P1['headline']['month']
CODEOF = {r['reason_detail']: r['reason'] for r in P1['rows'] + P2['rows'] if r['outcome'] == 'CANNOT_TELL'}   # prose reason of the plan to its Faults and Guards 2.0 code
R1, R1A, R2 = P1['headline']['req13']['line'], P1['req13']['line'], P2['headline']['req13']['line']
mrows = []
for m, v in P1['by_member'].items():
    wn = v.get('width_note') or {}; wtxt = ('%s' % n(wn['p90_abs_revision_tbd'])) if wn.get('p90_abs_revision_tbd') is not None else ('relative, see method' if m not in ('Libya', 'IR Iran', 'Venezuela') else '')
    why = ', '.join('%s %d (%s)' % (k, x, CODEOF.get(k, '')) for k, x in v['cannot_tell_why'].items())
    mrows.append('<tr><td>%s</td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(m), cts(v['counts']), e(why), n(v['median_gap_tbd']), wtxt, e('%s %s' % (n(v['largest_gap']), v['largest_gap_month'] or '') if v['largest_gap'] is not None else '')))
mo_rows = ['<tr><td>%s</td>%s</tr>' % (m, cts(c)) for m, c in P1['by_month'].items()]
lat = [r for r in P1['rows'] if r['month'] == hm]
lrows = ['<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(r['member']), n(r['required']), n(r['delivered']), n(r['gap']), n(r['width'], 1), r['outcome'], e(('%s (%s)' % (r['reason'], r['reason_detail'])) if r['reason'] else '')) for r in lat]
by = P2['by_year']
yrows = ['<tr><td>%s</td><td>%d</td>%s<td>%s</td><td>%s</td></tr>' % (y, v['months'], cts(v['counts']), n(v['median_signed_d'], 1), n(v['median_abs_d'], 1)) for y, v in by.items()]
erows = ['<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (r['month'], n(r['weekly_avg'], 1), r['n_weeks'], n(r['monthly']), n(r['d'], 1), r['outcome']) for r in P2['rows']]
sens = P2['sensitivity']; ec = P2['counts']; e2 = P2['headline']; big2 = e2['largest']
c1 = P1['counts']; ro = P1['ruler']
body = """<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>
<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>
<p>Volumes only. This desk reads barrels a day and nothing else.</p>
<p class="meta">The lead number, the count below the required level for the latest month, was chosen after the run. The rules for every outcome were set before it.</p>
<h2>Required production against delivered output</h2>
<p>OPEC+ ministerial statements publish a required production level in thousand barrels a day for each country. OPEC&rsquo;s Monthly Oil Market Report prints what secondary sources say each country produced. For %s, among the 22 countries of the report, delivered output sat above the required level by more than the width below for %d, below it for %d and inside it for %d, and %d read CANNOT_TELL. Across the 24 months from November 2024 to October 2026 the rows read %d ABOVE, %d BELOW, %d CONSISTENT and %d CANNOT_TELL. A reading says where the gap sits. It names no cause and passes no judgement on any country.</p>
<p class="meta">Beside the latest month: %s Across the 24 months: %s</p>
<h2>Where the width comes from</h2>
<p>OPEC publishes no width with a secondary-source figure. The yardstick is OPEC&rsquo;s own restatement of the same month. For each month we took the first print and the next issue&rsquo;s print of that month. For the nine OPEC members with a required level, the width is the 90th percentile of that restatement in tb/d over the months restated up to the October 2024 issue, from the May 2020 issue on. For the ten non-OPEC countries the report prints secondary-source crude only from the May 2024 issue, so the width is one pooled relative figure, %s percent of the delivered value, from the issues May to October 2024. The yardstick is ours. It says how far the delivered figure moved between OPEC&rsquo;s own prints. It is not a published width. The baseline ends before the first month read, so no gap the page reports shaped the width.</p>
<h2>The reading rule</h2>
<p>The gap is the delivered figure minus the required level. A gap over the width reads ABOVE and one under minus the width reads BELOW. A gap inside the width, edges included, reads CONSISTENT. Each gap is a published value set against a published value, so it is a reading with an interval of zero width and no interval method applies. CANNOT_TELL is kept as its own count with its reason and is never joined to CONSISTENT. A row with no required level, no transcribed table or no delivered value reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE. A row whose width could not be formed from enough revisions reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE. The rule is the sealed plan with the addendum of 12 November 2026 (PLAN_ADDENDUM_std2.md). Libya, IR Iran and Venezuela have no required level and read CANNOT_TELL. For the eight countries with voluntary adjustments, only the months that have their own monthly required production table in an OPEC statement have a stated figure. Every other month for those countries reads CANNOT_TELL, no target table transcribed. The UAE has no table after May 2026. The tables are images and were typed from them, with sums checked against the printed increments. Nothing is interpolated.</p>
<h2>Each country</h2>
<p>Counts over the 24 months. The median gap and the largest gap are over the months read. Width is in tb/d for the nine OPEC members.</p>
%s
<h2>Each month</h2>
%s
<h2>The latest month in full</h2>
<p>%s, in tb/d. Source tables and pages for every value are in the downloadable rows file (petrol_part1_rows.csv).</p>
%s
<h2>US crude production, weekly estimate against monthly figure</h2>
<p>EIA&rsquo;s Weekly Petroleum Status Report gives a weekly estimate of US field crude production, which EIA describes as model based and rounded. EIA&rsquo;s monthly figure is the delivered one. We averaged each month&rsquo;s weekly estimates, assigning a week to the month of its week-ending date, and set the average beside the monthly figure. The width is the 90th percentile of the absolute difference over January 2015 to December 2019, %s tb/d. EIA publishes no numeric uncertainty in the files read, so none is used. From January 2020 to %s the %d months read %d ABOVE, %d BELOW, %d CONSISTENT and %d CANNOT_TELL. The largest difference is %s tb/d in %s. At half the width the counts are %d ABOVE, %d BELOW and %d CONSISTENT. At twice the width they are %d, %d and %d.</p>
%s
<p class="meta">Beside the weekly comparison: %s</p>
<h2>Each month of the weekly comparison</h2>
<p>Weekly average minus monthly figure, in tb/d.</p>
%s
<h2>What this page holds and what it leaves out</h2>
<p>It holds the DoC secondary-source crude figures of the MOMR issues from May 2020 on, the required production levels transcribed from the statements listed below, and EIA&rsquo;s two history files. Each EIA file holds one vintage, so earlier prints and later revisions of the monthly figure cannot be read from it. Issues of the MOMR before May 2020 use another layout and are not read, and the December 2023 issue could not be fetched. It leaves out anything that is not a volume, forecasts, any cause of a gap, compensation plans, and liquids other than crude.</p>
<p class="meta">Sources: OPEC, Monthly Oil Market Report, issues May 2020 to October 2026, secondary-sources table. OPEC press statements of the 38th ONOMM (December 2024) and the monthly statements of the eight and seven countries named in the rows file. U.S. Energy Information Administration, Weekly Petroleum Status Report series WCRFPUS2 and Petroleum Supply Monthly series MCRFPUS2.</p>
<p class="meta">Data read from: <a href="https://www.opec.org/monthly-oil-market-report.html">OPEC Monthly Oil Market Report</a> &middot; <a href="https://www.opec.org/pr-detail/28-05-dec-2024.html">38th OPEC and non-OPEC Ministerial Meeting statement</a> &middot; <a href="https://www.eia.gov/dnav/pet/hist_xls/WCRFPUS2w.xls">EIA weekly US field production of crude oil</a> &middot; <a href="https://www.eia.gov/dnav/pet/hist_xls/MCRFPUS2m.xls">EIA monthly US field production of crude oil</a></p>
<p class="meta">The plan was sealed on %s, sha256 %s, before any outcome was computed. Tables are from the run of %s.</p>""" % (
    e(big), e(line), mname(hm), P1['headline']['counts']['ABOVE'], P1['headline']['counts']['BELOW'], P1['headline']['counts']['CONSISTENT'], P1['headline']['counts']['CANNOT_TELL'],
    c1['ABOVE'], c1['BELOW'], c1['CONSISTENT'], c1['CANNOT_TELL'], e(R1), e(R1A), n(ro['non_opec_pooled']['p90_relative'] * 100, 1),
    tb(['Country', 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'CANNOT_TELL reasons', 'Median gap', 'Width', 'Largest gap'], mrows), tb(['Month', 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL'], mo_rows),
    mname(hm), tb(['Country', 'Required', 'Delivered', 'Gap', 'Width', 'Reading', 'Reason'], lrows),
    n(P2['width_tbd']), mname(P2['monthly_last'] + '-01') if False else mname(P2['monthly_last']), e2['scored_months'], ec['ABOVE'], ec['BELOW'], ec['CONSISTENT'], ec['CANNOT_TELL'],
    n(big2['d'], 1), mname(big2['month']), sens['x0.5']['ABOVE'], sens['x0.5']['BELOW'], sens['x0.5']['CONSISTENT'], sens['x2.0']['ABOVE'], sens['x2.0']['BELOW'], sens['x2.0']['CONSISTENT'],
    tb(['Year', 'Months', 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'Median difference with sign', 'Median size of difference'], yrows), e(R2), tb(['Month', 'Weekly average', 'Weeks', 'Monthly figure', 'Difference', 'Reading'], erows),
    e(S['plan_sealed'][:10]), e(S['plan_sha256'][:8]), e(S['updated'][:10]))
open('petrol_body.html', 'w').write(body)
json.dump(dict(big=big, line=line, href='/petrol', updated=S['updated']), open('petrol_headline.json', 'w'), indent=1)
with open('petrol_part1_rows.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['member', 'month', 'outcome', 'reason', 'reason_detail', 'required_tbd', 'delivered_tbd', 'gap_tbd', 'width_tbd', 'delivered_issue', 'delivered_pdf', 'delivered_page', 'delivered_table', 'target_url', 'target_image'])
    for r in P1['rows']: w.writerow([r[k] for k in ('member', 'month', 'outcome', 'reason', 'reason_detail', 'required', 'delivered', 'gap', 'width', 'delivered_issue', 'delivered_pdf', 'delivered_page', 'delivered_table', 'target_url', 'target_image')])
with open('petrol_part2_rows.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['month', 'weekly_avg_tbd', 'n_weeks', 'monthly_tbd', 'difference_tbd', 'width_tbd', 'outcome', 'reason', 'reason_detail'])
    for r in P2['rows']: w.writerow([r[k] for k in ('month', 'weekly_avg', 'n_weeks', 'monthly', 'd', 'width', 'outcome', 'reason', 'reason_detail')])
print('petrol_body.html', len(body)); print(big, '|', line)
