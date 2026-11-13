#!/usr/bin/env python3
"""readcheck_hook.py: pre-commit gate (30 Oct 2026). A staged reading file (results, readings, hand-checks, outcomes, IRIS rows, the Book)
needs the nearest CHECKS.md at or above its folder staged in the same commit, and the staged additions must hold one complete check entry
(watch/readcheck.py). Off for the site repos that ship.sh and push_public.sh commit automatically, and for anything outside ~/bones-forge.
Escape hatch on the record: READCHECK_SKIP="why" git commit ...   (logged to watch/readcheck_skips.jsonl)."""
import os, re, sys, json, subprocess, datetime
B = os.path.expanduser('~/bones-forge'); RC = B + '/watch/readcheck.py'
OFF = ('heuremen.org', 'indahl-ai', 'public_mirror', 'llama.cpp', 'muse-glimmer-mlx', 'ane-track', 'bones-memory-repo', 'archive', 'touring-sage')
PAT = re.compile(r'(^|[_-])(results?|readings?)([_.-]|$)|^HANDCHECK|^outcomes_.*\.json$|_IRIS\.md$|^THE_BOOK|^IRIS_BOOK_register\.json$', re.I)
def git(*a): return subprocess.run(['git', *a], capture_output=True, text=True).stdout
top = git('rev-parse', '--show-toplevel').strip()
rel = os.path.relpath(top, B) if top.startswith(B + '/') else None
if rel is None or rel.split('/')[0] in OFF: sys.exit(0)
staged = [f for f in git('diff', '--cached', '--name-only', '--diff-filter=ACMR').splitlines() if f]
hits = [f for f in staged if PAT.search(os.path.basename(f))]
if not hits: sys.exit(0)
skip = os.environ.get('READCHECK_SKIP', '').strip()
if skip:
    open(B + '/watch/readcheck_skips.jsonl', 'a').write(json.dumps({'t': datetime.datetime.now().isoformat(timespec='seconds'), 'repo': rel, 'files': hits, 'why': skip}) + '\n')
    print('readcheck: skipped on the record (%s)' % skip); sys.exit(0)
bad = []; ok_checked = {}
for f in hits:
    d = os.path.dirname(f); found = None
    while True:
        c = os.path.join(d, 'CHECKS.md') if d else 'CHECKS.md'
        if os.path.exists(os.path.join(top, c)): found = c; break
        if not d: break
        d = os.path.dirname(d)
    if found is None: bad.append('%s: no CHECKS.md at or above its folder. Start one: python3 %s new %s --packs <Q,L,P,O> --what "<the reading>"' % (f, RC, os.path.dirname(os.path.join(top, f)))); continue
    if found not in staged: bad.append('%s: %s is not staged with it (add the check entry for this reading)' % (f, found)); continue
    if found not in ok_checked:
        r = subprocess.run([sys.executable, RC, 'check-staged', found], capture_output=True, text=True, cwd=top); ok_checked[found] = (r.returncode, r.stdout.strip())
    if ok_checked[found][0]: bad.append('%s: %s' % (f, ok_checked[found][1]))
if bad:
    print('READCHECK REFUSED this commit (a reading goes in with its check block):'); print('\n'.join('  ' + b for b in bad)); sys.exit(1)
print('readcheck: %d reading file(s) carry a complete check entry' % len(hits))
