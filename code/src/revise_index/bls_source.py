"""bls_source.py: REVISE reads from the BLS itself (9 Nov 2026, PLAN.md Addendum 1).
first_second_third(): the seasonally adjusted 1st, 2nd and 3rd over-the-month estimates of total nonfarm employment, in thousands, from the
BLS table "Nonfarm Payroll Employment: Revisions between over-the-month estimates, 1979-present" (bls.gov/web/empsit/cesnaicsrev.htm).
most_recent(): the current over-the-month change of the level series CES0000000001 from the BLS flat file ce.data.00a.TotalNonfarm.Employment.
Keys are 'YYYY:MM', as in the Philadelphia Fed file this replaces. BLS data are in the public domain."""
import re, json, html, hashlib, datetime as dt, urllib.request
UA = {'User-Agent': 'heuremen-revise/0.1 (+https://indahl.ai/revise)'}
TABLE = 'https://www.bls.gov/web/empsit/cesnaicsrev.htm'
MON = {m: i + 1 for i, m in enumerate(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))}   # the table writes Jun., June, Sep., Sept. ...
def _get(url, data=None, headers=None, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=dict(UA, **(headers or {}))), timeout=timeout).read()
def table_raw(): return _get(TABLE)
def first_second_third(raw=None):
    s = (raw or table_raw()).decode('utf-8', 'replace'); out = {}
    for tb in re.finditer(r'<table id="(\d{4})".*?</table>', s, re.S):
        for tr in re.finditer(r'<tr[^>]*>(.*?)</tr>', tb.group(0), re.S):
            th = re.search(r'<p class="sub0">([A-Za-z]+)\.?</p>', tr.group(1)); td = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', tr.group(1), re.S)]
            if not th or len(td) < 4 or th.group(1)[:3] not in MON or not re.fullmatch(r'\d{4}', td[0]): continue
            num = lambda x: float(x.replace(',', '')) if re.fullmatch(r'-?[\d,]+(\.\d+)?', x or '') else None
            out['%s:%02d' % (td[0], MON[th.group(1)[:3]])] = dict(first=num(td[1]), second=num(td[2]), third=num(td[3]))
    return out
FLAT = 'https://download.bls.gov/pub/time.series/ce/ce.data.00a.TotalNonfarm.Employment'
def flat_raw(): return _get(FLAT)
def most_recent(raw=None):
    """Current over-the-month change of CES0000000001, from the BLS flat file of total nonfarm employment (download.bls.gov, no key, no daily limit).
    raw: the flat file's bytes as read (10 Nov 2026: revise_tick.py keeps each version it reads in data/files/, so a run can be recomputed offline)."""
    pts = {}
    for line in (raw if raw is not None else flat_raw()).decode('utf-8', 'replace').splitlines():
        f = line.split('\t')
        if len(f) < 4 or f[0].strip() != 'CES0000000001' or not f[2].strip().startswith('M') or f[2].strip() == 'M13': continue
        try: pts[(int(f[1]), int(f[2].strip()[1:]))] = float(f[3].strip())
        except ValueError: continue
    prev = lambda k: (k[0] - (k[1] == 1), k[1] - 1 or 12)
    return {'%04d:%02d' % k: round(pts[k] - pts[prev(k)], 1) for k in pts if prev(k) in pts}
