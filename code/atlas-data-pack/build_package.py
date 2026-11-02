"""build_package.py: assembles the ATLAS Data Pack from the live ATLAS data files into dist/atlas-data-pack/ and zips it.
Writes the original JSON unchanged, one CSV per table, GeoJSON for point data, SOURCES.md, NOTICE.txt, README, START_HERE.html and verify.py.
Refuses if any text file names a local path, a key file, a token, an email address, or breaks the house wording rules.
Builds locally only. Nothing is published."""
import os, shutil, re, zipfile, hashlib, html, json, csv, importlib.util
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/atlas-data-pack'
SRC = B + 'cloudflare-workers/heuremen-door/public/atlas/'
FILES = ['datacenters', 'electricity', 'utilities', 'plants', 'planned', 'carbon', 'scale']
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
    fm = V.flat_meta({k: data[ds][k] for k in keys}); put_csv(D + f'/csv/{ds}_meta.csv', ['key', 'value'], [{'key': k, 'value': v} for k, v in fm.items()])
# 3. text from templates, counts from the data
d, e, c, s = data['datacenters'], data['electricity'], data['carbon'], data['scale']
tok = {'N_OSM': len(d['osm']), 'N_EPOCH': len(d['epoch']), 'N_EPOCH_UNPLACED': sum(1 for x in d['epoch'] if x['lat'] is None), 'N_PLANTS': len(data['plants']['plants']),
       'N_PLANNED': len(data['planned']['plants']), 'N_STATES': len(e['states']), 'N_UTIL': len(data['utilities']['utilities']), 'N_CARBON_STATES': len(c['states']),
       'N_SUBREGIONS': len(c['subregions']), 'N_SITES': len(s['sites']), 'N_SCALE_STATES': len(s['states']), 'N_CORR': len(s['corrections'])}
tok = {k: f'{v:,}' for k, v in tok.items()}
tok.update({'DC_PULLED': d['pulled'], 'OSM_PAGE_COUNT': '1,649 of 1,853 features kept', 'PLANTS_BUILT': data['plants']['built'], 'PLANNED_BUILT': data['planned']['built'],
            'ELEC_BUILT': e['built'], 'ELEC_PRICE_YEAR': e['price_year'], 'ELEC_GEN_YEAR': e['generation_year'], 'UTIL_YEAR': data['utilities']['year'],
            'CARBON_YEAR': c['data_year'], 'CARBON_BUILT': c['built'], 'SCALE_PRICE_YEAR': s['price_year'], 'SCALE_BUILT': s['built']})
assert tok['N_OSM'] == '1,649', 'the page count 1,649 no longer matches the data'
def fill(t):
    for k, v in tok.items(): t = t.replace('{' + k + '}', str(v))
    left = re.findall(r'\{[A-Z_]+\}', t); assert not left, left
    return t
for f in ('README.md', 'SOURCES.md'): open(D + '/' + f, 'w').write(fill(open(H + '/src/' + f).read()))
for f in ('NOTICE.txt', 'CITATION.cff'): shutil.copy(H + '/src/' + f, D + '/' + f)
shutil.copy(B + 'public_mirror/indahl.ai/LICENSE.txt', D + '/LICENSE.txt')
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
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:24px}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}pre{background:#efe4cf;padding:10px;overflow-x:auto;font-size:14px}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ATLAS Data Pack</title><style>{css}</style><main>'
    f'<header>{LOGO}<div><b>ATLAS Data Pack</b><br><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/atlas">indahl.ai/atlas</a></span></div></header>' + '\n'.join(body) + '</main></html>')
# 5. gate: nothing private, house wording
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|wrangler|(api|secret|access)[_-]?key\s*[=:]\s*\S{8}|(token|password)\s*[=:]\s*["\']?[A-Za-z0-9]{12}|hf_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|[\w.+-]+@[\w-]+\.[a-z]{2,}', re.I)
wording = re.compile(r';|by hand|hand-checked|hand-read|AI-assisted|generated by|written by an AI', re.I)
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f); m = bad.search(open(p, errors='replace').read())
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
        if f in ('README.md', 'SOURCES.md', 'NOTICE.txt'):
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
