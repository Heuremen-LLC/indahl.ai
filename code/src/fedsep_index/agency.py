"""agency.py: FEDSEP outcome series read from the agencies that publish them (9 Nov 2026, PLAN.md Addendum 1).
Each function returns {date: value} with the same keys the FRED graph downloads used ('YYYY-MM-01' for monthly and quarterly series,
'YYYY-MM-DD' for the daily target range), so the scoring code is unchanged.
  real GDP            BEA NIPA flat file NipaDataQ.txt, series A191RX (chained dollars, quarterly)
  PCE price index     BEA NIPA flat file NipaDataM.txt, series DPCERG (monthly)
  unemployment rate   BLS public API v1, series LNS14000000 (monthly, seasonally adjusted)
  federal funds rate  Federal Reserve Board H.15 data package, series RIFSPFF_N.M (monthly average of the effective rate)
  target range        Federal Reserve Board, "Open Market Operations" page: each change in the FOMC's target range and its level
All are public-domain U.S. government data. No key is used."""
import io, re, json, html, zipfile, datetime as dt, urllib.request
UA = {'User-Agent': 'heuremen-fedsep/0.1 (+https://indahl.ai/fedsep)'}
def _get(url, data=None, headers=None, timeout=180):
    h = dict(UA, **(headers or {})); return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout).read()
def _nipa(fname, code):
    out = {}
    for line in _get('https://apps.bea.gov/national/Release/TXT/' + fname).decode('utf-8', 'replace').splitlines():
        if not line.startswith(code + ','): continue
        _, per, val = line.split(',', 2); v = float(val.strip().strip('"').replace(',', ''))
        if 'Q' in per: y, q = per.split('Q'); out['%s-%02d-01' % (y, 3 * int(q) - 2)] = v
        elif 'M' in per: y, m = per.split('M'); out['%s-%02d-01' % (y, int(m))] = v
    return out
def gdp(): return _nipa('NipaDataQ.txt', 'A191RX')
def pce(): return _nipa('NipaDataM.txt', 'DPCERG')
def unrate(first=2013):
    out, last = {}, dt.date.today().year
    for a in range(first, last + 1, 10):   # the keyless API takes at most 10 years per request
        body = json.dumps({'seriesid': ['LNS14000000'], 'startyear': str(a), 'endyear': str(min(a + 9, last))}).encode()
        d = json.loads(_get('https://api.bls.gov/publicAPI/v1/timeseries/data/', body, {'Content-Type': 'application/json'}))
        if d.get('status') != 'REQUEST_SUCCEEDED': raise RuntimeError('BLS: ' + str(d.get('message')))
        for r in d['Results']['series'][0]['data']:
            if r['period'].startswith('M') and r['period'] != 'M13' and r['value'] not in ('-', ''): out['%s-%s-01' % (r['year'], r['period'][1:])] = float(r['value'])
    return out
def fedfunds():
    z = zipfile.ZipFile(io.BytesIO(_get('https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&filetype=zip', timeout=300)))
    s = z.read('H15_data.xml').decode('utf-8'); i = s.index('SERIES_NAME="RIFSPFF_N.M"'); seg = s[i:s.index('</kf:Series>', i)]; out = {}
    for m in re.finditer(r'<frb:Obs\b[^>]*>', seg):
        v, t = re.search(r'OBS_VALUE="([^"]+)"', m.group(0)), re.search(r'TIME_PERIOD="(\d{4})-(\d\d)-\d\d"', m.group(0))
        if v and t and v.group(1) not in ('ND', 'NC', 'NA'): out['%s-%s-01' % t.groups()] = float(v.group(1))
    return out
def target_range():
    """(upper, lower) as daily dicts from the first listed change of 2008 to today, built from the Board's list of changes."""
    t = html.unescape(re.sub(r'<[^>]+>', '|', _get('https://www.federalreserve.gov/monetarypolicy/openmarket.htm').decode('utf-8', 'replace')))
    t = re.sub(r'\s+', ' ', re.sub(r'\|\s*(\|\s*)+', '|', t)); ch = []
    for blk in re.finditer(r'\|(20\d\d)\|Date\|Increase\|Decrease\|Level \(%\)\|(.*?)Back to year navigation', t):
        y = int(blk.group(1))
        for m in re.finditer(r'([A-Z][a-z]+ \d{1,2})\|(?:\*\|)?[^|]*\|[^|]*\|(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)\|', blk.group(2)):
            d = dt.datetime.strptime('%s %d' % (m.group(1), y), '%B %d %Y').date(); ch.append((d, float(m.group(3)), float(m.group(2))))
    ch.sort(); tu, tl = {}, {}
    if not ch: return tu, tl
    d, k, today = ch[0][0], 0, dt.date.today()
    while d <= today:
        while k + 1 < len(ch) and ch[k + 1][0] <= d: k += 1
        tu[d.isoformat()], tl[d.isoformat()] = ch[k][1], ch[k][2]; d += dt.timedelta(days=1)
    return tu, tl
