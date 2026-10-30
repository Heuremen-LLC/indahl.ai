#!/usr/bin/env python3
"""readcheck_hook.py: git pre-commit gate for the check block. Heuremen LLC, 30 Oct 2026.
A staged reading file (results, readings, hand-checks, outcomes, by name) needs the nearest CHECKS.md at or above its folder staged in the
same commit, and the staged additions to that CHECKS.md must hold one complete entry (readcheck.py check-staged).
Which files count as readings: the regular expression in READCHECK_PATTERN, or the default below, matched against the file name.
A skip is allowed and goes on the record: READCHECK_SKIP="why" git commit ...   (written to .git/readcheck_skips.jsonl)."""
import os, re, sys, json, subprocess, datetime
RC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'readcheck.py')
PAT = re.compile(os.environ.get('READCHECK_PATTERN') or r'(^|[_-])(results?|readings?)([_.-]|$)|^HANDCHECK|^outcomes_.*\.json$', re.I)
def git(*a): return subprocess.run(['git', *a], capture_output=True, text=True).stdout
top = git('rev-parse', '--show-toplevel').strip(); gitdir = git('rev-parse', '--absolute-git-dir').strip()
staged = [f for f in git('diff', '--cached', '--name-only', '--diff-filter=ACMR').splitlines() if f]
hits = [f for f in staged if PAT.search(os.path.basename(f))]
if not hits: sys.exit(0)
skip = os.environ.get('READCHECK_SKIP', '').strip()
if skip:
    open(os.path.join(gitdir, 'readcheck_skips.jsonl'), 'a').write(json.dumps({'t': datetime.datetime.now().isoformat(timespec='seconds'), 'files': hits, 'why': skip}) + '\n')
    print('readcheck: skipped on the record (%s)' % skip); sys.exit(0)
bad = []; seen = {}
for f in hits:
    d = os.path.dirname(f); found = None
    while True:
        c = os.path.join(d, 'CHECKS.md') if d else 'CHECKS.md'
        if os.path.exists(os.path.join(top, c)): found = c; break
        if not d: break
        d = os.path.dirname(d)
    if found is None: bad.append('%s: no CHECKS.md at or above its folder. Start one: python3 %s new %s --packs <Q,L,P,O> --what "<the reading>"' % (f, RC, os.path.dirname(os.path.join(top, f)) or top)); continue
    if found not in staged: bad.append('%s: %s is not staged with it (add the check entry for this reading)' % (f, found)); continue
    if found not in seen:
        r = subprocess.run([sys.executable, RC, 'check-staged', found], capture_output=True, text=True, cwd=top); seen[found] = (r.returncode, r.stdout.strip())
    if seen[found][0]: bad.append('%s: %s' % (f, seen[found][1]))
if bad:
    print('READCHECK REFUSED this commit (a reading goes in with its check block):'); print('\n'.join('  ' + b for b in bad)); sys.exit(1)
print('readcheck: %d reading file(s) carry a complete check entry' % len(hits))
