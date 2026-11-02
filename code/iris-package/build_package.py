"""build_package.py: assembles the IRIS Research Package from public sources into dist/iris-research-package/ and zips it.
Only public files go in: our own code folders on github.com/Heuremen-LLC/indahl.ai, the faultsguards release from PyPI, the Faults and Guards PDFs.
Refuses if any file names a local path, a key file, a token, an email address or an internal label, or if the README links anywhere off the allowed list.
Builds locally only. It does not deploy, push or send anything."""
import os, shutil, re, zipfile, hashlib, urllib.request, html, json, subprocess, sys
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/iris-research-package'
PUB = B + 'public_mirror/indahl.ai/code/'
shutil.rmtree(H + '/dist', ignore_errors=True); os.makedirs(D)
SKIP = lambda r, f: '__pycache__' in r or f.endswith('.pyc') or f == '.DS_Store'
def cp(src, dst): os.makedirs(os.path.dirname(D + '/' + dst), exist_ok=True); shutil.copy(src, D + '/' + dst)
def cptree(src, dst):
    for r, _, fs in os.walk(src):
        for f in fs:
            if SKIP(r, f): continue
            p = os.path.join(r, f); cp(p, dst + '/' + os.path.relpath(p, src))
for f in ('iris_check.py', 'README.md', 'CITATION.cff'): cp(H + '/src/' + f, f)
cptree(H + '/src/tests', 'tests')
cp(B + 'public_mirror/indahl.ai/LICENSE.txt', 'LICENSE.txt')
cptree(PUB + 'checks', 'check-block')
cp(H + '/src/check-block/SPEC.md', 'check-block/SPEC.md'); cp(H + '/src/check-block/example/CHECKS.md', 'check-block/example/CHECKS.md')   # our own clean versions: core, pack L and pack P only; the original example stays out
def patch(path, pairs):
    t = open(D + '/' + path, encoding='utf-8').read()
    for old, new in pairs:
        assert t.count(old) >= 1, f'patch target missing in {path}: {old[:50]!r}'; t = t.replace(old, new)
    open(D + '/' + path, 'w', encoding='utf-8').write(t)
import re as _re
rc = open(D + '/check-block/readcheck.py', encoding='utf-8').read()
a0 = rc.index("PACKS = {'Q'"); a1 = rc.index("         'L': [")
rc = rc[:a0] + "PACKS = {" + rc[a1 + len("         "):]
b0 = rc.index(",\n         'O': ["); b1 = rc.index("]}", b0)
rc = rc[:b0] + "}" + rc[b1 + 2:]
open(D + '/check-block/readcheck.py', 'w', encoding='utf-8').write(rc)
patch('check-block/readcheck.py', [("--packs Q,L,P,O --what", "--packs L,P --what"), ("Packs: Q quantum hardware, L language-model evaluations, P public copy, O live operations.", "Packs: L language-model evaluations, P public copy."),
    ("(watch/readcheck.py)", "(readcheck.py)"), ("'parser read in full before any rate'", "'parser read in full before any rate'"), ("'ledger first, one release path, verified live'", "'source first, one release path, verified live'"),
    ("'house style rules'", "'style rules written down and checked'"), ("substituted with counts and an addendum", "substituted with counts and a note written first")])
patch('check-block/readcheck_hook.py', [("results, readings, hand-checks, outcomes, by name", "results, readings, parser-check files, outcomes, by name"), ("<Q,L,P,O>", "<L,P>")])
patch('check-block/README.md', [
    ("the packs for quantum hardware (Q), language-model evaluations (L), public\n  copy (P) and live operations (O). Each pack line comes from a mistake we made, with its date.", "the packs for language-model evaluations (L) and public\n  copy (P)."),
    (" Our own release ledger runs the same check, so a new public number, or a change to one,\nis refused without a complete entry.", ""),
    ("`example/CHECKS.md`: a real entry, from our pass over every page of indahl.ai with this block on 30 October 2026.", "`example/CHECKS.md`: a fictional entry, written to show the format."),
    ("python3 readcheck.py new path/to/run", "mkdir -p path/to/run     # the folder given to new must exist\npython3 readcheck.py new path/to/run")])
IR = PUB + 'iris/'
for f in ('items.json', 'score.py', 'synth.py'): cp(IR + 'faultsbench/' + f, 'faultsbench/' + f)
cp(H + '/src/replycheck.py', 'parser-check/replycheck.py')
open(D + '/faultsbench/README.md', 'w').write('# Faults and Guards bench: scorer and planted items\n\nHeuremen LLC. `items.json` holds the planted items, each with its own truth. `score.py` scores replies written as `out/<model>/<arm>.jsonl` '
    '(arms bare, bare_copy and guard, one JSON object per line with id, raw and done_reason) and writes `results.json`. `synth.py` runs the scorer on planted worlds and asserts the expected outcomes. Run it from inside this folder, because it reads `items.json` and imports `score.py` from the current folder.\n\n'
    '```\ncd faultsbench\npython synth.py\n```\n\nThe prompts (`items.py`), the runner and the plan are in the repository: https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/iris/faultsbench\n')
def get(u, dst):
    os.makedirs(os.path.dirname(D + '/' + dst), exist_ok=True)
    open(D + '/' + dst, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'heuremen-package/1.0'}), timeout=60).read())
pj = json.load(urllib.request.urlopen('https://pypi.org/pypi/faultsguards/json', timeout=60)); v = pj['info']['version']
whl = [u for u in pj['releases'][v] if u['filename'].endswith('.whl')][0]; get(whl['url'], 'faultsguards/' + whl['filename'])
assert hashlib.sha256(open(D + '/faultsguards/' + whl['filename'], 'rb').read()).hexdigest() == whl['digests']['sha256'], 'wheel hash differs from PyPI'
get('https://heuremen.org/faults.pdf', 'faultsguards/faults.pdf'); get('https://heuremen.org/guards.pdf', 'faultsguards/guards.pdf')
for p in ('faults.pdf', 'guards.pdf'): assert open(D + '/faultsguards/' + p, 'rb').read(5) == b'%PDF-', p + ' is not a PDF'
# START_HERE.html from README.md, with the logo
md = open(H + '/src/README.md').read(); body = []
for blk in md.split('\n\n'):
    b = html.escape(blk.strip()); b = re.sub(r'`([^`]+)`', r'<code>\1</code>', b); b = re.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
    if b.startswith('# '): continue
    if b.startswith('## '): body.append('<h2>' + b[3:] + '</h2>')
    elif re.match(r'^(-|\d\.) ', b): body.append('<ul>' + ''.join('<li>' + re.sub(r'^(-|\d\.) ', '', l.strip()) + '</li>' for l in re.split(r'\n(?=(?:-|\d\.) )', b)) + '</ul>')
    else: body.append('<p>' + b.replace('\n', ' ') + '</p>')
import importlib.util; sp = importlib.util.spec_from_file_location('ic', H + '/src/iris_check.py'); ic = importlib.util.module_from_spec(sp); sys.dont_write_bytecode = True; sp.loader.exec_module(ic)
css = ('body{font:16px/1.55 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:860px;margin:0 auto;padding:24px 16px}header{display:flex;gap:12px;align-items:center;'
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:24px}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IRIS Research Package</title><style>{css}</style><main>'
    f'<header>{ic.LOGO}<div><b>IRIS Research Package</b><br><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/iris">indahl.ai/iris</a></span></div></header>' + '\n'.join(body) + '</main></html>')
# gate: nothing private
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|\.ibm_.*crn|wrangler|\bKV\b|IBM_QUANTUM_TOKEN="?[A-Za-z0-9]{10}|hf_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}|[\w.+-]+@(?!example\.(invalid|com)\b)[\w-]+\.[a-z]{2,}'
                 r'|Wayfinder|\bNova\b|his word|Armature|127\.0\.0\.1:11500|\bBones\b')
INTERNAL = re.compile(r'watch/|release ledger|ledger first|three-box|\bbill\b|\bhis\b|\(\d{1,2}[–-]?\d* ?Oct|ROUND_S|Addendum|\bS[123]\b|\bpack Q\b', re.I)
HANDS = re.compile(r'by hand|hand-read|hand-checked|hand-reads')
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f)
        if p.endswith(('.pdf', '.whl')): continue
        m = bad.search(open(p, errors='replace').read())
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
        t = open(p, errors='replace').read(); m = HANDS.search(t)
        if m: raise AssertionError(f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}')
        m = INTERNAL.search(t)
        if m and ('/check-block/' in p or p.endswith(('replycheck.py', 'README.md'))): raise AssertionError(f'REFUSED: {os.path.relpath(p, D)} contains internal wording {m.group(0)!r}')
ALLOWED = re.compile(r'^https://(indahl\.ai/iris(/list|/key|/package)?|github\.com/Heuremen-LLC/indahl\.ai(/tree/main/code/[\w./-]+)?|pypi\.org/project/faultsguards/|huggingface\.co/indahl)$')
for f in ('README.md', 'faultsbench/README.md', 'CITATION.cff'):
    t = open(D + '/' + f).read()
    for u in re.findall(r'https://[^\s)"`>]+', t): assert ALLOWED.match(u), f'REFUSED: {f} links to {u}'
    assert ';' not in t.replace('\n', ' ') or f == 'CITATION.cff', f'REFUSED: semicolon in {f}'
# tests run against the assembled copy
r = subprocess.run([sys.executable, '-B', D + '/tests/test_iris_check.py'], capture_output=True, text=True, cwd=H)
assert r.returncode == 0, 'REFUSED: tests failed\n' + r.stderr[-1500:]
r = subprocess.run([sys.executable, '-B', 'synth.py'], capture_output=True, text=True, cwd=D + '/faultsbench')
assert r.returncode == 0 and 'SYNTH PASS' in r.stdout, 'REFUSED: synth failed\n' + r.stderr[-800:]
for r_, _, fs in os.walk(D):
    for f in fs:
        if SKIP(r_, f): os.remove(os.path.join(r_, f))
shutil.rmtree(D + '/faultsbench/__pycache__', ignore_errors=True)
for jf in ('results.json',):
    if os.path.exists(D + '/faultsbench/' + jf): os.remove(D + '/faultsbench/' + jf)
z = H + '/dist/iris-research-package.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r_, _, fs in os.walk(D):
        for f in sorted(fs):
            if SKIP(r_, f): continue
            p = os.path.join(r_, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  iris-research-package.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', os.path.getsize(z) // 1024, 'KB | sha256', h[:16], '| faultsguards', v)
