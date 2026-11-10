"""dsa_db.py: database side of SOCIAL section 1 (see PLAN.md). Downloads and checks the Commission's monthly aggregates of the
DSA Transparency Database, reduces them to the fields the plan uses for the mapped platforms, and runs known-good KG1, KG2, KG4.
Run with python3 -I. Reads untrusted parquet; never imports anything from the data folders."""
import os, sys, site, glob, json, time, hashlib, zipfile, shutil, urllib.request, datetime as D, csv, collections as C
sys.path.append(site.getusersitepackages())
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc

H = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(H, 'data', 'raw', 'agg'); ZIPS = os.path.join(RAW, 'zips'); UNZ = os.path.join(RAW, 'unz'); META = os.path.join(RAW, 'agg_meta')
BASE = 'https://d3vax7phxnku8l.cloudfront.net/agg/pqt/data/tdb_data/global___full/aggregations/'
UA = 'heuremen-social/0.1 (+https://indahl.ai/social)'
FIRST_MONTH = (2025, 7)

# PLAN.md, name mapping (exact platform_name). Key = our service name, value = database platform_name.
NAMES = {'Facebook': 'Facebook', 'Instagram': 'Instagram', 'TikTok': 'TikTok', 'YouTube': 'YouTube', 'X': 'X', 'LinkedIn': 'LinkedIn',
         'Snapchat': 'Snapchat', 'Pinterest': 'Pinterest', 'Amazon Store': 'Amazon', 'AliExpress': 'AliExpress', 'Temu': 'Temu', 'Shein': 'Shein',
         'Zalando': 'Zalando', 'Booking.com': 'Booking.com', 'Apple App Store': 'App Store', 'Google Maps': 'Google Maps', 'Google Play': 'Google Play',
         'Google Shopping': 'Google Shopping', 'Pornhub': 'Pornhub', 'XVideos': 'XVideos', 'XNXX': 'XNXX', 'Stripchat': 'Stripchat',
         'WhatsApp Channels': 'WhatsApp Channels'}
ALIASES = {'X (formerly Twitter)': 'X'}   # PLAN.md Addendum 6.9: a second name under which X filed (19 Nov 2025), counted as X
EU = set('AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
SPECIAL = {'EU', 'EEA', 'EEA_no_IS'}
COLS = ['platform_name', 'automated_decision', 'automated_detection', 'source_type', 'decision_ground', 'territorial_scope', 'application_date', 'created_at', 'CONTENT_TYPE_AD', 'count']
KEYS = ['platform_name', 'cre', 'app', 'automated_decision', 'automated_detection', 'source_type', 'decision_ground', 'eea_only', 'is_ad']   # is_ad: Addendum 6.1

def months(last):
    y, m = FIRST_MONTH; out = []
    while (y, m) <= last:
        out.append('%04d-%02d' % (y, m)); m += 1
        if m == 13: y, m = y + 1, 1
    return out

def get(url, path=None, timeout=900):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r:
                b = r.read()
            if path:
                open(path + '.part', 'wb').write(b); os.replace(path + '.part', path)
            return b
        except Exception as e:
            print('dsa_db: retry', a, url, type(e).__name__, file=sys.stderr); time.sleep(5 * (a + 1))
    return None

def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''): h.update(blk)
    return h.hexdigest()

def refresh(kind, ym):
    """Download the month if its published sha1 changed. Returns (status, published_sha1, local_sha1, unzip_dir)."""
    os.makedirs(ZIPS, exist_ok=True)
    f = 'aggregated-%s-%s-01-parquet.zip' % (kind, ym); zp = os.path.join(ZIPS, f)
    pub = get(BASE + f + '.sha1', timeout=60)
    pub = pub.decode().split()[0] if pub else None
    if not pub: return 'NOTHING_RETURNED', None, None, None
    if not (os.path.exists(zp) and sha1(zp) == pub):
        if get(BASE + f, zp) is None: return 'NOTHING_RETURNED', pub, None, None
    loc = sha1(zp)
    if loc != pub: return 'SHA1_MISMATCH', pub, loc, None
    ud = os.path.join(UNZ, f.replace('-parquet.zip', '')); stamp = os.path.join(ud, '.sha1')
    if not (os.path.exists(stamp) and open(stamp).read().strip() == loc):
        if os.path.exists(ud): shutil.rmtree(ud)
        os.makedirs(ud)   # each archive in its own new, empty directory
        with zipfile.ZipFile(zp) as z:
            for n in z.namelist():
                if n.startswith('/') or '..' in n.split('/'): raise SystemExit('unsafe path in ' + f)
            z.extractall(ud)
        open(stamp, 'w').write(loc)
    return 'OK', pub, loc, ud

def parts(ud):
    return sorted(p for p in glob.glob(os.path.join(ud, '**', '*.parquet'), recursive=True) if os.path.isfile(p) and not os.path.basename(p).startswith('.'))

def eea_only(scope):
    if scope is None or scope == '' or scope in SPECIAL: return False
    return not (set(scope.split('_')) & EU)

def reduce_month(ud):
    """Sum count over KEYS for the mapped platforms. Returns a pyarrow Table."""
    want = pa.array(sorted(set(NAMES.values()) | set(ALIASES)))
    acc = []
    for p in parts(ud):
        t = pq.read_table(p, columns=COLS)
        t = t.filter(pc.is_in(t['platform_name'], value_set=want))
        if t.num_rows == 0: continue
        for alias, name in ALIASES.items():
            t = t.set_column(t.schema.get_field_index('platform_name'), 'platform_name', pc.if_else(pc.equal(t['platform_name'], alias), pa.scalar(name), t['platform_name']))
        t = t.append_column('is_ad', t['CONTENT_TYPE_AD'])
        scopes = pc.unique(t['territorial_scope']).to_pylist(); eo = pa.array([s for s in scopes if eea_only(s)], type=pa.string())
        t = t.append_column('eea_only', pc.is_in(t['territorial_scope'], value_set=eo))
        t = t.append_column('cre', pc.strftime(t['created_at'], format='%Y-%m-%d')).append_column('app', pc.strftime(t['application_date'], format='%Y-%m-%d'))
        acc.append(t.select(KEYS + ['count']).group_by(KEYS).aggregate([('count', 'sum')]).rename_columns(KEYS + ['count']))
    if not acc: return None
    t = pa.concat_tables(acc)
    return t.group_by(KEYS).aggregate([('count', 'sum')]).rename_columns(KEYS + ['count'])

def all_platform_day_totals(ud, days=None):
    """KG1: total statements over ALL platforms by created_at day, for the given days (None: every day)."""
    tot = C.Counter()
    for p in parts(ud):
        t = pq.read_table(p, columns=['created_at', 'count'])
        d = pc.strftime(t['created_at'], format='%Y-%m-%d')
        g = pa.table({'d': d, 'c': t['count']}).group_by(['d']).aggregate([('c', 'sum')])
        for k, v in zip(g['d'].to_pylist(), g['c_sum'].to_pylist()):
            if days is None or k in days: tot[k] += v
    return tot

def published_daily_totals(max_pages=60):
    """Addendum 1: the Commission's published daily totals, every page of the download listing."""
    import re, html as H_
    days = {}; d = os.path.join(H, 'data', 'raw', 'docs', 'download_page'); os.makedirs(d, exist_ok=True)
    for p in range(1, max_pages + 1):
        b = get('https://transparency.dsa.ec.europa.eu/explore-data/download?page=%d' % p, timeout=60)
        if not b: break
        open(os.path.join(d, 'page_%d.html' % p), 'wb').write(b)
        t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', b.decode('utf8', 'ignore'), flags=re.S); t = H_.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'\s+', ' ', t)
        got = re.findall(r'(20\d\d-\d\d-\d\d) ((?:\d{1,3} )*\d{1,3}) zip', t)
        if not got: break
        for k, v in got: days[k] = int(v.replace(' ', ''))
    json.dump(days, open(os.path.join(d, 'daily_totals_published.json'), 'w'), indent=0, sort_keys=True)
    return days

def simple_platform_totals(ud):
    """KG2: totals per mapped platform from the simple aggregate."""
    tot = C.Counter(); want = pa.array(sorted(set(NAMES.values()) | set(ALIASES)))
    for p in parts(ud):
        t = pq.read_table(p, columns=['platform_name', 'count']); t = t.filter(pc.is_in(t['platform_name'], value_set=want))
        g = t.group_by(['platform_name']).aggregate([('count', 'sum')])
        for k, v in zip(g['platform_name'].to_pylist(), g['count_sum'].to_pylist()): tot[ALIASES.get(k, k)] += v
    return tot

def dates_coverage(first, last):
    """KG4: every day in [first, last] listed in the dates file with exactly one dump sha1."""
    os.makedirs(META, exist_ok=True); f = os.path.join(META, 'aggregated-complete.dates_files.csv')
    get(BASE + 'aggregated-complete.dates_files.csv', f, timeout=300)
    get(BASE + 'aggregated-complete.configuration.yaml', os.path.join(META, 'aggregated-complete.configuration.yaml'), timeout=60)
    by = C.defaultdict(set)
    for r in csv.DictReader(open(f)): by[r['date']].add(r['csv_dump_sha1'])
    d = D.date.fromisoformat(first); e = D.date.fromisoformat(last); missing = []; multi = []
    while d <= e:
        k = d.isoformat()
        if k not in by: missing.append(k)
        elif len(by[k]) > 1: multi.append(k)
        d += D.timedelta(days=1)
    newest = max(by)
    return dict(first=first, last=last, newest_listed=newest, missing=missing, multiple_sha1=multi)

def run(last_month=None):
    today = D.date.today()
    last = last_month or (today.year, today.month)
    ms = months(last); status = {}; reduced = []; kg2 = []
    for ym in ms:
        st_c, pub_c, loc_c, ud_c = refresh('complete', ym)
        st_s, pub_s, loc_s, ud_s = refresh('simple', ym)
        status[ym] = dict(complete=st_c, complete_sha1=pub_c, simple=st_s, simple_sha1=pub_s)
        if st_c != 'OK': continue
        t = reduce_month(ud_c)
        if t is not None: reduced.append(t.append_column('month', pa.array([ym] * t.num_rows)))
        if st_s == 'OK':
            s = simple_platform_totals(ud_s); c = C.Counter()
            if t is not None:
                for k, v in zip(t['platform_name'].to_pylist(), t['count'].to_pylist()): c[k] += v
            for k in sorted(set(s) | set(c)): kg2.append(dict(month=ym, platform=k, simple=s.get(k, 0), complete=c.get(k, 0)))
        print('dsa_db: month', ym, st_c, st_s, file=sys.stderr)
    big = pa.concat_tables(reduced) if reduced else None
    if big is not None: pq.write_table(big, os.path.join(H, 'data', 'db_reduced.parquet'))
    # KG1: the Commission's published daily totals (download page, read 9 Nov 2026 HST), three days
    published = {'2026-10-19': 22985118, '2026-10-25': 31183637, '2026-10-31': 32731904}
    kg1_days = {}
    if status.get('2026-10', {}).get('complete') == 'OK':
        tot = all_platform_day_totals(os.path.join(UNZ, 'aggregated-complete-2026-10-01'), set(published))
        for k, v in published.items(): kg1_days[k] = dict(published=v, aggregate=tot.get(k, 0), rel=(tot.get(k, 0) - v) / v)
    kg1 = dict(days=kg1_days, passed=bool(kg1_days) and all(abs(x['rel']) < 0.01 for x in kg1_days.values()),
               source='https://transparency.dsa.ec.europa.eu/explore-data/download (page read 9 Nov 2026 HST, research_social/samples/dsa_download.html)')
    # Addendum 1: KG1-all, every day of the window against the published daily totals
    pub = published_daily_totals(); agg_days = C.Counter()
    for ym in ms:
        if status[ym]['complete'] == 'OK': agg_days.update(all_platform_day_totals(os.path.join(UNZ, 'aggregated-complete-%s-01' % ym)))
    kg1all = []
    for k in sorted(agg_days):
        if k < '2025-07-01': continue
        pv = pub.get(k)
        kg1all.append(dict(day=k, published=pv, aggregate=agg_days[k], rel=None if not pv else (agg_days[k] - pv) / pv))
    fails = [r for r in kg1all if r['published'] is None or abs(r['rel']) >= 0.01]
    nopub = sorted(set(k for k in pub if '2025-07-01' <= k <= max(agg_days or ['0'])) - set(agg_days))
    kg1a = dict(days_checked=len(kg1all), failures=fails, published_days_missing_in_aggregate=nopub, max_abs_rel=max((abs(r['rel']) for r in kg1all if r['rel'] is not None), default=None),
                passed=bool(kg1all) and not fails and not nopub, source='https://transparency.dsa.ec.europa.eu/explore-data/download (every page, read %s UTC)' % time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
    bad2 = [r for r in kg2 if max(r['simple'], r['complete']) and abs(r['simple'] - r['complete']) / max(r['simple'], r['complete']) >= 1e-4]
    kg2r = dict(rows=len(kg2), failures=bad2, passed=bool(kg2) and not bad2)
    newest_day = None
    if big is not None: newest_day = max(big['cre'].to_pylist())
    kg4 = dates_coverage('2025-07-01', newest_day or today.isoformat())
    kg4['passed'] = not kg4['missing'] and not kg4['multiple_sha1']
    out = dict(read_utc=time.strftime('%Y-%m-%d %H:%M', time.gmtime()), months=status, newest_created_day=newest_day, KG1=kg1, KG1all=kg1a, KG2=kg2r, KG4=kg4)
    json.dump(out, open(os.path.join(H, 'data', 'db_status.json'), 'w'), indent=1)
    per_platform_shortfall()   # Addendum 3
    return json.load(open(os.path.join(H, 'data', 'db_status.json')))


SHORT_DAYS = ('2026-09-30', '2026-10-01', '2026-10-02')   # Addendum 3
CONTROL_DAYS = ('2026-09-29', '2026-10-03')
LISTING_LABEL = {'Amazon': 'Amazon Store'}                 # the aggregate normalises "Amazon Store" to "Amazon"

def per_platform_shortfall(save=True):
    """Addendum 3: per mapped platform, published per-platform daily totals (download page, platform filter) against the aggregate."""
    import re, html as H_
    d = os.path.join(H, 'data', 'raw', 'docs', 'download_page'); bp = os.path.join(d, 'by_platform'); os.makedirs(bp, exist_ok=True)
    p1 = os.path.join(d, 'page_1.html')
    if not os.path.exists(p1): get('https://transparency.dsa.ec.europa.eu/explore-data/download?page=1', p1, timeout=60)
    opts = {H_.unescape(t).strip(): v for v, t in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', open(p1, encoding='utf8', errors='ignore').read())}
    t = pq.read_table(os.path.join(H, 'data', 'db_reduced.parquet'), columns=['platform_name', 'cre', 'count']).to_pydict()
    agg = C.Counter()
    for p, c, n in zip(t['platform_name'], t['cre'], t['count']):
        if c in SHORT_DAYS or c in CONTROL_DAYS: agg[(p, c)] += n
    out = {}
    for dbn in sorted(set(NAMES.values())):
        label = LISTING_LABEL.get(dbn, dbn); pid = opts.get(label)
        if not pid: out[dbn] = dict(status='NOTHING_RETURNED', reason='no platform filter entry named %r' % label); continue
        pub = {}; used_cache = False
        for page in (1, 2):
            f = os.path.join(bp, 'p%s_page%d.html' % (pid, page))
            cached = open(f, 'rb').read() if os.path.exists(f) else None
            b = get('https://transparency.dsa.ec.europa.eu/explore-data/download?platform_id=%s&page=%d' % (pid, page), f, timeout=60)
            if not b and cached:   # the listing for past days does not change; a refused fetch falls back to the page saved on an earlier read
                b = cached; open(f, 'wb').write(cached); used_cache = True
            if not b: break
            tx = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', b.decode('utf8', 'ignore'), flags=re.S); tx = H_.unescape(re.sub(r'<[^>]+>', ' ', tx)); tx = re.sub(r'\s+', ' ', tx)
            for k, v in re.findall(r'(20\d\d-\d\d-\d\d) ((?:\d{1,3} )*\d{1,3}) zip', tx): pub[k] = int(v.replace(' ', ''))
            if min(pub, default='9') <= CONTROL_DAYS[0]: break
        days = {k: dict(published=pub.get(k), aggregate=agg.get((dbn, k), 0)) for k in SHORT_DAYS + CONTROL_DAYS}
        short = sum(max(0, (v['published'] or 0) - v['aggregate']) for k, v in days.items() if k in SHORT_DAYS)
        missing = [k for k in SHORT_DAYS if pub.get(k) is None and agg.get((dbn, k), 0) > 0]
        ctl_flag = [k for k in CONTROL_DAYS if (days[k]['published'] or 0) and abs(days[k]['aggregate'] - days[k]['published']) / days[k]['published'] > 0.01]
        out[dbn] = dict(status='OK', platform_id=pid, listing_label=label, days=days, shortfall=short, control_days_off_by_more_than_1pct=ctl_flag, days_without_published_row=missing, from_saved_page=used_cache)
    if save:
        st = json.load(open(os.path.join(H, 'data', 'db_status.json'))); st['shortfall_addendum3'] = out
        json.dump(st, open(os.path.join(H, 'data', 'db_status.json'), 'w'), indent=1)
    return out

if __name__ == '__main__':
    o = run()
    print(json.dumps({k: (v['passed'] if isinstance(v, dict) and 'passed' in v else None) for k, v in o.items() if k.startswith('KG')}))
