#!/usr/bin/env python3
"""build_page.py: writes census_vintages.html, the desk page draft, from summary_vintages.json. Reads no network. Every number comes from the summary.
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
S = json.load(open('summary_vintages.json')); e = html.escape
if not S['gates_all_passed'] or not S['plan_matches_seal']: print('gates or seal not clean, no page'); sys.exit(1)
C = {c['cell']: c for c in S['cells']}; R = S['rows']; MU = S['multiplier']
def n(x): return '' if x is None else '{:,}'.format(int(x))
def f(x, d=2): return '' if x is None else ('%.' + str(d) + 'f') % x
def lst(xs): return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else 'none')
def cts(c): k = c['counts']; return '<td>%d</td><td>%d</td><td>%d</td><td>%d</td>' % (k['ABOVE'], k['BELOW'], k['CONSISTENT'], k['CANNOT_TELL'])
def who(cell, o): return [r['area'] for r in R if r['cell'] == cell and r['outcome'] == o]
def pct(r): return 100.0 * (r['later'] - r['stated']) / r['stated']
KB = 'V2020 to V2025, July 1 2020'; KC = 'V2020 April 1 2020 to the census count'
def pcs(x): return 'under 0.01 percent in size' if abs(x) < 0.005 else '%s percent' % f(x, 2)
def msg(c): return '%s' % f(c['median_signed_pct'], 3)
def dn(c): return '%d down, %d up' % (c['n_negative'], c['n_positive'])
hb = 'July 1 2020, Vintage 2025 against Vintage 2020: %s' % ', '.join('%d %s' % (C[KB]['counts'][o], o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL'))
kb = C[KB]['counts']; k1 = C['V2020 to V2021, July 1 2020']['counts']
hl = ('For July 1 2020, the Vintage 2025 figure sits above the Vintage 2020 figure by more than the survey yardstick in %d states, below it in %d and inside it in %d, and CANNOT_TELL is kept as its own count (%s here). '
      'The Census Bureau publishes no width with any population estimate, and every comparison that has no yardstick is read CANNOT_TELL.') % (kb['ABOVE'], kb['BELOW'], kb['CONSISTENT'], 'none' if kb['CANNOT_TELL'] == 0 else kb['CANNOT_TELL'])
ca = [c for c in S['cells'] if c['cls'] == 'A']
arows = ''
for c in ca:
    L = c['largest']; arows += '<tr><td>%s</td><td>%d</td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s %d, %s</td></tr>' % (e(c['cell']), c['rows'], cts(c), f(c['median_abs_pct'], 3), msg(c), dn(c), e(L['area']), L['year'], pcs(L['pct']))
def sens(c):
    s = c['sensitivity_multiplier']; o = lambda m: '%d ABOVE, %d BELOW, %d CONSISTENT' % (s[m]['ABOVE'], s[m]['BELOW'], s[m]['CONSISTENT'])
    return 'At one times the standard error, %s. At two times, %s.' % (o('x1.0'), o('x2.0'))
def brow(c):
    L = c['largest']
    return '<tr><td>%s</td><td>%d</td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s %s</td></tr>' % (e(c['cell']), c['rows'], cts(c), f(c['median_abs_pct'], 3), msg(c), dn(c), sens(c), e(L['area']), pcs(L['pct']))
bc = [c for c in S['cells'] if c['cls'] in 'BC']; dc = [c for c in S['cells'] if c['cls'] == 'D']
brows = ''.join(brow(c) for c in bc); drows = ''.join(brow(c) for c in dc)
rb = {r['area']: r for r in R if r['cell'] == KB}; rc = {r['area']: r for r in R if r['cell'] == KC}
trs = ''
for a in S['pes_se']:
    b, c = rb[a], rc[a]
    trs += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(a), n(c['stated']), n(c['later']), f(S['pes_se'][a], 2), f(pct(c), 2), c['outcome'], n(b['stated']), n(b['later']), '%s, %s percent' % (b['outcome'], f(pct(b), 2)))
ba, bb = who(KB, 'ABOVE'), who(KB, 'BELOW'); ca_, cb_ = who(KC, 'ABOVE'), who(KC, 'BELOW')
dmax = max(abs(c['largest']['pct']) for c in dc); dmin_h = min(r['half'] / r['stated'] * 100 for r in R if r['cls'] == 'D')
sr = S['second_ruler']
def srrow(x, label):
    sd, sl = x['second'], x['sealed']
    return '<tr><td>%s</td><td>%d ABOVE, %d BELOW, %d CONSISTENT</td><td>%s</td><td>%d ABOVE, %d BELOW, %d CONSISTENT</td><td>%s</td></tr>' % (label, sl['ABOVE']['count'], sl['BELOW']['count'], sl['CONSISTENT']['count'],
        e('Above: %s. Below: %s.' % (lst(sl['ABOVE']['areas']), lst(sl['BELOW']['areas']))), sd['ABOVE']['count'], sd['BELOW']['count'], sd['CONSISTENT']['count'], e('Above: %s. Below: %s.' % (lst(sd['ABOVE']['areas']), lst(sd['BELOW']['areas']))))
srrows = srrow(sr[0], 'April 1 2020 estimate of Vintage 2020 against the count') + srrow(sr[1], 'July 1 2020, Vintage 2020 against Vintage 2025')
ssc = sr[0]['sealed']; ssd = sr[0]['second']
body = """<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>
<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>
<p>This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>
<h2>What a Vintage restates</h2>
<p>The Census Bureau publishes a Vintage of population estimates each December. A Vintage gives the July 1 estimate of every state for every year it covers. Each Vintage restates earlier years, so the same state and year can be read in several Vintages. Below, the figure from the earlier Vintage is called the earlier figure and the figure for the same state and year in a later Vintage is called the later value. Vintages 2019 and 2020 are built on the 2010 Census. Vintages 2021 and later are built on the 2020 Census. A Vintage is allowed to restate its past and this page makes no claim about which figure is the better one. The page reads where a later value sits against an earlier figure.</p>
<p>The frame is the 50 states and the District of Columbia. The Census Bureau publishes no width with any population estimate, so a comparison has a width only where something the Census Bureau published can supply one.</p>
<h2>Where the width comes from</h2>
<p>After the 2020 Census the Census Bureau ran the Post-Enumeration Survey and published a standard error for the net coverage error of every state. That figure says how precisely the survey measured the net coverage of the 2020 count for the household population. It is a sampling error of the survey. It is not a width on any population estimate. We use it as a yardstick and compute the half-width as %s times the standard error, in percent, times the earlier figure. The multiplier is the two sided 90 percent multiplier that the Census Bureau uses for its survey comparisons. The yardstick is ours.</p>
<p>The yardstick is centered on zero. It ignores each state&rsquo;s published net coverage error, both its sign and its size, so a state the survey says was undercounted or overcounted gets the same centered interval as any other. The survey covers the household population and the figures here are resident totals, so we apply the width as a relative width, and that step is ours too. A second yardstick that is centered on each state&rsquo;s published net coverage error is shown further down, beside this one.</p>
<p>The yardstick fits a comparison that crosses the census, such as an estimate built on the 2010 Census against one built on the 2020 Census, or an estimate against the census count. It does not fit a comparison between two Vintages on the same base. They share the level of that base. We do not use the spread between Vintages as a width either. That spread is the thing being read, and it would make every row read inside by construction. So every comparison between two Vintages on the same base is read CANNOT_TELL with the reason no width. We wrote that rule down before we computed anything.</p>
<h2>The reading rule</h2>
<p>For each state the interval is the earlier figure plus or minus its half-width. A later value inside the interval, edges included, reads CONSISTENT. A later value over the top reads ABOVE and one under the bottom reads BELOW. A state with no width reads CANNOT_TELL, and each reason is counted apart. The four readings are counted for each comparison and printed as four counts. No share is read against 90 percent. The interval is a yardstick and not a coverage figure for the later value. CONSISTENT does not say an estimate is right. It says the later value is within what the survey of the 2020 count can separate.</p>
<h2>Which comparison leads</h2>
<p>The plan named no headline comparison. We chose the latest Vintage for the lead after the run. Against Vintage 2021 the same July 1 2020 comparison reads %d ABOVE, %d BELOW and %d CONSISTENT, and the table below shows every Vintage. The comparisons of July 1 2020 in Vintage 2020 against Vintages 2021 to 2025 are not five separate tests. They show the same gap as the April 1 2020 comparison against the count, carried forward with later population components.</p>
<h2>Comparisons between Vintages on the same base</h2>
<p>These are every July 1 estimate that two Vintages on the same census base both hold. Each row is one state, one year and one pair of Vintages, and each cell pools the years the two Vintages share. All of them read CANNOT_TELL by the rule above. They are described and not scored. The size of a change is shown two ways. The median size ignores direction. The median with sign keeps it, so a value near zero beside a large median size means the changes go both ways. The count of rows that went down and up is beside it. The largest single change of each pair is named.</p>
<div class="tw"><table class="bench"><thead><tr><th>Vintage pair</th><th>Rows</th><th>ABOVE</th><th>BELOW</th><th>CONSISTENT</th><th>CANNOT_TELL, no width</th><th>Median size of change, percent, direction ignored</th><th>Median change with sign, percent</th><th>Rows down and up</th><th>Largest single change</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Vintage 2019 to Vintage 2020 covers 2010 to 2019. The pairs among Vintages 2021 to 2025 cover the years each pair shares. Vintage 2021 comes from the Census Data API (2021/pep/population). It has no flat-file check beyond one test, that its 51 values for July 1 2020 add to 331,501,080 and its 51 values for July 1 2021 add to 331,893,745, the totals of the 50 states and the District of Columbia. The other Vintages come from the Census Bureau population estimates files.</p>
<h2>Across the change of base</h2>
<p>Vintage 2020 gave the July 1 2020 estimate and an April 1 2020 estimate on the 2010 Census base. Vintages 2021 to 2025 restate July 1 2020 on the 2020 Census base, and the 2020 Census count itself was published in 2021. Those comparisons cross the census, so the survey yardstick applies. The table has one row per comparison, with the median size and the median with sign beside each other. The sensitivity column shows how the counts move if the multiplier is changed, and the reading that counts is the one at %s times.</p>
<div class="tw"><table class="bench"><thead><tr><th>Comparison</th><th>States</th><th>ABOVE</th><th>BELOW</th><th>CONSISTENT</th><th>CANNOT_TELL</th><th>Median size of change, percent, direction ignored</th><th>Median change with sign, percent</th><th>States down and up</th><th>Sensitivity, counts only</th><th>Largest change</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">ABOVE means the later value sits over the interval of the earlier figure. BELOW means it sits under. A later value above the 2010 based estimate is a state where the 2020 based figure came out larger.</p>
<p>For July 1 2020, Vintage 2020 against Vintage 2025, %s read ABOVE and %s reads BELOW. Against the 2020 Census count, the April 1 2020 estimate of Vintage 2020 reads ABOVE for %s and BELOW for %s. The same states sit outside the interval in both comparisons, apart from Massachusetts, which is outside only against the count.</p>
<h2>A second yardstick, added after the referee</h2>
<p>The outside referee asked what happens if the interval is centered on each state&rsquo;s published net coverage error and not on zero. We added that second reading after the referee. It is not a change to the sealed rule above, and no outcome in the tables above uses it. For each state the gap is the later value minus the earlier figure, as a percent of the earlier figure. The second reading takes the published net coverage error away from that gap and reads the rest against %s times the standard error. The sealed reading stays the lead. The two are shown side by side. Two reasonable yardsticks disagree, and the disagreement is part of what the data says.</p>
<div class="tw"><table class="bench"><thead><tr><th>Comparison</th><th>Sealed yardstick, counts</th><th>Sealed yardstick, states outside</th><th>Second yardstick, counts</th><th>Second yardstick, states outside</th></tr></thead><tbody>%s</tbody></table></div>
<h2>The count against later bases</h2>
<p>Each Vintage from 2022 on gives an estimates base for April 2020. The base is built from the 2020 Census count with small adjustments, so these rows read inside by construction. The widest gap between the base and the count is %s percent, against yardsticks of %s percent and up. This comparison tests nothing about the estimates. It shows that the base is the count.</p>
<div class="tw"><table class="bench"><thead><tr><th>Comparison</th><th>States</th><th>ABOVE</th><th>BELOW</th><th>CONSISTENT</th><th>CANNOT_TELL</th><th>Median size of change, percent, direction ignored</th><th>Median change with sign, percent</th><th>States down and up</th><th>Sensitivity, counts only</th><th>Largest change</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Each state</h2>
<p>The table gives each state with the April 1 2020 estimate of Vintage 2020, the 2020 Census count and the survey standard error, then the July 1 2020 estimate of Vintage 2020 and its value in Vintage 2025.</p>
<div class="tw"><table class="bench"><thead><tr><th>State</th><th>April 1 2020 estimate, Vintage 2020</th><th>2020 Census count</th><th>Survey standard error, percent</th><th>Count against estimate, percent</th><th>Reading against the count</th><th>July 1 2020 estimate, Vintage 2020</th><th>July 1 2020, Vintage 2025</th><th>Reading against Vintage 2025</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Values are as the Census Bureau files and API serve them. Intervals are ours, computed from the published survey standard error. The census count is the resident population from the 2020 redistricting file, API dataset 2020/dec/pl.</p>
<h2>What this page holds and what it leaves out</h2>
<p>It holds the state July 1 estimates of Vintages 2019 to 2025, the April 1 2020 estimate of Vintage 2020, the estimates base of Vintages 2022 to 2025, the 2020 Census count and the survey standard errors from the CENSUS COVERAGE desk. It leaves out counties, age, sex and race detail, Puerto Rico, July estimates against the April count (the dates differ), and any reason a Vintage restated. Vintage 2026 arrives in December and this page does not refresh.</p>
<p>What came before the seal. We copied the raw files and read the first rows of two API pulls before the plan was written. The scout had also printed California, Texas and Arkansas. No restatement, outcome or count existed then. The seal covers the text of the plan and its rule. The code was committed after the first reading. After the outside referee we added the second yardstick, the signed medians, the Vintage 2021 totals check and this wording, and none of them changed a sealed reading.</p>
<p class="meta">Sources: U.S. Census Bureau, Population Estimates Program state files for Vintages 2019 to 2025, Census Data API datasets 2019/pep/population, 2021/pep/population, 2020/dec/pl and 2020/dec/pes. PES20-G-02RV, June 2022. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>
<p class="meta">Data read from: <a href="https://www.census.gov/programs-surveys/popest.html">Census Population Estimates Program</a> &middot; <a href="https://www.census.gov/data/developers/data-sets.html">Census Data API datasets</a> &middot; <a href="https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/2020-source-and-accuracy-pes-estimates.pdf">Source and Accuracy of the 2020 PES Person Estimates</a></p>
<p class="meta">The plan was sealed on %s, commit %s, before any count of outcomes was computed. Tables are from the run of %s.</p>""" % (
    e(hb), hl, MU, k1['ABOVE'], k1['BELOW'], k1['CONSISTENT'], arows, MU, brows, lst(ba), lst(bb), lst(ca_), lst(cb_), MU, srrows, f(dmax, 2), f(dmin_h, 1), drows, trs, e(S['plan_commit_time'][:10]), e(S['plan_commit'][:7]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CENSUS | Population Estimates Against Their Later Vintages | Heuremen LLC</title>
<meta name="description" content="CENSUS: each state July 1 population estimate as an earlier Vintage gave it, set beside later Vintages and the 2020 Census count, with the Census Bureau survey standard error as the only yardstick and CANNOT_TELL kept as its own count.">
<meta name="tdm-reservation" content="1">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">CENSUS</b> &middot; Population Estimates Against Their Later Vintages</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % body
open('census_vintages.html', 'w').write(page); print('census_vintages.html', len(page))
