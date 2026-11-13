"""Referee recount pass over the CFPB complaint file. Independent of the desk code.
Streams the csv inside the zip once and writes per (company, family, year, month) counts.
Never reads ZIP code, State, Tags, Issue, Sub-issue, Company public response into any output."""
import csv, io, sys, zipfile, json, datetime, pickle

ZIP = sys.argv[1]
OUT = sys.argv[2]

FAM = {}
for fam, vals in {
    'credit reporting': ["Credit reporting", "Credit reporting, credit repair services, or other personal consumer reports", "Credit reporting or other personal consumer reports"],
    'debt collection': ["Debt collection"],
    'credit card': ["Credit card", "Credit card or prepaid card", "Prepaid card"],
    'checking or savings': ["Checking or savings account", "Bank account or service"],
    'mortgage': ["Mortgage"],
    'student loan': ["Student loan"],
    'vehicle loan': ["Vehicle loan or lease"],
    'money transfer': ["Money transfer, virtual currency, or money service", "Money transfers", "Virtual currency"],
    'personal or payday loan': ["Payday loan", "Payday loan, title loan, or personal loan", "Payday loan, title loan, personal loan, or advance loan"],
    'debt or credit management': ["Debt or credit management"],
}.items():
    for v in vals:
        FAM[v] = fam

RESP = ["Closed with explanation", "Closed with non-monetary relief", "Closed with monetary relief",
        "In progress", "Untimely response", "", "Closed", "Closed with relief", "Closed without relief"]
RIDX = {r: i for i, r in enumerate(RESP)}
# vector: 0 rows,1 yes,2 no,3 timely_other,4 lag01,5 lag_valid,6 neg,7 nosent/badsent,
# 8 b0_1, 9 b2_7, 10 b8_30, 11 b31+, 12.. resp (len RESP), last = resp_other
NV = 12 + len(RESP) + 1

ordcache = {}
def ordv(s):
    o = ordcache.get(s)
    if o is None:
        try:
            o = datetime.date(int(s[0:4]), int(s[5:7]), int(s[8:10])).toordinal()
            if len(s) != 10 or s[4] != '-' or s[7] != '-':
                o = -1
        except Exception:
            o = -1
        ordcache[s] = o
    return o

agg = {}
year_all = {}
stats = dict(total=0, bad_fields=0, bad_date=0, outside=0, in_window=0, dup_ids_all=0, dup_ids_window=0, bad_id=0)
seen_all = bytearray(1 << 25)
seen_win = bytearray(1 << 25)
lo, hi = datetime.date(2021, 1, 1).toordinal(), datetime.date(2025, 12, 31).toordinal()

with zipfile.ZipFile(ZIP) as z:
    with z.open('complaints.csv') as fb:
        f = io.TextIOWrapper(fb, encoding='utf-8', newline='')
        r = csv.reader(f)
        header = next(r)
        H = {h: i for i, h in enumerate(header)}
        iD, iP, iC, iS, iR, iT, iI = (H['Date received'], H['Product'], H['Company'], H['Date sent to company'],
                                      H['Company response to consumer'], H['Timely response?'], H['Complaint ID'])
        nh = len(header)
        for row in r:
            stats['total'] += 1
            if len(row) != nh:
                stats['bad_fields'] += 1
                continue
            d = row[iD]
            o = ordv(d)
            if o < 0:
                stats['bad_date'] += 1
                continue
            y = int(d[0:4])
            year_all[y] = year_all.get(y, 0) + 1
            try:
                cid = int(row[iI])
            except Exception:
                cid = -1
                stats['bad_id'] += 1
            if cid >= 0:
                if cid >= len(seen_all) * 8:
                    ext = bytearray(cid // 8 + 1 - len(seen_all) + (1 << 20))
                    seen_all.extend(ext); seen_win.extend(bytearray(len(ext)))
                b, bit = cid >> 3, 1 << (cid & 7)
                if seen_all[b] & bit:
                    stats['dup_ids_all'] += 1
                seen_all[b] |= bit
            if o < lo or o > hi:
                stats['outside'] += 1
                continue
            stats['in_window'] += 1
            if cid >= 0:
                if seen_win[b] & bit:
                    stats['dup_ids_window'] += 1
                    continue  # first kept
                seen_win[b] |= bit
            m = int(d[5:7])
            comp = row[iC]
            fam = FAM.get(row[iP], 'other')
            k = (comp, fam, y, m)
            v = agg.get(k)
            if v is None:
                v = [0] * NV
                agg[k] = v
            v[0] += 1
            t = row[iT]
            if t == 'Yes':
                v[1] += 1
            elif t == 'No':
                v[2] += 1
            else:
                v[3] += 1
            s = row[iS]
            os_ = ordv(s) if s else -1
            if os_ < 0:
                v[7] += 1
            else:
                lag = os_ - o
                if lag < 0:
                    v[6] += 1
                else:
                    v[5] += 1
                    if lag <= 1:
                        v[4] += 1; v[8] += 1
                    elif lag <= 7:
                        v[9] += 1
                    elif lag <= 30:
                        v[10] += 1
                    else:
                        v[11] += 1
            ri = RIDX.get(row[iR])
            if ri is None:
                v[NV - 1] += 1
            else:
                v[12 + ri] += 1

with open(OUT, 'wb') as fo:
    pickle.dump(dict(header=header, stats=stats, year_all=year_all, agg=agg, RESP=RESP), fo)
print(json.dumps(stats), json.dumps(year_all))
