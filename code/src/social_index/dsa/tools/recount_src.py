"""recount_src.py: independent recount of source_type x decision_ground for chosen platforms and periods (application basis), straight from the aggregate files."""
import sys, os, site, glob, datetime as D
sys.path.append(site.getusersitepackages())
import pyarrow.dataset as ds, pyarrow as pa
R = '/Users/heuremen/bones-forge/social_index/dsa/data/raw/agg/unz/'
fs = [p for p in glob.glob(R + 'aggregated-complete-*/**/*.parquet', recursive=True) if os.path.isfile(p) and not os.path.basename(p).startswith('.')]
d = ds.dataset(fs, format='parquet')
for plat, a, b in [('X', '2025-07-01', '2025-12-31'), ('X', '2026-01-01', '2026-06-30'), ('Snapchat', '2026-01-01', '2026-06-30'), ('LinkedIn', '2025-07-01', '2025-12-31'), ('Apple', None, None)]:
    if plat == 'Apple': plat, a, b = 'App Store', '2026-01-01', '2026-06-30'
    f = (ds.field('platform_name') == plat) & (ds.field('application_date') >= pa.scalar(D.datetime.fromisoformat(a), pa.timestamp('us'))) & (ds.field('application_date') < pa.scalar(D.datetime.fromisoformat(b) + D.timedelta(days=1), pa.timestamp('us')))
    t = d.to_table(columns=['count', 'source_type', 'decision_ground', 'automated_detection'], filter=f)
    g = sorted(t.group_by(['source_type', 'decision_ground']).aggregate([('count', 'sum')]).to_pylist(), key=lambda x: -x['count_sum'])
    print(plat, a, b, [(x['source_type'].replace('SOURCE_', ''), x['decision_ground'].replace('DECISION_GROUND_', ''), x['count_sum']) for x in g])
