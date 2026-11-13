#!/usr/bin/env python3
"""site_lock.py (10 Nov 2026): the ONE way to hold the site-edit lock.

The old .site_edit.lock was a label file that agents overwrote, so turns were lost. This tool holds a real
kernel lock (fcntl) on .site_edit.flock for as long as your command runs. Waiters block in line and get the lock
the moment the holder's command ends, even if it crashes. The label file still shows who holds it.

  python3 ~/bones-forge/ledger/site_lock.py run --label "SOLAR desk" -- bash -c 'python3 patch_site.py && bash ~/bones-forge/ledger/ship.sh "SOLAR desk"'
  python3 ~/bones-forge/ledger/site_lock.py who

Put the build_site.py edit AND ship.sh inside the one command, so nobody edits between your edit and your ship."""
import fcntl, os, subprocess, sys, time

D = os.path.dirname(os.path.abspath(__file__))
FLOCK, LABEL = os.path.join(D, '.site_edit.flock'), os.path.join(D, '.site_edit.lock')


def main():
    a = sys.argv[1:]
    if not a or a[0] == 'who':
        print(open(LABEL).read().strip() if os.path.exists(LABEL) else 'free'); return 0
    if a[0] != 'run' or '--' not in a:
        print(__doc__); return 2
    label = a[a.index('--label') + 1] if '--label' in a else 'unnamed'
    cmd = a[a.index('--') + 1:]
    f = open(FLOCK, 'a+')
    t0 = time.time()
    print(f'site_lock: waiting for the lock ({open(LABEL).read().strip() if os.path.exists(LABEL) else "free"})', flush=True)
    fcntl.flock(f, fcntl.LOCK_EX)   # blocks until free; released by the kernel if this process dies
    open(LABEL, 'w').write(f'{label} (pid {os.getpid()}) since {time.strftime("%H:%M:%S")}, via site_lock.py\n')
    print(f'site_lock: held after {time.time() - t0:.0f}s as "{label}"', flush=True)
    os.environ['SITE_LOCK_HELD'] = label   # ship.sh checks this and re-runs itself under the lock if it is missing
    try:
        rc = subprocess.call(cmd)
    finally:
        open(LABEL, 'w').write(f'free (last: {label}, released {time.strftime("%H:%M:%S")})\n')
        fcntl.flock(f, fcntl.LOCK_UN)
    print(f'site_lock: released, command exit {rc}', flush=True)
    return rc


if __name__ == '__main__':
    sys.exit(main())
