"""sweep_backups.py -- MOVE (never delete) every backup file and folder out of the served public folder and the public mirror
into the private archive: ~/bones-forge/archive_private/public_backups/<date>/<label>/<relative path>, with a manifest (path, size, sha256, mtime).
Heuremen LLC, 11 Nov 2026 (Wayfinder: backups into our private archives). Run by ship.sh step 1. Prints "swept N".
  sweep_backups.py [--dry]"""
import os, sys, time, shutil, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backup_patterns as bp
A = bp.B + '/archive_private/public_backups'
def files_of(p):
    if os.path.isdir(p): return [os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs]
    return [p]
def main():
    dry = '--dry' in sys.argv; found = bp.find()
    if not found: print('swept 0'); return
    day = time.strftime('%Y%m%d'); dest = f'{A}/{day}'; rows = []
    for lab, root, rel, isd in found:
        src = f'{root}/{rel}'; dst = f'{dest}/{lab}/{rel}'
        for f in files_of(src):
            st = os.stat(f); h = hashlib.sha256(open(f, 'rb').read()).hexdigest()
            rows.append({'label': lab, 'path': os.path.relpath(f, root), 'size': st.st_size, 'sha256': h, 'mtime': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(st.st_mtime)), 'moved_to': os.path.relpath(f.replace(src, dst, 1), bp.B)})
        if dry: continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):   # same path swept earlier the same day: keep both
            dst += time.strftime('.%H%M%S')
        shutil.move(src, dst)
    if not dry:
        mf = f'{dest}/MANIFEST_{time.strftime("%H%M%S")}.jsonl'
        with open(mf, 'w') as fh:
            for r in rows: fh.write(json.dumps(r) + '\n')
    print(f'swept {len(rows)} files ({len(found)} top-level items){" (dry)" if dry else ""}')
main()
