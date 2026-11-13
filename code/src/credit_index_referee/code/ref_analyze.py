"""Referee aggregation, block bootstrap (company-month blocks) and classification. Seed 987654."""
import pickle, json, sys
from collections import defaultdict
import numpy as np

AGG, OUT = sys.argv[1], sys.argv[2]
P = pickle.load(open(AGG, 'rb'))
agg, RESP = P['agg'], P['RESP']
NV = 12 + len(RESP) + 1
BUREAUS = ["EQUIFAX, INC.", "Experian Information Solutions Inc.", "TRANSUNION INTERMEDIATE HOLDINGS, INC."]
YEARS = [2021, 2022, 2023, 2024, 2025]
SEED, B = 987654, 2000
rng = np.random.default_rng(SEED)

# timely bands (timely share) from the plan
TB = {2021: (0.985, 0.995), 2022: (0.985, 0.995), 2023: (0.9955, 0.9965), 2024: (0.9965, 0.9975), 2025: (0.9955, 0.9965)}
NTB = {y: (round(1 - b[1], 6), round(1 - b[0], 6)) for y, b in TB.items()}  # not timely band (lo, hi]

def boot(nums, dens):
    nums = np.asarray(nums, float); dens = np.asarray(dens, float)
    n = len(nums)
    if n == 0 or dens.sum() == 0:
        return None, None, None
    pt = nums.sum() / dens.sum()
    stats = []
    chunk = max(1, min(B, 4_000_000 // n))
    done = 0
    while done < B:
        k = min(chunk, B - done)
        idx = rng.integers(0, n, size=(k, n))
        s_n = nums[idx].sum(1); s_d = dens[idx].sum(1)
        stats.append(np.where(s_d > 0, s_n / np.maximum(s_d, 1), np.nan))
        done += k
    st = np.concatenate(stats)
    st = st[~np.isnan(st)]
    return pt, float(np.percentile(st, 2.5)), float(np.percentile(st, 97.5))

def classify(lo, hi, band):
    a, b = band
    if lo is None:
        return 'CANNOT_TELL'
    if lo >= b:
        return 'ABOVE'
    if hi < a:
        return 'BELOW'
    if lo >= a and hi < b:
        return 'CONSISTENT'
    return 'CANNOT_TELL'

def classify_nt(lo, hi, band):  # band (a, b] for not timely share
    a, b = band
    if lo > b:
        return 'ABOVE'
    if hi <= a:
        return 'BELOW'
    if lo > a and hi <= b:
        return 'CONSISTENT'
    return 'CANNOT_TELL'

# company-month blocks
cm = defaultdict(lambda: np.zeros(NV, np.int64))           # (comp, y, m)
cfm = defaultdict(lambda: np.zeros(NV, np.int64))          # (comp, fam, y, m)
for (comp, fam, y, m), v in agg.items():
    cm[(comp, y, m)] += v
    cfm[(comp, fam, y, m)] += v

R = {}
# ---- ruler one
r1 = []
for y in YEARS:
    blocks = [v for (c, yy, m), v in cm.items() if yy == y]
    yes = np.array([b[1] for b in blocks]); no = np.array([b[2] for b in blocks])
    pt, lo, hi = boot(yes, yes + no)
    r1.append(dict(year=y, rows=int(sum(b[0] for b in blocks)), yes=int(yes.sum()), not_timely=int(no.sum()),
                   timely_other=int(sum(b[3] for b in blocks)), company_months=len(blocks),
                   timely=pt, lo=lo, hi=hi, band=TB[y], outcome=classify(lo, hi, TB[y]),
                   more_than_99=classify(lo, hi, (0.99, 1.0000001)) if y == 2025 else None))
R['ruler1'] = r1

# ---- ruler two, companies per year
comps = []
tally = {}
for y in YEARS:
    byc = defaultdict(list)
    for (c, yy, m), v in cm.items():
        if yy == y:
            byc[c].append(v)
    t = defaultdict(int)
    for c, bl in byc.items():
        rows = int(sum(b[0] for b in bl)); months = sum(1 for b in bl if b[0] > 0)
        if rows < 1000 or months < 10:
            t['too_few'] += 1
            continue
        no = np.array([b[2] for b in bl]); yes = np.array([b[1] for b in bl])
        pt, lo, hi = boot(no, yes + no)
        o = classify_nt(lo, hi, NTB[y])
        t[o] += 1
        comps.append(dict(company=c, year=y, rows=rows, not_timely=int(no.sum()), months=months, share=pt, lo=lo, hi=hi, outcome=o))
    tally[y] = dict(t)
R['companies'] = comps; R['tally'] = tally

# ---- company x family 2025
cf = defaultdict(list)
for (c, f, y, m), v in cfm.items():
    if y == 2025:
        cf[(c, f)].append(v)
cfo = []; t = defaultdict(int)
for (c, f), bl in cf.items():
    rows = int(sum(b[0] for b in bl)); months = sum(1 for b in bl if b[0] > 0)
    if rows < 1000 or months < 10:
        t['too_few'] += 1; continue
    no = np.array([b[2] for b in bl]); yes = np.array([b[1] for b in bl])
    pt, lo, hi = boot(no, yes + no)
    o = classify_nt(lo, hi, NTB[2025]); t[o] += 1
    cfo.append(dict(company=c, family=f, rows=rows, not_timely=int(no.sum()), months=months, share=pt, lo=lo, hi=hi, outcome=o))
R['comp_fam'] = cfo; R['tally_cf'] = dict(t)

# ---- bureau window
bw = []
for bco in BUREAUS:
    bl = [v for (c, y, m), v in cm.items() if c == bco]
    ry = {y: sum(int(v[0]) for (c, yy, m), v in cm.items() if c == bco and yy == y) for y in YEARS}
    W = sum(ry.values())
    band = (sum(ry[y] * NTB[y][0] for y in YEARS) / W, sum(ry[y] * NTB[y][1] for y in YEARS) / W)
    no = np.array([b[2] for b in bl]); yes = np.array([b[1] for b in bl])
    pt, lo, hi = boot(no, yes + no)
    bw.append(dict(company=bco, rows=int(sum(b[0] for b in bl)), not_timely=int(no.sum()), months=len(bl), share=pt, lo=lo, hi=hi, band=band, outcome=classify_nt(lo, hi, band)))
R['bureau_window'] = bw

# ---- others not timely, responses
def group_blocks(pred, y):
    return [v for (c, yy, m), v in cm.items() if pred(c) and (y == 'window' or yy == y)]
groups = [('three bureaus', lambda c: c in BUREAUS)] + [(b, (lambda bb: (lambda c: c == bb))(b)) for b in BUREAUS] + [('all others', lambda c: c not in BUREAUS)]
on = []; resp = []
for y in YEARS + ['window']:
    bl = group_blocks(lambda c: c not in BUREAUS, y)
    no = np.array([b[2] for b in bl]); yes = np.array([b[1] for b in bl])
    pt, lo, hi = boot(no, yes + no)
    on.append(dict(year=y, rows=int(sum(b[0] for b in bl)), not_timely=int(no.sum()), share=pt, lo=lo, hi=hi))
    cells = []
    for g, pred in groups:
        bl = group_blocks(pred, y)
        den = np.array([b[0] for b in bl])
        sh = []
        for i, cat in enumerate(RESP + ['(other)']):
            num = np.array([b[12 + i] for b in bl])
            if num.sum() == 0:
                sh.append(dict(category=cat or '(blank)', rows=0, share=0.0, lo=0.0, hi=0.0)); continue
            pt, lo, hi = boot(num, den)
            sh.append(dict(category=cat or '(blank)', rows=int(num.sum()), share=pt, lo=lo, hi=hi))
        cells.append(dict(group=g, rows=int(den.sum()), company_months=len(bl), shares=sh))
    resp.append(dict(year=y, cells=cells))
R['others_nt'] = on; R['responses'] = resp

# ---- q1c lag buckets and bureau credit reporting not timely
lag = []; bcr = []
for bco in BUREAUS:
    for y in YEARS:
        bl = [v for (c, f, yy, m), v in cfm.items() if c == bco and f == 'credit reporting' and yy == y]
        s = sum(bl) if bl else np.zeros(NV, np.int64)
        lag.append(dict(company=bco, year=y, buckets={'0 or 1': int(s[8]), '2 to 7': int(s[9]), '8 to 30': int(s[10]), 'over 30': int(s[11])}, negative=int(s[6]), no_sent=int(s[7])))
        no = np.array([b[2] for b in bl]); yes = np.array([b[1] for b in bl])
        pt, lo, hi = boot(no, yes + no)
        bcr.append(dict(company=bco, year=y, rows=int(s[0]), not_timely=int(s[2]), share=pt, lo=lo, hi=hi))
R['lag'] = lag; R['bcr'] = bcr

# ---- q1d
q1d = []
for y in YEARS:
    bl = [v for (c, yy, m), v in cm.items() if yy == y]
    num = np.array([b[4] for b in bl]); den = np.array([b[5] for b in bl])
    pt, lo, hi = boot(num, den)
    q1d.append(dict(year=y, rows=int(sum(b[0] for b in bl)), valid=int(den.sum()), within_1_day=int(num.sum()),
                    sent_before_received=int(sum(b[6] for b in bl)), no_sent=int(sum(b[7] for b in bl)),
                    share=pt, lo=lo, hi=hi, outcome=classify(lo, hi, (0.965, 0.975)) if y == 2025 else None))
R['q1d'] = q1d
R['stats'] = P['stats']; R['year_all'] = P['year_all']

json.dump(R, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else list(o))
print('ok')
