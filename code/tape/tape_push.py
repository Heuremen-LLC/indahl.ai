#!/usr/bin/env python3
"""tape_push.py: commits and pushes only code/tape in the public mirror, so the leaf links on the TAPE page open soon after each run instead of at the next release.
Called in the background by tape_tick.py. Nothing else in the mirror is touched. Any failure is printed and left for the next run or the release script, which pulls and pushes the whole mirror."""
import os, sys, fcntl, subprocess
M = os.environ.get('TAPE_MIRROR') or os.path.expanduser('~/bones-forge/public_mirror/indahl.ai')
def git(*a): return subprocess.run(['git', '-C', M] + list(a), capture_output=True, text=True, timeout=180)
try:
    if not os.path.isdir(M + '/.git'): print('tape push: no mirror clone'); sys.exit(0)
    lock = open(os.path.join(M, '.git', 'tape_push.lock'), 'w')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print('tape push: another push is running'); sys.exit(0)
    uid = subprocess.run(['/opt/homebrew/bin/gh', 'api', 'user', '--jq', '.id'], capture_output=True, text=True, timeout=30).stdout.strip()
    if not uid: print('tape push: gh login missing, skipped'); sys.exit(0)
    # the remote must not be ahead of the mirror: a local commit on top of newer remote commits would make the release script's pull diverge
    if git('fetch', '-q', 'origin').returncode: print('tape push: fetch failed, skipped'); sys.exit(0)
    if git('rev-list', '--count', 'HEAD..origin/main').stdout.strip() not in ('0', ''): print('tape push: the remote has newer commits, left to the release script'); sys.exit(0)
    git('add', 'code/tape')
    if git('diff', '--cached', '--quiet', '--', 'code/tape').returncode == 0: print('tape push: current'); sys.exit(0)
    n = sum(1 for l in open(M + '/code/tape/tape.jsonl') if l.strip())
    c = git('-c', 'user.name=Bones', '-c', 'user.email=%s+indahl-ai@users.noreply.github.com' % uid, 'commit', '-q', '-m',
            'TAPE: chain and leaves through entry %d\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011yBFhLDd1t7vJn7sBCeuZW' % n, '--', 'code/tape')
    if c.returncode: print('tape push: commit failed', (c.stderr or c.stdout)[-200:]); sys.exit(0)
    p = git('push', '-q', 'origin', 'HEAD')
    if p.returncode and git('log', '-1', '--format=%s').stdout.startswith('TAPE: chain'): git('reset', '-q', '--soft', 'HEAD~1')   # undo our commit, the files stay staged for the release script
    print('tape push: entry', n, 'pushed' if p.returncode == 0 else 'not pushed, left for the release script: ' + (p.stderr or p.stdout)[-200:])
except Exception as e: print('tape push: failed', type(e).__name__)
