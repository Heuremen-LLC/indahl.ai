"""dsa_rawdays.py: PLAN.md Addendum 2. Reads the Commission's raw daily parquet dumps for days where the monthly aggregate falls short of the
published daily total, reduces them to the aggregate's keys for the mapped platforms, and writes data/rawdays_reduced.parquet.
Each dump is read part by part (one part extracted at a time into its own folder, deleted after reading); the zip is deleted when done.
Run with python3 -I. Reads untrusted parquet; never executes anything from it."""
import os, sys, site, json, re, zipfile, glob, shutil, hashlib, collections as C
sys.path.append(site.getusersitepackages())
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
import dsa_db

TMP = os.path.join(H, 'data', 'raw', 'daily_tmp')
BASE = 'https://d3vax7phxnku8l.cloudfront.net/raw/pqt/data/tdb_data/global___full/daily_dumps_chunked/'
COLS = ['platform_name', 'territorial_scope', 'application_date', 'created_at', 'automated_decision', 'automated_detection', 'source_type', 'decision_ground']

def scope_eea_only(s):
    if not s: return False
    toks = set(re.findall(r'[A-Z]{2}', s))
    return bool(toks) and not (toks & dsa_db.EU)

def reduce_dump(day, zpath):
    want = pa.array(sorted(set(dsa_db.NAMES.values()))); acc = []; names = C.Counter(); rows_all = 0
    pdir = os.path.join(TMP, day, 'part')
    with zipfile.ZipFile(zpath) as z:
        members = [m for m in z.namelist() if m.endswith('.parquet')]
        for m in members:
            if m.startswith('/') or '..' in m.split('/'): raise SystemExit('unsafe path')
            if os.path.exists(pdir): shutil.rmtree(pdir)
            os.makedirs(pdir)
            with z.open(m) as src, open(os.path.join(pdir, 'p.parquet'), 'wb') as dst: shutil.copyfileobj(src, dst, 1 << 22)
            t = pq.read_table(os.path.join(pdir, 'p.parquet'), columns=COLS); rows_all += t.num_rows
            vc = pc.value_counts(t['platform_name'])
            for x in vc.to_pylist(): names[x['values']] += x['counts']
            t = t.filter(pc.is_in(t['platform_name'], value_set=want))
            if t.num_rows:
                sc = pc.unique(t['territorial_scope']).to_pylist(); eo = pa.array([s for s in sc if scope_eea_only(s)], type=pa.string())
                t = t.append_column('eea_only', pc.is_in(t['territorial_scope'], value_set=eo))
                t = t.append_column('cre', pc.strftime(t['created_at'], format='%Y-%m-%d')).append_column('app', pc.strftime(t['application_date'], format='%Y-%m-%d'))
                t = t.append_column('count', pa.array([1] * t.num_rows, type=pa.int64()))
                acc.append(t.select(dsa_db.KEYS + ['count']).group_by(dsa_db.KEYS).aggregate([('count', 'sum')]).rename_columns(dsa_db.KEYS + ['count']))
            shutil.rmtree(pdir)
            print('rawdays:', day, m.rsplit('/', 1)[-1], file=sys.stderr)
    big = pa.concat_tables(acc).group_by(dsa_db.KEYS).aggregate([('count', 'sum')]).rename_columns(dsa_db.KEYS + ['count']) if acc else None
    return big, names, rows_all

def run(days, delete_zip=True):
    out = []; info = {}
    agg_names = set(open(os.path.join(H, 'data', 'raw', 'agg', 'platform_names_2026-06.txt')).read().split('\n')) if os.path.exists(os.path.join(H, 'data', 'raw', 'agg', 'platform_names_2026-06.txt')) else set()
    for day in days:
        d = os.path.join(TMP, day); os.makedirs(d, exist_ok=True); zp = os.path.join(d, 'dump.zip')
        if not os.path.exists(zp): dsa_db.get(BASE + 'sor-global-%s-full.parquet.zip' % day, zp, timeout=7200)
        pub = dsa_db.get(BASE + 'sor-global-%s-full.parquet.zip.sha1' % day, timeout=60)
        pub = pub.decode().split()[0] if pub else None; loc = dsa_db.sha1(zp) if os.path.exists(zp) else None
        if not loc or loc != pub:
            info[day] = dict(status='NOTHING_RETURNED' if not loc else 'SHA1_MISMATCH', published_sha1=pub, local_sha1=loc); continue
        t, names, rows_all = reduce_dump(day, zp)
        mapped = {k: v for k, v in names.items() if k in set(dsa_db.NAMES.values())}
        info[day] = dict(status='OK', sha1=loc, rows=rows_all, mapped_rows=sum(mapped.values()),
                         names_not_in_aggregate_june=sorted(k for k in names if agg_names and k not in agg_names))
        if t is not None: out.append(t.append_column('dump_day', pa.array([day] * t.num_rows)))
        json.dump(info, open(os.path.join(H, 'data', 'rawdays_status.json'), 'w'), indent=1)
        if delete_zip: os.remove(zp)
    if out: pq.write_table(pa.concat_tables(out), os.path.join(H, 'data', 'rawdays_reduced.parquet'))
    json.dump(info, open(os.path.join(H, 'data', 'rawdays_status.json'), 'w'), indent=1)
    return info

if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1:]), indent=1))
