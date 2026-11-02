"""build_package.py: assembles the MODEL Data Pack from the live MODEL data files into dist/model-data-pack/ and zips it.
Writes the original files unchanged, one CSV per JSON table, SOURCES.md, NOTICE.txt, LICENSE.txt, README, START_HERE.html and verify.py.
Refuses if any file names a local path, a key file, a token, an email address, or if a text file breaks the house wording rules.
Builds locally only. Nothing is published."""
import os, shutil, re, zipfile, hashlib, html, json, csv, importlib.util
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/model-data-pack'
SRC = B + 'cloudflare-workers/heuremen-door/public/hermes/model/'
JSON_FILES = ['claims.json', 'accelerators_summary.json', 'storage_v30_results.json', 'mac_run.jsonl']
shutil.rmtree(H + '/dist', ignore_errors=True)
for s in ('json', 'csv'): os.makedirs(D + '/' + s)
sp = importlib.util.spec_from_file_location('verify', H + '/src/verify.py'); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
shutil.copy(H + '/src/verify.py', D + '/verify.py'); shutil.copy(H + '/src/APACHE-2.0.txt', D + '/APACHE-2.0.txt')
# 1. originals, byte for byte
data = {}
for f in JSON_FILES:
    shutil.copyfile(SRC + f, D + '/json/' + f)
    assert open(SRC + f, 'rb').read() == open(D + '/json/' + f, 'rb').read()
    data[f] = V.load_json(SRC + f)
shutil.copyfile(SRC + 'accelerators.csv', D + '/csv/accelerators.csv')
assert open(SRC + 'accelerators.csv', 'rb').read() == open(D + '/csv/accelerators.csv', 'rb').read()
# 2. CSV
def put_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, lineterminator='\n'); w.writerow(header)
        for r in rows: w.writerow([V.cell(r.get(h)) for h in header])
for t, (jf, rows, count, order) in V.TABLES.items():
    recs = rows(data[jf]); flat = [V.flatten(r) for r in recs]; header = []
    for fr in flat:
        for k in fr:
            if k not in header: header.append(k)
    if order: assert sorted(order) == sorted(header), (t, header); header = order
    put_csv(D + f'/csv/{t}.csv', header, flat)
for ds, (jf, keys) in V.META.items():
    fm = V.meta_want(ds, data[jf]); put_csv(D + f'/csv/{ds}_meta.csv', ['key', 'value'], [{'key': k, 'value': v} for k, v in fm.items()])
# 3. text from templates, counts from the data
c = data['claims.json']; S = c['summary']; cl = c['claims']; fx = sorted({x['source']['fetched'] for x in cl}); assert fx == ['2026-10-28'], fx
assert len({(x['source_key'], x['id']) for x in cl}) == len(cl), 'a source_key and id pair repeats'
mf = S['mlcommons_files']
tok = {'N_CLAIMS': len(cl), 'N_SOURCES': len(S['sources']), 'N_ACC_ROWS': S['accelerator_rows'], 'N_GROUPS': S['accelerator_groups'], 'N_STORAGE': len(data['storage_v30_results.json']['rows']),
       'N_MAC': len(data['mac_run.jsonl']), 'N_LABEL': sum(1 for x in cl if x['label_mismatch'])}
tok = {k: f'{v:,}' for k, v in tok.items()}
tok.update({'FETCHED': fx[0], 'BUILT': S['built'], 'ROWS_V50': f"{mf['v5.0']['rows']:,}", 'ROWS_V51': f"{mf['v5.1']['rows']:,}", 'ROWS_V60': f"{mf['v6.0']['rows']:,}", 'ROWS_V61': f"{mf['v6.1']['rows']:,}",
            'NOACC': f"{mf['v5.0']['excluded_no_accelerator_count']}, {mf['v5.1']['excluded_no_accelerator_count']} and {mf['v6.0']['excluded_no_accelerator_count']}",
            'LATENCY': f"{mf['v5.0']['excluded_latency_units']}, {mf['v5.1']['excluded_latency_units']} and {mf['v6.0']['excluded_latency_units']}"})
assert tok['N_CLAIMS'] == f"{S['claims']:,}"
def fill(t):
    for k, v in tok.items(): t = t.replace('{' + k + '}', str(v))
    left = re.findall(r'\{[A-Z_0-9]+\}', t); assert not left, left
    return t
for f in ('README.md', 'SOURCES.md', 'TESTED.md', 'LICENSE.txt', 'NOTICE.txt'): open(D + '/' + f, 'w').write(fill(open(H + '/src/' + f).read()))
shutil.copy(H + '/src/CITATION.cff', D + '/CITATION.cff')
_paths = lambda f: set(re.findall(r'(?:json|csv)/[A-Za-z0-9_]+\.(?:jsonl|json|csv)', open(D + '/' + f).read()))
assert _paths('LICENSE.txt') == _paths('NOTICE.txt'), ('LICENSE and NOTICE list different files', _paths('LICENSE.txt') ^ _paths('NOTICE.txt'))
assert all(os.path.exists(D + '/' + p) for p in _paths('LICENSE.txt')), 'a listed file is missing from the pack'
_all = {f'{x}/{y}' for x in ('json', 'csv') for y in os.listdir(D + '/' + x)}
assert _all == _paths('LICENSE.txt'), ('files not covered by LICENSE.txt', _all ^ _paths('LICENSE.txt'))
_readme = open(D + '/README.md').read()
for p in _all: assert p in _readme or p.endswith('_meta.csv'), ('README does not mention', p)
for f in ('SOURCES.md', 'NOTICE.txt', 'LICENSE.txt', 'TESTED.md', 'APACHE-2.0.txt', 'verify.py', 'START_HERE.html'):
    pass
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
open(D + '/START_HERE.html', 'w').write(f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>MODEL Data Pack</title>\n<style>{css}</style>\n</head>\n<body>\n<main>\n'
    f'<header>{LOGO}<div><h1>MODEL Data Pack</h1><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/hermes/model">indahl.ai/hermes/model</a></span></div></header>\n' + '\n'.join(body) + '\n</main>\n</body>\n</html>\n')
# 5. gate: nothing private, house wording
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|wrangler|(api|secret|access)[_-]?key\s*[=:]\s*\S{8}|(token|password)\s*[=:]\s*["\']?[A-Za-z0-9]{12}|hf_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|[\w.+-]+@[\w-]+\.[a-z]{2,}', re.I)
wording = re.compile(r';|by hand|hand-checked|hand-read|hand-checked|AI-assisted|AI assistant|generated by|written by an AI|Kory', re.I)
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f); txt = open(p, errors='replace').read(); m = bad.search(txt)
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
        if f in ('README.md', 'SOURCES.md', 'NOTICE.txt', 'LICENSE.txt', 'TESTED.md'):
            m = wording.search(re.sub(r'&[a-z]+;|&#\d+;', '', txt)); assert not m, f'REFUSED wording: {f} contains {m.group(0)!r}'
# 6. zip
z = H + '/dist/model-data-pack.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r, _, fs in os.walk(D):
        for f in sorted(fs):
            if '__pycache__' in r or f.endswith('.pyc'): continue
            p = os.path.join(r, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  model-data-pack.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', round(os.path.getsize(z) / 1048576, 2), 'MB | sha256', h)
