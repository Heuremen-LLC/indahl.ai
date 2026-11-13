import duckdb, sys, glob, os, re, collections
con = duckdb.connect()
g = sys.argv[1]
files = sorted(f for f in glob.glob(g + '/**/*.parquet', recursive=True) if os.path.isfile(f) and not os.path.basename(f).startswith('.'))
by = collections.defaultdict(list)
for f in files:
    m = re.search(r'part-\d+-([0-9a-f-]{36})', os.path.basename(f))
    by[m.group(1) if m else os.path.basename(f)].append(f)
for u, fs in by.items():
    lst = ','.join("'%s'" % f for f in fs)
    r = con.execute("select min(created_at), max(created_at), sum(count), sum(count) filter (where platform_name='TikTok') from read_parquet([%s], union_by_name=true)" % lst).fetchone()
    print(u, len(fs), r)
    days = con.execute("select cast(created_at as date) d, sum(count) filter (where platform_name='TikTok') from read_parquet([%s], union_by_name=true) group by 1 order by 1" % lst).fetchall()
    print('   TikTok days:', [(str(d), n) for d, n in days if n][:40])
