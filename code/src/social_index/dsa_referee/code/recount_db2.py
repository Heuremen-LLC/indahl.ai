"""Referee recount of the database side, written independently of dsa_db.py.
Reads every part file of every complete monthly aggregate, keeps its own reductions:
  names.json   : statements per platform_name per created month (all platforms) -> name-mapping check
  days.json    : statements per created day over all platforms -> daily-total check
  red.parquet  : mapped platforms, grouped by platform, cre day, app day, automated_decision, automated_detection,
                 source_type, decision_ground, scope class (EU / NONEU_ONLY / EMPTY)
  scopes.json  : territorial_scope strings classed NONEU_ONLY for the mapped platforms, with counts
Run: python3 -I recount_db.py <unz_dir> <out_dir>"""
import sys, os, site, glob, json, collections as C
sys.path.append(site.getusersitepackages())
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
from concurrent.futures import ProcessPoolExecutor

MAPPED = ['X (formerly Twitter)', 'Facebook', 'Instagram', 'TikTok', 'YouTube', 'X', 'LinkedIn', 'Snapchat', 'Pinterest', 'Amazon', 'AliExpress', 'Temu', 'Shein',
          'Zalando', 'Booking.com', 'App Store', 'Google Maps', 'Google Play', 'Google Shopping', 'Pornhub', 'XVideos', 'XNXX', 'Stripchat', 'WhatsApp Channels']
EU27 = set('AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
COLS = ['platform_name', 'automated_decision', 'automated_detection', 'source_type', 'decision_ground', 'territorial_scope', 'application_date', 'created_at', 'CONTENT_TYPE_AD', 'count']

def scope_class(s):
    if s is None or s == '': return 'EMPTY'
    if s in ('EU', 'EEA', 'EEA_no_IS'): return 'EU'
    toks = s.split('_')
    if any(t in EU27 for t in toks): return 'EU'
    return 'NONEU_ONLY'

def day_str(arr):
    # arr: timestamp array (us or ns), returns ISO day strings via integer arithmetic (no strftime)
    unit = arr.type.unit
    div = {'s': 86400, 'ms': 86400 * 10**3, 'us': 86400 * 10**6, 'ns': 86400 * 10**9}[unit]
    ints = pc.cast(arr, pa.int64())
    # exact integer floor division
    q = pc.divide(ints, pa.scalar(div, pa.int64()))   # truncates toward zero for ints
    neg = pc.less(ints, pa.scalar(0, pa.int64()))
    q = pc.if_else(pc.and_(neg, pc.not_equal(pc.multiply(q, pa.scalar(div, pa.int64())), ints)), pc.subtract(q, pa.scalar(1, pa.int64())), q)
    return pc.cast(pc.cast(q, pa.int32()), pa.date32())

def one_month(mdir):
    names = C.Counter(); days = C.Counter(); scopes = C.Counter(); parts = []
    files = sorted(f for f in glob.glob(os.path.join(mdir, '**', 'part-*.parquet'), recursive=True))
    nrows = 0
    for f in files:
        t = pq.read_table(f, columns=COLS)
        nrows += t.num_rows
        cre = day_str(t['created_at'])
        # all-platform per-day totals
        g = pa.table({'d': cre, 'c': t['count']}).group_by('d').aggregate([('c', 'sum')])
        for d, c in zip(g['d'].to_pylist(), g['c_sum'].to_pylist()): days[d.isoformat()] += c
        g = pa.table({'p': t['platform_name'], 'c': t['count']}).group_by('p').aggregate([('c', 'sum')])
        for p, c in zip(g['p'].to_pylist(), g['c_sum'].to_pylist()): names[p] += c
        m = pc.is_in(t['platform_name'], value_set=pa.array(MAPPED))
        t2 = t.filter(m)
        if t2.num_rows == 0: continue
        cre2 = day_str(t2['created_at']); app2 = day_str(t2['application_date']) if t2['application_date'].null_count < t2.num_rows else pa.nulls(t2.num_rows, pa.date32())
        sc = [scope_class(s) for s in t2['territorial_scope'].to_pylist()]
        for s, k, c in zip(t2['territorial_scope'].to_pylist(), sc, t2['count'].to_pylist()):
            if k == 'NONEU_ONLY': scopes[s] += c
        plat = pc.if_else(pc.equal(t2['platform_name'], 'X (formerly Twitter)'), pa.scalar('X'), t2['platform_name'])
        tt = pa.table({'platform': plat, 'isad': t2['CONTENT_TYPE_AD'], 'cre': cre2, 'app': app2, 'ad': t2['automated_decision'], 'det': t2['automated_detection'],
                       'src': t2['source_type'], 'gr': t2['decision_ground'], 'sc': pa.array(sc), 'n': t2['count']})
        parts.append(tt.group_by(['platform', 'isad', 'cre', 'app', 'ad', 'det', 'src', 'gr', 'sc']).aggregate([('n', 'sum')]))
    red = pa.concat_tables(parts).group_by(['platform', 'isad', 'cre', 'app', 'ad', 'det', 'src', 'gr', 'sc']).aggregate([('n_sum', 'sum')]).rename_columns(['platform', 'isad', 'cre', 'app', 'ad', 'det', 'src', 'gr', 'sc', 'n']) if parts else None
    return os.path.basename(mdir), dict(names), dict(days), dict(scopes), red, len(files), nrows

if __name__ == '__main__':
    unz, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    mdirs = sorted(glob.glob(os.path.join(unz, 'aggregated-complete-*')))
    names = {}; days = C.Counter(); scopes = C.Counter(); reds = []; info = {}
    with ProcessPoolExecutor(max_workers=9) as ex:
        for m, nm, dy, scp, red, nf, nr in ex.map(one_month, mdirs):
            names[m] = nm; days.update(dy); scopes.update(scp); info[m] = dict(files=nf, rows=nr)
            if red is not None: reds.append(red.append_column('month', pa.array([m] * red.num_rows)))
            print('done', m, nf, nr, flush=True)
    pq.write_table(pa.concat_tables(reds), os.path.join(out, 'red2.parquet'))
    json.dump(names, open(os.path.join(out, 'names.json'), 'w'), indent=0)
    json.dump(dict(sorted(days.items())), open(os.path.join(out, 'days.json'), 'w'), indent=0)
    json.dump(dict(scopes.most_common()), open(os.path.join(out, 'scopes.json'), 'w'), indent=0)
    json.dump(info, open(os.path.join(out, 'info.json'), 'w'), indent=0)
    print('ALL DONE')
