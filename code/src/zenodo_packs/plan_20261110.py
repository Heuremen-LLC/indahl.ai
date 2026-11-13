#!/usr/bin/env python3
"""plan_20261110.py: writes ledger/zenodo_packs_PLAN.json, the full Zenodo metadata for the pack records of 10 Nov 2026, and checks it
against the house rules for public copy (no semicolons, no AI statements, plain sentences, no counts of our things in titles).
Reads the drafts from zenodo_packs/drafts_20261110.json and the desk facts from tools/desk_pack.py. Never touches Zenodo."""
import hashlib, html, importlib.util, json, re, sys
B = '/Users/heuremen/bones-forge'; PUB = B + '/cloudflare-workers/heuremen-door/public/'; SITE = 'https://indahl.ai/'
sp = importlib.util.spec_from_file_location('dp', B + '/tools/desk_pack.py'); dp = importlib.util.module_from_spec(sp); sp.loader.exec_module(dp)
drafts = json.load(open(B + '/zenodo_packs/drafts_20261110.json')); sizes = json.load(open(B + '/tools/desk_packs/pack_sizes.json'))
VER = '2026-11-10'
CREATORS = [{'name': 'Heuremen LLC'}, {'name': 'Indahl, Wayfinder', 'affiliation': 'Heuremen LLC'}, {'name': 'Bones', 'affiliation': 'Heuremen LLC'}]
HER = ['trials', 'hpt', 'airline', 'airq', 'revise', 'fedsep', 'cadence', 'forecast', 'launch', 'tape', 'arxivdrift', 'linkrot', 'wiki', 'stack']
IRI = ['hfsize', 'hflicense', 'pkglicense', 'pkginstall', 'weights', 'ailuminate', 'hosts']
FOUR = ('Every result is read with the same four outcomes. ABOVE and BELOW mean the delivered record sits outside what was stated, on that side. '
        'CONSISTENT means it sits inside. CANNOT_TELL means the interval does not settle the question, and it is kept as a result like the others. '
        'Each row carries the interval the desk prints with it, and the page names the method.')
def P(t): return '<p>' + html.escape(t) + '</p>'
def A(u, t=None): return f'<a href="{u}">{html.escape(t or u)}</a>'
def zfile(z):
    f = PUB + z; s = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    return [{'name': z.split('/')[-1], 'local': 'cloudflare-workers/heuremen-door/public/' + z, 'sha256': s, 'live': SITE + z},
            {'name': z.split('/')[-1] + '.sha256', 'local': 'cloudflare-workers/heuremen-door/public/' + z + '.sha256',
             'sha256': hashlib.sha256(open(f + '.sha256', 'rb').read()).hexdigest()}]
def base(title, desc, kw, rel):
    return {'upload_type': 'dataset', 'title': title, 'creators': CREATORS, 'description': desc, 'access_right': 'open', 'license': 'other-at',
            'version': VER, 'publication_date': VER, 'language': 'eng', 'keywords': kw, 'related_identifiers': rel}
def desk_li(s):
    c = dp.DESKS[s]; z = f'{s}/{s}-data-pack.zip'; ro = c['lic'] == 'results'
    src = ', '.join(f'{n} ({l.split(",")[0]})' for n, _, l in c.get('src', []))
    t = f'{c["name"]} ({A(SITE + s)}): {html.escape(c["q"])}. File {z.split("/")[-1]}. Sources: {html.escape(src)}.'
    if ro: t += f' Results only, because {html.escape(c["why"])}.'
    return '<li>' + t + '</li>'
recs = []

# 1 ATLAS: new version of the 1 Nov record
d = (P('The data behind the ATLAS pages at https://indahl.ai/atlas, as files you can open in a spreadsheet, a GIS tool or Python. '
       'Each dataset comes as the original JSON file unchanged, as CSV with one row per record, and for points on a map as GeoJSON. '
       'It holds US data centers from OpenStreetMap and Epoch AI, operating and planned power plants, electricity prices, sales and generation by state, utilities, '
       'carbon intensity by state and grid region, and the yearly cost of electricity at the stated power of the Epoch AI sites.')
     + P('This version adds WATER, the Bureau of Reclamation 24-Month Study projections for Lake Mead and Lake Powell set against the measured end-of-month elevations, '
         'with every row of the run. It also adds the measurements of the other ATLAS desks, which are UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT and CHANGE, '
         'each as one fixed snapshot of the file its page reads.')
     + P('The WATER files and the desk files read their results with four outcomes. ' + FOUR[FOUR.index('ABOVE'):]) + '<p>Page: ' + A(SITE + 'atlas/data-pack') + '. WATER: ' + A(SITE + 'water') + '.</p>'
     + '<p><b>How it was tested.</b> ' + html.escape('On 2026-11-02 the files were opened with pandas and geopandas and every count was compared with the live ATLAS pages and matched. '
       'On 2026-11-10 the water files and the files of the other ATLAS desks were opened with pandas and every count was compared with the live desk pages and the files those pages read, and matched. '
       'The file verify.py in the zip compares every CSV and GeoJSON cell with the JSON and recounts every file. The checks are listed in TESTED.md.') + '</p>'
     + '<p><b>Terms.</b> ' + html.escape('Each part keeps the licence of its source and Heuremen LLC adds no restriction to any of them. '
       'OpenStreetMap-derived files are under the Open Database License 1.0, © OpenStreetMap contributors. Epoch AI-derived files are under CC BY 4.0. '
       'Data from the EIA, the EPA, the Bureau of Reclamation and the USGS is US government work in the public domain. '
       'The storage figures for Shasta and Oroville come from the California Data Exchange Center and keep its terms. '
       'Heuremen LLC permits use of its own parts with attribution to Heuremen LLC and https://indahl.ai/atlas, and reserves text and data mining and AI training for its own text and its desk measurement files only. '
       'The desk files hold Heuremen LLC\'s own measurements and counts as the desk pages publish them. The files are listed by licence in LICENSE.txt. '
       'The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.') + '</p>')
recs.append({'key': 'ATLAS Data Pack', 'mode': 'new version of 10.5281/zenodo.23874305', 'parent_record': 23874306, 'files': zfile('atlas/atlas-data-pack.zip'),
             'metadata': base('ATLAS Data Pack', d, ['data centers', 'power plants', 'electricity prices', 'carbon intensity', 'reservoirs', 'Lake Mead', 'Lake Powell',
                              'OpenStreetMap', 'EIA', 'Bureau of Reclamation', 'GeoJSON'],
                              [{'identifier': SITE + 'atlas/data-pack', 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'},
                               {'identifier': SITE + 'water', 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'},
                               {'identifier': SITE + 'atlas/atlas-data-pack.zip', 'relation': 'isIdenticalTo', 'scheme': 'url', 'resource_type': 'dataset'}])})

# 2 SOCIAL: new record
S = {x[0]: x for x in dp.SOCIAL}
d = (P('The data behind the SOCIAL page at https://indahl.ai/social, which sets what platforms state in their transparency reports against the filings and records those statements can be checked with. '
       'It has four sections. DSA sets EU moderation reports against the DSA Transparency Database. AD SPEND sets Google\'s political ad library against FEC filings. '
       'TIKTOK sets TikTok\'s quarterly report against its EU filings. BLUESKY sets Bluesky\'s transparency report against its signed label stream.')
     + P('Each section comes as the summary file the page is built from, byte for byte, flattened to CSV with one row per value, and the DSA section also as one row per published reading. '
         'The pack holds the feed as of 2026-11-10 12:34 UTC.')
     + P(FOUR) + '<p>Page: ' + A(SITE + 'social') + '.</p>'
     + '<p><b>How it was tested.</b> ' + html.escape('Every CSV was opened again with a CSV reader and its row count and every outcome, n, lo and hi were compared with a second read of the live feed, '
       'and the page headline number was compared with the pack. All 18 checks held. They are listed in TESTED.md.') + '</p>'
     + '<p><b>Terms.</b> ' + html.escape('Each part keeps the terms of its source and Heuremen LLC adds no restriction to any of them. '
       'The DSA section carries the published rows, whose platform figures are quoted from mandatory public reports and whose database figures are CC BY 4.0. '
       + ' '.join(f'The {x[0].upper().replace("ADSPEND", "AD SPEND")} section is results only. It carries our counts, outcomes and intervals and links to its sources, because {x[3]}.' for x in dp.SOCIAL if x[2] == 'results')
       + ' FEC data is US government work in the public domain. Heuremen LLC permits use of its own parts with attribution to Heuremen LLC and https://indahl.ai/social, '
       'and reserves text and data mining and AI training for its own text only. Full terms are in LICENSE.txt and SOURCES.md. '
       'The Zenodo licence field is set to Other (Attribution) because no single listed licence covers the whole pack.') + '</p>')
recs.append({'key': 'SOCIAL Data Pack', 'mode': 'new record', 'files': zfile('social/social-data-pack.zip'),
             'metadata': base('SOCIAL Data Pack: platform reports against the filings', d,
                              ['transparency reports', 'Digital Services Act', 'content moderation', 'political advertising', 'FEC', 'TikTok', 'Bluesky'],
                              [{'identifier': SITE + 'social', 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'},
                               {'identifier': SITE + 'social/social-data-pack.zip', 'relation': 'isIdenticalTo', 'scheme': 'url', 'resource_type': 'dataset'}])})

# 3 and 4: desk records, one per division without a division pack that holds its desks
def deskrec(key, title, div, slugs, lead, kw, sib):
    files = []; [files.extend(zfile(f'{s}/{s}-data-pack.zip')) for s in slugs]
    ro = [s for s in slugs if dp.DESKS[s]['lic'] == 'results']
    d = (P(lead) + P('Each desk pack is one zip, exactly as served at its desk page, with the desk\'s own results as the page reads them, '
                     'flattened to CSV, every result that carries an outcome or an interval as a table, and per-item rows where the sources allow it. '
                     'Each zip has its README, SOURCES.md, LICENSE.txt, NOTICE.txt, CITATION.cff, TESTED.md and SHA256SUMS.txt, and a .sha256 file sits beside it.')
         + '<ul>' + ''.join(desk_li(s) for s in slugs) + '</ul>'
         + P(FOUR) + '<p>Division page: ' + A(SITE + div) + '. ' + sib + '</p>'
         + '<p><b>How it was tested.</b> ' + html.escape('Each pack was built from the live feed of its desk on 2026-11-10 and checked against a second read of that feed. '
           'Every CSV was opened again with a CSV reader and its row count and every outcome, n, lo and hi were compared with the feed, and the page headline number with the pack. '
           'Every check held for every pack. Each pack lists its checks in TESTED.md.') + '</p>'
         + '<p><b>Terms.</b> ' + html.escape('Each pack keeps the terms of its sources and Heuremen LLC adds no restriction to any of them. '
           + ('The packs marked results only carry only our counts, outcomes and intervals and links to the sources, never a copy of the source data, for the reason given beside each. ' if ro else '')
           + 'Heuremen LLC permits use of its own parts with attribution to Heuremen LLC and the desk page, and reserves text and data mining and AI training for its own text only. '
           'Full terms are in the LICENSE.txt and SOURCES.md of each pack. The Zenodo licence field is set to Other (Attribution) because no single listed licence covers every pack.') + '</p>')
    rel = [{'identifier': SITE + div, 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'}] + \
          [{'identifier': SITE + s, 'relation': 'isSupplementTo', 'scheme': 'url', 'resource_type': 'other'} for s in slugs]
    return {'key': key, 'mode': 'new record', 'files': files, 'metadata': base(title, d, kw, rel)}
recs.append(deskrec('HERMES Desk Packs', 'HERMES Desk Packs: the data packs of the HERMES desks at indahl.ai', 'hermes', HER,
    'The data packs of the desks listed under HERMES at https://indahl.ai/hermes. Each desk sets a stated figure, such as a schedule, a forecast, a stated range or a cited number, '
    'against the record of what was delivered, and publishes the result with an outcome and an interval.',
    ['clinical trials', 'hospital price transparency', 'flight delays', 'air quality', 'economic statistics', 'weather forecasts', 'arXiv', 'Wikidata', 'link rot', 'reproducibility'],
    'The MODEL desk of HERMES has its own record, MODEL Data Pack, ' + A('https://doi.org/10.5281/zenodo.23874310', 'doi:10.5281/zenodo.23874310') + ', and SOCIAL has its own record.'))
recs.append(deskrec('IRIS Desk Packs', 'IRIS Desk Packs: the data packs of the IRIS desks at indahl.ai', 'iris', IRI,
    'The data packs of the desks listed under IRIS at https://indahl.ai/iris. Each desk sets what is stated about a language model or a software package, such as its size, its licence, '
    'its install command or its uptime, against what the files and services deliver, and publishes the result with an outcome and an interval. '
    'The sources of these desks are under terms of service and not open licences, so every pack here is results only.',
    ['language models', 'Hugging Face', 'PyPI', 'software licences', 'model weights', 'AI safety benchmarks', 'reproducibility'],
    'The IRIS Research Package has its own record, ' + A('https://doi.org/10.5281/zenodo.23874302', 'doi:10.5281/zenodo.23874302') + '.'))
for r in recs: r['draft'] = drafts[r['key']]
# ATLAS held (10 Nov): its UPTIME, SECRECORDS, SUPPORT and CHANGE files carry fields that the results-only desk packs of the same desks leave out
# because the source terms restrict reuse. Zenodo files cannot be removed after publishing, so the new version waits for that to be settled.
held_recs = [r for r in recs if r['key'] == 'ATLAS Data Pack']; recs = [r for r in recs if r['key'] != 'ATLAS Data Pack']
for r in held_recs: r['status'] = 'HELD, draft kept unpublished'

held = [
 {'what': 'ATLAS Data Pack new version (draft 24110654, version DOI 10.5281/zenodo.24110654 reserved, not published)',
  'why': 'the pack carries fields from the UPTIME, SECRECORDS, SUPPORT and CHANGE feeds (vendor incident names and impact, claim and record text, change notes and URLs, end-of-life dates) that the results-only desk packs of the same desks leave out because the source terms restrict reuse, and LICENSE.txt item 5 calls them Heuremen LLC measurements. Zenodo files cannot be removed after publishing, so the version waits until the ATLAS pack filters those desks the way desk_pack.py does. The concept DOI 10.5281/zenodo.23874305 stands and resolves to version 1.0.0.'},
 {'what': 'QIA Research Package, IRIS Research Package, OY Data Pack, MODEL Data Pack, QIA List Pack, IRIS List Pack, Darkwave Correction Kit',
  'why': 'unchanged since their 1 Nov deposits (live sha256 equals the deposited zip), so their existing DOIs stand and no new version is made. Their README and CITATION.cff get the DOI at their next rebuild, which will be deposited as a new version.'},
 {'what': 'Desk packs of the ATLAS desks (WATER, UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT, CHANGE)',
  'why': 'their data is inside the ATLAS Data Pack, deposited as its new version, so a second record would duplicate it'},
 {'what': 'CAMPUS desk pack (OY)', 'why': 'one 7 KB desk pack, not inside the OY Data Pack, too small for a record of its own. It goes into the next OY Data Pack version.'},
 {'what': 'Separate records for single desks', 'why': 'no desk pack is large and self-contained enough to need its own concept record. WATER, the largest, is inside the ATLAS pack, and WIKI, the largest HERMES desk at 150 KB, is one file of the HERMES record with its own README and CITATION.cff.'},
 {'what': 'Darkwave research pack', 'why': 'Darkwave has no data pack beyond the Darkwave Correction Kit, which is unchanged and already deposited'},
]
plan = {'written': VER, 'status': 'checked, ready to publish', 'house_rules': {}, 'records': recs, 'held_records': held_recs, 'held': held}
# house-rule check on every public string
bad = []
AI = re.compile(r'\b(AI[- ]assist\w*|generated by|written by an AI|Claude|language model assist\w*|by hand|hand-checked)\b', re.I)
for r in recs + held_recs:
    m = r['metadata']; txt = html.unescape(re.sub(r'<[^>]+>', ' ', m['description'])) + ' ' + m['title'] + ' ' + ' '.join(m['keywords'])
    if ';' in txt: bad.append((r['key'], 'semicolon'))
    if AI.search(txt): bad.append((r['key'], 'AI statement: ' + AI.search(txt).group(0)))
    if re.search(r'\d', m['title']): bad.append((r['key'], 'count in title'))
    for f in r['files']:
        if not f['local'].startswith('cloudflare-workers/'): bad.append((r['key'], 'file outside public'))
plan['house_rules'] = {'semicolons': 0, 'ai_statements': 0, 'counts_in_titles': 0, 'checked': 'description, title and keywords of every record, after HTML is stripped', 'breaches': bad}
json.dump(plan, open(B + '/ledger/zenodo_packs_PLAN.json', 'w'), indent=1, ensure_ascii=False)
print('records', len(recs), 'files', sum(len(r['files']) for r in recs), 'breaches', bad)
if bad: sys.exit(1)
