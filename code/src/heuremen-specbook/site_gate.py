"""site_gate.py [--list] -- every published page checked against site_rules.json (the specbook made machine-readable, 23 Oct 2026).
Exit 1 on any breach. Runs in the heuremen.org / indahl-ai pre-commit hooks and in ledger/ship.sh."""
import json, re, os, html, sys, glob, fnmatch
B = os.path.expanduser('~/bones-forge'); R = json.load(open(os.path.join(B, 'heuremen-specbook', 'site_rules.json')))
def pages():
    for site, globs in R['pages'].items():
        for g in globs:
            for p in sorted(glob.glob(os.path.join(B, g), recursive=True)):
                rel = os.path.relpath(p, B)
                if not any(fnmatch.fnmatch(rel, s) for s in R['skip']): yield site, rel
bad = 0; n = 0
for site, rel in pages():
    n += 1; s = open(os.path.join(B, rel), encoding='utf-8', errors='replace').read()
    for f in R['forbid']:
        if f['where'] in ('all', site) and re.search(f['pattern'], s):
            print(f'  BREACH {f["rule"]:5} {rel}: {f["why"]}'); bad += 1
    ft = R['footer']
    if ft['where'] == site and rel not in ft['exempt'] and ('class="foot"' in s or '<footer' in s):
        txt = lambda h: ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
        blocks = [txt(b) for b in re.findall(r'<p class="foot">(.*?)</p>|<footer>(.*?)</footer>', s, re.S) for b in b if b]
        if txt(ft['html']) not in blocks:
            print(f'  BREACH {ft["rule"]:5} {rel}: no footer block reads exactly the specbook footer'); bad += 1
import importlib.util as _u
_spec = _u.spec_from_file_location('count_scan', os.path.join(B, 'heuremen-specbook', 'count_scan.py')); _cs = _u.module_from_spec(_spec); _spec.loader.exec_module(_cs)
_files = [os.path.join(B, rel) for _, rel in pages()] + [os.path.join(B, 'ligera', f) for f in ('FAULTS.html', 'GUARDS.html')]   # 30 Oct (HEU1-12): experiment pages included
for rel, hit, ctx in _cs.scan(_files):
    print(f'  BREACH 0b.5  {rel}: count in a title/heading/label: {hit!r}'); bad += 1
_spec2 = _u.spec_from_file_location('tone_scan', os.path.join(B, 'heuremen-specbook', 'tone_scan.py')); _ts = _u.module_from_spec(_spec2); _spec2.loader.exec_module(_ts)
for site, rel in pages():
    if site != 'indahl.ai': continue
    for kind, hit in _ts.scan(os.path.join(B, rel)):
        print(f'  BREACH 0b.8  {rel}: tone {kind}: {hit!r}'); bad += 1
# 30 Oct 2026 (Wayfinder: "you ain't got hands" ... "read in full is the best"): public copy says "read in full", never "by hand".
HANDS = re.compile(r'(?i)\bby hand\b|\bhand[- ](?:read|check|count)|\bhand-?checked\b')
_nh = 0
_served = set(re.findall(r"from '\./([^']+\.html)'", open(os.path.join(B, 'indahl-ai', 'pages.js')).read())) if os.path.exists(os.path.join(B, 'indahl-ai', 'pages.js')) else set()   # only pages the site serves (held pages stay on disk unserved)
for p in [os.path.join(B, 'indahl-ai', s) for s in sorted(_served)] + sorted(glob.glob(os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public', '**', '*.js'), recursive=True)):
    rel = os.path.relpath(p, B)
    if any(fnmatch.fnmatch(rel, s) for s in R['skip']) or '.pre-' in rel: continue
    _nh += 1
    if p.endswith('.html'):   # 10 Nov 2026 (cold read BLOCK 1): rules with where "served" run on every served page, subfolders included
        _st = open(p, encoding='utf-8', errors='replace').read()
        for f in R['forbid']:
            if f['where'] == 'served' and re.search(f['pattern'], _st):
                print(f'  BREACH {f["rule"]:5} {rel}: {f["why"]}'); bad += 1
    for m in HANDS.finditer(open(p, encoding='utf-8', errors='replace').read()):
        print(f'  BREACH 0b.9  {rel}: say "read in full": {m.group(0)!r}'); bad += 1; break
    # 8 Nov 2026 (Wayfinder: "always use house externally, not flock, not yet anyway"): public copy says "house", never "flock".
    for m in re.finditer(r'(?i)\bflock', open(p, encoding='utf-8', errors='replace').read()):
        print(f'  BREACH 0b.10 {rel}: say "house", not "flock": {m.group(0)!r}'); bad += 1; break
print(f'site gate: {n} pages, {_nh} served files read for wording; breaches: {bad}'); sys.exit(1 if bad else 0)
