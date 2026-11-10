"""build_package.py: assembles the ATLAS Data Pack from the live ATLAS data files into dist/atlas-data-pack/ and zips it.
Writes the original JSON unchanged, one CSV per table, GeoJSON for point data, SOURCES.md, NOTICE.txt, README, START_HERE.html and verify.py.
Refuses if any text file names a local path, a key file, a token, an email address, or breaks the house wording rules.
Builds locally only. Nothing is published."""
import os, shutil, re, zipfile, hashlib, html, json, csv, importlib.util
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/atlas-data-pack'
SRC = B + 'cloudflare-workers/heuremen-door/public/atlas/'
FILES = ['datacenters', 'electricity', 'utilities', 'plants', 'planned', 'carbon', 'scale']
# 10 Nov 2026: desks whose figures live in the site KV are pinned in snap/ at build time (water.json = the bytes served at /water/live.json,
# water_rows.json = data/water.json of the same run), so the pack is one fixed snapshot and every rebuild gives the same files
SNAP = H + '/snap/'; SNAPS = ['water', 'water_rows', 'uptime', 'time', 'cada', 'secrecords', 'seat', 'support', 'change']   # the other ATLAS desks, from their /<desk>/live.json
shutil.rmtree(H + '/dist', ignore_errors=True)
for s in ('json', 'csv', 'geojson'): os.makedirs(D + '/' + s)
sp = importlib.util.spec_from_file_location('verify', H + '/src/verify.py'); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
shutil.copy(H + '/src/verify.py', D + '/verify.py')
# 1. originals, byte for byte
data = {}
for f in FILES:
    shutil.copyfile(SRC + f + '.json', D + f'/json/{f}.json')
    assert open(SRC + f + '.json', 'rb').read() == open(D + f'/json/{f}.json', 'rb').read()
    data[f] = json.load(open(SRC + f + '.json', encoding='utf-8'))
for f in SNAPS:
    shutil.copyfile(SNAP + f + '.json', D + f'/json/{f}.json')
    assert open(SNAP + f + '.json', 'rb').read() == open(D + f'/json/{f}.json', 'rb').read()
    data[f] = json.load(open(SNAP + f + '.json', encoding='utf-8'))
# 2. CSV and GeoJSON
def put_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, lineterminator='\n'); w.writerow(header)
        for r in rows: w.writerow([V.cell(r.get(h)) for h in header])
for t, (jf, rows, count, geo) in V.TABLES.items():
    recs = rows(data[jf[:-5]]); flat = [V.flatten(r) for r in recs]; header = []
    for fr in flat:
        for k in fr:
            if k not in header: header.append(k)
    put_csv(D + f'/csv/{t}.csv', header, flat)
    if geo:
        feats = [{'type': 'Feature', 'geometry': None if r.get('lat') is None else {'type': 'Point', 'coordinates': [r['lon'], r['lat']]}, 'properties': r} for r in recs]
        with open(D + f'/geojson/{t}.geojson', 'w', encoding='utf-8') as fh:
            json.dump({'type': 'FeatureCollection', 'features': feats}, fh, ensure_ascii=False, separators=(',', ':'))
for ds, keys in V.META.items():
    fm = V.flat_meta(V.meta_of(ds, data[ds])); put_csv(D + f'/csv/{ds}_meta.csv', ['key', 'value'], [{'key': k, 'value': v} for k, v in fm.items()])
# 3. text from templates, counts from the data
d, e, c, s = data['datacenters'], data['electricity'], data['carbon'], data['scale']
tok = {'N_OSM': len(d['osm']), 'N_EPOCH': len(d['epoch']), 'N_EPOCH_UNPLACED': sum(1 for x in d['epoch'] if x['lat'] is None), 'N_PLANTS': len(data['plants']['plants']),
       'N_PLANNED': len(data['planned']['plants']), 'N_STATES': len(e['states']), 'N_UTIL': len(data['utilities']['utilities']), 'N_CARBON_STATES': len(c['states']),
       'N_SUBREGIONS': len(c['subregions']), 'N_SITES': len(s['sites']), 'N_SCALE_STATES': len(s['states']), 'N_SCALE_NOT_PLACED': s['totals']['not_placed'], 'N_ADDR_STATE': sum(1 for x in s['sites'] if x['state_from'] == 'address text'), 'N_CORR': len(s['corrections'])}
tok = {k: f'{v:,}' for k, v in tok.items()}
tok.update({'DC_PULLED': d['pulled'], 'OSM_PAGE_COUNT': '1,649 of 1,853 features kept', 'PLANTS_BUILT': data['plants']['built'], 'PLANNED_BUILT': data['planned']['built'],
            'ELEC_BUILT': e['built'], 'ELEC_PRICE_YEAR': e['price_year'], 'ELEC_GEN_YEAR': e['generation_year'], 'UTIL_YEAR': data['utilities']['year'],
            'CARBON_YEAR': c['data_year'], 'CARBON_BUILT': c['built'], 'SCALE_PRICE_YEAR': s['price_year'], 'SCALE_BUILT': s['built']})
W, WR = data['water'], data['water_rows']; _wc = W['coverage']
assert len(WR) == _wc['rows'], 'water rows differ from the coverage count of the same run'
assert len(W['cells']) == 48 and {(c['res'], c['lead']) for c in W['cells']} == {(r, l) for r in ('mead', 'powell') for l in range(24)}, 'water cells are not 2 lakes by leads 0 to 23'
for _r in ('mead', 'powell'):   # the lead-6 band cell recounts from the rows of the same run
    _rs = [x for x in WR if x['res'] == _r and x['lead'] == 6 and x['outcome'] in ('ABOVE', 'BELOW', 'CONSISTENT')]
    _hb = W['headline_lead6'][_r]['band']; assert (len(_rs), sum(x['outcome'] == 'CONSISTENT' for x in _rs)) == (_hb['n'], _hb['inside']), ('water lead-6 recount', _r)
tok.update({k: f'{v:,}' for k, v in {'N_WATER_REPORTS': _wc['reports'], 'N_WATER_MP': _wc['by_scenario']['MP'], 'N_WATER_MIN': _wc['by_scenario']['MIN'], 'N_WATER_MAX': _wc['by_scenario']['MAX'],
            'N_WATER_ROWS': len(WR), 'N_WATER_CELLS': len(W['cells']), 'N_WATER_BAND_MONTHS': _wc['band_months'], 'N_WATER_SENT_MONTHS': len(W['band_sentence_months']['months']),
            'N_WATER_VARIANTS': len(W['variants']), 'N_WATER_NOTABLE': len(W['notable']), 'N_WATER_RES': len(W['live']['others']), 'N_WATER_THRESH': len(W['live']['thresholds']),
            'N_WATER_GAUGES': len(W['usgs_revisions']['gauges']), 'N_WATER_ERAS': len(W['misread_by_era']), 'N_WATER_FLAG_GROUPS': len(W['flagged']['groups']),
            'N_WATER_CDEC': sum(1 for o in W['live']['others'] if 'CDEC' in o['agency'])}.items()})
tok.update({'WATER_UPDATED': W['updated'], 'WATER_FIRST_ISSUE': _wc['first_issue'], 'WATER_LAST_ISSUE': _wc['last_issue'], 'WATER_MEASURED_LAST': _wc['measured_last']['mead'],
            'WATER_FIRST_READ': W['usgs_revisions']['first_read'], 'WATER_CDEC_NAMES': ' and '.join(o['name'] for o in W['live']['others'] if 'CDEC' in o['agency'])})
assert _wc['measured_last']['mead'] == _wc['measured_last']['powell'] and W['gate'] == 'passed' and not W['stale_sources'], 'water snapshot is not a clean run'
_u, _t, _c, _s, _se, _su, _ch = (data[k] for k in ('uptime', 'time', 'cada', 'secrecords', 'seat', 'support', 'change'))
tok.update({k: f'{v:,}' for k, v in {'N_UP_VENDORS': len(_u['vendors']), 'N_UP_INC': sum(len(v['incidents']) for v in _u['vendors']), 'N_TIME_SERVERS': len(_t['servers']),
            'N_CADA_RES': len(_c['resolvers']), 'N_SEC_DOMAINS': _s['domains'], 'N_SEC_FULL': len(_s['disagree_list']), 'N_SEAT_INC': len(_se['incidents']), 'N_SEAT_FEEDS': len(_se['feeds']),
            'N_SUP_PRODUCTS': _su['products'], 'N_SUP_CYCLES': _su['cycles'], 'N_SUP_BYPROD': len(_su['by_product']), 'N_SUP_SILENT': len(_su['silent_list']),
            'N_CH_SRC': len(_ch['sources']), 'N_CH_UP': len(_ch['upcoming']), 'N_CH_LIST': len(_ch['change_list']), 'N_CH_ROWS': _ch['rows']}.items()})
tok.update({'SEC_LISTDATE': _s['listdate'], 'SEAT_LAST': _se['last_probe'].replace(' UTC', ''), 'CH_FIRST': _ch['first_snapshot'],
            **{'UPD_' + k.upper(): data[k]['updated'][len('10 Nov '):] for k in ('uptime', 'time', 'cada', 'secrecords', 'seat', 'support', 'change')}})
assert all(data[k]['updated'].startswith('10 Nov ') for k in ('uptime', 'time', 'cada', 'secrecords', 'seat', 'support', 'change')), 'SOURCES.md says the desk snapshots are from 10 Nov'
assert _su['all']['unreleased'] == len(_su['silent_list']) and _su['supported_tested'] == _su['all']['tested'], 'support headline and its list differ'
assert all(v['n'] - (v['awaiting'] or 0) == sum(1 for x in _s['disagree_list'] if x['claim'] == k) for k, v in _s['comparison'].items()), 'secrecords read-in-full rows differ from the counts'
_na = [u for u in data['utilities']['utilities'] if u['ba_code'] == 'NA']
tok['N_NA'] = str(len(_na)); tok['NA_STATES'] = ', '.join(f"{st} {n}" for st, n in sorted(__import__('collections').Counter(u['state'] for u in _na).items()))
assert tok['N_SCALE_NOT_PLACED'] == '8' and tok['N_ADDR_STATE'] == '2' and int(tok['N_EPOCH_UNPLACED']) - 8 == 2, 'unplaced counts changed'
assert tok['N_OSM'] == '1,649', 'the page count 1,649 no longer matches the data'
import sys; sys.path.insert(0, H + '/tools'); import coord_scan
_hint = {70557: ', which is in California', 64670: ', which is in California', 70519: ', which is in the Atlantic south of Nantucket',
         68028: ', which is in Mississippi, and its utility is Entergy Mississippi LLC'}
_items = []
for _f, _p, _w in coord_scan.scan_all():
    _r = ' and '.join(x for x in ('outside the state box' if _w['box'] else '', f"{_w['near_km']} km from the nearest record of its state" if _w['near_km'] else '') if x)
    _items.append(f"- `{_f}` code {_p['code']} \"{_p['name']}\": stated state {_p['state']}, point at {_p['lat']}, {_p['lon']}{_hint.get(_p['code'], '')}. Flagged: {_r}.")
assert {70557, 64670, 68028} <= {int(i.split('code ')[1].split(' ')[0]) for i in _items}, 'the scan no longer finds the known records'
tok['COORD_ISSUES'] = ('Rule 1, state box: a record is listed when its point lies more than 1 degree outside an approximate latitude and longitude box for its stated state. '
    'Rule 2, nearest same-state record: plants and planned plants are pooled by stated state, and a record is listed when the nearest other record of its state is more than ' + str(coord_scan.NEAR_KM) + ' km away. Alaska and Hawaii are skipped by rule 2. '
    'Neither rule catches a wrong point that sits close to other records of the state or inside the box. A flag is a reason to look and not a finding. Some remote plants are flagged by rule 2 alone. The rules list ' + str(len(_items)) + ' records.\n\n' + '\n'.join(_items))
_ep = [r for r in csv.DictReader(open(B + 'atlas/raw/epoch/data_centers.csv', encoding='utf-8'))]
_us = [r for r in _ep if r['Country'] == 'United States']; assert len(_us) == len(d['epoch'])
tok['N_EPOCH_ALL'] = str(len(_ep)); tok['N_TAG'] = str(sum(1 for r in _us if '#' in r['Owner'])); tok['N_OWNER_EMPTY'] = str(sum(1 for r in _us if not r['Owner'].strip()))
assert not any(r['Owner'].strip().startswith('#') for r in _us), 'an owner that is only a tag exists'
assert sorted(r['Name'] for r in _us) == sorted(x['name'] for x in d['epoch']), 'Epoch names differ from the pack data'
def fill(t):
    for k, v in tok.items(): t = t.replace('{' + k + '}', str(v))
    left = re.findall(r'\{[A-Z_]+\}', t); assert not left, left
    return t
for f in ('README.md', 'SOURCES.md', 'TESTED.md'): open(D + '/' + f, 'w').write(fill(open(H + '/src/' + f).read()))
for f in ('LICENSE.txt', 'NOTICE.txt'): open(D + '/' + f, 'w').write(fill(open(H + '/src/' + f).read()))
shutil.copy(H + '/src/CITATION.cff', D + '/CITATION.cff')
_paths = lambda f: set(re.findall(r'(?:json|csv|geojson)/[A-Za-z0-9_]+\.(?:json|csv|geojson)', open(D + '/' + f).read()))
assert _paths('LICENSE.txt') == _paths('NOTICE.txt'), ('LICENSE and NOTICE list different files', _paths('LICENSE.txt') ^ _paths('NOTICE.txt'))
assert all(os.path.exists(D + '/' + p) for p in _paths('LICENSE.txt')), 'a listed file is missing from the pack'
_all = {f'{x}/{y}' for x in ('json', 'csv', 'geojson') for y in os.listdir(D + '/' + x)}
assert _all == _paths('LICENSE.txt'), ('files not covered by LICENSE.txt', _all ^ _paths('LICENSE.txt'))
# 4. START_HERE.html from README.md, with the logo
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
md = open(D + '/README.md').read(); body = []
for blk in md.split('\n\n'):
    if blk.strip().startswith('```'): body.append('<pre>' + html.escape(blk.strip().strip('`').strip()) + '</pre>'); continue
    b = html.escape(blk.strip()); b = re.sub(r'`([^`]+)`', r'<code>\1</code>', b); b = re.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
    if b.startswith('# '): continue
    if b.startswith('## '): body.append('<h2>' + b[3:] + '</h2>')
    elif re.match(r'^- ', b): body.append('<ul>' + ''.join('<li>' + re.sub(r'^- ', '', l.strip()) + '</li>' for l in re.split(r'\n(?=- )', b)) + '</ul>')
    else: body.append('<p>' + b.replace('\n', ' ') + '</p>')
css = ('body{font:16px/1.55 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:860px;margin:0 auto;padding:24px 16px}header{display:flex;gap:12px;align-items:center;'
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header h1{font-size:24px;margin:0}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}pre{background:#efe4cf;padding:10px;overflow-x:auto;font-size:14px}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>ATLAS Data Pack</title>\n<style>{css}</style>\n</head>\n<body>\n<main>\n'
    f'<header>{LOGO}<div><h1>ATLAS Data Pack</h1><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/atlas">indahl.ai/atlas</a></span></div></header>\n' + '\n'.join(body) + '\n</main>\n</body>\n</html>\n')
# 5. gate: nothing private, house wording
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|wrangler|(api|secret|access)[_-]?key\s*[=:]\s*\S{8}|(token|password)\s*[=:]\s*["\']?[A-Za-z0-9]{12}|hf_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|[\w.+-]+@[\w-]+\.[a-z]{2,}', re.I)
wording = re.compile(r';|by hand|hand-checked|hand-read|AI-assisted|generated by|written by an AI', re.I)
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f); m = bad.search(open(p, errors='replace').read())
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
        if f in ('README.md', 'SOURCES.md', 'NOTICE.txt', 'LICENSE.txt', 'TESTED.md'):
            m = wording.search(re.sub(r'&[a-z]+;|&#\d+;', '', open(p).read())); assert not m, f'REFUSED wording: {f} contains {m.group(0)!r}'
# 6. zip
z = H + '/dist/atlas-data-pack.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r, _, fs in os.walk(D):
        for f in sorted(fs):
            if '__pycache__' in r or f.endswith('.pyc'): continue
            p = os.path.join(r, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  atlas-data-pack.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', round(os.path.getsize(z) / 1048576, 2), 'MB | sha256', h)
