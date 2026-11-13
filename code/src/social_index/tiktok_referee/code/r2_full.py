"""Referee pass 2: every EU row, committed (Addendum 2 windows, day-check gate) and post hoc (Addendum 3.2), from own code.
Stated side from stated_recount.json (stated.py, own reader of the release zips). Delivered from the grouped month files,
which reproduce the Commission files exactly on 10 independently read months (extract_check.py). Writes eu_rows_recount.json."""
import re, glob, duckdb, datetime as D, json
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/'
R = '/Users/heuremen/bones-forge/social_index/tiktok_referee/'
S = json.load(open(R + 'stated_recount.json'))
pub = {}
for f in glob.glob(P + 'raw/dsa_pages/tiktok_p30_page*.html'):
    for d, n in re.findall(r'header="Date">(\d{4}-\d\d-\d\d)</td>\s*<td[^>]*header="Statements of reasons">([^<]+)</td>', open(f).read()):
        pub[d] = int(re.sub(r'[^\d]', '', n.replace('&nbsp;', '')) or 0)
con = duckdb.connect()
fs = sorted(glob.glob(P + 'raw/dsa_tiktok/complete_*.parquet'))
con.execute("create view c as select * from read_parquet([%s], union_by_name=true)" % ','.join("'%s'" % f for f in fs))
agg = {str(d): int(n) for d, n in con.execute("select created_day, sum(n) from c group by 1").fetchall()}
LAST = max(agg)
SETS = {'lower': "dv_removed and ct_video and not ct_ad and decision_ground = 'DECISION_GROUND_INCOMPATIBLE_CONTENT'",
        'point': "dv_removed and ct_video and not ct_ad",
        'upper': "dv_removed and not ct_ad and (ct_video or ct_image or ct_synthetic_media or (ct_other and not (ct_account or ct_link or ct_sticker or ct_hashtag or ct_product or ct_app or ct_text or ct_audio)))"}
K = "coalesce(sum(n),0), coalesce(sum(n) filter (where automated_decision='AUTOMATED_DECISION_FULLY'),0), coalesce(sum(n) filter (where source_type='SOURCE_VOLUNTARY'),0), coalesce(sum(n) filter (where dd=0),0), coalesce(sum(n) filter (where dd between 0 and 1),0)"
KEYS = ('n', 'auto', 'vol', 'd0', 'd01')
FAILED = ['2026-02-11', '2026-09-30', '2026-10-01', '2026-10-02']
def qb(q):
    y, n = int(q[:4]), int(q[5]); a = D.date(y, 3*n-2, 1); b = D.date(y + (n == 4), (3*n) % 12 + 1, 1) - D.timedelta(days=1); return a, b
def addm(d, m):
    y, mo = d.year + (d.month - 1 + m) // 12, (d.month - 1 + m) % 12 + 1
    return D.date(y, mo, 1)
def outcome(slo, shi, spt, dlo, dhi, share):
    glo, ghi = dlo - shi, dhi - slo
    m = 0.01 if share else 0.05 * spt
    if glo > 0: return 'ABOVE', glo, ghi, ('yes' if glo > m else ('no' if ghi <= m else 'cannot tell'))
    if ghi < 0: return 'BELOW', glo, ghi, ('yes' if ghi < -m else ('no' if glo >= -m else 'cannot tell'))
    if glo >= -m and ghi <= m: return 'CONSISTENT', glo, ghi, 'no'
    return 'CANNOT_TELL', glo, ghi, None
out = {}
for q in ['2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2']:
    a, b = qb(q); wend = addm(b, 4) - D.timedelta(days=1)  # three months after the quarter's last day
    days = [d for d in sorted(set(agg) | set(pub)) if a.isoformat() <= d <= wend.isoformat()]
    exc = {d: agg[d] - pub[d] for d in days if d in agg and d in pub and agg[d] > pub[d]}
    sh = sum(pub[d] - agg.get(d, 0) for d in days if d in pub and pub[d] > agg.get(d, 0) and d <= LAST)
    unv = [d for d in days if d in agg and d not in pub]
    gate_fail = [d for d in FAILED if a.isoformat() <= d <= wend.isoformat()]
    cells = []
    allow = {}
    for k in (-1, 0, 1):
        w = "application_day between DATE '%s' and DATE '%s'" % (a + D.timedelta(days=k), b + D.timedelta(days=k))
        for sn, sw in SETS.items():
            base = dict(zip(KEYS, map(int, con.execute("select %s from c where (%s) and (%s)" % (K, sw, w)).fetchone())))
            rem = dict((x, 0) for x in KEYS); remnon = dict((x, 0) for x in KEYS)
            for d in list(exc) + unv:
                r = dict(zip(KEYS, map(int, con.execute("select %s from c where (%s) and (%s) and created_day = DATE '%s'" % (K, sw, w, d)).fetchone())))
                cap = r['n'] if d in unv else min(exc[d], r['n'])
                for x in KEYS:
                    rem[x] += min(cap, r[x]); remnon[x] += min(cap, r['n'] - r[x])
            rem['n'] = sum(min(r_, 0) for r_ in []) or rem['n']
            cells.append(dict(set=sn, k=k, base=base, rem=rem, remnon=remnon))
    for key in ('n', 'auto'):
        vals = [con.execute("select %s from c where (%s) and application_day between DATE '%s' and DATE '%s' and created_day = DATE '%s'" % (K, SETS['upper'], a - D.timedelta(days=1), b + D.timedelta(days=1), d)).fetchone()[KEYS.index(key)] for d in ('2026-10-31', '2026-11-03')]
        allow[key] = 2 * int(max(vals))
    pt = [c_ for c_ in cells if c_['set'] == 'point' and c_['k'] == 0][0]['base']
    st = S[q]['stated']
    rows = {}
    def cnt(key, ph):
        lo = min(c_['base'][key] - (c_['rem'][key] if ph else 0) for c_ in cells if c_['set'] == 'lower')
        hi = max(c_['base'][key] for c_ in cells if c_['set'] == 'upper') + allow[key] + (sh if ph else 0)
        return lo, hi
    def shr(klo, khi, ph):
        lo = min((c_['base'][klo] - (c_['rem'][klo] if ph else 0)) / (c_['base']['n'] - (c_['rem'][klo] if ph else 0) + (sh if ph else 0)) for c_ in cells if c_['base']['n'])
        hi = max((c_['base'][khi] + (sh if ph else 0)) / (c_['base']['n'] - (c_['remnon'][khi] if ph else 0) + (sh if ph else 0)) for c_ in cells if c_['base']['n'])
        return lo, hi
    for ms, f in (('videos_removed', lambda ph: cnt('n', ph)), ('automated_removals', lambda ph: cnt('auto', ph)),
                  ('automated_share', lambda ph: shr('auto', 'auto', ph)), ('proactive_rate', lambda ph: shr('vol', 'vol', ph)),
                  ('within_24h_rate', lambda ph: shr('d0', 'd01', ph))):
        share = ms in ('automated_share', 'proactive_rate', 'within_24h_rate')
        dpt = {'videos_removed': pt['n'], 'automated_removals': pt['auto'], 'automated_share': pt['auto'] / pt['n'], 'proactive_rate': pt['vol'] / pt['n'], 'within_24h_rate': None}[ms]
        s = st[ms]
        r = {}
        for ph in (False, True):
            dlo, dhi = f(ph)
            oc, glo, ghi, mat = outcome(s['lo'], s['hi'], s['point'], dlo, dhi, share)
            r['posthoc' if ph else 'rule'] = dict(D=[dlo, dhi], gap=[glo, ghi], outcome=oc, material=mat)
        committed = r['rule']['outcome']
        if q == '2023Q3': committed = 'CANNOT_TELL'
        if gate_fail: committed = 'CANNOT_TELL'
        ph_out = r['posthoc']['outcome'] if q != '2023Q3' else 'CANNOT_TELL'
        rows[ms] = dict(S=[s['point'], s['lo'], s['hi']], Dpoint=dpt, committed=committed, gate_fail=gate_fail, posthoc_outcome=ph_out, **r)
    out[q] = dict(rows=rows, excess=exc, shortfall=sh, unverified=unv, allow=allow)
    print(q, 'gate_fail', gate_fail, 'shortfall', sh, 'unverified', unv, 'excess days', len(exc), 'allow', allow)
    for ms, v in rows.items():
        print('   %-18s committed=%-11s posthoc=%-11s rule_gap=[%.4g, %.4g] posthoc_gap=[%.4g, %.4g] mat=%s' % (ms, v['committed'], v['posthoc_outcome'], *v['rule']['gap'], *v['posthoc']['gap'], v['posthoc']['material']))
json.dump(out, open(R + 'eu_rows_recount.json', 'w'), indent=1)
