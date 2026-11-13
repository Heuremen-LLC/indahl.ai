#!/usr/bin/env python3
"""adspend_tick.py: ADSPEND, section 4 of the SOCIAL desk, per PLAN.md and its addenda (1 to 7). Rerunnable, installs no timer.
Reads Google's stated weekly election-ad spend per advertiser (keyless bundle) against each matched committee's FEC-reported payments to
Google (keyless bulk files: Schedule B operating expenditures and Schedule E), per cycle and per quarter. Writes data/adspend.json (every
row, quarters included), data/adspend_public.json (cycle rows, the file the page links), summary_adspend.json and section_adspend.html.
Never reads individual contributor files, the cm treasurer field, or the cn candidate name and address fields.
Run: python3 -I adspend_tick.py [--no-fetch] [--selftest]"""
import os, sys, re, io, csv, json, time, zipfile, bisect, datetime as D, collections as C, urllib.request, shutil, subprocess

H = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(H, 'data', 'raw'); os.makedirs(RAW, exist_ok=True)
UA = 'heuremen-adspend/0.1 (+https://indahl.ai/social)'
CYCLES = (2020, 2022, 2024, 2026)
GBUNDLE = 'https://storage.googleapis.com/political-csv/google-political-ads-transparency-bundle.zip'
GFILES = ('README.txt', 'google-political-ads-updated.csv', 'google-political-ads-advertiser-stats.csv', 'google-political-ads-advertiser-weekly-spend.csv',
          'google-political-ads-advertiser-geo-spend.csv')
FECB = 'https://www.fec.gov/files/bulk-downloads/'
PUBLIC_DATA_URL = '/social/adspend.json'          # where the page links the slim public file (Bones sets the final path at ship)
PLAN_URL = 'https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/adspend'
RULERS = {'primary': (31, 92), 'second': (92, 183)}          # (P days before the ad week, Q days after it), PLAN.md
ABOVE, BELOW, CONSISTENT, CANNOT_TELL, NOTHING = 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED'
SIZE_ABS, SIZE_REL, BAND_FACTOR, ROUND = 1000.0, 0.10, 2.0, 100.0
UNITEMIZED_CAP, UNSEEN_COVERAGE = 400.0, 0.9      # Addendum 5: 11 CFR 104.3(b)(3)(i) and (b)(4)(i); coverage threshold defined after the data
GEO_SHARE, FIRST_ACTIVITY_DAYS = 2.0 / 3.0, 90     # Addendum 7: match validity, defined after the data
FIRST_ACTIVITY_FROM = D.date(2019, 4, 1).toordinal()
SCOPE_TYPES = set('ICEZ')

# ---------------------------------------------------------------- payee and purpose rules (PLAN.md patterns, with the departures recorded in Addendum 6)
G_PAYEE = re.compile(r'GOOGLE|YOUTUBE|YOU ?TUBE|ADWORDS|DOUBLECLICK|ALPHABET INC|\bG ?-?SUITE\b|\bGSUITE\b')
G_EXCL = re.compile(r'TOP OF GOOGLE')
MIXED = re.compile(r'FACEBOOK|\bFB\b|\bMETA\b|TIKTOK|\bWIX\b|YAHOO|\bBING\b|MICROSOFT|AMAZON|TWITTER')
AD_P = re.compile(r'ADVERTI|ADVERTIZ|\bADS?\b|\bAD-|AD ?BUY|MEDIA BUY|PLACEMENT|PAID MEDIA|DIGITAL MEDIA|ONLINE FUNDRAISING|ACQUISITION|LIST BUILDING|DIGITAL ADVOCACY|ELECTIONEERING|PROMOTION|PROMOTED|MARKETING|YOUTUBE|PRE-?ROLL|\bSEM\b|\bPPC\b|PAY PER CLICK')
NONAD_P = re.compile(r'SOFTWARE|SUBSCRIPTION|E-?MAIL|HOSTING|WEB ?SITE|WEB SERVICE|DOMAIN|G-?SUITE|GSUITE|WORKSPACE|CLOUD|STORAGE|COMPUTER|\bIT\b|TECHNOLOGY|TECH SUPPORT|OFFICE|PHONE|VOICE|INTERNET SERVICE|INTERNET UTILITY|UTILIT|DATA ?BASE|DATA SERVICE|LICENS|\bAPPS?\b|PRODUCTIVITY|ORGANIZATIONAL TOOLS|DIGITAL TOOLS|PAYROLL|EQUIPMENT|SUPPLIES|WIRE SERVICE|SERVER|VOTER FILE|FIBER|CATERING|TRAVEL|RECRUIT|EMPLOYMENT|REFUND')
NONAD_PAYEE = re.compile(r'WORKSPACE|G ?-?SUITE|GSUITE|SUITES?\b|CLOUD|DOMAINS?|FIBER|\bFI\b|F1 PHONE|VOICE|\bPLAY\b|STORE|STORAGE|PHOTOS|\bNEST\b|GMAIL|\bTV\b|YOUTUBETV|PREMIUM|\bPRO\b|\bAPPS?\b|\bAPS\b|\bPAY\b|WALLET|LOOKER|CHATGPT|OTTER|CLASH|FOOTBALL|PHONE|MERCHANDISE|CATERING|OPERACIONES')
AD_PAYEE = re.compile(r'\bADS?\b|\*ADS|GOOGLEADS|ADS\d|ADWORDS|ADWRDS|\bADX\b|ADVERTIS|\bADDS\b|\bAD SERVICES|LEADS|DOUBLECLICK')   # Addendum 6.1 records the extra words
YT = re.compile(r'YOUTUBE|YOU TUBE')                      # an ad product only when no non-ad product word is present
POOL_X = re.compile(r'DIGITAL|MEDIA|ONLINE|INTERNET|\bWEB\b|SOCIAL|SEARCH|VIDEO|STREAMING|\bCTV\b|\bOTT\b|PROGRAMMATIC|CONNECTED TV')
EST_RX = re.compile(r'ESTIMAT')                                                         # Addendum 7: filer estimates on Schedule E
CARD_RX = re.compile(r'CREDIT CARD|\bCC\b|AMEX|AMERICAN EXPRESS|VISA|MASTERCARD|CARD PAYMENT|CHARGE CARD|CAPITAL ONE|CHASE|REIMB')   # Addendum 7 flag (referee's families)
NOTCAND = [(re.compile(r'NOT CANDIDATE SP|NON[- ]?CANDIDATE'), 'not candidate-specific'), (re.compile(r'NO EXPRESS ADVOC|NOT EXPRESS ADVOC|NON[- ]?EXPRESS'), 'no express advocacy'),
           (re.compile(r'\bNON[- ]?IE\b'), 'not an independent expenditure'), (re.compile(r'NON[- ]?FEDERAL'), 'nonfederal')]
STEM_STOP = {'PAC', 'INC', 'INCORPORATED', 'LLC', 'CORP', 'CORPORATION', 'THE', 'FEDERAL', 'CO'}
def up(s): return re.sub(r'\s+', ' ', (s or '').upper()).strip()
def is_google(payee):
    p = up(payee); return bool(G_PAYEE.search(p)) and not G_EXCL.search(p)
def payee_kind(p):
    if MIXED.search(p): return 'mixed'
    n = bool(NONAD_PAYEE.search(p)); a = bool(AD_PAYEE.search(p)) or (bool(YT.search(p)) and not n)
    return 'neutral' if (a and n) else ('ad' if a else ('nonad' if n else 'neutral'))
def gclass(payee, purpose):
    """AD, NONAD, UNCLEAR or MIXED for a Google row on Schedule B (PLAN.md payee rule)."""
    k = payee_kind(up(payee)); pu = up(purpose); pa, pn = bool(AD_P.search(pu)), bool(NONAD_P.search(pu))
    if k == 'mixed': return 'MIXED'
    if pa and not pn: return 'AD' if k != 'nonad' else 'UNCLEAR'
    if pn and not pa: return 'NONAD' if k != 'ad' else 'UNCLEAR'
    if pa and pn: return 'UNCLEAR'
    return 'AD' if k == 'ad' else ('NONAD' if k == 'nonad' else 'UNCLEAR')
def is_pool_purpose(purpose):
    pu = up(purpose); return bool(AD_P.search(pu) or POOL_X.search(pu))
def norm_name(s): return re.sub(r'\s+', ' ', re.sub(r'[^A-Z0-9]', ' ', (s or '').upper().replace('&', ' AND '))).strip()
def stem(s):
    w = [x for x in norm_name(s).split() if x not in STEM_STOP]; t = ' '.join(w)
    return t if len(w) >= 2 and len(t) >= 8 else None
def notcand_labels(purpose):
    pu = up(purpose); return [lab for rx, lab in NOTCAND if rx.search(pu)]

# ---------------------------------------------------------------- dates
MON = {m: i for i, m in enumerate(('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'), 1)}
def d_ord(y, m, d):
    try: return D.date(y, m, d).toordinal()
    except Exception: return None
def p_mdy(s):          # MM/DD/YYYY (oppexp, webk, weball)
    if len(s) != 10 or s[2] != '/' or s[5] != '/': return None
    try: return d_ord(int(s[6:]), int(s[:2]), int(s[3:5]))
    except Exception: return None
def p_ie(s):           # DD-MON-YY (independent expenditure file), else MM/DD/YYYY
    s = (s or '').strip().upper()
    m = re.match(r'^(\d{1,2})-([A-Z]{3})-(\d{2})$', s)
    if m and m.group(2) in MON:
        y = int(m.group(3)); return d_ord(2000 + y if y < 70 else 1900 + y, MON[m.group(2)], int(m.group(1)))
    return p_mdy(s)
def iso(o): return D.date.fromordinal(o).isoformat() if o else None
def qstarts(a, b):
    """calendar quarters [qa, qb] intersecting [a, b], clipped."""
    out = []; d = D.date.fromordinal(a); y, q = d.year, (d.month - 1) // 3
    while True:
        qa = D.date(y, 3 * q + 1, 1).toordinal(); ny, nq = (y, q + 1) if q < 3 else (y + 1, 0); qb = D.date(ny, 3 * nq + 1, 1).toordinal() - 1
        if qa > b: break
        out.append(('%dQ%d' % (y, q + 1), max(a, qa), min(b, qb), qa, qb)); y, q = ny, nq
    return out
def num(s):
    try: return float(s or 0)
    except Exception: return 0.0

# ---------------------------------------------------------------- fetch (only when the remote copy changed)
def head(url):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r: return r.headers.get('Last-Modified'), int(r.headers.get('Content-Length') or 0)
def fetch_all(no_fetch):
    man_p = os.path.join(RAW, 'manifest.json'); man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    want = [(GBUNDLE, os.path.join(RAW, 'google', 'google-political-ads-transparency-bundle.zip'))]
    for c in CYCLES:
        y = str(c)[2:]
        for f in ('oppexp%s.zip' % y, 'cm%s.zip' % y, 'cn%s.zip' % y, 'webk%s.zip' % y, 'weball%s.zip' % y, 'independent_expenditure_%d.csv' % c):
            want.append((FECB + '%d/%s' % (c, f), os.path.join(RAW, 'fec', str(c), f)))
    for f in ('oppexp_header_file.csv', 'cm_header_file.csv', 'cn_header_file.csv'):
        want.append((FECB + 'data_dictionaries/' + f, os.path.join(RAW, 'fec', 'dict', f)))
    changed_google = False
    for url, path in want:
        rec = man.get(path, {})
        if no_fetch:
            if not os.path.exists(path): raise SystemExit('missing ' + path + ' (run without --no-fetch)')
            continue
        try: lm, size = head(url)
        except Exception as e: print('adspend: head failed', url, e, file=sys.stderr); lm, size = rec.get('last_modified'), rec.get('size')
        if os.path.exists(path) and rec.get('last_modified') == lm and os.path.getsize(path) == size: continue
        if os.path.exists(path) and not rec and size and os.path.getsize(path) == size:
            man[path] = dict(url=url, last_modified=lm, size=size, fetched=None); continue      # first run on files fetched by hand
        os.makedirs(os.path.dirname(path), exist_ok=True); tmp = path + '.part'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=300) as r, open(tmp, 'wb') as o: shutil.copyfileobj(r, o, 1 << 20)
        os.replace(tmp, path); man[path] = dict(url=url, last_modified=lm, size=os.path.getsize(path), fetched=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        changed_google |= path.endswith('bundle.zip'); print('adspend: fetched', os.path.basename(path))
    x = os.path.join(RAW, 'google', 'x')
    if changed_google or not all(os.path.exists(os.path.join(x, f)) for f in GFILES):
        os.makedirs(x, exist_ok=True)
        with zipfile.ZipFile(want[0][1]) as z:
            for f in GFILES: z.extract(f, x)
    json.dump(man, open(man_p, 'w'), indent=1); return man

# ---------------------------------------------------------------- FEC reference files
def read_zip_lines(path):
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as fh:
            for l in io.TextIOWrapper(fh, encoding='latin-1', newline=''): yield l.rstrip('\r\n').split('|')
def load_cm():
    cm = {}; names = C.defaultdict(set)
    for c in CYCLES:
        for f in read_zip_lines(os.path.join(RAW, 'fec', str(c), 'cm%s.zip' % str(c)[2:])):
            if len(f) < 15: continue
            cid = f[0]; rec = dict(name=f[1].strip(), st=f[6].strip(), dsgn=f[8], tp=f[9], party=f[10], cand=f[14].strip())   # f[2] (treasurer) is never read
            cm.setdefault(cid, {})[c] = rec; names[norm_name(f[1])].add(cid)
    return cm, names
def load_cn():
    """Candidate master per cycle. Only CAND_ID, CAND_ELECTION_YR, CAND_OFFICE_ST, CAND_OFFICE, CAND_STATUS and CAND_PCC are read."""
    cn = {}
    for c in CYCLES:
        cn[c] = {}
        for f in read_zip_lines(os.path.join(RAW, 'fec', str(c), 'cn%s.zip' % str(c)[2:])):
            if len(f) < 10: continue
            try: yr = int(f[3])
            except Exception: yr = None
            cn[c][f[0]] = dict(yr=yr, ost=f[4].strip(), off=f[5].strip(), status=f[8].strip(), pcc=f[9].strip())
    return cn
def load_summaries():
    wk, wa = {}, {}
    for c in CYCLES:
        y = str(c)[2:]; wk[c] = {}; wa[c] = {}
        for f in read_zip_lines(os.path.join(RAW, 'fec', str(c), 'webk%s.zip' % y)):
            if len(f) >= 27:
                g = lambda i: num(f[i]) if re.fullmatch(r'-?[0-9.]+', f[i] or '0') else 0.0
                implied = g(12) - g(13) - g(14) - g(15) - g(17) - g(22) - g(23) - g(24)      # Addendum 4
                nonempty = bool(p_mdy(f[26])) or any(g(i) != 0 for i in range(5, 26))       # Addendum 7: an empty record counts as no summary
                wk[c][f[0]] = dict(cvg=p_mdy(f[26]), coord=g(24), ie_tot=g(23), implied=implied, nonempty=nonempty)
        for f in read_zip_lines(os.path.join(RAW, 'fec', str(c), 'weball%s.zip' % y)):
            if len(f) >= 30:                                                      # candidate name field is never read
                g = lambda i: num(f[i]) if re.fullmatch(r'-?[0-9.]+', f[i] or '0') else 0.0
                nonempty = bool(p_mdy(f[27])) or any(g(i) != 0 for i in list(range(5, 18)) + [25, 26, 28, 29])
                wa[c][f[0]] = dict(cvg=p_mdy(f[27]), implied=g(7) - g(8) - g(14) - g(15) - g(28) - g(29), nonempty=nonempty)
    return wk, wa

# ---------------------------------------------------------------- Google side
def load_google():
    x = os.path.join(RAW, 'google', 'x')
    st = list(csv.DictReader(open(os.path.join(x, 'google-political-ads-advertiser-stats.csv'), newline='', encoding='utf-8')))
    upd = open(os.path.join(x, 'google-political-ads-updated.csv'), encoding='utf-8').read().strip().splitlines()[-1]
    weekly = C.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(x, 'google-political-ads-advertiser-weekly-spend.csv'), newline='', encoding='utf-8')):
        y, m, d = map(int, r['Week_Start_Date'].split('-')); weekly[r['Advertiser_ID']].append((D.date(y, m, d).toordinal(), float(r['Spend_USD'] or 0)))
    for a in weekly: weekly[a].sort()
    geo = C.defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(x, 'google-political-ads-advertiser-geo-spend.csv'), newline='', encoding='utf-8')):
        v = float(r['Spend_USD'] or 0)
        if r['Country'] == 'US' and v > 0: geo[r['Advertiser_ID']][r['Country_Subdivision_Primary'].strip()] = v
    return st, weekly, upd, geo

def google_band(weeks, a, b, P, Q):
    lo = hi = pt = pos = 0.0; nl = nh = 0
    for s, v in weeks:
        if s + 6 + Q < a or s - P > b:
            continue
        hi += v + ROUND; nh += 1; pos += v
        if s >= a + P and s + 6 + Q <= b: lo += max(0.0, v - ROUND); nl += 1
    for s, v in weeks:
        if a <= s <= b: pt += v
    return dict(lo=lo, hi=hi, pt=pt, weeks_lo=nl, weeks_hi=nh, possible_spend=pos)

# ---------------------------------------------------------------- classification (PLAN.md outcomes with Addenda 3, 4, 5 and 7)
REASON = dict(
    scope='scope: committee type files no operating expenditures',
    cycle_reg='cycle: the matched committee is not registered with the FEC in this cycle',
    cycle_cand='cycle: the matched committee\'s candidate was not a candidate in this cycle',
    nothing='the FEC files hold no row and no summary for the committee in this cycle',
    name_nothing='name: matched by name only, and the FEC files hold no row and no summary for the committee in this cycle',
    name_below='name: the gap rests on an advertiser matched by name only',
    no_spend='no Google spend: Google lists no election-ad spend for this advertiser in the window',
    estimates='estimates: the reading rests on amounts the filer marked as estimates in 24- or 48-hour reports',
    above='ad payments to Google exceed the most the stated spend allows',
    below='every Google payment, the pool and unseen money together are short of the least the stated spend allows',
    consistent='reported payments sit inside the band of the stated spend',
    unseen='unseen: money in the summary that the itemized file does not show could decide the side',
    agency='agency: direct payments fall short and payments to others for ads, digital or media could cover the gap',
    near='near: outside the band by less than the size that matters',
    band='band: the timing band spans more than a factor of two',
    purpose='purpose: rows of unclear or non-ad purpose decide the side')
def core(G_lo, G_hi, d_lo, d_hi, pool, unseen):
    """ABOVE, BELOW or CONSISTENT on the plan's tests, else None."""
    if d_lo - G_hi >= max(SIZE_ABS, SIZE_REL * G_hi): return ABOVE
    if G_lo - (max(d_hi, 0.0) + pool + unseen) >= max(SIZE_ABS, SIZE_REL * G_lo): return BELOW
    if G_lo > 0 and G_hi <= BAND_FACTOR * G_lo and G_lo <= d_lo and d_hi + unseen <= G_hi: return CONSISTENT
    return None
def classify(g, f, unseen, ctx, g_noname=None):
    """g: Google band; f: dict(d_lo, d_lo_est, d_hi, pool); ctx: scope, cycle (reason key or ''), nothing, name_only, has_name, spend_listed.
    Returns (outcome, reason, tests)."""
    G_lo, G_hi = g['lo'], g['hi']; d_lo, d_lo_est, d_hi, pool = f['d_lo'], f['d_lo_est'], f['d_hi'], f['pool']
    upper = max(d_hi, 0.0) + pool + unseen
    above_m = d_lo - G_hi; above_size = max(SIZE_ABS, SIZE_REL * G_hi)
    below_m = G_lo - upper; below_size = max(SIZE_ABS, SIZE_REL * G_lo)
    tests = dict(above_margin=round(above_m, 2), above_size=round(above_size, 2), below_margin=round(below_m, 2), below_size=round(below_size, 2), unseen=round(unseen, 2))
    if ctx['scope']: return CANNOT_TELL, REASON['scope'], tests
    if ctx['cycle']: return CANNOT_TELL, REASON[ctx['cycle']], tests
    if ctx['nothing']: return (CANNOT_TELL, REASON['name_nothing'], tests) if ctx['name_only'] else (NOTHING, REASON['nothing'], tests)
    o = core(G_lo, G_hi, d_lo, d_hi, pool, unseen)
    if o == ABOVE:
        return (ABOVE, REASON['above'], tests) if ctx['spend_listed'] else (CANNOT_TELL, REASON['no_spend'], tests)
    if o == BELOW:
        if ctx['has_name'] and g_noname is not None:
            gl = g_noname['lo']
            if gl - upper < max(SIZE_ABS, SIZE_REL * gl): return CANNOT_TELL, REASON['name_below'], tests
        return BELOW, REASON['below'], tests
    if o == CONSISTENT: return CONSISTENT, REASON['consistent'], tests
    if d_lo_est != d_lo and core(G_lo, G_hi, d_lo_est, d_hi, pool, unseen) in (ABOVE, CONSISTENT):
        return CANNOT_TELL, REASON['no_spend' if not ctx['spend_listed'] else 'estimates'], tests
    band_ok = G_lo > 0 and G_hi <= BAND_FACTOR * G_lo
    inside = G_lo <= d_lo and d_hi <= G_hi
    if inside and band_ok: return CANNOT_TELL, REASON['unseen'], tests
    if d_hi < G_lo:
        gap = G_lo - (max(d_hi, 0.0) + pool)
        if gap <= 0: return CANNOT_TELL, REASON['agency'], tests
        if gap >= below_size: return CANNOT_TELL, REASON['unseen'], tests
        return CANNOT_TELL, REASON['near'], tests
    if not band_ok and inside: return CANNOT_TELL, REASON['band'], tests
    if (d_lo < G_lo <= d_hi) or (d_lo <= G_hi < d_hi): return CANNOT_TELL, REASON['purpose'], tests
    if not band_ok: return CANNOT_TELL, REASON['band'], tests
    return CANNOT_TELL, REASON['near'], tests

def selftest():
    """Planted rows (PLAN.md known-good 2, extended for Addendum 7). Returns (ok, details)."""
    a, b = D.date(2023, 1, 1).toordinal(), D.date(2024, 12, 31).toordinal(); sun = D.date(2023, 1, 1).toordinal()
    steady = [(sun + 7 * i, 10000.0) for i in range(105)]; late = [(D.date(2024, 11, 3).toordinal() + 7 * i, 125000.0) for i in range(8)]
    small = [(D.date(2024, 3, 3).toordinal() + 7 * i, 1000.0) for i in range(52)]
    P, Q = RULERS['primary']; gs, gl, gm = google_band(steady, a, b, P, Q), google_band(late, a, b, P, Q), google_band(small, a, b, P, Q)
    F = lambda dl, dh, pool, est=None: dict(d_lo=dl, d_lo_est=dl if est is None else est, d_hi=dh, pool=pool)
    X = lambda **k: dict(dict(scope=False, cycle='', nothing=False, name_only=False, has_name=False, spend_listed=True), **k)
    zero = dict(lo=0.0, hi=0.0)
    cases = [('ABOVE', classify(gm, F(2e5, 2e5, 0), 0, X())[0], ABOVE), ('BELOW', classify(gs, F(0, 0, 0), 0, X())[0], BELOW),
             ('CONSISTENT', classify(gs, F(gs['pt'], gs['pt'], 5e6), 0, X())[0], CONSISTENT), ('agency', classify(gs, F(1e5, 1e5, 2e6), 0, X())[1][:6], 'agency'),
             ('band', classify(gl, F(1e6, 1e6, 0), 0, X())[1][:4], 'band'), ('NOTHING', classify(gs, F(0, 0, 0), 0, X(nothing=True))[0], NOTHING),
             ('scope', classify(gs, F(0, 0, 0), 0, X(scope=True))[1][:5], 'scope'), ('scope before nothing', classify(gs, F(0, 0, 0), 0, X(scope=True, nothing=True))[1][:5], 'scope'),
             ('unseen blocks BELOW', classify(gs, F(0, 0, 0), 5e6, X())[1][:6], 'unseen'), ('unseen blocks CONSISTENT', classify(gs, F(gs['pt'], gs['pt'], 0), 5e5, X())[1][:6], 'unseen'),
             ('small unseen keeps CONSISTENT', classify(gs, F(gs['pt'], gs['pt'], 0), 100, X())[0], CONSISTENT), ('small unseen keeps BELOW', classify(gs, F(0, 0, 0), 100, X())[0], BELOW),
             ('cycle', classify(gs, F(0, 0, 0), 0, X(cycle='cycle_cand'))[1][:5], 'cycle'), ('cycle before nothing', classify(gs, F(0, 0, 0), 0, X(cycle='cycle_reg', nothing=True))[1][:5], 'cycle'),
             ('name only nothing', classify(gs, F(0, 0, 0), 0, X(nothing=True, name_only=True))[1][:4], 'name'),
             ('no spend blocks ABOVE', classify(gm, F(2e5, 2e5, 0), 0, X(spend_listed=False))[1][:14], 'no Google spen'),
             ('estimates block ABOVE', classify(gm, F(0, 2e5, 0, est=2e5), 0, X())[1][:9], 'estimates'),
             ('name cannot decide BELOW', classify(gs, F(0, 0, 0), 0, X(has_name=True), g_noname=zero)[1][:4], 'name'),
             ('name with id spend keeps BELOW', classify(gs, F(0, 0, 0), 0, X(has_name=True), g_noname=gs)[0], BELOW)]
    det = {n: (got, want) for n, got, want in cases}; ok = all(g == w for g, w in det.values())
    pc = [('GOOGLE LLC', 'DIGITAL ADVERTISING', 'AD'), ('GOOGLE', 'SOFTWARE', 'NONAD'), ('GOOGLE GSUITE', 'ADVERTISING', 'UNCLEAR'), ('GOOGLE ADS', '', 'AD'),
          ('GOOGLE WORKSPACE', '', 'NONAD'), ('GOOGLE', 'DIGITAL SERVICES', 'UNCLEAR'), ('FB/YOUTUBE/GOOGLE ADS', 'ADS', 'MIXED'), ('YOUTUBE TV', '', 'NONAD'),
          ('GOOGLE *ADS2583901760', '', 'AD'), ('GOOGLE ADS', 'SOFTWARE', 'UNCLEAR')]
    for p, pu, want in pc:
        got = gclass(p, pu); det['class %s / %s' % (p, pu)] = (got, want); ok &= got == want
    for p, want in (('WOODSPRING SUITES', False), ('TOP OF GOOGLE-YAHOO-BING', False), ('G SUITE', True), ('GOOGLE, INC.', True), ('URBAN HANG SUITE', False)):
        got = is_google(p); det['payee %s' % p] = (got, want); ok &= got == want
    for p, want in (('ADS - NOT CANDIDATE SPECIFIC', ['not candidate-specific']), ('DIGITAL ADVERTISING - NO EXPRESS ADVOC', ['no express advocacy']),
                    ('AD BUY (NON IE)', ['not an independent expenditure']), ('NONFEDERAL DIGITAL ADVERTISING', ['nonfederal']), ('DIGITAL ADVERTISING', [])):
        got = notcand_labels(p); det['purpose flag %s' % p] = (got, want); ok &= got == want
    for p, want in (('CASA IN ACTION PAC', 'CASA IN ACTION'), ('CASA IN ACTION, INC.', 'CASA IN ACTION'), ('THE PAC', None)):
        got = stem(p); det['stem %s' % p] = (got, want); ok &= got == want
    return ok, det

# ---------------------------------------------------------------- main
def main():
    args = set(sys.argv[1:])
    ok_plant, plant = selftest()
    if '--selftest' in args:
        for k, v in plant.items(): print(('OK   ' if v[0] == v[1] else 'FAIL ') + k, v)
        print('SELFTEST', 'PASSED' if ok_plant else 'FAILED'); return 0 if ok_plant else 1
    t0 = time.time(); man = fetch_all('--no-fetch' in args)
    plan_commit = subprocess.run(['git', 'log', '-1', '--format=%h %cI', '--', 'PLAN.md'], cwd=H, capture_output=True, text=True).stdout.strip()
    cm, cm_names = load_cm(); cn = load_cn(); wk, wa = load_summaries(); st, weekly, gupd, geo = load_google()

    # ---- known-good 1: Google internal check over every US advertiser
    us = [r for r in st if r['Regions'].strip() == 'US']; multi_region = [r for r in st if 'US' in [x.strip() for x in r['Regions'].split(',')] and r['Regions'].strip() != 'US']
    kg1_out = []; kg1_eq = kg1_above = kg1_below = 0
    for r in us:
        T = float(r['Spend_USD'] or 0); w = weekly.get(r['Advertiser_ID'], []); S = sum(v for _, v in w); n = len(w)
        if abs(S - T) > ROUND * n + ROUND: kg1_out.append(r['Advertiser_ID'])
        kg1_eq += S == T; kg1_above += S > T; kg1_below += S < T
    kg1_ok = len(kg1_out) <= 0.01 * len(us)
    advname = {r['Advertiser_ID']: r['Advertiser_Name'] for r in us}; advtot = {r['Advertiser_ID']: float(r['Spend_USD'] or 0) for r in us}
    advpub = {r['Advertiser_ID']: r['Public_IDs_List'] or '' for r in us}
    first_week = {a: next((s for s, v in weekly.get(a, ()) if v > 0), None) for a in advname}
    geo_top = {}
    for a in advname:
        g = geo.get(a, {}); tot = sum(g.values())
        if tot > 0:
            k, v = max(((k, v) for k, v in g.items() if k), key=lambda kv: kv[1], default=(None, 0.0)); geo_top[a] = (k, v / tot)
    statereg_names = {norm_name(r['Advertiser_Name']) for r in us if 'Registered in' in (r['Public_IDs_List'] or '')}

    # ---- matching gate (plan, Addendum 2) with name-match validity (Addendum 7: collision and geo here, first activity after the streams)
    gate = C.Counter(); gate_spend = C.defaultdict(float); adv_ids = {}; unm_forms = C.Counter(); unm_forms_spend = C.defaultdict(float); validity_drops = []
    def idform(pub):
        p = (pub or '').strip()
        if not p: return 'empty'
        kinds = {('EIN' if x.strip().startswith('EIN ID') else ('state registration' if x.strip().startswith('Registered in') else ('FEC ID' if x.strip().startswith('FEC ID') else 'other'))) for x in p.split(',')}
        return ' + '.join(sorted(kinds))
    def unmatched(a, key, form=None):
        T = advtot[a]; gate[key] += 1; gate_spend[key] += T; fm = form or idform(advpub[a]); unm_forms[fm] += 1; unm_forms_spend[fm] += T
    def home_state(cid):
        rec = cm[cid][max(cm[cid])]; cand = rec.get('cand')
        if cand:
            cr = next((cn[c][cand] for c in sorted(CYCLES, reverse=True) if cand in cn[c]), None)
            off = (cr or {}).get('off') or cand[:1]
            if off == 'P': return None
            if off in ('H', 'S'): return (cr or {}).get('ost') or cand[2:4]
        return rec.get('st') or None
    fec_any = re.compile(r'FEC ID\s+([A-Za-z0-9]+)', re.I)                   # Addendum 2: case-insensitive, candidate ids too
    principal = C.defaultdict(set)
    for cid, recs in cm.items():
        for c, rec in recs.items():
            if rec['dsgn'] == 'P' and rec['cand']: principal[rec['cand']].add(cid)
    for r in us:
        a = r['Advertiser_ID']; raw_ids = [x.upper() for x in fec_any.findall(r['Public_IDs_List'] or '')]
        if raw_ids:
            ids = []; okk = True; tier = 'id'
            for x in raw_ids:
                if re.fullmatch(r'C\d{8}', x) and x in cm: ids.append(x)
                elif re.fullmatch(r'[HSP][0-9A-Z]{8}', x) and principal.get(x): ids.extend(sorted(principal[x])); tier = 'candidate id' if tier == 'id' and not any(re.fullmatch(r'C\d{8}', y) for y in raw_ids) else tier
                else: okk = False
            if okk and ids: adv_ids[a] = (tier, list(dict.fromkeys(ids)))
            else: unmatched(a, 'unmatched_fec_id_not_in_cm', 'FEC ID not in cm')
            continue
        if 'Registered in' in (r['Public_IDs_List'] or ''): unmatched(a, 'unmatched_state_registration'); continue
        hits = cm_names.get(norm_name(r['Advertiser_Name']), set())
        if len(hits) > 1: unmatched(a, 'unmatched_ambiguous_name'); continue
        if not hits: unmatched(a, 'unmatched_no_id_no_name'); continue
        i = next(iter(hits))
        if norm_name(r['Advertiser_Name']) in statereg_names:
            unmatched(a, 'unmatched_name_collision'); validity_drops.append(dict(advertiser=a, name=advname[a], committee=i, test='collision', detail='a Google advertiser of the same name carries a state registration')); continue
        hs = home_state(i); gt = geo_top.get(a)
        if hs and gt and gt[0] and gt[1] >= GEO_SHARE and gt[0] != hs:
            unmatched(a, 'unmatched_name_geo'); validity_drops.append(dict(advertiser=a, name=advname[a], committee=i, test='geo', detail='%.0f%% of spend in %s, committee home state %s' % (100 * gt[1], gt[0], hs))); continue
        adv_ids[a] = ('name', [i])
    tentative = {m for _, ids in adv_ids.values() for m in ids}

    # ---- FEC Schedule B, pass 1: completeness, first activity, report file numbers (Addendum 6.3: amendments before any filter)
    Hh = open(os.path.join(RAW, 'fec', 'dict', 'oppexp_header_file.csv')).read().strip().split(','); ix = {k: i for i, k in enumerate(Hh)}
    I_DT, I_CM, I_AMT, I_NM, I_PU, I_MEMO, I_ENT, I_YR, I_TP, I_TR, I_FN, I_BK = (ix[k] for k in ('TRANSACTION_DT', 'CMTE_ID', 'TRANSACTION_AMT', 'NAME', 'PURPOSE', 'MEMO_CD', 'ENTITY_TP', 'RPT_YR', 'RPT_TP', 'TRAN_ID', 'FILE_NUM', 'BACK_REF_TRAN_ID'))
    months = C.Counter(); bad = C.Counter(); lines_total = 0; first_row = {}; rep_files = C.defaultdict(set)
    oppfiles = [(c, os.path.join(RAW, 'fec', str(c), 'oppexp%s.zip' % str(c)[2:])) for c in CYCLES]
    for c, path in oppfiles:
        for f in read_zip_lines(path):
            lines_total += 1
            if len(f) != 26: bad['field_count'] += 1; continue
            o = p_mdy(f[I_DT])
            if o is None: bad['bad_date'] += 1; continue
            dt = D.date.fromordinal(o); months[(dt.year, dt.month)] += 1
            cid = f[I_CM]
            if cid not in tentative: continue
            if o < first_row.get(cid, 10 ** 9): first_row[cid] = o
            rep_files[(cid, f[I_YR], f[I_TP])].add(f[I_FN])
    # ---- pass 2: rows of matched committees, amendments resolved for contested reports, then classified
    kept = []; has_b = C.defaultdict(set); item_tot = C.defaultdict(float); contested = []; n_amend = 0
    def take(cid, c, o, amt, name, purpose, memo, ent, fn, tran, back):
        if not memo: item_tot[(cid, c)] += amt                       # Addendum 4, after the amendment rule (Addendum 6.3)
        if is_google(name): kind = gclass(name, purpose)
        elif is_pool_purpose(purpose): kind = 'POOL'
        elif not memo and CARD_RX.search(up(purpose)): kind = 'CARD'
        else: return
        kept.append(dict(cid=cid, c=c, o=o, amt=amt, kind=kind, memo=memo, ent=ent, fn=fn, tran=tran, back=back,
                         payee=up(name) if kind not in ('POOL', 'CARD') else None, purpose=up(purpose) if kind not in ('POOL', 'CARD') else None))
    for c, path in oppfiles:
        for f in read_zip_lines(path):
            if len(f) != 26: continue
            cid = f[I_CM]
            if cid not in tentative: continue
            o = p_mdy(f[I_DT])
            if o is None: continue
            try: amt = float(f[I_AMT] or 0)
            except Exception: bad['bad_amount'] += 1; continue
            has_b[cid].add(c)
            args_ = (cid, c, o, amt, f[I_NM], f[I_PU], bool(f[I_MEMO].strip()), f[I_ENT], f[I_FN], f[I_TR], f[I_BK])
            if len(rep_files[(cid, f[I_YR], f[I_TP])]) > 1 and f[I_TR]: contested.append(((cid, f[I_YR], f[I_TP], f[I_TR]), args_))
            else: take(*args_)
    hi_fn = {}
    for k, a_ in contested:
        v = int(a_[8]) if a_[8].isdigit() else -1
        if v > hi_fn.get(k, -2): hi_fn[k] = v
    for k, a_ in contested:
        if (int(a_[8]) if a_[8].isdigit() else -1) == hi_fn[k]: take(*a_)
        else: n_amend += 1
    gkeys = {(r['cid'], r['fn'], r['tran']) for r in kept if r['kind'] in ('AD', 'NONAD', 'UNCLEAR', 'MIXED') and not r['memo']}
    drop_memo = [r for r in kept if r['memo'] and r['kind'] in ('AD', 'NONAD', 'UNCLEAR', 'MIXED') and (r['cid'], r['fn'], r['back']) in gkeys]
    dm = {id(r) for r in drop_memo}; kept = [r for r in kept if id(r) not in dm]

    # ---- FEC Schedule E (independent expenditure files)
    ie = []; ie_rows_total = 0; has_e = C.defaultdict(set)
    for c in CYCLES:
        for r in csv.DictReader(open(os.path.join(RAW, 'fec', str(c), 'independent_expenditure_%d.csv' % c), newline='', encoding='latin-1')):
            ie_rows_total += 1; cid = (r.get('spe_id') or '').strip()
            if cid not in tentative: continue
            o = p_ie(r.get('exp_date')) or p_ie(r.get('dissem_dt'))
            if o is None: bad['ie_bad_date'] += 1; continue
            try: amt = float(r.get('exp_amo') or 0)
            except Exception: bad['ie_bad_amount'] += 1; continue
            if o < first_row.get(cid, 10 ** 9): first_row[cid] = o
            has_e[cid].add(c); pay = up(r.get('pay')); g = is_google(pay); pur = up(r.get('pur'))
            ie.append(dict(cid=cid, c=c, o=o, amt=amt, g=g, mixed=g and bool(MIXED.search(pay)), est=bool(EST_RX.search(pur)), pur=pur, fn=r.get('file_num') or '', tran=(r.get('tran_id') or '').strip(),
                           key=(cid, o, amt, pay, r.get('cand_id') or '', r.get('sup_opp') or '')))
    # D_lo set: Google rows that are not mixed (Addendum 6.2); transaction-id rule first (Addendum 6.4), then the plan's key rule
    gl_ = [r for r in ie if r['g'] and not r['mixed']]; top_fn = {}
    for r in gl_:
        if r['tran']:
            v = int(r['fn']) if r['fn'].isdigit() else -1; k = (r['cid'], r['tran'])
            if v > top_fn.get(k, -2): top_fn[k] = v
    gl2 = [r for r in gl_ if not r['tran'] or (int(r['fn']) if r['fn'].isdigit() else -1) == top_fn[(r['cid'], r['tran'])]]
    ie_tran_drops = len(gl_) - len(gl2)
    per = C.defaultdict(C.Counter); purp = {}
    for r in gl2:
        k = r['key'] + (r['est'],); per[k][r['fn']] += 1; purp.setdefault(k, r['pur'])
    ie_dedup = []
    for k, cnt in per.items():
        for _ in range(max(cnt.values())): ie_dedup.append(dict(cid=k[0], o=k[1], amt=k[2], est=k[6], pur=purp[k]))

    # ---- name-match validity, first activity (Addendum 7)
    for a, (tier, ids) in list(adv_ids.items()):
        if tier != 'name': continue
        i = ids[0]; w = first_week.get(a); c0 = min(cm[i]); fr = first_row.get(i)
        why = None
        if w is not None and c0 >= 2022 and w + FIRST_ACTIVITY_DAYS < D.date(c0 - 1, 1, 1).toordinal(): why = 'spend from %s, committee first in the %d committee file' % (iso(w), c0)
        elif w is not None and fr is not None and fr >= FIRST_ACTIVITY_FROM and w + FIRST_ACTIVITY_DAYS < fr: why = 'spend from %s, committee first itemized row %s' % (iso(w), iso(fr))
        if why:
            del adv_ids[a]; unmatched(a, 'unmatched_name_first_activity'); validity_drops.append(dict(advertiser=a, name=advname[a], committee=i, test='first activity', detail=why))
    for a, (tier, ids) in adv_ids.items():
        key = {'id': 'A_id', 'candidate id': 'A_candidate_id', 'name': 'B_name'}[tier]; gate[key] += 1; gate_spend[key] += advtot[a]
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, (tier, ids) in adv_ids.items():
        for i in ids[1:]: parent[find(ids[0])] = find(i)
        find(ids[0])
    groups = C.defaultdict(lambda: dict(members=set(), advs=[], tiers=set()))
    for a, (tier, ids) in adv_ids.items():
        g = find(ids[0]); groups[g]['members'].update(ids); groups[g]['advs'].append(a); groups[g]['tiers'].add(tier)
    member_of = {m: g for g, v in groups.items() for m in v['members']}
    stem_advs = C.defaultdict(set)
    for a in advname:
        s_ = stem(advname[a])
        if s_: stem_advs[s_].add(a)

    # ---- 2026 cut: walk forward from April 2025, stop at the first month below 0.7 x the mean of the three before it
    seq = []; y, m = 2025, 1
    while (y, m) <= (2026, 12): seq.append((y, m)); y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    cut = None
    for i in range(3, len(seq)):
        prev = [months[seq[j]] for j in range(i - 3, i)]
        if months[seq[i]] < 0.7 * (sum(prev) / 3): cut = seq[i - 1]; break
    if cut is None: cut = seq[-1]
    cy, cmn = cut; cut_end = (D.date(cy + (cmn == 12), cmn % 12 + 1, 1) - D.timedelta(days=1)).toordinal()

    # ---- index FEC items by committee, sorted by date, for slicing by window
    by_cid_b = C.defaultdict(list); by_cid_e = C.defaultdict(list); by_cid_ed = C.defaultdict(list)
    for r in kept: by_cid_b[r['cid']].append(r)
    for r in ie: by_cid_e[r['cid']].append(r)
    for r in ie_dedup: by_cid_ed[r['cid']].append(r)
    keys = {}
    for dct in (by_cid_b, by_cid_e, by_cid_ed):
        for cid in dct: dct[cid].sort(key=lambda r: r['o'])
    def sl(dct, cid, a, b):
        lst = dct.get(cid)
        if not lst: return ()
        k = keys.get((id(dct), cid))
        if k is None: k = keys[(id(dct), cid)] = [r['o'] for r in lst]
        return lst[bisect.bisect_left(k, a):bisect.bisect_right(k, b)]
    def cvg_end(cid, c):
        if cid in wk[c] and wk[c][cid]['cvg']: return wk[c][cid]['cvg'], 'webk'
        cand = (cm.get(cid, {}).get(c) or {}).get('cand')
        if cand and cand in wa[c] and wa[c][cand]['cvg']: return wa[c][cand]['cvg'], 'weball'
        return None, None
    def summary_nonempty(cid, c):                                            # Addendum 7: an empty summary record counts as none
        cand = (cm.get(cid, {}).get(c) or {}).get('cand')
        return (cid in wk[c] and wk[c][cid]['nonempty']) or bool(cand and cand in wa[c] and wa[c][cand]['nonempty'])
    def cminfo(cid, c):
        rec = cm.get(cid, {}); return rec.get(c) or rec[max(rec)]
    def cycle_check(members, c, name_only):
        """Addendum 7 cycle guard: '' when valid, else the reason key."""
        reg = [m for m in members if c in cm.get(m, {})]
        if not reg: return 'cycle_reg'
        bad_ = 0
        for m in reg:
            rec = cm[m][c]; cand = rec.get('cand')
            if not cand or rec.get('dsgn') not in ('P', 'A'): continue
            cr = cn[c].get(cand)
            later = bool(cr and cr['status'] == 'N' and cr['yr'] and cr['yr'] > c)
            not_running = (not cr) or cr['status'] not in ('C', 'F')
            bad_ += later or (name_only and not_running)
        return 'cycle_cand' if bad_ == len(reg) else ''
    def fec_side(members, a, b, c):
        cls = {k: [0, 0.0, 0, 0.0] for k in ('AD', 'UNCLEAR', 'NONAD', 'MIXED', 'POOL')}; memo_n = 0; pool_ind = 0.0; card = 0.0; flagged = C.Counter()
        for cid in members:
            for r in sl(by_cid_b, cid, a, b):
                if r['kind'] == 'CARD':
                    if r['amt'] > 0: card += r['amt']
                    continue
                s = cls[r['kind']]
                if r['amt'] >= 0: s[0] += 1; s[1] += r['amt']
                else: s[2] += 1; s[3] += r['amt']
                memo_n += r['memo'] and r['kind'] != 'POOL'
                if r['kind'] == 'POOL' and r['ent'] == 'IND' and r['amt'] > 0: pool_ind += r['amt']
                if r['kind'] == 'AD':
                    for lab in notcand_labels(r['purpose']): flagged[lab] += r['amt']
        e_win = [r for cid in members for r in sl(by_cid_e, cid, a, b)]
        e_raw = [r for r in e_win if r['g']]; e_pool = [r for r in e_win if not r['g']]
        e_ded = [r for cid in members for r in sl(by_cid_ed, cid, a, b)]
        for r in e_ded:
            if not r['est']:
                for lab in notcand_labels(r['pur']): flagged[lab] += r['amt']
        coord = ie_tot = 0.0
        for cid in members:
            tp = (cm.get(cid, {}).get(c) or {}).get('tp', '')
            if cid in wk[c]:
                ie_tot += wk[c][cid]['ie_tot']
                if tp in ('X', 'Y'): coord += wk[c][cid]['coord']
        b_sum = lambda k: cls[k][1] + cls[k][3]
        e_pool_sum = sum(r['amt'] for r in e_pool if r['amt'] > 0)        # Addendum 3: positive items only
        e_lo = sum(r['amt'] for r in e_ded if not r['est']); e_est = sum(r['amt'] for r in e_ded if r['est'])
        d_lo = b_sum('AD') + e_lo
        d_hi = b_sum('AD') + b_sum('UNCLEAR') + b_sum('NONAD') + b_sum('MIXED') + sum(r['amt'] for r in e_raw)
        pool = cls['POOL'][1] + max(e_pool_sum, max(ie_tot, 0.0)) + max(coord, 0.0)
        flag_total = sum(r['amt'] for cid in members for r in sl(by_cid_b, cid, a, b) if r['kind'] == 'AD' and notcand_labels(r['purpose'])) + sum(r['amt'] for r in e_ded if not r['est'] and notcand_labels(r['pur']))
        return dict(d_lo=round(d_lo, 2), d_lo_est=round(d_lo + e_est, 2), d_hi=round(d_hi, 2), pool=round(pool, 2),
                    sched_b={k.lower(): dict(n_pos=v[0], sum_pos=round(v[1], 2), n_neg=v[2], sum_neg=round(v[3], 2)) for k, v in cls.items() if k != 'POOL'},
                    sched_e=dict(google_raw=round(sum(r['amt'] for r in e_raw), 2), n_raw=len(e_raw), google_dedup=round(e_lo, 2), estimates_dedup=round(e_est, 2),
                                 n_dedup=len(e_ded), mixed_raw=round(sum(r['amt'] for r in e_raw if r['mixed']), 2)),
                    pool_parts=dict(sched_b=round(cls['POOL'][1], 2), sched_b_negative_items_not_counted=round(cls['POOL'][3], 2), sched_b_n=cls['POOL'][0] + cls['POOL'][2], sched_b_paid_to_individuals=round(pool_ind, 2),
                                    sched_e_file_rows=round(e_pool_sum, 2), independent_expenditures_cycle_total=round(ie_tot, 2), party_coordinated_cycle_total=round(coord, 2)),
                    outside_pool=dict(card_or_reimbursement=round(card, 2)), purpose_text_flagged=dict(total=round(flag_total, 2), **{k: round(v, 2) for k, v in flagged.items()}),
                    google_memo_rows=memo_n)
    src_g = dict(file='google-political-ads-advertiser-weekly-spend.csv', bundle=GBUNDLE, report_data_updated_pt=gupd,
                 bundle_last_modified=man.get(os.path.join(RAW, 'google', 'google-political-ads-transparency-bundle.zip'), {}).get('last_modified'))
    def src_f(c):
        y = str(c)[2:]; m = lambda f: man.get(os.path.join(RAW, 'fec', str(c), f), {}).get('last_modified')
        return dict(sched_b='oppexp%s.zip (Last-Modified %s)' % (y, m('oppexp%s.zip' % y)), sched_e='independent_expenditure_%d.csv (Last-Modified %s)' % (c, m('independent_expenditure_%d.csv' % c)),
                    names='cm%s.zip' % y, candidates='cn%s.zip' % y, coverage='webk%s.zip, weball%s.zip' % (y, y))

    rows = []; P1, Q1 = RULERS['primary']; P2, Q2 = RULERS['second']; moved = C.Counter()
    for gid, gv in groups.items():
        members = sorted(gv['members']); weeks = C.defaultdict(float); weeks_nn = C.defaultdict(float)
        for a_ in gv['advs']:
            for s, v in weekly.get(a_, ()):
                weeks[s] += v
                if adv_ids[a_][0] != 'name': weeks_nn[s] += v
        wl = sorted(weeks.items()); wl_nn = sorted(weeks_nn.items())
        name_only = gv['tiers'] == {'name'}; has_name = 'name' in gv['tiers']
        primary = max(gv['advs'], key=lambda a_: advtot.get(a_, 0)); pid = adv_ids[primary][1][0]
        scope = any((cminfo(m, CYCLES[-1]) or {}).get('tp', '') in SCOPE_TYPES for m in members)
        stems = {s_ for s_ in [stem(advname[a_]) for a_ in gv['advs']] + [stem(cminfo(m, CYCLES[-1])['name']) for m in members] if s_}
        related = sorted({x for s_ in stems for x in stem_advs.get(s_, ()) if x not in gv['advs']})
        for c in CYCLES:
            a = D.date(c - 1, 1, 1).toordinal(); b = D.date(c, 12, 31).toordinal() if c != 2026 else cut_end
            ends = [cvg_end(m, c) for m in members]; ends_ok = [e for e, s in ends if e]
            if ends_ok: b = min(b, max(ends_ok)); cov_src = sorted({s for e, s in ends if s})
            else: cov_src = ['assumed full window']
            if b < a: b = a
            g1 = google_band(wl, a, b, P1, Q1); g2 = google_band(wl, a, b, P2, Q2)
            gn1 = google_band(wl_nn, a, b, P1, Q1) if has_name else None; gn2 = google_band(wl_nn, a, b, P2, Q2) if has_name else None
            any_b = any(c in has_b.get(m, ()) for m in members); any_e = any(c in has_e.get(m, ()) for m in members)
            summ = any(summary_nonempty(m, c) for m in members)
            fs = fec_side(members, a, b, c)
            unseen_full = 0.0; unseen = 0.0; seen_cand = set(); unseen_parts = []
            for m in members:
                rec = (cm.get(m, {}).get(c) or {}); cand = rec.get('cand'); tp = rec.get('tp', '')
                if m in wk[c]: imp = wk[c][m]['implied']; src = 'webk'
                elif cand and cand in wa[c] and cand not in seen_cand: imp = wa[c][cand]['implied']; src = 'weball'; seen_cand.add(cand)
                elif cand and cand in seen_cand: imp = 0.0; src = 'weball (counted with another member)'
                else: continue
                it = item_tot.get((m, c), 0.0); u = max(0.0, imp - it); cov = (it / imp) if imp > 0 else None
                full = tp in ('X', 'Y') or (cov is not None and cov < UNSEEN_COVERAGE)        # Addendum 5
                ue = u if full else min(u, UNITEMIZED_CAP)
                unseen_full += u; unseen += ue
                unseen_parts.append(dict(committee=m, implied=round(imp, 2), itemized=round(it, 2), coverage=(round(cov, 3) if cov is not None else None), unseen=round(u, 2), unseen_counted=round(ue, 2), rule='full' if full else 'itemization cap', source=src))
            fs['unseen'] = round(unseen, 2); fs['unseen_full'] = round(unseen_full, 2); fs['unseen_parts'] = unseen_parts
            if g1['weeks_hi'] == 0 and fs['d_hi'] == 0 and fs['sched_b']['ad']['n_pos'] == 0: continue
            cyc_bad = cycle_check(members, c, name_only)
            nothing = g1['pt'] > 0 and not (any_b or any_e or summ)                 # Addendum 7: spend stated inside the window, as the plan says
            ctx = dict(scope=scope, cycle=cyc_bad, nothing=nothing, name_only=name_only, has_name=has_name, spend_listed=g1['pt'] > 0)
            oc, why, tests = classify(g1, fs, unseen, ctx, gn1)
            oc2, why2, _ = classify(g2, fs, unseen, ctx, gn2)
            ocf, whyf, _ = classify(g1, fs, unseen_full, ctx, gn1)    # Addendum 5 sensitivity
            o_plan = core(g1['lo'], g1['hi'], fs['d_lo_est'], fs['d_hi'], fs['pool'], unseen) if not scope else None
            if o_plan and oc != o_plan: moved['%s to %s (%s)' % (o_plan, oc, why.split(':')[0])] += 1
            flags = []
            if oc == BELOW and fs['outside_pool']['card_or_reimbursement'] > tests['below_margin'] - tests['below_size']: flags.append('card payments or reimbursements could close the gap')
            rel_sp = 0.0; rel_list = []
            if related:
                for x in related:
                    sp_ = sum(v for s_, v in weekly.get(x, ()) if s_ + 6 + Q1 >= a and s_ - P1 <= b)
                    if sp_ > 0: rel_sp += sp_; rel_list.append(dict(id=x, name=advname[x], possible_window_spend=round(sp_, 2), matched_to=member_of_name(x, adv_ids)))
            if oc == ABOVE:
                if fs['d_lo'] - fs['purpose_text_flagged']['total'] - g1['hi'] < tests['above_size']:
                    labs = [k for k in ('not candidate-specific', 'no express advocacy', 'not an independent expenditure', 'nonfederal') if fs['purpose_text_flagged'].get(k)]
                    flags.append('purpose text: ' + ' and '.join(labs))
                if rel_sp > 0: flags.append('a related advertiser states spend in the window')
            win_sp = {a_: sum(v for s_, v in weekly.get(a_, ()) if a <= s_ <= b) for a_ in gv['advs']}
            top_a = max(gv['advs'], key=lambda a_: (win_sp[a_], advtot.get(a_, 0)))
            pid_c = adv_ids[top_a][1][0] if win_sp[top_a] > 0 else pid
            info = cminfo(pid_c, c)
            row = dict(level='cycle', cycle=c, quarter=None, window=[iso(a), iso(b)], coverage_source=cov_src, group_key='+'.join(members),
                       committee_id=pid_c, committee_name=info['name'], committee_type=info['tp'], designation=info['dsgn'], party_field=info['party'],
                       members=members, n_members=len(members), tier='+'.join(sorted(gv['tiers'])),
                       advertisers=[dict(id=a_, name=advname[a_], tier=adv_ids[a_][0], stated_in_window=round(win_sp[a_], 2)) for a_ in sorted(gv['advs'], key=lambda a_: (-win_sp[a_], -advtot.get(a_, 0)))[:6]], n_advertisers=len(gv['advs']),
                       related_advertisers=rel_list,
                       google=dict(stated_in_window=round(g1['pt'], 2), lo=round(g1['lo'], 2), hi=round(g1['hi'], 2), weeks_certain=g1['weeks_lo'], weeks_possible=g1['weeks_hi'],
                                   second_ruler=dict(lo=round(g2['lo'], 2), hi=round(g2['hi'], 2)), without_name_matched=(dict(lo=round(gn1['lo'], 2), hi=round(gn1['hi'], 2)) if gn1 else None), source=src_g),
                       fec=dict(fs, source=src_f(c)),
                       gap=dict(d_lo_minus_google_stated=round(fs['d_lo'] - g1['pt'], 2), ratio_d_lo_to_google_stated=(round(fs['d_lo'] / g1['pt'], 3) if g1['pt'] > 0 else None), **tests),
                       interval='Google side: spend that must (lo) or could (hi) have been paid in the window, payments allowed %d days before to %d days after each ad week, 100 dollars either way per listed week. It is a bound, not a confidence interval. FEC side: ad rows to Google, without amounts marked as estimates (lo), to every Google row (hi). The BELOW test adds payments to others for ad, digital or media purposes (pool) and summary disbursements the itemized file does not hold (unseen). CONSISTENT needs every Google row plus unseen inside the band.' % (P1, Q1),
                       outcome=oc, reason=why, flags=flags, outcome_second_ruler=oc2, timing_sensitive=oc != oc2, outcome_unseen_full=ocf, unseen_rule_sensitive=oc != ocf,
                       tp=dict(none='plan %s, dated addenda; match tier %s; gate counts and validity drops in the summary' % (plan_commit, '+'.join(sorted(gv['tiers']))),
                               gap_items='Schedule B Google rows by class with positive and negative counts in fec.sched_b; Schedule E raw %d, deduplicated %d' % (fs['sched_e']['n_raw'], fs['sched_e']['n_dedup']),
                               sign=('+' if fs['d_lo'] > g1['pt'] else ('-' if fs['d_lo'] < g1['pt'] else '0')) + ' (ad payments minus stated spend in the window, signed)',
                               ruler='interval as stated in the interval field; second ruler P=%d Q=%d gives %s' % (P2, Q2, oc2),
                               both_alternatives='ABOVE test margin %.0f against size %.0f; BELOW test margin %.0f against size %.0f' % (tests['above_margin'], tests['above_size'], tests['below_margin'], tests['below_size']),
                               record='Google %s (data updated %s PT); FEC %s' % (src_g['file'], gupd, src_f(c)['sched_b'])))
            rows.append(row)
            for qn, qa, qb, _, _ in qstarts(a, b):
                q1 = google_band(wl, qa, qb, P1, Q1); fq = fec_side(members, qa, qb, c)
                if q1['pt'] == 0 and fq['d_hi'] == 0 and fq['sched_b']['ad']['n_pos'] == 0: continue
                qn1 = google_band(wl_nn, qa, qb, P1, Q1) if has_name else None
                qctx = dict(ctx, spend_listed=q1['possible_spend'] > 0)
                qo, qw, qt = classify(q1, fq, unseen, qctx, qn1)
                rows.append(dict(level='quarter', cycle=c, quarter=qn, window=[iso(qa), iso(qb)], group_key='+'.join(members), committee_id=pid_c, committee_name=info['name'], n_members=len(members), tier=row['tier'],
                                 google=dict(stated_in_window=round(q1['pt'], 2), lo=round(q1['lo'], 2), hi=round(q1['hi'], 2)),
                                 fec=dict(d_lo=fq['d_lo'], d_lo_est=fq['d_lo_est'], d_hi=fq['d_hi'], pool=fq['pool'], sched_e_google_raw=fq['sched_e']['google_raw']),
                                 gap=dict(d_lo_minus_google_stated=round(fq['d_lo'] - q1['pt'], 2), **qt), outcome=qo, reason=qw))

    # ---- gates that turn every outcome into CANNOT_TELL
    bad_share = bad['field_count'] / max(1, lines_total)
    gate_ok = ok_plant and kg1_ok and bad_share <= 0.001
    if not gate_ok:
        for r in rows: r['outcome_before_gate'] = r['outcome']; r['outcome'] = CANNOT_TELL; r['reason'] = 'known-good gate failed'
    cyc = [r for r in rows if r['level'] == 'cycle']; qtr = [r for r in rows if r['level'] == 'quarter']
    def counts(rs):
        out = C.Counter(r['outcome'] for r in rs); return {k: out.get(k, 0) for k in (ABOVE, BELOW, CONSISTENT, CANNOT_TELL, NOTHING)}
    reasons = C.Counter((r['outcome'], r['reason'].split(':')[0] if r['outcome'] == CANNOT_TELL else '') for r in cyc)
    dec_ = [r for r in cyc if r['outcome'] in (ABOVE, BELOW, CONSISTENT)]
    flagc = C.Counter(fl.split(':')[0] for r in cyc for fl in r['flags'])
    summary = dict(
        updated=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), plan_commit=plan_commit, gate_ok=gate_ok,
        known_good=dict(planted_rows='passed' if ok_plant else 'FAILED', planted_detail={k: list(v) for k, v in plant.items()},
                        google_internal=dict(us_advertisers=len(us), outside_band=len(kg1_out), weekly_sum_equal_total=kg1_eq, weekly_sum_above_total=kg1_above, weekly_sum_below_total=kg1_below, ok=kg1_ok),
                        parser=dict(oppexp_lines=lines_total, dropped=dict(bad), dropped_share=round(bad_share, 6))),
        google=dict(report_data_updated_pt=gupd, us_advertisers=len(us), us_stated_spend=round(sum(advtot.values()), 2), advertisers_in_more_than_one_region_with_us=len(multi_region)),
        match_gate=dict(counts=dict(gate), stated_spend=dict((k, round(v, 2)) for k, v in gate_spend.items()), groups=len(groups),
                        unmatched_public_id_forms=dict(unm_forms), unmatched_public_id_forms_spend=dict((k, round(v, 2)) for k, v in unm_forms_spend.items()),
                        name_validity_drops=dict(C.Counter(v['test'] for v in validity_drops)), name_validity_drop_list=validity_drops,
                        groups_with_more_than_one_committee=sum(1 for g in groups.values() if len(g['members']) > 1),
                        largest_group_members=max((len(g['members']) for g in groups.values()), default=0)),
        fec=dict(sched_b_rows_kept_google=sum(1 for r in kept if r['kind'] not in ('POOL', 'CARD')), sched_b_rows_kept_pool=sum(1 for r in kept if r['kind'] == 'POOL'),
                 sched_b_rows_kept_card_or_reimbursement=sum(1 for r in kept if r['kind'] == 'CARD'),
                 amendment_duplicates_dropped=n_amend, memo_rows_with_google_parent_dropped=len(drop_memo), ie_rows_total=ie_rows_total, ie_rows_matched=len(ie),
                 ie_google_rows_raw=sum(1 for r in ie if r['g']), ie_google_rows_mixed=sum(1 for r in ie if r['mixed']), ie_google_rows_estimates=sum(1 for r in ie if r['g'] and r['est']),
                 ie_transaction_id_drops=ie_tran_drops, ie_google_rows_dedup=len(ie_dedup),
                 cut_2026=dict(last_complete_month='%d-%02d' % cut, window_end=iso(cut_end), month_rows={'%d-%02d' % k: months[k] for k in seq if months[k]})),
        rulers=dict(primary=dict(P=P1, Q=Q1), second=dict(P=P2, Q=Q2), size_that_matters='at least %d dollars and at least %d percent of the Google bound' % (SIZE_ABS, SIZE_REL * 100), band_factor=BAND_FACTOR,
                    unitemized_cap=UNITEMIZED_CAP, unseen_coverage=UNSEEN_COVERAGE, geo_share=round(GEO_SHARE, 4), first_activity_days=FIRST_ACTIVITY_DAYS),
        outcomes=dict(cycle_rows=dict(all=counts(cyc), **{str(c): counts([r for r in cyc if r['cycle'] == c]) for c in CYCLES}),
                      cycle_rows_by_tier={t: counts([r for r in cyc if r['tier'] == t]) for t in sorted({r['tier'] for r in cyc})},
                      quarter_rows=counts(qtr), timing_sensitive_cycle_rows=sum(1 for r in cyc if r['timing_sensitive']),
                      unseen_rule_sensitive_cycle_rows=sum(1 for r in cyc if r['unseen_rule_sensitive']),
                      unseen_full_cycle_rows=dict(C.Counter(r['outcome_unseen_full'] for r in cyc)),
                      second_ruler_cycle_rows=dict(C.Counter(r['outcome_second_ruler'] for r in cyc)),
                      cannot_tell_reasons_cycle={k[1]: v for k, v in reasons.items() if k[0] == CANNOT_TELL},
                      addendum7_moves_cycle=dict(moved), flags_cycle=dict(flagc),
                      decided_cycle_rows=dict(n=len(dec_), timing_sensitive=sum(r['timing_sensitive'] for r in dec_), unseen_rule_sensitive=sum(r['unseen_rule_sensitive'] for r in dec_),
                                              name_only=sum(r['tier'] == 'name' for r in dec_), flagged=sum(1 for r in dec_ if r['flags']),
                                              robust_id_no_flags=sum(1 for r in dec_ if not r['timing_sensitive'] and not r['unseen_rule_sensitive'] and 'name' not in r['tier'] and not r['flags']),
                                              above_with_google_zero_in_window=sum(1 for r in dec_ if r['outcome'] == ABOVE and r['google']['stated_in_window'] == 0))),
        totals=dict(cycle_rows=len(cyc), quarter_rows=len(qtr), committees_matched=len(member_of)),
        runtime_s=round(time.time() - t0, 1))
    json.dump(dict(summary=summary, rows=rows), open(os.path.join(H, 'data', 'adspend.json'), 'w'), separators=(',', ':'))
    json.dump(public_file(summary, cyc), open(os.path.join(H, 'data', 'adspend_public.json'), 'w'), separators=(',', ':'))
    json.dump(summary, open(os.path.join(H, 'summary_adspend.json'), 'w'), indent=1)
    open(os.path.join(H, 'section_adspend.html'), 'w').write(render(summary, cyc))
    print('adspend: %d cycle rows, %d quarter rows, gate %s, outcomes %s, %.0f s' % (len(cyc), len(qtr), 'ok' if gate_ok else 'FAILED', summary['outcomes']['cycle_rows']['all'], time.time() - t0))
    return 0

def member_of_name(adv, adv_ids):
    t = adv_ids.get(adv); return ('+'.join(t[1]) if t else None)

# ---------------------------------------------------------------- the slim public file (cycle rows only)
def public_file(s, cyc):
    def row(r):
        f = r['fec']; b = f['sched_b']; tot = lambda k: round(b[k]['sum_pos'] + b[k]['sum_neg'], 2)
        out = dict(committee_id=r['committee_id'], committee_name=r['committee_name'], committee_type=r['committee_type'], designation=r['designation'], party_field=r['party_field'],
                   cycle=r['cycle'], window=r['window'], match=r['tier'], advertisers=[dict(id=a['id'], name=a['name'], match=a['tier'], stated_in_window=a['stated_in_window']) for a in r['advertisers'][:3]],
                   google=dict(stated_in_window=r['google']['stated_in_window'], band=[r['google']['lo'], r['google']['hi']], second_band=[r['google']['second_ruler']['lo'], r['google']['second_ruler']['hi']]),
                   fec=dict(ad_rows_to_google=f['d_lo'], all_rows_to_google=f['d_hi'], estimates_to_google=round(f['d_lo_est'] - f['d_lo'], 2), paid_to_others_for_ads_digital_media=f['pool'],
                            unseen_counted=f['unseen'], unseen_full=f['unseen_full'], schedule_b=dict(ad=tot('ad'), unclear=tot('unclear'), nonad=tot('nonad'), mixed=tot('mixed')),
                            schedule_e=dict(google_raw=f['sched_e']['google_raw'], google_deduplicated=f['sched_e']['google_dedup'], estimates=f['sched_e']['estimates_dedup'])),
                   outcome=r['outcome'], reason=r['reason'], flags=r['flags'], outcome_second_band=r['outcome_second_ruler'], outcome_unseen_full=r['outcome_unseen_full'])
        if r['n_members'] > 1: out['members'] = r['members']
        if r.get('related_advertisers'): out['related_advertisers'] = r['related_advertisers']
        return out
    by_cycle = {}
    for r in cyc: by_cycle.setdefault(str(r['cycle']), dict(google=r['google']['source']['file'], **r['fec']['source']))
    about = dict(name='ADSPEND: Google political ad spend against FEC filings', publisher='Heuremen LLC', updated=s['updated'],
                 google_data_updated_pt=s['google']['report_data_updated_pt'], plan=PLAN_URL, plan_commit=s['plan_commit'],
                 interval=('Band: the Google spend that must have been paid inside the window to the spend that could have been, allowing payments %d days before to %d days after each ad week, '
                           'and 100 dollars either way per listed week for Google\'s rounding. It is a bound, not a confidence interval. Second band: %d and %d days.') % (s['rulers']['primary']['P'], s['rulers']['primary']['Q'], s['rulers']['second']['P'], s['rulers']['second']['Q']),
                 outcomes='ABOVE, BELOW, CONSISTENT, CANNOT_TELL with a reason, NOTHING_RETURNED. Definitions on the page and in the plan.',
                 sources=dict(google=GBUNDLE, fec='https://www.fec.gov/data/browse-data/?tab=bulk-data', files_by_cycle=by_cycle), rows=len(cyc),
                 note='Committee disbursements only. No individual contributor file was read. Party appears only as the filed field.')
    return dict(about=about, rows=[row(r) for r in sorted(cyc, key=lambda r: (r['cycle'], -r['google']['stated_in_window']))])

# ---------------------------------------------------------------- the public fragment (plain HTML, launch.html classes, no scripts)
def money(x):
    return '$' + format(int(round(x)), ',') if x >= 0 else '&minus;$' + format(int(round(-x)), ',')
def esc(s): return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
OUT_WORD = {ABOVE: 'Above', BELOW: 'Below', CONSISTENT: 'Consistent', CANNOT_TELL: 'Cannot tell', NOTHING: 'Nothing returned'}
def pdate(isod):
    d = D.date.fromisoformat(isod); return '%d %s %d' % (d.day, d.strftime('%B'), d.year)
def cell_name(r):
    out = esc(r['committee_name']) + ' <span class="by">' + esc(r['committee_id']) + '</span>'
    if r['n_members'] > 1:
        k = r['n_members'] - 1; out += ' <span class="by">and %d related committee%s joined with it through Google&rsquo;s file</span>' % (k, '' if k == 1 else 's')
    top = r['advertisers'][0]['name'] if r.get('advertisers') else ''
    if top and norm_name(top) != norm_name(r['committee_name']): out += ' <span class="by">Google advertiser: %s</span>' % esc(top)
    if r['tier'] == 'name': out += ' <span class="by">matched by name</span>'
    return out
def cell_outcome(r):
    out = OUT_WORD[r['outcome']]
    if r['outcome'] == CANNOT_TELL: out += ' <span class="by">%s</span>' % esc(r['reason'].split(':')[0])
    dep = []
    if r.get('timing_sensitive'): dep.append('depends on timing')
    if r.get('unseen_rule_sensitive'): dep.append('depends on the itemization rule')
    if dep: out += ' <span class="by">%s</span>' % esc(', '.join(dep))
    for fl in r.get('flags', []): out += ' <span class="by">%s</span>' % esc(fl)
    return out
def trow(r):
    return '<tr><td>%s</td><td>%d</td><td class="n">%s</td><td class="n">%s to %s</td><td class="n">%s to %s</td><td class="n">%s</td><td>%s</td></tr>' % (
        cell_name(r), r['cycle'], money(r['google']['stated_in_window']), money(r['google']['lo']), money(r['google']['hi']),
        money(r['fec']['d_lo']), money(r['fec']['d_hi']), money(r['fec']['pool']), cell_outcome(r))
THEAD = '<thead><tr><th>Committee as filed</th><th>Cycle</th><th>Google stated spend in the window</th><th>Band for payments in the window</th><th>Reported paid to Google: ad rows to all rows</th><th>Paid to others for ads, digital or media</th><th>Outcome</th></tr></thead>'
def render(s, cyc):
    oc = s['outcomes']['cycle_rows']; mg = s['match_gate']; cut = pdate(s['fec']['cut_2026']['window_end'])
    def line(c):
        k = oc[str(c)]
        return '<tr><td>%d</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            c, format(k[ABOVE], ','), format(k[BELOW], ','), format(k[CONSISTENT], ','), format(k[CANNOT_TELL], ','), format(k[NOTHING], ','))
    big = []
    for c in (2024, 2026):
        big += sorted([r for r in cyc if r['cycle'] == c], key=lambda r: -r['google']['stated_in_window'])[:10]
    dec = []
    for o in (CONSISTENT, ABOVE, BELOW):
        dec += sorted([r for r in cyc if r['outcome'] == o], key=lambda r: -max(r['google']['stated_in_window'], r['fec']['d_lo']))[:6]
    cA, cB = mg['counts'].get('A_id', 0) + mg['counts'].get('A_candidate_id', 0), mg['counts'].get('B_name', 0)
    unm = sum(v for k, v in mg['counts'].items() if k.startswith('unmatched')); unm_sp = sum(v for k, v in mg['stated_spend'].items() if k.startswith('unmatched'))
    fm = mg['unmatched_public_id_forms']; ein_state = fm.get('EIN', 0) + fm.get('state registration', 0); empty = fm.get('empty', 0)
    vd = mg.get('name_validity_drops', {}); nvd = sum(vd.values())
    RW = dict(band='a timing band wider than a factor of two', agency='purchases through others that could close the gap', purpose='Google rows of unclear purpose that decide the side',
              scope='a filer type that reports no operating expenditures', unseen='money the itemized file does not hold', near='a gap under the size that matters',
              cycle='a committee not registered, or its candidate not running, in that cycle', name='a reading that would rest on a name match alone',
              **{'no Google spend': 'no Google spend listed in the window', 'estimates': 'amounts the filer marked as estimates'})
    rs = sorted(s['outcomes']['cannot_tell_reasons_cycle'].items(), key=lambda kv: -kv[1])
    why_line = ('Most rows read Cannot tell. The commonest reasons are %s (%s rows) and %s (%s rows).' % (RW.get(rs[0][0], rs[0][0]), format(rs[0][1], ','), RW.get(rs[1][0], rs[1][0]), format(rs[1][1], ','))) if len(rs) > 1 else ''
    return f"""<section id="adspend">
<h2>Political ad spend: Google&rsquo;s library against campaign filings</h2>
<p>Google states how much each verified election advertiser spent on election ads, week by week. Federal political committees report their payments to the FEC, itemized by payee once a payee&rsquo;s total passes 200 dollars in a year, or in an election cycle for a candidate&rsquo;s committee. We set the two side by side, per two-year cycle, for every committee we can match.</p>
<p>Of the {s['google']['us_advertisers']:,} US advertisers in Google&rsquo;s file, {cA + cB:,} matched an FEC committee: {cA:,} through the FEC committee or candidate ID that Google lists for them and {cB:,} through a name that equals exactly one committee&rsquo;s name and passes the match checks. The other {unm:,} did not match and carry {money(unm_sp)} of Google&rsquo;s stated spend. Of those, {ein_state:,} list only a tax ID or a state registration and {empty:,} list no ID. They include {nvd:,} name matches we set aside because Google lists the same name under a state registration, because at least two thirds of the advertiser&rsquo;s spend sits in a state other than the committee&rsquo;s, or because the spend began more than 90 days before the committee&rsquo;s first itemized filing.</p>
<h3>Outcomes by cycle</h3>
<div class="scroll"><table class="mtx small"><thead><tr><th>Cycle</th><th>Above</th><th>Below</th><th>Consistent</th><th>Cannot tell</th><th>Nothing returned</th></tr></thead><tbody>
{''.join(line(c) for c in (2020, 2022, 2024, 2026))}
</tbody></table></div>
<p class="bench-note">One row per matched committee, or group of committees that Google&rsquo;s file joins, and cycle. The 2026 cycle runs to {cut}, the end of the last full month in the FEC&rsquo;s itemized file on the day we read it. {why_line} Nothing returned: Google states spend in the window and the FEC files hold no row and no summary for the committee in that cycle.</p>
<h3>Matched committees with the most Google stated spend, 2024 and 2026</h3>
<div class="scroll"><table class="mtx">{THEAD}<tbody>
{''.join(trow(r) for r in big)}
</tbody></table></div>
<h3>Rows that read Consistent, Above or Below, with the most Google stated spend or ad payments, across all cycles</h3>
<div class="scroll"><table class="mtx">{THEAD}<tbody>
{''.join(trow(r) for r in dec)}
</tbody></table></div>
<p class="bench-note">Band: the spend that must have been paid inside the window to the spend that could have been, allowing payments {s['rulers']['primary']['P']} days before to {s['rulers']['primary']['Q']} days after each ad week and 100 dollars either way per week for Google&rsquo;s rounding to whole hundreds. It is a bound, not a confidence interval. Ad rows leave out amounts that a filer marked as estimates in 24- or 48-hour reports. All rows count them. Above: ad payments to Google exceed the top of the band by at least 1,000 dollars and 10 percent, and Google lists spend in the window. Below: every payment to Google, every payment to others for ads, digital or media, and any money in the committee&rsquo;s own summary that the itemized file does not hold, all together, fall short of the bottom of the band by that much, and the gap does not rest on a name match alone. Consistent: ad payments to Google reach the bottom of the band, every payment to Google plus that unseen money stays under its top, and the band spans no more than a factor of two. Unseen money counts in full for party committees and for committees whose itemized file holds less than nine tenths of their own operating disbursements. Otherwise it counts up to 400 dollars, the most the itemization rule can leave unitemized for one payee over two years (200 dollars a calendar year, or 200 dollars an election cycle for a candidate&rsquo;s committee). That rule and its threshold were defined after the data, and rows whose outcome depends on it say so. Cannot tell: anything else. Agency means payments to others for ads, digital or media could close the gap. Band means the timing band spans more than a factor of two. Purpose means rows of unclear purpose decide the side. Unseen means money that the itemized file does not hold could decide it. Near means the gap is under the size that matters. Scope means the filer type reports no operating expenditures. Cycle means the committee is not registered in that cycle, or its candidate was not a candidate then. Name means the reading would rest on an advertiser matched by name alone. No Google spend means Google lists no election-ad spend for the advertiser in the window. Estimates means the reading rests on amounts the filer marked as estimates. Depends on timing means a wider band of {s['rulers']['second']['P']} days before and {s['rulers']['second']['Q']} days after gives another outcome. Other notes on a row keep its outcome and say what could move it. Google figures are from its weekly spend file. FEC figures are from Schedule B operating expenditures, the independent expenditure file and the summary files.</p>
<h3>How we read it</h3>
<p>The two filings count different things, so a gap is a measured difference between two filings and we name no cause for it. Google&rsquo;s library holds only ads that Google classes as election ads, and it counts them for the advertiser whoever paid. A committee that buys through an agency reports a payment to the agency, not to Google, so its direct payments to Google can only fall short. Those rows read Cannot tell unless the committee&rsquo;s payments to others for ads, digital or media cannot close the gap either. Card payments, reimbursements and consulting fees are not counted in that pool. Ads paid from accounts that do not report to the FEC appear only on Google&rsquo;s side. Ads that Google does not class as election ads, ads that run under another advertiser&rsquo;s account and refunds a committee receives from Google appear only on the FEC side, so a committee&rsquo;s payments can exceed Google&rsquo;s figure. Other Google products, such as email and office software, appear only on the FEC side and count only in the all-rows figure. Committee names are as each cycle&rsquo;s committee file holds them on the day we read it, and some committees have changed names since their ads ran. The plan, its sizes and its bands were written before we compared any committee. Later addenda are dated in the plan, and the ones on unseen money, match checks, Nothing returned and estimates were defined after the data. Party appears only as the filed field in the data and plays no part in any reading.</p>
<p class="meta">Rows, one per committee and cycle, with every figure and its source file: <a href="{PUBLIC_DATA_URL}">adspend.json</a> &middot; Plan with its dated addenda, and code: <a href="{PLAN_URL}">adspend</a></p>
<p class="meta">Named here and want to answer a row? <a href="/respond?u=adspend-all">Respond</a></p>
<p class="meta">Data read from: <a href="{GBUNDLE}">Google political ads transparency bundle</a> (advertiser, weekly and state spend files, data updated {esc(s['google']['report_data_updated_pt'])} Pacific time) &middot; <a href="https://adstransparency.google.com/political">Political advertising on Google</a> &middot; <a href="https://www.fec.gov/data/browse-data/?tab=bulk-data">FEC bulk data</a>, cycles 2020 to 2026: <a href="https://www.fec.gov/campaign-finance-data/operating-expenditures-file-description/">operating expenditures</a>, <a href="https://www.fec.gov/campaign-finance-data/independent-expenditures-file-description/">independent expenditures</a>, <a href="https://www.fec.gov/campaign-finance-data/committee-master-file-description/">committee master</a>, candidate master, PAC and party summary, candidate summary. Itemization rule: <a href="https://www.ecfr.gov/current/title-11/chapter-I/subchapter-A/part-104/section-104.3">11 CFR 104.3</a>. We read committee disbursements only and never individual contributor files.</p>
</section>
"""

if __name__ == '__main__': sys.exit(main())
