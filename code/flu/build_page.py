#!/usr/bin/env python3
"""build_page.py: writes flu.html, the desk's page draft, from summary_flu.json. Reads no network. The live page is built by the site build from this body."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from flu_headline import headline, cell, WORD, pc, f, ow
S = json.load(open('summary_flu.json')); e = html.escape
src = S['sources']; g = S['gates']; R = S['rows']; FR = S['frame']
def iv(c):
    if c['lo'] is None or c['weeks'] < FR['min_weeks']: return 'too few weeks'
    return '%s to %s' % (pc(c['lo']), pc(c['hi']))
def cov_row(label, c):
    return '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        e(label), f(c['scored']), f(c['inside']), pc(c['share']), iv(c), ow(c), pc(c['share_above']), pc(c['share_below']), f(c['cannot_tell']), f(c['nothing_returned']))
COVH = '<thead><tr><th>Cell</th><th>Scored</th><th>Inside</th><th>Inside, percent</th><th>95% interval, percent</th><th>Reading</th><th>Above, percent</th><th>Below, percent</th><th>Cannot tell</th><th>Not reported yet</th></tr></thead>'
def cov_table(names, level, side):
    return '<div class="tw"><table class="bench">%s<tbody>%s</tbody></table></div>' % (COVH, ''.join(cov_row(n.replace('season ', 'Season ').replace('horizon ', 'Horizon ').replace('all horizons', 'All horizons'), cell(S, n, level, side)) for n in names))
NAMES = ['all horizons', 'horizon 0', 'horizon 1', 'horizon 2', 'horizon 3']
SEAS = sorted({c['cell'] for c in S['cells'] if c['cell'].startswith('season ')})
def wis_rows():
    out = []
    for n in NAMES + SEAS:
        for side in ('final', 'first'):
            c = next(x for x in S['wis'] if x['cell'] == n and x['side'] == side)
            out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                e(n.replace('season ', 'Season ').replace('horizon ', 'Horizon ').replace('all horizons', 'All horizons')), 'latest' if side == 'final' else 'first reported', f(c['rows']),
                '' if c['ens_wis_mean'] is None else '%.1f' % c['ens_wis_mean'], '' if c['base_wis_mean'] is None else '%.1f' % c['base_wis_mean'], '' if c['ratio'] is None else '%.2f' % c['ratio'],
                'too few weeks' if c['lo'] is None or c['weeks'] < FR['min_weeks'] else '%.2f to %.2f' % (c['lo'], c['hi']), ow(c)))
    return ''.join(out)
def loc_rows():
    out = []
    for b in S['by_location']:
        c9 = next(x for x in b['cells'] if x['level'] == '95' and x['side'] == 'final'); c5 = next(x for x in b['cells'] if x['level'] == '50' and x['side'] == 'final')
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(b['name']), f(c9['scored']), pc(c9['share']), iv(c9), ow(c9), pc(c5['share']), iv(c5), ow(c5)))
    return ''.join(out)
def loc_count(level, o): return sum(1 for b in S['by_location'] for x in b['cells'] if x['level'] == level and x['side'] == 'final' and x['outcome'] == o)
AD = S['after_data']; SB = {(x['block_weeks'], x['level']): x for x in AD['block_sensitivity']}
a95 = cell(S, 'all horizons', '95'); a95f = cell(S, 'all horizons', '95', 'first'); rv = S['described']['revisions']
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
off = S['described']['offset_by_horizon']
body = hl + '''<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>
<h2>When the CDC flu forecast states an interval, how often does the reported count land inside it?</h2>
<p>The CDC FluSight Forecast Hub collects forecasts of the weekly number of laboratory-confirmed flu hospital admissions for the United States, each state, Washington DC and Puerto Rico. Each week it publishes the FluSight ensemble, which its metadata describes as &ldquo;a median of quantile outputs&rdquo; of the eligible forecasts. CDC&rsquo;s forecast page shows &ldquo;prediction intervals, which indicate the bounds of uncertainty&rdquo; and says these ensemble forecasts &ldquo;have been among the most accurate for previous influenza forecasting efforts.&rdquo;</p>
<p>The ensemble is published as quantiles. The quantiles at 2.5 and 97.5 percent state a 95 percent interval, and the quantiles at 25 and 75 percent state a 50 percent interval. This page sets each interval beside the count that was later reported for that place and week, for forecasts of the current week and up to three weeks ahead, from %s to %s. Below, the outer interval is the stated 95 percent interval and the middle interval is the stated 50 percent interval. It reads the count two ways. The latest count is the one in the newest release and is the primary reading. For the newest weeks it is also the only release. The first reported count is the one in the earliest release the hub keeps, used when that release came out within 14 days of the week&rsquo;s end. The hub keeps no releases for some summer months, the longest gap being %d days. This page does not say why a count lands outside. The plan, with the rules and the known-good checks, was fixed before any interval was set beside a reported count. %s</p>
<h2>By horizon, against the latest count</h2>
<h3>Outer interval</h3>%s
<h3>Middle interval</h3>%s
<p class="bench-note">One row is one forecast: a place, a week and a horizon. The places are the United States as a whole, the 50 states, Washington DC and Puerto Rico. Inside means the reported count is at or between the two stated quantiles. Above and below are printed apart, and a well-calibrated interval leaves about the same share on each side. Cannot tell is never folded into either side. Rows are not independent. Every place in a week shares one flu season, and forecasts made at different horizons share target weeks. So the interval is a moving-block bootstrap over target weeks, in blocks of 4 consecutive weeks, 2,000 draws, and it is much wider than an interval that treats rows as independent. Reading: below if the whole interval is under the stated level, above if it is over it, otherwise cannot tell (STRADDLES_EDGE) because the interval holds the stated level. The plan named no tolerance around the stated level, so no cell reads consistent (plan addendum of 12 November 2026, Faults and Guards 2.0). A cell needs 30 scored rows and 8 target weeks, and with fewer it reads cannot tell (TOO_WIDE_TO_RESOLVE). The block length was fixed in the plan. Tried after the data, longer blocks widen the all-horizons interval for the outer interval to %s to %s percent with blocks of 8 weeks and %s to %s percent with blocks of 13 weeks, which read %s and %s.</p>
<h2>By horizon, against the first reported count</h2>
<h3>Outer interval</h3>%s
<h3>Middle interval</h3>%s
<p class="bench-note">Of %s rows with both counts, the first reported and latest counts differ in %s, by a median of %s admissions where they differ. A row whose earliest release came more than 14 days after the week reads cannot tell on this side. In the all-horizons cell that is %s rows.</p>
<h2>By season</h2>
<h3>Outer interval, latest count</h3>%s
<h3>Middle interval, latest count</h3>%s
<h2>Against the hub&rsquo;s baseline model</h2>
<p>The weighted interval score is a common score for quantile forecasts. It is the distance from the reported count to the median plus a penalty for each interval&rsquo;s width and for counts outside it, and lower is closer. The hub runs a baseline model on the same weeks. Below is the ensemble&rsquo;s total score over the baseline&rsquo;s on the rows where both stated all 23 quantiles. The hub states no number for this ratio. Comparing it with 1 is our ruler. Below means the ensemble scored lower than the baseline. The ratio adds raw scores, so places with more admissions weigh more. The United States row carries %s percent of the ensemble&rsquo;s total score. Without it the ratio is %.2f (%.2f to %.2f), and in %d of %d places the ratio is under 1. The hub&rsquo;s own season rankings use a relative score on log-transformed counts, which this page does not reproduce.</p>
<div class="tw"><table class="bench"><thead><tr><th>Cell</th><th>Count</th><th>Rows</th><th>Ensemble mean score</th><th>Baseline mean score</th><th>Ratio</th><th>95%% interval</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">The interval is the same block bootstrap. Reading: below if the whole interval is under 1, above if over 1, otherwise cannot tell (STRADDLES_EDGE). The plan named no tolerance around 1, so no cell reads consistent.</p>
<h2>By place, all horizons, latest count</h2>
<p>For the stated 95 percent interval, %d places read below, %d above and %d cannot tell. For the stated 50 percent interval, %d read below, %d above and %d cannot tell. A single place has fewer weeks, so its interval is wide.</p>
<div class="tw"><table class="bench"><thead><tr><th>Place</th><th>Scored</th><th>Inside 95, percent</th><th>95%% interval</th><th>Reading</th><th>Inside 50, percent</th><th>95%% interval</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<h2>What this page holds and what it leaves out</h2>
<p>Every ensemble file in the hub is read, every place in it and horizons 0 to 3. The week before the reference date (horizon -1) is not scored. Its count can be released before the forecast is due. That leaves out %s rows. Described and not scored: the median distance from the stated median to the latest count, as a share of the 95 percent interval&rsquo;s width, is %s at horizon 0 and %s at horizon 3, where a positive value means the count came in higher. Set aside: rate-change categories, peak week and peak size, emergency department visit shares, sample trajectories, individual team models and seasons before 2023-24.</p>
<p class="meta">The hub states that the 2.5 and 97.5 quantiles &ldquo;correspond to the central 95%% Prediction Interval&rdquo;. Forecasts: FluSight-ensemble by the CDC FluSight team and the University of Massachusetts Amherst, licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, and FluSight-baseline, read from the hub and not altered. Our scores and readings are ours.</p>
<p class="meta">Sources: CDC FluSight Forecast Hub (MIT licence), FluSight-ensemble and FluSight-baseline forecasts, and the hub&rsquo;s NHSN target data with every release kept (%d releases, newest %s). Read with git, hub commit %s. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about every six hours, and the newest run is always in <a href="/flu/live.json">/flu/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/flu">flu</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://github.com/cdcepi/FluSight-forecast-hub">CDC FluSight Forecast Hub</a> &middot; <a href="https://www.cdc.gov/flu-forecasting/data-vis/current-week.html">CDC flu forecasts</a> &middot; <a href="https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data">NHSN Weekly Hospital Respiratory Data</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=flu-all">Respond</a></p>
<section id="replies" data-prefix="flu"></section><script src="/replies.js" defer></script>''' % (
    src['first_reference_date'], src['last_reference_date'], AD['longest_release_gap_days'], gate_line,
    cov_table(NAMES, '95', 'final'), cov_table(NAMES, '50', 'final'), pc(SB[(8, '95')]['lo']), pc(SB[(8, '95')]['hi']), pc(SB[(13, '95')]['lo']), pc(SB[(13, '95')]['hi']), ow(SB[(8, '95')]), ow(SB[(13, '95')]),
    cov_table(NAMES, '95', 'first'), cov_table(NAMES, '50', 'first'),
    f(rv['rows']), f(rv['differ']), '' if rv['median_abs_change_where_differ'] is None else '%g' % rv['median_abs_change_where_differ'], f(a95f['cannot_tell']),
    cov_table(SEAS, '95', 'final'), cov_table(SEAS, '50', 'final'), pc(AD['wis_without_us']['us_share_of_ensemble_total']), AD['wis_without_us']['ratio'], AD['wis_without_us']['lo'], AD['wis_without_us']['hi'], AD['wis_places_under_1'], len(AD['wis_by_location']), wis_rows(),
    loc_count('95', 'BELOW'), loc_count('95', 'ABOVE'), loc_count('95', 'CANNOT_TELL'), loc_count('50', 'BELOW'), loc_count('50', 'ABOVE'), loc_count('50', 'CANNOT_TELL'), loc_rows(),
    f(src['horizon_minus1_rows_not_scored']), '%.2f' % off[0]['median_offset_over_width95'], '%.2f' % off[-1]['median_offset_over_width95'],
    src['releases'], src['latest_release'], e(src['hub_commit'][:7]), e(S['generated'][:10]))
TITLE = 'FLU | Stated Flu Forecast Intervals Against Reported Admissions | Heuremen LLC'
DESC = 'FLU: the CDC FluSight ensemble stated 50 and 95 percent intervals for weekly flu hospital admissions, set beside the counts later reported, by horizon, season and place, with block bootstrap intervals.'
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/flu">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">FLU</b> &middot; Stated Flu Forecast Intervals Against Reported Admissions</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('flu.html', 'w').write(page); print('flu.html', len(page))
