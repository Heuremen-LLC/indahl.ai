#!/usr/bin/env python3
"""build_page.py: writes seasonal.html, the desk's page draft, from summary_seasonal.json. Reads no network. The live page is built by the site build from this body."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from seasonal_headline import headline, cell, WORD, pc, f
S = json.load(open('summary_seasonal.json')); e = html.escape
src = S['sources']; g = S['gates']; FR = S['frame']
def iv(c): return 'too few seasons' if c['lo'] is None or c['seasons'] < FR['min_seasons'] or c['rows'] < FR['min_rows'] else '%s to %s' % (pc(c['lo']), pc(c['hi']))
def rel_table(var):
    rows = []
    for c in S['cells']:
        if c['variable'] != var or c['cell'].endswith('leaning') or not c['rows']: continue
        rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(c['category']), e(c['bin']), f(c['rows']), f(c['seasons']), pc(c['mean_stated']), pc(c['observed']), iv(c), WORD[c['outcome']]))
    return ('<div class="tw"><table class="bench"><thead><tr><th>Category</th><th>Stated chance, percent</th><th>Rows</th><th>Seasons</th><th>Mean stated, percent</th><th>Observed, percent</th>'
            '<th>95%% interval, percent</th><th>Reading</th></tr></thead><tbody>'.replace('%%', '%') + ''.join(rows) + '</tbody></table></div>')
lean = [c for c in S['cells'] if c['cell'].endswith('leaning')]
lean_rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
    e(c['cell'].split(',')[0].capitalize()), f(c['rows']), f(c['seasons']), pc(c['mean_stated']), pc(c['observed']), iv(c), WORD[c['outcome']]) for c in lean)
VN = {'temp': 'Temperature', 'prec': 'Precipitation'}
hss_rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%+.3f</td><td>%+.3f to %+.3f</td><td>%s</td><td>%.3f</td><td>%s</td></tr>' % (
    VN[h['variable']], e(h['score']), f(h['seasons']), h['mean_difference'], h['lo'], h['hi'], f(h['within_1_point']), h['median_abs_difference'], WORD[h['outcome']]) for h in S['heidke'])
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
AD = S['after_data']; OS = AD['observed_shares']; LS = AD['leaning_split']['temp']
nprec = next(h for h in S['heidke'] if h['variable'] == 'prec')['seasons']
body = hl + '''<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>
<h2>When the seasonal outlook states a chance, how often does it happen?</h2>
<p>Each month the NOAA Climate Prediction Center issues 3-month outlooks for temperature and precipitation over the United States. For each place the outlook states the chance that the season lands in the upper third of the climate record (above normal), the middle third (near normal) or the lower third (below normal). Where no category is favoured it states equal chances, 33.33 percent each. CPC keeps an archive of these outlooks, issued half a month ahead, on a 2 by 2 degree grid over the contiguous United States, beside the category that was observed in each cell and season. This page reads that archive from the %s season to the %s season.</p>
<p>If a stated chance holds, a category stated at 40 percent should be observed in about 40 percent of such cells. This page groups stated chances into bins and counts how often the category happened. It also recomputes the Heidke skill score CPC publishes for every season, from the same archive and with CPC&rsquo;s stated formula, and sets ours beside CPC&rsquo;s. This page does not say why a category happens more or less often than stated. The plan, with the bins, the rules and the known-good checks, was fixed before any stated chance was set beside an observed category. %s</p>
<h2>When the outlook leans</h2>
<p>Every row in which any category was stated at 40 percent or more.</p>
<div class="tw"><table class="bench"><thead><tr><th>Variable</th><th>Rows</th><th>Seasons</th><th>Mean stated, percent</th><th>Observed, percent</th><th>95%% interval, percent</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">One row is one season, one grid cell and one category, with the chance stated for that category. Rows are not independent. Every cell in a season shares one weather pattern, and neighbouring 3-month seasons share two of their months. So the interval is a moving-block bootstrap over seasons, in blocks of 12 consecutive seasons, 2,000 draws, and it is much wider than one that treats cells as independent. Reading: above if the whole interval is over the mean stated chance (the category happened more often than stated), below if it is under, consistent if the mean stated chance is inside an interval no wider than 10 points, otherwise cannot tell. A cell needs 30 rows and 24 seasons.</p>
<h2>Temperature by stated chance</h2>
%s
<h2>Precipitation by stated chance</h2>
%s
<p class="bench-note">Near normal is 100 minus the stated chances of above and below. The bin from 31 to 35 percent holds the equal-chances rows. The observed categories come from CPC&rsquo;s own verification files. CPC&rsquo;s verification tutorial says &ldquo;The observation categories are determined by using the climatology data from 1981-2010 as the reference period.&rdquo; Over all cells and seasons the observed temperature category was above normal %s percent of the time, near %s percent and below %s percent. For precipitation it was %s, %s and %s percent. Cells are not weighted by area. Described and not scored: in the temperature leaning cell, %s rows stated above normal at a mean of %s percent and above normal was observed in %s percent, and %s rows stated below normal at a mean of %s percent and below normal was observed in %s percent.</p>
<h2>Our recompute of CPC&rsquo;s skill score</h2>
<p>CPC defines its score as &ldquo;HSS (%%) = 100 * (H - E) / (T - E) where H = Number of correct forecasts, E = Expected number of correct forecasts (1/3 of total), and T = Total number of valid forecast-observation pairs&rdquo;, and the score with equal chances as &ldquo;HSS withEC (%%) = HSS * coverage&rdquo;. We used CPC&rsquo;s categorical outlook file, counted only cells with a favoured category for the first score, left out the few cells whose category in that file is not a whole number, did not weight cells by area, and set the result beside the score CPC states for the same season. The difference is ours minus CPC&rsquo;s, in points.</p>
<div class="tw"><table class="bench"><thead><tr><th>Variable</th><th>Score</th><th>Seasons</th><th>Mean difference</th><th>95%% interval</th><th>Within 1 point</th><th>Median absolute difference</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Reading: consistent if the interval of the mean difference lies inside minus 2 to plus 2 points, above or below if it lies wholly beyond that, otherwise cannot tell. For precipitation the first score covers %s of %s seasons. In the other %s every cell was equal chances. CPC lists no first score for them and an all score of 0, and ours is the same. The largest gap is %s points, in %s for precipitation, where %s cells with a category that is not a whole number were left out. This check shows that our reading of the archive pairs each outlook with the right season. It does not test the chances themselves.</p>
<h2>What this page holds and what it leaves out</h2>
<p>Every season in the archive with an observed category is read, and every grid cell with an observed category, %s cells. Outlooks still waiting for their season: %s for temperature and %s for precipitation. Set aside: longer leads (kept only as map contours from 2007), monthly outlooks, Alaska and Hawaii, and climate divisions, for which no archive of past outlooks with observed categories was found.</p>
<p class="meta">Sources: NOAA Climate Prediction Center 3-month outlook verification files and stated Heidke scores, read without a key. NOAA/NWS information is in the public domain. Our counts and readings are ours and are not NWS material. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about once a day, and the newest run is always in <a href="/seasonal/live.json">/seasonal/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/seasonal">seasonal</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://www.cpc.ncep.noaa.gov/products/predictions/long_range/seasonal.php">CPC 3-month outlooks</a> &middot; <a href="https://www.cpc.ncep.noaa.gov/products/predictions/long_range/tools/briefing/seas_veri.grid.php">CPC seasonal verification</a> &middot; <a href="https://www.cpc.ncep.noaa.gov/products/verification/summary/index.php?page=tutorial">CPC verification tutorial</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=seasonal-all">Respond</a></p>
<section id="replies" data-prefix="seasonal"></section><script src="/replies.js" defer></script>''' % (
    src['first_season'], src['last_season'], gate_line, lean_rows, rel_table('temp'), rel_table('prec'), pc(OS['temp']['above']), pc(OS['temp']['near']), pc(OS['temp']['below']), pc(OS['prec']['above']), pc(OS['prec']['near']), pc(OS['prec']['below']),
    f(LS['above']['rows']), pc(LS['above']['mean_stated']), pc(LS['above']['observed']), f(LS['below']['rows']), pc(LS['below']['mean_stated']), pc(LS['below']['observed']), hss_rows, f(nprec), f(src['seasons_scored']), AD['cpc_all_ec_seasons_prec'], '%.2f' % AD['largest_heidke_gap']['prec']['difference'], AD['largest_heidke_gap']['prec']['season'], AD['largest_heidke_gap']['prec']['cells_left_out'],
    f(src['land_cells']), src['forecasts_waiting']['temp'], src['forecasts_waiting']['prec'], e(S['generated'][:10]))
TITLE = 'SEASONAL | Stated Seasonal Outlook Chances Against What Was Observed | Heuremen LLC'
DESC = 'SEASONAL: the chances the NOAA Climate Prediction Center stated for above, near and below normal seasons, set beside the observed category on its own grid, with block bootstrap intervals, and our recompute of its skill score.'
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/seasonal">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">SEASONAL</b> &middot; Stated Seasonal Outlook Chances Against What Was Observed</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('seasonal.html', 'w').write(page); print('seasonal.html', len(page))
