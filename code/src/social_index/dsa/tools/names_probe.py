"""names_probe.py: union of platform_name values per month across the complete aggregates. Names only, no counts."""
import sys, glob, os, site
sys.path.append(site.getusersitepackages())
import pyarrow.parquet as pq, pyarrow.compute as pc
root = sys.argv[1]; per = {}
for d in sorted(glob.glob(os.path.join(root, 'aggregated-complete-*'))):
    m = d.rsplit('-', 3)[-3] + '-' + d.rsplit('-', 3)[-2]
    s = set()
    for f in glob.glob(os.path.join(d, '**', '*.parquet'), recursive=True):
        if os.path.isfile(f) and not os.path.basename(f).startswith('.'):
            s |= set(pc.unique(pq.read_table(f, columns=['platform_name'])['platform_name']).to_pylist())
    per[m] = s
allnames = set().union(*per.values())
import re
pat = re.compile(sys.argv[2], re.I)
for n in sorted(allnames, key=str):
    if pat.search(str(n)): print(repr(n), ''.join('x' if n in per[m] else '.' for m in sorted(per)))
print('months', sorted(per)); print('total names', len(allnames))
