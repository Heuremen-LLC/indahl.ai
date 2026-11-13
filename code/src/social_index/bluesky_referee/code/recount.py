"""Referee recount of the Bluesky label rows from the stored stream (data/labels.sqlite), read-only.
Written for the referee pass. Does not import bsky_tick.py or heuremen_kit.py. Rules from PLAN.md (and Addendum 1) as read by the referee.

Usage: python3 -I recount.py DBPATH OUTJSON [--immutable]
"""
import sqlite3, sys, json, time, calendar
import numpy as np

DB, OUT = sys.argv[1], sys.argv[2]
URI = 'file:%s?%s' % (DB, 'immutable=1' if '--immutable' in sys.argv else 'mode=ro')
LAB = 'did:plc:ar7c4by46qjdydhdevvrndac'
HOUR = 3600 * 1000; DAYMS = 24 * HOUR
def utc(y, h=0): return calendar.timegm((y, 1, 1, h, 0, 0)) * 1000
YEARS = list(range(2022, 2030))
BOUND_U = np.array([utc(y) for y in YEARS], dtype=np.int64)
BOUND_P = np.array([utc(y, 8) for y in YEARS], dtype=np.int64)   # 1 Jan 08:00 UTC = 1 Jan 00:00 PST
TD = ('!takedown', '!suspend')
t0 = time.time()
def log(*a): print('[%6.0fs]' % (time.time() - t0), *a, flush=True)

con = sqlite3.connect(URI, uri=True)
V = dict(con.execute('SELECT s, id FROM vals')); VN = {i: s for s, i in V.items()}
labid = con.execute('SELECT id FROM srcs WHERE s = ?', (LAB,)).fetchone()[0]
NV = max(V.values()) + 1

# ---- served rows, recomputed from keys (not from the sup flag): one row per (did, coll, rkey, cidh, val, src), the highest seq
log('finding keys stored more than once')
nonmax = []
for seqs in con.execute('SELECT GROUP_CONCAT(seq) FROM label GROUP BY did, coll, rkey, cidh, val, src HAVING COUNT(*) > 1'):
    s = sorted(int(x) for x in seqs[0].split(',')); nonmax += s[:-1]
nonmax = np.array(sorted(nonmax), dtype=np.int64)
log('rows not served (an older copy of a key read again later):', len(nonmax))

# ---- load columns
log('loading columns')
n = con.execute('SELECT COUNT(*) FROM label').fetchone()[0]
seq = np.empty(n, np.int64); coll = np.empty(n, np.int32); val = np.empty(n, np.int32); neg = np.empty(n, np.int8)
cts = np.empty(n, np.int64); exp = np.empty(n, np.int64); src = np.empty(n, np.int32); sup = np.empty(n, np.int64)
i = 0
cur = con.execute('SELECT seq, coll, val, neg, IFNULL(cts, -9e18), IFNULL(exp, -9e18), src, sup FROM label ORDER BY seq')
while True:
    rows = cur.fetchmany(2_000_000)
    if not rows: break
    a = np.array(rows, dtype=np.int64); k = len(a)
    seq[i:i+k], coll[i:i+k], val[i:i+k], neg[i:i+k], cts[i:i+k], exp[i:i+k], src[i:i+k], sup[i:i+k] = a.T
    i += k
assert i == n
NOCTS = -9 * 10**18
served = ~np.isin(seq, nonmax)
out = dict(db=DB, rows_stored=int(n), head_seq=int(seq.max()), nonmax_rows=int(len(nonmax)),
           served_rows_all_src=int(served.sum()), builder_sup_flagged=int((sup != 0).sum()),
           served_mask_equals_builder_sup0=bool(np.array_equal(served, sup == 0)))
lab = served & (src == labid)
out['served_other_src'] = int((served & (src != labid)).sum())
out['served_lab_no_cts'] = int((lab & (cts <= NOCTS + 1)).sum())
lab &= cts > NOCTS + 1
out['served_lab_with_cts'] = int(lab.sum())
kind = np.where(coll == 0, 0, np.where(coll > 0, 1, 2)).astype(np.int8)   # 0 account (did:), 1 content (at://), 2 other
out['served_lab_other_uri_form'] = int((lab & (kind == 2)).sum())

yU = np.array(YEARS)[np.clip(np.searchsorted(BOUND_U, cts, 'right') - 1, 0, len(YEARS) - 1)]
yP = np.array(YEARS)[np.clip(np.searchsorted(BOUND_P, cts, 'right') - 1, 0, len(YEARS) - 1)]

def cnt(mask, yarr):
    """counts keyed (year, val, neg, kind) -> int, over mask"""
    idx = ((yarr[mask] - 2022).astype(np.int64) * NV + val[mask]) * 6 + neg[mask].astype(np.int64) * 3 + kind[mask]
    b = np.bincount(idx, minlength=len(YEARS) * NV * 6)
    return b.reshape(len(YEARS), NV, 2, 3)
cU = cnt(lab, yU); cP = cnt(lab, yP)

# ---- in-order test (Addendum 1): served labeler rows in seq order, rolling window of 21 centred on the row, truncated at the ends,
# median = element len//2 of the sorted window; in order when |cts - median| <= 24 h
log('in-order test')
L_seq = seq[lab]; L_cts = cts[lab]; m = len(L_cts); half = 10
med = np.empty(m, np.int64)
CH = 2_000_000
from numpy.lib.stride_tricks import sliding_window_view
for st in range(half, m - half, CH):
    en = min(m - half, st + CH)
    w = sliding_window_view(L_cts[st - half:en + half], 21)
    med[st:en] = np.partition(w, 10, axis=1)[:, 10]
for j in list(range(0, min(half, m))) + list(range(max(half, m - half), m)):
    w = np.sort(L_cts[max(0, j - half):min(m, j + half + 1)]); med[j] = w[len(w) // 2]
inorder = np.abs(L_cts - med) <= DAYMS
def S(t):
    c = L_seq[inorder & (L_cts >= t)]
    return int(c.min()) if len(c) else None
ooo = {}
yl = yU[lab]
for y in YEARS:
    k = int(((~inorder) & (yl == y)).sum())
    if k: ooo[str(y)] = k
out['out_of_order_by_year'] = ooo
SB = {y: S(utc(y)) for y in (2024, 2025, 2026)}
out['S'] = {str(y): v for y, v in SB.items()}
served_seq_all = seq[served]
G = {}; RNG = {}; c3 = {}
for Y in (2024, 2025):
    lo, hi = SB[Y], SB[Y + 1]
    if hi is None: hi = int(seq.max()) + 1
    RNG[Y] = (lo, hi)
    inr = (served_seq_all >= lo) & (served_seq_all < hi)
    G[Y] = (hi - lo) - int(inr.sum())
    mk = lab & (seq >= lo) & (seq < hi)
    c3[Y] = cnt(mk, np.full(n, 2022 + Y - 2022, dtype=np.int64))[Y - 2022]   # [val, neg, kind]
out['year_seq_ranges'] = {str(Y): dict(first=RNG[Y][0], next=RNG[Y][1], unserved=G[Y]) for Y in RNG}

# ---- R5: served negations of the labeler dated after Y, credited one application in Y, unless a content record key is a TID dated at or after next year start
log('R5 negations')
TIDC = '234567abcdefghijklmnopqrstuvwxyz'; TIDM = {c: i for i, c in enumerate(TIDC)}
def tid_time(rk):
    if rk is None or len(rk) != 13 or any(ch not in TIDM for ch in rk): return None
    if rk[0] not in '234567abcdefghij': return None            # top bit must be zero
    v = 0
    for ch in rk: v = v * 32 + TIDM[ch]
    return (v >> 10) // 1000                                   # microseconds since epoch -> ms
negrk = {}
for s, rk in con.execute('SELECT seq, rkey FROM label WHERE neg = 1 AND coll > 0'): negrk[s] = rk
c5 = {Y: np.zeros((NV, 3), np.int64) for Y in (2024, 2025)}
tid_refused = {Y: 0 for Y in (2024, 2025)}
nm = lab & (neg == 1)
for s, v, k, t in zip(seq[nm], val[nm], kind[nm], cts[nm]):
    for Y in (2024, 2025):
        if t >= utc(Y + 1):
            if k == 1:
                tt = tid_time(negrk.get(int(s)))
                if tt is not None and tt >= utc(Y + 1): tid_refused[Y] += 1; continue
            c5[Y][v, k] += 1
out['r5_tid_not_credited'] = tid_refused

# ---- R6: R1 rows sharing (uri, val) counted once (cid ignored)
log('R6 distinct subject and value')
con.execute('CREATE TEMP TABLE nm(seq INTEGER PRIMARY KEY)'); con.executemany('INSERT INTO nm VALUES (?)', ((int(x),) for x in nonmax))
yexpr = 'CASE ' + ' '.join('WHEN cts >= %d THEN %d' % (utc(y), y) for y in reversed(YEARS)) + ' ELSE 0 END'
c6 = {Y: np.zeros((NV, 3), np.int64) for Y in (2024, 2025)}
q = '''SELECT y, val, k, COUNT(*) FROM (SELECT DISTINCT did, coll, rkey, val, %s AS y, CASE WHEN coll = 0 THEN 0 WHEN coll > 0 THEN 1 ELSE 2 END AS k
       FROM label WHERE src = ? AND neg = 0 AND cts IS NOT NULL AND seq NOT IN (SELECT seq FROM nm) AND cts >= ? AND cts < ?) GROUP BY 1, 2, 3''' % yexpr
for y, v, k, c in con.execute(q, (labid, utc(2024), utc(2026))):
    c6[y][v, k] += c

# ---- expired labels, 2025, label values
nowms = int(time.time() * 1000)
e25 = lab & (yU == 2025) & ~np.isin(val, [V[x] for x in TD if x in V])
out['exp_2025'] = dict(with_exp=int((e25 & (exp > NOCTS + 1)).sum()), expired=int((e25 & (exp > NOCTS + 1) & (exp < nowms)).sum()))

# ---- daily series (label values only, served labeler rows), for the page's per-day numbers
day = cts[lab] // DAYMS; isTD = np.isin(val[lab], [V[x] for x in TD if x in V]); ng = neg[lab]
d0 = int(day.min()); nd = int(day.max()) - d0 + 1
app = np.bincount(day[(~isTD) & (ng == 0)] - d0, minlength=nd); negd = np.bincount(day[(~isTD) & (ng == 1)] - d0, minlength=nd)
out['series_tail'] = [dict(day=time.strftime('%Y-%m-%d', time.gmtime((d0 + j) * 86400)), applied=int(app[j]), negated=int(negd[j])) for j in range(max(0, nd - 10), nd)]
out['series_first_day'] = time.strftime('%Y-%m-%d', time.gmtime(d0 * 86400))

# ---- values by 2025 R1 (all), for mapping review
out['values_2025_R1'] = {VN[v]: int(cU[2025 - 2022, v, 0].sum()) for v in range(NV) if v in VN and cU[2025 - 2022, v, 0].sum()}
out['values_2024_R1'] = {VN[v]: int(cU[2024 - 2022, v, 0].sum()) for v in range(NV) if v in VN and cU[2024 - 2022, v, 0].sum()}
out['negations_2025'] = {VN[v]: int(cU[2025 - 2022, v, 1].sum()) for v in range(NV) if v in VN and cU[2025 - 2022, v, 1].sum()}

# ---- readings per row
def vset(names):
    if names == 'ALL': return [i for s, i in V.items() if s not in TD]
    return [V[x] for x in names if x in V]
def readings(names, Y, kinds=(0, 1, 2)):
    vs = vset(names); yi = Y - 2022
    R = {}
    R['R1'] = {k: int(cU[yi, vs, 0, k].sum()) for k in kinds}
    R['R2'] = {k: int(cP[yi, vs, 0, k].sum()) for k in kinds}
    R['R3'] = {k: int(c3[Y][vs, 0, k].sum()) for k in kinds}
    R['R4'] = {k: R['R1'][k] + int(cU[yi, vs, 1, k].sum()) for k in kinds}
    R['R5'] = {k: R['R1'][k] + int(c5[Y][vs, k].sum()) for k in kinds}
    R['R6'] = {k: int(c6[Y][vs, k].sum()) for k in kinds}
    return R

def classify(lo, hi, slo, shi):
    if lo is None or hi is None: return 'CANNOT_TELL'
    if lo > shi: return 'ABOVE'
    if hi < slo: return 'BELOW'
    if lo >= slo and hi <= shi: return 'CONSISTENT'
    return 'CANNOT_TELL'

M = 1_000_000; K = 1000
SPEC = [  # id, kind, values, year, side/subj, printed, lo, hi
    ('labels_2025', 'count', 'ALL', 2025, None, '16.49M', 16.485 * M, 16.495 * M),
    ('labels_2024', 'count', 'ALL', 2024, None, '5.5M', 5.45 * M, 5.55 * M),
    ('adult_detection', 'count', ['porn', 'adult', 'sexual', 'suggestive'], 2025, None, '14.2M', 14.15 * M, 14.25 * M),
    ('val_adult', 'count', ['porn', 'adult'], 2025, None, '10.79M', 10.785 * M, 10.795 * M),
    ('val_suggestive', 'count', ['sexual', 'suggestive'], 2025, None, '3.42M', 3.415 * M, 3.425 * M),
    ('val_spam', 'count', ['spam'], 2025, None, '761.77K', 761765, 761775),
    ('val_nudity', 'count', ['nudity'], 2025, None, '389.44K', 389435, 389445),
    ('val_needs_review', 'count', ['needs-review'], 2025, None, '370.14K', 370135, 370145),
    ('val_rude', 'count', ['rude'], 2025, None, '295.38K', 295375, 295385),
    ('val_sexual_figurative', 'count', ['sexual-figurative'], 2025, None, '152.58K', 152575, 152585),
    ('val_graphic_media', 'count', ['graphic-media'], 2025, None, '127.46K', 127455, 127465),
    ('val_hide', 'count', ['!hide'], 2025, None, '68.26K', 68255, 68265),
    ('val_intolerant', 'count', ['intolerant'], 2025, None, '60.20K', 60195, 60205),
    ('val_self_harm', 'count', ['self-harm'], 2025, None, '20.92K', 20915, 20925),
    ('val_threat', 'count', ['threat'], 2025, None, '15.86K', 15855, 15865),
    ('share_content', 'share', 'ALL', 2025, 1, '96.57%', 0.96565, 0.96575),
    ('share_intolerant', 'share', ['intolerant'], 2025, 1, '98%', 0.975, 0.985),
    ('share_threat', 'share', ['threat'], 2025, 1, '100%', 0.995, 1.0),
    ('share_rude', 'share', ['rude'], 2025, 1, '99%', 0.985, 0.995),
    ('share_needs_review', 'share', ['needs-review'], 2025, 0, '100% (exclusively)', 1.0, 1.0),
    ('takedown_items', 'wide', ['!takedown'], 2025, None, '2,446,334', 2446334, 2446334),
    ('takedown_accounts_2025', 'wide_acct', ['!takedown'], 2025, None, '2.08M', 2.075 * M, 2.085 * M),
    ('takedown_accounts_2024', 'wide_acct', ['!takedown'], 2024, None, '1.02M', 1.015 * M, 1.025 * M),
    ('suspensions_2025', 'wide', ['!suspend'], 2025, None, '13,192', 13192, 13192),
]
rows = []
for rid, kd, names, Y, side, printed, slo, shi in SPEC:
    kinds = (0,) if kd == 'wide_acct' else (0, 1, 2)
    R = readings(names, Y, kinds)
    r = dict(id=rid, stated=printed, stated_range=[slo, shi])
    if kd == 'share':
        sh = {}
        for key, d in R.items():
            den = d[0] + d[1]; sh[key] = d[side] / den if den else None
        a3, cc3 = R['R3'][0], R['R3'][1]; den = a3 + cc3 + G[Y]; mine = (a3, cc3)[side]
        sh['R7_other'] = mine / den if den else None; sh['R7_this'] = (mine + G[Y]) / den if den else None
        vals = [x for x in sh.values() if x is not None]
        lo, hi = (min(vals), max(vals)) if vals else (None, None)
        r.update(readings=sh, counts=R, delivered=sh['R1'], interval=[lo, hi])
        zero = all(sum(R[k].values()) == 0 for k in R)
    else:
        tot = {k: sum(d.values()) for k, d in R.items()}; tot['R7'] = tot['R3'] + G[Y]
        lo, hi = min(tot.values()), max(tot.values())
        r.update(readings=tot, delivered=tot['R1'], interval=[lo, hi], by_kind_R1=R['R1'])
        zero = all(tot[k] == 0 for k in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6'))
    oc = 'NOTHING_RETURNED' if zero else classify(lo, hi, slo, shi)
    if kd.startswith('wide') and oc != 'ABOVE' and not zero: oc = 'CANNOT_TELL'
    r['outcome'] = oc
    r['stated_inside_interval'] = (lo is not None and not (hi < slo or lo > shi))
    rows.append(r)
for rid in ('automated_share', 'reports_2025'): rows.append(dict(id=rid, outcome='CANNOT_TELL', delivered=None))
out['rows'] = rows
out['beside_R1_2025'] = {v: int(cU[3, V[v], 0].sum()) for v in ('gore', 'porn(self)', 'sexual(self)', 'nudity(self)', 'rude:1714644703844', 'adult', 'suggestive') if v in V}
json.dump(out, open(OUT, 'w'), indent=1, default=int)
log('done', OUT)
for r in rows: print(r['id'], r.get('delivered'), r.get('interval'), r['outcome'])
