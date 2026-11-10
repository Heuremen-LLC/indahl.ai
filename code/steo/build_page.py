#!/usr/bin/env python3
"""build_page.py: writes steo.html, the desk's page draft, from summary_steo.json. Reads no network. The live page is built by the site build from this body."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from steo_headline import headline, cell, WORD, pc, f
S = json.load(open('summary_steo.json')); e = html.escape
src = S['sources']; g = S['gates']; R = S['rows']; FR = S['frame']; AD = S['addendum1']
AF = S['after_data']; SB = {(x['reading'], x['series'], x['block_months']): x for x in AF['block_sensitivity']}
NAME = {'WTI': 'WTI crude oil', 'HH': 'Henry Hub natural gas'}
def iv(c): return 'too few months' if c['lo'] is None or c['months'] < FR['min_months'] else '%s to %s' % (pc(c['lo']), pc(c['hi']))
def table(cells):
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        e(NAME[c['series']]), e(c['cell']), f(c['scored']), f(c['inside']), pc(c['share']), iv(c), WORD[c['outcome']], pc(c['share_above']), pc(c['share_below']), f(c['cannot_tell']), f(c['months'])) for c in cells)
    return ('<div class="tw"><table class="bench"><thead><tr><th>Price</th><th>Stated ahead</th><th>Scored</th><th>Inside</th><th>Inside, percent</th><th>95%% interval, percent</th><th>Reading</th>'
            '<th>Above, percent</th><th>Below, percent</th><th>Cannot tell</th><th>Outcome months</th></tr></thead><tbody>%s</tbody></table></div>' % rows)
wid = S['described']['width']
def wid_rows(): return ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(NAME[x['series']]), e(x['cell']), '' if x['median_width_over_settle'] is None else '%.0f' % (100 * x['median_width_over_settle'])) for x in wid)
gate_line = 'All five known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
sq = g['same_quantity_detail']
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
body = hl + '''<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>
<h2>When EIA states a price interval, how often does the price land inside it?</h2>
<p>Each monthly Short-Term Energy Outlook from the U.S. Energy Information Administration charts the WTI crude oil price and the Henry Hub natural gas price with a &ldquo;95%% NYMEX futures price confidence interval&rdquo;, an upper and a lower bound for each coming month. The chart note says the interval is &ldquo;derived from options market information for the five trading days ending&rdquo; a stated date, and that &ldquo;Intervals not calculated for months with sparse trading in near-the-money options contracts.&rdquo; The January 2012 outlook describes the bounds as &ldquo;the lower and upper limits of a 95-percent confidence interval for the market&rsquo;s expectations of monthly average WTI prices&rdquo;. Since October 2025 the outlook says: &ldquo;We have temporarily suspended our publication of confidence intervals.&rdquo;</p>
<p>The numbers behind each chart are in the outlook&rsquo;s chart gallery workbook. EIA serves only the current one, so this page reads the copies the Internet Archive made at the time, from the %s issue to the %s issue. Each stated interval is set beside EIA&rsquo;s monthly average spot price for that month, WTI at Cushing and Henry Hub. Only months that began after the issue was released are scored. Lead is how many months after the release month the month falls. This page does not say why a price lands outside. The plan, with the rules and the known-good checks, was fixed before any interval was set beside a price. %s</p>
<h2>Issues whose workbook states the level</h2>
%s
<p class="bench-note">One row is one issue, one price and one month. Inside means the monthly average spot price is at or between the two stated bounds. Above and below are printed apart, and a 95 percent interval leaves about 2.5 percent on each side. Rows are not independent. Many issues state an interval for the same month, and prices in neighbouring months move together. So the interval is a moving-block bootstrap over outcome months, in blocks of 12 consecutive months, 2,000 draws, and it is much wider than one that treats rows as independent. Reading: below if the whole interval is under 95 percent, above if it is over, consistent if 95 percent is inside an interval no wider than 15 points, otherwise cannot tell. A cell needs 30 scored rows and 24 outcome months.</p>
<h2>Adding the later issues</h2>
<p>In later issues the workbook holds the bounds without the cell that states the level: for WTI from the June 2020 issue on, and for Henry Hub in the issues from November 2020 to October 2022. Under the plan&rsquo;s rule those rows read cannot tell. The report itself labels the same bounds &ldquo;95%% NYMEX futures price confidence interval&rdquo; on the chart page. The table below also reads a sheet with no level cell as 95 percent when the report for that issue labels it so. This second reading was decided after the first full run and is shown beside the plan&rsquo;s reading, not in place of it. It adds %s rows from %s issues. The June 2023 report has no such label in its text, so its WTI rows stay cannot tell.</p>
%s
<p class="bench-note">Tried after the data with blocks of 6 and 24 months, the plan&rsquo;s readings do not change. In this second reading WTI all leads reads %s with blocks of 6 months and %s with blocks of 24, and Henry Hub all leads reads %s and %s.</p>
<h2>How wide the stated intervals are</h2>
<p>Described and not scored: the median width of the stated interval as a percent of the futures settle price in the same workbook, by lead.</p>
<div class="tw"><table class="bench"><thead><tr><th>Price</th><th>Stated ahead</th><th>Median width, percent of settle</th></tr></thead><tbody>%s</tbody></table></div>
<h2>What this page holds and what it leaves out</h2>
<p>Every archived copy of the workbook is read, and copies with the same bytes are read once. The issue of a copy comes from the date in its chart note and EIA&rsquo;s release table. Where two copies of one issue exist the earliest is used, and %s values differed between copies. EIA states no interval for the release month or earlier, so no row is dropped for having begun before release (%s rows). The Internet Archive holds a workbook for %s of the %s issues released over this span. Described and not scored: %s of the %s WTI rows below the interval in the plan&rsquo;s reading fall in outcome months from November 2014 to February 2016. As a check that both sides are the same price, each workbook&rsquo;s own history column agrees with EIA&rsquo;s current monthly spot series within 2 percent in %s of %s WTI months and %s of %s Henry Hub months before release. Set aside: issues with no archived workbook, the outlook&rsquo;s own point forecast, other prices, and the probability workbooks.</p>
<p class="meta">Sources: EIA Short-Term Energy Outlook chart gallery workbooks as copied by the Internet Archive (%s copies held, %s used), the STEO release table and reports, and EIA monthly spot prices (series RWTC and RNGWHHD, read %s). EIA credits CME Group, Bloomberg, L.P., and Refinitiv an LSEG Business for the interval inputs. Source: U.S. Energy Information Administration. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about once a day, and the newest run is always in <a href="/steo/live.json">/steo/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/steo">steo</a>. The plan was fixed before the comparison it describes (commit %s), and its addendum (commit %s) says what was decided after.</p>
<p class="meta">Data read from: <a href="https://www.eia.gov/outlooks/steo/">EIA Short-Term Energy Outlook</a> &middot; <a href="https://www.eia.gov/outlooks/steo/outlook.php">STEO archive</a> &middot; <a href="https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&amp;s=RWTC&amp;f=M">WTI spot price</a> &middot; <a href="https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm">Henry Hub spot price</a> &middot; <a href="https://web.archive.org/">Internet Archive Wayback Machine</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=steo-all">Respond</a></p>
<section id="replies" data-prefix="steo"></section><script src="/replies.js" defer></script>''' % (
    src['first_issue'][:3].capitalize() + ' 20' + src['first_issue'][3:], src['last_issue'][:3].capitalize() + ' 20' + src['last_issue'][3:], gate_line,
    table(S['cells']), f(AD['rows_level_from_pdf']), AD['issues_level_from_pdf'], table(S['cells_addendum1']),
    WORD[SB[('addendum1', 'WTI', 6)]['outcome']], WORD[SB[('addendum1', 'WTI', 24)]['outcome']], WORD[SB[('addendum1', 'HH', 6)]['outcome']], WORD[SB[('addendum1', 'HH', 24)]['outcome']], wid_rows(),
    f(src['copies_differing_values']), f(R['months_begun_at_release']), AF['issues_with_workbook'], AF['issues_released_in_span'], AF['wti_plan_below_nov2014_feb2016'], cell(S['cells'], 'WTI', 'all leads')['below'], f(sq['WTI']['within_2pct']), f(sq['WTI']['months']), f(sq['HH']['within_2pct']), f(sq['HH']['months']),
    src['copies_held'], src['copies'].get('used', 0), e(str(src['spot_read'].get('WTI'))), e(S['generated'][:10]), e(S['plan_seal']['plan_commit'][:7]), e(AF['plan_addendum_commit'][:7]))
TITLE = 'STEO | Stated Energy Price Intervals Against the Spot Price | Heuremen LLC'
DESC = 'STEO: the 95 percent price intervals EIA stated for WTI crude oil and Henry Hub natural gas in its Short-Term Energy Outlook, set beside the monthly average spot price, by months ahead, with block bootstrap intervals.'
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/steo">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">STEO</b> &middot; Stated Energy Price Intervals Against the Spot Price</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('steo.html', 'w').write(page); print('steo.html', len(page))
