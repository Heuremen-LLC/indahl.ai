#!/usr/bin/env python3
"""RANK page body: rank_body.html from data/rank.json. build_site.py wraps it with the shared header, nav, division line and footer.
Copy rules: plain sentences, no semicolons, no digits in headings, no adjectives about schools or US News, no cause named. Heuremen LLC."""
import json, os, html, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
D = json.load(open('data/rank.json', encoding='utf-8'))
CK = json.load(open('data/checks.json', encoding='utf-8'))['checks'] if os.path.exists('data/checks.json') else []
CASES = json.load(open('public/corrections/cases.json', encoding='utf-8')) if os.path.exists('public/corrections/cases.json') else None
SRCS = json.load(open('data/sources.json', encoding='utf-8')) if os.path.exists('data/sources.json') else {}
HSP = json.load(open('public/hs_public.json', encoding='utf-8')) if os.path.exists('public/hs_public.json') else []
NJC = json.load(open('data/checks_nj.json', encoding='utf-8')) if os.path.exists('data/checks_nj.json') else {'checks': [], 'participation': [], 'school_day': []}
for c in NJC['checks']:
    if c['list'] == 'nj_k8': c['list'] = 'nj_k8'
CK = CK + NJC['checks']
GRADC = json.load(open('data/checks_grad.json', encoding='utf-8')) if os.path.exists('data/checks_grad.json') else {'checks': []}
CK = CK + GRADC['checks']
CLAIMS = json.load(open('data/claims_scored.json', encoding='utf-8')) if os.path.exists('data/claims_scored.json') else []
DONE = sorted({c['list'] for c in CK} | ({'nj_elem', 'nj_middle'} if any(c['list'] == 'nj_k8' for c in CK) else set()))
e = html.escape

def pct(w): return w.replace('%', ' percent')
def weights_line(l):
    parts = [f'{e(a)} {e(pct(w))}' for a, w in l['weights']]
    s = '<p class="bench-note">Indicators and weights as US News states them: ' + ', '.join(parts) + '.'
    if l.get('weights_note'): s += ' ' + e(l['weights_note'])
    return s + f' <a href="{e(l["method_url"])}">US News methodology</a>.</p>'

def resp(slug, label='Respond'): return f'<a href="/respond?u=rank-{e(slug)}">{label}</a>'


def same_school(a, b):
    import re
    norm = lambda x: re.sub(r'[^a-z]', '', x.lower().replace('university of pennsylvania (carey)', 'university of pennsylvania').replace('stem', 'stem'))
    a2, b2 = norm(a), norm(b)
    return a2 == b2 or a2.startswith(b2) or b2.startswith(a2) or a2.replace('law', '') == b2

READ = {'MATCH': 'match', 'MISMATCH': 'mismatch', 'CANNOT_TELL': 'cannot tell'}
WHY = {'year': 'year not printed or not the same', 'not_found': 'public figure not found', 'not_printed': 'not printed by US News or missing in the public file',
       'suppressed': 'suppressed by the state', 'floor_or_range_unsettled': 'binned figure does not settle it', 'definition': 'definition differs', 'paid_tier': 'paid tier, not read', '': ''}
RECOMPUTE = {
 'hs': 'College readiness and college curriculum breadth (40 percent together) use AP and IB exam results for each school, which are not published per school. State assessment performance (20 percent) is measured against what US News predicts for a school with its demographic characteristics.',
 'nu': 'Peer assessment (20 percent) is a survey US News runs. Graduation performance (10 percent) and Pell graduation performance (5.5 percent) are measured against rates US News predicts. Faculty salaries and spending per student come from what schools report.',
 'nlac': 'Peer assessment (20 percent) is a survey US News runs. Graduation performance (10 percent) and Pell graduation performance (5.5 percent) are measured against rates US News predicts. Faculty salaries and spending per student come from what schools report.',
 'elem': 'Mathematics and reading performance (50 percent) is measured against what a model US News fits would expect.', 'mba': 'Peer and recruiter assessments (25 percent) are surveys US News runs.', 'law': 'Peer and lawyers and judges assessments (25 percent) are surveys US News runs.',
 'eng': 'Peer and recruiter assessments (25 percent) are surveys US News runs.', 'edu': 'Peer and educational professionals assessments (25 percent) are surveys US News runs.',
 'med': 'Research activity per faculty member and faculty resources use counts that schools report to US News, which are not published per school in full.'}

GRAD_SHOWN = GRADC.get('shown_text', {})

def checks_section(l):
    k = l['key']
    if k in RECOMPUTE or k in ('nj_hs', 'nj_col', 'nj_elem', 'nj_middle'):
        k0 = {'nj_hs': 'hs', 'nj_col': 'nu', 'nj_elem': 'elem', 'nj_middle': 'elem'}.get(k, k)
        if k0 not in RECOMPUTE: RECOMPUTE[k0] = 'Mathematics and reading performance (50 percent) is measured against what a model US News fits would expect.'
    if k in RECOMPUTE or k in ('nj_hs', 'nj_col', 'nj_elem', 'nj_middle'):
        out.append(f'<p class="bench-note">Can the order be worked again from public inputs? Cannot tell. {e(RECOMPUTE[{"nj_hs": "hs", "nj_col": "nu", "nj_elem": "elem", "nj_middle": "elem"}.get(k, k)])}</p>')
    if k == 'nj_elem': return
    if k == 'nj_middle': k = 'nj_k8'
    rows = [c for c in CK if c['list'] == k and c['outcome'] != 'DISPLAY']
    if not rows: return
    out.append(f'<h3>Figures checked</h3>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>Figure</th><th>US News prints</th><th>Year US News names</th><th>Public record</th><th>Year</th><th>Reading</th><th>Note</th></tr></thead><tbody>')
    for c in rows:
        rd = READ[c['outcome']] + (f' ({WHY.get(c["reason"], c["reason"])})' if c['outcome'] == 'CANNOT_TELL' else '')
        pub = c['pub'] if c['pub'] not in (None, '') else ''
        if pub and pub.replace('.', '').isdigit() and '.' in pub and len(pub.split('.')[1]) > 2: pub = f'{float(pub):.2f}'
        note = e(c['note'])
        m = __import__('re').search(r'https?://\S+', c.get('source') or '')
        if m: note += f' <a href="{e(m.group(0).rstrip(")"))}">Source</a>.'
        elif c.get('source'): note += ' Source: ' + e(c['source']) + '.'
        out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(c['school']), e(c['field']), e(str(c['usn'] or '')), e(str(c['usn_year'] or 'not printed')), e(str(pub)), e(str(c['pub_year'] or '')), e(rd), note)) + '</tr>')
    out.append('</tbody></table></div>')
    disp = [c for c in CK if c['list'] == k and c['outcome'] == 'DISPLAY']
    if disp and k in GRAD_SHOWN:
        out.append(f'<h3>Shown beside, not scored</h3><p class="bench-note">{GRAD_SHOWN[k]}</p>')
        out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>Figure</th><th>US News</th><th>Public record</th><th>Year</th><th>Note</th></tr></thead><tbody>')
        for c in disp:
            note = e(c['note'])
            m = __import__('re').search(r'https?://\S+', c.get('source') or '')
            if m: note += f' <a href="{e(m.group(0).rstrip(")"))}">Source</a>.'
            out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(c['school']), e(c['field']), e(str(c['usn'] or '')), e(str(c['pub'] or 'not found')), e(str(c['pub_year'] or '')), note)) + '</tr>')
        out.append('</tbody></table></div>')
        return
    if disp:
        out.append('<p class="bench-note">Shown after the data and not scored: the same figures set beside each college&rsquo;s Common Data Set for 2025-26, the latest each college has published. US News prints no year for these figures, so they are not scored. Percents are worked from the counts in the Common Data Set.</p><ul class="bench-note">')
        for c in disp: out.append(f'<li>{e(c["school"])}: {e(c["note"]).replace("; ", ". ")}.</li>')
        out.append('</ul>')

def sources_table(l):
    rows = SRCS.get(l['key'])
    if not rows: return
    out.append('<div class="tw"><table class="bench"><thead><tr><th>Indicator</th><th>Weight</th><th>Where the data comes from</th><th>Public</th></tr></thead><tbody>')
    for ind, w, src, pub in rows:
        out.append(f'<tr><td>{e(ind)}</td><td>{e(pct(w))}</td><td>{e(src)}</td><td>{e(pub)}</td></tr>')
    out.append('</tbody></table></div>')
    out.append('<p class="bench-note">Public means the source publishes the figure for each school. Public inputs, US News calculation means the inputs are published and the scoring is US News&rsquo;s own. Not public means a survey US News runs, a model US News fits, licensed data, or figures schools report to US News that are not published for each school.</p>')

out = []
out.append('<h2>US News education rankings, set against the public record</h2>')
out.append('<p>US News &amp; World Report publishes rankings of schools and colleges. For each list it states the indicators it uses and the weight of each. '
           'This desk records the top of each list in the current edition, with the list and the stated method linked. '
           'It then sets each figure US News prints for a school against the same figure in the public record, such as a state report card, the federal school and college data, '
           'or the school&rsquo;s own published report, and checks whether the order follows from the stated method where the method can be worked again from public inputs.</p>')
out.append('<p>Each figure reads match, mismatch or cannot tell, with the year used on each side. Match means the public figure, rounded to the precision US News prints, is the same. '
           'Cannot tell is given with its reason, such as a year that is not printed, a figure the state suppresses, or a figure not found. The rules were fixed and committed before any figure was compared. '
           'Every list on this page is checked: high schools, National Universities, National Liberal Arts Colleges, the law, business, engineering, education and medical school lists, and the New Jersey lists. '
           'On the graduate school lists, figures US News shows only to paying subscribers were not read and read cannot tell (paid tier, not read).</p>')
SUM = Counter((c['list'], c['outcome']) for c in CK if c['outcome'] != 'DISPLAY')
def tally(k):
    m, x, t = SUM[(k, 'MATCH')], SUM[(k, 'MISMATCH')], SUM[(k, 'CANNOT_TELL')]
    return f'{m} match, {x} mismatch, {t} cannot tell'
NAMES = {'hs': 'High schools', 'nu': 'National Universities', 'nlac': 'National Liberal Arts Colleges', 'law': 'Law schools', 'mba': 'Business schools', 'eng': 'Engineering schools', 'edu': 'Education schools', 'med': 'Medical schools (Tier 1)', 'nj_hs': 'New Jersey high schools', 'nj_k8': 'New Jersey elementary and middle schools', 'nj_col': 'New Jersey colleges'}
if CK:
    out.append('<p>Figures checked so far: ' + ', '.join(f'{NAMES[k]} {tally(k)}' for k in ('hs', 'nu', 'nlac', 'law', 'mba', 'eng', 'edu', 'med', 'nj_hs', 'nj_k8', 'nj_col') if k in DONE) + '.</p>')
out.append(f'<p>The lists were read on {e(D["read"])}. A rank is printed as US News prints it. A tie is marked, and a tie at the tenth place is kept whole, so a list can hold more than ten schools. '
           'Only the rank, the stated method and the figures to be checked are shown here. The full lists are on the US News pages linked below.</p>')

_nj_said = False
for l in D['lists']:
    if l.get('nj') and not _nj_said:
        _nj_said = True
        out.append('<h2>New Jersey</h2>')
        out.append('<p>The New Jersey lists below are US News state lists. A state rank is printed with the national rank US News shows beside it where it shows one. The New Jersey college page orders schools by list and then rank, so each college rank is printed with the list it comes from, and ranks from different lists are not set against each other. US News names 2023-2024 state assessment data as its source for high school test results. New Jersey publishes these results as one file per test, and the state&rsquo;s School Performance Reports summarize them. Test results here are read from the per-test files, with the report&rsquo;s figure shown beside each. This choice was made after a first run against the report figures, and both are printed.</p>')
    out.append(f'<h2>{e(l["title"])}</h2>')
    if l['scope'] == 'none':
        out.append(f'<p>US News publishes no national list of this kind. Its method page says &ldquo;{e(l["quote"])}&rdquo; and describes {e(l["quote_more"])}. '
                   f'No state list is picked here in its place. Edition {e(l["edition"])}. <a href="{e(l["list_url"])}">US News list page</a>. {resp(l["key"] + "-list")}</p>')
        out.append(weights_line(l)); sources_table(l); continue
    if l['scope'] == 'tiers':
        out.append(f'<p>US News places medical schools in tiers and gives no rank within a tier. Its method page says &ldquo;{e(l["quote"])}&rdquo; and defines &ldquo;{e(l["tier_def"])}&rdquo;. '
                   f'The schools US News shows in Tier 1 are listed in the order its page shows them, which is not a rank. Edition {e(l["edition"])}. <a href="{e(l["list_url"])}">US News list</a>.</p>')
    else:
        out.append(f'<p>Edition {e(l["edition"])}, {e(l["scope"])} list. <a href="{e(l["list_url"])}">US News list</a>.</p>' if l['scope'] != 'state page' else f'<p>Edition {e(l["edition"])}. <a href="{e(l["list_url"])}">US News New Jersey page</a>. The first ten rows the page shows are National Universities. The two last rows are the New Jersey schools ranked highest on the other lists the page shows.</p>')
    out.append(weights_line(l)); sources_table(l)
    hs = l['key'] == 'hs'; col = l['key'] in ('nu', 'nlac'); njhs = l['key'] == 'nj_hs'; njk8 = l['key'] in ('nj_elem', 'nj_middle'); njcol = l['key'] == 'nj_col'
    head = ['Rank in New Jersey' if (njhs or njk8) else 'Rank'] + (['List'] if njcol else []) + ['School', 'Place']
    if njhs: head += ['National rank', 'Graduation rate, as US News prints it', 'Enrollment, grades 9 to 12, as US News prints it']
    if njk8: head += ['District', 'Grades', 'Enrollment, as US News prints it']
    if hs: head += ['Graduation rate, as US News prints it', 'Enrollment, grades 9 to 12, as US News prints it']
    if col: head += ['Undergraduate enrollment, fall 2025, as US News prints it']
    head += ['Check', 'Answer']
    out.append('<div class="tw"><table class="bench"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>')
    for r in l['rows']:
        rk = 'Tier 1' if l['scope'] == 'tiers' else (f'{r["rank"]}' + (' (tie)' if r['tie'] else ''))
        name = f'<a href="{e(r["url"])}">{e(r["name"])}</a>' if r.get('url') else e(r['name'])
        cells = [rk] + ([e(r['list_name'])] if njcol else []) + [name, e(r['place'])]
        if njhs: cells += [e(r['national'].lstrip('#')), e(r['grad']), e(r['enrollment'])]
        if njk8: cells += [e(r['district']), e(r['grades']), e(r['enrollment'])]
        if hs: cells += [e(r['grad']), e(r['enrollment'])]
        if col: cells += [e(r['enrollment'].replace(' (fall 2025)', ''))]
        if l['key'] in DONE:
            lk = 'nj_k8' if l['key'] in ('nj_elem', 'nj_middle') else l['key']
            mine = [c for c in CK if c['list'] == lk and c['outcome'] != 'DISPLAY' and same_school(c['school'], r['name'])]
            cc = Counter(c['outcome'] for c in mine)
            r_check = f"{cc['MATCH']} match, {cc['MISMATCH']} mismatch, {cc['CANNOT_TELL']} cannot tell" if mine else 'not checked'
        else:
            r_check = r['check']
        cells += [e(r_check), resp(r['slug'])]
        out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
    out.append('</tbody></table></div>')
    checks_section(l)
    if hs: out.append('<p class="bench-note">' + e(l['data_years']) + ' US News prints a graduation rate of &ldquo;&gt; 95%&rdquo; or &ldquo;&gt; 99%&rdquo; for some schools and N/A for one. These are shown as printed.</p>')

if NJC['participation']:
    out.append('<h2>New Jersey: who is in the proficiency figure</h2>')
    out.append('<p>A proficiency figure counts the students who took the test and received a valid score. For each New Jersey school above, the state publishes a participation rate for ELA and for mathematics. '
               'The state&rsquo;s test files also have columns for students registered to test and students not tested, and for all of these schools those two columns read &ldquo;*&rdquo; (suppressed) in every row, in both years. '
               'Next to each rate is 100 minus the rate. The state does not say how students who take the alternate assessment enter the rate. No reason is given for any count.</p>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>ELA participation 2023-24</th><th>100 minus participation rate</th><th>ELA participation 2024-25</th><th>100 minus participation rate</th><th>Math participation 2023-24</th><th>100 minus participation rate</th><th>Math participation 2024-25</th><th>100 minus participation rate</th><th>Alternate assessment</th></tr></thead><tbody>')
    for r in sorted(NJC['participation'], key=lambda r: r['school']):
        f = lambda k: (r.get(k) + ' percent') if r.get(k) else 'not published'
        out.append('<tr>' + ''.join(f'<td>{e(x)}</td>' for x in (r['school'], f('ELA 2023-24'), f('ELA 2023-24 not in figure'), f('ELA 2024-25'), f('ELA 2024-25 not in figure'), f('Math 2023-24'), f('Math 2023-24 not in figure'), f('Math 2024-25'), f('Math 2024-25 not in figure'), r['alternate assessment'])) + '</tr>')
    out.append('</tbody></table></div>')
    out.append('<p class="bench-note">Source: NJ School Performance Reports database files for 2023-24 and 2024-25 (ELA and Mathematics participation and performance), and the NJSLA results files. The state does not publish, for these schools, counts of first-year English learners exempt from ELA, medical exemptions or refusals. The alternate assessment column shows, for each year, what the report prints for the school (N, * or &ldquo;Fewer then 10 students registered for DLM&rdquo;, spelled as printed).</p>')
if NJC['school_day']:
    out.append('<h2>New Jersey: the school day</h2>')
    out.append('<p>The NJ School Performance Reports print, for each school, a typical start and end time, the length of the day and the time spent in instruction. Where the school or district publishes a bell schedule or calendar, what it states is set beside them. Nothing else is said about it.</p>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>State report, 2023-24</th><th>State report, 2024-25</th><th>What the school or district publishes</th></tr></thead><tbody>')
    for r in sorted(NJC['school_day'], key=lambda r: r['school']):
        pubs = ' '.join(f'{e(str(x.get("year") or "year not printed"))}: {e(str(x.get("states") or "")[:220])} <a href="{e(str(x.get("url") or ""))}">source</a>.' for x in r['published'] if x.get('url')) or 'Nothing found in the pages read.'
        out.append(f'<tr><td>{e(r["school"])}</td><td>{e(r["spr_2023_24"])}</td><td>{e(r["spr_2024_25"])}</td><td>{pubs}</td></tr>')
    out.append('</tbody></table></div>')
if CLAIMS:
    out.append('<h2>New Jersey: what schools say about their rank</h2>')
    out.append('<p>Public statements by New Jersey schools, districts and colleges about their US News rank, quoted from their own pages, set against the lists read on 2026-11-10. '
               'A statement matches when the rank, the list and the edition it names equal the list. A statement about an edition not read, or naming no edition or list, reads cannot tell.</p>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>Published by</th><th>Statement</th><th>Date on the page</th><th>What it states</th><th>List read on 2026-11-10</th><th>Reading</th></tr></thead><tbody>')
    for c in CLAIMS:
        rd = {'MATCH': 'match', 'MISMATCH': 'mismatch', 'CANNOT_TELL': 'cannot tell'}[c['outcome']] + (f' ({c["reason"]})' if c['reason'] else '')
        rec_ = c['record'].replace(';', ' ').replace('#', 'rank ').strip()
        out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(c['school']), e(c['publisher']), '&ldquo;' + e(c['quote'][:240]) + '&rdquo; <a href="' + e(c['url']) + '">source</a>', e(str(c.get('date_on_page')) if c.get('date_on_page') not in (None, 'null', '') else 'not printed'), e(c['stated']), e(rec_), e(rd))) + '</tr>')
    out.append('</tbody></table></div>')
out.append('<h2>National Blue Ribbon awards</h2>')
out.append('<p>The US Department of Education pages for the National Blue Ribbon Schools program, including the award search and the yearly lists at the addresses tried, showed &ldquo;Page not found&rdquo; in a browser on 2026-11-10 and refused automated reads. '
           'Award years below come from state education agency releases and from the National Archives copy of the Department&rsquo;s 2018 list. '
           'None of these sources states the category of each school&rsquo;s award, so the stated criterion for that category cannot be set against the state assessment data. Each reads cannot tell.</p>')
BR = []
for sch in HSP:
    for b in (sch.get('blue_ribbon') or {}).get('official_reads') or []:
        if b.get('category') == 'not read': continue
        BR.append((sch['school'], b['year'], b['source_url'], b.get('row_or_table', '')))
if BR:
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>Award year</th><th>Category</th><th>Source</th><th>Criterion check</th></tr></thead><tbody>')
    for nm, yr, u, rowt in BR:
        out.append(f'<tr><td>{e(nm)}</td><td>{e(yr)}</td><td>not stated in the source</td><td><a href="{e(u)}">source</a></td><td>cannot tell (category not stated)</td></tr>')
    out.append('</tbody></table></div>')
out.append('<p class="bench-note">Earlier or other awards named in school or press pages, without a Department or state agency record read here, are not listed. For the other high schools in the list no award record was read.</p>')
out.append('<h2>Instructional time</h2>')
out.append('<p>None of the ten states publishes instructional minutes or days per school in the files read. The District of Columbia publishes daily school hours. Nothing is set side by side.</p>')
QUOTE = {'George Washington University': "It was the decision of U.S. News to remove GW's numerical ranking from its website until next year"}
ITEM = {'Temple University': 'Number of new entrants who provided GMAT scores', 'University of Southern California': 'Doctoral program selectivity figures, with EdD data left out and PhD data reported',
        'George Washington University': 'Share of incoming students in the top 10 percent of their high school class, 58 percent reported as 78 percent', 'University of California': 'Alumni giving rate, with pledges counted',
        'University of Wisconsin': 'Not named. The document says a discrepancy in its data', 'Emory University': 'Test scores of admitted students reported as those of enrolled students, and class rank'}
out.append('<h2>Documented cases of corrected data</h2>')
if CASES:
    out.append('<p>Cases where a school&rsquo;s own statement or report says data it gave US News was inaccurate and its US News rank was removed or withdrawn. Primary sources only, quoted. '
               'The data item is described in short, and the quote is the document&rsquo;s own words.</p>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>List and edition</th><th>Data item, as the document states it</th><th>What the document says</th><th>Date</th><th>Source</th></tr></thead><tbody>')
    for v in [v for v in CASES['verified'] if not str(v.get('rank_outcome_type', '')).startswith('computed')]:
        out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(v['school']), e(v['list'].split(' (')[0].split(';')[0]), e(next((t for k_, t in ITEM.items() if v['school'].startswith(k_)), '')), '&ldquo;' + e(QUOTE.get(v['school'], v['rank_outcome_quote'])) + '&rdquo;', e(str(v.get('date', '')).split(' (')[0].split(';')[0]), ' '.join(f'<a href="{e(u)}">source</a>' for u in (v['primary_urls'] if isinstance(v['primary_urls'], list) else [v['primary_urls']])[:2]))) + '</tr>')
    out.append('</tbody></table></div>')
    out.append('<p class="bench-note">Cases named only in news reports, or whose primary page refused our reader, are not listed until the primary document is read.</p>')
out.append('<h2>What comes next</h2>')
out.append('<p>Colleges whose Common Data Set could not be read, and graduate school pages that stopped at a challenge or a login, are added when they can be read. '
           'Each list is read again when US News publishes a new edition.</p>')
out.append('<p class="meta">Rankings, list names and method text belong to US News &amp; World Report and are quoted here only as far as each check needs, with links. '
           f'Named here and want to answer a row? Each row has an answer link. US News can answer here: {resp("usnews", "Respond")}.</p>')
out.append('<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/rank">rank</a>. The plan was committed before any figure was compared.</p>')
out.append('<section id="replies" data-prefix="rank"></section><script src="/replies.js" defer></script>')
open(sys.argv[1] if len(sys.argv) > 1 else 'rank_body.html', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('rank_body.html', sum(len(l['rows']) for l in D['lists']), 'rows')
