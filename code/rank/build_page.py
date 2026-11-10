#!/usr/bin/env python3
"""RANK page body: rank_body.html from data/rank.json. build_site.py wraps it with the shared header, nav, division line and footer.
Copy rules: plain sentences, no semicolons, no digits in headings, no adjectives about schools or US News, no cause named. Heuremen LLC."""
import json, os, html, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
D = json.load(open('data/rank.json', encoding='utf-8'))
CK = json.load(open('data/checks.json', encoding='utf-8'))['checks'] if os.path.exists('data/checks.json') else []
CASES = json.load(open('public/corrections/cases.json', encoding='utf-8')) if os.path.exists('public/corrections/cases.json') else None
HSP = json.load(open('public/hs_public.json', encoding='utf-8')) if os.path.exists('public/hs_public.json') else []
DONE = sorted({c['list'] for c in CK})
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
 'hs': 'College readiness and college curriculum breadth (40 percent together) use AP and IB exam results for each school, which are not published per school. State assessment performance and underserved student performance (30 percent) are measured against what a model US News fits would expect.',
 'nu': 'Peer assessment (20 percent) is a survey US News runs. Graduation performance (10 percent) and Pell graduation performance (5.5 percent) are measured against rates US News predicts. Faculty salaries and spending per student come from what schools report.',
 'nlac': 'Peer assessment (20 percent) is a survey US News runs. Graduation performance (10 percent) and Pell graduation performance (5.5 percent) are measured against rates US News predicts. Faculty salaries and spending per student come from what schools report.',
 'mba': 'Peer and recruiter assessments (25 percent) are surveys US News runs.', 'law': 'Peer and lawyers and judges assessments (25 percent) are surveys US News runs.',
 'eng': 'Peer and recruiter assessments (25 percent) are surveys US News runs.', 'edu': 'Peer and educational professionals assessments (25 percent) are surveys US News runs.',
 'med': 'Research activity per faculty member and faculty resources use counts that schools report to US News, which are not published per school in full.'}

def checks_section(l):
    k = l['key']
    if k in RECOMPUTE:
        out.append(f'<p class="bench-note">Can the order be worked again from public inputs? Cannot tell. {e(RECOMPUTE[k])}</p>')
    rows = [c for c in CK if c['list'] == k and c['outcome'] != 'DISPLAY']
    if not rows: return
    out.append(f'<h3>Figures checked</h3>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>Figure</th><th>US News prints</th><th>Year US News names</th><th>Public record</th><th>Year</th><th>Reading</th><th>Note</th></tr></thead><tbody>')
    for c in rows:
        rd = READ[c['outcome']] + (f' ({WHY.get(c["reason"], c["reason"])})' if c['outcome'] == 'CANNOT_TELL' else '')
        pub = c['pub'] if c['pub'] not in (None, '') else ''
        if pub and pub.replace('.', '').isdigit() and '.' in pub and len(pub.split('.')[1]) > 2: pub = f'{float(pub):.2f}'
        note = c['note'] + (' Source: ' + c['source'] if c.get('source') else '')
        out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(c['school']), e(c['field']), e(str(c['usn'] or '')), e(str(c['usn_year'] or 'not printed')), e(str(pub)), e(str(c['pub_year'] or '')), e(rd), e(note))) + '</tr>')
    out.append('</tbody></table></div>')
    disp = [c for c in CK if c['list'] == k and c['outcome'] == 'DISPLAY']
    if disp:
        out.append('<p class="bench-note">Shown after the data and not scored: the same figures set beside each college&rsquo;s Common Data Set for 2025-26, the latest each college has published, because US News prints no year for them. Percents are worked from the counts in the Common Data Set.</p><ul class="bench-note">')
        for c in disp: out.append(f'<li>{e(c["school"])}: {e(c["note"])}.</li>')
        out.append('</ul>')

out = []
out.append('<h2>US News education rankings, set against the public record</h2>')
out.append('<p>US News &amp; World Report publishes rankings of schools and colleges. For each list it states the indicators it uses and the weight of each. '
           'This desk records the top of each list in the current edition, with the list and the stated method linked. '
           'It then sets each figure US News prints for a school against the same figure in the public record, such as a state report card, the federal school and college data, '
           'or the school&rsquo;s own published report, and checks whether the order follows from the stated method where the method can be worked again from public inputs.</p>')
out.append('<p>Each figure reads match, mismatch or cannot tell, with the year used on each side. Match means the public figure, rounded to the precision US News prints, is the same. '
           'Cannot tell is given with its reason, such as a year that is not printed, a figure the state suppresses, or a figure not found. The rules were fixed and committed before any figure was compared. '
           'High schools, National Universities, National Liberal Arts Colleges and law schools are checked. Rows on the other lists read <b>check in progress</b>.</p>')
SUM = Counter((c['list'], c['outcome']) for c in CK if c['outcome'] != 'DISPLAY')
def tally(k):
    m, x, t = SUM[(k, 'MATCH')], SUM[(k, 'MISMATCH')], SUM[(k, 'CANNOT_TELL')]
    return f'{m} match, {x} mismatch, {t} cannot tell'
NAMES = {'hs': 'High schools', 'nu': 'National Universities', 'nlac': 'National Liberal Arts Colleges', 'law': 'Law schools'}
if CK:
    out.append('<p>Figures checked so far: ' + ', '.join(f'{NAMES[k]} {tally(k)}' for k in ('hs', 'nu', 'nlac', 'law') if k in DONE) + '.</p>')
out.append(f'<p>The lists were read on {e(D["read"])}. A rank is printed as US News prints it. A tie is marked, and a tie at the tenth place is kept whole, so a list can hold more than ten schools. '
           'Only the rank, the stated method and the figures to be checked are shown here. The full lists are on the US News pages linked below.</p>')

for l in D['lists']:
    out.append(f'<h2>{e(l["title"])}</h2>')
    if l['scope'] == 'none':
        out.append(f'<p>US News publishes no national list of this kind. Its method page says &ldquo;{e(l["quote"])}&rdquo; and describes {e(l["quote_more"])}. '
                   f'No state list is picked here in its place. Edition {e(l["edition"])}. <a href="{e(l["list_url"])}">US News list page</a>. {resp(l["key"] + "-list")}</p>')
        out.append(weights_line(l)); continue
    if l['scope'] == 'tiers':
        out.append(f'<p>US News places medical schools in tiers and gives no rank within a tier. Its method page says &ldquo;{e(l["quote"])}&rdquo; and defines &ldquo;{e(l["tier_def"])}&rdquo;. '
                   f'The schools US News shows in Tier 1 are listed in the order its page shows them, which is not a rank. Edition {e(l["edition"])}. <a href="{e(l["list_url"])}">US News list</a>.</p>')
    else:
        out.append(f'<p>Edition {e(l["edition"])}, {e(l["scope"])} list. <a href="{e(l["list_url"])}">US News list</a>.</p>')
    out.append(weights_line(l))
    hs = l['key'] == 'hs'; col = l['key'] in ('nu', 'nlac')
    head = ['Rank', 'School', 'Place']
    if hs: head += ['Graduation rate, as US News prints it', 'Enrollment, grades 9 to 12, as US News prints it']
    if col: head += ['Undergraduate enrollment, fall 2025, as US News prints it']
    head += ['Check', 'Answer']
    out.append('<div class="tw"><table class="bench"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>')
    for r in l['rows']:
        rk = 'Tier 1' if l['scope'] == 'tiers' else (f'{r["rank"]}' + (' (tie)' if r['tie'] else ''))
        name = f'<a href="{e(r["url"])}">{e(r["name"])}</a>' if r.get('url') else e(r['name'])
        cells = [rk, name, e(r['place'])]
        if hs: cells += [e(r['grad']), e(r['enrollment'])]
        if col: cells += [e(r['enrollment'].replace(' (fall 2025)', ''))]
        if l['key'] in DONE:
            mine = [c for c in CK if c['list'] == l['key'] and c['outcome'] != 'DISPLAY' and same_school(c['school'], r['name'])]
            cc = Counter(c['outcome'] for c in mine)
            r_check = f"{cc['MATCH']} match, {cc['MISMATCH']} mismatch, {cc['CANNOT_TELL']} cannot tell" if mine else 'not checked'
        else:
            r_check = r['check']
        cells += [e(r_check), resp(r['slug'])]
        out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
    out.append('</tbody></table></div>')
    checks_section(l)
    if hs: out.append('<p class="bench-note">' + e(l['data_years']) + ' US News prints a graduation rate of &ldquo;&gt; 95%&rdquo; or &ldquo;&gt; 99%&rdquo; for some schools and N/A for one. These are shown as printed.</p>')

out.append('<h2>National Blue Ribbon awards</h2>')
out.append('<p>The US Department of Education pages for the National Blue Ribbon Schools program, including the award search and the yearly lists at the addresses tried, returned &ldquo;Page not found&rdquo; on 2026-11-10. '
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
out.append('<p class="bench-note">Earlier or other awards named in school or press pages, without a Department or state agency record read here, are not listed. For the other high schools in the list no award record was found in the sources read.</p>')
out.append('<h2>Instructional time</h2>')
out.append('<p>None of the ten states publishes instructional minutes or days per school in the files read. The District of Columbia publishes daily school hours. Nothing is set side by side.</p>')
out.append('<h2>Documented cases of corrected data</h2>')
if CASES:
    out.append('<p>Cases where a school&rsquo;s own statement or report says data it gave US News was inaccurate and its US News rank was removed, withdrawn or computed again. Primary sources only, quoted. '
               'None of these schools is in a current top-ten list above, except where named.</p>')
    out.append('<div class="tw"><table class="bench"><thead><tr><th>School</th><th>List and edition</th><th>Data item, as the document states it</th><th>What the document says</th><th>Date</th><th>Source</th></tr></thead><tbody>')
    for v in CASES['verified']:
        out.append('<tr>' + ''.join(f'<td>{x}</td>' for x in (e(v['school']), e(v['list'] + ', ' + v['editions']), e(v['data_item']), '&ldquo;' + e(v['rank_outcome_quote']) + '&rdquo;', e(v.get('date', '')), ' '.join(f'<a href="{e(u)}">source</a>' for u in (v['primary_urls'] if isinstance(v['primary_urls'], list) else [v['primary_urls']])[:2]))) + '</tr>')
    out.append('</tbody></table></div>')
    out.append('<p class="bench-note">Cases named only in news reports, or whose primary page refused our reader, are not listed until the primary document is read.</p>')
out.append('<h2>What comes next</h2>')
out.append('<p>The business, engineering, education and medical school lists are checked next, against each school&rsquo;s own published reports. '
           'Colleges whose Common Data Set could not be read are added when it can be.</p>')
out.append('<p class="meta">Rankings, list names and method text belong to US News &amp; World Report and are quoted here only as far as each check needs, with links. '
           f'Named here and want to answer a row? Each row has an answer link. US News can answer here: {resp("usnews", "Respond")}.</p>')
out.append('<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/rank">rank</a>. The plan was committed before any figure was compared.</p>')
out.append('<section id="replies" data-prefix="rank"></section><script src="/replies.js" defer></script>')
open(sys.argv[1] if len(sys.argv) > 1 else 'rank_body.html', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('rank_body.html', sum(len(l['rows']) for l in D['lists']), 'rows')
