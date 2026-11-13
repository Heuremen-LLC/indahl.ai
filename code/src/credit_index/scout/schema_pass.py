"""Schema pass before the plan: value sets and row counts by year only. No share of any value by company is computed."""
import csv, io, zipfile, sys, collections as C, json
z = zipfile.ZipFile(sys.argv[1]); f = io.TextIOWrapper(z.open('complaints.csv'), encoding='utf-8', newline='')
r = csv.reader(f); h = next(r); ix = {k: i for i, k in enumerate(h)}
yr = C.Counter(); prod = set(); resp = set(); tim = set(); bureau = set(); via = set(); bad = 0
for row in r:
    if len(row) != len(h): bad += 1; continue
    yr[row[ix['Date received']][:4]] += 1; prod.add(row[ix['Product']]); resp.add(row[ix['Company response to consumer']]); tim.add(row[ix['Timely response?']]); via.add(row[ix['Submitted via']])
    c = row[ix['Company']]
    if any(b in c.upper() for b in ('EQUIFAX', 'EXPERIAN', 'TRANSUNION', 'TRANS UNION')): bureau.add(c)
json.dump(dict(header=h, rows_by_year=dict(sorted(yr.items())), bad_rows=bad, products=sorted(prod), responses=sorted(resp), timely_values=sorted(tim), submitted_via=sorted(via), bureau_like_names=sorted(bureau)), open(sys.argv[2], 'w'), indent=1)
