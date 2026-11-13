#!/usr/bin/env python3
"""credit_tick.py: CREDIT rider (see PLAN.md). Rerunnable. Installs no timer. Reads public sources with no key, one request at a time, paced:
the CFPB Consumer Complaint Database full file, the CFPB search API (gate 2 only), the CFPB Terms of Credit Card Plans survey files and the
Federal Reserve G.19 history table. Sets the CFPB's printed figures beside the database and the stated card APRs beside G.19.
Aggregate company-level data only. The ZIP code, State, Tags, Issue, Sub-issue and Company public response columns are never read into any output.
Writes data/credit.json (company cells), summary_credit.json, data/credit_live.json and data/credit_history.jsonl.
--offline: cached files only. --publish: also put data/credit_live.json in the site KV as credit_live, served at /credit/live.json."""
import os, sys, json, time, csv, io, zipfile, hashlib, subprocess, calendar, zlib, re, urllib.request, urllib.parse, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import numpy as np
import heuremen_kit as K, xlsx_lite as X
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
UA = 'heuremen-credit/0.1 (+https://indahl.ai/credit)'
CCDB_URL = 'https://files.consumerfinance.gov/ccdb/complaints.csv.zip'
API = 'https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?'
G19_URL = 'https://www.federalreserve.gov/releases/g19/HIST/cc_hist_tc_levels.html'
TCCP = [('2022 H2', '2022-12-31', 'cfpb_tccp-data_2022-07-01_2022_12-31.xlsx'), ('2023 H1', '2023-06-30', 'cfpb_tccp-data_2023-01-01_2023-06-30.xlsx'),
        ('2023 H2', '2023-12-31', 'cfpb_tccp-data_2023-07-01_2023_12-31.xlsx'), ('2024 H1', '2024-06-30', 'cfpb_tccp-data_2024-06-30.xlsx'),
        ('2024 H2', '2024-12-31', 'cfpb_tccp-data_2024-12-31_uYJ9Krf.xlsx'), ('2025 H1', '2025-06-30', 'cfpb_tccp-data_2025-06-30.xlsx'),
        ('2025 H2', '2025-12-31', 'cfpb_tccp-data_2025-12-31.xlsx')]
YEARS = (2021, 2022, 2023, 2024, 2025)
# S2, printed timely share per year, read as the band its rounding allows (PLAN.md Rules)
PRINTED = {2021: ('99%', 0.985, 0.995, 752800, 'approximately 752,800'), 2022: ('99%', 0.985, 0.995, 819800, 'approximately 819,800'),
           2023: ('99.6%', 0.9955, 0.9965, 1348200, '1,348,200'), 2024: ('99.7%', 0.9965, 0.9975, 2829400, 'approximately 2,829,400'),
           2025: ('99.6%', 0.9955, 0.9965, 5900000, 'more than 5.9 million')}
SENT_BAND = (0.965, 0.975)   # S3, "97%" in a day or less, 2025
BUREAUS = ('EQUIFAX, INC.', 'Experian Information Solutions Inc.', 'TRANSUNION INTERMEDIATE HOLDINGS, INC.')
FAM = {'Credit reporting': 'credit reporting', 'Credit reporting, credit repair services, or other personal consumer reports': 'credit reporting',
       'Credit reporting or other personal consumer reports': 'credit reporting', 'Debt collection': 'debt collection',
       'Credit card': 'credit card', 'Credit card or prepaid card': 'credit card', 'Prepaid card': 'credit card',
       'Checking or savings account': 'checking or savings', 'Bank account or service': 'checking or savings', 'Mortgage': 'mortgage',
       'Student loan': 'student loan', 'Vehicle loan or lease': 'vehicle loan', 'Money transfer, virtual currency, or money service': 'money transfer',
       'Money transfers': 'money transfer', 'Virtual currency': 'money transfer', 'Payday loan': 'personal or payday loan',
       'Payday loan, title loan, or personal loan': 'personal or payday loan', 'Payday loan, title loan, personal loan, or advance loan': 'personal or payday loan',
       'Debt or credit management': 'debt or credit management'}
RESP = ['Closed with explanation', 'Closed with non-monetary relief', 'Closed with monetary relief', 'In progress', 'Untimely response', 'Closed', 'Closed with relief', 'Closed without relief', '']
HEADER = ['Date received', 'Product', 'Sub-product', 'Issue', 'Sub-issue', 'Company public response', 'Company', 'State', 'ZIP code', 'Tags', 'Submitted via',
          'Date sent to company', 'Company response to consumer', 'Timely response?', 'Complaint ID']
MIN_ROWS, MIN_MONTHS, NBOOT, SEED = 1000, 10, 2000, 20261110
PACE = 1.5
for d in ('data', 'data/raw', 'data/raw/ccdb', 'data/raw/tccp', 'data/raw/g19', 'data/cache'): os.makedirs(d, exist_ok=True)
NOW = time.time(); STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW))
def log(*a): print('credit:', *a, file=sys.stderr, flush=True)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=1800):
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 404, 422): break
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:140], err))
def fetch_to(path, url, max_age_h=None):
    fresh = os.path.exists(path) and (max_age_h is None or (NOW - os.path.getmtime(path)) / 3600 < max_age_h)
    if fresh or OFF: return os.path.exists(path)
    try:
        b = get(url); open(path + '.part', 'wb').write(b); os.replace(path + '.part', path); return True
    except Exception as e:
        log('fetch FAILED', url[:120], repr(e)[:120]); STALE.append(os.path.basename(path)); return os.path.exists(path)
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

# ---------------- 1. fetch ----------------
ZIP = 'data/raw/ccdb/complaints.csv.zip'
fetch_to(ZIP, CCDB_URL, max_age_h=160)   # the rider runs about weekly
for _, _, f in TCCP: fetch_to('data/raw/tccp/' + f, 'https://files.consumerfinance.gov/f/documents/' + f)
fetch_to('data/raw/g19/cc_hist_tc_levels.html', G19_URL, max_age_h=160)
zsha = sha256(ZIP); zinfo = zipfile.ZipFile(ZIP).infolist()[0]
zfile_time = '%04d-%02d-%02dT%02d:%02d' % zinfo.date_time[:5]

# ---------------- 2. one pass over the complaint file (aggregate, company-month) ----------------
agg_f = 'data/cache/agg_%s.json' % zsha[:16]
if os.path.exists(agg_f):
    AG = json.load(open(agg_f))
else:
    f = io.TextIOWrapper(zipfile.ZipFile(ZIP).open(zinfo.filename), encoding='utf-8', newline='')
    r = csv.reader(f); h = next(r); fmt_ok = h == HEADER; ix = {k: i for i, k in enumerate(h)}
    iD, iP, iC, iS, iR, iT, iI = (ix[k] for k in ('Date received', 'Product', 'Company', 'Date sent to company', 'Company response to consumer', 'Timely response?', 'Complaint ID'))
    T = C.defaultdict(lambda: [0, 0])          # (company, month, family) -> [yes_or_no rows, no rows]
    RS = C.defaultdict(int)                     # (company, month, response) -> rows
    SD = C.defaultdict(lambda: [0, 0, 0])      # (company, month) -> [sent 0 or 1 day, valid pairs, sent before received]
    LAG = C.defaultdict(int)                    # (bureau credit reporting, year, days bucket) -> rows
    cnt = C.Counter(); ids = []; badlen = 0; dpar = {}
    def days(a, b):
        k = (a, b)
        if k not in dpar:
            dpar[k] = (calendar.timegm(time.strptime(b, '%Y-%m-%d')) - calendar.timegm(time.strptime(a, '%Y-%m-%d'))) // 86400
        return dpar[k]
    for row in r:
        if len(row) != len(h): badlen += 1; continue
        d = row[iD]
        if len(d) != 10 or d[4] != '-': cnt['bad_date'] += 1; continue
        y = int(d[:4])
        if y < 2021 or y > 2025: cnt['outside_window'] += 1; continue
        cnt['rows'] += 1; ids.append(int(row[iI]) if row[iI].isdigit() else -1)
        co = row[iC]; m = d[:7]; fam = FAM.get(row[iP], 'other'); tv = row[iT]
        if tv in ('Yes', 'No'):
            x = T[(co, m, fam)]; x[0] += 1; x[1] += tv == 'No'
        else: cnt['timely_other'] += 1
        RS[(co, m, row[iR])] += 1
        s = row[iS]
        if len(s) == 10:
            g = days(d, s); x = SD[(co, m)]
            if g < 0: x[2] += 1
            else:
                x[1] += 1; x[0] += g <= 1
                if co in BUREAUS and fam == 'credit reporting':
                    LAG[(co, y, '0 or 1' if g <= 1 else '2 to 7' if g <= 7 else '8 to 30' if g <= 30 else 'over 30')] += 1
        else: cnt['no_sent_date'] += 1
    a = np.array(ids, dtype=np.int64); u, c = np.unique(a, return_counts=True)
    AG = dict(fmt_ok=fmt_ok, header=h, badlen=badlen, counts=dict(cnt), dup_ids=int((c > 1).sum()), dup_rows=int((c[c > 1] - 1).sum()),
              T=[[k[0], k[1], k[2], v[0], v[1]] for k, v in T.items()], RS=[[k[0], k[1], k[2], v] for k, v in RS.items()],
              SD=[[k[0], k[1], v[0], v[1], v[2]] for k, v in SD.items()], LAG=[[k[0], k[1], k[2], v] for k, v in LAG.items()])
    json.dump(AG, open(agg_f + '.tmp', 'w')); os.replace(agg_f + '.tmp', agg_f)
    for old_f in os.listdir('data/cache'):
        if old_f.startswith('agg_') and old_f != os.path.basename(agg_f): os.remove(os.path.join('data/cache', old_f))   # keep only the aggregate of the current file
log('rows', AG['counts'], 'dup ids', AG['dup_ids'])

# ---------------- 3. block bootstrap (company-month blocks) ----------------
def seed_of(name): return [SEED, zlib.crc32(name.encode())]
def boot(num, den, name):
    """Ratio sum(num)/sum(den) with a 95 percent percentile interval over resampled blocks (multinomial weights, 2,000 resamples)."""
    num = np.asarray(num, float); den = np.asarray(den, float); B = len(num)
    if B == 0 or den.sum() == 0: return None, None, None
    est = num.sum() / den.sum()
    rng = np.random.default_rng(seed_of(name)); out = []; left = NBOOT; step = max(1, min(NBOOT, 4_000_000 // max(B, 1)))
    while left > 0:
        k = min(step, left); w = rng.multinomial(B, np.full(B, 1.0 / B), size=k)
        dd = w @ den; nn = w @ num; ok = dd > 0; out.extend((nn[ok] / dd[ok]).tolist()); left -= k
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(est), float(lo), float(hi)

T = C.defaultdict(lambda: [0, 0]); TF = C.defaultdict(lambda: [0, 0])
for co, m, fam, n, no in AG['T']:
    x = T[(co, m)]; x[0] += n; x[1] += no; x = TF[(co, m, fam)]; x[0] += n; x[1] += no
def blocks(sel):
    """sel(company, month) -> bool; returns arrays (timely yes, rows) per company-month."""
    num, den = [], []
    for (co, m), (n, no) in T.items():
        if sel(co, m): num.append(n - no); den.append(n)
    return num, den
def r4(x): return None if x is None else round(x, 6)

# ---------------- 4. known-good gates ----------------
kg = {}
kg['format'] = bool(AG['fmt_ok']) and AG['badlen'] == 0 and AG['counts'].get('timely_other', 0) == 0
def ours(company=None, year=None, timely=None):
    s = 0
    for co, m, fam, n, no in AG['T']:
        if company and co != company: continue
        if year and not m.startswith(str(year)): continue
        s += no if timely == 'No' else n
    return s
gate_f = 'data/cache/api_gate_%s.json' % zsha[:16]; G2 = json.load(open(gate_f)) if os.path.exists(gate_f) else {}
checks = [('EQUIFAX, INC. 2023 not timely', dict(company='EQUIFAX, INC.', year=2023, timely='No')), ('2024 not timely', dict(year=2024, timely='No')),
          ('Experian Information Solutions Inc. 2025 all rows', dict(company='Experian Information Solutions Inc.', year=2025)), ('2022 all rows', dict(year=2022))]
g2rows = []
for name, q in checks:
    if name not in G2 and not OFF:
        p = dict(date_received_min='%d-01-01' % q['year'], date_received_max='%d-12-31' % q['year'], size=0, no_aggs='true')
        if q.get('company'): p['company'] = q['company']
        if q.get('timely'): p['timely'] = q['timely']
        try: G2[name] = json.loads(get(API + urllib.parse.urlencode(p)))['hits']['total']['value']
        except Exception as e: log('api gate failed', name, repr(e)[:100])
    o = ours(**q); a = G2.get(name)
    g2rows.append(dict(cell=name, ours=o, api=a, ok=a is not None and abs(o - a) <= 0.005 * max(a, 1)))
json.dump(G2, open(gate_f, 'w'))
kg['reader'] = all(x['ok'] for x in g2rows)
def rule_selftest():
    ok = True
    ok &= K.classify(0.997, 0.998, 0.9955, 0.9965) == K.ABOVE and K.classify(0.990, 0.993, 0.9955, 0.9965) == K.BELOW
    ok &= K.classify(0.9957, 0.9963, 0.9955, 0.9965) == K.CONSISTENT and K.classify(0.995, 0.997, 0.9955, 0.9965) == K.CANNOT_TELL
    # planted cells: the interval holds its own estimate every time and the planted share in most draws (a single draw can miss by chance, 10 Nov fix of the test)
    cover = 0
    for s_ in range(40):
        rng = np.random.default_rng(s_); den = rng.integers(50, 500, 120); num = rng.binomial(den, 0.9)
        e, lo, hi = boot(num, den, 'planted %d' % s_); ok &= lo <= e <= hi; cover += lo < 0.9 < hi
    ok &= cover >= 34
    return ok
import contextlib
with contextlib.redirect_stdout(io.StringIO()): _kit = K.selftest()
kg['rule'] = rule_selftest() and _kit
GATE_PRE = all(kg.values())

# ---------------- 5. readings ----------------
# Q1a ruler one: pooled per year against the printed share
ruler1 = []
for y in YEARS:
    num, den = blocks(lambda co, m, y=y: m.startswith(str(y)))
    e, lo, hi = boot(num, den, 'pooled %d' % y); txt, blo, bhi, sent, senttxt = PRINTED[y]
    ruler1.append(dict(year=y, rows=int(sum(den)), not_timely=int(sum(den) - sum(num)), company_months=len(den), timely=r4(e), lo=r4(lo), hi=r4(hi),
                       printed=txt, band=[blo, bhi], printed_sent=senttxt, outcome=K.classify(lo, hi, blo, bhi),
                       at_edge_display=any(abs(v - bd) < 0.0001 for v in (lo, hi) for bd in (blo, bhi)),
                       printed_base_if_unpublished_timely_display=round((sum(num) + max(sent - sum(den), 0)) / max(sent, sum(den)), 6), database_share_of_printed_count=round(sum(den) / sent, 4)))   # referee R7, display only
    if y == 2025: ruler1[-1]['more_than_99'] = dict(band=[0.99, 1.0], outcome_display=K.classify(lo, hi, 0.99, 1.0))
# Q1a ruler two: each company per year, not timely share against the share the printed figure leaves
def nt_band(y): _, blo, bhi, _, _ = PRINTED[y]; return round(1 - bhi, 6), round(1 - blo, 6)
bycoy = C.defaultdict(list)
for (co, m), (n, no) in T.items(): bycoy[(co, int(m[:4]))].append((m, n, no))
companies = []; tally = {y: C.Counter() for y in YEARS}
for (co, y), lst in sorted(bycoy.items()):
    n = sum(x[1] for x in lst)
    if n < MIN_ROWS or len(lst) < MIN_MONTHS:
        tally[y]['too_few'] += 1; continue
    e, lo, hi = boot([x[2] for x in lst], [x[1] for x in lst], 'co %s %d' % (co, y)); bl, bh = nt_band(y)
    o = K.classify(lo, hi, bl, bh); tally[y][o] += 1
    k_ = sum(x[2] for x in lst); wl_, wh_ = K.wilson(k_, n)
    edge = any(v is not None and abs(v - bd) < 0.0001 for v in (lo, hi) for bd in (bl, bh))   # referee R5: within 0.01 points of a band edge, display only
    companies.append(dict(company=co, year=y, rows=n, not_timely=k_, months=len(lst), share=r4(e), lo=r4(lo), hi=r4(hi), band=[bl, bh], outcome=o, bureau=co in BUREAUS,
                          wilson=[r4(wl_), r4(wh_)], wilson_reading_display=K.classify(wl_, wh_, bl, bh), at_edge_display=edge))   # after the data (10 Nov): a zero count gives a block interval of zero width, the Wilson interval is shown beside it, display only
# company x product family, 2025
byf = C.defaultdict(list)
for (co, m, fam), (n, no) in TF.items():
    if m.startswith('2025'): byf[(co, fam)].append((m, n, no))
comp_fam = []; tally_f = C.Counter()
for (co, fam), lst in sorted(byf.items()):
    n = sum(x[1] for x in lst)
    if n < MIN_ROWS or len(lst) < MIN_MONTHS: tally_f['too_few'] += 1; continue
    e, lo, hi = boot([x[2] for x in lst], [x[1] for x in lst], 'cf %s %s' % (co, fam)); bl, bh = nt_band(2025); o = K.classify(lo, hi, bl, bh); tally_f[o] += 1
    comp_fam.append(dict(company=co, family=fam, rows=n, not_timely=sum(x[2] for x in lst), months=len(lst), share=r4(e), lo=r4(lo), hi=r4(hi), outcome=o,
                         at_edge_display=any(v is not None and abs(v - bd) < 0.0001 for v in (lo, hi) for bd in (bl, bh))))
# bureaus over the window, display only, against the rows-weighted printed share
bureau_window = []
for b in BUREAUS:
    lst = [(m, n, no) for (co, m), (n, no) in T.items() if co == b]
    e, lo, hi = boot([x[2] for x in lst], [x[1] for x in lst], 'bw %s' % b)
    w = C.Counter(); [w.update({int(m[:4]): n}) for m, n, no in lst]
    wl = sum(w[y] * nt_band(y)[0] for y in YEARS) / sum(w.values()); wh = sum(w[y] * nt_band(y)[1] for y in YEARS) / sum(w.values())
    bureau_window.append(dict(company=b, rows=sum(x[1] for x in lst), not_timely=sum(x[2] for x in lst), months=len(lst), share=r4(e), lo=r4(lo), hi=r4(hi), band=[round(wl, 6), round(wh, 6)], outcome_display=K.classify(lo, hi, wl, wh)))
# all-others pooled not timely per year (display beside the bureaus)
others_nt = []
for y in YEARS + (None,):
    sel = (lambda co, m, y=y: co not in BUREAUS and (y is None or m.startswith(str(y))))
    num, den = blocks(sel); nt = [d - n for n, d in zip(num, den)]
    e, lo, hi = boot(nt, den, 'others nt %s' % y)
    others_nt.append(dict(year=y or 'window', rows=int(sum(den)), not_timely=int(sum(nt)), share=r4(e), lo=r4(lo), hi=r4(hi)))

# Q1b: response categories, bureaus pooled, each bureau, all others
RS = C.defaultdict(lambda: C.Counter())
for co, m, resp, v in AG['RS']: RS[(co, m)][resp] += v
cats = sorted({resp for co, m, resp, v in AG['RS']}, key=lambda c: RESP.index(c) if c in RESP else 99)
def resp_cell(label, sel):
    keys = [k for k in RS if sel(*k)]; den = [sum(RS[k].values()) for k in keys]; out = dict(group=label, rows=int(sum(den)), company_months=len(keys), shares=[])
    for c in cats:
        num = [RS[k][c] for k in keys]; e, lo, hi = boot(num, den, 'resp %s %s' % (label, c))
        out['shares'].append(dict(category=c or '(blank)', rows=int(sum(num)), share=r4(e), lo=r4(lo), hi=r4(hi)))
    return out
responses = []
for y in YEARS + (None,):
    ys = (lambda m, y=y: y is None or m.startswith(str(y)))
    yl = y or 'window'
    responses.append(dict(year=yl, cells=[resp_cell('three bureaus', lambda co, m, ys=ys: co in BUREAUS and ys(m))] +
                          [resp_cell(b, lambda co, m, b=b, ys=ys: co == b and ys(m)) for b in BUREAUS] +
                          [resp_cell('all others', lambda co, m, ys=ys: co not in BUREAUS and ys(m))]))
TABLE1 = {2024: dict(monetary='<1%', non_monetary='52%', explanation='42%', admin='3%', reviewing='2%', not_timely='<1%', all_monetary='0.8%'),
          2025: dict(monetary='<1%', non_monetary='40%', explanation='51%', admin='10%', reviewing='<1%', not_timely='<1%')}
q1b_table1 = dict(row='Credit or consumer reporting', printed=TABLE1, outcome=K.CANNOT_TELL, why='Table 1 counts complaints closed with an admin response, which the database does not publish, so the bases differ.')

# Q1c: CANNOT_TELL by plan, with the forwarding lag and the CFPB flag beside it
lag = C.defaultdict(C.Counter)
for co, y, bucket, v in AG['LAG']: lag[(co, y)][bucket] += v
q1c = dict(outcome=K.CANNOT_TELL, why='The database records the date the CFPB received the complaint and the date it sent it to the company. It records no date of company response, and no date a bureau received a dispute notice under 15 U.S.C. 1681i. A complaint to the CFPB is not by itself the dispute notice the statute counts from.',
           lag=[dict(company=co, year=y, buckets={k: lag[(co, y)].get(k, 0) for k in ('0 or 1', '2 to 7', '8 to 30', 'over 30')}) for co in BUREAUS for y in YEARS],
           bureau_credit_reporting_not_timely=[])
for b in BUREAUS:
    for y in YEARS:
        lst = [(m, n, no) for (co, m, fam), (n, no) in TF.items() if co == b and fam == 'credit reporting' and m.startswith(str(y))]
        e, lo, hi = boot([x[2] for x in lst], [x[1] for x in lst], 'q1c %s %d' % (b, y))
        q1c['bureau_credit_reporting_not_timely'].append(dict(company=b, year=y, rows=sum(x[1] for x in lst), not_timely=sum(x[2] for x in lst), share=r4(e), lo=r4(lo), hi=r4(hi)))

# Q1d: sent in 0 or 1 day, 2025, against 97%
SD = [(co, m, a, b, neg) for co, m, a, b, neg in AG['SD']]
q1d = []
for y in YEARS:
    sel = [(a, b, neg) for co, m, a, b, neg in SD if m.startswith(str(y))]
    e, lo, hi = boot([x[0] for x in sel], [x[1] for x in sel], 'sent %d' % y)
    q1d.append(dict(year=y, rows=sum(x[1] for x in sel), within_1_day=sum(x[0] for x in sel), sent_before_received=sum(x[2] for x in sel), share=r4(e), lo=r4(lo), hi=r4(hi),
                    band=list(SENT_BAND) if y == 2025 else None, outcome=K.classify(lo, hi, *SENT_BAND) if y == 2025 else None))

# ---------------- 6. Q2: TCCP stated APRs beside G.19 ----------------
def num_(v):
    try: x = float(str(v).replace('%', '').replace('$', '').replace(',', '').strip())
    except Exception: return None
    return x
def apr(v):
    x = num_(v)
    if x is None: return None
    if x > 1.0: return None   # files carry fractions. A value above 1 is the files' 9.99 or 9.98 code for not applicable (999 percent), counted apart (referee R1, 10 Nov)
    return x * 100
g19 = {}; g19_header = []
try:
    t = open('data/raw/g19/cc_hist_tc_levels.html', errors='ignore').read()
    g19_header = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x)).strip() for x in re.findall(r'(?is)<th id="header[45]"[^>]*>(.*?)</th>', t)]
    for tr in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', t):
        q = re.search(r'(?is)<th scope="row"[^>]*>\s*(\d{4} Q[1-4])\s*</th>', tr)
        if not q: continue
        v = {hd: re.sub(r'<[^>]+>', '', x).strip() for hd, x in re.findall(r'(?is)<td headers="\S+ (header[45]) header10">(.*?)</td>', tr)}
        g19[q.group(1)] = (v.get('header4'), v.get('header5'))
except Exception as e:
    log('g19 read failed', repr(e))
ia, ib = (len(g19_header) == 2 and 'all credit' in g19_header[0].lower()), (len(g19_header) == 2 and 'assessed interest' in g19_header[1].lower())
tccp = []
for label, rdate, fn in TCCP:
    p = 'data/raw/tccp/' + fn
    if not os.path.exists(p): tccp.append(dict(period=label, report_date=rdate, nothing_returned='file missing')); continue
    try:
        s = list(X.sheets(p).values())[0]; hi_ = next(i for i, r in enumerate(s) if 'Institution Name' in r); h = s[hi_]
        def col(*names):
            for nm in names:
                if nm in h: return h.index(nm)
            return None
        iN = col('Institution Name'); iTop = col('Issued by Top 25 Institution')
        iMin = col('Purchase APR min') if col('Purchase APR min') is not None else col('Minimum APR'); iMed = col('Purchase APR median') if col('Purchase APR median') is not None else col('Median APR')
        iMax = col('Purchase APR max') if col('Purchase APR max') is not None else col('Maximum APR')
        iLate = col('Late Fee ($)', 'Amount (Dollars) - Late Payment Fee'); iAnn = col('Annual Fee')
        rows = [r for r in s[hi_ + 1:] if len(r) > iN and r[iN].strip()]
        def g(r, i): return r[i] if i is not None and i < len(r) else ''
        med = [(apr(g(r, iMed)), str(g(r, iTop)).strip().upper() in ('1', 'TRUE', 'YES') if iTop is not None else None) for r in rows]
        meds = np.array([m for m, _ in med if m is not None]); top = np.array([m for m, t_ in med if m is not None and t_]) if iTop is not None else np.array([])
        mins = [apr(g(r, iMin)) for r in rows]; maxs = [apr(g(r, iMax)) for r in rows]
        na_code = sum(1 for r in rows for i_ in (iMin, iMed, iMax) if num_(g(r, i_)) is not None and num_(g(r, i_)) > 1.0)
        late = np.array([x for x in (num_(g(r, iLate)) for r in rows) if x is not None and x > 0]); ann = np.array([x for x in (num_(g(r, iAnn)) for r in rows) if x is not None])
        q = '%s Q%d' % (rdate[:4], 2 if rdate[5:7] == '06' else 4); gv = g19.get(q)
        ga = num_(gv[0]) if gv and ia else None; gb = num_(gv[1]) if gv and ib else None
        def pct(a, k): return round(float(np.percentile(a, k)), 2) if len(a) else None
        row = dict(period=label, report_date=rdate, plans=len(rows), plans_with_apr=int(len(meds)), median_of_medians=pct(meds, 50), p10=pct(meds, 10), p90=pct(meds, 90),
                   top25_plans=int(len(top)) if iTop is not None else None, top25_median=pct(top, 50), top25_p10=pct(top, 10), top25_p90=pct(top, 90),
                   lowest_min=round(min(x for x in mins if x is not None), 2) if any(x is not None for x in mins) else None,
                   highest_max=round(max(x for x in maxs if x is not None), 2) if any(x is not None for x in maxs) else None,
                   late_fee_median=pct(late, 50), late_fee_plans=int(len(late)), plans_with_min=int(sum(1 for x in mins if x is not None)), not_applicable_code_cells=na_code,
                   g19_quarter=q, g19_all_accounts=ga, g19_assessed_interest=gb, outcome=K.CANNOT_TELL)
        if len(top) and ga is not None: row['display_all_accounts_inside_top25_p10_p90'] = pct(top, 10) <= ga <= pct(top, 90)
        if len(top) and gb is not None: row['display_assessed_inside_top25_p10_p90'] = pct(top, 10) <= gb <= pct(top, 90)
        tccp.append(row)
    except Exception as e:
        tccp.append(dict(period=label, report_date=rdate, nothing_returned='unreadable: ' + type(e).__name__))
kg['format'] = kg['format'] and bool(ia) and bool(ib) and len(g19) > 100

# ---------------- 7. privacy gate, gate application ----------------
BANNED = ('zip code', 'zip_code', 'state', 'tags', 'issue', 'sub-issue', 'company public response', 'narrative')
def keys_of(o, acc):
    if isinstance(o, dict):
        for k, v in o.items(): acc.add(str(k).lower()); keys_of(v, acc)
    elif isinstance(o, list):
        for v in o: keys_of(v, acc)
    return acc
body = dict(ruler1=ruler1, companies=companies, comp_fam=comp_fam, bureau_window=bureau_window, others_nt=others_nt, responses=responses, q1b_table1=q1b_table1, q1c=q1c, q1d=q1d, tccp=tccp)
kg['privacy'] = not (keys_of(body, set()) & set(BANNED))
GATE = all(kg.values())
def gate_all(obj):
    if GATE: return obj
    if isinstance(obj, dict):
        o = {k: gate_all(v) for k, v in obj.items()}
        if 'outcome' in o and o['outcome'] in K.OUTCOMES: o['outcome_before_gate'] = o['outcome']; o['outcome'] = K.CANNOT_TELL
        return o
    if isinstance(obj, list): return [gate_all(x) for x in obj]
    return obj
body = gate_all(body)
if not kg['privacy']: log('PRIVACY GATE FAILED, nothing written'); sys.exit(2)
t25 = {y: dict(tally[y]) for y in YEARS}
if not GATE:   # counted after the gate
    t25 = {y: {'CANNOT_TELL': sum(1 for c in body['companies'] if c['year'] == y), 'too_few': tally[y]['too_few']} for y in YEARS}

# ---------------- 8. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
summary = dict(
    desk='CREDIT', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    source=dict(file=CCDB_URL, file_time=zfile_time, sha256=zsha, bytes=os.path.getsize(ZIP), rows_in_window=AG['counts'].get('rows', 0), outside_window=AG['counts'].get('outside_window', 0),
                bad_date=AG['counts'].get('bad_date', 0), timely_other=AG['counts'].get('timely_other', 0), no_sent_date=AG['counts'].get('no_sent_date', 0), duplicate_ids=AG['dup_ids'], duplicate_rows=AG['dup_rows'],
                tccp_files=[x[2] for x in TCCP], g19=G19_URL, g19_header=g19_header, stale=STALE),
    frame=dict(window=['2021-01-01', '2025-12-31'], bureaus=list(BUREAUS), families=FAM, min_rows=MIN_ROWS, min_months=MIN_MONTHS, bootstrap=dict(resamples=NBOOT, seed=SEED, block='company-month')),
    gates=dict(kg, passed=GATE, api_check=g2rows),
    tally_companies=t25, wilson_display_2025={'%s|%s' % k: v for k, v in C.Counter((c['outcome'], c['wilson_reading_display']) for c in body['companies'] if c['year'] == 2025).items()} if GATE else None,
    after_data_note='At the outside referee (credit_index_referee/REFEREE.md, 10 Nov): TCCP values above 1 are read as the files\' not applicable code and counted apart (R1), at_edge_display marks intervals within 0.01 points of a band edge (R5), ruler1 printed_base_if_unpublished_timely_display and database_share_of_printed_count are shown (R7), all display only or a reader fix on the TCCP side, which has no outcome other than CANNOT_TELL. companies[].wilson and wilson_reading_display, and wilson_display_2025, were added after the data on 10 Nov 2026 (a company with no not timely complaint has a block bootstrap interval of zero width). Display only. No outcome uses them. The planted-cell test in the rule gate was changed after the first run from one planted draw to coverage over 40 draws, because one draw can miss by chance.', tally_company_family_2025=dict(tally_f) if GATE else {'CANNOT_TELL': len(body['comp_fam']), 'too_few': tally_f['too_few']},
    **body)
json.dump(summary, open('summary_credit.json.tmp', 'w'), indent=1); os.replace('summary_credit.json.tmp', 'summary_credit.json')
live = dict(summary, updated=summary['generated']); live['companies'] = [c for c in summary['companies'] if c['year'] == 2025]; live.pop('comp_fam', None)
json.dump(live, open('data/credit_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/credit_live.json.tmp', 'data/credit_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'credit_live', '--path', os.path.join(H, 'data', 'credit_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('credit_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/credit_history.jsonl', 'a') as f:
    f.write(json.dumps(dict(t=summary['generated'], sha=zsha[:16], gate=GATE, ruler1=[(x['year'], x['timely'], x['lo'], x['hi'], x['outcome']) for x in summary['ruler1']], tally=t25, stale=STALE)) + '\n')
log('gates', kg, g2rows)
for x in summary['ruler1']: log(x['year'], x['rows'], x['timely'], x['lo'], x['hi'], x['printed'], x['outcome'])
log('tally', t25); log('q1d', [(x['year'], x['share'], x['lo'], x['hi'], x['outcome']) for x in summary['q1d']])
