#!/usr/bin/env python3
"""build_page.py: writes census_coverage.html, the desk page, from summary_coverage.json. Reads no network. Every number comes from the summary.
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
S = json.load(open('summary_coverage.json')); e = html.escape
if not S['gates_all_passed'] or not S['plan_matches_seal']: print('gates or seal not clean, no page'); sys.exit(1)
C = S['counts']; A = S['areas']; D = S['da']; U = S['us_pes']; CP = S['components']; F = S['floor']
WORD = {'BELOW': 'BELOW, interval under zero (undercount)', 'ABOVE': 'ABOVE, interval over zero (overcount)', 'CONSISTENT': 'CONSISTENT, interval holds zero', 'CANNOT_TELL': 'CANNOT_TELL'}
CW = {'BELOW': 'BELOW', 'ABOVE': 'ABOVE', 'CONSISTENT': 'CONSISTENT', 'CANNOT_TELL': 'CANNOT_TELL'}
def cw(x): return CW[x['outcome']] + (' (%s)' % x['reason'] if x['outcome'] == 'CANNOT_TELL' and x.get('reason') else '')   # 12 Nov 2026: Faults and Guards 2.0, the reason sits beside the word
def f(x, d=2): return '' if x is None else ('%.' + str(d) + 'f') % x
def n(x): return '' if x is None else '{:,}'.format(int(x))
def lst(xs): return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else (xs[0] if xs else 'none')
hb = '%d areas BELOW, %d ABOVE, %d CANNOT_TELL' % (C['BELOW'], C['ABOVE'], C['CANNOT_TELL'])
hl = 'The Census Bureau measured the 2020 count of each state against its own independent survey. At the 90 percent level that Census states, the %d states and the District of Columbia are each read against zero with no tolerance, so an area reads BELOW, ABOVE or CANNOT_TELL. CANNOT_TELL is kept as its own count and is split by reason. %s' % (len(A) - 1, S['req13']['line'])
rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td></tr>' % (e(a['area']), n(a['household_count']), n(a['resident_total']), f(a['nce']), f(a['se']), f(a['lo90']), f(a['hi90']), cw(a)) for a in A)
def crow(c):
    cells = ''.join('<td>%s &plusmn; %s</td>' % (f(c[k]['est'], 1), f(c[k]['se'], 2 if c.get('area') == 'United States' else 1)) for k in ('omissions', 'duplication', 'other_erroneous'))
    return '<tr><td>%s</td>%s</tr>' % (e(c['area']), cells)
crows = ''.join(crow(c) for c in S['component_rows'])
natrow = ''.join('<td>%s &plusmn; %s</td>' % (f(CP['national'][k]['est'], 1), f(CP['national'][k]['se'], 2)) for k in ('omissions', 'duplication', 'other_erroneous')) + '</tr>'
import math
MINF = min((abs(a['nce'] / a['se']), a['area']) for a in A if a['outcome'] in ('BELOW', 'ABOVE')); MAXU = max((abs(a['nce'] / a['se']), a['area']) for a in A if a['outcome'] == 'CANNOT_TELL' and a.get('reason') == 'STRADDLES_EDGE')
MLO = math.floor(MAXU[0] * 100) / 100 + 0.01; MHI = math.floor(MINF[0] * 100) / 100
dasig = lambda v: ('an undercount' if v < 0 else 'an overcount')
body = '''<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>
<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>
<h2>Where each state count sits against the Census Bureau&rsquo;s own survey</h2>
<p>This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>
<p>After the 2020 Census the Census Bureau ran the Post-Enumeration Survey. It is an independent sample survey whose people are matched case by case to the census. From it Census publishes a net coverage error for each state with a standard error. Net coverage error is the census count minus the survey estimate, as a percent. A negative figure is an undercount and a positive figure is an overcount. The survey is the Census Bureau&rsquo;s own measure of its own count. This page does not judge the count. It sets each published count beside the width of the second measurement and reads where the count sits.</p>
<h2>Who the survey covers</h2>
<p>The survey covers the household population of the 50 states and the District of Columbia on 1 April 2020. It leaves out people living in group quarters such as nursing homes, college dormitories, jails, shelters and military barracks, and people living in Remote Alaska areas. The census count inside the survey tables is therefore a household count rounded to the thousand, and it is smaller than the resident total. Both are in the table. The gap between them is group quarters and Remote Alaska and is not an undercount figure. The reading applies to the household count. Puerto Rico is published in a separate table and is not read here.</p>
<h2>The reading rule</h2>
<p>Three terms first. The standard error is how far the survey figure could move from sampling alone. Nonsampling error is anything that moves a figure other than sampling noise, for example people matched incorrectly, and the standard error leaves it out. A 90 percent interval is the range that holds the true value 9 times in 10 if the survey method is unbiased. Census states that survey comparisons are tested at the 90 percent confidence level with a two sided test, and its state charts show a 90 percent confidence interval around each estimate. We compute the interval as the net coverage error plus or minus 1.645 times its standard error. This uses the 90 percent level Census states. The lowest flagged ratio of net coverage error to standard error is %s (%s) and the highest unflagged is %s (%s), so no multiplier from %s to %s changes the %d flagged areas. An area reads BELOW when the whole interval is under zero, so the census count sits below the survey estimate. It reads ABOVE when the whole interval is over zero. Zero is a figure with no tolerance around it and the plan names no size that matters, so an interval that holds zero reads CANNOT_TELL with the reason STRADDLES_EDGE and is not read as agreement with zero. It reads CANNOT_TELL with the reason NO_INTERVAL_FORMABLE when no width is published. The test of both alternatives is not applied, as no size is named. CONSISTENT is not available. The counts are BELOW, ABOVE and CANNOT_TELL split by reason, and CANNOT_TELL is never folded into another count. Beside the headline the page prints the count of failed reads, which is NOTHING_RETURNED and sits outside every count, and the CANNOT_TELL share split by reason. The rule was written down and sealed before any count of outcomes was computed, and the 12 November 2026 addendum moved only the outcome rule to Faults and Guards 2.0. The raw data and one look at the full list came before the seal, see the end.</p>
<h2>The states</h2>
<table class="bench"><thead><tr><th>Outcome</th><th>Areas</th><th>Which</th></tr></thead><tbody>
<tr><td>BELOW</td><td>%d</td><td>%s</td></tr>
<tr><td>ABOVE</td><td>%d</td><td>%s</td></tr>
<tr><td>CONSISTENT</td><td>%d</td><td>not available, zero has no tolerance and no size that matters is named</td></tr>
<tr><td>CANNOT_TELL</td><td>%d</td><td>%s, the interval holds zero, listed in the full table. Every area publishes a standard error, so none is NO_INTERVAL_FORMABLE</td></tr></tbody></table>
<p class="bench-note">These are the same areas Census names in its own report, six with an undercount and eight with an overcount. We checked the match in code against the asterisks in the Census table and it is exact. A reading of CANNOT_TELL does not say the count is right. It says the interval of the survey holds zero, and without a named size that matters the page does not read that as agreement with zero. Census marks the same %d areas. A 90 percent test flags about one area in ten when nothing is off, and the areas are not independent of each other, so we do not read the count of %d as a result. The standard error also leaves out nonsampling error, as Census states in the same document, and we name no cause for why an area reads as it does.</p>
<div class="tw"><table class="bench"><thead><tr><th>Area</th><th>Household count in the survey</th><th>Resident total, includes group quarters and Remote Alaska, not used in the reading</th><th>Net coverage error, percent</th><th>Standard error, percent</th><th>90 percent interval, percent</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Household counts and survey figures are as the Census Bureau API serves them for dataset 2020/dec/pes, group G_STATES. Resident totals are from the 2020 redistricting file. The interval is ours and is computed from the two published figures.</p>
<p class="bench-note">BELOW means the census count missed people, an undercount. ABOVE means the census count was more than the people there, an overcount. CANNOT_TELL with STRADDLES_EDGE means the interval holds zero.</p>
<h2>The United States</h2>
<p>For the nation the survey gives a net coverage error of %s percent with a standard error of %s, so the 90 percent interval is %s to %s percent and the national cell reads %s. This is its own cell and is not a count of areas.</p>
<h2>A second method, Demographic Analysis</h2>
<p>Demographic Analysis is a different method. It builds the population from births, deaths, migration and Medicare records and does not use a survey. It covers the total resident population, and the survey covers the household population outside Remote Alaska, so the two are not the same people and are never merged here. Census gives three Demographic Analysis series for 2020. The low series is a net coverage error of %s percent and is %s, the middle series is %s percent and is %s, and the high series is %s percent and is %s. The three series are scenarios that Census gives and not a statistical interval, and Census states no standard error for them, so this cell reads the range and not an interval. %s The survey national estimate of %s percent sits inside that range%s.</p>
<h2>Omissions and erroneous enumerations</h2>
<p>Census also publishes the pieces behind the net figure for each state. Omissions are people the census missed. Erroneous enumerations are people counted that should not have been, here split into duplicates and other reasons. Each value is shown in percent with its standard error, and the national value is the first row. These are values only. Census rounds them to one decimal place and a rounded value cannot carry a reading, so we do not read them against the national value or against the net reading above. Census does not publish a total of erroneous enumerations by state, so none is formed.</p>
<div class="tw"><table class="bench"><thead><tr><th>Area</th><th>Omissions, percent &plusmn; standard error</th><th>Duplicates, percent &plusmn; standard error</th><th>Other erroneous, percent &plusmn; standard error</th></tr></thead><tbody><tr><td>United States</td>%s%s</tbody></table></div>
<h2>What this page holds and what it leaves out</h2>
<p>It holds the state figures of one Census Bureau release, the Post-Enumeration Survey results of 2022, and the Demographic Analysis release of 10 March 2022. Nothing on it refreshes. It leaves out regions, race, age and housing units, Puerto Rico, any cause, and any effect on apportionment or funding.</p>
<p>What came before the seal. We pulled the raw data before the plan was written and sealed. We also printed the full list of survey figures once, with a quick marker at 1.645 times the standard error, and it matched the areas Census names. So the match with the Census asterisks is a replication and not a prediction. No count of outcomes or page existed then. The seal covers the text of the plan and the rule and nothing else. The code was committed after the first reading. The first run failed two of its own checks. Our parser missed counts under one million, which turned every outcome into CANNOT_TELL, so no outcome came from the bad parser. We fixed the parser and the rule did not change.</p>
<p class="meta">Sources: U.S. Census Bureau, Census Data API, 2020 Post-Enumeration Survey (dataset 2020/dec/pes) and 2020 redistricting file. U.S. Census Bureau, Census Coverage Estimates for People in the United States by State and Census Operations, PES20-G-02RV, June 2022, and Source and Accuracy of the 2020 PES Person Estimates. U.S. Census Bureau press release CB22-CN.02, 10 March 2022. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>
<p class="meta">Data read from: <a href="https://www.census.gov/newsroom/press-releases/2022/2020-census-estimates-of-undercount-and-overcount.html">Census release of estimates of undercount and overcount</a> &middot; <a href="https://www.census.gov/programs-surveys/decennial-census/about/coverage-measurement/pes.html">Census Post-Enumeration Survey</a> &middot; <a href="https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/census-coverage-estimates-for-people-in-the-united-states-by-state-and-census-operations.pdf">PES20-G-02RV</a> &middot; <a href="https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/2020-source-and-accuracy-pes-estimates.pdf">Source and accuracy statement</a> &middot; <a href="https://api.census.gov/data/2020/dec/pes.html">Census Data API, 2020 PES</a></p>
<p class="meta">The plan was sealed on %s, commit %s, before any count of outcomes was computed. Tables are from the run of %s.</p>''' % (
    e(hb), e(hl), '%.2f' % MINF[0], e(MINF[1]), '%.2f' % MAXU[0], e(MAXU[1]), '%.2f' % MLO, '%.2f' % MHI, C['BELOW'] + C['ABOVE'], C['BELOW'], e(lst(S['below'])), C['ABOVE'], e(lst(S['above'])), C['CONSISTENT'], C['CANNOT_TELL'], e(', '.join('%d %s' % (v, k) for k, v in sorted(S['cannot_tell_why'].items())) or 'none'),
    C['BELOW'] + C['ABOVE'], C['BELOW'] + C['ABOVE'], rows,
    f(U['nce']), f(U['se']), f(U['lo90']), f(U['hi90']), cw(U),
    f(D['low']), dasig(D['low']), f(D['middle']), dasig(D['middle']), f(D['high']), dasig(D['high']), ('The range holds zero, so the cell reads CANNOT_TELL (%s).' % D['reason']) if D['outcome'] == 'CANNOT_TELL' and D.get('reason') == 'STRADDLES_EDGE' else ('The cell reads %s.' % D['outcome']), f(U['nce']), '' if S['da']['pes_national_interval_inside_range'] else ', though its interval does not',
    natrow, crows,
    e(S['plan_commit_time'][:10]), e(S['plan_commit'][:7]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CENSUS | The Census Count Against Its Own Survey | Heuremen LLC</title>
<meta name="description" content="CENSUS: the 2020 Census count of each state set beside the Census Bureau's own Post-Enumeration Survey, with the 90 percent interval Census uses, and the Demographic Analysis range as a separate cell.">
<meta name="tdm-reservation" content="1">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">CENSUS</b> &middot; The Census Count Against Its Own Survey</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % body
open('census_coverage.html', 'w').write(page); print('census_coverage.html', len(page))
