#!/usr/bin/env python3
"""fetch_wayback.py: STEO desk. Lists Internet Archive copies of the EIA STEO chart gallery workbook (chart-gallery.xls and .xlsx, under
/outlooks/steo/xls/ and /forecasts/steo/xls/) and downloads each copy not yet held to data/raw/wayback, one request at a time, 2 s apart."""
import os, json, time, urllib.request, sys
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); D = 'data/raw/wayback'; os.makedirs(D, exist_ok=True)
UA = 'heuremen-steo/0.1 (+https://indahl.ai/steo)'; last = [0.0]
def get(u, tries=3):
    err = None
    for a in range(tries):
        w = 2.0 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=180) as r: b = r.read()
            last[0] = time.time(); return b
        except Exception as e:
            last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (403, 404): break
            time.sleep(8 * (a + 1))
    raise RuntimeError('fetch failed %s %r' % (u[:120], err))
rows = []
for pat in ('eia.gov/outlooks/steo/xls/chart-gallery.xls*', 'eia.gov/forecasts/steo/xls/chart-gallery.xls*'):
    try:
        d = json.loads(get('https://web.archive.org/cdx/search/cdx?url=%s&matchType=exact&output=json&fl=timestamp,original,statuscode,digest,length&filter=statuscode:200&limit=5000' % pat.replace('*', '') + '') )[1:]
    except Exception: d = []
    try: d += json.loads(get('https://web.archive.org/cdx/search/cdx?url=%s&output=json&fl=timestamp,original,statuscode,digest,length&filter=statuscode:200&limit=5000' % pat))[1:]
    except Exception as e: print('cdx failed', pat, e, file=sys.stderr)
    rows += d
seen = set(); uniq = []
for ts, orig, sc, dg, ln in sorted(rows):
    if dg in seen: continue          # same bytes as an earlier copy
    seen.add(dg); uniq.append(dict(ts=ts, url=orig, digest=dg, length=ln))
json.dump(uniq, open(D + '/cdx_chart_gallery.json', 'w'), indent=0)
for u in uniq:
    ext = '.xlsx' if u['url'].split('?')[0].endswith('.xlsx') else '.xls'
    f = '%s/cg_%s_%s%s' % (D, u['ts'], u['digest'][:8], ext)
    if os.path.exists(f) and os.path.getsize(f) > 1000: continue
    try: b = get('https://web.archive.org/web/%sid_/%s' % (u['ts'], u['url'])); open(f + '.part', 'wb').write(b); os.replace(f + '.part', f); print('got', f, len(b))
    except Exception as e: print('not fetched', u['ts'], e)
print('distinct copies', len(uniq))
