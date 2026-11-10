#!/usr/bin/env python3
"""tiktok_fetch.py: the fetch half of SOCIAL section 3 (TikTok report against DSA filings). See PLAN.md.

Downloads, keyless:
  1. TikTok Community Guidelines Enforcement Report zips (one per quarter), plus any new quarter linked from the report page.
  2. The Commission's complete and simple monthly aggregates of the DSA Transparency Database (CC BY 4.0), month by month.
     For each month only TikTok rows are kept, grouped on the fields PLAN.md uses, in data/raw/dsa_tiktok/YYYY-MM.parquet.
     The month's zip and its unpacked files are deleted afterwards; the .sha1 is kept as the receipt.
A month is re-read only when its published .sha1 changed. Nothing here installs a timer.
Run with the desk's own venv: .venv/bin/python -I tiktok_fetch.py [--months 2023-09:2026-11] [--force]
"""
import os, sys, json, time, shutil, zipfile, hashlib, re, subprocess, urllib.request, urllib.parse, datetime as D

H = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(H, 'data', 'raw')
UA = 'heuremen-social/0.1 (+https://indahl.ai/social)'
AGG = 'https://d3vax7phxnku8l.cloudfront.net/agg/pqt/data/tdb_data/global___full/aggregations/'
CG_PAGE = 'https://www.tiktok.com/safety/en/transparency/cg-report'
TT_SEEDS = {   # quarter -> URL of its own release (found in archived copies of TikTok's report pages, 10 Nov 2026)
    '2023Q4': 'https://sf16-va.tiktokcdn.com/obj/eden-va2/uhsllrta/Q4_2023_CGER/2023Q4CGER_English.zip',
    '2024Q1': 'https://sf16-va.tiktokcdn.com/obj/eden-va2/uhkklyeh7othpu/Q1_2024_CGER/2024Q1_CGER_English.zip',
    **{q: 'https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/ljhwZthlaukjlkulzlp/' + q + '_CGER/' + q + '_CGER_English.zip'
       for q in ('2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3', '2025Q4')},
    '2026Q1': 'https://sf16-va.tiktokcdn.com/obj/eden-va2/zkyhviozhk_YLNJ/ljhwZthlaukjlkulzlp/2026Q1/2026Q1_CGER_English.zip',
    '2026Q2': 'https://sf16-va.tiktokcdn.com/obj/eden-va2/zkyhviozhk_YLNJ/ljhwZthlaukjlkulzlp/2026_Q2/26Q2USexcl/2026Q2_CGER_English.zip',
}
CT = ['APP', 'AUDIO', 'IMAGE', 'PRODUCT', 'SYNTHETIC_MEDIA', 'TEXT', 'VIDEO', 'OTHER', 'LINK', 'ACCOUNT', 'AD', 'STICKER', 'HASHTAG']
DV = ['REMOVED', 'DISABLED', 'DEMOTED', 'AGE_RESTRICTED', 'INTERACTION_RESTRICTED', 'LABELLED']


def log(*a):
    print('tiktok_fetch:', *a, flush=True)


def http(url, path=None, tries=4, timeout=900):
    """GET url. With path: stream to path, return bytes written. Without: return the body bytes. None on failure."""
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if path is None:
                    return r.read()
                tmp = path + '.part'
                with open(tmp, 'wb') as f:
                    shutil.copyfileobj(r, f, 1 << 20)
                os.replace(tmp, path)
                return os.path.getsize(path)
        except Exception as e:
            code = getattr(e, 'code', None)
            if code in (403, 404):
                return None
            log('retry', a, url[-80:], e)
            time.sleep(5 * (a + 1))
    return None


def sha1_file(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def load_json(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default


# ---------------------------------------------------------------- TikTok side
def tiktok_page_link():
    """The current 'Download data' link on TikTok's report page (raw HTML carries it URL-encoded in page JSON)."""
    b = http(CG_PAGE, timeout=60)
    if not b:
        return None
    h = urllib.parse.unquote(b.decode('utf-8', 'ignore').replace('\\u002F', '/'))
    m = re.findall(r'https://sf16-va\.tiktokcdn\.com/obj/eden-va2/[^"\'<> ]*?CGER[^"\'<> ]*?\.zip', h)
    return m[0] if m else None


def quarter_of_zip(path):
    """Read the latest Period in the zip's CSV, e.g. 'Apr-Jun 2026' -> '2026Q2'."""
    order = {'Jan-Mar': 1, 'Apr-Jun': 2, 'Jul-Sep': 3, 'Oct-Dec': 4}
    best = None
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.lower().endswith('.csv') and not n.startswith('__MACOSX'):
                with z.open(n) as f:
                    import io, csv
                    r = csv.reader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                    hdr = next(r); i = hdr.index('Period')
                    for row in r:
                        p = row[i]; k = (int(p[-4:]), order.get(p[:7], 0))
                        best = k if best is None or k > best else best
    return '%dQ%d' % best if best else None


def fetch_tiktok():
    d = os.path.join(RAW, 'tiktok_cger'); os.makedirs(d, exist_ok=True)
    src = load_json(os.path.join(H, 'data', 'sources.json'), {})
    tt = src.setdefault('tiktok', {})
    urls = dict(TT_SEEDS)
    link = tiktok_page_link()
    if link and link not in urls.values():
        urls['page_latest'] = link
    log('report page link:', link)
    for q, u in urls.items():
        known = tt.get(q)
        p = os.path.join(d, q + '.zip')
        if known and os.path.exists(p) and known.get('url') == u:
            continue
        n = http(u, p, timeout=120)
        if not n:
            log('TikTok zip not reachable', q, u); continue
        if q == 'page_latest':
            qq = quarter_of_zip(p)
            if not qq or qq in tt:
                os.remove(p); continue
            os.replace(p, os.path.join(d, qq + '.zip')); q, p = qq, os.path.join(d, qq + '.zip')
            log('new TikTok quarter from the report page:', q)
        xd = os.path.join(d, 'x_' + q); os.makedirs(xd, exist_ok=True)
        with zipfile.ZipFile(p) as z:
            for n_ in z.namelist():
                b = os.path.basename(n_)
                if n_.startswith('__MACOSX') or not b:
                    continue
                if b.lower().endswith('.csv') or 'readme' in b.lower() or b.lower().endswith('.pdf'):
                    with z.open(n_) as f, open(os.path.join(xd, b), 'wb') as o:
                        shutil.copyfileobj(f, o)
        tt[q] = dict(url=u, bytes=os.path.getsize(p), sha256=sha256_file(p), fetched=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                     csv=[b for b in os.listdir(xd) if b.lower().endswith('.csv')])
        log('TikTok', q, tt[q]['bytes'], 'bytes')
    json.dump(src, open(os.path.join(H, 'data', 'sources.json'), 'w'), indent=1)
    return src


# ---------------------------------------------------------------- database side
def month_list(a, b):
    y, m = map(int, a.split('-')); Y, M = map(int, b.split('-')); out = []
    while (y, m) <= (Y, M):
        out.append('%04d-%02d' % (y, m)); m += 1
        if m == 13: y, m = y + 1, 1
    return out


def extract_month(ym, kind, zpath, outp, con):
    """Unpack one monthly zip into a temp dir, keep TikTok rows grouped on PLAN.md's fields, write outp, delete the unpacked files."""
    tmp = os.path.join(RAW, '_tmp_' + kind + '_' + ym); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if n.endswith('.parquet')]
        parts = sorted(set(re.findall(r'created_at_month=([0-9-]+)', ' '.join(names))))
        for n in names:
            z.extract(n, tmp)
    glob = os.path.join(tmp, '**', '*.parquet').replace("'", "''")
    src = "read_parquet('%s', hive_partitioning=true, union_by_name=true)" % glob
    cols = [r[0] for r in con.execute('describe select * from ' + src).fetchall()]
    def b(c):
        return ('coalesce(%s, false)' % c) if c in cols else 'false'
    if kind == 'complete':
        dd = ("case when application_date is null or content_date is null then null "
              "else greatest(-1, least(31, date_diff('day', cast(content_date as date), cast(application_date as date)))) end")
        sel = ["cast(created_at as date) as created_day", "cast(application_date as date) as application_day", dd + " as dd",
               "coalesce(territorial_scope, '') as territorial_scope", "content_language", "decision_ground",
               "automated_decision", "automated_detection", "source_type", "decision_account", "decision_provision", "decision_monetary"]
    else:
        sel = ["cast(created_at as date) as created_day", "decision_ground", "automated_decision", "automated_detection", "source_type"]
    sel += [b('CONTENT_TYPE_' + c) + ' as ct_' + c.lower() for c in CT] + [b('DECISION_VISIBILITY_CONTENT_' + c) + ' as dv_' + c.lower() for c in DV]
    sel += [b('DECISION_VISIBILITY_OTHER') + ' as dv_other']
    keys = ', '.join(str(i + 1) for i in range(len(sel)))
    q = "copy (select %s, sum(count) as n from %s where platform_name = 'TikTok' group by %s) to '%s' (format parquet)" % (
        ', '.join(sel), src, keys, outp.replace("'", "''"))
    con.execute(q)
    tot = con.execute("select coalesce(sum(n),0), count(*) from read_parquet('%s')" % outp.replace("'", "''")).fetchone()
    allp = con.execute("select coalesce(sum(count),0) from %s" % src).fetchone()[0]
    # Addendum 2: every platform's statements per created day, for the known-good against the Commission's published daily totals
    days = con.execute("select strftime(cast(created_at as date), '%%Y-%%m-%%d'), sum(count) from %s group by 1 order by 1" % src).fetchall()
    json.dump({d: int(n) for d, n in days}, open(outp.replace('.parquet', '_alldays.json'), 'w'), indent=0)
    shutil.rmtree(tmp, ignore_errors=True)
    return dict(partitions=parts, tiktok_statements=int(tot[0]), rows=int(tot[1]), all_platform_statements=int(allp))


def fetch_dsa(months, force=False):
    import duckdb
    con = duckdb.connect(); con.execute("set threads to 4")
    od = os.path.join(RAW, 'dsa_tiktok'); os.makedirs(od, exist_ok=True)
    rd = os.path.join(RAW, 'dsa_receipts'); os.makedirs(rd, exist_ok=True)
    mf = os.path.join(H, 'data', 'dsa_manifest.json'); man = load_json(mf, {})
    for ym in months:
        for kind in KINDS:
            name = 'aggregated-%s-%s-01-parquet.zip' % (kind, ym)
            key = kind + ':' + ym
            sb = http(AGG + name + '.sha1', timeout=60)
            if not sb:
                log('no file yet', name); man.setdefault(key, {})['status'] = 'not published'; continue
            pub = sb.decode().split()[0]
            outp = os.path.join(od, '%s_%s.parquet' % (kind, ym))
            if not force and man.get(key, {}).get('sha1') == pub and os.path.exists(outp) and os.path.exists(outp.replace('.parquet', '_alldays.json')):
                continue
            zp = os.path.join(RAW, name)
            n = http(AGG + name, zp)
            if not n:
                log('download failed', name); man.setdefault(key, {})['status'] = 'download failed'; continue
            got = sha1_file(zp)
            if got != pub:
                log('SHA1 MISMATCH', name, got, pub); os.remove(zp); man.setdefault(key, {})['status'] = 'sha1 mismatch'; continue
            info = extract_month(ym, kind, zp, outp, con)
            os.remove(zp)
            open(os.path.join(rd, name + '.sha1'), 'w').write(sb.decode())
            man[key] = dict(sha1=pub, bytes=n, status='ok', read=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **info)
            log(key, 'TikTok', info['tiktok_statements'], 'statements in', info['rows'], 'rows; partitions', info['partitions'])
            json.dump(man, open(mf, 'w'), indent=1, sort_keys=True)
    json.dump(man, open(mf, 'w'), indent=1, sort_keys=True)
    return man


KINDS = ('complete', 'simple')


def fetch_published_totals():
    """The Commission's published daily statement totals, all platforms (download page listing), for KG3-days (b). Saved as data/published_daily_totals.json."""
    import html as H_
    d = os.path.join(RAW, 'dsa_pages'); os.makedirs(d, exist_ok=True)
    out = {}
    for page in range(1, 60):
        f = os.path.join(d, 'all_page%d.html' % page)
        if not os.path.exists(f) or time.time() - os.path.getmtime(f) > 6 * 3600:
            b = http('https://transparency.dsa.ec.europa.eu/explore-data/download?page=%d' % page, timeout=60)
            if not b:
                break
            open(f, 'wb').write(b); time.sleep(1)
        tx = open(f, encoding='utf8', errors='ignore').read()
        tx = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', tx, flags=re.S); tx = H_.unescape(re.sub(r'<[^>]+>', ' ', tx)); tx = re.sub(r'\s+', ' ', tx)
        got = {k: int(v.replace(' ', '')) for k, v in re.findall(r'(20\d\d-\d\d-\d\d) ((?:\d{1,3} )*\d{1,3}) zip', tx)}
        if not got:
            break
        out.update(got)
        if min(got) <= '2023-09-25':
            break
    if out:
        json.dump(out, open(os.path.join(H, 'data', 'published_daily_totals.json'), 'w'), indent=0, sort_keys=True)
    log('published daily totals:', len(out), 'days')
    return out


def main():
    global KINDS
    args = sys.argv[1:]
    if '--kinds' in args:
        KINDS = tuple(args[args.index('--kinds') + 1].split(','))
    force = '--force' in args
    now = D.datetime.now(D.timezone.utc)
    rng = '2023-09:%04d-%02d' % (now.year, now.month)
    if '--months' in args:
        rng = args[args.index('--months') + 1]
    a, b = rng.split(':')
    if '--dsa-only' not in args:
        fetch_tiktok()
    if '--tiktok-only' not in args:
        fetch_dsa(month_list(a, b), force)
        fetch_published_totals()


if __name__ == '__main__':
    main()
