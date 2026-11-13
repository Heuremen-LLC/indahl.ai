"""HEU2-15: try to rebuild Faults 45 ("about 1,805 words of copy before, 542 after", six pages) and Guards 39
("catches that morning's version 23 times") from indahl-ai git history, 23 Oct 2026. Read only: git show to stdout.
Word count = words in tone_scan.visible() (the gate's own notion of visible copy)."""
import subprocess, sys, re, html
sys.path.insert(0, '/Users/heuremen/bones-forge/heuremen-specbook')
import tone_scan as T
REPO = '/Users/heuremen/bones-forge/indahl-ai'
def show(c, f):
    r = subprocess.run(['git', '-C', REPO, 'show', f'{c}:{f}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
def ls(c):
    r = subprocess.run(['git', '-C', REPO, 'ls-tree', '--name-only', c], capture_output=True, text=True)
    return [x for x in r.stdout.split() if x.endswith('.html')]
commits = sys.argv[1:]
import tempfile, os
tmp = tempfile.mkdtemp(dir='/Users/heuremen/bones-forge/watch/site_pass_20261030/heu/fg_fix')
for c in commits:
    files = ls(c)
    tot = 0; hits = 0; per = []
    for f in files:
        s = show(c, f)
        if s is None: continue
        w = len(T.visible(s).split())
        p = os.path.join(tmp, f.replace('/', '_')); open(p, 'w').write(s)
        h = T.scan(p)
        per.append((f, w, len(h))); tot += w; hits += len(h)
    print(f'{c}: {len(per)} top-level html, words {tot}, tone hits {hits}')
    for f, w, h in per: print(f'    {f:28s} {w:5d} words  {h:3d} hits')
