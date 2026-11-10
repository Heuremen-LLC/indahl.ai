#!/usr/bin/env python3
"""RANK page body: rank_body.html from data/rank.json. build_site.py wraps it with the shared header, nav, division line and footer.
Copy rules: plain sentences, no semicolons, no digits in headings, no adjectives about schools or US News, no cause named. Heuremen LLC."""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
D = json.load(open('data/rank.json', encoding='utf-8'))
e = html.escape

def pct(w): return w.replace('%', ' percent')
def weights_line(l):
    parts = [f'{e(a)} {e(pct(w))}' for a, w in l['weights']]
    s = '<p class="bench-note">Indicators and weights as US News states them: ' + ', '.join(parts) + '.'
    if l.get('weights_note'): s += ' ' + e(l['weights_note'])
    return s + f' <a href="{e(l["method_url"])}">US News methodology</a>.</p>'

def resp(slug, label='Respond'): return f'<a href="/respond?u=rank-{e(slug)}">{label}</a>'

out = []
out.append('<h2>US News education rankings, set against the public record</h2>')
out.append('<p>US News &amp; World Report publishes rankings of schools and colleges. For each list it states the indicators it uses and the weight of each. '
           'This desk records the top of each list in the current edition, with the list and the stated method linked. '
           'It then sets each figure US News prints for a school against the same figure in the public record, such as a state report card, the federal school and college data, '
           'or the school&rsquo;s own published report, and checks whether the order follows from the stated method where the method can be worked again from public inputs.</p>')
out.append('<p>Every row below reads <b>check in progress</b>. The checks are added list by list as each is done. Each figure will read match, mismatch or cannot tell, '
           'with the year used on each side. The rules were fixed and committed before any figure was compared.</p>')
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
        cells += [e(r['check']), resp(r['slug'])]
        out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
    out.append('</tbody></table></div>')
    if hs: out.append('<p class="bench-note">' + e(l['data_years']) + ' US News prints a graduation rate of &ldquo;&gt; 95%&rdquo; or &ldquo;&gt; 99%&rdquo; for some schools and N/A for one. These are shown as printed.</p>')

out.append('<h2>What comes next</h2>')
out.append('<p>For high schools, each printed figure is set against the state report card for the same school and year and against the federal Common Core of Data. '
           'Schools in the list that hold a National Blue Ribbon award get the award year, its category and its stated criterion, checked against the state assessment data for the years the award cites. '
           'For colleges, the stated inputs are set against IPEDS, the College Scorecard and each school&rsquo;s own Common Data Set. '
           'For graduate schools, they are set against the published ABA disclosures, AAMC figures where public, and each school&rsquo;s own reports. '
           'Where a stated input is a survey score, purchased data or a model US News fits, the order cannot be worked again from public inputs, and the page will say which input is missing. '
           'Public, documented cases where a school&rsquo;s submitted data was later corrected and its rank changed will be listed from primary sources only.</p>')
out.append('<p class="meta">Rankings, list names and method text belong to US News &amp; World Report and are quoted here only as far as each check needs, with links. '
           f'Named here and want to answer a row? Each row has an answer link. US News can answer here: {resp("usnews", "Respond")}.</p>')
out.append('<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/rank">rank</a>. The plan was committed before any figure was compared.</p>')
out.append('<section id="replies" data-prefix="rank"></section><script src="/replies.js" defer></script>')
open('rank_body.html', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('rank_body.html', sum(len(l['rows']) for l in D['lists']), 'rows')
