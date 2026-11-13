import duckdb, sys
con = duckdb.connect()
g = sys.argv[1]
src = "read_parquet('%s/**/*.parquet', hive_partitioning=true, union_by_name=true)" % g
for r in con.execute('describe select * from ' + src).fetchall(): print(r[0], r[1])
print(con.execute("select platform_name, sum(count) from %s where platform_name ilike '%%tiktok%%' group by 1" % src).fetchall())
