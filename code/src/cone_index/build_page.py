#!/usr/bin/env python3
"""build_page.py: writes cone.html, the desk's page draft, from summary_cone.json. Reads no network. The live page is built by the site build from this body."""
import json, os, sys, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
from cone_headline import headline, seasons_phrase, WORD, pc, rw
S = json.load(open('summary_cone.json'))
e = html.escape
BN = {'AL': 'Atlantic', 'EP': 'East Pacific'}
cells = S['cells']; wp = [c for c in cells if c['kind'] == 'whole path']; circ = [c for c in cells if c['kind'] == 'circle']
src = S['sources']; g = S['gates']; R = S['rows']
TITLE = 'CONE | The Hurricane Forecast Cone Against Where Storms Went | Heuremen LLC'
DESC = 'CONE: National Hurricane Center official track forecasts set beside the post-season best track, scored against the cone NHC states holds the storm center about 60 to 70 percent of the time.'
def nr(c):
    w = c.get('nothing_returned_why') or {}
    t = []
    if w.get('no best-track point'): t.append('{:,} track ended'.format(w['no best-track point']))
    if w.get('not a tropical cyclone'): t.append('{:,} no longer tropical'.format(w['not a tropical cyclone']))
    return '{:,}'.format(c['nothing_returned']) + (' (' + ', '.join(t) + ')' if t else '')
def iv(c): return '' if c['lo'] is None else '%s to %s' % (pc(c['lo']), pc(c['hi']))
def wp_rows():
    return ''.join('<tr><td>%s</td><td>%d</td><td>{:,}</td><td>{:,}</td><td>{:,}</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'.format(c['scored'], c['inside'], c['outside']) % (
        BN[c['basin']], c['storms'], pc(c['share']), iv(c), rw(c), nr(c)) for c in wp)
def circ_rows():
    out = []
    for c in circ:
        out.append('<tr><td>%s</td><td>%d h</td><td>%d</td><td>{:,}</td><td>{:,}</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'.format(c['scored'], c['inside']) % (
            BN[c['basin']], c['lead'], c['storms'], pc(c['share']), iv(c), rw(c), '' if c['median_nmi'] is None else '%.0f' % c['median_nmi'], nr(c)))
    return ''.join(out)
def season_rows():
    out = []
    for s in S['by_season']:
        w = s['whole_path']; c48 = s['circles']['48']; c120 = s['circles']['120']
        if not s.get('radii'):
            out.append('<tr><td>%d</td><td>%s</td><td colspan="7">No cone radii table names this season. Not scored.</td></tr>' % (s['season'], BN[s['basin']])); continue
        out.append('<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            s['season'], BN[s['basin']], e(s['radii_stats'] or ''), '%d of %d' % (w['inside'], w['scored']), pc(w['share']), rw(w),
            '%s (%d)' % (pc(c48['share']), c48['scored']), '%s (%d)' % (pc(c120['share']), c120['scored']), 'post-season best track' if s['best_track'] == 'HURDAT2' else 'operational best track'))
    return ''.join(out)
V = S['verification']
def ver_rows(rs):
    return ''.join('<tr><td>%s</td><td>%d</td><td>%d h</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        BN[v['basin']], v['season'], v['lead'], '' if v['stated'] is None else '%.1f' % v['stated'], '' if v['n_stated'] is None else v['n_stated'],
        '' if v['ours'] is None else '%.1f' % v['ours'], v['n_ours'], '' if v['band'] is None else '%.1f to %.1f' % tuple(v['band']),
        WORD[v['outcome']] + ((' (%s, case counts differ)' % v['reason'] if v.get('reason') else ' (case counts differ)') if v.get('why') == 'case counts differ' else (' (%s)' % v['reason'] if v.get('reason') else '')),
        ('%.1f (%d)' % (v['ours_60h']['mean'], v['ours_60h']['n'])) if (v.get('ours_60h') or {}).get('mean') is not None else '') for v in rs)
vt = S['verification_tally']
def vt_line():
    out = []
    for b in ('AL', 'EP'):
        t = vt.get(b, {}); n = sum(t.values())
        out.append('%s: %d rows, %d consistent, %d above, %d below and %d cannot tell' % (BN[b], n, t.get('CONSISTENT', 0), t.get('ABOVE', 0), t.get('BELOW', 0), t.get('CANNOT_TELL', 0))
                   + (', every cannot tell row a row whose case counts differ' if t.get('CANNOT_TELL') and all(v.get('why') == 'case counts differ' for v in V if v['basin'] == b and v['outcome'] == 'CANNOT_TELL') else ''))
    return '. '.join(out) + '.'
not_cons = [v for v in V if v['outcome'] != 'CONSISTENT']
cur = S.get('current') or []
def cur_line():
    if not cur: return 'No season is waiting for its post-season best track.'
    t = []
    for s in cur:
        w = s['whole_path']
        if not w['scored']: t.append('%s %d: no forecast had a full track yet, so the whole path cannot be read' % (BN[s['basin']], s['season'])); continue
        t.append('%s %d: %d of %d forecasts with a full track stayed inside for the whole path (%s percent), which reads %s' % (BN[s['basin']], s['season'], w['inside'], w['scored'], pc(w['share']), rw(w)))
    return '. '.join(t) + '. These seasons use the operational best track NHC keeps during the season, and they enter the cells above when the post-season best track is posted.'
def knife():
    a = wp[0]
    if a['outcome'] == 'CANNOT_TELL' and a['hi'] is not None and 0 <= a['hi'] - 0.60 < 0.01:
        return ' The upper end of the Atlantic interval is %.1f points above the lower end of NHC\'s range.' % (100 * (a['hi'] - 0.60))
    if a['outcome'] == 'CANNOT_TELL' and a['lo'] is not None and 0 <= 0.70 - a['lo'] < 0.01:
        return ' The lower end of the Atlantic interval is %.1f points below the upper end of NHC\'s range.' % (100 * (0.70 - a['lo']))
    return ''
WP_REQ = ' '.join('%s: %s' % (BN[c['basin']], c['req13']['line']) for c in wp) if all(c.get('req13') for c in wp) else ''
CIRC_REQ = ' '.join('%s %d h: %s' % (BN[c['basin']], c['lead'], c['req13']['line']) for c in circ) if all(c.get('req13') for c in circ) else ''
fo = src['frame_out']
fo_line = ', '.join('%s %s' % ('{:,}'.format(v), k) for k, v in sorted(fo.items(), key=lambda kv: -kv[1]))
gate_line = 'All four known-good checks passed on this run.' if g['passed'] else 'A known-good check did not pass on this run, so every outcome reads cannot tell.'
fl = S['frame']['final_last']
HL_BIG, HL_LINE = headline(S)
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HL_BIG), e(HL_LINE))
body = hl + '''<p class="meta crumb">Division: <a href="/atlas">ATLAS</a></p>
<h2>When the National Hurricane Center draws a cone, how often does the storm stay inside it?</h2>
<p>Every official track forecast from the National Hurricane Center (NHC) comes with a cone. The NHC cone page says the size of each circle that forms it &ldquo;is set so that two-thirds of historical official forecast errors over a 5-year sample fall within the circle.&rdquo; The page shown with each forecast says: &ldquo;Historical data indicate that the entire 5-day path of the center of the tropical cyclone will remain within the cone about 60-70%% of the time.&rdquo; NHC changes the circle sizes every year and prints them in a table.</p>
<p>This page sets each official forecast position from NHC's public forecast files beside the best track, NHC's own post-season record of where the center was, every six hours. It asks two things. Did the whole five-day path stay inside that forecast's cone? And at each lead time, did the center fall inside the circle of that year's size? Seasons %s are read with the post-season best track. The plan, with the rules and the known-good checks, was fixed before any forecast was set beside a best-track position. %s</p>
<h2>The whole five-day path</h2>
<div class="tw"><table class="bench"><thead><tr><th>Basin</th><th>Storms</th><th>Forecasts scored</th><th>Inside the whole way</th><th>Left the cone</th><th>Inside, percent</th><th>95%% interval, percent</th><th>Reading against 60 to 70 percent</th><th>Nothing returned</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">A forecast is scored when it carries all seven lead times and the storm was still a tropical or subtropical cyclone in the best track at every six-hour point from 12 to 120 hours. The cone is built from NHC's circles at 12, 24, 36, 48, 72, 96 and 120 hours with that season's sizes, joined the way NHC describes, starting from the forecast's first position. Inside the whole way means every six-hour best-track point from 12 to 120 hours lies in it. Timing is not checked, as NHC's wording is about the path. Nothing returned counts forecasts whose storm track ended or stopped being tropical within five days. Those are never folded into either side. Forecasts shorter than five days are left out: %s. The cone here leaves out the 60 h circle, as NHC's graphic page does (NHC's cone page lists it). Starting the cone at the 12 h circle instead of the first position lowers the share by 1.6 points in the Atlantic and 2.8 in the East Pacific, in the referee's recount after the data, which decides nothing.%s</p>
<p class="bench-note">Forecasts of one storm share most of their track, so they are not independent. Each interval is a storm-level block bootstrap: storms are drawn again with replacement, all of a drawn storm's forecasts come with it, 2,000 times. Reading: consistent if the whole interval lies inside 60 to 70 percent, above if it lies above 70, below if it lies below 60, otherwise cannot tell with the reason STRADDLES_EDGE. A cell with fewer than 10 storms or 30 scored rows is cannot tell with the reason TOO_WIDE_TO_RESOLVE, and a cell with no scored rows is cannot tell with the reason NO_INTERVAL_FORMABLE. Edges are closed, so an interval end equal to 60 or 70 percent is inside the band. A cone reading is a share against a band, so no size that matters is named and the check for an interval that holds both zero and a size that matters is not applied. Beside each share the rows behind it are counted: %s</p>
<h2>At each lead time</h2>
<div class="tw"><table class="bench"><thead><tr><th>Basin</th><th>Lead</th><th>Storms</th><th>Positions scored</th><th>Inside the circle</th><th>Inside, percent</th><th>95%% interval, percent</th><th>Reading against two-thirds</th><th>Median miss, n mi</th><th>Nothing returned</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">Inside means the best-track position at the verifying time lies within that season's circle radius of the forecast position, by great-circle distance. NHC states two-thirds. Reading two-thirds as 61.7 to 71.7 percent is our reading. Positions are compared at the tenth of a degree NHC prints, with no tolerance added. The interval is the same storm-level bootstrap, the edges of the band are closed, and a cell that straddles an edge reads cannot tell with the reason STRADDLES_EDGE. Rows behind each cell: %s</p>
<h2>Season by season</h2>
<div class="tw"><table class="bench"><thead><tr><th>Season</th><th>Basin</th><th>Circle sizes set from seasons</th><th>Whole path inside</th><th>Percent</th><th>Reading</th><th>48 h circle, percent (scored)</th><th>120 h circle, percent (scored)</th><th>Best track</th></tr></thead><tbody>%s</tbody></table></div>
<p class="bench-note">%s</p>
<h2>A second ruler: the averages NHC publishes</h2>
<p>NHC publishes, in its tables titled &ldquo;Average NHC Atlantic Track Forecast Errors&rdquo; and the same for the Eastern North Pacific, the average great-circle distance between its official forecast position and the best track for every season and lead time, with the number of cases. We recounted the same average from the same forecast files and the best track, using NHC's rule that both the forecast time and the verifying time must be tropical or subtropical. A row reads consistent if our average is within the larger of 1 n mi and 2 percent of NHC's, and cannot tell, with the reason NO_INTERVAL_FORMABLE, if the case counts differ by more than the larger of 2 cases and 5 percent, since then the samples differ and the two averages cannot be compared. The band edges are closed. %s</p>
%s
<h2>What this page holds and what it leaves out</h2>
<p>The forecasts are NHC's official ones as stored in its public forecast files, one per storm and six-hour initial time. In the East Pacific only forecasts starting east of 140 W are read. Central Pacific forecasts are left out. Set aside by the plan's frame, each forecast counted in the first reason that applies in the order the run tests them: %s. The circle sizes come from the NHC cone page and its copies in the Internet Archive, each season using the table that names it.</p>
<p>The cone's day one to three and day four to five shading, wind field size, watches and warnings, and intensity forecasts are not read. A forecast outside the cone is a forecast outside the cone. This page does not say why the storm went where it went.</p>
<p class="meta">Sources: NOAA National Hurricane Center ATCF forecast files (official forecasts), HURDAT2 best track (%s), ATCF operational best track for the current season, the NHC cone page and NHC verification tables, and the Internet Archive Wayback Machine. NOAA data are in the public domain, credit NOAA/NHC. Forecast files read: %d. Generated %s. Heuremen LLC.</p>
<p class="meta">The headline is read again about every six hours. The tables are from the run of %s, and the newest run is always in <a href="/cone/live.json">/cone/live.json</a>.</p>
<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/cone">cone</a>. The plan was fixed before the comparison it describes.</p>
<p class="meta">Data read from: <a href="https://www.nhc.noaa.gov/aboutcone.shtml">NHC cone definition</a> &middot; <a href="https://ftp.nhc.noaa.gov/atcf/">NHC ATCF files</a> &middot; <a href="https://www.nhc.noaa.gov/data/#hurdat">NHC HURDAT2</a> &middot; <a href="https://www.nhc.noaa.gov/verification/">NHC forecast verification</a> &middot; <a href="https://web.archive.org/">Internet Archive Wayback Machine</a>.</p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=cone-all">Respond</a></p>
<section id="replies" data-prefix="cone"></section><script src="/replies.js" defer></script>''' % (
    e(seasons_phrase(S)), gate_line, wp_rows(), ', '.join('%s %s' % (BN[b], '{:,}'.format(n)) for b, n in sorted(src['forecasts_shorter_than_five_days'].items())), knife(),
    WP_REQ, circ_rows(), CIRC_REQ, season_rows(), e(cur_line()), e(vt_line()),
    ('<p>Rows that do not read consistent are listed here. Every row is in the data. For these rows the last column gives our recount at 60 hours, a lead NHC forecasts but these tables do not print. It was added after the data and decides nothing.</p><div class="tw"><table class="bench"><thead><tr><th>Basin</th><th>Season</th><th>Lead</th><th>NHC average, n mi</th><th>NHC cases</th><th>Our average, n mi</th><th>Our cases</th><th>Consistent band, n mi</th><th>Reading</th><th>Our 60 h average, n mi (cases)</th></tr></thead><tbody>%s</tbody></table></div>' % ver_rows(not_cons)) if not_cons else '<p>Every row reads consistent.</p>',
    e(fo_line), e(', '.join('%s %s' % (k, v['file']) for k, v in sorted(src['hurdat'].items()))), src['adeck_files'], e(S['generated'][:10]), e(S['generated'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="https://indahl.ai/cone">
<meta name="tdm-reservation" content="1">
<meta name="tdm-policy" content="https://indahl.ai/terms#ai-training">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">CONE</b> &middot; The Hurricane Forecast Cone Against Where Storms Went</h1></div></section>
<main class="wrap">%s</main>
</body>
</html>
''' % (e(TITLE), e(DESC), body)
open('cone.html', 'w').write(page); print('cone.html', len(page))
