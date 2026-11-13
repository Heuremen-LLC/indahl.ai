"""Referee TCCP + G.19 recount."""
import sys, os, json, glob, re, statistics, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref_xlsx
import numpy as np

TDIR, G19, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

def num(s):
    try:
        return float(s)
    except Exception:
        return None

def pct(v):  # stored as fraction; 9.99 = 999% = not applicable
    if v is None:
        return None
    if abs(v - 9.99) < 1e-9:
        return 'NA'
    return v * 100 if v <= 1.0 else ('ODD', v)

def q(xs, p):
    return float(np.percentile(xs, p)) if xs else None

res = []
for p in sorted(glob.glob(os.path.join(TDIR, '*.xlsx'))):
    _, rows = ref_xlsx.read(p)
    h = rows[9]
    data = [r + [''] * (len(h) - len(r)) for r in rows[10:] if len(r) > 1 and r[1].strip()]
    def col(names):
        for n in names:
            if n in h:
                return h.index(n)  # first occurrence = purchase APR block in 2022 H2
        return None
    imin, imed, imax = col(['Purchase APR min', 'Minimum APR']), col(['Purchase APR median', 'Median APR']), col(['Purchase APR max', 'Maximum APR'])
    itop = col(['Issued by Top 25 Institution'])
    ioff = col(['Purchase APR Offered?'])
    ivary = col(['Purchase APR Vary by Credit Tier'])
    ilate = col(['Late Fee ($)', 'Amount (Dollars) - Late Payment Fee'])
    iann = col(['Annual Fee'])
    iannq = [i for i, c in enumerate(h) if 'nnual' in c and 'Fee' in c]
    rd = data[0][col(['Report Date'])]
    meds, meds_top, mins, maxs = [], [], [], []
    na_med = odd = 0
    have_min = have_med = have_any = 0
    med_blank_vary = {}
    topvals = {}
    for r in data:
        a, m, b = pct(num(r[imin])), pct(num(r[imed])), pct(num(r[imax]))
        if itop is not None:
            topvals[r[itop]] = topvals.get(r[itop], 0) + 1
        if any(isinstance(x, float) for x in (a, m, b)):
            have_any += 1
        if isinstance(a, float): mins.append(a); have_min += 1
        if isinstance(b, float): maxs.append(b)
        if m == 'NA': na_med += 1
        if isinstance(m, float):
            have_med += 1; meds.append(m)
            if itop is not None and r[itop] in ('TRUE', '1'):
                meds_top.append(m)
        else:
            k = (r[ivary] if ivary is not None else '?', 'minmax_equal' if isinstance(a, float) and isinstance(b, float) and abs(a - b) < 1e-9 else 'minmax_differ_or_blank')
            med_blank_vary[str(k)] = med_blank_vary.get(str(k), 0) + 1
        for x in (a, m, b):
            if isinstance(x, tuple): odd += 1
    # alternative: median APR per plan, falling back to (min+max)/2 or min==max when median blank
    alt = []
    for r in data:
        a, m, b = pct(num(r[imin])), pct(num(r[imed])), pct(num(r[imax]))
        if isinstance(m, float): alt.append(m)
        elif isinstance(a, float) and isinstance(b, float) and abs(a - b) < 1e-9: alt.append(a)
    lates = [num(r[ilate]) for r in data if ilate is not None and num(r[ilate]) is not None]
    anns = [num(r[iann]) for r in data if num(r[iann]) is not None]
    res.append(dict(file=os.path.basename(p), report_date=rd, header_cols=dict(min=h[imin], med=h[imed], max=h[imax], min_idx=imin), plans=len(data),
                    offered_yes=sum(1 for r in data if r[ioff] == 'Yes'), plans_with_min=have_min, plans_with_median=have_med, median_na_999=na_med, odd_values=odd,
                    median_of_medians=q(meds, 50), p10=q(meds, 10), p90=q(meds, 90), top25_plans=len(meds_top) if itop is not None else None,
                    top25_median=q(meds_top, 50), top25_p10=q(meds_top, 10), top25_p90=q(meds_top, 90), top_flag_values=topvals,
                    lowest_min=min(mins) if mins else None, highest_max=max(maxs) if maxs else None,
                    median_blank_by_vary_and_minmax=med_blank_vary,
                    alt_median_with_flat_plans=q(alt, 50), alt_n=len(alt),
                    late_fee_col=h[ilate] if ilate is not None else None, late_fee_median=q(lates, 50), late_fee_plans=len(lates),
                    annual_fee_plans=len(anns), annual_fee_zero=sum(1 for x in anns if x == 0), annual_fee_cols=[h[i] for i in iannq]))

# G.19 history table
t = open(G19, encoding='utf-8', errors='replace').read()
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S)
g = []
for r in rows:
    cells = [re.sub(r'<[^>]+>', ' ', c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.S)]
    cells = [html.unescape(re.sub(r'\s+', ' ', c)).strip() for c in cells]
    if cells:
        g.append(cells)
json.dump(dict(tccp=res, g19_rows_head=g[:8], g19_rows_tail=g[-14:], g19_n=len(g)), open(OUT, 'w'), indent=1)
for x in res:
    print(json.dumps(x))
for r in g[:8]: print(r)
for r in g[-14:]: print(r)
