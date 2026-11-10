#!/usr/bin/env python3
"""build_page.py: writes neo.html, the desk's first page draft, from summary_neo.json. Reads no network. The live page is built by the site build, not here."""
import json, os, sys, html, time
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
S = json.load(open('summary_neo.json'))
e = html.escape
def au(x): return '' if x is None else ('%.8f' % x)
def pc(x): return '' if x is None else ('%.1f' % (100 * x))
def day(ts): return '%s-%s-%s' % (ts[:4], ts[4:6], ts[6:8])
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
cells = S['cells']; allc = cells[0]; R = S['rows']; src = S['sources']; g = S['gates']
first, last = day(R['first_stated_copy']), day(R['last_stated_copy'])
TITLE = 'NEO | Stated Close-Approach Distances Against the Later Record | Heuremen LLC'
DESC = 'NEO: each near-Earth object close-approach distance range that JPL stated from an earlier orbit solution, set beside the distance from the latest solution, by how long before the approach it was stated.'

def cell_rows():
    out = []
    for c in cells:
        why = c['cannot_tell_why']
        out.append('<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(c['cell']), c['scored'], c['inside'], c['above'], c['below'], pc(c['share']), pc(c['lo']), pc(c['hi']), WORD[c['outcome']], c['cannot_tell'],
            '' if c['median_abs_shift_sigma'] is None else '%.2f' % c['median_abs_shift_sigma'], pc(c['share_beyond_1_sigma']), '' if c.get('median_abs_move_km') is None else '{:,.0f}'.format(c['median_abs_move_km'])))
    return ''.join(out)
def why_line():
    w = allc['cannot_tell_why']; names = (('same solution', 'the stated solution is still the latest one'), ('edge', 'the latest range crosses an edge of the stated range'),
                                         ('wide range', 'the stated range is wider than 0.05 au'), ('no record', 'no current record of the approach was found'), ('unreadable', 'a value did not parse'))
    return ', '.join('%d where %s' % (w[k], t) for k, t in names if w.get(k))
def out_rows(rs):
    out = []
    for r in rs:
        ls = r.get('latest_solution') or {}
        link = '<a href="%s" rel="nofollow">%s</a>' % (e(r['stated_url']), day(r['stated_copy'])) if r.get('stated_url') else day(r['stated_copy'])
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%.0f</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s to %s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(r['des']), e(r['approach'][:10]), link, r['lead_days'], au(r['stated']), au(r['stated_min']), au(r['stated_max']), au(r.get('latest')), au(r.get('latest_min')), au(r.get('latest_max')),
            '' if r.get('z') is None else '%+.1f' % r['z'], '' if r.get('move_km') is None else '{:+,.0f}'.format(r['move_km']), WORD.get(r['outcome'], e(r['outcome'].lower().replace('_', ' '))) + ((' (' + e(r['why']) + ')') if r.get('why') else ''),
            e('%s to %s' % (r.get('stated_orbit'), r.get('latest_orbit'))) + ((', arc %s d' % e(str(ls.get('data_arc')))) if ls.get('data_arc') else '')))
    return ''.join(out)
outside = [r for r in S['outside_range'] if r['headline']]
BC = S['by_copy_day']; BIG = max(BC['scored'], key=lambda k: BC['scored'][k]); BIGDAY = time.strftime('%d %B %Y', time.strptime(BIG, '%Y%m%d')).lstrip('0')
def lop_note():
    ls = [r['des'] for r in outside if r.get('lopsided')]
    if not ls: return ''
    return (' For %s the stated nominal sits near one end of a wide range, so a small shift in stated sigma can still leave the range.' % (', '.join(e(x) for x in ls[:-1]) + ' and ' + e(ls[-1]) if len(ls) > 1 else e(ls[0])))
def without_line():
    a, n = DC.get('all leads'), DC.get('0 to 7 days')
    if not (a and n and DEP.get('copy') and BIG == DEP['copy_day']): return ''
    return (' Without that copy %d of %d scored rows are inside and the first row reads %s, and the 0 to 7 day cell holds %d of %d and reads %s. These readings without the copy were added after the data and decide nothing.'
            % (a['without']['inside'], a['without']['scored'], WORD[a['without']['outcome']], n['without']['inside'], n['without']['scored'], WORD[n['without']['outcome']]))
small = sum(1 for r in outside if r.get('move_km') is not None and abs(r['move_km']) < 2000)
aug = S['august_2026']; augr = S['august_rows']
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
need = 'At this sample size a cell can read consistent only if nearly every row is inside. It takes about 190 scored rows, all inside, for the lower bound to reach 98 percent.'
from neo_headline import headline
DEP = S.get('dependence') or {}; DC = {c['cell']: c for c in DEP.get('cells', [])}
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
body = hl + '''<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>
<h2>When JPL states how close an object will pass, where does the latest solution put it?</h2>
<p>NASA's Center for Near-Earth Object Studies at JPL publishes a table of close approaches to Earth. For each approach it states a nominal distance, a minimum distance and a maximum distance. The data service defines the last two as the &ldquo;minimum (3-sigma) approach distance&rdquo; and the &ldquo;maximum (3-sigma) approach distance&rdquo;. Each row names the orbit solution it was computed from. The CNEOS page on uncertainties says: &ldquo;Earth close-approach statistics for a given NEO can change (often by large amounts) as new data become available and the orbit is updated.&rdquo;</p>
<p>JPL serves the current solution only. An earlier statement can be read only from a copy made at the time. This page uses the copies of the JPL close-approach service that the Internet Archive holds from January 2024 on, and the copies this desk has stored since %s. Each stated range is set beside the distance from the latest solution for the same approach. The first statement used was copied on %s and the last on %s.</p>
<p>JPL does not state how often a later distance should fall inside the range. Reading a 3-sigma range as one that holds about 99.7 percent of later values comes from a normal distribution and is our reading. CNEOS bases the minimum on a 3-sigma ellipse in the target plane. Under a normal distribution a point falls inside such an ellipse about 98.9 percent of the time, and every cell reads the same against 98.9 percent as against 99.7 percent. A later distance outside the range is a later distance outside the range. This page does not say why it moved. The plan, with the rules and the known-good checks, was fixed before any stated distance was set beside a later one. %s</p>
<h2>By how long before the approach the range was stated</h2>
<div class="tw"><table class="bench"><thead><tr><th>Stated before the approach</th><th>Scored</th><th>Inside</th><th>Farther</th><th>Closer</th><th>Inside, percent</th><th>95%% interval, percent</th><th>Reading</th><th>Cannot tell</th><th>Median shift, stated sigma</th><th>Beyond one sigma, percent</th><th>Median move, km</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">One row is one object and one approach inside 0.05 au since 1 January 2024, taken from the earliest copy that shows it before the approach. An object is counted once in a cell. Inside means the whole 3-sigma range of the latest solution lies inside the range stated earlier. Farther and closer mean the whole latest range lies outside it. Cannot tell is never folded into either side. In the first row it holds %s. The interval is a 95%% Wilson interval. Reading: below if the upper bound is under 99.7 percent, consistent if the lower bound is 98 percent or more, otherwise cannot tell. %s The interval treats rows as independent. Rows from one copy share one moment of JPL\'s data, so the interval can be too narrow. The shift is the move of the nominal distance divided by one sixth of the stated range. It describes the move and is not a test.</p>
<h2>Approaches where the latest solution is outside the stated range</h2>
<div class="tw"><table class="bench"><thead><tr><th>Object</th><th>Approach</th><th>Stated copy</th><th>Days before</th><th>Stated nominal, au</th><th>Stated range, au</th><th>Latest nominal, au</th><th>Latest range, au</th><th>Shift, stated sigma</th><th>Move, km</th><th>Reading</th><th>Solution</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">In %d of these %d rows the nominal distance moved by less than 2,000 km. Each stated copy links to the archived response. Solution shows the orbit ID the range was stated from and the latest orbit ID, with the latest solution's data arc in days where it was read.%s</p>
<h2>August approaches</h2>
<p>Approaches dated August 2026 are shown apart. The rows and rules are the same. %d rows are scored, %d inside, %d farther and %d closer, and %d cannot tell. %s</p>
<div class="tw"><table class="bench"><thead><tr><th>Object</th><th>Approach</th><th>Stated copy</th><th>Days before</th><th>Stated nominal, au</th><th>Stated range, au</th><th>Latest nominal, au</th><th>Latest range, au</th><th>Shift, stated sigma</th><th>Move, km</th><th>Reading</th><th>Solution</th></tr></thead><tbody>%s</tbody></table></div>
<h2>What this page holds and what it leaves out</h2>
<p>The copies are what the Internet Archive and this desk happened to store. They are not a random sample of approaches. One archived copy holds the full table out to the year 2200. It was made on %s and it gives %d of the %d scored rows and %d of the %d rows outside the range.%s The statements in that copy were made months or years before the approach, for objects already known then. Objects found days before they pass appear only in the smaller copies. The JPL table itself lists only approaches whose 3-sigma time uncertainty is within 10 days and whose position uncertainty is within 0.1 au.</p>
<p>The latest solution is the delivered side. For an approach that has passed it may include observations made during and after the approach. It carries its own 3-sigma range, and that range is what is set against the stated one.</p>
<p>Set aside: Sentry impact probabilities and removals, which have no stated range to test and are stored on each run for later. Scout. Minor Planet Center circulars and orbits. Other agencies' lists. Orbit fits of our own. Approaches to other bodies, approaches before 2024 and stated distances beyond 0.05 au. Later statements of an approach are scored and kept in the data, and are not in the cells: %d rows.</p>
<p class="meta">Sources: NASA/JPL SBDB Close-Approach Data API version %s and SBDB API, read without a key, one request at a time. Internet Archive Wayback Machine. Archived copies indexed: %d. Used: %d. Copies of our own: %d. Rows read: %s, of which %s describe approaches that have not happened yet. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about every six hours. The tables are from the run of %s, and the newest run is always in <a href="/neo/live.json">/neo/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/neo">neo</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://cneos.jpl.nasa.gov/ca/">NASA/JPL CNEOS close approaches</a> &middot; <a href="https://ssd-api.jpl.nasa.gov/doc/cad.html">JPL SBDB Close-Approach Data API</a> &middot; <a href="https://ssd-api.jpl.nasa.gov/doc/sbdb.html">JPL SBDB API</a> &middot; <a href="https://web.archive.org/">Internet Archive Wayback Machine</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=neo-all">Respond</a></p>
<section id="replies" data-prefix="neo"></section><script src="/replies.js" defer></script>''' % (
    day(src['own_first_copy']) if src.get('own_first_copy') else 'its first run', first, last, gate_line, cell_rows(), why_line(), need,
    out_rows(sorted(outside, key=lambda r: -abs(r.get('z') or 0))), small, len(outside), lop_note(),
    aug['scored'], aug['inside'], aug['above'], aug['below'], aug['cannot_tell'], 'With fewer than 10 scored rows the subset has no reading of its own.' if aug['scored'] < 10 else 'The subset reads %s, with a 95%% interval of %s to %s percent.' % (WORD[aug['outcome']], pc(aug['lo']), pc(aug['hi'])),
    out_rows(sorted(augr, key=lambda r: r['approach'])),
    BIGDAY, BC['scored'].get(BIG, 0), allc['scored'], BC['outside'].get(BIG, 0), allc['above'] + allc['below'], without_line(),
    R['later_statements'], e(S['claim']['source'].split()[-1]), src['wayback_index_copies'], src['wayback'].get('used', 0), src['own_copies'], '{:,}'.format(R['total']), '{:,}'.format(R['outcomes'].get('NOTHING_RETURNED', 0)), e(S['generated'][:10]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/neo">
<meta name="tdm-reservation" content="1">
<meta name="tdm-policy" content="https://indahl.ai/terms#ai-training">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">NEO</b> &middot; Stated Close-Approach Distances Against the Later Record</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('neo.html', 'w').write(page); print('neo.html', len(page))
