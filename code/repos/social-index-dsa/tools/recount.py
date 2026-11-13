"""recount.py: independent recount of delivered counts straight from the aggregate files (pyarrow.dataset filters, no reducer)."""
import sys, os, site, glob, datetime as D
sys.path.append(site.getusersitepackages())
import pyarrow.dataset as ds, pyarrow.compute as pc, pyarrow as pa
R = '/Users/heuremen/bones-forge/social_index/dsa/data/raw/agg/unz/'
def files(kind, months):
    out = []
    for m in months:
        out += [p for p in glob.glob(R + 'aggregated-%s-%s-01/**/*.parquet' % (kind, m), recursive=True) if os.path.isfile(p) and not os.path.basename(p).startswith('.')]
    return out
ALL = ['2025-%02d' % m for m in range(7, 13)] + ['2026-%02d' % m for m in range(1, 12)]
def count(kind, platform, basis, a, b, months=ALL, extra=None):
    d = ds.dataset(files(kind, months), format='parquet')
    col = 'application_date' if basis == 'app' else 'created_at'
    f = (ds.field('platform_name') == platform) & (ds.field(col) >= pa.scalar(D.datetime.fromisoformat(a), pa.timestamp('us'))) & (ds.field(col) < pa.scalar(D.datetime.fromisoformat(b) + D.timedelta(days=1), pa.timestamp('us')))
    if extra is not None: f = f & extra
    t = d.to_table(columns=['count', 'automated_decision'], filter=f)
    g = t.group_by(['automated_decision']).aggregate([('count', 'sum')]).to_pylist()
    res = {x['automated_decision']: x['count_sum'] for x in g}; res['ALL'] = sum(res.values()); return res
for plat, per, basis in [('YouTube', ('2026-01-01', '2026-06-30'), 'cre'), ('YouTube', ('2026-01-01', '2026-06-30'), 'app'), ('X', ('2026-01-01', '2026-06-30'), 'app'), ('Facebook', ('2026-01-01', '2026-06-30'), 'app'), ('Instagram', ('2026-01-01', '2026-06-30'), 'app'), ('Temu', ('2025-07-01', '2025-12-31'), 'app'), ('Google Shopping', ('2025-07-01', '2025-12-31'), 'app')]:
    print(plat, per, basis, count('complete', plat, basis, *per))
# scout's YouTube figure came from the simple aggregate, created Jan-Jun 2026
s = count('simple', 'YouTube', 'cre', '2026-01-01', '2026-06-30', months=['2026-%02d' % m for m in range(1, 7)])
print('SIMPLE YouTube created 2026H1', s)
dbl = ['2026-02-09', '2026-02-10', '2026-02-11', '2026-02-12', '2026-05-30', '2026-05-31']
sd = sum(count('simple', 'YouTube', 'cre', x, x, months=['2026-02', '2026-05'])['ALL'] for x in dbl)
cd = sum(count('complete', 'YouTube', 'cre', x, x, months=['2026-02', '2026-05'])['ALL'] for x in dbl)
print('YouTube on the six double days: simple', sd, 'complete', cd, 'excess', sd - cd)
