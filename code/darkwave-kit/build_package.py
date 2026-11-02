"""build_package.py: assembles the Darkwave Correction Kit from public sources into dist/darkwave-correction-kit/ and zips it.
Refuses if any text file names a local path, a key file or a token."""
import os, shutil, re, zipfile, hashlib, html, importlib.util
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/darkwave-correction-kit'
RUN = B + 'public_mirror/indahl.ai/code/readout-correction/run/data/'
shutil.rmtree(H + '/dist', ignore_errors=True); os.makedirs(D)
def cp(src, dst): os.makedirs(os.path.dirname(D + '/' + dst), exist_ok=True); shutil.copy(src, D + '/' + dst)
for f in ('darkwave_kit.py', 'README.md', 'CITATION.cff', 'requirements.txt'): cp(H + '/src/' + f, f)
cp(B + 'public_mirror/indahl.ai/LICENSE.txt', 'LICENSE.txt')
for chip in ('ibm_kingston', 'ibm_marrakesh'): cp(RUN + f'fresh_kicks_{chip}.json', f'examples/table_31oct2026_{chip}.json')
open(D + '/examples/README.md', 'w').write('# Example tables\n\nThe tables measured minutes before our 31 October 2026 run (fields k4 and k8: degrees per readout from blocks of 4 and 8 readouts, cohD8: coherence of the idle comparison). '
    'They are in the study\'s format and cannot be used with the kit\'s apply command. They come from the study\'s public files (https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/readout-correction/run/data) and show the size of the turn we saw. They are not a table for your run.\n')
sp = importlib.util.spec_from_file_location('qc', B + 'qia_package/src/qia_check.py'); qc = importlib.util.module_from_spec(sp); sp.loader.exec_module(qc)
md = open(H + '/src/README.md').read(); body = []
for blk in md.split('\n\n'):
    b = html.escape(blk.strip()); b = re.sub(r'`([^`]+)`', r'<code>\1</code>', b); b = re.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
    if b.startswith('# '): continue
    if b.startswith('## '): body.append('<h2>' + b[3:] + '</h2>')
    elif re.match(r'^(-|\d\.) ', b): body.append('<ul>' + ''.join('<li>' + re.sub(r'^(-|\d\.) ', '', l.strip()) + '</li>' for l in re.split(r'\n(?=(?:-|\d\.) )', b)) + '</ul>')
    else: body.append('<p>' + b.replace('\n', ' ') + '</p>')
css = ('body{font:16px/1.55 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:860px;margin:0 auto;padding:24px 16px}header{display:flex;gap:12px;align-items:center;'
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:24px}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Darkwave Correction Kit</title><style>{css}</style><main>'
    f'<header>{qc.LOGO}<div><b>Darkwave Correction Kit</b><br><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/darkwave">indahl.ai/darkwave</a></span></div></header>' + '\n'.join(body) + '</main></html>')
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|\.ibm_.*crn|wrangler|<our IBM instance>|hf_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}')
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f); m = bad.search(open(p, errors='replace').read())
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
z = H + '/dist/darkwave-correction-kit.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r, _, fs in os.walk(D):
        for f in sorted(fs):
            if '__pycache__' in r or f.endswith('.pyc'): continue
            p = os.path.join(r, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  darkwave-correction-kit.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', os.path.getsize(z) // 1024, 'KB | sha256', h[:16])
