# compare numbers quoted in the STEO PDF text with the workbook values for the same issue (own regex, own reader)
import re, json, logging, sys
logging.disable(logging.CRITICAL)
import pypdf
sys.path.insert(0, '.')
import recount as R
REL, SP, copies = R.main()
relname = {d: p for d, n, p in REL}
res = []
for c in copies:
    if 'err' in c or not c['rel']: continue
    iss = relname[c['rel']]
    f = R.D+'raw/archives/%s.pdf' % iss
    try: pages = [re.sub(r'\s+', ' ', (p.extract_text() or '')).replace('‐', '-').replace('‑', '-').replace('․', '.') for p in pypdf.PdfReader(f).pages[:12]]
    except Exception: continue
    t = ' '.join(pages)
    # WTI sentence
    for sr, pat in (('WTI', r'95.percent confidence interval for the market.s expectations of monthly average WTI prices in (\w+) (\d{4}) (?:of|at) \$(\d+) per barrel and \$(\d+)'),
                    ('HH', r'bounds for the 95.percent confidence interval for (\w+) (\d{4}) contracts are \$([\d.]+) per MMBtu and \$([\d.]+)')):
        m = re.search(pat, t)
        if not m: continue
        mo = [i for i, n in enumerate(R.MONTHS) if n.startswith(m.group(1).lower()[:3])][0]+1
        ym = (int(m.group(2)), mo)
        s = c['sheets'].get(sr)
        if not s or ym not in s['rows']: res.append((iss, sr, ym, 'no row')); continue
        lo, up = s['rows'][ym][:2]
        res.append((iss, sr, ym, (float(m.group(3)), float(m.group(4))), (round(lo, 2) if isinstance(lo, float) else lo, round(up, 2) if isinstance(up, float) else up)))
for r in res: print(r)
ok = [r for r in res if len(r) == 5 and isinstance(r[4][0], float) and abs(r[3][0]-r[4][0]) <= (0.6 if r[1]=='WTI' else 0.011) and abs(r[3][1]-r[4][1]) <= (0.6 if r[1]=='WTI' else 0.011)]
print(len(res), 'quoted; agree within rounding:', len(ok))
