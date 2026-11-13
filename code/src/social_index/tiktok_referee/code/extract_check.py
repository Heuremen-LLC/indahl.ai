"""Referee: re-extract TikTok rows from a Commission complete-aggregate month and compare with the desk's grouped parquet.
Usage: extract_check.py <unzipped dir> <desk parquet>"""
import duckdb, sys, glob, os
con = duckdb.connect()
g, desk = sys.argv[1], sys.argv[2]
files = sorted(f for f in glob.glob(g + '/**/*.parquet', recursive=True) if os.path.isfile(f) and not os.path.basename(f).startswith('.'))
con.execute("create view raw as select * from read_parquet([%s], union_by_name=true) where platform_name = 'TikTok'" % ','.join("'%s'" % f for f in files))
con.execute("create view desk as select * from read_parquet('%s')" % desk)
cols = [r[0] for r in con.execute('describe raw').fetchall()]
def b(c):
    return 'coalesce(%s,false)' % c if c in cols else 'false'
R = {
 'all': 'true',
 'video_removed_noad': "%s and %s and not %s" % (b('DECISION_VISIBILITY_CONTENT_REMOVED'), b('CONTENT_TYPE_VIDEO'), b('CONTENT_TYPE_AD')),
}
D = {
 'all': 'true',
 'video_removed_noad': 'dv_removed and ct_video and not ct_ad',
}
for k in R:
    print('==', k)
    for dim_raw, dim_desk in (("source_type", "source_type"), ("automated_decision", "automated_decision"),
                              ("strftime(cast(application_date as date),'%Y-%m')", "strftime(application_day,'%Y-%m')"),
                              ("coalesce(territorial_scope,'')", "territorial_scope"), ("decision_ground", "decision_ground"),
                              ("strftime(cast(created_at as date),'%Y-%m-%d')", "strftime(created_day,'%Y-%m-%d')")):
        a = dict(con.execute("select %s, sum(count) from raw where %s group by 1" % (dim_raw, R[k])).fetchall())
        d = dict(con.execute("select %s, sum(n) from desk where %s group by 1" % (dim_desk, D[k])).fetchall())
        keys = set(a) | set(d)
        diff = {x: (a.get(x), d.get(x)) for x in keys if (a.get(x) or 0) != (d.get(x) or 0)}
        print('  %-50s raw_total=%s desk_total=%s mismatching_keys=%d %s' % (dim_raw[:50], sum(v for v in a.values() if v), sum(v for v in d.values() if v), len(diff), list(diff.items())[:5]))
# days posted to decision, point set
a = dict(con.execute("""select case when application_date is null or content_date is null then null else greatest(-1, least(31, date_diff('day', cast(content_date as date), cast(application_date as date)))) end, sum(count)
         from raw where %s group by 1""" % R['video_removed_noad']).fetchall())
d = dict(con.execute("select dd, sum(n) from desk where %s group by 1" % D['video_removed_noad']).fetchall())
print('  dd mismatches:', {x: (a.get(x), d.get(x)) for x in set(a) | set(d) if (a.get(x) or 0) != (d.get(x) or 0)})
print('  dd raw (point set):', sorted(((k if k is not None else -99), v) for k, v in a.items())[:8])
# content types removed, all removals
for ct in ['VIDEO','IMAGE','SYNTHETIC_MEDIA','OTHER','TEXT','ACCOUNT','AUDIO','AD','LINK','PRODUCT','APP','STICKER','HASHTAG']:
    a = con.execute("select coalesce(sum(count),0) from raw where %s and %s" % (b('DECISION_VISIBILITY_CONTENT_REMOVED'), b('CONTENT_TYPE_' + ct))).fetchone()[0]
    d = con.execute("select coalesce(sum(n),0) from desk where dv_removed and ct_%s" % ct.lower()).fetchone()[0]
    print('  removed & %-16s raw=%12d desk=%12d %s' % (ct, a, d, 'OK' if a == d else 'DIFF'))
