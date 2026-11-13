#!/usr/bin/env python3
"""build_page.py: writes census_revisions.html, the desk page, from summary_census.json. Reads no network. Every number comes from the summary.
indahl-ai/build_site.py takes the body from this file. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from census_headline import headline, cell as cellof, join, mname, NUM
S = json.load(open('summary_census.json')); e = html.escape
import heuremen_kit as K
WORD = {'ABOVE': 'share above 90', 'BELOW': 'share below 90', 'CONSISTENT': 'share consistent with 90', 'CANNOT_TELL': 'cannot tell'}
def word(c): return WORD[c['outcome']] + (' (%s)' % c['reason'] if c['outcome'] == 'CANNOT_TELL' and c.get('reason') else '')   # 12 Nov 2026: Faults and Guards 2.0, reason beside the word
SER = {'SALES': 'New residential sales', 'STARTS': 'Housing starts', 'COMPLETIONS': 'Housing completions', 'PERMITS': 'Building permits', 'RETAIL': 'Advance retail and food services'}
STEP = {'S1': 'second print', 'S2': 'third print', 'S3': 'current value'}
def pc(x, d=1): return '' if x is None else ('%.' + str(d) + 'f') % (100 * x)
def why(c): return ', '.join('%d %s' % (v, k) for k, v in sorted(c['cannot_tell_why'].items(), key=lambda kv: -kv[1])) or 'none'
C = S['cells']; g = S['gates']; R = S['rows']
def row(c, full=False):
    return '<tr><td>%s</td>%s<td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%d</td><td>%s</td></tr>' % (
        e(SER[c['series']]), '<td>%s</td>' % e(c['geo']) if full else '', STEP[c['step']], e(c['width_basis']), c['scored'], c['inside'], c['above'], c['below'], pc(c['share']), pc(c['lo']), pc(c['hi']), word(c), c['cannot_tell'], e(why(c)))
HEAD = '<th>Series</th>%s<th>Compared with</th><th>Width</th><th>Scored</th><th>Inside</th><th>Above</th><th>Below</th><th>Inside, percent</th><th>95%% interval, percent</th><th>Reading of the share against 90 percent</th><th>Cannot tell</th><th>Why</th>'
us_tab = ''.join(row(c) for c in C if c['geo'] == 'US' and c['series'] != 'PERMITS')
all_tab = ''.join(row(c, True) for c in C if c['geo'] != 'US' or c['series'] == 'PERMITS')
def cl(s, st): return cellof(S, s, st)
def revline():
    out = []
    for s in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL'):
        c = cl(s, 'S1'); out.append('%s %.1f percent of the first print, or %.2f stated half-widths' % (SER[s].lower(), c['median_abs_rev_pct'], c['median_abs_miss_half_widths']))
    return ', '.join(out)
def p90line():
    out = []
    for s in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL'):
        a, b = cl(s, 'S1')['p90_abs_miss_half_widths'], cl(s, 'S2')['p90_abs_miss_half_widths']
        out.append('%s %.2f and %.2f' % (SER[s].lower(), a, b))
    return ', '.join(out)
def sens_line():
    out = []
    for s in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL'):
        c = cl(s, 'S1')
        if c['share_rse_minus_half'] is not None: out.append('%s %s to %s' % (SER[s].lower(), pc(c['share_rse_plus_half']), pc(c['share_rse_minus_half'])))
    return ', '.join(out)
def narrow_line():
    cs = [cl(s, st) for s in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL') for st in ('S1', 'S2')]
    sh = lambda k: [100.0 * c[k]['inside'] / c[k]['scored'] for c in cs]
    return min(sh('at_half_width')), max(sh('at_half_width')), min(sh('at_two_thirds_width')), max(sh('at_two_thirds_width'))
def counted_in():
    out = []
    for st in ('S1', 'S2'):
        c = cl('RETAIL', st)['counted_in']
        word = {'ABOVE': 'above', 'BELOW': 'below'}.get(K.read(c['lo'], c['hi'], bound=0.9)[0], 'straddles')   # 12 Nov 2026: a point figure with no tolerance has no consistent
        out.append('%s %d of %d inside (%s to %s percent, %s)' % ('second print' if st == 'S1' else 'third print', c['inside'], c['scored'], pc(c['lo']), pc(c['hi']), word))
    # national housing cells: does counting the annual revision rows in change a reading?
    same = True
    for s in ('SALES', 'STARTS', 'COMPLETIONS'):
        for st in ('S1', 'S2'):
            c = cl(s, st); ci = c['counted_in']; w = K.read(ci['lo'], ci['hi'], bound=0.9)[0]
            same &= (w == c['outcome'])
    return out, same
brk = S['series_meta']['RSAFS']['retail_break_vintage']; det = S['series_meta']['RSAFS']['annual_revision_detail']
d1, d2 = det['2025-04-25'], det[brk]
HB, HL = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HB), e(HL))
lo_h, hi_h, lo_t, hi_t = narrow_line(); ci_lines, ci_same = counted_in()
srm = S['same_release_months']['HSN1F']
nm = {k: cl(k, 'S1') for k in ('SALES', 'STARTS', 'COMPLETIONS')}
body = '''<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>
<h2>When the Census Bureau states how uncertain a first print is, does the later value stay inside?</h2>
<p>This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>
<p>The Census Bureau publishes advance monthly estimates of new home sales, housing starts and completions, and retail and food services sales. Each comes with a sampling uncertainty, and each month is then revised. This page sets the first print of each month, with the 90 percent interval Census states for it, beside the value the same month carries after one revision, after two, and today.</p>
<h2>What the stated width is</h2>
<p>For sales, starts and completions the Census API field E_TOTAL is the estimated relative standard error in percent, rounded to a whole number. Census prints it as the average relative standard error for the latest six months. Census gives the 90 percent interval as 1.645 times the standard error. For advance retail the field E_SM is the median estimated coefficient of variation Census gives for the monthly total, in percent. Census gives the interval as the estimated value plus or minus 1.753 times the coefficient of variation times the value. Quotes and links are in the desk notes.</p>
<p>Census states this width for sampling error of the level. Most of what moves a first print later is late reports and re-benchmarking, which sampling error does not describe, so a later value inside the interval is not a test of Census&rsquo;s sampling error. Census states 90 percent as the share of its intervals that would hold the value a complete count gives, and a later revised estimate is not that value. Reading the share of later values inside the interval against 90 percent is our reading.</p>
<h2>The national totals</h2>
<div class="tw"><table class="bench"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">One row is one month. Inside means the later value sits inside the interval stated for the first print. A share is inside rows over inside, above and below rows. Cannot tell rows are shown beside every cell and are never part of a share. The interval is a 95 percent Wilson interval. Months overlap in what they measure, so the interval is narrower than it should be. The figure 90 percent has no tolerance around it, so a cell reads above when its interval lies over 90 percent, below when it lies under, and cannot tell with the reason STRADDLES_EDGE when its interval holds 90 percent. A cell with fewer than ten scored rows reads cannot tell with the reason TOO_WIDE_TO_RESOLVE, and a cell with no scored row reads cannot tell with the reason NO_INTERVAL_FORMABLE. No size that matters is named for this figure, so the test of both alternatives is not applied. Beside the headline the page prints the count of failed reads, which is NOTHING_RETURNED and sits outside every share, and the cannot tell count split by reason. In %s months the second print came in the same release as the first (%s), so those rows show no revision. With them left out, sales read %d of %d, starts %d of %d and completions %d of %d, and the readings do not change.</p>
<h2>Regions and permits</h2>
<div class="tw"><table class="bench"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Regions are separate cells and are not pooled with the national totals. They sum to the national total, so they are not independent of it. Building permits carry no published width in the API, so every permits row reads cannot tell with the reason no width.</p>
<h2>How big the revisions are</h2>
<p>Median absolute revision from the first print to the second print: %s. Moving the served width down and up by its rounding, half a point for sales, starts and completions and 0.05 for retail, moves the share of second prints inside to (up, down): %s percent. These are described and not scored.</p>
<p>The 90th percentile of the miss, in stated half-widths, for the second and third print: %s. The stated interval is several times the size of a typical revision. Cutting every stated half-width to two thirds would leave the national cells at %.1f to %.1f percent inside. Cutting them to half would take them to %.1f to %.1f percent. These two lines are computed in code after the data and are described and not scored.</p>
<h2>The retail revisions</h2>
<p>There are two retail revisions in the record. The vintage of 2025-04-25 is the April 2025 annual revision, in which Census removed nonemployers from the series. It changed %d months by a median of %.1f percent and at most %.1f percent. The vintage of %s is the annual revision Census announced in its advance retail release of 15 October 2026 (CB26-165): &ldquo;Monthly retail sales estimates were revised on September 28, 2026 based on historical corrections and the results of the 2023 and 2024 Annual Integrated Economic Survey.&rdquo; It changed %d months by a median of %.1f percent and at most %.1f percent. The sealed rule in the plan, a change of more than 3 percent in a month at least 14 months older than the newest, caught only the second. First prints before %s are not compared with values from after it, and every retail current-value row falls there.</p>
<h2>Annual revisions</h2>
<p>A second or third print is not scored when an annual revision vintage falls between the first print and that print. Such rows are counted as cannot tell with the reason NO_INTERVAL_FORMABLE. The later value is not the one the stated interval was made for. The current value is the annual revised one by design. The rows dropped for an annual revision are the larger revisions. Counted in, advance retail would read %s. %s</p>
<h2>What this page holds and what it leaves out</h2>
<p>Widths. Census serves the current width of each month and does not keep the width as printed at the time. Our own dated copies of the Census response began on %s. Until a month has a copy made within three days of its release, its width is the one served now, and the table says so in the Width column. %d rows have a width as printed. The history is read with widths as served in 2026 and is labelled that way everywhere.</p>
<p>Dates. First prints and later values come from the St. Louis Fed ALFRED archive, one vintage per call. A vintage date is the day ALFRED first recorded the values. It stands in for the Census release date. In the release texts we compared, the two dates were the same. The first print of a month is the earliest vintage that holds it, from January 2016 vintages on. The second print is the value in the vintage where the next month first appears, and the third print the value in the vintage where the month after next first appears. The retail release text before 2026 was not read.</p>
<p>The frame has %s rows from %s to %s across all series and steps. The plan was fixed before the comparison, and its seal and the run code are in the public desk folder linked at the foot of this page. M3 durable goods orders, construction spending and international trade are copied by the snapshot job and are not read on this page.</p>
<p class="meta">Sources: U.S. Census Bureau, Economic Indicators Time Series API (new residential sales, new residential construction, monthly retail trade) and the Census explanatory notes. Federal Reserve Bank of St. Louis, ALFRED archival series HSN1F, HOUST, PERMIT, COMPUTSA and RSAFS, from Census and HUD data. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau. Tables are from the run of %s.</p>
<p class="meta">Data read from: <a href="https://www.census.gov/construction/nrc/index.html">Census new residential construction</a> &middot; <a href="https://www.census.gov/construction/nrs/index.html">Census new residential sales</a> &middot; <a href="https://www.census.gov/retail/marts/how_surveys_are_collected.html">Census monthly retail trade, how surveys are collected</a> &middot; <a href="https://www.census.gov/retail/sales.html">Census advance retail release</a> &middot; <a href="https://alfred.stlouisfed.org/">ALFRED, St. Louis Fed</a></p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/census">census</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">The headline and the tables are from the run of %s. The desk reads again about once a day, and the newest run is always in <a href="/census/live.json">/census/live.json</a>.</p>''' % (
    HEAD % '', us_tab, NUM.get(len(srm), str(len(srm))), join([mname(m) for m in srm]),
    nm['SALES']['without_same_release']['inside'], nm['SALES']['without_same_release']['scored'], nm['STARTS']['without_same_release']['inside'], nm['STARTS']['without_same_release']['scored'], nm['COMPLETIONS']['without_same_release']['inside'], nm['COMPLETIONS']['without_same_release']['scored'],
    HEAD % '<th>Geography</th>', all_tab, e(revline()), e(sens_line()), e(p90line()), lo_t, hi_t, lo_h, hi_h,
    d1['all_changed'], d1['all_median_changed_pct'], d1['all_max_pct'], e(brk), d2['all_changed'], d2['all_median_changed_pct'], d2['all_max_pct'], e(brk),
    e(' and '.join(ci_lines)),
    ('The national housing cells read the same with those rows counted in.' if ci_same else 'The national housing cells change reading with those rows counted in, and the counts are in the desk notes.'),
    e('%s-%s-%s' % (S['snapshots']['earliest'][:4], S['snapshots']['earliest'][4:6], S['snapshots']['earliest'][6:8])), S['snapshots']['as_printed_rows'],
    '{:,}'.format(R['total']), e(R['first_month']), e(R['last_month']), e(S['generated'][:10]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CENSUS | Stated Uncertainty Against Later Revisions | Heuremen LLC</title>
<meta name="description" content="CENSUS: the first print of each Census economic indicator with its stated 90 percent interval, set beside the value after one revision, two, and today.">
<meta name="tdm-reservation" content="1">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">CENSUS</b> &middot; Stated Uncertainty Against Later Revisions</h1></div></section>
<main class="wrap">%s
%s</main>
</body>
</html>
''' % (hl, body)
open('census_revisions.html', 'w').write(page); print('census_revisions.html', len(page))
