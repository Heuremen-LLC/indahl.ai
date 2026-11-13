#!/usr/bin/env python3
"""parse_momr.py: reads every cached MOMR PDF and writes data/momr_secondary.csv: one row per issue, member, month with the secondary-source crude production (tb/d),
the source PDF, page and table title. Only the DoC secondary-sources table is read. Run with the venv python (pymupdf)."""
import os, re, csv, glob, json, warnings
warnings.filterwarnings('ignore')
import pymupdf
H = os.path.dirname(os.path.abspath(__file__))
MEM = ['Angola','Algeria','Congo','Equatorial Guinea','Gabon','IR Iran','Iraq','Kuwait','Libya','Nigeria','Saudi Arabia','UAE','Venezuela','Azerbaijan','Bahrain','Brunei','Kazakhstan','Malaysia','Mexico','Oman','Russia','Sudan','South Sudan']
MON = {m: i + 1 for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
num = re.compile(r'^-?[\d,]+(\.\d+)?\*?$|^\.\.$|^-$')
def tonum(s):
    s = s.rstrip('*').replace(',', '')
    return None if s in ('..', '-') else float(s)
def parse_issue(path):
    """Every table whose header block starts with the line Secondary (sources) is read from that line to the next Notes line. Older issues hold OPEC members and non-OPEC DoC members in separate tables."""
    d = pymupdf.open(path); rows = {}; labs = None; pages = {}; title = ''
    for pi, p in enumerate(d):
        t = p.get_text()
        if 'Secondary' not in t or not re.search(r'(?i)secondary\s*\n\s*sources|^Secondary\s*sources', t, re.M) and 'Secondary' not in t: continue
        L = [x.strip() for x in t.split('\n') if x.strip()]
        for s0 in [k for k, x in enumerate(L) if x == 'Secondary']:
            e0 = next((k for k in range(s0, len(L)) if L[k].startswith('Notes')), len(L)); seg = L[s0:e0]
            lb = [x for x in seg if re.match(r'^[A-Z][a-z]{2} \d\d$', x)]
            if len(lb) < 3: continue
            k = 0
            while k < len(seg):
                if seg[k] in MEM and seg[k] not in rows:
                    name = seg[k]; vals = []; k += 1
                    while k < len(seg) and num.match(seg[k]): vals.append(seg[k]); k += 1
                    rows[name] = vals; pages[name] = pi + 1
                else: k += 1
            if labs is None: labs = lb[:3] if len(lb) >= 3 else lb
            tt = re.search(r'Table\s+\d\s*[–-]\s*\d+:?\s*[^\n]*secondary sources[^\n]*', t)
            if tt and not title: title = tt.group(0).strip()
    if not rows: return None, 'no page'
    return dict(page=pages, labs=labs, rows=rows, title=title), None
def main():
    out = []; bad = {}
    for f in sorted(glob.glob(H + '/data/raw/momr/momr_*.pdf')):
        key = os.path.basename(f)[5:12]
        try: r, err = parse_issue(f)
        except Exception as e: r, err = None, repr(e)
        if r is None: bad[key] = err; continue
        labs = r['labs'][-3:] if r['labs'] and len(r['labs']) >= 3 else None
        if not labs: bad[key] = 'no month labels %s' % r['labs']; continue
        months = ['20%s-%02d' % (l[4:], MON[l[:3]]) for l in labs]
        for name, vals in r['rows'].items():
            if len(vals) < 4: bad.setdefault(key + ' ' + name, 'short row %s' % vals); continue
            m3 = [tonum(v) for v in vals[-4:-1]]   # last value is the change column
            for mo, v in zip(months, m3): out.append([key, mo, name, '' if v is None else v, 'momr_%s.pdf' % key, r['page'][name], r['title'][:70]])
    with open(H + '/data/momr_secondary.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['issue','month','member','secondary_tbd','pdf','page','table']); w.writerows(out)
    json.dump(bad, open(H + '/data/momr_parse_problems.json', 'w'), indent=1)
    print(len(out), 'rows', len(bad), 'problems')
main()
