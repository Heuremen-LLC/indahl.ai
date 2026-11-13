#!/usr/bin/env python3
"""reproduce.py -- Heuremen LLC (https://indahl.ai/reproduce). Standard library plus git. MIT license.

  python3 reproduce.py list                 the desks that have a kit, with their expected output sha256
  python3 reproduce.py fetch <desk> [--dir D] fetch one kit (git sparse checkout of reproduce/<desk> from github.com/Heuremen-LLC/indahl.ai)
  python3 reproduce.py run <desk> [--dir D]   fetch, then print the commit, the kit files and the command it would run; runs nothing
  python3 reproduce.py run <desk> --ref <sha> --yes-commit <sha>
                                              runs the kit's own `python3 run.py --check`, only if the fetched commit is exactly <sha>
  --ref <commit or tag>                       fetch that commit instead of the current main branch

The kit's run.py checks the sha256 of every input before it runs and checks its one line of output against expected.json. This script
adds nothing to that check: it fetches, runs and prints what the kit printed, with the kit's exit code. It runs code downloaded from
the repository, so it runs only with --yes-commit equal to the commit fetched, which binds
the go to the exact code the user reviewed. Exit 3 means nothing was run. A matching sha256 shows the kit reproduces its published output with the desk's own code,
not that the measurement is right."""
import argparse, json, os, re, subprocess, sys, urllib.request
REPO = 'https://github.com/Heuremen-LLC/indahl.ai'; RAW = 'https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/main/reproduce/README.md'
def desks():
    t = urllib.request.urlopen(urllib.request.Request(RAW, headers={'User-Agent': 'heuremen-reproduce/1.0'}), timeout=30).read().decode()
    return re.findall(r'\| \[([A-Z0-9]+)\]\(([a-z0-9]+)/\) \| ([^|]+) \| `([0-9a-f]{64})` \|', t)
def fetch(desk, base, ref=None):
    if not re.fullmatch(r'[a-z0-9]+', desk): sys.exit(f'not a desk name: {desk}')
    if ref and not re.fullmatch(r'[0-9a-fA-F]{7,40}|[A-Za-z0-9][A-Za-z0-9._/-]*', ref): sys.exit(f'not a commit or tag: {ref}')
    d = os.path.join(base, 'indahl-reproduce')
    if not os.path.isdir(os.path.join(d, '.git')):
        subprocess.run(['git', 'clone', '--filter=blob:none', '--sparse', '--no-checkout', '--', REPO, d], check=True)
    url = subprocess.run(['git', '-C', d, 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
    if url.rstrip('/').removesuffix('.git') != REPO: sys.exit(f'{d} points at {url}, not {REPO}; use another --dir')
    subprocess.run(['git', '-C', d, 'sparse-checkout', 'set', '--no-cone', f'/reproduce/{desk}/'], check=True)
    subprocess.run(['git', '-C', d, 'fetch', '--filter=blob:none', '--', 'origin', ref or 'main'], check=True)
    subprocess.run(['git', '-C', d, 'checkout', '--detach', 'FETCH_HEAD'], check=True, capture_output=True)
    k = os.path.join(d, 'reproduce', desk)
    if not os.path.isfile(os.path.join(k, 'run.py')): sys.exit(f'no kit named {desk}; run: reproduce.py list')
    return k
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True); sp.add_parser('list')
    for c in ('fetch', 'run'):
        p = sp.add_parser(c); p.add_argument('desk'); p.add_argument('--dir', default='.'); p.add_argument('--ref')
        if c == 'run': p.add_argument('--yes-commit', dest='yes_commit', help='run the kit, only if the fetched commit is exactly this sha')
    a = ap.parse_args()
    if a.cmd == 'list':
        for name, slug, inputs, sha in desks(): print(f'{slug:12s} {inputs.strip():18s} {sha}')
        return
    desk = a.desk.lower().strip('/'); k = fetch(desk, os.path.abspath(a.dir), a.ref)
    commit = subprocess.run(['git', '-C', k, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    print(f'kit: {k}\ncommit: {commit} ({REPO}/tree/{commit}/reproduce/{desk})', flush=True)
    if a.cmd == 'fetch': return
    print(f'command: {sys.executable} run.py --check   (in {k})', flush=True)
    if not a.yes_commit:
        print(f'not run: read the kit README.md and run.py, then rerun with --ref {commit} --yes-commit {commit} to execute it'); sys.exit(3)
    if a.yes_commit != commit: sys.exit(f'commit moved: fetched {commit}, approved {a.yes_commit}; review again')
    r = subprocess.run([sys.executable, 'run.py', '--check'], cwd=k)
    print(f'kit exit code: {r.returncode}'); sys.exit(r.returncode)
if __name__ == '__main__': main()
