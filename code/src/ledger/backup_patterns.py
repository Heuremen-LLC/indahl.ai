"""backup_patterns.py -- one list of what counts as a backup file or folder. Used by sweep_backups.py (ship.sh step 1), the backups gate (ship.sh step 3) and push_public.sh.
Heuremen LLC, 11 Nov 2026. A path is a backup when any part of it is named like one (a backup folder holds backups)."""
import os, re, sys
PAT = re.compile(r'(\.bak($|[-._])|[._]bak-|\.pre-|~$|\.orig$|\.rej$|\.swp$|\.old$|\.tmp$|^\.#|\.pre$)')
B = os.path.expanduser('~/bones-forge')
ROOTS = {'public': B + '/cloudflare-workers/heuremen-door/public', 'mirror_indahl.ai': B + '/public_mirror/indahl.ai'}
def is_backup(name): return bool(PAT.search(name))
def find(roots=None):
    """top-most backup files and folders: [(label, root, relpath, is_dir)]"""
    out = []
    for lab, r in (roots or ROOTS).items():
        for d, ds, fs in os.walk(r):
            ds[:] = [x for x in ds if x != '.git']
            for x in list(ds):
                if is_backup(x): out.append((lab, r, os.path.relpath(os.path.join(d, x), r), True)); ds.remove(x)
            out += [(lab, r, os.path.relpath(os.path.join(d, f), r), False) for f in fs if is_backup(f)]
    return sorted(out, key=lambda t: (t[0], t[2]))
def count(): return len(find())
if __name__ == '__main__':
    f = find()
    for lab, r, rel, isd in f: print('  BACKUP', lab, rel + ('/' if isd else ''))
    print(f'backups gate: {len(f)} in public'); sys.exit(1 if f else 0)
