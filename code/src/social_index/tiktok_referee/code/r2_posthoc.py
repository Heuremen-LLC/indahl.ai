"""Referee pass 2: independent check of Addendum 3.2 (post hoc day reading) for 2025Q4-2026Q2.
Parses TikTok's published daily totals from the saved download pages, compares with the complete aggregate per created day,
and widens the delivered range per the addendum text. Own code."""
import re, glob, duckdb, datetime as D, json
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/'
pub = {}
for f in glob.glob(P + 'raw/dsa_pages/tiktok_p30_page*.html'):
    s = open(f).read()
    for d, n in re.findall(r'header="Date">(\d{4}-\d\d-\d\d)</td>\s*<td[^>]*header="Statements of reasons">([\d&nbsp;\s]+)</td>', s):
        pub[d] = int(re.sub(r'[^\d]', '', n.replace('&nbsp;', '')))
print('published days', len(pub), min(pub), max(pub))
con = duckdb.connect()
fs = sorted(glob.glob(P + 'raw/dsa_tiktok/complete_*.parquet'))
con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
agg = {str(d): int(n) for d, n in con.execute("select created_day, sum(n) from c group by 1").fetchall()}
alld = sorted(set(agg) | set(pub))
eq = sum(1 for d in alld if d in agg and d in pub and agg[d] == pub[d])
both = sum(1 for d in alld if d in agg and d in pub)
print('days in both', both, 'equal', eq, 'agg only', [d for d in alld if d in agg and d not in pub][:10], 'pub only', [d for d in alld if d in pub and d not in agg][:10])
diff = sorted(((d, agg[d], pub[d]) for d in alld if d in agg and d in pub and agg[d] != pub[d]), key=lambda x: -abs(x[1]-x[2]))
print('largest diffs', diff[:6])
PT = "dv_removed and ct_video and not ct_ad"
UP = "dv_removed and not ct_ad and (ct_video or ct_image or ct_synthetic_media or (ct_other and not (ct_account or ct_link or ct_sticker or ct_hashtag or ct_product or ct_app or ct_text or ct_audio)))"
LO = PT + " and decision_ground = 'DECISION_GROUND_INCOMPATIBLE_CONTENT'"
def qb(q):
    y, n = int(q[:4]), int(q[5]); a = D.date(y, 3*n-2, 1); b = D.date(y + (n == 4), (3*n) % 12 + 1, 1) - D.timedelta(days=1); return a, b
out = {}
for q in ('2025Q4', '2026Q1', '2026Q2'):
    a, b = qb(q); end = b + D.timedelta(days=92)
    days = [d for d in alld if a.isoformat() <= d <= end.isoformat()]
    exc = {d: agg[d] - pub[d] for d in days if d in agg and d in pub and agg[d] > pub[d]}
    sh = {d: pub[d] - agg.get(d, 0) for d in days if d in pub and pub[d] > agg.get(d, 0)}
    unv = [d for d in days if d in agg and d not in pub]
    res = {}
    for k in (-1, 0, 1):
        w = "application_day between DATE '%s' and DATE '%s'" % (a + D.timedelta(days=k), b + D.timedelta(days=k))
        for sn, sw in (('lower', LO), ('point', PT), ('upper', UP)):
            base = con.execute("select coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0), coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0) from c where (%s) and (%s)" % (sw, w)).fetchone()
            # removable mass per excess/unverified day, split by flag
            rem = {'n': 0, 'auto': 0, 'nonauto': 0, 'vol': 0, 'nonvol': 0}
            for d in list(exc) + unv:
                r = con.execute("select coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0), coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0) from c where (%s) and (%s) and created_day = DATE '%s'" % (sw, w, d)).fetchone()
                cap = r[0] if d in unv else min(exc[d], r[0])
                rem['n'] += cap
                rem['auto'] += min(cap, r[1]); rem['nonauto'] += min(cap, r[0] - r[1])
                rem['vol'] += min(cap, r[2]); rem['nonvol'] += min(cap, r[0] - r[2])
            res['%s|%d' % (sn, k)] = dict(n=int(base[0]), auto=int(base[1]), vol=int(base[2]), rem=rem)
    S = sum(sh.values())
    o = {}
    o['videos_lo'] = min(v['n'] - v['rem']['n'] for kk, v in res.items() if kk.startswith('lower'))
    o['videos_hi_add'] = S
    for nm, f in (('auto', 'auto'), ('vol', 'vol')):
        lo = min((v[f] - v['rem'][f]) / (v['n'] - v['rem'][f] + S) for v in res.values())
        hi = max((v[f] + S) / (v['n'] - v['rem']['non' + f] + S) for v in res.values())
        lo_cap = min((v[f] - v['rem'][f]) / (v['n'] - v['rem'][f]) for v in res.values())
        o[nm + '_share'] = [lo, hi]
    o['excess_days'] = exc; o['shortfall'] = sh; o['unverified'] = unv
    out[q] = o
    print(q, 'videos D_lo after excess', o['videos_lo'], 'shortfall added', S, 'auto share', ['%.4f' % x for x in o['auto_share']], 'vol share', ['%.4f' % x for x in o['vol_share']], 'unverified', unv)
json.dump(out, open('/Users/heuremen/bones-forge/social_index/tiktok_referee/posthoc_recount.json', 'w'), indent=1, default=str)
