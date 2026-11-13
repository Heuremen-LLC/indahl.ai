"""day_compare.py: per created_at day totals over all platforms, simple against complete aggregate, for one month."""
import sys, os, site, glob, collections as C
sys.path.append(site.getusersitepackages())
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
def days(ud):
    tot = C.Counter(); per_file = C.defaultdict(C.Counter)
    for p in glob.glob(os.path.join(ud, '**', '*.parquet'), recursive=True):
        if not os.path.isfile(p) or os.path.basename(p).startswith('.'): continue
        t = pq.read_table(p, columns=['created_at', 'count']); d = pc.strftime(t['created_at'], format='%Y-%m-%d')
        g = pa.table({'d': d, 'c': t['count']}).group_by(['d']).aggregate([('c', 'sum')])
        uu = os.path.basename(p).split('-', 2)[2].split('.c000')[0]
        for k, v in zip(g['d'].to_pylist(), g['c_sum'].to_pylist()): tot[k] += v; per_file[k][uu] += v
    return tot, per_file
ym = sys.argv[1]; R = '/Users/heuremen/bones-forge/social_index/dsa/data/raw/agg/unz/'
s, sf = days(R + 'aggregated-simple-%s-01' % ym); c, cf = days(R + 'aggregated-complete-%s-01' % ym)
for d in sorted(set(s) | set(c)):
    flag = '' if s.get(d, 0) == c.get(d, 0) else '  DIFF %+d  simple jobs=%d complete jobs=%d' % (s.get(d, 0) - c.get(d, 0), len(sf[d]), len(cf[d]))
    print(d, s.get(d, 0), c.get(d, 0), flag)
