"""build_package.py: assembles the QIA Research Package from public sources into dist/qia-research-package/ and zips it.
Only public files go in: our own code folders on github.com/Heuremen-LLC/indahl.ai, the faultsguards release from PyPI, YO's reader, our PDFs.
Refuses if any file names a local path, a key file or a token variable with a value."""
import os, shutil, re, zipfile, hashlib, urllib.request, html, json
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/qia-research-package'
PUB = B + 'public_mirror/indahl.ai/code/'
shutil.rmtree(H + '/dist', ignore_errors=True); os.makedirs(D)
def cp(src, dst): os.makedirs(os.path.dirname(D + '/' + dst), exist_ok=True); shutil.copy(src, D + '/' + dst)
for f in ('qia_check.py', 'README.md', 'CITATION.cff', 'TESTED.md'): cp(H + '/src/' + f, f)
cp(B + 'public_mirror/indahl.ai/LICENSE.txt', 'LICENSE.txt')
cp(B + 'yo/release/yo_audit.py', 'yo/yo_audit.py')
for f in ('run_check.py', 'PLAN.md', 'README.md', 'requirements.txt'): cp(PUB + 't1t2-check/' + f, 't1t2-check/' + f)
CB = B + 'iris_package/dist/iris-research-package/check-block'   # 2 Nov: the cleaned check block, built and tested in the IRIS package
assert os.path.isdir(CB), 'build the IRIS package first'
for r, _, fs in os.walk(CB):
    for f in fs:
        if '__pycache__' in r or f.endswith('.pyc'): continue
        p = os.path.join(r, f); cp(p, 'check-block/' + os.path.relpath(p, CB))
cp(B + 'indahl-ai/quantum-idle-audit.pdf', 'papers/a-readout-is-not-an-idle.pdf')
def get(u, dst):
    os.makedirs(os.path.dirname(D + '/' + dst), exist_ok=True)
    open(D + '/' + dst, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'heuremen-package/1.0'}), timeout=60).read())
pj = json.load(urllib.request.urlopen('https://pypi.org/pypi/faultsguards/json', timeout=60)); v = pj['info']['version']
whl = [u for u in pj['releases'][v] if u['filename'].endswith('.whl')][0]; get(whl['url'], 'faultsguards/' + whl['filename'])
assert hashlib.sha256(open(D + '/faultsguards/' + whl['filename'], 'rb').read()).hexdigest() == whl['digests']['sha256'], 'wheel hash differs from PyPI'
get('https://heuremen.org/faults.pdf', 'faultsguards/faults.pdf'); get('https://heuremen.org/guards.pdf', 'faultsguards/guards.pdf')
open(D + '/yo/README.md', 'w').write('# YO\n\nHeuremen LLC. YO reads an IBM calibration record and flags stale and zero entries. The exact answer computed by code is printed beside it.\n\n'
    'Model: https://huggingface.co/indahl/YO\n\n```\npip install mlx-lm            # Apple silicon\npython yo_audit.py record.json --model indahl/YO\n\n'
    'pip install transformers torch  # elsewhere\npython yo_audit.py record.json --fused indahl/YO\n```\n\nEvery result: https://indahl.ai/iris/lab\n')
# START_HERE.html from README.md, with the logo
md = open(H + '/src/README.md').read(); body = []
for blk in md.split('\n\n'):
    b = html.escape(blk.strip()); b = re.sub(r'`([^`]+)`', r'<code>\1</code>', b); b = re.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
    if b.startswith('# '): continue
    if b.startswith('## '): body.append('<h2>' + b[3:] + '</h2>')
    elif re.match(r'^(-|\d\.) ', b): body.append('<ul>' + ''.join('<li>' + re.sub(r'^(-|\d\.) ', '', l.strip()) + '</li>' for l in re.split(r'\n(?=(?:-|\d\.) )', b)) + '</ul>')
    else: body.append('<p>' + b.replace('\n', ' ') + '</p>')
import importlib.util; sp = importlib.util.spec_from_file_location('qc', H + '/src/qia_check.py'); qc = importlib.util.module_from_spec(sp); sp.loader.exec_module(qc)
css = ('body{font:16px/1.55 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:860px;margin:0 auto;padding:24px 16px}header{display:flex;gap:12px;align-items:center;'
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:24px}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>QIA Research Package</title><style>{css}</style><main>'
    f'<header>{qc.LOGO}<div><b>QIA Research Package</b><br><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/qia">indahl.ai/qia</a></span></div></header>' + '\n'.join(body) + '</main></html>')
# gate: nothing private
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|\.ibm_.*crn|wrangler|IBM_QUANTUM_TOKEN="?[A-Za-z0-9]{10}|hf_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}')
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f)
        if p.endswith(('.pdf', '.whl')): continue
        m = bad.search(open(p, errors='replace').read())
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
z = H + '/dist/qia-research-package.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r, _, fs in os.walk(D):
        for f in sorted(fs):
            if '__pycache__' in r or f.endswith('.pyc'): continue
            p = os.path.join(r, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  qia-research-package.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', os.path.getsize(z) // 1024, 'KB | sha256', h[:16], '| faultsguards', v)
