"""Build the public indahl.ai worker from heuremen-door: drop the code only the retired flock hosts reach, strip comments, drop unused bindings.
Writes build/worker.js and build/wrangler.toml. Never edits the live files. Every cut is anchored to exact text and refuses if an anchor is missing."""
import os, re, subprocess, sys
SRC = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')
s = open(SRC + '/worker.js').read()
def cut_between(start, end, keep_end=True):
    global s
    i = s.find(start); j = s.find(end, i + 1)
    if i < 0 or j < 0: sys.exit('ANCHOR MISSING: %r .. %r' % (start[:40], end[:40]))
    s = s[:i] + (s[j:] if keep_end else s[j + len(end):])
def rep(a, b):
    global s
    if s.count(a) != 1: sys.exit('ANCHOR %d times: %r' % (s.count(a), a[:60]))
    s = s.replace(a, b)
cut_between('// heuremen-door (Bones, 7 Oct 2026)', '// 21 Oct 2026 (Wayfinder: "make Indahl.ai our consulting page")')   # header quotes, HOUSE, SERVICE, PAGE, COMPANY
cut_between('// 29 Oct 2026 (his word): every outside domain shows the same door', '// 10 Nov 2026 (findable pass)')         # DOOR_HEADERS and doorPage
s = re.sub(r"\n\s*const home = HOUSE\.includes\(ip\)[^\n]*", '', s, count=1)
s = re.sub(r"\n\s*if \(u\.pathname === '/__house'\)[^\n]*", '', s, count=1)
s = re.sub(r"\n\s*if \(host === 'thetrailtothepast\.online'[^\n]*", '', s, count=1)
rep("    const b = SERVICE[host];\n    if (home && b && env[b]) return env[b].fetch(req);\n    return doorPage(host, env);",
    "    return Response.redirect('https://indahl.ai/', 301);")
for w in ('HOUSE', 'SERVICE', 'doorPage', 'COMPANY', 'home &&', '73.248.227.244'):
    if re.search(r'\b' + re.escape(w) + r'\b' if w.isidentifier() else re.escape(w), s): sys.exit('LEFTOVER: ' + w)
os.makedirs(OUT, exist_ok=True); tmp = OUT + '/_cut.js'; open(tmp, 'w').write(s)
# strip comments with a real parser (esbuild ships with wrangler); no bundling, imports kept as they are
r = subprocess.run(['npx', '--yes', 'esbuild@0.24.0', tmp, '--format=esm', '--legal-comments=none', '--log-level=error'], capture_output=True, text=True, cwd=SRC)
if r.returncode: sys.exit('esbuild failed: ' + r.stderr[:400])
js = r.stdout.replace("'../../indahl-ai/", "'../../indahl-ai/")
open(OUT + '/worker.js', 'w').write('// indahl.ai worker (Heuremen LLC). Serves indahl.ai and its MTA-STS host. Built from the private source by kibble/worker-clean/clean_worker.py.\n' + js)
os.remove(tmp)
# wrangler.toml: drop every [[services]] block (the retired flock bindings); keep assets, KV, D1, vars
t = open(SRC + '/wrangler.toml').read()
t = re.sub(r'\[\[services\]\]\nbinding = "[A-Z_]+"\nservice = "[a-z0-9-]+"\n\n?', '', t)
if '[[services]]' in t: sys.exit('services left in wrangler.toml')
open(OUT + '/wrangler.toml', 'w').write(t)
print('built: worker.js %d bytes, wrangler.toml %d bytes' % (len(js), len(t)))
