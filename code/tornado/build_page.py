#!/usr/bin/env python3
"""build_page.py: writes tornado.html, the desk's page draft, from summary_tornado.json. Reads no network. The live page is built by the site build, which
takes the body from this file."""
import json, os, sys, html, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from tornado_headline import headline
S = json.load(open('summary_tornado.json'))
e = html.escape
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', None: ''}
def pc(x, d=1):
    if x is None: return ''
    if d == 2 and 0 < x < 0.001: d = 3   # small shares keep three decimals so the interval shows
    return ('%.' + str(d) + 'f') % (100 * x)
def num(x): return '{:,}'.format(int(x))
def day(d): return time.strftime('%d %B %Y', time.strptime(d, '%Y%m%d')).lstrip('0') if d else ''
def cell(name, pre=False): return next(c for c in S['cells'] if c['cell'] == name and c['preliminary'] == pre)
F = S['frame']; y0, y1 = F['closed_years']; G = S['gates']; SR = S['sources']; NR = S['nothing_returned']; W = S['warnings']
def band_table(c):
    out = []
    for b in c['bands']:
        lo_s = '%s to %s' % (pc(b['lo_stated'], 0), pc(b['hi_stated'], 0)) if b['band'] != 'under 2' else 'under 2'
        if b['band'] == '60 and over': lo_s = '60 and over'
        lev = '' if b['band'] == 'under 2' else pc(b['lo_stated'], 0)
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(lo_s), num(b['rows']), num(b['days']), num(b['events']), pc(b['freq'], 2), ('%s to %s' % (pc(b['lo'], 2), pc(b['hi'], 2))) if b['lo'] is not None else '', WORD[b['outcome']],
            lev, WORD[b.get('label_reading')]))
    return ('<div class="tw"><table class="bench"><thead><tr><th>Stated chance, percent</th><th>Point-days</th><th>Days</th><th>With a tornado within 25 miles</th><th>Observed, percent</th>'
            '<th>95% interval, percent</th><th>Reading against the band</th><th>Contour drawn, percent</th><th>Against the contour value</th></tr></thead><tbody>' + ''.join(out) + '</tbody></table></div>')
def extra_table(cs):
    out = []
    for c in cs:
        h = c['hatched']; br = c['brier']
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(c['cell']), num(h['rows']), num(h['days']), pc(h['freq'], 2), ('%s to %s' % (pc(h['lo'], 2), pc(h['hi'], 2))) if h['lo'] is not None else '', WORD[h['outcome']],
            '' if br['bss'] is None else '%.3f' % br['bss'], ('%.3f to %.3f' % (br['lo'], br['hi'])) if br['lo'] is not None else '', WORD[br['outcome']]))
    return ('<div class="tw"><table class="bench"><thead><tr><th>Cell</th><th>Hatched point-days</th><th>Days</th><th>EF2 or stronger within 25 miles, percent</th><th>95% interval, percent</th>'
            '<th>Reading against 10 percent or more</th><th>Brier skill score against climatology</th><th>95% interval</th><th>Reading against zero</th></tr></thead><tbody>' + ''.join(out) + '</tbody></table></div>')
def year_table():
    out = []
    for c in S['years']:
        b = next(x for x in c['bands'] if x['band'] == '10 to 15'); bo = c['band_outcomes']; br = c['brier']
        out.append('<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td></tr>' % (
            c['year'], num(c['days']), num(b['rows']), pc(b['freq'], 1), WORD[b['outcome']], bo['CONSISTENT'], bo['ABOVE'], bo['BELOW'], bo['CANNOT_TELL'],
            '' if br['bss'] is None else '%.3f' % br['bss'], ('%.3f to %.3f' % (br['lo'], br['hi'])) if br['lo'] is not None else ''))
    return ('<div class="tw"><table class="bench"><thead><tr><th>Year</th><th>Days</th><th>Point-days at 10 to 15</th><th>Observed at 10 to 15, percent</th><th>Reading at 10 to 15</th>'
            '<th>Bands consistent</th><th>Above</th><th>Below</th><th>Cannot tell</th><th>Brier skill score</th><th>95% interval</th></tr></thead><tbody>' + ''.join(out) + '</tbody></table></div>')
def warn_rows(ws):
    out = []
    for w in ws:
        out.append('<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td></tr>' % (
            e(w['label']), ' (preliminary)' if w['preliminary'] else '', num(w['tornadoes']), num(w['warnings']),
            pc(w['pod']['value']), pc(w['pod']['lo']), pc(w['pod']['hi']), WORD[w['pod']['outcome']],
            '' if w['lead_min']['value'] is None else '%.1f' % w['lead_min']['value'], '' if w['lead_min']['lo'] is None else '%.1f' % w['lead_min']['lo'], '' if w['lead_min']['hi'] is None else '%.1f' % w['lead_min']['hi'], WORD[w['lead_min']['outcome']],
            pc(w['far']['value']), pc(w['far']['lo']), pc(w['far']['hi']), WORD[w['far']['outcome']],
            '' if w['initial_lead_min']['value'] is None else '%.1f' % w['initial_lead_min']['value']))
    return ''.join(out)
us, ks, al = cell('United States'), cell('Kansas'), cell('Tornado Alley')
UB = SR['database_unrated_by_year']; RB = SR['database_rows_by_year']
UNR = ', '.join('%s percent in %s' % (round(100 * UB[y] / RB[y]), y) for y in ('2021', '2022', '2023', '2024', '2025') if RB.get(y))
YB = next(b for b in us['bands'] if b['band'] == '10 to 15')['year_blocks']
pus, pks, pal = cell('United States', True), cell('Kansas', True), cell('Tornado Alley', True)
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
gate_line = 'All known-good checks passed on this run.' if G['passed'] else 'A known-good check did not pass on this run, so every reading shows cannot tell.'
wp = W['pooled']; WF = W['polygon_end_floor']
nr_days = NR['no_outlook_days']
body = hl + '''<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>
<h2>When the Storm Prediction Center draws a tornado chance, how often does a tornado come?</h2>
<p>Every morning the NOAA Storm Prediction Center issues a Day 1 Convective Outlook. It draws tornado probability contours at 2, 5, 10, 15, 30, 45 and 60 percent. Its product page says the probabilities &ldquo;represent the probability of one or more events occurring&rdquo; &ldquo;within 25 miles of a point during the outlook period.&rdquo; The Center's verification paper by Kay and Brooks describes the hatched area as a &ldquo;10%% or greater chance of 1 or more F2 or stronger tornadoes&rdquo;, now rated EF2 or stronger.</p>
<p>This page scores the 1300 UTC Day 1 outlook, valid until 1200 UTC the next day. It uses the 80 km grid spacing and the outlook valid period of the Center's verification paper, which scored the 1300 and 2000 UTC outlooks and binned reports into grid boxes rather than measuring distance to a point. Points 80 km apart cover the 48 contiguous states. None falls in the District of Columbia. Each point takes the highest contour around it, with no smoothing between contours. A point counts as hit when a tornado track in the SPC tornado database passes within 25 miles of it during the outlook period. A point inside the 10 percent contour and outside the 15 percent contour was given a chance from 10 up to 15 percent, and the observed share at those points should sit in that band. That band reading is the one the plan fixed. Read against the contour value alone, with the same interval, every United States contour with 30 or more days shows tornadoes more often than the value drawn, and the table shows that reading beside the band. It was added after the data at the outside referee and decides nothing.</p>
<p>Points on one day share the same storms, and nearby days share weather systems. The intervals come from a bootstrap that draws whole days, so points on the same day stay together. It does not cover the link between neighbouring days. Resampling whole years instead widens the United States 10 to 15 percent interval to %s to %s percent, and the reading stays %s. The plan, with the rules, the cells and the known-good checks, was fixed and committed before any outlook was set beside a tornado. %s</p>
<h2>The United States, closed years</h2>
<p>Outlooks from %s to %s against the SPC tornado database. %s days, %s grid points.</p>
%s
<p class="bench-note">Reading: above if the whole 95%% interval is above the band, below if the whole interval is under it, consistent if it lies inside the band, otherwise cannot tell. A band needs 30 days with points in it. A point-day is one grid point on one outlook day.</p>
<h2>Kansas</h2>
<p>Grid points inside Kansas, the same outlooks and the same rules. %s grid points.</p>
%s
<h2>Tornado Alley</h2>
<p>Tornado Alley has no official boundary. Here it means grid points inside Texas, Oklahoma, Kansas, Nebraska, South Dakota and Iowa, fixed in the plan before the data. %s grid points.</p>
%s
<h2>The hatched area and a second ruler</h2>
<p>The hatched area states a 10 percent or greater chance of a tornado rated EF2 or stronger within 25 miles. The Brier skill score compares the outlook with climatology, the share of days with a tornado within 25 miles of the same point in the same month in the other closed years. Above zero means the outlook scored better than climatology. The Center states no figure for this score, so it reads only above or below zero. In the closed years %s tornadoes in the database carry no rating, and they are not counted as EF2 or stronger. Unrated tornadoes are rare before 2016 and are %s. If every unrated tornado were EF2 or stronger, the hatched share would be at most %s percent in the United States, %s in Kansas and %s in Tornado Alley, so the Kansas and Tornado Alley readings depend on how unrated tornadoes are read.</p>
%s
<h2>Year by year</h2>
<p>The United States cell for each closed year. These rows are shown and are not in the headline.</p>
%s
<h2>This year, preliminary</h2>
<p>From 1 January %d the tornado database is not out yet. These cells use the Center's preliminary storm reports, which are points with a time and no rating, from %s to %s. They are preliminary and are never pooled with the closed years. %s preliminary days were read.</p>
<h3>United States, preliminary</h3>
%s
<h3>Kansas, preliminary</h3>
%s
<h3>Tornado Alley, preliminary</h3>
%s
%s
<h2>Do tornado warnings meet their stated goals?</h2>
<p>The National Weather Service reports three tornado warning measures each fiscal year under the Government Performance and Results Act. The Commerce Inspector General's report OIG-25-026-I (2025) gives the definitions and the goals it calls current: probability of detection, the mean share of each tornado's one-minute segments that fell inside a warning in force, at least 72 percent. Lead time, the mean over each tornado's segments of the time since the warning was issued, with an unwarned segment counted as zero, at least 13 minutes. False alarm ratio, the share of warnings that no tornado verified, at most 71 percent. The same report says the public description of lead time differs from the one computed. The computed one is used here. The lead time of the first segment is shown beside it and decides nothing.</p>
<p>Warnings are the storm-based tornado warning polygons as issued, from the Iowa Environmental Mesonet archive. Tornadoes are the tracks in the SPC tornado database, cut into one-minute segments along a straight line from start to end. Each fiscal year is read against the current goals. The goals printed for earlier years in each budget were not read. The intervals come from the same day bootstrap. Each issuance polygon is held until the warning expires. The archive also gives the time a polygon was replaced by a later statement, and the replacement polygons are not in the file read. Counting the issuance polygon only until it was replaced gives a floor: detection %s percent, lead %s minutes and false alarms %s percent over the closed years. Detection and lead read below at both ends. The false alarm reading is the most open of the three. When several warnings cover a segment, its lead is taken from the earliest issued.</p>
<div class="tw"><table class="bench"><thead><tr><th>Fiscal year</th><th>Tornadoes</th><th>Warnings</th><th>Detection, percent</th><th>95%% interval</th><th>Reading against 72</th><th>Lead, minutes</th><th>95%% interval</th><th>Reading against 13</th><th>False alarms, percent</th><th>95%% interval</th><th>Reading against 71</th><th>First-segment lead, minutes</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Reading for detection and lead time: consistent if the whole interval is at or above the goal, below if the whole interval is under it, otherwise cannot tell. For false alarms: consistent if the whole interval is at or under 71 percent, above if the whole interval is over it, otherwise cannot tell. The first row pools the closed fiscal years. Every warning and every tornado in the files is used, in any state or territory, with no match by forecast office. Fiscal years from FY%d on use the preliminary reports for 2026 and are labelled preliminary. A preliminary report is one point at one time, so it counts as a tornado of one minute.</p>
<h2>Nothing returned</h2>
<p>Counted apart and never folded into a reading. Days in the frame with no outlook of the 1300 UTC cycle as the archive labels it: %s. On %s of them the archive holds a product issued for 1300 UTC under another cycle label (%s), which the plan does not score. On %s scored days the 1300 UTC cycle product was issued after 1300 UTC and is scored from 1300 UTC. Outlook days whose tornado layer could not be read: %s. Preliminary days whose file could not be fetched: %s. Fiscal years whose warning file could not be fetched: %s. Contour values outside the stated set: %s%s. Database rows with no start position or time: %s. Tornadoes that started between 1200 and 1300 UTC, the hour no 1300 UTC outlook covers: %s.</p>
<h2>What this page holds and what it leaves out</h2>
<p>Left out: the other Day 1 issuances, the Day 2 and Day 3 outlooks, the hail, wind and categorical outlooks, tornado watches, outlooks before 2007, and Alaska, Hawaii and Puerto Rico in the outlook grid. A reading says how often tornadoes came where a band was drawn. It does not say why.</p>
<p class="meta">Sources: NOAA Storm Prediction Center Day 1 Convective Outlooks as kept by the Iowa Environmental Mesonet, Iowa State University. SPC tornado database 1950 to %d. SPC preliminary storm reports. NWS storm-based tornado warnings as kept by the Iowa Environmental Mesonet. US Census state boundaries. All read without a key, one request at a time. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about once a day. The newest run is always in <a href="/tornado/live.json">/tornado/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/tornado">tornado</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://www.spc.noaa.gov/products/outlook/archive/">SPC outlook archive</a> &middot; <a href="https://mesonet.agron.iastate.edu/request/gis/outlooks.phtml">Iowa Environmental Mesonet outlook archive</a> &middot; <a href="https://www.spc.noaa.gov/wcm/">SPC tornado database</a> &middot; <a href="https://www.spc.noaa.gov/climo/reports/">SPC storm reports</a> &middot; <a href="https://mesonet.agron.iastate.edu/vtec/">Iowa Environmental Mesonet warning archive</a> &middot; <a href="https://spc.noaa.gov/publications/mkay/probver">Kay and Brooks, SPC verification</a> &middot; <a href="https://www.oig.doc.gov/wp-content/OIGPublications/OIG-25-026-I_FinalReport-SECURED.pdf">OIG-25-026-I</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=tornado-all">Respond</a></p>
<section id="replies" data-prefix="tornado"></section><script src="/replies.js" defer></script>''' % (
    pc(YB['lo'], 1), pc(YB['hi'], 1), WORD[YB['outcome']], gate_line, day(us['first_day']), day(us['last_day']), num(us['days']), num(us['points']), band_table(us),
    num(ks['points']), band_table(ks), num(al['points']), band_table(al),
    num(SR['database_unrated_closed']), UNR, pc(us['hatched']['unrated_as_ef2_upper']), pc(ks['hatched']['unrated_as_ef2_upper']), pc(al['hatched']['unrated_as_ef2_upper']), extra_table([us, ks, al]), year_table(),
    y1 + 1, day(pus['first_day']), day(pus['last_day']), num(SR['preliminary_days']), band_table(pus), band_table(pks), band_table(pal),
    '<p>The hatched area and the Brier score for the preliminary cells:</p>' + extra_table([pus, pks, pal]) + '<p class="bench-note">The preliminary reports read for this page carry no rating, so the hatched area cannot be read for this year until the database is out.</p>',
    pc(WF['pod']['value']), '%.1f' % WF['lead_min']['value'], pc(WF['far']['value']), warn_rows([wp] + W['years']), F['fiscal_years_closed'][1] + 1,
    num(nr_days), num(len(NR['no_outlook_other_cycle_1300'])), ', '.join(day(d) for d in NR['no_outlook_other_cycle_1300']), num(len(NR['late_cycle13_scored'])), num(len(NR['outlook_unreadable'])), num(len(NR['prelim_missing'])), num(len(NR['warnings_missing_fy'])), num(sum(SR['threshold_outside_set'].values())), (' (%s, the conditional intensity groups that replaced the hatched SIGN area in March 2026 under NWS notice SCN 26-11, so the 2026 hatched area is not read)' % ' and '.join(sorted(SR['threshold_outside_set']))) if SR['threshold_outside_set'] and all(k.startswith('CIG') for k in SR['threshold_outside_set']) else '',
    num(SR['database_counts'].get('no start position or time', 0)), num(SR['tornado_placement'].get('start between 1200 and 1300 UTC, in no outlook day', 0)),
    y1, e(S['generated'][:10]))
TITLE = 'TORNADO | Stated Tornado Chances Against the Tornadoes That Came | Heuremen LLC'
DESC = 'TORNADO: the Storm Prediction Center Day 1 tornado probabilities and the National Weather Service tornado warning goals, set beside the tornadoes in the SPC tornado database, with Kansas and Tornado Alley apart.'
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/tornado">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">TORNADO</b> &middot; Stated Tornado Chances Against the Tornadoes That Came</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('tornado.html', 'w').write(page); print('tornado.html', len(page))
