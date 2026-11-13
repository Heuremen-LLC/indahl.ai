#!/usr/bin/env python3
"""solar_tick.py: SOLAR rider (see PLAN.md). Rerunnable. Installs no timer. Reads public sources with no key, one request at a time, paced:
the SWPC Warehouse and indices on ftp.swpc.noaa.gov (RSGA as originally published, Edited Solar Events, DGD, DSD, SPE.txt), the current SWPC
text products on services.swpc.noaa.gov (stored as dated copies), and the GFZ Potsdam Kp file. Sets each stated chance beside what happened.
Writes data/solar.json (every row), summary_solar.json, data/solar_live.json, data/snapshots/*.txt.gz and data/solar_history.jsonl.
--offline: files on disk only. --publish: also put data/solar_live.json in the site KV as solar_live, served at /solar/live.json. --selftest: rule checks only."""
import os, sys, json, time, math, re, gzip, glob, hashlib, tarfile, random, calendar, subprocess, urllib.request, collections as C, datetime as DT
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
UA = 'heuremen-solar/0.1 (+https://indahl.ai/solar)'
FTP = 'ftp://ftp.swpc.noaa.gov/pub'; SVC = 'https://services.swpc.noaa.gov/text/'
GFZ = 'https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt'
FIRST_ISSUE = DT.date(2021, 1, 1); SETTLE_DAYS = 3; MIN_N = 30; MIN_EVENTS = 5; BLOCK = 27; REPS = 2000; SEED = 27
BINS = ((0, 2), (3, 7), (8, 17), (18, 27), (28, 42), (43, 57), (58, 72), (73, 87), (88, 100))
EVENTS = (('M', 'M-class flare', 'Class M, one or more flares of M1.0 or more'), ('X', 'X-class flare', 'Class X, one or more flares of X1.0 or more'),
          ('P', 'Proton event', 'Proton, a proton event starts that day (10 pfu at more than 10 MeV)'),
          ('MID5', 'Middle latitude storm, K 5 or more', 'Minor storm plus major-severe storm, middle latitudes, our reading, Fredericksburg'),
          ('MID6', 'Middle latitude major or severe storm', 'Major-severe storm, middle latitudes, Fredericksburg'),
          ('HI5', 'High latitude storm, K 5 or more', 'Minor storm plus major-severe storm, high latitudes, our reading, College'),
          ('HI6', 'High latitude major or severe storm', 'Major-severe storm, high latitudes, College'))
PACE = 1.0; SNAP_HOURS = 6
for d in ('data', 'data/raw', 'data/raw/warehouse', 'data/raw/indices', 'data/raw/gfz', 'data/snapshots'): os.makedirs(d, exist_ok=True)
NOW = time.time(); TODAY = DT.datetime.fromtimestamp(NOW, DT.timezone.utc).date(); STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW))
MON = {m: i for i, m in enumerate(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'), 1)}
def log(*a): print('solar:', *a, file=sys.stderr)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=180):
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 403, 404): break
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:120], err))
def save(path, b):
    open(path + '.tmp', 'wb').write(b); os.replace(path + '.tmp', path)
def ftp_list(path):
    """[(name, size, 'Mon DD HH:MM' or 'Mon DD YYYY')] of an FTP directory."""
    out = []
    for l in get(FTP + path + '/').decode('latin-1').splitlines():
        p = l.split()
        if len(p) >= 9: out.append((p[8], int(p[4]), ' '.join(p[5:8])))
    return out
def ftp_date(s):
    """FTP listing date to a date. 'Nov 13  2025' has a year, 'Nov 10 12:30' is within the last six months."""
    m, d, y = s.split()
    if ':' in y:
        y = TODAY.year; dd = DT.date(y, MON[m], int(d))
        return dd if dd <= TODAY + DT.timedelta(1) else DT.date(y - 1, MON[m], int(d))
    return DT.date(int(y), MON[m], int(d))

# ---------------- 1. fetch ----------------
SPE_CHANGED = None
if not OFF:
    W = 'data/raw/warehouse'
    for y in range(FIRST_ISSUE.year, TODAY.year):
        for p in ('RSGA', 'events'):
            f = '%s/%d_%s.tar.gz' % (W, y, p)
            if not os.path.exists(f):
                try: save(f, get('%s/warehouse/%d/%d_%s.tar.gz' % (FTP, y, y, p)))
                except Exception as e: log(repr(e)[:120]); STALE.append('%d_%s' % (y, p))
        for p in ('DGD', 'DSD'):
            f = '%s/%d_%s.txt' % (W, y, p)
            if not os.path.exists(f):
                try: save(f, get('%s/warehouse/%d/%d_%s.txt' % (FTP, y, y, p)))
                except Exception as e: log(repr(e)[:120]); STALE.append('%d_%s' % (y, p))
    y = TODAY.year
    for p, sub in (('RSGA', '%d/RSGA' % y), ('events', '%d/%d_events' % (y, y))):
        d = '%s/%d_%s' % (W, y, p); os.makedirs(d, exist_ok=True)
        try: L = ftp_list('/warehouse/' + sub)
        except Exception as e: L = []; log(repr(e)[:120]); STALE.append(sub)
        for name, size, _ in L:
            if not name.endswith('.txt'): continue
            f = os.path.join(d, name)
            # RSGA: kept as first fetched, never replaced (as originally published). Events: refetched while their size changes (edited lists settle).
            if os.path.exists(f) and (p == 'RSGA' or os.path.getsize(f) == size): continue
            try: save(f, get('%s/warehouse/%s/%s' % (FTP, sub, name)))
            except Exception as e: log(repr(e)[:120]); STALE.append(name)
    for q in range(1, 5):
        for p in ('DGD', 'DSD'):
            name = '%dQ%d_%s.txt' % (y, q, p)
            try: save('data/raw/indices/' + name, get('%s/indices/old_indices/%s' % (FTP, name)))
            except Exception as e:
                if not os.path.exists('data/raw/indices/' + name): log(repr(e)[:80])
    try:
        L = {n: dt for n, s, dt in ftp_list('/indices')}
        SPE_CHANGED = ftp_date(L['SPE.txt']).isoformat(); save('data/raw/SPE.txt', get(FTP + '/indices/SPE.txt'))
        json.dump(dict(changed=SPE_CHANGED, read=STAMP), open('data/raw/SPE_listing.json', 'w'))
    except Exception as e: log(repr(e)[:120]); STALE.append('SPE')
    try: save('data/raw/gfz/Kp_ap_Ap_SN_F107_since_1932.txt', get(GFZ))
    except Exception as e: log(repr(e)[:120]); STALE.append('GFZ')
    # our own dated copies of the current products (stated side kept even if a later copy changes; 3-day products stored for a later plan)
    last = max((os.path.getmtime(f) for f in glob.glob('data/snapshots/*.txt.gz')), default=0)
    if NOW - last >= SNAP_HOURS * 3600:
        for name in ('sgarf.txt', '3-day-forecast.txt', '3-day-geomag-forecast.txt'):
            try: b = get(SVC + name); gzip.open('data/snapshots/%s_%s.gz' % (STAMP, name), 'wb').write(b)
            except Exception as e: log(repr(e)[:120]); STALE.append(name)
if SPE_CHANGED is None and os.path.exists('data/raw/SPE_listing.json'): SPE_CHANGED = json.load(open('data/raw/SPE_listing.json'))['changed']

# ---------------- 2. stated side: RSGA ----------------
def rsga_texts():
    """(source, text) for every RSGA on disk: Warehouse tar files, Warehouse day files, our own copies of sgarf.txt."""
    for f in sorted(glob.glob('data/raw/warehouse/*_RSGA.tar.gz')):
        with tarfile.open(f) as t:
            for m in t.getmembers():
                if m.isfile() and m.name.endswith('RSGA.txt'): yield 'warehouse:' + m.name, t.extractfile(m).read().decode('latin-1')   # every RSGA file, so an amendment (2024onRSGA.txt) is read and refused by name
    for f in sorted(glob.glob('data/raw/warehouse/*_RSGA/*RSGA.txt')): yield 'warehouse:' + os.path.basename(f), open(f, encoding='latin-1').read()
    for f in sorted(glob.glob('data/snapshots/*_sgarf.txt.gz')): yield 'own:' + os.path.basename(f), gzip.open(f).read().decode('latin-1')
def triple(text, label):
    m = re.search(r'^\s*' + label + r'\s+(\d{1,3})/(\d{1,3})/(\d{1,3})\s*$', text, re.M | re.I)
    return [int(x) for x in m.groups()] if m else None
def parse_rsga(text):
    """Returns dict(issued=datetime, dates=[d1,d2,d3], M, X, P, mid_minor, mid_major, hi_minor, hi_major) or raises ValueError(reason)."""
    m = re.search(r'^:Issued:\s+(\d{4}) (\w{3}) (\d{1,2}) (\d{2})(\d{2}) UTC', text, re.M)
    if not m: raise ValueError('no issued line')
    iss = DT.datetime(int(m.group(1)), MON[m.group(2)], int(m.group(3)), int(m.group(4)), int(m.group(5)))
    # the report's own day: "SDF Number 116 Issued at 2200Z on 25 Apr 2024". A report can go out after midnight (":Issued: 2024 Apr 26 0015 UTC"
    # for the report of 25 April), so the day a report belongs to is read from this line, and the late issue time is kept for the issued-late rule.
    if re.search(r'^SDF Number .*(Correction|AMD|Amended)', text, re.M | re.I): raise ValueError('a correction or amendment, not used')   # PLAN: a re-issued or corrected copy is never used
    s = re.search(r'^SDF Number \d+ Issued at \d{4}Z on (\d{1,2}) (\w{3})\w* (\d{4})', text, re.M)
    if not s: raise ValueError('no SDF line')
    day = DT.date(int(s.group(3)), MON[s.group(2)], int(s.group(1)))
    h = re.search(r'^III\.\s+Event [Pp]robabilities\s+(\d{1,2}) (\w{3})\s*-\s*(\d{1,2}) (\w{3})', text, re.M)
    if not h: raise ValueError('no part III header')
    d1m, d1d = MON[h.group(2)], int(h.group(1)); y = day.year + (1 if d1m < day.month else 0)
    d1 = DT.date(y, d1m, d1d); dates = [d1 + DT.timedelta(i) for i in range(3)]
    p3 = text[h.start():]; p3 = p3[:p3.find('IV.')] if 'IV.' in p3 else p3
    vi = re.search(r'^VI\.\s+Geomagnetic Activity Probabilities', text, re.M)
    if not vi: raise ValueError('no part VI')
    v = text[vi.start():]; a_i = re.search(r'^A\.\s+Middle', v, re.M); b_i = re.search(r'^B\.\s+High', v, re.M)
    if not a_i or not b_i: raise ValueError('no latitude blocks')
    A, B = v[a_i.start():b_i.start()], v[b_i.start():]
    r = dict(issued=iss, day=day, dates=dates, M=triple(p3, 'Class M'), X=triple(p3, 'Class X'), P=triple(p3, 'Proton'),
             mid_minor=triple(A, 'Minor storm'), mid_major=triple(A, 'Major-severe storm'), hi_minor=triple(B, 'Minor storm'), hi_major=triple(B, 'Major-severe storm'))
    return r
stated = {}; dup_issue = C.Counter(); unparsed = []
for src, text in rsga_texts():
    try: r = parse_rsga(text)
    except ValueError as e: unparsed.append((src, str(e))); continue
    if r['day'] < FIRST_ISSUE: continue
    k = r['day']; r['src'] = src
    if k in stated:
        dup_issue[k.isoformat()] += 1
        if (r['issued'], src.startswith('own')) >= (stated[k]['issued'], stated[k]['src'].startswith('own')): continue
    stated[k] = r
date_ok = sum(1 for k, r in stated.items() if r['dates'][0] == k + DT.timedelta(1)); date_n = len(stated)

# ---------------- 3. delivered side ----------------
def events_texts():
    for f in sorted(glob.glob('data/raw/warehouse/*_events.tar.gz')):
        with tarfile.open(f) as t:
            for m in t.getmembers():
                mm = re.search(r'/(\d{8})events\.txt$', m.name)
                if m.isfile() and mm: yield mm.group(1), t.extractfile(m).read().decode('latin-1')
    for f in sorted(glob.glob('data/raw/warehouse/*_events/*events.txt')): yield os.path.basename(f)[:8], open(f, encoding='latin-1').read()
# PLAN Addendum 2: an event number under 1000 is printed with a leading space (" 640 +     1843 ..."), so the line may start with spaces. Channel 1-8A only.
XRA = re.compile(r'^\s*\d+\s+\+?\s*(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+XRA\s+1-8A\s+([A-Z])(\d+(?:\.\d+)?)', re.M)
def hhmm(s):
    s = re.sub(r'\D', '', s); return int(s) if len(s) == 4 else None
flare = C.defaultdict(lambda: dict(M=0, X=0, Monly=0)); events_days = set()
for day, text in events_texts():
    d0 = DT.date(int(day[:4]), int(day[4:6]), int(day[6:])); events_days.add(d0)
    for b, mx, e, letter, num in XRA.findall(text):
        tb, tm = hhmm(b), hhmm(mx); t = tm if tm is not None else tb
        d = d0 + DT.timedelta(1) if (tm is not None and tb is not None and tm < tb) else d0
        if letter in ('M', 'X'): flare[d]['M'] += 1
        if letter == 'X': flare[d]['X'] += 1
        if letter == 'M': flare[d]['Monly'] += 1
spe_days = set()
if os.path.exists('data/raw/SPE.txt'):
    yr = None
    for l in open('data/raw/SPE.txt', encoding='latin-1'):
        m = re.match(r'^\s+((?:19|20)\d\d)\s*$', l)
        if m: yr = int(m.group(1)); continue
        m = re.match(r'^(\w{3}) (\d\d)/(\d{4})', l)
        if m and yr and m.group(1) in MON: spe_days.add(DT.date(yr, MON[m.group(1)], int(m.group(2))))
NUM = re.compile(r'-?\d+(?:\.\d+)?')
kfred, kcol, kpest = {}, {}, {}
for f in sorted(glob.glob('data/raw/warehouse/*_DGD.txt')) + sorted(glob.glob('data/raw/indices/*_DGD.txt')):
    for l in open(f, encoding='latin-1'):
        if not re.match(r'^\d{4} \d\d \d\d', l): continue
        t = NUM.findall(l)
        if len(t) != 30: continue
        d = DT.date(int(t[0]), int(t[1]), int(t[2])); fk = [int(x) for x in t[4:12]]; ck = [int(x) for x in t[13:21]]
        kfred[d] = None if min(fk) < 0 else max(fk); kcol[d] = None if min(ck) < 0 else max(ck)
dsd = {}
for f in sorted(glob.glob('data/raw/warehouse/*_DSD.txt')):
    for l in open(f, encoding='latin-1'):
        if not re.match(r'^\d{4} \d\d \d\d', l): continue
        t = l.split()
        if len(t) == 16:
            try: dsd[DT.date(int(t[0]), int(t[1]), int(t[2]))] = int(t[10]) + int(t[11])
            except ValueError: pass
kp = {}
gf = 'data/raw/gfz/Kp_ap_Ap_SN_F107_since_1932.txt'
if os.path.exists(gf):
    for l in open(gf):
        if l.startswith('#'): continue
        t = l.split()
        if len(t) >= 15 and int(t[0]) >= 2020:
            v = [float(x) for x in t[7:15]]; kp[DT.date(int(t[0]), int(t[1]), int(t[2]))] = None if min(v) < 0 else max(v)

# ---------------- 4. rows ----------------
SPE_LAST = DT.date.fromisoformat(SPE_CHANGED) if SPE_CHANGED else None
SETTLED = TODAY - DT.timedelta(SETTLE_DAYS)       # a target day is scored once it ended at least 3 days before the run
def delivered(ev, d):
    """(o, why): o 1 or 0, or None with the reason there is no delivered record."""
    if d >= SETTLED: return None, 'not yet settled'
    if ev in ('M', 'X', 'Monly'):
        if d not in events_days: return None, 'no events file'
        return int(flare[d][ev] > 0) if d in flare else 0, None
    if ev == 'P':
        if SPE_LAST is None or d > SPE_LAST: return None, 'after the proton list last changed'
        return int(d in spe_days), None
    src = kfred if ev.startswith('MID') else kcol
    if d not in src or src[d] is None: return None, 'no K for the day'
    return int(src[d] >= (5 if ev.endswith('5') else 6)), None
def stated_p(r, ev, i):
    if ev in ('M', 'X', 'P'): v = r[ev]; return (None, 'section did not parse') if v is None else (v[i], None)
    lat = 'mid' if ev.startswith('MID') else 'hi'; mi, ma = r[lat + '_minor'], r[lat + '_major']
    if mi is None or ma is None: return None, 'section did not parse'
    if ev.endswith('5'): return min(100, mi[i] + ma[i]), ('capped' if mi[i] + ma[i] > 100 else None)
    return ma[i], None
rows = []; issue_days = []
d = FIRST_ISSUE
while d <= TODAY: issue_days.append(d); d += DT.timedelta(1)
counts = {(ev, L): C.Counter() for ev, _, _ in EVENTS for L in (1, 2, 3)}; capped = 0
for iss in issue_days:
    r = stated.get(iss)
    for L in (1, 2, 3):
        tgt = iss + DT.timedelta(L)
        for ev, _, _ in EVENTS:
            row = dict(ev=ev, lead=L, issue=iss.isoformat(), target=tgt.isoformat())
            if r is None: row.update(status='no RSGA on file'); rows.append(row); counts[(ev, L)][row['status']] += 1; continue
            row['src'] = r['src']
            if r['dates'][0] != iss + DT.timedelta(1): row.update(status='dates do not match the issue day')
            elif r['issued'] >= DT.datetime.combine(tgt, DT.time()): row.update(status='issued late')
            else:
                p, why = stated_p(r, ev, L - 1)
                if p is None: row.update(status=why)
                else:
                    if why == 'capped': capped += 1
                    o, w2 = delivered(ev, tgt); row['p'] = p
                    if o is None: row.update(status=w2)
                    else: row.update(status='scored', o=o)
            rows.append(row); counts[(ev, L)][row['status']] += 1
monly_rows = []
for row in rows:
    if row['ev'] == 'M' and row.get('status') == 'scored':
        o, _ = delivered('Monly', DT.date.fromisoformat(row['target']))
        if row['lead'] == 1: monly_rows.append((row['p'], o, row['target']))

# ---------------- 5. rulers ----------------
def bin_of(p):
    for a, b in BINS:
        if a <= p <= b: return '%d to %d' % (a, b)
def bin_outcome(k, n, mean_p):
    lo, hi = K.wilson(k, n)
    if n < MIN_N: return K.CANNOT_TELL, lo, hi
    if lo > mean_p: return K.ABOVE, lo, hi
    if hi < mean_p: return K.BELOW, lo, hi
    return K.CONSISTENT, lo, hi
def bss(se, os_):
    n = len(os_); f = sum(os_) / n if n else 0
    return None if n == 0 or f in (0, 1) else 1 - (sum(se) / n) / (f * (1 - f))
def skill_outcome(lo, hi, n, ne):
    if n < MIN_N or ne < MIN_EVENTS or lo is None or hi is None: return K.CANNOT_TELL
    if lo > 0: return K.ABOVE
    if hi < 0: return K.BELOW
    if lo >= -0.05 and hi <= 0.05: return K.CONSISTENT
    return K.CANNOT_TELL
def block_boot(series, rng):
    """series: [(p, o)] in date order. Moving blocks of BLOCK days. Returns list of resampled index lists."""
    n = len(series)
    if n < BLOCK: return []
    out = []
    for _ in range(REPS):
        idx = []
        while len(idx) < n:
            s = rng.randrange(0, n - BLOCK + 1); idx.extend(range(s, s + BLOCK))
        out.append(idx[:n])
    return out
def ruler(series, rng):
    """series: [(p percent, o, target)] in date order. Returns bins, skill."""
    bins = []
    by = C.defaultdict(list)
    for i, (p, o, t) in enumerate(series): by[bin_of(p)].append(i)
    reps = block_boot(series, rng)
    for a, b in BINS:
        nm = '%d to %d' % (a, b); ix = by.get(nm, [])
        n = len(ix); k = sum(series[i][1] for i in ix); mp = (sum(series[i][0] for i in ix) / n / 100) if n else None
        o, lo, hi = bin_outcome(k, n, mp) if n else (K.CANNOT_TELL, 0.0, 1.0)
        bins.append(dict(bin=nm, n=n, events=k, mean_stated=round(mp, 4) if mp is not None else None, observed=round(k / n, 4) if n else None,
                         lo=round(lo, 4), hi=round(hi, 4), outcome=o if GATE else K.CANNOT_TELL))
    # block bootstrap: skill and (described) each bin's frequency
    se = [(p / 100 - o) ** 2 for p, o, t in series]; os_ = [o for p, o, t in series]
    s0 = bss(se, os_); vals = []; binv = C.defaultdict(list); skipped = 0
    binof = [bin_of(p) for p, o, t in series]
    for idx in reps:
        v = bss([se[i] for i in idx], [os_[i] for i in idx])
        if v is None: skipped += 1
        else: vals.append(v)
        cnt = C.Counter(); ev = C.Counter()
        for i in idx: cnt[binof[i]] += 1; ev[binof[i]] += os_[i]
        for nm in cnt: binv[nm].append(ev[nm] / cnt[nm])
    def pct(xs, q):
        xs = sorted(xs); return xs[min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))] if xs else None
    lo, hi = pct(vals, 0.025), pct(vals, 0.975)
    for bn in bins:
        xs = binv.get(bn['bin'], [])
        bn['boot_lo'], bn['boot_hi'] = (round(pct(xs, 0.025), 4), round(pct(xs, 0.975), 4)) if len(xs) >= 100 else (None, None)
    n = len(series); ne = sum(os_); f = ne / n if n else None
    skill = dict(n=n, events=ne, base_rate=round(f, 4) if f is not None else None, brier=round(sum(se) / n, 5) if n else None,
                 brier_clim=round(f * (1 - f), 5) if f is not None else None, bss=round(s0, 4) if s0 is not None else None,
                 lo=round(lo, 4) if lo is not None else None, hi=round(hi, 4) if hi is not None else None, reps=len(vals), reps_skipped=skipped,
                 outcome=skill_outcome(lo, hi, n, ne) if GATE else K.CANNOT_TELL)
    return bins, skill

# ---------------- 6. known-good gates ----------------
kg = {}
kgr = json.load(open('data/known_good_rows.json')) if os.path.exists('data/known_good_rows.json') else []
def g_reader(_):
    if len(kgr) < 3: return False
    for row in kgr:
        r = stated.get(DT.date.fromisoformat(row['issue']))
        if not r: return False
        for k, v in row['values'].items():
            if r[k] != v: return False
    return True
kg['reader'] = K.known_good(g_reader, None)[1]
kg['dates'] = K.known_good(lambda _: date_n > 0 and date_ok / date_n >= 0.99, None)[1]
both = [d for d in dsd if d in events_days and d.year < TODAY.year and d >= DT.date(FIRST_ISSUE.year, 1, 1)]
agree = sum(1 for d in both if (dsd[d] > 0) == ((flare[d]['M'] if d in flare else 0) > 0))
# display (Addendum 2): every day the two records disagree, and whether a flare that began the day before peaked after midnight (DSD counts by begin day)
cross = C.defaultdict(int)
for day, text in events_texts():
    d0 = DT.date(int(day[:4]), int(day[4:6]), int(day[6:]))
    for b, mx, e2, letter, num in XRA.findall(text):
        tb, tm = hhmm(b), hhmm(mx)
        if letter in ('M', 'X') and tm is not None and tb is not None and tm < tb: cross[d0] += 1; cross[d0 + DT.timedelta(1)] += 1
join_disagree = [dict(day=d.isoformat(), dsd_m_plus_x=dsd[d], events_m_or_x=(flare[d]['M'] if d in flare else 0), midnight_crossing=bool(cross.get(d))) for d in sorted(both) if (dsd[d] > 0) != ((flare[d]['M'] if d in flare else 0) > 0)]
kg['join'] = K.known_good(lambda _: len(both) > 300 and agree / len(both) >= 0.95, None)[1]
def g_rule(_):
    # bins: planted frequencies against a stated 30 percent
    ok = bin_outcome(60, 100, 0.30)[0] == K.ABOVE and bin_outcome(5, 100, 0.30)[0] == K.BELOW and bin_outcome(30, 100, 0.30)[0] == K.CONSISTENT and bin_outcome(9, 29, 0.30)[0] == K.CANNOT_TELL
    ok &= skill_outcome(0.1, 0.3, 100, 20) == K.ABOVE and skill_outcome(-0.3, -0.1, 100, 20) == K.BELOW and skill_outcome(-0.03, 0.04, 100, 20) == K.CONSISTENT and skill_outcome(-0.2, 0.3, 100, 20) == K.CANNOT_TELL and skill_outcome(0.1, 0.3, 100, 3) == K.CANNOT_TELL
    # a perfect forecaster and a climatology forecaster: skill 1 and 0
    os_ = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0]; ok &= abs(bss([0.0] * 10, os_) - 1) < 1e-9 and abs(bss([(0.3 - o) ** 2 for o in os_], os_)) < 1e-9
    ok &= bin_of(0) == '0 to 2' and bin_of(2) == '0 to 2' and bin_of(3) == '3 to 7' and bin_of(100) == '88 to 100' and all(bin_of(p) for p in range(101))
    return ok and K.selftest()
_so = sys.stdout; sys.stdout = open(os.devnull, 'w')
try: kg['rule'] = K.known_good(g_rule, None)[1]
finally: sys.stdout.close(); sys.stdout = _so
GATE = all(v == 'passed' for v in kg.values())
if '--selftest' in sys.argv: print(kg); sys.exit(0 if kg['rule'] == 'passed' else 1)

# ---------------- 7. cells ----------------
cells = []
for ev, name, defn in EVENTS:
    for L in (1, 2, 3):
        series = sorted(((r['p'], r['o'], r['target']) for r in rows if r['ev'] == ev and r['lead'] == L and r['status'] == 'scored'), key=lambda x: x[2])
        bins, skill = ruler(series, random.Random(SEED))   # each cell its own generator, seed 27, so a cell reads the same whatever the other cells hold
        cn = counts[(ev, L)]
        cells.append(dict(event=ev, name=name, stated=defn, lead=L, bins=bins, skill=skill, scored=cn['scored'],
                          not_scored={k: v for k, v in cn.items() if k != 'scored'},
                          bin_outcomes=dict(C.Counter(b['outcome'] for b in bins if b['n'] >= MIN_N)), first_target=series[0][2] if series else None, last_target=series[-1][2] if series else None))
# PLAN Addendum 1 item 3: proton cells are held. The delivered list leaves out events SWPC's own daily reports record (23 March 2024, 955 pfu).
HELD_FIGURES = {}
HELD = {'P': 'held: the delivered proton list leaves out events SWPC daily reports record (PLAN Addendum 1)'}
for c in cells:
    if c['event'] in HELD:
        c['held'] = HELD[c['event']]
        HELD_FIGURES['%s%d' % (c['event'], c['lead'])] = json.loads(json.dumps(dict(bins=c['bins'], skill=c['skill'])))   # kept in data/solar.json only
        for b in c['bins']:
            for k in ('events', 'observed', 'lo', 'hi', 'boot_lo', 'boot_hi'): b[k] = None
            b['outcome'] = K.CANNOT_TELL
        c['skill'] = dict(n=c['skill']['n'], events=None, base_rate=None, brier=None, brier_clim=None, bss=None, lo=None, hi=None, reps=0, reps_skipped=0, outcome=K.CANNOT_TELL)
        c['bin_outcomes'] = dict(C.Counter(b['outcome'] for b in c['bins'] if b['n'] >= MIN_N))
# described, not scored
def described(series):
    bins, skill = ruler(series, random.Random(SEED)); return dict(bins=bins, skill=skill)
desc = {}
desc['M only, day one'] = described(sorted(((p, o, t) for p, o, t in monly_rows if o is not None), key=lambda x: x[2]))
mid_rows = {(r['issue'], r['lead']): r for r in rows if r['ev'] == 'MID5' and r.get('p') is not None}
maj_rows = {(r['issue'], r['lead']): r for r in rows if r['ev'] == 'MID6' and r.get('p') is not None}
def kp_series(src, thr):
    out = []
    for (iss, L), r in src.items():
        if L != 1: continue
        d = DT.date.fromisoformat(r['target'])
        if d < SETTLED and kp.get(d) is not None: out.append((r['p'], int(kp[d] >= thr - 0.34), r['target']))
    return sorted(out, key=lambda x: x[2])
# after the data (10 Nov 2026, first read): SWPC states 99 on days a proton event is already in progress, and the plan's event is a start. Display only:
# the proton cells read again with an event day being any day from the list's start day through the day of its maximum.
spe_span = set()
if os.path.exists('data/raw/SPE.txt'):
    yr = None
    for l in open('data/raw/SPE.txt', encoding='latin-1'):
        m = re.match(r'^\s+((?:19|20)\d\d)\s*$', l)
        if m: yr = int(m.group(1)); continue
        m = re.match(r'^(\w{3}) (\d\d)/\d{4}\s+(\w{3}) (\d\d)/\d{4}', l)
        if m and yr and m.group(1) in MON and m.group(3) in MON:
            a = DT.date(yr, MON[m.group(1)], int(m.group(2))); b = DT.date(yr + (1 if MON[m.group(3)] < MON[m.group(1)] else 0), MON[m.group(3)], int(m.group(4)))
            while a <= b: spe_span.add(a); a += DT.timedelta(1)
DESC_HELD = {}
for L in (1, 2, 3):
    DESC_HELD['Proton, an event day is any day from its start through its maximum, day %d (after the data)' % L] = described(sorted(((r['p'], int(DT.date.fromisoformat(r['target']) in spe_span), r['target']) for r in rows if r['ev'] == 'P' and r['lead'] == L and r['status'] == 'scored'), key=lambda x: x[2]))
# Kp 5 or more means Kp of 5- (4.667) or more, Kp 6 or more means 6- (5.667) or more, the NOAA G-scale reading of Kp thirds
desc['Planetary Kp 5 or more against the middle latitude storm chance, day one'] = described(kp_series(mid_rows, 5))
kpest = {}
for f in sorted(glob.glob('data/raw/warehouse/*_DGD.txt')) + sorted(glob.glob('data/raw/indices/*_DGD.txt')):
    for l in open(f, encoding='latin-1'):
        if re.match(r'^\d{4} \d\d \d\d', l):
            t = NUM.findall(l)
            if len(t) == 30:
                v = [float(x) for x in t[22:30]]; kpest[DT.date(int(t[0]), int(t[1]), int(t[2]))] = None if min(v) < 0 else max(v)
def est_series(src, thr):
    out = []
    for (iss, L), r in src.items():
        d = DT.date.fromisoformat(r['target'])
        if L == 1 and d < SETTLED and kpest.get(d) is not None: out.append((r['p'], int(kpest[d] >= thr - 0.34), r['target']))
    return sorted(out, key=lambda x: x[2])
desc['SWPC estimated planetary K 5 or more against the middle latitude storm chance, day one'] = described(est_series(mid_rows, 5))
desc['SWPC estimated planetary K 6 or more against the middle latitude major-severe chance, day one'] = described(est_series(maj_rows, 6))
desc['Planetary Kp 6 or more against the middle latitude major-severe chance, day one'] = described(kp_series(maj_rows, 6))
lit = []
for r in rows:
    if r['ev'] == 'MID5' and r['lead'] == 1 and r.get('status') == 'scored':
        rs = stated[DT.date.fromisoformat(r['issue'])]; d = DT.date.fromisoformat(r['target'])   # stated is keyed by the report's own day
        lit.append((rs['mid_minor'][0], None, r['target'], d))
lit2 = [(p, t, d) for p, _, t, d in lit]   # literal reading: at least one Fredericksburg K equal to 5, read from the eight values
KFRED8 = {}
for f in sorted(glob.glob('data/raw/warehouse/*_DGD.txt')) + sorted(glob.glob('data/raw/indices/*_DGD.txt')):
    for l in open(f, encoding='latin-1'):
        if re.match(r'^\d{4} \d\d \d\d', l):
            t = NUM.findall(l)
            if len(t) == 30: KFRED8[DT.date(int(t[0]), int(t[1]), int(t[2]))] = [int(x) for x in t[4:12]]
desc['Literal minor storm, at least one Fredericksburg K equal to 5, day one'] = described(sorted(((p, int(5 in KFRED8[d]), t) for p, t, d in lit2 if d in KFRED8 and min(KFRED8[d]) >= 0), key=lambda x: x[2]))

# ---------------- 8. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
def _hl():
    # PLAN, Headline row: M-class flares, day one. Bins with MIN_N days or more, how many read consistent, and the Brier skill.
    c = next(x for x in cells if x['event'] == 'M' and x['lead'] == 1); bs = [b for b in c['bins'] if b['n'] >= MIN_N]
    return dict(event='M', lead=1, bins=len(bs), consistent=sum(b['outcome'] == K.CONSISTENT for b in bs), above=sum(b['outcome'] == K.ABOVE for b in bs),
                below=sum(b['outcome'] == K.BELOW for b in bs), share=round(sum(b['outcome'] == K.CONSISTENT for b in bs) / len(bs), 4) if bs else None,
                bss=c['skill']['bss'], lo=c['skill']['lo'], hi=c['skill']['hi'], outcome=c['skill']['outcome'],
                # display, added at the outside referee (Addendum 2): the same bins read on the block bootstrap interval, and every scored cell's bins together
                boot_consistent=sum(1 for b in bs if b.get('boot_lo') is not None and b['boot_lo'] <= b['mean_stated'] <= b['boot_hi']),
                all_bins=C.Counter(b['outcome'] for x in cells if not x.get('held') for b in x['bins'] if b['n'] >= MIN_N),
                by_event={ev: dict(C.Counter(b['outcome'] for x in cells if x['event'] == ev for b in x['bins'] if b['n'] >= MIN_N)) for ev in ('M', 'X', 'MID5', 'MID6', 'HI5', 'HI6')})
summary = dict(
    desk='SOLAR', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='NOAA SWPC Report and Forecast of Solar and Geophysical Activity (RSGA), as originally published in the SWPC Warehouse',
               stated='Part III Class M, Class X and Proton chances, Part VI geomagnetic chances at middle and high latitudes, for each of the next 3 days'),
    frame=dict(first_issue=FIRST_ISSUE.isoformat(), settle_days=SETTLE_DAYS, bins=['%d to %d' % b for b in BINS], min_n=MIN_N, block_days=BLOCK, reps=REPS, seed=SEED),
    gates=dict(kg, passed=GATE, dates_agree=date_ok, dates_n=date_n, join_days=len(both), join_agree=agree, join_disagree=join_disagree),
    sources=dict(rsga_issue_days=len(stated), rsga_unparsed=len(unparsed), rsga_unparsed_list=unparsed[:20], rsga_duplicate_issue_days=dict(dup_issue), rsga_own_copies=len(glob.glob('data/snapshots/*_sgarf.txt.gz')),
                 events_days=len(events_days), dgd_days=len(kfred), dsd_days=len(dsd), spe_list_changed=SPE_CHANGED, spe_event_days_in_frame=sum(1 for d in spe_days if d >= FIRST_ISSUE),
                 gfz_days=len(kp), stale=STALE, capped_sums=capped, settled_before=SETTLED.isoformat(), issue_days_in_frame=len(issue_days)),
    cells=cells, described=desc,
    headline_cell=dict(event='M', lead=1), headline=_hl())
json.dump(dict(generated=summary['generated'], held_figures=dict(note=HELD['P'], cells=HELD_FIGURES, described_proton_span=DESC_HELD), rows=rows), open('data/solar.json.tmp', 'w')); os.replace('data/solar.json.tmp', 'data/solar.json')
json.dump(summary, open('summary_solar.json.tmp', 'w'), indent=1); os.replace('summary_solar.json.tmp', 'summary_solar.json')
json.dump(dict(summary, updated=summary['generated']), open('data/solar_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/solar_live.json.tmp', 'data/solar_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'solar_live', '--path', os.path.join(H, 'data', 'solar_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('solar_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
with open('data/solar_history.jsonl', 'a') as f:
    f.write(json.dumps(dict(t=summary['generated'], gate=GATE, cells=[(c['event'], c['lead'], c['scored'], c['bin_outcomes'], c['skill']['bss'], c['skill']['outcome']) for c in cells], stale=STALE)) + '\n')
log('gates', kg, 'issue days', len(stated), 'unparsed', len(unparsed))
for c in cells: log('%-5s day %d scored %5d bins %s skill %s [%s, %s] %s' % (c['event'], c['lead'], c['scored'], c['bin_outcomes'], c['skill']['bss'], c['skill']['lo'], c['skill']['hi'], c['skill']['outcome']))
