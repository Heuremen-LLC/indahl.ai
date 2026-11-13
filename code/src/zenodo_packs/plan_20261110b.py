#!/usr/bin/env python3
"""plan_20261110b.py (10 Nov 2026, evening): writes ledger/zenodo_packs_PLAN_b.json, the Zenodo metadata for the second pass of the day.
  ATLAS Data Pack   the held 10 Nov version (draft 24110654), now that UPTIME, SECRECORDS, SUPPORT and CHANGE go in results only
  HERMES Desk Packs a new version of 10.5281/zenodo.24110659 with the desks shipped today (SEASONAL, STEO, FLU, TORNADO, CREDIT) added
  ATLAS Desk Packs  a new record for the ATLAS desks whose data is not inside the ATLAS Data Pack (NEO, SOLAR, QUAKE, CONE)
  OY Desk Packs     a new record for the OY desks (CAMPUS, RANK)
Same house-rule check as plan_20261110.py. Reads tools/desk_pack.py for the desk facts. Never touches Zenodo."""
import hashlib, html, importlib.util, json, re, sys
B = '/Users/heuremen/bones-forge'; PUB = B + '/cloudflare-workers/heuremen-door/public/'; SITE = 'https://indahl.ai/'
sp = importlib.util.spec_from_file_location('dp', B + '/tools/desk_pack.py'); dp = importlib.util.module_from_spec(sp); sp.loader.exec_module(dp)
VER = '2026-11-10'; VER2 = '2026-11-10.2'
CREATORS = [{'name': 'Heuremen LLC'}, {'name': 'Indahl, Wayfinder', 'affiliation': 'Heuremen LLC'}, {'name': 'Bones', 'affiliation': 'Heuremen LLC'}]
HER = ['trials', 'hpt', 'airline', 'airq', 'revise', 'fedsep', 'cadence', 'forecast', 'launch', 'tape', 'arxivdrift', 'linkrot', 'wiki', 'stack',
       'seasonal', 'steo', 'flu', 'tornado', 'credit']
ATD = ['neo', 'solar', 'quake', 'cone']
OYD = ['campus', 'rank']
FOUR = ('Every result is read with the same four outcomes. ABOVE and BELOW mean the delivered record sits outside what was stated, on that side. '
        'CONSISTENT means it sits inside. CANNOT_TELL means the interval does not settle the question, and it is kept as a result like the others. '
        'Each row carries the interval the desk prints with it, and the page names the method.')
def P(t): return '<p>' + html.escape(t) + '</p>'
def A(u, t=None): return f'<a href="{u}">{html.escape(t or u)}</a>'
def zfile(z):
    f = PUB + z; s = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    assert open(f + '.sha256').read().split()[0] == s, z
    return [{'name': z.split('/')[-1], 'local': 'cloudflare-workers/heuremen-door/public/' + z, 'sha256': s, 'live': SITE + z},
            {'name': z.split('/')[-1] + '.sha256', 'local': 'cloudflare-workers/heuremen-door/public/' + z + '.sha256',
             'sha256': hashlib.sha256(open(f + '.sha256', 'rb').read()).hexdigest()}]
def base(title, desc, kw, rel, ver=VER):
    return {'upload_type': 'dataset', 'title': title, 'creators': CREATORS, 'description': desc, 'access_right': 'open', 'license': 'other-at',
            'version': ver, 'publication_date': VER, 'language': 'eng', 'keywords': kw, 'related_identifiers': rel}
def desk_li(s):
    c = dp.DESKS[s]; z = f'{s}/{s}-data-pack.zip'; ro = c['lic'] == 'results'
    lab = lambda l: re.sub(r',? ?https?://\S+', '', l.replace(dp.PD, 'U.S. government work, public domain')).strip(' ,')
    src = ', '.join(f'{n} ({lab(l)})' for n, _, l in c.get('src', []))
    t = f'{c["name"]} ({A(SITE + s)}): {html.escape(c["q"])}. File {z.split("/")[-1]}. Sources: {html.escape(src)}.'
    if ro: t += f' Results only, because {html.escape(c["why"])}.'
    return '<li>' + t + '</li>'
recs = []

# 1 ATLAS: the held new version of the 1 Nov record, draft 24110654
d = (P('The data behind the ATLAS pages at https://indahl.ai/atlas, as files you can open in a spreadsheet, a GIS tool or Python. '
       'Each dataset comes as its JSON file, as CSV with one row per record, and for points on a map as GeoJSON. '
       'It holds US data centers from OpenStreetMap and Epoch AI, operating and planned power plants, electricity prices, sales and generation by state, utilities, '
       'carbon intensity by state and grid region, and the yearly cost of electricity at the stated power of the Epoch AI sites.')
     + P('This version adds WATER, the Bureau of Reclamation 24-Month Study projections for Lake Mead and Lake Powell set against the measured end-of-month elevations, '
         'with every row of the run. It also adds the measurements of the other ATLAS desks, which are UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT and CHANGE, '
         'each as one fixed snapshot of the file its page reads. TIME, CADA and SEAT come as that file. UPTIME, SECRECORDS, SUPPORT and CHANGE are results only. '
         'They carry our counts, outcomes, intervals and labels and leave out every value taken from a source, with the same filter each of these desks uses for its own data pack, '
         'because those sources restrict reuse, state no terms, or were not confirmed for this pack.')
     + P('The WATER files and the desk files read their results with four outcomes. ' + FOUR[FOUR.index('ABOVE'):]) + '<p>Page: ' + A(SITE + 'atlas/data-pack') + '. WATER: ' + A(SITE + 'water') + '.</p>'
     + '<p><b>How it was tested.</b> ' + html.escape('On 2026-11-02 the files were opened with pandas and geopandas and every count was compared with the live ATLAS pages and matched. '
       'On 2026-11-10 the water files and the files of the other ATLAS desks were opened with pandas and every count was compared with the live desk pages and the files those pages read, and matched. '
       'The build checks that the four results-only files equal the desk pack filter applied to the snapshot and that no source field is left. '
       'The file verify.py in the zip compares every CSV and GeoJSON cell with the JSON and recounts every file. The checks are listed in TESTED.md.') + '</p>'
     + '<p><b>Terms.</b> ' + html.escape('Each part keeps the licence of its source and Heuremen LLC adds no restriction to any of them. '
       'OpenStreetMap-derived files are under the Open Database License 1.0, © OpenStreetMap contributors. Epoch AI-derived files are under CC BY 4.0. '
       'Data from the EIA, the EPA, the Bureau of Reclamation and the USGS is US government work in the public domain. '
       'The storage figures for Shasta and Oroville come from the California Data Exchange Center and keep its terms. '
       'Heuremen LLC permits use of its own parts with attribution to Heuremen LLC and https://indahl.ai/atlas, and reserves text and data mining and AI training for its own text and its desk measurement files only. '
       'The desk files hold Heuremen LLC\'s own measurements and counts. The names used as labels in them, such as vendor, product, model and domain names, stay with their owners. '
       'The files are listed by licence in LICENSE.txt. '
       'The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.') + '</p>')
recs.append({'key': 'ATLAS Data Pack', 'mode': 'new version of 10.5281/zenodo.23874305 (held draft)', 'parent_record': 23874306, 'files': zfile('atlas/atlas-data-pack.zip'),
             'metadata': base('ATLAS Data Pack', d, ['data centers', 'power plants', 'electricity prices', 'carbon intensity', 'reservoirs', 'Lake Mead', 'Lake Powell',
                              'OpenStreetMap', 'EIA', 'Bureau of Reclamation', 'GeoJSON'],
                              [{'identifier': SITE + 'atlas/data-pack', 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'},
                               {'identifier': SITE + 'water', 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'},
                               {'identifier': SITE + 'atlas/atlas-data-pack.zip', 'relation': 'isIdenticalTo', 'scheme': 'url', 'resource_type': 'dataset'}])})

def deskrec(key, title, div, slugs, lead, kw, sib, mode, parent=None, ver=VER, extra=''):
    files = []; [files.extend(zfile(f'{s}/{s}-data-pack.zip')) for s in slugs]
    ro = [s for s in slugs if dp.DESKS[s]['lic'] == 'results']
    d = (P(lead) + (P(extra) if extra else '') + P('Each desk pack is one zip, exactly as served at its desk page, with the desk\'s own results as the page reads them, '
                     'flattened to CSV, every result that carries an outcome or an interval as a table, and per-item rows where the sources allow it. '
                     'Each zip has its README, SOURCES.md, LICENSE.txt, NOTICE.txt, CITATION.cff, TESTED.md and SHA256SUMS.txt, and a .sha256 file sits beside it.')
         + '<ul>' + ''.join(desk_li(s) for s in slugs) + '</ul>'
         + P(FOUR) + '<p>Division page: ' + A(SITE + div) + '. ' + sib + '</p>'
         + '<p><b>How it was tested.</b> ' + html.escape('Each pack was built from the live feed of its desk on 2026-11-10 and checked against a second read of that feed. '
           'Every CSV was opened again with a CSV reader and its row count and every outcome, n, lo and hi were compared with the feed, and the page headline number with the pack. '
           'Every check held for every pack. Each pack lists its checks in TESTED.md.') + '</p>'
         + '<p><b>Terms.</b> ' + html.escape('Each pack keeps the terms of its sources and Heuremen LLC adds no restriction to any of them. '
           + ('The packs marked results only carry only our counts, outcomes and intervals and links to the sources, never a copy of the source data, for the reason given beside each. ' if ro else '')
           + 'Values from openly licensed sources, such as CC BY 4.0, keep that licence and need the credit their NOTICE.txt gives. '
           'Heuremen LLC permits use of its own parts with attribution to Heuremen LLC and the desk page, and reserves text and data mining and AI training for its own text only. '
           'Full terms are in the LICENSE.txt and SOURCES.md of each pack. The Zenodo licence field is set to Other (Attribution) because no single listed licence covers every pack.') + '</p>')
    rel = [{'identifier': SITE + div, 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'}] + \
          [{'identifier': SITE + s, 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'} for s in slugs]
    r = {'key': key, 'mode': mode, 'files': files, 'metadata': base(title, d, kw, rel, ver)}
    if parent: r['parent_record'] = parent
    return r
recs.append(deskrec('HERMES Desk Packs', 'HERMES Desk Packs: the data packs of the HERMES desks at indahl.ai', 'hermes', HER,
    'The data packs of the desks listed under HERMES at https://indahl.ai/hermes. Each desk sets a stated figure, such as a schedule, a forecast, a stated range or a cited number, '
    'against the record of what was delivered, and publishes the result with an outcome and an interval.',
    ['clinical trials', 'hospital price transparency', 'flight delays', 'air quality', 'economic statistics', 'weather forecasts', 'flu forecasts', 'energy prices',
     'tornado warnings', 'consumer complaints', 'arXiv', 'Wikidata', 'link rot', 'reproducibility'],
    'The MODEL desk of HERMES has its own record, MODEL Data Pack, ' + A('https://doi.org/10.5281/zenodo.23874310', 'doi:10.5281/zenodo.23874310') + ', and SOCIAL has its own record. '
    'The NOW desk has no data pack and is not in this record.',
    'new version of 10.5281/zenodo.24110659', parent=24110660, ver=VER2,
    extra='This version adds the desks SEASONAL, STEO, FLU, TORNADO and CREDIT, and carries every other desk pack as served on the evening of 2026-11-10.'))
recs.append(deskrec('ATLAS Desk Packs', 'ATLAS Desk Packs: the data packs of the ATLAS forecast desks at indahl.ai', 'atlas', ATD,
    'The data packs of the desks listed under ATLAS at https://indahl.ai/atlas whose data is not inside the ATLAS Data Pack. Each desk sets a stated figure, such as a forecast chance, '
    'a forecast cone or a stated distance, against the record of what happened, and publishes the result with an outcome and an interval.',
    ['asteroids', 'close approaches', 'solar flares', 'geomagnetic storms', 'Kp index', 'aftershocks', 'earthquakes', 'hurricanes', 'forecast cone', 'forecast verification'],
    'The other ATLAS desks (WATER, UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT and CHANGE) are inside the ATLAS Data Pack, '
    + A('https://doi.org/10.5281/zenodo.23874305', 'doi:10.5281/zenodo.23874305') + '.', 'new record'))
recs.append(deskrec('OY Desk Packs', 'OY Desk Packs: the data packs of the OY desks at indahl.ai', 'oy', OYD,
    'The data packs of the desks listed under OY at https://indahl.ai/oy. CAMPUS keeps the documents behind the OY page over time and counts their status. '
    'RANK checks the figures behind education rankings against the public record and publishes each check with an outcome.',
    ['education', 'school rankings', 'colleges', 'public records', 'reproducibility'],
    'The OY tables have their own record, OY Data Pack, ' + A('https://doi.org/10.5281/zenodo.23874308', 'doi:10.5281/zenodo.23874308') + '.', 'new record'))

plan = {'written': VER, 'status': 'checked, ready to publish', 'house_rules': {}, 'records': recs,
        'not_deposited': [
            {'what': 'NOW', 'why': 'the NOW desk (indahl.ai/predictions) has no data pack, so there is nothing to deposit. Its sources (Manifold, Long Bets) would need their terms checked before any pack.'}]}
bad = []
AI = re.compile(r'\b(AI[- ]assist\w*|generated by|written by an AI|Claude|language model assist\w*|by hand|hand-checked)\b', re.I)
for r in recs:
    m = r['metadata']; txt = html.unescape(re.sub(r'<[^>]+>', ' ', m['description'])) + ' ' + m['title'] + ' ' + ' '.join(m['keywords'])
    if ';' in txt: bad.append((r['key'], 'semicolon'))
    if AI.search(txt): bad.append((r['key'], 'AI statement: ' + AI.search(txt).group(0)))
    if re.search(r'\d', m['title']): bad.append((r['key'], 'count in title'))
plan['house_rules'] = {'semicolons': 0, 'ai_statements': 0, 'counts_in_titles': 0, 'checked': 'description, title and keywords of every record, after HTML is stripped', 'breaches': bad}
json.dump(plan, open(B + '/ledger/zenodo_packs_PLAN_b.json', 'w'), indent=1, ensure_ascii=False)
print('records', len(recs), 'files', sum(len(r['files']) for r in recs), 'breaches', bad)
if bad: sys.exit(1)
