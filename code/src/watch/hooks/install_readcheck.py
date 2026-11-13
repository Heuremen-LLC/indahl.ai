#!/usr/bin/env python3
"""install_readcheck.py: put the readcheck line in every ~/bones-forge repo's pre-commit (existing hooks kept, line appended before any exit),
and in the global git template so new repos (qia_runs/<run>) get it at git init. Safe to run again."""
import os, glob, subprocess
B = os.path.expanduser('~/bones-forge'); LINE = '"$HOME/bones-forge/watch/hooks/readcheck_hook.sh" || exit 1   # readcheck gate (30 Oct)'
OFF = ('heuremen.org', 'indahl-ai', 'public_mirror', 'llama.cpp', 'muse-glimmer-mlx', 'ane-track', 'bones-memory-repo', 'archive', 'touring-sage')
def put(hookdir):
    os.makedirs(hookdir, exist_ok=True); p = os.path.join(hookdir, 'pre-commit')
    t = open(p).read() if os.path.exists(p) else '#!/bin/sh\n'
    if 'readcheck_hook' in t: return 'had it'
    if t.rstrip().splitlines()[-1].strip().startswith(('exit 0', 'exec ')): ls = t.rstrip().splitlines(); t = '\n'.join(ls[:-1] + [LINE, ls[-1]]) + '\n'
    else: t = t.rstrip('\n') + '\n' + LINE + '\n'
    open(p, 'w').write(t); os.chmod(p, 0o755); return 'added'
n = {}
for g in sorted(glob.glob(B + '/**/.git', recursive=True)):
    repo = os.path.dirname(g); rel = os.path.relpath(repo, B)
    if rel.split('/')[0] in OFF or not os.path.isdir(g) or '/venv' in rel or 'site-packages' in rel: continue
    hp = subprocess.run(['git', '-C', repo, 'config', 'core.hooksPath'], capture_output=True, text=True).stdout.strip()
    r = put(os.path.join(repo, hp) if hp else os.path.join(g, 'hooks')); n[r] = n.get(r, 0) + 1
T = os.path.expanduser('~/.git-templates'); print('template:', put(T + '/hooks'))
cur = subprocess.run(['git', 'config', '--global', 'init.templateDir'], capture_output=True, text=True).stdout.strip()
if not cur: subprocess.run(['git', 'config', '--global', 'init.templateDir', T]); print('init.templateDir set to', T)
elif cur != T: print('init.templateDir already', cur, '(left as is; add the line there by hand)')
print('repos:', n)
