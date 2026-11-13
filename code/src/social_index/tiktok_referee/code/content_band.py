"""Referee: what the wide content set adds, quarter by quarter (decision date), and how the videos-removed outcome moves
if the wide set is video+image only, or video only."""
import duckdb, glob, json, datetime as D
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/raw/dsa_tiktok/'
con = duckdb.connect()
fs = sorted(glob.glob(P + 'complete_*.parquet'))
con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
S = json.load(open('/Users/heuremen/bones-forge/social_index/tiktok_referee/stated_recount.json'))
NORM = "(ct_account or ct_link or ct_sticker or ct_hashtag or ct_product or ct_app or ct_text or ct_audio)"
def qb(q):
    y, n = int(q[:4]), int(q[5]); a = D.date(y, 3*n-2, 1); b = D.date(y + (n == 4), (3*n) % 12 + 1, 1) - D.timedelta(days=1); return a, b
def cnt(where):
    return con.execute("select coalesce(sum(n),0) from c where " + where).fetchone()[0]
print('quarter    video      +image_only  +other_only(unnorm) synthetic  | upper    | video+image | gap ranges (S range vs D range) for: video-only / video+image / plan upper')
for q in ['2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2']:
    a, b = qb(q); d1 = D.timedelta(days=1)
    wins = ["application_day between DATE '%s' and DATE '%s'" % (a + k*d1, b + k*d1) for k in (-1, 0, 1)]
    w0 = wins[1]
    base = "dv_removed and not ct_ad and " + w0
    v = cnt(base + " and ct_video")
    img = cnt(base + " and ct_image and not ct_video")
    oth = cnt(base + " and ct_other and not ct_video and not ct_image and not ct_synthetic_media and not " + NORM)
    syn = cnt(base + " and ct_synthetic_media and not ct_video and not ct_image")
    up = v + img + oth + syn
    s = S[q]['stated']['videos_removed']
    lower = min(cnt("dv_removed and not ct_ad and ct_video and decision_ground='DECISION_GROUND_INCOMPATIBLE_CONTENT' and " + w) for w in wins)
    hi_v = max(cnt("dv_removed and not ct_ad and ct_video and " + w) for w in wins)
    hi_vi = max(cnt("dv_removed and not ct_ad and (ct_video or ct_image) and " + w) for w in wins)
    hi_up = max(cnt("dv_removed and not ct_ad and (ct_video or ct_image or ct_synthetic_media or (ct_other and not %s)) and %s" % (NORM, w)) for w in wins)
    def g(hi):
        lo_g, hi_g = (lower - s['hi']) / s['point'], (hi - s['lo']) / s['point']
        m = 0.05
        oc = 'ABOVE' if lo_g > 0 else ('BELOW' if hi_g < 0 else ('CONSISTENT' if lo_g >= -m and hi_g <= m else 'CANNOT_TELL'))
        return '[%+.1f%%, %+.1f%%] %s' % (100*lo_g, 100*hi_g, oc)
    print('%s %10d %10d %10d %10d | %10d | %10d | %s / %s / %s' % (q, v, img, oth, syn, up, v + img, g(hi_v), g(hi_vi), g(hi_up)))
