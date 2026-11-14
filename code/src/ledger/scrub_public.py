#!/usr/bin/env python3
"""scrub_public.py (13 Nov 2026, Wayfinder: "the council lane full scrub from anything public. Real Sage still gets all the commits.")
Runs on the public mirror (public_mirror/indahl.ai) right before push_public.sh commits it.
  1. Deletes the retired the council lane site files that the page mirror keeps after they leave the served folder.
  2. In every other text file, rewrites the the council lane terms in the PUBLIC COPY only (house originals are untouched):
     "the council lane" (not followed by a letter, so "Sage VERDICT" and every credit to Sage stay) -> "the council lane",
     council / council / council in paths and names -> "council".
  3. Gate: exits 1 if any the council lane term is left anywhere in the mirror outside .git, listing each file.
Usage: python3 scrub_public.py [--check]   (--check: gate only, no rewrite)"""
import os, re, sys
M = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai')
TERM = re.compile(r'the council lane(?![A-Za-z])|sage[-_]v(?![a-z])|council', re.I)
RETIRED = ['iris/lab-live.js', 'iris/lab/live.html', 'iris/lab/live/index.html']
TXT = ('.py', '.md', '.js', '.json', '.html', '.txt', '.sh', '.csv', '.tsv', '.yml', '.yaml', '.toml', '.xml', '.cff', '.jsonl')

def sub(t):
    t = re.sub(r'the council lane(?![A-Za-z])', 'the council lane', t)
    return re.sub(r'sage[-_]v(?![a-z])|council', 'council', t, flags=re.I)

def main():
    check = '--check' in sys.argv; changed = removed = 0
    if not check:
        for r in RETIRED:
            p = os.path.join(M, r)
            if os.path.isfile(p): os.remove(p); removed += 1
    left = []
    for d, ds, fs in os.walk(M):
        ds[:] = [x for x in ds if x != '.git']
        for f in fs:
            p = os.path.join(d, f)
            if not f.endswith(TXT) and TERM.search(f) is None: continue
            try: t = open(p, encoding='utf-8').read()
            except (UnicodeDecodeError, OSError): continue
            if not TERM.search(t): continue
            if check: left.append(os.path.relpath(p, M)); continue
            open(p, 'w', encoding='utf-8').write(sub(t)); changed += 1
            if TERM.search(open(p, encoding='utf-8').read()): left.append(os.path.relpath(p, M))
    if left:
        print('scrub gate: the council lane terms remain in the public mirror:'); [print('  ' + x) for x in left]; sys.exit(1)
    print(f'scrub gate: no the council lane term in the public mirror ({removed} retired file(s) removed, {changed} file(s) rewritten)')

if __name__ == '__main__': main()
