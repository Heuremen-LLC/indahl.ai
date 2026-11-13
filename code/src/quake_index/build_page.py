#!/usr/bin/env python3
"""build_page.py: writes quake.html, the desk's page draft, from summary_quake.json. Reads no network. The live page is built by the site build from this file."""
import json, os, sys, html, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
S = json.load(open('summary_quake.json'))
e = html.escape
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def n(x): return '{:,}'.format(x)
def day(ms): return time.strftime('%Y-%m-%d', time.gmtime(ms / 1000))
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
R = S['rows']; src = S['sources']; g = S['gates']; D = S['described']
TITLE = 'QUAKE | Stated Aftershock Odds Against the Aftershocks That Followed | Heuremen LLC'
DESC = 'QUAKE: every archived USGS aftershock forecast, its stated probabilities and 95% ranges set beside the earthquakes the USGS catalog shows in the same zone and window.'
SEQN = {s['id']: s for s in S['sequences']}
def iv(a): return '' if not a else '%s to %s' % (pc(a[0]), pc(a[1]))
def cover_rows(cs):
    return ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        e(c['cell']), n(c['scored']), n(c['inside']), n(c['above']), n(c['below']), pc(c['share']), iv(c['wilson']), iv(c['boot']), rw(c), n(c['blocks']), n(c['range_zero_zero'])) for c in cs)
def rel_rows(cs):
    return ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        e(c['cell']), n(c['scored']), n(c['occurred']), pc(c['stated_mean']), pc(c['share']), iv(c['wilson']), iv(c['boot']), rw(c), n(c['blocks'])) for c in cs if c['scored'])
def miss_rows(ms):
    out = []
    for m in ms:
        s = SEQN.get(m['seq'], {})
        out.append('<tr><td><a href="https://earthquake.usgs.gov/earthquakes/eventpage/%s/oaf" rel="nofollow">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td></tr>' % (
            e(m['seq']), e(s.get('title') or m['seq']), day(m['issued']), e(m['window'].lower()), pc(m['p']), n(m['nmin']), n(m['nmax']), n(m['count']), WORD[m['outcome']]))
    return ''.join(out)
def reasons(d, names):
    return ', '.join('%s %s' % (n(d[k]), t) for k, t in names if d.get(k))
from quake_headline import headline, rw
NZ = D['cover_without_zero_ranges'][0]
def _reg(g):
    c, r = g['cover'], g['rel10']
    return ('%s (%s events): M3 and above %s of %s inside, %s percent, %s, and at least one happened in %s of %s windows stated at 10 percent or more, %s percent against %s stated, %s'
            % (g['region'], n(g['sequences']), n(c['inside']), n(c['scored']), pc(c['share']), rw(c), n(r['occurred']), n(r['scored']), pc(r['share']), pc(r['stated_mean']), rw(r)))
REG = ', and '.join(e(_reg(g)) for g in D['by_region'])
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
fc = D['first_forecast_cover']; net = D['cover_by_network']; rnd = D['magnitude_rounded_check']; ra = S['reliability_above_mainshock']
nr = R['nothing_returned']; ct = R['cannot_tell']; vm = src['versions_missing']
body = hl + '''<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>
<h2>When the USGS states the odds of aftershocks, what follows?</h2>
<p>After a significant earthquake in the United States or its territories, and after some large earthquakes elsewhere, the USGS publishes an aftershock forecast and updates it on a schedule, daily at first and then weekly for a year. Each version states, for the next day, week, month and year, the chance of at least one earthquake at or above magnitude 3, 4, 5, 6 and 7, and a range for how many. The USGS scientific background calls that range &ldquo;the 95%% confidence range&rdquo; and says its 2.5 and 97.5 percent points are approximate for a number that can only be a whole number.</p>
<p>The USGS event catalog keeps every version of every forecast. This page reads all of them, from %s to %s, and uses a window only when the version was stamped in the catalog before the window opened. The count for each window comes from the same catalog, in the zone the forecast states for itself, for earthquakes at or above the forecast magnitude, leaving out the mainshock. A window is read once it has been closed for a week. %s</p>
<p>Windows from one sequence overlap. Every version of one forecast counts the same aftershocks, and the day, week, month and year windows of one version are nested. So every interval here is given two ways. The Wilson interval treats rows as independent. The second resamples whole groups of sequences, where sequences within 100 km and a year of each other form one group. The reading uses the wider of the two. A count outside the range is a count outside the range. This page does not say why. The plan, with the rules and the known-good checks, was fixed before any stated figure was set beside a count.</p>
<h2>How often the count fell inside the stated range</h2>
<div class="tw"><table class="bench"><thead><tr><th>Cell</th><th>Scored</th><th>Inside</th><th>Above the range</th><th>Below the range</th><th>Inside, percent</th><th>Wilson 95%% interval</th><th>Sequence 95%% interval</th><th>Reading</th><th>Groups of sequences</th><th>Rows with a range of 0 to 0</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">One row is one forecast version, one window and one magnitude. Reading against the stated 95 percent: below if the upper bound is under 95 percent, above if the lower bound is over 95 percent, consistent if the interval lies within 92.5 to 97.5 percent, otherwise cannot tell with the reason STRADDLES_EDGE. Fewer than 30 rows or fewer than 10 separate groups of nearby sequences is cannot tell with the reason TOO_WIDE_TO_RESOLVE. A cell with no rows or no interval is cannot tell with the reason NO_INTERVAL_FORMABLE. Edges are closed, so an interval end equal to a stated figure is neither above nor below it. No size that matters is named for these cells, so the check for an interval that holds both zero and a size that matters is not applied. A range of 0 to 0 is a statement that none is likely, and a single event breaks it. Most rows at M5 and above have a range of 0 to 0, and those rows are inside unless one such earthquake happens. Without them, M3 and above holds %s of %s inside (%s percent, %s, %s).</p>
<h2>How often at least one happened, by stated chance</h2>
<div class="tw"><table class="bench"><thead><tr><th>Stated chance</th><th>Scored</th><th>At least one happened</th><th>Stated, mean percent</th><th>Happened, percent</th><th>Wilson 95%% interval</th><th>Sequence 95%% interval</th><th>Reading</th><th>Groups of sequences</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Every magnitude and window together. Reading: above if the lower bound is over the mean stated chance, below if the upper bound is under it, consistent if the whole interval lies within a tolerance of it, otherwise cannot tell with the reason STRADDLES_EDGE. Fewer than 30 rows or 10 groups is cannot tell with the reason TOO_WIDE_TO_RESOLVE. The tolerance is 5 points, or half the stated chance or half its complement when that is smaller, and never under 1 point. The chance of an earthquake as large as the mainshock is read on its own: %s of %s windows saw one against a mean stated chance of %s percent, and the reading is %s.</p>
<h2>Higher stated chances, by magnitude and by window</h2>
<p>The same rows, stated at 10 percent or more, pooled and then split by magnitude and by window. This split was added after the data, at the outside review, and decides nothing.</p>
<div class="tw"><table class="bench"><thead><tr><th>Rows</th><th>Scored</th><th>At least one happened</th><th>Stated, mean percent</th><th>Happened, percent</th><th>Wilson 95%% interval</th><th>Sequence 95%% interval</th><th>Reading</th><th>Groups of sequences</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Counts farthest outside the stated range</h2>
<p>For M3 and above, the row farthest outside its range for each event. Each event links to its USGS forecast page.</p>
<div class="tw"><table class="bench"><thead><tr><th>Event</th><th>Version</th><th>Window</th><th>Stated chance of at least one, percent</th><th>Stated range</th><th>Count</th><th>Reading</th></tr></thead><tbody>%s</tbody></table></div>
<h2>Described, not scored</h2>
<p>The first version of each forecast alone, for M3 and above: %s of %s inside, %s percent, with a sequence interval of %s percent. Split by the network that located the mainshock, for M3 and above: %s. That split does not separate events in the United States from events elsewhere, since the USGS national network locates both. Split by place, %s. The Brier score of every scored probability is %s. With catalog magnitudes rounded to one decimal before the comparison, %s of %s rows keep the same range reading.</p>
<h2>What this page holds and what it leaves out</h2>
<p>Read on this run: %s events with a forecast, %s versions, and %s rows. Not yet readable: %s. Versions with no product to read: %s. Rows that cannot be read against the catalog: %s. These are counted apart and never folded into a share. Windows that opened before their version was stamped are listed apart and not scored: %s rows from %s of %s versions. Most of those versions were stamped a few minutes after their windows opened, with a median of %s minutes, and %s of them more than a day after. Among scored rows, %s come from versions the catalog indexed after the window opened, though stamped before it.</p>
<p>Older versions do not always state their zone in the forecast file. Where the forecast file states none, the zone in the same version's data file is used. Where neither states one, the rows read cannot tell. The count comes from the USGS catalog as it stands on the day of the run, which can differ from what the USGS had when it issued a forecast. The split by the network that located the mainshock is shown and not scored.</p>
<p>Set aside: the shape of the full distribution of the number, spatial forecasts, which the USGS says it does not issue, and any judgment of the forecast model.</p>
<p class="meta">Sources: USGS ComCat event service, aftershock forecast product (oaf), every archived version, and the ComCat catalog, read without a key. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about every six hours. The tables are from the run of %s, and the newest run is always in <a href="/quake/live.json">/quake/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/quake">quake</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://earthquake.usgs.gov/data/oaf/overview.php">USGS aftershock forecast overview</a> &middot; <a href="https://earthquake.usgs.gov/data/oaf/background.php">USGS aftershock forecast scientific background</a> &middot; <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS ComCat event service</a>. USGS data are in the public domain.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=quake-all">Respond</a></p>
<section id="replies" data-prefix="quake"></section><script src="/replies.js" defer></script>''' % (
    e(src['first_event'][:10]), e(src['last_event'][:10]), gate_line,
    cover_rows([S['headline_cell']] + [c for c in S['cover_by_magnitude'] if c['cell'] != 'M3 and above'] + S['cover_by_window'] + [S['cover_all']]), n(NZ['inside']), n(NZ['scored']), pc(NZ['share']), 'interval %s to %s percent' % (pc(NZ['lo']), pc(NZ['hi'])), rw(NZ),
    rel_rows(S['reliability']), n(ra['occurred']), n(ra['scored']), pc(ra['stated_mean']), rw(ra),
    rel_rows([D['stated_10_percent_or_more_all']] + D['stated_10_percent_or_more']),
    miss_rows(S['biggest_misses'][:15]),
    n(fc['inside']), n(fc['scored']), pc(fc['share']), iv(fc['boot']),
    ', and '.join('%s, %s of %s inside (%s percent)' % (e(c['cell'].split('by the ')[-1]), n(c['inside']), n(c['scored']), pc(c['share'])) for c in net),
    REG,
    '' if D['brier_score'] is None else '%.4f' % D['brier_score'], n(rnd['same_cover']), n(rnd['rows']),
    n(src['events']), n(src['versions']), n(R['total']),
    reasons(nr, (('window not closed', 'rows whose window has not closed a week ago'), ('catalog not read', 'rows whose catalog copy was not read after the window closed'))) or 'none',
    reasons(vm, (('deleted', 'deleted'), ('forecast not read', 'whose forecast file could not be read'), ('no forecast windows', 'with no windows'))) or 'none',
    reasons(ct, (('zone not stated', 'where the product states no zone'), ('zone not readable', 'where the zone has another shape'), ('unreadable', 'where a value did not parse'))) or 'none',
    n(R['issued_after_window_opened']), n(R['late_versions']['versions']), n(R['late_versions']['versions_parsed']), '%g' % R['late_versions']['median_minutes'], n(R['late_versions']['over_one_day']), n(D['indexed_after_window_opened']['rows']),
    e(S['generated'][:10]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/quake">
<meta name="tdm-reservation" content="1">
<meta name="tdm-policy" content="https://indahl.ai/terms#ai-training">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">QUAKE</b> &middot; Stated Aftershock Odds Against the Aftershocks That Followed</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('quake.html', 'w').write(page); print('quake.html', len(page))
