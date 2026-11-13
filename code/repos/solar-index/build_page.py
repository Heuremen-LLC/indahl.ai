#!/usr/bin/env python3
"""build_page.py: writes solar.html, the desk's page draft, from summary_solar.json. Reads no network. The live page is built by the site build from this file."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from solar_headline import headline, WORD, SKILL, pc
S = json.load(open('summary_solar.json'))
e = html.escape
MINN = S['frame']['min_n']; src = S['sources']; g = S['gates']
TITLE = 'SOLAR | Stated Space Weather Chances Against What Happened | Heuremen LLC'
DESC = 'SOLAR: the chances of solar flares and geomagnetic storms that NOAA SWPC states each day, as first published, set beside what happened, bin by bin, with a Brier score against the base rate.'
NAMES = {c['event']: c['name'] for c in S['cells']}
def cell(ev, L): return next(c for c in S['cells'] if c['event'] == ev and c['lead'] == L)
def f2(x): return '' if x is None else '%.2f' % x
def f3(x): return '' if x is None else '%.3f' % x
def summary_rows():
    out = []
    for c in S['cells']:
        bs = [b for b in c['bins'] if b['n'] >= MINN]; cnt = lambda o: sum(b['outcome'] == o for b in bs)
        k = c['skill']; held = c.get('held')
        if held:
            out.append('<tr><td>%s</td><td>%d</td><td>%s</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td>held</td></tr>' % (e(c['name']), c['lead'], '{:,}'.format(c['scored']))); continue
        out.append('<tr><td>%s</td><td>%d</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td></tr>' % (
            e(c['name']), c['lead'], '{:,}'.format(c['scored']), k['events'] or 0, len(bs), cnt('CONSISTENT'), cnt('ABOVE'), cnt('BELOW'), pc(k['base_rate']), f3(k['brier']), f3(k['bss']), f3(k['lo']), f3(k['hi']),
            'held' if held else WORD[k['outcome']]))
    return ''.join(out)
def bin_table(bins):
    rows = []
    for b in bins:
        if not b['n']: continue
        rows.append('<tr><td>%s</td><td>%d</td><td>%s</td><td>%d</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td></tr>' % (
            e(b['bin']), b['n'], pc(b['mean_stated']), b['events'], pc(b['observed']), pc(b['lo']), pc(b['hi']),
            '' if b.get('boot_lo') is None else '%s to %s' % (pc(b['boot_lo']), pc(b['boot_hi'])), WORD[b['outcome']]))
    return ('<div class="tw"><table class="bench"><thead><tr><th>Stated chance, percent</th><th>Days</th><th>Mean stated, percent</th><th>Days with the event</th>'
            '<th>Happened, percent</th><th>95%% Wilson interval, percent</th><th>Block bootstrap interval, percent</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows))
def ns_line(c):
    n = c['not_scored']; parts = []
    for key, txt in (('no RSGA on file', 'no report on file'), ('issued late', 'issued after the day began'), ('dates do not match the issue day', 'dates in the report that do not follow its own day'),
                     ('section did not parse', 'a section that did not parse'), ('no events file', 'no events list for the day'), ('no K for the day', 'a missing K value'),
                     ('after the proton list last changed', 'no proton list yet for the day'), ('not yet settled', 'not yet settled')):
        if n.get(key): parts.append(('%d %s' if key in ('issued late', 'not yet settled') else '%d with %s') % (n[key], txt))
    return ', '.join(parts)
m1 = cell('M', 1)
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
DEFN = {'M': 'Stated as Class M. The event is a day with at least one flare of M1.0 or more at its peak.',
        'X': 'Stated as Class X. The event is a day with at least one flare of X1.0 or more at its peak.',
        'MID5': 'Stated as the minor storm chance plus the major or severe storm chance at middle latitudes, and adding them is our reading. The event is a day whose greatest Fredericksburg K is 5 or more.',
        'MID6': 'Stated as the major or severe storm chance at middle latitudes. The event is a day whose greatest Fredericksburg K is 6 or more.',
        'HI5': 'Stated as the minor storm chance plus the major or severe storm chance at high latitudes, and adding them is our reading. The event is a day whose greatest College K is 5 or more.',
        'HI6': 'Stated as the major or severe storm chance at high latitudes. The event is a day whose greatest College K is 6 or more.'}
D = S['described']
H3 = {'M': 'M-class flares', 'X': 'X-class flares', 'MID5': 'Middle latitude storms', 'MID6': 'Middle latitude major or severe storms', 'HI5': 'High latitude storms', 'HI6': 'High latitude major or severe storms'}
sections = []
for ev in ('M', 'X', 'MID5', 'MID6', 'HI5', 'HI6'):
    c = cell(ev, 1)
    extra = ''
    if ev in ('MID5', 'MID6'):
        key = 'SWPC estimated planetary K %s or more against the middle latitude %s, day one' % ('5' if ev == 'MID5' else '6', 'storm chance' if ev == 'MID5' else 'major-severe chance')
        d = D.get(key)
        if d:
            extra = ('<p class="bench-note">The report names no station for its geomagnetic chances. Its Part V names Fredericksburg for the A index, and Fredericksburg is our reading here. The same stated chances read against SWPC&rsquo;s estimated planetary K of %s- or more from the same daily data are in the table below. They sit close to what happened, so a below reading at Fredericksburg may say more about which index is meant than about the forecast. The planetary table is shown at the same size and decides nothing.</p>%s'
                     % ('5' if ev == 'MID5' else '6', bin_table(d['bins'])))
    sections.append('<h3>%s, the day after the forecast</h3><p class="bench-note">%s Not scored: %s.</p>%s%s' % (H3[ev], DEFN[ev], ns_line(c), bin_table(c['bins']), extra))
def drow(name, key):
    d = D.get(key)
    if not d: return ''
    bs = [b for b in d['bins'] if b['n'] >= MINN]; k = d['skill']
    return '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s to %s</td></tr>' % (
        e(name), '{:,}'.format(k['n']), sum(b['outcome'] == 'CONSISTENT' for b in bs), sum(b['outcome'] == 'ABOVE' for b in bs), sum(b['outcome'] == 'BELOW' for b in bs), f3(k['bss']), f3(k['lo']), f3(k['hi']))
desc_rows = (drow('M-class read as M only, flares from M1.0 to M9.9', 'M only, day one') +
             drow('SWPC estimated planetary K of 5- or more against the middle latitude storm chance', 'SWPC estimated planetary K 5 or more against the middle latitude storm chance, day one') +
             drow('SWPC estimated planetary K of 6- or more against the middle latitude major or severe chance', 'SWPC estimated planetary K 6 or more against the middle latitude major-severe chance, day one') +
             drow('Planetary Kp of 5- or more (GFZ) against the middle latitude storm chance', 'Planetary Kp 5 or more against the middle latitude storm chance, day one') +
             drow('Planetary Kp of 6- or more (GFZ) against the middle latitude major or severe chance', 'Planetary Kp 6 or more against the middle latitude major-severe chance, day one') +
             drow('Minor storm read literally, at least one Fredericksburg K equal to 5, against the minor storm chance alone', 'Literal minor storm, at least one Fredericksburg K equal to 5, day one'))
p1 = cell('P', 1)
first, last = m1['first_target'], m1['last_target']
body = hl + '''<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>
<h2>When SWPC states a chance of a solar flare or a geomagnetic storm, how often does it happen?</h2>
<p>Every day at 2200 UTC the NOAA Space Weather Prediction Center issues its Report and Forecast of Solar and Geophysical Activity. It states a chance for each of the next three days. The product description defines them. Class M and class X are a &ldquo;probability forecast of the occurrence of one or more class-M or class-X x-ray flares for each of the next 3 days&rdquo;. The geomagnetic chances are &ldquo;the probability of at least one 3-hour K index, at the indicated level&rdquo; at middle and high latitudes, with minor storm at K = 5 and major or severe storm at K of 6 or more. If a stated 30 percent holds, the event should come on about 30 percent of such days.</p>
<p>The stated chances are read from the reports as first published, kept in the SWPC Warehouse, and from copies this desk stores. A corrected or amended report is never used, and a forecast counts only if it was issued before its day began. What happened is read from SWPC&rsquo;s own records: the edited solar event lists for flares, and the daily geomagnetic data for the eight 3-hour K values a day at Fredericksburg and at College. The report does not name its middle and high latitude stations. Reading them as Fredericksburg and College, the stations SWPC lists under those headings, is our reading. An M-class day is a day with a flare of M1.0 or more at its peak, and reading Class M as M or greater is also ours.</p>
<p>The frame starts with forecasts issued on 1 January 2021, more than a year after SWPC moved its main X-ray input to GOES-16 and stopped scaling flare classes, so every day is on one flare scale. Scored days run from %s to %s. %s The plan, with the bins, events and rules, was fixed before any stated chance was set beside an outcome. One addendum was made after the first read and is marked where it applies.</p>
<h2>Every event and day ahead</h2>
<div class="tw"><table class="bench"><thead><tr><th>Event</th><th>Day ahead</th><th>Days scored</th><th>Days with the event</th><th>Bins with %d days or more</th><th>Consistent</th><th>Above</th><th>Below</th><th>Base rate, percent</th><th>Brier score</th><th>Brier skill</th><th>95%% block bootstrap interval</th><th>Skill reading</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">A bin is a range of stated chance. Above means the event came more often than the mean stated chance in the bin, and below means less often, each by more than the 95%% Wilson interval. Consistent means the mean stated chance is inside the interval. A bin with fewer than %d days reads cannot tell. The Brier score is the mean squared gap between the stated chance and what happened. The skill compares it with always stating the base rate of the same days. Above zero is better than the base rate, and the skill reads consistent if its whole interval is within 0.05 of zero.</p>
<p class="bench-note">The Wilson interval treats days as independent. They are not. Active regions and storms last for days, and the three days of one forecast share most of what the forecaster knew, so the Wilson interval can be too narrow. The effect is not the same everywhere. It is largest for M-class flares and high latitude storms, where the interval may be about one and a half times too narrow, and small for X-class flares and middle latitude storms. The skill interval is a moving block bootstrap over blocks of 27 days, one solar rotation, which keeps runs of days together. Each bin table also shows a block bootstrap interval beside the Wilson interval, as a description. The plan&rsquo;s reading uses the Wilson interval.</p>
<h2>Bin by bin, the day after the forecast</h2>
%s
<p class="bench-note">The tables for the second and third day are in the feed.</p>
<h2>Proton events are held</h2>
<p>The report also states a chance of a proton event, at least 10 pfu above 10 MeV. The plan scored it against the SWPC list of solar proton events. That list leaves out events SWPC&rsquo;s own daily reports record. The report of 23 March 2024 says protons above 10 MeV &ldquo;reached a peak level of 955 pfu&rdquo;, and the list has no event in March 2024. Scored against that list a stated chance would look too high, so the proton rows read cannot tell. Their figures stay in the data, marked as held, until a complete record is set in a later plan.</p>
<h2>Other readings, described and not scored</h2>
<div class="tw"><table class="bench"><thead><tr><th>Reading, the day after the forecast</th><th>Days</th><th>Consistent bins</th><th>Above</th><th>Below</th><th>Brier skill</th><th>95%% block bootstrap interval</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">These rows decide nothing. The report names no station or index for its geomagnetic chances. Against SWPC&rsquo;s estimated planetary K and against the planetary Kp from GFZ Potsdam the middle latitude storm chances sit closer to what happened than against Fredericksburg K. That does not say which index SWPC means. The most recent GFZ values are nowcast values and may be replaced by definitive ones.</p>
<h2>What this page holds and what it leaves out</h2>
<p>The delivered records are SWPC&rsquo;s preliminary records. SWPC says it does not encourage the use of preliminary data for research. The edited event lists are read once a day has been over for at least three days. A flare that begins before midnight and peaks after it counts on the day of its peak. SWPC&rsquo;s Daily Solar Data counts it on the day it began, and the two records agree on whether a day had an M-class or larger flare on JOINAGREE of JOINDAYS days. Days with no report, no event list or a missing K value are counted apart and are never read as days with or without an event. Reports refused as a correction or amendment, or that did not parse: %d.</p>
<p>Set aside: the 3-day forecast and the 3-day geomagnetic forecast, which SWPC keeps for 75 days only. This desk stores each new one so a later plan can score them. Also set aside: the polar cap absorption forecast, flux and Ap predictions, and forecasts before 2021. A bin that reads above or below says the stated chance and the share of days differ for this record and this method. This page does not say why.</p>
<p class="meta">Sources: NOAA SWPC Report and Forecast of Solar and Geophysical Activity, Edited Solar Events, Daily Geomagnetic Data and Daily Solar Data, read from the SWPC Warehouse and indices, public domain. GFZ Potsdam Kp, CC BY 4.0, Matzka et al. 2021, doi 10.1029/2020SW002641, data doi 10.5880/Kp.0001. Reports read: %s. Generated %s. Heuremen LLC.</p>
<p class="meta">The tables are from the run of %s, and the newest run is always in <a href="/solar/live.json">/solar/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/solar">solar</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://www.swpc.noaa.gov/">NOAA Space Weather Prediction Center</a> &middot; <a href="ftp://ftp.swpc.noaa.gov/pub/warehouse/">SWPC Warehouse</a> &middot; <a href="https://kp.gfz.de/">GFZ Potsdam Kp</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=solar-all">Respond</a></p>
<section id="replies" data-prefix="solar"></section><script src="/replies.js" defer></script>''' % (
    first, last, gate_line, MINN, summary_rows(), MINN, '\n'.join(sections), desc_rows, src['rsga_unparsed'], '{:,}'.format(src['rsga_issue_days']), e(S['generated'][:10]), e(S['generated'][:10]))
body = body.replace('JOINAGREE', '{:,}'.format(g['join_agree'])).replace('JOINDAYS', '{:,}'.format(g['join_days']))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/solar">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">SOLAR</b> &middot; Stated Space Weather Chances Against What Happened</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('solar.html', 'w').write(page); print('solar.html', len(page))
