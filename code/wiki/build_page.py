#!/usr/bin/env python3
"""build_page.py: draft page wiki.html for the WIKI desk, rendered from data/wiki_live.json (every number on the page comes from it).
Head, header/nav, footer and tab bar are copied from indahl-ai/launch.html as they are; only the page's own title, description,
canonical URL and structured data are changed. Nothing is published: Bones places the page, adds the nav entry and ships."""
import os, re, json, html, time, datetime as D

H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser('~/bones-forge/indahl-ai/launch.html')
L = json.load(open(os.path.join(H, 'data', 'wiki_live.json')))
E = lambda s: html.escape(str(s), quote=True)

TITLE = 'WIKI | Figures Against Their Source | Heuremen LLC'
DESC = ('WIKI: figures in Wikidata that cite the World Bank or UNESCO, read against that source\'s current and archived releases, '
        'and the Wikimedia Foundation\'s stated reach read against its own public data.')
FEED = '/wiki/live.json'
OUT_WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell'}
BIN_WORD = {'MATCHES_CURRENT': 'Matches the current release', 'MATCHES_AN_OLDER_RELEASE': 'Matches an older release',
            'MATCHES_NO_RELEASE_READ': 'Matches no release read', 'SOURCE_UNREADABLE': 'Nothing returned'}
VERB = {'MATCHES_CURRENT': 'match the current release', 'MATCHES_AN_OLDER_RELEASE': 'match an older release',
        'MATCHES_NO_RELEASE_READ': 'match no release read', 'SOURCE_UNREADABLE': 'returned nothing'}
BINS = list(BIN_WORD); OUTS = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL']
GROUP_ORDER = ['WB-POP', 'WB-GDP', 'WB-GINI', 'WB-UNEMP', 'UIS-LE', 'UIS-TFR']
SRC_SHORT = {'World Bank WDI': 'World Bank', 'UNESCO Institute for Statistics': 'UIS'}
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}
WIN = {'latest12': 'last 12 months', 'fy2425': 'July 2024 to June 2025', 'today': 'read today', 'moments': 'three moments'}


def n(x): return f'{x:,}'
def pc(x, d=1): return '' if x is None else f'{100 * x:.{d}f}%'
def iv(a): return '' if not a or a[0] is None else f'[{100 * a[0]:.1f}, {100 * a[1]:.1f}]'
def word(k): return WORDS.get(k, n(k))
def written(c):
    """The cited figure with thousands separators and every written digit kept."""
    if re.fullmatch(r'-?\d+', c): return f'{int(c):,}'
    m = re.fullmatch(r'(-?)(\d+)\.(\d+)', c)
    return f'{m.group(1)}{int(m.group(2)):,}.{m.group(3)}' if m else c
def long_date(iso):
    try: d = D.date.fromisoformat(iso[:10]); return f'{d.day} {d.strftime("%B %Y")}'
    except Exception: return iso
def short_date(iso):
    try: d = D.date.fromisoformat(iso[:10]); return f'{d.day} {d.strftime("%b %Y")}'
    except Exception: return iso
def read_stamp(s):
    """10 Nov 2026 (ship): the feed's stamp is now YYYY-MM-DD HH:MM UTC (so the drift seat can read it); the page keeps the long form."""
    try: d = D.datetime.strptime(s, '%Y-%m-%d %H:%M UTC'); return f'{d.day} {d.strftime("%b %Y")} {d.strftime("%H:%M")} UTC'
    except Exception: return s
def date_ts(ts):
    d = D.datetime.strptime(ts[:8], '%Y%m%d'); return f'{d.day} {d.strftime("%b %Y")}'
def date_tm(ts):
    d = D.datetime.strptime(ts[:12], '%Y%m%d%H%M'); return f'{d.day} {d.strftime("%b %Y")} {d.strftime("%H:%M")} UTC'
def wb_link(ts, url, with_time=False):
    return f'<a href="https://web.archive.org/web/{ts}/{E(url)}">{date_tm(ts) if with_time else date_ts(ts)}</a>'
def fbig(x):
    if x is None: return ''
    if abs(x) >= 1e9: return f'{x / 1e9:g} billion'
    if abs(x) >= 1e6: return f'{x / 1e6:g} million'
    return f'{x:,g}'
def big(v, kind):
    if v is None: return ''
    if kind == 'views': return f'{v / 1e9:.2f} billion'
    if kind == 'edits': return f'{v:.1f}'
    return n(int(round(v)))
def cell(t):
    if not t or t['n'] == 0: return '<td class="n">0</td>'
    return (f'<td class="n">{n(t["k"])}<br><span class="srckind">{pc(t["share"])} &middot; Wilson 95% {iv(t["wilson95"])}'
            f' &middot; countries 95% {iv(t["country95"])}</span></td>')
def table(head, rows, small=False):
    return (f'<div class="scroll"><table class="mtx{" small" if small else ""}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) +
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


# ------------------------------------------------------------------------------------------------ section 1
s1 = L['section1']; allg = s1['ALL']; pop = s1.get('WB-POP', {}); gdp = s1.get('WB-GDP', {}); un = s1.get('WB-UNEMP', {})
def k(g, b): return g['bins'][b]['k']
parts = []
hl_big = f'{n(k(pop, "MATCHES_CURRENT") + k(pop, "MATCHES_AN_OLDER_RELEASE"))} of {n(pop["rows"])}'
hl_line = (f'population figures for countries and territories in Wikidata that cite the World Bank match a World Bank release at the precision '
           f'they are written in. {n(k(pop, "MATCHES_CURRENT"))} match the current release and {n(k(pop, "MATCHES_AN_OLDER_RELEASE"))} an older one.')

wbr = pop.get('source_read') or {}; uisr = (s1.get('UIS-LE', {}).get('source_read') or {})
parts.append('<h2>Cited figures against their source</h2>')
parts.append(
    '<p>Wikidata keeps many official figures with a reference to where they came from. For population, GDP, the Gini coefficient and the '
    'unemployment rate the reference is often the World Bank. For life expectancy and the fertility rate it is often the UNESCO Institute for '
    'Statistics (UIS). We read every such figure held for a country or territory with an ISO country code, and compare it with the source\'s '
    'current release and with every older release the source still publishes. The World Bank publishes its releases back to April 1989: we read '
    f'its current release (last updated {E(long_date(wbr.get("lastupdated", "")))}) and the {E(wbr.get("releases_read", ""))} releases in its WDI Database '
    f'Archives. The UIS data API keeps its releases from September 2024 on: we read all {E(uisr.get("releases_read", ""))} of its versions, which hold '
    f'{word(uisr.get("distinct_value_sets", 0))} distinct sets of these figures (a count defined after the data).</p>')
parts.append(
    '<p>A figure matches a release when the two differ by no more than half a unit of the figure\'s last written digit, counted to at least its '
    'first three significant digits, plus about 6 in 100 million of the release\'s value. The plan adds that last allowance because some archived '
    'releases store values in single precision. On a GDP of $17 billion it comes to about $1,000. Each figure lands in one of four bins: it matches '
    'the current release, it matches an older release (we name the newest release that carried it), it matches no release we read, or the source '
    'returned nothing for that country and year. A figure that matches an older release carries a value that release carried, at the precision the '
    'figure is written in. We measure the gap and name no cause for it. The rules were committed before any comparison was read.</p>')
rows_html = []
for gid in GROUP_ORDER + ['ALL']:
    g = s1.get(gid)
    if not g: continue
    lab = 'All of the above' if gid == 'ALL' else f'{E(g["label"])}<br><span class="srckind">{E(SRC_SHORT.get(g["source"], g["source"]))}, {E(g["series"])}</span>'
    rows_html.append(f'<tr><td>{lab}</td><td class="n">{n(g["rows"])}<br><span class="srckind">{n(g["countries"])} countries and territories</span></td>' +
                     ''.join(cell(g['bins'][b]) for b in BINS) + '</tr>')
parts.append(table(['Figure', 'Figures read'] + [BIN_WORD[b] for b in BINS], rows_html))
parts.append('<p class="bench-note">Each share has two 95% intervals. Wilson treats every figure as independent. Countries resamples whole countries '
             '(2,000 draws), since the figures for one country come from one source series and are not independent of each other. The bins use neither interval.</p>')

# UIS: what the figures cite, and the second reading (B2: count only real matches; denominator: figures that match no UIS release)
uis_bits, cite_bits, nodate_bits = [], [], []
for gid in ('UIS-LE', 'UIS-TFR'):
    g = s1.get(gid) or {}; sec = g.get('wb_secondary_norel') or {}; cit = g.get('uis_citation') or {}
    if sec.get('rows'):
        hit = sec.get('match_current', 0) + sec.get('match_older', 0)
        nm = 'life expectancy' if gid == 'UIS-LE' else 'fertility'
        uis_bits.append((f'all {n(hit)}' if hit == sec['rows'] else f'{n(hit)} of the {n(sec["rows"])}') + f' {nm} figures')
    if cit: cite_bits.append(f'{n(cit["cite_uis_stat"])} of {n(cit["rows"])}'); nodate_bits.append(n(cit['no_retrieved']))
if cite_bits:
    parts.append(f'<p>The UIS figures here cite UIS.Stat, the database UIS ran before its data API ({cite_bits[0]} life-expectancy figures and {cite_bits[1]} '
                 f'fertility figures, a count defined after the data), and nearly all carry no retrieval date ({nodate_bits[0]} and {nodate_bits[1]}). The API keeps no '
                 'release before September 2024, so an older UIS.Stat figure can match only a UIS release that still carries it. As a second reading fixed before '
                 'the data, we read the UIS figures that match no UIS release against the World Bank\'s releases of the indicator code they carry. '
                 f'{uis_bits[0][0].upper() + uis_bits[0][1:]} and {uis_bits[1]} that match no UIS release equal a World Bank release of the same code. UIS does not state '
                 'the source of these series in its API, so this reading does not change the bins.</p>')
uis_norel = sum((s1.get(g) or {}).get('bins', {}).get('MATCHES_NO_RELEASE_READ', {}).get('k', 0) for g in ('UIS-LE', 'UIS-TFR'))
parts.append('<p class="bench-note">The row for all figures mixes sources with different depths of history: the World Bank archive reaches back to 1989, the UIS '
             f'data API to September 2024. Defined after the data: {n(uis_norel)} of its {n(k(allg, "MATCHES_NO_RELEASE_READ"))} figures that match no release read are UIS figures.</p>')
gd = gdp.get('by_unit') or {}
if gd:
    def unit_line(d): return ', '.join(f'{n(d.get(b, 0))} {VERB[b]}' for b in BINS if d.get(b))
    parts.append(f'<p>GDP figures by unit. With the US-dollar unit ({n(sum(gd.get("Q4917", {}).values()))}): {unit_line(gd.get("Q4917", {}))}. '
                 f'With no unit ({n(sum(gd.get("1", {}).values()))}), read as US dollars because the reference names that series: {unit_line(gd.get("1", {}))}.</p>')
gs = gdp.get('sensitivity') or {}
if gs.get('moved'):
    hb = gs['half_unit_bins']; mk = gs.get('moved_kinds') or {}; ps = (pop.get('sensitivity') or {}).get('moved', 0)
    parts.append(f'<p>Defined after the data: for GDP figures written to the dollar, the allowance of about 6 in 100 million decides {n(gs["moved"])} of the '
                 f'{n(gdp["rows"])} bins. In {n(mk.get("cut", 0))} of them the cited figure is the source\'s value with its decimals cut off rather than rounded. '
                 f'In {n(mk.get("revision", 0))} an older release carried the figure to the dollar and the current release differs from it by less than the allowance. '
                 f'With half a written unit alone, GDP would read {n(hb["MATCHES_CURRENT"])} matching the current release, {n(hb["MATCHES_AN_OLDER_RELEASE"])} an older '
                 f'release, {n(hb["MATCHES_NO_RELEASE_READ"])} no release read and {n(hb["SOURCE_UNREADABLE"])} nothing returned, against {n(k(gdp, "MATCHES_CURRENT"))}, '
                 f'{n(k(gdp, "MATCHES_AN_OLDER_RELEASE"))}, {n(k(gdp, "MATCHES_NO_RELEASE_READ"))} and {n(k(gdp, "SOURCE_UNREADABLE"))} above. For population the allowance '
                 f'decides {word(ps)} bin{"" if ps == 1 else "s"}.</p>')

parts.append('<h3>The size of the gap</h3>')
parts.append('<p>We also read the gap between each figure and the source\'s current figure for the same country and year. The size that matters, '
             'fixed before the data, is 1 percent of the current figure. Above means the figure as cited is more than 1 percent above the source\'s '
             'current figure, and below means more than 1 percent below. Within 1 percent is a bound, not a claim that the two are equal. Cannot tell '
             'means the figure\'s written precision leaves its gap on both sides of the 1 percent line, or the source has no current figure for that year.</p>')
rows_html = []
for gid in GROUP_ORDER + ['ALL']:
    g = s1.get(gid)
    if not g: continue
    rows_html.append(f'<tr><td>{"All of the above" if gid == "ALL" else E(g["label"])}</td>' + ''.join(cell(g['size'][o]) for o in OUTS) +
                     f'<td class="n">{pc(g.get("median_abs_gap_not_matching_current"))}</td></tr>')
parts.append(table(['Figure', 'More than 1% above', 'More than 1% below', 'Within 1%', 'Cannot tell', 'Median absolute gap, figures not matching the current release'], rows_html))
line = [(gid, x) for gid in GROUP_ORDER for x in ((s1.get(gid) or {}).get('on_the_line') or [])]
if line:
    bits = []
    for gid, x in line:
        oc = x['outcomes']
        bits.append(f'{n(x["rows"])} {E(s1[gid]["label"].split(",")[0])} figures for {E(x.get("label") or x["item"])}, {x["years"][0]} to {x["years"][1]}, sit on the 1 percent '
                    'line (each gap is -1.0000 percent). Their outcome turns on the ninth digit: ' +
                    ', '.join(f'{n(c)} {OUT_WORD[o]}' for o, c in sorted(oc.items(), key=lambda kv: -kv[1])) + '.')
    parts.append('<p class="bench-note">Defined after the data: ' + ' '.join(bits) + '</p>')
if un.get('written_whole'):
    wz = un.get('written_whole_size') or {}; uw = (un.get('sensitivity') or {}).get('wrong_year') or {}
    low = max(((s1.get(g) or {}).get('sensitivity') or {}).get('wrong_year', {}).get('share') or 0 for g in ('WB-POP', 'WB-GDP', 'UIS-LE'))
    top = (un.get('sensitivity') or {}).get('consistent_top_country') or {}
    parts.append(f'<p>Most unemployment figures in this frame are written as whole percentages ({n(un["written_whole"])} of {n(un["rows"])}, a count defined after the '
                 f'data). A match there is a match to the nearest point, and the size reading cannot tell for {n(wz.get("CANNOT_TELL", 0))} of them. Defined after the '
                 'data: read against every release\'s value for the same country two years earlier and two years later, years they do not describe, unemployment '
                 f'figures match some release in {100 * (uw.get("share") or 0):.0f} percent of tries, and whole-percent figures in {100 * (uw.get("whole_share") or 0):.0f} '
                 f'percent. For population, GDP and life expectancy the same test matches in {100 * low:.1f} percent of tries or fewer. So a matching release on an '
                 'unemployment row says little about where the figure came from.' +
                 (f' {n(top["rows"])} of the {n(top["of"])} unemployment figures within 1 percent are for {E(top.get("label") or top["item"])}.' if top.get('rows') else '') + '</p>')
ph = [(gid, s1[gid]['post_hoc_alias']) for gid in GROUP_ORDER if s1.get(gid, {}).get('post_hoc_alias')]
if ph:
    rowsph = [x for _, p in ph for x in p['rows']]
    codes = sorted({(x['code'], x['alias']) for x in rowsph})
    n_old = sum(1 for x in rowsph if x['bin_under_alias'] == 'MATCHES_AN_OLDER_RELEASE'); n_cur = sum(1 for x in rowsph if x['bin_under_alias'] == 'MATCHES_CURRENT')
    hits = n_old + n_cur; what = 'an older World Bank release' if n_cur == 0 else ('the current World Bank release' if n_old == 0 else 'a World Bank release')
    parts.append(f'<p>Defined after the data: the {n(len(rowsph))} World Bank figures that returned nothing are held under codes the World Bank does not use for that territory ('
                 + ', '.join(f'{E(a)} where the World Bank uses {E(b)}' for a, b in codes) +
                 f'). Read under the World Bank\'s codes, {("all " + n(hits)) if hits == len(rowsph) else (n(hits) + " of them")} match {what}. The bins above are unchanged.</p>')

parts.append('<h3>The value a plain query returns</h3>')
parts.append('<p>When a country holds several figures for one property, a plain query to Wikidata returns the best-ranked ones. '
             'These are the values a plain query returns. The same bins, for those figures only:</p>')
rows_html = []
for gid in GROUP_ORDER:
    g = s1.get(gid)
    if not g: continue
    d = g['defaults']
    rows_html.append(f'<tr><td>{E(g["label"])}</td><td class="n">{n(d["rows"])}<br><span class="srckind">{n(d["countries"])} countries and territories</span></td>' +
                     ''.join(cell(d['bins'][b]) for b in BINS) + '</tr>')
parts.append(table(['Figure', 'Figures read'] + [BIN_WORD[b] for b in BINS], rows_html))

parts.append('<h3>Largest gaps among those values</h3>')
parts.append('<p>For each figure, the ten best-ranked values with the largest gap to the source\'s current figure, and any other beyond 10 percent. '
             'Every row was read a second time, from the Wikidata Query Service and from the source\'s own record, before it was listed. Each country links '
             'to its statements for that property in Wikidata, each current figure to the source\'s own record, and each release to that archived release.</p>')
def notable_row(g, r):
    rel = r.get('newest_release')
    if rel and r.get('release_url'): relc = f'<a href="{E(r["release_url"])}">{E(rel)}</a>'
    elif r['bin'] == 'MATCHES_NO_RELEASE_READ' and r['group'].startswith('UIS'):
        relc = 'No UIS release kept (the API starts September 2024).'
        if r.get('wb_newest') and r.get('wb_release_url'): relc += f' Equals World Bank release <a href="{E(r["wb_release_url"])}">{E(r["wb_newest"])}</a>.'
    elif r['bin'] == 'MATCHES_NO_RELEASE_READ': relc = 'No release read'
    elif r['bin'] == 'MATCHES_CURRENT': relc = 'Current release'
    else: relc = ''
    if r.get('reread_agrees') is False: relc += f' <span class="srckind">(a second read of this row disagrees, see the <a href="{FEED}">data feed</a>)</span>'
    cur = '' if r['current'] is None else (n(int(round(r['current']))) if abs(r['current']) >= 1000 else f'{r["current"]:g}')
    gap = '' if r['gap'] is None else f'{100 * r["gap"]:+.1f}%'
    return (f'<tr><td><a href="{E(r["wikidata_url"])}">{E(r["name"])}</a></td><td>{E(g["label"])}</td><td class="n">{r["year"]}</td>'
            f'<td class="n">{E(written(r["cited"]))}</td><td class="n"><a href="{E(r["source_url"])}">{cur}</a></td><td class="n">{gap}</td><td>{relc}</td></tr>')
THEAD = ['Country', 'Figure', 'Year', 'As cited in Wikidata', 'Source now', 'Gap', 'Newest release that carried it']
rows_html, more_html = [], []
for gid in GROUP_ORDER:
    g = s1.get(gid)
    if not g: continue
    for i, r in enumerate(g.get('notable', [])):
        (rows_html if i < 10 else more_html).append(notable_row(g, r))
parts.append(table(THEAD, rows_html))
if more_html:
    parts.append('<details><summary>Every other best-ranked figure with a gap beyond 10 percent</summary>' + table(THEAD, more_html) + '</details>')
parts.append('<p class="bench-note">Gap is the figure as cited minus the source\'s current figure, as a percentage of the current figure. The source\'s '
             'figure for a past year changes when the source revises it. A row names the newest release we read that carried the cited value. For a '
             'whole-percent unemployment figure, that release is one of many that carried the same value to the nearest point.</p>')

years = sorted({y for gid in GROUP_ORDER if gid in s1 for y in (s1[gid].get('newest_matching_release_by_year') or {})})
if years:
    parts.append('<h3>Which release the older figures match</h3>')
    parts.append('<p>For figures that match an older release, the year of the newest release that carried the value.</p>')
    hdr = [E(s1[g]['label']) for g in GROUP_ORDER if g in s1]
    body = [f'<tr><td>{y}</td>' + ''.join(f'<td class="n">{n((s1[g].get("newest_matching_release_by_year") or {}).get(y, 0)) if (s1[g].get("newest_matching_release_by_year") or {}).get(y) else ""}</td>'
                                         for g in GROUP_ORDER if g in s1) + '</tr>' for y in years]
    parts.append(table(['Release year'] + hdr, body, small=True))

aside = {}
for gid in GROUP_ORDER:
    for kk, v in ((s1.get(gid) or {}).get('set_aside') or {}).items(): aside[kk] = aside.get(kk, 0) + v
if aside:
    parts.append('<p class="bench-note">Set aside before scoring and counted: ' + ', '.join(f'{E(kk)} {n(v)}' for kk, v in sorted(aside.items(), key=lambda x: -x[1])) +
                 '. Statements come from the live Wikidata API. Two statements with the same country, year and value count once.</p>')
kg = L['known_good']; hp = (L.get('hand_check_plan') or {}).get('rows') or []
parts.append('<p class="bench-note">Before the real figures, planted figures ran through the same rules and read as the plan requires '
             f'({"passed" if kg["s1"] else "FAILED"}). Our pull of the 29 World Bank releases a first scout read on 9 November equals the scout\'s files '
             f'value for value ({"passed" if kg["s1_scout"] else "FAILED"}). Ten figures drawn with seed 11 across all six figures were opened in the live '
             'Wikidata entity record and in the source\'s own record for the release their bin names: '
             f'{sum(1 for h in hp if h["all_agree"])} of {len(hp)} agree on value, year, rank, reference, current value and bin. A first run of that check '
             'read the Wikidata Query Service instead and drew from all figures at once, and the plan notes the change.</p>')


# ------------------------------------------------------------------------------------------------ section 2
figs = {f['id']: f for f in L['section2']}
def quote_html(f):
    q = f['quote'] or ''; foc = f.get('focus')
    if foc and foc in q: return E(q).replace(E(foc), f'<b>{E(foc)}</b>', 1)
    return E(q)
def band_words(f):
    lo, hi = (f.get('band') or [None, None])[0], (f.get('band') or [None, None])[1]; w = f.get('word')
    if w == 'over': return f'above {fbig(lo)}'
    if w in ('plus', 'counting'): return f'{fbig(lo)} or more'
    return f'{fbig(lo)} to {fbig(hi)}'

parts.append('<h2>The Foundation\'s numbers against its own data</h2>')
parts.append('<p>The Wikimedia Foundation states its reach on its homepage, on its projects page and in its 2024-2025 annual report, and it files EU user '
             'numbers under the Digital Services Act. It also publishes data that can check such figures: the Wikimedia Analytics API, under CC0, and each '
             'wiki\'s site statistics. We quote each figure as read today and look up how long it has stood in the Wayback Machine. The pages do not say which '
             'traffic or which edits a figure counts, so we read each one against the plausible definitions side by side: human traffic or all agents, '
             'Wikipedia or all projects, edits with or without bots. When those definitions disagree about the stated figure, the outcome is cannot tell.</p>')
mom = L.get('moments') or {}
fc = mom.get('report_first_capture')
parts.append('<p>Present-tense figures on the homepage and projects page are read against the last 12 complete months. Annual report rates are read '
             'against the report\'s own year, July 2024 to June 2025. The annual report does not say which moment its counts describe, so, defined after the '
             'data, we read them at three moments: at the end of the report\'s year, just before the report page\'s first capture in the Wayback Machine'
             + (f' ({E(date_ts(fc))})' if fc else '') + ', and today. Other counts are read today. "Nearly X" is read as 90 to 100 percent of X, "over X" and '
             '"more than X" as anything above X, "X+" and "X and counting" as X or more, and a plain figure as itself to half a unit of its last written digit. '
             'A figure card is a lead-in, a large number and a caption shown together on the page, and we quote it as one line.</p>')
rows_html = []
for f in L['section2']:
    wb = f.get('wayback') or {}; since = ''
    if wb.get('first_with'):
        same = bool(wb.get('last_without')) and wb['last_without'][:8] == wb['first_with'][:8]
        since = f'First in a capture of {wb_link(wb["first_with"], f["url"], same)}'
        if wb.get('last_without'): since += f', not in the capture of {wb_link(wb["last_without"], f["url"], same)}'
        if (wb.get('note') or '').startswith('the phrase is missing'): since += '. It is missing from a later capture, so this is not a start date'
        elif (wb.get('note') or '').startswith('in the earliest'): since = f'In the first capture of this page, {wb_link(wb["first_with"], f["url"])}, and in every capture checked since'
    elif wb.get('note'): since = E(wb['note'])
    where = f'<a href="{E(f["url"])}">{E(f["page_name"])}</a>' + (', figure card' if f.get('card') else '') + f', read {E(short_date(f["read"] or ""))}'
    rows_html.append(f'<tr><td><span class="quote">&ldquo;{quote_html(f)}&rdquo;</span><br><span class="srckind">{where}</span></td><td>{since}</td>'
                     f'<td>{E(OUT_WORD.get(f["outcome"], f["outcome"]))}</td></tr>')
parts.append(table(['Stated figure', 'How long it has stood', 'Outcome'], rows_html))

ya, bc = mom.get('year_end') or {}, mom.get('before_first_capture') or {}
if ya and bc:
    parts.append(f'<p>Defined after the data: the annual report\'s counts read differently by moment. At the end of the report\'s year, 30 June 2025, Wikipedia held '
                 f'{n(ya["A2"])} articles and Commons {n(ya["C1"])} files, both below the report\'s "66 million" and "135 million". Just before the report page was first '
                 f'captured, Wikipedia held {n(bc["A2"])} articles and Commons {n(bc["C1"])} files, both above them. So the outcome for "66 million Wikipedia articles", '
                 '"More than 66 million articles" and "135 million freely usable media files" is cannot tell. "300+ Languages on Wikipedia" holds at every moment. '
                 'The past counts come from the Commons statistics table as it stood at each moment. A bot posts that table from each wiki\'s site statistics '
                 f'(revisions of <a href="{E(ya["url"])}">30 June 2025</a> and <a href="{E(bc["url"])}">{E(short_date(bc["revision_time"]))}</a>, CC0).</p>')

parts.append('<h3>Each definition, side by side</h3>')
rows_html = []
for f in L['section2']:
    if not f.get('definitions'): continue
    kind = 'views' if 'views' in f['id'] else ('edits' if 'edits' in f['id'] else 'count')
    rows_html.append(f'<tr><td colspan="5"><span class="quote">&ldquo;{quote_html(f)}&rdquo;</span> <span class="srckind">Stated band {E(band_words(f))}, {E(WIN.get(f["window"], f["window"]))}. '
                     f'Outcome: {E(OUT_WORD.get(f["outcome"], f["outcome"]))}.</span></td></tr>')
    for d in f['definitions']:
        if d.get('lo') is None: deliv = 'no data'
        elif d['lo'] == d['hi']: deliv = big(d['lo'], kind)
        else: deliv = f'{big(d["lo"], kind)} to {big(d["hi"], kind)}, mean {big(d["mean"], kind)}'
        name = E(d['name'])
        if d.get('source_url'): name += f' <span class="srckind">(<a href="{E(d["source_url"])}">{E(d["source"])}</a>)</span>'
        if d.get('in_outcome') is False: name += ' <span class="srckind">(all projects, not the scope the figure names, shown for reference)</span>'
        pf = d.get('pre_first_capture') or {}
        rows_html.append(f'<tr><td>{name}</td><td class="n">{deliv}</td><td>{E(OUT_WORD.get(d["outcome"], d["outcome"]))}</td>'
                         f'<td>{E(OUT_WORD.get(d["mean_reading"], d["mean_reading"])) if not d.get("moment") else ""}</td>'
                         f'<td class="n">{big(pf["mean"], kind) if pf.get("mean") is not None else ""}</td></tr>')
parts.append(table(['Definition', 'Delivered (monthly low to high)', 'Reading', 'Reading on the mean', 'Mean of the 12 months before it first appeared'], rows_html))
parts.append('<p class="bench-note">Reading: above means the stated band lies wholly above every delivered month, below means wholly below, consistent '
             'means every delivered month lies inside the stated band, and cannot tell means they overlap. The reading on the mean, a second ruler fixed '
             'before the data, places the 12-month mean against the band. The last column, for homepage rates, is descriptive and has no outcome. The two view '
             'figures name Wikipedia, so only the Wikipedia definitions decide their outcome (defined after the data). Views come from the Analytics API page '
             'view counts, edits from its edit counts divided by the minutes in each month, articles and files from each wiki\'s site statistics.</p>')

vol = [f for f in L['section2'] if f.get('bounds')]
vb = L.get('volunteer_bounds') or {}
if vol and vb:
    parts.append('<h3>Volunteers</h3>')
    by_page = {}
    for f in vol: by_page.setdefault(f['page_name'], []).append(f'&ldquo;{E(f["quote"])}&rdquo;')
    qs = ' '.join(f'The {E(pg.replace("Wikimedia Foundation ", ""))} states {" and ".join(q)}' + ('' if q[-1].endswith('.&rdquo;') else '.') for pg, q in by_page.items())
    parts.append(f'<p>{qs} The Analytics API counts registered editors per wiki only. It has no count of people deduplicated across wikis, so the outcome for '
                 'every volunteers figure is cannot tell. What the data do allow is a bound: a deduplicated count cannot be smaller than the largest single wiki '
                 'that month, and cannot be larger than the sum over wikis, which counts a person once on every wiki they edit. We place the homepage\'s '
                 '"supports nearly 265,000 volunteers" against all wikis, and the three figures about Wikipedia against Wikipedias only.</p>')
    rows_html = []
    for w, wl in (('latest12', 'Last 12 months (homepage figures)'), ('fy2425', 'July 2024 to June 2025 (annual report figures)')):
        for sc, sl in (('all_wikis', 'All open wikis'), ('wikipedias', 'Wikipedias only')):
            for lv in ('1+', '5+'):
                x = vb[w][sc][lv]
                rows_html.append(f'<tr><td>{wl}</td><td>{sl}</td><td>{lv} edits in the month</td><td class="n">{n(int(round(x["lower_mean"])))}</td>'
                                 f'<td class="n">{n(int(round(x["upper_mean"])))}</td></tr>')
    parts.append(table(['Window', 'Scope', 'Registered editors with', 'Lower bound, monthly mean', 'Upper bound, monthly mean'], rows_html))
    p1 = {f['placement']['one_plus'] for f in vol}; p5 = {f['placement']['five_plus'] for f in vol}
    if p1 == {'CANNOT_TELL'} and p5 == {'ABOVE'}:
        parts.append('<p>Defined after the data: with one or more edits in a month, each stated figure overlaps the range between its scope\'s two bounds, so the '
                     'data cannot tell. With five or more edits, each stated figure lies above the upper bound.</p>')
    parts.append('<p class="bench-note">Registered editors without bots, all pages, monthly means over each window. The public MediaWiki history dumps list a global '
                 f'user id (event_user_central_id), which would allow one count per person. We have not read them. Monthly values are in the <a href="{FEED}">data feed</a>.</p>')

dsa = L['dsa']
parts.append('<h3>EU user numbers under the Digital Services Act</h3>')
parts.append('<p>The Foundation\'s DSA page states its method: EU unique devices, averaged over six months, divided by 2.4 devices per person. EU-only device '
             'counts are not published, so the figures themselves cannot be rebuilt from public data, and the outcome for them is cannot tell. These checks '
             'are the ones the public data allow.</p>')
r = dsa['rounding']; off = r['not_whole_thousands']
parts.append(f'<p>Rounding. The page says: &ldquo;{E(r["statement"])}&rdquo;. Of the {n(r["cells"])} figures in its two tables, '
             + (f'{word(len(off))} {"is" if len(off) == 1 else "are"} not a whole thousand: ' + ', '.join(f'{E(o["row"])}, {E(o["window"])}, {n(o["value"])}' for o in off) + '.'
                if off else 'every one is a whole thousand.') + '</p>')
for h in dsa['harmonised']:
    if h.get('total') is None: parts.append(f'<p>{E(h["title"])}: {E(h.get("reason", ""))}.</p>'); continue
    cf = h.get('cross_filing') or {}
    a_, z_ = h['period'].split('/'); a_ = D.date.fromisoformat(a_); z_ = D.date.fromisoformat(z_)
    per = f'{a_.strftime("%B")} to {z_.strftime("%B %Y")}' if a_.year == z_.year else f'{a_.strftime("%B %Y")} to {z_.strftime("%B %Y")}'
    eq = 'equal (difference 0)' if h['difference'] == 0 else f'{n(int(h["difference"]))} apart'
    parts.append(f'<p>Harmonised report for Wikipedia, {E(per)}. The EU total, {n(int(h["total"]))}, against the sum of its {h["member_rows"]} member-state rows, '
                 f'{n(int(h["member_sum"]))}: {eq}, {E(OUT_WORD.get(h["outcome"], h["outcome"]))} (rounding to the nearest thousand allows up to 13,500). '
                 + (f'Its member-state rows equal the DSA page\'s figures for the same half-year in {cf["equal"]} of {h["member_rows"]}.' if cf else '') +
                 f' <a href="{E(h.get("url") or "")}">Report file</a>.</p>')
bd = dsa['bound']
if bd:
    wins, fams = [], []
    for x in bd:
        if x['window'] not in wins: wins.append(x['window'])
        if x['family'] not in fams: fams.append(x['family'])
    get = {(x['family'], x['window']): x for x in bd}; body = []
    for fm in fams:
        row = f'<tr><td>{E(fm)}</td>'
        for w in wins:
            x = get.get((fm, w))
            if not x: row += '<td></td>'; continue
            row += '<td class="n">no data</td>' if x['outcome'] == 'CANNOT_TELL' else f'<td class="n">{pc(x["implied_eu_share"], 0)}{" (above)" if x["outcome"] == "ABOVE" else ""}</td>'
        body.append(row + '</tr>')
    parts.append('<p>Bound. A family\'s stated EU devices (the figure times 2.4) cannot exceed its global unique devices for the same months. The table gives '
                 'the stated EU devices as a share of the global devices. A share above 100% would read above the bound.</p>')
    parts.append(table(['Project family'] + [E(w) for w in wins], body))
    n_above = sum(1 for x in bd if x['outcome'] == 'ABOVE'); n_ct = sum(1 for x in bd if x['outcome'] == 'CANNOT_TELL')
    wp = [x['implied_eu_share'] for x in bd if x['family'] == 'Wikipedia' and 'implied_eu_share' in x]
    parts.append('<p class="bench-note">' + ('Every family and window is within the bound.' if not n_above and not n_ct else
                 f'{n(n_above)} family-windows read above the bound and {n(n_ct)} cannot be read.') +
                 (f' For Wikipedia the stated EU devices are {pc(min(wp), 0)} to {pc(max(wp), 0)} of global unique devices.' if wp else '') +
                 ' Global unique devices: Analytics API, unique devices per project family, all sites, monthly, averaged over each window.</p>')
reps = [x for x in dsa['repeats'] if x['half_years'] >= 3]; twice = [x for x in dsa['repeats'] if x['half_years'] == 2]
if reps:
    fr = dsa.get('finland_revision') or {}
    txt = ' '.join(f'{E(x["member_state"])} reads {n(x["value"])} in each of {word(x["half_years"])} half-years in a row ({E(x["windows"][0])} to {E(x["windows"][1])}).' for x in reps)
    txt += ' A first scout reading saw this repeat before the plan was written.'
    for c in (fr.get('changes') or []):
        txt += (f' The DSA page\'s <a href="{E(fr["diff_url"])}">revision of {E(long_date(fr["timestamp"]))}</a> changed its {E(c["window"])} figure from '
                f'{n(c["before"])} to {n(c["after"])}.')
    if fr.get('note'): txt += f' The page\'s own note on that column reads: &ldquo;{E(fr["note"])}&rdquo;'
    if twice: txt += ' ' + ' '.join(f'{E(x["member_state"])} repeats once ({n(x["value"])}).' for x in twice)
    parts.append(f'<p>Repeats. {txt}</p>')

parts.append('<p class="meta">Named here and want to answer a row? <a href="/respond?u=wiki-all">Respond</a></p>')
parts.append('<p class="meta">Plan, code and trend history for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/wiki">wiki</a>. '
             'The plan was committed before any comparison on this page was read. A first scout reading of population, of the homepage figures and of the DSA '
             'member-state table (the Finland repeat and the Wikispecies figure that is not a whole thousand) came before it, and the plan says so. '
             f'Every number on this page comes from the reading of {E(read_stamp(L["updated"]))}. The desk reads its sources again about once a week and puts '
             f'each new reading in the data feed, <a href="{FEED}">{FEED}</a>, so the feed can be newer than this page.</p>')
parts.append('<p class="meta">Data read from: <a href="https://www.wikidata.org">Wikidata</a> (CC0) &middot; <a href="https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/">Wikimedia Analytics API</a> (CC0) '
             '&middot; Wikimedia site statistics and the <a href="https://commons.wikimedia.org/wiki/Data:Wikipedia_statistics/data.tab">Commons statistics table</a> (CC0) '
             '&middot; <a href="https://data.worldbank.org">World Bank World Development Indicators</a> and <a href="https://databank.worldbank.org/source/wdi-database-archives-(beta)">WDI Database Archives</a> (CC BY 4.0) '
             '&middot; <a href="https://api.uis.unesco.org/api/public/documentation/">UNESCO Institute for Statistics data API</a> (CC BY-SA 4.0) '
             '&middot; <a href="https://wikimediafoundation.org">Wikimedia Foundation</a> pages and <a href="https://foundation.wikimedia.org/wiki/Legal:EU_DSA_Userbase_Statistics">DSA filings</a> (CC BY-SA 4.0) '
             f'&middot; <a href="https://web.archive.org">Internet Archive Wayback Machine</a>. Wikidata and Wikimedia data courtesy of the Wikimedia Foundation. Read {E(read_stamp(L["updated"]))}.</p>')
parts.append('<section id="replies" data-prefix="wiki"></section><script src="/replies.js" defer></script>')

main = (f'<main class="wrap"><section id="hl-slot" class="hl-slot hl"><div class="hl-big">{hl_big}</div><p class="hl-line">{E(hl_line)}</p></section>'
        '<p class="meta crumb">Division: <a href="/hermes">HERMES</a></p>\n' + '\n'.join(parts) + '</main>')

# ------------------------------------------------------------------------------------------------ chrome from launch.html
src = open(SRC).read()
head, rest = src.split('<body>', 1)
old_title = re.search(r'<title>(.*?)</title>', head).group(1)
old_desc = re.search(r'<meta name="description" content="(.*?)">', head).group(1)
head = head.replace(old_title, TITLE).replace(old_desc, html.escape(DESC, quote=True))
head = head.replace('https://indahl.ai/launch/live.json', 'https://indahl.ai/wiki/live.json').replace('https://indahl.ai/launch', 'https://indahl.ai/wiki')
head = head.replace('"name": "LAUNCH"', '"name": "WIKI"')
head = re.sub(r'"dateModified": "\d{4}-\d{2}-\d{2}"', '"dateModified": "' + time.strftime('%Y-%m-%d', time.gmtime()) + '"', head)
head = head.replace(html.escape(old_desc, quote=False), html.escape(DESC, quote=True))
head = head.replace(old_desc.replace('&#x27;', "'"), DESC.replace('"', '\\"'))      # JSON-LD carries the description unescaped
hdr = rest.split('<section class="hero slim">', 1)[0]
foot = rest.split('</main>', 1)[1]
hero = '<section class="hero slim"><div class="wrap"><h1><b class="ac">WIKI</b> &middot; Figures Against Their Source</h1></div></section>\n'
page = head + '<body>' + hdr + hero + main + foot
open(os.path.join(H, 'wiki.html'), 'w').write(page)
print('wiki.html written,', len(page), 'chars')
