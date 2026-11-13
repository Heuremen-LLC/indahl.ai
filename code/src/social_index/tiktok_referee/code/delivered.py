"""Referee recount of the delivered side (DSA database, TikTok) from the desk's grouped month files, which the referee
checked against two Commission months downloaded independently (exact match). Own SQL, own windows."""
import duckdb, glob, json, datetime as D, sys
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/raw/dsa_tiktok/'
con = duckdb.connect()
fs = sorted(glob.glob(P + 'complete_*.parquet'))
fs = [f for f in fs if not f.endswith('_alldays.json')]
con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
SETS = {
    'lower': "dv_removed and ct_video and not ct_ad and decision_ground = 'DECISION_GROUND_INCOMPATIBLE_CONTENT'",
    'point': "dv_removed and ct_video and not ct_ad",
    'upper': "dv_removed and not ct_ad and (ct_video or ct_image or ct_synthetic_media or (ct_other and not (ct_account or ct_link or ct_sticker or ct_hashtag or ct_product or ct_app or ct_text or ct_audio)))",
    'video_or_image': "dv_removed and not ct_ad and (ct_video or ct_image)",
}
def q_bounds(q):
    y, n = int(q[:4]), int(q[5]); a = D.date(y, 3*n-2, 1)
    b = D.date(y + (n == 4), (3*n) % 12 + 1, 1) - D.timedelta(days=1)
    return a, b
def W(a, b):
    d = D.timedelta(days=1)
    return {'app': "application_day between DATE '%s' and DATE '%s'" % (a, b),
            'app-1': "application_day between DATE '%s' and DATE '%s'" % (a-d, b-d),
            'app+1': "application_day between DATE '%s' and DATE '%s'" % (a+d, b+d),
            'created': "created_day between DATE '%s' and DATE '%s'" % (a, b)}
def agg(where):
    r = con.execute("""select coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0),
        coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_PARTIALLY'),0),
        coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0), coalesce(sum(n) filter (where dd=0),0),
        coalesce(sum(n) filter (where dd between 0 and 1),0), coalesce(sum(n) filter (where dd is null or dd<0),0),
        coalesce(sum(n) filter (where automated_detection='Yes'),0) from c where """ + where).fetchone()
    return dict(n=int(r[0]), fully=int(r[1]), partially=int(r[2]), vol=int(r[3]), d0=int(r[4]), d01=int(r[5]), bad=int(r[6]), det=int(r[7]))
QS = sys.argv[1:] or ['2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2']
out = {}
for q in QS:
    a, b = q_bounds(q); ws = W(a, b); g = {}
    for s, sw in SETS.items():
        for w, ww in ws.items():
            g[s + '|' + w] = agg('(%s) and (%s)' % (sw, ww))
    # Addendum 2.2 allowance: statements created on 31 Oct / 3 Nov 2026 with decision in the widened window, upper set
    allow = {}
    for key in ('n', 'fully'):
        vals = [agg("(%s) and application_day between DATE '%s' and DATE '%s' and created_day = DATE '%s'" % (SETS['upper'], a - D.timedelta(days=1), b + D.timedelta(days=1), d))[key] for d in ('2026-10-31', '2026-11-03')]
        allow[key] = 2 * max(vals)
    out[q] = dict(grid=g, allow=allow)
    P_ = g['point|app']
    print(q, 'point n=%d fully=%.4f vol=%.5f d0=%.4f d01=%.4f bad=%.4f partially=%.4f det=%.4f | created n=%d | allowance n=%d fully=%d' % (
        P_['n'], P_['fully']/P_['n'], P_['vol']/P_['n'], P_['d0']/P_['n'], P_['d01']/P_['n'], P_['bad']/P_['n'], P_['partially']/P_['n'], P_['det']/P_['n'],
        g['point|created']['n'], allow['n'], allow['fully']))
json.dump(out, open('/Users/heuremen/bones-forge/social_index/tiktok_referee/delivered_recount.json', 'w'), indent=1)
