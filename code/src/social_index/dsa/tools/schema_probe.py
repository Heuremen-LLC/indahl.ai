"""schema_probe.py: print the schema and the distinct values of categorical columns of one aggregate month. No counts by platform."""
import sys, glob, os, collections, site
sys.path.append(site.getusersitepackages())
import pyarrow.parquet as pq, pyarrow as pa, pyarrow.compute as pc
root = sys.argv[1]
files = sorted(f for f in glob.glob(os.path.join(root, '**', '*.parquet'), recursive=True) if os.path.isfile(f) and not os.path.basename(f).startswith('.'))
uu = collections.Counter(os.path.basename(f).split('-', 2)[2].split('.c000')[0] for f in files)
print('part files', len(files), 'job uuids', len(uu))
sch = pq.read_schema(files[0]); print(sch)
for f in files[1:]:
    s = pq.read_schema(f)
    if s.names != sch.names: print('SCHEMA DIFFERS', f, set(s.names) ^ set(sch.names))
cols = [c for c in ['platform_name', 'automated_decision', 'automated_detection', 'source_type', 'decision_ground', 'category', 'decision_account', 'decision_provision', 'decision_monetary', 'account_type', 'incompatible_content_illegal'] if c in sch.names]
vals = {c: set() for c in cols}
for f in files:
    t = pq.read_table(f, columns=cols)
    for c in cols: vals[c] |= set(pc.unique(t[c]).to_pylist())
for c in cols:
    v = sorted(vals[c], key=lambda x: (x is None, str(x)))
    print('\n##', c, len(v)); print(v if c != 'platform_name' else '(%d names)' % len(v))
open(sys.argv[2], 'w').write('\n'.join(sorted(str(x) for x in vals.get('platform_name', set()))))
