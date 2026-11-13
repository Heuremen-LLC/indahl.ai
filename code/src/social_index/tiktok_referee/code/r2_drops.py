"""Referee pass 2: what each gate drops, by side, Apr-Jun 2026 and every quarter (decision date), plus territorial scopes."""
import duckdb, glob, datetime as D, json, collections
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/'
con = duckdb.connect()
fs = sorted(glob.glob(P + 'raw/dsa_tiktok/complete_*.parquet'))
con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
w = "application_day between DATE '2026-04-01' and DATE '2026-06-30'"
q = lambda s: con.execute(s).fetchall()
print('Apr-Jun 2026, removals, not ads, by exclusive content class:')
for nm, cond in (('video', 'ct_video'), ('image (no video)', 'ct_image and not ct_video'), ('synthetic only', 'ct_synthetic_media and not ct_video and not ct_image'),
                 ('text (no video/image)', 'ct_text and not ct_video and not ct_image'), ('account', 'ct_account and not ct_video'), ('audio', 'ct_audio and not ct_video'),
                 ('other', 'ct_other and not ct_video and not ct_image')):
    print('  %-22s %12d' % (nm, q("select coalesce(sum(n),0) from c where dv_removed and not ct_ad and %s and %s" % (cond, w))[0][0]))
print('  ads removed (video)   %12d' % q("select coalesce(sum(n),0) from c where dv_removed and ct_ad and ct_video and " + w)[0][0])
cols = [r[0] for r in q('describe c')]
print('  columns:', [x for x in cols if x.startswith('dv_') or x.startswith('ct_')])
for col in [x for x in cols if x.startswith('dv_') and x != 'dv_removed']:
    print('  video, not removed, %s: %d' % (col, q("select coalesce(sum(n),0) from c where ct_video and not ct_ad and not dv_removed and %s and %s" % (col, w))[0][0]))
print('  point set by decision_ground:', q("select decision_ground, sum(n) from c where dv_removed and ct_video and not ct_ad and %s group by 1" % w))
print('  point set by source_type:', q("select source_type, sum(n) from c where dv_removed and ct_video and not ct_ad and %s group by 1" % w))
print('territorial scopes of video removals (all decision dates):')
sc = q("select territorial_scope, sum(n) from c where dv_removed and ct_video and not ct_ad group by 1 order by 2 desc")
for s, n in sc[:12]: print('   %-40s %d' % (str(s)[:40], n))
print('   distinct scopes', len(sc))
# source type by quarter, point set, decision date
print('source type by quarter (point set, decision date):')
for y in (2023, 2024, 2025, 2026):
    for n_ in (1, 2, 3, 4):
        a = D.date(y, 3*n_-2, 1); b = D.date(y + (n_ == 4), (3*n_) % 12 + 1, 1) - D.timedelta(days=1)
        if a < D.date(2023, 10, 1) or a > D.date(2026, 4, 1): continue
        r = dict(q("select source_type, sum(n) from c where dv_removed and ct_video and not ct_ad and application_day between DATE '%s' and DATE '%s' group by 1" % (a, b)))
        t = sum(r.values()); nv = t - r.get('SOURCE_VOLUNTARY', 0)
        print('  %dQ%d total %10d non-voluntary %8d (%.3f%%) %s' % (y, n_, t, nv, 100 * nv / t, {k[7:]: v for k, v in r.items() if k != 'SOURCE_VOLUNTARY'}))
