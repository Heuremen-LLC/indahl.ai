#!/usr/bin/env python3
"""fetch_archive.py: STEO desk. Reads the EIA STEO archive index (outlook.php), writes data/releases.json (issue, release date, pdf), and downloads
each archived PDF from 2010 on that is not yet held, one request at a time, 1.5 s apart. Also refreshes the two monthly spot price files. Keyless."""
import os, re, json, time, html, urllib.request, sys
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
UA = 'heuremen-steo/0.1 (+https://indahl.ai/steo)'; R = 'data/raw'
for d in (R, R + '/archives', R + '/spot', R + '/terms'): os.makedirs(d, exist_ok=True)
last = [0.0]
def get(u, tries=3):
    for a in range(tries):
        w = 1.5 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=120) as r: b = r.read()
            last[0] = time.time(); return b
        except Exception as e:
            last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (403, 404): break
            time.sleep(5 * (a + 1))
    raise RuntimeError('fetch failed %s %r' % (u, err))
idx = R + '/terms/archive_index_outlook.html'
try: open(idx, 'wb').write(get('https://www.eia.gov/outlooks/steo/outlook.php'))
except Exception as e: print('index fetch failed, using last copy', e, file=sys.stderr)
t = open(idx, errors='ignore').read(); rel = []
for r in re.findall(r'(?is)<tr.*?</tr>', t):
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', r); p = re.search(r'href="(archives/[a-z]{3}\d\d\.pdf)"', r, re.I)
    if m and p: rel.append(dict(issue=p.group(1)[9:14].lower(), released='%s-%02d-%02d' % (m.group(3), int(m.group(1)), int(m.group(2))), pdf=p.group(1)))
rel.sort(key=lambda x: x['released']); json.dump(rel, open('data/releases.json', 'w'), indent=0)
want = [x for x in rel if '2010-01-01' <= x['released']]
for x in want:
    f = R + '/archives/%s.pdf' % x['issue']
    if os.path.exists(f) and os.path.getsize(f) > 10000: continue
    try: b = get('https://www.eia.gov/outlooks/steo/' + x['pdf']); open(f + '.part', 'wb').write(b); os.replace(f + '.part', f); print('got', x['issue'], len(b))
    except Exception as e: print('missing', x['issue'], e)
for n, u in (('RWTCm.xls', 'https://www.eia.gov/dnav/pet/hist_xls/RWTCm.xls'), ('RNGWHHDm.xls', 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls')):
    try: b = get(u); open(R + '/spot/' + n, 'wb').write(b)
    except Exception as e: print('spot fetch failed', n, e, file=sys.stderr)
print('releases', len(rel), 'from 2010', len(want))
